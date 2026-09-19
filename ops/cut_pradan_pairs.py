"""Real pairs from the PRADAN products at SAC's benchmark site.

    python -m ops.cut_pradan_pairs tmc-fore-aft      # TMC-2 fore vs aft, one pass: a REAL viewpoint test
    python -m ops.cut_pradan_pairs ohrc-tmc          # OHRC vs TMC-2 nadir (cross-sensor, same mission)
    python -m ops.cut_pradan_pairs ohrc-tmc --windows 5
    python -m ops.cut_pradan_pairs ohrc-nac          # SAC's own OHRC <-> LRO NAC pair, 13 S
    python -m ops.cut_pradan_pairs ohrc-nac-polar    # SAC's polar OHRC <-> LRO NAC pair, 62 S

THE SITE is SAC's own benchmark OHRC frame `ch2_ohr_ncp_20210401T2357376656` (arXiv:2509.04775,
Table 1; 13.06-13.89 S, 25.13-25.24 E). No TMC-2 strip covers our 74 S site (checked 18 Sep against
the calibrated grids - ops/national_round/PRADAN_GUIDE.md section 3a); TMC-2 pass `20250707T1853`
covers this frame completely, in all three cameras. Products and sha256: <data>/pradan/,
<data>/download_manifest_done.csv.

THE MAP is a local equirectangular grid (sphere R = 1737.4 km, standard parallel and central
meridian at the site). The 74 S work uses south-polar stereographic, which at 13 S would stretch
every distance by ~1.6x and put every metre figure off by that much. Over a few kilometres the
equirectangular scale error is well under 0.1 %. Each image is placed on the grid through its own
archive geolocation lattice (`*_g_grd_*.csv`, every 100 px), exactly as `ops/cut_site_pairs.py`
does with the OHRC at 74 S - so the prior between the two files of a pair is a pure scale, and
anything else the pipeline finds is the archives' disagreement.

WHAT EACH PAIR IS (Invariant 2):
  tmc-fore-aft  TMC-2 fore (+25 deg) vs aft (-25 deg) of ONE pass: same instrument, same sun,
                seconds apart - the only difference is the viewing direction (~50 deg apart).
                Tier A (same sensor, viewpoint). NOT cross-sensor. The archive grids are computed
                for the reference surface, so terrain relief leaves a parallax of roughly
                h * (tan 25 + tan 25) ~ 0.93 h between the two - which one homography cannot model
                (the synthetic parallax sweep measured exactly this). Expect it in the residuals.
  ohrc-tmc      OHRC (0.26 m native, area-averaged 4x4 to ~1.05 m here) vs TMC-2 nadir (~6 m):
                cross-sensor, SAME mission (both Chandrayaan-2), both panchromatic - NOT
                multi-modal, NOT cross-mission. Sun from the labels: OHRC az 270.9 / elev 9.9 deg,
                TMC-2 az 31.1 / elev 69.4 deg - a large illumination change on top of ~6x scale
                (the native ratio is ~23x; the area-averaging is stated, not hidden).
  ohrc-nac      SAC's Table 1 pairs, both halves: OHRC `20210401T2357376656` vs LRO NAC
  ohrc-nac-polar  `M1350459544RE` (13-14 S), and OHRC `20200824T0806596861` vs NAC `M165491149RE`
                (61.5-62.3 S). Cross-sensor AND cross-mission; both panchromatic - NOT
                multi-modal. OHRC at its native ~0.26 m, NAC at its native 1.2-1.6 m. The NAC's
                geometry is LROC's four published corners (0.01 deg), corrected by an affine
                field fitted against the OHRC grid at 4 m (`ops.cut_site_pairs.coarse_prior`,
                tried on direct AND inverted intensity - SAC's equatorial pair has the sun on
                opposite sides - and saved to <data>/site_geometry/<pid>.json). The NAC EDRs are
                public (<data>/nac/nac_sac_pages.json: product page fields; sha256 in
                <data>/nac_sac_manifest_done.csv). At 62 S the local equirectangular map's
                x-scale drifts by tan(62 deg) x d_lat ~ 1.9 % per degree of latitude away from
                lat_ts; each window is ~0.01 deg tall, so within a pair it is a constant
                anisotropy common to both images, recorded per window.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAIRS = ROOT / "data" / "pairs"
DATA = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())
P = DATA / "pradan"
R = 1737400.0

OHRC_ID = "ch2_ohr_ncp_20210401T2357376656_d_img_d18"
TMC_PASS = "20250707T1853"
PRODUCTS = {
    "ohrc": (P / "ohrc/data/calibrated/20210401" / f"{OHRC_ID}.xml",
             P / "ohrc/geometry/calibrated/20210401/ch2_ohr_ncp_20210401T2357376656_g_grd_d18.csv",
             "Chandrayaan-2 OHRC"),
    "tmcn": (P / "tmc2/data/calibrated/20250707/ch2_tmc_ncn_20250707T1853051045_d_img_d18.xml",
             P / "tmc2/geometry/calibrated/20250707/ch2_tmc_ncn_20250707T1853051045_g_grd_d18.csv",
             "Chandrayaan-2 TMC-2 nadir"),
    "tmcf": (P / "tmc2/data/calibrated/20250707/ch2_tmc_ncf_20250707T1853051078_d_img_d18.xml",
             P / "tmc2/geometry/calibrated/20250707/ch2_tmc_ncf_20250707T1853051078_g_grd_d18.csv",
             "Chandrayaan-2 TMC-2 fore (+25 deg)"),
    "tmca": (P / "tmc2/data/calibrated/20250707/ch2_tmc_nca_20250707T1853051045_d_img_d18.xml",
             P / "tmc2/geometry/calibrated/20250707/ch2_tmc_nca_20250707T1853051045_g_grd_d18.csv",
             "Chandrayaan-2 TMC-2 aft (-25 deg)"),
    "ohrc_polar": (P / "ohrc/data/calibrated/20200824/ch2_ohr_ncp_20200824T0806596861_d_img_d18.xml",
                   P / "ohrc/geometry/calibrated/20200824/ch2_ohr_ncp_20200824T0806596861_g_grd_d18.csv",
                   "Chandrayaan-2 OHRC"),
}
OHRC_BLOCK = 4          # OHRC area-averaged 4x4 before projection (0.26 m -> ~1.05 m)


def tmc_nadir(product_id: str):
    """PRODUCTS-style tuple for any calibrated TMC-2 nadir product, from its id alone
    (`ch2_tmc_ncn_<yyyymmddThhmmss><4 digits>_d_img_<stn>`): the zip unpacks to
    <data>/pradan/tmc2/{data,geometry}/calibrated/<yyyymmdd>/. Added 20 Sep 2026 so a second pass
    over SAC's site (`--tmc-product`) needs no code change - only its download."""
    m = re.match(r"^ch2_tmc_ncn_(\d{8})T\d+_d_img_[a-z0-9]+$", product_id)
    if not m:
        raise SystemExit(f"{product_id!r} is not a calibrated TMC-2 nadir product id")
    day = m.group(1)
    return (P / "tmc2/data/calibrated" / day / f"{product_id}.xml",
            P / "tmc2/geometry/calibrated" / day / f"{product_id.replace('_d_img_', '_g_grd_')}.csv",
            "Chandrayaan-2 TMC-2 nadir")
