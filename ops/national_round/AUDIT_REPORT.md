# SIH26166 national-round audit report

Two passes on 20 Sep 2026: 02:30-05:10 and 09:00-13:00. Started at commit `6a5686b`; the
pre-audit submission is preserved as tag `submission-v1` (= `0297936`) and
`presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf`, sha256 `f9d0194a…`. Answers `AUDIT_PROMPT.md`.
Every number here is either a command output recorded below or a REPORT.md value at the commit
named beside it. Sections are in reading order, not in the order the work happened. Nothing is
left in progress.

---

## What this found, in one page

**The deck's numbers were already right.** Both passes re-derived every figure on every slide and
in the portal text straight from the CSV cells, independently of REPORT.md's rendering: **zero
numeric mismatches**, twice. `claim-checker` agreed. So the audit's value was never going to be
in catching a wrong number on a slide.

**It was in catching a wrong file.** `is_inlier` in the exported match table was decided by
comparing float64 match coordinates against their float32 copies - an identity that holds for
some reference grids and not others. **41 of 183 exported bundles flagged zero inliers while
MAGSAC++ had kept thousands**, so they shipped an empty `gcps.txt`, an empty `gcps.points` and a
header-only `matches_isis.csv`. Those are deliverables the problem statement names by name and
slide 3 tells a reviewer we produce. No metric reads that file, which is why nothing noticed -
except loop closure, the one number computed from it, which was therefore also slightly wrong.
Fixed, tested five ways, and every bundle rewritten (F12).

**And in catching a check that could not fail.** The first pass had looked for exactly this defect
and reported "0 missing". Its condition used `inliers_exported` - the field the bug set to zero -
so it skipped precisely the broken bundles. A check whose predicate comes from the value under
suspicion is not a check (F17). Both replacements now compare quantities with independent
provenance.

**Eight ceiling-raising candidates were closed.** Four produced new frozen evidence: the
multi-modal fallback measured against the visible band (0.23-1.09 px = 3.4-16.2 m), a sub-pixel
claim with every grid named, the trust layer extended to opposite-Sun windows and then to
rotation and scale errors, and one whole OHRC/NAC overlap tiled end to end (37 windows, 13 km²).
Two produced nothing and say so with their reasons: a tighter final fit **missed its
pre-registered bar and was dropped** even though adopting it would have let us print a pixel
figure lower than the SAC paper's, and DEM relighting is not feasible on any elevation data we
hold. One is blocked on a download only Samartha can do (a TMC-2 pass with a closer Sun). One was
reporting-only.

**A limit of our own headline metric is now known.** `residual_median_px` is robust only while the
inlier ratio stays well above 0.5; at 0.542 one correctly registered window reported 316 px. It
was found only because the dense tiling looked between the hand-picked windows, all of which have
ratios 0.614-0.998. Rather than quote the tiled set's median and leave that window out of sight,
slide 4 now says "37/37 accepted, median 0.61 px, **36 of 37 under 3 px**", and REPORT.md's own
section explains the 37th in the paragraph above its table. A judge who checks the log will find
the number we told them about.

**Honest cost.** The freeze was run three times. Two of those re-runs were caused by defects in
code this audit wrote, and one by an operator error of mine; all three are written up in full
(F18, F19 and "The freeze had to be run twice"). Nothing about them touched a number.

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
(Second pass: 325 tests after the audit's own additions - 20 on the planted-error transforms, 3 on
report provenance.)

### Unhandled inputs (second pass): nothing raises, and one confound was caught in the probe itself

`run_all` promises it "never raises on a bad pair" and `export_bundle` promises the same. Probed
with seven inputs the pipeline has never been shown (`scratchpad/b4_edge_inputs.py`): uint16,
uint8, NaN borders, tiny frames, a constant source, two constant images, an all-NaN source.
**RESULT: no input raised**, every case produced a bundle (5 files with no transform, 7 with one),
and the trust layer refused every case whose answer was wrong.

The first run of that probe also produced an apparently alarming result - the same pair as uint16
collapsed from 2,952 inliers to 12 - which on inspection was **an artefact of the probe, not of
the pipeline**: it wrote its cases as untagged TIFFs, so `load()` reported no map scale,
`to_common_gsd` took its no-op branch, and a 2,383-px source was matched against a 479-px
reference at five times the wrong scale. Every case was therefore a scale-mismatch test wearing a
dtype test's clothes. Recorded here because it is exactly the kind of confound this audit is
supposed to catch in its own work, not only in the project's. The corrected probe
(`scratchpad/b4_bitdepth.py`) writes each case with the pair's own geotransform so the only thing
that changes is the one the case names. On `site_ohrc_m1363141432re_w03_t` (source 2,383 px at
0.25 m, reference 479 px at 1.245 m):

| case | dtype | matches | inliers | held-out median px | verdict |
|---|---|---|---|---|---|
| float32 as-is (the frozen pipeline) | float32 | 2968 | 2952 | 0.4996 | agrees |
| uint16, values preserved | uint16 | 2968 | 2957 | 0.4936 | agrees |
| uint16 × 256 (a true 16-bit encoding) | uint16 | 2969 | 2953 | 0.4863 | agrees |
| float32 × 256 (scale only) | float32 | 2968 | 2952 | 0.4996 | agrees |
| float32, percentile-stretched to [0,1] | float32 | 2971 | 2954 | 0.5018 | agrees |
| uint8, values preserved | uint8 | 2968 | 2957 | 0.4936 | agrees |
| NaN borders (source 160 px, reference 40 px) | float32 | 0 | 0 | n/a | unconfirmed, no transform |
| frames 16× smaller (source 148 px, reference 29 px) | float32 | 0 | 0 | n/a | unconfirmed, fallback declared |
| constant source | float32 | 19 | 5 | 186.5 | **contradicted**, fallback declared |

