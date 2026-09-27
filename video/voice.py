"""Speak every beat of script.py with a Microsoft neural voice, one file per beat.

    python -m video.voice            # -> video/dist/voice/<nn>.wav + voice.json

Needs the `edge-tts` package and a network connection (the voice is synthesised by Microsoft's
speech service; only the narration text is sent). It is a production tool for the explainer, and
nothing on the demo path imports it.

voice.json records, per beat, the audio length and the time each spoken word starts, so the
picture can hold each scene for exactly its line and the captions can follow the voice.
"""
from __future__ import annotations

import asyncio
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from video.script import BEATS, RATE, VOICE          # noqa: E402

OUT = HERE / "dist" / "voice"


async def speak(i: int, text: str) -> dict:
    import edge_tts
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    mp3, words = bytearray(), []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            mp3.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            words.append({"t": chunk["offset"] / 1e7, "d": chunk["duration"] / 1e7, "w": chunk["text"]})
    src, wav = OUT / f"{i:02d}.mp3", OUT / f"{i:02d}.wav"
    src.write_bytes(bytes(mp3))
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
                    "-ar", "48000", "-ac", "2", str(wav)], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(wav)], text=True).strip())
    return {"i": i, "file": wav.name, "seconds": round(dur, 3), "words": words}


async def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for i, b in enumerate(BEATS):
        r = await speak(i, b["say"])
        r["scene"] = b["scene"]
        out.append(r)
        print(f"  {i:02d} {b['scene']:<12} {r['seconds']:5.2f} s  {len(r['words'])} words")
    (OUT / "voice.json").write_text(json.dumps({"voice": VOICE, "rate": RATE, "beats": out}, indent=1),
                                    encoding="utf-8")
    print(f"  total speech {sum(r['seconds'] for r in out):.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
