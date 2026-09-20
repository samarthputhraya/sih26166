# The Mission Console — how to drive it

The console at `web/` is a **read-only instrument panel over frozen evidence**. It never computes
a result. It reads the evidence logs, the demo caches, `geometry_prior.json` and the LOLA DEM, and
draws them. That is deliberate: a page that could compute its own numbers could disagree with
`REPORT.md`, and then neither could be trusted.

It lives in `web/`, **outside `core/`, `evaluation/`, `ops/` and `app/`**, so building it can never
re-stamp an evidence row or a demo cache. You can rebuild it as often as you like without
invalidating the freeze.

---

## 1. Build it

```
python -m web.build_console
```

Takes about 20 seconds. Writes `web/dist/mission-console.html` — one self-contained file, no
network needed except Google Fonts and the three.js CDN. Open it in any browser.

`web/dist/` is gitignored. The **source** is what is committed:

| File | What it is |
|---|---|
| `web/console.template.html` | the page: markup, CSS, JS. Contains the literal `/*__DATA__*/null` |
| `web/build_console.py` | reads the evidence, replaces that marker with a JSON blob, writes `dist/` |

If the build says `template must contain '/*__DATA__*/null' exactly once`, you deleted the marker.
Put it back.

## 2. Publish it

The live link is a Claude Artifact. Republishing the same file keeps the same URL. It is
**private by default** — a judge cannot open it until you share it from the page's Share menu.

## 3. Change which pairs it shows

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

## 4. Check it is working as intended

The console can only be wrong in two ways: it can show the wrong number, or it can show the wrong
image. Both are checkable.

**Numbers.** Every figure must appear in `REPORT.md` at the freeze commit. The independent check:

```
python -m ops.freeze --check          # must print FROZEN
python -m ops.make_report             # re-renders REPORT.md from the logs
```

Then pick any number on the page and find it in `REPORT.md`. The bay headers name the section it
comes from. The build script reads the same CSVs `make_report` reads, so if they disagree, one of
them has a bug and that is worth knowing.

The sweep table is a deliberate cross-check: the console **recomputes** the bins from the rows
rather than copying REPORT's table, and the two agree cell for cell. If they ever stop agreeing,
`ops/sun_sweep.py`'s rule has changed under one of them.

**Images.** The trap that already bit once: for a refused pair the cache holds *two* results —
`warped` (the matcher's answer, rejected) and `warped_final` (the fallback that rescued it).
Showing `warped_final` under a REFUSED banner teaches the opposite of the truth. The page shows
`warped` and labels the fallback separately. If you add a pair, check its `MATCHER'S ANSWER`
layer actually looks like what the verdict claims.

**Quick sanity run:**

```
python -m pytest -q                   # 340 passed
python -m web.build_console           # prints the row counts it found
```

The build prints its own tallies (windows, tiles, cell counts, verdicts). If a count changes
without you changing the evidence, something is wrong.

## 5. What each bay proves

| Bay | The question it answers | Where the numbers live |
|---|---|---|
| **SUN** | Does Sun angle break it, and does it know when it has? | `REPORT.md` → Real sun-angle sweep |
| **TRUST MAP** | What does a verdict actually mean, per region? | cached `run_all()` + `real_pairs_log.csv` |
| **TILING** | Did you pick the windows that worked? | `REPORT.md` → The whole lit overlap |
| **CALIBRATION** | How wrong does an answer have to be before you catch it? | `trust_real_calibration.csv` |
| **PIPELINE** | What actually runs? | `core/pipeline.py::run_all` |
| **RESULTS** | What does it register, and how well? | `REPORT.md`, one section per row |
| **REFUSALS** | What does it decline, and did it say so itself? | `REPORT.md`, one section per row |

## 6. The one thing it cannot do

There is no upload button, and there should not be one here. The engine is Python — LoFTR,
sub-pixel refinement, MAGSAC++ — on CPU, offline. A browser cannot run it.

To let a judge drop in their own pair, the console needs a small **FastAPI** backend calling
`core.pipeline.run_all` directly, served locally with the network off. The front end does not
change; only its data source does. That is finale work, not submission work.

Until then the live demo is `app/streamlit_app.py`, which does run the real pipeline:

```
streamlit run app/streamlit_app.py
```

---

## 7. The live server — register a pair someone hands you

```
python -m web.build_console        # once, if the page is not built
python -m web.server              # http://127.0.0.1:8000
```

The page served this way grows a **LIVE** bay at the top: drop in two images, press
*Register the pair*, and `core.pipeline.run_all` runs on this CPU. The result is appended to the
pair roster and rendered by `web/panel.py` — **the same renderer the frozen pairs use**, so a
live panel and a frozen panel cannot disagree about what a verdict means.

The bay is hidden unless `GET api/health` answers with this service's marker. Opened as the
published link that fetch fails, the bay stays hidden, and the shared page stays read-only.
One built file, two honest deployments.

| | |
|---|---|
| Accepts | GeoTIFF, PDS `.img` / `.xml` / `.lbl`, PNG, JPEG — 64 MB per request |
| Speed | ~20–60 s per pair on CPU. One at a time (LoFTR is memory-hungry) |
| Writes | **nothing.** Uploads go to a temp folder deleted when the request ends. No evidence log, no cache, no repo file |
| Binds | `127.0.0.1` only. No auth, and it runs an expensive pipeline on request — never expose it |
| Needs | standard library only. Nothing to `pip install` on the demo laptop |

**A GeoTIFF exercises scale invariance; a PNG cannot.** PNG and JPEG carry no ground scale, so
`to_common_gsd` has nothing to bridge and both images are taken to be at the same scale. The
panel says so when it happens rather than hiding the assumption.

**Verified end to end (20 Sep):** uploading `site_ohrc_m1153871873le_w02` through the API returned
`agrees`, **5,112 matches** and **56 / 64 verified cells**. The frozen log for that same pair says
`agrees`, **5,112 matches**, **56 verified**. Inlier counts differ by about 1 % run to run
(4,630 vs 4,680) because MAGSAC++ samples randomly — say that before a judge notices it.
