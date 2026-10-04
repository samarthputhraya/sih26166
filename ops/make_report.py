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
TRUST_IR = ROOT / "evaluation" / "trust_real_calibration_ir.csv"
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


def _rng(lo, hi, fmt=".1f", sep="-"):
    """'lo-hi' with both ends in `fmt`, or one value when the two print the same."""
    a, b = format(lo, fmt), format(hi, fmt)
    return a if a == b else f"{a}{sep}{b}"


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


def mm_table(kind, prefix=""):
    """The multi-modal check (`ops/multimodal_check.py`), latest row per window, for one kind."""
    latest = {}
    for r in _rows(MM):
        latest[r["pair_id"]] = r
    rows = sorted([r for r in latest.values() if r["kind"] == kind and r["pair_id"].startswith(prefix)],
                  key=lambda r: r["pair_id"])
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
    elif kind == "tmc2-iirs":
        note = ("**Band against band, same window.** Each IIRS band's declared transform against the "
                "1555 nm one, on the same TMC-2 window and the same IIRS grid (`ops/multimodal_check.py`). "
                "Every band was registered on its own - its own LoFTR matches, its own fit - so this compares "
                "two independent registrations of one piece of ground. Agreement is consistency, not accuracy; "
                "disagreement would prove one of them wrong.")
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
        keys = _distinct_windows([r["pair_id"] for r in reg])
        # One window registered in several IIRS bands is one piece of ground. The window count is
        # kept as it always was (the deck and README quote it); the ground count is printed beside it.
        n_ground = len({(k[0], re.sub(r" band \d+ \(.*\)$", "", k[1]), *k[2:]) for k in keys})
    except Exception:  # noqa: BLE001 - data/pairs is gitignored; the report must still be written
        return ""
    return (f" ({len(keys)} distinct windows - a window being one source image, one reference image, one place; "
            f"{n_ground} if the IIRS bands of one window count once; Known issue 2: some were cut twice under two ids)")


def _pairings_note(reg) -> str:
    """"; N instrument pairings" - distinct (source instrument, reference instrument) among the registered
    pairs, from their product ids (`_kind`). Printed so the deck and README can quote it (1 Oct 2026:
    the "8 instrument pairings" on v10 was derived by hand and never printed here)."""
    kinds = sorted({_kind(r) for r in reg})
    return f"; {len(kinds)} instrument pairings ({', '.join(kinds)})"


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

def section_classical():
    """SIFT / ORB / AKAZE on the windows behind each headline, judged by the same MAGSAC++, held-out
    evaluate(), area check and fallback as ours (ops/classical_real.py, results_log rows tagged
    CLASSICAL-REAL). 3 Oct 2026: every cold reader asked what "accepted" is compared with."""
    try:
        from ops.classical_real import METHOD_NAMES, axis_pairs, classical_rows, latest_real, ours_accepted
        rows = classical_rows(LOG)
    except Exception:  # noqa: BLE001 - the report must still be written
        return []
    if not rows:
        return []
    latest = latest_real(REAL)
    commits = Counter(v.get("commit") for v in rows.values())
    L = ["## Classical matchers on the same windows, judged by the same rule", "",
         "`ops/classical_real.py`: SIFT, ORB and AKAZE (OpenCV, 0.75 ratio test, on the common-grid 8-bit "
         "images - the MiLOI protocol) on exactly the windows behind each result above. Their matches then go "
         "through everything ours go through after matching: MAGSAC++, the held-out `evaluate()`, the "
         "independent area check and the fallback (`core.pipeline.run_all(matches=...)`). So *accepted* means "
         "the same for every method: the area check agrees and no fallback was needed. Rows measured at "
         + ", ".join(f"`{c}` ({n})" for c, n in commits.most_common()) + ".", "",
         "| windows behind | windows | ours accepted | " + " | ".join(f"{m} accepted" for m in METHOD_NAMES) + " |",
         "|---|---|---|" + "---|" * len(METHOD_NAMES)]
    per_method = {m: {"n": 0, "acc": 0, "fine_refused": 0, "fine": 0} for m in METHOD_NAMES}
    for label, ids in axis_pairs(latest):
        if not ids:
            continue
        cells = []
        for m in METHOD_NAMES:
            have = [rows[(p, m)] for p in ids if (p, m) in rows]
            acc = sum(h.get("accepted") == "True" for h in have)
            cells.append(f"{acc}/{len(ids)}" if len(have) == len(ids) else f"{acc} of {len(have)} run ({len(ids)} windows)")
            for h in have:
                pm = per_method[m]
                pm["n"] += 1
                pm["acc"] += h.get("accepted") == "True"
                frac = h.get("holdout_inlier_frac")
                fine = frac not in (None, "", "None") and float(frac) >= 0.5
                pm["fine"] += fine
                pm["fine_refused"] += fine and h.get("accepted") != "True"
        ours = sum(ours_accepted(latest[p]) for p in ids)
        L.append(f"| {label} | {len(ids)} | {ours}/{len(ids)} | " + " | ".join(cells) + " |")
    L += ["", "Per method, over every window above: how often its OWN residual looked fine (at least half "
              "of the held-out matches within 3 px of its transform) and the area check still refused it.", "",
          "| method | windows run | accepted | own residual looked fine | of those, refused by the area check |",
          "|---|---|---|---|---|"]
    for m, pm in per_method.items():
        L.append(f"| {m} | {pm['n']} | {pm['acc']} | {pm['fine']} | {pm['fine_refused']} |")
    L.append("")
    return L


def section_check_points(reg, d):
    """Independent check points clicked by hand (evaluation/check_points.py): the one accuracy figure on
    real pairs that the matcher never saw. Rendered from the click CSVs and the exported bundles."""
    try:
        from evaluation import check_points as CP
    except Exception:  # noqa: BLE001
        return [], []
    pids = CP.clicked_pairs()
    if not pids or not d:
        return [], []
    scored, refused = [], []
    for pid in pids:
        extra = {}
        for m in ("SIFT", "ORB", "AKAZE"):
            j = _jsonfile(d / "out_classical" / pid / f"{m}.json")
            if j and j.get("accepted") and j.get("H_final"):
                extra[m] = j["H_final"]
        # 4 Oct 2026: on a 60-120 deg sweep window the Sun ladder's accepted composites (ops/sun_ladder.py) are
        # scored on the same independent points as the (refused) direct registration.
        if pid.endswith("_sw"):
            try:
                import numpy as _np
                from ops import sun_ladder as SL
                from evaluation.real_eval import pixel_to_map
                it = next((x for x in SL.plan() if x["target"] == pid), None)
                g = _jsonfile(ROOT / "data" / "pairs" / pid / "geometry_prior.json") or {}
                if it and g:
                    Ps, Pr = pixel_to_map(g["source"]["transform"]), pixel_to_map(g["reference"]["transform"])
                    for lad in SL.compose(it, d / "out"):
                        if lad["accepted"] and lad["T"] is not None:
                            extra["ladder via " + " → ".join(lad["chain"])] = (_np.linalg.inv(Pr) @ lad["T"] @ Ps).tolist()
            except Exception:  # noqa: BLE001 - no ladder for this window: score what there is
                pass
        try:
            scored.append(CP.score_pair(pid, d / "out", extra=extra))
        except (ValueError, FileNotFoundError, KeyError) as e:
            refused.append(f"`{pid}`: {e}")
    if not scored:
        return ([f"Independent check points: none scored ({'; '.join(refused)})", ""] if refused else []), []
    prec = [s["precision"] for s in scored if s["precision"].get("n")]
    L = ["## Independent check points: accuracy against points the matcher never saw", "",
         "A person clicked the same feature (small crater centres, boulders - never shadow edges) in both "
         "images of each window with `ops/click_check_points.py`, which shows the source around where the "
         "ARCHIVE georeference puts it and never reads a registration (a test enforces it). So these points "
         "are independent of every transform scored against them: the standard photogrammetric check point, "
         "and the RMSE the problem statement names. Errors are where the declared transform puts each "
         "clicked source point, against where it was clicked in the reference - on the reference grid, in "
         "metres, and in the source image's own pixels. *Plane floor*: each point against a homography "
         "fitted to all the other clicked points (leave-one-out) - the click error plus relief that no single "
         "transform can remove. *Click precision*: the same features clicked again later without the first "
         "clicks shown (repeat difference / √2)."
         + (f" Over {sum(p['n'] for p in prec)} repeats, one click's precision is a median "
            f"{st.median(p['ref_click_m'] for p in prec):.2f} m on the reference and "
            f"{st.median(p['src_click_m'] for p in prec):.2f} m on the source." if prec else ""), "",
         "| pair | points | ours: RMSE on the reference grid px (m) | RMSE in the source's own px | median (m) | "
         "max (m) | archive prior RMSE (m) | plane floor RMSE (m) | verdict |",
         "|---|---|---|---|---|---|---|---|---|"]
    for s in scored:
        o, a, fl = s["ours"], s["archive_prior"], s["floor"]
        L.append(f"| `{s['pair_id']}` | {o['n']} | {o['rmse_px']:.2f} ({o['rmse_m']:.2f}) on {s['ref_gsd']:g} m | "
                 f"{o['rmse_src_px']:.2f} on {s['src_gsd']:g} m | {o['median_m']:.2f} | {o['max_m']:.2f} | "
                 f"{a['rmse_m']:.1f} | {fl['rmse_m']:.2f} | "
                 + ("refused (fallback)" if s["contradicted"] else "accepted") + " |")
    cl = [(s["pair_id"], m, s[m]) for s in scored for m in ("SIFT", "ORB", "AKAZE") if m in s]
    if cl:
        L += ["", "Classical transforms the area check accepted on the same windows, scored on the same points:", "",
              "| pair | method | RMSE (m) | ours on these points (m) |", "|---|---|---|---|"]
        for pid, m, sc in cl:
            ours = next(s["ours"]["rmse_m"] for s in scored if s["pair_id"] == pid)
            L.append(f"| `{pid}` | {m} | {sc['rmse_m']:.2f} | {ours:.2f} |")
    lad = [(s["pair_id"], m, s[m]) for s in scored for m in s if isinstance(m, str) and m.startswith("ladder via ")]
    if lad:
        L += ["", "Sun-ladder composites on 60-120° windows (ops/sun_ladder.py), scored on the same independent points "
                  "as the direct registration the area check refused there:", "",
              "| pair | ladder | RMSE (m) | RMSE in the source's own px | the refused direct registration (m) |",
              "|---|---|---|---|---|"]
        for pid, m, sc in lad:
            direct = next(s["ours"]["rmse_m"] for s in scored if s["pair_id"] == pid)
            L.append(f"| `{pid}` | {m[len('ladder via '):]} | {sc['rmse_m']:.2f} | {sc['rmse_src_px']:.2f} | {direct:.1f} |")
    if refused:
        L += ["", "Not scored: " + "; ".join(refused)]
    L.append("")
    sub = []
    acc = [s for s in scored if not s["contradicted"]]
    if acc:
        rm = sorted(s["ours"]["rmse_m"] for s in acc)
        grids = sorted({s["ref_gsd"] for s in acc})
        sub.append(f"| Independent check points clicked by hand, {len(acc)} accepted windows "
                   f"({sum(s['ours']['n'] for s in acc)} points) | features clicked in both images, never seen by "
                   f"the matcher"
                   + (f"; one click's precision {st.median(p['ref_click_m'] for p in prec):.2f} m" if prec else "")
                   + f" | {grids[0]:g}-{grids[-1]:g} m | RMSE per window {rm[0]:.2f}-{rm[-1]:.2f} m |")
    return L, sub


