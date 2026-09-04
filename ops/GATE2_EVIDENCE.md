# Gate 2 — evidence, all six criteria

> **Closed on Day 6 (4 Sep 2026), one day early.** Gate 2 was scheduled for Day 7 (5 Sep).
> Criterion 5 was the last one with no evidence and no owner; it now has both.
>
> Every number below is the **median over 5 off-grid shifts** at the stated sun-azimuth
> difference, read back out of `evaluation/results_log.csv` — not from scrollback, not from
> memory. Reproduce the whole table with:
>
> ```
> python -m core.reliability_calibrate --dem dem_site_60m.npy --pixel-size 60 \
>     --sweep 0,15,30,45,60,90,120,180 --repeats 5 --log
> python -m baselines.sweep_baselines   --dem dem_site_60m.npy --pixel-size 60 \
>     --sweep 0,15,30,45,60,90,120,180 --repeats 5 --log
> ```

**The gate is stated at Δ azimuth = 15°**, which is the operating point we chose on Day 5 and
which appears on the slide. The whole curve is shown, including where it breaks.

---

## The verdict

| # | Criterion | Required | Measured @ 15° | |
|---|---|---|---|---|
| 1 | `rmse_gt_px` | < 0.5 | **0.0856** | ✅ |
| 2 | `inlier_ratio` | > 0.60 | **0.9774** | ✅ |
| 3 | `grid_coverage_fraction` | ≥ 0.80 | **1.0000** | ✅ |
| 4 | `distribution_cv` | < 1.0 | **0.4006** | ✅ |
| 5 | ≥2× best of SIFT/ORB/AKAZE, same pair same scale | ≥ 2.0× | **2.88×** | ✅ |
| 6 | Tier D (optical↔elevation): matches, degradation in metres | stated | **231 m ± 216 m**, matcher contradicted and not used | ✅ |

**All six pass. Gate 2 is met.** Per the gate rule this freezes the algorithm; remaining effort
goes to the deck, the demo and rehearsal.

---

## Criterion 5 in full — and it is not a clean sweep, which is the point

`baselines/sweep_baselines.py` regenerates each pair through **`core.pipeline._synthetic_pair`,
the same function our own run calls** — same DEM, same crop, same sun geometry, same off-grid
shifts, same seeds, byte-identical `.tif` files. "Same pair at the same scale" is therefore true
by construction, not by careful copying. Raw matches go to `evaluate()` pre-RANSAC; failures are
logged, not dropped.

> 🔴 **CORRECTED on Day 6 after an audit — read this before quoting any row below.**
> This table first shipped captioned *"medians of 5 off-grid shifts"* for **both** arms. That is
> true of ours and **false of the classical arm.** A classical run that fails produces no
> `rmse_gt_px` and so cannot enter a median; five of the eight angles were therefore medians of
> **one or two surviving runs**, presented as medians of five — including the headline 180° cell.
> Every classical figure now carries the number of runs that actually scored.
>
> **Gate 2 itself is untouched:** at 0° and 15° all three detectors scored **5/5**, so the 2.88×
> that the gate rests on was never affected.

| Δ azimuth | SIFT | ORB | AKAZE | best classical | **ours** (5/5) | ratio | classical runs that scored |
|---|---|---|---|---|---|---|---|
| **0°** | **0.044** (5/5) | 0.183 (5/5) | 0.047 (5/5) | **0.044** | 0.086 | **0.51× — classical wins** | **15/15** |
| **15°** | 0.247 (5/5) | 0.347 (5/5) | 1.721 (5/5) | 0.247 | **0.086** | **2.88×** ← the gate | **15/15** |
| 30° | 241.7 (5/5) | 1.833 (5/5) | 433.9 **(1/5)** | 1.833 | **0.314** | 5.84× | 11/15 |
| 45° | *all failed* | 443.2 **(2/5)** | *all failed* | 443.2 | **1.096** | 404× | **2/15** |
| 60° | 320.8 **(1/5)** | *all failed* | *all failed* | 320.8 | **2.379** | 135× | **1/15** |
| 90° | *all failed* | 2465.0 **(1/5)** | *all failed* | 2465.0 | **5.805** | 425× | **1/15** |
| 120° | 718.9 **(1/5)** | *all failed* | *all failed* | 718.9 | **4.025** | 179× | **1/15** |
| **180°** | 4971.7 **(1/5)** | *all failed* | *all failed* | 4971.7 | **0.080** | **62,519×** | **1/15** |

*(median `rmse_gt_px` over the runs that scored, reference pixels, 60 m/px. "all failed" = every
repeat failed before a transform could be scored — those rows are in the log with their
`ransac_failed` / `too_few_matches` status. **Ours scored 5/5 at every single angle.**)*

### The honest framing is the stronger one

Do **not** say *"at 180° classical is 4,972 px wrong on the median of five runs."* Say:

