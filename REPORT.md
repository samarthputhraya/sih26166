# SIH26166 - evaluation report

Generated 2026-09-22T23:47 from commit `3fa526b` by `python -m ops.make_report`. **Do not edit by hand** - every number below is read from the evidence files named in each section. The latest real-pair rows were measured at commit `7dd4e5b` (183 rows).

All pixel figures are on the REFERENCE image's grid, with its metres stated. Real pairs have no exact ground truth: accuracy on them is reported as held-out residuals (the 20 % of matches the fit never saw) and as loop closure. `residual_px` in results_log.csv is the RMSE over ALL held-out matches including outliers and is not quoted for real pairs.

## Products downloaded (sha256 recorded)

145 files: miloi 90, mimap 2, nac 4, nac_sac 2, nac_sweep 30, pradan_iirs 4, pradan_ohrc 2, pradan_tmc2 5, tcevem 2, tcmorm 2, tcort 2. Full list with URLs and sha256: `C:\Users\samar\sih26166_data\download_manifest_done.csv` and `nac_sweep_manifest_done.csv`, `nac_sac_manifest_done.csv`. The Chandrayaan-2 OHRC frame `ch2_ohr_ncp_20200229T0739312111_d_img_d18` was already on disk (archive.org mirror).

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

Dense tiling, not hand-spread windows: every non-overlapping 640-px window (centres at least 1.1 × the window apart) that `ops.cut_site_pairs --windows 60 --tag full` finds in shared, lit, textured ground of the 74 °S OHRC frame and NAC `M1153871873LE` (Sun azimuths 3.3° apart). 37 windows of 596 m = 13.1 km². Verdicts: agrees 37; **accepted 37/37**; held-out median of the accepted windows: median 0.61 px = 0.57 m on the 0.931 m grid, 36 of 37 under 3 px (range 0.44-316.06). 1 accepted window(s) report a held-out median above 3 px (`site_ohrc_m1153871873le_w15_full` 316 px at an inlier ratio of 0.542). That number is the median of the 20 % of matches the fit never saw, and it is robust only while the inlier ratio stays well above 0.5 - at 0.54 a random held-out draw can be majority-outlier, and the median then describes the outliers. Independent image evidence says these windows are registered: the exported `registered_product.tif` correlates with its reference at NCC +0.87 to +0.95 across all 37 accepted windows (`ops/sun_sweep.py`'s |NCC| >= 0.30 rule, applied to the declared warp), and under the declared transform the median error over ALL matches on the worst of them is 1.08 px. This is a limit of the metric, not of the registration, and it is why the area check never looks at the matches. Wall time of `run_all`: 5.0 min in total, median 7.9 s per window, CPU only. Archive offset of each accepted window against its nearest accepted neighbour: median difference 19.3 m, max 57.2 m (`site_ohrc_m1153871873le_w15_full`), 3 over 50 m. Reported separately from the hand-spread windows above and never merged with them.

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

## Real viewpoint: TMC-2 fore (+25°) → aft (−25°), one pass (same sensor)

Same instrument, same sun, seconds apart: only the viewing direction differs (~50°). Relief parallax between the two (~0.93 × height) is not a homography - compare with the synthetic parallax rows below. Same sensor - NOT cross-sensor. Reference (aft) grid 5.929 m, source (fore) 5.933 m.

| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `sac_tmcfore_tmcaft_w01` | -13.1565, 25.1892 | 0.0 | 0.999 | 234 | 52 | 0.222 | 0.14 | 49.358 (292.642) | 1.802 | 0 / 55 | contradicted | fft_phase_correlation (fallback) | 1292.3 |
| `sac_tmcfore_tmcaft_w02` | -13.3669, 25.1880 | 0.0 | 0.999 | 282 | 118 | 0.418 | 0.41 | 4.075 (24.158) | 1.908 | 10 / 37 | unconfirmed | loftr+magsac++ | 364.2 |
| `sac_tmcfore_tmcaft_w03` | -13.5773, 25.1869 | 0.0 | 0.999 | 302 | 101 | 0.334 | 0.45 | 5.240 (31.065) | 1.934 | 5 / 32 | unconfirmed | loftr+magsac++ | 96.3 |
| `sac_tmcfore_tmcaft_w04` | -13.7877, 25.1857 | 0.0 | 0.999 | 651 | 368 | 0.565 | 0.62 | 2.617 (15.514) | 1.847 | 28 / 22 | agrees | loftr+magsac++ | 135.6 |

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

| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 |
|---|---|---|---|---|
| 0 | 0.00 | 44 | 0.0% | 62.2 |
| 1 | 0.80 | 176 | 0.0% | 60.7 |
| 2 | 1.61 | 176 | 0.0% | 44.1 |
| 3 | 2.41 | 176 | 74.4% | 10.0 |
| 5 | 4.02 | 176 | 100.0% | 0.0 |
| 10 | 8.03 | 176 | 100.0% | 0.0 |
| 20 | 16.06 | 176 | 100.0% | 0.0 |
| 50 | 40.16 | 176 | 100.0% | 0.0 |
| 100 | 80.32 | 176 | 100.0% | 0.0 |
| 200 | 160.64 | 176 | 100.0% | 0.0 |

### Sun azimuths 132-174° apart (SAC's own OHRC/NAC pairs): 8 windows

Sun azimuth differences 132.2, 132.3, 173.5, 173.6, 173.7°; |NCC| of the true alignment 0.53-0.90 (sign negative: opposite Suns anti-correlate). Windows: `sac_ohrc_nac_w01`, `sac_ohrc_nac_w02`, `sac_ohrc_nac_w03`, `sac_ohrc_nac_w04`, `sac_ohrc_nac_w05`, `sac_ohrc_nac_w06`, `sac_polar_ohrc_nac_w01`, `sac_polar_ohrc_nac_w03`.

| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 |
|---|---|---|---|---|
| 0 | 0.00 | 16 | 0.0% | 40.5 |
| 1 | 0.62 | 64 | 0.0% | 38.5 |
| 2 | 1.23 | 64 | 4.7% | 34.7 |
| 3 | 1.85 | 64 | 12.5% | 24.3 |
| 5 | 3.08 | 64 | 84.4% | 2.9 |
| 10 | 6.17 | 64 | 100.0% | 0.0 |
| 20 | 12.33 | 64 | 100.0% | 0.0 |
| 50 | 30.83 | 64 | 100.0% | 0.0 |
| 100 | 61.65 | 64 | 100.0% | 0.0 |
| 200 | 123.31 | 64 | 100.0% | 0.0 |

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

## Sub-pixel accuracy, with the pixel grid named

"Sub-pixel" means nothing without its grid. Every figure below is on the REFERENCE grid with its metres, and says what its truth is. None is a new measurement: each is the row or table above it came from.

| evidence | what the truth is | reference grid | result |
|---|---|---|---|
| Synthetic rendered pair (LOLA DEM), Sun azimuths 0° / 15° / 30° / 45° apart, medians over the off-grid shifts (the fig1 rows) | exact: a known transform | 60 m | rmse_gt_px 0.086 / 0.086 / 0.314 / 1.096 px = 5.1 / 5.1 / 18.8 / 65.8 m |
| Real Chandrayaan-2 OHRC → LRO NAC, 74 °S, 20 windows | held-out matches (the 20 % the fit never saw) - no ground truth | 0.931 and 1.245 m | median per window 0.41-1.01 px = 0.51-0.94 m |
| Real OHRC → LRO NAC, SAC's equatorial pair, 6 windows, Sun azimuths 173.5-173.7° apart | held-out matches | 1.622 m | median per window 0.69-1.68 px = 1.1-2.7 m |
| Loop closure OHRC → NAC A → NAC B vs OHRC → NAC B, 6 loops | consistency of three registrations (cancels per-image error) | 1.245 m (NAC B) | RMS median 0.086 px = 0.107 m |
| MiLOI LRO NAC ↔ NAC (same sensor), the `agrees` pairs: the matcher's transform vs the network truth | a translation network from ours+SIFT agreement on OTHER pairs; its own leave-one-out error is in the MiLOI section (S3: not measurable) | per pair | S1 median 0.52 px = 0.73 m (n=9, grids 1.12-1.53 m); S2 median 1.18 px = 1.30 m (n=11, grids 0.88-1.21 m); S3 median 1.12 px = 0.78 m (n=13, grids 0.62-0.95 m) |

## Runtime and match distribution

Wall time of `run_all` per window (the `seconds` column; LoFTR on CPU, tiled; no GPU), latest rows: median 8.2 s over the 89 OHRC → NAC windows at 74 °S (the loop legs and the sun sweep; 640-px NAC references), 7.8 s over all 177 registered windows (Intel64 Family 6 Model 170 Stepping 4, GenuineIntel; Windows-11-10.0.26200-SP0).

Uniform distribution (PS demand): `grid_coverage_fraction` is the share of the 8 × 8 reference cells holding at least one inlier. On the 20 OHRC → NAC windows at 74 °S it is 0.19-1.00, median 1.00; 17 of 20 windows are at 0.95 or above (the lowest: `site_ohrc_m1153871873le_w01` 0.19, `site_ohrc_m1153871873le_w05` 0.44).

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

Rows in real_pairs_log.csv: 929: 187 distinct pair ids (latest row wins) = 177 registered pairs (160 distinct ground windows; Known issue 2: some were cut twice under two ids) + 6 loops + 4 withdrawn (INVALIDATED). Rows in results_log.csv: 3299.
