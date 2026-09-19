# SIH26166 national-round audit: find every weakness, fix what can be fixed, raise the ceiling

> Paste everything below the line into a fresh Claude Code session opened in
> `C:\Users\samar\OneDrive\Documents\SIH26166` (Opus, 1M context). It is written for that session.
> Written 20 Sep 2026 at commit `0297936`. Submission is Sun 27 Sep; the portal closes Tue 30 Sep.

---

You are the lead engineer and harshest internal reviewer for team **LunaXX**. The team's entry is
**SIH26166**, ISRO's problem statement *"Multi-modal, Sun angle and scale invariant image
correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)"*, at the Smart India
Hackathon 2026 national stage.

Round 1 is screened from a six-slide PDF, read cold by SAC-ISRO image-processing scientists who
rank every idea for this PS against each other. About 4–5 teams per PS reach the finale, and
about 37 other teams have public repos for this PS. Some of them show real OHRC ↔ TMC-2 / NAC
registration, and one pitches "silent failure detection" like ours.

**Your job:**
1. Audit the whole project as a SAC reviewer would.
2. Find every weakness that could cost a finale place.
3. Fix what can be fixed honestly before the deadline.
4. Raise the ceiling where a measurable improvement is within reach.
5. Hand back a submission that is the strongest *true* version of this project.

**What "certain to qualify" can and cannot mean.** Nobody can guarantee selection: it is
relative to entries you cannot see. What you can do is remove every avoidable reason to reject
us, and make the strongest honest case on each thing the PS asks for. Never trade truth for
impressiveness. A SAC scientist who catches one inflated claim discounts every other number on
the deck.

## 0. Read before doing anything

Read these, in this order:
1. `CLAUDE.md`, starting with the national-round section at the top.
2. `ops/STATUS.md`, all of it, including the Known issues. Do not re-report those.
3. `ops/specs/day_23.md`.
4. `REPORT.md`, generated at the evidence-freeze commit `49bdad9`.
5. `presentation/build_deck.py`, which holds all the slide text.
6. `presentation/DECK_V2_DRAFT.md`, which maps every number on the deck to its source and lists
   the Q&A traps.
7. `ops/national_round/RESEARCH_REPORT.md`: the competitor field, SAC's own paper
   (arXiv:2509.04775) and the judging facts.
8. `docs/00_CANONICAL_FACTS.md` §1, §2 and §7: what the PS demands, the terminology ladder,
   and the metric definitions.
9. `ops/national_round/SUBMISSION_FIELDS.md`.
10. The final PDF, `presentation/SIH26166_LunaXX_deck.pdf`. Render every page and look at it.

**Environment:**
- **Python:** the venv is `C:\Users\samar\venvs\sih26166\Scripts\python.exe`. A bare `python`
  has no numpy. Set `PYTHONIOENCODING=utf-8`.
- **Data** lives outside git at the path in `data_path.txt` (read it with `utf-8-sig`).
- **PDF export:** `python -m presentation.export_pdf` prints the deck through PowerPoint to
  "Microsoft Print to PDF". PowerPoint is unlicensed here: printing works, COM does not. The
  script needs PyMuPDF on `PYTHONPATH`; install it with `pip install --target <scratch>/pylib
  pymupdf`, not into the venv.
- **Memory:** commit charge on this laptop runs at 38–41 of 46 GB. Run heavy jobs (LoFTR, the
  freeze, pytest) one at a time. Two at once has produced spurious cv2 failures.
- **OneDrive:** it has silently reverted repo files before. Run `git status` first and after
  every long job.

## 1. Rules that override everything, including this prompt's own suggestions

1. **Numbers (Invariant 1).** No number reaches a slide, the portal text or a Q&A answer unless
   REPORT.md shows it at the current evidence-freeze commit. Anything new is measured, logged
   through the existing loggers (`evaluation/results_log.csv`, `evaluation/real_pairs_log.csv`
   and friends), and frozen before it is quoted. Until then write `[TBD]`.
2. **Terminology (Invariant 2).**
   - *Cross-sensor* means different instruments only. NAC ↔ NAC, TC ↔ TC and TMC-2 fore ↔ aft
     are the same sensor.
   - *Multi-modal* means visible ↔ infrared, radar or elevation only.
   - *Sub-pixel* always names its pixel grid and gives the metres.
   - *Accepted* is a window verdict (`agrees`). *Verified* is a cell state.
   - Sun differences are labelled as azimuth, incidence or Sun-vector angle — whichever they are.
