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

HARD-SUN WINDOWS (20 Sep 2026). Until then every window used had Sun azimuths under 10 deg
apart (the 74 S OHRC/NAC site), because step 1 demanded NCC >= 0.5 on plain intensity and an
opposite Sun anti-correlates a correct alignment: SAC's equatorial pair (azimuths 174 deg apart)
registers at NCC about -0.6. The rule is now |NCC| >= 0.5 - the same sign change the sun
sweep's rule v2 made on 18 Sep (ops/sun_sweep.py). Every window used before has NCC > +0.5, so
their trials are unchanged; the SAC windows (132-174 deg) can now be used, and each trial row
carries the window's d_sun_azimuth_deg and its true-alignment NCC so REPORT.md can show the two
populations separately. Nothing else - thresholds, displacements, directions, seed - changed.
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
# Non-translation errors (20 Sep 2026). A planted rotation or scale change about the frame centre
# leaves the centre where it was and displaces the CORNERS most, so one number describes it: the
# corner displacement in metres, swept over the same small values as a translation. Both signs of
# each are planted. The frame verdict is the wrong thing to watch here - at 3 m of corner
# displacement it is still `agrees` - so the row also carries what the per-cell map did, which is
# where the information is: `cells_moved_2px` and how many of those the map refused to verify.
KINDS = ("translation", "rotation", "scale")
NON_TRANSLATION_M = [0.0, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]
# SAC's own OHRC <-> NAC pairs, Sun azimuths 132-174 deg apart: the hard-Sun population the
# evidence freeze adds to the calibration's own window list (ops.freeze, step `trust`). Windows
# that fail the rule above (|NCC| < 0.5, not `agrees`, < 50 inliers) are skipped and printed.
EXTRA_WINDOWS = ("sac_ohrc_nac_w*", "sac_polar_ohrc_nac_w*")


def _apply(H, pts):
    p = np.c_[pts, np.ones(len(pts))] @ np.asarray(H, np.float64).T
    return p[:, :2] / p[:, 2:3]


def _n_trials(kind: str, dm: float) -> int:
    """How many trials one (kind, displacement) earns. d = 0 is the false-alarm baseline and is
    the same transform however it is drawn, so it gets 2 either way."""
    if dm == 0:
        return 2
    return N_DIRECTIONS if kind == "translation" else 2


def _about_centre(M2, cx, cy):
    """A 2x2 linear map applied about (cx, cy) instead of the origin."""
    T = np.array([[1.0, 0, cx], [0, 1.0, cy], [0, 0, 1.0]])
    Ti = np.array([[1.0, 0, -cx], [0, 1.0, -cy], [0, 0, 1.0]])
    M = np.eye(3)
    M[:2, :2] = M2
    return T @ M @ Ti


def plant(kind, dpx, angle, shape):
    """The error to compose with the true H, as a 3x3 on the REFERENCE grid.

    `dpx` is the displacement in reference pixels: of every point for a translation, of the
    frame's CORNERS for a rotation or a scale change (both about the frame centre, so the centre
    does not move and the corners move most). `angle` is the direction for a translation and the
    sign for the other two. Returns the identity when dpx is 0.
    """
    if dpx == 0:
        return np.eye(3)
    if kind == "translation":
        return np.array([[1.0, 0, dpx * np.cos(angle)], [0, 1.0, dpx * np.sin(angle)], [0, 0, 1.0]])
    h, w = int(shape[0]), int(shape[1])
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    radius = float(np.hypot(cx, cy))            # centre -> corner, in reference pixels
    s = 1.0 if angle >= 0 else -1.0
    if kind == "rotation":
        th = s * dpx / radius                   # arc length dpx at the corner
        return _about_centre(np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]), cx, cy)
    if kind == "scale":
        k = 1.0 + s * dpx / radius
        return _about_centre(np.array([[k, 0.0], [0.0, k]]), cx, cy)
    raise ValueError(f"unknown planted-error kind {kind!r}")


