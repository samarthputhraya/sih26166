# STATUS - 22 September 2026 (Day 25), late. National round, solo push.

> **v7: the TMC-2 / IIRS gap, stated as the standard rather than the miss.** The PS title names
> OHRC, TMC and IIRS; we register OHRC well and refuse TMC-2 (0/4) and IIRS (0/11), and the
> strongest visible competitor claims both. Slide 4 now says why in their own terms: on
> OHRC→TMC-2 the matcher kept **6–7 inliers per window at 5–9 % coverage**, a fit to that
> handful reports a small in-sample residual *by construction*, and the area check measured the
> the area check could verify **not one cell of 64** and contradicted all four (`REPORT.md`
> lines 148–151; the held-out medians of 112–268 px on those rows are deliberately NOT quoted as
> "how wrong" - at inlier ratio 0.05 that statistic describes the outliers, Known issue 1). The
> competitor's TMC-2 result is an in-sample RMSE on 5–7 inliers at 5–7 % coverage - the exact
> regime our check refuses. Nobody is named on the slide; the standard is. The strategies bullet
> is now an ordered roadmap whose first item is the closer-Sun TMC-2 pass (`ops/specs/day_24.md`).
> fig6's axis and caption were also fixed (grids 0.93–1.62 across both populations; 30 windows,
> not 22) - only that figure changed, hash-verified. **1,094,206 bytes, sha256 `0bf4927c…`,
> `AUDIT: clean`, `PDF CHECK: clean`.** Slide 4 body is 11 pt; that is the floor.
>
> **The one evidence move that turns the weak line into a strong one is still yours to make:**
> the closer-Sun TMC-2 pass needs a PRADAN download (0.6–0.9 GB) only you can do, then ~2 h.
> Evidence cut-off is Thu 24 Sep 18:00. Either result improves the deck - a second refusal at
> ~9° of Sun is also publishable. Commands are in `ops/specs/day_24.md` §"The one measurable".


> **Deck v6: the pitch pass.** Product work stopped on Samartha's call - the remaining days go to
> the deck, and gaps get closed after selection. v5 was correct and read like a lab report (278
> and 272 words of ours on slides 2 and 4, the thesis last on slide 2). v6 keeps every figure and
> every condition and changes the argument's shape: the thesis leads slide 1 and slide 2, slide 2
> stops reciting the pipeline that slide 3 draws, slide 4 states its limits as the field's rather
> than ours, and slide 5 opens on who it is for. **6 pages, 1,091,396 bytes, sha256 `3ddae7ce...`,
> `AUDIT: clean`, `PDF CHECK: clean`.** Evidence untouched: still frozen at `7dd4e5b`, REPORT.md
> unchanged, nothing under `core/ evaluation/ ops/ app/` edited.
>
> **Two SAC hooks were added, both verified before use.** The polar benchmark pair, where SAC's
> own study found only SuperGlue registered it (`REPORT.md` lines 97 and 121); and their 2026
> mosaic paper stating its framework "does not address geometric misalignment or parallax
> effects", with joint geometric/radiometric frameworks as future research (arXiv:2604.25208
> sections VI and VII, read 22 Sep). **No accuracy comparison with arXiv:2509.04775 is made
> anywhere, deliberately** - their SuperGlue figure is 0.62 px on a 1.118 m grid (0.69 m) and our
> best in-sample on that pair is 0.656 px on a 1.622 m grid (1.06 m). That comparison loses, so
> it is not on a slide. Know it cold; do not volunteer it.
>
> **The claim-check found five defects in the rewrite and all five are fixed** - see
> "Deck v6 claim-check" below. Two were in lines written that same hour, which is the argument
> for running it every time `presentation/` changes.

# STATUS - 20 September 2026 (Day 23), ~22:35 IST. National round, solo push.

