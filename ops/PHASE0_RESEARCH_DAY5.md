# Phase 0 — what wins, what loses, and where we sit (research ledger)

**Day 5, 3 Sep 2026, evening. Samartha (with the AI research pass).**
Purpose: the evidence base for the Phase 1 novelty decision. Nothing here is a decision.

Every claim is labelled. **VERIFIED** = the primary source was fetched and the text says it; the
extract or PDF is on disk in the session scratchpad and the URL is given. **INFERRED** = a
secondary source, a snippet, or my synthesis. The distinction matters because the last plan
carried a wrong prior-art claim (see §5.1) for a week.

How this was gathered, honestly: an 8-agent web research pass ran for 18 minutes, fetched ~500
pages, then died on the account's session limit before writing output; two relaunches died on
API overload (529) at zero cost. The queries, URLs and fetched extracts were salvaged from the
dead agents' transcripts, and I re-fetched or text-extracted every primary source that matters
myself (official SIH PDFs, the pptx template, the 2025 SAC paper PDF, institution rubric PDFs,
the Wan 2021 PDF). Three gap-filling agents were still running when this was written; their
findings, if any, go in §8.

---

## 1. The rubric — what is actually written down

### 1.1 Official SIH idea-selection criteria (VERIFIED, no weights exist)

SIH 2026 Guidelines for College SPOCs, p.20, "IDEA SELECTION CRITERIA":

> "Post Idea submission process, the ideas will be evaluated by experts. Evaluation criteria will
> include novelty of the idea, complexity, clarity and details in the prescribed format,
> feasibility, practicability, sustainability, scale of impact, user experience and potential for
> future work progression."

Source: https://www.sih.gov.in/letters/SIH2026-Guidelines-College-SPOC.pdf (26 pp, extracted).
Identical sentence in the 2024 guidelines, the 2020 idea-submission FAQ, the 2019 student FAQ, and
in college circulars that copy it (TSEC 2020, IIEST 2020, NIT Jamshedpur 2023). **No official
weights exist for this list.** "Novelty of the idea" is listed first every time.

Same document, p.24: "The ideas or solutions provided/developed/proposed by the teams must be new
and must not have been present in any previous event/program of any sort." p.18: "4-5 teams per
problem statement may be selected for the grand finale, but the final decision rests with the
problem statement creating organization, which isn't obligated to declare a winner unless student
proposals meet their expectations." p.25: prize Rs 1,50,000 per PS, paid "ONLY IF that
organization likes the idea of the winning team."

### 1.2 The template is a rubric prompt (VERIFIED — pptx on disk, sha unchanged from Canonical Facts)

`SIH2026-IDEA-Presentation-Format.pptx`: slide 2 bullets are "Detailed explanation of the proposed
solution / How it addresses the problem / Innovation and uniqueness of the solution". Instructions
slide: "Idea should be unique and novel." · "Kindly keep the maximum slides limit up to six (6).
(Including the title slide)" · PDF only. Canonical Facts §10 is correct.

### 1.3 Internal-round rubrics colleges actually publish (VERIFIED — PDFs/pages on disk)

SIH does not prescribe the internal rubric; the SPOC guideline only requires a report with
"Judging process (1 page), Jury panel details (1 page)". Each college writes its own. Found:

