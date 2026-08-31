"""SIFT baseline for SIH26166.

Implements run_sift(img1, img2, nfeatures=0) returning (src_pts, ref_pts)
as (N, 2) float32 arrays in (x, y) order.

Ratio test threshold: 0.7 (Lowe's ratio test for SIFT).
This is the standard threshold for SIFT with FLANN matcher.
Lower = stricter matching, fewer outliers, fewer total matches.
"""
import cv2
import numpy as np

EMPTY = (np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32))


def _to_points(kp1, kp2, good):
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 2)
    ref = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 2)
    return src, ref


def run_sift(img1: np.ndarray, img2: np.ndarray, nfeatures: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Match SIFT features between two grayscale images.

    Args:
        img1: Source image (uint8 grayscale, HxW)
        img2: Reference image (uint8 grayscale, HxW)
        nfeatures: Maximum number of features to retain (0 = unlimited)

    Returns:
        (src_pts, ref_pts) each (N, 2) float32 in (x, y) order.
        Returns empty arrays on failure (no descriptors, too few keypoints).
    """
    sift = cv2.SIFT_create(nfeatures=nfeatures)
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
        return EMPTY

    # SIFT descriptors are float32 -> FLANN KD-tree is correct here.
    flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    knn = flann.knnMatch(des1, des2, k=2)

    # Lowe's ratio test: 0.7 is standard for SIFT
    good = [p[0] for p in knn if len(p) == 2 and p[0].distance < 0.7 * p[1].distance]
    return _to_points(kp1, kp2, good) if good else EMPTY


if __name__ == "__main__":
    from baselines.make_test_pair import make_pair

    src, ref, H_true = make_pair(dx=7, dy=5, seed=0)
    src_pts, ref_pts = run_sift(src, ref)

    print(f"Matches: {len(src_pts)}")
    if len(src_pts) > 0:
        offset = np.median(ref_pts - src_pts, axis=0)
        print(f"Median ref - src: {offset}")
        expected = np.array([-7.0, -5.0])
        print(f"Expected: {expected}")
        print(f"Error: {np.abs(offset - expected)}")
        assert np.allclose(offset, expected, atol=0.5), "Shift recovery failed"
        print("SIFT baseline: PASS")
    else:
        print("SIFT baseline: NO MATCHES")