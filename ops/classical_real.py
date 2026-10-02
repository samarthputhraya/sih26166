"""Classical matchers on the headline real pairs, judged by the same rule as ours.

    python -m ops.classical_real                    # every axis, print the table, log nothing
    python -m ops.classical_real --log --resume     # what the evidence freeze runs (step `classic`)

Every reader asked the same thing of "6/6 accepted": accepted compared with what? This runs SIFT, ORB
and AKAZE on exactly the windows behind each headline - SAC's pair with the Suns 174 deg apart, the
Sun-elevation ladder on SAC's frame, Site N's three legs, the real viewpoint test, TMC-2 -> IIRS -
and puts their matches through EVERYTHING ours goes through after matching: MAGSAC++, the held-out
evaluate(), the independent area check and the fallback (core.pipeline.run_all(matches=...)). So
"accepted" means the same thing for every method: the area check agrees and no fallback was needed.

The classical side follows the MiLOI protocol (evaluation/miloi.py run_pair): both images on the
common ground grid, 8-bit, detector + the 0.75 ratio test, matches mapped back to each image's own
pixels. No gradient-orientation step: that is part of ours, not of theirs.

Rows go to evaluation/results_log.csv (outside the evidence stamp, like every results row), one per
pair and method, method `<NAME>+magsac++`, config `CLASSICAL-REAL ...`, and a `key=value | ...` tail
in notes that ops.make_report reads. The transforms go to <data>/out_classical/<pair>/<NAME>.json
for the independent check points (evaluation/check_points.py).
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REAL_LOG = ROOT / "evaluation" / "real_pairs_log.csv"
RESULTS_LOG = ROOT / "evaluation" / "results_log.csv"
PAIRS = ROOT / "data" / "pairs"
METHOD_NAMES = ("SIFT", "ORB", "AKAZE")
CONFIG_TAG = "CLASSICAL-REAL"

# (label, pair-id pattern, optional row filter). The labels are REPORT's.
AXES = (
    ("SAC's OHRC -> LRO NAC pair, Suns 174 deg apart (1.622 m grid)", r"^sac_ohrc_nac_w\d+$", None),
    ("the same pair on SAC's 1.1179 m grid", r"^sac_ohrc_nac112_w\d+$", None),
    ("Sun raised up to 41.7 deg, azimuth within 20 deg (SAC's frame)", r"^sac_ohrclroc_nacm\w+_c\d+$",
     lambda r: float(r["d_sun_azimuth_deg"]) <= 20.0),
    ("Sun 154-177 deg away in azimuth (SAC's frame)", r"^sac_ohrclroc_nacm\w+_c\d+$",
     lambda r: float(r["d_sun_azimuth_deg"]) > 20.0),
    ("Site N, OHRC -> TMC-2 (Suns matched)", r"^siten_ohrc\d+_tmc\d{8}_c\d+$", None),
    ("Site N, OHRC -> LRO NAC", r"^siten_ohrc\d+_nacm\w+_c\d+$", None),
    ("Site N, LRO NAC -> TMC-2", r"^siten_nacm\w+_tmc\d{8}_c\d+$", None),
    ("viewpoint: OHRC -> OHRC, views 40 deg apart", r"^siten_ohrc\d+_ohrc\d+_c\d+$", None),
    ("TMC-2 -> IIRS beyond 850 nm (multi-modal)", r"^chain_tmc\d{8}_iirs(999|1555|2381|3223)_w\d+$", None),
    ("TMC-2 -> IIRS 746 nm (visible control)", r"^chain_tmc\d{8}_iirs746_w\d+$", None),
)


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def latest_real(log=REAL_LOG) -> dict:
    """{pair_id: latest row}, withdrawn pairs left out - the same rule as ops.freeze.latest_real
    (the LATEST row decides; its verdict or notes say INVALIDATED)."""
    out = {}
    for r in read_csv(log):
        out[r["pair_id"]] = r
    return {k: r for k, r in out.items()
            if (r.get("verdict") or "") != "INVALIDATED" and "INVALIDATED" not in (r.get("notes") or "")}


def axis_pairs(latest: dict) -> list[tuple[str, list[str]]]:
    out = []
    for label, pat, keep in AXES:
        ids = sorted(k for k, r in latest.items() if re.match(pat, k) and (keep is None or keep(r)))
        out.append((label, ids))
    return out


def ours_accepted(r: dict) -> bool:
    """The rule REPORT applies to our rows: the area check agrees and the matcher's answer stood."""
    return r.get("verdict") == "agrees" and "fallback" not in (r.get("method_declared") or "")


