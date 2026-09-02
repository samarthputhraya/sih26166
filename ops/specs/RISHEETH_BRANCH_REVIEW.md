# Risheeth — your branch reviewed. Do not merge it as it stands.

**Written 2 Sep 2026 (Day 4).** I reviewed `origin/risheeth-baseline-pipeline` — 11 commits,
2,158 insertions across 13 files — by checking it out into an isolated worktree and running it,
not by reading the diff. Nothing on `main` was touched.

**Short version: there is real, good work here, and it cannot be merged as-is.** Three problems
would break other people's code, and one of them undoes a fix you yourself made. None of this is
hard to put right — most of it is one afternoon — but the merge has to be selective.

---

## ✅ What is genuinely good

**1. `core/bench_loftr_cpu.py` is the most thorough benchmark in the project.** Environment
capture (python/torch/kornia versions, CPU model, core counts, RAM, AC power), a size sweep, a
drift run, thermal and memory guards, and a `skipped_low_memory` state instead of a crash. That is
better instrumentation than I wrote. It also produced a finding nobody had:

```
480 px  -> median 12.165 s, 1618 matches
640 px  -> SKIPPED, low memory     (3.26 GB free of 16.79)
1024 px -> SKIPPED, low memory
640 px drift run -> median 21.077 s, drift 1.7%
noise input      -> 139 matches (vs 2824 on lunar)  <- good negative control
```

**640² does not fit on your machine.** It runs fine on mine. That is a real constraint on who can
run what, and it belongs in `STATUS.md`.

**2. You added the test file.** `baselines/test_baselines.py` with the parametrised shift-recovery
and blank-image tests, and a `get_points()` helper so the tests do not care about tuple width.
That is the right shape.

**3. Returning `confidence` and `elapsed` from each baseline** is a genuine improvement. Match
count alone does not tell you whether the matches are any good.

---

## 🔴 What blocks the merge

### 1. AKAZE is completely broken — and you had already fixed this

```python
akaze = cv2.AKAZE_create()
AttributeError: module 'cv2' has no attribute 'AKAZE_create'
```

**Two of your own tests fail on your own branch** because of it. In OpenCV 5 it is
`cv2.xfeatures2d.AKAZE_create()`.

You had this right on `main`, *with a warning comment you wrote yourself*:

> `IMPORTANT: In OpenCV 5.x, AKAZE moved to cv2.xfeatures2d.AKAZE_create().`
> `Do NOT use cv2.AKAZE_create() - it raises AttributeError.`

The rewrite dropped the fix and the comment. This is the single strongest argument for patching
rather than rewriting: **a rewrite loses the scar tissue.** It is Known Issue #8 in our own
`STATUS.md`.

⚠️ Related: `baselines/results.csv` on your branch shows AKAZE finding 1922 matches. That cannot
have come from this code, because this code raises. The CSV is stale — generated before the
regression — so it reads as evidence that something works when it does not.

### 2. You modified Samrudh's files, and they now conflict

`evaluation/metrics.py` (+285) and `evaluation/test_metrics.py` (+157) are **Samrudh's**. He has
been actively developing both on `main` — his latest is 1 Sep 16:47, yours is 1 Sep 11:39.

I ran a trial merge. It conflicts in **both** files. Resolving it means someone chooses between
two divergent versions of the module that produces every number in the project, which is exactly
the situation one-owner-per-folder exists to prevent.

### 3. A breaking signature change that reaches outside `baselines/`

| | `main` | your branch |
|---|---|---|
| `run_sift(img1, img2)` | returns **2** values | returns **4** |
| `make_pair(dx, dy, seed)` | returns **2** values | returns **3** |

`core/bench_subpixel.py` on main unpacks two values from `run_sift`. Merging your branch breaks it
silently at the call site.

The four-value return is a good idea. It just needs to arrive as a deliberate interface change we
both know about, not inside a merge.

### 4. Neither blocking bug from your spec is fixed

- **Pair discovery still fails.** I ran your failure gallery: `No pairs found in data/pairs/`.
  Pairs live in `data/pairs/<pair_id>/<pair_id>_source.tif` — each in its own folder. You need the
  `*/` in the glob and the `pair_id` in the path.
- **The harness no longer runs on real data at all.** It is now hardcoded to one synthetic pair
  (`pair_test_source.tif`, tier `TEST`). Config 1 vs Config 2 — raw versus illumination-normalised,
  the entire point of the comparison — is gone.

### 5. It writes to the wrong file

