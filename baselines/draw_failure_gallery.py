"""Draw failure gallery images for classical baselines.

Produces visualizations with green inlier lines and red outlier lines,
annotated with real metrics from the CSV.
"""
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from baselines.sift_baseline import run_sift
from baselines.orb_baseline import run_orb
from baselines.akaze_baseline import run_akaze
from core.io_loader import load

METHODS = {
    "SIFT": run_sift,
    "ORB": run_orb,
    "AKAZE": run_akaze,
}

GALLERY_DIR = REPO_ROOT / "baselines" / "failure_gallery"
GALLERY_DIR.mkdir(parents=True, exist_ok=True)

INLIER_THRESH_PX = 3.0
GRID = 8


def _load_pair(pair_id: str):
    """Load source and reference images for a pair_id."""
    pairs_dir = REPO_ROOT / "data" / "pairs"
    src_path = pairs_dir / f"{pair_id}_source.tif"
    ref_path = pairs_dir / f"{pair_id}_ref.tif"

    if not src_path.exists() or not ref_path.exists():
        raise FileNotFoundError(f"Pair {pair_id} not found in {pairs_dir}")

    src_img, src_meta = load(str(src_path))
    ref_img, ref_meta = load(str(ref_path))

    def to_uint8(img):
        if img.dtype == np.float32 or img.dtype == np.float64:
            if img.max() <= 1.0:
                img = (img * 255).clip(0, 255)
            else:
                img = img.clip(0, 255)
            return img.astype(np.uint8)
        return img.astype(np.uint8)

    return to_uint8(src_img), to_uint8(ref_img), src_meta, ref_meta


def _compute_metrics(src_pts, ref_pts, ref_shape):
    """Compute metrics matching evaluation.metrics.evaluate() output."""
    n = len(src_pts)
    if n < 4:
        return {
            "n_matches": n,
            "inlier_count": 0,
            "inlier_ratio": 0.0,
            "residual_px": None,
            "grid_coverage_fraction": 0.0,
            "distribution_cv": None,
        }

    H, mask = cv2.findHomography(
        src_pts, ref_pts,
        method=cv2.USAC_MAGSAC,
        ransacReprojThreshold=INLIER_THRESH_PX,
        confidence=0.999
    )

    if H is None or mask is None:
        return {
            "n_matches": n,
            "inlier_count": 0,
            "inlier_ratio": 0.0,
            "residual_px": None,
            "grid_coverage_fraction": 0.0,
            "distribution_cv": None,
        }

    inlier_mask = mask.ravel().astype(bool)
    inlier_count = int(inlier_mask.sum())
    inlier_ratio = inlier_count / max(n, 1)

    # Held-out residual (20% holdout)
    rng = np.random.default_rng(42)
    idx = rng.permutation(n)
    n_hold = max(4, int(0.2 * n))
    hold_idx = idx[:n_hold]
    fit_idx = idx[n_hold:]

    if len(fit_idx) >= 4:
        H_fit, _ = cv2.findHomography(
            src_pts[fit_idx], ref_pts[fit_idx],
            method=cv2.USAC_MAGSAC,
            ransacReprojThreshold=INLIER_THRESH_PX,
            confidence=0.999
        )
        if H_fit is not None:
            proj = cv2.perspectiveTransform(
                src_pts[hold_idx].reshape(-1, 1, 2), H_fit
            ).reshape(-1, 2)
            residual_px = float(np.sqrt(np.mean(np.sum((proj - ref_pts[hold_idx]) ** 2, axis=1))))
        else:
            residual_px = None
    else:
        residual_px = None

    # Grid coverage
    h, w = ref_shape
    cells = np.zeros((GRID, GRID), dtype=int)
    for (x, y) in ref_pts[inlier_mask]:
        r = min(int(y / h * GRID), GRID - 1)
        c = min(int(x / w * GRID), GRID - 1)
        cells[r, c] += 1

    grid_coverage_fraction = float((cells > 0).sum() / (GRID * GRID))
    distribution_cv = float(cells.std() / cells.mean()) if cells.mean() > 0 else None

    return {
        "n_matches": n,
        "inlier_count": inlier_count,
        "inlier_ratio": inlier_ratio,
        "residual_px": residual_px,
        "grid_coverage_fraction": grid_coverage_fraction,
        "distribution_cv": distribution_cv,
        "inlier_mask": inlier_mask,
        "H": H,
    }


