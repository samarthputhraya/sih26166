"""Speak every beat of script.py, one file per beat: Gemini 2.5 Pro TTS, voice Charon, Indian English.

    python -m video.voice            # -> video/dist/voice/<nn>.wav + voice.json

The same engine and voice as the FraudLens film (HHGoa task 4), directed to an Indian English
accent. Needs Google application-default credentials and a project in GOOGLE_CLOUD_PROJECT (Cloud
Text-to-Speech, falling back to Vertex AI). Only the narration text is sent. A production tool:
nothing on the demo path imports it.

Gemini returns audio without word timings, so voice.json carries estimated ones: the words are
spread over the voiced stretches of each clip by length, with every sentence and clause break
snapped to a real pause in the audio. That is what the edit keys scene cues and captions to.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import wave

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from video.script import BEATS                        # noqa: E402

OUT = HERE / "dist" / "voice"
CACHE = HERE / "dist" / "voice_cache"
VOICE, MODEL, LANG = "Charon", "gemini-2.5-pro-tts", "en-IN"
RATE = 24000
DIRECTION = ("You are narrating a premium explainer film for a panel of ISRO scientists and engineers. "
             "Speak in a natural, educated Indian English accent, like an Indian science presenter. "
             "Voice: calm, confident and warm, at a natural, measured pace, never slow or drawn out, "
             "like a great documentary narrator. Real pauses at full stops, light ones at commas. "
             "Give key numbers a little weight. Never salesy.")
TRUNCATED_DB, TAKES = -35.0, 4
TEMPO = 1.04          # 4% quicker, pitch kept: the film stays under three minutes


def _db(x) -> float:
    return float(10 * np.log10(np.mean((np.asarray(x, np.float64) / 32768) ** 2) + 1e-12))


def tail_db(pcm) -> float:
    return _db(pcm[-int(RATE * 0.05):])


def trim(pcm, lead=0.10, tail=0.30, floor_db=-50.0):
    win = int(RATE * 0.01)
    loud = [i for i in range(len(pcm) // win) if _db(pcm[i * win:(i + 1) * win]) > floor_db]
    if not loud:
        return pcm
    return pcm[max(0, loud[0] * win - int(RATE * lead)): min(len(pcm), (loud[-1] + 1) * win + int(RATE * tail))]


def tighten(pcm, longest=0.55, floor_db=-45.0, xfade=0.03):
    """Pauses longer than `longest` are shortened inside the silence, with a 30 ms crossfade."""
    win = int(RATE * 0.02)
    n = len(pcm) // win
    quiet = [_db(pcm[i * win:(i + 1) * win]) < floor_db for i in range(n)]
    cuts, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if i > 0 and j < n and (j - i) * win / RATE > longest:
                keep = int(longest * RATE)
                cuts.append((i * win + keep // 2, j * win - keep // 2))
            i = j
        else:
            i += 1
    if not cuts:
        return pcm
    x, k = pcm.astype(np.float64), int(RATE * xfade)
    out = x[: cuts[0][0]]
    for c, (a, b) in enumerate(cuts):
        nxt = x[b: cuts[c + 1][0]] if c + 1 < len(cuts) else x[b:]
        t = np.linspace(0, np.pi / 2, k)
        out = np.concatenate([out[:-k], out[-k:] * np.cos(t) + nxt[:k] * np.sin(t), nxt[k:]])
    return out.astype("<i2")


def fade(pcm, ms=12.0):
    k = min(len(pcm) // 2, int(RATE * ms / 1000))
    x = pcm.astype(np.float64)
    r = np.linspace(0.0, 1.0, k)
    x[:k] *= r
    x[-k:] *= r[::-1]
    return x.astype("<i2")


def _cloud(text, prompt):
    import google.auth
    import google.auth.transport.requests
    import requests
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    r = requests.post("https://texttospeech.googleapis.com/v1/text:synthesize", timeout=180,
                      headers={"Authorization": f"Bearer {creds.token}",
                               "x-goog-user-project": os.environ["GOOGLE_CLOUD_PROJECT"]},
                      json={"input": {"text": text, "prompt": prompt},
                            "voice": {"languageCode": LANG, "name": VOICE, "modelName": MODEL},
                            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": RATE}})
    if r.status_code != 200:
        raise RuntimeError(f"cloud-tts {r.status_code}: {r.text[:300]}")
    wav = base64.b64decode(r.json()["audioContent"])
    return np.frombuffer(wav[44:] if wav[:4] == b"RIFF" else wav, dtype="<i2").copy()


def synth(text, prompt):
    last = None
    for attempt in range(8):
        try:
            return _cloud(text, prompt)
        except Exception as e:            # noqa: BLE001 - quota and transient errors: wait and retry
            last = e
            wait = 35 + attempt * 15 if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) else 3 * 2 ** attempt
            print(f"  retry in {wait}s: {str(e)[:120]}", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"TTS failed: {last}")


def word_times(pcm, text):
    """Estimated start and length of each word.

    The clip's pauses (120 ms or longer) are found from its energy. Each clause break in the text
    (a word ending in . , ; : ? !) is assigned, in order, to the unused pause nearest where a
    length-proportional reading would put it; then the words of each span between anchors are
    spread over that span by length. A word that starts a clause therefore starts on a real
    pause, which is where the edit's cues sit."""
    win = int(RATE * 0.01)
    n = len(pcm) // win
    db = np.array([_db(pcm[i * win:(i + 1) * win]) for i in range(n)])
    voiced = db > max(-42.0, db.max() - 38)
    gaps, i = [], 0
    while i < n:
        if not voiced[i]:
            j = i
            while j < n and not voiced[j]:
                j += 1
            if i > 0 and j < n and (j - i) >= 12:
                gaps.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    on = np.where(voiced)[0]
    t0, t1 = on[0] * 0.01, (on[-1] + 1) * 0.01
    toks = text.split()
    wt = [max(1.0, len(re.sub(r"[^\w]", "", w)) ** 0.9) for w in toks]
    cum = np.concatenate([[0.0], np.cumsum(wt)])
    frac = cum / cum[-1]
    # anchors: (word index, start time of that word, end time of the previous word)
    anchors, used = [(0, t0, t0)], -1
    for k in range(1, len(toks)):
        if not re.search(r"[.,;:?!]$", toks[k - 1]):
            continue
        est = t0 + frac[k] * (t1 - t0)
        cand = [(abs(g[1] - est), gi) for gi, g in enumerate(gaps) if gi > used and g[0] > anchors[-1][1]]
        if not cand:
            continue
        dist, gi = min(cand)
        if dist < 1.2:
            used = gi
            anchors.append((k, gaps[gi][1], gaps[gi][0]))
    anchors.append((len(toks), None, t1))
    starts, ends = [0.0] * len(toks), [0.0] * len(toks)
    for (k0, s0, _), (k1, _, e1) in zip(anchors, anchors[1:]):
        span_w = cum[k1] - cum[k0]
        for k in range(k0, k1):
            starts[k] = s0 + (cum[k] - cum[k0]) / span_w * (e1 - s0)
            ends[k] = s0 + (cum[k + 1] - cum[k0]) / span_w * (e1 - s0)
    return [{"t": round(a_, 3), "d": round(max(0.05, e - a_), 3), "w": re.sub(r"[.,;:?!]+$", "", w)}
            for a_, e, w in zip(starts, ends, toks)]


