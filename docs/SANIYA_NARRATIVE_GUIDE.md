# Saniya — Narrative Lead Guide

**Role:** Deck, demo script, Q&A bank, rehearsals — make six people read as one team
**Time:** ~2 hrs/day | **You own presentation quality, format compliance, and the truth of every number**

> Read `00_CANONICAL_FACTS.md` completely. §9 (numbers discipline) is your enforcement power.

---

## 🔴 FIVE THINGS THE OLD GUIDE GOT WRONG

**1. The six slides were the wrong six.** It listed *Problem · Solution · Tech Approach · Results ·
Demo/Application · Future/Team*. Three of those are invented. The official format is different —
§2 below. *"Clarity and detail in the prescribed format"* is a **scored criterion**, so this was
free marks thrown away. It also listed six slides in one place and then added three more later
(Literature Review, Results/Metrics, Future Scope + Team) — nine slides in a six-slide format.

**2. The Q&A bank contained invented results.** *"0.7–1.2px on 10 cross-orbit pairs"*,
*"SIFT: 12 matches, 8px error. Ours: 142 matches, 0.7px"*. Nothing was measured when those were
written, and Rehearsal 3 would have had four people saying them aloud.

**3. It told the team to claim a GPU that doesn't exist.** *"GPU: RTX 3080"* and
*"$0 — local gaming GPU (RTX 3080)"*. There is no RTX 3080 on this team. Samartha's laptop has an
Intel integrated GPU; Rohan has an AMD card 30 km away. **Stating specific false hardware to a
judge is the kind of thing that gets checked.**

**4. Q&A answer 7 was factually false.** *"LROC-LROC cross-orbit is same problem (different
geometry, public data)."* Same sensor is not the same problem as cross-sensor. Corrected in §5.

**5. Impact got one bullet.** Impact and Benefits is a whole official slide and one of the
highest-weighted criteria — and it is structurally the weakest area for a registration project.
It now gets a full day (Day 6).

---

## 🎯 YOUR MISSION

1. A **six-slide deck in the official SIH template**, exactly as prescribed
2. A **3-minute demo script** where **all six people speak**
3. A **Q&A bank** where every answer is true and every number traces to the CSV
4. **Three rehearsals**
5. A **backup video**

You are also the team's **fact-checker**. If a number appears in a slide and not in
`evaluation/results_log.csv`, you delete it. Nobody outranks you on that.

---

## 📅 YOUR 12-DAY PLAN

### DAY 1 — ⚠️ THE TEMPLATE. This blocks the whole deck.

**Download the official SIH 2026 idea-presentation template** from sih.gov.in or your SPOC.
**Open it. Read the actual slide headings. Post them in team chat.**

Expected (from guidance, **not yet confirmed against the file**):

| # | Slide |
|---|---|
| 1 | Problem Statement |
| 2 | Proposed Solution |
| 3 | Technical Approach |
| 4 | **Feasibility and Viability** |
| 5 | **Impact and Benefits** |
| 6 | **Research and References** |

**If the real template differs, the real template wins** — tell everyone immediately, because
Days 2–7 are one slide per day against these headings. Guidance says use the template
**unaltered**: don't add slides, don't rename headings, don't restyle.

**Also on Day 1 — the reading list.** Corrections from the old version:

| Topic | Who | Note |
|---|---|---|
| OHRC instrument spec | You | Use the **ISRO OHRC user guide** Rohan pulls from archive.org — primary source |
| LROC NAC reference | You | |
| Phase congruency (Kovesi) | Samartha | |
| **LoFTR** | Samartha | ⚠️ Old list said **SuperGlue** — we are not using it, its weights are non-commercial |
| MAGSAC++ / USAC | Samartha | |
| Lunar registration survey | Samrudh | |
| **CH-2 OHRC-derived DEM of the Chandrayaan-3 landing site** | Risheeth | ⚠️ Old list called this "Chandrayaan-3 DEM" — **Chandrayaan-3 had no orbiter and no camera that made this.** It's Chandrayaan-2 OHRC imaging the CH-3 *site*. Getting this wrong in front of ISRO is bad. |
| RIFT2 / radiation-invariant features | Risheeth | |
| M3 spectrometer overview | Rishabh | The multi-modal leg |
| SIH26166 full PS text | You | Day 2 |

