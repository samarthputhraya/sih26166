# Risheeth — fix these two first, then your next four days

**Written 1 Sep 2026 (Day 3).** Your three baselines are the cleanest teammate code in the repo.
All three recover the known shift **exactly** — `(-7, -5)`, zero error. You spotted the OpenCV 5
AKAZE trap on your own and wrote a warning comment about it. And your CSV column list matches
Samrudh's header **character for character**, which means you read his guide properly instead of
guessing. That is genuinely good work.

There are two bugs, and they are both in the part you have never been able to run.

> ✅ **Every command and number below was run before it was sent to you.** If something here does
> not work on your machine, that is an environment difference worth reporting — not you misreading
> the spec.

---

# PART 1 · Fix these two first (~45 min, today)

Both bugs are in the "real data" path. Neither shows up in `--test` mode, which is why your Day-1
work looked complete — it *was* complete for what it covered.

## Fix 1 🔴 — your code looks for pairs in the wrong place, so it finds none

**Where:** `baselines/run_all_baselines.py` line 75 and line 223, and the same two lines again in
`baselines/draw_failure_gallery.py` (lines 37 and 223).

Your code looks for:
```
data/pairs/pair_01_source.tif
```

The file is actually at:
```
data/pairs/pair_01/pair_01_source.tif
```

Every pair lives in **its own folder**. So `run_all_baselines.py` finds zero pairs, prints
*"No pairs found in data/pairs/"*, and exits successfully. Nothing errors. It just quietly does
nothing — which is why you would never have caught it.

**The fix**, in both files. The lookup:

```python
def _load_pair(pair_id: str):
    pairs_dir = REPO_ROOT / "data" / "pairs" / pair_id      # <-- add / pair_id
    src_path = pairs_dir / f"{pair_id}_source.tif"
    ref_path = pairs_dir / f"{pair_id}_ref.tif"
```

And the discovery:

```python
for f in (REPO_ROOT / "data" / "pairs").glob("*/*_source.tif"):   # <-- */ added
    pair_ids.append(f.stem.replace("_source", ""))
```

> 🔴 **One more thing, or the fix will bite you.** With that glob corrected, discovery finds **two**
> pairs: `pair_01` and `pair_00_dryrun`. **`pair_00_dryrun` is a known-fake fixture** — it was a
> synthetic dry-run file that got mistaken for real Chandrayaan-2 data last week, and it reports
> flatteringly good numbers precisely because it is not real imagery. It is kept only so we can
> point at it.
>
> **Skip it.** Add one line:
> ```python
> pair_ids = [p for p in pair_ids if not p.startswith("pair_00")]
> ```
> If a number from `pair_00_dryrun` ever reaches a slide, we will have shipped the same mistake
> twice.

## Fix 2 🔴 — Config 2 crashes, so half your comparison has never run

**Where:** `run_all_baselines.py`, `_run_config()`, the `config == 2` branch.

```python
src_norm = illum_normalize(src_img)
src_pts, ref_pts = run_fn(src_norm, ref_norm)
```

`illumination.normalize()` returns **float32**. SIFT, ORB and AKAZE all require **uint8**. I ran it:

```
cv2.error: (-5:Bad argument) image is empty or has incorrect depth
```

Config 2 is the *illumination-normalised* half of your comparison — the entire point of the
baseline exercise, and what Gate 2-alt is judged on. It has never executed once.

**The fix** — convert back to uint8 after normalising:

```python
src_norm = np.clip(illum_normalize(src_img), 0, 255).astype(np.uint8)
ref_norm = np.clip(illum_normalize(ref_img), 0, 255).astype(np.uint8)
```

> ⚠️ **`normalize()` returns 0–255, not 0–1.** Do not "tidy" this by dividing by 255. There is a
> test in `core/` whose whole job is to stop that change, because it silently produces zero matches.

## Fix 3 🟡 — your failure gallery will commit images into the repo

`draw_failure_gallery.py` writes PNGs to `baselines/failure_gallery/`. I checked: that path is
**not** in `.gitignore`, so `git add -A` would commit every one of them permanently.

We have already put ~18 MB of images into git history twice and cannot get them out. Please do not
make it three.

**The fix** — add one line to `.gitignore` yourself (that file is shared, not owned):

