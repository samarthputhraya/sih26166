"""Deterministic test pair generator for Day 1 baseline verification.

Generates a textured grayscale image and a shifted version with known ground truth.
Depends on no external files and no teammates.
"""
import cv2
import numpy as np


def make_pair(dx: int = 7, dy: int = 5, seed: int = 0):
    """Create a deterministic textured base image and its shifted version.

    Args:
        dx: Horizontal shift in pixels (source moves right relative to reference)
        dy: Vertical shift in pixels (source moves down relative to reference)
        seed: Random seed for reproducibility

    Returns:
        (source, reference, H_true) where:
        - source, reference: uint8 grayscale arrays of shape (H, W)
        - H_true: (3, 3) float32 homography from source to reference coordinates
        Ground truth: src - ref = (dx, dy), so median(ref - src) = (-dx, -dy).
    """
    rng = np.random.default_rng(seed)
    img = np.full((480, 640), 40, np.uint8)
    for _ in range(300):
        cx, cy = int(rng.integers(30, 610)), int(rng.integers(30, 450))
        cv2.circle(img, (cx, cy), int(rng.integers(4, 18)),
                   int(rng.integers(90, 255)), -1)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    shifted = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

    # Homography from source to reference: ref = H_true @ src
    H_true = np.eye(3, dtype=np.float32)
    H_true[0, 2] = -dx  # source is shifted by +dx, so to go from src->ref we subtract dx
    H_true[1, 2] = -dy

    return shifted, img, H_true  # (source, reference, H_true)


if __name__ == "__main__":
    src, ref, H_true = make_pair()
    print(f"source shape: {src.shape}, dtype: {src.dtype}")
    print(f"reference shape: {ref.shape}, dtype: {ref.dtype}")
    print(f"H_true:\n{H_true}")
    cv2.imwrite("baselines/test_source.png", src)
    cv2.imwrite("baselines/test_ref.png", ref)
    print("Wrote baselines/test_source.png and baselines/test_ref.png")