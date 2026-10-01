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


def run(a=None, b=None, log=False, out_root=None, tag="", legs=None):
    """`legs` = (OA stem, AB stem, OB stem) for pairs cut by ops.cut_chain_pairs site, whose ids end in
    _c<candidate index> (e.g. OHRC -> NAC, NAC -> TMC-2, OHRC -> TMC-2 at Site N); otherwise the
    74 S triples site_ohrc_<a>_wNN / site_<a>_<b>_wNN / site_ohrc_<b>_wNN."""
    from evaluation.real_eval import _apply, log_real, loop_closure, map_transform, pixel_to_map
    from core.export import _commit
    out_root = pathlib.Path(out_root or (_data() / "out"))
    if legs:
        oa, ab, ob = (s.lower() for s in legs)
        a, b = oa, ob
        name = f"loop_{oa}_tmc{ob.rsplit('_tmc', 1)[-1]}" if "_tmc" in ob else f"loop_{oa}_{ob}"
        ks, kind = range(0, 40), "loop OHRC->A->B vs OHRC->B (A, B: the AB leg's source and reference)"
    else:
        a, b = a.lower(), b.lower()
        ks, kind = range(1, 20), "loop OHRC->A->B vs OHRC->B"
    results = []
    for k in ks:
        sfx = f"_{tag}" if tag else ""
        if legs:
            ids = {"OA": f"{oa}_c{k:02d}", "AB": f"{ab}_c{k:02d}", "OB": f"{ob}_c{k:02d}"}
            wtag, loop_pid, loop_id = f"c{k:02d}", f"{name}_c{k:02d}", f"{oa} -> {ab} vs {ob} c{k:02d}"
        else:
            ids = {"OA": f"site_ohrc_{a}_w{k:02d}{sfx}", "AB": f"site_{a}_{b}_w{k:02d}{sfx}",
                   "OB": f"site_ohrc_{b}_w{k:02d}{sfx}"}
            wtag, loop_pid, loop_id = f"w{k:02d}", f"loop_{a}_{b}_w{k:02d}{sfx}", f"{a}->{b} w{k:02d}"
        if not all((out_root / i / "report.json").exists() for i in ids.values()):
            continue
        bundles = {n: _leg(i, out_root) for n, i in ids.items()}
        T, ok = {}, True
        for n, (rep, prior) in bundles.items():
            H = rep.get("H_final")
            if H is None:
                ok = False
                break
            T[n] = map_transform(H, prior["source"]["transform"], prior["reference"]["transform"])
        methods = {n: (bundles[n][0].get("declared") or {}).get("method") for n in bundles}
        verdicts = {n: (bundles[n][0].get("trust") or {}).get("verdict") for n in bundles}
        if not ok:
            results.append({"k": k, "ok": False, "methods": methods})
            continue
        src_pts = _inlier_src_points(ids["OA"], out_root)
        if len(src_pts) < 10:
            results.append({"k": k, "ok": False, "why": "too few O->A inliers"})
            continue
        P = pixel_to_map(bundles["OA"][1]["source"]["transform"])
        pts_map = _apply(P, src_pts)
        gsd_b = bundles["OB"][1]["reference"]["resampled_gsd_mpp"]
        gsd_a = bundles["OA"][1]["reference"]["resampled_gsd_mpp"]
        lc = loop_closure([T["OA"], T["AB"]], T["OB"], pts_map, gsd_b)
        res = {"k": k, "ok": True, "n_points": lc["n_points"], "rms_m": lc["rms_m"],
               "p90_m": lc["p90_m"], "max_m": lc["max_m"], "rms_px_B": lc["rms_px"],
               "rms_px_A": lc["rms_m"] / gsd_a, "per_leg_est_m": lc["rms_m"] / np.sqrt(3),
               "methods": methods, "verdicts": verdicts, "ids": ids, "gsd_a": gsd_a, "gsd_b": gsd_b}
        results.append(res)
        print(f"{wtag}: loop RMS {lc['rms_m']:.3f} m = {lc['rms_px']:.3f} px on B's {gsd_b} m grid "
              f"({res['rms_px_A']:.3f} px on A's {gsd_a} m grid); p90 {lc['p90_m']:.3f} m; "
              f"per-registration estimate {res['per_leg_est_m']:.3f} m; "
              f"{lc['n_points']} ground points; methods {set(methods.values())}; verdicts {set(verdicts.values())}")
        if log:
            log_real({"pair_id": loop_pid, "tier": "loop closure (real, 3 legs)",
                      "kind": kind,
                      "source_product": bundles["OA"][1]["source"]["product_id"],
                      "reference_product": f"{bundles['OA'][1]['reference']['product_id']} + "
                                           f"{bundles['OB'][1]['reference']['product_id']}",
                      "window_lat": round(bundles["OA"][1]["window_centre_latlon"][0], 5),
                      "window_lon": round(bundles["OA"][1]["window_centre_latlon"][1], 5),
                      "loop_id": loop_id, "loop_rms_px": round(lc["rms_px"], 4),
                      "loop_p90_px": round(lc["p90_px"], 4), "loop_rms_m": round(lc["rms_m"], 4),
                      "ref_gsd_m": gsd_b, "method_declared": ",".join(sorted(set(methods.values()))),
                      "verdict": ",".join(sorted(set(str(v) for v in verdicts.values()))),
                      "command": "python -m ops.loop_closure " + " ".join(sys.argv[1:]),
                      # until 19 Sep loop rows carried no commit, so no freeze could vouch for them
                      "git_commit": _commit(),
                      "notes": f"legs {ids['OA']}, {ids['AB']}, {ids['OB']} (bundles from commits "
                               f"{sorted({str(bundles[k][0].get('git_commit')) for k in bundles})}); points = O->A source "
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
    ap.add_argument("--a", help="74 S triples: NAC A")
    ap.add_argument("--b", help="74 S triples: NAC B")
    ap.add_argument("--legs", nargs=3, metavar=("OA", "AB", "OB"),
                    help="pair-id stems of three legs cut on shared candidate windows (ids end in _cNN), "
                         "e.g. siten_ohrc2031_nacm1282456834re siten_nacm1282456834re_tmc20200607 "
                         "siten_ohrc2031_tmc20200607")
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--tag", default="")
    x = ap.parse_args(argv)
    if not (x.legs or (x.a and x.b)):
        ap.error("give --a and --b, or --legs")
    run(x.a, x.b, x.log, x.out, x.tag, legs=x.legs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
