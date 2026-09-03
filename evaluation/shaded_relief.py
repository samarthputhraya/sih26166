"""Hillshade a DEM from a stated sun position.

    render_shaded_relief(dem, sun_azimuth_deg, sun_elevation_deg, pixel_size_m) -> float32 in [0, 1]

CONVENTION - read this before changing a sign
--------------------------------------------
`sun_azimuth_deg` is measured CLOCKWISE FROM IMAGE-UP (row 0 is the top of the
array): 0 = light arrives from the top of the image, 90 = from the right, 180 =
from the bottom, 270 = from the left. That is "north" only if image-up is north,
which it is NOT for a polar-stereographic product - see `ops/solar_geometry.py`
for the correction from a label's true-north azimuth to this frame.

The formula is the standard one (Horn 1981; GDAL `gdaldem hillshade`):

    x  = dz/dcol            (elevation change per pixel to the RIGHT)
    y  = dz/drow            (elevation change per pixel DOWNWARD)
    slope  = atan(hypot(x, y))
    aspect = atan2(y, -x)
    az     = 360 - sun_azimuth + 90      (compass -> mathematical angle)
    shade  = cos(zenith) cos(slope) + sin(zenith) sin(slope) cos(az - aspect)

WHAT WAS WRONG BEFORE 3 SEP 2026, AND HOW IT WAS FOUND
------------------------------------------------------
The previous version unpacked `np.gradient(dem)` as `dzdx, dzdy`. NumPy returns
the gradients in AXIS order - (d/drow, d/dcol) - so the two were swapped, and the
aspect was then built as `atan2(-dzdy, dzdx)`. The net effect was a REFLECTION of
the lighting direction about the image diagonal: asking for a sun at azimuth `a`
lit the terrain as if the sun were at `90 - a`. On a round hill, a sun requested
from the top lit the right-hand flank.

It was first noticed on the real Kaguya <-> LOLA pair as a negative correlation
between the render and the photograph (-0.57), and diagnosed on Day 5 as "the
terrain is lit from az+180". That diagnosis was itself only half right - a
reflection, not a rotation - and the remaining ~15 deg that the Day-5 azimuth
sweep could not explain turned out to be the map projection's meridian
convergence, not a rendering error. Both are written up in
`ops/specs/TIER_D_FINDINGS_DAY5.md` and `ops/PHASE0_RESEARCH_DAY5.md`.

`evaluation/test_shaded_relief.py` pins the convention with a hill and a crater:
a sun from the top must light a hill's top flank and a crater's BOTTOM wall.
Do not change a sign in here without that test.

LIMIT - state it wherever these renders are used as evidence
-----------------------------------------------------------
This is a local cosine law. There is NO cast-shadow / ray-occlusion term. A sun
AZIMUTH change rotates the shading and is a meaningful illumination test; a sun
ELEVATION change only rescales brightness - a spire that should throw a long
shadow throws none. The synthetic sweep therefore varies azimuth at a fixed
elevation and is described as an illumination test, never a shadow test.
"""
import numpy as np


def render_shaded_relief(dem, sun_azimuth_deg, sun_elevation_deg, pixel_size_m):
    """Render a DEM as a shaded-relief image lit from a given sun position.

    dem             : 2-D elevation array, metres, rows = image rows (top first).
    sun_azimuth_deg : clockwise from image-up (see the module docstring).
    sun_elevation_deg : degrees above the horizon.
    pixel_size_m    : ground sample distance of `dem`, metres per pixel.

    Returns float32 in [0, 1]. The same terrain lit from two sun positions gives
    two images whose pixels correspond exactly, because it is the same grid -
    that is what makes these renders usable as ground truth.
    """
    if pixel_size_m is None or pixel_size_m <= 0:
        raise ValueError(f"pixel_size_m must be positive, got {pixel_size_m!r}")
    z = np.asarray(dem, dtype=np.float64)
    if z.ndim != 2:
        raise ValueError(f"dem must be 2-D, got shape {z.shape}")

    # np.gradient returns one array per AXIS: axis 0 is rows (downward), axis 1
    # is columns (rightward). Naming them in that order is the whole fix.
    dz_drow, dz_dcol = np.gradient(z, pixel_size_m)

    slope = np.arctan(np.hypot(dz_dcol, dz_drow))
    aspect = np.arctan2(dz_drow, -dz_dcol)
    az = np.deg2rad(360.0 - float(sun_azimuth_deg) + 90.0)
    ze = np.deg2rad(90.0 - float(sun_elevation_deg))
    shade = (np.cos(ze) * np.cos(slope)
             + np.sin(ze) * np.sin(slope) * np.cos(az - aspect))
    return np.clip(shade, 0.0, 1.0).astype(np.float32)
