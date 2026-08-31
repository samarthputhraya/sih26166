# [Day 3] Rishabh — change detection on REAL lunar imagery, aligned by the real pipeline

**Time: ~2 hrs.** Day 1 is done and pushed — good work, and you avoided both OpenCV 5 traps
unprompted. This is the next step.

---

## ⚠️ Your Day-3 row changed, and here is why

`TEAM_TASK_GUIDE.md` says *"Run change detection on **Samrudh's** synthetic aligned pairs."*
**Samrudh has not pushed anything yet** — `evaluation/` still contains only `.gitkeep`. Writing you
a spec that depends on a file which does not exist would leave you blocked on day three, and this
project's own rule is that *a spec whose dependencies aren't met is a bug shipped to a teammate.*

So Day 3 is now **self-contained** and, better, moves you off synthetic circles onto **real lunar
imagery aligned by the real pipeline**. Everything you need exists and is pushed.

---

## Goal, in one sentence

`detect_changes()` runs on a genuinely aligned pair of **real lunar images**, and you can state
honestly how many of its detections are real changes versus registration artifacts.

---

## 🔴 Step 0 FIRST — install what the pipeline needs (~25 min)

**This step was missing from the first version of this spec. You would have hit it at Step 3 and
been stuck.** Step 3 calls `core.pipeline.run_all()`, which uses the LoFTR matcher — that needs
PyTorch, kornia, and a 46 MB weights file you don't have. Day-1 setup deliberately told you *not*
to install torch, so you don't have it.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install kornia certifi
python core/fetch_weights.py
```

`fetch_weights.py` downloads the model weights and checks them against a known fingerprint. It is
self-contained — you don't need the Google Drive folder for this.

⚠️ **Use that exact CPU index URL.** The default `pip install torch` pulls ~2 GB of NVIDIA GPU code
that is useless here — there is no CUDA anywhere on this project.

**If `fetch_weights.py` fails, or LoFTR is unbearably slow on your machine, say so in chat within
30 minutes — don't burn your afternoon on it.** Fallback: you already know the transform `H`, so
skip `run_all` entirely and warp directly with
`cv2.warpPerspective(src, H, (640, 640), flags=cv2.INTER_CUBIC)`. You lose "aligned by the real
pipeline", but the whole change-detection exercise still works.

---

## Step 1 — Get a real lunar image (10 min)

Public, no login, 22.6 MB. Verified working on 31 Aug 2026:

```
https://astrogeo-ard.s3.us-west-2.amazonaws.com/moon/kaguya/terrain_camera/monoscopic/uncontrolled/TC1S2B0_01_03482S746E0433/TC1S2B0_01_03482S746E0433.tif
```

Put it in `data/raw/` (gitignored — do not commit it, and never `git add -f`).

🔴 **Two things about this file that will confuse you if nobody says them:**
- **51.8% of it is NoData with fill value `-32768`.** Mask it: `valid = img != -32768`.
  An unmasked fill region reads as an enormous "change" and will swamp your detector.
- It is a **polar** scene, so much of it is in deep shadow. **Use the window below** — I searched
  the scene for you. `x=5120, y=2240` is fully valid (no NoData), only **4% dark**, std 189, and
  full of craters and ridges. Avoid `x=3200, y=640`: it is fully valid but ~90% shadow, which
  would give you a false negative and waste your afternoon.

## Step 2 — Make an aligned pair, using the real pipeline (45 min)

```python
import sys; sys.path.insert(0, '.')
import numpy as np, cv2
from core.io_loader import load
from core.pipeline import run_all

img, meta = load(r'data/raw/TC1S2B0_01_03482S746E0433.tif')
img = np.where(img == -32768, 0, img)          # mask the fill FIRST

ref = img[2240:2880, 5120:5760]                 # 640x640 of well-lit real terrain

# "before" = the same ground, seen slightly differently (a real registration problem)
H = np.array([[1.0, 0.0, 9.0], [0.0, 1.0, -6.0], [0.0, 0.0, 1.0]])
src = cv2.warpPerspective(ref, np.linalg.inv(H), (640, 640), flags=cv2.INTER_CUBIC)

# now PLANT a change you know the truth about
after = ref.copy()
cv2.circle(after, (400, 300), 18, float(ref.max()), -1)   # one new bright feature
```

Save `src` and `after` as a pair, run them through `core.pipeline.run_all()`, and take the
**warped** output. That warped image is what your detector must consume — not the raw crops.
`run_all()` returns a dict; the aligned image is under `"warped"`.

## Step 3 — Run your detector and be honest about it (45 min)

```python
from app.change_detection import detect_changes
overlay, changes = detect_changes(aligned_a, aligned_b, gsd_mpp=9.3699, thresh=30)
```

> **`gsd_mpp` is 9.3699 for this Kaguya scene, not the 0.5 default in your signature.** Your area
> figures in m² are wrong by a factor of ~350 if you leave the default. This is exactly the kind of
> number an ISRO judge asks about.

**Then classify every detection yourself, by eye:**

| bucket | meaning |
|---|---|
| the planted circle | the one true positive — did you find it? |
| edges / borders | registration artifact, not a change |
| shadow boundaries | illumination, not a change |
| anything else | say honestly which it is |

---

## Acceptance criteria

1. `detect_changes` runs on a **pipeline-aligned pair of real lunar imagery** without crashing.
2. **The planted circle is detected**, and its reported area is within ±25% of the true area
   (radius 18 px at 9.3699 m/px → π·(18·9.3699)² ≈ **89,400 m²**).
3. You report the honest split: *"N detections — 1 real, X registration artifacts, Y shadow."*
4. `gsd_mpp` is passed explicitly. Never rely on the 0.5 default again.
5. Pushed, with a short note in `app/README.md` on what you observed.

## Test cases

1. `planted_circle_found` — a detection whose centroid is within 20 px of `(400, 300)`.
2. `area_within_tolerance` — that detection's area is 67,000–112,000 m².
3. `nodata_does_not_dominate` — with the fill masked, total detections < 50. If you get hundreds,
   the mask is wrong, not the detector.

## Starter for the honest count

```python
real, artifact, shadow = 0, 0, 0
for c in changes:
    print(c)          # look at each one and bucket it by hand this time
```

Hand-counting 20 detections once teaches you more about your own thresholds than any automated
metric, and Gate 5 asks you to explain your module cold.

## Dependencies

- **Needs from others: nothing.** `core/io_loader.py`, `core/pipeline.py`, `core/matcher.py`,
  `core/ransac.py` are all committed and working (`ee383de`). The Kaguya file is public.
- **Delivers to:** Samartha (Day 9 UI integration), Saniya (the honest false-positive line in the
  demo script).

## Do not

- Do not wait for Samrudh. Nothing here needs `evaluation/`.
- Do not commit the `.tif`.
- Do not report a change count without saying how many are artifacts. *"X found, Y plausible, Z are
  registration artifacts"* is your Day-7 deliverable and a strong Q&A answer; a bare count is not.
