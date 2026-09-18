# SIH 2026 national round — research report (team LunaXX, PS SIH26166)

**18 Sep 2026 (Day 20), 11:15–12:20 IST.** Answers `RESEARCH_PROMPT.md` in this folder. Written by
Samartha with Claude Code; three capped research agents were used, and every headline claim they
returned was re-checked here before it went in.

Tags: **[OFFICIAL]** SIH/MoE/AICTE/ISRO page or PDF · **[RESULT-LIST]** official shortlist or
result list · **[FIRST-PERSON]** a finalist's or judge's own account · **[SECONDARY]** blog, video,
forum, repo · **[ANALYSIS]** our own computation on official data (method stated) ·
**[INFERENCE]** judgement. No number about our own system appears here unless it is already on the
deck and traced to `evaluation/results_log.csv`.

---

## 0. Bottom line

- **Portfolio (D1): keep SIH26166 as the main entry, and add SIH26227** (MoD, multi-temporal change
  analysis of satellite imagery), staffed by two people who are not on SIH26166's critical path.
  SIH26166 is far more crowded with serious builders than its idea count suggests: **37 public
  GitHub repos under the exact PS ID**, against 29 submitted ideas. SIH26227 has 5 repos, is
  projected to close at ~130–180 ideas, and is judged by a different organisation. Final go/no-go
  on **25 Sep** by the rule in §3.
- **Deadline 30 Sep 2026** [OFFICIAL]. **Submit by 27 Sep.** In 2024, problem statements at our
  level didn't freeze before deadline day, but their counts nearly doubled in the last two days.
- **Top three changes for SIH26166:**
  1. Register **SAC's own benchmark pair** (arXiv:2509.04775 Table 1: OHRC ↔ NAC `M1350459544RE`)
     and report held-out error beside their in-sample RMSE.
  2. Put **TMC-2** into the loop — the PS title names it and at least one competitor already has
     real OHRC↔TMC-2 results.
  3. Export the **registered product and match points** — named PS deliverables, which we compute
     but never write to disk.
- **Top three finale builds:** full-scene Chandrayaan-2 processing with georeferenced output; an
  IIRS optical↔infrared leg; real multi-illumination validation. ISRO ranks all its finalists
  together at one nodal centre, so the demo must impress judges from outside our PS.

## 1. Rules and mechanics

| Rule | Exact wording / evidence | Source | Confidence |
|---|---|---|---|
| Deadline | "The last date for team nomination and idea submission by College SPOC and Team leader on SIH portal is till 30th Sept 2026 only. No request will be entertained after the deadline" | [OFFICIAL] SIH 2026 Guidelines p.10 (sih.gov.in/letters/2026/); all 240 PS rows say "30 September 2026" (sih.gov.in/sih2026PS) | High. **Time of day not stated anywhere** |
| Max 2 PS | "One team can submit Ideas against maximum of 2 Problem Statement only" (same line in 2025) | [OFFICIAL] 2026 and 2025 Guidelines; FAQ "each team can submit only two ideas" | High |
| Freeze | "only 500 ideas will be submitted for a particular PS … the particular PS will get freeze" (2025 cap was **300**) | [OFFICIAL] 2026 vs 2025 Guidelines | High |
| Shortlisted on both | 2023: "these teams will be provided with the option to select only one PS for the grand finale" | [RESULT-LIST] sih.gov.in/sih2023-screening-final-result | High for 2023, assumed for 2026 |
| Fields | Chosen PS or Student Innovation · idea title · idea description · idea presentation (PDF) | [OFFICIAL] 2026 Guidelines p.11 | High |
| Editing | FAQ (SPOC section): "Team & idea details once entered cannot be altered" | [OFFICIAL] sih.gov.in/faqs | **Unknown for the team leader's own upload — check in the portal** |
| Title/description limits, draft save, PDF size | Nothing official found. PDF "25 MB" appears only on Scribd mirrors of the 2025 template | [SECONDARY] | Unknown. Our PDF is 1.1 MB, so size is not a risk |
| Links in the PDF | Not addressed officially. Three of 13 finale-winner decks carried a YouTube or prototype link (§4) | [ANALYSIS] | Allowed in practice |
| Student Innovation vs the cap of 2 | Not stated | — | Unknown — ask the SPOC |
| Finalists per PS | "4-5 teams per problem statement may be selected … [org] isn't obligated to declare a winner" | [OFFICIAL] 2026 Guidelines p.12 | High. 2023 actual: 1,155 SELECTED + 82 wildcard + 45 from waitlist over 231 PSs; SELECTED per PS was 5 on 163 PSs, 3–8 overall; 3 PSs got nobody |
| Team name | "must not contain the name of your institute in any form" | [OFFICIAL] 2026 Guidelines p.9 | High. **Our title slide still says "SNPSU LunaX" / "SNPSU0192"; the portal says LunaXX** |
| Prize | ₹1,50,000 per PS, "ONLY IF that organization likes the idea". **ISRO grades instead** (§5) | [OFFICIAL] | High |
| Deadline history | 2024: 12 Sep → extended to 30 Sep (notices kept in the page source of sih.gov.in and sih.gov.in/faqs), and counts kept rising to ~7 Oct. 2025: 30 Sep | [OFFICIAL] page source; [SECONDARY] | Extensions happen, **but don't plan on one** |
| "Demo video must not be AI-generated" | Found only on college internal-hackathon pages | [SECONDARY] | Not a national rule as far as we can find |
| Finale | 2026: offline at nodal centres, December; up to 2 mentors (≥5 yrs); travel ≤ ₹3,000 per person | [OFFICIAL] | High |

