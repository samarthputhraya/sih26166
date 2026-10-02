"""Independent check points: matching features a person clicked in a pair's two images, and how
far a registration lands from them.

Every other accuracy figure in this project comes from the matcher's own matches (held-out medians,
loops). These do not: the clicks are made with `ops/click_check_points.py`, which shows the source
around the ARCHIVE prior position (`geometry_prior.json`) and never reads a registration, so a
check point knows nothing about the transform it is used to judge. That is the standard
photogrammetric independent check point (ICP), and its RMSE is the "RMSE" the problem statement
names, measured against truth the matcher never saw.

One CSV per pair, `evaluation/check_points/<pair_id>.csv`:

    point_id, src_x, src_y, ref_x, ref_y, repeat_of, confidence, feature, clicker, utc,
    src_sha12, ref_sha12

Coordinates are each image's own pixels with pixel centres at integers (numpy / OpenCV / imshow).
A row whose `repeat_of` names an earlier point is a second click of the same feature, made later
without the first click shown: it measures how precisely a feature can be clicked, and it is never
a check point itself. `src_sha12` / `ref_sha12` are the first 12 hex digits of the sha256 of the
two pair files the clicks were made on; a pair whose files have changed since is refused.

    python -m evaluation.check_points                 # every pair with clicks, against its bundle
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
CP_DIR = ROOT / "evaluation" / "check_points"
PAIRS = ROOT / "data" / "pairs"
REAL_LOG = ROOT / "evaluation" / "real_pairs_log.csv"
FIELDS = ("point_id", "src_x", "src_y", "ref_x", "ref_y", "repeat_of", "confidence", "feature",
          "clicker", "utc", "src_sha12", "ref_sha12")
MIN_POINTS = 6          # fewer than this and an RMSE describes the points, not the registration


def sha12(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()[:12]


def pair_paths(pair_id: str, pairs: pathlib.Path = PAIRS) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    d = pairs / pair_id
    return d / f"{pair_id}_source.tif", d / f"{pair_id}_ref.tif", d / "geometry_prior.json"


def read_csv(path: pathlib.Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load(pair_id: str, cp_dir: pathlib.Path = CP_DIR, pairs: pathlib.Path = PAIRS,
         check_files: bool = True) -> dict:
    """{'icp': rows that are check points, 'repeats': second clicks}. Refuses clicks made on other
    files than the pair holds now (the sha12 columns), when the pair files are present."""
    rows = read_csv(cp_dir / f"{pair_id}.csv")
    if check_files:
        src, ref, _ = pair_paths(pair_id, pairs)
        if src.exists() and ref.exists():
            have = {sha12(src), sha12(ref)}
            for r in rows:
                if {r["src_sha12"], r["ref_sha12"]} != have:
                    raise ValueError(f"{pair_id}: point {r['point_id']} was clicked on other files "
                                     f"({r['src_sha12']}/{r['ref_sha12']}) than the pair holds now")
    return {"icp": [r for r in rows if not (r.get("repeat_of") or "").strip()],
            "repeats": [r for r in rows if (r.get("repeat_of") or "").strip()]}


def xy(rows: list[dict], which: str) -> np.ndarray:
    return np.array([[float(r[f"{which}_x"]), float(r[f"{which}_y"])] for r in rows], np.float64).reshape(-1, 2)


def apply_h(H, pts: np.ndarray) -> np.ndarray:
    p = np.c_[pts, np.ones(len(pts))] @ np.asarray(H, np.float64).T
    return p[:, :2] / p[:, 2:3]


def score(H, src_xy: np.ndarray, ref_xy: np.ndarray, ref_gsd: float, src_gsd: float) -> dict:
    """Where H (source pixels -> reference pixels) puts each clicked source point, against where the
    person clicked it in the reference. Errors in reference pixels, metres, and source pixels."""
    d = apply_h(H, src_xy) - ref_xy
    e = np.hypot(d[:, 0], d[:, 1])
    n = len(e)
    out = {"n": n,
           "rmse_px": float(np.sqrt(np.mean(e ** 2))) if n else math.nan,
           "rmse_x_px": float(np.sqrt(np.mean(d[:, 0] ** 2))) if n else math.nan,
           "rmse_y_px": float(np.sqrt(np.mean(d[:, 1] ** 2))) if n else math.nan,
           "median_px": float(np.median(e)) if n else math.nan,
           "max_px": float(np.max(e)) if n else math.nan}
    for k in ("rmse", "rmse_x", "rmse_y", "median", "max"):
        out[f"{k}_m"] = out[f"{k}_px"] * ref_gsd
        out[f"{k}_src_px"] = out[f"{k}_m"] / src_gsd
    return out


def fit_h(src_xy: np.ndarray, ref_xy: np.ndarray) -> np.ndarray:
    """Least-squares homography through all the given points (DLT on normalised coordinates)."""
    def norm(p):
        c = p.mean(axis=0)
        s = math.sqrt(2) / max(np.sqrt(((p - c) ** 2).sum(axis=1)).mean(), 1e-12)
        return np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1]])
    Ts, Tr = norm(src_xy), norm(ref_xy)
    a = apply_h(Ts, src_xy)
    b = apply_h(Tr, ref_xy)
    A = []
    for (x, y), (u, v) in zip(a, b):
        A.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        A.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    _, _, vt = np.linalg.svd(np.asarray(A))
    Hn = vt[-1].reshape(3, 3)
    H = np.linalg.inv(Tr) @ Hn @ Ts
    return H / H[2, 2]


def floor(src_xy: np.ndarray, ref_xy: np.ndarray, ref_gsd: float, src_gsd: float) -> dict:
    """Leave-one-out: each point against a homography fitted to all the others. What one plane
    through the clicks themselves misses - click error plus relief - so no single transform can be
    expected to do better than this on these points."""
    n = len(src_xy)
    if n < MIN_POINTS:
        return {"n": n}
    pred = []
    for i in range(n):
        keep = np.arange(n) != i
        pred.append(apply_h(fit_h(src_xy[keep], ref_xy[keep]), src_xy[i:i + 1])[0])
    d = np.asarray(pred) - ref_xy
    return score(np.eye(3), ref_xy + d, ref_xy, ref_gsd, src_gsd)


def precision(rows: list[dict], repeats: list[dict], ref_gsd: float, src_gsd: float) -> dict:
    """How precisely a feature is clicked: each repeat against its original, per image. The RMS of
    a difference of two equally noisy clicks is sqrt(2) times one click's noise."""
    by_id = {r["point_id"]: r for r in rows}
    pairs = [(by_id[r["repeat_of"]], r) for r in repeats if r["repeat_of"] in by_id]
    if not pairs:
        return {"n": 0}
    out = {"n": len(pairs)}
    for which, gsd in (("src", src_gsd), ("ref", ref_gsd)):
        d = xy([b for _a, b in pairs], which) - xy([a for a, _b in pairs], which)
        one = float(np.sqrt(np.mean((d ** 2).sum(axis=1)) / 2))
        out[f"{which}_click_px"] = one
        out[f"{which}_click_m"] = one * gsd
    return out


