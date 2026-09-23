# SIH26166 national deck: the numbers audit

> **v9, 23 Sep 2026 - the template-and-visuals pass** (`f26535a`). Same evidence, new form. The
> template decisions rest on 32 idea decks rendered and read, of which only three are verifiable
> national winners (Cannon Crew 2024 SIH1686, ExpertChain 2024 SIH1788, Ourobonics 2025
> SIH25117 - PS ids checked against the official 2024/2025 results pages): the idea title
> replaces "TITLE PAGE" and "IDEA TITLE"; the pointer prompts are heading tabs in the template's
> words (`_check_pointers` proves each is present); the blue footer bar stays. The SIH 2026 SPOC
> guidelines p.13 name the criteria; v9 added what v8 lacked for two of them - a prototype
> screenshot (user experience) and the strategies as a roadmap (future work progression).
>
> - **Every number is v8's**, re-read against REPORT.md by the v9 claim-check: 0 fabricated.
> - **Dropped from slides** (still true, still in REPORT.md): the 25 NAC frames of the sweep,
>   the SuperGlue-on-the-polar-pair comparison, the 5–9 % coverage and "0 of 64 cells" on
>   OHRC→TMC-2, SAC's 2026 paper quoted verbatim (now paraphrased, cited [2]).
> - **Corrected - wrong since v8, missed by two passes (H1):** "at 5 m, 105 of 120 trials still
>   say good". 105 is the count *not contradicted*; of those, 79 are `unconfirmed`, only 26
>   `agree` (`trust_real_calibration.csv`, rotation+scale, 5 m). Now: "at 3 m it refuses 0 of 120
>   trials, at 5 m only 15 of 120" (REPORT.md 354–355, 361–362).
> - **Other claim-check fixes:** "GeoTIFF / GDAL" chip → tifffile (the repo is GDAL-free by
>   design); no "open-source" claim for our own code (the repository has no LICENSE file); kornia
>   and the libraries are pinned in `requirements.txt`, not "credited above"; the console
>   screenshot is its left column only (the right column showed cache values - 91 %, one cell's
>   0.60 px, one run's 8.2 s - that are not REPORT.md rows); OHRC→TMC-2's 0.13–0.96 px is per
>   axis on the 5.58 m TMC-2 grid; the 37/37 tiling carries its scope (one OHRC × one NAC,
>   74 °S, Suns 3.3° apart); the subtitle and portal title no longer say "Sun-, scale- and
>   sensor-robust" - slide 4 shows where they are not.
> - **For Q&A, not on a slide (M9):** the rotation/scale 94 % holds per Sun population
>   (93.5 % near-Sun, 96.1 % SAC); the companion 87.4 % does not (97.3 % vs 66.0 %).
>   `make_report` pools the two in that table; split it after 27 Sep.
>
> **v6, 22 Sep 2026 - the pitch pass.** The table below is v4's and every row in it still holds:
> the pitch pass changed the *shape* of the argument, not the evidence, and the freeze is
> untouched at `7dd4e5b`. What changed on the slides, so this file is not read as current:
>
> - **Dropped from slides** (still true, still in REPORT.md, just not on a slide any more):
>   the MiLOI S1 sub-pixel figure, the 1.9 km archive-geometry offset, the IIRS 10/11 count,
>   and the per-verdict description of agrees / unconfirmed / contradicted (slide 3 draws it).
> - **Added, both checked before use:** the polar pair where SAC's own study found only
>   SuperGlue registered it (`REPORT.md` lines 97 and 121), and their 2026 mosaic paper's
>   statement that its framework "does not address geometric misalignment or parallax effects"
>   (arXiv:2604.25208 section VI, read 22 Sep 2026).
> - **Conditions restored by the 22 Sep claim-check:** the synthetic 0.086 px now carries its
>   0-15 deg Sun condition and the 45 deg degradation; the multi-modal px range carries its
>   metres; the rotation "3 px out" became "3 m of corner displacement, 0 of 120 trials
>   contradicted"; slide 6's provenance is now clause-by-clause per log.
> - **Deliberately absent:** any accuracy comparison with arXiv:2509.04775. Their SuperGlue
>   figure is 0.62 px on a 1.118 m grid (0.69 m); our best in-sample on that pair is 0.656 px
>   on a 1.622 m grid (1.06 m). The comparison loses and is not made.
>
> - **v7 (22 Sep, late):** slide 4's OHRC→TMC-2 line now carries its own evidence - 6–7
>   inliers per window, 5–9 % coverage, 0 of 64 cells verified by the area check, all four
>   contradicted with the fallback declared (`REPORT.md` 148–151; the held-out medians there
>   are not quoted as alignment error - Known issue 1) - and the strategies bullet is an ordered roadmap.
> - **v8 (22 Sep, late):** the claim-check on v7 found "160 windows / 8 pairings" on **no slide**
>   (dropped from slide 4 on the false premise that slide 2 carried it) - it is now slide 2's
>   first "How it addresses" bullet. The TMC-2 bullet gained its measured form: in-sample
>   0.13–0.96 px per axis on 6–7 inliers and **0 % of held-out matches within 3 px** on all
>   four windows, both printed in `REPORT.md`'s TMC section as of `3fa526b` (rendering-only
>   change to `ops/make_report.py`; header stamp and one new table are the whole diff). IIRS
>   names its counterpart (Kaguya TC) in both places. fig6: axis grids now 0.93–1.62 (both populations); caption counts 30 windows.
>
> PDF as shipped (v8): 1090972 bytes, sha256 `ae571678...`, `AUDIT: clean`, `PDF CHECK: clean`.