## 2. Competition model

**Is "fewer ideas ⇒ better chance" right?** Partly. The panel shortlists about k = 5 per PS, so
what matters is how many decks are better than ours (B). We're in if B < 5.
- Raw count N matters because more entries mean more strong ones.
- Count is a weak proxy on technical PSs: SIH26166 has **more public repos (37) than submitted
  ideas (29)**. Its builders are unusually serious.
- For **winning**, count doesn't matter: it's you against the other finalists. At ISRO that means
  against all ~50 ISRO finalists (§5).

**Projection method [ANALYSIS]:** for each 2026 PS, take the 25 software PSs of 2024 with the
nearest count on 18 Sep 2024 (Wayback snapshots of sih.gov.in/sih2024PS) and read their final
counts. Capped finals stay in, so the freeze is modelled. Two scenarios:
- **Same growth:** 2026 grows like 2024.
- **Earlier submitting:** 2026 is already ~1.3× 2024's total at this date (6,005 vs 4,570), so
  each 2026 count is divided by 1.31 first.
Snapshots: 6,005 ideas at 11:15 IST and 6,048 at 12:02 (≈57/hour) — too short a gap to trust as a
rate. The 2025 and early-2026 pages are not archived (403 to the Wayback crawler).

| PS | Org | Ideas 18 Sep | Final P10/P50/P90 (earlier) | Final P10/P50/P90 (same growth) | P(freeze) | Public repos | Fit |
|---|---|---|---|---|---|---|---|
| **SIH26166** | ISRO | 29 | 190 / 288 / 423 | 281 / 395 / 500 | 8–16% | **37** | ours |
| **SIH26227** | MoD | 12 | 111 / 131 / 214 | 120 / 177 / 272 | 0 | **5** | high: registration-aware false-change suppression, confidence, offline |
| SIH26013 | MoRD | 4 | 90 / 108 / 132 | 82 / 108 / 132 | 0 | 3 | medium: geo-referencing engine and confidence fit; most of it is GIS vector work |
| SIH26175 | ISRO (SAC) | 12 | 111 / 131 / 214 | 120 / 177 / 272 | 0 | 13 | medium: DEM/rendering skills; same judges as SIH26166, so it barely diversifies |
| SIH26142 | NTRO | 10 | 107 / 130 / 184 | 116 / 148 / 217 | 0 | 14 | medium: needs co-registered LR/HR pairs and uncertainty; GPU training |
| SIH26158 | NTRO | 13 | 116 / 148 / 217 | 120 / 177 / 296 | 0 | 16 | medium: matching for SfM; 3D reconstruction is heavy on CPU |
| SIH26169 | ISRO | 8 | 97 / 126 / 184 | 111 / 131 / 214 | 0 | 11 | low–medium: tracking/simulation |
| SIH26012 | MoRD | 10 | 107 / 130 / 184 | 116 / 148 / 217 | 0 | 10 | low–medium: segmentation of drone imagery |
| SIH26209 | Student Innovation, Space | 17 | 120 / 177 / 296 | 166 / 219 / 322 | 0 | — | open theme, many strong space ideas |
| SIH26167 | ISRO | 53 | 351 / 446 / 500 | 370 / 500 / 500 | 32–60% | 44 | VLM, GPU-heavy; crowded |
| SIH26143 | NTRO | 43 | 296 / 425 / 500 | 367 / 464 / 500 | 24–40% | 37 | crowded |

