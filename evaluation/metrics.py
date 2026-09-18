import numpy as np
import cv2

GRID = 8
INLIER_THRESH_PX = 3.0

def _failed(reason, n):
    return {"rmse_gt_px": None, "residual_px": None, "inlier_count": 0,
            "inlier_ratio": 0.0, "grid_coverage_fraction": None,
            "distribution_cv": None, "n_matches": n, "status": reason,
            "residual_median_px": None, "holdout_inlier_rmse_px": None, "holdout_inlier_frac": None}

def evaluate(ref_shape, matches_src, matches_ref, H_true=None, holdout_frac=0.2, seed=0):
    """Score one registration.

    matches_src/matches_ref MUST be the RAW matcher output, BEFORE any RANSAC filtering.

    matches_src, matches_ref : (N,2) float arrays of (x, y), same order.
    H_true : ground-truth homography if known (synthetic / DEM pairs), else None.
    ALL pixel units are REFERENCE-image pixels.
    """
    rng = np.random.default_rng(seed)
    n = len(matches_src)
    
    # We need at least 4 points to compute a homography
    if n < 4:
        return _failed("too_few_matches", n)
        
    idx = rng.permutation(n)
    n_hold = max(4, int(holdout_frac * n))
    
    # Ensure the fit set has at least 4 points
    if n - n_hold < 4:
        n_hold = max(0, n - 4)
        
    hold, fit = idx[:n_hold], idx[n_hold:]

    # --- fit the transform on the FIT set only -----------------------------
    H, mask = cv2.findHomography(matches_src[fit], matches_ref[fit],
                                 method=cv2.USAC_MAGSAC,
                                 ransacReprojThreshold=INLIER_THRESH_PX,
                                 confidence=0.999)
                                 
    if H is None:
        return _failed("ransac_failed", n)

    # --- residual on the HELD-OUT set (real pairs) -------------------------
    # residual_px is the RMSE over EVERY held-out match, outliers included. On the
    # synthetic pairs it was designed on (~98 % inliers) that is the registration
    # error; on a real pair with 40 % outliers it is the outliers' spread, and on
    # 18 Sep 2026 it read 352 px on a pair whose inliers sit at 0.5 px. Its meaning
    # is kept (every existing row in results_log.csv uses it) and three robust
    # held-out numbers are added beside it, each computed on the SAME held-out 20 %
    # the fit never saw:
    #   residual_median_px      median held-out error - no threshold, robust to <50 % outliers
    #   holdout_inlier_rmse_px  RMSE of held-out matches within INLIER_THRESH_PX of the fit
    #   holdout_inlier_frac     share of held-out matches within that threshold
    residual_median_px = holdout_inlier_rmse_px = holdout_inlier_frac = None
    if len(hold) > 0:
        proj = cv2.perspectiveTransform(matches_src[hold].reshape(-1,1,2), H).reshape(-1,2)
        e_hold = np.sqrt(np.sum((proj - matches_ref[hold])**2, axis=1))
        residual_px = float(np.sqrt(np.mean(e_hold**2)))
        residual_median_px = float(np.median(e_hold))
        in_h = e_hold < INLIER_THRESH_PX
        holdout_inlier_frac = float(in_h.mean())
        if in_h.any():
            holdout_inlier_rmse_px = float(np.sqrt(np.mean(e_hold[in_h]**2)))
    else:
        residual_px = None

    # --- true accuracy vs ground truth (synthetic / DEM only) --------------
    rmse_gt_px = None
    if H_true is not None:
        h, w = ref_shape
        gx, gy = np.meshgrid(np.linspace(0, w-1, 20), np.linspace(0, h-1, 20))
        pts  = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32)
        ours = cv2.perspectiveTransform(pts.reshape(-1,1,2), H).reshape(-1,2)
        true = cv2.perspectiveTransform(pts.reshape(-1,1,2), H_true).reshape(-1,2)
        rmse_gt_px = float(np.sqrt(np.mean(np.sum((ours - true)**2, axis=1))))

    # --- inliers and spatial uniformity ------------------------------------
    err = np.linalg.norm(
        cv2.perspectiveTransform(matches_src.reshape(-1,1,2), H).reshape(-1,2) - matches_ref,
        axis=1)
    inlier = err < INLIER_THRESH_PX
    inlier_count = int(inlier.sum())

    h, w = ref_shape
    cells = np.zeros((GRID, GRID), dtype=int)
    for (x, y) in matches_ref[inlier]:
        r = min(int(y / h * GRID), GRID-1)
        c = min(int(x / w * GRID), GRID-1)
        cells[r, c] += 1

    return {
        "rmse_gt_px":             rmse_gt_px,                       # accuracy. None on real pairs.
        "residual_px":            residual_px,                      # held-out fit residual, ALL held-out matches.
        "residual_median_px":     residual_median_px,               # held-out, median (robust).
        "holdout_inlier_rmse_px": holdout_inlier_rmse_px,           # held-out, within 3 px of the fit.
        "holdout_inlier_frac":    holdout_inlier_frac,
        "inlier_count":           inlier_count,
        "inlier_ratio":           inlier_count / max(n, 1),
        "grid_coverage_fraction": float((cells > 0).sum() / (GRID*GRID)),
        "distribution_cv":        float(cells.std() / cells.mean()) if cells.mean() > 0 else None,
        "n_matches":              n,
        "status":                 "ok",
    }

if __name__ == "__main__":
    # Sanity check with dummy data
    dummy_src = np.random.rand(100, 2) * 1000
    dummy_ref = dummy_src + np.array([5.0, -2.0]) # simple translation
    H_dummy = np.array([[1, 0, 5], [0, 1, -2], [0, 0, 1]], dtype=float)
    
    results = evaluate((1024, 1024), dummy_src.astype(np.float32), dummy_ref.astype(np.float32), H_true=H_dummy)
    print("Metrics Engine Test Run:")
    for k, v in results.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")