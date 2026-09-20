"""Assemble the recorded frames (and the voice-over, when it exists) into one video.

    python -m web.cut                  # -> web/dist/mission-console.mp4
    python -m web.cut --silent         # picture only, ignore any audio present

Each beat is held for whichever is longer, its picture or its line, so a sentence that over-runs
is never cut off mid-word. Short beats are filled by LOOPING that beat's own frames rather than
freezing the last one: on the Sun sweep a freeze would stop the shadows dead, which is the one
thing that shot exists to show.

Needs ffmpeg on PATH. Reads `dist/film/shots.json` and, if present, `dist/film/audio/*.wav`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import wave

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FILM = HERE / "dist" / "film"
AUDIO = FILM / "audio"
OUT = HERE / "dist" / "mission-console.mp4"
GAP = 0.55                     # breath after each line before the next shot


def ffmpeg(args, **kw):
    return subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                          check=True, **kw)


def wav_seconds(p: pathlib.Path) -> float:
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--silent", action="store_true")
    ap.add_argument("--crf", type=int, default=20)
    a = ap.parse_args(argv)

    if not shutil.which("ffmpeg"):
        print("ffmpeg is not on PATH"); return 1
    shots_path = FILM / "shots.json"
    if not shots_path.exists():
        print("No frames. Run:  python -m web.film"); return 1
    shots = json.loads(shots_path.read_text(encoding="utf-8"))
    fps, beats = shots["fps"], shots["beats"]
    frames = sorted(FILM.glob("f_*.jpg"))
    if not frames:
        print("No frames on disk. Run:  python -m web.film"); return 1

    voices = {}
    if not a.silent and AUDIO.is_dir():
        for w in sorted(AUDIO.glob("*.wav")):
            label = w.stem.split("_", 1)[1] if "_" in w.stem else w.stem
            voices[label] = w
    if voices:
        print(f"  {len(voices)} voice files found")
    else:
        print("  no voice-over yet - building a silent cut")

    work = FILM / "_work"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)

    concat, audio_parts, total = [], [], 0.0
    for i, b in enumerate(beats):
        start = int(round(b["at"] * fps))
        stop = min(len(frames), int(round((b["at"] + b["dur"]) * fps)))
        own = frames[start:stop] or frames[start:start + 1]
        v = voices.get(b["label"])
        vdur = wav_seconds(v) if v else 0.0
        target = max(b["dur"], vdur + GAP if v else 0.0)
        need = max(1, int(round(target * fps)))
        for k in range(need):
            concat.append(f"file '{own[k % len(own)].as_posix()}'\nduration {1 / fps:.6f}")
        if v:
            pad = target - vdur
            sil = work / f"sil_{i:02d}.wav"
            ffmpeg(["-f", "lavfi", "-t", f"{pad:.3f}", "-i",
                    "anullsrc=channel_layout=mono:sample_rate=24000", "-c:a", "pcm_s16le", str(sil)])
            audio_parts += [v, sil]
        elif not a.silent and voices:
            sil = work / f"sil_{i:02d}.wav"
            ffmpeg(["-f", "lavfi", "-t", f"{target:.3f}", "-i",
                    "anullsrc=channel_layout=mono:sample_rate=24000", "-c:a", "pcm_s16le", str(sil)])
            audio_parts.append(sil)
        total += target
        print(f"  {b['label']:18} picture {b['dur']:5.1f}s  voice {vdur:5.1f}s  ->  {target:5.1f}s")

    concat.append(f"file '{frames[-1].as_posix()}'")          # concat demuxer wants a final entry
    lst = work / "frames.txt"
    lst.write_text("\n".join(concat) + "\n", encoding="utf-8")

    silent_mp4 = work / "picture.mp4"
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-fps_mode", "cfr", "-r", str(fps),
            "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf),
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(silent_mp4)])

    if audio_parts:
        alst = work / "audio.txt"
        alst.write_text("\n".join(f"file '{p.as_posix()}'" for p in audio_parts) + "\n",
                        encoding="utf-8")
        voice_wav = work / "voice.wav"
        ffmpeg(["-f", "concat", "-safe", "0", "-i", str(alst), "-c:a", "pcm_s16le", str(voice_wav)])
        ffmpeg(["-i", str(silent_mp4), "-i", str(voice_wav), "-c:v", "copy",
                "-c:a", "aac", "-b:a", "160k", "-shortest",
                "-movflags", "+faststart", str(OUT)])
    else:
        shutil.copy2(silent_mp4, OUT)

    shutil.rmtree(work, ignore_errors=True)
    size = OUT.stat().st_size / 1048576
    print(f"\n  {OUT.relative_to(ROOT)}  {total / 60:.1f} min  {size:.1f} MB"
          f"  {'with voice-over' if audio_parts else 'SILENT'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
