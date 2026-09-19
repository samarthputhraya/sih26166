"""MiLOI: real LROC NAC images of the same ground under many suns, with a measured truth.

    python -m evaluation.miloi --convert        # the three xlsx sheets -> miloi_illumination.csv
    python -m evaluation.miloi --run            # match every pair (ours + SIFT/ORB/AKAZE); resumes
    python -m evaluation.miloi --retrust        # re-judge ours' stored matches after a trust-layer change
    python -m evaluation.miloi --truth          # per-image corrections -> miloi_truth.json
    python -m evaluation.miloi --score --log    # every method vs that truth -> the two logs
    python -m evaluation.miloi --table          # success rate vs sun difference, from the log

WHAT IT IS. MiLOI (Xie et al. 2025) ships inside github.com/Bin501/CNSFM, pinned at commit
94cebaa (sha256 of every file in <data>/download_manifest_done.csv, group `miloi`; the repo
has no licence file, so it is used for evaluation only and cited). 42 LROC NAC images, each
cropped to the same ~1 km x 1 km of ground and map-projected at its own native resolution,
in three scenes. Scene centres are computed from the GeoTIFF keys, not typed from the paper:
    S1   44.12 N, 340.49 E   Mercator            10 images
    S2    0.67 N,  23.47 E   Mercator            10 images   (the Apollo 11 landing site)
    S3  ~88.8 S,  123.8 E    polar stereographic 22 images   (sun near the horizon, every azimuth)
Every pair inside a scene is LROC NAC <-> LROC NAC: SAME SENSOR, cross-illumination - Tier A,
never "cross-sensor" (Invariant 2).

THE MAP IS NOT THE TRUTH (measured 18 Sep). The tiles share one projection per scene, so the
two geotransforms give a nominal source->reference transform. It is wrong by 4-253 m: on the
easiest pairs (sun 3.6-16 deg apart) LoFTR and SIFT agree with EACH OTHER to ~0.3 px with
hundreds to thousands of inliers, and both sit 17-210 px from the map. The residual after
removing one translation is 0.15-1.0 m over the frame, so each image's error is a
translation: nominal SPICE pointing, not co-registration. Scoring against the map would call
every correct registration a failure.

THE TRUTH USED INSTEAD: a per-image translation network, solved per scene.
  edge     a pair where ours AND SIFT (independent detectors, descriptors and preprocessing)
           each have >= EDGE_MIN_INLIERS MAGSAC++ inliers and agree within AGREE_PX over the
           reference frame. Its map offset d_ij = t_i - t_j is the mean of the two methods'.
  solve    least squares for one translation t_i per image, mean fixed to 0 per connected
           component (the absolute position is unknowable and irrelevant to a pair).
  truth    H_ij = P_ref^-1 . shift(t_src - t_ref) . P_src (real_eval.pixel_to_map).
  no self-scoring: a pair that is itself an edge is scored against the network solved
           WITHOUT that edge (leave-one-out). If removing it disconnects the pair, the pair has
           no truth and is reported as such, not scored.
  uncertainty: every edge's leave-one-out prediction error is the truth's own error; it is
           in miloi_truth.json and must be quoted beside any success rate.

SUN. The sheet column `northAzimuth` is the sun's azimuth clockwise from north at the tile.
Verified, not assumed: for M102285549LE, LROC's product page gives the sub-solar point
(0.21, 263.38); `core.geometry.sun_direction` at the S1 tile centre (44.1214, -19.5117) then
gives incidence 80.636 / azimuth 261.097 deg against the sheet's 80.628 / 261.091. Three sun
differences are logged: azimuth, incidence, and the angle between the two sun vectors (the
one scalar that means the same thing at the equator and at the pole).

PAIRS AND METHODS. Every unordered pair in a scene; source = the finer image, reference =
the coarser, so metrics are on the coarser grid (as for OHRC -> NAC). The matcher takes a
reference of at most one 640-px tile, so the reference is its central 640 x 640 window and
the source the same ground plus MARGIN_M. SIFT/ORB/AKAZE get the SAME common-GSD resampling
ours does (`core.scale.to_common_gsd`) and the shared ratio test, and their raw matches are
mapped back to original pixels - scale is not the baselines' handicap, illumination is what
is compared. All four are scored by the one `evaluate(H_true=)` on their raw matches;
success = rmse_gt_px < SUCCESS_PX on the reference grid. For ours also:
    matcher_err_px   the matcher's H against truth
    declared_err_px  what the system declared (H, or the fallback) against truth
    outcome          the trust layer judged against truth: correct_accepted / false_alarm /
                     caught_failure / missed_failure / no_transform
Both errors use `core.reliability._true_error_grid`, the definition the fallback row uses.

FILES. `--run` writes raw matches and transforms to <data>/miloi_runs/ (outside git, ~KB-MB
per pair) so the truth and the scoring can be redone without re-matching. `--score --log`
appends one results_log.csv row per (pair, method) - Invariant 1 - and one row to the
append-only evaluation/miloi_log.csv with the same numbers in columns. Failed registrations
are rows too: a success rate without its failures is not one.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import itertools
import json
import math
import pathlib
import sys
import tempfile
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCENES = ("S1", "S2", "S3")
TIER = "A (MiLOI real, network truth)"
SUCCESS_PX = 3.0
AGREE_PX = 1.0
EDGE_MIN_INLIERS = 50
MARGIN_M = 150.0
METHODS = ("ours", "SIFT", "ORB", "AKAZE")
OURS_METHOD = "ours_loftr+subpixel"
ILLUM_CSV = ROOT / "evaluation" / "miloi_illumination.csv"
TRUTH_JSON = ROOT / "evaluation" / "miloi_truth.json"
LOG = ROOT / "evaluation" / "miloi_log.csv"
ILLUM_FIELDS = ["scene", "image_id", "start_time", "map_resolution_m", "sun_azimuth_deg",
                "incidence_deg", "emission_deg", "phase_deg"]
FIELDS = ["timestamp", "pair_id", "scene", "source", "reference", "src_gsd_m", "ref_gsd_m",
          "scale_ratio", "d_sun_azimuth_deg", "d_incidence_deg", "d_sun_angle_deg", "method",
          "status", "n_matches", "inliers", "rmse_gt_px", "residual_median_px", "success",
          "truth", "declared_method", "matcher_err_px", "declared_err_px", "verdict", "outcome",
          "seconds", "git_commit", "command", "notes"]
BINS = ((0, 15), (15, 30), (30, 60), (60, 90), (90, 120), (120, 181))


def data_dir() -> pathlib.Path:
    p = ROOT / "data_path.txt"
    return pathlib.Path(p.read_text(encoding="utf-8-sig").strip())


def runs_dir() -> pathlib.Path:
    return data_dir() / "miloi_runs"


# --- illumination -------------------------------------------------------------------

def convert_sheets(miloi: pathlib.Path, out: pathlib.Path = ILLUM_CSV) -> int:
    """The three Image_illumination_angles.xlsx sheets -> one CSV in the repo (42 rows)."""
    import openpyxl
    rows = []
    for scene in SCENES:
        wb = openpyxl.load_workbook(miloi / scene / "Image_illumination_angles.xlsx",
                                    read_only=True, data_only=True)
        it = wb.worksheets[0].iter_rows(values_only=True)
        head = [str(h) for h in next(it) if h is not None]
        if head[:7] != ["imageID", "start time", "map resolution", "northAzimuth",
                        "incidence", "emission", "phase"]:
            raise SystemExit(f"{scene}: unexpected sheet header {head}")
        for r in it:
            if not r or not r[0]:
                continue
            rows.append(dict(zip(ILLUM_FIELDS, [scene, *r[:7]])))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ILLUM_FIELDS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def illumination(path: pathlib.Path = ILLUM_CSV) -> dict:
    """{(scene, image_id): {sun_azimuth_deg, incidence_deg, ...}} from the converted CSV."""
    if not path.exists():
        raise SystemExit(f"{path} missing - run `python -m evaluation.miloi --convert` once")
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        out[(r["scene"], r["image_id"])] = {k: (float(v) if k.endswith(("_deg", "_m")) else v)
                                           for k, v in r.items()}
    return out


def d_azimuth(a: float, b: float) -> float:
    """Circular azimuth difference, 0-180 deg."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def sun_angle(inc_a: float, az_a: float, inc_b: float, az_b: float) -> float:
    """Angle between the two sun direction vectors, deg."""
    ia, ib = math.radians(inc_a), math.radians(inc_b)
    c = (math.cos(ia) * math.cos(ib)
         + math.sin(ia) * math.sin(ib) * math.cos(math.radians(az_a - az_b)))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


