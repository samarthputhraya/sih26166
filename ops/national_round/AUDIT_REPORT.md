# SIH26166 national-round audit report

Started 20 Sep 2026, 02:30 IST, at commit `6a5686b` (submission-v1 tag = `0297936`, safe PDF copy
`presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf`, sha256 `f9d0194a…`). Answers
`AUDIT_PROMPT.md`. Every number in this file is either a command output recorded below or a
REPORT.md value at the commit named beside it. Sections are filled in the order the work was done;
"[in progress]" marks what is not finished yet.

---

## Phase A: baseline (20 Sep, 02:30-02:40, commit `6a5686b`)

| Check | Result |
|---|---|
| `git status` | clean; `git log` head `6a5686b` (AUDIT_PROMPT), `0297936` = Team ID commit |
| `git tag submission-v1 0297936` + push | done, tag on origin |
| `python -m pytest -q` (alone) | **298 passed** in 29 s |
| `python -m ops.freeze --plan` | 71 pairs by exact id from 12 commands (~8 min), sweep 25 NACs / 69 windows (~14 min), 1 loop command, trust 22 windows, MiLOI matching code **UNCHANGED** since the stored matches |
| `python -m ops.freeze --check` at `6a5686b` | NOT FROZEN (479 stale items) - expected: every latest row names `49bdad9`; `git diff 49bdad9 HEAD -- core evaluation ops baselines app` minus evidence logs and docs is one 7-line reporting hunk in `core/pipeline.py` (Known issue 13) |
| `python -m presentation.make_figures` | 7 figures, no overflow; on-slide font floor 6.5 pt (fig3) |
| `python -m presentation.build_deck` | 6 slides, pointers unchanged, **AUDIT: clean**; words per slide s2=240 s3=125 s4=207 s5=151 s6=150 |
| `python -m presentation.export_pdf` | 6 pages 792x446 pt, 1,102,990 bytes, **PDF CHECK: clean** (first attempt failed only because the pymupdf copy in one scratchpad was broken; a working 1.28.2 copy was used) |
| Rendered pages 1-6 (140 dpi PNG), read by eye | all six render cleanly: nothing overflows, no `[TBD]`, Team ID SNPSU0192 / LunaXX on slide 1, figures legible. Nothing red. |
| Memory at start | commit charge 42.7 of 51.3 GB (Chrome 10.9 GB, 25 `claude` processes 9.1 GB, VS Code 6.8 GB). Heavy jobs run one at a time. |

Freeze step durations at `49bdad9` (from `<data>/freeze/49bdad9/state.json`): real 7.4 min, sweep
20.2, loops 0.1, trust 35.6, miloi 25.8, viewpoint 7.9, calib 5.3, gate2 4.9, report 1.0 = 108 min.

---

## B2: evidence integrity - every deck and portal number re-derived from the CSV cells

Script: `scratchpad/rederive.py` (reads `real_pairs_log.csv`, `miloi_log.csv`,
`trust_real_calibration.csv`, `results_log.csv`, the site_geometry JSONs). Run 20 Sep 02:50.