Repo counts: GitHub search on the exact PS ID, 18 Sep ~12:05 IST. For SIH26166, 56 distinct repos
turn up across four search phrasings.

**What the SIH26166 field looks like [SECONDARY, READMEs read 18 Sep]:**
- **github.com/Fable98/chandrayaan2-crossmatch** reports:
  - real OHRC↔TMC-2 results over 8 Chandrayaan-2 regions;
  - OHRC↔NAC on real calibrated products (CDRs);
  - IIRS co-registration;
  - "quality gates", held-out RMSE, error in metres.
- **github.com/Ashwin0r7/siim-lunar-image-registration** is built around "silent registration
  failure":
  - VERIFIED / REJECTED / INCONCLUSIVE verdicts on real LROC NAC;
  - CPU-only, offline;
  - a registered product with match points already exported.

  **This is the same pitch as our trust layer.** It states it has no Chandrayaan-2 data.
- **github.com/Priyanshu8yadav/sih-2026:**
  - refuses rather than answers when unsure;
  - benchmarks on real OHRC and NAC tiles;
  - reports that OHRC↔NAC needs a map-projected NAC product (or ISIS `cam2map`). Useful for us.

So "knows when it's wrong" is no longer unique on this PS. What is still ours:
- a check that **never sees the matches**, calibrated against exact ground truth (77% of failures
  caught at 0% false alarms, over 2,560 cells);
- the three-state map with *no evidence* as its own state;
- the gate on downstream change detection.

The deck has to say *calibrated*, with the number — not just "refuses".

## 3. PS-portfolio decision

**The arithmetic [INFERENCE — the inputs are judgements, stated so they can be argued with]:**
P(shortlisted) ≈ P(fewer than 5 decks judged better than ours).
- **SIH26166 as the deck stands:** at least 2–3 visible competitors show more real Chandrayaan-2
  evidence, and there are unseen ones → **p₁ ≈ 0.15–0.30**.
