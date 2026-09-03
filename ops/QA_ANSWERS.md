# Q&A — the questions most likely to end the round, with the answers we will give

**Written 3 Sep 2026 (Day 5, night). Every number below is in `evaluation/results_log.csv`; the row
is named. Rehearse these aloud. If a number is not here, it is not said on stage.**

Row-naming key: `ours_loftr` = refinement OFF; `ours_loftr+subpixel` = refinement ON (the shipped
default since 3 Sep); `fft_phase_correlation (fallback)` = what the system declared on Tier D;
`reliability_calibration_pooled` (config `matcher arm: ours_loftr+subpixel`) = the calibration.

---

## The three that end a round

### 1. "Show me a cross-sensor result."

> "We don't have one, and we say so. Tier A and Tier B were never cut; every real pair we own is
> either one OHRC frame cropped twice or a Kaguya photograph against a LOLA elevation model. What we
> validate is sun-angle invariance against exact ground truth on a rendered sweep, and — the part
> that is ours — where in the frame an alignment can be trusted. If you want the cross-sensor
> number, the honest answer is that the public MiLOI set (321 multi-illumination LROC NAC pairs with
> ground truth) is the route, and it is a same-sensor sun-angle set, not cross-sensor either."

*Follow-up: "Then what does the PS's 'multi-modal' mean for you?"* → question 3.

### 2. "Your log says AKAZE gets 0.12 px and you get 0.19 px on the same pair."

> "Correct, and we log it. That pair (`pair_01`) is one OHRC frame cropped twice — zero sun
> difference, the one case where a classical detector is strongest and illumination normalisation
> buys nothing. With refinement on we get 0.038 px there (row `pair_01`, method
> `ours_loftr+subpixel`), but that is a fit residual on a pair with no ground truth, so we do not
> call either number an accuracy. Where we measure accuracy — the rendered sweep with exact ground
> truth — the median true error is 0.086 px at 0° and 15° sun difference, 0.314 px at 30° and
> 1.096 px at 45° (rows `synthetic_d0xx_*`, method `ours_loftr+subpixel`, medians of five off-grid
> shifts). Same-scale classical baselines on those same 20 pairs are the open item; Risheeth has
> the pairs."

*Follow-up: "So the classical comparison isn't done?"* → "Not at the same scale. The SIFT rows at
10 m/px are a different experiment and we do not compare across grids."

### 3. "The PS asks for multi-modal OHRC/TMC/IIRS. Where is it?"

> "Our one real multi-modal pair is optical against elevation: a Kaguya photograph against a LOLA
> hillshade rendered at the photograph's own sun geometry. Our feature matcher produced 87
> correspondences and RANSAC reached consensus on a homography. Zero of the 87 were correct within
> 10 pixels — 94 metres — and we know because we built the ground truth for that pair by global
> correlation and checked it quadrant by quadrant (rows `pair_04_tierD_native`, method
> `ours_loftr`, 3 Sep evening). A fit residual would have called that registration sub-pixel. Our
> trust layer looked at the pixels instead: 0 of 35 measurable cells agreed with the transform, so
> the system declared it contradicted, switched to global phase correlation, registered the pair by
> 231 metres, and reported that the four quadrants disagree by up to 216 metres — the two products
> are not related by one translation (row `fft_phase_correlation (fallback)`). We have no
> optical-against-infrared pair. What we can show is a system that knows when its matcher has
> failed on a modality, and says so."

---

## The trust layer — the questions a hostile expert asks next

**"Isn't this just the RANSAC inlier ratio with a colour map?"**
> "No. On that pair the inlier consensus held — the median inlier residual was 0.00 px — and every
> match was wrong. Our verdict comes from an independent test that never sees the matches: each
> cell of the warped source is cross-correlated against the reference, and the cells vote. And
> 'no evidence' is a separate state, not a low score: a cell with no inliers is unmeasured, and
> painting it red or green would both be fabrications."

