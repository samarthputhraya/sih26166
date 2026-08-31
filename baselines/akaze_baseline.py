"""AKAZE baseline for SIH26166.

Implements run_akaze(img1, img2) returning (src_pts, ref_pts)
as (N, 2) float32 arrays in (x, y) order.
Uses BFMatcher with NORM_HAMMING for binary descriptors.

IMPORTANT: In OpenCV 5.x, AKAZE moved to cv2.xfeatures2d.AKAZE_create().
Do NOT use cv2.AKAZE_create() - it raises AttributeError.

Ratio test threshold: 0.75 (standard for AKAZE with BFMatcher).
Same rationale as ORB: binary descriptors use Hamming distance,
which has a different distribution than SIFT's L2 distance.
The 0.75 threshold admits more matches but also more outliers,
leading to higher residual_px after RANSAC. This is expected.

Residual_px note: AKAZE typically shows higher residual_px than SIFT
on the synthetic test pair because the looser ratio test admits more
outliers that RANSAC must reject. The median offset remains accurate.
"""
import cv2
import numpy as np

from baselines.sift_baseline import EMPTY, _to_points


def _run_binary(det, img1: np.ndarray, img2: np.ndarray, ratio: float = 0.75):
    """Internal runner for binary descriptor detectors (ORB, AKAZE).

    Args:
        det: Feature detector (ORB or AKAZE)
        img1, img2: Grayscale images
        ratio: Lowe's ratio test threshold. Default 0.75 for binary
               descriptors (ORB, AKAZE). Higher than SIFT's 0.7 because
               Hamming distance distribution differs from L2.
    """
    kp1, des1 = det.detectAndCompute(img1, None)
    kp2, des2 = det.detectAndCompute(img2, None)

    if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
        return EMPTY

    # Binary descriptors -> BFMatcher with Hamming distance
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    knn = bf.knnMatch(des1, des2, k=2)

    good = [p[0] for p in knn if len(p) == 2 and p[0].distance < ratio * p[1].distance]
    return _to_points(kp1, kp2, good) if good else EMPTY


def run_akaze(img1: np.ndarray, img2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Match AKAZE features between two grayscale images.

    Args:
        img1: Source image (uint8 grayscale, HxW)
        img2: Reference image (uint8 grayscale, HxW)

    Returns:
        (src_pts, ref_pts) each (N, 2) float32 in (x, y) order.
        Returns empty arrays on failure (no descriptors, too few keypoints).
    """
    # OpenCV 5: AKAZE lives in xfeatures2d, NOT at cv2 top level.
    return _run_binary(cv2.xfeatures2d.AKAZE_create(), img1, img2)


if __name__ == "__main__":
    from baselines.make_test_pair import make_pair

    src, ref, H_true = make_pair(dx=7, dy=5, seed=0)
    src_pts, ref_pts = run_akaze(src, ref)

    print(f"Matches: {len(src_pts)}")
    if len(src_pts) > 0:
        offset = np.median(ref_pts - src_pts, axis=0)
        print(f"Median ref - src: {offset}")
        expected = np.array([-7.0, -5.0])
        print(f"Expected: {expected}")
        print(f"Error: {np.abs(offset - expected)}")
        assert np.allclose(offset, expected, atol=0.5), "Shift recovery failed"
        print("AKAZE baseline: PASS")
    else:
        print("AKAZE baseline: NO MATCHES")