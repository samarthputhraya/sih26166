"""Pins the lighting convention of `render_shaded_relief`.

The bug this exists to prevent (live 30 Aug - 3 Sep 2026): the gradients from
`np.gradient` were unpacked in the wrong order, so the sun was reflected about the
image diagonal and every Tier D render was lit from the wrong side. A test on a
single round hill would have caught it on Day 1.
"""
import numpy as np
import pytest

from evaluation.shaded_relief import render_shaded_relief

N = 201
PX = 60.0


def _hill(sign=1.0):
    yy, xx = np.mgrid[0:N, 0:N]
    r = np.hypot(xx - N // 2, yy - N // 2)
    return sign * 500.0 * np.exp(-(r / 40.0) ** 2)


def _flanks(img, d=25):
    c = N // 2
    return {"top": float(img[c - d, c]), "bottom": float(img[c + d, c]),
            "left": float(img[c, c - d]), "right": float(img[c, c + d])}


@pytest.mark.parametrize("az,lit", [(0, "top"), (90, "right"), (180, "bottom"), (270, "left")])
def test_hill_is_lit_on_the_flank_facing_the_sun(az, lit):
    f = _flanks(render_shaded_relief(_hill(+1.0), az, 30.0, PX))
    assert max(f, key=f.get) == lit, f"sun from {az} deg lit the {max(f, key=f.get)} flank: {f}"


@pytest.mark.parametrize("az,lit", [(0, "bottom"), (90, "left"), (180, "top"), (270, "right")])
def test_crater_is_lit_on_the_far_wall(az, lit):
    f = _flanks(render_shaded_relief(_hill(-1.0), az, 30.0, PX))
    assert max(f, key=f.get) == lit, f"sun from {az} deg lit the {max(f, key=f.get)} wall: {f}"


def test_diagonal_sun_lights_the_diagonal_flank():
    img = render_shaded_relief(_hill(+1.0), 45.0, 30.0, PX)
    c, d = N // 2, 18
    ne, sw = img[c - d, c + d], img[c + d, c - d]
    nw, se = img[c - d, c - d], img[c + d, c + d]
    assert ne > nw > sw and ne > se > sw


def test_flat_ground_brightness_is_sin_elevation():
    flat = render_shaded_relief(np.zeros((32, 32)), 123.0, 30.0, PX)
    assert np.allclose(flat, 0.5, atol=1e-6)


def test_output_is_float32_in_unit_range():
    img = render_shaded_relief(_hill(), 284.901, 16.98, PX)
    assert img.dtype == np.float32 and img.min() >= 0.0 and img.max() <= 1.0


def test_rejects_bad_pixel_size():
    with pytest.raises(ValueError):
        render_shaded_relief(_hill(), 0.0, 30.0, 0.0)