**The pipeline is bit-depth and scale agnostic, and the reason is in the code rather than in
luck.** `core.illumination.normalize` returns [0, 255] whatever comes in, because gradient
orientation weights by `mag / (mag + k)` with `k` the median gradient magnitude of that same
image. Measured on the same window: raw maxima of 251 and 64,269 both normalise to
[13.27, 240.01] with mean 109.5 and standard deviation 34.4, so `core.matcher`'s unconditional
divide by 255 receives the same array either way. A judge asking "what if we hand you 16-bit
data?" can be answered with this table. The three degenerate inputs behave as the docstrings
promise: no exception, a bundle written in every case, and the one case that produced a
confident wrong answer (a constant source, 19 spurious matches) was contradicted and fell back.

### BLOCKER found and fixed: the exported match points flagged no inliers on 41 of 183 bundles

Chasing why the probe's bundles held 6 files instead of 8 turned up a real defect, not a probe
artefact. `core.export.match_table` decided `is_inlier` by asking whether a match's coordinates
appear in the inlier array - an exact float comparison. But `core.ransac.filter_matches` casts to
**float32** (cv2 requires it) while the points it is handed are **float64** out of
`core.scale.to_original`. The identity therefore holds only when the float64 value happens to be
exactly representable in float32, which depends on the resample factor and so on the reference
grid. Measured across every exported bundle: **41 of 183 flagged zero inliers** while MAGSAC++
had kept thousands - for example `site_m1153871873le_m1363141432re_w02_t`, 2,734 inliers, 0
flagged. Those bundles have **no `gcps.txt`, no `gcps.points`, and a `matches_isis.csv` with only
its header**: three of the deliverables the problem statement names ("registered product with
corresponding match points"), and slide 3 says we export them.

Why almost nothing caught it. `inlier_count`, the residuals, the verdicts and the trust map are
all computed from the in-memory result, never from the exported table, so they were and remain
correct. The one field that did expose it, `inliers_exported`, is written into each bundle's
`report.json` and read by nobody. **My own Phase A check missed it for a worse reason:** it asked
"does any bundle have a georeferenced reference and `inliers_exported` and yet no `gcps.txt`?" -
and `inliers_exported` was 0 on exactly the broken bundles, so the condition skipped them and the
check reported "0 missing". A test whose predicate is derived from the same broken value cannot
fail. Recorded rather than quietly corrected.

**One logged number WAS affected, and the first draft of this section said otherwise.** Loop
closure is the only metric computed from the exported match table rather than from the result
dict: `ops/loop_closure.py::_inlier_src_points` reads `matches.csv` and keeps the rows flagged
`is_inlier`. Its three legs' bundles were among the ones whose flags survived, but not all of
them did - a handful of inlier coordinates per window failed the float32 round trip and were
dropped from the exported set - so the loops were computed over slightly the wrong points. After
the fix the exported flags equal MAGSAC++'s count exactly (`site_ohrc_m1153871873le_w01_t`: 4,476
kept, 4,476 flagged), and the loop figures move by about 2 %:

| loop | RMS m before | after |
|---|---|---|
| `…_w01_t` | 0.1284 | 0.1307 |
| `…_w02_t` | 0.1038 | 0.1062 |
| `…_w03_t` | 0.1208 | 0.1211 |
| `…_w04_t` | 0.0965 | 0.0956 |
| `…_w05_t` | 0.0965 | 0.0966 |
| `…_w06_t` | 0.1041 | 0.1077 |

Some rise, some fall, which is what a corrected point set should do rather than a systematic
shift. The deck's loop figure moves with it; the new value is taken from REPORT.md at the freeze,
not from this table. Every other logged number is unchanged, and that was verified pair by pair
rather than assumed.

Fixed in `183a54f`: `filter_matches` now returns MAGSAC++'s own boolean mask in its `info`, and
`match_table` uses it; the coordinate comparison stays only as a fallback for result dicts
pickled before the mask existed (old demo caches). `core/test_export_inlier_flag.py` pins it with
five tests, including one that deliberately builds points which lose bits in float32 and asserts
it proves nothing if they do not. Verified end to end on two previously broken pairs and one
previously working one: all three now write 8 files with every inlier in the ISIS list. The
re-freeze rewrites all 183 bundles.

**One deck number changes** - the loop-closure figure on slide 4, by about 2 %. Everything else
on the deck is untouched; what mainly changes is what a reviewer gets if they open the
deliverables.

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

## B5 (second pass): the demo as a LIVE SERVER, driven through a browser

AppTest never renders a pixel - it executes the script and inspects the element tree - so the
first pass could not see CSS, layout or anything a judge would actually look at. This pass ran
`streamlit run app/streamlit_app.py` on port 8765 and drove it through Chrome DevTools.

| Pair | What the page showed |
|---|---|
| `sac_ohrc_nac_w06` | `ALIGNED`, tier "B (OHRC-NAC real)", "Chandrayaan-2 OHRC vs LRO LROC NAC", reference grid 1.622 m/px, verified 58 / weak 6 / no evidence 0, "AGREES - 91% of 64 measurable cells", held-out median 1.0037 px = 1.63 m, four download buttons |
| `site_tc_morning_mi1548_w01` | `FALLBACK USED`, tier "C (visible-infrared real, multi-modal)", "Kaguya Terrain Camera vs Kaguya Multiband Imager", "CONTRADICTED - 16% of 51 measurable cells", verified 0 / no evidence 59, quadrant spread "18 px (266 m) - the uncertainty to quote" |
| `pair_04_tierD_native` | `FALLBACK USED`, tier D, "Kaguya_TC vs LOLA_LDEM", "CONTRADICTED - 0% of 35 measurable cells", grid 9.37 m/px |
| `pair_01` | `ALIGNED`, "CH2_OHRC vs CH2_OHRC", and the same-sensor note fires: *"Same instrument on both sides - this is **not** a cross-sensor result, whatever else it shows."* Grid 0.2298 m/px, labelled "(catalogue)" |

Change detection was run on a result: "2 candidates ... After the reliability gate: 2 kept (in
verified cells), 0 rejected, 0 unassessable", with its own caveat sentence. Every collapsed
section was expanded and re-scanned.

