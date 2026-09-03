# SIH26166 — Plan to 9 September

> **Status: APPROVED. Written Day 5 (3 Sep 2026); this is what we are executing.**
>
> It lived on Samartha's laptop outside the repo for half a day, which meant the other five people
> could not read the plan they were being assigned work from. That is why it is here.
>
> **Part 6 is the part that concerns you** — it is the per-person assignment for Days 5–10, and it
> supersedes the Days 5–10 rows in `docs/TEAM_TASK_GUIDE.md`.
>
> Gate days and criteria are **not** set here — `docs/00_CANONICAL_FACTS.md` §11 is authoritative
> for those. If this file and Canonical Facts ever disagree, Canonical Facts wins.

## Context

The SPOC confirmed the internal hackathon is **9 Sep 2026** = **Day 11**. We have **7 days including
today (3 Sep)**. Judging weights novelty heavily; without enough points we do not qualify for the
next round.

**Two scheduling breaks, fixed in Part 7:** Gate 4 (demo runs 3× offline) sits on **Day 11, the event
day itself**, and Gate 5 (all six explain their module cold) sits on **Day 12, after the event**.

### What the research established

- **The slide template is the rubric.** Institutional internal-hackathon rubrics weight
  Innovation/Originality ~25%, **Relevance to the problem statement ~25%**, Feasibility ~20%, plus
  Impact, Technical Execution and Presentation. The official template's own bullet prompt reads
  *"Innovation and uniqueness of the solution"* — novelty is a required field, not just a criterion.
- **Our current novelty claims will not survive an expert.** Phase-congruency illumination-invariant
  lunar registration is established work (HOPC / HAPCG / HOWP / CFOG), and a 2025 paper already
  benchmarks **LoFTR on Chandrayaan-2 data**. LoFTR is off-the-shelf; we contributed nothing to it.
  *[Correction, 3 Sep evening: that paper (arXiv 2509.04775, Space Applications Centre) benchmarks
  SuperGlue, not LoFTR — LoFTR does not appear in it. The point stands: the matcher is not ours.
  See `ops/PHASE0_RESEARCH_DAY5.md` §5.1.]*
- **Two of our four written novelty bullets are false today**
  (`docs/SANIYA_NARRATIVE_GUIDE.md:131-142`): `redetect()` (`core/distribution.py:130`) has **zero
  callers** — we measure uniformity, we do not enforce it; and `core/scale.py` has **no pyramid**.
- **Our illumination A/B is near-circular** — `core/bench_illumination.py:56-64` builds the hard case
  as contrast inversion, and `gradient_orientation` is *designed* to be invariant to exactly that.

### The discovery that reshaped this plan

`data/pairs/pair_03_tierD/PROVENANCE.md` shows Tier D is **already** render-and-match: the LOLA DEM
rendered at the Kaguya image's own solar geometry (az 284.901°, el 16.98°). It scores 37.8 px
(~2268 m) and we have been calling that a multi-modal limitation.

**It is not. It is an information-starvation bug in our own pipeline, and both halves are confirmed
in our code:**

| | |
|---|---|
| Kaguya optical | 640 px × 9.37 m/px = 5997 m across |
| LOLA rendered | 101 px × 60.0 m/px = 6060 m across |
| Same ground, scale ratio | **6.4×** |

`core/scale.py:101` is `target = float(max(ga, gb))` — it resamples to the **coarser** grid, with a
comment at `:84` saying it "throws information away on purpose." So the 640 px optical image is
downsampled to **99 px** before matching. `core/matcher.py:68-71` confirms LoFTR's coarse stage runs
at **1/8** (`STRIDE = 8`).

**The consequence, and this is the whole insight:**

| Input size | Coarse grid | Effective resolution | vs. LOLA's real 60 m/px |
|---|---|---|---|
| 99 px (today) | 12×12 | **500 m/px** | 8× coarser than the data |
| 640 px (proposed) | 80×80 | **75 m/px** | **matches the data** |

We are matching at 500 m/px when our elevation data carries 60 m/px of information. We observed 19
matches, 10 inliers. **We threw away 97.6% of the optical pixels, then concluded multi-modal matching
is hard.**

