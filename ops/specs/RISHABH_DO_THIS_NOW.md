# Rishabh — fix these three first, then your next four days

**Written 1 Sep 2026 (Day 3).** Your Day-1 and Day-2 work is good: 256 lines, 7 passing tests,
and you avoided both OpenCV 5 traps without being told. This is what comes next.

Read Part 1 today. It is about 40 minutes and it fixes three real bugs. Parts 2–5 are one day each.

> ✅ **Every code block below has been run before it was sent to you.** I applied Fixes 1 and 3 to a
> scratch copy of your file and re-ran your suite: **all 7 of your tests still pass.** The three new
> tests I ask you to add pass on the patched file too. So if something here does not work on your
> machine, it is an environment difference worth reporting — not you misreading the spec.

---

# PART 1 · Fix these three first (~40 min, today)

These were sent to you on Day 2. They are still in the file. None is your fault as a design
choice — they are ordinary bugs — but all three are the kind a judge finds in ten seconds.

## Fix 1 🔴 — the border cleanup can erase your entire image

**Where:** `app/change_detection.py`, line 166.

```python
mask[-margin:, :] = 0
```

**What goes wrong:** when `margin` is `0`, Python reads `-0` as `0`, so `mask[-0:, :]` means
*"the whole image"*, not *"nothing"*. Your detector silently returns **zero detections** and never
raises an error. It looks like it worked and found nothing.

**I ran this on your code just now:**

```
edge_margin_frac=0.05  ->  1 detection   (correct)
edge_margin_frac=0.0   ->  0 detections  (WRONG - big obvious change in the middle)
18x18 image, default   ->  0 detections  (WRONG - 0.05 x 18 rounds down to 0)
```

**The fix** — wrap the four lines so they only run when there is actually a margin:

```python
if margin > 0:
    mask[:margin, :] = 0
    mask[-margin:, :] = 0
    mask[:, :margin] = 0
    mask[:, -margin:] = 0
```

**Add a test for it**, or it will come back:

```python
def test_zero_margin_does_not_erase_everything():
    a = np.zeros((100, 100), np.uint8)
    b = a.copy()
    b[40:60, 40:60] = 200
    _, changes = detect_changes(a, b, gsd_mpp=1.0, edge_margin_frac=0.0)
    assert len(changes) == 1, "margin=0 wiped the mask"
```

## Fix 2 🔴 — the default pixel size is wrong for every camera we own

**Where:** line 41, `gsd_mpp=0.5`.

We do not have a single camera at 0.5 m/px. Kaguya TC is **9.3699**, Chandrayaan-2 OHRC is
**0.22977**. If someone calls your function and forgets the argument, every area in m² is wrong —
by about **350×** on Kaguya. Nobody would notice, because the number still looks like a number.

**The fix:** make it impossible to forget. Delete the default so Python demands it:

```python
def detect_changes(img_a, img_b, gsd_mpp, thresh=30, ...):
```

Your 7 existing tests already pass `gsd_mpp=0.5` explicitly, so **none of them will break.**

> If a required argument feels awkward, the alternative is `gsd_mpp=None` plus
> `raise ValueError("gsd_mpp is required - get it from the catalogue")`. Either is fine. A silent
> wrong default is not.

## Fix 3 🟡 — `classify()` judges a whole region by one pixel

**Where:** lines 19–20.

```python
a_val = int(img_a[cy, cx])
b_val = int(img_b[cy, cx])
```

`cy, cx` is the centroid. For a **crescent or a ring shape, the centroid can sit outside the region
entirely** — so you are reading a pixel that is not part of the thing you are describing.

**The fix** — use the region's average instead of one pixel:

```python
region = np.zeros(img_a.shape, np.uint8)
cv2.drawContours(region, [cnt], -1, 255, -1)
a_val = float(cv2.mean(img_a, mask=region)[0])
b_val = float(cv2.mean(img_b, mask=region)[0])
```

Your four classification tests use solid blobs, so they should still pass. If one shifts, the new
answer is the more honest one — tell me rather than tuning the number until it goes green.

## Fix 4 🟢 — 2 minutes, cosmetic

`app/README.md` has a backslash before every `#`, `-` and `*` (`\## Purpose`). Your editor escaped
the markdown on save, so GitHub shows the backslashes instead of formatting. Find-and-replace
`\#` to `#`, `\-` to `-`, `\*` to `*`. The content is good; only the rendering is broken.

## Then

```bash
python -m pytest app/ -q
git add app/
git commit -m "change_detection: fix zero-margin mask wipe, require gsd_mpp, classify on region mean"
git push
```

