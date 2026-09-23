# STATUS — 23 September 2026. National round, solo push.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM — read with `utf-8-sig`).
> Set `PYTHONIOENCODING=utf-8` for scripts that print → ° ↔ (cp1252 console crashes on them).

---

## Position

```
Wed 23 Sep        |  submit Sun 27 Sep (4 days)  |  portal closes Tue 30 Sep
Evidence cut-off  Thu 24 Sep 18:00     <- the only hard deadline with work behind it, TOMORROW
Deck/portal final Fri 25 Sep 22:00
Read PDF cold     Sat 26 Sep
Submit            Sun 27 Sep
```

**The submission is DONE and sitting on disk.** Deck v8 PDF, portal text, evidence frozen, all
committed and pushed. The repository is public and slide 6 carries its URL. Nothing is
half-finished. Everything from here is either the TMC-2 decision below (deadline: tomorrow) or
optional upside.

The old college-round gates (Days 5, 8, 10, 11, 12) are all past and do not apply. The national
round has cut-offs, not gates — the four dates above are all of them.

## Read this first

1. **Evidence is FROZEN at `7dd4e5b`** (10/10 steps; 183/183 real rows, 324/324 MiLOI, 8/8
   multi-modal). `--check` at a later HEAD prints NOT FROZEN because the rows name `7dd4e5b`, not
   HEAD — that is expected and not a bug. The test that matters:
   `git diff 7dd4e5b HEAD -- core evaluation ops baselines app` — as of tonight this shows the
   frozen evidence CSVs, docs, and exactly one behavioural change since the freeze:
   `ops/make_report.py` gained a rendering-only in-sample table for the OHRC→TMC-2 section
   (commit `3fa526b`, tonight). It reads no new evidence file and writes none; the `REPORT.md`
   diff against the frozen render is the header timestamp and one new table, no logged number
   changed. `ops/trust_real_calibration.py` is still 0 behavioural lines (comments only).

2. **Deck is v8**, commit `f876759`. `AUDIT: clean`, `PDF CHECK: clean`, 6 pages,
   **1,090,972 bytes**, sha256 `ae571678…`. This is the file for the portal:
   `presentation/SIH26166_LunaXX_deck.pdf`.

   The full arc, v4→v8, so nobody re-litigates it: v4/v5 were correct and read like a lab
   report. v6 was a pitch rewrite — same figures, argument reshaped, thesis moved to the front.
   Two claim-check passes (v6→v7, v7→v8) each found real defects and both were fixed the same
   night; nothing shipped uncorrected. The last fix (v8) restored a "160 windows / 8 pairings"
   line that had been accidentally dropped from every slide, and upgraded the OHRC→TMC-2 bullet
   from an argument-by-construction to a measured one: **0.13–0.96 px per axis in-sample on
   6–7 inliers, 0% of held-out matches within 3 px, on all four windows** — the exact regime
   the strongest visible competitor's own README admits it ships (in-sample only, no held-out
   validation possible). That is now the headline of slide 4's hardest bullet, not a caveat.

   **Exporting the PDF needs PyMuPDF on `PYTHONPATH`** — deliberately not in the demo venv
   (`presentation/export_pdf.py` docstring). What works, first try:
   `pip install --target <scratch>/pylibs pymupdf`, then
   `PYTHONPATH=<scratch>/pylibs python -m presentation.export_pdf`. Without it the print still
   happens but the crop does not, and the script leaves an **uncropped** PDF in `%TEMP%` with
   white bands — do not upload that one. `export_pdf` intermittently prints "NO PDF" (Known
   issue 17) — kill POWERPNT, wait 10–20 s, retry; every retry so far has succeeded.

3. **The Mission Console**, `web/`. A dark instrument-panel front end over the frozen evidence;
   `app/streamlit_app.py` is untouched and is still what Gate 4 (finale) tests. Also published
   as a Claude Artifact at **https://claude.ai/artifact/LbbZKdvnVYCCBbPjEBZCA9** — private, and
   its render/share state has never been verified from a session (Known issue 23). Slide 6
   points at the public repo instead, which needs no login and was verified logged-out.
   - Covers all 8 instrument pairings and all 3 verdicts (10 pairs in the roster).
   - `python -m web.server` adds a LIVE bay that registers a pair you upload, calling
     `core.pipeline.run_all` directly. Verified end to end through the browser's own file inputs.
   - It writes nothing and lives outside `core/ evaluation/ ops/ app/`.
   - Build writes TWO files: `dist/index.html` (a complete document — open this one by hand or
     serve statically) and `dist/mission-console.html` (a fragment, Artifact-only — opening it
     directly lands in quirks mode with 60 mojibake sequences). Operator guide: `web/README.md`.
   - Lighthouse (snapshot, desktop): accessibility 100, best practices 100, SEO 100, 0 failures.