---

## v4's audit table, unchanged and still valid

> **RE-FILLED AGAIN from the freeze at `7dd4e5b`** (`--check`: FROZEN, 10/10 steps; 183/183 real
> rows, 324/324 MiLOI, 8/8 multi-modal). The re-freeze was forced by the F12 fix (`core/ransac.py`
> now returns MAGSAC++'s own inlier mask; `is_inlier` in the exported match table had been decided
> by float64-vs-float32 equality, so 41 of 183 bundles shipped empty `gcps.txt`, `gcps.points` and
> `matches_isis.csv`). `ops/loop_closure.py` reads that flag, so the loop numbers moved ~2 %.
> Six values changed and are marked **v4** below; every other row re-derived identical.
> Two clauses were earned and added: the dense tiling on slide 4 and the rotation/scale trust
> result on slide 5, both against bars written down before the runs (`AUDIT_REPORT.md`).
> The hand-picked 20-window residual range on slide 4 was **replaced** by the 37-window tiled
> result over the same site - denser, unselected, and the answer to "did you pick your windows?".
>
> **`claim-checker` on v4: 0 fabricated numbers; all six changed values correct.** It returned
> 2 HIGH, 8 MEDIUM, 4 LOW on nouns, scope and labels; every one was verified against REPORT.md by
> hand before acting. Applied: **H1** slide 4 says "160 distinct ground windows", not "160 real
> window pairs" - REPORT's footer prints 177 pairs AND 160 windows and they are different counts;
> **H2** slide 5 no longer says rotation and scale "behave the same way" as translation, because
> at 5 m the FRAME verdict catches a rotation only 10-15 % of the time against 100 % for a shift -
> it now says "caught cell by cell, not by the frame verdict"; **M1** the tiling clause names its
> scope (one OHRC frame with one NAC) and the texture screen; **M2** MiLOI S1 gains its metres
> (0.52 px = 0.73 m); **M3/L3** the loops are labelled "a median … - consistency, not ground
> truth" so they cannot read as truth error after the preceding "vs exact truth"; **M4** MiLOI's
> 90° is named a **Sun-vector** angle, not an azimuth; **M5** slide 2's second `0/N` is named as
> the floor; **M6/M7/L4** the portal text gains the 36-of-37 caveat, names Sun **azimuth** on both
> populations, and gives the loops' grid; **M8** this file and `build_deck.py`'s docstring name
> v4 / `7dd4e5b`; **L1** fore/aft is 15.5 m, not 16 m (2.617 px × 5.929 m).
>
> **Declined, with the reason: L2**, which asked for "11/11 refused" instead of "10/11 refused,
> none registers" on the IIRS bullet. *Refused* has a defined meaning here - the pipeline declared
> a fallback - and that is true of exactly 10 of the 11; the 11th is `unconfirmed`, which is kept
> and not certified, a different state. "None registers" already covers all 11. Changing 10 to 11
> would make the sentence easier to read and less true.

