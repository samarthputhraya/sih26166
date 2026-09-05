"""
Sub-pixel refinement - NCC on an 11x11 patch per match, then a quadratic peak fit.

    from core.subpixel import refine
    src_out, ref_out, info = refine(src_pts, ref_pts, img_a, img_b)

Canonical Facts Sec.6.6 locks the method: *"NCC on an 11x11 patch per match +
quadratic peak fit."* This module is that sentence and nothing else.

WHY IT EXISTS
-------------
It is the project's headline claim. Sec.7 is explicit that an unqualified
"sub-pixel" is not an answer:

    "Sub-pixel means sub-pixel of WHICH image? Always the REFERENCE grid, and
     always report the metres equivalent alongside."

So this module refines the REFERENCE coordinates, and every number it produces
is in reference-image pixels. At Chandrayaan-2 OHRC's 0.22977 m/px, half a pixel
is 11.5 cm; `metres()` below does that conversion so nobody does it in their head
on stage.

HOW IT WORKS
------------
For each match we already have a rough correspondence. We cut an 11x11 patch
from the source around it, slide that patch over a small search window in the
reference, and take normalised cross-correlation at every integer offset. That
gives a (2S+1, 2S+1) correlation surface whose peak is the best integer
alignment. Real correlation surfaces are smooth near their peak, so we fit a
parabola through the peak and its two neighbours - separately in x and in y -
and take the vertex. The vertex lands between pixels. That is the sub-pixel part.

    y(x) = A x^2 + B x + C  through y(-1), y(0), y(+1)
    vertex at  x* = 0.5 * (y(-1) - y(+1)) / (y(-1) - 2 y(0) + y(+1))

HOW ACCURATE IT ACTUALLY IS, AND WHERE IT IS WORST
--------------------------------------------------
Measured against known fractional shifts on textured synthetic imagery
(`test_subpixel.py`), median endpoint error in reference pixels:

    true offset (0.10, 0.10)  ->  0.103 px
    true offset (0.25, 0.00)  ->  0.106 px
    true offset (-0.25, 0.44) ->  0.166 px
    true offset (0.37, -0.62) ->  0.174 px
    true offset (0.50, 0.50)  ->  0.235 px   <- worst case

Accuracy is worst at an offset of exactly half a pixel. That is **peak-locking**,
a known property of fitting a symmetric curve to a sampled correlation surface:
the estimate is pulled slightly toward the nearest integer, and half-way is
where that pull is largest. It is a property of the method, not a bug, and it
bounds what we may claim. Quote the worst case, not the best.

The literature's usual remedy is a Gaussian fit (the same parabola on the LOG of
the correlation values, since a correlation peak is closer to Gaussian than to
parabolic). **A/B'd, and it is within noise here** - better by ~0.01 px on three
shifts, worse by ~0.01 px on two. So Canonical Facts' parabola stands, now on
measurement rather than assumption. If someone asks why not Gaussian, that is
the answer, and it cost one experiment.

*** WHEN TO USE THIS AT ALL - AND WHEN NOT TO ***

`bench_subpixel.py` measures all four matchers against known fractional shifts on
real Chandrayaan-2 OHRC texture. Worst-case median endpoint error, in reference
pixels:

    matcher   raw    refined   refinement helped
    LoFTR    0.336    0.431    2 of 5 shifts
    SIFT     0.340    0.428    3 of 5
    ORB      0.722    0.437    5 of 5
    AKAZE    0.420    0.424    4 of 5

**The rule: NCC refinement converges on a floor of roughly 0.16-0.43 px whatever
it is handed. It helps a matcher that is WORSE than that floor and HURTS one that
is already better.**

LoFTR is already better ON THIS METRIC, and until 3 Sep 2026 that is why this
module shipped OFF. It also earns its place on Gate 1's fallback path (Sec.11:
*"drop LoFTR, ship classical + illumination normalisation + sub-pixel +
uniformity"*), where ORB goes from 0.722 px to 0.437 px - a 1.65x gain on the
matcher that needs it most.

*** IT NOW SHIPS ON. A SECOND MEASUREMENT REVERSED THE FIRST. ***

`pipeline.run_all(subpixel=True)` has been the default since 3 Sep 2026. Read
`core/pipeline.py::_refine_subpixel` for the full account; the short version is
that the two measurements are of DIFFERENT QUANTITIES and both are real:

- The table above is **per-match endpoint error** (`core/bench_subpixel_results.csv`,
  columns `median_err_raw_px` / `median_err_refined_px`). By it, refinement hurts
  LoFTR: 0.336 -> 0.431 px.
- **Transform-level `rmse_gt_px`** - the metric Gate 2 is actually judged on
  (Sec.11 C1), logged in `evaluation/results_log.csv`, medians over 5 off-grid
  shifts - improves at every sun difference: 0 deg 0.120 -> 0.086, 15 deg
  0.249 -> 0.086, 30 deg 0.571 -> 0.314, 45 deg 1.655 -> 1.096 px, and
  0.156 -> 0.024 px on real OHRC texture with a known half-pixel shift. The
  30 deg point moves from FAIL to PASS.

MAGSAC fits one transform through thousands of matches, so the fit can get more
accurate while the individual matches get noisier. Both arms are in the log:
`ours_loftr` (OFF) and `ours_loftr+subpixel` (ON). `--no-subpixel` reproduces the
old rows. **Every Gate 2 number was measured with refinement ON.**

Canonical Facts Sec.6.6 lists sub-pixel refinement as a locked step. It is built,
measured, and shipped. What the measurements changed is *when* it is switched on,
not whether it exists.

*** THE TRAP, WHICH POINTS THE OTHER WAY AND IS STILL A TRAP ***

Run the Gate-1 pair with refinement enabled and `residual_px` FALLS from 0.195 to
0.038 - a five-fold "improvement" on the number the pipeline prints. That fall is
NOT the reason the default changed, and it is not evidence of accuracy at all.

NCC pulls every match onto the same locally-correlating peak, so the matches agree
with each other far better than before - and `residual_px` measures exactly that
agreement. It does not measure truth; it cannot, because on a real pair there is
no truth to measure against. The default changed on `rmse_gt_px`, on synthetic
pairs where the transform IS known. Had we changed it on the residual we would
have been right by accident, which is the same as being wrong.

This is Sec.7's "the two accuracy numbers are NOT the same thing" arriving as a
concrete, reproducible trap rather than a caution. A step that makes points more
self-consistent while making them less correct will improve `residual_px` every
time. **Never accept a falling `residual_px` as evidence that accuracy improved.**

THREE THINGS THAT WILL CATCH YOU
--------------------------------
1. **Points are (x, y), not (row, col).** Same convention as `matcher.py`, and
   the same trap. Patch extraction indexes `img[y0:y1, x0:x1]`.

2. **We return the SOURCE points too, and they are not the ones you passed in.**
   The template is cut on an integer grid, so the refined reference position
   corresponds to the source point ROUNDED to whole pixels. Returning the
   original fractional source alongside a refined reference would pair two
   coordinates measured from different origins and bias every downstream fit by
   up to half a pixel - invisibly, and in the direction that flatters us.
   Use the `src_out` this function returns, not the `src_pts` you gave it.

3. **Feed it the same arrays the matcher saw.** NCC with `TM_CCOEFF_NORMED` is
   invariant to `I -> a*I + b` only for `a > 0`. Under a real sun-angle change
   shadows REVERSE, which is `a < 0`, and correlation goes to -1 rather than +1.
   Passing illumination-normalised images (what `pipeline.py` already holds at
   that point) keys the correlation on structure instead, where the sign problem
   does not arise. Passing raw DN across a sun-angle change will quietly refine
   toward the wrong peak.

WHAT IT REFUSES TO DO
---------------------
A refinement that cannot be trusted is worse than none, because it moves a point
and reports success. Every match is kept or rejected explicitly, and the mask
says which. Rejections: too close to an image edge to cut a patch, a correlation
peak on the border of the search surface (no neighbours to fit through), a flat
or degenerate parabola, a vertex further than one pixel from the integer peak,
or a peak correlation below `MIN_PEAK`. Rejected matches are returned UNCHANGED
(with the source rounded, per note 2) so the arrays stay the same length.
"""
from __future__ import annotations

