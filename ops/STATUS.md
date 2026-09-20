# STATUS - 20 September 2026 (Day 23), ~18:15 IST. National round, solo push.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM - read with `utf-8-sig`).
> Set `PYTHONIOENCODING=utf-8` for scripts that print → ° ↔ (cp1252 console crashes on them).

---

## Position

```
Sun 20 Sep 18:15  |  submit Sun 27 Sep (7 days)  |  portal closes Tue 30 Sep
Evidence cut-off  Thu 24 Sep 18:00     <- the only hard deadline with work behind it
Deck/portal final Fri 25 Sep 22:00
Read PDF cold     Sat 26 Sep
Submit            Sun 27 Sep
```

**The submission is DONE and sitting on disk.** Deck v4 PDF, portal text, evidence frozen, all
committed and pushed. Everything from here is optional upside or Samartha's 15 minutes at the
portal. Nothing is half-finished.

The old college-round gates (Days 5, 8, 10, 11, 12) are all past. **There is no gate tomorrow.**
The national round has cut-offs, not gates, and they are listed above.

## Read this first

1. **Evidence is FROZEN at `7dd4e5b`** (10/10 steps; 183/183 real rows, 324/324 MiLOI, 8/8
   multi-modal). `--check` at a later HEAD prints NOT FROZEN because the rows name `7dd4e5b`, not
   HEAD - that is expected. The test that matters, re-run tonight:
   `git diff 7dd4e5b HEAD -- core evaluation ops baselines app` shows only docs, the freeze's own
   evidence CSVs, and two source files that cannot change a number:
   `ops/trust_real_calibration.py` (**0 behavioural lines**, comments only) and
   `ops/make_report.py` (30 lines, all rendering - it writes no evidence file).
2. **Deck is v4 and final.** `AUDIT: clean`, `PDF CHECK: clean`, 6 pages, 1,112,713 bytes,
   sha256 `510a5c50…`. All six pages rendered and read. `claim-checker` found 0 fabricated
   numbers; its 2 HIGH / 8 MEDIUM / 4 LOW were verified by hand, 13 applied, 1 declined on the
   record. Safety net: tag `submission-v1` = `0297936` and `SIH26166_LunaXX_deck_v1_SAFE.pdf`.
3. **NEW TODAY - the Mission Console**, `web/`. A dark instrument-panel front end over the frozen
   evidence, replacing nothing: `app/streamlit_app.py` is untouched and is still what Gate 4
   tests. Published (private) at **https://claude.ai/artifact/LbbZKdvnVYCCBbPjEBZCA9**, version 7.
   - Covers **all 8 instrument pairings and all 3 verdicts** (10 pairs in the roster).
   - `python -m web.server` adds a LIVE bay that registers a pair you upload, calling
     `core.pipeline.run_all` directly. Verified end to end through the browser's own file inputs.
   - It **writes nothing** and lives outside `core/ evaluation/ ops/ app/`, so rebuilding it can
     never restamp an evidence row or a demo cache.
   - Operator guide: `web/README.md`. Build: `python -m web.build_console`.
4. **NEW TODAY - the explainer video pipeline.** `web/dist/mission-console.mp4` is built and
   **silent**: 1600×1000, 12 fps, 108 s, 7.6 MB, from 1,649 real screencast frames of the console
   driving itself through 16 beats. `web/narration.md` is the script (683 words, ~4.7 min spoken,
   every number traceable to REPORT.md at the freeze).
   **`web/voice.py` is UNTESTED** - it needs a Gemini key Samartha has not provided yet. It parses
   all 16 beats under `--dry`; the TTS call itself has never run.

## Verified by command tonight (20 Sep, 18:10-18:20)

| Check | Exit | Result |
|---|---|---|
| `python -m pytest evaluation/ -q` | **0** | 81 passed in 2.2 s |
| `python -m pytest -q` (whole repo) | **0** | **340 passed** in 13.5 s |
| `import core.pipeline` | **0** | OK |
| `git status --short` | - | clean, nothing uncommitted |
| `git diff 7dd4e5b HEAD -- core evaluation ops baselines app` | - | docs + evidence only; 0 behavioural lines in trust_real_calibration.py |
| deck PDF on disk | - | 1,112,713 bytes, 12:46 |
| video on disk | - | 7,997,862 bytes, 18:13 |

## What landed today (`f928995`..`f2216fa`, 9 commits)

