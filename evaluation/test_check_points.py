"""Independent check points: the scorer's arithmetic and its refusals."""
import json

import numpy as np
import pytest

from evaluation import check_points as C

PTS = np.array([[10.0, 12.0], [200.0, 40.0], [55.5, 300.0], [400.0, 380.0], [123.0, 222.0],
                [310.0, 90.0], [80.0, 150.0], [260.0, 260.0]])


def test_a_perfect_transform_scores_zero():
    H = np.array([[0.5, 0.0, 3.0], [0.0, 0.5, -2.0], [0.0, 0.0, 1.0]])
    s = C.score(H, PTS, C.apply_h(H, PTS), ref_gsd=1.0, src_gsd=0.5)
    assert s["n"] == len(PTS) and s["rmse_px"] == pytest.approx(0.0, abs=1e-9)


def test_a_one_pixel_shift_is_one_pixel_and_converts_to_metres_and_source_pixels():
    s = C.score(np.eye(3), PTS, PTS + [1.0, 0.0], ref_gsd=1.2, src_gsd=0.3)
    assert s["rmse_px"] == pytest.approx(1.0)
    assert s["rmse_x_px"] == pytest.approx(1.0) and s["rmse_y_px"] == pytest.approx(0.0)
    assert s["rmse_m"] == pytest.approx(1.2)
    assert s["rmse_src_px"] == pytest.approx(4.0)        # 1.2 m on a 0.3 m source grid


def test_the_floor_of_points_on_one_plane_is_zero():
    H = np.array([[0.9, 0.05, 4.0], [-0.03, 1.1, -7.0], [1e-5, -2e-5, 1.0]])
    f = C.floor(PTS, C.apply_h(H, PTS), ref_gsd=1.0, src_gsd=1.0)
    assert f["rmse_px"] == pytest.approx(0.0, abs=1e-6)


def test_the_floor_needs_enough_points():
    assert C.floor(PTS[:4], PTS[:4], 1.0, 1.0) == {"n": 4}


def _pair(tmp_path, pid="p_w01"):
    d = tmp_path / "pairs" / pid
    d.mkdir(parents=True)
    (d / f"{pid}_source.tif").write_bytes(b"source bytes")
    (d / f"{pid}_ref.tif").write_bytes(b"reference bytes")
    (d / "geometry_prior.json").write_text(json.dumps({
        "source": {"resampled_gsd_mpp": 0.5}, "reference": {"resampled_gsd_mpp": 1.0},
        "prior_H_source_to_reference": [[0.5, 0, 0], [0, 0.5, 0], [0, 0, 1]]}), encoding="utf-8")
    return d


def _clicks(tmp_path, pid, rows):
    cp = tmp_path / "cp"
    cp.mkdir(exist_ok=True)
    with open(cp / f"{pid}.csv", "w", encoding="utf-8", newline="") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=C.FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in C.FIELDS})
    return cp


def test_repeats_are_never_check_points_and_give_the_click_precision(tmp_path):
    d = _pair(tmp_path)
    sha = (C.sha12(d / "p_w01_source.tif"), C.sha12(d / "p_w01_ref.tif"))
    base = {"src_sha12": sha[0], "ref_sha12": sha[1], "clicker": "t"}
    rows = [{**base, "point_id": "p001", "src_x": 10, "src_y": 10, "ref_x": 5, "ref_y": 5},
            {**base, "point_id": "p002", "src_x": 20, "src_y": 20, "ref_x": 10, "ref_y": 10},
            {**base, "point_id": "p003", "src_x": 11, "src_y": 10, "ref_x": 5, "ref_y": 6, "repeat_of": "p001"}]
    cp = _clicks(tmp_path, "p_w01", rows)
    c = C.load("p_w01", cp, tmp_path / "pairs")
    assert [r["point_id"] for r in c["icp"]] == ["p001", "p002"]
    p = C.precision(c["icp"], c["repeats"], ref_gsd=1.0, src_gsd=0.5)
    assert p["n"] == 1
    assert p["src_click_px"] == pytest.approx(1 / np.sqrt(2))
    assert p["ref_click_m"] == pytest.approx(1 / np.sqrt(2))


def test_clicks_made_on_other_files_are_refused(tmp_path):
    _pair(tmp_path)
    rows = [{"point_id": "p001", "src_x": 1, "src_y": 1, "ref_x": 1, "ref_y": 1,
             "src_sha12": "000000000000", "ref_sha12": "111111111111", "clicker": "t"}]
    cp = _clicks(tmp_path, "p_w01", rows)
    with pytest.raises(ValueError, match="other files"):
        C.load("p_w01", cp, tmp_path / "pairs")


def test_a_stale_bundle_is_refused(tmp_path):
    out = tmp_path / "out" / "p_w01"
    out.mkdir(parents=True)
    (out / "report.json").write_text(json.dumps({"git_commit": "old1234", "H_final": np.eye(3).tolist(),
                                                 "declared": {"method": "loftr+magsac++"}}), encoding="utf-8")
    log = tmp_path / "log.csv"
    log.write_text("pair_id,notes,git_commit\np_w01,,new5678\n", encoding="utf-8")
    with pytest.raises(ValueError, match="re-run"):
        C.bundle("p_w01", tmp_path / "out", log)