import numpy as np
import cv2

# Canonical Facts Sec.6.6. Do not change these without changing that document.
PATCH = 11

# Half-width of the integer search, in reference pixels. The matcher is already
# accurate to a pixel or two; 3 covers that with room to spare and keeps the
# correlation surface at 7x7, which is cheap.
SEARCH = 3

# Below this peak correlation the surface is noise and its vertex is meaningless.
MIN_PEAK = 0.30

# A parabola vertex further than one pixel from the integer peak means the peak
# was not the peak. Reject rather than trust it.
MAX_SHIFT = 1.0

_DEGENERATE = 1e-12


def _as_float32(img: np.ndarray) -> np.ndarray:
    """cv2.matchTemplate wants float32 or uint8; float64 raises. Cast once, here."""
    a = np.asarray(img)
    return a.astype(np.float32) if a.dtype != np.float32 else a


def _parabola_vertex(left: float, centre: float, right: float) -> float | None:
    """Vertex of the parabola through (-1, left), (0, centre), (+1, right).

    Returns None when the three points are collinear or the curve opens upward
    (which would make the 'peak' a trough).
    """
    denom = left - 2.0 * centre + right
    if abs(denom) < _DEGENERATE or denom >= 0.0:
        return None
    return 0.5 * (left - right) / denom


