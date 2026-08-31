"""
Outlier rejection with MAGSAC++.

    from core.ransac import filter_matches
    src_in, ref_in, H, mask = filter_matches(src_pts, ref_pts)

Locked decision (00_CANONICAL_FACTS.md Sec.6.3): `cv2.USAC_MAGSAC`, built into
OpenCV, nothing to install. **`pip install magsac` does not exist** - that claim
was in an earlier draft of our own docs and cost real time. If you ever need a
standalone binding it is `pymagsac`, but OpenCV's is fine and is what we use.

Measured against the installed opencv-contrib-python 5.0.0.93, because OpenCV 5
changed return arities elsewhere (`cv2.findContours` now returns 2, not 3) and
recalling an arity is exactly how this project has been bitten before:

    cv2.USAC_MAGSAC == 38
    cv2.findHomography(...) returns 2 values: (H, mask)
    H     -> (3, 3) float64
    mask  -> (N, 1) uint8      <-- NOT (N,). Ravel it before boolean indexing,
                                   or numpy broadcasts into an (N, N) selection
                                   and you silently get the wrong points.
    accepts (N,2) and (N,1,2); accepts float32 and float64

Failure modes, all measured rather than assumed:

    < 4 points   -> RAISES cv2.error
    exactly 4    -> returns a homography (no redundancy, so no error estimate)
    all points identical -> returns (None, None), does NOT raise
    all collinear        -> returns (None, None), does NOT raise

That asymmetry is the trap: two of the four degenerate cases raise and two
return None. Unattended runs - Gate 1, and Rohan's catalogue loop - must handle
both, so this module never propagates either. It returns an empty result with a
reason instead.

**The held-out split does NOT live here.** `evaluation/metrics.py :: evaluate()`
(Samrudh's, signature fixed in his guide) withholds 20% of matches, fits on the
rest, and reports `residual_px`. This module fits on everything, because its job
is the operational transform used to actually warp the image. Duplicating the
split here would create a second source of truth for the project's headline
accuracy number, which is precisely what Invariant 1 exists to prevent.
"""
from __future__ import annotations

import cv2
import numpy as np

# 3 px at the reference grid. Deliberately loose for a first pass: MAGSAC++
# weights points by how well they fit rather than applying a hard threshold, so
# an over-tight value here mostly discards usable geometry. Tune against
# results_log.csv, never by eye.
DEFAULT_THRESHOLD_PX = 3.0
DEFAULT_CONFIDENCE = 0.999
MIN_POINTS = 4


def filter_matches(src: np.ndarray, ref: np.ndarray,
                   threshold_px: float = DEFAULT_THRESHOLD_PX,
                   confidence: float = DEFAULT_CONFIDENCE,
                   method: int = cv2.USAC_MAGSAC):
    """Fit a homography and drop the outliers.

    Returns (src_inliers, ref_inliers, H, info) where H is (3,3) float64 or None
    and `info` carries n_input, n_inliers, inlier_ratio and a `note`.

    Never raises on degenerate input. An unattended pipeline that dies on one bad
    pair takes the whole catalogue run with it.
    """
    src = np.ascontiguousarray(np.asarray(src, dtype=np.float32).reshape(-1, 2))
    ref = np.ascontiguousarray(np.asarray(ref, dtype=np.float32).reshape(-1, 2))
    n = len(src)
    empty = (src[:0], ref[:0], None)

    if len(ref) != n:
        return (*empty, _info(n, 0, "src and ref have different lengths"))
    if n < MIN_POINTS:
        return (*empty, _info(n, 0, f"only {n} matches, need >= {MIN_POINTS}"))
    if not (np.isfinite(src).all() and np.isfinite(ref).all()):
        return (*empty, _info(n, 0, "non-finite coordinates in the matches"))

    try:
        H, mask = cv2.findHomography(src, ref, method=method,
                                     ransacReprojThreshold=threshold_px,
                                     confidence=confidence)
    except cv2.error as e:
        return (*empty, _info(n, 0, f"cv2.findHomography failed: {str(e)[:120]}"))

    if H is None or mask is None:
        return (*empty, _info(n, 0, "degenerate geometry (collinear or coincident "
                                    "points); no homography exists"))

    keep = mask.ravel().astype(bool)      # (N,1) -> (N,); see the module docstring
    k = int(keep.sum())
    if k < MIN_POINTS:
        return (*empty, _info(n, k, f"only {k} inliers survived at "
                                    f"{threshold_px} px"))
    return src[keep], ref[keep], H, _info(n, k, f"MAGSAC++ at {threshold_px} px")


def _info(n_input: int, n_inliers: int, note: str) -> dict:
    return {
        "n_input": n_input,
        "inlier_count": n_inliers,
        "inlier_ratio": (n_inliers / n_input) if n_input else 0.0,
        "threshold_px": DEFAULT_THRESHOLD_PX,
        "note": note,
    }


def warp(img: np.ndarray, H: np.ndarray, out_shape: tuple[int, int]) -> np.ndarray:
    """Warp `img` into the reference frame. out_shape is (height, width)."""
    h, w = out_shape
    return cv2.warpPerspective(np.ascontiguousarray(img, dtype=np.float32),
                               np.asarray(H, dtype=np.float64), (w, h),
                               flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                               borderValue=0.0)
