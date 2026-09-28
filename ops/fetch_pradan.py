"""Pull files out of a PRADAN product zip by HTTP range, without downloading the whole zip.

    python -m ops.fetch_pradan ch2_tmc_ncn_20200203T1845562233_d_img_m65 --cookie-file <file>
    python -m ops.fetch_pradan ch2_iir_nci_20200203T1845559180_d_img_m65 --bands 3 18 51 --cookie-file <file>
    python -m ops.fetch_pradan <product> --list --cookie-file <file>      # members and sizes only

WHY BY RANGE. PRADAN serves every Chandrayaan-2 product as one zip behind a login, and it honours
HTTP Range. A calibrated IIRS zip is 3-5 GB, served at ~0.5 MB/s, and on 18 Sep three whole-file
downloads died part-way (150 MB, 544 MB, 1.34 GB). What registration needs from it is two or three
bands. The cube inside is one deflated ENVI BSQ member (band after band), so reading it through
`zipfile` on top of a seekable range reader inflates the stream from its start and can STOP after
the last band wanted: bands 3, 18 and 51 of 256 cost about a fifth of the zip. Deflate has no
random access, so a band near the end of the cube costs nearly the whole zip.

A TMC-2 zip (0.4-0.9 GB, ~8 MB/s) is taken whole but member by member, which is the same code.

THE LOGIN. The script never sees a password. It sends the `Cookie` header of a logged-in browser
session, read from `--cookie-file` (one line, as DevTools shows it on a request to
pradan.issdc.gov.in). Keep that file out of the repository. PRADAN logs a session out after
30 minutes idle; a long IIRS read keeps it busy, and a failed chunk is retried, not restarted.

WHAT IT WRITES, in the layout the cutters read (`ops/cut_pradan_pairs.py`, `ops/cut_site_pairs.py`):
    <data>/pradan/<tmc2|iirs|ohrc>/<member path inside the zip>
    IIRS bands as <id>_band<NNN>.f32 (float32, lines x samples) beside the label, with
    <id>_bands_PROVENANCE.json (source URL, member offsets, sha256 per band)
and appends one row per file to <data>/download_manifest_done.csv (url, dest, bytes, sha256,
group, id, utc) - the list REPORT.md's "Products downloaded" section is built from.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import io
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())
MANIFEST = DATA / "download_manifest_done.csv"
BASE = "https://pradan.issdc.gov.in/ch2/protected/downloadData/POST_OD/isda_archive/ch2_bundle/cho_bundle/nop"
# instrument code in the product id -> (collection, query tag, folder under <data>/pradan, manifest group)
COLLECTIONS = {"tmc": ("tmc_collection", "tmc2", "tmc2", "pradan_tmc2"),
               "iir": ("iir_collection", "iirs", "iirs", "pradan_iirs"),
               "ohr": ("ohr_collection", "ohrc", "ohrc", "pradan_ohrc")}
CHUNK = 16 << 20


def product_url(pid: str) -> str:
    """ch2_<ins>_<n><c|d><x>_<yyyymmdd>T..._d_<kind>_<stn> -> its zip on PRADAN."""
    m = re.match(r"^ch2_(tmc|iir|ohr)_n([cd])[a-z]_(\d{8})T\d+_d_[a-z]+_[a-z0-9]+$", pid)
    if not m:
        raise SystemExit(f"{pid!r} does not look like a Chandrayaan-2 product id")
    ins, level, day = m.groups()
    coll, tag, _, _ = COLLECTIONS[ins]
    return f"{BASE}/{coll}/data/{'calibrated' if level == 'c' else 'derived'}/{day}/{pid}.zip?{tag}"


class RangeReader(io.RawIOBase):
    """A read-only, seekable file over HTTP Range, with one cached chunk and retries."""

    def __init__(self, url, cookie, chunk=CHUNK, tries=6):
        self.url, self.cookie, self.chunk, self.tries = url, cookie, chunk, tries
        self.pos, self.buf_start, self.buf = 0, -1, b""
        self.fetched = 0
        first = self._get(0, 0)
        self.size = first[1]

    def _get(self, start, end):
        """Bytes [start, end] and the total size; retries with backoff on any network error."""
        for k in range(self.tries):
            req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}",
                                                            "Cookie": self.cookie,
                                                            "User-Agent": "sih26166-fetch/1"})
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    ctype = r.headers.get("Content-Type", "")
                    cr = r.headers.get("Content-Range", "")
                    if r.status != 206 or not cr:
                        raise SystemExit(f"no ranged answer (HTTP {r.status}, {ctype!r}): the cookie is "
                                         "missing or expired - log in again and refresh the cookie file")
                    data = r.read()
                    total = int(cr.rsplit("/", 1)[1])
                    self.fetched += len(data)
                    return data, total
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                wait = min(60, 5 * 2 ** k)
                print(f"    range {start}-{end}: {type(e).__name__} {e}; retry {k + 1}/{self.tries} in {wait}s",
                      flush=True)
                time.sleep(wait)
        raise SystemExit(f"range {start}-{end} failed {self.tries} times")

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=io.SEEK_SET):
        self.pos = {io.SEEK_SET: off, io.SEEK_CUR: self.pos + off, io.SEEK_END: self.size + off}[whence]
        return self.pos

    def readinto(self, b):
        if self.pos >= self.size:
            return 0
        if not (self.buf_start <= self.pos < self.buf_start + len(self.buf)):
            end = min(self.pos + self.chunk, self.size) - 1
            self.buf, _ = self._get(self.pos, end)
            self.buf_start = self.pos
        i = self.pos - self.buf_start
        n = min(len(b), len(self.buf) - i)
        b[:n] = self.buf[i:i + n]
        self.pos += n
        return n


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _manifest(rows):
    new = not MANIFEST.exists()
    with open(MANIFEST, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["url", "dest", "bytes", "sha256", "group", "id", "utc"])
        w.writerows(rows)


def _copy(src, dst, total, label):
    t0, done = time.time(), 0
    with open(dst, "wb") as out:
        while True:
            c = src.read(CHUNK)
            if not c:
                break
            out.write(c)
            done += len(c)
            rate = done / max(time.time() - t0, 1e-6) / 1e6
            print(f"    {label}: {done / 1e6:,.0f} / {total / 1e6:,.0f} MB ({rate:.1f} MB/s out)", flush=True)
    return done


def fetch(pid, cookie, bands=None, list_only=False):
    url = product_url(pid)
    ins = pid[4:7]
    _, _, folder, group = COLLECTIONS[ins]
    dest_root = DATA / "pradan" / folder
    rr = RangeReader(url, cookie)
    print(f"{pid}: zip is {rr.size / 1e6:,.1f} MB at {url}")
    zf = zipfile.ZipFile(io.BufferedReader(rr, buffer_size=CHUNK))
    infos = zf.infolist()
    for i in infos:
        print(f"  {i.filename}  {i.file_size / 1e6:,.1f} MB (stored as {i.compress_size / 1e6:,.1f} MB, "
              f"{'deflated' if i.compress_type == zipfile.ZIP_DEFLATED else 'stored'})")
    if list_only:
        return 0
    utc = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    rows = []
    cube = next((i for i in infos if i.filename.endswith(".qub")), None)
    for i in infos:
        if i.is_dir() or (i is cube and bands):
            continue
        dst = dest_root / i.filename
        if dst.exists() and dst.stat().st_size == i.file_size:
            print(f"  {dst.name}: already on disk ({i.file_size:,} bytes) - kept, not re-listed")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(i) as src:
            _copy(src, dst, i.file_size, pathlib.Path(i.filename).name)
        rows.append([url, dst.as_posix(), dst.stat().st_size, _sha(dst), group, pid, utc])
        print(f"  wrote {dst}")
    if cube is not None and bands:
        rows += _bands(zf, cube, url, pid, dest_root, sorted(set(bands)), group, utc)
    _manifest(rows)
    print(f"{len(rows)} file(s); {rr.fetched / 1e6:,.1f} MB transferred of a {rr.size / 1e6:,.1f} MB zip")
    return 0


def _bands(zf, cube, url, pid, dest_root, bands, group, utc):
    """Stream the BSQ cube and keep `bands` (1-based, as in the label), stopping after the last."""
    import numpy as np
    hdr_name = cube.filename[:-4] + ".hdr"
    hdr = zf.read(hdr_name).decode("latin1") if hdr_name in zf.namelist() else ""
    if not hdr:
        hdr_i = next(i for i in zf.infolist() if i.filename.endswith(".hdr"))
        hdr = zf.read(hdr_i).decode("latin1")
    get = lambda k: int(re.search(rf"^\s*{k}\s*=\s*(\d+)", hdr, re.M | re.I).group(1))  # noqa: E731
    S, L, B = get("samples"), get("lines"), get("bands")
    if not re.search(r"^\s*interleave\s*=\s*bsq", hdr, re.M | re.I) or get("data type") != 4:
        raise SystemExit(f"{cube.filename}: expected float32 BSQ, header says:\n{hdr}")
    per = S * L * 4
    if cube.file_size != per * B:
        raise SystemExit(f"{cube.filename}: {cube.file_size} bytes is not {B} bands x {L} x {S} x 4")
    base = dest_root / pathlib.Path(cube.filename).parent / pid
    base.parent.mkdir(parents=True, exist_ok=True)
    rows, shas = [], {}
    with zf.open(cube) as src:
        for b in range(1, max(bands) + 1):
            t0 = time.time()
            raw = src.read(per)
            if len(raw) != per:
                raise SystemExit(f"band {b}: short read ({len(raw)} of {per})")
            if b in bands:
                dst = base.parent / f"{pid}_band{b:03d}.f32"
                np.frombuffer(raw, dtype="<f4").reshape(L, S).tofile(dst)
                shas[dst.stem] = _sha(dst)
                rows.append([f"{url}#band{b}", dst.as_posix(), dst.stat().st_size, shas[dst.stem], group, pid, utc])
                print(f"  band {b}: wrote {dst.name} ({time.time() - t0:.0f}s)", flush=True)
            else:
                print(f"  band {b}: passed ({time.time() - t0:.0f}s)", flush=True)
    prov_p = base.parent / f"{pid}_bands_PROVENANCE.json"
    old = json.loads(prov_p.read_text(encoding="utf-8")) if prov_p.exists() else {}
    prov = {"product": pid, "source_zip": url,
            "qub_member": {"name": cube.filename, "start": cube.header_offset, "csize": cube.compress_size,
                           "usize": cube.file_size},
            "method": f"ops.fetch_pradan: HTTP Range reads of the zip ({CHUNK >> 20} MB requests, retried), the "
                      f"deflated cube inflated by zipfile and read band by band; BSQ float32 little-endian "
                      f"{B} x {L} x {S}; each run stops after its last band wanted and keeps only those.",
            "runs": old.get("runs", []) + [{"utc": utc, "bands": bands}],
            "bands": {**old.get("bands", {}), **shas}}      # a later run adds bands, never drops them
    prov_p.write_text(json.dumps(prov, indent=1), encoding="utf-8")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("product", help="Chandrayaan-2 product id, e.g. ch2_tmc_ncn_20200203T1845562233_d_img_m65")
    ap.add_argument("--cookie-file", required=True, type=pathlib.Path,
                    help="one line: the Cookie header of a logged-in PRADAN browser session")
    ap.add_argument("--bands", type=int, nargs="*", help="IIRS: 1-based bands to keep (the cube is not kept)")
    ap.add_argument("--list", action="store_true", help="list the zip's members and stop")
    a = ap.parse_args(argv)
    cookie = a.cookie_file.read_text(encoding="utf-8").strip()
    if cookie.lower().startswith("cookie:"):
        cookie = cookie.split(":", 1)[1].strip()
    return fetch(a.product, cookie, bands=a.bands, list_only=a.list)


if __name__ == "__main__":
    sys.exit(main())