# SAC's OHRC <-> NAC pairs (arXiv:2509.04775, Table 1): kind -> (OHRC key, NAC pid, pair-id stem)
SAC_NAC = {"ohrc-nac": ("ohrc", "M1350459544RE", "sac_ohrc_nac"),
           "ohrc-nac-polar": ("ohrc_polar", "M165491149RE", "sac_polar_ohrc_nac")}
SAC_PAGES = DATA / "nac" / "nac_sac_pages.json"


# --- the local map ------------------------------------------------------------------------

class LocalEqc:
    """Equirectangular on the lunar sphere, standard parallel lat_ts, central meridian lon0.
    x = R cos(lat_ts) (lon - lon0), y = R lat (radians; y is 0 at the equator)."""

    def __init__(self, lat_ts, lon0):
        self.lat_ts, self.lon0 = float(lat_ts), float(lon0)
        self.k = R * math.cos(math.radians(self.lat_ts))

    def fwd(self, lat, lon):
        lat = np.asarray(lat, np.float64)
        dlon = (np.asarray(lon, np.float64) - self.lon0 + 180.0) % 360.0 - 180.0
        return self.k * np.radians(dlon), R * np.radians(lat)

    def inv(self, x, y):
        return (np.degrees(np.asarray(y, np.float64) / R),
                self.lon0 + np.degrees(np.asarray(x, np.float64) / self.k))

    @property
    def name(self):
        return f"Moon sphere 1737.4 km / local equirectangular (lat_ts {self.lat_ts:.4f}, lon_0 {self.lon0:.4f})"

    def geotiff_tags(self, transform, nodata=None):
        """GeoTIFF keys for this CRS: projected, PixelIsArea, user-defined equirectangular
        (CT 17) on a 1737400 m sphere - so QGIS/GDAL place the pair correctly."""
        x0, sx, _, y0, _, sy = transform
        asc = f"{self.name}|GCS Name = Moon 2015 sphere|Datum = Moon 2015|Ellipsoid = Moon sphere|Primem = Reference Meridian||"
        cit = len(self.name) + 1
        keys = [(1024, 0, 1, 1), (1025, 0, 1, 1), (1026, 34737, cit, 0),
                (2048, 0, 1, 32767), (2049, 34737, len(asc) - cit, cit), (2050, 0, 1, 32767),
                (2054, 0, 1, 9102), (2056, 0, 1, 32767), (2057, 34736, 1, 5), (2058, 34736, 1, 6),
                (3072, 0, 1, 32767), (3074, 0, 1, 32767), (3075, 0, 1, 17), (3076, 0, 1, 9001),
                (3078, 34736, 1, 0), (3082, 34736, 1, 2), (3083, 34736, 1, 3),
                (3088, 34736, 1, 1), (3089, 34736, 1, 4)]
        directory = (1, 1, 0, len(keys)) + tuple(v for k in keys for v in k)
        doubles = (self.lat_ts, self.lon0, 0.0, 0.0, 0.0, R, R)
        tags = [(33550, 12, 3, (float(sx), float(-sy), 0.0), True),
                (33922, 12, 6, (0.0, 0.0, 0.0, float(x0), float(y0), 0.0), True),
                (34735, 3, len(directory), directory, True),
                (34736, 12, len(doubles), doubles, True),
                (34737, 2, 0, asc, True)]
        if nodata is not None:
            tags.append((42113, 2, 0, str(nodata), True))
        return tags


