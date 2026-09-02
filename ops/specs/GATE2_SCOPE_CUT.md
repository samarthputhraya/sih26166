# Gate 2 — the Day 5 scope cut

**Written:** 2 Sep 2026, Day 5 · **Gate 2 is Day 8, three days out**
**Decision owner:** Samartha. This is a proposal with the evidence attached, not a done deal.

> Invariant 6: *"Gates cut scope, never extend time. A failed gate means dropping features,
> not adding days."* The value of that rule is claiming it **early**, while there is still
> runway to execute the smaller scope. Making this call on Day 8 buys nothing.

---

## 1. Where Gate 2 actually stands, on evidence that counts

Every number below is a row in `evaluation/results_log.csv` as of commit `29f2c43`.
29 rows, 15 fields, zero blank status cells. Nothing here is from scrollback.

**Synthetic, real LOLA site DEM (375×364 @ 60 m/px), 5 off-grid shifts per angle, medians:**

| Δazimuth | n | `rmse_gt_px` | `inlier_ratio` | `grid_coverage` | `distribution_cv` |
|---|---|---|---|---|---|
| **0°** | 5 | **0.11992** ✅ | **1.0000** ✅ | **1.0000** ✅ | **0.3662** ✅ |
| **15°** | 5 | **0.32230** ✅ | **0.9757** ✅ | **1.0000** ✅ | **0.4145** ✅ |
| 30° | 5 | 0.93134 ❌ | 0.7404 ✅ | 0.8281 ✅ | 0.9141 ✅ |
| 45° | 5 | 2.58557 ❌ | 0.3484 ❌ | 0.4062 ❌ | 1.8419 ❌ |

**Real pairs:**

| pair | tier | `residual_px` | `inlier_ratio` | `grid_coverage` | `distribution_cv` |
|---|---|---|---|---|---|
| `pair_01` | same-frame offset crop — **not a validation tier** | 0.19452 | 0.9996 | 1.0000 | 0.3630 |
| `pair_03_tierD` | D (optical ↔ elevation) | **37.81** = **2268.76 m** | 0.5263 | 0.1094 | 3.2435 |

### The headline

**At a 15° sun-azimuth difference, four of Gate 2's numeric criteria pass at once**, on a pair
with exact ground truth. That is a real result and it did not exist this morning.

**Two criteria cannot pass by Day 8 no matter what we write**, because they are data problems,
not code problems:

- **C2, ≥2× best classical on Tier A** — no Tier A pair has ever been cut. `pairs_catalogue.csv`
  row `tier_a_01` is `status=identified`, the source columns are bare product IDs, and
  `DATASET_CARD.md` records an honest negative after five cropping attempts.
- **C6, runs on ≥1 Tier B pair** — there is **no Tier B row in the catalogue at all**. Tier B is
  CH-2 OHRC ↔ LROC NAC. We have B+ (OHRC ↔ Kaguya), which is a different rung. No owner, no data,
  no plan. `STATUS.md` has flagged this as undecided since Day 4.

And one criterion is **structurally unreachable on the data we own**:

- **C4 on Tier D** — the reference is 101×101, so an 8×8 grid needs ≥52 occupied cells for 0.80.
  The pair yields **10 inliers**. The arithmetic ceiling is 10/64 = **0.156**. No algorithm change
  moves this; only a bigger reference image would.

---

## 2. The proposal

### Keep, unchanged — they are met

- **C1** `rmse_gt_px` < 0.5 on synthetic — **met**, 0.11992 @ 0°, 0.32230 @ 15°.
- **C7** matches on ≥1 multi-modal pair, degradation honestly quantified — **met**. 19 matches,
  10 inliers, and the degradation is now a number: **37.81 reference px = 2268.76 m on the
  ground**. It produces matches; it does **not** register. Say exactly that and nothing stronger.

### Re-base from "Tier A" onto synthetic — C2, C3, C4, C5

The substance of C2 is *"are we better than classical, and by how much?"* That question does not
require a Tier A pair. It requires **ground truth**, and as of today we have exact ground truth
on demand via `core/pipeline.py --synthetic`.