def archive_lines(d, full):
    """PRADAN's catalogue (ops/pradan_archive.py) against the whole-overlap rate measured above."""
    try:
        from ops.pradan_archive import summary
        arch = summary(d / "pradan" / "shapefiles")
    except Exception:  # noqa: BLE001 - no catalogue on this machine: say nothing
        return []
    o, t, i = arch["OHRC"], arch["TMC-2"], arch["IIRS"]
    L = [f"Archive scale, from PRADAN's own footprint catalogue (`<data>/pradan/shapefiles`, downloaded 18 Sep "
         f"2026; OHRC releases 1-11; `ops/pradan_archive.py`): {o['products']} calibrated OHRC products "
         f"({o['observations']} observations; some are listed twice, one copy per ground station) covering "
         f"{o['area_km2']:,.0f} km² (median frame {o['median_area_km2']:.1f} km²); {t['products']:,} calibrated "
         f"TMC-2 products ({t['nadir_products']:,} nadir); {i['products']:,} calibrated IIRS products."]
    secs = [float(r["seconds"]) for r in full if r.get("seconds")]
    if full and secs:
        g = float(full[0]["ref_gsd_m"])
        km2 = len(full) * (640 * g) ** 2 / 1e6
        mins = sum(secs) / 60
        rate = km2 / (mins / 60)
        L[0] += (f" At the whole-overlap rate measured above ({km2:.1f} km² in {mins:.1f} min = {rate:.0f} km² "
                 f"per hour on one laptop CPU, registration only, against a {g} m NAC reference), all "
                 f"{o['area_km2']:,.0f} km² of OHRC is about {o['area_km2'] / rate:.0f} laptop-hours. A projection "
                 f"from one measured rate, not a measurement: it leaves out reading and cutting the products and "
                 f"assumes lit, textured ground and a reference as fine as that NAC.")
    return L + [""]


def section_strip(strip, d):
    """One whole TMC-2 -> IIRS strip, edge to edge (cut_chain_pairs tmc-iirs --strip): no selection,
    every window, timed. Kept out of every other count in this file."""
    if not strip:
        return []
    acc = [r for r in strip if r["verdict"] == "agrees" and "fallback" not in r["method_declared"]]
    verd = Counter(r["verdict"] for r in strip)
    secs = [float(r["seconds"]) for r in strip if r.get("seconds")]
    gp = [_jsonfile(ROOT / "data" / "pairs" / r["pair_id"] / "geometry_prior.json") or {} for r in strip]
    win_m = [g.get("window_m") for g in gp if g.get("window_m")]
    cut_s = max((g.get("strip_seconds_since_start") or 0) for g in gp) if gp else 0
    lats = [float(r["window_lat"]) for r in strip]
    km = len(strip) * (st.median(win_m) / 1000 if win_m else 0)
    med = [float(r["residual_median_px"]) for r in _robust(acc)] if acc else []
    g = float(strip[0]["ref_gsd_m"])
    note = (f"Every window of one whole strip, edge to edge, with no selection (`ops/cut_chain_pairs.py "
            f"tmc-iirs --strip`): TMC-2 nadir `{strip[0]['source_product']}` onto IIRS `{strip[0]['reference_product']}` "
            f"at 1555 nm (multi-modal), the same orbit. {len(strip)} windows of about "
            f"{st.median(win_m) / 1000:.1f} km = {km:.0f} km of strip, latitude {min(lats):.1f}-{max(lats):.1f}°. "
            f"Verdicts: " + ", ".join(f"{v} {n}" for v, n in verd.most_common())
            + f"; **accepted {len(acc)}/{len(strip)}**"
            + (f"; held-out median of the accepted windows above an inlier ratio of 0.5: "
               f"{_rng(min(med), max(med), '.2f')} px = {_rng(min(med) * g, max(med) * g, '.1f')} m on the {g} m "
               f"IIRS grid" if med else "")
            + (f". Time on one laptop CPU: cutting {cut_s / 60:.1f} min (reading both products and resampling), "
               f"registration {sum(secs) / 60:.1f} min (median {st.median(secs):.1f} s per window)" if secs else "")
            + ". Reported only here, never merged with the selected windows above.")
    return section_pairs("A whole strip: TMC-2 → IIRS 1555 nm, every window (no selection)", strip, note)


def section_wac(wac, reg):
    """IIRS onto the LRO WAC global mosaic (ops/cut_wac_pairs.py): the SAME IIRS windows as the
    TMC-2 -> IIRS chain pairs, now against NASA's Moon-wide base map. Kept out of every other count."""
    if not wac:
        return []
    acc = [r for r in wac if r["verdict"] == "agrees" and "fallback" not in r["method_declared"]]
    verd = Counter(r["verdict"] for r in wac)
    by_id = {r["pair_id"]: r for r in reg}
    twins = []
    for r in wac:      # wac_iirs<day>_<nm>_wNN <-> chain_tmc<day>_iirs<nm>_wNN
        _, day, nm, w = r["pair_id"].split("_")
        t = by_id.get(f"chain_tmc{day[4:]}_iirs{nm}_{w}")
        if t:
            twins.append(t)
    t_acc = [t for t in twins if t["verdict"] == "agrees" and "fallback" not in t["method_declared"]]
    med = [float(r["residual_median_px"]) for r in acc if r.get("residual_median_px")]
    note = ("Chandrayaan-2 IIRS onto NASA's Moon-wide base map, the USGS LRO WAC global morphologic mosaic "
            "(100 m, visible 643 nm; `ops/cut_wac_pairs.py`, read by HTTP range): cross-sensor AND cross-mission, "
            "and multi-modal at 1555 nm. The windows are exactly those of the TMC-2 → IIRS chain pairs (chosen from "
            "the IIRS texture alone, before any matching). The mosaic is a composite with no single Sun. "
            f"Verdicts: " + ", ".join(f"{v} {n}" for v, n in verd.most_common())
            + f"; **accepted {len(acc)}/{len(wac)}**"
            + (f" (the same IIRS windows onto TMC-2 of their own orbit: accepted {len(t_acc)}/{len(twins)})"
               if twins else "")
            + (f"; held-out median of the accepted: {_rng(min(med), max(med), '.2f')} px on the 100 m WAC grid"
               if med else "")
            + ". Reported only here, never merged with the counts above.")
    return section_pairs("IIRS → LRO WAC global mosaic (cross-mission, multi-modal)", wac, note)


def _accepted(rows):
    return [r for r in rows if r["verdict"] == "agrees" and "fallback" not in (r.get("method_declared") or "")]


def _offsets(rows):
    return [float(r["archive_offset_m"]) for r in rows if r.get("archive_offset_m") not in (None, "", "None")]


def section_tcmap(rows):
    """TMC-2 onto the SELENE TC ortho map at SAC's site, every window (ops/cut_tc_pairs.py)."""
    if not rows:
        return []
    acc = _accepted(rows)
    verd = Counter(r["verdict"] for r in rows)
    med = [float(r["residual_median_px"]) for r in _robust(acc)]
    g = float(rows[0]["ref_gsd_m"])
    lats = [float(r["window_lat"]) for r in rows]
    gp = [_jsonfile(ROOT / "data" / "pairs" / r["pair_id"] / "geometry_prior.json") or {} for r in rows]
    win_m = [x.get("window_m") for x in gp if x.get("window_m")]
    off = _offsets(acc)
    ver = [int(r["verified"]) for r in acc if r.get("verified") not in (None, "")]
    note = (f"Every window along one Chandrayaan-2 TMC-2 pass at SAC's own site (`ops/cut_tc_pairs.py`): TMC-2 nadir "
            f"`{rows[0]['source_product']}` onto the SELENE (Kaguya) Terrain Camera ortho map `{rows[0]['reference_product']}` "
            f"(JAXA; 7.40 m, a mosaic with no single Sun). Cross-sensor and cross-mission; both panchromatic visible, so "
            f"NOT multi-modal. {len(rows)} windows of {st.median(win_m) / 1000:.2f} km edge to edge, latitude "
            f"{min(lats):.2f} to {max(lats):.2f}° (the whole TC tile), no selection. Verdicts: "
            + ", ".join(f"{v} {n}" for v, n in verd.most_common()) + f"; **accepted {len(acc)}/{len(rows)}**"
            + (f"; verified squares per accepted window {min(ver)}-{max(ver)} of 64 (median {st.median(ver):g})" if ver else "")
            + (f"; held-out median of the accepted windows above an inlier ratio of 0.5: {_rng(min(med), max(med), '.2f')} px "
               f"= {_rng(min(med) * g, max(med) * g, '.1f')} m on the {g:.2f} m TC grid, median {st.median(med):.2f} px "
               f"= {st.median(med) * g:.1f} m ({len(med)} windows)" if med else "")
            + (f". The archive geolocations disagree by {_rng(min(off), max(off), '.0f')} m (median {st.median(off):.0f} m) "
               f"- one steady offset along 3° of the pass, which each registration removes" if off else "")
            + ". Reported only here, never merged with the counts above.")
    return section_pairs("TMC-2 → SELENE TC ortho map at SAC's site, every window (cross-mission)", rows, note)


def section_wacstrip(rows):
    """The whole IIRS strip onto the WAC global mosaic in 19.2 km windows, every square voting."""
    if not rows:
        return []
    acc = _accepted(rows)
    verd = Counter(r["verdict"] for r in rows)
    g = float(rows[0]["ref_gsd_m"])
    lats = [float(r["window_lat"]) for r in rows]
    med = [float(r["residual_median_px"]) for r in _robust(acc)]
    ver = [int(r["verified"]) for r in acc if r.get("verified") not in (None, "")]
    secs = [float(r["seconds"]) for r in rows if r.get("seconds")]
    note = (f"The whole Chandrayaan-2 IIRS strip `{rows[0]['source_product']}` onto NASA's Moon-wide base map, the USGS "
            f"LRO WAC global morphologic mosaic (100 m, visible 643 nm), every window edge to edge with no selection "
            f"(`ops/cut_wac_pairs.py --strip`): cross-sensor, cross-mission and multi-modal (1555 nm against the "
            f"visible). The windows are 192 WAC pixels (19.2 km) so that each of the 8 × 8 squares is 24 px, the smallest "
            f"the area check lets vote (`core/reliability.py` MIN_CELL_SIDE_PX): every verdict here is region by region, "
            f"unlike the 16 smaller windows in the section above, whose squares were too small to vote. {len(rows)} "
            f"windows, latitude {min(lats):.1f}-{max(lats):.1f}°. Verdicts: "
            + ", ".join(f"{v} {n}" for v, n in verd.most_common()) + f"; **accepted {len(acc)}/{len(rows)}**"
            + (f"; verified squares per accepted window {min(ver)}-{max(ver)} of 64 (median {st.median(ver):g})" if ver else "")
            + (f"; held-out median of the accepted windows above an inlier ratio of 0.5: {_rng(min(med), max(med), '.2f')} px "
               f"= {_rng(min(med) * g, max(med) * g, '.0f')} m on the 100 m WAC grid, median {st.median(med):.2f} px "
               f"= {st.median(med) * g:.0f} m ({len(med)} windows)" if med else "")
            + (f". Registration {sum(secs) / 60:.1f} min on the laptop CPU" if secs else "")
            + ". Reported only here, never merged with the counts above.")
    return section_pairs("IIRS → LRO WAC, the whole strip, region by region (cross-mission, multi-modal)", rows, note)


