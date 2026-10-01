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


def _orbit_files(tmp_path, records):
    """A label and its .spm / .oat in PRADAN's layout: data/calibrated/<day>/ and miscellaneous/..."""
    d = tmp_path / "data" / "calibrated" / "20250612"
    m = tmp_path / "miscellaneous" / "calibrated" / "20250612"
    d.mkdir(parents=True)
    m.mkdir(parents=True)
    xml = d / "p.xml"
    xml.write_text("<start_date_time>2025-06-12T22:29:00.000Z</start_date_time>"
                   "<stop_date_time>2025-06-12T22:29:10.000Z</stop_date_time><elements>101</elements>",
                   encoding="latin1")
    spm, oat = [], []
    for k, (sec, az, el, s_lat, s_lon, alt) in enumerate(records):
        t = f"ORBTATTD {k + 1:5d} 2492025 6 12 22 29 {sec} 0"
        spm.append(f"{t} 1 2 3 0.1 0.2 0.3 60.0 105.6 {az} {el}")
        oat.append(f"{t} " + " ".join(["0"] * 18) + f" {s_lat} {s_lon} {az} {el} 0 0 0 0 0 0 0 {alt} 0 0 0 0 0")
    (m / "p.spm").write_text("\n".join(spm), encoding="latin1")
    (m / "p.oat").write_text("\n".join(oat), encoding="latin1")
    return xml


def test_spm_sun_and_oat_view_take_the_record_nearest_the_line(tmp_path):
    from ops.cut_chain_pairs import oat_view, spm_sun
    # t=0 s: Sun (200, 20); t=10 s: Sun (210, 40). Spacecraft 100 km straight above (10 N, 20 E).
    xml = _orbit_files(tmp_path, [(0, 200.0, 20.0, 10.0, 20.0, 100.0), (10, 210.0, 40.0, 10.0, 20.0, 100.0)])
    assert spm_sun(xml, 0) == (200.0, 20.0)
    assert spm_sun(xml, 100) == (210.0, 40.0)            # the last line is the stop time
    assert spm_sun(xml, 80) == (210.0, 40.0)             # 8 s: nearer the second record
    e, _, v = oat_view(xml, 0, 10.0, 20.0)
    assert e < 1e-6 and abs(np.linalg.norm(v) - 1) < 1e-12           # nadir
    # 1 deg of latitude south of the sub-spacecraft point: seen from the north, ~16 deg off vertical
    e, az, _ = oat_view(xml, 0, 9.0, 20.0)
    assert 15.0 < e < 18.0 and (az < 1.0 or az > 359.0)
