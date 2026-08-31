# 00 — CANONICAL FACTS (Read First, Everyone)

**This file is the single source of truth.** Every other guide references it. If another
document contradicts this one, this one wins and the other one is a bug — report it in chat.

**Why this file exists:** in the first draft of these guides, the same claim was written five
different ways across six files. One of those ways was factually wrong and would have been said
out loud to an ISRO judge. Definitions live here now, once.

---

## 1. THE PROBLEM STATEMENT — WHAT IT ACTUALLY DEMANDS

**SIH26166** — *Multi-modal, Sun angle and scale invariant image correspondence using
Chandrayaan-2 optical images (OHRC, TMC and IIRS)* — ISRO, Space Technology, Software.

The PS names six things. We must be able to point at evidence for each:

| # | PS demands | Our evidence |
|---|---|---|
| 1 | **Multi-modal** (genuinely different sensor modality) | Tier C pairs — optical ↔ infrared |
| 2 | **Sun-angle invariant** | Tier A + Tier D swept-illumination curve |
| 3 | **Scale invariant** | Tier B+ pairs at ≥20× GSD ratio |
| 4 | **Sub-pixel accuracy** | `rmse_gt_px` on synthetic with true ground truth |
| 5 | **Uniform distribution across the image** | `grid_coverage_fraction` + `distribution_cv` |
| 6 | **A stated evaluation metric** | All five metrics, logged to CSV every run |

Note the exact wording of the Expected Solution: *"correspondence between Chandrayaan-2 acquired
optical images and **Lunar reference images**"*. Only the **source** must be Chandrayaan-2. The
reference is deliberately unnamed — LRO/LROC is a legitimate reference. The word **"Generic"** in
that same sentence is why we build a sensor-agnostic engine, not a CH-2-only one.

---

## 2. TERMINOLOGY — THE VALIDATION LADDER

**This is the most important section in the document set.** Using these words loosely is how we
lose the room in Q&A.

| Tier | Pair | What it legitimately proves | Data source |
|---|---|---|---|
| **A** | LROC NAC ↔ LROC NAC, same site, incidence differs ≥15° | **Sun-angle invariance.** Same sensor. | LROC PDS / QuickMap |
| **B** | CH-2 OHRC ↔ LROC NAC | **Cross-sensor, cross-mission**, ~2× scale. Both panchromatic. | archive.org / chmapbrowse |
| **B+** | CH-2 OHRC ↔ Kaguya TC | **Cross-sensor at ~20× scale ratio** | archive.org + AWS |
| **C** | Optical ↔ M3 (or CH-2 IIRS) infrared band | **MULTI-MODAL.** Visible ↔ infrared. | PDS Imaging / PRADAN |
| **D** | Optical ↔ SLDEM shaded relief | Multi-modal **and** exact ground truth at any sun angle | PDS Geosciences |

### Hard terminology rules — no exceptions

- **"cross-sensor"** — ONLY when the two images come from **different instruments**.
- **"multi-modal"** — ONLY when the two images come from **different physical modalities**
  (visible vs infrared vs radar vs elevation). Two panchromatic cameras are NOT multi-modal.
- **"cross-illumination"** — same sensor, different sun angle. This is Tier A.
- **NEVER** describe Tier A as cross-sensor or multi-modal.

> ❌ **BANNED SENTENCE** — this was in the first draft and is false:
> *"LROC-LROC different orbits — this IS valid cross-sensor (different orbits = different geometry)."*
>
> Two LROC NAC images are the **same sensor**. Different orbit changes viewpoint and illumination,
> not modality. Saying otherwise to an ISRO judge ends the conversation. Tier A is a
> **sun-angle** experiment. Call it that and it is a good experiment.

### The honest one-sentence summary we all use

> "We validate on a ladder: same-sensor cross-illumination for sun angle, Chandrayaan-2 against
> LROC and Kaguya for cross-sensor and 20× scale, and optical-against-infrared for the
> multi-modal case."

