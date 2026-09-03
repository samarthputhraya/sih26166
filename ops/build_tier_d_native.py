"""Build a Tier-D pair with the elevation model rendered into the SENSOR's grid.

WHY THIS EXISTS
---------------
`ops/build_tier_d_pair.py` (Rohan) writes the Kaguya optical crop at its native
9.37 m/px and the LOLA shaded relief at LOLA's native 60 m/px. `core.scale.to_common_gsd`
then resamples BOTH to the coarser of the two - so the 640x640 optical image is
downsampled to 99x99 before it ever reaches the matcher, and LoFTR's coarse stage
(stride 8, `core/matcher.py:68-71`) runs on a 12x12 grid. That is an effective
500 m/px, on elevation data that carries 60 m/px.

We measured 37.81 reference-pixels of residual on that pair and called it a
multi-modal limitation. It is not: it is an information-starvation bug of our own
making. We threw away 97.6% of the optical pixels and then blamed the modality.

This script inverts the choice. Instead of degrading the sensor to the model's
grid, it renders the model into the SENSOR's grid: the DEM is sampled at the
optical image's own pixel centres, giving a 640x640 elevation array at exactly
9.3698731836556 m/px, and the hillshade is computed at that spacing. Both images
then carry an identical `gsd_mpp`, `to_common_gsd` becomes an exact no-op, and
LoFTR's coarse stage lands at 75 m/px - matched to what the DEM actually holds.

WHAT THIS DOES *NOT* CLAIM - read before quoting any number from it
------------------------------------------------------------------
Upsampling invents no terrain. The DEM still holds 60 m/px of real information
and this script does not add a single metre of new relief. `to_common_gsd`'s
docstring is right that upsampling the coarse image "invents detail the sensor
never recorded" - the point here is narrower, and it matters:

    the invented detail is not what we match on.

The coarse stage is what needs a grid fine enough to place a correspondence at
all; the fine stage refines against the OPTICAL image's real texture, which was
never interpolated. Upsampling buys spatial sampling density, not information.
Anyone who reads a result from this script as "we recovered sub-60 m terrain
detail" has misread it, and that sentence must never reach a slide.

Also unchanged from the Lambertian caveat in `evaluation/shaded_relief.py`:
shading rotates, shadows do not move. There is no occlusion term.

REPRODUCING
-----------
    python -m ops.build_tier_d_native \
        C:/Users/samar/sih26166_data/raw/TC1S2B0_01_03482S746E0433.tif \
        data/pairs/pair_04_tierD_native

Reads the same cached LOLA band as the original pair (no network), and writes
`tier_d_native_source.tif` / `tier_d_native_ref.tif` plus PROVENANCE.md.
"""
from __future__ import annotations

import argparse
import pathlib

import numpy as np
from scipy.ndimage import map_coordinates

from core.io_loader import load
from evaluation.shaded_relief import render_shaded_relief
from ops.fetch_lola_dem import OFFSET_PX, SCALE_M, fetch_window, pixel_to_latlon
from ops.solar_geometry import image_frame_azimuth
# Private, and deliberately imported rather than copied: the GeoTIFF tag set is
# what `core/io_loader.py` reads back. Two divergent copies of it is a bug that
# shows up as a silently wrong gsd_mpp, which is the one field this whole
# experiment turns on. `ops/build_tier_d_pair.py` is Rohan's file - importing it
# keeps a single definition without editing someone else's module.
from ops.build_tier_d_pair import KAGUYA_GSD, LOLA_GSD, _write_geotiff

# The measured Kaguya illumination for this scene (STAC `view:sun_azimuth`, clockwise
# from TRUE NORTH). The renderer wants azimuth clockwise from IMAGE-UP, and in this
# south-polar stereographic map north is rotated clockwise by the longitude - see
# `ops/solar_geometry.py`. `build_native` derives the image-frame value from the
# crop's own centre longitude and writes both numbers into PROVENANCE.md.
SUN_AZIMUTH_TRUE_NORTH_DEG = 284.901
SUN_ELEVATION_DEG = 16.98


