"""Render the LunaXX explainer: timeline -> frames -> sound -> one MP4.

    python -m video.voice                  # narration, once (network)
    python -m video.record                 # live workbench clips (needs python -m web.server --port 8791)
    python -m video.render                 # -> video/dist/LunaXX_SIH26166_explainer.mp4
    python -m video.render --stills 3 20   # just a few frames, for checking a scene

Every frame is drawn by film.html as a pure function of time (FILM.seek(t)) and captured by
headless Chrome, so the picture is exact at 30 fps however slow a frame is to draw. The scene
lengths come from the measured length of each spoken line, and the clip timings from the marks
the recorder logged, so picture, voice and captions cannot drift apart.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import pathlib
import pickle
import re
import subprocess
import sys
import tempfile
import time
import wave

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = HERE / "dist"
VOICE = DIST / "voice"
CLIPS = DIST / "clips"
FRAMES = DIST / "frames"
OUT = DIST / "LunaXX_SIH26166_explainer.mp4"
CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
FPS = 30
sys.path.insert(0, str(ROOT))
from video.script import BEATS                      # noqa: E402

LEAD, TAIL = 0.35, 0.30                             # silence before / after each line, in its scene
EXTRA = {"hook": (0.9, 0.0), "title": (0.2, 0.5), "live-accept": (0.0, 0.9), "live-refuse": (0.0, 0.8),
         "live-known": (0.0, 0.6), "evidence": (0.0, 0.4), "close": (0.0, 2.6)}


# ------------------------------------------------------------------------------ data for the page
def console_blob() -> str:
    page = (ROOT / "web" / "dist" / "mission-console.html").read_text(encoding="utf-8")
    i = page.index("const D = ") + len("const D = ")
    return page[i:page.index(";\nconst $ = ", i)]


def matches() -> dict:
    """Real LoFTR matches of SAC's pair (w06), from the pipeline's saved run, normalised to [0, 1]."""
    r = pickle.load(open(ROOT / "demo_cache" / "results" / "sac_ohrc_nac_w06.pkl", "rb"))
    hs, ws = r["shape_source"][:2]
    hr, wr = r["shape_reference"][:2]
    src, ref, H = np.asarray(r["src_matches"]), np.asarray(r["ref_matches"]), np.asarray(r["H"])
    p = np.c_[src, np.ones(len(src))] @ H.T
    err = np.linalg.norm(p[:, :2] / p[:, 2:] - ref, axis=1)
    rng = np.random.default_rng(3)
    inl, out = np.where(err < 3)[0], np.where(err >= 8)[0]
    inl = rng.choice(inl, 150, replace=False)
    out = rng.choice(out, min(36, len(out)), replace=False)
    f = lambda idx: [[round(src[k, 0] / ws, 4), round(src[k, 1] / hs, 4), round(ref[k, 0] / wr, 4),
                      round(ref[k, 1] / hr, 4)] for k in idx]
    return {"inliers": f(inl), "outliers": f(out), "src_n": int(ws), "ref_n": int(wr)}


def normalised() -> dict:
    """SAC's pair at one ground scale, through core.illumination.normalize: what LoFTR is given."""
    import cv2
    from core.illumination import normalize
    from core.io_loader import load
    from web.panel import jpg
    d = ROOT / "data" / "pairs" / "sac_ohrc_nac_w06"
    src, _ = load(d / "sac_ohrc_nac_w06_source.tif")
    ref, _ = load(d / "sac_ohrc_nac_w06_ref.tif")
    src = cv2.resize(np.nan_to_num(src), ref.shape[::-1], interpolation=cv2.INTER_AREA)
    return {"src": jpg(normalize(src), q=86), "ref": jpg(normalize(np.nan_to_num(ref)), q=86)}


def word_at(words, pattern, fallback):
    for w in words:
        if re.search(pattern, w["w"]):
            return w["t"]
    return fallback


def fit(rect, margin=1.12, zmax=2.2):
    x, y, w, h = rect
    z = min(1920 / (w * margin), 1080 / (h * margin), zmax)
    return {"cx": x + w / 2, "cy": y + h / 2, "z": round(z, 3)}


def union(*rs):
    x0 = min(r[0] for r in rs); y0 = min(r[1] for r in rs)
    x1 = max(r[0] + r[2] for r in rs); y1 = max(r[1] + r[3] for r in rs)
    return [x0, y0, x1 - x0, y1 - y0]