---

## 3. DATA — ALL VERIFIED PUBLIC, NO INSTITUTIONAL EMAIL REQUIRED

**The PRADAN block from the first draft was based on an unverified assumption.** Nothing on the
PRADAN login page, the FAQ, or chmapbrowse states any email-domain, organisation, or nationality
restriction. And regardless — **real Chandrayaan-2 OHRC imagery is publicly mirrored with no
account at all.**

| Dataset | Where | Login? | Format |
|---|---|---|---|
| **CH-2 OHRC imagery + all instrument user guides** | `archive.org/details/chandrayaan-2-high-resolution-images-of-the-moon` | **No account** | PDS4 `.img` + `.xml`, in ~750 MB ZIPs |
| CH-2 OHRC / TMC-2 / IIRS (full archive) | `chmapbrowse.issdc.gov.in` — ISRO's own recommended route | Registration | PDS4 |
| CH-2 (alternate portal) | `pradan.issdc.gov.in/ch2/` | Registration (Keycloak SSO) | PDS4 |
| LROC NAC / WAC | `pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/` — open directory | **No** | PDS3 |
| LROC map-projected NAC | ODE, dataset `LRO-L-LROC-5-RDR-V1.0`, product type **`SDPPHO`** | **No** | PDS3, georeferenced |
| **LROC NAC + illumination geometry** | **ODE REST API, product type `EDRNAC4` or `CDRNAC4`** — returns `Incidence_angle` per product | **No** | PDS3 + JSON metadata |

> ⚠️ **`SDRPHO` does not exist — the code is `SDPPHO`** (P, not R). An earlier version of this table
> had the typo and it propagated into `DATASET_CARD.md`. Verified 31 Aug 2026 against ODE's own
> `query=iipy` product-type listing.
>
> **For Tier A, do not use `SDPPHO`.** ODE reports `ValidIncidenceAngles = F` for it, but **`T` for
> `EDRNAC4` and `CDRNAC4`** — so ordinary NAC EDRs come back from the ODE REST API *with their
> incidence angle attached*, which is exactly what "same site, incidence differs ≥15°" needs. A NAC
> EDR **label** carries no illumination geometry (verified on a real product); ODE's metadata does.
> Query shape:
> `oderest.rsl.wustl.edu/live2/?target=moon&query=product&results=fmp&output=JSON&pt=EDRNAC4&iid=LROC&ihid=LRO&minlat=..&maxlat=..&westlon=..&eastlon=..`
> Only use incidence **20–80°**; above 90° is the night side.
| Search front-end | `ode.rsl.wustl.edu/moon` — "You are an anonymous user" | **No** | — |
| Browse UI | `quickmap.lroc.im-ldi.com` | **No** | — |
| **Kaguya TC** | `s3://astrogeo-ard/moon/kaguya/terrain_camera/monoscopic/uncontrolled/` | **No AWS account** | **Cloud-Optimized GeoTIFF, CC0 1.0** |
| **Chandrayaan-1 M3** (IIRS analogue) | `pds-imaging.jpl.nasa.gov` | **No** | PDS3; L1B = label + radiance + 3-band LOC + **10-band observation geometry** |
| **SLDEM2015** DEM | `pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/sldem2015/` | **No** | 512 ppd ≈ 59 m/px, ±60° lat, IMG + JP2 |
| Pre-rendered shaded relief | USGS Astropedia, "LOLA–Kaguya TC Shaded Relief Merge 60N60S 59m" | **No** | — |

### Two things worth knowing

**Kaguya TC is the cheapest win in the set.** CC0 licence, Cloud-Optimized GeoTIFF —
`rasterio.open()` reads it directly over HTTP with no download and zero licence risk.

**M3's 10-band observation-geometry file carries per-pixel illumination geometry.** That is real
measured sun angle data, not simulated. Use it.

### ISRO's own instructions to SIH students

From a prior ISRO SIH problem statement (SIH1732, hosted on VEDAS/SAC):