> **Second session tonight (19:45-22:35): the judge's walk-through, and the fixes from it.**
> A read-only inspection drove the deck, the console (three serving paths), the live upload bay
> and the Streamlit app in a real browser, then graded the submission **Above average**. The
> report is `ops/national_round/JUDGE_REPORT_2026-09-20.md`. Everything in its
> "before Fri 25 Sep" list is now **done** except one item deliberately declined; see
> "Judge-report fixes" below. The evidence was not touched and did not move: `pytest` 340 passed,
> and the console's own build prints the same tallies it printed this afternoon.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM - read with `utf-8-sig`).
> Set `PYTHONIOENCODING=utf-8` for scripts that print → ° ↔ (cp1252 console crashes on them).

---

## Position

```
Tue 22 Sep        |  submit Sun 27 Sep (5 days)  |  portal closes Tue 30 Sep
Evidence cut-off  Thu 24 Sep 18:00     <- the only hard deadline with work behind it
Deck/portal final Fri 25 Sep 22:00
Read PDF cold     Sat 26 Sep
Submit            Sun 27 Sep
```

**The submission is DONE and sitting on disk.** Deck v6 PDF, portal text, evidence frozen, all
committed and pushed. The repository is now **public**, and slide 6 carries its URL. Everything from here is optional upside or Samartha's 15 minutes at the
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
2. **Deck is v6** (22 Sep pitch pass; see the header). `AUDIT: clean`, `PDF CHECK: clean`,
   6 pages, **1,091,396 bytes**, sha256 `3ddae7ce…`. The v5 note below is kept because the
   slide-6 link it describes is still there. v5 differed from v4 in **one place**: slide 6 gained two bullets at the top, under
   a new heading "Code, evidence and the full report" - the repository URL, and the line "Every
   figure on these slides is in REPORT.md at the evidence-freeze commit 7dd4e5b". Nothing else on
   any slide moved; slides 1-5 carry exactly the v4 content, and v4's claim-checker pass (0
   fabricated numbers; 2 HIGH / 8 MEDIUM / 4 LOW, 13 applied, 1 declined on the record) still
   stands for them. Safety net: tag `submission-v1` = `0297936` and
   `SIH26166_LunaXX_deck_v1_SAFE.pdf`.
   **Exporting the PDF needs PyMuPDF on `PYTHONPATH`** - it is deliberately not in the demo venv
   (`presentation/export_pdf.py` docstring). What worked tonight, first try:
   `pip install --target <scratch>/pylibs pymupdf`, then
   `PYTHONPATH=<scratch>/pylibs python -m presentation.export_pdf`. Without it the print still
   happens but the crop does not, and the script leaves an **uncropped** PDF in `%TEMP%`.
   Do not upload that one: it has white bands and is not what `PDF CHECK` passed.
3. **NEW TODAY - the Mission Console**, `web/`. A dark instrument-panel front end over the frozen
   evidence, replacing nothing: `app/streamlit_app.py` is untouched and is still what Gate 4
   tests. Also published as a Claude Artifact at **https://claude.ai/artifact/LbbZKdvnVYCCBbPjEBZCA9**
   - **private, and its share state has never been verified from a session**; slide 6 points at
   the public repo instead, which needs no login and can be checked.
   - Covers **all 8 instrument pairings and all 3 verdicts** (10 pairs in the roster).
   - `python -m web.server` adds a LIVE bay that registers a pair you upload, calling
     `core.pipeline.run_all` directly. Verified end to end through the browser's own file inputs.
   - It **writes nothing** and lives outside `core/ evaluation/ ops/ app/`, so rebuilding it can
     never restamp an evidence row or a demo cache.
   - Operator guide: `web/README.md`. Build: `python -m web.build_console`.
   - **The build now writes TWO files.** `dist/index.html` is a complete document and is the one
     to open by hand or serve statically; `dist/mission-console.html` is the **fragment** for the
     Artifact only. Opening the fragment directly lands in quirks mode, decodes as windows-1252
     (60 mojibake sequences) and paints a hidden trust-map layer over the visible one - the
     README used to tell you to do exactly that. The build also runs `node --check` over the
     page's inline script when node is present.
   - Lighthouse (snapshot, desktop) on the served page: **accessibility 100, best practices 100,
     SEO 100**, 41 audits passed, 0 failed. Zero console errors, zero 404s.
