import cv2
import numpy as np
import time


def run_akaze(img1, img2, ratio=0.75):
    """
    AKAZE + BFMatcher/Hamming baseline.

    Returns:
        src_pts: (N, 2) float32
        ref_pts: (N, 2) float32
        confidence: (N,) float32
        elapsed_seconds: float
    """

    start = time.perf_counter()

    akaze = cv2.AKAZE_create()

    kp1, des1 = akaze.detectAndCompute(img1, None)
    kp2, des2 = akaze.detectAndCompute(img2, None)

    if (
        des1 is None
        or des2 is None
        or len(kp1) < 2
        or len(kp2) < 2
    ):
        elapsed = time.perf_counter() - start

        return (
            np.zeros((0, 2), dtype=np.float32),
            np.zeros((0, 2), dtype=np.float32),
            np.zeros((0,), dtype=np.float32),
            elapsed,
        )

    # AKAZE default descriptor is binary.
    # Therefore use Hamming distance.
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    knn = bf.knnMatch(des1, des2, k=2)

    good = []

    for pair in knn:
        if len(pair) != 2:
            continue

        m, n = pair

        if m.distance < ratio * n.distance:
            good.append(m)

    src = np.float32(
        [kp1[m.queryIdx].pt for m in good]
    ).reshape(-1, 2)

    ref = np.float32(
        [kp2[m.trainIdx].pt for m in good]
    ).reshape(-1, 2)

    confidence = np.float32([
        1.0 / (1.0 + m.distance)
        for m in good
    ])

    elapsed = time.perf_counter() - start

    return src, ref, confidence, elapsed