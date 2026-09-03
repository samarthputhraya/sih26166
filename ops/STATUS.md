# STATUS — end of Day 5 (3 Sep 2026)

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewritten in full, not appended.** True as of 3 Sep 2026, ~11:00 IST.

---

## 🔴 THE DATE IS KNOWN — this changes the schedule

**The internal hackathon is 9 September 2026 = Day 11.** Confirmed by the SPOC today.
Open since Day 0; now closed.

**7 days including today.** Two gates were scheduled on or after the event and have been moved:

| Gate | Was | Now | Why |
|---|---|---|---|
| 4 (demo 3× offline) | Day 11 | **Day 9 (7 Sep)** | Day 11 *is* the event |
| 5 (all six explain cold) | Day 12 | **Day 10 (8 Sep)** | Day 12 is *after* the event |

Full reasoning and the approved plan live in
`C:\Users\samar\.claude\plans\i-asked-abt-the-nifty-origami.md`.
**That plan is approved and is what the next session executes. Read it first.**

**Format:** pitch-primary. The SPOC says a live demo is **not compulsory** for software projects, and
there is **no prior upload** — we present on the day. So capabilities need to reach *"a measured
result plus one figure on a slide"*, not polished-UI standard. We carry a demo anyway because it
differentiates, but **the deck must score on its own.**

---

## Position

```
Day 5 of 11  |  6 days to the event  |  Internal hackathon: 9 SEP 2026 (CONFIRMED)
Gate 1: PASSED and reproducible      Next: Gate 2 on Day 7 (5 Sep, moved from Day 8)
```

**Smoke test — run this session, exit codes observed, not inferred:**

| Check | Exit | Result |
|---|---|---|
| `pytest evaluation/ -q` | **0** | 9 passed |
| `pytest -q` (full) | **0** | **179 passed** |
| `import core.pipeline` | **0** | ok |
| `python -m core.pipeline data/pairs/pair_01` | **0** | `residual_px 0.19452325191421008` — exact, unchanged |

---

## What landed today

- **`app/streamlit_app.py` now exists** (Samartha). Was scheduled for Day 9, shipped Day 5 — that
  four-day surplus is what pays for the novelty work in the plan. Verified by *executing* it with
  `streamlit.testing.v1.AppTest`: 0 exceptions on first render and through a full
  select-pair → Align → render cycle. 21 tests in `app/`.
- **The classical baselines ran on real lunar data for the first time in the project's history**
  (Samartha, fixing Risheeth's folder at the user's explicit request).
  `baselines/run_all_baselines.py` was hardcoded to `pair_test_source.tif`, a file that has never
  existed on any machine — so it raised `FileNotFoundError` for everyone, including its author.
- **Gate 2's re-scope is now canonical** — in `docs/00_CANONICAL_FACTS.md` §11, not just a proposal.
- **Two false "Tier A" claims removed** from `docs/RISHEETH_BASELINE_GUIDE.md` and
  `docs/ROHAN_DATA_GUIDE.md`. Both described `pair_01` as Tier A with a 26° sun difference; it is
  two crops of ONE OHRC frame — same sensor, zero sun difference.
- **Samrudh** hardened `evaluation/logger.py` twice, unprompted, overnight.
- **Rishabh** moved his stray root-level notes into `app/` and started logging via `log_result()`.
- **Risheeth** fixed the AKAZE constructor himself — correctly, with a `hasattr` fallback covering
  both OpenCV 4 and 5. Better than what `main` had.

---

## 🔴 The finding that reshaped the plan

`data/pairs/pair_03_tierD/PROVENANCE.md` shows Tier D is **already** render-and-match: the LOLA DEM
rendered at the Kaguya image's own solar geometry. It scores 37.8 px and we have been calling that a
multi-modal limitation.

**It is not. It is an information-starvation bug in our own pipeline.** Both halves confirmed in code:

- `core/scale.py:101` — `target = float(max(ga, gb))`, i.e. resample to the **coarser** grid.
  The comment at `:84` says it "throws information away on purpose."
- `core/matcher.py:68-71` — LoFTR's coarse stage runs at 1/8, `STRIDE = 8`.

| Input | Coarse grid | Effective resolution | vs LOLA's real 60 m/px |
|---|---|---|---|
| 99 px (today) | 12×12 | **500 m/px** | 8× coarser than the data |
| 640 px (proposed) | 80×80 | **75 m/px** | **matches the data** |

Kaguya 640 px × 9.37 m/px = 5997 m; LOLA 101 px × 60 m/px = 6060 m — same ground, 6.4× scale ratio.
We downsample the optical image to 99 px, then match at 500 m/px when the elevation data carries
60 m/px. **We threw away 97.6% of the optical pixels and concluded multi-modal matching is hard.**

