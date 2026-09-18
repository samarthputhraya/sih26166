"""Where can this registration be trusted? A per-cell answer with three states.

    from core.reliability import reliability_map
    rel = reliability_map(ref_shape, src_raw, ref_raw, H, src_in, ref_in,
                          warped_img, ref_img, gsd_mpp=..., H_true=...)
    rel["state"]        # (8, 8) array of "verified" | "weak" | "no_evidence"
    rel["global"]       # the independent area check on the whole frame

WHY THREE STATES AND NOT A SCORE
--------------------------------
Every registration tool we found reports one number for the whole image, and the
number it reports is usually a fit residual - how well the matches agree with the
transform fitted to them. That is self-consistency, not accuracy. On the real
Kaguya <-> LOLA pair this project's matcher produced 105 correspondences, MAGSAC
reached consensus on a homography, and ZERO of the 105 were correct within 94 m
(`ops/tier_d_investigation.py`, `evaluation/results_log.csv`). A colour map of
the inlier ratio would have painted that pair green.

So each 8x8 cell of the reference frame gets one of three states, and they are
NOT points on one scale:

  no_evidence  the matcher produced no inlier in this cell. The system has no
               measurement here. This is NOT a low score - painting it "bad"
               would be as much of a fabrication as painting it "good".
  weak         there are inliers, but the cell fails at least one of the tests
               below. Something was measured and it does not hold up.
  verified     enough inliers, they agree with the transform, AND an INDEPENDENT
               test that never looks at the matches agrees too.

THE INDEPENDENT TEST
--------------------
After warping the source into the reference frame with H, each cell of the warped
image is cross-correlated (FFT, on illumination-normalised pixels) against the same
cell of the reference. If the two are aligned, the correlation peak sits at a zero
shift with a high value. If H is a plausible fit to wrong matches, the peak sits
elsewhere - on Tier D it sits ~200 px away - and no amount of RANSAC consensus can
hide that, because this test never sees the matches. The same test on the whole
frame gives the GLOBAL verdict: `global["contradicted"]` is True when the area
check disagrees with H by more than a few pixels. That flag is what triggers the
fallback in `core/pipeline.py`.

This is not a new idea and the slide must say so: Uss et al. 2016 (IEEE TGRS)
estimate per-area registration accuracy without ground truth; Brown & Lowe 2007
verify an image match from inlier counts; Wan et al. 2021 use phase correlation
where features fail on optical-vs-DEM. What is ours: the explicit no-evidence
state, the matcher-vs-area disagreement as the failure signal, and the
calibration below against exact ground truth on lunar data.

CALIBRATION - the part that can kill the claim
----------------------------------------------
With `H_true` (synthetic pairs), every cell also gets its TRUE error: the RMS
distance, over a 5x5 grid of reference points in the cell, between where H sends
the true source point and where it belongs. `summary_by_state` then says, per
state, the median and 90th-percentile true error and the fraction of cells under
0.5 px and 1 px. If "verified" cells are not measurably better than "weak" ones,
the three states are a colour scheme, not a claim. `python -m core.reliability_calibrate`
runs this over the sun-azimuth sweep and writes `core/reliability_calibration.csv`.

UNITS. Cells are on the REFERENCE grid, thresholds are in reference pixels, and
every pixel figure is also given in metres when `gsd_mpp` is known - two grids
6.4x apart nearly produced a wrong conclusion on Day 5.
"""
from __future__ import annotations

import numpy as np

try:  # the grid is Samrudh's definition; never redefine it here
    from evaluation.metrics import GRID, INLIER_THRESH_PX
except ImportError:  # pragma: no cover - evaluation/ absent on a bare checkout
    GRID, INLIER_THRESH_PX = 8, 3.0

VERIFIED, WEAK, NO_EVIDENCE = "verified", "weak", "no_evidence"
STATE_CODE = {NO_EVIDENCE: 0, WEAK: 1, VERIFIED: 2}