def frame_from_grid(csv_path, shape, proj, name, keep_km=40.0):
    """A core.geometry.Frame from a Chandrayaan-2 `*_g_grd_*.csv` lattice (Longitude, Latitude or
    'Lattitude', Pixel, Scan), placed on `proj`. Same construction as Frame.from_ohrc_grid, with
    the map projection as a parameter.

    Only lattice rows within `keep_km` of the map origin are kept. A TMC-2 strip is ~1,300 km
    long and 24 km wide; triangulating all ~90,000 nodes gives needle triangles, and on 18 Sep
    the inverse returned NaN at a few nodes well inside the image (a window came out 1.3 %
    short). Pixel coordinates are unchanged - only the lattice is cropped."""
    from core import geometry as G
    g = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    lon, lat, px, sc = g.T
    xs, ys = np.unique(px), np.unique(sc)
    if len(xs) * len(ys) != len(g):
        raise ValueError(f"{csv_path}: not a full lattice ({len(xs)} x {len(ys)} != {len(g)})")
    ix, iy = np.searchsorted(xs, px), np.searchsorted(ys, sc)
    LAT = np.empty((len(ys), len(xs)))
    LON = np.empty((len(ys), len(xs)))
    LAT[iy, ix], LON[iy, ix] = lat, lon
    X, Y = proj.fwd(LAT, LON)
    Xc, Yc = proj.fwd(proj.lat_ts, proj.lon0)          # the site: standard parallel x central meridian
    near = np.nonzero((np.hypot(X - Xc, Y - Yc) < keep_km * 1e3).any(axis=1))[0]
    if len(near) == 0:
        raise ValueError(f"{csv_path}: no lattice node within {keep_km} km of the site")
    r0, r1 = max(near.min() - 1, 0), min(near.max() + 2, len(ys))
    return G.Frame(name, tuple(shape), xs.astype(float), ys[r0:r1].astype(float), X[r0:r1], Y[r0:r1],
                   source=f"archive geolocation grid {pathlib.Path(csv_path).name} (lattice rows "
                          f"{int(ys[r0])}-{int(ys[r1 - 1])}), {proj.name}")


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def product(key, proj, block=OHRC_BLOCK):
    """(frame, reader, info) for one product; an OHRC is area-averaged `block` x (1 = native)."""
    from core.io_loader import load
    xml, grid, instrument = PRODUCTS[key]
    _, meta = load(xml, window=(0, 0, 8, 8))
    full = meta["full_shape"]
    frame = frame_from_grid(grid, full, proj, instrument)
    info = {"instrument": instrument, "product_id": xml.stem, "path": str(xml),
            "native_gsd_mpp_label": meta.get("gsd_mpp"),
            "sun": {"azimuth_deg_label": meta.get("sun_azimuth"),
                    "elevation_deg_label": meta.get("sun_elevation")},
            "geometry": frame.source}
    if not key.startswith("ohrc") or block == 1:
        return frame, (lambda x, y, w, h: load(xml, window=(x, y, w, h))[0]), info
    f = block

    def read(x, y, w, h):
        a = load(xml, window=(x * f, y * f, w * f, h * f))[0]
        hh, ww = a.shape[0] // f, a.shape[1] // f
        return a[:hh * f, :ww * f].reshape(hh, f, ww, f).mean(axis=(1, 3))
    from ops.cut_site_pairs import _decimated
    info["geometry"] += f"; area-averaged {f}x{f} before projection"
    return _decimated(frame, f), read, info


