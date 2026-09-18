# SIH 2026 national round — research brief (team LunaXX, PS SIH26166)

> **For the team, not the researcher.** Paste everything below the line into a deep-research tool
> (ChatGPT Deep Research, Gemini Deep Research, Claude Research, Perplexity). If it accepts files,
> attach `ps_counts_2026-09-18.csv` from this folder. If the report comes back shallow, run it
> twice: first with only workstreams A and B, then with C–F. Every figure in §3 was pulled from
> official pages on 18 Sep 2026; `pull_ps_counts.py` re-pulls the live counts.

---

## 0. Role and standard

You are a research analyst and competition strategist. A six-person undergraduate team has just been
nominated by its institute to the national stage of Smart India Hackathon (SIH) 2026, Software
edition. Today is 18 September 2026 and the idea-submission deadline is 30 September 2026, so your
report drives decisions the team takes in the next 48 hours.

Rules for your work:

- Be quantitative and sceptical. Correct us where the evidence says we are wrong, including anything
  in this brief.
- Tag every claim and give its URL and the date you accessed it: **[OFFICIAL]** SIH / MoE Innovation
  Cell / AICTE / ISRO page or PDF · **[RESULT-LIST]** official shortlist or winner list ·
  **[FIRST-PERSON]** a finalist's, winner's or judge's own account · **[SECONDARY]** blog, video,
  forum · **[INFERENCE]** your reasoning.
- Keep SIH 2026 rules apart from what happened in 2022–2025. Never present an earlier year's
  practice as a 2026 rule.
- Never invent a number. Estimates show the formula and inputs. Unknown means
  "UNKNOWN — how to find out: …".
- For login walls and JavaScript-only pages, try the Wayback Machine (web.archive.org) and state what
  you could not see.
- No generic hackathon advice. If a finding would not change one of the decisions in §1, leave it out.
- Do not recommend anything that needs a GPU on the demo path, a change to the official slide
  template, or claiming a result we have not measured.

## 1. The decisions this research must settle, in priority order

- **D1 — PS portfolio.** The rules allow ideas against at most two problem statements, one idea each.
  Options: (a) SIH26166 only; (b) SIH26166 plus one other PS — which?; (c) move away from SIH26166.
  Recommend one, with the expected-value arithmetic.
- **D2 — Submission mechanics and timing.** What we submit, field by field; whether it can be edited
  after submission; the date we should submit by, given that a PS freezes at 500 ideas.
- **D3 — The SIH26166 submission.** What to change so that ISRO/SAC expert screeners, reading the PDF
  alone, put us in their top 4–5.
- **D4 — The Grand Finale (December 2026).** What to build between the shortlist and the finale to
  win it.

## 2. Who we are and what exists — context, do not re-research

### The problem statement (official text, condensed)

**SIH26166** · Indian Space Research Organisation (Department of Space) · Space Technology · Software
*"Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images
(OHRC, TMC and IIRS)"*

- Named challenges: **illumination variation** (sun azimuth and elevation); **viewpoint variation**
  (camera position/orientation → shift, scale, rotation, perspective distortion); **scale variation**
  (different altitudes and resolutions).
- Expected solution, verbatim: *"Generic software solution for finding correspondence between
  Chandrayaan-2 acquired optical images and Lunar reference images with a sub-pixel accuracy of source
  image maintaining uniform distribution across the images."* Deliverables: *"Software and registered
  product with corresponding match points"*; *"Evaluation metric (eg. RMSE, inlier match count, inlier
  ratio, etc.)"*.
- Data: *"Specific datasets link will be provided - TBD"*; Chandrayaan-2 OHRC, TMC-2 and IIRS via
  chmapbrowse.issdc.gov.in; references LRO NAC (LROC downloads, QuickMap) and SELENE.
- Probable authors **[INFERENCE]**: the Signal and Image Processing Area at SAC-ISRO, Ahmedabad — see
  arXiv:2509.04775 (2025), *"Comparative Evaluation of Traditional and Deep Learning Feature Matching
  Algorithms using Chandrayaan-2 Lunar Data"* (SIFT, ASIFT, AKAZE, RIFT2, SuperGlue on OHRC↔LROC NAC,
  IIRS↔LROC WAC, DFSAR↔SELENE; its RMSE is a fit residual, not error against ground truth).

### What we built in 20 days — working, measured, CPU-only Python