def accepted(verdict, declared) -> bool:
    return verdict == "agrees" and "fallback" not in (declared or "")


def parse_notes(notes: str) -> dict:
    """The `key=value | key=value` tail this module writes into a row's notes."""
    out = {}
    for part in (notes or "").split("|"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def classical_rows(log=RESULTS_LOG) -> dict:
    """{(pair_id, NAME): parsed latest row} of this module's rows in results_log.csv."""
    out = {}
    for r in read_csv(log):
        if not (r.get("config") or "").startswith(CONFIG_TAG):
            continue
        name = (r.get("method") or "").split("+")[0]
        out[(r["pair_id"], name)] = {**parse_notes(r.get("notes")), "method": r["method"]}
    return out


def match_classical(src_path, ref_path, name):
    """The MiLOI protocol's classical side: (src_pts, ref_pts) in each image's own pixels, or error."""
    from baselines.run_all_baselines import METHODS as BASE, to_uint8
    from baselines.settings import RATIO_TEST
    from core.io_loader import load
    from core.scale import to_common_gsd, to_original
    a, ma = load(src_path)
    b, mb = load(ref_path)
    a_s, b_s, _gsd, f = to_common_gsd(a, ma, b, mb)
    try:
        s, q, _c, _t = dict(BASE)[name](to_uint8(a_s), to_uint8(b_s), ratio=RATIO_TEST)
    except Exception as e:  # noqa: BLE001 - a dead detector is a failed pair, not a dead run
        return np.zeros((0, 2)), np.zeros((0, 2)), f"{type(e).__name__}: {e}"
    if not len(s):
        return np.zeros((0, 2)), np.zeros((0, 2)), None
    return to_original(s, f["a"]), to_original(q, f["b"]), None


def judge(pair_id: str, name: str) -> dict:
    """One classical method on one pair, judged by run_all's own MAGSAC++, evaluate(), area check
    and fallback."""
    from core.pipeline import resolve_pair, run_all
    t0 = time.perf_counter()
    sp, rp = resolve_pair(str(PAIRS / pair_id))
    s, q, err = match_classical(sp, rp, name)
    r = run_all(sp, rp, matches=(np.asarray(s, np.float32), np.asarray(q, np.float32), None))
    rel = r.get("reliability") or {}
    g, c = rel.get("global", {}), rel.get("counts", {})
    declared = r["declared"]["method"].replace("loftr", name.lower())
    m = r.get("metrics") or {}
    src_in = r.get("src_inliers")
    return {"pair_id": pair_id, "method": name, "n_matches": int(len(s)), "error": err,
            "inliers": int(len(src_in)) if (r.get("H") is not None and src_in is not None) else 0,
            "verdict": g.get("verdict"), "declared": declared,
            "accepted": accepted(g.get("verdict"), declared),
            "verified": c.get("verified"), "weak": c.get("weak"), "no_evidence": c.get("no_evidence"),
            "residual_median_px": m.get("residual_median_px"), "holdout_inlier_frac": m.get("holdout_inlier_frac"),
            "metrics": m, "gsd_mpp": r.get("gsd_mpp"),
            "H": None if r.get("H") is None else np.asarray(r["H"]).tolist(),
            "H_final": None if r.get("H_final") is None else np.asarray(r["H_final"]).tolist(),
            "seconds": round(time.perf_counter() - t0, 2)}


def notes_of(j: dict, commit: str) -> str:
    def f(v):
        return "None" if v is None else (f"{v:.4f}" if isinstance(v, float) else str(v))
    keys = ("verdict", "declared", "accepted", "verified", "weak", "no_evidence", "n_matches", "inliers",
            "residual_median_px", "holdout_inlier_frac", "seconds")
    tail = " | ".join(f"{k}={f(j[k])}" for k in keys)
    return (f"classical baseline judged by the same MAGSAC++, held-out evaluate(), area check and "
            f"fallback as ours | {tail} | error={j['error'] or 'None'} | commit={commit}")


def write_sidecar(j: dict, out_root: pathlib.Path) -> None:
    d = out_root / j["pair_id"]
    d.mkdir(parents=True, exist_ok=True)
    keep = {k: v for k, v in j.items() if k != "metrics"}
    (d / f"{j['method']}.json").write_text(json.dumps(keep, indent=1, default=str), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", action="store_true", help="append one results_log row per pair and method")
    ap.add_argument("--resume", action="store_true", help="skip pair x method rows already logged at HEAD")
    ap.add_argument("--methods", nargs="+", default=list(METHOD_NAMES), choices=METHOD_NAMES)
    ap.add_argument("--axis", type=int, action="append", help="only these axis numbers (0-based)")
    ap.add_argument("--limit", type=int, help="at most this many pairs per axis (a dry run)")
    a = ap.parse_args(argv)
    from core.export import _commit
    commit = _commit(("core", "evaluation", "ops"))
    if a.log:
        from core.pipeline import _log_preflight
        err = _log_preflight()
        if err:
            print(err)
            return 3
    out_root = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip()) / "out_classical"
    latest = latest_real()
    logged = classical_rows() if a.resume else {}
    done = {k for k, v in logged.items() if v.get("commit") == commit}
    table = []
    for i, (label, ids) in enumerate(axis_pairs(latest)):
        if a.axis and i not in a.axis:
            continue
        ids = ids[:a.limit] if a.limit else ids
        ours = sum(ours_accepted(latest[p]) for p in ids)
        counts = {}
        for name in a.methods:
            n_acc = 0
            for pid in ids:
                if (pid, name) in done:
                    n_acc += logged[(pid, name)].get("accepted") == "True"
                    continue
                j = judge(pid, name)
                n_acc += j["accepted"]
                write_sidecar(j, out_root)
                print(f"  {pid} {name}: {j['n_matches']} matches, {j['inliers']} inliers, verdict {j['verdict']}, "
                      f"{j['declared']} -> {'ACCEPTED' if j['accepted'] else 'not accepted'} ({j['seconds']} s)",
                      flush=True)
                if a.log:
                    from core.pipeline import _log_row
                    tier = latest[pid].get("tier") or "real"
                    m = dict(j["metrics"]) if j["metrics"] else {"status": "no_matches"}
                    ok, note = _log_row(pid, tier, f"{name}+magsac++", m,
                                        config=(f"{CONFIG_TAG}: {name} raw matches (ratio test 0.75) on the "
                                                f"common-GSD images; MAGSAC++, evaluate(), area check and "
                                                f"fallback exactly as ours"),
                                        gsd_mpp=j["gsd_mpp"], notes=notes_of(j, commit), allow_failed=True)
                    if not ok:
                        print(f"  NOT LOGGED: {note}")
                        return 4
            counts[name] = n_acc
        table.append((label, len(ids), ours, counts))
    print(f"\n{'axis':66s} {'windows':>7s} {'ours':>5s} " + " ".join(f"{n:>6s}" for n in a.methods))
    for label, n, ours, counts in table:
        print(f"{label:66s} {n:7d} {ours:5d} " + " ".join(f"{counts[m]:6d}" for m in a.methods))
    return 0


if __name__ == "__main__":
    sys.exit(main())