# Initial thresholds. They are stated in the row's `config` and justified (or
# corrected) by core/reliability_calibration.csv - never tuned by eye.
MIN_INLIERS = 3            # fewer than this and the cell is only "weak" evidence
MIN_LOCAL_INLIER_RATIO = 0.5   # of the RAW matches in the cell, the share MAGSAC kept
MAX_CELL_SHIFT_PX = 2.0    # area check: correlation peak must sit within this of zero
MIN_CELL_NCC = 0.30        # ...and be at least this strong
MAX_GLOBAL_SHIFT_PX = 3.0  # whole-frame area check (used only when cells are too small)
MIN_GLOBAL_NCC = 0.30
MIN_CELL_SIDE_PX = 24      # below this an FFT peak on a cell means nothing
# The global verdict is a CONSENSUS OF CELLS, not one whole-frame peak. Measured on
# the calibration sweep (3 Sep 2026): a single whole-frame FFT is pulled 10-17 px off
# by the large-scale shading change at a 30-45 deg sun difference while 85-93% of
# the individual cells still agree with H within 2 px - and the fallback it then
# triggered was 10-40x LESS accurate than the homography it replaced. Cells are
# high-pass by construction and vote independently.
MIN_CELLS_FOR_VERDICT = 4  # fewer measurable cells than this -> frame-level check only
AGREE_FRAC = 0.50          # >= this share of measurable cells agree  -> H agrees
CONTRADICT_FRAC = 0.25     # <  this share agree                       -> H contradicted
                           # in between                                 -> unconfirmed


def _standardise(x):
    """Percentile-stretch to [0, 1], then zero-mean unit-variance. None if constant."""
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return None
    lo, hi = np.percentile(x, [2, 98])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo < 1e-9:
        return None
    x = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    s = x.std()
    if s < 1e-6:
        return None
    return (x - x.mean()) / s


def xcorr_peak(a, b):
    """Integer shift (dx, dy) that moves `a` onto `b`, and the peak NCC.

    Circular FFT cross-correlation on standardised pixels, so the peak value is a
    plain normalised correlation in [-1, 1]. Returns (None, None, 0.0) when either
    block is constant (nothing to correlate).

    Sign convention, pinned by `core/test_reliability.py::test_xcorr_peak_sign`:
    if b == roll(a, (dy, dx)) then xcorr_peak(a, b) == (dx, dy).
    """
    A, B = _standardise(a), _standardise(b)
    if A is None or B is None or A.shape != B.shape:
        return None, None, 0.0
    h, w = A.shape
    F = np.fft.ifft2(np.fft.fft2(B) * np.conj(np.fft.fft2(A))).real / A.size
    F = np.fft.fftshift(F)
    r, c = np.unravel_index(int(np.argmax(F)), F.shape)
    return int(c - w // 2), int(r - h // 2), float(F[r, c])


def _cell_slices(shape, grid):
    h, w = shape
    rows = np.linspace(0, h, grid + 1).astype(int)
    cols = np.linspace(0, w, grid + 1).astype(int)
    return rows, cols


def _cell_of(pts, shape, grid):
    """(row, col) cell index for each (x, y) point, same rule as evaluation/metrics.py."""
    h, w = shape
    pts = np.asarray(pts, dtype=np.float64).reshape(-1, 2)
    r = np.minimum((pts[:, 1] / h * grid).astype(int), grid - 1)
    c = np.minimum((pts[:, 0] / w * grid).astype(int), grid - 1)
    r = np.clip(r, 0, grid - 1)
    c = np.clip(c, 0, grid - 1)
    return r, c


def _reproj_error(src, ref, H):
    import cv2
    src = np.asarray(src, dtype=np.float32).reshape(-1, 1, 2)
    proj = cv2.perspectiveTransform(src, np.asarray(H, dtype=np.float64)).reshape(-1, 2)
    return np.linalg.norm(proj - np.asarray(ref, dtype=np.float64).reshape(-1, 2), axis=1)


def _true_error_grid(ref_shape, H, H_true, grid, n=5):
    """Per-cell RMS of |H(H_true^-1 p) - p| over an n x n grid of reference points p."""
    import cv2
    h, w = ref_shape
    rows, cols = _cell_slices(ref_shape, grid)
    H_inv_true = np.linalg.inv(np.asarray(H_true, dtype=np.float64))
    out = np.full((grid, grid), np.nan)
    for r in range(grid):
        for c in range(grid):
            ys = np.linspace(rows[r], rows[r + 1] - 1, n)
            xs = np.linspace(cols[c], cols[c + 1] - 1, n)
            gx, gy = np.meshgrid(xs, ys)
            p = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32).reshape(-1, 1, 2)
            p_src = cv2.perspectiveTransform(p, H_inv_true)
            q = cv2.perspectiveTransform(p_src, np.asarray(H, dtype=np.float64)).reshape(-1, 2)
            e = np.linalg.norm(q - p.reshape(-1, 2), axis=1)
            out[r, c] = float(np.sqrt(np.mean(e ** 2)))
    return out


