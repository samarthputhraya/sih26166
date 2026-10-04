"""The Sun ladder: register across Suns 60-120 deg apart through an image lit in between.

    python -m ops.sun_ladder --plan                 # which windows, which intermediates (no writes)
    python -m ops.sun_ladder --cut                  # cut both legs of every ladder, print their ids
    python -m ops.run_real_pairs "ladder_*" --log   # register the legs (the freeze's `real` step)
    python -m ops.sun_ladder --log                  # compose, judge, cross-check; one row per ladder

WHY. Registered directly, the OHRC frame at 74 S fails against every LROC NAC whose Sun is 60-120 deg away
in azimuth (REPORT, "Real sun-angle sweep": 0 of 12). A quarter-turn of the Sun changes which slopes are lit,
so edges present in one image are missing from the other, and no re-encoding recovers them. Near 0 deg and
near 180 deg it holds (0-60 deg: 41 of 42; 120-180 deg: 10 of 15). So a ladder never asks one registration to
cross the gap: OHRC -> M, then M -> T, where M is an LROC NAC over the same ground whose Sun is

  - outside 60-120 deg of the OHRC's (and M registered correctly in the sweep), and
  - within LINK_MAX_DEG of T's.

Both legs are cut over exactly the failing window's ground and size (`ops.cut_site_pairs.cut`, centres
reused), registered by `run_all` like any pair, and judged by their own area checks, each inside the Sun range
where that check is calibrated. A ladder is ACCEPTED only if both legs are (`agrees`, matcher declared).

WHAT IS NOT CLAIMED. At 60-120 deg the image cannot judge even a perfect alignment (plain |NCC| ~ 0: the
sweep calls those windows inconclusive), so a ladder's composite is not judged against T's pixels. Its
evidence is its two links, and - where two intermediates cover the window - the two composites compared
with each other (two independent ladders that are each right agree; a wrong one does not), as in
`ops/loop_closure.py`. The composite is also compared with the failed direct registration, which says how
far that one was off. Independent hand-clicked check points on these windows are scored by
`evaluation/check_points.py` like any other pair, if they exist.

Rows go to evaluation/real_pairs_log.csv (pair ids `ladder_<target window>_via_<M>`), REPORT renders
them in their own section; they never join the site_ tables or the window counts.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAIRS = ROOT / "data" / "pairs"
LOG = ROOT / "evaluation" / "real_pairs_log.csv"
GAP = (60.0, 120.0)          # the band the direct sweep fails in (REPORT: 0 of 12)
LINK_MAX_DEG = 60.0          # an M -> T link stays inside the 0-60 deg band, where 41 of 42 register
PER_WINDOW = 2               # up to two intermediates per window: the second one is the cross-check
SWEEP = "site_ohrc_{nac}_w{k}_sw"


def _data():
    p = ROOT / "data_path.txt"
    return pathlib.Path(p.read_text(encoding="utf-8-sig").strip()) if p.exists() else ROOT / "external_data"


def _dz(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _latest(rows=None):
    rows = rows if rows is not None else list(csv.DictReader(open(LOG, encoding="utf-8")))
    out = {}
    for r in rows:
        out[r["pair_id"]] = r
    return out


def _inside(corners, lat, lon):
    from matplotlib.path import Path as _P
    poly = _P([(corners[k][1], corners[k][0]) for k in ("Upper left", "Upper right", "Lower right", "Lower left")])
    return bool(poly.contains_point((lon, lat)))


def _nacs_and_targets(latest):
    nacs, targets = {}, []
    for pid, r in latest.items():
        if not (pid.startswith("site_ohrc_m") and pid.endswith("_sw")):
            continue
        g = json.loads((PAIRS / pid / "geometry_prior.json").read_text(encoding="utf-8"))
        ref = g["reference"]
        n = nacs.setdefault(ref["product_id"], {"az": ref["sun_azimuth_deg_from_north"],
                                                "corners": ref["corners_latlon"], "ok": False,
                                                "d_az": float(r["d_sun_azimuth_deg"])})
        n["ok"] |= r.get("outcome") == "correct_accepted"
        if GAP[0] <= float(r["d_sun_azimuth_deg"]) < GAP[1]:
            targets.append((pid, ref["product_id"], g))
    return nacs, targets


def plan(rows=None):
    """[{target pair id, T, window, centre, window_m, d_az OHRC-T, chains: [{"chain": [M...], "d": [link deg...]}]}]

    Everything is read from the sweep's own pairs and rows: the targets are the sweep windows whose Sun
    azimuths are 60-120 deg apart.
      One step, O -> M -> T: M is a sweep NAC that registered correctly there (outcome correct_accepted on at
        least one window), outside the gap, covering the window's centre, not the target's own observation
        (LE/RE share a Sun), within LINK_MAX_DEG of T. Up to PER_WINDOW, closest Sun to T first.
      Two steps, O -> M1 -> M2 -> T, where a window's only one-step intermediates are opposite-Sun images
        (every O -> M link > 120 deg): M2 is a NAC IN the gap (its Sun 60-120 deg from the OHRC's, so never
        registered to the OHRC directly) within LINK_MAX_DEG of T, and M1 a near-Sun NAC (O -> M1 < 60 deg,
        correct in the sweep) within LINK_MAX_DEG of M2; all three cover the window. Up to PER_WINDOW."""
    nacs, targets = _nacs_and_targets(_latest(rows))
    out = []
    for pid, T, g in sorted(targets):
        lat, lon = g["window_centre_latlon"]
        cover = {M: v for M, v in nacs.items() if M[:-2] != T[:-2] and _inside(v["corners"], lat, lon)}
        one = sorted((round(_dz(v["az"], nacs[T]["az"]), 1), M, v["d_az"]) for M, v in cover.items()
                     if v["ok"] and not GAP[0] <= v["d_az"] < GAP[1])
        chains = [{"chain": [M], "d": [d_om, d_mt]} for d_mt, M, d_om in one if d_mt <= LINK_MAX_DEG][:PER_WINDOW]
        if all(c["d"][0] > GAP[1] for c in chains):
            two = []
            for M2, v2 in cover.items():
                d2t = _dz(v2["az"], nacs[T]["az"])
                if not GAP[0] <= v2["d_az"] < GAP[1] or d2t > LINK_MAX_DEG:
                    continue
                for M1, v1 in cover.items():
                    d12 = _dz(v1["az"], v2["az"])
                    if v1["ok"] and v1["d_az"] < GAP[0] and d12 <= LINK_MAX_DEG and M1[:-2] != M2[:-2]:
                        two.append((round(d12 + d2t, 1), M1, M2, v1["d_az"], round(d12, 1), round(d2t, 1)))
            chains += [{"chain": [M1, M2], "d": [d1, d12, d2t]}
                       for _, M1, M2, d1, d12, d2t in sorted(two)][:PER_WINDOW]
        out.append({"target": pid, "T": T, "window": pid.split("_")[3], "centre": g["window_centre_map_m"],
                    "latlon": [lat, lon], "window_m": g["window_m"], "d_az": float(g["d_sun_azimuth_deg"]),
                    "chains": chains})
    return out


def leg_ids(item, chain):
    """The leg ids of one chain, in order: O -> M1 [-> M2] -> T."""
    t = f"{item['T'].lower()}_{item['window']}"
    ms = [m.lower() for m in chain]
    legs = [f"ladder_{t}_ohrc_{ms[0]}"]
    legs += [f"ladder_{t}_{a}_to_{b}" for a, b in zip(ms, ms[1:])]
    return legs + [f"ladder_{t}_{ms[-1]}"]


def ladder_id(item, chain):
    return f"ladder_{item['T'].lower()}_{item['window']}_via_" + "_".join(m.lower() for m in chain)


def cut_all(items, only=None):
    """Every leg of every chain, centred on the failing window. A leg keeps the window's ground unless its
    reference is finer than T's, when it is the central 640 px of that reference (the matcher's tile:
    `core.matcher` refuses larger pairs). Legs already cut are kept; `only`: leg ids to (re)cut."""
    from ops import cut_site_pairs as C
    ids = []
    for it in items:
        c = [it["centre"]]
        for ch in it["chains"]:
            nodes = ["ohrc"] + list(ch["chain"]) + [it["T"]]
            for (src, ref), leg in zip(zip(nodes, nodes[1:]), leg_ids(it, ch["chain"])):
                if only is not None and leg not in only:
                    continue
                if only is None and (PAIRS / leg / "geometry_prior.json").exists():
                    continue
                w = it["window_m"] if ref == it["T"] else min(it["window_m"], 640 * C._frame(ref)[3])
                if C.cut(ref, src=src, centres=c, window_m=w, pair_ids=[leg]):
                    ids.append(leg)
    return ids


def _bundle(pid, out_root):
    rep = json.loads((out_root / pid / "report.json").read_text(encoding="utf-8"))
    prior = json.loads((PAIRS / pid / "geometry_prior.json").read_text(encoding="utf-8"))
    return rep, prior


def _accepted(rep):
    return ((rep.get("trust") or {}).get("verdict") == "agrees"
            and (rep.get("declared") or {}).get("method") == "loftr+magsac++" and rep.get("H_final") is not None)


def _src_points(pid, out_root):
    with open(out_root / pid / "matches.csv", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(line for line in f if not line.startswith("#"))]
    return np.array([[float(r["src_x"]), float(r["src_y"])] for r in rows if r["is_inlier"] == "1"])


def compose(item, out_root):
    """Per chain: the composite OHRC-map -> T-map transform (the legs' map transforms, in order), the links'
    verdicts, and the points (OHRC map metres: the first leg's inliers) it is compared on."""
    from evaluation.real_eval import _apply, map_transform, pixel_to_map
    res = []
    for ch in item["chains"]:
        legs = leg_ids(item, ch["chain"])
        if not all((out_root / p / "report.json").exists() for p in legs):
            continue
        b = [_bundle(p, out_root) for p in legs]
        ok = all(_accepted(r) for r, _ in b)
        T = None
        if all(r.get("H_final") is not None for r, _ in b):
            T = np.eye(3)
            for r, pr in b:
                T = map_transform(r["H_final"], pr["source"]["transform"], pr["reference"]["transform"]) @ T
        pts = _src_points(legs[0], out_root)
        pts = _apply(pixel_to_map(b[0][1]["source"]["transform"]), pts) if len(pts) else pts
        res.append({"chain": ch["chain"], "d": ch["d"], "legs": legs, "accepted": ok, "T": T, "pts": pts,
                    "verdicts": [(r.get("trust") or {}).get("verdict") for r, _ in b],
                    "commits": sorted({str(r.get("git_commit")) for r, _ in b})})
    return res


def _disagree(Ta, Tb, pts, gsd):
    from evaluation.real_eval import _apply
    r = np.hypot(*(_apply(Ta, pts) - _apply(Tb, pts)).T)
    return {"rms_m": float(np.sqrt(np.mean(r ** 2))), "p90_m": float(np.percentile(r, 90)),
            "rms_px": float(np.sqrt(np.mean(r ** 2)) / gsd), "n": int(len(r))}


def run(log=False, out_root=None, rows=None):
    from core.export import _commit
    from evaluation.real_eval import log_real, map_transform
    out_root = pathlib.Path(out_root or (_data() / "out"))
    latest = _latest(rows)
    summary = []
    for it in plan(rows):
        lads = compose(it, out_root)
        # The direct registration's MATCHER answer (H_matcher) - what the area check refused - not its H_final:
        # on a refused window H_final is the declared phase-correlation fallback (claim-check, 4 Oct: the first
        # version compared against H_final and read the fallback's distance as the refused answer's).
        direct, declared = None, ""
        if (out_root / it["target"] / "report.json").exists():
            rd, pd = _bundle(it["target"], out_root)
            declared = (rd.get("declared") or {}).get("method") or ""
            H = rd.get("H_matcher") if rd.get("H_matcher") is not None else rd.get("H_final")
            if H is not None:
                direct = map_transform(H, pd["source"]["transform"], pd["reference"]["transform"])
        gsd_t = json.loads((PAIRS / it["target"] / "geometry_prior.json").read_text(encoding="utf-8"))[
            "reference"]["resampled_gsd_mpp"]
        good = [L for L in lads if L["accepted"] and len(L["pts"]) >= 10]
        cross = None
        if len(good) >= 2:
            pts = np.vstack([good[0]["pts"], good[1]["pts"]])
            cross = _disagree(good[0]["T"], good[1]["T"], pts, gsd_t)
        for L in lads:
            vs_direct = (_disagree(L["T"], direct, L["pts"], gsd_t)
                         if direct is not None and L["T"] is not None and len(L["pts"]) >= 10 else None)
            other = [g for g in good if g is not L]
            via = " -> ".join(L["chain"])
            links = "; ".join(f"{leg} ({v}; Sun {d:.1f} deg)" for leg, v, d in zip(L["legs"], L["verdicts"], L["d"]))
            line = (f"{it['target']}: via {via} (links " + ", ".join(f"{d:.1f}" for d in L["d"]) + " deg) "
                    f"{L['verdicts']} -> {'ACCEPTED' if L['accepted'] else 'not accepted'}")
            if vs_direct:
                line += f"; the direct matcher answer is {vs_direct['rms_m']:.1f} m RMS from it (declared there: {declared})"
            if cross and L in good:
                line += f"; the two ladders agree to {cross['rms_m']:.2f} m RMS = {cross['rms_px']:.2f} px of T"
            print(line)
            summary.append({"target": it["target"], "chain": L["chain"], "accepted": L["accepted"], "cross": cross,
                            "vs_direct": vs_direct})
            if log:
                paired = bool(cross and other and L in good)
                log_real({
                    "pair_id": ladder_id(it, L["chain"]), "tier": f"Sun ladder (real, {len(L['legs'])} legs)",
                    "kind": "OHRC -> M ... -> T, Sun azimuths O-T 60-120 deg apart; no leg crosses that band",
                    "source_product": latest.get(it["target"], {}).get("source_product", ""),
                    "reference_product": it["T"], "window_lat": round(it["latlon"][0], 5),
                    "window_lon": round(it["latlon"][1], 5), "ref_gsd_m": gsd_t,
                    "d_sun_azimuth_deg": it["d_az"],
                    "verdict": "agrees" if L["accepted"] else "not accepted",
                    "method_declared": f"ladder: loftr+magsac++ x{len(L['legs'])}",
                    "loop_id": f"via {via} vs via {' -> '.join(other[0]['chain'])}" if paired else "",
                    "loop_rms_m": round(cross["rms_m"], 4) if paired else "",
                    "loop_rms_px": round(cross["rms_px"], 4) if paired else "",
                    "command": "python -m ops.sun_ladder --log",
                    "git_commit": _commit(),
                    "notes": (f"links: {links}; bundles from commits {L['commits']}; the direct matcher answer "
                              f"(declared: {declared or 'n/a'}) vs the composite "
                              + (f"{vs_direct['rms_m']:.2f} m RMS over {vs_direct['n']} points"
                                 if vs_direct else "n/a")),
                })
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--cut", action="store_true")
    ap.add_argument("--log", action="store_true")
    ap.add_argument("--out-root")
    a = ap.parse_args(argv)
    items = plan()
    if a.plan or a.cut:
        for it in items:
            print(f"{it['target']} (O-T {it['d_az']:.1f} deg): "
                  + (", ".join(" -> ".join(c["chain"]) + " (links " + ", ".join(f"{d:.1f}" for d in c["d"]) + ")"
                               for c in it["chains"]) or "no intermediate covers it"))
    if a.cut:
        ids = cut_all(items)
        print("\ncut " + str(len(ids)) + " legs:\n" + " ".join(ids))
        return 0
    if not a.plan:
        run(log=a.log, out_root=a.out_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
