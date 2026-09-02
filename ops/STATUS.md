# STATUS — SIH26166

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewrite, never append.** This must be true as of right now.
>
> Last wrap: **2 Sep 2026, evening — end of Day 4.**

---

## Position

| | |
|---|---|
| **Day** | **4 of 12, COMPLETE.** Tomorrow is **Day 5 (3 Sep)** |
| **Next gate** | 🚪 **GATE 1 IS TOMORROW.** `python -m core.pipeline data/pairs/pair_01`, five metrics |
| **Gate 1 outlook** | ✅ **PASSES.** Verified three consecutive runs, exit 0, bit-identical output. One blocker found and fixed tonight — see below |
| **Gate 2 (Day 8)** | 🔴 **AT RISK. Zero of seven criteria met on evidence that counts.** Four days out |
| **Gates passed** | none yet |
| **Internal hackathon** | ⚠️ **DATE STILL UNKNOWN — chase the SPOC.** Open since Day 0 |
| **Repo** | `github.com/samarthputhraya/sih26166` · branch `main` |
| **venv** | `C:\Users\samar\venvs\sih26166` — outside OneDrive, deliberately |
| **Data root** | `C:\Users\samar\sih26166_data` — path in `data_path.txt` (gitignored) |

---

## Smoke test — exit codes observed this session, not inferred

| Command | Exit | Meaning |
|---|---|---|
| `pytest core/ -q` | **0** | **99 passed** ⬆ was 15 on Day 2 |
| `pytest evaluation/ -q` | **0** | 6 passed (Samrudh) |
| `pytest app/ -q` | **0** | 9 passed (Rishabh) |
| `pytest baselines/ -q` | **5** | 🔴 **no tests collected** (Risheeth — tests exist only on his unmerged branch) |
| `import core.pipeline` | **0** | chain imports clean |
| `python -m core.pipeline data/pairs/pair_01` | **0** | ✅ **Gate 1 command, all five metrics** |

Gate 1 output, reproduced three times bit-identically:
```
matches 5185 · inliers 5183 (100.0%) · residual_px 0.19452325191421008
inlier_ratio 0.9996 · grid_coverage 1.0 · distribution_cv 0.363 · rmse_gt_px n/a
```

---

## 🔴 A Gate-1 blocker found AND FIXED tonight — read this first

**The shared data root held the discredited synthetic fixture under the name `pair_01`.** Any
teammate who synced from the Drive and ran the Gate 1 command got **exit 0 and
`residual_px 87.09`** — a silent false pass, on gate day.

Verified by hash: the data-root files were **byte-identical** to `pair_00_dryrun`
(`d7010f6eb753e541` / `9ad5e7b423f338ee`, float32, ref with 15 distinct values, std 1.40).
The real pair is uint8, 248 levels, std 34.46.

**Fixed:** real `pair_01` copied into the data root; the fixture moved to
`pair_00_dryrun_DO_NOT_USE/` with a README explaining the trap. Re-ran the gate on the corrected
root: `residual_px 0.19452325191421008`. ✅

> ⚠️ **Still to do before the gate:** push the corrected `pair_01` to the Drive, and have **one
> teammate run the command and read their number aloud.** If they say 87, their sync is stale.

---

## Gate 2 (Day 8) — the honest position

**Zero of seven criteria are met on evidence that counts.** Not "behind" — not started, for most.

| Criterion | State |
|---|---|
| `rmse_gt_px` < 0.5 on synthetic | 🔴 **never computed by any code path.** `run_all` accepts `H_true`; `main()` never passes it. Nothing in the repo does |
| ≥2× best classical on Tier A | 🔴 **unmeasurable.** No Tier A pair exists; `baselines/` finds zero pairs and exits 0 |
| `inlier_ratio` > 0.60 | ⚠️ met **only on `pair_01`**, which its own PROVENANCE disqualifies as a validation tier |
| `grid_coverage_fraction` ≥ 0.80 | ⚠️ same. On Tier D it is 0.109 — and **structurally unreachable**: the 101×101 reference gives 12.6 px cells, so 0.80 needs ≥52 inliers from 19 matches |
| `distribution_cv` < 1.0 | ⚠️ same. Tier D is 3.24 |
| runs on ≥1 **Tier B** pair | 🔴 **no Tier B pair is even catalogued.** Tier B is OHRC↔LROC NAC; we have B+ (OHRC↔Kaguya), which is a different row |
| matches on ≥1 multi-modal pair | ✅ **the one that is met.** Tier D produces 19 matches, 10 inliers |

**All four catalogue rows are `status=identified`. None is `ready`.**