- **SIH26166 after §6 items 1–3** (SAC's benchmark pair, TMC-2, export) and a calibrated novelty
  claim → **p₁ ≈ 0.35–0.55**.
- **SIH26227 from two people in eight days:** a working change-analysis prototype on public
  Sentinel-2, strong on false-change suppression and weaker on semantic retrieval, against a field
  of ~5 visible builders → **p₂ ≈ 0.20–0.40**.
- Different organisation, different judges, so treat the two as independent:
  P(at least one) = 1 − (1 − p₁)(1 − p₂).

| | SIH26166 only | + SIH26227 |
|---|---|---|
| Deck as today | 0.15–0.30 | 0.32–0.58 |
| After gap closure | 0.35–0.55 | 0.48–0.73 |

The second PS adds roughly **+15 to +20 points** for about 16 person-days (Rishabh plus one other,
eight days). That's worth it only if it takes nobody from SIH26166's critical path: Rohan (data),
Samartha (pipeline, export), Samrudh (evaluation), Saniya (deck). If both get shortlisted, the 2023
rule says we pick one.
- **Winning pays better on SIH26227:** MoD-style organisations name a per-PS "Winner" (₹1.5 L).
- **ISRO grades across all its PSs:** in 2023 one ₹1 L winner out of 9 PSs.

**Why not the others?**
- **SIH26013:** lowest count, but most of the work is cadastral/GIS.
- **SIH26175:** same SAC judges, so correlated with SIH26166, and ISRO's cross-PS ranking again.
- **SIH26142 and SIH26158:** more builders and GPU-heavy.

**Re-check rule, 25 Sep evening.** Run `python ops/national_round/pull_ps_counts.py`, then submit
SIH26227 only if all three hold:
1. SIH26227's count is at most 0.6 × SIH26166's (0.41 today);
2. its deck shows a real screenshot of our pipeline on Sentinel-2 imagery, not a mock-up;
3. SIH26166's real-data result is already in `results_log.csv`, or has an owner finishing by
   26 Sep.

Otherwise submit SIH26166 alone.

### Student Innovation instead of SIH26227? No (checked 18 Sep, 12:30)

The Student Innovation (SI) software themes are SIH26193–SIH26209: 17 themes, 500 cap each, in the
same public table. The least crowded today:

| Theme | Ideas now | Projected final P50 (earlier / same growth) |
|---|---|---|
| Robotics and Drones (SIH26201) | 8 | 126 / 131 |
| Smart Vehicles (SIH26203) | 12 | 131 / 177 |
| Space Technology (SIH26209) | 17 | 177 / 219 |

For comparison, SIH26227 has 12 ideas, projected 131 / 177.

1. **It takes the same slot.** SI themes carry SIH IDs and 500 caps like any PS, and the form asks
   for a "Chosen problem statement *or* Student Innovation Category". Assume SI is one of the two
   [INFERENCE — ask the SPOC, §9 Q4].
2. **No extra finalist places.** 2023 SI themes shortlisted 4–9 teams each, mostly 5 — the same as
   ordinary PSs [RESULT-LIST]. SI also wins no more often: 1.42 awarded teams per theme in 2024 and
   1.24 in 2025, against 1.83 and 1.00 for MoD [RESULT-LIST].
3. **SI Space would fail for the same reasons as SIH26166.** A space idea built on our lunar engine
   has the same missing real Chandrayaan-2 data, and probably space-minded judges. A second entry
   is only worth it if it wouldn't fail for the same reasons. SIH26227 has different judges (MoD)
   and different data. Sentinel-2 and Landsat multi-date pairs are public and plentiful, so that
   deck can show **real-data** results quickly — exactly what the SIH26166 deck lacks. Two
   near-identical lunar ideas also invite a duplicate-idea objection.
4. **SI means winning twice.** The judges score whether our self-chosen problem matters, as well as
   how we solve it, and open themes draw vision pitches. On a specified PS, the question is whether
   we met the spec — the way this team already works.
5. **SIH26227's text asks for what we already have.** §2.2.3 names "imperfect co-registration",
   "illumination and view-angle differences" and "confidence estimates", and §2.2.7 requires
   offline, local-only operation.
6. **Repo counts don't help for SI.** SI teams name repos after their own ideas, so the 3/1/1
   public repos for SIH26209/26201/26203 undercount their competition.

The one SI idea worth keeping in reserve: **GPS-denied drone localisation**, registering drone
frames to a satellite basemap with the trust gate refusing bad fixes, under Robotics and Drones.
It's independent of ISRO, and our engine fits it. Revisit it only if the SPOC says SI does **not**
count toward the two — and even then only if nobody on SIH26166 or SIH26227 has to be moved to it.

**SIH26227's risk is scope.** Six capabilities are required. The deck should build two properly
(multi-temporal change analysis with false-change suppression and per-change confidence) and show
retrieval as a working baseline: an off-the-shelf remote-sensing image–text model plus a vector
index, with its licence checked first. The rest goes on the plan slide.

## 4. What shortlisted decks share

13 idea-stage decks from **finale winners** (so shortlisted), 2022–2025, from
github.com/Krishna-Techstar/SIH-Resources-and-Winning-PPTs, each rendered and coded by eye
[ANALYSIS]. There is no rejected-deck comparison group, and none of them is an ISRO PS — this is a
survivorship sample.

| Feature | Winners with it |
|---|---|
| Architecture / flow diagram | **13 / 13** |
| Tech stack (logos or list) | 12 / 13 |
| References with real links or papers (six-slide decks) | 8 / 10 |
| Text-heavy (>~80 words/slide) | ~7 / 10 |
| Prototype screenshot or UI mock-up | 3 / 13 |
| Demo video or live prototype link | 3 / 13 (Chanakya 2024, Gryffindors 2025, VardhitRakshak 2025) |
| Measured results from their own work | 1–2 / 13 (Gryffindors: loss and accuracy curves) |
| Comparison table against existing systems | 1 / 13 (Tech Pioneers 2025) |

**Reading [INFERENCE]:** on general PSs a clean template, a diagram and a plausible stack were
enough; measured evidence was rare. **SIH26166 is not a general PS** — its visible field publishes
benchmarks. Our measured-results style is necessary but no longer differentiating. A demo link is
allowed in practice, and **we have no demo video yet.**

Exemplars: Gryffindors 2025 (results plot and prototype link), VardhitRakshak 2025 (demo video,
user flow), Tech Pioneers 2025 (comparison matrix), Expert Chain 2024 (flowchart and cited papers),
Cannon Crew 2024 (clean template use). All five are in that repo.

## 5. ISRO intelligence

**Where and who:**
- ISRO's PSs were judged at **Gujarat Technological University, Ahmedabad** in 2023 (46 finalist
  teams) and 2024 [RESULT-LIST]. 2025 is not shown in the result list.
