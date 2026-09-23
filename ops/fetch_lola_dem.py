"""Fetch a window of the LOLA south-polar DEM without downloading 1.93 GB.

WHY THIS EXISTS
---------------
Our demo site is at latitude -74. `SLDEM2015` — which Canonical Facts SS2 names as the Tier D
source and which the college-round Day 4 plan scheduled — **only covers +/-60 degrees**. It does not
reach our site. Verified 1 Sep 2026: the southernmost tile in
`.../sldem2015/tiles/float_img/` is `sldem2015_256_60s_0s_*`.

The product that DOES cover us is LOLA `ldem_60s_60m` (60 S to 90 S, 60 m/px, essentially the
same resolution as SLDEM2015's 59 m/px). It is a single 1.93 GB raw binary with a detached
label, so this module range-fetches only the rows it needs (~34 MB for a 550-row band).

THE PROJECTION, AND THE SIGN THAT WILL CATCH YOU
------------------------------------------------
Both LOLA and the Kaguya TC scenes use south polar stereographic on a 1737.4 km sphere, so their
projected metres are directly comparable. The line axis increases SOUTHWARD-to-NORTHWARD in the
opposite sense to Y:

    line = OFFSET - Y/scale        <-- minus, not plus

Getting that sign wrong puts you 180 degrees away in longitude at the same latitude, which looks
completely plausible: you still get sane-looking lunar elevations, just of the wrong ground.
That happened while writing this file. `latlon_to_pixel` round-trips against `pixel_to_latlon`,
and `self_test()` checks the -60 edge lands on line ~0. Run it if you change anything.
"""
from __future__ import annotations

import math
import pathlib
import urllib.request

import numpy as np

BASE = ("https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/"
        "lrolol_1xxx/data/lola_gdr/polar/img/ldem_60s_60m")

R_M = 1737.4 * 1000.0     # A_AXIS_RADIUS from the label
SCALE_M = 60.0            # MAP_SCALE
OFFSET_PX = 15519.5       # LINE_/SAMPLE_PROJECTION_OFFSET
N = 31040                 # LINES == LINE_SAMPLES
ROW_BYTES = N * 2         # SAMPLE_BITS = 16, LSB_INTEGER
ELEV_SCALE = 0.5          # SCALING_FACTOR: height_m = DN * 0.5


def latlon_to_pixel(lat_deg: float, lon_deg: float) -> tuple[float, float]:
    """(lat, lon) -> (line, sample) in the ldem_60s_60m grid. Lat must be negative."""
    rho = 2.0 * R_M * math.tan(math.radians(45.0 + lat_deg / 2.0))
    x = rho * math.sin(math.radians(lon_deg))
    y = rho * math.cos(math.radians(lon_deg))
    return OFFSET_PX - y / SCALE_M, OFFSET_PX + x / SCALE_M


def pixel_to_latlon(line: float, sample: float) -> tuple[float, float]:
    """Inverse of latlon_to_pixel."""
    x = (sample - OFFSET_PX) * SCALE_M
    y = (OFFSET_PX - line) * SCALE_M
    rho = math.hypot(x, y)
    lat = -(90.0 - 2.0 * math.degrees(math.atan(rho / (2.0 * R_M))))
    return lat, math.degrees(math.atan2(x, y)) % 360.0


