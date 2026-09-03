# STATUS — end of Day 5, third session (3 Sep 2026, night)

> Rewritten in full at the end of every session. True as of 3 Sep 2026, ~21:20 IST.
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

⚠️ The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly or activate it.

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

## Next session (Day 6, 4 Sep) — in order

1. `/next`, pull, `pytest -q`, both Gate-1 commands.
2. Gate 2 criterion 5: run the three classical baselines on the 20 sweep pairs and log them, or
   assign it in writing.
3. Deck: transcribe `docs/SANIYA_NARRATIVE_GUIDE.md` + `ops/briefs/BRIEF_SANIYA.md` into the
   official template; one figure = the trust map on the Tier D pair from the app.
4. Gate 3 rehearsal with a stranger on the cached demo; Gate 4 dry run with wifi off
   (`ops/precompute_demo_cache.py` must be re-run after any change to `core/`).
5. Optional: MiLOI (2-hour timebox to check ground truth), `redetect()` opt-in flag with logged rows.

## Not doing — settled

Bet A (closed); a cross-sensor chase; a pyramid; a new matcher; any VM/cloud; re-litigating the
refinement default without a transform-level measurement that says otherwise.