---

### DAY 2 — Slide 1: Problem Statement

Read the full PS text first. Then write to what it actually says.

- **What:** Chandrayaan-2 images must be aligned to reference imagery to sub-pixel accuracy.
- **Why it's hard — the PS's own three:** illumination variation (sun azimuth/elevation change how
  the surface looks), viewpoint variation, scale variation.
- **The number that makes it land:** OHRC ~28 cm/px, TMC-2 ~5 m/px, IIRS ~80 m/px. **Up to a 285×
  scale ratio between instruments on the same spacecraft.**
- **Why ISRO cares:** mosaic generation, landing-site characterisation, change monitoring, LUPEX
  site selection.

> **Remember who is judging the internal round: faculty, not domain experts.** Lead with the
> picture — the same crater under two lightings, side by side, visibly unmatched. Then the words.
> If Slide 1 needs computer-vision background to follow, it has failed.

---

### DAY 3 — Slide 2: Proposed Solution

The pipeline, as a diagram (Excalidraw or draw.io):

```
Input pair → resample to common GSD → illumination normalisation
           → LoFTR dense matching → MAGSAC++ outlier rejection
           → sub-pixel NCC refinement → 8×8 grid distribution → aligned output + metrics
```

**Name the innovation precisely** — and be careful here, because *novelty* is the
highest-weighted criterion and "we used a pretrained model" is not novel. What is actually ours:

