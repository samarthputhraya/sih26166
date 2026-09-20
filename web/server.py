"""Serve the Mission Console locally AND let it register a pair you upload.

    python -m web.server                 # http://127.0.0.1:8000
    python -m web.server --port 8123

Why this exists: the published console is a read-only panel over frozen evidence, and the most
common reaction to it is "can I try my own images?". A browser cannot answer that - LoFTR and
MAGSAC++ are Python - so the page posts the two images here and THIS process runs the pipeline.

Three properties it is built to keep:

1. **It calls `core.pipeline.run_all` directly.** Not a copy, not a simplified path. What a judge
   watches run is the same function that produced every number in REPORT.md. The result is then
   rendered by `web/panel.py`, the same renderer the frozen pairs use, so a live panel and a
   frozen panel cannot disagree about what a verdict means.

2. **It writes nothing.** No evidence log, no cache, no file in the repo. Uploads live in a
   temporary directory that is deleted when the request finishes. A demo cannot corrupt the
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
import json
import pathlib
import shutil
import sys
import tempfile
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE / "dist" / "mission-console.html"
sys.path.insert(0, str(ROOT))

MAX_UPLOAD = 64 * 1024 * 1024          # per request, both images together
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
<meta name="color-scheme" content="dark">
<meta name="description" content="Chandrayaan-2 image registration across Sun angle, scale and sensor, with an independent area check that never sees the matches and a verdict for every region of every result. Team LunaXX, SIH 2026 problem statement SIH26166.">
<style>
  :root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
  body{margin:0;font:14px system-ui,-apple-system,sans-serif;background:#faf9f7}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>
</head><body>
<!--PAGE-->
</body></html>
"""


FAVICON = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    b'<rect width="32" height="32" fill="#0b0d11"/>'
    b'<circle cx="16" cy="16" r="9" fill="none" stroke="#e9e5dc" stroke-width="2"/>'
    b'<path d="M16 7a9 9 0 0 0 0 18z" fill="#e9e5dc"/></svg>'
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
                                    "accepts": sorted(ALLOWED)})
        if path == "/favicon.ico":
            # Chrome asks for this unprompted and a 404 is the only error in the console.
            # One inline SVG moon, so a judge's devtools open on a clean log.
            return self._send(200, FAVICON, "image/svg+xml")
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/register":
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
            if not isinstance(body, dict) or "a" not in body or "b" not in body:
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
