# `core/` — the fixed interfaces

Everything four other people build against. **Locked by `core/test_interfaces.py`**, so a rename
or a reorder fails a test rather than someone else's afternoon.

Changing an interface is allowed. Changing it *silently* is not — update that test in the same
commit and say so in the message.

---

## The chain

```
load  ->  to_common_gsd  ->  normalize  ->  match  ->  filter_matches  ->  warp
                                                   \-> refine (optional)
                                                   \-> counts / redetect (optional)
```

`run_all()` in `pipeline.py` is that chain end to end. Call it rather than reassembling the parts.

---

## Signatures

| Function | Returns |
|---|---|
| `io_loader.load(path, window=None)` | `(float32 2-D array, meta dict)` |
| `io_loader.as_cv_safe(arr)` | float32, 2-D, native byte order, contiguous |
| `io_loader.plan_overlap(meta_a, meta_b, shape_a, shape_b)` | dict |
| `io_loader.crop_to_overlap(src_path, ref_path, out_prefix)` | dict |
| `scale.to_common_gsd(img_a, meta_a, img_b, meta_b)` | `(a, b, gsd, factors)` |
| `scale.to_original(pts, factors)` | `(N, 2)` in original pixels |
| `scale.resample(img, factor_x, factor_y)` | `(img, factors)` |
| `illumination.normalize(img, method="gradient_orientation")` | array in **[0, 255]** |
| `ransac.filter_matches(src, ref, threshold_px=3.0, confidence=0.999, method=USAC_MAGSAC)` | `(src_in, ref_in, H, info)` |
| `ransac.warp(img, H, out_shape)` | warped array |
| `matcher.match(a, b, tile=640, overlap=96, min_confidence=0.2, progress=None)` | `(src_pts, ref_pts, scores)` |
| `subpixel.refine(src_pts, ref_pts, src_img, ref_img, patch=11, search=3, min_peak=0.3)` | `(src_out, ref_out, info)` |
| `subpixel.metres(px, gsd_mpp)` · `subpixel.describe(px, gsd_mpp, grid)` | float · str |
| `distribution.counts(pts, shape, grid=8)` | `(8, 8)` int array |
| `distribution.weak_cells(cell_counts, min_per_cell=2)` | `[(row, col), ...]` |
| `distribution.redetect(src_img, ref_img, H, cells, match_fn=None, ...)` | `(src_new, ref_new, info)` — **built and tested, NOT called by `run_all`.** "We enforce uniformity" is not a claim this repo supports. |
| `pipeline.run_all(src_path, ref_path, H_true=None, progress=None, subpixel=True)` | result dict |
| `reliability.reliability_map(ref_shape, src_raw, ref_raw, H, src_in, ref_in, warped_img, ref_img, gsd_mpp=None, H_true=None, ...)` | dict: `state` (8×8 of `verified`/`weak`/`no_evidence`), `counts`, `global` (verdict, contradicted, cell vote), `true_error_px` when `H_true` is given |
| `reliability.gate(changes, rel, ref_shape, keep_states=("verified",))` | `{"kept", "rejected_weak", "unassessable", "counts"}` |
| `reliability.xcorr_peak(a, b)` | `(dx, dy, ncc)` — the shift that moves `a` onto `b`; sign pinned by test |

`run_all`'s result dict also carries (added 3 Sep 2026): `reliability`, `declared`
(`{"method", "why", "contradicted"}`), `fallback` (None, or the global-correlation translation
with its quadrant spread), `H_final` / `warped_final` (what the system declared and used — the
matcher's own `H` / `warped` are kept unchanged), `src_matches` / `ref_matches` (the raw matches).

Points are **`(x, y)`**, never `(row, col)`. Every one of them, everywhere.

---

## Five rules that are not obvious from the signatures

**1. `load()` returns raw DN, and never rescales.** A loader must not alter science data.
`matcher.py` divides by 255 in exactly one place. A second normalisation anywhere puts every
pixel in `[0, 0.004]`, and LoFTR returns **zero matches with no exception**.

**2. `normalize()` returns `[0, 255]`, not `[0, 1]`.** Same trap, reversed. Guarded by a test
that says so in its failure message.

**3. `None` in metadata means "the label did not say".** Never zero, never a default. A
fabricated sun angle is exactly what Invariant 1 exists to prevent, so handle the `None`.

**4. `refine()` returns source points you did not pass in.** They are rounded to the integer grid
the NCC templates were cut on. Pair `src_out` with `ref_out`; pairing the original fractional
source with a refined reference biases every downstream fit by up to half a pixel, invisibly and
in the flattering direction.

**5. `evaluate()` gets RAW matches, never `filter_matches`' survivors.** Handing it the points
RANSAC already accepted makes `inlier_ratio` ask "of the points RANSAC kept, how many does a
second RANSAC keep?" — always ~1.0. Measured: 0.500 truth versus 1.000 reported on a pair with
half its matches deliberate garbage. Guarded by `core/test_pipeline_contract.py`.

---

## What `core/` deliberately does NOT do

**It does not compute the five metrics.** Those come from `evaluation/metrics.py :: evaluate()`,
which is Samrudh's. If it is missing, `pipeline.py` reports that plainly and computes nothing in
its place. Two implementations of one headline number is how this project shipped an invented
figure through four documents.

**`distribution.py` does not report `grid_coverage_fraction` or `distribution_cv`.** It finds the
empty cells and fills them; the scoring stays with the module that owns it. `GRID` is imported
from `evaluation.metrics`, never redefined here.

---

## Defaults that were measured, not chosen

| Default | Why |
|---|---|
| `method="gradient_orientation"` | `bench_illumination_results.csv` — restores 5023 of 5185 matches under an inverted-and-gamma'd image, where `off` keeps 336. ~15% faster than phase congruency. |
| `subpixel=True` (since 3 Sep 2026) | Two measurements that disagree, and the one Gate 2 is judged on wins. Per-match endpoint error (`bench_subpixel_results.csv`, Day 3): refinement hurt LoFTR (0.336 → 0.431 px). Transform-level `rmse_gt_px` (`results_log.csv`, Day 5 evening, medians over 5 shifts): refinement helps at every sun difference — 0° 0.120 → 0.086, 15° 0.249 → 0.086, 30° 0.571 → 0.314, 45° 1.655 → 1.096 px — and 0.156 → 0.024 px on real OHRC texture. Rows `ours_loftr` (OFF) and `ours_loftr+subpixel` (ON). `--no-subpixel` reproduces the old rows. |
| `tile=640` | `bench_loftr_cpu_results.csv` — the CPU budget on the demo machine. |
| `threshold_px=3.0` | Canonical Facts §6.3. |
| `patch=11`, `grid=8` | Canonical Facts §6.6 and §6.7. |

> ⚠️ `residual_px` and `rmse_gt_px` move independently, in **both** directions. With refinement
> on, `residual_px` fell 0.195 → 0.038 on `pair_01` while the per-match error got worse; on the
> real-texture ground-truth pair it **rose** 0.457 → 0.524 while the transform's true error got
> **better** (0.156 → 0.024). NCC changes how much matches agree with each other; `residual_px`
> measures agreement, not truth. Never read a residual as an accuracy, in either direction.
