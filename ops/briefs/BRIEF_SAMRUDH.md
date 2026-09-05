# Brief for Samrudh — `evaluation/` — what changed on 3 Sep and what you must be able to explain

**Read time: 10 minutes. Gate 5 (8 Sep) asks you to explain your own module cold. Two of your files
were edited under the build-alone decision; you did not write the fix, so you must be able to
re-derive it.**

## What changed in your folder

1. **`evaluation/shaded_relief.py` — the sun was reflected.** `np.gradient(dem)` returns the
   gradients in AXIS order, `(d/drow, d/dcol)`. The old code unpacked them as `dzdx, dzdy`, so the
   two were swapped and the aspect was built from the wrong pair. Effect: a sun requested at
   azimuth `a` lit the terrain as if from `90 - a` (a reflection about the image diagonal — not the
   "az + 180" the Day-5 note said). Fixed to the standard Horn/GDAL formula:
   `slope = atan(hypot(dz/dcol, dz/drow))`, `aspect = atan2(dz/drow, -dz/dcol)`,
   `az = 360 - azimuth + 90`. Azimuth is clockwise from **image-up**.
2. **`evaluation/test_shaded_relief.py` — new, 6 tests.** A round hill lit from the top must be
   bright on its top flank; a crater lit from the top must be bright on its **bottom** wall; a
   diagonal sun lights the diagonal flank; flat ground at 30° elevation is exactly 0.5. Run
   `pytest evaluation/test_shaded_relief.py`. **Derive the crater case yourself** — it is the one a
   judge will ask.
3. **`evaluation/test_metrics.py` — test contamination fixed.** The last test called
   `log_result` without redirecting `RESULTS_LOG`, so every `pytest` run appended a junk row to the
   real evidence file (hit and reverted four times on Day 5). Now `monkeypatch.setattr(logger,
   "RESULTS_LOG", tmp_path / ...)` like every other test in the repo.
4. **`evaluation/README.md`** — the `shaded_relief.py` line no longer says "accurate shadows". There
   are no cast shadows. It is a local cosine law.
5. **`evaluation/results_log.csv` — 32 new rows tonight**, all through `core.pipeline`'s logger:
   20 sun-sweep rows with the corrected renderer and reliability notes, 1 pooled calibration row,
   2 + 2 Tier D rows (matcher + fallback, both pairs), 3 Tier D true-error rows, 2 + 2 sub-pixel
   A/B rows, 20 refinement-ON sweep rows, and the change-detection gate rows. Nothing was edited or
   deleted. Your Day-5 rows are still there; the new synthetic rows carry
   "hillshade convention fixed 3 Sep 2026" in their notes so nobody mixes the two sets.

## What did NOT change

- `metrics.py`, `synthetic_data.py`, `logger.py`: untouched. Your five metrics are still the only
  source of numbers. The trust layer (`core/reliability.py`) reads them; it does not redefine them.
- The synthetic sweep headline moved only slightly with the renderer fix (both renders of a pair
  are lit the same way, so the sun *difference* is preserved). New medians are in the log under the
  `ours_loftr` rows dated 3 Sep evening; quote those, not the Day-5 ones.

## The five questions you must answer cold

1. **"Why does your synthetic ground truth count as ground truth?"** — Both images are rendered from
   one DEM on one grid, so the pixel correspondence is exact by construction; the source is then
   warped by a known homography `H_true`. `rmse_gt_px` is the RMS distance between where our
   transform sends a dense grid of points and where `H_true` sends them. No real pair can give
   this, which is why real pairs report `residual_px` instead.
2. **"Do your shadows move?"** — No. The renderer is a local cosine law with no occlusion term.
   Changing the sun azimuth rotates the *shading*; a spire that should throw a long shadow throws
   none. It is an illumination test, not a shadow test, and elevation is held fixed at 30° for
   that reason. Say this before being asked.
3. **"What was wrong with the renderer and how do you know it is right now?"** — The axis-order
   swap above. Proof: the hill/crater tests, and on the real Kaguya ↔ LOLA pair the render now
   correlates with the photograph at NCC +0.64 at zero offset (it was −0.57).
4. **"What is the difference between `residual_px` and `rmse_gt_px`?"** — Fit residual on held-out
   matches versus true error against a known transform. They can move in opposite directions:
   on real OHRC texture with a known half-pixel shift, NCC refinement made `residual_px` worse
   (0.457 → 0.524) and `rmse_gt_px` better (0.156 → 0.024) — rows `ohrc_fracshift_x+0.50_y+0.50`.
5. **"What is the calibration row?"** — quote `reliability_calibration_envelope`, the claimed
   envelope (sun azimuth difference ≤ 30°): cells the trust layer marks *verified* have median
   true error **0.123 px (7.4 m at 60 m/px), 99.0% under 0.5 px, 100% under 1 px, n=817**;
   *weak* 0.229 px; *no evidence* 0.390 px. The `reliability_calibration_pooled` rows are the
   wider populations — 0.147 px over all eight deltas, and the Day-5 0.162 px over four — and
   they average in 45–180°, which is outside what we claim. Derivation:
   `core/reliability_calibration.csv` (one row per cell); note that the calibrate script opens
   it `"w"`, so always run the full delta list.

## Never say

"Accurate shadows", "the render is lit from az+180" (it was a reflection, and the remaining
offset was the map projection's meridian convergence — `ops/solar_geometry.py`), any Tier D
`residual_px` as an accuracy.
