"""Tests for core/subpixel.py.

The test that matters is `test_recovers_a_known_fractional_shift`: build an image pair whose
true offset is a known fraction of a pixel, hand the refiner a deliberately ROUNDED
correspondence, and check it recovers the fraction. Everything else guards a way the module
could quietly do harm.

No LoFTR here - these run in milliseconds. The measurement on real lunar data lives in
core/bench_subpixel.py.
"""
import numpy as np
import cv2
import pytest

from core.subpixel import refine, metres, describe, PATCH


def _textured(n=256, seed=0):
    """Something with corners in it. Smooth blobs, so the correlation surface is smooth."""
    rng = np.random.default_rng(seed)
    img = np.zeros((n, n), np.float32)
    for _ in range(260):
        cv2.circle(img, (int(rng.integers(8, n - 8)), int(rng.integers(8, n - 8))),
                   int(rng.integers(2, 9)), float(rng.uniform(60, 255)), -1)
    return cv2.GaussianBlur(img, (5, 5), 1.1)


def _shifted(img, tx, ty):
    """`img` translated by (tx, ty). A feature at (x, y) moves to (x + tx, y + ty)."""
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]),
                          flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def _grid_points(n_img, step=24, margin=40):
    xs = np.arange(margin, n_img - margin, step)
    return np.array([(x, y) for y in xs for x in xs], np.float64)


@pytest.mark.parametrize("tx,ty", [(0.37, -0.62), (-0.25, 0.44), (0.5, 0.5), (0.0, 0.0)])
def test_recovers_a_known_fractional_shift(tx, ty):
    a = _textured()
    b = _shifted(a, tx, ty)

    src = _grid_points(a.shape[0])
    truth = src + np.array([tx, ty])
    # What the refiner is given: the correspondence rounded to whole pixels, i.e. the
    # fractional part deliberately thrown away. Recovering it is the whole job.
    ref_rounded = np.round(truth)

    src_out, ref_out, info = refine(src, ref_rounded, a, b)
    assert info["n_refined"] > 0.7 * len(src), f"only refined {info['n_refined']}/{len(src)}"

    m = info["refined"]
    err_before = np.linalg.norm(ref_rounded[m] - truth[m], axis=1)
    err_after = np.linalg.norm(ref_out[m] - truth[m], axis=1)

    # 0.30 px is where this method actually lands, measured across the shifts below -
    # NOT a threshold picked to make the test pass. Worst case is a true offset of
    # exactly half a pixel (peak-locking; see the module docstring), which measures
    # ~0.23 px. A tighter bound here would be a claim we cannot support.
    assert np.median(err_after) < 0.30, (
        f"median error after refinement {np.median(err_after):.3f} px "
        f"(before {np.median(err_before):.3f} px)"
    )
    # The zero-shift case starts perfect, so there is nothing to improve there.
    if (tx, ty) != (0.0, 0.0):
        assert np.median(err_after) < 0.5 * np.median(err_before), (
            "refinement must at least halve the rounding error to be worth its cost"
        )


def test_source_points_come_back_rounded():
    """Note 2 in the docstring: pairing a fractional source with a refined reference biases
    every downstream fit by up to half a pixel, invisibly."""
    a = _textured()
    b = _shifted(a, 0.3, -0.3)
    src = _grid_points(a.shape[0]) + 0.4          # deliberately fractional
    src_out, _, _ = refine(src, np.round(src + np.array([0.3, -0.3])), a, b)
    assert np.allclose(src_out, np.round(src)), "src_out must sit on the integer grid"


def test_rejected_matches_are_returned_unchanged_not_dropped():
    a = _textured()
    b = _shifted(a, 0.3, -0.3)
    src = _grid_points(a.shape[0])
    ref = np.round(src + np.array([0.3, -0.3]))
    src_out, ref_out, info = refine(src, ref, a, b)
    assert len(src_out) == len(ref_out) == len(src)
    not_refined = ~info["refined"]
    assert np.allclose(ref_out[not_refined], ref[not_refined]), \
        "a rejected match must not be moved"


def test_points_near_the_edge_are_rejected_not_clipped():
    a = _textured(n=64)
    b = _shifted(a, 0.3, -0.3)
    src = np.array([[2.0, 2.0], [61.0, 61.0], [32.0, 32.0]])
    ref = src.copy()
    _, _, info = refine(src, ref, a, b)
    assert info["reasons"]["edge"] >= 2, "the two corner points must be rejected"
    assert info["refined"][2], "the centre point should still refine"


def test_flat_image_refines_nothing():
    """No structure means no peak. It must decline, not invent an offset."""
    flat = np.full((128, 128), 50.0, np.float32)
    src = _grid_points(128, step=20, margin=30)
    _, ref_out, info = refine(src, src.copy(), flat, flat)
    assert info["n_refined"] == 0
    assert np.allclose(ref_out, src)


def test_length_mismatch_and_even_patch_raise():
    a = _textured(n=64)
    with pytest.raises(ValueError, match="differ in length"):
        refine(np.zeros((3, 2)), np.zeros((4, 2)), a, a)
    with pytest.raises(ValueError, match="odd"):
        refine(np.zeros((3, 2)), np.zeros((3, 2)), a, a, patch=10)


def test_patch_size_is_the_canonical_eleven():
    assert PATCH == 11, "Canonical Facts Sec.6.6 fixes the patch at 11x11"


def test_metres_names_the_grid_and_the_scale():
    # CH-2 OHRC: half a pixel is 11.5 cm. This is the project's headline conversion.
    assert metres(0.5, 0.22977) == pytest.approx(0.114885, abs=1e-6)
    # The same 0.5 px on Kaguya TC is 4.7 m - two very different claims.
    assert metres(0.5, 9.3698731836556) == pytest.approx(4.685, abs=1e-3)
    assert "cm" in describe(0.5, 0.22977, "CH-2 OHRC")
    assert "CH-2 OHRC" in describe(0.5, 0.22977, "CH-2 OHRC")
    assert "m" in describe(0.5, 9.3698731836556, "Kaguya TC")


@pytest.mark.parametrize("bad", [0, -1, None, float("nan")])
def test_metres_refuses_a_missing_scale(bad):
    """A sub-pixel claim without a real GSD is exactly the number we must never print."""
    with pytest.raises(ValueError):
        metres(0.5, bad)
