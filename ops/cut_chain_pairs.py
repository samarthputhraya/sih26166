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
            IIRS band >= 1000 nm: MULTI-MODAL (visible vs near-infrared).
            IIRS band < 1000 nm (e.g. band 3, 746 nm): NOT multi-modal - the control.
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
import datetime as _dt
import json
import math
import pathlib
import re
import sys

import numpy as np

from ops.cut_pradan_pairs import DATA, PAIRS, LocalEqc, _sha, frame_from_grid, tmc_nadir

IIRS_DIR = DATA / "pradan" / "iirs"


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
            "path": str(f32), "band": band, "center_wavelength_nm": nm,
            "modality": "near-infrared" if nm >= 1000 else "visible/near-visible",
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
    multimodal = info_i["center_wavelength_nm"] >= 1000
    tier = ("C (visible-infrared real, multi-modal; Chandrayaan-2 TMC-2 vs IIRS, same orbit)" if multimodal
            else "B (cross-sensor real, TMC-2 vs IIRS near-visible band, same orbit)")
    term = ("cross-sensor (Chandrayaan-2 TMC-2 vs IIRS), same mission - NOT cross-mission; "
            + ("MULTI-MODAL: visible panchromatic vs near-infrared" if multimodal
               else "NOT multi-modal: IIRS band under 1000 nm against a visible camera - the control")
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
                          "is disagreement between the TMC-2 archive grid and the OHRC-corrected NAC",
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


def ohrc_to_lroc_shift(proj, ohrc_f):
    """The map shift that puts SAC's OHRC frame into LROC's geometry, from the correction SAC's own
    NAC already carries (<data>/site_geometry/M1350459544RE.json, fitted 19 Sep against the OHRC
    at 4 m, frozen evidence): the NAC was moved by `correction_m` plus an affine field to sit on the
    OHRC, so the OHRC moves by minus that displacement, evaluated at the OHRC frame's centre. Uses
    no TMC-2 pixel."""
    from ops import cut_site_pairs as S
    p = json.loads((S.GEOM_DIR / f"{SAC_NAC}.json").read_text(encoding="utf-8"))
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=("tmc-iirs", "nac-tmc", "ohrc-tmc"))
    ap.add_argument("--tmc", required=True, help="calibrated TMC-2 nadir product id")
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
