# Phase 1 — the novelty bet. Decided.

**Day 5, 3 Sep 2026, night. Samartha.** Evidence base: `ops/PHASE0_RESEARCH_DAY5.md`.
Status: **COMMITTED.** Phase 2 builds this and nothing else.

---

## The decision in one line

> **We claim the trust layer, not the matcher: "a registration system that knows when it is
> wrong."** Rigour (the ground-truth sun sweep) is the evidence under it; CPU-only/offline/Apache
> is the feasibility slide. Neither of those is claimed as novelty.

---

## The three angles, ranked

### 1 — The trust layer  ✅ COMMITTED

**The sentence a judge hears:**
> "Every registration tool gives you one accuracy number for the whole image. Ours tells you,
> cell by cell, where the alignment is *verified*, where it is *weak*, and where it has *no
> evidence at all* — and when its own matcher is confidently wrong, it says so and switches
> method."

**Defensible today?** Half of it.
- Measured and logged today: on the real optical↔elevation pair our matcher produced 105
  correspondences, RANSAC reached consensus, and **0 of 105** were correct within 94 m
  (`results_log.csv`, `pair_04_tierD_native`). A plain FFT correlation registers the same pair
  to ~230 m. And a sub-pixel refiner that improved `residual_px` 5× while making ground-truth
  error worse (0.336 → 0.431 px) was shipped switched off (`core/bench_subpixel_results.csv`).
- Exists in code: 8×8 binning (`core/distribution.py`), per-match LoFTR confidences
  (`core/matcher.py` returns `scores`), exact-ground-truth evaluation (`evaluation/metrics.py`
  with `H_true`), the FFT peak and quadrant-agreement check (`ops/tier_d_investigation.py`).
- Not built: the three-state map itself, the in-pipeline wrongness check, the fallback path,
  the calibration measurement, the change-detection gate. All are days-not-weeks.

**What is already published (unsparing):**
- Uss, Vozel, Lukin, Chehdi 2016 (IEEE TGRS) — RAE: per-fragment registration accuracy
  *without ground truth*, including optical↔DEM; "can identify image areas for which a
  predefined registration accuracy is guaranteed". The closest prior art. Continuous bound,
  area-based method, no "unmeasured" state.
- Truong et al. 2021 (CVPR) PDC-Net — per-pixel confidence for dense correspondences.
- Brown & Lowe 2007 — probabilistic accept/reject of an image match from inlier counts. **Our
  Tier D case is the one where this test passes and the match is wrong.**
- Feng, Du, Li 2019 (ISPRS) — hybrid feature/area registration with residual analysis.
- Wan, Shao, Li 2021; NASA ASP `image_align` docs — feature matching fails on optical↔DEM
  shading, dense correlation is the recommended fallback.
- Kybic 2009; Bierbrier et al. 2022 (165-work review) — registration error estimation without
  ground truth is a mature field in medical imaging.

**The narrow claim that survives all of that** (this exact wording goes on slide 2):
> A three-state per-region reliability map — verified / weak / **no evidence** — for a learned
> matcher's output, where "no evidence" is a distinct state and not a low score; an independent
> agreement check that catches a consensus homography fitted to wrong matches; automatic
> fallback to global correlation with the method declared; validated cell-by-cell against exact
> ground truth on lunar data; on a CPU. Cite Uss 2016 and Brown & Lowe 2007 on the same slide.

**Why this and not a convenience pick:** it is the only angle that (a) has measured evidence
today, (b) leaves an honest gap in the literature, (c) answers the PS-setters' own benchmark —
arXiv 2509.04775 (SAC) reports an RMSE that is a fit residual with no ground truth, which is
exactly the failure our Tier D case exposes, (d) is legible to a faculty judge in one picture,
and (e) is *bounded* novelty, which is what non-expert evaluators reward (Boudreau et al. 2016:
the "right tail" of novelty scores lower).

**The measurements that prove it, in order, with what each one can kill:**