Your branch writes `baselines/results.csv` with its own schema. **Every number in this project has
to come from `evaluation/results_log.csv`** — that is Invariant 1, and it is why Samrudh built
`evaluation/logger.py`. A second results file with a second schema is how two numbers for the same
thing end up in a deck.

### 6. The branch is 21 commits behind `main`

Since you branched: the `inlier_ratio` fix (we were passing Gate 2's threshold automatically),
`subpixel.py`, `distribution.py`, the Tier D decision, the LOLA route, and an `io_loader` crash on
every CH-2 product.

---

## What to do — in this order, ~3 hours

**Do not merge the branch. Do not delete it either.** Bring the good parts across in three small
commits that each land on current `main`.

### Step 1 — Rebase onto main first (20 min)

```bash
git checkout risheeth-baseline-pipeline
git fetch origin
git rebase origin/main
```

Take **main's version** of `evaluation/metrics.py` and `evaluation/test_metrics.py` on every
conflict — they are Samrudh's and his are newer. Your branch should end up with **no changes to
`evaluation/` at all.**

### Step 2 — Land the benchmark on its own (30 min)

`core/bench_loftr_cpu.py` is mine, but the work is yours and it is better than what is there.
**Open it as a separate commit and tell me** — I will review and merge it rather than have it ride
in with everything else. Add one line to `ops/STATUS.md` recording that 640² is skipped for low
memory on your machine; that is a demo-machine fact and Gate 4 depends on knowing it.

### Step 3 — Fix the four things in `baselines/` (90 min)

1. **AKAZE:** restore `cv2.xfeatures2d.AKAZE_create()` **and the warning comment**.
2. **Pair discovery:** `data/pairs/<pair_id>/<pair_id>_source.tif`; glob `*/*_source.tif`; fix it
   in `run_all_baselines.py` *and* `draw_failure_gallery.py`. Then skip `pair_00_dryrun` — it is a
   known-fake fixture that reports flatteringly good numbers.
3. **Config 2:** `illumination.normalize()` returns float32, SIFT/ORB/AKAZE need uint8. Wrap it:
   `np.clip(x, 0, 255).astype(np.uint8)`. This half of the comparison has never once run.
4. **Logging:** delete your `CSV_FIELDS` and your writer. Use Samrudh's:
   ```python
   from evaluation.logger import log_result
   ```
   His schema has 15 columns; yours has 13. As written you would append short rows to
   `results_log.csv` and misalign it.

### Step 4 — Then the real run

```bash
python -m baselines.run_all_baselines --pairs pair_01
```

Expected, from my run of the patched code — if you get roughly these, you are correct:

```
method  config          matches   recovered shift  (truth -40, -25)
SIFT    1 raw               442   (-40.00, -25.00)
SIFT    2 illum_norm       4780   (-40.00, -25.00)
ORB     1 raw               739   (-39.81, -24.88)
ORB     2 illum_norm       2625   (-40.00, -25.00)
AKAZE   1 raw               263   (-40.00, -25.00)
AKAZE   2 illum_norm       3073   (-40.00, -25.00)
```

> 🔴 **Do not write "illumination normalisation helps across sun angles" from that table.**
> `pair_01` is two crops of the *same frame* — there is no illumination difference in it at all.
> What it shows is that normalisation raises match count on identical imagery. The sun-angle claim
> comes from the synthetic swept-azimuth test, not from here. Name the pair type —
> *"same-frame offset crop"* — every time you quote it.

---

## Why this matters more than it looks

You are the critical path for Gate 2's *"≥2× better than the best classical baseline"* criterion.
That number cannot be computed until your harness runs on real pairs and logs to
`results_log.csv`. Everything else for Gate 2 is either done or has a route.

**And the quality of your code is not in question.** Your baselines on `main` recover the known
shift exactly, and your benchmark is better than mine. The problem is entirely about *where the
changes landed* and *rewriting instead of patching* — both fixable in an afternoon, and neither
says anything about whether you can write the code.

---

## Rules worth restating

- **One folder per person.** Yours is `baselines/`. `evaluation/` is Samrudh's, `core/` is mine.
  Found a bug in someone else's? Tell them — or open it as its own commit and say so.
- **Patch, do not rewrite.** A rewrite loses the traps someone already paid for. The AKAZE line is
  the proof.
- **`results_log.csv` is the only results file.**
- **Rebase before you build.** Twenty-one commits of drift is how signatures diverge.
- **If any step runs 30 minutes over, say so in chat.** A wrong spec is my bug, not yours.