```
baselines/failure_gallery/*
!baselines/failure_gallery/.gitkeep
```

## Fix 4 🟢 — you have zero automated tests (~20 min, and it is nearly free)

`pytest baselines/` collects **nothing**. Your checks live in `if __name__ == "__main__":` blocks,
so they only run when someone remembers to run them by hand. Nobody will.

You do not need to write anything new — just move what you already have. Create
`baselines/test_baselines.py`:

```python
import numpy as np
import pytest
from baselines.make_test_pair import make_pair
from baselines.sift_baseline import run_sift
from baselines.orb_baseline import run_orb
from baselines.akaze_baseline import run_akaze

@pytest.mark.parametrize("name,fn", [("sift", run_sift), ("orb", run_orb), ("akaze", run_akaze)])
def test_recovers_known_shift(name, fn):
    src, ref = make_pair(dx=7, dy=5, seed=0)
    src_pts, ref_pts = fn(src, ref)
    assert len(src_pts) > 20, f"{name} found almost nothing on an easy pair"
    offset = np.median(ref_pts - src_pts, axis=0)
    assert np.allclose(offset, [-7.0, -5.0], atol=0.5)

@pytest.mark.parametrize("fn", [run_sift, run_orb, run_akaze])
def test_blank_images_return_empty_not_crash(fn):
    blank = np.zeros((100, 100), np.uint8)
    src_pts, ref_pts = fn(blank, blank)
    assert len(src_pts) == 0
```

That is 6 real tests for 20 minutes, and it makes your module the only baseline suite that cannot
quietly rot.

## Then

```bash
python -m pytest baselines/ -q
python -m baselines.run_all_baselines --test
git add baselines/ .gitignore
git commit -m "baselines: fix pair path layout, fix config-2 dtype crash, add test suite"
git push
```

Tell me in chat when this is pushed.

---

# PART 2 · Day 3 (today, after the fixes) — the experiment that became possible this morning

**~1 hr. No downloads. Nothing to wait for.**

Your Day-3 row says *"Run all 3 baselines on Samrudh's synthetic pairs."* Until 09:18 today that
was impossible, because his files were empty. **They are real now**, and they do something no
fixture we have has ever done: render the **same terrain lit from two different sun positions**,
with exact ground truth.

That means real shadows that genuinely **move** — which is the thing your baselines are supposed to
struggle with, and the thing we have never actually measured.

```python
import numpy as np
from evaluation.synthetic_data import make_pair
from baselines.sift_baseline import run_sift
from baselines.orb_baseline import run_orb
from baselines.akaze_baseline import run_akaze
from core.illumination import normalize

def crater_dem(n=420, seed=3, ncr=90):
    """Non-repetitive crater terrain. A smooth or repeating surface will NOT work - see below."""
    rng = np.random.default_rng(seed)
    dem = rng.normal(0, 3, (n, n))
    yy, xx = np.mgrid[0:n, 0:n]
    for _ in range(ncr):
        cx, cy = rng.integers(20, n-20, 2)
        rad = rng.integers(8, 34)
        depth = rad * rng.uniform(0.4, 1.0)
        d = np.sqrt((xx-cx)**2 + (yy-cy)**2)
        dem += np.where(d < rad, -depth*(1-(d/rad)**2), 0.0)
        dem += np.where((d >= rad) & (d < rad*1.25), depth*0.28*(1-(d-rad)/(rad*0.25)), 0.0)
    return dem

dem = crater_dem()

def u8(i):
    i = np.asarray(i, np.float32)
    if i.max() <= 1.0:
        i = i * 255.0
    return np.clip(i, 0, 255).astype(np.uint8)

for d, label in ((0, "0 deg"), (30, "30 deg"), (90, "90 deg"), (180, "180 deg")):
    s, r, H_true, meta = make_pair(dem, pixel_size_m=10.0, sun_a=(45, 25), sun_b=(45+d, 25),
                                   rotation_deg=0.0, scale=1.0, shift_px=(10.0, -6.0))
    s8, r8 = u8(s), u8(r)
    sn, rn = u8(normalize(s8)), u8(normalize(r8))
    for name, fn in (("SIFT", run_sift), ("ORB", run_orb), ("AKAZE", run_akaze)):
        raw, _ = fn(s8, r8)
        nrm, _ = fn(sn, rn)
        print(f"{label:>8} {name:6} raw={len(raw):5d}  illum_norm={len(nrm):5d}")
```