# --- geometry -----------------------------------------------------------------------

def _shift(t) -> np.ndarray:
    return np.array([[1.0, 0.0, t[0]], [0.0, 1.0, t[1]], [0.0, 0.0, 1.0]])


def map_truth(src_transform, ref_transform, t_src=(0.0, 0.0), t_ref=(0.0, 0.0)) -> np.ndarray:
    """Source px -> reference px when the two images' map positions are corrected by
    t_src / t_ref metres. With no corrections this is the nominal (archive) transform."""
    from evaluation.real_eval import pixel_to_map
    d = np.subtract(t_src, t_ref)
    return np.linalg.inv(pixel_to_map(ref_transform)) @ _shift(d) @ pixel_to_map(src_transform)


def map_offset(H, src_transform, ref_transform, ref_shape) -> tuple[np.ndarray, float]:
    """What H says about the map: mean of P_ref(p) - P_src(H^-1 p) over the reference frame
    (= t_src - t_ref, metres), and the RMS of what one translation does not explain."""
    from evaluation.real_eval import _apply, _pts_grid, pixel_to_map
    p = _pts_grid(ref_shape)
    x = _apply(np.linalg.inv(np.asarray(H, np.float64)), p)
    d = _apply(pixel_to_map(ref_transform), p) - _apply(pixel_to_map(src_transform), x)
    mean = d.mean(0)
    return mean, float(np.sqrt(np.mean(np.sum((d - mean) ** 2, axis=1))))


