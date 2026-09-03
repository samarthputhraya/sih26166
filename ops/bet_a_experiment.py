"""Bet A, measured honestly: does matching on the sensor's grid help Tier D?

THE CONFOUND THIS SCRIPT EXISTS TO REMOVE
-----------------------------------------
Running `pair_03_tierD` (reference at 60 m/px) against `pair_04_tierD_native`
(reference at 9.37 m/px) and comparing `residual_px` is meaningless, and comparing
their inlier ratios is worse than meaningless - it is misleading in our favour or
against us depending on which way we squint.

Both RANSAC gates are expressed in PIXELS and both default to 3.0:

    core/ransac.py:52        DEFAULT_THRESHOLD_PX = 3.0
    evaluation/metrics.py:5  INLIER_THRESH_PX     = 3.0

On the 60 m/px grid, 3 px is a 180 m ground tolerance.
On the 9.37 m/px grid, 3 px is a 28 m ground tolerance.

So the "native grid" arm was silently judged against a bar 6.4x stricter. Any
collapse in `inlier_ratio` between the two arms is partly - possibly entirely -
that constant, not the matcher and not the modality.

This script fixes the tolerance in METRES and converts to each grid's pixels, so
the two arms are asked the same question. It also reports every residual in
metres, because `residual_px` on two grids 6.4x apart cannot be compared and
Invariant 2 requires the pixel grid to be named anyway.

WHAT IT DOES NOT TOUCH
----------------------
`evaluation/metrics.py` is Samrudh's file and `INLIER_THRESH_PX` is a module
constant with no parameter. This script rebinds it per-measurement in memory,
inside a try/finally, and restores it. That is a measurement harness reading his
function at several operating points - not an edit to his module, and not a
change to its default.

`core.pipeline.run_all`'s signature is pinned by list equality at
`core/test_interfaces.py:59`, so the pipeline steps are re-walked here rather
than parameterised there.

    python -m ops.bet_a_experiment
"""
from __future__ import annotations

import pathlib
import time

import numpy as np

import evaluation.metrics as metrics_mod
from core.illumination import __name__ as _illum_check  # noqa: F401  (import guard)
from core.io_loader import load
from core.pipeline import _normalise_illumination
from core.matcher import match
from core.ransac import filter_matches
from core.scale import to_common_gsd, to_original

# Ground tolerances to ask both arms about. 180 m is what the ORIGINAL Tier D run
# was actually granted (3 px x 60 m/px) - it is included so the historical 37.81 px
# number is reproduced exactly rather than quietly re-based.
GROUND_TOLERANCES_M = [28.1, 60.0, 100.0, 180.0, 300.0]

ARMS = [
    ("pair_03_tierD", "data/pairs/pair_03_tierD/tier_d_01",
     "reference at LOLA native 60 m/px; optical downsampled 640->99"),
    ("pair_04_tierD_native", "data/pairs/pair_04_tierD_native/tier_d_native",
     "reference rendered onto the Kaguya grid at 9.37 m/px; no downsampling"),
]


def _pair_paths(prefix: str) -> tuple[pathlib.Path, pathlib.Path]:
    p = pathlib.Path(prefix)
    return (p.parent / f"{p.name}_source.tif", p.parent / f"{p.name}_ref.tif")


def match_once(src_path, ref_path):
    """Everything up to and including matching. Expensive; run one time per arm."""
    a, meta_a = load(src_path)
    b, meta_b = load(ref_path)
    a_s, b_s, gsd, factors = to_common_gsd(a, meta_a, b, meta_b)
    a_n, _ = _normalise_illumination(a_s, meta_a)
    b_n, _ = _normalise_illumination(b_s, meta_b)

    t0 = time.perf_counter()
    src_pts, ref_pts, _scores = match(a_n, b_n)
    elapsed = time.perf_counter() - t0

    src_full = to_original(src_pts, factors["a"]) if len(src_pts) else src_pts
    ref_full = to_original(ref_pts, factors["b"]) if len(ref_pts) else ref_pts
    return {
        "src": src_full, "ref": ref_full, "ref_shape": b.shape[:2],
        "gsd": gsd, "match_shape": a_n.shape, "n_matches": len(src_full),
        "elapsed_s": elapsed,
    }


def score_at(m, tol_m: float) -> dict:
    """Score one arm's matches at a tolerance expressed in ground metres."""
    tol_px = tol_m / m["gsd"]
    original = metrics_mod.INLIER_THRESH_PX
    try:
        metrics_mod.INLIER_THRESH_PX = tol_px
        _si, _ri, H, info = filter_matches(m["src"], m["ref"], threshold_px=tol_px)
        met = metrics_mod.evaluate(m["ref_shape"], m["src"], m["ref"], H_true=None)
    finally:
        metrics_mod.INLIER_THRESH_PX = original

    res_px = met.get("residual_px")
    return {
        "tol_m": tol_m, "tol_px": tol_px,
        "ransac_inliers": info.get("inliers") if isinstance(info, dict) else None,
        "residual_px": res_px,
        "residual_m": None if res_px is None else res_px * m["gsd"],
        "inlier_count": met.get("inlier_count"),
        "inlier_ratio": met.get("inlier_ratio"),
        "grid_coverage_fraction": met.get("grid_coverage_fraction"),
        "status": met.get("status"),
    }


def main() -> int:
    results = {}
    for name, prefix, note in ARMS:
        src, ref = _pair_paths(prefix)
        if not src.exists() or not ref.exists():
            print(f"  SKIP {name}: {src.name} / {ref.name} not on disk")
            continue
        m = match_once(src, ref)
        results[name] = (m, note)
        print(f"\n=== {name} ===")
        print(f"  {note}")
        print(f"  matched at {m['match_shape']}  gsd {m['gsd']:.4g} m/px  "
              f"{m['n_matches']} raw matches  ({m['elapsed_s']:.1f} s)")

    print("\n" + "=" * 92)
    print("  EQUAL GROUND TOLERANCE - the same question asked of both arms")
    print("=" * 92)
    header = (f"{'arm':<22}{'tol_m':>8}{'tol_px':>9}{'matches':>9}"
              f"{'inliers':>9}{'ratio':>8}{'residual_m':>13}{'coverage':>10}")
    print(header)
    print("-" * 92)
    for name, (m, _note) in results.items():
        for tol in GROUND_TOLERANCES_M:
            s = score_at(m, tol)
            res = "n/a" if s["residual_m"] is None else f"{s['residual_m']:.1f}"
            ratio = "n/a" if s["inlier_ratio"] is None else f"{s['inlier_ratio']:.3f}"
            cov = ("n/a" if s["grid_coverage_fraction"] is None
                   else f"{s['grid_coverage_fraction']:.3f}")
            print(f"{name:<22}{tol:>8.1f}{s['tol_px']:>9.2f}{m['n_matches']:>9}"
                  f"{str(s['inlier_count']):>9}{ratio:>8}{res:>13}{cov:>10}")
        print("-" * 92)

    print("\n  residual_m = residual_px * gsd_mpp. The two arms' pixel grids differ by 6.4x,")
    print("  so ONLY the metres column is comparable between them.")
    print("  Scene width is 5997 m; a residual of that order means no usable registration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
