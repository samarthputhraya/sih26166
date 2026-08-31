"""
The registration pipeline, end to end. This module IS Gate 1.

    python -m core.pipeline data/pairs/pair_01

Gate 1 (Day 5, 00_CANONICAL_FACTS.md Sec.11), verbatim: *"runs end to end on a
real lunar pair, no manual steps, prints all five metrics"*.

    load -> to_common_gsd -> illumination -> match -> RANSAC -> warp -> metrics

Four design decisions worth defending.

1. THE FIVE METRICS ARE NOT COMPUTED HERE. They come from
   `evaluation/metrics.py :: evaluate()`, which is SAMRUDH'S module (his Day 3).
   A second implementation living in `core/` would give this project two sources
   of truth for its headline accuracy number, and Invariant 1 exists because we
   already shipped an invented figure through four documents. So: we import his
   `evaluate()` if it exists, and if it does not we print the geometry we do have
   and say plainly that the metrics are unavailable. We never substitute our own.

2. `residual_px` AND `rmse_gt_px` ARE NOT INTERCHANGEABLE, and printing the wrong
   one is a fabrication rather than a bug. `rmse_gt_px` is accuracy against a
   KNOWN transform and exists only for synthetic and Tier D pairs. `residual_px`
   is a held-out fit residual and is what a real pair can honestly report. On a
   real lunar pair we have no ground truth, so `rmse_gt_px` is printed as `n/a`,
   never as a number.

3. THE HELD-OUT SPLIT BELONGS TO `evaluate()`, NOT TO US. Samrudh withholds 20%
   and fits on the remainder. Our `filter_matches` fits on everything because its
   output is the operational transform used to warp the image. Fitting a
   transform from the matches and then measuring error on those same matches is
   circular - that exact bug is recorded in Canonical Facts Sec.7.

4. `illumination.py` DOES NOT EXIST YET (Day 5-6) and the chain must run without
   it, so the hook is a no-op that reports itself as absent. Same for a missing
   `evaluate()`. Gate 1 must not depend on work that is not due until after it.

The CLI argument is a DIRECTORY or a prefix, not two files, because that is what
Gate 1 specifies and what Rohan's naming produces (Sec.14):
`pair_01_source.tif` / `pair_01_ref.tif`.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

from core.io_loader import load
from core.matcher import match
from core.ransac import filter_matches, warp
from core.scale import to_common_gsd, to_original

SOURCE_HINTS = ("_source", "_src", "_a")
REF_HINTS = ("_ref", "_reference", "_b")
EXTENSIONS = (".tif", ".tiff", ".IMG", ".img", ".xml", ".lbl")


def resolve_pair(target: str | pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """Turn `data/pairs/pair_01` into the two files it names.

    Accepts a directory containing exactly one source/reference pair, or a
    prefix such as `data/pairs/pair_01` matching `pair_01_source.tif` and
    `pair_01_ref.tif`. Tolerant of extension, because Rohan may deliver .tif,
    .IMG or PDS4 .xml depending on tier.
    """
    p = pathlib.Path(target)
    candidates = sorted(p.iterdir()) if p.is_dir() else sorted(
        p.parent.glob(p.name + "*"))
    files = [f for f in candidates if f.suffix in EXTENSIONS and f.is_file()]
    if not files:
        raise SystemExit(
            f"no image files found for {target!r}\n"
            f"  looked for {EXTENSIONS} in "
            f"{p if p.is_dir() else p.parent} matching {p.name!r}*"
        )

    def pick(hints):
        for f in files:
            if any(h in f.stem.lower() for h in hints):
                return f
        return None

    src, ref = pick(SOURCE_HINTS), pick(REF_HINTS)
    if src and ref:
        return src, ref
    if len(files) == 2:
        return files[0], files[1]
    raise SystemExit(
        f"could not identify a source/reference pair in {target!r}.\n"
        f"  found: {[f.name for f in files]}\n"
        f"  expected names containing {SOURCE_HINTS} and {REF_HINTS}, "
        "e.g. pair_01_source.tif / pair_01_ref.tif"
    )


def _normalise_illumination(img, meta):
    """Hook for core/illumination.py, which is Day 5-6 work.

    Returns (image, description). Absent is a legitimate state, not an error -
    but it must be VISIBLE, because 'we normalise illumination' is a claim we
    intend to make to a judge and it must not be made before it is true.
    """
    try:
        from core.illumination import normalize
    except ImportError:
        return img, "none (core/illumination.py not written yet)"
    return normalize(img), "applied"


def _evaluate(ref_shape, src_pts, ref_pts, H_true=None):
    """Call Samrudh's evaluate(), or report honestly that it is unavailable."""
    try:
        from evaluation.metrics import evaluate
    except ImportError:
        return None, ("evaluation/metrics.py does not exist yet (Samrudh, Day 3) "
                      "- the five metrics cannot be reported")
    return evaluate(ref_shape, src_pts, ref_pts, H_true=H_true), "ok"


