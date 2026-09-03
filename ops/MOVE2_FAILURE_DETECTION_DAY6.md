# Move 2 — the failure-detection rate, measured

> Day 6, 4 Sep 2026. Run: `python -m core.reliability_calibrate --dem dem_site_60m.npy
> --pixel-size 60 --sweep 0,15,30,45,60,90,120,180 --repeats 5 --log`
> 40 pairs · 2,560 cells · every row in `core/reliability_calibration.csv`; citations in
> `evaluation/results_log.csv` (`reliability_calibration_pooled`, 4 Sep, 8-delta config).
> Ground truth is exact at every delta — the pair is rendered from one DEM under two suns and
> warped by a known homography, so "true error" is not an estimate.

Move 2 asked: *does the trust layer detect failure once, or does it always?* Day 5 had one
anecdote (2 of 2 real Tier D pairs caught, 0 of 20 false alarms). This is the measurement.

---

## 1 · What the sweep did to the matcher

| Δ azimuth | pairs | **contradicted** | median `rmse_gt_px` | in metres @ 60 m/px |
|---|---|---|---|---|
| 0° | 5 | 0 | 0.086 | 5.1 m |
| 15° | 5 | 0 | 0.086 | 5.1 m |
| 30° | 5 | 0 | 0.314 | 18.8 m |
| 45° | 5 | 0 | 1.096 | 65.8 m |
| 60° | 5 | 0 | 2.379 | **142.7 m** |
| 90° | 5 | **5** | 5.805 | 348.3 m |
| 120° | 5 | **5** | 4.025 | 241.5 m |
| **180°** | 5 | 0 | **0.080** | **4.8 m** |

## 2 · 🔴 The headline is not the one we expected: 180° is the *easiest* hard case

**At a 180° sun-azimuth difference the matcher is as accurate as at 0°** — 0.080 px, 4.8 m, with
**100% of verified cells under half a pixel** (n=298). The failure peak is at **90°**, not at the
extreme.

This is explicable and it is not luck. A 180° azimuth flip **inverts** the shading: what was a lit
slope becomes a shadowed one. Our illumination normalisation is **gradient orientation**, which is
invariant to contrast inversion — orientation is preserved under negation, so an inverted render
still matches. At 90° the shading is not inverted but **rotated**: ridge lines that ran across the
frame now run along it, gradient orientation genuinely changes, and there is no invariance to
exploit. **The hard axis is orthogonality, not magnitude.**

Nothing in the lunar-registration literature surveyed in `PHASE0_RESEARCH_DAY5.md` reports this.
It is a measured, counter-intuitive, mechanistically explained result — and it is free novelty,
because we already had the data.

## 3 · Detection rate against false-alarm rate

"Failure" has to be defined before a detection rate means anything, so here it is at four
thresholds. A pair counts as a true failure when its median `rmse_gt_px` exceeds the threshold; a
detection is `global_contradicted = True` on that pair.

| Failure threshold | true failures | detected | **detection rate** | good pairs | false alarms | **false-alarm rate** |
|---|---|---|---|---|---|---|
| 0.5 px = 30 m | 20 | 10 | 50% | 20 | 0 | **0%** |
| 1.0 px = 60 m | 18 | 10 | 56% | 22 | 0 | **0%** |
| **2.0 px = 120 m** | 13 | 10 | **77%** | 27 | 0 | **0%** |
| 4.0 px = 240 m | 7 | 7 | **100%** | 33 | 3 | 9% |

**The defensible operating point is 120 m: 77% detection at a 0% false-alarm rate.** Push the
threshold to 240 m and detection is 10 of 10 — but three good pairs get flagged, so the honest
statement is *100% detection at a 9% false-alarm cost*, not "100% detection".

**The zero false-alarm column is the strong half.** Across 27 pairs that were right to within
120 m, the system never once cried wolf. A failure detector that fires on good data is worse than
none, because nobody keeps trusting it.

## 4 · 🔴 The blind spot, stated before a judge finds it

**Between 45° and 60° the system is wrong and does not know it.** At 60° the transform is
**142.7 m** out, the contradiction flag stays down, and 33 cells are still labelled *verified* —
of which only 9.1% are actually under half a pixel. That is the gap: not the extremes, which are
either fine (180°) or caught (90–120°), but the **shoulder** where degradation is real and
gradual and the self-check has not yet tripped.

We say this ourselves, on the slide. A limitation we name is a limitation we own.

## 5 · What this changes about the number we quote

**Stop quoting the pooled figure.** Pooling now averages over deltas we do not claim to operate
at, so it *understates* the system inside its envelope and *overstates* it outside:

| Population | n cells | median | < 0.5 px | < 1 px |
|---|---|---|---|---|
| **Δaz ≤ 30° — the claimed envelope** | **817** | **0.123 px (7.4 m)** | **99.0%** | **100%** |
| pooled over all 8 deltas | 1,257 | 0.147 px (8.8 m) | 91.6% | 96.7% |
| 45° only | 109 | 0.580 px | 38.5% | 78.9% |
| 60° only | 33 | 1.016 px | 9.1% | 42.4% |
| 180° only | 298 | 0.080 px | 100% | 100% |

**The number for the deck is the envelope row: inside Δaz ≤ 30°, cells marked *verified* have a
median true error of 0.123 px = 7.4 m, 99.0% are under half a pixel and 100% under one pixel,
over 817 cells.** That is both more honest and *better* than the 0.162 px / 92% we published on
Day 5 — because the Day-5 pooled figure was dragged down by 45°, a delta outside the envelope.

## 6 · ⚠️ Provenance note — two things changed under existing documents

1. **`core/reliability_calibration.csv` was rewritten** (the script opens it `"w"`, by design —
   it is a derivation, not a log). It now holds 2,560 cells over 8 deltas instead of 1,280 over 4.
   The Day-5 population is preserved in `evaluation/results_log.csv` row
   `reliability_calibration_pooled` dated 3 Sep 15:36, and a pre-run backup was taken.
   **No results_log row was edited or deleted.**
2. **Six documents quote the Day-5 pooled figure "0.162 px / 926 cells / 92% / 98%"** —
   `ops/briefs/BRIEF_SAMARTHA.md`, `BRIEF_SAMRUDH.md`, `BRIEF_SANIYA.md`,
   `ops/PHASE1_NOVELTY_DECISION.md`, `ops/QA_ANSWERS.md`, `ops/STATUS.md`. Those figures remain
   **traceable and true** for the 20-pair population, but they should be migrated to the envelope
   figure in §5 before the deck is built. Tracked as Day-6 follow-up.
3. **A logged row misdescribed its own population and was corrected.** The first 8-delta run wrote
   `config = "...deltas 0/15/30/45 deg x 5 off-grid shifts"` — hardcoded — against 40 pairs, which
   is self-contradictory. `core/reliability_calibrate.py` now derives the delta list and the repeat
   count from the summary; a corrected row was appended (4 Sep 19:16). The wrong row was **not**
   deleted, per the append-only rule; it is superseded, and this note is why.

## 7 · Kill conditions from `PHASE1_NOVELTY_DECISION.md` — checked

The amendment said: *"if the detector turns out to raise false alarms at high deltas, log that and
report the honest rate. A measured 70% detection rate is still an instrument; a claimed 100% with
no measurement is not."*

**It did not raise false alarms** — 0% up to a 120 m threshold. The claim survives, with a
measured detection rate of **77% at 120 m**, a blind spot named at 45–60°, and an unexpected
result at 180° that is worth more than the rate itself.
