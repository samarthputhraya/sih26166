"""IIRS onto NASA's Moon-wide base map: Chandrayaan-2 IIRS windows registered to the LRO WAC global
morphologic mosaic (100 m, USGS).

    python -m ops.cut_wac_pairs chain_tmc20200607_iirs1555 chain_tmc20200203_iirs1555
    python -m ops.run_real_pairs wac_iirs* --log

WHY. Every other IIRS result here needs a TMC-2 strip from the same orbit. The WAC mosaic covers the
whole Moon, so if IIRS registers onto it, any IIRS strip can be placed on the standard base map
without a partner image. The prior evidence says it is hard: IIRS onto Kaguya TC failed 0/11.

WHAT EACH PAIR IS (Invariant 2): reference LRO WAC global morphologic mosaic (visible, 643 nm, ~100 m,
assembled from many WAC images); source Chandrayaan-2 IIRS band (~74-84 m). Different instruments on
different missions: cross-sensor AND cross-mission. A source band beyond 850 nm is MULTI-MODAL
(visible vs near-infrared).

THE WINDOWS are not chosen here: they are exactly the windows of existing `chain_tmc<day>_iirs<nm>_w*`
pairs (chosen before any matching from the IIRS texture alone, ops/cut_chain_pairs.py), so the same
IIRS ground is registered once onto TMC-2 and once onto WAC. The mosaic is read by HTTP range from
USGS and cached under `<data>/wac/`.

THE SUN. The mosaic is a composite of many WAC images (USGS: incidence chosen for morphology), so it
has no single Sun direction and the file carries none: `d_sun_azimuth_deg` is None and the note says
why. The IIRS strip's Sun is the TMC-2 label value of the same orbit.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import sys
import time

import numpy as np

from ops.cut_chain_pairs import iirs_product
from ops.cut_pradan_pairs import DATA, PAIRS, LocalEqc, _sha, frame_from_grid

WAC_URL = "https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013.tif"
WAC_SHAPE = (54582, 109164)          # rows, cols (read from the file's header, 3 Oct 2026)
WAC_X0, WAC_Y0, WAC_GSD = -5458203.08, 2729101.54, 100.0    # simple cylindrical, sphere 1737.4 km
R = 1737400.0
CACHE = DATA / "wac"
MARGIN_PX = 40


def _wac_rc(lat, lon):
    """Fractional (col, row) of a pixel CENTRE in the global mosaic (pixel (0, 0) centre = (0, 0))."""
    lon = (np.asarray(lon, np.float64) + 180.0) % 360.0 - 180.0
    x = R * np.radians(lon)
    y = R * np.radians(np.asarray(lat, np.float64))
    return (x - WAC_X0) / WAC_GSD - 0.5, (WAC_Y0 - y) / WAC_GSD - 0.5


def wac_chunk(lat, lon, half_m):
    """The mosaic around (lat, lon), at least `half_m` each way plus a margin: (array, row0, col0)."""
    c, r = _wac_rc(lat, lon)
    hr = int(math.ceil(half_m / WAC_GSD)) + MARGIN_PX
    hc = int(math.ceil(half_m / (WAC_GSD * max(math.cos(math.radians(lat)), 0.05)))) + MARGIN_PX
    r0, c0 = int(r) - hr, int(c) - hc
    h, w = 2 * hr, 2 * hc
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"wac100_r{r0}_c{c0}_{h}x{w}.npy"
    if f.exists():
        return np.load(f), r0, c0
    import rasterio
    from rasterio.windows import Window
    with rasterio.open("/vsicurl/" + WAC_URL) as ds:
        a = ds.read(1, window=Window(c0, r0, w, h))
    np.save(f, a)
    return a, r0, c0


def wac_frame(a, r0, c0, proj, step=8):
    """A core.geometry.Frame for the chunk, in the GLOBAL mosaic's pixel coordinates."""
    from core import geometry as G
    h, w = a.shape
    xs = np.unique(np.r_[np.arange(c0, c0 + w, step), c0 + w - 1]).astype(float)
    ys = np.unique(np.r_[np.arange(r0, r0 + h, step), r0 + h - 1]).astype(float)
    gx, gy = np.meshgrid(xs, ys)
    lon = np.degrees((WAC_X0 + (gx + 0.5) * WAC_GSD) / R)
    lat = np.degrees((WAC_Y0 - (gy + 0.5) * WAC_GSD) / R)
    X, Y = proj.fwd(lat, lon)
    return G.Frame("LRO WAC global mosaic", WAC_SHAPE, xs, ys, X, Y,
                   source=f"USGS LRO WAC global morphologic mosaic 100 m (June 2013), simple cylindrical, "
                          f"{WAC_URL}; {proj.name}")


