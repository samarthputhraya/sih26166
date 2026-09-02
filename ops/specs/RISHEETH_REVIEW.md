# Review — `risheeth-baseline-pipeline` @ `d473876`

**Reviewed:** 2 Sep 2026 (Day 5) · against `main` @ `9794a4d`
**Verdict:** **Do not merge as-is.** Four blockers — but the fix is mostly *un-doing*, not
rework. One `git checkout` clears three of them.

Findings only, nothing fixed for you. `baselines/` is yours, and Gate 5 asks you to explain
your own module cold.

---

## Credit first, because it is real

- **You rebased, cleanly.** 11 commits, and a trial merge produces **zero conflicts**. That is
  exactly what you were asked for on Day 4.
- **`baselines/test_baselines.py` is new and wanted.** Before it, `pytest baselines/` collected
  **zero tests** and exited 5. That gap had been open since Day 2.
- **`make_test_pair.py` and the failure-gallery script** are real deliverables against the
  Day 5/6 row.
- **Repo hygiene is good** where it counts: only `.gitkeep` is tracked under
  `baselines/failure_gallery/`. No binaries added. Invariant 5 respected.

---

## The one thing that explains almost everything

**The rebase carried OLD versions of files forward as if they were new work.** This is a rebase
problem, not a coding problem — and it silently reverted fixes that already exist on `main`,
including **one of your own**.

Blockers 1–3 are all symptoms of that single cause. Fix the cause and they go together.

---

## Blocker 1 — you reverted your own AKAZE fix

`baselines/akaze_baseline.py:19` on your branch:

```python
akaze = cv2.AKAZE_create()
```

Reproduced on the demo machine:

```
$ python -c "import cv2; print(cv2.__version__); cv2.AKAZE_create()"
5.0.0
AttributeError: module 'cv2' has no attribute 'AKAZE_create'

$ python -c "import cv2; cv2.xfeatures2d.AKAZE_create(); print('OK')"
OK
```

**`main` already has this right — and you wrote it.** Commit `5067ffb`, 31 Aug, your name,
`baselines/akaze_baseline.py:44`:

```python
return _run_binary(cv2.xfeatures2d.AKAZE_create(), img1, img2)
```

with a docstring at lines 7–8 saying, verbatim: *"IMPORTANT: In OpenCV 5.x, AKAZE moved to
cv2.xfeatures2d.AKAZE_create(). Do NOT use cv2.AKAZE_create() - it raises AttributeError."*

Your branch puts the broken call back. Cost: the AKAZE baseline is dead, and it fails **2 of
your own 6 tests**, turning the root suite red.

> Worth checking: you may be developing against **OpenCV 4.x**, where `cv2.AKAZE_create()`
> exists. The demo machine is **5.0.0**, and Invariant 3 says the demo machine is what counts.

---

## Blocker 2 — `evaluation/metrics.py` drops the `status` key

Your branch rewrites Samrudh's `evaluation/metrics.py` (+290 lines). The constants are all
safely unchanged (`GRID=8`, `INLIER_THRESH_PX=3.0`, `USAC_MAGSAC`, `holdout_frac=0.2`) — but
the return dict loses one key. Reproduced by swapping **only** that file into a copy of main:

```
YOURS : [distribution_cv, grid_coverage_fraction, inlier_count,
         inlier_ratio, n_matches, residual_px, rmse_gt_px]        # 7 keys
MAIN  : [ ... the same 7 ... , status]                            # 8 keys
```

Two things break, both silently:

1. **`core/pipeline.py --log` stops writing to `results_log.csv`, permanently.** The guard is
   `elif m.get("status") != "ok":`. With your version `.get` returns `None` for a *perfect*
   registration, so every run is classified a failure and refused. **Exit code stays 0**, so
   nothing announces it. Under Invariant 1 no number could ever become citable again.
2. **Samrudh's `evaluation/swept_azimuth_curve.py` dies.** He pushed it at 14:47 today; your
   branch predates it.

```
$ python -m evaluation.swept_azimuth_curve
  File "evaluation/swept_azimuth_curve.py", line 41
    f"status={m['status']:16s}  ..."
KeyError: 'status'
exit: 1
```

Your rewrite *does* contain three genuine improvements — input coercion, a length-mismatch
guard, and a grid clamp for negative coordinates. They are good. They are just in someone
else's file, and they arrived with a regression attached. Offer them to Samrudh as a patch
instead of carrying them here.

---

## Blocker 3 — the harness cannot run, for anyone

`baselines/run_all_baselines.py:20-21`:

```python
PAIR_SOURCE    = ROOT / "data" / "pairs" / "pair_test_source.tif"
PAIR_REFERENCE = ROOT / "data" / "pairs" / "pair_test_ref.tif"
```

Neither file exists. And `baselines/make_test_pair.py:93-94` — the thing meant to create them —
writes somewhere else, with a different extension:

```python
cv2.imwrite("baselines/test_source.png", src)
cv2.imwrite("baselines/test_ref.png", ref)
```

