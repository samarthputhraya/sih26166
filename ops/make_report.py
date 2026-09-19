"""Write REPORT.md - the evaluation report - from the evidence files alone.

    python -m ops.make_report            # -> REPORT.md at the repo root

Nothing in the report is typed: every number is read from
    evaluation/results_log.csv            (the 15-column evidence log, Invariant 1)
    evaluation/real_pairs_log.csv         (real-pair structure: sun, window, loops, outcomes)
    evaluation/trust_real_calibration.csv (planted-failure trials on real windows)
    <data>/download_manifest_done.csv     (every downloaded product with its sha256)
    <data>/site_geometry/<pid>.json       (the saved NAC correction fields)
Where a pair was run more than once, the LATEST row wins and the table says how many
rows exist. Re-run this after the evidence freeze; never edit REPORT.md by hand.
"""
from __future__ import annotations

import csv
import datetime as _dt
import pathlib
import re
import statistics as st
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "evaluation" / "results_log.csv"
REAL = ROOT / "evaluation" / "real_pairs_log.csv"
TRUST = ROOT / "evaluation" / "trust_real_calibration.csv"
OUT = ROOT / "REPORT.md"


def _data():
    p = ROOT / "data_path.txt"
    return pathlib.Path(p.read_text(encoding="utf-8-sig").strip()) if p.exists() else None


def _rows(p):
    if not pathlib.Path(p).exists():
        return []
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def _jsonfile(p):
    import json
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8")) if pathlib.Path(p).exists() else None


def _f(v, nd=3):
    try:
        return f"{float(v):.{nd}f}"
    except (TypeError, ValueError):
        return "n/a"


def _latest(rows, key="pair_id"):
    out, n = {}, Counter()
    for r in rows:
        out[r[key]] = r
        n[r[key]] += 1
    return out, n


def _git():
    from core.export import _commit
    return _commit(("core", "evaluation", "ops"))


def _kind(r):
    """The pair's instruments from its product ids. The logged `kind` column said
    "nac-nac" for the Kaguya TC -> MI rows (fixed in run_real_pairs on 18 Sep; the log
    is append-only, so the report derives it)."""
    def one(pid):
        pid = pid or ""
        if pid.startswith("ch2_ohr"):
            return "ohrc"
        if pid.startswith("ch2_tmc"):
            return "tmc2"
        if pid.startswith("ch2_iir"):
            return "iirs"
        if pid.startswith("TCO_"):
            return "tc"
        if pid.startswith("MI_MAP"):
            return "mi"
        if pid.startswith("ldem_"):
            return "lola"
        return "nac" if re.match(r"^M\d+[LR]E$", pid) else "other"
    if r["pair_id"].startswith("loop_"):
        return r["kind"]
    return f"{one(r['source_product'])}-{one(r['reference_product'])}"


