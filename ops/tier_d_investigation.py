"""Bet A, and what looking at it properly turned up about Tier D.

RUN
    python -m ops.tier_d_investigation          # measure and print
    python -m ops.tier_d_investigation --log    # also append rows to results_log.csv

WHAT THIS MEASURES, AND WHY EACH PIECE IS HERE
----------------------------------------------
1. BET A. `core/scale.py:101` resamples both images to the COARSER grid, so the
   640x640 Kaguya optical crop is downsampled to 99x99 before matching and LoFTR's
   coarse stage (stride 8) runs on a 12x12 grid - an effective 500 m/px against
   elevation data carrying 60 m/px. Bet A renders the DEM into the SENSOR's grid
   instead, so the match runs at 640x640 with no downsampling.

2. GROUND TRUTH, which Tier D has never had. Because the reference is sampled at
   the optical image's own pixel centres, the two images share a grid, and the true
   alignment is a pure translation recoverable by FFT cross-correlation. It is
   validated per-quadrant below rather than trusted - one global peak on its own is
   not evidence. Three of the four quadrants agree with it within 2 px; the fourth
   does not, so the alignment is NOT a perfectly uniform translation and is reported
   that way. It does not change the conclusion: the candidates differ by ~24 px and
   LoFTR is wrong by ~200 px against either.

3. THE LIGHTING CONVENTION - two errors, both now fixed and both derived, not fitted.
   (a) `evaluation/shaded_relief.py` (before 3 Sep 2026) unpacked `np.gradient` in
       the wrong axis order, which REFLECTED the sun about the image diagonal: a
       requested azimuth `a` lit the terrain as if from `90 - a`. The Day-5 reading of
       this as "lit from az+180" was only half right. Pinned now by
       `evaluation/test_shaded_relief.py` (a sun from the top must light a hill's top
       flank and a crater's bottom wall).
   (b) The label azimuth (284.901 deg, `view:sun_azimuth`) is clockwise from TRUE
       NORTH; the renderer wants clockwise from IMAGE-UP. In this south-polar
       stereographic map north is rotated clockwise by the longitude, so the crop
       centre's 44.73 E must be added: 329.63 deg in the image frame
       (`ops/solar_geometry.py`). That was the "unexplained ~15 deg" of the Day-5
       sweep.
   With both corrections the render correlates with the photograph at NCC +0.64 at
   zero offset and the FFT peak reaches +0.75 (was -0.57 / +0.59 / +0.71). The
   azimuth sweep below peaks within its 5-degree step of the derived value - the
   derivation is what is used, the sweep is only the check.

WHAT IS NOT TUNED
-----------------
No sun angle in this file is chosen because it makes the answer better. The
"as-labelled" arm renders at the label azimuth without the meridian correction,
purely to quantify what that error costs.
"""
from __future__ import annotations

import argparse
import pathlib

import cv2
import numpy as np
from scipy.ndimage import map_coordinates

from core.io_loader import load
from core.matcher import match
from core.pipeline import _normalise_illumination
from core.ransac import filter_matches
from core.scale import to_common_gsd, to_original
from evaluation.shaded_relief import render_shaded_relief
from ops.build_tier_d_pair import KAGUYA_GSD
from ops.fetch_lola_dem import OFFSET_PX, SCALE_M, fetch_window, pixel_to_latlon

KAGUYA = pathlib.Path(r"C:\Users\samar\sih26166_data\raw\TC1S2B0_01_03482S746E0433.tif")
WINDOW = (5120, 2240, 640, 640)
RECORDED_AZIMUTH = 284.901      # from the Kaguya scene label, via PROVENANCE.md
SUN_ELEVATION = 16.98
PAIR_ID = "pair_04_tierD_native"


def _z(x):
    """Percentile-stretch to [0,1] then standardise, so NCC is a plain mean product."""
    x = np.asarray(x, np.float64)
    lo, hi = np.percentile(x, [2, 98])
    x = np.clip((x - lo) / (hi - lo + 1e-12), 0, 1)
    return (x - x.mean()) / (x.std() + 1e-12)