def _normalised(img):
    """Illumination-normalise for the area check; fall back to raw pixels if unavailable."""
    try:
        from core.illumination import DEFAULT_METHOD, normalize
        return normalize(np.asarray(img, dtype=np.float32)), DEFAULT_METHOD
    except Exception:  # noqa: BLE001 - the check must never take the pipeline down
        return np.asarray(img, dtype=np.float32), "raw"


def xcorr_peak_subpixel(a, b):
    """`xcorr_peak`'s shift, refined to sub-pixel. Same sign convention (a -> b).
    Returns (dx, dy, peak) as floats, or (None, None, 0.0).

    Hann-windowed phase correlation (OpenCV's weighted-centroid peak) on the same
    standardised pixels. Measured on known fractional shifts of a textured image
    (core/test_reliability.py): errors mostly under 0.06 px, worst 0.14 px on a 14 px
    shift. A parabola through the NCC peak was tried first and was biased by
    0.10-0.18 px - not good enough to call sub-pixel.

    Used ONLY for the fallback's global translation. The per-cell area check keeps
    the integer peak: its thresholds (MAX_CELL_SHIFT_PX) were calibrated on it.
    """
    import cv2
    A, B = _standardise(a), _standardise(b)
    if A is None or B is None or A.shape != B.shape:
        return None, None, 0.0
    w = cv2.createHanningWindow(A.shape[::-1], cv2.CV_64F)
    (dx, dy), peak = cv2.phaseCorrelate(A.astype(np.float64), B.astype(np.float64), w)
    return float(dx), float(dy), float(peak)


def representations(img):
    """The two pixel representations the area check correlates on.

    `gradient_orientation` is what the matcher saw and is built for sun-angle
    changes; plain percentile-stretched intensity is what a hillshade and a
    photograph of the same terrain under the same sun share. Optical <-> DEM pairs
    correlate at +0.75 on intensity and near zero on orientation (measured on the
    Kaguya/LOLA pair, 3 Sep 2026), so the check tries both and keeps whichever
    peak is stronger - and says which. Neither one ever looks at a match.
    """
    n, method = _normalised(img)
    return [(method, n), ("intensity", np.asarray(img, dtype=np.float32))]


def best_peak(reps_a, reps_b):
    """xcorr_peak over paired representations; the strongest peak wins."""
    best = (None, None, 0.0, "n/a")
    for (ma, a), (_mb, b) in zip(reps_a, reps_b):
        dx, dy, ncc = xcorr_peak(a, b)
        if dx is not None and ncc > best[2]:
            best = (dx, dy, ncc, ma)
    return best