---

## Strategy

One theme ties the deck, the demo and the novelty claim together:

> ### "A registration system that knows when it is wrong."

Every other team shows a number. We show *where* that number can be trusted, *at what sun angle* it
stops being true, and one feature we shipped **switched off** because we proved it was lying to us.

Novelty moves out of the matcher — where we have none — and into **the output layer and the honesty
layer**, both of which are genuinely ours.

⚠️ **Format constraint that shapes everything:** the SPOC says a live demo is **not compulsory** for
software projects, and there is **no prior upload** — we present on the day. So this is
**pitch-primary**. Capabilities must exist to the standard of *a measured result plus one figure on a
slide*, **not** a polished UI feature. We carry a demo because it differentiates, but the deck must
score on its own.

---

## Part 1 — Novelty bet A: match at the resolution the data actually carries 🔴 *primary*

**The claim:** *"When registering optical imagery against an elevation model, don't degrade the
sensor to the model's grid. Render the model into the sensor's grid — and match at the resolution
the elevation data actually carries."*

**Why this is the right bet:** it scores **Relevance (~25%) and Novelty simultaneously**, because
multi-modal registration is the problem statement's central demand *and* our weakest result. Nothing
else on the table does both.

**The work:** re-render the LOLA DEM at 9.37 m/px (Kaguya's scale) instead of its native 60 m/px,
giving a 640×640 rendered relief image, and match against the 640×640 optical image with no
downsampling.

Upsampling adds no real terrain detail — but it does not need to. It puts LoFTR's **coarse stage at
75 m/px, matched to the DEM's true information content**, while the fine stage refines against the
optical image's real texture. `gradient_orientation` matches on structure, not brightness, and
structure survives upsampling.

- Reuses `evaluation/shaded_relief.py` and `ops/build_tier_d_pair.py`. **No new algorithm.**
- `PROVENANCE.md` records exact crop lines, so it is fully reproducible.
- **Timebox: end of Day 6.** Success = Tier D `residual_px` materially below 37.8.
- **Failure is still a win.** We will have *measured* the resolution limit of optical↔elevation
  matching — converting our worst result into a quantified finding and a strong Q&A answer where we
  currently have silence: *"multi-modal registration here is bounded by the elevation data's
  resolution, not by our matcher. Here is the curve."*

---

## Part 2 — Novelty bet B: the spatial reliability map *(fallback + the demo's second visual)*

**The claim:** *"We don't report one accuracy number for a whole image. We report where the alignment
is verified, where it is weak, and where we have no evidence at all."*

Published work reports a single scalar per pair. An operational analyst needs to know **which part of
the frame** to trust.

- New `core/reliability.py`: per 8×8 cell, combine inlier count and median reprojection residual into
  `verified` / `weak` / `no evidence`.
- **`no evidence` must be a distinct state, not a low score.** A cell with no matches is *unmeasured*,
  not badly aligned. Conflating them is the overclaim this project exists to avoid.
- **Reuses `core/distribution.py`**, which already bins (`cell_index`, `counts`, `weak_cells`, 16
  passing tests). Wire beside `_distribution()` at `core/pipeline.py:184` as a new dict key — **do not
  change `run_all()`'s signature**, it is pinned by list equality at `core/test_interfaces.py:59`.
- **It fixes our worst demo moment.** `app/notes_day6_tierd.md` records **35 change candidates, 0 real,
  31 shadow, 4 registration artifacts** — a 100% false-positive rate we currently demo live. Gating
  detections to `verified` cells turns that into *"our own reliability map rejected the regions that
  produced them."*

Lower risk than bet A. **Both ship if time allows; bet B alone is sufficient if bet A fails.**

---

## Part 3 — Make the claims true before making them louder

Non-negotiable before anything reaches a slide. A false novelty claim is worse than a modest true one.

| # | Issue | Where | Action |
|---|---|---|---|
| 1 | 🔴 **The missing experiment** — no illumination-OFF arm on the sun sweep | `evaluation/results_log.csv` | **Highest-value measurement available.** Re-run `--synthetic --sweep 0,15,30,45 --repeats 5` with normalisation disabled. Converts our central claim from *asserted* to *measured*. It is a flag and a re-run. |
| 2 | `redetect()` has zero callers — "we enforce uniformity" is false | `core/distribution.py:130` | Wire it, or delete the claim. Wiring **trades accuracy for coverage** (measured: coverage 0.797→0.891 while `rmse_gt_px` 0.41→0.72). Log both arms as separate rows. |
| 3 | No pyramid — cross-scale claim half-built | `core/scale.py` | **Soften the claim.** Wrong week to build it. |
| 4 | Illumination A/B is near-circular | `core/bench_illumination.py:56-64` | Relabel "intensity inversion, **not** sun angle" everywhere it appears. |
| 5 | Synthetic ground truth has **no moving shadows** | `evaluation/shaded_relief.py` | Pure Lambertian, no occlusion term — shading rotates, shadows do not move. Its docstring overclaims. Disclose on the slide; being caught is worse. |
| 6 | 8 junk `method=test` rows in the evidence file | `evaluation/results_log.csv` | Samrudh's tests write to the real file. Redirect to temp, delete the rows. |
| 7 | Same Tier D pair under two `pair_id`s | `pair_03_tierD` vs `tier_d_01` | Normalise — a judge grepping the CSV cannot tell they are the same pair. |

---

## Part 4 — The three questions that end a Q&A round

1. **"Show me a cross-sensor result."** We have none, ever. All catalogue rows are
   `status=identified`. **Answer:** name it as scoped-out with the reason, pivot to the synthetic
   sweep where we control ground truth. Do not bluff.
2. **"Your CSV says AKAZE gets 0.12 px and you get 0.19 px on the same pair."** True — and AKAZE
   beats us 3.5× on Tier D. **Answer:** `pair_01` is a same-frame crop with *zero* sun difference —
   the one case where classical is strongest and our illumination handling buys nothing. Our
   advantage appears with a sun difference. **This answer only works if Part 3 item 1 is done.**
3. **"Do your synthetic shadows actually move?"** No — see Part 3 item 5.

---

## Part 5 — The 20-second moment that wins novelty marks

Currently buried in a docstring at `core/subpixel.py:87-103` and in **no** pitch material:

> "We built a sub-pixel refiner. It made our headline number 5× better — 0.195 px down to 0.038 px.
> Then we measured it against known ground truth and found it was making us **less** accurate:
> 0.336 px to 0.431 px. So we shipped it switched **off**. Here are both numbers."

Reproducible from `core/bench_subpixel_results.csv`. Pair it with publishing the **failure half** of
the sun-angle curve (30° and 45°, where we fail our own threshold). Rigour as a bullet scores nothing;
one concrete instance where the rigour caught us lying to ourselves scores in the novelty column.

---

## Part 6 — Per-person assignment 🔴 *the plan is only as good as who executes it*

| Person | Days 5–6 | Days 7–8 | Days 9–10 |
|---|---|---|---|
| **Samartha** | Bet A attempt + decision. Reliability map core. | Reliability map → UI. Gate 2. | Freeze. Gate 4 driver. Rehearsal. |
| **Samrudh** | 🔴 Illumination-OFF sweep (Part 3 #1). Fix test contamination (#6). | Same-scale ours-vs-classical comparison. | Verify every slide number against `results_log.csv`. |
| **Rishabh** | Change-detection gating hooks. | Reliability-gated detection results. | Rehearse his 60-sec segment. |
| **Rohan** | 🔴 Tier A decision — `cut` or `abandoned`, **end of Day 6**. Re-render DEM for bet A. | Verify `demo_cache/` opens offline. Recruit the Gate 3 stranger. | Provenance answer. Rehearsal. |
| **Risheeth** | Baseline numbers into the comparison table. | Failure gallery → one slide figure. | Rehearse his segment. |
| **Saniya** | 🔴 Slides 3, 5, 6 (need **no** final numbers). | Slides 2, 4. Full deck draft. | Deck final. Lead rehearsals. |

**Deck contingency — 🔴 THE TRIGGER WAS BROKEN AND WAS REWRITTEN ON DAY 6 (4 Sep). Read why.**

It used to read: *"If there is no committed `.pptx` by end of Day 6 (4 Sep), `presentation/` is
reassigned to Samartha."* **That criterion could never be satisfied.** `.gitignore` line 31 blocks
`*.pptx`, and `docs/SANIYA_NARRATIVE_GUIDE.md` explicitly instructs Saniya to keep `deck.pptx` **in
Drive, not git**, and *"do not reach for `git add -f`."* The contingency therefore measured a thing
the project forbids her from doing: it would have read **failed** whether she had built five slides
or none. Acting on it would have taken a teammate's Gate 5 module away on the basis of an
instrument that reads zero by construction — and "her zero commits in six days" is **not** evidence
of no work, it is evidence that her only deliverable format is excluded from the repo.

**The corrected trigger — an observable she is actually permitted to produce:**

> **By 20:00 on Day 6 (4 Sep), `presentation/DECK_STATUS.md` must exist in git** — a text file
> (which `presentation/` accepts) carrying the **Drive link** to `deck.pptx`, whether the official
> template has been downloaded, and a **per-slide state** for all six slides. The format is given
> verbatim in `docs/SANIYA_NARRATIVE_GUIDE.md` under 📁 YOUR FILES.
>
> - **File exists and shows ≥3 slides drafted** → Saniya keeps `presentation/`. No change.
> - **File exists and shows she is blocked** → the blocker is Samartha's to clear *that same day*.
>   She keeps `presentation/`. A blocked teammate is a bad spec, not a failing teammate.
> - **File does not exist and she has not replied by 20:00** → Samartha writes the slide *content*
>   into `ops/DECK_CONTENT.md` (a folder he owns) and Saniya transcribes it into the template.
>   `presentation/` is reassigned **only** if there is still no reply by end of Day 7.

**Why the softer ladder is also the safer one:** the deck's real risk is *content*, not
*transcription*. `docs/SANIYA_NARRATIVE_GUIDE.md` is 29 KB and already carries all five content
slides, corrected on Day 5. Writing that content down is a few hours and can be done by Samartha
without touching `presentation/`; transcribing finished content into the template is ~90 minutes by
anyone. So the content risk gets closed on Day 6 **regardless of what Saniya answers**, and the
reassignment decision stops being all-or-nothing. Decide it on an observable, not on a feeling —
and make sure the observable is one the rules permit.

---

## Part 7 — Revised gate schedule

| Day | Date | What | Gate |
|---|---|---|---|
| 5 | **3 Sep** (today) | Bet A attempt. Illumination-OFF sweep. Deck skeleton committed. **Ask SPOC for the actual rubric.** | |
| 6 | 4 Sep | **Bet A decision point.** Reliability map core. Part 3 fixes. **Deck contingency call.** | |
| 7 | 5 Sep | **Gate 2** (from Day 8). Reliability map in UI + detection gating. Slides 2 + 5. | 🚪 2 |
| 8 | 6 Sep | **Gate 3** — stranger operates the UI unaided. Slide 6. Q&A bank finished. | 🚪 3 |
| 9 | 7 Sep | 🔒 **CODE FREEZE.** **Gate 4** — 3 consecutive runs, wifi off. Deck final. | 🚪 4 |
| 10 | 8 Sep | **Gate 5** — all six explain cold. Two full dress rehearsals. | 🚪 5 |
| 11 | **9 Sep** | **INTERNAL HACKATHON** | 🎯 |

Gate 4 moves Day 11 → Day 9; Gate 5 moves Day 12 → Day 10. Day 10 is pure rehearsal.

**We already banked the time:** `app/streamlit_app.py` was scheduled for Day 9 and shipped on Day 5.
That four-day surplus is what pays for the novelty work.

### Two cheap, high-leverage actions on Day 5

1. **Ask the SPOC for the actual evaluation rubric and its weights.** We are optimising against
   *inferred* weights from other colleges. If their rubric weights Impact or Presentation more
   heavily than Novelty, the allocation below should shift. **This is one message and it de-risks the
   entire plan.**
2. **Precompute the demo results and cache them.** A live 15-second align inside a 3-minute pitch is
   a risk with no upside. Show cached results instantly; keep the live run available *if a judge asks*.

---

## Part 8 — The deck: 0% built, ~70% already written

`presentation/` contains one 0-byte `.gitkeep`. No `.pptx` or `.pdf` exists anywhere in the repo.
**But `docs/SANIYA_NARRATIVE_GUIDE.md` (25 KB) already contains** the verified 6-slide structure, the
technical-approach diagram as text, the feasibility and licensing argument (Apache-2.0 vs SuperPoint
non-commercial), the impact bullets (LUPEX, DFSAR/Vikram, 200+ OHRC scenes), and a timed 3-minute
demo script for all six speakers.

**The gap is transcription plus one diagram, not authorship.** One person, one day.

| Slide | Rubric dimension | State |
|---|---|---|
| 2 · IDEA / Proposed Solution | **Innovation & uniqueness (~25%)** | Rewrite around bet A/B + the shipped-it-off story |
| 3 · TECHNICAL APPROACH | Technical execution | Diagram written, needs drawing |
| 4 · FEASIBILITY AND VIABILITY | **Feasibility (~20%)** | Strong — CPU-only, offline, permissive licensing |
| 5 · IMPACT AND BENEFITS | Impact | Good bullets exist |
| 6 · RESEARCH AND REFERENCES | Credibility | Cite the literature we found, honestly |

⚠️ **Six slides including the title page — five content slides.** No "Problem Statement" slide and no
"Proposed Solution" slide; "Proposed Solution" is a bullet prompt *inside* slide 2.

---

## Part 9 — Risk management: the qualification floor

The plan is deliberately larger than the minimum. **Protect this floor first and sacrifice everything
else in this order.**

**Must have, in priority order:**
1. A complete 6-slide deck, every number traceable to `results_log.csv`
2. Written, rehearsed answers to the three Q&A killers (Part 4)
3. Gate 5 — all six explain their own module cold
4. **One** true, distinctive novelty claim — bet A *or* bet B, not both

**Cut in this order if behind:** change-detection gating → reliability heatmap polish → `redetect()`
wiring → bet A's UI integration (keep the *measurement*) → the live demo itself.

**Never cut:** the deck, the Q&A answers, the rehearsals. A brilliant capability nobody can explain in
three minutes scores zero.

---

## Verification

1. **Regression floor** — `python -m pytest -q` stays green (currently **179 passed**) and
   `python -m core.pipeline data/pairs/pair_01` still prints `residual_px 0.19452325191421008`
   *[3 Sep evening: sub-pixel refinement became the default on measured evidence, so the command
   now prints `0.03761504064805703`; `--no-subpixel` reproduces the old figure exactly.]*
   exactly. That figure is quoted in our documents; if it moves, something upstream changed.
2. **Bet A** — new Tier D rows in `results_log.csv` with the render resolution in `config`. Success =
   `residual_px` materially below 37.8. **Log either outcome.**
3. **Illumination ablation** — new rows with normalisation off, `config` populated, readable by
   `csv.DictReader`. State the 15° delta in one sentence.
4. **UI** — `streamlit.testing.v1.AppTest` gives **0 exceptions** on first render and through a full
   select-pair → Align → render cycle. Harness exists at `app/test_streamlit_app.py`.
5. **Gate 3** — someone who has never seen the project operates the UI and explains the output with
   nobody speaking. Recruit by Day 7.
6. **Gate 4** — three consecutive clean runs, wifi physically off, lid closed between runs. Procedure
   in `.claude/agents/demo-medic.md`. **No automation substitutes for this.**
7. **Final number pass, Day 9** — grep every figure on every slide against `results_log.csv`.

---

## What this plan deliberately does NOT do

- **No pyramid in `core/scale.py`.** Real gap, wrong week. Soften the claim instead.
- **No chase for a cross-sensor pair.** Tier A `status=identified` for five days; Tier B has no
  catalogue row. Both formally dropped in the Day-5 scope cut. Do not reopen.
- **No new matcher or detector work.** The matcher is off-the-shelf and that is fine.
- **No further polishing of `core/`.** 179 tests green, Gate 1 exact. It is done. Every remaining hour
  goes to novelty, the deck, and rehearsal.
