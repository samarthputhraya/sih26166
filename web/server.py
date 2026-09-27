"""Serve the Mission Console locally as a working registration bench.

    python -m web.server                 # http://127.0.0.1:8000
    python -m web.server --port 8123

Why this exists: the published console is a read-only panel over frozen evidence, and the most
common reaction to it is "can I try my own images?". A browser cannot answer that - LoFTR and
MAGSAC++ are Python - so the page sends the images here and THIS process runs the pipeline.

What the bench can run, each as a background job the page polls for progress:

    upload   two images someone hands you (GeoTIFF, PDS, PNG, JPEG)
    sample   any real pair in data/pairs/, straight from its files, re-run live
    known    ONE image, warped here by a transform the page chose, then registered back - so
             the answer is known exactly and the error is measured, not estimated

Three properties it is built to keep:

1. **It calls `core.pipeline.run_all` directly.** Not a copy, not a simplified path. What a judge
   watches run is the same function that produced every number in REPORT.md. The result is then
   rendered by `web/panel.py`, the same renderer the frozen pairs use, so a live panel and a
   frozen panel cannot disagree about what a verdict means.

2. **It writes nothing.** No evidence log, no cache, no file in the repo. Uploads live in a
   temporary directory that is deleted when the job finishes. A demo cannot corrupt the
   freeze, which is the whole reason the evidence is frozen in the first place.

3. **Standard library only** (plus what core/ already needs). No FastAPI, no uvicorn, nothing to
   pip install on a demo laptop with the network off - Invariant 3.

Bind address is 127.0.0.1 deliberately: this serves a local demo, not a network service. It has
no authentication and runs an expensive pipeline on request, so it should never listen on 0.0.0.0.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import io
import json
import math
import pathlib
import re
import shutil
import sys
import tempfile
import threading
import time
import traceback
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE / "dist" / "mission-console.html"
sys.path.insert(0, str(ROOT))

MAX_UPLOAD = 64 * 1024 * 1024          # per request, both images together
PAIRS = ROOT / "data" / "pairs"          # real pairs; data lives in Drive, not git (Invariant 5)
KNOWN_MAX_SIDE = 900                     # a one-image test is shrunk to this first, for speed
KEEP_JOBS = 8                            # finished jobs held in memory for the page to fetch
ALLOWED = {".tif", ".tiff", ".img", ".xml", ".lbl", ".png", ".jpg", ".jpeg"}
_lock = threading.Lock()                # one registration at a time: LoFTR is memory-hungry


# The built page is a FRAGMENT: the Artifact runtime wraps it in a document and supplies a small
# reset. Serving the fragment raw drops that reset, and the most visible casualty is
# `[hidden]`, which without it loses to `.io{display:grid}` and paints empty boxes where hidden
# panels should be. Reproduce the wrapper here so the local page and the published page render
# identically - a demo that looks different from the link you sent is a demo you cannot trust.
SKELETON = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light">
<meta name="description" content="Chandrayaan-2 image registration across Sun angle, scale and sensor, with an independent area check that never sees the matches and a verdict region by region. Team LunaXX, SIH 2026 problem statement SIH26166.">
<style>
  :root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
  body{margin:0;font:14px system-ui,-apple-system,sans-serif;background:#bab8b2}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>
</head><body>
<!--PAGE-->
</body></html>
"""


FAVICON = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    b'<rect width="32" height="32" fill="#bab8b2"/>'
    b'<circle cx="16" cy="16" r="12" fill="#f4f4f1" stroke="#000" stroke-width="1.8"/>'
    b'<path d="M16 4a12 12 0 0 0 0 24c-4-3-5.8-7.3-5.8-12S12 7 16 4z" fill="#000"/></svg>'
)


def _document(fragment: str) -> str:
    return SKELETON.replace("<!--PAGE-->", fragment)


def _commit():
    from core.export import _commit as c
    return c(("core", "evaluation", "app"))