- SAC publishes the per-PS experts (vedas.sac.gov.in/hi/sih2024.html) [OFFICIAL]. Plan on SAC
  scientists as judges.

**ISRO grades across PSs** [RESULT-LIST]:

| Year | Awards |
|---|---|
| 2023 | 9 PSs: one Winner ₹1,00,000 (SIH1517); 1st runner-up ₹75,000; 2nd runner-up ₹50,000; three Consolations ₹25,000; two Specials ₹5,000; SIH1523 nothing |
| 2024 | 10 PSs: Winner SIH1740 (map-matching, IIT Guwahati); 1st runner-up SIH1736; 2nd runner-up SIH1738; Consolations incl. **SIH1732, the lunar OHRC PS**; Nari Shakti Award; four PSs nothing |
| 2025 | 11 PSs: First "Vasuki" SIH25172; Second SIH25170; Third SIH25169; Consolations; Future Innovators, Girls Achiever and Quantum Frontier awards (amounts not listed) |

**Finale format:**
- 36-hour software edition [OFFICIAL/SECONDARY].
- 2024 winner's account (how-we-won-sih-24-and-survived-it.hashnode.dev): **three unscored
  mentoring rounds and three scored evaluation rounds**; build the prototype *before* the finale,
  and expect to improve only ~5–10% on site [FIRST-PERSON].
- The 20/30/50 round weighting from a Scribd copy of the "Evaluation Guideline for SIH 2023" could
  not be confirmed [SECONDARY, unverified].
- No rule on pre-built code was found. GPU/internet policy at nodal centres: unknown.

**What to take from it [INFERENCE]:**
- The lunar PS was the weak finisher in 2024.
- At GTU our demo is ranked against every ISRO PS, so it has to be legible to SAC scientists
  outside image registration: a mission story (landing-site safety, OHRC mosaics), a live run, and
  honest limits.

## 6. Technical gap matrix (SIH26166)

**What SAC's own paper does** [OFFICIAL/PAPER, arXiv:2509.04775 read in full]: Makharia, Singla,
Amitabh, Dube, Sharma (SAC Signal & Image Processing Area + Manipal University Jaipur).
- **Table 1 pairs:**
  - OHRC `ch2_ohr_ncp_20210401T235737…_d_img_d18` (0.2648 m) ↔ NAC `M1350459544RE` (1.1179 m),
    equatorial;
  - OHRC `ch2_ohr_ncp_20200824T080…_d_img_d18` (0.2586 m) ↔ NAC `M165491149RE` (0.88779 m), polar;
  - IIRS `ch2_iir_nci_20220221T…` / `20230620T…` ↔ the WAC global morphologic map;
  - DFSAR ↔ SELENE.
  - The table wraps the OHRC and IIRS IDs across lines; copy the exact strings from the PDF.
- **RMSE (§4.7.1):** error of the fitted control points after the transform — **in-sample**, in
  NAC-resolution pixels, because OHRC was first resampled to NAC's resolution.
- **Registered product:** the source is warped to the reference, then given the reference's
  coordinate system (§4.5–4.6).
- **Result:** SuperGlue best (OHRC–NAC equatorial 0.62/0.57 px X/Y); only SuperGlue registered the
  polar pair.

