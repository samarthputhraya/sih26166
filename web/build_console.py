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

from web.panel import jpg, panel

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())
HERE = pathlib.Path(__file__).resolve().parent
FREEZE = "7dd4e5b"
sys.path.insert(0, str(ROOT))

def rows(p): return list(csv.DictReader(open(ROOT / p, encoding="utf-8-sig")))
def f(x): return float(x) if x not in ("", None) else None

def sharpness(path):
    """High-frequency content of a reference frame, as the variance of its Laplacian.

    Reported so the "it is only blurrier" reading can be tested rather than argued with. It is a
    relative measure between two frames on the same grid, not an absolute resolution figure.
    """
    a = tifffile.imread(str(path)).astype(np.float64)
    if a.ndim == 3:
        a = a[..., 0]
    a = (a - np.nanmin(a)) / max(np.nanmax(a) - np.nanmin(a), 1e-9)
    return float(cv2.Laplacian(np.nan_to_num(a), cv2.CV_64F).var())


def twin(pid, other, band, other_band):
    """The same source image against a different BAND of the same reference product."""
    def one(p):
        r = pickle.load(open(ROOT / f"demo_cache/results/{p}.pkl", "rb")) if (ROOT / f"demo_cache/results/{p}.pkl").exists() else None
        row = latest.get(p)
        return {"matches": int(f(row["n_matches"])), "inliers": int(f(row["inliers"])),
                "ratio": round(f(row["inlier_ratio"]), 3),
                "cov": round(f(row["grid_coverage_fraction"]), 2),
                "verdict": row["verdict"], "declared": row["method_declared"],
                "med": round(f(row["residual_median_px"]), 3), "gsd": round(f(row["ref_gsd_m"]), 1),
                "sharp": round(sharpness(next((ROOT / "data/pairs" / p).glob("*_ref.tif"))), 5)}
    g = json.loads((ROOT / "data/pairs" / pid / "geometry_prior.json").read_text(encoding="utf-8"))
    mm = {r["pair_id"]: r for r in rows("evaluation/multimodal_check.csv")}
    fb = mm.get(pid)
    return {"band": band, "other_band": other_band, "a": one(other), "b": one(pid),
            "src": g["source"]["product_id"], "ref": g["reference"]["product_id"].split(" band")[0],
            "fallback_px": round(f(fb["disagreement_median_px"]), 3) if fb else None,
            "fallback_m": round(f(fb["disagreement_median_m"]), 1) if fb else None}


def trust(pid, label, sub, tag, plain):
    """A frozen pair, rendered by the SAME function the live server uses (web/panel.py)."""
    r = pickle.load(open(ROOT / f"demo_cache/results/{pid}.pkl", "rb"))
    g = json.loads((ROOT / "data/pairs" / pid / "geometry_prior.json").read_text(encoding="utf-8"))

    def side(k):
        s = g[k]
        return {"inst": s.get("instrument"), "band": s.get("band"),
                "prod": s.get("product_id"), "gsd": s.get("resampled_gsd_mpp")}

    return panel(r, side("source"), side("reference"), pid=pid, label=label, sub=sub, tag=tag,
                 plain=plain,
                 twin=twin(pid, "site_tc_morning_mi749_w01", "1548 nm (near-infrared)",
                           "749 nm (visible)") if "mi1548" in pid else None)