def err_vs_truth(H, H_true, ref_shape) -> float | None:
    """RMS error of a transform against truth over the reference frame, in reference px."""
    if H is None:
        return None
    from core.reliability import _true_error_grid
    return float(np.sqrt(np.nanmean(_true_error_grid(tuple(ref_shape), H, H_true, 8) ** 2)))


def outcome(matcher_err, contradicted: bool) -> str:
    """The trust layer judged against truth, on the MATCHER's transform."""
    if matcher_err is None:
        return "no_transform"
    if matcher_err < SUCCESS_PX:
        return "false_alarm" if contradicted else "correct_accepted"
    return "caught_failure" if contradicted else "missed_failure"


# --- pairs --------------------------------------------------------------------------

def scene_pairs(scene: str, illum: dict, miloi: pathlib.Path, seed: int = 0) -> list[dict]:
    """Every unordered pair in a scene, finer image as source, in a seeded random order
    (so a run stopped part-way is still a spread over sun differences, not its easy end)."""
    from core.io_loader import load
    ims = []
    for tif in sorted((miloi / scene).glob("*.tif")):
        _, meta = load(tif, window=(0, 0, 8, 8))
        ims.append({"id": tif.stem, "path": tif, "gsd": meta["gsd_mpp"],
                    "transform": meta["transform"], **illum[(scene, tif.stem)]})
    pairs = []
    for a, b in itertools.combinations(ims, 2):
        src, ref = (a, b) if (a["gsd"], a["id"]) < (b["gsd"], b["id"]) else (b, a)
        pairs.append({
            "pair_id": f"miloi_{scene}_{src['id']}_{ref['id']}", "scene": scene,
            "src": src, "ref": ref,
            "scale_ratio": ref["gsd"] / src["gsd"],
            "d_az": d_azimuth(src["sun_azimuth_deg"], ref["sun_azimuth_deg"]),
            "d_inc": ref["incidence_deg"] - src["incidence_deg"],
            "d_sun": sun_angle(src["incidence_deg"], src["sun_azimuth_deg"],
                               ref["incidence_deg"], ref["sun_azimuth_deg"]),
        })
    order = np.random.default_rng(seed).permutation(len(pairs))
    return [pairs[i] for i in order]


def _write_crop(src_tif: pathlib.Path, out: pathlib.Path, x0: int, y0: int, w: int, h: int):
    """A window of a MiLOI GeoTIFF, as a GeoTIFF with the tie point moved to match."""
    import tifffile
    with tifffile.TiffFile(src_tif) as t:
        page = t.pages[0]
        img = page.asarray()[y0:y0 + h, x0:x0 + w]
        tags = {c: (page.tags[c].dtype, page.tags[c].count, page.tags[c].value)
                for c in (33550, 33922, 34735, 34736, 34737, 42113) if c in page.tags}
    sx, sy = tags[33550][2][:2]
    tp = list(tags[33922][2])
    tp[3] += x0 * sx
    tp[4] -= y0 * sy
    tags[33922] = (tags[33922][0], tags[33922][1], tuple(tp))
    tifffile.imwrite(str(out), np.ascontiguousarray(img),
                     extratags=[(c, dt, n, v, True) for c, (dt, n, v) in tags.items()])


