# SIH26166 national-round audit report

Started 20 Sep 2026, 02:30 IST, at commit `6a5686b` (submission-v1 tag = `0297936`, safe PDF copy
`presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf`, sha256 `f9d0194a…`). Answers
`AUDIT_PROMPT.md`. Every number in this file is either a command output recorded below or a
REPORT.md value at the commit named beside it. Sections are filled in the order the work was done;
Nothing is left in progress.

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

(The exception scan, the tests and determinism are in "B4: code correctness (continued)" below.)

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

## B3: scientific validity, as a SAC reviewer would attack it

**MiLOI truth network (partly circular).** Truth = one translation per image, solved from edges
where ours AND SIFT agree within 1 px with ≥ 50 inliers each; a pair that is itself an edge is
scored against the network solved without it (leave-one-out); a pair its network cannot reach
is not scored. S1: 8 edges, leave-one-out error median 0.22 / max 0.29 px (n = 3). S2: 7 edges,
0.26 / 0.40 px (n = 5). S3: 14 edges, every one a bridge, error not measurable (56 of the 81
scored pairs). What it really supports: (a) the per-scene *success* rates on S1/S2 are against a
truth validated to ~0.3 px; (b) on S3 they are against an unvalidated truth; (c) the *trust
cross-tab* (agrees 33/33 within 3 px, contradicted 43/43 beyond it) is robust to any truth error
under ~4 px, because the contradicted pairs' matcher errors start at 7.4 px (the next at 31.7,
median 288 px) and the agreeing ones end at 2.9 px. Only the five `unconfirmed` pairs (3.2-9.1 px)
sit near the threshold. Circularity cannot manufacture this separation: a truth built from our
own wrong answer would call that answer *right*, and the cross-tab shows the opposite. Q&A ready;
the deck already says "truth from other pairs where ours and SIFT agree" and names S3.

**Held-out residual as accuracy.** The 20 % held-out matches come from the same matcher, so an
error common to every match (a bias in how features are localised under one Sun) does not show.
Loop closure cancels per-image error too, by construction. The absolute-accuracy evidence is
therefore: the synthetic exact truth (0.086 px on a 60 m grid, shaded relief without cast
shadows), the MiLOI network truth (S1 median 0.52 px on a truth good to 0.22 px) and, for the
infrared band, the visible-band registration (E1). The deck labels the held-out figure "not ground
truth" and the loops "consistency, not ground accuracy". Nothing to fix; disclosed.

**Trust calibration scope.** 22 windows, all 74 °S, Sun azimuths 3.3-9.1°, planted translations
only. E2 extends the Sun scope to SAC's 132-174° pairs. Rotations, scale errors and local
distortion were never planted. What the mechanism would do: a rotation or scale error moves the
corner cells more than the centre, so the corner cells fail the per-cell area check (peak > 2 px
off) and are not verified; the frame verdict follows the share of agreeing cells (< 25 % =
contradicted, 25-50 % = unconfirmed). A small rotation that keeps > 50 % of cells within 2 px
would be `agrees` with a reduced verified count. Untested: Q&A answer, not a slide claim.

