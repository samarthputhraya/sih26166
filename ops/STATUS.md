# STATUS - 9 September 2026. **TODAY IS THE EVENT.**

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> WARNING: the venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly. A bare
> `python` fails here with `ModuleNotFoundError: numpy` - that is the missing venv, not a broken build.

---

## Position

```
Day 11 of 11  |  9 SEP 2026 - THE INTERNAL HACKATHON IS TODAY
Gate 1: PASSED (Day 5)      Gate 2: PASSED (Day 6, one day early)
Gates 3, 4, 5: NOT RECORDED IN THE REPO - see "What is unknown" below
Novelty weight: 25% (confirmed)
```

## Verified right now, by command, this session

| Check | Result |
|---|---|
| `pytest -q` | **242 passed**, exit 0 |
| `git status` | clean, nothing uncommitted |
| `main` vs `origin/main` | in sync, 0 unpushed |
| Total commits | 135 |
| Evidence log | 277 rows, append-only guard passing |

The code, the evidence and the documents are in the state the 5-6 Sep sessions left them. Nothing
has regressed.

## What is unknown, and it is being stated rather than assumed

**There are ZERO commits between 6 Sep and today.** No gate evidence file was written, and no
document was touched. So from the repo alone I cannot tell whether Gate 3 (a stranger operates the
UI), Gate 4 (three wifi-off runs) or Gate 5 (all six answer cold) were actually run.

They may well have been run offline. **The repo simply does not record it**, and this file will not
claim they passed. If they were run, say so out loud today; if they were not, the demo is optional
per the SPOC and the deck carries the round regardless.

## 🔴 In flight - THE ONE THING FOR THE NEXT SESSION

**Saniya has made a PPT and it needs reviewing before it is presented or uploaded.**

**It is not in this repo.** The only PowerPoint files here are `SIH26166_deck.pptx` (5 Sep, built by
`presentation/build_deck.py`) and the blank official template. Deck files are gitignored by rule, so
hers lives in Drive / on her machine. **She will need to share the actual file at the start of the
next session.**

### The first question to ask about it, and it decides everything else

> **Was it built by running `presentation/build_deck.py`, or typed by hand in PowerPoint?**

- **If the script built it** - every number came from the audited content file and cannot have
  drifted. Then the review is quick: check the two portal fields, check the export, done.
- **If it was typed by hand** - the property that protects this whole project is gone. Every figure
  on every slide must then be checked one at a time against the audit table at the bottom of
  `presentation/DECK_CONTENT.md`. That is not a criticism of her work; it is that a typed number
  cannot be traced, and Invariant 1 is the thing the project is defended by.

### What to check it against

| Check | Where the answer lives |
|---|---|
| Every number traces to a logged row | audit table at the foot of `presentation/DECK_CONTENT.md` |
| "cross-sensor" / "multi-modal" used only where literally true | `docs/00_CANONICAL_FACTS.md` sec.2 |
| Exactly 6 slides including the title page | official instructions; `build_deck.py` docstring |
| Template's grey pointer text unedited | same - this one risks disqualification |
| Team ID + Team Name filled from the portal | `build_deck.py` lines 58-59 are still `<TEAM ID ...>` placeholders |
| Submission is a **PDF**, not .pptx | portal accepts PDF only |
| No bare pixel figure without its grid and metres | Invariant 2 |

⚠️ **`build_deck.py` lines 58-59 still hold the placeholder text.** If her deck has real values in
those fields, she filled them in PowerPoint - which is fine for the artefact, but means the script
can no longer regenerate the deck. Worth knowing before anyone re-runs it and overwrites her work.

## What was built on Day 7 (5 Sep), all pushed

| commit | what |
|---|---|
| `68b3680` | the eight design-lens findings in the demo UI |
| `03ea293` | the two Tier D pairs catalogued - the novelty pair stops calling itself "not evidence" |
| `591ec5e` | sub-pixel ships ON, the docs said OFF; the append-only log now enforces itself |
| `43d1692` | the cache stamps `-dirty` when the tree that produced it was |
| `cc5890e` | the deck's headline trust figure was not in the log - appended |
| `2d2bb5e` | the demo script, two Q&A answers, the docs describing the old UI |
| `c958eb0` | pair_01 gets its metres, with the scale's provenance stated |
| `34fa4c7` | `ops/PITCH.md` - the 3-minute spoken pitch |
| `f654dd0` | the novelty slide's detection figure had no row either - appended |
| `f02e467` | `ops/gate5/` - one card per person |
| `698232b` | `ops/UNDERSTAND_EVERYTHING.md` - the whole project taught from zero |

## The documents that matter today

| File | What it is |
|---|---|
| `ops/PITCH.md` | the 3-minute spoken script, two speakers, the five numbers to say |
| `ops/UNDERSTAND_EVERYTHING.md` | the whole project from zero, for anyone who needs to understand it fast |
| `ops/gate5/<NAME>.md` | one card per person: their part, why it is hard, what it does NOT do |
| `ops/QA_ANSWERS.md` | the questions judges ask, with answers |
| `presentation/DECK_CONTENT.md` | what is on each slide, and the row behind every number |
| `ops/SANIYA_DECK_AND_PITCH_GUIDE.md` | the deck build and quality pass |

## The five numbers, and nothing else

| Number | What it is |
|---|---|
| **~2 km** | how wrong a matcher that reported success actually was |
| **2.88x** | better than best classical at 15 deg sun difference |
| **14x** | verified vs no-evidence cell accuracy, hard cases |
| **77% / 0%** | failure detection rate, false-alarm rate |
| **150 m** | the floor below which we cannot detect an error |

**Never say:** cross-sensor - multi-modal for anything but optical-vs-elevation - the 62,519x ratio
- any Tier D residual as an accuracy - "43.9 km" (that is a fit residual times the grid) - a pixel
figure without its grid and its metres.

## Known issues - do not re-report

1. **OneDrive has silently rolled back working-tree files twice** (3 and 5 Sep). Once it undid a
   reference-grid fix; once it restored a wrong figure that had already been corrected. **Run
   `git status` first thing every session.** A rollback looks exactly like an edit.
2. `core/reliability_calibration.csv` is a derivation, not a log - the script opens it `"w"`.
   Always run the full delta list.
3. `presentation/sih_template.pptx` is gitignored; a fresh clone has no template. The curl command
   is in `DECK_CONTENT.md`.
4. No real pair with a sun difference. Stated openly; not a blocker.
5. No cross-sensor pair and no IIRS infrared pair. Stated openly; the answer is written in
   `QA_ANSWERS.md` sec.1 and sec.3.
6. `redetect()` unwired - claim removed, not deferred.
7. The demo cache stores absolute paths from this machine. Non-fatal since `c958eb0` - the app
   renders a void plate and an `IMAGES NOT READABLE` strip instead of crashing.

## Open questions

- Submission deadline, 15 vs 20 Sep - still unasked of the SPOC.
- The rest of the grading rubric. Novelty is 25%, confirmed. The remaining 75% is inferred.
