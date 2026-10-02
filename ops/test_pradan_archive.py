"""PRADAN's footprint catalogue: the .dbf reader, the polar projection and the area on the sphere."""
import math
import struct

import pytest

from ops import pradan_archive as A


def test_a_one_degree_box_at_the_equator():
    # 2 pi R^2 (sin 1 deg - sin 0) (1 deg in radians) on the 1737.4 km sphere
    want = A.R_KM ** 2 * math.sin(math.radians(1.0)) * math.radians(1.0)
    got = A.quad_area_km2([(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)])
    assert got == pytest.approx(want, rel=1e-3)
    assert got == pytest.approx(919.5, rel=2e-3)


def test_the_polar_stereographic_inverse_round_trips():
    # forward, south pole, true scale at the pole: rho = 2R tan(pi/4 + lat/2), x = rho sin lon, y = rho cos lon
    lat, lon = -84.25, 37.0
    rho = 2 * A.R_KM * 1000 * math.tan(math.pi / 4 + math.radians(lat) / 2)
    x, y = rho * math.sin(math.radians(lon)), rho * math.cos(math.radians(lon))
    la, lo = A.polar_to_latlon(x, y, south=True)
    assert la == pytest.approx(lat, abs=1e-9) and lo == pytest.approx(lon, abs=1e-9)
    rho_n = 2 * A.R_KM * 1000 * math.tan(math.pi / 4 - math.radians(80.0) / 2)
    la, _ = A.polar_to_latlon(rho_n, 0.0, south=False)
    assert la == pytest.approx(80.0, abs=1e-9)


def test_two_stations_copies_are_one_observation():
    assert A.observation("ch2_ohr_ncp_20200229T0739312111_d_img_d18") == \
           A.observation("ch2_ohr_ncp_20200229T0739312111_d_img_d32")


def _dbf(path, rows, fields):
    hlen = 32 + 32 * len(fields) + 1
    rlen = 1 + sum(w for _, w in fields)
    head = struct.pack("<BBBBIHH20x", 3, 126, 10, 3, len(rows), hlen, rlen)
    desc = b"".join(n.encode().ljust(11, b"\0") + b"C" + b"\0" * 4 + bytes([w]) + b"\0" * 15 for n, w in fields)
    body = b"".join(b" " + b"".join(str(r[n]).encode().ljust(w) for n, w in fields) for r in rows)
    path.write_bytes(head + desc + b"\r" + body + b"\x1a")


def test_the_dbf_reader_and_the_per_observation_sum(tmp_path):
    fields = [("PRODUCT_ID", 48)] + [(f"{c}_{k}", 16) for c in A.CORNERS for k in ("LAT", "LON")]
    box = {"UL_LAT": 1, "UL_LON": 0, "UR_LAT": 1, "UR_LON": 1, "BR_LAT": 0, "BR_LON": 1, "BL_LAT": 0, "BL_LON": 0}
    rows = [{"PRODUCT_ID": "ch2_ohr_ncp_20200101T0000000000_d_img_d18", **box},
            {"PRODUCT_ID": "ch2_ohr_ncp_20200101T0000000000_d_img_d32", **box},
            {"PRODUCT_ID": "ch2_ohr_ncp_20200102T0000000000_d_img_d18", **box}]
    d = tmp_path / "OHRC_ShapeFiles" / "v"
    d.mkdir(parents=True)
    _dbf(d / "ch2_ohr_cal.dbf", rows, fields)
    assert len(A.read_dbf(d / "ch2_ohr_cal.dbf")) == 3
    for folder in ("TMC2_ShapeFiles", "IIRS_ShapeFiles"):
        (tmp_path / folder).mkdir()
    s = A.summary(tmp_path)
    assert s["OHRC"]["products"] == 3 and s["OHRC"]["observations"] == 2
    assert s["OHRC"]["area_km2"] == pytest.approx(2 * 919.5, rel=2e-3)
    assert "area_km2" not in s["TMC-2"]
