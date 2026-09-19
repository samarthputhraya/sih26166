"""Write the deliverables the problem statement names, for one registered pair.

SIH26166's Expected Solution asks for "Software and registered product with
corresponding match points" and "Evaluation metric". `run_all` computes all of it
and, until this module, wrote none of it to disk. One call now produces:

    registered_product.tif   the source warped onto the reference pixel grid.
                             GeoTIFF carrying the REFERENCE's georeferencing when
                             the reference has any; float32, NaN outside the
                             source footprint (GDAL_NODATA "nan"). 0 is a real DN
                             in polar imagery - deep shadow - so it cannot be nodata.
    registered_product.json  only when the reference has no map transform: says
                             the product is in reference PIXELS, and which product.
    matches.csv              every raw match: source xy, reference xy, whether
                             MAGSAC++ kept it, its residual under the matcher's H,
                             the trust state of the reference cell it lands in,
                             and the matcher's confidence.
    gcps.txt                 inliers as GDAL `-gcp pixel line X Y` (only when the
                             reference is georeferenced)
    gcps.points              the same inliers in QGIS Georeferencer format
    matches_isis.csv         inliers in ISIS's 1-based sample/line convention
    trust_map.csv            the 8x8 verified / weak / no_evidence map
    report.json, report.md   metrics, declared method, trust summary, timings,
                             input sha256, library versions, git commit

COORDINATE CONVENTIONS - the half pixel a sub-pixel claim lives on.
Inside this project a point (x, y) is OpenCV's: the CENTRE of the top-left pixel
is (0, 0). GDAL puts the top-left CORNER at (0, 0), so its pixel/line = x + 0.5,
y + 0.5. ISIS is 1-based with the top-left centre at (1, 1), so sample/line =
x + 1, y + 1. Each file states which convention it uses in its header.
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import importlib.metadata as _md
import json
import pathlib
import platform
import subprocess
import tempfile
from typing import Any

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent

# GeoTIFF tags copied verbatim from a GeoTIFF reference:
# ModelPixelScale, ModelTiepoint, ModelTransformation, GeoKeyDirectory,
# GeoDoubleParams, GeoAsciiParams, GDAL_METADATA. GDAL_NODATA is written fresh.
_GEO_TAGS = (33550, 33922, 34264, 34735, 34736, 34737, 42112)
_GDAL_NODATA = 42113

MATCH_FIELDS = ["src_x", "src_y", "ref_x", "ref_y", "is_inlier",
                "residual_px", "cell_state", "score"]


# --- the match table ---------------------------------------------------------

def match_table(result: dict) -> list[dict]:
    """One row per RAW match, in the order the matcher produced them.

    `is_inlier` is exact membership in MAGSAC++'s survivors (`src_inliers` are rows
    of `src_matches` selected by a boolean mask, so the coordinates are identical
    floats). `residual_px` is the reprojection error under the MATCHER's H in
    reference pixels - not under the fallback's, which is translation-only and
    was not fitted to these points.
    """
    src = np.asarray(result.get("src_matches") if result.get("src_matches") is not None
                     else np.zeros((0, 2)), dtype=np.float64).reshape(-1, 2)
    ref = np.asarray(result.get("ref_matches") if result.get("ref_matches") is not None
                     else np.zeros((0, 2)), dtype=np.float64).reshape(-1, 2)
    n = min(len(src), len(ref))
    src, ref = src[:n], ref[:n]

    inl = set()
    si, ri = result.get("src_inliers"), result.get("ref_inliers")
    if si is not None and ri is not None and len(si):
        for a, b in zip(np.asarray(si, np.float64).reshape(-1, 2),
                        np.asarray(ri, np.float64).reshape(-1, 2)):
            inl.add((float(a[0]), float(a[1]), float(b[0]), float(b[1])))

    H = result.get("H")
    resid = np.full(n, np.nan)
    if H is not None and n:
        p = np.hstack([src, np.ones((n, 1))]) @ np.asarray(H, np.float64).T
        with np.errstate(divide="ignore", invalid="ignore"):
            proj = p[:, :2] / p[:, 2:3]
        resid = np.hypot(*(proj - ref).T)

    rel = result.get("reliability")
    ref_shape = tuple(result.get("shape_reference") or ())[:2]
    scores = result.get("match_scores")
    scores = np.asarray(scores).ravel() if scores is not None and len(scores) == n else None

    state_at = None
    if rel is not None and len(ref_shape) == 2:
        from core.reliability import state_at
    rows = []
    for i in range(n):
        key = (float(src[i, 0]), float(src[i, 1]), float(ref[i, 0]), float(ref[i, 1]))
        rows.append({
            "src_x": src[i, 0], "src_y": src[i, 1],
            "ref_x": ref[i, 0], "ref_y": ref[i, 1],
            "is_inlier": int(key in inl),
            "residual_px": None if not np.isfinite(resid[i]) else float(resid[i]),
            "cell_state": state_at(rel, ref[i, 0], ref[i, 1], ref_shape) if state_at else "",
            "score": None if scores is None else float(scores[i]),
        })
    return rows


def _fmt(v, nd=4):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def write_matches_csv(path, rows: list[dict]) -> pathlib.Path:
    path = pathlib.Path(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("# coordinates: OpenCV pixel-centre convention, top-left pixel centre = (0,0); "
                "residual_px in REFERENCE pixels under the matcher's homography\n")
        w = csv.DictWriter(f, fieldnames=MATCH_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: _fmt(r[k]) for k in MATCH_FIELDS})
    return path


# --- georeferencing ----------------------------------------------------------

def _ref_geotags(ref_path) -> list[tuple] | None:
    """The reference's own GeoTIFF tags as tifffile `extratags`, or None."""
    p = pathlib.Path(ref_path)
    if p.suffix.lower() not in (".tif", ".tiff"):
        return None
    import tifffile
    try:
        with tifffile.TiffFile(str(p)) as tf:
            page = tf.pages[0]
            out = []
            for code in _GEO_TAGS:
                t = page.tags.get(code)
                if t is None:
                    continue
                val = t.value
                if isinstance(val, bytes):
                    val = val.decode("latin-1")
                out.append((code, int(t.dtype), t.count, val, True))
            return out or None
    except Exception:  # noqa: BLE001 - a reference we cannot re-read is "no geo"
        return None


