# Day 4 status, and everyone's plan to Day 8

**Written 2 Sep 2026, morning of Day 4.** Read your own section. The whole-team picture is at the
top because two of the risks are not in anybody's individual section.

---

## Where the project actually is

**Gate 1 (Day 5) is already met, a day early.** `python -m core.pipeline data/pairs/pair_01` runs
end to end on real Chandrayaan-2 data and prints all five metrics, exit 0.

**Gate 2's hardest criterion may also be met.** Gate 2 needs *"matches on ≥1 Tier C (multi-modal)
pair, with degradation honestly quantified."* Rohan built a real Kaguya-optical ↔ LOLA-elevation
pair overnight, and I registered it this morning:

```
Kaguya TC 9.37 m/px  <->  LOLA shaded relief 60 m/px   (resampled to 60, ratio 6.40x)
  19 matches, 10 inliers, inlier_ratio 0.526
  residual_px 37.8   grid_coverage 0.109   distribution_cv 3.24
```

That is a genuine multi-modal registration — a photograph against an elevation model — and the
degradation against our easy pair (`residual_px` 0.19) is exactly the honest quantification the
gate asks for. **It is not a pass on the other thresholds and must never be quoted as one.**

### The two risks nobody owns

1. 🔴 **Saniya has never pushed. Four days, zero commits, `presentation/` is a `.gitkeep`.**
   Slides 3, 4 and 5 were due Days 3, 4 and 5. This is now the single largest schedule risk and a
   Gate 5 risk on top. Someone has to speak to her today.
2. 🔴 **Risheeth has not pushed since 31 Aug 11:45 — two days.** His two blocking bugs are still
   unfixed, so `baselines/` still cannot run on real data at all.

### Test state

| folder | tests | owner |
|---|---|---|
| `core/` | **99 passing** | Samartha |
| `app/` | 9 passing | Rishabh |
| `evaluation/` | 6 passing | Samrudh |
| `baselines/` | **0 — collects nothing** | Risheeth |

### 🔴 One thing I fixed this morning that everyone should know about

`core/io_loader.py` was crashing on **every Chandrayaan-2 product** — our primary data source.
A well-meant one-line change added `_pick(leaves, "solar_incidence")` as a fallback, but `_pick`
takes a *key* and `"solar_incidence"` is an alias *value*, so it raised `KeyError`. It sat behind
an `or`, so it only fired when incidence was **absent** — which is every CH-2 product, because
CH-2 carries no illumination geometry at all.

Reverted, with two regression tests. **The 23 existing io_loader tests all passed while this was
broken**, because none of them loads a PDS4 product that lacks incidence. That is the lesson, not
the typo: a green suite told us nothing about the case that mattered.

---

## Days completed, per person

Counted against your own row in `TEAM_TASK_GUIDE.md`, not against the calendar.

| Person | Days done | State |
|---|---|---|
| **Samartha** | **4 of 4**, plus Day-5, -7 and -8 core modules | ahead |
| **Rohan** | **5 of 4** — caught up and past | ahead, with one gap |
| **Rishabh** | **4 of 4** | on time |
| **Samrudh** | **4 of 4**, Day 5 half done | on time |
| **Risheeth** | **2 of 4** | ⚠️ two days behind, silent |
| **Saniya** | **0 of 4** | 🔴 nothing, ever |

---

# Samrudh — evaluation

**Quality: high.** `metrics.py` is the best-designed teammate module in the repo. `rmse_gt_px`
returns `None` rather than `0.0` without ground truth — you built the anti-fabrication guard
unprompted, and it is the reason Invariant 1 actually holds. `logger.py` making `tier` mandatory
and *raising* if it is missing is the same instinct. You also recovered cleanly from the empty-file
incident and fixed the residual test yourself.

**🔴 One live bug, and it is between you and Risheeth.** You added `status` and `notes` to the
schema, so `logger.py` writes **15 columns**. `baselines/run_all_baselines.py` still declares
**13**. When Risheeth runs his harness it will append 13-wide rows to a 15-wide file, and
`results_log.csv` — the single source of every number in the project — becomes misaligned.
**Fix: you own the schema, so tell Risheeth to import `FIELDS` from your `logger.py` instead of
declaring his own.** One import replaces his whole writer.

**⚠️ `results_log.csv` still has zero data rows on Day 4.** The writer exists; nothing has been
written. Invariant 1 means the deck cannot contain a single number until it does.

| Day | Task |
|---|---|
| **5** | **Plug `evaluate()` into the pipeline and log the first real rows.** Run `pair_01` and the Tier D pair (`data/pairs/pair_03_tierD/`) through `log_result()`. ⚠️ Tier `pair_01` as **`same-frame offset crop`**, never `A`. |
| **6** | The **swept-illumination curve** — your guide calls it "your best single figure". Sweep sun azimuth 0°→180° on `evaluation/shaded_relief.py`, ours vs SIFT, using real LOLA terrain (`ops/fetch_lola_dem.py`), not a made-up surface. |
| **7** | Run on Tier B+ when Rohan's crops exist. **Verify one pair entirely by hand** — recompute `residual_px` in a notebook and check it matches. |
| **8** | Full evaluation table, all tiers, Tier D degradation quantified. **Gate 2.** |

