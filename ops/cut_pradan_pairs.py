"""Real pairs from the PRADAN products at SAC's benchmark site.

    python -m ops.cut_pradan_pairs tmc-fore-aft      # TMC-2 fore vs aft, one pass: a REAL viewpoint test
    python -m ops.cut_pradan_pairs ohrc-tmc          # OHRC vs TMC-2 nadir (cross-sensor, same mission)
    python -m ops.cut_pradan_pairs ohrc-tmc --windows 5

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
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import pathlib
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
}
OHRC_BLOCK = 4          # OHRC area-averaged 4x4 before projection (0.26 m -> ~1.05 m)


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


def product(key, proj):
    """(frame, reader, info, native_gsd) for one product; OHRC is area-averaged OHRC_BLOCK x."""
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
    if key != "ohrc":
        return frame, (lambda x, y, w, h: load(xml, window=(x, y, w, h))[0]), info
    f = OHRC_BLOCK

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


def cut(kind, n_windows=4, ref_px=384):
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
        pair_id = {"tmc-fore-aft": "sac_tmcfore_tmcaft", "ohrc-tmc": "sac_ohrc_tmc"}[kind] + f"_w{k:02d}"
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


def _frame_centre_latlon(grid_csv):
    g = np.loadtxt(grid_csv, delimiter=",", skiprows=1)
    return float(np.median(g[:, 1])), float(np.median(g[:, 0]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=("tmc-fore-aft", "ohrc-tmc"))
    ap.add_argument("--windows", type=int, default=4)
    ap.add_argument("--ref-px", type=int, default=384)
    a = ap.parse_args(argv)
    dirs = cut(a.kind, a.windows, a.ref_px)
    print(f"{len(dirs)} pair(s) written under {PAIRS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