> The slide text lives in `presentation/build_deck.py` (S2-S6) and nowhere else. This file is
> the audit table for it: every number on a slide, the value it holds, and the REPORT.md section
> it was copied from.
>
> **RE-FILLED 20 Sep 2026 from the evidence freeze at `b678272`** (`python -m ops.freeze --check`:
> FROZEN, 10/10 steps; 146 of 150 latest real-pair rows at `b678272` - the 4 withdrawn rows stay
> at `5ea70d1`; every latest MiLOI row scored `b678272`; `multimodal_check.csv` 8/8). All 146
> registration rows reproduced the `49bdad9` values exactly; the rows marked "New" or "Moved"
> below are the audit's additions (`ops/national_round/AUDIT_REPORT.md`). No placeholder is open.
> `build_deck`: AUDIT clean; `export_pdf`: PDF CHECK clean; `claim-checker` on v3: 0 numeric
> mismatches, its H/M findings applied (metres on every sub-pixel figure, "Sun azimuths",
> population named on slide 5, metres-first for the multi-modal fallback). Every "Value at b678272"
> that was already on the v2 deck is the value the `b678272` freeze reproduced.
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
| Team ID | SNPSU0192 | the SIH portal, read by Samartha 20 Sep (the audit's SNPSU ban now targets only the old team name "SNPSU LunaX") |
| Team Name | LunaXX | portal, 18 Sep nomination |

## Slide 2 (idea title)

| Text on the slide | Value at 7dd4e5b | Source (REPORT.md section → column) |
|---|---|---|
| Sun azimuths … apart, … accepted (SAC equatorial) | 174° (173.5–173.7); 6/6 | "SAC's own benchmark pair (equatorial …)" → Δsun az; `agrees` / rows |
| polar …°, …, the other two flagged | 132° (132.2–132.3); 4/6; w05 unconfirmed, w06 contradicted + fallback | "SAC's own benchmark pair (polar …)" → Δsun az; verdicts |
| … NAC frames, azimuths …–…° apart | 25; 3–153 (3.3–152.7) | "Real sun-angle sweep" → the "All bins" line |
| TC …×, … accepted | 29.6×; 3/4 (w04 unconfirmed) | "Scale rung: … TC ortho map" → scale; `agrees` / rows |
| TC (visible) to MI 1548 nm: refused on …/… windows; the declared fallback lands …–… m from the visible-band registration of the same window (…–… px on MI's … m grid) | 3/3 fallback; 3.4–16.2 m (3.4, 4.2, 16.2 as REPORT prints them); 0.23–1.09 px (0.227, 0.283, 1.093); 14.8 m grid | "Kaguya TC → Kaguya MI" 1548 nm rows → declared; its "Fallback vs the visible band" table → disagreement median px (m). **New at `b678272`** (`ops/multimodal_check.py`, E1 of the audit) |
| TC to Chandrayaan-2 IIRS (…×, … m): …/… refused, none registers | 12× (12.019); 89 m (88.94); 10/11 fallback; the 11th (`site_tc_ortho_iirs1555_w10`) is LoFTR but `unconfirmed`, so no window `agrees` | "… IIRS" rows → scale, declared, verdict; the "Band against band" table shows the fallbacks disagree by up to 3.4 km |
| MiLOI, … pairs (… in scene S3); agrees within 3 px; contradicted wrong; unconfirmed wrong | 81 (56 in S3); 33/33; 43/43; 5/5 | "MiLOI" → the verdict table, column **matcher H within 3 px** (what the trust layer judges). `rmse_gt_px` for agrees is 28/33: have both ready for Q&A |
| … real windows (Sun azimuths under …° apart): …/44 false alarms; flagged …% at 3 m, …% from 5 m, and 0 of 352 at 1–2 m — the floor | 22 (3.3, 5.8, 9.1°); 0/44; **74%** (131/176 = 74.4 %); 100% (176/176 at each of 5–200 m); **0/352 (v4)** (1 m 0/176; 2 m 0/176) | "Trust layer on real imagery: planted …" → the "Sun azimuths under 10° apart" population, rows 0, 1, 2, 3 and ≥ 5 m. **Moved at `b678272`**: the 3 m rate was 81.2 % (143/176) at `49bdad9`, 73.9 % (130/176) at `b678272`, 74.4 % (131/176) at `7dd4e5b` - three draws, all quotable as 74 %; the 1–2 m rate has been 1/352 and 0/352, so say "almost none", never "zero", in speech. Same 22 windows, same code path for them; the planted directions and match noise are drawn from one RNG stream that the eight SAC windows now consume first, so this is a second random draw of the same experiment. 3 m is the transition point (2.41 px against a 2 px cell threshold), and two draws put it at 74-81 %: quote 74 % (frozen) and say "about three quarters" in speech |
| on … of SAC's windows (Suns 132–174° apart): …/16 false alarms, …% at 5 m, …% from 10 m | 8 windows (`sac_ohrc_nac_w01-w06`, `sac_polar_ohrc_nac_w01`, `w03`; true-alignment NCC −0.53 to −0.90); 0/16 at 0 m; 0/64 at 1 m; 4.7 % at 2 m; 12.5 % at 3 m; **84.4 % at 5 m (54/64) (v4)**; 100 % (64/64) at each of 10–200 m. On the 1.622 / 1.215 m grids 5 m is only 3.1 px, hence 84 %, not 100 %. It was 93.8 % (60/64) at `b678272`: same windows and code path, a fresh draw of the planted directions and match noise (the trial list changed when E5 added rotation and scale, so the RNG stream is consumed differently). 5 m is the transition point for this population; quote 84 % (frozen) and say "most, not all, at 5 m" in speech | same section, the "Sun azimuths 132-174° apart" population (E2 of the audit) |

## Slide 3 (technical approach)

| Text on the slide | Value at 7dd4e5b | Source |
|---|---|---|
| median … s per 640-px window (… OHRC → NAC windows) | **8.2 s (v4)**; 89 windows (the 74 °S loop legs and the sun sweep; `seconds` of the latest rows, re-run at `7dd4e5b`; wall time, so it differs run to run - 10.0 s at `49bdad9`, 10.7 s at `b678272`, 8.2 s here. Quote the frozen number; in speech say "about ten seconds a window on a laptop" and note it is wall time on a machine that was doing nothing else) | "Runtime and match distribution" |

## Slide 4 (feasibility)

| Text on the slide | Value at 7dd4e5b | Source |
|---|---|---|
| … distinct ground windows | **160 (v4)** | REPORT.md footer, verbatim: "177 registered pairs (160 distinct ground windows; Known issue 2: some were cut twice under two ids)". A ground window is (source product, reference product, centre, size) from `geometry_prior.json` (`presentation.make_figures._distinct_windows`), so the deck counts ground, not ids. It was 136 of 140 at `b678272`; the E7 dense tiling added 37 and the E2/E5 work the rest |
| … instrument pairings | 8 | REPORT.md pair sections: OHRC-NAC, NAC-NAC, OHRC-TMC2, TMC2-TMC2, TC-MI, TC-IIRS, OHRC-TC, OHRC-LOLA. (Some pre-18-Sep rows' `kind` said `nac-nac` for TC→MI; the latest rows say `tc-mi`, and REPORT.md derives the kind from the product ids anyway.) |
| Sub-pixel, grid named: … px = … m vs exact truth at 0° and 15° Sun azimuth difference (synthetic, 60 m grid) | 0.086 px (median at 0° and at 15°, the fig1 rows); 5.1 m | "Sub-pixel accuracy, with the pixel grid named" → the synthetic row (from `presentation.make_figures.load_curves`) |
| six loops close to a median … px = … m on the 1.245 m NAC grid - consistency, not ground truth | **0.086 px, 0.107 m (v4)** (median loop RMS on the B grid; max 0.131 m) | same table, the loop row; "Loop closure". Moved ~2 % at `7dd4e5b` because `ops/loop_closure.py::_inlier_src_points` reads `is_inlier` from `matches.csv`, which the F12 fix corrected (0.104 m at `b678272`). The deck now prints three significant figures so a judge comparing it with REPORT.md sees the same number, not a truncation |
| MiLOI network truth, 9 S1 pairs: median … px = … m on 1.1–1.5 m grids (truth error … px) | 0.52 px = **0.73 m (v4)** (n=9, grids 1.12–1.53 m); truth error 0.22 px = S1's leave-one-out median (max 0.29, n=3) | same table, the MiLOI row; "MiLOI" scene table → S1 truth error |
| the whole lit 74 °S overlap tiled, not hand-picked — … windows, … km² — accepts …/…, median … px = … m on the … m grid, … of … under 3 px | **NEW in v4**: 37 windows of 596 m = 13.1 km²; 37/37 `agrees`; median 0.61 px = 0.57 m; 0.931 m grid; 36 of 37 under 3 px | "The whole lit overlap, tiled" (E7 of the audit). **This row replaced** the hand-picked 20-window range (3–6° apart; 0.41–1.01 px = 0.51–0.94 m; 20/20 agree), which is still in REPORT.md under "Chandrayaan-2 OHRC → LRO NAC" and is the answer to "what about your original windows?". The tiled set is denser and unselected, so it is the honest headline; it is also slightly worse (0.61 vs 0.41–1.01 median range), which is the point. The one window over 3 px is `site_ohrc_m1153871873le_w15_full` at 316 px, an inlier-ratio limit of the held-out median (0.542), not a registration failure - NCC of the aligned window is +0.87 to +0.95 on all 37. **Say that if asked; do not let "37/37 accepted" imply 37/37 sub-pixel** |
| … on SAC's equatorial pair, 174° apart, 1.62 m grid | 0.69–1.68 px (0.690–1.676); 1.1–2.7 m (1.120–2.718) | "SAC's own benchmark pair (equatorial …)" → held-out median column and its (m) |
| MiLOI past 90°: any of the … pairs with **Sun vectors** 90° or more apart (all scene S3) - a Sun-VECTOR angle, not an azimuth like every other Sun figure on the deck | 16 (9 + 7 pairs, every method 0; all S3 in miloi_log) | "MiLOI" table → rows 90-120 and 120-181 |
| sweep: … of … at 60-120°, … of … at 120-153° | 0 of 12 (7 + 5); 10 of 15 | "Real sun-angle sweep" → bins 60-90 + 90-120, and 120-180 (registered & accepted / windows) |
| OHRC → TMC-2 at SAC's site (azimuths …°, incidence …° apart): all 4 refused | 120° (120.2); 59° (d_incidence −59.44); 4/4 contradicted + fallback | "SAC's benchmark site: OHRC → TMC-2 nadir" → Δsun az; verdict; declared |
| NAC's published corners and the OHRC grid disagree by … km | 1.9 km (+488, +1790 m → 1.86 km); applied before cutting by `cut_pradan_pairs.wide_offset` | "SAC's own benchmark pair (equatorial …)" note → wide-search offset (`site_geometry/M1350459544RE.json`) |
| fore/aft accepts … window of 4, held-out median … px (… m) - **15.5 m (v4)**, not the 16 m v3 printed: 2.617 px × 5.929 m = 15.51 | 1 (w04 agrees; w02, w03 unconfirmed; w01 contradicted + fallback); 2.6 px (2.617) × 5.929 m = 16 m (15.5) | "Real viewpoint: TMC-2 fore → aft" → **held-out median** column, not "RMSE ≤ 3 px" (capped at 3 px by definition) |

## Slide 5 (impact)

| Text on the slide | Value at 7dd4e5b | Source |
|---|---|---|
| planted errors of 5 m or more were all flagged, …% at 3 m, and at 2 m or less almost none (… SAC windows with Suns 132–174° apart: …/16 false alarms, 100% from … m) | 176/176 at 5–200 m; 74% at 3 m; **0/352 (v4)** at 1–2 m; 8 SAC windows, 0/16, 100 % from 10 m (**84 % (v4)** at 5 m, said on both slides) | "Trust layer …", both populations |
| Planted rotation and scale are caught cell by cell, not by the frame verdict: of the 8×8 cells they displace past 2 px, …% lose verified state | **NEW in v4**: 94 % (19653 of 20896 cells, over 840 trials, 420 rotation and 420 scale, at 0–20 m corner displacement). The companion number, not on the deck but the one a sceptic should ask for: of the 22464 cells the same errors moved by LESS than 1 px, 87.4 % stayed verified - the map is not simply refusing everything | "Errors that are not translations: planted rotation and scale" → the summary line under the table (E5 of the audit). **Cells, not frames**: the frame verdict still says `agrees` while a corner is 3 px out, because a rotation is not uniform over the frame - that is why this clause counts cells and says so. Pre-registered bar was 90 % refused / 80 % kept, written down before the run; measured 94.1 % / 87.4 % |
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

- **"Multi-modal: you just refuse. Does anything register?"** Yes, and it is measured. On the
  three TC → MI 1548 nm windows the area check refuses LoFTR (5-6 inliers of 33-35) and the
  declared correlation fallback lands 0.23-1.09 px (3.4-16 m on the 14.8 m MI grid) from the LoFTR
  registration of the visible 749 nm band of the SAME window, while the archive prior was 38-46 m
  off ("Fallback vs the visible band" table). The infrared band is registered to about one MI
  pixel; what is refused is the *matcher*, not the registration. IIRS is different: 89 m pixels,
  12× scale, 112-px frames; the two bands' fallbacks disagree by up to 3.4 km, so nothing there is
  a registration and the deck says none registers.
- **"TMC is in the title. 0 of 4?"** The only TMC-2 pass on disk over SAC's frame has the Sun
  59° higher (elevation 69° vs 10°) and 120° round in azimuth; the honest result is four refusals,
  declared. The PRADAN footprints hold a second nadir pass, `20251107T2205`, with the Sun about 9°
  from the OHRC's in azimuth and 25° in incidence; `cut_pradan_pairs --tmc-product` is ready for
  it. [If it lands before the final freeze, quote its rows; otherwise say exactly this.]
- **"Your trust calibration is only on easy Sun."** Not any more: on 8 of SAC's own windows
  (Sun azimuths 132-174° apart, where a correct alignment anti-correlates at NCC −0.5 to −0.9)
  the same planted-failure test gives 0/16 false alarms, 94 % flagged at 5 m and 100 % from 10 m,
  against 100 % from 5 m on the 22 near-Sun windows. The difference is the grid: 5 m is 3.1 px on
  SAC's 1.6 m NAC grid but 4 px on the 1.25 m grid, and the detection edge sits near 2-3 px. The
  two populations are reported separately in REPORT.md, never pooled.
- **"81 % or 74 % at 3 m?"** Both are honest draws of the same experiment on the same 22
  windows (random planting directions and noise): 143/176 at the 19 Sep freeze, 130/176 at the
  20 Sep freeze. The deck quotes the frozen 74 %. 3 m is the transition (2.4 px against a 2 px
  cell threshold); say "about three quarters at 3 m, everything from 5 m".
- **"How much of the MiLOI cross-tab depends on your own truth?"** The contradicted pairs' matcher
  errors start at 7.4 px (next 31.7, median 288 px) and the agreeing ones end at 2.9 px; a truth
  error under ~4 px cannot move a pair across the 3 px line. S1/S2 truths are good to 0.22-0.26 px
  (leave-one-out); S3's is unmeasured. Only the 5 unconfirmed pairs (3.2-9.1 px) sit near the line.
- **"Sub-pixel on which grid?"** Every figure names it: 0.086 px on the 60 m synthetic grid (exact
  truth; 5 m); 0.61 px held out over the whole tiled 74 °S overlap on the 0.93 m NAC grid (0.57 m;
  not truth) and 0.41-1.01 px on the 20 hand-picked windows of that site; 0.086 px loop closure on
  1.245 m (0.107 m, consistency); 0.52 px on MiLOI S1 (1.1-1.5 m grids, truth good
  to 0.22 px). The 0.086 px is a rendered pair without cast shadows; the real-data figures are the
  ones to lead with.
- **"Did you choose the windows that worked?"** No: the 74 °S headline is now every non-overlapping
  640-px window the cutter finds in shared, lit, textured ground of that overlap - 37 of them,
  13.1 km², selected by texture and illumination before any matching, 37/37 accepted. One reports a
  held-out median of 316 px at an inlier ratio of 0.542; that is the metric degrading, not the
  alignment (NCC +0.87 to +0.95 on all 37), and REPORT.md says so in the same section.
- **"Runtime for a full OHRC strip?"** Median 8.2 s per 640-px NAC-grid window on this laptop
  (89 windows); a 12,000 × 90,000 px OHRC strip at 0.25 m covers about 1,300 such windows on a
  1.2 m NAC grid, i.e. roughly 3 hours single-threaded - an estimate, not a measurement. Wall time
  varies run to run (10.0, 10.7, 8.2 s over three freezes), so say "under four hours", not a
  precise figure, and say it is single-threaded CPU with no GPU.

- **"SuperGlue got 0.62/0.57 px on our pair."** Their figure is an in-sample control-point RMSE
  per axis, on their resampled NAC grid (1.1179 m). Our headline is held out (matches the fit
  never saw), on the NAC's own grid in our cut (1.62 m). It differs in measure and in grid; say
  both before comparing anything. Since 19 Sep the SAME measure is logged for ours too
  (`insample_rmse_x_px` / `_y_px` in real_pairs_log; REPORT.md's "In-sample, per axis (SAC's
  measure)" table under each SAC section). Quote it in px AND metres, with the inlier count
  graded: ours grades thousands of MAGSAC++ inliers up to 3 px, not a handful of control points,
  so it is not smaller by construction. Compare in metres (their px × 1.1179 m).
  **At b678272 (unchanged since 49bdad9) ours is NOT better on this measure**: equatorial X 0.66–1.15 px, Y 0.73–1.07 px
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
- **"What happens between the windows you chose?"** We tiled one whole overlap to find out. Every
  non-overlapping 640-px window in the shared lit ground of the 74 °S OHRC frame and NAC
  M1153871873LE - 37 windows, 13 km², Sun azimuths 3.3° apart - was registered: all 37 accepted,
  3.8 min of wall time in total, a median of 7.3 s per window. It is its own REPORT.md section and
  is never pooled with the 20 hand-spread windows the deck quotes.
- **"One of those windows reports a 316 px residual and you accepted it."** Correct, and it is the
  metric that failed, not the registration. `residual_median_px` is the median error of the 20 %
  of matches the fit never saw, and it is robust only while the inlier ratio stays well above 0.5.
  That window (`site_ohrc_m1153871873le_w15_full`) has an inlier ratio of 0.542, so a random
  held-out draw can be majority-outlier and the median then describes the outliers. Under the
  transform the system declared, the median error over ALL its matches is 1.08 px; its exported
  registered product correlates with the reference at NCC +0.93, as do all 37 (+0.87 to +0.95).
  The 20 windows on the deck have inlier ratios 0.614-0.998. This is the honest floor of that
  number and it is in REPORT.md, not hidden.
- **"You only planted translations."** Not any more. The calibration also plants rotations and
  scale changes about the frame centre, sized by how far they move the corners. Their point is
  that they are NOT uniform over the frame: the verdict stays `agrees` at small sizes while the
  map loses cells, so the frame verdict is the wrong thing to watch and the 8 × 8 map is what
  carries the information. [numbers: REPORT.md "Errors that are not translations"]
- **"Did you try to get the accuracy up?"** Yes, and we pre-registered the bar before looking. A
  final least-squares fit on a tighter inlier set was tried on all 26 OHRC → NAC windows; it had
  to improve the HELD-OUT median on 5 of 6 SAC windows and 15 of 20 at 74 °S, and it made 5 of 6
  and 13 of 20. It is not in the pipeline. It would have cut the in-sample per-axis RMSE to
  0.46-0.60 px, which is a smaller number than the paper's 0.62 px - but on a 1.622 m grid
  against their 1.1179 m, and in metres it still loses (0.75-0.98 m against 0.69 m). That is the
  comparison we refuse to make.
- **"Is everything from one commit?"** Every registration, sweep, loop, trust trial and the
  MiLOI re-judge ran at b678272. The MiLOI MATCHES themselves (LoFTR/SIFT/ORB/AKAZE, ~4.5 h)
  were made at six earlier commits (3 of ours' 81 rows on `c9fb875-dirty`); `ops.freeze --plan`
  checks that the matching code has not changed since, and it had not.
