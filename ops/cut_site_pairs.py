"""Cut real Chandrayaan-2 OHRC <-> LROC NAC pairs at the 74 S site, as georeferenced GeoTIFFs.

    python -m ops.cut_site_pairs --nac M1153871873LE --windows 6
    python -m ops.cut_site_pairs --nac M1153871873LE --windows 6 --coarse-only

What it does, in order:
  1. Geometry. OHRC: its own geolocation grid (every 100 px). NAC: the four footprint
     corners LROC publishes (0.01 deg), bilinear - a COARSE prior. Both go to lunar
     south-polar stereographic metres (`core.geometry`).
  2. Coarse check at 4 m/px. Overviews of both images are projected onto one grid and
     correlated in boxes that lie entirely inside the shared footprint. The median
     box offset is how far the NAC corner prior is from the OHRC grid. It is applied
     to the NAC frame only if enough boxes agree; either way it is recorded.
  3. Windows. Square windows inside the shared footprint, in lit terrain on the OHRC
     side (the OHRC here was taken at 6.9 deg sun elevation - much of it is shadow),
     spread along the overlap.
  4. Cut. The NAC window at its native ~0.9 m/px, the OHRC window over the SAME ground
     at 0.25 m/px (so the scale difference is real), both GeoTIFF in the same CRS,
     plus geometry_prior.json and PROVENANCE.md.

A pair written here is NOT pre-registered to sub-pixel: it is aligned only as well as
the two archives' own geolocation (plus the coarse correction). The pipeline's job
is the rest, and what it finds is reported against this prior, never replaced by it.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip()) if (ROOT / "data_path.txt").exists() \
    else pathlib.Path(r"C:\Users\samar\sih26166_data")
OHRC_ID = "ch2_ohr_ncp_20200229T0739312111"
OHRC_XML = DATA / "raw_samples" / "ohrc" / f"{OHRC_ID}_d_img_d18.xml"
OHRC_GRID = DATA / "raw_samples" / "ohrc" / f"{OHRC_ID}_g_grd_d18.csv"
NAC_DIR = DATA / "nac"
PAGES = NAC_DIR / "nac_site_pages.json"
PAIRS = ROOT / "data" / "pairs"

# OHRC illumination at the frame centre, derived from the acquisition time and the
# sub-solar point LROC publishes for NAC frames taken 37 min earlier (sub-solar
# longitude drift measured at -12.23 deg/day between two such frames). The OHRC
# PDS4 label carries no sun angles.
OHRC_SUN = {"incidence_deg": 83.07, "azimuth_deg_from_north": 70.5,
            "time_utc": "2020-02-29T07:39:39Z",
            "method": "sub-solar point (-1.40, 113.08) from LROC NAC M1337598991LE/M1337597649LE "
                      "(2020-02-29 06:39-07:02 UTC) propagated at -12.232 deg/day"}
SITE_LATLON = (-73.94, 43.66)

OVERVIEW_GSD = 4.0
OHRC_FACTOR, NAC_FACTOR = 16, 4


def _ohrc():
    from core import geometry as G
    from core.io_loader import load
    _, meta = load(OHRC_XML, window=(0, 0, 8, 8))
    frame = G.Frame.from_ohrc_grid(OHRC_GRID, meta["full_shape"], "OHRC " + OHRC_ID)
    reader = lambda x, y, w, h: load(OHRC_XML, window=(x, y, w, h))[0]  # noqa: E731
    return frame, reader, meta


def _nac_page(pid):
    for d in json.loads(PAGES.read_text()):
        if d["pid"] == pid:
            return d
    raise SystemExit(f"{pid} is not in {PAGES}")


def _nac(pid):
    from core import geometry as G
    from core.io_loader import load
    d = _nac_page(pid)
    path = NAC_DIR / f"{pid}.IMG"
    if not path.exists():
        raise SystemExit(f"{path} not downloaded yet")
    c = lambda k: (d[f"{k} latitude"], d[f"{k} longitude"])  # noqa: E731
    shape = (int(d["Image lines"]), int(d["Line samples"]))
    frame = G.Frame.from_corners(c("Upper left"), c("Upper right"), c("Lower right"),
                                 c("Lower left"), shape, "NAC " + pid,
                                 source="LROC footprint corners (0.01 deg), bilinear - coarse prior")
    reader = lambda x, y, w, h: load(path, window=(x, y, w, h))[0]  # noqa: E731
    inc, az = G.sun_direction(*SITE_LATLON, d["Sub solar latitude"], d["Sub solar longitude"])
    info = {"product_id": pid, "path": str(path), "page": d["url"], "edr_url": d.get("edr_url"),
            "resolution_mpp": d["Resolution"], "emission_deg": d["Emission angle"],
            "incidence_deg_at_site": round(inc, 2), "sun_azimuth_deg_from_north": round(az, 1),
            "subsolar": [d["Sub solar latitude"], d["Sub solar longitude"]],
            "corners_latlon": {k: c(k) for k in ("Upper left", "Upper right",
                                                 "Lower right", "Lower left")}}
    return frame, reader, info


def _decimated(frame, f):
    from core import geometry as G
    return G.Frame(frame.name + f"/{f}", (frame.shape[0] // f, frame.shape[1] // f),
                   (frame.xs - (f - 1) / 2) / f, (frame.ys - (f - 1) / 2) / f, frame.X, frame.Y,
                   frame.source)


def overviews(ohrc, o_read, nac, n_read, cache_dir):
    """Both images at ~4 m on one polar-stereographic grid over their shared footprint."""
    from core import geometry as G
    cache_dir.mkdir(parents=True, exist_ok=True)
    oc = cache_dir / f"ohrc_overview_f{OHRC_FACTOR}.npy"
    if oc.exists():
        o_small = np.load(oc)
    else:
        o_small = G.block_mean(o_read, ohrc.shape, OHRC_FACTOR)
        np.save(oc, o_small)
    nc = cache_dir / f"{nac.name.split()[-1]}_overview_f{NAC_FACTOR}.npy"
    if nc.exists():
        n_small = np.load(nc)
    else:
        n_small = G.block_mean(n_read, nac.shape, NAC_FACTOR)
        np.save(nc, n_small)
    mask, tr = G.overlap_mask([ohrc, nac], res=10)
    ys, xs = np.nonzero(mask)
    if not len(ys):
        raise SystemExit("the two footprints do not overlap")
    pad = 400.0
    x0 = tr[0] + xs.min() * 10 - pad
    x1 = tr[0] + (xs.max() + 1) * 10 + pad
    y1 = tr[3] - ys.min() * 10 + pad
    y0 = tr[3] - (ys.max() + 1) * 10 - pad
    gt, gshape = G.map_grid(x0, y1, x1 - x0, y1 - y0, OVERVIEW_GSD)
    of, nf = _decimated(ohrc, OHRC_FACTOR), _decimated(nac, NAC_FACTOR)
    a, va = G.project(of, lambda x, y, w, h: o_small[y:y + h, x:x + w], gt, gshape)
    b, vb = G.project(nf, lambda x, y, w, h: n_small[y:y + h, x:x + w], gt, gshape)
    return a, va, b, vb, gt


def _boxes(support, box, step):
    import cv2
    ii = cv2.integral(support.astype(np.uint8))
    H, W = support.shape
    out = []
    for y in range(0, H - box, step):
        for x in range(0, W - box, step):
            s = ii[y + box, x + box] - ii[y, x + box] - ii[y + box, x] + ii[y, x]
            if s == box * box:
                out.append((x, y))
    return out


def coarse_prior(a, va, b, vb, gt, box=128, min_lit=0.8, min_peak=0.3, thresh_m=30.0):
    """How far the NAC corner prior is from the OHRC grid, as an affine field.

    Boxes lying fully inside both footprints and lit on the OHRC side are phase-
    correlated on log-standardised intensity (the chosen NACs share the OHRC's sun to
    within a few degrees, so intensity is the stronger signal here; gradient
    orientation is kept for the matcher). Box offsets drift along the 45 km NAC strip -
    a four-corner bilinear model at 0.01 deg cannot be right everywhere - so a single
    translation is the wrong model: an affine displacement field is fitted robustly.
    Returns a dict; `apply` says whether it is trustworthy enough to cut windows on.
    """
    import cv2
    from core import geometry as G
    support = cv2.erode((va & vb).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    lit_thr = np.percentile(a[va], 60) * 0.5 if va.any() else 0
    w = cv2.createHanningWindow((box, box), cv2.CV_32F)

    def logstd(z):
        z = np.log1p(np.clip(z.astype(np.float32), 0, None))
        return (z - z.mean()) / (z.std() + 1e-6)
    rows = []
    for x, y in _boxes(support, box, box // 2):
        A, B = a[y:y + box, x:x + box], b[y:y + box, x:x + box]
        lit = float((A > lit_thr).mean())
        if lit < min_lit:
            continue
        An, Bn = logstd(A), logstd(B)
        (dx, dy), pk = cv2.phaseCorrelate((Bn * w).astype(np.float64), (An * w).astype(np.float64))
        cx = gt[0] + (x + box / 2) * gt[1]
        cy = gt[3] + (y + box / 2) * gt[5]
        rows.append((cx, cy, lit, dx, dy, pk))
    good = [r for r in rows if r[5] >= min_peak]
    out = {"boxes_tested": len(rows), "boxes_above_peak": len(good), "box_px": box,
           "grid_gsd_m": OVERVIEW_GSD, "min_peak": min_peak, "apply": False, "model": None}
    if len(good) >= 6:
        P = [(r[0], r[1]) for r in good]
        Dm = [(r[3] * OVERVIEW_GSD, -r[4] * OVERVIEW_GSD) for r in good]
        fit = G.fit_affine_correction(P, Dm, thresh_m=thresh_m)
        out["median_offset_m"] = np.median(np.asarray(Dm), axis=0).tolist()
        if fit:
            out["model"] = fit
            out["apply"] = bool(fit["inliers"] >= max(6, 0.4 * len(good)))
    out["boxes"] = [dict(cx=round(r[0], 1), cy=round(r[1], 1), lit=round(r[2], 3), dx=round(r[3], 2),
                         dy=round(r[4], 2), peak=round(r[5], 3)) for r in rows]
    return out


def pick_windows(a, va, b, vb, gt, window_m, n, min_lit=0.9, spacing_m=None):
    """Window centres (map metres) in shared, lit, textured terrain, spread out."""
    import cv2
    box = int(np.ceil(window_m / OVERVIEW_GSD)) + 4
    support = cv2.erode((va & vb).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    lit_thr = np.percentile(a[va], 60) * 0.5 if va.any() else 0
    cands = []
    for x, y in _boxes(support, box, max(4, box // 4)):
        A, B = a[y:y + box, x:x + box], b[y:y + box, x:x + box]
        lit = float((A > lit_thr).mean())
        if lit < min_lit:
            continue
        tex = float(min(np.std(A) / (np.mean(A) + 1e-6), np.std(B) / (np.mean(B) + 1e-6)))
        cx = gt[0] + (x + box / 2) * gt[1]
        cy = gt[3] + (y + box / 2) * gt[5]
        cands.append((tex * lit, cx, cy, lit))
    cands.sort(reverse=True)
    spacing = spacing_m or window_m * 1.1
    chosen = []
    for s, cx, cy, lit in cands:
        if all(np.hypot(cx - px, cy - py) >= spacing for _, px, py, _ in chosen):
            chosen.append((s, cx, cy, lit))
        if len(chosen) >= n:
            break
    return [dict(cx=float(cx), cy=float(cy), score=float(s), lit=float(lit)) for s, cx, cy, lit in chosen]


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


GEOM_DIR = DATA / "site_geometry"


def nac_frame_corrected(nac_pid, refit=False, verbose=True):
    """The NAC's frame with its correction field vs the OHRC grid - computed ONCE and
    saved, so every pair that uses this NAC shares one georeference (loop closure is
    only meaningful if each image has exactly one)."""
    ohrc, o_read, _ = _ohrc()
    nac, n_read, n_info = _nac(nac_pid)
    GEOM_DIR.mkdir(parents=True, exist_ok=True)
    gp = GEOM_DIR / f"{nac_pid}.json"
    if gp.exists() and not refit:
        prior = json.loads(gp.read_text(encoding="utf-8"))
    else:
        cache = DATA / "overviews"
        a, va, b, vb, gt = overviews(ohrc, o_read, nac, n_read, cache)
        prior = coarse_prior(a, va, b, vb, gt)
        if verbose:
            _say_prior(f"{nac_pid} archive geometry", prior)
        if prior["apply"]:
            nac_c = nac.corrected(prior["model"], "(4 m correlation field vs the OHRC grid)")
            a, va, b, vb, gt = overviews(ohrc, o_read, nac_c, n_read, cache)
            check = coarse_prior(a, va, b, vb, gt)
            if verbose:
                _say_prior(f"{nac_pid} after correction", check)
            prior["after_correction"] = {k: v for k, v in check.items() if k != "boxes"}
        prior["nac_pid"] = nac_pid
        gp.write_text(json.dumps(prior, indent=1), encoding="utf-8")
    if prior.get("apply"):
        nac = nac.corrected(prior["model"], "(4 m correlation field vs the OHRC grid)")
    return nac, n_read, n_info, prior


def _frame(kind_or_pid):
    """('ohrc' | NAC pid) -> (frame, reader, info, gsd_to_write, label)."""
    if kind_or_pid.lower() == "ohrc":
        f, rd, meta = _ohrc()
        info = {"instrument": "Chandrayaan-2 OHRC", "product_id": OHRC_ID + "_d_img_d18",
                "path": str(OHRC_XML), "native_gsd_mpp": meta.get("gsd_mpp"),
                "geometry": f.source, "sun": OHRC_SUN}
        return f, rd, info, None, "ohrc"
    f, rd, info, prior = nac_frame_corrected(kind_or_pid)
    info = {"instrument": "LRO LROC NAC", **info, "geometry": f.source,
            "coarse_prior": {k: v for k, v in prior.items() if k != "boxes"}}
    return f, rd, info, round(float(np.mean(f.gsd())), 3), kind_or_pid.lower()


def _inside(frame, cx, cy, half_m, n=9):
    """True when a square window lies entirely inside the frame's image."""
    g = np.linspace(-half_m, half_m, n)
    X, Y = np.meshgrid(cx + g, cy + g)
    x, y = frame.from_map(X, Y)
    rows, cols = frame.shape
    return bool(np.all(np.isfinite(x)) and x.min() >= 0 and y.min() >= 0
                and x.max() <= cols - 1 and y.max() <= rows - 1)


