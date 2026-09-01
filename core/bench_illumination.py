"""
A/B the two illumination methods through the real matcher.

    python -m core.bench_illumination data/pairs/pair_01

Canonical Facts Sec.6.4 says *"phase congruency OR sign-invariant gradient
orientation - A/B test both."* This is that test. It reports match count, inlier
ratio and - where the pair has a known transform - accuracy, for the same pair
with normalisation off, then each method on.

WHAT THIS MEASURES, AND WHAT IT DOES NOT
----------------------------------------
Two cases run, and they answer different questions.

  IDENTICAL       The pair exactly as delivered. Both images are lit the same,
                  so there is nothing for illumination normalisation to fix.
                  The question here is only "what does turning it on COST?" -
                  because a preprocessing step that helps on hard pairs and
                  wrecks easy ones is not a step we can leave switched on.

  INTENSITY XFORM The reference is contrast-inverted, gamma-shifted and given a
                  brightness ramp. This is an INTENSITY transform, NOT a sun
                  angle change. It flips which side of a rim is bright, so it
                  breaks any intensity-keyed matcher - but the shadows do not
                  MOVE, and under a real sun-angle change they move. So a good
                  result here is necessary and not sufficient.

The honest sun-angle number needs a real Tier A pair (Rohan) or Samrudh's shaded
relief at two azimuths, and neither exists yet. Until one does, nothing from
this script describes cross-illumination performance, and it must not be
described that way in a slide. It goes in results_log.csv labelled for what it
is.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

from core.illumination import METHODS, normalize
from core.io_loader import load
from core.matcher import match
from core.pipeline import resolve_pair
from core.ransac import filter_matches


def _intensity_transform(img: np.ndarray) -> np.ndarray:
    """Contrast inversion + gamma + a brightness ramp, in raw DN.

    Deliberately nastier than a real illumination change in intensity terms and
    deliberately silent about geometry - see the module docstring.
    """
    a = np.asarray(img, dtype=np.float32)
    lo, hi = float(a.min()), float(a.max())
    span = max(hi - lo, 1e-6)
    u = (a - lo) / span                     # to [0, 1]
    u = 1.0 - u                             # contrast inversion: shadows flip
    u = np.power(u, 1.6)                    # gamma: non-linear response
    h, w = a.shape
    ramp = np.linspace(-0.15, 0.15, w, dtype=np.float32)[None, :]
    u = np.clip(u + ramp, 0.0, 1.0)         # uneven illumination across frame
    return (u * span + lo).astype(np.float32)


def _translation_from(H) -> tuple[float, float] | None:
    """Recover (dx, dy) if H is close to a pure translation, else None."""
    if H is None:
        return None
    lin = H[:2, :2] / (H[2, 2] if H[2, 2] else 1.0)
    if np.abs(lin - np.eye(2)).max() > 1e-2:
        return None
    return float(H[0, 2] / H[2, 2]), float(H[1, 2] / H[2, 2])


def _run(a: np.ndarray, b: np.ndarray, method: str | None) -> dict:
    t0 = time.perf_counter()
    if method is None:
        a_n, b_n = a, b
    else:
        a_n, b_n = normalize(a, method), normalize(b, method)
    t_norm = time.perf_counter() - t0

    src, ref, _ = match(a_n, b_n)
    if len(src) < 4:
        return {"method": method or "off", "n": len(src), "inliers": 0,
                "ratio": 0.0, "shift": None, "t_norm": t_norm,
                "t_total": time.perf_counter() - t0}

    _, _, H, info = filter_matches(src, ref)
    return {"method": method or "off",
            "n": info["n_input"], "inliers": info["inlier_count"],
            "ratio": info["inlier_ratio"], "shift": _translation_from(H),
            "t_norm": t_norm, "t_total": time.perf_counter() - t0}


def _table(title: str, rows: list[dict], note: str = "") -> None:
    print(f"\n  {title}")
    if note:
        print(f"  {note}")
    print(f"  {'-' * 74}")
    print(f"  {'method':<22}{'matches':>9}{'inliers':>9}{'ratio':>8}"
          f"{'recovered shift':>22}{'s':>7}")
    print(f"  {'-' * 74}")
    for r in rows:
        shift = ("--" if r["shift"] is None
                 else f"({r['shift'][0]:+.2f}, {r['shift'][1]:+.2f})")
        print(f"  {r['method']:<22}{r['n']:>9}{r['inliers']:>9}"
              f"{r['ratio']:>8.3f}{shift:>22}{r['t_total']:>7.1f}")


RESULTS_CSV = pathlib.Path(__file__).with_name("bench_illumination_results.csv")


def _write_csv(pair: str, cases: list[tuple[str, list[dict]]]) -> None:
    """Write our own results file, next to the bench, as bench_loftr_cpu does.

    Deliberately NOT `evaluation/results_log.csv`: Samrudh owns that file and
    its schema (day_3.md sequencing decision 1). Two writers on one CSV is how
    a results file becomes untrustworthy. If these numbers are ever wanted in
    the project log, he ingests them on his schema, not ours on his.
    """
    with RESULTS_CSV.open("w", encoding="utf-8", newline="") as fh:
        fh.write("pair,case,method,matches,inliers,inlier_ratio,"
                 "recovered_dx,recovered_dy,seconds\n")
        for case, rows in cases:
            for r in rows:
                dx, dy = ("", "") if r["shift"] is None else r["shift"]
                dx = f"{dx:.4f}" if dx != "" else ""
                dy = f"{dy:.4f}" if dy != "" else ""
                fh.write(f"{pair},{case},{r['method']},{r['n']},{r['inliers']},"
                         f"{r['ratio']:.4f},{dx},{dy},{r['t_total']:.2f}\n")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        print("usage: python -m core.bench_illumination <pair directory>")
        return 2

    src_path, ref_path = resolve_pair(argv[1])
    a, _ = load(src_path)
    b, _ = load(ref_path)
    print(f"\n{'=' * 78}\n  ILLUMINATION A/B - {pathlib.Path(argv[1]).name}\n{'=' * 78}")
    print(f"  source     {pathlib.Path(src_path).name}  {a.shape}  "
          f"DN [{a.min():.0f}, {a.max():.0f}]")
    print(f"  reference  {pathlib.Path(ref_path).name}  {b.shape}  "
          f"DN [{b.min():.0f}, {b.max():.0f}]")

    methods = [None] + sorted(METHODS)

    rows = [_run(a, b, m) for m in methods]
    _table("CASE 1 - IDENTICAL ILLUMINATION (what does turning it on cost?)", rows)

    b_x = _intensity_transform(b)
    rows_x = [_run(a, b_x, m) for m in methods]
    _table("CASE 2 - INTENSITY TRANSFORM (inverted + gamma + ramp)", rows_x,
           "NOT a sun-angle change: shadows flip polarity but do not move.")

    _write_csv(pathlib.Path(argv[1]).name,
               [("identical", rows), ("intensity_transform", rows_x)])

    print(f"\n{'=' * 78}")
    print("  Numbers above are matcher behaviour, not project metrics. Nothing")
    print("  here is cross-illumination performance - see the module docstring.")
    print(f"  written -> {RESULTS_CSV.relative_to(pathlib.Path.cwd())}")
    print(f"{'=' * 78}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