def crop_pair(p: dict, workdir: pathlib.Path, side: int = 640) -> dict:
    """The reference's central `side` x `side` window (the matcher's limit), and the source
    cut to the same nominal ground plus MARGIN_M each side - generous, because the nominal
    geometry is off by up to ~250 m."""
    from core.io_loader import load
    from evaluation.real_eval import _apply
    rh, rw = load(p["ref"]["path"])[0].shape[:2]
    rx, ry = max(0, (rw - side) // 2), max(0, (rh - side) // 2)
    rcw, rch = min(side, rw), min(side, rh)
    ref_out = workdir / f"{p['ref']['id']}_ref.tif"
    _write_crop(p["ref"]["path"], ref_out, rx, ry, rcw, rch)
    m = MARGIN_M / p["ref"]["gsd"]
    corners = np.array([[rx - m, ry - m], [rx + rcw + m, ry - m],
                        [rx - m, ry + rch + m], [rx + rcw + m, ry + rch + m]], np.float64)
    s = _apply(np.linalg.inv(map_truth(p["src"]["transform"], p["ref"]["transform"])), corners)
    sh, sw = load(p["src"]["path"])[0].shape[:2]
    sx0, sy0 = (max(0, int(math.floor(v))) for v in s.min(0))
    sx1 = min(sw, int(math.ceil(s[:, 0].max())) + 1)
    sy1 = min(sh, int(math.ceil(s[:, 1].max())) + 1)
    src_out = workdir / f"{p['src']['id']}_source.tif"
    _write_crop(p["src"]["path"], src_out, sx0, sy0, sx1 - sx0, sy1 - sy0)
    _, ms = load(src_out)
    _, mr = load(ref_out)
    return {"src_path": src_out, "ref_path": ref_out, "src_transform": ms["transform"],
            "ref_transform": mr["transform"], "ref_shape": list(mr["full_shape"][:2])}


# --- --run: match every pair, keep the raw matches ----------------------------------

def _mat(H):
    return None if H is None else np.asarray(H, np.float64).tolist()


def run_pair(p: dict, methods=METHODS) -> dict:
    """Match one pair with every method; returns (json_meta, arrays). No truth is used."""
    from baselines.run_all_baselines import METHODS as BASE, to_uint8
    from baselines.settings import RATIO_TEST
    from core.io_loader import load
    from core.pipeline import run_all
    from core.scale import to_common_gsd, to_original
    arrays, meta = {}, {"methods": {}}
    with tempfile.TemporaryDirectory() as tmp:
        c = crop_pair(p, pathlib.Path(tmp))
        meta.update({k: c[k] for k in ("src_transform", "ref_transform", "ref_shape")})
        for name in methods:
            if name == "ours":
                r = run_all(c["src_path"], c["ref_path"])
                arrays["ours_src"], arrays["ours_ref"] = r["src_matches"], r["ref_matches"]
                rel = r.get("reliability")
                meta["methods"]["ours"] = {
                    "seconds": r["seconds"], "n_matches": r["n_matches"], "H": _mat(r["H"]),
                    "H_final": _mat(r["H_final"]), "declared": r["declared"]["method"],
                    "contradicted": bool(r["declared"]["contradicted"]),
                    "verdict": rel["global"].get("verdict") if rel else None,
                    "counts": rel["counts"] if rel else None,
                    "inliers": int(len(r["src_inliers"])) if r["H"] is not None else 0}
                continue
            t0 = time.perf_counter()
            a, ma = load(c["src_path"])
            b, mb = load(c["ref_path"])
            a_s, b_s, _gsd, f = to_common_gsd(a, ma, b, mb)
            err = None
            try:
                s, q, _c, _t = dict(BASE)[name](to_uint8(a_s), to_uint8(b_s), ratio=RATIO_TEST)
            except Exception as e:  # noqa: BLE001 - a dead detector is a failed pair
                s = q = np.zeros((0, 2), np.float32)
                err = f"{type(e).__name__}: {e}"
            arrays[f"{name}_src"] = to_original(s, f["a"]) if len(s) else np.zeros((0, 2))
            arrays[f"{name}_ref"] = to_original(q, f["b"]) if len(q) else np.zeros((0, 2))
            meta["methods"][name] = {"seconds": time.perf_counter() - t0,
                                     "n_matches": int(len(s)), "error": err}
    return meta, arrays


def retrust(scenes=SCENES) -> int:
    """Re-judge OURS' stored matches under the CURRENT trust layer: re-crop the pair and call
    run_all(matches=...) - MAGSAC++, the area check and the fallback run again; LoFTR does not.
    The earlier verdict is kept under `previous_trust`, so the change is visible, not overwritten."""
    from core.export import _commit
    from core.pipeline import run_all
    illum, miloi, commit, n = illumination(), data_dir() / "miloi", _commit(), 0
    for scene in scenes:
        pairs = {p["pair_id"]: p for p in scene_pairs(scene, illum, miloi)}
        for jp in sorted(runs_dir().glob(f"miloi_{scene}_*.json")):
            meta, arrays = load_run(jp.stem)
            o = meta["methods"].get("ours")
            if o is None or o.get("retrusted_at") == commit:
                continue
            with tempfile.TemporaryDirectory() as tmp:
                c = crop_pair(pairs[meta["pair_id"]], pathlib.Path(tmp))
                r = run_all(c["src_path"], c["ref_path"], matches=(arrays["ours_src"], arrays["ours_ref"]))
            rel = r.get("reliability")
            o.setdefault("previous_trust", {**{k: o.get(k) for k in (
                "H", "H_final", "declared", "contradicted", "verdict", "counts", "inliers")},
                "at": meta["git_commit"]})
            o.update({"H": _mat(r["H"]), "H_final": _mat(r["H_final"]), "declared": r["declared"]["method"],
                      "contradicted": bool(r["declared"]["contradicted"]),
                      "verdict": rel["global"].get("verdict") if rel else None,
                      "counts": rel["counts"] if rel else None,
                      "inliers": int(len(r["src_inliers"])) if r["H"] is not None else 0,
                      "retrusted_at": commit})
            jp.write_text(json.dumps(meta, indent=1))
            n += 1
            prev = o["previous_trust"]
            if (prev["verdict"], prev["declared"]) != (o["verdict"], o["declared"]):
                print(f"{meta['pair_id']:<42} {prev['verdict']}/{prev['declared']} -> "
                      f"{o['verdict']}/{o['declared']}", flush=True)
    print(f"{n} pair(s) re-judged at {commit}")
    return n


def _run_paths(pair_id: str):
    d = runs_dir()
    return d / f"{pair_id}.json", d / f"{pair_id}.npz"


def load_run(pair_id: str):
    jp, npz = _run_paths(pair_id)
    if not jp.exists():
        return None, None
    with np.load(npz) as z:
        arrays = {k: z[k] for k in z.files}
    return json.loads(jp.read_text()), arrays


def run_all_pairs(scenes, methods, max_pairs=None) -> None:
    from core.export import _commit
    illum, miloi = illumination(), data_dir() / "miloi"
    runs_dir().mkdir(exist_ok=True)
    for scene in scenes:
        pairs = scene_pairs(scene, illum, miloi)[:max_pairs]
        todo = [p for p in pairs if not _run_paths(p["pair_id"])[0].exists()]
        print(f"\n== {scene}: {len(pairs)} pairs, {len(todo)} to run ==", flush=True)
        for i, p in enumerate(todo, 1):
            meta, arrays = run_pair(p, methods)
            meta.update({"pair_id": p["pair_id"], "scene": scene, "source": p["src"]["id"],
                         "reference": p["ref"]["id"], "src_gsd_m": p["src"]["gsd"],
                         "ref_gsd_m": p["ref"]["gsd"], "scale_ratio": p["scale_ratio"],
                         "d_sun_azimuth_deg": p["d_az"], "d_incidence_deg": p["d_inc"],
                         "d_sun_angle_deg": p["d_sun"], "git_commit": _commit(),
                         "utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")})
            jp, npz = _run_paths(p["pair_id"])
            np.savez_compressed(npz, **{k: np.asarray(v, np.float32) for k, v in arrays.items()})
            jp.write_text(json.dumps(meta, indent=1))   # written last: its presence = done
            o = meta["methods"].get("ours", {})
            print(f"[{i}/{len(todo)}] {p['pair_id']:<42} d_sun {p['d_sun']:5.1f}  ours inl "
                  f"{o.get('inliers', '-'):>5} {o.get('declared', '')}  "
                  + "  ".join(f"{m} {meta['methods'][m]['n_matches']}"
                              for m in methods if m != "ours")
                  + f"  {sum(v['seconds'] for v in meta['methods'].values()):.0f}s", flush=True)