**This is "bet A" in the plan and it is the next session's first task.**

---

## Per person

| Who | Last push | Delivered | Blocked on |
|---|---|---|---|
| **Samartha** | 3 Sep 10:54 | UI, baselines fix, docs corrections, Gate 2 canonical | Nothing. Bet A next. |
| **Samrudh** | 3 Sep 09:39 | Logger guards ×2 overnight, `allow_failed`, swept-curve KeyError fix | Nothing. Owes the illumination-OFF sweep + fixing his test contamination. |
| **Rishabh** | 3 Sep 10:44 | Change detection logged, notes moved into `app/` | Nothing. Most consistent contributor — committed all 5 days. |
| **Risheeth** | 3 Sep 09:52 | AKAZE fix (his own, correct) | Nothing technically. **Owes understanding** — see Known issue 3. |
| **Rohan** | **2 Sep 20:21** | Catalogue, Tier D pair, honest negative recorded | 🔴 **Tier A decision overdue.** `cut` or `abandoned` — due end of Day 6. |
| **Saniya** | **NEVER** | Nothing. `presentation/` is a 0-byte `.gitkeep` | 🔴 See Known issue 1. |

---

## In flight — resume here

**Nothing is half-finished in the working tree.** The repo is clean and pushed.

**The next session starts with plan Part 1, bet A:**

1. Re-render the LOLA DEM at **9.37 m/px** (not its native 60) using `evaluation/shaded_relief.py`
   and `ops/build_tier_d_pair.py`. `PROVENANCE.md` records the exact crop lines
   (LOLA lines 9669:9770, samples 21214:21315; solar az 284.901°, el 16.98°).
2. Match the resulting 640×640 render against the 640×640 Kaguya optical image **without**
   downsampling.
3. **Log the result either way. Timebox: end of Day 6.** Success = Tier D `residual_px` materially
   below 37.8. Failure is still a win — it *measures* the resolution limit, which is a strong Q&A
   answer where we currently have silence.

**Fallback if bet A fails:** "bet B" — `core/reliability.py`, a per-cell
verified / weak / **no evidence** map. Reuses `core/distribution.py`'s existing binning. Do **not**
change `run_all()`'s signature — it is pinned by list equality at `core/test_interfaces.py:59`.

---

## Known issues — do not re-report these

1. 🔴 **`presentation/` is empty and its owner has never committed.** Highest-probability failure
   mode in the project. **But `docs/SANIYA_NARRATIVE_GUIDE.md` (25 KB) already contains ~70% of the
   deck as prose** — verified 6-slide structure, technical diagram as text, feasibility and
   licensing argument, impact bullets, and a timed 3-minute demo script for all six speakers. The
   gap is transcription plus one diagram, not authorship. **The plan sets a hard contingency: no
   committed `.pptx` by end of Day 6 → `presentation/` reassigns to Samartha.**
2. 🔴 **Test contamination — rows cleaned, ROOT CAUSE STILL LIVE.** Samrudh deleted all junk
   `method=test` rows late on Day 5 (the file is now clean at 43 rows). **But the bug that creates
   them is not fixed.** Verified by md5: hash the file, run `pytest -q`, hash again — it changes,
   and a fresh `test_pair_allowed / method=test` row appears. `evaluation/test_metrics.py` calls
   `log_result` **without** redirecting `RESULTS_LOG`, so the file re-contaminates on every single
   test run by anyone. Three such rows were reverted before commit during this session alone.
   The fix is one `monkeypatch.setattr(logger, "RESULTS_LOG", tmp_path / "x.csv")`; it is Samrudh's
   file, and every other test in the repo already redirects correctly.
   **Until it is fixed, check `git diff evaluation/results_log.csv` before every commit.**
3. **Risheeth's code is fixed; his understanding is not.** Of 5 blockers in `baselines/`, he fixed 1
   (AKAZE, well). Samartha fixed the other 4 at the user's explicit request. Gate 5 requires him to
   explain his own module cold — he needs to read the diff and be able to say *why* each change was
   necessary. **This is a Gate 5 risk, not a code risk.**
4. **AKAZE beats us on both real pairs.** `pair_01`: AKAZE `residual_px` 0.1215 vs ours 0.1945
   (1.6×). Tier D: AKAZE 10.95 vs ours 37.81 (3.5×). **Neither real pair has a sun difference** —
   `pair_01` is a same-frame crop and Tier D is optical↔elevation — so they test the one thing we do
   not claim an advantage on. Our claim needs the synthetic sweep. **This is Q&A killer #2 and the
   answer only works once the illumination-OFF sweep exists.**
5. **No illumination-OFF arm on the sun sweep.** Highest-value measurement still unmade. Until it
   exists we **cannot** say "illumination normalisation improves our sun-angle accuracy by N."
   It is a flag and a re-run. Assigned to Samrudh.
