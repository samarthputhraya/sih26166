import numpy as np
import cv2
import pytest
from evaluation.metrics import evaluate

def test_perfect_matches():
    # Identity transform -> rmse_gt_px ~ 0
    src = np.random.rand(100, 2) * 1000
    ref = src.copy()
    H_true = np.eye(3)
    
    res = evaluate((1024, 1024), src.astype(np.float32), ref.astype(np.float32), H_true=H_true)
    assert res is not None
    assert res["rmse_gt_px"] < 1e-4

def test_known_offset():
    # Shift by (2,3) -> residual ~ sqrt(4+9) = 3.6055
    src = np.random.rand(100, 2) * 1000
    ref = src + np.array([2.0, 3.0])
    
    res = evaluate((1024, 1024), src.astype(np.float32), ref.astype(np.float32))
    assert res is not None
    assert np.isclose(res["residual_px"], 3.6055, atol=1e-2)

def test_clustered_matches():
    # All matches in one corner (e.g., top-left 10x10 area of a 1024x1024 image)
    src = np.random.rand(100, 2) * 10
    ref = src.copy()
    
    res = evaluate((1024, 1024), src.astype(np.float32), ref.astype(np.float32))
    assert res is not None
    # 1 cell out of 64 -> 1/64 = 0.015625
    assert res["grid_coverage_fraction"] < 0.05
    assert res["distribution_cv"] > 5.0  # Highly skewed distribution

def test_holdout_actually_holds_out():
    # Feed 80 perfect points (RANSAC fits these) and 20 garbage points.
    # Because of the random split, the holdout set will inevitably contain garbage points.
    # If the holdout is correctly held out, the residual_px must be large.
    src_good = np.random.rand(80, 2) * 1000
    ref_good = src_good.copy()
    
    src_bad = np.random.rand(20, 2) * 1000
    ref_bad = src_bad + 500.0  # massive 500px error
    
    src = np.vstack([src_good, src_bad]).astype(np.float32)
    ref = np.vstack([ref_good, ref_bad]).astype(np.float32)
    
    res = evaluate((1024, 1024), src, ref, seed=42)
    assert res is not None
    assert res["residual_px"] > 10.0  # Proves we are measuring actual held-out error

def test_reports_none_without_ground_truth():
    # H_true=None -> rmse_gt_px is None, never 0.0.
    src = np.random.rand(100, 2) * 1000
    ref = src.copy()
    
    res = evaluate((1024, 1024), src.astype(np.float32), ref.astype(np.float32), H_true=None)
    assert res is not None
    assert res["rmse_gt_px"] is None