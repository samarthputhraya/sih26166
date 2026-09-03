import cv2
import numpy as np
import time


def run_sift(img1, img2, nfeatures=0, ratio=0.7):
    """
    SIFT + FLANN baseline.

    img1 = source image, uint8 grayscale
    img2 = reference image, uint8 grayscale

    Returns:
        src_pts: (N, 2) float32
        ref_pts: (N, 2) float32
        confidence: (N,) float32
        elapsed_seconds: float
    """

    start = time.perf_counter()

    sift = cv2.SIFT_create(nfeatures=nfeatures)

    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

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

    flann = cv2.FlannBasedMatcher(
        dict(algorithm=1, trees=5),
        dict(checks=50),
    )

    knn = flann.knnMatch(des1, des2, k=2)

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

    # Convert descriptor distance into a simple confidence score.
    confidence = np.float32([
        1.0 / (1.0 + m.distance)
        for m in good
    ])

    elapsed = time.perf_counter() - start

    return src, ref, confidence, elapsed