"""
Measure sub-pixel refinement on REAL lunar texture, against a known answer.

    python core/bench_subpixel.py

Writes `core/bench_subpixel_results.csv`. Same shape as `bench_illumination.py`:
a known truth, a number measured against it, and a CSV nobody has to take on
trust.

WHY A SYNTHETIC SHIFT ON REAL PIXELS
------------------------------------
Sec.7 requires a sub-pixel claim to be measured against a KNOWN transform. No
real lunar pair has one - that is the whole reason `rmse_gt_px` is `n/a` on real
pairs. So we take a real Chandrayaan-2 OHRC crop and shift it by an offset WE
chose, with cubic interpolation. The texture, noise and contrast are real lunar
data; only the displacement is manufactured, and it is manufactured precisely so
there is something to be right or wrong about.

*** WHAT THIS DOES AND DOES NOT SUPPORT ***

It supports: "our refinement recovers a known sub-pixel displacement on real
lunar texture to within X px on the CH-2 OHRC grid, which is Y cm."

It does NOT support any claim about cross-illumination, cross-sensor or
multi-modal performance. Both images here come from ONE frame with ONE sun
angle. Interpolating a crop does not change where a shadow falls. Log it as
`same-frame fractional shift`, exactly as `pair_01` is logged as `same-frame
offset crop`.

The number belongs in `evaluation/results_log.csv` (Samrudh's file, his schema).
It is written here to `core/` for the same reason the illumination A/B was:
this is a development measurement of a `core/` module, not an evaluation run,
and Invariant 4 gives that file one owner.
"""
from __future__ import annotations

import csv
import pathlib
import sys
import time

import numpy as np
import cv2

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from core.io_loader import load                       # noqa: E402
from core.illumination import normalize               # noqa: E402
from core.matcher import match                        # noqa: E402
from core.subpixel import refine, describe, metres    # noqa: E402

# CH-2 OHRC, from the instrument's own PDS4 label (<isda:pixel_resolution>),
# not from any document. See data/DATASET_CARD.md.
CH2_OHRC_MPP = 0.22977000623605362
GRID_NAME = "CH-2 OHRC"

PAIR = pathlib.Path("data/pairs/pair_01/pair_01_source.tif")
OUT = pathlib.Path(__file__).resolve().parent / "bench_subpixel_results.csv"

# Chosen to sample the range including the half-pixel worst case.
SHIFTS = [(0.10, 0.10), (0.25, 0.00), (0.37, -0.62), (-0.25, 0.44), (0.50, 0.50)]


def _shift(img: np.ndarray, tx: float, ty: float) -> np.ndarray:
    """Translate by (tx, ty). A feature at (x, y) moves to (x + tx, y + ty)."""
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]),
                          flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def _endpoint_error(src, ref, tx, ty):
    """Distance from each match to where the known shift says it should be."""
    return np.linalg.norm(ref - (src + np.array([tx, ty])), axis=1)


def _matchers():
    """LoFTR is what we ship; the classical three are Gate 1's fallback path (Sec.11)."""
    from baselines.sift_baseline import run_sift
    from baselines.orb_baseline import run_orb
    from baselines.akaze_baseline import run_akaze

    def loftr(a, b):
        src, ref, _ = match(a, b)
        return src, ref

    def _u8(fn):
        def go(a, b):
            return fn(np.clip(a, 0, 255).astype(np.uint8), np.clip(b, 0, 255).astype(np.uint8))
        return go

    return {"LoFTR": loftr, "SIFT": _u8(run_sift), "ORB": _u8(run_orb), "AKAZE": _u8(run_akaze)}


