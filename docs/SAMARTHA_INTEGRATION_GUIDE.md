# Samartha — Team Lead & Integration Guide

**Role:** Matching core + integration + web UI + unblocking five people
**Time:** 5–6 hrs/day | **You own the critical path**

> Read `00_CANONICAL_FACTS.md` end to end. You are the person who enforces it.

---

## 🔴 THE THREE THINGS THAT CHANGED

**1. There is no GPU.** Your laptop has an Intel Arc iGPU with 0 MB dedicated VRAM. Rohan's
RX 9060 XT is 30 km away and is AMD, not CUDA. **The demo machine is your laptop and all demo
inference is CPU-only.** The old guide's Day 1 line `torch.cuda.is_available()` would have printed
`False` and the old plan had no answer for that.

**2. `pip install magsac` does not exist.** Verified — no such package on PyPI. Use
`cv2.USAC_MAGSAC`, which is built into OpenCV.

**3. Scale invariance was never in the plan.** The PS demands it; real ratios are 18–285×. LoFTR
degrades past roughly 4–8× on its own. `core/scale.py` is now a required module, not an extra.

---

## 🎯 YOUR MISSION

1. Build the core engine: **load → resample to common GSD → illumination normalise → match →
   RANSAC → sub-pixel refine → enforce distribution**
2. Build the Streamlit UI that ties it together
3. Integrate five people's modules
4. **Unblock teammates by writing specs the night before**
5. Enforce gates — no "we'll fix it later"

If the pipeline doesn't run end to end on Day 5, that's on you. If a teammate is blocked mid-task,
that's also on you — the spec was bad.

---

## 📅 YOUR 12-DAY PLAN

### DAY 1 — The measurement that decides everything

**Morning (1 hr)**
```bash
mkdir sih26166 && cd sih26166 && git init
python -m venv venv && venv\Scripts\activate

pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install kornia opencv-contrib-python numpy pandas matplotlib streamlit pillow
pip install pds4_tools pvl rasterio scikit-image
```
Create the repo structure from Canonical Facts §14. Add all 6 as collaborators.

> **Note the CPU index URL.** Do not install the default torch wheel — it pulls a large CUDA
> payload you cannot use.

**Morning (1 hr) — ⚠️ THE CRITICAL BENCHMARK. Do this before anything else.**

```python
import time, torch, kornia as K
matcher = K.feature.LoFTR(pretrained="outdoor").eval()

for size in (480, 640, 1024):
    a = torch.rand(1, 1, size, size)
    b = torch.rand(1, 1, size, size)
    with torch.inference_mode():
        matcher({"image0": a, "image1": b})              # warm-up
        t0 = time.perf_counter()
        out = matcher({"image0": a, "image1": b})
        print(size, f"{time.perf_counter()-t0:.2f}s", len(out["keypoints0"]))
```

**Post the numbers in team chat immediately.** They decide:
- your tile size for the rest of the project
- whether the demo can run inference live or must show precomputed tiles
- what Saniya can promise in the demo script
- what Gate 4 can claim

Rules of thumb for the decision:
- **< 3 s at 640²** → live inference in the UI is comfortable
- **3–10 s** → live, but the UI needs a progress bar and Saniya narrates over it
- **> 10 s** → drop to 480², or precompute demo results and be explicit on screen that they are cached

**Afternoon (3 hrs)**
- Write `core/io_loader.py` with a format abstraction from the start:
  ```python
  def load(path) -> tuple[np.ndarray, dict]:
      """Returns (grayscale float32 array, metadata dict).
      metadata keys: gsd_mpp, instrument, sun_azimuth, sun_elevation, incidence, crs, transform
      Dispatches on extension: .xml → pds4_tools | .IMG → pvl+rasterio | .tif → rasterio
      """
  ```
  **Write the abstraction now even though you only need one format today.** CH-2 is PDS4, LROC is
  PDS3, Kaguya is GeoTIFF. Hardcoding one format costs you two days on Day 9.
- Load one of Rohan's real lunar images. Display it. Confirm the metadata dict populates.

---

### DAY 2 — Matcher on real lunar data, weights cached

**(2 hrs)** Get LoFTR matching **two real lunar tiles**, not two random photos. The old guide said
"run on ANY two images (even non-lunar)" — that proves nothing about low-texture maria, which is
precisely where this is hard.

**Cache the weights.** They download on first use and wifi is off at Gate 4:
```python
import kornia as K, torch, pathlib
m = K.feature.LoFTR(pretrained="outdoor")
pathlib.Path("weights").mkdir(exist_ok=True)
torch.save(m.state_dict(), "weights/loftr_outdoor.pt")
```
Then load from `weights/` everywhere, never from the network. **Verify this at Gate 4 with wifi
genuinely off** — not "probably fine."