def _save(upload, into: pathlib.Path, stem: str) -> pathlib.Path:
    """Write one uploaded image to disk, converting anything core.io_loader cannot read.

    A judge is most likely to hand over a PNG or a screenshot. `load()` accepts TIFF and PDS
    products only, so those are re-encoded as a plain TIFF - which carries no ground scale, and
    the caller is told so rather than being shown a silent assumption.
    """
    name = pathlib.Path(upload.get("name") or "upload.tif").name
    ext = pathlib.Path(name).suffix.lower()
    if ext not in ALLOWED:
        raise ValueError(f"{name}: need one of {', '.join(sorted(ALLOWED))}")
    try:
        raw = base64.b64decode(upload["data"], validate=True)
    except (binascii.Error, KeyError, TypeError) as e:
        raise ValueError(f"{name}: not valid base64 ({e})") from e
    if not raw:
        raise ValueError(f"{name}: empty file")

    path = into / f"{stem}{ext}"
    path.write_bytes(raw)
    if ext in (".png", ".jpg", ".jpeg"):
        import cv2
        import numpy as np
        import tifffile
        im = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
        if im is None:
            raise ValueError(f"{name}: could not be decoded as an image")
        if im.ndim == 3:
            im = cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2GRAY)
        path = into / f"{stem}.tif"
        tifffile.imwrite(str(path), im)
    return path


def register(body: dict) -> dict:
    """Run the real pipeline on two uploaded images and return a console panel."""
    from core.pipeline import run_all
    from core.io_loader import load
    from web.panel import panel

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="lunaxx_upload_"))
    try:
        a = _save(body["a"], tmp, "a")
        b = _save(body["b"], tmp, "b")
        t0 = time.perf_counter()
        with _lock:
            r = run_all(a, b)
        wall = time.perf_counter() - t0

        def side(path, which):
            _, meta = load(path)
            gsd = meta.get("gsd_mpp")
            return {"inst": meta.get("instrument") or f"uploaded {which}",
                    "band": None if gsd else "no ground scale in the file",
                    "prod": pathlib.Path(body[which.lower()].get("name") or path.name).name,
                    "gsd": round(float(gsd), 3) if gsd else "unknown"}

        sa, sb = side(a, "A"), side(b, "B")
        # core's note is written for a log line, not a panel: it ends in its own full stop (so
        # " Scale: {note}." printed "..") and it names a NAC EDR label even when neither upload
        # is a NAC. Trim the sentence and drop the instrument-specific hint; the general advice
        # is already in the next sentence. Cosmetic only - no value is touched.
        scaled = ((r.get("scale_factors") or {}).get("note") or "").strip()
        scaled = scaled.split(". A NAC EDR label")[0].rstrip(". ")
        plain = (
            "<b>This ran just now, on this machine.</b> Not a cached result: "
            f"<code>core.pipeline.run_all</code> took {wall:.1f} s on CPU, the same function that "
            "produced every number in the frozen evidence, and the panel you are reading was "
            "drawn by the same renderer the frozen pairs use."
            + (f" Scale: {scaled}." if scaled else "")
            + ("" if sa["gsd"] != "unknown" and sb["gsd"] != "unknown" else
               " <b>Neither upload carried a ground scale</b>, so the common-scale step had "
               "nothing to bridge and both images were taken to be at the same scale already. "
               "Upload GeoTIFFs to exercise scale invariance.")
        )
        return panel(r, sa, sb, pid="upload", label="Your upload",
                     sub="Registered live on this machine, not from cache.",
                     tag="LIVE", plain=plain)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- the library: every real pair on this machine ------------------------------------------
#
# Labels and terminology come from each pair's own geometry_prior.json, written when the pair
# was cut. Nothing here decides whether a pair is cross-sensor or multi-modal: the prior says so,
# in the words Invariant 2 requires, and the page repeats it.

_library: list[dict] | None = None
_thumbs: dict[str, bytes] = {}


def _term(t: str) -> str:
    """The prior's terminology up to its first explanation: 'cross-sensor, cross-mission'."""
    return re.split(r"\s*[(:;]|\s+-\s+", t or "", maxsplit=1)[0].strip().rstrip(",")