> **C2 (re-based):** ours vs SIFT / ORB / AKAZE on the **same synthetic pair at the same scale**,
> scored against exact `H_true`, across the sun-angle sweep. Claim the ratio at each angle.

This is a **stronger** claim than one Tier A pair would have given — it is a curve, not a point,
and it shows where we degrade. C3, C4 and C5 come along for free: all three already pass on
synthetic at ≤15° and at 30° (see the table).

### Drop, formally and in writing — C6

> **Drop Tier B.** No pair, no owner, no data path, three days out. Record it in
> `00_CANONICAL_FACTS.md` §11 with the reason, so nobody re-adds it and no slide implies it.

### What we must stop claiming

**We have no cross-sensor validation and will not have any by Day 8.** Under Invariant 2,
cross-sensor means *different instruments*. Every one of these is therefore off-limits until a
real Tier A or Tier B pair exists:

- ❌ "cross-sensor registration" — `pair_01` is one OHRC frame cropped twice
- ❌ any comparison to classical **on real lunar data** — the baselines have never run on one
- ❌ "sub-pixel" without naming the grid and the metres — say *"0.32 px on the 60 m/px synthetic
  reference ≈ 19 m"*, never a bare number

Struck claims must be removed from `docs/RISHEETH_BASELINE_GUIDE.md:234` and
`docs/ROHAN_DATA_GUIDE.md:227`, which both still label `pair_01` as *Tier A with a 26° sun
difference*. It is neither.

---

## 3. What Gate 2 becomes

> **Gate 2 (re-scoped, Day 8).** On the synthetic pair with exact ground truth, at a stated
> sun-azimuth difference ≤ 15°: `rmse_gt_px` < 0.5, `inlier_ratio` > 0.60,
> `grid_coverage_fraction` ≥ 0.80, `distribution_cv` < 1.0, **and** a measured ratio against the
> best of SIFT / ORB / AKAZE on the *same pair at the same scale*. Plus: produces matches on the
> real Tier D multi-modal pair with the degradation quantified in metres.
>
> **Tier A and Tier B are dropped**, and the deck says so rather than implying otherwise.

**On that definition we are at 5 of 6 today.** The only open item is the classical comparison,
which is one person for one afternoon (§4).

---

## 4. Who does what, by Day 8

| Who | What | Why it is the blocker |
|---|---|---|
| **Samrudh** | ours vs SIFT/ORB/AKAZE on the **same** synthetic pair, same scale, logged | The one open criterion. Spec in `SAMRUDH_DAY5_TO_8.md` |
| **Risheeth** | fix his branch per `RISHEETH_REVIEW.md`, ~30 min | His AKAZE baseline currently raises on the demo machine |
| **Rohan** | Tier A: cut a pair or declare it dead **by end of Day 6** | If it lands, C2 gets a real-data arm as a bonus. If not, the cut above stands |
| **Samartha** | this cut into `00_CANONICAL_FACTS.md` §11; strike the false Tier A labels in the two guides | Invariant 2 |
| **Saniya** | the deck has to reflect the re-scope | Five content slides, none exist |

---

## 5. The honest framing for the deck and the viva

This is not a retreat, and it should not be presented as one. The claim becomes:

> *"We validate against exact ground truth, across a swept sun angle, and we report the angle at
> which we stop meeting our own threshold. On the one real multi-modal pair we own, we report
> that the method finds matches and does not yet register — 2268 m of residual error — rather
> than quoting the match count alone."*

A judge who hears a team state where its method **fails**, with the number, trusts the numbers
where it succeeds. The alternative on offer — claiming cross-sensor performance we cannot
evidence — is the single likeliest way to lose a Q&A round.

**The one number that decides the gate is the sun-angle difference we choose.** At 15° we pass
four criteria; at 30° `rmse_gt_px` fails; at 45° everything fails. Choosing it silently would be
the dishonest move. Choose 15°, state it on the slide, and show the whole curve including the
part where it breaks.