# --- --truth: the per-image translation network --------------------------------------

def _method_H(meta, arrays, name):
    """The transform a method's raw matches give under the pipeline's own MAGSAC++."""
    if name == "ours":
        H, n = meta["methods"]["ours"]["H"], meta["methods"]["ours"]["inliers"]
        return (None if H is None else np.asarray(H)), n
    from core.ransac import filter_matches
    s, q = arrays.get(f"{name}_src"), arrays.get(f"{name}_ref")
    if s is None or len(s) < 4:
        return None, 0
    si, _qi, H, _info = filter_matches(s.astype(np.float64), q.astype(np.float64))
    return H, (0 if H is None else int(len(si)))


def edges_for(runs: list) -> list[dict]:
    """Pairs where ours and SIFT independently agree - the network's observations."""
    out = []
    for meta, arrays in runs:
        Ho, no = _method_H(meta, arrays, "ours")
        Hs, ns = _method_H(meta, arrays, "SIFT")
        if Ho is None or Hs is None or min(no, ns) < EDGE_MIN_INLIERS:
            continue
        agree = err_vs_truth(Ho, Hs, meta["ref_shape"])
        if agree is None or not agree < AGREE_PX:
            continue
        do, ro = map_offset(Ho, meta["src_transform"], meta["ref_transform"], meta["ref_shape"])
        ds, rs = map_offset(Hs, meta["src_transform"], meta["ref_transform"], meta["ref_shape"])
        out.append({"pair_id": meta["pair_id"], "src": meta["source"], "ref": meta["reference"],
                    "d_m": ((do + ds) / 2).tolist(), "agree_px": agree,
                    "inliers_ours": no, "inliers_sift": ns,
                    "nontranslation_rms_m": max(ro, rs), "d_sun_angle_deg": meta["d_sun_angle_deg"],
                    "ref_gsd_m": meta["ref_gsd_m"]})
    return out


