"""
Match distribution - finding the empty parts of the frame, and filling them.

    from core.distribution import counts, weak_cells, redetect

    c = counts(ref_pts, ref_img.shape)          # 8x8 matches-per-cell
    weak = weak_cells(c)                        # cells with fewer than 2
    extra_src, extra_ref = redetect(a, b, H, weak, a.shape, b.shape)

Canonical Facts Sec.6.7: *"Uniform distribution: 8x8 grid, min 2 matches/cell,
re-detect in empty cells."*

WHY THIS IS A SEPARATE MODULE FROM THE METRIC
---------------------------------------------
`evaluation/metrics.py :: evaluate()` already reports `grid_coverage_fraction`
and `distribution_cv`. **It MEASURES distribution. This module IMPROVES it.**
Those are different jobs and they must not share an owner, because a module that
both improves a number and reports it can always make itself look good.

So this module never computes a metric anyone quotes. It answers one question -
*which cells are short of matches* - and then goes and looks there again. The
scoring stays in Samrudh's file, on his schema, and Gate 2's
`grid_coverage_fraction >= 0.80` is judged by his code, not ours.

*** THE GRID IS IMPORTED, NEVER REDEFINED ***

`GRID` comes from `evaluation.metrics`. If we wrote `GRID = 8` here as well, the
two could drift and every coverage number in the project would quietly depend on
which module you asked. That is the same class of failure as the invented
"0.7 px" - two sources of truth for one figure. One definition, imported.

WHY UNIFORMITY IS A SCORED CRITERION AT ALL
-------------------------------------------
Matches clustered in one bright, high-contrast corner can fit a transform that
looks excellent by residual and is wrong everywhere else in the frame. A crater
rim gives a hundred matches within a few hundred pixels; the featureless mare
next to it gives none. The fit then honours the rim and drifts across the plain,
and no intensity statistic complains. Spreading the matches is what makes the
transform hold across the whole image, which is why Sec.7 scores it and why
Gate 2 sets a floor on it.

WHAT RE-DETECTION NEEDS, AND WHY IT NEEDS IT
--------------------------------------------
To look again inside an empty reference cell we must know where that ground is in
the SOURCE image, and only the current transform `H` can tell us. So `redetect`
takes `H` and is honest that its output is conditional on it: if `H` is badly
wrong the crops will not correspond and the new matches will be junk. They still
pass through RANSAC afterwards, which is the safety net - but do not run this
before you have a transform worth trusting.
"""
from __future__ import annotations

import numpy as np
import cv2

# ONE definition of the grid, imported from the module that owns the metric.
# See "THE GRID IS IMPORTED, NEVER REDEFINED" above before touching this.
try:
    from evaluation.metrics import GRID
except ImportError:  # pragma: no cover - evaluation/ is Samrudh's, may lag
    raise ImportError(
        "core/distribution.py needs GRID from evaluation/metrics.py, which owns the "
        "8x8 definition. Do not define a local GRID to work around this - two grids "
        "means two different coverage numbers depending on who you ask."
    )

# Sec.6.7. A cell with one match constrains nothing locally; two is the minimum
# that says anything about whether the transform holds there.
MIN_PER_CELL = 2

# Fraction of a cell's width added on each side when re-cropping, so a feature
# sitting on a cell boundary is not cut in half by the grid we invented.
CELL_MARGIN = 0.25


def cell_index(pts: np.ndarray, shape: tuple[int, int], grid: int = GRID) -> np.ndarray:
    """(N, 2) points of (x, y) -> (N, 2) integer (row, col) cell indices."""
    h, w = shape[:2]
    p = np.asarray(pts, np.float64).reshape(-1, 2)
    r = np.clip((p[:, 1] / h * grid).astype(int), 0, grid - 1)
    c = np.clip((p[:, 0] / w * grid).astype(int), 0, grid - 1)
    return np.stack([r, c], axis=1)


def counts(pts: np.ndarray, shape: tuple[int, int], grid: int = GRID) -> np.ndarray:
    """Matches per cell, as a (grid, grid) integer array. Row 0 is the TOP of the image."""
    out = np.zeros((grid, grid), int)
    if len(pts) == 0:
        return out
    idx = cell_index(pts, shape, grid)
    np.add.at(out, (idx[:, 0], idx[:, 1]), 1)
    return out


def weak_cells(cell_counts: np.ndarray, min_per_cell: int = MIN_PER_CELL) -> list[tuple[int, int]]:
    """Cells below the Sec.6.7 minimum, emptiest first - so a budget spends where it helps most."""
    rows, cols = np.where(cell_counts < min_per_cell)
    return [(int(r), int(c)) for _, r, c in
            sorted(zip(cell_counts[rows, cols], rows, cols), key=lambda t: t[0])]


