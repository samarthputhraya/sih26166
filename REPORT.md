# SIH26166 - evaluation report

Generated 2026-09-18T22:04 from commit `e10deb0-dirty` by `python -m ops.make_report`. **Do not edit by hand** - every number below is read from the evidence files named in each section.

All pixel figures are on the REFERENCE image's grid, with its metres stated. Real pairs have no exact ground truth: accuracy on them is reported as held-out residuals (the 20 % of matches the fit never saw) and as loop closure. `residual_px` in results_log.csv is the RMSE over ALL held-out matches including outliers and is not quoted for real pairs.

## Products downloaded (sha256 recorded)

139 files: miloi 90, mimap 2, nac 4, nac_sweep 30, pradan_ohrc 2, pradan_tmc2 5, tcevem 2, tcmorm 2, tcort 2. Full list with URLs and sha256: `C:\Users\samar\sih26166_data\download_manifest_done.csv` and `nac_sweep_manifest_done.csv`. The Chandrayaan-2 OHRC frame `ch2_ohr_ncp_20200229T0739312111_d_img_d18` was already on disk (archive.org mirror).

## Chandrayaan-2 OHRC → LRO NAC (cross-sensor, cross-mission)

Windows cut at 0.25 m (OHRC) and the NAC's native ~0.9-1.25 m over the same ground on a south-polar-stereographic grid (`ops/cut_site_pairs.py`). Archive offset = how far the registration moved the source from where the two archives' (corrected) geometry put it - a property of the archives.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_ohrc_m1153871873le_w01` | -74.2457, 43.5769 | 3.3 | 3.724 | 603 | 370 | 0.614 | 0.19 | 0.724 (0.674) | 0.701 | 10 / 52 | agrees | loftr+magsac++ | 495.2 |
| `site_ohrc_m1153871873le_w01_t` | -73.7012, 43.7860 | 3.3 | 3.724 | 4603 | 4419 | 0.960 | 0.97 | 0.657 (0.612) | 0.926 | 57 / 1 | agrees | loftr+magsac++ | 2.7 |
| `site_ohrc_m1153871873le_w02` | -73.8679, 43.7733 | 3.3 | 3.724 | 5112 | 4680 | 0.915 | 1.00 | 1.005 (0.936) | 1.151 | 56 / 2 | agrees | loftr+magsac++ | 7.0 |
| `site_ohrc_m1153871873le_w02_t` | -73.7255, 43.7718 | 3.3 | 3.724 | 5284 | 5151 | 0.975 | 1.00 | 0.586 (0.546) | 0.751 | 64 / 0 | agrees | loftr+magsac++ | 2.7 |
| `site_ohrc_m1153871873le_w03` | -73.9686, 43.7529 | 3.3 | 3.724 | 3239 | 3120 | 0.963 | 0.75 | 0.655 (0.610) | 0.854 | 43 / 15 | agrees | loftr+magsac++ | 93.4 |
| `site_ohrc_m1153871873le_w03_t` | -73.7568, 43.7818 | 3.3 | 3.724 | 4877 | 4789 | 0.982 | 1.00 | 0.646 (0.602) | 0.890 | 61 / 0 | agrees | loftr+magsac++ | 11.0 |
| `site_ohrc_m1153871873le_w04` | -73.7012, 43.7860 | 3.3 | 3.724 | 4603 | 4419 | 0.960 | 0.97 | 0.657 (0.612) | 0.926 | 57 / 1 | agrees | loftr+magsac++ | 2.7 |
| `site_ohrc_m1153871873le_w04_t` | -73.7809, 43.7427 | 3.3 | 3.724 | 5285 | 5243 | 0.992 | 1.00 | 0.701 (0.653) | 0.874 | 64 / 0 | agrees | loftr+magsac++ | 15.2 |
| `site_ohrc_m1153871873le_w05` | -74.1375, 43.5232 | 3.3 | 3.724 | 1553 | 1339 | 0.862 | 0.44 | 0.951 (0.885) | 1.056 | 25 / 34 | agrees | loftr+magsac++ | 248.1 |
| `site_ohrc_m1153871873le_w05_t` | -73.6426, 43.8521 | 3.3 | 3.724 | 5420 | 5332 | 0.984 | 1.00 | 0.606 (0.564) | 0.755 | 64 / 0 | agrees | loftr+magsac++ | 10.0 |
| `site_ohrc_m1153871873le_w06` | -73.8054, 43.7781 | 3.3 | 3.724 | 4979 | 4861 | 0.976 | 1.00 | 0.656 (0.611) | 0.845 | 61 / 0 | agrees | loftr+magsac++ | 18.1 |
| `site_ohrc_m1153871873le_w06_t` | -73.7190, 43.8467 | 3.3 | 3.724 | 5152 | 5036 | 0.977 | 1.00 | 0.597 (0.556) | 0.752 | 64 / 0 | agrees | loftr+magsac++ | 4.1 |
| `site_ohrc_m1153871873le_w07` | -73.9058, 43.7077 | 3.3 | 3.724 | 4692 | 4553 | 0.970 | 1.00 | 0.741 (0.690) | 1.021 | 59 / 0 | agrees | loftr+magsac++ | 8.8 |
| `site_ohrc_m1153871873le_w08` | -73.9340, 43.7808 | 3.3 | 3.724 | 4099 | 4057 | 0.990 | 0.97 | 0.605 (0.563) | 0.764 | 55 / 2 | agrees | loftr+magsac++ | 37.5 |
| `site_ohrc_m1363141432re_w01_t` | -73.7012, 43.7860 | 5.8 | 4.98 | 2992 | 2930 | 0.979 | 0.98 | 0.493 (0.614) | 0.694 | 62 / 1 | agrees | loftr+magsac++ | 2.5 |
| `site_ohrc_m1363141432re_w02_t` | -73.7255, 43.7718 | 5.8 | 4.98 | 2756 | 2700 | 0.980 | 1.00 | 0.471 (0.587) | 0.634 | 64 / 0 | agrees | loftr+magsac++ | 3.9 |
| `site_ohrc_m1363141432re_w03_t` | -73.7568, 43.7818 | 5.8 | 4.98 | 2968 | 2952 | 0.995 | 1.00 | 0.500 (0.622) | 0.641 | 63 / 0 | agrees | loftr+magsac++ | 11.8 |
| `site_ohrc_m1363141432re_w04_t` | -73.7809, 43.7427 | 5.8 | 4.98 | 3021 | 3016 | 0.998 | 1.00 | 0.444 (0.553) | 0.575 | 64 / 0 | agrees | loftr+magsac++ | 13.3 |
| `site_ohrc_m1363141432re_w05_t` | -73.6426, 43.8521 | 5.8 | 4.98 | 2994 | 2962 | 0.989 | 1.00 | 0.415 (0.517) | 0.587 | 64 / 0 | agrees | loftr+magsac++ | 2.5 |
| `site_ohrc_m1363141432re_w06_t` | -73.7190, 43.8467 | 5.8 | 4.98 | 2280 | 2238 | 0.982 | 1.00 | 0.410 (0.510) | 0.579 | 64 / 0 | agrees | loftr+magsac++ | 8.5 |

## LRO NAC → LRO NAC (same sensor; loop legs)

Same sensor - NOT cross-sensor.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_m1153871873le_m1363141432re_w01_t` | -73.7012, 43.7860 | 9.1 | 1.337 | 2603 | 2549 | 0.979 | 0.98 | 0.326 (0.405) | 0.476 | 61 / 1 | agrees | loftr+magsac++ | 4.7 |
| `site_m1153871873le_m1363141432re_w02_t` | -73.7255, 43.7718 | 9.1 | 1.337 | 2796 | 2736 | 0.979 | 1.00 | 0.331 (0.412) | 0.548 | 64 / 0 | agrees | loftr+magsac++ | 4.2 |
| `site_m1153871873le_m1363141432re_w03_t` | -73.7568, 43.7818 | 9.1 | 1.337 | 2990 | 2954 | 0.988 | 1.00 | 0.316 (0.393) | 0.469 | 63 / 0 | agrees | loftr+magsac++ | 3.6 |
| `site_m1153871873le_m1363141432re_w04_t` | -73.7809, 43.7427 | 9.1 | 1.337 | 3066 | 3051 | 0.995 | 1.00 | 0.372 (0.463) | 0.533 | 64 / 0 | agrees | loftr+magsac++ | 3.6 |
| `site_m1153871873le_m1363141432re_w05_t` | -73.6426, 43.8521 | 9.1 | 1.337 | 2340 | 2262 | 0.967 | 1.00 | 0.322 (0.401) | 0.492 | 63 / 0 | agrees | loftr+magsac++ | 8.4 |
| `site_m1153871873le_m1363141432re_w06_t` | -73.7190, 43.8467 | 9.1 | 1.337 | 2709 | 2677 | 0.988 | 1.00 | 0.297 (0.369) | 0.509 | 64 / 0 | agrees | loftr+magsac++ | 5.6 |

