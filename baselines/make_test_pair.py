"""Deterministic test pair generator for Day 1 baseline verification.

Generates a textured grayscale image and a transformed version with known ground truth.
Depends on no external files and no teammates.

Homography convention:
    H_true maps from SOURCE coordinates to REFERENCE coordinates.
    That is: ref_point = H_true @ src_point (in homogeneous coordinates).
    For a pure translation (dx, dy) where source is shifted right/down
    relative to reference: H_true = [[1, 0, -dx], [0, 1, -dy], [0, 0, 1]].
    This means median(ref_pts - src_pts) ≈ (-dx, -dy).
"""
import cv2
import numpy as np


def make_pair(dx: float = 7.0, dy: float = 5.0, angle_deg: float = 0.0,
              scale: float = 1.0, seed: int = 0):
    """Create a deterministic textured base image and its transformed version.

    Args:
        dx: Horizontal shift in pixels (source moves right relative to reference).
        dy: Vertical shift in pixels (source moves down relative to reference).
        angle_deg: Rotation angle in degrees (positive = counter-clockwise).
                   Source is rotated by this angle relative to reference.
        scale: Scale factor. Source is scaled by this factor relative to reference.
               scale > 1 means source is larger (zoomed in).
        seed: Random seed for reproducibility.

    Returns:
        (source, reference, H_true) where:
        - source, reference: uint8 grayscale arrays of shape (H, W)
        - H_true: (3, 3) float32 homography from source to reference coordinates.
                  ref_pt = H_true @ src_pt (homogeneous)
                  For pure translation: median(ref - src) ≈ (-dx, -dy).

    Coordinate convention:
        - OpenCV image coordinates: (x, y) = (col, row)
        - H_true transforms from source image coordinate frame to
          reference image coordinate frame.
        - Positive rotation = counter-clockwise in image coordinates
          (which appears clockwise visually since y increases downward).
    """
    rng = np.random.default_rng(seed)
    img = np.full((480, 640), 40, np.uint8)
    for _ in range(300):
        cx, cy = int(rng.integers(30, 610)), int(rng.integers(30, 450))
        cv2.circle(img, (cx, cy), int(rng.integers(4, 18)),
                   int(rng.integers(90, 255)), -1)
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # Build transformation: source = transform(reference)
    # We want to apply inverse transform to get source from reference.
    # H_true maps source -> reference.
    h, w = img.shape
    cx, cy = w / 2.0, h / 2.0

    # Translation to center
    T_center = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]], dtype=np.float32)
    # Rotation
    theta = np.deg2rad(angle_deg)
    R = np.array([[np.cos(theta), -np.sin(theta), 0],
                  [np.sin(theta),  np.cos(theta), 0],
                  [0, 0, 1]], dtype=np.float32)
    # Scale
    S = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]], dtype=np.float32)
    # Translation back + dx/dy
    T_back = np.array([[1, 0, cx + dx], [0, 1, cy + dy], [0, 0, 1]], dtype=np.float32)

    # Combined: M maps reference -> source
    M = T_back @ S @ R @ T_center
    # We need source = warpAffine(reference, M)
    # But we want to generate source from reference, so we use M directly
    # with warpAffine (which takes 2x3 matrix for inverse mapping)
    M_affine = M[:2, :].astype(np.float32)

    # Actually warpAffine does: dst = src(M^-1 @ pt)
    # So to get source from reference with transform M (ref->src), we use M
    source = cv2.warpAffine(img, M_affine, (w, h))
    reference = img

    # H_true maps source -> reference
    H_true = np.linalg.inv(M).astype(np.float32)

    return source, reference, H_true


if __name__ == "__main__":
    src, ref, H_true = make_pair()
    print(f"source shape: {src.shape}, dtype: {src.dtype}")
    print(f"reference shape: {ref.shape}, dtype: {ref.dtype}")
    print(f"H_true:\n{H_true}")
    cv2.imwrite("baselines/test_source.png", src)
    cv2.imwrite("baselines/test_ref.png", ref)
    print("Wrote baselines/test_source.png and baselines/test_ref.png")