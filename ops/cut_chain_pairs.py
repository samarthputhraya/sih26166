"""Real pairs for the chained route: IIRS and TMC-2 from the SAME orbit, and TMC-2 onto LRO NAC.

    python -m ops.cut_chain_pairs tmc-iirs --tmc ch2_tmc_ncn_20200203T1845562233_d_img_m65 \\
        --iirs ch2_iir_nci_20200203T1845559180_d_img_m65 --band 51 --windows 8
    python -m ops.cut_chain_pairs tmc-iirs ... --band 3 --same-as 1555  # same windows, another band
    python -m ops.cut_chain_pairs nac-tmc --tmc ch2_tmc_ncn_20250707T1853051045_d_img_d18 \\
        --nac M1447829089LE --edr-url <PDS url of the .IMG>           # a NAC with a matching Sun

WHY SAME ORBIT. The problem statement names OHRC, TMC and IIRS. Registered directly, IIRS
(89 m, 1.0-1.6 um) onto Kaguya TC failed 0/11, and OHRC onto TMC-2 failed 4/4 with the Sun 120 deg
apart in azimuth and 60 deg apart in elevation. PRADAN's footprint catalogue shows that IIRS and
TMC-2 were operated TOGETHER: on hundreds of orbits both imaged the same ground seconds apart. On
such a pair the Sun is the same by construction, so what is left is the change of band and the
~16x scale - the multi-modal question on its own, with Chandrayaan-2 on both sides.

WHAT EACH PAIR IS (Invariant 2):
  tmc-iirs  TMC-2 nadir (visible panchromatic, ~5.6 m) -> IIRS band (~80-90 m), one orbit.
            Cross-sensor (different instruments), SAME mission - NOT cross-mission.
            IIRS band beyond TMC-2's passband (above 850 nm): MULTI-MODAL (visible vs infrared).
            IIRS band inside it (band 3, 746 nm): NOT multi-modal - the control.
            (TMC2_PASSBAND_NM below; one rule, so 999 nm is not left sitting on a 1000 nm line.)
            Same orbit, same minute: the Sun difference is ~0 by construction, and the labels say so.

THE WINDOWS are chosen BEFORE any matching, from the reference band alone: candidate squares
every `--step-km` along the IIRS strip's centre line, inside `--lat` and fully covered by both
images, ranked by texture (mean gradient magnitude over the median brightness of the IIRS window)
and taken best-first with centres at least one window apart. `--same-as <band>` reuses another
band's windows exactly, so band-against-band comparisons are on identical ground. The rule is
here so that nobody - including us - can pick windows by whether they registered.

THE MAP is a local equirectangular grid per window (`ops.cut_pradan_pairs.LocalEqc`, standard
parallel and central meridian at the window centre), each image placed through its own archive
geolocation lattice. The prior between the two files of a pair is therefore a pure scale, and
anything else the pipeline finds is the two archives' disagreement.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import json
import math
import pathlib
import re
import sys

import numpy as np

from ops.cut_pradan_pairs import DATA, PAIRS, LocalEqc, _sha, frame_from_grid, tmc_nadir

IIRS_DIR = DATA / "pradan" / "iirs"
# TMC-2 is panchromatic 0.4-0.85 um (PRADAN's TMC-2 payload description). An IIRS band beyond that
# passband is a different part of the spectrum from anything TMC-2 records: multi-modal.
TMC2_PASSBAND_NM = (400, 850)


def _start_utc(xml):
    m = re.search(r"<start_date_time>([^<]+)<", pathlib.Path(xml).read_text(encoding="latin1"))
    return _dt.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")) if m else None


def _hdr_shape(hdr_path):
    t = hdr_path.read_text(encoding="latin1")
    get = lambda k: int(re.search(rf"^\s*{k}\s*=\s*(\d+)", t, re.M | re.I).group(1))  # noqa: E731
    return get("lines"), get("samples")


def iirs_product(pid, band):
    """(xml, grid csv, reader, shape, info) for one IIRS band stored by ops.fetch_pradan."""
    try:
        xml = next(IIRS_DIR.rglob(f"{pid}.xml"))
    except StopIteration:
        raise SystemExit(f"{pid}.xml not under {IIRS_DIR} - fetch it first (python -m ops.fetch_pradan)")
    grid = next(IIRS_DIR.rglob(pid.replace("_d_img_", "_g_grd_") + ".csv"))
    f32 = xml.parent / f"{pid}_band{band:03d}.f32"
    if not f32.exists():
        raise SystemExit(f"{f32.name} not on disk - fetch it: python -m ops.fetch_pradan {pid} --bands {band}")
    shape = _hdr_shape(xml.with_suffix(".hdr"))
    label = xml.read_text(encoding="latin1")
    centres = [float(v) for v in re.findall(r"<center_wavelength[^>]*>([\d.]+)<", label)]
    nm = centres[band - 1]
    img = np.memmap(f32, dtype="<f4", mode="r", shape=shape)

    def read(x, y, w, h):
        a = np.array(img[y:y + h, x:x + w], np.float32)
        a[~np.isfinite(a) | (a <= 0)] = np.nan
        return a
    sun = {k: (re.search(r"<isda:" + k + r"[^>]*>(-?[\d.]+)<", label) or [None, None])[1]
           for k in ("sun_azimuth", "sun_elevation")}
    info = {"instrument": "Chandrayaan-2 IIRS", "product_id": f"{pid} band {band} ({nm:.1f} nm)",
            "path": str(f32), "band": f"{nm:.1f} nm ({'infrared' if nm > TMC2_PASSBAND_NM[1] else 'visible red'})",
            "band_index": band, "center_wavelength_nm": nm,
            "modality": ("infrared, beyond TMC-2's passband" if nm > TMC2_PASSBAND_NM[1]
                         else "visible red, inside TMC-2's passband"),
            "sun": {"azimuth_deg_label": None if sun["sun_azimuth"] is None else float(sun["sun_azimuth"]),
                    "elevation_deg_label": None if sun["sun_elevation"] is None else float(sun["sun_elevation"])}}
    return xml, grid, read, shape, info


def tmc_product(pid):
    from core.io_loader import load
    xml, grid, instrument = tmc_nadir(pid)
    if not xml.exists():
        raise SystemExit(f"{xml} not on disk - fetch it first (python -m ops.fetch_pradan {pid})")
    _, meta = load(xml, window=(0, 0, 8, 8))
    info = {"instrument": instrument, "product_id": pid, "path": str(xml),
            "native_gsd_mpp_label": meta.get("gsd_mpp"),
            "sun": {"azimuth_deg_label": meta.get("sun_azimuth"), "elevation_deg_label": meta.get("sun_elevation")}}
    return xml, grid, (lambda x, y, w, h: load(xml, window=(x, y, w, h))[0]), meta["full_shape"], info


def _centre_line(grid_csv):
    """(lat, lon) along the strip's centre sample, top to bottom: interpolated between the two
    lattice columns either side of it. An IIRS strip is only ~16 km wide and a 192-px window is
    ~14 km, so the nearest lattice column (sample 100 of 250) is not centre enough."""
    g = np.loadtxt(grid_csv, delimiter=",", skiprows=1)
    lon, lat, px, sc = g.T
    cols = np.unique(px)
    mid = (cols.min() + cols.max()) / 2.0
    lo_c, hi_c = cols[cols <= mid].max(), cols[cols >= mid].min()
    w = 0.0 if hi_c == lo_c else (mid - lo_c) / (hi_c - lo_c)
    out = []
    for c in (lo_c, hi_c):
        k = px == c
        order = np.argsort(sc[k])
        out.append((lat[k][order], lon[k][order]))
    return (1 - w) * out[0][0] + w * out[1][0], (1 - w) * out[0][1] + w * out[1][1]


def _cut_one(lat, lon, t, i, ref_px, with_source=True):
    """Project both images onto a local grid centred at (lat, lon). Returns None if not covered."""
    from core import geometry as G
    proj = LocalEqc(lat, lon)
    ref_f = frame_from_grid(i["grid"], i["shape"], proj, "IIRS")
    src_f = frame_from_grid(t["grid"], t["shape"], proj, "TMC-2 nadir")
    ref_gsd = round(float(np.mean(ref_f.gsd())), 2)
    src_gsd = round(float(np.mean(src_f.gsd())), 3)
    window_m = ref_px * ref_gsd
    # LocalEqc's y is R x latitude (0 at the equator, not at lat_ts), so the window centre is
    # proj.fwd(lat, lon) = (0, R lat), not the origin
    cx, cy = (float(v) for v in proj.fwd(lat, lon))
    x0, y1 = cx - window_m / 2, cy + window_m / 2
    tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
    r_img, r_ok = G.project(ref_f, i["read"], tr_r, sh_r, coarse=8, order="cubic")
    if r_ok.mean() < 0.998:
        return None
    s_px = int(round(window_m / src_gsd))
    tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
    if not with_source:
        # candidates only: is the TMC-2 there at all? (a grid of 9 points, not a 3000-px resample)
        gx, gy = np.meshgrid(x0 + window_m * np.array([0.01, 0.5, 0.99]), y1 - window_m * np.array([0.01, 0.5, 0.99]))
        sx, sy = src_f.from_map(gx.ravel(), gy.ravel())
        rows, cols = t["shape"]
        inside = np.isfinite(sx) & np.isfinite(sy) & (sx >= 0) & (sy >= 0) & (sx <= cols - 1) & (sy <= rows - 1)
        return None if not inside.all() else dict(proj=proj, window_m=window_m, r=(r_img, r_ok, tr_r, sh_r))
    s_img, s_ok = G.project(src_f, t["read"], tr_s, sh_s, coarse=32, order="cubic")
    if s_ok.mean() < 0.998:
        return None
    return dict(proj=proj, ref_f=ref_f, src_f=src_f, ref_gsd=ref_gsd, src_gsd=src_gsd, window_m=window_m,
                centre_map=(cx, cy), r=(r_img, r_ok, tr_r, sh_r), s=(s_img, s_ok, tr_s, sh_s))


def _texture(img):
    gy, gx = np.gradient(img.astype(np.float64))
    return float(np.mean(np.hypot(gx, gy)) / (np.median(img) + 1e-9))


def choose_windows(t, i, n, ref_px, lat_range, step_km):
    """Pre-registered window rule (module docstring): texture of the REFERENCE only, spaced apart."""
    lats, lons = _centre_line(i["grid"])
    keep = (lats >= lat_range[0]) & (lats <= lat_range[1])
    lats, lons = lats[keep], lons[keep]
    if not len(lats):
        raise SystemExit(f"the IIRS strip has no lattice node between latitudes {lat_range}")
    # candidates every step_km along the centre line (lattice rows are denser than that)
    d = np.r_[0, np.cumsum(np.hypot(np.diff(lats), np.diff(lons) * np.cos(np.radians(lats[1:]))))] \
        * math.pi / 180 * 1737.4
    cands = []
    for target in np.arange(0, d[-1], step_km):
        j = int(np.argmin(np.abs(d - target)))
        c = _cut_one(float(lats[j]), float(lons[j]), t, i, ref_px, with_source=False)
        if c is None:
            continue
        r_img, r_ok = c["r"][0], c["r"][1]
        win_m = c["window_m"]
        cands.append((_texture(np.where(r_ok, r_img, np.nanmedian(r_img))), float(lats[j]), float(lons[j]), float(d[j])))
        print(f"  candidate {lats[j]:+.3f}, {lons[j]:.3f}: texture {cands[-1][0]:.4f}", flush=True)
    cands.sort(reverse=True)
    chosen = []
    win_km = win_m / 1000.0 if cands else 0.0
    for tex, la, lo, dk in cands:
        if all(abs(dk - c[3]) >= 1.05 * win_km for c in chosen):   # centres at least one window apart
            chosen.append((tex, la, lo, dk))
        if len(chosen) == n:
            break
    return sorted(chosen, key=lambda c: -c[1])  # north to south


def cut_tmc_iirs(tmc_pid, iirs_pid, band, n_windows=8, ref_px=192, lat_range=(-60.0, 60.0), step_km=15.0,
                 same_as=None):
    xml_t, grid_t, read_t, shape_t, info_t = tmc_product(tmc_pid)
    xml_i, grid_i, read_i, shape_i, info_i = iirs_product(iirs_pid, band)
    t = dict(grid=grid_t, read=read_t, shape=shape_t)
    i = dict(grid=grid_i, read=read_i, shape=shape_i)
    stem = f"chain_tmc{tmc_pid[12:20]}_iirs{round(info_i['center_wavelength_nm'])}"
    if same_as:
        other = f"chain_tmc{tmc_pid[12:20]}_iirs{same_as}"
        centres = []
        for p in sorted(PAIRS.glob(f"{other}_w*")):
            m = json.loads((p / "geometry_prior.json").read_text(encoding="utf-8"))
            centres.append((None, *m["window_centre_latlon"], None))
        if not centres:
            raise SystemExit(f"no {other}_w* pairs to copy windows from")
        rule = f"the windows of {other}_w* (same ground, another band)"
    else:
        centres = choose_windows(t, i, n_windows, ref_px, lat_range, step_km)
        rule = (f"pre-registered: candidates every {step_km} km along the IIRS centre line within latitude "
                f"{lat_range}, fully covered by both, ranked by the IIRS window's texture, best-first at least "
                f"one window apart (ops/cut_chain_pairs.py docstring)")
    multimodal = info_i["center_wavelength_nm"] > TMC2_PASSBAND_NM[1]
    tier = ("C (visible-infrared real, multi-modal; Chandrayaan-2 TMC-2 vs IIRS, same orbit)" if multimodal
            else "B (cross-sensor real, TMC-2 vs an IIRS band inside TMC-2 passband, same orbit)")
    term = ("cross-sensor (Chandrayaan-2 TMC-2 vs IIRS), same mission - NOT cross-mission; "
            + ("MULTI-MODAL: visible panchromatic vs near-infrared" if multimodal
               else f"NOT multi-modal: IIRS band inside TMC-2's {TMC2_PASSBAND_NM[0]}-{TMC2_PASSBAND_NM[1]} nm "
                    "passband - the control")
            + "; same orbit, so the same Sun")
    s_sun, r_sun = info_t["sun"], info_i["sun"]
    d_az = d_inc = None
    sun_note = "scene-level label values (isda:sun_azimuth / sun_elevation); same orbit, seconds apart"
    starts = [_start_utc(xml_t), _start_utc(xml_i)]
    gap = abs((starts[0] - starts[1]).total_seconds()) if all(starts) else None
    if s_sun["azimuth_deg_label"] is not None and r_sun["azimuth_deg_label"] is not None:
        d_az = round(abs((r_sun["azimuth_deg_label"] - s_sun["azimuth_deg_label"] + 180) % 360 - 180), 1)
        d_inc = round((90 - r_sun["elevation_deg_label"]) - (90 - s_sun["elevation_deg_label"]), 2)
    elif gap is not None and gap < 60:
        # The IIRS calibrated label carries no Sun fields (checked 28 Sep on 20200203T1845). Both
        # instruments look at nadir and started their strips `gap` seconds apart, so each piece of
        # ground is imaged by both within seconds; the Sun moves ~0.5 deg per hour over the Moon.
        d_az, d_inc = 0.0, 0.0
        sun_note = (f"IIRS label has no Sun fields; both nadir strips start {gap:.1f} s apart "
                    f"({starts[0]:%H:%M:%S.%f} TMC-2, {starts[1]:%H:%M:%S.%f} IIRS UTC), so the Sun is the same "
                    f"to well under 0.1 deg: difference set to 0 by construction. TMC-2 label: azimuth "
                    f"{s_sun['azimuth_deg_label']}, elevation {s_sun['elevation_deg_label']} (strip centre)")
    out = []
    import tifffile
    from core import geometry as G
    for k, (tex, la, lo, _) in enumerate(centres, 1):
        pair_id = f"{stem}_w{k:02d}"
        c = _cut_one(la, lo, t, i, ref_px)
        if c is None:
            print(f"  {pair_id}: window not covered - skipped")
            continue
        r_img, r_ok, tr_r, sh_r = c["r"]
        s_img, s_ok, tr_s, sh_s = c["s"]
        r_img, r_fill = G.fill_invalid(r_img, r_ok)
        s_img, s_fill = G.fill_invalid(s_img, s_ok)
        d = PAIRS / pair_id
        d.mkdir(parents=True, exist_ok=True)
        src_p, ref_p = d / f"{pair_id}_source.tif", d / f"{pair_id}_ref.tif"
        tifffile.imwrite(str(src_p), s_img.astype(np.float32), photometric="minisblack",
                         extratags=c["proj"].geotiff_tags(tr_s))
        tifffile.imwrite(str(ref_p), r_img.astype(np.float32), photometric="minisblack",
                         extratags=c["proj"].geotiff_tags(tr_r))
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": tier, "terminology": term, "crs": c["proj"].name,
            "window_centre_map_m": list(c["centre_map"]), "window_centre_latlon": [la, lo],
            "window_m": c["window_m"], "window_rule": rule,
            "texture_score": tex,
            "source": {**info_t, "geometry": c["src_f"].source, "resampled_gsd_mpp": c["src_gsd"],
                       "shape": list(sh_s), "transform": list(tr_s)},
            "reference": {**info_i, "geometry": c["ref_f"].source, "resampled_gsd_mpp": c["ref_gsd"],
                          "shape": list(sh_r), "transform": list(tr_r)},
            "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc,
            "sun_note": sun_note,
            "scale_ratio": round(c["ref_gsd"] / c["src_gsd"], 3),
            "prior_H_source_to_reference": [[c["src_gsd"] / c["ref_gsd"], 0, 0], [0, c["src_gsd"] / c["ref_gsd"], 0],
                                            [0, 0, 1]],
            "prior_note": "both files are on the same north-up local map grid over the same ground, so the "
                          "archive-geometry prior is a pure scale; any rotation or offset the pipeline finds "
                          "is disagreement between the two archive georeferences",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.cut_chain_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: centre ({la:.4f}, {lo:.4f}); src {sh_s} @ {c['src_gsd']} m, ref {sh_r} @ "
              f"{c['ref_gsd']} m; d_az {d_az}, d_inc {d_inc}")
    return out


# --- LRO NAC -> TMC-2 at SAC's site ------------------------------------------------------------

LROC_PAGE = "https://data.lroc.im-ldi.com/lroc/view_lroc/LRO-L-LROC-2-EDR-V1.0/{pid}"


def nac_page(pid, edr_url):
    """LROC's product-page fields for one NAC EDR, cached in <data>/nac/nac_chain_pages.json in the
    same shape as nac_sac_pages.json (so ops.cut_pradan_pairs.nac_product reads it unchanged)."""
    import html
    import urllib.request
    from ops.cut_pradan_pairs import CHAIN_PAGES
    pages = json.loads(CHAIN_PAGES.read_text(encoding="utf-8")) if CHAIN_PAGES.exists() else []
    hit = next((p for p in pages if p["pid"] == pid), None)
    if hit:
        return hit
    url = LROC_PAGE.format(pid=pid)
    text = urllib.request.urlopen(url, timeout=120).read().decode("utf-8", "replace")
    page = {"pid": pid, "url": url}
    # one field per two-cell table row (the page opens with a downloads cell that is not a field,
    # and its rows close <td> with </th>, so rows are split first and cells counted per row)
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                 for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]
        if len(cells) != 2 or not cells[0]:
            continue
        k, v = cells
        try:
            page[k] = float(v)
        except ValueError:
            page[k] = v
    need = ("Image lines", "Line samples", "Resolution", "Sub solar latitude", "Sub solar longitude",
            "Upper left latitude", "Lower right longitude")
    missing = [k for k in need if k not in page]
    if missing or page.get("Product") != pid:
        raise SystemExit(f"{url}: could not read {missing or 'the product id'} from the page")
    page["edr_url"] = edr_url
    pages.append(page)
    CHAIN_PAGES.write_text(json.dumps(pages, indent=1), encoding="utf-8")
    return page


def _with_drift(q, agree_m=60.0):
    """`wide_offset` asks its templates to agree on ONE translation within `agree_m`. Along a 25 km
    NAC strip the corner prior's error is a translation that drifts: on 28 Sep all 11 templates of
    M1258792259LE against SAC's NAC peaked at 0.74-0.86 on offsets sliding smoothly from (+432,
    +2052) to (+312, +1852) m, and only 5 fell inside one 60 m circle. So the same majority rule is
    applied to a straight-line fit of offset against position along the strip; when it passes, the
    median offset is removed and the residual drift (well under the box field's ~256 m reach) is
    left to the 4 m field, exactly as for a plain translation."""
    t = q.get("templates") or []
    if q.get("apply") or len(t) < 5:
        return q
    T = np.array([x[:2] for x in t], float)
    rows = np.array([x[3] for x in t], float)
    A = np.c_[rows, np.ones_like(rows)]
    coef, *_ = np.linalg.lstsq(A, T, rcond=None)
    ok = np.hypot(*(T - A @ coef).T) <= agree_m
    if ok.sum() >= max(3, len(t) // 2 + 1):
        off = np.median(T[ok], axis=0)
        q = dict(q, apply=True, n_agree=int(ok.sum()), offset_m=off.tolist(), correction_m=(-off).tolist(),
                 mean_peak_agreeing=round(float(np.mean([x[2] for x, k in zip(t, ok) if k])), 3),
                 model="translation drifting linearly along the strip; median removed",
                 drift_m_per_px=coef[0].tolist())
    return q


def correct_against_anchor(nac_pid, anchor_pid, proj, ohrc_f, o_read):
    """Fit `nac_pid`'s 4 m correction field against an already-corrected NAC `anchor_pid` and save
    it where ops.cut_pradan_pairs.nac_corrected will load it (<data>/site_geometry/<pid>.json).

    For a NAC whose Sun is too far from the OHRC's for the two to correlate (a NAC picked to match
    a TMC-2 pass is, by design, far from the OHRC's low western Sun). The anchor is itself
    corrected against the OHRC grid, so the chain stays in the OHRC-aligned frame and never
    touches the TMC-2 image the NAC is about to be registered to. Same fit as
    ops.cut_site_pairs.correct_against, on SAC's local map instead of the 74 S polar one."""
    from ops import cut_pradan_pairs as CP
    from ops import cut_site_pairs as S
    anchor, a_read, _, a_prior = CP.nac_corrected(anchor_pid, "ohrc", proj, ohrc_f, o_read)
    if not a_prior.get("apply"):
        raise SystemExit(f"anchor {anchor_pid} has no applied correction")
    nac, n_read, _ = CP.nac_product(nac_pid, proj)
    ov = S.overviews_between(anchor, a_read, anchor_pid, nac, n_read, nac_pid, DATA / "overviews")
    if ov is None:
        raise SystemExit(f"{nac_pid} does not overlap its anchor {anchor_pid}")
    a, va, b, vb, gt = ov
    # first a wide translation search, as nac_corrected does: LROC's corners can be kilometres off
    # (SAC's own NAC was off by ~1.9 km), and the box field only sees offsets under ~256 m
    # 12 templates, not 7: a NAC strip overlaps its anchor over a shorter stretch than an OHRC frame
    wides = [_with_drift(CP.wide_offset(a, va, b, vb, invert=inv, n=12)) for inv in (False, True)]
    wide = max(wides, key=lambda q: (q["n_agree"], q.get("mean_peak_agreeing", 0)))
    for q in wides:
        print(f"wide search ({nac_pid} vs anchor {anchor_pid}, {q['polarity']} intensity): {q['n_agree']}/"
              f"{q['n_templates']} templates agree" + (f" on ({q['offset_m'][0]:+.0f}, {q['offset_m'][1]:+.0f}) m, "
                                                        f"mean peak {q['mean_peak_agreeing']}" if q["n_agree"] else ""))
    wide["other_polarity"] = wides[1] if wide is wides[0] else wides[0]
    if wide["apply"]:
        nac = nac.shifted(*wide["correction_m"], note=f"(wide search vs anchor {anchor_pid})")
        a, va, b, vb, gt = S.overviews_between(anchor, a_read, anchor_pid, nac, n_read, nac_pid, DATA / "overviews")
    tries = [S.coarse_prior(a, va, b, vb, gt, invert=inv) for inv in (False, True)]
    rank = lambda p: (p["apply"], (p["model"] or {}).get("inliers", 0), p["boxes_above_peak"])  # noqa: E731
    prior = max(tries, key=rank)
    other = tries[1] if prior is tries[0] else tries[0]
    for p in tries:
        S._say_prior(f"{nac_pid} vs anchor {anchor_pid}, {p['polarity']} intensity", p)
    prior["other_polarity"] = {k: v for k, v in other.items() if k != "boxes"}
    if prior["apply"]:
        nac_c = nac.corrected(prior["model"], f"(4 m correlation field vs anchor {anchor_pid})")
        a, va, b, vb, gt = S.overviews_between(anchor, a_read, anchor_pid, nac_c, n_read, nac_pid,
                                               DATA / "overviews")
        check = S.coarse_prior(a, va, b, vb, gt, invert=prior["polarity"] == "inverted")
        S._say_prior(f"{nac_pid} after correction", check)
        prior["after_correction"] = {k: v for k, v in check.items() if k != "boxes"}
    prior.update(nac_pid=nac_pid, against=f"anchor {anchor_pid}", anchor=anchor_pid, wide_offset=wide,
                 anchor_chain=[anchor_pid, f"ohrc {CP.PRODUCTS['ohrc'][0].stem}"], crs=proj.name)
    S.GEOM_DIR.mkdir(parents=True, exist_ok=True)
    (S.GEOM_DIR / f"{nac_pid}.json").write_text(json.dumps(prior, indent=1), encoding="utf-8")
    return prior


def cut_nac_tmc(tmc_pid, nac_pid, edr_url, n_windows=6, ref_px=384, refit=False, anchor=None):
    """LRO NAC (source, native ~0.8 m) -> TMC-2 nadir (reference, ~5.6 m) at SAC's benchmark frame.

    The NAC is chosen for a Sun that matches the TMC-2 pass (Sun vectors a few degrees apart at the
    site), so this is the TMC-2 leg with the illumination variable taken out.

    WHICH GEOMETRY PRIOR. `anchor="corners"` (the default for this kind) uses LROC's published
    corners as they are: an independent georeference from another mission, never fitted to the
    TMC-2. The alternative - the 4 m field against the OHRC grid (directly or through an anchor NAC)
    - puts the NAC in the OHRC's frame, and on 28 Sep that frame turned out to sit ~2 km from
    BOTH TMC-2 passes over it (2020-02-03 and 2025-07-07, independently: offsets (-516, -1948) and
    (-504, -1932) m against the OHRC-aligned NAC), while LROC's own corners sit within ~160 m of
    them. So SAC's OHRC frame, not the NACs, carries the ~2 km archive offset at this site, and an
    OHRC-aligned prior would put every window 2 km off its TMC-2 ground."""
    from core import geometry as G
    from core.io_loader import load
    from ops import cut_pradan_pairs as CP
    from ops import cut_site_pairs as S
    page = nac_page(nac_pid, edr_url)
    if not (DATA / "nac" / f"{nac_pid}.IMG").exists():
        raise SystemExit(f"{nac_pid}.IMG not in {DATA / 'nac'} - download {edr_url}")
    proj = LocalEqc(*CP._frame_centre_latlon(CP.PRODUCTS["ohrc"][1]))
    if anchor in (None, "corners"):
        nac_f, n_read, n_info = CP.nac_product(nac_pid, proj)
        n_info["coarse_prior"] = {"model": "none: LROC's published corners, uncorrected (see docstring)"}
    else:
        ohrc_f, o_read, _ = CP.product("ohrc", proj, block=1)
        if anchor != "ohrc" and (refit or not (S.GEOM_DIR / f"{nac_pid}.json").exists() or json.loads(
                (S.GEOM_DIR / f"{nac_pid}.json").read_text(encoding="utf-8")).get("anchor") != anchor):
            correct_against_anchor(nac_pid, anchor, proj, ohrc_f, o_read)
            refit = False
        nac_f, n_read, n_info, prior = CP.nac_corrected(nac_pid, "ohrc", proj, ohrc_f, o_read, refit=refit)
        if not prior.get("apply"):
            raise SystemExit(f"{nac_pid}: no trustworthy correction against the OHRC grid")
        n_info["coarse_prior"] = {k: v for k, v in prior.items() if k != "boxes"}
    n_info["geometry"] = nac_f.source
    xml_t, grid_t, read_t, shape_t, info_t = tmc_product(tmc_pid)
    tmc_f = frame_from_grid(grid_t, shape_t, proj, "TMC-2 nadir")
    ref_gsd = round(float(np.mean(tmc_f.gsd())), 3)
    src_gsd = round(float(np.mean(nac_f.gsd())), 3)
    window_m = ref_px * ref_gsd
    ov = S.overviews_between(tmc_f, read_t, tmc_pid, nac_f, n_read, nac_pid, DATA / "overviews")
    if ov is None:
        raise SystemExit(f"{tmc_pid} and {nac_pid} do not overlap")
    a, va, b, vb, gt = ov
    wins = S.pick_windows(a, va, b, vb, gt, window_m, n_windows)
    if not wins:
        raise SystemExit("no lit window of that size fits inside the shared footprint")
    t_sun = info_t["sun"]
    ss_lat, ss_lon = n_info["subsolar"]
    stem = f"chain_nac{nac_pid.lower()}_tmc{tmc_pid[12:20]}"
    tier = "B (cross-sensor real, nac-tmc2)"
    term = ("cross-sensor, cross-mission (LRO LROC NAC vs Chandrayaan-2 TMC-2 nadir); both panchromatic "
            "visible, so NOT multi-modal; NAC chosen for a Sun close to the TMC-2 pass's")
    out = []
    import tifffile
    for k, w in enumerate(wins, 1):
        pair_id = f"{stem}_w{k:02d}"
        x, y = w["cx"], w["cy"]
        x0, y1 = x - window_m / 2, y + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
        r_img, r_ok = G.project(tmc_f, read_t, tr_r, sh_r, coarse=16, order="cubic")
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(nac_f, n_read, tr_s, sh_s, coarse=32, order="cubic")
        if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
            print(f"  {pair_id}: window not covered (ref {r_ok.mean():.4f}, src {s_ok.mean():.4f}) - skipped")
            continue
        r_img, r_fill = G.fill_invalid(r_img, r_ok)
        s_img, s_fill = G.fill_invalid(s_img, s_ok)
        lat, lon = proj.inv(x, y)
        n_inc, n_az = G.sun_direction(float(lat), float(lon), ss_lat, ss_lon)
        t_inc, t_az = 90.0 - t_sun["elevation_deg_label"], t_sun["azimuth_deg_label"]
        d_az = round(abs((t_az - n_az + 180) % 360 - 180), 1)
        d_inc = round(t_inc - n_inc, 2)
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
            "tier": tier, "terminology": term, "crs": proj.name,
            "window_centre_map_m": [float(x), float(y)], "window_centre_latlon": [float(lat), float(lon)],
            "window_m": window_m, "window_rule": "ops.cut_site_pairs.pick_windows on the 4 m overviews: shared, "
                                                 "lit, textured, spread out - no matching involved",
            "source": {**n_info, "resampled_gsd_mpp": src_gsd, "shape": list(sh_s), "transform": list(tr_s),
                       "incidence_deg_at_site": round(n_inc, 2), "sun_azimuth_deg_from_north": round(n_az, 1)},
            "reference": {**info_t, "geometry": tmc_f.source, "resampled_gsd_mpp": ref_gsd, "shape": list(sh_r),
                          "transform": list(tr_r)},
            "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc,
            "sun_note": "NAC: computed at the window from LROC's published sub-solar point "
                        "(core.geometry.sun_direction); TMC-2: scene-level label (the strip centre, not the window)",
            "scale_ratio": round(ref_gsd / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / ref_gsd, 0, 0], [0, src_gsd / ref_gsd, 0], [0, 0, 1]],
            "prior_note": "both files are on the same north-up local map grid over the same ground, so the "
                          "archive-geometry prior is a pure scale; any rotation or offset the pipeline finds "
                          "is disagreement between the TMC-2 archive grid and the NAC's geometry prior "
                          "(see source.coarse_prior: LROC's published corners unless --anchor says otherwise)",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.cut_chain_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: centre ({lat:.4f}, {lon:.4f}); src {sh_s} @ {src_gsd} m, ref {sh_r} @ "
              f"{ref_gsd} m; d_az {d_az} deg, d_inc {d_inc} deg")
    return out


