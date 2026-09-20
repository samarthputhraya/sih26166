"""A report must never leave the reader guessing which commit produced which part of it.

The demo can export a report for a result it loaded from a cache written by earlier code. Before
20 Sep 2026 the header printed only the commit that WROTE the file, so the download said one
commit while the app's identification plate said another for the same numbers.
"""
import numpy as np

from core.export import render_markdown, report


def _result():
    src = np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0], [10.0, 10.0]], np.float32)
    return {
        "source": "s.tif", "reference": "r.tif", "shape_source": (32, 32), "shape_reference": (32, 32),
        "gsd_mpp": 1.0, "scale_note": "n/a", "illumination": "gradient_orientation",
        "n_matches": 4, "ransac": {"inlier_count": 4, "inlier_ratio": 1.0, "note": "ok"},
        "H": np.eye(3), "H_final": np.eye(3), "warped": None, "warped_final": None,
        "src_inliers": src, "ref_inliers": src, "src_matches": src, "ref_matches": src,
        "match_scores": None, "metrics": {"status": "ok", "residual_median_px": 0.5},
        "metrics_note": "ok", "distribution": None, "reliability": None, "fallback": None,
        "declared": {"method": "loftr+magsac++", "why": "", "contradicted": False},
        "seconds": 1.0, "meta_source": {}, "meta_reference": {},
    }


def _header(rep):
    return render_markdown(rep).splitlines()[2]


def test_a_live_run_names_one_commit():
    rep = report(_result(), "p", "s.tif", "r.tif")
    assert rep["computed_at_commit"] is None
    h = _header(rep)
    assert h.count("commit") == 1 and "Result computed by" not in h


def test_a_cached_result_names_both_the_computing_and_the_writing_commit():
    r = _result()
    r["computed_at_commit"] = "b678272"
    rep = report(r, "p", "s.tif", "r.tif")
    rep["git_commit"] = "34e3c97"          # pretend the file is written by later code
    h = _header(rep)
    assert "Result computed by commit `b678272`" in h
    assert "this report written by commit `34e3c97`" in h


def test_the_two_commit_form_collapses_when_they_are_the_same():
    r = _result()
    r["computed_at_commit"] = "b678272"
    rep = report(r, "p", "s.tif", "r.tif")
    rep["git_commit"] = "b678272"
    h = _header(rep)
    assert h.count("commit") == 1 and "Result computed by" not in h