def solve(nodes: list[str], edges: list[dict], skip: str | None = None) -> dict:
    """Least-squares translation per image from edge offsets d = t_src - t_ref; mean 0 per
    connected component. Returns {image_id: (t, component)} for images with any edge."""
    use = [e for e in edges if e["pair_id"] != skip]
    parent = {n: n for n in nodes}

    def find(n):
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    for e in use:
        parent[find(e["src"])] = find(e["ref"])
    comps = {}
    for n in nodes:
        if any(n in (e["src"], e["ref"]) for e in use):
            comps.setdefault(find(n), []).append(n)
    out = {}
    for k, (root, members) in enumerate(sorted(comps.items())):
        idx = {n: i for i, n in enumerate(members)}
        es = [e for e in use if e["src"] in idx]
        A = np.zeros((len(es) + 1, len(members)))
        b = np.zeros((len(es) + 1, 2))
        for r, e in enumerate(es):
            A[r, idx[e["src"]]], A[r, idx[e["ref"]]] = 1.0, -1.0
            b[r] = e["d_m"]
        A[-1, :] = 1.0                      # gauge: the component's mean translation is 0
        t, *_ = np.linalg.lstsq(A, b, rcond=None)
        for n, i in idx.items():
            out[n] = (t[i], k)
    return out


def build_truth(scenes=SCENES) -> dict:
    illum = illumination()
    report = {"method": "per-image translation network from ours+SIFT agreement "
                        f"(< {AGREE_PX} px, >= {EDGE_MIN_INLIERS} inliers each); leave-one-out "
                        "for edge pairs", "scenes": {}}
    for scene in scenes:
        runs = [load_run(jp.stem) for jp in sorted(runs_dir().glob(f"miloi_{scene}_*.json"))]
        nodes = sorted(i for (s, i) in illum if s == scene)
        edges = edges_for(runs)
        full = solve(nodes, edges)
        for e in edges:
            loo = solve(nodes, edges, skip=e["pair_id"])
            ts, tr = loo.get(e["src"]), loo.get(e["ref"])
            if ts and tr and ts[1] == tr[1]:
                pred = ts[0] - tr[0]
                e["loo_err_m"] = float(np.hypot(*(np.asarray(e["d_m"]) - pred)))
                e["loo_err_px"] = e["loo_err_m"] / e["ref_gsd_m"]
            else:
                e["loo_err_m"] = e["loo_err_px"] = None
            fs, fr = full[e["src"]][0], full[e["ref"]][0]
            e["fit_resid_m"] = float(np.hypot(*(np.asarray(e["d_m"]) - (fs - fr))))
        loo_px = [e["loo_err_px"] for e in edges if e["loo_err_px"] is not None]
        report["scenes"][scene] = {
            "pairs_run": len(runs), "edges": edges,
            "images": {n: {"t_m": full[n][0].tolist(), "component": full[n][1]} if n in full
                       else None for n in nodes},
            "n_components": len({v[1] for v in full.values()}),
            "images_without_truth": [n for n in nodes if n not in full],
            "loo_err_px": ({"n": len(loo_px), "median": float(np.median(loo_px)),
                            "p90": float(np.percentile(loo_px, 90)), "max": float(max(loo_px))}
                           if loo_px else None),
        }
    TRUTH_JSON.write_text(json.dumps(report, indent=1))
    return report


