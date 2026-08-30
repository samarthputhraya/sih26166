# SIH26166 — Team Task Guide (12 Days)

**Problem:** Register Chandrayaan-2 lunar images against reference imagery across different
sensors, sun angles and scales, to sub-pixel accuracy, with matches spread evenly across the frame.
**Goal:** Win the college internal round → advance to nationals.
**Team:** 6 people | Samartha: 5–6 hrs/day | Everyone else: ~2 hrs/day

> **Read `00_CANONICAL_FACTS.md` first.** It holds every definition, number and data source. This
> guide is the schedule; that one is the truth. If they disagree, that one wins.

---

## 🎯 WHO DOES WHAT

| Person | Role | One-Liner |
|--------|------|-----------|
| **Samartha** | **Matching Core & Integration** | Build the alignment engine, wire everything together, make the web UI |
| **Rohan** | **Data Lead** | Build the validation ladder — real pairs across four missions, fully documented |
| **Samrudh** | **Evaluation Lead** | Build the scorecard that proves how good the alignment is |
| **Risheeth** | **Baseline Lead** | Run classical methods, show exactly where they fail |
| **Rishabh** | **Application Lead** | Change detection — show what changed between two aligned images |
| **Saniya** | **Narrative Lead** | Deck, demo script, Q&A bank, rehearsals |

---

## ⚠️ FIVE THINGS THAT CHANGED FROM THE FIRST DRAFT

Read these before the schedule. They invalidate habits you may already have formed.

1. **We are not blocked on PRADAN.** Real Chandrayaan-2 OHRC imagery is publicly mirrored on
   archive.org with no account. Rohan has CH-2 data on Day 1.
2. **"Cross-sensor" has a strict meaning now.** LROC↔LROC is *not* cross-sensor. See the
   validation ladder in Canonical Facts §2. This wording appeared wrongly in five documents.
3. **There is no GPU on the demo machine.** All demo inference is CPU-only on Samartha's laptop.
   Tile size comes from a Day-1 measurement.
4. **No number goes anywhere until it is in `results_log.csv`.** The first draft contained
   fabricated results that four people were scheduled to rehearse.
5. **The plan is 12 days, not 15.** Days 13–15 are buffer, not scheduled work.

---

## 📅 DAY-BY-DAY (PRINT THIS)

**Nobody has an idle day.** In the first draft Rohan had nine consecutive blank days and then had
to answer for his module cold at Gate 5. People who stop working stop understanding.

### PHASE 0 · DAYS 1–2 — KILL THE RISKS

| Day | Samartha | Rohan | Samrudh | Risheeth | Rishabh | Saniya |
|-----|----------|-------|---------|----------|---------|--------|
| **1** | Repo + CPU env. **BENCHMARK LoFTR ON CPU** at 640²/1024² — report the number to the team. Load one real lunar image. | Download CH-2 OHRC ZIP from archive.org (no login). Attempt chmapbrowse registration with a **personal** email. Report both outcomes. | Install. Write `shaded_relief.py` stub. Download one SLDEM tile. | Install. Get SIFT/ORB/AKAZE running on a **self-made** pair (shift any image 5 px in numpy). Zero dependencies. | Install. Get `detect_changes` running on a **self-made** pair (copy an image, draw a circle). Zero dependencies. | **Download the official SIH 2026 template** (`sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx`, **924,505 bytes** — the 2025 filename differs by two characters). **Confirm the real headings — TITLE PAGE + five content slides — and post them in chat.** |
| **2** | Get LoFTR matching two real lunar tiles. Cache weights to `weights/`. Commit `io_loader.py` skeleton. | Download LROC NAC Tier A set: same site, incidence differs ≥15°. | Synthetic generator v1: SLDEM shaded relief at two sun angles + known homography. | Tune all three baselines on own pair. Log CSV. | Threshold + contour tuning on own pair. | Read the full PS text. Fill **Slide 1 (TITLE PAGE)** metadata, then draft **Slide 2 (IDEA TITLE)**. |

