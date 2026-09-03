import numpy as np
import pytest

from baselines.make_test_pair import make_pair
from baselines.sift_baseline import run_sift
from baselines.orb_baseline import run_orb
from baselines.akaze_baseline import run_akaze


def get_points(result):
    """Extract source and reference points from a baseline result."""
    return result[0], result[1]


@pytest.mark.parametrize(
    "name, fn",
    [
        ("sift", run_sift),
        ("orb", run_orb),
        ("akaze", run_akaze),
    ],
)
def test_recovers_known_shift(name, fn):
    src, ref, h_true = make_pair(dx=7, dy=5, seed=0)

    result = fn(src, ref)
    src_pts, ref_pts = get_points(result)

    assert len(src_pts) > 20, (
        f"{name} found too few matches on an easy synthetic pair"
    )

    offset = np.median(ref_pts - src_pts, axis=0)

    assert np.allclose(
        offset,
        [-7.0, -5.0],
        atol=0.5,
    ), (
        f"{name} recovered offset {offset}, "
        "expected approximately [-7, -5]"
    )


@pytest.mark.parametrize(
    "name, fn",
    [
        ("sift", run_sift),
        ("orb", run_orb),
        ("akaze", run_akaze),
    ],
)
def test_blank_images_do_not_crash(name, fn):
    blank = np.zeros((100, 100), np.uint8)

    result = fn(blank, blank)
    src_pts, ref_pts = get_points(result)

    assert len(src_pts) == 0
    assert len(ref_pts) == 0