**Two things to fix while you are in there.** `evaluate()` returns `None` for both "<4 matches" and
"RANSAC failed" — the caller cannot tell them apart; return a dict with a reason. And
`synthetic_data.make_pair` still defaults `scale` to a random **1–20×**; at 19× there is almost no
overlap, so anyone who forgets to pass `scale=1.0` gets a broken pair and blames their matcher.

---

# Rohan — data

**Quality: much better than two days ago, and you have overtaken your own schedule.** The
catalogue has the right schema, `pair_01` is correctly tiered as `same-frame offset crop` rather
than A, the Kaguya sun angles are filled and the CH-2 ones are correctly blank. You corrected
§4's scale ratio in Canonical Facts from 36× to 40.8× *with the derivation shown* — that is
exactly the right way to change a shared document. And `build_tier_d_pair.py` **works**: I ran it
this morning and it produced a real 640 px Kaguya crop with its exact LOLA counterpart, rendered
at the scene's own measured sun angles. That is Day-6 work delivered on Day 3.

**🔴 The gap: you have not verified anything yourself.** Every row of the catalogue says
"handoff-sourced", "not locally present during audit", "no repository source evidence". That is
honest, and I would rather have it than a confident guess — but it means **at Gate 5 you still
cannot answer for your own file.** Gate 5 is all six of us explaining our module cold.

**⚠️ Also:** `overlap_lat` and `overlap_lon` are swapped. I measured 0.598° **longitude** ×
0.591° **latitude**; your row has them the other way round. Small, but it is the kind of thing a
judge spots.

| Day | Task |
|---|---|
| **5** | 🔴 **Get the data on your machine and re-derive two numbers.** Copy `SIH26166_DATA/raw/` from the Drive. Run `load()` on the Kaguya scene and confirm `9.3698731836556` and 51.82% NoData yourself. Then run `python ops/build_tier_d_pair.py <kaguya.tif> data/pairs/pair_03_tierD`. Replace "handoff-sourced" in those rows with what you measured. Fix the lat/lon swap. |
| **6** | **Tier A crops — the last real data gap.** Your candidates are good; the crops cannot be cut from raw EDRs because four footprint corners cannot model a 52,224-line pushbroom strip. The route is **map-projected products** from `LRO-L-LROC-5-RDR-V1.0` (reachable, HTTP 200). If two hours does not crack it, say so and we drop Tier A rather than fake it. |
| **7** | Hard pairs: incidence > 70°, polar. You already have one — Kaguya at incidence 86.5° is a 3.5°-above-horizon grazing sun. |
| **8** | `DATASET_CARD.md` complete: every file with URL, date, licence, product ID. |

**Do not start M3.** Tier C infrared is a stretch goal now; Tier D carries the multi-modal claim.

---

# Rishabh — change detection

**Quality: good, and your Day-4 write-up is the most intellectually honest document any of us has
produced.** You tried two discriminators, neither worked, and you wrote that down instead of
quietly promoting one. That is exactly right and it is worth more than a fake success.

**But Experiment 2 was mis-designed, so its conclusion is not supported.** You compared **global
mean intensity**: A 102.73 vs B 102.67, ratio 0.9994. Shaded relief conserves total brightness
almost exactly — moving the sun moves light from one side of a crater to the other without
changing the average. So that ratio was always going to be ~1.0 whatever happened. It does not
show "no useful separation"; it shows the global mean is the wrong statistic. **The ratio idea
needs testing per-pixel, on the ratio image `A / (B + 1)`, not on two scalars.**

**⚠️ And you edited `core/io_loader.py`.** The alias you added was right and I kept it. The call
site you changed crashed every CH-2 load — details at the top of this document. No harm done and
it is a genuinely subtle trap, but `core/` is mine: **send me the finding and I will make the
change**, so we do not both edit the same file.

| Day | Task |
|---|---|
| **5** | **Areas in real metres.** Take `gsd_mpp` from Rohan's `data/pairs_catalogue.csv` rather than typing a number. Add the known-circle test: radius 18 px at 9.3699 m/px ≈ 89,400 m². Sanity-check one by hand. |
| **6** | **Re-run Experiment 2 properly** — per-pixel ratio image, not global means. Then run the detector on the **real** Tier D pair at `data/pairs/pair_03_tierD/`, which is genuine lunar imagery. |
| **7** | The honest characterisation: *"X found, Y plausible, Z are registration artifacts."* This is your headline deliverable and the sentence Saniya needs. |
| **8** | **Freeze.** Agree the `detect_changes` signature with me and stop changing it. |

---

# Risheeth — baselines ⚠️

**Quality of what exists: the best-written teammate code in the repo.** All three baselines recover
the known shift exactly, you caught the OpenCV 5 AKAZE trap unprompted, and your CSV columns
matched Samrudh's guide character for character.

**But you have not pushed in two days, and `baselines/` still cannot run on real data.** Both
blocking bugs from your spec are unfixed. That makes you the critical path for Gate 2's
*"≥2× better than best classical baseline"* criterion — which cannot be measured at all until your
harness runs.

