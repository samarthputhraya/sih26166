# Samrudh — Evaluation Lead Guide

**Role:** Build the scorecard that makes every other person's claim believable
**Time:** ~2 hrs/day | **This is the role that answers "how do you know it works?"**

> Read `00_CANONICAL_FACTS.md` §7 (metric definitions) before writing a line of code.

---

## 🔴 TWO THINGS THE OLD GUIDE GOT WRONG

**1. The metric was circular.** It said: *"Use matches to warp source onto reference. RMSE:
average distance between warped points and reference points."* That fits a transform **from** the
matches and then measures the error **of those same matches**. It measures how well a model fits
the points it was fitted to — not accuracy. It will produce a beautifully low number on a
completely wrong registration. An ISRO judge who has done registration will find this in one
question. **Fix: hold out 20%.** Details in §Day 3.

**2. The simulated sun-angle change wasn't one.** It said: *"Illumination change = multiply by a
smooth gradient."* That changes brightness. **Sun angle moves shadows** — it changes their
direction and length, which is the entire difficulty of the problem. A brightness ramp is not a
sun-angle change, and claiming it is would be indefensible.

**Fix:** render real lunar terrain from a DEM at two different sun positions. Real shadows, real
terrain, and you know the exact geometric relationship. This is now your Days 1–2 task and it is
the strongest evidence the whole team will have.

Also: the old guide's `scale (0.8-1.2)` is a 1.25× ratio. Our real ratios are **18–285×**.

---

## 🎯 YOUR MISSION

Build `evaluate()` — the function that turns "it looks aligned" into a number, plus the ground
truth that makes the number mean something.

Without you the team is guessing. With you they can prove it.

---

## 📅 YOUR 12-DAY PLAN

### DAY 1 — Setup + get the DEM

```bash
pip install opencv-contrib-python numpy pandas scikit-image matplotlib rasterio
```
(`python`, not `python3`, on Windows.)

Ask Rohan for the **SLDEM2015** tile (he delivers Day 4, but ask now — he may have it sooner).
SLDEM2015 is a LOLA + Kaguya merged elevation model, 512 pixels/degree ≈ 59 m/px.

Write the skeleton of `evaluation/shaded_relief.py`. Read the PS text so you know what you are
measuring toward.

---

### DAYS 1–2 — The ground-truth generator (your most valuable deliverable)

**`evaluation/shaded_relief.py`**

```python
import numpy as np

def render_shaded_relief(dem, sun_azimuth_deg, sun_elevation_deg, pixel_size_m):
    """Render a DEM as a shaded-relief image lit from a given sun position.

    This is standard hillshade. The point: the SAME terrain lit from two different
    sun positions gives two images with genuinely different shadows -- and we know
    exactly how their pixels correspond, because it is the same grid.
    """
    dzdx, dzdy = np.gradient(dem.astype(np.float64), pixel_size_m)
    slope  = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(-dzdy, dzdx)
    az = np.deg2rad(360.0 - sun_azimuth_deg + 90.0)
    ze = np.deg2rad(90.0 - sun_elevation_deg)
    shade = (np.cos(ze) * np.cos(slope)
             + np.sin(ze) * np.sin(slope) * np.cos(az - aspect))
    return np.clip(shade, 0, 1).astype(np.float32)
```

**`evaluation/synthetic_data.py`**

```python
def make_pair(dem, pixel_size_m,
              sun_a=(45, 30), sun_b=(225, 30),     # opposite azimuth -> shadows flip
              rotation_deg=None, scale=None, shift_px=None, seed=0):
    """Returns (source, reference, H_true, meta).

    reference = render(dem, sun_a)
    source    = warp(render(dem, sun_b), H_true)

    Two independent difficulties, both with EXACT ground truth:
      - illumination differs (real shadows, opposite direction)
      - geometry differs by a known homography H_true
    """
```

**Sampling ranges — use these, not the old ones:**

