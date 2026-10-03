"""Relief parallax removed with a DTM: TMC-2 fore -> aft of one pass, both orthorectified first.

    python -m ops.ortho_tmc                  # cut sac_tmcfore_tmcaft_dtm_w01..w04
    python -m ops.run_real_pairs "sac_tmcfore_tmcaft_dtm_w*" --log

WHY. TMC-2's fore (+25 deg) and aft (-25 deg) cameras see one pass from two directions, so every
point at height h above the sphere the archive lattice is computed on lands ~h (tan e_f + tan e_a)
~ 0.93 h apart in the two images (REPORT "Real viewpoint: TMC-2 fore -> aft"): not a homography,
and only 1 of the 4 windows of sac_tmcfore_tmcaft_w* is accepted. The deck's strategy for relief
is orthorectification; this is it, on the same four windows.

HOW. A ground point P at height h is seen along a ray of emission e from the local vertical and
azimuth a (ground -> spacecraft). A geolocation that assumed a surface dh lower than the true one
puts P dh tan(e) further along the ray, i.e. at P - dh tan(e) (sin a, cos a) in (east, north)
metres. An ORTHO frame maps a true ground position P to the pixel the lattice gives for that
displaced point (`OrthoFrame`).

WHICH HEIGHT (measured 3 Oct, not assumed). The calibrated label says `reference_data_used`
SELENE, and the uncorrected fore and aft lattices agree to ~135 m on the accepted window although
the ground there lies ~970 m below the 1737.4 km sphere - so the lattice already carries terrain at
its nodes (every 100 px, ~590 m). A first cut that corrected the FULL height moved the two images
~1.4 km apart (that double-counts). So dh is the relief the lattice cannot carry: the DTM at P minus
the DTM bilinear between the four lattice nodes around the pixel (`OrthoFrame.lattice_height`).
h comes from the TMC-2 DTM of the SAME pass (`ch2_tmc_ndn_<pass>_d_dtm`, ISRO's derived product,
~10 m posting, controlled to SELENE); e and a come from the spacecraft's sub-satellite point and
altitude in the pass's own orbit-attitude file (<pid>.oat, as ops.cut_chain_pairs.oat_view) at the
time each camera imaged the window, one geometry per window and camera.

WHAT IT IS AND IS NOT. Same instrument, same Sun, two viewpoints (Tier A viewpoint test, NOT
cross-sensor). The DTM was made by ISRO from this pass's own stereo, so this measures whether the
pipeline registers what is left once ISRO's own terrain model is applied - the workflow SAC would
use - not an independent height check. The windows are exactly those of sac_tmcfore_tmcaft_w*.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import re
import sys

import numpy as np

from ops.cut_pradan_pairs import (DATA, PAIRS, PRODUCTS, LocalEqc, _frame_centre_latlon, _sha,
                                  frame_from_grid)

PASS = "ch2_tmc_ndn_20250707T1853051045"
DTM = DATA / "pradan/tmc2/data/derived/20250707" / f"{PASS}_d_dtm_d18.tif"
OAT = DATA / "pradan/tmc2/miscellaneous/calibrated/20250707/ch2_tmc_ncn_20250707T1853051045_d_img_d18.oat"
MOON_R_KM = 1737.4
STEM = "sac_tmcfore_tmcaft_dtm"
BASE_STEM = "sac_tmcfore_tmcaft"


class Dtm:
    """Heights (m) from the TMC-2 DTM GeoTIFF over one lat/lon box, bilinear; NaN off the data."""

    def __init__(self, lat_lo, lat_hi, lon_lo, lon_hi, path=DTM):
        import rasterio
        from rasterio.windows import from_bounds
        with rasterio.open(path) as ds:
            w = from_bounds(lon_lo, lat_lo, lon_hi, lat_hi, ds.transform).round_offsets().round_lengths()
            a = ds.read(1, window=w).astype(np.float64)
            t = ds.window_transform(w)
            nodata = ds.nodata
        if nodata is not None:
            a[a == nodata] = np.nan
        self.h, self.lon0, self.dlon, self.lat0, self.dlat = a, t.c, t.a, t.f, t.e   # pixel EDGE origin

    def __call__(self, lat, lon):
        lat, lon = np.asarray(lat, np.float64), np.asarray(lon, np.float64)
        c = (lon - self.lon0) / self.dlon - 0.5
        r = (lat - self.lat0) / self.dlat - 0.5
        rows, cols = self.h.shape
        c0, r0 = np.floor(c).astype(int), np.floor(r).astype(int)
        ok = (c0 >= 0) & (r0 >= 0) & (c0 < cols - 1) & (r0 < rows - 1)
        c0, r0 = np.clip(c0, 0, cols - 2), np.clip(r0, 0, rows - 2)
        fc, fr = c - c0, r - r0
        H = self.h
        v = ((1 - fc) * (1 - fr) * H[r0, c0] + fc * (1 - fr) * H[r0, c0 + 1]
             + (1 - fc) * fr * H[r0 + 1, c0] + fc * fr * H[r0 + 1, c0 + 1])
        return np.where(ok, v, np.nan)


def _times(xml):
    text = xml.read_text(encoding="latin1")
    t0, t1 = (_dt.datetime.fromisoformat(re.search(rf"<{k}_date_time>([^<]+)<", text).group(1).replace("Z", ""))
              for k in ("start", "stop"))
    n = int(re.findall(r"<elements>(\d+)<", text)[0])
    return t0, t1, n


def _oat_records(path=OAT):
    """(seconds since the first record, sub-spacecraft lat, lon, altitude km) for every ORBTATTD."""
    out = []
    for ln in path.read_text(encoding="latin1").splitlines():
        f = ln.split()
        if len(f) < 40 or f[0] != "ORBTATTD":
            continue
        t = (_dt.datetime(int(f[2][-4:]), int(f[3]), int(f[4]), int(f[5]), int(f[6]), int(f[7]))
             + _dt.timedelta(milliseconds=int(f[8])))
        out.append((t, float(f[-17]), float(f[-16]), float(f[-6])))
    return out


def _unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def view(records, xml, line, lat, lon):
    """(emission deg, azimuth deg of the spacecraft from north) seen from ground (lat, lon) when the
    camera of `xml` imaged image LINE `line` (its time placed linearly between start and stop)."""
    t0, t1, n = _times(xml)
    t = t0 + (t1 - t0) * (max(0.0, min(float(line), n - 1.0)) / max(n - 1, 1))
    rec = min(records, key=lambda r: abs((r[0] - t).total_seconds()))
    s_lat, s_lon, alt = rec[1], rec[2], rec[3]
    g = MOON_R_KM * _unit(lat, lon)
    v = (MOON_R_KM + alt) * _unit(s_lat, s_lon) - g
    v /= np.linalg.norm(v)
    up = _unit(lat, lon)
    east = np.array([-np.sin(np.radians(lon)), np.cos(np.radians(lon)), 0.0])
    north = np.cross(up, east)
    e = float(np.degrees(np.arccos(np.clip(v @ up, -1, 1))))
    a = float(np.degrees(np.arctan2(v @ east, v @ north)) % 360)
    return e, a, abs((rec[0] - t).total_seconds())


class OrthoFrame:
    """A core.geometry.Frame seen through a DTM: map point P (true ground, height h) -> the pixel
    whose sphere-lattice position is P - h tan(e) (sin a, cos a). Only `from_map` is ortho; the
    rest is the base frame's (G.project calls from_map and gsd only)."""

    def __init__(self, base, proj, dtm, emission_deg, azimuth_deg):
        self.base, self.proj, self.dtm = base, proj, dtm
        k = math.tan(math.radians(emission_deg))
        self.kx, self.ky = k * math.sin(math.radians(azimuth_deg)), k * math.cos(math.radians(azimuth_deg))
        self.shape, self.name = base.shape, base.name + " (orthorectified)"
        self.source = (f"{base.source}; ORTHORECTIFIED with {DTM.name} (heights bilinear), emission "
                       f"{emission_deg:.2f} deg, spacecraft azimuth {azimuth_deg:.2f} deg from the pass's .oat")

    def lattice_height(self, x, y):
        """The height the archive lattice already carries at image pixel (x, y): the DTM at the four
        surrounding lattice nodes' ground positions, bilinear in pixel space - the surface a lattice
        sampled every 100 px can represent (module docstring, "WHICH HEIGHT")."""
        b = self.base
        ix = np.clip(np.searchsorted(b.xs, x, side="right") - 1, 0, len(b.xs) - 2)
        iy = np.clip(np.searchsorted(b.ys, y, side="right") - 1, 0, len(b.ys) - 2)
        fx = (x - b.xs[ix]) / (b.xs[ix + 1] - b.xs[ix])
        fy = (y - b.ys[iy]) / (b.ys[iy + 1] - b.ys[iy])
        hn = lambda j, i: self.dtm(*self.proj.inv(b.X[j, i], b.Y[j, i]))  # noqa: E731
        return ((1 - fx) * (1 - fy) * hn(iy, ix) + fx * (1 - fy) * hn(iy, ix + 1)
                + (1 - fx) * fy * hn(iy + 1, ix) + fx * fy * hn(iy + 1, ix + 1))

    def from_map(self, X, Y):
        X, Y = np.asarray(X, np.float64), np.asarray(Y, np.float64)
        lat, lon = self.proj.inv(X, Y)
        h = self.dtm(lat, lon)
        x, y = self.base.from_map(X, Y)                      # first guess, then the residual relief
        for _ in range(2):
            dh = h - self.lattice_height(x, y)
            x, y = self.base.from_map(X - dh * self.kx, Y - dh * self.ky)
        bad = ~np.isfinite(h) | ~np.isfinite(x)
        x, y = np.where(bad, np.nan, x), np.where(bad, np.nan, y)
        return x, y

    def to_map(self, x, y):
        return self.base.to_map(x, y)

    def gsd(self):
        return self.base.gsd()