def _tags_from_meta(meta: dict) -> list[tuple] | None:
    """Minimal GeoTIFF tags from a loader transform, for non-TIFF references."""
    t = meta.get("transform")
    if not t:
        return None
    x0, sx, _, y0, _, sy = t
    tags = [(33550, 12, 3, (float(sx), float(-sy), 0.0), True),
            (33922, 12, 6, (0.0, 0.0, 0.0, float(x0), float(y0), 0.0), True)]
    if meta.get("crs"):
        tags.append((34737, 2, 0, str(meta["crs"]) + "|", True))
    return tags


def write_registered_product(path, warped, ref_path, ref_meta, footprint=None) -> dict:
    """The source resampled onto the reference grid. Returns what was written.

    `footprint` (bool, reference shape) marks where the source actually landed; when
    None it is taken as every finite pixel. Outside it the product is NaN.
    """
    import tifffile
    path = pathlib.Path(path)
    img = np.asarray(warped, dtype=np.float32).copy()
    if footprint is not None:
        img[~np.asarray(footprint, bool)] = np.nan
    tags = _ref_geotags(ref_path) or _tags_from_meta(ref_meta or {})
    extratags = list(tags or []) + [(_GDAL_NODATA, 2, 0, "nan", True)]
    tifffile.imwrite(str(path), img, photometric="minisblack", extratags=extratags)
    info = {"path": str(path), "dtype": "float32", "nodata": "nan",
            "shape": list(img.shape), "georeferenced": bool(tags)}
    if not tags:
        side = path.with_suffix(".json")
        side.write_text(json.dumps({
            "frame": "reference image pixels (no map transform in the reference)",
            "reference": str(ref_path),
            "reference_product_id": (ref_meta or {}).get("product_id"),
            "transform": None, "crs": None,
            "convention": "row/column of the reference image; pixel centre of (0,0) is the "
                          "top-left pixel",
        }, indent=2), encoding="utf-8")
        info["sidecar"] = str(side)
    return info


