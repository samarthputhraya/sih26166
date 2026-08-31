"""Run all classical baselines across configurations and log to evaluation/results_log.csv.

Configs:
  1: Raw images (no illumination normalization)
  2: Illumination-normalized images (using core.illumination.normalize when available)
  3: LoFTR alone (handled by Samartha's pipeline, not here)
  4: Full pipeline (illumination + LoFTR, handled by Samartha's pipeline)

This script handles Configs 1 and 2 for SIFT, ORB, AKAZE.
"""
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from baselines.sift_baseline import run_sift
from baselines.orb_baseline import run_orb
from baselines.akaze_baseline import run_akaze
from core.io_loader import load

try:
    from evaluation.metrics import evaluate
    HAS_EVALUATE = True
except ImportError:
    HAS_EVALUATE = False
    print("WARNING: evaluation.metrics not available. Logging basic stats only.", file=sys.stderr)

try:
    from core.illumination import normalize as illum_normalize
    HAS_ILLUM = True
except ImportError:
    HAS_ILLUM = False
    print("WARNING: core.illumination.normalize not available. Config 2 will be skipped.", file=sys.stderr)

METHODS = {
    "SIFT": run_sift,
    "ORB": run_orb,
    "AKAZE": run_akaze,
}

CONFIGS = {
    1: "raw",
    2: "illum_normalized",
}

RESULTS_LOG = REPO_ROOT / "evaluation" / "results_log.csv"
RESULTS_LOG.parent.mkdir(parents=True, exist_ok=True)

# CSV header from SAMRUDH_EVALUATION_GUIDE.md
CSV_FIELDS = [
    "timestamp", "pair_id", "tier", "method", "config",
    "rmse_gt_px", "residual_px", "inlier_count", "inlier_ratio",
    "grid_coverage_fraction", "distribution_cv", "n_matches", "gsd_mpp"
]