#: Short instrument names for the library's grouping chips. Anything not listed keeps its name.
SHORT = {"Chandrayaan-2 OHRC": "OHRC", "LRO LROC NAC": "NAC", "Chandrayaan-2 IIRS": "IIRS",
         "SELENE (Kaguya) Terrain Camera": "Kaguya TC", "SELENE (Kaguya) Multiband Imager": "Kaguya MI",
         "Chandrayaan-2 TMC-2 nadir": "TMC-2", "Chandrayaan-2 TMC-2 fore (+25 deg)": "TMC-2 fore",
         "Chandrayaan-2 TMC-2 aft (-25 deg)": "TMC-2 aft", "LRO LOLA (elevation, rendered)": "LOLA relief"}


def library(root: pathlib.Path = PAIRS) -> list[dict]:
    """Every pair under `root` that has both images and a prior, labelled from the prior."""
    global _library
    if _library is not None and root == PAIRS:
        return _library
    out = []
    for prior in sorted(root.glob("*/geometry_prior.json")):
        d = prior.parent
        pid = d.name
        if not ((d / f"{pid}_source.tif").exists() and (d / f"{pid}_ref.tif").exists()):
            continue
        try:
            j = json.loads(prior.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        s, r = j.get("source") or {}, j.get("reference") or {}
        m = re.search(r"_w(\d+)", pid)
        a, b = s.get("instrument") or "source", r.get("instrument") or "reference"
        rid = r.get("product_id") or ""
        band = (r.get("band") or "").split(" (")[0]          # "749 nm (visible)" -> "749 nm"
        band = re.sub(r"\.0 nm$", " nm", band) if re.fullmatch(r"\d+(\.\d+)? nm", band) else ""
        b_full = f"{b} {band}" if band else b
        out.append({"id": pid, "family": pid[:m.start()] if m else pid,
                    "window": int(m.group(1)) if m else None,
                    "label": f"{a} → {b_full}" + (f" {rid}" if rid.startswith("M1") else ""),
                    "group": f"{SHORT.get(a, a)} → {SHORT.get(b, b)}" + (f" {band}" if band else ""),
                    "a": a, "b": b_full, "tag": _term(j.get("terminology") or ""),
                    "tier": j.get("tier") or ""})
    if root == PAIRS:
        _library = out
    return out


def thumb(pid: str, side: str = "ref") -> bytes | None:
    """A small JPEG of one image of a library pair, made once and kept in memory."""
    key = f"{pid}/{side}"
    if key in _thumbs:
        return _thumbs[key]
    if side not in ("ref", "source") or not any(e["id"] == pid for e in library()):
        return None
    from web.panel import jpg
    uri = jpg(PAIRS / pid / f"{pid}_{side}.tif", size=176 if side == "ref" else 320, q=74)
    _thumbs[key] = base64.b64decode(uri.split(",", 1)[1])
    return _thumbs[key]


# --- one image, a known answer ---------------------------------------------------------------

def known_transform(w: int, h: int, rot_deg: float, scale: float, dx: float, dy: float):
    """H_true mapping SOURCE pixels to REFERENCE pixels, built the way
    evaluation/synthetic_data.make_pair builds its own: rotation and scale about the centre,
    then a shift.

    The shift is pushed off the whole-pixel grid (+0.37, -0.63) whatever the page asked for. A
    whole-pixel shift is the one case the warp copies pixels without interpolating, and the
    error measured on it flatters the matcher - see SYNTH_SHIFT_PX in core/pipeline.py. The page
    is told the shift actually used.
    """
    import cv2
    import numpy as np
    dx, dy = float(dx) + 0.37, float(dy) - 0.63
    H = np.vstack([cv2.getRotationMatrix2D((w / 2, h / 2), float(rot_deg), float(scale)),
                   [0.0, 0.0, 1.0]])
    H[0, 2] += dx
    H[1, 2] += dy
    return H, dx, dy


def grid_error(H, H_true, w: int, h: int) -> dict | None:
    """RMS and max distance between where H and H_true send a 20 x 20 grid over the reference:
    the grid evaluation.metrics.evaluate uses for rmse_gt_px."""
    if H is None:
        return None
    import cv2
    import numpy as np
    gx, gy = np.meshgrid(np.linspace(0, w - 1, 20), np.linspace(0, h - 1, 20))
    pts = np.stack([gx.ravel(), gy.ravel()], 1).astype(np.float64).reshape(-1, 1, 2)
    got = cv2.perspectiveTransform(pts, np.asarray(H, np.float64)).reshape(-1, 2)
    want = cv2.perspectiveTransform(pts, np.asarray(H_true, np.float64)).reshape(-1, 2)
    d = np.linalg.norm(got - want, axis=1)
    return {"rms": round(float(np.sqrt(np.mean(d ** 2))), 3), "max": round(float(d.max()), 3)}


def decompose(H, w: int, h: int) -> dict | None:
    """Rotation, scale and centre shift read back out of a homography, in known_transform's
    terms. Exact for a similarity; for anything else it is the best similarity reading."""
    if H is None:
        return None
    import numpy as np
    H = np.asarray(H, np.float64) / H[2, 2]
    A, c = H[:2, :2], np.array([w / 2, h / 2, 1.0])
    m = H @ c
    return {"rot": round(math.degrees(math.atan2(-A[1, 0], A[0, 0])), 3),
            "scale": round(math.sqrt(abs(np.linalg.det(A))), 4),
            "dx": round(float(m[0] / m[2] - c[0]), 3), "dy": round(float(m[1] / m[2] - c[1]), 3)}


def known_pair(upload: dict, into: pathlib.Path, rot: float, scale: float, dx: float, dy: float,
               blur: float = 0.0, noise: float = 0.0):
    """Write (source, reference) for a one-image test and return them with H_true.

    The reference is the upload itself, shrunk to KNOWN_MAX_SIDE. The source is the reference
    warped by inv(H_true), then optionally blurred and given noise. Both are plain TIFFs with no
    map scale, so run_all's scale step does nothing and every pixel figure is in the pixels of
    the shrunk upload.
    """
    import cv2
    import numpy as np
    import tifffile
    from core.io_loader import load
    img, _ = load(_save(upload, into, "orig"))
    img = np.asarray(img, np.float32)
    if img.ndim == 3:
        img = img[..., 0]
    fin = np.isfinite(img)
    if not fin.any():
        raise ValueError("that image has no finite pixels")
    img = np.where(fin, img, np.float32(np.median(img[fin])))
    h0, w0 = img.shape
    k = KNOWN_MAX_SIDE / max(h0, w0)
    if k < 1:
        img = cv2.resize(img, (max(1, round(w0 * k)), max(1, round(h0 * k))),
                         interpolation=cv2.INTER_AREA)
    h, w = img.shape
    if min(h, w) < 96:
        raise ValueError(f"that image is {w} x {h} px; a one-image test needs at least 96 px a side")
    H, dx, dy = known_transform(w, h, rot, scale, dx, dy)
    src = cv2.warpPerspective(img, np.linalg.inv(H), (w, h), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if blur > 0:
        src = cv2.GaussianBlur(src, (0, 0), float(blur))
    if noise > 0:
        lo, hi = np.percentile(img, [1, 99])
        src = src + np.random.default_rng(0).normal(
            0, float(noise) / 100 * max(float(hi - lo), 1e-6), src.shape).astype(np.float32)
    a, b = into / "known_source.tif", into / "known_ref.tif"
    tifffile.imwrite(str(a), src.astype(np.float32))
    tifffile.imwrite(str(b), img.astype(np.float32))
    return a, b, H, {"w": w, "h": h, "shrunk_from": [w0, h0] if k < 1 else None,
                     "rot": float(rot), "scale": float(scale), "dx": round(dx, 2),
                     "dy": round(dy, 2), "blur": float(blur), "noise": float(noise)}


# --- jobs: a registration runs in the background and the page polls it -----------------------

_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _bundle_zip(r, pid, a, b) -> bytes | None:
    """The deliverables core/export.py writes for a pair, zipped; None if the export fails."""
    try:
        from core.export import bundle_bytes
        files = bundle_bytes(r, pid, a, b)
    except Exception:                                   # a download must not sink the result
        traceback.print_exc()
        return None
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(f"{pid}/{name}", data)
    return buf.getvalue()


def _side_from(meta: dict, inst: str, prod: str) -> dict:
    gsd = meta.get("gsd_mpp")
    return {"inst": meta.get("instrument") or inst,
            "band": None if gsd else "no ground scale in the file", "prod": prod,
            "gsd": round(float(gsd), 3) if gsd else "unknown"}


def run_job(job: dict, body: dict, run=None) -> None:
    """Do one job end to end. Fills job['result'] or job['error']; never raises."""
    from core.io_loader import load
    from web.panel import panel
    if run is None:
        from core.pipeline import run_all as run

    def progress(done, total):
        job.update(stage="check" if done >= total else "match", done=int(done), total=int(total))

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="lunaxx_job_"))
    try:
        mode, H_true, extra = job["mode"], None, {}
        if mode == "sample":
            pid = str(body.get("id") or "")
            e = next((x for x in library() if x["id"] == pid), None)
            if e is None:
                raise ValueError(f"no pair called {pid!r} in data/pairs")
            a, b = PAIRS / pid / f"{pid}_source.tif", PAIRS / pid / f"{pid}_ref.tif"
            label, tag, names = e["label"], e["tag"], (e["a"], e["b"])
            sub = (f"Window {e['window']:02d}, " if e["window"] else "") + "run from its files in data/pairs."
            plain = ("<b>Run just now, on this machine, from the pair's own files.</b> A live run can "
                     "differ from the logged row by a few inliers, because MAGSAC++ samples at random.")
        elif mode == "known":
            def v(k, d, lo, hi):
                return min(hi, max(lo, float(body.get(k, d))))
            a, b, H_true, extra = known_pair(body["a"], tmp, v("rot", 0, -45, 45), v("scale", 1, 0.6, 1.6),
                                             v("dx", 0, -150, 150), v("dy", 0, -150, 150),
                                             v("blur", 0, 0, 4), v("noise", 0, 0, 20))
            label, tag = "Your image, against itself", "known answer"
            sub = "Warped here by a transform the page chose, so the right answer is known exactly."
            plain = ("<b>The right answer is known here, so this measures the error instead of "
                     "estimating it.</b> Both images are the same picture, so the Sun has not moved: "
                     "this tests geometry, blur and noise, not lighting.")
            names = ("your image, warped", "your image")
        else:
            a, b = _save(body["a"], tmp, "a"), _save(body["b"], tmp, "b")
            label, tag = "Your upload", "live"
            sub = "Registered live on this machine, not from cache."
            plain = ("<b>This ran just now, on this machine.</b> Not a cached result: "
                     "<code>core.pipeline.run_all</code>, the same function that produced every "
                     "number in the frozen evidence.")
            names = (body["a"].get("name") or "image A", body["b"].get("name") or "image B")

        if _lock.locked():
            job["stage"] = "wait"
        with _lock:
            job.update(stage="prepare", started=time.time())
            r = run(a, b, H_true=H_true, progress=progress)
        job["stage"] = "pack"
        sa = _side_from(load(a)[1], names[0], pathlib.Path(str(names[0])).name)
        sb = _side_from(load(b)[1], names[1], pathlib.Path(str(names[1])).name)
        if mode == "upload" and "unknown" in (sa["gsd"], sb["gsd"]):
            plain += (" <b>At least one image carried no ground scale</b>, so both were taken to be "
                      "at the same scale already. Upload GeoTIFFs to exercise the scale step.")
        res = panel(r, sa, sb, pid=f"{mode}-{job['id'][:6]}", label=label, sub=sub, tag=tag, plain=plain)
        if mode == "known":
            w, h = extra["w"], extra["h"]
            res["known"] = dict(extra, err_final=grid_error(r.get("H_final"), H_true, w, h),
                                err_matcher=grid_error(r.get("H"), H_true, w, h),
                                got=decompose(r.get("H_final"), w, h), want=decompose(H_true, w, h))
        job["bundle"] = _bundle_zip(r, res["id"], a, b)
        res["bundle"] = f"api/jobs/{job['id']}/bundle.zip" if job["bundle"] else None
        job.update(result=res, state="done", stage="done")
    except ValueError as e:
        job.update(state="error", error=str(e))
    except Exception as e:                              # a bad pair must not kill the bench
        traceback.print_exc()
        job.update(state="error", error=f"{type(e).__name__}: {e}")
    finally:
        job["finished"] = time.time()
        shutil.rmtree(tmp, ignore_errors=True)


