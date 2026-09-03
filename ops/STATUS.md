# STATUS — end of Day 5, third session (3 Sep 2026, night)

> Rewritten in full at the end of every session. True as of 3 Sep 2026, ~22:10 IST (`/wrap`).
> Previous session's STATUS is in git history (`fce6d05`).

---

## Position

```
Day 5 of 11  |  6 days to the event  |  Internal hackathon: 9 SEP 2026 (confirmed)
Novelty weight: 25% (confirmed)   |   Build-alone decision in force (Samartha, Days 5-7)
Gate 1: PASSED, reproducible (two pinned numbers, see below)
Next: Gate 2 on Day 7 (5 Sep) - criteria 1-4 and 6 met on the log; criterion 5 still unowned
```

## 🔴 What this session decided and built — read this first

**Phase 0 (research) and Phase 1 (the novelty bet) are done and written down:**
`ops/PHASE0_RESEARCH_DAY5.md` (evidence ledger, every claim labelled verified/inferred) and
`ops/PHASE1_NOVELTY_DECISION.md` (committed bet + postscript). **The bet is the trust layer:**
"a registration system that knows when it is wrong" — per-cell verified / weak / no-evidence,
an independent pixel check that votes on the matcher's transform, a declared fallback.

**Phase 2 built it in one evening and every measurement is in `evaluation/results_log.csv`
(46 → 111 rows; nothing edited or deleted).** The order was the kill order:

| # | What | Result | Rows |
|---|---|---|---|
| M1 | `core/reliability.py` + `core/reliability_calibrate.py`: calibrate the three states against exact ground truth over the 20-pair sun sweep | **Claim survives.** Verified cells: median true error **0.162 px** (9.7 m), 92% < 0.5 px, 98% < 1 px. Weak 0.363 px. No evidence 0.766 px. | `reliability_calibration_pooled` (config `matcher arm: ours_loftr+subpixel`) |
| M2 | Wrongness check + fallback in `core/pipeline.py`, on both Tier D pairs | Native pair: **0 of 35 measurable cells agree → contradicted**; matcher had 88 matches, 5 inliers, median inlier residual 0.00 px; LoFTR vs truth **0 of 87 correct within 10 px**; fallback (+9, −23) px = **231 m**, quadrant disagreement **216 m**. Coarse pair: contradicted (whole-frame basis), fallback 170 m ± 180 m. | `pair_04_tierD_native`, `pair_03_tierD` (methods `ours_loftr+subpixel`, `fft_phase_correlation (fallback)`, `ours_loftr` ×2 from `ops.tier_d_investigation`) |
| M3 | `core.reliability.gate()` on change detection | On the corrected pair the detector finds **1** candidate; gate: unassessable (native) / rejected (coarse). Nothing kept in a contradicted frame. | `change_detection_absdiff+reliability_gate` ×6 |
| M4 | Sub-pixel A/B, transform-level, real texture + renders + the whole sweep | **Reversed the Day-3 decision.** ON improves true error at every delta (0° 0.120→0.086, 15° 0.249→0.086, 30° 0.571→0.314 → **PASS**, 45° 1.655→1.096 px; real OHRC 0.156→0.024 px) while `residual_px` worsens. **Default is now ON.** | `ours_loftr` (OFF) vs `ours_loftr+subpixel` (ON), 20+20 sweep rows, `ohrc_fracshift_x+0.50_y+0.50` ×2 |

**Two bugs in the reference lighting were found and DERIVED, not fitted** (`evaluation/shaded_relief.py`
reflected the sun about the image diagonal — axis-order bug, pinned by `evaluation/test_shaded_relief.py`;
and a label's true-north azimuth needs the meridian convergence of the polar stereographic projection,
`ops/solar_geometry.py`: 284.9° from north = 329.6° from image-up at 44.7 °E). Both Tier D pairs
were regenerated; the render now correlates with the photograph at +0.64 (was −0.57).

**Demo:** `app/streamlit_app.py` shows the trust map (green/amber/grey over the reference), the
declared method, the fallback with its uncertainty, gated change detection, and loads
**precomputed results** (`ops/precompute_demo_cache.py` → `demo_cache/results/*.pkl`, rebuilt 21:07)
with the live path one checkbox away.

## Smoke test — run this session, exit codes observed

| Check | Result |
|---|---|
| `pytest -q` (full) | **206 passed**, 10 s |
| `python -m core.pipeline data/pairs/pair_01` | `residual_px 0.03761504064805703` (refinement ON, the new default); 63/64 cells verified |
| `python -m core.pipeline data/pairs/pair_01 --no-subpixel` | `residual_px 0.19452325191421008` — the old pinned number, reproduced exactly |
| `python -m core.pipeline data/pairs/pair_04_tierD_native` | CONTRADICTED → `fft_phase_correlation (fallback)`, 231 m ± 216 m |
| `pytest app/test_streamlit_app.py` | 12 passed (first render, no network, no nested buttons) |
| `git diff evaluation/results_log.csv` | only appended rows; test contamination root cause **fixed** (`evaluation/test_metrics.py` now redirects) |