| Claim on the deck / portal | Re-derived from the cells | Match |
|---|---|---|
| SAC equatorial: Sun azimuths 174° apart, 6/6 accepted | d_sun_az 173.5-173.7; 6 rows, 6 `agrees` | yes |
| SAC polar: 132°, 4/6, other two flagged | 132.2-132.3; 4 agrees, 1 unconfirmed (w05), 1 contradicted + fallback (w06) | yes |
| Sweep: 25 NAC frames, azimuths 3-153° | 69 windows, 25 distinct reference products, 3.3-152.7° | yes |
| Sweep bins: 0 of 12 at 60-120°, 10 of 15 at 120-153° | 60-90: 7 windows (5 inconclusive, 1 false alarm, 1 caught); 90-120: 5 (4 inconclusive, 1 false alarm); 120-181: 15 (10 accepted, 5 inconclusive) | yes |
| TC rung 29.6x, 3/4 accepted | scale 29.6; 3 agrees + 1 unconfirmed; archive offsets 381-431 m | yes |
| Multi-modal: 13 of 14 refused and fall back, the other unconfirmed | MI 1548: 3/3 fallback; IIRS: 10/11 fallback, `site_tc_ortho_iirs1555_w10` loftr + unconfirmed | yes |
| MiLOI: 81 pairs, 56 in S3; agrees 33/33 within 3 px, contradicted 43/43 wrong, unconfirmed 5/5 wrong | 81 latest ours rows, 56 S3; matcher-H-within-3-px: agrees 33/33 (rmse_gt 28/33), unconfirmed 0/5, contradicted 0/43 | yes |
| 16 MiLOI pairs over 90°, all S3, no method registered any | 16 rows with d_sun_angle >= 90, all S3; ours/SIFT/ORB/AKAZE 0 successes each | yes |
| Trust: 22 windows, Sun azimuths under 10° apart | 22 window ids (16 OHRC-NAC + 6 NAC-NAC), d_sun_az {3.3, 5.8, 9.1} | yes |
| 0/44 false alarms; 81% at 3 m; 100% from 5 m; 2/352 at 1-2 m | d=0: 0/44; d=3: 143/176 = 81.2%; d=5..200: 176/176 each; d=1: 0/176, d=2: 2/176 (58 unconfirmed) | yes |
| 136 real window pairs, 8 instrument pairings | 140 registered ids, 136 distinct ground windows (`_distinct_windows`); kinds: ohrc-nac 101, tc-iirs 11, nac-nac 6, tc-mi 6, ohrc-tmc2 4, tmc2-tmc2 4, ohrc-tc 4, ohrc-lola 4 = 8 | yes |
| Six loops close to a median 0.10 m | 6 loop rows, median 0.104 m, max 0.128 m (0.083 px on the B grid) | yes |
| OHRC -> NAC 74 °S: 0.41-1.0 px (0.51-0.94 m), Sun 3-6° apart, ~1 m grids | 20 rows, all agrees; held-out median 0.410-1.005 px; 0.510-0.936 m; d_sun_az {3.3, 5.8}; grids {0.931, 1.245} | yes |
| SAC equatorial held-out 0.69-1.7 px (1.1-2.7 m), 1.62 m grid | 0.690-1.676 px; 1.120-2.718 m; ref_gsd 1.622 | yes |
| OHRC -> TMC-2: azimuths 120°, incidence 59° apart, all 4 refused | d_az 120.2, d_inc -59.44; 4 contradicted + fallback | yes |
| NAC corners vs OHRC grid disagree by 1.9 km | wide_offset (+488, +1790) m, 4/7 templates, inverted intensity, applied | yes |
| Fore/aft: 1 of 4 accepted, held-out median 2.6 px (16 m) on 5.9 m grid | w04 agrees, 2.617 px x 5.929 m = 15.5 m; w02, w03 unconfirmed; w01 contradicted | yes |
| OHRC frames with LRO NAC: 3 frames at 3 sites; Kaguya TC 1 site | three `ch2_ohr_*` products (74 °S: NAC + TC + LOLA; 62 °S polar: NAC; 14 °S: NAC + TMC-2) | yes |
| In-sample (Q&A only): X 0.66-1.15, Y 0.73-1.07 px | insample_rmse_x 0.656-1.146, y 0.730-1.071 | yes |

**Result: 0 numeric mismatches.** Every latest real-pair row (146/146) names `49bdad9`; every MiLOI
row is "scored 49bdad9". The four withdrawn rows are the `sac_tmc_fore_aft_w0*` self-registrations
and appear nowhere.

**Chosen-number check (what claim-checker cannot see).** The OHRC -> NAC held-out range quotes all
20 windows (not the best); the SAC ranges quote all 6; the sweep quotes every bin including the
empty 60-120° band; the trust table quotes the 1-2 m floor. The one place a range hides a
distribution: "0.41-1.0 px" on slide 4 mixes two NAC grids (0.931 and 1.245 m), which the metres
range (0.51-0.94 m) makes harmless. No number was found to be "correct but chosen".