| Institution | Year | Criteria and weights | Source |
|---|---|---|---|
| St Aloysius College | 2025 | Relevance to SIH PS **25** · Innovation & Originality **25** · Feasibility (technical + time) 20 · Impact & Usefulness 20 · Presentation & Clarity 10 (/100) | staloysiuscollege.ac.in …/2026/05/Hacathon-report.pdf |
| TCET Mumbai | 2026 | Problem Understanding & Impact 25% · Innovation & Technical Excellence **30%** · Feasibility/Practicability/Scalability 25% · Solution Quality & Presentation 20% | tcetcercd.in/hackathons/3 |
| LPI | 2025 | Innovation/Originality 10 · Feasibility 10 · Social/Env Impact/Business Value 10 · Technical Execution 10 · Presentation 10 (/50) | lpi.ac.in …Internal Hackathon 2025 LPI.pdf |
| SIT Siliguri | 2024 | Innovation & Creativity 15 · Technical Proficiency 15 · Impact & Relevance 15 · UX 15 · Team Collaboration 10 · Problem Solving 10 · Presentation 15 · Overall Impression 5 (/100) | sittechno.org …SIT Siliguri.pdf |
| SSIP Gujarat college | 2024 | the eight official criteria verbatim, no weights | ssipgujarat.in …HACKATHON 2024 REPORT.pdf |
| GUNI | 2024 | Innovation · Functionality · Technical Implementation · Impact · Presentation, no weights | ssipgujarat.in …GUNI SIH 2024 Report.pdf |
| MMMUT Gorakhpur (IEEE SB) | 2024 | Innovation · Feasibility · Relevance · Technical Proficiency · Presentation, no weights; jury = 7 faculty | events.vtools.ieee.org/event_media/download/48136 |
| VIT Pune | 2026 | Problem Understanding · Innovation · Technical Feasibility · Practical Impact · Presentation (+2 unnamed); judges are alumni/industry, **not faculty**; 15 min incl. Q&A | scribd SIH-2026-Rules-and-FAQ |
| BCREC Durgapur | 2026 | no weights; 10-min pitch; "strict 6-slide PDF" | bcrec.ac.in/sih |

Pattern (INFERRED from the table): innovation is listed first everywhere and carries 20–30% wherever
weights exist; **relevance to the PS is its own 15–25% line in three of the four weighted rubrics**;
feasibility 20–25%; presentation 10–20%. Our SPOC's 25% for novelty is mid-range. The St Aloysius
sheet (25/25/20/20/10) is the closest match to what Canonical Facts inferred.

### 1.4 The grand-finale rubric (VERIFIED via a Scribd mirror of "Evaluation Guideline for SIH 2023"; issuer not printed on the mirror, so treat the attribution to MIC as INFERRED)

Three rounds, every criterion scored 1–20, three evaluators averaged, final = R1×0.20 + R2×0.30 +
R3×0.50 out of 100.

- **Round 1 (20%)**: Presentation of the solution/idea · Innovation ("uniqueness and creativity")
  · Solution approach · Technical soundness/feasibility · Execution timeline for the hackathon.
- **Round 2 (30%)**: Prototype development · Improvement (changes made on feedback) · Integration ·
  Usability · Team work.
- **Round 3 (50%)**: Functionality / relevance to the problem statement · Performance / final demo
  · User experience, aesthetics and design · Market readiness / impact · Implementation plan /
  future scope.

Source: https://www.scribd.com/document/712193023/Evaluation-Guideline-for-Smart-India-Hackathon-2023.
Consistent with judge Kuldeep Singh's SIH 2020 account (thinkuldeep.com/event/sih-2020): parameters
"User Experience, Solution appearance, Impact, Technology, Execution"; Day-1 feedback was about
"alignment towards problem statements, product thinking, and analysis".

**Reading:** innovation is one criterion of five in a round worth 20% at the finale. The finale is
won on rounds 2 and 3: a working, improving, relevant prototype. The internal round is where novelty
carries its highest weight, and that is the round we face on 9 Sep.

### 1.5 Who judges (VERIFIED)

- Internal round: faculty, per our SPOC and per every college report above (VIT Pune is the
  exception and uses external alumni/industry).
- ISRO finale, 2022: "judged by Jury consisting of Scientists/Engineers from ISRO/DOS and Domain
  experts from various ISRO/DOS centres. Shri Shashikant Sharma was Chief judge."
  (isro.gov.in/ISRO_Organizes_Smart.html). At nationals, ISRO problem statements are judged by
  ISRO domain experts. Anything that would not survive a SAC scientist will not survive nationals.

---

## 2. What winners have in common (mostly INFERRED — secondary first-person accounts)

- **The finale is iterative.** Every first-person account describes mentoring → evaluation loops
  over 36 hours; scores reward "Improvement" explicitly (§1.4). SIH 2023 winner (Medium,
  sarika-purohit): Round 1 "judges questioned originality" and the team answered with their own
  Figma designs and process; Round 2 was "a list of improvements"; Round 3 a live demo.
  "Presentation and storytelling matter as much as coding." SIH 2025 MathWorks-track winner TwinX:
  "get feedback from judges in mentoring round and modify the solution till upcoming evaluation
  round"; validated against "real Indian road conditions" rather than ideal ones.
