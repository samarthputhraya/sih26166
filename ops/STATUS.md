# STATUS — SIH26166

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewrite, never append.** This must be true as of right now.

---

## Position

| | |
|---|---|
| **Day** | **2 of 12** — Day-2 checkpoint PASSED on real Chandrayaan-2 data |
| **Next gate** | **Gate 1, Day 5 — 3 days away.** `python -m core.pipeline data/pairs/pair_01` end to end, five metrics |
| **Gates passed** | none yet (Gate 1 is the first) |
| **Gate 1 outlook** | ⚠️ **Chain is built and runs. Two things missing, neither is code.** See Gate check below |
| **Internal hackathon** | ⚠️ **DATE STILL UNKNOWN — chase the SPOC.** Open since Day 0 |
| **Repo** | `https://github.com/samarthputhraya/sih26166` · branch `main` · clean, in sync |
| **venv** | `C:\Users\samar\venvs\sih26166` — outside OneDrive, deliberately |
| **Deadlines** | SIH26166 closes 20 Sep 2026 · SPOC upload 30 Sep 2026 · Finale Dec 2026 |

---

## Smoke test — exit codes observed this session, not inferred

| Command | Exit | Meaning |
|---|---|---|
| `pytest evaluation/ -q` | **5** | no tests — Samrudh hasn't started. Not a regression |
| `pytest app/ -q` | **0** | **7 passed** — Rishabh's suite |
| `pytest baselines/ -q` | **5** | no tests — Risheeth wrote modules, no test file yet |
| `import core.pipeline` | **0** | ✅ **was 1 this morning** — the chain now exists |
| all 8 core + app modules import | **0** | clean |

---

## What landed today — 15 commits

**Samartha (13):** the whole Gate-1 chain — `core/scale.py`, `core/matcher.py`, `core/ransac.py`,
`core/pipeline.py` — plus windowed PDS4 reads in `io_loader`, real CH-2 verification, and doc fixes.
**Risheeth (1):** all three classical baselines. **Rohan (1, yesterday):** dataset card + policy.

### The Day-2 checkpoint result