**Re-run at `/wrap` time, exit codes observed not inferred:** `pytest evaluation/ -q` → **21 passed,
exit 0** · `pytest -q` → **206 passed, exit 0** · `import core.pipeline` → **ok, exit 0**.

⚠️ The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly or activate it.
The `/wrap` skill's bare `python` fails here with `ModuleNotFoundError: numpy` — that is the
missing venv, not a broken build.

## The demo was driven in a real browser this session, not judged by eye

`streamlit run app/streamlit_app.py`, then clicked through as a user would. Verified live:

- `pair_01` → 63/64 verified, 1 weak, 0 no-evidence, green tint over the frame. **Matches the
  logged row exactly.**
- `pair_04_tierD_native` → the precomputed result loads instantly (the caption names the commit and
  when it was computed), with the warning **"The matcher's result was contradicted and not used"**,
  0% of 35 cells agreeing, the fallback translation 231 m, the 216 m quadrant disagreement, a
  0/4/60 trust map, and the collapsed expander "What the matcher alone would have shown".
- The five-metric table correctly shows the **matcher's** numbers (residual 4684.9 px, three
  Gate-2 FAILs) beside a fallback that worked — the honest reading, since `evaluate()` always
  scores the raw matcher output. Nobody can mistake one for the other on screen.
- "Detect changes" → the reliability gate reported **0 kept, 5 rejected, 178 unassessable**.

The server was **shut down** at the end of the session (port 8501 free). A background-task
notification claimed the shell had stopped while the process was still listening — check
`netstat -ano | grep 8501` rather than trusting that notification.

## Gate 2 (Day 7) against the log tonight

| # | Criterion | Evidence | Verdict |
|---|---|---|---|
| 1 | `rmse_gt_px` < 0.5 at Δaz ≤ 15° | 0.086 (ON) | ✅ — and 0.314 at 30° now passes too |
| 2 | `inlier_ratio` > 0.60 | 0.93–1.00 at ≤15° | ✅ |
| 3 | `grid_coverage_fraction` ≥ 0.80 | 1.0 | ✅ |
| 4 | `distribution_cv` < 1.0 | ~0.4 | ✅ |
| 5 | ≥2× better than best of SIFT/ORB/AKAZE on the **same pair at the same scale** | **none** | 🔴 unowned. The 20 sweep pairs are on disk (`demo_cache/synthetic/`); it is a baselines run + log |
| 6 | Tier D: matches produced, degradation in metres | 231 m ± 216 m, declared, contradicted matcher | ✅ **honestly** (the system says it cannot verify any cell) |

## Docs swept for false claims (Phase 2 definition of done)

Corrected tonight: `docs/00_CANONICAL_FACTS.md` (§1 evidence table, §2 summary sentence, §6 items
5/6/7 + new §6.9, §8 answers 1–2, §10 deadline discrepancy, layout tree), `docs/SANIYA_NARRATIVE_GUIDE.md`
(slide-2 innovation bullet rewritten; Q&A 5/6/8/9), `docs/RISHEETH_BASELINE_GUIDE.md`,
`docs/ROHAN_DATA_GUIDE.md`, `README.md`, `core/INTERFACES.md`, `evaluation/README.md`,
`ops/PLAN_TO_9_SEP.md` (two correction notes). The "2025 paper benchmarks LoFTR on Chandrayaan-2"
claim was wrong — it benchmarks SuperGlue (SAC ISRO authors) — and is corrected everywhere.

**Deliverables for the team:** `ops/briefs/BRIEF_<NAME>.md` (one per person, Gate 5 material) and
`ops/QA_ANSWERS.md` (the three killers + the trust-layer follow-ups, every number row-named).

## Known issues — do not re-report

1. **Gate 2 criterion 5 is still nobody's.** Risheeth's baselines on the 20 sweep pairs at 60 m/px.
2. **Two `reliability_calibration_pooled` rows exist.** The later one (config `matcher arm:
   ours_loftr+subpixel`) is the shipped default; the earlier is the refinement-OFF arm (0.208 px).
   `core/reliability_calibration.csv` holds the ON run only.
3. **Rows named `ours_loftr` before 3 Sep 21:00 are refinement OFF**; rows after carry
   "sub-pixel NCC refinement ON/OFF" in `config`. The CLI now names the method automatically.
4. **No real pair with a sun difference.** MiLOI (github.com/Bin501/CNSFM, 321 LROC NAC pairs) is
   the route; its ground-truth format is unverified. Not attempted tonight.
5. **`redetect()` still unwired** — the claim was removed instead. No pyramid — claim removed.
6. **Submission deadline discrepancy** (15 vs 20 Sep) — ask the SPOC. Canonical Facts §10 flags it.
7. **`presentation/` is still empty.** Saniya's brief carries the slide-by-slide content; the
   Day-6 contingency (reassign to Samartha if no `.pptx` by end of 4 Sep) stands.
8. The verdict on frames whose cells are narrower than 24 px (pair_03) falls back to the
   whole-frame peak; it says so in `basis`.