4. **NEW TODAY - the explainer video pipeline.** `web/dist/mission-console.mp4` is built and
   **silent**: 1600×1000, 12 fps, 108 s, 7.6 MB, from 1,649 real screencast frames of the console
   driving itself through 16 beats. `web/narration.md` is the script (every number traceable to
   REPORT.md at the freeze).
   **`web/voice.py` is UNTESTED** - it needs a Gemini key Samartha has not provided yet. It parses
   all 16 beats under `--dry`; the TTS call itself has never run.
   **And the script does not fit the picture.** Measured tonight: the 16 beat headings sum to
   exactly 108.0 s, matching the cut, but the spoken lines under them total **790 words**, which
   is **327 s at 145 wpm - 3.0x over**. Per beat it is worse: "calibration - 8 s" carries 72
   words (30 s). Cut the script to ~260 words, or re-time `web/film.py`'s beats, **before**
   spending a TTS call on it. Left as-is tonight by decision: the video is finale work, not
   submission work, and a rushed re-cut is how a number gets lost.

## Deck v6 claim-check (22 Sep) - five defects, all fixed

`claim-checker` re-derived every figure from the raw CSVs and found **no invented number** on any
slide, Invariant 2 holding everywhere, and hardware/cost claims clean. It found five real defects,
two of them in lines written the same hour:

| What was wrong | Why it mattered | Now |
|---|---|---|
| Slide 6: "evidence logs **measured at** the freeze commit 7dd4e5b" | True only of `real_pairs_log.csv`. `miloi_log.csv` stamps **"run e10deb0, scored 7dd4e5b"**; `results_log.csv` and `trust_real_calibration.csv` have **no commit column at all**; and `trust_real_calibration.csv` is absent from the `7dd4e5b` tree. **Second round running this sentence has been wrong**, and slide 6 hands the judge the repo to check it with | Clause by clause per log: real-pair rows measured at 7dd4e5b; MiLOI matched at e10deb0, scored at 7dd4e5b; REPORT.md regenerated at f928995 |
| Slide 4: "Against exact truth: 0.086 px = 5.1 m" | The **0 deg/15 deg** value of four. The row is 0.086 / 0.086 / 0.314 / 1.096 px = 5.1 / 5.1 / 18.8 / 65.8 m. Best-of-four quoted bare, on the Sun-angle slide | Carries its condition and the 45 deg degradation |
| Slide 2: "within 0.23-1.09 px ... on MI's 14.8 m grid" | Invariant 2 wants metres too, and **1.09 px is 16.2 m** - a judge who multiplies feels misled | "0.23-1.09 px = 3.4-16.2 m" |
| Slide 5: "a corner is **3 px** out" | No trial lands at 3 px: they are planted in **metres** across **four** reference grids (0.931/1.215/1.245/1.622), so no single px value exists. Inherited from `REPORT.md:338`, which still says it | "at 3 m of corner displacement 0 of 120 trials contradict, and at 5 m, 105 of 120 still say good" |
| Slide 1: "a verdict for every region of **every result**" | The 112-px IIRS windows are too small to cell, so a whole-frame verdict decides them (`REPORT.md:188`) | "every region of **the** result" |

Also applied from the same pass: the 316 px tiled window and the OHRC->TMC-2 0-of-4 rung are now
printed on slide 4 rather than left for a judge to find in REPORT.md; slide 3 names the difference
between its two 8x8 checks (the coverage check *does* read matches, the area check never does);
and the Sun sweep is detached from SAC's pairs so the 69/25 population is not read as theirs.

