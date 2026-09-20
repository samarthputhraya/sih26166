"""Record the Mission Console driving itself, as frames, for an explainer video.

    python -m web.film                     # -> web/dist/film/frames + shots.json
    python -m web.film --fps 12 --width 1600

It launches its own Chrome with remote debugging, loads the built console, runs a scripted
sequence of BEATS - scroll here, dial the Sun there, blink the comparator, switch to the refused
pair - and captures the viewport with CDP `Page.startScreencast` while it happens. ffmpeg turns
the frames into a video; `narration.md` carries the matching script, beat by beat, so the
voice-over and the picture stay in step without anyone counting seconds by hand.

Why its own Chrome and not the one already open: a backgrounded tab is throttled to about 1 fps
by the browser, so anything captured from a tab that is not frontmost records a slideshow of a
smooth page. This process owns its window and keeps it active.

Nothing here touches the repository or the evidence. It reads the built page and writes frames.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE / "dist" / "mission-console.html"
OUT = HERE / "dist" / "film"
CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# Each beat: (seconds, label, javascript). The label is what narration.md keys off.
BEATS = [
    (7.0, "open", "window.scrollTo({top:0}); null"),
    (5.0, "telemetry", "document.querySelector('.tele').scrollIntoView({block:'center'}); null"),
    (4.0, "sun-arrive", "document.querySelector('#sun').scrollIntoView({block:'start'}); null"),
    (11.0, "sun-sweep", """(()=>{const d=document.querySelector('#dz');let v=0;
        clearInterval(window.__f);window.__f=setInterval(()=>{v=(v+3)%155;d.value=v;
        d.dispatchEvent(new Event('input'));},90);})()"""),
    (5.0, "sun-hard-band", """(()=>{clearInterval(window.__f);const d=document.querySelector('#dz');
        d.value=100;d.dispatchEvent(new Event('input'));})()"""),
    (5.0, "trust-arrive", "document.querySelector('#trust').scrollIntoView({block:'start'}); null"),
    (8.0, "trust-accepted", """(()=>{document.querySelector('[data-p=\\"0\\"]').click();
        setTimeout(()=>document.querySelector('[data-layer=\\"blink\\"]').click(),600);})()"""),
    (9.0, "trust-refused", """(()=>{document.querySelector('[data-p=\\"5\\"]').click();
        setTimeout(()=>document.querySelector('[data-layer=\\"warp\\"]').click(),600);})()"""),
    (8.0, "trust-band-test", """(()=>{const b=document.querySelector('#band');
        if(b) b.scrollIntoView({block:'center'});})()"""),
    (6.0, "trust-iirs", """(()=>{document.querySelector('[data-p=\\"6\\"]').click();
        setTimeout(()=>document.querySelector('#verdict').scrollIntoView({block:'center'}),500);})()"""),
    (7.0, "tiling", "document.querySelector('#tile').scrollIntoView({block:'start'}); null"),
    (8.0, "calibration", "document.querySelector('#cal').scrollIntoView({block:'start'}); null"),
    (6.0, "pipeline", "document.querySelector('#flow').scrollIntoView({block:'start'}); null"),
    (7.0, "results", "document.querySelector('#registers').scrollIntoView({block:'start'}); null"),
    (7.0, "refusals", "document.querySelector('#refused').scrollIntoView({block:'start'}); null"),
    (5.0, "close", "document.querySelector('footer').scrollIntoView({block:'end'}); null"),
]


async def record(port: int, width: int, height: int, fps: int, quality: int):
    import websockets
    import urllib.request

    for _ in range(80):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2).read())
            page = next(t for t in tabs if t["type"] == "page")
            break
        except Exception:
            await asyncio.sleep(0.25)
    else:
        raise SystemExit("Chrome never exposed a debugging target")

    frames, beats, n = [], [], [0]
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=64 * 1024 * 1024) as ws:
        ident = [0]

        async def send(method, params=None):
            ident[0] += 1
            await ws.send(json.dumps({"id": ident[0], "method": method, "params": params or {}}))
            while True:
                m = json.loads(await ws.recv())
                if m.get("id") == ident[0]:
                    return m.get("result", {})
                await handle(m)

        async def handle(m):
            if m.get("method") == "Page.screencastFrame":
                p = m["params"]
                frames.append((time.perf_counter(), p["data"]))
                await ws.send(json.dumps({"id": 900000 + n[0], "method": "Page.screencastFrameAck",
                                          "params": {"sessionId": p["sessionId"]}}))
                n[0] += 1

        async def drain(seconds):
            end = time.perf_counter() + seconds
            while time.perf_counter() < end:
                try:
                    m = json.loads(await asyncio.wait_for(ws.recv(), timeout=max(0.02, end - time.perf_counter())))
                except asyncio.TimeoutError:
                    return
                await handle(m)

        await send("Page.enable")
        await send("Runtime.enable")
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
        await send("Page.navigate", {"url": PAGE.resolve().as_uri()})
        await drain(6.0)                                    # fonts, three.js, first render
        await send("Page.startScreencast",
                   {"format": "jpeg", "quality": quality, "everyNthFrame": 1,
                    "maxWidth": width, "maxHeight": height})
        t0 = time.perf_counter()
        for seconds, label, js in BEATS:
            beats.append({"label": label, "at": round(time.perf_counter() - t0, 2), "dur": seconds})
            await send("Runtime.evaluate", {"expression": js, "awaitPromise": False})
            await drain(seconds)
        await send("Page.stopScreencast")
        total = time.perf_counter() - t0

    if not frames:
        raise SystemExit("no frames captured")
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("f_*.jpg"):
        f.unlink()
    base = frames[0][0]
    step, k, j = 1.0 / fps, 0, 0
    while k * step <= total:                                # resample to a constant frame rate
        want = base + k * step
        while j + 1 < len(frames) and frames[j + 1][0] <= want:
            j += 1
        (OUT / f"f_{k:05d}.jpg").write_bytes(base64.b64decode(frames[j][1]))
        k += 1
    (OUT / "shots.json").write_text(json.dumps(
        {"fps": fps, "width": width, "height": height, "seconds": round(total, 2),
         "captured": len(frames), "written": k, "beats": beats}, indent=2), encoding="utf-8")
    print(f"  captured {len(frames)} screencast frames over {total:.1f} s")
    print(f"  wrote {k} frames at {fps} fps -> {OUT.relative_to(ROOT)}")
    return k, total


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=1000)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--port", type=int, default=9333)
    a = ap.parse_args(argv)
    if not PAGE.exists():
        print("Build the page first:  python -m web.build_console")
        return 1
    if not CHROME.exists():
        print(f"Chrome not found at {CHROME}")
        return 1
    profile = tempfile.mkdtemp(prefix="lunaxx_film_")
    proc = subprocess.Popen(
        [str(CHROME), f"--remote-debugging-port={a.port}", f"--user-data-dir={profile}",
         "--no-first-run", "--no-default-browser-check", "--disable-extensions",
         "--hide-crash-restore-bubble", "--autoplay-policy=no-user-gesture-required",
         f"--window-size={a.width},{a.height + 120}", "--window-position=0,0", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        asyncio.run(record(a.port, a.width, a.height, a.fps, a.quality))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