| Commit | What |
|---|---|
| `be94774` | **Deck v4** refilled from `7dd4e5b`; REPORT.md committed so the numbers point at a commit a judge can open; claim-checker applied |
| `f6a6c50` | Mission Console v1 - template + build script, outside Streamlit |
| `f9ee137` | Refused pairs showed the FALLBACK under a REFUSED banner; now the matcher's own rejected warp, and both inputs always visible |
| `467b361` | The band test (749 nm vs 1548 nm) + a "What it registers" ledger to balance the refusals table |
| `64ed1d7` | All 8 pairings in the roster, not 2; `web/README.md` |
| `957cd6a` | `web/server.py` - live upload, calling `run_all` directly, standard library only |
| `5c6b1c3` | README section 6 contradicted section 7 |
| `23e3395` | **Six defects found by auditing the built page**, incl. a pair that displayed the previous pair's verdict |
| `f2216fa` | The three verifications + `film.py` / `narration.md` / `voice.py` / `cut.py` |

## In flight - resume here

**Nothing is running.** No server, no background job, no PowerPoint process. Working tree clean,
pushed to `origin/main` at `f2216fa`.

The first thing to pick up is **not** code. It is the TMC-2 decision (below), because it is the
only remaining item with a deadline and it needs a download only Samartha can do.

## Samartha - what is actually left