def cut(n_windows=4):
    """One orthorectified fore -> aft pair per window of sac_tmcfore_tmcaft_w*: same centre, size and
    grids, both images through `OrthoFrame`."""
    import tifffile
    from core import geometry as G
    from core.io_loader import load
    from ops.cut_pradan_pairs import product
    proj = LocalEqc(*_frame_centre_latlon(PRODUCTS["ohrc"][1]))
    src_f, src_read, src_info = product("tmcf", proj)
    ref_f, ref_read, ref_info = product("tmca", proj)
    records = _oat_records()
    out = []
    for k in range(1, n_windows + 1):
        base_id, pair_id = f"{BASE_STEM}_w{k:02d}", f"{STEM}_w{k:02d}"
        m = json.loads((PAIRS / base_id / "geometry_prior.json").read_text(encoding="utf-8"))
        cx, cy = m["window_centre_map_m"]
        window_m = m["window_m"]
        ref_gsd, src_gsd = m["reference"]["resampled_gsd_mpp"], m["source"]["resampled_gsd_mpp"]
        lat, lon = (float(v) for v in proj.inv(cx, cy))
        pad = 3 * window_m / (1000 * 30.3)          # deg; the DTM box covers the window and its parallax
        dtm = Dtm(lat - pad, lat + pad, lon - pad / max(math.cos(math.radians(lat)), 0.1),
                  lon + pad / max(math.cos(math.radians(lat)), 0.1))
        geo = {}
        frames = {}
        for key, base, xml in (("source", src_f, PRODUCTS["tmcf"][0]), ("reference", ref_f, PRODUCTS["tmca"][0])):
            px, py = base.from_map(np.array([cx]), np.array([cy]))
            e, a, dt_s = view(records, xml, float(py[0]), lat, lon)
            geo[key] = {"emission_deg": round(e, 3), "spacecraft_azimuth_deg": round(a, 3),
                        "image_line": round(float(py[0]), 1), "oat_record_dt_s": round(dt_s, 3)}
            frames[key] = OrthoFrame(base, proj, dtm, e, a)
        h_win = dtm(*proj.inv(*np.meshgrid(cx + np.linspace(-window_m / 2, window_m / 2, 41),
                                          cy + np.linspace(-window_m / 2, window_m / 2, 41))))
        x0, y1 = cx - window_m / 2, cy + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
        r_img, r_ok = G.project(frames["reference"], ref_read, tr_r, sh_r, coarse=4, order="cubic")
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(frames["source"], src_read, tr_s, sh_s, coarse=4, order="cubic")
        if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
            print(f"  {pair_id}: not covered (ref {r_ok.mean():.4f}, src {s_ok.mean():.4f}) - skipped")
            continue
        r_img, r_fill = G.fill_invalid(r_img, r_ok)
        s_img, s_fill = G.fill_invalid(s_img, s_ok)
        d = PAIRS / pair_id
        d.mkdir(parents=True, exist_ok=True)
        src_p, ref_p = d / f"{pair_id}_source.tif", d / f"{pair_id}_ref.tif"
        tifffile.imwrite(str(src_p), s_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_s))
        tifffile.imwrite(str(ref_p), r_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_r))
        relief = float(np.nanpercentile(h_win, 99) - np.nanpercentile(h_win, 1))
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": "A (same sensor, viewpoint, real; both orthorectified with the pass's TMC-2 DTM)",
            "terminology": ("same instrument (TMC-2 fore vs aft, one pass, same sun): a VIEWPOINT test, NOT "
                            "cross-sensor; both images orthorectified with ISRO's TMC-2 DTM of the same pass"),
            "crs": proj.name, "window_centre_map_m": [cx, cy], "window_centre_latlon": [lat, lon],
            "window_m": window_m, "window_rule": f"the window of {base_id} exactly (same centre, size, grids)",
            "orthorectification": {"dtm": DTM.name, "view": geo,
                                   "dtm_relief_in_window_m_p1_p99": round(relief, 1),
                                   "height_used": "DTM minus the DTM bilinear between the lattice's 100-px nodes"},
            "source": {**src_info, "geometry": frames["source"].source, "resampled_gsd_mpp": src_gsd,
                       "shape": list(sh_s), "transform": list(tr_s)},
            "reference": {**ref_info, "geometry": frames["reference"].source, "resampled_gsd_mpp": ref_gsd,
                          "shape": list(sh_r), "transform": list(tr_r)},
            "d_sun_azimuth_deg": m.get("d_sun_azimuth_deg"), "d_incidence_deg": m.get("d_incidence_deg"),
            "sun_note": m.get("sun_note"),
            "scale_ratio": round(ref_gsd / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / ref_gsd, 0, 0], [0, src_gsd / ref_gsd, 0], [0, 0, 1]],
            "prior_note": "both files are orthorectified onto the same north-up local map grid, so the prior "
                          "is a pure scale; anything else the pipeline finds is what the DTM and the two "
                          "archive lattices leave",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.ortho_tmc " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: ({lat:.4f}, {lon:.4f}); relief p1-p99 {relief:.0f} m; fore e {geo['source']['emission_deg']}"
              f" az {geo['source']['spacecraft_azimuth_deg']}, aft e {geo['reference']['emission_deg']} az "
              f"{geo['reference']['spacecraft_azimuth_deg']}", flush=True)
    return out


def main(argv=None):
    cut()
    return 0


if __name__ == "__main__":
    sys.exit(main())
