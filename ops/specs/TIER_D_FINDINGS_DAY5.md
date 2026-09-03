# Tier D — what bet A found, and the two things it found on the way

**Day 5 (3 Sep 2026), afternoon session. Samartha.**
Everything below is reproducible with `python -m ops.tier_d_investigation`.
Three rows were logged to `evaluation/results_log.csv` (now 46 rows).

**Nothing in anyone else's folder was edited.** Two of the three findings are fixes
that belong to other people, and they are written here as findings for their owners —
`docs/02_DAILY_REVIEW_PROTOCOL.md` rules, and Gate 5 means you have to be able to
explain your own module's bug yourself.

---

## 1. Bet A failed. Cleanly, and we now know why.

**The hypothesis** (from `ops/PLAN_TO_9_SEP.md` Part 1): Tier D scores 37.81 px because
`core/scale.py:101` resamples to the **coarser** grid, downsampling the 640×640 Kaguya
optical image to 99×99 before matching. LoFTR's coarse stage then runs at stride 8 on a
12×12 grid — an effective 500 m/px against elevation data carrying 60 m/px. Render the
DEM into the *sensor's* grid instead and the coarse stage lands at 75 m/px, matched to
what the data actually holds.

**Built it.** `ops/build_tier_d_native.py` samples the LOLA DEM at the Kaguya crop's own
pixel centres — 640×640 at 9.3698731836556 m/px — so `to_common_gsd` becomes an exact
no-op and the match runs at full resolution.

**The prediction was half right and it did not help.**

| | matches | inlier ratio | residual |
|---|---|---|---|
| `pair_03_tierD` — coarse grid, 99×99 | 19 | 0.526 | 2268.8 m |
| `pair_04_tierD_native` — 640×640 | **105** | **0.048** | **3995.6 m** |

5.5× more correspondences, exactly as predicted. **All of the extra ones are wrong.**

### The confound I had to remove first

Comparing those two rows naively is invalid, and it took a second experiment
(`ops/bet_a_experiment.py`) to say so. Both RANSAC gates are in **pixels**:

    core/ransac.py:52        DEFAULT_THRESHOLD_PX = 3.0
    evaluation/metrics.py:5  INLIER_THRESH_PX     = 3.0

On the 60 m/px grid, 3 px is a **180 m** ground tolerance. On the 9.37 m/px grid it is
**28 m**. The native-grid arm was silently judged against a bar 6.4× stricter.

Re-asking both arms the same question, in metres:

| arm | tol 28 m | tol 60 m | tol 100 m | tol 180 m | tol 300 m |
|---|---|---|---|---|---|
| `pair_03_tierD` residual | 2456 m | 2269 m | 2269 m | **2269 m** | 2391 m |
| `pair_04_tierD_native` residual | 3996 m | 3996 m | 3996 m | **3996 m** | 5211 m |

The fine grid is worse at **every** equal ground tolerance. The threshold was not the
story. Bet A is a genuine negative.

> **Note for whoever writes the sub-pixel slide:** `residual_px` on two grids 6.4× apart
> cannot be compared, and the plan's own success criterion ("residual_px materially below
> 37.8") would have been a **6.4× stricter** bar than intended. Canonical Facts §2 already
> requires naming the pixel grid. This is what that rule is for.

---

## 2. 🔴 The shaded relief has been lit from the wrong side. All project long.

**Owner: Samrudh — `evaluation/shaded_relief.py:10-16`.**

Rendering the DEM at the recorded solar azimuth and correlating it against the Kaguya
optical image of the same ground:

```
as-recorded  az 284.901°   NCC vs optical at zero offset   -0.5744
corrected    az 104.901°   NCC vs optical at zero offset   +0.5926
```

A **negative** correlation of that size is not noise — it is the same terrain, shaded
backwards. I tested eight gradient/sign conventions at the recorded azimuth; exactly one
flips the sign, and it is negating **both** gradients:

```python
dzdx, dzdy = np.gradient(dem.astype(np.float64), pixel_size_m)   # line 10
aspect = np.arctan2(-dzdy, dzdx)                                  # line 12
```

Negating both is `aspect → aspect + 180°`. So `render_shaded_relief(dem, az, ...)` lights
the terrain from **`az + 180`**. Confirmed independently by an azimuth sweep: correlation
peaks near 120° and troughs near 300°, and 284.901° sits in the trough.

**What this contaminates.** Every Tier D row in `evaluation/results_log.csv` — ours *and*
Risheeth's SIFT 36.03 / ORB 26.76 / AKAZE 10.95 — was scored against a reference lit from
the opposite side. **Including the AKAZE result we call Q&A killer #2.**

It does **not** touch the synthetic sun-azimuth sweep's headline numbers: those compare
two renders of the same DEM to each other, so a constant 180° offset cancels. The 15°
Gate 2 result stands. What changes is anything comparing a render to a *real optical
image*, which is Tier D and only Tier D.

**Samrudh:** the fix is a sign, but please derive it rather than pasting it — Gate 5 asks
you to explain your own module. `ops/tier_d_investigation.py` prints the evidence, and
the eight-convention test is easy to re-run.

