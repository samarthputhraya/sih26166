"""Run SIFT, ORB and AKAZE on real lunar pairs and record the five metrics.

    python baselines/run_all_baselines.py                  # every pair it can find
    python baselines/run_all_baselines.py --log            # ...and record them
    python baselines/run_all_baselines.py --pairs pair_01

This is the classical arm of Gate 2: *"≥2× better than the best classical
baseline"*. Our own numbers come from `core/pipeline.py`; these are what they are
measured against, so the two have to be produced the same way or the comparison
is not a comparison.

Five design decisions worth defending.

1. IT FINDS PAIRS, IT DOES NOT HARDCODE THEM. Until Day 5 this script pointed at
   `data/pairs/pair_test_source.tif`, a file that has never existed - so it
   raised `FileNotFoundError` on every machine including its author's, and the
   classical baselines had therefore never run on a single real lunar pair. The
   search is `**/*_source.tif`, with the `**` mattering: every real pair lives one
   directory down (`data/pairs/pair_01/...`) and a flat glob finds nothing.

2. IT LOADS WITH `core.io_loader.load`, NOT `cv2.imread`. `imread` returns None
   for the Tier D GeoTIFF and cannot read PDS4 at all, and it silently drops the
   big-endian and signedness handling that `io_loader` exists to provide. Reading
   another owner's module is normal; this one is the project's single front door
   for pixels.

3. THE FIVE METRICS COME FROM `evaluation/metrics.py`, NOT FROM HERE. This script
   used to invent its own columns - `mean_confidence`, `dx_px`, `offset_spread_px`
   - which no other part of the project could compare against. Worse, `dx/dy` was
   a plain mean over *unfiltered* matches, so a handful of wild outliers moved it
   arbitrarily. Now the baselines are scored by exactly the function that scores
   our own method, on exactly the same definition of each metric.

4. `evaluate()` GETS THE RAW MATCHES. Every detector here returns its matches
   before any RANSAC, which is what `evaluate()` requires: it fits on 80% and
   measures on the 20% it never saw. Handing it points that a RANSAC has already
   accepted makes `inlier_ratio` ask "of the points I kept, how many do I keep?"
   and the answer is always about 1.0. That exact bug cost this project a week
   (Canonical Facts §7) and it is not going to be reintroduced here.

5. NUMBERS GO TO `evaluation/results_log.csv`, THROUGH `log_result`. Invariant 1:
   a figure that is not in that file cannot go on a slide, in the demo, or into
   an answer to a judge. This script used to write only `baselines/results.csv`
   with its own schema, which is why none of its numbers were ever quotable.
   `baselines/results.csv` is still written, as a local convenience - but it is
   scratch, and the evidence file is the one that counts.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from baselines.akaze_baseline import run_akaze          # noqa: E402
from baselines.orb_baseline import run_orb              # noqa: E402
from baselines.settings import RATIO_TEST               # noqa: E402
from baselines.sift_baseline import run_sift            # noqa: E402

PAIRS_DIR = ROOT / "data" / "pairs"
CATALOGUE = ROOT / "data" / "pairs_catalogue.csv"
SCRATCH_CSV = ROOT / "baselines" / "results.csv"

METHODS = [("SIFT", run_sift), ("ORB", run_orb), ("AKAZE", run_akaze)]

# Every extension io_loader can open, in the order resolve_pair lists them.
SOURCE_SUFFIXES = ("*_source.tif", "*_source.tiff", "*_source.IMG",
                   "*_source.img", "*_source.xml", "*_source.png")


# --------------------------------------------------------------------------
# Finding the data
# --------------------------------------------------------------------------

def _pair_id_for(src: pathlib.Path, pairs_dir: pathlib.Path) -> str:
    """The id this pair is known by in pairs_catalogue.csv.

    The directory name and the file name do not always agree - `pair_03_tierD/`
    contains `tier_d_01_source.tif`, and the catalogue calls it `tier_d_01`. Take
    whichever of the two the catalogue actually knows, so the tier resolves
    instead of reading UNCATALOGUED and refusing to log.

    Falls back to the directory name, which is what a person would call it.
    """
    from_dir = src.parent.name if src.parent != pairs_dir else ""
    from_file = src.stem.replace("_source", "")
    for candidate in (from_dir, from_file):
        if candidate and catalogue_tier(candidate) is not None:
            return candidate
    return from_dir or from_file


def discover_pairs(pairs_dir: pathlib.Path = PAIRS_DIR) -> list[tuple[str, pathlib.Path, pathlib.Path]]:
    """Every (pair_id, source, reference) under `pairs_dir`, recursively.

    Returns them sorted, so a run is reproducible and two people comparing
    output are looking at the same rows in the same order.
    """
    if not pairs_dir.is_dir():
        return []

    found: list[tuple[str, pathlib.Path, pathlib.Path]] = []
    for pattern in SOURCE_SUFFIXES:
        for src in pairs_dir.glob(f"**/{pattern}"):      # ** - pairs sit one level down
            ref = src.with_name(src.name.replace("_source", "_ref"))
            if not ref.exists():
                continue
            found.append((_pair_id_for(src, pairs_dir), src, ref))

    # A directory could match two patterns; keep the first per pair_id.
    seen: set[str] = set()
    unique = []
    for pair_id, src, ref in sorted(found, key=lambda t: (t[0], t[1].name)):
        if pair_id in seen:
            continue
        seen.add(pair_id)
        unique.append((pair_id, src, ref))
    return unique


def catalogue_tier(pair_id: str) -> str | None:
    """Rohan's tier for this pair, or None if it is not catalogued.

    NEVER invent one. `log_result` refuses a falsy tier on purpose: a number
    without its validation tier is not evidence, and guessing "A" for a pair that
    is actually two crops of one frame is the single likeliest way to lose a Q&A
    round (Invariant 2).
    """
    if not CATALOGUE.is_file():
        return None
    try:
        with open(CATALOGUE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("pair_id") == pair_id:
                    tier = (row.get("tier") or "").strip()
                    return tier or None
    except (OSError, csv.Error):
        return None
    return None


def catalogue_gsd(pair_id: str) -> float | None:
    """Ground scale from the catalogue, so areas and residuals can be given in metres."""
    if not CATALOGUE.is_file():
        return None
    try:
        with open(CATALOGUE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("pair_id") == pair_id:
                    for key in ("ref_gsd_mpp", "source_gsd_mpp"):
                        try:
                            return float(row.get(key) or "")
                        except ValueError:
                            continue
    except (OSError, csv.Error):
        return None
    return None


# --------------------------------------------------------------------------
# Pixels
# --------------------------------------------------------------------------

def to_uint8(img: np.ndarray) -> np.ndarray:
    """Raw DN -> uint8, which is what the OpenCV detectors expect.

    `io_loader.load` returns float32 raw DN by design and the range differs
    wildly between products: [7, 255] on pair_01, [0, 2040] on the Tier D source.
    Handing float32 straight to `cv2.SIFT_create().detectAndCompute` raises, and
    naively casting a [0, 2040] array to uint8 wraps it into noise.

    The 2nd-98th percentile stretch keeps terrain visible in both cases and is
    applied identically to both images of a pair, so it cannot bias the match.
    Non-finite values are replaced BEFORE the cast: NaN cast to uint8 is
    undefined behaviour and produces arbitrary bytes rather than an error.
    """
    a = np.asarray(img, dtype=np.float64)
    if a.ndim != 2:
        raise ValueError(f"expected a 2-D grayscale image, got shape {a.shape}")

    finite = a[np.isfinite(a)]
    if finite.size == 0:
        return np.zeros(a.shape, np.uint8)

    lo, hi = np.percentile(finite, [2, 98])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        lo, hi = float(finite.min()), float(finite.max())
        if hi <= lo:
            return np.zeros(a.shape, np.uint8)

    scaled = (a - lo) / (hi - lo) * 255.0
    scaled = np.nan_to_num(scaled, nan=0.0, posinf=255.0, neginf=0.0)
    return np.clip(scaled, 0, 255).astype(np.uint8)


def load_pair(src_path: pathlib.Path, ref_path: pathlib.Path):
    """Both images of a pair as uint8, plus the reference shape metrics use."""
    from core.io_loader import load

    a, _ = load(src_path)
    b, _ = load(ref_path)
    return to_uint8(a), to_uint8(b), b.shape[:2]


# --------------------------------------------------------------------------
# Scoring - by evaluation/metrics.py, never here
# --------------------------------------------------------------------------

def score(ref_shape, src_pts, ref_pts) -> dict | None:
    """Samrudh's `evaluate()` on the RAW matches. See design decision 4."""
    try:
        from evaluation.metrics import evaluate
    except ImportError:
        return None
    return evaluate(ref_shape, np.asarray(src_pts, np.float32),
                    np.asarray(ref_pts, np.float32))