def _ensure_csv_header():
    if not RESULTS_LOG.exists():
        with open(RESULTS_LOG, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def _load_pair(pair_id: str):
    """Load source and reference images for a pair_id."""
    pairs_dir = REPO_ROOT / "data" / "pairs"
    src_path = pairs_dir / f"{pair_id}_source.tif"
    ref_path = pairs_dir / f"{pair_id}_ref.tif"

    if not src_path.exists() or not ref_path.exists():
        raise FileNotFoundError(f"Pair {pair_id} not found in {pairs_dir}")

    src_img, src_meta = load(str(src_path))
    ref_img, ref_meta = load(str(ref_path))

    # io_loader.load returns float32; convert to uint8 for classical detectors
    # Scale from float32 [0, 1] or [0, 255] to uint8
    def to_uint8(img):
        if img.dtype == np.float32 or img.dtype == np.float64:
            if img.max() <= 1.0:
                img = (img * 255).clip(0, 255)
            else:
                img = img.clip(0, 255)
            return img.astype(np.uint8)
        return img.astype(np.uint8)

    return to_uint8(src_img), to_uint8(ref_img), src_meta, ref_meta


def _run_config(method_name: str, run_fn, src_img, ref_img, config: int):
    """Run a single method on a single config."""
    if config == 1:
        # Raw images
        src_pts, ref_pts = run_fn(src_img, ref_img)
    elif config == 2:
        if not HAS_ILLUM:
            return None
        # Illumination normalized
        src_norm = illum_normalize(src_img)
        ref_norm = illum_normalize(ref_img)
        src_pts, ref_pts = run_fn(src_norm, ref_norm)
    else:
        raise ValueError(f"Unknown config: {config}")
    return src_pts, ref_pts


def _compute_basic_metrics(src_pts, ref_pts, ref_shape):
    """Compute basic metrics without evaluation.metrics."""
    n = len(src_pts)
    if n < 4:
        return {
            "inlier_count": 0,
            "inlier_ratio": 0.0,
            "grid_coverage_fraction": 0.0,
            "distribution_cv": None,
            "n_matches": n,
        }

    # Run RANSAC to get inliers
    H, mask = cv2.findHomography(
        src_pts, ref_pts,
        method=cv2.USAC_MAGSAC,
        ransacReprojThreshold=3.0,
        confidence=0.999
    )

    if H is None or mask is None:
        return {
            "inlier_count": 0,
            "inlier_ratio": 0.0,
            "grid_coverage_fraction": 0.0,
            "distribution_cv": None,
            "n_matches": n,
        }

    inlier_mask = mask.ravel().astype(bool)
    inlier_count = int(inlier_mask.sum())
    inlier_ratio = inlier_count / max(n, 1)

    # Grid coverage (8x8)
    GRID = 8
    h, w = ref_shape
    cells = np.zeros((GRID, GRID), dtype=int)
    for (x, y) in ref_pts[inlier_mask]:
        r = min(int(y / h * GRID), GRID - 1)
        c = min(int(x / w * GRID), GRID - 1)
        cells[r, c] += 1

    grid_coverage_fraction = float((cells > 0).sum() / (GRID * GRID))
    distribution_cv = float(cells.std() / cells.mean()) if cells.mean() > 0 else None

    return {
        "inlier_count": inlier_count,
        "inlier_ratio": inlier_ratio,
        "grid_coverage_fraction": grid_coverage_fraction,
        "distribution_cv": distribution_cv,
        "n_matches": n,
    }


def run_all_baselines(pair_ids=None, tiers=None):
    """Run all baseline methods on all configs for given pairs.

    Args:
        pair_ids: List of pair IDs to process (e.g., ["pair_01", "pair_02"])
        tiers: Dict mapping pair_id to tier (A, B, B+, C, D)

    If pair_ids is None, discovers all pairs in data/pairs/.
    """
    _ensure_csv_header()

    pairs_dir = REPO_ROOT / "data" / "pairs"
    if pair_ids is None:
        # Discover pairs from _source.tif files
        pair_ids = []
        for f in pairs_dir.glob("*_source.tif"):
            pair_ids.append(f.stem.replace("_source", ""))

    if not pair_ids:
        print("No pairs found in data/pairs/. Run with test pair generator instead.")
        return

    # Default tier mapping if not provided
    if tiers is None:
        tiers = {pid: "unknown" for pid in pair_ids}

    rows = []
    for pair_id in pair_ids:
        print(f"\nProcessing {pair_id} (tier: {tiers.get(pair_id, 'unknown')})...")
        try:
            src_img, ref_img, src_meta, ref_meta = _load_pair(pair_id)
        except FileNotFoundError as e:
            print(f"  SKIP: {e}")
            continue

        ref_shape = ref_img.shape[:2]
        gsd_mpp = ref_meta.get("gsd_mpp")

        for method_name, run_fn in METHODS.items():
            for config_num, config_name in CONFIGS.items():
                print(f"  {method_name} config={config_num} ({config_name})...")
                result = _run_config(method_name, run_fn, src_img, ref_img, config_num)

                if result is None:
                    print(f"    SKIP (illumination not available)")
                    continue

                src_pts, ref_pts = result
                n_matches = len(src_pts)

                # Get metrics
                if HAS_EVALUATE and n_matches >= 4:
                    metrics = evaluate(
                        ref_shape=ref_shape,
                        matches_src=src_pts,
                        matches_ref=ref_pts,
                        H_true=None,  # No ground truth for real pairs
                        holdout_frac=0.2,
                        seed=42
                    )
                else:
                    metrics = _compute_basic_metrics(src_pts, ref_pts, ref_shape)
                    metrics["rmse_gt_px"] = None
                    metrics["residual_px"] = None

                row = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "pair_id": pair_id,
                    "tier": tiers.get(pair_id, "unknown"),
                    "method": method_name,
                    "config": config_num,
                    "rmse_gt_px": metrics.get("rmse_gt_px"),
                    "residual_px": metrics.get("residual_px"),
                    "inlier_count": metrics.get("inlier_count", 0),
                    "inlier_ratio": metrics.get("inlier_ratio", 0.0),
                    "grid_coverage_fraction": metrics.get("grid_coverage_fraction", 0.0),
                    "distribution_cv": metrics.get("distribution_cv"),
                    "n_matches": metrics.get("n_matches", 0),
                    "gsd_mpp": gsd_mpp,
                }
                rows.append(row)
                print(f"    matches={row['n_matches']}, inliers={row['inlier_count']}, "
                      f"coverage={row['grid_coverage_fraction']:.2%}")

    # Append to CSV
    with open(RESULTS_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        for row in rows:
            writer.writerow(row)

    print(f"\nLogged {len(rows)} rows to {RESULTS_LOG}")


def run_test_pair():
    """Run baselines on the synthetic test pair (Day 1 verification)."""
    from baselines.make_test_pair import make_pair

    print("Running baselines on synthetic test pair (dx=7, dy=5)...")
    src, ref = make_pair(dx=7, dy=5, seed=0)

    for method_name, run_fn in METHODS.items():
        src_pts, ref_pts = run_fn(src, ref)
        n = len(src_pts)
        if n > 0:
            offset = np.median(ref_pts - src_pts, axis=0)
            print(f"  {method_name}: {n} matches, median(ref-src)={offset}")
        else:
            print(f"  {method_name}: NO MATCHES")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run classical baselines")
    parser.add_argument("--test", action="store_true", help="Run on synthetic test pair")
    parser.add_argument("--pairs", nargs="+", help="Pair IDs to process")
    args = parser.parse_args()

    if args.test:
        run_test_pair()
    else:
        run_all_baselines(pair_ids=args.pairs)