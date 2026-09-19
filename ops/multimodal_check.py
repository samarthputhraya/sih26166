"""Did the multi-modal fallback register the infrared band correctly? Checked against the visible band.

    python -m ops.multimodal_check            # print the comparison, log nothing
    python -m ops.multimodal_check --log      # append one row per window to evaluation/multimodal_check.csv

On the Kaguya TC -> MI windows the SAME TC source window was registered twice: against MI 749 nm
(visible; LoFTR accepted) and against MI 1548 nm (near-infrared; LoFTR refused by the area check,
global-correlation fallback declared). Both references are the same MI map product, so the two
DECLARED transforms (H_final in the exported bundles) can be compared point for point on the
reference grid: how far apart do they put the same source point? That disagreement is the
fallback's error relative to the visible-band registration - the nearest thing to a truth the
infrared band has - and until 20 Sep 2026 it was never measured, so the deck could only say
"refused and fell back".

For the TC -> IIRS windows there is no visible band on the IIRS side; the two IIRS bands (999 and
1555 nm) are compared with each other. Agreement between two fallbacks is self-consistency, not
accuracy; disagreement proves at least one of them wrong.

Inputs: the bundles `ops.run_real_pairs` exported (<data>/out/<pair>/report.json: H_final, the
declared method, the inputs' sha256 and grids) and the latest real_pairs_log row of each pair.
A pairing is only compared when both bundles were cut from the same source file (sha256) onto
the same reference grid (transform and shape); anything else is skipped and said.

The comparison is on the reference pixel grid over a 20 x 20 lattice of points, exactly as
`evaluation.real_eval.consistency_vs_prior` measures the archive offset. Metres = pixels x ref_gsd_m.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "evaluation" / "multimodal_check.csv"
FIELDS = ["timestamp", "pair_id", "against", "kind", "window_lat", "window_lon", "ref_gsd_m",
          "declared", "verdict", "against_declared", "against_verdict", "against_inliers",
          "disagreement_median_px", "disagreement_p90_px", "disagreement_max_px",
          "mean_dx_px", "mean_dy_px", "disagreement_median_m",
          "archive_offset_m", "against_archive_offset_m", "fallback_ncc", "fallback_spread_px",
          "git_commit", "command", "notes"]

# (regex on the pair being checked, its counterpart, kind, what the comparison means)
PAIRINGS = [
    (re.compile(r"^(?P<stem>.+)_mi1548_(?P<w>w\d+)$"), "{stem}_mi749_{w}", "tc-mi",
     "declared transform on MI 1548 nm (infrared) vs the LoFTR registration on MI 749 nm "
     "(visible) of the same TC window"),
    (re.compile(r"^(?P<stem>.+)_iirs1000_(?P<w>w\d+)$"), "{stem}_iirs1555_{w}", "tc-iirs",
     "declared transform on IIRS 999 nm vs on IIRS 1555 nm, same TC window - self-consistency "
     "of two fallbacks, not accuracy"),
]


def _data() -> pathlib.Path:
    return pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())


def pairings(latest: dict) -> list[dict]:
    """The window pairings present in `latest` ({pair_id: latest real_pairs_log row})."""
    out = []
    for pid in sorted(latest):
        for rx, fmt, kind, note in PAIRINGS:
            m = rx.match(pid)
            if m:
                other = fmt.format(**m.groupdict())
                if other in latest:
                    out.append({"pair_id": pid, "against": other, "kind": kind, "note": note})
    return out


def _apply(H, pts):
    p = np.c_[pts, np.ones(len(pts))] @ np.asarray(H, np.float64).T
    return p[:, :2] / p[:, 2:3]


def disagreement(H_a, H_b, ref_shape, n=20) -> dict:
    """|H_a(H_b^-1 p) - p| over an n x n lattice of reference points p, in reference pixels:
    how far apart the two transforms put the same source point."""
    h, w = int(ref_shape[0]), int(ref_shape[1])
    gx, gy = np.meshgrid(np.linspace(0, w - 1, n), np.linspace(0, h - 1, n))
    p = np.c_[gx.ravel(), gy.ravel()]
    q = _apply(H_a, _apply(np.linalg.inv(np.asarray(H_b, np.float64)), p))
    d = q - p
    r = np.hypot(*d.T)
    return {"median_px": float(np.median(r)), "p90_px": float(np.percentile(r, 90)),
            "max_px": float(r.max()), "mean_dx_px": float(d[:, 0].mean()),
            "mean_dy_px": float(d[:, 1].mean())}


def _report(out_root: pathlib.Path, pid: str) -> dict | None:
    p = out_root / pid / "report.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def check_one(pr: dict, latest: dict, out_root: pathlib.Path) -> tuple[dict | None, str]:
    """One pairing -> (row, note). row is None when the two bundles are not comparable."""
    a, b = _report(out_root, pr["pair_id"]), _report(out_root, pr["against"])
    if a is None or b is None:
        return None, "bundle missing (run ops.run_real_pairs first)"
    ia, ib = a["inputs"], b["inputs"]
    same = (ia["source"].get("sha256") and ia["source"]["sha256"] == ib["source"].get("sha256")
            and ia["reference"].get("transform") == ib["reference"].get("transform")
            and list(ia["reference"].get("shape") or []) == list(ib["reference"].get("shape") or []))
    if not same:
        return None, "different source file or reference grid - not comparable"
    if a.get("H_final") is None or b.get("H_final") is None:
        return None, "no declared transform on one side"
    ra, rb = latest[pr["pair_id"]], latest[pr["against"]]
    gsd = float(ra["ref_gsd_m"])
    d = disagreement(a["H_final"], b["H_final"], ia["reference"]["shape"])
    fb = a.get("fallback") or {}
    da, db = a.get("declared") or {}, b.get("declared") or {}
    row = {
        "pair_id": pr["pair_id"], "against": pr["against"], "kind": pr["kind"],
        "window_lat": ra.get("window_lat"), "window_lon": ra.get("window_lon"), "ref_gsd_m": gsd,
        "declared": da.get("method"), "verdict": (a.get("trust") or {}).get("verdict"),
        "against_declared": db.get("method"), "against_verdict": (b.get("trust") or {}).get("verdict"),
        "against_inliers": rb.get("inliers"),
        "disagreement_median_px": round(d["median_px"], 4), "disagreement_p90_px": round(d["p90_px"], 4),
        "disagreement_max_px": round(d["max_px"], 4),
        "mean_dx_px": round(d["mean_dx_px"], 4), "mean_dy_px": round(d["mean_dy_px"], 4),
        "disagreement_median_m": round(d["median_px"] * gsd, 3),
        "archive_offset_m": ra.get("archive_offset_m"), "against_archive_offset_m": rb.get("archive_offset_m"),
        "fallback_ncc": None if fb.get("ncc") is None else round(float(fb["ncc"]), 3),
        "fallback_spread_px": fb.get("spread_px"),
        "notes": pr["note"],
    }
    return row, "ok"


def log_rows(rows: list[dict], path: pathlib.Path = OUT_CSV) -> None:
    """Append-only; the header is written once and must match FIELDS."""
    new = not path.exists() or path.stat().st_size == 0
    if not new:
        with open(path, encoding="utf-8-sig", newline="") as f:
            header = next(csv.reader(f))
        if header != FIELDS:
            raise RuntimeError(f"{path} header differs from FIELDS; extend the header line first")
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in FIELDS})


def latest_rows(path: pathlib.Path = OUT_CSV) -> dict:
    """{pair_id: latest row} of the check log."""
    out = {}
    if path.exists():
        for r in csv.DictReader(open(path, encoding="utf-8-sig")):
            out[r["pair_id"]] = r
    return out


def main(argv=None) -> int:
    from core.export import _commit
    from ops.freeze import latest_real
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--out", help="bundle root (default <data_path>/out)")
    a = ap.parse_args(argv)
    out_root = pathlib.Path(a.out) if a.out else _data() / "out"
    latest = latest_real()
    prs = pairings(latest)
    if not prs:
        print("no multi-modal window pairings in real_pairs_log.csv")
        return 2
    cmd = "python -m ops.multimodal_check " + " ".join(argv if argv is not None else sys.argv[1:])
    commit = _commit(("core", "evaluation", "ops"))
    rows, skipped = [], []
    print(f"{'pair':30} {'against':30} {'declared':14} {'median px':>9} {'p90 px':>7} {'median m':>9} "
          f"{'archive m':>9} {'against m':>9}")
    for pr in prs:
        row, note = check_one(pr, latest, out_root)
        if row is None:
            skipped.append((pr["pair_id"], note))
            print(f"{pr['pair_id']:30} {pr['against']:30} SKIPPED: {note}")
            continue
        row.update(timestamp=_dt.datetime.now().isoformat(timespec="seconds"), git_commit=commit,
                   command=cmd)
        rows.append(row)
        print(f"{row['pair_id']:30} {row['against']:30} {(row['declared'] or '')[:14]:14} "
              f"{row['disagreement_median_px']:9.3f} {row['disagreement_p90_px']:7.3f} "
              f"{row['disagreement_median_m']:9.2f} {float(row['archive_offset_m'] or 0):9.1f} "
              f"{float(row['against_archive_offset_m'] or 0):9.1f}")
    if a.log and rows:
        log_rows(rows)
        print(f"{len(rows)} row(s) -> {OUT_CSV.name}")
    return 0 if rows and not skipped else (1 if rows else 2)


if __name__ == "__main__":
    sys.exit(main())
