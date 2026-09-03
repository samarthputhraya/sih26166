"""Pins the one conversion in the sweep whose failure mode is SILENT.

`_synthetic_pair` writes float32 DN in [0, 255]. SIFT/ORB/AKAZE want uint8. Handing them
the float array raises nothing and returns near-zero keypoints, which would have shown up
as a flattering "classical fails completely" at every sun angle - including the two where
classical actually beats or nearly matches us. That is the difference between a comparison
and a rigged one, so it gets a test.
"""
import numpy as np
import pytest

from baselines.sweep_baselines import build_parser, u8


def test_u8_preserves_dn_range_and_dtype():
    src = np.array([[0.0, 127.4, 255.0]], dtype=np.float32)
    out = u8(src)
    assert out.dtype == np.uint8
    np.testing.assert_array_equal(out, np.array([[0, 127, 255]], dtype=np.uint8))


def test_u8_clips_instead_of_wrapping():
    """Wrapping is the dangerous failure: 260 -> 4 would put bright terrain at black."""
    out = u8(np.array([[-40.0, 260.0]], dtype=np.float32))
    np.testing.assert_array_equal(out, np.array([[0, 255]], dtype=np.uint8))


def test_u8_does_not_rescale_a_01_image():
    """A [0,1] array must stay dark, not be silently stretched.

    If this ever "helpfully" rescaled, a caller passing the wrong range would get
    plausible numbers from the wrong pixels - the exact class of bug this file exists for.
    """
    out = u8(np.full((4, 4), 0.5, dtype=np.float32))
    assert out.max() == 0


def test_parser_requires_dem_and_pixel_size():
    p = build_parser()
    with pytest.raises(SystemExit):
        p.parse_args([])
    args = p.parse_args(["--dem", "d.npy", "--pixel-size", "60"])
    assert args.sweep == "0,15,30,45" and args.repeats == 5 and args.max_size == 640


def test_parser_sweep_parses_to_the_deltas_we_ran():
    args = build_parser().parse_args(
        ["--dem", "d.npy", "--pixel-size", "60", "--sweep", "0,15,30,45,60,90,120,180"])
    assert [float(d) for d in args.sweep.split(",")] == [0, 15, 30, 45, 60, 90, 120, 180]
