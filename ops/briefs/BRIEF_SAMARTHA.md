# Brief for Samartha — `core/` and `app/` — what was built on 3 Sep, for the record

**This is the owner's own brief, so the build is explainable by someone other than the AI session
that wrote it.** Everything below is in the working tree; the commit message carries the summary.

## Built

- `core/reliability.py` — `reliability_map()`: per 8×8 cell of the reference frame, `verified` /
  `weak` / `no_evidence`. Verified needs ≥3 inliers, local inlier ratio ≥0.5, and an independent
  area check: FFT cross-correlation of the warped source against the reference in that cell (on
  gradient-orientation *or* intensity pixels, whichever peaks stronger) with peak shift ≤2 px and
  NCC ≥0.3. The whole-frame verdict is a **vote of measurable cells**: ≥50% agree → agrees; <25% →
  contradicted; between → unconfirmed. Cells narrower than 24 px cannot vote; then the whole-frame
  peak decides and the basis is stated. Nothing is verified in a contradicted frame.
  `gate()` labels change candidates. `xcorr_peak()` sign is pinned by a test.
- `core/pipeline.py` — `run_all()` now also returns `reliability`, `declared` (method, why),
  `fallback` (global-correlation translation + quadrant spread, only when contradicted or when the
  matcher gave no transform), `H_final` / `warped_final`, raw matches. The matcher's own `H`,
  `warped` and the five metrics are untouched. `--log` writes a second row for the fallback.
- `core/reliability_calibrate.py` — the kill test (M1): per-cell true error by state over the
  sweep; `core/reliability_calibration.csv` + summary; one pooled row in the log.
- `app/streamlit_app.py` — "Where the alignment can be trusted" section (tinted map, counts, the
  verdict), declared-method banner, fallback expander, gated change detection, and **precomputed
  results** (`ops/precompute_demo_cache.py` → `demo_cache/results/*.pkl`; the checkbox in the
  sidebar; the live path stays one click away).
- `ops/solar_geometry.py`, the two Tier D builders, `ops/tier_d_investigation.py`,
  `ops/gate_tier_d_changes.py`, `ops/subpixel_ab_real.py`, `ops/precompute_demo_cache.py`.
- Tests: `core/test_reliability.py` (11), `evaluation/test_shaded_relief.py` (6), interface lock
  extended. Suite: 206 passing, 10 s. Gate 1 prints `residual_px 0.03761504064805703` (refinement
  ON) and `0.19452325191421008` with `--no-subpixel`.

## Why the verdict is a cell vote and not one FFT

The first version used the whole-frame peak. On the calibration sweep it declared every 30° and 45°
pair contradicted (large-scale shading pulls the frame peak 10–17 px off while 85–93% of cells
still agree within 2 px) and the fallback it triggered was 10–40× *less* accurate than the
homography it replaced (rows from that run were discarded before logging the final set). Cells are
high-pass by construction and vote independently. That is a measured design decision, not a
preference — say it if asked "why cells".

## What "verified" means, exactly, from the pooled row (refinement ON, the shipped default)

Median true error 0.162 px (9.7 m), p90 0.435 px, 92% under 0.5 px, 98% under 1 px (20 pairs,
926 cells). At 0–15° it is 100% under 0.5 px; at 30° 96%; at 45° the median is 0.58 px and 79%
are under 1 px. Weak: 0.363 px median. No evidence: 0.766 px. "Verified" promises "under one
reference pixel in ~98% of calibrated cells, under half a pixel in ~92%"; at 45° of sun
difference it is a one-pixel promise, and the slide must not imply better. (The earlier pooled
row in the log, without `matcher arm` in its config, is the refinement-OFF arm: 0.208 px median.)

Gate 1 now prints `residual_px 0.03761504064805703` with the ON default;
`--no-subpixel` reproduces `0.19452325191421008` exactly — both were run tonight.

## Sub-pixel refinement: the story changed tonight

The Day-3 bench (per-match endpoint error) said refinement *hurt* LoFTR (0.336 → 0.431 px). The
pipeline's transform-level `rmse_gt_px` says it *helps*: real OHRC texture 0.156 → 0.024 px
(3.6 → 0.6 cm on the OHRC grid), hillshade render 0.143 → 0.055 px — while `residual_px` got
worse both times. Same data, different quantity: RANSAC averages thousands of matches, so a
transform can improve while individual matches get noisier. Across the sun sweep (medians of 5
shifts, rows `ours_loftr` vs `ours_loftr+subpixel`): 0° 0.120 → 0.086, 15° 0.249 → 0.086,
30° 0.571 → 0.314, 45° 1.655 → 1.096 px. **The 30° point moves from FAIL to PASS on Gate 2 C1.**
On that evidence the default was switched to ON at 21:05 on 3 Sep; `--no-subpixel` reproduces
the old rows. The Gate-1 pinned residual therefore changed (see STATUS.md for the new value).
The honest sentence: "we shipped it off on per-match evidence, re-measured on the transform-level
metric, and turned it on — both sets of rows are in the log; the divergence between fit residual
and true error is the point".

## Open, for tomorrow

Rerun `ops/precompute_demo_cache.py` after any change to `core/`; `redetect()` still unwired
(claim removed instead); Gate 2 criterion 5 (same-scale classical comparison) still unowned;
MiLOI as the real multi-illumination set; the SPOC date question.