**Still open from that report, not done:** `REPORT.md:338`'s own "3 px out" (a `REPORT.md` edit
means `ops/make_report.py` and a regeneration - queued, not worth touching before submission), and
`docs/00_CANONICAL_FACTS.md` lines 27-29, 50 and 76, which are **stale by success**: they still say
no Tier B/B+/C pair was ever cut and no real Sun-difference pair exists. CLAUDE.md routes all prep
through that file, so **rehearsing from it will produce answers weaker than the evidence.** Fix it
before any rehearsal.

## Judge-report fixes (20 Sep, 19:45-22:35)

Every item the report put in "before Fri 25 Sep" is applied except one, which was declined with
a reason. **Nothing under `core/`, `evaluation/`, `app/` or `baselines/`-as-code was touched, so
no re-freeze was needed and no number moved.**

| # | What was wrong | Fixed where | Verified how |
|---|---|---|---|
| **B1** | The PDF had **0 hyperlinks on all 6 pages**, the repo was private and the portal has no link field, so a PDF-only judge reached nothing | `presentation/build_deck.py` `S6`; both descriptions in `SUBMISSION_FIELDS.md`; **repo made public** | `AUDIT: clean`, `PDF CHECK: clean`; slide 6 re-rendered and read |
| **B2** | `OHRC → TMC-2` was chipped **SAME MISSION** in the trust map and **CROSS-SENSOR** in the refusals table - on a page whose footer publishes "Cross-sensor means different instruments" | `web/console.template.html` refusals row, now SAME MISSION, matching `REPORT.md:145` ("same mission - NOT cross-mission") | read both bays in the browser after rebuild |
| **B3** | The IIRS pair was chipped MULTI-MODAL with its B side labelled **"998.8 nm (visible/near-visible)"** - the cutter's threshold is `nm >= 1000` and it misses by 1.2 nm | `BAND_FIX` in `web/build_console.py`. **Not** in `ops/cut_site_pairs.py`: that is inside the freeze stamp path | panel now reads `998.8 nm (near-infrared)` |
| **B4** | A failed or in-flight live run left the **previous** pair's green ACCEPTED panel on screen under "This ran just now, on this machine" | `clearResult()` on submit, on HTTP error and on exception, `web/console.template.html` | banner reads `RUNNING…` mid-run; `NOT REGISTERED` on failure |
| **B4** | The 52.8 MB roster pair gave `ERR_CONNECTION_RESET` → a bare `Failed to fetch` | client-side size pre-check against `api/health`'s `max_bytes` × ¾; `_drain()` before the 413 in `web/server.py` | page refuses before uploading, naming both sizes and the cap; an 80 MB curl body now gets a readable **413 in 0.2 s** |
| **B5** | "0 of 64 verified, 5 weak, **59 no evidence**" sat a line above "16 % of **51 measurable cells**" - two different tests, both called cells | `countsSaid()` / `whySaid()` + a new note under the trust map | now "59 **with no match evidence**" and "51 **cells the area check could measure**" |
| **H1** | `web/README.md` §1 told the operator to open the **fragment**, which lands in quirks mode, windows-1252, 60 mojibake, and paints a hidden layer over the visible one | build writes `dist/index.html` too; README §1 rewritten | static path now: doctype ✔, `CSS1Compat`, UTF-8, viewport ✔, **mojibake 0**, hidden layer `display:none` |
| **H3** | The differentiator was not on the first screen, and a competitor now also pitches clean failure reporting | three new hero tiles, ordered first: `8×8 cells vote … never sees the matches`, `0/44 · 0/16 false alarms`, `100 % of planted 5 m errors flagged` | read on desktop, phone and projector |
| **M1** | `failed, and NOT caught: 0` was a hardcoded literal, identical in all six bands | reads `missed_failure` from the bin | still 0 in every band, now because the data says so |
| **M2** | Two RESULTS rows quoted sub-pixel figures without naming the grid | loops row names the **1.245 m NAC B** grid; MI 1548 row names **MI's 14.8 m** grid | read in the browser |
| **L1-L7** | favicon 404 · nav listed LIVE first but it sits second · empty sha during load · `heading-order` + `meta-description` · doubled full stop and a NAC-EDR hint on a PNG upload · unqualified `8.2 s` · both uploaded filenames truncating identically | `web/server.py` + `web/console.template.html` + `web/build_console.py` | **Lighthouse 100 / 100 / 100**, 41 passed, **0 failed**; zero console messages |
| — | Build had no guard on its own 2 MB inline script (a stray backtick broke it once tonight, caught in the browser) | `node --check` in `web/build_console.py` | build prints `js: 1 inline script(s) parse clean` |
| — | Three `baselines/failure_gallery/*.jpg` had **`1424 matches · residual 0.2px · inliers 100%`** burned into the pixels, on random blobs. `pair_test` appears **0 times** in `results_log.csv`, and `claim-checker` greps text, so it can never see them. An Invariant 1 violation about to become public | deleted (the generator `draw_failure_gallery.py` stays) | `grep -c pair_test evaluation/results_log.csv` → 0 |
| — | 19.6 MB of unreferenced exploratory PNGs in `data/lroc_analysis/` (Invariant 5) and 0.8 MB of candid internal audit dumps in `ops/audit/*.json`, all about to become public | deleted | tracked bytes **23.08 MB → 8.52 MB**, 264 → 242 files |

