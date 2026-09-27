# The Mission Console — how to drive it

The console at `web/` is two things in one built page:

- **A workbench.** Served by `python -m web.server`, it registers images on the spot: two images
  you drop in, one image tested against a transform it chose itself, or any of the real pairs in
  `data/pairs/`, re-run live from their files. Every run is `core.pipeline.run_all` on this CPU,
  followed live, and the result can be downloaded as the full set of deliverables.
- **The evidence.** The frozen results, drawn from the evidence logs, the demo caches,
  `geometry_prior.json` and the LOLA DEM. This part never computes a number: a page that computed
  its own could disagree with `REPORT.md`, and then neither could be trusted.

Opened without the server (the published link, or `dist/index.html` double-clicked), the page
cannot run Python. It says so on the workbench, and the real pairs there open their saved runs.

It lives in `web/`, **outside `core/`, `evaluation/`, `ops/` and `app/`**, so building it can never
re-stamp an evidence row or a demo cache, and nothing the workbench runs is written anywhere.

<p align="center"><img src="preview.jpg" width="720" alt="The workbench: the pair library and drop zones on the left, and on the right the empty bench, the words 'Shadows move. The ground doesn't.' standing as relief on the 74°S LOLA terrain"></p>

### How it looks, and why

The problem is that the Moon's ground stays put while its shadows swing round it, so the page is
built from that one fact.

- **The tool comes first.** The page opens on the workbench: what to register on the left, the
  result on the right. The evidence is one link away in the bar, not a slide deck to scroll past.
- **The empty bench is terrain.** Before anything runs, the result area shows "Shadows move. The
  ground doesn't." set as a heightfield on the real 74 °S site from the LOLA DEM, lit by one low
  Sun with cast shadows. On load the Sun swings once and every shadow swings with it; dragging
  across the ground moves it after that. That sweep is the only motion that runs by itself.
- **A result is a plate.** The warped image under the 8 × 8 trust map, squares referenced A–H and
  1–8 like a chart's grid squares, with the verdict, every square's numbers, and the download.
  The same viewer draws the frozen pairs in the evidence, so a live verdict and a saved one mean
  the same thing.
- **One colour, one meaning.** Lunar grey, black and white, the colours of the imagery. The only
  hue is magenta, and it marks what the system refused. Weak squares are white hatching,
  no-evidence squares are stipple, and a verified square has nothing drawn on it.
- **Images sit in the dark, as they do in space.** The result area and the instruments use a night
  background; the controls and the reading sections use the lit ground.

In the evidence, "Line it up yourself" lets the reader drag a real pair into register while a
simplified in-browser version of the check scores each square, and says that it is simplified.
The Sun section is a polar relief of the same site with cast shadows at the OHRC frame's 7° Sun,
contours every 250 m, and a compass you drag the second Sun round.

Type is Jost alone, a revival of Futura, the typeface on the plaque Apollo 11 left on the Moon. It
is SIL OFL 1.1 and lives in `web/fonts/` with its licence; the build embeds it, so the page needs no
network at all.

---

## 1. Build it

```
python -m web.build_console
```

Takes about 20 seconds and writes **two** files:

| File | What it is | Open it how |
|---|---|---|
| `dist/index.html` | a complete HTML document | **this is the one you open by hand** — double-click it, or serve `dist/` with any static server |
| `dist/mission-console.html` | a **fragment**: no doctype, no `<meta charset>`, no viewport | only for embedding in a host page that supplies the document around it |

**Open the fragment directly and it is visibly wrong**, which is why `index.html` exists. Chrome
falls into quirks mode, decodes the file as windows-1252 (60 mojibake sequences — `SIH26166 Â·
CHANDRAYAAN-2`), has no viewport meta, and `[hidden]` loses to `.io{display:grid}`, so a hidden
trust-map layer paints on top of the visible one and the verified/weak colours go muddy. The
build prints which file is which; `python -m web.server` wraps the fragment itself and is always
correct. All three paths were driven in a real browser on 20 Sep and only the raw fragment failed.

The build also runs `node --check` over the page's inline script when node is present. The whole
page is one 2 MB document whose entire behaviour is that one script: a syntax error in it renders
the hero and nothing else, and the only sign is one line in a console nobody has open. It has
happened once.

Neither output is committed — `web/dist/` is gitignored. The **source** is what is committed:

| File | What it is |
|---|---|
| `web/console.template.html` | the page: markup, CSS, JS. Contains the literal `/*__DATA__*/null` |
| `web/build_console.py` | reads the evidence, replaces that marker with a JSON blob, writes `dist/` |

If the build says `template must contain '/*__DATA__*/null' exactly once`, you deleted the marker.
Put it back.

## 2. Change which pairs it shows

This is the main thing you will want to do. The roster is one list at the bottom of
`web/build_console.py`:

```python
ROSTER = [
    ("sac_ohrc_nac_w06", "Chandrayaan-2 OHRC → LRO NAC", "...", "CROSS-SENSOR", "..."),
    #  pair_id            label on the verdict panel      subtitle  tag chip    plain-English line
]
```

