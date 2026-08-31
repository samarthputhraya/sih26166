"""Tests for evaluation.metrics.evaluate()."""

import numpy as np
import cv2
from evaluation.metrics import evaluate


def test_perfect_matches():
    """Identity transform -> rmse_gt_px ~ 0."""
    ref_shape = (480, 640)
    n = 100
    xs = np.linspace(50, 590, 10)
    ys = np.linspace(50, 430, 10)
    gx, gy = np.meshgrid(xs, ys)
    src_pts = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32)
    ref_pts = src_pts.copy()

    H_true = np.eye(3, dtype=np.float32)
    metrics = evaluate(ref_shape, src_pts, ref_pts, H_true=H_true)

    assert metrics["rmse_gt_px"] is not None
    assert metrics["rmse_gt_px"] < 0.1
    assert metrics["inlier_ratio"] > 0.99
    assert metrics["grid_coverage_fraction"] > 0.8


def test_known_offset():
    """Shift by (2, 3) -> rmse_gt_px ~ 0, residual ~ 0 (perfectly consistent matches)."""
    ref_shape = (480, 640)
    n = 100
    xs = np.linspace(50, 590, 10)
    ys = np.linspace(50, 430, 10)
    gx, gy = np.meshgrid(xs, ys)
    src_pts = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32)
    ref_pts = src_pts + np.array([2.0, 3.0], dtype=np.float32)

    H_true = np.eye(3, dtype=np.float32)
    H_true[0, 2] = 2.0
    H_true[1, 2] = 3.0

    metrics = evaluate(ref_shape, src_pts, ref_pts, H_true=H_true)

    assert metrics["rmse_gt_px"] is not None
    assert metrics["rmse_gt_px"] < 0.1
    # All matches are perfectly consistent -> residual on holdout ~ 0
    assert metrics["residual_px"] < 0.1


def test_clustered_matches():
    """All matches in one corner -> grid_coverage low, distribution_cv high."""
    ref_shape = (480, 640)
    n = 50
    src_pts = np.random.default_rng(42).uniform(10, 50, (n, 2)).astype(np.float32)
    ref_pts = src_pts + np.array([1.5, -0.5], dtype=np.float32)

    H_true = np.eye(3, dtype=np.float32)
    H_true[0, 2] = 1.5
    H_true[1, 2] = -0.5

    metrics = evaluate(ref_shape, src_pts, ref_pts, H_true=H_true)

    assert metrics["grid_coverage_fraction"] < 0.3
    assert metrics["distribution_cv"] is not None
    assert metrics["distribution_cv"] > 1.0


def test_holdout_actually_holds_out():
    """Feed matches consistent with H1 for fit set, garbage for holdout.
    residual_px must be LARGE. If small, holdout isn't held out.
    """
    ref_shape = (480, 640)
    n = 100

    # Fit set: consistent with identity
    fit_n = 80
    xs = np.linspace(50, 590, 10)
    ys = np.linspace(50, 430, 8)
    gx, gy = np.meshgrid(xs, ys)
    fit_src = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32)[:fit_n]
    fit_ref = fit_src.copy()

    # Holdout set: completely wrong (shifted by 100 px)
    hold_n = 20
    hold_src = np.random.default_rng(123).uniform(100, 200, (hold_n, 2)).astype(np.float32)
    hold_ref = hold_src + np.array([100.0, 100.0], dtype=np.float32)

    src_pts = np.vstack([fit_src, hold_src])
    ref_pts = np.vstack([fit_ref, hold_ref])

    H_true = np.eye(3, dtype=np.float32)
    metrics = evaluate(ref_shape, src_pts, ref_pts, H_true=H_true, seed=42)

    # With holdout, residual should be large (~141 px)
    # Without holdout (circular), it would be near 0
    assert metrics["residual_px"] > 50.0, f"Holdout failed: residual={metrics['residual_px']:.1f}"


def test_reports_none_without_ground_truth():
    """H_true=None -> rmse_gt_px is None, never 0.0."""
    ref_shape = (480, 640)
    n = 50
    src_pts = np.random.default_rng(42).uniform(50, 590, (n, 2)).astype(np.float32)
    ref_pts = src_pts + np.array([1.0, 2.0], dtype=np.float32)

    metrics = evaluate(ref_shape, src_pts, ref_pts, H_true=None)

    assert metrics["rmse_gt_px"] is None
    assert metrics["residual_px"] is not None
    assert metrics["n_matches"] == n


if __name__ == "__main__":
    test_perfect_matches()
    print("test_perfect_matches: PASS")
    test_known_offset()
    print("test_known_offset: PASS")
    test_clustered_matches()
    print("test_clustered_matches: PASS")
    test_holdout_actually_holds_out()
    print("test_holdout_actually_holds_out: PASS")
    test_reports_none_without_ground_truth()
    print("test_reports_none_without_ground_truth: PASS")
    print("\nAll tests passed!")