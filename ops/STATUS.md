# STATUS — end of Day 5, second session (3 Sep 2026)

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewritten in full, not appended.** True as of 3 Sep 2026, ~16:45 IST.

---

## 🔴 Two decisions were made today. Both change what the next session does.

**1. Novelty is worth 25%. CONFIRMED by the user with the SPOC.** This was the last open question
in `CLAUDE.md` and it is now closed. It is the highest-weighted single criterion and the one we are
weakest on.

**2. Samartha is building alone for the next two days.** Deliberate, and a reversal of the
per-person plan in `ops/PLAN_TO_9_SEP.md` Part 6. The reasoning: the team has been slow to converge,
we do not have time to coordinate five people through a novelty decision, and the build is the
critical path. Teammates are **not** being given nightly specs for Day 6 and Day 7.

> ⚠️ **This puts Gate 5 at risk and that is understood, not overlooked.** Gate 5 (Day 10) requires
> all six to explain their own module cold. The mitigation is a **hard deliverable**: one written
> brief per teammate at the end of the sprint, covering what changed in their area and what they
> must be able to answer. **That brief is not optional and it is not a nice-to-have** — without it,
> five people cannot answer for code they did not write. It is written into the Day-6 prompt's
> definition of done.

**No `spec-writer` run this session.** Step 4 of `/wrap` was deliberately skipped — drafting five
nightly specs would contradict the decision above. This is the one wrap step not performed, and it
is recorded here rather than silently omitted.

---

## Position

```
Day 5 of 11  |  6 days to the event  |  Internal hackathon: 9 SEP 2026 (CONFIRMED)
Gate 1: PASSED and reproducible      Next: Gate 2 on Day 7 (5 Sep)
Novelty weight: 25% — CONFIRMED
```

Gate days are now in `docs/00_CANONICAL_FACTS.md` §11 with a Date column: **2 → Day 7 (5 Sep) ·
3 → Day 8 (6 Sep) · 4 → Day 9 (7 Sep) · 5 → Day 10 (8 Sep) · event Day 11 (9 Sep).**

**Smoke test — run this session, exit codes observed, not inferred:**

| Check | Exit | Result |
|---|---|---|
| `pytest evaluation/ -q` | **0** | 9 passed |
| `pytest -q` (full) | **0** | **179 passed** |
| `import core.pipeline` | **0** | ok |
| `python -m core.pipeline data/pairs/pair_01` | **0** | `residual_px 0.19452325191421008` — exact, unchanged |

⚠️ **The venv is at `C:\Users\samar\venvs\sih26166` and must be activated.** Unactivated, `python`
on this machine is a bare 3.12 with no numpy and no pytest, and every check above fails in a way
that reads as "a teammate broke the build." This cost real time this session. Now in `README.md`.

---

## 🔴 GATE 2 IS IN TWO DAYS AND ONE CRITERION HAS ZERO EVIDENCE

Checked against `results_log.csv` this session, criterion by criterion (§11):

| # | Criterion | Evidence | Verdict |
|---|---|---|---|
| 1 | `rmse_gt_px` < 0.5 at Δaz ≤ 15° | 0.32230 | ✅ |
| 2 | `inlier_ratio` > 0.60 | 0.9757 | ✅ |
| 3 | `grid_coverage_fraction` ≥ 0.80 | 1.0000 | ✅ |
| 4 | `distribution_cv` < 1.0 | 0.4145 | ✅ |
| 5 | **≥2× better than best of SIFT/ORB/AKAZE on the *same pair at the same scale*** | **NONE** | 🔴 |
| 6 | Matches on ≥1 Tier D pair, degradation in metres | literal pass, honestly rotten | ⚠️ |

**Criterion 5 has no evidence at all, and I verified that rather than assuming it.** Every classical
synthetic row is SIFT at `gsd_mpp=10.0` with an empty `config`; all 20 of ours are at `60.0`. There
are **zero** SIFT/ORB/AKAZE rows at 60.0 on synthetic. A comparison at two different scales is a
different experiment, and at 0° it reads as "SIFT is 34× better than us" — which is exactly the
number a judge would find.

**Nobody is currently assigned to fix this.** It was Samrudh's Days 7–8 task in
`ops/PLAN_TO_9_SEP.md` Part 6, and Samrudh is not being given specs under the build-alone decision.
It is a re-run of the existing classical baselines at `gsd_mpp=60.0` on the same synthetic pairs —
hours, not days — but **it has to be somebody's job on Day 6 or Gate 2 fails on the one criterion
that carries our whole "better than classical" claim.**

---