def draw_failure_gallery(pair_id: str, max_images: int = 3):
    """Generate failure gallery images for a pair.

    Args:
        pair_id: Pair identifier (e.g., "pair_01")
        max_images: Maximum number of failure images to generate per pair
    """
    print(f"Generating failure gallery for {pair_id}...")
    src_img, ref_img, src_meta, ref_meta = _load_pair(pair_id)

    # Run all methods on raw images (config 1)
    results = {}
    for method_name, run_fn in METHODS.items():
        src_pts, ref_pts = run_fn(src_img, ref_img)
        metrics = _compute_metrics(src_pts, ref_pts, ref_img.shape[:2])
        metrics["src_pts"] = src_pts
        metrics["ref_pts"] = ref_pts
        results[method_name] = metrics
        print(f"  {method_name}: {metrics['n_matches']} matches, "
              f"inliers={metrics['inlier_count']}, "
              f"residual={metrics['residual_px']}, "
              f"coverage={metrics['grid_coverage_fraction']:.2%}")

    # Sort by residual_px (worst first) or by inlier_ratio (lowest first)
    # Filter to methods that actually produced matches
    valid_results = {k: v for k, v in results.items() if v["n_matches"] > 0}
    if not valid_results:
        print("  No valid results to visualize")
        return

    # Sort: worst residual_px first, then lowest inlier_ratio
    sorted_methods = sorted(
        valid_results.items(),
        key=lambda kv: (kv[1]["residual_px"] or float('inf'), kv[1]["inlier_ratio"])
    )

    # Take worst N
    for method_name, metrics in sorted_methods[:max_images]:
        src_pts = metrics["src_pts"]
        ref_pts = metrics["ref_pts"]
        inlier_mask = metrics["inlier_mask"]

        # Create side-by-side visualization
        vis = np.hstack([src_img, ref_img])
        vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)
        offset = src_img.shape[1]

        # Draw match lines
        for (x1, y1), (x2, y2), ok in zip(src_pts, ref_pts, inlier_mask):
            color = (0, 255, 0) if ok else (0, 0, 255)  # Green inlier, Red outlier
            cv2.line(vis, (int(x1), int(y1)), (int(x2) + offset, int(y2)), color, 1)

        # Draw keypoints as small circles
        for (x1, y1), ok in zip(src_pts, inlier_mask):
            color = (0, 255, 0) if ok else (0, 0, 255)
            cv2.circle(vis, (int(x1), int(y1)), 2, color, -1)
        for (x2, y2), ok in zip(ref_pts, inlier_mask):
            color = (0, 255, 0) if ok else (0, 0, 255)
            cv2.circle(vis, (int(x2) + offset, int(y2)), 2, color, -1)

        # Caption with real metrics
        residual_str = f"{metrics['residual_px']:.1f}px" if metrics['residual_px'] is not None else "N/A"
        caption = (
            f"{method_name} | {pair_id} | "
            f"{metrics['n_matches']} matches | "
            f"residual {residual_str} | "
            f"inliers {metrics['inlier_ratio']:.0%} | "
            f"coverage {metrics['grid_coverage_fraction']:.0%}"
        )

        # Add caption background
        cv2.rectangle(vis, (5, 5), (vis.shape[1] - 5, 35), (0, 0, 0), -1)
        cv2.putText(vis, caption, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        out_path = GALLERY_DIR / f"{pair_id}_{method_name}_failure.jpg"
        cv2.imwrite(str(out_path), vis)
        print(f"  Saved: {out_path}")


def draw_all_galleries(pair_ids=None, max_per_pair: int = 3):
    """Generate failure galleries for all pairs."""
    pairs_dir = REPO_ROOT / "data" / "pairs"
    if pair_ids is None:
        pair_ids = []
        for f in pairs_dir.glob("*_source.tif"):
            pair_ids.append(f.stem.replace("_source", ""))

    if not pair_ids:
        print("No pairs found in data/pairs/")
        return

    for pair_id in pair_ids:
        try:
            draw_failure_gallery(pair_id, max_images=max_per_pair)
        except FileNotFoundError as e:
            print(f"SKIP {pair_id}: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate failure gallery images")
    parser.add_argument("--pairs", nargs="+", help="Pair IDs to process")
    parser.add_argument("--max-per-pair", type=int, default=3, help="Max images per pair")
    args = parser.parse_args()

    draw_all_galleries(pair_ids=args.pairs, max_per_pair=args.max_per_pair)