Resample both images to a common ground sample distance → gradient-orientation illumination
normalisation → LoFTR matcher (Apache-2.0, via kornia) → MAGSAC++ → NCC sub-pixel refinement → 8×8
spatial-distribution metrics → a **trust layer**: an independent per-cell FFT/phase-correlation check
that never sees the matches, labels every cell *verified / weak / no evidence*, detects when the
matcher's homography is wrong, falls back to global correlation and says which method it used.
Streamlit UI. Every run's metrics go into one append-only results log. Automated tests.

Measured (from that log — do not suggest figures we have not measured):

- Rendered-DEM sun-azimuth sweep with exact ground truth, 15° sun difference: 0.0856 px RMSE
  (≈5.1 m at 60 m/px), inlier ratio 0.977, full grid coverage, 2.88× the accuracy of the best of
  SIFT/ORB/AKAZE on identical files.
- At 0° SIFT beats us (0.044 vs 0.086 px). At 180° we score 5/5 runs while 14 of 15 classical runs
  fail. Between 45° and 60° we are wrong without knowing it: 142.7 m out at 60°, with no warning.
- The trust check catches 77% of failures at 0% false alarms, over 2,560 cells.
- One real optical↔elevation pair (Kaguya TC against a LOLA hillshade): the matcher reports success
  and is more than 2 km wrong; the trust check catches it and the fallback gives 231 m ± 216 m.

### Known gaps — verify, extend and rank these; don't just repeat them

- No genuine cross-sensor pair (OHRC↔LROC NAC). Our only real OHRC test is two crops of one frame.
- TMC-2 and IIRS, both in the PS title, have never been used. No optical↔infrared result.
- All sun-angle evidence is Lambertian renders without cast shadows; no real multi-illumination pair.
- Scale is handled only by resampling, with no pyramid. Real ratios: OHRC↔TMC ≈18×, OHRC↔IIRS ≈285×.
- Viewpoint variation, one of the three named challenges, is not measured.
- The pipeline computes the warp and the matches but writes neither to disk: no registered product and
  no match-point file, although the PS names both as deliverables.
- Spatial uniformity is measured, not enforced.
- The idea deck (the six-slide SIH 2026 template) was written for a college faculty jury that also
  heard us pitch. National screeners read the PDF alone.

### Terminology we hold ourselves to

"Cross-sensor" means different instruments only (LROC NAC↔LROC NAC is the same sensor).
"Multi-modal" means different physical modalities (visible↔infrared/radar/elevation); two
panchromatic cameras are not multi-modal. "Sub-pixel" always names the pixel grid and gives metres.
Don't recommend wording that breaks these.

### Constraints

Six people, one institute; about ten working days before submission; the demo laptop has no discrete
GPU (Intel iGPU), so the demo path is CPU-only; free Kaggle GPUs for experiments; one member has an
AMD (non-CUDA) GPU.

## 3. Already verified on 18 Sep 2026 — build on these; re-check only if an official source contradicts them

Official — sih.gov.in/sih2026PS; the "SIH 2026 Guidelines" PDF under sih.gov.in/letters/2026/;
sih.gov.in/faqs:

1. Last date for team nomination and idea submission: **30 Sep 2026**. All 240 PSs show it.
2. *"One team can submit Ideas against maximum of 2 Problem Statement only."*
3. *"Only 500 ideas will be submitted for a particular PS. Once the count number got all 500 ideas,
   the particular PS will get freeze and no idea submission will be allowed."* The counter is public.
4. The team leader submits: chosen PS or Student Innovation category, idea title, idea description,
   idea presentation (PDF).
5. Screening is online and by experts: *"novelty of the idea, complexity, clarity and details in the
   prescribed format, feasibility, practicability, sustainability, scale of impact, user experience
   and potential for future work progression."* No weights are published.
6. *"4-5 teams per problem statement may be selected for the grand finale, but the final decision
   rests with the problem statement creating organization, which isn't obligated to declare a
   winner."* Shortlisted teams must be available for *"meetings, sessions and trainings during the
   preparation phase"*.
7. Grand Finale offline at nodal centres, proposed for December 2026. ₹1,50,000 per PS, paid
   *"ONLY IF that organization likes the idea of the winning team"*. Up to two mentors with ≥5 years'
   experience. The team name *"must not contain the name of your institute in any form"*.