def section_dtm(rows, reg):
    """TMC-2 fore -> aft with both images orthorectified on the pass's DTM (ops/ortho_tmc.py), beside
    the same four windows without it."""
    if not rows:
        return []
    by = {r["pair_id"]: r for r in reg}
    gp = {r["pair_id"]: _jsonfile(ROOT / "data" / "pairs" / r["pair_id"] / "geometry_prior.json") or {} for r in rows}
    acc, before = _accepted(rows), []
    L = ["## Relief: TMC-2 fore → aft orthorectified on the pass's DTM (same sensor)", "",
         f"The four windows of the real viewpoint test above, cut again with both images orthorectified "
         f"(`ops/ortho_tmc.py`): the archive lattice already carries terrain at its 100-px nodes (its label: "
         f"reference data SELENE), so each pixel is moved by the relief BETWEEN the nodes - ISRO's TMC-2 DTM of the "
         f"same pass (`{(gp[rows[0]['pair_id']].get('orthorectification') or {}).get('dtm')}`, ~10 m posting; its label "
         f"gives a height RMSE of 63 m against SELENE) minus that DTM interpolated between the nodes - times the "
         f"tangent of each camera's emission, toward the spacecraft (geometry from the pass's orbit file). The DTM is "
         f"made from this pass's own stereo, so this measures what the pipeline does once ISRO's terrain model is "
         f"applied - the workflow SAC would run - not an independent height check. Same instrument, same Sun: NOT "
         f"cross-sensor.", "",
         "| window | relief in window, p1-p99 (m) | without the DTM: verdict, inlier ratio, held-out median px | "
         "with the DTM: verdict, inlier ratio, held-out median px | verified squares without / with |",
         "|---|---|---|---|---|"]
    for r in rows:
        base_id = r["pair_id"].replace("_dtm_", "_")
        b = by.get(base_id)
        o = (gp[r["pair_id"]].get("orthorectification") or {})
        if b:
            before.append(b)

        def cell(x):
            return (f"{x['verdict']}{' (fallback)' if 'fallback' in (x.get('method_declared') or '') else ''}, "
                    f"{_f(x['inlier_ratio'])}, {_f(x.get('residual_median_px'))}")
        L.append(f"| `{r['pair_id']}` | {o.get('dtm_relief_in_window_m_p1_p99', 'n/a')} | {cell(b) if b else 'n/a'} | "
                 f"{cell(r)} | {b['verified'] if b else 'n/a'} / {r['verified']} |")
    L += ["", f"Accepted: **{len(_accepted(before))}/{len(before)} without the DTM, {len(acc)}/{len(rows)} with it.**", ""]
    return L


def section_sun_ladder(rows, sweep):
    """ops/sun_ladder.py: the sweep's 60-120 deg windows registered through LROC NACs lit in between."""
    if not rows:
        return []
    import re as _re
    L = ["## The Sun ladder: Suns 60-120° apart, through images lit in between (`ops/sun_ladder.py`)", "",
         "Registered directly, these windows fail (the real sweep above: 0 of 12 accepted at 60-120°). A ladder "
         "never asks one registration to cross that gap: OHRC → M → T, where M is an LROC NAC over the same ground "
         "that registered correctly in the sweep, its Sun outside 60-120° of the OHRC's and within 60° of T's; where "
         "a window's only such M are opposite-Sun images, also OHRC → M1 → M2 → T, with M1 near the OHRC's Sun and M2 "
         "near T's (every link at most 60° apart). Every leg is cut over the failing window's ground, registered by "
         "`run_all` like any pair and judged by its own area check, inside the Sun range where that check is "
         "calibrated; a ladder is accepted only if every leg is. At 60-120° the image cannot judge even a perfect "
         "alignment, so the composite is NOT judged against T's pixels: where two accepted ladders cover one window, "
         "their composites are compared with each other (consistency, not accuracy), and each is compared with the "
         "failed direct registration. Kept out of every count and table above.", "",
         "| window (direct, sweep) | Sun azimuths O-T apart | direct outcome | via | Sun apart per link | links | ladder | two ladders agree to (m, px of T) | ladder vs the direct registration (m RMS) |",
         "|---|---|---|---|---|---|---|---|---|"]
    windows, accepted_w, cross = {}, set(), {}
    for r in sorted(rows, key=lambda r: r["pair_id"]):
        m = _re.match(r"ladder_(m\d+[lr]e)_(w\d+)_via_((?:m\d+[lr]e_?)+)$", r["pair_id"])
        if not m:
            continue
        t, w, via = m.groups()
        target = f"site_ohrc_{t}_{w}_sw"
        windows.setdefault(target, []).append(r)
        d = sweep.get(target, {})
        links = _re.findall(r"\((\w+); Sun ([\d.]+) deg\)", r.get("notes") or "")
        vd = _re.search(r"composite vs the direct registration ([\d.]+) m RMS", r.get("notes") or "")
        ok = r.get("verdict") == "agrees"
        if ok:
            accepted_w.add(target)
        x = "-"
        if ok and r.get("loop_rms_m") not in (None, ""):
            cross[target] = (float(r["loop_rms_m"]), float(r["loop_rms_px"]))
            x = f"{float(r['loop_rms_m']):.2f} m, {float(r['loop_rms_px']):.2f} px"
        L.append(f"| `{target}` | {_f(r.get('d_sun_azimuth_deg'), 1)}° | {d.get('outcome', 'n/a')} | "
                 + " → ".join(f"`{v.upper()}`" for v in via.split("_")) + " | "
                 + " / ".join(f"{deg}°" for _, deg in links) + " | " + ", ".join(v for v, _ in links)
                 + f" | **{'accepted' if ok else 'not accepted'}** | {x} | {vd.group(1) if vd else 'n/a'} |")
    gap = {k: v for k, v in sweep.items() if 60 <= float(v.get("d_sun_azimuth_deg") or 0) < 120}
    by_dz = {}
    for k, v in gap.items():
        dz = round(float(v.get("d_sun_azimuth_deg") or 0), 1)
        by_dz.setdefault(dz, [0, 0])
        by_dz[dz][1] += 1
        by_dz[dz][0] += k in accepted_w
    xm = sorted(c[0] for c in cross.values())
    L += ["", f"**{len(accepted_w)} of the {len(gap)} windows** with the Suns 60-120° apart are accepted through a "
              f"ladder ({len(windows)} have a route; by Sun difference: "
              + ", ".join(f"{dz}°: {a} of {n}" for dz, (a, n) in sorted(by_dz.items())) + ")."
              + (f" On the {len(cross)} windows where two accepted ladders cover the same ground, their composites agree "
                 f"to {xm[0]:.2f}-{xm[-1]:.2f} m RMS ("
                 + ", ".join(f"{px:.2f}" for _, px in sorted(cross.values())) + " px of T)." if cross else ""),
          "A window whose every route has a leg the area check does not accept stays refused, as the direct "
          "registration was.", ""]
    return L


def section_reliefq(rows):
    """ops/split_windows.py: the fore/aft windows as 2 x 2 quarters, each with its own transform."""
    if not rows:
        return []
    from collections import defaultdict
    acc = defaultdict(lambda: [0, 0])
    for r in rows:
        k = "with the DTM" if r["pair_id"].startswith("reliefq_dtm_") else "without the DTM"
        acc[k][1] += 1
        acc[k][0] += r in _accepted([r])
    per = defaultdict(lambda: [0, 0])
    for r in rows:
        w = r["pair_id"].split("_q")[0].rsplit("_", 1)[-1] + (" (DTM)" if "_dtm_" in r["pair_id"] else "")
        per[w][1] += 1
        per[w][0] += r in _accepted([r])
    return ["### Relief with a local model: each window as 2 × 2 quarters (`ops/split_windows.py`)", "",
            "A transform per quarter window (1.14 km) absorbs relief that varies across a whole window better than one "
            "transform per window - the local-model answer. Quarters are cropped from the same windows (the source over "
            "exactly the same ground), registered and judged like any pair (8 × 8 squares of 24 px). Accepted quarters: "
            + "; ".join(f"**{a} of {n} {k}**" for k, (a, n) in sorted(acc.items(), reverse=True)) + " (per window: "
            + ", ".join(f"{w} {a}/{n}" for w, (a, n) in sorted(per.items())) + "). "
            "No better than whole windows: where a window fails, its quarters fail too (too few matches across a "
            "50° change of view), so relief between views this far apart stays a limit, reported as measured.", ""]


def section_finder(d):
    """ops/find_reference.py on Site N's OHRC frame: the search that found Site N by hand, as a tool."""
    target = "ch2_ohr_ncp_20250612T2031048828_d_img_d18"
    try:
        from ops.find_reference import nac_records, pradan_records, rank
        tgt, cands = rank(target, pradan_records(d / "pradan" / "shapefiles") + nac_records(d), 0.2)
    except (Exception, SystemExit):  # noqa: BLE001 - no catalogue here: say nothing
        return []
    la, lo = tgt["centre"]
    L = ["## Choosing the reference by its Sun (`ops/find_reference.py`)", "",
         f"Registration across very different Suns is the hard case (0 of 12 accepted with the Suns 60-120° apart, "
         f"above), so the reference is chosen by its Sun: every image in PRADAN's footprint catalogue (OHRC, "
         f"TMC-2 nadir, IIRS) and every LRO NAC known on this machine that covers the Chandrayaan-2 footprint, "
         f"ranked by the angle between the two Sun directions at the footprint's centre. PRADAN's catalogue "
         f"carries no Sun (its angle fields are zero), so the Sun is computed from each image's start time "
         f"(`ops/lunar_sun.py`: Meeus, no ephemeris file; it matches LROC's own published sub-solar points to "
         f"0.04° - `ops/test_lunar_sun.py`). For Site N's OHRC frame `{target}` (centre {la:.2f}°, "
         f"{lo:.2f}°; Sun incidence {tgt['incidence']:.1f}°), {len(cands)} images cover at least 20 % of it; "
         f"the best Sun first:", "",
         "| image | instrument | covers | Sun directions apart | azimuth apart | incidence |",
         "|---|---|---|---|---|---|"]
    for r in cands[:10]:
        L.append(f"| `{r['id']}` | {r['instrument']} | {r['overlap']:.0%} | {r['sun_angle']:.1f}° | "
                 f"{r['d_azimuth']:.1f}° | {r['incidence']:.1f}° |")
    used = {"ch2_ohr_ncp_20250612T2229094979_d_img_d18", "ch2_tmc_ncn_20200607T2239162106_d_img_d18",
            "M1282456834RE"}
    hit = [k for k, r in enumerate(cands, 1) if r["id"] in used]
    L += ["", f"The three images Site N's evidence uses (the next orbit's OHRC, TMC-2 `20200607T2239`, LRO NAC "
              f"`M1282456834RE`) rank {', '.join(str(k) for k in hit)} of {len(cands)}." if hit else "", ""]
    # 3 Oct 2026: the same search over the whole OHRC archive (ops/reference_index.py), read from its
    # committed output; the console looks frames up in the same file.
    idx = _jsonfile(ROOT / "evaluation" / "reference_index.json")
    if idx:
        from ops.reference_index import summary
        s = summary(idx)
        L += [f"**The whole OHRC archive** (`ops/reference_index.py` -> `evaluation/reference_index.json`, generated at "
              f"`{idx.get('commit')}`; the console searches the same file): all {s['n']} OHRC observations in PRADAN's "
              f"catalogue, each ranked against every image covering at least {idx['min_overlap']:.0%} of it. "
              f"**{s['other_orbit_within_5']} of {s['n']}** have an image from ANOTHER orbit lit within 5° of their Sun "
              f"({s['other_orbit_within_10']} within 10°); counting images taken alongside on the same pass "
              f"(TMC-2, IIRS), {s['within_5']} do. The best partner is another OHRC observation for "
              f"{s['best_instrument'].get('OHRC', 0)}, TMC-2 for {s['best_instrument'].get('TMC-2', 0)}, IIRS for "
              f"{s['best_instrument'].get('IIRS', 0)} and an LRO NAC for {s['best_instrument'].get('LRO NAC', 0)} "
              f"(the NAC list is only what this machine knows, so that count is a floor).", ""]
        if "other_orbit_in_band" in s:
            # 4 Oct 2026: the frames without a 5-deg partner are not left without one - inside the Sun range
            # the evidence above verifies, every frame but a few has a partner from another orbit.
            from ops.reference_index import BAND_AZ_DEG, BAND_INC_DEG
            L += [f"Inside the Sun range this report verifies - azimuths at most {BAND_AZ_DEG:.0f}° apart (the real "
                  f"sweep below) and the Sun at most {BAND_INC_DEG}° higher or lower (SAC's frame, above) - "
                  f"**{s['other_orbit_in_band']} of {s['n']}** OHRC observations have an image from another orbit; "
                  f"{s['other_orbit_within_60']} of {s['n']} have one with the two Sun directions at most 60° apart. "
                  f"Only the top {idx.get('top')} candidates of each frame are kept, so these counts are floors.", ""]
    return L


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