def run_one(name, fn, img_a, img_b, ref_shape, ratio):
    """One detector on one pair. Returns (metrics_or_None, n_raw, seconds)."""
    t0 = time.perf_counter()
    try:
        src_pts, ref_pts, _conf, _elapsed = fn(img_a, img_b, ratio=ratio)
    except Exception as e:                       # a dead detector must not kill the sweep
        return None, 0, time.perf_counter() - t0, f"{type(e).__name__}: {e}"
    seconds = time.perf_counter() - t0
    return score(ref_shape, src_pts, ref_pts), int(len(src_pts)), seconds, None


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python baselines/run_all_baselines.py",
        description="Run the three classical baselines on real lunar pairs.")
    p.add_argument("--pairs", nargs="*", default=None,
                   help="pair ids to run; default is every pair found")
    p.add_argument("--ratio", type=float, default=RATIO_TEST,
                   help=f"Lowe ratio test, same for all three (default {RATIO_TEST})")
    p.add_argument("--log", action="store_true",
                   help="append each result to evaluation/results_log.csv")
    p.add_argument("--tier", default=None,
                   help="override the catalogue tier; needed only for an uncatalogued pair")
    p.add_argument("--notes", default="", help="free text for the logged rows")
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv[1:])

    pairs = discover_pairs()
    if args.pairs:
        wanted = set(args.pairs)
        pairs = [p for p in pairs if p[0] in wanted]
        missing = wanted - {p[0] for p in pairs}
        if missing:
            print(f"no such pair(s) under {PAIRS_DIR}: {sorted(missing)}")
            return 2

    if not pairs:
        print(f"No pairs found under {PAIRS_DIR}.")
        print("  Looked for **/*_source.* with a matching *_ref.* beside it.")
        print("  The image files are gitignored - sync them from the shared Drive folder.")
        return 2

    print("=" * 74)
    print(f"CLASSICAL BASELINES - SIFT / ORB / AKAZE   (ratio test {args.ratio}, "
          f"identical for all three)")
    print("=" * 74)

    scratch_rows = []
    logged = failed = 0

    for pair_id, src_path, ref_path in pairs:
        tier = args.tier or catalogue_tier(pair_id)
        gsd = catalogue_gsd(pair_id)

        print(f"\n{pair_id}   tier={tier or 'UNCATALOGUED'}")
        print(f"  source {src_path.name}")
        print(f"  ref    {ref_path.name}")

        try:
            img_a, img_b, ref_shape = load_pair(src_path, ref_path)
        except Exception as e:
            print(f"  SKIPPED - could not load: {type(e).__name__}: {e}")
            failed += 1
            continue
        print(f"  shapes {img_a.shape} vs {img_b.shape}")

        for name, fn in METHODS:
            metrics, n_raw, seconds, err = run_one(
                name, fn, img_a, img_b, ref_shape, args.ratio)

            if err is not None:
                print(f"  {name:6s} FAILED - {err}")
                failed += 1
                continue
            if metrics is None:
                print(f"  {name:6s} evaluation/metrics.py unavailable - not scored")
                failed += 1
                continue

            status = metrics.get("status", "ok")
            print(f"  {name:6s} matches={n_raw:5d}  status={status:16s} "
                  f"inlier_ratio={metrics['inlier_ratio']:.4f}  "
                  f"residual_px={metrics['residual_px'] if metrics['residual_px'] is None else round(metrics['residual_px'], 4)}  "
                  f"{seconds:.2f}s")

            scratch_rows.append({
                "pair_id": pair_id, "tier": tier, "method": name,
                "n_matches": n_raw, "status": status,
                "residual_px": metrics["residual_px"],
                "inlier_ratio": metrics["inlier_ratio"],
                "grid_coverage_fraction": metrics["grid_coverage_fraction"],
                "distribution_cv": metrics["distribution_cv"],
                "runtime_s": round(seconds, 4),
            })

            if args.log:
                if not tier:
                    print(f"         NOT LOGGED - {pair_id} has no tier in "
                          f"pairs_catalogue.csv. Add the row, or pass --tier. "
                          f"A number without its tier is not evidence.")
                    failed += 1
                    continue
                try:
                    from evaluation.logger import log_result
                    config = (f"{name}, Lowe ratio {args.ratio}, raw DN percentile-stretched "
                              f"to uint8, no illumination normalisation, matches unfiltered")
                    log_result(pair_id, tier, name, metrics, config=config,
                               gsd_mpp=gsd, notes=args.notes or "classical baseline")
                    logged += 1
                except Exception as e:
                    print(f"         NOT LOGGED - {type(e).__name__}: {e}")
                    failed += 1

    # Scratch CSV, for reading at a glance. NOT the evidence file - see decision 5.
    if scratch_rows:
        SCRATCH_CSV.parent.mkdir(parents=True, exist_ok=True)
        with open(SCRATCH_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(scratch_rows[0]))
            w.writeheader()
            w.writerows(scratch_rows)
        print(f"\nScratch table: {SCRATCH_CSV}")

    if args.log:
        print(f"Logged {logged} row(s) to evaluation/results_log.csv")
    else:
        print("\nNothing was logged. Re-run with --log to record these in "
              "evaluation/results_log.csv - under Invariant 1 nothing here is "
              "quotable until you do.")

    if failed:
        print(f"{failed} method/pair combination(s) did not produce a row.")
    return 0 if scratch_rows else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