def reliability_map(ref_shape, src_raw, ref_raw, H, src_in, ref_in,
                    warped_img, ref_img, gsd_mpp=None, H_true=None, grid=GRID,
                    min_inliers=MIN_INLIERS, min_local_ratio=MIN_LOCAL_INLIER_RATIO,
                    max_cell_shift_px=MAX_CELL_SHIFT_PX, min_cell_ncc=MIN_CELL_NCC,
                    max_global_shift_px=MAX_GLOBAL_SHIFT_PX, min_global_ncc=MIN_GLOBAL_NCC,
                    inlier_thresh_px=INLIER_THRESH_PX) -> dict:
    """Classify every cell of the reference frame. Never raises on a bad pair.

    ref_shape  : (h, w) of the reference image.
    src_raw/ref_raw : ALL matcher output, (N, 2) (x, y), reference-frame pixels for ref.
    src_in/ref_in   : the MAGSAC inliers, same convention.
    H          : (3, 3) source -> reference, or None.
    warped_img : the source warped into the reference frame (None if H is None).
    ref_img    : the reference image, same shape as warped_img.
    gsd_mpp    : reference ground sample distance, for the metre figures.
    H_true     : ground truth, when it exists. Enables the per-cell true error.
    """
    h, w = int(ref_shape[0]), int(ref_shape[1])
    g = int(grid)
    state = np.full((g, g), NO_EVIDENCE, dtype=object)
    n_in = np.zeros((g, g), dtype=int)
    n_raw = np.zeros((g, g), dtype=int)
    local_ratio = np.full((g, g), np.nan)
    med_resid = np.full((g, g), np.nan)
    area_dx = np.full((g, g), np.nan)
    area_dy = np.full((g, g), np.nan)
    area_ncc = np.full((g, g), np.nan)
    area_ok = np.zeros((g, g), dtype=bool)

    config = (f"reliability v2: grid {g}x{g} on the reference frame; verified needs "
              f">={min_inliers} inliers, local inlier ratio >={min_local_ratio:g}, and an "
              f"area check (FFT cross-correlation of the warped source vs the reference, on "
              f"gradient-orientation or intensity pixels, whichever peaks stronger) with peak "
              f"shift <={max_cell_shift_px:g} px and NCC >={min_cell_ncc:g}; no_evidence = zero "
              f"inliers in the cell; H is contradicted when <{CONTRADICT_FRAC:.0%} of measurable "
              f"cells agree (agrees at >={AGREE_FRAC:.0%}, unconfirmed between), whole-frame peak "
              f"shift >{max_global_shift_px:g} px or NCC <{min_global_ncc:g} only when fewer than "
              f"{MIN_CELLS_FOR_VERDICT} cells are measurable; cells narrower than "
              f"{MIN_CELL_SIDE_PX} px skip the area check; nothing is verified in a "
              f"contradicted frame")

    glob = {"contradicted": None, "verdict": "unconfirmed", "basis": None,
            "agree_frac": None, "n_measurable": 0, "consensus_shift_px": None,
            "shift_px": None, "shift_m": None, "ncc": None,
            "quadrants": [], "self_consistency_px": None, "note": ""}

    if H is None:
        glob["note"] = "no transform - nothing to verify"
        return _package(state, n_in, n_raw, local_ratio, med_resid, area_dx, area_dy,
                        area_ncc, area_ok, glob, None, gsd_mpp, config, area_method="n/a")

    # --- what the matcher says, cell by cell ---------------------------------
    if len(ref_in):
        r, c = _cell_of(ref_in, (h, w), g)
        np.add.at(n_in, (r, c), 1)
    if len(ref_raw):
        r, c = _cell_of(ref_raw, (h, w), g)
        np.add.at(n_raw, (r, c), 1)
        err = _reproj_error(src_raw, ref_raw, H)
        inl = err < inlier_thresh_px
        for rr in range(g):
            for cc in range(g):
                m = (r == rr) & (c == cc)
                if m.any():
                    local_ratio[rr, cc] = float(inl[m].mean())
                    if inl[m].any():
                        med_resid[rr, cc] = float(np.median(err[m][inl[m]]))
    if len(src_in):
        glob["self_consistency_px"] = float(np.median(_reproj_error(src_in, ref_in, H)))

    # --- the independent test: correlation of pixels, never of matches ----------
    area_method = "n/a"
    if warped_img is not None and ref_img is not None \
            and np.asarray(warped_img).shape == np.asarray(ref_img).shape:
        reps_w = representations(warped_img)
        reps_r = representations(ref_img)
        rows, cols = _cell_slices((h, w), g)
        methods_used = []
        for rr in range(g):
            for cc in range(g):
                ys, xs = slice(rows[rr], rows[rr + 1]), slice(cols[cc], cols[cc + 1])
                if (rows[rr + 1] - rows[rr]) < MIN_CELL_SIDE_PX or (cols[cc + 1] - cols[cc]) < MIN_CELL_SIDE_PX:
                    continue
                dx, dy, ncc, meth = best_peak([(m, a[ys, xs]) for m, a in reps_w],
                                              [(m, b[ys, xs]) for m, b in reps_r])
                if dx is None:
                    continue
                methods_used.append(meth)
                area_dx[rr, cc], area_dy[rr, cc], area_ncc[rr, cc] = dx, dy, ncc
                area_ok[rr, cc] = (np.hypot(dx, dy) <= max_cell_shift_px) and (ncc >= min_cell_ncc)
        # Whole-frame peak and quadrants: reported as diagnostics, never the decider.
        gdx, gdy, gncc, gmeth = best_peak(reps_w, reps_r)
        if gdx is not None:
            area_method = gmeth
            glob["shift_px"] = (gdx, gdy)
            glob["ncc"] = gncc
            glob["representation"] = gmeth
            glob["shift_m"] = None if not gsd_mpp else float(np.hypot(gdx, gdy) * gsd_mpp)
            hh, ww = h // 2, w // 2
            for name, ys, xs in (("top-left", slice(0, hh), slice(0, ww)),
                                 ("top-right", slice(0, hh), slice(ww, None)),
                                 ("bottom-left", slice(hh, None), slice(0, ww)),
                                 ("bottom-right", slice(hh, None), slice(ww, None))):
                qdx, qdy, qncc, _qm = best_peak([(m, a[ys, xs]) for m, a in reps_w],
                                                [(m, b[ys, xs]) for m, b in reps_r])
                glob["quadrants"].append({"name": name, "shift_px": None if qdx is None else (qdx, qdy),
                                          "ncc": qncc})

        # THE VERDICT: cells vote. Each measurable cell either agrees with H (peak
        # within max_cell_shift_px and NCC >= min_cell_ncc) or it does not.
        meas = np.isfinite(area_ncc)
        n_meas = int(meas.sum())
        glob["n_measurable"] = n_meas
        if n_meas >= MIN_CELLS_FOR_VERDICT:
            frac = float((area_ok & meas).sum() / n_meas)
            glob["agree_frac"] = frac
            glob["basis"] = f"{n_meas} cells"
            strong = meas & (area_ncc >= min_cell_ncc)
            if strong.any():
                glob["consensus_shift_px"] = (float(np.median(area_dx[strong])),
                                              float(np.median(area_dy[strong])))
            if frac >= AGREE_FRAC:
                glob["verdict"] = "agrees"
            elif frac < CONTRADICT_FRAC:
                glob["verdict"] = "contradicted"
            else:
                glob["verdict"] = "unconfirmed"
            glob["contradicted"] = glob["verdict"] == "contradicted"
            glob["note"] = (f"{frac:.0%} of {n_meas} measurable cells agree with H -> "
                            f"{glob['verdict']}")
        elif gdx is not None:
            # Too few cells wide enough to vote (small frames): the whole-frame peak
            # decides, and the basis is said out loud.
            glob["basis"] = "whole frame (cells too small to vote)"
            glob["contradicted"] = bool(np.hypot(gdx, gdy) > max_global_shift_px or gncc < min_global_ncc)
            glob["verdict"] = "contradicted" if glob["contradicted"] else "agrees"
            glob["note"] = (f"whole-frame check ({gmeth}): peak shift ({gdx:+d},{gdy:+d}) px, "
                            f"NCC {gncc:+.2f} -> {glob['verdict']}")
        else:
            # A constant WARPED image with a textured reference means H pushed the
            # source out of the frame. That is not "unmeasurable"; it is wrong.
            ref_textured = _standardise(ref_img) is not None
            glob["contradicted"] = True if ref_textured else None
            glob["verdict"] = "contradicted" if ref_textured else "unconfirmed"
            glob["basis"] = "whole frame"
            glob["note"] = ("warped source is empty or constant - H maps the source outside "
                            "the reference frame" if ref_textured
                            else "area check not possible (constant images)")
    else:
        glob["note"] = "area check skipped (no warped image)"
    area_possible = np.isfinite(area_ncc)

    # --- the verdict --------------------------------------------------------
    for rr in range(g):
        for cc in range(g):
            if n_in[rr, cc] == 0:
                state[rr, cc] = NO_EVIDENCE
                continue
            enough = n_in[rr, cc] >= min_inliers
            consistent = np.isfinite(local_ratio[rr, cc]) and local_ratio[rr, cc] >= min_local_ratio
            # where the area check cannot run (tiny cells), it cannot verify either:
            # the cell stays weak. A cell is never promoted on matcher evidence alone,
            # and nothing is verified inside a frame whose transform is contradicted.
            independent = bool(area_possible[rr, cc] and area_ok[rr, cc]) and not glob["contradicted"]
            state[rr, cc] = VERIFIED if (enough and consistent and independent) else WEAK

    true_err = _true_error_grid((h, w), H, H_true, g) if H_true is not None else None
    return _package(state, n_in, n_raw, local_ratio, med_resid, area_dx, area_dy, area_ncc,
                    area_ok, glob, true_err, gsd_mpp, config, area_method)