## What landed today (two commits, both pushed)

**`4b23ec2` — the schedule is in the repo.** The 9 Sep date existed only in STATUS.md and a plan
file on Samartha's laptop. `00_CANONICAL_FACTS.md` — the document everyone is told to read first,
which declares itself authoritative — did not contain the string "9 Sep" at all, and still scheduled
Gate 4 on the event day and Gate 5 the day after the round is judged. Fixed §10 (date + the SPOC's
format facts: **live demo NOT compulsory, no prior upload, we are pitch-primary**), §11 (gates
re-anchored, Date column added, old days kept beside them), §12 (11 days, not 12; deleted "if you
get extra days"). `TEAM_TASK_GUIDE.md` banner + killed its "Days 13–15 buffer". The approved plan
is now committed at **`ops/PLAN_TO_9_SEP.md`** — it was outside git, so the five people it assigns
work to could not read it.

**`7f625c7` — bet A, and two findings underneath it.** See below.

---

## 🔴 Bet A is CLOSED. It failed, and it was worth doing.

**The hypothesis:** Tier D scores 37.81 px because `core/scale.py:101` resamples to the coarser
grid, downsampling the 640×640 optical crop to 99×99 so LoFTR's coarse stage runs at an effective
500 m/px on 60 m/px data. Render the DEM into the sensor's grid instead.

**Built** (`ops/build_tier_d_native.py`): DEM sampled at the Kaguya crop's own pixel centres,
640×640 at 9.3698731836556 m/px, `to_common_gsd` an exact no-op.

**Result: the prediction was half right and it did not help.** 19 → **105** matches, exactly as
predicted. Every extra one is wrong. Residual 2268.8 m → 3995.6 m.

**It is not a threshold artifact, and checking that mattered.** Both RANSAC gates are in **pixels**
and default to 3.0 (`core/ransac.py:52`, `evaluation/metrics.py:5`), so the fine-grid arm was
silently judged at a 28 m ground tolerance against the coarse arm's 180 m — a 6.4× stricter bar.
`ops/bet_a_experiment.py` re-asks both arms the same question in metres; the fine grid is worse at
**every** tolerance. Genuine negative.

> The plan's own success criterion — "residual_px materially below 37.8" — was the same trap. On a
> 6.4× finer grid that is a 6.4× stricter bar than intended. **Compare metres, never `residual_px`
> across different grids.**

---

## 🔴 Finding 1 — the shaded relief has been lit from the wrong side all along

**Owner: Samrudh. `evaluation/shaded_relief.py:10-16`. NOT FIXED — deliberately left to him.**

```
as-recorded  az 284.901°   NCC vs the real Kaguya image of that ground   -0.5744
corrected    az 104.901°                                                 +0.5926
```

A negative correlation that size is the same terrain shaded backwards. Of eight gradient/sign
conventions tested at the recorded azimuth, only negating **both** gradients flips it — exactly
`aspect + 180`. So `render_shaded_relief(dem, az, ...)` lights terrain from `az + 180`.

**Contaminates every Tier D row in `results_log.csv`** — ours *and* Risheeth's SIFT 36.03 / ORB
26.76 / AKAZE 10.95, including the AKAZE number we call Q&A killer #2. **Does not** touch the
synthetic sun-azimuth sweep: that compares two renders, so a constant offset cancels. The 15° Gate 2
result stands.

Rendering at `az+180` through the existing function is arithmetically identical to a fixed one, so
the measurement was possible without editing his file. **Fixing it does not rescue Tier D.**

---

## 🔴 Finding 2 — we have never had a correct Tier D match. Not once.

Because the reference now shares the optical grid, the true alignment is a translation recoverable
without any feature matching. FFT cross-correlation over the full ±320 px range:

```
global peak (dx,dy) = (-9, +23) px = (-84, +216) m    NCC +0.7139
  top-left    (-9,+23) +0.5455      bottom-left  ( 0, +1) +0.7524
  top-right   (-8,+23) +0.6409      bottom-right (-9,+21) +0.5381
```

**Three of four quadrants agree within 2 px; the fourth does not** — so it is not a perfectly
uniform translation, and that is reported rather than smoothed away. It does not change the
conclusion: the candidates differ by ~24 px and the matcher is wrong by ~200 px against either.

| lighting | matches | RMSE vs truth | correct within 94 m |
|---|---|---|---|
| as-recorded | 107 | 2434 m | **0 / 107** |
| corrected | 94 | 2520 m | **0 / 94** |

**The 37.81 px we have been quoting was never a degraded registration. It is RANSAC fitting a
plausible homography to matches that are all wrong** — exactly what `core/pipeline.py:21-23` warns
about when it says `residual_px` and `rmse_gt_px` are not interchangeable.

**And a plain FFT cross-correlation registers the same pair to ~230 m, with no features and no
RANSAC.** Logged as `fft_phase_correlation` with **no `rmse_gt_px` on purpose** — it defines the
reference alignment, so scoring it against itself would be circular.

Full write-up with per-owner actions: **`ops/specs/TIER_D_FINDINGS_DAY5.md`**.

---

## 🔴 The Gate 2 decision this forces — due before Day 7

Gate 2 requires *"produces matches on ≥1 multi-modal (Tier D, optical↔elevation) pair with
degradation quantified in metres."*

**We pass that literally.** We produce 105 matches and can quantify degradation in metres better
than ever. **"Show me one of those multi-modal matches" ends the Q&A round.**

The honest version, and it is stronger than bet A would have been:

> We tested our matcher against optical↔elevation and it produced 105 correspondences, none
> correct. We know they are wrong because we built ground truth for that pair ourselves. Feature
> matching has no purchase on a hillshade — so for that case we register by global correlation
> instead, which lands it inside ~230 m. We report which method is used and why.

**This is a decision, not a task.** It is Samartha's to make in the next session.

---

## In flight — resume here

**Nothing is half-finished. The working tree is clean and both commits are pushed.**

**The next session is a NEW session, not a continuation.** Plan agreed with the user:

1. **Model: Claude Fable 5.1** (`claude-fable-5-1`) — 1M context, built for long-horizon agentic
   work. 2× Opus 5's price; worth it for a 2-day autonomous build.
2. **Effort: `xhigh`** for the build (Claude Code's default and the documented sweet spot for
   agentic coding). **`max` for the Phase 1 novelty decision only** — one reasoning-heavy call
   where correctness beats cost.
3. **Ultracode: ON for research and review. OFF for editing `core/`** — parallel agents mutating a
   repo with 179 tests and a pinned exact number is how Gate 1 breaks silently.
4. **The user has a prepared prompt** covering: Phase 0 web research on what wins and loses at SIH,
   Phase 1 a ranked-and-committed novelty decision, Phase 2 a 2-day build. Phase 1 was rewritten to
   be less prescriptive — Fable 5.1 degrades on over-prescriptive prompts.

**A research workflow was launched this session and deliberately stopped** before completion. It
produced **no output and nothing was written**. Phase 0 runs fresh in the new session. Do not go
looking for a research file; there isn't one.

**Bet B (`core/reliability.py`) is now the only live novelty bet** — per-cell verified / weak /
**no evidence**. Reuses `core/distribution.py`'s binning. Wire beside `_distribution()` at
`core/pipeline.py:184` as a new dict key. **Do not change `run_all()`'s signature** — it is pinned
by parameter-name list equality at `core/test_interfaces.py:59`.

---

## Known issues — do not re-report these

1. 🔴 **`evaluation/shaded_relief.py` lights terrain from `az+180`.** Samrudh's. Unfixed by design.
2. 🔴 **Every Tier D row is meaningless as an accuracy number** — ours and all three baselines. Do
   not quote 37.81 / 36.03 / 26.76 / 10.95 as registration accuracy anywhere.
3. 🔴 **Test contamination — ROOT CAUSE STILL LIVE.** `evaluation/test_metrics.py` calls
   `log_result` without redirecting `RESULTS_LOG`, so every `pytest` run appends a
   `test_pair_allowed / method=test` row. **Hit and reverted four separate times this session.**
   The fix is one `monkeypatch.setattr(logger, "RESULTS_LOG", tmp_path / "x.csv")`; it is Samrudh's
   file and every other test in the repo already redirects correctly.
   **Check `git diff evaluation/results_log.csv` before every commit until it is fixed.**
4. 🔴 **`presentation/` is still a 0-byte `.gitkeep` and Saniya has never committed** — verified
   again today, six days. But `docs/SANIYA_NARRATIVE_GUIDE.md` (25 KB) already holds ~70% of the
   deck as prose. The gap is transcription plus one diagram, not authorship.
5. **RANSAC thresholds are in PIXELS, not metres** (`core/ransac.py:52`,
   `evaluation/metrics.py:5`). Any comparison across two different pixel grids is invalid unless
   the tolerance is converted. This nearly produced a wrong conclusion today.
6. **AKAZE beats us on both real pairs** — 0.1215 vs 0.1945 on `pair_01`. Neither real pair has a
   sun difference, so they test the one thing we do not claim. Our claim needs the synthetic sweep.
   **Q&A killer #2, and the Tier D half of it is now void for everyone.**
7. **No illumination-OFF arm on the sun sweep.** Still the highest-value measurement unmade. Until
   it exists we cannot say "illumination normalisation improves our sun-angle accuracy by N."
8. **The illumination A/B is near-circular** — `core/bench_illumination.py:56-64` builds the hard
   case as contrast inversion and `gradient_orientation` is designed to be invariant to exactly
   that. Relabel "intensity inversion, **not** sun angle" everywhere.
9. **Synthetic ground truth has no moving shadows** — pure Lambertian, no occlusion term. Shading
   rotates, shadows do not. Disclose on the slide. Q&A killer #3.
10. **`redetect()` has zero callers** (`core/distribution.py:130`) — so that novelty bullet in
    `SANIYA_NARRATIVE_GUIDE.md:131-142` is false as written.
11. **No pyramid in `core/scale.py`.** The cross-scale novelty bullet is half-built. Soften the
    claim; wrong week to build it.
12. **The same Tier D pair is logged under two `pair_id`s** — `pair_03_tierD` vs `tier_d_01`. A
    third now exists: `pair_04_tierD_native` (legitimately a different pair — different grid).
13. **Two sets of `tier=synthetic` rows are not comparable** — Samrudh's SIFT rows are at
    `gsd_mpp=10.0` with an empty `config`; the 20 `ours_loftr` rows are at 60.0 with full config.
14. **Risheeth's understanding gap.** Code fine, but 4 of 5 `baselines/` blockers were fixed for
    him. Gate 5 risk, not a code risk.
15. **Risheeth has 3 stale remote branches** — `risheeth-baseline-pipeline`,
    `risheeth-invariant-pipeline`, `risheeth-baselines-clean`. Merged to `main`; delete them.

---

## Evidence file — `evaluation/results_log.csv`

**46 rows, 15 fields, `csv.DictReader`-clean.** 3 added today, no existing row edited or deleted.

| Rows | Tier | Method |
|---|---|---|
| 20 | synthetic | `ours_loftr` — the sun-azimuth sweep, 5 off-grid shifts × 4 angles |
| 14 | synthetic | SIFT (Samrudh) — see issue 13 |
| 4 | same-frame offset crop | `ours_loftr`, SIFT, ORB, AKAZE |
| 5 | D | `ours_loftr`, SIFT, ORB, AKAZE, `change_detection_absdiff` — **see issue 2** |
| 3 | D | **NEW:** `ours_loftr` ×2 (both lightings, with real `rmse_gt_px`) + `fft_phase_correlation` |

**The headline result — medians over 5 off-grid shifts. Unaffected by today's findings:**

| Δazimuth | `rmse_gt_px` | `inlier_ratio` | `grid_coverage` | Gate 2 C1 (<0.5) |
|---|---|---|---|---|
| 0° | 0.11992 | 1.0000 | 1.0000 | PASS |
| **15°** | **0.32230** | **0.9757** | **1.0000** | **PASS** |
| 30° | 0.93134 | 0.7404 | 0.8281 | FAIL |
| 45° | 2.58557 | 0.3484 | 0.4062 | FAIL |

Report the **median, never the minimum**.

---

## Open questions

1. **Reframe the multi-modal claim honestly, or drop it?** Due before Gate 2 on Day 7. See above.
2. **Saniya — engage or reassign?** The plan's contingency (no `.pptx` by end of Day 6 →
   `presentation/` moves to Samartha) is now entangled with the build-alone decision. Still
   undecided.
3. **Rohan — Tier A `cut` or `abandoned`?** Overdue since Day 6. Lower stakes now that Tier A is
   formally dropped, but an open question is not an answer.

*(Resolved today: the novelty weight — 25%, confirmed. The internal hackathon date — 9 Sep,
resolved this morning.)*

---

## Not doing — settled, do not re-litigate

- **Bet A.** Closed, measured, logged. Do not rebuild it.
- **No VM or cloud machine.** Breaks Gate 4, which needs the demo on this laptop with wifi off.
  LoFTR 640² in 5.50 s, 1.84 GB peak, `torch 2.13.0+cpu`.
- **No pyramid**, no cross-sensor chase (Tier A/B dropped in the Day-5 scope cut), no new matcher
  work. 179 tests green and Gate 1 exact — `core/` is done.
- **`core/scale.py` stays as it is.** Its "downsampling is the honest direction" reasoning survived
  bet A: upsampling did not invent useful detail, it invented *matchable-looking* detail, which is
  worse. The docstring was right.