def _map_xy(transform, x, y):
    """Map coordinates of the CENTRE of pixel (x, y) under a GDAL-order transform."""
    x0, sx, rx, y0, ry, sy = transform
    gx, gy = x + 0.5, y + 0.5              # GDAL: corner of the top-left pixel is (0,0)
    return x0 + gx * sx + gy * rx, y0 + gx * ry + gy * sy


def write_gcps(out_dir, rows, ref_meta) -> list[pathlib.Path]:
    """Inliers as ground control points. Only meaningful with a georeferenced reference."""
    out_dir = pathlib.Path(out_dir)
    t = (ref_meta or {}).get("transform")
    inl = [r for r in rows if r["is_inlier"]]
    if not t or not inl:
        return []
    crs = (ref_meta or {}).get("crs") or "unknown CRS"
    g = out_dir / "gcps.txt"
    with open(g, "w", encoding="utf-8") as f:
        f.write(f"# {len(inl)} GCPs for gdal_translate: -gcp <pixel> <line> <X> <Y>\n"
                f"# pixel/line are SOURCE coordinates in GDAL's convention (top-left corner "
                f"of the top-left pixel = 0,0; i.e. OpenCV x+0.5, y+0.5)\n"
                f"# X/Y are map coordinates of the matched reference pixel centre, CRS: {crs}\n")
        for r in inl:
            X, Y = _map_xy(t, r["ref_x"], r["ref_y"])
            f.write(f"-gcp {r['src_x'] + 0.5:.4f} {r['src_y'] + 0.5:.4f} {X:.4f} {Y:.4f}\n")
    q = out_dir / "gcps.points"
    with open(q, "w", encoding="utf-8") as f:
        # QGIS Georeferencer: source pixel Y is negative (image rows grow downward).
        f.write(f"#CRS: {crs}\nmapX,mapY,sourceX,sourceY,enable,dX,dY,residual\n")
        for r in inl:
            X, Y = _map_xy(t, r["ref_x"], r["ref_y"])
            f.write(f"{X:.4f},{Y:.4f},{r['src_x'] + 0.5:.4f},{-(r['src_y'] + 0.5):.4f},1,0,0,0\n")
    return [g, q]


def write_isis_csv(path, rows, src_id, ref_id) -> pathlib.Path:
    path = pathlib.Path(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("# ISIS convention: 1-based sample/line, centre of the top-left pixel = (1,1)\n")
        w = csv.writer(f)
        w.writerow(["point_id", "source_serial", "source_sample", "source_line",
                    "reference_serial", "reference_sample", "reference_line"])
        k = 0
        for r in rows:
            if not r["is_inlier"]:
                continue
            k += 1
            w.writerow([f"P{k:05d}", src_id, f"{r['src_x'] + 1:.4f}", f"{r['src_y'] + 1:.4f}",
                        ref_id, f"{r['ref_x'] + 1:.4f}", f"{r['ref_y'] + 1:.4f}"])
    return path


def write_trust_map(path, rel) -> pathlib.Path | None:
    if rel is None:
        return None
    path = pathlib.Path(path)
    st = np.asarray(rel["state"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("# reliability state per cell of the REFERENCE frame; row 0 = top\n")
        w = csv.writer(f)
        w.writerow(["row"] + [f"col{c}" for c in range(st.shape[1])])
        for r in range(st.shape[0]):
            w.writerow([r] + [str(s) for s in st[r]])
    return path


# --- the report --------------------------------------------------------------

def sha256_file(path, limit_bytes: int = 4 << 30) -> str | None:
    p = pathlib.Path(path)
    if not p.exists() or p.stat().st_size > limit_bytes:
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _versions() -> dict:
    out = {"python": platform.python_version(), "platform": platform.platform(),
           "cpu": platform.processor()}
    for pkg in ("numpy", "opencv-contrib-python", "torch", "kornia", "tifffile", "pillow",
                "scipy"):
        try:
            out[pkg] = _md.version(pkg)
        except _md.PackageNotFoundError:
            pass
    return out


# The append-only evidence logs. Appending a row is not a code change.
# Evidence the runs WRITE - append-only logs and regenerated outputs. A freeze regenerates
# the calibration CSVs and miloi_truth.json mid-run; counting them as code would stamp every
# later row "-dirty".
EVIDENCE_LOGS = ("evaluation/results_log.csv", "evaluation/real_pairs_log.csv",
                 "evaluation/trust_real_calibration.csv", "evaluation/miloi_log.csv",
                 "evaluation/miloi_truth.json", "core/reliability_calibration.csv",
                 "core/reliability_calibration_summary.csv")


def _commit(paths=("core", "evaluation"), root=ROOT) -> str:
    """Short HEAD sha, `-dirty` when anything under `paths` differs from it.

    EVIDENCE_LOGS are left out of the check. They live in evaluation/, so counting
    them meant the first `--log` row of a run stamped every later row `-dirty`
    (18 Sep: every sun-sweep row after `5a3c586`), and no logged number could ever
    name a clean commit - which is the whole point of the evidence freeze.
    """
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                                      text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:  # noqa: BLE001
        return "?"
    spec = [*paths, *(f":(exclude){p}" for p in EVIDENCE_LOGS)]
    try:
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--", *spec],
                                        cwd=root, text=True,
                                        stderr=subprocess.DEVNULL).strip()
    except Exception:  # noqa: BLE001
        return sha + "-unknown"
    return sha + ("-dirty" if dirty else "")


def _jsonable(o: Any):
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.floating,)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not np.isfinite(o):
        return None
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, pathlib.Path):
        return str(o)
    return o


