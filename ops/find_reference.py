"""Pick the reference for a Chandrayaan-2 image by its Sun.

    python -m ops.find_reference ch2_ohr_ncp_20250612T2031048828_d_img_d18 [--top 12] [--min-overlap 0.2]

Registration across very different Suns is the hard case (REPORT: 0 of 12 accepted with the Suns 60-120
deg apart). The remedy is to choose the reference: among every image that covers the same ground, take
the one lit most like the Chandrayaan-2 image. This lists them, best Sun first:

  * candidates: every PRADAN product (OHRC, TMC-2 nadir, IIRS) in the footprint catalogue
    (ops/pradan_archive.py), and every LRO NAC this machine has an LROC page or an ODE record for
    (<data>/nac/*pages.json, <data>/ode/*.json);
  * overlap: the share of the Chandrayaan-2 footprint the candidate covers (convex quadrilaterals clipped
    on a plane tangent to the Moon at the footprint's centre);
  * Sun: the angle between the two Sun directions at that centre, from each image's start time
    (ops/lunar_sun.py: Meeus, checked against LROC's own sub-solar points) - PRADAN's catalogue carries
    no Sun, its angle fields are zero.

Site N (REPORT, "One site, every camera") was found this way by hand on 1 Oct 2026; this is that search
as a tool.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ops import pradan_archive as A          # noqa: E402
from ops.lunar_sun import sun_angle_between, sun_at  # noqa: E402

R_KM = A.R_KM


# --- geometry on a local tangent plane ----------------------------------------------------------

def to_plane(lat, lon, lat0, lon0):
    """(x, y) km on an equirectangular plane centred at (lat0, lon0); fine over a footprint's extent."""
    dlon = (lon - lon0 + 180.0) % 360.0 - 180.0
    return (math.radians(dlon) * R_KM * math.cos(math.radians(lat0)), math.radians(lat - lat0) * R_KM)


def area(poly) -> float:
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))


def ccw(poly):
    return poly if area(poly) >= 0 else poly[::-1]


def clip(subject, clipper):
    """Sutherland-Hodgman: the part of convex `subject` inside convex `clipper` (both counter-clockwise)."""
    out = list(subject)
    for (ax, ay), (bx, by) in zip(clipper, clipper[1:] + clipper[:1]):
        if not out:
            break
        inside = lambda p: (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax) >= 0  # noqa: E731

        def cross(p, q):
            x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
            den = (x1 - x2) * (ay - by) - (y1 - y2) * (ax - bx)
            if den == 0:
                return q
            t = ((x1 - ax) * (ay - by) - (y1 - ay) * (ax - bx)) / den
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        src, out = out, []
        for k, q in enumerate(src):
            p = src[k - 1]
            if inside(q):
                if not inside(p):
                    out.append(cross(p, q))
                out.append(q)
            elif inside(p):
                out.append(cross(p, q))
    return out


def overlap_fraction(target_ll, other_ll, lat0, lon0) -> float:
    t = ccw([to_plane(la, lo, lat0, lon0) for la, lo in target_ll])
    o = ccw([to_plane(la, lo, lat0, lon0) for la, lo in other_ll])
    a = abs(area(t))
    inter = clip(t, o)
    return abs(area(inter)) / a if a and len(inter) >= 3 else 0.0


def centre(corners):
    lat = sum(c[0] for c in corners) / len(corners)
    lon0 = corners[0][1]
    lon = lon0 + sum(((c[1] - lon0 + 180) % 360) - 180 for c in corners) / len(corners)
    return lat, lon % 360.0


# --- candidates -----------------------------------------------------------------------------

def pradan_records(shp_root=None) -> list[dict]:
    shp_root = shp_root or A.data_root() / "pradan" / "shapefiles"
    out, seen = [], set()
    for inst, (folder, stem) in A.INSTRUMENTS.items():
        for dbf in sorted((shp_root / folder).rglob(f"{stem}*.dbf")):
            polar = next((p for p in ("np", "sp") if dbf.stem.endswith(f"_{p}")), None)
            for rec in A.read_dbf(dbf):
                pid = rec["PRODUCT_ID"]
                if pid in seen or (inst == "TMC-2" and "_ncn_" not in pid):
                    continue
                seen.add(pid)
                try:
                    corners = A.corners_of(rec, polar)
                except (ValueError, KeyError):
                    continue
                out.append({"id": pid, "instrument": inst, "time": rec["OBS_ST_TIME"], "corners": corners})
    return out


