"""Write REPORT.md - the evaluation report - from the evidence files alone.

    python -m ops.make_report            # -> REPORT.md at the repo root

Nothing in the report is typed: every number is read from
    evaluation/results_log.csv            (the 15-column evidence log, Invariant 1)
    evaluation/real_pairs_log.csv         (real-pair structure: sun, window, loops, outcomes)
    evaluation/trust_real_calibration.csv (planted-failure trials on real windows)
    <data>/download_manifest_done.csv     (every downloaded product with its sha256)
Where a pair was run more than once, the LATEST row wins and the table says how many
rows exist. Re-run this after the evidence freeze; never edit REPORT.md by hand.
"""
from __future__ import annotations

import csv
import datetime as _dt
import pathlib
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
    reg = [r for r in latest.values() if not r["pair_id"].startswith("loop_")]
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
    man = _rows(d / "download_manifest_done.csv") + _rows(d / "nac_sweep_manifest_done.csv") if d else []
    if man:
        by = Counter(r["group"] for r in man)
        L += ["## Products downloaded (sha256 recorded)", "",
              f"{len(man)} files: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())) +
              f". Full list with URLs and sha256: `{d / 'download_manifest_done.csv'}` and "
              f"`nac_sweep_manifest_done.csv`. The Chandrayaan-2 OHRC frame "
              f"`ch2_ohr_ncp_20200229T0739312111_d_img_d18` was already on disk (archive.org mirror).", ""]

    # --- cross-sensor, same ground -----------------------------------------------------
    ohrc_nac = sorted([r for r in reg if r["kind"] == "ohrc-nac" and not r.get("outcome")],
                      key=lambda r: r["pair_id"])
    L += section_pairs("Chandrayaan-2 OHRC → LRO NAC (cross-sensor, cross-mission)", ohrc_nac,
                       "Windows cut at 0.25 m (OHRC) and the NAC's native ~0.9-1.25 m over the same "
                       "ground on a south-polar-stereographic grid (`ops/cut_site_pairs.py`). "
                       "Archive offset = how far the registration moved the source from where the two "
                       "archives' (corrected) geometry put it - a property of the archives.")
    nac_nac = sorted([r for r in reg if r["kind"] == "nac-nac" and not r.get("outcome")], key=lambda r: r["pair_id"])
    if nac_nac:
        L += section_pairs("LRO NAC → LRO NAC (same sensor; loop legs)", nac_nac, "Same sensor - NOT cross-sensor.")
    other = sorted([r for r in reg if r["kind"] not in ("ohrc-nac", "nac-nac")], key=lambda r: r["pair_id"])
    mm = [r for r in reg if "multi-modal" in r["tier"] or "tc-mi" in r["tier"]]
    if mm:
        L += section_pairs("Kaguya TC → Kaguya MI (visible and 1548 nm infrared)",
                           sorted(mm, key=lambda r: r["pair_id"]),
                           "Tier C rows are multi-modal (visible vs near-infrared). On them the declared "
                           "method is the global-correlation fallback; compare its archive offset with the "
                           "visible-band rows on the same windows.")

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
        bins = [(0, 10), (10, 30), (30, 60), (60, 90), (90, 120), (120, 181)]
        L += ["## Real sun-angle sweep (one OHRC frame vs LRO NAC frames)", "",
              "Outcome by image evidence (`ops/sun_sweep.py` docstring: the matcher's warp must "
              "correlate with the reference at NCC ≥ 0.30 and better than the archive alignment). "
              "This sweep is NOT the trust layer's detection evidence - see the next section.", "",
              "| Δsun az (deg) | windows | NAC frames | registered & verified | failed & caught | failed, not caught | correct but flagged | median inliers |",
              "|---|---|---|---|---|---|---|---|"]
        for lo, hi in bins:
            b = [r for r in sweep if lo <= float(r["d_sun_azimuth_deg"]) < hi]
            if not b:
                continue
            c = Counter(r["outcome"] for r in b)
            L.append(f"| {lo}-{hi if hi < 181 else 180} | {len(b)} | {len({r['reference_product'] for r in b})} | "
                     f"{c['correct_accepted']} | {c['caught_failure']} | {c['missed_failure']} | "
                     f"{c['false_alarm']} | {int(st.median([float(r['inliers'] or 0) for r in b]))} |")
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
        L += ["## Viewpoint (synthetic, exact truth)", "",
              "| pair | rmse_gt_px | inliers | ratio | coverage |", "|---|---|---|---|---|"]
        for r in vp[-40:]:
            L.append(f"| `{r['pair_id']}` | {_f(r['rmse_gt_px'])} | {r['inlier_count']} | "
                     f"{_f(r['inlier_ratio'])} | {_f(r['grid_coverage_fraction'], 2)} |")
        L.append("")

    L += ["## Reproduce", "", "```",
          "python -m ops.cut_site_pairs --nac M1153871873LE --windows 8 --refit",
          "python -m ops.run_real_pairs \"site_ohrc_*\" --log",
          "python -m ops.loop_closure --a M1153871873LE --b M1363141432RE --tag t --log",
          "python -m ops.cut_site_pairs --correct-chain $(cat <data>/nac/sweep_order.txt)",
          "python -m ops.sun_sweep --windows 3 --log",
          "python -m ops.trust_real_calibration \"site_ohrc_m1153871873le_w*_t\" ... --log",
          "python -m ops.make_report", "```", "",
          f"Rows in real_pairs_log.csv: {len(real_rows)} ({len(latest)} distinct pairs/loops; where a "
          f"pair was re-run, the latest row is shown). Rows in results_log.csv: {len(log)}.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
