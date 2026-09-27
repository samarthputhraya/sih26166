"""Record the live workbench doing real registrations, as frames, for the explainer.

    python -m web.server --port 8791          # in another terminal
    python -m video.record                    # -> video/dist/clips/<name>/f_*.jpg + clips.json

Headless Chrome at 1280 x 720 CSS pixels and 1.5x density, so every frame is 1920 x 1080 and the
interface reads large on a phone. The page gets a drawn cursor (a headless screencast has none),
and each clip logs when its run was started and when the result arrived, so render.py can speed
through the wait without touching the moments that matter. Every run in these clips is real:
core.pipeline.run_all on this laptop's CPU.
"""
from __future__ import annotations

import asyncio
import base64
import json
import pathlib
import subprocess
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "dist" / "clips"
CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
URL = "http://127.0.0.1:8791/"
FPS = 30
W, H, DPR = 1280, 720, 1.5

CURSOR = r"""
(() => {
  if (window.__cur) return;
  const c = document.createElement('div');
  c.innerHTML = '<svg width="30" height="30" viewBox="0 0 30 30"><path d="M5 3 L5 24 L10.5 18.6 L14.6 27.5 L18.2 26 L14.1 17.2 L21.6 17.2 Z" fill="#fff" stroke="#111" stroke-width="1.7" stroke-linejoin="round"/></svg>';
  c.style.cssText = 'position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none;filter:drop-shadow(0 2px 3px rgba(0,0,0,.45));transform:translate(700px,420px)';
  const ring = document.createElement('div');
  ring.style.cssText = 'position:fixed;left:0;top:0;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 2px rgba(0,0,0,.35);z-index:2147483646;pointer-events:none;opacity:0';
  document.documentElement.append(ring, c);
  let x = 700, y = 420;
  const ease = t => t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2;
  window.__cur = {
    at: () => [x, y],
    move(tx, ty, ms = 700) {
      const x0 = x, y0 = y, t0 = performance.now();
      return new Promise(res => { const f = now => { const p = Math.min(1, (now - t0) / ms), q = ease(p);
        x = x0 + (tx - x0) * q; y = y0 + (ty - y0) * q; c.style.transform = `translate(${x}px,${y}px)`;
        if (p < 1) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); });
    },
    async to(el, fx = .5, fy = .5, ms = 700) {
      if (typeof el === 'string') el = document.querySelector(el);
      const r = el.getBoundingClientRect(); await this.move(r.left + r.width * fx, r.top + r.height * fy, ms); return el;
    },
    pulse() {
      ring.style.transition = 'none'; ring.style.opacity = '1'; ring.style.transform = `translate(${x}px,${y}px) scale(.4)`;
      requestAnimationFrame(() => { ring.style.transition = 'transform .45s ease-out, opacity .45s ease-out';
        ring.style.transform = `translate(${x}px,${y}px) scale(1.3)`; ring.style.opacity = '0'; });
    },
    async click(el, fx = .5, fy = .5, ms = 700) { el = await this.to(el, fx, fy, ms); this.pulse(); await new Promise(r => setTimeout(r, 180)); el.click(); return el; },
    async hover(el, fx = .5, fy = .5, ms = 600) { el = await this.to(el, fx, fy, ms);
      el.dispatchEvent(new PointerEvent('pointerover', {bubbles: true})); return el; },
  };
})();
"""