def clip_plan(name, meta, dur, words):
    """Map scene time to clip time, and frame the clip with a camera."""
    m, R = meta["marks"], meta["rects"]
    end = m["end"]
    if name == "accept":
        align = word_at(words, r"^Accepted", 11) - 0.15
        pre, wait = m["click"] + 0.7, m["done"] - m["click"] - 0.7
        w_out = max(1.2, align - pre)
        plan = [dict(o0=0, o1=pre, c0=0, c1=pre),
                dict(o0=pre, o1=pre + w_out, c0=pre, c1=m["done"], badge=True),
                dict(o0=pre + w_out, o1=dur, c0=m["done"], c1=min(end, m["done"] + dur - pre - w_out))]
        top = [R["verdict"][0], R["verdict"][1], R["verdict"][2], R["facts"][1] - R["verdict"][1]]
        cam = [dict(t=pre + .2, cx=1250, cy=560, z=1.1, d=1.5),
               dict(t=pre + w_out + .05, **fit(union(R["plate"], top), 1.08), d=1.0),
               dict(t=pre + w_out + 3.2, **fit(R["plate"], 1.06), d=1.4)]
    elif name == "refuse":
        align = word_at(words, r"^refuses", 6) - 0.1
        pre, wait = m["click"] + 0.5, m["done"] - m["click"] - 0.5
        hold = max(0.0, align - pre - wait)
        w_out = max(0.8, min(wait, align - pre))
        plan = [dict(o0=0, o1=hold, c0=0, c1=0), dict(o0=hold, o1=hold + pre, c0=0, c1=pre),
                dict(o0=hold + pre, o1=hold + pre + w_out, c0=pre, c1=m["done"], badge=True),
                dict(o0=hold + pre + w_out, o1=dur, c0=m["done"], c1=min(end, m["done"] + dur - hold - pre - w_out))]
        t_done = hold + pre + w_out
        top = [R["verdict"][0], R["verdict"][1], R["verdict"][2], 330]
        cam = [dict(t=t_done + .05, **fit(union(R["plate"], top), 1.08), d=1.0)]
    else:                                                     # known
        align = word_at(words, r"^measures", 8) - 0.2
        s1, s2 = m["sliders"], m["click"] + 0.5 - m["sliders"]
        s3, s4 = m["done"] - m["click"] - 0.5, m["known"] - m["done"]
        o3 = max(1.0, min(s3, align - s1 * 0.55 - s2 - s4))
        o1 = max(s1 * 0.55, min(s1, align - s2 - o3 - s4))
        t = [0, o1, o1 + s2, o1 + s2 + o3, o1 + s2 + o3 + s4]
        plan = [dict(o0=t[0], o1=t[1], c0=0, c1=s1),
                dict(o0=t[1], o1=t[2], c0=s1, c1=s1 + s2),
                dict(o0=t[2], o1=t[3], c0=s1 + s2, c1=m["done"], badge=True),
                dict(o0=t[3], o1=t[4], c0=m["done"], c1=m["known"]),
                dict(o0=t[4], o1=dur, c0=m["known"], c1=min(end, m["known"] + dur - t[4]))]
        cam = [dict(t=max(0, t[1] - .5), **fit(R["preview"], 1.25, 1.9), d=1.0),
               dict(t=t[2] - .1, cx=960, cy=540, z=1.0, d=.8),
               dict(t=t[4] - .3, **fit(R["known"], 1.06), d=1.0)]
    for g in plan:
        g["badge"] = bool(g.get("badge"))
    return {"name": name, "frames": meta["frames"], "plan": plan, "cam": cam}


def timeline() -> dict:
    v = json.loads((VOICE / "voice.json").read_text(encoding="utf-8"))["beats"]
    clips = json.loads((CLIPS / "clips.json").read_text(encoding="utf-8"))
    out, t = [], 0.0
    for b, vb in zip(BEATS, v):
        pre, post = EXTRA.get(b["scene"], (0, 0))
        voice = LEAD + pre
        dur = voice + vb["seconds"] + TAIL + post
        words = [{"t": round(voice + w["t"], 3), "d": w["d"], "w": w["w"]} for w in vb["words"]]
        e = {"scene": b["scene"], "start": round(t, 3), "dur": round(dur, 3), "voice": voice,
             "vdur": vb["seconds"], "words": words, "cap": b["cap"], "wav": vb["file"]}
        if b["scene"].startswith("live-"):
            name = b["scene"][5:]
            e["clip"] = clip_plan(name, clips[name], dur, words)
        out.append(e)
        t += dur
    return {"scenes": out, "duration": round(t, 3), "fps": FPS}


def write_data(tl) -> pathlib.Path:
    p = DIST / "data.js"
    p.write_text("window.D=" + console_blob() + ";\nwindow.X=" + json.dumps({"matches": matches(), "norm": normalised()})
                 + ";\nwindow.TL=" + json.dumps(tl) + ";\n", encoding="utf-8")
    return p