def report(result: dict, pair_id: str, src_path, ref_path, rows=None,
           prior: dict | None = None) -> dict:
    rows = rows if rows is not None else match_table(result)
    rel = result.get("reliability")
    fb = result.get("fallback") or {}
    ms, mr = result.get("meta_source") or {}, result.get("meta_reference") or {}
    inputs = {}
    for role, p, m in (("source", src_path, ms), ("reference", ref_path, mr)):
        pp = pathlib.Path(p)
        inputs[role] = {"path": str(pp), "bytes": pp.stat().st_size if pp.exists() else None,
                        "sha256": sha256_file(pp), "product_id": m.get("product_id"),
                        "instrument": m.get("instrument"), "gsd_mpp": m.get("gsd_mpp"),
                        "shape": list(result.get(f"shape_{role}") or []),
                        "crs": m.get("crs"), "transform": m.get("transform")}
    inl = [r for r in rows if r["is_inlier"]]
    res_in = [r["residual_px"] for r in inl if r["residual_px"] is not None]
    rep = {
        "pair_id": pair_id,
        "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _commit(),
        "environment": _versions(),
        "inputs": inputs,
        "common_gsd_mpp": result.get("gsd_mpp"),
        "scale_note": result.get("scale_note"),
        "illumination": result.get("illumination"),
        "n_matches": result.get("n_matches"),
        "ransac": result.get("ransac"),
        "inliers_exported": len(inl),
        "inlier_residual_px": ({"median": float(np.median(res_in)),
                                "p90": float(np.percentile(res_in, 90)),
                                "max": float(np.max(res_in))} if res_in else None),
        "metrics": result.get("metrics"),
        "metrics_note": result.get("metrics_note"),
        "distribution": result.get("distribution"),
        "trust": None if rel is None else {
            "counts": rel.get("counts"), "n_cells": rel.get("n_cells"),
            "verdict": (rel.get("global") or {}).get("verdict"),
            "contradicted": (rel.get("global") or {}).get("contradicted"),
            "note": (rel.get("global") or {}).get("note"),
            "config": rel.get("config"),
        },
        "declared": result.get("declared"),
        "fallback": None if not fb.get("used") else {
            k: fb.get(k) for k in ("reason", "shift_px_common_grid", "gsd_mpp_common",
                                   "shift_m", "ncc", "spread_px", "spread_m", "note")},
        "H_matcher": result.get("H"),
        "H_final": result.get("H_final"),
        "prior": prior,
        "seconds": result.get("seconds"),
    }
    return _jsonable(rep)


