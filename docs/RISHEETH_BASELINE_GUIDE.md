# Risheeth — Baseline Lead Guide

**Role:** Run classical methods, show exactly where and why they fail
**Time:** ~2 hrs/day | **You produce the picture judges remember**

> Read `00_CANONICAL_FACTS.md` §2 (the tier ladder) and §7 (metrics) first.

---

## 🔴 THREE CHANGES FROM THE OLD GUIDE

**1. You are no longer blocked on Day 1.** The old plan had you running SIFT "on Samrudh's
synthetic pairs" on Day 2 — but Samrudh doesn't finish those until Day 3. You'd have started
blocked. **Now you make your own test pair in five lines of numpy on Day 1 and depend on nobody.**

**2. Every number in the old comparison table was invented.** "SIFT 4.2 · ORB 5.1 · AKAZE 3.8 ·
Ours 0.7 · 5.4×" and "SIFT: 12 matches, RMSE=8.2px, inlier_ratio=0.15" were placeholder values
that read like measurements. They had already propagated into the demo script and the Q&A bank.
**Every cell you publish must come from `evaluation/results_log.csv`.**

**3. Your comparison must be a fair one.** See the ablation below — this is the biggest upgrade to
your role.

---

## 🎯 YOUR MISSION

Run SIFT, ORB and AKAZE through Samrudh's harness. Find where they break. Make it visible in two
seconds. Build the comparison table that turns "ours is better" into something a judge can check.

**This is "run scripts, log numbers, make pictures" — not research.** If something takes more than
20 minutes to debug, post in chat and move on.

---

## ⭐ THE ABLATION — READ THIS BEFORE YOU BUILD THE TABLE

The obvious comparison is *our full pipeline* vs *bare SIFT*. A sharp judge will immediately say:
**"You're comparing your entire pipeline against a raw baseline. How much of the gain is the
learned matcher and how much is your preprocessing?"**

That question is fatal if unprepared and a gift if prepared. So run **four** configurations, not two:

| Config | Illumination normalisation | Matcher | What it isolates |
|---|---|---|---|
| **1** | ✗ | SIFT / ORB / AKAZE | the true raw baseline |
| **2** | ✓ (Samartha's `illumination.py`) | SIFT / ORB / AKAZE | **how much our preprocessing alone buys** |
| **3** | ✗ | LoFTR | how much the learned matcher alone buys |
| **4** | ✓ | LoFTR | the full system |

Config 2 is the one nobody expects and the one that makes the work look rigorous. If our
illumination normalisation lifts plain SIFT substantially, that is a genuine, separable
contribution — and it survives even if the learned matcher gets dropped at Gate 1.

Ask Samartha for `from core.illumination import normalize` on Day 6. One import.

---

## 📅 YOUR 12-DAY PLAN

### DAY 1 — Working, dependent on nobody

```bash
pip install opencv-contrib-python numpy pandas matplotlib
```
(`opencv-contrib-python` has SIFT. Use `python`, not `python3`, on Windows.)

**Make your own test pair — no waiting:**
```python
import cv2, numpy as np
img = cv2.imread("any_image.jpg", 0)          # literally any photo
M   = np.float32([[1, 0, 7], [0, 1, 5]])      # shift 7 right, 5 down
shifted = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
cv2.imwrite("my_test_source.png", shifted)
cv2.imwrite("my_test_ref.png", img)
# You now know the exact answer: dx=7, dy=5.
```

Write `baselines/sift_baseline.py`:

```python
import cv2, numpy as np

def run_sift(img1, img2, nfeatures=0):
    """img1=source, img2=reference, both uint8 grayscale.
    Returns (src_pts, ref_pts) as (N,2) float32 arrays."""
    sift = cv2.SIFT_create(nfeatures=nfeatures)
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
        return np.zeros((0,2), np.float32), np.zeros((0,2), np.float32)

    flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    knn = flann.knnMatch(des1, des2, k=2)

    good = [m for pair in knn if len(pair) == 2
            for m, n in [pair] if m.distance < 0.7 * n.distance]

    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 2)
    ref = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 2)
    return src, ref
```

> ⚠️ **The old guide's version crashes.** `for m, n in matches` throws `ValueError` when
> `knnMatch` returns a single match for some descriptor — which happens constantly on
> low-texture lunar imagery. The guard above is why. It also didn't handle `des is None`, which
> is the *normal* outcome on a dark mare region and would have crashed you on real data.

Verify: your shifted pair should give matches whose average offset is ≈ (7, 5).

**Day 1 deliverable:** SIFT running, offset recovered correctly on your own pair.

---

### DAY 2 — All three baselines

Copy the file twice:
- `orb_baseline.py` → `cv2.ORB_create(nfeatures=5000)`
- `akaze_baseline.py` → `cv2.AKAZE_create()`

> ⚠️ **ORB and AKAZE need a different matcher.** They produce **binary** descriptors; FLANN's
> KD-tree is for float descriptors like SIFT's. Use:
> ```python
> bf = cv2.BFMatcher(cv2.NORM_HAMMING)
> knn = bf.knnMatch(des1, des2, k=2)
> ```
> The old guide said *"Use same matcher code"* — that silently produces garbage matches or an
> assertion error. This would have cost you a day.

Write `baselines/run_all_baselines.py` — takes a pair, runs all three, appends to CSV.

**Day 2 deliverable:** three baselines, all working on your own pair, logging to CSV.

---

### DAY 3 — Samrudh's synthetic pairs

His generator is ready. Run all three against pairs with **real DEM-rendered shadows** at
different sun angles. This is the first honest look at how classical methods handle illumination.

Expect SIFT to struggle badly as the sun-azimuth difference grows. **That's the finding, not a
bug.** Log it.

---

### DAY 4 — Tier A real pairs

Rohan's Tier A set: LROC NAC, same site, incidence differs ≥15°. Same sensor — this isolates
illumination cleanly.

**Terminology:** Tier A is a **sun-angle** test. It is **not** cross-sensor and **not**
multi-modal. Never label it either in your table.

---

### DAY 5 — Failure gallery v1

Pick the **3 worst** cases from your logs. For each, one image showing:
- matches drawn as lines, **green = inlier, red = outlier**
- the caption with **the real numbers from your CSV**

```python
def draw_failure(img_src, img_ref, src_pts, ref_pts, inlier_mask, method, pair_id, metrics):
    vis = np.hstack([img_src, img_ref])
    off = img_src.shape[1]
    for (x1,y1), (x2,y2), ok in zip(src_pts, ref_pts, inlier_mask):
        colour = (0,255,0) if ok else (0,0,255)
        cv2.line(vis, (int(x1),int(y1)), (int(x2)+off,int(y2)), colour, 1)
    caption = (f"{method} | {metrics['n_matches']} matches | "
               f"residual {metrics['residual_px']:.1f}px | "
               f"inliers {metrics['inlier_ratio']:.0%} | "
               f"coverage {metrics['grid_coverage_fraction']:.0%}")
    cv2.putText(vis, caption, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.imwrite(f"baselines/failure_gallery/{pair_id}_{method}_failure.jpg", vis)
```

**Every number in that caption comes from the metrics dict.** Never type a number by hand.

Make it obvious in two seconds: a wall of red lines going to the wrong places. A faculty judge who
knows no computer vision must be able to see that this one is bad.

---

### DAY 6 — Gallery final + the ablation begins

Annotate each gallery image with **why** it failed, in one plain sentence:
- "SIFT matched shadow edges rather than crater rims — the shadows moved between images."
- "All matches landed on one bright ejecta ray; the rest of the frame has none."
- "Detector found almost nothing in the smooth mare."

Then get `from core.illumination import normalize` from Samartha and start **Config 2** — the
three classical methods *with* our preprocessing.

---

### DAY 7 — Tier B

Run on Tier B (CH-2 OHRC ↔ LROC NAC). This is genuinely cross-sensor. Also genuinely harder —
expect worse numbers across the board, including for us.

---

### DAY 8 — Tier C + table v1

Run on the Tier C multi-modal pair (optical ↔ infrared). Classical methods will likely fail almost
completely here. **That is a legitimate and important result** — it is precisely why the PS exists.

Build comparison table v1. Mark it DRAFT.

---

### DAY 9 — Comparison table FINAL

Safe now: the algorithm froze at Gate 2 on Day 8, so the "Ours" column is stable.

> The old plan had you producing "Final comparison table v2" on **Day 7**, while Samartha was
> still adding sub-pixel refinement on Day 8 and distribution on Day 9. The table would have been
> wrong before it was printed.

**Structure — note the tier column and the ablation rows:**

| Pair | Tier | Sun Δ | Scale | SIFT | SIFT+illum | ORB | AKAZE | LoFTR | **Ours (full)** |
|---|---|---|---|---|---|---|---|---|---|
| pair_01 | A | 26° | 1× | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| pair_07 | B | — | 1.8× | [TBD] | … | | | | |
| pair_09 | B+ | — | 36× | [TBD] | … | | | | |
| pair_11 | **C** | — | — | [TBD] | … | | | | |

**Leave `[TBD]` until the CSV has the value.** A blank cell is honest; an invented one is fatal.

Save as `baselines/results_table.csv` plus a formatted version for Saniya.

---

### DAY 10 — UI + hand-off

Give Samartha the baseline numbers for the UI's side-by-side panel — **as a CSV he reads at
runtime, not as numbers he hardcodes.** Give Saniya the gallery images and the final table.

---

### DAYS 11–12 — Rehearse and Gate 5

**Your Gate 5 answers:**
- *"Why these three baselines?"* → "SIFT is the standard reference. ORB and AKAZE are the fast
  binary-descriptor alternatives you'd actually use in an operational pipeline. Together they cover
  what a practitioner would try first."
- *"Isn't comparing your full pipeline to raw SIFT unfair?"* → **"Yes, which is why we also ran
  SIFT with our illumination normalisation. That row separates the preprocessing contribution from
  the matcher contribution."** ← the ablation, and the strongest thing you say
- *"SIFT gets 0.2 px in published papers. Why is yours worse?"* → "Those are same-sensor,
  similar-illumination pairs. Ours are cross-sensor with large sun-angle differences. Different
  problem."
- *"What if SIFT is good enough?"* → point at the Tier C row and the failure gallery.
- *"Which of your results is weakest?"* → know it. Say it.

---

## 🛠️ TOOLS

```bash
pip install opencv-contrib-python numpy pandas matplotlib
```

---

## 📁 YOUR FILES

```
baselines/
├── sift_baseline.py
├── orb_baseline.py          # BFMatcher + NORM_HAMMING, not FLANN
├── akaze_baseline.py        # BFMatcher + NORM_HAMMING, not FLANN
├── run_all_baselines.py     # all methods x all configs x all pairs -> CSV
├── draw_failure_gallery.py
├── results_table.csv
└── failure_gallery/
```

---

## 💡 TIPS

| Situation | What to do |
|---|---|
| "SIFT not found" | `pip install opencv-contrib-python` |
| `ValueError: not enough values to unpack` in the ratio test | knnMatch returned 1 match. Guard with `if len(pair)==2` — see Day 1 code. |
| `des1 is None` | No keypoints found. **That is a result, not a crash.** Return empty arrays and log zero matches. |
| ORB/AKAZE give nonsense matches | You're using FLANN KD-tree on binary descriptors. Switch to `BFMatcher(NORM_HAMMING)`. |
| "Too few matches" | Try ratio 0.75, raise `nfeatures`. If it's still bad — **that's the finding.** Gallery it. |
| "All matches in one corner" | **That's the finding.** `distribution_cv` will be high. Gallery it. |
| Running slow | Downscale to ~1000 px wide before matching. Record that you did. |
| Samrudh's format differs | Five-line adapter on your side. |
| Tempted to fill a table cell to make it look complete | **Don't.** Write `[TBD]`. |
| Blocked > 20 min | Post in chat. |

---

## ✅ DELIVERABLES

- [ ] Three baseline scripts, all handling the empty-descriptor case without crashing
- [ ] `run_all_baselines.py` — all methods × 4 configs × all pairs → CSV
- [ ] `results_table.csv` — every cell traceable to `results_log.csv`, `tier` column present
- [ ] **The ablation row: classical *with* our illumination normalisation**
- [ ] `failure_gallery/` — 3–4 images, obvious in two seconds, real captions
- [ ] One plain-language failure explanation per gallery image
- [ ] Baseline numbers handed to Samartha as a CSV, not as hardcoded values

---

## 🗣️ WHAT TO SAY IN THE DEMO (30 seconds)

> "We ran three classical methods — SIFT, ORB and AKAZE — across the whole dataset. The table has
> the numbers, but the picture tells it better: look at the red lines. SIFT is matching shadow
> edges instead of crater rims, because the shadows moved between the two images. On the
> multi-modal pair it barely finds anything at all. And we ran a fourth configuration — classical
> SIFT *with* our illumination normalisation — so we can separate how much comes from the
> preprocessing and how much from the matcher. That's the row that shows our preprocessing is
> doing real work, independent of the learned model."

**Insert the actual figures the night before, from the CSV.** Rehearse the sentences, not the digits.

---

## 📞 ESCALATION

| Problem | Ask |
|---|---|
| OpenCV install or error | Samartha |
| `illumination.normalize` for the ablation | Samartha (Day 6) |
| Match format for the harness | Samrudh |
| Need pairs | Rohan |
| Which failures to feature | Saniya + Samartha |

---

**You don't need to invent anything.** Run OpenCV, log numbers, make the failures obvious. The
comparison is the persuasive part — and the ablation is what makes it credible rather than just
flattering.