**Sun-sweep judging rule v2.** The rule is image evidence (|NCC| of the matcher's warp vs the
archive alignment, both on plain intensity), independent of the matches. v2 was defined after v1
had been run; both are in the log (v1 in `outcome`, v2 derived by `outcomes_v2` from the logged
NCCs) and the docstring records what moved: 14 caught-failure → inconclusive, 11 caught-failure
→ false-alarm, 1 missed → correct, 1 missed → inconclusive. v2 therefore made the *system* look
worse on 11 windows and better on one; it is a reinterpretation of the anti-correlation at
opposite Suns, not a re-tuning toward a better score. Selection: `sweep_order.txt` lists 30 NACs;
25 were used. The five skipped: M1258744166RE, M1295016540LE, M1338673330RE (the 4 m archive
correction could not be fitted; Sun azimuths 36.8°, 116.6° and 152.7° from the OHRC's) and
M159642518LE, M1258737127RE (no lit window shared; 21.1°, 35.7°). Two of the three
correction failures are hard-Sun NACs, so the sweep is mildly biased toward frames whose
gradient-orientation correlation at 4 m worked. Disclose in Q&A; the 120-153° bin still holds 15
windows from 5 frames.

**The wide-offset correction.** SAC's equatorial NAC corner prior sits 1.9 km from the OHRC grid.
Without the wide search the two windows would be cut over different ground and no matcher could
register them, so "6/6 accepted" depends on it entirely - as a coarse-search stage, not as the
registration: the 1.2 km template correlation at 4 m (inverted intensity, 4 of 7 templates
agreeing) is followed by a 4 m affine field (276/386 boxes, rms 13.2 m), and the matcher then
still moves the source 6-76 m from that corrected prior (the archive-offset column). Both stages
are logged in `site_geometry/M1350459544RE.json`. The deck says "a wide search removes it before
matching"; the Q&A answer is that the coarse search is part of the system's search range.

**In-sample RMSE vs SuperGlue.** Ours X 0.66-1.15 px, Y 0.73-1.07 px on the 1.622 m grid
(1.06-1.86 m / 1.18-1.74 m) against the paper's 0.62 / 0.57 px on 1.1179 m (0.69 / 0.64 m).
Not better, in metres either. Sound reasons it is not comparable: ours grades 3,219-4,182
MAGSAC++ inliers up to 3 px on a 640-px window, theirs a set of control points on their own
resampled grid; a final fit on a tighter inlier set would lower ours by construction and is
exactly the "choosing" Rule 7 forbids. A real gap may remain from relief: a homography over a
1 km window at 1.16° NAC emission and OHRC nadir is sub-metre, so the gap is more likely the
inlier population than the model. Left as the Q&A answer in DECK_V2_DRAFT; not raised on a slide.

**Determinism.** 144 of the 146 pairs with two or more logged rows have byte-identical numbers
(matches, inliers, held-out median, verified cells, verdict) on consecutive commits; the two that
differ changed because the code's rule changed (a verdict rule, a kind label). The re-freeze is
therefore expected to reproduce every registration number exactly.

## B4: code correctness (continued)

The 19 broad `except` handlers in `core/`, `evaluation/`, `ops/` (grep 20 Sep): the loaders
re-raise as `LoaderError`; `export._ref_geotags` returns "no geo" and the product then gets an
explicit pixel-frame sidecar; `pipeline._reliability` turns a crashed trust map into a printed
"UNAVAILABLE" and an empty verdict (never happened in 146 logged rows); `reliability._normalised`
falls back to raw pixels and *says* "raw"; `miloi` records a dead detector as a failed pair;
`distribution` skips a bad crop in a diagnostic; `fetch_weights` prints the failure; the two in
`make_report` are the audit's own (the report must still be written). None hides a number.
Tests: 302 pass; 9 `pytest.skip` are all environment guards (gitignored data, git absent). No
`assert True`. Seeds: `evaluate` seed 0, the trust calibration seed 7, USAC deterministic.

## B6: the deck as a SAC scientist reads it in two minutes (v1 pages, before the rewrite)

| Slide | Answers its pointers? | Verdict |
|---|---|---|
| 2 Idea | all four; the novelty sentence is the bold last bullet and reads in one pass | dense (240 words) but structured; the multi-modal bullet under-sold (F2); no sub-pixel word (F1); the trust map is the one image that proves the idea |
| 3 Approach | both; the pipeline figure is the strongest single image in the deck | no runtime (F5) |
| 4 Feasibility | all three; the hard band is stated with numbers; the sweep figure carries it | densest slide; no sub-pixel line (F1) |
| 5 Impact | both; F4 impact, F6 sustainability, F7 economics, F8 security each get a line | F7 "business viability" is thin (one clause); no rubric criterion is unanswered |
| 6 References | yes; the two SAC papers, MiLOI, LoFTR, MAGSAC++, the reliability lineage, the data licences | no repo link, no demo link (B8) |

Against the 13 finale-winner decks (RESEARCH_REPORT §4): architecture diagram yes, tech stack
yes, references yes, measured results yes (1-2 of 13 winners had any), prototype screenshot no
(3 of 13), demo link no (3 of 13). The two "no"s are Samartha's calls (video, repo).

## B7: competitive position (verified first-hand, 20 Sep; 2 fetches after a capped agent sweep)

- **Fable98/chandrayaan2-crossmatch**: real OHRC ↔ TMC-2 over 8 regions, fit RMSE 0.99-1.30 px
  with **6-7 inliers**, flagged LOW; LRO NAC 0.30-1.29 px with 5-6 inliers, LOW_CONFIDENCE;
  OHRC ↔ IIRS "0 direct inliers", composed through TMC; "NOT invariant to diametric shadow
  reversal (~162° flip yields only fragile LOW fits)"; a public Vercel demo.
- **Priyanshu8yadav/sih-2026 (CSPC)**: one real OHRC and one real NAC product, scored on
  *self-warped tiles* (30/30 and 25/30 "certified", medians 0.25 / 0.32 px); "cross-modal
  4 certified, 3 sub-pixel" without saying against what; the one real OHRC → NAC attempt
  **refused**; the ≥ 90° Sun claim "measured on synthetic terrain only"; an admitted unrepaired
  bug in the shipped phase-congruency weighting; ~2.5 s per 256² tile on CPU.
- **Ashwin0r7/siim**: no Chandrayaan-2 data at all; LRO NAC only; the same "silent failure"
  pitch with VERIFIED / REJECTED / INCONCLUSIVE; fails at a 51.5° incidence gap.
- Two more (PixOrb, LunarSynapse): one sample pair with "0.12 px", or synthetic only.

What the strongest can show that we cannot: a public live demo URL (Fable98). What we show that
none of them can: real cross-sensor registration on **SAC's own benchmark pairs** with thousands
of inliers per window and the Sun 174° apart; 136 real windows across 8 pairings; a trust layer
**calibrated** on planted failures (0/44 false alarms, 100 % from 5 m); loop closure at 0.10 m;
a measured multi-modal result (E1). The deck makes the first two unmissable (slide 2, bullet 3
and the bold last bullet); after this audit it also says sub-pixel with its grid and gives the
multi-modal number.

## B8: packaging

- README → REPORT.md → `python -m ops.freeze` reproduces every number from a clean commit; the
  freeze runs about two hours on this laptop. Good.
- The repository is private. Every "traces to the log" sentence is unverifiable to a reviewer
  until it is public. Recommendation: make it public and put the link on slide 6 (Samartha's
  decision, Rule 10).
- No demo video. Three of 13 finale winners had one; it is the one thing a cold reader cannot
  get from six slides. Recommendation: 2 minutes, unlisted, link on slide 6 (Samartha).
- The portal description (1,322 characters) carries the same numbers as the deck; it will be
  updated with the multi-modal and sub-pixel sentences after the freeze.

## Phase D: the re-freeze at `b678272` (started 20 Sep 02:57 IST)

Commit `b678272` = E1 + E2 + E3 code + `--tmc-product`, 302 tests green. Step timings and
results are filled in as they land.

- `real` (16.7 min): all 140 registered pairs re-run. **146 of 146 rows (140 pairs + 6 loops)
  are identical to the `49bdad9` rows** in matches, inliers, held-out median, verified cells,
  verdict, archive offset, loop RMS and sweep outcome. Every deck number that was already on the
  slides therefore stays exactly as it was.
- `sweep` (14.8 min), `loops` (2 s): identical, as above.
- `mmcheck` (1 s): **E1 result, logged** (`evaluation/multimodal_check.csv`, latest rows at
  `b678272`; the first logging carried a `-dirty` stamp because this report file - under `ops/` -
  was being edited during the freeze; it was parked in the scratchpad and the step re-logged on a
  clean tree, latest row wins):

  | window | fallback (1548 nm) vs LoFTR (749 nm), median | p90 | metres (14.8 m grid) | archive offset (1548 / 749) |
  |---|---|---|---|---|
  | w01 | 0.283 px | 0.431 | 4.20 m | 41.5 / 41.0 m |
  | w02 | 1.093 px | 1.205 | 16.18 m | 37.8 / 46.4 m |
  | w03 | 0.227 px | 0.356 | 3.36 m | 38.2 / 38.9 m |

  Hypothesis E1 holds (all three under 1.5 px; drop rule at 3 px not triggered). IIRS band vs
  band: w05 and w07 agree exactly (0 px), w11 differs by 1.4 px (126 m), w08 by 38.6 px (3.4 km),
  w10 by 21.8 px (1.9 km) - the IIRS fallback is not a registration, as pre-registered, and stays a
  declared failure on the deck.
- `trust` (41.0 min; from 03:45 a second heavy job from another session - the `sih26227` venv's
  `evaluation.incremental_eval` - ran beside it and commit charge reached 49.7 of 53.4 GB; it was
  left alone and nothing failed). **E2 result, logged** (`trust_real_calibration.csv`, 30 windows,
  2,220 trials):

  | population | windows | 0 m (false alarms) | 1 m | 2 m | 3 m | 5 m | 10-200 m |
  |---|---|---|---|---|---|---|---|
  | Sun azimuths 3.3-9.1° (74 °S), grids 0.93 / 1.25 m | 22 | **0/44** | 0/176 | 1/176 (0.6 %) | 130/176 (**73.9 %**) | 176/176 | 176/176 each |
  | Sun azimuths 132-174° (SAC's pairs), grids 1.62 / 1.22 m, true-alignment NCC −0.53 to −0.90 | 8 (`sac_ohrc_nac_w01-w06`, `sac_polar_ohrc_nac_w01`, `w03`) | **0/16** | 0/64 | 4/64 (6.2 %) | 8/64 (12.5 %) | 60/64 (**93.8 %**) | 64/64 each |

  Hypothesis E2 holds on false alarms (0/16) and from 10 m; at 5 m the hard-Sun population is
  93.8 %, not 100 %, because 5 m is only 3.1 px on SAC's 1.62 m grid (4.0 px on the 1.25 m grid).
  The 3 m rate of the 22-window population moved from 81.2 % (143/176, the 19 Sep freeze) to
  73.9 % (130/176): the same windows and the same code path, but the planted directions and
  match noise come from one RNG stream that the eight SAC windows (alphabetically first) now
  consume ahead of them - a second random draw of the same experiment. 3 m is the transition
  point (2.41 px against a 2 px cell threshold), and two draws put it at 74-81 %. Rule 7: the
  frozen 74 % is what the deck says; both draws are recorded here and in DECK_V2_DRAFT. Polar w02
  and w04 (verdict `agrees`, 697 and 511 inliers) were skipped by the |NCC| ≥ 0.5 rule.
- `miloi` (11.9 min): re-judged and re-scored, 324/324 rows at `b678272`; the cross-tab is
  unchanged (agrees 33/33, unconfirmed 0/5, contradicted 0/43) - the trust code did not change.
- `viewpoint`, `calib`, `gate2` (1.7, 1.9, 2.0 min): synthetic sweeps re-run; the medians are
  unchanged (deterministic seeds; e.g. 0.086 px at 0° and 15°).
- `report` (0.3 min): REPORT.md regenerated at `b678272`; `python -m ops.freeze --check`:
  **FROZEN** (146/146 real rows, 324/324 MiLOI rows, 8/8 multi-modal rows, 10/10 steps). Total
  90 min.

## Deck v3 (20 Sep, 04:45): what changed on the slides

| Slide | Before (v2, `49bdad9`) | After (v3, `b678272`) |
|---|---|---|
| 2, multi-modal bullet | "learned matching fails; 13 of 14 windows are refused and fall back, the other stays unconfirmed" | "LoFTR refused on 3/3 windows; the declared fallback lands 0.23–1.09 px (3.4–16 m) from the visible-band registration of the same window. TC to Chandrayaan-2 IIRS (12×, 89 m): 10/11 refused, none registers." |
| 2, trust bullet | 22 windows, 0/44, 81 % at 3 m, 100 % from 5 m, 2/352 at 1-2 m | 22 windows, 0/44, **74 %** at 3 m, 100 % from 5 m, **1/352**; **8 SAC windows, Suns 132–174° apart: 0/16 false alarms, 94 % at 5 m, 100 % from 10 m** |
| 2, Sun/scale bullet | "to LOLA 60 m it declares failure" | "LOLA 60 m: declared failure" (words, to fit) |
| 3, hardware bullet | "CPU only, no discrete GPU, fully offline" | + "median 10.7 s per 640-px window (89 OHRC → NAC windows)" |
| 4, first bullet | 136 pairs, 8 pairings, public data, open source; six loops 0.10 m | 136 pairs, 8 pairings, public data, open source; "one command re-runs every number from a clean commit" |
| 4, new bullet | - | "Sub-pixel, grid named: 0.086 px vs exact truth at 0–15° Sun difference (synthetic, 60 m grid); six loops close to 0.08 px (0.10 m) on the 1.245 m NAC grid; MiLOI network truth, 9 S1 pairs: median 0.52 px on 1.1–1.5 m grids (truth error 0.22 px)" |
| 4, strategies | two bullets | one bullet, same content |
| 5, first bullet | 81 % at 3 m | 74 % at 3 m; + "(8 SAC windows with Suns 132–174° apart: 0/16 false alarms, 100% from 10 m)" |
| 5, figure | 22-window bars | + the 8 hard-Sun windows as diamond markers, two populations, never pooled |
| 2 / 4 body size | 12.5 / 13 pt | 11.5 / 12.5 pt (the new clauses did not fit; `export_pdf`'s footer check enforces it) |

Build: `AUDIT: clean`; `export_pdf`: `PDF CHECK: clean`, 6 pages, 1,112,699 bytes. All six pages
rendered and read. Words per slide: s2=266, s3=136, s4=248, s5=165, s6=150.

## B1: coverage matrix - after

| PS demand | On the deck (v3) | Still missing |
|---|---|---|
| Multi-modal | TC → MI 1548 nm: refused 3/3, fallback within 0.23-1.09 px (3.4-16 m) of the visible-band registration; IIRS: refused, none registers; LOLA: declared failure | an IIRS pair that registers (89 m pixels, 12-350× scale: beyond this method) |
| Sun-angle invariance | SAC 174° 6/6, 132° 4/6; sweep 3-153°; MiLOI to 181°; trust calibration now at 132-174° too | DEM relighting |
| Scale invariance | 3.7-5.8×, 29.6× (3/4), 240× declared failure | pyramid |
| Sub-pixel | named grids on slide 4: 0.086 px / 60 m (exact), 0.41-1.0 px / 0.93-1.25 m (held out), 0.08 px / 1.245 m (loops), 0.52 px / 1.1-1.5 m (MiLOI, truth 0.22 px) | - |
| Uniform distribution | the 8×8 check on slide 3; coverage in REPORT.md (median 1.00; 17/20 ≥ 0.95) | a coverage number on a slide (no room; REPORT.md carries it) |
| Evaluation metric | held-out median, loops, verdict tables, runtime 10.7 s | - |
| Registered product / match points | slide 3; verified numerically (B4) | a thumbnail |
| OHRC / TMC-2 / IIRS as CH-2 input | OHRC 3 frames; TMC-2 0/4 (hard Sun) + fore/aft 1/4; IIRS as reference 10/11 refused | TMC-2 with a closer Sun (E4: pass identified, download pending); OHRC/TMC-2 → IIRS |

## Findings and resolutions

| ID | Sev. | Finding | Resolution |
|---|---|---|---|
| F1 | HIGH | No sub-pixel claim on the deck | **Fixed** on slide 4 with grids named (E3, REPORT.md "Sub-pixel accuracy"); `b678272` |
| F2 | HIGH | Multi-modal presented as a pure failure | **Fixed**: measured (E1, `ops/multimodal_check.py`, freeze step `mmcheck`), on slide 2 and in the portal text; `b678272` |
| F3 | HIGH | TMC-2 evidence is 0/4 on a pair with the Sun 59° higher | **Blocked on a download** (Rule 10): pass `ch2_tmc_ncn_20251107T2205342105_d_img_d18` identified from the PRADAN footprints (E4); `cut_pradan_pairs --tmc-product` ready; Q&A answer written in DECK_V2_DRAFT; push notification sent to Samartha |
| F4 | MEDIUM | Trust calibration scope: Sun azimuths under 10° only, translations only | **Half fixed**: Sun scope extended to 132-174° (E2) on slides 2 and 5; rotation/scale stay a Q&A answer |
| F5 | MEDIUM | No runtime figure | **Fixed** on slide 3 (10.7 s per window) |
| F6 | LOW | `--check` at HEAD says NOT FROZEN after docs-only commits | **Disclosed** in STATUS.md (expected; the rows name `b678272`) |
| F7 | MEDIUM | The 3 m detection rate has ±7-point sampling scatter (81 → 74 %) | **Disclosed** here and in DECK_V2_DRAFT; the deck quotes the frozen 74 %; Q&A: "about three quarters at 3 m, everything from 5 m" |
| F8 | LOW | Sweep NAC selection mildly favours frames whose 4 m correction fitted (2 of 3 failures are hard-Sun) | **Q&A answer** (B3) |
| F9 | LOW | fig6 legend/label overlaps after adding the second population | **Fixed** (labels lifted above markers, legend moved) |
| F10 | LOW | Repo private; no demo video | **Samartha's decision** (B8) |
| F11 | LOW | The runaway `precompute_demo_cache` (no arguments caches every pair) | 75 stray caches deleted; the 6 demo caches are at `b678272` |

**Numbers that moved, before → after** (all others reproduced exactly):
3 m detection 81 % → 74 % (F7); 1-2 m contradictions 2/352 → 1/352 (same cause); mean verified
cells at 3 m 7.3 → 10.9; runtime median 10.0 → 10.7 s (wall time). New: 0.23-1.09 px multi-modal;
the 8-window hard-Sun table; the sub-pixel table.

## B5: the demo (Gate 4 by AppTest, 20 Sep 04:43-04:50)

The six demo caches were regenerated at `b678272` (`ops.precompute_demo_cache <pairs>`; a first
call without arguments started caching all ~150 pairs and was stopped - Known issue 16). With
every socket connect blocked in the process (the demo must be offline), three consecutive
AppTest sessions of the four demo pairs (`pair_01`, `pair_04_tierD_native`, `sac_ohrc_nac_w06`,
`site_tc_morning_mi1548_w01`) rendered, aligned from the cache and raised nothing: 12/12 clean,
0.8-2.4 s per cached align. Cold start: 1.0 s to import Streamlit, 3.5 s to the first render,
1.2 s for the cached align of `pair_01`. On-screen strings were grepped for Invariant 2: the
same-sensor note fires on NAC ↔ NAC and TMC-2 fore/aft; "cross-sensor" is used only for
different instruments; no "sub-pixel" claim is printed by the app. The live server (a human at
the keyboard, wifi off) remains Samartha's Gate 4.

## claim-checker on deck v3 (20 Sep 04:50; read-only agent, verified first-hand)

**0 numeric mismatches** on every slide against REPORT.md at `b678272` (the five new figures and a
sample of 15 older ones re-checked; the freeze verified from the CSVs independently). Findings
2 HIGH / 5 MEDIUM / 13 LOW, all on scope and labels; applied before the final export:

- H1: the 0.086 px figure now carries its metres (= 5.1 m) and says "at 0° and 15°" (M4).
- H2: the portal's short description now says "100 % flagged from 10 m" (true of both Sun
  populations); the long one already split them.
- M1: slide 5 names the population ("on 22 windows with Sun azimuths under 10° apart") and gives
  the hard-Sun 94 % at 5 m beside its 100 % from 10 m.
- M2: "Sun azimuths 132–174° apart" on slides 2 and 5 (was "Suns").
- M3: slide 2's multi-modal bullet leads with metres (3.4–16.2 m) and names MI's 14.8 m grid
  before the pixels.
- M5: `build_deck.py`, `DECK_V2_DRAFT.md` and `SUBMISSION_FIELDS.md` now name `b678272` / v3.
- L1-L3: "3.4–16.2 m", "0.41–1.01 px", "0.69–1.68 px" as REPORT prints them; L11 aligned.
- L4-L8 (make_report should also print the incidence difference, the fore/aft grid, the S3
  split of the >90° pairs, "136 distinct windows" and the MiLOI metres): **not done** - each is a
  reporting-only change under `ops/` that would re-stamp REPORT.md's header after the freeze;
  the values are traceable to the log rows named in DECK_V2_DRAFT.md. Worth doing before the
  finale, not before the upload.
- L9/L10: Q&A caveats (the MiLOI raw matching is not redone by the freeze; polar w05 is
  `unconfirmed`, w06 contradicted + fallback).
- L12/L13: the PDF was re-exported from the rebuilt deck and everything committed (below).

## Remaining risks, ranked

1. **TMC-2**: the title names it and the deck shows a refusal. Only the download closes it.
2. **In-sample RMSE vs SuperGlue** is not better (Q&A only; a reviewer who knows the paper will
   ask).
3. **S3 truth** unvalidated for 56 of 81 MiLOI pairs (disclosed on the slide; the 7.4 px
   separation is the defence).
4. **The 3 m point** is a coin-flip region; say so rather than defend 74 %.
5. **Slide density**: slides 2 and 4 are at 11.5 / 12.5 pt; a cold reader gets a lot per slide.
   The structure (pointer headings, one figure each) carries it, but nothing more can be added.
6. **Demo**: three AppTest runs pass on the cached pairs [see below]; a live align on a busy
   laptop still takes 48-61 s (Known issue 12).

## Verdict

Against the visible field (B7), no public SIH26166 repo shows real cross-sensor registration on
SAC's own benchmark pairs, thousands of inliers per window, a calibrated failure detector, loop
closure, or a measured multi-modal result; ours now shows all five with the grid named beside
every sub-pixel figure. What would still beat us: a team that registers OHRC ↔ TMC-2 on a
closer-Sun pass with a working number (we show a refusal), a team whose in-sample RMSE beats
SuperGlue on SAC's pair, or a team with a live demo link and video where we have neither. The
deck is at its honest ceiling for the evidence on disk; the one measurable step left is E4, and
it is a 20-minute download away.

## Findings as first written (before Phase C/D; their resolutions are in the table above)

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

Session end: 20 Sep 2026, 05:10 IST. Final PDF `presentation/SIH26166_LunaXX_deck.pdf`, sha256
`86ac52fd1f4b2f244aa6ecb5597943947978920c14640d8429b186f49672063c`, 1,112,452 bytes. The
pre-audit deck stays reachable as tag `submission-v1` and the `_v1_SAFE.pdf` copy. v3 beats v1
because it says sub-pixel with the grid named, measures the multi-modal fallback, extends the
trust calibration to opposite Suns and states the runtime, with every number frozen at one commit
and 0 numeric mismatches under claim-checker; the one number that got worse (74 % vs 81 % at 3 m)
is a fair second draw and is disclosed.
