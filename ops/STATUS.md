# STATUS - 18 September 2026 (Day 20), 18:40 IST. National round, solo push: Day 0 done.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, which has a BOM - read it
> with `encoding="utf-8-sig"`). Deliverable bundles for every real pair: `<data>\out\<pair_id>\`.

---

## 🔴 Read this first

1. **Two background runs were still going at wrap** (both append to the evidence logs; see "In flight").
   Check them before anything else.
2. **We are nominated to the SIH 2026 national stage** as **LunaXX**. Ideas close **30 Sep**; we
   submit **Sun 27 Sep**. Max two PSs per team; a PS freezes at 500 ideas (SIH26166: 29 on 18 Sep).
3. **Samartha builds both entries alone** (decided 18 Sep; approved plan
   `C:\Users\samar\.claude\plans\wait-lets-do-it-zazzy-liskov.md`). CLAUDE.md Invariant 4 (folder
   ownership) is suspended for this push; Invariants 1, 2, 3, 5 hold. Teammates have no tasks.
4. **SIH26227** (MoD, satellite change analysis) is scaffolded in `C:\Users\samar\dev\sih26227`
   (CLAUDE.md, PLAN.md, official PS text, SIH template, venv `C:\Users\samar\venvs\sih26227` with
   torch/faiss/open_clip/rasterio installed) but **no code yet**. It needs its own Claude session.
   **Go/no-go: Fri 25 Sep evening.**
5. The deck title slide still says `SNPSU0192` / `SNPSU LunaX` (`presentation/build_deck.py:81-82`);
   the portal name is **LunaXX** and the rules forbid the institute's name.

## Position

```
Day 20 (18 Sep)  |  submit Day 29 (Sun 27 Sep) - 9 days  |  deadline 30 Sep
College gates: all moot (the internal round was 11 Sep and we cleared it)
Next checkpoints: Thu 24 Sep evidence freeze begins | Fri 25 Sep SIH26227 go/no-go + numbers frozen
```

## Verified this session, by command (18 Sep, 18:35)

| Check | Result |
|---|---|
| `python -m pytest evaluation/ -q` | 24 passed, exit 0 |
| `import core.pipeline` | OK, exit 0 |
| `python -m pytest -q` (whole repo) | **260 passed**, exit 0 |
| app, headless (`streamlit.testing`) on `site_ohrc_m1153871873le_w02_t` | no exception; held-out median readout; 4 download buttons |

## What landed today (commits `2e3e41e`..`bbacf68`, 11 commits)

| Area | Files | What |
|---|---|---|
| Research | `ops/national_round/` | brief, report (PS choice, competitors, ISRO awards), counter script + snapshots, **PRADAN_GUIDE.md** |
| Deliverables | `core/export.py`, `core/test_export.py`, CLI `--out`, `--allow-failed` | registered-product GeoTIFF (NaN outside footprint, reference geotags), matches.csv, GCPs (GDAL + QGIS), ISIS csv, trust map, report.json/md |
| Geometry | `core/geometry.py`, `core/test_geometry.py` | OHRC grid / LROC corners / equirect maps / GeoTIFF -> south polar stereographic; Newton-exact inverse; fillPoly overlap; fast projection |
| Real pairs | `ops/cut_site_pairs.py` | per-NAC correction field fitted and SAVED once (`<data>/site_geometry/<pid>.json`), anchor chaining for large sun gaps, Kaguya TC/MI kinds, three-way overlap, fixed ground size |
| Real scoring | `evaluation/real_eval.py`, `ops/run_real_pairs.py`, `ops/loop_closure.py`, `evaluation/real_pairs_log.csv` | archive-offset consistency, map transforms, loop closure, structured append-only log |
| Metrics | `evaluation/metrics.py` | `residual_median_px`, `holdout_inlier_rmse_px`, `holdout_inlier_frac` beside `residual_px` |
| Fallback | `core/reliability.py::xcorr_peak_subpixel`, `core/pipeline.py` | sub-pixel global shift (<0.15 px on known shifts) |
| App | `app/streamlit_app.py` | headline = held-out median; DELIVERABLES section (zip, GeoTIFF, CSV, report) |
| Viewpoint | `evaluation/synthetic_data.py`, CLI `--tilt-sweep --tilt-azimuth --parallax` | off-nadir tilt with exact truth; relief parallax field (NOT yet run) |
| Sweep / trust | `ops/sun_sweep.py`, `ops/trust_real_calibration.py` | real sun sweep with image-evidence judging; planted confident-wrong registrations on real windows |
| Deck / report | `ops/make_report.py` -> `REPORT.md`, `presentation/make_figures.py` (fig5, fig6), `presentation/DECK_V2_DRAFT.md` | report from logs only; deck v2 text with every number `[TBD]` |

## Evidence logged so far (results_log 344 rows; real_pairs_log 74 rows)

Site: CH-2 OHRC `ch2_ohr_ncp_20200229T0739312111_d_img_d18`, 74 S 43.6 E, sun elevation 6.9 deg (derived).
- **OHRC -> NAC, cross-sensor:** 20 windows, 3,000-5,400 inliers per ~600 m window on lit ground,
  91-99.8 % inlier ratio, held-out median 0.41-1.0 px on the 0.93-1.25 m NAC grid.
- **Loop closure** OHRC->A->B vs OHRC->B: 6 loops, **0.096-0.128 m RMS**.
- **Multi-modal:** TC vs MI 1548 nm: matcher fails, area check contradicts in 3/3, fallback within
  0.58-1.13 MI px of the visible-band solution.
- **Sun sweep (partial):** 36 windows over 13 NACs, sun-azimuth gap 3.3-50.9 deg: 35 correct_accepted,
  1 labelled missed_failure (see Known issue 1 - probably a labelling artefact).

## In flight - resume here

1. **`python -m ops.sun_sweep --windows 3 --log`** (started 18:28, log `<data>/sun_sweep_log2.txt`).
   Walks `<data>/nac/sweep_order.txt` (30 NACs, sun gap 3-153 deg), logs each window to both logs.
   Had reached the 51 deg NACs at wrap. **If it died, rerun the same command** - it skips pair_ids
   already carrying an `outcome` in real_pairs_log.
2. **`python -m ops.trust_real_calibration "site_ohrc_m1153871873le_w*_t" "site_ohrc_m1363141432re_w*_t" "site_m1153871873le_m1363141432re_w*_t" "site_ohrc_m1153871873le_w0[24678]" --log`**
   (log `<data>/trust_real_calibration_log.txt`). Registers 23 windows first (was ~2/3 through at
   wrap), then plants 76 trials per window, then writes `evaluation/trust_real_calibration.csv` and 10
   results_log rows. **If it died, rerun it** (the CSV did not exist yet, so nothing duplicates).
3. When both finish: `python -m presentation.make_figures` (fig5, fig6) and `python -m ops.make_report`,
   read REPORT.md, commit the logs.

## Tomorrow (Day 21, Sat 19 Sep) - `ops/specs/day_21.md`

## Open questions

1. Portal: draft save? editable after submit? title/description limits? exact Team ID / PS-ID format?
2. SPOC: does Student Innovation count toward the two PSs? who uploads? internal-hackathon report and
   authorisation letter uploaded?
3. PRADAN registration (guide: `ops/national_round/PRADAN_GUIDE.md`) - drop if no data by Tue 22 Sep.
4. SIH26227: has the second session started? (If not by Sun 20 Sep, the 25 Sep checkpoint is at risk.)

## Known issues - do not re-report these

1. **Sweep label `site_ohrc_m187919735re_w01_sw` = missed_failure** is probably wrong: matcher 3.49 m
   from the corrected archive geometry, 27 verified cells, but warp NCC 0.42 vs archive 0.39 misses the
   0.05 margin. The image-evidence rule is weak where both NCCs are low (large sun gaps). Review the rule
   before quoting sweep outcomes; never use the sweep as trust-layer evidence (that is fig6's job).
2. **`residual_px` is meaningless on real pairs** (RMSE over ALL held-out matches incl. outliers). Quote
   `residual_median_px` / `holdout_inlier_rmse_px`.
3. **Duplicate windows under two ids:** the sweep's `site_ohrc_m1153871873le_w0k_sw` are the same windows
   as `site_ohrc_m1153871873le_w0k` (deterministic picker). Count distinct windows, not rows.
4. **NACs without a usable correction** (`apply=false`): M1258744166RE, M1295016540LE, M1338673330RE.
   **No lit shared window:** M159642518LE, M1258737127RE. Both are recorded, not bugs.
5. `trust_real_calibration.csv` is appended by every run - a second run double-counts trials in fig6 and
   REPORT.md. Delete the CSV before a deliberate rerun (it is derived data; results_log keeps the history).
6. Plan item W2's `run_all(prior=)` hook and W8's tiled driver are **not built** - not needed so far,
   because pairs are cut onto a common map grid. The 40.8x OHRC<->Kaguya TC rung still needs one of them.
7. Every deck number must be re-run on the final commit (evidence freeze) so the deck cites one version.
8. PowerPoint on this machine is unlicensed; PDF via Print to PDF or another machine.
9. `docs/00_CANONICAL_FACTS.md`, `CLAUDE.md`, `ops/specs/day_20.md` describe the college round and the
   team split; they are stale. `day_20.md`'s teammate specs are parked.
10. **(added after wrap, 18 Sep ~19:00) Both runs FINISHED** - see "In flight" items 1-2: they are done.
    Sun sweep: 69 windows / 25 NACs. 0-30 deg: 30/30 correct_accepted (inliers median ~4,500);
    30-60 deg: 10 correct, 2 "missed_failure"; >= 60 deg: every window has 0 verified cells and is
    contradicted. Trust calibration: 1,702 planted trials on 23 windows - 0 % false alarms at d=0,
    0 % caught at 1-2 m (the design floor), 81.5 % at 3 m, 100 % at >= 5 m (~4 px).
11. **The sweep's labels above 120 deg are probably WRONG, and possibly in the trust layer's favour.**
    At 131-143 deg (sun from the opposite side) the matcher returns 400-1,400 inliers, its warp
    correlates at NCC -0.54 to -0.66 (vs archive alignment -0.28 to -0.41) and sits 5-53 m from the
    corrected archive geometry for M1233889992RE / M1369217819RE - i.e. it looks CORRECT under
    inverted shading. The trust layer rejected all of them (0 verified), and `ops/sun_sweep.classify`
    uses SIGNED NCC, so it labels them "caught_failure". They may be trust-layer FALSE ALARMS under
    contrast inversion. Before quoting anything >= 60 deg: (a) make classify sign-aware (|NCC|, or
    compare against the archive alignment by magnitude), (b) find out why the area check does not
    verify inverted-shading cells (its gradient-orientation representation should be invariant to a
    180 deg flip - check `core/reliability.representations`). Record the outcome in REPORT.md.
