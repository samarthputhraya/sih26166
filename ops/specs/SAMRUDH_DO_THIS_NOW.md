# Samrudh — fix these first, then your next four days

**Written 1 Sep 2026 (Day 3).** The recovery worked. All six files have real content, and the work
is better than the empty-commit episode suggested. Two things stand out:

- **`rmse_gt_px` returns `None`, never `0.0`, when there is no ground truth.** Nobody told you to do
  that. It is the single most important guard in the whole evaluation module — a `0.0` there would
  read as "perfect accuracy" and would have gone straight into a slide.
- **`test_holdout_actually_holds_out`** is a real test. Feeding 80 clean and 20 garbage points and
  asserting the residual is large actually proves the split is not leaking. Most people write a test
  that would pass either way.

Your `README.md` explanation of `rmse_gt_px` vs `residual_px` is the clearest writing in the repo.

There are four things to fix, one of which is serious and is **half mine**.

> ✅ **Every number and command below was run before it was sent to you.**

---

---

# 🔴 READ THIS BEFORE ANYTHING ELSE — you and Risheeth have both written `metrics.py`

Risheeth has an unmerged branch, `risheeth-baseline-pipeline`, which **rewrites
`evaluation/metrics.py` (156 lines changed) and `evaluation/test_metrics.py` (157 lines)**. Those
are your files. He wrote his version while yours was still empty, so this is not him overstepping —
it is the empty-files episode still causing damage a day later.

**If he merges that branch as-is, it will collide head-on with the version you pushed this morning,
and one of you will lose a day's work.**

His version is good, and on one point it is **ahead of yours**: he already returns a dict instead of
`None` when there are too few matches — which is exactly Fix 3 below. So the resolution is not
"whose is better", it is:

1. **You keep ownership of `evaluation/`.** Your version on `main` is the one that survives.
2. **Take his dict-return idea** — it is Fix 3, and you were getting that instruction anyway.
3. **Ask him to drop `evaluation/*` from his branch** before merging, keeping only `baselines/*`
   and the `.gitignore` line.

**Message him about this today, before he merges.** Samartha has been told too. This is a
five-minute conversation now and a two-hour merge conflict tomorrow.

---

# PART 1 · Fix these first (~1 hr, today)

## Fix 1 🔴 — the most important bug in the project right now, and it is half mine

**Your `evaluate()` is correct. It is being fed the wrong thing.**

`core/pipeline.py` runs RANSAC, throws away the bad matches, and then hands you **only the
survivors**. So when you compute `inlier_ratio`, you are answering *"of the points RANSAC already
accepted, how many does a second RANSAC accept?"* — and the answer is always about 1.0.

**I built a pair where exactly half the matches are deliberate garbage. Truth: 0.50.**

```
evaluate(RAW matches)       inlier_ratio = 0.500   <- honest
evaluate(FILTERED inliers)  inlier_ratio = 1.000   <- what the pipeline reports today
```

**Gate 2 requires `inlier_ratio > 0.60`. Today we would pass that automatically, on a pair where
half the matches are wrong.** That is exactly the flattering-number failure that has already bitten
this project twice.

**Two halves to the fix:**

- **Mine:** `pipeline.py` must pass the raw matches, not `src_in, ref_in`. I am fixing that.
- **Yours:** the contract belongs to you, because you own the definition. Please:
  1. Put one line at the top of the `evaluate()` docstring in capitals:
     `matches_src/matches_ref MUST be the RAW matcher output, BEFORE any RANSAC filtering.`
  2. Say the same thing in `evaluation/README.md` under the `inlier_ratio` description.
  3. Add a test that pins it:

```python
def test_inlier_ratio_reflects_garbage_in_the_input():
    # half the matches are wrong -> ratio must be near 0.5, NOT near 1.0
    rng = np.random.default_rng(7)
    good = (rng.random((100, 2)) * 900 + 50).astype(np.float32)
    good_r = (good + np.array([12.0, -8.0])).astype(np.float32)
    bad = (rng.random((100, 2)) * 1000).astype(np.float32)
    bad_r = (rng.random((100, 2)) * 1000).astype(np.float32)
    src = np.vstack([good, bad]).astype(np.float32)
    ref = np.vstack([good_r, bad_r]).astype(np.float32)
    res = evaluate((1024, 1024), src, ref, seed=1)
    assert 0.4 < res["inlier_ratio"] < 0.6, "inlier_ratio is not seeing the bad matches"
```