def cut(nac_pid, n_windows=6, window_px=640, ohrc_gsd=0.25, coarse_only=False,
        force_prior=None, src="ohrc", centres=None, tag=None, require_inside=(), window_m=None):
    """Cut `src` (ohrc or a NAC pid) against the reference NAC `nac_pid`.

    centres: reuse these window centres [(cx, cy), ...] in map metres instead of picking
    new ones - how the three legs of a loop are cut over the same ground.
    """
    from core import geometry as G
    ref_f, ref_read, ref_info, ref_gsd, ref_label = _frame(nac_pid)
    if coarse_only:
        return json.loads((GEOM_DIR / f"{nac_pid}.json").read_text(encoding="utf-8"))
    src_f, src_read, src_info, src_gsd, src_label = _frame(src)
    src_gsd = ohrc_gsd if src_label == "ohrc" else src_gsd
    window_m = window_m or window_px * ref_gsd
    if centres is None:
        if src_label != "ohrc":
            raise SystemExit("new windows are picked on OHRC-lit ground; pass --centres-from for NAC-NAC")
        ohrc, o_read, _ = _ohrc()
        a, va, b, vb, gt = overviews(ohrc, o_read, ref_f, ref_read, DATA / "overviews")
        others = [nac_frame_corrected(pid, verbose=False)[0] for pid in require_inside]
        wins = pick_windows(a, va, b, vb, gt, window_m, n_windows * 8 if others else n_windows)
        if others:
            wins = [w for w in wins
                    if all(_inside(f, w["cx"], w["cy"], window_m * 0.75) for f in others)][:n_windows]
            print(f"  {len(wins)} windows also lie inside {', '.join(require_inside)}")
        centres = [(w["cx"], w["cy"], w["lit"]) for w in wins]
    else:
        centres = [(c[0], c[1], None) for c in centres]
    if not centres:
        raise SystemExit("no lit window fits inside the shared footprint")
    same_sensor = src_label != "ohrc"
    s_sun = src_info.get("sun") or {"incidence_deg": src_info.get("incidence_deg_at_site"),
                                    "azimuth_deg_from_north": src_info.get("sun_azimuth_deg_from_north")}
    r_sun_az, r_inc = ref_info["sun_azimuth_deg_from_north"], ref_info["incidence_deg_at_site"]
    d_az = round(abs((r_sun_az - s_sun["azimuth_deg_from_north"] + 180) % 360 - 180), 1)
    d_inc = round(r_inc - s_sun["incidence_deg"], 2)
    out_dirs = []
    for k, (cx, cy, lit) in enumerate(centres, 1):
        pair_id = f"site_{src_label}_{ref_label}_w{k:02d}" + (f"_{tag}" if tag else "")
        d = PAIRS / pair_id
        d.mkdir(parents=True, exist_ok=True)
        x0, y1 = cx - window_m / 2, cy + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
        r_img, r_ok = G.project(ref_f, ref_read, tr_r, sh_r, coarse=16, order="cubic")
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(src_f, src_read, tr_s, sh_s, coarse=32 if src_label == "ohrc" else 16,
                                order="cubic")
        if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
            print(f"  {pair_id}: window not covered (ref {r_ok.mean():.4f}, "
                  f"src {s_ok.mean():.4f}) - skipped")
            continue
        r_img, r_fill = G.fill_invalid(r_img, r_ok)
        s_img, s_fill = G.fill_invalid(s_img, s_ok)
        src_p = d / f"{pair_id}_source.tif"
        ref_p = d / f"{pair_id}_ref.tif"
        G.write_geotiff(src_p, s_img.astype(np.float32), tr_s)
        G.write_geotiff(ref_p, r_img.astype(np.float32), tr_r)
        lat, lon = G.ps_south_inv(cx, cy)
        tier = ("A (NAC-NAC real, same sensor)" if same_sensor else "B (OHRC-NAC real)")
        term = ("same sensor (LROC NAC) - a sun-angle / geometry test, NOT cross-sensor"
                if same_sensor else
                "cross-sensor, cross-mission (Chandrayaan-2 OHRC vs LRO LROC NAC); both "
                "panchromatic, so NOT multi-modal")
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": tier, "terminology": term, "crs": G.PS_SOUTH_CRS,
            "window_centre_map_m": [cx, cy], "window_centre_latlon": [float(lat), float(lon)],
            "window_m": window_m,
            "source": {**src_info, "resampled_gsd_mpp": src_gsd, "shape": list(sh_s),
                       "transform": list(tr_s), "lit_fraction_4m": lit},
            "reference": {**ref_info, "resampled_gsd_mpp": ref_gsd, "shape": list(sh_r),
                          "transform": list(tr_r)},
            "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc,
            "scale_ratio": round(ref_gsd / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / ref_gsd, 0, 0], [0, src_gsd / ref_gsd, 0],
                                            [0, 0, 1]],
            "prior_note": "both files are on the same north-up map grid over the same ground, so the "
                          "archive-geometry prior is a pure scale; any rotation or offset the pipeline "
                          "finds is disagreement between the (corrected) archive georeferences",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.cut_site_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        (d / "PROVENANCE.md").write_text(_provenance(meta), encoding="utf-8")
        out_dirs.append(d)
        print(f"  {pair_id}: centre ({lat:.4f}, {lon:.4f}); src {sh_s} @ {src_gsd} m, "
              f"ref {sh_r} @ {ref_gsd} m; d_az {d_az} deg, d_inc {d_inc:+} deg")
    return out_dirs