def _frac(v) -> str:
    return "n/a" if v is None else f"{100 * float(v):.1f} %"


def _grid(rep, role="reference"):
    i = rep["inputs"][role]
    g = i.get("gsd_mpp")
    name = pathlib.Path(i["path"]).name
    return name, g


def render_markdown(rep: dict) -> str:
    ref_name, ref_g = _grid(rep, "reference")
    src_name, src_g = _grid(rep, "source")
    m = rep.get("metrics") or {}
    d = rep.get("declared") or {}
    t = rep.get("trust") or {}

    def px(v, g=ref_g):
        if v is None:
            return "n/a"
        s = f"{v:.4f} px on the reference grid ({ref_name})"
        return s + (f" = {v * g:.3f} m at {g:.4g} m/px" if g else " (reference has no map scale)")

    pr = rep.get("prior") or {}
    L = [f"# Registration report - {rep['pair_id']}", "",
         f"Created {rep['created_utc']} from commit `{rep['git_commit']}`.", ""]
    if pr.get("tier"):
        L += [f"Tier: **{pr['tier']}**. {pr.get('terminology') or ''}".rstrip(), ""]
    L += ["## Inputs", "",
          "| role | file | instrument | GSD m/px | shape | sha256 |", "|---|---|---|---|---|---|"]
    for role in ("source", "reference"):
        i = rep["inputs"][role]
        inst = i.get("instrument") or (pr.get(role) or {}).get("instrument") or "-"
        L.append(f"| {role} | `{pathlib.Path(i['path']).name}` | {inst} | "
                 f"{i.get('gsd_mpp') or '-'} | {i.get('shape')} | `{(i.get('sha256') or '-')[:16]}` |")
    L += ["", "## What the system declared", "",
          f"- Method used: **{d.get('method')}**",
          f"- Why: {d.get('why')}",
          f"- Area check contradicted the matcher: {d.get('contradicted')}", "",
          "## Metrics (`evaluation/metrics.py`, raw matches)", "",
          f"- matches from the matcher: {rep.get('n_matches')}",
          f"- inlier_count: {m.get('inlier_count', 'n/a')}; inlier_ratio: {m.get('inlier_ratio', 'n/a')}"]
    # The same headline as the app's readout: on a real pair with outliers the RMSE over
    # every held-out match measures the outliers (Known issue 1), so the median leads.
    if m.get("residual_median_px") is not None:
        L += [f"- **held-out median residual** (residual_median_px; the 20 % of matches the fit "
              f"never saw): {px(m.get('residual_median_px'))}",
              f"- held-out RMSE of the matches within 3 px of the fit on the reference grid "
              f"(holdout_inlier_rmse_px, capped at 3 px by that definition): "
              f"{px(m.get('holdout_inlier_rmse_px'))}; "
              f"{_frac(m.get('holdout_inlier_frac'))} of the held-out matches are within 3 px"]
    L += [f"- residual_px (RMSE over ALL held-out matches, outliers included - the synthetic "
          f"sweep's measure): {px(m.get('residual_px'))}",
          f"- rmse_gt_px (only with a known transform): {px(m.get('rmse_gt_px'))}",
          f"- grid_coverage_fraction (8x8): {m.get('grid_coverage_fraction', 'n/a')}; "
          f"distribution_cv: {m.get('distribution_cv', 'n/a')}", ""]
    ir = rep.get("inlier_residual_px")
    if ir:
        lead = "the held-out median" if m.get("residual_median_px") is not None else "`residual_px`"
        L += [f"Exported inliers: {rep['inliers_exported']}; their residual under the matcher's "
              f"homography is in-sample (fitted), median {px(ir['median'])}, p90 {px(ir['p90'])}. "
              f"Read {lead} above for accuracy, not this.", ""]
    if t:
        c = t.get("counts") or {}
        L += ["## Where it can be trusted", "",
              f"verified {c.get('verified', 0)} / weak {c.get('weak', 0)} / no evidence "
              f"{c.get('no_evidence', 0)} of {t.get('n_cells')} cells; whole-frame verdict: "
              f"**{t.get('verdict')}** - {t.get('note')}", ""]
    fb = rep.get("fallback")
    if fb:
        L += ["## Fallback", "", f"{fb.get('note')}; reason: {fb.get('reason')}; "
              f"shift {fb.get('shift_px_common_grid')} px on the common "
              f"{fb.get('gsd_mpp_common')} m/px grid; quadrant disagreement "
              f"{fb.get('spread_px')} px ({fb.get('spread_m')} m) - the uncertainty to quote.", ""]
    L += ["## Scale and illumination", "", f"- {rep.get('scale_note')}",
          f"- {rep.get('illumination')}", "",
          f"Source `{src_name}` at {src_g or '?'} m/px; reference `{ref_name}` at {ref_g or '?'} m/px.",
          "", "## Environment", ""]
    L += [f"- {k}: {v}" for k, v in (rep.get("environment") or {}).items()]
    L += ["", f"Elapsed {rep.get('seconds') or 0:.1f} s, CPU only.", ""]
    return "\n".join(L)


