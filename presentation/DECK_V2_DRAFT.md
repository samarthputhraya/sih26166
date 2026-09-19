# SIH26166 national deck, v2: the numbers audit (19 Sep 2026)

> The slide text lives in `presentation/build_deck.py` (S2-S6) and nowhere else. This file is
> the audit table for it: every number on a slide, the value it holds, and the REPORT.md section
> it was copied from.
>
> **FILLED 20 Sep 2026 from the evidence freeze at `49bdad9`** (`python -m ops.freeze --check`:
> FROZEN; 146/146 real-pair rows and 324/324 MiLOI rows at that commit; evidence commit
> `36de5f4`). A new freeze means re-reading every row of this table. The only open placeholder
> is the Team ID (slide 1), which comes from the portal, not from the evidence.
> `python -m presentation.build_deck` exits 1 while it is open;
> `python -m presentation.export_pdf` refuses to pass a PDF with it.
>
> Audience: SAC-ISRO image-processing scientists reading the PDF cold, ranking it against every
> other SIH26166 idea. Output: `presentation/SIH26166_LunaXX_deck.pptx`. The college-round deck
> (`SIH26166_deck.pptx`) is left as it was.
>
> Revised 20 Sep after `claim-checker` on the filled deck (3214e8a: 0 numeric mismatches; 3 HIGH,
> 7 MEDIUM, 12 LOW on scope and labels). Fixed: the held-out residual now says it is the 74 °S
> site with Suns 3–6° apart and puts SAC's equatorial pair beside it; OHRC → TMC-2 gives azimuth
> AND incidence difference; fig5's legend says "accepted", not "verified"; MiLOI's scene S3 is
> named on both slides; the planted-error scope (22 windows, Sun azimuths under 10° apart) and
> the 1–2 m behaviour are stated; the NAC corner offset is a disagreement, removed by a wide
> search before matching; loops are "consistency, not ground accuracy"; the visible side of the
> multi-modal pairs is named (Kaguya TC); "never uses match positions"; fig4 shows the
> unconfirmed branch; "traces to", not "copied from"; fore/aft quotes the one accepted window.
> Slides 2 and 4 then overflowed the footer in the PowerPoint render and were tightened;
> `presentation/export_pdf.py` now fails on any text in the footer band.
>
> Revised 19 Sep after `claim-checker` (19 findings). Fixed in the text: the "nothing registers
> past 90°" claim (the sweep accepts near-opposite Suns), "one log / nothing typed", the fore/aft
> statistic, "independent truth", the false-alarm label, the shadow claim, the safety absolute,
> grid naming, the LOLA scale overclaim, "verified" for accepted windows, the "62 m" figure, the
> infrared fallback count, the pipeline order (slide 2 and fig4), ISIS, the archive
> generalisation, and the slide 6 references. Also fixed: REPORT.md's footer count (a variable
> clobbered by the MiLOI section).

## Terminology (Invariant 2), as the slides use it