def wac_reader(a, r0, c0):
    def read(x, y, w, h):
        out = np.full((h, w), np.nan, np.float32)
        ys, xs = slice(max(y, r0), min(y + h, r0 + a.shape[0])), slice(max(x, c0), min(x + w, c0 + a.shape[1]))
        if ys.start < ys.stop and xs.start < xs.stop:
            blk = a[ys.start - r0:ys.stop - r0, xs.start - c0:xs.stop - c0].astype(np.float32)
            blk[blk == 0] = np.nan                       # 0 = no data in the mosaic
            out[ys.start - y:ys.stop - y, xs.start - x:xs.stop - x] = blk
        return out
    return read


def _cut_window(pair_id, la, lo, window_m, info_i, grid_i, read_i, shape_i, rule, iirs_sun, extra=None):
    """One IIRS -> WAC pair centred at (la, lo): WAC on a whole number of 100 m pixels, IIRS at its own
    resampled GSD on the same local map. Returns its folder, or None if either image does not cover it."""
    import tifffile
    from core import geometry as G
    t0 = time.perf_counter()
    proj = LocalEqc(la, lo)
    src_f = frame_from_grid(grid_i, shape_i, proj, "IIRS")
    src_gsd = round(float(np.mean(src_f.gsd())), 2)
    ref_px = int(round(window_m / WAC_GSD))
    window_m = ref_px * WAC_GSD
    a, r0, c0 = wac_chunk(la, lo, window_m / 2)
    ref_f = wac_frame(a, r0, c0, proj)
    cx, cy = (float(v) for v in proj.fwd(la, lo))
    x0, y1 = cx - window_m / 2, cy + window_m / 2
    tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, WAC_GSD)
    r_img, r_ok = G.project(ref_f, wac_reader(a, r0, c0), tr_r, sh_r, coarse=8, order="cubic")
    s_px = int(round(window_m / src_gsd))
    tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
    s_img, s_ok = G.project(src_f, read_i, tr_s, sh_s, coarse=8, order="cubic")
    if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
        print(f"  {pair_id}: not fully covered (WAC {r_ok.mean():.3f}, IIRS {s_ok.mean():.3f}) - skipped")
        return None
    r_img, r_fill = G.fill_invalid(r_img, r_ok)
    s_img, s_fill = G.fill_invalid(s_img, s_ok)
    d = PAIRS / pair_id
    d.mkdir(parents=True, exist_ok=True)
    src_p, ref_p = d / f"{pair_id}_source.tif", d / f"{pair_id}_ref.tif"
    tifffile.imwrite(str(src_p), s_img.astype(np.float32), photometric="minisblack",
                     extratags=proj.geotiff_tags(tr_s))
    tifffile.imwrite(str(ref_p), r_img.astype(np.float32), photometric="minisblack",
                     extratags=proj.geotiff_tags(tr_r))
    multimodal = info_i["center_wavelength_nm"] > 850
    meta = {
        "pair_id": pair_id,
        "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "tier": ("C (visible-infrared real, multi-modal; LRO WAC mosaic vs Chandrayaan-2 IIRS, cross-mission)"
                 if multimodal else "B (cross-sensor real, cross-mission; LRO WAC mosaic vs Chandrayaan-2 IIRS)"),
        "terminology": ("cross-sensor AND cross-mission (LRO WAC vs Chandrayaan-2 IIRS); "
                        + ("MULTI-MODAL: visible 643 nm mosaic vs near-infrared" if multimodal
                           else "NOT multi-modal: IIRS band in the visible")),
        "crs": proj.name, "window_centre_map_m": [cx, cy], "window_centre_latlon": [la, lo],
        "window_m": window_m, "window_rule": rule,
        "source": {**info_i, "geometry": src_f.source, "resampled_gsd_mpp": src_gsd,
                   "shape": list(sh_s), "transform": list(tr_s)},
        "reference": {"instrument": "LRO WAC (global morphologic mosaic, USGS, June 2013)",
                      "product_id": "Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013",
                      "path": WAC_URL, "band": "643 nm (visible)", "geometry": ref_f.source,
                      "resampled_gsd_mpp": WAC_GSD, "shape": list(sh_r), "transform": list(tr_r),
                      "sun": None},
        "d_sun_azimuth_deg": None, "d_incidence_deg": None,
        "sun_note": ("the WAC mosaic is a composite of many images with no single Sun (none in the file); "
                     f"IIRS strip Sun (TMC-2 label, same orbit): {iirs_sun}"),
        "scale_ratio": round(WAC_GSD / src_gsd, 3),
        "prior_H_source_to_reference": [[src_gsd / WAC_GSD, 0, 0], [0, src_gsd / WAC_GSD, 0], [0, 0, 1]],
        "prior_note": "both files are on the same north-up local map grid over the same ground, so the "
                      "archive-geometry prior is a pure scale; any offset the pipeline finds is "
                      "disagreement between the IIRS geolocation and the WAC mosaic's control",
        "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
        "files": {q.name: _sha(q) for q in (src_p, ref_p)},
        "cut_seconds": round(time.perf_counter() - t0, 1),
        "command": "python -m ops.cut_wac_pairs " + " ".join(sys.argv[1:]),
        **(extra or {}),
    }
    (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"  {pair_id}: centre ({la:.4f}, {lo:.4f}); IIRS {sh_s} @ {src_gsd} m -> WAC {sh_r} @ "
          f"{WAC_GSD} m ({meta['cut_seconds']} s)", flush=True)
    return d


