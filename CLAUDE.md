# SIH26166 — Lunar Image Registration

Smart India Hackathon 2026, ISRO problem statement SIH26166. Six-person team. **The college
internal round is 9 September 2026 = Day 11** (Day 1 was 30 Aug); confirmed by the SPOC on Day 5.
Full context is in `docs/00_CANONICAL_FACTS.md` — **read it before answering anything
substantive.** The approved plan for Days 5–10 is `ops/PLAN_TO_9_SEP.md`.

---

## Session commands

| Command | When |
|---|---|
| `/next` | Start of every session — pulls, rebuilds context, proposes a plan |
| `/wrap` | End of every session — smoke test, STATUS.md, specs, commit, team message |
| `/review` | After teammates push — findings for owners, never silent fixes |

`ops/STATUS.md` is the handoff between sessions. `/wrap` rewrites it; `/next` reads it.

---

## Agent routing

| Trigger | Agent | Writes files? |
|---|---|---|
| Teammates pushed; time for the daily review | `daily-reviewer` | **No** — findings only |
| End of session; tomorrow's five tasks need defining | `spec-writer` | **No** |
| Day ≥ 9, or before Gate 3 / Gate 4 | `demo-medic` | **No** |
| Day ≥ 8, or `presentation/` changed | `claim-checker` | **No** |

**No agent in this project may write or edit files.** That is deliberate. Gate 5 requires all six
team members to explain their own module cold; an agent that silently repairs a teammate's code
takes that away from them, and "the AI wrote it" does not survive an SIH Q&A round.

Do **not** rebuild `/code-review`, `/security-review`, `/simplify`, or the built-in `Explore`
subagent as project agents — use them directly.

---

## Invariants — these override convenience

**1. Numbers.** No figure enters a slide, demo script, Q&A answer or README until it exists in
`evaluation/results_log.csv`. Until then write `[TBD — results_log.csv]`. An earlier draft of this
project carried the invented figure "0.7 px" through four documents as though measured.

**2. Terminology.** `docs/00_CANONICAL_FACTS.md` §2 defines a five-tier validation ladder.
- **cross-sensor** — different instruments only. LROC NAC ↔ LROC NAC is the *same sensor* (Tier A,
  a sun-angle test). Calling it cross-sensor is false and is the likeliest ISRO judge question.
- **multi-modal** — visible↔infrared / radar / elevation only. Two panchromatic cameras are not.
- **sub-pixel** — always name the pixel grid (the reference image) and give the metres equivalent.

**3. No GPU.** The demo machine is an Intel Arc iGPU with 0 MB dedicated VRAM. All demo-path code
runs on CPU. Rohan's AMD card is 30 km away and can never be on the demo path. Install torch from
the CPU index. `pip install magsac` does not exist — use `cv2.USAC_MAGSAC`.

**4. Ownership.** One folder per person: `core/` + `app/streamlit_app.py` = Samartha ·
`evaluation/` = Samrudh · `baselines/` = Risheeth · `app/change_detection.py` = Rishabh ·
`presentation/` = Saniya · `data/*.csv|*.md` = Rohan. Never edit someone else's folder — that is
how six people avoid merge conflicts and keep Gate 5 answerable.

**5. Data lives in Google Drive, code in git.** Nothing over ~5 MB or binary goes in the repo.

**6. Gates cut scope, never extend time.** Gates at Days 5, 8, 10, 11, 12 — criteria in
`00_CANONICAL_FACTS.md` §11. A failed gate means dropping features, not adding days.

**7. Slide format.** The SIH 2026 template is TITLE PAGE · IDEA TITLE · TECHNICAL APPROACH ·
FEASIBILITY AND VIABILITY · IMPACT AND BENEFITS · RESEARCH AND REFERENCES. **There is no "Problem
Statement" slide and no "Proposed Solution" slide** — "Proposed Solution" is the first bullet
*prompt* inside IDEA TITLE, not a heading. The six-slide cap **includes** the title page, so we have
**five content slides**. Confirmed against the real file (924,505 bytes, sha256 `ce3e5dee…`).
Slides 3–6 keep the numbers our docs already used — a blind "shift everything by one" breaks four
correct things.

---

## Layout

```
docs/         00_CANONICAL_FACTS · 01_HOW_WE_WORK_TOGETHER · 02_DAILY_REVIEW_PROTOCOL
              TEAM_TASK_GUIDE + one guide per person
ops/          STATUS.md (session handoff) · specs/ (nightly task specs)
core/         Samartha — io_loader, scale, illumination, matcher, ransac, subpixel,
              distribution, pipeline
evaluation/   Samrudh — synthetic_data, shaded_relief, metrics, results_log.csv
baselines/    Risheeth — sift/orb/akaze, failure_gallery
app/          change_detection.py (Rishabh) · streamlit_app.py (Samartha)
presentation/ Saniya
weights/      cached model weights — gitignored, required offline for Gate 4
demo_cache/   demo inputs — gitignored
```

---

## Open, every session until resolved

- **The rest of the grading rubric.** **Novelty is 25% — CONFIRMED Day 5.** The remaining 75% is
  still inferred from other institutions (Relevance ~25%, Feasibility ~20%, plus Impact, Technical
  Execution, Presentation). Novelty being confirmed is the load-bearing part; the rest only changes
  the margin.

*(Resolved Day 5: the internal hackathon date — 9 Sep 2026 = Day 11. And the novelty weight — 25%.)*