def fetch_window(lat_min, lat_max, lon_min, lon_max, pad_px=40, cache_dir=None):
    """Range-fetch the DEM rows covering a lat/lon box. Returns (elev_m, (line0, sample0)).

    Only whole rows are fetched (one HTTP range request), then columns are cropped in memory.
    """
    corners = [(lat_min, lon_min), (lat_min, lon_max), (lat_max, lon_min), (lat_max, lon_max)]
    px = [latlon_to_pixel(a, b) for a, b in corners]
    l0 = max(0, int(min(p[0] for p in px)) - pad_px)
    l1 = min(N, int(max(p[0] for p in px)) + pad_px)
    s0 = max(0, int(min(p[1] for p in px)) - pad_px)
    s1 = min(N, int(max(p[1] for p in px)) + pad_px)

    cache_dir = pathlib.Path(cache_dir) if cache_dir else pathlib.Path(".")
    cache_dir.mkdir(parents=True, exist_ok=True)
    raw = cache_dir / f"ldem_60s_60m_{l0}_{l1}.raw"

    if not raw.exists():
        byte_start = l0 * ROW_BYTES
        byte_end = l1 * ROW_BYTES - 1
        expected_bytes = byte_end - byte_start + 1
        req = urllib.request.Request(
            BASE + ".img",
            headers={"Range": f"bytes={byte_start}-{byte_end}"},
        )
        with urllib.request.urlopen(req, timeout=600) as r:
            status = getattr(r, "status", r.getcode())
            content_range = r.headers.get("Content-Range", "")
            expected_range = f"bytes {byte_start}-{byte_end}/"
            if status != 206 or not content_range.startswith(expected_range):
                raise RuntimeError(
                    "LOLA server did not honor the requested byte range; refusing a possible "
                    f"full {N * ROW_BYTES / 1e9:.2f} GB download "
                    f"(status={status}, Content-Range={content_range!r})"
                )
            content_length = r.headers.get("Content-Length")
            if content_length is not None and int(content_length) != expected_bytes:
                raise RuntimeError(
                    f"LOLA range response length is {content_length}, expected {expected_bytes}"
                )
            payload = r.read(expected_bytes + 1)
        if len(payload) != expected_bytes:
            raise RuntimeError(
                f"LOLA range payload is {len(payload)} bytes, expected {expected_bytes}"
            )
        raw.write_bytes(payload)

    band = np.fromfile(raw, dtype="<i2").reshape(l1 - l0, N)
    return band[:, s0:s1].astype(np.float32) * ELEV_SCALE, (l0, s0)


def self_test() -> None:
    """Round-trip the projection and check the documented edge case."""
    for lat, lon in [(-74.563, 43.2812), (-73.94, 43.66), (-60.0, 0.0), (-89.0, 200.0)]:
        line, sample = latlon_to_pixel(lat, lon)
        back_lat, back_lon = pixel_to_latlon(line, sample)
        assert abs(back_lat - lat) < 1e-6, f"lat round-trip failed at {lat}"
        assert abs(back_lon - lon % 360.0) < 1e-6, f"lon round-trip failed at {lon}"

    # MAXIMUM_LATITUDE = -60 must sit at the image edge, i.e. line ~ 0 at lon 0.
    line, sample = latlon_to_pixel(-60.0, 0.0)
    assert abs(line) < 3.0, f"-60 deg should land on line ~0, got {line:.1f}"
    assert abs(sample - OFFSET_PX) < 1e-6

    # The sign trap: +Y instead of -Y lands 180 deg away at the SAME latitude.
    wrong_line = OFFSET_PX + (OFFSET_PX - latlon_to_pixel(-74.0, 43.0)[0])
    wrong_lat, wrong_lon = pixel_to_latlon(wrong_line, latlon_to_pixel(-74.0, 43.0)[1])
    assert abs(wrong_lat - (-74.0)) < 0.5, "the sign trap should preserve latitude"
    assert abs(wrong_lon - 43.0) > 90.0, "the sign trap should move longitude a long way"
    print("self_test: projection round-trips, -60 lands on the edge, sign trap reproduced")


if __name__ == "__main__":
    self_test()
    # The CH-2 OHRC footprint, measured from its own geometry CSV.
    elev, (l0, s0) = fetch_window(-74.3661, -73.5168, 43.3595, 43.9577,
                                  cache_dir=r"C:/Users/samar/sih26166_data/raw")
    print(f"window {elev.shape} at line0={l0} sample0={s0}")
    print(f"elevation {elev.min():.1f} .. {elev.max():.1f} m   relief {np.ptp(elev):.0f} m")
