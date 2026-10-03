"""TMC-2 onto the SELENE (Kaguya) Terrain Camera ortho map at SAC's equatorial site: every window
along 3 degrees of one TMC-2 pass, edge to edge, no selection.

    python -m ops.cut_tc_pairs            # tcmap_tmc20250707_sNNN, inside TCO_MAP_02_S12E024S15E027SC
    python -m ops.run_real_pairs "tcmap_tmc20250707_s*" --log

WHAT EACH PAIR IS (Invariant 2): source Chandrayaan-2 TMC-2 nadir (panchromatic, ~5 m), reference the
SELENE TC ortho map v2 (panchromatic visible, 7.4 m, 4096 px/deg, a mosaic of many TC images
orthorectified on TC's own DTMs; JAXA DARTS, PDS3). Different instruments on different missions:
cross-sensor AND cross-mission; both panchromatic visible, so NOT multi-modal. The map is a
composite with no single Sun; the TMC-2 pass's Sun is its label value.

WHERE AND WHY. SAC's own benchmark site (13.3-13.9 S, 25.2 E; paper [1]) lies on TMC-2 pass
20250707T1853 and inside one TC map tile (12-15 S, 24-27 E, read from its PDS label). The windows are
every 384-px TC window (2.84 km) along the TMC-2 strip's centre line inside the tile, one window
length apart, wherever both images cover it - the whole stretch, so no window is chosen by whether
it registers.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import sys
import time

import numpy as np

from ops.cut_chain_pairs import _centre_line, tmc_product
from ops.cut_pradan_pairs import DATA, PAIRS, LocalEqc, _sha, frame_from_grid

TMC_PID = "ch2_tmc_ncn_20250707T1853051045_d_img_d18"
TILE = "TCO_MAP_02_S12E024S15E027SC"
TILE_PATH = DATA / "kaguya_maps" / f"{TILE}.IMG"
TILE_URL = f"https://data.darts.isas.jaxa.jp/pub/pds3/sln-l-tc-5-ortho-map-v2.0/lon024/data/{TILE}.img"
MAX_LAT, WEST_LON, PPD, N = -12.0, 24.0, 4096.0, 12288      # PDS label: pixel CENTRES, 12288 x 12288 u16
TC_GSD = 7.4031617                                            # MAP_SCALE, m per pixel (label)
REF_PX = 384
STEM = "tcmap_tmc20250707"


def tc_tile():
    return np.memmap(TILE_PATH, dtype=">u2", mode="r", shape=(N, N))


def tc_frame(proj, lat, lon, half_m, step=16):
    """A core.geometry.Frame over the tile around (lat, lon), in the tile's own pixel coordinates."""
    from core import geometry as G
    r = (MAX_LAT - lat) * PPD
    c = (lon - WEST_LON) * PPD
    hr = half_m / TC_GSD + 64
    hc = half_m / (TC_GSD * math.cos(math.radians(lat))) + 64
    r0, r1 = max(0, int(r - hr)), min(N - 1, int(r + hr))
    c0, c1 = max(0, int(c - hc)), min(N - 1, int(c + hc))
    xs = np.unique(np.r_[np.arange(c0, c1, step), c1]).astype(float)
    ys = np.unique(np.r_[np.arange(r0, r1, step), r1]).astype(float)
    gx, gy = np.meshgrid(xs, ys)
    X, Y = proj.fwd(MAX_LAT - gy / PPD, WEST_LON + gx / PPD)
    return G.Frame("SELENE TC ortho map", (N, N), xs, ys, X, Y,
                   source=f"{TILE}: simple cylindrical, {PPD:.0f} px/deg, pixel centres from the PDS label; "
                          f"{proj.name}")