def _package(state, n_in, n_raw, local_ratio, med_resid, area_dx, area_dy, area_ncc,
             area_ok, glob, true_err, gsd_mpp, config, area_method):
    g = state.shape[0]
    counts = {s: int((state == s).sum()) for s in (VERIFIED, WEAK, NO_EVIDENCE)}
    out = {
        "state": state,
        "state_code": np.vectorize(STATE_CODE.get)(state).astype(int),
        "counts": counts,
        "n_cells": g * g,
        "n_inliers": n_in, "n_raw": n_raw,
        "local_inlier_ratio": local_ratio,
        "median_inlier_residual_px": med_resid,
        "area_shift_dx": area_dx, "area_shift_dy": area_dy, "area_ncc": area_ncc,
        "area_agrees": area_ok,
        "area_method": area_method,
        "global": glob,
        "gsd_mpp": gsd_mpp,
        "config": config,
        "true_error_px": true_err,
        "summary_by_state": None,
    }
    if true_err is not None:
        out["summary_by_state"] = summary_by_state(state, true_err, gsd_mpp)
    return out


def summary_by_state(state, true_err, gsd_mpp=None):
    """Per state: how wrong were those cells really? The calibration table."""
    out = {}
    for s in (VERIFIED, WEAK, NO_EVIDENCE):
        e = true_err[state == s]
        e = e[np.isfinite(e)]
        if len(e) == 0:
            out[s] = {"n": 0}
            continue
        d = {"n": int(len(e)), "median_px": float(np.median(e)),
             "p90_px": float(np.percentile(e, 90)), "max_px": float(e.max()),
             "frac_under_0p5px": float((e < 0.5).mean()),
             "frac_under_1px": float((e < 1.0).mean())}
        if gsd_mpp:
            d["median_m"] = d["median_px"] * float(gsd_mpp)
            d["p90_m"] = d["p90_px"] * float(gsd_mpp)
        out[s] = d
    return out


