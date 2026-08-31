# Day 3 specs — 1 Sep 2026

Every dependency below was verified against the working tree before being written. Paste each
section into a GitHub Issue assigned to that person.

**The team is not uniformly on Day 3.** Samrudh and Saniya are being re-issued **Day 1**; Risheeth
gets **Day 2**. That is deliberate — see "Slipped" at the bottom.

| Person | What they get | Already written? |
|---|---|---|
| **Samrudh** | `evaluation/metrics.py` — **the Gate-1 blocker** | new, below |
| **Risheeth** | Day 2 — tune the three baselines, log CSV | new, below |
| **Saniya** | Day 1 re-issued — the SIH template | new, below (long form: `day01_saniya_template.md`) |
| **Rohan** | `ROHAN_DO_THIS_NOW.md` — send this one only | ✅ exists, verified |
| **Rishabh** | `day03_rishabh_change_detection.md` | ✅ exists, **Step 0 added tonight** |

---

## 🔴 [Day 3] Samrudh — `evaluation/metrics.py` — THE GATE-1 BLOCKER

`core/pipeline.py` already calls your function and prints *"the five metrics cannot be reported"*.
Gate 1 is **Day 5** and its criterion is *"prints all five metrics"*. **Nothing else in the project
is on the critical path today. Do this and only this.**

### Signature — FIXED, two callers already pushed

```python
def evaluate(ref_shape, matches_src, matches_ref,
             H_true=None, holdout_frac=0.2, seed=0) -> dict:
```

- `core/pipeline.py` calls it **positionally**: `evaluate(b.shape[:2], src_in, ref_in, H_true=H_true)`
- `baselines/run_all_baselines.py` calls it **all-keyword**

Rename anything and you silently break Samartha's pipeline and Risheeth's runner.

### Acceptance criteria

1. `matches_src` / `matches_ref` are `(N,2)` **`(x, y)`** — *not* `(row, col)`. `float32` in, accept
   `float64` and lists (`np.asarray` first).
2. Returns a dict with exactly these keys:
   `rmse_gt_px · residual_px · inlier_count · inlier_ratio · grid_coverage_fraction ·
   distribution_cv · n_matches`
   **`rmse_gt_px` is `None` when `H_true is None`. Never a placeholder number.**
3. **Never raises.** `pipeline.run_all` sometimes hands you a `(0,2)` empty array. An exception kills
   an unattended Gate-1 run. Return the dict with `None`s and a `note`.
4. `GRID = 8`, `INLIER_THRESH_PX = 3.0` (matches `core/ransac.DEFAULT_THRESHOLD_PX`).
5. `pytest evaluation/ -q` exits **0** with 5 tests (currently exits 5 — no tests collected).

### Test cases — measured on this venv, not estimated

1. **`test_perfect_matches`** — 60 points, `ref == src`, `H_true = eye(3)`
   → `rmse_gt_px < 1e-6` · `residual_px == 0.0` · `inlier_count == 60`
2. **`test_known_offset`** — `ref = src + (2,3)`, `H_true = eye(3)`
   → **`rmse_gt_px == 3.6055 ± 0.001`** (= √13) and **`residual_px == 0.0`**
   ⚠️ **Your guide says this test gives `residual ≈ 3.606`. That is wrong and will cost you an
   hour.** `residual_px` is measured *after* fitting, so the fit absorbs the shift → ~0. The 3.606
   belongs to `rmse_gt_px`.
3. **`test_clustered_matches`** — 40 points all inside one 80px cell of a 640×640 frame
   → `grid_coverage_fraction == 0.015625` (1/64) · `distribution_cv == 7.9373 ± 0.001` (= √63)
4. **`test_holdout_actually_holds_out`** — 50 points, `ref = src + (5,0)`, then corrupt exactly the
   points `evaluate(seed=0)` will hold out by `+(100,100)`
   → **`residual_px == 141.4214 ± 0.01`** (= 100√2), `inlier_count == 40`.
   **If this comes back small, your holdout isn't held out and the circularity bug is back.**
5. **`test_reports_none_without_ground_truth`** — `H_true=None` → `rmse_gt_px is None`.
   **Assert `is None`, not `== 0`.** A silent `0.0` puts fake "perfect accuracy" in the deck.

### Starter