> **✅ DAY 2 CHECKPOINT** — Not a go/no-go on data any more, because data is no longer at risk.
> The checkpoint is: *does LoFTR run on a real lunar tile at an acceptable CPU latency?*
> If latency is unacceptable → reduce tile size, or fall back to classical + illumination
> normalisation now rather than on Day 8.

---

### PHASE 1 · DAYS 3–5 — WALKING SKELETON (UGLY BUT WORKS)

| Day | Samartha | Rohan | Samrudh | Risheeth | Rishabh | Saniya |
|-----|----------|-------|---------|----------|---------|--------|
| **3** | Wire `load → resample → match → RANSAC → warp`. Output a warped image. Nothing pretty. | Kaguya TC via AWS `--no-sign-request`. Tier B+ candidate. | `metrics.py` — all five metrics. | Run all 3 baselines on Samrudh's synthetic pairs. | Run change detection on Samrudh's synthetic aligned pairs. | **Slide 3 (TECHNICAL APPROACH).** |
| **4** | Integrate `evaluate()`. **Refactor `core/` to fixed interfaces today** — not Day 5. | SLDEM tile for the demo site. Start `DATASET_CARD.md`. | `test_metrics.py` — 3 tests. Held-out split logic. | Run baselines on Rohan's Tier A pairs. | Shadow-vs-real-change discriminator (shape + orientation). | **Slide 4 (FEASIBILITY AND VIABILITY).** |
| **5** | **GATE 1.** Then start `illumination.py`. | **Deliver catalogue v1** — Tier A + Tier B, `pairs_catalogue.csv` with tier column. | Plug into pipeline. First real numbers into `results_log.csv`. | Failure gallery v1 — 3 worst cases, annotated. | Area estimate in m² using GSD from the catalogue. | **Slide 5 (IMPACT AND BENEFITS)** — day 1 of 2. Our weakest scored area; it gets the day freed by the re-count. |

> **🚪 GATE 1 (End Day 5)** — `python -m core.pipeline data/pairs/pair_01` runs end to end on a
> real lunar pair, no manual steps, prints all five metrics.
> **If it fails:** drop LoFTR, ship classical + illumination normalisation + sub-pixel + uniformity.
> **Then Gate 2 is replaced by Gate 2-alt** (Canonical Facts §11) — otherwise you would be
> comparing classical against classical, which proves nothing.

---

### PHASE 2 · DAYS 6–8 — MAKE IT GOOD

| Day | Samartha | Rohan | Samrudh | Risheeth | Rishabh | Saniya |
|-----|----------|-------|---------|----------|---------|--------|
| **6** | Finish `illumination.py` (phase congruency vs gradient orientation, A/B). | Download M3 — **Tier C, the multi-modal leg**. Extract the observation-geometry band. | Results logging. Full run on Tier A. Swept-illumination curve started. | Failure gallery final, with annotations. | Run on Samartha's **real** aligned outputs (available since Gate 1). | **Slide 5 (IMPACT AND BENEFITS)** — day 2 of 2. Finish it. |
| **7** | `scale.py` — resample to common GSD + pyramid. Run Tier B and B+. | Hard pairs: incidence >70°, polar. | Run on Tier B. Verify numbers by hand on one pair. | Run baselines on Tier B. | Honest false-positive characterisation: "X found, Y plausible, Z are registration artifacts." | Slide 6 (RESEARCH AND REFERENCES). |
| **8** | `subpixel.py` + `distribution.py`. **GATE 2.** | `DATASET_CARD.md` complete — every file: URL, date, licence, product ID. | Full evaluation table, all tiers. Tier C degradation quantified. | Run on Tier C. Comparison table v1. | **Freeze change-detection module.** Fix the interface with Samartha. | Deck v1 complete, every number marked `[TBD]`. |