1. **Put `C:\sih26166_backup\` on a USB stick.** `weights/`, `data/pairs/`, `demo_cache/` -
   181 files, 103 MB, re-synced today. Gitignored, inside OneDrive, and the only unrecoverable
   thing in this project.
2. **TMC-2 closer-Sun pass - DECIDE BY WED 23 SEP.** The evidence cut-off is Thu 24 Sep 18:00 and
   the chain (cut → run → freeze → re-read every deck row → rebuild → re-export → claim-checker)
   is about two hours. Needs a PRADAN login and a 0.6-0.9 GB download; commands are in
   `ops/specs/day_24.md`. It is the only pass over SAC's frame with the Sun ~9° in azimuth from
   the OHRC's, and **a second refusal is also a publishable result** - say so on the slide.
3. **Read the v4 PDF cold**, then portal: PS, title, description from `SUBMISSION_FIELDS.md`,
   upload the PDF, screenshot the confirmation.
4. **Decide on the slide-6 console link before Fri 25 Sep 22:00.** The artifact is private; a
   judge cannot open it until it is shared from the page's Share menu.
5. Optional: Gemini key → narrated video; repo public; Gate 4 by hand.

## Open questions

1. **Portal mechanics** - draft save? editable after submit? character caps? The long description
   is 1,804 characters; the 507-character short version is ready if there is a cap.
2. **SPOC** - Student Innovation and the two-PS cap; who uploads; authorisation letter.
3. **Gemini key** for the voice-over. Until it arrives `web/voice.py` is unexercised code.
4. **Does the console link go on slide 6?** Needs a decision AND the artifact made shareable.

## The other five

Invariant 4 (one folder per person) is **suspended** for the solo push and teammates have no
assigned work until after submission - so there are no specs tonight, and `spec-writer` was
deliberately not run. Writing five specs for five people with no tasks would be fiction.
Last delivered state, for when they restart:

| Person | Folder | Last delivered | Now |
|---|---|---|---|
| Samrudh | `evaluation/` | synthetic data, shaded relief, metrics, results_log | idle until after 27 Sep |
| Risheeth | `baselines/` | SIFT / ORB / AKAZE + failure gallery | idle |
| Rishabh | `app/change_detection.py` | change detection | idle |
| Saniya | `presentation/` | deck template work (Samartha owns v4) | idle; **needed for PDF export if PowerPoint is required** (Known issue 17) |
| Rohan | `data/*.csv|*.md` | pairs catalogue | idle |

**Gate 5 still requires all six to explain their own module cold.** Nobody has rehearsed the
Mission Console or the v4 deck numbers. That is finale work, not submission work, but it is not
zero work.

## Known issues - do not re-report these

1. **`residual_px` is meaningless on real pairs.** Quote `residual_median_px` or
   `holdout_inlier_rmse_px`. The held-out median is itself only robust while the inlier ratio is
   well above 0.5 - one tiled window reads 316 px at 0.542 with the alignment visibly correct
   (NCC +0.87 to +0.95).
2. **Duplicate windows under two ids** (`…_sw`, `…_w01_t`). Count with
   `presentation.make_figures._distinct_windows`: 160 of 177.
3. **MiLOI truth:** 81 of 321 pairs reachable; S3 (56 of 81) has no redundancy.
4. **LoFTR is weak under near-overhead Sun** (MiLOI S2). The trust layer catches it.
5. **Withdrawn rows:** `sac_tmc_fore_aft_w01..w04` are INVALIDATED. Never quote 0.019 px.
6. **NACs without a usable correction:** M1258744166RE, M1295016540LE, M1338673330RE.
   **No lit shared window:** M159642518LE, M1258737127RE.
7. **`trust_real_calibration.csv` is a fresh RNG draw whenever the trial list changes.** The 3 m
   rate has been 81 %, 74 %, 74 %; 1-2 m 2/352, 1/352, 0/352; hard-Sun 5 m 94 % then 84 %. These
   are draws of one experiment, not a regression. Quote the frozen value; hedge in speech.
8. **Memory:** commit charge runs 40-50 of 53 GB; run heavy jobs one at a time.
9. **MiLOI matches were made at six earlier commits**; only re-judge and scoring ran at `7dd4e5b`.
10. **Pairs cut before `3917a1b`** have up to 16 nearest-filled edge pixels. Negligible.
11. **`build_deck`'s audit measures text boxes, not rendered text.** `export_pdf`'s footer check
    is the real test. Slides 2, 4 and 5 are at capacity; only slide 6 has room.
12. **Live align on a busy laptop takes 48-61 s**; demo from the cached pairs.
13. **REPORT.md's header and the multi-modal rows stamp `ops/`**: any modified file under `ops/`
    at run time marks them `-dirty`. Park doc edits elsewhere while a freeze runs.
14. **13 pair folders have no images.** The picker hides them.
15. **Docs below the national-round sections** (CLAUDE.md, canonical facts §1, §10-11) are the
    college round's, kept as history.
16. **`ops.precompute_demo_cache` with no arguments caches every pair.** Always name them.
    `demo_cache/` now holds **14** pairs (6 Streamlit demo + 8 console roster), not 6.
17. **`export_pdf` intermittently prints "NO PDF"** - roughly every other attempt. Kill POWERPNT,
    wait 10-20 s, retry. Check the PDF's mtime is later than the .pptx's before uploading.
18. **F18** - `ops.freeze`'s `trust` step reads the window list from the CSV it then deletes; lose
    that file and the step fails in seconds with a zero-byte log. **F19** - the freeze summary
    adds `None` to an int on a precondition-failed step, ending a completed run in a traceback.
    Both are `ops/` changes that would force another freeze. First in line after submission.
19. **Two orphan bundles** (`site_tc_ortho_mi1548_w01`, `site_tc_ortho_mi749_w01`, `057664a-dirty`)
    still show the F12 signature. In no log, referenced by nothing. Do not quote them.
20. **NEW: a backgrounded browser tab throttles `requestAnimationFrame` to ~1 fps.** Measuring
    WebGL performance on a tab that is not frontmost reports a false failure - it did today.
    Focused, the console holds 59.9 fps with 0 context losses on the Intel Arc iGPU.
21. **NEW: `NaN` is valid JavaScript but invalid JSON.** The built page embeds its data as a JS
    literal so NaN parsed fine statically, while the live API response could not be parsed at all.
    `web/panel.py` emits `None`; `web/server.py` uses `allow_nan=False` so it fails loudly.
22. **NEW: ffmpeg 9 removed `-vsync`.** Use `-fps_mode`.
23. **NEW: the MCP-driven Chrome is not signed into claude.ai**, so the published artifact's
    *rendering* cannot be checked from this session - only its bytes, which were verified verbatim.
24. **NEW: `web/voice.py` has never made a live call.** No Gemini key yet.
25. **NEW, and it matters for Gate 4: the demo cache staleness plate raises a false alarm after
    ANY commit.** `core.export._commit(("core","evaluation","app"))` returns **HEAD's** sha
    whether or not those paths changed, so a docs-only commit makes every cached result render
    `CACHED RESULT commit <a> — CODE IS NOW <b>` in caution colour. Verified tonight: all 14
    caches are flagged, and `git diff f928995 HEAD -- core evaluation app` is **empty**. The code
    genuinely has not moved.
    **Before Gate 4 or any live demo**, re-run on the final commit - it takes about 30 s for the
    six demo pairs:
    `python -m ops.precompute_demo_cache pair_00_dryrun pair_01 pair_03_tierD pair_04_tierD_native sac_ohrc_nac_w06 site_tc_morning_mi1548_w01`
    The real fix is for `_commit` to return the last commit that TOUCHED the watched paths, not
    HEAD. **Not done tonight on purpose**: `core/export.py` is inside the freeze stamp path, so
    changing it would invalidate `7dd4e5b` and force a 90-110 minute re-freeze four days before
    submission. It goes in the queue with F18 and F19, after 27 Sep.