| Parameter | Range | Why |
|---|---|---|
| rotation | ±15° | orbit-to-orbit attitude difference |
| **scale** | **1× to 20×** | ← the old guide said 0.8–1.2×. Real ratios are 18–285×. **1.25× proves nothing.** |
| shift | ±20% of image width | realistic footprint offset |
| sun azimuth difference | **0° to 180°, swept** | the sun-angle experiment |
| sun elevation | 10° to 70° | grazing to high sun |

**The swept-azimuth curve is your best single figure.** Hold everything else fixed, sweep the sun
azimuth difference from 0° to 180°, plot `rmse_gt_px` against it, for our method and for SIFT.
Classical methods collapse as the difference grows; if ours doesn't, that one chart is the most
persuasive thing in the deck — and it is real, measured, and reproducible.

**Deliverable:** run `synthetic_data.py`, get pairs with exact answer keys.

---

### DAY 3 — `metrics.py`

```python
import numpy as np, cv2

GRID = 8
INLIER_THRESH_PX = 3.0

def evaluate(ref_shape, matches_src, matches_ref, H_true=None, holdout_frac=0.2, seed=0):
    """Score one registration.

    matches_src, matches_ref : (N,2) float arrays of (x, y), same order.
    H_true : ground-truth homography if known (synthetic / DEM pairs), else None.

    ALL pixel units are REFERENCE-image pixels.
    """
    rng = np.random.default_rng(seed)
    n = len(matches_src)
    idx = rng.permutation(n)
    n_hold = max(4, int(holdout_frac * n))
    hold, fit = idx[:n_hold], idx[n_hold:]

    # --- fit the transform on the FIT set only -----------------------------
    H, mask = cv2.findHomography(matches_src[fit], matches_ref[fit],
                                 method=cv2.USAC_MAGSAC,
                                 ransacReprojThreshold=INLIER_THRESH_PX,
                                 confidence=0.999)

    # --- residual on the HELD-OUT set (real pairs) -------------------------
    proj = cv2.perspectiveTransform(matches_src[hold].reshape(-1,1,2), H).reshape(-1,2)
    residual_px = float(np.sqrt(np.mean(np.sum((proj - matches_ref[hold])**2, axis=1))))

    # --- true accuracy vs ground truth (synthetic / DEM only) --------------
    rmse_gt_px = None
    if H_true is not None:
        h, w = ref_shape
        gx, gy = np.meshgrid(np.linspace(0, w-1, 20), np.linspace(0, h-1, 20))
        pts  = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32)
        ours = cv2.perspectiveTransform(pts.reshape(-1,1,2), H).reshape(-1,2)
        true = cv2.perspectiveTransform(pts.reshape(-1,1,2), H_true).reshape(-1,2)
        rmse_gt_px = float(np.sqrt(np.mean(np.sum((ours - true)**2, axis=1))))

    # --- inliers and spatial uniformity ------------------------------------
    err = np.linalg.norm(
        cv2.perspectiveTransform(matches_src.reshape(-1,1,2), H).reshape(-1,2) - matches_ref,
        axis=1)
    inlier = err < INLIER_THRESH_PX
    inlier_count = int(inlier.sum())

    h, w = ref_shape
    cells = np.zeros((GRID, GRID), dtype=int)
    for (x, y) in matches_ref[inlier]:
        r = min(int(y / h * GRID), GRID-1)
        c = min(int(x / w * GRID), GRID-1)
        cells[r, c] += 1

    return {
        "rmse_gt_px":             rmse_gt_px,                       # accuracy. None on real pairs.
        "residual_px":            residual_px,                      # held-out fit residual.
        "inlier_count":           inlier_count,
        "inlier_ratio":           inlier_count / max(n, 1),
        "grid_coverage_fraction": float((cells > 0).sum() / (GRID*GRID)),
        "distribution_cv":        float(cells.std() / cells.mean()) if cells.mean() > 0 else None,
        "n_matches":              n,
    }
```