# --- OHRC -> TMC-2 again, with the OHRC placed by LRO's geometry ---------------------------------

SAC_NAC = "M1350459544RE"


def ohrc_to_lroc_shift(proj, ohrc_f, nac_pid=SAC_NAC):
    """The map shift that puts an OHRC frame into LROC's geometry, from the correction a NAC
    carries against it (<data>/site_geometry/<nac_pid>.json; for SAC's frame, M1350459544RE,
    fitted 19 Sep against the OHRC at 4 m, frozen evidence): the NAC was moved by `correction_m`
    plus an affine field to sit on the OHRC, so the OHRC moves by minus that displacement,
    evaluated at the OHRC frame's centre. Uses no TMC-2 pixel."""
    from ops import cut_site_pairs as S
    p = json.loads((S.GEOM_DIR / f"{nac_pid}.json").read_text(encoding="utf-8"))
    dx, dy = p["wide_offset"]["correction_m"] if (p.get("wide_offset") or {}).get("apply") else (0.0, 0.0)
    rows, cols = ohrc_f.shape
    ox, oy = (float(v[0]) for v in ohrc_f.to_map(np.array([cols / 2.0]), np.array([rows / 2.0])))
    if p.get("apply"):
        A = np.asarray(p["model"]["A"], float)
        cx, cy = p["model"]["centre"]
        dx += A[0, 0] * (ox - cx) + A[0, 1] * (oy - cy) + A[0, 2]
        dy += A[1, 0] * (ox - cx) + A[1, 1] * (oy - cy) + A[1, 2]
    return -dx, -dy


