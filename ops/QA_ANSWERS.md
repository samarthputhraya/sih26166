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
> shifts). And we have now run the classical baselines on those exact same pairs — at 15° the best
> of SIFT, ORB and AKAZE is 0.247 px against our 0.086, so **2.88× better**."

*Follow-up: "So the classical comparison isn't done?"* → **Done on Day 6.** "Same-scale, on
byte-identical files: `baselines/sweep_baselines.py` regenerates each pair through the same
function our own run calls, so both arms see the same pixels. The old SIFT rows at 10 m/px are a
different experiment and we still do not compare across grids."

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
> "Measured, not asserted, and promised only inside the envelope we claim. Across the rendered
> sweep with exact ground truth, at a sun azimuth difference of 30° or less, the cells we mark
> verified have a median true error of **0.123 px — 7.4 metres at 60 m/px — with 99.0% under
> half a pixel and 100% under one pixel, over 817 cells.** Weak cells: 0.229 px. No-evidence
> cells: 0.390 px. Row `reliability_calibration_envelope`; derivation
> `core/reliability_calibration.csv`, one row per cell.
>
> Outside that envelope it degrades, and we show the whole curve rather than the average: at 45°
> the verified median is 0.580 px and only 38.5% are under half a pixel; at 60° it is 1.016 px.
> So 'verified' is a half-pixel promise inside 30° and a one-pixel promise at 45°, and the slide
> says which. Pool everything together and you get 0.147 px, which looks similar and means less,
> because it averages the case we claim with five cases we do not."

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

## Added Day 6 — the four questions today's results invite

### 4. "You claim you beat classical methods. By how much, and where do you lose?"

> "At 15° of sun difference, **2.88×** — best classical 0.247 px against our 0.086, medians of five
> off-grid shifts on byte-identical pairs. At 30° it is 5.84×, and past 45° the classical baselines
> stop producing a scoreable transform at all.
>
> **And at 0° we lose.** SIFT gets 0.044 px where we get 0.086. With identical illumination there
> is no illumination problem to solve, and SIFT is a better sub-pixel corner localiser than a dense
> matcher plus our refinement. So the claim is not *'a better matcher'* — it is **illumination
> robustness, and it grows monotonically with the sun difference.** That is the axis the problem
> statement is about."

**Say the 0° loss before they find it.** A team that volunteers the case where it loses is believed
about the cases where it wins. Rows: methods `SIFT`/`ORB`/`AKAZE`, notes `GATE 2 CRITERION 5`.

### 5. "Your error goes DOWN at 180° of sun difference. That looks like a bug."

> "It looks like one, so we tested it. At 180° we are at 0.080 px — better than our own 15° number
> — and the failure peak is at **90°**, not at the extreme.
>
> The reason is the illumination normalisation. A 180° azimuth flip **inverts** the shading: lit
> slopes become shadowed. We normalise on **gradient orientation**, which is invariant to contrast
> inversion, so an inverted render still matches. At 90° the shading **rotates** instead — ridges
> that ran across the frame now run along it — and no invariance covers that. **The hard axis is
> orthogonality, not magnitude.**
>
> The control is the classical arm on the same pairs. At 180°, **fourteen of fifteen classical
> runs failed to produce a scoreable transform at all**; the single one that did was **4,972 px
> wrong.** We scored five of five, at 0.080 px. If our
> recovery were an artifact of how the renderer produces an inverted image, classical would recover
> too. It does not. That attributes the recovery to the component we are claiming."

### 6. "How often does your failure detector actually work?"

> "Measured over 40 pairs and 2,560 cells with exact ground truth. At a failure threshold of
> **120 m**: **77% detection at a 0% false-alarm rate** — across 27 pairs that were correct it never
> once raised a false alarm. Raise the threshold to 240 m and detection is 10 of 10, at the cost of
> a 9% false-alarm rate.
>
> **And there is a blind spot we will state before you find it:** between 45° and 60° the system is
> wrong and does not know it. At 60° the transform is 142.7 m out and the contradiction flag stays
> down. Not the extremes — the *shoulder*, where degradation is gradual and the self-check has not
> yet tripped."

*Follow-up: "Why is a 0% false-alarm rate the number you lead with?"* → "Because a failure detector
that fires on good data is worse than none — nobody keeps trusting it. Detection rate is
adjustable by threshold; the false-alarm rate is the one that decides whether an operator believes
the amber cells."

### 7. "How do we know your own numbers are right?"

> "We assume they are not, until a second, independent path agrees. Two examples from Day 6 alone.
>
> The change detector reported **183 candidates in the UI and 1 from the command line** on the same
> pair. That was not cosmetic: it normalised both images by their *combined* max, and on a
> multi-modal pair the reference peaks at 37,488 DN against the optical image's 2,040 — so the
> optical image was crushed to a 2–98 percentile range of [0, 5] and nothing could exceed the
> threshold. The '1 candidate' was contrast collapse, on exactly the multi-modal case this project
> is about. It is fixed, both paths now agree, and it is pinned with a test that feeds the same
> pixels through both preprocessings and requires the same answer.
>
> Second: a logged row described its own population as four sun angles when the run used eight,
> because that string was hardcoded. Also fixed, and the delta list is now derived.
>
> **Every number we quote is in `evaluation/results_log.csv`, which is append-only — nothing is
> edited or deleted, including the rows that made us look worse.**"

---

## Things we do not say

Cross-sensor · pyramid · "we enforce uniformity" · "a 2025 paper benchmarks LoFTR on Chandrayaan-2"
· any Tier D residual as an accuracy · "accurate shadows" · "0.7 px" · a pixel figure without its
grid and its metres.
