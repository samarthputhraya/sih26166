"""The planted-error shapes of ops/trust_real_calibration.py.

Lives here because `ops/` is not in pytest's testpaths and these transforms decide numbers that
reach REPORT.md and the deck. A planted error that is not the shape the row claims would make the
whole calibration meaningless while every column still looked plausible.
"""
import numpy as np
import pytest

from ops.trust_real_calibration import KINDS, NON_TRANSLATION_M, cell_effect, plant

SHAPE = (640, 640)
CORNER_PX = float(np.hypot((SHAPE[1] - 1) / 2, (SHAPE[0] - 1) / 2))


def _corners(shape):
    h, w = shape
    return np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], float)


def _apply(H, p):
    q = np.c_[p, np.ones(len(p))] @ np.asarray(H, float).T
    return q[:, :2] / q[:, 2:3]


def test_zero_displacement_is_the_identity_for_every_kind():
    for kind in KINDS:
        assert np.allclose(plant(kind, 0.0, 0.0, SHAPE), np.eye(3))


@pytest.mark.parametrize("dpx", [1.0, 4.0, 16.0])
def test_translation_moves_every_point_by_exactly_the_displacement(dpx):
    H = plant("translation", dpx, 0.7, SHAPE)
    p = np.array([[0.0, 0.0], [320.0, 320.0], [639.0, 639.0], [100.0, 500.0]])
    d = np.hypot(*(_apply(H, p) - p).T)
    assert np.allclose(d, dpx, atol=1e-9), f"translation displaced points by {d}, not {dpx}"


@pytest.mark.parametrize("kind", ["rotation", "scale"])
@pytest.mark.parametrize("dpx", [1.0, 4.0, 16.0])
def test_rotation_and_scale_hold_the_centre_and_move_the_corners_by_the_displacement(kind, dpx):
    H = plant(kind, dpx, +1.0, SHAPE)
    centre = np.array([[(SHAPE[1] - 1) / 2, (SHAPE[0] - 1) / 2]])
    assert np.allclose(_apply(H, centre), centre, atol=1e-9), "the frame centre must not move"
    c = _corners(SHAPE)
    moved = np.hypot(*(_apply(H, c) - c).T)
    # a rotation moves a corner along an arc, so its chord is very slightly shorter than dpx
    assert np.allclose(moved, dpx, rtol=2e-3), f"{kind} moved the corners by {moved}, not {dpx}"


def test_a_scale_change_is_exactly_reversed_by_its_other_sign():
    c = _corners(SHAPE)
    a = _apply(plant("scale", 8.0, +1.0, SHAPE), c) - c
    b = _apply(plant("scale", 8.0, -1.0, SHAPE), c) - c
    assert np.allclose(a, -b, atol=1e-9), "a scale change about the centre is linear in its sign"


@pytest.mark.parametrize("dpx", [2.0, 8.0, 16.0])
def test_the_two_rotation_signs_cancel_to_the_second_order_term_and_no_more(dpx):
    """d(+t) + d(-t) = (R(t) + R(-t) - 2I) r = 2(cos t - 1) r, so the residue is |r| t^2 = dpx^2 / R
    for a corner at radius R. Asserting exactly that, rather than a loosened tolerance, is what
    makes this a check on the transform instead of a check on a fudge factor."""
    c = _corners(SHAPE)
    a = _apply(plant("rotation", dpx, +1.0, SHAPE), c) - c
    b = _apply(plant("rotation", dpx, -1.0, SHAPE), c) - c
    residue = float(np.hypot(*(a + b).T).max())
    assert residue == pytest.approx(dpx ** 2 / CORNER_PX, rel=1e-3)
    assert float(np.hypot(*a.T).max()) == pytest.approx(dpx, rel=1e-3)


@pytest.mark.parametrize("kind", ["rotation", "scale"])
def test_the_error_is_not_uniform_over_the_frame(kind):
    """The claim the REPORT table rests on: a rotation or scale error displaces the corner cells
    far more than the middle ones, which is why the frame verdict alone would miss it and the
    8x8 map is what carries the information."""
    from core.reliability import _true_error_grid
    te = _true_error_grid(SHAPE, plant(kind, 8.0, +1.0, SHAPE), np.eye(3), 8)
    assert te.max() > 5 * te.min(), f"{kind}: cell displacement spanned only {te.max() / te.min():.1f}x"
    assert te.max() <= 8.0 + 1e-6, "no cell may move further than the corners do"


def test_a_three_pixel_corner_error_splits_the_frame_into_moved_and_unmoved_cells():
    """At 3 px of corner displacement both classes the REPORT table counts are non-empty, so the
    percentages in it are computed over real populations and not over an empty set."""
    from core.reliability import VERIFIED
    state = np.full((8, 8), VERIFIED, dtype=object)
    e = cell_effect(SHAPE, plant("rotation", 3.0, +1.0, SHAPE), np.eye(3), state)
    assert e["cells_moved_2px"] > 0 and e["cells_under_1px"] > 0
    assert e["cells_moved_2px"] + e["cells_under_1px"] <= 64
    assert e["max_cell_displacement_px"] <= 3.0 + 1e-6
    # every cell is verified here, so the map refuses none of the moved ones
    assert e["moved_not_verified"] == 0 and e["under_1px_verified"] == e["cells_under_1px"]


def test_cell_effect_counts_a_refusal_when_the_map_does_not_verify_a_moved_cell():
    from core.reliability import VERIFIED, WEAK
    H = plant("scale", 12.0, +1.0, SHAPE)
    state = np.full((8, 8), VERIFIED, dtype=object)
    state[0, :] = WEAK                      # the top row is refused
    e = cell_effect(SHAPE, H, np.eye(3), state)
    assert 0 < e["moved_not_verified"] <= e["cells_moved_2px"]


def test_the_non_translation_sweep_starts_at_zero_so_a_false_alarm_rate_exists():
    assert NON_TRANSLATION_M[0] == 0.0 and len(NON_TRANSLATION_M) > 3


def test_an_unknown_kind_is_refused_rather_than_silently_planted():
    with pytest.raises(ValueError):
        plant("shear", 4.0, 1.0, SHAPE)