def build_native(kaguya: pathlib.Path, out_dir: pathlib.Path,
                 x: int = 5120, y: int = 2240, tile: int = 640) -> dict:
    """Write an optical crop and a DEM hillshade sampled on that crop's own grid."""
    optical, meta = load(kaguya, window=(x, y, tile, tile))
    if optical.shape != (tile, tile):
        raise ValueError(f"requested {tile}x{tile} Kaguya tile, got {optical.shape}")
    if np.any(optical == -32768):
        raise ValueError("selected Kaguya window contains NoData (-32768)")
    transform = meta.get("transform")
    if not transform or meta.get("gsd_mpp") != KAGUYA_GSD:
        raise ValueError("Kaguya GeoTIFF metadata is missing or has an unexpected GSD")

    kx0, sx, _, ky0, _, sy = transform
    x_left = kx0 + sx * x
    y_top = ky0 + sy * y
    x_right = x_left + sx * tile
    y_bottom = y_top + sy * tile

    # Fetch the same padded LOLA band the original pair used. `cache_dir` holds the
    # raw range-cache, so this is offline once warmed.
    dem_corners = [
        (OFFSET_PX - yy / SCALE_M, OFFSET_PX + xx / SCALE_M)
        for xx in (x_left, x_right) for yy in (y_top, y_bottom)
    ]
    latlon = [pixel_to_latlon(line, sample) for line, sample in dem_corners]
    dem, (band_l0, band_s0) = fetch_window(
        min(v[0] for v in latlon), max(v[0] for v in latlon),
        min(v[1] for v in latlon), max(v[1] for v in latlon),
        cache_dir=kaguya.parent,
    )

    # --- the whole point of this file -----------------------------------------
    # Sample the DEM at the OPTICAL image's pixel centres. Both products are south
    # polar stereographic on the same 1737.4 km sphere, so projected metres are
    # directly comparable and this is a resampling, not a reprojection.
    cols = x_left + sx * (np.arange(tile, dtype=np.float64) + 0.5)
    rows = y_top + sy * (np.arange(tile, dtype=np.float64) + 0.5)
    gx, gy = np.meshgrid(cols, rows)
    # NOTE THE SIGN. line = OFFSET - Y/scale, not plus. Getting this backwards
    # lands you 180 degrees away at the same latitude with plausible elevations.
    dem_lines = (OFFSET_PX - gy / SCALE_M) - band_l0
    dem_samples = (OFFSET_PX + gx / SCALE_M) - band_s0

    margin = 2  # cubic interpolation reads a 4x4 neighbourhood
    if (dem_lines.min() < margin or dem_samples.min() < margin
            or dem_lines.max() > dem.shape[0] - 1 - margin
            or dem_samples.max() > dem.shape[1] - 1 - margin):
        raise ValueError(
            "the optical footprint reaches the edge of the fetched LOLA band; "
            "increase pad_px in fetch_window before trusting this render"
        )

    dem_native = map_coordinates(
        dem.astype(np.float64), [dem_lines, dem_samples], order=3, mode="reflect",
    ).astype(np.float32)

    # Sun azimuth in the IMAGE frame: label azimuth (from true north) plus the
    # meridian convergence at the crop centre. Derived, not fitted - the azimuth
    # sweep in ops/tier_d_investigation.py confirms it to within its 5 deg step.
    xc, yc = x_left + sx * (tile / 2.0), y_top + sy * (tile / 2.0)
    _lat_c, lon_c = pixel_to_latlon(OFFSET_PX - yc / SCALE_M, OFFSET_PX + xc / SCALE_M)
    sun_azimuth_image_deg = image_frame_azimuth(SUN_AZIMUTH_TRUE_NORTH_DEG, lon_c)

    # Hillshade at the FINE spacing. render_shaded_relief takes gradients with
    # np.gradient(dem, pixel_size_m), so passing the true 9.37 m spacing keeps the
    # slope field physically correct on the new grid.
    relief = render_shaded_relief(dem_native, sun_azimuth_image_deg, SUN_ELEVATION_DEG, KAGUYA_GSD)

    out_dir.mkdir(parents=True, exist_ok=True)
    source_path = out_dir / "tier_d_native_source.tif"
    ref_path = out_dir / "tier_d_native_ref.tif"
    _write_geotiff(source_path, np.rint(optical).astype(np.int32), KAGUYA_GSD, x_left, y_top)
    # Same GSD and same origin as the optical crop: to_common_gsd is now a no-op.
    _write_geotiff(ref_path, np.rint(relief * 65535.0).astype(np.uint16), KAGUYA_GSD,
                   x_left, y_top)

    (out_dir / "PROVENANCE.md").write_text(
        "# Tier D pair provenance - NATIVE-GRID render (bet A)\n\n"
        f"- Kaguya source: `{kaguya}`\n"
        f"- Kaguya source window: x={x}, y={y}, size={tile} px; GSD={KAGUYA_GSD} m/px\n"
        f"- LOLA: `ldem_60s_60m`, native {LOLA_GSD} m/px, resampled by cubic spline onto the\n"
        f"  Kaguya pixel grid ({tile}x{tile} at {KAGUYA_GSD} m/px) BEFORE hillshading.\n"
        f"- Hillshade computed at {KAGUYA_GSD} m/px, solar elevation {SUN_ELEVATION_DEG} deg,\n"
        f"  solar azimuth {SUN_AZIMUTH_TRUE_NORTH_DEG} deg from true north (STAC view:sun_azimuth)\n"
        f"  = {sun_azimuth_image_deg:.3f} deg from image-up after adding the meridian\n"
        f"  convergence at the crop centre (lon {lon_c:.3f} E) - see ops/solar_geometry.py.\n"
        f"  Renderer convention fixed 3 Sep 2026 (evaluation/shaded_relief.py); earlier\n"
        f"  versions of this pair were lit from a reflected direction.\n"
        f"- LOLA band origin: line {band_l0}, sample {band_s0}; band shape {dem.shape}.\n"
        "- Both crops use Moon (2015) south-polar stereographic on a 1737.4 km sphere.\n"
        "\n"
        "## What differs from `pair_03_tierD`, and what does not\n\n"
        "The optical crop is identical in extent and content. The ONLY change is the grid\n"
        "the reference is rendered on: 60 m/px there, 9.37 m/px here. Because both images\n"
        "now carry the same `gsd_mpp`, `core.scale.to_common_gsd` performs no resampling,\n"
        "and the match runs at 640x640 instead of 99x99.\n\n"
        "**Upsampling adds no terrain information.** The DEM still holds 60 m/px of real\n"
        "relief. What changes is sampling density for the matcher's coarse stage, not the\n"
        "information content of the elevation model. Do not read any result from this pair\n"
        "as recovered sub-60 m detail.\n\n"
        "**`residual_px` from this pair is NOT comparable to `pair_03_tierD`'s.** The pixel\n"
        "grids differ by 6.4x. Compare in METRES: `residual_px * gsd_mpp`.\n\n"
        "- Generated files are ignored by Git; this file records how to reproduce them.\n",
        encoding="utf-8",
    )
    return {"source": source_path, "reference": ref_path,
            "source_shape": tuple(optical.shape), "reference_shape": tuple(relief.shape),
            "gsd_mpp": KAGUYA_GSD,
            "dem_band_shape": tuple(dem.shape),
            "dem_native_range_m": (float(dem_native.min()), float(dem_native.max())),
            "source_bounds": (x_left, y_bottom, x_right, y_top)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kaguya", type=pathlib.Path)
    parser.add_argument("out_dir", type=pathlib.Path)
    args = parser.parse_args()
    result = build_native(args.kaguya, args.out_dir)
    for k, v in result.items():
        print(f"  {k:22} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
