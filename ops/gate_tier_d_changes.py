"""M3 - run change detection on the aligned Tier D pair, then gate it by reliability.

    python -m ops.gate_tier_d_changes [pair_dir] [--log]

On Day 6 the change detector produced 35 candidates on the optical <-> elevation
pair and manual inspection found 0 real changes, 31 shadow/illumination effects and
4 registration artefacts (`app/notes_day6_tierd.md`) - a 100% false-positive rate,
demonstrated live. This script re-runs the detector on the aligned pair the
pipeline now produces (the fallback translation, since the matcher's homography is
contradicted) and asks the reliability map which candidates it can vouch for.

Expected on Tier D: the whole frame is contradicted and no cell is verified, so
NOTHING is kept - every candidate is either "rejected (weak)" or "unassessable (no
evidence)". That is the right answer: a registration whose alignment cannot be
verified anywhere has no business reporting surface changes. The numbers go to
`evaluation/results_log.csv` under `change_detection_absdiff+reliability_gate`.
"""
from __future__ import annotations

import argparse
import pathlib

import numpy as np

from app.change_detection import detect_changes
from core.pipeline import _log_row, resolve_pair, run_all
from core.reliability import ascii_map, describe, gate


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pair", nargs="?", default="data/pairs/pair_04_tierD_native")
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--thresh", type=int, default=30)
    ap.add_argument("--min-area-px", type=int, default=50)
    ap.add_argument("--alignment", choices=("declared", "matcher"), default="declared",
                    help="detect on the alignment the system declared (default), or on the "
                         "matcher's own homography even where the pixels contradict it - the "
                         "'before' picture")
    args = ap.parse_args()

    src, ref = resolve_pair(args.pair)
    r = run_all(src, ref)
    rel = r["reliability"]
    from core.io_loader import load
    b, _ = load(ref)
    aligned = r["warped_final"] if args.alignment == "declared" else r["warped"]
    align_name = (r["declared"]["method"] if args.alignment == "declared"
                  else "loftr+magsac++ (matcher's homography, contradicted by the pixels)")
    if aligned is None:
        print("no alignment at all; nothing to detect on")
        return 1
    gsd = r["gsd_mpp"]
    overlay, changes = detect_changes(aligned.astype(np.float32), b.astype(np.float32), gsd,
                                      thresh=args.thresh, min_area_px=args.min_area_px)
    g = gate(changes, rel, b.shape[:2])

    print(f"\n  pair            {pathlib.Path(args.pair).name}")
    print(f"  detected on     {align_name}")
    print(f"  method used     {r['declared']['method']}  ({r['declared']['why']})")
    for line in describe(rel):
        print(f"  {line}")
    print("  " + ascii_map(rel).replace("\n", "\n  "))
    c = g["counts"]
    print(f"\n  change candidates (absdiff, thresh {args.thresh}, min area {args.min_area_px} px): {c['input']}")
    print(f"    kept (in verified cells)        {c['kept']}")
    print(f"    rejected (in weak cells)        {c['rejected_weak']}")
    print(f"    unassessable (no-evidence cells){c['unassessable']:>3}")
    by_label = {}
    for ch in changes:
        by_label[ch.get("classification", "?")] = by_label.get(ch.get("classification", "?"), 0) + 1
    print(f"    detector's own labels: {by_label}")

    if args.log:
        notes = (f"{c['input']} candidates on the pair aligned by {align_name}: "
                 f"kept {c['kept']} (verified cells), rejected {c['rejected_weak']} (weak cells), "
                 f"unassessable {c['unassessable']} (no-evidence cells); detector labels {by_label}; "
                 f"reliability: verified {rel['counts']['verified']}/weak {rel['counts']['weak']}/"
                 f"no_evidence {rel['counts']['no_evidence']} of 64, frame "
                 f"{'CONTRADICTED' if rel['global'].get('contradicted') else 'consistent'}. "
                 f"Day-6 manual truth on this pair: 0 real changes of 35.")
        ok, note = _log_row(pathlib.Path(args.pair).name, "D",
                            "change_detection_absdiff+reliability_gate",
                            {"rmse_gt_px": None, "residual_px": None, "inlier_count": None,
                             "inlier_ratio": None, "grid_coverage_fraction": None,
                             "distribution_cv": None, "n_matches": c["input"], "status": "ok"},
                            config=(f"thresh={args.thresh}, min_area_px={args.min_area_px}, "
                                    f"edge_margin_frac=0.05; gate keeps only candidates whose "
                                    f"centroid lies in a verified cell; {rel['config']}"),
                            gsd_mpp=gsd, notes=notes)
        print(("  " + note) if ok else f"\n{note}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