```python
import numpy as np, cv2
GRID, INLIER_THRESH_PX, MIN_FIT = 8, 3.0, 4

def evaluate(ref_shape, matches_src, matches_ref, H_true=None,
             holdout_frac=0.2, seed=0):
    src = np.asarray(matches_src, np.float32).reshape(-1, 2)
    ref = np.asarray(matches_ref, np.float32).reshape(-1, 2)
    n = len(src)
    empty = {"rmse_gt_px": None, "residual_px": None, "inlier_count": 0,
             "inlier_ratio": 0.0, "grid_coverage_fraction": 0.0,
             "distribution_cv": None, "n_matches": n, "note": ""}
    if len(ref) != n or n < MIN_FIT * 2:
        empty["note"] = f"only {n} matches; need >= 8"; return empty

    # hold out FIRST, then fit. Never the other way round.
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    n_hold = min(max(MIN_FIT, int(holdout_frac * n)), n - MIN_FIT)
    hold, fit = idx[:n_hold], idx[n_hold:]

    # TODO cv2.findHomography(src[fit], ref[fit], cv2.USAC_MAGSAC,
    #                         ransacReprojThreshold=INLIER_THRESH_PX) -> (H, mask)
    # TODO residual_px : perspectiveTransform(src[hold], H) vs ref[hold], RMSE
    # TODO rmse_gt_px  : only if H_true is not None. 20x20 check grid over ref_shape,
    #                    transform by H and by H_true, RMSE between them. Else None.
    # TODO inliers     : err over ALL n under H, err < INLIER_THRESH_PX
    # TODO 8x8 cells of ref[inliers]:
    #        r = min(int(y / h * GRID), GRID-1); c = min(int(x / w * GRID), GRID-1)
    #        grid_coverage_fraction = (cells > 0).sum() / 64
    #        distribution_cv = cells.std() / cells.mean()
```

`cv2.perspectiveTransform` needs `(N,1,2) float32` — reshape in and out.

### Dependencies — all verified present
`numpy` + `cv2` only (**no torch, no rasterio, no pandas today**) · nothing from any teammate ·
`core/pipeline.py::_evaluate()` ✅ · `core/ransac.py::filter_matches` returns `(N,2) float32` ✅ ·
no `__init__.py` needed, `evaluation/` resolves as a namespace package ✅ (confirmed by running it).

### Do not
- **Do not fit on all matches then measure residual on those same matches** — the exact bug in
  Canonical Facts §7.
- **Do not return `0.0` for `rmse_gt_px` when there's no ground truth.** Return `None`.
- **Do not `pip install magsac`** — no such package. `cv2.USAC_MAGSAC` is `38`, verified.
- **Do not let `findHomography` raise** — under 4 points it raises; all-collinear returns
  `(None, None)` without raising. Both happen on real pairs.
- **Do not import from `core/`** — `core.pipeline` imports you; that's a cycle.
- **Do not start `shaded_relief.py` today.** Deferred to Day 4 deliberately.

**Time: 2 hrs.** ~20 min install, ~60 min `metrics.py`, ~40 min the five tests.

---

## [Day 2] Risheeth — `baselines/tune_baselines.py`

Day 1 delivered and verified — all three recover `(-7,-5)` exactly, and you dodged all three
OpenCV-5 traps unprompted. This is your Day-2 row: *tune all three, log CSV.*

### Goal
A CSV showing, against **known ground truth**, what the Lowe ratio actually costs and buys for
SIFT/ORB/AKAZE across three difficulty levels — so Day-6's failure gallery is tuned, not guessed.

### Signature
```python
def make_hard_pair(dx=7, dy=5, rotation_deg=0.0, scale=1.0, seed=0)
    # -> (source, reference, H_true)   H_true maps SOURCE (x,y) -> REFERENCE (x,y)
def score(src_pts, ref_pts, H_true, thresh_px=3.0) -> dict
def sweep(ratios=(0.6, 0.7, 0.75, 0.8, 0.9)) -> list[dict]
```
Add a `ratio=` keyword to your three existing entry points, defaulting to today's values so nothing
breaks.

### Acceptance criteria
1. Reuses your own `make_test_pair.make_pair` texture. **Do not change `make_pair`'s return arity** —
   `run_all_baselines.py` unpacks it as 2 values.