def _tier(kind):
    if kind == "tmc-fore-aft":
        return ("A (same sensor, viewpoint, real)",
                "same instrument (TMC-2 fore vs aft, one pass, same sun): a VIEWPOINT test, NOT cross-sensor")
    return ("B (cross-sensor real, ohrc-tmc2)",
            "cross-sensor (Chandrayaan-2 OHRC vs TMC-2), same mission - NOT cross-mission; both "
            "panchromatic, so NOT multi-modal")


def cut(kind, n_windows=4, ref_px=384, stem=None):
    """`stem` overrides the pair-id stem (default per kind) - used for a second TMC-2 pass."""
    from core import geometry as G
    from core.io_loader import load
    _, om = load(PRODUCTS["ohrc"][0], window=(0, 0, 8, 8))
    # the map is centred on the OHRC frame; every pair (including fore/aft) is cut over its ground
    proj = LocalEqc(*_frame_centre_latlon(PRODUCTS["ohrc"][1]))
    ohrc_f = frame_from_grid(PRODUCTS["ohrc"][1], om["full_shape"], proj, "ohrc")
    rows, cols = ohrc_f.shape
    src_key, ref_key = {"tmc-fore-aft": ("tmcf", "tmca"), "ohrc-tmc": ("ohrc", "tmcn")}[kind]
    src_f, src_read, src_info = product(src_key, proj)
    ref_f, ref_read, ref_info = product(ref_key, proj)
    ref_gsd = round(float(np.mean(ref_f.gsd())), 3)
    src_gsd = round(float(np.mean(src_f.gsd())), 3)
    window_m = ref_px * ref_gsd
    # window centres: along the OHRC frame's centre line, evenly spaced, clear of its ends
    ys = np.linspace(0.12, 0.88, n_windows) * rows
    cx, cy = ohrc_f.to_map(np.full(n_windows, cols / 2.0), ys)
    tier, term = _tier(kind)
    s_sun, r_sun = src_info["sun"], ref_info["sun"]
    d_az = d_inc = None
    if s_sun["azimuth_deg_label"] is not None and r_sun["azimuth_deg_label"] is not None:
        d_az = round(abs((r_sun["azimuth_deg_label"] - s_sun["azimuth_deg_label"] + 180) % 360 - 180), 1)
        d_inc = round((90 - r_sun["elevation_deg_label"]) - (90 - s_sun["elevation_deg_label"]), 2)
    out = []
    for k, (x, y) in enumerate(zip(cx, cy), 1):
        # No "_a"/"_b" anywhere in a pair id: core.pipeline.resolve_pair takes the source by the
        # substring hints ("_source", "_src", "_a"), and on 18 Sep "sac_tmc_fore_aft_*" put "_aft"
        # in BOTH file names - the reference was registered against itself (4 invalid rows).
        pair_id = (stem or {"tmc-fore-aft": "sac_tmcfore_tmcaft", "ohrc-tmc": "sac_ohrc_tmc"}[kind]) + f"_w{k:02d}"
        x0, y1 = x - window_m / 2, y + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
        r_img, r_ok = G.project(ref_f, ref_read, tr_r, sh_r, coarse=16, order="cubic")
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(src_f, src_read, tr_s, sh_s, coarse=16, order="cubic")
        if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
            print(f"  {pair_id}: window not covered (ref {r_ok.mean():.4f}, src {s_ok.mean():.4f}) - skipped")
            continue
        r_img, r_fill = G.fill_invalid(r_img, r_ok)
        s_img, s_fill = G.fill_invalid(s_img, s_ok)
        d = PAIRS / pair_id
        d.mkdir(parents=True, exist_ok=True)
        src_p, ref_p = d / f"{pair_id}_source.tif", d / f"{pair_id}_ref.tif"
        import tifffile
        tifffile.imwrite(str(src_p), s_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_s))
        tifffile.imwrite(str(ref_p), r_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_r))
        lat, lon = proj.inv(x, y)
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": tier, "terminology": term, "crs": proj.name,
            "window_centre_map_m": [float(x), float(y)], "window_centre_latlon": [float(lat), float(lon)],
            "window_m": window_m,
            "source": {**src_info, "resampled_gsd_mpp": src_gsd, "shape": list(sh_s), "transform": list(tr_s)},
            "reference": {**ref_info, "resampled_gsd_mpp": ref_gsd, "shape": list(sh_r), "transform": list(tr_r)},
            "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc,
            "sun_note": "scene-level label values (isda:sun_azimuth / sun_elevation), not at the window",
            "scale_ratio": round(ref_gsd / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / ref_gsd, 0, 0], [0, src_gsd / ref_gsd, 0], [0, 0, 1]],
            "prior_note": "both files are on the same north-up local map grid over the same ground, so the "
                          "archive-geometry prior is a pure scale; any rotation or offset the pipeline finds "
                          "is disagreement between the two archive georeferences",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.cut_pradan_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: centre ({lat:.4f}, {lon:.4f}); src {sh_s} @ {src_gsd} m, ref {sh_r} @ "
              f"{ref_gsd} m; d_az {d_az} deg, d_inc {d_inc} deg")
    return out


