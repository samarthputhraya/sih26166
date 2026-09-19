# STATUS - 20 September 2026 (Day 23), ~05:00 IST, audit session wrapped. National round, solo push.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM - read with `utf-8-sig`).
> Set `PYTHONIOENCODING=utf-8` for scripts that print → ° ↔ (cp1252 console crashes on them).

---

## Read this first

1. **The audit ran (20 Sep, 02:30-05:00): `ops/national_round/AUDIT_REPORT.md`.** Every deck
   number was re-derived from the CSV cells (0 mismatches), the code was read, the deliverables
   checked numerically, and two evidence extensions were pre-registered, run and frozen:
   - **E1, multi-modal measured**: on the three TC → MI 1548 nm windows the declared fallback
     lands 0.23-1.09 px (3.4-16 m) from the LoFTR registration of the visible 749 nm band of the
     same window (`ops/multimodal_check.py`, `evaluation/multimodal_check.csv`, freeze step
     `mmcheck`). The IIRS fallbacks disagree between bands by up to 3.4 km: still a declared failure.
   - **E2, trust calibration on hard Sun**: SAC's own pairs (Sun azimuths 132-174°, 8 windows)
     added as a second population: 0/16 false alarms, 94 % flagged at 5 m, 100 % from 10 m.
     Window selection now uses |NCC| ≥ 0.5 (opposite Suns anti-correlate). The 22-window
     population's 3 m rate moved 81 % → **74 %** (a second random draw of the planted directions;
     both draws are recorded). Never pool the two populations.
   - Reporting-only: REPORT.md gained "Sub-pixel accuracy, with the pixel grid named" and
     "Runtime and match distribution" (10.7 s median per 640-px window).
2. **The evidence freeze is DONE: FROZEN at `b678272`** (10/10 steps, 90 min, 20 Sep 02:57-04:27).
   146/146 real rows, 324/324 MiLOI rows, 8/8 multi-modal rows name it. All 146 registration rows
   reproduced the `49bdad9` numbers exactly. `--check` at a later HEAD says NOT FROZEN because
   the rows name `b678272`, not HEAD; the test that matters is
   `git diff b678272 HEAD -- core evaluation ops baselines app` showing only docs and evidence.
3. **The deck is v3; the PDF is final.** All numbers filled from REPORT.md at `b678272`; each
   value and its source in `presentation/DECK_V2_DRAFT.md` (rows added for the multi-modal,
   hard-Sun, sub-pixel and runtime figures; Q&A answers for every disclosed weakness).
   `build_deck`: `AUDIT: clean`; `export_pdf`: `PDF CHECK: clean`, 6 pages, 1,112,452 bytes,
   sha256 `86ac52fd…` (05:06 IST). `claim-checker` ran on v3: 0 numeric mismatches; its HIGH and
   MEDIUM findings were applied before this export (AUDIT_REPORT.md lists them).
   **Safety net:** tag `submission-v1` = `0297936` (the pre-audit deck) and
   `presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf` (gitignored).
4. **Slides 2 and 4 body text is 11.5 / 12 pt** (was 12.5 / 13): the new clauses did not fit;
   nothing more can be added to them.
5. **Demo:** the six demo caches are at `b678272`; three consecutive AppTest runs of the four
   demo pairs passed with sockets blocked (0.8-2.4 s per cached align). Gate 4 by hand is still
   a human job.
6. **Portal text** (`ops/national_round/SUBMISSION_FIELDS.md`) carries the new sentences.

## Position

```
Sun 20 Sep, 05:00  |  submit Sun 27 Sep (7 days)  |  portal closes Tue 30 Sep
Built: everything, PDF v3 final. Left: read the PDF -> portal -> upload (Samartha, ~15 min)
Optional, measurable: the closer-Sun TMC-2 pass (needs a PRADAN download) - ops/specs/day_24.md
```

## Verified by command (20 Sep, 04:30-05:00, at `b678272` + docs)

| Check | Result |
|---|---|
| `python -m ops.freeze` at `b678272` | 10/10 steps ok in 90 min; `--check`: FROZEN |
| `python -m pytest -q` (whole repo, alone, before the freeze) | 302 passed |
| `python -m presentation.make_figures` | 7 figures; fig6 shows both Sun populations |
| `python -m presentation.build_deck` | 6 slides, pointers unchanged, AUDIT: clean |
| `python -m presentation.export_pdf` | 6 pages at 792×446 pt; PDF CHECK: clean (the print step failed with "NO PDF" on 4 of 9 attempts today and succeeded on retry - see Known issue 17) |
| AppTest, 4 pairs × 3 runs, sockets blocked | all clean, cached |
| Deliverables (`out/sac_ohrc_nac_w01`) | GeoTIFF tags identical to the reference's; GCP line re-derived by hand |

## What landed this session (`6a5686b`..)

| Commit | What |
|---|---|
| `b678272` | E1 `ops/multimodal_check.py` + freeze step; E2 |NCC| rule + `EXTRA_WINDOWS` + per-trial Sun column; REPORT sub-pixel / runtime / coverage; `cut_pradan_pairs --tmc-product`; tests (302) |
| (evidence + docs commit) | the freeze's evidence at `b678272`, REPORT.md, figures, deck v3 text, DECK_V2_DRAFT rows and Q&A, AUDIT_REPORT.md, SUBMISSION_FIELDS, README, this STATUS, day_24 |

## Evidence at the freeze (REPORT.md, `b678272`)