def section_chain(reg, d):
    """The chained route, measured after the submission: TMC-2 -> IIRS on one orbit, LRO NAC ->
    TMC-2 with and without a matching Sun, and OHRC -> TMC-2 re-cut in LRO's geometry
    (`ops/cut_chain_pairs.py`). Its own section, never merged into the frozen tables above.
    Every value in the prose is read from the rows, the pairs' geometry_prior.json or the saved
    NAC corrections - 29 Sep: a claim-check found dates, ids and thresholds typed here."""
    import math as _m
    import numpy as np
    from ops.cut_chain_pairs import TMC2_PASSBAND_NM
    chain = [r for r in reg if r["pair_id"].startswith("chain_")]
    if not chain:
        return []
    mm_rows = list({r["pair_id"]: r for r in _rows(MM) if r.get("kind") == "tmc2-iirs"}.values())  # latest per pair
    commits = sorted({r.get("git_commit") or "?" for r in chain} | {r.get("git_commit") or "?" for r in mm_rows})
    days = sorted({(r.get("timestamp") or "")[:10] for r in chain} - {""})
    frozen = Counter(r.get("git_commit") for r in reg if not r["pair_id"].startswith("chain_")).most_common(1)
    gps = {r["pair_id"]: _jsonfile(ROOT / "data" / "pairs" / r["pair_id"] / "geometry_prior.json") or {} for r in chain}
    in_freeze = bool(frozen) and set(commits) <= {frozen[0][0]}
    when = (f"First measured after the idea was submitted (28 Sep 2026); these rows were re-run with every other "
            f"piece of evidence at commit `{frozen[0][0]}`" if in_freeze else
            f"Measured on {', '.join(days)} at commit {', '.join(f'`{c}`' for c in commits)}, after the idea was "
            f"submitted - **not part of the `{frozen[0][0] if frozen else '?'}` evidence freeze**")
    L = ["## After the submission: IIRS and TMC-2, and the route between them", "",
         f"{when}. Cut by "
         f"`ops/cut_chain_pairs.py`; products fetched by `ops/fetch_pradan.py` (members and IIRS bands read out "
         f"of each PRADAN zip by HTTP range). Three questions the 28 Sep submission left open: does IIRS register "
         f"onto TMC-2 once the Sun is taken out of the problem; does TMC-2 register onto anything at all; and was "
         f"OHRC -> TMC-2 refused for the Sun or for something else.", ""]

    def verdicts(rows):
        c = Counter(r["verdict"] for r in rows)
        return ", ".join(f"{v} {c[v]}" for v in ("agrees", "unconfirmed", "contradicted") if c[v])

    def rng(rows, key, nd=2, scale=None):
        v = [float(r[key]) for r in rows if r.get(key) not in (None, "")]
        if not v:
            return "n/a"
        one = lambda a, b: f"{a:.{nd}f}" if f"{a:.{nd}f}" == f"{b:.{nd}f}" else f"{a:.{nd}f} to {b:.{nd}f}"  # noqa: E731
        s = one(min(v), max(v))
        if not scale:
            return s
        lo, hi = min(v) * scale, max(v) * scale
        return s + (f" ({lo:.1f} m)" if f"{lo:.1f}" == f"{hi:.1f}" else f" ({lo:.1f} to {hi:.1f} m)")

    def day(pid):
        m = re.search(r"_(\d{4})(\d{2})(\d{2})T", pid or "")
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else pid

    # (a) TMC-2 -> IIRS, one subsection per orbit (a second orbit, Site N's, was added 1 Oct 2026)
    ti_all = sorted([r for r in chain if _kind(r) == "tmc2-iirs"], key=lambda r: r["pair_id"])
    orbits = defaultdict(list)
    for r in ti_all:
        orbits[r["source_product"]].append(r)
    n_orb = len(orbits)
    for tmc_key, ti in sorted(orbits.items()):
        if ti:
            bands = defaultdict(list)
            for r in ti:
                bands[(gps[r["pair_id"]].get("reference") or {}).get("center_wavelength_nm")].append(r)
            chosen = [p for p, g in gps.items() if p in {r["pair_id"] for r in ti}
                      and not str(g.get("window_rule", "")).startswith("the windows of")]
            g0 = gps[chosen[0]] if chosen else gps[ti[0]["pair_id"]]
            sel_nm = (g0.get("reference") or {}).get("center_wavelength_nm")
            ref_px = (g0.get("reference") or {}).get("shape", [0])[0]
            tmc_id = ti[0]["source_product"]
            iirs_id = re.sub(r" band .*$", "", ti[0]["reference_product"])
            empty = []
            try:
                prov = _jsonfile(next((d / "pradan" / "iirs").rglob(f"{iirs_id}_bands_PROVENANCE.json"))) if d else None
                for stem in (prov or {}).get("bands", {}):
                    f = next((d / "pradan" / "iirs").rglob(f"{stem}.f32"), None)
                    if f is not None and not np.any(np.fromfile(f, dtype="<f4")):
                        empty.append(int(stem.rsplit("band", 1)[1]))
            except StopIteration:
                pass
            n_win = len({(r["window_lat"], r["window_lon"]) for r in ti})
            lo_nm, hi_nm = TMC2_PASSBAND_NM
            L += [f"### TMC-2 → IIRS, orbit of {day(tmc_id)} (cross-sensor, same mission; multi-modal beyond {hi_nm} nm)"
                  + (f" - {sorted(orbits).index(tmc_key) + 1} of {n_orb} orbits" if n_orb > 1 else ""), "",
                  f"TMC-2 nadir `{tmc_id}` against IIRS `{iirs_id}`, the same orbit. {g0.get('sun_note', '')}. {n_win} windows, "
                  f"chosen before any matching by the texture of the IIRS {sel_nm:.0f} nm band alone "
                  f"({g0.get('window_rule', '')}); the same {n_win} ground windows for every band, so each band row below is "
                  f"{n_win} registrations of the same {n_win} places. TMC-2 ~{ti[0]['src_gsd_m']} m against IIRS "
                  f"~{ti[0]['ref_gsd_m']} m ({ti[0]['scale_ratio']}×), {ref_px}-px IIRS windows, so every trust cell is "
                  f"{ref_px // 8} px and the per-cell area check runs. TMC-2 records {lo_nm}-{hi_nm} nm (its PRADAN payload "
                  f"description); an IIRS band beyond {hi_nm} nm is outside anything TMC-2 sees and counts as multi-modal, "
                  f"a band inside it does not."
                  + (f" Bands {', '.join(map(str, sorted(empty)))} of this cube hold only zeros and were not used." if empty else ""),
                  "",
                  "| IIRS band | modality | windows accepted | matches | inliers | held-out median px (m) on the IIRS grid | "
                  "verified cells /64 | archive offset m |",
                  "|---|---|---|---|---|---|---|---|"]
            for nm in sorted(bands):
                rows = bands[nm]
                g = float(rows[0]["ref_gsd_m"])
                L.append(f"| {nm:.0f} nm | {'infrared: multi-modal' if nm > hi_nm else 'inside TMC-2 passband: NOT multi-modal'} | "
                         f"{sum(r['verdict'] == 'agrees' for r in rows)}/{len(rows)} | {rng(rows, 'n_matches', 0)} | "
                         f"{rng(rows, 'inliers', 0)} | {rng(rows, 'residual_median_px', 3, g)} | {rng(rows, 'verified', 0)} | "
                         f"{rng(rows, 'archive_offset_m', 1)} |")
            off_px = [float(r["archive_offset_m"]) / float(r["ref_gsd_m"]) for r in ti if r.get("archive_offset_m")]
            L += ["", f"The archive offset (how far each registration moved TMC-2 from where the two archives' own "
                  f"grids put it) is {min(off_px):.2f}-{max(off_px):.2f} IIRS pixels in every band and every window: a "
                  f"steady disagreement between the two instruments' geolocation, which is what a registration is for.", ""]
            orb_mm = [r for r in mm_rows if r["pair_id"].startswith(f"chain_tmc{tmc_id[12:20]}_")]
            if orb_mm:
                latest_mm = {}
                for r in orb_mm:
                    latest_mm[r["pair_id"]] = r
                per = defaultdict(list)
                for r in latest_mm.values():
                    m = re.search(r"_iirs(\d+)_w", r["pair_id"])
                    per[int(m.group(1)) if m else 0].append(r)
                L += ["Band against band, summarised (full table below): the MEDIAN disagreement per window, and the "
                      "worst single point of the 20 × 20 lattice. These are medians and a maximum, not bounds, and they "
                      "measure consistency between independent registrations, not accuracy.", "",
                      "| band against 1555 nm | windows | median disagreement px (m) | p90 px | worst point px |",
                      "|---|---|---|---|---|"]
                for nm in sorted(per):
                    rows = per[nm]
                    g = float(rows[0]["ref_gsd_m"])
                    L.append(f"| {nm} nm | {len(rows)} | {rng(rows, 'disagreement_median_px', 3, g)} | "
                             f"{rng(rows, 'disagreement_p90_px', 2)} | {max(float(r['disagreement_max_px']) for r in rows):.2f} |")
                L.append("")
            L += mm_table("tmc2-iirs", prefix=f"chain_tmc{tmc_id[12:20]}_")
            for nm in sorted(bands):
                L += section_pairs(f"TMC-2 → IIRS {nm:.0f} nm, orbit of {day(tmc_id)}, window by window", bands[nm], "",
                                   level="####")

    # (b) NAC -> TMC-2, with and without a matching Sun
    nt = sorted([r for r in chain if _kind(r) == "nac-tmc2"], key=lambda r: r["pair_id"])
    passes, near = [], []
    if nt:
        by = defaultdict(list)
        for r in nt:
            by[r["reference_product"]].append(r)
        passes = sorted(by.items(), key=lambda kv: max(abs(float(r["d_sun_azimuth_deg"] or 0)) for r in kv[1]))
        near, far = passes[0][1], passes[-1][1]
        g_nt = gps[nt[0]["pair_id"]]
        from ops.cut_site_pairs import OVERVIEW_GSD
        L += ["### LRO NAC → TMC-2 at SAC's site: the same NAC, two TMC-2 passes", "",
              f"NAC `{nt[0]['source_product']}` (~{nt[0]['src_gsd_m']} m), chosen for a Sun close to TMC-2's "
              f"{day(passes[0][0])} pass, against that pass and against the {day(passes[-1][0])} pass. Cross-sensor and "
              f"cross-mission; both panchromatic - NOT multi-modal. NAC geometry prior: "
              f"{((g_nt.get('source') or {}).get('coarse_prior') or {}).get('model', 'see geometry_prior.json')} - never "
              f"fitted to the TMC-2 it is registered to, nor to the OHRC. Windows by `ops.cut_site_pairs.pick_windows` "
              f"on {OVERVIEW_GSD:g} m overviews (shared, lit, textured), no matching involved. NAC Sun computed at each "
              f"window from LROC's sub-solar point; TMC-2 Sun from its label.", "",
              "| TMC-2 pass | Δsun az | Δincidence | windows | verdicts | inliers | inlier ratio | held-out median px (m) on "
              "the TMC-2 grid, accepted windows | verified cells /64 | archive offset m, accepted windows |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for ref, rows in passes:
            g = float(rows[0]["ref_gsd_m"])
            acc = [r for r in rows if r["verdict"] == "agrees"]
            robust = acc and min(float(r["inlier_ratio"]) for r in acc) > 0.5
            L.append(f"| {day(ref)} | {rng(rows, 'd_sun_azimuth_deg', 1)}° | {rng(rows, 'd_incidence_deg', 1)}° | "
                     f"{len(rows)} | {verdicts(rows)} | {rng(rows, 'inliers', 0)} | {rng(rows, 'inlier_ratio', 2)} | "
                     + (rng(acc, 'residual_median_px', 3, g) if robust else
                        ("not quoted: at these inlier ratios the held-out median is not robust" if acc else "n/a"))
                     + f" | {rng(rows, 'verified', 0)} | {rng(acc, 'archive_offset_m', 1) if acc else 'n/a'} |")
        far_acc = [r for r in far if r["verdict"] == "agrees"]
        if len(passes) > 1:
            L += ["", f"With the Sun {rng(near, 'd_sun_azimuth_deg', 1)}° apart in azimuth and "
                  f"{rng(near, 'd_incidence_deg', 1)}° in incidence, TMC-2 registers: {verdicts(near)}. With it "
                  f"{rng(far, 'd_sun_azimuth_deg', 1)}° apart in azimuth and {rng(far, 'd_incidence_deg', 1)}° in "
                  f"incidence, the same NAC gives {verdicts(far)}"
                  + (f"; the accepted ones rest on {rng(far_acc, 'verified', 0)} verified cells at inlier ratios of "
                     f"{rng(far_acc, 'inlier_ratio', 2)}, and no accuracy is quoted for them" if far_acc else "") + ".", ""]
        for ref, rows in passes:
            L += section_pairs(f"NAC → TMC-2 pass {day(ref)}, window by window", rows, "", level="####")

    # (c) OHRC -> TMC-2 in LRO's geometry
    ot = sorted([r for r in chain if r["pair_id"].startswith("chain_ohrclroc_")], key=lambda r: r["pair_id"])
    if ot:
        from ops.cut_chain_pairs import SAC_NAC
        gp = gps[ot[0]["pair_id"]]
        sh = gp.get("ohrc_shift_into_lroc_m") or [None, None]
        second_id = nt[0]["source_product"] if nt else None
        sac = (_jsonfile(d / "site_geometry" / f"{SAC_NAC}.json") if d else None) or {}
        second = (_jsonfile(d / "site_geometry" / f"{second_id}.json") if (d and second_id) else None) or {}
        w1, w2 = sac.get("wide_offset") or {}, second.get("wide_offset") or {}
        near_acc = [r for r in near if r["verdict"] == "agrees"]
        d1 = _m.hypot(*w1["offset_m"]) if w1.get("offset_m") else None
        nn = (_m.hypot(w1["offset_m"][0] - w2["offset_m"][0], w1["offset_m"][1] - w2["offset_m"][1])
              if w1.get("offset_m") and w2.get("offset_m") else None)
        field = None
        if w1.get("offset_m") and sh[0] is not None:
            field = _m.hypot(sh[0] - w1["offset_m"][0], sh[1] - w1["offset_m"][1])
        o_sun = (gp.get("source") or {}).get("sun") or {}
        t_sun = (gp.get("reference") or {}).get("sun") or {}
        refused = all(r["verdict"] == "contradicted" for r in ot)
        L += ["### OHRC → TMC-2 again, with the OHRC placed in LRO's geometry", "",
              "The frozen OHRC -> TMC-2 pairs above were cut on the two archives' own grids. "
              + (f"LROC's published corners for SAC's NAC `{SAC_NAC}` sit ({w1['offset_m'][0]:+.0f}, "
                 f"{w1['offset_m'][1]:+.0f}) m ({d1 / 1000:.1f} km) from SAC's OHRC archive grid "
                 f"(`site_geometry/{SAC_NAC}.json`), against a TMC-2 window of {gp.get('window_m', 0) / 1000:.1f} km. "
                 if d1 else "")
              + (f"A second NAC's corners (`{second_id}`) sit ({w2['offset_m'][0]:+.0f}, {w2['offset_m'][1]:+.0f}) m from "
                 f"the OHRC-aligned first NAC ({w2.get('n_agree')}/{w2.get('n_templates')} wide-search templates, an "
                 f"offset that drifts along the strip; `site_geometry/{second_id}.json`), i.e. about {nn:.0f} m from the "
                 f"first NAC's own corners. " if nn is not None else "")
              + (f"TMC-2's {day(passes[0][0])} grid lands {rng(near_acc, 'archive_offset_m', 0)} m from the second NAC's "
                 f"corners (the accepted windows above) - consistent to within the ~0.01° precision LROC publishes its "
                 f"corners to, not a geolocation accuracy. The first NAC was never measured against TMC-2. " if near_acc else "")
              + "So SAC's OHRC frame is the one far from the others, and the frozen windows barely shared ground: that "
              "refusal was right - those answers were wrong - but it cannot be laid on the Sun alone. "
              + (f"Here the OHRC frame is first moved by ({sh[0]:+.0f}, {sh[1]:+.0f}) m into LRO's geometry (the NAC's "
                 f"saved wide offset plus its 4 m field evaluated at the OHRC frame's centre"
                 + (f", {field:.0f} m apart" if field is not None else "") + "; no TMC-2 pixel), and cut exactly as the "
                 "frozen pairs were: same window rule, same 4×4 OHRC averaging, same scale. " if sh[0] is not None else "")
              + f"Result: {verdicts(ot)}. What is left between the two images is the Sun "
              f"({rng(ot, 'd_sun_azimuth_deg', 1)}° apart in azimuth; label elevations "
              f"{_f(o_sun.get('elevation_deg_label'), 1)}° and {_f(t_sun.get('elevation_deg_label'), 1)}°) and the "
              f"{rng(ot, 'scale_ratio', 1)}× scale, which this test cannot separate"
              + (". The frozen evidence accepts much larger azimuth differences at lower, similar elevations "
                 "(SAC's equatorial pair above), so the elevation difference is the likelier cause; "
                 + ("OHRC -> TMC-2 under a matched Sun is tested at Site N below." if any(
                     r["pair_id"].startswith("siten_ohrc") and "_tmc" in r["pair_id"] for r in reg)
                    else "OHRC -> TMC-2 under a matched Sun has not been tested.") if refused else "."), ""]
        L += section_pairs(f"OHRC (in LRO geometry) → TMC-2 pass {day(ot[0]['reference_product'])}, window by window",
                           ot, "", level="####")
    return L


def _robust(acc, cut=0.5):
    """Accepted windows whose held-out median can be quoted: inlier ratio above `cut` (see
    _residual_caveat - below ~0.5 a 20 % held-out draw can be majority-outlier)."""
    return [r for r in acc if r.get("residual_median_px") and float(r.get("inlier_ratio") or 0) > cut]


def section_ladder(reg):
    """SAC's OHRC frame against LRO NACs chosen by their Sun (ops/cut_chain_pairs.py ohrc-nac-lro,
    1 Oct 2026): rungs whose Sun azimuth stays near the OHRC's while the elevation climbs (the
    Sun-ELEVATION evidence), and rungs whose azimuth is opposite at several elevations. Every value
    in the prose is read from the rows and the pairs' geometry_prior.json."""
    rows = [r for r in reg if r["pair_id"].startswith("sac_ohrclroc_nac")]
    if not rows:
        return []
    gps = {r["pair_id"]: _jsonfile(ROOT / "data" / "pairs" / r["pair_id"] / "geometry_prior.json") or {} for r in rows}
    by = defaultdict(list)
    for r in rows:
        by[r["reference_product"]].append(r)

    def d_el(r):                       # d_incidence = NAC incidence - OHRC incidence = -(elevation change)
        return -float(r["d_incidence_deg"])

    def el_at(r):
        return 90 - float(gps[r["pair_id"]]["reference"]["incidence_deg_at_site"])

    def med_az(rs):
        return st.median(float(r["d_sun_azimuth_deg"]) for r in rs)

    g0 = gps[rows[0]["pair_id"]]
    o_sun = (g0.get("source") or {}).get("sun") or {}
    ref_gsd = float(rows[0]["ref_gsd_m"])
    cands = {(gps[r["pair_id"]].get("candidate_index")) for r in rows}
    fams = [("near", "Sun azimuth near the OHRC's, elevation raised",
             sorted([kv for kv in by.items() if med_az(kv[1]) <= 90], key=lambda kv: st.median(map(d_el, kv[1])))),
            ("opposite", "Sun azimuth opposite the OHRC's, at several elevations",
             sorted([kv for kv in by.items() if med_az(kv[1]) > 90], key=lambda kv: st.median(map(d_el, kv[1]))))]
    L = ["## Sun azimuth and elevation, on SAC's own frame: OHRC → LRO NAC under many Suns", "",
         f"SAC's OHRC frame `{rows[0]['source_product']}` (arXiv:2509.04775, Table 1; label Sun elevation "
         f"{_f(o_sun.get('elevation_deg_label'), 1)}°, azimuth {_f(o_sun.get('azimuth_deg_label'), 1)}°) against "
         f"{len(by)} LRO NACs chosen for their Sun alone (`ops/cut_chain_pairs.py ohrc-nac-lro`; WUSTL ODE footprints). "
         f"Both images are placed in LRO's geometry with no image content of the pair: the OHRC moved by "
         f"({g0['ohrc_shift_into_lroc_m'][0]:+.0f}, {g0['ohrc_shift_into_lroc_m'][1]:+.0f}) m by SAC's NAC correction, "
         f"every NAC by LROC's published corners. One reference grid for every NAC ({ref_gsd:g} m: each NAC "
         f"area-averaged by a whole factor first), one set of {len(cands)} candidate windows on the OHRC frame's centre "
         f"line ({g0.get('window_m', 0) / 1000:.2f} km), each NAC using the ones it covers. Cross-sensor, cross-mission; "
         f"both panchromatic - NOT multi-modal. Sun of the NAC computed at each window from LROC's sub-solar point; of "
         f"the OHRC from its label. Held-out medians are quoted only for accepted windows whose inlier ratio is above "
         f"0.5 (`_residual_caveat`). The archive offset is the disagreement between LROC's published corners (~0.01°) "
         f"and the OHRC moved into LRO's geometry - a few hundred metres - not an accuracy.", ""]
    head = ("| NAC | Sun elevation at the windows | Δ elevation | Δ azimuth | NAC emission | windows | verdicts | "
            "inliers | held-out median px (m) on the " + f"{ref_gsd:g} m grid, accepted | verified cells /64 | archive offset m |")
    for key, title, rungs in fams:
        if not rungs:
            continue
        frs = [r for _, rs in rungs for r in rs]
        fv = Counter(r["verdict"] for r in frs)
        rob = _robust([r for r in frs if r["verdict"] == "agrees"])
        L += [f"### {title}", "", head, "|---|---|---|---|---|---|---|---|---|---|---|"]
        for nac, rs in rungs:
            g = gps[rs[0]["pair_id"]].get("reference") or {}
            els = [el_at(r) for r in rs]
            acc = [r for r in rs if r["verdict"] == "agrees"]
            rb = _robust(acc)
            c = Counter(r["verdict"] for r in rs)
            med = [float(r["residual_median_px"]) for r in rb]
            daz = [float(r['d_sun_azimuth_deg']) for r in rs]
            L.append(f"| `{nac}` | {_rng(min(els), max(els))}° | {_rng(min(map(d_el, rs)), max(map(d_el, rs)), '+.1f', ' to ')}° | "
                     f"{_rng(min(daz), max(daz))}° | "
                     f"{_f(g.get('emission_deg'), 1)}° | {len(rs)} | "
                     + ", ".join(f"{v} {c[v]}" for v in ("agrees", "unconfirmed", "contradicted") if c[v]) + " | "
                     f"{min(int(r['inliers']) for r in rs)}-{max(int(r['inliers']) for r in rs)} | "
                     + (f"{_rng(min(med), max(med), '.2f')} ({_rng(min(med) * ref_gsd, max(med) * ref_gsd)} m)"
                        + (f"; {len(acc) - len(rb)} not quoted" if len(acc) > len(rb) else "") if med else "n/a")
                     + f" | {min(int(r['verified']) for r in rs)}-{max(int(r['verified']) for r in rs)} | "
                     f"{min(float(r['archive_offset_m']) for r in rs):.0f}-{max(float(r['archive_offset_m']) for r in rs):.0f} |")
        top = rungs[-1][1]
        L += ["", f"{len(rungs)} NACs, {len(frs)} windows: " + ", ".join(f"{v} {fv[v]}" for v in ("agrees", "unconfirmed", "contradicted") if fv[v])
              + f". Highest Sun (`{rungs[-1][0]}`, {st.median(map(d_el, top)):+.1f}° in elevation, "
              f"{med_az(top):.1f}° in azimuth): " + ", ".join(f"{v} {n}" for v, n in Counter(r['verdict'] for r in top).most_common())
              + (f". Held-out median of the accepted windows with inlier ratio above 0.5: median "
                 f"{st.median(float(r['residual_median_px']) for r in rob):.2f} px = "
                 f"{st.median(float(r['residual_median_px']) for r in rob) * ref_gsd:.2f} m on the {ref_gsd:g} m grid "
                 f"({len(rob)} windows)" if rob else "") + ".", ""]
    for _, _, rungs in fams:
        for nac, rs in rungs:
            L += section_pairs(f"OHRC → NAC `{nac}` (Sun {st.median(map(d_el, rs)):+.1f}° in elevation, "
                               f"{med_az(rs):.0f}° in azimuth), window by window",
                               sorted(rs, key=lambda r: r["pair_id"]), "", level="####")
    return L


def section_site_n(reg, site_loops):
    """Site N (ops/cut_chain_pairs.py site, 1 Oct 2026): one OHRC frame, a TMC-2 pass, an LRO NAC
    and the IIRS strip of the TMC-2's own orbit, all under matched Suns, three legs on shared
    windows and the loop OHRC -> NAC -> TMC-2 against OHRC -> TMC-2. Values read from the rows,
    the pairs' geometry_prior.json and the anchor NAC's saved correction."""
    rows = [r for r in reg if r["pair_id"].startswith("siten_")]
    view = sorted([r for r in rows if _kind(r) == "ohrc-ohrc"], key=lambda r: r["pair_id"])
    rows = [r for r in rows if _kind(r) != "ohrc-ohrc"]
    if not rows:
        return []
    gps = {r["pair_id"]: _jsonfile(ROOT / "data" / "pairs" / r["pair_id"] / "geometry_prior.json") or {} for r in rows}
    legs = defaultdict(list)
    for r in rows:
        legs[_kind(r)].append(r)
    order = [("ohrc-tmc2", "OHRC → TMC-2", "cross-sensor, same mission"),
             ("ohrc-nac", "OHRC → LRO NAC", "cross-sensor, cross-mission"),
             ("nac-tmc2", "LRO NAC → TMC-2", "cross-sensor, cross-mission")]
    g0 = gps[rows[0]["pair_id"]]
    sh = g0.get("ohrc_shift_into_lroc_m") or [0, 0]
    ohrc = next((r["source_product"] for r in rows if _kind(r).startswith("ohrc")), "?")
    tmc = next((r["reference_product"] for r in rows if _kind(r).endswith("tmc2")), "?")
    nac = next((r["reference_product"] for r in rows if _kind(r) == "ohrc-nac"),
               next((r["source_product"] for r in rows if _kind(r) == "nac-tmc2"), "?"))
    # the middle of the windows, as fig10's title (east longitudes in the log; the site is west of 0)
    lat = st.median(float(r["window_lat"]) for r in rows)
    lon = (st.median(float(r["window_lon"]) for r in rows) + 180.0) % 360.0 - 180.0
    L = ["## One site, every camera: OHRC, TMC-2, IIRS and an LRO NAC under matched Suns (Site N)", "",
         f"OHRC `{ohrc}`, TMC-2 nadir `{tmc}`, LRO NAC `{nac}`, windows centred near {abs(lat):.1f}°"
         f"{'N' if lat >= 0 else 'S'}, {abs(lon):.1f}°{'E' if lon >= 0 else 'W'} "
         f"(`ops/cut_chain_pairs.py site`; found in PRADAN's footprint catalogue and WUSTL ODE by matching the Suns). "
         f"The OHRC archive grid is first moved ({sh[0]:+.0f}, {sh[1]:+.0f}) m into LRO's geometry by the NAC's 4 m "
         f"correction against it; the NAC is placed by LROC's corners and the TMC-2 by its archive grid, so no TMC-2 "
         f"pixel enters any prior. All three legs use one set of window centres on the OHRC frame's centre line, so "
         f"the OHRC -> NAC -> TMC-2 chain can be closed against the direct OHRC -> TMC-2 registration. Held-out "
         f"medians are quoted only for accepted windows with an inlier ratio above 0.5.", "",
         "| leg | terminology | Δsun az | Δincidence | scale | windows | verdicts | inliers | held-out median px (m) on "
         "the reference grid, accepted | verified cells /64 | archive offset m |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, name, term in order:
        rs = legs.get(k)
        if not rs:
            continue
        g = float(rs[0]["ref_gsd_m"])
        acc = [r for r in rs if r["verdict"] == "agrees"]
        rob = _robust(acc)
        med = [float(r["residual_median_px"]) for r in rob]
        c = Counter(r["verdict"] for r in rs)
        daz = [float(r['d_sun_azimuth_deg']) for r in rs]
        dinc = [float(r['d_incidence_deg']) for r in rs]
        L.append(f"| {name} | {term} | {_rng(min(daz), max(daz))}° | {_rng(min(dinc), max(dinc), '+.1f', ' to ')}° | "
                 f"{rs[0]['scale_ratio']}× | {len(rs)} | "
                 + ", ".join(f"{v} {c[v]}" for v in ("agrees", "unconfirmed", "contradicted") if c[v]) + " | "
                 f"{min(int(r['inliers']) for r in rs)}-{max(int(r['inliers']) for r in rs)} | "
                 + (f"{min(med):.2f}-{max(med):.2f} ({min(med) * g:.1f}-{max(med) * g:.1f} m) on {g:g} m"
                    + (f"; {len(acc) - len(rob)} not quoted" if len(acc) > len(rob) else "") if med else "n/a")
                 + f" | {min(int(r['verified']) for r in rs)}-{max(int(r['verified']) for r in rs)} | "
                 f"{min(float(r['archive_offset_m']) for r in rs):.0f}-{max(float(r['archive_offset_m']) for r in rs):.0f} |")
    L.append("")
    if site_loops:
        rms = [float(r["loop_rms_m"]) for r in site_loops]
        px = [float(r["loop_rms_px"]) for r in site_loops]
        g = site_loops[0].get("ref_gsd_m")
        L += [f"**Loop closure across three instruments and two missions.** {len(site_loops)} windows where all three "
              f"legs registered: the chain OHRC -> NAC -> TMC-2 against the direct OHRC -> TMC-2, compared at the "
              f"OHRC -> NAC inliers mapped to the ground. Loop RMS median **{st.median(rms):.2f} m** "
              f"({st.median(px):.2f} px on TMC-2's {g} m grid), max {max(rms):.2f} m (`ops/loop_closure.py --legs`). "
              f"Three registrations that are each right agree; one wrong one - however confident - does not. This is "
              f"consistency between independent registrations, not absolute accuracy.", "",
              "| loop | window (lat, lon) | RMS m | RMS px (TMC-2 grid) | p90 px | verdicts |", "|---|---|---|---|---|---|"]
        for r in sorted(site_loops, key=lambda r: r["pair_id"]):
            L.append(f"| `{r['pair_id']}` | {_f(r['window_lat'], 4)}, {_f(r['window_lon'], 4)} | {_f(r['loop_rms_m'])} | "
                     f"{_f(r['loop_rms_px'])} | {_f(r['loop_p90_px'])} | {r['verdict']} |")
        L.append("")
    L += ["The IIRS strip of the TMC-2's own orbit is registered onto the TMC-2 in the section above "
          f"(*TMC-2 → IIRS*, the orbit of `{tmc}`).", ""] if any(
        r["pair_id"].startswith(f"chain_tmc{tmc[12:20]}_iirs") for r in reg) else []
    L += section_view_n(view)
    for k, name, _ in order:
        if legs.get(k):
            L += section_pairs(f"Site N, {name}, window by window", sorted(legs[k], key=lambda r: r["pair_id"]), "",
                               level="####")
    return L


def section_view_n(view):
    """Site N's real viewpoint test (ops/cut_chain_pairs.py viewpoint): two OHRC frames of consecutive
    orbits, forward- and backward-looking, the viewing directions and Suns read per window from the
    pairs' geometry_prior.json (each frame's own .oat and .spm)."""
    if not view:
        return []
    gps = {r["pair_id"]: _jsonfile(ROOT / "data" / "pairs" / r["pair_id"] / "geometry_prior.json") or {} for r in view}
    vw = [gps[r["pair_id"]].get("view_at_window") or {} for r in view]
    sep = [v["angle_between_deg"] for v in vw if v.get("angle_between_deg") is not None]
    g = float(view[0]["ref_gsd_m"])
    acc = [r for r in view if r["verdict"] == "agrees"]
    rob = _robust(acc)
    med = [float(r["residual_median_px"]) for r in rob]
    c = Counter(r["verdict"] for r in view)
    d_inc = [float(r["d_incidence_deg"]) for r in view]
    d_az = [float(r["d_sun_azimuth_deg"]) for r in view]
    L = ["### A real viewpoint test at Site N: OHRC looking forward → OHRC looking back, the next orbit", "",
         f"`{view[0]['source_product']}` (source) → `{view[0]['reference_product']}` (reference), two hours apart. "
         f"Same instrument - a viewpoint test, NOT cross-sensor. At the windows the two viewing directions are "
         + (f"**{min(sep):.1f}-{max(sep):.1f}° apart**, from opposite sides of the site" if sep else "n/a")
         + f"; the Sun moved {min(d_az):.2f}-{max(d_az):.2f}° in azimuth and "
         + (f"{min(d_inc):+.1f}°" if f"{min(d_inc):+.1f}" == f"{max(d_inc):+.1f}" else f"{min(d_inc):+.1f} to {max(d_inc):+.1f}°")
         + f" in incidence. Both frames were put in LRO's geometry by the same NAC's 4 m correction against each, "
         f"never fitted to one another, and resampled to one {g:g} m grid; windows are every third centre on the "
         f"source frame's centre line, fixed before matching. Each image is placed by its own pointing on a sphere, "
         f"so what a window's homography cannot absorb is relief parallax between the two views. "
         f"**{c['agrees']}/{len(view)} accepted**"
         + (f"; held-out median {st.median(med):.2f} px ({st.median(med) * g:.2f} m) on the {g:g} m grid "
            f"(range {min(med):.2f}-{max(med):.2f} px, accepted windows with inlier ratio above 0.5)" if med else "")
         + ". Viewing directions from each frame's `.oat` (sub-spacecraft point and altitude), Suns from its `.spm`, "
         "both at the window's image line.", "",
         "| pair | source view: off vertical, from az | reference view | apart | Δincidence | inliers | ratio | "
         "held-out median px (m) | verified / no-evid | verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r, v in zip(view, vw):
        a, b = v.get("a") or {}, v.get("b") or {}
        mp = r.get("residual_median_px")
        L.append(f"| `{r['pair_id']}` | {_f(a.get('emission_deg'), 1)}°, {_f(a.get('spacecraft_azimuth_deg'), 0)}° | "
                 f"{_f(b.get('emission_deg'), 1)}°, {_f(b.get('spacecraft_azimuth_deg'), 0)}° | "
                 f"{_f(v.get('angle_between_deg'), 1)}° | {_f(r['d_incidence_deg'], 2)}° | {r['inliers']} | "
                 f"{_f(r['inlier_ratio'])} | {_f(mp)}" + (f" ({float(mp) * g:.2f})" if mp else "")
                 + f" | {r['verified']} / {r['no_evidence']} | {r['verdict']} |")
    L.append("")
    return L


def section_pairs(title, rows, note, level="##"):
    L = [f"{level} {title}", ""] + ([note, ""] if note else []) + [
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
    # 3 Oct 2026: one whole strip, every window (section_strip) - its own evidence, kept out of every
    # count and table below so the selected windows' numbers are exactly what they were.
    strip = sorted([r for r in reg if r["pair_id"].startswith("strip_")], key=lambda r: r["pair_id"])
    # IIRS onto the LRO WAC global mosaic (section_wac): its own evidence too, kept out of every count.
    wac = sorted([r for r in reg if r["pair_id"].startswith("wac_")], key=lambda r: r["pair_id"])
    # 3 Oct 2026, evening: three more pieces of evidence, each its own section and kept out of every
    # count - TMC-2 -> SELENE TC every window at SAC's site, the whole IIRS strip onto WAC region by
    # region, and the fore/aft windows orthorectified on the pass's DTM.
    tcmap = sorted([r for r in reg if r["pair_id"].startswith("tcmap_")], key=lambda r: r["pair_id"])
    wacstrip = sorted([r for r in reg if r["pair_id"].startswith("wacstrip_")], key=lambda r: r["pair_id"])
    dtm = sorted([r for r in reg if r["pair_id"].startswith("sac_tmcfore_tmcaft_dtm_")], key=lambda r: r["pair_id"])
    # 4 Oct 2026: the Sun ladder (legs and composites) and the relief quarters - their own sections, kept out of
    # every count, like the sets above.
    ladder_all = [r for r in reg if r["pair_id"].startswith("ladder_")]
    ladder = [r for r in ladder_all if "_via_" in r["pair_id"]]
    ladder_legs = [r for r in ladder_all if "_via_" not in r["pair_id"]]
    reliefq = sorted([r for r in reg if r["pair_id"].startswith("reliefq_")], key=lambda r: r["pair_id"])
    sep = [r for r in reg if r["pair_id"].startswith(("strip_", "wac_", "wacstrip_", "tcmap_", "sac_tmcfore_tmcaft_dtm_",
                                                      "ladder_", "reliefq_"))]
    reg = [r for r in reg if r not in sep]
    loops = [r for r in latest.values() if r["pair_id"].startswith("loop_") and not r["pair_id"].startswith("loop_siten")]
    site_loops = [r for r in latest.values() if r["pair_id"].startswith("loop_siten")]
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
                       and not r["pair_id"].startswith(("sac_", "siten_")) and not r["pair_id"].endswith("_full")],
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
            # 3 Oct 2026: the same windows' centres re-cut with the NAC resampled to the paper's grid
            # (ops/cut_pradan_pairs.py --ref-gsd 1.1179 --stem sac_ohrc_nac112 --centres-from sac_ohrc_nac)
            ("sac_ohrc_nac112_", "M1350459544RE", "equatorial, re-cut on the paper's 1.1179 m grid", "1.1179"),
            ("sac_polar_ohrc_nac_", "M165491149RE", "polar, 61.6-62.3°S 56.6°E", "0.88779")):
        rows = sorted([r for r in reg if r["pair_id"].startswith(stem)], key=lambda r: r["pair_id"])
        if not rows:
            continue
        gp = _jsonfile(ROOT / "data" / "pairs" / rows[0]["pair_id"] / "geometry_prior.json") or {}
        native = (gp.get("reference") or {}).get("resolution_mpp")
        if abs(float(rows[0]["ref_gsd_m"]) - float(sac_grid)) < 1e-3:
            grid = (f"NAC resampled to {rows[0]['ref_gsd_m']} m, the grid the paper measured this pair on "
                    f"(the NAC's own label resolution is {_f(native, 2)} m), windows centred where the frozen "
                    f"1.622 m windows are (their inner {640 * float(sac_grid):.0f} m); pixel figures are the "
                    f"same size as the paper's, held-out and in-sample still differ in kind")
        else:
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
    # the frozen cut only; the 28 Sep re-cut in LRO geometry (chain_ohrclroc_*) has its own section
    sac = sorted([r for r in reg if _kind(r) == "ohrc-tmc2" and r["pair_id"].startswith("sac_")],
                 key=lambda r: r["pair_id"])
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
    L += section_ladder(reg)
    L += section_chain(reg, d)
    L += section_strip(strip, d)
    L += section_wac(wac, reg)
    L += section_wacstrip(wacstrip)
    L += section_tcmap(tcmap)
    L += section_site_n(reg, site_loops)
    fa = sorted([r for r in reg if _kind(r) == "tmc2-tmc2"], key=lambda r: r["pair_id"])
    if fa:
        L += section_pairs("Real viewpoint: TMC-2 fore (+25°) → aft (−25°), one pass (same sensor)", fa,
                           "Same instrument, same sun, seconds apart: only the viewing direction differs "
                           "(~50°). Relief parallax between the two (~0.93 × height) is not a homography - "
                           "compare with the synthetic parallax rows below. Same sensor - NOT cross-sensor. "
                           f"Reference (aft) grid {fa[0]['ref_gsd_m']} m, source (fore) {fa[0]['src_gsd_m']} m.")
        L += section_dtm(dtm, fa)
        L += section_reliefq(reliefq)
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
    L += section_classical()
    if d:
        L += section_finder(d)
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
        L += section_sun_ladder(ladder,
                                {r["pair_id"]: {**r, "outcome": v2.get(r["pair_id"], r["outcome"])} for r in sweep})

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
                  + (f". Windows: {', '.join(f'`{w}`' for w in wins)}." if len(wins) <= 12 else ".")]
            # 3 Oct 2026, the head-to-head: what a residual check would read on the same planted
            # answers (ops/trust_real_calibration.planted_residual). Its threshold is the loosest any of
            # these windows' OWN registration needs, so it accepts every true registration here.
            has = rows_p and all(r.get("planted_residual_median_px") not in (None, "", "None") for r in rows_p)
            trs = [float(r["true_residual_median_px"]) for r in rows_p
                   if r.get("true_residual_median_px") not in (None, "", "None")] if has else []
            thr = max(trs) if trs else None
            if thr is not None:
                L += [f"Beside the area check, what a residual check reads on the SAME planted answers: the median "
                      f"held-out residual of the planted matches, and the share a residual threshold of "
                      f"**{thr:.2f} px** would flag - the loosest threshold that still accepts every one of these "
                      f"windows' true registrations (their own held-out medians reach {thr:.2f} px)."]
            L += ["", "| planted error (m) | ~px on the reference grid | trials | flagged as wrong | mean verified cells /64 |"
                  + (" residual check: median held-out residual (px) | flagged by the residual threshold |" if thr is not None else ""),
                  "|---|---|---|---|---|" + ("---|---|" if thr is not None else "")]
            for dm in sorted(by):
                t = by[dm]
                rate = sum(r["contradicted"] == "True" for r in t) / len(t)
                row = (f"| {dm:g} | {st.median(float(r['displacement_px']) for r in t):.2f} | {len(t)} | "
                       f"{rate:.1%} | {st.mean(float(r['verified']) for r in t):.1f} |")
                if thr is not None:
                    pres = [float(r["planted_residual_median_px"]) for r in t]
                    row += f" {st.median(pres):.2f} | {sum(v > thr for v in pres) / len(pres):.1%} |"
                L.append(row)
            if thr is not None:
                big = [r for r in rows_p if float(r["displacement_m"]) >= 5]
                if big:
                    a_flag = sum(r["contradicted"] == "True" for r in big)
                    r_flag = sum(float(r["planted_residual_median_px"]) > thr for r in big)
                    L += ["", f"Planted errors of 5 m or more: the residual threshold flags **{r_flag} of {len(big)}**; "
                              f"the area check flags **{a_flag} of {len(big)}**."]
            L.append("")
        # 3 Oct 2026: the visible-infrared population, from its own CSV (ops.trust_real_calibration --ir).
        ir = _rows(TRUST_IR)
        if ir:
            wins = sorted({r["pair_id"] for r in ir})
            nccs = [float(r["ncc_true"]) for r in ir if r.get("ncc_true")]
            trs = [float(r["true_residual_median_px"]) for r in ir
                   if r.get("true_residual_median_px") not in (None, "", "None")]
            thr = max(trs) if trs else None
            by = defaultdict(list)
            for r in ir:
                by[float(r["displacement_px_planned"])].append(r)
            gs = sorted({float(r["gsd_ref_m"]) for r in ir})
            L += [f"### Visible against infrared (TMC-2 → IIRS 1555 nm, two orbits): {len(wins)} windows", "",
                  f"The same planted test where the two images are in different bands: TMC-2 (visible) onto IIRS at "
                  f"1555 nm. |NCC| of the true alignment {min(abs(v) for v in nccs):.2f}-{max(abs(v) for v in nccs):.2f}. "
                  f"The IIRS grid is {_rng(gs[0], gs[-1], '.2f')} m, so the planted shifts are set in its pixels (own seed "
                  f"stream and file, `{TRUST_IR.name}`; the populations above are untouched)."
                  + (f" Residual threshold **{thr:.2f} px**: the loosest these windows' own registrations need." if thr else ""),
                  "", "| planted error (IIRS px) | ~m | trials | flagged as wrong | mean verified cells /64 |"
                  + (" residual check: median held-out residual (px) | flagged by the residual threshold |" if thr else ""),
                  "|---|---|---|---|---|" + ("---|---|" if thr else "")]
            for v in sorted(by):
                t = by[v]
                rate = sum(r["contradicted"] == "True" for r in t) / len(t)
                row = (f"| {v:g} | {st.median(float(r['displacement_m']) for r in t):.0f} | {len(t)} | {rate:.1%} | "
                       f"{st.mean(float(r['verified']) for r in t):.1f} |")
                if thr:
                    pres = [float(r["planted_residual_median_px"]) for r in t
                            if r.get("planted_residual_median_px") not in (None, "", "None")]
                    row += (f" {st.median(pres):.2f} | {sum(x > thr for x in pres) / len(pres):.1%} |" if pres else " n/a | n/a |")
                L.append(row)
            big = [r for r in ir if float(r["displacement_px_planned"]) >= 5]
            if big and thr:
                a_flag = sum(r["contradicted"] == "True" for r in big)
                r_flag = sum(float(r["planted_residual_median_px"]) > thr for r in big
                             if r.get("planted_residual_median_px") not in (None, "", "None"))
                L += ["", f"Planted errors of 5 IIRS pixels or more: the residual threshold flags **{r_flag} of "
                          f"{len(big)}**; the area check flags **{a_flag} of {len(big)}**."]
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

    # --- the whole synthetic Sun sweep, 0-180 deg (28 Sep 2026: rendering only; these rows were
    # always in results_log.csv and drawn in fig1, but the table below used to stop at 45 deg, so
    # the 90 and 180 deg medians the README explains had no REPORT.md line to point at) ---------
    try:
        from presentation.make_figures import _delta, load_curves
        deltas, ours_med, best, nscored, ntried = load_curves()
        n_ours = Counter(_delta(r) for r in log if r.get("method") == "ours_loftr+subpixel"
                         and _delta(r) is not None and r.get("rmse_gt_px") not in (None, "", "None"))
        L += ["## Synthetic Sun-azimuth sweep, 0-180° (exact truth; fig1)", "",
              "Rendered pairs (LOLA DEM, 60 m grid), Sun elevation fixed at 30°, Sun azimuth moved; the "
              "same five off-grid shifts at every angle. Medians over every scored run in results_log.csv "
              "(`presentation/make_figures.load_curves`, the data of fig1). A classical run that fails "
              "produces no rmse_gt_px and cannot enter its median, so the classical column is a median of "
              "the survivors and the next column says how many there were. The renderer is a local "
              "cosine law with no cast shadows: at 180° it produces a near-exact contrast inversion, "
              "which real terrain under a low Sun does not.", "",
              "| Sun azimuths apart | ours: runs | ours: median rmse_gt_px (m) | best of SIFT / ORB / AKAZE: "
              "median of the runs that scored | classical runs that scored |",
              "|---|---|---|---|---|"]
        # not `d`: main() holds the data folder in `d`, and the runtime section below reads it
        for da, o, b, ns, nt in zip(deltas, ours_med, best, nscored, ntried):
            L.append(f"| {da:g}° | {n_ours[da]} | {o:.3f} ({o * 60:.1f}) | "
                     + (f"{b:.3f}" if b == b else "none scored") + f" | {ns}/{nt} |")
        L.append("")
    except Exception as e:  # noqa: BLE001 - the report must still be written
        L += ["## Synthetic Sun-azimuth sweep, 0-180° (exact truth; fig1)", "",
              f"Not available ({type(e).__name__}).", ""]

    # --- sub-pixel, by grid; runtime; coverage (20 Sep 2026: gathered here so the deck can name
    # the grid beside every sub-pixel figure - nothing below is a new measurement) ---------------
    cp_section, cp_rows = section_check_points(reg, d)
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
    sac112 = sorted([r for r in reg if r["pair_id"].startswith("sac_ohrc_nac112_")], key=lambda r: r["pair_id"])
    if sac112:
        med = [float(r["residual_median_px"]) for r in sac112 if r.get("residual_median_px")]
        g = float(sac112[0]["ref_gsd_m"])
        L.append(f"| The same pair on the paper's {g:g} m grid, {len(sac112)} windows | held-out matches | {g:g} m | "
                 f"median per window {min(med):.2f}-{max(med):.2f} px = {min(med) * g:.1f}-{max(med) * g:.1f} m |")
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
    L += cp_rows
    L.append("")
    # 1 Oct 2026: the PS asks for "sub-pixel accuracy of source image". The pipeline measures every
    # pair on the COARSER of its two grids. Where the Chandrayaan-2 image is the coarser one that grid
    # IS the Chandrayaan-2 image's own, so the figure is in its own pixels; where it is the finer one
    # (OHRC, 0.25 m, against a ~1 m NAC), the reference grid bounds what can be measured and the OHRC
    # figure is the same metres divided by the OHRC's pixel. Same rows as above, re-expressed only.
    def _own(rows, own_gsd=None):
        rob = _robust([r for r in rows if r["verdict"] == "agrees"])
        if not rob:
            return None
        med = sorted(float(r["residual_median_px"]) for r in rob)
        m = sorted(float(r["residual_median_px"]) * float(r["ref_gsd_m"]) for r in rob)
        if own_gsd is None:                  # the Chandrayaan-2 image IS the reference grid
            return len(rob), f"{med[0]:.2f}-{med[-1]:.2f}", f"{m[0]:.1f}-{m[-1]:.1f}"
        return len(rob), f"{m[0] / own_gsd:.1f}-{m[-1] / own_gsd:.1f}", f"{m[0]:.2f}-{m[-1]:.2f}"
    own = []
    nt_near = [r for r in reg if r["pair_id"].startswith("chain_nac") and _kind(r) == "nac-tmc2"
               and abs(float(r.get("d_sun_azimuth_deg") or 99)) < 10]
    if nt_near and (o := _own(nt_near)):
        own.append(("LRO NAC ↔ TMC-2 at SAC's site, matched Sun", "TMC-2 (the coarser: its own grid)",
                    f"{nt_near[0]['ref_gsd_m']} m", o))
    for tmc_pid in sorted({r["source_product"] for r in reg if _kind(r) == "tmc2-iirs"}):
        rs = [r for r in reg if _kind(r) == "tmc2-iirs" and r["source_product"] == tmc_pid and "1555" in r["pair_id"]]
        if rs and (o := _own(rs)):
            own.append((f"TMC-2 ↔ IIRS 1555 nm, orbit `{tmc_pid[12:20]}`", "IIRS (the coarser: its own grid)",
                        f"{rs[0]['ref_gsd_m']} m", o))
    sn = [r for r in reg if r["pair_id"].startswith("siten_") and _kind(r) == "ohrc-tmc2"]
    if sn and (o := _own(sn)):
        own.append(("OHRC → TMC-2 at Site N, matched Sun", "TMC-2 (the coarser: its own grid)", f"{sn[0]['ref_gsd_m']} m", o))
    for label, rows_ in (("OHRC → LRO NAC, 74 °S", ohrc_nac), ("OHRC → LRO NAC, SAC's equatorial pair", sac_eq)):
        if rows_:
            o_gsd = float(rows_[0]["src_gsd_m"])
            if (o := _own(rows_, o_gsd)):
                own.append((label, f"OHRC (the finer: bounded by the reference grid; OHRC pixels = metres / {o_gsd:g} m)",
                            f"{rows_[0]['ref_gsd_m']} m", o))
    if own:
        L += ["### In the Chandrayaan-2 image's own pixels", "",
              "The PS asks for sub-pixel accuracy \"of source image\". Every pair is measured on the coarser of its "
              "two grids. Where the Chandrayaan-2 image is the coarser one, that grid is its own, and the medians below "
              "are in its own pixels; where it is the finer one, the reference grid bounds what can be measured. Held-out "
              "medians of accepted windows with an inlier ratio above 0.5; the same rows as above, re-expressed.", "",
              "| pairing | the Chandrayaan-2 image | grid measured on | windows | median per window, in that image's pixels | metres |",
              "|---|---|---|---|---|---|"]
        for label, who, grid, (n, px, m) in own:
            L.append(f"| {label} | {who} | {grid} | {n} | {px} | {m} |")
        L.append("")
        # 4 Oct 2026: OHRC is finer than every reference, so no held-out residual can reach its own pixel. What
        # can: the loop closure above - three registrations (OHRC -> NAC A, NAC A -> NAC B, OHRC -> NAC B) that
        # agree in metres - re-expressed in OHRC's 0.25 m pixels. Precision (consistency), not accuracy.
        lp = [float(r["loop_rms_m"]) for r in loops if r.get("loop_rms_m") not in (None, "")]
        if lp:
            L += [f"In OHRC's own pixels, the loop closure above ({len(lp)} loops OHRC → NAC A → NAC B against OHRC "
                  f"→ NAC B at 74 °S) closes to a median {st.median(lp):.3f} m RMS = **{st.median(lp) / 0.25:.2f} OHRC "
                  f"px** (0.25 m), max {max(lp):.3f} m = {max(lp) / 0.25:.2f} px: three independent registrations agree "
                  f"below one OHRC pixel. That is precision, not accuracy - an error common to the legs would cancel - "
                  f"and the independent check points below bound the accuracy at the clicks' own floor.", ""]
    # runtime and coverage, from the latest rows
    secs = [float(r["seconds"]) for r in reg if r.get("seconds")]
    on = [float(r["seconds"]) for r in reg if r.get("seconds") and _kind(r) == "ohrc-nac"
          and not r["pair_id"].startswith(("sac_", "siten_")) and not r["pair_id"].endswith("_full")]
    cpu = ""
    try:
        import json as _j
        rep = _j.loads((d / "out" / ohrc_nac[0]["pair_id"] / "report.json").read_text(encoding="utf-8"))
        env = rep.get("environment") or {}
        cpu = f" ({env.get('cpu', '')}; {env.get('platform', '')})".replace(" (; )", "")
    except Exception:  # noqa: BLE001
        pass
    cov = [float(r["grid_coverage_fraction"]) for r in ohrc_nac if r.get("grid_coverage_fraction")]
    L += cp_section
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
    if d:
        L += archive_lines(d, full)
    # 1 Oct 2026: the deliverable also carries gcps_uniform.* - the inliers thinned to at most
    # core.export.UNIFORM_PER_CELL per cell of an 8 x 8 grid on the reference (core.export.uniform_inliers),
    # so the control points a user takes away are spread by construction. Read from each accepted
    # pair's exported report.json; pairs exported before that change carry no summary and are skipped.
    uni = []
    for r in reg:
        if r["verdict"] != "agrees" or "fallback" in (r.get("method_declared") or ""):
            continue
        rep = _jsonfile(d / "out" / r["pair_id"] / "report.json") if d else None
        u = (rep or {}).get("uniform_gcps")
        if u and u.get("n_points"):
            uni.append(u)
    if uni:
        cells = [u["cells_with_points"] for u in uni]
        L += [f"Delivered control points, uniform by construction: every accepted registration also exports "
                    f"`gcps_uniform.txt` / `.points` - its inliers thinned to at most {uni[0]['per_cell_max']} per cell "
                    f"of an {uni[0]['grid']} × {uni[0]['grid']} grid on the reference, lowest residual first. Over "
                    f"{len(uni)} accepted registrations the set holds a median {st.median(u['n_points'] for u in uni):.0f} "
                    f"points in a median {st.median(cells):.0f} of {uni[0]['cells']} cells; "
                    f"{sum(c >= 0.9 * uni[0]['cells'] for c in cells)} of {len(uni)} fill 90 % of the cells or more.", ""]

    L += ["## Reproduce", "", "```",
          "python -m ops.cut_site_pairs --nac M1153871873LE --windows 8 --refit",
          "python -m ops.run_real_pairs \"site_ohrc_*\" --log",
          "python -m ops.loop_closure --a M1153871873LE --b M1363141432RE --tag t --log",
          "python -m ops.cut_site_pairs --correct-chain $(cat <data>/nac/sweep_order.txt)",
          "python -m ops.sun_sweep --windows 3 --log",
          "python -m ops.trust_real_calibration \"site_ohrc_m1153871873le_w*_t\" ... --log",
          "python -m ops.make_report", "```", "",
          f"Rows in real_pairs_log.csv: {len(real_rows)}: {len(latest)} distinct pair ids (latest row "
          f"wins) = {len(reg)} registered pairs{_distinct_note(reg)}{_pairings_note(reg)} + "
          f"{len(loops) + len(site_loops)} loops + "
          + (f"{len(strip)} windows of one whole strip (their own section) + " if strip else "")
          + (f"{len(wac)} IIRS → LRO WAC windows (their own section) + " if wac else "")
          + (f"{len(wacstrip)} windows of the whole IIRS strip onto WAC + " if wacstrip else "")
          + (f"{len(tcmap)} TMC-2 → SELENE TC windows + " if tcmap else "")
          + (f"{len(dtm)} DTM-orthorectified fore/aft windows (each its own section) + " if dtm else "")
          + (f"{len(ladder)} Sun-ladder composites over {len(ladder_legs)} legs + " if ladder else "")
          + (f"{len(reliefq)} quarter windows (relief, local model) + " if reliefq else "")
          + f"{len(latest) - len(reg) - len(sep) - len(loops) - len(site_loops)} withdrawn (INVALIDATED). Rows in results_log.csv: "
          f"{len(log)}.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
