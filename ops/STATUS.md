# STATUS - 20 September 2026 (Day 23), ~12:45 IST, audit second pass wrapped. National round, solo push.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM - read with `utf-8-sig`).
> Set `PYTHONIOENCODING=utf-8` for scripts that print → ° ↔ (cp1252 console crashes on them).

---

## Read this first

1. **The audit ran in two passes** (20 Sep, 02:30-05:00 and 09:00-12:45):
   `ops/national_round/AUDIT_REPORT.md`. The second pass found and fixed a blocker, added two
   measured results, and forced a second re-freeze.
   - **F12, the blocker (fixed).** `is_inlier` in the exported match table was decided by
     comparing float64 match coordinates against their float32 copies, so **41 of 183 bundles
     flagged ZERO inliers** and shipped empty `gcps.txt`, `gcps.points` and `matches_isis.csv` -
     deliverables the problem statement names. `core/ransac.py` now returns MAGSAC++'s own mask
     and `core/export.py` uses it. Every metric had stayed right, because nothing else asked that
     question; loop closure moved ~2 % because it is the one number read back from that file.
   - **E5, trust against non-translation errors.** Planted rotation and scale, 420 trials:
     **94.1 %** of the cells they moved past 2 px lost verified state (pre-registered bar 90 %),
     and 87.4 % of the cells they moved less than 1 px stayed verified (bar 80 %). On slide 5.
   - **E7, the whole lit overlap tiled.** Every non-overlapping 640-px window the cutter finds in
     shared, lit, textured ground of the 74 °S OHRC ↔ NAC overlap: **37 windows, 13.1 km²,
     37/37 accepted**, held-out median 0.61 px = 0.57 m. On slide 4, and it replaced the
     hand-picked 20-window range - it answers "did you pick the windows that worked?".
   - **E6 dropped and E8 ruled out**, both honestly: E6 could have produced a pixel figure below
     SuperGlue's but not by a method we could defend; E8 fails on physics (every available DEM is
     50-240× coarser than the imagery). Reasons in AUDIT_REPORT.md.
2. **The evidence freeze is DONE: FROZEN at `7dd4e5b`** (10/10 steps). 183/183 real rows,
   324/324 MiLOI rows, 8/8 multi-modal rows name it. Every per-pair number reproduced the
   `b678272` values exactly except loop closure, which is the one the F12 fix predicts.
   `--check` at a later HEAD says NOT FROZEN because the rows name `7dd4e5b`, not HEAD; the test
   that matters is `git diff 7dd4e5b HEAD -- core evaluation ops baselines app` showing only docs.
   **It took three attempts** - two crashes in code that only runs at the end of the job. Both
   causes are fixed and tested; see Known issues 7 and 18.
3. **The deck is v4; the PDF is final.** `build_deck`: `AUDIT: clean`; `export_pdf`:
   `PDF CHECK: clean`, 6 pages, 1,112,713 bytes, sha256 `510a5c50…` (12:46 IST). All six pages
   rendered at 150 dpi and read. Six numbers moved from v3 and two clauses were added; every value
   and its source is in `presentation/DECK_V2_DRAFT.md`.
   **`claim-checker` ran on v4: 0 fabricated numbers, all six changed values confirmed.** Its
   2 HIGH / 8 MEDIUM / 4 LOW findings were all on nouns, scope and labels; each was verified
   against REPORT.md by hand and then applied, except one that was declined on the record
   (AUDIT_REPORT.md). The two that mattered: slide 4 said "160 real window pairs" when REPORT
   says 177 pairs / **160 distinct ground windows**; and slide 5 said rotation and scale "behave
   the same way" as translation, which the frame column disproves (10-15 % contradicted at 5 m
   against 100 % for a shift) - it now says "caught cell by cell, not by the frame verdict".
   It also caught that **REPORT.md was still uncommitted**, so the deck's numbers pointed at no
   commit a judge could open. Committed now. `ops.freeze --check` does not test for this.
   **Safety net:** tag `submission-v1` = `0297936` (the pre-audit deck) and
   `presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf` (gitignored).
4. **Slides 2, 4 and 5 are full.** Body text is 11.5 / 12 pt. Slide 4 overflowed twice during the
   refill and one bullet had to be removed to fit the tiling clause. Only slide 6 has room left
   (for a demo-video link). `export_pdf`'s footer check is the only thing that sees this -
   `build_deck`'s audit measures text boxes, not rendered text (Known issue 11).
5. **Demo: the six caches were rebuilt at `f928995`** - four of them predated the F12 fix and
   carried its bug. All six identification plates are clean (no "CODE IS NOW" caution), and three
   consecutive AppTest runs of the four demo pairs passed with sockets blocked. Gate 4 by hand is
   still a human job.
