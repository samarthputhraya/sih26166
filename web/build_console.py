"""Build the Mission Console: web/console.template.html + the frozen evidence -> web/dist/.

    python -m web.build_console

The console is a DISPLAY of the evidence, never a source of it. This script only READS: the
evidence logs, the demo caches, geometry_prior.json and the LOLA DEM. Every number the page shows
is one REPORT.md also prints at the freeze commit (Invariant 1 applies to this page exactly as it
does to the deck), and the figures typed into the template's prose are the claim-checked deck's.
It lives in web/, outside core/ evaluation/ ops/ app/, so building it can never restamp an
evidence row or a demo cache. Re-run it after any new freeze and update FREEZE below.
"""
import base64, collections, csv, json, pathlib, pickle, statistics as st, sys
import numpy as np, cv2, tifffile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())
HERE = pathlib.Path(__file__).resolve().parent
FREEZE = "7dd4e5b"
sys.path.insert(0, str(ROOT))

def rows(p): return list(csv.DictReader(open(ROOT / p, encoding="utf-8-sig")))
def f(x): return float(x) if x not in ("", None) else None

def jpg(a, size=448, q=78):
    if isinstance(a, (str, pathlib.Path)):
        a = tifffile.imread(str(a))
    a = np.asarray(a, dtype=np.float64)
    if a.ndim == 3: a = a[..., 0]
    ok = np.isfinite(a)
    lo, hi = np.percentile(a[ok], [1, 99]) if ok.any() else (0, 1)
    a = np.clip((np.nan_to_num(a, nan=lo) - lo) / max(hi - lo, 1e-9), 0, 1)
    a = cv2.resize((a * 255).astype(np.uint8), (size, size), interpolation=cv2.INTER_AREA)
    _, buf = cv2.imencode(".jpg", a, [cv2.IMWRITE_JPEG_QUALITY, q])
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()

def trust(pid, label, sub):
    r = pickle.load(open(ROOT / f"demo_cache/results/{pid}.pkl", "rb"))
    rel = r["reliability"]; g = lambda k: np.asarray(rel[k])
    cells = []
    for y in range(8):
        for x in range(8):
            ncc = g("area_ncc")[y, x]; res = g("median_inlier_residual_px")[y, x]
            cells.append({"s": str(g("state")[y, x]), "n": int(g("n_inliers")[y, x]),
                          "raw": int(g("n_raw")[y, x]),
                          "ncc": None if not np.isfinite(ncc) else round(float(ncc), 3),
                          "res": None if not np.isfinite(res) else round(float(res), 3),
                          "lir": round(float(g("local_inlier_ratio")[y, x]), 3)})
    warped = r.get("warped_final") if r.get("warped_final") is not None else r.get("warped")
    return {"id": pid, "label": label, "sub": sub, "cells": cells,
            "counts": {k: int(v) for k, v in rel["counts"].items()},
            "verdict": rel["global"]["verdict"], "method": r["declared"]["method"],
            "why": r["declared"]["why"], "gsd": rel["gsd_mpp"], "n_matches": int(r["n_matches"]),
            "inliers": int(r["ransac"]["inlier_count"]), "seconds": round(float(r["seconds"]), 1),
            "ref": jpg(r["reference"]), "warped": jpg(warped), "src": jpg(r["source"])}

real = rows("evaluation/real_pairs_log.csv")
latest = {}
for r in real: latest[r["pair_id"]] = r
reg = {k: r for k, r in latest.items() if r["verdict"] != "INVALIDATED" and not k.startswith("loop_")}

tiles = []
for k, r in sorted(reg.items()):
    if not k.endswith("_full"): continue
    gp = json.loads((ROOT / "data/pairs" / k / "geometry_prior.json").read_text(encoding="utf-8"))
    tiles.append({"id": k.split("_")[-2], "x": gp["window_centre_map_m"][0], "y": gp["window_centre_map_m"][1],
                  "w": gp["window_m"], "med": round(f(r["residual_median_px"]), 3),
                  "inl": int(f(r["inliers"])), "ratio": round(f(r["inlier_ratio"]), 3),
                  "ver": int(f(r["verified"])), "verdict": r["verdict"], "sec": round(f(r["seconds"]), 1)})