1. **Illumination normalisation before matching**, so features come from structure rather than
   brightness — with an ablation proving how much it contributes on its own (Risheeth's Config 2).
2. **Explicit common-GSD resampling** before matching, because learned matchers degrade past
   ~4–8× and our real ratios reach 285×.
3. **Enforced spatial uniformity** as a first-class constraint, not a side effect — the PS asks for
   it explicitly and almost nobody implements it.
4. **Ground truth from DEM re-rendering**, which lets us measure sun-angle invariance
   quantitatively instead of asserting it.

That list is defensible. "We used LoFTR" is not.

---

### DAY 4 — Slide 3: Technical Approach

Stack, methods, data. **Hardware — say this, and only this:**

> "Runs on a standard laptop, CPU only, no discrete GPU required."

That is true, verifiable, and a genuine deployment virtue. **Do not name a GPU model.**

**Rule for this slide:** no unnamed technique.
- ❌ "we use AI" → ✅ "LoFTR, a detector-free transformer matcher"
- ❌ "image processing" → ✅ "phase congruency illumination normalisation"
- ❌ "public lunar data" → ✅ "Chandrayaan-2 OHRC, LROC NAC, Kaguya TC, Chandrayaan-1 M3"

---

### DAY 5 — Slide 4: Feasibility and Viability

This slide was **entirely missing** from the old plan. It asks: can you actually build it, and does
it hold up?

- **Feasibility:** all data is public and already downloaded; all libraries are open-source and
  permissively licensed; the whole pipeline runs on CPU on a laptop.
- **Licensing, and be specific — this is a real differentiator:** LoFTR is **Apache-2.0**. We
  deliberately rejected SuperPoint because its pretrained weights are **academic/non-commercial
  research only**, which would block operational deployment. Kaguya TC data is **CC0**.
  *Very few student teams will have thought about this, and an ISRO judge will notice.*
- **Risks and mitigations, honestly:** multi-modal matching degrades (quantified, not hidden);
  extreme scale ratios need resampling; shadow-dominated regions remain hard.
- **Viability:** sensor-agnostic by design, so a new instrument is a metadata entry, not a rewrite.

---

### DAY 6 — Slide 5: Impact and Benefits ⭐ GIVE THIS THE WHOLE DAY

**This is our structurally weakest scored area.** Image registration has no user, no beneficiary
count, no cost saving. The old draft gave impact one bullet and 15 seconds. It is a full official
slide and one of the heaviest-weighted criteria.

**Frame impact as what registration unlocks, not what registration is:**

- **Landing-site characterisation.** Aligning high-res imagery across epochs and sensors is a
  prerequisite for hazard mapping. Directly relevant to **LUPEX**, India's next lunar lander
  mission — CH-2 tasking shifted toward polar imaging for exactly this.
- **Change monitoring.** New impacts, and locating landed assets. **Chandrayaan-2's DFSAR imaged
  the Vikram lander after touchdown** — this task is real ISRO work, not a hypothetical.
- **Getting more out of data ISRO already owns.** 200+ OHRC images already sit in the archive.
  Registration is what turns individual strips into mosaics and time series. No new spacecraft.
- **Sovereign tooling.** OHRC is the sharpest operational camera at the Moon — sharper than LROC
  NAC. Indian tooling for Indian data at the highest available resolution.
- **Sensor-agnostic reuse.** The same engine works for Mars, or for Earth-observation
  cross-sensor registration.

**Include a short Future Scope block here** (the old plan had a separate slide for it — there is no
such slide): DEM-assisted orthorectification · polar-region optimisation · onboard deployment.

---

### DAY 7 — Slide 6: Research and References

Also missing from the old plan. Papers and data sources, cited properly. **List the archives with
their licences** — CC0 for Kaguya, ISRO open data, NASA PDS. It demonstrates you understand data
provenance, which is a maturity signal.

---

### DAY 8 — Deck v1 complete

Every slide has content. **Every number is written `[TBD — results_log.csv]`.**

Then do a **numbers audit**: search the deck for every bare decimal. For each one, open
`evaluation/results_log.csv` and confirm it exists there. If it doesn't, replace it with `[TBD]`.
Do this again after Rehearsal 1 and again on Day 12.

> You are the last line of defence against a fabricated number reaching a judge. In the first
> draft, four separate documents carried the invented figure "0.7 px" as if it were measured.

---

### DAY 9 — Demo script (3:00, all six speak)

The old script left **Rishabh silent** for the entire demo and then Gate 5 required him to answer
for his own module cold. Everyone speaks.

```
TIME  | SPEAKER  | CONTENT                                                      | SCREEN
------|----------|--------------------------------------------------------------|--------
0:00  | Saniya   | "Team [Name], SIH26166 for ISRO. Chandrayaan-2 carries three | Slide 1
      |          |  optical instruments that differ in resolution by up to      |
      |          |  285 times, and the same crater looks completely different   |
      |          |  under different sunlight. Aligning them is unsolved."       |
0:25  | Rohan    | "Our data is real and public: Chandrayaan-2 OHRC at 28 cm,   | Slide 1
      |          |  LROC NAC, Kaguya, and Chandrayaan-1's infrared             |
      |          |  spectrometer. Four missions, every file documented."        |
0:45  | Samartha | "Two things before matching: resample to a common ground     | Slide 2
      |          |  scale, and normalise illumination so features come from     |
      |          |  structure. Then dense matching, outlier rejection,          |
      |          |  sub-pixel refinement, and a grid constraint for coverage."  |
1:05  | Samartha | LIVE DEMO — align a pair, swipe view, metrics panel          | UI
1:45  | Samrudh  | "How we know it works: DEM-rendered ground truth where we    | UI/Slide
      |          |  know the true answer, and held-out residuals on real pairs. |
      |          |  Those are different things and we don't conflate them."     |
2:05  | Risheeth | "Classical methods, and where they break — look at the red   | Gallery
      |          |  lines. And we ran SIFT *with* our preprocessing, so you can |
      |          |  see what the preprocessing contributes by itself."          |
2:30  | Rishabh  | CHANGE DETECTION — [Chandrayaan-3 landing site if available] | UI
2:50  | Saniya   | "This is infrastructure for landing-site characterisation,   | Slide 5
      |          |  change monitoring and LUPEX. It runs on a laptop with no    |
      |          |  GPU. Thank you — questions?"                                |
```

**Time it. Cut words, not speakers.** Every person speaking once is what Gate 5 is really testing.

---

### DAY 10 — Q&A bank (20 questions)

**Every answer below is true as written. Bracketed values are filled from the CSV, not guessed.**

**Technical**
1. *"Why not train your own model?"* — Samartha: "Twelve days and no GPU cluster. Pretrained
   LoFTR plus our illumination preprocessing beats what we could train from scratch."
2. *"How does phase congruency help with sun angle?"* — Samartha: "It responds to structure —
   phase coherence across frequencies — rather than brightness. A crater rim gives the same
   signature whether lit from the left or the right."
3. *"What's your accuracy on real data?"* — Samrudh: **"Two different numbers, deliberately. On
   DEM-rendered and synthetic pairs, where we know the true transform, accuracy is [rmse_gt_px].
   On real pairs there's no ground truth, so we hold out twenty percent of matches and report a
   residual of [residual_px] — that's a residual, not accuracy, and we don't claim otherwise."**
4. *"Why LoFTR and not SuperPoint?"* — Samartha: "Two reasons. LoFTR is detector-free and works in
   smooth maria where corner detectors find nothing. And SuperPoint's pretrained weights are
   academic and non-commercial only — that would block operational use. LoFTR is Apache-2.0."
5. *"How do you handle a 20× scale difference?"* — Samartha: **"We resample both images to a common
   ground sample distance using the mission metadata, then match coarse-to-fine on a pyramid.
   Learned matchers degrade past roughly four to eight times on their own, so we don't rely on
   that — it's an explicit preprocessing step."**
6. *"SIFT reaches 0.2 px in papers. Why is yours higher?"* — Risheeth: "Those are same-sensor,
   similar-illumination pairs. Ours are cross-sensor with large sun-angle differences."
7. *"Did you actually get Chandrayaan-2 data?"* — Rohan: **"Yes. ISRO's OHRC products are publicly
   available and we're using them. We also registered on ISRO's own portal. And because the PS
   asks for a *generic* solution, we validated across four missions."**
8. *"Is LROC-to-LROC cross-sensor?"* — Rohan: **"No. Same sensor. That's our sun-angle test and we
   label it that way. Our cross-sensor work is Chandrayaan-2 against LROC and against Kaguya."**
   ← **the trap question. The old guide's answer to this was false.**
9. *"Where's the multi-modal part?"* — Samartha: "Optical against infrared — Chandrayaan-1's M3
   spectrometer, same modality class as CH-2's IIRS. It's harder and our numbers are worse there;
   we report by how much."
10. *"How does change detection avoid shadow false positives?"* — Rishabh: "Shape elongation,
    intensity direction, and alignment with the sun-azimuth difference from the metadata. It's
    heuristic — properly you'd predict shadows from a DEM."
11. *"How do you know your metric is right?"* — Samrudh: "We hand-checked one pair: picked three
    craters manually, computed the offset ourselves, compared to the harness."
12. *"What's your worst result?"* — whoever owns that tier. **Know it. Say it.**

**Process / team**
13. *"What did YOU do?"* — each person, 30 seconds, in their own words.
14. *"How did you split the work?"* — Saniya: "One critical path and five independent modules,
    each with a written spec the night before, so nobody ever waits."
15. *"What if Samartha were unavailable?"* — Samartha: "Samrudh and Rishabh paired with me on the
    pipeline and the UI on three occasions. They can debug both."
16. *"How do you know it's not overfitted?"* — Samrudh: "Nothing is trained. The matcher is
    pretrained and frozen; we tune no parameters on the evaluation pairs."

**Impact / curveballs**
17. *"How would ISRO use this?"* — Saniya: "Mosaic generation, landing-site characterisation for
    LUPEX, and change monitoring — Chandrayaan-2's radar was used to locate the Vikram lander."
18. *"What hardware does it need?"* — Samartha: **"This laptop. CPU only, no discrete GPU."**
19. *"What did it cost?"* — Saniya: **"Nothing. All data is public, all libraries are open-source,
    and it runs on hardware we already had."**
20. *"One thing you'd fix with more time?"* — each person has their own honest answer.

---

### DAY 11 — Rehearsals 1 & 2, and the video

**Rehearsal 1 (1 hr):** full 3-minute run plus 5 minutes of Q&A. Time every section. Record on a
phone. Note stumbles — don't fix mid-run.

**Rehearsal 2 (1 hr):** fix the stumbles. Then **cold Q&A**: fire 10 random questions, each person
answers unaided. Note who struggles.

**Backup video, after Rehearsal 2** (not before — the old plan recorded it on Day 11 and then let
the code change on Days 12–13, so the video would have shown a UI that no longer existed):
- Phone on a tripod, landscape, laptop screen clearly visible
- **Wifi off, cached data** — the video must show the real offline demo
- Upload to Drive **and keep a local copy on a phone.** A Drive link is useless if the venue wifi
  is down, which is the exact scenario the video exists for.

---

### DAY 12 — Rehearsal 3 + Gate 5

**Rehearsal 3:** full run plus all 20 questions.

**Gate 5** — every member answers cold, no notes:
1. What problem are we solving?
2. Why is it hard?
3. What does *your* module do?
4. How do we know it works?
5. What would you do next?

**Anyone who can't answer #3 or #4 about their own work is a fail.** Extra prep, not a pass.

**Final numbers audit.** Every figure in the deck, script and Q&A bank against
`evaluation/results_log.csv`. **Any `[TBD]` still unfilled gets deleted, not guessed.**

Deck final in the official template. Print copies.

---

## 📁 YOUR FILES

```
presentation/
├── deck.pptx            # official template, 6 slides, unaltered
├── demo_script.md       # timed, all six speak
├── qa_bank.md           # 20 Q&As, each assigned by name
├── demo_video.mp4       # recorded after Rehearsal 2, offline, local copy on a phone
├── paper_summaries.md
└── rehearsal_log.md
```

---

## 💡 TIPS

| Situation | What to do |
|---|---|
| A number isn't ready | Write `[TBD]`. **Never a plausible placeholder** — placeholders become quoted facts. |
| Someone quotes a number you can't find in the CSV | Stop them. Every time. This is your job. |
| Someone says "cross-sensor" about LROC↔LROC | Correct it on the spot, in every rehearsal. |
| Deck looks cluttered | Template colours only. One font. One diagram style. Less text. |
| Script runs over | Cut words, never speakers. All six must speak. |
| Someone freezes in Q&A | Practise the handoff: "Let me add —" then pass back. Rehearse it twice. |
| Judges are non-technical | Lead every slide with the picture. The words support the image. |
| Asked about team composition | Six members, one female member, all from this institution. Confirmed. |
| Tempted to add a seventh slide | Don't. The format is scored. |

---

## ✅ DELIVERABLES

- [ ] Official template **downloaded and its real headings confirmed to the team on Day 1**
- [ ] `deck.pptx` — 6 slides, official headings, unaltered template
- [ ] Every number traced to `results_log.csv`; zero unfilled `[TBD]` at Day 12
- [ ] `demo_script.md` — 3:00, **all six speak**
- [ ] `qa_bank.md` — 20 answers, all true, each assigned by name
- [ ] `demo_video.mp4` — offline, post-Rehearsal-2, local copy on a phone
- [ ] 3 rehearsals logged
- [ ] Gate 5: all six answer cold
- [ ] Three numbers audits done (Day 8, post-Rehearsal 1, Day 12)

---

## 🗣️ YOUR OWN LINES

> **Opening:** "We're Team [Name], solving ISRO's SIH26166 — aligning Chandrayaan-2 imagery across
> sensors, sun angles and scales that differ by up to 285 times."
>
> **Closing:** "This is infrastructure. It's what has to work before you can build a mosaic, verify
> a landing site, or monitor a region over time — and it runs on a laptop with no GPU. Thank you.
> We'd love your questions."

---

## 📞 ESCALATION

| Problem | Ask |
|---|---|
| Numbers for slides | Samrudh (metrics) / Risheeth (baselines) |
| UI screenshots | Samartha (Day 10) |
| Failure gallery | Risheeth (Day 6) |
| Data provenance wording | Rohan |
| Template questions | SPOC / sih.gov.in |
| Someone is silent for two days | Samartha — you raise it on Day 4 and Day 7 |

---

**You're not "the presentation person." You're the coherence person and the fact-checker.** Great
technical work loses to a messy story — and a good story dies the instant a judge catches one
invented number. Protect both.