## SAC's benchmark site: Chandrayaan-2 OHRC → TMC-2 nadir (cross-sensor, same mission)

OHRC frame `ch2_ohr_ncp_20210401T2357376656` (arXiv:2509.04775, Table 1), 13.1-13.9°S 25.2°E, vs TMC-2 pass `20250707T1853` (`ops/cut_pradan_pairs.py`). OHRC area-averaged 4×4 (~1.1 m) before resampling; TMC-2 ~5.6 m. Label sun: OHRC elevation 9.9°, TMC-2 69.4°, azimuths 120° apart. Both panchromatic - NOT multi-modal; same mission - NOT cross-mission.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrc_tmc_w01` | -13.1565, 25.1892 | 120.2 | 5.005 | 90 | 6 | 0.067 | 0.06 | 170.058 (948.245) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 637.9 |
| `sac_ohrc_tmc_w02` | -13.3669, 25.1880 | 120.2 | 5.005 | 105 | 6 | 0.057 | 0.09 | 112.891 (629.481) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 814.6 |
| `sac_ohrc_tmc_w03` | -13.5773, 25.1869 | 120.2 | 5.005 | 96 | 7 | 0.073 | 0.06 | 268.087 (1494.851) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 1006.7 |
| `sac_ohrc_tmc_w04` | -13.7877, 25.1857 | 120.2 | 5.005 | 148 | 7 | 0.047 | 0.05 | 124.811 (695.948) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 933.8 |

## Real viewpoint: TMC-2 fore (+25°) → aft (−25°), one pass (same sensor)

Same instrument, same sun, seconds apart: only the viewing direction differs (~50°). Relief parallax between the two (~0.93 × height) is not a homography - compare with the synthetic parallax rows below. Same sensor - NOT cross-sensor.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_tmcfore_tmcaft_w01` | -13.1565, 25.1892 | 0.0 | 0.999 | 234 | 52 | 0.222 | 0.14 | 49.358 (292.642) | 1.802 | 4 / 55 | unconfirmed | loftr+magsac++ | 1077.8 |
| `sac_tmcfore_tmcaft_w02` | -13.3669, 25.1880 | 0.0 | 0.999 | 282 | 118 | 0.418 | 0.41 | 4.075 (24.158) | 1.908 | 10 / 37 | unconfirmed | loftr+magsac++ | 364.2 |
| `sac_tmcfore_tmcaft_w03` | -13.5773, 25.1869 | 0.0 | 0.999 | 302 | 101 | 0.334 | 0.45 | 5.240 (31.065) | 1.934 | 5 / 32 | unconfirmed | loftr+magsac++ | 96.3 |
| `sac_tmcfore_tmcaft_w04` | -13.7877, 25.1857 | 0.0 | 0.999 | 651 | 368 | 0.565 | 0.62 | 2.617 (15.514) | 1.847 | 28 / 22 | agrees | loftr+magsac++ | 135.6 |