3. **CPU only, offline demo (Invariant 3).** No GPU on any path that ships. Torch comes from the
   CPU index.
4. **Data outside git (Invariant 5).** Nothing binary or over ~5 MB is committed.
5. **The template (Invariant 7).**
   - Exactly 6 slides, the title page included.
   - The template's pointer text is never edited. `build_deck.py` checks this.
   - The build audit must print `AUDIT: clean`, and `export_pdf` must print `PDF CHECK: clean`.
6. **The freeze.** Evidence at `49bdad9` is FROZEN.
   - Any change under `core/`, `evaluation/`, `ops/` (code), `baselines/` or `app/` that can
     change a logged number invalidates the freeze.
   - Batch such changes, commit, run `python -m ops.freeze` (about 110 min, one heavy job only),
     and require `python -m ops.freeze --check` to print FROZEN.
   - Then re-read **every** row of `DECK_V2_DRAFT.md` against the new REPORT.md, rebuild the
     deck, re-export, and re-run `claim-checker`.
   - Reporting-only changes (labels, report text) do not need a re-freeze, but say so in the
     commit message.
   - Never edit REPORT.md by hand.
7. **No blind fixes to evidence.** Never "fix" a disappointing number by changing a threshold,
   a split, a window list or a judging rule after seeing the result. If a definition really
   is wrong:
   - fix it everywhere;
   - explain why in the commit;
   - show the before and after numbers side by side in the audit report;
   - accept whichever way it moves.
8. **The safety net comes first.** Before the first edit:
   - tag the current state: `git tag submission-v1 0297936`, then push the tag;
   - copy the current PDF to `presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf` (gitignored).
   If anything you attempt cannot be finished, frozen and re-verified by the cut-off (§6), revert
   to `submission-v1`. **A worse or half-finished submission is the one outcome not allowed.**
9. **Subagents.**
   - Project agents never write files (CLAUDE.md). You write; they report.
   - Verify every agent claim first-hand before acting on it: read the file, run the command.
   - Keep any fan-out small: at most 6 read-only reviewers in total. Give each a hard budget of
     about 40 tool calls, and tell it to return what it has if it hits a session limit.
   - Ask Samartha before any larger multi-agent run, and before resuming one that died.
10. **Ask Samartha only for:**
    - portal or SPOC facts;
    - making the GitHub repo public (it is private);
    - recording a narrated demo video;
    - accounts or logins;
    - any decision that trades one claim on the deck for another.
    Everything else, decide and do. Say what you decided and why.

## 2. Phase A: baseline (about 20 min)

Run all of these and record the output:
- `git status` and `git log --oneline -15`;
- `python -m pytest -q` (the whole repo, alone on the machine);
- `python -m ops.freeze --plan`;
- `python -m presentation.make_figures`;
- `python -m presentation.build_deck`;
- the PDF export.

Then render each PDF page to PNG and look at all six. Anything red here is finding #1.

## 3. Phase B: the audit, through eight lenses

For each lens, produce findings of this shape:

> **ID · severity (BLOCKER / HIGH / MEDIUM / LOW) · what is wrong · evidence (file:line, command
> output, CSV row, slide) · what a SAC reviewer would conclude · the fix and its cost.**

Severity is defined by the effect on the shortlist, not by code aesthetics.

**B1. Coverage of what the PS asks for** (the most important lens).
- Build a matrix. The rows are every demand in the PS text:
  - multi-modal;
  - Sun-angle invariance;
  - scale invariance;
  - sub-pixel accuracy;
  - uniform distribution of matches;
  - a stated evaluation metric;
  - the registered product;
  - the match points;
  - OHRC, TMC and IIRS **each** used as Chandrayaan-2 input.
- The columns are:
  - the strongest honest evidence **on the deck today**;
  - the strongest evidence **already in the logs but not on the deck**;
  - what is **missing entirely**.