def nac_product(pid, proj):
    """(frame, reader, info) for an LRO NAC EDR on `proj`, from its product-page corners."""
    from core import geometry as G
    from core.io_loader import load
    page = next((d for d in json.loads(SAC_PAGES.read_text(encoding="utf-8")) if d["pid"] == pid), None)
    if page is None:
        raise SystemExit(f"{pid} is not in {SAC_PAGES}")
    path = DATA / "nac" / f"{pid}.IMG"
    if not path.exists():
        raise SystemExit(f"{path} not downloaded yet ({page['edr_url']})")
    c = lambda k: (page[f"{k} latitude"], page[f"{k} longitude"])  # noqa: E731
    shape = (int(page["Image lines"]), int(page["Line samples"]))
    frame = G.Frame.from_corners(c("Upper left"), c("Upper right"), c("Lower right"), c("Lower left"),
                                 shape, "NAC " + pid, fwd=proj.fwd,
                                 source=f"LROC footprint corners (0.01 deg), bilinear - coarse prior; {proj.name}")
    info = {"instrument": "LRO LROC NAC", "product_id": pid, "path": str(path), "page": page["url"],
            "edr_url": page["edr_url"], "resolution_mpp": page["Resolution"],
            "emission_deg": page["Emission angle"],
            "subsolar": [page["Sub solar latitude"], page["Sub solar longitude"]],
            "start_time": page.get("Start time"),
            "corners_latlon": {k: c(k) for k in ("Upper left", "Upper right", "Lower right", "Lower left")}}
    return frame, (lambda x, y, w, h: load(path, window=(x, y, w, h))[0]), info