> *"Chandrayaan-2 OHRC images can be downloaded from https://chmapbrowse.issdc.gov.in — a. Change
> Projection into South Pole. b. Under Instrument footprint, select footprints will be displayed
> over the pole mosaic image. c. User can click on any of the footprint in the map view, details
> will be displayed in the left panel. d. User can select desirable PDS product, which can be
> downloaded and used. Image is stored in ".IMG" format, which is a PDS-4 standard. User can use
> PDS-4 data reader package for python to read the datasets."*

That names the portal, the projection, and the library (`pds4_tools`). Follow it.

### Ames Stereo Pipeline has an official CH-2 tutorial

`stereopipeline.readthedocs.io/en/latest/examples/chandrayaan2.html` — working ingestion commands
and real product IDs, e.g. `ch2_ohr_nrp_20200827T0030107497_d_img_d18`. It warns:
**"Keep the original ISRO filenames; a rename can break isisimport."** Applies to us too — never
rename a downloaded product.

---

## 4. INSTRUMENT FACTS — USE THESE NUMBERS, NOT OTHERS

| Instrument | Resolution | Band | Notes |
|---|---|---|---|
| CH-2 **OHRC** | **~28 cm/px** (ISRO's own portal figure; literature says 20–30 cm) | Panchromatic | Sharpest operational lunar orbital camera |
| CH-2 **TMC-2** | ~5 m/px | Panchromatic | Raw, calibrated, DTM, ortho, grid products |
| CH-2 **IIRS** | ~80 m/px | **0.8–5.0 µm infrared** | The multi-modal leg |
| CH-2 **DFSAR** | 2–75 m | Radar | Not used by us |
| LROC **NAC** | ~0.5 m/px | Panchromatic | |
| LROC **WAC** | ~100 m/px | Panchromatic/colour | |
| Kaguya **TC** | ~10 m/px | Panchromatic | CC0 |
| CH-1 **M3** | ~140 m/px (global) | **0.43–3.0 µm hyperspectral** | IIRS analogue, NASA instrument on an Indian mission |

**Do not say "0.25 m" for OHRC.** ISRO's own portal says 28 cm. If asked, say
*"about 25–30 centimetres; ISRO quotes 28."*

**Scale ratios that matter:** OHRC↔TMC ≈ 18×. OHRC↔Kaguya TC ≈ 36×. OHRC↔IIRS ≈ 285×.
This is why a naive matcher fails and why we need a pyramid — see §6.

⚠️ **UNVERIFIED — do not repeat as fact:** the "Level 1" difficulty label. It does not appear in
the SIH 2026 problem-statement listing. Never describe this PS as "Level 1" to a judge.

---

## 5. COMPUTE — READ THIS BEFORE DESIGNING ANYTHING

**The demo machine is Samartha's laptop. It has no discrete GPU.**

| | Samartha (demo machine) | Rohan (data server) |
|---|---|---|
| CPU | Intel Core Ultra 5 125H, 14C/18T | i7-14700K, 20C/28T |
| GPU | **Intel Arc iGPU, 0 MB dedicated VRAM** | RX 9060 XT 16 GB (**AMD, not CUDA**) |
| RAM | 15.4 GB (shared with iGPU) | 32 GB DDR5-6000 |
| Storage | 785 GB free | 1 TB SSD + 2 TB HDD |
| Location | In the room on demo day | ~30 km away |

### Consequences — these are not negotiable

1. **All demo inference is CPU-only.** The GPU is 30 km away and can never be in the demo path.
2. **Tile size is set by measurement, not by preference.** Samartha benchmarks LoFTR on CPU at
   640² and 1024² on **Day 1, hour 1**. Every downstream decision waits on that number.
3. **Model weights must be pre-cached** in `weights/` and committed to the demo machine. They
   download from the internet on first use. Wifi is off at Gate 4.
4. **Kaggle is the experiment surface** — real CUDA, T4/P100 16 GB, guaranteed 30 hrs/week, free.
   Code developed there runs unchanged locally (see below).
5. **Rohan's PC is a data server first.** 20 cores, 32 GB, 3 TB — right place for bulk download,
   tiling and DEM rendering. Keep the data there; pull back metrics and crops, never full images.
6. **ROCm on Rohan's PC is optional and timeboxed to 2 hours.** RX 9060 XT is gfx1200 and IS in
   AMD's Windows support matrix (ROCm 7.2.1, PyTorch 2.9, **Python 3.12 exactly**, Adrenalin
   26.2.2). But `torch-directml` is dead — never use it. If it doesn't work in 2 hours, stop;
   Kaggle already covers us.