### The two accuracy numbers are different things — never merge them

| | What it is | When |
|---|---|---|
| `rmse_gt_px` | **Accuracy.** Distance from the true transform, measured on a dense check grid. | Synthetic and DEM pairs only |
| `residual_px` | **Fit residual** on held-out matches. Lower bound on error, not accuracy. | Real pairs |

On a real lunar pair there is no ground truth. Anyone who reports `residual_px` as "our accuracy"
is overclaiming. **You are the person who stops that happening.** Say it out loud in rehearsals.

**Units:** everything is in **reference-image pixels**. Always report the metres equivalent
alongside — `residual_px × ref_gsd_mpp`. When a judge asks "sub-pixel of what?", the answer is
"of the reference grid; on LROC NAC that's half a metre per pixel."

---

### DAY 4 — Tests

`evaluation/test_metrics.py` — keep these three, they were well chosen in the old guide:

```python
def test_perfect_matches():      # identity -> rmse_gt_px ~ 0
def test_known_offset():         # shift by (2,3) -> residual ~ 3.606
def test_clustered_matches():    # all in one corner -> grid_coverage low, distribution_cv high
```

Add two more that catch the failure modes we now know about:

```python
def test_holdout_actually_holds_out():
    # Feed matches consistent with H1 for the fit set and garbage for the holdout.
    # residual_px must be LARGE. If it's small, the holdout isn't held out
    # and you've reintroduced the circularity bug.

def test_reports_none_without_ground_truth():
    # H_true=None -> rmse_gt_px is None, never 0.0.
    # A silent 0.0 here would put a fake "perfect accuracy" into the deck.
```

---

### DAY 5 — Integrate

Samartha calls `evaluate()` from `pipeline.py`. Every run appends one row to
`evaluation/results_log.csv`:

```csv
timestamp,pair_id,tier,method,config,rmse_gt_px,residual_px,inlier_count,inlier_ratio,grid_coverage_fraction,distribution_cv,n_matches,gsd_mpp
```

**The `tier` column is mandatory.** A number without its tier is meaningless — Tier A results say
nothing about multi-modal performance, and mixing them is exactly how a team accidentally
overclaims.

> **`results_log.csv` is the only source of numbers for the entire project.** Deck, demo script,
> Q&A bank — everything traces here. If it isn't in this file, nobody says it.

---

### DAY 6 — Tier A + the illumination curve

Run the full harness on Rohan's Tier A pairs (same sensor, different sun angle). Start the
swept-azimuth curve on DEM-rendered pairs: sun difference 0° → 180°, ours vs SIFT.

---

### DAY 7 — Tier B, and check one by hand

Run on Tier B (CH-2 OHRC ↔ LROC NAC).

**Then verify one pair manually.** Pick a result, open both images, click three obvious craters,
compute the offset yourself, compare to what the harness says. If they disagree, the harness is
wrong. This half hour is worth more than any amount of additional automation — it is also the
answer to "how do you know your metric is right?"

---

### DAY 8 — Full table + Tier C

Complete the evaluation table across all tiers. **Quantify the Tier C (multi-modal) degradation
honestly.** Optical-against-infrared will be worse than optical-against-optical. That is expected
and physically reasonable — say by how much and why. A team that reports a hard case honestly
reads as competent; a team whose every number is excellent reads as suspicious.

This feeds Gate 2. After Gate 2 the algorithm freezes, so these numbers are close to final.

---

### DAYS 9–10 — Verify the UI

Samartha's UI must show **exactly** what your CSV shows. Check every metric on three pairs.
When they disagree it is almost always coordinate order — `(x, y)` versus `(row, col)`. Print
shapes, debug with Samartha.

Then give Saniya the final numbers for the deck **in writing**, with the tier attached to each.

---

### DAYS 11–12 — Rehearse and Gate 5