2. `baselines/results_table.csv`, 45 rows + header:
   `difficulty,method,ratio,n_matches,gt_inliers,gt_inlier_ratio,median_err_px,seconds`
   `difficulty ∈ {easy, rot10, scale15}`.
3. **`score()` uses `H_true`, never a fitted homography.** That's real accuracy — and it's exactly
   why you don't need Samrudh.
4. One chat line: *"the ratio that maximises matches is not the ratio that maximises correct
   matches — here's the number."*

### Test cases — measured on your own `make_pair(seed=0)`
1. `easy, AKAZE, 0.75` → `n_matches ≈ 1922`, `gt_inlier_ratio ≈ 0.998`, `median_err_px ≈ 0.0`
   (1922 is exactly your Day-1 count — confirms the harness agrees with your own run.)
2. **`ratio=0.9` is worse everywhere at `scale15`:** SIFT `0.849 < 0.987` · ORB `0.636 < 0.958` ·
   AKAZE `0.695 < 0.986` — while `n_matches` goes *up* (ORB 2351 vs 850).
3. `easy, ratio=0.75`: ORB `median_err_px ≈ 0.283` while SIFT and AKAZE are `0.0`. ORB's
   integer-grid keypoints cost sub-pixel accuracy even on a trivial pair — that single row is a
   legitimate line in the comparison table.

### Dependencies — all verified present
`make_test_pair.make_pair` ✅ · `run_sift` / `run_orb` / `run_akaze`, all returning `(N,2) float32
(x,y)` ✅ · **nothing from Samrudh** — your ground-truth `score()` replaces `metrics.py` here, and
is arguably better because you have `H_true`.

### Do not
- **Do not write to `evaluation/results_log.csv`.** Samrudh owns that file and starts writing it
  today; two people appending to one CSV on `main` is a guaranteed merge conflict git cannot
  resolve. Yours is `baselines/results_table.csv` (Canonical Facts §14 assigns it to you).
- **Do not tune for maximum matches.** The data disproves it: `0.9` gives ORB 2351 matches at 64%
  correct; `0.6` gives 850 at 96%. More matches at a worse ratio is a *worse* baseline — and it
  makes our own method look artificially good, which is what an ISRO judge catches.
- **Do not use FLANN for ORB/AKAZE** — binary descriptors need `BFMatcher(NORM_HAMMING)`, which you
  already correctly wrote.
- **Do not put these numbers in a slide.** Synthetic texture. They reach the deck only via
  `results_log.csv`.

**Time: 2 hrs.** The 45-row sweep runs in under a minute — the time is in reading it.

---

## [Day 1 — re-issued] Saniya — `presentation/TEMPLATE_HEADINGS.md`

`presentation/` still contains only `.gitkeep`. This has been outstanding three days and blocks
every slide from Day 3 on. **No repo access, no Python, no teammate needed.**

### Acceptance criteria
1. Download `https://sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx` —
   **exactly 924,505 bytes.** ✅ Re-checked today: HTTP 200, `Content-Length: 924505`.
   A different size means you got the 2025 file.
2. `presentation/TEMPLATE_HEADINGS.md` committed and pushed — one row per slide, heading **and its
   bullet prompts**, transcribed from the file *you* opened.
3. One chat message: *"There is no Problem Statement slide. The six-slide cap includes the title
   page. We have five content slides."*

### Test cases
1. The file has **7** slides — 6 template + a final instructions slide we delete.
2. The six, in order: **TITLE PAGE · IDEA TITLE · TECHNICAL APPROACH · FEASIBILITY AND VIABILITY ·
   IMPACT AND BENEFITS · RESEARCH AND REFERENCES**. **If your file differs, the file wins — say so
   immediately.**
3. The instructions slide says verbatim: *"Kindly keep the maximum slides limit up to six (6).
   (Including the title slide)"* → **five content slides.**

### Dependencies — verified
`presentation/` exists ✅ · URL live at the exact byte count ✅ ·
`git check-ignore presentation/deck.pptx` → `.gitignore:31:*.pptx` ✅ (binary ignored, markdown not).

### Do not
- **Do not download `SIH2025-…`** — the filenames differ by two characters. Check the byte count.
- **Do not `git add -f` the `.pptx`** — it's gitignored deliberately; `git add` will silently do
  nothing and you'll think it worked. Commit the markdown; the binary goes to Drive.
