"""Build a real Kaguya TC ↔ LOLA shaded-relief Tier-D pair.

The inputs remain outside Git.  Given the bounded Kaguya TIFF and the public
LOLA source, this script writes a 640 px Kaguya optical crop and its exact
overlapping LOLA shaded-relief crop under an ignored pair directory.  The two
GeoTIFFs retain their native ground sampling distances (9.369873... m/px and
60 m/px); ``core.scale.to_common_gsd`` performs the required honest
downsampling before matching.
"""
from __future__ import annotations

import argparse
import pathlib

import numpy as np
from PIL import Image, TiffImagePlugin

from core.io_loader import load
from evaluation.shaded_relief import render_shaded_relief
from ops.fetch_lola_dem import OFFSET_PX, SCALE_M, fetch_window, pixel_to_latlon
from ops.solar_geometry import image_frame_azimuth

KAGUYA_GSD = 9.3698731836556
LOLA_GSD = 60.0
CRS = "Moon (2015) - Sphere / Ocentric / South Polar"
SUN_AZIMUTH_TRUE_NORTH_DEG = 284.901   # STAC view:sun_azimuth for TC1S2B0_01_03482S746E0433
SUN_ELEVATION_DEG = 16.98


def _write_geotiff(path: pathlib.Path, image: np.ndarray, gsd: float,
                   x0: float, y0: float) -> None:
    """Write pixels with the GeoTIFF fields read by ``core.io_loader``."""
    # Pillow is already the loader fallback for LZW GeoTIFFs on the demo
    # laptop. It keeps this utility runnable without imagecodecs or tifffile.
    tags = TiffImagePlugin.ImageFileDirectory_v2()
    tags[33550] = (gsd, gsd, 0.0)                         # ModelPixelScale
    tags[33922] = (0.0, 0.0, 0.0, x0, y0, 0.0)            # ModelTiepoint
    tags[34737] = CRS + "|"                               # GeoAsciiParams
    Image.fromarray(image).save(path, format="TIFF", tiffinfo=tags)


def build(kaguya: pathlib.Path, out_dir: pathlib.Path,
          x: int = 5120, y: int = 2240, tile: int = 640) -> dict:
    """Write a spatially overlapping optical/reference pair and provenance."""
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

    # Convert the exact projected crop rectangle to the DEM's pixel grid, then
    # fetch a padded source band.  Both products use the same south-polar sphere.
    dem_corners = [
        (OFFSET_PX - yy / SCALE_M, OFFSET_PX + xx / SCALE_M)
        for xx in (x_left, x_right) for yy in (y_top, y_bottom)
    ]
    latlon = [pixel_to_latlon(line, sample) for line, sample in dem_corners]
    dem, (band_l0, band_s0) = fetch_window(
        min(v[0] for v in latlon), max(v[0] for v in latlon),
        min(v[1] for v in latlon), max(v[1] for v in latlon),
        # Raw range-cache stays beside the externally stored source TIFF, not
        # in the repository's ignored pair directory (OneDrive ignores Git).
        cache_dir=kaguya.parent,
    )
    lines = [p[0] for p in dem_corners]
    samples = [p[1] for p in dem_corners]
    line0, line1 = int(np.floor(min(lines))), int(np.ceil(max(lines)))
    sample0, sample1 = int(np.floor(min(samples))), int(np.ceil(max(samples)))
    relief_dem = dem[line0 - band_l0:line1 - band_l0,
                     sample0 - band_s0:sample1 - band_s0]
    if relief_dem.size == 0:
        raise ValueError("LOLA crop is empty")

    # The measured Kaguya illumination (STAC view:sun_azimuth 284.901 deg, clockwise
    # from TRUE NORTH). The renderer takes azimuth from IMAGE-UP; in this south-polar
    # stereographic map north is rotated clockwise by the longitude, so the crop
    # centre's longitude is added - derived in ops/solar_geometry.py, not fitted.
    _lat_c, lon_c = pixel_to_latlon((line0 + line1) / 2.0, (sample0 + sample1) / 2.0)
    sun_az_image = image_frame_azimuth(SUN_AZIMUTH_TRUE_NORTH_DEG, lon_c)
    relief = render_shaded_relief(relief_dem, sun_az_image, SUN_ELEVATION_DEG, LOLA_GSD)
    out_dir.mkdir(parents=True, exist_ok=True)
    source_path = out_dir / "tier_d_01_source.tif"
    ref_path = out_dir / "tier_d_01_ref.tif"
    _write_geotiff(source_path, np.rint(optical).astype(np.int32), KAGUYA_GSD, x_left, y_top)
    _write_geotiff(ref_path, np.rint(relief * 65535.0).astype(np.uint16), LOLA_GSD,
                   (sample0 - OFFSET_PX) * LOLA_GSD,
                   (OFFSET_PX - line0) * LOLA_GSD)
    (out_dir / "PROVENANCE.md").write_text(
        "# Tier D pair provenance\n\n"
        f"- Kaguya source: `{kaguya}`\n"
        f"- Kaguya source window: x={x}, y={y}, size={tile} px; GSD={KAGUYA_GSD} m/px\n"
        f"- LOLA: `ldem_60s_60m`, rendered at Kaguya solar elevation {SUN_ELEVATION_DEG} deg and\n"
        f"  azimuth {SUN_AZIMUTH_TRUE_NORTH_DEG} deg from true north = {sun_az_image:.3f} deg from\n"
        f"  image-up (meridian convergence at crop-centre lon {lon_c:.3f} E; ops/solar_geometry.py).\n"
        f"  Renderer convention fixed 3 Sep 2026; earlier builds were lit from a reflected direction.\n"
        f"- LOLA crop: lines {line0}:{line1}, samples {sample0}:{sample1}; GSD={LOLA_GSD} m/px\n"
        "- Both crops use Moon (2015) south-polar stereographic on a 1737.4 km sphere.\n"
        "- Generated files are ignored by Git; this file records how to reproduce them.\n",
        encoding="utf-8",
    )
    return {"source": source_path, "reference": ref_path,
            "source_shape": optical.shape, "reference_shape": relief.shape,
            "source_bounds": (x_left, y_bottom, x_right, y_top),
            "lola_origin": (line0, sample0)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kaguya", type=pathlib.Path)
    parser.add_argument("out_dir", type=pathlib.Path)
    args = parser.parse_args()
    result = build(args.kaguya, args.out_dir)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