from ops.sun_sweep import outcomes_v2
sw = {k: r for k, r in reg.items() if (r.get("outcome") or "").strip()}
v2 = outcomes_v2(list(sw.values()), rows("evaluation/results_log.csv"))
sweep = [{"az": round(f(r["d_sun_azimuth_deg"]), 1), "inl": int(f(r["inliers"]) or 0),
          "o": v2.get(k, r["outcome"]), "nac": r["reference_product"]} for k, r in sw.items()]
bins = []
for a, b in [(0, 10), (10, 30), (30, 60), (60, 90), (90, 120), (120, 180)]:
    rs_ = [s for s in sweep if a <= s["az"] < b]
    bins.append({"a": a, "b": b, "n": len(rs_), "frames": len({s["nac"] for s in rs_}),
                 "o": dict(collections.Counter(s["o"] for s in rs_)),
                 "inl": int(st.median(s["inl"] for s in rs_)) if rs_ else 0})

tr = rows("evaluation/trust_real_calibration.csv")
def pop(sel):
    by = {}
    for r in tr:
        if (r.get("kind") or "translation") != "translation" or not sel(r): continue
        by.setdefault(f(r["displacement_m"]), []).append(r["contradicted"] == "True")
    return [{"m": d, "n": len(v), "hit": sum(v)} for d, v in sorted(by.items())]
near = pop(lambda r: f(r.get("d_sun_azimuth_deg") or 0) < 10)
hard = pop(lambda r: f(r.get("d_sun_azimuth_deg") or 0) >= 10)
nt = [r for r in tr if (r.get("kind") or "translation") != "translation"]
rs = {"moved": sum(int(r["cells_moved_2px"]) for r in nt), "refused": sum(int(r["moved_not_verified"]) for r in nt),
      "still": sum(int(r["cells_under_1px"]) for r in nt), "kept": sum(int(r["under_1px_verified"]) for r in nt),
      "trials": len(nt)}

dem = np.load(DATA / "raw/dem_site_60m.npy").astype(np.float64)
n = min(dem.shape); dem = dem[:n, :n]; N = 224
small = cv2.resize(dem, (N, N), interpolation=cv2.INTER_AREA)
lo, hi = float(small.min()), float(small.max())
q = np.round((small - lo) / (hi - lo) * 65535).astype("<u2")
demd = {"n": N, "lo": round(lo, 1), "hi": round(hi, 1), "km": round(n * 0.06, 2),
        "b64": base64.b64encode(q.tobytes()).decode()}

data = {"freeze": FREEZE, "dem": demd, "bins": bins,
        "maps": [trust("sac_ohrc_nac_w06", "SAC benchmark: OHRC to LRO NAC", "cross-sensor, Sun azimuths 174 deg apart"),
                 trust("site_tc_morning_mi1548_w01", "Kaguya TC to MI 1548 nm", "multi-modal, visible to near-infrared")],
        "tiles": tiles, "sweep": sweep, "near": near, "hard": hard, "rotscale": rs}
blob = json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\/")
tpl = (HERE / "console.template.html").read_text(encoding="utf-8")
MARK = "/*__DATA__*/null"
if tpl.count(MARK) != 1:
    raise SystemExit(f"template must contain {MARK!r} exactly once, found {tpl.count(MARK)}")
(HERE / "dist").mkdir(exist_ok=True)
OUT = HERE / "dist" / "mission-console.html"
OUT.write_text(tpl.replace(MARK, blob), encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)}: {OUT.stat().st_size/1024:.0f} KB")
print("outcomes", dict(collections.Counter(s["o"] for s in sweep)))
for b_ in bins: print("  bin", b_["a"], b_["b"], "n", b_["n"], "frames", b_["frames"], b_["o"], "inl", b_["inl"])
print("dem", demd["n"], demd["lo"], demd["hi"], demd["km"], "km")
print("tiles", len(tiles), "| max med", max(t_["med"] for t_ in tiles), "| rotscale", rs)
for m in data["maps"]: print(m["id"], m["counts"], m["verdict"], m["method"], m["inliers"])
