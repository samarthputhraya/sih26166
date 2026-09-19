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

Sub-pixel always names its grid: "px on the ~0.9 m NAC grid (x m)".

## Slide 1 (title page)

| Field | Value | Source |
|---|---|---|
| Team ID | `[TBD - portal Team ID]` | the SIH portal (STATUS, open question 1) |
| Team Name | LunaXX | portal, 18 Sep nomination |

## Slide 2 (idea title): 19 placeholders

| Text | Source (REPORT.md section → column) |
|---|---|
| Sun `[TBD]`° apart (SAC equatorial) | "SAC's own benchmark pair (equatorial …)" → Δsun az |
| `[TBD]/[TBD]` windows verified | same section → count of `agrees` / rows |
| polar `[TBD]/[TBD]` | "SAC's own benchmark pair (polar …)" → count of `agrees` / rows |
| `[TBD]` NAC frames, `[TBD]–[TBD]`° apart | "Real sun-angle sweep" → NAC frames, min–max Δsun az |
| TC `[TBD]`× | "Scale rung: … TC ortho map" → scale |
| fore vs aft `[TBD]` px | "Real viewpoint: TMC-2 fore → aft" → held-out RMSE ≤ 3 px (median over windows) |
| On `[TBD]` MiLOI pairs | "MiLOI" → pairs with a truth |
| agrees right `[TBD]/[TBD]`, contradicted wrong `[TBD]/[TBD]`, unconfirmed wrong `[TBD]/[TBD]` | "MiLOI" → trust verdict vs truth cross-tab |
| `[TBD]`% false alarms at 0-2 m, `[TBD]`% caught from 5 m | "Trust layer on real imagery: planted …" → rate by displacement |

## Slide 4 (feasibility): 9 placeholders

| Text | Source |
|---|---|
| `[TBD]` real windows across `[TBD]` instrument pairings | REPORT.md footer (distinct pairs) and its section count |
| loops close to `[TBD]` m | "Loop closure" → loop RMS median |
| held-out median `[TBD]` px on the NAC grid (`[TBD]` m) | "Chandrayaan-2 OHRC → LRO NAC" → held-out median range |
| `[TBD]` of `[TBD]` MiLOI pairs past 90° | "MiLOI" table → the 90-120° and 120-180° rows, all methods |
| NAC corners `[TBD]` km off at SAC's site | "SAC's own benchmark pair (equatorial …)" note → wide-search offset (`site_geometry/M1350459544RE.json`) |
| fore/aft leaves `[TBD]` px | as slide 2 |

## Figures

| Slide | Figure | Built from |
|---|---|---|
| 2 | `fig3_trust_map.jpg` | college-round demo cache. **Open:** a real-data version (OHRC→NAC accepted beside TC→MI refused) |
| 3 | `fig4_pipeline.png` | `core/pipeline.py` order |
| 4 | `fig5_real_sun_sweep.png` | `real_pairs_log.csv` outcome rows (rule v2) |
| 5 | `fig6_trust_real_calibration.png` | `trust_real_calibration.csv`. Re-run at the freeze, deleting the file first (Known issue 8: every run appends to it) |
| backup | `fig7_miloi_sun.png` | `miloi_log.csv` |

## Q&A traps this deck invites (answers must come from REPORT.md)

- "SuperGlue got 0.62/0.57 px on our pair." Their figure is an in-sample control-point RMSE per
  axis. Ours is held out (matches the fit never saw). Not the same measure. Say so before
  comparing.
- "Your MiLOI truth uses your own matcher." It does, on OTHER pairs: a translation network from
  ours+SIFT agreement, leave-one-out. S3's network has no redundancy, so its error is unmeasured.
- "Is OHRC ↔ NAC multi-modal?" No. Both are panchromatic. It is cross-sensor and cross-mission.