def _one(name, tx, ty, src_pts, ref_pts, a_n, b_n, t_match):
    """One (matcher, shift) measurement."""
    t0 = time.perf_counter()
    src_out, ref_out, info = refine(src_pts, ref_pts, a_n, b_n)
    t_refine = time.perf_counter() - t0

    m = info["refined"]
    if m.sum() < 10:
        print(f"  ({tx:+.2f},{ty:+.2f}) only {int(m.sum())} refined - skipped")
        return None

    # THREE baselines, because two of them can mislead.
    #
    #  raw          the matcher's own output, untouched. The only honest thing to beat.
    #  rounded_src  the same reference points paired with the ROUNDED source the refiner
    #               used. Rounding injects error the matcher is not responsible for, so
    #               this looks worse than raw - it is here only so `refined` is compared
    #               against a like-for-like origin.
    #  refined      the refined reference, from the rounded source.
    #
    # Quoting `rounded_src -> refined` alone would flatter the refinement by crediting it
    # with undoing damage this benchmark itself caused.
    raw = _endpoint_error(src_pts[m], ref_pts[m], tx, ty)
    rounded = _endpoint_error(src_out[m], ref_pts[m], tx, ty)
    after = _endpoint_error(src_out[m], ref_out[m], tx, ty)

    med_raw, med_rounded, med_after = (float(np.median(raw)), float(np.median(rounded)),
                                       float(np.median(after)))
    verdict = "helps" if med_after < med_raw else "HURTS"
    print(f"  ({tx:+.2f},{ty:+.2f})  {len(src_pts):5d} matched, {info['n_refined']:5d} refined"
          f"   raw {med_raw:.3f}  ->  refined {med_after:.3f} px   {verdict}")
    return {
        "matcher": name, "true_dx": tx, "true_dy": ty,
        "n_matches": len(src_pts), "n_refined": info["n_refined"],
        "median_err_raw_px": round(med_raw, 4),
        "median_err_rounded_src_px": round(med_rounded, 4),
        "median_err_refined_px": round(med_after, 4),
        "p90_err_refined_px": round(float(np.percentile(after, 90)), 4),
        "median_err_refined_m": round(metres(med_after, CH2_OHRC_MPP), 5),
        "refined_vs_raw_x": round(med_raw / med_after, 2) if med_after > 0 else None,
        "verdict": verdict,
        "match_s": round(t_match, 1), "refine_s": round(t_refine, 2),
    }


def main() -> int:
    if not PAIR.exists():
        print(f"missing {PAIR}", file=sys.stderr)
        print("data/pairs/ is gitignored - rebuild with core/make_demo_pair.py, or copy "
              "pairs/pair_01/ from the SIH26166_DATA Drive folder.", file=sys.stderr)
        return 1

    img, meta = load(str(PAIR))
    base = np.clip(np.asarray(img, np.float32), 0, 255).astype(np.uint8)
    print(f"source {PAIR.name}  {base.shape}  DN {base.min()}..{base.max()}  std {base.std():.1f}")
    if base.std() < 10:
        print("REFUSING: std < 10, this crop has no texture (Known issue #6)", file=sys.stderr)
        return 1

    matchers = _matchers()
    rows = []
    for name, run in matchers.items():
        print(f"\n{name}")
        for tx, ty in SHIFTS:
            shifted = _shift(base, tx, ty)

            # The matcher sees illumination-normalised images, and so must the refiner -
            # see note 3 in subpixel.py. Passing raw DN here would be measuring a
            # different pipeline than the one we ship.
            a_n, b_n = normalize(base), normalize(shifted)

            t0 = time.perf_counter()
            src_pts, ref_pts = run(a_n, b_n)
            t_match = time.perf_counter() - t0

            if len(src_pts) < 10:
                print(f"  ({tx:+.2f},{ty:+.2f}) only {len(src_pts)} matches - skipped")
                continue
            row = _one(name, tx, ty, src_pts, ref_pts, a_n, b_n, t_match)
            if row is not None:
                rows.append(row)

    if not rows:
        print("no rows produced", file=sys.stderr)
        return 1

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"\nwrote {OUT} ({len(rows)} rows)\n")
    print(f"  {'matcher':8}{'worst raw':>11}{'worst refined':>15}   refinement")
    for name in dict.fromkeys(r["matcher"] for r in rows):
        sub = [r for r in rows if r["matcher"] == name]
        w_raw = max(r["median_err_raw_px"] for r in sub)
        w_ref = max(r["median_err_refined_px"] for r in sub)
        helped = sum(1 for r in sub if r["verdict"] == "helps")
        print(f"  {name:8}{w_raw:10.3f}px{w_ref:14.3f}px   helps {helped}/{len(sub)}")

    best = min(rows, key=lambda r: r["median_err_raw_px"])
    print()
    print("THE RULE THIS MEASURES: NCC refinement converges on a floor of roughly")
    print("0.16-0.43 px whatever it is given. It helps a matcher that is WORSE than")
    print("that floor and hurts one that is already BETTER. Check before enabling it.")
    print()
    print(f"Best raw localisation here: {best['matcher']} at "
          f"{describe(best['median_err_raw_px'], CH2_OHRC_MPP, GRID_NAME)}")
    print("Quote the worst case, and quote whichever pipeline you actually ship.")
    print("Tier: same-frame fractional shift - NOT cross-illumination, NOT cross-sensor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