Real Chandrayaan-2 OHRC (`ch2_ohr_ncp_20200229T0739312111_d_img_d18`, 1.12 GB, **MD5 verified
against the label's own checksum**), 93693 × 12000 at **0.22977 m/px**:

| | |
|---|---|
| two 640² tiles read (windowed) | **0.01 s** |
| matches | **5186**, confidence 0.998 |
| inliers | 5183 (**99.9%**) |
| recovered offset | (−40.00, −24.98) vs known (−40, −25) |
| error | median **0.117 px** = 2.7 cm |
| latency / RAM | 6.1 s / 1.41 GB |

> ⚠️ **NOT QUOTABLE.** Not in `results_log.csv`. The tiles are an **integer**-offset crop of the
> *same* frame — identical pixels, no rotation, no scale change, **no illumination difference**.
> Easiest possible case. Same chain on synthetic relief *with* rotation and scale gives **0.37 px**.
> Expect real Tier A/B pairs to be worse than both. Not cross-sensor, not multi-modal, not Tier A.
>
> What it *does* prove: LoFTR works on real OHRC texture at affordable CPU latency, and the chain
> is wired correctly. That was the Day-2 question and the answer is yes.

---

## Per person

| Person | Last push | Delivered | Blocked on |
|---|---|---|---|
| **Samartha** | today, 13 commits | Gate-1 chain + io_loader (41 tests) | nothing |
| **Risheeth** | **today** | 3 baselines + failure gallery + runner, 759 lines | nothing |
| **Rishabh** | yesterday | `change_detection.py`, 7 passing tests, README | nothing |
| **Rohan** | yesterday | `DATASET_CARD.md` + provenance policy | Drive folder (Samartha) |
| **Samrudh** | ❌ **never** | nothing — `evaluation/` is empty | nothing. **He is the Gate-1 blocker** |
| **Saniya** | ❌ **never** | nothing — `presentation/` is empty | nothing |

**Risheeth delivered well.** Verified by running his own acceptance test: all three recover the
known shift exactly — SIFT 1424 matches, ORB 3657, AKAZE 1922, every one at median `(-7.00, -5.00)`.
He avoided all three known traps unprompted (`cv2.xfeatures2d.AKAZE_create()`, the `des is None`
guard, the `len(p)==2` ratio guard).

**Rishabh's module works on real data** — found a planted change on a real OHRC tile, area within
7% of truth. **Three findings handed to him** (see Known issues #7).

🔴 **Samrudh has not pushed in three days and is now the single Gate-1 blocker.** `pipeline.py`
prints "metrics unavailable" until `evaluation/metrics.py :: evaluate()` exists. Escalate.

🔴 **Saniya has not pushed in three days.** Her Day-1 task (download the template, post the real
headings) is 2 hours and blocks the entire deck.

---

## In flight — resume here

**Nothing is half-written. Working tree clean, everything pushed.**

### The next build is `core/illumination.py`

It is the last untouched piece of the core problem (scale ✅, matching ✅, illumination ❌) and it is
**PS demand #2**. Right now `pipeline.py` calls a hook that reports
`"none (core/illumination.py not written yet)"` — deliberate, and it announces itself at runtime.

Two approaches to A/B (Canonical Facts §6.4): **phase congruency** vs **sign-invariant gradient
orientation**. Keep the loser's numbers — "we tried both, here's the comparison" is a strong Q&A
answer.

**The test data is ready and needs nobody.** Two LROC NAC images, same site, **54° of sun-angle
difference** — verified downloadable today, HTTP 206, 264.5 MB each (529 MB total):

```
inc 25.2°  https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0003/DATA/MAP/2010088/NAC/M124545845LE.IMG
inc 79.3°  https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0001/DATA/COM/2009194/NAC/M102128467RE.IMG
```

**The measurable claim:** matches before normalisation vs after, on genuinely different lighting.
Good → strongest technical slide. Bad → we learn it on Day 3, not Day 8, and the fallback is open.

⚠️ **Check each is not an empty frame before using it** (`std > 10`) — see Known issue #6.

⚠️ **RAM was 2.1 GB free at wrap.** LoFTR needs ~1.84 GB at 640². Close Chrome before starting.

### Also free to build, needs nobody
`core/subpixel.py`, `core/distribution.py` (both Day 8), `app/streamlit_app.py` (Day 9).

### Blocked
Integrating `evaluate()` (Samrudh) · multi-modal Tier C (no infrared data yet, and it is in the
PS title).

---

## Open questions

1. **Internal hackathon date** — unknown since Day 0. Chase the SPOC. Reshapes everything.
2. **Google Drive `SIH26166_DATA` still does not exist.** Blocks Rohan and blocks distributing
   `weights/loftr_outdoor.pt` (46 MB, gitignored) — it exists on **exactly one laptop**. Needs a
   browser; cannot be scripted (no Drive desktop mount here).
   Folders: `raw_samples/ pairs/ demo_cache/ weights/ isro_user_guides/`
3. **Multi-modal (Tier C) has no data and no owner action yet.** It is in the PS *title*. Nobody
   has infrared imagery. Decide by Day 5 who gets it.
4. **Gate 1 needs a real pair in `data/pairs/`.** Rohan's catalogue. If he slips we can build one
   ourselves from the CH-2 data, but then say so honestly.
5. **CH-3 landing-site NAC product IDs** — still unverified. Rishabh needs them ~Day 6.
   ⚠️ These are **LROC NAC images of the CH-3 site**, not "Chandrayaan-3 imagery".

---

## Known issues / traps already found

*Recorded so `daily-reviewer` does not re-report them.*

**1. 🔴 LoFTR needs `[0,1]`. Raw DN returns ZERO matches, silently.** No exception — just an empty
result reading as "the matcher doesn't work on lunar imagery". Measured on real NAC texture:
`[0,1]` → **5402 matches**; raw DN `[32..199]` → **0**. `io_loader` deliberately returns raw DN (a
loader must not rescale science data), so `matcher.py` normalises once, internally, with a fixed
`/255`. **Never pass raw DN to LoFTR.** Keypoints are `(x, y)`, not `(row, col)` — confirmed by sign.

**2. 🔴 Big-endian silently corrupts OpenCV.** cv2 5.0.0.93 accepts a big-endian array without
raising and returns garbage — max abs difference **34935**. LROC NAC is `MSB_INTEGER`, PDS4 is often
`UnsignedMSB2`. `io_loader.as_cv_safe()` normalises before anything else sees the array; all `core/`
may assume it. Second-order: **numpy arithmetic does not preserve byte order** —
`np.arange(n, dtype=">u2") * 37` returns native order. Cast *after* arithmetic.

**3. `rasterio` is unusable — DECIDED: GDAL-free.** Smart App Control blocks its DLLs by content
hash; disabling it needs an OS reinstall. Cost: no `/vsicurl`, so **Kaguya must be downloaded, not
streamed**. `imagecodecs` is absent so tifffile cannot decode **LZW** — `io_loader` falls back to
Pillow for pixels while keeping tifffile's tags. **Verified on the real Kaguya file, which is LZW.**
Also: `tifffile.geotiff_metadata` returns `None` without tag 34735 — read tags 33550/33922 by number.

**4. LROC NAC EDR mislabels its own signedness.** Declares `LSB_INTEGER` at 8 bits (signed) for
`RAW_INSTRUMENT_COUNT` (unsigned 0–255). Read strictly, everything above DN 127 wraps negative.
`io_loader` corrects only when unambiguous and sets `dn_signedness_corrected`.

**5. 🔴 Illumination geometry is not where you'd expect.**
- **CH-2 OHRC has none at all** — not in the label, and not in the geometry CSV either (that has
  only `Longitude, Lattitude, Pixel, Scan`, 113,499 rows). Sun-angle claims about CH-2 are **not
  supportable from the product**. The upside: those points *are* georeferencing.
  ⚠️ The CSV header spells it **`Lattitude`** (two t's) while the label says `Latitude`.
- **LROC NAC EDR labels have none either** — but **ODE's metadata does**. `SDRPHO` **does not
  exist** (it is **`SDPPHO`**, P not R — our own typo, now fixed), and `SDPPHO` has
  `ValidIncidenceAngles = F` anyway. **`EDRNAC4` has `T`** — ordinary NAC EDRs come back from the
  ODE REST API *with* `Incidence_angle`. **That is the Tier A route.** Filter to **20–80°**; ODE
  returns 139° and 164°, which are night-side.

**6. 🔴 Always look at the picture.** Rohan's `M108587604RE.IMG` decodes perfectly and contains
**nothing** — 98.1% of pixels in DN 32–46, std 1.42, no craters. The only bright pixels are the
detector's masked columns. Every numeric test passed while the image was empty, and it made a
dry-run figure look **10× better than reality**. **Check `std > 10` and view every product before
cataloguing it.**

**7. Findings handed to Rishabh (his to fix, not ours).**
`mask[-margin:, :] = 0` erases the **whole mask** when margin is 0 (`-0` is `0`) → silent zero
detections for `edge_margin_frac=0` or any image under 20px · `gsd_mpp=0.5` default is wrong for
every camera we use (350× off on Kaguya) · `classify()` reads a single pixel at the centroid ·
**absolute difference cannot separate "sun moved" from "something changed"** — 8 false positives on
identical terrain with only brightness changed. That last one is his Day-4 task, not a bug.

**8. Environment.** `cv2.AKAZE_create()` does not exist — it is `cv2.xfeatures2d.AKAZE_create()`
(guide fixed) · Windows console is **cp1252**, so use `PYTHONIOENCODING=utf-8` for any script
printing em-dashes or arrows · the repo is inside **OneDrive**, which ignores `.gitignore` — keep
large downloads outside it · `.gitignore` now covers `data_path.txt`, `*.pdf`, `*.pptx`, `*.mp4`.

**9. Binaries already in history.** Rohan committed 12 PNGs (~3.9 MB) to `data/lroc_analysis/`.
Git keeps them permanently — deleting won't shrink the repo. Future plots go to Drive. He also
wrote ~1200 lines into `ops/` and `docs/`, which Invariant 4 assigns to Samartha — a boundary
question, not a quality one; his analysis is good.
