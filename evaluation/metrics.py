import numpy as np
import cv2

GRID = 8
INLIER_THRESH_PX = 3.0

def _failed(reason, n):
    return {"rmse_gt_px": None, "residual_px": None, "inlier_count": 0,
            "inlier_ratio": 0.0, "grid_coverage_fraction": 0.0,
            "distribution_cv": None, "n_matches": n, "status": reason}

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
    if len(hold) > 0:
        proj = cv2.perspectiveTransform(matches_src[hold].reshape(-1,1,2), H).reshape(-1,2)
        residual_px = float(np.sqrt(np.mean(np.sum((proj - matches_ref[hold])**2, axis=1))))
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
        "residual_px":            residual_px,                      # held-out fit residual.
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