def start_job(body: dict, runner=run_job) -> dict:
    """Validate a job request, register it and start it on a thread. Raises ValueError."""
    mode = body.get("mode") or "upload"
    if mode not in ("upload", "sample", "known"):
        raise ValueError("mode must be upload, sample or known")
    if mode == "upload" and not ("a" in body and "b" in body):
        raise ValueError("send {mode:'upload', a:{name,data}, b:{name,data}} with base64 data")
    if mode == "known" and "a" not in body:
        raise ValueError("send {mode:'known', a:{name,data}, rot, scale, dx, dy}")
    job = {"id": uuid.uuid4().hex, "mode": mode, "state": "running", "stage": "queued",
           "done": 0, "total": 0, "created": time.time()}
    with _jobs_lock:
        finished = sorted((j for j in _jobs.values() if j["state"] != "running"),
                          key=lambda j: j["created"])
        for old in finished[:max(0, len(_jobs) + 1 - KEEP_JOBS)]:
            _jobs.pop(old["id"], None)
        _jobs[job["id"]] = job
    threading.Thread(target=runner, args=(job, body), daemon=True).start()
    return job


def job_view(job: dict) -> dict:
    """What the page polls: state, stage and tile progress, and the result once there is one."""
    out = {k: job.get(k) for k in ("id", "mode", "state", "stage", "done", "total", "error", "result")}
    end = job.get("finished") or time.time()
    out["elapsed"] = round(end - (job.get("started") or job["created"]), 1)
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "LunaXXConsole/1.0"

    def log_message(self, fmt, *args):      # one tidy line per request
        sys.stderr.write(f"  {self.address_string()} {fmt % args}\n")

    def _send(self, code, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        # allow_nan=False: json.dumps emits bare NaN/Infinity by default, which is valid
        # JavaScript but invalid JSON, so a browser's JSON.parse rejects the whole response.
        # Fail here, loudly, instead of sending a body no client can read.
        try:
            body = json.dumps(obj, allow_nan=False).encode("utf-8")
        except ValueError as e:
            body = json.dumps({"error": f"result was not JSON-serialisable: {e}"}).encode("utf-8")
            code = 500
        self._send(code, body)

    #: Read and throw away an over-size body so the client can finish sending and then read our
    #: reply. Bounded in both bytes and time: a rejected upload must not become a way to make the
    #: demo laptop sit in a read loop. Past the bound we give up and let the connection close,
    #: which is the old behaviour and no worse.
    DRAIN_LIMIT = 512 * 1024 * 1024
    DRAIN_SECONDS = 20.0

    def _drain(self, n: int) -> None:
        if n <= 0 or n > self.DRAIN_LIMIT:
            return
        left, deadline = n, time.monotonic() + self.DRAIN_SECONDS
        try:
            while left > 0 and time.monotonic() < deadline:
                chunk = self.rfile.read(min(left, 1 << 20))
                if not chunk:
                    break
                left -= len(chunk)
        except OSError:
            pass

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            if not PAGE.exists():
                return self._send(503, b"Run: python -m web.build_console", "text/plain")
            return self._send(200, _document(PAGE.read_text(encoding="utf-8")).encode("utf-8"),
                              "text/html; charset=utf-8")
        if path == "/api/health":
            return self._json(200, {"ok": True, "service": "lunaxx-console",
                                    "commit": _commit(), "max_bytes": MAX_UPLOAD,
                                    "accepts": sorted(ALLOWED),
                                    "modes": ["upload", "sample", "known"],
                                    "library": len(library()), "known_max_side": KNOWN_MAX_SIDE})
        if path == "/api/library":
            return self._json(200, {"pairs": library()})
        m = re.fullmatch(r"/api/thumb/([A-Za-z0-9_.-]+?)(_source)?\.jpg", path)
        if m:
            data = thumb(m.group(1), "source" if m.group(2) else "ref")
            if data is None:
                return self._json(404, {"error": "no such pair"})
            return self._send(200, data, "image/jpeg")
        m = re.fullmatch(r"/api/jobs/([0-9a-f]{32})(/bundle\.zip)?", path)
        if m:
            job = _jobs.get(m.group(1))
            if job is None:
                return self._json(404, {"error": "no such job; the server may have restarted"})
            if not m.group(2):
                return self._json(200, job_view(job))
            if not job.get("bundle"):
                return self._json(404, {"error": "no download for this job"})
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition",
                             f'attachment; filename="lunaxx_{job["result"]["id"]}.zip"')
            self.send_header("Content-Length", str(len(job["bundle"])))
            self.end_headers()
            self.wfile.write(job["bundle"])
            return None
        if path == "/favicon.ico":
            # Chrome asks for this unprompted and a 404 is the only error in the console.
            # One inline SVG moon, so a judge's devtools open on a clean log.
            return self._send(200, FAVICON, "image/svg+xml")
        self._json(404, {"error": "not found"})

    def do_POST(self):
        route = self.path.split("?", 1)[0]
        if route not in ("/api/register", "/api/jobs"):
            return self._json(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._json(400, {"error": "bad Content-Length"})
        if n <= 0 or n > MAX_UPLOAD:
            # Replying without reading the body leaves the client still uploading into a socket
            # nobody is draining: the connection resets and fetch() throws "Failed to fetch", so
            # the operator never sees this message. Drain first (bounded), then answer. Found by
            # uploading the 52.8 MB roster pair through the browser's own file inputs.
            self._drain(n)
            mb = lambda b: f"{b / 1048576:.1f} MB"                               # noqa: E731
            return self._json(413, {"error": (
                f"Request body is {mb(n)}; this server accepts {mb(MAX_UPLOAD)} "
                f"(about {mb(MAX_UPLOAD * 3 / 4)} of image, because the payload is base64). "
                f"Crop or downsample, or register a 640-px window instead of the whole frame - "
                f"that is what every frozen pair on the page is. The cap is a memory guard on "
                f"this laptop, not a limit of the pipeline.")})
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("send a JSON object")
            if route == "/api/jobs":
                return self._json(202, job_view(start_job(body)))
            if "a" not in body or "b" not in body:
                raise ValueError("send {a:{name,data}, b:{name,data}} with base64 data")
        except (ValueError, UnicodeDecodeError) as e:
            return self._json(400, {"error": str(e)})
        try:
            return self._json(200, register(body))
        except ValueError as e:
            return self._json(400, {"error": str(e)})
        except Exception as e:                      # a bad pair must not kill the demo
            traceback.print_exc()
            return self._json(500, {"error": f"{type(e).__name__}: {e}"})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1",
                    help="loopback by default; this has no auth, do not expose it")
    a = ap.parse_args(argv)
    if not PAGE.exists():
        print("The page is not built yet. Run:  python -m web.build_console")
        return 1
    # Build LoFTR NOW, before the server accepts anything. core builds it inside an offline guard
    # that replaces socket.socket process-wide for the second or two it takes; built lazily by the
    # first job, that window caught this server's own accept() (the page polls while a job runs)
    # and killed the process. Found on 27 Sep by polling a job every 0.4 s.
    print("  loading LoFTR weights (offline) ...", flush=True)
    try:
        from core.matcher import _get_matcher
        _get_matcher()
    except (Exception, SystemExit) as e:    # SystemExit: build_matcher's missing-weights message
        print(f"  LoFTR could not be built, so registration will fail until it can: {e}")
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"  Mission Console (live)  http://{a.host}:{a.port}")
    print(f"  code commit {_commit()} · uploads run core.pipeline.run_all on CPU")
    print("  nothing is written to the repo; Ctrl-C to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
