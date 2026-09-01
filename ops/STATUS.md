# STATUS — SIH26166

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewrite, never append.** This must be true as of right now.
>
> Last wrap: **31 Aug 2026, 21:30 IST** (second session of Day 2 — an evening block after the
> 20:03 wrap).

---

## Position

| | |
|---|---|
| **Day** | **2 of 12, COMPLETE.** Tomorrow is **Day 3 (1 Sep)** |
| **Next gate** | **Gate 1, Day 5 — 3 days away.** `python -m core.pipeline data/pairs/pair_01` end to end, five metrics |
| **Gates passed** | none yet (Gate 1 is the first) |
| **Gate 1 outlook** | ⚠️ **ONE thing missing, and it is not ours.** `evaluation/metrics.py`. Everything else now runs. See Gate check |
| **Internal hackathon** | ⚠️ **DATE STILL UNKNOWN — chase the SPOC.** Open since Day 0 |
| **Repo** | `https://github.com/samarthputhraya/sih26166` · branch `main` |
| **venv** | `C:\Users\samar\venvs\sih26166` — outside OneDrive, deliberately |
| **Data root** | `C:\Users\samar\sih26166_data` — outside OneDrive. Path is in `data_path.txt` (gitignored) |
| **Deadlines** | SIH26166 closes 20 Sep 2026 · SPOC upload 30 Sep 2026 · Finale Dec 2026 |

---

## Smoke test — exit codes observed this session, not inferred

| Command | Exit | Meaning |
|---|---|---|
| `pytest core/ -q` | **0** | **15 passed** — ⬆ **was 5 (no tests) this morning** |
| `pytest app/ -q` | **0** | **7 passed** — Rishabh's suite |
| `pytest evaluation/ -q` | **5** | no tests — Samrudh hasn't started. Not a regression |
| `pytest baselines/ -q` | **5** | no tests — Risheeth wrote modules, no test file yet |
| `import core.pipeline` | **0** | ✅ chain imports clean |
| `python -m core.pipeline data/pairs/pair_01` | **0** | ✅ **runs end to end on REAL CH-2 data** |
| `from evaluation.metrics import evaluate` | **ImportError** | 🔴 **`metrics.py` is 0 bytes.** See "Late pushes" below |

> Re-run **after** rebasing onto the six commits that landed 20:12–21:33. The `evaluation/` exit
> code is still **5** *with all four of Samrudh's files present*, because they are empty.

---

## What landed this evening (session 2 of Day 2)

Three things, in order of how much they change the picture.

### 1. 🔴 `data/pairs/pair_01` was NOT real data. It is now.

The `pair_01` the Gate-1 command pointed at was a **synthetic dry-run fixture**, not lunar imagery:

| | old `pair_01_source` | old `pair_01_ref` |
|---|---|---|
| distinct values | 329,763 (continuous float, **incl. negatives**) | **15** (integers 35–49) |
| std | 10.56 | **1.40** |
| metadata | none | none |

Two crops of one frame cannot have 329,763 and 15 distinct values. The timestamps close it: the
fixture was written **09:34**, the CH-2 image downloaded **10:37** — it predates the real data by an
hour. And the pipeline reported **100.0% inliers** on it, the same flattering-number failure as the
`0.0392 px` correction in `0ee11d2`.

**Rebuilt** with new `core/make_demo_pair.py` from the real CH-2 strip (region scanned for texture,
x=2000 y=64000, std 32.4):

```
pair_01_{source,ref}.tif   640x640 uint8   DN [7, 255]  std 34.5   known offset (40, 25)
python -m core.pipeline data/pairs/pair_01
  -> 5185 matches, 5183 inliers (100.0%), illumination gradient_orientation, 5.6 s, exit 0
```

Old fixture preserved at `data/pairs/pair_00_dryrun/`, not deleted.

> ⚠️ **Still not a validation tier.** Same frame, same exposure, integer offset — identical pixels,
> no illumination difference. Gate-1 wiring fixture and known-answer check only. Log it as
> `same-frame offset crop`. Not cross-sensor, not cross-illumination, not multi-modal.

### 2. `core/illumination.py` — built, tested, and A/B'd

Both methods Canonical Facts §6.4 names, behind one contract. **15 tests, all passing.**

