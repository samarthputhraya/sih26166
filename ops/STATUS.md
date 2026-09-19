# STATUS - 19 September 2026 (Day 21), ~11:15 IST. National round, solo push.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM - read with `utf-8-sig`).
> **Keep the laptop from sleeping during long runs** - on 19 Sep 02:00-10:00 every background job paused.

---

## Read this first

1. **The trust layer changed (`ac4524b`)**: the area check also correlates INVERTED intensity. Opposite
   suns anti-correlate a correct alignment; before this, every real window at 131-152 deg was refused.
   Measured before landing: planted-failure calibration identical (1,702 trials: 0 % false alarms at
   0-2 m, 81.5 % caught at 3 m, 100 % at >= 5 m); the sweep's false alarms fell 12 -> 2. Every number
   produced before `ac4524b` that involves a trust verdict is superseded - the freeze reruns all.
2. **MiLOI is scored** (`evaluation/miloi_log.csv`, REPORT.md section). Its truth is a translation
   network from ours+SIFT agreement, because the tiles' map geometry is off by 4-253 m. Only 81 of 321
   pairs have truth; S3's truth error is NOT measurable (tree network). Ours is roughly level with
   AKAZE/SIFT up to 60 deg, slightly ahead at 60-90 deg (2/18 vs 0), and nothing works > 90 deg there.
   Trust vs truth: `agrees` 33/33 right, `contradicted` 43/43 wrong, `unconfirmed` 5/5 wrong.
3. **PRADAN is done** (registered 18 Sep). No TMC-2 strip covers our 74 S site; TMC-2 is used at SAC's
   own benchmark OHRC frame instead. IIRS: 4 bands streamed out of the zip by HTTP range (full file
   never downloaded). Everything, with sha256: `ops/national_round/PRADAN_GUIDE.md` section 3a.
4. **SIH26227**: session 2 exists (`C:\Users\samar\dev\sih26227`); go/no-go is **Fri 25 Sep evening**.
5. Deck title slide still says `SNPSU0192` / `SNPSU LunaX` (`presentation/build_deck.py:81-82`); the
   portal name is **LunaXX**.

## Position

```
Day 21 (Sat 19 Sep)  |  submit Sun 27 Sep - 8 days  |  portal closes 30 Sep
Next: Thu 24 Sep evidence freeze begins | Fri 25 Sep SIH26227 go/no-go + numbers frozen
```

## Verified by command (19 Sep, ~11:00)

| Check | Result |
|---|---|
| `python -m pytest -q` (whole repo) | **281 passed**, exit 0 (at `ac4524b`) |
| `python -m ops.make_report` | REPORT.md, 13 sections, every number from the logs |
| `python -m presentation.make_figures` | fig1 unchanged (15 deg ours 0.086 px); fig5, fig6 rewritten |

## What landed (18 Sep evening - 19 Sep, commits `a4f7838`..HEAD)

| Area | What |
|---|---|
| Provenance | `core.export._commit()` ignores the append-only logs (every row used to say `-dirty`) |
| Sweep rule v2 | `ops/sun_sweep.py`: |NCC|, "at least as good as archive", `inconclusive`; `--rerun` |
| Trust layer | `core/reliability.best_peak` + `_fallback`: inverted intensity (see Read-first 1) |
| Safety | `resolve_pair` never uses one file as both source and reference (test); `run_all(matches=)` |
| MiLOI | `evaluation/miloi.py`: `--run`, `--retrust`, `--truth`, `--score --log`, `--table`; 321 pairs |
| PRADAN pairs | `ops/cut_pradan_pairs.py` (local equirectangular at 13 S): OHRC vs TMC-2, TMC-2 fore vs aft |
| IIRS | `ops/cut_site_pairs.py` kind `iirs<nm>` (per-band files); IIRS vs Kaguya TC at 74 S |
| Viewpoint | synthetic tilt sweep logged (tilt <= 40 deg median <= 0.26 px; 50 deg 0.61 px; parallax 2.3-16 px) |
| Report/figs | MiLOI, SAC, fore/aft, IIRS sections; pair kind from product ids; fig1 no longer reads viewpoint rows |

## Evidence logged (results_log 843 rows; real_pairs_log 203; miloi_log 324)