> 🔴 **You MUST pass `scale=1.0` and `rotation_deg=0.0` explicitly.** If you leave them out,
> Samrudh's generator picks a random scale **between 1× and 20×**. I checked four seeds: it gave
> 6.1×, 19.1×, 6.7× and 5.5×. At 19× your baselines fail because of the zoom, not the sun — and
> your failure gallery would be showing the wrong failure. Change one thing at a time.

> 🔴 **And always run the 0° point as a control.** At 0° the two images are identical apart from the
> shift, so every method should find *hundreds* of matches. My first attempt used a smooth ripple
> surface and SIFT found **5 matches at 0°** — repetitive terrain defeats the ratio test, so I was
> measuring the pattern, not the sun. **If your 0° row is not in the hundreds, the terrain is wrong
> and nothing below it means anything.** That is why `crater_dem` above is built from random craters
> rather than a wave.

**Here is what I got, so you know whether yours is working:**

```
   0 deg SIFT    raw=  488  illum_norm=  988      <- control: both find plenty
   0 deg ORB     raw= 2399  illum_norm= 1677
   0 deg AKAZE   raw=  213  illum_norm=    5

  30 deg SIFT    raw=   10  illum_norm=    0
  30 deg ORB     raw=  142  illum_norm=    2
  30 deg AKAZE   raw=   20  illum_norm=    2

  90 deg SIFT    raw=    0  illum_norm=    0
  90 deg ORB     raw=   31  illum_norm=    0
  90 deg AKAZE   raw=    3  illum_norm=    0

 180 deg SIFT    raw=    2  illum_norm=  203
 180 deg ORB     raw=   48  illum_norm=  218
 180 deg AKAZE   raw=    7  illum_norm=    0
```

**This is your headline result, and it has two halves — report both.**

**Half one: classical matching collapses when the sun moves.** SIFT goes from **488 matches to 10**
with only 30° of sun movement, and to **zero** by 90°. That is the measured evidence for why this
project uses a learned matcher. Everything the team claims on that point rests on this table.

**Half two, and do not hide it: illumination normalisation often makes things WORSE here.** AKAZE
goes 213 → 5 at 0°. ORB goes 142 → 2 at 30°. It only helps dramatically at 180° (SIFT 2 → 203). So
the honest sentence is *"normalisation helps when the lighting is reversed, and hurts when the
lighting is already similar"* — not *"normalisation helps"*.

That second half is more valuable than the first. Any team can show a method failing. Showing that
your own preprocessing has a cost, and knowing when it applies, is what a judge remembers.

**What to do with it:**

1. Write the table into a new `baselines/README.md`, with a plain sentence saying what the terrain
   was and that it is synthetic.
2. Post it in the team chat and **send the numbers to Samrudh** for `evaluation/results_log.csv`.
   Your script can write there, but tell him first so you are not both appending blind.
3. ⚠️ **Say clearly that the terrain is a made-up mathematical surface, not real lunar terrain.**
   The shape of the result is right; the exact numbers will change on a real DEM. Rohan is meant to
   bring an SLDEM tile — re-run this on it when he does. Never let this table be quoted without the
   word "synthetic" attached.

---

# PART 3 · Day 4 — the real-pair comparison, and your first rows in the log

**~1.5 hrs.**

**First, get the data.** `data/pairs/` is gitignored, so you do **not** have `pair_01` — ask
Samartha for the `SIH26166_DATA` Drive folder and copy `pairs/pair_01/` into your `data/pairs/`.

Then, with Fixes 1 and 2 in:

```bash
python -m baselines.run_all_baselines --pairs pair_01
```

**Here is what it should produce** (I ran the patched version):

```
method  config          matches   recovered shift   (truth: -40, -25)
SIFT    1 raw               442   (-40.00, -25.00)
SIFT    2 illum_norm       4780   (-40.00, -25.00)
ORB     1 raw               739   (-39.81, -24.88)
ORB     2 illum_norm       2625   (-40.00, -25.00)
AKAZE   1 raw               263   (-40.00, -25.00)
AKAZE   2 illum_norm       3073   (-40.00, -25.00)
```