def _iirs_info(chain_pair_dir):
    m = json.loads((chain_pair_dir / "geometry_prior.json").read_text(encoding="utf-8"))
    info_i = {k: v for k, v in m["reference"].items()
              if k not in ("geometry", "resampled_gsd_mpp", "shape", "transform")}
    return m, info_i


def cut(chain_stem):
    """One WAC pair per window of `chain_stem`_w*: same centre, same window size."""
    out = []
    for p in sorted(PAIRS.glob(f"{chain_stem}_w*")):
        m, info_i = _iirs_info(p)
        pid, band = info_i["product_id"].split()[0], int(info_i["band_index"])
        _, grid_i, read_i, shape_i, _ = iirs_product(pid, band)
        nm = round(info_i["center_wavelength_nm"])
        pair_id = f"wac_iirs{pid[12:20]}_{nm}_{p.name.rsplit('_', 1)[1]}"
        d = _cut_window(pair_id, *m["window_centre_latlon"], m["window_m"], info_i, grid_i, read_i, shape_i,
                        f"the windows of {p.name} exactly (same centre; size rounded to whole WAC pixels)",
                        m["source"].get("sun"))
        if d:
            out.append(d)
    return out


STRIP_PX = 192      # WAC pixels: 8 x 8 squares of 24 px, the area check's smallest cell that may vote


def cut_strip(chain_stem, lat_range=(-90.0, 90.0)):
    """The WHOLE IIRS strip of `chain_stem` onto WAC, edge to edge, no selection: windows of STRIP_PX
    WAC pixels (19.2 km) one window length apart along the IIRS centre line, wherever the strip
    covers the whole window. Big enough that every one of the 8 x 8 squares can vote (24 px), so
    each window gets the region-by-region verdict, not the whole-frame check the 16 smaller
    `wac_` windows (16.1 km, 20-px squares) fell back to. Ids wacstrip_iirs<day>_<nm>_sNNN."""
    import math
    from ops.cut_chain_pairs import _centre_line
    first = sorted(PAIRS.glob(f"{chain_stem}_w*"))[0]
    m, info_i = _iirs_info(first)
    pid, band = info_i["product_id"].split()[0], int(info_i["band_index"])
    _, grid_i, read_i, shape_i, _ = iirs_product(pid, band)
    nm = round(info_i["center_wavelength_nm"])
    lats, lons = _centre_line(grid_i)
    keep = (lats >= lat_range[0]) & (lats <= lat_range[1])
    lats, lons = lats[keep], lons[keep]
    d_km = np.r_[0, np.cumsum(np.hypot(np.diff(lats), np.diff(lons) * np.cos(np.radians(lats[1:]))))] \
        * math.pi / 180 * 1737.4
    win_km = STRIP_PX * WAC_GSD / 1000
    t_start = time.perf_counter()
    out, k = [], 0
    for target in np.arange(win_km / 2, d_km[-1], win_km):
        j = int(np.argmin(np.abs(d_km - target)))
        k += 1
        pair_id = f"wacstrip_iirs{pid[12:20]}_{nm}_s{k:03d}"
        d = _cut_window(pair_id, float(lats[j]), float(lons[j]), STRIP_PX * WAC_GSD, info_i, grid_i, read_i,
                        shape_i, f"the whole IIRS strip of {chain_stem}: every {win_km:.1f} km window along its "
                                 f"centre line, edge to edge, no selection", m["source"].get("sun"),
                        extra={"strip_window_index": k,
                               "strip_seconds_since_start": round(time.perf_counter() - t_start, 1)})
        if d:
            out.append(d)
    print(f"  {len(out)} of {k} strip windows cut in {(time.perf_counter() - t_start) / 60:.1f} min")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("chain_stems", nargs="+", help="e.g. chain_tmc20200607_iirs1555")
    ap.add_argument("--strip", action="store_true", help="the whole IIRS strip, 19.2 km windows (cut_strip)")
    a = ap.parse_args(argv)
    for s in a.chain_stems:
        cut_strip(s) if a.strip else cut(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