8. Ideas *"must be new and must not have been present in any previous event/program of any sort"*.
9. The FAQ's SPOC section says *"Team & idea details once entered cannot be altered."* Whether that
   binds the team leader's own submission is unverified.

Our own analysis of official pages (method in brackets, so you can reproduce it):

10. On 18 Sep 2026: 240 PSs (182 software, 58 hardware) and 6,005 ideas in total. Software median
    17 ideas per PS (P25 8, P75 30, P90 71, max 169). **SIH26166: 29/500** — more than 134 of the 182
    software PSs. [parsed sih.gov.in/sih2026PS]
11. The 2024 analogue [Wayback Machine snapshots of sih.gov.in/sih2024PS on 18, 22, 25, 28 and
    30 Sep, 7 Oct and 18 Nov 2024]. Total ideas rose from 4,570 on 18 Sep to about 55,000. The 2024
    deadline had been extended to 30 Sep, yet counts kept rising until about 7 Oct — find out whether
    it was extended again. Final count against the count on 18 Sep, software PSs:

    | Ideas on 18 Sep 2024 | PSs | Final median | P10–P90 | Reached 500 |
    |---|---|---|---|---|
    | 0–4 | 51 | 104 | 67–134 | 0 |
    | 5–9 | 38 | 127 | 91–162 | 0 |
    | 10–19 | 34 | 190 | 121–294 | 0 |
    | 20–39 | 31 | 380 | 275–500 | 4 |
    | 40–79 | 16 | 500 | 390–500 | 12 |
    | 80+ | 8 | 500 | 500 | 8 |

    The rank order barely moved (Spearman ≈ 0.89). PSs at the cap: 8 by 22 Sep, 16 by 25 Sep, 20 by
    28 Sep, 30 by 30 Sep, 35 at the end.
12. SIH 2023 grand-finale shortlist [sih.gov.in/sih2023-screening-final-result]: 1,282 teams across
    231 PSs. Five teams per PS is the mode (range 3–10); ISRO's PSs had 3–8 each.
13. SIH 2025 results [sih.gov.in/sih2025/sih2025-grand-finale-result]: each of ISRO's 11 software PSs
    (SIH25169–SIH25179) has exactly one awardee, graded across PSs — First, Second and Third Prize,
    Consolation Prize, and special awards (Future Innovators, Girls Achiever, Quantum Frontier). Most
    other organisations list "Winner" or "Joint Winner". In 2024 ISRO's lunar OHRC PS (SIH1732, 211
    ideas) got a consolation prize and the ISRO winner was a map-matching PS (SIH1740) — verify.
14. Seeds for a second PS, with ideas on 18 Sep. Seeds, not conclusions — scan all 182 software PSs
    and the Student Innovation themes:
    - **SIH26227**, MoD — semantic retrieval and multi-temporal change analysis of satellite imagery
      (12). Lists imperfect co-registration, illumination and view-angle differences as false-change
      confounders, and asks for confidence estimates.
    - **SIH26013**, MoRD — multi-source geospatial data harmonisation for urban land records (4). Asks
      for spatial matching, a geo-referencing engine, change detection and confidence scoring.
    - **SIH26142**, NTRO — deep-learning super-resolution mapping from medium-resolution satellite
      imagery (10).
    - **SIH26175**, ISRO — "DepthWizard", single-view height estimation and 3D flythrough (12); SAC
      reference repository github.com/IMG-PROCESS-SAC/SIH-DepthWizard-2026.
    - **SIH26169**, ISRO — AI virtual-camera tracking for coarse alignment of free-space optical
      terminals (8).
    - **SIH26167**, ISRO — "SatQuery AI", a vision-language assistant for remote-sensing imagery (53).
    - **SIH26162**, NTRO — industrial fires from NASA FIRMS, OSM and satellite data (16).
    - **SIH26143**, NTRO — oil spills from satellite imagery with AIS correlation (43).
    - **SIH26209**, AICTE — Student Innovation, Space Technology, software (17).

## 4. Workstreams

### A. Rules and portal mechanics — do this first

- **A1.** Deadline: exact date, time and time zone; the extension history in 2024 and 2025, and how
  extensions were announced.
- **A2.** The two-PS rule: does a Student Innovation idea count toward the two? If we are shortlisted
  on both, can we compete in both or must we choose, and when? Is there any sign that screeners of one
  PS see, or hold against us, a second submission? Is there a per-institute cap at shortlisting?
