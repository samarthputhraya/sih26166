# [Day 1] Risheeth — `baselines/{sift,orb,akaze}_baseline.py`

**Time: 2 hrs.** Read `day01_00_SHARED_SETUP.md` first.

> **`cv2.AKAZE_create()` DOES NOT EXIST in our pinned OpenCV.** Verified on the demo machine:
> `opencv-contrib-python 5.0.0.93` raises `AttributeError: module 'cv2' has no attribute
> 'AKAZE_create'`. In OpenCV 5, AKAZE/KAZE/BRISK moved into `cv2.xfeatures2d`. The correct call is
> **`cv2.xfeatures2d.AKAZE_create()`** — verified working. `RISHEETH_BASELINE_GUIDE.md` has the old
> call. **Use this spec, not the guide.**

## Goal, in one sentence
All three classical detectors recover a known shift on a pair you generated yourself, with the sign
convention written down.

## Signature
```python
def run_sift(img1: np.ndarray, img2: np.ndarray, nfeatures: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """img1=source, img2=reference, both uint8 grayscale. Returns (src_pts, ref_pts), each (N,2) float32."""
```
`run_orb` and `run_akaze` take and return exactly the same types.

## Install
```bash
pip install opencv-contrib-python==5.0.0.93 numpy==2.5.2 pandas==3.0.5 matplotlib==3.11.1
```
Must be `opencv-contrib-python`, **not** `opencv-python` — the latter has no `xfeatures2d` and no SIFT.

## Acceptance criteria
1. **Input:** two `numpy.uint8` arrays, HxW grayscale, 0–255, identical shape.
2. **Output:** a 2-tuple `(src_pts, ref_pts)`, both `numpy.float32` shape `(N, 2)` in `(x, y)` order,
   same length, same ordering. On failure (`des is None`, or fewer than 2 keypoints) return
   `(np.zeros((0,2), np.float32), np.zeros((0,2), np.float32))` — an empty result, **never** an
   exception.
3. All three test cases print the correct median offset.

## Test cases
Using the generator below (`default_rng(0)`, byte-reproducible), with a shift of `dx=7, dy=5`:

1. `sift_recovers_shift` — `np.median(ref_pts - src_pts, axis=0)` == `(-7.00, -5.00)`
2. `orb_recovers_shift` — same
3. `akaze_recovers_shift` — same

> **Sign convention — read before you conclude you are broken.** `warpAffine` with `[[1,0,7],[0,1,5]]`
> moves content **right and down**, so a feature at `(x, y)` in the reference sits at `(x+7, y+5)` in
> the source. Therefore `median(ref - src) = (-7, -5)` and `median(src - ref) = (+7, +5)`. Your guide
> says "average offset ≈ (7, 5)" — that is `src - ref`. **Both are correct; state which one you
> printed.** Getting `(-7, -5)` is success, not a bug.

## Starter
```python
# baselines/make_test_pair.py
import cv2, numpy as np

def make_pair(dx=7, dy=5, seed=0):
    """Deterministic textured base. Depends on no file and no teammate."""
    rng = np.random.default_rng(seed)
    img = np.full((480, 640), 40, np.uint8)
    for _ in range(300):
        cx, cy = int(rng.integers(30, 610)), int(rng.integers(30, 450))
        cv2.circle(img, (cx, cy), int(rng.integers(4, 18)),
                   int(rng.integers(90, 255)), -1)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    shifted = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
    return shifted, img          # (source, reference); truth: src - ref = (dx, dy)
```

```python
# baselines/sift_baseline.py
import cv2, numpy as np

EMPTY = (np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32))

def _to_points(kp1, kp2, good):
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 2)
    ref = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 2)
    return src, ref

def run_sift(img1, img2, nfeatures=0):
    sift = cv2.SIFT_create(nfeatures=nfeatures)
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)
    if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
        return EMPTY
    # SIFT descriptors are float32 -> a FLANN KD-tree is correct HERE ONLY.
    flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    knn = flann.knnMatch(des1, des2, k=2)
    good = [p[0] for p in knn if len(p) == 2 and p[0].distance < 0.7 * p[1].distance]
    return _to_points(kp1, kp2, good) if good else EMPTY
```

```python
# baselines/orb_baseline.py   (akaze_baseline.py is identical but for the detector)
import cv2, numpy as np
from baselines.sift_baseline import EMPTY, _to_points

def _run_binary(det, img1, img2, ratio=0.75):
    kp1, des1 = det.detectAndCompute(img1, None)
    kp2, des2 = det.detectAndCompute(img2, None)
    if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2:
        return EMPTY
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)      # binary descriptors -> Hamming
    knn = bf.knnMatch(des1, des2, k=2)
    good = [p[0] for p in knn if len(p) == 2 and p[0].distance < ratio * p[1].distance]
    return _to_points(kp1, kp2, good) if good else EMPTY

def run_orb(img1, img2, nfeatures=5000):
    return _run_binary(cv2.ORB_create(nfeatures=nfeatures), img1, img2)

def run_akaze(img1, img2):
    # OpenCV 5: AKAZE lives in xfeatures2d, NOT at cv2 top level.
    return _run_binary(cv2.xfeatures2d.AKAZE_create(), img1, img2)
```

## Dependencies
- Needs **nothing from any teammate**. `baselines/` exists in commit `7644b4c`.
- Verified present on the demo machine: `cv2.SIFT_create`, `cv2.ORB_create`,
  `cv2.xfeatures2d.AKAZE_create`, `cv2.BFMatcher`, `cv2.NORM_HAMMING`, `cv2.USAC_MAGSAC` (= 38).
  AKAZE descriptors are `uint8 (N, 61)`; SIFT's are `float32` — which is exactly why they need
  different matchers.
- Delivers to: yourself Days 2–3; Samrudh Day 3 (your `(N,2) float32` output is what `evaluate()` takes).

## Do not
- **Do not call `cv2.AKAZE_create()`.** It raises `AttributeError`. Use `cv2.xfeatures2d.AKAZE_create()`.
  **And when a generic assistant tells you to fix it by downgrading to `opencv-python==4.x`, refuse** —
  that breaks version parity with the team and loses SIFT.
- **Do not use FLANN for ORB or AKAZE.** Their descriptors are binary `uint8`. A KD-tree index on
  them gives silent garbage or an assertion. Use `cv2.BFMatcher(cv2.NORM_HAMMING)`.
- **Do not `cv2.imread("some_image.jpg")`.** If the file is absent, `imread` returns `None` with no
  error and you get a confusing crash three lines later. Use the generator above.
- **Do not write `for m, n in knn`.** `knnMatch` returns a 1-element list for some descriptors,
  raising `ValueError: not enough values to unpack`. Guard with `len(p) == 2`. This happens
  constantly on low-texture lunar imagery.
- **Do not compute RMSE, inlier ratio or coverage today.** `evaluation/metrics.py` does not exist
  yet. Day 1 is offset recovery only.

## You are BLOCKED if
`cv2.xfeatures2d` is missing after install → you almost certainly have plain `opencv-python`
installed alongside. `pip uninstall opencv-python opencv-contrib-python -y`, then reinstall only
`opencv-contrib-python==5.0.0.93`. Still broken after 20 minutes → **ping Samartha.**

## The ONE thing most likely to make your Day 1 fail
**The `cv2.AKAZE_create()` AttributeError.** It looks like a broken install rather than a moved API,
and every generic assistant will tell you to downgrade OpenCV — costing you the session *and*
desynchronising you from everyone's pinned versions. The fix is one namespace: `cv2.xfeatures2d.`
