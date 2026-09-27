# The explainer video

A 2 min 50 s narrated walkthrough of LunaXX for the SIH idea submission: the problem, the method,
three live registrations on the workbench, and the frozen evidence. Every figure in it is one the
claim-checked deck carries, from `REPORT.md` at the freeze commit `7dd4e5b`. The live runs are
real runs of `core.pipeline.run_all`; the narration never quotes their counts.

| File | What it does |
|---|---|
| `script.py` | the narration, one line per scene: what the voice says and the on-screen caption |
| `voice.py` | speaks each line with a Microsoft neural voice (`edge-tts`, needs a network), one WAV per line, with word timings |
| `record.py` | drives the live workbench in headless Chrome and records three clips at 1080p, logging when each run starts and finishes |
| `film.html` | draws every frame as a pure function of time: the motion graphics, the clips with a camera, the captions |
| `render.py` | builds the timeline from the measured lines, captures every frame, mixes voice and a quiet pad, encodes the MP4 |

```
pip install --target <somewhere> edge-tts          # production tool only, never on the demo path
python -m video.voice
python -m web.server --port 8791                   # in another terminal
python -m video.record
python -m video.render                             # -> video/dist/LunaXX_SIH26166_explainer.mp4
python -m video.render --stills 12 40              # check single frames while editing a scene
```

Outputs land in `video/dist/` (gitignored): the video, a voice-only version without the music
bed, and an `.srt` of the captions for YouTube. Scene lengths follow the spoken lines, and the
clips are re-timed so the verdict appears on the word that announces it; wherever a pipeline
run is shown faster than real time, the frame says so ("shown at ×1.4").