A second SAC paper, arXiv:2604.25208 (Singh, Singla, Hemrajani, Dube, Amitabh, Patel, 2026, *"Towards
Seamless Lunar Mosaics: Deep Radiometric Normalization for Cross-Sensor Orbital Imagery Using
Chandrayaan-2 TMC Data"*), says its framework "does not address geometric misalignment or parallax
effects". Its future work is "hybrid frameworks that jointly address both geometric alignment and
radiometric harmonization". The same group names our problem as its next step: cite it on slides
2 and 6.

| # | Gap | Why SAC cares | Evidence | Effort | When | Owner |
|---|---|---|---|---|---|---|
| 1 | No real cross-sensor result | The PS is about Chandrayaan-2 against a lunar reference; competitors have it | Only same-frame OHRC crops (`pair_01`) | Data 2–3 d, run 1 d. Needs map-projected NAC (or ISIS `cam2map`) and the OHRC geolocation grid | **By 27 Sep** — use SAC's Table 1 pair | Rohan, Samartha, Samrudh |
| 2 | TMC-2 never used | In the PS title; a competitor shows 8 regions | 0 rows in `results_log.csv` | PRADAN/chmapbrowse registration (human step) + 2 d | **By 27 Sep** if data lands by 22 Sep | Rohan |
| 3 | No registered product or match-point file | Named PS deliverable; a competitor exports both | `run_all()` returns `H` and `warped` (`core/pipeline.py:387`) but nothing is written | ~1 d: GeoTIFF with the reference's georeferencing + CSV (src_x, src_y, ref_x, ref_y, cell verdict); optional GDAL GCPs | **By 24 Sep** | Samartha |
| 4 | Viewpoint variation unmeasured | One of three named challenges | Nothing in the repo | 1–2 d synthetic perspective sweep with exact ground truth | By 25 Sep | Samrudh |
| 5 | Real sun-angle evidence | "Sun angle invariant" rests on Lambertian renders | Deck slide 4 admits it | LROC NAC pairs with different incidence (ODE REST) 2–3 d; MiLOI downloadability unverified | Partial by 27 Sep, full by Dec | Rohan, Samrudh |
| 6 | Novelty no longer unique | A competitor pitches "silent failure" | §2 | 0.5 d of wording: say *calibrated*, give the number, keep the *no evidence* state | By 24 Sep | Saniya, Samartha |
| 7 | Classical baselines on real data | "2.88×" is synthetic only | Deck admits it | 1 d once pair 1 exists | By 26 Sep | Risheeth |
| 8 | IIRS optical↔infrared | The PS's multi-modal leg | None | MINIMA or structural descriptors (RIFT2/CFOG) + trust layer | December | Samartha, Rishabh |
| 9 | No pyramid for 18–285× | Scale variation | Resampling only | Coarse-to-fine | December | Samartha |
| 10 | Wrong citation on slide 6 | Probably the PS setters' own paper | Deck says "Singla, Patel, Dube et al."; the PDF says Makharia, Singla, Amitabh, Dube, Sharma | 5 min | **Now** | Saniya |

**The two or three that would most change a SAC expert's mind: 1, 2 and 3** — our pipeline on
*their* pair, in *their* instrument set, producing *their* named deliverable.

**Licences for anything new:**
- MASt3R is CC BY-NC-SA — avoid.
- LightGlue + DISK/ALIKED is Apache/BSD (avoid SuperPoint weights).
- RIFT2, XFeat and MINIMA licences are unverified — check the LICENSE file before any use.

## 7. Deck rewrite brief (six-slide template, PDF only)

The college jury heard us speak; SAC reads the PDF cold. Change what's on the slides, not the
template.

1. **Title page:**
   - team name exactly **LunaXX**;
   - the Team ID the portal shows;
   - PS ID as the portal writes it (`presentation/build_deck.py` `TEAM_ID` / `TEAM_NAME`).
2. **Idea title:**
   - lead with the result on SAC's own OHRC↔NAC pair, if gap 1 closes;
   - the trust map moves from the same-frame crop to that real pair;
   - give the novelty as calibrated detection, with its number.
3. **Technical approach:**
   - pipeline figure plus the two outputs (registered GeoTIFF, match-point CSV), with a real
     thumbnail of each;
   - one line on how the 36 hours would be used — R1 scores an execution timeline.
4. **Feasibility:**
   - a PS-requirement checklist: illumination · viewpoint · scale · multi-modal · sub-pixel (grid
     named) · uniform distribution · registered product · match points · metrics;
   - each marked *measured on real data* / *measured on synthetic* / *planned for finale*;
   - keep the honest limits.
5. **Impact:**
   - keep landing-site safety and change detection;
   - point to Chandrayaan-4 site work, which is SAC's own current programme (LPSC 2026 #1198, per
     `ops/PHASE0_RESEARCH_DAY5.md`).