⚠️ **Fixing it does not rescue Tier D** — see §4. Fix it because it is wrong, not because
it will help.

---

## 3. Tier D has ground truth now, and it never did before

Because the reference is sampled on the optical image's own grid, the true alignment is a
translation, recoverable without any feature matching. FFT cross-correlation over the full
±320 px range:

```
global peak (dx,dy) = (-9, +23) px = (-84, +216) m    NCC +0.7139
  top-left     (-9,+23)  +0.5455       bottom-left  ( 0, +1)  +0.7524
  top-right    (-8,+23)  +0.6409       bottom-right (-9,+21)  +0.5381
```

**Three of four quadrants agree within 2 px. The fourth does not.** So this is *not* a
perfectly uniform translation — there is real spatial variation, and the honest statement
is "the two products are offset by roughly 100–230 m", not a single exact number. That is
recorded in the logged row rather than smoothed over.

It does not weaken §4: the two candidate truths differ by ~24 px and the matcher is wrong
by ~200 px against either.

---

## 4. 🔴 The finding that actually matters: we have never had a correct Tier D match

Scoring LoFTR's raw matches against that ground truth:

| lighting | matches | RMSE vs truth | median error | within 10 px (94 m) |
|---|---|---|---|---|
| as-recorded | 107 | 259.8 px = **2434 m** | 222.6 px | **0 / 107** |
| corrected | 94 | 268.9 px = **2520 m** | 204.0 px | **0 / 94** |

**Zero correct correspondences, under either lighting, at any tolerance we would accept.**
The scene is 5997 m across; the median match is wrong by a third of the frame.

So the 37.81 px we have been quoting as a Tier D result was never a degraded registration.
**It is RANSAC fitting a plausible homography to matches that are all wrong** — which is
precisely what a consensus algorithm will do when handed enough noise, and precisely why
`residual_px` (self-consistency) must never be read as accuracy. `core/pipeline.py:21-23`
already warns that `residual_px` and `rmse_gt_px` are not interchangeable. This is that
warning coming true on real data.

**And a simple FFT cross-correlation registers the same pair, at 0.714 peak correlation,
with no features and no RANSAC.** Logged as `fft_phase_correlation`, deliberately with
**no `rmse_gt_px`**: it defines the reference alignment, so scoring it against itself
would be circular. Its evidence is the quadrant agreement, not an accuracy number.

---

## 5. What this does to Gate 2, and what to say instead

Gate 2 (Canonical Facts §11) requires: *"produces matches on ≥1 multi-modal (Tier D,
optical↔elevation) pair with degradation quantified in metres."*

Read literally, we pass — we produce matches, and we can now quantify degradation in
metres better than ever. **Read honestly, passing it that way would be the single most
dangerous thing in the deck.** "Show me one of those multi-modal matches" ends it.

**The good version of this, and it is better than bet A would have been:**

> We tested our matcher against optical↔elevation and it produced 105 correspondences,
> none of them correct. We know they are wrong because we built ground truth for that pair
> ourselves. Feature matching has no purchase on a hillshade — so for that case we register
> by global correlation instead, which lands it inside ~230 m. We report which method is
> being used and why.

That is the *"a registration system that knows when it is wrong"* theme, on real data,
with a number attached — and it is the honest reading, not spin. It needs a decision from
the team, not from me.

---

## 6. Actions, by owner

| Who | What | Why it is theirs |
|---|---|---|
| **Samrudh** | Fix the 180° flip in `evaluation/shaded_relief.py`. Derive the sign yourself. | His module; Gate 5. |
| **Samrudh** | Still owes the illumination-OFF sweep and the `RESULTS_LOG` test-contamination fix. Unchanged, still the highest-value measurement open. | |
| **Risheeth** | His three Tier D baseline rows were scored against a wrongly-lit reference. **Do not delete them** — re-run after Samrudh's fix and keep both, the delta is evidence. | His folder. |
| **Rohan** | `ops/build_tier_d_pair.py` renders through the same function, so `pair_03_tierD` inherits the bug. Regenerate after the fix. | His file. |
| **Team** | Decide §5: reframe the multi-modal claim honestly, or drop it. **This is a deck decision and it is due before Gate 2 on Day 7.** | |
| **Samartha** | Bet B (`core/reliability.py`) is now the only live novelty bet. Bet A is closed. | |

## What I did not do

- Did not edit `evaluation/shaded_relief.py`, `evaluation/metrics.py`,
  `ops/build_tier_d_pair.py`, or anything in `baselines/`.
- Did not change `core/scale.py`. Its "downsample is the honest direction" reasoning
  survives this: upsampling did not invent useful detail, it invented *matchable-looking*
  detail, which is worse. The docstring was right.
- Did not delete or edit any existing row in `results_log.csv`.
- Did not tune the sun angle to make anything work — the corrected azimuth is
  `recorded + 180`, from the convention error. A sweep peaks ~15° away from that; that
  extra 15° is not claimed and not used.