---

## B4: code correctness - the deliverables, numerically

`<data>/out/sac_ohrc_nac_w01/registered_product.tif` vs `data/pairs/sac_ohrc_nac_w01_ref.tif`:
GeoTIFF tags 33550 (pixel scale 1.622 m), 33922 (tie point), 34735/34736/34737 (GeoKeys, doubles,
ASCII: local equirectangular lat_ts -13.4724 lon_0 25.1875) are byte-identical; the product adds
GDAL_NODATA "nan"; shape 640x640 float32; 10.8 % NaN outside the footprint. Same result on the
south-polar `site_m1153871873le_m1363141432re_w01_t` bundle (1.245 m, polar stereographic tags
identical). The first GCP line checks out numerically: ISIS sample 887.1445 -> OpenCV x 886.1445 ->
GDAL 886.6445 (x + 0.5); reference (174.2116, 45.7515) -> map X = -547.7299 + 174.7116 x 1.622 =
-264.348 (file: -264.3476), Y = -419485.114 - 46.2515 x 1.622 = -419560.13 (file: -419560.1341).
All 140 bundles at `49bdad9` that have a georeferenced reference and inliers carry gcps.txt and
gcps.points (0 missing). Six stale bundles from older commits exist in `out/` (the withdrawn
fore/aft ids and two `site_tc_ortho_mi*` ids) and are referenced by nothing.

[in progress: silent exception scan (19 broad excepts in core/evaluation/ops, each to be judged),
tests that cannot fail, determinism]

---

## B1: coverage matrix - before

| PS demand | Strongest honest evidence on the deck today | In the logs but not on the deck | Missing entirely |
|---|---|---|---|
| Multi-modal | TC (visible) -> MI 1548 nm and IIRS: "learned matching fails; 13 of 14 refused and fall back" (slide 2) - reads as a failure | **The fallback's transform on MI 1548 nm agrees with the LoFTR registration on MI 749 nm (same TC window, same MI grid) to 0.28 / 1.09 / 0.23 px = 4.2 / 16.2 / 3.4 m on the 14.8 m grid, on all 3 windows, while the archive prior was 39-46 m off** (computed from the `out/` bundles, 20 Sep; not yet a logged number). IIRS: the two bands' fallbacks agree on w05/w07 (0 m) and disagree by 126 m, 2.0 km and 3.4 km on w11/w10/w08 - not a registration | an IIRS pair that registers |
| Sun-angle invariance | SAC 174°/6-6 and 132°/4-6; sweep 3-153° with the hard band shown; MiLOI to 181° with 0 % past 90° for every method | - | DEM relighting of the reference |
| Scale invariance | 3.7-5.8x (NAC), 29.6x (TC, 3/4), 240x (LOLA, declared failure) | - | coarse-to-fine pyramid |
| Sub-pixel accuracy | **nothing** - the word does not appear on the deck (the pipeline box "sub-pixel refinement" is the only mention) | synthetic exact truth: median rmse_gt_px 0.086 at 0° and 15°, 0.314 at 30° (60 m grid: 5.2 / 5.2 / 18.8 m); real OHRC -> NAC held-out median 0.41-1.0 px on 0.93/1.25 m grids; loops 0.083 px (0.104 m) on the 1.245 m grid; MiLOI agrees pairs vs the network truth: S1 median 0.52 px (n=9, truth error 0.22 px, grids 1.12-1.53 m), S2 1.18 px (n=11, truth error 0.26 px, grids 0.88-1.21 m), S3 1.12 px (n=13, truth error unmeasured) | - |
| Uniform distribution | "8x8 distribution check (coverage, CV)" box on slide 3; coverage column in REPORT.md (0.97-1.00 on the 74 °S windows) | grid_coverage_fraction per window | a number on the deck |
| Evaluation metric | held-out median residual, loop closure, verdict tables | runtime: median 9.0 s per 640-px OHRC -> NAC window (n=101), 7.9 s over all 140, on this CPU (`seconds` column) | - |
| Registered product | slide 3: "registered GeoTIFF, GDAL/QGIS control points, ISIS-style match list" | verified above: tags identical to the reference's | a thumbnail |
| Match points | same line | matches.csv with inlier flag, residual, cell state | - |
| OHRC as CH-2 input | 3 frames, 3 sites, 101 + 4 + 4 + 4 windows | - | - |
| TMC-2 as CH-2 input | OHRC -> TMC-2 0/4 (Sun elevations 10° vs 69°); fore/aft 1/4 | - | **a TMC-2 pass with a closer Sun** - see E4 below |
| IIRS as CH-2 input | TC -> IIRS, refused 10/11 | - | OHRC/TMC-2 -> IIRS (a reviewer may expect it; at 89 m vs 0.25-5 m it is a 18-350x scale gap on top of the modality) |