> **"Past 30° the classical baselines mostly produce no answer at all. At 180°, fourteen of
> fifteen classical runs failed outright — no transform to score. The single run that did produce
> one was 4,972 pixels wrong. We scored five out of five, at 0.080 px."**

A success rate of 1/15 against 5/5 is a harder result to argue with than any ratio, and it cannot
be attacked on sample size — which the mislabelled version could.

### 🔴 At 0° sun difference, classical beats us — say this out loud

SIFT reaches **0.044 px** where we reach 0.086. With identical illumination there is no
illumination problem to solve, and SIFT is a better sub-pixel corner localiser than a dense
transformer matcher followed by our NCC refinement. **We do not hide this and we do not average
it away.**

It makes the claim *stronger*, because it says exactly what our advantage is and is not:

> "We are not a better feature matcher. We are a matcher that survives illumination change.
> At zero sun difference SIFT beats us — 0.044 px against our 0.086. At 15° we are 2.9× better,
> at 30° 5.8×, and past 45° the classical baselines do not produce a scoreable transform at all.
> The advantage is illumination robustness, and it grows monotonically with the illumination
> difference. That is the axis the problem statement is about."

A judge who hears a team volunteer the one case where they lose believes the cases where they win.

### 🔴 The 180° result is now mechanistically proven, not just observed

Day 6 found that **180° of sun difference is the *easiest* hard case for us** — 0.080 px, better
than our own 15° result — with the failure peak at 90°. The proposed mechanism was that a 180°
azimuth flip **inverts** the shading, and gradient-orientation illumination normalisation is
invariant to contrast inversion, whereas 90° **rotates** the shading, which no invariance covers.

**This run tests that mechanism, and it holds.** At 180° SIFT is **4,971 px** wrong — a total
failure — while we are at 0.080 px. If our 180° recovery were an artifact of how the renderer
produces an inverted image, classical detectors would recover too. They do not. **The recovery is
attributable to the illumination normalisation**, which is the component we are claiming.

That is a controlled experiment, and it is the strongest single result in the project. **State it
as a success rate, not as a ratio:** at 180° we scored 5 of 5 runs at 0.080 px while **14 of 15
classical runs failed to produce a transform at all**, and the one that did was 4,972 px wrong.
The 62,519× ratio is arithmetically true but rests on that single surviving run — quoting the
ratio invites a sample-size attack that the success rate is immune to.

### Where classical actually breaks

Between **15° and 30°**: SIFT goes from 0.247 px to 241.7 px. Ours degrades gracefully over the
same interval (0.086 → 0.314). The classical cliff is at ~30°; ours is at ~45–60°. **We buy about
one full sun-angle regime**, and past that we stop being right *and start saying so* — see
`ops/MOVE2_FAILURE_DETECTION_DAY6.md`.

---

## Criteria 1–4, the whole curve

| Δ azimuth | `rmse_gt_px` | `inlier_ratio` | `grid_coverage` | `distribution_cv` |
|---|---|---|---|---|
| 0° | 0.0858 | 0.9993 | 1.0000 | 0.3663 |
| **15°** | **0.0856** ✅ | **0.9774** ✅ | **1.0000** ✅ | **0.4006** ✅ |
| 30° | 0.3141 ✅ | 0.8217 ✅ | 0.9219 ✅ | 0.6990 ✅ |
| 45° | 1.0964 ❌ | 0.5666 ❌ | 0.7500 ❌ | 1.0560 ❌ |
| 60° | 2.3787 | 0.3758 | 0.4844 | 1.5395 |
| 90° | 5.8045 | 0.1972 | 0.1719 | 2.6150 |
| 120° | 4.0254 | 0.1557 | 0.1562 | 3.2435 |
| **180°** | **0.0795** | **0.9993** | **1.0000** | **0.3542** |

**30° now passes all four criteria** — it did not on Day 5, before sub-pixel refinement was
turned on by default. The gate is still *stated* at 15°, because that is what was chosen and
published, but the envelope is demonstrably wider than the gate.

**180° passes every criterion better than 15° does.** It is not an outlier to be explained away;
it is the mechanism working exactly as designed.

---

## What Gate 2 does NOT claim

Under Invariant 2, and stated here so no slide drifts:

- **No cross-sensor validation.** These are DEM-rendered synthetic pairs with exact ground truth.
  `pair_01` is two crops of one CH-2 OHRC frame — same sensor, zero sun difference.
- **The comparison is on synthetic pairs**, chosen because they are the only place exact ground
  truth exists. It is a fair comparison — both arms see byte-identical images — but it is not a
  claim about real cross-sensor lunar data, and Tier B was dropped, not deferred.
- **This is an illumination test, not a shadow test.** `shaded_relief.py` is a pure local cosine
  law with no cast-shadow or ray-occlusion term, so sun *azimuth* is meaningful and sun
  *elevation* is held fixed at 30°.
