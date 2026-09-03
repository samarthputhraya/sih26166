"""The detector's answer must not depend on what the caller did to the pixels first.

This is the invariant that broke on Day 5 and was found in a browser: the Streamlit UI
passed percentile-stretched uint8 and got 183 candidates on pair_04_tierD_native, while
ops/gate_tier_d_changes.py passed raw float32 and got 1. Same detector, same pair.

The cause was worse than "different contrast". `detect_changes` scaled both images by
their COMBINED max, and on a multi-modal pair the reference peaks at 37488 DN while the
aligned optical image peaks at 2040. Dividing both by 37488 left the optical image with a
2nd-98th percentile range of [0, 5] - so nothing could differ by thresh=30, and the "1
candidate" was total contrast collapse rather than a conservative result.

Kept in its own file so it does not collide with the existing app/test_change_detection.py.
"""
import numpy as np
import pytest

from app.change_detection import detect_changes

GSD = 9.37


def _scene(seed=0, size=160):
    """A textured base image with one obvious bright square added in `b`."""
    rng = np.random.default_rng(seed)
    a = rng.normal(120, 25, (size, size)).clip(0, 255)
    b = a.copy()
    b[60:90, 60:90] = 250.0
    return a.astype(np.float32), b.astype(np.float32)


def _pct(img):
    a = np.asarray(img, np.float64)
    lo, hi = np.percentile(a, [2, 98])
    return np.clip((a - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)


def test_answer_is_identical_through_raw_float_and_prestretched_uint8():
    """The exact regression: two entry points, two preprocessings, one answer."""
    a, b = _scene()
    _, raw = detect_changes(a, b, GSD, thresh=30, min_area_px=50)
    _, pre = detect_changes(_pct(a), _pct(b), GSD, thresh=30, min_area_px=50)
    assert len(raw) == len(pre)


def test_a_uniform_gain_on_the_input_does_not_change_the_answer():
    """Scaling both images by a constant is a display choice, not a measurement."""
    a, b = _scene()
    _, base = detect_changes(a, b, GSD, thresh=30, min_area_px=50)
    _, gained = detect_changes(a * 7.5, b * 7.5, GSD, thresh=30, min_area_px=50)
    assert len(base) == len(gained)


def test_wildly_mismatched_dn_ranges_do_not_annihilate_the_darker_image():
    """The multi-modal case. Joint max-scaling used to return 0-1 candidates here.

    `b` carries the same structure as `a` plus a change, but on a scale 18x larger -
    which is what an optical image against an elevation hillshade actually looks like.
    """
    a, b = _scene()
    b_bright = b * 18.0
    _, changes = detect_changes(a, b_bright, GSD, thresh=30, min_area_px=50)
    assert len(changes) > 0, "the darker image was crushed to black again"


def test_the_planted_change_is_actually_found():
    """Guards against the opposite failure: a normalisation that finds nothing."""
    a, b = _scene()
    _, changes = detect_changes(a, b, GSD, thresh=30, min_area_px=50)
    assert len(changes) >= 1


def test_identical_images_report_no_change():
    a, _ = _scene()
    _, changes = detect_changes(a, a.copy(), GSD, thresh=30, min_area_px=50)
    assert len(changes) == 0


def test_a_flat_image_does_not_raise():
    """Percentile stretch on a constant image has hi == lo; it must degrade, not crash."""
    flat = np.full((120, 120), 42.0, np.float32)
    _, changes = detect_changes(flat, flat.copy(), GSD, thresh=30, min_area_px=50)
    assert changes == [] or len(changes) == 0


def test_grayscale_is_still_required():
    rgb = np.zeros((40, 40, 3), np.float32)
    with pytest.raises(ValueError):
        detect_changes(rgb, rgb.copy(), GSD)