---

## Pre-registered experiments (written before they were run)

### E1. Multi-modal fallback vs the visible-band registration (new logged number)

- **Hypothesis.** On each Kaguya TC -> MI window the declared fallback transform for the 1548 nm
  band agrees with the accepted LoFTR registration for the 749 nm band (identical TC source
  window, identical MI reference grid) within 1.5 px of the 14.8 m MI grid (22 m) on all three
  windows. The IIRS 999 nm and 1555 nm fallbacks disagree with each other by more than 5 px
  (445 m) on at least one window, i.e. the IIRS fallback is not a registration and stays
  presented as a declared failure.
- **Metric.** `disagreement_median_px`: median over a 20x20 grid of reference points p of
  |H_ir(H_vis^-1 p) - p| in reference pixels, with p90, max, the mean vector and metres
  (x ref_gsd_m). Both H are the `H_final` in the bundles' report.json (what the system declared).
- **Rows produced.** `evaluation/multimodal_check.csv`, one row per window pairing (3 tc-mi,
  5 tc-iirs), written by `python -m ops.multimodal_check --log` (new freeze step `mmcheck`,
  after `real`). REPORT.md gets a table under each of the two sections.
- **Drop rule.** If any TC -> MI window disagrees by more than 3 px (44 m), the deck keeps its
  current wording ("refused and fall back") and the number is reported in REPORT.md only.
- **Expected from the unlogged computation (20 Sep):** 0.28, 1.09, 0.23 px.

### E2. Trust calibration on hard-Sun windows (extension, not a re-tuning)

- **Hypothesis.** The planted-failure detection measured on 22 windows with Sun azimuths under
  10° apart also holds on SAC's own pairs with azimuths 132-174° apart: 0 false alarms at d = 0,
  100 % flagged from 5 m. The 3 m rate may differ and is reported whatever it is.
- **What changes in code.** `ops/trust_real_calibration.py` selects a window as "independently
  good" when |NCC| >= 0.5 (was NCC >= 0.5). The sign change is the same one the sweep's rule v2
  made on 18 Sep: an opposite Sun anti-correlates a correct alignment. Every existing window has
  NCC > +0.5, so the 22-window table is expected to be unchanged; it is shown before and after.
  The per-trial CSV gains `d_sun_azimuth_deg` and `ncc_true` so REPORT.md can split populations
  without a join. Nothing else (thresholds, displacements, directions, seed) changes.
- **Rows produced.** Per-trial rows for the SAC windows that pass the rule (expected: 6
  equatorial, up to 4 polar) appended to `trust_real_calibration.csv`; the freeze's `trust` step
  then re-runs all windows from that CSV at the freeze commit.
- **Drop rule.** None - the result is reported either way. If d = 0 false alarms > 0 or the
  >= 5 m rate < 100 % on the hard-Sun windows, that becomes a disclosed limit on slides 2 and 5.

### E3. Sub-pixel, runtime and coverage: reporting only