def cut(ref_px=REF_PX):
    import tifffile
    from core import geometry as G
    if not TILE_PATH.exists():
        raise SystemExit(f"{TILE_PATH} missing - download {TILE_URL}")
    tile = tc_tile()

    def tc_read(x, y, w, h):
        a = np.asarray(tile[y:y + h, x:x + w], np.float32)
        a[a == 0] = np.nan                                     # 0 = no data in the map
        return a

    xml_t, grid_t, read_t, shape_t, info_t = tmc_product(TMC_PID)
    lats, lons = _centre_line(grid_t)
    window_m = ref_px * TC_GSD
    pad = window_m / 2 / 30300 + 0.002                         # deg of latitude kept clear of the tile edge
    keep = (lats <= MAX_LAT - pad) & (lats >= MAX_LAT - N / PPD + pad)
    lats, lons = lats[keep], lons[keep]
    d_km = np.r_[0, np.cumsum(np.hypot(np.diff(lats), np.diff(lons) * np.cos(np.radians(lats[1:]))))] \
        * math.pi / 180 * 1737.4
    t_start = time.perf_counter()
    out, k = [], 0
    for target in np.arange(window_m / 2000, d_km[-1], window_m / 1000):
        j = int(np.argmin(np.abs(d_km - target)))
        la, lo = float(lats[j]), float(lons[j])
        k += 1
        pair_id = f"{STEM}_s{k:03d}"
        t0 = time.perf_counter()
        proj = LocalEqc(la, lo)
        src_f = frame_from_grid(grid_t, shape_t, proj, "TMC-2 nadir")
        src_gsd = round(float(np.mean(src_f.gsd())), 3)
        ref_f = tc_frame(proj, la, lo, window_m / 2)
        cx, cy = (float(v) for v in proj.fwd(la, lo))
        x0, y1 = cx - window_m / 2, cy + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, TC_GSD)
        r_img, r_ok = G.project(ref_f, tc_read, tr_r, sh_r, coarse=16, order="cubic")
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(src_f, read_t, tr_s, sh_s, coarse=16, order="cubic")
        if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
            print(f"  {pair_id}: not fully covered (TC {r_ok.mean():.3f}, TMC-2 {s_ok.mean():.3f}) - skipped")
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
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": "B (cross-sensor real, cross-mission; Chandrayaan-2 TMC-2 vs SELENE TC ortho map)",
            "terminology": ("cross-sensor AND cross-mission (Chandrayaan-2 TMC-2 vs SELENE Terrain Camera); both "
                            "panchromatic visible, so NOT multi-modal"),
            "crs": proj.name, "window_centre_map_m": [cx, cy], "window_centre_latlon": [la, lo],
            "window_m": window_m,
            "window_rule": (f"every {window_m / 1000:.2f} km window along the TMC-2 centre line inside {TILE}, edge "
                            "to edge, no selection"),
            "source": {**info_t, "geometry": src_f.source, "resampled_gsd_mpp": src_gsd,
                       "shape": list(sh_s), "transform": list(tr_s)},
            "reference": {"instrument": "SELENE (Kaguya) Terrain Camera ortho map v2", "product_id": TILE,
                          "path": TILE_URL, "band": "panchromatic visible (430-850 nm)", "geometry": ref_f.source,
                          "native_gsd_mpp": TC_GSD, "resampled_gsd_mpp": TC_GSD, "shape": list(sh_r),
                          "transform": list(tr_r), "sun": None},
            "d_sun_azimuth_deg": None, "d_incidence_deg": None,
            "sun_note": ("the TC ortho map is a mosaic with no single Sun (none in its label); TMC-2 pass Sun "
                         f"(label): {info_t.get('sun')}"),
            "scale_ratio": round(TC_GSD / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / TC_GSD, 0, 0], [0, src_gsd / TC_GSD, 0], [0, 0, 1]],
            "prior_note": "both files are on the same north-up local map grid over the same ground, so the "
                          "archive-geometry prior is a pure scale; any offset the pipeline finds is "
                          "disagreement between the TMC-2 geolocation and the TC map's",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "cut_seconds": round(time.perf_counter() - t0, 1), "strip_window_index": k,
            "strip_seconds_since_start": round(time.perf_counter() - t_start, 1),
            "command": "python -m ops.cut_tc_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: ({la:.4f}, {lo:.4f}); TMC-2 {sh_s} @ {src_gsd} m -> TC {sh_r} @ {TC_GSD:.2f} m "
              f"({meta['cut_seconds']} s)", flush=True)
    print(f"  {len(out)} of {k} windows cut in {(time.perf_counter() - t_start) / 60:.1f} min")
    return out


def main(argv=None):
    cut()
    return 0


if __name__ == "__main__":
    sys.exit(main())