# ------------------------------------------------------------------------------ frames
async def capture(times, port=9345, into=FRAMES, quality=92, hash_=""):
    import urllib.request
    import websockets
    prof = tempfile.mkdtemp(prefix="lunaxx_film_")
    chrome = subprocess.Popen([str(CHROME), "--headless=new", f"--remote-debugging-port={port}", f"--user-data-dir={prof}",
                               "--no-first-run", "--hide-scrollbars", "--allow-file-access-from-files",
                               "--force-device-scale-factor=1", "--window-size=1920,1080", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(80):
            try:
                tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2).read())
                page = next(x for x in tabs if x["type"] == "page")
                break
            except Exception:
                await asyncio.sleep(.25)
        async with websockets.connect(page["webSocketDebuggerUrl"], max_size=256 * 1024 * 1024) as ws:
            n = [0]

            async def send(method, **params):
                n[0] += 1
                await ws.send(json.dumps({"id": n[0], "method": method, "params": params}))
                while True:
                    m = json.loads(await ws.recv())
                    if m.get("id") == n[0]:
                        if "error" in m:
                            raise RuntimeError(f"{method}: {m['error']}")
                        return m.get("result", {})

            async def js(expr):
                r = await send("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
                if r.get("exceptionDetails"):
                    raise RuntimeError(json.dumps(r["exceptionDetails"])[:1500])
                return r.get("result", {}).get("value")

            await send("Page.enable")
            await send("Runtime.enable")
            await send("Emulation.setDeviceMetricsOverride", width=1920, height=1080, deviceScaleFactor=1, mobile=False)
            await send("Page.navigate", url=(HERE / "film.html").resolve().as_uri() + hash_)
            for _ in range(240):
                await asyncio.sleep(.5)
                try:
                    if await js("typeof FILM !== 'undefined' && FILM.ready.then(() => true)"):
                        break
                except RuntimeError as e:
                    if "FILM" not in str(e):
                        raise
            into.mkdir(parents=True, exist_ok=True)
            t0 = time.perf_counter()
            for k, (name, T) in enumerate(times):
                await js(f"FILM.seek({T:.4f})")
                shot = await send("Page.captureScreenshot", format="jpeg", quality=quality)
                (into / name).write_bytes(base64.b64decode(shot["data"]))
                if k and k % 150 == 0:
                    el = time.perf_counter() - t0
                    print(f"  frame {k}/{len(times)}  {el:.0f} s, ~{el / k * (len(times) - k):.0f} s left", flush=True)
    finally:
        chrome.kill()


# ------------------------------------------------------------------------------ sound
def read_wav(p):
    with wave.open(str(p), "rb") as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels()), w.getframerate()


def pad_music(seconds, sr=48000, seed=11):
    """A quiet, slow, warm pad: four chords, soft attack, long release, a little air."""
    n = int(seconds * sr)
    t = np.arange(n) / sr
    out = np.zeros((n, 2), np.float32)
    # A minor - F major - C major - G major, low voicings (Hz)
    chords = [(110.0, 164.81, 220.0, 261.63), (87.31, 130.81, 174.61, 220.0),
              (65.41, 130.81, 164.81, 196.0), (98.0, 146.83, 196.0, 246.94)]
    seg = 8.0
    rng = np.random.default_rng(seed)
    for k in range(int(np.ceil(seconds / seg)) + 1):
        c = chords[k % 4]
        a, b = max(0, int((k * seg - 1.5) * sr)), min(n, int(((k + 1) * seg + 2.5) * sr))
        if a >= n:
            break
        tt = t[a:b] - k * seg
        env = np.clip((tt + 1.5) / 2.5, 0, 1) * np.clip(((seg + 2.5) - tt) / 3.0, 0, 1)
        env = env ** 1.6
        for i, f in enumerate(c):
            for det, pan in ((-0.6, 0.35), (0.6, 0.65)):
                ph = rng.uniform(0, 2 * np.pi)
                wv = np.sin(2 * np.pi * (f + det) * tt + ph) + 0.18 * np.sin(2 * np.pi * 2 * (f + det) * tt + ph)
                g = env * (0.9 - 0.12 * i) * (1 + 0.15 * np.sin(2 * np.pi * 0.07 * tt + i))
                out[a:b, 0] += (wv * g * (1 - pan)).astype(np.float32)
                out[a:b, 1] += (wv * g * pan).astype(np.float32)
    # soft low-pass (one-pole) and a short diffuse reverb from decaying noise
    from scipy.signal import lfilter
    for ch in range(2):
        out[:, ch] = lfilter([0.06], [1, -0.94], out[:, ch]).astype(np.float32)
    ir_n = int(1.8 * sr)
    ir = rng.standard_normal((ir_n, 2)).astype(np.float32) * np.exp(-np.arange(ir_n) / (0.45 * sr))[:, None]
    ir /= np.sqrt((ir ** 2).sum(0))
    from numpy.fft import irfft, rfft
    L = 1 << int(np.ceil(np.log2(n + ir_n)))
    wet = np.stack([irfft(rfft(out[:, c], L) * rfft(ir[:, c], L), L)[:n] for c in range(2)], 1)
    mix = 0.75 * out + 0.45 * wet
    mix /= np.sqrt(np.mean(mix ** 2)) + 1e-9
    fade = np.clip(t / 2.5, 0, 1) * np.clip((seconds - t) / 3.0, 0, 1)
    return (mix * fade[:, None]).astype(np.float32)