- **Do not add a seventh slide, rename a heading, or delete a bullet prompt.** The template forbids
  changing the pointers and format clarity is scored.
- **Do not write slide content today.** Content on the wrong structure gets rebuilt.
- **Do not put any number in any slide.** Write `[TBD — results_log.csv]`.

**Time: 2 hrs.** Full version: `ops/specs/day01_saniya_template.md`.

---

## Rohan and Rishabh — existing specs verified

**Rohan → send `ROHAN_DO_THIS_NOW.md` only.** All dependencies re-checked today: `io_loader.load()`
✅ · Kaguya URL HTTP 200 ✅ · gitignore rules ✅ · `DATASET_CARD.md` present ✅.
⚠️ Part D duplicates `day03_rohan_kaguya.md` — send the one guide or he'll do Kaguya twice.
⚠️ `DATASET_CARD.md` still says `SDRPHO` at lines 14 and 18, confirming he hasn't reached Part E.

**Rishabh → `day03_rishabh_change_detection.md`, Step 0 added tonight.** The spec called
`run_all()`, which needs torch + kornia + the 46 MB weights — **he has none of them**, and Day-1
setup explicitly told him not to install torch. Step 0 now covers the CPU-index install and
`fetch_weights.py` (self-contained, no Drive needed), plus a fallback if LoFTR is too slow.
Honest new estimate: **~2h15m** — consider cutting his hand-classification to 10 detections.
⚠️ Also verified: `io_loader` accepts only `.xml .lbl .img .tif .tiff` — a `.png` pair raises.

---

## Sequencing risks — decided tonight

1. **Two writers on `results_log.csv`.** `run_all_baselines.py` already targets it and Samrudh's
   Day-5 integration will too. **Decision: Samrudh owns `results_log.csv` and its schema;
   Risheeth's tuning goes to `baselines/results_table.csv`.** Written into both specs.
2. **`weights/loftr_outdoor.pt` exists on exactly one laptop and there's no Drive folder.** Every
   teammate who ever calls `run_all()` hits this. `fetch_weights.py` works over plain network, so
   it's survivable — but **test it on one teammate's machine before Day 5, not at Gate 4.**
3. **Gate 1 needs three late things at once:** `evaluate()` (Samrudh, not started), a real pair in
   `data/pairs/` (Rohan, not started), `illumination.py` (Samartha, not gate-critical). Two are on
   people who've delivered nothing this week.
4. **No slack left:** if Samrudh slips `metrics.py` to Day 4, Samartha's Day-4 integration has
   nothing to integrate and **Gate 1 fails on Day 5.** Escalate Day 4 morning, not Day 5.
5. **Tier C (multi-modal) — in the PS title, a hard Gate-2 criterion, no data, no owner action.**
   Decide the owner by Day 5.

## Slipped from the plan — flagged, not papered over

- **Samrudh is 2 days behind.** Order inverted deliberately: `metrics.py` (his Day-3 row) first
  because it's the only Gate-1 blocker; `shaded_relief.py` + `synthetic_data.py` slip to Days 4–5.
  **Consequence:** the swept sun-azimuth curve (his strongest figure) and Tier D ground truth drift
  toward Gate 2 — and `rmse_gt_px < 0.5 on synthetic` is a Gate-2 criterion needing
  `synthetic_data.py`.
- **Saniya is 3 days behind** on a task blocking Days 3–7 of the deck. The one-day cushion the
  slide re-count freed is now spent.
- **Rohan is a day behind on Day 1.** Realistically CH-2 + Tier A tomorrow, Kaguya Day 4 — that is
  acceptable (Tier B+ isn't needed until Day 7). **CH-2 slipping further is not.**
- **Risheeth is one day behind on the calendar but ahead on substance** — `run_all_baselines.py` and
  `draw_failure_gallery.py` are Day-5/6 deliverables he wrote on Day 1. **Do not tell him he's
  behind.**
- ⚠️ **`TEAM_TASK_GUIDE.md` Day-3 rows for both Risheeth and Rishabh say "on Samrudh's synthetic
  pairs"** — the same two-people-blocked-on-one-unfinished-harness mistake this project already
  caught once. Rishabh's is rewritten; **Risheeth's Day 3 should become "run the tuned baselines on
  Rohan's real Tier A pair"** (his Day-4 row pulled forward). The guide's table needs correcting,
  not just working around.