I ran that test against your current code: **it passes.** Your module is already right. The test is
there so that nobody "helpfully" pre-filters the input again later.

## Fix 2 🟡 — one of your five tests asserts the wrong thing

`test_known_offset` fails. **Your code is right and your test is wrong**, so do not change
`metrics.py` to make it pass.

The test shifts every point by `(2, 3)` and then asserts `residual_px == 3.6055`, which is the
*size of the shift*. But `residual_px` is the error **left over after fitting** — and a pure
translation is fit perfectly, so the correct answer is **0.0**, which is what your code returns.

```python
def test_known_offset():
    src = np.random.rand(100, 2) * 1000
    ref = src + np.array([2.0, 3.0])
    res = evaluate((1024, 1024), src.astype(np.float32), ref.astype(np.float32))
    assert res["residual_px"] < 1e-3, "a pure translation should be fit exactly"
```

Worth holding on to, because it is the distinction your own README explains well: **the offset is
what the transform removes; the residual is what it could not.**

## Fix 3 🟡 — `None` means two different things, and it loses data

`evaluate()` returns `None` both when there are fewer than 4 matches **and** when RANSAC fails.
The caller cannot tell which, and cannot log either.

This bites you on Day 4. When I ran your swept-azimuth curve, **five of the seven points came back
as bare `None`** — so the most interesting part of the curve (where classical collapses) would be
missing from the CSV entirely. A curve that silently drops its failures tells the opposite story
from the truth.

**The fix** — return a dict that says what happened, so every point can be logged:

```python
def _failed(reason, n):
    return {"rmse_gt_px": None, "residual_px": None, "inlier_count": 0,
            "inlier_ratio": 0.0, "grid_coverage_fraction": 0.0,
            "distribution_cv": None, "n_matches": n, "status": reason}

if n < 4:
    return _failed("too_few_matches", n)
...
if H is None:
    return _failed("ransac_failed", n)
```

Add `"status": "ok"` to the success return too, and a `status` column to the CSV. Then a failure is
a **row that says it failed**, instead of a hole.

## Fix 4 🟡 — your pair generator makes impossible pairs by default

In `synthetic_data.make_pair`, if `scale` is not passed you sample `rng.uniform(1.0, 20.0)`.
I checked four seeds:

```
seed=0: scale=6.1x    seed=1: scale=19.1x    seed=2: scale=6.7x    seed=3: scale=5.5x
```

At 19× a 400×400 reference leaves about 5% of the scene visible in the source — nothing can register
that, and anyone using your generator will think their method failed when really the pair was
impossible.

**The fix:** default to `scale = 1.0` and `rotation_deg = 0.0`, and let callers opt in to the hard
range. A generator's default should be a pair that *can* be solved. Keep the 1–20× sweep as an
explicit option — it is a great experiment, just not a default.

I have already warned Risheeth to pass `scale=1.0` explicitly, so his numbers this week are safe
either way.

## Then

```bash
python -m pytest evaluation/ -q     # should be 6 passed, 0 failed
git add evaluation/ && git commit -m "metrics: pin the raw-matches contract, fix residual test, log failures instead of None"
git push
```

---

# PART 2 · Day 3 (today) — the one thing only you can build

**~1 hr. Nothing to download, nobody to wait for.**

**You own `results_log.csv`, but you have not given anyone a way to write to it.** So Risheeth wrote
his own CSV appender inside `baselines/`, and I will need one in `core/`. Three people hand-rolling
three writers against one file is how that file ends up with mismatched columns and a merge
conflict nobody can untangle.

**Ship the writer today.** In `evaluation/metrics.py` (or a new `evaluation/logger.py`):