Each entry is `(pair_id, label, sub, tag, plain)`:

- **`pair_id`** — a folder name under `data/pairs/`. It must have `<id>_ref.tif`,
  `<id>_source.tif` and `geometry_prior.json`, **and** a cached result (see below).
- **`label`** — the instrument pair, e.g. `Kaguya TC → Kaguya MI`.
- **`sub`** — one line on what makes this pair hard.
- **`tag`** — the terminology chip. Use only: `CROSS-SENSOR`, `SAME SENSOR`, `MULTI-MODAL`,
  `SAME MISSION`. **Invariant 2 applies here exactly as it does on the deck** — NAC↔NAC and
  TMC-2 fore↔aft are `SAME SENSOR`, never cross-sensor; only visible↔infrared or
  optical↔elevation is `MULTI-MODAL`.
- **`plain`** — the sentence under the verdict. Say what the reader is looking at, in words a
  non-specialist gets right the first time.

**Every pair needs a cached result first.** Always name the pairs — a bare call caches all ~150
and fills your disk (Known issue 16):

```
python -m ops.precompute_demo_cache <pair_id> <pair_id> ...
python -m web.build_console
```

The cache stores the exact dict `run_all()` returned, so the page shows the real pipeline output,
not a re-render.

## 3. Check it is working as intended

The console can only be wrong in two ways: it can show the wrong number, or it can show the wrong
image. Both are checkable.

**Numbers.** Every figure must appear in `REPORT.md` at the freeze commit. The independent check:

```
python -m ops.freeze --check          # must print FROZEN
python -m ops.make_report             # re-renders REPORT.md from the logs
```

Then pick any number on the page and find it in `REPORT.md`. The source line under each section
heading names the section it comes from. The build script reads the same CSVs `make_report` reads, so if they disagree, one of
them has a bug and that is worth knowing.

The sweep table is a deliberate cross-check: the console **recomputes** the bins from the rows
rather than copying REPORT's table, and the two agree cell for cell. If they ever stop agreeing,
`ops/sun_sweep.py`'s rule has changed under one of them.

