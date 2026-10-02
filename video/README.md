# The explainer video

A 3 min 48 s narrated walkthrough of LunaXX for the SIH idea submission (v11, 2 Oct 2026): the
problem, the method, three live registrations on the workbench, the frozen evidence (Site N,
the Sun moved in azimuth and elevation on SAC's own frame, the checker's calibration, what it
refuses), and the published console on a phone in Hindi. Every figure in it is one the
claim-checked deck v11 carries, from `REPORT.md` at the freeze commit `51a9ad0`. The live runs are
real runs of `core.pipeline.run_all`; the narration never quotes their counts.

| File | What it does |
|---|---|
| `script.py` | the narration, one line per scene: what the voice says and the on-screen caption |
| `voice.py` | speaks each line with Gemini 2.5 Pro TTS, voice Charon, in Indian English (the FraudLens film's voice), one WAV per line, with word timings estimated from the audio's pauses |
| `record.py` | drives the live workbench in headless Chrome and records three clips at 1080p, logging when each run starts and finishes; a fourth clip records the published console on a phone |
| `film.html` | draws every frame as a pure function of time: the motion graphics, the clips with a camera, the captions |
| `render.py` | builds the timeline from the measured lines, captures every frame, mixes voice and a quiet pad, encodes the MP4 |

```
pip install --target <somewhere> google-auth       # production tool only, never on the demo path
set PYTHONPATH=<somewhere>
set GOOGLE_CLOUD_PROJECT=<project>                 # Cloud Text-to-Speech, application-default credentials
python -m video.voice
python -m web.server --port 8791                   # in another terminal
python -m video.record                             # the phone clip needs the published console online
python -m video.render                             # -> video/dist/LunaXX_SIH26166_explainer.mp4
python -m video.render --stills 12 40              # check single frames while editing a scene
python -m video.render --thumb 29                  # a caption-free 1280 x 720 thumbnail
```

Outputs land in `video/dist/` (gitignored): the video, a voice-only version without the music
bed, and an `.srt` of the captions for YouTube. Scene lengths follow the spoken lines, and the
clips are re-timed so the verdict appears on the word that announces it; wherever a pipeline
run is shown faster than real time, the frame says so ("shown at ×1.4").