| # | Measurement | Proves | Time | If it fails |
|---|---|---|---|---|
| M1 | Per-cell calibration on the 20 synthetic pairs (0/15/30/45°, exact `H_true`): true error per cell vs state | "verified" cells really are better than "weak" cells; "no evidence" cells are excluded, not guessed | ~4 h | **The claim dies.** Log it and fall back to angle 2. That is why M1 is first. |
| M2 | Wrongness check + fallback inside the pipeline, run on Tier D, logged with metres | consensus-on-noise is caught by an independent test; declared method; ~230 m by correlation | ~5 h (includes fixing the `az+180` hillshade sign, which the fallback needs) | Detector too weak → report the residual-vs-truth gap alone (already measured) |
| M3 | Gate change detection to verified cells on Tier D (35 candidates, 0 real) | the layer has a consumer; false positives drop | ~3 h | Keep ungated numbers; state it |
| M4 | Reproduce the sub-pixel on/off pair into `results_log.csv` | the 20-second story is quotable under Invariant 1 | ~1 h | — |
| M5 (optional) | Real multi-illumination LROC NAC pairs from MiLOI (Xie et al. 2025, github.com/Bin501/CNSFM): calibrate the map on real data | "knows when it is wrong" on real sun differences, not renders | timebox 2 h to check that ground truth is in the repo; ~4 h more if yes | Drop silently; synthetic calibration stands |

Core M1–M4 ≈ 13 hours, which fits Days 6–7 with half a day for the deck contingency.

**How it fails under a hostile third question, and the answers we will have written:**
1. *"Isn't this just the RANSAC inlier ratio with a colour map?"* — No. On Tier D the inlier
   ratio was 0.53 and the homography reached consensus; 0 of 105 matches were correct. "Verified"
   requires an independent agreement test (held-out residual in metres plus global-correlation
   agreement), and "no evidence" is a separate state. M1 shows the states are calibrated.
2. *"Uss et al. did per-region accuracy without ground truth in 2016, including optical–DEM."*
   — Yes, and we cite them. Theirs is a continuous bound for an area-based method; ours is a
   three-state map for a learned matcher's output with an explicit unmeasured state, validated
   against exact ground truth, and it drives a consumer. It is a system contribution, not a new
   estimator. (If the judge is from SAC, this is the push. The answer is short and true.)
3. *"The PS asks for multi-modal OHRC/TMC/IIRS; you show optical versus elevation and your
   matcher failed."* — Correct. The system detected the failure and registered by correlation to
   ~230 m, bounded by the 60 m/px DEM. We have no IIRS pair and we say so. **This flank stays
   weak under every angle; no two-day bet fixes it.**

### 2 — Ground-truth rigour: "we publish where it stops working"  ⤵ evidence layer, not the headline

**Sentence:** "We measure exactly where our sun-angle invariance stops working, against exact
ground truth, and we publish the angle at which it fails."
**Defensible today:** synthetic yes (0.32 px at 15°, fails at 30°); real no — no real pair with
a sun difference exists in our data.
**Prior art:** rendered sun sweeps are standard (Geo-LoFTR 2025; Singla, Patel, Dube 2026 at
SAC; LunarStereo 2025), and a real multi-illumination benchmark already exists (MiLOI, 2025).
**Verdict:** methodology, not novelty. A SAC judge would say "we do this". It scores Technical
Execution and Relevance and it is the evidence under angle 1 (M1 runs on this sweep). Keep it,
cite it, disclose the Lambertian-no-cast-shadow limit before being asked.

### 3 — Deployability: CPU-only, offline, Apache-2.0, sensor-agnostic  ⤵ feasibility slide

**Sentence:** "The whole pipeline runs on a laptop with no GPU, offline, on permissively licensed
components — the published SAC benchmark's best method (SuperGlue) cannot say that."
**Defensible today:** fully (torch CPU, 5.5 s per 640² tile, weights cached, LoFTR Apache-2.0).
**Prior art:** not a novelty claim at all; LoFTR is off-the-shelf.
**Verdict:** this is the Feasibility line (20–25% in every weighted rubric found). Say it there,
deliberately, and never on the innovation bullet.

### Not chosen, and what would have to change