> ⚠️ **Correction to a claim I made on Day 4.** I called the Tier D result "Gate 2's multi-modal
> criterion, met". It **produces matches**, which is what the criterion literally says — but the
> matches are wrong. Ground truth is derivable from the two GeoTIFF affines (both are
> south-polar stereographic in the same CRS), and against it **`rmse_gt_px` ≈ 13 reference pixels
> ≈ 788 m on the ground.** It registers *something*, not the right thing. Quote it as
> "produces matches, does not yet register" and nothing stronger.

---

## Per person

| Person | Last push | Delivered | Blocked on |
|---|---|---|---|
| **Samartha** | 2 Sep 10:06 | Gate-1 chain · illumination + A/B · subpixel (measured, off by default) · distribution · 99 tests · Tier C→D decision · LOLA route | nothing |
| **Rohan** | 1 Sep 23:15 | `pairs_catalogue.csv` · **`build_tier_d_pair.py` — works, I ran it** · Canonical Facts 36×→40.8× fix | nothing. Needs to verify his own rows |
| **Samrudh** | 1 Sep 16:47 | `metrics.py` · `logger.py` · 6 tests | nothing |
| **Rishabh** | 1 Sep 22:10 | 3 bug fixes · 9 tests · Day-4 discriminator write-up | nothing |
| **Risheeth** | 31 Aug 11:45 **on `main`** — but **11 commits on `origin/risheeth-baseline-pipeline`**, last 1 Sep 22:58 | baselines + tests + a very good LoFTR benchmark, **none of it merged** | needs to rebase and land it |
| **Saniya** | ❌ **never — 5 days, zero commits on any branch** | nothing. `presentation/` is a `.gitkeep` | nothing. 🔴 Gate 5 risk |

---

## In flight — Samartha resumes here

`core/` is **complete as a module set**: all 8 modules CLAUDE.md lists exist, 99 tests pass.
Days 5, 6 and half of 8 are already done. **What remains is not new modules — it is wiring.**

**Three Gate-2 levers are built but not connected:**

1. 🔴 **`rmse_gt_px` has no code path.** `run_all(src, ref, H_true=None)` — `main()` never passes
   `H_true`, and nothing calls `synthetic_data.make_pair` from the pipeline. **This is Gate 2's
   first criterion and it has never once been produced outside a unit test.** Wire a
   `--synthetic` mode that generates a pair with known `H_true` and passes it through.
2. 🔴 **`core/distribution.py` is fully built, tested, and never imported by `pipeline.py`.**
   It is the only lever on `grid_coverage_fraction`, which Gate 2 needs at ≥0.80.
3. 🔴 **`log_result()` has zero callers.** `pipeline.py` never writes to `results_log.csv`.

**Also missing:**
- **`app/streamlit_app.py` does not exist.** No file matching `*streamlit*` anywhere. Gate 3
  (Day 10) needs a stranger to operate a UI unaided.
- **`scale.py` has no pyramid.** §6.5 locks "explicit image pyramid + resample-to-common-GSD";
  only the GSD half is written. Zero hits for "pyramid" in `core/`.
- **`crop_to_overlap` and `plan_overlap` are defined but never called.** `matcher.match` raises on
  two >640 px images and points at `crop_to_overlap` as the remedy — so the Tier B/B+ path has
  never been exercised.
- **`demo_cache/` is empty** in the repo and at the data root. Gate 4 (Day 11) needs cached inputs
  with wifi off. `weights/loftr_outdoor.pt` **is** present and verified (46,348,591 bytes).

⚠️ **`core/pipeline.py`'s docstring is stale** — design note 4 still says `illumination.py` does
not exist. It has existed since Day 2.

---

## Open questions