**Start here, today, in this order (~45 min):**

1. 🔴 **Pair discovery looks in the wrong place.** You expect `data/pairs/pair_01_source.tif`; the
   real path is `data/pairs/pair_01/pair_01_source.tif` — every pair is in its own folder. Your
   harness finds zero pairs and exits **successfully**, which is why you never saw it. Fix
   `_load_pair` and the discovery glob (`*/*_source.tif`), in **both**
   `run_all_baselines.py` and `draw_failure_gallery.py`.
2. 🔴 **Config 2 crashes.** `illumination.normalize()` returns float32; SIFT/ORB/AKAZE need uint8.
   Wrap with `np.clip(..., 0, 255).astype(np.uint8)`. Config 2 is the illumination-normalised half
   of your comparison — the entire point — and it has never once executed.
3. 🔴 **Delete your `CSV_FIELDS` and import Samrudh's instead:** `from evaluation.logger import
   FIELDS, log_result`. His schema now has 15 columns and yours has 13; as written you would
   corrupt `results_log.csv`, which is where every number in the project comes from.
4. **Add the 6 tests** from your spec — they are your existing `__main__` checks, moved.
5. ⚠️ Once discovery is fixed it will also find `pair_00_dryrun`. **Skip it** — it is a known-fake
   fixture that reports flatteringly good numbers.

| Day | Task |
|---|---|
| **5** | The four fixes above, then baselines running on `pair_01` and logging real rows |
| **6** | Failure gallery v1 — three worst cases, plain-English captions |
| **7** | Run on Tier B+/Tier D; gallery final |
| **8** | Comparison table v1 — every method, every tier. **Gate 2.** |

---

# Saniya — narrative 🔴

**Nothing has been delivered, on any day, and there is no `presentation/` content at all.**
Slides 3, 4 and 5 are overdue. The deck is a scored deliverable and the whole team's numbers are
now arriving, so the blocker is no longer "there is nothing to write about".

| Day | Task |
|---|---|
| **5** | Slide 1 (TITLE PAGE) + Slide 2 (IDEA TITLE), and confirm the six headings in chat |
| **6** | Slide 3 (TECHNICAL APPROACH) |
| **7** | Slide 4 (FEASIBILITY) + Slide 5 (IMPACT) |
| **8** | Deck v1 complete, **every number written as `[TBD — results_log.csv]`** |

⚠️ **The template is TITLE PAGE · IDEA TITLE · TECHNICAL APPROACH · FEASIBILITY AND VIABILITY ·
IMPACT AND BENEFITS · RESEARCH AND REFERENCES.** There is no "Problem Statement" slide and no
"Proposed Solution" slide — "Proposed Solution" is the first bullet *prompt* inside IDEA TITLE.
Six slides **including** the title page, so five content slides.

⚠️ **Not one number goes in until it is in `evaluation/results_log.csv`.** Write `[TBD]` and we
fill them the night before. An earlier draft of this project carried an invented "0.7 px" through
four documents as though it had been measured.

---

# Samartha — me

Done: Gate-1 chain, `illumination.py` + A/B, `subpixel.py` (measured, and **off by default** —
it makes LoFTR worse), `distribution.py`, 99 tests, the Tier C→D decision, the LOLA route after
finding SLDEM cannot reach our site, and the `inlier_ratio` fix that had us passing Gate 2's
threshold automatically.

> ⚠️ **Superseded on 3 Sep 2026 (Day 5):** sub-pixel refinement ships **ON**, not off. The
> "makes LoFTR worse" measurement above is *per-match endpoint error*; the transform-level
> `rmse_gt_px` that Gate 2 is judged on improves at every sun difference, and every Gate 2
> number was measured with refinement ON. See `core/pipeline.py::_refine_subpixel`. This
> paragraph is kept as a dated record of what was believed on Day 4.

| Day | Task |
|---|---|
| **5** | **Gate 1 formally.** Then `app/streamlit_app.py` — Gate 3 is Day 10 and nothing exists yet. |
| **6** | Help Rohan with Tier A map-projected products; wire `log_result()` into the pipeline |
| **7** | `scale.py` pyramid; run Tier B+ and Tier D end to end |
| **8** | **Gate 2.** Freeze the algorithm. |

---

## Rules that have not changed

- **One folder per person.** `core/` + `app/streamlit_app.py` Samartha · `evaluation/` Samrudh ·
  `baselines/` Risheeth · `app/change_detection.py` Rishabh · `presentation/` Saniya ·
  `data/*.csv|*.md` Rohan. Found something in someone else's folder? Tell them.
- **No number reaches a slide until it is in `results_log.csv`.**
- **Name the pair type with every number.** "Same-frame offset crop" and "Tier D multi-modal" are
  different worlds and mixing them up is how we lose a Q&A round.
- **Nothing over ~5 MB in git**, and nothing at the repo root. I moved two more files out this
  morning.
- **If a task runs 30 minutes over, say so in chat.** A wrong spec is my bug, not yours.
