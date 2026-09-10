# STATUS - 10 September 2026, night. **THE EVENT IS TOMORROW, 11 SEPTEMBER.**

> Rewritten in full at the end of every session. Previous STATUS is in git history.
> WARNING: the venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly. A bare
> `python` fails here with `ModuleNotFoundError: numpy` - that is the missing venv, not a broken build.

---

## 🔴 The date was wrong in this repo, and it is now corrected here

Every document still says the round is **9 September = Day 11**. It is not.

**The SPOC's own schedule (`SIH 2026 - Schedule_Instructions_Evaluation criteria-1.pdf`, in
Downloads) says Friday 11 September.** Day 1 was 30 Aug, so the event is **Day 13**, and today,
10 Sep, is Day 12.

`docs/00_CANONICAL_FACTS.md` §10-11 and `CLAUDE.md` still carry 9 Sep. **They were not edited this
session** - they are outside `presentation/` and `ops/`, and changing four documents at 8pm the
night before is how a wrong edit ships. Fix them after the round, or read this file instead.

### The schedule, verbatim from that PDF

```
08:45-09:30  Team leaders report to B Block Seminar Hall
09:00        Team members report to their assigned classrooms
10:00-11:30  Inauguration -> guidelines -> evaluation setup
11:30-12:00  ROUND 1 - evaluated on criteria F1-F8   <- the PPT alone, nobody presents
12:00-12:30  Evaluation and result compilation
12:30        ROUND 1 RESULTS - shortlist announced
13:00        ROUND 2 - criteria F9 & F10, shortlisted teams only
```

Formal dress: white shirt, black trousers. **All six must be present for Round 2.**
Only Round-2 qualifiers receive certificates.

### The real criteria - no longer inferred

F1 Innovation & Creativity · F2 Technical Feasibility · F3 User Experience & Design ·
F4 Impact & Usefulness · F5 Technical Execution · F6 Sustainability & Future Scope ·
F7 Business Viability · F8 Security & Privacy · **F9 Presentation & Communication** ·
**F10 Collaboration & Teamwork**.

Round 1 = F1-F8, from the PDF, with nobody in the room. Round 2 = F9 + F10 only.

---

## Position

```
Day 12 of 13  |  EVENT IS TOMORROW, 11 SEP 2026
Gate 1: PASSED (Day 5)      Gate 2: PASSED (Day 6, one day early)
Gates 3, 4, 5: STILL NOT RECORDED IN THE REPO - see Known issues
Novelty weight: 25% (confirmed)
```

## Verified this session, by command

| Check | Result |
|---|---|
| `pytest -q` (full) | **242 passed**, exit 0 |
| `pytest evaluation/ -q` | **24 passed**, exit 0 |
| `import core.pipeline` | OK, exit 0 |
| `python -m presentation.make_figures` | 4 figures, all three figure audits clean |
| `python -m presentation.build_deck` | 6 slides, `AUDIT: clean`, pointers unchanged |
| Final PDF | 6 pages, exact 16:9, no banned strings, nothing required missing |

---

## ✅ DONE AND READY TO SUBMIT

**`presentation/SIH26166_deck_UPLOAD.pdf`** - 6 pages, 11.000 x 6.1875 in (exact 16:9),
1,098,333 bytes, sha256 `5f6adbc7931d1896`. **`SIH26166_deck.pdf` is byte-identical**, so
whichever file is uploaded is the correct one. Both are gitignored and live only on this machine
and in Drive.

Round 1 is a PDF read without us present, so the deck was rebuilt to be read that way:

- **Every heading is one of the template's own pointers**, in the template's order. An evaluator
  reads down the grey prompts and finds each answered directly beneath. The earlier build used
  headings we invented ("The finding, not the feature", "Built, tested, usable") and never
  answered "Detailed explanation of the proposed solution" at all.
- Team ID **SNPSU0192**, team name **SNPSU LunaX**, taken from Saniya's portal deck.
- The template footer "@SIH Idea submission- Template" is cleared; the bar and page number stay.
- Four generated figures, one on every content slide, including the trust map itself.

### What the build now checks on every run, so nobody has to eyeball it

`build_deck._audit_deck`: 6 slides · every shape inside the 0.55-12.78 in band · nothing in the
footer bar · no figure overlapping a text box · **Calibri named for latin, ea AND cs on every run**
· every bullet has a hanging indent · no box mixes terminal full stops · nine banned strings absent
· team ID/name/`SIH26166` present. `_check_pointers`: pointer text byte-identical.
`make_figures._audit` and `._overflows`: no label wider than its box, no text off-canvas, no text
printing through other text, and the **effective on-slide point size** of every figure.

**The font rule is not cosmetic.** The template's theme sets `<a:latin>` to Calibri but leaves
`<a:ea>` and `<a:cs>` empty, so inherited runs sent `°` and `×` through East-Asian font linking -
the 9 Sep build rendered "at a 15°   sun difference" and "2.88 ×  better" with gaps nobody typed.

---

## 🔴 IN FLIGHT - the first thing tomorrow morning

**Nothing is half-finished in the repo.** The deck is built, verified, exported and cropped; the
script is written and checked. What remains is human, and it is all in one file:

### `ops/ROUND2_SCRIPT.md` - read your own section, nobody else's

Word-for-word scripts for all six, built for F9 and F10:

| Who | Owns | Their opening idea |
|---|---|---|
| Samartha | the problem, then the engine | opens on the 2 km failure; "it never looks at a single match" |
| Rohan | the chain of custody | "we tried five times to cut that pair. Five times it failed" |
| Samrudh | how we know | "I am the exam marker. I never touch the alignment" |
| Risheeth | the comparison | "I am the control group. My job is to make our result falsifiable" |
| Rishabh | what the gate protects | "a shadow that moved is a difference. A new crater is a change" |
| Saniya | impact and the close | Vikram, LUPEX, then the one sentence |

**Ownership, not one-slide-per-person** - five content slides do not divide by six, and taking
turns reading loses F9 while four silent people lose F10.

**Length ladder** (measured from the prose at 130 wpm, not estimated): **6:53** with the
⟨angle-bracket⟩ passages, **5:46** without them, 3:00 and 1:30 cuts in §8. Every story and every
headline number sits outside the brackets. **Ask the SPOC the slot length before 1 PM.**

Also in that file: handover choreography, Q&A routing by module owner, the three-layer answer rule,
the never-say table, the AI answer, and the rehearsal plan.

---

## Per person - what to do tomorrow

| Person | Tomorrow |
|---|---|
| **Samartha** | Upload the PDF. Hold the clicker for the whole pitch. Segments 1 and 3. Answers the pipeline, the trust layer, the 150 m floor, and the AI question. |
| **Rohan** | Segment 2. Answers data provenance, licences, what we could not get. |
| **Samrudh** | Segment 4. Answers ground truth, calibration, the evidence log. |
| **Risheeth** | Segment 5. Answers the classical baselines and where we lose. |
| **Rishabh** | Segment 6. Answers change detection and the 183 -> 0 gate. |
| **Saniya** | Segment 7. Answers the deck and how it was built. **Do not say we used DFSAR - it is radar and not ours.** |

Everyone: read `ops/gate5/<YOUR NAME>.md` once tonight, then explain your module to someone
outside the team in 60 seconds with no jargon.

---

## Open questions

1. **How long is the Round 2 slot?** The schedule says "1:00 PM onwards" and gives no duration.
   This decides which version of the script is used. **Ask the SPOC before 1 PM.**
2. **Is a live demo wanted in Round 2?** The SPOC previously confirmed a demo is not mandatory.
   See Known issues #2 before offering one.
3. **Does the portal show the PS ID as `SIH26166` or `26166`?** Slide 1 says `SIH26166`; Saniya's
   deck said `26166`. If the portal disagrees, change `TITLE_META` in `build_deck.py` and rebuild.

---

## Known issues - do not re-report these

1. **Gates 3, 4 and 5 have no evidence in the repo.** There are still zero commits between 6 Sep
   and 9 Sep. Whether a stranger drove the UI, whether the demo survived three wifi-off runs, and
   whether all six answered cold are all unrecorded. This file does not claim they passed.
2. **The Streamlit demo is unverified for tomorrow.** Following from #1, `demo-medic` has never
   been run against the current build. **Do not offer a live demo unless it survives three
   consecutive offline runs on Samartha's laptop first.** A failed demo costs more than no demo.
3. **`docs/00_CANONICAL_FACTS.md`, `CLAUDE.md` and `ops/STATUS.md` history all say 9 Sep.** The
   event is 11 Sep. Corrected at the top of this file only; the other documents were deliberately
   not edited tonight.
4. **`ops/PITCH.md` has drifted from the deck.** It still says "~2 km" where the deck and
   `ROUND2_SCRIPT.md` say "over 2 km", and it still carries "200+ OHRC scenes", a count with no
   source in this repo. `ROUND2_SCRIPT.md` supersedes it for tomorrow.
5. **PowerPoint on this machine is an unlicensed install.** COM automation is refused
   (`0x80048240`), so the .pptx cannot be exported to PDF programmatically - a human must run
   File > Export, or Print > Microsoft Print to PDF. It also takes an exclusive lock: **close
   PowerPoint before any rebuild**, or `build_deck` fails with PermissionError.
6. **Print to PDF letterboxes onto Letter paper.** The export arrives 11 x 8.5 in with the 16:9
   slide centred. The crop step (PyMuPDF `show_pdf_page` with a clip) is what produces the
   uploadable file; it preserves vector text and loses no ink.
7. **`64` and `35` on slide 2 count different things** and now say so on the slide. 64 = every cell
   in the 8x8 grid; 35 = how many the independent area check could score (`n_meas =
   np.isfinite(area_ncc).sum()`). Of the 35, zero agreed - that is what trips CONTRADICTED.
   If asked why not 64: "the other 29 gave the check no usable signal; we don't score what we
   can't measure, and we don't guess it either."

---

## What changed in the repo this session

| File | Change |
|---|---|
| `presentation/build_deck.py` | Rewritten against the template's pointers; real bullets with hanging indents; Calibri on latin/ea/cs; template footer cleared; symmetric margins; `_audit_deck` self-check; portal Team ID/Name |
| `presentation/make_figures.py` | Trust map restacked vertically; pipeline flowchart added; all type enlarged for on-slide legibility; `_audit` (off-canvas + text-overlap + effective point size) and `_overflows` |
| `presentation/DECK_CONTENT.md` | Slide sections now **generated from `build_deck`**, so the record cannot drift from the file |
| `presentation/figures/` | fig1, fig2 regenerated; **fig3_trust_map.jpg** and **fig4_pipeline.png** new |
| `ops/ROUND2_SCRIPT.md` | **New** - the full Round 2 presentation |

Not in git (gitignored, on this machine and in Drive): `SIH26166_deck.pptx`,
`SIH26166_deck.pdf`, `SIH26166_deck_UPLOAD.pdf`.
