# Samrudh — Days 5 to 8

**Written:** 2 Sep 2026 (Day 5). This spec was owed on Day 4 and never arrived — the agent
drafting it died mid-run. Sorry about that; it was mine to get to you and I didn't.

**Your headline this week:** you own the one remaining open criterion in the re-scoped Gate 2.
Everything else is either met or dropped — see `ops/specs/GATE2_SCOPE_CUT.md`.

---

## First, credit

- **`log_result()` + the newline fix** unblocked the whole project this afternoon. Before it,
  `results_log.csv` had 155 bytes, no terminator, and `csv.DictReader` parsed **zero** rows —
  so every number we had was uncitable under Invariant 1. Your one byte turned that around;
  the file now holds 29 readable rows.
- **`swept_azimuth_curve.py`** is the right shape: sweep a parameter, log every point including
  the failures, plot it. That is what a defensible result looks like.
- **`metrics.py`'s held-out split** is the reason our `inlier_ratio` means anything. Keep
  defending it — it is the single best answer you have for a Gate 5 viva.

---

## 🔴 Day 5 — the one that matters: make ours and classical comparable

### The problem, precisely

`results_log.csv` now holds **two sets of `tier=synthetic` rows that look comparable and are
not**:

| | rows | `gsd_mpp` | `config` | DEM |
|---|---|---|---|---|
| `method=SIFT` (yours) | 7 | **10.0** | **empty** | not recorded |
| `method=ours_loftr` (mine) | 20 | **60.0** | full | `dem_site_60m.npy` (375×364) |

At Δazimuth 0° your SIFT row logs `rmse_gt_px = 0.00355` and my median is `0.11992`. Read
straight off the file that says **"SIFT is 34× better than the learned matcher"** — and it is
not a comparison at all, it is two different experiments at a 6× ground-scale difference.

Someone will make that comparison. It might be a judge.

### What to build

**One script that runs all four methods on the SAME pair, at the SAME scale, in one pass**, and
logs one row per (method, angle, shift).

You now have exact ground truth on demand. `core/pipeline.py` grew a `--synthetic` mode today:

```bash
python -m core.pipeline --synthetic \
  --dem C:/Users/samar/sih26166_data/raw/dem_site_60m.npy \
  --pixel-size 60 --sweep 0,15,30,45 --repeats 5 --log
```

`core.pipeline._synthetic_pair(dem_path, pixel_size_m, sun_delta_deg, shift_px=..., seed=...)`
returns `(src_path, ref_path, H_true, meta)`. `H_true` maps **source → reference in (x, y)** —
the same direction your `evaluate()` fits, so it drops straight into
`evaluate(ref_shape, src, ref, H_true=H_true)`.

⚠️ **Importing `core.pipeline` pulls in torch.** If that is awkward for a classical-only script,
ask me to lift `_synthetic_pair` into a torch-free module — that is a 10-minute job on my side
and you should not work around it.

**Three things that will bite you, all measured:**

1. **Use an off-grid shift.** An integer translation is the one case `cv2.warpPerspective` does
   not interpolate — the warped image is a literal pixel copy and the truth lands exactly on the
   detector's integer grid. Measured at 30°: shift `(12, -8)` gives 0.412, shift `(11, -9)` gives
   1.045. Same everything else. The default `SYNTH_SHIFT_PX` is `(12.37, -8.63)` for this reason.
2. **Report the median of several shifts, never the best.** One shift is one sample. At 30° the
   five shifts spread 0.712 → 1.653.
3. **`render_shaded_relief` returns [0, 1] floats and `cv2` detectors want uint8.** Scale by 255
   before handing anything to SIFT/ORB/AKAZE, or you will get a keypoint famine and read it as a
   result.

### Fill in your `config` column

Your 7 existing rows have an empty `config`, which makes them unreproducible — nobody can tell
which DEM, which scale, which shift produced them. Either re-run them with `config` populated or
mark them superseded. Mine look like:

```
dem=dem_site_60m.npy (375, 364); d_azimuth=0deg at fixed 30deg elevation;
shift=(+12.3700,-8.6300); rot=0; scale=1; seed=0
```

### Done when

A table you can put on a slide:

| Δazimuth | ours | SIFT | ORB | AKAZE | ratio vs best classical |
|---|---|---|---|---|---|
| 0° | | | | | |
| 15° | | | | | |
| 30° | | | | | |
| 45° | | | | | |

every cell a `rmse_gt_px` median over ≥3 shifts, every row in `results_log.csv`, one command to
reproduce it. **That is Gate 2's last open criterion.**

⚠️ **Coordinate with Risheeth before you start.** His `run_all_baselines.py` is currently broken
(hardcoded paths to files that do not exist, and his AKAZE call raises on this machine — see
`ops/specs/RISHEETH_REVIEW.md`). Either he fixes it first, or you call
`baselines/{sift,orb,akaze}_baseline.py` directly and skip his harness. **Do not fix his files
yourself** — Gate 5 asks him to explain them cold.

---

## Day 6 — two small fixes in your own file

**1. `log_result()` has one guard, not two.** I recorded in `STATUS.md` that it enforced both a
mandatory tier and a failure status. That was wrong and I have corrected it. It checks tier only:

```python
log_result("x", "A", "m", {"status": "ransac_failed", ...})   # accepted, writes a row
```

A failed registration therefore enters the evidence file as an ordinary row with blank
`rmse_gt_px` and `residual_px`. **Blank is not zero and it is not a pass.** I added a guard on
the `core/pipeline.py` side, but the file is yours and the guard belongs in it. Suggested:

```python
if metrics and metrics.get("status") not in (None, "ok"):
    raise ValueError(f"refusing to log a failed run ({metrics['status']}) as a result")
```

Your call whether to raise or to require an explicit `allow_failed=True` — recording failures on
purpose is legitimate, which is exactly what your azimuth sweep does. Silently is the problem.

**2. `swept_azimuth_curve.py:41` uses a bare `m['status']`.** It is correct against your own
`metrics.py`, but it means any change to that return dict takes the script down with a
`KeyError`. Risheeth's branch does exactly that. `.get('status', '?')` for display only —
**do not** soften the guard above the same way.

---

## Day 7 — hold the line on the numbers

You own `results_log.csv` and therefore Invariant 1. As the deck comes together, you are the
person who says **"that figure is not in the file"**. Two currently in flight to watch:

- **`pair_01` is not Tier A.** Two crops of ONE OHRC frame, same sensor, zero sun difference. It
  is logged as `same-frame offset crop`, matching Rohan's catalogue. Two guides still call it
  Tier A with a 26° sun difference — `RISHEETH_BASELINE_GUIDE.md:234`,
  `ROHAN_DATA_GUIDE.md:227`. I am fixing those.
- **Tier D produces matches and does not register.** `residual_px 37.81` = **2268.76 m** on the
  ground, `inlier_ratio 0.5263` — which is *below* Gate 2's 0.60. If anyone writes "works on
  multi-modal data", that is the row to point at.

---

## Day 8 — Gate 2

Re-scoped; read `ops/specs/GATE2_SCOPE_CUT.md`. Short version: Tier A and Tier B are being
dropped, the classical comparison moves onto synthetic where we have exact ground truth, and on
that definition **we are at 5 of 6 with your task as the only open item**.

Bring: the comparison table, and the sun angle we are choosing. It is 15° — at 30° `rmse_gt_px`
fails and at 45° everything fails, and we show the whole curve including the part that breaks.

---

## Anything blocking you

Message me. Two of the three things blocking you this week were mine (this spec, and the
`--synthetic` path that gives you ground truth), and both are cleared as of tonight. If a third
turns up, it is a bad spec, not your problem — tell me the same evening.