6. **The illumination A/B is near-circular.** `core/bench_illumination.py:56-64` builds the hard case
   as contrast inversion, and `gradient_orientation` is *designed* to be invariant to exactly that.
   Must be relabelled "intensity inversion, **not** sun angle" wherever it appears.
7. **Synthetic ground truth has no moving shadows.** `evaluation/shaded_relief.py` is a pure
   Lambertian hillshade with no occlusion term — shading rotates, shadows do not move. Its own
   docstring overclaims. **Disclose on the slide; being caught is worse.** Q&A killer #3.
8. **`redetect()` has zero callers** (`core/distribution.py:130`). We measure uniformity, we do not
   enforce it — so that novelty bullet in `SANIYA_NARRATIVE_GUIDE.md:131-142` is **false as
   written**. Wiring it trades accuracy for coverage (measured: coverage 0.797→0.891 while
   `rmse_gt_px` 0.41→0.72).
9. **No pyramid in `core/scale.py`.** The cross-scale novelty bullet is half-built. **The plan says
   soften the claim, not build it** — wrong week.
10. **The same Tier D pair is logged under two `pair_id`s** — `pair_03_tierD` (ours) vs `tier_d_01`
    (baselines). A judge grepping the CSV cannot tell they are the same pair.
11. **Two sets of `tier=synthetic` rows are not comparable.** Samrudh's 7 SIFT rows are at
    `gsd_mpp=10.0` with an **empty `config`**; the 20 `ours_loftr` rows are at 60.0 with full config.
    At 0° SIFT reads 0.00355 against our 0.11992 — which looks like "SIFT is 34× better" and is a
    different experiment entirely.
12. **Risheeth has 3 stale remote branches** — `risheeth-baseline-pipeline`,
    `risheeth-invariant-pipeline`, `risheeth-baselines-clean`. His work is merged to `main`; the
    branches should be deleted so nobody merges an old copy. **His earlier merge already reverted
    Samartha's doc fixes once** — a rebase happened to save them.

---

## Evidence file — `evaluation/results_log.csv`

**43 rows, 15 fields, `csv.DictReader`-clean. Junk rows removed by Samrudh on Day 5.**

| Rows | Tier | Method |
|---|---|---|
| 20 | synthetic | `ours_loftr` — the sun-azimuth sweep, 5 off-grid shifts × 4 angles |
| 14 | synthetic | SIFT (Samrudh) — ⚠️ check `config` is populated, see issue 11 |
| 4 | same-frame offset crop | `ours_loftr`, SIFT, ORB, AKAZE |
| 5 | D | `ours_loftr`, SIFT, ORB, AKAZE, `change_detection_absdiff` |

**The headline result — medians over 5 off-grid shifts:**

| Δazimuth | `rmse_gt_px` | `inlier_ratio` | `grid_coverage` | Gate 2 C1 (<0.5) |
|---|---|---|---|---|
| 0° | 0.11992 | 1.0000 | 1.0000 | PASS |
| **15°** | **0.32230** | **0.9757** | **1.0000** | **PASS** |
| 30° | 0.93134 | 0.7404 | 0.8281 | FAIL |
| 45° | 2.58557 | 0.3484 | 0.4062 | FAIL |

**Four criteria pass simultaneously at 15°.** Report the **median, never the minimum** — a single 30°
run returns anywhere from 0.71 to 1.65 on sub-pixel offset alone, and an *integer* shift returns a
flattering 0.41 because the warp does not interpolate.

---

## Open questions

1. 🔴 **What is our college's actual rubric, and its weights?** We are optimising against *inferred*
   weights from other institutions (Innovation ~25%, Relevance ~25%, Feasibility ~20%). **One
   message to the SPOC de-risks the whole allocation.** If Impact or Presentation outrank Novelty,
   the plan's effort split should shift. **Day 5 action, not yet done.**
2. **Saniya — engage or reassign?** Decision due end of Day 6.
3. **Rohan — Tier A `cut` or `abandoned`?** Overdue. Either answer is fine; an open question is not.

---

## Not doing — settled, do not re-litigate

- **No VM or cloud machine.** Checked this session: it appears nowhere in the repo, and it would
  break Gate 4, which requires the demo to run on Samartha's laptop with **wifi off**. This machine
  is sufficient and measured: LoFTR 640² in **5.50 s**, 1.84 GB peak, 14 threads,
  `torch 2.13.0+cpu`. The 640 px tile size was chosen *because* of this hardware.
- **No pyramid**, no cross-sensor chase (Tier A/B formally dropped in the Day-5 scope cut), no new
  matcher work, no further `core/` polish. 179 tests green and Gate 1 exact — `core/` is done.
