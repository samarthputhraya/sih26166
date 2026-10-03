# SIH26166 - evaluation report

Generated 2026-10-04T00:58 from commit `04ed5f6` by `python -m ops.make_report`. **Do not edit by hand** - every number below is read from the evidence files named in each section. The latest real-pair rows were measured at commit `04ed5f6` (591 rows).

All pixel figures are on the REFERENCE image's grid, with its metres stated. Real pairs have no exact ground truth: accuracy on them is reported as held-out residuals (the 20 % of matches the fit never saw) and as loop closure. `residual_px` in results_log.csv is the RMSE over ALL held-out matches including outliers and is not quoted for real pairs.

## Products downloaded (sha256 recorded)

262 files: miloi 90, mimap 2, nac 4, nac_flip 5, nac_ladder 9, nac_sac 2, nac_siten 4, nac_sweep 30, pradan_iirs 52, pradan_ohrc 22, pradan_tmc2 36, tcevem 2, tcmorm 2, tcort 2. Full list with URLs and sha256: `C:\Users\samar\sih26166_data\download_manifest_done.csv` and `nac_sweep_manifest_done.csv`, `nac_sac_manifest_done.csv`. The Chandrayaan-2 OHRC frame `ch2_ohr_ncp_20200229T0739312111_d_img_d18` was already on disk (archive.org mirror).

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

## The whole lit overlap of one OHRC frame with one NAC (dense tiling)

Dense tiling, not hand-spread windows: every non-overlapping 640-px window (centres at least 1.1 × the window apart) that `ops.cut_site_pairs --windows 60 --tag full` finds in shared, lit, textured ground of the 74 °S OHRC frame and NAC `M1153871873LE` (Sun azimuths 3.3° apart). 37 windows of 596 m = 13.1 km². Verdicts: agrees 37; **accepted 37/37**; held-out median of the accepted windows: median 0.61 px = 0.57 m on the 0.931 m grid, 36 of 37 under 3 px (range 0.44-316.06). 1 accepted window(s) report a held-out median above 3 px (`site_ohrc_m1153871873le_w15_full` 316 px at an inlier ratio of 0.542). That number is the median of the 20 % of matches the fit never saw, and it is robust only while the inlier ratio stays well above 0.5 - at 0.54 a random held-out draw can be majority-outlier, and the median then describes the outliers. Independent image evidence says these windows are registered: the exported `registered_product.tif` correlates with its reference at NCC +0.87 to +0.95 across all 37 accepted windows (`ops/sun_sweep.py`'s |NCC| >= 0.30 rule, applied to the declared warp), and under the declared transform the median error over ALL matches on the worst of them is 1.08 px. This is a limit of the metric, not of the registration, and it is why the area check never looks at the matches. Wall time of `run_all`: 10.5 min in total, median 17.1 s per window, CPU only. Archive offset of each accepted window against its nearest accepted neighbour: median difference 19.3 m, max 57.2 m (`site_ohrc_m1153871873le_w15_full`), 3 over 50 m. Reported separately from the hand-spread windows above and never merged with them.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_ohrc_m1153871873le_w01_full` | -74.2457, 43.5769 | 3.3 | 3.724 | 603 | 371 | 0.615 | 0.19 | 0.868 (0.808) | 0.748 | 10 / 52 | agrees | loftr+magsac++ | 495.2 |
| `site_ohrc_m1153871873le_w02_full` | -73.8679, 43.7733 | 3.3 | 3.724 | 5113 | 4772 | 0.933 | 1.00 | 1.100 (1.025) | 1.266 | 55 / 0 | agrees | loftr+magsac++ | 6.8 |
| `site_ohrc_m1153871873le_w03_full` | -73.9686, 43.7529 | 3.3 | 3.724 | 3241 | 3121 | 0.963 | 0.75 | 0.646 (0.601) | 0.864 | 43 / 15 | agrees | loftr+magsac++ | 93.4 |
| `site_ohrc_m1153871873le_w04_full` | -73.7012, 43.7860 | 3.3 | 3.724 | 4604 | 4472 | 0.971 | 0.98 | 0.696 (0.648) | 0.990 | 57 / 1 | agrees | loftr+magsac++ | 2.7 |
| `site_ohrc_m1153871873le_w05_full` | -74.1375, 43.5232 | 3.3 | 3.724 | 1553 | 1352 | 0.871 | 0.47 | 1.059 (0.986) | 1.141 | 25 / 34 | agrees | loftr+magsac++ | 248.0 |
| `site_ohrc_m1153871873le_w06_full` | -73.8054, 43.7781 | 3.3 | 3.724 | 4979 | 4861 | 0.976 | 1.00 | 0.656 (0.611) | 0.845 | 61 / 0 | agrees | loftr+magsac++ | 18.1 |
| `site_ohrc_m1153871873le_w07_full` | -73.9058, 43.7077 | 3.3 | 3.724 | 4693 | 4554 | 0.970 | 1.00 | 0.744 (0.693) | 1.041 | 59 / 0 | agrees | loftr+magsac++ | 8.8 |
| `site_ohrc_m1153871873le_w08_full` | -73.9340, 43.7808 | 3.3 | 3.724 | 4099 | 4057 | 0.990 | 0.97 | 0.605 (0.563) | 0.764 | 55 / 2 | agrees | loftr+magsac++ | 37.5 |
| `site_ohrc_m1153871873le_w09_full` | -73.7255, 43.7718 | 3.3 | 3.724 | 5285 | 5151 | 0.975 | 1.00 | 0.582 (0.542) | 0.747 | 64 / 0 | agrees | loftr+magsac++ | 2.7 |
| `site_ohrc_m1153871873le_w10_full` | -74.0933, 43.6669 | 3.3 | 3.724 | 1903 | 1772 | 0.931 | 0.62 | 0.591 (0.550) | 0.794 | 34 / 24 | agrees | loftr+magsac++ | 196.8 |
| `site_ohrc_m1153871873le_w11_full` | -74.0134, 43.6863 | 3.3 | 3.724 | 4028 | 3983 | 0.989 | 0.77 | 0.661 (0.615) | 0.887 | 48 / 15 | agrees | loftr+magsac++ | 99.1 |
| `site_ohrc_m1153871873le_w12_full` | -74.0514, 43.6451 | 3.3 | 3.724 | 3133 | 3049 | 0.973 | 0.75 | 0.568 (0.528) | 0.687 | 43 / 16 | agrees | loftr+magsac++ | 142.1 |
| `site_ohrc_m1153871873le_w13_full` | -73.7568, 43.7818 | 3.3 | 3.724 | 4876 | 4788 | 0.982 | 1.00 | 0.658 (0.613) | 0.903 | 61 / 0 | agrees | loftr+magsac++ | 11.0 |
| `site_ohrc_m1153871873le_w14_full` | -73.7809, 43.7427 | 3.3 | 3.724 | 5285 | 5243 | 0.992 | 1.00 | 0.701 (0.653) | 0.874 | 64 / 0 | agrees | loftr+magsac++ | 15.2 |
| `site_ohrc_m1153871873le_w15_full` | -74.2450, 43.4745 | 3.3 | 3.724 | 718 | 389 | 0.542 | 0.23 | 316.057 (294.249) | 0.647 | 11 / 49 | agrees | loftr+magsac++ | 463.7 |
| `site_ohrc_m1153871873le_w16_full` | -74.0721, 43.6180 | 3.3 | 3.724 | 2822 | 2760 | 0.978 | 0.77 | 0.491 (0.457) | 0.724 | 41 / 15 | agrees | loftr+magsac++ | 162.2 |
| `site_ohrc_m1153871873le_w17_full` | -73.9509, 43.6915 | 3.3 | 3.724 | 3885 | 3812 | 0.981 | 1.00 | 0.474 (0.441) | 0.639 | 57 / 0 | agrees | loftr+magsac++ | 61.3 |
| `site_ohrc_m1153871873le_w18_full` | -73.9853, 43.6382 | 3.3 | 3.724 | 3585 | 3498 | 0.976 | 0.92 | 0.704 (0.656) | 0.920 | 48 / 5 | agrees | loftr+magsac++ | 88.2 |
| `site_ohrc_m1153871873le_w19_full` | -74.1865, 43.5696 | 3.3 | 3.724 | 956 | 749 | 0.783 | 0.39 | 1.151 (1.071) | 1.223 | 19 / 39 | agrees | loftr+magsac++ | 340.7 |
| `site_ohrc_m1153871873le_w20_full` | -73.6426, 43.8521 | 3.3 | 3.724 | 5420 | 5332 | 0.984 | 1.00 | 0.606 (0.564) | 0.755 | 64 / 0 | agrees | loftr+magsac++ | 10.0 |
| `site_ohrc_m1153871873le_w21_full` | -73.8364, 43.7383 | 3.3 | 3.724 | 4941 | 4877 | 0.987 | 1.00 | 0.642 (0.598) | 0.832 | 62 / 0 | agrees | loftr+magsac++ | 8.1 |
| `site_ohrc_m1153871873le_w22_full` | -73.9299, 43.6681 | 3.3 | 3.724 | 4357 | 4257 | 0.977 | 1.00 | 0.494 (0.460) | 0.690 | 62 / 0 | agrees | loftr+magsac++ | 29.9 |
| `site_ohrc_m1153871873le_w23_full` | -74.0692, 43.7069 | 3.3 | 3.724 | 2587 | 2506 | 0.969 | 0.77 | 0.457 (0.426) | 0.592 | 39 / 15 | agrees | loftr+magsac++ | 173.5 |
| `site_ohrc_m1153871873le_w24_full` | -74.1206, 43.5883 | 3.3 | 3.724 | 2082 | 2006 | 0.963 | 0.56 | 0.760 (0.708) | 0.939 | 30 / 28 | agrees | loftr+magsac++ | 226.4 |
| `site_ohrc_m1153871873le_w25_full` | -73.7190, 43.8467 | 3.3 | 3.724 | 5153 | 5036 | 0.977 | 1.00 | 0.605 (0.563) | 0.762 | 64 / 0 | agrees | loftr+magsac++ | 4.1 |
| `site_ohrc_m1153871873le_w26_full` | -74.0346, 43.7351 | 3.3 | 3.724 | 3572 | 3525 | 0.987 | 0.77 | 0.445 (0.414) | 0.626 | 49 / 15 | agrees | loftr+magsac++ | 120.7 |
| `site_ohrc_m1153871873le_w27_full` | -74.1523, 43.6491 | 3.3 | 3.724 | 1690 | 1566 | 0.927 | 0.55 | 0.640 (0.595) | 0.894 | 28 / 29 | agrees | loftr+magsac++ | 278.0 |
| `site_ohrc_m1153871873le_w28_full` | -74.1177, 43.6775 | 3.3 | 3.724 | 2152 | 2056 | 0.955 | 0.56 | 0.748 (0.697) | 0.917 | 34 / 28 | agrees | loftr+magsac++ | 232.0 |
| `site_ohrc_m1153871873le_w29_full` | -74.0960, 43.5525 | 3.3 | 3.724 | 2574 | 2454 | 0.953 | 0.70 | 0.541 (0.504) | 0.742 | 37 / 19 | agrees | loftr+magsac++ | 187.8 |
| `site_ohrc_m1153871873le_w30_full` | -73.8299, 43.8137 | 3.3 | 3.724 | 4944 | 4902 | 0.992 | 1.00 | 0.532 (0.496) | 0.681 | 63 / 0 | agrees | loftr+magsac++ | 14.3 |
| `site_ohrc_m1153871873le_w31_full` | -74.0302, 43.5964 | 3.3 | 3.724 | 3587 | 3556 | 0.991 | 0.77 | 0.525 (0.489) | 0.701 | 49 / 15 | agrees | loftr+magsac++ | 117.2 |
| `site_ohrc_m1153871873le_w32_full` | -74.2172, 43.4772 | 3.3 | 3.724 | 843 | 645 | 0.765 | 0.30 | 0.647 (0.602) | 0.641 | 16 / 45 | agrees | loftr+magsac++ | 406.5 |
| `site_ohrc_m1153871873le_w33_full` | -74.1587, 43.5721 | 3.3 | 3.724 | 1742 | 1635 | 0.939 | 0.52 | 0.467 (0.435) | 0.652 | 27 / 31 | agrees | loftr+magsac++ | 282.7 |
| `site_ohrc_m1153871873le_w34_full` | -74.2247, 43.5533 | 3.3 | 3.724 | 693 | 489 | 0.706 | 0.25 | 0.610 (0.568) | 0.681 | 14 / 48 | agrees | loftr+magsac++ | 438.5 |
| `site_ohrc_m1153871873le_w35_full` | -74.1929, 43.4924 | 3.3 | 3.724 | 1140 | 1009 | 0.885 | 0.39 | 0.499 (0.465) | 0.639 | 22 / 39 | agrees | loftr+magsac++ | 348.6 |
| `site_ohrc_m1153871873le_w36_full` | -74.0060, 43.6112 | 3.3 | 3.724 | 3980 | 3971 | 0.998 | 0.77 | 0.566 (0.527) | 0.698 | 49 / 15 | agrees | loftr+magsac++ | 97.9 |
| `site_ohrc_m1153871873le_w37_full` | -74.2077, 43.6188 | 3.3 | 3.724 | 939 | 787 | 0.838 | 0.30 | 0.571 (0.531) | 0.707 | 16 / 45 | agrees | loftr+magsac++ | 401.5 |

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

## SAC's own benchmark pair (equatorial, 13.3-13.9°S 25.2°E): Chandrayaan-2 OHRC → LRO NAC `M1350459544RE`

The pair in the problem setters' paper (arXiv:2509.04775, Table 1), cut by `ops/cut_pradan_pairs.py` on a local equirectangular grid: OHRC at ~0.279 m, NAC on a 1.622 m grid (its label resolution 1.61 m; the paper's NAC grid was 1.1179 m, so pixel figures differ in size as well as in kind), same ground. Before cutting, the NAC's corner prior disagreed with the OHRC grid by (+488, +1790) m (4/7 wide-search templates, inverted intensity); the 4 m correction field then fits 276/386 boxes at rms 13.2 m (inverted intensity; `site_geometry/M1350459544RE.json`). Cross-sensor and cross-mission; both panchromatic - NOT multi-modal. The paper reports SuperGlue at 0.62 / 0.57 px (X / Y) on the equatorial pair and that only SuperGlue registered the polar one; its figure is an IN-SAMPLE control-point RMSE per axis, the table above is held-out (matches the fit never saw) - not the same measure. The same in-sample measure for ours follows.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrc_nac_w01` | -13.8508, 25.1865 | 173.5 | 5.814 | 3451 | 3349 | 0.970 | 0.88 | 0.690 (1.120) | 1.004 | 43 / 8 | agrees | loftr+magsac++ | 76.0 |
| `sac_ohrc_nac_w02` | -13.8247, 25.1507 | 173.6 | 5.814 | 3696 | 3389 | 0.917 | 0.84 | 0.874 (1.417) | 1.142 | 48 / 10 | agrees | loftr+magsac++ | 26.9 |
| `sac_ohrc_nac_w03` | -13.7290, 25.1954 | 173.6 | 5.814 | 4601 | 3971 | 0.863 | 0.92 | 1.184 (1.920) | 1.316 | 50 / 5 | agrees | loftr+magsac++ | 19.5 |
| `sac_ohrc_nac_w04` | -13.5113, 25.1507 | 173.7 | 5.814 | 4139 | 3212 | 0.776 | 0.88 | 1.676 (2.718) | 1.599 | 36 / 8 | agrees | loftr+magsac++ | 6.0 |
| `sac_ohrc_nac_w05` | -13.3546, 25.1865 | 173.7 | 5.814 | 4248 | 4041 | 0.951 | 1.00 | 1.119 (1.816) | 1.318 | 53 / 0 | agrees | loftr+magsac++ | 34.8 |
| `sac_ohrc_nac_w06` | -13.3372, 25.1507 | 173.7 | 5.814 | 4346 | 4179 | 0.962 | 1.00 | 1.004 (1.628) | 1.274 | 58 / 0 | agrees | loftr+magsac++ | 36.4 |

In-sample, per axis (SAC's measure): the MAGSAC++ inliers the matcher's H was fitted to, graded under that H. MAGSAC++ keeps only matches within 3 px, so this can only flatter; it is here for comparison with the paper, never as our accuracy.

| pair | inliers graded | RMSE X px (m) | RMSE Y px (m) | verdict |
|---|---|---|---|---|
| `sac_ohrc_nac_w01` | 3349 | 0.656 (1.063) | 0.730 (1.183) | agrees |
| `sac_ohrc_nac_w02` | 3374 | 0.756 (1.225) | 0.792 (1.285) | agrees |
| `sac_ohrc_nac_w03` | 3972 | 0.799 (1.295) | 1.071 (1.737) | agrees |
| `sac_ohrc_nac_w04` | 3219 | 1.146 (1.858) | 1.014 (1.645) | agrees |
| `sac_ohrc_nac_w05` | 4041 | 0.793 (1.287) | 1.063 (1.724) | agrees |
| `sac_ohrc_nac_w06` | 4182 | 0.773 (1.254) | 0.971 (1.575) | agrees |

## SAC's own benchmark pair (equatorial, re-cut on the paper's 1.1179 m grid): Chandrayaan-2 OHRC → LRO NAC `M1350459544RE`

The pair in the problem setters' paper (arXiv:2509.04775, Table 1), cut by `ops/cut_pradan_pairs.py` on a local equirectangular grid: OHRC at ~0.279 m, NAC resampled to 1.1179 m, the grid the paper measured this pair on (the NAC's own label resolution is 1.61 m), windows centred where the frozen 1.622 m windows are (their inner 715 m); pixel figures are the same size as the paper's, held-out and in-sample still differ in kind, same ground. Before cutting, the NAC's corner prior disagreed with the OHRC grid by (+488, +1790) m (4/7 wide-search templates, inverted intensity); the 4 m correction field then fits 276/386 boxes at rms 13.2 m (inverted intensity; `site_geometry/M1350459544RE.json`). Cross-sensor and cross-mission; both panchromatic - NOT multi-modal. The paper reports SuperGlue at 0.62 / 0.57 px (X / Y) on the equatorial pair and that only SuperGlue registered the polar one; its figure is an IN-SAMPLE control-point RMSE per axis, the table above is held-out (matches the fit never saw) - not the same measure. The same in-sample measure for ours follows.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrc_nac112_w01` | -13.8508, 25.1865 | 173.5 | 4.007 | 3073 | 2857 | 0.930 | 0.78 | 0.859 (0.960) | 1.096 | 41 / 14 | agrees | loftr+magsac++ | 76.1 |
| `sac_ohrc_nac112_w02` | -13.8247, 25.1507 | 173.6 | 4.007 | 3813 | 3272 | 0.858 | 0.89 | 1.068 (1.194) | 1.250 | 48 / 9 | agrees | loftr+magsac++ | 27.6 |
| `sac_ohrc_nac112_w03` | -13.7290, 25.1954 | 173.6 | 4.007 | 4422 | 3997 | 0.904 | 0.97 | 0.899 (1.005) | 1.148 | 48 / 3 | agrees | loftr+magsac++ | 21.4 |
| `sac_ohrc_nac112_w04` | -13.5113, 25.1507 | 173.7 | 4.007 | 4083 | 3048 | 0.747 | 0.89 | 1.599 (1.788) | 1.525 | 40 / 13 | agrees | loftr+magsac++ | 6.4 |
| `sac_ohrc_nac112_w05` | -13.3546, 25.1865 | 173.7 | 4.007 | 3658 | 3401 | 0.930 | 1.00 | 1.068 (1.194) | 1.278 | 53 / 0 | agrees | loftr+magsac++ | 35.4 |
| `sac_ohrc_nac112_w06` | -13.3372, 25.1507 | 173.7 | 4.007 | 4041 | 3812 | 0.943 | 1.00 | 1.139 (1.273) | 1.350 | 57 / 0 | agrees | loftr+magsac++ | 34.7 |

In-sample, per axis (SAC's measure): the MAGSAC++ inliers the matcher's H was fitted to, graded under that H. MAGSAC++ keeps only matches within 3 px, so this can only flatter; it is here for comparison with the paper, never as our accuracy.

| pair | inliers graded | RMSE X px (m) | RMSE Y px (m) | verdict |
|---|---|---|---|---|
| `sac_ohrc_nac112_w01` | 2853 | 0.715 (0.799) | 0.782 (0.874) | agrees |
| `sac_ohrc_nac112_w02` | 3224 | 0.744 (0.832) | 0.830 (0.927) | agrees |
| `sac_ohrc_nac112_w03` | 3886 | 0.783 (0.875) | 0.809 (0.904) | agrees |
| `sac_ohrc_nac112_w04` | 3144 | 1.014 (1.134) | 0.912 (1.019) | agrees |
| `sac_ohrc_nac112_w05` | 3402 | 0.784 (0.877) | 0.986 (1.102) | agrees |
| `sac_ohrc_nac112_w06` | 3809 | 0.904 (1.010) | 1.029 (1.151) | agrees |

## SAC's own benchmark pair (polar, 61.6-62.3°S 56.6°E): Chandrayaan-2 OHRC → LRO NAC `M165491149RE`

The pair in the problem setters' paper (arXiv:2509.04775, Table 1), cut by `ops/cut_pradan_pairs.py` on a local equirectangular grid: OHRC at ~0.275 m, NAC on a 1.215 m grid (its label resolution 1.22 m; the paper's NAC grid was 0.88779 m, so pixel figures differ in size as well as in kind), same ground. Before cutting, the NAC's corner prior disagreed with the OHRC grid by (-48, -76) m (4/7 wide-search templates, inverted intensity); the 4 m correction field then fits 169/177 boxes at rms 10.4 m (inverted intensity; `site_geometry/M165491149RE.json`). Cross-sensor and cross-mission; both panchromatic - NOT multi-modal. The paper reports SuperGlue at 0.62 / 0.57 px (X / Y) on the equatorial pair and that only SuperGlue registered the polar one; its figure is an IN-SAMPLE control-point RMSE per axis, the table above is held-out (matches the fit never saw) - not the same measure. The same in-sample measure for ours follows.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_polar_ohrc_nac_w01` | -61.6397, 56.6354 | 132.3 | 4.418 | 451 | 161 | 0.357 | 0.50 | 4.499 (5.466) | 1.739 | 5 / 31 | agrees | loftr+magsac++ | 11.0 |
| `sac_polar_ohrc_nac_w02` | -61.9500, 56.6354 | 132.2 | 4.418 | 1062 | 697 | 0.656 | 0.84 | 2.383 (2.895) | 1.846 | 25 / 11 | agrees | loftr+magsac++ | 8.4 |
| `sac_polar_ohrc_nac_w03` | -62.2732, 56.6905 | 132.2 | 4.418 | 631 | 314 | 0.498 | 0.67 | 2.789 (3.388) | 1.567 | 16 / 21 | agrees | loftr+magsac++ | 13.9 |
| `sac_polar_ohrc_nac_w04` | -61.9952, 56.6492 | 132.2 | 4.418 | 897 | 511 | 0.570 | 0.80 | 2.444 (2.969) | 1.669 | 23 / 13 | agrees | loftr+magsac++ | 34.9 |
| `sac_polar_ohrc_nac_w05` | -62.1762, 56.6630 | 132.2 | 4.418 | 433 | 161 | 0.372 | 0.53 | 4.048 (4.918) | 1.730 | 11 / 31 | unconfirmed | loftr+magsac++ | 8.0 |
| `sac_polar_ohrc_nac_w06` | -62.0534, 56.6630 | 132.2 | 4.418 | 242 | 78 | 0.322 | 0.27 | 88.541 (107.577) | 1.873 | 0 / 45 | contradicted | fft_phase_correlation (fallback) | 16.2 |