Tell me in chat when this is pushed. **Nothing in Parts 2–5 should start before this is done** —
every later measurement you make would be measured on a detector with a known bug in it.

---

# PART 2 · Day 3 (today, after the fixes) — the free experiment nobody could run until this morning

**~1 hr. No downloads. Everything you need is already in the repo.**

Samrudh pushed `evaluation/shaded_relief.py` at 09:18 today. This changes what is possible for you,
so read this even if you skip everything else.

It takes a terrain model and renders it **lit from any sun position**. So you can produce two
images of *the same ground, with nothing whatsoever changed, only the sun moved.*

**That is the exact test your module has never had.** Ground truth is known and total: **nothing
changed, so every single detection is a false positive.** You do not need a judgement call, and you
do not need real data.

Copy this and run it:

```python
import numpy as np
from evaluation.shaded_relief import render_shaded_relief
from app.change_detection import detect_changes

# some made-up terrain with craters and ridges
x, y = np.mgrid[-160:160, -160:160]
dem = np.sin(np.sqrt(x**2 + y**2) / 14.0) * 60 + np.cos(x / 23.0) * 25

# SAME terrain, sun on opposite sides. Nothing has changed. Only the light.
A = (render_shaded_relief(dem, 45,  25, pixel_size_m=10.0) * 255).astype(np.uint8)
B = (render_shaded_relief(dem, 225, 25, pixel_size_m=10.0) * 255).astype(np.uint8)

for t in (30, 60, 90, 120):
    _, ch = detect_changes(A, B, gsd_mpp=10.0, thresh=t)
    covered = 100 * sum(c["area_px"] for c in ch) / A.size
    print(f"thresh={t:3d}  {len(ch):3d} detections  covering {covered:5.1f}% of the frame")
```

**I already ran it on your current code. Here is what comes back:**

```
thresh= 30    1 detections  covering  62.0% of the frame
thresh= 60    9 detections  covering  41.5% of the frame
thresh= 90    9 detections  covering  31.0% of the frame
thresh=120    9 detections  covering  20.4% of the frame
```

**At your default threshold, the detector flags 62% of the picture as "changed" when absolutely
nothing changed.** That is not you doing bad work — it is what plain image subtraction *does* on the
Moon, where shadows are enormous and the sun angle is never the same twice. It is the reason your
Day-4 task exists.

**Do not be discouraged by this number. It is the most valuable thing your module can say.** A team
that shows this and then shows what they did about it is far stronger than a team that quietly picks
a threshold that happens to look clean.

**What to do with it:**

1. Write the four numbers into `app/README.md` under a new heading *"Why plain differencing is not
   enough"*.
2. Post the same table in the team chat and **send the numbers to Samrudh** so he can put them in
   `evaluation/results_log.csv`. **Do not edit that file yourself** — it is his, and our rule is one
   owner per file.
3. Try a smaller sun move (`45°` vs `75°` instead of `45°` vs `225°`) and note that it gets better
   but does not go away. I measured that one too: 20.5% of the frame at `thresh=30`.

---

# PART 3 · Day 4 — teach it to tell a shadow from a real change

**~2 hrs.** This is the heart of your module and the thing that makes it worth a slide.

You now have a machine (Part 2) that generates unlimited **known-false** detections. Use it as your
scoreboard: try an idea, re-run Part 2, see whether the false-positive percentage drops.

**Three ideas, easiest first. You do not need all three.**

**Idea 1 — shadows point the same way.** The sun is in one place, so every shadow in the image is
cast in the same direction. Real changes are not aligned with each other. Get each region's
orientation from `cv2.fitEllipse(cnt)` (it gives you an angle). If most regions share an angle, they
are shadows.

**Idea 2 — shadows swap, changes appear.** When the sun moves, a spot that was dark becomes bright
*and* a nearby spot that was bright becomes dark. Brightness moves around. A genuinely new object is
bright in one image with nothing correspondingly darker beside it. Check whether each bright region
has a matching dark region close by.

**Idea 3 — ratio instead of subtraction.** Shadows scale brightness up and down; new objects change
it in a way that does not scale. Try `img_a / (img_b + 1)` instead of `absdiff` and see whether the
false-positive percentage falls.

**How you will know it worked:** re-run the Part 2 script. The "% of frame" numbers must go **down**
while a real planted change is still found. Record before-and-after in `app/README.md`.

⚠️ **You are not expected to get this to zero.** Getting 62% down to 15% is a genuinely good result
and an honest one. Do not tune until it reads 0% — that would mean you have switched it off.

---

# PART 4 · Day 5 — areas in real metres, from the real catalogue