> **🚪 GATE 2 (End Day 8)** — `rmse_gt_px` < 0.5 synthetic · ≥2× best classical on Tier A ·
> `inlier_ratio` > 0.60 · `grid_coverage_fraction` ≥ 0.80 · `distribution_cv` < 1.0 · runs on ≥1
> Tier B pair · **produces matches on ≥1 Tier C multi-modal pair, degradation honestly quantified.**
> **STOP ALL ALGORITHM WORK AFTER THIS.**
> **If it fails:** freeze the algorithm anyway and move everything to UI and demo. A working
> honest demo beats a better algorithm nobody sees.

---

### PHASE 3 · DAYS 9–10 — PRODUCT LAYER (UX = JUDGE POINTS)

| Day | Samartha | Rohan | Samrudh | Risheeth | Rishabh | Saniya |
|-----|----------|-------|---------|----------|---------|--------|
| **9** | Build `streamlit_app.py`: upload 2 → Align → result + metrics panel. | Verify every `demo_cache/` file opens offline. Checksums. | Prepare UI-vs-harness comparison. | **Comparison table FINAL** (safe now — algorithm froze at Gate 2). | UI integration: Detect Changes button. | Demo script — **all six speak**, timed to 3:00. |
| **10** | Swipe + checkerboard + baseline side-by-side. **GATE 3.** | Write and rehearse his 60-sec data-provenance answer. Recruit the Gate 3 stranger. | **Verify UI numbers == harness numbers.** Debug mismatch with Samartha. | Baseline numbers into the UI panel. | Overlay polish: colours, legend, region table. | Q&A bank — 20 questions, each assigned to a named person. |

> **🚪 GATE 3 (Day 10)** — a stranger operates the UI and explains the output with nobody speaking.
> Day 10, **before** code freeze, so the remedy "fix the UX" is actually legal.
> Rohan recruits the stranger — a hostel-mate, not a team member, not a friend who has heard about it.

---

### PHASE 4 · DAYS 11–12 — FREEZE & REHEARSE

| Day | Samartha | Rohan | Samrudh | Risheeth | Rishabh | Saniya |
|-----|----------|-------|---------|----------|---------|--------|
| **11** | **CODE FREEZE.** Crash fixes only. Verify `weights/` + `demo_cache/` complete. **GATE 4.** | Rehearsal 1: his section + Q&A. | Rehearsal 1. Final numbers to Saniya. | Rehearsal 1. | Rehearsal 1. | **Rehearsals 1 & 2.** Record backup video after Rehearsal 2. |
| **12** | Final rehearsal. Sleep early. | Rehearsal 3. | Rehearsal 3. | Rehearsal 3. | Rehearsal 3. | **Rehearsal 3 + GATE 5.** Deck final in official template. Print copies. |

> **🚪 GATE 4 (Day 11)** — demo runs 3× consecutively on **Samartha's laptop, CPU only, wifi OFF**,
> cached weights and cached data, no crashes.
> **🚪 GATE 5 (Day 12)** — all six answer cold: *what problem · why hard · what does my module do ·
> how do we know it works · what next.*

### Days 13–15 — buffer, if you have them
Extra Tier C pairs · the full swept-illumination curve · a second illumination method · a fourth
rehearsal. **Never** add features. **Never** touch `core/` after Gate 2.

---

## 🧭 THE VALIDATION LADDER — MEMORISE THIS

Every person will be asked what data we used. There is one correct answer.

| Tier | Pair | Proves | Never call it |
|---|---|---|---|
| **A** | LROC NAC ↔ LROC NAC, incidence differs ≥15° | Sun-angle invariance | ~~cross-sensor~~ ~~multi-modal~~ |
| **B** | CH-2 OHRC ↔ LROC NAC | Cross-sensor, cross-mission | ~~multi-modal~~ |
| **B+** | CH-2 OHRC ↔ Kaguya TC | Cross-sensor at ~20× scale | ~~multi-modal~~ |
| **C** | Optical ↔ M3 / IIRS infrared | **Multi-modal** | — |
| **D** | Optical ↔ SLDEM shaded relief | Multi-modal + exact ground truth | — |

