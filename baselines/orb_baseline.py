"""ORB baseline for SIH26166.

Implements run_orb(img1, img2, nfeatures=5000) returning (src_pts, ref_pts)
as (N, 2) float32 arrays in (x, y) order.
Uses BFMatcher with NORM_HAMMING for binary descriptors.
"""
import cv2
import numpy as np

from baselines.sift_baseline import EMPTY, _to_points


def _run_binary(det, img1: np.ndarray, img2: np.ndarray, ratio: float = 0.75):
    """Internal runner for binary descriptor detectors (ORB, AKAZE)."""
    kp1, des1 = det.detectAndCompute(img1, None)
    kp2, des2 = det.detectAndCompute(img2, None)

    if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
        return EMPTY

    # Binary descriptors -> BFMatcher with Hamming distance
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    knn = bf.knnMatch(des1, des2, k=2)

    good = [p[0] for p in knn if len(p) == 2 and p[0].distance < ratio * p[1].distance]
    return _to_points(kp1, kp2, good) if good else EMPTY


def run_orb(img1: np.ndarray, img2: np.ndarray, nfeatures: int = 5000) -> tuple[np.ndarray, np.ndarray]:
    """Match ORB features between two grayscale images.

    Args:
        img1: Source image (uint8 grayscale, HxW)
        img2: Reference image (uint8 grayscale, HxW)
        nfeatures: Maximum number of features to retain

    Returns:
        (src_pts, ref_pts) each (N, 2) float32 in (x, y) order.
        Returns empty arrays on failure (no descriptors, too few keypoints).
    """
    return _run_binary(cv2.ORB_create(nfeatures=nfeatures), img1, img2)


if __name__ == "__main__":
    from baselines.make_test_pair import make_pair

    src, ref = make_pair(dx=7, dy=5, seed=0)
    src_pts, ref_pts = run_orb(src, ref)

    print(f"Matches: {len(src_pts)}")
    if len(src_pts) > 0:
        offset = np.median(ref_pts - src_pts, axis=0)
        print(f"Median ref - src: {offset}")
        expected = np.array([-7.0, -5.0])
        print(f"Expected: {expected}")
        print(f"Error: {np.abs(offset - expected)}")
        assert np.allclose(offset, expected, atol=0.5), "Shift recovery failed"
        print("ORB baseline: PASS")
    else:
        print("ORB baseline: NO MATCHES")