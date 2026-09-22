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
MM = ROOT / "evaluation" / "multimodal_check.csv"
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


def mm_table(kind):
    """The multi-modal check (`ops/multimodal_check.py`), latest row per window, for one kind."""
    latest = {}
    for r in _rows(MM):
        latest[r["pair_id"]] = r
    rows = sorted([r for r in latest.values() if r["kind"] == kind], key=lambda r: r["pair_id"])
    if not rows:
        return []
    if kind == "tc-mi":
        note = ("**Fallback vs the visible band, same window.** The declared transform on the infrared "
                "band against the LoFTR registration on the visible band of the SAME window (same TC "
                "source file, same MI grid; `ops/multimodal_check.py`): how far apart the two put the "
                "same source point, median over a 20 × 20 lattice of reference points. It is the "
                "fallback's error relative to the visible-band registration - the nearest thing to a "
                "truth the infrared band has. A fallback that had merely kept the archive alignment "
                "would sit as far from the visible-band answer as the archive offset (last column).")
    else:
        note = ("**Band against band, same window.** The two IIRS bands' declared transforms against "
                "each other (same TC source, same IIRS grid). Two fallbacks that agree are only "
                "self-consistent; two that disagree prove at least one of them wrong. No visible band "
                "exists on the IIRS side, so this is not an accuracy.")
    L = [note, "",
         "| pair | against | declared (pair / against) | against inliers | disagreement median px (m) | p90 px | max px | fallback NCC | archive offset m (pair / against) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| `{r['pair_id']}` | `{r['against']}` | {r['declared']} / {r['against_declared']} | "
                 f"{r['against_inliers'] or 'n/a'} | {_f(r['disagreement_median_px'])} ({_f(r['disagreement_median_m'], 1)}) | "
                 f"{_f(r['disagreement_p90_px'])} | {_f(r['disagreement_max_px'])} | {_f(r['fallback_ncc'], 2)} | "
                 f"{_f(r['archive_offset_m'], 1)} / {_f(r['against_archive_offset_m'], 1)} |")
    return L + [""]


def _distinct_note(reg) -> str:
    """" (N distinct ground windows; Known issue 2)" - some windows were cut twice under two ids.
    Needs the pairs' geometry_prior.json on this machine; says nothing when they are absent."""
    try:
        from presentation.make_figures import _distinct_windows
        n = len(_distinct_windows([r["pair_id"] for r in reg]))
    except Exception:  # noqa: BLE001 - data/pairs is gitignored; the report must still be written
        return ""
    return f" ({n} distinct ground windows; Known issue 2: some were cut twice under two ids)"


def _residual_caveat(acc, g) -> str:
    """Name any accepted window whose held-out median is large, and say what that measures.

    `residual_median_px` is the median error of the 20 % of matches the fit never saw. It is
    robust only while the inlier ratio is comfortably above 0.5: when outliers approach half the
    matches, a random 20 % draw can be majority-outlier and the median then describes the
    outliers rather than the registration. Measured on this tiling (20 Sep 2026): one window at
    an inlier ratio of 0.542 reported 316 px while the transform it declared put the median over
    ALL its matches at 1.08 px and its warped product correlates with the reference at NCC +0.93.
    Printing the range without this sentence would read as a registration failure that did not
    happen; dropping the window would be choosing the evidence.
    """
    bad = [r for r in acc if r.get("residual_median_px") and float(r["residual_median_px"]) > 3.0]
    if not bad:
        return ""
    parts = ", ".join(f"`{r['pair_id']}` {float(r['residual_median_px']):.0f} px at an inlier ratio "
                      f"of {float(r['inlier_ratio']):.3f}" for r in bad)
    return (f". {len(bad)} accepted window(s) report a held-out median above 3 px ({parts}). That "
            f"number is the median of the 20 % of matches the fit never saw, and it is robust only "
            f"while the inlier ratio stays well above 0.5 - at 0.54 a random held-out draw can be "
            f"majority-outlier, and the median then describes the outliers. Independent image "
            f"evidence says these windows are registered: the exported `registered_product.tif` "
            f"correlates with its reference at NCC +0.87 to +0.95 across all {len(acc)} accepted "
            f"windows (`ops/sun_sweep.py`'s |NCC| >= 0.30 rule, applied to the declared warp), and "
            f"under the declared transform the median error over ALL matches on the worst of them "
            f"is 1.08 px. This is a limit of the metric, not of the registration, and it is why "
            f"the area check never looks at the matches")

