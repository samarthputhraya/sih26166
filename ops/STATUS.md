# STATUS - 18 September 2026 (Day 20), evening. National round: nominated. Solo push, Day 0 of 9.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> WARNING: the venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly.
> External data lives in `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, which has a BOM -
> read it with `encoding="utf-8-sig"`).

---

## 🔴 Read this first

1. **We cleared the college round and are nominated to the SIH 2026 national stage** (portal team
   name **LunaXX**). Ideas close **30 Sep 2026**; we submit **27 Sep**. Max two PSs per team; a PS
   freezes at 500 ideas (SIH26166 had 29 on 18 Sep). Research: `ops/national_round/RESEARCH_REPORT.md`.
2. **Samartha is building both entries alone** (decision 18 Sep; plan
   `C:\Users\samar\.claude\plans\wait-lets-do-it-zazzy-liskov.md`). CLAUDE.md Invariant 4 (folder
   ownership) is suspended for this push; Invariants 1, 2, 3, 5 hold. Second entry **SIH26227**
   (MoD, satellite change analysis) lives in `C:\Users\samar\dev\sih26227` with its own CLAUDE.md /
   PLAN.md / venv - run it in a second Claude session. **Go/no-go on SIH26227: 25 Sep evening.**
3. **The title slide is wrong for the national round**: `presentation/build_deck.py:81-82` still
   say `SNPSU0192` / `SNPSU LunaX`; the portal name is **LunaXX** and the 2026 rules forbid the
   institute's name. Fix when the portal's exact Team ID is known.
4. **`residual_px` is meaningless on real pairs** - it is the RMSE over ALL held-out matches incl.
   outliers (352 px on a pair whose inliers sit at 0.5 px). Quote `residual_median_px` /
   `holdout_inlier_rmse_px` (added to `evaluate()` 18 Sep; the app now shows the median).

## Samartha's manual tasks (not code)

- Portal: draft save? edit after submit? title/description limits? exact Team ID and PS-ID format?
- SPOC: does Student Innovation count toward the two? who uploads? internal-hackathon report and
  authorisation letter uploaded?
- PRADAN / chmapbrowse registration (TMC-2, IIRS, SAC's own OHRC products) - bonus track only.

---

## What exists now that did not this morning (all on `main`)

| Commit | What |
|---|---|
| `2e3e41e` | national-round research, PS-count snapshots, `ops/national_round/pull_ps_counts.py` |
| `e9508bc` | **deliverables**: `core/export.py` - registered-product GeoTIFF, `matches.csv`, GCPs (GDAL + QGIS), ISIS csv, trust map, `report.json/md`; `--out`, `--allow-failed` on the CLI |
| `42845fe` | **real geometry**: `core/geometry.py` (OHRC grid, LROC corners, equirect maps, GeoTIFF frames -> south polar stereographic), `ops/cut_site_pairs.py`, robust held-out residuals |
| `057664a` | **26 real OHRC/NAC registrations logged + 6 three-image loops closed** (`ops/run_real_pairs.py`, `ops/loop_closure.py`, `evaluation/real_eval.py`, `evaluation/real_pairs_log.csv`) |
| `1a62951` | **real multi-modal**: Kaguya TC (visible) vs Kaguya MI 1548 nm (infrared) |
| `dcd2bc3` | sub-pixel fallback (`xcorr_peak_subpixel`); app shows held-out median + DELIVERABLES downloads |
| `2429e88` | real sun sweep (`ops/sun_sweep.py`), planted-failure trust calibration (`ops/trust_real_calibration.py`), 100x faster geometry |
| uncommitted | viewpoint: `evaluation/synthetic_data.make_pair(tilt_deg, tilt_azimuth_deg, parallax)`, `--tilt-sweep` on the CLI |

## The evidence so far (results_log rows 277-308, real_pairs_log rows 1-38)

The site: Chandrayaan-2 OHRC `ch2_ohr_ncp_20200229T0739312111_d_img_d18` at 74 S 43.6 E (sun
elevation 6.9 deg, derived). **166 LROC NAC frames overlap it**; 30 downloaded for a sun sweep.

- **OHRC -> NAC (cross-sensor, cross-mission), 20 windows**: 3,000-5,400 inliers per 600 m
  window at 91-99.8 % inlier ratio and full grid coverage on the lit windows; held-out median
  0.41-1.0 px on the 0.93-1.25 m NAC grid. (Best public competitor: 5-7 inliers per pair.)
- **Loop closure**, OHRC -> NAC A -> NAC B vs OHRC -> NAC B, 6 windows: **0.096-0.128 m RMS**
  (0.08-0.10 px of the 1.245 m grid). Loop closure cancels errors attached to one image
  (geolocation, its own shading) - it is correspondence consistency, not absolute accuracy.
- **Multi-modal**: TC vs MI 749 nm (visible): 313-429 inliers, verified. TC vs MI 1548 nm
  (infrared): the matcher fails (5-6 inliers), the area check contradicts it in all three windows,
  the fallback lands 0.58-1.13 MI px (8.5-16.7 m) from the visible-band solution.
- **Archive disagreement found**: LROC NAC corners (0.01 deg) are off ~150 m and drift along the
  strip; the two Kaguya map products disagree by ~40 m here; TC morning and evening maps are the
  SAME pixels at this latitude (not a sun pair - not used).

## Running / pending at the end of the session

- `ops/cut_site_pairs.py --correct-chain` over the 30 sweep NACs (28 done; M1258744166RE and
  M1295016540LE could not be corrected - record as such).
- `ops/trust_real_calibration.py` on the 18 loop legs + 5 verified windows -> `evaluation/trust_real_calibration.csv`.
- Next: `python -m ops.sun_sweep --windows 3 --log`; the synthetic viewpoint sweep
  (`python -m core.pipeline --synthetic --dem <data>/raw/dem_site_60m.npy --pixel-size 60
  --sun-delta 15 --tilt-sweep 0,10,20,30,40,50 --repeats 3 --log --allow-failed`, with and without
  `--parallax`); then deck figures from the logs.

## Known issues - do not re-report these

1. **The sun sweep's first judging rule was wrong** (archive geometry as truth); it is now image
   evidence, explained in `ops/sun_sweep.py`. The trust layer's detection rate comes ONLY from the
   planted-failure calibration, never from the sweep.
2. **Evidence freeze**: every deck number must be re-run on the final commit (Day 7) so the deck
   cites one code version; rows logged today carry their commit in real_pairs_log.
3. PowerPoint on this machine is unlicensed; PDF via Print to PDF or another machine.
4. `docs/00_CANONICAL_FACTS.md` and `CLAUDE.md` still describe the college round (9 Sep, gates);
   they are stale, not wrong about the invariants.
