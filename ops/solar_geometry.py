"""Turn a label's solar azimuth into the azimuth the renderer needs.

    from ops.solar_geometry import image_frame_azimuth
    az_img = image_frame_azimuth(sun_azimuth_true_north=284.901, lon_deg=43.27)   # -> 328.17

WHY THIS EXISTS
---------------
`evaluation.shaded_relief.render_shaded_relief` measures azimuth clockwise from
IMAGE-UP. A product label measures it clockwise from TRUE NORTH (the STAC field
`view:sun_azimuth` and the Kaguya `SOLAR_AZIMUTH_ANGLE` both do). Those agree only
when image-up is north - and for a polar stereographic map it is not.

In the south-polar stereographic used by both the LOLA `ldem_60s` product and the
Kaguya TC GeoTIFF (`ops/fetch_lola_dem.py`: x = (sample - offset)*scale,
y = (offset - line)*scale, longitude = atan2(x, y)), a point at longitude L sits
at map position rho*(sin L, cos L). "North" there is the direction AWAY from the
south pole, i.e. radially outward, (sin L, cos L) - which is image-up rotated
CLOCKWISE by L. So a sun that is A degrees clockwise from true north is A + L
degrees clockwise from image-up:

    azimuth_image = (azimuth_true_north + longitude) mod 360

For the Tier D scene (centre longitude 43.27 E, label azimuth 284.90):
328.17 deg in the image frame. The Day-5 azimuth sweep against the real Kaguya
photograph found its correlation peak "near 330", which at the time looked like an
unexplained 15-degree residual on top of the renderer's sign bug. It was this.

This is derived from the projection, not fitted to the data. The empirical check
lives in `ops/tier_d_investigation.py`; the derivation is the thing to quote.
"""
from __future__ import annotations

import math


def image_frame_azimuth(sun_azimuth_true_north: float, lon_deg: float) -> float:
    """Sun azimuth clockwise from image-up, for a south-polar stereographic raster
    whose +y axis points toward longitude 0 and whose longitude increases clockwise.
    """
    return (float(sun_azimuth_true_north) + float(lon_deg)) % 360.0


def north_direction_in_image(lon_deg: float) -> tuple[float, float]:
    """Unit vector (dx_right, dy_up) pointing to true north at longitude `lon_deg`."""
    L = math.radians(float(lon_deg))
    return (math.sin(L), math.cos(L))


def self_test() -> None:
    # At longitude 0 north is straight up, so nothing changes.
    assert image_frame_azimuth(284.901, 0.0) == 284.901
    # At 90 E north points to the right: a sun from true north (0) comes from the right (90).
    assert abs(image_frame_azimuth(0.0, 90.0) - 90.0) < 1e-9
    assert abs(image_frame_azimuth(284.901, 43.272381) - 328.173381) < 1e-6
    dx, dy = north_direction_in_image(90.0)
    assert abs(dx - 1.0) < 1e-12 and abs(dy) < 1e-12
    print("ops.solar_geometry self-test ok")


if __name__ == "__main__":
    self_test()