- **Matcher-level novelty.** None exists and none is buildable in two days. Illumination
  normalisation and common-GSD resampling are the SAC paper's own preprocessing (their §4.1.2).
  They stay in the pipeline as engineering, with the citation, and come off slide 2.
- **A real multi-modal (IIRS) pair.** It would make the PS's central demand real. Tier C was
  never cut, no owner, no route; it is not reopened.
- **Bet A** (match at native resolution). Closed on Day 5 with a measured negative.

### No question for Samartha

No two angles came out equivalent. Angle 1 is the only one with evidence, a gap, and a
judge-legible sentence. Angles 2 and 3 are its supporting slides.

---

## What Phase 2 builds (order is the order of what can kill the claim)

**Day 6 (4 Sep)** — M1 `core/reliability.py` + per-cell ground-truth calibration on the sweep,
rows logged → M2 wrongness check, fallback path, declared method, Tier D rows logged (fix the
hillshade sign first; the fix is Samrudh's file — done under the build-alone decision and written
into his brief).
**Day 7 (5 Sep)** — M3 gated change detection → M4 sub-pixel rows → sweep the repo for claims
that are no longer true (redetect, pyramid, cross-sensor, "LoFTR benchmarked on CH-2") →
cached demo → written answers to the three questions → one-page brief per teammate → M5 if
time remains. Gate 2 re-read against `results_log.csv` at the end of Day 7.

**Every number above that will reach a slide is `[TBD — results_log.csv]` until it is logged.**

---

## Postscript — what happened when it was built (3 Sep, 20:00–21:10)

- **M1 ran first and the claim survived**, after one redesign. The first verdict rule (one
  whole-frame correlation) wrongly contradicted every 30° and 45° pair and triggered a fallback
  10–40× worse than the homography it replaced; the rule became a vote of cells and the rows from
  the bad rule were discarded before logging. Final (refinement ON), inside the claimed envelope
  of sun azimuth difference ≤ 30°: verified cells median true error 0.123 px, 99.0% under 0.5 px,
  100% under 1 px, n=817; weak 0.229 px; no evidence 0.390 px. Row
  `reliability_calibration_envelope`. (The Day-5 figure quoted here until 5 Sep — 0.162 px,
  92%/98% — was the pooled population, which averages in deltas outside the envelope.)
- **M2 works on real data.** Tier D native: 0 of 35 measurable cells agree → contradicted →
  fallback (+9, −23) px = 231 m, quadrant disagreement 216 m. LoFTR vs ground truth: 0 of 87
  correct within 10 px. Two lighting errors in the reference were found and derived on the way
  (`evaluation/shaded_relief.py`, `ops/solar_geometry.py`).
- **M3**: on the corrected pair the detector finds 1 candidate; the gate marks it unassessable /
  rejected. The Day-6 "35 candidates" was measured on the reflected render.
- **M4 reversed itself.** Refinement helps the transform-level true error at every sun angle
  (30° moves from FAIL to PASS on Gate 2 C1) while worsening the held-out residual on real
  texture. Default switched to ON; Gate 1 now prints 0.03761504064805703, `--no-subpixel`
  reproduces 0.19452325191421008.
- M5 (MiLOI) not attempted; the dataset's ground-truth format is unverified.

---

## Amendment — Day 5, late night. The framing was under-sold; the bet is unchanged.

**Raised by Samartha after the wrap:** *"why are we playing safe? why is the novelty partly? we
need full marks for novelty."* The challenge was correct and the answer is recorded here so the
next session starts from it rather than re-deriving it.

### What was wrong, and what was not

The **bet is not changed.** The trust layer stays the claim, the prior art stays cited, and we
still do not claim to have invented per-region registration confidence — Uss et al. 2016 published
that, it is on the references slide, and a judge who knows it and hears us claim it stops believing
the rest.