def nac_records(data=None) -> list[dict]:
    """LRO NACs this machine knows: LROC product pages (corners) and ODE records (bounding boxes)."""
    data = data or A.data_root()
    out, seen = [], set()
    for p in sorted((data / "nac").glob("*pages.json")):
        for r in json.loads(p.read_text(encoding="utf-8")):
            if not isinstance(r, dict) or "Start time" not in r or r.get("pid") in seen:
                continue
            try:
                corners = [(float(r[f"{c} latitude"]), float(r[f"{c} longitude"]))
                           for c in ("Upper left", "Upper right", "Lower right", "Lower left")]
            except (KeyError, ValueError):
                continue
            seen.add(r["pid"])
            out.append({"id": r["pid"], "instrument": "LRO NAC",
                        "time": re.sub(r"^\(DOY:\d+\)\s*", "", r["Start time"]), "corners": corners})
    for p in sorted((data / "ode").glob("*EDRNAC*.json")):
        j = json.loads(p.read_text(encoding="utf-8"))
        prods = (((j.get("ODEResults") or {}).get("Products") or {}).get("Product")) if isinstance(j, dict) else None
        for r in (prods if isinstance(prods, list) else []):
            pid = (r.get("pdsid") or "").split(".")[-1].upper()
            if not pid or pid in seen:
                continue
            try:
                s, n = float(r["Minimum_latitude"]), float(r["Maximum_latitude"])
                w, e = float(r["Westernmost_longitude"]), float(r["Easternmost_longitude"])
            except (KeyError, ValueError, TypeError):
                continue
            seen.add(pid)
            out.append({"id": pid, "instrument": "LRO NAC", "time": r.get("UTC_start_time"),
                        "corners": [(n, w), (n, e), (s, e), (s, w)]})
    return out


def rank(target_id: str, records: list[dict], min_overlap: float = 0.2) -> tuple[dict, list[dict]]:
    by_id = {r["id"]: r for r in records}
    if target_id not in by_id:
        raise SystemExit(f"{target_id} is not in PRADAN's footprint catalogue on this machine")
    tgt = by_id[target_id]
    lat0, lon0 = centre(tgt["corners"])
    inc0, az0 = sun_at(tgt["time"], lat0, lon0)
    out = []
    for r in records:
        if r["id"] == target_id or not r.get("time"):
            continue
        if min(abs(((c[1] - lon0 + 180) % 360) - 180) for c in r["corners"]) > 30 and \
                max(abs(c[0]) for c in r["corners"]) < 80:
            continue                                             # nowhere near (cheap pre-filter)
        f = overlap_fraction(tgt["corners"], r["corners"], lat0, lon0)
        if f < min_overlap:
            continue
        inc, az = sun_at(r["time"], lat0, lon0)
        out.append({**r, "overlap": f, "sun_angle": sun_angle_between(tgt["time"], r["time"], lat0, lon0),
                    "incidence": inc, "azimuth": az, "d_azimuth": abs((az - az0 + 180) % 360 - 180)})
    out.sort(key=lambda r: r["sun_angle"])
    return {**tgt, "centre": (lat0, lon0), "incidence": inc0, "azimuth": az0}, out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("product_id", help="a Chandrayaan-2 product id from PRADAN's catalogue")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--min-overlap", type=float, default=0.2, help="share of the target footprint covered")
    a = ap.parse_args(argv)
    tgt, cands = rank(a.product_id, pradan_records() + nac_records(), a.min_overlap)
    la, lo = tgt["centre"]
    print(f"{tgt['id']} ({tgt['instrument']}, {tgt['time']}): centre {la:.3f}, {lo:.3f}; Sun incidence "
          f"{tgt['incidence']:.1f} deg, azimuth {tgt['azimuth']:.1f} deg")
    print(f"{len(cands)} images cover at least {a.min_overlap:.0%} of it; best Sun first:")
    print(f"  {'image':46s} {'instrument':10s} {'covers':>6s} {'Sun apart':>9s} {'d_azimuth':>9s} {'incidence':>9s}  time")
    for r in cands[:a.top]:
        print(f"  {r['id']:46s} {r['instrument']:10s} {r['overlap']:6.0%} {r['sun_angle']:8.1f}° "
              f"{r['d_azimuth']:8.1f}° {r['incidence']:8.1f}°  {r['time']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