def cut_ohrc_tmc(tmc_pid, n_windows=4, ref_px=384):
    """OHRC (source, area-averaged 4x4, ~1.1 m) -> TMC-2 nadir (reference) on SAC's frame, the frozen
    `ops.cut_pradan_pairs ohrc-tmc` cut in every respect but one: the OHRC frame is first moved into
    LRO's geometry (`ohrc_to_lroc_shift`).

    WHY. The frozen OHRC -> TMC-2 pairs (4/4 refused) were cut on the two archives' own grids. On
    28 Sep the OHRC grid at this site turned out to sit ~2 km from BOTH TMC-2 passes (via SAC's NAC,
    whose LROC corners agree with TMC-2 to ~160 m), and a 384-px TMC-2 window is only ~2.1 km: those
    windows barely shared ground. Their refusal was right - the answers were wrong - but it cannot be
    blamed on the Sun alone. This cut asks the Sun question with the geometry taken out."""
    from core import geometry as G
    from ops import cut_pradan_pairs as CP
    import tifffile
    proj = LocalEqc(*CP._frame_centre_latlon(CP.PRODUCTS["ohrc"][1]))
    ohrc_f, o_read, o_info = CP.product("ohrc", proj)          # area-averaged 4x4, as frozen
    sx, sy = ohrc_to_lroc_shift(proj, ohrc_f)
    ohrc_f = ohrc_f.shifted(sx, sy, note=f"(into LROC's geometry via {SAC_NAC}'s saved correction)")
    o_info["geometry"] = ohrc_f.source
    xml_t, grid_t, read_t, shape_t, info_t = tmc_product(tmc_pid)
    tmc_f = frame_from_grid(grid_t, shape_t, proj, "TMC-2 nadir")
    info_t["geometry"] = tmc_f.source
    ref_gsd = round(float(np.mean(tmc_f.gsd())), 3)
    src_gsd = round(float(np.mean(ohrc_f.gsd())), 3)
    window_m = ref_px * ref_gsd
    rows, cols = ohrc_f.shape
    ys = np.linspace(0.12, 0.88, n_windows) * rows              # the frozen cut's window rule
    cx, cy = ohrc_f.to_map(np.full(n_windows, cols / 2.0), ys)
    o_sun, t_sun = o_info["sun"], info_t["sun"]
    d_az = round(abs((t_sun["azimuth_deg_label"] - o_sun["azimuth_deg_label"] + 180) % 360 - 180), 1)
    d_inc = round((90 - t_sun["elevation_deg_label"]) - (90 - o_sun["elevation_deg_label"]), 2)
    stem = f"chain_ohrclroc_tmc{tmc_pid[12:20]}"
    out = []
    for k, (x, y) in enumerate(zip(cx, cy), 1):
        pair_id = f"{stem}_w{k:02d}"
        x0, y1 = x - window_m / 2, y + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
        r_img, r_ok = G.project(tmc_f, read_t, tr_r, sh_r, coarse=16, order="cubic")
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(ohrc_f, o_read, tr_s, sh_s, coarse=16, order="cubic")
        if r_ok.mean() < 0.998 or s_ok.mean() < 0.998:
            print(f"  {pair_id}: window not covered (ref {r_ok.mean():.4f}, src {s_ok.mean():.4f}) - skipped")
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
        lat, lon = proj.inv(x, y)
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": "B (cross-sensor real, ohrc-tmc2)",
            "terminology": "cross-sensor (Chandrayaan-2 OHRC vs TMC-2), same mission - NOT cross-mission; both "
                           "panchromatic, so NOT multi-modal",
            "crs": proj.name,
            "window_centre_map_m": [float(x), float(y)], "window_centre_latlon": [float(lat), float(lon)],
            "window_m": window_m, "window_rule": "as the frozen ohrc-tmc cut: evenly along the OHRC centre line",
            "ohrc_shift_into_lroc_m": [round(sx, 1), round(sy, 1)],
            "source": {**o_info, "resampled_gsd_mpp": src_gsd, "shape": list(sh_s), "transform": list(tr_s)},
            "reference": {**info_t, "resampled_gsd_mpp": ref_gsd, "shape": list(sh_r), "transform": list(tr_r)},
            "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc,
            "sun_note": "scene-level label values (isda:sun_azimuth / sun_elevation), not at the window",
            "scale_ratio": round(ref_gsd / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / ref_gsd, 0, 0], [0, src_gsd / ref_gsd, 0], [0, 0, 1]],
            "prior_note": "OHRC moved into LROC's geometry first (ohrc_shift_into_lroc_m); any offset the pipeline "
                          "finds is the disagreement between that and the TMC-2 archive grid",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.cut_chain_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: centre ({lat:.4f}, {lon:.4f}); OHRC shifted ({sx:+.0f}, {sy:+.0f}) m; src {sh_s} "
              f"@ {src_gsd} m, ref {sh_r} @ {ref_gsd} m; d_az {d_az} deg, d_inc {d_inc} deg")
    return out