def wide_offset(a, va, b, vb, invert=False, gsd=4.0, tpl=300, search=700, blur=2.0, n=7, agree_m=60.0):
    """One translation between two ~4 m overviews, for a prior too far off for the box field.

    `coarse_prior` phase-correlates 512 m boxes, so it can only see offsets under ~256 m. At
    SAC's equatorial site the NAC corner prior and the OHRC grid disagree by ~1.9 km (measured
    19 Sep: 5 of 7 templates agree within 100 m, peaks 0.72-0.90, inverted intensity only). So
    `n` templates of `tpl` px, spread along the OHRC, are searched +/- `search` px in the NAC
    overview (normalised cross-correlation on blurred log intensity), and the offset most of
    them agree on (within `agree_m`) is kept. Returns the NAC map correction (the negated offset)."""
    import cv2

    def prep(z, v):
        z = np.log1p(np.clip(np.nan_to_num(z), 0, None)).astype(np.float32)
        z[~v] = z[v].mean()
        z = cv2.GaussianBlur(z, (0, 0), blur) if blur else z
        return (z - z[v].mean()) / (z[v].std() + 1e-6)
    A, B = prep(a, va), prep(b, vb)
    A = -A if invert else A
    h = tpl // 2
    rows = np.nonzero((va & vb).any(axis=1))[0]
    found = []
    for cy in np.linspace(rows.min() + h + 20, rows.max() - h - 20, n).astype(int):
        cx = int(np.median(np.nonzero(va[cy])[0]))
        if not va[cy - h: cy + h, cx - h: cx + h].all():
            continue
        y0, x0 = max(0, cy - h - search), max(0, cx - h - search)
        r = cv2.matchTemplate(B[y0: cy + h + search, x0: cx + h + search], A[cy - h: cy + h, cx - h: cx + h],
                              cv2.TM_CCOEFF_NORMED)
        _, peak, _, (lx, ly) = cv2.minMaxLoc(r)
        dxp, dyp = lx + x0 - (cx - h), ly + y0 - (cy - h)
        found.append((float(dxp * gsd), float(-dyp * gsd), round(float(peak), 3), int(cy)))
    out = {"polarity": "inverted" if invert else "direct", "templates": found, "n_templates": len(found),
           "n_agree": 0, "apply": False, "tpl_m": tpl * gsd, "search_m": search * gsd}
    if not found:
        return out
    P = np.array([f[:2] for f in found])
    near = [np.hypot(*(P - p).T) <= agree_m for p in P]
    best = max(range(len(P)), key=lambda i: (near[i].sum(), found[i][2]))
    agree = near[best]
    off = np.median(P[agree], axis=0)
    out.update(n_agree=int(agree.sum()), offset_m=off.tolist(), correction_m=(-off).tolist(),
               mean_peak_agreeing=round(float(np.mean([f[2] for f, k in zip(found, agree) if k])), 3),
               apply=bool(agree.sum() >= max(3, len(found) // 2 + 1)))
    return out


def nac_corrected(pid, ohrc_key, proj, ohrc_f, o_read, refit=False):
    """The NAC frame with an affine correction field fitted against the OHRC grid at 4 m, saved
    once per NAC (<data>/site_geometry/<pid>.json) so every window shares one georeference.
    First a wide translation search (`wide_offset`) in case the prior is off by more than the
    box field can see, then the box field. Both intensity polarities are tried at each step;
    the better one is kept and the other recorded beside it."""
    from ops import cut_site_pairs as S
    nac_f, n_read, info = nac_product(pid, proj)
    gp = S.GEOM_DIR / f"{pid}.json"
    if gp.exists() and not refit:
        prior = json.loads(gp.read_text(encoding="utf-8"))
        wide = prior.get("wide_offset") or {}
        if wide.get("apply"):
            nac_f = nac_f.shifted(*wide["correction_m"], note=f"(wide search vs {prior['against']})")
    else:
        cache = DATA / "overviews"
        okey = PRODUCTS[ohrc_key][0].stem
        a, va, b, vb, gt = S.overviews_between(ohrc_f, o_read, okey, nac_f, n_read, pid, cache)
        wides = [wide_offset(a, va, b, vb, invert=inv) for inv in (False, True)]
        wide = max(wides, key=lambda q: (q["n_agree"], q.get("mean_peak_agreeing", 0)))
        for q in wides:
            print(f"wide search ({pid} vs {okey}, {q['polarity']} intensity): {q['n_agree']}/{q['n_templates']} "
                  f"templates agree" + (f" on ({q['offset_m'][0]:+.0f}, {q['offset_m'][1]:+.0f}) m, mean peak "
                                        f"{q['mean_peak_agreeing']}" if q["n_agree"] else ""))
        wide["other_polarity"] = wides[1] if wide is wides[0] else wides[0]
        if wide["apply"]:
            nac_f = nac_f.shifted(*wide["correction_m"], note=f"(wide search vs {okey})")
            a, va, b, vb, gt = S.overviews_between(ohrc_f, o_read, okey, nac_f, n_read, pid, cache)
        tries = [S.coarse_prior(a, va, b, vb, gt, invert=inv) for inv in (False, True)]
        rank = lambda p: (p["apply"], (p["model"] or {}).get("inliers", 0), p["boxes_above_peak"])  # noqa: E731
        prior = max(tries, key=rank)
        other = tries[1] if prior is tries[0] else tries[0]
        for p in tries:
            S._say_prior(f"{pid} vs {okey}, {p['polarity']} intensity", p)
        prior["other_polarity"] = {k: v for k, v in other.items() if k != "boxes"}
        if prior["apply"]:
            nac_c = nac_f.corrected(prior["model"], f"(4 m correlation field vs {okey})")
            a, va, b, vb, gt = S.overviews_between(ohrc_f, o_read, okey, nac_c, n_read, pid, cache)
            check = S.coarse_prior(a, va, b, vb, gt, invert=prior["polarity"] == "inverted")
            S._say_prior(f"{pid} after correction", check)
            prior["after_correction"] = {k: v for k, v in check.items() if k != "boxes"}
        prior.update(nac_pid=pid, against=okey, crs=proj.name, wide_offset=wide)
        S.GEOM_DIR.mkdir(parents=True, exist_ok=True)
        gp.write_text(json.dumps(prior, indent=1), encoding="utf-8")
    if prior.get("apply"):
        nac_f = nac_f.corrected(prior["model"], f"(4 m correlation field vs {prior['against']}, "
                                                f"{prior['polarity']} intensity)")
    return nac_f, n_read, info, prior


def cut_ohrc_nac(kind, n_windows=6, ref_px=640, refit=False):
    """SAC's OHRC <-> NAC pairs: OHRC (native) source, NAC (native) reference, windows picked in
    shared, lit, textured ground on the corrected 4 m overviews."""
    from core import geometry as G
    from ops import cut_site_pairs as S
    ohrc_key, pid, stem = SAC_NAC[kind]
    proj = LocalEqc(*_frame_centre_latlon(PRODUCTS[ohrc_key][1]))
    ohrc_f, o_read, o_info = product(ohrc_key, proj, block=1)
    nac_f, n_read, n_info, prior = nac_corrected(pid, ohrc_key, proj, ohrc_f, o_read, refit=refit)
    n_info["coarse_prior"] = {k: v for k, v in prior.items() if k != "boxes"}
    n_info["geometry"] = nac_f.source
    src_gsd = round(float(np.mean(ohrc_f.gsd())), 3)
    ref_gsd = round(float(np.mean(nac_f.gsd())), 3)
    window_m = ref_px * ref_gsd
    a, va, b, vb, gt = S.overviews_between(ohrc_f, o_read, PRODUCTS[ohrc_key][0].stem, nac_f, n_read, pid,
                                           DATA / "overviews")
    wins = S.pick_windows(a, va, b, vb, gt, window_m, n_windows)
    if not wins:
        raise SystemExit("no lit window fits inside the shared footprint")
    tier, term = S._tier("ohrc", pid.lower())
    o_sun = o_info["sun"]
    ss_lat, ss_lon = n_info["subsolar"]
    out = []
    for k, w in enumerate(wins, 1):
        pair_id = f"{stem}_w{k:02d}"
        x, y = w["cx"], w["cy"]
        x0, y1 = x - window_m / 2, y + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
        r_img, r_ok = G.project(nac_f, n_read, tr_r, sh_r, coarse=16, order="cubic")
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(ohrc_f, o_read, tr_s, sh_s, coarse=32, order="cubic")
        if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
            print(f"  {pair_id}: window not covered (ref {r_ok.mean():.4f}, src {s_ok.mean():.4f}) - skipped")
            continue
        r_img, r_fill = G.fill_invalid(r_img, r_ok)
        s_img, s_fill = G.fill_invalid(s_img, s_ok)
        lat, lon = proj.inv(x, y)
        n_inc, n_az = G.sun_direction(float(lat), float(lon), ss_lat, ss_lon)
        o_inc, o_az = 90.0 - o_sun["elevation_deg_label"], o_sun["azimuth_deg_label"]
        d_az = round(abs((n_az - o_az + 180) % 360 - 180), 1)
        d_inc = round(n_inc - o_inc, 2)
        d = PAIRS / pair_id
        d.mkdir(parents=True, exist_ok=True)
        src_p, ref_p = d / f"{pair_id}_source.tif", d / f"{pair_id}_ref.tif"
        import tifffile
        tifffile.imwrite(str(src_p), s_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_s))
        tifffile.imwrite(str(ref_p), r_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_r))
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": tier, "terminology": term, "crs": proj.name,
            "window_centre_map_m": [float(x), float(y)], "window_centre_latlon": [float(lat), float(lon)],
            "window_m": window_m,
            "map_x_scale_anisotropy": round(math.cos(math.radians(float(lat))) /
                                            math.cos(math.radians(proj.lat_ts)) - 1.0, 5),
            "source": {**o_info, "resampled_gsd_mpp": src_gsd, "shape": list(sh_s), "transform": list(tr_s),
                       "lit_fraction_4m": w["lit"]},
            "reference": {**n_info, "resampled_gsd_mpp": ref_gsd, "shape": list(sh_r), "transform": list(tr_r),
                          "incidence_deg_at_site": round(n_inc, 2), "sun_azimuth_deg_from_north": round(n_az, 1)},
            "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc,
            "sun_note": "OHRC: scene-level label (isda:sun_azimuth / sun_elevation); NAC: computed at the "
                        "window from LROC's published sub-solar point (core.geometry.sun_direction)",
            "scale_ratio": round(ref_gsd / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / ref_gsd, 0, 0], [0, src_gsd / ref_gsd, 0], [0, 0, 1]],
            "prior_note": "both files are on the same north-up local map grid over the same ground, so the "
                          "archive-geometry prior is a pure scale; any rotation or offset the pipeline finds "
                          "is disagreement between the (corrected) archive georeferences",
            "benchmark": "SAC's own pair, arXiv:2509.04775 Table 1",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.cut_pradan_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: centre ({lat:.4f}, {lon:.4f}); src {sh_s} @ {src_gsd} m, ref {sh_r} @ "
              f"{ref_gsd} m; d_az {d_az} deg, d_inc {d_inc} deg")
    return out