**Your Gate 5 answers:**
- *"How do you know it works?"* → "Two ways. On DEM-rendered and synthetic pairs we know the true
  transform, so we measure real accuracy. On real lunar pairs there's no ground truth, so we hold
  out 20% of matches and report the residual — and we're careful not to call that accuracy."
- *"Why hold out?"* → "Otherwise you're measuring how well the model fits the points you fitted it
  to. That number can look excellent on a wrong registration."
- *"How did you simulate sun angle?"* → "We didn't simulate it. We rendered real lunar terrain
  from the LOLA-Kaguya DEM at different sun positions, so the shadows are physically real and we
  still know the exact pixel correspondence."
- *"What's your worst result?"* → know it, say it. Have the number ready.

---

## 🛠️ YOUR FILES

```
evaluation/
├── shaded_relief.py    # DEM -> hillshade at chosen sun azimuth/elevation
├── synthetic_data.py   # pair generator + exact answer keys
├── metrics.py          # evaluate()
├── test_metrics.py     # 5 tests
├── results_log.csv     # THE source of all numbers
└── README.md
```

---

## 💡 TIPS

| Situation | What to do |
|---|---|
| "I don't know how to warp" | `cv2.warpPerspective`. Ask Samartha for his helper. |
| "My RMSE is suspiciously low" | Check the holdout is actually held out. That was the old bug. |
| "OpenCV shape error" | `print(arr.shape, arr.dtype)`. Usually needs `(N,1,2) float32`. |
| "Numbers look wrong" | Test on synthetic where you know the answer. Always. |
| "Risheeth's format differs" | Write a 5-line adapter. Don't change your interface for one caller. |
| Tempted to fill the return dict with example values | **Don't.** The old guide's `evaluate()` returned hardcoded `0.73 / 142 / 0.71`. Those numbers escaped into the deck and the demo script as if measured. Return `None`, never a plausible-looking placeholder. |
| Blocked > 30 min | Post in chat. |

---

## ✅ DELIVERABLES

- [ ] `shaded_relief.py` — renders a DEM at any sun azimuth/elevation
- [ ] `synthetic_data.py` — pairs with exact ground truth, scale range to **20×**
- [ ] `metrics.py` — `evaluate()` with **held-out split**
- [ ] `test_metrics.py` — 5 tests including the two anti-regression tests
- [ ] `results_log.csv` — every run, with `tier`
- [ ] Swept sun-azimuth curve (ours vs SIFT)
- [ ] One pair verified by hand
- [ ] UI numbers == harness numbers, on 3 pairs
- [ ] Final numbers handed to Saniya in writing, tier-labelled

---

## 🗣️ WHAT TO SAY IN THE DEMO (30 seconds)

> "The hard part of proving this is that real lunar pairs have no ground truth. So we built two
> kinds of test. First, we render real terrain from the LOLA-Kaguya elevation model at different
> sun positions — real shadows, and we know the exact pixel correspondence, so we can measure true
> accuracy. Second, on real image pairs we hold out twenty percent of the matches and report the
> residual on those, and we're careful to call that a residual, not accuracy, because they're
> different things. Every run is logged with all five metrics — including spatial uniformity,
> because clustered matches give you a good average and a bad warp at the edges."

**Numbers:** insert from `results_log.csv` the night before. **Rehearse the sentences, not the
digits** — the digits change until Day 8.

---

## 📞 ESCALATION

| Problem | Ask |
|---|---|
| Warping / homography maths | Samartha |
| SLDEM file won't load | Rohan, then Samartha |
| Match format mismatch | Samartha / Risheeth |
| UI numbers disagree with CSV | Samartha — it's usually coordinate order |
| Not enough time | Saniya — she decides what goes in the deck |

---

**You're the proof person.** Everyone else produces claims; you produce the reason to believe
them. Your module is the smallest in the project and the one a technical judge will probe hardest.
