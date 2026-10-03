"""The Sun reference finder run over the WHOLE OHRC archive: for every OHRC observation in PRADAN's
footprint catalogue, the images that cover it, best Sun first.

    python -m ops.reference_index            # -> evaluation/reference_index.json (and the console's copy)

`ops/find_reference.py` answers the question for one frame; this answers it for all of them, once,
so the console can look any OHRC frame up without a server, and REPORT can say how much of the
archive already has a well-lit partner. Candidates are the same as the finder's: every PRADAN
product (OHRC, TMC-2 nadir, IIRS) and every LRO NAC this machine has a page or an ODE record for -
so the NAC column is partial and the Chandrayaan-2 columns are complete. An OHRC observation listed
twice (one copy per ground station) is indexed once. Deterministic: no randomness, no network.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ops import find_reference as F       # noqa: E402

OUT = ROOT / "evaluation" / "reference_index.json"
WEB_COPY = ROOT / "web" / "reference_index.json"
TOP = 8
MIN_OVERLAP = 0.2


def _obs_key(pid: str) -> str:
    """One OHRC observation: the product id up to its start time (the station suffix differs)."""
    return pid.split("_d_img_")[0]


def build(records=None, top=TOP, min_overlap=MIN_OVERLAP) -> dict:
    records = records if records is not None else F.pradan_records() + F.nac_records()
    ohrc, seen = [], set()
    for r in records:
        if r["instrument"] == "OHRC" and r.get("time") and _obs_key(r["id"]) not in seen:
            seen.add(_obs_key(r["id"]))
            ohrc.append(r["id"])
    targets = []
    for pid in sorted(ohrc):
        tgt, cands = F.rank(pid, records, min_overlap)
        # the same observation from another station is the frame itself, not a reference
        cands = [c for c in cands if _obs_key(c["id"]) != _obs_key(pid)]
        la, lo = tgt["centre"]
        targets.append({
            "id": pid, "time": tgt["time"], "centre": [round(la, 4), round(lo, 4)],
            "incidence": round(tgt["incidence"], 2), "azimuth": round(tgt["azimuth"], 2),
            "n_candidates": len(cands),
            "candidates": [{"id": c["id"], "instrument": c["instrument"], "time": c["time"],
                            "overlap": round(c["overlap"], 3), "sun_angle": round(c["sun_angle"], 2),
                            "d_azimuth": round(c["d_azimuth"], 2), "incidence": round(c["incidence"], 2)}
                           for c in cands[:top]]})
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip()
    except OSError:
        commit = None
    counts = {}
    for r in records:
        counts[r["instrument"]] = counts.get(r["instrument"], 0) + 1
    return {"generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "commit": commit, "min_overlap": min_overlap, "top": top,
            "catalogue_records": counts, "n_ohrc_observations": len(targets), "targets": targets}


def _t(s):
    """UTC, naive: PRADAN's times end in Z, LROC's and ODE's carry no zone."""
    if not s:
        return None
    try:
        return _dt.datetime.fromisoformat(str(s).strip().replace("Z", "").replace(" ", "T")[:26]).replace(tzinfo=None)
    except ValueError:
        return None


SAME_ORBIT_S = 2 * 3600       # Chandrayaan-2's orbit is ~2 h: closer than that is the same pass


def summary(index: dict) -> dict:
    """How much of the archive already has a well-lit partner. `other_orbit_*` leaves out images taken
    within 2 h of the frame (the same pass: TMC-2 and IIRS often image alongside OHRC), so it counts
    only partners from a different orbit - the case the finder exists for."""
    n = len(index["targets"])
    best, other, inst = [], [], {}
    for t in index["targets"]:
        c = t["candidates"]
        best.append(c[0]["sun_angle"] if c else None)
        if c:
            inst[c[0]["instrument"]] = inst.get(c[0]["instrument"], 0) + 1
        t0 = _t(t["time"])
        o = [x for x in c if t0 and _t(x["time"]) and abs((_t(x["time"]) - t0).total_seconds()) >= SAME_ORBIT_S]
        other.append(o[0]["sun_angle"] if o else None)
    have = [b for b in best if b is not None]
    oth = [b for b in other if b is not None]
    return {"n": n, "with_any": len(have), "within_5": sum(b <= 5 for b in have),
            "within_10": sum(b <= 10 for b in have), "none": n - len(have), "best_instrument": inst,
            "other_orbit_within_5": sum(b <= 5 for b in oth), "other_orbit_within_10": sum(b <= 10 for b in oth)}


def main(argv=None) -> int:
    idx = build()
    text = json.dumps(idx, indent=1)
    OUT.write_text(text, encoding="utf-8")
    WEB_COPY.write_text(json.dumps(idx, separators=(",", ":")), encoding="utf-8")
    s = summary(idx)
    print(f"{s['n']} OHRC observations indexed -> {OUT.name} ({len(text) / 1e6:.2f} MB) and {WEB_COPY}")
    print(f"  best reference within 5 deg of its Sun: {s['within_5']}; within 10: {s['within_10']}; "
          f"from ANOTHER orbit within 5: {s['other_orbit_within_5']}, within 10: {s['other_orbit_within_10']}; "
          f"no image covering >= {MIN_OVERLAP:.0%}: {s['none']}; best by instrument {s['best_instrument']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