def describe(rel: dict) -> list[str]:
    """Lines for the CLI report and the demo."""
    c = rel["counts"]
    g = rel["global"]
    lines = [f"verified {c[VERIFIED]}  weak {c[WEAK]}  no evidence {c[NO_EVIDENCE]}  "
             f"of {rel['n_cells']} cells"]
    v = g.get("verdict", "unconfirmed")
    lines.append(f"area check verdict: {v.upper()} - {g.get('note', '')}"
                 + (f" (basis: {g['basis']})" if g.get("basis") else ""))
    if g.get("consensus_shift_px") is not None:
        cx, cy = g["consensus_shift_px"]
        lines.append(f"cell-consensus shift of the warped source vs the reference: "
                     f"({cx:+.1f},{cy:+.1f}) px (median over cells with a real peak)")
    if g.get("shift_px") is not None:
        dx, dy = g["shift_px"]
        m = f" = {g['shift_m']:.0f} m" if g.get("shift_m") is not None else ""
        lines.append(f"whole-frame peak (diagnostic): ({dx:+d},{dy:+d}) px{m}, NCC {g['ncc']:+.3f}")
        if g.get("self_consistency_px") is not None:
            lines.append(f"matcher self-consistency (median inlier residual) "
                         f"{g['self_consistency_px']:.2f} px")
        qs = [q for q in g["quadrants"] if q["shift_px"] is not None]
        if qs:
            lines.append("quadrants: " + "  ".join(
                f"{q['name']} ({q['shift_px'][0]:+d},{q['shift_px'][1]:+d}) {q['ncc']:+.2f}" for q in qs))
    s = rel.get("summary_by_state")
    if s:
        for st in (VERIFIED, WEAK, NO_EVIDENCE):
            d = s[st]
            if d.get("n"):
                mm = f" ({d['median_m']:.1f} m)" if "median_m" in d else ""
                lines.append(f"  true error, {st:<11} n={d['n']:2d}  median {d['median_px']:.3f} px{mm}  "
                             f"p90 {d['p90_px']:.3f}  <0.5px {d['frac_under_0p5px']:.0%}  <1px {d['frac_under_1px']:.0%}")
            else:
                lines.append(f"  true error, {st:<11} n= 0")
    return lines


