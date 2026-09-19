import csv

import numpy as np
import pytest

from evaluation import real_eval
from evaluation.real_eval import REAL_FIELDS, insample_axis_rmse


def test_insample_axis_rmse_reads_each_axis_on_its_own():
    # A pure translation H and inliers whose errors are +-0.3 px in x and +-0.4 px in y:
    # each axis's RMSE is exactly its own error, never the combined one.
    H = np.array([[1.0, 0, 5.0], [0, 1.0, -2.0], [0, 0, 1.0]])
    src = np.array([[10, 10], [50, 20], [30, 80], [70, 60]], np.float64)
    ref = src + [5.0, -2.0] + np.array([[0.3, 0.4], [-0.3, -0.4], [0.3, -0.4], [-0.3, 0.4]])
    r = insample_axis_rmse(H, src, ref)
    assert r["n"] == 4
    assert r["x_px"] == pytest.approx(0.3)
    assert r["y_px"] == pytest.approx(0.4)


def test_insample_axis_rmse_is_empty_without_a_fit():
    pts = np.zeros((10, 2))
    assert insample_axis_rmse(None, pts, pts) == {"x_px": None, "y_px": None, "n": 0}
    assert insample_axis_rmse(np.eye(3), pts[:3], pts[:3])["n"] == 0      # < 4 points


def test_log_real_refuses_to_append_under_a_stale_header(tmp_path, monkeypatch):
    log = tmp_path / "real_pairs_log.csv"
    with open(log, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(REAL_FIELDS[:-3])
    monkeypatch.setattr(real_eval, "REAL_LOG", log)
    with pytest.raises(RuntimeError, match="header"):
        real_eval.log_real({"pair_id": "x"})


def test_log_real_appends_under_the_current_header(tmp_path, monkeypatch):
    log = tmp_path / "real_pairs_log.csv"
    monkeypatch.setattr(real_eval, "REAL_LOG", log)
    real_eval.log_real({"pair_id": "a", "insample_rmse_x_px": 0.5})
    real_eval.log_real({"pair_id": "b"})
    rows = list(csv.DictReader(open(log, encoding="utf-8")))
    assert [r["pair_id"] for r in rows] == ["a", "b"]
    assert rows[0]["insample_rmse_x_px"] == "0.5" and rows[1]["insample_rmse_x_px"] == ""


def test_the_committed_log_header_matches_real_fields():
    with open(real_eval.REAL_LOG, encoding="utf-8-sig", newline="") as f:
        assert next(csv.reader(f)) == REAL_FIELDS