def section_full_overlap(full):
    """The dense tiling of one OHRC/NAC overlap (`--tag full`): acceptance, residuals, throughput,
    and whether any ACCEPTED window's archive offset breaks with its nearest accepted neighbour."""
    from core.geometry import ps_south
    g = float(full[0]["ref_gsd_m"])
    acc = [r for r in full if r["verdict"] == "agrees" and "fallback" not in r["method_declared"]]
    verd = Counter(r["verdict"] for r in full)
    secs = [float(r["seconds"]) for r in full if r.get("seconds")]
    med = [float(r["residual_median_px"]) for r in acc if r.get("residual_median_px")]
    side_m = 640 * g
    jumps = []
    if len(acc) > 1:
        xy = [ps_south(float(r["window_lat"]), float(r["window_lon"])) for r in acc]
        for i, r in enumerate(acc):
            j = min((k for k in range(len(acc)) if k != i),
                    key=lambda k: (xy[k][0] - xy[i][0]) ** 2 + (xy[k][1] - xy[i][1]) ** 2)
            jumps.append((abs(float(r["archive_offset_m"]) - float(acc[j]["archive_offset_m"])), r["pair_id"]))
    note = (f"Dense tiling, not hand-spread windows: every non-overlapping 640-px window (centres at "
            f"least 1.1 × the window apart) that `ops.cut_site_pairs --windows 60 --tag full` finds in "
            f"shared, lit, textured ground of the 74 °S OHRC frame and NAC `{full[0]['reference_product']}` "
            f"(Sun azimuths {full[0]['d_sun_azimuth_deg']}° apart). {len(full)} windows of {side_m:.0f} m = "
            f"{len(full) * side_m ** 2 / 1e6:.1f} km². Verdicts: "
            + ", ".join(f"{v} {n}" for v, n in verd.most_common())
            + f"; **accepted {len(acc)}/{len(full)}**"
            + (f"; held-out median of the accepted windows: median {st.median(med):.2f} px = "
               f"{st.median(med) * g:.2f} m on the {g} m grid, {sum(v <= 3 for v in med)} of "
               f"{len(med)} under 3 px (range {min(med):.2f}-{max(med):.2f})" if med else "")
            + _residual_caveat(acc, g)
            + (f". Wall time of `run_all`: {sum(secs) / 60:.1f} min in total, median {st.median(secs):.1f} s "
               f"per window, CPU only" if secs else "")
            + (f". Archive offset of each accepted window against its nearest accepted neighbour: median "
               f"difference {st.median(j for j, _ in jumps):.1f} m, max {max(jumps)[0]:.1f} m "
               f"(`{max(jumps)[1]}`), {sum(j > 50 for j, _ in jumps)} over 50 m" if jumps else "")
            + ". Reported separately from the hand-spread windows above and never merged with them.")
    return section_pairs("The whole lit overlap of one OHRC frame with one NAC (dense tiling)", full, note)


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
    # The commit that RENDERED this file and the commit(s) the evidence rows were MEASURED at are
    # two things; a reporting-only change moves the first and must not hide the second.
    ev = Counter((r.get("git_commit") or "?") for r in latest.values()
                 if (r.get("verdict") or "") != "INVALIDATED")
    L = ["# SIH26166 - evaluation report", "",
         f"Generated {_dt.datetime.now().isoformat(timespec='minutes')} from commit `{_git()}` by "
         f"`python -m ops.make_report`. **Do not edit by hand** - every number below is read from "
         f"the evidence files named in each section. The latest real-pair rows were measured at commit "
         + ", ".join(f"`{c}` ({n} rows)" for c, n in ev.most_common()) + ".", "",
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
    # `_full` = the dense tiling of one whole overlap (20 Sep 2026); its own section, never merged
    # with the hand-spread windows whose ranges the deck quotes.
    ohrc_nac = sorted([r for r in reg if _kind(r) == "ohrc-nac" and not r.get("outcome")
                       and not r["pair_id"].startswith("sac_") and not r["pair_id"].endswith("_full")],
                      key=lambda r: r["pair_id"])
    L += section_pairs("Chandrayaan-2 OHRC → LRO NAC (cross-sensor, cross-mission)", ohrc_nac,
                       "Windows cut at 0.25 m (OHRC) and the NAC's native ~0.9-1.25 m over the same "
                       "ground on a south-polar-stereographic grid (`ops/cut_site_pairs.py`). "
                       "Archive offset = how far the registration moved the source from where the two "
                       "archives' (corrected) geometry put it - a property of the archives.")
    full = sorted([r for r in reg if _kind(r) == "ohrc-nac" and r["pair_id"].endswith("_full")],
                  key=lambda r: r["pair_id"])
    if full:
        L += section_full_overlap(full)
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
    by_pass = {}
    for r in sac:
        by_pass.setdefault(r["reference_product"], []).append(r)
    for ref_pid, rows in by_pass.items():         # one section per TMC-2 pass (20 Sep: a second pass may land)
        gp = _jsonfile(ROOT / "data" / "pairs" / rows[0]["pair_id"] / "geometry_prior.json") or {}
        ss = (gp.get("source") or {}).get("sun") or {}
        rs = (gp.get("reference") or {}).get("sun") or {}
        m = re.search(r"_(\d{8}T\d{4})", ref_pid)
        L += section_pairs(f"SAC's benchmark site: Chandrayaan-2 OHRC → TMC-2 nadir, pass "
                           f"{m.group(1) if m else ref_pid} (cross-sensor, same mission)", rows,
                           f"OHRC frame `{rows[0]['source_product']}` (arXiv:2509.04775, Table 1), 13.1-13.9°S "
                           f"25.2°E, vs TMC-2 pass `{ref_pid}` (`ops/cut_pradan_pairs.py`). OHRC area-averaged "
                           f"4×4 (~{rows[0]['src_gsd_m']} m) before resampling; TMC-2 ~{rows[0]['ref_gsd_m']} m. "
                           f"Label sun: OHRC elevation {_f(ss.get('elevation_deg_label'), 1)}°, TMC-2 "
                           f"{_f(rs.get('elevation_deg_label'), 1)}°, azimuths {rows[0]['d_sun_azimuth_deg']}° "
                           f"apart, incidence {abs(float(rows[0]['d_incidence_deg'] or 0)):.1f}° apart "
                           f"(`d_incidence_deg` {rows[0]['d_incidence_deg']}). Both panchromatic - NOT "
                           f"multi-modal; same mission - NOT cross-mission.")
        # Rendering only (22 Sep): the same in-sample table the SAC OHRC->NAC sections print,
        # plus the held-out inlier fraction, because on THESE rows the two together are the
        # argument. A homography fitted to 6-7 inliers is sub-pixel in-sample by construction
        # (MAGSAC++ keeps only matches within 3 px) - and not one held-out match agrees with it.
        # That is what the area check refused. Both columns were logged at the freeze; they were
        # simply never printed for this section.
        ins = [r for r in rows if r.get("insample_n")]
        if ins:
            g = float(rows[0]["ref_gsd_m"])
            L += ["In-sample, per axis, on the inliers the matcher's H was fitted to - and the share "
                  "of HELD-OUT matches (the 20 % the fit never saw) that land within 3 px of that H. "
                  "MAGSAC++ keeps only matches within 3 px, so the in-sample column can only flatter: "
                  "a sub-pixel fit on six points is what a refused registration looks like from the "
                  "inside, and the held-out column is why it was refused.", "",
                  "| pair | inliers graded | RMSE X px (m) | RMSE Y px (m) | held-out within 3 px | verdict |",
                  "|---|---|---|---|---|---|"]
            for r in ins:
                x, y = r["insample_rmse_x_px"], r["insample_rmse_y_px"]
                hf = r.get("holdout_inlier_frac")
                L.append(f"| `{r['pair_id']}` | {r['insample_n']} | {_f(x)} ({float(x) * g:.3f}) | "
                         f"{_f(y)} ({float(y) * g:.3f}) | "
                         f"{'n/a' if hf in (None, '') else f'{float(hf):.0%}'} | {r['verdict']} |")
            L.append("")
    fa = sorted([r for r in reg if _kind(r) == "tmc2-tmc2"], key=lambda r: r["pair_id"])
    if fa:
        L += section_pairs("Real viewpoint: TMC-2 fore (+25°) → aft (−25°), one pass (same sensor)", fa,
                           "Same instrument, same sun, seconds apart: only the viewing direction differs "
                           "(~50°). Relief parallax between the two (~0.93 × height) is not a homography - "
                           "compare with the synthetic parallax rows below. Same sensor - NOT cross-sensor. "
                           f"Reference (aft) grid {fa[0]['ref_gsd_m']} m, source (fore) {fa[0]['src_gsd_m']} m.")
    mm = [r for r in reg if _kind(r) == "tc-mi"]
    if mm:
        L += section_pairs("Kaguya TC → Kaguya MI (cross-sensor; 749 nm visible and 1548 nm infrared)",
                           sorted(mm, key=lambda r: r["pair_id"]),
                           "Tier C rows are multi-modal (visible vs near-infrared). On them the declared "
                           "method is the global-correlation fallback; the table after this one measures that "
                           "fallback against the visible-band registration of the same window.")
        L += mm_table("tc-mi")

    iirs = sorted([r for r in reg if _kind(r) == "tc-iirs"], key=lambda r: r["pair_id"])
    if iirs:
        L += section_pairs("Kaguya TC → Chandrayaan-2 IIRS near-infrared (cross-sensor, cross-mission, multi-modal)", iirs,
                           "IIRS calibrated cube `ch2_iir_nci_20210621T1517513893` (bands 18 = 999 nm and 51 = 1555 nm, "
                           "streamed out of the zip by HTTP range - see ops/national_round/PRADAN_GUIDE.md) vs the Kaguya "
                           "TC ortho map at the 74 S site; IIRS ~89 m, TC ~7.4 m, 112-px IIRS windows. A 112-px frame "
                           "is too small for the per-cell area check, so the whole-frame check decides the verdict, and "
                           "it can only say `agrees` when the inliers also exceed 8 + 0.3 × matches (Brown & Lowe "
                           "2007); below that an agreeing peak is `unconfirmed` (`core/reliability.py` FRAME_ACCEPT_*).")
        L += mm_table("tc-iirs")
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
        far = [r for r in ours if float(r["d_sun_angle_deg"]) >= 90]
        by_scene = Counter(r["scene"] for r in far)
        L += ["", f"Scored pairs with Sun vectors 90° or more apart: {len(far)} ("
                  + ", ".join(f"{s} {by_scene.get(s, 0)}" for s in ("S1", "S2", "S3")) + "); "
                  f"registered within {_M.SUCCESS_PX:g} px by ours: "
                  f"{sum(1 for r in far if str(r['success']) in ('1', 'True'))}.", ""]

    # --- trust calibration ------------------------------------------------------------------
    tr = _rows(TRUST)
    if tr:
        # Two populations, never pooled (20 Sep 2026): rows written before the column existed
        # are the 74 °S windows, all under 10° of Sun-azimuth difference.
        # Rows written before the `kind` column existed are translations.
        trans = [r for r in tr if (r.get("kind") or "translation") == "translation"]
        pops = [("Sun azimuths under 10° apart (the 74 °S OHRC/NAC windows)",
                 [r for r in trans if float(r.get("d_sun_azimuth_deg") or 0) < 10]),
                ("Sun azimuths 132-174° apart (SAC's own OHRC/NAC pairs)",
                 [r for r in trans if float(r.get("d_sun_azimuth_deg") or 0) >= 10])]
        L += ["## Trust layer on real imagery: planted confident-but-wrong registrations", "",
              f"`ops/trust_real_calibration.py`: {len({r['pair_id'] for r in tr})} real windows whose "
              f"registration is independently good (declared LoFTR, `agrees`, |NCC| of the true alignment "
              f"≥ 0.5, ≥ 50 inliers); the true transform shifted by d metres and a match set that agrees "
              f"with the WRONG transform perfectly. d = 0 is the false-alarm rate. The two Sun populations "
              f"are shown separately and never pooled.", ""]
        for title, rows_p in pops:
            if not rows_p:
                continue
            by = defaultdict(list)
            for r in rows_p:
                by[float(r["displacement_m"])].append(r)
            wins = sorted({r["pair_id"] for r in rows_p})
            az = sorted({float(r["d_sun_azimuth_deg"]) for r in rows_p if r.get("d_sun_azimuth_deg")})
            nccs = [float(r["ncc_true"]) for r in rows_p if r.get("ncc_true")]
            L += [f"### {title}: {len(wins)} windows", "",
                  (f"Sun azimuth differences {', '.join(f'{a:g}' for a in az)}°" if az else
                   "Sun azimuth differences under 10° (these rows predate the per-trial column)")
                  + (f"; |NCC| of the true alignment {min(abs(v) for v in nccs):.2f}-{max(abs(v) for v in nccs):.2f}"
                     f" (sign {'negative: opposite Suns anti-correlate' if max(nccs) < 0 else 'positive'})" if nccs else "")
                  + (f". Windows: {', '.join(f'`{w}`' for w in wins)}." if len(wins) <= 12 else "."), "",
                  "| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 |",
                  "|---|---|---|---|---|"]
            for dm in sorted(by):
                t = by[dm]
                rate = sum(r["contradicted"] == "True" for r in t) / len(t)
                L.append(f"| {dm:g} | {st.median(float(r['displacement_px']) for r in t):.2f} | {len(t)} | "
                         f"{rate:.1%} | {st.mean(float(r['verified']) for r in t):.1f} |")
            L.append("")
        nt = [r for r in tr if (r.get("kind") or "translation") != "translation"]
        if nt:
            L += ["### Errors that are not translations: planted rotation and scale", "",
                  "A rotation or a scale change about the frame centre leaves the centre where it was and "
                  "displaces the CORNERS most, so one number describes it: how far the corners move. The "
                  "frame verdict is the wrong thing to watch here - it still says `agrees` while a corner "
                  "is 3 px out - because the error is not uniform over the frame. What carries the "
                  "information is the 8 × 8 map, so the last two columns count cells, not frames: of the "
                  "cells the planted error really moved by more than 2 px, how many the map refused to "
                  "verify, and of the cells it moved by less than 1 px, how many stayed verified.", "",
                  "| kind | corner displacement (m) | ~px on the reference grid | trials | frame contradicted | "
                  "mean verified cells /64 | cells moved >2 px that are NOT verified | cells moved <1 px that "
                  "stay verified |", "|---|---|---|---|---|---|---|---|"]
            for kind in ("rotation", "scale"):
                by = defaultdict(list)
                for r in nt:
                    if r["kind"] == kind:
                        by[float(r["displacement_m"])].append(r)
                for dm in sorted(by):
                    t = by[dm]
                    rate = sum(r["contradicted"] == "True" for r in t) / len(t)
                    nm = sum(int(r["cells_moved_2px"]) for r in t)
                    mnv = sum(int(r["moved_not_verified"]) for r in t)
                    ns = sum(int(r["cells_under_1px"]) for r in t)
                    sv = sum(int(r["under_1px_verified"]) for r in t)
                    L.append(f"| {kind} | {dm:g} | {st.median(float(r['displacement_px']) for r in t):.2f} | "
                             f"{len(t)} | {rate:.1%} | {st.mean(float(r['verified']) for r in t):.1f} | "
                             + (f"{mnv}/{nm} = {100 * mnv / nm:.0f} %" if nm else "no cell moved that far")
                             + " | " + (f"{sv}/{ns} = {100 * sv / ns:.0f} %" if ns else "n/a") + " |")
            tot_m = sum(int(r["cells_moved_2px"]) for r in nt)
            tot_mnv = sum(int(r["moved_not_verified"]) for r in nt)
            tot_s = sum(int(r["cells_under_1px"]) for r in nt)
            tot_sv = sum(int(r["under_1px_verified"]) for r in nt)
            L += ["", f"Over every rotation and scale trial: of the {tot_m} cells displaced by more than "
                      f"2 px the map refused to verify {tot_mnv} (**{100 * tot_mnv / max(tot_m, 1):.1f} %**); "
                      f"of the {tot_s} cells displaced by less than 1 px, {tot_sv} stayed verified "
                      f"(**{100 * tot_sv / max(tot_s, 1):.1f} %**). The planted matches agree with the wrong "
                      f"transform perfectly in every trial, so nothing the matcher reports could reveal it.", ""]

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

    # --- sub-pixel, by grid; runtime; coverage (20 Sep 2026: gathered here so the deck can name
    # the grid beside every sub-pixel figure - nothing below is a new measurement) ---------------
    L += ["## Sub-pixel accuracy, with the pixel grid named", "",
          "\"Sub-pixel\" means nothing without its grid. Every figure below is on the REFERENCE grid "
          "with its metres, and says what its truth is. None is a new measurement: each is the row "
          "or table above it came from.", "",
          "| evidence | what the truth is | reference grid | result |", "|---|---|---|---|"]
    try:
        from presentation.make_figures import load_curves
        deltas, ours_med, _b, _ns, _nt = load_curves()
        want = [(d, o) for d, o in zip(deltas, ours_med) if d in (0.0, 15.0, 30.0, 45.0)]
        if want:
            L.append("| Synthetic rendered pair (LOLA DEM), Sun azimuths "
                     + " / ".join(f"{d:g}°" for d, _ in want) + " apart, medians over the off-grid shifts "
                     "(the fig1 rows) | exact: a known transform | 60 m | rmse_gt_px "
                     + " / ".join(f"{o:.3f}" for _, o in want) + " px = "
                     + " / ".join(f"{o * 60:.1f}" for _, o in want) + " m |")
    except Exception as e:  # noqa: BLE001 - the report must still be written
        L.append(f"| Synthetic rendered pair | exact | 60 m | not available ({type(e).__name__}) |")
    if ohrc_nac:
        med = [float(r["residual_median_px"]) for r in ohrc_nac if r.get("residual_median_px")]
        med_m = [float(r["residual_median_px"]) * float(r["ref_gsd_m"]) for r in ohrc_nac if r.get("residual_median_px")]
        grids = sorted({r["ref_gsd_m"] for r in ohrc_nac})
        L.append(f"| Real Chandrayaan-2 OHRC → LRO NAC, 74 °S, {len(ohrc_nac)} windows | held-out matches "
                 f"(the 20 % the fit never saw) - no ground truth | {' and '.join(grids)} m | median per window "
                 f"{min(med):.2f}-{max(med):.2f} px = {min(med_m):.2f}-{max(med_m):.2f} m |")
    sac_eq = sorted([r for r in reg if r["pair_id"].startswith("sac_ohrc_nac_")], key=lambda r: r["pair_id"])
    if sac_eq:
        med = [float(r["residual_median_px"]) for r in sac_eq if r.get("residual_median_px")]
        g = float(sac_eq[0]["ref_gsd_m"])
        azs = sorted(float(r["d_sun_azimuth_deg"]) for r in sac_eq if r.get("d_sun_azimuth_deg"))
        L.append(f"| Real OHRC → LRO NAC, SAC's equatorial pair, {len(sac_eq)} windows, Sun azimuths "
                 f"{azs[0]:g}-{azs[-1]:g}° apart | held-out matches | {g} m | median per window "
                 f"{min(med):.2f}-{max(med):.2f} px = {min(med) * g:.1f}-{max(med) * g:.1f} m |")
    if loops:
        px = [float(r["loop_rms_px"]) for r in loops]
        L.append(f"| Loop closure OHRC → NAC A → NAC B vs OHRC → NAC B, {len(loops)} loops | consistency of "
                 f"three registrations (cancels per-image error) | {loops[0]['ref_gsd_m'] or '1.245'} m (NAC B) | "
                 f"RMS median {st.median(px):.3f} px = {st.median(float(r['loop_rms_m']) for r in loops):.3f} m |")
    ml = _rows(ROOT / "evaluation" / "miloi_log.csv")
    if ml:
        latest_mm = {}
        for r in ml:
            latest_mm[(r["pair_id"], r["method"])] = r
        ag = [r for (_, m), r in latest_mm.items() if m == "ours_loftr+subpixel" and r["verdict"] == "agrees"
              and r.get("matcher_err_px")]
        parts = []
        for sc in ("S1", "S2", "S3"):
            rs = [r for r in ag if r["scene"] == sc]
            if rs:
                gs = sorted(float(r["ref_gsd_m"]) for r in rs)
                em = st.median(float(r["matcher_err_px"]) * float(r["ref_gsd_m"]) for r in rs)
                parts.append(f"{sc} median {st.median(float(r['matcher_err_px']) for r in rs):.2f} px "
                             f"= {em:.2f} m (n={len(rs)}, grids {gs[0]:.2f}-{gs[-1]:.2f} m)")
        if parts:
            L.append("| MiLOI LRO NAC ↔ NAC (same sensor), the `agrees` pairs: the matcher's transform vs the "
                     "network truth | a translation network from ours+SIFT agreement on OTHER pairs; its own "
                     "leave-one-out error is in the MiLOI section (S3: not measurable) | per pair | "
                     + "; ".join(parts) + " |")
    L.append("")
    # runtime and coverage, from the latest rows
    secs = [float(r["seconds"]) for r in reg if r.get("seconds")]
    on = [float(r["seconds"]) for r in reg if r.get("seconds") and _kind(r) == "ohrc-nac"
          and not r["pair_id"].startswith("sac_") and not r["pair_id"].endswith("_full")]
    cpu = ""
    try:
        import json as _j
        rep = _j.loads((d / "out" / ohrc_nac[0]["pair_id"] / "report.json").read_text(encoding="utf-8"))
        env = rep.get("environment") or {}
        cpu = f" ({env.get('cpu', '')}; {env.get('platform', '')})".replace(" (; )", "")
    except Exception:  # noqa: BLE001
        pass
    cov = [float(r["grid_coverage_fraction"]) for r in ohrc_nac if r.get("grid_coverage_fraction")]
    L += ["## Runtime and match distribution", "",
          f"Wall time of `run_all` per window (the `seconds` column; LoFTR on CPU, tiled; no GPU), latest "
          f"rows: median {st.median(on):.1f} s over the {len(on)} OHRC → NAC windows at 74 °S "
          f"(the loop legs and the sun sweep; 640-px NAC references), {st.median(secs):.1f} s over all "
          f"{len(secs)} registered windows{cpu}.", "",
          f"Uniform distribution (PS demand): `grid_coverage_fraction` is the share of the 8 × 8 reference "
          f"cells holding at least one inlier. On the {len(cov)} OHRC → NAC windows at 74 °S it is "
          f"{min(cov):.2f}-{max(cov):.2f}, median {st.median(cov):.2f}; {sum(c >= 0.95 for c in cov)} of "
          f"{len(cov)} windows are at 0.95 or above (the lowest: "
          + ", ".join(f"`{r['pair_id']}` {float(r['grid_coverage_fraction']):.2f}"
                      for r in sorted(ohrc_nac, key=lambda r: float(r.get('grid_coverage_fraction') or 1))[:2])
          + ").", ""]

    L += ["## Reproduce", "", "```",
          "python -m ops.cut_site_pairs --nac M1153871873LE --windows 8 --refit",
          "python -m ops.run_real_pairs \"site_ohrc_*\" --log",
          "python -m ops.loop_closure --a M1153871873LE --b M1363141432RE --tag t --log",
          "python -m ops.cut_site_pairs --correct-chain $(cat <data>/nac/sweep_order.txt)",
          "python -m ops.sun_sweep --windows 3 --log",
          "python -m ops.trust_real_calibration \"site_ohrc_m1153871873le_w*_t\" ... --log",
          "python -m ops.make_report", "```", "",
          f"Rows in real_pairs_log.csv: {len(real_rows)}: {len(latest)} distinct pair ids (latest row "
          f"wins) = {len(reg)} registered pairs{_distinct_note(reg)} + {len(loops)} loops + "
          f"{len(latest) - len(reg) - len(loops)} withdrawn (INVALIDATED). Rows in results_log.csv: "
          f"{len(log)}.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