1. **Internal hackathon date** — unknown since Day 0. Chase the SPOC.
2. **Does Tier A survive?** The ODE route is open again (see Known issues #11). If it does not
   produce a pair by end of Day 6, **drop Tier A** rather than fake it — a failed gate cuts scope.
3. **Tier B (OHRC↔LROC NAC) has no owner and no row.** Gate 2 names it explicitly. Decide by Day 6
   whether we pursue it or formally drop it and say so.
4. **Saniya.** Five days, nothing, on any branch. This needs a conversation, not another spec.

---

## Known issues / traps

*Recorded so `daily-reviewer` does not re-report them. Entries 1–10 carried forward; 11–17 are new
on Days 3–4.*

**1. 🔴 LoFTR needs `[0,1]`. Raw DN returns ZERO matches, silently.** `io_loader` returns raw DN by
design; `matcher.py` divides by 255 once, internally. Keypoints are `(x, y)`, not `(row, col)`.

**1b. 🔴 `illumination.normalize()` must return `[0, 255]`, not `[0,1]`** — the matcher divides
downstream. Returning unit range gives zero matches with no error. Guarded by a test.

**2. 🔴 Big-endian silently corrupts OpenCV.** `io_loader.as_cv_safe()` normalises first. numpy
arithmetic does not preserve byte order — cast *after* arithmetic.

**3. `rasterio` is unusable — DECIDED: GDAL-free.** Blocked by Smart App Control. `imagecodecs`
absent so tifffile cannot decode LZW; `io_loader` falls back to Pillow for pixels, keeps tifffile
tags.

**4. LROC NAC EDR mislabels its own signedness.** Declares `LSB_INTEGER` at 8 bits for unsigned
data. `io_loader` corrects only when unambiguous.

**5. 🔴 Illumination geometry is not where you'd expect.** **CH-2 OHRC has none at all** — not in
the label, not in the geometry CSV (whose header is spelled `Lattitude`, two t's).
**Amended Day 3: Kaguya DOES have it** — `INCIDENCE_ANGLE` 86.548, `SOLAR_AZIMUTH_ANGLE` 284.911,
plus STAC `sun_elevation` 16.98.

**6. 🔴 Always look at the picture.** `M108587604RE.IMG` decodes perfectly and contains nothing
(std 1.42). ⚠️ **Amended Day 4: the `std > 10` rule is WRONG for raw NAC EDR**, which is companded
— good frames sit at std 4–6. Use **row-to-row correlation** instead (`ops/find_tier_a_pairs.py`).
A live test still asserts the old rule.

**7. Findings handed to Rishabh** — all three fixed on Day 3 ✅.

**8. Environment.** `cv2.AKAZE_create()` does not exist — it is `cv2.xfeatures2d.AKAZE_create()`.
Windows console is cp1252, so use `PYTHONIOENCODING=utf-8`. The repo is inside OneDrive, which
ignores `.gitignore`.

**9. Binaries already in history.** `data/lroc_analysis/ch2_ohr_preview.png` is **10.44 MB** —
double Invariant 5's ceiling, and that folder is ~98% of the repo's tracked payload. Permanent.

**10. A green suite says nothing about the case it does not cover.** `io_loader` had 23 passing
tests while a `KeyError` broke **every Chandrayaan-2 load** — none of them loaded a PDS4 product
lacking incidence. Fixed in `55c5cb7`.

**11. 🔴 NEW — ODE is NOT dead. My commit `2b4cad5` is wrong.** It records
`oderest.rsl.wustl.edu does not resolve` and abandons the documented Tier A route on that basis.
**Re-checked tonight: it resolves to 128.252.144.24 and the API answers.** A bounded query with
`ihid=LRO&iid=LROC&pt=EDRNAC4` over our site returns `Status: Success` and real NAC product IDs.
My earlier DNS failure was transient and I generalised from it. **The Tier A route is open**, and
it is a much better path than scraping the 203 MB PDS index.

**12. 🔴 NEW — `logger.py` corrupts `results_log.csv` on its very first call.** The file is 155
bytes with **no trailing newline**, and `log_result` only writes a header when size is 0. So the
first row concatenates onto the header: one 30-field line, and `csv.DictReader` parses **zero data
rows**. Reproduced on a copy tonight. **One newline fixes it — Samrudh's file, Samrudh's fix.**

**13. 🔴 NEW — `pair_01` is labelled Tier A with a 26° sun difference in two of our own guides.**
`docs/RISHEETH_BASELINE_GUIDE.md:234` and `docs/ROHAN_DATA_GUIDE.md:227`. It is two crops of ONE
frame — same sensor, same exposure, **zero** sun-angle difference. `pairs_catalogue.csv` and
`DATASET_CARD.md` have it right; the guides do not. This is exactly the Invariant-2 violation that
loses a Q&A round, and it is sitting in the guides teammates read.

**14. 🔴 NEW — the SLDEM correction never reached Canonical Facts.**
`docs/00_CANONICAL_FACTS.md:46` still names SLDEM as the Tier D source and `:102` still lists
SLDEM2015 with no warning, although SLDEM stops at ±60° and our site is at −74°.
`ROHAN_DATA_GUIDE.md:200` and `SAMRUDH_EVALUATION_GUIDE.md:50` still schedule the impossible task.

**15. ⚠️ NEW — the 180° sun-difference result is a trap number.** A 180° azimuth flip is a near-exact
contrast inversion (Pearson −0.9936), and `gradient_orientation` is *designed* to be invariant to
exactly that. It is not evidence of sun-angle invariance. Middle of the range is where it hurts.

> **UPDATED Day 5, and the old numbers here were unsourced.** This entry used to record
> `0° → 0.058, 15° → 0.355, 30° → 1.097, 45° → 2.295`. Those were never in `results_log.csv` and
> no committed script produced them — an Invariant 1 violation sitting in our own handoff.
> They are now **replaced by 20 logged rows** from
> `python -m core.pipeline --synthetic --dem <dem> --pixel-size 60 --sweep 0,15,30,45 --repeats 5 --log`
> on the real LOLA site DEM (375×364 @ 60 m/px), 5 off-grid shifts per angle:
>
> | Δazimuth | n | min | **median** | max | Gate 2 C1 (< 0.5 px) |
> |---|---|---|---|---|---|
> | 0° | 5 | 0.10457 | **0.11992** | 0.14126 | PASS |
> | 15° | 5 | 0.20491 | **0.32230** | 0.40369 | PASS |
> | 30° | 5 | 0.71244 | **0.93134** | 1.65310 | **FAIL** |
> | 45° | 5 | 1.74957 | **2.58557** | 4.72013 | **FAIL** |
>
> Same conclusion as before — **the 0.5 px threshold holds to ~15°, not beyond** — but now it is
> evidence. **Report the median, never the minimum.** A single run at 30° can return 0.71 or 1.65
> depending only on the sub-pixel offset chosen, and an *integer* shift returns a flattering 0.41
> because `warpPerspective` does not interpolate one — the truth then lands on the matcher's
> integer query grid and nothing sub-pixel is being measured at all.

**Choosing the sun difference chooses whether the gate passes — say which you chose.**

**16. ⚠️ NEW — `shaded_relief.py` cannot model a real incidence difference.** It is a pure
Lambertian hillshade with no cast-shadow / ray-occlusion term, so sweeping sun *elevation* changes
brightness but never moves a shadow. Azimuth sweeps are meaningful; elevation sweeps are not.

**17. ⚠️ NEW — the 13-vs-15 column collision is still live.** `evaluation/logger.py` declares 15
fields; `baselines/run_all_baselines.py` declares its own 13 and writes with its own `DictWriter`,
bypassing `log_result()` and **its one guard** (mandatory tier).
⚠️ **Corrected Day 5:** this entry used to say "both guards … (mandatory tier, failure status)".
`log_result` has only the tier check — a `status='ransac_failed'` dict is accepted and written
without complaint. The failure guard lives in `core/pipeline.py`, not in the logger.

**18. 🔴 NEW (Day 5) — `results_log.csv` now holds TWO sets of `tier=synthetic` rows that are NOT
comparable, sitting next to each other.** This is the likeliest way we quote a wrong number now.

| | rows | gsd_mpp | config column | DEM |
|---|---|---|---|---|
| `method=SIFT` (Samrudh) | 7 | **10.0** | **EMPTY** | not recorded |
| `method=ours_loftr` (Samartha) | 20 | **60.0** | full | `dem_site_60m.npy` (375×364) |

Different DEM, different ground scale, different geometry — **a 6× pixel-size difference alone
makes the two `rmse_gt_px` columns mean different things.** At Δazimuth 0° SIFT logs `0.00355`
and ours logs a median `0.11992`, which reads as "SIFT is 34× better than our method" and is not
a comparison at all. Gate 2 criterion 2 needs `ours` vs classical **on the same pair, same
scale** — we do not have that yet, on any tier.
**Two things needed:** Samrudh's rows need their `config` filled in (they are currently
unreproducible), and one of us must re-run the other's geometry before anything is compared.
Until then, never put those two numbers in the same sentence.

---

## Tonight's audit — how it was produced, and its limits

A 13-agent workflow audited six dimensions. **8 of the 13 agents died on network errors
(`ENOTFOUND`)** — including **every adversarial-verification agent** and both spec-drafting agents.

So the findings above are **single-source audit claims, not adversarially verified.** I personally
re-verified the four that drive action — the data-root fixture, the logger corruption, the ODE
route, and the `pair_01`-as-Tier-A mislabelling — and all four reproduced. **The rest are
unconfirmed and should be treated as leads, not facts.**

**Not produced tonight, and still owed:** Day 5–8 specs for **Samrudh** and **Saniya** (both agents
died). Risheeth, Rohan and Rishabh have theirs, written earlier today and left **uncommitted at the
user's request**: `ops/specs/{RISHEETH,ROHAN,RISHABH}_DAY5_TO_8.md`.