**Declined, on the record:** the Known-issue-25 demo-cache re-run. Its own command re-caches
`sac_ohrc_nac_w06` and `site_tc_morning_mi1548_w01`, which are **Mission Console roster pairs**.
MAGSAC++ resamples, so their inlier counts would drift ~1 % and the console would then display
numbers that are **not in REPORT.md** - an Invariant 1 break to silence a cosmetic plate. See
Known issue 25 for what to say instead.

**Also declined** (both offered, both judged not worth the risk this week): moving the LIVE bay
above SUN, and re-cutting `web/narration.md`.

### claim-checker, run after the deck changed (CLAUDE.md routing)

**0 fabricated numbers.** It re-derived the trust tables from `trust_real_calibration.csv` itself
and got 0/44, 0/16, 74.4 %, 84.4 %, 94.1 %, 87.4 % - exact. It re-counted all four portal
character counts - correct. No Invariant 2 violation anywhere in the deck, the console, the
README or the portal text.

It found **one false claim, and it was in the bullet added tonight**. Slide 6 said "Every figure
on these slides is in REPORT.md **at** the evidence-freeze commit 7dd4e5b". That is not true, and
it is checkable in fifteen seconds by the judge the bullet above it just handed the repository to:

```
$ git show 7dd4e5b:evaluation/trust_real_calibration.csv
fatal: path ... exists on disk, but not in '7dd4e5b'
$ git show 7dd4e5b:REPORT.md | head -3
Generated 2026-09-20T04:27 from commit `b678272` ...
```

The freeze **measures** the rows at `7dd4e5b`; `REPORT.md` is regenerated from them afterwards and
committed separately, at `be94774`. At `7dd4e5b` the tree still holds the previous report, and
none of "13.1 km", "0.57 m", "8.2 s", "160 distinct", "94.1" or "0.107" is in it. **Say
"measured at".** Fixed in all four places it had been written: `presentation/build_deck.py`
(slide 6), `ops/national_round/SUBMISSION_FIELDS.md`, `web/console.template.html` (the hero
provenance sentence) and `web/build_console.py`'s docstring.

`presentation/build_deck.py`'s own audit now **verifies** the claim instead of trusting it: any
slide saying "REPORT.md ... at commit `<sha>`" makes the build run `git show <sha>:REPORT.md` and
fail if the deck's sample figures are not in it. Tested against both the wrong and the right
wording before shipping.

Three more of its findings applied the same night:
- the hero tile read "(84 % on SAC's 8; **74.4 % at 3 m**)", which lets a reader attach the 3 m
  rate to SAC's 8, where the true value is **12.5 %**. Every rate now carries its population.
