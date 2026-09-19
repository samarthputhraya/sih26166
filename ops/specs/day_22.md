# Day 22 (Sun 20 Sep 2026) - solo plan, Samartha + Claude

> Team split suspended for the national push (decision 18 Sep): no teammate specs, `spec-writer` not
> run. The plan previously in this file (scale rungs, SAC's pairs, Known issue 3, fig7, deck v2
> text) was all DONE on 19 Sep (commits `1c21e18`..`bae82b2`); it is in git history. Every input
> below was checked on disk at the 19 Sep ~22:15 wrap. Read `ops/STATUS.md` first.

## Track A - SIH26166 (this repo)

1. **Freeze rehearsal, overnight.** Laptop plugged in, lid OPEN (the runner keeps Windows awake
   but the lid setting still wins). `python -m ops.freeze --plan`, then `python -m ops.freeze`.
   Nothing it logs is wasted or harmful - Thursday's commit re-runs everything, latest row wins -
   but it measures the real wall time and flushes out any step that fails before it matters.
   Done when: `python -m ops.freeze --check` says FROZEN at the rehearsal commit, and the time per
   step is written in STATUS. If a step fails, its log is `<data>/freeze/<commit>/<step>.log`.
2. **`demo-medic` on the Streamlit app** (`app/streamlit_app.py`). The app has not been checked
   since the national-round work: does it load the real pairs (`data/pairs/sac_*`, `site_*`) and
   their cached results offline, CPU-only, three clean runs? The finale needs a live demo.
   Done when: demo-medic's findings are fixed or written into STATUS Known issues.
3. **REPORT.md for Q&A: one SAC-comparable number.** SAC's 0.62 / 0.57 px (arXiv:2509.04775) is an
   IN-SAMPLE control-point RMSE per axis on a 1.1179 m NAC grid. If we want to answer that question
   with a number, compute the per-axis in-sample inlier RMSE on `sac_ohrc_nac_w*` and LOG it
   (a new results_log method, e.g. `ours_insample_axis_rmse`), then add it to the SAC section of
   `ops/make_report.py` beside - never instead of - the held-out figure. Optional; skip if short.
4. **Docs that still describe the college round**: `CLAUDE.md` (Invariant 4 is suspended; the
   internal-round date; gates), `docs/00_CANONICAL_FACTS.md` §10-11. One short "National round"
   section each, pointing at STATUS - not a rewrite. Low priority.

## Track B - SIH26227 (session 2, `C:\Users\samar\dev\sih26227`)

5. Continue its PLAN.md; the go/no-go is Fri 25 Sep evening. (19 Sep: its tree had uncommitted
   `evaluation/results_log.csv` and `ops/STATUS.md` - that session's, do not touch from here.)

## Samartha (manual)

6. Portal: Team ID format (slide 1 placeholder), draft save, editable after submit, title/
   description limits. 7. SPOC: Student Innovation vs the 2-PS cap, who uploads, authorisation
   letter. 8. Power: plugged in, never sleep, lid open before item 1.

## Calendar to submission

- Mon 21 - Wed 23: fixes from items 1-2; anything the rehearsal exposed.
- **Thu 24: the freeze** - commit, `python -m ops.freeze`, `--check` must say FROZEN.
- Fri 25: fill the deck's 44 `[TBD]`s from REPORT.md (`presentation/DECK_V2_DRAFT.md` maps each
  one to its source), `claim-checker`, SIH26227 go/no-go.
- Sat 26: PDF (PowerPoint here is unlicensed - Print to PDF or another machine), portal form.
- **Sun 27: submit.** Portal closes Tue 30.

## BLOCKED

None. Item 1 needs only a committed tree; item 2 needs the app and `demo_cache/`.
