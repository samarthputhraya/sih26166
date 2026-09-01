"""Guards the contract between `core/pipeline.py` and `evaluation/metrics.py`.

The bug this exists to prevent (live until 1 Sep 2026): `run_all` handed `evaluate()` the
matches that `filter_matches` had already accepted, so `inlier_ratio` asked "of the points
RANSAC kept, how many does a second RANSAC keep?" and always answered ~1.0.

Gate 2 requires `inlier_ratio > 0.60`. That criterion would have passed automatically on a pair
where half the matches were wrong.

LoFTR is not involved here -- `match` is stubbed -- so these run in milliseconds.
"""
import numpy as np
import cv2
import pytest

from core import pipeline


def _write_pair(tmp_path, n=64):
    """A minimal on-disk pair. Content is irrelevant; `match` is stubbed out."""
    d = tmp_path / "pair_test"
    d.mkdir()
    rng = np.random.default_rng(0)
    img = rng.integers(20, 200, (n, n), dtype=np.uint8)
    cv2.imwrite(str(d / "pair_test_source.tif"), img)
    cv2.imwrite(str(d / "pair_test_ref.tif"), img)
    return d / "pair_test_source.tif", d / "pair_test_ref.tif"


@pytest.fixture
def half_garbage_matches():
    """100 matches on a clean translation, plus 100 that are pure noise. Truth: ratio 0.50."""
    rng = np.random.default_rng(7)
    good = (rng.random((100, 2)) * 900 + 50).astype(np.float32)
    good_ref = (good + np.array([12.0, -8.0])).astype(np.float32)
    bad = (rng.random((100, 2)) * 1000).astype(np.float32)
    bad_ref = (rng.random((100, 2)) * 1000).astype(np.float32)
    src = np.vstack([good, bad]).astype(np.float32)
    ref = np.vstack([good_ref, bad_ref]).astype(np.float32)
    return src, ref


def test_evaluate_receives_raw_matches_not_ransac_survivors(tmp_path, monkeypatch,
                                                            half_garbage_matches):
    """The contract: `evaluate()` sees every match the matcher produced."""
    src, ref = half_garbage_matches
    monkeypatch.setattr(pipeline, "match",
                        lambda a, b, progress=None: (src, ref, np.ones(len(src), np.float32)))

    seen = {}

    def spy(ref_shape, matches_src, matches_ref, H_true=None, **kw):
        seen["n"] = len(matches_src)
        return {"n_matches": len(matches_src), "inlier_ratio": 0.0, "rmse_gt_px": None,
                "residual_px": None, "inlier_count": 0, "grid_coverage_fraction": 0.0,
                "distribution_cv": None}

    monkeypatch.setattr(pipeline, "_evaluate",
                        lambda shape, s, r, H_true=None: (spy(shape, s, r, H_true), "ok"))

    src_path, ref_path = _write_pair(tmp_path)
    result = pipeline.run_all(str(src_path), str(ref_path))

    assert seen["n"] == len(src), (
        f"evaluate() was given {seen['n']} points but the matcher produced {len(src)}. "
        "Passing RANSAC survivors makes inlier_ratio meaningless."
    )
    assert len(result["src_inliers"]) < len(src), (
        "sanity check: RANSAC should have rejected the garbage half"
    )


def test_inlier_ratio_reflects_the_garbage(tmp_path, monkeypatch, half_garbage_matches):
    """End to end with the real `evaluate()`: half the matches are wrong, so ~0.5, not ~1.0."""
    evaluate = pytest.importorskip("evaluation.metrics").evaluate  # noqa: F841

    src, ref = half_garbage_matches
    monkeypatch.setattr(pipeline, "match",
                        lambda a, b, progress=None: (src, ref, np.ones(len(src), np.float32)))

    src_path, ref_path = _write_pair(tmp_path)
    metrics = pipeline.run_all(str(src_path), str(ref_path))["metrics"]

    assert metrics is not None, "evaluation/metrics.py should be importable"
    assert 0.35 < metrics["inlier_ratio"] < 0.65, (
        f"inlier_ratio came back {metrics['inlier_ratio']:.3f}; half the matches are deliberate "
        "garbage, so anything near 1.0 means the pipeline pre-filtered the input again"
    )