| Pair | Say | Never say |
|---|---|---|
| OHRC ↔ LRO NAC (74 S site; SAC's two pairs) | cross-sensor, cross-mission | multi-modal |
| OHRC ↔ Kaguya TC | cross-sensor, cross-mission | multi-modal |
| OHRC ↔ TMC-2 | cross-sensor, same mission | cross-mission, multi-modal |
| TMC-2 fore ↔ aft | same sensor, viewpoint | cross-sensor |
| MiLOI (NAC ↔ NAC), the sweep's NAC legs | same sensor, Sun-angle test | cross-sensor |
| TC ↔ MI 1548 nm, TC ↔ IIRS 999/1555 nm | multi-modal (visible ↔ infrared) | — |
| OHRC ↔ LOLA shaded relief | multi-modal (optical ↔ elevation), declared failure | registered |

- Sub-pixel always names its grid and gives metres.
- A window is **accepted** when its verdict is `agrees`. **Verified** is a cell state, not a
  window verdict.
- Sweep and SAC Sun differences are **azimuth** differences. MiLOI bins are the **angle between
  the Sun vectors**. Label each one as what it is.

## Slide 1 (title page)

| Field | Value | Source |
|---|---|---|
| Team ID | `[TBD - portal Team ID]` | the SIH portal (STATUS, open question 1) |
| Team Name | LunaXX | portal, 18 Sep nomination |

## Slide 2 (idea title)

| Text on the slide | Value at 49bdad9 | Source (REPORT.md section → column) |
|---|---|---|
| Sun azimuths … apart, … accepted (SAC equatorial) | 174° (173.5–173.7); 6/6 | "SAC's own benchmark pair (equatorial …)" → Δsun az; `agrees` / rows |
| polar …°, …, the other two flagged | 132° (132.2–132.3); 4/6; w05 unconfirmed, w06 contradicted + fallback | "SAC's own benchmark pair (polar …)" → Δsun az; verdicts |
| … NAC frames, azimuths …–…° apart | 25; 3–153 (3.3–152.7) | "Real sun-angle sweep" → the "All bins" line |
| TC …×, … accepted | 29.6×; 3/4 (w04 unconfirmed) | "Scale rung: … TC ortho map" → scale; `agrees` / rows |
| Kaguya TC (visible) to MI 1548 nm and Chandrayaan-2 IIRS: … of … refused and fall back, the other stays unconfirmed | 13 of 14 (MI 1548 nm 3/3, IIRS 10/11; IIRS 1555 w10 unconfirmed) | "Kaguya TC → Kaguya MI" 1548 nm rows + "… IIRS" rows → declared / verdict |
| MiLOI, … pairs (… in scene S3); agrees within 3 px; contradicted wrong; unconfirmed wrong | 81 (56 in S3); 33/33; 43/43; 5/5 | "MiLOI" → the verdict table, column **matcher H within 3 px** (what the trust layer judges). `rmse_gt_px` for agrees is 28/33: have both ready for Q&A |
| … real windows (Sun azimuths under …° apart): …/44 false alarms; flagged …% at 3 m, …% from 5 m, …/352 at 1–2 m | 22 (3.3, 5.8, 9.1°); 0/44; 81% (143/176 = 81.2 %); 100% (176/176 at each of 5–200 m); 2/352 (1 m 0/176; 2 m 2/176 contradicted, 58 unconfirmed, 116 agrees) | "Trust layer on real imagery: planted …" → the 0, 1, 2, 3 and ≥ 5 m rows |

## Slide 4 (feasibility)

| Text on the slide | Value at 49bdad9 | Source |
|---|---|---|
| … real window pairs | 136 | REPORT.md footer: 140 registered pairs, minus 4 duplicate windows of Known issue 2 (`presentation.make_figures._distinct_windows`: `w01`=`w01_sw`, `w02`=`w02_sw`, `w03`=`w03_sw`, `w01_t`=`w04` of M1153871873LE) |
| … instrument pairings | 8 | REPORT.md pair sections: OHRC-NAC, NAC-NAC, OHRC-TMC2, TMC2-TMC2, TC-MI, TC-IIRS, OHRC-TC, OHRC-LOLA. (Some pre-18-Sep rows' `kind` said `nac-nac` for TC→MI; the latest rows say `tc-mi`, and REPORT.md derives the kind from the product ids anyway.) |
| Six three-image loops close to a median … m | 0.10 (median 0.104, max 0.128, 6 loops) | "Loop closure" → loop RMS median |
| OHRC → NAC residual: 74 °S, Sun azimuths …° apart, median … px, … m | 3–6° (3.3, 5.8); 0.41–1.0 px (0.410–1.005); 0.51–0.94 m; 20/20 agree | "Chandrayaan-2 OHRC → LRO NAC" → Δsun az range, held-out median range, the (m) values. Two NAC grids (0.931 and 1.245 m) |
| … on SAC's equatorial pair, 174° apart, 1.62 m grid | 0.69–1.7 px (0.690–1.676); 1.1–2.7 m (1.120–2.718) | "SAC's own benchmark pair (equatorial …)" → held-out median column and its (m) |
| MiLOI past 90°: any of the … pairs (all scene S3) | 16 (9 + 7 pairs, every method 0; all S3 in miloi_log) | "MiLOI" table → rows 90-120 and 120-181 |
| sweep: … of … at 60-120°, … of … at 120-153° | 0 of 12 (7 + 5); 10 of 15 | "Real sun-angle sweep" → bins 60-90 + 90-120, and 120-180 (registered & accepted / windows) |
| OHRC → TMC-2 at SAC's site (azimuths …°, incidence …° apart): all 4 refused | 120° (120.2); 59° (d_incidence −59.44); 4/4 contradicted + fallback | "SAC's benchmark site: OHRC → TMC-2 nadir" → Δsun az; verdict; declared |
| NAC's published corners and the OHRC grid disagree by … km | 1.9 km (+488, +1790 m → 1.86 km); applied before cutting by `cut_pradan_pairs.wide_offset` | "SAC's own benchmark pair (equatorial …)" note → wide-search offset (`site_geometry/M1350459544RE.json`) |
| fore/aft accepts … window of 4, held-out median … px (… m) | 1 (w04 agrees; w02, w03 unconfirmed; w01 contradicted + fallback); 2.6 px (2.617) × 5.929 m = 16 m (15.5) | "Real viewpoint: TMC-2 fore → aft" → **held-out median** column, not "RMSE ≤ 3 px" (capped at 3 px by definition) |

## Slide 5 (impact)

| Text on the slide | Value at 49bdad9 | Source |
|---|---|---|
| LRO NAC (… frames at … sites) and Kaguya TC (… site) | 3 at 3; TC 1 site (74 °S) | distinct `ch2_ohr_*` source products in the latest real_pairs_log rows: `…20200229T0739312111` (74 °S; NAC + TC + LOLA), `…20200824T0806596861` (62 °S, SAC polar; NAC), `…20210401T2357376656` (14 °S, SAC equatorial; NAC + TMC-2) |

## Figures

| Slide | Figure | Built from |
|---|---|---|
| 2 | `fig3_trust_map.jpg` | real pairs since 19 Sep: `sac_ohrc_nac_w06` (SAC's pair, accepted) above `site_tc_morning_mi1548_w01` (1548 nm, refused), from `demo_cache/results/` - `ops.freeze` re-caches both before drawing; counts match their real_pairs_log rows |
| 3 | `fig4_pipeline.png` | `core/pipeline.py` order (refinement before MAGSAC++, fixed 19 Sep) |
| 4 | `fig5_real_sun_sweep.png` | `real_pairs_log.csv` outcome rows (rule v2) |
| 5 | `fig6_trust_real_calibration.png` | `trust_real_calibration.csv`, re-run at the freeze (file deleted first; the duplicate window `w01_t` = `w04` dropped, so 22 windows). Axis names both grids (0.93 and 1.25 m) |
| backup | `fig7_miloi_sun.png` | `miloi_log.csv` |

## Q&A traps this deck invites (answers must come from REPORT.md)

- **"SuperGlue got 0.62/0.57 px on our pair."** Their figure is an in-sample control-point RMSE
  per axis, on their resampled NAC grid (1.1179 m). Our headline is held out (matches the fit
  never saw), on the NAC's own grid in our cut (1.62 m). It differs in measure and in grid; say
  both before comparing anything. Since 19 Sep the SAME measure is logged for ours too
  (`insample_rmse_x_px` / `_y_px` in real_pairs_log; REPORT.md's "In-sample, per axis (SAC's
  measure)" table under each SAC section). Quote it in px AND metres, with the inlier count
  graded: ours grades thousands of MAGSAC++ inliers up to 3 px, not a handful of control points,
  so it is not smaller by construction. Compare in metres (their px × 1.1179 m).
  **At 49bdad9 ours is NOT better on this measure**: equatorial X 0.66–1.15 px, Y 0.73–1.07 px
  on the 1.622 m grid (1.06–1.86 m, 1.18–1.74 m) against SuperGlue's 0.62 / 0.57 px on 1.1179 m
  (0.69 / 0.64 m). Do not raise it. If asked: theirs grades a set of control points, ours grades
  every one of 3,219–4,182 inliers per window up to 3 px; the claim we make is not a smaller
  in-sample RMSE but held-out residual, coverage, loop closure and a verdict that says when to
  distrust the result - and on their polar pair, which they report only SuperGlue registered,
  ours accepts 4 of 6 windows and flags the other two.
- **"Your MiLOI truth uses your own matcher."** It does, on OTHER pairs: a translation network
  from ours+SIFT agreement, leave-one-out. S3's network has no redundancy, so its error is
  unmeasured. 56 of the 81 scored pairs are S3.
- **"'Unconfirmed' pairs were wrong. Did you ship them?"** Yes: the matcher's transform is kept,
  labelled unconfirmed and not certified (the log calls them `missed_failure`).
- **"Is OHRC ↔ NAC multi-modal?"** No. Both are panchromatic. It is cross-sensor and
  cross-mission.
- **"What does the check miss?"** Planted errors of 1-2 m (under ~2 px) are not contradicted (2
  of 352), though at 2 m a third come back `unconfirmed`; at 3 m 19 % still pass. State the floor.
  The test was on 22 windows at 74 °S with Sun azimuths under 10° apart; nothing was planted on
  the 132°/174° pairs.
- **"Your TC rung: 3 of 4 accepted?"** w01 is dense (134 inliers, held-out median 0.55 px =
  4.0 m); w02 (17 inliers, median 33.9 px) and w03 (39 inliers, 4.8 px) are thin. The defence:
  the archive offset is 381–431 m on all four windows, consistent. Do not claim more.
- **"Is everything from one commit?"** Every registration, sweep, loop, trust trial and the
  MiLOI re-judge ran at 49bdad9. The MiLOI MATCHES themselves (LoFTR/SIFT/ORB/AKAZE, ~4.5 h)
  were made at six earlier commits (3 of ours' 81 rows on `c9fb875-dirty`); `ops.freeze --plan`
  checks that the matching code has not changed since, and it had not.