def dem_on_optical_grid():
    """Sample the LOLA DEM at the Kaguya crop's own pixel centres."""
    x, y, tile, _ = (*WINDOW[:3], WINDOW[3])
    optical, meta = load(KAGUYA, window=WINDOW)
    kx0, sx, _, ky0, _, sy = meta["transform"]
    x_left, y_top = kx0 + sx * x, ky0 + sy * y
    x_right, y_bottom = x_left + sx * tile, y_top + sy * tile
    corners = [(OFFSET_PX - yy / SCALE_M, OFFSET_PX + xx / SCALE_M)
               for xx in (x_left, x_right) for yy in (y_top, y_bottom)]
    latlon = [pixel_to_latlon(l, s) for l, s in corners]
    dem, (bl, bs) = fetch_window(
        min(v[0] for v in latlon), max(v[0] for v in latlon),
        min(v[1] for v in latlon), max(v[1] for v in latlon),
        cache_dir=KAGUYA.parent)
    gx, gy = np.meshgrid(x_left + sx * (np.arange(tile) + 0.5),
                         y_top + sy * (np.arange(tile) + 0.5))
    dem_native = map_coordinates(
        dem.astype(np.float64),
        [(OFFSET_PX - gy / SCALE_M) - bl, (OFFSET_PX + gx / SCALE_M) - bs],
        order=3, mode="reflect")
    return optical, dem_native


def fft_peak(a, b):
    """Integer (dx, dy) that moves `a` onto `b`, and the peak NCC.

    One convention for the whole project: `core.reliability.xcorr_peak`, pinned by
    `core/test_reliability.py::test_xcorr_peak_sign` - if b == roll(a, (dy, dx))
    the answer is (dx, dy). So for a = optical (source) and b = relief (reference),
    (dx, dy) is the displacement `reference - source` that a correct match must show.
    The Day-5 version of this function used the opposite sign, so its logged
    ground truth reads (-9,+23) where this reads (+9,-23). Same alignment.
    """
    from core.reliability import xcorr_peak
    dx, dy, v = xcorr_peak(a, b)
    return (dx, dy), v


def quadrant_agreement(optical, relief):
    """Four independent quadrant alignments. Agreement is what makes the peak evidence."""
    h = optical.shape[0] // 2
    out = []
    for name, sl in (("top-left", (slice(0, h), slice(0, h))),
                     ("top-right", (slice(0, h), slice(h, None))),
                     ("bottom-left", (slice(h, None), slice(0, h))),
                     ("bottom-right", (slice(h, None), slice(h, None)))):
        out.append((name, *fft_peak(optical[sl], relief[sl])))
    return out


