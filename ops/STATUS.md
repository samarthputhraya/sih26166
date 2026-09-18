# STATUS - 18 September 2026 (Day 20). The college internal round is over. Its result is not in the repo.

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> WARNING: the venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly. A bare
> `python` fails here with `ModuleNotFoundError: numpy` - that is the missing venv, not a broken build.

---

## 🔴 Read this first

1. **The internal round happened on Fri 11 Sep 2026** (Day 13; Day 1 was 30 Aug). The repo's
   `docs/00_CANONICAL_FACTS.md` and `CLAUDE.md` still say 9 Sep; they are wrong and have not been
   edited.
2. **Nobody has recorded the outcome.** Whether we were shortlisted in Round 1, how Round 2 went,
   and whether the SPOC is nominating us to the national SIH portal are all unknown to this repo.
   **Write them down at the start of the next session** - everything below depends on them.
3. **The national idea-submission deadline may be 20 Sep 2026 - two days from today.**
   `00_CANONICAL_FACTS.md` §10 records 20 Sep for SIH26166 idea submission and 30 Sep for SPOC
   portal nomination, with an unresolved conflict against a 15 Sep date in the SPOC guidelines.
   If we were nominated, confirm with the SPOC **tomorrow** which date binds and whether the
   uploaded PDF (`presentation/SIH26166_deck_UPLOAD.pdf`) is what goes to the portal.

---

## Position

```
Day 20  |  Internal round: 11 Sep, DONE, result unrecorded
Gate 1: PASSED (Day 5)      Gate 2: PASSED (Day 6)
Gates 3, 4, 5: never recorded in the repo; all scheduled before 11 Sep, so now moot
Next gate: none defined. The gate plan ended at the internal round.
Novelty weight: 25% (confirmed Day 5)
```

## Verified this session, by command (18 Sep)

| Check | Result |
|---|---|
| `pytest evaluation/ -q` | **24 passed**, exit 0 |
| `import core.pipeline` | OK, exit 0 |
| `git fetch` | origin/main has nothing new; local was 1 commit ahead before tonight's push |

---

## What changed since the last STATUS (10 Sep night)

| Commit | What |
|---|---|
| `e41473c` (11 Sep) | **`ops/ROUND2_SCRIPT_SOLO.md` added.** On the day, Round 2 changed to one presenter, seven-minute cap. The solo script covers context, need, solution, evidence and impact over the five content slides; 844 spoken words = 6:41 at 130 wpm with clicks (6:29 with the bracketed passages dropped); per-slide clock checkpoints; cut-downs to 4 min and 90 s; a numbers table naming the `results_log.csv` row behind every spoken figure; eight Q&A answers. Slide 5 rewritten in plain language as three reasons: landing, finding changes, cost. `ops/ROUND2_SCRIPT.md` got a banner pointing to it. |
| this commit | This STATUS, and `ops/specs/day_20.md`: five small, outcome-independent specs for Day 21 (README and dataset-card drift fixes in each owner's folder, Saniya's `DECK_STATUS.md`, and a "round record" everyone who was present fills in). `spec-writer` reported BLOCKED: none. |

Also produced in-session on 11 Sep but **not stored in the repo** (they went straight into forms):
a problem-statement-and-solution overview for a college form, one-word team roles
(Samartha Architect, Rohan Data, Samrudh Evaluation, Risheeth Benchmarking, Rishabh Detection,
Saniya Presentation), and a project-title answer. The project has no name of its own; the
deck's slide-2 line is *"A lunar image-registration engine that knows when it is wrong"*.

---

## Per person