> **Useful fact:** ROCm maps `torch.cuda.*` onto HIP transparently. You still write `.to('cuda')`.
> There is no second code path between Kaggle, Rohan's card, and CPU — just a device string.

### Turn this into a pitch, not an apology

> "The whole pipeline runs on a standard laptop with no discrete GPU. That matters for
> deployment — you don't need a GPU cluster to register lunar imagery."

That scores on feasibility and impact. Say it deliberately.

---

## 6. LOCKED TECHNICAL DECISIONS

1. **Matcher: LoFTR.** Dense, no detector, strong on low-texture maria, and **Apache-2.0
   licensed** (verified from the LICENSE file). Available via `kornia`.
2. **Do NOT use SuperPoint.** LightGlue's own README states that using SuperPoint as the detector
   implies *"ACADEMIC OR NON-PROFIT ORGANIZATION NONCOMMERCIAL RESEARCH USE ONLY."* If we want a
   sparse alternative, use **ALIKED or DISK + LightGlue** — both permissive.
   - This is a *good* Q&A answer, not a weakness. See §8.
3. **RANSAC: `cv2.USAC_MAGSAC`** — built into OpenCV, nothing to install.
   ⚠️ `pip install magsac` **DOES NOT EXIST** — verified, no such package. The first draft said it
   did. If you need a standalone binding it is `pymagsac`, but OpenCV's is fine.
4. **Illumination: phase congruency OR sign-invariant gradient orientation.** A/B test both.
5. **Scale: explicit image pyramid + resample-to-common-GSD.** LoFTR is not reliably invariant
   past ~4–8× on its own; our real ratios are 18–285×. **Resample both images to a common ground
   sample distance before matching.** This is a required step, not an optimisation.
6. **Sub-pixel: NCC on an 11×11 patch per match + quadratic peak fit.**
7. **Uniform distribution: 8×8 grid, min 2 matches/cell, re-detect in empty cells.**
8. **UI: Streamlit.** A notebook on screen reads as unfinished.

---

## 7. METRICS — EXACT DEFINITIONS

All five are returned by `evaluation/metrics.py :: evaluate()`. **Every number in the deck, the
demo and the Q&A bank must come from `evaluation/results_log.csv`.**

| Metric | Definition | Applies to |
|---|---|---|
| `rmse_gt_px` | RMSE against the **known ground-truth transform**, measured on a dense grid of check points, in **reference-image pixels**. | Synthetic + Tier D only |
| `residual_px` | RMSE of **held-out** matches (20% withheld from the fit). | Real pairs |
| `inlier_count` | Matches within the RANSAC threshold | All |
| `inlier_ratio` | `inlier_count / total_matches` | All |
| `grid_coverage_fraction` | Fraction of the 8×8 = 64 cells containing ≥1 inlier | All |
| `distribution_cv` | Coefficient of variation of inliers-per-cell. **Lower = more uniform.** | All |

### The two accuracy numbers are NOT the same thing — this matters

- `rmse_gt_px` is **accuracy**. We know the true answer.
- `residual_px` is **fit residual**. On a real pair we have no ground truth.

> ⚠️ **The first draft had a methodological bug**: it fitted a transform *from* the matches and
> then measured the error *of those same matches*. That is circular — it measures how well the
> model fits the points it was fitted to, not how accurate the registration is. Always hold out
> 20%. Never report `residual_px` as if it were accuracy.

