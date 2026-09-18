"""Loop closure over real triples: the accuracy evidence when no ground truth exists.

    python -m ops.loop_closure --a M1153871873LE --b M1363141432RE --log

For every window k cut at the same ground centre for all three legs
    O -> A   site_ohrc_<a>_w0k        (Chandrayaan-2 OHRC -> NAC A)
    A -> B   site_<a>_<b>_w0k         (NAC A -> NAC B)
    O -> B   site_ohrc_<b>_w0k        (OHRC -> NAC B)
each registration H is turned into a map -> map transform with its window's exact
geotransforms, the chain T_AB(T_OA(p)) is compared with the direct T_OB(p), and the
disagreement is reported in metres and in reference pixels. Three independent
registrations that are each right agree; a wrong one - however confident - does not.
If the three errors are independent and similar, each registration's error is about
loop / sqrt(3); that estimate is printed and labelled as an estimate.

Points: the source inlier locations of the O -> A leg (from its matches.csv), mapped to
map metres - the ground the registrations actually rest on, not an extrapolation.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _data():
    p = ROOT / "data_path.txt"
    return pathlib.Path(p.read_text(encoding="utf-8-sig").strip())


def _leg(pair_id, out_root):
    rep = json.loads((out_root / pair_id / "report.json").read_text(encoding="utf-8"))
    prior = json.loads((ROOT / "data" / "pairs" / pair_id / "geometry_prior.json").read_text(encoding="utf-8"))
    return rep, prior


def _inlier_src_points(pair_id, out_root):
    with open(out_root / pair_id / "matches.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(line for line in f if not line.startswith("#"))]
    return np.array([[float(r["src_x"]), float(r["src_y"])] for r in rows if r["is_inlier"] == "1"])


def run(a, b, log=False, out_root=None, tag=""):
    from evaluation.real_eval import _apply, log_real, loop_closure, map_transform, pixel_to_map
    out_root = pathlib.Path(out_root or (_data() / "out"))
    a, b = a.lower(), b.lower()
    results = []
    for k in range(1, 20):
        sfx = f"_{tag}" if tag else ""
        ids = {"OA": f"site_ohrc_{a}_w{k:02d}{sfx}", "AB": f"site_{a}_{b}_w{k:02d}{sfx}",
               "OB": f"site_ohrc_{b}_w{k:02d}{sfx}"}
        if not all((out_root / i / "report.json").exists() for i in ids.values()):
            continue
        legs = {n: _leg(i, out_root) for n, i in ids.items()}
        T, ok = {}, True
        for n, (rep, prior) in legs.items():
            H = rep.get("H_final")
            if H is None:
                ok = False
                break
            T[n] = map_transform(H, prior["source"]["transform"], prior["reference"]["transform"])
        methods = {n: (legs[n][0].get("declared") or {}).get("method") for n in legs}
        verdicts = {n: (legs[n][0].get("trust") or {}).get("verdict") for n in legs}
        if not ok:
            results.append({"k": k, "ok": False, "methods": methods})
            continue
        src_pts = _inlier_src_points(ids["OA"], out_root)
        if len(src_pts) < 10:
            results.append({"k": k, "ok": False, "why": "too few O->A inliers"})
            continue
        P = pixel_to_map(legs["OA"][1]["source"]["transform"])
        pts_map = _apply(P, src_pts)
        gsd_b = legs["OB"][1]["reference"]["resampled_gsd_mpp"]
        gsd_a = legs["OA"][1]["reference"]["resampled_gsd_mpp"]
        lc = loop_closure([T["OA"], T["AB"]], T["OB"], pts_map, gsd_b)
        res = {"k": k, "ok": True, "n_points": lc["n_points"], "rms_m": lc["rms_m"],
               "p90_m": lc["p90_m"], "max_m": lc["max_m"], "rms_px_B": lc["rms_px"],
               "rms_px_A": lc["rms_m"] / gsd_a, "per_leg_est_m": lc["rms_m"] / np.sqrt(3),
               "methods": methods, "verdicts": verdicts, "ids": ids, "gsd_a": gsd_a, "gsd_b": gsd_b}
        results.append(res)
        print(f"w{k:02d}: loop RMS {lc['rms_m']:.3f} m = {lc['rms_px']:.3f} px on B's {gsd_b} m grid "
              f"({res['rms_px_A']:.3f} px on A's {gsd_a} m grid); p90 {lc['p90_m']:.3f} m; "
              f"per-registration estimate {res['per_leg_est_m']:.3f} m; "
              f"{lc['n_points']} ground points; methods {set(methods.values())}; verdicts {set(verdicts.values())}")
        if log:
            log_real({"pair_id": f"loop_{a}_{b}_w{k:02d}{sfx}", "tier": "loop closure (real, 3 legs)",
                      "kind": "loop OHRC->A->B vs OHRC->B",
                      "source_product": legs["OA"][1]["source"]["product_id"],
                      "reference_product": f"{legs['OA'][1]['reference']['product_id']} + "
                                           f"{legs['OB'][1]['reference']['product_id']}",
                      "window_lat": round(legs["OA"][1]["window_centre_latlon"][0], 5),
                      "window_lon": round(legs["OA"][1]["window_centre_latlon"][1], 5),
                      "loop_id": f"{a}->{b} w{k:02d}", "loop_rms_px": round(lc["rms_px"], 4),
                      "loop_p90_px": round(lc["p90_px"], 4), "loop_rms_m": round(lc["rms_m"], 4),
                      "ref_gsd_m": gsd_b, "method_declared": ",".join(sorted(set(methods.values()))),
                      "verdict": ",".join(sorted(set(str(v) for v in verdicts.values()))),
                      "command": "python -m ops.loop_closure " + " ".join(sys.argv[1:]),
                      "notes": f"legs {ids['OA']}, {ids['AB']}, {ids['OB']}; points = O->A source "
                               f"inliers mapped to map metres; per-registration estimate = loop/sqrt(3) "
                               f"= {res['per_leg_est_m']:.3f} m (assumes independent, similar errors)"})
    good = [r for r in results if r.get("ok")]
    if good:
        rms = np.array([r["rms_m"] for r in good])
        print(f"\n{len(good)} closed loops: loop RMS median {np.median(rms):.3f} m, "
              f"max {rms.max():.3f} m; per-registration estimate median {np.median(rms) / np.sqrt(3):.3f} m")
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--tag", default="")
    x = ap.parse_args(argv)
    run(x.a, x.b, x.log, x.out, x.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