- **Sun sweep (re-logged at `ac4524b`, 69 windows)**: 51 correct_accepted, 2 false_alarm,
  15 inconclusive, 1 caught_failure, **0 missed_failure**.
- **SAC site, OHRC vs TMC-2 nadir** (4 windows): matcher fails (6-7 inliers), all contradicted,
  fallback declared - a correct refusal (sun elev 9.9 vs 69.4 deg, azimuths 120 deg apart).
- **SAC site, TMC-2 fore vs aft** (4 windows, real viewpoint ~50 deg): 52-368 inliers, held-out inlier
  RMSE ~1.85 px (~11 m) on the 5.9 m grid; 1 agrees, 3 unconfirmed; archive disagreement 96-1,078 m.
- **IIRS 999/1555 nm vs Kaguya TC at 74 S** (11 windows): matcher fails (4-7 inliers), 10 contradicted,
  1 `agrees` on a 112-px frame (see Known issue 3).
- **MiLOI**: see Read-first 2 and REPORT.md.

## Tomorrow / next

1. Scale rungs: OHRC <-> Kaguya TC (40.8x; chunked reference) and OHRC <-> LOLA (declared failure).
2. SAC's own pair: fetch LRO NAC `M1350459544RE` (public) and cut OHRC <-> NAC at the SAC frame;
   same for `M165491149RE` vs the 2020-08-24 OHRC (61.5-62.4 S).
3. Fix Known issue 3 (tiny-frame verdict) before any IIRS number is quoted.
4. Deck v2 text from REPORT.md; title slide fix; `claim-checker`.
5. Freeze plan (Thu 24): rerun synthetic trust calibration (`core/reliability_calibrate.py`, fig2 -
   predates `ac4524b`), real calibration, sweep, MiLOI `--retrust --score`, every pair, on one commit.

## Open questions

1. Portal: draft save? editable after submit? title/description limits? exact Team ID / PS-ID format?
2. SPOC: does Student Innovation count toward the two PSs? who uploads? authorisation letter uploaded?

## Known issues - do not re-report these

1. **`residual_px` is meaningless on real pairs** (RMSE over ALL held-out matches incl. outliers). Quote
   `residual_median_px` / `holdout_inlier_rmse_px`.
2. **Duplicate windows under two ids**: the sweep's `site_ohrc_m1153871873le_w0k_sw` are the same windows
   as `site_ohrc_m1153871873le_w0k`. Count distinct windows, not rows.
3. **Tiny frames decide on the whole frame**: a reference under ~8 x MIN_CELL_SIDE_PX has 0 measurable
   cells; `site_tc_ortho_iirs1555_w10` got `agrees` on 6 inliers and a 2 km archive offset. A frame with
   no measurable cells and few inliers should be `unconfirmed`. Not fixed.
4. **MiLOI truth**: only 81/321 pairs reachable; S3 (polar) truth has no redundancy, so its error is
   unknown - quote S3 separately and say so. The 5 `missed_failure` are all `unconfirmed` (3.2-9.1 px).
5. **LoFTR is weak under near-overhead sun** (MiLOI S2, Apollo 11 site): 12-14 inliers where SIFT/ORB/
   AKAZE get 170-320 on some pairs; the trust layer catches it.
6. **Withdrawn rows**: `sac_tmc_fore_aft_w01..w04` (18 Sep 21:4x) registered the reference against
   itself; superseded by INVALIDATED rows; real pairs are `sac_tmcfore_tmcaft_w0N`. Never quote 0.019 px.
7. **NACs without a usable correction** (`apply=false`): M1258744166RE, M1295016540LE, M1338673330RE.
   **No lit shared window:** M159642518LE, M1258737127RE.
8. `trust_real_calibration.csv` is appended by every run - delete it before a deliberate rerun.
9. Plan W8 (tiled driver) not built; the 40.8x OHRC<->TC rung needs it or a chunked reference.
10. Every deck number must be re-run on the final commit (evidence freeze).
11. Fresh scratch Python processes intermittently die in `cv2.resize` ("Unknown C++ exception"); not an
    import-order bug; wrap `run_all`/`warp` in a retry in scratch runners.
12. PowerPoint on this machine is unlicensed; PDF via Print to PDF or another machine.
13. `docs/00_CANONICAL_FACTS.md`, `CLAUDE.md`, `ops/specs/day_20.md` describe the college round; stale.
