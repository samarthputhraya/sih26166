"""Speak `web/narration.md`, one WAV per beat, with Google Gemini's text-to-speech.

    set GEMINI_API_KEY=...
    python -m web.voice                       # -> web/dist/film/audio/<nn>_<label>.wav
    python -m web.voice --voice Charon --dry  # print what it would say, call nothing

One file per beat rather than one long take, because `web.cut` needs to know how long each line
actually runs in order to hold its shot for exactly that long. A single take would force the
picture to guess.

The key is read from --key or the GEMINI_API_KEY environment variable and is never written to
disk, never logged, and never committed. Pass it at the command line only if your shell does not
keep history.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import re
import struct
import sys
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "narration.md"
OUT = HERE / "dist" / "film" / "audio"
MODEL = "gemini-2.5-flash-preview-tts"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"

# Gemini returns raw signed 16-bit little-endian PCM, single channel, 24 kHz.
RATE, CHANNELS, BITS = 24000, 1, 16

STYLE = ("Read this as a measured, confident technical briefing to senior spacecraft-imaging "
         "scientists. Unhurried and plain. No salesmanship, no rising enthusiasm. Let the "
         "numbers carry the weight. Short pause at each full stop.\n\n")


def beats(path: pathlib.Path = SCRIPT):
    """[(label, text)] from the '### n - label - s' headings, in order.

    Scans the whole file for those headings rather than trying to slice the document on its
    horizontal rules: the front matter contains rules of its own, and an off-by-one there
    silently produced zero beats.
    """
    out, cur, buf = [], None, []

    def flush():
        if cur and " ".join(buf).strip():
            out.append((cur, " ".join(buf).strip()))

    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        m = re.match(r"^###\s*\d+\s*[·.]\s*([\w-]+)\s*[—-]", s)
        if m:
            flush()
            cur, buf = m.group(1), []
        elif cur is not None:
            if s.startswith("## ") or s.startswith("### "):
                flush()
                cur, buf = None, []
            elif s and not s.startswith("---"):
                buf.append(s)
    flush()
    return out


def wav(pcm: bytes) -> bytes:
    """Wrap raw PCM in a WAV header. Gemini returns headerless samples."""
    block = CHANNELS * BITS // 8
    return (b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt "
            + struct.pack("<IHHIIHH", 16, 1, CHANNELS, RATE, RATE * block, block, BITS)
            + b"data" + struct.pack("<I", len(pcm)) + pcm)


def say(text: str, key: str, voice: str) -> bytes:
    body = json.dumps({
        "contents": [{"parts": [{"text": STYLE + text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }).encode("utf-8")
    req = urllib.request.Request(ENDPOINT.format(m=MODEL, k=key), body,
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise SystemExit(f"Gemini returned HTTP {e.code}.\n{detail}") from e
    try:
        part = data["candidates"][0]["content"]["parts"][0]
        return base64.b64decode(part["inlineData"]["data"])
    except (KeyError, IndexError) as e:
        raise SystemExit(f"unexpected response shape: {json.dumps(data)[:500]}") from e


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--key", default=os.environ.get("GEMINI_API_KEY", ""))
    ap.add_argument("--voice", default="Charon",
                    help="a Gemini prebuilt voice, e.g. Charon, Kore, Puck, Fenrir")
    ap.add_argument("--dry", action="store_true", help="print the lines, call nothing")
    a = ap.parse_args(argv)

    lines = beats()
    if not lines:
        print("no beats parsed from narration.md"); return 1
    words = sum(len(t.split()) for _, t in lines)
    print(f"  {len(lines)} beats, {words} words, about {words / 145 * 60:.0f} s at 145 wpm")
    if a.dry:
        for i, (label, t) in enumerate(lines, 1):
            print(f"\n  [{i:02d}] {label}  ({len(t.split())} words)\n      {t[:150]}...")
        return 0
    if not a.key:
        print("No key. Pass --key or set GEMINI_API_KEY."); return 1

    OUT.mkdir(parents=True, exist_ok=True)
    for i, (label, text) in enumerate(lines, 1):
        path = OUT / f"{i:02d}_{label}.wav"
        pcm = say(text, a.key, a.voice)
        path.write_bytes(wav(pcm))
        secs = len(pcm) / (RATE * CHANNELS * BITS // 8)
        print(f"  [{i:02d}] {label:16} {secs:5.1f} s  ->  {path.name}")
    print(f"\n  {len(lines)} files in {OUT}")
    print("  next:  python -m web.cut")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