**Invariant 2 on screen: clean.** "cross-sensor" appears twice, both correct - once to deny it
(`pair_01`, same instrument) and once in the TC → MI pair note, where it is right because the
Kaguya Terrain Camera and the Multiband Imager *are* different instruments (that string comes
from the pair's own `geometry_prior.json`, written by `ops/cut_site_pairs.py:604`). "multi-modal"
appears only on the visible↔infrared and optical↔elevation pairs. "verified" is used only as a
cell state; the app makes no sub-pixel claim at all. `rmse_gt_px` reads "n/a - no ground truth on
a real pair". Every pixel figure on screen carries its metres and names its grid.

**Offline: clean.** `performance.getEntriesByType('resource')` after four aligns: 190 requests,
**0** not to `localhost:8765`. Zero console errors or warnings; zero server-side errors.

## B5 (second pass): what demo-medic found, verified first-hand

Every claim below was re-checked here before being acted on. `git diff b678272..HEAD -- core/
app/` contains no `.py` line; both `.streamlit/config.toml` copies are sha256 `a0f5bee4…`;
`weights/loftr_outdoor.pt` is sha256 `6d2e110d…`, exactly the pin at `core/bench_loftr_cpu.py:54`;
all six cache sidecars say `b678272`; `ops/` is imported by neither `app/` nor `core/`.

- **HIGH-1, a stale cache was undetectable - FIXED.** The identification plate printed the cache's
  commit verbatim with nothing comparing it to the running code, so a cache written by older code
  would show old numbers under a commit string nobody reads: "plausible, internally consistent,
  and wrong", which is the exact failure this project exists to prevent. The plate now reads
  `CACHED RESULT commit <a> — CODE IS NOW <b>` in the caution colour whenever they differ, with
  the words as well as the colour carrying it. Driven both ways through AppTest
  (`scratchpad/test_stale_cache_tag.py`): matching cache → plain tag, no warning; a cache stamped
  `deadbee` → the warning, naming both commits. Cost measured at ~0.25 s, cached per session.
- **HIGH-2, gitignored demo assets inside OneDrive with no backup - DONE.** `weights/` and the six
  demo pairs are copied to `C:\sih26166_backup\` (108 MB), the weights verified by hash after the
  copy. `demo_cache/` is copied after the final precompute; the USB step is in `day_24.md`.
- **MEDIUM-1, the downloaded report contradicted the screen - FIXED.** A report exported from a
  cached result stamped only the commit that WROTE the file, while the plate showed the commit
  that COMPUTED the numbers. `report.md` now says "Result computed by commit `a`; this report
  written by commit `b`" whenever they differ, and keeps its single-commit form when they do not
  (`core/test_export_provenance.py`, 3 tests).
- **MEDIUM-3, `discover_pairs()` re-stats every pair directory on every rerun - FIXED.** It had no
  `@st.cache_data` while its two neighbours did. This mattered more after E7 took `data/pairs`
  from 160 to 197 directories, and the swipe slider is the control a judge drags continuously.
- **MEDIUM-2 and MEDIUM-4, accepted as they are.** If `data/pairs` disappears the six caches
  become unreachable through the UI (the folder is the index); the backup above is the answer.
  The 197-entry dropdown is long, but the cached six sort first and are marked "(cached)", and
  changing the selection only resets the result - it never starts a run.
- **LOW-1/2/3 noted, not acted on:** `verify_weights()` is not called on the demo path (a
  structurally different checkpoint would still be caught by `strict=True`, and the file was hash-
  checked here today); the per-image fullscreen button is unstyled and unexercised; the loose
  `ops/make_report.py` edit is now committed.

**Gate 4 remains a human job.** demo-medic wrote the by-hand procedure and it is reproduced in
`ops/specs/day_24.md`; the one step worth repeating here is that Windows reconnects wifi on
resume, so `ping -n 1 8.8.8.8` must be re-run after the lid test or the whole run proves nothing.

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
- **Ashwin0r7/siim** (README re-read here, 20 Sep): the closest pitch to ours - "CPU-only, runs
  offline", verdicts of VERIFIED / REJECTED / INCONCLUSIVE "with the reasons", and the same
  insistence on corroboration rather than ground truth. Its own README is also the sharpest
  statement of what it lacks: "**NO Chandrayaan-2 data**. OHRC / TMC-2 / IIRS are behind ISSDC
  authentication"; "**NO multi-modal claim is supported anywhere in this repository**"; "**NO
  Sun-azimuth invariance claim**"; "no measured edge above 40° passes". Its headline 0.003 px is
  on **self-warps** - an image warped and registered back to itself. So on the three things the
  PS actually asks for, its author has disclaimed all three in writing.
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

## Second pass (20 Sep, from 09:00): what the first pass left undone

The first pass closed at 05:10 with five items open or only reasoned about. Nothing below was run
before this section was written.

**Open audit items (no new numbers):** (a) the live-server demo run and its on-screen strings
(B5 - only AppTest was run); (b) unhandled inputs - 16-bit data, NaN borders, tiny frames, empty
matches (B4); (c) `demo-medic`, which Phase D asks for because `core/export.py` changed; (d) the
claim-checker's L4-L8, reporting-only additions to `ops/make_report.py`; (e) before/after renders
of the rewritten slides (B6); (f) the README's one-pair command, re-run (B8).

### E5. Trust layer against NON-translation errors (pilot, then logged if it earns a place)

- **Hypothesis.** A planted rotation or scale error about the frame centre displaces the corner
  cells most. The per-cell area check refuses exactly the displaced cells: of the cells whose true
  displacement exceeds 2 px, at least 90 % are NOT `verified`; of the cells displaced by less than
  1 px, at least 80 % stay `verified`. The frame verdict turns `contradicted` only once fewer
  than 25 % of cells agree, i.e. at corner displacements of roughly 8 px and beyond; below that
  the frame is `agrees` or `unconfirmed` with a reduced verified count - the map, not the
  verdict, carries the information.
- **Metric.** Per trial: the frame verdict, and per cell the true displacement (RMS over a 5×5
  lattice, `core.reliability._true_error_grid` with the unshifted H as truth) against the cell
  state. Cell-level sensitivity = share of cells with true displacement > 2 px that are not
  verified; specificity = share of cells with displacement < 1 px that are verified (among cells
  verified at d = 0).
- **Pilot.** 6 windows (2 OHRC→NAC at 3.3°, 1 at 5.8°, 1 NAC→NAC at 9.1°, 2 SAC equatorial at
  174°), rotation and scale, corner displacement 0, 1, 2, 3, 5, 10, 20 m, both signs; unlogged
  (`scratchpad/e5_pilot.py`). If the hypothesis holds, the same trial kinds go into
  `ops/trust_real_calibration.py` as logged rows and into the next freeze; if it fails, the
  failure is reported here and becomes the Q&A answer.
- **Drop rule for the deck.** No slide changes unless cell-level sensitivity is at least 90 % on
  the pilot; slides 2 and 4 are full, so at most one clause on slide 5 would change.

### E6. A tighter final fit (offline, from the frozen bundles' matches)

- **Hypothesis (the audit prompt's candidate).** A final fit on a tighter inlier set improves
  held-out error as well as in-sample error.
- **Method.** For the 6 SAC equatorial and the 20 74 °S OHRC → NAC windows, read `matches.csv`
  from the frozen bundles, make `evaluate()`'s own 80/20 split (seed 0), and fit on the 80 % with
  (A) MAGSAC++ at 3 px (today's pipeline), (B) MAGSAC++ at 1.5 px, (C) A then least squares on its
  inliers within 1.5 px, (D) A then least squares on all its inliers. Score each on the SAME
  held-out 20 %: median residual and RMSE within 3 px.
- **Adopt only if** a variant lowers the held-out median by more than 2 % on at least 5 of 6 SAC
  windows and at least 15 of 20 74 °S windows. In-sample RMSE falling by construction does not
  count. Otherwise dropped, and the SuperGlue comparison stays the Q&A answer it is.

### E7. The whole lit overlap of one OHRC frame with one NAC (dense tiling, with throughput)

- **Why.** "Full-scene tiled processing" is on slide 4 as a *strategy*; the evidence so far is
  hand-spread windows (8 + 6 per NAC). A reviewer asks what happens between them.
- **Method.** `ops.cut_site_pairs --nac M1153871873LE --windows 60 --tag full` cuts up to 60
  non-overlapping 640-px windows (spacing 1.1 × window) over all shared, lit, textured ground of
  the 74 °S OHRC frame and that NAC (Sun azimuths 3.3° apart); `ops.run_real_pairs
  "site_ohrc_m1153871873le_w*_full" --log` registers them. Reported as its own REPORT.md section,
  never merged into the 20-window table.
- **Hypothesis.** At least 80 % of the windows are accepted; every accepted window's held-out
  median is under 1.5 px on the 0.931 m grid; the rest are `unconfirmed` or `contradicted`
  (flagged), none silently wrong as judged by loop-free evidence (archive offset consistent with
  its neighbours within 50 m).
- **Rows.** One real_pairs_log row per window plus a throughput line (windows, total wall time).
- **Drop rule.** None for REPORT.md - the result is reported whatever it is. The deck gains a
  clause only if acceptance is at least 80 %.

### Results of the second pass

**E6 (tighter final fit): FAILED its pre-registered bar, and is NOT adopted.** Measured offline
from the frozen bundles' `matches.csv`, the same 80/20 split (seed 0) for every arm, every arm
scored on the same held-out 20 % (`scratchpad/e6_tighter_fit.py`):

| variant | SAC equatorial, better by >2 % | 74 °S, better by >2 % | median change in the held-out median |
|---|---|---|---|
| B: MAGSAC++ at 1.5 px instead of 3 px | 2/6 | 2/20 | −0.02 % / +0.00 % |
| **C: MAGSAC++ at 3 px, then least squares on its inliers within 1.5 px** | **5/6** | **13/20** | **−5.79 % / −2.28 %** |
| D: MAGSAC++ at 3 px, then least squares on all its inliers | 3/6 | 7/20 | −1.64 % / −0.56 % |

The pre-registered rule was "at least 5 of 6 SAC windows **and** at least 15 of 20 74 °S
windows". Variant C clears the first and misses the second (13 of 20). Rule 7 forbids moving a
bar after seeing the result, so **the pipeline is unchanged** and no number on the deck moves.

Why this is worth recording rather than deleting. Variant C would have cut the IN-SAMPLE per-axis
RMSE - the measure arXiv:2509.04775 reports for SuperGlue - on SAC's equatorial pair from
X 0.66-1.15 / Y 0.73-1.14 px to **X 0.46-0.60 / Y 0.54-0.73 px** (`scratchpad/e6_peraxis.py`;
that script re-derives variant A too, and its A differs from the logged in-sample values by up to
0.07 px because it re-thresholds the inliers instead of using MAGSAC's own mask - REPORT.md's
values are the authority). Against the paper's 0.62 / 0.57 px that is a smaller number **in
pixels**, and a team chasing the headline could have written "better than SuperGlue". In metres
it is not: 0.75-0.98 m against their 0.69 m on X, so C beats SuperGlue on **0 of 6** windows on
each axis once both are put on the ground. Comparing pixels across a 1.622 m grid and a 1.1179 m
grid is exactly the trap Invariant 2 exists to stop, and the held-out bar was pre-registered
precisely so that the in-sample number could not decide this. Dropped.

**E5 (non-translation errors): PASSED its pre-registered bar, and is now logged evidence.** The
pilot (`scratchpad/e5_pilot.py`, 6 windows, 156 planted trials, unlogged) rotated and rescaled
the true transform about the frame centre, sized by how far the CORNERS move:

| population | cells displaced >2 px that the map refused to verify | cells displaced <1 px that stayed verified |
|---|---|---|
| Suns under 10° apart (4 windows) | 2802/3008 = **93.2 %** | 1739/1756 = **99.0 %** |
| Suns 174° apart, SAC's pair (2 windows) | 1011/1056 = **95.7 %** | 1027/1108 = **92.7 %** |

That clears the pre-registered 90 % sensitivity and 80 % specificity. The frame verdict behaved
exactly as predicted and is the wrong thing to watch: it stays `agrees` at 1-3 m of corner
displacement while the mean verified count falls 58.5 → 47, becomes `unconfirmed` around 5 m, and
only reaches `contradicted` at 10 m (8 px). The information is in the map, not the verdict. The
geometry behind that: an 8 × 8 cell is 80 px wide, so the per-cell displacement spans exactly
5.8× from the middle of the frame to its corners at every size of error.

So `ops/trust_real_calibration.py` now plants three KINDS - translation, rotation, scale - and
every trial row carries what the map did cell by cell; the freeze re-runs it and REPORT.md gains
"Errors that are not translations". Translations are drawn from the RNG first and in the order
they always were, so that population's trials do not shift because a kind was added after them.
`evaluation/test_trust_planted_errors.py` (20 tests) pins the transforms: that a translation
moves every point equally, that a rotation and a scale change hold the centre and move the
corners by exactly the stated amount, that the two rotation signs cancel to exactly `dpx² / R`
and no more, and that an unknown kind is refused rather than silently planted.

**E7 (the whole lit overlap, dense tiling): run.** `ops.cut_site_pairs --nac M1153871873LE
--windows 60 --tag full` found **37** non-overlapping 640-px windows (centres at least 1.1 × the
window apart; lit fraction 0.90-1.00) spanning −74.25 to −73.64 °S and 43.47 to 43.85 °E - the
whole shared lit ground of the 74 °S OHRC frame and that NAC, 13.1 km². Results below. It gets
its own REPORT.md section and is never merged into the 20-window table the deck quotes.

**E7 result: the acceptance bar passed, the residual bar failed on one window, and the failure was
worth more than the pass.** All **37 of 37** windows were accepted (`agrees`, matcher declared) -
the pre-registered bar was 80 %. Registration took 3.8 min of wall time in total, a median of
7.3 s per 640-px window.

The pre-registered hypothesis also promised "every accepted window's held-out median is under
1.5 px". **One window breaks it**: `site_ohrc_m1153871873le_w15_full`, held-out median
**316.06 px**. Reported rather than trimmed, and then chased down, because an accepted window
with a 316 px residual is either a missed failure or a broken metric, and both matter.

It is a broken metric, and the evidence is independent of the matcher. Correlating each window's
exported `registered_product.tif` - the source warped under the transform the system declared -
against its reference over the finite overlap (`scratchpad/e7_independent_check.py`, the same
|NCC| ≥ 0.30 rule the sun sweep uses) gives **+0.87 to +0.95 on all 37 windows**, w15 included at
**+0.934**. The declared alignment is right everywhere. Under that declared transform the median
error over ALL of w15's matches is **1.079 px**; `evaluate()`'s own fit on the other 80 % lands
on the same transform (they differ by **0.0 px** at the frame centre). What differs is the sample:
w15 has 718 matches and 389 inliers, an inlier ratio of **0.542**, so a random 20 % held-out draw
can be majority-outlier, and the MEDIAN of a majority-outlier sample describes the outliers.

**This is a real limit of the number slide 4 quotes, and it is now written down.**
`residual_median_px` is robust only while the inlier ratio is comfortably above 0.5; at 0.542 it
jumped by two orders of magnitude on a correctly registered window. The 20 windows the deck
quotes have inlier ratios **0.614 to 0.998** and held-out medians 0.41-1.01 px, so the quoted
range is unaffected - but the floor is now known rather than assumed, and it is a sharper version
of Known issue 1 (which only warned about `residual_px`). It also happens to be a clean
demonstration of the project's own thesis: the independent area check accepted a window that the
match-derived residual metric misjudged, because the area check never looks at the matches.

The "archive offset within 50 m of the nearest accepted neighbour" sub-criterion also fails -
offsets run 2.7 to 495 m across the frame - but that measures the ARCHIVE's correction field
varying over 13 km², not our registration, and the NCC evidence is the better test. Recorded as
a badly chosen criterion on my part, not as a result.

### E8. DEM relighting of the reference for the 60-120° band: assessed, not run

The idea needs a DEM at about the reference's resolution under the source's Sun. On disk: LOLA
`ldem_60s_60m` (60 m) at 74 °S and the TMC-2 DTM at SAC's site (tens of metres). Both are 50-240×
coarser than the 0.25-1.6 m images; a relit 60 m surface shares no matchable texture with a 1 m
NAC window (the LOLA rung at 240× already finds 0 matches). NAC DTMs (2-5 m) exist for a few
sites, none of ours. Verdict: not feasible on the data we hold before 24 Sep; it stays on slide 4
as a strategy ("LOLA orthorectification") and as a finale item. No number, no claim.

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

## Phase D, second pass: the re-freeze at `183a54f`

Three commits carry the second pass, in this order and each with its tests green before the next:
`34e3c97` (the pre-registration, docs only), `7a71a9f` (E5's trial kinds, the reporting
additions, the demo and provenance fixes), `183a54f` (the F12 deliverable bug). The freeze then
ran on `183a54f` with a clean tree.

**The re-run reproduced every per-pair number exactly.** Comparing each pair's new row against
its `b678272`/`7a71a9f` row on matches, inliers, held-out median, verified cells, verdict and
archive offset: identical on every one of the 177 registered pairs, and the sun sweep's 69
windows return the same outcome distribution over the same 25 NAC frames. The multi-modal check
returns the same three numbers to four decimals.

**The single exception is loop closure, and it is the exception the F12 fix predicts.** The loops
are the only metric read back from the exported match table, so correcting which rows are flagged
moves them - by about 2 %, in both directions (table in the F12 section). Finding that the one
number to move is exactly the one that reads the repaired file is the strongest evidence that the
repair did what it claims and nothing else.

### The freeze had to be run twice, and the reason is worth recording

The first attempt (`183a54f`) completed registration, the sun sweep, the loops and the multi-modal
check, then **crashed 45 minutes into the trust step - in a format string**. The per-cell clause
of a summary row's note guarded both its halves with a single `or`:

```python
(f"... refused to verify {mnv} ({100 * mnv / nm:.1f} %); of the {ns} cells ..." if nm or ns else "")
```

so any row where no cell moved past 2 px but many stayed under 1 px divided by `nm = 0`. That is
**7 of the 24 summary rows, including the very first one written**, so every trial had been
computed and the CSV written before it failed. The freeze then retried the step, and the retry
deleted the per-trial CSV that the completed work had produced (`freeze.trust` unlinks it first -
Known issue 7, which exists because the script appends). Forty-five minutes for a `%` sign.

Fixed in `7dd4e5b`: the two clauses are independent, so each guards its own count, and six tests
walk the whole `(kind, displacement)` grid the run can produce. Two further things were done
rather than just the minimum:

- **The same fail-fast rule the rest of the project follows was applied here.**
  `core.pipeline.main()` decides every refusal it can from the arguments "before a single second
  of matching"; the trust run, which is an hour of work, did not. It now calls `_log_preflight()`
  up front, so an unwritable log is refused in a second rather than after the hour.
- **Before restarting a 100-minute job, every remaining step was rehearsed against a realistic
  three-kind calibration file** built by the real `plant`/`cell_effect` code. That found a SECOND
  latent crash: `fig_trust_real` calls `_distinct_windows`, which opens a file per pair, and
  `data/pairs` is gitignored - so on a machine holding the logs but not the imagery the figure,
  and with it the freeze's report step, would die over a caption. Guarded the same way
  `ops.make_report._distinct_note` already guards the identical call.

The lesson is the same one F17 taught in a different form: the expensive part of this project is
not computation, it is discovering at the end that the cheap part was wrong. Both fixes are
reporting-only - no logged number changes - but the freeze was re-run in full anyway rather than
splicing a second commit's rows into the first's, because "every number from one commit" is the
whole point of having a freeze.

**The second attempt's trust step failed too, and that one was operator error with a real design
flaw behind it.** `ops.freeze`'s `trust` step takes its window list from
`evaluation/trust_real_calibration.csv` - the file it then deletes and rewrites. Cleaning up
after the smoke test that verified the crash fix, I removed that CSV, and a `git add -A` then
committed its deletion. The step had no window list, printed one line to the console (not to its
log, which is why `trust.log` was zero bytes), and returned "precondition failed" in seconds. The
file was recovered from commit `183a54f` (2,220 trials, 30 windows) and the step re-run on its
own with `--only trust`, then `--only report` to regenerate everything downstream of it.

**F19 · LOW · `ops.freeze`'s own summary line crashes when a step returns the "precondition
failed" sentinel.** `sum(results.values())` at `freeze.py:429` adds `None` to an int, so the run
ends in a `TypeError` after every step has finished and been recorded. Cosmetic - the state file
and all the evidence are intact, and `--check` reads the state, not the summary - but it turns a
clean "9/10 steps ok" report into a traceback, which is exactly the wrong signal at the end of a
two-hour job. Not fixed now (an `ops/` change would force a third freeze); in Known issues.

**F18 · MEDIUM · the trust step's input is the file it deletes.** If that CSV is ever lost the
step cannot run at all, and the freeze reports a failure whose cause appears nowhere in its logs.
The window list should live in the freeze state or in a pinned list in the script, not in the
output of the previous run. Not changed now - it is an `ops/` change and would force a third
freeze - but it is written into Known issues and is the first thing to fix after submission.

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

## Deck v4 (20 Sep, 12:30): refilled from the `7dd4e5b` freeze

The second pass forced a second re-freeze, so every number on the deck was re-derived from the CSV
cells a third time (`rederive2.py`, which reads only the evidence files, never REPORT.md, so it
also checks the report's rendering). **Six values moved and two clauses were earned.** Everything
else re-derived identical, which is the result that matters: a re-freeze that changed numbers it
had no reason to change would mean the freeze is not deterministic.

| Slide | v3 (`b678272`) | v4 (`7dd4e5b`) | Why it moved |
|---|---|---|---|
| 4, first bullet | 136 real window pairs | **160** | E7's dense tiling and E2/E5's extra windows are real, registered, logged rows. REPORT's footer prints "177 registered pairs (160 distinct ground windows)" |
| 4, sub-pixel bullet | six loops close to 0.08 px (0.10 m) | **0.086 px (0.107 m)** | The F12 fix. `loop_closure._inlier_src_points` reads `is_inlier` from `matches.csv`, so repairing that flag moved the loops ~2 %. Now printed to three figures so it matches REPORT exactly instead of being a truncation |
| 3, hardware bullet | median 10.7 s | **8.2 s** | Wall time, re-measured. It has been 10.0, 10.7 and 8.2 s over three freezes on the same machine |
| 2 and 5, trust | 1/352 at 1-2 m | **0/352** | A fresh draw of the planted directions (Known issue 7). Two draws now: 1/352 and 0/352 |
| 2 and 5, hard Sun | 94 % at 5 m | **84 %** (54/64) | The same fresh draw. 5 m is 3.1 px on these grids - the transition point for this population, so it is the number that moves |
| 4, residual bullet | 0.41-1.01 px on 20 hand-picked windows | **the 37-window tiled result: 37/37, median 0.61 px = 0.57 m** | Replaced, not added - see below |

**Two clauses were earned against bars written down before the runs, and both bars were met.**

- Slide 4 gains the dense tiling (E7): every non-overlapping 640-px window the cutter finds in
  shared, lit, textured ground of the 74 °S overlap - 37 of them, 13.1 km² - accepted 37/37.
  Pre-registered bar: acceptance ≥ 80 %.
- Slide 5 gains the non-translation trust result (E5): of the 20,896 cells a planted rotation or
  scale moved by more than 2 px, the map refused to verify 94.1 %. Pre-registered bar: 90 %. The
  companion number, 87.4 % of cells moved less than 1 px staying verified (bar 80 %), is in
  DECK_V2_DRAFT.md for Q&A - without it, "94 % refused" could just mean the map refuses everything.

**The one deliberate removal.** Slide 4's held-out residual was the range over 20 hand-picked
windows at 74 °S (0.41-1.01 px). The tiled result covers the same site with every window the
cutter finds, chosen on texture and illumination before any matching, so it answers "did you pick
the windows that worked?" - which the hand-picked range invites and cannot answer. It is also
slightly worse (median 0.61 px against a 0.41-1.01 range), and that is the point of quoting it.
The old range stays in REPORT.md and in DECK_V2_DRAFT.md's Q&A for the judge who asks.

**The tiling clause says "36 of 37 under 3 px" on the slide.** One window
(`site_ohrc_m1153871873le_w15_full`) reports a held-out median of 316 px at an inlier ratio of
0.542. That is the metric degrading, not the alignment: the held-out median is only robust while
the inlier ratio is well above 0.5, and the NCC of the aligned window is +0.87 to +0.95 on all 37.
Leaving "37/37 accepted" on the slide without that clause would let a reader infer 37 sub-pixel
windows, which is not what was measured.

Build: `AUDIT: clean`; `export_pdf`: `PDF CHECK: clean`, 6 pages, 1,112,703 bytes. Words per slide:
s2=272, s3=136, s4=266, s5=199, s6=150. All six pages rendered at 150 dpi and read.

**Slides 2 and 4 overflowed the footer twice during the refill**, caught by `export_pdf`'s check,
not by `build_deck`'s audit (Known issue 11 - the build audit measures text boxes, not rendered
text). The first overflow was mine: I put the rotation/scale clause on slide 2, where it did not
fit and did not belong; it went to slide 5, which had room. The second needed slide 4 measured
directly (0.259 in past the footer top, ~1.2 lines) before it was clear that trimming words could
not fix it and one bullet had to go.

## claim-checker on deck v4 (20 Sep 12:50; read-only agent, every finding verified first-hand)

**0 fabricated numbers, and all six changed v4 values confirmed correct** against REPORT.md.
Findings: 2 HIGH, 8 MEDIUM, 4 LOW - every one on a noun, a scope or a label rather than a digit.
Each was checked against REPORT.md by hand before anything was changed; two are worth recording
because they are the kind of error a SAC scientist catches and a spell-check does not.

**H1 - the deck used the wrong noun for a right number.** Slide 4 said "160 real window pairs".
REPORT.md's footer prints *"177 registered pairs (160 distinct ground windows)"* - two different
counts of two different things. The v4 refill had correctly moved 136 → 160 and kept the v3 noun,
so the deck would have told a judge there were 160 pairs while the log they were pointed at says
177. Now "160 distinct ground windows", which is REPORT's own wording.

**H2 - a true number with a false sentence around it.** Slide 5 said planted rotation and scale
"behave the same way" as planted translation, then gave the 94 % cell figure. The 94 % is right.
"The same way" is not: at 5 m the *frame* verdict is contradicted on 100 % of translation trials
but only 10 % (rotation) and 15 % (scale). REPORT.md says exactly this in the paragraph above its
own table - *"The frame verdict is the wrong thing to watch here … because the error is not
uniform over the frame"* - and the slide was quietly contradicting it. The clause now reads
"caught cell by cell, not by the frame verdict", which is both true and the more interesting
claim: the trust map sees a rotation the frame verdict misses.

The rest were applied as written: the tiling clause names its scope (one OHRC frame with one NAC)
and the texture screen (M1); MiLOI S1 gains its metres (M2); the loops are labelled "a median …
- consistency, not ground truth" so they cannot read as accuracy after the preceding "vs exact
truth" (M3, L3); MiLOI's 90° is named a **Sun-vector** angle, since every other Sun figure on the
deck is an azimuth (M4); slide 2's second `0/N` is named as the floor, because a sentence with a
strength and a weakness both written `0/N` is a misread waiting to happen in the flattering
direction (M5); the portal text gains the 36-of-37 caveat, names Sun azimuth on both populations
and gives the loops' grid (M6, M7, L4); `build_deck.py`'s docstring and this file name v4 and
`7dd4e5b` instead of v3 and `b678272` (M8); fore/aft is 15.5 m, not 16 m - 2.617 px × 5.929 m =
15.51, and the slide's own two figures never reconciled to 16 (L1).

**One finding was declined, and the reason matters more than the finding.** L2 asked for "11/11
refused" in place of "10/11 refused, none registers" on the IIRS bullet, since all 11 windows are
non-accepted. But *refused* is a defined state here - the pipeline declared a fallback - and that
is true of exactly 10; the 11th is `unconfirmed`, which is kept and not certified. "None
registers" already covers all 11. Taking the suggestion would have made the sentence easier to
read and less true, which is the trade this audit exists to refuse.

**It also caught something neither the freeze nor the build audit can see:** at the time it ran,
the REPORT.md every v4 number was read from was **uncommitted**. `git show 7dd4e5b:REPORT.md` is
an older render with no dense-tiling section at all, so a judge pointed at the freeze commit would
not have found the numbers on the slides. The render is now committed (below). This is a real gap
in the freeze discipline: `ops.freeze --check` verifies that the evidence rows name one commit,
but nothing verified that the REPORT.md rendering those rows had been committed anywhere.

Slides 2, 4 and 5 were rebuilt and re-exported after the fixes: `AUDIT: clean`, `PDF CHECK: clean`,
and all three changed pages rendered and read again. Slide 4 needed one line back to fit H1/M1-M4,
and it came from the first bullet's tail ("public data, open-source libraries; one command re-runs
every number from a clean commit"), which slide 3 already says twice - in Technologies and in the
last Methodology bullet. No evidence was dropped to make room.

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

## Every high-ceiling candidate the prompt listed, and what became of it

| Candidate (AUDIT_PROMPT §4) | Outcome |
|---|---|
| A logged accuracy figure for the multi-modal fallback | **Done** (E1): 0.23-1.09 px = 3.4-16.2 m from the visible-band registration of the same window, logged and on slide 2 |
| A defensible sub-pixel claim with its grid named | **Done** (E3): four figures on slide 4, each naming its grid and its metres and saying what its truth is |
| Better TMC-2 data (a closer Sun) | **Blocked on a download only Samartha can do** (E4, Rule 10): the pass is identified from the PRADAN footprints, the cut command is written and tested, the Q&A answer is written for if it does not land |
| DEM-based relighting of the reference for the 60-120° band | **Assessed and not attempted** (E8): every DEM we hold is 50-240× coarser than the images; a relit 60 m surface shares no matchable texture with a 1 m NAC window, which the existing 240× LOLA rung already demonstrates by finding 0 matches |
| A tighter final fit, if it improves held-out as well as in-sample | **Tried and dropped** (E6): missed its pre-registered held-out bar (13 of 20, needed 15). Recorded with the number it would have produced, because that number would have looked like beating SuperGlue |
| A full OHRC strip or large-area run, with runtime on this CPU | **Done** (E7): one whole overlap tiled end to end, 37 windows, 13 km², all accepted, with wall time |
| Runtime and throughput figures | **Done** (E3, E7): a median per-window time on slide 3 and a total for the tiled run |
| A trust test on hard-Sun windows and non-translation errors | **Done** (E2 hard Sun, E5 rotation and scale), both logged and frozen |

All eight are closed except the one that needs a login. Nothing on this list was dropped for
being inconvenient; the two that produced nothing (E6, E8) say so with their reasons.

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
| F11 | LOW | The runaway `precompute_demo_cache` (no arguments caches every pair) | 75 stray caches deleted; the 6 demo caches are regenerated at the final freeze commit |
| F12 | **BLOCKER** | `is_inlier` in the exported match table was an exact float comparison between float64 matches and their float32 copies, so 41 of 183 bundles shipped empty `gcps.txt`, `gcps.points` and `matches_isis.csv` - deliverables the PS names and slide 3 claims | **Fixed** in `183a54f`: MAGSAC++'s own mask is carried through and used; 5 tests; all bundles rewritten by the re-freeze. No logged number changes |
| F13 | HIGH | A stale demo cache was undetectable: the plate printed the cache's commit with nothing comparing it to the running code | **Fixed**: the plate says `commit <a> — CODE IS NOW <b>` in the caution colour; driven both ways through AppTest |
| F14 | HIGH | `weights/`, `demo_cache/` and `data/pairs/` are gitignored inside OneDrive, which has reverted this repo's files before, with no backup | **Done**: copied to `C:\sih26166_backup\` and hash-verified; the USB step and the `demo_cache` copy are step 0 of `day_24.md` |
| F15 | MEDIUM | A report exported from a cached result named only the commit that wrote the file, contradicting the commit the screen showed for the same numbers | **Fixed**: both commits are named when they differ (`core/test_export_provenance.py`) |
| F16 | MEDIUM | `discover_pairs()` re-stats every pair directory on every Streamlit rerun; E7 took that from 160 to 197 directories | **Fixed**: `@st.cache_data`, matching its two neighbours |
| F17 | MEDIUM | My own Phase A check for missing GCP files used `inliers_exported` as its predicate - the very field the bug zeroed - so it reported "0 missing" over exactly the broken bundles | **Recorded**, and the replacement check counts bundles whose RANSAC inlier count and exported inlier count disagree |

**Numbers that moved, before → after** (all others reproduced exactly):
3 m detection 81 % → 74 % (F7); 1-2 m contradictions 2/352 → 1/352 (same cause); mean verified
cells at 3 m 7.3 → 10.9; runtime median 10.0 → 10.7 s (wall time). New: 0.23-1.09 px multi-modal;
the 8-window hard-Sun table; the sub-pixel table.

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
## What the second pass changed about the audit's own verdict

The first pass concluded that the deck was "at its honest ceiling for the evidence on disk". That
was wrong in one specific way, and finding out how is the most useful thing the second pass did.
Two of its four experiments were designed to raise the ceiling (E6, E7) and one to close a
disclosed weakness (E5); none of those is what mattered most. **What mattered was that chasing a
six-file bundle instead of an eight-file one uncovered a defect in a named deliverable that every
metric in the project was blind to** (F12), and that my own Phase A check for that exact defect
had been written so that it could not fail (F17).

The lesson worth carrying into the finale: a check built on a number the suspected bug produces
is not a check. Both replacements compare two numbers with independent provenance -
`ransac.inlier_count` against `inliers_exported` and the actual data rows in the ISIS file, and
the declared warp against the reference by NCC rather than by its own matches.

## Remaining risks, ranked

1. **TMC-2**: the title names it and the deck shows a refusal. Only the download closes it.
2. **In-sample RMSE vs SuperGlue** is not better (Q&A only; a reviewer who knows the paper will
   ask).
3. **S3 truth** unvalidated for 56 of 81 MiLOI pairs (disclosed on the slide; the 7.4 px
   separation is the defence).
4. **The 3 m point** is a coin-flip region; say so rather than defend 74 %.
5. **Slide density**: slides 2, 4 and 5 are at 11.5 / 12 pt and at capacity; a cold reader gets a
   lot per slide. The structure (pointer headings, one figure each) carries it, but the v4 refill
   could only add the tiling clause to slide 4 by removing a bullet. Only slide 6 has room left.
6. **Demo**: three AppTest runs pass on the cached pairs [see below]; a live align on a busy
   laptop still takes 48-61 s (Known issue 12).

## Verdict

Against the visible field (B7), no public SIH26166 repo shows real cross-sensor registration on
SAC's own benchmark pairs, thousands of inliers per window, a calibrated failure detector, loop
closure, or a measured multi-modal result; ours now shows all five with the grid named beside
every sub-pixel figure, plus a failure detector calibrated against rotation and scale as well as
translation, and a whole overlap tiled rather than a handful of chosen windows. What would still
beat us: a team that registers OHRC ↔ TMC-2 on a closer-Sun pass with a working number (we show a
refusal), a team whose in-sample RMSE beats SuperGlue on SAC's pair, or a team with a live demo
link and video where we have neither. The deck is at its honest ceiling for the evidence on disk;
the one measurable step left is E4, and it is a 20-minute download away.

**Is v4 better than `submission-v1`?** Yes, and the comparison is not close. `submission-v1` was
built before the audit: its deliverables were silently empty on 41 of 183 bundles, its multi-modal
claim was unmeasured, its sub-pixel figures did not name their grids, its trust layer had been
calibrated only against translation, and its headline residual came from twenty windows chosen by
hand. Every one of those is now either fixed or measured, and the two numbers that moved against
us - the hard-Sun rate from 94 % to 84 %, and the tiled median being worse than the hand-picked
range - are on the deck in that form. Nothing in v4 is half-finished: the freeze says FROZEN, the
suite is 340 green, the build and PDF checks are clean, and all six pages have been read.