- **SAC equatorial:** 6/6 accepted, Sun azimuths 174° apart, held-out median 0.69-1.68 px on the
  1.622 m grid. In-sample per axis X 0.66-1.15 / Y 0.73-1.07 px: not better than SuperGlue's
  0.62 / 0.57 px (Q&A only).
- **SAC polar:** 4/6 accepted, 1 unconfirmed, 1 contradicted + fallback.
- **74 °S OHRC → NAC:** 20/20 accepted, held-out median 0.41-1.0 px (0.51-0.94 m). Loops: 6,
  median 0.104 m = 0.083 px on 1.245 m.
- **Sun sweep:** 69 windows, 25 NAC frames, 3.3-152.7°.
- **TC rung:** 3/4. **Infrared:** MI 1548 nm 3/3 refused, fallback 0.23-1.09 px from the visible
  band; IIRS 10/11 refused, none registers. **OHRC → TMC-2:** 0/4.
- **Trust, 22 windows ≤ 10°:** 0/44 false alarms; 74 % at 3 m; 100 % from 5 m; 1/352 at 1-2 m.
  **8 SAC windows 132-174°:** 0/16; 94 % at 5 m; 100 % from 10 m.
- **MiLOI:** 81 scored pairs, 56 in S3; agrees 33/33 right, contradicted 43/43 wrong.
- **Sub-pixel by grid:** 0.086 px / 60 m (exact); 0.41-1.0 px / 0.93-1.25 m (held out); 0.083 px
  loops; MiLOI S1 0.52 px (truth 0.22 px).
- **Runtime:** median 10.7 s per 640-px window (89 OHRC → NAC windows), CPU only.

## In flight - resume here

Nothing is running. No PowerPoint process is left open. The 75 stray demo caches that a
no-argument `ops.precompute_demo_cache` wrote were deleted; the six demo caches remain.

## Samartha - to submit (ops/specs/day_24.md has the full list)

1. Read the v3 PDF cold, all six pages.
2. Portal: PS, title and description from `SUBMISSION_FIELDS.md`; upload the PDF; screenshot.
3. Optional and measurable: download the TMC-2 pass `ch2_tmc_ncn_20251107T2205342105_d_img_d18`
   (PRADAN login) - the only pass over SAC's frame with the Sun near the OHRC's; the cut command is
   ready (`--tmc-product`). Cut-off Thu 24 Sep 18:00.
4. Optional: demo video; repo public + link on slide 6; Gate 4 by hand.

## Open questions

1. Portal: draft save? editable after submit? title/description limits?
2. SPOC: Student Innovation and the two-PS cap; who uploads; authorisation letter.

## Known issues - do not re-report these

1. **`residual_px` is meaningless on real pairs** (RMSE over all held-out matches). Quote
   `residual_median_px` or `holdout_inlier_rmse_px` (capped at 3 px).
2. **Duplicate windows under two ids:** `…_w0N_sw` = `…_w0N`, `…_w01_t` = `…_w04`. Count distinct
   windows with `presentation.make_figures._distinct_windows` (136 of 140).
3. **MiLOI truth:** 81 of 321 pairs reachable; S3 (56 of 81) has no redundancy. The contradicted
   pairs' errors start at 7.4 px, so the cross-tab survives any truth error under ~4 px.
4. **LoFTR is weak under near-overhead Sun** (MiLOI S2). The trust layer catches it.
5. **Withdrawn rows:** `sac_tmc_fore_aft_w01..w04` are INVALIDATED. Never quote 0.019 px.
6. **NACs without a usable correction:** M1258744166RE, M1295016540LE, M1338673330RE (Sun
   azimuths 37°, 117°, 153° from the OHRC's). **No lit shared window:** M159642518LE, M1258737127RE.
7. **`trust_real_calibration.csv` is appended by every run** and refuses a header mismatch;
   `ops.freeze` deletes it first. Its trials draw from ONE RNG stream in window order, so adding
   a window changes every later window's planted directions (81 % → 74 % at 3 m on 20 Sep).
8. **Memory:** commit charge runs at 40-50 of 53 GB; run heavy jobs one at a time.
9. **The MiLOI matches were made at six earlier commits**; only the re-judge and scoring ran at
   `b678272`. `--plan` verifies the matching code is unchanged.
10. **Pairs cut before `3917a1b`** have up to 16 nearest-filled edge pixels. Negligible.
11. **The build audit checks text boxes, not rendered text**; `export_pdf`'s footer check is the
    real test. Always export before trusting a deck edit.
12. **Live align on a busy laptop takes 48-61 s**; demo from the cached pairs.
13. **The commit stamp of the multi-modal rows and REPORT.md's header include `ops/`**: any
    modified file under `ops/` (docs included) at run time stamps them `-dirty`. Park doc edits
    outside `ops/` while a freeze runs (done on 20 Sep).
14. **13 pair folders have no images** (`site_m…re_w01..05,07,08`,
    `site_ohrc_m1363141432re_w01,02,03,05,07,08`). The picker hides them.
15. **Docs below the national-round sections** (CLAUDE.md, canonical facts §1 and §10-11) are
    the college round's, kept as history.
16. **`ops.precompute_demo_cache` with no arguments caches every pair** (~150 × LoFTR, GBs of
    pickles). Always name the pairs.
17. **`export_pdf` intermittently prints nothing** ("printing failed: NO PDF", then a
    PermissionError on the temp dir): roughly every other attempt on 20 Sep. Kill POWERPNT, wait
    10-20 s, run it again; it never produced a wrong PDF, only no PDF. Check the PDF's mtime is
    later than the .pptx's before uploading.