> 🔴 **`normalize()` returns [0, 255], NOT [0, 1].** `matcher._to_tensor` divides by 255
> unconditionally. Returning unit range puts every pixel in [0, 0.004] → zero matches, **no
> exception**. `core/test_illumination.py::test_output_is_dn_range_not_unit_range` guards this.

**The A/B — run twice, bit-identical both times** → `core/bench_illumination_results.csv`:

| case | method | matches | ratio | recovered shift (truth −40, −25) |
|---|---|---|---|---|
| identical | off | 5184 | 1.000 | (−39.99, −24.92) |
| identical | **gradient_orientation** | **5185** | 1.000 | (−40.01, −24.96) |
| identical | phase_congruency | 4938 | 1.000 | (−40.01, −24.94) |
| inverted+gamma+ramp | off | **336** | **0.342** | **(−41.31, −24.96)** ← 1.31 px error |
| inverted+gamma+ramp | **gradient_orientation** | **5023** | **1.000** | **(−40.00, −24.96)** |
| inverted+gamma+ramp | phase_congruency | 4886 | 0.999 | (−39.98, −24.95) |

**Decision: `gradient_orientation` is the default**, on measurement. It costs nothing on the easy
case, fully restores the hard one, and is ~15% faster than phase congruency (which also loses 5% of
matches on the easy case). Both are kept — "we tried both, here is the comparison" is the Q&A answer.

> ⚠️ **Case 2 is an INTENSITY transform, not a sun-angle change.** Shadows flip polarity but do not
> **move**. Under a real sun-angle change they move. This result is necessary, not sufficient, and
> says **nothing** about cross-illumination performance. Written to
> `core/bench_illumination_results.csv`, deliberately **not** `evaluation/results_log.csv` —
> Samrudh owns that file and its schema.

`pipeline.py` now prints the method name rather than `applied` — "we normalise illumination" invites
"with what?", and the answer should be in the output.

### 3. Data rescued out of a temp folder that Windows deletes

