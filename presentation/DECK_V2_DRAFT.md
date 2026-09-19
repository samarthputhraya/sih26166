# SIH26166 national deck, v2: the numbers audit (19 Sep 2026)

> The slide text lives in `presentation/build_deck.py` (S2-S6) and nowhere else. This file is
> the audit table for it. Each `[TBD]` on a slide is listed here with the evidence it will be
> read from. **Fill them only from the evidence-freeze commit** (Thu 24 Sep onwards), after the
> freeze has re-run every pair, the MiLOI re-judge and both trust calibrations on that commit.
> Then re-run `python -m ops.make_report`, copy each number from REPORT.md, and run
> `claim-checker`. `python -m presentation.build_deck` reports every placeholder still open and
> exits 1 until none are left.
>
> Audience: SAC-ISRO image-processing scientists reading the PDF cold, ranking it against every
> other SIH26166 idea. Output: `presentation/SIH26166_LunaXX_deck.pptx`. The college-round deck
> (`SIH26166_deck.pptx`) is left as it was.
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

| Text | Source (REPORT.md section → column) |
|---|---|
| Sun azimuths `[TBD]`° apart, `[TBD]/[TBD]` accepted (SAC equatorial) | "SAC's own benchmark pair (equatorial …)" → Δsun az; `agrees` / rows |
| polar `[TBD]/[TBD]` | "SAC's own benchmark pair (polar …)" → `agrees` / rows |
| `[TBD]` NAC frames, azimuths `[TBD]–[TBD]`° apart | "Real sun-angle sweep" → the "All bins" line |
| TC `[TBD]`×, `[TBD]/[TBD]` accepted | "Scale rung: … TC ortho map" → scale; `agrees` / rows |
| infrared: `[TBD]` of `[TBD]` refused and fall back | "Kaguya TC → Kaguya MI" 1548 nm rows + "… IIRS" rows → declared `fft_phase_correlation (fallback)` / rows |
| MiLOI: `[TBD]` pairs; agrees within 3 px `[TBD]/[TBD]`; contradicted wrong `[TBD]/[TBD]`; unconfirmed wrong `[TBD]/[TBD]` | "MiLOI" → the verdict table, column **matcher H within 3 px** (what the trust layer judges). The `rmse_gt_px` column differs for agrees: have both ready for Q&A |
| `[TBD]`% false alarms, `[TBD]`% caught at 3 m, `[TBD]`% from 5 m | "Trust layer on real imagery: planted …" → the 0 m row, the 3 m row, the ≥ 5 m rows |

## Slide 4 (feasibility)

| Text | Source |
|---|---|
| `[TBD]` real windows | REPORT.md footer → registered pairs, minus the duplicate windows of Known issue 2 (count them by hand and say how) |
| `[TBD]` instrument pairings | REPORT.md pair sections: OHRC-NAC, NAC-NAC, OHRC-TMC2, TMC2-TMC2, TC-MI, TC-IIRS, OHRC-TC, OHRC-LOLA. Do NOT count by the log's `kind` column (the TC→MI rows say `nac-nac`) |
| loops close to `[TBD]` m | "Loop closure" → loop RMS median |
| OHRC → NAC residual: Sun `[TBD]–[TBD]`°, median `[TBD]–[TBD]` px, `[TBD]–[TBD]` m | "Chandrayaan-2 OHRC → LRO NAC" → Δsun az range, held-out median range, the (m) values. Two NAC grids (0.93 and 1.25 m) |
| MiLOI past 90°: `[TBD]` of `[TBD]` | "MiLOI" table → rows 90-120 and 120-180, all methods |
| sweep: `[TBD]` of `[TBD]` at 60-120°, `[TBD]` of `[TBD]` at 120-153° | "Real sun-angle sweep" → bins 60-90 + 90-120, and 120-180 (registered & accepted / windows) |
| NAC corners `[TBD]` km off at SAC's site | "SAC's own benchmark pair (equatorial …)" note → wide-search offset (`site_geometry/M1350459544RE.json`) |
| fore/aft held-out median `[TBD]–[TBD]` px | "Real viewpoint: TMC-2 fore → aft" → **held-out median** column, not "RMSE ≤ 3 px" (that one is capped at 3 px by definition) |

## Slide 5 (impact)

| Text | Source |
|---|---|
| `[TBD]` OHRC frames at `[TBD]` sites | distinct `ch2_ohr_*` source products in the latest real_pairs_log rows (74 S; SAC equatorial; SAC polar) |

## Figures

| Slide | Figure | Built from |
|---|---|---|
| 2 | `fig3_trust_map.jpg` | college-round demo cache. **Open:** a real-data version (OHRC→NAC accepted beside TC→MI refused). Its "accepted" example (`pair_01`) is two crops of one OHRC frame |
| 3 | `fig4_pipeline.png` | `core/pipeline.py` order (refinement before MAGSAC++, fixed 19 Sep) |
| 4 | `fig5_real_sun_sweep.png` | `real_pairs_log.csv` outcome rows (rule v2) |
| 5 | `fig6_trust_real_calibration.png` | `trust_real_calibration.csv`. Re-run at the freeze, deleting the file first (Known issue 8: every run appends to it). Its axis label uses one grid (1.245 m); 11 of the windows are on 0.931 m |
| backup | `fig7_miloi_sun.png` | `miloi_log.csv` |

## Q&A traps this deck invites (answers must come from REPORT.md)

- **"SuperGlue got 0.62/0.57 px on our pair."** Their figure is an in-sample control-point RMSE
  per axis, on their resampled NAC grid (1.1179 m). Ours is held out (matches the fit never saw),
  on the NAC's own grid in our cut (1.62 m). It differs in measure and in grid; say both before
  comparing anything.
- **"Your MiLOI truth uses your own matcher."** It does, on OTHER pairs: a translation network
  from ours+SIFT agreement, leave-one-out. S3's network has no redundancy, so its error is
  unmeasured. 56 of the 81 scored pairs are S3.
- **"'Unconfirmed' pairs were wrong. Did you ship them?"** Yes: the matcher's transform is kept,
  labelled unconfirmed and not certified (the log calls them `missed_failure`).
- **"Is OHRC ↔ NAC multi-modal?"** No. Both are panchromatic. It is cross-sensor and
  cross-mission.
- **"What does the check miss?"** Planted errors of 1-2 m (under ~2 px) pass; at 3 m some still
  agree. State the floor.
