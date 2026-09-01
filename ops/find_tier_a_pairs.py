"""Find Tier A pairs (same site, LROC NAC, incidence differing >=15 deg) from the PDS index.

WHY THIS EXISTS
---------------
The planned Tier A route was ODE's `EDRNAC4` metadata. **`oderest.rsl.wustl.edu` does not
resolve** (checked 1 Sep 2026; `ode.rsl.wustl.edu` resolves but has no `/live2/` endpoint).
So the live-API route is unavailable.

The PDS volumes ship the same geometry in `INDEX/CUMINDEX.TAB`: 225,950 rows x 901 fixed bytes,
with PRODUCT_ID, CENTER_LATITUDE/LONGITUDE, INCIDENCE/EMISSION/PHASE_ANGLE and
FILE_SPECIFICATION_NAME. It is a static file, so it cannot go down, and it is the canonical
source rather than a derived service.

A NAC EDR is 264 MB, but it is uncompressed 8-bit with fixed 5064-byte records and the server
sends `Accept-Ranges: bytes` -- so a 640-line crop is a 3.2 MB range request, not a 264 MB
download. `crop()` below does that.

THE TEXTURE TEST -- READ THIS BEFORE REJECTING ANY FRAME
---------------------------------------------------------
Known issue #6 says "check std > 10". **That threshold is for CALIBRATED imagery** (CH-2 OHRC is
`data_calibrated`, std 32.4). LROC NAC **EDR is raw and companded**, and good frames sit at
std 4-6 with 93% of pixels inside a 16-DN band. Applying `std > 10` to raw EDR rejects perfectly
good data -- it rejected every one of the six best Tier A pairs on the first pass.

Use `looks_like_terrain()` instead. The discriminator that actually works is **row-to-row
correlation**, because it separates structure from noise, which a stretch cannot:

    good Tier A frame   raw std 4.4   DN span 51   row corr 0.973   <- real terrain
    M108587604RE        raw std 1.5   DN span 14   row corr 0.352   <- noise, correctly rejected

Stretching noise gives a high std (59.8) and a convincing-looking picture, so **std after
stretching proves nothing**. Correlation is the test.
"""
from __future__ import annotations

import csv
import math
import re
import urllib.request
from collections import defaultdict

import numpy as np

PDS = "https://pds.lroc.im-ldi.com/data/"
CUMINDEX = PDS + "LRO-L-LROC-2-EDR-V1.0/LROLRC_0003/INDEX/CUMINDEX.TAB"
REC = 901

# name: (START_BYTE as printed in CUMINDEX.LBL, BYTES)
FIELDS = {
    "file_spec": (16, 75), "product_id": (122, 13), "emission": (725, 5),
    "incidence": (731, 6), "phase": (738, 6), "sub_solar_az": (752, 6),
    "lat": (806, 6), "lon": (813, 6),
}


def _field(rec: bytes, key: str) -> str:
    start, n = FIELDS[key]
    return rec[start - 1:start - 1 + n].decode("ascii", "replace").strip().strip('"')


def scan_index(out_csv, inc_range=(20.0, 80.0)):
    """Stream CUMINDEX (203 MB) and write a compact catalogue. Nothing is stored on disk."""
    kept = total = 0
    with urllib.request.urlopen(CUMINDEX, timeout=900) as stream, \
            open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(list(FIELDS))
        buf = b""
        while True:
            chunk = stream.read(REC * 512)
            if not chunk:
                break
            buf += chunk
            while len(buf) >= REC:
                rec, buf = buf[:REC], buf[REC:]
                total += 1
                try:
                    inc = float(_field(rec, "incidence"))
                    float(_field(rec, "lat")); float(_field(rec, "lon"))
                except ValueError:
                    continue                       # night-side rows carry junk here
                if not (inc_range[0] <= inc <= inc_range[1]):
                    continue                       # ODE also returns 139 and 164 deg
                w.writerow([_field(rec, k) for k in FIELDS])
                kept += 1
    return total, kept


def find_pairs(catalogue_csv, min_inc_diff=15.0, max_sep_deg=0.02, modes=("LE", "RE")):
    """Co-located frames whose incidence differs enough to be a sun-angle test."""
    rows = []
    for r in csv.DictReader(open(catalogue_csv)):
        if r["product_id"][-2:] not in modes:
            continue
        r["latf"], r["lonf"] = float(r["lat"]), float(r["lon"])
        r["inc"] = float(r["incidence"])
        rows.append(r)

    cells = defaultdict(list)
    for r in rows:
        cells[(round(r["latf"] / 0.05), round(r["lonf"] / 0.05))].append(r)

    pairs = []
    for group in cells.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                if a["product_id"][:10] == b["product_id"][:10]:
                    continue                       # same observation, LE/RE of one frame
                d_inc = abs(a["inc"] - b["inc"])
                if d_inc < min_inc_diff:
                    continue
                sep = math.hypot(a["latf"] - b["latf"],
                                 (a["lonf"] - b["lonf"]) * math.cos(math.radians(a["latf"])))
                if sep > max_sep_deg:
                    continue
                pairs.append({"a": a["product_id"], "b": b["product_id"],
                              "inc_a": a["inc"], "inc_b": b["inc"], "d_inc": d_inc,
                              "sep_km": sep * 30.3, "lat": a["latf"], "lon": a["lonf"],
                              "file_a": a["file_spec"], "file_b": b["file_spec"]})
    pairs.sort(key=lambda p: (-p["d_inc"], p["sep_km"]))
    return pairs