def _say_prior(label, p):
    m = p.get("model")
    if m:
        print(f"coarse check ({label}): {p['boxes_above_peak']}/{p['boxes_tested']} lit boxes with "
              f"peak >= {p['min_peak']}; median offset ({p['median_offset_m'][0]:+.1f}, "
              f"{p['median_offset_m'][1]:+.1f}) m; affine field fits {m['inliers']}/{m['n']} "
              f"boxes, rms {m['rms_m']:.1f} m, p90 {m['p90_m']:.1f} m; apply={p['apply']}")
    else:
        print(f"coarse check ({label}): {p['boxes_above_peak']}/{p['boxes_tested']} lit boxes with "
              f"peak >= {p['min_peak']}; no field fitted")


def _provenance(m):
    s, r = m["source"], m["reference"]

    def sun(x):
        if "sun" in x:
            return f"inc {x['sun']['incidence_deg']} deg, az {x['sun']['azimuth_deg_from_north']} deg (derived)"
        return f"inc {x.get('incidence_deg_at_site')} deg, az {x.get('sun_azimuth_deg_from_north')} deg"

    def native(x):
        v = x.get("native_gsd_mpp") or x.get("resolution_mpp")
        return f"{v:.4f} m/px" if v else "?"
    return f"""# {m['pair_id']}

Tier **{m['tier']}** - {m['terminology']}.
Cut {m['created_utc']} by `{m['command']}`.

| | source (moving) | reference (fixed) |
|---|---|---|
| instrument | {s['instrument']} | {r['instrument']} |
| product | `{s['product_id']}` | `{r['product_id']}` |
| native GSD | {native(s)} | {native(r)} |
| written at | {s['resampled_gsd_mpp']} m/px, {s['shape']} | {r['resampled_gsd_mpp']} m/px, {r['shape']} |
| sun at site | {sun(s)} | {sun(r)} |
| geometry | {s['geometry']} | {r['geometry']} |

Window centre ({m['window_centre_latlon'][0]:.5f}, {m['window_centre_latlon'][1]:.5f}), {m['window_m']:.1f} m square,
map: {m['crs']}. Sun difference: azimuth {m['d_sun_azimuth_deg']} deg, incidence {m['d_incidence_deg']:+} deg.
Scale ratio {m['scale_ratio']}x.

OHRC sun angles are derived from the acquisition time, not read (the PDS4 label has none).
NAC geometry is LROC's four published footprint corners (0.01 deg) plus a correction field
fitted against the OHRC grid (`site_geometry/<pid>.json`, recorded in geometry_prior.json).

Files (sha256): {', '.join(f'`{k}` {v[:16]}' for k, v in m['files'].items())}
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--nac", required=True, help="reference LROC NAC product id, e.g. M1153871873LE")
    ap.add_argument("--src", default="ohrc", help="'ohrc' (default) or a NAC product id")
    ap.add_argument("--windows", type=int, default=6)
    ap.add_argument("--window-px", type=int, default=640)
    ap.add_argument("--window-m", type=float, help="fixed ground size in metres (same square for every loop leg)")
    ap.add_argument("--ohrc-gsd", type=float, default=0.25)
    ap.add_argument("--centres-from", help="glob of existing pair dirs whose window centres to reuse")
    ap.add_argument("--tag", help="suffix for the pair ids")
    ap.add_argument("--require-inside", nargs="*", default=[],
                    help="only pick windows that ALSO lie inside these NACs (for loops)")
    ap.add_argument("--coarse-only", action="store_true")
    ap.add_argument("--refit", action="store_true", help="recompute the saved NAC correction field")
    a = ap.parse_args(argv)
    if a.refit:
        nac_frame_corrected(a.nac, refit=True)
    centres = None
    if a.centres_from:
        import glob
        dirs = sorted(glob.glob(str(PAIRS / a.centres_from)))
        centres = [json.loads((pathlib.Path(d) / "geometry_prior.json").read_text(encoding="utf-8"))
                   ["window_centre_map_m"] for d in dirs]
        print(f"reusing {len(centres)} window centres from {a.centres_from}")
    r = cut(a.nac, a.windows, a.window_px, a.ohrc_gsd, a.coarse_only, src=a.src,
            centres=centres, tag=a.tag, require_inside=a.require_inside, window_m=a.window_m)
    if a.coarse_only:
        print(json.dumps({k: v for k, v in r.items() if k != "boxes"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