4. **The explainer video pipeline is unfinished, on purpose.** `web/dist/mission-console.mp4` is
   built and silent (1600×1000, 12 fps, 108 s, 7.6 MB). `web/voice.py` has never made a live
   call — no Gemini key yet — and even with a key, **the narration script does not fit the cut**:
   16 beat headings sum to exactly 108.0 s but the spoken lines total 790 words = 327 s at
   145 wpm, 3× over (Known issue 27). Do not spend a TTS call on it until it is cut to ~260
   words or the beats are re-timed. This is optional upside, not submission work.

## In flight — resume here

**Nothing is running.** No server, no background job, no PowerPoint process. Working tree clean,
pushed to `origin/main` at `f876759`.

**The first thing to pick up is the TMC-2 decision below — it is now urgent, not optional.**
"Decide by Wed 23 Sep" was today. It is still undecided: `C:\Users\samar\sih26166_data\calibrated\`
has no `20251107` folder, confirmed by listing it tonight. The evidence cut-off is **tomorrow**,
Thu 24 Sep 18:00. If the download does not start early tomorrow there will not be time for the
full chain (cut → run → freeze → re-read every deck row → rebuild → re-export → claim-check),
which the last session measured at about two hours once the download is in hand.

## Samartha — what is actually left

1. **TMC-2 closer-Sun pass — decide and start TOMORROW MORNING, not later.** Needs a PRADAN
   login and a 0.6–0.9 GB download of `ch2_tmc_ncn_20251107T2205342105_d_img_d18.zip`
   (calibrated nadir; PRADAN Table View, TMC-2, 2025-11-07). Commands are in
   `ops/specs/day_24.md` under "The one measurable improvement left". It is the only pass over
   SAC's frame with the Sun ~9° in azimuth from the OHRC's. **Either outcome is a publishable
   result** — if it registers, slide 4's weakest line becomes a second success; if it refuses at
   ~9° of Sun (much closer than the 120° pass already on the deck), that is a *stronger*
   statement about the trust layer than anything currently on the slide. Not running it at all
   is the only outcome that leaves the gap open. If the download or the chain does not finish
   in time for the Thu 18:00 cut-off, do not force it — the deck as shipped (v8) is complete and
   submittable without this.

2. **Put `C:\sih26166_backup\` on a USB stick**, if not already done. `weights/`, `data/pairs/`,
   `demo_cache/` — gitignored, inside OneDrive, and the only unrecoverable thing in this
   project. Not verified from this session (it is a physical action).

3. **Read the v8 PDF cold**, then portal: PS, title, description from `SUBMISSION_FIELDS.md`,
   upload the PDF, screenshot the confirmation. **Open `github.com/samarthputhraya/sih26166` in
   a private/logged-out window first** and confirm it loads — a dead link on slide 6 is worse
   than no link. Verified reachable tonight (HTTP 200, logged-out).
   - If the TMC-2 pass lands before Fri 25 Sep 22:00, the deck needs one more rebuild/export/
     claim-check cycle before this step. If it doesn't land, skip straight to submitting v8.

4. **Optional, in rough order of value:** rehearse the Mission Console and the v8 deck numbers
   cold (nobody has yet, and the finale wants each module explained without notes); cut the
   video narration to fit the film, then voice it if a Gemini key arrives; a by-hand Gate 4 run
   through `app/streamlit_app.py`.

5. **If a judge will browse the repo**, spend ten minutes on `ops/specs/` and `ops/audit/`. They
   are honest working notes addressed to teammates, not to a reviewer. Nothing in them is
   wrong; some of it is stale in a way that invites a question not worth spending time on
   (Known issue 15).

## Open questions

1. **Portal mechanics** — draft save? editable after submit? character caps? The long
   description is 1,804 characters; the 507-character short version is ready if there is a cap.
2. **SPOC** — Student Innovation and the two-PS cap; who uploads; authorisation letter.
3. **Gemini key** for the voice-over. Until it arrives `web/voice.py` is unexercised code.

## The other five

Invariant 4 (one folder per person) is **suspended** for the solo push and teammates have no
assigned work until after submission — so `spec-writer` is not run and no per-person specs are
drafted. Writing five specs for five people with no tasks would be fiction. Last delivered
state, for when they restart:

| Person | Folder | Last delivered | Now |
|---|---|---|---|
| Samrudh | `evaluation/` | synthetic data, shaded relief, metrics, results_log | idle until after 27 Sep |
| Risheeth | `baselines/` | SIFT / ORB / AKAZE + failure gallery | idle |
| Rishabh | `app/change_detection.py` | change detection | idle |
| Saniya | `presentation/` | deck template work (Samartha owns v8) | idle; may be needed for PDF export if PowerPoint access changes (Known issue 17) |
| Rohan | `data/*.csv|*.md` | pairs catalogue | idle |

**The finale still requires all six to explain their own module cold.** Nobody has rehearsed the
Mission Console or the v8 deck numbers yet. That is finale work, not submission work, but it is
not zero work — start it once 27 Sep has passed.

## Known issues — do not re-report these

1. **`residual_px` is meaningless on real pairs.** Quote `residual_median_px` or
   `holdout_inlier_rmse_px`. The held-out median is itself only robust while the inlier ratio is
   well above 0.5 — one tiled window reads 316 px at 0.542 with the alignment visibly correct
   (NCC +0.87 to +0.95). Same effect, much worse, on the OHRC→TMC-2 rows (inlier ratio
   0.05–0.07) — this is why slide 4 quotes the in-sample and held-out-agreement figures for
   that bullet, never a held-out median in metres.
2. **Duplicate windows under two ids** (`…_sw`, `…_w01_t`). Count with
   `presentation.make_figures._distinct_windows`: 160 of 177.
3. **MiLOI truth:** 81 of 321 pairs reachable; S3 (56 of 81) has no redundancy.
4. **LoFTR is weak under near-overhead Sun** (MiLOI S2). The trust layer catches it.
5. **Withdrawn rows:** `sac_tmc_fore_aft_w01..w04` are INVALIDATED. Never quote 0.019 px.
6. **NACs without a usable correction:** M1258744166RE, M1295016540LE, M1338673330RE.
   **No lit shared window:** M159642518LE, M1258737127RE.
7. **`trust_real_calibration.csv` is a fresh RNG draw whenever the trial list changes.** The 3 m
   rate has been 81%, 74%, 74%; 1–2 m 2/352, 1/352, 0/352; hard-Sun 5 m 94% then 84%. These
   are draws of one experiment, not a regression. Quote the frozen value; hedge in speech.
8. **Memory:** commit charge runs 40–50 of 53 GB; run heavy jobs one at a time.
9. **MiLOI matches were made at six earlier commits**; only re-judge and scoring ran at `7dd4e5b`.
10. **Pairs cut before `3917a1b`** have up to 16 nearest-filled edge pixels. Negligible.
11. **`build_deck`'s audit measures text boxes, not rendered text.** `export_pdf`'s footer check
    is the real test. Slides 2 and 4 are now at their type floor (11.5 pt / 11 pt) after the v8
    additions — any further text on either must be paid for with a cut, not a smaller font.
12. **Live align on a busy laptop takes 48–61 s**; demo from the cached pairs.
13. **REPORT.md's header and the multi-modal rows stamp `ops/`**: any modified file under `ops/`
    at run time marks them `-dirty`. Park doc edits elsewhere while a freeze or `make_report`
    run is in progress.
14. **13 pair folders have no images.** The picker hides them.
15. **Docs below the national-round sections** (CLAUDE.md, canonical facts §1, §10–11) are the
    college round's, kept as history.
16. **`ops.precompute_demo_cache` with no arguments caches every pair.** Always name them.
    `demo_cache/` holds 14 pairs (6 Streamlit demo + 8 console roster), not 6.
17. **`export_pdf` intermittently prints "NO PDF"** — roughly every other attempt. Kill POWERPNT,
    wait 10–20 s, retry. Check the PDF's mtime is later than the .pptx's before uploading.
18. **F18** — `ops.freeze`'s `trust` step reads the window list from the CSV it then deletes;
    lose that file and the step fails in seconds with a zero-byte log. **F19** — the freeze
    summary adds `None` to an int on a precondition-failed step, ending a completed run in a
    traceback. Both are `ops/` changes that would force another freeze. First in line after 27 Sep.
19. **Two orphan bundles** (`site_tc_ortho_mi1548_w01`, `site_tc_ortho_mi749_w01`, `057664a-dirty`)
    still show the F12 signature. In no log, referenced by nothing. Do not quote them.
20. **A backgrounded browser tab throttles `requestAnimationFrame` to ~1 fps.** Measuring WebGL
    performance on a tab that is not frontmost reports a false failure. Focused, the console
    holds 59.9 fps with 0 context losses on the Intel Arc iGPU.
21. **`NaN` is valid JavaScript but invalid JSON.** `web/panel.py` emits `None`; `web/server.py`
    uses `allow_nan=False` so a bad value fails loudly instead of silently.
22. **ffmpeg 9 removed `-vsync`.** Use `-fps_mode`.
23. **The MCP-driven Chrome is not signed into claude.ai**, so the published Artifact's
    *rendering* cannot be checked from a session — only its bytes, which were verified verbatim.
24. **`web/voice.py` has never made a live call.** No Gemini key yet. See also Known issue 27.
25. **The demo cache staleness plate raises a false alarm after ANY commit.**
    `core.export._commit(("core","evaluation","app"))` returns HEAD's sha whether or not those
    paths changed, so a docs-only commit makes every cached result render
    `CACHED RESULT commit <a> — CODE IS NOW <b>` in caution colour.
    **Do NOT run `ops.precompute_demo_cache` on `sac_ohrc_nac_w06` or
    `site_tc_morning_mi1548_w01` to "fix" this** — they are Mission Console roster pairs;
    MAGSAC++ resamples, inlier counts drift ~1%, and the console would then show numbers not in
    `REPORT.md`. That trades a cosmetic plate for an Invariant 1 break.
    **What to do instead:** (1) untick "Use the precomputed result" and run live — the plate
    disappears and results match the cache to ~1%; or (2) say out loud that
    `git diff f928995 HEAD -- core evaluation app` is empty, so the code has not moved.
    Real fix (`_commit` should return the last commit that TOUCHED the watched paths, not HEAD)
    is queued for after 27 Sep — `core/export.py` is inside the freeze stamp path, so touching
    it now would force a 90–110 minute re-freeze.
26. **The repository is PUBLIC.** Slide 6 and both portal descriptions point at
    `github.com/samarthputhraya/sih26166`; the portal has no link field, so that URL is the only
    route a judge has off the PDF. Verified reachable logged-out tonight. If it ever goes
    private again, cut the slide-6 bullet and the clause in both descriptions first.
27. **The narration is 3× too long for the film.** 16 beat headings sum to exactly 108.0 s,
    matching `mission-console.mp4`; the spoken lines total 790 words = 327 s at 145 wpm. Cut to
    ~260 words, or re-time `web/film.py`'s beats, **before** spending a TTS call.
28. **Only the first download fires per Streamlit session.** Chrome blocks repeat automatic
    downloads. **Demo rule: click "All deliverables (.zip)" and nothing else** — the other three
    files are inside it.
29. **The exported GeoTIFF for `pair_01` carries no geotransform** — `pair_01_ref.tif` has none
    to inherit. `registered_product.json` says so (`"transform": null`). Honest, but a judge who
    opens it in QGIS sees an ungeoreferenced raster. **Demo a pair that has a grid**, or say the
    sentence before they ask.
30. **`requestAnimationFrame` throttles to ~358 ms when the Chrome window is not OS-frontmost**,
    even with `document.visibilityState === "visible"`. Anyone scripting the console must await
    `requestAnimationFrame`, not `setTimeout`, or will file bugs that are not there.
31. **NEW: the OHRC→TMC-2 in-sample table** (`ops/make_report.py`, added tonight at `3fa526b`)
    reads `insample_rmse_x_px` / `insample_rmse_y_px` / `holdout_inlier_frac` from
    `real_pairs_log.csv` — these columns were already logged at the freeze but never rendered
    for the TMC section. If a future `make_report` change touches this block, re-verify against
    the frozen row values before trusting the render: `sac_ohrc_tmc_w01..w04`, RMSE X/Y px
    0.715/0.926, 0.336/0.860, 0.880/0.128, 0.962/0.700; held-out-within-3px 0% on all four.
32. **For the Q&A, the 64-cell breakdown on OHRC→TMC-2** (`real_pairs_log.csv`): per window
    0 verified / 4–5 weak / 59–60 no evidence / 0 actively contradicted. If asked "how many
    cells contradicted?": *none actively — 59 or 60 of 64 returned no usable evidence at all,
    four or five came back weak, and not one verified. The frame refuses on zero verified.* The
    slide's own wording is exact on this ("verify not one cell" is cell-level, "contradicted" is
    frame-level) — do not let it be simplified in speech to "contradicted all 64 cells".