def audio(tl, music=True) -> pathlib.Path:
    sr, total = 48000, tl["duration"]
    n = int(total * sr) + sr
    voice = np.zeros((n, 2), np.float32)
    for e in tl["scenes"]:
        a, r = read_wav(VOICE / e["wav"])
        assert r == sr
        if a.shape[1] == 1:
            a = np.repeat(a, 2, 1)
        k = int((e["start"] + e["voice"]) * sr)
        voice[k:k + len(a)] += a[: n - k]
    out = voice.copy()
    if music:
        m = pad_music(n / sr, sr)
        # duck the pad under the voice: follow the voice envelope with a slow release
        env = np.abs(voice).max(1)
        win = int(0.25 * sr)
        c = np.concatenate([[0.0], np.cumsum(env, dtype=np.float64)])     # moving mean, O(n)
        lo = np.clip(np.arange(n) - win // 2, 0, n); hi = np.clip(np.arange(n) + win // 2, 0, n)
        env = ((c[hi] - c[lo]) / np.maximum(hi - lo, 1)).astype(np.float32)
        duck = 1 - 0.7 * np.clip(env / (env.max() * 0.12 + 1e-9), 0, 1)
        out += m * duck[:, None] * 0.032
    p = DIST / ("mix.wav" if music else "mix_voice_only.wav")
    pcm = np.clip(out, -1, 1)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((pcm * 32767).astype(np.int16).tobytes())
    return p


def encode(tl, wav: pathlib.Path, out: pathlib.Path):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(FPS),
                    "-i", str(FRAMES / "f_%05d.jpg"), "-i", str(wav),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-profile:v", "high", "-movflags", "+faststart",
                    "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", str(out)], check=True)


def srt(tl) -> pathlib.Path:
    def ts(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}".replace(",1000", ",999")
    lines, k = [], 1
    for e in tl["scenes"]:
        a = e["start"] + e["voice"]; b = a + e["vdur"]
        lines += [str(k), f"{ts(a)} --> {ts(b)}", e["cap"], ""]; k += 1
    p = DIST / "LunaXX_SIH26166_explainer.srt"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--skip-frames", action="store_true")
    ap.add_argument("--thumb", type=float, help="write a caption-free 1280x720 thumbnail at this time")
    a = ap.parse_args(argv)
    tl = timeline()
    write_data(tl)
    print(f"  timeline {tl['duration']:.1f} s, {len(tl['scenes'])} scenes")
    for e in tl["scenes"]:
        print(f"    {e['start']:6.2f}  {e['dur']:5.2f}  {e['scene']}")
    if a.thumb is not None:
        asyncio.run(capture([("thumb_full.jpg", a.thumb)], into=DIST, quality=95, hash_="#nocap"))
        from PIL import Image
        Image.open(DIST / "thumb_full.jpg").resize((1280, 720), Image.LANCZOS).save(DIST / "LunaXX_thumbnail.jpg", quality=92)
        print(f"  wrote {DIST / 'LunaXX_thumbnail.jpg'}")
        return 0
    if a.stills is not None:
        d = DIST / "stills"
        asyncio.run(capture([(f"s_{T:07.2f}.jpg", T) for T in a.stills], into=d))
        print(f"  stills in {d}")
        return 0
    if not a.skip_frames:
        nf = int(tl["duration"] * FPS)
        if a.t0 == 0:
            for f in FRAMES.glob("f_*.jpg"):
                f.unlink()
        start = int(a.t0 * FPS)
        stop = nf if a.t1 is None else min(nf, int(a.t1 * FPS) + 1)
        asyncio.run(capture([(f"f_{k:05d}.jpg", k / FPS) for k in range(start, stop)]))
    wav = audio(tl, music=True)
    encode(tl, wav, OUT)
    wav2 = audio(tl, music=False)
    encode(tl, wav2, OUT.with_name(OUT.stem + "_voice_only.mp4"))
    print(f"  wrote {OUT} and {srt(tl).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
