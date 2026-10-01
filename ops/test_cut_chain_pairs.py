"""The ladder/site window rule and the three-leg loop over _cNN ids - pinned on synthetic geometry."""
import json

import numpy as np

from core.geometry import Frame
from ops.cut_chain_pairs import LADDER_STEP, _block_reader, ladder_candidates


def _frame(rows=1000, cols=100, gsd=10.0):
    # map = (gsd * x, -gsd * y): a north-up strip 1 km wide and 10 km long
    xs, ys = np.array([0.0, cols - 1.0]), np.array([0.0, rows - 1.0])
    X = np.array([[0.0, gsd * (cols - 1)]] * 2)
    Y = np.array([[0.0, 0.0], [-gsd * (rows - 1)] * 2])
    return Frame("strip", (rows, cols), xs, ys, X, Y, source="synthetic")


def test_ladder_candidates_sit_on_the_centre_line_one_step_apart_and_clear_of_the_ends():
    f = _frame()
    window_m = 1120.0
    c = ladder_candidates(f, window_m)
    assert len(c) >= 2
    assert np.allclose(c[:, 0], 500.0)                       # the centre column, x = 10 m * 50
    gaps = -np.diff(c[:, 1])
    assert np.all(gaps > 0) and np.allclose(gaps, gaps[0])   # evenly spaced, top to bottom
    assert gaps[0] >= LADDER_STEP * window_m - 1e-6          # never closer than the step
    length = 10.0 * 999
    assert c[0, 1] <= -(window_m / 2) and c[-1, 1] >= -(length - window_m / 2)   # windows stay inside


def test_ladder_candidates_depend_on_the_frame_alone():
    f = _frame()
    assert np.array_equal(ladder_candidates(f, 800.0), ladder_candidates(f, 800.0))


def test_block_reader_area_averages_and_is_a_no_op_at_one():
    full = np.arange(64, dtype=np.float32).reshape(8, 8)
    read = lambda x, y, w, h: full[y:y + h, x:x + w]  # noqa: E731
    assert _block_reader(read, 1) is read
    r2 = _block_reader(read, 2)
    out = r2(0, 0, 2, 2)                                     # pixels (0..3, 0..3) in 2x2 blocks
    assert out.shape == (2, 2)
    assert out[0, 0] == np.mean(full[0:2, 0:2]) and out[1, 1] == np.mean(full[2:4, 2:4])


def _pair(root, out, pid, H, src_tr, ref_tr, gsd, inliers=None):
    d = root / "data" / "pairs" / pid
    d.mkdir(parents=True)
    (d / "geometry_prior.json").write_text(json.dumps({
        "source": {"transform": src_tr, "product_id": "src"},
        "reference": {"transform": ref_tr, "product_id": "ref", "resampled_gsd_mpp": gsd},
        "window_centre_latlon": [0.0, 0.0]}), encoding="utf-8")
    o = out / pid
    o.mkdir(parents=True)
    (o / "report.json").write_text(json.dumps({"H_final": H, "declared": {"method": "loftr+magsac++"},
                                               "trust": {"verdict": "agrees"}}), encoding="utf-8")
    if inliers is not None:
        lines = ["src_x,src_y,is_inlier"] + [f"{x},{y},1" for x, y in inliers]
        (o / "matches.csv").write_text("\n".join(lines), encoding="utf-8")


def test_three_legs_on_cnn_ids_close_to_zero_when_they_agree(tmp_path, monkeypatch):
    import ops.loop_closure as L
    monkeypatch.setattr(L, "ROOT", tmp_path)
    out = tmp_path / "out"
    I = np.eye(3).tolist()
    # one map grid for all three images: pixel (x, y) -> map (x, -y) metres; identity registrations
    tr = [0.0, 1.0, 0.0, 0.0, 0.0, -1.0]
    pts = [(x, y) for x in range(10, 100, 15) for y in range(10, 100, 15)]
    _pair(tmp_path, out, "oa_c03", I, tr, tr, 1.0, inliers=pts)
    _pair(tmp_path, out, "ab_c03", I, tr, tr, 1.0)
    _pair(tmp_path, out, "ob_tmc2020_c03", I, tr, tr, 1.0)
    res = L.run(legs=("oa", "ab", "ob_tmc2020"), out_root=out)
    good = [r for r in res if r.get("ok")]
    assert [r["k"] for r in good] == [3]
    assert good[0]["rms_m"] < 1e-9


def test_three_legs_report_a_planted_one_metre_inconsistency(tmp_path, monkeypatch):
    import ops.loop_closure as L
    monkeypatch.setattr(L, "ROOT", tmp_path)
    out = tmp_path / "out"
    I = np.eye(3).tolist()
    shifted = [[1.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]      # 1 px = 1 m east on the direct leg
    tr = [0.0, 1.0, 0.0, 0.0, 0.0, -1.0]
    pts = [(x, y) for x in range(10, 100, 15) for y in range(10, 100, 15)]
    _pair(tmp_path, out, "oa_c01", I, tr, tr, 1.0, inliers=pts)
    _pair(tmp_path, out, "ab_c01", I, tr, tr, 1.0)
    _pair(tmp_path, out, "ob_tmc2020_c01", shifted, tr, tr, 1.0)
    good = [r for r in L.run(legs=("oa", "ab", "ob_tmc2020"), out_root=out) if r.get("ok")]
    assert abs(good[0]["rms_m"] - 1.0) < 1e-9
