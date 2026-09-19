# STATUS - 19 September 2026 (Day 21), ~22:15 IST, session wrapped. National round, solo push.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM - read with `utf-8-sig`).
> Set `PYTHONIOENCODING=utf-8` for scripts that print → ° ↔ (cp1252 console crashes on them).

---

## Read this first

1. **The evidence freeze is one command now: `python -m ops.freeze`** (`b325a60`..`bae82b2`).
   - `--plan` shows the work and last run times.
   - `--check` says whether every latest row names the current commit.
   - The work list is read from the logs by EXACT pair id. It is resumable per step and per pair.
   - It keeps Windows awake while running (lid must stay open). State and per-step logs live in
     `<data>/freeze/<commit>/`.
   - Steps: real (71 pairs) · sweep (69 windows) · loops · trust (22 distinct windows) · miloi
     (retrust, truth, score) · viewpoint · calib · gate2 · report.
   - Last-run estimate: real ~13 min, sweep ~15 min.
   - Tested end to end only on `loops`, which correctly refused because its legs were at an older
     commit. It has NOT been run in full: that is tomorrow's item 1.
2. **SAC's own benchmark pairs are registered** (arXiv:2509.04775, Table 1).
   - Equatorial (`M1350459544RE`, Sun azimuths 174° apart): 6/6 `agrees`, 3.2-4.2k inliers.
   - Polar (`M165491149RE`, 132°): 4 agree, 1 unconfirmed, 1 contradicted (fallback).
   - The NAC's published corners sat (+488, +1790) m from the OHRC grid at the equatorial site.
     The new wide search (`cut_pradan_pairs.wide_offset`) fixes that. REPORT.md has both sections.
3. **Deck v2 text is in `presentation/build_deck.py`**; output `SIH26166_LunaXX_deck.pptx`.
   - Every number is `[TBD]`: 44 across slides 2, 4 and 5, plus the Team ID.
   - `presentation/DECK_V2_DRAFT.md` maps each placeholder to its REPORT.md source and lists the
     Q&A traps.
   - `claim-checker` ran and all 19 findings were fixed (`64760ab`).
   - The build exits 1 on purpose until the freeze fills the placeholders.
4. **Trust layer, Known issue 3 fixed** (`1c21e18`). A whole-frame "agrees" on a frame too small for
   cells to vote now also needs the Brown & Lowe inlier count; otherwise it is "unconfirmed".
   - IIRS `iirs1555_w10` is now unconfirmed.
   - The MiLOI re-judge changed 0 of 321 verdicts; the Tier D pair is unchanged.
5. **Deck title slide now says `LunaXX`.** The Team ID is a placeholder until read off the portal.

## Position

```
Day 21 (Sat 19 Sep)  |  submit Sun 27 Sep - 8 days  |  portal closes Tue 30 Sep
Next: Sun 20 freeze REHEARSAL | Thu 24 the freeze | Fri 25 deck numbers + SIH26227 go/no-go
```
The college-round gates are all past (internal round 11 Sep; nominated 18 Sep). Nothing for the
national round is at risk tonight. The riskiest item is the untested full freeze run, hence the
rehearsal.

## Verified by command (19 Sep, ~22:10, at `bae82b2`)

| Check | Result |
|---|---|
| `python -m pytest evaluation/ -q` | 42 passed, exit 0 |
| `import core.pipeline` | OK, exit 0 |
| `python -m pytest -q` (whole repo, now includes `ops/`) | 291 passed, exit 0 |
| `python -m presentation.make_figures` | 7 figures, audit clean |
| `python -m presentation.build_deck` | 6 slides, pointers unchanged; 4 audit lines, all `[TBD]` counts (by design) |
| `python -m ops.freeze --plan` | code clean; MiLOI matching code unchanged since the stored matches |

## What landed this session (`1c21e18`..`bae82b2`, 13 commits, not yet pushed at time of writing)

