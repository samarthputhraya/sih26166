"""Relief, with a local model: each window registered as 2 x 2 quarter windows, each with its own transform.

    python -m ops.split_windows                     # cut reliefq_dtm_wNN_qIJ and reliefq_wNN_qIJ
    python -m ops.run_real_pairs "reliefq_*" --log  # register them (the freeze's `real` step)

WHY. TMC-2's fore and aft cameras see one pass 50 deg apart, so terrain shifts every point by about
0.93 x its height between the two images: not a homography. Registered as whole 2.28 km windows, 1 of 4
is accepted; after orthorectification on ISRO's TMC-2 DTM of the pass, 2 of 4 (REPORT, "Relief"), and the
held-out residuals of those that pass are still 2.4-3.9 px - the parallax the DTM did not remove. A single
transform per window cannot absorb a distortion that varies across it; a smaller window has less relief in
it, so a transform per quarter window approximates it far better. That is the local-model answer
(piecewise / thin-plate registration does the same with more pieces), built here from the pipeline as is:
each quarter is an ordinary pair, run by `run_all`, judged by its own area check (8 x 8 cells of 24 px,
the smallest the check lets vote), never merged with the whole-window rows.

Quarters are cut from the SAME orthorectified (and, for comparison, plain) windows: the reference image is
cropped into its four quarters, the source over exactly the same ground. Nothing is re-projected.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAIRS = ROOT / "data" / "pairs"
R_MOON_M = 1737400.0
SETS = {"reliefq_dtm": "sac_tmcfore_tmcaft_dtm_w{:02d}", "reliefq": "sac_tmcfore_tmcaft_w{:02d}"}


def _sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:12]


def _read(path):
    import tifffile
    return np.asarray(tifffile.imread(str(path)), np.float32)


def split(parent: str, prefix: str, n: int = 2) -> list:
    """Cut `parent` into n x n sub-pairs over the same ground; returns their ids."""
    from core import geometry as G
    d = PAIRS / parent
    g = json.loads((d / "geometry_prior.json").read_text(encoding="utf-8"))
    src, ref = _read(d / f"{parent}_source.tif"), _read(d / f"{parent}_ref.tif")
    st, rt = list(g["source"]["transform"]), list(g["reference"]["transform"])
    assert st[2] == st[4] == rt[2] == rt[4] == 0, "north-up grids only"
    rh, rw = ref.shape
    win = parent.rsplit("_", 1)[-1]
    out = []
    for i in range(n):
        for j in range(n):
            r0, r1, c0, c1 = i * rh // n, (i + 1) * rh // n, j * rw // n, (j + 1) * rw // n
            x0, y0 = rt[0] + c0 * rt[1], rt[3] + r0 * rt[5]                 # the quarter's top-left, map m
            x1, y1 = rt[0] + c1 * rt[1], rt[3] + r1 * rt[5]
            sc0, sr0 = int(round((x0 - st[0]) / st[1])), int(round((y0 - st[3]) / st[5]))
            sc1, sr1 = int(round((x1 - st[0]) / st[1])), int(round((y1 - st[3]) / st[5]))
            s_img, r_img = src[sr0:sr1, sc0:sc1], ref[r0:r1, c0:c1]
            pid = f"{prefix}_{win}_q{i + 1}{j + 1}"
            q = PAIRS / pid
            q.mkdir(parents=True, exist_ok=True)
            s_tr = [st[0] + sc0 * st[1], st[1], 0.0, st[3] + sr0 * st[5], 0.0, st[5]]
            r_tr = [x0, rt[1], 0.0, y0, 0.0, rt[5]]
            sp, rp = q / f"{pid}_source.tif", q / f"{pid}_ref.tif"
            G.write_geotiff(sp, s_img, s_tr)
            G.write_geotiff(rp, r_img, r_tr)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            meta = {**g, "pair_id": pid,
                    "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
                    "window_centre_map_m": [cx, cy], "window_m": abs(x1 - x0),
                    "window_rule": f"quarter ({i + 1}, {j + 1}) of {parent}, the same ground, cropped",
                    "source": {**g["source"], "transform": s_tr, "shape": list(s_img.shape)},
                    "reference": {**g["reference"], "transform": r_tr, "shape": list(r_img.shape)},
                    "files": {sp.name: _sha(sp), rp.name: _sha(rp)},
                    "command": "python -m ops.split_windows"}
            # the quarter's centre: the parent's, moved by the quarter's offset on the local map (metres)
            pcx, pcy = g["window_centre_map_m"]
            plat, plon = g["window_centre_latlon"]
            lat_ts = float(g["crs"].split("lat_ts")[1].split(",")[0]) if "lat_ts" in g.get("crs", "") else plat
            meta["window_centre_latlon"] = [plat + float(np.degrees((cy - pcy) / R_MOON_M)),
                                            plon + float(np.degrees((cx - pcx) / (R_MOON_M * np.cos(np.radians(lat_ts)))))]
            (q / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
            out.append(pid)
    return out


def main(argv=None):
    ids = []
    for prefix, stem in SETS.items():
        for k in range(1, 5):
            if (PAIRS / stem.format(k)).exists():
                ids += split(stem.format(k), prefix)
    print(f"cut {len(ids)} quarter windows:\n" + " ".join(ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
