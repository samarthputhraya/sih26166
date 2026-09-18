"""Register every real site pair, export its deliverables, and log it.

    python -m ops.run_real_pairs "site_ohrc_m1153871873le_w*" --log
    python -m ops.run_real_pairs "site_ohrc_m1153871873le_w*"          # dry run: no log rows

For each pair directory (cut by `ops.cut_site_pairs`, so it carries geometry_prior.json):
  - run_all() on it, exactly as the CLI and the app do;
  - write the deliverables bundle to <data_path>/out/<pair_id>/ (core.export);
  - with --log: one row in evaluation/results_log.csv through core.pipeline._log_row
    (tier from the pair's own geometry_prior.json; robust held-out residuals, trust
    counts and archive offset in `notes`), and one structured row in
    evaluation/real_pairs_log.csv that names it.
A failed registration is logged too (allow_failed) - on real data a declared failure
is a result, and leaving it out would be choosing the evidence.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _data():
    p = ROOT / "data_path.txt"
    return pathlib.Path(p.read_text(encoding="utf-8-sig").strip()) if p.exists() else ROOT / "out"


def run_pair(pair_dir: pathlib.Path, log: bool = False, out_root=None, command=""):
    from core.export import _commit, export_bundle
    from core.pipeline import _log_row, resolve_pair, run_all
    from evaluation.real_eval import consistency_vs_prior, log_real

    prior = json.loads((pair_dir / "geometry_prior.json").read_text(encoding="utf-8"))
    src, ref = resolve_pair(str(pair_dir))
    r = run_all(src, ref)
    m = r["metrics"] or {}
    rel = r["reliability"] or {}
    c = rel.get("counts", {})
    g = rel.get("global", {})
    gsd = prior["reference"]["resampled_gsd_mpp"]
    cons = consistency_vs_prior(r["H_final"], prior["prior_H_source_to_reference"],
                                r["shape_reference"], gsd)
    out_root = pathlib.Path(out_root or (_data() / "out"))
    export_bundle(r, out_root / pair_dir.name, pair_dir.name, src, ref, prior=prior)

    def f(v, nd=3):
        return "n/a" if v is None else f"{v:.{nd}f}"
    notes = (f"REAL PAIR, no exact ground truth. held-out (20 %, never fitted): median "
             f"{f(m.get('residual_median_px'))} px, RMSE within 3 px {f(m.get('holdout_inlier_rmse_px'))} px "
             f"({f(m.get('holdout_inlier_frac'), 3)} of held-out within 3 px) on the reference "
             f"grid at {gsd} m/px. residual_px column = RMSE over ALL held-out matches incl. "
             f"outliers. | trust: verified {c.get('verified')}/weak {c.get('weak')}/no_evidence "
             f"{c.get('no_evidence')} of 64, area check {g.get('verdict')}; method declared "
             f"{r['declared']['method']} | archive geometry disagreement after coarse correction: "
             f"median {f(cons['median_px'], 1)} px = {f(cons['median_m'], 1)} m | "
             f"d_sun_az {prior.get('d_sun_azimuth_deg')} deg, d_inc {prior.get('d_incidence_deg')} deg, "
             f"scale {prior.get('scale_ratio')}x")
    row = {
        "pair_id": pair_dir.name, "tier": prior["tier"],
        "kind": "ohrc-nac" if "OHRC" in prior["source"]["instrument"] else "nac-nac",
        "method_declared": r["declared"]["method"],
        "source_product": prior["source"]["product_id"],
        "reference_product": prior["reference"]["product_id"],
        "window_lat": round(prior["window_centre_latlon"][0], 5),
        "window_lon": round(prior["window_centre_latlon"][1], 5),
        "src_gsd_m": prior["source"]["resampled_gsd_mpp"], "ref_gsd_m": gsd,
        "scale_ratio": prior.get("scale_ratio"),
        "d_sun_azimuth_deg": prior.get("d_sun_azimuth_deg"),
        "d_incidence_deg": prior.get("d_incidence_deg"),
        "n_matches": r["n_matches"], "inliers": m.get("inlier_count"),
        "inlier_ratio": m.get("inlier_ratio"),
        "grid_coverage_fraction": m.get("grid_coverage_fraction"),
        "residual_median_px": m.get("residual_median_px"),
        "holdout_inlier_rmse_px": m.get("holdout_inlier_rmse_px"),
        "holdout_inlier_frac": m.get("holdout_inlier_frac"),
        "verified": c.get("verified"), "weak": c.get("weak"), "no_evidence": c.get("no_evidence"),
        "verdict": g.get("verdict"),
        "archive_offset_px": cons["median_px"], "archive_offset_m": cons["median_m"],
        "seconds": round(r["seconds"], 1), "git_commit": _commit(), "command": command,
    }
    logged = None
    if log:
        ok, note = _log_row(pair_dir.name, prior["tier"], "ours_loftr+subpixel", r["metrics"] or {
            "status": "no_metrics"}, config=f"real {prior['source']['instrument']} -> "
            f"{prior['reference']['instrument']} window, {prior['window_m']:.0f} m square; "
            f"source resampled {prior['source']['resampled_gsd_mpp']} m, reference {gsd} m",
                            gsd_mpp=gsd, notes=notes, allow_failed=True)
        logged = ok
        if ok:
            row["notes"] = "results_log row: same pair_id, method ours_loftr+subpixel, same run"
            log_real(row)
        print(("  " + note) if ok else f"  NOT LOGGED: {note}")
    return r, row, logged


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pattern", help='pair directory glob under data/pairs, e.g. "site_ohrc_*"')
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--out", help="deliverables root (default <data_path>/out)")
    a = ap.parse_args(argv)
    dirs = sorted(pathlib.Path(p) for p in glob.glob(str(ROOT / "data" / "pairs" / a.pattern)))
    if not dirs:
        print(f"no pair directories match {a.pattern}")
        return 2
    cmd = "python -m ops.run_real_pairs " + " ".join(argv if argv is not None else sys.argv[1:])
    print(f"{'pair':34} {'n':>5} {'inl':>5} {'ratio':>6} {'cov':>5} {'hold_med':>8} "
          f"{'hold_rmse':>9} {'V':>3} {'N':>3} {'verdict':>12} {'arch_m':>7}")
    for d in dirs:
        r, row, _ = run_pair(d, log=a.log, out_root=a.out, command=cmd)

        def f(v, nd=3):
            return "n/a" if v is None else f"{v:.{nd}f}"
        print(f"{d.name:34} {row['n_matches']:>5} {row['inliers'] or 0:>5} "
              f"{f(row['inlier_ratio']):>6} {f(row['grid_coverage_fraction'], 2):>5} "
              f"{f(row['residual_median_px']):>8} {f(row['holdout_inlier_rmse_px']):>9} "
              f"{row['verified']!s:>3} {row['no_evidence']!s:>3} {row['verdict']!s:>12} "
              f"{f(row['archive_offset_m'], 1):>7}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