def _label(url):
    req = urllib.request.Request(url, headers={"Range": "bytes=0-20000"})
    text = urllib.request.urlopen(req, timeout=180).read().replace(b"\x00", b"").decode("ascii", "replace")
    g = lambda k: int(re.search(k + r"\s*=\s*(\d+)", text).group(1))
    return g("RECORD_BYTES"), g(r"\^IMAGE"), g("LINES"), g("LINE_SAMPLES")


def crop(file_spec, line0=None, n_lines=640, n_cols=640):
    """Range-fetch a crop from a NAC EDR. ~3 MB instead of the full 264 MB."""
    url = PDS + file_spec
    rec_bytes, image_rec, lines, samples = _label(url)
    line0 = (lines // 2 - n_lines // 2) if line0 is None else line0
    line0 = max(0, min(line0, lines - n_lines))
    offset = (image_rec - 1) * rec_bytes
    first = offset + line0 * rec_bytes
    last = offset + (line0 + n_lines) * rec_bytes - 1
    req = urllib.request.Request(url, headers={"Range": f"bytes={first}-{last}"})
    raw = urllib.request.urlopen(req, timeout=600).read()
    arr = np.frombuffer(raw, np.uint8)[:n_lines * rec_bytes].reshape(n_lines, rec_bytes)[:, :samples]
    mid = samples // 2
    return arr[:, max(0, mid - n_cols // 2):mid + n_cols // 2]


def looks_like_terrain(arr, min_row_corr=0.80, min_dn_span=15):
    """Does THIS CROP contain usable terrain, or is it noise?

    Do NOT use `std > 10` on raw EDR -- see the module docstring. Row-to-row correlation is
    the discriminator: terrain is spatially coherent, sensor noise is not.

    The two numbers mean different things, and so do their failures:

    - **low `row_corr`** -> noise. The FRAME is bad; reject it and pick another pair.
    - **low `dn_span` with high `row_corr`** -> real but locally flat ground. The frame is
      fine; this CROP is a poor matching target. Scan other line offsets before giving up --
      a 52,224-line NAC frame varies enormously along its length.
    """
    x = arr.astype(np.float64)
    corrs = [np.corrcoef(x[i], x[i + 1])[0, 1] for i in range(0, len(x) - 1, max(1, len(x) // 32))]
    row_corr = float(np.nanmedian(corrs))
    dn_span = float(np.percentile(x, 99) - np.percentile(x, 1))
    return {
        "row_corr": row_corr,
        "dn_span": dn_span,
        "raw_std": float(x.std()),
        "ok": bool(row_corr >= min_row_corr and dn_span >= min_dn_span),
    }


def stretch(arr, lo_pct=2, hi_pct=98):
    """Percentile stretch, for LOOKING at raw EDR. Never judge texture on the result."""
    x = arr.astype(np.float32)
    lo, hi = np.percentile(x, (lo_pct, hi_pct))
    return np.clip((x - lo) * 255.0 / max(hi - lo, 1), 0, 255).astype(np.uint8)


if __name__ == "__main__":
    import pathlib
    import sys

    cat = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "nac_catalogue.csv")
    if not cat.exists():
        print(f"streaming CUMINDEX -> {cat} (203 MB over the wire, not stored) ...")
        print("scanned %d records, kept %d" % scan_index(cat))

    pairs = find_pairs(cat)
    print(f"\n{len(pairs)} Tier A candidate pairs\n")
    print(f"{'d_inc':>7} {'sep_km':>7}  {'A':13}{'incA':>6}  {'B':13}{'incB':>6}  {'lat':>7}{'lon':>8}")
    for p in pairs[:10]:
        print(f"{p['d_inc']:6.1f}d {p['sep_km']:7.1f}  {p['a']:13}{p['inc_a']:6.1f}  "
              f"{p['b']:13}{p['inc_b']:6.1f}  {p['lat']:7.2f}{p['lon']:8.2f}")

    if pairs:
        best = pairs[0]
        print(f"\nchecking {best['a']} / {best['b']} for terrain ...")
        for tag, fs in (("A", best["file_a"]), ("B", best["file_b"])):
            v = looks_like_terrain(crop(fs))
            print(f"  {tag}: row_corr {v['row_corr']:.3f}  dn_span {v['dn_span']:.0f}  "
                  f"raw_std {v['raw_std']:.1f}  -> {'terrain' if v['ok'] else 'REJECT'}")