```python
import csv
from datetime import datetime, timezone
from pathlib import Path

RESULTS_LOG = Path(__file__).resolve().parent / "results_log.csv"

FIELDS = ["timestamp", "pair_id", "tier", "method", "config", "rmse_gt_px",
          "residual_px", "inlier_count", "inlier_ratio", "grid_coverage_fraction",
          "distribution_cv", "n_matches", "gsd_mpp", "status", "notes"]

def log_result(pair_id, tier, method, metrics, config=None, gsd_mpp=None, notes=""):
    """Append one run to results_log.csv. The ONLY way anything gets written there."""
    if not tier:
        raise ValueError("tier is mandatory - a number without its tier is meaningless")
    row = {f: None for f in FIELDS}
    row.update(metrics or {})
    row.update(timestamp=datetime.now(timezone.utc).isoformat(), pair_id=pair_id,
               tier=tier, method=method, config=config, gsd_mpp=gsd_mpp, notes=notes)
    new = not RESULTS_LOG.exists() or RESULTS_LOG.stat().st_size == 0
    with open(RESULTS_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)
```

Two things that make this worth doing properly:

- **`tier` is mandatory and it raises if missing.** Your own guide says a number without its tier is
  meaningless. Making it a hard error is how that stays true when everyone is tired on Day 11.
- **`extrasaction="ignore"`** means someone passing an extra key does not crash the run.

⚠️ You are adding two columns (`status`, `notes`) to a header Risheeth has already matched
character-for-character. **Tell him in chat before you push**, and tell him to call `log_result()`
instead of his own writer. That is a two-line change for him and it removes a whole class of future
breakage.

---

# PART 3 · Day 4 — the swept-azimuth curve, your best figure

**~2 hrs.** Your own guide calls this *"your best single figure"*, and as of this morning nothing
blocks it. It uses your `shaded_relief.py`, your `make_pair`, your `metrics.py`, and Risheeth's
baselines — all committed, all working.

> 🔴 **First, one trap that will cost you the afternoon if nobody warns you.**
> **Do not test on a smooth or repeating surface** (sine ripples, a wave pattern). I tried exactly
> that and SIFT found **5 matches at ZERO sun difference** — where the two images are identical
> apart from a shift. Repetitive terrain defeats the ratio test, so you measure the pattern, not the
> sun, and the curve is meaningless.
>
> **Always run the 0° point first as a control.** If it is not in the hundreds, your terrain is
> wrong — fix that before reading anything else.

Use a crater surface. This one is non-repetitive and behaves properly:

```python
def crater_dem(n=420, seed=3, ncr=90):
    rng = np.random.default_rng(seed)
    dem = rng.normal(0, 3, (n, n))
    yy, xx = np.mgrid[0:n, 0:n]
    for _ in range(ncr):
        cx, cy = rng.integers(20, n-20, 2)
        rad = rng.integers(8, 34)
        depth = rad * rng.uniform(0.4, 1.0)
        d = np.sqrt((xx-cx)**2 + (yy-cy)**2)
        dem += np.where(d < rad, -depth*(1-(d/rad)**2), 0.0)                        # bowl
        dem += np.where((d >= rad) & (d < rad*1.25),
                        depth*0.28*(1-(d-rad)/(rad*0.25)), 0.0)                     # rim
    return dem
```

Then sweep the sun and log **every** point, including the failures:

```python
for d in (0, 30, 60, 90, 120, 150, 180):
    s, r, H_true, meta = make_pair(dem, pixel_size_m=10.0, sun_a=(45, 25),
                                   sun_b=(45+d, 25), rotation_deg=0.0,
                                   scale=1.0, shift_px=(10.0, -6.0))
    src_pts, ref_pts = run_sift(u8(s), u8(r))
    m = evaluate(r.shape, src_pts, ref_pts, H_true=H_true)
    log_result(f"synth_sun_{d:03d}", tier="synthetic", method="SIFT",
               metrics=m, gsd_mpp=10.0, notes=f"sun azimuth difference {d} deg")
```

**Here is what I got, so you know yours is working:**

```
 sun diff  matches  inlier_ratio  rmse_gt_px
      0deg      488         1.000        0.00
     30deg       11         0.909        0.75
     60deg        0  too few (<4)           -
     90deg        0  too few (<4)           -
    120deg        1  too few (<4)           -
    150deg        0  too few (<4)           -
    180deg        2  too few (<4)           -
```

