"""
Tests for core/illumination.py.

No data files, no weights, no network - these run anywhere, including on a
teammate's machine that has never seen a lunar image.

The thresholds below were MEASURED on this venv (numpy 2.5.2), not estimated.
Both methods came back invariant to 1.7e-4 DN out of a 255 DN range, which is
float32 rounding rather than any real sensitivity. The assertions use 1e-3 - an
order of magnitude of headroom so they are not brittle across numpy versions,
still five orders below the signal.
"""
import numpy as np
import pytest

from core.illumination import (
    DEFAULT_METHOD,
    DN_MAX,
    METHODS,
    normalize,
)

ATOL_DN = 1e-3          # measured worst case 1.65e-4; see module docstring
ALL_METHODS = sorted(METHODS)


def _terrain(h=192, w=192, seed=0):
    """Something with edges in it. Pure noise has no structure to be invariant about."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    img = 120 + 60 * np.sin(xx / 9.0) * np.cos(yy / 11.0)
    img += 25 * rng.standard_normal((h, w))
    return np.clip(img, 0, 255).astype(np.float32)


@pytest.mark.parametrize("method", ALL_METHODS)
def test_output_is_dn_range_not_unit_range(method):
    """THE contract with core.matcher, and the one worth failing loudly over.

    matcher._to_tensor divides by 255 unconditionally. If normalize() is ever
    "tidied up" to return [0, 1], LoFTR silently returns zero matches and the
    failure reads as "illumination normalisation broke the matcher". This test
    is here so that edit fails in CI instead of at a demo.
    """
    out = normalize(_terrain(), method)
    assert out.dtype == np.float32
    assert 0.0 <= out.min() and out.max() <= DN_MAX
    # A unit-range return would put max at or below 1.0. Real structure maps
    # well above that, so this separates the two cases without a magic number.
    assert out.max() > 1.0, (
        f"{method} returned max={out.max()}, which looks like [0, 1]. "
        "core.matcher divides by 255 - see the illumination module docstring."
    )


@pytest.mark.parametrize("method", ALL_METHODS)
def test_shape_preserved(method):
    img = _terrain(h=64, w=97)          # deliberately not square, not a multiple of 8
    assert normalize(img, method).shape == img.shape


@pytest.mark.parametrize("method", ALL_METHODS)
def test_invariant_to_affine_intensity(method):
    """I -> a*I + b with a > 0: a brighter or hazier view of the same terrain."""
    img = _terrain()
    a = normalize(img, method)
    b = normalize(img * 1.7 + 35.0, method)
    assert np.abs(a - b).max() < ATOL_DN


@pytest.mark.parametrize("method", ALL_METHODS)
def test_invariant_to_contrast_reversal(method):
    """I -> -I: the sun crosses to the other side and every shadow flips.

    This is the case the whole module exists for. A method that fails this is
    not illumination-normalising anything.
    """
    img = _terrain()
    a = normalize(img, method)
    b = normalize(-img + 255.0, method)
    assert np.abs(a - b).max() < ATOL_DN


@pytest.mark.parametrize("method", ALL_METHODS)
def test_constant_image_is_finite(method):
    """Flat mare, or a tile that fell off the edge of the strip.

    There is no gradient and no phase to be congruent about, so the answer is
    undefined - but it must be a finite, uniform answer, not NaN. A NaN here
    propagates into LoFTR and takes out the whole match, not just this tile.
    """
    out = normalize(np.full((64, 64), 77.0, np.float32), method)
    assert np.isfinite(out).all()
    assert out.min() == out.max()


@pytest.mark.parametrize("method", ALL_METHODS)
def test_accepts_int_input(method):
    """io_loader returns raw DN, which for LROC NAC is an integer dtype."""
    img = _terrain().astype(np.uint8)
    out = normalize(img, method)
    assert out.dtype == np.float32
    assert np.isfinite(out).all()


def test_default_method_is_registered():
    assert DEFAULT_METHOD in METHODS


def test_unknown_method_raises():
    with pytest.raises(ValueError, match="unknown illumination method"):
        normalize(_terrain(), "sobel_but_vibes")


def test_rejects_non_2d():
    """A 3-band product reaching here means something upstream is wrong."""
    with pytest.raises(ValueError, match="2-D single-band"):
        normalize(np.zeros((16, 16, 3), np.float32))