The **only** copy of the CH-2 data was in a dead session's `%LOCALAPPDATA%\Temp` scratchpad. Moved to
`C:\Users\samar\sih26166_data\`, **MD5 re-verified against the `md5_checksum` in ISRO's own PDS4
label** (`8a566034bdc1cdd2e59bb2b33984c5e7`, match). Drive `SIH26166_DATA` is now populated
including `weights/loftr_outdoor.pt`.

---

## Late pushes — six commits landed 20:12–21:33, during this session

**Read this before reacting to the commit log. Two of the three pushes are not what they look like.**

### 🔴 Samrudh's four commits are all EMPTY FILES

| commit | file | size on disk |
|---|---|---|
| `4d89928` shaded_relief: DEM hillshade at arbitary sun azimuth/elevation | `evaluation/shaded_relief.py` | **0 bytes** |
| `28f9cd4` synthetic_data: pair generator with exact H_true… | `evaluation/synthetic_data.py` | **0 bytes** |
| `4ce10ad` metrics: evaluate() with held-out residual split… | `evaluation/metrics.py` | **0 bytes** |
| `0e847e4` test_metrics: 5 test incl. holdout and no-GT… | `evaluation/test_metrics.py` | **0 bytes** |

The messages describe exactly the right work. The files contain nothing. Verified three ways:
`git cat-file -s` on each blob returns `0`; `pytest evaluation/` still exits **5** with all four
present; `from evaluation.metrics import evaluate` raises **ImportError**.

**Gate 1 is therefore still blocked and the blocker is unchanged.** This is most likely `git add` of
files created but never saved from the editor — an easy and very recoverable mistake. **Ask him to
re-save and re-push; do not assume he has to start over, and do not treat this as him not
delivering.** He started, at 21:12, after three quiet days.

### ⚠️ Rohan committed ~18 MB of binaries — permanent, Invariant 5

`e31f444` added 1,391 lines plus PNGs including **`data/lroc_analysis/ch2_ohr_preview.png` at
9.96 MB**, `ohrc_preview.png` (2.30 MB) and `ch2_ohr_full_preview.png` (2.30 MB). Also
`find_lroc_matches.py`, `lroc_coverage.html`, `lroc_ohrc_matches.csv` and two JPGs **at the repo
root**, not under `data/`. Git keeps all of it permanently — **deleting them will not shrink the
repo.** This is Known issue #9 happening a second time, larger. The *analysis* looks genuinely
useful (LROC↔OHRC footprint matching, 998 rows) — this is a placement problem, not a quality one.
**He needs telling tonight, kindly, before Day 3 adds more.**

### ✅ Rishabh — `app/README.md`, Kaguya change-detection validation notes (21 lines)

---

## Per person

| Person | Last push | Delivered | Blocked on |
|---|---|---|---|
| **Samartha** | today | Gate-1 chain · illumination + A/B · real `pair_01` · **first 15 tests in `core/`** | nothing |
| **Risheeth** | today | 3 baselines + failure gallery + runner, 759 lines | nothing |
| **Rishabh** | **today 20:32** | `change_detection.py`, 7 passing tests, README + Kaguya notes | nothing |
| **Rohan** | **today 20:12** | `DATASET_CARD.md` · LROC↔OHRC footprint analysis · **Drive populated** | nothing — but see binaries above |
| **Samrudh** | **today 21:12–21:33** | 4 commits, **all four files 0 bytes** | nothing. **Still the sole Gate-1 blocker** |
| **Saniya** | ❌ **never — 3 days** | nothing. `presentation/` is empty | nothing |

🔴 **Gate 1 still hangs on `evaluation/metrics.py` having content.** His spec with exact expected
test values is in `ops/specs/day_3.md`. **If it is not in by Day 4 evening, Gate 1 fails on Day 5** —
escalate then, not on Day 5 morning when there is no night left.

🔴 **Saniya has not pushed in three days** and is now the only person who has delivered nothing.
2-hour task, blocks the whole deck from Day 3 on. ⚠️ **Gate 5 risk** — Gate 5 is all six explaining
their own module cold, and someone who has not started cannot.

⚠️ **Both are also a Gate 5 risk.** Gate 5 is all six explaining their own module cold. Someone who
has not started cannot.

---

## In flight — resume here

**Nothing is half-written.** Working tree committed and pushed.

### Next build: `core/subpixel.py` (Canonical Facts §6.6)

NCC on an 11×11 patch per match + quadratic peak fit. Two core modules from the layout still do not
exist — `subpixel.py` and `distribution.py` — and both are pure Samartha work blocked by nobody.

**Take `subpixel.py` first, because it is the one that can be measured without Samrudh.** `pair_01`
has a known *integer* offset; cut a companion fixture at a known **fractional** shift and endpoint
error against a known answer is a real number, computed the way `bench_illumination.py` already
reports recovered shift — without borrowing any of `evaluate()`'s definitions.

It also earns the project's headline claim: at CH-2's **0.22977 m/px**, half a pixel is **11.5 cm**.
Invariant 2 requires a sub-pixel claim to name the grid and give the metres. We currently have
neither the module nor the number.

> **Hold `distribution.py`.** Judging coverage and CV means using `evaluate()`'s definitions, and
> computing our own in the meantime is exactly the substitution `pipeline.py` refuses to make.

### The real illumination test is still outstanding

Tonight's A/B used a synthetic intensity transform. The **honest** sun-angle number needs real data.
Two LROC NAC images, same site, **54° of sun-angle difference** — verified downloadable, HTTP 206,
264.5 MB each (529 MB total):

```
inc 25.2°  https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0003/DATA/MAP/2010088/NAC/M124545845LE.IMG
inc 79.3°  https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0001/DATA/COM/2009194/NAC/M102128467RE.IMG
```

⚠️ **Check each has `std > 10` before using it** — see Known issue #6. **This is LROC NAC ↔ LROC NAC
= same sensor = Tier A cross-illumination. It is NOT cross-sensor** (Invariant 2).

### Also free to build, needs nobody
`core/distribution.py` (§6.7) · `app/streamlit_app.py` (Gate 3 is Day 10) · `io_loader` tests.

### Blocked
Integrating `evaluate()` (Samrudh) · multi-modal Tier C (no infrared data, and it is in the PS title).

---

## Open questions

1. **Internal hackathon date** — unknown since Day 0. Chase the SPOC. Reshapes everything.
2. **Multi-modal (Tier C) has no data and no owner action.** It is in the PS *title* and a hard
   Gate-2 criterion. Nobody has infrared imagery. **Decide the owner by Day 5.**
3. **CH-3 landing-site NAC product IDs** — still unverified. Rishabh needs them ~Day 6.
   ⚠️ These are **LROC NAC images of the CH-3 site**, not "Chandrayaan-3 imagery".
4. **`fetch_weights.py` has never been run on a teammate's machine.** Drive now carries the 46 MB
   checkpoint, so there are two routes — but **test one of them before Day 5, not at Gate 4.**
5. **`data/pairs/*` is gitignored, so `PROVENANCE.md` for `pair_01` is not in git.** The recipe is
   reproducible from `core/make_demo_pair.py` (defaults are the exact coordinates used), which is
   arguably better. Flagged so nobody hunts for a missing file.

---

## Known issues / traps already found

*Recorded so `daily-reviewer` does not re-report them.*

**1. 🔴 LoFTR needs `[0,1]`. Raw DN returns ZERO matches, silently.** No exception — just an empty
result reading as "the matcher doesn't work on lunar imagery". Measured on real NAC texture:
`[0,1]` → **5402 matches**; raw DN `[32..199]` → **0**. `io_loader` deliberately returns raw DN (a
loader must not rescale science data), so `matcher.py` normalises once, internally, with a fixed
`/255`. **Never pass raw DN to LoFTR.** Keypoints are `(x, y)`, not `(row, col)` — confirmed by sign.

**1b. 🔴 The same trap, in reverse, now applies to `illumination.normalize()`.** It must return
**[0, 255]**, because the matcher divides by 255 downstream. A "tidy-up" that makes it return
[0, 1] gives zero matches with no error. Guarded by a test that says so in its failure message.

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
  exist** (it is **`SDPPHO`**, P not R), and `SDPPHO` has `ValidIncidenceAngles = F` anyway.
  **`EDRNAC4` has `T`.** **That is the Tier A route.** Filter to **20–80°**; ODE returns 139° and
  164°, which are night-side.

**6. 🔴 Always look at the picture.** Rohan's `M108587604RE.IMG` decodes perfectly and contains
**nothing** — 98.1% of pixels in DN 32–46, std 1.42, no craters. Every numeric test passed while the
image was empty, and it made a dry-run figure look **10× better than reality**. **Check `std > 10`
and view every product before cataloguing it.** The `pair_01` finding above is the same lesson a
second time: *a green pipeline says nothing about whether its input is real.*

**6b. Tonight's corollary — a fixture can be fake even when the pipeline is honest.** Nothing in
`core/` was wrong; the input was. When a result looks too good (100% inliers), **check the input's
histogram before believing the output.**

**7. Findings handed to Rishabh (his to fix, not ours).**
`mask[-margin:, :] = 0` erases the **whole mask** when margin is 0 (`-0` is `0`) → silent zero
detections for `edge_margin_frac=0` or any image under 20px · `gsd_mpp=0.5` default is wrong for
every camera we use (350× off on Kaguya) · `classify()` reads a single pixel at the centroid ·
**absolute difference cannot separate "sun moved" from "something changed"** — 8 false positives on
identical terrain with only brightness changed. That last one is his Day-4 task, not a bug.

**8. Environment.** `cv2.AKAZE_create()` does not exist — it is `cv2.xfeatures2d.AKAZE_create()` ·
Windows console is **cp1252**, so use `PYTHONIOENCODING=utf-8` for any script printing em-dashes or
arrows · the repo is inside **OneDrive**, which ignores `.gitignore` — keep large downloads outside
it · `.gitignore` covers `data_path.txt`, `*.pdf`, `*.pptx`, `*.mp4`, `data/pairs/*`.

**9. Binaries already in history.** Rohan committed 12 PNGs (~3.9 MB) to `data/lroc_analysis/`.
Git keeps them permanently — deleting won't shrink the repo. Future plots go to Drive.

**10. A STATUS claim was wrong and is corrected here.** The previous STATUS said Samartha had
delivered "`io_loader` (41 tests)". **Those tests existed only in a scratchpad and were never
committed** — `core/` had **zero** tests in the repo until tonight. `io_loader.py` (874 lines, the
most trap-laden module we have) **still has none**, and Day 4's row schedules a refactor of it.
Write tests before that refactor, not after.