**(1 hr)** Start `core/scale.py`:
```python
def to_common_gsd(img_a, meta_a, img_b, meta_b):
    """Resample both to the coarser GSD of the two. Returns (a, b, gsd, scale_factors).
    Without this, an 18-36x ratio pair simply will not match."""
```

**(1 hr)** Write Day 3 specs for all five teammates.

> **✅ Day 2 checkpoint:** LoFTR matches a real lunar tile pair at acceptable CPU latency.
> If not → decide the fallback **now**, not on Day 8.

---

### DAY 3 — Walking skeleton

Wire it end to end, deliberately ugly:
```
load → to_common_gsd → match → cv2.findHomography(USAC_MAGSAC) → warpPerspective → save
```
Output: `warped_source.jpg`. No metrics, no UI. **It just has to run.**

```python
H, mask = cv2.findHomography(src_pts, ref_pts, method=cv2.USAC_MAGSAC,
                             ransacReprojThreshold=3.0, confidence=0.999)
```

---

### DAY 4 — Metrics + refactor (moved a day earlier)

- Integrate Samrudh's `evaluate()`. First real numbers into `results_log.csv`.
- **Refactor `core/` to fixed interfaces today, not Day 5.** The old plan put the refactor on the
  same day as Gate 1 and Samrudh's integration and Rohan's data delivery — four moving parts, one
  gate. Do it now while nothing depends on it.

```
core/
├── io_loader.py     load(path) -> (img, meta)
├── scale.py         to_common_gsd(a, ma, b, mb) -> (a, b, gsd, factors)
├── illumination.py  normalize(img) -> img
├── matcher.py       match(a, b) -> (src_pts, ref_pts, scores)
├── ransac.py        filter_matches(src, ref) -> (src_in, ref_in, H, mask)
├── subpixel.py      refine(a, b, src, ref) -> (src_ref, ref_ref)
├── distribution.py  enforce_grid(matches, shape, grid=8) -> matches
└── pipeline.py      run_all(src_path, ref_path) -> (warped, matches, metrics)
```
One function per file. Clear I/O. No global state. **Freeze these signatures today** — five people
code against them.

- **Pairing session 1 (1 hr): Samrudh.** Walk him through `pipeline.py` → `evaluate()`.

---

### DAY 5 — 🚪 GATE 1, then illumination

**Gate 1:** `python -m core.pipeline data/pairs/pair_01` runs end to end on a real lunar pair, no
manual steps, prints all five metrics.

**If it fails:** drop LoFTR, ship classical + illumination normalisation + sub-pixel + uniformity,
and **switch to Gate 2-alt** (Canonical Facts §11). Do not keep the original Gate 2 — comparing
classical against classical proves nothing, and the old plan never noticed that.

Then start `core/illumination.py`.

---

### DAY 6 — Illumination normalisation

- **Option A: phase congruency** — structure from phase, not intensity. `phasepack` on PyPI, or
  port Kovesi's MATLAB reference.
- **Option B: sign-invariant gradient orientation** — Sobel → orientation, discard sign so a
  crater rim looks the same whether lit from left or right.

Implement both, A/B on Rohan's Tier A pairs, keep the winner, **and keep the loser's numbers** —
"we tried both and here's the comparison" is a strong Q&A answer.

Test that matters: same crater, two sun angles → the same keypoints should survive.

---

### DAY 7 — Scale invariance + cross-sensor runs

Finish `core/scale.py`:
1. Read GSD from both metadata dicts
2. Resample both to a common GSD (use the coarser)
3. Coarse-to-fine pyramid: match at low res → estimate transform → refine at full res

Then run **Tier B** (OHRC↔LROC, ~1.8×) and **Tier B+** (OHRC↔Kaguya, ~36×). Log both.

> The 36× case is the one that proves scale invariance. If it fails without resampling and works
> with it, **that is your best technical slide.** Save both numbers.

- **Pairing session 2 (1 hr): Rishabh.** Walk him through UI integration.

---

### DAY 8 — Sub-pixel + distribution → 🚪 GATE 2

**`core/subpixel.py`** — per match: 11×11 patch from both images, normalised cross-correlation,
quadratic fit to the correlation peak, update coordinates to sub-pixel precision.

**`core/distribution.py`** — 8×8 grid over the reference image; cells with <2 matches trigger a
re-detect at a lowered threshold in that region; report `grid_coverage_fraction` and
`distribution_cv`.