6. **References:**
   - fix the arXiv:2509.04775 authors;
   - add arXiv:2604.25208;
   - add a demo-video link if one is recorded (unlisted YouTube, narrated by us).

Every new number enters through `results_log.csv` first (Invariant 1); run `claim-checker` before
export.

## 8. Plans

**F1 — 19–30 Sep:**

| Day | Work |
|---|---|
| Sat 19 | Samartha logs into the portal and records answers to §9. Team call: decide on SIH26227 staffing. Rohan registers on PRADAN/chmapbrowse and pulls the SAC Table 1 products + TMC-2 over the same site. Saniya fixes the title slide and citation. |
| 20–22 | Samartha: export (gap 3). Rohan: map-project and crop the real pairs. Samrudh: viewpoint sweep. Rishabh (+1): SIH26227 prototype on Sentinel-2. |
| 23–24 | Real-pair runs logged. Risheeth: baselines on the same pairs. Deck v2 text with `[TBD — results_log.csv]` placeholders. |
| 25 | Counts re-pulled; §3 rule applied. Numbers frozen into the log. |
| 26 | Build and export the PDF (PowerPoint on this machine is unlicensed — use Saniya's copy or Print-to-PDF); `claim-checker`; one outside reader. |
| **27** | **Submit.** |
| 28–30 | Buffer only. |

**F2 — October to December (priority order):**
1. Full-scene, tiled Chandrayaan-2 processing on CPU, with georeferenced output and batch mode.
2. IIRS leg.
3. Coarse-to-fine scale.
4. Real multi-illumination validation.
5. A mission-framed demo that runs offline three times in a row (`demo-medic`).
6. Mentors: up to two, ≥5 years' experience; pick one in planetary/remote-sensing imaging.

## 9. Questions only the logged-in team leader or the SPOC can answer

1. Portal: is there a save-as-draft, and can the PDF, title or description be replaced after
   pressing submit?
2. Portal: what are the character limits on the title and description, and the PDF size limit?
3. Portal: what Team ID and team name does the portal show for us? Is "LunaXX" final?
4. SPOC: does a Student Innovation idea count toward our two?
5. SPOC: for 2026, does the team leader upload the idea, or does the SPOC? Is there any
   college-internal deadline before 30 Sep?
6. SPOC: have the internal-hackathon report and the authorisation letter (Annexure A) been uploaded?
   Without them the nomination may not stand.
7. SPOC: is a demo video expected or allowed at the national stage, or was that the college
   round's rule?

## 10. Sources (all accessed 18 Sep 2026)

- [OFFICIAL] sih.gov.in/sih2026PS; sih.gov.in/letters/2026/SIH 2026 Guidelines.pdf; SIH2025-Guidelines-College-SPOC-updated.pdf; sih.gov.in/faqs; sih.gov.in (page source)
- [RESULT-LIST] sih.gov.in/sih2023-screening-final-result; sih.gov.in/sih2023-grand-finale-result; sih.gov.in/sih2024/sih2024-grand-finale-result; sih.gov.in/sih2025/sih2025-grand-finale-result
- [ANALYSIS] web.archive.org snapshots of sih.gov.in/sih2024PS, 18 Sep–18 Nov 2024; `ps_counts_*.csv` in this folder
- [OFFICIAL/PAPER] arxiv.org/abs/2509.04775; arxiv.org/html/2604.25208v1; vedas.sac.gov.in/hi/sih2024.html
- [FIRST-PERSON] how-we-won-sih-24-and-survived-it.hashnode.dev/everything-about-winning-sih-2024
- [SECONDARY] github.com/Fable98/chandrayaan2-crossmatch; github.com/Ashwin0r7/siim-lunar-image-registration; github.com/Priyanshu8yadav/sih-2026; github.com/Krishna-Techstar/SIH-Resources-and-Winning-PPTs; scribd.com/document/712193023 (2023 evaluation guideline); archive.org/details/chandrayaan-2-high-resolution-images-of-the-moon; pradan.issdc.gov.in/ch2; ode.rsl.wustl.edu/moon

**Could not verify:** the portal's draft/edit behaviour and field limits; the 20/30/50 finale
weighting; 2025 ISRO prize amounts and nodal centre; MiLOI's download; any official SIH26166
dataset (none on github.com/IMG-PROCESS-SAC today); the licences of RIFT2, XFeat and MINIMA.