**Images.** The trap that already bit once: for a refused pair the cache holds *two* results —
`warped` (the matcher's answer, rejected) and `warped_final` (the fallback that rescued it).
Showing `warped_final` under a REFUSED banner teaches the opposite of the truth. The page shows
`warped` and labels the fallback separately. If you add a pair, check its "The matcher's answer"
layer actually looks like what the verdict claims.

**Quick sanity run:**

```
python -m pytest -q                   # 352 passed
python -m web.build_console           # prints the row counts it found
```

The build prints its own tallies (windows, tiles, cell counts, verdicts). If a count changes
without you changing the evidence, something is wrong.

## 4. What each section proves

| Section | The question it answers | Where the numbers live |
|---|---|---|
| **Workbench** | Does it work on images I choose, right now? | computed live by `core.pipeline.run_all`; not evidence |
| **Line it up yourself** | What does the area check actually test? | cached `run_all()` images; the verdict line quotes the pair's cached counts |
| **Same ground, two Suns** | Does Sun angle break it, and does it know when it has? | `REPORT.md` → Real sun-angle sweep |
| **Every pairing, and what the check said** | What does a verdict actually mean, square by square? | cached `run_all()` + `real_pairs_log.csv` |
| **The check, tested on purpose** | How wrong does an answer have to be before you catch it? | `trust_real_calibration.csv` |
| **The whole overlap, not chosen windows** | Did you pick the windows that worked? | `REPORT.md` → The whole lit overlap |
| **What it registers** | What does it register, and how well? | `REPORT.md`, one section per row |
| **What it refuses** | What does it decline, and did it say so itself? | `REPORT.md`, one section per row |
| **How it runs** | What actually runs? | `core/pipeline.py::run_all` |

## 5. What runs where

The browser draws; it never registers. LoFTR, sub-pixel refinement and MAGSAC++ are Python, and no
page can run them. So there are two deployments of the one built file:

| | Published link | `python -m web.server` |
|---|---|---|
| Shows the frozen evidence | yes | yes |
| Workbench | saved runs of the 10 roster pairs; says it cannot run Python | **live**: uploads, one-image tests, all real pairs in `data/pairs/` |
| Needs Python running | no | yes |
| Shareable | yes | no — loopback only |

Section 6 covers the live one. The other live demo is `app/streamlit_app.py`, which runs the same
pipeline with the cached pairs and is what Gate 4 tests:

```
streamlit run app/streamlit_app.py
```

---

## 6. The live server — the workbench

```
python -m web.build_console        # once, if the page is not built
python -m web.server              # http://127.0.0.1:8000
```

The server loads the LoFTR weights before it takes its first request, then serves the page with the
workbench live. Three ways to run something:

| On the workbench | What runs | What it shows |
|---|---|---|
| **Two images** | `run_all` on the two files you drop in | the verdict, the trust map, every square, and a download |
| **One image, known answer** | the server warps your one image by the rotation, scale, shift, blur and noise you set, then registers the warped copy back onto the original | the same, plus the true error: RMS distance between the delivered and the true transform over a 20 × 20 grid, and the rotation, scale and shift asked for against those recovered |
| **Real pairs** | any pair in `data/pairs/` (180 on this laptop), straight from its files | the same; filter by instrument pairing |

Each run is a background job the page polls, so a long run shows its stage and time instead of a
frozen button, and the *This session* list keeps every result to go back to. **Download the
result (.zip)** is exactly what `core/export.py` writes for a pair: the registered image on the
reference grid (GeoTIFF when the reference has a map), `matches.csv`, GCPs for GDAL and QGIS, an
ISIS match list, the trust map and a report.

The known-answer test is honest about its limits on the page: the two images are the same picture,
so the Sun has not moved and it tests geometry, blur and noise, not lighting; images over 900 px are
shrunk to 900 first; and the shift is always moved off the whole-pixel grid (+0.37, −0.63 px),
because a whole-pixel shift copies pixels without interpolating and flatters the result (see
`SYNTH_SHIFT_PX` in `core/pipeline.py`). Measured on 27 Sep with a 448-px OHRC display image,
rotation 8°, scale 1.10, blur 1 px and 3 % noise: 0.52 px RMS, rotation recovered as 7.91°.

The workbench stays in its offline state unless `GET api/health` answers with this service's
marker, so the published link never pretends to run anything.

| | |
|---|---|
| Accepts | GeoTIFF, PDS `.img` / `.xml` / `.lbl`, PNG, JPEG — 64 MB per **request**, which is about **48 MB of image** because the payload is JSON+base64 and inflates by 4/3. Photos over 1600 px can be shrunk in the browser first, both by one factor so their relative scale is kept |
| Speed | ~6–120 s per pair on CPU, and it is the image size that decides. Two 640-px windows: ~7 s. A 2,383-px frame against a 640-px reference: **119 s**. One at a time (LoFTR is memory-hungry); a second run waits and says so |
| Writes | **nothing to disk.** Uploads go to a temp folder deleted when the job ends; the last 8 results and their zips are held in memory only |
| Binds | `127.0.0.1` only. No auth, and it runs an expensive pipeline on request — never expose it |
| Needs | standard library only. Nothing to `pip install` on the demo laptop |

| API | |
|---|---|
| `GET api/health` | the service marker, code commit, upload cap, modes, library size |
| `GET api/library` | every real pair in `data/pairs/` with its instruments and the terminology from its own `geometry_prior.json` |
| `GET api/thumb/<id>.jpg`, `<id>_source.jpg` | small previews of a pair's reference and source |
| `POST api/jobs` | `{mode:"upload", a, b}`, `{mode:"sample", id}` or `{mode:"known", a, rot, scale, dx, dy, blur, noise}`; answers 202 with a job id |
| `GET api/jobs/<id>` | state, stage, tile progress, and the panel once done |
| `GET api/jobs/<id>/bundle.zip` | the deliverables for that run |
| `POST api/register` | the older one-shot call, kept for scripts: waits and returns the panel |

**A GeoTIFF exercises scale invariance; a PNG cannot.** PNG and JPEG carry no ground scale, so
`to_common_gsd` has nothing to bridge and both images are taken to be at the same scale. The
result says so when it happens rather than hiding the assumption.

**Verified end to end (27 Sep), in the browser:** the real pair `sac_ohrc_nac_w06` through the job
API returned `agrees` with 58 of 64 squares verified, as its cached run does; `sac_ohrc_nac_w01`
from the library, `agrees`; the OHRC → TMC-2 window uploaded as two JPEGs, refused with the
phase-correlation fallback declared. Inlier counts differ by about 1 % run to run because
MAGSAC++ samples randomly — say that before anyone else notices it.

### Hand it something it cannot take

Three things a reviewer will try, and what they now get. All three were driven through the browser's
own file inputs on 20 Sep, not through curl.

| They do this | What happens |
|---|---|
| Choose a pair over the cap | **The page refuses before it uploads anything.** *Register the pair* greys out and the log gives the size and the cap (checked 27 Sep with 55 MB of files) |
| Post an over-size body anyway (curl, or a bypassed page) | A readable **413** in 0.2 s. The server drains the body first — replying without draining used to reset the connection, so the browser showed `Failed to fetch` and the operator never saw the message |
| Upload something that is not an image | The run stops with **Not registered** and the reason: `notes.png: could not be decoded as an image` (checked 27 Sep) |
| Upload two PNGs | It runs, and the result says the uploads carried no ground scale, so scale invariance was *not* exercised. It does not silently assume 1:1 |
| Upload one image twice | 64 / 64 verified, identity. A fine thing to show on purpose; the one-image mode does the same with a known warp |

**Demo tip:** in the Streamlit app, click **All deliverables (.zip)** and nothing else. Chrome
blocks the second and later automatic downloads in a session, so clicking the other three buttons
can look like they do nothing. Everything they produce is already inside the zip.