What was wrong was the **pitch language**, in one word. "Partly novel" is correct internal
reasoning and a bad sentence to say out loud: hedging reads as weakness. Confident citation reads
as scholarship — *"this builds on Uss 2016; what is ours is X; here is the measurement."* Same
truth, different register. Note also (PHASE0 §, Boudreau et al. 2016, 2,130 evaluator-proposal
pairs) that **maximum novelty is not maximum score** — non-expert evaluators mark down what they
cannot place. Full marks come from a claim a faculty judge can hold in their head, cannot poke a
hole in, and can see evidence for.

### Move 1 — the reframe. Costs nothing. Do it in the deck language.

The PS's own Expected Outcome names three deliverable metrics: **RMSE, inlier counts, inlier
ratios** (§1 of `00_CANONICAL_FACTS.md`). We implemented all three. Then, on real lunar data, we
found a case where all three are satisfied or explicable and the registration is 100% wrong
(`pair_04_tierD_native`: 88 correspondences, RANSAC consensus, median inlier residual **0.00 px**,
**0 of 87** correct within 10 px = 94 m).

> **The sentence for slide 2:** "The problem statement asks for RMSE, inlier count and inlier
> ratio. We implemented all three, then found a reproducible case on real lunar data where all
> three look acceptable and the registration is 100% wrong. Self-consistency cannot detect its own
> failure. So we built the independent check that can — and measured it."

This is a **finding**, not a feature. It scores Novelty and Relevance together because it is aimed
at the PS's own deliverable list. It does **not** attack the SAC authors — who very likely wrote
this PS — and it must never be phrased as though it does. We do not know their control-point
procedure and we do not claim their paper is wrong.

### Move 2 — the paid upgrade. ~Half a day. Turns one anecdote into a measured capability.

Today the failure detection rests on one dramatic case. The hostile third question is *"did it work
once, or does it always work?"* — and we cannot answer it yet.

**Already measured, verified from `core/reliability_calibration.csv` on Day 5:**
- **0 false alarms on 20 known-good pairs.** `global_contradicted` is `False` in every one of the
  1,280 rows, and `method_used` is `loftr+magsac++` throughout — the fallback never once fired on
  a pair that did not need it.
- **2 of 2 true failures caught** — both real Tier D pairs contradicted, both genuinely wrong.

That is 2/2 detection and 0/20 false positives. Suggestive, and far too thin to quote as a rate.

**What to run:** extend the sun sweep past the point where the matcher actually breaks —
**60°, 90°, 120°, 180°** — where ground truth is still exact and the matcher fails while its own
self-consistency metrics stay plausible. Same command, more deltas; ~10 minutes of compute plus
the analysis. Then build the table: **detection rate** (induced failures flagged) against
**false-alarm rate** (good registrations wrongly contradicted), with the failure threshold stated
in metres.

The claim then becomes *"we detect registration failure with a measured detection rate and a
measured false-alarm rate"* — a capability with a number on it. Nothing in the lunar registration
literature surveyed in `PHASE0_RESEARCH_DAY5.md` reports one. **This is the difference between a
colour map and an instrument, and it is the highest novelty return per hour available.**

*What can kill it:* if the detector turns out to raise false alarms at high deltas, log that and
report the honest rate. A measured 70% detection rate is still an instrument; a claimed 100% with
no measurement is not.

### Move 3 — the stretch, if Day 6 has room. 2–3 h, from data already held.

The 1,280 calibrated cells already support a **reliability diagram**: turn "verified" from a label
into a *calibrated bound* — "in verified cells we promise under one pixel, and we are right 98% of
the time" — and plot promised against achieved. Standard in forecasting, essentially absent from
registration papers. No new compute; the data is in `core/reliability_calibration.csv`.

### The honest cost — this is a scope decision, not a free win

Move 2's hours are the same Day 6 hours wanted by **Gate 2 criterion 5** (same-scale classical
comparison — still the only criterion with no evidence and no owner) and by **the deck** (still an
empty `presentation/`, and the deck is the actual deliverable on 9 Sep, since a live demo is not
compulsory). Recommended order: Move 1 tonight in the deck language (free) → Move 2 first thing
Day 6 → **hand criterion 5 to Risheeth in writing rather than doing it.**

**Decided by Samartha:** start the next session with Move 2, then work the remaining steps in
order.