def truth_for(meta: dict, truth: dict) -> tuple[np.ndarray | None, str]:
    """(H_true, how) for one run: leave-one-out when the pair is itself an edge."""
    sc = truth["scenes"].get(meta["scene"])
    if not sc:
        return None, "scene not in truth"
    edges = sc["edges"]
    if any(e["pair_id"] == meta["pair_id"] for e in edges):
        nodes = list(sc["images"])
        sol = solve(nodes, edges, skip=meta["pair_id"])
        how = "network, leave-one-out"
    else:
        sol = {n: (np.asarray(v["t_m"]), v["component"]) for n, v in sc["images"].items() if v}
        how = "network"
    s, r = sol.get(meta["source"]), sol.get(meta["reference"])
    if not s or not r or s[1] != r[1]:
        return None, "no truth (images not connected by agreeing pairs)"
    return map_truth(meta["src_transform"], meta["ref_transform"], s[0], r[0]), how


# --- --score: every method against the truth -> the logs ------------------------------

def _logged() -> set:
    if not LOG.exists():
        return set()
    return {(r["pair_id"], r["method"]) for r in csv.DictReader(open(LOG, encoding="utf-8"))}


def _append(row: dict) -> None:
    new = not LOG.exists() or LOG.stat().st_size == 0
    if not new:
        with open(LOG, "rb") as f:
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                raise RuntimeError(f"{LOG} does not end in a newline; refusing to append")
    unknown = set(row) - set(FIELDS)
    if unknown:
        raise ValueError(f"unknown miloi_log fields: {sorted(unknown)}")
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in FIELDS})


def _fmt(v, nd=3):
    return "n/a" if v is None else f"{v:.{nd}f}"


def score(log: bool, command: str, scenes=SCENES) -> None:
    from core.export import _commit
    from core.pipeline import _log_row
    from evaluation.metrics import evaluate
    if not TRUTH_JSON.exists():
        raise SystemExit(f"{TRUTH_JSON} missing - run --truth first")
    truth = json.loads(TRUTH_JSON.read_text())
    done = _logged() if log else set()
    commit = _commit()
    for scene in scenes:
        for jp in sorted(runs_dir().glob(f"miloi_{scene}_*.json")):
            meta, arrays = load_run(jp.stem)
            H_true, how = truth_for(meta, truth)
            if H_true is None:
                print(f"{meta['pair_id']:<42} {how}")
                continue
            shape = tuple(meta["ref_shape"])
            sun = (f"d_sun_az {meta['d_sun_azimuth_deg']:.1f} deg, d_inc "
                   f"{meta['d_incidence_deg']:+.2f} deg, sun-vector angle "
                   f"{meta['d_sun_angle_deg']:.1f} deg; scale {meta['scale_ratio']:.2f}x")
            for name, mm in meta["methods"].items():
                method = OURS_METHOD if name == "ours" else name
                if (meta["pair_id"], method) in done:
                    continue
                m = evaluate(shape, arrays[f"{name}_src"].astype(np.float32),
                             arrays[f"{name}_ref"].astype(np.float32), H_true=H_true)
                rmse = m.get("rmse_gt_px")
                ok = rmse is not None and rmse < SUCCESS_PX
                ours = {}
                if name == "ours":
                    m_err = err_vs_truth(None if mm["H"] is None else np.asarray(mm["H"]),
                                         H_true, shape)
                    d_err = err_vs_truth(None if mm["H_final"] is None else np.asarray(mm["H_final"]),
                                         H_true, shape)
                    ours = {"declared_method": mm["declared"], "matcher_err_px": m_err,
                            "declared_err_px": d_err, "verdict": mm["verdict"],
                            "outcome": outcome(m_err, mm["contradicted"])}
                print(f"{meta['pair_id']:<42} {name:<6} d_sun {meta['d_sun_angle_deg']:5.1f} "
                      f"inl {m.get('inlier_count') or 0:>5} rmse_gt {_fmt(rmse):>9} "
                      f"{'OK ' if ok else 'FAIL'}"
                      + (f" declared {_fmt(ours['declared_err_px'])} [{ours['outcome']}]"
                         if ours else ""), flush=True)
                if not log:
                    continue
                extra = (f"; declared {ours['declared_method']}, error vs truth: matcher "
                         f"{_fmt(ours['matcher_err_px'])} px, declared "
                         f"{_fmt(ours['declared_err_px'])} px; trust outcome {ours['outcome']}"
                         if ours else "")
                config = (f"MiLOI truth: {how} ({TRUTH_JSON.name}); "
                          + ("run_all defaults" if ours else
                             "same common-GSD resampling as ours; ratio test 0.75"))
                ok_log, note = _log_row(
                    meta["pair_id"], TIER, method, m, config=config, gsd_mpp=meta["ref_gsd_m"],
                    notes=(f"MiLOI {scene} {meta['source']} -> {meta['reference']}; {sun}{extra}; "
                           f"success = rmse_gt_px < {SUCCESS_PX}; matches from run at "
                           f"{meta['git_commit']}"
                           + (f", ours' trust verdict re-judged at {mm['retrusted_at']}"
                              if mm.get("retrusted_at") else "")),
                    allow_failed=True)
                if not ok_log:
                    raise SystemExit(note)
                _append({
                    "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
                    "pair_id": meta["pair_id"], "scene": scene, "source": meta["source"],
                    "reference": meta["reference"], "src_gsd_m": meta["src_gsd_m"],
                    "ref_gsd_m": meta["ref_gsd_m"], "scale_ratio": round(meta["scale_ratio"], 4),
                    "d_sun_azimuth_deg": round(meta["d_sun_azimuth_deg"], 2),
                    "d_incidence_deg": round(meta["d_incidence_deg"], 2),
                    "d_sun_angle_deg": round(meta["d_sun_angle_deg"], 2), "method": method,
                    "status": m.get("status"), "n_matches": mm["n_matches"],
                    "inliers": m.get("inlier_count"), "rmse_gt_px": rmse,
                    "residual_median_px": m.get("residual_median_px"), "success": int(ok),
                    "truth": how, **ours, "seconds": round(mm["seconds"], 1),
                    "git_commit": f"run {meta['git_commit']}, scored {commit}",
                    "command": command,
                    "notes": f"reliability {mm['counts']}" if name == "ours" and mm.get("counts") else "",
                })