- **A3.** Editing: can the team leader change the title, description or PDF after submitting? Is
  there a draft state, and does a draft count toward the 500? What happens to a draft if the PS
  freezes?
- **A4.** Field limits: length of title and description; PDF size; whether hyperlinks (GitHub, demo
  video) inside the PDF are allowed, and whether shortlisted teams used them; what the "Team ID" on
  the title slide must be at national level.
- **A5.** After submission: screening and result dates in 2023, 2024 and 2025; what the "preparation
  phase" involved; whether PS organisations contacted or interviewed teams before the shortlist.
- **A6.** Anything new in 2026 compared with 2025: AI-generated content, plagiarism checks,
  code-repository requirements, pre-built code.
- **A7.** Institute-side risks: the SPOC's internal-hackathon report, the authorisation letter, and
  anything else whose absence has cost teams their place.

### B. Competition model and the choice of PS

- **B1.** Test our hypothesis "fewer submitted ideas means better chances". Keep the chance of being
  shortlisted apart from the chance of winning the finale. Start from this model and improve it:
  experts rank the N final ideas on a PS and shortlist the top k (4–5, sometimes up to 10), so we are
  shortlisted if our quality percentile beats 1 − k/N. With k = 5 that is the top 1.3% at N = 380
  and the top 4.8% at N = 104. How skewed is the quality of SIH submissions, and so how much does N
  matter compared with quality?
- **B2.** Project every software PS's final count (P10/P50/P90) from the 2024 analogue; add 2025 if
  the Wayback Machine holds snapshots of sih.gov.in/sih2025PS (we found none). Re-pull the live
  counts twice, at least 24 hours apart, to measure 2026's pace. Flag the PSs — SIH26166 included —
  at risk of freezing before 30 Sep, and by what date.
- **B3.** Score every software PS and Student Innovation theme on fit: (a) reuse of what we have —
  registration, illumination normalisation, confidence/trust estimation, change detection, PDS/GeoTIFF
  input, CPU-only computer vision; (b) public data usable offline; (c) whether two people can produce a
  prototype-backed six-slide deck in eight days without taking anything from the SIH26166 deck; (d) a
  CPU-only demo; (e) who judges it and what they reward; (f) how winnable the finale is.
- **B4.** For the top five: projected final ideas, expected finalists, our likely quality percentile
  (argue it), P(shortlist), effort in person-days, the risk of weakening SIH26166, and the gain in
  P(shortlisted on at least one). Recommend, and give a rule we can re-check on 25 Sep against live
  counts.
- **B5.** Competitor intelligence: search GitHub, LinkedIn, YouTube, Reddit, Medium and Hashnode for
  "SIH26166", "SIH 26166", "SIH 2026 Chandrayaan image registration" and variants — who is working on
  it, with what approach, how far along. Do the same for the top two alternatives. Which institutions
  have historically reached ISRO or space finals?

### C. What gets shortlisted, and what wins

- **C1.** Collect at least 15 idea-stage decks from teams shortlisted for the 2022–2025 finals
  (priority: ISRO/SAC/NRSC, remote sensing, image processing, lunar or planetary) and at least 5 from
  teams that were not shortlisted. Confirm each status against the official lists.