def state_at(rel: dict, x: float, y: float, ref_shape) -> str:
    """The reliability state of the cell containing reference pixel (x, y)."""
    r, c = _cell_of(np.array([[x, y]]), tuple(ref_shape), rel["state"].shape[0])
    return str(rel["state"][int(r[0]), int(c[0])])


def gate(changes: list, rel: dict, ref_shape, keep_states=(VERIFIED,)) -> dict:
    """Keep only change candidates that sit in cells the registration can vouch for.

    `changes` is `app.change_detection.detect_changes`' list: each has
    `centroid_px` [x, y] in the reference frame. Each candidate gets a
    `reliability` key. A candidate in a `no_evidence` cell is not "rejected" - it
    is UNASSESSABLE, and it is reported under that word, because a difference in a
    region where the alignment was never measured is not a detection and not a
    false alarm; it is a hole in the evidence. Only cells in `keep_states` pass.

    Returns {"kept": [...], "rejected_weak": [...], "unassessable": [...],
             "counts": {...}}. Nothing here changes the detector's output; it
    labels it. If the whole frame's transform was contradicted, nothing is kept.
    """
    kept, weak, unk = [], [], []
    for ch in changes:
        cx, cy = ch.get("centroid_px", (None, None))
        st = NO_EVIDENCE if cx is None else state_at(rel, cx, cy, ref_shape)
        if rel["global"].get("contradicted"):
            st = WEAK if st == VERIFIED else st
        ch = dict(ch, reliability=st)
        (kept if st in keep_states else (unk if st == NO_EVIDENCE else weak)).append(ch)
    return {"kept": kept, "rejected_weak": weak, "unassessable": unk,
            "counts": {"input": len(changes), "kept": len(kept),
                       "rejected_weak": len(weak), "unassessable": len(unk)}}


def ascii_map(rel: dict) -> str:
    """An 8x8 picture: V verified, w weak, . no evidence. Row 0 is the top of the image."""
    sym = {VERIFIED: "V", WEAK: "w", NO_EVIDENCE: "."}
    return "\n".join(" ".join(sym[s] for s in row) for row in rel["state"])
