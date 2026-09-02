import cv2
import numpy as np
import time


def run_akaze(img1, img2, ratio=0.75):
    """
    AKAZE + BFMatcher/Hamming baseline.

    Works with different OpenCV versions.

    Returns:
        src_pts: (N, 2) float32
        ref_pts: (N, 2) float32
        confidence: (N,) float32
        elapsed_seconds: float
    """

    start = time.perf_counter()

    # --------------------------------------------------------
    # Create AKAZE detector
    # --------------------------------------------------------
    if hasattr(cv2, "AKAZE_create"):
        akaze = cv2.AKAZE_create()

    elif hasattr(cv2, "xfeatures2d") and hasattr(
        cv2.xfeatures2d, "AKAZE_create"
    ):
        akaze = cv2.xfeatures2d.AKAZE_create()

    else:
        raise RuntimeError(
            "AKAZE is not available in this OpenCV installation."
        )

    # --------------------------------------------------------
    # Detect keypoints and descriptors
    # --------------------------------------------------------
    kp1, des1 = akaze.detectAndCompute(img1, None)
    kp2, des2 = akaze.detectAndCompute(img2, None)

    # --------------------------------------------------------
    # Handle blank / unusable images
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # AKAZE uses binary descriptors -> Hamming distance
    # --------------------------------------------------------
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    knn = bf.knnMatch(des1, des2, k=2)

    # --------------------------------------------------------
    # Lowe's ratio test
    # --------------------------------------------------------
    good = []

    for pair in knn:

        if len(pair) != 2:
            continue

        m, n = pair

        if m.distance < ratio * n.distance:
            good.append(m)

    # --------------------------------------------------------
    # Convert matches to point arrays
    # --------------------------------------------------------
    if not good:
        elapsed = time.perf_counter() - start

        return (
            np.zeros((0, 2), dtype=np.float32),
            np.zeros((0, 2), dtype=np.float32),
            np.zeros((0,), dtype=np.float32),
            elapsed,
        )

    src = np.float32(
        [kp1[m.queryIdx].pt for m in good]
    ).reshape(-1, 2)

    ref = np.float32(
        [kp2[m.trainIdx].pt for m in good]
    ).reshape(-1, 2)

    # --------------------------------------------------------
    # Match confidence
    # --------------------------------------------------------
    confidence = np.float32([
        1.0 / (1.0 + m.distance)
        for m in good
    ])

    elapsed = time.perf_counter() - start

    return src, ref, confidence, elapsed