## Kaguya TC → Kaguya MI (cross-sensor; 749 nm visible and 1548 nm infrared)

Tier C rows are multi-modal (visible vs near-infrared). On them the declared method is the global-correlation fallback; compare its archive offset with the visible-band rows on the same windows.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_tc_morning_mi1548_w01` | -74.1077, 43.5487 | n/a | 2.0 | 35 | 6 | 0.171 | 0.08 | 57.068 (844.610) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 37.8 |
| `site_tc_morning_mi1548_w02` | -74.2982, 43.7217 | n/a | 2.0 | 33 | 5 | 0.152 | 0.08 | 62.375 (923.153) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 37.8 |
| `site_tc_morning_mi1548_w03` | -74.2100, 43.4127 | n/a | 2.0 | 34 | 5 | 0.147 | 0.08 | 74.582 (1103.817) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 37.8 |
| `site_tc_morning_mi749_w01` | -74.1077, 43.5487 | n/a | 2.0 | 334 | 313 | 0.937 | 0.97 | 0.468 (6.926) | 0.692 | 45 / 2 | agrees | loftr+magsac++ | 41.0 |
| `site_tc_morning_mi749_w02` | -74.2982, 43.7217 | n/a | 2.0 | 436 | 429 | 0.984 | 0.95 | 0.387 (5.720) | 0.562 | 56 / 3 | agrees | loftr+magsac++ | 46.4 |
| `site_tc_morning_mi749_w03` | -74.2100, 43.4127 | n/a | 2.0 | 416 | 413 | 0.993 | 1.00 | 0.234 (3.464) | 0.445 | 55 / 0 | agrees | loftr+magsac++ | 38.9 |

## Loop closure (OHRC → NAC A → NAC B vs OHRC → NAC B)

6 closed loops. Loop RMS median **0.104 m**, max 0.128 m (`ops/loop_closure.py`). Loop closure cancels any error attached to a single image (its geolocation, its own shading), so it measures correspondence consistency, not absolute ground accuracy.

| loop | window | RMS m | RMS px (B grid) | p90 px | methods | verdicts |
|---|---|---|---|---|---|---|
| `loop_m1153871873le_m1363141432re_w01_t` | -73.7012, 43.7860 | 0.128 | 0.103 | 0.156 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w02_t` | -73.7255, 43.7718 | 0.104 | 0.083 | 0.131 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w03_t` | -73.7568, 43.7818 | 0.121 | 0.097 | 0.152 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w04_t` | -73.7809, 43.7427 | 0.097 | 0.077 | 0.118 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w05_t` | -73.6426, 43.8521 | 0.097 | 0.077 | 0.104 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w06_t` | -73.7190, 43.8467 | 0.104 | 0.084 | 0.127 | loftr+magsac++ | agrees |