class Tab:
    def __init__(self, ws):
        self.ws, self.n, self.frames, self.recording = ws, 0, [], False
        self.pending = {}

    async def pump(self):
        async for raw in self.ws:
            m = json.loads(raw)
            if m.get("method") == "Page.screencastFrame":
                p = m["params"]
                if self.recording:
                    self.frames.append((time.perf_counter(), p["data"]))
                await self.ws.send(json.dumps({"id": 10 ** 9 + p["sessionId"], "method": "Page.screencastFrameAck",
                                               "params": {"sessionId": p["sessionId"]}}))
            elif "id" in m and m["id"] in self.pending:
                self.pending.pop(m["id"]).set_result(m)

    async def send(self, method, **params):
        self.n += 1
        fut = asyncio.get_running_loop().create_future()
        self.pending[self.n] = fut
        await self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        m = await fut
        if "error" in m:
            raise RuntimeError(f"{method}: {m['error']}")
        return m.get("result", {})

    async def js(self, expr, wait=True):
        r = await self.send("Runtime.evaluate", expression=expr, awaitPromise=wait, returnByValue=True)
        if r.get("exceptionDetails"):
            raise RuntimeError(f"JS failed: {r['exceptionDetails'].get('exception', {}).get('description', r)}")
        return r.get("result", {}).get("value")

    async def until(self, expr, timeout=120.0, step=0.25):
        end = time.perf_counter() + timeout
        while time.perf_counter() < end:
            if await self.js(expr):
                return True
            await asyncio.sleep(step)
        raise TimeoutError(expr)


WARM = ("sac_ohrc_nac_w06", "site_tc_morning_mi1548_w01")


async def fresh(tab):
    import urllib.request
    for pid in WARM:                         # the source thumbnails of big OHRC files take seconds
        for side in ("", "_source"):
            urllib.request.urlopen(f"{URL}api/thumb/{pid}{side}.jpg", timeout=120).read()
    await tab.send("Page.navigate", url=URL)
    await asyncio.sleep(1.0)
    await tab.until("typeof B !== 'undefined' && B.live && B.lib.length > 100", 60)
    await tab.js(CURSOR)
    await asyncio.sleep(1.2)


async def scroll_deck_to_library(tab):
    await tab.js("(() => { const d = document.querySelector('.deck'); d.scrollTop = document.querySelector('.libh').offsetTop - 16; })()")
    await asyncio.sleep(1.5)                     # thumbnails load


async def rect(tab, sel):
    """[x, y, w, h] of the first match, in frame pixels (CSS px x DPR)."""
    r = await tab.js(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); if (!e) return null;"
                     f" const r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }})()")
    return [round(v * DPR, 1) for v in r] if r else None


async def clip_accept(tab, mark):
    await fresh(tab)
    await scroll_deck_to_library(tab)
    await tab.js("(() => { const b = [...document.querySelectorAll('#chips button')].find(b => /OHRC → NAC/.test(b.textContent)); b.click(); })()")
    await asyncio.sleep(1.5)
    await tab.js("document.querySelector('.deck').scrollTop = document.querySelector('.libh').offsetTop - 16")
    mark("start")
    await asyncio.sleep(1.0)
    await tab.js("__cur.click('#lib button[data-id=\"sac_ohrc_nac_w06\"]', .5, .45, 900)")
    mark("click")
    await tab.until("!document.querySelector('#result').hidden", 180)
    mark("done")
    mark.rects.update(plate=await rect(tab, "#bview .plate"), verdict=await rect(tab, "#bview .verdict"),
                      facts=await rect(tab, "#bview .facts"))
    await asyncio.sleep(1.4)
    await tab.js("__cur.hover(document.querySelectorAll('#bview .cell')[27], .5, .5, 900)")
    await asyncio.sleep(1.8)
    await tab.js("__cur.hover(document.querySelectorAll('#bview .cell')[32], .5, .5, 800)")
    await asyncio.sleep(1.8)
    await tab.js("__cur.to('#bview .vword', .3, .5, 900)")
    await asyncio.sleep(4.0)
    mark("end")


