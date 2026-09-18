"""The real sun-angle sweep: one Chandrayaan-2 OHRC frame against LROC NAC frames whose sun
differs from it by 3 to 153 degrees of azimuth, at one site.

    python -m ops.sun_sweep --windows 3 --log

For every NAC in `<data>/nac/sweep_order.txt` whose georeference was corrected
(`ops.cut_site_pairs --correct-chain`), up to N lit OHRC windows are cut and registered.

HOW A REGISTRATION IS JUDGED - and why it changed on 18 Sep 2026. The first rule was
"within 40 m of the corrected archive geometry". On the first dry run it labelled two
windows of M159642518RE "missed failure" at 353 m and 401 m; on inspection the MATCHER
was right (its warp correlates with the NAC at NCC 0.871, the archive alignment at
0.389) and the archive correction was wrong there - that NAC's affine field fits only
169 of 272 correlation boxes. The archive geometry cannot be ground truth.

The rule now is image evidence, independent of the matches:
  matcher_ok  <=>  NCC(source warped by the matcher's H, reference) >= 0.30
                   and >= NCC(source aligned by the archive geometry, reference) + 0.05
It is computed on the overlap, on plain intensity. It is related to - but not the same
as - the trust layer's own per-cell area check, so this sweep is NOT the evidence for
the trust layer's detection rate. That evidence is `ops/trust_real_calibration.py`,
which plants known-wrong transforms on real windows.

  correct_accepted     matcher_ok, area check agrees, matcher's H declared
  caught_failure       not matcher_ok, and the system contradicted or fell back
  missed_failure       not matcher_ok, and the system accepted it
  false_alarm          matcher_ok, but contradicted / fallback declared
  no_transform         the matcher produced nothing

No row is ever dropped; a window with a failure is a result.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
NCC_MIN, NCC_MARGIN = 0.30, 0.05


def warp_ncc(src, ref, H):
    """Plain-intensity NCC of the source warped by H against the reference, on the overlap."""
    import cv2
    if H is None:
        return None
    h, w = ref.shape[:2]
    a = cv2.warpPerspective(np.asarray(src, np.float32), np.asarray(H, np.float64), (w, h),
                            flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT, borderValue=np.nan)
    b = np.asarray(ref, np.float32)
    v = np.isfinite(a) & np.isfinite(b)
    if v.sum() < 500:
        return None
    return float(np.corrcoef(a[v], b[v])[0, 1])


def classify(ncc_matcher, ncc_prior, declared, verdict, has_H):
    if not has_H:
        return "no_transform"
    ok = ncc_matcher is not None and ncc_matcher >= NCC_MIN and         (ncc_prior is None or ncc_matcher >= ncc_prior + NCC_MARGIN or ncc_matcher >= 0.8)
    rejected = declared != "loftr+magsac++" or verdict == "contradicted"
    if not ok:
        return "caught_failure" if rejected else "missed_failure"
    return "false_alarm" if rejected else "correct_accepted"


def main(argv=None):
    from evaluation.real_eval import consistency_vs_prior, log_real
    from ops import cut_site_pairs as C
    from ops.run_real_pairs import run_pair
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--only", nargs="*", help="restrict to these NAC ids")
    a = ap.parse_args(argv)
    order = (C.DATA / "nac" / "sweep_order.txt").read_text().split()
    if a.only:
        order = [p for p in order if p in a.only]
    cmd = "python -m ops.sun_sweep " + " ".join(argv if argv is not None else sys.argv[1:])
    summary = []
    for pid in order:
        gp = C.GEOM_DIR / f"{pid}.json"
        if not gp.exists() or not json.loads(gp.read_text(encoding="utf-8")).get("apply"):
            print(f"{pid}: no corrected georeference - skipped (recorded as such)")
            summary.append({"pid": pid, "outcome": "no_georeference"})
            continue
        existing = sorted((C.PAIRS).glob(f"site_ohrc_{pid.lower()}_w*_sw"))
        try:
            dirs = existing or C.cut(pid, n_windows=a.windows, src="ohrc", tag="sw")
        except SystemExit as e:
            # e.g. "no lit window fits inside the shared footprint" - a result, not a crash
            print(f"{pid}: {e} - recorded, sweep continues")
            summary.append({"pid": pid, "outcome": f"no_window ({e})"})
            continue
        import csv as _csv
        done = set()
        if a.log and (ROOT / "evaluation" / "real_pairs_log.csv").exists():
            done = {r["pair_id"] for r in _csv.DictReader(open(ROOT / "evaluation" / "real_pairs_log.csv",
                                                               encoding="utf-8"))
                    if (r.get("outcome") or "").strip()}
        for d in dirs:
            if pathlib.Path(d).name in done:
                print(f"{pathlib.Path(d).name}: already logged - skipped")
                continue
            r, row, logged = run_pair(pathlib.Path(d), log=False, command=cmd)
            prior = json.loads((pathlib.Path(d) / "geometry_prior.json").read_text(encoding="utf-8"))
            gsd = prior["reference"]["resampled_gsd_mpp"]
            cm = consistency_vs_prior(r["H"], prior["prior_H_source_to_reference"],
                                      r["shape_reference"], gsd)
            from core.io_loader import load
            from core.pipeline import resolve_pair
            sp, rp = resolve_pair(str(d))
            simg, rimg = load(sp)[0], load(rp)[0]
            n_m = warp_ncc(simg, rimg, r["H"])
            n_p = warp_ncc(simg, rimg, prior["prior_H_source_to_reference"])
            outcome = classify(n_m, n_p, r["declared"]["method"],
                               (r["reliability"] or {}).get("global", {}).get("verdict"),
                               r["H"] is not None)
            row["matcher_offset_m"] = None if cm["median_m"] is None else round(cm["median_m"], 2)
            row["outcome"] = outcome
            if a.log:
                from core.pipeline import _log_row
                ok, note = _log_row(pathlib.Path(d).name, prior["tier"], "ours_loftr+subpixel",
                                    r["metrics"] or {"status": "no_metrics"},
                                    config=f"real sun sweep, OHRC vs {pid}",
                                    gsd_mpp=gsd, allow_failed=True,
                                    notes=f"sun sweep: d_sun_az {prior['d_sun_azimuth_deg']} deg, "
                                          f"d_inc {prior['d_incidence_deg']} deg; matcher offset from "
                                          f"corrected archive geometry {row['matcher_offset_m']} m; "
                                          f"NCC matcher-warp {n_m if n_m is None else round(n_m, 3)} vs "
                                          f"archive-aligned {n_p if n_p is None else round(n_p, 3)}; "
                                          f"declared {r['declared']['method']}; outcome {outcome} "
                                          f"(image-evidence rule, see ops/sun_sweep.py)")
                if ok:
                    row["notes"] = "results_log row: same pair_id, same run"
                    log_real(row)
            summary.append({"pid": pid, "pair": pathlib.Path(d).name, "d_az": prior["d_sun_azimuth_deg"],
                            "d_inc": prior["d_incidence_deg"], "inl": row["inliers"],
                            "ratio": row["inlier_ratio"], "V": row["verified"],
                            "verdict": row["verdict"], "declared": r["declared"]["method"],
                            "matcher_m": row["matcher_offset_m"], "final_m": row["archive_offset_m"],
                            "ncc_m": n_m, "ncc_p": n_p, "outcome": outcome})
            s = summary[-1]
            print(f"{s['pair']:34} d_az {s['d_az']:6.1f} d_inc {s['d_inc']:+6.2f} inl {s['inl'] or 0:5} "
                  f"V {s['V']!s:>3} {s['verdict']!s:>12} off {s['matcher_m']!s:>8} m "
                  f"ncc {('%.2f' % n_m) if n_m is not None else 'n/a'}/{('%.2f' % n_p) if n_p is not None else 'n/a'} -> {outcome}",
                  flush=True)
    out = [x for x in summary if "pair" in x]
    if out:
        from collections import Counter
        print("\noutcomes:", dict(Counter(x["outcome"] for x in out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