In-sample, per axis (SAC's measure): the MAGSAC++ inliers the matcher's H was fitted to, graded under that H. MAGSAC++ keeps only matches within 3 px, so this can only flatter; it is here for comparison with the paper, never as our accuracy.

| pair | inliers graded | RMSE X px (m) | RMSE Y px (m) | verdict |
|---|---|---|---|---|
| `sac_polar_ohrc_nac_w01` | 161 | 1.243 (1.511) | 1.409 (1.711) | agrees |
| `sac_polar_ohrc_nac_w02` | 682 | 1.043 (1.268) | 1.285 (1.562) | agrees |
| `sac_polar_ohrc_nac_w03` | 314 | 1.225 (1.489) | 1.238 (1.504) | agrees |
| `sac_polar_ohrc_nac_w04` | 514 | 0.985 (1.197) | 1.371 (1.666) | agrees |
| `sac_polar_ohrc_nac_w05` | 165 | 1.219 (1.481) | 1.175 (1.428) | unconfirmed |
| `sac_polar_ohrc_nac_w06` | 80 | 0.923 (1.121) | 1.157 (1.406) | contradicted |

## SAC's benchmark site: Chandrayaan-2 OHRC → TMC-2 nadir, pass 20250707T1853 (cross-sensor, same mission)

OHRC frame `ch2_ohr_ncp_20210401T2357376656_d_img_d18` (arXiv:2509.04775, Table 1), 13.1-13.9°S 25.2°E, vs TMC-2 pass `ch2_tmc_ncn_20250707T1853051045_d_img_d18` (`ops/cut_pradan_pairs.py`). OHRC area-averaged 4×4 (~1.114 m) before resampling; TMC-2 ~5.576 m. Label sun: OHRC elevation 9.9°, TMC-2 69.4°, azimuths 120.2° apart, incidence 59.4° apart (`d_incidence_deg` -59.44). Both panchromatic - NOT multi-modal; same mission - NOT cross-mission.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrc_tmc_w01` | -13.1565, 25.1892 | 120.2 | 5.005 | 90 | 6 | 0.067 | 0.06 | 170.058 (948.245) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 242.7 |
| `sac_ohrc_tmc_w02` | -13.3669, 25.1880 | 120.2 | 5.005 | 105 | 6 | 0.057 | 0.09 | 112.891 (629.481) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 70.3 |
| `sac_ohrc_tmc_w03` | -13.5773, 25.1869 | 120.2 | 5.005 | 96 | 7 | 0.073 | 0.06 | 268.087 (1494.851) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 1360.3 |
| `sac_ohrc_tmc_w04` | -13.7877, 25.1857 | 120.2 | 5.005 | 148 | 7 | 0.047 | 0.05 | 124.811 (695.948) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 933.8 |

In-sample, per axis, on the inliers the matcher's H was fitted to - and the share of HELD-OUT matches (the 20 % the fit never saw) that land within 3 px of that H. MAGSAC++ keeps only matches within 3 px, so the in-sample column can only flatter: a sub-pixel fit on six points is what a refused registration looks like from the inside, and the held-out column is why it was refused.

| pair | inliers graded | RMSE X px (m) | RMSE Y px (m) | held-out within 3 px | verdict |
|---|---|---|---|---|---|
| `sac_ohrc_tmc_w01` | 7 | 0.715 (3.988) | 0.926 (5.162) | 0% | contradicted |
| `sac_ohrc_tmc_w02` | 6 | 0.336 (1.871) | 0.860 (4.794) | 0% | contradicted |
| `sac_ohrc_tmc_w03` | 7 | 0.880 (4.906) | 0.128 (0.717) | 0% | contradicted |
| `sac_ohrc_tmc_w04` | 7 | 0.962 (5.366) | 0.700 (3.903) | 0% | contradicted |

## Sun azimuth and elevation, on SAC's own frame: OHRC → LRO NAC under many Suns

SAC's OHRC frame `ch2_ohr_ncp_20210401T2357376656_d_img_d18` (arXiv:2509.04775, Table 1; label Sun elevation 9.9°, azimuth 270.9°) against 16 LRO NACs chosen for their Sun alone (`ops/cut_chain_pairs.py ohrc-nac-lro`; WUSTL ODE footprints). Both images are placed in LRO's geometry with no image content of the pair: the OHRC moved by (+519, +1821) m by SAC's NAC correction, every NAC by LROC's published corners. One reference grid for every NAC (1.75 m: each NAC area-averaged by a whole factor first), one set of 18 candidate windows on the OHRC frame's centre line (1.12 km), each NAC using the ones it covers. Cross-sensor, cross-mission; both panchromatic - NOT multi-modal. Sun of the NAC computed at each window from LROC's sub-solar point; of the OHRC from its label. Held-out medians are quoted only for accepted windows whose inlier ratio is above 0.5 (`_residual_caveat`). The archive offset is the disagreement between LROC's published corners (~0.01°) and the OHRC moved into LRO's geometry - a few hundred metres - not an accuracy.

### Sun azimuth near the OHRC's, elevation raised

| NAC | Sun elevation at the windows | Δ elevation | Δ azimuth | NAC emission | windows | verdicts | inliers | held-out median px (m) on the 1.75 m grid, accepted | verified cells /64 | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|
| `M1468925984LE` | 8.4° | -1.5° | 1.7-1.8° | 15.4° | 8 | agrees 7, contradicted 1 | 6-2700 | 0.76-2.19 (1.3-3.8 m) | 0-33 | 24-491 |
| `M1382142111LE` | 10.6-10.7° | +0.7° | 3.0° | 9.8° | 7 | agrees 6, unconfirmed 1 | 882-4573 | 0.62-1.04 (1.1-1.8 m) | 24-52 | 118-211 |
| `M1188200376RE` | 17.2° | +7.3° | 1.7-1.8° | 1.1° | 8 | agrees 8 | 376-4688 | 0.85-2.24 (1.5-3.9 m) | 17-56 | 23-150 |
| `M1249388815RE` | 24.1-24.2° | +14.2° | 3.3-3.6° | 16.1° | 8 | agrees 7, unconfirmed 1 | 168-2514 | 1.01-1.63 (1.8-2.8 m); 1 not quoted | 11-33 | 199-651 |
| `M1527456612LE` | 29.2-29.3° | +19.3 to +19.4° | 7.1-7.3° | 1.7° | 8 | agrees 7, unconfirmed 1 | 1585-4131 | 0.78-1.20 (1.4-2.1 m) | 31-50 | 82-130 |
| `M1295221357RE` | 32.9-33.0° | +22.9 to +23.1° | 9.6-10.0° | 1.1° | 8 | agrees 7, unconfirmed 1 | 301-3710 | 0.83-1.49 (1.4-2.6 m) | 15-51 | 39-210 |
| `M1236436979LE` | 47.5-47.6° | +37.6 to +37.7° | 16.0-16.4° | 13.7° | 8 | agrees 4, unconfirmed 3, contradicted 1 | 15-1149 | 1.56-2.02 (2.7-3.5 m) | 0-33 | 143-372 |
| `M1236429945LE` | 48.3-48.5° | +38.4 to +38.6° | 16.6-17.3° | 9.5° | 8 | agrees 8 | 88-2855 | 0.76-1.42 (1.3-2.5 m); 1 not quoted | 8-53 | 110-216 |
| `M1356313970LE` | 51.4-51.7° | +41.5 to +41.8° | 18.8-19.7° | 1.7° | 8 | agrees 7, unconfirmed 1 | 28-2486 | 1.20-1.91 (2.1-3.3 m) | 1-50 | 13-206 |

9 NACs, 71 windows: agrees 61, unconfirmed 8, contradicted 2. Highest Sun (`M1356313970LE`, +41.7° in elevation, 19.2° in azimuth): agrees 7, unconfirmed 1. Held-out median of the accepted windows with inlier ratio above 0.5: median 1.20 px = 2.09 m on the 1.75 m grid (59 windows).

### Sun azimuth opposite the OHRC's, at several elevations

| NAC | Sun elevation at the windows | Δ elevation | Δ azimuth | NAC emission | windows | verdicts | inliers | held-out median px (m) on the 1.75 m grid, accepted | verified cells /64 | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|
| `M1467772940RE` | 8.3° | -1.6° | 176.8° | 6.1° | 8 | agrees 7, unconfirmed 1 | 288-2301 | 0.87-2.07 (1.5-3.6 m) | 13-46 | 95-281 |
| `M1350459544RE` | 17.9° | +8.0° | 173.5-173.7° | 1.2° | 8 | agrees 7, unconfirmed 1 | 1943-4930 | 0.67-1.16 (1.2-2.0 m) | 26-57 | 6-129 |
| `M1335172151RE` | 19.7° | +9.8° | 175.0-175.2° | 1.2° | 8 | agrees 8 | 2346-4342 | 0.70-1.41 (1.2-2.5 m) | 40-53 | 33-171 |
| `M1508738205RE` | 30.1-30.2° | +20.2 to +20.3° | 169.8-170.1° | 6.3° | 8 | agrees 7, unconfirmed 1 | 55-2650 | 1.09-1.97 (1.9-3.5 m) | 6-43 | 157-314 |
| `M1378641884LE` | 32.6-32.8° | +22.7 to +22.9° | 169.5-169.9° | 1.7° | 8 | agrees 7, unconfirmed 1 | 71-3516 | 0.92-1.80 (1.6-3.2 m) | 3-52 | 56-263 |
| `M1258792259LE` | 43.8-43.9° | +33.9 to +34.0° | 164.9-165.2° | 1.7° | 8 | agrees 8 | 234-1971 | 0.99-3.17 (1.7-5.5 m) | 15-41 | 197-237 |
| `M1506397068RE` | 56.8-57.1° | +46.9 to +47.2° | 154.2-155.2° | 5.8° | 8 | agrees 4, unconfirmed 1, contradicted 3 | 6-504 | 2.04 (3.6 m); 3 not quoted | 0-24 | 154-561 |

7 NACs, 56 windows: agrees 48, unconfirmed 5, contradicted 3. Highest Sun (`M1506397068RE`, +47.0° in elevation, 154.7° in azimuth): agrees 4, contradicted 3, unconfirmed 1. Held-out median of the accepted windows with inlier ratio above 0.5: median 1.19 px = 2.08 m on the 1.75 m grid (45 windows).

#### OHRC → NAC `M1468925984LE` (Sun -1.5° in elevation, 2° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1468925984le_c00` | -13.0170, 25.2072 | 1.7 | 1.571 | 2550 | 2258 | 0.885 | 0.72 | 1.637 (2.864) | 1.695 | 33 / 18 | agrees | loftr+magsac++ | 271.1 |
| `sac_ohrclroc_nacm1468925984le_c01` | -13.0634, 25.2069 | 1.7 | 1.571 | 1871 | 1286 | 0.687 | 0.56 | 1.923 (3.365) | 1.597 | 21 / 27 | agrees | loftr+magsac++ | 266.0 |
| `sac_ohrclroc_nacm1468925984le_c03` | -13.1564, 25.2064 | 1.7 | 1.571 | 135 | 6 | 0.044 | 0.06 | 164.354 (287.619) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 24.4 |
| `sac_ohrclroc_nacm1468925984le_c04` | -13.2029, 25.2062 | 1.7 | 1.571 | 3507 | 2190 | 0.624 | 0.62 | 2.191 (3.834) | 1.592 | 26 / 24 | agrees | loftr+magsac++ | 264.3 |
| `sac_ohrclroc_nacm1468925984le_c06` | -13.2959, 25.2057 | 1.7 | 1.571 | 2963 | 2700 | 0.911 | 0.67 | 1.474 (2.579) | 1.589 | 32 / 21 | agrees | loftr+magsac++ | 326.2 |
| `sac_ohrclroc_nacm1468925984le_c07` | -13.3424, 25.2054 | 1.7 | 1.571 | 2880 | 2648 | 0.919 | 0.64 | 0.758 (1.326) | 0.998 | 32 / 23 | agrees | loftr+magsac++ | 388.6 |
| `sac_ohrclroc_nacm1468925984le_c09` | -13.4353, 25.2049 | 1.7 | 1.571 | 1047 | 848 | 0.810 | 0.45 | 1.142 (1.998) | 1.256 | 25 / 35 | agrees | loftr+magsac++ | 458.0 |
| `sac_ohrclroc_nacm1468925984le_c10` | -13.4818, 25.2047 | 1.8 | 1.571 | 278 | 151 | 0.543 | 0.27 | 1.482 (2.594) | 1.060 | 14 / 47 | agrees | loftr+magsac++ | 490.8 |

#### OHRC → NAC `M1382142111LE` (Sun +0.7° in elevation, 3° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1382142111le_c00` | -13.0170, 25.2072 | 3.0 | 1.571 | 3866 | 3749 | 0.970 | 0.88 | 0.622 (1.089) | 0.913 | 46 / 8 | agrees | loftr+magsac++ | 203.9 |
| `sac_ohrclroc_nacm1382142111le_c01` | -13.0634, 25.2069 | 3.0 | 1.571 | 3745 | 3575 | 0.955 | 0.88 | 0.892 (1.561) | 1.198 | 50 / 8 | agrees | loftr+magsac++ | 178.0 |
| `sac_ohrclroc_nacm1382142111le_c02` | -13.1099, 25.2067 | 3.0 | 1.571 | 2227 | 2059 | 0.925 | 0.66 | 0.743 (1.301) | 0.973 | 38 / 22 | agrees | loftr+magsac++ | 171.4 |
| `sac_ohrclroc_nacm1382142111le_c03` | -13.1564, 25.2064 | 3.0 | 1.571 | 1069 | 882 | 0.825 | 0.50 | 0.905 (1.584) | 1.120 | 24 / 32 | unconfirmed | loftr+magsac++ | 199.3 |
| `sac_ohrclroc_nacm1382142111le_c04` | -13.2029, 25.2062 | 3.0 | 1.571 | 4048 | 3678 | 0.909 | 0.83 | 0.917 (1.605) | 1.121 | 47 / 11 | agrees | loftr+magsac++ | 210.9 |
| `sac_ohrclroc_nacm1382142111le_c05` | -13.2494, 25.2059 | 3.0 | 1.571 | 4058 | 3982 | 0.981 | 0.88 | 0.754 (1.320) | 1.071 | 50 / 8 | agrees | loftr+magsac++ | 166.3 |
| `sac_ohrclroc_nacm1382142111le_c06` | -13.2959, 25.2057 | 3.0 | 1.571 | 4629 | 4573 | 0.988 | 0.97 | 1.045 (1.828) | 1.272 | 52 / 2 | agrees | loftr+magsac++ | 117.7 |

#### OHRC → NAC `M1188200376RE` (Sun +7.3° in elevation, 2° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1188200376re_c00` | -13.0170, 25.2072 | 1.7 | 1.571 | 3178 | 3088 | 0.972 | 0.81 | 0.967 (1.692) | 1.109 | 46 / 12 | agrees | loftr+magsac++ | 126.3 |
| `sac_ohrclroc_nacm1188200376re_c01` | -13.0634, 25.2069 | 1.7 | 1.571 | 3258 | 2877 | 0.883 | 0.92 | 1.019 (1.783) | 1.185 | 44 / 6 | agrees | loftr+magsac++ | 95.1 |
| `sac_ohrclroc_nacm1188200376re_c03` | -13.1564, 25.2064 | 1.7 | 1.571 | 628 | 376 | 0.599 | 0.52 | 2.236 (3.912) | 1.150 | 17 / 31 | agrees | loftr+magsac++ | 132.5 |
| `sac_ohrclroc_nacm1188200376re_c04` | -13.2029, 25.2062 | 1.7 | 1.571 | 4018 | 3537 | 0.880 | 0.81 | 1.257 (2.199) | 1.424 | 40 / 10 | agrees | loftr+magsac++ | 149.7 |
| `sac_ohrclroc_nacm1188200376re_c06` | -13.2959, 25.2057 | 1.7 | 1.571 | 4625 | 4464 | 0.965 | 1.00 | 1.202 (2.103) | 1.393 | 49 / 0 | agrees | loftr+magsac++ | 40.6 |
| `sac_ohrclroc_nacm1188200376re_c07` | -13.3424, 25.2054 | 1.8 | 1.571 | 4907 | 4688 | 0.955 | 1.00 | 0.851 (1.489) | 1.139 | 56 / 0 | agrees | loftr+magsac++ | 23.1 |
| `sac_ohrclroc_nacm1188200376re_c09` | -13.4353, 25.2049 | 1.8 | 1.571 | 3402 | 3156 | 0.928 | 0.91 | 1.168 (2.044) | 1.335 | 45 / 6 | agrees | loftr+magsac++ | 41.0 |
| `sac_ohrclroc_nacm1188200376re_c10` | -13.4818, 25.2047 | 1.8 | 1.571 | 2881 | 2720 | 0.944 | 0.88 | 0.911 (1.595) | 1.120 | 43 / 8 | agrees | loftr+magsac++ | 52.7 |

#### OHRC → NAC `M1249388815RE` (Sun +14.2° in elevation, 3° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1249388815re_c02` | -13.1099, 25.2067 | 3.3 | 1.571 | 369 | 168 | 0.455 | 0.33 | 5.618 (9.832) | 1.370 | 11 / 43 | agrees | loftr+magsac++ | 199.2 |
| `sac_ohrclroc_nacm1249388815re_c04` | -13.2029, 25.2062 | 3.3 | 1.571 | 3791 | 2153 | 0.568 | 0.72 | 2.486 (4.350) | 1.652 | 24 / 20 | unconfirmed | loftr+magsac++ | 212.6 |
| `sac_ohrclroc_nacm1249388815re_c06` | -13.2959, 25.2057 | 3.4 | 1.571 | 2905 | 2514 | 0.865 | 0.78 | 1.627 (2.848) | 1.685 | 33 / 14 | agrees | loftr+magsac++ | 262.8 |
| `sac_ohrclroc_nacm1249388815re_c08` | -13.3888, 25.2052 | 3.4 | 1.571 | 2587 | 2362 | 0.913 | 0.64 | 1.541 (2.696) | 1.655 | 28 / 23 | agrees | loftr+magsac++ | 389.4 |
| `sac_ohrclroc_nacm1249388815re_c11` | -13.5283, 25.2044 | 3.5 | 1.571 | 632 | 436 | 0.690 | 0.20 | 1.008 (1.765) | 0.917 | 13 / 51 | agrees | loftr+magsac++ | 542.5 |
| `sac_ohrclroc_nacm1249388815re_c13` | -13.6213, 25.2039 | 3.5 | 1.571 | 2018 | 1788 | 0.886 | 0.50 | 1.358 (2.377) | 1.496 | 20 / 32 | agrees | loftr+magsac++ | 613.1 |
| `sac_ohrclroc_nacm1249388815re_c15` | -13.7142, 25.2034 | 3.6 | 1.571 | 2093 | 1623 | 0.775 | 0.47 | 1.407 (2.463) | 1.449 | 18 / 34 | agrees | loftr+magsac++ | 651.0 |
| `sac_ohrclroc_nacm1249388815re_c17` | -13.8072, 25.2029 | 3.6 | 1.571 | 2513 | 2227 | 0.886 | 0.59 | 1.175 (2.055) | 1.446 | 28 / 27 | agrees | loftr+magsac++ | 524.3 |

#### OHRC → NAC `M1527456612LE` (Sun +19.3° in elevation, 7° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1527456612le_c09` | -13.4353, 25.2049 | 7.1 | 1.571 | 2278 | 2130 | 0.935 | 0.72 | 1.023 (1.791) | 1.238 | 39 / 18 | agrees | loftr+magsac++ | 128.3 |
| `sac_ohrclroc_nacm1527456612le_c10` | -13.4818, 25.2047 | 7.1 | 1.571 | 1894 | 1759 | 0.929 | 0.69 | 0.777 (1.359) | 1.078 | 38 / 20 | agrees | loftr+magsac++ | 117.6 |
| `sac_ohrclroc_nacm1527456612le_c11` | -13.5283, 25.2044 | 7.1 | 1.571 | 2217 | 2133 | 0.962 | 0.78 | 0.792 (1.386) | 1.000 | 40 / 14 | agrees | loftr+magsac++ | 96.1 |
| `sac_ohrclroc_nacm1527456612le_c12` | -13.5748, 25.2042 | 7.1 | 1.571 | 1694 | 1585 | 0.936 | 0.80 | 1.198 (2.097) | 1.423 | 32 / 13 | agrees | loftr+magsac++ | 87.5 |
| `sac_ohrclroc_nacm1527456612le_c14` | -13.6678, 25.2037 | 7.2 | 1.571 | 3992 | 3035 | 0.760 | 0.84 | 1.625 (2.844) | 1.543 | 31 / 9 | unconfirmed | loftr+magsac++ | 82.3 |
| `sac_ohrclroc_nacm1527456612le_c15` | -13.7142, 25.2034 | 7.2 | 1.571 | 4238 | 4131 | 0.975 | 0.98 | 1.016 (1.778) | 1.245 | 49 / 1 | agrees | loftr+magsac++ | 86.5 |
| `sac_ohrclroc_nacm1527456612le_c16` | -13.7607, 25.2032 | 7.2 | 1.571 | 4217 | 4043 | 0.959 | 0.91 | 0.918 (1.606) | 1.197 | 50 / 6 | agrees | loftr+magsac++ | 104.5 |
| `sac_ohrclroc_nacm1527456612le_c17` | -13.8072, 25.2029 | 7.3 | 1.571 | 3892 | 3570 | 0.917 | 0.86 | 0.803 (1.404) | 1.004 | 49 / 9 | agrees | loftr+magsac++ | 129.7 |

#### OHRC → NAC `M1295221357RE` (Sun +23.0° in elevation, 10° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1295221357re_c00` | -13.0170, 25.2072 | 9.6 | 1.571 | 2231 | 2051 | 0.919 | 0.83 | 1.083 (1.896) | 1.225 | 45 / 11 | agrees | loftr+magsac++ | 210.1 |
| `sac_ohrclroc_nacm1295221357re_c02` | -13.1099, 25.2067 | 9.7 | 1.571 | 427 | 301 | 0.705 | 0.39 | 1.486 (2.600) | 1.390 | 15 / 39 | agrees | loftr+magsac++ | 159.6 |
| `sac_ohrclroc_nacm1295221357re_c04` | -13.2029, 25.2062 | 9.7 | 1.571 | 3282 | 2977 | 0.907 | 0.86 | 1.286 (2.250) | 1.505 | 39 / 9 | agrees | loftr+magsac++ | 199.6 |
| `sac_ohrclroc_nacm1295221357re_c06` | -13.2959, 25.2057 | 9.8 | 1.571 | 3898 | 3707 | 0.951 | 1.00 | 1.195 (2.092) | 1.413 | 51 / 0 | agrees | loftr+magsac++ | 75.8 |
| `sac_ohrclroc_nacm1295221357re_c08` | -13.3888, 25.2052 | 9.9 | 1.571 | 3990 | 3710 | 0.930 | 1.00 | 1.315 (2.300) | 1.523 | 50 / 0 | agrees | loftr+magsac++ | 38.6 |
| `sac_ohrclroc_nacm1295221357re_c10` | -13.4818, 25.2047 | 9.9 | 1.571 | 2149 | 2012 | 0.936 | 0.81 | 0.826 (1.445) | 1.074 | 44 / 12 | agrees | loftr+magsac++ | 59.8 |
| `sac_ohrclroc_nacm1295221357re_c12` | -13.5748, 25.2042 | 10.0 | 1.571 | 1762 | 1660 | 0.942 | 0.61 | 1.108 (1.939) | 1.317 | 31 / 25 | agrees | loftr+magsac++ | 118.6 |
| `sac_ohrclroc_nacm1295221357re_c14` | -13.6678, 25.2037 | 10.0 | 1.571 | 3552 | 2767 | 0.779 | 0.75 | 1.741 (3.047) | 1.586 | 29 / 18 | unconfirmed | loftr+magsac++ | 155.1 |

#### OHRC → NAC `M1236436979LE` (Sun +37.6° in elevation, 16° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1236436979le_c00` | -13.0170, 25.2072 | 16.0 | 1.571 | 1195 | 834 | 0.698 | 0.72 | 2.019 (3.533) | 1.775 | 24 / 18 | agrees | loftr+magsac++ | 145.8 |
| `sac_ohrclroc_nacm1236436979le_c01` | -13.0634, 25.2069 | 16.1 | 1.571 | 1026 | 580 | 0.565 | 0.64 | 2.496 (4.369) | 1.722 | 19 / 25 | unconfirmed | loftr+magsac++ | 159.0 |
| `sac_ohrclroc_nacm1236436979le_c02` | -13.1099, 25.2067 | 16.1 | 1.571 | 211 | 15 | 0.071 | 0.05 | 220.609 (386.065) | 1.824 | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 167.6 |
| `sac_ohrclroc_nacm1236436979le_c03` | -13.1564, 25.2064 | 16.2 | 1.571 | 317 | 74 | 0.233 | 0.30 | 86.569 (151.496) | 1.630 | 3 / 46 | unconfirmed | loftr+magsac++ | 142.7 |
| `sac_ohrclroc_nacm1236436979le_c05` | -13.2494, 25.2059 | 16.3 | 1.571 | 1773 | 1149 | 0.648 | 0.72 | 2.309 (4.041) | 1.768 | 25 / 13 | unconfirmed | loftr+magsac++ | 165.7 |
| `sac_ohrclroc_nacm1236436979le_c06` | -13.2959, 25.2057 | 16.3 | 1.571 | 1325 | 969 | 0.731 | 0.80 | 1.865 (3.264) | 1.609 | 33 / 13 | agrees | loftr+magsac++ | 252.9 |
| `sac_ohrclroc_nacm1236436979le_c07` | -13.3424, 25.2054 | 16.4 | 1.571 | 1267 | 968 | 0.764 | 0.66 | 1.563 (2.735) | 1.460 | 33 / 22 | agrees | loftr+magsac++ | 328.4 |
| `sac_ohrclroc_nacm1236436979le_c08` | -13.3888, 25.2052 | 16.4 | 1.571 | 1310 | 984 | 0.751 | 0.64 | 1.774 (3.105) | 1.636 | 26 / 23 | agrees | loftr+magsac++ | 372.2 |

#### OHRC → NAC `M1236429945LE` (Sun +38.5° in elevation, 17° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1236429945le_c00` | -13.0170, 25.2072 | 16.6 | 1.571 | 1799 | 1647 | 0.916 | 0.72 | 0.763 (1.336) | 1.081 | 45 / 18 | agrees | loftr+magsac++ | 206.8 |
| `sac_ohrclroc_nacm1236429945le_c02` | -13.1099, 25.2067 | 16.7 | 1.571 | 225 | 88 | 0.391 | 0.28 | 117.731 (206.029) | 1.124 | 8 / 46 | agrees | loftr+magsac++ | 175.4 |
| `sac_ohrclroc_nacm1236429945le_c04` | -13.2029, 25.2062 | 16.8 | 1.571 | 1883 | 1495 | 0.794 | 0.73 | 1.238 (2.166) | 1.351 | 43 / 16 | agrees | loftr+magsac++ | 216.1 |
| `sac_ohrclroc_nacm1236429945le_c06` | -13.2959, 25.2057 | 16.9 | 1.571 | 2714 | 2518 | 0.928 | 0.89 | 1.112 (1.947) | 1.335 | 49 / 7 | agrees | loftr+magsac++ | 140.0 |
| `sac_ohrclroc_nacm1236429945le_c08` | -13.3888, 25.2052 | 17.0 | 1.571 | 3010 | 2855 | 0.949 | 0.94 | 0.880 (1.541) | 1.101 | 53 / 4 | agrees | loftr+magsac++ | 110.6 |
| `sac_ohrclroc_nacm1236429945le_c10` | -13.4818, 25.2047 | 17.1 | 1.571 | 1706 | 1529 | 0.896 | 0.72 | 0.792 (1.386) | 1.089 | 36 / 18 | agrees | loftr+magsac++ | 109.5 |
| `sac_ohrclroc_nacm1236429945le_c12` | -13.5748, 25.2042 | 17.2 | 1.571 | 1308 | 1200 | 0.917 | 0.64 | 1.027 (1.797) | 1.234 | 33 / 25 | agrees | loftr+magsac++ | 112.9 |
| `sac_ohrclroc_nacm1236429945le_c14` | -13.6678, 25.2037 | 17.3 | 1.571 | 2006 | 1578 | 0.787 | 0.73 | 1.422 (2.489) | 1.414 | 31 / 11 | agrees | loftr+magsac++ | 125.6 |

#### OHRC → NAC `M1356313970LE` (Sun +41.7° in elevation, 19° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1356313970le_c01` | -13.0634, 25.2069 | 18.8 | 1.571 | 1035 | 788 | 0.761 | 0.66 | 1.202 (2.104) | 1.294 | 32 / 22 | agrees | loftr+magsac++ | 193.3 |
| `sac_ohrclroc_nacm1356313970le_c03` | -13.1564, 25.2064 | 18.9 | 1.571 | 278 | 28 | 0.101 | 0.19 | 137.518 (240.657) | 0.956 | 1 / 50 | unconfirmed | loftr+magsac++ | 206.0 |
| `sac_ohrclroc_nacm1356313970le_c06` | -13.2959, 25.2057 | 19.1 | 1.571 | 2261 | 1991 | 0.881 | 0.98 | 1.294 (2.265) | 1.394 | 45 / 1 | agrees | loftr+magsac++ | 105.1 |
| `sac_ohrclroc_nacm1356313970le_c08` | -13.3888, 25.2052 | 19.2 | 1.571 | 2924 | 2486 | 0.850 | 0.95 | 1.257 (2.199) | 1.423 | 48 / 1 | agrees | loftr+magsac++ | 35.5 |
| `sac_ohrclroc_nacm1356313970le_c10` | -13.4818, 25.2047 | 19.3 | 1.571 | 1115 | 892 | 0.800 | 0.78 | 1.319 (2.308) | 1.346 | 31 / 14 | agrees | loftr+magsac++ | 12.6 |
| `sac_ohrclroc_nacm1356313970le_c12` | -13.5748, 25.2042 | 19.4 | 1.571 | 562 | 391 | 0.696 | 0.66 | 1.910 (3.343) | 1.677 | 24 / 22 | agrees | loftr+magsac++ | 52.6 |
| `sac_ohrclroc_nacm1356313970le_c15` | -13.7142, 25.2034 | 19.6 | 1.571 | 2054 | 1768 | 0.861 | 0.98 | 1.403 (2.455) | 1.483 | 45 / 1 | agrees | loftr+magsac++ | 76.0 |
| `sac_ohrclroc_nacm1356313970le_c17` | -13.8072, 25.2029 | 19.7 | 1.571 | 2343 | 1989 | 0.849 | 0.97 | 1.263 (2.210) | 1.420 | 50 / 2 | agrees | loftr+magsac++ | 36.3 |

#### OHRC → NAC `M1467772940RE` (Sun -1.6° in elevation, 177° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1467772940re_c00` | -13.0170, 25.2072 | 176.8 | 1.571 | 2464 | 2195 | 0.891 | 0.88 | 1.433 (2.508) | 1.511 | 46 / 8 | agrees | loftr+magsac++ | 115.7 |
| `sac_ohrclroc_nacm1467772940re_c02` | -13.1099, 25.2067 | 176.8 | 1.571 | 486 | 288 | 0.593 | 0.34 | 2.011 (3.520) | 1.601 | 13 / 45 | unconfirmed | loftr+magsac++ | 95.4 |
| `sac_ohrclroc_nacm1467772940re_c03` | -13.1564, 25.2064 | 176.8 | 1.571 | 744 | 500 | 0.672 | 0.70 | 2.067 (3.617) | 1.636 | 23 / 19 | agrees | loftr+magsac++ | 124.8 |
| `sac_ohrclroc_nacm1467772940re_c05` | -13.2494, 25.2059 | 176.8 | 1.571 | 2698 | 2301 | 0.853 | 0.89 | 1.787 (3.127) | 1.734 | 38 / 7 | agrees | loftr+magsac++ | 125.8 |
| `sac_ohrclroc_nacm1467772940re_c06` | -13.2959, 25.2057 | 176.8 | 1.571 | 1171 | 970 | 0.828 | 0.66 | 1.090 (1.907) | 1.285 | 26 / 22 | agrees | loftr+magsac++ | 146.3 |
| `sac_ohrclroc_nacm1467772940re_c08` | -13.3888, 25.2052 | 176.8 | 1.571 | 2448 | 2187 | 0.893 | 0.88 | 1.304 (2.281) | 1.401 | 42 / 8 | agrees | loftr+magsac++ | 214.1 |
| `sac_ohrclroc_nacm1467772940re_c09` | -13.4353, 25.2049 | 176.8 | 1.571 | 1390 | 1170 | 0.842 | 0.66 | 0.913 (1.598) | 1.115 | 34 / 22 | agrees | loftr+magsac++ | 229.5 |
| `sac_ohrclroc_nacm1467772940re_c11` | -13.5283, 25.2044 | 176.8 | 1.571 | 978 | 825 | 0.844 | 0.58 | 0.870 (1.522) | 1.062 | 31 / 27 | agrees | loftr+magsac++ | 281.0 |

#### OHRC → NAC `M1350459544RE` (Sun +8.0° in elevation, 174° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1350459544re_c05` | -13.2494, 25.2059 | 173.7 | 1.571 | 3917 | 3712 | 0.948 | 0.94 | 1.134 (1.985) | 1.372 | 44 / 4 | agrees | loftr+magsac++ | 128.7 |
| `sac_ohrclroc_nacm1350459544re_c07` | -13.3424, 25.2054 | 173.7 | 1.571 | 4803 | 4601 | 0.958 | 1.00 | 0.673 (1.178) | 0.992 | 56 / 0 | agrees | loftr+magsac++ | 23.1 |
| `sac_ohrclroc_nacm1350459544re_c08` | -13.3888, 25.2052 | 173.7 | 1.571 | 5147 | 4930 | 0.958 | 1.00 | 1.141 (1.997) | 1.368 | 55 / 0 | agrees | loftr+magsac++ | 5.9 |
| `sac_ohrclroc_nacm1350459544re_c10` | -13.4818, 25.2047 | 173.7 | 1.571 | 2709 | 2503 | 0.924 | 0.86 | 0.973 (1.702) | 1.164 | 52 / 9 | agrees | loftr+magsac++ | 27.6 |
| `sac_ohrclroc_nacm1350459544re_c12` | -13.5748, 25.2042 | 173.6 | 1.571 | 2106 | 1943 | 0.923 | 0.86 | 1.163 (2.035) | 1.404 | 38 / 9 | agrees | loftr+magsac++ | 73.6 |
| `sac_ohrclroc_nacm1350459544re_c14` | -13.6678, 25.2037 | 173.6 | 1.571 | 3986 | 2932 | 0.736 | 0.92 | 1.838 (3.216) | 1.692 | 26 / 6 | unconfirmed | loftr+magsac++ | 93.4 |
| `sac_ohrclroc_nacm1350459544re_c15` | -13.7142, 25.2034 | 173.6 | 1.571 | 4589 | 4437 | 0.967 | 1.00 | 1.010 (1.768) | 1.205 | 49 / 0 | agrees | loftr+magsac++ | 87.8 |
| `sac_ohrclroc_nacm1350459544re_c17` | -13.8072, 25.2029 | 173.5 | 1.571 | 4655 | 4518 | 0.971 | 0.97 | 0.769 (1.346) | 0.973 | 57 / 2 | agrees | loftr+magsac++ | 17.5 |

#### OHRC → NAC `M1335172151RE` (Sun +9.8° in elevation, 175° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1335172151re_c04` | -13.2029, 25.2062 | 175.2 | 1.571 | 3666 | 3441 | 0.939 | 0.77 | 1.415 (2.476) | 1.554 | 40 / 16 | agrees | loftr+magsac++ | 171.3 |
| `sac_ohrclroc_nacm1335172151re_c06` | -13.2959, 25.2057 | 175.2 | 1.571 | 4437 | 4271 | 0.963 | 1.00 | 1.031 (1.804) | 1.242 | 52 / 0 | agrees | loftr+magsac++ | 62.3 |
| `sac_ohrclroc_nacm1335172151re_c08` | -13.3888, 25.2052 | 175.1 | 1.571 | 4556 | 4273 | 0.938 | 1.00 | 1.163 (2.036) | 1.383 | 51 / 0 | agrees | loftr+magsac++ | 32.5 |
| `sac_ohrclroc_nacm1335172151re_c10` | -13.4818, 25.2047 | 175.1 | 1.571 | 2923 | 2748 | 0.940 | 0.91 | 0.852 (1.490) | 1.084 | 51 / 6 | agrees | loftr+magsac++ | 54.7 |
| `sac_ohrclroc_nacm1335172151re_c11` | -13.5283, 25.2044 | 175.1 | 1.571 | 2415 | 2346 | 0.971 | 0.81 | 0.881 (1.542) | 1.052 | 44 / 12 | agrees | loftr+magsac++ | 84.1 |
| `sac_ohrclroc_nacm1335172151re_c13` | -13.6213, 25.2039 | 175.1 | 1.571 | 3755 | 3671 | 0.978 | 0.97 | 0.770 (1.348) | 1.032 | 47 / 2 | agrees | loftr+magsac++ | 111.4 |
| `sac_ohrclroc_nacm1335172151re_c15` | -13.7142, 25.2034 | 175.0 | 1.571 | 4432 | 4342 | 0.980 | 0.91 | 1.000 (1.751) | 1.177 | 49 / 6 | agrees | loftr+magsac++ | 123.5 |
| `sac_ohrclroc_nacm1335172151re_c17` | -13.8072, 25.2029 | 175.0 | 1.571 | 4438 | 4316 | 0.973 | 0.95 | 0.699 (1.224) | 0.982 | 53 / 3 | agrees | loftr+magsac++ | 61.8 |

#### OHRC → NAC `M1508738205RE` (Sun +20.3° in elevation, 170° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1508738205re_c00` | -13.0170, 25.2072 | 170.1 | 1.571 | 1308 | 1063 | 0.813 | 0.77 | 1.544 (2.703) | 1.524 | 34 / 15 | agrees | loftr+magsac++ | 243.5 |
| `sac_ohrclroc_nacm1508738205re_c02` | -13.1099, 25.2067 | 170.1 | 1.571 | 188 | 55 | 0.293 | 0.20 | 174.762 (305.834) | 1.253 | 6 / 51 | unconfirmed | loftr+magsac++ | 197.7 |
| `sac_ohrclroc_nacm1508738205re_c04` | -13.2029, 25.2062 | 170.0 | 1.571 | 2310 | 1757 | 0.761 | 0.80 | 1.972 (3.451) | 1.696 | 28 / 14 | agrees | loftr+magsac++ | 224.4 |
| `sac_ohrclroc_nacm1508738205re_c06` | -13.2959, 25.2057 | 169.9 | 1.571 | 2936 | 2650 | 0.903 | 0.83 | 1.440 (2.520) | 1.550 | 41 / 11 | agrees | loftr+magsac++ | 156.9 |
| `sac_ohrclroc_nacm1508738205re_c07` | -13.3424, 25.2054 | 169.9 | 1.571 | 2871 | 2555 | 0.890 | 0.88 | 1.093 (1.912) | 1.270 | 43 / 8 | agrees | loftr+magsac++ | 175.8 |
| `sac_ohrclroc_nacm1508738205re_c09` | -13.4353, 25.2049 | 169.9 | 1.571 | 1093 | 746 | 0.683 | 0.64 | 1.742 (3.048) | 1.516 | 31 / 23 | agrees | loftr+magsac++ | 209.5 |
| `sac_ohrclroc_nacm1508738205re_c11` | -13.5283, 25.2044 | 169.8 | 1.571 | 497 | 347 | 0.698 | 0.52 | 1.312 (2.296) | 1.148 | 22 / 31 | agrees | loftr+magsac++ | 268.4 |
| `sac_ohrclroc_nacm1508738205re_c13` | -13.6213, 25.2039 | 169.8 | 1.571 | 1531 | 1277 | 0.834 | 0.75 | 1.615 (2.826) | 1.633 | 33 / 16 | agrees | loftr+magsac++ | 314.4 |

#### OHRC → NAC `M1378641884LE` (Sun +22.8° in elevation, 170° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1378641884le_c03` | -13.1564, 25.2064 | 169.9 | 1.571 | 292 | 71 | 0.243 | 0.34 | 167.081 (292.391) | 1.142 | 3 / 41 | unconfirmed | loftr+magsac++ | 263.3 |
| `sac_ohrclroc_nacm1378641884le_c05` | -13.2494, 25.2059 | 169.8 | 1.571 | 2676 | 2317 | 0.866 | 0.78 | 1.556 (2.724) | 1.551 | 37 / 14 | agrees | loftr+magsac++ | 206.5 |
| `sac_ohrclroc_nacm1378641884le_c07` | -13.3424, 25.2054 | 169.8 | 1.571 | 3741 | 3516 | 0.940 | 0.97 | 0.981 (1.716) | 1.192 | 52 / 2 | agrees | loftr+magsac++ | 85.9 |
| `sac_ohrclroc_nacm1378641884le_c09` | -13.4353, 25.2049 | 169.7 | 1.571 | 1434 | 1049 | 0.732 | 0.83 | 1.804 (3.157) | 1.617 | 34 / 12 | agrees | loftr+magsac++ | 55.7 |
| `sac_ohrclroc_nacm1378641884le_c11` | -13.5283, 25.2044 | 169.7 | 1.571 | 972 | 849 | 0.873 | 0.72 | 1.142 (1.999) | 1.293 | 39 / 18 | agrees | loftr+magsac++ | 73.8 |
| `sac_ohrclroc_nacm1378641884le_c13` | -13.6213, 25.2039 | 169.6 | 1.571 | 2304 | 2059 | 0.894 | 0.86 | 1.187 (2.077) | 1.358 | 48 / 9 | agrees | loftr+magsac++ | 105.6 |
| `sac_ohrclroc_nacm1378641884le_c15` | -13.7142, 25.2034 | 169.5 | 1.571 | 3556 | 3308 | 0.930 | 0.88 | 1.283 (2.246) | 1.417 | 46 / 8 | agrees | loftr+magsac++ | 123.4 |
| `sac_ohrclroc_nacm1378641884le_c17` | -13.8072, 25.2029 | 169.5 | 1.571 | 3745 | 3442 | 0.919 | 0.97 | 0.916 (1.603) | 1.164 | 50 / 1 | agrees | loftr+magsac++ | 78.0 |

#### OHRC → NAC `M1258792259LE` (Sun +33.9° in elevation, 165° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1258792259le_c10` | -13.4818, 25.2047 | 165.2 | 1.571 | 469 | 253 | 0.539 | 0.47 | 3.167 (5.543) | 1.166 | 17 / 34 | agrees | loftr+magsac++ | 237.4 |
| `sac_ohrclroc_nacm1258792259le_c11` | -13.5283, 25.2044 | 165.2 | 1.571 | 406 | 234 | 0.576 | 0.48 | 2.594 (4.539) | 1.336 | 18 / 33 | agrees | loftr+magsac++ | 236.4 |
| `sac_ohrclroc_nacm1258792259le_c12` | -13.5748, 25.2042 | 165.1 | 1.571 | 416 | 235 | 0.565 | 0.45 | 2.564 (4.487) | 1.555 | 15 / 35 | agrees | loftr+magsac++ | 236.6 |
| `sac_ohrclroc_nacm1258792259le_c13` | -13.6213, 25.2039 | 165.1 | 1.571 | 1852 | 1686 | 0.910 | 0.80 | 1.194 (2.090) | 1.329 | 40 / 13 | agrees | loftr+magsac++ | 235.7 |
| `sac_ohrclroc_nacm1258792259le_c14` | -13.6678, 25.2037 | 165.0 | 1.571 | 1768 | 1288 | 0.729 | 0.70 | 1.753 (3.067) | 1.554 | 28 / 18 | agrees | loftr+magsac++ | 236.4 |
| `sac_ohrclroc_nacm1258792259le_c15` | -13.7142, 25.2034 | 165.0 | 1.571 | 2137 | 1911 | 0.894 | 0.77 | 1.246 (2.180) | 1.438 | 40 / 15 | agrees | loftr+magsac++ | 228.4 |
| `sac_ohrclroc_nacm1258792259le_c16` | -13.7607, 25.2032 | 165.0 | 1.571 | 1787 | 1448 | 0.810 | 0.77 | 1.394 (2.440) | 1.513 | 38 / 15 | agrees | loftr+magsac++ | 207.5 |
| `sac_ohrclroc_nacm1258792259le_c17` | -13.8072, 25.2029 | 164.9 | 1.571 | 2227 | 1971 | 0.885 | 0.77 | 0.987 (1.727) | 1.208 | 41 / 15 | agrees | loftr+magsac++ | 197.1 |

#### OHRC → NAC `M1506397068RE` (Sun +47.0° in elevation, 155° in azimuth), window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_ohrclroc_nacm1506397068re_c00` | -13.0170, 25.2072 | 155.2 | 1.571 | 318 | 72 | 0.226 | 0.23 | 92.890 (162.558) | 1.659 | 0 / 49 | contradicted | fft_phase_correlation (fallback) | 295.6 |
| `sac_ohrclroc_nacm1506397068re_c02` | -13.1099, 25.2067 | 155.0 | 1.571 | 151 | 6 | 0.040 | 0.06 | 263.675 (461.431) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 560.6 |
| `sac_ohrclroc_nacm1506397068re_c04` | -13.2029, 25.2062 | 154.9 | 1.571 | 530 | 203 | 0.383 | 0.52 | 8.543 (14.950) | 1.832 | 8 / 31 | agrees | loftr+magsac++ | 234.8 |
| `sac_ohrclroc_nacm1506397068re_c06` | -13.2959, 25.2057 | 154.8 | 1.571 | 828 | 504 | 0.609 | 0.72 | 2.039 (3.568) | 1.611 | 24 / 18 | agrees | loftr+magsac++ | 157.5 |
| `sac_ohrclroc_nacm1506397068re_c09` | -13.4353, 25.2049 | 154.6 | 1.571 | 326 | 66 | 0.202 | 0.31 | 158.670 (277.673) | 1.783 | 5 / 45 | unconfirmed | loftr+magsac++ | 210.8 |
| `sac_ohrclroc_nacm1506397068re_c11` | -13.5283, 25.2044 | 154.4 | 1.571 | 171 | 9 | 0.053 | 0.05 | 259.512 (454.146) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 153.8 |
| `sac_ohrclroc_nacm1506397068re_c13` | -13.6213, 25.2039 | 154.3 | 1.571 | 291 | 77 | 0.265 | 0.25 | 177.104 (309.932) | 1.355 | 6 / 46 | agrees | loftr+magsac++ | 336.5 |
| `sac_ohrclroc_nacm1506397068re_c15` | -13.7142, 25.2034 | 154.2 | 1.571 | 450 | 180 | 0.400 | 0.45 | 4.230 (7.402) | 1.499 | 12 / 34 | agrees | loftr+magsac++ | 368.4 |

## After the submission: IIRS and TMC-2, and the route between them

First measured after the idea was submitted (28 Sep 2026); these rows were re-run with every other piece of evidence at commit `04ed5f6`. Cut by `ops/cut_chain_pairs.py`; products fetched by `ops/fetch_pradan.py` (members and IIRS bands read out of each PRADAN zip by HTTP range). Three questions the 28 Sep submission left open: does IIRS register onto TMC-2 once the Sun is taken out of the problem; does TMC-2 register onto anything at all; and was OHRC -> TMC-2 refused for the Sun or for something else.

### TMC-2 → IIRS, orbit of 2020-02-03 (cross-sensor, same mission; multi-modal beyond 850 nm) - 1 of 2 orbits

TMC-2 nadir `ch2_tmc_ncn_20200203T1845562233_d_img_m65` against IIRS `ch2_iir_nci_20200203T1845559180_d_img_m65`, the same orbit. IIRS label has no Sun fields; both nadir strips start 0.3 s apart (18:45:56.223300 TMC-2, 18:45:55.918000 IIRS UTC), so the Sun is the same to well under 0.1 deg: difference set to 0 by construction. TMC-2 label: azimuth 73.610046, elevation 48.276148 (strip centre). 8 windows, chosen before any matching by the texture of the IIRS 1555 nm band alone (pre-registered: candidates every 15.0 km along the IIRS centre line within latitude (-60.0, 60.0), fully covered by both, ranked by the IIRS window's texture, best-first at least one window apart (ops/cut_chain_pairs.py docstring)); the same 8 ground windows for every band, so each band row below is 8 registrations of the same 8 places. TMC-2 ~4.556 m against IIRS ~73.85 m (16.209×), 192-px IIRS windows, so every trust cell is 24 px and the per-cell area check runs. TMC-2 records 400-850 nm (its PRADAN payload description); an IIRS band beyond 850 nm is outside anything TMC-2 sees and counts as multi-modal, a band inside it does not. Bands 200, 240 of this cube hold only zeros and were not used.

| IIRS band | modality | windows accepted | matches | inliers | held-out median px (m) on the IIRS grid | verified cells /64 | archive offset m |
|---|---|---|---|---|---|---|---|
| 746 nm | inside TMC-2 passband: NOT multi-modal | 8/8 | 144 to 288 | 122 to 278 | 0.547 to 0.934 (40.4 to 69.0 m) | 19 to 41 | 58.2 to 98.7 |
| 999 nm | infrared: multi-modal | 8/8 | 386 to 400 | 382 to 400 | 0.199 to 0.309 (14.7 to 22.8 m) | 50 to 57 | 67.8 to 84.8 |
| 1555 nm | infrared: multi-modal | 8/8 | 393 to 400 | 391 to 400 | 0.212 to 0.319 (15.6 to 23.6 m) | 50 to 57 | 65.4 to 82.0 |
| 2381 nm | infrared: multi-modal | 8/8 | 341 to 396 | 334 to 396 | 0.307 to 0.416 (22.7 to 30.7 m) | 47 to 55 | 67.8 to 78.0 |
| 3223 nm | infrared: multi-modal | 8/8 | 71 to 260 | 51 to 241 | 0.436 to 1.188 (32.2 to 87.7 m) | 7 to 38 | 55.4 to 88.0 |

The archive offset (how far each registration moved TMC-2 from where the two archives' own grids put it) is 0.75-1.33 IIRS pixels in every band and every window: a steady disagreement between the two instruments' geolocation, which is what a registration is for.

Band against band, summarised (full table below): the MEDIAN disagreement per window, and the worst single point of the 20 × 20 lattice. These are medians and a maximum, not bounds, and they measure consistency between independent registrations, not accuracy.

| band against 1555 nm | windows | median disagreement px (m) | p90 px | worst point px |
|---|---|---|---|---|
| 746 nm | 8 | 0.249 to 0.754 (18.4 to 55.7 m) | 0.49 to 2.25 | 5.06 |
| 999 nm | 8 | 0.044 to 0.068 (3.2 to 5.0 m) | 0.07 to 0.15 | 0.29 |
| 2381 nm | 8 | 0.091 to 0.154 (6.7 to 11.4 m) | 0.16 to 0.31 | 0.50 |
| 3223 nm | 8 | 0.226 to 0.724 (16.7 to 53.5 m) | 0.34 to 2.24 | 3.92 |

**Band against band, same window.** Each IIRS band's declared transform against the 1555 nm one, on the same TMC-2 window and the same IIRS grid (`ops/multimodal_check.py`). Every band was registered on its own - its own LoFTR matches, its own fit - so this compares two independent registrations of one piece of ground. Agreement is consistency, not accuracy; disagreement would prove one of them wrong.

| pair | against | declared (pair / against) | against inliers | disagreement median px (m) | p90 px | max px | fallback NCC | archive offset m (pair / against) |
|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200203_iirs2381_w01` | `chain_tmc20200203_iirs1555_w01` | loftr+magsac++ / loftr+magsac++ | 399 | 0.098 (7.3) | 0.158 | 0.243 | n/a | 76.1 / 78.6 |
| `chain_tmc20200203_iirs2381_w02` | `chain_tmc20200203_iirs1555_w02` | loftr+magsac++ / loftr+magsac++ | 397 | 0.134 (9.9) | 0.207 | 0.273 | n/a | 69.0 / 73.3 |
| `chain_tmc20200203_iirs2381_w03` | `chain_tmc20200203_iirs1555_w03` | loftr+magsac++ / loftr+magsac++ | 394 | 0.110 (8.1) | 0.273 | 0.498 | n/a | 67.8 / 65.4 |
| `chain_tmc20200203_iirs2381_w04` | `chain_tmc20200203_iirs1555_w04` | loftr+magsac++ / loftr+magsac++ | 400 | 0.091 (6.7) | 0.159 | 0.363 | n/a | 70.3 / 73.0 |
| `chain_tmc20200203_iirs2381_w05` | `chain_tmc20200203_iirs1555_w05` | loftr+magsac++ / loftr+magsac++ | 400 | 0.154 (11.4) | 0.314 | 0.474 | n/a | 67.8 / 67.5 |
| `chain_tmc20200203_iirs2381_w06` | `chain_tmc20200203_iirs1555_w06` | loftr+magsac++ / loftr+magsac++ | 391 | 0.146 (10.8) | 0.216 | 0.404 | n/a | 70.8 / 72.9 |
| `chain_tmc20200203_iirs2381_w07` | `chain_tmc20200203_iirs1555_w07` | loftr+magsac++ / loftr+magsac++ | 395 | 0.092 (6.8) | 0.187 | 0.321 | n/a | 76.1 / 82.0 |
| `chain_tmc20200203_iirs2381_w08` | `chain_tmc20200203_iirs1555_w08` | loftr+magsac++ / loftr+magsac++ | 391 | 0.149 (11.0) | 0.229 | 0.384 | n/a | 78.0 / 78.8 |
| `chain_tmc20200203_iirs3223_w01` | `chain_tmc20200203_iirs1555_w01` | loftr+magsac++ / loftr+magsac++ | 399 | 0.526 (38.8) | 0.948 | 1.436 | n/a | 65.0 / 78.6 |
| `chain_tmc20200203_iirs3223_w02` | `chain_tmc20200203_iirs1555_w02` | loftr+magsac++ / loftr+magsac++ | 397 | 0.251 (18.5) | 0.552 | 0.669 | n/a | 61.7 / 73.3 |
| `chain_tmc20200203_iirs3223_w03` | `chain_tmc20200203_iirs1555_w03` | loftr+magsac++ / loftr+magsac++ | 394 | 0.444 (32.8) | 1.671 | 2.394 | n/a | 55.4 / 65.4 |
| `chain_tmc20200203_iirs3223_w04` | `chain_tmc20200203_iirs1555_w04` | loftr+magsac++ / loftr+magsac++ | 400 | 0.551 (40.7) | 1.621 | 3.410 | n/a | 88.0 / 73.0 |
| `chain_tmc20200203_iirs3223_w05` | `chain_tmc20200203_iirs1555_w05` | loftr+magsac++ / loftr+magsac++ | 400 | 0.724 (53.4) | 2.242 | 3.924 | n/a | 70.2 / 67.5 |
| `chain_tmc20200203_iirs3223_w06` | `chain_tmc20200203_iirs1555_w06` | loftr+magsac++ / loftr+magsac++ | 391 | 0.396 (29.3) | 0.952 | 2.250 | n/a | 76.6 / 72.9 |
| `chain_tmc20200203_iirs3223_w07` | `chain_tmc20200203_iirs1555_w07` | loftr+magsac++ / loftr+magsac++ | 395 | 0.226 (16.8) | 0.340 | 0.724 | n/a | 70.1 / 82.0 |
| `chain_tmc20200203_iirs3223_w08` | `chain_tmc20200203_iirs1555_w08` | loftr+magsac++ / loftr+magsac++ | 391 | 0.376 (27.9) | 0.682 | 1.117 | n/a | 72.3 / 78.8 |
| `chain_tmc20200203_iirs746_w01` | `chain_tmc20200203_iirs1555_w01` | loftr+magsac++ / loftr+magsac++ | 399 | 0.573 (42.3) | 1.238 | 2.667 | n/a | 95.4 / 78.6 |
| `chain_tmc20200203_iirs746_w02` | `chain_tmc20200203_iirs1555_w02` | loftr+magsac++ / loftr+magsac++ | 397 | 0.249 (18.4) | 0.494 | 0.949 | n/a | 62.1 / 73.3 |
| `chain_tmc20200203_iirs746_w03` | `chain_tmc20200203_iirs1555_w03` | loftr+magsac++ / loftr+magsac++ | 394 | 0.278 (20.5) | 0.611 | 0.851 | n/a | 65.1 / 65.4 |
| `chain_tmc20200203_iirs746_w04` | `chain_tmc20200203_iirs1555_w04` | loftr+magsac++ / loftr+magsac++ | 400 | 0.388 (28.6) | 0.950 | 1.738 | n/a | 62.1 / 73.0 |
| `chain_tmc20200203_iirs746_w05` | `chain_tmc20200203_iirs1555_w05` | loftr+magsac++ / loftr+magsac++ | 400 | 0.441 (32.6) | 1.149 | 1.413 | n/a | 60.2 / 67.5 |
| `chain_tmc20200203_iirs746_w06` | `chain_tmc20200203_iirs1555_w06` | loftr+magsac++ / loftr+magsac++ | 391 | 0.754 (55.8) | 2.249 | 5.057 | n/a | 98.7 / 72.9 |
| `chain_tmc20200203_iirs746_w07` | `chain_tmc20200203_iirs1555_w07` | loftr+magsac++ / loftr+magsac++ | 395 | 0.450 (33.4) | 0.745 | 0.976 | n/a | 59.4 / 82.0 |
| `chain_tmc20200203_iirs746_w08` | `chain_tmc20200203_iirs1555_w08` | loftr+magsac++ / loftr+magsac++ | 391 | 0.456 (33.8) | 0.846 | 1.099 | n/a | 58.2 / 78.8 |
| `chain_tmc20200203_iirs999_w01` | `chain_tmc20200203_iirs1555_w01` | loftr+magsac++ / loftr+magsac++ | 399 | 0.059 (4.4) | 0.141 | 0.208 | n/a | 74.5 / 78.6 |
| `chain_tmc20200203_iirs999_w02` | `chain_tmc20200203_iirs1555_w02` | loftr+magsac++ / loftr+magsac++ | 397 | 0.052 (3.8) | 0.136 | 0.217 | n/a | 69.8 / 73.3 |
| `chain_tmc20200203_iirs999_w03` | `chain_tmc20200203_iirs1555_w03` | loftr+magsac++ / loftr+magsac++ | 394 | 0.065 (4.8) | 0.110 | 0.286 | n/a | 71.2 / 65.4 |
| `chain_tmc20200203_iirs999_w04` | `chain_tmc20200203_iirs1555_w04` | loftr+magsac++ / loftr+magsac++ | 400 | 0.047 (3.4) | 0.120 | 0.208 | n/a | 69.5 / 73.0 |
| `chain_tmc20200203_iirs999_w05` | `chain_tmc20200203_iirs1555_w05` | loftr+magsac++ / loftr+magsac++ | 400 | 0.068 (5.0) | 0.134 | 0.200 | n/a | 67.8 / 67.5 |
| `chain_tmc20200203_iirs999_w06` | `chain_tmc20200203_iirs1555_w06` | loftr+magsac++ / loftr+magsac++ | 391 | 0.051 (3.8) | 0.146 | 0.254 | n/a | 74.3 / 72.9 |
| `chain_tmc20200203_iirs999_w07` | `chain_tmc20200203_iirs1555_w07` | loftr+magsac++ / loftr+magsac++ | 395 | 0.067 (5.0) | 0.134 | 0.173 | n/a | 84.8 / 82.0 |
| `chain_tmc20200203_iirs999_w08` | `chain_tmc20200203_iirs1555_w08` | loftr+magsac++ / loftr+magsac++ | 391 | 0.044 (3.3) | 0.074 | 0.114 | n/a | 82.6 / 78.8 |

#### TMC-2 → IIRS 746 nm, orbit of 2020-02-03, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200203_iirs746_w01` | -4.3757, 24.9058 | 0.0 | 16.209 | 188 | 166 | 0.883 | 0.72 | 0.934 (68.983) | 1.030 | 27 / 18 | agrees | loftr+magsac++ | 95.4 |
| `chain_tmc20200203_iirs746_w02` | -10.3175, 24.9038 | 0.0 | 16.208 | 235 | 220 | 0.936 | 0.92 | 0.665 (49.109) | 0.840 | 33 / 5 | agrees | loftr+magsac++ | 62.1 |
| `chain_tmc20200203_iirs746_w03` | -10.8703, 24.9036 | 0.0 | 16.21 | 288 | 278 | 0.965 | 0.86 | 0.547 (40.378) | 0.951 | 41 / 9 | agrees | loftr+magsac++ | 65.1 |
| `chain_tmc20200203_iirs746_w04` | -12.2521, 24.9031 | 0.0 | 16.21 | 195 | 170 | 0.872 | 0.73 | 0.886 (65.437) | 1.146 | 31 / 17 | agrees | loftr+magsac++ | 62.1 |
| `chain_tmc20200203_iirs746_w05` | -12.8049, 24.9028 | 0.0 | 16.21 | 144 | 122 | 0.847 | 0.55 | 0.857 (63.231) | 0.954 | 19 / 29 | agrees | loftr+magsac++ | 60.2 |
| `chain_tmc20200203_iirs746_w06` | -24.6853, 24.8962 | 0.0 | 16.209 | 167 | 144 | 0.862 | 0.64 | 0.923 (68.321) | 1.270 | 21 / 23 | agrees | loftr+magsac++ | 98.7 |
| `chain_tmc20200203_iirs746_w07` | -26.6182, 24.8946 | 0.0 | 16.21 | 233 | 210 | 0.901 | 0.80 | 0.613 (45.470) | 1.077 | 33 / 13 | agrees | loftr+magsac++ | 59.4 |
| `chain_tmc20200203_iirs746_w08` | -27.1704, 24.8941 | 0.0 | 16.208 | 163 | 142 | 0.871 | 0.61 | 0.863 (64.022) | 0.989 | 24 / 25 | agrees | loftr+magsac++ | 58.2 |

#### TMC-2 → IIRS 999 nm, orbit of 2020-02-03, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200203_iirs999_w01` | -4.3757, 24.9058 | 0.0 | 16.209 | 399 | 399 | 1.000 | 0.97 | 0.210 (15.524) | 0.403 | 54 / 2 | agrees | loftr+magsac++ | 74.5 |
| `chain_tmc20200203_iirs999_w02` | -10.3175, 24.9038 | 0.0 | 16.208 | 400 | 400 | 1.000 | 1.00 | 0.254 (18.765) | 0.375 | 57 / 0 | agrees | loftr+magsac++ | 69.8 |
| `chain_tmc20200203_iirs999_w03` | -10.8703, 24.9036 | 0.0 | 16.21 | 397 | 397 | 1.000 | 1.00 | 0.266 (19.641) | 0.407 | 50 / 0 | agrees | loftr+magsac++ | 71.2 |
| `chain_tmc20200203_iirs999_w04` | -12.2521, 24.9031 | 0.0 | 16.21 | 400 | 399 | 0.998 | 0.98 | 0.243 (17.915) | 0.431 | 56 / 1 | agrees | loftr+magsac++ | 69.5 |
| `chain_tmc20200203_iirs999_w05` | -12.8049, 24.9028 | 0.0 | 16.21 | 400 | 400 | 1.000 | 1.00 | 0.309 (22.813) | 0.487 | 57 / 0 | agrees | loftr+magsac++ | 67.8 |
| `chain_tmc20200203_iirs999_w06` | -24.6853, 24.8962 | 0.0 | 16.209 | 386 | 382 | 0.990 | 1.00 | 0.209 (15.464) | 0.360 | 55 / 0 | agrees | loftr+magsac++ | 74.3 |
| `chain_tmc20200203_iirs999_w07` | -26.6182, 24.8946 | 0.0 | 16.21 | 398 | 397 | 0.997 | 1.00 | 0.199 (14.770) | 0.402 | 56 / 0 | agrees | loftr+magsac++ | 84.8 |
| `chain_tmc20200203_iirs999_w08` | -27.1704, 24.8941 | 0.0 | 16.208 | 391 | 391 | 1.000 | 1.00 | 0.235 (17.408) | 0.424 | 55 / 0 | agrees | loftr+magsac++ | 82.6 |

#### TMC-2 → IIRS 1555 nm, orbit of 2020-02-03, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200203_iirs1555_w01` | -4.3757, 24.9058 | 0.0 | 16.209 | 399 | 399 | 1.000 | 0.97 | 0.212 (15.638) | 0.320 | 54 / 2 | agrees | loftr+magsac++ | 78.6 |
| `chain_tmc20200203_iirs1555_w02` | -10.3175, 24.9038 | 0.0 | 16.208 | 398 | 397 | 0.997 | 1.00 | 0.253 (18.655) | 0.343 | 54 / 0 | agrees | loftr+magsac++ | 73.3 |
| `chain_tmc20200203_iirs1555_w03` | -10.8703, 24.9036 | 0.0 | 16.21 | 395 | 394 | 0.997 | 0.98 | 0.252 (18.610) | 0.433 | 50 / 1 | agrees | loftr+magsac++ | 65.4 |
| `chain_tmc20200203_iirs1555_w04` | -12.2521, 24.9031 | 0.0 | 16.21 | 400 | 400 | 1.000 | 1.00 | 0.276 (20.391) | 0.494 | 56 / 0 | agrees | loftr+magsac++ | 73.0 |
| `chain_tmc20200203_iirs1555_w05` | -12.8049, 24.9028 | 0.0 | 16.21 | 400 | 400 | 1.000 | 1.00 | 0.319 (23.555) | 0.370 | 57 / 0 | agrees | loftr+magsac++ | 67.5 |
| `chain_tmc20200203_iirs1555_w06` | -24.6853, 24.8962 | 0.0 | 16.209 | 393 | 391 | 0.995 | 0.98 | 0.214 (15.865) | 0.467 | 57 / 1 | agrees | loftr+magsac++ | 72.9 |
| `chain_tmc20200203_iirs1555_w07` | -26.6182, 24.8946 | 0.0 | 16.21 | 397 | 395 | 0.995 | 1.00 | 0.224 (16.631) | 0.388 | 54 / 0 | agrees | loftr+magsac++ | 82.0 |
| `chain_tmc20200203_iirs1555_w08` | -27.1704, 24.8941 | 0.0 | 16.208 | 393 | 391 | 0.995 | 1.00 | 0.255 (18.872) | 0.519 | 53 / 0 | agrees | loftr+magsac++ | 78.8 |

#### TMC-2 → IIRS 2381 nm, orbit of 2020-02-03, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200203_iirs2381_w01` | -4.3757, 24.9058 | 0.0 | 16.209 | 369 | 363 | 0.984 | 0.97 | 0.326 (24.041) | 0.683 | 52 / 2 | agrees | loftr+magsac++ | 76.1 |
| `chain_tmc20200203_iirs2381_w02` | -10.3175, 24.9038 | 0.0 | 16.208 | 392 | 390 | 0.995 | 1.00 | 0.339 (25.046) | 0.433 | 54 / 0 | agrees | loftr+magsac++ | 69.0 |
| `chain_tmc20200203_iirs2381_w03` | -10.8703, 24.9036 | 0.0 | 16.21 | 380 | 380 | 1.000 | 0.98 | 0.364 (26.905) | 0.492 | 50 / 1 | agrees | loftr+magsac++ | 67.8 |
| `chain_tmc20200203_iirs2381_w04` | -12.2521, 24.9031 | 0.0 | 16.21 | 383 | 383 | 1.000 | 1.00 | 0.342 (25.232) | 0.497 | 55 / 0 | agrees | loftr+magsac++ | 70.3 |
| `chain_tmc20200203_iirs2381_w05` | -12.8049, 24.9028 | 0.0 | 16.21 | 396 | 396 | 1.000 | 0.98 | 0.416 (30.686) | 0.673 | 53 / 1 | agrees | loftr+magsac++ | 67.8 |
| `chain_tmc20200203_iirs2381_w06` | -24.6853, 24.8962 | 0.0 | 16.209 | 341 | 336 | 0.985 | 0.98 | 0.323 (23.957) | 0.699 | 51 / 1 | agrees | loftr+magsac++ | 70.8 |
| `chain_tmc20200203_iirs2381_w07` | -26.6182, 24.8946 | 0.0 | 16.21 | 374 | 369 | 0.987 | 0.98 | 0.307 (22.745) | 0.505 | 52 / 1 | agrees | loftr+magsac++ | 76.1 |
| `chain_tmc20200203_iirs2381_w08` | -27.1704, 24.8941 | 0.0 | 16.208 | 341 | 334 | 0.979 | 0.95 | 0.364 (26.978) | 0.643 | 47 / 3 | agrees | loftr+magsac++ | 78.0 |

#### TMC-2 → IIRS 3223 nm, orbit of 2020-02-03, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200203_iirs3223_w01` | -4.3757, 24.9058 | 0.0 | 16.209 | 173 | 154 | 0.890 | 0.66 | 1.188 (87.744) | 1.439 | 24 / 21 | agrees | loftr+magsac++ | 65.0 |
| `chain_tmc20200203_iirs3223_w02` | -10.3175, 24.9038 | 0.0 | 16.208 | 204 | 182 | 0.892 | 0.77 | 0.672 (49.598) | 1.109 | 27 / 14 | agrees | loftr+magsac++ | 61.7 |
| `chain_tmc20200203_iirs3223_w03` | -10.8703, 24.9036 | 0.0 | 16.21 | 71 | 51 | 0.718 | 0.33 | 0.585 (43.186) | 1.085 | 7 / 43 | agrees | loftr+magsac++ | 55.4 |
| `chain_tmc20200203_iirs3223_w04` | -12.2521, 24.9031 | 0.0 | 16.21 | 84 | 59 | 0.702 | 0.44 | 0.737 (54.412) | 0.812 | 9 / 36 | agrees | loftr+magsac++ | 88.0 |
| `chain_tmc20200203_iirs3223_w05` | -12.8049, 24.9028 | 0.0 | 16.21 | 73 | 53 | 0.726 | 0.36 | 0.522 (38.530) | 0.486 | 8 / 41 | agrees | loftr+magsac++ | 70.2 |
| `chain_tmc20200203_iirs3223_w06` | -24.6853, 24.8962 | 0.0 | 16.209 | 260 | 241 | 0.927 | 0.81 | 0.567 (42.004) | 1.045 | 38 / 12 | agrees | loftr+magsac++ | 76.6 |
| `chain_tmc20200203_iirs3223_w07` | -26.6182, 24.8946 | 0.0 | 16.21 | 251 | 240 | 0.956 | 0.83 | 0.507 (37.592) | 0.675 | 34 / 11 | agrees | loftr+magsac++ | 70.1 |
| `chain_tmc20200203_iirs3223_w08` | -27.1704, 24.8941 | 0.0 | 16.208 | 221 | 206 | 0.932 | 0.77 | 0.436 (32.306) | 0.672 | 29 / 15 | agrees | loftr+magsac++ | 72.3 |

### TMC-2 → IIRS, orbit of 2020-06-07 (cross-sensor, same mission; multi-modal beyond 850 nm) - 2 of 2 orbits

TMC-2 nadir `ch2_tmc_ncn_20200607T2239162106_d_img_d18` against IIRS `ch2_iir_nci_20200607T2239153893_d_img_d18`, the same orbit. IIRS label has no Sun fields; both nadir strips start 0.8 s apart (22:39:16.210600 TMC-2, 22:39:15.389300 IIRS UTC), so the Sun is the same to well under 0.1 deg: difference set to 0 by construction. TMC-2 label: azimuth 203.756456, elevation 41.766894 (strip centre). 8 windows, chosen before any matching by the texture of the IIRS 1555 nm band alone (pre-registered: candidates every 15.0 km along the IIRS centre line within latitude (29.0, 62.0), fully covered by both, ranked by the IIRS window's texture, best-first at least one window apart (ops/cut_chain_pairs.py docstring)); the same 8 ground windows for every band, so each band row below is 8 registrations of the same 8 places. TMC-2 ~5.17 m against IIRS ~83.67 m (16.184×), 192-px IIRS windows, so every trust cell is 24 px and the per-cell area check runs. TMC-2 records 400-850 nm (its PRADAN payload description); an IIRS band beyond 850 nm is outside anything TMC-2 sees and counts as multi-modal, a band inside it does not.

| IIRS band | modality | windows accepted | matches | inliers | held-out median px (m) on the IIRS grid | verified cells /64 | archive offset m |
|---|---|---|---|---|---|---|---|
| 999 nm | infrared: multi-modal | 8/8 | 263 to 400 | 245 to 399 | 0.153 to 0.412 (12.8 to 34.5 m) | 40 to 55 | 139.4 to 167.0 |
| 1555 nm | infrared: multi-modal | 8/8 | 344 to 400 | 338 to 400 | 0.165 to 0.325 (13.8 to 27.2 m) | 48 to 55 | 146.3 to 168.9 |
| 2381 nm | infrared: multi-modal | 8/8 | 183 to 397 | 169 to 394 | 0.262 to 0.792 (21.9 to 66.3 m) | 27 to 55 | 127.4 to 168.1 |
| 3223 nm | infrared: multi-modal | 6/6 | 134 to 295 | 103 to 278 | 0.623 to 1.206 (52.3 to 101.3 m) | 16 to 44 | 115.1 to 165.3 |

The archive offset (how far each registration moved TMC-2 from where the two archives' own grids put it) is 1.37-2.01 IIRS pixels in every band and every window: a steady disagreement between the two instruments' geolocation, which is what a registration is for.

Band against band, summarised (full table below): the MEDIAN disagreement per window, and the worst single point of the 20 × 20 lattice. These are medians and a maximum, not bounds, and they measure consistency between independent registrations, not accuracy.

| band against 1555 nm | windows | median disagreement px (m) | p90 px | worst point px |
|---|---|---|---|---|
| 999 nm | 8 | 0.032 to 0.214 (2.7 to 17.9 m) | 0.07 to 0.51 | 0.99 |
| 2381 nm | 8 | 0.054 to 0.435 (4.5 to 36.4 m) | 0.08 to 0.84 | 1.72 |
| 3223 nm | 6 | 0.201 to 0.612 (16.9 to 51.4 m) | 0.30 to 0.87 | 1.19 |

**Band against band, same window.** Each IIRS band's declared transform against the 1555 nm one, on the same TMC-2 window and the same IIRS grid (`ops/multimodal_check.py`). Every band was registered on its own - its own LoFTR matches, its own fit - so this compares two independent registrations of one piece of ground. Agreement is consistency, not accuracy; disagreement would prove one of them wrong.

| pair | against | declared (pair / against) | against inliers | disagreement median px (m) | p90 px | max px | fallback NCC | archive offset m (pair / against) |
|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200607_iirs2381_w01` | `chain_tmc20200607_iirs1555_w01` | loftr+magsac++ / loftr+magsac++ | 338 | 0.425 (35.6) | 0.841 | 1.718 | n/a | 161.4 / 157.5 |
| `chain_tmc20200607_iirs2381_w02` | `chain_tmc20200607_iirs1555_w02` | loftr+magsac++ / loftr+magsac++ | 380 | 0.195 (16.4) | 0.338 | 0.430 | n/a | 154.0 / 156.3 |
| `chain_tmc20200607_iirs2381_w03` | `chain_tmc20200607_iirs1555_w03` | loftr+magsac++ / loftr+magsac++ | 373 | 0.279 (23.5) | 0.556 | 0.764 | n/a | 158.9 / 158.5 |
| `chain_tmc20200607_iirs2381_w04` | `chain_tmc20200607_iirs1555_w04` | loftr+magsac++ / loftr+magsac++ | 380 | 0.435 (36.5) | 0.823 | 1.134 | n/a | 127.4 / 146.3 |
| `chain_tmc20200607_iirs2381_w05` | `chain_tmc20200607_iirs1555_w05` | loftr+magsac++ / loftr+magsac++ | 399 | 0.054 (4.5) | 0.081 | 0.129 | n/a | 154.6 / 153.9 |
| `chain_tmc20200607_iirs2381_w06` | `chain_tmc20200607_iirs1555_w06` | loftr+magsac++ / loftr+magsac++ | 400 | 0.093 (7.8) | 0.252 | 0.379 | n/a | 149.2 / 152.8 |
| `chain_tmc20200607_iirs2381_w07` | `chain_tmc20200607_iirs1555_w07` | loftr+magsac++ / loftr+magsac++ | 397 | 0.080 (6.7) | 0.125 | 0.185 | n/a | 162.8 / 162.8 |
| `chain_tmc20200607_iirs2381_w08` | `chain_tmc20200607_iirs1555_w08` | loftr+magsac++ / loftr+magsac++ | 392 | 0.124 (10.5) | 0.165 | 0.247 | n/a | 168.1 / 168.9 |
| `chain_tmc20200607_iirs3223_w02` | `chain_tmc20200607_iirs1555_w02` | loftr+magsac++ / loftr+magsac++ | 380 | 0.257 (21.6) | 0.543 | 0.963 | n/a | 143.0 / 156.3 |
| `chain_tmc20200607_iirs3223_w04` | `chain_tmc20200607_iirs1555_w04` | loftr+magsac++ / loftr+magsac++ | 380 | 0.457 (38.4) | 0.870 | 1.190 | n/a | 162.9 / 146.3 |
| `chain_tmc20200607_iirs3223_w05` | `chain_tmc20200607_iirs1555_w05` | loftr+magsac++ / loftr+magsac++ | 399 | 0.201 (16.9) | 0.297 | 0.393 | n/a | 137.5 / 153.9 |
| `chain_tmc20200607_iirs3223_w06` | `chain_tmc20200607_iirs1555_w06` | loftr+magsac++ / loftr+magsac++ | 400 | 0.612 (51.5) | 0.862 | 1.180 | n/a | 115.1 / 152.8 |
| `chain_tmc20200607_iirs3223_w07` | `chain_tmc20200607_iirs1555_w07` | loftr+magsac++ / loftr+magsac++ | 397 | 0.351 (29.6) | 0.800 | 0.996 | n/a | 165.3 / 162.8 |
| `chain_tmc20200607_iirs3223_w08` | `chain_tmc20200607_iirs1555_w08` | loftr+magsac++ / loftr+magsac++ | 392 | 0.312 (26.3) | 0.706 | 1.111 | n/a | 161.9 / 168.9 |
| `chain_tmc20200607_iirs999_w01` | `chain_tmc20200607_iirs1555_w01` | loftr+magsac++ / loftr+magsac++ | 338 | 0.157 (13.1) | 0.407 | 0.605 | n/a | 155.9 / 157.5 |
| `chain_tmc20200607_iirs999_w02` | `chain_tmc20200607_iirs1555_w02` | loftr+magsac++ / loftr+magsac++ | 380 | 0.134 (11.3) | 0.209 | 0.327 | n/a | 145.8 / 156.3 |
| `chain_tmc20200607_iirs999_w03` | `chain_tmc20200607_iirs1555_w03` | loftr+magsac++ / loftr+magsac++ | 373 | 0.214 (17.9) | 0.514 | 0.989 | n/a | 146.0 / 158.5 |
| `chain_tmc20200607_iirs999_w04` | `chain_tmc20200607_iirs1555_w04` | loftr+magsac++ / loftr+magsac++ | 380 | 0.202 (17.0) | 0.378 | 0.556 | n/a | 139.4 / 146.3 |
| `chain_tmc20200607_iirs999_w05` | `chain_tmc20200607_iirs1555_w05` | loftr+magsac++ / loftr+magsac++ | 399 | 0.040 (3.3) | 0.137 | 0.214 | n/a | 154.8 / 153.9 |
| `chain_tmc20200607_iirs999_w06` | `chain_tmc20200607_iirs1555_w06` | loftr+magsac++ / loftr+magsac++ | 400 | 0.032 (2.7) | 0.070 | 0.107 | n/a | 151.9 / 152.8 |
| `chain_tmc20200607_iirs999_w07` | `chain_tmc20200607_iirs1555_w07` | loftr+magsac++ / loftr+magsac++ | 397 | 0.049 (4.1) | 0.113 | 0.217 | n/a | 164.5 / 162.8 |
| `chain_tmc20200607_iirs999_w08` | `chain_tmc20200607_iirs1555_w08` | loftr+magsac++ / loftr+magsac++ | 392 | 0.094 (7.9) | 0.193 | 0.301 | n/a | 167.0 / 168.9 |

#### TMC-2 → IIRS 999 nm, orbit of 2020-06-07, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200607_iirs999_w01` | 60.6731, 354.7980 | 0.0 | 16.184 | 317 | 307 | 0.968 | 0.81 | 0.362 (30.322) | 0.710 | 45 / 12 | agrees | loftr+magsac++ | 155.9 |
| `chain_tmc20200607_iirs999_w02` | 59.5974, 354.8125 | 0.0 | 16.179 | 347 | 339 | 0.977 | 0.89 | 0.412 (34.602) | 0.960 | 52 / 7 | agrees | loftr+magsac++ | 145.8 |
| `chain_tmc20200607_iirs999_w03` | 58.6562, 354.8242 | 0.0 | 16.178 | 344 | 340 | 0.988 | 0.86 | 0.377 (31.689) | 0.798 | 47 / 9 | agrees | loftr+magsac++ | 146.0 |
| `chain_tmc20200607_iirs999_w04` | 57.7151, 354.8352 | 0.0 | 16.18 | 263 | 245 | 0.932 | 0.83 | 0.294 (24.749) | 0.667 | 40 / 11 | agrees | loftr+magsac++ | 139.4 |
| `chain_tmc20200607_iirs999_w05` | 56.2364, 354.8510 | 0.0 | 16.18 | 397 | 396 | 0.997 | 0.88 | 0.167 (14.047) | 0.254 | 54 / 8 | agrees | loftr+magsac++ | 154.8 |
| `chain_tmc20200607_iirs999_w06` | 54.6236, 354.8667 | 0.0 | 16.18 | 400 | 399 | 0.998 | 0.88 | 0.182 (15.346) | 0.319 | 55 / 8 | agrees | loftr+magsac++ | 151.9 |
| `chain_tmc20200607_iirs999_w07` | 52.7423, 354.8829 | 0.0 | 16.179 | 399 | 396 | 0.992 | 0.88 | 0.153 (12.885) | 0.259 | 55 / 8 | agrees | loftr+magsac++ | 164.5 |
| `chain_tmc20200607_iirs999_w08` | 51.6674, 354.8914 | 0.0 | 16.18 | 393 | 391 | 0.995 | 0.88 | 0.202 (17.040) | 0.483 | 55 / 8 | agrees | loftr+magsac++ | 167.0 |

#### TMC-2 → IIRS 1555 nm, orbit of 2020-06-07, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200607_iirs1555_w01` | 60.6731, 354.7980 | 0.0 | 16.184 | 344 | 338 | 0.983 | 0.84 | 0.217 (18.185) | 0.614 | 48 / 10 | agrees | loftr+magsac++ | 157.5 |
| `chain_tmc20200607_iirs1555_w02` | 59.5974, 354.8125 | 0.0 | 16.179 | 383 | 380 | 0.992 | 0.89 | 0.325 (27.270) | 0.608 | 52 / 7 | agrees | loftr+magsac++ | 156.3 |
| `chain_tmc20200607_iirs1555_w03` | 58.6562, 354.8242 | 0.0 | 16.178 | 379 | 373 | 0.984 | 0.84 | 0.224 (18.815) | 0.678 | 53 / 10 | agrees | loftr+magsac++ | 158.5 |
| `chain_tmc20200607_iirs1555_w04` | 57.7151, 354.8352 | 0.0 | 16.18 | 384 | 380 | 0.990 | 0.91 | 0.198 (16.649) | 0.624 | 53 / 6 | agrees | loftr+magsac++ | 146.3 |
| `chain_tmc20200607_iirs1555_w05` | 56.2364, 354.8510 | 0.0 | 16.18 | 399 | 399 | 1.000 | 0.88 | 0.165 (13.853) | 0.262 | 55 / 8 | agrees | loftr+magsac++ | 153.9 |
| `chain_tmc20200607_iirs1555_w06` | 54.6236, 354.8667 | 0.0 | 16.18 | 400 | 400 | 1.000 | 0.88 | 0.172 (14.446) | 0.359 | 55 / 8 | agrees | loftr+magsac++ | 152.8 |
| `chain_tmc20200607_iirs1555_w07` | 52.7423, 354.8829 | 0.0 | 16.179 | 398 | 397 | 0.997 | 0.89 | 0.177 (14.922) | 0.381 | 55 / 7 | agrees | loftr+magsac++ | 162.8 |
| `chain_tmc20200607_iirs1555_w08` | 51.6674, 354.8914 | 0.0 | 16.18 | 396 | 392 | 0.990 | 0.86 | 0.200 (16.882) | 0.648 | 54 / 9 | agrees | loftr+magsac++ | 168.9 |

#### TMC-2 → IIRS 2381 nm, orbit of 2020-06-07, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200607_iirs2381_w01` | 60.6731, 354.7980 | 0.0 | 16.184 | 271 | 243 | 0.897 | 0.77 | 0.483 (40.425) | 0.859 | 32 / 15 | agrees | loftr+magsac++ | 161.4 |
| `chain_tmc20200607_iirs2381_w02` | 59.5974, 354.8125 | 0.0 | 16.179 | 286 | 270 | 0.944 | 0.83 | 0.630 (52.909) | 0.962 | 39 / 11 | agrees | loftr+magsac++ | 154.0 |
| `chain_tmc20200607_iirs2381_w03` | 58.6562, 354.8242 | 0.0 | 16.178 | 268 | 251 | 0.937 | 0.88 | 0.493 (41.443) | 0.916 | 38 / 8 | agrees | loftr+magsac++ | 158.9 |
| `chain_tmc20200607_iirs2381_w04` | 57.7151, 354.8352 | 0.0 | 16.18 | 183 | 169 | 0.923 | 0.72 | 0.792 (66.589) | 1.034 | 27 / 18 | agrees | loftr+magsac++ | 127.4 |
| `chain_tmc20200607_iirs2381_w05` | 56.2364, 354.8510 | 0.0 | 16.18 | 391 | 390 | 0.997 | 0.88 | 0.288 (24.219) | 0.571 | 52 / 8 | agrees | loftr+magsac++ | 154.6 |
| `chain_tmc20200607_iirs2381_w06` | 54.6236, 354.8667 | 0.0 | 16.18 | 397 | 394 | 0.992 | 0.88 | 0.293 (24.616) | 0.516 | 55 / 8 | agrees | loftr+magsac++ | 149.2 |
| `chain_tmc20200607_iirs2381_w07` | 52.7423, 354.8829 | 0.0 | 16.179 | 384 | 377 | 0.982 | 0.88 | 0.287 (24.133) | 0.568 | 55 / 8 | agrees | loftr+magsac++ | 162.8 |
| `chain_tmc20200607_iirs2381_w08` | 51.6674, 354.8914 | 0.0 | 16.18 | 382 | 372 | 0.974 | 0.89 | 0.262 (22.041) | 0.532 | 53 / 7 | agrees | loftr+magsac++ | 168.1 |

#### TMC-2 → IIRS 3223 nm, orbit of 2020-06-07, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_tmc20200607_iirs3223_w02` | 59.5974, 354.8125 | 0.0 | 16.179 | 287 | 276 | 0.962 | 0.89 | 0.623 (52.315) | 0.978 | 37 / 7 | agrees | loftr+magsac++ | 143.0 |
| `chain_tmc20200607_iirs3223_w04` | 57.7151, 354.8352 | 0.0 | 16.18 | 134 | 103 | 0.769 | 0.58 | 1.206 (101.365) | 1.301 | 16 / 27 | agrees | loftr+magsac++ | 162.9 |
| `chain_tmc20200607_iirs3223_w05` | 56.2364, 354.8510 | 0.0 | 16.18 | 268 | 255 | 0.951 | 0.81 | 0.874 (73.518) | 1.086 | 41 / 12 | agrees | loftr+magsac++ | 137.5 |
| `chain_tmc20200607_iirs3223_w06` | 54.6236, 354.8667 | 0.0 | 16.18 | 295 | 278 | 0.942 | 0.89 | 1.080 (90.867) | 1.305 | 44 / 7 | agrees | loftr+magsac++ | 115.1 |
| `chain_tmc20200607_iirs3223_w07` | 52.7423, 354.8829 | 0.0 | 16.179 | 214 | 187 | 0.874 | 0.75 | 0.656 (55.212) | 0.882 | 31 / 16 | agrees | loftr+magsac++ | 165.3 |
| `chain_tmc20200607_iirs3223_w08` | 51.6674, 354.8914 | 0.0 | 16.18 | 274 | 243 | 0.887 | 0.80 | 0.726 (61.194) | 1.027 | 41 / 13 | agrees | loftr+magsac++ | 161.9 |

### LRO NAC → TMC-2 at SAC's site: the same NAC, two TMC-2 passes

NAC `M1258792259LE` (~0.784 m), chosen for a Sun close to TMC-2's 2020-02-03 pass, against that pass and against the 2025-07-07 pass. Cross-sensor and cross-mission; both panchromatic - NOT multi-modal. NAC geometry prior: none: LROC's published corners, uncorrected (see docstring) - never fitted to the TMC-2 it is registered to, nor to the OHRC. Windows by `ops.cut_site_pairs.pick_windows` on 4 m overviews (shared, lit, textured), no matching involved. NAC Sun computed at each window from LROC's sub-solar point; TMC-2 Sun from its label.

| TMC-2 pass | Δsun az | Δincidence | windows | verdicts | inliers | inlier ratio | held-out median px (m) on the TMC-2 grid, accepted windows | verified cells /64 | archive offset m, accepted windows |
|---|---|---|---|---|---|---|---|---|---|
| 2020-02-03 | 2.6 to 3.2° | -4.5 to -4.3° | 6 | agrees 6 | 1128 to 1588 | 0.96 to 0.99 | 0.361 to 0.481 (1.6 to 2.2 m) | 49 to 58 | 121.4 to 175.3 |
| 2025-07-07 | 44.7 to 45.7° | -25.6 to -25.4° | 6 | agrees 3, unconfirmed 2, contradicted 1 | 21 to 74 | 0.15 to 0.35 | not quoted: at these inlier ratios the held-out median is not robust | 0 to 6 | 127.4 to 197.6 |

With the Sun 2.6 to 3.2° apart in azimuth and -4.5 to -4.3° in incidence, TMC-2 registers: agrees 6. With it 44.7 to 45.7° apart in azimuth and -25.6 to -25.4° in incidence, the same NAC gives agrees 3, unconfirmed 2, contradicted 1; the accepted ones rest on 4 to 6 verified cells at inlier ratios of 0.16 to 0.35, and no accuracy is quoted for them.

#### NAC → TMC-2 pass 2020-02-03, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_nacm1258792259le_tmc20200203_w01` | -13.0252, 25.1261 | 3.0 | 5.81 | 1371 | 1330 | 0.970 | 0.91 | 0.481 (2.191) | 0.683 | 51 / 6 | agrees | loftr+magsac++ | 144.2 |
| `chain_nacm1258792259le_tmc20200203_w02` | -13.3444, 25.1261 | 2.7 | 5.81 | 1185 | 1141 | 0.963 | 1.00 | 0.361 (1.645) | 0.652 | 58 / 0 | agrees | loftr+magsac++ | 124.0 |
| `chain_nacm1258792259le_tmc20200203_w03` | -12.7930, 25.1261 | 3.2 | 5.81 | 1430 | 1417 | 0.991 | 0.91 | 0.374 (1.702) | 0.546 | 49 / 6 | agrees | loftr+magsac++ | 175.3 |
| `chain_nacm1258792259le_tmc20200203_w04` | -13.4170, 25.1261 | 2.6 | 5.81 | 1462 | 1441 | 0.986 | 0.97 | 0.443 (2.018) | 0.620 | 50 / 2 | agrees | loftr+magsac++ | 130.6 |
| `chain_nacm1258792259le_tmc20200203_w05` | -13.1558, 25.1261 | 2.9 | 5.81 | 1165 | 1128 | 0.968 | 0.98 | 0.424 (1.929) | 0.681 | 50 / 1 | agrees | loftr+magsac++ | 128.8 |
| `chain_nacm1258792259le_tmc20200203_w06` | -13.2283, 25.1261 | 2.8 | 5.81 | 1601 | 1588 | 0.992 | 1.00 | 0.398 (1.811) | 0.642 | 57 / 0 | agrees | loftr+magsac++ | 121.4 |

#### NAC → TMC-2 pass 2025-07-07, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_nacm1258792259le_tmc20250707_w01` | -13.0742, 25.1280 | 45.5 | 7.112 | 167 | 36 | 0.216 | 0.25 | 68.311 (380.903) | 0.954 | 4 / 48 | unconfirmed | loftr+magsac++ | 154.8 |
| `chain_nacm1258792259le_tmc20250707_w02` | -13.7865, 25.1829 | 44.8 | 7.112 | 179 | 28 | 0.156 | 0.14 | 68.348 (381.110) | 1.987 | 4 / 53 | agrees | loftr+magsac++ | 127.4 |
| `chain_nacm1258792259le_tmc20250707_w03` | -13.4838, 25.1646 | 45.1 | 7.112 | 141 | 21 | 0.149 | 0.16 | 100.908 (562.662) | 1.559 | 2 / 51 | unconfirmed | loftr+magsac++ | 197.3 |
| `chain_nacm1258792259le_tmc20250707_w04` | -12.8071, 25.1463 | 45.7 | 7.112 | 210 | 74 | 0.352 | 0.28 | 54.859 (305.894) | 1.422 | 5 / 46 | agrees | loftr+magsac++ | 197.6 |
| `chain_nacm1258792259le_tmc20250707_w05` | -13.8934, 25.2012 | 44.7 | 7.112 | 178 | 46 | 0.258 | 0.22 | 87.353 (487.081) | 1.151 | 6 / 48 | agrees | loftr+magsac++ | 141.3 |
| `chain_nacm1258792259le_tmc20250707_w06` | -13.6797, 25.1646 | 44.9 | 7.112 | 169 | 25 | 0.148 | 0.17 | 13.679 (76.275) | 1.748 | 0 / 54 | contradicted | fft_phase_correlation (fallback) | 86.9 |

### OHRC → TMC-2 again, with the OHRC placed in LRO's geometry

The frozen OHRC -> TMC-2 pairs above were cut on the two archives' own grids. LROC's published corners for SAC's NAC `M1350459544RE` sit (+488, +1790) m (1.9 km) from SAC's OHRC archive grid (`site_geometry/M1350459544RE.json`), against a TMC-2 window of 2.1 km. A second NAC's corners (`M1258792259LE`) sit (+356, +1980) m from the OHRC-aligned first NAC (9/11 wide-search templates, an offset that drifts along the strip; `site_geometry/M1258792259LE.json`), i.e. about 231 m from the first NAC's own corners. TMC-2's 2020-02-03 grid lands 121 to 175 m from the second NAC's corners (the accepted windows above) - consistent to within the ~0.01° precision LROC publishes its corners to, not a geolocation accuracy. The first NAC was never measured against TMC-2. So SAC's OHRC frame is the one far from the others, and the frozen windows barely shared ground: that refusal was right - those answers were wrong - but it cannot be laid on the Sun alone. Here the OHRC frame is first moved by (+519, +1821) m into LRO's geometry (the NAC's saved wide offset plus its 4 m field evaluated at the OHRC frame's centre, 44 m apart; no TMC-2 pixel), and cut exactly as the frozen pairs were: same window rule, same 4×4 OHRC averaging, same scale. Result: contradicted 4. What is left between the two images is the Sun (120.2° apart in azimuth; label elevations 9.9° and 69.4°) and the 5.0× scale, which this test cannot separate. The frozen evidence accepts much larger azimuth differences at lower, similar elevations (SAC's equatorial pair above), so the elevation difference is the likelier cause; OHRC -> TMC-2 under a matched Sun is tested at Site N below.

#### OHRC (in LRO geometry) → TMC-2 pass 2025-07-07, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `chain_ohrclroc_tmc20250707_w01` | -13.0965, 25.2068 | 120.2 | 5.005 | 83 | 8 | 0.096 | 0.08 | 81.677 (455.433) | 2.334 | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 329.8 |
| `chain_ohrclroc_tmc20250707_w02` | -13.3069, 25.2056 | 120.2 | 5.005 | 124 | 8 | 0.065 | 0.05 | 108.604 (605.573) | 0.319 | 0 / 61 | contradicted | fft_phase_correlation (fallback) | 916.3 |
| `chain_ohrclroc_tmc20250707_w03` | -13.5173, 25.2045 | 120.2 | 5.005 | 92 | 5 | 0.054 | 0.06 | 167.738 (935.307) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 631.6 |
| `chain_ohrclroc_tmc20250707_w04` | -13.7277, 25.2034 | 120.2 | 5.005 | 114 | 6 | 0.053 | 0.06 | 173.354 (966.623) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 633.5 |

## A whole strip: TMC-2 → IIRS 1555 nm, every window (no selection)

Every window of one whole strip, edge to edge, with no selection (`ops/cut_chain_pairs.py tmc-iirs --strip`): TMC-2 nadir `ch2_tmc_ncn_20200607T2239162106_d_img_d18` onto IIRS `ch2_iir_nci_20200607T2239153893_d_img_d18 band 51 (1555.0 nm)` at 1555 nm (multi-modal), the same orbit. 58 windows of about 16.2 km = 940 km of strip, latitude 30.3-60.8°. Verdicts: agrees 58; **accepted 58/58**; held-out median of the accepted windows above an inlier ratio of 0.5: 0.15-0.95 px = 12.9-79.2 m on the 83.57 m IIRS grid. Time on one laptop CPU: cutting 2.9 min (reading both products and resampling), registration 1.3 min (median 1.3 s per window). Reported only here, never merged with the selected windows above.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `strip_tmc20200607_iirs1555_s001` | 60.8076, 354.7962 | 0.0 | 16.183 | 355 | 350 | 0.986 | 0.88 | 0.230 (19.234) | 0.528 | 50 / 8 | agrees | loftr+magsac++ | 164.6 |
| `strip_tmc20200607_iirs1555_s002` | 60.2697, 354.8036 | 0.0 | 16.185 | 237 | 220 | 0.928 | 0.77 | 0.453 (38.071) | 0.744 | 38 / 15 | agrees | loftr+magsac++ | 146.7 |
| `strip_tmc20200607_iirs1555_s003` | 59.7318, 354.8107 | 0.0 | 16.179 | 365 | 360 | 0.986 | 0.86 | 0.280 (23.544) | 0.709 | 52 / 8 | agrees | loftr+magsac++ | 155.5 |
| `strip_tmc20200607_iirs1555_s004` | 59.1940, 354.8176 | 0.0 | 16.183 | 332 | 322 | 0.970 | 0.84 | 0.313 (26.277) | 0.895 | 47 / 10 | agrees | loftr+magsac++ | 142.4 |
| `strip_tmc20200607_iirs1555_s005` | 58.6562, 354.8242 | 0.0 | 16.178 | 379 | 373 | 0.984 | 0.84 | 0.224 (18.815) | 0.678 | 53 / 10 | agrees | loftr+magsac++ | 158.5 |
| `strip_tmc20200607_iirs1555_s006` | 58.1184, 354.8306 | 0.0 | 16.176 | 371 | 362 | 0.976 | 0.84 | 0.351 (29.533) | 0.687 | 48 / 10 | agrees | loftr+magsac++ | 158.8 |
| `strip_tmc20200607_iirs1555_s007` | 57.5806, 354.8367 | 0.0 | 16.177 | 342 | 338 | 0.988 | 0.88 | 0.216 (18.191) | 0.542 | 52 / 8 | agrees | loftr+magsac++ | 153.2 |
| `strip_tmc20200607_iirs1555_s008` | 57.0429, 354.8426 | 0.0 | 16.181 | 315 | 310 | 0.984 | 0.86 | 0.205 (17.208) | 0.508 | 52 / 9 | agrees | loftr+magsac++ | 153.3 |
| `strip_tmc20200607_iirs1555_s009` | 56.5052, 354.8483 | 0.0 | 16.182 | 399 | 399 | 1.000 | 0.88 | 0.191 (16.088) | 0.377 | 54 / 8 | agrees | loftr+magsac++ | 155.7 |
| `strip_tmc20200607_iirs1555_s010` | 55.9676, 354.8537 | 0.0 | 16.176 | 400 | 400 | 1.000 | 0.88 | 0.188 (15.824) | 0.332 | 55 / 8 | agrees | loftr+magsac++ | 151.9 |
| `strip_tmc20200607_iirs1555_s011` | 55.4300, 354.8591 | 0.0 | 16.18 | 400 | 400 | 1.000 | 0.88 | 0.155 (13.016) | 0.274 | 55 / 8 | agrees | loftr+magsac++ | 151.1 |
| `strip_tmc20200607_iirs1555_s012` | 54.8924, 354.8642 | 0.0 | 16.181 | 400 | 400 | 1.000 | 0.88 | 0.181 (15.194) | 0.253 | 55 / 8 | agrees | loftr+magsac++ | 157.4 |
| `strip_tmc20200607_iirs1555_s013` | 54.3548, 354.8691 | 0.0 | 16.182 | 400 | 400 | 1.000 | 0.88 | 0.168 (14.125) | 0.264 | 55 / 8 | agrees | loftr+magsac++ | 158.6 |
| `strip_tmc20200607_iirs1555_s014` | 53.8173, 354.8739 | 0.0 | 16.18 | 397 | 395 | 0.995 | 0.88 | 0.162 (13.629) | 0.269 | 55 / 8 | agrees | loftr+magsac++ | 157.4 |
| `strip_tmc20200607_iirs1555_s015` | 53.2797, 354.8785 | 0.0 | 16.178 | 399 | 399 | 1.000 | 0.88 | 0.198 (16.667) | 0.484 | 55 / 8 | agrees | loftr+magsac++ | 165.7 |
| `strip_tmc20200607_iirs1555_s016` | 52.7423, 354.8829 | 0.0 | 16.179 | 398 | 397 | 0.997 | 0.89 | 0.177 (14.922) | 0.381 | 55 / 7 | agrees | loftr+magsac++ | 162.8 |
| `strip_tmc20200607_iirs1555_s017` | 52.2048, 354.8872 | 0.0 | 16.179 | 381 | 375 | 0.984 | 0.89 | 0.191 (16.099) | 0.514 | 55 / 7 | agrees | loftr+magsac++ | 163.6 |
| `strip_tmc20200607_iirs1555_s018` | 51.6674, 354.8914 | 0.0 | 16.18 | 396 | 392 | 0.990 | 0.86 | 0.200 (16.882) | 0.648 | 54 / 9 | agrees | loftr+magsac++ | 168.9 |
| `strip_tmc20200607_iirs1555_s019` | 51.1300, 354.8955 | 0.0 | 16.181 | 396 | 395 | 0.997 | 0.88 | 0.216 (18.228) | 0.405 | 54 / 8 | agrees | loftr+magsac++ | 169.0 |
| `strip_tmc20200607_iirs1555_s020` | 50.5927, 354.8994 | 0.0 | 16.179 | 391 | 389 | 0.995 | 0.89 | 0.242 (20.423) | 0.387 | 55 / 7 | agrees | loftr+magsac++ | 171.0 |
| `strip_tmc20200607_iirs1555_s021` | 50.0553, 354.9032 | 0.0 | 16.177 | 373 | 369 | 0.989 | 0.89 | 0.300 (25.285) | 0.773 | 54 / 7 | agrees | loftr+magsac++ | 170.2 |
| `strip_tmc20200607_iirs1555_s022` | 49.5180, 354.9068 | 0.0 | 16.178 | 363 | 360 | 0.992 | 0.91 | 0.336 (28.361) | 0.596 | 51 / 6 | agrees | loftr+magsac++ | 167.7 |
| `strip_tmc20200607_iirs1555_s023` | 49.1150, 354.9095 | 0.0 | 16.179 | 338 | 332 | 0.982 | 0.88 | 0.267 (22.529) | 0.636 | 51 / 8 | agrees | loftr+magsac++ | 172.1 |
| `strip_tmc20200607_iirs1555_s024` | 48.5778, 354.9130 | 0.0 | 16.178 | 374 | 368 | 0.984 | 0.89 | 0.328 (27.709) | 0.763 | 52 / 7 | agrees | loftr+magsac++ | 165.9 |
| `strip_tmc20200607_iirs1555_s025` | 48.0406, 354.9163 | 0.0 | 16.178 | 306 | 298 | 0.974 | 0.89 | 0.687 (57.970) | 0.935 | 48 / 7 | agrees | loftr+magsac++ | 163.0 |
| `strip_tmc20200607_iirs1555_s026` | 47.5034, 354.9196 | 0.0 | 16.179 | 364 | 355 | 0.975 | 0.91 | 0.524 (44.180) | 0.844 | 48 / 6 | agrees | loftr+magsac++ | 173.6 |
| `strip_tmc20200607_iirs1555_s027` | 46.9662, 354.9228 | 0.0 | 16.18 | 268 | 250 | 0.933 | 0.81 | 0.459 (38.735) | 0.867 | 39 / 12 | agrees | loftr+magsac++ | 168.2 |
| `strip_tmc20200607_iirs1555_s028` | 46.4290, 354.9258 | 0.0 | 16.181 | 248 | 211 | 0.851 | 0.80 | 0.948 (80.008) | 1.311 | 34 / 13 | agrees | loftr+magsac++ | 154.1 |
| `strip_tmc20200607_iirs1555_s029` | 45.8919, 354.9288 | 0.0 | 16.178 | 326 | 321 | 0.985 | 0.89 | 0.609 (51.447) | 0.953 | 51 / 7 | agrees | loftr+magsac++ | 155.0 |
| `strip_tmc20200607_iirs1555_s030` | 45.3548, 354.9317 | 0.0 | 16.177 | 247 | 232 | 0.939 | 0.80 | 0.607 (51.235) | 0.912 | 37 / 13 | agrees | loftr+magsac++ | 151.8 |
| `strip_tmc20200607_iirs1555_s031` | 44.8177, 354.9345 | 0.0 | 16.178 | 273 | 261 | 0.956 | 0.86 | 0.686 (57.927) | 0.893 | 42 / 9 | agrees | loftr+magsac++ | 156.4 |
| `strip_tmc20200607_iirs1555_s032` | 44.2807, 354.9372 | 0.0 | 16.178 | 225 | 202 | 0.898 | 0.75 | 0.689 (58.191) | 0.828 | 30 / 16 | agrees | loftr+magsac++ | 162.9 |
| `strip_tmc20200607_iirs1555_s033` | 43.7437, 354.9398 | 0.0 | 16.179 | 293 | 283 | 0.966 | 0.86 | 0.658 (55.576) | 0.728 | 44 / 9 | agrees | loftr+magsac++ | 153.9 |
| `strip_tmc20200607_iirs1555_s034` | 43.2067, 354.9424 | 0.0 | 16.175 | 321 | 312 | 0.972 | 0.88 | 0.506 (42.745) | 0.795 | 44 / 8 | agrees | loftr+magsac++ | 149.8 |
| `strip_tmc20200607_iirs1555_s035` | 42.6697, 354.9449 | 0.0 | 16.176 | 352 | 344 | 0.977 | 0.89 | 0.393 (33.193) | 0.752 | 45 / 7 | agrees | loftr+magsac++ | 146.2 |
| `strip_tmc20200607_iirs1555_s036` | 42.1328, 354.9473 | 0.0 | 16.176 | 377 | 371 | 0.984 | 0.88 | 0.393 (33.227) | 0.632 | 49 / 8 | agrees | loftr+magsac++ | 154.6 |
| `strip_tmc20200607_iirs1555_s037` | 41.5958, 354.9497 | 0.0 | 16.177 | 349 | 342 | 0.980 | 0.91 | 0.362 (30.647) | 0.709 | 47 / 6 | agrees | loftr+magsac++ | 146.4 |
| `strip_tmc20200607_iirs1555_s038` | 41.0589, 354.9519 | 0.0 | 16.176 | 353 | 345 | 0.977 | 0.91 | 0.271 (22.893) | 0.542 | 51 / 6 | agrees | loftr+magsac++ | 153.2 |
| `strip_tmc20200607_iirs1555_s039` | 40.5221, 354.9542 | 0.0 | 16.177 | 356 | 351 | 0.986 | 0.89 | 0.266 (22.539) | 0.765 | 49 / 7 | agrees | loftr+magsac++ | 145.0 |
| `strip_tmc20200607_iirs1555_s040` | 39.9852, 354.9563 | 0.0 | 16.177 | 381 | 371 | 0.974 | 0.94 | 0.184 (15.580) | 0.400 | 52 / 4 | agrees | loftr+magsac++ | 153.4 |
| `strip_tmc20200607_iirs1555_s041` | 39.4484, 354.9584 | 0.0 | 16.178 | 367 | 361 | 0.984 | 0.88 | 0.260 (22.000) | 0.544 | 50 / 8 | agrees | loftr+magsac++ | 152.2 |
| `strip_tmc20200607_iirs1555_s042` | 38.9116, 354.9604 | 0.0 | 16.177 | 390 | 386 | 0.990 | 0.95 | 0.173 (14.648) | 0.257 | 50 / 3 | agrees | loftr+magsac++ | 157.1 |
| `strip_tmc20200607_iirs1555_s043` | 38.3748, 354.9624 | 0.0 | 16.178 | 363 | 362 | 0.997 | 0.88 | 0.202 (17.102) | 0.439 | 50 / 8 | agrees | loftr+magsac++ | 154.0 |
| `strip_tmc20200607_iirs1555_s044` | 37.8381, 354.9643 | 0.0 | 16.178 | 315 | 309 | 0.981 | 0.94 | 0.213 (18.054) | 0.455 | 42 / 4 | agrees | loftr+magsac++ | 149.9 |
| `strip_tmc20200607_iirs1555_s045` | 37.3013, 354.9662 | 0.0 | 16.177 | 359 | 353 | 0.983 | 0.95 | 0.207 (17.500) | 0.398 | 50 / 3 | agrees | loftr+magsac++ | 154.3 |
| `strip_tmc20200607_iirs1555_s046` | 36.7647, 354.9680 | 0.0 | 16.178 | 339 | 337 | 0.994 | 0.91 | 0.237 (20.111) | 0.623 | 48 / 6 | agrees | loftr+magsac++ | 151.3 |
| `strip_tmc20200607_iirs1555_s047` | 36.2280, 354.9698 | 0.0 | 16.177 | 375 | 371 | 0.989 | 0.89 | 0.238 (20.211) | 0.492 | 51 / 7 | agrees | loftr+magsac++ | 158.0 |
| `strip_tmc20200607_iirs1555_s048` | 35.6913, 354.9715 | 0.0 | 16.177 | 372 | 363 | 0.976 | 0.91 | 0.226 (19.195) | 0.517 | 49 / 6 | agrees | loftr+magsac++ | 166.6 |
| `strip_tmc20200607_iirs1555_s049` | 35.1547, 354.9732 | 0.0 | 16.176 | 392 | 392 | 1.000 | 0.91 | 0.188 (15.976) | 0.411 | 50 / 6 | agrees | loftr+magsac++ | 169.9 |
| `strip_tmc20200607_iirs1555_s050` | 34.6181, 354.9748 | 0.0 | 16.177 | 393 | 393 | 1.000 | 0.89 | 0.176 (14.953) | 0.510 | 49 / 7 | agrees | loftr+magsac++ | 168.3 |
| `strip_tmc20200607_iirs1555_s051` | 34.0816, 354.9764 | 0.0 | 16.178 | 395 | 394 | 0.997 | 0.91 | 0.174 (14.769) | 0.353 | 49 / 6 | agrees | loftr+magsac++ | 171.6 |
| `strip_tmc20200607_iirs1555_s052` | 33.5450, 354.9779 | 0.0 | 16.177 | 359 | 347 | 0.967 | 0.84 | 0.224 (18.995) | 0.479 | 47 / 10 | agrees | loftr+magsac++ | 181.9 |
| `strip_tmc20200607_iirs1555_s053` | 33.0085, 354.9794 | 0.0 | 16.177 | 270 | 263 | 0.974 | 0.81 | 0.290 (24.631) | 0.644 | 40 / 12 | agrees | loftr+magsac++ | 183.4 |
| `strip_tmc20200607_iirs1555_s054` | 32.4720, 354.9809 | 0.0 | 16.176 | 337 | 329 | 0.976 | 0.83 | 0.257 (21.828) | 0.654 | 46 / 11 | agrees | loftr+magsac++ | 173.7 |
| `strip_tmc20200607_iirs1555_s055` | 31.9355, 354.9823 | 0.0 | 16.177 | 235 | 224 | 0.953 | 0.80 | 0.167 (14.188) | 0.271 | 36 / 13 | agrees | loftr+magsac++ | 180.8 |
| `strip_tmc20200607_iirs1555_s056` | 31.3991, 354.9837 | 0.0 | 16.176 | 252 | 237 | 0.940 | 0.86 | 0.404 (34.298) | 0.876 | 33 / 9 | agrees | loftr+magsac++ | 194.8 |
| `strip_tmc20200607_iirs1555_s057` | 30.8626, 354.9851 | 0.0 | 16.182 | 377 | 374 | 0.992 | 0.89 | 0.226 (19.224) | 0.447 | 50 / 7 | agrees | loftr+magsac++ | 188.3 |
| `strip_tmc20200607_iirs1555_s058` | 30.3263, 354.9864 | 0.0 | 16.19 | 371 | 369 | 0.995 | 0.86 | 0.206 (17.551) | 0.530 | 48 / 9 | agrees | loftr+magsac++ | 190.0 |

## IIRS → LRO WAC global mosaic (cross-mission, multi-modal)

Chandrayaan-2 IIRS onto NASA's Moon-wide base map, the USGS LRO WAC global morphologic mosaic (100 m, visible 643 nm; `ops/cut_wac_pairs.py`, read by HTTP range): cross-sensor AND cross-mission, and multi-modal at 1555 nm. The windows are exactly those of the TMC-2 → IIRS chain pairs (chosen from the IIRS texture alone, before any matching). The mosaic is a composite with no single Sun. Verdicts: agrees 12, contradicted 4; **accepted 12/16** (the same IIRS windows onto TMC-2 of their own orbit: accepted 16/16); held-out median of the accepted: 0.70-1.63 px on the 100 m WAC grid. Reported only here, never merged with the counts above.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `wac_iirs20200203_1555_w01` | -4.3757, 24.9058 | n/a | 1.354 | 108 | 93 | 0.861 | 0.61 | 1.242 (124.169) | 1.369 | 0 / 25 | contradicted | fft_phase_correlation (fallback) | 502.8 |
| `wac_iirs20200203_1555_w02` | -10.3175, 24.9038 | n/a | 1.355 | 135 | 129 | 0.956 | 0.67 | 0.696 (69.599) | 0.989 | 0 / 21 | agrees | loftr+magsac++ | 81.6 |
| `wac_iirs20200203_1555_w03` | -10.8703, 24.9036 | n/a | 1.355 | 33 | 6 | 0.182 | 0.09 | 46.935 (4693.511) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 169.2 |
| `wac_iirs20200203_1555_w04` | -12.2521, 24.9031 | n/a | 1.355 | 162 | 159 | 0.981 | 0.69 | 0.918 (91.807) | 1.288 | 0 / 20 | agrees | loftr+magsac++ | 103.0 |
| `wac_iirs20200203_1555_w05` | -12.8049, 24.9028 | n/a | 1.355 | 86 | 72 | 0.837 | 0.48 | 1.010 (101.030) | 1.002 | 0 / 33 | agrees | loftr+magsac++ | 117.5 |
| `wac_iirs20200203_1555_w06` | -24.6853, 24.8962 | n/a | 1.35 | 106 | 92 | 0.868 | 0.53 | 1.634 (163.397) | 1.695 | 0 / 30 | agrees | loftr+magsac++ | 114.2 |
| `wac_iirs20200203_1555_w07` | -26.6182, 24.8946 | n/a | 1.349 | 54 | 33 | 0.611 | 0.20 | 2.388 (238.753) | 1.685 | 0 / 51 | contradicted | fft_phase_correlation (fallback) | 173.5 |
| `wac_iirs20200203_1555_w08` | -27.1704, 24.8941 | n/a | 1.349 | 70 | 50 | 0.714 | 0.38 | 0.754 (75.434) | 0.990 | 0 / 40 | contradicted | fft_phase_correlation (fallback) | 1824.5 |
| `wac_iirs20200607_1555_w01` | 60.6731, 354.7980 | n/a | 1.195 | 217 | 202 | 0.931 | 0.94 | 1.028 (102.828) | 1.144 | 0 / 4 | agrees | loftr+magsac++ | 79.3 |
| `wac_iirs20200607_1555_w02` | 59.5974, 354.8125 | n/a | 1.191 | 207 | 191 | 0.923 | 0.92 | 1.214 (121.407) | 1.501 | 0 / 4 | agrees | loftr+magsac++ | 200.4 |
| `wac_iirs20200607_1555_w03` | 58.6562, 354.8242 | n/a | 1.19 | 201 | 169 | 0.841 | 0.81 | 0.880 (87.958) | 1.195 | 0 / 12 | agrees | loftr+magsac++ | 217.3 |
| `wac_iirs20200607_1555_w04` | 57.7151, 354.8352 | n/a | 1.19 | 156 | 113 | 0.724 | 0.66 | 1.173 (117.260) | 1.378 | 0 / 22 | agrees | loftr+magsac++ | 194.1 |
| `wac_iirs20200607_1555_w05` | 56.2364, 354.8510 | n/a | 1.189 | 241 | 212 | 0.880 | 0.91 | 0.969 (96.870) | 1.194 | 0 / 5 | agrees | loftr+magsac++ | 199.9 |
| `wac_iirs20200607_1555_w06` | 54.6236, 354.8667 | n/a | 1.188 | 104 | 70 | 0.673 | 0.53 | 1.429 (142.887) | 1.441 | 0 / 32 | agrees | loftr+magsac++ | 262.6 |
| `wac_iirs20200607_1555_w07` | 52.7423, 354.8829 | n/a | 1.188 | 148 | 112 | 0.757 | 0.64 | 1.523 (152.267) | 1.167 | 0 / 24 | agrees | loftr+magsac++ | 221.1 |
| `wac_iirs20200607_1555_w08` | 51.6674, 354.8914 | n/a | 1.187 | 173 | 153 | 0.884 | 0.86 | 0.868 (86.848) | 1.176 | 0 / 9 | agrees | loftr+magsac++ | 259.8 |

## IIRS → LRO WAC, the whole strip, region by region (cross-mission, multi-modal)

The whole Chandrayaan-2 IIRS strip `ch2_iir_nci_20200607T2239153893_d_img_d18 band 51 (1555.0 nm)` onto NASA's Moon-wide base map, the USGS LRO WAC global morphologic mosaic (100 m, visible 643 nm), every window edge to edge with no selection (`ops/cut_wac_pairs.py --strip`): cross-sensor, cross-mission and multi-modal (1555 nm against the visible). The windows are 192 WAC pixels (19.2 km) so that each of the 8 × 8 squares is 24 px, the smallest the area check lets vote (`core/reliability.py` MIN_CELL_SIDE_PX): every verdict here is region by region, unlike the 16 smaller windows in the section above, whose squares were too small to vote. 49 windows, latitude 30.3-60.7°. Verdicts: agrees 44, unconfirmed 3, contradicted 2; **accepted 44/49**; verified squares per accepted window 0-34 of 64 (median 15.5); held-out median of the accepted windows above an inlier ratio of 0.5: 0.91-4.81 px = 91-481 m on the 100 m WAC grid, median 1.58 px = 158 m (39 windows). Registration 0.8 min on the laptop CPU. Reported only here, never merged with the counts above.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `wacstrip_iirs20200607_1555_s002` | 60.6731, 354.7980 | n/a | 1.195 | 193 | 162 | 0.839 | 0.69 | 1.318 (131.797) | 1.350 | 20 / 20 | agrees | loftr+magsac++ | 89.2 |
| `wacstrip_iirs20200607_1555_s003` | 60.0007, 354.8072 | n/a | 1.191 | 137 | 108 | 0.788 | 0.67 | 0.913 (91.301) | 1.080 | 19 / 22 | agrees | loftr+magsac++ | 155.3 |
| `wacstrip_iirs20200607_1555_s004` | 59.4629, 354.8142 | n/a | 1.191 | 163 | 127 | 0.779 | 0.58 | 1.738 (173.770) | 1.427 | 20 / 27 | agrees | loftr+magsac++ | 234.5 |
| `wacstrip_iirs20200607_1555_s005` | 58.7906, 354.8226 | n/a | 1.19 | 195 | 135 | 0.692 | 0.62 | 1.607 (160.719) | 1.303 | 19 / 24 | agrees | loftr+magsac++ | 249.9 |
| `wacstrip_iirs20200607_1555_s006` | 58.1184, 354.8306 | n/a | 1.19 | 217 | 170 | 0.783 | 0.72 | 1.476 (147.620) | 1.342 | 23 / 18 | agrees | loftr+magsac++ | 189.4 |
| `wacstrip_iirs20200607_1555_s007` | 57.4462, 354.8382 | n/a | 1.19 | 134 | 98 | 0.731 | 0.59 | 1.610 (161.024) | 1.389 | 14 / 27 | agrees | loftr+magsac++ | 169.1 |
| `wacstrip_iirs20200607_1555_s008` | 56.9085, 354.8440 | n/a | 1.189 | 174 | 129 | 0.741 | 0.58 | 1.439 (143.912) | 1.451 | 20 / 26 | agrees | loftr+magsac++ | 201.7 |
| `wacstrip_iirs20200607_1555_s009` | 56.2364, 354.8510 | n/a | 1.189 | 261 | 238 | 0.912 | 0.89 | 1.165 (116.507) | 1.216 | 30 / 7 | agrees | loftr+magsac++ | 162.6 |
| `wacstrip_iirs20200607_1555_s010` | 55.5644, 354.8577 | n/a | 1.189 | 252 | 210 | 0.833 | 0.84 | 1.085 (108.480) | 1.181 | 31 / 10 | agrees | loftr+magsac++ | 212.9 |
| `wacstrip_iirs20200607_1555_s011` | 55.0268, 354.8629 | n/a | 1.189 | 296 | 255 | 0.861 | 0.83 | 1.040 (103.990) | 1.356 | 34 / 11 | agrees | loftr+magsac++ | 199.6 |
| `wacstrip_iirs20200607_1555_s012` | 54.3548, 354.8691 | n/a | 1.188 | 74 | 31 | 0.419 | 0.30 | 4.003 (400.282) | 1.803 | 2 / 45 | agrees | loftr+magsac++ | 277.8 |
| `wacstrip_iirs20200607_1555_s013` | 53.6829, 354.8750 | n/a | 1.188 | 30 | 6 | 0.200 | 0.08 | 59.743 (5974.328) | 1.360 | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 6.8 |
| `wacstrip_iirs20200607_1555_s014` | 53.0110, 354.8807 | n/a | 1.188 | 174 | 133 | 0.764 | 0.62 | 1.699 (169.861) | 1.593 | 16 / 24 | agrees | loftr+magsac++ | 214.0 |
| `wacstrip_iirs20200607_1555_s015` | 52.4736, 354.8851 | n/a | 1.187 | 140 | 90 | 0.643 | 0.55 | 2.390 (238.978) | 1.547 | 10 / 28 | agrees | loftr+magsac++ | 181.3 |
| `wacstrip_iirs20200607_1555_s016` | 51.8018, 354.8904 | n/a | 1.187 | 185 | 121 | 0.654 | 0.67 | 1.583 (158.348) | 1.422 | 17 / 21 | agrees | loftr+magsac++ | 234.2 |
| `wacstrip_iirs20200607_1555_s017` | 51.1300, 354.8955 | n/a | 1.187 | 73 | 25 | 0.342 | 0.31 | 40.023 (4002.306) | 1.163 | 1 / 44 | agrees | loftr+magsac++ | 208.0 |
| `wacstrip_iirs20200607_1555_s018` | 50.5927, 354.8994 | n/a | 1.186 | 198 | 156 | 0.788 | 0.75 | 1.257 (125.660) | 1.198 | 24 / 16 | agrees | loftr+magsac++ | 251.7 |
| `wacstrip_iirs20200607_1555_s019` | 49.9210, 354.9041 | n/a | 1.186 | 227 | 195 | 0.859 | 0.83 | 1.311 (131.100) | 1.411 | 31 / 10 | agrees | loftr+magsac++ | 226.9 |
| `wacstrip_iirs20200607_1555_s020` | 49.2494, 354.9086 | n/a | 1.186 | 100 | 60 | 0.600 | 0.41 | 2.550 (254.978) | 1.834 | 9 / 39 | agrees | loftr+magsac++ | 349.7 |
| `wacstrip_iirs20200607_1555_s021` | 48.5778, 354.9130 | n/a | 1.186 | 229 | 182 | 0.795 | 0.84 | 1.384 (138.408) | 1.419 | 26 / 10 | agrees | loftr+magsac++ | 245.0 |
| `wacstrip_iirs20200607_1555_s022` | 48.0406, 354.9163 | n/a | 1.185 | 119 | 82 | 0.689 | 0.47 | 1.712 (171.219) | 1.708 | 10 / 35 | agrees | loftr+magsac++ | 209.1 |
| `wacstrip_iirs20200607_1555_s023` | 47.3691, 354.9204 | n/a | 1.185 | 176 | 147 | 0.835 | 0.75 | 1.609 (160.870) | 1.541 | 25 / 16 | agrees | loftr+magsac++ | 241.8 |
| `wacstrip_iirs20200607_1555_s024` | 46.6976, 354.9243 | n/a | 1.185 | 81 | 49 | 0.605 | 0.33 | 2.195 (219.522) | 1.630 | 5 / 43 | agrees | loftr+magsac++ | 306.0 |
| `wacstrip_iirs20200607_1555_s025` | 46.1605, 354.9273 | n/a | 1.184 | 119 | 71 | 0.597 | 0.53 | 2.360 (236.047) | 1.281 | 8 / 30 | agrees | loftr+magsac++ | 259.6 |
| `wacstrip_iirs20200607_1555_s026` | 45.4891, 354.9310 | n/a | 1.184 | 178 | 141 | 0.792 | 0.62 | 0.991 (99.112) | 1.293 | 22 / 23 | agrees | loftr+magsac++ | 187.9 |
| `wacstrip_iirs20200607_1555_s027` | 44.8177, 354.9345 | n/a | 1.184 | 114 | 71 | 0.623 | 0.42 | 2.499 (249.930) | 1.686 | 11 / 38 | agrees | loftr+magsac++ | 262.8 |
| `wacstrip_iirs20200607_1555_s028` | 44.1464, 354.9379 | n/a | 1.183 | 46 | 13 | 0.283 | 0.12 | 18.439 (1843.942) | 2.052 | 0 / 56 | contradicted | fft_phase_correlation (fallback) | 348.9 |
| `wacstrip_iirs20200607_1555_s029` | 43.6094, 354.9405 | n/a | 1.183 | 157 | 115 | 0.732 | 0.64 | 1.202 (120.172) | 1.231 | 16 / 24 | agrees | loftr+magsac++ | 258.3 |
| `wacstrip_iirs20200607_1555_s030` | 42.9382, 354.9437 | n/a | 1.183 | 83 | 47 | 0.566 | 0.33 | 1.455 (145.535) | 1.310 | 6 / 43 | agrees | loftr+magsac++ | 266.5 |
| `wacstrip_iirs20200607_1555_s031` | 42.2670, 354.9467 | n/a | 1.182 | 149 | 106 | 0.711 | 0.62 | 2.042 (204.190) | 1.285 | 15 / 25 | agrees | loftr+magsac++ | 308.4 |
| `wacstrip_iirs20200607_1555_s032` | 41.7301, 354.9491 | n/a | 1.182 | 117 | 72 | 0.615 | 0.48 | 2.217 (221.746) | 1.672 | 8 / 35 | agrees | loftr+magsac++ | 313.7 |
| `wacstrip_iirs20200607_1555_s033` | 41.0589, 354.9519 | n/a | 1.182 | 127 | 81 | 0.638 | 0.53 | 1.951 (195.142) | 1.724 | 10 / 31 | agrees | loftr+magsac++ | 292.9 |
| `wacstrip_iirs20200607_1555_s034` | 40.3879, 354.9547 | n/a | 1.182 | 72 | 23 | 0.319 | 0.22 | 5.431 (543.128) | 1.476 | 3 / 49 | unconfirmed | loftr+magsac++ | 502.2 |
| `wacstrip_iirs20200607_1555_s035` | 39.7168, 354.9574 | n/a | 1.181 | 155 | 106 | 0.684 | 0.62 | 1.571 (157.092) | 1.500 | 16 / 24 | agrees | loftr+magsac++ | 382.1 |
| `wacstrip_iirs20200607_1555_s036` | 39.1800, 354.9594 | n/a | 1.181 | 195 | 146 | 0.749 | 0.75 | 1.249 (124.945) | 1.320 | 17 / 16 | agrees | loftr+magsac++ | 370.3 |
| `wacstrip_iirs20200607_1555_s037` | 38.5090, 354.9619 | n/a | 1.181 | 114 | 80 | 0.702 | 0.56 | 2.031 (203.078) | 1.707 | 10 / 28 | agrees | loftr+magsac++ | 276.8 |
| `wacstrip_iirs20200607_1555_s038` | 37.8381, 354.9643 | n/a | 1.18 | 103 | 53 | 0.515 | 0.38 | 2.346 (234.602) | 1.738 | 6 / 40 | unconfirmed | loftr+magsac++ | 418.5 |
| `wacstrip_iirs20200607_1555_s039` | 37.3013, 354.9662 | n/a | 1.18 | 137 | 95 | 0.693 | 0.61 | 1.529 (152.850) | 1.554 | 13 / 24 | agrees | loftr+magsac++ | 216.0 |
| `wacstrip_iirs20200607_1555_s040` | 36.6305, 354.9685 | n/a | 1.18 | 68 | 20 | 0.294 | 0.19 | 20.455 (2045.550) | 2.026 | 0 / 51 | agrees | loftr+magsac++ | 320.8 |
| `wacstrip_iirs20200607_1555_s041` | 35.9597, 354.9706 | n/a | 1.18 | 193 | 149 | 0.772 | 0.73 | 1.553 (155.311) | 1.206 | 22 / 17 | agrees | loftr+magsac++ | 328.8 |
| `wacstrip_iirs20200607_1555_s042` | 35.2889, 354.9728 | n/a | 1.18 | 81 | 32 | 0.395 | 0.25 | 5.624 (562.384) | 1.814 | 4 / 47 | agrees | loftr+magsac++ | 234.2 |
| `wacstrip_iirs20200607_1555_s043` | 34.7523, 354.9744 | n/a | 1.179 | 104 | 55 | 0.529 | 0.45 | 4.809 (480.864) | 1.293 | 5 / 34 | agrees | loftr+magsac++ | 312.4 |
| `wacstrip_iirs20200607_1555_s044` | 34.0816, 354.9764 | n/a | 1.179 | 230 | 189 | 0.822 | 0.88 | 1.235 (123.542) | 1.252 | 25 / 8 | agrees | loftr+magsac++ | 326.8 |
| `wacstrip_iirs20200607_1555_s045` | 33.4109, 354.9783 | n/a | 1.179 | 114 | 70 | 0.614 | 0.41 | 2.152 (215.189) | 1.498 | 10 / 37 | agrees | loftr+magsac++ | 293.7 |
| `wacstrip_iirs20200607_1555_s046` | 32.7402, 354.9802 | n/a | 1.179 | 75 | 41 | 0.547 | 0.31 | 2.878 (287.814) | 1.883 | 2 / 43 | unconfirmed | loftr+magsac++ | 512.0 |
| `wacstrip_iirs20200607_1555_s047` | 32.2038, 354.9816 | n/a | 1.178 | 112 | 71 | 0.634 | 0.45 | 1.896 (189.598) | 1.876 | 6 / 34 | agrees | loftr+magsac++ | 565.2 |
| `wacstrip_iirs20200607_1555_s048` | 31.5332, 354.9834 | n/a | 1.178 | 65 | 36 | 0.554 | 0.34 | 3.777 (377.722) | 1.152 | 2 / 42 | agrees | loftr+magsac++ | 252.0 |
| `wacstrip_iirs20200607_1555_s049` | 30.8626, 354.9851 | n/a | 1.177 | 193 | 144 | 0.746 | 0.66 | 1.423 (142.306) | 1.447 | 17 / 22 | agrees | loftr+magsac++ | 375.8 |
| `wacstrip_iirs20200607_1555_s050` | 30.3263, 354.9864 | n/a | 1.176 | 136 | 68 | 0.500 | 0.55 | 3.818 (381.804) | 1.993 | 8 / 28 | agrees | loftr+magsac++ | 358.9 |

## TMC-2 → SELENE TC ortho map at SAC's site, every window (cross-mission)

Every window along one Chandrayaan-2 TMC-2 pass at SAC's own site (`ops/cut_tc_pairs.py`): TMC-2 nadir `ch2_tmc_ncn_20250707T1853051045_d_img_d18` onto the SELENE (Kaguya) Terrain Camera ortho map `TCO_MAP_02_S12E024S15E027SC` (JAXA; 7.40 m, a mosaic with no single Sun). Cross-sensor and cross-mission; both panchromatic visible, so NOT multi-modal. 31 windows of 2.84 km edge to edge, latitude -14.92 to -12.11° (the whole TC tile), no selection. Verdicts: agrees 31; **accepted 31/31**; verified squares per accepted window 7-35 of 64 (median 22); held-out median of the accepted windows above an inlier ratio of 0.5: 0.88-9.30 px = 6.5-68.8 m on the 7.40 m TC grid, median 1.58 px = 11.7 m (21 windows). The archive geolocations disagree by 273-315 m (median 287 m) - one steady offset along 3° of the pass, which each registration removes. Reported only here, never merged with the counts above.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `tcmap_tmc20250707_s001` | -12.1060, 25.1042 | n/a | 1.327 | 537 | 391 | 0.728 | 0.81 | 1.276 (9.444) | 1.308 | 35 / 12 | agrees | loftr+magsac++ | 293.0 |
| `tcmap_tmc20250707_s002` | -12.2025, 25.1009 | n/a | 1.327 | 391 | 244 | 0.624 | 0.64 | 2.065 (15.288) | 1.170 | 24 / 23 | agrees | loftr+magsac++ | 293.3 |
| `tcmap_tmc20250707_s003` | -12.2989, 25.0977 | n/a | 1.327 | 548 | 434 | 0.792 | 0.73 | 0.879 (6.511) | 1.156 | 34 / 17 | agrees | loftr+magsac++ | 289.5 |
| `tcmap_tmc20250707_s004` | -12.3792, 25.0950 | n/a | 1.327 | 384 | 273 | 0.711 | 0.64 | 1.547 (11.452) | 1.354 | 25 / 23 | agrees | loftr+magsac++ | 289.0 |
| `tcmap_tmc20250707_s005` | -12.4756, 25.0917 | n/a | 1.327 | 373 | 242 | 0.649 | 0.59 | 1.805 (13.362) | 1.365 | 24 / 27 | agrees | loftr+magsac++ | 287.5 |
| `tcmap_tmc20250707_s006` | -12.5722, 25.0883 | n/a | 1.327 | 366 | 261 | 0.713 | 0.62 | 1.447 (10.716) | 1.404 | 27 / 24 | agrees | loftr+magsac++ | 287.5 |
| `tcmap_tmc20250707_s007` | -12.6688, 25.0849 | n/a | 1.327 | 469 | 335 | 0.714 | 0.69 | 2.400 (17.764) | 1.391 | 32 / 20 | agrees | loftr+magsac++ | 285.9 |
| `tcmap_tmc20250707_s008` | -12.7653, 25.0816 | n/a | 1.327 | 438 | 288 | 0.658 | 0.70 | 1.581 (11.703) | 1.451 | 31 / 19 | agrees | loftr+magsac++ | 285.7 |
| `tcmap_tmc20250707_s009` | -12.8618, 25.0783 | n/a | 1.327 | 220 | 116 | 0.527 | 0.39 | 3.017 (22.334) | 1.588 | 13 / 39 | agrees | loftr+magsac++ | 291.1 |
| `tcmap_tmc20250707_s010` | -12.9423, 25.0755 | n/a | 1.327 | 195 | 64 | 0.328 | 0.48 | 4.518 (33.451) | 1.968 | 8 / 32 | agrees | loftr+magsac++ | 285.1 |
| `tcmap_tmc20250707_s011` | -13.0388, 25.0722 | n/a | 1.327 | 211 | 81 | 0.384 | 0.44 | 3.434 (25.426) | 1.558 | 9 / 36 | agrees | loftr+magsac++ | 288.7 |
| `tcmap_tmc20250707_s012` | -13.1352, 25.0689 | n/a | 1.327 | 239 | 129 | 0.540 | 0.55 | 4.410 (32.648) | 1.522 | 16 / 29 | agrees | loftr+magsac++ | 285.4 |
| `tcmap_tmc20250707_s013` | -13.2316, 25.0656 | n/a | 1.327 | 358 | 218 | 0.609 | 0.64 | 2.362 (17.489) | 1.626 | 23 / 24 | agrees | loftr+magsac++ | 285.4 |
| `tcmap_tmc20250707_s014` | -13.3282, 25.0622 | n/a | 1.327 | 336 | 200 | 0.595 | 0.62 | 1.833 (13.571) | 1.287 | 23 / 24 | agrees | loftr+magsac++ | 284.4 |
| `tcmap_tmc20250707_s015` | -13.4098, 25.0586 | n/a | 1.327 | 360 | 235 | 0.653 | 0.67 | 1.456 (10.776) | 1.368 | 26 / 21 | agrees | loftr+magsac++ | 298.5 |
| `tcmap_tmc20250707_s016` | -13.5073, 25.0545 | n/a | 1.327 | 195 | 83 | 0.426 | 0.34 | 5.593 (41.407) | 1.526 | 7 / 42 | agrees | loftr+magsac++ | 315.3 |
| `tcmap_tmc20250707_s017` | -13.6010, 25.0533 | n/a | 1.328 | 210 | 102 | 0.486 | 0.44 | 6.742 (49.916) | 1.504 | 16 / 36 | agrees | loftr+magsac++ | 286.5 |
| `tcmap_tmc20250707_s018` | -13.6979, 25.0497 | n/a | 1.327 | 226 | 114 | 0.504 | 0.52 | 9.297 (68.827) | 1.690 | 17 / 31 | agrees | loftr+magsac++ | 282.4 |
| `tcmap_tmc20250707_s019` | -13.7947, 25.0461 | n/a | 1.327 | 376 | 261 | 0.694 | 0.64 | 1.464 (10.838) | 1.241 | 22 / 24 | agrees | loftr+magsac++ | 287.8 |
| `tcmap_tmc20250707_s020` | -13.8913, 25.0427 | n/a | 1.327 | 303 | 172 | 0.568 | 0.56 | 3.123 (23.121) | 1.516 | 19 / 27 | agrees | loftr+magsac++ | 287.6 |
| `tcmap_tmc20250707_s021` | -13.9718, 25.0400 | n/a | 1.328 | 212 | 87 | 0.410 | 0.39 | 5.723 (42.369) | 1.468 | 8 / 39 | agrees | loftr+magsac++ | 290.9 |
| `tcmap_tmc20250707_s022` | -14.0683, 25.0367 | n/a | 1.328 | 238 | 88 | 0.370 | 0.41 | 25.211 (186.642) | 1.558 | 11 / 39 | agrees | loftr+magsac++ | 288.5 |
| `tcmap_tmc20250707_s023` | -14.1647, 25.0333 | n/a | 1.328 | 263 | 131 | 0.498 | 0.47 | 3.279 (24.275) | 1.601 | 15 / 34 | agrees | loftr+magsac++ | 292.4 |
| `tcmap_tmc20250707_s024` | -14.2612, 25.0300 | n/a | 1.328 | 229 | 127 | 0.555 | 0.45 | 1.839 (13.616) | 1.277 | 15 / 35 | agrees | loftr+magsac++ | 287.0 |
| `tcmap_tmc20250707_s025` | -14.3577, 25.0266 | n/a | 1.328 | 253 | 119 | 0.470 | 0.53 | 32.622 (241.508) | 1.147 | 13 / 30 | agrees | loftr+magsac++ | 285.0 |
| `tcmap_tmc20250707_s026` | -14.4543, 25.0232 | n/a | 1.328 | 204 | 56 | 0.275 | 0.31 | 85.952 (636.313) | 2.097 | 8 / 44 | agrees | loftr+magsac++ | 279.6 |
| `tcmap_tmc20250707_s027` | -14.5348, 25.0203 | n/a | 1.328 | 197 | 79 | 0.401 | 0.28 | 100.953 (747.371) | 1.179 | 9 / 46 | agrees | loftr+magsac++ | 272.5 |
| `tcmap_tmc20250707_s028` | -14.6313, 25.0169 | n/a | 1.328 | 425 | 296 | 0.696 | 0.64 | 1.328 (9.832) | 1.368 | 26 / 22 | agrees | loftr+magsac++ | 276.8 |
| `tcmap_tmc20250707_s029` | -14.7277, 25.0135 | n/a | 1.328 | 510 | 393 | 0.771 | 0.69 | 1.088 (8.053) | 1.168 | 35 / 20 | agrees | loftr+magsac++ | 273.5 |
| `tcmap_tmc20250707_s030` | -14.8242, 25.0101 | n/a | 1.328 | 416 | 287 | 0.690 | 0.67 | 1.446 (10.708) | 1.283 | 27 / 21 | agrees | loftr+magsac++ | 274.0 |
| `tcmap_tmc20250707_s031` | -14.9207, 25.0067 | n/a | 1.328 | 488 | 357 | 0.732 | 0.66 | 1.164 (8.617) | 1.257 | 26 / 22 | agrees | loftr+magsac++ | 273.2 |

## One site, every camera: OHRC, TMC-2, IIRS and an LRO NAC under matched Suns (Site N)

OHRC `ch2_ohr_ncp_20250612T2031048828_d_img_d18`, TMC-2 nadir `ch2_tmc_ncn_20200607T2239162106_d_img_d18`, LRO NAC `M1282456834RE`, windows centred near 60.7°N, 4.6°W (`ops/cut_chain_pairs.py site`; found in PRADAN's footprint catalogue and WUSTL ODE by matching the Suns). The OHRC archive grid is first moved (-29, -61) m into LRO's geometry by the NAC's 4 m correction against it; the NAC is placed by LROC's corners and the TMC-2 by its archive grid, so no TMC-2 pixel enters any prior. All three legs use one set of window centres on the OHRC frame's centre line, so the OHRC -> NAC -> TMC-2 chain can be closed against the direct OHRC -> TMC-2 registration. Held-out medians are quoted only for accepted windows with an inlier ratio above 0.5.

| leg | terminology | Δsun az | Δincidence | scale | windows | verdicts | inliers | held-out median px (m) on the reference grid, accepted | verified cells /64 | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|
| OHRC → TMC-2 | cross-sensor, same mission | 2.2-2.3° | +0.5° | 4.199× | 10 | agrees 10 | 116-1028 | 0.61-1.57 (3.2-8.1 m) on 5.173 m; 1 not quoted | 16-49 | 48-108 |
| OHRC → LRO NAC | cross-sensor, cross-mission | 3.3° | +2.5° | 1.025× | 5 | agrees 5 | 3403-3869 | 0.59-1.19 (0.7-1.5 m) on 1.263 m | 44-55 | 7-45 |
| LRO NAC → TMC-2 | cross-sensor, cross-mission | 5.5° | -2.0° | 4.096× | 4 | agrees 4 | 683-934 | 0.53-0.77 (2.7-4.0 m) on 5.173 m | 43-47 | 90-100 |

**Loop closure across three instruments and two missions.** 4 windows where all three legs registered: the chain OHRC -> NAC -> TMC-2 against the direct OHRC -> TMC-2, compared at the OHRC -> NAC inliers mapped to the ground. Loop RMS median **1.99 m** (0.38 px on TMC-2's 5.173 m grid), max 4.04 m (`ops/loop_closure.py --legs`). Three registrations that are each right agree; one wrong one - however confident - does not. This is consistency between independent registrations, not absolute accuracy.

| loop | window (lat, lon) | RMS m | RMS px (TMC-2 grid) | p90 px | verdicts |
|---|---|---|---|---|---|
| `loop_siten_ohrc2031_nacm1282456834re_tmc20200607_c00` | 60.9687, 355.4145 | 4.041 | 0.781 | 1.257 | agrees |
| `loop_siten_ohrc2031_nacm1282456834re_tmc20200607_c01` | 60.8846, 355.4066 | 1.172 | 0.227 | 0.314 | agrees |
| `loop_siten_ohrc2031_nacm1282456834re_tmc20200607_c02` | 60.8005, 355.3988 | 2.245 | 0.434 | 0.635 | agrees |
| `loop_siten_ohrc2031_nacm1282456834re_tmc20200607_c03` | 60.7164, 355.3911 | 1.731 | 0.335 | 0.396 | agrees |

The IIRS strip of the TMC-2's own orbit is registered onto the TMC-2 in the section above (*TMC-2 → IIRS*, the orbit of `ch2_tmc_ncn_20200607T2239162106_d_img_d18`).

### A real viewpoint test at Site N: OHRC looking forward → OHRC looking back, the next orbit

`ch2_ohr_ncp_20250612T2031048828_d_img_d18` (source) → `ch2_ohr_ncp_20250612T2229094979_d_img_d18` (reference), two hours apart. Same instrument - a viewpoint test, NOT cross-sensor. At the windows the two viewing directions are **39.6-39.8° apart**, from opposite sides of the site; the Sun moved 0.06-0.08° in azimuth and -2.2° in incidence. Both frames were put in LRO's geometry by the same NAC's 4 m correction against each, never fitted to one another, and resampled to one 1.232 m grid; windows are every third centre on the source frame's centre line, fixed before matching. Each image is placed by its own pointing on a sphere, so what a window's homography cannot absorb is relief parallax between the two views. **8/8 accepted**; held-out median 0.91 px (1.12 m) on the 1.232 m grid (range 0.49-2.15 px, accepted windows with inlier ratio above 0.5). Viewing directions from each frame's `.oat` (sub-spacecraft point and altitude), Suns from its `.spm`, both at the window's image line.

| pair | source view: off vertical, from az | reference view | apart | Δincidence | inliers | ratio | held-out median px (m) | verified / no-evid | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `siten_ohrc2031_ohrc2229_c00` | 19.0°, 22° | 21.1°, 190° | 39.8° | -2.25° | 2340 | 0.795 | 1.535 (1.89) | 38 / 4 | agrees |
| `siten_ohrc2031_ohrc2229_c03` | 19.0°, 22° | 21.0°, 190° | 39.8° | -2.25° | 2845 | 0.684 | 2.153 (2.65) | 31 / 3 | agrees |
| `siten_ohrc2031_ohrc2229_c06` | 19.0°, 22° | 21.0°, 190° | 39.8° | -2.25° | 3118 | 0.734 | 1.712 (2.11) | 37 / 9 | agrees |
| `siten_ohrc2031_ohrc2229_c09` | 19.0°, 22° | 20.9°, 190° | 39.7° | -2.25° | 4949 | 0.984 | 0.909 (1.12) | 53 / 0 | agrees |
| `siten_ohrc2031_ohrc2229_c12` | 19.0°, 22° | 20.9°, 190° | 39.7° | -2.24° | 4423 | 0.957 | 0.731 (0.90) | 55 / 0 | agrees |
| `siten_ohrc2031_ohrc2229_c15` | 19.0°, 22° | 20.9°, 190° | 39.7° | -2.24° | 4105 | 0.987 | 0.488 (0.60) | 57 / 0 | agrees |
| `siten_ohrc2031_ohrc2229_c18` | 19.0°, 22° | 20.9°, 191° | 39.6° | -2.24° | 4213 | 0.958 | 0.856 (1.05) | 53 / 0 | agrees |
| `siten_ohrc2031_ohrc2229_c21` | 19.0°, 22° | 20.8°, 191° | 39.6° | -2.24° | 3978 | 0.917 | 0.911 (1.12) | 47 / 1 | agrees |

#### Site N, OHRC → TMC-2, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `siten_ohrc2031_tmc20200607_c00` | 60.9687, 355.4145 | 2.3 | 4.199 | 845 | 673 | 0.796 | 0.95 | 1.489 (7.701) | 1.474 | 49 / 3 | agrees | loftr+magsac++ | 48.2 |
| `siten_ohrc2031_tmc20200607_c01` | 60.8846, 355.4066 | 2.3 | 4.199 | 751 | 611 | 0.814 | 0.97 | 1.089 (5.634) | 1.427 | 44 / 2 | agrees | loftr+magsac++ | 49.3 |
| `siten_ohrc2031_tmc20200607_c02` | 60.8005, 355.3988 | 2.2 | 4.199 | 912 | 840 | 0.921 | 0.89 | 0.873 (4.518) | 1.074 | 45 / 7 | agrees | loftr+magsac++ | 98.0 |
| `siten_ohrc2031_tmc20200607_c03` | 60.7164, 355.3911 | 2.2 | 4.199 | 1061 | 1028 | 0.969 | 0.97 | 0.612 (3.164) | 0.967 | 49 / 2 | agrees | loftr+magsac++ | 97.4 |
| `siten_ohrc2031_tmc20200607_c04` | 60.6323, 355.3833 | 2.2 | 4.199 | 576 | 483 | 0.839 | 0.81 | 0.757 (3.918) | 1.046 | 39 / 12 | agrees | loftr+magsac++ | 107.9 |
| `siten_ohrc2031_tmc20200607_c05` | 60.5482, 355.3756 | 2.2 | 4.199 | 486 | 383 | 0.788 | 0.80 | 1.186 (6.135) | 1.240 | 33 / 13 | agrees | loftr+magsac++ | 103.1 |
| `siten_ohrc2031_tmc20200607_c06` | 60.4642, 355.3679 | 2.2 | 4.199 | 244 | 116 | 0.475 | 0.50 | 13.919 (72.001) | 1.493 | 16 / 33 | agrees | loftr+magsac++ | 105.9 |
| `siten_ohrc2031_tmc20200607_c07` | 60.3801, 355.3603 | 2.2 | 4.199 | 276 | 176 | 0.638 | 0.64 | 1.461 (7.556) | 1.161 | 23 / 22 | agrees | loftr+magsac++ | 105.6 |
| `siten_ohrc2031_tmc20200607_c08` | 60.2960, 355.3527 | 2.2 | 4.199 | 348 | 257 | 0.739 | 0.70 | 1.569 (8.118) | 1.336 | 25 / 18 | agrees | loftr+magsac++ | 103.5 |
| `siten_ohrc2031_tmc20200607_c09` | 60.2119, 355.3451 | 2.2 | 4.199 | 491 | 409 | 0.833 | 0.86 | 0.901 (4.662) | 1.212 | 33 / 9 | agrees | loftr+magsac++ | 97.2 |

#### Site N, OHRC → LRO NAC, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `siten_ohrc2031_nacm1282456834re_c00` | 60.9687, 355.4145 | 3.3 | 1.025 | 3818 | 3638 | 0.953 | 0.98 | 0.952 (1.202) | 1.182 | 47 / 1 | agrees | loftr+magsac++ | 45.3 |
| `siten_ohrc2031_nacm1282456834re_c01` | 60.8846, 355.4066 | 3.3 | 1.025 | 3699 | 3403 | 0.920 | 1.00 | 1.187 (1.499) | 1.383 | 44 / 0 | agrees | loftr+magsac++ | 44.0 |
| `siten_ohrc2031_nacm1282456834re_c02` | 60.8005, 355.3988 | 3.3 | 1.025 | 4128 | 3821 | 0.926 | 0.97 | 0.921 (1.163) | 1.076 | 50 / 2 | agrees | loftr+magsac++ | 16.1 |
| `siten_ohrc2031_nacm1282456834re_c03` | 60.7164, 355.3911 | 3.3 | 1.025 | 4026 | 3869 | 0.961 | 1.00 | 0.673 (0.850) | 0.993 | 51 / 0 | agrees | loftr+magsac++ | 9.7 |
| `siten_ohrc2031_nacm1282456834re_c04` | 60.6323, 355.3833 | 3.3 | 1.025 | 3586 | 3416 | 0.953 | 1.00 | 0.589 (0.744) | 0.909 | 55 / 0 | agrees | loftr+magsac++ | 7.0 |

#### Site N, LRO NAC → TMC-2, window by window

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `siten_nacm1282456834re_tmc20200607_c00` | 60.9687, 355.4145 | 5.5 | 4.096 | 1005 | 934 | 0.929 | 0.98 | 0.527 (2.726) | 0.848 | 47 / 1 | agrees | loftr+magsac++ | 93.0 |
| `siten_nacm1282456834re_tmc20200607_c01` | 60.8846, 355.4066 | 5.5 | 4.096 | 894 | 791 | 0.885 | 0.92 | 0.691 (3.577) | 0.959 | 43 / 5 | agrees | loftr+magsac++ | 90.2 |
| `siten_nacm1282456834re_tmc20200607_c02` | 60.8005, 355.3988 | 5.5 | 4.096 | 839 | 741 | 0.883 | 0.94 | 0.551 (2.851) | 0.909 | 43 / 4 | agrees | loftr+magsac++ | 96.0 |
| `siten_nacm1282456834re_tmc20200607_c03` | 60.7164, 355.3911 | 5.5 | 4.096 | 779 | 683 | 0.877 | 0.94 | 0.770 (3.985) | 1.126 | 44 / 4 | agrees | loftr+magsac++ | 99.8 |

## Real viewpoint: TMC-2 fore (+25°) → aft (−25°), one pass (same sensor)

Same instrument, same sun, seconds apart: only the viewing direction differs (~50°). Relief parallax between the two (~0.93 × height) is not a homography - compare with the synthetic parallax rows below. Same sensor - NOT cross-sensor. Reference (aft) grid 5.929 m, source (fore) 5.933 m.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_tmcfore_tmcaft_w01` | -13.1565, 25.1892 | 0.0 | 0.999 | 234 | 52 | 0.222 | 0.14 | 49.358 (292.642) | 1.802 | 0 / 55 | contradicted | fft_phase_correlation (fallback) | 1292.3 |
| `sac_tmcfore_tmcaft_w02` | -13.3669, 25.1880 | 0.0 | 0.999 | 282 | 118 | 0.418 | 0.41 | 4.075 (24.158) | 1.908 | 10 / 37 | unconfirmed | loftr+magsac++ | 364.2 |
| `sac_tmcfore_tmcaft_w03` | -13.5773, 25.1869 | 0.0 | 0.999 | 302 | 101 | 0.334 | 0.45 | 5.240 (31.065) | 1.934 | 5 / 32 | unconfirmed | loftr+magsac++ | 96.3 |
| `sac_tmcfore_tmcaft_w04` | -13.7877, 25.1857 | 0.0 | 0.999 | 651 | 368 | 0.565 | 0.62 | 2.617 (15.514) | 1.847 | 28 / 22 | agrees | loftr+magsac++ | 135.6 |

## Relief: TMC-2 fore → aft orthorectified on the pass's DTM (same sensor)

The four windows of the real viewpoint test above, cut again with both images orthorectified (`ops/ortho_tmc.py`): the archive lattice already carries terrain at its 100-px nodes (its label: reference data SELENE), so each pixel is moved by the relief BETWEEN the nodes - ISRO's TMC-2 DTM of the same pass (`ch2_tmc_ndn_20250707T1853051045_d_dtm_d18.tif`, ~10 m posting; its label gives a height RMSE of 63 m against SELENE) minus that DTM interpolated between the nodes - times the tangent of each camera's emission, toward the spacecraft (geometry from the pass's orbit file). The DTM is made from this pass's own stereo, so this measures what the pipeline does once ISRO's terrain model is applied - the workflow SAC would run - not an independent height check. Same instrument, same Sun: NOT cross-sensor.

| window | relief in window, p1-p99 (m) | without the DTM: verdict, inlier ratio, held-out median px | with the DTM: verdict, inlier ratio, held-out median px | verified squares without / with |
|---|---|---|---|---|
| `sac_tmcfore_tmcaft_dtm_w01` | 327.1 | contradicted (fallback), 0.222, 49.358 | unconfirmed, 0.247, 7.129 | 0 / 4 |
| `sac_tmcfore_tmcaft_dtm_w02` | 318.6 | unconfirmed, 0.418, 4.075 | unconfirmed, 0.464, 3.363 | 10 / 8 |
| `sac_tmcfore_tmcaft_dtm_w03` | 159.7 | unconfirmed, 0.334, 5.240 | agrees, 0.325, 3.859 | 5 / 8 |
| `sac_tmcfore_tmcaft_dtm_w04` | 417.0 | agrees, 0.565, 2.617 | agrees, 0.562, 2.417 | 28 / 25 |

Accepted: **1/4 without the DTM, 2/4 with it.**

## Kaguya TC → Kaguya MI (cross-sensor; 749 nm visible and 1548 nm infrared)

Tier C rows are multi-modal (visible vs near-infrared). On them the declared method is the global-correlation fallback; the table after this one measures that fallback against the visible-band registration of the same window.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_tc_morning_mi1548_w01` | -74.1077, 43.5487 | n/a | 2.0 | 35 | 6 | 0.171 | 0.08 | 57.068 (844.610) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 41.5 |
| `site_tc_morning_mi1548_w02` | -74.2982, 43.7217 | n/a | 2.0 | 33 | 5 | 0.152 | 0.08 | 62.375 (923.153) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 37.8 |
| `site_tc_morning_mi1548_w03` | -74.2100, 43.4127 | n/a | 2.0 | 34 | 5 | 0.147 | 0.08 | 74.582 (1103.817) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 38.2 |
| `site_tc_morning_mi749_w01` | -74.1077, 43.5487 | n/a | 2.0 | 334 | 313 | 0.937 | 0.97 | 0.468 (6.926) | 0.692 | 45 / 2 | agrees | loftr+magsac++ | 41.0 |
| `site_tc_morning_mi749_w02` | -74.2982, 43.7217 | n/a | 2.0 | 436 | 429 | 0.984 | 0.95 | 0.387 (5.720) | 0.562 | 56 / 3 | agrees | loftr+magsac++ | 46.4 |
| `site_tc_morning_mi749_w03` | -74.2100, 43.4127 | n/a | 2.0 | 416 | 413 | 0.993 | 1.00 | 0.234 (3.464) | 0.445 | 54 / 0 | agrees | loftr+magsac++ | 38.9 |

**Fallback vs the visible band, same window.** The declared transform on the infrared band against the LoFTR registration on the visible band of the SAME window (same TC source file, same MI grid; `ops/multimodal_check.py`): how far apart the two put the same source point, median over a 20 × 20 lattice of reference points. It is the fallback's error relative to the visible-band registration - the nearest thing to a truth the infrared band has. A fallback that had merely kept the archive alignment would sit as far from the visible-band answer as the archive offset (last column).

| pair | against | declared (pair / against) | against inliers | disagreement median px (m) | p90 px | max px | fallback NCC | archive offset m (pair / against) |
|---|---|---|---|---|---|---|---|---|
| `site_tc_morning_mi1548_w01` | `site_tc_morning_mi749_w01` | fft_phase_correlation (fallback) / loftr+magsac++ | 313 | 0.283 (4.2) | 0.431 | 0.620 | 0.61 | 41.5 / 41.0 |
| `site_tc_morning_mi1548_w02` | `site_tc_morning_mi749_w02` | fft_phase_correlation (fallback) / loftr+magsac++ | 429 | 1.093 (16.2) | 1.205 | 1.245 | 0.51 | 37.8 / 46.4 |
| `site_tc_morning_mi1548_w03` | `site_tc_morning_mi749_w03` | fft_phase_correlation (fallback) / loftr+magsac++ | 413 | 0.227 (3.4) | 0.356 | 0.475 | 0.47 | 38.2 / 38.9 |

## Kaguya TC → Chandrayaan-2 IIRS near-infrared (cross-sensor, cross-mission, multi-modal)

IIRS calibrated cube `ch2_iir_nci_20210621T1517513893` (bands 18 = 999 nm and 51 = 1555 nm, streamed out of the zip by HTTP range - see ops/national_round/PRADAN_GUIDE.md) vs the Kaguya TC ortho map at the 74 S site; IIRS ~89 m, TC ~7.4 m, 112-px IIRS windows. A 112-px frame is too small for the per-cell area check, so the whole-frame check decides the verdict, and it can only say `agrees` when the inliers also exceed 8 + 0.3 × matches (Brown & Lowe 2007); below that an agreeing peak is `unconfirmed` (`core/reliability.py` FRAME_ACCEPT_*).

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_tc_ortho_iirs1000_w04` | -73.6817, 43.8428 | n/a | 12.019 | 17 | 7 | 0.412 | 0.06 | 8.811 (783.652) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 981.8 |
| `site_tc_ortho_iirs1000_w05` | -73.6798, 44.1181 | n/a | 12.019 | 12 | 5 | 0.417 | 0.08 | 33.673 (2994.866) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 981.8 |
| `site_tc_ortho_iirs1000_w07` | -73.9474, 43.8643 | n/a | 12.019 | 14 | 5 | 0.357 | 0.08 | 116.280 (10341.971) | n/a | 0 / 58 | contradicted | fft_phase_correlation (fallback) | 1472.2 |
| `site_tc_ortho_iirs1000_w08` | -73.9455, 44.1439 | n/a | 12.019 | 21 | 6 | 0.286 | 0.08 | 16.087 (1430.752) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 3514.6 |
| `site_tc_ortho_iirs1000_w10` | -74.2131, 43.8865 | n/a | 12.019 | 13 | 4 | 0.308 | 0.06 | 23.011 (2046.608) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 1041.8 |
| `site_tc_ortho_iirs1000_w11` | -74.2112, 44.1704 | n/a | 12.019 | 16 | 5 | 0.312 | 0.08 | 66.906 (5950.589) | n/a | 0 / 58 | contradicted | fft_phase_correlation (fallback) | 1169.2 |
| `site_tc_ortho_iirs1555_w05` | -73.6798, 44.1181 | n/a | 12.019 | 13 | 5 | 0.385 | 0.08 | 8.564 (761.710) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 981.8 |
| `site_tc_ortho_iirs1555_w07` | -73.9474, 43.8643 | n/a | 12.019 | 13 | 5 | 0.385 | 0.08 | 62.763 (5582.168) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 1472.2 |
| `site_tc_ortho_iirs1555_w08` | -73.9455, 44.1439 | n/a | 12.019 | 16 | 6 | 0.375 | 0.08 | 59.978 (5334.418) | n/a | 0 / 59 | contradicted | fft_phase_correlation (fallback) | 956.9 |
| `site_tc_ortho_iirs1555_w10` | -74.2131, 43.8865 | n/a | 12.019 | 16 | 6 | 0.375 | 0.09 | 45.876 (4080.178) | n/a | 0 / 57 | unconfirmed | loftr+magsac++ | 2041.2 |
| `site_tc_ortho_iirs1555_w11` | -74.2112, 44.1704 | n/a | 12.019 | 13 | 5 | 0.385 | 0.06 | 19.699 (1752.009) | n/a | 0 / 60 | contradicted | fft_phase_correlation (fallback) | 1048.6 |

**Band against band, same window.** The two IIRS bands' declared transforms against each other (same TC source, same IIRS grid). Two fallbacks that agree are only self-consistent; two that disagree prove at least one of them wrong. No visible band exists on the IIRS side, so this is not an accuracy.

| pair | against | declared (pair / against) | against inliers | disagreement median px (m) | p90 px | max px | fallback NCC | archive offset m (pair / against) |
|---|---|---|---|---|---|---|---|---|
| `site_tc_ortho_iirs1000_w05` | `site_tc_ortho_iirs1555_w05` | fft_phase_correlation (fallback) / fft_phase_correlation (fallback) | 5 | 0.000 (0.0) | 0.000 | 0.000 | 0.22 | 981.8 / 981.8 |
| `site_tc_ortho_iirs1000_w07` | `site_tc_ortho_iirs1555_w07` | fft_phase_correlation (fallback) / fft_phase_correlation (fallback) | 5 | 0.000 (0.0) | 0.000 | 0.000 | 0.19 | 1472.2 / 1472.2 |
| `site_tc_ortho_iirs1000_w08` | `site_tc_ortho_iirs1555_w08` | fft_phase_correlation (fallback) / fft_phase_correlation (fallback) | 6 | 38.639 (3436.6) | 38.639 | 38.639 | 0.19 | 3514.6 / 956.9 |
| `site_tc_ortho_iirs1000_w10` | `site_tc_ortho_iirs1555_w10` | fft_phase_correlation (fallback) / loftr+magsac++ | 6 | 21.793 (1938.2) | 156.091 | 35929.140 | 0.56 | 1041.8 / 2041.2 |
| `site_tc_ortho_iirs1000_w11` | `site_tc_ortho_iirs1555_w11` | fft_phase_correlation (fallback) / fft_phase_correlation (fallback) | 5 | 1.414 (125.8) | 1.414 | 1.414 | 0.38 | 1169.2 / 1048.6 |

## Scale rung: Chandrayaan-2 OHRC → SELENE (Kaguya) TC ortho map (cross-sensor, cross-mission)

The same OHRC source at 0.25 m against the TC ortho mosaic at 7.4 m (the scale column is the ratio the pipeline bridges: it area-averages the OHRC down to the TC grid itself). Windows ~1.5 km square, the most an axis-aligned square fits inside the ~2.8 km OHRC swath at 74 S; 200-px references, 25-px trust cells. Both panchromatic - NOT multi-modal. The TC mosaic has no single sun, so Δsun is n/a.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_ohrc_tc_ortho_w01` | -74.2443, 43.5705 | n/a | 29.6 | 152 | 134 | 0.882 | 0.52 | 0.545 (4.032) | 0.858 | 26 / 31 | agrees | loftr+magsac++ | 430.7 |
| `site_ohrc_tc_ortho_w02` | -73.9472, 43.6896 | n/a | 29.6 | 56 | 17 | 0.304 | 0.19 | 33.923 (251.031) | 1.265 | 1 / 52 | agrees | loftr+magsac++ | 406.8 |
| `site_ohrc_tc_ortho_w03` | -74.0829, 43.6162 | n/a | 29.6 | 71 | 39 | 0.549 | 0.25 | 4.847 (35.870) | 2.008 | 7 / 48 | agrees | loftr+magsac++ | 381.3 |
| `site_ohrc_tc_ortho_w04` | -73.9979, 43.6237 | n/a | 29.6 | 83 | 46 | 0.554 | 0.30 | 2.165 (16.025) | 1.574 | 6 / 45 | unconfirmed | loftr+magsac++ | 402.2 |

## Declared-failure rung: OHRC → LOLA elevation rendered as shaded relief (Tier D, multi-modal)

Same windows as the TC rung. LOLA `ldem_60s_60m` rendered under the OHRC's own derived sun, so Δsun is 0 by construction and what remains is the modality and a 240× scale: the reference is 25 × 25 px. The matcher finds nothing, the system says so and falls back; the fallback's translation on a 25-px frame is not evidence of anything and the verdict stays `unconfirmed`. This row exists to show the declared failure, not a registration.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `site_ohrc_lola_w01` | -74.2443, 43.5705 | 0.0 | 240.0 | 0 | 0 | 0.000 | n/a | n/a | n/a | 0 / 64 | unconfirmed | fft_phase_correlation (fallback) | 29.6 |
| `site_ohrc_lola_w02` | -73.9472, 43.6896 | 0.0 | 240.0 | 0 | 0 | 0.000 | n/a | n/a | n/a | 0 / 64 | unconfirmed | fft_phase_correlation (fallback) | 30.3 |
| `site_ohrc_lola_w03` | -74.0829, 43.6162 | 0.0 | 240.0 | 0 | 0 | 0.000 | n/a | n/a | n/a | 0 / 64 | unconfirmed | fft_phase_correlation (fallback) | 137.7 |
| `site_ohrc_lola_w04` | -73.9979, 43.6237 | 0.0 | 240.0 | 0 | 0 | 0.000 | n/a | n/a | n/a | 0 / 64 | unconfirmed | fft_phase_correlation (fallback) | 45.1 |

## Classical matchers on the same windows, judged by the same rule

`ops/classical_real.py`: SIFT, ORB and AKAZE (OpenCV, 0.75 ratio test, on the common-grid 8-bit images - the MiLOI protocol) on exactly the windows behind each result above. Their matches then go through everything ours go through after matching: MAGSAC++, the held-out `evaluate()`, the independent area check and the fallback (`core.pipeline.run_all(matches=...)`). So *accepted* means the same for every method: the area check agrees and no fallback was needed. Rows measured at `04ed5f6` (1008).

| windows behind | windows | ours accepted | SIFT accepted | ORB accepted | AKAZE accepted |
|---|---|---|---|---|---|
| SAC's OHRC -> LRO NAC pair, Suns 174 deg apart (1.622 m grid) | 6 | 6/6 | 0/6 | 0/6 | 0/6 |
| the same pair on SAC's 1.1179 m grid | 6 | 6/6 | 0/6 | 0/6 | 0/6 |
| Sun raised up to 41.7 deg, azimuth within 20 deg (SAC's frame) | 71 | 61/71 | 58/71 | 59/71 | 59/71 |
| Sun 154-177 deg away in azimuth (SAC's frame) | 56 | 48/56 | 0/56 | 0/56 | 0/56 |
| Site N, OHRC -> TMC-2 (Suns matched) | 10 | 10/10 | 10/10 | 10/10 | 10/10 |
| Site N, OHRC -> LRO NAC | 5 | 5/5 | 5/5 | 5/5 | 5/5 |
| Site N, LRO NAC -> TMC-2 | 4 | 4/4 | 4/4 | 4/4 | 4/4 |
| viewpoint: OHRC -> OHRC, views 40 deg apart | 8 | 8/8 | 8/8 | 7/8 | 8/8 |
| TMC-2 -> IIRS beyond 850 nm (multi-modal) | 62 | 62/62 | 61/62 | 54/62 | 52/62 |
| TMC-2 -> IIRS 746 nm (visible control) | 8 | 8/8 | 8/8 | 8/8 | 8/8 |
| IIRS 1555 nm -> LRO WAC global mosaic (cross-mission, multi-modal) | 16 | 12/16 | 0/16 | 2/16 | 1/16 |
| IIRS 1555 nm -> LRO WAC, the whole strip, 19.2 km windows | 49 | 44/49 | 23/49 | 37/49 | 18/49 |
| TMC-2 -> SELENE TC ortho map, every window at SAC's site (cross-mission) | 31 | 31/31 | 23/31 | 28/31 | 19/31 |
| TMC-2 fore -> aft, both orthorectified on the pass's DTM | 4 | 2/4 | 0/4 | 2/4 | 1/4 |

Per method, over every window above: how often its OWN residual looked fine (at least half of the held-out matches within 3 px of its transform) and the area check still refused it.

| method | windows run | accepted | own residual looked fine | of those, refused by the area check |
|---|---|---|---|---|
| SIFT | 336 | 200 | 201 | 11 |
| ORB | 336 | 216 | 222 | 18 |
| AKAZE | 336 | 185 | 202 | 24 |

## Choosing the reference by its Sun (`ops/find_reference.py`)

Registration across very different Suns is the hard case (0 of 12 accepted with the Suns 60-120° apart, above), so the reference is chosen by its Sun: every image in PRADAN's footprint catalogue (OHRC, TMC-2 nadir, IIRS) and every LRO NAC known on this machine that covers the Chandrayaan-2 footprint, ranked by the angle between the two Sun directions at the footprint's centre. PRADAN's catalogue carries no Sun (its angle fields are zero), so the Sun is computed from each image's start time (`ops/lunar_sun.py`: Meeus, no ephemeris file; it matches LROC's own published sub-solar points to 0.04° - `ops/test_lunar_sun.py`). For Site N's OHRC frame `ch2_ohr_ncp_20250612T2031048828_d_img_d18` (centre 60.59°, 355.38°; Sun incidence 60.6°), 42 images cover at least 20 % of it; the best Sun first:

| image | instrument | covers | Sun directions apart | azimuth apart | incidence |
|---|---|---|---|---|---|
| `ch2_tmc_ncn_20230605T1503198538_d_img_n18` | TMC-2 | 92% | 0.5° | 0.2° | 61.1° |
| `ch2_tmc_ncn_20230605T1503198538_d_img_d32` | TMC-2 | 92% | 0.5° | 0.2° | 61.1° |
| `ch2_iir_nci_20210626T2030097751_d_img_d32` | IIRS | 100% | 1.0° | 0.3° | 61.5° |
| `ch2_ohr_ncp_20250612T2229094979_d_img_d18` | OHRC | 84% | 1.0° | 1.1° | 60.7° |
| `ch2_iir_nci_20210626T1832071349_d_img_d32` | IIRS | 100% | 1.1° | 0.8° | 61.3° |
| `ch2_iir_nci_20210626T2228131842_d_img_d32` | IIRS | 100% | 1.6° | 1.4° | 61.7° |
| `ch2_tmc_ncn_20200607T2239162106_d_img_d18` | TMC-2 | 100% | 1.9° | 0.7° | 62.4° |
| `ch2_iir_nri_20200607T2239153893_d_img_d18` | IIRS | 87% | 1.9° | 0.7° | 62.4° |
| `M1282456834RE` | LRO NAC | 64% | 5.1° | 4.1° | 64.2° |
| `ch2_iir_nci_20210726T1841109188_d_img_d32` | IIRS | 100% | 6.1° | 6.8° | 62.0° |

The three images Site N's evidence uses (the next orbit's OHRC, TMC-2 `20200607T2239`, LRO NAC `M1282456834RE`) rank 4, 7, 9 of 42.

**The whole OHRC archive** (`ops/reference_index.py` -> `evaluation/reference_index.json`, generated at `d03f435`; the console searches the same file): all 300 OHRC observations in PRADAN's catalogue, each ranked against every image covering at least 20% of it. **208 of 300** have an image from ANOTHER orbit lit within 5° of their Sun (234 within 10°); counting images taken alongside on the same pass (TMC-2, IIRS), 287 do. The best partner is another OHRC observation for 270, TMC-2 for 12, IIRS for 14 and an LRO NAC for 4 (the NAC list is only what this machine knows, so that count is a floor).

## Loop closure (OHRC → NAC A → NAC B vs OHRC → NAC B)

6 closed loops. Loop RMS median **0.107 m**, max 0.131 m (`ops/loop_closure.py`). Loop closure cancels any error attached to a single image (its geolocation, its own shading), so it measures correspondence consistency, not absolute ground accuracy.

| loop | window | RMS m | RMS px (B grid) | p90 px | methods | verdicts |
|---|---|---|---|---|---|---|
| `loop_m1153871873le_m1363141432re_w01_t` | -73.7012, 43.7860 | 0.131 | 0.105 | 0.160 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w02_t` | -73.7255, 43.7718 | 0.106 | 0.085 | 0.133 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w03_t` | -73.7568, 43.7818 | 0.121 | 0.097 | 0.156 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w04_t` | -73.7809, 43.7427 | 0.096 | 0.077 | 0.115 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w05_t` | -73.6426, 43.8521 | 0.097 | 0.078 | 0.106 | loftr+magsac++ | agrees |
| `loop_m1153871873le_m1363141432re_w06_t` | -73.7190, 43.8467 | 0.108 | 0.086 | 0.131 | loftr+magsac++ | agrees |

## Real sun-angle sweep (one OHRC frame vs LRO NAC frames)

Outcome by image evidence, rule v2 (`ops/sun_sweep.py` docstring): the matcher is right when |NCC| of its warp against the reference is ≥ 0.30 and at least the archive alignment's |NCC| − 0.05; when neither reaches 0.30 the image cannot judge (inconclusive). |NCC| because opposite suns anti-correlate a correct alignment. All 69 latest rows were logged under rule v2. This sweep is NOT the trust layer's detection evidence - see the next section.

| Δsun az (deg) | windows | NAC frames | registered & accepted | failed & caught | failed, not caught | correct but refused | inconclusive | median inliers |
|---|---|---|---|---|---|---|---|---|
| 0-10 | 16 | 6 | 16 | 0 | 0 | 0 | 0 | 4818 |
| 10-30 | 14 | 5 | 14 | 0 | 0 | 0 | 0 | 4247 |
| 30-60 | 12 | 4 | 11 | 0 | 0 | 0 | 1 | 559 |
| 60-90 | 7 | 3 | 0 | 1 | 0 | 1 | 5 | 58 |
| 90-120 | 5 | 2 | 0 | 0 | 0 | 1 | 4 | 8 |
| 120-180 | 15 | 5 | 10 | 0 | 0 | 0 | 5 | 209 |

All bins: 69 windows over 25 NAC frames, Δsun azimuth 3.3-152.7°. Known issue 2: some windows are logged under two ids (`_sw` and plain) - rows, not distinct ground.

## MiLOI: real LROC NAC images of one ground under many suns (same sensor)

`evaluation/miloi.py` (Xie et al. 2025, github.com/Bin501/CNSFM @94cebaa). 321 pairs matched; 81 have a truth. The tiles' map geometry is off by metres to hundreds of metres, so truth is a per-image translation network built only from pairs where ours AND SIFT agree within 1.0 px with ≥50 inliers each; a pair that is itself an edge is scored leave-one-out, and a pair its network cannot reach has no truth and is not scored. Same sensor (LROC NAC ↔ LROC NAC) - NOT cross-sensor.

| scene | edges | images without truth | truth's own error (leave-one-out, px) |
|---|---|---|---|
| S1 | 8 | 0 | median 0.22, max 0.29 (n=3) |
| S2 | 7 | 4 | median 0.26, max 0.40 (n=5) |
| S3 | 14 | 5 | **not measurable** - every edge is a bridge (no redundancy) |

```
success = rmse_gt_px < 3.0 px on the reference grid, vs the MiLOI network truth (miloi_truth.json)
d_sun_angle_deg      ours_loftr+subpixel                 AKAZE                   ORB                  SIFT
   0-15   deg                  2/2 (100%)            2/2 (100%)            2/2 (100%)            2/2 (100%)
  15-30   deg                 13/16 (81%)           14/16 (88%)           13/16 (81%)           12/16 (75%)
  30-60   deg                 11/29 (38%)           10/29 (34%)            5/29 (17%)            8/29 (28%)
  60-90   deg                  2/18 (11%)             0/18 (0%)             0/18 (0%)             0/18 (0%)
  90-120  deg                    0/9 (0%)              0/9 (0%)              0/9 (0%)              0/9 (0%)
 120-181  deg                    0/7 (0%)              0/7 (0%)              0/7 (0%)              0/7 (0%)

ours, trust outcomes vs truth: caught_failure 43, correct_accepted 33, missed_failure 5
ours, declared transform within 3.0 px of truth: 34/81
```

Trust verdict against truth, ours (latest row per pair). Two definitions of "right", both shown: the MATCHER's homography against truth over the frame (what the trust layer judges - `outcome`), and the success rule of the table above (`rmse_gt_px` of the raw matches). S3's truth has no measurable error of its own.

| verdict | pairs | of which S3 | matcher H within 3 px | rmse_gt_px under 3 px |
|---|---|---|---|---|
| agrees | 33 | 13 | 33 | 28 |
| unconfirmed | 5 | 5 | 0 | 0 |
| contradicted | 43 | 38 | 0 | 0 |

Scored pairs with Sun vectors 90° or more apart: 16 (S1 0, S2 0, S3 16); registered within 3 px by ours: 0.

## Trust layer on real imagery: planted confident-but-wrong registrations

`ops/trust_real_calibration.py`: 30 real windows whose registration is independently good (declared LoFTR, `agrees`, |NCC| of the true alignment ≥ 0.5, ≥ 50 inliers); the true transform shifted by d metres and a match set that agrees with the WRONG transform perfectly. d = 0 is the false-alarm rate. The two Sun populations are shown separately and never pooled.

### Sun azimuths under 10° apart (the 74 °S OHRC/NAC windows): 22 windows

Sun azimuth differences 3.3, 5.8, 9.1°; |NCC| of the true alignment 0.81-0.96 (sign positive).
Beside the area check, what a residual check reads on the SAME planted answers: the median held-out residual of the planted matches, and the share a residual threshold of **1.01 px** would flag - the loosest threshold that still accepts every one of these windows' true registrations (their own held-out medians reach 1.01 px).

| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 | residual check: median held-out residual (px) | flagged by the residual threshold |
|---|---|---|---|---|---|---|
| 0 | 0.00 | 44 | 0.0% | 62.2 | 0.35 | 0.0% |
| 1 | 0.80 | 176 | 0.0% | 60.7 | 0.35 | 0.0% |
| 2 | 1.61 | 176 | 0.0% | 44.1 | 0.35 | 0.0% |
| 3 | 2.41 | 176 | 74.4% | 10.0 | 0.35 | 0.0% |
| 5 | 4.02 | 176 | 100.0% | 0.0 | 0.35 | 0.0% |
| 10 | 8.03 | 176 | 100.0% | 0.0 | 0.36 | 0.0% |
| 20 | 16.06 | 176 | 100.0% | 0.0 | 0.35 | 0.0% |
| 50 | 40.16 | 176 | 100.0% | 0.0 | 0.35 | 0.0% |
| 100 | 80.32 | 176 | 100.0% | 0.0 | 0.35 | 0.0% |
| 200 | 160.64 | 176 | 100.0% | 0.0 | 0.35 | 0.0% |

Planted errors of 5 m or more: the residual threshold flags **0 of 1056**; the area check flags **1056 of 1056**.

### Sun azimuths 132-174° apart (SAC's own OHRC/NAC pairs): 8 windows

Sun azimuth differences 132.2, 132.3, 173.5, 173.6, 173.7°; |NCC| of the true alignment 0.53-0.90 (sign negative: opposite Suns anti-correlate). Windows: `sac_ohrc_nac_w01`, `sac_ohrc_nac_w02`, `sac_ohrc_nac_w03`, `sac_ohrc_nac_w04`, `sac_ohrc_nac_w05`, `sac_ohrc_nac_w06`, `sac_polar_ohrc_nac_w01`, `sac_polar_ohrc_nac_w03`.
Beside the area check, what a residual check reads on the SAME planted answers: the median held-out residual of the planted matches, and the share a residual threshold of **4.50 px** would flag - the loosest threshold that still accepts every one of these windows' true registrations (their own held-out medians reach 4.50 px).

| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 | residual check: median held-out residual (px) | flagged by the residual threshold |
|---|---|---|---|---|---|---|
| 0 | 0.00 | 16 | 0.0% | 40.5 | 0.35 | 0.0% |
| 1 | 0.62 | 64 | 0.0% | 38.5 | 0.35 | 0.0% |
| 2 | 1.23 | 64 | 4.7% | 34.7 | 0.35 | 0.0% |
| 3 | 1.85 | 64 | 12.5% | 24.3 | 0.36 | 0.0% |
| 5 | 3.08 | 64 | 84.4% | 2.9 | 0.35 | 0.0% |
| 10 | 6.17 | 64 | 100.0% | 0.0 | 0.36 | 0.0% |
| 20 | 12.33 | 64 | 100.0% | 0.0 | 0.35 | 0.0% |
| 50 | 30.83 | 64 | 100.0% | 0.0 | 0.35 | 0.0% |
| 100 | 61.65 | 64 | 100.0% | 0.0 | 0.35 | 0.0% |
| 200 | 123.31 | 64 | 100.0% | 0.0 | 0.35 | 0.0% |

Planted errors of 5 m or more: the residual threshold flags **0 of 384**; the area check flags **374 of 384**.

### Visible against infrared (TMC-2 → IIRS 1555 nm, two orbits): 16 windows

The same planted test where the two images are in different bands: TMC-2 (visible) onto IIRS at 1555 nm. |NCC| of the true alignment 0.81-0.96. The IIRS grid is 73.81-84.25 m, so the planted shifts are set in its pixels (own seed stream and file, `trust_real_calibration_ir.csv`; the populations above are untouched). Residual threshold **0.32 px**: the loosest these windows' own registrations need.

| planted error (IIRS px) | ~m | trials | flagged as wrong | mean verified cells /64 | residual check: median held-out residual (px) | flagged by the residual threshold |
|---|---|---|---|---|---|---|
| 0 | 0 | 32 | 0.0% | 54.0 | 0.33 | 71.9% |
| 0.5 | 39 | 128 | 0.0% | 53.7 | 0.36 | 86.7% |
| 1 | 79 | 128 | 0.0% | 53.6 | 0.36 | 86.7% |
| 2 | 158 | 128 | 6.2% | 37.5 | 0.35 | 83.6% |
| 3 | 237 | 128 | 66.4% | 7.5 | 0.36 | 85.9% |
| 5 | 395 | 128 | 85.9% | 2.6 | 0.35 | 87.5% |
| 10 | 789 | 128 | 99.2% | 0.1 | 0.36 | 86.7% |
| 20 | 1578 | 128 | 99.2% | 0.1 | 0.36 | 87.5% |

Planted errors of 5 IIRS pixels or more: the residual threshold flags **335 of 384**; the area check flags **364 of 384**.

### Errors that are not translations: planted rotation and scale

A rotation or a scale change about the frame centre leaves the centre where it was and displaces the CORNERS most, so one number describes it: how far the corners move. The frame verdict is the wrong thing to watch here - it still says `agrees` while a corner is 3 px out - because the error is not uniform over the frame. What carries the information is the 8 × 8 map, so the last two columns count cells, not frames: of the cells the planted error really moved by more than 2 px, how many the map refused to verify, and of the cells it moved by less than 1 px, how many stayed verified.

| kind | corner displacement (m) | ~px on the reference grid | trials | frame contradicted | mean verified cells /64 | cells moved >2 px that are NOT verified | cells moved <1 px that stay verified |
|---|---|---|---|---|---|---|---|
| rotation | 0 | 0.00 | 60 | 0.0% | 56.4 | no cell moved that far | 3384/3840 = 88 % |
| rotation | 1 | 0.80 | 60 | 0.0% | 56.1 | no cell moved that far | 3367/3840 = 88 % |
| rotation | 2 | 1.61 | 60 | 0.0% | 53.8 | no cell moved that far | 1823/2096 = 87 % |
| rotation | 3 | 2.41 | 60 | 0.0% | 45.5 | 476/752 = 63 % | 964/1072 = 90 % |
| rotation | 5 | 4.02 | 60 | 10.0% | 23.9 | 2065/2400 = 86 % | 280/336 = 83 % |
| rotation | 10 | 8.03 | 60 | 91.7% | 1.1 | 3478/3504 = 99 % | 14/48 = 29 % |
| rotation | 20 | 16.06 | 60 | 100.0% | 0.0 | 3792/3792 = 100 % | n/a |
| scale | 0 | 0.00 | 60 | 0.0% | 56.4 | no cell moved that far | 3384/3840 = 88 % |
| scale | 1 | 0.80 | 60 | 0.0% | 56.0 | no cell moved that far | 3360/3840 = 88 % |
| scale | 2 | 1.61 | 60 | 0.0% | 53.2 | no cell moved that far | 1817/2096 = 87 % |
| scale | 3 | 2.41 | 60 | 0.0% | 45.4 | 469/752 = 62 % | 963/1072 = 90 % |
| scale | 5 | 4.02 | 60 | 15.0% | 22.9 | 2092/2400 = 87 % | 267/336 = 79 % |
| scale | 10 | 8.03 | 60 | 95.0% | 0.8 | 3489/3504 = 100 % | 12/48 = 25 % |
| scale | 20 | 16.06 | 60 | 100.0% | 0.0 | 3792/3792 = 100 % | n/a |

Over every rotation and scale trial: of the 20896 cells displaced by more than 2 px the map refused to verify 19653 (**94.1 %**); of the 22464 cells displaced by less than 1 px, 19635 stayed verified (**87.4 %**). The planted matches agree with the wrong transform perfectly in every trial, so nothing the matcher reports could reveal it.

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

## Synthetic Sun-azimuth sweep, 0-180° (exact truth; fig1)

Rendered pairs (LOLA DEM, 60 m grid), Sun elevation fixed at 30°, Sun azimuth moved; the same five off-grid shifts at every angle. Medians over every scored run in results_log.csv (`presentation/make_figures.load_curves`, the data of fig1). A classical run that fails produces no rmse_gt_px and cannot enter its median, so the classical column is a median of the survivors and the next column says how many there were. The renderer is a local cosine law with no cast shadows: at 180° it produces a near-exact contrast inversion, which real terrain under a low Sun does not.

| Sun azimuths apart | ours: runs | ours: median rmse_gt_px (m) | best of SIFT / ORB / AKAZE: median of the runs that scored | classical runs that scored |
|---|---|---|---|---|
| 0° | 71 | 0.086 (5.1) | 0.044 | 105/105 |
| 15° | 112 | 0.086 (5.1) | 0.247 | 105/105 |
| 30° | 70 | 0.314 (18.8) | 1.833 | 77/105 |
| 45° | 70 | 1.096 (65.8) | 443.240 | 14/105 |
| 60° | 65 | 2.379 (142.7) | 320.832 | 7/105 |
| 90° | 65 | 5.805 (348.3) | 2464.972 | 7/105 |
| 120° | 65 | 4.025 (241.5) | 718.935 | 7/105 |
| 180° | 65 | 0.080 (4.8) | 4971.677 | 7/105 |

## Sub-pixel accuracy, with the pixel grid named

"Sub-pixel" means nothing without its grid. Every figure below is on the REFERENCE grid with its metres, and says what its truth is. None is a new measurement: each is the row or table above it came from.

| evidence | what the truth is | reference grid | result |
|---|---|---|---|
| Synthetic rendered pair (LOLA DEM), Sun azimuths 0° / 15° / 30° / 45° apart, medians over the off-grid shifts (the fig1 rows) | exact: a known transform | 60 m | rmse_gt_px 0.086 / 0.086 / 0.314 / 1.096 px = 5.1 / 5.1 / 18.8 / 65.8 m |
| Real Chandrayaan-2 OHRC → LRO NAC, 74 °S, 20 windows | held-out matches (the 20 % the fit never saw) - no ground truth | 0.931 and 1.245 m | median per window 0.41-1.01 px = 0.51-0.94 m |
| Real OHRC → LRO NAC, SAC's equatorial pair, 6 windows, Sun azimuths 173.5-173.7° apart | held-out matches | 1.622 m | median per window 0.69-1.68 px = 1.1-2.7 m |
| The same pair on the paper's 1.1179 m grid, 6 windows | held-out matches | 1.1179 m | median per window 0.86-1.60 px = 1.0-1.8 m |
| Loop closure OHRC → NAC A → NAC B vs OHRC → NAC B, 6 loops | consistency of three registrations (cancels per-image error) | 1.245 m (NAC B) | RMS median 0.086 px = 0.107 m |
| MiLOI LRO NAC ↔ NAC (same sensor), the `agrees` pairs: the matcher's transform vs the network truth | a translation network from ours+SIFT agreement on OTHER pairs; its own leave-one-out error is in the MiLOI section (S3: not measurable) | per pair | S1 median 0.52 px = 0.73 m (n=9, grids 1.12-1.53 m); S2 median 1.18 px = 1.30 m (n=11, grids 0.88-1.21 m); S3 median 1.12 px = 0.78 m (n=13, grids 0.62-0.95 m) |
| Independent check points clicked by hand, 6 accepted windows (60 points) | features clicked in both images, never seen by the matcher; one click's precision 1.47 m | 0.931-1.263 m | RMSE per window 1.69-2.39 m |

### In the Chandrayaan-2 image's own pixels

The PS asks for sub-pixel accuracy "of source image". Every pair is measured on the coarser of its two grids. Where the Chandrayaan-2 image is the coarser one, that grid is its own, and the medians below are in its own pixels; where it is the finer one, the reference grid bounds what can be measured. Held-out medians of accepted windows with an inlier ratio above 0.5; the same rows as above, re-expressed.

| pairing | the Chandrayaan-2 image | grid measured on | windows | median per window, in that image's pixels | metres |
|---|---|---|---|---|---|
| LRO NAC ↔ TMC-2 at SAC's site, matched Sun | TMC-2 (the coarser: its own grid) | 4.555 m | 6 | 0.36-0.48 | 1.6-2.2 |
| TMC-2 ↔ IIRS 1555 nm, orbit `20200203` | IIRS (the coarser: its own grid) | 73.85 m | 8 | 0.21-0.32 | 15.6-23.6 |
| TMC-2 ↔ IIRS 1555 nm, orbit `20200607` | IIRS (the coarser: its own grid) | 83.67 m | 8 | 0.16-0.32 | 13.9-27.3 |
| OHRC → TMC-2 at Site N, matched Sun | TMC-2 (the coarser: its own grid) | 5.173 m | 9 | 0.61-1.57 | 3.2-8.1 |
| OHRC → LRO NAC, 74 °S | OHRC (the finer: bounded by the reference grid; OHRC pixels = metres / 0.25 m) | 0.931 m | 20 | 2.0-3.7 | 0.51-0.94 |
| OHRC → LRO NAC, SAC's equatorial pair | OHRC (the finer: bounded by the reference grid; OHRC pixels = metres / 0.279 m) | 1.622 m | 6 | 4.0-9.7 | 1.12-2.72 |

## Independent check points: accuracy against points the matcher never saw

A person clicked the same feature (small crater centres, boulders - never shadow edges) in both images of each window with `ops/click_check_points.py`, which shows the source around where the ARCHIVE georeference puts it and never reads a registration (a test enforces it). So these points are independent of every transform scored against them: the standard photogrammetric check point, and the RMSE the problem statement names. Errors are where the declared transform puts each clicked source point, against where it was clicked in the reference - on the reference grid, in metres, and in the source image's own pixels. *Plane floor*: each point against a homography fitted to all the other clicked points (leave-one-out) - the click error plus relief that no single transform can remove. *Click precision*: the same features clicked again later without the first clicks shown (repeat difference / √2). Over 10 repeats, one click's precision is a median 1.47 m on the reference and 1.55 m on the source.

| pair | points | ours: RMSE on the reference grid px (m) | RMSE in the source's own px | median (m) | max (m) | archive prior RMSE (m) | plane floor RMSE (m) | verdict |
|---|---|---|---|---|---|---|---|---|
| `site_ohrc_m1153871873le_w04_full` | 10 | 1.86 (1.73) on 0.931 m | 6.93 on 0.25 m | 1.70 | 2.70 | 2.9 | 2.48 | accepted |
| `site_ohrc_m1153871873le_w09_full` | 10 | 2.56 (2.39) on 0.931 m | 9.54 on 0.25 m | 2.33 | 3.49 | 4.0 | 2.93 | accepted |
| `site_ohrc_m1153871873le_w25_full` | 10 | 1.82 (1.69) on 0.931 m | 6.77 on 0.25 m | 1.48 | 2.58 | 5.3 | 2.78 | accepted |
| `siten_ohrc2031_nacm1282456834re_c02` | 10 | 1.46 (1.84) on 1.263 m | 1.49 on 1.232 m | 1.67 | 3.47 | 15.1 | 2.24 | accepted |
| `siten_ohrc2031_nacm1282456834re_c03` | 10 | 1.62 (2.04) on 1.263 m | 1.66 on 1.232 m | 1.56 | 3.11 | 10.2 | 1.96 | accepted |
| `siten_ohrc2031_nacm1282456834re_c04` | 10 | 1.79 (2.25) on 1.263 m | 1.83 on 1.232 m | 1.75 | 4.12 | 8.4 | 5.31 | accepted |

Classical transforms the area check accepted on the same windows, scored on the same points:

| pair | method | RMSE (m) | ours on these points (m) |
|---|---|---|---|
| `siten_ohrc2031_nacm1282456834re_c02` | SIFT | 1.79 | 1.84 |
| `siten_ohrc2031_nacm1282456834re_c02` | ORB | 1.95 | 1.84 |
| `siten_ohrc2031_nacm1282456834re_c02` | AKAZE | 2.00 | 1.84 |
| `siten_ohrc2031_nacm1282456834re_c03` | SIFT | 2.15 | 2.04 |
| `siten_ohrc2031_nacm1282456834re_c03` | ORB | 1.94 | 2.04 |
| `siten_ohrc2031_nacm1282456834re_c03` | AKAZE | 2.11 | 2.04 |
| `siten_ohrc2031_nacm1282456834re_c04` | SIFT | 2.24 | 2.25 |
| `siten_ohrc2031_nacm1282456834re_c04` | ORB | 2.23 | 2.25 |
| `siten_ohrc2031_nacm1282456834re_c04` | AKAZE | 2.21 | 2.25 |

## Runtime and match distribution

Wall time of `run_all` per window (the `seconds` column; LoFTR on CPU, tiled; no GPU), latest rows: median 13.3 s over the 89 OHRC → NAC windows at 74 °S (the loop legs and the sun sweep; 640-px NAC references), 8.3 s over all 423 registered windows (Intel64 Family 6 Model 170 Stepping 4, GenuineIntel; Windows-11-10.0.26200-SP0).

Uniform distribution (PS demand): `grid_coverage_fraction` is the share of the 8 × 8 reference cells holding at least one inlier. On the 20 OHRC → NAC windows at 74 °S it is 0.19-1.00, median 1.00; 17 of 20 windows are at 0.95 or above (the lowest: `site_ohrc_m1153871873le_w01` 0.19, `site_ohrc_m1153871873le_w05` 0.44).

Archive scale, from PRADAN's own footprint catalogue (`<data>/pradan/shapefiles`, downloaded 18 Sep 2026; OHRC releases 1-11; `ops/pradan_archive.py`): 311 calibrated OHRC products (300 observations; some are listed twice, one copy per ground station) covering 23,651 km² (median frame 79.0 km²); 10,793 calibrated TMC-2 products (3,598 nadir); 2,196 calibrated IIRS products. At the whole-overlap rate measured above (13.1 km² in 10.5 min = 75 km² per hour on one laptop CPU, registration only, against a 0.931 m NAC reference), all 23,651 km² of OHRC is about 314 laptop-hours. A projection from one measured rate, not a measurement: it leaves out reading and cutting the products and assumes lit, textured ground and a reference as fine as that NAC.

Delivered control points, uniform by construction: every accepted registration also exports `gcps_uniform.txt` / `.points` - its inliers thinned to at most 4 per cell of an 8 × 8 grid on the reference, lowest residual first. Over 351 accepted registrations the set holds a median 214 points in a median 56 of 64 cells; 152 of 351 fill 90 % of the cells or more.

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

Rows in real_pairs_log.csv: 3336: 595 distinct pair ids (latest row wins) = 423 registered pairs (406 distinct windows - a window being one source image, one reference image, one place; 347 if the IIRS bands of one window count once; Known issue 2: some were cut twice under two ids); 11 instrument pairings (nac-nac, nac-tmc2, ohrc-lola, ohrc-nac, ohrc-ohrc, ohrc-tc, ohrc-tmc2, tc-iirs, tc-mi, tmc2-iirs, tmc2-tmc2) + 10 loops + 58 windows of one whole strip (their own section) + 16 IIRS → LRO WAC windows (their own section) + 49 windows of the whole IIRS strip onto WAC + 31 TMC-2 → SELENE TC windows + 4 DTM-orthorectified fore/aft windows (each its own section) + 4 withdrawn (INVALIDATED). Rows in results_log.csv: 9225.