9. 🔴 **NEW — the change-detection candidate count is not consistent between entry points.** On
   `pair_04_tierD_native` the live UI button reports **183** raw candidates where
   `python -m ops.gate_tier_d_changes` reports **1**. Cause: the UI hands `detect_changes`
   `to_display()`-percentile-stretched uint8 images, the ops script hands it raw float32 arrays and
   lets `detect_changes` do its own max-based scaling. Same detector, different contrast going in.
   **The gate's conclusion is identical either way — 0 kept, because no cell is verified — so the
   novelty claim is unaffected**, but a judge who tries both routes sees two numbers. Fix by making
   one path use the other's preprocessing; do not "fix" it by deleting a row. Neither number is
   quoted anywhere in the deck.

## After the wrap — three things happened, and they change the Day-6 order

The session was wrapped at `af94228`. Three things followed and are recorded here because the
handoff would otherwise be stale:

1. **Samartha challenged the novelty framing** — *"why are we playing safe? we need full marks."*
   The answer is written into `ops/PHASE1_NOVELTY_DECISION.md` as a dated amendment. **The bet is
   unchanged; the pitch language was under-sold.** Three moves came out of it (reframe / measured
   detection rate / calibrated bound). **Samartha decided: the next session starts with Move 2.**
2. **A teaching document was published** — a from-zero primer on the whole project for Gate 5 prep
   and for briefing anyone who has not seen the code:
   `https://claude.ai/code/artifact/ce1b8d99-e4ed-44c5-98aa-08cfc009c49c`
   It is an artifact, not a repo file. Every number in it was re-read from `results_log.csv` and
   `core/reliability_calibration_summary.csv` at the time of writing, not recalled.
3. **One figure was verified first-hand and is now quotable:** across all 20 calibration pairs
   (1,280 rows of `core/reliability_calibration.csv`), `global_contradicted` is `False` in every
   row and `method_used` is `loftr+magsac++` throughout — **the trust layer raised zero false
   alarms on 20 known-good pairs, and the fallback never fired when it was not needed.** Together
   with both real Tier D pairs contradicted, that is 2/2 caught and 0/20 false positives. Too thin
   to quote as a *rate*; it is the seed of Move 2.

## Next session (Day 6, 4 Sep) — in order

1. **`git push`** — three commits are local-only now (`65b3224`, `af94228`, and tonight's).
   Deferred at the user's instruction on Day 5; it is the first action of Day 6, before anyone pulls.
2. `/next`, pull, `pytest -q`, both Gate-1 commands.
3. **Move 2 — the failure-detection rate.** Extend the sun sweep to 60/90/120/180°, where ground
   truth is still exact and the matcher fails while its self-consistency metrics stay plausible.
   Build the detection-rate vs false-alarm-rate table with the failure threshold stated in metres,
   and log the rows. ~Half a day. Full reasoning and kill conditions in the
   `PHASE1_NOVELTY_DECISION.md` amendment. **This is task one by Samartha's decision.**
4. **Move 1 — the reframe** into the deck language (free, no compute): the PS asks for RMSE, inlier
   count and inlier ratio; we implemented all three and found the case where all three pass and the
   answer is 100% wrong. Goes into `docs/SANIYA_NARRATIVE_GUIDE.md` slide-2 wording.
5. Gate 2 criterion 5: **hand to Risheeth in writing** rather than doing it — the three classical
   baselines on the 20 sweep pairs at the same scale, logged.
6. Deck: transcribe `docs/SANIYA_NARRATIVE_GUIDE.md` + `ops/briefs/BRIEF_SANIYA.md` into the
   official template; one figure = the trust map on the Tier D pair from the app.
7. Gate 3 rehearsal with a stranger on the cached demo; Gate 4 dry run with wifi off
   (`ops/precompute_demo_cache.py` must be re-run after any change to `core/`).
8. Known issue 9 (change-detection preprocessing mismatch) — one of the two paths, ~20 minutes.
9. **Move 3 (stretch)** — the reliability diagram from the 1,280 cells already held, 2–3 h, no new
   compute. Only if Day 6 has room after 3–8.
10. Optional: MiLOI (2-hour timebox to check ground truth), `redetect()` opt-in flag with logged rows.

⚠️ **Not yet done and not silently dropped:** the 19 teammate commits dated 2–3 Sep (Rishabh,
Risheeth, Samrudh) are already merged into local `main` but have **not** had a `/review` pass this
session. Run `/review` before building on `evaluation/` or `baselines/`.

## `/wrap` step 4 (nightly specs) deliberately NOT run — second night running

No `spec-writer` agent. The build-alone decision (Days 5–7) means the five teammates are not being
handed nightly task specs, so drafting them would contradict the plan in force. **What replaces
them is stronger and already written:** one brief per person in `ops/briefs/BRIEF_<NAME>.md`, each
covering what changed in their area, the questions they must answer cold for Gate 5, and an
explicit "never say" list. Recorded here rather than silently omitted.

## Not doing — settled

Bet A (closed); a cross-sensor chase; a pyramid; a new matcher; any VM/cloud; re-litigating the
refinement default without a transform-level measurement that says otherwise.