def main(only) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    out = []
    for i, b in enumerate(BEATS):
        if only and b["scene"] not in only and str(i) not in only:
            prev = json.loads((OUT / "voice.json").read_text(encoding="utf-8"))["beats"][i]
            out.append(prev)
            continue
        prompt = DIRECTION + (" For this line: " + b["style"] + "." if b.get("style") else "")
        key = hashlib.sha256(json.dumps([VOICE, MODEL, LANG, prompt, b["say"]]).encode()).hexdigest()[:20]
        cached = CACHE / f"{key}.wav"
        takes = 0
        if cached.exists():
            with wave.open(str(cached)) as w:
                pcm = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").copy()
        else:
            best = None
            for takes in range(1, TAKES + 1):
                pcm = synth(b["say"], prompt)
                d = tail_db(pcm)
                if best is None or d < best[0]:
                    best = (d, pcm)
                if d < TRUNCATED_DB:
                    break
                print(f"  {b['scene']}: take {takes} ends at {d:.1f} dBFS (cut syllable), retaking", flush=True)
            pcm = best[1]
            with wave.open(str(cached), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(pcm.tobytes())
        clip = fade(tighten(trim(pcm)))
        words = [dict(w, t=round(w["t"] / TEMPO, 3), d=round(w["d"] / TEMPO, 3)) for w in word_times(clip, b["say"])]
        mono, wav = OUT / f"{i:02d}_mono.wav", OUT / f"{i:02d}.wav"
        with wave.open(str(mono), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(clip.astype("<i2").tobytes())
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mono),
                        "-af", f"atempo={TEMPO},aresample=48000:resampler=soxr", "-ac", "2", str(wav)], check=True)
        mono.unlink()
        secs = round(len(clip) / RATE / TEMPO, 3)
        out.append({"i": i, "file": wav.name, "seconds": secs, "words": words, "scene": b["scene"]})
        print(f"  {i:02d} {b['scene']:<12} {secs:5.2f} s  takes={takes}", flush=True)
    (OUT / "voice.json").write_text(json.dumps({"voice": VOICE, "model": MODEL, "lang": LANG, "beats": out}, indent=1),
                                    encoding="utf-8")
    print(f"  total speech {sum(r['seconds'] for r in out):.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
