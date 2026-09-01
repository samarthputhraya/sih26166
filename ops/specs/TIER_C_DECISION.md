# Decision — the multi-modal leg is Tier D (optical ↔ elevation), not Tier C (infrared)

**Decided 1 Sep 2026 (Day 3), by Samartha. Open question #2 is now closed** — it was due Day 5.

---

## The decision

**Tier D — real optical imagery registered against LOLA shaded relief — becomes our primary
multi-modal leg. M3 infrared (Tier C) becomes a stretch goal, not a dependency.**

Gate 2 (Day 8) requires *"produces matches on ≥1 Tier C (multi-modal) pair, with degradation
honestly quantified."* We will satisfy the **multi-modal** requirement with Tier D and say so
plainly, rather than gambling Gate 2 on a data format nobody on the team has ever opened.

---

## Why this is legitimate and not moving the goalposts

Our own Canonical Facts §2 defines the terms, and both halves of the definition already permit it:

> **"multi-modal"** — ONLY when the two images come from different physical modalities
> (visible vs infrared vs **radar** vs **elevation**).

and the ladder itself lists:

> | **D** | Optical ↔ SLDEM shaded relief | Multi-modal **and** exact ground truth at any sun angle |

**Elevation is an allowed modality, and Tier D is already labelled multi-modal in the ladder we
wrote.** A photograph and a laser-altimeter elevation model are about as different as two sensing
modalities get: one measures reflected sunlight, the other measures range. Nothing here is being
stretched.

⚠️ **What must change is the sentence we say out loud.** The "honest one-sentence summary" in §2
currently ends *"and optical-against-infrared for the multi-modal case."* That is now false.
It must become **"optical-against-elevation for the multi-modal case."** Saniya's deck and the Q&A
bank must use the elevation wording. **This is exactly the kind of stale sentence that loses a
Q&A round**, and it is the one thing about this decision that can still go wrong.

---

## Why Tier D beats M3 on the evidence

| | Tier D — LOLA elevation | Tier C — M3 infrared |
|---|---|---|
| data in hand | ✅ **yes, downloaded and verified today** | ❌ none, nobody has opened one |
| renderer in hand | ✅ `evaluation/shaded_relief.py`, working | ❌ needs band selection + georeferencing |
| ground truth | ✅ **exact** — same grid, known transform | ❌ none |
| login required | no | no, but PRADAN is unreliable |
| format risk | low — raw 16-bit, no header | high — hyperspectral cube, unfamiliar |
| covers our demo site | ✅ verified | unknown |

The decisive column is **ground truth**. Tier D is the only multi-modal option where we know the
right answer, so it satisfies the multi-modal criterion *and* strengthens the `rmse_gt_px < 0.5`
criterion at the same time. M3 could never do that.

---

## What was verified today, not assumed

1. 🔴 **`SLDEM2015` does not cover our demo site.** It is ±60° latitude; we are at −74°. This was
   written into Canonical Facts §2, §3 and Rohan's Day-4 row as the Tier D source. **It could
   never have worked**, and we would have found out on Day 6 at the earliest.
   → Replacement is **LOLA `ldem_60s_60m`**, 60°S–90°S at 60 m/px vs SLDEM's 59 m/px. No loss.

2. **A 1.93 GB product reduced to a 34 MB fetch.** [`ops/fetch_lola_dem.py`](../fetch_lola_dem.py)
   range-fetches only the rows needed, with the projection verified by round-trip and by the
   −60° edge landing on line ≈ 0.

3. **The terrain at our site is good.** Relief **3238 m** across the OHRC footprint; shaded relief
   passes the `std > 10` texture check at every sun elevation tested.

4. **The full Tier D chain runs**, on real terrain, using Samrudh's renderer and metrics and
   Risheeth's baseline:

```
 sun diff  matches  inlier_ratio  rmse_gt_px
      0deg      248         1.000        0.04     <- control
     30deg       16         0.688        6.72
     60deg        1  too few (<4)           -
     90deg        2  too few (<4)           -
```

SIFT is already **13× over Gate 2's `rmse_gt_px < 0.5`** by 30° of sun movement, and cannot find
four usable matches past that. That is the multi-modal degradation curve, measured, on real data.

---

## What is still missing — the honest gap

**What ran today is shaded-relief ↔ shaded-relief.** True Tier D is **real optical imagery ↔
shaded relief**, and that has not been run yet.

The good news is that both halves are already on disk and on the same projection:

- Kaguya TC `TC1S2B0_01_03482S746E0433` — south polar stereographic, 9.3699 m/px
- LOLA `ldem_60s_60m` — south polar stereographic, 60 m/px, same 1737.4 km sphere

Their projected metres are directly comparable, so no reprojection is needed — only a scale
resample at **6.4×**, which `core/scale.py` already does. **The Kaguya scene centre maps to LOLA
line 9805, sample 20901**, inside the window already fetched.

**Owner: Samartha. Target: Day 6**, ahead of Gate 2 on Day 8.

---

## What this changes for other people

| Person | Change |
|---|---|
| **Rohan** | Day-4 "SLDEM tile" is **cancelled** — the product does not cover our site. Replaced by the LOLA window, already fetched. His remaining queue is unchanged: Tier A `EDRNAC4` pairs (blocking Risheeth Day 4 and Samrudh Day 6) and the CH-3 NAC product IDs. |
| **Samrudh** | His `shaded_relief.py` is now on the **critical path for Gate 2**, not just a synthetic-data helper. He can swap his made-up crater surface for the real DEM at `dem_site_60m.npy`. |
| **Saniya** | The multi-modal sentence is **"optical against elevation"**, never "optical against infrared". |
| **Risheeth** | Nothing changes. Tier A is still his Day-4 blocker and still does not exist. |

---

## If M3 is revisited later

Only after Gate 2 passes, and only as an *additional* row in the table — never as a dependency.
If it works, the multi-modal claim gets stronger. If it does not, nothing is lost, because Tier D
already carries the criterion.