- **Relevance beats cleverness.** Judge Singh's first Day-1 note is PS alignment; a 2022 winner's
  tips (anishprashun.me): "Carefully study and address every word in the official problem
  statement" and "Judges care more about how your tech solves the problem, not how fancy your
  stack is."
- **A visible, working artefact.** Winners' advice is uniform: prototype screenshot/video/test case
  in the deck; integration "from day one"; end-to-end working by the last round.
- **ISRO PS winners are often not the space-science entries.** VERIFIED from result pages:
  SIH 2024 ISRO winner SIH1740 (vehicle map-matching, IIT Guwahati) — while the lunar OHRC/PSR PS
  SIH1732 produced only a consolation (Chandrakriti, SAL Engineering). SIH 2025 ISRO first prize
  SIH25172 "Vasuki" (Manipal) — a transformer web-application firewall (title INFERRED from a
  YouTube listing). SIH 2023 ISRO winner SIH1517 hereWeGoAgain (IIT Durgapur), title unresolved.
  The one lunar entry with a public write-up (SIH1732, hashnode) was CLAHE + NLM + gamma with PSNR/SSIM
  — competent, generic, and it did not win.

---

## 3. Why teams lose

**Official (VERIFIED):** idea "must be new" and not from a previous event; altered template or
non-PDF; more than six slides; team composition; "assembly of available components" makes the team
liable for plagiarism/IP conflicts (sih.gov.in/projectImplementation) — cite and acknowledge every
open-source piece; the PS owner "isn't obligated to declare a winner".

**Anecdotal, consistent across ≥3 accounts (INFERRED):** drifting from the specific PS; "we'll use
AI" without the how; generic AI-written decks ("many teams rely too heavily on AI tools for
content, which leads to generic submissions"); no prototype evidence; overcomplication; failing
the Round-1 originality challenge; running out of time in a 7-minute pitch.

---

## 4. What "novelty" means to these judges

- Official wording only ever says "novelty of the idea", "uniqueness and creativity", "Innovation
  and uniqueness of the solution", "unique and novel". No definition. (VERIFIED)
- Non-expert evaluators penalise the extremes. Boudreau, Guinan, Lakhani & Riedl, *Management
  Science* 2016 (2,130 randomised evaluator–proposal pairs): "evaluators systematically give lower
  scores to research proposals that are closer to their own areas of expertise" and "more novel
  proposals are associated with lower evaluations … it is proposals with particularly high levels
  of novelty — the 'right tail' — that account for this result." (VERIFIED, PMC5062254.)
  Implication for faculty judges: novelty must be legible and bounded — one clear "what is new"
  sentence with a comparison to what exists, not a claim that the whole method is unprecedented.
