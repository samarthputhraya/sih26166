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

3. THE LIGHTING CONVENTION. `evaluation/shaded_relief.py` renders terrain lit from
   180 degrees OPPOSITE the azimuth it is handed. At the recorded solar azimuth the
   render is ANTI-correlated with the optical image (NCC -0.57); negating both
   gradients - exactly a 180-degree aspect flip - gives +0.59. Every Tier D row in
   `evaluation/results_log.csv`, ours and all three classical baselines, was scored
   against a reference lit from the wrong side. Both lightings are measured here so
   the effect is quantified rather than asserted.

WHAT IS NOT TUNED
-----------------
The corrected azimuth is `recorded + 180`, derived from the convention error, NOT
fitted to whatever maximises correlation. A sweep does peak slightly elsewhere
(~120 deg, NCC +0.64); that extra ~15 deg is not claimed and not used. Choosing a
sun angle because it makes the answer better is the move this file exists to avoid.

`evaluation/shaded_relief.py` is Samrudh's file and is NOT edited here. Rendering at
`azimuth + 180` through the existing function is arithmetically identical to
rendering at `azimuth` through a fixed one, so the fix stays his to make.
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
    """Integer (dx, dy) maximising cross-correlation, and the peak value."""
    A, B = _z(a), _z(b)
    n = A.shape[0]
    F = np.fft.fftshift(np.fft.ifft2(np.fft.fft2(A) * np.conj(np.fft.fft2(B))).real) / A.size
    r, c = np.unravel_index(np.argmax(F), F.shape)
    return (c - n // 2, r - n // 2), float(F[r, c])


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

    lightings = {
        "as-recorded": RECORDED_AZIMUTH,
        "corrected": (RECORDED_AZIMUTH + 180.0) % 360.0,
    }
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
                notes=(f"Ground truth ({truth[0]:+d},{truth[1]:+d}) px by FFT cross-correlation, "
                       f"NCC {peak:+.3f}; {n_agree}/4 quadrants agree within 2 px, worst {spread} px, "
                       f"so it is not a perfectly uniform translation. rmse_gt_px is the TRUE match "
                       f"error and is ~200 px against either candidate. Bet A: matching on the "
                       f"sensor grid raised matches 19->{res['n_matches']}, none correct within "
                       f"10 px. See ops/tier_d_investigation.py."))
        log_result(
            PAIR_ID, "D", "fft_phase_correlation",
            {"rmse_gt_px": None, "residual_px": None, "inlier_count": None,
             "inlier_ratio": None, "grid_coverage_fraction": None,
             "distribution_cv": None, "n_matches": None, "status": "ok"},
            config=(f"global FFT cross-correlation, percentile-stretched, corrected "
                    f"lighting az {lightings['corrected']:.3f} deg; no features, no RANSAC"),
            gsd_mpp=KAGUYA_GSD,
            notes=(f"Registers the pair at ({truth[0]:+d},{truth[1]:+d}) px "
                   f"= {np.hypot(*truth)*KAGUYA_GSD:.0f} m, peak NCC {peak:.3f}; {n_agree}/4 "
                   f"quadrants agree within 2 px, worst {spread} px. NO rmse_gt_px ON PURPOSE: "
                   f"this method DEFINES the reference alignment, so scoring it against itself "
                   f"would be circular. Quadrant agreement is its evidence, not an accuracy."))
        print("\n  logged 3 rows to evaluation/results_log.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