- the decimal is gone: the 3 m rate is a fresh RNG draw per freeze (143 / 130 / 131 of 176 over
  three freezes, Known issue 7), so "74.4 %" advertises precision the experiment does not have
  and disagreed with the deck's "74 %".
- two RESULTS rows gave px with a grid but no metres (now "= 1.1-2.7 m" and "= 3.5-6.9 m"); the
  loop row now says its A->B leg is NAC<->NAC, same sensor; "cells **vote on** the transform"
  became "cells **judge** the transform", because the cells judge a transform built without them;
  slide 5's "(3 frames at 3 sites)" is now "(3 OHRC frames at 3 sites)", since there are 25 NAC
  frames and the bare word invited the wrong one.

Its note on OHRC -> TMC-2, worth having in your mouth: `REPORT.md:143` and `README.md` both call
that pair "cross-sensor, same mission". Both are true. **If asked: "yes, cross-sensor - two
different cameras - but same mission, so we chip it SAME MISSION rather than bank it as
cross-sensor evidence."** No edit needed; the console's row text already says "Two different
cameras on one spacecraft".

## Verified by command tonight (20 Sep, 22:00-22:35)

| Check | Exit | Result |
|---|---|---|
| `python -m pytest -q` (whole repo) | **0** | **340 passed** in 12.4 s, after every change |
| `python -m web.build_console` | **0** | same tallies as this afternoon: 69 sweep windows, 25 frames, 37 tiles, 10 roster pairs, rotscale 20896/19653/22464/19635 |
| `python -m presentation.build_deck` | **0** | `AUDIT: clean` |
| `python -m presentation.export_pdf` | **0** | `PDF CHECK: clean`, 6 pages, 1,113,285 bytes (Known issue 17 hit once: killed POWERPNT, waited, retried) |
| `run_all` inside `no_network()` | **0** | **6.4 s, zero sockets opened**, `agrees`, 5185/5183 - same as the Streamlit live run |
| live upload through the browser | - | `agrees`, **5,112 matches**, **56/64 verified** = `REPORT.md` line 22; inliers 4,630 vs 4,680 (1.1 %, MAGSAC++) |
| 80 MB body to `api/register` | - | **HTTP 413 in 0.2 s** with a readable message (was: connection reset) |
| Lighthouse snapshot, desktop | - | **100 / 100 / 100**, 41 passed, 0 failed |
| phone 393×852 · projector 1366×768 | - | no horizontal overflow, nothing clipped, 8 hero tiles legible at both |
| console with both CDNs blackholed | - | degrades honestly: `three` undefined, caption changes itself to "hillshade (no WebGL in this viewer)", everything else works |
| `git diff 7dd4e5b HEAD -- core evaluation ops baselines app` | - | docs + evidence + 3 deleted JPGs + 2 deleted audit dumps; **still 0 behavioural lines** |

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
pushed to `origin/main` at `90bb15c`. The two local servers and the Streamlit process used for
tonight's inspection were stopped; if a port is busy, look for a stray `python -m web.server`.

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
3. **Read the v5 PDF cold**, then portal: PS, title, description from `SUBMISSION_FIELDS.md`,
   upload the PDF, screenshot the confirmation. Slide 6 now carries the repository URL, so
   **open `github.com/samarthputhraya/sih26166` in a private window first** and confirm it
   loads. A dead link on slide 6 is worse than no link.
4. ~~Decide on the slide-6 console link.~~ **Done**: the repo is public and slide 6 points at it,
   which needs no login and can be verified from any browser. The Claude Artifact stays private -
   its render and its share state could never be checked from a session (Known issue 23), and an
   unverifiable link was not worth printing on the deck. If you want it shared too, use the
   page's Share menu and check it from a logged-out browser before adding it anywhere.
5. Optional, in rough order of value: **rehearse the Mission Console** (nobody has, and Gate 5
   wants each module explained cold); cut the narration to fit the film (Known issue 27) and then
   voice it; Gate 4 by hand.
