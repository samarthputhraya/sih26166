"""Tests for core/distribution.py.

Two things these guard above all:
  - the grid is Samrudh's, imported, never redefined here;
  - `redetect` maps its local matches back into full-image coordinates correctly,
    because an off-by-one there produces plausible-looking points in the wrong place.

`match_fn` is injected throughout, so none of this needs LoFTR.
"""
import numpy as np
import pytest

from core.distribution import (GRID, MIN_PER_CELL, cell_index, counts, weak_cells,
                               cell_bounds, redetect, summary)

SHAPE = (640, 640)


def test_grid_is_the_one_from_evaluation_not_a_local_copy():
    from evaluation.metrics import GRID as OWNER_GRID
    assert GRID is OWNER_GRID or GRID == OWNER_GRID
    assert GRID == 8, "Canonical Facts Sec.6.7 fixes the grid at 8x8"


def test_cell_index_uses_xy_order_and_row_zero_is_the_top():
    # (x=10, y=10) is top-left; (x=630, y=10) is TOP-RIGHT -> row 0, last column.
    idx = cell_index(np.array([[10.0, 10.0], [630.0, 10.0], [10.0, 630.0]]), SHAPE)
    assert tuple(idx[0]) == (0, 0)
    assert tuple(idx[1]) == (0, GRID - 1), "x must drive the COLUMN, not the row"
    assert tuple(idx[2]) == (GRID - 1, 0)


def test_points_on_the_far_edge_do_not_fall_off_the_grid():
    idx = cell_index(np.array([[640.0, 640.0], [639.9, 639.9]]), SHAPE)
    assert (idx == GRID - 1).all()


def test_counts_total_matches_the_input():
    rng = np.random.default_rng(0)
    pts = rng.random((500, 2)) * 640
    c = counts(pts, SHAPE)
    assert c.sum() == 500
    assert c.shape == (GRID, GRID)


def test_counts_of_nothing_is_all_zeros():
    c = counts(np.zeros((0, 2)), SHAPE)
    assert c.shape == (GRID, GRID) and c.sum() == 0


def test_weak_cells_finds_the_gaps_emptiest_first():
    c = np.full((GRID, GRID), 5, int)
    c[3, 4] = 0
    c[1, 1] = 1
    weak = weak_cells(c)
    assert weak[0] == (3, 4), "the empty cell must come before the sparse one"
    assert set(weak) == {(3, 4), (1, 1)}


def test_a_cell_with_exactly_the_minimum_is_not_weak():
    c = np.full((GRID, GRID), MIN_PER_CELL, int)
    assert weak_cells(c) == []
    c[0, 0] = MIN_PER_CELL - 1
    assert weak_cells(c) == [(0, 0)]


def test_clustered_matches_leave_most_cells_weak():
    """The failure this module exists for: everything in one corner."""
    rng = np.random.default_rng(1)
    pts = rng.random((300, 2)) * 60          # all inside the top-left cell
    s = summary(pts, SHAPE)
    assert s["n_empty"] == GRID * GRID - 1
    assert s["busiest_cell"] == (0, 0)
    assert s["max_in_one_cell"] == 300


def test_cell_bounds_are_clipped_and_overlap_by_the_margin():
    x0, y0, x1, y1 = cell_bounds((0, 0), SHAPE)
    assert (x0, y0) == (0, 0), "margin must not push the box off the image"
    mid = cell_bounds((4, 4), SHAPE)
    assert mid[2] - mid[0] > 640 / GRID, "interior cells should be widened by the margin"


def test_summary_refuses_to_report_the_owned_metrics():
    """Coverage and CV belong to evaluation/metrics.py. A second implementation here
    would give the project two answers for one Gate 2 criterion."""
    s = summary(np.zeros((0, 2)), SHAPE)
    assert "grid_coverage_fraction" not in s
    assert "distribution_cv" not in s


# --- redetect ---------------------------------------------------------------

def _identity_H():
    return np.eye(3, dtype=np.float64)


def test_redetect_maps_local_matches_back_to_full_image_coordinates():
    """The off-by-one that matters: points must come back in whole-image pixels."""
    src = np.zeros((640, 640), np.uint8)
    ref = np.zeros((640, 640), np.uint8)
    seen = {}

    def fake_match(a, b):
        seen["shape"] = a.shape
        # one match at the centre of whatever crop it was handed
        c = np.array([[b.shape[1] / 2, b.shape[0] / 2]], np.float32)
        return c.copy(), c.copy()

    cell = (4, 4)
    s_new, r_new, info = redetect(src, ref, _identity_H(), [cell], match_fn=fake_match)

    assert info["succeeded"] == 1 and info["added"] == 1
    x0, y0, x1, y1 = cell_bounds(cell, ref.shape)
    assert r_new[0, 0] == pytest.approx(x0 + (x1 - x0) / 2)
    assert r_new[0, 1] == pytest.approx(y0 + (y1 - y0) / 2)
    # and the point must land inside the cell it was asked about
    assert tuple(cell_index(r_new, ref.shape)[0]) == cell


def test_redetect_without_a_transform_returns_empty_not_garbage():
    src = ref = np.zeros((640, 640), np.uint8)
    s, r, info = redetect(src, ref, None, [(0, 0)], match_fn=lambda a, b: (None, None))
    assert len(s) == len(r) == 0
    assert "no transform" in info["note"]


def test_redetect_survives_a_singular_transform():
    src = ref = np.zeros((640, 640), np.uint8)
    s, r, info = redetect(src, ref, np.zeros((3, 3)), [(0, 0)], match_fn=lambda a, b: (None, None))
    assert len(s) == 0 and "singular" in info["note"]


def test_one_bad_cell_does_not_abort_the_rest():
    src = ref = np.zeros((640, 640), np.uint8)
    calls = {"n": 0}

    def flaky(a, b):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("matcher blew up on this crop")
        c = np.array([[4.0, 4.0]], np.float32)
        return c.copy(), c.copy()

    s, r, info = redetect(src, ref, _identity_H(), [(0, 0), (1, 1), (2, 2)], match_fn=flaky)
    assert info["attempted"] == 3
    assert info["succeeded"] == 2, "a crash in one cell must not lose the others"


def test_max_cells_caps_the_work():
    src = ref = np.zeros((640, 640), np.uint8)
    c = np.array([[4.0, 4.0]], np.float32)
    _, _, info = redetect(src, ref, _identity_H(), [(i, i) for i in range(GRID)],
                          match_fn=lambda a, b: (c.copy(), c.copy()), max_cells=3)
    assert info["attempted"] == 3


def test_redetect_skips_cells_that_project_outside_the_source():
    """A far-off transform must yield nothing rather than clamp to a wrong crop."""
    src = ref = np.zeros((640, 640), np.uint8)
    H = np.array([[1, 0, 100000.0], [0, 1, 100000.0], [0, 0, 1]])
    c = np.array([[4.0, 4.0]], np.float32)
    _, _, info = redetect(src, ref, H, [(0, 0), (4, 4)],
                          match_fn=lambda a, b: (c.copy(), c.copy()))
    assert info["attempted"] == 0 and info["added"] == 0
