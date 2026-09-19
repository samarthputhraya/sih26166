# STATUS - 20 September 2026 (Day 22), ~01:10 IST, session wrapped. National round, solo push.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly (bare `python` has no numpy).
> External data: `C:\Users\samar\sih26166_data\` (path in `data_path.txt`, BOM - read with `utf-8-sig`).
> Set `PYTHONIOENCODING=utf-8` for scripts that print → ° ↔ (cp1252 console crashes on them).

---

## Read this first

1. **The evidence freeze is DONE: FROZEN at `49bdad9`.**
   - `python -m ops.freeze` ran 9/9 steps in 108 min (19 Sep 22:48 to 20 Sep 00:36).
   - Every latest real-pair row (146/146) and MiLOI row (324/324) names `49bdad9`.
   - The evidence is committed in `36de5f4`; REPORT.md is regenerated from it.
   - `--check` at a later HEAD will say NOT FROZEN, because rows name `49bdad9`, not HEAD. That
     is expected. The test that matters is `git diff 49bdad9 HEAD -- core evaluation ops baselines app`,
     which shows only evidence logs, docs, and the one CLI reporting hunk (Known issue 13).
2. **The deck is finished except the Team ID.**
   - All 44 numbers are filled from REPORT.md at `49bdad9`; each value and its source is in
     `presentation/DECK_V2_DRAFT.md`.
   - `claim-checker` ran twice. The second pass (on the filled deck) found 0 numeric mismatches
     plus 22 scope and label findings; all were fixed except M6 (TC rung), which went to the Q&A
     notes (`27266f8`).
   - The build audit is clean apart from `TEAM_ID`.
3. **The PDF can now be made on this laptop: `python -m presentation.export_pdf`.**
   - PowerPoint prints to "Microsoft Print to PDF" with `/pt`, even though COM does not work.
     The script answers the save dialog by keystroke and crops each page to the slide with
     PyMuPDF.
   - It checks 6 pages, each title, no `[TBD]`, and **no text running into the footer bar**.
     That last check exists because the build audit missed an overflow on slides 2 and 4 today.
   - PyMuPDF is not in the venv. Run it with
     `PYTHONPATH=<dir with pymupdf>`; this session installed one with
     `pip install --target <scratchpad>/pylib pymupdf`.
   - Output: `presentation/SIH26166_LunaXX_deck.pdf` (gitignored). While it prints, windows flash
     on screen; do not type during those ~20 s.
4. **Portal text is drafted:** `ops/national_round/SUBMISSION_FIELDS.md` has the title
   (107 or 71 characters) and the description (1,322 or 498 characters). Every number in it
   is from `49bdad9`.
5. **Demo (demo-medic, 19 Sep): all HIGH and MEDIUM findings are fixed and re-checked with AppTest.**
   - Real pairs show their tier and instruments from `geometry_prior.json`.
   - The same-sensor note fires on NAC↔NAC and TMC-2 fore/aft.
   - The downloaded report.md leads with the held-out median, as the screen does.
   - Cached pairs are listed first; old absolute paths are re-rooted.
   - All 6 caches are at the current code.
   - Gate 4 itself is still a human job: 3 consecutive offline runs, with the procedure in the
     demo-medic report.

## Position

```
Sun 20 Sep, 01:10  |  submit Sun 27 Sep (7 days)  |  portal closes Tue 30 Sep
Built: everything. Left: Team ID -> build -> export -> eyeball -> submit (Samartha, ~15 min)
```

## Verified by command (20 Sep, ~01:00, at `27266f8`)

| Check | Result |
|---|---|
| `python -m ops.freeze --check` (at 49bdad9, before the evidence commit) | FROZEN |
| `python -m pytest -q` (whole repo) | 298 passed, exit 0 |
| `python -m presentation.make_figures` | 7 figures, no overflow |
| `python -m presentation.build_deck` | 6 slides, pointers unchanged, AUDIT: only `TEAM_ID` |
| `python -m presentation.export_pdf` | 6 pages at 792×446 pt, 1.10 MB; PDF CHECK: only page 1 `[TBD]` |
| `python -m core.pipeline data/pairs/sac_ohrc_nac_w01 --out <dir>` | 8 deliverables, report.md names tier and instruments |
| AppTest: sac_ohrc_nac_w06 → Align (cached) | tier "B (OHRC-NAC real)", 4 downloads, bundle of 8 files, no exception |

## What landed this session (`49bdad9`..`27266f8`)

| Commit | What |
|---|---|
| `49bdad9` | SAC's measure logged: in-sample per-axis RMSE (`evaluation/real_eval.insample_axis_rmse`, 3 new real_pairs_log columns, REPORT table). demo-medic fixes to the app and export. Browser server address pinned. National-round sections in CLAUDE.md, canonical facts and README |
| `36de5f4` | The freeze's evidence: 146 real rows, 324 MiLOI rows, trust re-run on 22 distinct windows, synthetic sweeps, REPORT.md, figures |
| `3214e8a` | Deck numbers filled; `presentation/export_pdf.py` |
| `27266f8` | claim-checker fixes (scope and labels); fig4/fig5; slides 2 and 4 fit; footer check; CLI `--out` passes the prior; `SUBMISSION_FIELDS.md` |

## Evidence at the freeze (REPORT.md, `49bdad9`)

- **SAC equatorial:** 6/6 accepted, Sun azimuths 174° apart, held-out median 0.69–1.68 px on
  the 1.622 m grid. **In-sample per axis** (SAC's own measure) is X 0.66–1.15 px and
  Y 0.73–1.07 px, which is **not better than SuperGlue's 0.62 / 0.57 px**. Q&A only; see
  DECK_V2_DRAFT.
- **SAC polar:** 4/6 accepted, 1 unconfirmed, 1 contradicted + fallback.
- **74 °S OHRC → NAC:** 20/20 accepted, held-out median 0.41–1.0 px (0.51–0.94 m).
- **Loops:** 6, median 0.104 m.
- **Sun sweep:** 69 windows over 25 NAC frames.
- **TC rung:** 3/4 accepted.
- **Infrared:** 13/14 fall back.
- **OHRC → TMC-2:** 0/4 accepted, all refused.
- **Trust layer, planted failures:** 0/44 false alarms; 81.2% flagged at 3 m; 100% from 5 m;
  2/352 flagged at 1–2 m.
- **MiLOI:** 81 scored pairs, 56 of them in scene S3. Agrees 33/33 right; contradicted 43/43 wrong.

## In flight - resume here

Nothing is running. The tree is clean and pushed. No PowerPoint process is left open.

## Per person

The team split is suspended for the national push. No teammate has a task, and nobody is
blocked on Samartha. Nobody has pushed since 2–3 Sep, so no teammate can explain the
national-round code yet. Plan a walkthrough after 27 Sep, in case LunaXX reaches the finale.

## Samartha - to submit (ops/specs/day_23.md has the full list)

1. **Team ID.** Read it off the portal.
   - Set `TEAM_ID` in `presentation/build_deck.py`.
   - Run `python -m presentation.build_deck` (must say `AUDIT: clean`).
   - Run `python -m presentation.export_pdf` (must say `PDF CHECK: clean`).
   - Open the PDF and look at all 6 pages.
2. **Portal:** PS, title and description from `SUBMISSION_FIELDS.md`, then upload the PDF.
   Screenshot the confirmation and record it here.
3. **Optional:**
   - a 2-min narrated demo video (unlisted), with its link added to slide 6;
   - making the GitHub repo public only if a link to it goes on a slide (it is private now);
   - Gate 4 by hand: 3 offline runs.

## Open questions

1. Portal: is there a draft save? Can the submission be edited after submit? What are the
   title and description limits? (SUBMISSION_FIELDS has short and long versions.)
2. SPOC: does Student Innovation count toward the two PSs? Who uploads? Is the authorisation
   letter uploaded?

## Known issues - do not re-report these

1. **`residual_px` is meaningless on real pairs:** it is the RMSE over ALL held-out matches,
   outliers included. Quote `residual_median_px` or `holdout_inlier_rmse_px`; the latter is
   capped at 3 px by definition.
2. **Duplicate windows under two ids:** `…_w0N_sw` = `…_w0N`, and `…_w01_t` = `…_w04`. Count
   distinct windows with `presentation.make_figures._distinct_windows` (136 of 140).
3. **MiLOI truth:** only 81 of 321 pairs are reachable. S3 (56 of the 81) has no redundancy,
   so its truth error is unmeasured. The deck names S3 on both slides.
4. **LoFTR is weak under near-overhead Sun** (MiLOI S2). The trust layer catches it.
5. **Withdrawn rows:** `sac_tmc_fore_aft_w01..w04` are INVALIDATED. Never quote 0.019 px.
6. **NACs without a usable correction:** M1258744166RE, M1295016540LE, M1338673330RE.
   **No lit shared window:** M159642518LE, M1258737127RE.
7. **`trust_real_calibration.csv` is appended by every run.** `ops.freeze` deletes it first; do
   the same by hand.
8. **Intermittent cv2 failures are most likely memory-commit exhaustion.** Commit charge runs
   at 38–41 of 46 GB: about 22 idle `claude` processes from 17–19 Sep (~12 GB) plus Chrome
   (~8 GB). One pytest run next to a 3.5 GB app process had 47 cv2 failures; the same run
   alone was clean. Run heavy jobs one at a time, and close old Claude sessions.
9. **The MiLOI matches were made at six earlier commits.** Only the re-judge and scoring ran at
   `49bdad9`. `--plan` verified that the matching code is unchanged since.
10. **Pairs cut before `3917a1b`** have up to 16 nearest-filled edge pixels. This is recorded
    and negligible.
11. **The build audit checks text boxes, not rendered text.** Overflow is caught only by
    `export_pdf`'s footer check, so always export before trusting a deck edit.
12. **Live align on a busy laptop takes 48–61 s** (demo-medic). Demo from the cached pairs,
    listed first and marked "(cached)".
13. **One post-freeze code change:** `core/pipeline.py` CLI `--out` now passes the prior to
    `export_bundle` (`27266f8`). It is reporting only; no evidence path uses it and no logged
    number changes.
14. **13 pair folders have no images** (`site_m…re_w01..05,07,08`,
    `site_ohrc_m1363141432re_w01,02,03,05,07,08`). The picker hides them. No deck or doc names
    them.
15. **Docs below the national-round sections** (CLAUDE.md, canonical facts §1 and §10–11)
    are the college round's, kept as history. The national sections at the top win.