- The Round-1 challenge is "is this original / how is it different" (winner account above). A
  comparison-to-existing table is expected by every unofficial guide (Reskilll: "What's NEW about
  your approach? How is it different from existing solutions?") — INFERRED.
- No evidence either way on how SIH judges score honest negative results. Absence of evidence.

---

## 5. Prior art — the section where we lose if we are careless

### 5.1 The paper the plan misdescribed (VERIFIED — 27-page PDF extracted)

arXiv:2509.04775 (5 Sep 2025), *Comparative Evaluation of Traditional and Deep Learning Feature
Matching Algorithms using Chandrayaan-2 Lunar Data*. Makharia & Sharma (Manipal University Jaipur);
**Singla, Amitabh, Dube — "Signal and Image Processing Area, Space Applications Centre ISRO,
Ahmedabad".** Amitabh (amitabh@sac.isro.gov.in) leads SAC's Planetary and Space Science Data
Processing Division (LPSC 2026 abstract 1198, Chandrayaan-4 landing-site work with OHRC) and was
the SAC expert on the 2023 ISRO lunar hazard-map PS. **Treat this group as the probable author of
SIH26166.** The PS's expected metrics ("RMSE, inlier counts, inlier ratios") are this paper's.

What it does: SIFT, ASIFT, AKAZE, RIFT2, SuperGlue on OHRC↔LROC NAC, IIRS↔LROC WAC, DFSAR↔SELENE,
equatorial and polar. Preprocessing: georeferencing; **"Resolution Resampling — OHRC (~30 cm) was
resampled to match NAC's resolution … IIRS (~80 m) was resampled to align with WAC's 100 m … DFSAR
… to SELENE's ~9 m"**; intensity normalisation to 8-bit; CLAHE; histogram matching; **shadow
normalisation**; PCA for IIRS; RANSAC homography; warp. Table 3 (RMSE X/Y px, s): OHRC–NAC
equatorial SuperGlue 0.62/0.57 in 3.8 s, RIFT2 1.50/1.19, ASIFT 1.99/1.63, AKAZE 3.12/4.71, SIFT
3.61/5.96 (678 s); OHRC–NAC polar only SuperGlue succeeded (0.92/0.76). Conclusion: SuperGlue best;
"SIFT, ASIFT, and AKAZE … are likely not the best options for polar regions".

What it does **not** do — and this is where our room is:
- **LoFTR, LightGlue and the word "transformer" do not appear.** The plan's line "a 2025 paper
  already benchmarks LoFTR on Chandrayaan-2 data" is false; it benchmarks SuperGlue.
- **RMSE is a fit residual, not accuracy.** §4.7.1: "Identifying matching control points … Applying
  the derived perspective transformation … Calculating the Euclidean distance". The words "ground
  truth" do not occur. That is exactly the `residual_px` trap Canonical Facts §7 warns about, and
  we have a measured case where it fails by two orders of magnitude (§6).
- No sun-angle sweep, no scale sweep, no spatial-distribution metric, no failure detection.
  Illumination is handled by CLAHE/shadow normalisation; polar failures are attributed to
  "significant viewpoint changes and variations in crater shapes".

Consequence for our claims: **D (illumination normalisation before a learned matcher) and E
(common-GSD resampling before matching) are this paper's own preprocessing.** They are correct
engineering and must stay in the pipeline, but they are not novelty and must not be presented as
such. Saying so, with the citation, is worth more than claiming them.

### 5.2 Illumination-invariant lunar matching is an active, benchmarked field (VERIFIED)

- Xie, Liu, Di et al. 2025, *Remote Sensing* 17(13):2302 — MiLOI: 321 multi-illumination LROC NAC
  pairs (azimuth differences up to 180°, incidence differences up to 78°), ground truth from five
  manual correspondences + similarity fit (<1 px residual); crater-neighbourhood matching beats
  SIFT/HAPCG/ML-HLMO/WSSF (success 100/100/72% by scene vs SIFT 0–17% on the hard scenes). No learned
  matchers tested. Code and data public: github.com/Bin501/CNSFM. **This is a ready-made real
  Tier-A dataset with ground truth** — the thing we said we could never get.
- Rothenberger, Georgakis, Cheng, Ansar (JPL), AIAA SciTech 2025-2073, "Illumination Invariant Image
  Matching for Lunar TRN": LIMA, a correlation-based lighting-invariant algorithm plus learned
  illumination-invariant features; extended to LRO NAC mosaics in AIAA 2026-2244. (INFERRED —
  publisher page blocked, abstract via search.)
- Phase-congruency / structural families (HOPC, CFOG, HAPCG, RIFT) are the standard multimodal
  baselines the SAC paper itself uses (RIFT2). Our gradient-orientation normalisation is a
  textbook member of this family.

### 5.3 Rendering a DEM at swept sun angles is the standard way to get ground truth (VERIFIED)

- Geo-LoFTR (Pisanti, Hewitt, Brockers, Georgakis, arXiv 2502.09795, 2025): a LoFTR variant trained
  and evaluated on Blender renders of HiRISE maps "with sun azimuth spanning 0°–360° and elevations
  of 30°, 60°, 90°"; no illumination normalisation; "87% @1 m" with matched lighting, all methods
  degrade at 2° elevation.
- Singla, Patel, Dube (SAC) 2026, arXiv 2604.22296: evaluates lunar image simulators (ABRAM, CORTO,
  Blender, QGIS, custom Python) with Lambertian, Lommel-Seeliger and Hapke reflectance from
  OHRC/NAC/WAC/LOLA at different sun angles; notes the Python approach "does not support detailed
  lighting and shadow effects". Does not evaluate matchers.
- LunarStereo (Grethen et al., arXiv 2510.18172, ICCV-W 2025): SurRender ray tracing, Hapke BRDF,
  LOLA 5 m South-Pole DEM, "strong cast shadows"; fine-tunes MASt3R.
- Lunar-G2R (arXiv 2601.10449): scores rendering realism by the 2D matching-error distribution of a
  learned matcher; Hapke renders are "overly smooth, with attenuated contrast".

Consequence: **claim C is methodology, not novelty**, and ours is the weakest variant (Lambertian,
no cast shadows) of a method the PS-setters themselves study. Keep it as rigour, cite it, and
disclose the no-shadow limitation before being asked.

### 5.4 Optical ↔ DEM: feature matching fails, correlation works — published (VERIFIED, PDF on disk)

Wan, Shao, Li 2021, arXiv 2106.12738 (planetary UAV ↔ DEM): Table 3 — SIFT fails in **five of nine**
Mars optical-vs-DEM-shading scenes ("SIFT can hardly generate enough feature pairs owing to the low
texture … and large appearance variation between optical images and DEM terrain shading images");
phase correlation is below 1 px in seven of nine, and "did fail in several cases … as large as 20
pixels". No automatic method selection, no per-region confidence. NASA Ames Stereo Pipeline
`image_align` docs: "If only DEMs exist, their hillshaded versions can be used as images" and "When
the images are notably different, an approach based on dense pyramid correlation is recommended."
Also Aadi, Singla, Dube, Alexandrov 2026 (arXiv 2604.01032): SAC validates OHRC-derived DEM
horizontal accuracy by manual planimetric matching against NAC hillshade in QGIS.

Consequence: **the mechanism of claim B (fall back from features to global correlation on
optical↔DEM) is standard practice.** What is not in any of these: detecting, from the matcher's own
output, that a confident-looking correspondence set is wrong, and declaring which method was used.

### 5.5 "Knowing when you are wrong" — mature in other fields (VERIFIED abstracts)

- Uss, Vozel, Lukin, Chehdi, IEEE TGRS 2016 (arXiv 1602.02720), RAE: per-fragment Cramér–Rao bound
  on registration error "without ground truth", for optical–optical, optical–SAR, **optical–DEM**
  and DEM–SAR; "can identify image areas for which a predefined registration accuracy is
  guaranteed". Closest prior art to claim A. It is area-based, continuous, and has no explicit
  "unmeasured" state.
- Truong et al., CVPR 2021, PDC-Net: dense correspondences "coupled with a robust pixel-wise
  confidence map indicating the reliability and accuracy of the prediction" — "when to trust them".
- Brown & Lowe 2007, IJCV, panorama stitching: a probabilistic test that accepts an image match from
  RANSAC inlier/outlier counts. **Our Tier D result is the case where that test passes and the match
  is wrong** — 105 matches, a consensus homography, zero correct.
- Jin et al. 2020/2021, IJCV, "Image Matching Across Wide Baselines": evaluate matchers on
  "the accuracy of the reconstructed camera pose — as our primary metric", not on match counts.
- LGCN2025 (Di et al., LPSC 2025 #1380) and the LROC south-polar controlled mosaic (Wagner et al.,
  LPSC 2022 #2573; Wagner et al. 2024 PSJ): production lunar control uses brute-force 2-D
  correlation to LOLA-controlled frames; uncontrolled NAC offsets "up to ~100 m" at the pole.
- Feng, Du, Li, *ISPRS J. Photogramm. Remote Sens.* 2019 (doi 10.1016/j.isprsjprs.2019.03.002),
  "Robust registration for remote sensing images by combining and localizing feature- and
  area-based methods": a hybrid that moves between feature- and area-based registration with
  residual analysis. Closest prior art to the *switching* half of claim B. (VERIFIED title/venue via
  OpenAlex; the abstract summary is the tool's paraphrase, so the exact switching rule is INFERRED.)
- Kybic, *IEEE Trans. Image Processing* 2009: bootstrap resampling estimates pixel-level
  registration uncertainty "using only the two input images", for SSD/correlation/MI methods.
  (VERIFIED abstract via OpenAlex.)
- Bierbrier, Gueziri, Collins, *Medical Image Analysis* 2022: taxonomy and scoping review of
  registration error and confidence estimation across 165 works. (VERIFIED abstract via OpenAlex.)
  The field is mature; "we estimate our own registration error" is not, by itself, novel anywhere.

Consequence for claim A: **per-region registration confidence is published (RAE, PDC-Net).** The
part not found anywhere: a three-state map where "no evidence" is distinct from "low confidence",
applied to a learned matcher's output on lunar data, and used to gate a downstream consumer
(change detection, claim H). That is narrow. It is also true, measured, and ours.

### 5.6 The Chandrayaan-2 TMC/IIRS registration work at SAC (VERIFIED abstract)

Islam, Suhail, Amitabh Singh (SAC), *J. Indian Soc. Remote Sensing*, 2026: mosaicking Chandrayaan-2
TMC-2 DEM (10 m) with IIRS band 52 (1653 nm) over polar areas, with 3-D registration and LOLA fill
for shadowed regions. The PS's "OHRC, TMC and IIRS" triple is live work inside SAC.

---

## 6. Where our project sits, against the lists above

**On the winning list**
- Working end-to-end pipeline, 179 tests, exact reproducible Gate-1 number. (VERIFIED in repo.)
- Exact-ground-truth evaluation on a synthetic sun sweep, with the failure half of the curve
  (30°, 45°) logged. Rigour of a kind the SAC benchmark lacks (§5.1).
- CPU-only, offline, Apache-2.0 stack — a real feasibility line the SAC paper's SuperGlue choice
  (non-commercial SuperPoint weights) cannot make.
- One measured negative that is *ours*: a refiner that improved `residual_px` 5× while making
  ground-truth error worse, shipped off (core/bench_subpixel_results.csv, both numbers logged).
- One measured negative on real multi-modal data that is *ours*: 105 confident correspondences, 0
  correct within 94 m; RANSAC consensus on noise; FFT correlation to ~230 m (results_log.csv, Day 5).

**On the losing list**
- Two of four written novelty bullets are false today (`redetect()` has zero production callers —
  only its own docstring and tests; `core/scale.py` has no pyramid). Re-verified this evening.
- Two more (D, E) are the PS-setters' own preprocessing. Claiming them as innovation to a SAC judge
  is the "this already exists" failure mode in its purest form.
- The Tier D figures quoted anywhere (37.81 / 36.03 / 26.76 / 10.95) are fit residuals on wrong
  matches; and `evaluation/shaded_relief.py` still lights terrain from `az+180`.
- No real pair with a sun difference, so "sun-angle invariant" rests entirely on Lambertian renders
  without cast shadows. MiLOI (§5.2) is public and would fix that.
- `presentation/` is a 0-byte `.gitkeep` six days in; the deck is the deliverable on 9 Sep.
- Terminology: "cross-sensor" appears nowhere true in our data; every sentence using it is false.

**Two administrative findings**
- **Deadline discrepancy.** The SIH 2026 SPOC guideline (p.16) says team nomination and idea
  submission close **15 Sept 2026**; the PS listing mirror says **20 September 2026** for SIH26166;
  Canonical Facts §10 says 20 Sep with SPOC nomination 30 Sep. Ask the SPOC which is binding.
- The internal-round rubric is the college's own document. Ask the SPOC for the actual sheet; the
  St Aloysius / TCET sheets show what one looks like.

---

## 7. Sources on disk (session scratchpad, for re-verification)

`scratchpad/salvage/full/*.txt` — 172 fetched-page extracts from the first run, keyed by question.
`scratchpad/salvage/pdf/*.txt` — text of 38 PDFs/pptx the agents downloaded (official SIH
guidelines 2024 and 2026, student FAQs 2019/2020, the 2026 pptx template, nine institution reports,
Wan 2021 full text, Brown & Lowe 2007, LuNaMaps, Corsini 2009, the SIH 2026 226-PS catalogue).
`scratchpad/papers/` — arXiv 2509.04775 full PDF and clean text; LPSC 2022 #2573, 2025 #1380 and
#1504, 2026 #1198.

## 8. Late additions from the gap-filling agents

None. All four gap-filling agents (Q1+Q2 winners/losers, Q4 novelty, Q5b optical–DEM, Q5c
reliability) died on API overload (HTTP 529) at zero cost, at ~20:00 IST on 3 Sep. Everything
above was therefore verified in the main session, not by an agent. The open gaps that an agent
would have closed: the SIH 2023 PS SIH1517 title; more than four first-person winner accounts;
the exact switching rule in Feng, Du & Li 2019; and the AIAA 2025-2073 abstract (publisher blocked).