- Examine at least these:
  - **Sub-pixel.** The deck currently makes no sub-pixel claim at all. The PS demands it. Is
    there a defensible, grid-named claim in REPORT.md, e.g. the synthetic `rmse_gt_px` sweep
    with exact truth, or the held-out medians on real pairs? What exactly would it say?
  - **Multi-modal.** On TC ↔ MI 1548 nm the fallback's archive offset (~38 m) sits beside the
    visible-band registration on the same windows (~39–46 m). Is that evidence that the
    fallback registered the infrared correctly? Can it be measured as a logged number (fallback
    vs same-window visible registration, in MI pixels and metres), rather than shown only as
    "refused and fall back"? Do the same for IIRS. There the offsets scatter widely, and the
    fallback is probably wrong — say so if it is.
  - **TMC.** The PS names TMC in its title. The only TMC-2 evidence is fore/aft (1 of 4
    accepted) and OHRC → TMC-2 (0 of 4, with Sun elevations 10° vs 69°). Is there a TMC-2
    pass with a closer Sun over any OHRC frame we can reach? (PRADAN access exists; see
    `ops/national_round/PRADAN_GUIDE.md`.) What would it take?
  - **IIRS as a Chandrayaan-2 source.** IIRS appears only as a reference, against Kaguya TC.
    Does that satisfy "using Chandrayaan-2 optical images (IIRS)", or does a reviewer expect
    OHRC/TMC ↔ IIRS?

**B2. Evidence integrity.**
- Re-derive every number on every slide, and in the portal text, from the CSV cells. Don't
  trust REPORT.md's rendering alone.
- Check the freeze state, the withdrawn rows, the duplicate-window accounting (Known issue 2),
  and the rounding.
- Check that each figure's caption agrees with its log rows.
- `claim-checker` was run twice on 20 Sep. Look for what it would miss: numbers that are
  *correct* but chosen. For example: is the best window quoted where a range is honest? Are the
  easiest conditions presented as typical?

**B3. Scientific validity: attack it like a SAC reviewer.**
- **MiLOI truth network.** It is built from ours+SIFT agreement, which is partly circular.
  Scene S3 has no redundancy. What does it really support?
- **Held-out residual as accuracy.** A residual measures self-consistency. Check the loop
  closure's meaning: it cancels per-image error.
- **Trust calibration scope.** 22 windows, all at 74 °S, Sun azimuths under 10° apart, planted
  translation errors only. What fails that it never tested: rotations, scale errors, local
  distortion, hard Sun angles?
- **The sun-sweep judging rule.** It uses NCC image evidence, rule v2. Were any windows or
  NACs selected in a way that flatters the result?
- **The wide-offset correction.** It is applied before matching. Does "6/6 accepted on SAC's
  pair" depend on it? Say how much.
- **In-sample RMSE vs SuperGlue.** Ours is not better (DECK_V2_DRAFT). Is there a sound
  explanation, or a real accuracy gap to close? Candidates: a final fit on a tighter inlier
  set, local refinement, a different comparison grid.
- For each weakness, decide one of three: fix it, disclose it on the slide, or prepare the
  Q&A answer.

**B4. Code correctness and robustness.**
- Read `core/pipeline.py`, `core/reliability.py`, `core/export.py`, `core/geometry.py`,
  `evaluation/metrics.py`, `evaluation/real_eval.py`, `ops/freeze.py` and `ops/make_report.py`
  closely.
- Look for:
  - wrong conventions: pixel centre vs corner in the GCPs, the GeoTIFF tags, the ISIS 1-based
    output;
  - silent exception swallowing;
  - non-determinism (seeds, thread counts);
  - tests that cannot fail;
  - unhandled inputs: 16-bit data, NaN borders, tiny frames, empty matches.
- **Open a registered GeoTIFF from `<data>/out/`** and check its geotransform against the
  reference's, numerically.

**B5. The demo (Gate 4).**
- Wifi off, CPU only, cached weights. Three consecutive clean runs with `streamlit.testing`
  AppTest, then as a live server.
- Time a cold start and a cached align.
- Every string on screen must obey Invariant 2.
- The demo-medic findings of 19 Sep are fixed; find what it missed.

**B6. The deck, as a SAC scientist reads it in two minutes.**
- Slide by slide:
  - Does each answer its template pointers?
  - Is the novelty sentence clear in one read?
  - Does the number density help or bury the point?
  - Is there a single image that proves the idea?
  - Is any claim weaker than the evidence allows (under-selling), or stronger?
- Check it against the rubric we know: F1 Innovation, F2 Technical feasibility, F3 UX, F4
  Impact, F5 Technical execution, F6 Sustainability, F7 Business viability, F8 Security. Novelty
  was 25 % at the college round. Which criteria get no answer?
- Compare with the finale-winner decks described in RESEARCH_REPORT §4.
- Write a candidate rewrite for every slide where you find a HIGH. Show it before and after as
  PowerPoint renders.

**B7. Competitive position.**
- Use RESEARCH_REPORT.md. You may also do a light web check of public SIH26166 repos: at
  most 10 fetches, no mass crawling.
