# Mission Console — narration script

**Audience:** SAC / ISRO image-processing scientists and the SIH evaluation panel. Assume they
know photogrammetry and will check every number. Do not explain what a homography is; do explain
what *we* did and what we refused to claim.

**Running time:** ~1 min 48 s of picture (16 beats). Read at a steady pace — roughly 145 words a
minute. Each beat below is keyed to `web/film.py`'s `BEATS` list and to `shots.json`, so the
voice and the picture stay in step without anyone counting seconds by hand.

**Rules this script obeys**, the same ones the deck obeys:
- Every number appears in `REPORT.md` at freeze commit `7dd4e5b`.
- *Cross-sensor* means different instruments. *Multi-modal* means visible ↔ infrared or elevation.
- A held-out residual is never called accuracy against truth.
- Nothing is claimed that the page does not show on screen at that moment.

---

### 1 · open — 7 s

Every image-matching system can produce a number. The question a landing-site engineer actually
has to answer is different: *can I trust this one?* This is Team LunaXX's answer for problem
statement SIH 26166 — lunar image registration that knows when it is wrong.

### 2 · telemetry — 5 s

These six figures are not a summary we wrote. Every one of them is read back from our evidence
logs at a single frozen commit, and one command regenerates all of them from scratch.

### 3 · sun-arrive — 4 s

Start with the hardest thing about the Moon: the Sun moves, and when it does, the surface stops
looking like itself.

### 4 · sun-sweep — 11 s

This is the real elevation of our study site at seventy-four degrees south, from LOLA, at true
vertical scale, lit at the seven-degree Sun elevation of our Chandrayaan-2 OHRC frame. Watch the
shadows as the second Sun moves. Every edge a matcher depends on slides, shortens, and eventually
inverts. Beside it, the panel is not an illustration — those are our real OHRC-to-NAC windows in
whichever azimuth band is dialled.

### 5 · sun-hard-band — 5 s

Past sixty degrees, we register almost nothing. That is the honest result. But look at the last
row in every band: a failure the system did not catch. Zero, throughout.

### 6 · trust-arrive — 5 s

So how does it know? Every result carries a verdict, and the verdict is about the *pair* — never
about how sharp either picture is.

### 7 · trust-accepted — 8 s

Chandrayaan-2 OHRC against LRO NAC. Different instruments, different missions, and Sun azimuths
one hundred and seventy-four degrees apart — every shadow reversed. Blink between them and nothing
jumps. Fifty-eight of sixty-four regions verified. Two independent lines of evidence agree: the
matches, and the pixels.

### 8 · trust-refused — 9 s

Now one it refuses. Kaguya's Terrain Camera against its Multiband Imager at one-five-four-eight
nanometres — visible light against near-infrared. The matcher found thirty-five correspondences in
the whole frame, and this is the transform it built from them. It is visibly wrong. An area check
that never looks at the matches caught that, and the system refused to ship it.

### 9 · trust-band-test — 8 s

And here is why that refusal is a scientific result rather than a failure. The same source image,
against two bands of the same map product, on the same fourteen-point-eight metre grid. At seven
hundred and forty-nine nanometres: three hundred and thirty-four matches, accepted. At fifteen
forty-eight: thirty-five, refused. The wavelength changed, not the resolution.

### 10 · trust-iirs — 6 s

The same honesty applies to IIRS. Ten of eleven windows refused, none registers. We report that as
a limit of the method, not as a number we massaged into looking like success.

### 11 · tiling — 7 s

A fair reviewer asks whether we chose the windows that worked. So we stopped choosing. This is
every non-overlapping window the cutter finds in the shared, lit, textured overlap — thirty-seven
of them, thirteen square kilometres, selected before any matching ran. Thirty-seven of
thirty-seven accepted.

### 12 · calibration — 8 s

Then we tried to fool it. We shift the correct answer by a known distance and plant matches that
agree with the wrong answer perfectly, so nothing the matcher reports could reveal it. At zero
metres it must stay silent, and it does — no false alarms in sixty trials. From five metres it
catches every one. Below three metres it cannot see the error, and that floor is stated, not
hidden.

### 13 · pipeline — 6 s

The pipeline itself is ordinary and deliberately so: one ground scale, illumination reduced to
gradient orientation, LoFTR, sub-pixel refinement, MAGSAC++. The unusual part is the box beneath
it — an area check that never uses match positions, so it can disagree with the matcher.

### 14 · results — 7 s

This is what it registers. SAC's own published benchmark pair. A twenty-nine-times scale gap.
Three-image loops closing to a tenth of a metre. All of it on public data, on a laptop CPU, with
no GPU and no network.

### 15 · refusals — 7 s

And this is what it declines. Every one of these was flagged by the system itself — not one was
found by a reviewer afterwards. For a landing-site hazard map, an alignment that is quietly wrong
is the dangerous one. Ours is loud when it is wrong.

### 16 · close — 5 s

Every figure you have seen traces to one frozen commit, and one command rebuilds all of them.
Team LunaXX, problem statement SIH 26166.

---

## Producing the audio

```
python -m web.film                    # picture: web/dist/film/frames + shots.json
python -m web.voice --key <GEMINI_KEY>  # voice:   per-beat wav, timed to shots.json
python -m web.cut                     # mux:     web/dist/mission-console.mp4
```

`web/cut.py` stretches each beat to whichever is longer, the picture or its line, so a line that
over-runs never gets cut off — the shot holds instead.

## If you record it yourself instead

Open the console, start a screen recorder, and follow the beats above in order. The page drives
the same sequence under `python -m web.film`, so you can watch that once to learn the rhythm.
Say the numbers exactly as written; every one is checkable against `REPORT.md`, and a SAC
scientist who catches one inflated figure will discount all the others.