- **C2.** Find what separates the two groups, and count it ("12 of 15 shortlisted decks showed a
  prototype screenshot; 1 of 5 rejected decks did"): prototype evidence, measured results, a
  demo-video link, coverage of the PS's own wording, an architecture diagram, named datasets,
  comparison with existing methods, feasibility and cost, impact on the PS owner's mission,
  references, text density, template compliance.
- **C3.** ISRO, 2022–2025: PS titles, finalists, winners and what they built (SIH1740 in 2024,
  SIH25172 "Vasuki" in 2025, SIH1732 "Chandrakriti" in 2024, SIH1517 in 2023); who judged; what ISRO
  judges asked; how the graded ISRO awards are decided and what each pays.
- **C4.** The finale: duration, rounds, mentoring and the rubric. An SIH 2023 evaluation guideline
  **[SECONDARY — a Scribd mirror, issuer not printed]** weights three rounds 20/30/50: R1 idea,
  innovation, approach, feasibility, execution timeline; R2 prototype, improvement after feedback,
  integration, usability, teamwork; R3 functionality and relevance, final demo, UX, market readiness
  and impact, implementation plan. Confirm or correct it for 2024 and 2025. Also: which nodal centre
  hosted ISRO's PSs; internet, power and GPUs at nodal centres; whether bringing pre-built code is
  allowed, and how judges treat it.
- **C5.** What winners did between the shortlist and the finale: mentors, meetings with the PS owner,
  asking for data, rehearsal.

### D. The technical gaps on SIH26166, as a SAC expert would see them

- **D1.** Map every phrase of the PS to what a SAC reviewer will look for. In particular: on which
  pixel grid do SAC's own papers measure "sub-pixel accuracy of source image"? What does "generic"
  demand? In what format is a "registered product with corresponding match points" expected —
  GeoTIFF, a GCP list, an ISIS control network?
- **D2.** The state of the art in 2024–2026 for multi-illumination, multi-scale and multi-modal
  planetary registration: learned matchers (LoFTR, LightGlue with ALIKED or DISK, RoMa, MASt3R, XFeat,
  OmniGlue, modality-invariant matchers such as MINIMA), structural descriptors (RIFT2, HOPC/CFOG,
  phase congruency), lunar work (MiLOI/CNSFM 2025, JPL's LIMA 2025–26, Geo-LoFTR 2025) and SAC's own
  publications. Give each one's licence (commercial use allowed or not) and CPU run time, and separate
  what we could adopt in ten days from what could land by December.
- **D3.** Data routes that actually work, with product IDs where you can: OHRC↔LROC NAC overlaps;
  OHRC↔TMC-2; TMC-2 or OHRC↔IIRS; real multi-illumination pairs (MiLOI; LROC NAC with incidence
  angles from the ODE REST API); and any official SIH26166 dataset (the PS says "TBD" — watch
  github.com/IMG-PROCESS-SAC and ISSDC/PRADAN). Include preprocessing (ISIS, Ames Stereo Pipeline,
  pds4_tools), georeferencing and download sizes.
- **D4.** Rank the gaps in §2, plus any you find, by effect on a SAC shortlisting decision ×
  feasibility by 27 Sep, and separately by what matters for December. Name the two or three that would
  most change a SAC expert's mind.
- **D5.** Is there evidence on how expert screeners treat honestly reported limitations and negative
  results?

### E. The submission itself

- **E1.** Our deck was written for a college jury that also heard us speak. What should change for
  SAC/ISRO experts reading only the PDF? Go slide by slide within the six-slide template: Title page ·
  Idea title · Technical approach · Feasibility and viability · Impact and benefits · Research and
  references.
- **E2.** Best practice for the idea-title and idea-description fields.
- **E3.** A checklist of disqualifiers and common rejection reasons: template changed, more than six
  slides, not a PDF, team name not matching the portal or containing the institute's name, wrong or
  missing PS ID or team ID, plagiarism, generic AI-written text. (Our title slide still carries the
  college-round team name and ID; the portal name is "LunaXX".)

### F. Plans

- **F1.** 19–30 Sep, day by day, for six people: SIH26166 improvements, the optional second PS, and
  submission by 27 Sep at the latest (portal load, the 500 freeze), with a go/no-go rule for the
  second PS.
- **F2.** October–December: what to build for the finale in priority order, what to prepare in
  advance within the rules, whom to approach as mentors, how to rehearse.

## 5. Output

0. **Bottom line, at most 200 words:** the recommendation on D1; the exact deadline and our
   submit-by date; the three changes that most raise SIH26166's shortlisting odds; the three builds
   that most raise our finale odds.
1. **Rules and mechanics:** Rule | Exact official wording | Source URL | Date accessed | Confidence.
2. **Competition model,** with one table for SIH26166 and the top ten alternatives: PS |
   organisation | ideas on 18 Sep | projected final P10/P50/P90 | freeze risk | fit (a–f) |
   P(shortlist) | person-days | verdict.
3. **The PS-portfolio decision,** with the expected-value arithmetic and the 25 Sep re-check rule.
4. **What shortlisted decks share,** with counts and five exemplar links.
5. **ISRO intelligence** (C3–C5).
6. **Technical gap matrix:** Gap | Why SAC cares | Evidence | Effort | By 27 Sep or by December |
   Role that should own it.
7. **Deck rewrite brief,** slide by slide.
8. **The day-by-day plan (F1) and the finale plan (F2).**
9. **Questions only our SPOC or the logged-in team leader can answer,** worded ready to send.
10. **Sources:** URL, title, date accessed, tier.

If time runs short, deliver 0, 1, 2, 3 and 6 first.