| Area | What |
|---|---|
| Trust layer | Brown & Lowe floor for whole-frame agrees (`core/reliability.py` FRAME_ACCEPT_*); tests |
| SAC pairs | `ops/cut_pradan_pairs.py` kinds `ohrc-nac`, `ohrc-nac-polar`; `wide_offset`; NAC pages `<data>/nac/nac_sac_pages.json`; EDR sha256 `<data>/nac_sac_manifest_done.csv`; corrections `<data>/site_geometry/M1350459544RE.json`, `M165491149RE.json` |
| Scale rungs | `cut_site_pairs` kinds `tc_ortho` (from OHRC) and `lola` (shaded relief under the OHRC's sun); 4 + 4 windows logged |
| Geometry | `core.geometry.project`: border value 0 and a geometric validity test. OpenCV 5's cubic remap with a NaN border blanked interior rows. Test: `core/test_geometry.py` |
| Figures | fig7 (MiLOI); fig3 on real pairs (SAC accepted / TC→MI 1548 nm refused); fig4 order (refine before MAGSAC++); fig6 names both grids and counts distinct windows |
| Report | SAC, scale-rung and LOLA sections; sweep azimuth range; both MiLOI "right" definitions; footer count fixed |
| Freeze | `ops/freeze.py` + tests. MiLOI `--score --log` dedupes per SCORING commit (it used to log nothing on a re-score). `run_real_pairs` takes several ids. Generated evidence files don't stamp `-dirty`. Loop rows carry `git_commit` |
| Deck | v2 text, LunaXX, audit counts `[TBD]`s and checks same-sensor wording; `DECK_V2_DRAFT.md` rewritten as the numbers audit |

## Evidence logged (results_log 874 rows · real_pairs_log 234 rows, 150 pair ids · miloi_log 324 · trust trials 1,702)

- **SAC equatorial:** 6/6 agree. Held-out median 0.69-1.68 px on the 1.62 m NAC grid.
- **SAC polar:** held-out median 2.4-4.5 px on the 1.22 m grid (accepted windows); w06 is 88.5 px,
  contradicted, fallback.
- **OHRC → TC ortho (29.6×):** 3 agree, 1 unconfirmed. Archive offset 381-431 m, consistent across
  all 4 windows.
- **OHRC → LOLA (240×):** 0 matches, fallback, unconfirmed (the declared failure).
- **IIRS re-logged:** 10 contradicted + fallback, 1 unconfirmed (w10).
- **MiLOI verdict vs truth:** agrees 33/33 by matcher-H error, but 28/33 by `rmse_gt_px`.
  Contradicted 43/43 wrong; unconfirmed 5/5 wrong. S3 accounts for 13, 38 and 5 of those.
- **Everything else** (sun sweep 69 windows, loops 0.104 m median, planted failures) is unchanged
  from 18-19 Sep. It is all re-run at the freeze.

## In flight - resume here

Nothing is running and the tree is clean at wrap.
- **First thing: `ops/specs/day_22.md` item 1**, the full freeze rehearsal.
- `demo_cache/results/` now also holds `sac_ohrc_nac_w06` and `site_tc_morning_mi1548_w01` (fig3's
  pairs; gitignored; `ops.freeze` re-caches them).
- The automation Chrome window may still be logged in to PRADAN; it can be closed.

## Per person

The team split is suspended for the national push (decision 18 Sep). No teammate has a task and
nobody is blocked on Samartha. The last teammate pushes were 2-3 Sep (Rohan 2 Sep; Risheeth,
Samrudh, Rishabh 3 Sep; Saniya earlier), so nobody can explain the national-round code yet. Plan a
walkthrough after submission (27 Sep) in case LunaXX reaches the finale.

## Tomorrow - `ops/specs/day_22.md`

1. Freeze rehearsal, overnight. 2. `demo-medic` on the app. 3. (Optional) a logged, SAC-comparable
in-sample per-axis RMSE for Q&A. 4. A short "national round" note in CLAUDE.md and the canonical
facts. Track B: SIH26227 continues.

## Open questions

1. Portal: draft save? Editable after submit? Title/description limits? Exact Team ID format
   (slide 1 placeholder)?
2. SPOC: does Student Innovation count toward the two PSs? Who uploads? Is the authorisation
   letter uploaded?

## Known issues - do not re-report these

1. **`residual_px` is meaningless on real pairs** (RMSE over ALL held-out matches, outliers
   included). Quote `residual_median_px`, or `holdout_inlier_rmse_px`. The latter is capped at 3 px
   by definition, so it can never show parallax.
2. **Duplicate windows under two ids.** The sweep's `site_ohrc_m1153871873le_w0N_sw` are the same
   windows as `…_w0N`, and `…_w01_t` = `…_w04`. Count distinct windows
   (`presentation.make_figures._distinct_windows`), not rows. The freeze's trust step drops the
   duplicate.
3. ~~Tiny frames decide on the whole frame~~: FIXED `1c21e18`.
4. **MiLOI truth:** only 81/321 pairs are reachable. S3's truth has no redundancy, so its error is
   unknown; quote S3 separately. MiLOI "right" has two definitions (see Evidence); the deck uses
   matcher-H error.
5. **LoFTR is weak under near-overhead Sun** (MiLOI S2): the trust layer catches it.
6. **Withdrawn rows:** `sac_tmc_fore_aft_w01..w04` (INVALIDATED). Never quote 0.019 px.
7. **NACs without a usable correction:** M1258744166RE, M1295016540LE, M1338673330RE. **No lit
   shared window:** M159642518LE, M1258737127RE.
8. `trust_real_calibration.csv` is appended by every run. `ops.freeze` deletes it first; do the
   same by hand.
9. **Rows from before the freeze name many commits.** The 12 SAC rows say `1c21e18-dirty`, and
   loop rows before 19 Sep have no `git_commit` at all. The freeze fixes both.
10. **Every deck number must come from the freeze commit.** 44 `[TBD]`s, mapped in
    `DECK_V2_DRAFT.md`.
11. **Fresh Python processes intermittently die in `cv2.resize`** ("Unknown C++ exception"). Not an
    import-order bug. `ops.freeze` retries a failed step once. Related: one full `pytest` run at
    ~22:05 on 19 Sep had 62 failures and did not reproduce in 4 reruns. No output was captured; if
    it recurs, run with `-rf` and keep the output.
12. **PowerPoint on this machine is unlicensed.** Make the PDF via Print to PDF or another machine.
13. **Stale docs:** `docs/00_CANONICAL_FACTS.md`, `CLAUDE.md` and `ops/specs/day_20.md` describe
    the college round (day_22 item 4).
14. **Pairs cut before `3917a1b` have up to 16 nearest-filled edge pixels** (`edge_pixels_filled`
    in their geometry_prior.json), from the OpenCV NaN-border quirk. It is recorded, negligible,
    and not re-cut.
15. **REPORT.md's SAC sections say "NAC at native"**; the cut grids are 1.622 and 1.215 m, while
    SAC's paper used 1.1179 and 0.88779 m. Any SuperGlue comparison differs in grid as well as in
    in-sample vs held-out.
