"""Does the trust layer catch a confident, wrong registration on REAL imagery?

    python -m ops.trust_real_calibration "site_ohrc_m1153871873le_w*_t" "site_ohrc_m1363141432re_w*_t" --log

The synthetic calibration (core/reliability_calibration.csv) says the area check catches
77 % of failures at 0 % false alarms on rendered pairs. This is the same question on real
Chandrayaan-2 OHRC / LROC NAC windows, with ground truth we control:

  1. Register the window. Keep it only if the registration is independently good (the
     matcher's H is declared, the area check agrees, and the warped source correlates
     with the reference at NCC >= 0.5) - these are the windows whose loops close to
     ~0.1 m (ops/loop_closure.py).
  2. Plant a failure: H_wrong = (shift by d metres in direction theta) o H_true, and a
     match set that agrees with H_wrong PERFECTLY - every match an inlier, 0.3 px noise.
     To the matcher's own statistics this is a flawless registration. It is the Tier D
     failure mode (confident consensus on a wrong answer), placed on real imagery.
  3. Run core.reliability.reliability_map exactly as run_all does, and record whether
     the area check contradicts H_wrong, and how many cells it still verifies.

d = 0 is the false-alarm baseline (the planted matches then agree with the true H).
Every trial is written to evaluation/trust_real_calibration.csv; with --log one summary
row per displacement goes to results_log.csv (method `reliability_real_calibration`).
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "evaluation" / "trust_real_calibration.csv"
DISPLACEMENTS_M = [0.0, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]
N_DIRECTIONS = 8


def _apply(H, pts):
    p = np.c_[pts, np.ones(len(pts))] @ np.asarray(H, np.float64).T
    return p[:, :2] / p[:, 2:3]


def main(argv=None):
    import cv2
    from core.io_loader import load
    from core.pipeline import resolve_pair, run_all
    from core.ransac import warp
    from core.reliability import reliability_map
    from ops.sun_sweep import warp_ncc
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("patterns", nargs="+")
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(a.seed)
    dirs = sorted({pathlib.Path(p) for pat in a.patterns for p in glob.glob(str(ROOT / "data" / "pairs" / pat))})
    trials, used = [], []
    for d in dirs:
        sp, rp = resolve_pair(str(d))
        r = run_all(sp, rp)
        A, B = load(sp)[0], load(rp)[0]
        rel = r["reliability"] or {}
        ncc = warp_ncc(A, B, r["H"])
        good = (r["declared"]["method"] == "loftr+magsac++" and rel.get("global", {}).get("verdict") == "agrees"
                and ncc is not None and ncc >= 0.5 and len(r["src_inliers"]) >= 50)
        print(f"{d.name}: declared {r['declared']['method']}, verdict {rel.get('global', {}).get('verdict')}, "
              f"NCC {ncc if ncc is None else round(ncc, 3)}, inliers {len(r['src_inliers'])} -> "
              f"{'USED' if good else 'skipped'}", flush=True)
        if not good:
            continue
        used.append(d.name)
        prior = json.loads((d / "geometry_prior.json").read_text(encoding="utf-8"))
        gsd_ref = prior["reference"]["resampled_gsd_mpp"]
        H = np.asarray(r["H"], np.float64)
        src_in = np.asarray(r["src_inliers"], np.float64)
        for dm in DISPLACEMENTS_M:
            for k in range(N_DIRECTIONS if dm > 0 else 2):
                th = rng.uniform(0, 2 * np.pi)
                dpx = dm / gsd_ref
                T = np.array([[1, 0, dpx * np.cos(th)], [0, 1, dpx * np.sin(th)], [0, 0, 1.0]])
                Hw = T @ H
                ref_w = _apply(Hw, src_in) + rng.normal(0, 0.3, src_in.shape)
                warped = warp(A, Hw, B.shape[:2])
                relw = reliability_map(B.shape[:2], src_in.astype(np.float32), ref_w.astype(np.float32),
                                       Hw, src_in.astype(np.float32), ref_w.astype(np.float32),
                                       warped, B, gsd_mpp=r["gsd_mpp"], H_true=None)
                g, c = relw["global"], relw["counts"]
                trials.append({"pair_id": d.name, "gsd_ref_m": gsd_ref, "displacement_m": dm,
                               "displacement_px": round(dpx, 3), "direction_deg": round(np.degrees(th), 1),
                               "contradicted": bool(g.get("contradicted")), "verdict": g.get("verdict"),
                               "verified": c["verified"], "weak": c["weak"], "no_evidence": c["no_evidence"]})
    if not trials:
        print("no usable windows")
        return 1
    new = not OUT_CSV.exists()
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(trials[0]))
        if new:
            w.writeheader()
        w.writerows(trials)
    print(f"\n{len(used)} windows, {len(trials)} trials -> {OUT_CSV.name}")
    print(f"{'d (m)':>6} {'d (px)':>7} {'n':>4} {'contradicted':>13} {'mean verified cells':>20}")
    rows = []
    for dm in DISPLACEMENTS_M:
        t = [x for x in trials if x["displacement_m"] == dm]
        rate = np.mean([x["contradicted"] for x in t])
        ver = np.mean([x["verified"] for x in t])
        dpx = np.median([x["displacement_px"] for x in t])
        rows.append((dm, dpx, len(t), rate, ver))
        print(f"{dm:6.1f} {dpx:7.2f} {len(t):4d} {rate:13.1%} {ver:20.1f}")
    if a.log:
        from core.pipeline import _log_row
        for dm, dpx, n, rate, ver in rows:
            ok, note = _log_row(
                f"trust_real_calibration_d{dm:g}m", "B (OHRC-NAC real) + A (NAC-NAC real), planted failures",
                "reliability_real_calibration",
                {"rmse_gt_px": None, "residual_px": None, "inlier_count": None, "inlier_ratio": None,
                 "grid_coverage_fraction": None, "distribution_cv": None, "n_matches": n, "status": "ok"},
                config=(f"planted confident-wrong registrations: H_true shifted by {dm:g} m (~{dpx:.2f} px of "
                        f"the reference grid), all matches consistent with the wrong H (0.3 px noise); "
                        f"{len(used)} real windows x {N_DIRECTIONS if dm > 0 else 2} directions; seed {a.seed}"),
                notes=(f"area check contradicted {rate:.1%} of {n} trials; mean verified cells "
                       f"{ver:.1f}/64. d=0 is the false-alarm baseline. windows: {', '.join(used)}. "
                       f"per-trial table: evaluation/trust_real_calibration.csv"))
            print(("  " + note) if ok else f"  NOT LOGGED: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