**~1.5 hrs.**

Your module already computes `area_m2`. Now make it defensible.

1. Get the pixel size from `data/DATASET_CARD.md` (Rohan's file) rather than typing a number in.
   ⚠️ That card currently has **one row and it is not usable yet** — ask Rohan in chat which pair to
   use and what its m/px is. If he has not answered by evening, use Kaguya's **9.3699** and write in
   your notes that it is hard-coded pending the catalogue.

2. Add a test with a shape whose area you know:

```python
def test_area_matches_known_circle():
    a = np.zeros((400, 400), np.uint8)
    b = a.copy()
    cv2.circle(b, (200, 200), 18, 255, -1)      # radius 18 px
    _, ch = detect_changes(a, b, gsd_mpp=9.3699, thresh=30)
    expected = np.pi * (18 * 9.3699) ** 2       # about 89,400 m2
    assert abs(ch[0]["area_m2"] - expected) / expected < 0.25
```

> I ran this one: your module reports **83,054 m²** against an expected **89,364 m²** — **7.1% low**,
> comfortably inside the tolerance. The small undershoot is expected, because `cv2.contourArea`
> measures the polygon through the pixel centres rather than the pixels themselves. Worth knowing so
> you can explain it rather than chase it.

3. Sanity-check by hand once. A crater 100 px across on OHRC (0.22977 m/px) is about 23 m across. If
   your module says 23 m, you can answer the area question at Gate 5 without notes.

---

# PART 5 · Day 6 — run it on real lunar imagery

**~2 hrs.** Your Day-3 spec (`ops/specs/day03_rishabh_change_detection.md`) has the full
step-by-step for this. It is still valid — just later than planned, which is fine. Two things have
changed since it was written:

- **The pipeline now works end to end** and prints all five metrics, so `run_all()` will not leave
  you stranded.
- **`weights/loftr_outdoor.pt` (46 MB) is on the Drive**, so you may not need to download it. Check
  `SIH26166_DATA/weights/` before running `python core/fetch_weights.py`.

Short version of that spec:

1. Install what the matcher needs — **use the CPU index URL exactly as written**, or pip pulls ~2 GB
   of GPU code we can never use:
   ```
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   pip install kornia certifi
   ```
2. **The Kaguya scene is already downloaded** (1 Sep) — you do not need to fetch it. It is on the
   Drive and at `C:\Users\samar\sih26166_data\raw\TC1S2B0_01_03482S746E0433.tif` on Samartha's
   machine. Copy it to your own data root (the path in your `data_path.txt`), **not** into the repo:
   this clone lives inside OneDrive, and OneDrive uploads files regardless of `.gitignore`.
   Its verified numbers are in [data/DATASET_CARD.md](../../data/DATASET_CARD.md).
3. ⚠️ **Half that file is empty "NoData" with the value −32768.** Mask it first
   (`img = np.where(img == -32768, 0, img)`) or it will read as one giant change.
4. Use the window `x=5120, y=2240` — I checked the scene for you, it is well-lit and full of
   craters. Avoid `x=3200, y=640`, which is 90% shadow.
5. Plant one circle you know the truth about, run the pair through the real pipeline, and detect on
   the **aligned** output.
6. Report the honest split: *"N detections — 1 real, X registration artifacts, Y shadow."*

---

# What this builds to

| Day | What you deliver |
|---|---|
| **3** (today) | 3 bugs fixed · the false-positive number nobody had |
| **4** | A discriminator, with a before/after number proving it helped |
| **5** | Areas in real metres, checked by hand once |
| **6** | It runs on real lunar imagery aligned by the real pipeline |
| **7** | The honest sentence: *"X found, Y plausible, Z are artifacts"* |
| **8** | Freeze. Agree the function signature with Samartha and stop changing it |

**The Gate 5 question you will be asked** is not "what does your code do" — it is **"how do you know
it works?"** After Part 2 you have the best possible answer: *"I measured what it does when I know
for certain that nothing changed, here is the number, and here is what I did to improve it."*

---

## Rules that still apply

- **Only touch `app/`.** Not `evaluation/`, not `data/`. Send numbers to their owner instead.
- **No number goes in a slide until it is in `evaluation/results_log.csv`.** Give yours to Samrudh.
- **Nothing over ~5 MB in git.** No `.tif`, no `.IMG`, no preview PNGs. That has already cost us
  18 MB of permanent history twice.
- **Nothing here needs a GPU**, and nothing here should be made to.
- **If something takes more than 30 minutes longer than it says, say so in chat.** A spec that is
  wrong is my bug, not yours.
