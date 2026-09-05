# Demo script — 3:00, Gate 3 and the internal round

**Written 5 Sep 2026 (Day 7). Every number here is on screen or in
`evaluation/results_log.csv`, and the row is named. If a figure is not in this script, it is not
said.** Rehearse with a timer. The demo runs on the *precomputed* result — the box stays ticked —
because a 15-second live align inside a three-minute pitch is risk with no upside. The live path
is one untick away and question 4 below is what to say if a judge asks for it.

Before you start: **launch from the repo root**, wifi off, browser at 100% zoom, sidebar open,
`pair_01` selected but **not yet aligned**.

---

## 0:00 – 0:25 · The problem, in the judge's language

> "Two photographs of the same place on the Moon, taken months apart, look completely different —
> because the Sun has moved and the shadows with it. Standard software aligns images by finding
> corners and edges, and a shadow edge is a fake corner that moves. So the alignment drifts, and
> nobody downstream is told."

Point at the two plates on screen (do not click yet).

> "This is a Chandrayaan-2 frame against a reference. Our system does three things: it removes the
> lighting before matching, it matches whole patches instead of corners — and then it does the
> part nobody else does, which is tell you **where on the image you are allowed to believe the
> answer**."

---

## 0:25 – 1:00 · Align, and the picture that convinces

Click **ALIGN**. It returns instantly (precomputed).

Read the verdict strip aloud — it is one sentence in plain words:

> "**Aligned.** The matcher registered it, and an independent check of the pixels — which never
> sees the matches — agrees."

Scroll to **02 SWIPE** and drag the seam back and forth twice.

> "Left of the line is the reference, right of it is the aligned image. Craters run straight
> across the seam. That is the whole result, before any number."

**If the room is quiet, this is the moment to pause.** The swipe is more convincing than any
figure and it costs five seconds.

---

## 1:00 – 1:50 · The trust layer — this is the novelty, spend the time here

Scroll to **03 WHERE THE ALIGNMENT CAN BE TRUSTED**.

> "Every cell of the frame gets one of three states. **Verified** in green: enough matches, they
> agree with the transform, *and* an independent check of the pixels agrees too. **Weak**, hatched
> amber. **No evidence**, faded out — and that is a separate state, not a bad score. It means the
> matcher measured nothing there. Painting it green or red would both be inventions."

Point at the counts: **63 verified, 1 weak, 0 no-evidence** on this pair.

> "And *verified* is a measured promise, not a word. Across our rendered sweep with exact ground
> truth, inside the envelope we claim — sun difference of 30 degrees or less — cells we mark
> verified have a median true error of **0.123 pixels, 7.4 metres on the ground, with 99% under
> half a pixel, over 817 cells.**"

Row: `reliability_calibration_envelope`.

> "Outside that envelope it degrades and we show the curve rather than the average: 0.580 pixels at
> 45 degrees, 1.016 at 60."

---

## 1:50 – 2:40 · The pair where the matcher is confidently wrong

Switch the sidebar to **`pair_04_tierD_native`**, click **ALIGN**.

> "This one is different in kind: a Kaguya photograph against a LOLA elevation model. Optical
> against elevation — genuinely two modalities, which is what the problem statement asks about."

Read the rail: **TIER D · Kaguya_TC vs LOLA_LDEM**.

> "The matcher found 88 correspondences and RANSAC reached consensus on a transform. It was
> **completely wrong** — and here is the point of the whole project: **the system knew.** Zero of
> the 35 measurable cells agreed with that transform. So it declared the matcher contradicted,
> threw its answer away, fell back to global correlation of the raw pixels, and registered the
> pair by **231 metres** — while telling you the four quadrants disagree with each other by up to
> **216 metres**, which is the uncertainty to quote."

Point at **04 THE FIVE METRICS** and the rule above it.

> "The metrics here say *matcher's metrics — transform not used*, and three of them read FAIL.
> That is the system reporting its own failure rather than hiding it — these are the numbers for a
> transform it threw away."

> ⚠️ **Do NOT say "it was 43.9 kilometres out."** That is `residual_px` times the grid — a fit
> residual converted to metres, which is the exact error this project exists to prevent, and the
> app prints it labelled *not an accuracy*. The true error against ground truth is **~200 px, about
> two kilometres.** If you want the number, say that one."

---

## 2:40 – 3:00 · Land it

> "So: illumination-robust registration that **beats classical methods by 2.88× at 15 degrees of
> sun difference** — and loses to SIFT at zero degrees, which we also put on the slide, because
> with identical lighting there is no illumination problem to solve.
>
> But the contribution is the second half. Every alignment comes with a per-cell map of where it
> can be trusted, calibrated against ground truth, with an explicit *no evidence* state — and a
> system that detects its own failure at **77% with a zero percent false-alarm rate** and says so
> instead of returning a confident number."

Stop. Do not fill silence.

---

## The four questions this demo invites, and the short answers

Full versions in `ops/QA_ANSWERS.md`; these are the 20-second forms.

1. **"Is this cross-sensor?"** — "No, and we never say it is. `pair_01` is two crops of one
   Chandrayaan-2 frame; the Tier D pair is optical against elevation, which is multi-modal but not
   two cameras. We have no cross-sensor pair and the UI says so on screen." (§1)

2. **"What is the smallest error it can catch?"** — "Two and a half reference pixels, 150 metres
   at this grid, by construction — the area check reads an integer correlation peak against a
   2-pixel threshold. That is also why our 45-to-60-degree blind spot exists: at 60 degrees we are
   142.7 metres out, which is inside that floor." (§8)

3. **"Why does the headline pair show no metres?"** — "Neither of that pair's labels carries a map
   scale, so we print the pixel figure and say the metres are unavailable rather than multiply by
   a number the file does not contain. The Tier D pair does carry one, and there we print both."

4. **"Can you run it live?"** — "Yes — untick the box and it runs the real pipeline in about 15
   seconds on this CPU. The precomputed result is the same `run_all()` output saved earlier; it is
   not a different code path." Then do it, if there is time.

---

## Rules for whoever is driving

- **Never say** cross-sensor · pyramid · "we enforce uniformity" · any Tier D residual as an
  accuracy · "accurate shadows" · "0.7 px" · a pixel figure without its grid and its metres.
- **Do not read `residual_px` aloud as an accuracy on any real pair.** It is a fit residual. The
  readout on screen already says so; let it.
- If the projector washes the screen out, tick **Projector mode (larger type)** in the sidebar and
  carry on. Do not start restyling.
- If anything crashes: say "that is what Gate 4 is for" and switch to the PDF handout. Do not
  debug in front of the room.