6. **Backups are current**: `C:\sih26166_backup\` has `weights/`, `data/pairs/` and `demo_cache/`
   (165 files, 94.8 MB, 12:36). **Not yet on a USB stick** - that is step 0 of `day_24.md`.
7. **Portal text** (`ops/national_round/SUBMISSION_FIELDS.md`) is refilled at `7dd4e5b`; its
   character counts were recounted (the stated "1,322" had been stale by 228).

## Position

```
Sun 20 Sep, 12:45  |  submit Sun 27 Sep (7 days)  |  portal closes Tue 30 Sep
Built: everything, PDF v4 final. Left: read the PDF -> portal -> upload (Samartha, ~15 min)
Optional, measurable: the closer-Sun TMC-2 pass (needs a PRADAN download) - ops/specs/day_24.md
Evidence cut-off Thu 24 Sep 18:00 | deck and portal text final Fri 25 Sep 22:00
```

## Verified by command (20 Sep, 12:00-12:45, at `7dd4e5b` + docs)

| Check | Result |
|---|---|
| `python -m ops.freeze --check` at `7dd4e5b` | FROZEN, 10/10 steps |
| `python -m pytest -q` (whole repo) | **340 passed** in 13.7 s |
| `python -m presentation.make_figures` | 7 figures; fig6 counts translations only, pinned by a test |
| `python -m presentation.build_deck` | 6 slides, pointers unchanged, AUDIT: clean |
| `python -m presentation.export_pdf` | 6 pages at 792×446 pt; PDF CHECK: clean (3 footer overflows caught and fixed first; two "NO PDF" retries - Known issue 17) |
| All six pages rendered at 150 dpi and read | clean; title page carries LunaXX / SNPSU0192 / SIH26166 |
| `claim-checker` on deck v4, portal text and README | 0 fabricated numbers; 2 HIGH / 8 MEDIUM / 4 LOW on nouns, scope and labels, all verified by hand, 13 applied and 1 declined on the record |
| `ops.precompute_demo_cache` (six pairs, named) | all at `f928995`; flagged inliers == `ransac.inlier_count` on every one (F12 verified in the caches) |
| AppTest, 4 pairs × 3 runs, sockets blocked | 3 consecutive clean runs, all cached |
| `robocopy demo_cache C:\sih26166_backup\demo_cache /E` | 165 files, 94.8 MB, 0 failed |

## Evidence at the freeze (REPORT.md, `7dd4e5b`)

- **SAC equatorial:** 6/6 accepted, Sun azimuths 174° apart, held-out median 0.69-1.68 px on the
  1.622 m grid. In-sample per axis X 0.66-1.15 / Y 0.73-1.07 px: not better than SuperGlue's
  0.62 / 0.57 px (Q&A only).
- **SAC polar:** 4/6 accepted, 1 unconfirmed, 1 contradicted + fallback.
- **74 °S OHRC → NAC, whole overlap tiled:** 37 windows, 13.1 km², **37/37 accepted**, held-out
  median 0.61 px = 0.57 m on the 0.931 m grid, 36 of 37 under 3 px. The 20 hand-picked windows of
  the same site: 20/20, 0.41-1.0 px (0.51-0.94 m). Loops: 6, median **0.107 m = 0.086 px** on 1.245 m.
- **Sun sweep:** 69 windows, 25 NAC frames, 3.3-152.7°.
- **TC rung:** 3/4. **Infrared:** MI 1548 nm 3/3 refused, fallback 0.23-1.09 px (3.4-16.2 m) from
  the visible band; IIRS 10/11 refused, none registers. **OHRC → TMC-2:** 0/4.
- **Trust, 22 windows ≤ 10°:** 0/44 false alarms; 74 % at 3 m; 100 % from 5 m; **0/352** at 1-2 m.
  **8 SAC windows 132-174°:** 0/16; **84 %** at 5 m; 100 % from 10 m. Never pool the two.
- **Trust, rotation and scale (new):** 94.1 % of cells moved >2 px lose verified state;
  87.4 % of cells moved <1 px keep it. Cells, not frames - a rotation is not uniform over a frame.
- **MiLOI:** 81 scored pairs, 56 in S3; agrees 33/33 right, contradicted 43/43 wrong, unconfirmed 5/5.
- **Sub-pixel by grid:** 0.086 px / 60 m (exact truth); 0.61 px / 0.93 m (held out, tiled);
  0.086 px / 1.245 m (loops, consistency); MiLOI S1 0.52 px / 1.1-1.5 m (truth 0.22 px).
- **Runtime:** median **8.2 s** per 640-px window (89 OHRC → NAC windows), CPU only. Wall time:
  10.0, 10.7 and 8.2 s over three freezes on this machine - quote the frozen one, say "about ten
  seconds" in speech.
- **Coverage:** 177 registered pairs = **160 distinct ground windows**, 8 instrument pairings.

## In flight - resume here

Nothing is running. No PowerPoint process is left open.

## Samartha - to submit (ops/specs/day_24.md has the full list)

1. Put `C:\sih26166_backup\` on a USB stick. Nothing else here is unrecoverable.
2. Read the v4 PDF cold, all six pages.
3. Portal: PS, title and description from `SUBMISSION_FIELDS.md`; upload the PDF; screenshot.
4. Optional and measurable: download the TMC-2 pass `ch2_tmc_ncn_20251107T2205342105_d_img_d18`
   (PRADAN login) - the only pass over SAC's frame with the Sun near the OHRC's; the cut command
   is ready (`--tmc-product`). Cut-off Thu 24 Sep 18:00.
5. Optional: demo video; repo public + link on slide 6; Gate 4 by hand.

## Open questions

1. Portal: draft save? editable after submit? title/description limits? (the long description is
   1,648 characters - if there is a 1,500 cap, the short one is ready)
2. SPOC: Student Innovation and the two-PS cap; who uploads; authorisation letter.

## Known issues - do not re-report these

1. **`residual_px` is meaningless on real pairs** (RMSE over all held-out matches). Quote
   `residual_median_px` or `holdout_inlier_rmse_px` (capped at 3 px). And the held-out median
   itself is only robust while the inlier ratio is well above 0.5 - one tiled window reports
   316 px at a ratio of 0.542 with the alignment visibly correct (NCC +0.87 to +0.95).
2. **Duplicate windows under two ids:** `…_w0N_sw` = `…_w0N`, `…_w01_t` = `…_w04`. Count distinct
   windows with `presentation.make_figures._distinct_windows` (160 of 177).
3. **MiLOI truth:** 81 of 321 pairs reachable; S3 (56 of 81) has no redundancy. The contradicted
   pairs' errors start at 7.4 px, so the cross-tab survives any truth error under ~4 px.
4. **LoFTR is weak under near-overhead Sun** (MiLOI S2). The trust layer catches it.
5. **Withdrawn rows:** `sac_tmc_fore_aft_w01..w04` are INVALIDATED. Never quote 0.019 px.
6. **NACs without a usable correction:** M1258744166RE, M1295016540LE, M1338673330RE (Sun
   azimuths 37°, 117°, 153° from the OHRC's). **No lit shared window:** M159642518LE, M1258737127RE.
7. **`trust_real_calibration.csv` is appended by every run** and refuses a header mismatch;
   `ops.freeze` deletes it first. Its trials draw from ONE RNG stream in window order, so changing
   the trial list redraws every planted direction: the 3 m rate has been 81 %, 74 % and 74 %, the
   1-2 m rate 2/352, 1/352 and 0/352, and the hard-Sun 5 m rate 94 % and 84 %. These are draws of
   one experiment, not a regression. Quote the frozen values; hedge in speech.
8. **Memory:** commit charge runs at 40-50 of 53 GB; run heavy jobs one at a time.
9. **The MiLOI matches were made at six earlier commits**; only the re-judge and scoring ran at
   `7dd4e5b`. `--plan` verifies the matching code is unchanged.
10. **Pairs cut before `3917a1b`** have up to 16 nearest-filled edge pixels. Negligible.
11. **The build audit checks text boxes, not rendered text**; `export_pdf`'s footer check is the
    real test. Always export before trusting a deck edit. Slides 2, 4 and 5 are at capacity.
12. **Live align on a busy laptop takes 48-61 s**; demo from the cached pairs.
13. **The commit stamp of the multi-modal rows and REPORT.md's header include `ops/`**: any
    modified file under `ops/` (docs included) at run time stamps them `-dirty`. Park doc edits
    outside `ops/` while a freeze runs. The demo cache's stamp is `core`/`evaluation`/`app`.
14. **13 pair folders have no images** (`site_m…re_w01..05,07,08`,
    `site_ohrc_m1363141432re_w01,02,03,05,07,08`). The picker hides them.
15. **Docs below the national-round sections** (CLAUDE.md, canonical facts §1 and §10-11) are
    the college round's, kept as history.
16. **`ops.precompute_demo_cache` with no arguments caches every pair** (~150 × LoFTR, GBs of
    pickles). Always name the pairs.
17. **`export_pdf` intermittently prints nothing** ("printing failed: NO PDF", then a
    PermissionError on the temp dir): roughly every other attempt. Kill POWERPNT, wait 10-20 s,
    run it again; it never produced a wrong PDF, only no PDF. Check the PDF's mtime is later than
    the .pptx's before uploading.
18. **F18: `ops.freeze`'s `trust` step takes its window list from the CSV it then deletes.** Lose
    that file and the step fails in seconds with a zero-byte log and no cause recorded. This cost
    a freeze on 20 Sep. **F19: the freeze's summary line adds `None` to an int** when a step
    returns the precondition-failed sentinel, so a completed run ends in a traceback. Both are
    `ops/` changes that would force another freeze; both are first in line after submission.
19. **Two orphan bundles** (`site_tc_ortho_mi1548_w01`, `site_tc_ortho_mi749_w01`, commit
    `057664a-dirty`) still show the F12 signature. They are in no log and referenced by nothing;
    all 177 current bundles are clean. Do not quote them.
