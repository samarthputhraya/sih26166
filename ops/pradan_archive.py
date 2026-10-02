"""How big the Chandrayaan-2 archive is, from PRADAN's own footprint catalogue.

    python -m ops.pradan_archive            # counts and OHRC area, from <data>/pradan/shapefiles

PRADAN publishes one footprint shapefile per instrument and product level (downloaded 18 Sep 2026;
OHRC releases 1-11). Each record is one product with its four corners. This reads only the .dbf
tables (the corners are there), with no shapefile library: a dBASE III table is a 32-byte header,
32-byte field descriptors and fixed-width records.

The polar files are not in degrees: their "LAT/LON" corner fields hold polar-stereographic metres
on the 1737.4 km sphere, true scale at the pole (their .prj: Stereographic_South_Pole /
Stereographic_North_Pole, central meridian 0). They are converted before any area is summed.

Counts are of calibrated products (`*_cal*.dbf`). One observation can be listed more than once
(the same strip received at two ground stations: `_d_img_d18` and `_d_img_d32`), so areas are
summed per observation, never per product. Area is each footprint quadrilateral on the sphere,
from two spherical triangles (Van Oosterom & Strackee's solid angle).
"""
from __future__ import annotations

import math
import pathlib
import re
import statistics
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
R_KM = 1737.4
INSTRUMENTS = {"OHRC": ("OHRC_ShapeFiles", "ch2_ohr_cal"), "TMC-2": ("TMC2_ShapeFiles", "ch2_tmc_cal"),
               "IIRS": ("IIRS_ShapeFiles", "ch2_iir_cal")}
CORNERS = ("UL", "UR", "BR", "BL")          # in order round the footprint


def data_root() -> pathlib.Path:
    return pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())


def read_dbf(path: pathlib.Path) -> list[dict]:
    """Every live record of a dBASE III table, as {field: stripped text}."""
    b = path.read_bytes()
    n, hlen, rlen = struct.unpack("<IHH", b[4:12])
    fields, i = [], 32
    while i < hlen - 1 and b[i] != 0x0D:
        name = b[i:i + 11].split(b"\0")[0].decode("ascii", "replace")
        fields.append((name, b[i + 16]))
        i += 32
    out = []
    for k in range(n):
        rec = b[hlen + k * rlen: hlen + (k + 1) * rlen]
        if not rec or rec[0:1] == b"*":                     # deleted
            continue
        pos, row = 1, {}
        for name, width in fields:
            row[name] = rec[pos:pos + width].decode("latin-1").strip()
            pos += width
        out.append(row)
    return out


def polar_to_latlon(x: float, y: float, south: bool) -> tuple[float, float]:
    """Inverse polar stereographic on the sphere, true scale at the pole (Snyder 1987, eq. 21-14)."""
    rho = math.hypot(x, y)
    c = 2.0 * math.atan(rho / (2.0 * R_KM * 1000.0))
    if south:
        return math.degrees(c - math.pi / 2), math.degrees(math.atan2(x, y))
    return math.degrees(math.pi / 2 - c), math.degrees(math.atan2(x, -y))


def _unit(lat: float, lon: float) -> tuple[float, float, float]:
    la, lo = math.radians(lat), math.radians(lon)
    return math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)


def _triangle_sr(a, b, c) -> float:
    """Solid angle of a spherical triangle of unit vectors (Van Oosterom & Strackee 1983)."""
    cross = (b[1] * c[2] - b[2] * c[1], b[2] * c[0] - b[0] * c[2], b[0] * c[1] - b[1] * c[0])
    num = abs(a[0] * cross[0] + a[1] * cross[1] + a[2] * cross[2])
    dot = lambda u, v: u[0] * v[0] + u[1] * v[1] + u[2] * v[2]  # noqa: E731
    den = 1.0 + dot(a, b) + dot(b, c) + dot(c, a)
    return 2.0 * math.atan2(num, den)


def quad_area_km2(corners: list[tuple[float, float]]) -> float:
    """Area on the 1737.4 km sphere of a quadrilateral given as four (lat, lon) in order."""
    p = [_unit(*q) for q in corners]
    return (_triangle_sr(p[0], p[1], p[2]) + _triangle_sr(p[0], p[2], p[3])) * R_KM ** 2


def corners_of(rec: dict, polar: str | None) -> list[tuple[float, float]]:
    pts = []
    for c in CORNERS:
        a, b = float(rec[f"{c}_LAT"]), float(rec[f"{c}_LON"])
        pts.append(polar_to_latlon(b, a, polar == "sp") if polar else (a, b))
    return pts


def observation(product_id: str) -> str:
    """One observation, whichever ground station's copy: drop the `_d_img_<station>` tail."""
    return re.sub(r"_d_img_\w+$", "", product_id)


def footprints(instrument: str, shp_root: pathlib.Path) -> dict[str, dict]:
    """{product_id: {'observation', 'area_km2', 'polar'}} over the instrument's calibrated tables."""
    folder, stem = INSTRUMENTS[instrument]
    out = {}
    for dbf in sorted((shp_root / folder).rglob(f"{stem}*.dbf")):
        polar = next((p for p in ("np", "sp") if dbf.stem.endswith(f"_{p}")), None)
        for rec in read_dbf(dbf):
            pid = rec["PRODUCT_ID"]
            try:
                area = quad_area_km2(corners_of(rec, polar))
            except (ValueError, KeyError):
                area = math.nan
            out.setdefault(pid, {"observation": observation(pid), "area_km2": area, "polar": polar})
    return out


def summary(shp_root: pathlib.Path | None = None) -> dict:
    """Per instrument: calibrated products, distinct observations, and (OHRC) the area they cover."""
    shp_root = shp_root or data_root() / "pradan" / "shapefiles"
    out = {"source": str(shp_root)}
    for inst in INSTRUMENTS:
        fp = footprints(inst, shp_root)
        obs = {}
        for pid, f in fp.items():
            obs.setdefault(f["observation"], f["area_km2"])
        row = {"products": len(fp), "observations": len(obs)}
        # Area only for OHRC: its frames are short and rarely overlap, so their sum is the ground they
        # cover. TMC-2 and IIRS strips run for hundreds of km and cross one another on every orbit -
        # summed, they exceed the Moon's whole surface (37.9 million km2) several times.
        if inst == "OHRC":
            areas = [a for a in obs.values() if math.isfinite(a)]
            row.update(area_km2=sum(areas), median_area_km2=statistics.median(areas) if areas else math.nan)
        if inst == "TMC-2":
            row["nadir_products"] = sum(1 for p in fp if "_ncn_" in p)
        out[inst] = row
    return out


def main(argv=None) -> int:
    s = summary()
    for inst in INSTRUMENTS:
        r = s[inst]
        extra = f", {r['nadir_products']} of them nadir" if "nadir_products" in r else ""
        area = (f"; {r['area_km2']:,.0f} km2 (median frame {r['median_area_km2']:.1f} km2)"
                if "area_km2" in r else "")
        print(f"{inst}: {r['products']} calibrated products{extra}; {r['observations']} observations{area}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