def refine(src_pts: np.ndarray, ref_pts: np.ndarray,
           src_img: np.ndarray, ref_img: np.ndarray,
           patch: int = PATCH, search: int = SEARCH,
           min_peak: float = MIN_PEAK) -> tuple[np.ndarray, np.ndarray, dict]:
    """Refine reference coordinates to sub-pixel precision.

    Args:
        src_pts, ref_pts: (N, 2) float arrays of (x, y), same order.
        src_img, ref_img: 2-D arrays. Pass the SAME arrays the matcher saw -
            see note 3 in the module docstring.
        patch: NCC template size, odd. Canonical Facts fixes this at 11.
        search: half-width of the integer search window, in reference pixels.
        min_peak: reject refinements whose peak correlation is below this.

    Returns:
        (src_out, ref_out, info)
        src_out: (N, 2) float32, the source points rounded to the integer grid
            the templates were cut on. **Use these, not the inputs.**
        ref_out: (N, 2) float32, refined where possible, else unchanged.
        info: dict with `n_input`, `n_refined`, `refined` (bool mask),
            `median_shift_px`, `peak` (per-match correlation, NaN if rejected)
            and `reasons` (a count per rejection cause).
    """
    if patch % 2 == 0:
        raise ValueError(f"patch must be odd, got {patch}")

    src = np.asarray(src_pts, np.float64).reshape(-1, 2)
    ref = np.asarray(ref_pts, np.float64).reshape(-1, 2)
    if len(src) != len(ref):
        raise ValueError(f"src_pts and ref_pts differ in length: {len(src)} vs {len(ref)}")

    a = _as_float32(src_img)
    b = _as_float32(ref_img)
    ah, aw = a.shape[:2]
    bh, bw = b.shape[:2]

    half = patch // 2
    pad = half + search

    src_out = np.round(src).astype(np.float32)
    ref_out = ref.astype(np.float32).copy()
    refined = np.zeros(len(src), bool)
    peaks = np.full(len(src), np.nan, np.float32)
    reasons = {"edge": 0, "peak_on_border": 0, "degenerate": 0,
               "shift_too_large": 0, "weak_peak": 0}

    for i in range(len(src)):
        xs, ys = int(src_out[i, 0]), int(src_out[i, 1])
        xr, yr = int(round(ref[i, 0])), int(round(ref[i, 1]))

        # Template must fit in the source, search window must fit in the reference.
        if not (half <= xs < aw - half and half <= ys < ah - half):
            reasons["edge"] += 1
            continue
        if not (pad <= xr < bw - pad and pad <= yr < bh - pad):
            reasons["edge"] += 1
            continue

        template = a[ys - half:ys + half + 1, xs - half:xs + half + 1]
        window = b[yr - pad:yr + pad + 1, xr - pad:xr + pad + 1]

        # (2*search+1, 2*search+1). Index (py, px) means the template centre sits
        # at reference pixel (xr - search + px, yr - search + py).
        surface = cv2.matchTemplate(window, template, cv2.TM_CCOEFF_NORMED)

        py, px = np.unravel_index(int(np.argmax(surface)), surface.shape)
        peak = float(surface[py, px])
        peaks[i] = peak

        if peak < min_peak:
            reasons["weak_peak"] += 1
            continue
        # A peak on the border has no neighbour on one side to fit through, and
        # also means the true peak is probably outside the search window.
        if px == 0 or py == 0 or px == surface.shape[1] - 1 or py == surface.shape[0] - 1:
            reasons["peak_on_border"] += 1
            continue

        dx = _parabola_vertex(surface[py, px - 1], peak, surface[py, px + 1])
        dy = _parabola_vertex(surface[py - 1, px], peak, surface[py + 1, px])
        if dx is None or dy is None:
            reasons["degenerate"] += 1
            continue
        if abs(dx) > MAX_SHIFT or abs(dy) > MAX_SHIFT:
            reasons["shift_too_large"] += 1
            continue

        ref_out[i, 0] = xr - search + px + dx
        ref_out[i, 1] = yr - search + py + dy
        refined[i] = True

    moved = ref_out[refined] - ref[refined].astype(np.float32) if refined.any() else np.zeros((0, 2), np.float32)
    info = {
        "n_input": int(len(src)),
        "n_refined": int(refined.sum()),
        "refined": refined,
        "peak": peaks,
        "median_shift_px": float(np.median(np.linalg.norm(moved, axis=1))) if len(moved) else None,
        "reasons": reasons,
        "patch": patch,
        "search": search,
    }
    return src_out, ref_out, info


def metres(px: float, gsd_mpp: float) -> float:
    """Convert a reference-pixel figure to metres.

    Sec.7: a sub-pixel claim must name the grid AND give the metres equivalent.
    CH-2 OHRC is 0.22977 m/px, so half a pixel is 11.5 cm; Kaguya TC is 9.3699,
    where half a pixel is 4.7 m. The same '0.5 px' means two very different
    things, which is exactly why the number never travels alone.
    """
    if gsd_mpp is None or not np.isfinite(gsd_mpp) or gsd_mpp <= 0:
        raise ValueError("gsd_mpp must be a positive number - get it from the catalogue")
    return float(px) * float(gsd_mpp)


def describe(px: float, gsd_mpp: float, grid: str) -> str:
    """The one-line form a slide or a Q&A answer should use, never a bare number."""
    m = metres(px, gsd_mpp)
    scale = f"{m * 100:.1f} cm" if m < 1.0 else f"{m:.2f} m"
    return f"{px:.3f} px on the {grid} reference grid - about {scale}"
