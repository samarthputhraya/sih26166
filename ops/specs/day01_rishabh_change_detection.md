# [Day 1] Rishabh — `app/change_detection.py`

**Time: 2 hrs.** Read `day01_00_SHARED_SETUP.md` first.

## Goal, in one sentence
`detect_changes` finds exactly one injected bright circle on a pair you made yourself, reports its
area in m², and returns zero regions when the two images are identical.

## Signature
```python
def detect_changes(img_a: np.ndarray, img_b: np.ndarray, gsd_mpp: float = 0.5,
                   thresh: int = 30, min_area_px: int = 50,
                   edge_margin_frac: float = 0.05) -> tuple[np.ndarray, list[dict]]:
    """img_a=before, img_b=after, aligned, same size. Returns (overlay_bgr_uint8, changes)."""

def classify(cnt, img_a: np.ndarray, img_b: np.ndarray,
             cx: int, cy: int) -> tuple[str, tuple[int, int, int]]:
    """One of four labels plus its BGR colour. Blunt heuristics, honestly described."""
```

## Install
```bash
pip install opencv-contrib-python==5.0.0.93 numpy==2.5.2 pandas==3.0.5 pillow==12.3.0
```

## Acceptance criteria
1. **Input:** `img_a`, `img_b` — numpy grayscale, same shape. **uint8, uint16 and float32 must all
   work**; convert internally before any OpenCV call that demands uint8.
2. **Output:** exactly a 2-tuple.
   - `overlay` — numpy **uint8**, shape `(H, W, 3)`, BGR, one labelled rectangle per region.
   - `changes` — a `list[dict]`, each with **exactly these five keys**: `"bbox"` `[x, y, w, h]`,
     `"centroid_px"` `[cx, cy]`, `"area_px"` (float), `"area_m2"` (float), `"classification"`
     (one of `"shadow?"`, `"new bright"`, `"disappeared"`, `"uncertain"`).
3. All three test cases pass.

## Test cases
Using the generator below (`default_rng(1)`, reproducible):

1. `finds_injected_circle` — base plus a filled circle of radius 25 at (200, 150) →
   `len(changes) == 1`, `classification == "new bright"`, and
   `area_m2 == area_px * gsd_mpp**2`.
2. `identical_images_find_nothing` — `detect_changes(before, before.copy())` → **`len(changes) == 0`**.
   This is the test that catches a broken threshold.
3. `uint16_does_not_crash` — pass both images as `uint16` (`* 257`) → `len(changes) == 1` and
   `overlay.dtype == np.uint8`.

## Starter
```python
# app/change_detection.py
import cv2, numpy as np

def classify(cnt, img_a, img_b, cx, cy):
    x, y, w, h = cv2.boundingRect(cnt)
    elong = max(w, h) / max(min(w, h), 1)
    a_val = int(img_a[cy, cx]); b_val = int(img_b[cy, cx])   # note [row, col] = [cy, cx]
    if elong > 4:           return "shadow?",     (0, 200, 200)   # yellow
    if b_val > a_val + 40:  return "new bright",  (0, 255, 0)     # green
    if a_val > b_val + 40:  return "disappeared", (255, 80, 0)    # blue
    return "uncertain", (160, 160, 160)                            # grey


def detect_changes(img_a, img_b, gsd_mpp=0.5, thresh=30,
                   min_area_px=50, edge_margin_frac=0.05):
    # 1. dtype guard FIRST -- lunar products arrive uint16/float far more often than uint8
    # 2. cv2.absdiff -> cv2.medianBlur(.., 5) -> cv2.threshold(.., thresh, 255, BINARY)
    # 3. MORPH_OPEN then MORPH_CLOSE with a 5x5 ellipse
    # 4. zero out an edge_margin_frac border on all four sides
    # 5. findContours(RETR_EXTERNAL, CHAIN_APPROX_SIMPLE) -- returns 2 values in OpenCV 5
    # 6. skip contours with contourArea < min_area_px
    # 7. centroid from cv2.moments, guarding m00 == 0
    # 8. classify(), append the 5-key dict, draw rectangle + putText
    ...


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    before = np.full((480, 640), 60, np.uint8)
    for _ in range(200):
        cx, cy = int(rng.integers(20, 620)), int(rng.integers(20, 460))
        cv2.circle(before, (cx, cy), int(rng.integers(3, 14)),
                   int(rng.integers(45, 110)), -1)
    before = cv2.GaussianBlur(before, (5, 5), 0)
    after = before.copy()
    cv2.circle(after, (200, 150), 25, 255, -1)     # the "new" bright object
    overlay, changes = detect_changes(before, after, gsd_mpp=0.5)
    print(len(changes), changes)
    cv2.imwrite("app/my_overlay.png", overlay)
```

## Dependencies
- Needs **nothing from any teammate**. `app/` exists in commit `7644b4c`.
- Verified present: `cv2.medianBlur`, `cv2.absdiff`, `cv2.findContours` (returns **2** values in
  OpenCV 5, not 3), `cv2.moments`, `cv2.fitEllipse`.
- Delivers to: Samartha Day 9 — `streamlit_app.py` imports `detect_changes` directly.

## Do not
- **Do not run `cv2.medianBlur` on a float array.** It requires uint8 and raises immediately.
  Convert *before* the blur, not after.
- **Do not `cv2.cvtColor(float_img, cv2.COLOR_GRAY2BGR)`.** It returns an all-black overlay with no
  error, and you will blame the detector.
- **Do not build a Flask or FastAPI endpoint.** A generic assistant will suggest this for "an app".
  Streamlit imports your function directly — a server is one more process to launch, one more port
  to conflict, one more thing to crash at Gate 4. There is no `api.py` in this project.
- **Do not `cv2.imread("some_image.jpg")`** — returns `None` silently if absent. Use the generator.
- **Do not hardcode `gsd_mpp`.** `data/pairs_catalogue.csv` does not exist yet, so pass it
  explicitly today. From Day 5 it comes from that file. LROC NAC is ~0.5 m, OHRC ~0.28 m, Kaguya
  ~10 m — a hardcoded 0.5 makes a Kaguya area wrong by a factor of hundreds, on screen, in front of
  a judge.
- **For Day 2, not today:** `cv2.normalize(..., NORM_MINMAX)` applied to each image *separately*
  rescales them differently and can manufacture a global difference on real uint16 pairs. Safe today
  because both test inputs are uint8. Flag it when you move to real data.

## You are BLOCKED if
Nothing can block you — this task depends on no file, no teammate and no network. Stuck >30 min on
an OpenCV error → post the full traceback in chat and tag Samartha.

**Also today, 5 minutes:** ask **Rohan** in chat for the **Chandrayaan-3 landing-site LROC NAC pair**
(pre- and post-August-2023). He needs the lead time; you need it around Day 6. Asking is the
deliverable — you are not blocked on the answer.

## The ONE thing most likely to make your Day 1 fail
**You use a personal photo as the base, draw the white circle over an already-bright region,
`absdiff` comes out under the threshold of 30, nothing is detected — and you start tuning thresholds
instead of fixing the test image.** The generator above has a base around 60 and a circle at 255.
Never tune a threshold against an input you have not verified.
