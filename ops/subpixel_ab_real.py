"""M4 - the sub-pixel refiner, on and off, on REAL lunar texture with a known answer.

    python -m ops.subpixel_ab_real [--log] [--shift 0.5,0.5]

`core/bench_subpixel.py` measured on Day 3 that NCC refinement makes LoFTR's
matches agree with each other better (residual_px falls) while making them LESS
accurate against a known displacement on real OHRC texture (0.336 -> 0.431 px at
a half-pixel shift). That number lives in a development CSV. Invariant 1 says a
number reaches a slide only from evaluation/results_log.csv, through the same
pipeline that produces every other number - so this script rebuilds the same
experiment as a pair on disk and runs `core.pipeline.run_all` on it twice, with
refinement off and on, logging both.

The pair: a real Chandrayaan-2 OHRC crop (pair_01's source) and the same crop
translated by a chosen sub-pixel amount with cubic interpolation. Texture, noise
and contrast are real; only the displacement is manufactured, precisely so there
is a right answer. Tier: `same-frame fractional shift`. It says NOTHING about
cross-illumination, cross-sensor or multi-modal behaviour - both images are one
frame under one sun.

The synthetic-render A/B (`core.pipeline --synthetic --subpixel`) gives the
OPPOSITE sign of effect on a hillshade (refinement helps there). Both are logged;
the honest sentence is "it helped on renders and hurt on real texture, so the
default is off and both numbers are published".
"""
from __future__ import annotations

import argparse
import pathlib

import cv2
import numpy as np
import tifffile

from core.io_loader import load
from core.pipeline import _log_row, _print_report, run_all

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "pairs" / "pair_01" / "pair_01_source.tif"
OUT = ROOT / "demo_cache" / "synthetic"
CH2_OHRC_MPP = 0.22977000623605362   # from the OHRC PDS4 label, see data/DATASET_CARD.md


def build(shift):
    img, _meta = load(str(SRC))
    base = np.asarray(img, dtype=np.float32)
    tx, ty = shift
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    shifted = cv2.warpAffine(base, M, (base.shape[1], base.shape[0]),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    # source = base, reference = base moved by (tx, ty): H_true maps source -> reference
    H_true = np.array([[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]])
    OUT.mkdir(parents=True, exist_ok=True)
    stem = f"ohrc_fracshift_x{tx:+.2f}_y{ty:+.2f}"
    sp, rp = OUT / f"{stem}_source.tif", OUT / f"{stem}_ref.tif"
    tifffile.imwrite(str(sp), base)
    tifffile.imwrite(str(rp), shifted.astype(np.float32))
    return sp, rp, H_true, stem


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shift", default="0.5,0.5")
    ap.add_argument("--log", action="store_true")
    args = ap.parse_args()
    if not SRC.is_file():
        print(f"missing {SRC} - sync data/pairs/pair_01 from the Drive folder")
        return 1
    shift = tuple(float(v) for v in args.shift.split(","))
    sp, rp, H_true, stem = build(shift)
    results = {}
    for name, sub in (("ours_loftr", False), ("ours_loftr+subpixel", True)):
        r = run_all(sp, rp, H_true=H_true, subpixel=sub)
        _print_report(r)
        results[name] = r
        m = r["metrics"] or {}
        print(f"  {name:<22} rmse_gt_px {m.get('rmse_gt_px')}   residual_px {m.get('residual_px')}")
        if args.log and m.get("status") == "ok":
            config = (f"real CH-2 OHRC crop (pair_01 source, 640x640 at {CH2_OHRC_MPP} m/px) vs the "
                      f"same crop translated by ({shift[0]:+.2f},{shift[1]:+.2f}) px with cubic "
                      f"interpolation; sun difference 0; NCC sub-pixel refinement "
                      f"{'ON' if sub else 'OFF'}")
            ok, note = _log_row(stem, "same-frame fractional shift", name, m, config=config,
                                gsd_mpp=CH2_OHRC_MPP,
                                notes=("M4 sub-pixel A/B on real texture. Compare rmse_gt_px "
                                       "(truth) with residual_px (self-consistency) between the "
                                       "OFF and ON rows. NOT cross-illumination, NOT cross-sensor."))
            print(("  " + note) if ok else f"\n{note}\n")
    off, on = results["ours_loftr"]["metrics"], results["ours_loftr+subpixel"]["metrics"]
    if off and on:
        print(f"\n  refinement OFF: rmse_gt {off['rmse_gt_px']:.3f} px  residual {off['residual_px']:.3f} px")
        print(f"  refinement ON : rmse_gt {on['rmse_gt_px']:.3f} px  residual {on['residual_px']:.3f} px")
        print(f"  on the CH-2 OHRC grid, {off['rmse_gt_px'] * CH2_OHRC_MPP * 100:.1f} cm -> "
              f"{on['rmse_gt_px'] * CH2_OHRC_MPP * 100:.1f} cm true error")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