def cell_bounds(cell: tuple[int, int], shape: tuple[int, int],
                grid: int = GRID, margin: float = CELL_MARGIN) -> tuple[int, int, int, int]:
    """Pixel box (x0, y0, x1, y1) for a cell, widened by `margin` and clipped to the image."""
    h, w = shape[:2]
    r, c = cell
    ch, cw = h / grid, w / grid
    mh, mw = ch * margin, cw * margin
    return (int(max(0, c * cw - mw)), int(max(0, r * ch - mh)),
            int(min(w, (c + 1) * cw + mw)), int(min(h, (r + 1) * ch + mh)))


def _project_box(box, H_inv, src_shape):
    """Map a reference box back into source pixels via H_inv, as an axis-aligned box."""
    x0, y0, x1, y1 = box
    corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float32).reshape(-1, 1, 2)
    p = cv2.perspectiveTransform(corners, H_inv).reshape(-1, 2)
    if not np.all(np.isfinite(p)):
        return None
    sh, sw = src_shape[:2]
    sx0, sy0 = int(np.floor(p[:, 0].min())), int(np.floor(p[:, 1].min()))
    sx1, sy1 = int(np.ceil(p[:, 0].max())), int(np.ceil(p[:, 1].max()))
    sx0, sy0 = max(0, sx0), max(0, sy0)
    sx1, sy1 = min(sw, sx1), min(sh, sy1)
    if sx1 - sx0 < 16 or sy1 - sy0 < 16:
        return None                      # projected outside the source, or too small to match in
    return sx0, sy0, sx1, sy1


def redetect(src_img: np.ndarray, ref_img: np.ndarray, H: np.ndarray,
             cells, match_fn=None, grid: int = GRID, margin: float = CELL_MARGIN,
             max_cells: int | None = None):
    """Look again inside under-filled reference cells. Returns (src_pts, ref_pts, info).

    Args:
        src_img, ref_img: the SAME arrays the first pass matched on.
        H: current source -> reference transform. Required, and the result is only
            as trustworthy as it is - see the module docstring.
        cells: iterable of (row, col) from `weak_cells`.
        match_fn: callable (a, b) -> (src_pts, ref_pts) in local pixel coordinates.
            Defaults to `core.matcher.match`. Injected so this is testable without
            paying for LoFTR.
        max_cells: stop after this many cells. Each one costs a match call, so an
            8x8 grid that is mostly empty can cost 64 of them.

    Returns points in FULL-IMAGE coordinates, ready to concatenate with the first pass.
    """
    if H is None:
        return (np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32),
                {"attempted": 0, "succeeded": 0, "added": 0, "note": "no transform available"})

    if match_fn is None:                              # pragma: no cover - needs torch
        from core.matcher import match as _m

        def match_fn(a, b):
            s, r, _ = _m(a, b)
            return s, r

    try:
        H_inv = np.linalg.inv(np.asarray(H, np.float64))
    except np.linalg.LinAlgError:
        return (np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32),
                {"attempted": 0, "succeeded": 0, "added": 0, "note": "H is singular"})

    cells = list(cells)[:max_cells] if max_cells is not None else list(cells)
    got_src, got_ref = [], []
    attempted = succeeded = 0

    for cell in cells:
        rx0, ry0, rx1, ry1 = cell_bounds(cell, ref_img.shape, grid, margin)
        projected = _project_box((rx0, ry0, rx1, ry1), H_inv, src_img.shape)
        if projected is None:
            continue
        sx0, sy0, sx1, sy1 = projected

        attempted += 1
        try:
            s_loc, r_loc = match_fn(src_img[sy0:sy1, sx0:sx1], ref_img[ry0:ry1, rx0:rx1])
        except Exception:
            continue                      # a bad crop must not take the whole run down
        if len(s_loc) == 0:
            continue

        succeeded += 1
        got_src.append(np.asarray(s_loc, np.float32) + [sx0, sy0])
        got_ref.append(np.asarray(r_loc, np.float32) + [rx0, ry0])

    if not got_src:
        return (np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32),
                {"attempted": attempted, "succeeded": 0, "added": 0, "note": "no new matches"})

    src_new = np.concatenate(got_src).astype(np.float32)
    ref_new = np.concatenate(got_ref).astype(np.float32)
    return src_new, ref_new, {"attempted": attempted, "succeeded": succeeded,
                              "added": int(len(src_new)), "note": "ok"}


def summary(pts: np.ndarray, shape: tuple[int, int], grid: int = GRID,
            min_per_cell: int = MIN_PER_CELL) -> dict:
    """A human-readable picture of where the matches are. NOT a metric.

    Deliberately does not return `grid_coverage_fraction` or `distribution_cv`.
    Those are Samrudh's, defined in `evaluation/metrics.py`, and quoting a second
    implementation of them is exactly the substitution `pipeline.py` refuses to make.
    """
    c = counts(pts, shape, grid)
    weak = weak_cells(c, min_per_cell)
    return {
        "cell_counts": c,
        "n_cells": grid * grid,
        "n_empty": int((c == 0).sum()),
        "n_weak": len(weak),
        "weak_cells": weak,
        "busiest_cell": tuple(int(v) for v in np.unravel_index(int(np.argmax(c)), c.shape)),
        "max_in_one_cell": int(c.max()),
        "min_per_cell": min_per_cell,
    }