def run_all(src_path, ref_path, H_true=None, progress=None) -> dict:
    """Register one pair. Returns a result dict; never raises on a bad pair."""
    t0 = time.perf_counter()
    a, meta_a = load(src_path)
    b, meta_b = load(ref_path)

    a_s, b_s, gsd, factors = to_common_gsd(a, meta_a, b, meta_b)
    a_n, illum = _normalise_illumination(a_s, meta_a)
    b_n, _ = _normalise_illumination(b_s, meta_b)

    src_pts, ref_pts, scores = match(a_n, b_n, progress=progress)

    # Back to ORIGINAL pixel coordinates before anything is measured or reported.
    # Metrics are defined in reference-image pixels (Sec.7); reporting them in
    # resampled pixels would silently change what the number means.
    src_full = to_original(src_pts, factors["a"]) if len(src_pts) else src_pts
    ref_full = to_original(ref_pts, factors["b"]) if len(ref_pts) else ref_pts

    src_in, ref_in, H, info = filter_matches(src_full, ref_full)
    warped = warp(a, H, b.shape[:2]) if H is not None else None
    metrics, metrics_note = _evaluate(b.shape[:2], src_in, ref_in, H_true)

    return {
        "source": str(src_path), "reference": str(ref_path),
        "shape_source": a.shape, "shape_reference": b.shape,
        "gsd_mpp": gsd, "scale_note": factors["note"], "scale_factors": factors,
        "illumination": illum,
        "n_matches": int(len(src_pts)), "ransac": info,
        "H": H, "warped": warped,
        "src_inliers": src_in, "ref_inliers": ref_in,
        "metrics": metrics, "metrics_note": metrics_note,
        "seconds": time.perf_counter() - t0,
        "meta_source": meta_a, "meta_reference": meta_b,
    }


def _print_report(r: dict) -> None:
    print(f"\n{'='*64}\n  REGISTRATION - SIH26166\n{'='*64}")
    print(f"  source     {pathlib.Path(r['source']).name}  {r['shape_source']}"
          f"  [{r['meta_source'].get('instrument') or 'instrument not in label'}]")
    print(f"  reference  {pathlib.Path(r['reference']).name}  {r['shape_reference']}"
          f"  [{r['meta_reference'].get('instrument') or 'instrument not in label'}]")
    print(f"\n  scale         {r['scale_note']}")
    print(f"  illumination  {r['illumination']}")
    print(f"  matches       {r['n_matches']}")
    print(f"  ransac        {r['ransac']['note']}")
    print(f"  inliers       {r['ransac']['inlier_count']} "
          f"({r['ransac']['inlier_ratio']:.1%})")
    print(f"  elapsed       {r['seconds']:.1f} s")

    print(f"\n  {'-'*60}\n  THE FIVE METRICS\n  {'-'*60}")
    m = r["metrics"]
    if m is None:
        print(f"  UNAVAILABLE - {r['metrics_note']}")
        print("  No substitute is computed here on purpose: evaluation/metrics.py")
        print("  is the single source of numbers for this project.")
    else:
        gt = m.get("rmse_gt_px")
        print(f"  rmse_gt_px              {gt if gt is not None else 'n/a (no ground truth on a real pair)'}")
        for k in ("residual_px", "inlier_count", "inlier_ratio",
                  "grid_coverage_fraction", "distribution_cv"):
            v = m.get(k)
            print(f"  {k:<24}{v if v is not None else 'n/a'}")
        if r["gsd_mpp"] and m.get("residual_px") is not None:
            print(f"\n  residual_px is in REFERENCE-image pixels; at "
                  f"{r['gsd_mpp']:.4g} m/px that is "
                  f"{m['residual_px'] * r['gsd_mpp']:.3f} m on the ground.")
    print(f"{'='*64}\n")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        print("usage: python -m core.pipeline <pair directory or prefix>")
        return 2
    src, ref = resolve_pair(argv[1])
    r = run_all(src, ref, progress=lambda d, t: print(f"    matching tile {d}/{t}",
                                                      flush=True))
    _print_report(r)
    # Exit non-zero when there is no usable registration, so an unattended run
    # (Gate 1, Rohan's catalogue loop) can tell success from a printed apology.
    return 0 if r["H"] is not None else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