def section_pairs(title, rows, note):
    L = [f"## {title}", "", note, "",
         "| pair | window (lat, lon) | Δsun az | scale | matches | inliers | ratio | coverage | "
         "held-out median px (m) | held-out RMSE ≤3 px | verified / no-evid | verdict | declared | archive offset m |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        g = float(r["ref_gsd_m"]) if r.get("ref_gsd_m") else None
        med = r.get("residual_median_px")
        med_m = f" ({float(med) * g:.3f})" if (med and g) else ""
        L.append(f"| `{r['pair_id']}` | {_f(r['window_lat'], 4)}, {_f(r['window_lon'], 4)} | "
                 f"{r.get('d_sun_azimuth_deg') or 'n/a'} | {r.get('scale_ratio') or 'n/a'} | {r['n_matches']} | "
                 f"{r['inliers']} | {_f(r['inlier_ratio'])} | {_f(r['grid_coverage_fraction'], 2)} | "
                 f"{_f(med)}{med_m} | {_f(r.get('holdout_inlier_rmse_px'))} | {r['verified']} / {r['no_evidence']} | "
                 f"{r['verdict']} | {r['method_declared']} | {_f(r.get('archive_offset_m'), 1)} |")
    return L + [""]


def main(argv=None):
    real_rows = _rows(REAL)
    latest, counts = _latest(real_rows)
    # A pair whose latest row says INVALIDATED is withdrawn (the row says why); it is not shown.
    reg = [r for r in latest.values() if not r["pair_id"].startswith("loop_")
           and (r.get("verdict") or "") != "INVALIDATED"]
    loops = [r for r in latest.values() if r["pair_id"].startswith("loop_")]
    L = ["# SIH26166 - evaluation report", "",
         f"Generated {_dt.datetime.now().isoformat(timespec='minutes')} from commit `{_git()}` by "
         f"`python -m ops.make_report`. **Do not edit by hand** - every number below is read from "
         f"the evidence files named in each section.", "",
         "All pixel figures are on the REFERENCE image's grid, with its metres stated. Real pairs "
         "have no exact ground truth: accuracy on them is reported as held-out residuals (the 20 % "
         "of matches the fit never saw) and as loop closure. `residual_px` in results_log.csv is "
         "the RMSE over ALL held-out matches including outliers and is not quoted for real pairs.", ""]

    # --- products -----------------------------------------------------------------------
    d = _data()
    man = (_rows(d / "download_manifest_done.csv") + _rows(d / "nac_sweep_manifest_done.csv")
           + _rows(d / "nac_sac_manifest_done.csv")) if d else []
    if man:
        by = Counter(r["group"] for r in man)
        L += ["## Products downloaded (sha256 recorded)", "",
              f"{len(man)} files: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())) +
              f". Full list with URLs and sha256: `{d / 'download_manifest_done.csv'}` and "
              f"`nac_sweep_manifest_done.csv`, `nac_sac_manifest_done.csv`. The Chandrayaan-2 OHRC frame "
              f"`ch2_ohr_ncp_20200229T0739312111_d_img_d18` was already on disk (archive.org mirror).", ""]

    # --- cross-sensor, same ground -----------------------------------------------------
    ohrc_nac = sorted([r for r in reg if _kind(r) == "ohrc-nac" and not r.get("outcome")
                       and not r["pair_id"].startswith("sac_")], key=lambda r: r["pair_id"])
    L += section_pairs("Chandrayaan-2 OHRC → LRO NAC (cross-sensor, cross-mission)", ohrc_nac,
                       "Windows cut at 0.25 m (OHRC) and the NAC's native ~0.9-1.25 m over the same "
                       "ground on a south-polar-stereographic grid (`ops/cut_site_pairs.py`). "
                       "Archive offset = how far the registration moved the source from where the two "
                       "archives' (corrected) geometry put it - a property of the archives.")
    nac_nac = sorted([r for r in reg if _kind(r) == "nac-nac" and not r.get("outcome")], key=lambda r: r["pair_id"])
    if nac_nac:
        L += section_pairs("LRO NAC → LRO NAC (same sensor; loop legs)", nac_nac, "Same sensor - NOT cross-sensor.")
    # SAC's grids are the paper's (arXiv:2509.04775, Table 1), cited, not measured here
    for stem, pid, where, sac_grid in (
            ("sac_ohrc_nac_", "M1350459544RE", "equatorial, 13.3-13.9°S 25.2°E", "1.1179"),
            ("sac_polar_ohrc_nac_", "M165491149RE", "polar, 61.6-62.3°S 56.6°E", "0.88779")):
        rows = sorted([r for r in reg if r["pair_id"].startswith(stem)], key=lambda r: r["pair_id"])
        if not rows:
            continue
        gp = _jsonfile(ROOT / "data" / "pairs" / rows[0]["pair_id"] / "geometry_prior.json") or {}
        native = (gp.get("reference") or {}).get("resolution_mpp")
        grid = (f"NAC on a {rows[0]['ref_gsd_m']} m grid (its label resolution "
                f"{_f(native, 2)} m; the paper's NAC grid was {sac_grid} m, so pixel figures "
                f"differ in size as well as in kind)")
        geo = _jsonfile(d / "site_geometry" / f"{pid}.json") if d else None
        wide = (geo or {}).get("wide_offset") or {}
        field = (geo or {}).get("model") or {}
        pre = (f"Before cutting, the NAC's corner prior disagreed with the OHRC grid by "
               f"({wide['offset_m'][0]:+.0f}, {wide['offset_m'][1]:+.0f}) m ({wide['n_agree']}/"
               f"{wide['n_templates']} wide-search templates, {wide['polarity']} intensity); "
               if wide.get("apply") else "")
        if field:
            pre += (f"the 4 m correction field then fits {field.get('inliers')}/{field.get('n')} boxes at "
                    f"rms {_f(field.get('rms_m'), 1)} m ({(geo or {}).get('polarity')} intensity; "
                    f"`site_geometry/{pid}.json`). ")
        L += section_pairs(f"SAC's own benchmark pair ({where}): Chandrayaan-2 OHRC → LRO NAC `{pid}`", rows,
                           f"The pair in the problem setters' paper (arXiv:2509.04775, Table 1), cut by "
                           f"`ops/cut_pradan_pairs.py` on a local equirectangular grid: OHRC at "
                           f"~{rows[0]['src_gsd_m']} m, {grid}, same ground. {pre}Cross-sensor and "
                           f"cross-mission; both panchromatic - NOT multi-modal. The paper reports SuperGlue "
                           f"at 0.62 / 0.57 px (X / Y) on the equatorial pair and that only SuperGlue "
                           f"registered the polar one; its figure is an IN-SAMPLE control-point RMSE per "
                           f"axis, the table above is held-out (matches the fit never saw) - not the same "
                           f"measure. The same in-sample measure for ours follows.")
        ins = [r for r in rows if r.get("insample_n")]
        if ins:
            g = float(rows[0]["ref_gsd_m"])
            L += ["In-sample, per axis (SAC's measure): the MAGSAC++ inliers the matcher's H was "
                  "fitted to, graded under that H. MAGSAC++ keeps only matches within 3 px, so this "
                  "can only flatter; it is here for comparison with the paper, never as our accuracy.", "",
                  "| pair | inliers graded | RMSE X px (m) | RMSE Y px (m) | verdict |", "|---|---|---|---|---|"]
            for r in ins:
                x, y = r["insample_rmse_x_px"], r["insample_rmse_y_px"]
                L.append(f"| `{r['pair_id']}` | {r['insample_n']} | {_f(x)} ({float(x) * g:.3f}) | "
                         f"{_f(y)} ({float(y) * g:.3f}) | {r['verdict']} |")
            L.append("")
    other = sorted([r for r in reg if _kind(r) not in ("ohrc-nac", "nac-nac")], key=lambda r: r["pair_id"])
    sac = sorted([r for r in reg if _kind(r) == "ohrc-tmc2"], key=lambda r: r["pair_id"])
    if sac:
        L += section_pairs("SAC's benchmark site: Chandrayaan-2 OHRC → TMC-2 nadir (cross-sensor, same mission)", sac,
                           "OHRC frame `ch2_ohr_ncp_20210401T2357376656` (arXiv:2509.04775, Table 1), 13.1-13.9°S "
                           "25.2°E, vs TMC-2 pass `20250707T1853` (`ops/cut_pradan_pairs.py`). OHRC area-averaged "
                           "4×4 (~1.1 m) before resampling; TMC-2 ~5.6 m. Label sun: OHRC elevation 9.9°, TMC-2 "
                           "69.4°, azimuths 120° apart. Both panchromatic - NOT multi-modal; same mission - NOT "
                           "cross-mission.")
    fa = sorted([r for r in reg if _kind(r) == "tmc2-tmc2"], key=lambda r: r["pair_id"])
    if fa:
        L += section_pairs("Real viewpoint: TMC-2 fore (+25°) → aft (−25°), one pass (same sensor)", fa,
                           "Same instrument, same sun, seconds apart: only the viewing direction differs "
                           "(~50°). Relief parallax between the two (~0.93 × height) is not a homography - "
                           "compare with the synthetic parallax rows below. Same sensor - NOT cross-sensor.")
    mm = [r for r in reg if _kind(r) == "tc-mi"]
    if mm:
        L += section_pairs("Kaguya TC → Kaguya MI (cross-sensor; 749 nm visible and 1548 nm infrared)",
                           sorted(mm, key=lambda r: r["pair_id"]),
                           "Tier C rows are multi-modal (visible vs near-infrared). On them the declared "
                           "method is the global-correlation fallback; compare its archive offset with the "
                           "visible-band rows on the same windows.")

    iirs = sorted([r for r in reg if _kind(r) == "tc-iirs"], key=lambda r: r["pair_id"])
    if iirs:
        L += section_pairs("Kaguya TC → Chandrayaan-2 IIRS near-infrared (cross-sensor, cross-mission, multi-modal)", iirs,
                           "IIRS calibrated cube `ch2_iir_nci_20210621T1517513893` (bands 18 = 999 nm and 51 = 1555 nm, "
                           "streamed out of the zip by HTTP range - see ops/national_round/PRADAN_GUIDE.md) vs the Kaguya "
                           "TC ortho map at the 74 S site; IIRS ~89 m, TC ~7.4 m, 112-px IIRS windows. A 112-px frame "
                           "is too small for the per-cell area check, so the whole-frame check decides the verdict, and "
                           "it can only say `agrees` when the inliers also exceed 8 + 0.3 × matches (Brown & Lowe "
                           "2007); below that an agreeing peak is `unconfirmed` (`core/reliability.py` FRAME_ACCEPT_*).")
    rung_tc = sorted([r for r in reg if _kind(r) == "ohrc-tc"], key=lambda r: r["pair_id"])
    if rung_tc:
        L += section_pairs("Scale rung: Chandrayaan-2 OHRC → SELENE (Kaguya) TC ortho map (cross-sensor, cross-mission)",
                           rung_tc,
                           "The same OHRC source at 0.25 m against the TC ortho mosaic at 7.4 m (the scale column is "
                           "the ratio the pipeline bridges: it area-averages the OHRC down to the TC grid itself). "
                           "Windows ~1.5 km square, the most an axis-aligned square fits inside the ~2.8 km OHRC swath "
                           "at 74 S; 200-px references, 25-px trust cells. Both panchromatic - NOT multi-modal. The TC "
                           "mosaic has no single sun, so Δsun is n/a.")
    rung_lola = sorted([r for r in reg if _kind(r) == "ohrc-lola"], key=lambda r: r["pair_id"])
    if rung_lola:
        L += section_pairs("Declared-failure rung: OHRC → LOLA elevation rendered as shaded relief (Tier D, multi-modal)",
                           rung_lola,
                           "Same windows as the TC rung. LOLA `ldem_60s_60m` rendered under the OHRC's own derived sun, "
                           "so Δsun is 0 by construction and what remains is the modality and a 240× scale: the "
                           "reference is 25 × 25 px. The matcher finds nothing, the system says so and falls back; the "
                           "fallback's translation on a 25-px frame is not evidence of anything and the verdict stays "
                           "`unconfirmed`. This row exists to show the declared failure, not a registration.")
    # --- loops ----------------------------------------------------------------------------
    if loops:
        rms = [float(r["loop_rms_m"]) for r in loops]
        L += ["## Loop closure (OHRC → NAC A → NAC B vs OHRC → NAC B)", "",
              f"{len(loops)} closed loops. Loop RMS median **{st.median(rms):.3f} m**, max "
              f"{max(rms):.3f} m (`ops/loop_closure.py`). Loop closure cancels any error attached to "
              f"a single image (its geolocation, its own shading), so it measures correspondence "
              f"consistency, not absolute ground accuracy.", "",
              "| loop | window | RMS m | RMS px (B grid) | p90 px | methods | verdicts |", "|---|---|---|---|---|---|---|"]
        for r in sorted(loops, key=lambda r: r["pair_id"]):
            L.append(f"| `{r['pair_id']}` | {_f(r['window_lat'], 4)}, {_f(r['window_lon'], 4)} | "
                     f"{_f(r['loop_rms_m'])} | {_f(r['loop_rms_px'])} | {_f(r['loop_p90_px'])} | "
                     f"{r['method_declared']} | {r['verdict']} |")
        L.append("")

    # --- sun sweep --------------------------------------------------------------------------
    sweep = [r for r in reg if (r.get("outcome") or "").strip()]
    if sweep:
        from ops.sun_sweep import outcomes_v2
        v2 = outcomes_v2(sweep, _rows(LOG))
        moved = Counter((r["outcome"], v2[r["pair_id"]]) for r in sweep
                        if r["pair_id"] in v2 and v2[r["pair_id"]] != r["outcome"])
        bins = [(0, 10), (10, 30), (30, 60), (60, 90), (90, 120), (120, 181)]
        L += ["## Real sun-angle sweep (one OHRC frame vs LRO NAC frames)", "",
              "Outcome by image evidence, rule v2 (`ops/sun_sweep.py` docstring): the matcher is "
              "right when |NCC| of its warp against the reference is ≥ 0.30 and at least the archive "
              "alignment's |NCC| − 0.05; when neither reaches 0.30 the image cannot judge "
              "(inconclusive). |NCC| because opposite suns anti-correlate a correct alignment. "
              + (f"Derived from the logged NCCs; v2 moved {sum(moved.values())} of {len(sweep)} logged v1 "
                 "labels (" + ", ".join(f"{a} → {b} {n}" for (a, b), n in sorted(moved.items())) + "). "
                 if moved else f"All {len(sweep)} latest rows were logged under rule v2. ")
              + 
              "This sweep is NOT the trust layer's detection evidence - see the next section.", "",
              "| Δsun az (deg) | windows | NAC frames | registered & accepted | failed & caught | failed, not caught | correct but refused | inconclusive | median inliers |",
              "|---|---|---|---|---|---|---|---|---|"]
        for lo, hi in bins:
            b = [r for r in sweep if lo <= float(r["d_sun_azimuth_deg"]) < hi]
            if not b:
                continue
            c = Counter(v2.get(r["pair_id"], r["outcome"]) for r in b)
            L.append(f"| {lo}-{hi if hi < 181 else 180} | {len(b)} | {len({r['reference_product'] for r in b})} | "
                     f"{c['correct_accepted']} | {c['caught_failure']} | {c['missed_failure']} | "
                     f"{c['false_alarm']} | {c['inconclusive']} | {int(st.median([float(r['inliers'] or 0) for r in b]))} |")
        az = [float(r["d_sun_azimuth_deg"]) for r in sweep]
        L += ["", f"All bins: {len(sweep)} windows over {len({r['reference_product'] for r in sweep})} NAC "
                  f"frames, Δsun azimuth {min(az):.1f}-{max(az):.1f}°. Known issue 2: some windows are "
                  f"logged under two ids (`_sw` and plain) - rows, not distinct ground.", ""]

    # --- MiLOI (real multi-illumination NAC benchmark, network truth) -------------------------
    ml = _rows(ROOT / "evaluation" / "miloi_log.csv")
    tj = ROOT / "evaluation" / "miloi_truth.json"
    if ml and tj.exists():
        import json as _json
        from evaluation import miloi as _M
        truth = _json.loads(tj.read_text(encoding="utf-8"))
        # NOT `latest`: that name holds the real-pairs rows the footer counts (it printed
        # "234 rows (324 distinct pairs)" when this block overwrote it - claim-checker, 19 Sep).
        latest_mm = {}
        for r in ml:
            latest_mm[(r["pair_id"], r["method"])] = r
        ours = [r for (_, m), r in latest_mm.items() if m == _M.OURS_METHOD]
        n_run = sum(v["pairs_run"] for v in truth["scenes"].values())
        L += ["## MiLOI: real LROC NAC images of one ground under many suns (same sensor)", "",
              f"`evaluation/miloi.py` (Xie et al. 2025, github.com/Bin501/CNSFM @94cebaa). {n_run} pairs "
              f"matched; {len(ours)} have a truth. The tiles' map geometry is off by metres to hundreds of "
              f"metres, so truth is a per-image translation network built only from pairs where ours AND "
              f"SIFT agree within {_M.AGREE_PX} px with ≥{_M.EDGE_MIN_INLIERS} inliers each; a pair that is "
              f"itself an edge is scored leave-one-out, and a pair its network cannot reach has no truth "
              f"and is not scored. Same sensor (LROC NAC ↔ LROC NAC) - NOT cross-sensor.", "",
              "| scene | edges | images without truth | truth's own error (leave-one-out, px) |",
              "|---|---|---|---|"]
        for s, v in truth["scenes"].items():
            loo = v["loo_err_px"]
            L.append(f"| {s} | {len(v['edges'])} | {len(v['images_without_truth'])} | "
                     + (f"median {loo['median']:.2f}, max {loo['max']:.2f} (n={loo['n']})" if loo else
                        "**not measurable** - every edge is a bridge (no redundancy)") + " |")
        L += ["", "```"] + _M.table() + ["```", "",
              "Trust verdict against truth, ours (latest row per pair). Two definitions of \"right\", "
              "both shown: the MATCHER's homography against truth over the frame (what the trust layer "
              "judges - `outcome`), and the success rule of the table above (`rmse_gt_px` of the raw "
              "matches). S3's truth has no measurable error of its own.", "",
              f"| verdict | pairs | of which S3 | matcher H within {_M.SUCCESS_PX:g} px | rmse_gt_px under "
              f"{_M.SUCCESS_PX:g} px |", "|---|---|---|---|---|"]
        for v in ("agrees", "unconfirmed", "contradicted"):
            rs = [r for r in ours if r["verdict"] == v]
            ok = sum(1 for r in rs if r["matcher_err_px"] and float(r["matcher_err_px"]) < _M.SUCCESS_PX)
            ok2 = sum(1 for r in rs if r["rmse_gt_px"] and float(r["rmse_gt_px"]) < _M.SUCCESS_PX)
            L.append(f"| {v} | {len(rs)} | {sum(1 for r in rs if r['scene'] == 'S3')} | {ok} | {ok2} |")
        L.append("")

    # --- trust calibration ------------------------------------------------------------------
    tr = _rows(TRUST)
    if tr:
        by = defaultdict(list)
        for r in tr:
            by[float(r["displacement_m"])].append(r)
        L += ["## Trust layer on real imagery: planted confident-but-wrong registrations", "",
              f"`ops/trust_real_calibration.py`: {len({r['pair_id'] for r in tr})} real windows whose "
              f"registration is independently good; the true transform shifted by d metres and a match "
              f"set that agrees with the WRONG transform perfectly. d = 0 is the false-alarm rate.", "",
              "| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 |",
              "|---|---|---|---|---|"]
        for dm in sorted(by):
            t = by[dm]
            rate = sum(r["contradicted"] == "True" for r in t) / len(t)
            L.append(f"| {dm:g} | {st.median(float(r['displacement_px']) for r in t):.2f} | {len(t)} | "
                     f"{rate:.1%} | {st.mean(float(r['verified']) for r in t):.1f} |")
        L.append("")

    # --- synthetic (exact truth) ------------------------------------------------------------------
    log = _rows(LOG)
    vp = [r for r in log if r.get("tier") == "synthetic viewpoint"]
    if vp:
        import re as _re
        groups = defaultdict(list)
        for r in vp:
            m = _re.search(r"_t(\d+)a(\d+)(p?)$", r["pair_id"])
            if m and r.get("rmse_gt_px"):
                groups[(int(m[1]), int(m[2]), bool(m[3]))].append(float(r["rmse_gt_px"]))
        L += ["## Viewpoint (synthetic, exact truth)", "",
              "Off-nadir tilt applied to one image of a rendered pair (sun 15° apart), latest rows. "
              "With relief parallax ON the truth is a field and rmse_gt_px is measured against the "
              "plane homography, so it measures how far relief is from a homography, not a "
              "registration error.", "",
              "| tilt (deg) | parallax | runs | median rmse_gt_px | max |", "|---|---|---|---|---|"]
        for (t, az, par), v in sorted(groups.items(), key=lambda kv: (kv[0][2], kv[0][0])):
            v = v[-3:]
            L.append(f"| {t} | {'on' if par else 'off'} | {len(v)} | {st.median(v):.3f} | {max(v):.3f} |")
        L.append("")

    L += ["## Reproduce", "", "```",
          "python -m ops.cut_site_pairs --nac M1153871873LE --windows 8 --refit",
          "python -m ops.run_real_pairs \"site_ohrc_*\" --log",
          "python -m ops.loop_closure --a M1153871873LE --b M1363141432RE --tag t --log",
          "python -m ops.cut_site_pairs --correct-chain $(cat <data>/nac/sweep_order.txt)",
          "python -m ops.sun_sweep --windows 3 --log",
          "python -m ops.trust_real_calibration \"site_ohrc_m1153871873le_w*_t\" ... --log",
          "python -m ops.make_report", "```", "",
          f"Rows in real_pairs_log.csv: {len(real_rows)}: {len(latest)} distinct pair ids (latest row "
          f"wins) = {len(reg)} registered pairs + {len(loops)} loops + "
          f"{len(latest) - len(reg) - len(loops)} withdrawn (INVALIDATED). Rows in results_log.csv: "
          f"{len(log)}.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