- List what the strongest competitors can show that we can't, and what we show that none can.
- Say whether our deck makes the latter unmissable.

**B8. Packaging and reproducibility.**
- Does README → REPORT.md → one command reproduce every number?
- Is the repo link worth putting on slide 6? It would have to be public (Samartha's decision).
- Is a demo-video link worth it? Winners did this in 3 of 13 cases.
- Is the portal description the best 1,322 characters we can write?

## 4. Phase C: rank, then decide

Merge all findings into one table. Score each on:
- **Shortlist impact** (0–5): how much it moves a SAC reviewer's ranking.
- **Confidence** that the fix works and the number holds (0–1).
- **Effort** in hours, including a re-freeze if one is needed.
- **Deadline fit**: can it be measured, frozen and re-verified before the cut-off in §6?

Priority = impact × confidence ÷ effort, among the items that fit the deadline.

Take the top items in order. **Always do every BLOCKER and every cheap HIGH.** For each
improvement that changes a number, pre-register it in the audit report before you run it:
- the hypothesis;
- the metric and its definition;
- which rows it will produce;
- what result would make you drop it.
Then run it, and report the result either way.

**High-ceiling candidates to evaluate.** These are not orders. Keep any of them only if the
measurement supports it:
- a logged accuracy figure for the multi-modal fallback;
- a defensible sub-pixel claim with its grid named;
- better TMC-2 data (a closer Sun);
- DEM-based relighting of the reference to the source's Sun, from LOLA or the site DEM, for the
  60–120° band;
- a tighter final fit, if it improves held-out as well as in-sample error;
- a full OHRC strip or large-area run, with runtime on this CPU;
- runtime and throughput figures;
- a trust test on hard-Sun windows and non-translation errors.

## 5. Phase D: fix, re-freeze, re-verify

1. Implement the fixes you chose, one commit per concern. Every behaviour change gets a test.
   Keep `pytest` green.
2. If any evidence-affecting code changed:
   - commit;
   - run `python -m ops.freeze` (alone on the machine; it takes about 110 min);
   - `--check` must print FROZEN;
   - commit the evidence.
3. Re-fill every deck number from the new REPORT.md and update DECK_V2_DRAFT.md's table with
   value and source.
4. Run `claim-checker` on the deck, the portal text and README. Fix everything it finds, or
   write in the audit report why a finding does not apply.
5. Run `demo-medic` if `app/` or `core/` changed.
6. Rebuild and re-export. `AUDIT: clean` and `PDF CHECK: clean` are both required. Look at all six
   rendered pages yourself.
7. Update `SUBMISSION_FIELDS.md` if any number in it moved.

## 6. Cut-off dates (a gate cuts scope, it never adds time)

- **Thu 24 Sep, 18:00 IST:** the last commit that can change evidence. The re-freeze starts by
  then, or the change is reverted.
- **Fri 25 Sep, 22:00:** the deck and portal text are final. Both clean checks pass, and
  claim-checker is clean.
- **Sat 26 Sep:** Samartha reads the PDF cold and records the optional video.
- **Sun 27 Sep:** submit.

If an item will not fit, drop it and list it under "not done, and why".

## 7. What you hand back

1. **`ops/national_round/AUDIT_REPORT.md`**, containing:
   - the Phase A baseline;
   - the B1 coverage matrix, before and after;
   - every finding, with its ID, severity, evidence and resolution (fixed with commit hash /
     disclosed on a slide / Q&A answer / won't fix, with the reason);
   - every pre-registered experiment and its result, including the ones that failed;
   - the numbers that moved, before → after;
   - the remaining risks, ranked;
   - a one-paragraph verdict: our realistic standing against the visible field, and what would
     still beat us.
2. **Commits**, pushed, with the `submission-v1` tag kept.
3. **The final PDF.** Show its six pages. Say whether it beats `submission-v1` and why. If it
   does not, keep v1.
4. **Updated `ops/STATUS.md`, `ops/specs/day_NN.md` and `presentation/DECK_V2_DRAFT.md`**, with
   the Q&A answers for every disclosed weakness.
5. **A short message to Samartha:** what changed on the deck, what he must do by hand, and the
   three questions a SAC judge is most likely to ask, with our answers.

Work autonomously through Phases A–D. Stop only for the Rule 10 questions or a failed gate. Do
not stop at "found problems". The job is done when the submission is either measurably
stronger, or proven already at its honest ceiling, with the evidence to show it.