async def clip_refuse(tab, mark):
    await fresh(tab)
    await scroll_deck_to_library(tab)
    mark("start")
    await asyncio.sleep(0.8)
    await tab.js("__cur.click([...document.querySelectorAll('#chips button')].find(b => /MI 1548/.test(b.textContent)), .5, .5, 900)")
    await asyncio.sleep(0.9)
    await tab.js("__cur.click('#lib button[data-id=\"site_tc_morning_mi1548_w01\"]', .5, .45, 800)")
    mark("click")
    await tab.until("!document.querySelector('#result').hidden", 180)
    mark("done")
    mark.rects.update(plate=await rect(tab, "#bview .plate"), verdict=await rect(tab, "#bview .verdict"))
    await asyncio.sleep(1.2)
    await tab.js("__cur.to('#bview .vword', .35, .6, 900)")
    await asyncio.sleep(2.2)
    await tab.js("__cur.hover(document.querySelectorAll('#bview .cell')[20], .5, .5, 900)")
    await asyncio.sleep(3.5)
    mark("end")


async def clip_known(tab, mark):
    await fresh(tab)
    mark("start")
    await asyncio.sleep(0.5)
    await tab.js("__cur.click('#tabKnown', .5, .5, 800)")
    await asyncio.sleep(0.3)
    await tab.js("__cur.to('#dropK', .5, .55, 700)")
    # a real Chandrayaan-2 OHRC window stands in for "any Moon picture"; dropped as a PNG file
    await tab.js("""(async () => {
        const src = D.maps[0].layers.find(l => l.k === 'src').img;
        const im = new Image(); im.src = src; await im.decode();
        const c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight;
        c.getContext('2d').drawImage(im, 0, 0);
        const blob = await new Promise(r => c.toBlob(r, 'image/png'));
        const f = new File([blob], 'moon_crater.png', {type: 'image/png'});
        const dt = new DataTransfer(); dt.items.add(f);
        const inp = document.querySelector('#fileK'); inp.files = dt.files; inp.dispatchEvent(new Event('change'));
        __cur.pulse();
    })()""")
    await asyncio.sleep(0.9)
    await tab.js("document.querySelector('.deck').scrollTo({top: document.querySelector('#kprev').offsetTop - 60, behavior: 'smooth'})")
    await asyncio.sleep(0.8)
    mark("sliders")
    # move the rotation and scale sliders by hand, and the preview follows
    for sid, a, b in (("#k_rot", 8, 17), ("#k_scale", 1.1, 1.22)):
        await tab.js(f"__cur.to('{sid}', {0.5}, .5, 500)")
        await tab.js(f"""(async () => {{ const s = document.querySelector('{sid}'), a = {a}, b = {b}, t0 = performance.now();
            await new Promise(res => {{ const f = now => {{ const p = Math.min(1, (now - t0) / 1000);
              s.value = a + (b - a) * p; s.dispatchEvent(new Event('input'));
              const r = s.getBoundingClientRect(), fr = (s.value - s.min) / (s.max - s.min);
              __cur.move(r.left + r.width * fr, r.top + r.height / 2, 1);
              if (p < 1) requestAnimationFrame(f); else res(); }}; requestAnimationFrame(f); }}); }})()""")
    mark.rects.update(preview=await rect(tab, "#kprev"))
    await asyncio.sleep(0.4)
    await tab.js("__cur.click('#goKnown', .3, .5, 700)")
    mark("click")
    await tab.until("!document.querySelector('#result').hidden", 180)
    mark("done")
    await asyncio.sleep(0.5)
    await tab.js("""(() => { const sp = document.querySelector('#stagep'), k = document.querySelector('#bview .known');
        sp.scrollTo({top: k.getBoundingClientRect().top - sp.getBoundingClientRect().top + sp.scrollTop - 30, behavior: 'smooth'}); })()""")
    await asyncio.sleep(1.3)
    mark("known")
    mark.rects.update(known=await rect(tab, "#bview .known"), kbig=await rect(tab, "#bview .kbig"))
    await tab.js("__cur.to('#bview .kbig', .25, .4, 800)")
    await asyncio.sleep(3.2)
    await tab.js("""(() => { const sp = document.querySelector('#stagep'), k = document.querySelector('#bview .dl');
        sp.scrollTo({top: k.getBoundingClientRect().top - sp.getBoundingClientRect().top + sp.scrollTop - 220, behavior: 'smooth'}); })()""")
    await asyncio.sleep(1.1)
    mark("download")
    mark.rects.update(dl=await rect(tab, "#bview .dl"))
    await tab.js("__cur.to('#bview .dl a', .5, .5, 800)")
    await asyncio.sleep(2.2)
    mark("end")