def _frame_centre_latlon(grid_csv):
    g = np.loadtxt(grid_csv, delimiter=",", skiprows=1)
    return float(np.median(g[:, 1])), float(np.median(g[:, 0]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=("tmc-fore-aft", "ohrc-tmc", *SAC_NAC))
    ap.add_argument("--windows", type=int, help="default 4 (TMC-2 kinds) or 6 (OHRC-NAC)")
    ap.add_argument("--ref-px", type=int, help="default 384 (TMC-2 kinds) or 640 (OHRC-NAC)")
    ap.add_argument("--refit", action="store_true", help="recompute the saved NAC correction field")
    ap.add_argument("--tmc-product", help="a calibrated TMC-2 nadir product id other than the "
                                          f"{TMC_PASS} pass, for ohrc-tmc; the pair ids become "
                                          "sac_ohrc_tmc<yyyymmdd>_wNN")
    a = ap.parse_args(argv)
    stem = None
    if a.tmc_product:
        if a.kind != "ohrc-tmc":
            raise SystemExit("--tmc-product applies to the ohrc-tmc kind only")
        PRODUCTS["tmcn"] = tmc_nadir(a.tmc_product)
        # no "_a"/"_b" anywhere in the stem (core.pipeline.resolve_pair's hints)
        stem = f"sac_ohrc_tmc{a.tmc_product[12:20]}"
    if a.kind in SAC_NAC:
        dirs = cut_ohrc_nac(a.kind, a.windows or 6, a.ref_px or 640, refit=a.refit)
    else:
        dirs = cut(a.kind, a.windows or 4, a.ref_px or 384, stem=stem)
    print(f"{len(dirs)} pair(s) written under {PAIRS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