**Read what that says.** Gate 2 wants `rmse_gt_px < 0.5` on synthetic. SIFT is at **0.75 by 30° of
sun movement**, and past 30° it cannot produce four usable matches at all. That is the strongest
single argument the project has, and it is measured rather than asserted.

Then add our own method as the second line on the curve. That needs the LoFTR weights
(`weights/loftr_outdoor.pt`, 46 MB, on the Drive) and `pip install torch --index-url
https://download.pytorch.org/whl/cpu`. **Do the SIFT line first and push it** — a one-line curve
today beats a two-line curve on Friday.

⚠️ **Label it "synthetic, DEM-rendered" everywhere it appears.** It is rendered terrain, not
photographs. The shape of the result is real; the exact numbers will move on a real SLDEM tile.

---

# PART 4 · Day 5 — plug into the pipeline, and the first real numbers

**~1.5 hrs.** This is your Day-5 row and it is the one Gate 1 has been waiting on.

1. I will have fixed the raw-matches call by then. Re-run
   `python -m core.pipeline data/pairs/pair_01` and confirm `inlier_ratio` is no longer exactly
   `1.000`. If it still is, tell me — that means my half is not done.
2. Log that run with `log_result()`, and **tier it honestly**. `pair_01` is *not* a validation tier:
   it is two crops of the same frame with an integer offset, identical pixels, no illumination
   difference. **Log it as `tier="same-frame offset crop"`.** Do not let it be called cross-sensor,
   cross-illumination or multi-modal — that is the likeliest question an ISRO judge asks, and the
   answer has to be already right in the file.
3. Get Risheeth's baseline rows into the same file via `log_result()` so the comparison lives in one
   place.

**By the end of Day 5, `results_log.csv` should have real rows in it for the first time.** Until it
does, Invariant 1 means Saniya cannot put a single number on a slide — so this unblocks her, not
just you.

---

# PART 5 · Day 6 — Tier A, and finish the curve

**~2 hrs.** Your Day-6 row.

1. Add our method to the swept curve so it is two lines, and export it as a figure. Save the PNG to
   **Drive, not the repo** — we have already put ~18 MB of images permanently into git twice.
2. Run the full harness on Rohan's Tier A pairs (same sensor, different sun angle).
   ⚠️ **Those pairs do not exist yet** — the dataset card has one row and it points at an image that
   turned out to be blank. Do not sit waiting: say so in chat so it is visible, and spend the time
   on the curve and on hand-checking one pair instead.
3. **Verify one pair by hand.** Take four matched points, compute the transform on paper or in a
   notebook, and check your `evaluate()` agrees. Doing this once is what lets you say "I checked it
   myself" at Gate 5 instead of "the library returned it".

---

# What this builds to

| Day | What you deliver |
|---|---|
| **3** (today) | 4 fixes · the raw-matches contract pinned by a test · `log_result()` shipped |
| **4** | The swept-azimuth curve — the project's best single figure |
| **5** | Pipeline integration · **the first real rows in `results_log.csv`** |
| **6** | Curve finished with both methods · one pair verified by hand |
| **7** | Tier B, and the numbers checked rather than trusted |
| **8** | Full table, all tiers, Tier C degradation quantified. **Gate 2.** |

**Your Gate 5 question is the hardest one on the team:** *"How do you know the alignment is good?"*
After this week you can answer it in one breath — *"Two different numbers. On synthetic pairs I know
the true transform, so I measure real accuracy. On real pairs nobody knows the truth, so I hold out
20% of the matches and report the residual, and I never call that accuracy."*

---

## Rules that still apply

- **`results_log.csv` is yours, and it is the only source of numbers for the whole project.** Nothing
  reaches a slide that is not in it.
- **The `tier` column is mandatory and honest.** `pair_01` is a same-frame offset crop.
- **Never let `rmse_gt_px` become `0.0` when there is no ground truth.** You already got this right;
  keep it that way through every refactor.
- **No figures in git.** Curve PNGs go to Drive.
- **If a task takes 30 minutes longer than it says, say so in chat.** A spec that is wrong is my bug,
  not yours.