# (pair_id, label, sub, tag, plain). One representative of every instrument pairing in the
# evidence, and of all three verdicts. `tag` obeys Invariant 2: NAC-NAC and TMC-2 fore-aft are
# SAME SENSOR, and only visible-to-infrared or optical-to-elevation is MULTI-MODAL.
ROSTER = [
    ("sac_ohrc_nac_w06", "Chandrayaan-2 OHRC \u2192 LRO NAC", "SAC's own published benchmark pair. Sun azimuths 174\u00b0 apart, so every shadow points the opposite way.", "CROSS-SENSOR",
     "The hardest lighting there is, and it holds. Two different cameras on two different missions, photographed under opposite Suns, and the matches and the pixels independently agree on the same alignment."),
    ("sac_polar_ohrc_nac_w06", "Chandrayaan-2 OHRC \u2192 LRO NAC, polar", "SAC's polar pair at 62\u00a0\u00b0S. Sun azimuths 132\u00b0 apart, long shadows over steep ground.", "CROSS-SENSOR",
     "Four of the six windows on this pair were accepted. This is one of the two that were not. Nothing about the picture tells you that \u2014 the area check did, and the window was flagged rather than shipped."),
    ("site_m1153871873le_m1363141432re_w01_t", "LRO NAC \u2192 LRO NAC", "One instrument against itself at 74\u00a0\u00b0S. A pure Sun-angle test, and deliberately not a cross-sensor one.", "SAME SENSOR",
     "Same camera, same optics, different Sun. We label this <b>same sensor</b> and never count it as cross-sensor evidence, because calling it that is the single easiest claim for a reviewer to catch and it would discredit every other number."),
    ("site_ohrc_tc_ortho_w01", "Chandrayaan-2 OHRC \u2192 Kaguya TC", "A 29.6\u00d7 scale gap: 0.25 m imagery onto a 7.4 m ortho map.", "CROSS-SENSOR",
     "Scale invariance, at nearly thirty to one. Both images are resampled to one ground scale before matching, so the matcher never sees the gap \u2014 and three of the four windows at this site were accepted."),
    ("site_tc_morning_mi749_w01", "Kaguya TC \u2192 Kaguya MI 749 nm", "Visible against visible, on MI's 14.8 m grid. The control for the infrared pair below.", "CROSS-SENSOR",
     "This is the control experiment. Same source file, same reference product, same grid as the 1548 nm pair below \u2014 only the waveband differs. In visible light it registers cleanly."),
    ("site_tc_morning_mi1548_w01", "Kaguya TC \u2192 Kaguya MI 1548 nm", "Visible light matched against near-infrared. Same source file and grid as the 749 nm pair above.", "MULTI-MODAL",
     "<b>Refused, then delivered anyway.</b> The matcher found 35 matches where its visible-light twin found 334, and the transform it built is visibly wrong \u2014 open MATCHER'S ANSWER. The area check caught it, the system refused it and fell back to global phase correlation, <b>declaring which method it used</b>. That fallback lands 0.283 px = 4.2 m from the visible-band registration of this same window. The window IS registered. What the system refuses to do is pretend the feature matcher is what did it."),
    ("site_tc_ortho_iirs1000_w04", "Kaguya TC \u2192 Chandrayaan-2 IIRS", "Visible onto an imaging spectrometer band: 12\u00d7 coarser, at 89 m per pixel.", "MULTI-MODAL",
     "The hardest multi-modal rung we attempt, and the honest result is that it does not register. Ten of the eleven IIRS windows are refused and none registers. We report that as a limit, not as a number \u2014 IIRS band selection is named on the deck as the next step, not as a solved problem."),
    ("sac_ohrc_tmc_w01", "Chandrayaan-2 OHRC \u2192 TMC-2", "Two cameras on the same spacecraft. Sun azimuths 120\u00b0 and incidence 59\u00b0 apart.", "SAME MISSION",
     "Same mission, and still refused: all four windows at SAC's site. The Sun geometry is the reason, not the sensors. There is one TMC-2 pass over this frame with the Sun about 9\u00b0 from the OHRC's, and testing it is the one measurable improvement left open."),
    ("sac_tmcfore_tmcaft_w04", "TMC-2 fore \u2192 TMC-2 aft", "One instrument, one pass, seconds apart. Only the viewing direction differs, by about 50\u00b0.", "SAME SENSOR",
     "Identical camera, identical Sun, and only one of the four windows is accepted \u2014 because relief parallax is not a homography. When two views differ by 50\u00b0 the terrain itself shifts differently at different heights, and no single flat transform can describe it. The system does not pretend otherwise."),
    ("site_ohrc_lola_w01", "Chandrayaan-2 OHRC \u2192 LOLA relief", "Optical imagery onto elevation rendered as shaded relief, 240\u00d7 coarser.", "MULTI-MODAL",
     "Declared a failure rung before it was ever run, and it failed as predicted. It is on the page because a method that is only ever shown its best case has not been tested. The pre-registered prediction and the result are both in the audit report."),
]

real = rows("evaluation/real_pairs_log.csv")
latest = {}  # read by twin(), which runs later, when data = {...} calls trust()
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
        "maps": [trust(*r) for r in ROSTER],
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
print(f"roster: {len(data['maps'])} pairs")
for m in data["maps"]:
    print(f"  {m['id']:40} {m['tag']:13} {m['verdict']:13} {m['counts']['verified']:>2}/64 verified")