## Real sun-angle sweep (one OHRC frame vs LRO NAC frames)

Outcome by image evidence, rule v2 (`ops/sun_sweep.py` docstring): the matcher is right when |NCC| of its warp against the reference is ≥ 0.30 and at least the archive alignment's |NCC| − 0.05; when neither reaches 0.30 the image cannot judge (inconclusive). |NCC| because opposite suns anti-correlate a correct alignment. Derived from the logged NCCs; v2 moved 27 of 69 logged v1 labels (caught_failure → false_alarm 11, caught_failure → inconclusive 14, missed_failure → correct_accepted 1, missed_failure → inconclusive 1). This sweep is NOT the trust layer's detection evidence - see the next section.

| Δsun az (deg) | windows | NAC frames | registered & accepted | failed & caught | failed, not caught | correct but refused | inconclusive | median inliers |
|---|---|---|---|---|---|---|---|---|
| 0-10 | 16 | 6 | 16 | 0 | 0 | 0 | 0 | 4818 |
| 10-30 | 14 | 5 | 14 | 0 | 0 | 0 | 0 | 4247 |
| 30-60 | 12 | 4 | 11 | 0 | 0 | 0 | 1 | 559 |
| 60-90 | 7 | 3 | 0 | 1 | 0 | 1 | 5 | 58 |
| 90-120 | 5 | 2 | 0 | 0 | 0 | 1 | 4 | 8 |
| 120-180 | 15 | 5 | 0 | 0 | 0 | 10 | 5 | 209 |

## Trust layer on real imagery: planted confident-but-wrong registrations

`ops/trust_real_calibration.py`: 23 real windows whose registration is independently good; the true transform shifted by d metres and a match set that agrees with the WRONG transform perfectly. d = 0 is the false-alarm rate.

| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 |
|---|---|---|---|---|
| 0 | 0.00 | 46 | 0.0% | 62.0 |
| 1 | 0.80 | 184 | 0.0% | 60.5 |
| 2 | 1.61 | 184 | 0.0% | 43.7 |
| 3 | 2.41 | 184 | 81.5% | 8.1 |
| 5 | 4.02 | 184 | 100.0% | 0.0 |
| 10 | 8.03 | 184 | 100.0% | 0.0 |
| 20 | 16.06 | 184 | 100.0% | 0.0 |
| 50 | 40.16 | 184 | 100.0% | 0.0 |
| 100 | 80.32 | 184 | 100.0% | 0.0 |
| 200 | 160.64 | 184 | 100.0% | 0.0 |

## Viewpoint (synthetic, exact truth)

Off-nadir tilt applied to one image of a rendered pair (sun 15° apart), latest rows. With relief parallax ON the truth is a field and rmse_gt_px is measured against the plane homography, so it measures how far relief is from a homography, not a registration error.

| tilt (deg) | parallax | runs | median rmse_gt_px | max |
|---|---|---|---|---|
| 10 | off | 3 | 0.110 | 0.111 |
| 20 | off | 3 | 0.137 | 0.202 |
| 30 | off | 3 | 0.143 | 0.224 |
| 40 | off | 3 | 0.260 | 0.284 |
| 50 | off | 3 | 0.607 | 0.750 |
| 10 | on | 3 | 2.272 | 2.335 |
| 20 | on | 3 | 5.004 | 5.115 |
| 30 | on | 3 | 8.411 | 8.658 |
| 40 | on | 3 | 13.327 | 13.694 |
| 50 | on | 3 | 16.063 | 22.174 |

## Reproduce

```
python -m ops.cut_site_pairs --nac M1153871873LE --windows 8 --refit
python -m ops.run_real_pairs "site_ohrc_*" --log
python -m ops.loop_closure --a M1153871873LE --b M1363141432RE --tag t --log
python -m ops.cut_site_pairs --correct-chain $(cat <data>/nac/sweep_order.txt)
python -m ops.sun_sweep --windows 3 --log
python -m ops.trust_real_calibration "site_ohrc_m1153871873le_w*_t" ... --log
python -m ops.make_report
```

Rows in real_pairs_log.csv: 123 (119 distinct pairs/loops; where a pair was re-run, the latest row is shown). Rows in results_log.csv: 439.