# --- OHRC -> LRO NAC on SAC's frame with the Sun's ELEVATION moved: the elevation ladder ----------

LADDER_GSD = 1.75   # m: the coarsest NAC on the ladder (M1382142111LE), so no NAC is ever upsampled
LADDER_STEP = 1.25  # candidate window centres every 1.25 windows along the OHRC frame's centre line


def _block_reader(read, f):
    """`read` area-averaged f x f, as cut_pradan_pairs.product does for the OHRC (f = 1: unchanged)."""
    if f == 1:
        return read

    def r(x, y, w, h):
        a = read(x * f, y * f, w * f, h * f)
        hh, ww = a.shape[0] // f, a.shape[1] // f
        return a[:hh * f, :ww * f].reshape(hh, f, ww, f).mean(axis=(1, 3))
    return r


def _edr_url_from_manifest(pid):
    """The NAC's PDS URL as recorded in <data>/nac_sac_manifest.csv (the downloader's own list)."""
    import csv
    p = DATA / "nac_sac_manifest.csv"
    if p.exists():
        for row in csv.DictReader(open(p, encoding="utf-8")):
            if row["id"].upper() == pid.upper():
                return row["url"]
    return None


def ladder_candidates(ohrc_f, window_m, step=LADDER_STEP):
    """Window centres (map x, y) on the OHRC frame's centre line, `step` windows apart, clear of its
    ends. Fixed by the OHRC frame alone, so every rung of the ladder is offered the same ground."""
    rows, cols = ohrc_f.shape
    ends = ohrc_f.to_map(np.array([cols / 2.0, cols / 2.0]), np.array([0.0, rows - 1.0]))
    length = float(np.hypot(ends[0][1] - ends[0][0], ends[1][1] - ends[1][0]))
    margin = (window_m / 2 + 50.0) / length
    n = max(1, int((length * (1 - 2 * margin)) // (step * window_m)) + 1)
    fr = np.linspace(margin, 1 - margin, n)
    return np.array(ohrc_f.to_map(np.full(n, cols / 2.0), fr * (rows - 1))).T


def cut_ohrc_nac_lro(nac_pid, edr_url=None, n_windows=8, ref_px=640):
    """SAC's OHRC frame (source) -> one LRO NAC (reference), BOTH placed in LRO's geometry, on one
    common reference grid: a rung of the Sun-elevation ladder.

    WHY. The PS names Sun azimuth AND elevation. The frozen evidence moves the azimuth (SAC's pair,
    174 deg) but the real sweep at 74 S spans only 0-10 deg of incidence difference. On SAC's own
    equatorial frame, LROC NACs exist whose Sun azimuth is within 2-19 deg of the OHRC's (271 deg,
    10 deg up) while the elevation runs from 8 to 52 deg (WUSTL ODE footprints; Sun from DE421 at
    the frame centre, 1 Oct 2026 scout). Each NAC is one rung: same OHRC, same candidate windows,
    same reference grid, only the Sun's elevation (and, on the top rungs, up to 19 deg of azimuth)
    changes.

    THE PRIOR USES NO IMAGE CONTENT OF THE PAIR. The OHRC is moved into LRO's geometry by
    `ohrc_to_lroc_shift` (SAC's NAC correction, frozen 19 Sep); each rung's NAC is placed by LROC's
    published corners alone (precise to ~0.01 deg, so a few hundred metres - inside a 1.1 km
    window). A wide search against the OHRC would fail exactly where the ladder is meant to measure
    failure (M1447829089LE, 28 Sep), so it is not used.

    ONE GRID. Every rung's reference is resampled to LADDER_GSD (1.75 m) after an integer f x f
    area average (f = round(1.75 / NAC resolution)), so a 0.74 m NAC is not compared at a finer
    scale than a 1.75 m one. The OHRC is area-averaged 4x4 (~1.1 m), as in the OHRC -> TMC-2 cut.

    WINDOWS. `ladder_candidates`: centres every LADDER_STEP windows along the OHRC centre line;
    each rung uses those its NAC covers (>= 99.8 % of the window in both images), up to `n_windows`
    spread evenly. No matching is involved in placing them."""
    from core import geometry as G
    from ops import cut_pradan_pairs as CP
    from ops import cut_site_pairs as S
    import tifffile
    edr_url = edr_url or _edr_url_from_manifest(nac_pid)
    if not edr_url:
        raise SystemExit(f"{nac_pid}: no --edr-url and not in {DATA / 'nac_sac_manifest.csv'}")
    nac_page(nac_pid, edr_url)
    if not (DATA / "nac" / f"{nac_pid}.IMG").exists():
        raise SystemExit(f"{nac_pid}.IMG not in {DATA / 'nac'} - download {edr_url}")
    proj = LocalEqc(*CP._frame_centre_latlon(CP.PRODUCTS["ohrc"][1]))
    ohrc_f, o_read, o_info = CP.product("ohrc", proj)          # area-averaged 4x4
    sx, sy = ohrc_to_lroc_shift(proj, ohrc_f)
    ohrc_f = ohrc_f.shifted(sx, sy, note=f"(into LROC's geometry via {SAC_NAC}'s saved correction)")
    o_info["geometry"] = ohrc_f.source
    nac_f, n_read, n_info = CP.nac_product(nac_pid, proj)
    f = max(1, int(round(LADDER_GSD / float(n_info["resolution_mpp"]))))
    nac_f, n_read = (S._decimated(nac_f, f), _block_reader(n_read, f)) if f > 1 else (nac_f, n_read)
    n_info["coarse_prior"] = {"model": "none: LROC's published corners, uncorrected (see docstring)"}
    n_info["geometry"] = nac_f.source + (f"; area-averaged {f}x{f} before projection" if f > 1 else "")
    n_info["block_factor"] = f
    ref_gsd, src_gsd = LADDER_GSD, round(float(np.mean(ohrc_f.gsd())), 3)
    window_m = ref_px * ref_gsd
    cands = ladder_candidates(ohrc_f, window_m)
    covered = []
    for k, (x, y) in enumerate(cands):
        x0, y1 = x - window_m / 2, y + window_m / 2
        tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
        r_img, r_ok = G.project(nac_f, n_read, tr_r, sh_r, coarse=16, order="cubic")
        if r_ok.mean() < 0.998:
            continue
        s_px = int(round(window_m / src_gsd))
        tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
        s_img, s_ok = G.project(ohrc_f, o_read, tr_s, sh_s, coarse=32, order="cubic")
        if s_ok.mean() < 0.998:
            continue
        covered.append((k, x, y, (r_img, r_ok, tr_r, sh_r), (s_img, s_ok, tr_s, sh_s)))
    print(f"  {nac_pid}: {len(covered)} of {len(cands)} candidate windows covered by both images")
    if not covered:
        raise SystemExit(f"{nac_pid}: no candidate window is covered by both images")
    keep = sorted({int(round(v)) for v in np.linspace(0, len(covered) - 1, min(n_windows, len(covered)))})
    o_sun = o_info["sun"]
    ss_lat, ss_lon = n_info["subsolar"]
    stem = f"sac_ohrclroc_nac{nac_pid.lower()}"
    out = []
    for j in keep:
        k, x, y, (r_img, r_ok, tr_r, sh_r), (s_img, s_ok, tr_s, sh_s) = covered[j]
        pair_id = f"{stem}_c{k:02d}"      # the candidate's own index: rungs share window ids
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
        tifffile.imwrite(str(src_p), s_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_s))
        tifffile.imwrite(str(ref_p), r_img.astype(np.float32), photometric="minisblack",
                         extratags=proj.geotiff_tags(tr_r))
        meta = {
            "pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": "B (cross-sensor real, ohrc-nac, Sun ladder on SAC's frame)",
            "terminology": "cross-sensor, cross-mission (Chandrayaan-2 OHRC vs LRO LROC NAC); both panchromatic "
                           "visible, so NOT multi-modal; "
                           + ("an OPPOSITE-Sun rung: NAC chosen for a Sun azimuth opposite the OHRC's, at a chosen "
                              "elevation" if d_az > 90 else
                              "a Sun-ELEVATION rung: NAC chosen for a Sun azimuth near the OHRC's"),
            "crs": proj.name,
            "window_centre_map_m": [float(x), float(y)], "window_centre_latlon": [float(lat), float(lon)],
            "window_m": window_m, "candidate_index": int(k),
            "window_rule": f"pre-registered: candidate centres every {LADDER_STEP} windows along SAC's OHRC frame "
                           "centre line (ladder_candidates); each rung uses those its NAC covers, up to "
                           f"{n_windows} evenly spread - no image content and no matching involved",
            "ohrc_shift_into_lroc_m": [round(sx, 1), round(sy, 1)],
            "source": {**o_info, "resampled_gsd_mpp": src_gsd, "shape": list(sh_s), "transform": list(tr_s)},
            "reference": {**n_info, "resampled_gsd_mpp": ref_gsd, "shape": list(sh_r), "transform": list(tr_r),
                          "incidence_deg_at_site": round(n_inc, 2), "sun_azimuth_deg_from_north": round(n_az, 1),
                          "sun_elevation_deg_at_site": round(90.0 - n_inc, 2)},
            "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc,
            "sun_note": "OHRC: scene-level label (isda:sun_azimuth / sun_elevation); NAC: computed at the window "
                        "from LROC's published sub-solar point (core.geometry.sun_direction)",
            "scale_ratio": round(ref_gsd / src_gsd, 3),
            "prior_H_source_to_reference": [[src_gsd / ref_gsd, 0, 0], [0, src_gsd / ref_gsd, 0], [0, 0, 1]],
            "prior_note": "both images placed in LRO's geometry with no image content of this pair: the OHRC by "
                          "SAC's NAC correction (ohrc_shift_into_lroc_m), the NAC by LROC's published corners; any "
                          "offset the pipeline finds is the disagreement between those two placements",
            "benchmark": "SAC's own OHRC frame, arXiv:2509.04775 Table 1",
            "edge_pixels_filled": {"source": s_fill, "reference": r_fill},
            "files": {q.name: _sha(q) for q in (src_p, ref_p)},
            "command": "python -m ops.cut_chain_pairs " + " ".join(sys.argv[1:]),
        }
        (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        out.append(d)
        print(f"  {pair_id}: centre ({lat:.4f}, {lon:.4f}); NAC Sun el {90 - n_inc:.1f} az {n_az:.1f}; "
              f"d_az {d_az} deg, d_inc {d_inc} deg; src {sh_s} @ {src_gsd} m, ref {sh_r} @ {ref_gsd} m (f={f})")
    return out


# --- Site N (60.7 N, 4.6 W): OHRC, TMC-2, IIRS and an LRO NAC under matched Suns --------------
#
# Found 1 Oct 2026 in PRADAN's footprint catalogue and WUSTL ODE (Sun from DE421 at the OHRC frame
# centre): OHRC ch2_ohr_ncp_20250612T2031048828 (Sun 29 deg up, azimuth 200 deg); TMC-2
# ch2_tmc_ncn_20200607T2239162106 covering all of it with the Sun 1.9 deg away; the IIRS strip of
# that same orbit (0.8 s apart); LROC NAC M1282456834RE over 64 % of it with the Sun 5.2 deg away.
# Three legs share one set of window centres, so OHRC -> NAC -> TMC-2 can be closed against
# OHRC -> TMC-2 (ops.loop_closure --legs).

def ohrc_key(pid):
    """Register any calibrated OHRC product with cut_pradan_pairs.PRODUCTS (ops.fetch_pradan unpacks
    the zip to <data>/pradan/ohrc/{data,geometry}/calibrated/<yyyymmdd>/) and return its key."""
    from ops import cut_pradan_pairs as CP
    if pid == CP.OHRC_ID:
        return "ohrc"
    day = pid[12:20]
    key = f"ohrc_{pid[12:27]}"
    xml = CP.P / "ohrc/data/calibrated" / day / f"{pid}.xml"
    grid = CP.P / "ohrc/geometry/calibrated" / day / f"{pid.replace('_d_img_', '_g_grd_')}.csv"
    if not (xml.exists() and grid.exists()):
        raise SystemExit(f"{pid}: {xml.name} or its _g_grd_ csv not on disk - python -m ops.fetch_pradan {pid}")
    CP.PRODUCTS[key] = (xml, grid, "Chandrayaan-2 OHRC")
    return key


def site_frame(ohrc_pid, anchor_nac, refit=False, proj=None):
    """(key, proj, OHRC 4x4 frame in LRO's geometry, reader, info, shift, anchor prior).

    The map is a local equirectangular grid centred on the OHRC frame (or `proj`, to put a second
    OHRC frame of the same site on the first one's map). The OHRC archive grid can sit
    kilometres from LRO's (1.9 km at SAC's frame, 28 Sep), so it is moved into LRO's geometry by the
    correction `anchor_nac` carries against it - fitted here once if absent (ops.cut_pradan_pairs.
    nac_corrected: wide template search, then the 4 m box field; both intensity polarities) and saved
    to <data>/site_geometry/<anchor_nac>.json. That uses the OHRC and the NAC, never a TMC-2 pixel,
    so the OHRC -> TMC-2 prior holds no image content of the pair it serves."""
    from ops import cut_pradan_pairs as CP
    from ops import cut_site_pairs as S
    key = ohrc_key(ohrc_pid)
    proj = proj or LocalEqc(*CP._frame_centre_latlon(CP.PRODUCTS[key][1]))
    gp = S.GEOM_DIR / f"{anchor_nac}.json"
    stale = (not gp.exists() or json.loads(gp.read_text(encoding="utf-8")).get("against")
             != CP.PRODUCTS[key][0].stem)
    if refit or stale:
        url = _edr_url_from_manifest(anchor_nac)
        if not url:
            raise SystemExit(f"{anchor_nac} is not in {DATA / 'nac_sac_manifest.csv'}")
        nac_page(anchor_nac, url)
        native, n_read, _ = CP.product(key, proj, block=1)
        CP.nac_corrected(anchor_nac, key, proj, native, n_read, refit=True)
    prior = json.loads(gp.read_text(encoding="utf-8"))
    if not (prior.get("apply") or (prior.get("wide_offset") or {}).get("apply")):
        raise SystemExit(f"{anchor_nac}: no trustworthy correction against {ohrc_pid} - the OHRC cannot be "
                         "placed in LRO's geometry this way")
    ohrc_f, o_read, o_info = CP.product(key, proj)                # area-averaged 4x4
    sx, sy = ohrc_to_lroc_shift(proj, ohrc_f, anchor_nac)
    ohrc_f = ohrc_f.shifted(sx, sy, note=f"(into LROC's geometry via {anchor_nac}'s correction against it)")
    o_info["geometry"] = ohrc_f.source
    return key, proj, ohrc_f, o_read, o_info, (sx, sy), prior


def spm_sun(xml, line):
    """(Sun azimuth, Sun elevation) in degrees at one image LINE of a Chandrayaan-2 OHRC or TMC-2
    product, from its own Sun-parameter file (miscellaneous/calibrated/<day>/<pid>.spm, shipped in
    the PRADAN zip): ORBTATTD records of time, spacecraft position and velocity, then solar
    incidence, -, Sun azimuth, Sun elevation at the sub-spacecraft point. The line's time is placed
    between the label's start and stop times; the nearest record is used.

    WHY. A TMC-2 label carries ONE Sun, at the strip centre (Known issue 33): on Site N's pass the
    strip runs from 61.6 N to 29.4 N and the label says 41.8 deg up, while at 60.7 N, where the OHRC
    frame is, the Sun is ~27 deg up. Quoting the label there would call a matched Sun 13 deg off."""
    f = _nearest_record(xml, line, ".spm", 19)
    return None if f is None else (float(f[17]), float(f[18]))


def _nearest_record(xml, line, suffix, min_fields):
    """The ORBTATTD record of <pid><suffix> (miscellaneous/calibrated/<day>/, beside the label's
    data/calibrated/<day>/) nearest in time to one image LINE, as a list of fields; None if absent.
    The line's time is placed linearly between the label's start and stop times."""
    import datetime as dt
    xml = pathlib.Path(xml)
    p = pathlib.Path(str(xml).replace("\\data\\", "\\miscellaneous\\")
                     .replace("/data/", "/miscellaneous/")).with_suffix(suffix)
    if not p.exists():
        return None
    text = xml.read_text(encoding="latin1")
    t0, t1 = (dt.datetime.fromisoformat(re.search(rf"<{k}_date_time>([^<]+)<", text).group(1).replace("Z", ""))
              for k in ("start", "stop"))
    n = int(re.findall(r"<elements>(\d+)<", text)[0])
    t = t0 + (t1 - t0) * (max(0.0, min(float(line), n - 1.0)) / max(n - 1, 1))
    best = None
    for ln in p.read_text(encoding="latin1").splitlines():
        f = ln.split()
        if len(f) < min_fields or f[0] != "ORBTATTD":
            continue
        tr = (dt.datetime(int(f[2][-4:]), int(f[3]), int(f[4]), int(f[5]), int(f[6]), int(f[7]))
              + dt.timedelta(milliseconds=int(f[8])))
        d = abs((tr - t).total_seconds())
        if best is None or d < best[0]:
            best = (d, f)
    return None if best is None else best[1]


MOON_R_KM = 1737.4


def _unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def oat_view(xml, line, lat, lon):
    """The direction from ground point (lat, lon) to the spacecraft when it imaged one LINE of a
    Chandrayaan-2 OHRC or TMC-2 product: (emission angle from the local vertical, azimuth of the
    spacecraft from north, unit vector in Moon-fixed axes), from its orbit-attitude file <pid>.oat.
    Each ORBTATTD record ends with: sub-spacecraft latitude and longitude, Sun azimuth and elevation,
    boresight latitude and longitude, eight scalars of which the 6th is the altitude in km, then
    yaw, roll, pitch. The spacecraft is put at that altitude over that point on a sphere of the
    Moon's mean radius. Geometry only - no attitude field is used."""
    f = _nearest_record(xml, line, ".oat", 40)
    if f is None:
        return None
    s_lat, s_lon, alt = float(f[-17]), float(f[-16]), float(f[-6])
    g = MOON_R_KM * _unit(lat, lon)
    v = (MOON_R_KM + alt) * _unit(s_lat, s_lon) - g
    v /= np.linalg.norm(v)
    up = _unit(lat, lon)
    east = np.array([-np.sin(np.radians(lon)), np.cos(np.radians(lon)), 0.0])
    north = np.cross(up, east)
    emission = float(np.degrees(np.arccos(np.clip(v @ up, -1, 1))))
    az = float(np.degrees(np.arctan2(v @ east, v @ north)) % 360)
    return emission, az, v


def _site_write(pair_id, proj, x, y, window_m, r, s, meta):
    """Write one pair (both GeoTIFFs and geometry_prior.json) and return its folder."""
    from core import geometry as G
    import tifffile
    r_img, r_ok, tr_r, sh_r = r
    s_img, s_ok, tr_s, sh_s = s
    r_img, r_fill = G.fill_invalid(r_img, r_ok)
    s_img, s_fill = G.fill_invalid(s_img, s_ok)
    d = PAIRS / pair_id
    d.mkdir(parents=True, exist_ok=True)
    src_p, ref_p = d / f"{pair_id}_source.tif", d / f"{pair_id}_ref.tif"
    tifffile.imwrite(str(src_p), s_img.astype(np.float32), photometric="minisblack", extratags=proj.geotiff_tags(tr_s))
    tifffile.imwrite(str(ref_p), r_img.astype(np.float32), photometric="minisblack", extratags=proj.geotiff_tags(tr_r))
    lat, lon = proj.inv(x, y)
    meta = {"pair_id": pair_id,
            "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "crs": proj.name, "window_centre_map_m": [float(x), float(y)],
            "window_centre_latlon": [float(lat), float(lon)], "window_m": window_m, **meta}
    meta["source"] = {**meta["source"], "shape": list(sh_s), "transform": list(tr_s)}
    meta["reference"] = {**meta["reference"], "shape": list(sh_r), "transform": list(tr_r)}
    meta.update(edge_pixels_filled={"source": s_fill, "reference": r_fill},
                files={q.name: _sha(q) for q in (src_p, ref_p)},
                command="python -m ops.cut_chain_pairs " + " ".join(sys.argv[1:]))
    (d / "geometry_prior.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return d


def _project_pair(ref_f, ref_read, ref_gsd, src_f, src_read, src_gsd, x, y, window_m):
    """Both images onto the window's map grid; None unless >= 99.8 % of each is covered."""
    from core import geometry as G
    x0, y1 = x - window_m / 2, y + window_m / 2
    tr_r, sh_r = G.map_grid(x0, y1, window_m, window_m, ref_gsd)
    r_img, r_ok = G.project(ref_f, ref_read, tr_r, sh_r, coarse=16, order="cubic")
    if r_ok.mean() < 0.998:
        return None
    s_px = int(round(window_m / src_gsd))
    tr_s, sh_s = G.map_grid(x0, y1, s_px * src_gsd, s_px * src_gsd, src_gsd)
    s_img, s_ok = G.project(src_f, src_read, tr_s, sh_s, coarse=32, order="cubic")
    if s_ok.mean() < 0.998:
        return None
    return (r_img, r_ok, tr_r, sh_r), (s_img, s_ok, tr_s, sh_s)


SITE_TMC_PX = 384   # TMC-2 reference windows (~1.7-2.2 km); candidates are spaced on this window


def cut_site(ohrc_pid, tmc_pid, nac_pid, legs=("ohrc-tmc", "ohrc-nac", "nac-tmc"), anchor_nac=None,
             n_windows=8, refit=False):
    """Site N's three legs on ONE set of window centres (ladder_candidates on the OHRC frame's centre
    line, spaced on the TMC-2 window), each leg keeping the centres its two images both cover:
      ohrc-tmc  OHRC (4x4, in LRO's geometry) -> TMC-2 nadir: cross-sensor, same mission
      ohrc-nac  OHRC (4x4, in LRO's geometry) -> LRO NAC by its LROC corners: cross-sensor, cross-mission
      nac-tmc   LRO NAC by its LROC corners -> TMC-2 nadir: cross-sensor, cross-mission
    Pair ids end in _c<candidate index>, so the legs of one ground window share it (the loop needs
    that). The OHRC's move into LRO's geometry comes from `anchor_nac` (default: `nac_pid`) against
    the OHRC; on the ohrc-nac leg of that same NAC the prior is therefore partly from the pair itself
    (a 4 m fit), which the pair's prior_note says."""
    from core import geometry as G
    from ops import cut_pradan_pairs as CP
    anchor_nac = anchor_nac or nac_pid
    key, proj, ohrc_f, o_read, o_info, (sx, sy), aprior = site_frame(ohrc_pid, anchor_nac, refit)
    xml_t, grid_t, read_t, shape_t, info_t = tmc_product(tmc_pid)
    tmc_f = frame_from_grid(grid_t, shape_t, proj, "TMC-2 nadir")
    info_t["geometry"] = tmc_f.source
    tmc_gsd = round(float(np.mean(tmc_f.gsd())), 3)
    o_gsd = round(float(np.mean(ohrc_f.gsd())), 3)
    cands = ladder_candidates(ohrc_f, SITE_TMC_PX * tmc_gsd)
    nac_f = n_read = n_info = None
    if any(lg in legs for lg in ("ohrc-nac", "nac-tmc")):
        url = _edr_url_from_manifest(nac_pid)
        nac_page(nac_pid, url)
        nac_f, n_read, n_info = CP.nac_product(nac_pid, proj)
        n_info["coarse_prior"] = {"model": "none: LROC's published corners, uncorrected"}
        n_info["geometry"] = nac_f.source
        nac_gsd = round(float(np.mean(nac_f.gsd())), 3)
    o_sun, t_sun = o_info["sun"], info_t["sun"]
    hhmm = ohrc_pid[21:25]
    shift_note = (f"OHRC moved ({sx:+.0f}, {sy:+.0f}) m into LRO's geometry by {anchor_nac}'s 4 m correction "
                  "against it (site_frame)")
    out = []
    for leg in legs:
        if leg == "ohrc-tmc":
            stem, ref, src = f"siten_ohrc{hhmm}_tmc{tmc_pid[12:20]}", (tmc_f, read_t, tmc_gsd), (ohrc_f, o_read, o_gsd)
            window_m = SITE_TMC_PX * tmc_gsd
            tier, term = _tier_chain("ohrc-tmc")
            prior_note = shift_note + "; TMC-2 on its archive grid - no TMC-2 pixel in the prior"
        elif leg == "ohrc-nac":
            stem, ref, src = f"siten_ohrc{hhmm}_nac{nac_pid.lower()}", (nac_f, n_read, nac_gsd), (ohrc_f, o_read, o_gsd)
            window_m = 640 * nac_gsd
            tier, term = _tier_chain("ohrc-nac")
            prior_note = shift_note + f"; NAC by LROC's corners" + (
                f" - the OHRC's move was fitted against THIS NAC at 4 m, so this leg's prior is partly from the "
                "pair itself" if nac_pid == anchor_nac else "")
        elif leg == "nac-tmc":
            stem, ref, src = f"siten_nac{nac_pid.lower()}_tmc{tmc_pid[12:20]}", (tmc_f, read_t, tmc_gsd), (nac_f, n_read, nac_gsd)
            window_m = SITE_TMC_PX * tmc_gsd
            tier, term = _tier_chain("nac-tmc")
            prior_note = "NAC by LROC's corners, TMC-2 on its archive grid: no image content in the prior"
        else:
            raise SystemExit(f"unknown leg {leg}")
        made = []
        for k, (x, y) in enumerate(cands):
            pr = _project_pair(*ref, *src, x, y, window_m)
            if pr is None:
                continue
            lat, lon = proj.inv(x, y)
            # The Sun AT THE WINDOW for every image: OHRC and TMC-2 from their own .spm at the window's
            # line (spm_sun), the NAC from LROC's sub-solar point. Labels only as a fallback.
            suns = {}
            for name, fr, xml_, lab in (("ohrc", ohrc_f, CP.PRODUCTS[key][0], o_sun), ("tmc2", tmc_f, xml_t, t_sun)):
                _, ln = fr.from_map(np.array([x]), np.array([y]))
                scale = 4 if name == "ohrc" else 1            # the OHRC frame is area-averaged 4x4
                v = spm_sun(xml_, float(ln[0]) * scale) if np.isfinite(ln[0]) else None
                suns[name] = (v, ".spm at the window's line") if v else (
                    (lab["azimuth_deg_label"], lab["elevation_deg_label"]), "scene-level label")
            if nac_f is not None:
                n_inc, n_az = G.sun_direction(float(lat), float(lon), *n_info["subsolar"])
                suns["nac"] = ((n_az, 90.0 - n_inc), "LROC sub-solar point at the window")
            s_name, r_name = {"ohrc-tmc": ("ohrc", "tmc2"), "ohrc-nac": ("ohrc", "nac"), "nac-tmc": ("nac", "tmc2")}[leg]
            (s_az, s_el), s_how = suns[s_name]
            (r_az, r_el), r_how = suns[r_name]
            # d_incidence = reference incidence - source incidence, as in every other cut
            d_az = round(abs((r_az - s_az + 180) % 360 - 180), 1)
            d_inc = round((90.0 - r_el) - (90.0 - s_el), 2)
            sun_note = f"Sun at the window: {s_name} from its {s_how}, {r_name} from its {r_how}"
            meta = {"tier": tier, "terminology": term, "candidate_index": int(k), "site": "N (60.7 N, 4.6 W)",
                    "window_rule": "pre-registered: centres every 1.25 TMC-2 windows along the OHRC frame's centre "
                                   "line (ladder_candidates), the same for all three legs - no matching involved",
                    "source": {**(o_info if leg != "nac-tmc" else n_info), "resampled_gsd_mpp": src[2]},
                    "reference": {**(info_t if leg != "ohrc-nac" else n_info), "resampled_gsd_mpp": ref[2]},
                    "d_sun_azimuth_deg": d_az, "d_incidence_deg": d_inc, "sun_note": sun_note,
                    "scale_ratio": round(ref[2] / src[2], 3),
                    "prior_H_source_to_reference": [[src[2] / ref[2], 0, 0], [0, src[2] / ref[2], 0], [0, 0, 1]],
                    "prior_note": prior_note, "ohrc_shift_into_lroc_m": [round(sx, 1), round(sy, 1)],
                    "sun_at_window_az_el": {k: [round(v[0][0], 2), round(v[0][1], 2), v[1]] for k, v in suns.items()}}
            made.append(_site_write(f"{stem}_c{k:02d}", proj, x, y, window_m, pr[0], pr[1], meta))
            if len(made) >= n_windows:
                break
        print(f"  {leg}: {len(made)} pair(s) ({stem}_c..), {len(cands)} candidate centres")
        out += made
    return out


VIEW_PX = 640       # OHRC windows (4x4 frame, ~1.2 m) for the viewpoint pair: ~790 m on the ground
VIEW_EVERY = 3      # every third candidate centre along the frame, so 8 windows span its length


@contextlib.contextmanager
def _geometry_dir(sub):
    """Put NAC corrections in <data>/site_geometry/<sub>/ for the duration. A NAC's correction is
    saved per NAC and names the OHRC it was fitted against; fitting the same NAC against a SECOND
    OHRC frame must not overwrite the one the first frame's pairs were cut with."""
    from ops import cut_site_pairs as S
    base = S.GEOM_DIR
    S.GEOM_DIR = base / sub
    try:
        yield S.GEOM_DIR
    finally:
        S.GEOM_DIR = base


def cut_viewpoint(a_pid, b_pid, anchor_nac, n_windows=8, every=VIEW_EVERY, refit=False):
    """A REAL viewpoint test: two OHRC frames of one site, taken two hours apart on consecutive
    orbits, one looking forward and one looking back. Same instrument (Tier A, NOT cross-sensor),
    the Sun within ~2 deg, the viewing direction ~39 deg apart and from opposite sides of the site.

    Both frames are put in LRO's geometry the same way, each by `anchor_nac`'s 4 m correction against
    it (site_frame; b's correction kept in its own folder), so neither image of the pair is fitted
    against the other and no pixel of the pair is matched to build the prior. Both are resampled to
    one map grid at the coarser frame's spacing. Windows: every `every`-th centre along frame a's
    centre line (ladder_candidates), fixed before matching. Each image is placed by its own pointing
    on a sphere, so what is left between the two is relief parallax and how slopes look from each side.
    Reference = b, source = a. Per window the pair records both Suns (spm_sun) and both viewing
    directions (oat_view) at the window's line, and the angle between the two viewing directions."""
    from ops import cut_pradan_pairs as CP
    ka, proj, fa, ra, ia, (sxa, sya), _ = site_frame(a_pid, anchor_nac)
    kb = ohrc_key(b_pid)
    with _geometry_dir(f"against_{kb}"):
        _, _, fb, rb, ib, (sxb, syb), _ = site_frame(b_pid, anchor_nac, refit, proj=proj)
    gsd = round(float(max(np.mean(fa.gsd()), np.mean(fb.gsd()))), 3)
    window_m = VIEW_PX * gsd
    cands = ladder_candidates(fa, window_m)
    stem = f"siten_ohrc{a_pid[21:25]}_ohrc{b_pid[21:25]}"
    term = ("same instrument (Chandrayaan-2 OHRC vs OHRC, consecutive orbits, Sun within ~2 deg): a VIEWPOINT "
            "test, NOT cross-sensor")
    made = []
    for k, (x, y) in enumerate(cands):
        if k % every:
            continue
        pr = _project_pair(fb, rb, gsd, fa, ra, gsd, x, y, window_m)
        if pr is None:
            continue
        lat, lon = proj.inv(x, y)
        at = {}
        for name, fr, xml_ in (("a", fa, CP.PRODUCTS[ka][0]), ("b", fb, CP.PRODUCTS[kb][0])):
            _, ln = fr.from_map(np.array([x]), np.array([y]))
            line = float(ln[0]) * 4                              # the frames are area-averaged 4x4
            at[name] = (spm_sun(xml_, line), oat_view(xml_, line, float(lat), float(lon)))
        (sa, va), (sb, vb) = at["a"], at["b"]
        sep = float(np.degrees(np.arccos(np.clip(va[2] @ vb[2], -1, 1))))
        meta = {"tier": "A (same sensor, viewpoint, real)", "terminology": term, "candidate_index": int(k),
                "site": "N (60.7 N, 4.6 W)",
                "window_rule": f"pre-registered: one in every {every} centres of ladder_candidates along frame a's "
                               "centre line - no matching involved",
                "source": {**ia, "resampled_gsd_mpp": gsd}, "reference": {**ib, "resampled_gsd_mpp": gsd},
                "d_sun_azimuth_deg": round(abs((sb[0] - sa[0] + 180) % 360 - 180), 2),
                "d_incidence_deg": round((90.0 - sb[1]) - (90.0 - sa[1]), 2),
                "sun_note": "Sun at the window from each frame's own .spm at the window's line",
                "view_at_window": {"a": {"emission_deg": round(va[0], 2), "spacecraft_azimuth_deg": round(va[1], 1)},
                                   "b": {"emission_deg": round(vb[0], 2), "spacecraft_azimuth_deg": round(vb[1], 1)},
                                   "angle_between_deg": round(sep, 2),
                                   "how": "oat_view: sub-spacecraft point and altitude from each frame's .oat"},
                "scale_ratio": 1.0, "prior_H_source_to_reference": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                "prior_note": (f"both frames moved into LRO's geometry by {anchor_nac}'s 4 m correction against "
                               f"each (a: ({sxa:+.0f}, {sya:+.0f}) m, b: ({sxb:+.0f}, {syb:+.0f}) m); neither "
                               "frame fitted against the other"),
                "ohrc_shift_into_lroc_m": {"a": [round(sxa, 1), round(sya, 1)], "b": [round(sxb, 1), round(syb, 1)]}}
        made.append(_site_write(f"{stem}_c{k:02d}", proj, x, y, window_m, pr[0], pr[1], meta))
        print(f"  {stem}_c{k:02d}: views {va[0]:.1f} deg from az {va[1]:.0f} and {vb[0]:.1f} deg from az "
              f"{vb[1]:.0f}, {sep:.1f} deg apart; Sun {sa[1]:.1f} / {sb[1]:.1f} deg up")
        if len(made) >= n_windows:
            break
    print(f"  viewpoint: {len(made)} pair(s) ({stem}_c..), {len(cands)} candidate centres")
    return made


def _tier_chain(leg):
    return {"ohrc-tmc": ("B (cross-sensor real, ohrc-tmc2, Sun matched)",
                         "cross-sensor (Chandrayaan-2 OHRC vs TMC-2), same mission - NOT cross-mission; both "
                         "panchromatic, so NOT multi-modal; the Sun matched (a different orbit and year)"),
            "ohrc-nac": ("B (cross-sensor real, ohrc-nac, Sun matched)",
                         "cross-sensor, cross-mission (Chandrayaan-2 OHRC vs LRO LROC NAC); both panchromatic, "
                         "so NOT multi-modal"),
            "nac-tmc": ("B (cross-sensor real, nac-tmc2, Sun matched)",
                        "cross-sensor, cross-mission (LRO LROC NAC vs Chandrayaan-2 TMC-2 nadir); both "
                        "panchromatic, so NOT multi-modal")}[leg]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=("tmc-iirs", "nac-tmc", "ohrc-tmc", "ohrc-nac-lro", "site", "viewpoint"))
    ap.add_argument("--ohrc", help="site, viewpoint: the OHRC product id (viewpoint: the source frame, a)")
    ap.add_argument("--ohrc-b", help="viewpoint: the second OHRC frame of the same site (the reference, b)")
    ap.add_argument("--legs", nargs="*", default=["ohrc-tmc", "ohrc-nac", "nac-tmc"],
                    help="site: which legs to cut (ohrc-tmc, ohrc-nac, nac-tmc)")
    ap.add_argument("--anchor-nac", help="site, viewpoint: the NAC whose correction against the OHRC places the OHRC in "
                                         "LRO's geometry (default: --nac)")
    ap.add_argument("--tmc", help="calibrated TMC-2 nadir product id (all kinds but ohrc-nac-lro)")
    ap.add_argument("--iirs", help="tmc-iirs: calibrated IIRS product id (same orbit)")
    ap.add_argument("--band", type=int, help="tmc-iirs: IIRS band, 1-based as in its label")
    ap.add_argument("--nac", help="nac-tmc: LRO NAC product id, e.g. M1258792259LE")
    ap.add_argument("--edr-url", help="nac-tmc: the NAC EDR's PDS URL (recorded in the pair)")
    ap.add_argument("--windows", type=int, help="default 8 (tmc-iirs) or 6 (nac-tmc)")
    ap.add_argument("--ref-px", type=int, help="default 192 IIRS px (24-px trust cells) or 384 TMC-2 px")
    ap.add_argument("--lat", type=float, nargs=2, default=(-60.0, 60.0))
    ap.add_argument("--step-km", type=float, default=15.0)
    ap.add_argument("--same-as", type=int, help="reuse the windows of this band's pairs (nm, as in their ids)")
    ap.add_argument("--refit", action="store_true", help="nac-tmc: recompute the NAC's saved correction field")
    ap.add_argument("--anchor", default="corners",
                    help="nac-tmc: the NAC's geometry prior - 'corners' (default: LROC's published corners, "
                         "uncorrected), 'ohrc' (the 4 m field against SAC's OHRC), or an already-corrected NAC "
                         "id to fit against (e.g. M1350459544RE). See cut_nac_tmc's docstring for why corners.")
    a = ap.parse_args(argv)
    if a.kind == "viewpoint":
        if not (a.ohrc and a.ohrc_b and a.anchor_nac):
            raise SystemExit("viewpoint needs --ohrc, --ohrc-b and --anchor-nac")
        dirs = cut_viewpoint(a.ohrc, a.ohrc_b, a.anchor_nac, a.windows or 8, refit=a.refit)
        print(f"{len(dirs)} pair(s) written under {PAIRS}")
        return 0
    if a.kind == "site":
        if not (a.ohrc and a.tmc and a.nac):
            raise SystemExit("site needs --ohrc, --tmc and --nac")
        dirs = cut_site(a.ohrc, a.tmc, a.nac, tuple(a.legs), a.anchor_nac, a.windows or 8, refit=a.refit)
        print(f"{len(dirs)} pair(s) written under {PAIRS}")
        return 0
    if a.kind == "ohrc-nac-lro":
        if not a.nac:
            raise SystemExit("ohrc-nac-lro needs --nac (and --edr-url unless it is in <data>/nac_sac_manifest.csv)")
        dirs = cut_ohrc_nac_lro(a.nac, a.edr_url, a.windows or 8, a.ref_px or 640)
        print(f"{len(dirs)} pair(s) written under {PAIRS}")
        return 0
    if not a.tmc:
        raise SystemExit(f"{a.kind} needs --tmc")
    if a.kind == "tmc-iirs":
        if not (a.iirs and a.band):
            raise SystemExit("tmc-iirs needs --iirs and --band")
        dirs = cut_tmc_iirs(a.tmc, a.iirs, a.band, a.windows or 8, a.ref_px or 192, tuple(a.lat), a.step_km,
                            a.same_as)
    elif a.kind == "ohrc-tmc":
        dirs = cut_ohrc_tmc(a.tmc, a.windows or 4, a.ref_px or 384)
    else:
        if not (a.nac and a.edr_url):
            raise SystemExit("nac-tmc needs --nac and --edr-url")
        dirs = cut_nac_tmc(a.tmc, a.nac, a.edr_url, a.windows or 6, a.ref_px or 384, refit=a.refit,
                           anchor=a.anchor)
    print(f"{len(dirs)} pair(s) written under {PAIRS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