**Gate 2 criteria** — Canonical Facts §11. Includes **producing matches on ≥1 Tier C multi-modal
pair**, with honest quantification of how much worse it is. Multi-modal is the PS title; it cannot
be absent from the gate.

**After Gate 2: STOP. No more algorithm work. `core/` is frozen.**

---

### DAY 9 — Build the UI

```python
import streamlit as st
from core.pipeline import run_all
from app.change_detection import detect_changes

st.set_page_config(page_title="LunarAlign — SIH26166", layout="wide")
st.title("LunarAlign — SIH26166")

col1, col2 = st.columns(2)
source = col1.file_uploader("Source (Chandrayaan-2)", type=["tif","tiff","img","png","jpg"])
ref    = col2.file_uploader("Reference (LROC / Kaguya / M3)", type=["tif","tiff","img","png","jpg"])

st.caption("Or pick a prepared pair:")
preset = st.selectbox("Prepared pairs", list_demo_pairs())   # from demo_cache/

if st.button("Align", type="primary"):
    with st.spinner("Matching… (CPU inference, no GPU required)"):
        st.session_state.result = run_all(source or preset_src, ref or preset_ref)

if "result" in st.session_state:
    warped, matches, metrics = st.session_state.result
    st.image([src_img, ref_img, warped], caption=["Source","Reference","Aligned"])
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Residual (px)", f"{metrics['residual_px']:.2f}")
    m2.metric("Inlier ratio", f"{metrics['inlier_ratio']:.0%}")
    m3.metric("Grid coverage", f"{metrics['grid_coverage_fraction']:.0%}")
    m4.metric("Distribution CV", f"{metrics['distribution_cv']:.2f}")
    if st.button("Detect Changes"):
        overlay, changes = detect_changes(warped, ref_img, gsd_mpp=metrics["gsd_mpp"])
        st.image(overlay); st.dataframe(changes)
```

> ⚠️ **Streamlit gotcha the old guide got wrong:** it nested `st.button("Detect Changes")` inside
> `if st.button("Align")`. Streamlit reruns the whole script on every interaction, so the inner
> button can never fire — clicking it re-runs with Align false and everything vanishes. **Use
> `st.session_state`** as above. This would have cost you an evening on Day 10.

> ⚠️ Label the pixel grid in the UI. `residual_px` is in **reference** pixels. Show the metres
> equivalent next to it — a judge will ask "sub-pixel of what?"

---

### DAY 10 — Comparison views → 🚪 GATE 3

- Swipe slider (`streamlit-image-comparison`) and checkerboard blend
- Side-by-side: ours vs Risheeth's best classical baseline, **numbers read from the CSV, never
  hardcoded**
- Match-distribution visualisation — the 8×8 grid overlaid, showing coverage. This is the picture
  that explains "uniform distribution" instantly to a faculty judge.

**Gate 3:** Rohan's stranger operates the UI and explains the output with nobody speaking.
Day 10, **before** freeze, so "fix the UX" is actually possible.

- **Pairing session 3 (1 hr): Samrudh + Rishabh.** Both must be able to restart the app and read a
  traceback without you. This matters for the 36-hour finale.

---

### DAY 11 — 🚪 CODE FREEZE + GATE 4

**Freeze.** Crash fixes, typos, path fixes only. Nothing else.

Gate 4 procedure — run it exactly like this:
1. Copy every demo input into `demo_cache/`
2. Verify `weights/` has the LoFTR weights
3. **Turn wifi off. Physically. Airplane mode.**
4. `streamlit run app/streamlit_app.py`
5. Full demo run ×3 consecutively. **Any crash = fail. Restart the count from zero.**
6. Close the laptop between runs — that's what actually happens on demo day

---

### DAY 12 — Rehearse, sleep

Final rehearsal. Gate 5 — you answer cold too. Sleep early; you'll need it more than one more
commit.

---

## 🛠️ NIGHTLY SPEC TEMPLATE (30 min, every night)

This is your highest-leverage half hour. Five people's next day depends on it.

```markdown
## TOMORROW: [Name] — [Module]

### Signature
def their_function(input1: type, input2: type) -> output_type

### Acceptance criteria
1. Input: [exact format — "numpy float32 HxW, range 0-1"]
2. Output: [exact format — "dict with keys rmse_gt_px, inlier_count, ..."]
3. Must pass: [named test]

### Test cases (2-3, with expected values)
1. ...
2. ...

### Starter code
```python
def their_function(input1, input2):
    # TODO
    pass