def write_report(out_dir, rep: dict) -> list[pathlib.Path]:
    out_dir = pathlib.Path(out_dir)
    j = out_dir / "report.json"
    j.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    md = out_dir / "report.md"
    md.write_text(render_markdown(rep), encoding="utf-8")
    return [j, md]


# --- orchestration -------------------------------------------------------------

def _footprint(result) -> np.ndarray | None:
    """Where the source lands on the reference grid under the DECLARED transform."""
    H = result.get("H_final")
    shp = result.get("shape_source")
    rshp = result.get("shape_reference")
    if H is None or shp is None or rshp is None:
        return None
    import cv2
    ones = np.ones(tuple(shp)[:2], np.float32)
    fp = cv2.warpPerspective(ones, np.asarray(H, np.float64), (int(rshp[1]), int(rshp[0])),
                             flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT,
                             borderValue=0)
    return fp > 0.5


def export_bundle(result: dict, out_dir, pair_id: str, src_path=None, ref_path=None,
                  prior: dict | None = None) -> dict[str, pathlib.Path]:
    """Write every deliverable for one pair into `out_dir`. Never raises on a failed pair:
    a pair with no transform still gets its matches and a report that says why."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    src_path = src_path or result.get("source")
    ref_path = ref_path or result.get("reference")
    ms, mr = result.get("meta_source") or {}, result.get("meta_reference") or {}
    rows = match_table(result)
    written: dict[str, pathlib.Path] = {"matches.csv": write_matches_csv(out_dir / "matches.csv", rows)}

    warped = result.get("warped_final")
    if warped is not None:
        info = write_registered_product(out_dir / "registered_product.tif", warped, ref_path, mr,
                                        footprint=_footprint(result))
        written["registered_product.tif"] = pathlib.Path(info["path"])
        if info.get("sidecar"):
            written["registered_product.json"] = pathlib.Path(info["sidecar"])
    for p in write_gcps(out_dir, rows, mr):
        written[p.name] = p
    src_id = ms.get("product_id") or pathlib.Path(str(src_path)).stem
    ref_id = mr.get("product_id") or pathlib.Path(str(ref_path)).stem
    written["matches_isis.csv"] = write_isis_csv(out_dir / "matches_isis.csv", rows, src_id, ref_id)
    tm = write_trust_map(out_dir / "trust_map.csv", result.get("reliability"))
    if tm:
        written["trust_map.csv"] = tm
    rep = report(result, pair_id, src_path, ref_path, rows=rows, prior=prior)
    rep["files"] = sorted(written)
    for p in write_report(out_dir, rep):
        written[p.name] = p
    return written


def bundle_bytes(result: dict, pair_id: str, src_path=None, ref_path=None,
                 prior: dict | None = None) -> dict[str, bytes]:
    """The same files, as bytes, for a download button. Written to a temp dir and read back
    so the app offers exactly what the CLI writes."""
    with tempfile.TemporaryDirectory() as td:
        files = export_bundle(result, td, pair_id, src_path, ref_path, prior)
        return {name: pathlib.Path(p).read_bytes() for name, p in files.items()}