# --- the table ----------------------------------------------------------------------

def table(path: pathlib.Path = LOG, key: str = "d_sun_angle_deg", scene=None) -> list[str]:
    """Success rate per method per sun-difference bin, from miloi_log.csv only.
    The latest row per (pair, method) wins."""
    latest = {}
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if scene is None or r["scene"] == scene:
            latest[(r["pair_id"], r["method"])] = r
    methods = sorted({m for _, m in latest}, key=lambda m: (m != OURS_METHOD, m))
    out = [f"success = rmse_gt_px < {SUCCESS_PX} px on the reference grid, vs the MiLOI "
           f"network truth ({TRUTH_JSON.name}){'' if scene is None else ', scene ' + scene}",
           f"{key:<18}" + "".join(f"{m:>22}" for m in methods)]
    for lo, hi in BINS:
        cells = []
        for m in methods:
            rs = [r for (_, mm), r in latest.items() if mm == m and lo <= float(r[key]) < hi]
            k = sum(int(r["success"]) for r in rs)
            cells.append(f"{k}/{len(rs)}" + (f" ({100 * k / len(rs):.0f}%)" if rs else ""))
        out.append(f"{lo:>4}-{hi:<4} deg      " + "".join(f"{c:>22}" for c in cells))
    ours = [r for (_, m), r in latest.items() if m == OURS_METHOD]
    if ours:
        from collections import Counter
        c = Counter(r["outcome"] for r in ours)
        d_ok = sum(1 for r in ours if r["declared_err_px"] and float(r["declared_err_px"]) < SUCCESS_PX)
        out += ["", "ours, trust outcomes vs truth: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())),
                f"ours, declared transform within {SUCCESS_PX} px of truth: {d_ok}/{len(ours)}"]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m evaluation.miloi",
                                 description=__doc__.split("\n")[0])
    ap.add_argument("--convert", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--retrust", action="store_true",
                    help="re-judge ours' stored matches under the current trust layer (no LoFTR)")
    ap.add_argument("--truth", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--log", action="store_true", help="with --score: append to the logs")
    ap.add_argument("--scenes", nargs="*", default=list(SCENES))
    ap.add_argument("--methods", nargs="*", default=list(METHODS), choices=METHODS)
    ap.add_argument("--max-pairs", type=int, default=None, help="per scene, in the seeded order")
    ap.add_argument("--by", default="d_sun_angle_deg",
                    choices=("d_sun_angle_deg", "d_sun_azimuth_deg"))
    a = ap.parse_args(argv)
    command = "python -m evaluation.miloi " + " ".join(argv if argv is not None else sys.argv[1:])
    if a.convert:
        print(f"{convert_sheets(data_dir() / 'miloi')} images -> {ILLUM_CSV}")
    if a.run:
        run_all_pairs(a.scenes, a.methods, a.max_pairs)
    if a.retrust:
        retrust(a.scenes)
    if a.truth:
        rep = build_truth(a.scenes)
        for s, v in rep["scenes"].items():
            print(f"{s}: {v['pairs_run']} pairs run, {len(v['edges'])} edges, "
                  f"{v['n_components']} component(s), no truth for {v['images_without_truth']}; "
                  f"leave-one-out error px {v['loo_err_px']}")
    if a.score:
        score(a.log, command, a.scenes)
    if a.table:
        print("\n".join(table(key=a.by)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