**Sub-pixel means sub-pixel of WHICH image?** Always the **reference** grid, and always report
the metres equivalent alongside: *"0.4 px on the LROC NAC reference grid — about 20 cm."*
A judge will ask. An unqualified "sub-pixel" is not an answer.

---

## 8. THE FIVE ANSWERS EVERYONE MUST HAVE

Not slogans — these are the questions most likely to be asked, with honest answers.

**"Is this really multi-modal?"**
> "Our Tier C pairs are visible-against-infrared, which is genuinely multi-modal. Tier A is
> same-sensor and we call it a sun-angle experiment, not multi-modal."

**"How do you handle a 20× scale difference?"**
> "We resample both images to a common ground sample distance using the metadata, then match on a
> pyramid. Learned matchers degrade past roughly 4–8× on their own — we don't rely on that."

**"What's your accuracy on real data?"**
> "On synthetic and DEM-rendered pairs where we have true ground truth: [rmse_gt_px]. On real
> pairs we report held-out residual, [residual_px], because there is no ground truth to measure
> against — those are different quantities and we don't conflate them."

**"Why not SuperPoint, everyone uses it?"**
> "Its pretrained weights are academic/non-commercial research only. LoFTR is Apache-2.0. If ISRO
> ever wanted to deploy this operationally, SuperPoint would be a licensing blocker."

**"You didn't get PRADAN data, did you?"**
> "We did use Chandrayaan-2 OHRC. We also registered on ISRO's portal. Our engine is
> sensor-agnostic by design — the PS asks for a generic solution — so we validated across four
> missions."

---

## 9. NUMBERS DISCIPLINE — THE ONE RULE THAT PROTECTS US

> **No number goes into a slide, a script, or the Q&A bank until it exists in
> `evaluation/results_log.csv`.**

Until then it is written as `[TBD — results_log.csv]`.

The first draft of these guides contained **fabricated example results** — "0.7 px", "SIFT 4.2 px",
"5.4× improvement", "12 matches, RMSE=8.2px" — presented as though measured, in the comparison
table, the failure gallery, the demo script and the Q&A bank. Four people were scheduled to
rehearse those numbers on Days 13–15.

Being caught quoting a number you did not measure ends the run. There is no recovery from it in a
Q&A round. **If you catch a bare number anywhere in these documents that is not marked
`[TBD]` and not traceable to the CSV, delete it and tell the team.**

---

## 10. SIH SUBMISSION FACTS

- College SPOC registered before the 14 Aug 2026 deadline ✅. Team registered, SIH26166 submitted ✅.
- **Internal college hackathon: September 2026, exact date TBC.** Chase your SPOC.
- SIH26166 submission closes **20 September 2026**; SPOC portal nomination **30 September 2026**.
- Grand Finale: **December 2026**, 36 hours, at a nodal centre.
- Eligibility, all satisfied: team of 6 ✅, ≥1 female member (Saniya) ✅, all from one institution ✅.

### The official idea format — six slides INCLUDING the title page

1. **TITLE PAGE** — metadata only: PS ID · PS title · theme · PS category (Software/Hardware) ·
   team ID · team name (as registered on the portal). Not a content slide.
   **There is no "Problem Statement" slide.**
2. **IDEA TITLE** — prompts: Proposed Solution · Detailed explanation · How it addresses the
   problem · Innovation and uniqueness. The problem framing lives in the third bullet here, or in
   the spoken script. It does not get a slide of its own.
3. **TECHNICAL APPROACH** — Technologies used · Methodology and process for implementation.
4. **FEASIBILITY AND VIABILITY** — Analysis of feasibility · Potential challenges and risks ·
   Strategies for overcoming them.
5. **IMPACT AND BENEFITS** — Potential impact on the target audience · Benefits (social, economic,
   environmental).