def cell_effect(ref_shape, H_wrong, H_true, state):
    """Per-cell: how far the planted error moved the cell, against what the map said about it.

    The frame verdict is the wrong thing to watch for a rotation or a scale error - it stays
    `agrees` while a corner is already 3 px out - so this records what the 8x8 map did:
    of the cells the error actually moved by more than 2 px, how many did the map refuse to
    verify, and of the cells it barely moved (under 1 px), how many stayed verified.
    """
    from core.reliability import VERIFIED, _true_error_grid
    te = _true_error_grid(tuple(ref_shape), H_wrong, H_true, state.shape[0])
    ver = state == VERIFIED
    moved, still = te > 2.0, te < 1.0
    return {"cells_moved_2px": int(moved.sum()), "moved_not_verified": int((moved & ~ver).sum()),
            "cells_under_1px": int(still.sum()), "under_1px_verified": int((still & ver).sum()),
            "max_cell_displacement_px": round(float(np.nanmax(te)), 3)}


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
        # |NCC|: an opposite Sun anti-correlates a correct alignment (see the docstring).
        good = (r["declared"]["method"] == "loftr+magsac++" and rel.get("global", {}).get("verdict") == "agrees"
                and ncc is not None and abs(ncc) >= 0.5 and len(r["src_inliers"]) >= 50)
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
        # Translations first, drawing from the RNG exactly as before this file learned the other
        # two kinds, so that population's trials do not shift when a kind is added after it.
        for kind in KINDS:
            for dm in (DISPLACEMENTS_M if kind == "translation" else NON_TRANSLATION_M):
                # A translation can point anywhere, so it is sampled over N_DIRECTIONS random
                # bearings. A rotation or a scale change about the centre has only TWO shapes -
                # one per sign - so eight iterations would re-plant four identical transforms and
                # differ only in the match noise, at four times the cost.
                for k in range(_n_trials(kind, dm)):
                    th = rng.uniform(0, 2 * np.pi)
                    dpx = dm / gsd_ref
                    ang = th if kind == "translation" else (1.0 if k % 2 == 0 else -1.0)
                    Hw = plant(kind, dpx, ang, B.shape[:2]) @ H
                    ref_w = _apply(Hw, src_in) + rng.normal(0, 0.3, src_in.shape)
                    warped = warp(A, Hw, B.shape[:2])
                    relw = reliability_map(B.shape[:2], src_in.astype(np.float32), ref_w.astype(np.float32),
                                           Hw, src_in.astype(np.float32), ref_w.astype(np.float32),
                                           warped, B, gsd_mpp=r["gsd_mpp"], H_true=None)
                    g, c = relw["global"], relw["counts"]
                    trials.append({"pair_id": d.name, "gsd_ref_m": gsd_ref, "kind": kind,
                                   "displacement_m": dm,
                                   "displacement_px": round(dpx, 3), "direction_deg": round(np.degrees(th), 1),
                                   "contradicted": bool(g.get("contradicted")), "verdict": g.get("verdict"),
                                   "verified": c["verified"], "weak": c["weak"], "no_evidence": c["no_evidence"],
                                   "d_sun_azimuth_deg": prior.get("d_sun_azimuth_deg"),
                                   "ncc_true": round(ncc, 3),
                                   **cell_effect(B.shape[:2], Hw, H, relw["state"])})
    if not trials:
        print("no usable windows")
        return 1
    fields = list(trials[0])
    new = not OUT_CSV.exists() or OUT_CSV.stat().st_size == 0
    if not new:
        with open(OUT_CSV, encoding="utf-8-sig", newline="") as f:
            header = next(csv.reader(f))
        if header != fields:
            # An older CSV has fewer columns; appending under its header would put values in
            # the wrong columns. The freeze deletes the file first; do the same by hand.
            print(f"refusing to append: {OUT_CSV.name} has columns {header}, this run writes "
                  f"{fields}. Delete the file (ops.freeze does) and re-run.")
            return 2
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerows(trials)
    print(f"\n{len(used)} windows, {len(trials)} trials -> {OUT_CSV.name}")
    print(f"{'kind':12} {'d (m)':>6} {'d (px)':>7} {'n':>4} {'contradicted':>13} {'mean verified':>13} "
          f"{'cells >2px refused':>19} {'cells <1px kept':>16}")
    rows = []
    for kind in KINDS:
        for dm in (DISPLACEMENTS_M if kind == "translation" else NON_TRANSLATION_M):
            t = [x for x in trials if x["kind"] == kind and x["displacement_m"] == dm]
            if not t:
                continue
            rate = float(np.mean([x["contradicted"] for x in t]))
            ver = float(np.mean([x["verified"] for x in t]))
            dpx = float(np.median([x["displacement_px"] for x in t]))
            nm = sum(x["cells_moved_2px"] for x in t)
            mnv = sum(x["moved_not_verified"] for x in t)
            ns = sum(x["cells_under_1px"] for x in t)
            sv = sum(x["under_1px_verified"] for x in t)
            rows.append((kind, dm, dpx, len(t), rate, ver, nm, mnv, ns, sv))
            print(f"{kind:12} {dm:6.1f} {dpx:7.2f} {len(t):4d} {rate:13.1%} {ver:13.1f} "
                  f"{(f'{mnv}/{nm}' if nm else '-'):>19} {(f'{sv}/{ns}' if ns else '-'):>16}")
    if a.log:
        from core.pipeline import _log_row
        az = sorted({str(t["d_sun_azimuth_deg"]) for t in trials})
        for kind, dm, dpx, n, rate, ver, nm, mnv, ns, sv in rows:
            what = {"translation": f"H_true shifted by {dm:g} m (~{dpx:.2f} px of the reference grid)",
                    "rotation": f"H_true rotated about the frame centre until the CORNERS move {dm:g} m "
                                f"(~{dpx:.2f} px); the centre does not move",
                    "scale": f"H_true scaled about the frame centre until the CORNERS move {dm:g} m "
                             f"(~{dpx:.2f} px); the centre does not move"}[kind]
            ok, note = _log_row(
                f"trust_real_calibration_{kind}_d{dm:g}m",
                "B (OHRC-NAC real) + A (NAC-NAC real), planted failures",
                "reliability_real_calibration",
                {"rmse_gt_px": None, "residual_px": None, "inlier_count": None, "inlier_ratio": None,
                 "grid_coverage_fraction": None, "distribution_cv": None, "n_matches": n, "status": "ok"},
                config=(f"planted confident-wrong registrations, kind {kind}: {what}, all matches "
                        f"consistent with the wrong H (0.3 px noise); {len(used)} real windows x "
                        f"{_n_trials(kind, dm)} "
                        f"{'directions' if kind == 'translation' else 'signs'}; seed {a.seed}"),
                notes=(f"area check contradicted {rate:.1%} of {n} trials; mean verified cells "
                       f"{ver:.1f}/64. d=0 is the false-alarm baseline. "
                       + (f"Per cell: of the {nm} cells this error moved by more than 2 px the map refused "
                          f"to verify {mnv} ({100 * mnv / nm:.1f} %); of the {ns} cells it moved by less "
                          f"than 1 px, {sv} stayed verified ({100 * sv / max(ns, 1):.1f} %). " if nm or ns else "")
                       + f"windows: {', '.join(used)} "
                       f"(Sun azimuth differences {', '.join(az)} deg; window selection by |NCC| >= 0.5). "
                       f"per-trial table: evaluation/trust_real_calibration.csv"))
            print(("  " + note) if ok else f"  NOT LOGGED: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
