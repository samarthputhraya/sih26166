# Brief for Rishabh — `app/change_detection.py` — what changed on 3 Sep and what you must explain

**Read time: 8 minutes.** Your detector was not edited. What changed is what sits *in front of* it
and what sits *after* it.

## What changed

1. **The alignment your detector receives is now the one the system declared.** `run_all()` returns
   `warped_final`: when the matcher's homography is contradicted by the pixels (both Tier D pairs),
   that is the fallback translation from global correlation, not the matcher's warp. The Streamlit
   app feeds `warped_final` to `detect_changes`. The matcher's own warp is kept under an expander
   labelled "what the matcher alone would have shown".
2. **A gate after your detector — `core.reliability.gate()`.** Every candidate you return gets a
   `reliability` label from the cell its centroid lands in: *verified* (kept), *weak* (rejected),
   *no evidence* (**unassessable** — reported under that word, not as a false alarm, because a
   difference in a region where the alignment was never measured is a hole in the evidence, not a
   detection). If the whole frame's transform was contradicted, nothing is kept. Your output is
   labelled, never altered.
3. **`ops/gate_tier_d_changes.py`** runs your detector on a Tier D pair and gates it, with
   `--alignment declared|matcher`, and logs rows `change_detection_absdiff+reliability_gate`.

## What the numbers now say

- Your Day-6 note: 35 candidates on the optical ↔ elevation pair, 0 real, 31 shadow, 4 artefacts —
  measured on the reflected render with the matcher's misalignment. That number stays in the log
  as history.
- Tonight, on the pair aligned by the declared fallback: **1 candidate, unassessable** (its cell has
  no inliers). With the matcher's contradicted alignment: `[TBD — results_log.csv]` candidates, all
  rejected because no cell in a contradicted frame can be verified. Both rows are logged under
  `pair_04_tierD_native` / `pair_03_tierD`, method `change_detection_absdiff+reliability_gate`.
- **The honest sentence:** "On this pair no change-detection result is quotable, and the system
  says so instead of showing 35 boxes."

## The five questions you must answer cold

1. **"Why did your detector find 35 changes on a pair with none?"** — Because the two images were
   misaligned and differently lit; absolute difference cannot tell a moved shadow from a moved
   rock. That is exactly why the output is now gated by where the alignment is verified.
2. **"What does the gate change?"** — Nothing in the detection. It attaches a reliability state per
   candidate and reports three counts: kept, rejected, unassessable.
3. **"Why three states and not a confidence score?"** — "No evidence" is an absence of measurement,
   not a low confidence. Scoring it low would claim knowledge we do not have.
4. **"Would a real change ever be kept?"** — Only in a verified cell of a frame whose transform the
   pixels agree with. On the synthetic sweep at ≤15° sun difference nearly every cell is verified;
   that is where the detector could speak.
5. **"How do you classify shadow vs new bright?"** — Your own `classify()` rules; know them
   (elongation, intensity sign). The gate does not touch the classification.

## Never say

"We detected N changes on the Moon"; any Tier D number as a detection rate; "the detector rejects
shadows" (it labels them as likely shadow; the gate is what rejects unverified regions).
