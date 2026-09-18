"""MiLOI scoring without the data: sun geometry, the truth network, crops, outcomes.

The network is the part a judge will push on ("you made your own truth"), so it is tested
on offsets built from known per-image translations: it must recover them, and a pair that
is itself an edge must be scored against a solution that never saw it.
"""
import numpy as np
import pytest

from evaluation import miloi as M
from evaluation.real_eval import _apply, pixel_to_map

# Two map frames on one projection: 1.0 m and 1.5 m pixels, tie points 3 m apart.
T_SRC = (-500.0, 1.0, 0.0, 1000.0, 0.0, -1.0)
T_REF = (-497.0, 1.5, 0.0, 1000.0, 0.0, -1.5)


def test_azimuth_difference_is_circular():
    assert M.d_azimuth(350.0, 10.0) == pytest.approx(20.0)
    assert M.d_azimuth(10.0, 190.0) == pytest.approx(180.0)
    assert M.d_azimuth(90.0, 90.0) == 0.0


def test_sun_angle_matches_the_azimuth_gap_near_the_horizon_and_vanishes_overhead():
    assert M.sun_angle(90.0, 0.0, 90.0, 40.0) == pytest.approx(40.0)
    assert M.sun_angle(0.0, 0.0, 0.0, 170.0) == pytest.approx(0.0, abs=1e-9)
    assert M.sun_angle(7.4, 103.7, 15.8, 273.2) < 25.0      # MiLOI S2: opposite azimuths, ~23 deg apart


def test_map_truth_moves_the_same_ground_to_the_same_place():
    t_src, t_ref = (12.0, -7.0), (-3.0, 4.0)
    H = M.map_truth(T_SRC, T_REF, t_src, t_ref)
    x = np.array([[10.0, 20.0], [300.0, 150.0]])
    ground = _apply(pixel_to_map(T_SRC), x) + t_src
    np.testing.assert_allclose(_apply(pixel_to_map(T_REF), _apply(H, x)) + t_ref, ground, atol=1e-9)


def test_map_offset_reads_back_the_correction_and_nothing_else():
    H = M.map_truth(T_SRC, T_REF, (12.0, -7.0), (-3.0, 4.0))
    d, rest = M.map_offset(H, T_SRC, T_REF, (400, 400))
    np.testing.assert_allclose(d, [15.0, -11.0], atol=1e-6)
    assert rest < 1e-6


def _edges(t, pairs, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    return [{"pair_id": f"{a}_{b}", "src": a, "ref": b,
             "d_m": (np.subtract(t[a], t[b]) + rng.normal(0, noise, 2)).tolist()}
            for a, b in pairs]


def test_network_recovers_translations_up_to_the_component_mean():
    t = {"A": (10.0, 0.0), "B": (-5.0, 3.0), "C": (1.0, -8.0), "D": (0.0, 0.0)}
    edges = _edges(t, [("A", "B"), ("B", "C"), ("C", "A"), ("A", "D")])
    sol = M.solve(list(t), edges)
    for a, b in [("A", "C"), ("B", "D"), ("D", "C")]:
        np.testing.assert_allclose(sol[a][0] - sol[b][0], np.subtract(t[a], t[b]), atol=1e-9)
    assert len({v[1] for v in sol.values()}) == 1


def test_leave_one_out_never_uses_the_pair_being_scored():
    t = {"A": (10.0, 0.0), "B": (-5.0, 3.0), "C": (1.0, -8.0)}
    edges = _edges(t, [("A", "B"), ("B", "C"), ("C", "A")])
    edges[0]["d_m"] = [999.0, 999.0]                      # a wrong measurement on A-B
    loo = M.solve(list(t), edges, skip="A_B")
    np.testing.assert_allclose(loo["A"][0] - loo["B"][0], np.subtract(t["A"], t["B"]), atol=1e-9)


def test_an_image_reached_only_through_the_skipped_edge_has_no_truth():
    t = {"A": (0.0, 0.0), "B": (5.0, 5.0), "C": (9.0, 1.0)}
    edges = _edges(t, [("A", "B"), ("B", "C")])
    sol = M.solve(list(t), edges, skip="B_C")
    assert "C" not in sol
    sc = {"edges": edges, "images": {n: {"t_m": [0, 0], "component": 0} for n in t}}
    meta = {"scene": "S9", "pair_id": "B_C", "source": "B", "reference": "C",
            "src_transform": T_SRC, "ref_transform": T_REF}
    H, how = M.truth_for(meta, {"scenes": {"S9": sc}})
    assert H is None and how.startswith("no truth")


def test_disconnected_images_land_in_different_components():
    t = {"A": (0.0, 0.0), "B": (5.0, 5.0), "C": (9.0, 1.0), "D": (2.0, 2.0)}
    sol = M.solve(list(t), _edges(t, [("A", "B"), ("C", "D")]))
    assert sol["A"][1] == sol["B"][1] != sol["C"][1] == sol["D"][1]


def test_outcome_judges_the_matcher_against_truth():
    assert M.outcome(0.4, False) == "correct_accepted"
    assert M.outcome(0.4, True) == "false_alarm"
    assert M.outcome(40.0, True) == "caught_failure"
    assert M.outcome(40.0, False) == "missed_failure"
    assert M.outcome(None, True) == "no_transform"


def test_crop_moves_the_tie_point_by_exactly_the_window(tmp_path):
    tifffile = pytest.importorskip("tifffile")
    from core.io_loader import load
    img = np.arange(100 * 120, dtype=np.uint8).reshape(100, 120)
    src = tmp_path / "t.tif"
    tifffile.imwrite(str(src), img, extratags=[
        (33550, 12, 3, (1.5, 1.5, 0.0), True),
        (33922, 12, 6, (0.0, 0.0, 0.0, -500.0, 1000.0, 0.0), True),
        (34737, 2, 0, "Mercator MOON|", True)])
    out = tmp_path / "c.tif"
    M._write_crop(src, out, 30, 20, 40, 50)
    a, meta = load(out)
    np.testing.assert_array_equal(a, img[20:70, 30:70])
    assert meta["transform"][0] == pytest.approx(-500.0 + 30 * 1.5)
    assert meta["transform"][3] == pytest.approx(1000.0 - 20 * 1.5)
