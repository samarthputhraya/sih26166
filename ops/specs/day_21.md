# Day 21 (Sat 19 Sep 2026) - solo plan, Samartha + Claude

> The team split is suspended for the national-round push (decision 18 Sep). There are no teammate
> specs today; `spec-writer` was not run because no teammate has an assignment. This file is the
> day's plan, in order. Each item names the command and the "done when".

## Track A - SIH26166 (this repo, session 1)

1. **Finish yesterday's two runs** (see STATUS "In flight"). Done when: `ops/sun_sweep.py` has
   walked all 30 NACs; `evaluation/trust_real_calibration.csv` exists; `python -m presentation.make_figures`
   writes fig5 + fig6; `python -m ops.make_report` regenerates REPORT.md; logs committed.
2. **Review the sweep's judging rule** against Known issue 1 (low-NCC large sun gaps). Decide the rule
   on the evidence, write it in `ops/sun_sweep.py`'s docstring, re-classify from the logged NCCs (no
   re-registration needed), and say in REPORT.md how many labels moved.
3. **Viewpoint sweep (synthetic, exact truth).** `python -m core.pipeline --synthetic --dem
   C:\Users\samar\sih26166_data\raw\dem_site_60m.npy --pixel-size 60 --sun-delta 15 --tilt-sweep
   0,10,20,30,40,50 --repeats 3 --log --allow-failed`, then the same with `--parallax`. Done when:
   rows with tier `synthetic viewpoint` are in results_log and the curve is in REPORT.md.
4. **MiLOI benchmark** (data already at `<data>/miloi/`, 42 map-projected NAC tiles, 3 scenes):
   write `evaluation/miloi.py` (pairs per scene, truth from the two geotransforms, ours + SIFT/ORB/AKAZE,
   success = rmse_gt_px < 3), convert `Image_illumination_angles.xlsx` (openpyxl installed). Done when:
   a success-rate-vs-sun-gap table for ours and the classical baselines is logged.
5. **Scale rungs:** OHRC <-> Kaguya TC (40.8x; needs a chunked reference or the tiled driver) and
   OHRC <-> LOLA hillshade (261x, `--allow-failed`, the declared-failure rung). Done when both are rows.

## Track B - SIH26227 (second session, `C:\Users\samar\dev\sih26227`)

6. Open a second Claude Code session there and say: "Read CLAUDE.md and PLAN.md, then start Day 0."
   Done when: one Sentinel-2 date over the AOI is on disk with its STAC item JSON, and the RemoteCLIP
   licence decision is written in `evaluation/PROVENANCE.md`.

## Samartha (manual)

7. Portal check (draft / edit / limits / Team ID). 8. SPOC questions (STATUS Open questions 2).
9. PRADAN registration per `ops/national_round/PRADAN_GUIDE.md`.

## BLOCKED

None. Every input above is on disk or in the repo as of 18 Sep 18:40 (MiLOI, Kaguya maps, 34 NACs,
LOLA DEM, OHRC frame; SIH26227 venv installed).
