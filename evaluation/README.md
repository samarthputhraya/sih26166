# Evaluation Module — SIH26166

This module calculates all metrics for the lunar image registration pipeline. It acts as the single source of truth for the project's performance. All results must be logged to `results_log.csv` before being quoted in the presentation or UI.

## Core Files
* `shaded_relief.py`: Hillshades a DEM from a stated sun azimuth (clockwise from image-up) and elevation. A local cosine law — **no cast shadows**; azimuth sweeps are an illumination test, not a shadow test. The axis-order bug that reflected the sun until 3 Sep 2026 is pinned by `test_shaded_relief.py` (a sun from the top must light a hill's top flank). A label's true-north azimuth needs the meridian correction in `ops/solar_geometry.py` before it goes in here.
* `synthetic_data.py`: Generates evaluation pairs with exact ground-truth homographies and scales up to 20x.
* `metrics.py`: The evaluation engine. Calculates fit, accuracy, and spatial distribution.
* `test_metrics.py`: Anti-regression tests for the evaluation logic.
* `results_log.csv`: The canonical record of all runs.

## Running Tests
Execute the test suite from the repository root:
`pytest evaluation/test_metrics.py -v`

## CRITICAL: Understanding the Error Metrics
Never conflate the two error numbers. A judge will probe this distinction.

* **`rmse_gt_px` (Accuracy):** The distance from the true transform, measured on a dense grid of check points. This is only available on Synthetic and Tier D (DEM) pairs where the true mapping is known.
* **`residual_px` (Fit Residual):** The RMSE measured on a 20% held-out set of RANSAC matches. On real lunar pairs, there is no ground truth, so this serves as a lower bound on error. It measures how well the model generalizes to points it was not fitted to. It is a residual, NOT an absolute accuracy.