CLIPS = {"accept": clip_accept, "refuse": clip_refuse, "known": clip_known}


async def record_all(port: int, names):
    import urllib.request
    import websockets
    for _ in range(80):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2).read())
            page = next(t for t in tabs if t["type"] == "page")
            break
        except Exception:
            await asyncio.sleep(0.25)
    else:
        raise SystemExit("Chrome never exposed a debugging target")
    meta = {}
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=256 * 1024 * 1024) as ws:
        tab = Tab(ws)
        pump = asyncio.create_task(tab.pump())
        await tab.send("Page.enable")
        await tab.send("Runtime.enable")
        # All three are needed for 1080p frames from a 1280-wide layout: headless Chrome's
        # screencast ignores deviceScaleFactor unless the process itself runs at that density.
        await tab.send("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=DPR,
                       mobile=False, screenWidth=int(W * DPR), screenHeight=int(H * DPR))
        await tab.send("Page.startScreencast", format="jpeg", quality=88, everyNthFrame=1,
                       maxWidth=int(W * DPR), maxHeight=int(H * DPR))
        for name in names:
            marks = {}
            tab.frames, tab.recording = [], False
            t0 = [None]

            def mark(k):
                now = time.perf_counter()
                if k == "start":
                    t0[0] = now
                    tab.frames.clear()
                    tab.recording = True
                marks[k] = round(now - t0[0], 3)
            mark.rects = {}

            await CLIPS[name](tab, mark)
            tab.recording = False
            frames = list(tab.frames)
            if not frames:
                raise SystemExit(f"{name}: no frames")
            d = OUT / name
            d.mkdir(parents=True, exist_ok=True)
            for f in d.glob("f_*.jpg"):
                f.unlink()
            total = marks["end"]
            step, k, j, base = 1.0 / FPS, 0, 0, t0[0]
            while k * step <= total:
                want = base + k * step
                while j + 1 < len(frames) and frames[j + 1][0] <= want:
                    j += 1
                (d / f"f_{k:05d}.jpg").write_bytes(base64.b64decode(frames[j][1]))
                k += 1
            meta[name] = {"frames": k, "fps": FPS, "marks": marks, "rects": mark.rects,
                          "captured": len(frames), "size": [int(W * DPR), int(H * DPR)]}
            print(f"  {name}: {k} frames ({len(frames)} captured), marks {marks}")
        await tab.send("Page.stopScreencast")
        pump.cancel()
    OUT.mkdir(parents=True, exist_ok=True)
    prev = json.loads((OUT / "clips.json").read_text(encoding="utf-8")) if (OUT / "clips.json").exists() else {}
    prev.update(meta)
    (OUT / "clips.json").write_text(json.dumps(prev, indent=1), encoding="utf-8")


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", default=list(CLIPS))
    ap.add_argument("--port", type=int, default=9333)
    a = ap.parse_args(argv)
    prof = tempfile.mkdtemp(prefix="lunaxx_rec_")
    chrome = subprocess.Popen([str(CHROME), "--headless=new", f"--remote-debugging-port={a.port}",
                               f"--user-data-dir={prof}", "--no-first-run", "--hide-scrollbars",
                               f"--force-device-scale-factor={DPR}",
                               f"--window-size={int(W * DPR)},{int(H * DPR)}", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        asyncio.run(record_all(a.port, a.names))
    finally:
        chrome.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