Different directory **and** different format, so it fails on your machine too.

Same file, related:

- `load_gray()` uses raw `cv2.imread` instead of `core.io_loader.load`. It therefore cannot read
  the Tier D GeoTIFF, cannot read PDS4, and loses the big-endian and signedness handling that
  `io_loader` exists to provide.
- **Pair discovery was removed rather than fixed.** The known defect was globbing
  `data/pairs/*_source.tif` flat while pairs sit one level down; `**/*_source.tif` fixes it.
  Hardcoding two paths means the harness can never touch `pair_01` or `pair_03_tierD` — and
  **Gate 2 criterion 2 requires baselines on a real pair.**

---

## Blocker 4 — `.gitignore` drops `*.npy` and `*.raw`

Your `.gitignore` deletes these two lines and the comment explaining them:

```
# Raw range-fetched DEM windows (ops/fetch_lola_dem.py)
*.raw
*.npy
```

`data/raw/*` still covers the DEM at the data root, so nothing is at risk today. But a `.raw` or
`.npy` written **anywhere else** — e.g. `ops/`, which is exactly where `fetch_lola_dem.py` runs
— is now committable. Those artifacts total **77 MB**. Invariant 5 caps the repo at ~5 MB, git
history is permanent, and we already carry one 10.44 MB mistake.

Lower priority in the same diff:

- It adds `evaluation/results_log.csv` to `.gitignore`. I tested this — the file stays tracked
  and `git add` still works, so it is a **latent trap, not an immediate break**. Still: that
  file is Invariant 1's single source of truth and must stay shared. Drop the line.
- A **trailing TAB** on the last line silently disables the
  `data/lroc_analysis/M124545845LE_enhanced.png` rule.
- The explanatory comments were deleted. They recorded *why* each rule exists, which is what
  stops the next person removing it.

---

## Trial merge, measured

| | `main` | merged with your branch |
|---|---|---|
| `pytest -q` | 113 passed, 1 skipped — **exit 0** | 116 passed, **2 failed**, 1 skipped — **exit 1** |
| Gate 1 `residual_px` | `0.19452325191421008` | `0.19452302157878876` |

Gate 1 still passes (exit 0), but its published number shifts in the 7th decimal — your
`metrics.py` downcasts inputs to float32. Small, but that figure is quoted in `STATUS.md` and
would stop reproducing.

---

## What to do — roughly 30 minutes

**1. Take `evaluation/` and `core/` off the branch.** Three blockers vanish in one command,
because `main` already has better versions:

```bash
git checkout origin/main -- evaluation/ core/ .gitignore
```

Then re-add only the `.gitignore` lines that are actually yours:

```
# Generated baseline evaluation outputs
baselines/failure_gallery/*.jpg
```

**2. Restore your own AKAZE fix** in `baselines/akaze_baseline.py`:

```python
akaze = cv2.xfeatures2d.AKAZE_create()
```

and check your local OpenCV version against the demo machine's 5.0.0.

**3. Make the harness runnable.** Either point `run_all_baselines.py` at what
`make_test_pair.py` actually writes, or better — restore discovery so it works on real pairs:

```python
pairs = sorted(Path("data/pairs").glob("**/*_source.tif"))
```

and switch `load_gray` to `core.io_loader.load`.

**4. Re-run and confirm:**

```bash
python -m pytest -q                          # expect exit 0, no AKAZE failures
python -m core.pipeline data/pairs/pair_01   # expect residual_px 0.19452325191421008
python -m evaluation.swept_azimuth_curve     # expect exit 0
```

**5. Send your three `metrics.py` improvements to Samrudh separately** — as a patch or a
message, not on this branch. They are worth having.

---

## Two open questions for Samartha, not for Risheeth

- **Where do baseline numbers live?** `run_all_baselines.py` writes `baselines/results.csv` with
  10 self-invented columns (`mean_confidence`, `dx_px`, `offset_spread_px`) and `tier=TEST` —
  none of the five metrics — bypassing `log_result()` and its mandatory-tier guard. That matches
  `core/bench_illumination.py`'s stated policy ("Samrudh owns results_log.csv") but contradicts
  Gate 2 criterion 2, which needs `ours` and the classical methods **comparable in one file**.
  This needs a ruling and it is not Risheeth's to make.
- **Gate 2-alt needs a raw-vs-normalised arm.** The claim is "classical + our preprocessing
  beats classical alone", which requires running the baselines **both** ways. Nothing in
  `baselines/` imports `core/illumination.py`. If Gate 1 holds, Gate 2-alt never activates and
  this is moot — worth deciding before Day 8 rather than after.

---

## Scope of this review

Blockers 1–4 and the merge table were each reproduced by hand on the demo machine, reading from
the immutable git ref (`git show origin/risheeth-baseline-pipeline:<path>`). A broader automated
pass produced further findings that are **not** included here because they were not
independently confirmed — two of its claims were overstated and are corrected above
(`results_log.csv` supposedly unaddable; supposedly tracked gallery binaries). Neither was true.