**"Uss et al. did per-region accuracy without ground truth in 2016, including optical–DEM."**
> "Yes — and it is on our references slide with Brown & Lowe 2007 and Wan et al. 2021. Theirs is a
> continuous accuracy bound inside an area-based method. Ours is a three-state map over a learned
> matcher's output with an explicit unmeasured state, a pixel-versus-match disagreement as the
> failure signal, a declared fallback, and a calibration on lunar data. It is a system
> contribution, not a new estimator, and we say that."

**"What does 'verified' actually promise?"**
> "Measured, not asserted. Over 20 rendered pairs with exact ground truth — 1,280 cells — the
> cells we mark verified have a median true error of 0.162 px, 9.7 metres at 60 m/px; 92% are
> under half a pixel and 98% under one pixel. Weak cells: 0.363 px median. No-evidence cells: 0.766
> px. At 45° of sun difference 'verified' is a one-pixel promise, not a half-pixel one, and we
> show that column (row `reliability_calibration_pooled`; derivation
> `core/reliability_calibration.csv`)."

**"Why is the verdict a vote of cells and not one correlation of the whole frame?"**
> "Because we tried the whole frame first and it was wrong. At 30–45° of sun difference the
> large-scale shading change pulls the whole-frame peak 10–17 px off while 85–93% of the cells
> still agree within 2 px — and the fallback that triggered was ten to forty times less accurate
> than the homography it replaced. Cells are high-pass by construction and vote independently.
> That was measured on the same sweep and is why the rule is what it is."

**"Do your synthetic shadows move?"**
> "No. The renderer is a local cosine law with no cast-shadow term. A sun azimuth change rotates
> the shading; a spire that should throw a long shadow throws none. So the sweep is an illumination
> test, not a shadow test, and we hold the sun elevation fixed at 30° for that reason. The
> PS-setters' own simulator paper lists Lambertian as the simplest of three reflectance models; ours
> is that one."

**"The renderer had a bug. How do you know it is right now?"**
> "Two errors, both derived rather than fitted. `np.gradient` returns axis-ordered gradients and
> the old code swapped them, reflecting the sun about the image diagonal — a six-line test on a
> synthetic hill and crater now pins the convention. And a label's solar azimuth is measured from
> true north, which in the south-polar stereographic projection is rotated clockwise by the
> longitude: 284.9° from north is 329.6° from image-up at 44.7 °E. The render now correlates with
> the photograph at +0.64 at zero offset; it was −0.57."

**"You turned sub-pixel refinement on. Yesterday's notes say it hurt."**
> "Both are true and both are logged. Per-match endpoint error said refinement hurt LoFTR
> (0.336 → 0.431 px). The transform-level true error — the metric Gate 2 is judged on — says it
> helps at every sun difference: 0.120 → 0.086 at 0°, 0.249 → 0.086 at 15°, 0.571 → 0.314 at 30°,
> 1.655 → 1.096 at 45°, and 0.156 → 0.024 px on real OHRC texture with a known half-pixel shift.
> RANSAC averages thousands of matches, so the transform improves while individual matches get
> noisier. We changed the default on that evidence and kept the switch. The lesson is the one this
> whole project is about: a residual is not an accuracy, in either direction."

**"Why LoFTR and not SuperGlue, which the SAC paper found best?"**
> "SuperGlue's published weights depend on SuperPoint, whose licence is academic non-commercial
> only. LoFTR is Apache-2.0, detector-free, and runs on this laptop's CPU in about six seconds per
> 640-pixel tile with no GPU. If ISRO wanted to deploy this, the licence is the difference."

---

## Things we do not say

Cross-sensor · pyramid · "we enforce uniformity" · "a 2025 paper benchmarks LoFTR on Chandrayaan-2"
· any Tier D residual as an accuracy · "accurate shadows" · "0.7 px" · a pixel figure without its
grid and its metres.