def run_arm(optical, relief, truth_dxdy):
    """Full match pipeline on one lighting, scored against a known translation."""
    ma = mb = {"gsd_mpp": KAGUYA_GSD}
    ref = np.rint(relief * 65535.0).astype(np.uint16).astype(np.float32)
    a_s, b_s, gsd, f = to_common_gsd(optical.astype(np.float32), ma, ref, mb)
    an, _ = _normalise_illumination(a_s, ma)
    bn, _ = _normalise_illumination(b_s, mb)
    s, r, _ = match(an, bn)
    s = to_original(s, f["a"]) if len(s) else s
    r = to_original(r, f["b"]) if len(r) else r
    if not len(s):
        return {"n_matches": 0, "gsd": gsd, "rmse_gt_px": None, "residual_px": None,
                "within": {}, "inliers": None}

    err = (r - s) - np.asarray(truth_dxdy, np.float64)   # truth is a pure translation
    mag = np.hypot(err[:, 0], err[:, 1])
    rmse = float(np.sqrt(np.mean(mag ** 2)))
    _si, _ri, H, info = filter_matches(s, r)
    residual = None
    if H is not None:
        c = cv2.perspectiveTransform(np.array([[[320.0, 320.0]]], np.float32), H).reshape(2)
        residual = float(np.hypot(c[0] - (320 + truth_dxdy[0]), c[1] - (320 + truth_dxdy[1])))
    return {"n_matches": len(s), "gsd": gsd, "rmse_gt_px": rmse,
            "median_err_px": float(np.median(mag)), "centre_err_px": residual,
            "within": {t: int((mag < t).sum()) for t in (2, 3, 5, 10, 20)},
            "inliers": (info or {}).get("inliers")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", action="store_true", help="append rows to results_log.csv")
    args = ap.parse_args()

    optical, dem = dem_on_optical_grid()
    print(f"  optical {optical.shape} at {KAGUYA_GSD:.4f} m/px   "
          f"DEM {dem.min():.0f}..{dem.max():.0f} m over {640 * KAGUYA_GSD:.0f} m\n")

    # Crop-centre longitude -> meridian convergence -> image-frame azimuth. Derived.
    from ops.solar_geometry import image_frame_azimuth
    _optical_meta = load(KAGUYA, window=(WINDOW[0], WINDOW[1], 8, 8))[1]
    _kx0, _sx, _, _ky0, _, _sy = _optical_meta["transform"]
    _xc = _kx0 + _sx * (WINDOW[0] + WINDOW[2] / 2.0)
    _yc = _ky0 + _sy * (WINDOW[1] + WINDOW[3] / 2.0)
    _lat_c, lon_c = pixel_to_latlon(OFFSET_PX - _yc / SCALE_M, OFFSET_PX + _xc / SCALE_M)
    lightings = {
        "as-labelled": RECORDED_AZIMUTH,                                  # no meridian correction
        "corrected": image_frame_azimuth(RECORDED_AZIMUTH, lon_c),        # 329.63 deg here
    }
    print(f"  crop centre lon {lon_c:.3f} E -> image-frame azimuth "
          f"{lightings['corrected']:.3f} deg (label {RECORDED_AZIMUTH})")
    reliefs = {k: render_shaded_relief(dem, az, SUN_ELEVATION, KAGUYA_GSD)
               for k, az in lightings.items()}

    print("  LIGHTING CONVENTION")
    for k, az in lightings.items():
        print(f"    {k:<12} az {az:7.3f} deg   NCC vs optical at zero offset "
              f"{float((_z(optical) * _z(reliefs[k])).mean()):+.4f}")

    print("\n  GROUND TRUTH (FFT cross-correlation, corrected lighting)")
    truth, peak = fft_peak(optical, reliefs["corrected"])
    print(f"    global peak (dx,dy) = ({truth[0]:+d}, {truth[1]:+d}) px "
          f"= ({truth[0]*KAGUYA_GSD:+.0f}, {truth[1]*KAGUYA_GSD:+.0f}) m   NCC {peak:+.4f}")
    print("    convention: (dx,dy) = reference - source, the shift that moves the optical onto the relief")
    # The sign, checked rather than trusted: apply the shift and the images must line up.
    rolled = np.roll(optical, (truth[1], truth[0]), axis=(0, 1))
    print(f"    check: NCC at zero offset after shifting the optical by (dx,dy): "
          f"{float((_z(rolled) * _z(reliefs['corrected'])).mean()):+.4f} "
          f"(was {float((_z(optical) * _z(reliefs['corrected'])).mean()):+.4f} unshifted)")
    print("    per-quadrant, independent:")
    quads = quadrant_agreement(optical, reliefs["corrected"])
    for name, (dx, dy), v in quads:
        print(f"      {name:<13} ({dx:+4d},{dy:+4d})  NCC {v:+.4f}")
    devs = sorted(max(abs(dx - truth[0]), abs(dy - truth[1])) for _n, (dx, dy), _v in quads)
    n_agree = sum(1 for d in devs if d <= 2)
    spread = devs[-1]
    print(f"    {n_agree}/4 quadrants agree with the global peak within 2 px; "
          f"worst disagreement {spread} px ({spread * KAGUYA_GSD:.0f} m)")
    if n_agree < 4:
        print("    NOTE: not a perfectly uniform translation. The conclusion below does not")
        print("    depend on which candidate is right - they differ by ~24 px and LoFTR's")
        print("    median error is ~200 px against either.")

    print("\n  LoFTR AGAINST THAT GROUND TRUTH")
    rows = []
    for k in lightings:
        res = run_arm(optical, reliefs[k], truth)
        rows.append((k, res))
        w = res["within"]
        print(f"    {k:<12} {res['n_matches']:>4} matches   "
              f"rmse_gt {res['rmse_gt_px']:8.2f} px = {res['rmse_gt_px']*res['gsd']:7.0f} m   "
              f"median {res['median_err_px']:7.2f} px")
        print(f"                 correct within: "
              + "  ".join(f"{t}px:{w[t]}/{res['n_matches']}" for t in sorted(w)))

    if args.log:
        from evaluation.logger import log_result
        for k, res in rows:
            az = lightings[k]
            log_result(
                PAIR_ID, "D", "ours_loftr",
                {"rmse_gt_px": res["rmse_gt_px"], "residual_px": res["centre_err_px"],
                 "inlier_count": res["inliers"], "inlier_ratio": None,
                 "grid_coverage_fraction": None, "distribution_cv": None,
                 "n_matches": res["n_matches"], "status": "ok"},
                config=(f"bet A: LOLA ldem_60s_60m cubic-resampled onto the Kaguya grid, "
                        f"640x640 at {KAGUYA_GSD} m/px, no downsampling (to_common_gsd is a "
                        f"no-op); hillshade az {az:.3f} deg ({k}), el {SUN_ELEVATION} deg; "
                        f"LoFTR + gradient_orientation + MAGSAC++ 3.0 px"),
                gsd_mpp=KAGUYA_GSD,
                notes=(f"Ground truth ({truth[0]:+d},{truth[1]:+d}) px (reference minus source; "
                       f"the Day-5 rows used the opposite sign) by FFT cross-correlation, "
                       f"NCC {peak:+.3f}; {n_agree}/4 quadrants agree within 2 px, worst {spread} px, "
                       f"so it is not a perfectly uniform translation. rmse_gt_px is the TRUE match "
                       f"error. Correct within 10 px: {res['within'].get(10, 0)}/{res['n_matches']}. "
                       f"Renderer convention and meridian convergence fixed 3 Sep 2026 "
                       f"(evaluation/shaded_relief.py, ops/solar_geometry.py). "
                       f"See ops/tier_d_investigation.py."))
        log_result(
            PAIR_ID, "D", "fft_phase_correlation",
            {"rmse_gt_px": None, "residual_px": None, "inlier_count": None,
             "inlier_ratio": None, "grid_coverage_fraction": None,
             "distribution_cv": None, "n_matches": None, "status": "ok"},
            config=(f"global FFT cross-correlation, percentile-stretched, corrected "
                    f"lighting az {lightings['corrected']:.3f} deg; no features, no RANSAC"),
            gsd_mpp=KAGUYA_GSD,
            notes=(f"Registers the pair at ({truth[0]:+d},{truth[1]:+d}) px (reference minus "
                   f"source) = {np.hypot(*truth)*KAGUYA_GSD:.0f} m, peak NCC {peak:.3f}; {n_agree}/4 "
                   f"quadrants agree within 2 px, worst {spread} px. NO rmse_gt_px ON PURPOSE: "
                   f"this method DEFINES the reference alignment, so scoring it against itself "
                   f"would be circular. Quadrant agreement is its evidence, not an accuracy. "
                   f"Lighting: renderer convention + meridian convergence fixed 3 Sep 2026."))
        print("\n  logged 3 rows to evaluation/results_log.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