No new measurement. `ops/make_report.py` gains (a) a "Sub-pixel accuracy, grid named" table
gathering the rows listed in the B1 matrix, (b) the median wall time per window, (c) the
coverage range. No number changes; no re-freeze needed for these on their own.

### E4. TMC-2 with a closer Sun (needs a download only Samartha can do)

The PRADAN TMC-2 footprint shapefile on disk (`pradan/shapefiles/TMC2_ShapeFiles`, 8,457
calibrated products) has three passes over SAC's equatorial OHRC frame (13.06-13.89 °S,
25.13-25.24 °E). Sun incidence estimated from the acquisition time (sub-solar longitude
propagated from the NAC M1350459544RE page value at -12.19°/day; checked against the two labels
on disk: 20250707 pass 15° vs label 20.6°, OHRC 82.6° vs label 80.1°):

| pass (nadir product) | Sun incidence (est.) | azimuth (est.) | vs OHRC (inc 80°, az 271°) | covers the frame |
|---|---|---|---|---|
| `ch2_tmc_ncn_20250707T1853051045_d_img_d18` (on disk) | 15-21° | 28-31° | Δaz 120°, Δinc 59° | fully |
| **`ch2_tmc_ncn_20251107T2205342105_d_img_d18`** | **~55°** | **~280°** | **Δaz ~9°, Δinc ~25°** | fully (lon 24.38-25.71, lat -30.4 to -12.9) |
| `ch2_tmc_ncn_20200203T1845562233_d_img_m65` | ~39° | ~73° | Δaz ~162°, Δinc ~41° | western half only (east edge at 25.19 °E) |

The 20251107 pass is the one to fetch (~0.6-0.9 GB zip; PRADAN serves TMC-2 at ~8 MB/s).
`ops/cut_pradan_pairs.py` is being parametrised (`--tmc-product`) so the cut is one command once
the zip is unpacked under `pradan/tmc2/data/calibrated/20251107/` and `geometry/calibrated/20251107/`.
Hypothesis: with Sun azimuths ~9° apart and incidence ~25° apart, at least 3 of 4 windows register
and are accepted. Drop rule: if the zip is not on disk by Tue 22 Sep evening, this is a Q&A
answer ("the only pass on disk has the Sun 59° higher; the 20251107 pass is identified").

---

## Findings [in progress]

(ID · severity · what · evidence · what a SAC reviewer concludes · fix and cost)

- **F1 · HIGH · The deck makes no sub-pixel claim although the PS demands one.** Evidence: the
  string "sub-pixel" occurs once on the deck, as a pipeline box. Reviewer: "they never measured
  it". Fix: E3 + one sentence on slide 4 naming the grids. Cost: 1 h, reporting only.
- **F2 · HIGH · Multi-modal is presented as a pure failure when the declared fallback is right to
  ~1 px.** Evidence: B1 matrix row 1. Reviewer: "no multi-modal capability". Fix: E1 + reword
  slide 2's multi-modal bullet. Cost: 3 h + re-freeze.
- **F3 · HIGH · TMC-2 evidence is 0/4 on a pair whose Sun is 59° higher.** Evidence: REPORT
  "SAC's benchmark site". Reviewer: "TMC is in the title and they show nothing that works".
  Fix: E4 (blocked on a download). Cost: 20 min download (Samartha) + 1.5 h + re-freeze.
- **F4 · MEDIUM · Trust calibration scope is narrow (22 windows, Sun azimuths under 10°,
  translations only).** Fix: E2 for the Sun scope; rotation/scale stay a Q&A answer.
- **F5 · MEDIUM · No runtime figure anywhere.** F2/feasibility readers look for one. Fix: E3.
- **F6 · LOW · `ops.freeze --check` says NOT FROZEN at HEAD** because of docs-only commits after
  the evidence commit; a reviewer running it would be confused. Fix: a re-freeze at the final
  code commit resolves it; otherwise say so in README.

[to be continued after Phase C/D]