6. **RESEARCH AND REFERENCES** — Details / links of reference and research work.

The template's own instructions slide says, verbatim: *"Kindly keep the maximum slides limit up to
six (6). (Including the title slide)"* — so the cap **includes** the title page.
**We have five content slides, not six.**

> ✅ **Confirmed against the real file** — `SIH2026-IDEA-Presentation-Format.pptx`, 924,505 bytes,
> sha256 `ce3e5dee…`, 7 slides (the 6 above plus an instructions slide we delete from our deck).
> Two earlier drafts of this section were wrong. The first invented "Results", "Demo/Application"
> and "Future/Team". The second — the one this replaces — listed "Problem Statement" and "Proposed
> Solution" as slides 1 and 2, and counted six *content* slides. Neither heading exists; "Proposed
> Solution" is a bullet prompt inside IDEA TITLE. Use the template unaltered: do not add slides,
> rename headings, or delete the bullet prompts.
>
> ⚠️ Slides 3–6 keep the numbers our docs already used. A blind "shift everything by one" breaks
> four things that are already correct.

### What the internal round is

**In-person, live demo, faculty judges — not domain experts.** Two implications:
- The demo must survive on Samartha's laptop with wifi off.
- The pitch must be legible to someone who does not know what a homography is. Lead with the
  picture, not the method.

---

## 11. GATES — THE ONLY VERSION

A failed gate means **cut scope, never extend time.** These supersede any gate list elsewhere.

| Gate | Day | Pass criteria | If it fails |
|---|---|---|---|
| **1** | 5 | `python -m core.pipeline data/pairs/pair_01` runs end to end on a real lunar pair, no manual steps, prints all five metrics | Drop LoFTR. Ship classical + illumination normalisation + sub-pixel + uniformity. **Then use Gate 2-alt below.** |
| **2** | 8 | `rmse_gt_px` < 0.5 on synthetic · ≥2× better than best classical baseline on Tier A · `inlier_ratio` > 0.60 · `grid_coverage_fraction` ≥ 0.80 · `distribution_cv` < 1.0 · runs on ≥1 Tier B pair · **produces matches on ≥1 Tier C (multi-modal) pair, with degradation honestly quantified** | Freeze the algorithm. Everything moves to UI and demo. |
| **2-alt** | 8 | *(only if Gate 1 failed)* Same, except the comparison baseline is **plain SIFT/ORB/AKAZE without illumination normalisation**, and the claim becomes "classical + our preprocessing beats classical alone" | Freeze and move to UI |
| **3** | 10 | A stranger operates the UI and explains the output with nobody speaking | Fix UX until they can — **this is before code freeze, so you can** |
| **4** | 11 | Demo runs 3× consecutively on **Samartha's laptop, CPU only, wifi OFF**, cached weights and data, no crashes | Debug until stable |
| **5** | 12 | All 6 answer cold: what problem · why hard · what does my module do · how do we know it works · what next | Extra prep for weak members |

### Two traps the first draft walked into

**Gate 1's fallback used to break Gate 2.** "Drop the learned matcher" plus "be 3× better than the
classical baseline" means comparing classical to classical. That is why **Gate 2-alt** exists.

**Gate 2 used to require a real cross-sensor pair while the data fallback was "LROC-only."** That
fallback could never satisfy that gate. It is fixed because we now have actual CH-2 data with no
login, plus Kaguya and M3.

**Gate 3 used to sit on code-freeze day** with the remedy "fix UX until they can" — which would
break the freeze. It is now Day 10, before freeze.

---

## 12. SCHEDULE SHAPE

The plan is **12 working days**. Today is 29 Aug 2026; if the internal round lands in the second
week of September you have roughly 10–13 days, not 15.

- **Days 1–2** Kill the risks
- **Days 3–5** Walking skeleton → **Gate 1**
- **Days 6–8** Make it good → **Gate 2**
- **Days 9–10** Product layer → **Gate 3**
- **Days 11–12** Freeze and rehearse → **Gates 4, 5**