6. **If a judge will browse the repo**, spend ten minutes on `ops/specs/` and `ops/audit/`. They
   are honest working notes addressed to teammates, not to a reviewer, and Known issue 15 already
   says the docs below the national-round sections are the college round's. Nothing there is
   wrong; some of it is just stale in a way that invites a question you would rather not spend
   time on.

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
    **Do NOT run the obvious workaround.** The command below re-caches `sac_ohrc_nac_w06` and
    `site_tc_morning_mi1548_w01`, which are **Mission Console roster pairs**; MAGSAC++ resamples,
    their inlier counts drift about 1 %, and the console would then show numbers that are not in
    `REPORT.md`. That trades a cosmetic plate for an Invariant 1 break.
    ~~`python -m ops.precompute_demo_cache pair_00_dryrun pair_01 pair_03_tierD pair_04_tierD_native sac_ohrc_nac_w06 site_tc_morning_mi1548_w01`~~
    **What to do instead**, in order of preference:
    1. **Untick "Use the precomputed result" and run live.** Verified tonight: the plate
       disappears, the header reads `RESULT LIVE RUN`, and three consecutive runs took 6.8 / 6.1 /
       6.5 s with identical results (5,185 matches, 63/64 verified, AGREES).
    2. **Say it out loud.** `git diff f928995 HEAD -- core evaluation app` is **empty**: the code
       genuinely has not moved. The plate compares HEAD, not the last commit that touched those
       paths. One sentence and a command answers it.
    The real fix is for `_commit` to return the last commit that TOUCHED the watched paths, not
    HEAD. **Not done on purpose**: `core/export.py` is inside the freeze stamp path, so changing
    it would invalidate `7dd4e5b` and force a 90-110 minute re-freeze. Queue it with F18 and F19,
    after 27 Sep.
26. **NEW: the repository is PUBLIC.** Slide 6 and both portal descriptions point at
    `github.com/samarthputhraya/sih26166`, and the portal has no link field, so that URL is the
    only route a judge has off the PDF. **Check it from a logged-out browser before submitting.**
    If it ever goes private again, cut the slide-6 bullet and the clause in both descriptions -
    a dead link on slide 6 is worse than no link. Three classes of file were removed before it
    was flipped: the `pair_test_*_failure.jpg` gallery (unsourced numbers burned into pixels),
    `data/lroc_analysis/*.png` (19.6 MB, Invariant 5), `ops/audit/00_RECON_*` (candid internal
    prose). They remain in git history; nothing reads them and 340 tests pass without them.
27. **NEW: the narration is 3x too long for the film.** 16 beat headings sum to exactly 108.0 s,
    matching `mission-console.mp4`; the spoken lines total 790 words = 327 s at 145 wpm. Cut to
    ~260 words, or re-time `web/film.py`'s beats, **before** spending a TTS call.
28. **NEW: only the first download fires per Streamlit session.** Chrome blocks repeat automatic
    downloads, so clicking "Registered product (GeoTIFF)" after the zip can look like nothing
    happens. **Demo rule: click "All deliverables (.zip)" and nothing else** - the other three
    files are inside it. The zip was opened and verified tonight: 7 files, `testzip()` clean.
29. **NEW: the exported GeoTIFF for `pair_01` carries no geotransform**, because
    `pair_01_ref.tif` has none to inherit. The sidecar `registered_product.json` says so in
    words (`"transform": null`, `"frame": "reference image pixels"`). That is honest, but a judge
    who opens it in QGIS sees an ungeoreferenced raster. **Demo a pair that has a grid**, or say
    the sentence before they ask.
30. **NEW: `requestAnimationFrame` throttles to ~358 ms when the Chrome window is not OS-frontmost**,
    even with `document.visibilityState === "visible"`. This is Known issue 20 in a second guise,
    and it makes a DevTools-driven page look one step behind. Anyone scripting the console must
    await `requestAnimationFrame`, not `setTimeout`, or they will file bugs that are not there.
