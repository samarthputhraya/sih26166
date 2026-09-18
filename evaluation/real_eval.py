"""Scoring a REAL pair, where no exact ground truth exists.

`evaluate()` (metrics.py) gives the five metrics plus robust held-out residuals. What
a real pair adds, and what lives here:

  consistency_vs_prior  how far the registration moved the source from where the two
                        archives' own geometry put it - the archives' disagreement,
                        in reference pixels and metres. Not an error of ours.
  map_transform         a registration H (source px -> reference px) expressed as a
                        map -> map transform, using each window's exact geotransform.
  loop_closure          compose A->B->C->A over the same ground; with no ground truth
                        this is the accuracy evidence: a chain of wrong registrations
                        does not close.

`real_pairs_log.csv` is the append-only companion to results_log.csv for the fields
its 15-column schema cannot hold (sun geometry, window location, archive offset,
robust residuals, loop residuals). Every row names the results_log row it belongs to.
"""
from __future__ import annotations

import csv
import datetime as _dt
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
REAL_LOG = ROOT / "evaluation" / "real_pairs_log.csv"
REAL_FIELDS = [
    "timestamp", "pair_id", "tier", "kind", "method_declared", "source_product", "reference_product",
    "window_lat", "window_lon", "src_gsd_m", "ref_gsd_m", "scale_ratio",
    "d_sun_azimuth_deg", "d_incidence_deg",
    "n_matches", "inliers", "inlier_ratio", "grid_coverage_fraction",
    "residual_median_px", "holdout_inlier_rmse_px", "holdout_inlier_frac",
    "verified", "weak", "no_evidence", "verdict",
    "archive_offset_px", "archive_offset_m",
    "loop_id", "loop_rms_px", "loop_p90_px", "loop_rms_m",
    "seconds", "git_commit", "command", "notes",
    # added 18 Sep 2026 for the real sun-angle sweep (older rows leave them empty)
    "matcher_offset_m", "outcome",
]


def _pts_grid(shape, n=20, margin=0.0):
    h, w = shape[:2]
    gx, gy = np.meshgrid(np.linspace(margin, w - 1 - margin, n), np.linspace(margin, h - 1 - margin, n))
    return np.c_[gx.ravel(), gy.ravel()]


def _apply(H, pts):
    p = np.c_[pts, np.ones(len(pts))] @ np.asarray(H, np.float64).T
    return p[:, :2] / p[:, 2:3]


def consistency_vs_prior(H, prior_H, ref_shape, gsd_m=None) -> dict:
    """Displacement between where H and the archive prior put the same source points,
    measured on a 20x20 grid over the reference frame (in reference pixels)."""
    if H is None:
        return {"median_px": None, "p90_px": None, "mean_vec_px": None, "median_m": None}
    ref_pts = _pts_grid(ref_shape)
    src_pts = _apply(np.linalg.inv(np.asarray(prior_H, np.float64)), ref_pts)
    d = _apply(H, src_pts) - ref_pts
    r = np.hypot(*d.T)
    out = {"median_px": float(np.median(r)), "p90_px": float(np.percentile(r, 90)),
           "mean_vec_px": [float(v) for v in d.mean(0)]}
    out["median_m"] = None if gsd_m is None else out["median_px"] * float(gsd_m)
    return out


def pixel_to_map(transform) -> np.ndarray:
    """3x3 matrix taking OpenCV pixel coordinates (centre of pixel 0 at 0) to map metres."""
    x0, sx, rx, y0, ry, sy = transform
    return np.array([[sx, rx, x0 + 0.5 * (sx + rx)],
                     [ry, sy, y0 + 0.5 * (ry + sy)],
                     [0.0, 0.0, 1.0]])


def map_transform(H, src_transform, ref_transform) -> np.ndarray:
    """H (source px -> reference px) as map metres -> map metres."""
    Ps, Pr = pixel_to_map(src_transform), pixel_to_map(ref_transform)
    return Pr @ np.asarray(H, np.float64) @ np.linalg.inv(Ps)


def loop_closure(T_chain: list, T_direct, pts_map, gsd_m) -> dict:
    """Compose the chain of map transforms and compare with the direct one.

    T_chain: [T_AB, T_BC] (applied in order) and T_direct: T_AC, all map -> map.
    Residual = |T_chain(p) - T_direct(p)| over pts_map, in metres and in pixels of gsd_m.
    """
    p = np.asarray(pts_map, np.float64)
    q = p
    for T in T_chain:
        q = _apply(T, q)
    d = _apply(T_direct, p)
    r = np.hypot(*(q - d).T)
    return {"rms_m": float(np.sqrt(np.mean(r ** 2))), "p90_m": float(np.percentile(r, 90)),
            "max_m": float(r.max()), "rms_px": float(np.sqrt(np.mean(r ** 2)) / gsd_m),
            "p90_px": float(np.percentile(r, 90) / gsd_m), "n_points": int(len(r)),
            "gsd_m": float(gsd_m)}


def log_real(row: dict) -> None:
    """Append one row to real_pairs_log.csv. Append-only; the header is written once."""
    new = not REAL_LOG.exists() or REAL_LOG.stat().st_size == 0
    if not new:
        with open(REAL_LOG, "rb") as f:
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                raise RuntimeError(f"{REAL_LOG} does not end in a newline; refusing to append")
    row = dict(row)
    row.setdefault("timestamp", _dt.datetime.now().isoformat(timespec="seconds"))
    unknown = set(row) - set(REAL_FIELDS)
    if unknown:
        raise ValueError(f"unknown real_pairs_log fields: {sorted(unknown)}")
    with open(REAL_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REAL_FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in REAL_FIELDS})
