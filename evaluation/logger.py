import csv
from datetime import datetime, timezone
from pathlib import Path

RESULTS_LOG = Path(__file__).resolve().parent / "results_log.csv"

FIELDS = ["timestamp", "pair_id", "tier", "method", "config", "rmse_gt_px",
          "residual_px", "inlier_count", "inlier_ratio", "grid_coverage_fraction",
          "distribution_cv", "n_matches", "gsd_mpp", "status", "notes"]

def log_result(pair_id, tier, method, metrics, config=None, gsd_mpp=None, notes=""):
    """Append one run to results_log.csv. The ONLY way anything gets written there."""
    if not tier:
        raise ValueError("tier is mandatory - a number without its tier is meaningless")
    row = {f: None for f in FIELDS}
    row.update(metrics or {})
    row.update(timestamp=datetime.now(timezone.utc).isoformat(), pair_id=pair_id,
               tier=tier, method=method, config=config, gsd_mpp=gsd_mpp, notes=notes)
    new = not RESULTS_LOG.exists() or RESULTS_LOG.stat().st_size == 0
    with open(RESULTS_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)