```

### Dependencies
- Needs from others: [MUST already exist. If it doesn't, this spec is invalid — rewrite it.]
- Delivers to: [who consumes this]

### Time estimate: 2 hrs
```

> **The dependency line is the important one.** Before you send a spec, check that everything it
> needs already exists. In the old plan, Risheeth and Rishabh were both scheduled on Day 2 to use
> a harness Samrudh wasn't finishing until Day 3. Both would have started blocked. **A spec whose
> dependencies aren't met yet is a bug you are shipping to a teammate.**

---

## 🚨 BLOCKER PROTOCOL

| Blocker | Your response |
|---|---|
| "I'm waiting for you" | **You failed to spec.** Fix the spec now, not tomorrow. |
| "OpenCV error" | Google it, 10 min, then pair for 15 min. |
| "Data not ready" | Synthetic or Tier A fallback. Nobody waits on data. |
| "Metric mismatch UI vs harness" | Almost always coordinate order (x,y) vs (row,col). Print shapes. |
| "UI crashes" | try/except + `st.error()`. Log the traceback. Fix tomorrow. |
| Teammate silent 2 days | Saniya checks in Day 4 and Day 7. Reassign by Day 7 if needed. |

---

## 🗣️ YOUR DEMO LINES (30 seconds)

> "The core problem is that the same crater looks completely different under different lighting,
> and Chandrayaan-2's cameras differ in resolution by up to a factor of thirty. So we do two things
> before matching: resample both images to a common ground scale using the mission metadata, and
> normalise illumination so features come from structure rather than brightness. Then LoFTR does
> dense matching — it works in the smooth maria where corner detectors find nothing. MAGSAC++
> removes outliers without threshold tuning, sub-pixel refinement uses cross-correlation peak
> fitting, and a grid constraint forces matches across the whole frame instead of clustering on
> bright features. All of this runs on this laptop, on CPU, with no GPU."

**Numbers in this script:** none, deliberately. Add exact figures the night before the demo,
read from `results_log.csv`. Never rehearse a number that doesn't exist yet.

---

## ✅ DELIVERABLES

- [ ] `core/io_loader.py` — PDS4 / PDS3 / GeoTIFF behind one interface
- [ ] `core/scale.py` — common-GSD resample + pyramid ← **the scale-invariance requirement**
- [ ] `core/illumination.py` — phase congruency or gradient orientation, both benchmarked
- [ ] `core/matcher.py` — LoFTR wrapper, weights loaded from `weights/`
- [ ] `core/ransac.py` — `cv2.USAC_MAGSAC`
- [ ] `core/subpixel.py` — 11×11 NCC + quadratic peak fit
- [ ] `core/distribution.py` — 8×8 grid enforcement
- [ ] `core/pipeline.py` — orchestrates, returns metrics dict
- [ ] `app/streamlit_app.py` — session_state, metrics panel, swipe, comparison, change detection
- [ ] `weights/` — cached, verified offline
- [ ] `demo_cache/` — all demo inputs
- [ ] Day-1 CPU benchmark posted
- [ ] Gates 1–5 passed
- [ ] 3 pairing sessions done (Days 4, 7, 10)

---

## 📞 YOUR ESCALATION

| Problem | Where |
|---|---|
| LoFTR / kornia API | kornia docs, `kornia.feature.LoFTR` |
| MAGSAC++ | `cv2.USAC_MAGSAC` — OpenCV USAC tutorial. **Not `pip install magsac`, it doesn't exist.** |
| PDS4 parsing | `pds4_tools` docs + the ISRO OHRC user guide in `data/docs/` |
| CH-2 ingestion reference | Ames Stereo Pipeline CH-2 tutorial — real product IDs and commands |
| Phase congruency | `phasepack`, or Kovesi's MATLAB reference |
| Streamlit reruns / state | Streamlit `session_state` docs — read this before Day 9 |
| Need GPU for an experiment | Kaggle: 30 guaranteed hrs/week. Code is identical — just the device string. |
| Team conflict | Saniya, then faculty guide |

---

## ⚡ DAILY ROUTINE

| When | What |
|---|---|
| Night before | Write 5 specs (30 min) — **check every dependency exists** |
| Morning | `git pull`, run the pipeline, read chat for blocks (15 min) |
| Core hours | Your module (4–5 hrs) |
| Evening | Read the day's diffs against spec, commit, write tomorrow's 5 specs as GitHub Issues (30 min) |

---

**You're not "the coder." You're the integration engineer.** Your code is the glue and your specs
are the scaffolding. Five people's ability to answer for their own work at Gate 5 depends on
whether your specs let them understand what they built, not just complete it.
