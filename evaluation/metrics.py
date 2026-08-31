"""Evaluation metrics for SIH26166.

Implements evaluate() with hold-out split to avoid circularity.
All pixel units are REFERENCE-image pixels.
"""

import numpy as np
import cv2

GRID = 8
INLIER_THRESH_PX = 3.0


def evaluate(ref_shape, matches_src, matches_ref, H_true=None, holdout_frac=0.2, seed=0):
    """Score one registration.

    Args:
        ref_shape: (H, W) of reference image
        matches_src: (N, 2) float32 source points in (x, y)
        matches_ref: (N, 2) float32 reference points in (x, y)
        H_true: Ground-truth homography (3, 3) if known (synthetic/DEM pairs), else None
        holdout_frac: Fraction of matches to hold out for residual computation
        seed: Random seed for hold-out split

    Returns:
        dict with keys:
            rmse_gt_px: Accuracy vs ground truth (None on real pairs)
            residual_px: Held-out fit residual (lower bound on error)
            inlier_count: Number of inliers
            inlier_ratio: inlier_count / total_matches
            grid_coverage_fraction: Fraction of 8x8 cells with >=1 inlier
            distribution_cv: Coefficient of variation of inliers per cell
            n_matches: Total matches
    """
    rng = np.random.default_rng(seed)
    n = len(matches_src)

    if n < 4:
        return {
            "rmse_gt_px": None,
            "residual_px": None,
            "inlier_count": 0,
            "inlier_ratio": 0.0,
            "grid_coverage_fraction": 0.0,
            "distribution_cv": None,
            "n_matches": n,
        }

    idx = rng.permutation(n)
    n_hold = max(4, int(holdout_frac * n))
    hold_idx = idx[:n_hold]
    fit_idx = idx[n_hold:]

    # Fit transform on FIT set only
    H, mask = cv2.findHomography(
        matches_src[fit_idx], matches_ref[fit_idx],
        method=cv2.USAC_MAGSAC,
        ransacReprojThreshold=INLIER_THRESH_PX,
        confidence=0.999
    )

    if H is None or mask is None:
        return {
            "rmse_gt_px": None,
            "residual_px": None,
            "inlier_count": 0,
            "inlier_ratio": 0.0,
            "grid_coverage_fraction": 0.0,
            "distribution_cv": None,
            "n_matches": n,
        }

    # Residual on HELD-OUT set
    proj = cv2.perspectiveTransform(
        matches_src[hold_idx].reshape(-1, 1, 2), H
    ).reshape(-1, 2)
    residual_px = float(np.sqrt(np.mean(np.sum((proj - matches_ref[hold_idx]) ** 2, axis=1))))

    # True accuracy vs ground truth (synthetic/DEM only)
    rmse_gt_px = None
    if H_true is not None:
        h, w = ref_shape
        gx, gy = np.meshgrid(np.linspace(0, w - 1, 20), np.linspace(0, h - 1, 20))
        pts = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32)
        ours = cv2.perspectiveTransform(pts.reshape(-1, 1, 2), H).reshape(-1, 2)
        true = cv2.perspectiveTransform(pts.reshape(-1, 1, 2), H_true).reshape(-1, 2)
        rmse_gt_px = float(np.sqrt(np.mean(np.sum((ours - true) ** 2, axis=1))))

    # Inliers and spatial uniformity on ALL matches
    err = np.linalg.norm(
        cv2.perspectiveTransform(matches_src.reshape(-1, 1, 2), H).reshape(-1, 2) - matches_ref,
        axis=1
    )
    inlier_mask = err < INLIER_THRESH_PX
    inlier_count = int(inlier_mask.sum())
    inlier_ratio = inlier_count / max(n, 1)

    # Grid coverage (8x8)
    h, w = ref_shape
    cells = np.zeros((GRID, GRID), dtype=int)
    for (x, y) in matches_ref[inlier_mask]:
        r = min(int(y / h * GRID), GRID - 1)
        c = min(int(x / w * GRID), GRID - 1)
        cells[r, c] += 1

    grid_coverage_fraction = float((cells > 0).sum() / (GRID * GRID))
    distribution_cv = float(cells.std() / cells.mean()) if cells.mean() > 0 else None

    return {
        "rmse_gt_px": rmse_gt_px,
        "residual_px": residual_px,
        "inlier_count": inlier_count,
        "inlier_ratio": inlier_ratio,
        "grid_coverage_fraction": grid_coverage_fraction,
        "distribution_cv": distribution_cv,
        "n_matches": n,
    }