**If you get extra days**, they go to Phase 2 (Days 6–8 becomes 6–11): more Tier C pairs, the
swept-illumination curve, a second illumination method. **Never** extend Phase 4 — rehearsal
saturates after three runs.

**If you get fewer days**, cut in this order: (1) baseline comparison in the UI, (2) Tier B+
Kaguya pairs, (3) the second illumination method. **Never cut** Gate 4 or Gate 5.

---

## 13. TOOLING — VERIFIED AVAILABLE

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu   # CPU build for the demo machine
pip install kornia opencv-contrib-python numpy pandas matplotlib streamlit pillow
pip install pds4_tools pvl rasterio scikit-image
```

Verified on PyPI: `pds4_tools` 1.4 · `pvl` 1.3.2 · `rasterio` 1.5.1 · `kornia` 0.8.3 ·
`opencv-contrib-python` 5.0.0.93 · `streamlit` 1.62.0 · `pymagsac` 0.2.3.

⚠️ **On Windows, `python3` does not work** — it opens the Microsoft Store. Use `python` or `py`.
Every command in these guides uses `python`.

⚠️ `pip install magsac` fails — no such package. Use `cv2.USAC_MAGSAC`.

---

## 14. REPO STRUCTURE

```
sih26166/
├── data/
│   ├── raw/                    # Rohan: original downloads, ORIGINAL FILENAMES, never renamed
│   ├── pairs/                  # Rohan: pair_01_source.tif, pair_01_ref.tif, ...
│   ├── pairs_catalogue.csv     # Rohan: one row per pair, tier labelled
│   └── DATASET_CARD.md         # Rohan: provenance — URL, date, licence, product ID
├── evaluation/                 # Samrudh
│   ├── synthetic_data.py
│   ├── shaded_relief.py        # SLDEM → shaded relief at chosen sun az/el
│   ├── metrics.py
│   ├── test_metrics.py
│   └── results_log.csv         # THE ONLY SOURCE OF NUMBERS
├── baselines/                  # Risheeth
│   ├── sift_baseline.py, orb_baseline.py, akaze_baseline.py
│   ├── run_all_baselines.py
│   ├── results_table.csv
│   └── failure_gallery/
├── app/                        # Rishabh + Samartha
│   ├── change_detection.py     # Rishabh
│   └── streamlit_app.py        # Samartha
├── core/                       # Samartha
│   ├── io_loader.py            # format abstraction — PDS3, PDS4, GeoTIFF
│   ├── illumination.py
│   ├── scale.py                # resample to common GSD + pyramid
│   ├── matcher.py
│   ├── ransac.py
│   ├── subpixel.py
│   ├── distribution.py
│   └── pipeline.py
├── presentation/               # Saniya
├── weights/                    # Pre-cached model weights — REQUIRED for Gate 4
├── demo_cache/                 # Demo inputs copied locally — REQUIRED for Gate 4
├── requirements.txt
└── README.md
```

**Naming:** `pair_01_source.tif` · `results_YYYYMMDD_HHMM_config.csv` · no spaces, no special
characters. **Never rename a raw download** — it breaks PDS label association.

---

## 15. WORKING RULES

- **Daily 15-min standup, all 6, same time. Show an artifact, not a status.**
- **Git:** work directly on `main`, one folder per person, `git pull` before and `git push`
  after every session. No branches, no PRs — see `01_HOW_WE_WORK_TOGETHER.md`.
- **Big image data lives in Google Drive, never in Git.** Code and CSVs in Git, images in Drive.
- **No teammate ever waits on Samartha.** If you are blocked mid-task, the spec was bad — say so
  in chat and Samartha fixes the spec, not you.
- **Blocked more than 30 minutes? Post in chat.** Not after two hours. Thirty minutes.
- **Scope creep (3D reconstruction, DEM generation, onboard deployment):** refuse. It goes on the
  Future Scope portion of the Impact slide and nowhere else.
