"""Calibrate the three reliability states against exact ground truth.

    python -m core.reliability_calibrate --dem <dem.npy> --pixel-size 60 \
        --sweep 0,15,30,45 --repeats 5 [--log]

This is the measurement that can kill the novelty claim, which is why it runs
first (ops/PHASE1_NOVELTY_DECISION.md, M1). For every synthetic pair in the sun
sweep - the same pairs, shifts and seeds the Gate 2 rows use - every 8x8 cell gets
its reliability state from `core/reliability.py` AND its TRUE error against the
known transform. If the "verified" cells are not measurably more accurate than the
"weak" ones, the map is a colour scheme and the claim is withdrawn.

Outputs
  core/reliability_calibration.csv          one row per cell per pair (the evidence)
  core/reliability_calibration_summary.csv  per state, pooled and per sun delta
  evaluation/results_log.csv                one row per pair when --log is given,
                                            through the same `_log_row` as the sweep

Numbers reach a slide only from results_log.csv (Invariant 1). The per-cell file
is for the figure and for anyone who wants to re-derive the summary.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

import numpy as np

from core.pipeline import (SYNTH_SHIFT_PX, _draw_shift, _log_preflight, _print_report,
                           _synthetic_pair, run_all)
from core.reliability import NO_EVIDENCE, VERIFIED, WEAK

HERE = pathlib.Path(__file__).resolve().parent
CELLS_CSV = HERE / "reliability_calibration.csv"
SUMMARY_CSV = HERE / "reliability_calibration_summary.csv"

CELL_FIELDS = ["pair_id", "sun_delta_deg", "shift_x", "shift_y", "seed", "gsd_mpp",
               "cell_row", "cell_col", "state", "n_inliers", "n_raw", "local_inlier_ratio",
               "median_inlier_residual_px", "area_dx", "area_dy", "area_ncc", "area_agrees",
               "true_error_px", "true_error_m", "global_contradicted", "global_shift_dx",
               "global_shift_dy", "global_ncc", "method_used", "fallback_rmse_gt_px",
               "pair_rmse_gt_px", "pair_inlier_ratio"]


def _f(v):
    return None if v is None or (isinstance(v, float) and not np.isfinite(v)) else v


def _stats(errs, gsd):
    e = np.asarray([x for x in errs if x is not None and np.isfinite(x)], dtype=float)
    if len(e) == 0:
        return {"n": 0, "median_px": None, "p90_px": None, "max_px": None,
                "frac_under_0p5px": None, "frac_under_1px": None, "median_m": None}
    return {"n": int(len(e)), "median_px": float(np.median(e)),
            "p90_px": float(np.percentile(e, 90)), "max_px": float(e.max()),
            "frac_under_0p5px": float((e < 0.5).mean()), "frac_under_1px": float((e < 1.0).mean()),
            "median_m": float(np.median(e) * gsd) if gsd else None}


def log_summary_row(pixel_size, method="ours_loftr+subpixel") -> tuple[bool, str]:
    """One pooled row in results_log.csv, so the calibration table can be quoted at all.

    Invariant 1: a number reaches a slide only from evaluation/results_log.csv. The
    per-cell file and the summary CSV are the derivation; this row is the citation.
    """
    from core.pipeline import _log_row
    rows = list(csv.DictReader(open(SUMMARY_CSV, encoding="utf-8")))
    pooled = {r["state"]: r for r in rows if r["group"] == "all"}
    n_pairs = len({c["pair_id"] for c in csv.DictReader(open(CELLS_CSV, encoding="utf-8"))})
    parts = []
    for st in (VERIFIED, WEAK, NO_EVIDENCE):
        r = pooled.get(st, {})
        if r.get("n") and int(r["n"]):
            parts.append(f"{st}: n={r['n']} cells, median true error {float(r['median_px']):.3f} px "
                         f"({float(r['median_m']):.1f} m), p90 {float(r['p90_px']):.3f} px, "
                         f"{float(r['frac_under_0p5px']):.0%} under 0.5 px, "
                         f"{float(r['frac_under_1px']):.0%} under 1 px")
    per_delta = []
    for d in sorted({r["group"] for r in rows if r["group"] != "all"}):
        v = next((r for r in rows if r["group"] == d and r["state"] == VERIFIED), None)
        w = next((r for r in rows if r["group"] == d and r["state"] == WEAK), None)
        seg = f"{d}: verified"
        seg += (f" n={v['n']} median {float(v['median_px']):.3f} px"
                if v and v.get("n") and int(v["n"]) else " n=0")
        seg += (f"; weak n={w['n']} median {float(w['median_px']):.3f} px"
                if w and w.get("n") and int(w["n"]) else "; weak n=0")
        per_delta.append(seg)
    metrics = {"rmse_gt_px": None, "residual_px": None, "inlier_count": None,
               "inlier_ratio": None, "grid_coverage_fraction": None, "distribution_cv": None,
               "n_matches": None, "status": "ok"}
    return _log_row("reliability_calibration_pooled", "synthetic", "reliability_calibration",
                    metrics,
                    config=(f"matcher arm: {method}; pooled over {n_pairs} synthetic pairs (sun "
                            f"azimuth deltas 0/15/30/45 deg x 5 off-grid shifts), 64 cells each; "
                            f"true error per cell = RMS of "
                            f"|H(H_true^-1 p) - p| over a 5x5 grid of reference points; derivation in "
                            f"core/reliability_calibration.csv and core/reliability_calibration_summary.csv"),
                    gsd_mpp=pixel_size,
                    notes="M1 CALIBRATION. " + "; ".join(parts) + " | per delta: " + " | ".join(per_delta))


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log-summary-only", action="store_true",
                   help="do not run anything; log one pooled row from the existing summary CSV")
    p.add_argument("--dem", required=False)
    p.add_argument("--pixel-size", type=float, required=True)
    p.add_argument("--sweep", default="0,15,30,45")
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-size", type=int, default=640)
    p.add_argument("--log", action="store_true", help="also append one row per pair to results_log.csv")
    p.add_argument("--quiet", action="store_true", help="skip the per-pair report")
    p.add_argument("--no-subpixel", action="store_true",
                   help="run the matcher without NCC refinement (the pre-3-Sep default)")
    args = p.parse_args(argv[1:])
    use_subpixel = not args.no_subpixel
    method = "ours_loftr+subpixel" if use_subpixel else "ours_loftr"

    if args.log_summary_only:
        err = _log_preflight()
        if err:
            print(err)
            return 3
        ok, note = log_summary_row(args.pixel_size, method)
        print(("  " + note) if ok else f"\n{note}\n")
        return 0 if ok else 3

    deltas = [float(d) for d in args.sweep.split(",") if d.strip()]
    if args.log:
        err = _log_preflight()
        if err:
            print(err)
            return 3

    cell_rows, pair_rows = [], []
    for d in deltas:
        for rep in range(args.repeats):
            shift = tuple(SYNTH_SHIFT_PX) if rep == 0 else _draw_shift(args.seed + rep)
            src, ref, H_true, meta = _synthetic_pair(args.dem, args.pixel_size, d, shift_px=shift,
                                                     seed=args.seed + rep, max_size=args.max_size)
            r = run_all(src, ref, H_true=H_true, progress=None, subpixel=use_subpixel)
            if not args.quiet:
                _print_report(r)
            rel = r.get("reliability")
            if rel is None:
                print(f"  {meta['pair_id']}: no reliability map ({r.get('reliability_note')})")
                continue
            g = rel["global"]
            m = r.get("metrics") or {}
            fb = r.get("fallback") or {}
            for rr in range(rel["state"].shape[0]):
                for cc in range(rel["state"].shape[1]):
                    te = rel["true_error_px"][rr, cc] if rel.get("true_error_px") is not None else None
                    cell_rows.append({
                        "pair_id": meta["pair_id"], "sun_delta_deg": d, "shift_x": shift[0],
                        "shift_y": shift[1], "seed": args.seed + rep, "gsd_mpp": args.pixel_size,
                        "cell_row": rr, "cell_col": cc, "state": rel["state"][rr, cc],
                        "n_inliers": int(rel["n_inliers"][rr, cc]), "n_raw": int(rel["n_raw"][rr, cc]),
                        "local_inlier_ratio": _f(float(rel["local_inlier_ratio"][rr, cc])),
                        "median_inlier_residual_px": _f(float(rel["median_inlier_residual_px"][rr, cc])),
                        "area_dx": _f(float(rel["area_shift_dx"][rr, cc])),
                        "area_dy": _f(float(rel["area_shift_dy"][rr, cc])),
                        "area_ncc": _f(float(rel["area_ncc"][rr, cc])),
                        "area_agrees": bool(rel["area_agrees"][rr, cc]),
                        "true_error_px": _f(None if te is None else float(te)),
                        "true_error_m": _f(None if te is None else float(te) * args.pixel_size),
                        "global_contradicted": g.get("contradicted"),
                        "global_shift_dx": None if g.get("shift_px") is None else g["shift_px"][0],
                        "global_shift_dy": None if g.get("shift_px") is None else g["shift_px"][1],
                        "global_ncc": _f(g.get("ncc")),
                        "method_used": r["declared"]["method"],
                        "fallback_rmse_gt_px": _f(fb.get("rmse_gt_px")),
                        "pair_rmse_gt_px": _f(m.get("rmse_gt_px")),
                        "pair_inlier_ratio": _f(m.get("inlier_ratio")),
                    })
            pair_rows.append((d, meta, r))
            if args.log:
                from core.pipeline import _log_row
                s = rel.get("summary_by_state") or {}
                notes = (f"reliability calibration (M1): verified {rel['counts'][VERIFIED]}/weak "
                         f"{rel['counts'][WEAK]}/no_evidence {rel['counts'][NO_EVIDENCE]} of 64; "
                         + "; ".join(f"{k} n={v['n']}" + (f" median true err {v['median_px']:.3f} px"
                                                          if v.get("n") else "") for k, v in s.items())
                         + f"; area check {g.get('note', '')}; method used {r['declared']['method']}"
                         + "; hillshade convention fixed 3 Sep 2026")
                ok, note = _log_row(meta["pair_id"], "synthetic", method, m,
                                    config=(meta["config"] + f"; sub-pixel NCC refinement "
                                            f"{'ON' if use_subpixel else 'OFF'}; " + rel["config"]),
                                    gsd_mpp=args.pixel_size, notes=notes)
                print(("  " + note) if ok else f"\n{note}\n")

    with open(CELLS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CELL_FIELDS)
        w.writeheader()
        w.writerows(cell_rows)

    # --- the table that decides ------------------------------------------------
    bar = "=" * 72
    print(f"\n{bar}\n  CALIBRATION - true error of cells, by reliability state\n{bar}")
    summary = []
    groups = [("all", cell_rows)] + [(f"d{int(d):03d}", [c for c in cell_rows if c["sun_delta_deg"] == d])
                                     for d in deltas]
    for name, rows in groups:
        print(f"\n  {name}  ({len({c['pair_id'] for c in rows})} pairs)")
        print(f"  {'state':<12}{'n':>5}{'median px':>11}{'p90 px':>9}{'max px':>9}{'<0.5px':>8}{'<1px':>7}{'median m':>10}")
        for st in (VERIFIED, WEAK, NO_EVIDENCE):
            s = _stats([c["true_error_px"] for c in rows if c["state"] == st], args.pixel_size)
            summary.append({"group": name, "state": st, **s})
            if s["n"]:
                print(f"  {st:<12}{s['n']:>5}{s['median_px']:>11.3f}{s['p90_px']:>9.3f}{s['max_px']:>9.3f}"
                      f"{s['frac_under_0p5px']:>8.0%}{s['frac_under_1px']:>7.0%}{s['median_m']:>10.1f}")
            else:
                print(f"  {st:<12}{0:>5}")
        n_contra = sum(1 for c in rows if c["global_contradicted"] and c["cell_row"] == 0 and c["cell_col"] == 0)
        print(f"  pairs where the area check contradicted H: {n_contra}")

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    # The verdict, stated by code so nobody has to squint at a table.
    alls = {s["state"]: s for s in summary if s["group"] == "all"}
    v, wk = alls.get(VERIFIED, {}), alls.get(WEAK, {})
    print(f"\n{bar}")
    if v.get("n") and wk.get("n"):
        better = v["median_px"] < wk["median_px"] and v["p90_px"] < wk["p90_px"]
        print(f"  VERDICT: verified cells median {v['median_px']:.3f} px / p90 {v['p90_px']:.3f} px vs "
              f"weak {wk['median_px']:.3f} / {wk['p90_px']:.3f} px -> "
              f"{'the states are calibrated' if better else 'NOT calibrated - do not claim'}")
    elif v.get("n"):
        print(f"  VERDICT: verified cells median {v['median_px']:.3f} px, p90 {v['p90_px']:.3f} px; "
              f"no weak cells to compare against")
    else:
        print("  VERDICT: no verified cells at all - the thresholds or the check are wrong")
    print(f"  wrote {len(cell_rows)} cell rows to {CELLS_CSV.name} and the summary to {SUMMARY_CSV.name}")
    if args.log:
        ok, note = log_summary_row(args.pixel_size, method)
        print(("  " + note) if ok else f"\n{note}\n")
    print(f"{bar}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