Illumination normalisation gives SIFT **10.8× more matches** and AKAZE **11.7×**. All six recover
the known offset exactly.

> 🔴 **Do not write "illumination normalisation helps across sun angles" from this table.**
> `pair_01` is two crops of *the same frame* — identical pixels, one shifted. There is no
> illumination difference in it at all. What this table shows is that the normalisation step
> **increases match count on identical imagery** (it sharpens texture). The sun-angle claim comes
> from Part 2, not from here.
>
> This exact confusion has already put a wrong number into four of our documents once. When you
> report it, name the pair type: *"same-frame offset crop"*.

**Your Day-4 row says "run baselines on Rohan's Tier A pairs."** Those do not exist yet — the
dataset card has one row and it points at an image that turned out to be blank. Do not wait for it.
Do `pair_01` plus Part 2, and say in chat that Tier A is still outstanding so it is visible.

---

# PART 4 · Day 5 — failure gallery v1, three worst cases

**~2 hrs.** This is your most visible deliverable — it is the picture the judges remember.

You now have genuine failures to draw, which you did not have last week. **The best three:**

1. **SIFT at 90° sun difference — 0 matches, against 488 at 0°.** A total collapse, with the 0°
   panel beside it as the control. This is the single clearest picture in the project.
2. **AKAZE at 0° — 213 raw, but only 5 after normalisation.** The preprocessing is not free. Show
   the case where our own step *hurts*; it is the most credible panel in the gallery.
3. **SIFT at 180° — 2 raw → 203 normalised.** The success case, for contrast, and the reason we keep
   the step despite panel 2.

For each: source and reference side by side, matches drawn between them, and a one-line caption in
plain English — *"SIFT finds one match when the sun moves 90°."*

Keep captions non-technical. Somebody who has never heard of SIFT should understand the picture in
five seconds. That is the whole job of a failure gallery.

⚠️ Check Fix 3 is in before you run this, or you will commit the PNGs.

---

# PART 5 · Day 6 — finish the gallery, and one honest paragraph

**~1.5 hrs.**

1. Finish the annotations on all three panels.
2. Re-run Part 2 on a **real** DEM if Rohan has delivered an SLDEM tile, and update the table.
   If he has not, keep the synthetic numbers and keep the word "synthetic" on them.
3. Write one paragraph at the top of `baselines/README.md` that answers the Gate 5 question:

> *"Classical methods work well when two images differ only by a shift — they recover a 40-pixel
> offset exactly, with hundreds of matches. They break down when the sun moves: SIFT drops from 488
> matches to 10 with 30° of sun change, and to zero by 90°. Illumination normalisation helps only
> when the lighting is strongly reversed — at 180° it took SIFT from 2 matches back up to 203 — and
> it actively hurts when the lighting is already similar, cutting AKAZE from 213 to 5. That is why
> the project uses a learned matcher, and why we apply the normalisation selectively rather than
> always."*

Write it in your own words. If you can say that paragraph out loud without notes, you have passed
your part of Gate 5.

---

# What this builds to

| Day | What you deliver |
|---|---|
| **3** (today) | 2 bugs fixed · 6 real tests · the sun-angle collapse table |
| **4** | The real-pair comparison, config 1 vs 2, first rows in the log |
| **5** | Failure gallery v1 — three cases, captioned in plain English |
| **6** | Gallery final, and the paragraph that explains why the project exists |
| **7** | Run on Tier B pairs (needs Rohan's catalogue) |
| **8** | Comparison table v1 — every method, every tier, one table. **Gate 2.** |

---

## Rules that still apply

- **Only touch `baselines/`** (plus the one `.gitignore` line). Send numbers to their owner.
- **Never quote a number without saying which pair type it came from.** "Same-frame offset crop" and
  "synthetic sun-angle pair" are different worlds, and mixing them up is the single most likely way
  we lose marks in Q&A.
- **No images in git.** Gallery PNGs go to Drive.
- **Nothing here needs a GPU.**
- **If a task takes 30 minutes longer than it says, say so in chat.** A spec that is wrong is my
  bug, not yours.