def gsds(pair_id: str, pairs: pathlib.Path = PAIRS) -> tuple[float, float]:
    """(reference, source) grid of the pair files, from geometry_prior.json."""
    g = json.loads(pair_paths(pair_id, pairs)[2].read_text(encoding="utf-8"))
    return float(g["reference"]["resampled_gsd_mpp"]), float(g["source"]["resampled_gsd_mpp"])


def prior_h(pair_id: str, pairs: pathlib.Path = PAIRS) -> np.ndarray:
    g = json.loads(pair_paths(pair_id, pairs)[2].read_text(encoding="utf-8"))
    return np.asarray(g["prior_H_source_to_reference"], np.float64)


def latest_commit(pair_id: str, log: pathlib.Path = REAL_LOG) -> str | None:
    last = None
    for r in read_csv(log):
        if r["pair_id"] == pair_id and "INVALIDATED" not in (r.get("notes") or ""):
            last = r.get("git_commit")
    return last


def bundle(pair_id: str, out_root: pathlib.Path, log: pathlib.Path = REAL_LOG) -> dict:
    """Our registration of the pair as exported (report.json): H_final, the verdict, the commit -
    refused when it is not the bundle of the pair's latest logged row."""
    rep = json.loads((out_root / pair_id / "report.json").read_text(encoding="utf-8"))
    want = latest_commit(pair_id, log)
    if want and rep.get("git_commit") != want:
        raise ValueError(f"{pair_id}: bundle is from {rep.get('git_commit')}, the latest logged row "
                         f"from {want} - re-run the pair before scoring it")
    return {"H": np.asarray(rep["H_final"], np.float64), "commit": rep.get("git_commit"),
            "declared": rep.get("declared", {}),
            "contradicted": bool(rep.get("declared", {}).get("contradicted"))}


def score_pair(pair_id: str, out_root: pathlib.Path, cp_dir: pathlib.Path = CP_DIR,
               pairs: pathlib.Path = PAIRS, log: pathlib.Path = REAL_LOG, extra: dict | None = None) -> dict:
    """Everything the report prints for one pair: ours, the archive prior, any `extra` transforms
    (name -> H, e.g. the classical matchers'), the leave-one-out floor, and click precision."""
    c = load(pair_id, cp_dir, pairs)
    ref_gsd, src_gsd = gsds(pair_id, pairs)
    s, r = xy(c["icp"], "src"), xy(c["icp"], "ref")
    b = bundle(pair_id, out_root, log)
    out = {"pair_id": pair_id, "ref_gsd": ref_gsd, "src_gsd": src_gsd, "commit": b["commit"],
           "declared": b["declared"].get("method"), "contradicted": b["contradicted"],
           "ours": score(b["H"], s, r, ref_gsd, src_gsd),
           "archive_prior": score(prior_h(pair_id, pairs), s, r, ref_gsd, src_gsd),
           "floor": floor(s, r, ref_gsd, src_gsd),
           "precision": precision(c["icp"], c["repeats"], ref_gsd, src_gsd),
           "clickers": sorted({x["clicker"] for x in c["icp"]})}
    for name, H in (extra or {}).items():
        out[name] = score(H, s, r, ref_gsd, src_gsd)
    return out


def clicked_pairs(cp_dir: pathlib.Path = CP_DIR) -> list[str]:
    return sorted(p.stem for p in cp_dir.glob("*.csv"))


def main(argv=None) -> int:
    out_root = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip()) / "out"
    for pid in clicked_pairs():
        try:
            s = score_pair(pid, out_root)
        except (ValueError, FileNotFoundError, KeyError) as e:
            print(f"{pid}: not scored - {e}")
            continue
        o, a, fl, pr = s["ours"], s["archive_prior"], s["floor"], s["precision"]
        print(f"{pid}: {o['n']} check points; ours RMSE {o['rmse_px']:.2f} px = {o['rmse_m']:.2f} m "
              f"({o['rmse_src_px']:.1f} source px), median {o['median_m']:.2f} m, max {o['max_m']:.2f} m; "
              f"archive prior {a['rmse_m']:.1f} m; floor {fl.get('rmse_m', math.nan):.2f} m; "
              f"click precision {pr.get('ref_click_m', math.nan):.2f} m on the reference ({pr['n']} repeats)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
