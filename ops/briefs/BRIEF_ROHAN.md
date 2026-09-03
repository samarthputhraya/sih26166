# Brief for Rohan — `data/` and the Tier D builders — what changed on 3 Sep and what you must explain

**Read time: 10 minutes.** Your Tier D pair was rebuilt tonight. You must be able to explain why,
and what the sun-azimuth number in PROVENANCE.md now means.

## What changed

1. **`ops/build_tier_d_pair.py` and `ops/build_tier_d_native.py`** now render the LOLA hillshade at
   the sun azimuth **in the image frame**, not at the label's value. The Kaguya STAC field
   `view:sun_azimuth = 284.901°` is clockwise from **true north**. Both products are in the Moon
   south-polar stereographic projection, where north at longitude L is rotated clockwise from
   image-up by L. The crop centre is at 44.73 °E, so the renderer gets 284.901 + 44.726 =
   **329.627°**. `ops/solar_geometry.py::image_frame_azimuth()` does this and its docstring derives
   it. The scripts write both numbers into `PROVENANCE.md`.
2. **Both pairs were regenerated** (`data/pairs/pair_03_tierD`, `data/pairs/pair_04_tierD_native`)
   with the corrected renderer (see Samrudh's brief for the reflection bug). The optical crops are
   unchanged; only the hillshades changed. The files are gitignored — the PROVENANCE.md files are
   the reproducible record. Re-run the two commands in their docstrings if you need to rebuild.
3. **The Tier D "ground truth" moved by convention, not by content.** The FFT cross-correlation
   peak that defines the reference alignment is now reported as `(+9, −23)` px = reference minus
   source (`core.reliability.xcorr_peak`, sign pinned by a test). The Day-5 rows said `(−9, +23)`
   with the opposite sign. Same alignment. The new rows say which convention they use.

## The evidence you own

- The azimuth derivation was **checked, not fitted**: a 5° sweep of the renderer against the real
  photograph peaks at 325° (NCC +0.642); the derived value 329.6° gives +0.639. The whole-frame
  FFT peak reaches NCC +0.75 (it was +0.71 on the reflected render, −0.57 at the naive azimuth).
- The pair is **not** related by one translation: the top two quadrants say (+8, −23) px and the
  bottom two say (0, 0). The two products disagree by ~23 px = 216 m across the frame. That is
  reported as the uncertainty of the fallback alignment; it is not smoothed over.

## What this pair now proves — say it exactly this way

On optical ↔ elevation our feature matcher produced 87 correspondences, RANSAC found a consensus
homography, and **0 of 87 were correct within 10 px** (row `pair_04_tierD_native`,
`ours_loftr`, 3 Sep evening). The trust layer's cell vote (0% of 35 measurable cells agree)
contradicted that homography; the system fell back to global correlation and registered the pair
by (+9, −23) px = 231 m with a quadrant disagreement of up to 216 m (row
`fft_phase_correlation (fallback)`). **It does not prove multi-modal registration works. It proves
the system knows when it does not.**

## The five questions you must answer cold

1. **"Where did the data come from?"** — Kaguya TC tile `TC1S2B0_01_03482S746E0433` (CC0, AWS
   astrogeo-ard, Cloud-Optimized GeoTIFF); LOLA `ldem_60s_60m` from PDS Geosciences; Chandrayaan-2
   OHRC from the public archive.org mirror. None needed an account.
2. **"Is Kaguya ↔ LOLA cross-sensor?"** — It is *multi-modal*: a photograph against an elevation
   model. "Cross-sensor" means two cameras; we have no such pair and we say so.
3. **"Why 329.6° and not the label's 284.9°?"** — Meridian convergence of the polar stereographic
   projection at 44.7 °E. Derived from the map definition; the correlation sweep only confirms it.
4. **"Why is the reference offset by 200 m from the photograph?"** — Uncontrolled Kaguya
   georeferencing versus the LOLA frame; Wagner et al. 2024 report uncontrolled NAC offsets of tens
   of metres to ~100 m at the pole, so a ~200 m Kaguya offset is unsurprising. Which is "right"
   is not ours to say; we report the disagreement.
5. **"Tier A — cut or abandoned?"** — Abandoned for 9 Sep. State it. The public MiLOI dataset (321
   multi-illumination LROC NAC pairs with ground truth, github.com/Bin501/CNSFM) is the route if
   we go to nationals.

## Never say

"Cross-sensor" for anything in this repo; "37.8 px" or "10.9 px" as Tier D accuracies (they were
fit residuals on wrong matches, against a reflected render); "the sun angle was tuned".
