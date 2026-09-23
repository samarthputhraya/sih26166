"""
Resample two images to a common ground sample distance.

    from core.scale import to_common_gsd
    a, b, gsd, factors = to_common_gsd(img_a, meta_a, img_b, meta_b)

This is a REQUIRED step, not an optimisation.
Our real GSD ratios are 18x (OHRC to TMC-2), 36x (OHRC to Kaguya TC) and 285x
(OHRC to IIRS). LoFTR is not reliably invariant past roughly 4-8x on its own, so
without this step the large-ratio pairs simply do not match, and that failure
looks like a matcher problem rather than a preprocessing one.

Three things here are not obvious.

1. THE RETURNED FACTORS ARE EFFECTIVE AND PER-AXIS, NOT THE NOMINAL GSD RATIO.
   The output size is an integer, so the realised scale is out_size/in_size,
   which is not exactly the ratio you asked for. Width and height round
   INDEPENDENTLY, so a single scalar factor is wrong on one axis. At the sizes
   this project actually handles that discrepancy is around 2 m on the ground -
   fatal for a claim measured in fractions of a pixel. Callers mapping a point
   back to the original must use these factors, not recompute the ratio.

2. DOWNSAMPLING USES INTER_AREA. Every other interpolator aliases when you
   shrink: INTER_LINEAR samples a handful of source pixels and ignores the rest,
   so fine lunar texture turns into moire that is not present in the scene, and
   the matcher then confidently matches artefacts. INTER_AREA integrates over
   the full source footprint, which is what averaging detector elements actually
   means. We upsample with INTER_CUBIC.

3. GSD IS OFTEN UNKNOWN, AND THAT IS NORMAL. An LROC NAC EDR label carries no
   map scale at all - verified on the real product M108587604RE. `io_loader`
   correctly reports gsd_mpp as None. You cannot resample to a common ground
   scale without knowing the ground scale, so this function does NOT invent one:
   it returns both images untouched with factors of 1.0 and a `note` saying why.
   The caller must read the note. Silently proceeding as though the scales
   matched is how an 18x pair gets reported as a matcher failure.
"""
from __future__ import annotations

import cv2
import numpy as np


def resample(img: np.ndarray, factor_x: float, factor_y: float) -> tuple[np.ndarray, tuple[float, float]]:
    """Resize by the given per-axis factors. Returns (image, EFFECTIVE factors).

    The effective factors are what actually happened after the output size was
    rounded to whole pixels, which is what a caller needs to map coordinates.
    """
    h, w = img.shape[:2]
    out_w = max(1, int(round(w * factor_x)))
    out_h = max(1, int(round(h * factor_y)))
    if (out_w, out_h) == (w, h):
        return img, (1.0, 1.0)
    # cv2.resize cannot handle int32/uint32/int64 at all; float32 is our contract
    # from io_loader anyway, but be explicit rather than failing deep in cv2.
    src = np.ascontiguousarray(img, dtype=np.float32)
    interp = cv2.INTER_AREA if (out_w < w or out_h < h) else cv2.INTER_CUBIC
    out = cv2.resize(src, (out_w, out_h), interpolation=interp)
    return out, (out_w / w, out_h / h)


def to_original(pts: np.ndarray, factors: tuple[float, float]) -> np.ndarray:
    """Map (N,2) (x, y) points from a resampled image back to the original.

    Pixel-centre convention: cv2.resize maps source centre (i+0.5)/f - 0.5 to
    destination index i, so the inverse is (x + 0.5)/f - 0.5. Dropping the half
    pixel introduces a systematic bias of up to half a pixel, which for a project
    whose headline claim is sub-pixel accuracy is the entire margin.
    """
    fx, fy = factors
    out = np.asarray(pts, dtype=np.float64).copy()
    out[:, 0] = (out[:, 0] + 0.5) / fx - 0.5
    out[:, 1] = (out[:, 1] + 0.5) / fy - 0.5
    return out


def to_common_gsd(img_a: np.ndarray, meta_a: dict, img_b: np.ndarray, meta_b: dict):
    """Resample both images to the COARSER of the two ground sample distances.

    Returns (a, b, gsd, factors) where `factors` is
        {"a": (fx, fy), "b": (fx, fy), "gsd_mpp": float | None, "note": str}

    Resampling to the coarser scale throws information away on purpose. The
    alternative - upsampling the coarse image - invents detail that the sensor
    never recorded, and the matcher would then match the interpolator's
    invention. Downsampling is the honest direction.
    """
    ga, gb = meta_a.get("gsd_mpp"), meta_b.get("gsd_mpp")
    one = (1.0, 1.0)

    if not ga or not gb or ga <= 0 or gb <= 0:
        missing = [n for n, g in (("source", ga), ("reference", gb)) if not g or g <= 0]
        return img_a, img_b, None, {
            "a": one, "b": one, "gsd_mpp": None,
            "note": f"gsd_mpp unknown for {' and '.join(missing)}; images NOT resampled. "
                    "A NAC EDR label carries no map scale - use a map-projected "
                    "product, or supply gsd_mpp from the catalogue.",
        }

    target = float(max(ga, gb))
    # Finer image shrinks by its_gsd/target (< 1); the coarser one is already there.
    a_out, fa = resample(img_a, ga / target, ga / target)
    b_out, fb = resample(img_b, gb / target, gb / target)
    return a_out, b_out, target, {
        "a": fa, "b": fb, "gsd_mpp": target,
        "note": f"resampled to the coarser gsd {target:.4g} m/px "
                f"(source {ga:.4g}, reference {gb:.4g}, ratio {max(ga,gb)/min(ga,gb):.2f}x)",
    }