| Person | Last push | Delivered | Blocked on |
|---|---|---|---|
| **Samartha** | 11 Sep, `e41473c` | core/, the app, the deck build, all Round 2 scripts | recording the round's outcome |
| **Rohan** | 2 Sep, `f486e1c` | data pairs, provenance, licences | nothing in the repo; next step depends on the outcome |
| **Samrudh** | 3 Sep, `580d371` | evaluation/, ground truth, results log | same |
| **Risheeth** | 3 Sep, `fa40590` | baselines/ (SIFT, ORB, AKAZE) | same |
| **Rishabh** | 3 Sep, `483dcc2` | `app/change_detection.py`, limitations doc | same |
| **Saniya** | no commits under her name | portal deck values, team name, deck design | same |

---

## In flight

**Nothing half-finished in the code.** The one thing to resume first is not code:

> Record the internal-round outcome in this file - shortlisted in Round 1 or not, Round 2 result,
> national nomination yes/no, and any judge questions people remember. Then decide whether there
> is a next phase (national idea submission, then a December Grand Finale per §10), and only then
> write a new gate plan.

If nominated, the two concrete tasks are: (1) confirm the submission deadline and exact portal
PS-ID format (`SIH26166` vs `26166`, see Open questions); (2) re-verify the deck PDF is the
submitted version (`SIH26166_deck_UPLOAD.pdf`, sha256 `5f6adbc7931d1896`, gitignored, on this
machine and in Drive).

---

## Open questions

1. **What happened on 11 Sep?** Round 1 shortlist, Round 2 result, nomination. Unrecorded.
2. **Which national deadline binds - 15 Sep or 20 Sep?** Unresolved since 3 Sep. If 15 Sep, it
   has passed.
3. **Does the portal show the PS ID as `SIH26166` or `26166`?** Slide 1 says `SIH26166`. If the
   portal differs, change `TITLE_META` in `presentation/build_deck.py` and rebuild.
4. **Is there a next phase at all?** If not, the repo should be tidied and archived, not extended.
5. **Does `app/README.md` belong to Rishabh?** The ownership rule names only
   `app/change_detection.py`; all four README commits are his. Confirm before sending his Issue.

---

## Known issues - do not re-report these

1. **Gates 3, 4 and 5 have no evidence in the repo** and were all scheduled before the round.
   They cannot be retroactively passed; treat them as never recorded.
2. **The Streamlit demo has never been checked by `demo-medic`** against the current build. Run it
   before any future demo.
3. **`docs/00_CANONICAL_FACTS.md` and `CLAUDE.md` still say the round was 9 Sep.** It was 11 Sep.
   Not edited; fix when the docs are next revised.
4. **`ops/PITCH.md` has drifted from the deck** ("~2 km", "200+ OHRC scenes" with no source).
   Superseded by `ops/ROUND2_SCRIPT_SOLO.md`.
5. **PowerPoint on this machine is unlicensed**; COM export is refused (`0x80048240`). PDF export
   needs File > Export by hand or Print to PDF, then the PyMuPDF crop. Close PowerPoint before any
   rebuild or `build_deck` fails with PermissionError.
6. **`64` and `35` on slide 2 count different things.** 64 = every grid cell; 35 = cells the area
   check could score. Zero of the 35 agreed.
7. **No teammate has pushed since 3 Sep.** Not a fault; the work after that was the deck and the
   script. But any new phase starts with everyone pulling `main`.
8. **`docs/00_CANONICAL_FACTS.md` §7 says `rmse_gt_px` applies to "Synthetic + Tier D only".**
   The log has exact ground truth only for tiers `synthetic` and `same-frame fractional shift`;
   the four Tier D rows that fill it measure against an FFT *estimate*. Samartha's file; not
   edited tonight.
9. **`docs/00_CANONICAL_FACTS.md` §14 lists `baselines/results_table.csv`;** the real file is
   `baselines/results.csv`.
10. **Teammates' READMEs have drifted** (`evaluation/README.md` calls the residual a "lower bound";
    `app/README.md` predates commit `80f198b`; `data/DATASET_CARD.md` says the never-run B+ pair
    "proves scale invariance"; `baselines/draw_failure_gallery.py` cannot load a real pair). Each
    is assigned to its owner in `ops/specs/day_20.md`.