> Two LROC images are the **same sensor**. Different orbit changes viewpoint and lighting, not
> modality. Full rules in Canonical Facts §2.

---

## 🧱 SHARED CONVENTIONS

**Repo structure, naming, tooling:** Canonical Facts §13–§14. Do not invent your own.

**Communication**
- Daily 15-min standup, all 6, same time. **Show an artifact, not a status.**
- Blocked >30 min → post in chat. Not two hours. Thirty minutes.
- Git: work directly on `main`, one folder per person. `git pull` before, `git push` after.
  Big images live in Google Drive, not Git. Full setup: `01_HOW_WE_WORK_TOGETHER.md`.

**The no-wait rule**
> No teammate ever waits on Samartha. If you are blocked mid-task, **the spec was bad.** Say so;
> Samartha fixes the spec. This is a process failure, never your failure.

**The numbers rule**
> No number enters a slide, script or Q&A answer until it exists in `evaluation/results_log.csv`.
> Until then write `[TBD — results_log.csv]`.

---

## ⚠️ PITFALLS

| Pitfall | Prevention |
|---------|------------|
| Someone says "cross-sensor" about LROC↔LROC | Ladder table above. Saniya corrects it on the spot in every rehearsal. |
| A fabricated number reaches the deck | Numbers rule. Saniya greps the deck for bare decimals before Rehearsal 1. |
| Demo needs a GPU that isn't there | CPU benchmark Day 1. Tile size follows the measurement. Gate 4 is CPU-only. |
| Model weights download at demo time | `weights/` committed and verified at Gate 4. Wifi off during the test. |
| LoFTR fails on lunar imagery | Day 2 checkpoint, not Day 7. Fallback = classical + illumination normalisation → **Gate 2-alt**. |
| Only Samartha understands the code | Pairing sessions Days 4, 7, 10 with Samrudh and Rishabh. |
| Someone idle, then can't answer at Gate 5 | Nobody has a blank cell in the schedule above. |
| Scale invariance never actually addressed | `scale.py` is a Day-7 deliverable with a gate criterion, not an optional extra. |
| Multi-modal never actually addressed | Tier C is **in Gate 2**. Rohan downloads M3 on Day 6. |
| Scope creep (3D, DEM generation, onboard) | Refuse. Future Scope portion of the Impact slide only. |

---

## 🎯 WHAT SUCCESS LOOKS LIKE ON DEMO DAY

- Laptop opens, wifi off, UI loads in under 10 seconds
- Upload two real lunar images → Align → result appears within the latency we measured on Day 1
- Swipe and checkerboard views show the overlay; metrics panel shows all five numbers
- Detect Changes highlights regions with honest labelling of which are artifacts
- Baseline side-by-side shows classical vs ours, with numbers that are in the CSV
- **All six speak. All six answer cold.**
- Deck is the official template, six slides, every number traceable
- Backup video on a phone, tested

**That wins.** Not because the RMSE is impressive — because nothing in it is invented and every
person in the room can defend their own work.

---

## 📞 WHO OWNS WHAT WHEN IT BREAKS

| Symptom | Owner |
|---|---|
| Pipeline crash, integration, algorithm decision | Samartha |
| A file won't load / where did this data come from | Rohan |
| A metric looks wrong / is this number real | Samrudh |
| Baseline comparison, failure gallery | Risheeth |
| Change detection, overlay | Rishabh |
| Deck, script, template compliance, rehearsal | Saniya |
| **Someone is silent for 2 days** | **Saniya escalates to Samartha, Day 4 and Day 7 checkpoints** |

---

**Print this. Read Canonical Facts once properly. Execute gates ruthlessly.**
