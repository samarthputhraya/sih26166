# The pitch — 3 minutes, and the Q&A behind it

**Written 5 Sep 2026 (Day 7).** The SPOC has confirmed the live demo is **not mandatory**, so the
deck and how you speak to it now carry the entire round. Every figure below is in
`evaluation/results_log.csv`; the deck's own audit table names each row.

Read this with `presentation/DECK_CONTENT.md` open. That file is *what is on the slides*. This
file is *what comes out of your mouth*, which is not the same thing and should not be the same
words.

---

## 1 · The one sentence

> **"A lunar image-registration engine that knows when it is wrong."**

If a judge remembers one thing, it is that. Every part of the pitch either sets it up or proves
it. If you find yourself explaining something that does neither, cut it.

**The audience is faculty who are not domain experts.** They will not adjudicate LoFTR versus
SuperGlue. They are deciding three things: *is this real, do these six understand it, and did
they find something?* Speak to those.

---

## 2 · Who speaks

**Two speakers for the three minutes. Not six.**

Three minutes divided six ways is thirty seconds each — five handovers, no momentum, and it reads
as a group assignment rather than a team. Gate 5 asks that *all six can answer cold*, and that is
tested in **Q&A**, which is where the other four earn the marks.

| Part | Who | Why |
|---|---|---|
| Open, problem, what we built (0:00–1:10) | **Samartha** | owns `core/` and the app; the failure story is his to tell |
| Evidence, honesty, impact, close (1:10–3:00) | **one other** — Saniya if she is comfortable, else Samrudh | the numbers belong to whoever can say them without reading |
| **Q&A — all six** | everyone | see §6; each of you owns your own module's questions |

If your format insists every member speaks, use the five-way split in §5 — but say so in advance
and rehearse the handovers, because that is where a group pitch falls apart.

---

## 3 · The three-minute script

Word counts are set for ~130 words a minute, which is deliberate projected speech — slower than
you talk normally. **Rehearse with a timer. Three minutes means three minutes.**

### 0:00 – 0:30 · Open on the failure, not the problem
*(Slide 2 up. Do not read the slide.)*

> "Two photographs of the same place on the Moon, taken months apart. The Sun has moved, so every
> shadow has moved with it. Standard software aligns images by finding corners and edges — and a
> shadow edge is a corner that moves.
>
> Here is what that costs. On a real pair from our data, the matcher found eighty-eight
> correspondences, fitted a transform, and **reported success.** Against ground truth that
> transform was **about two kilometres wrong** — and nothing it reported would have told you so,
> because match statistics describe the matches. They cannot see the ground."

**Why this opening:** it is concrete, it is surprising, and it makes the rest of the pitch
necessary. Do not open with "lunar image registration is important." Every team opens that way.

> ⚠️ **Two things in this paragraph are load-bearing and were both got wrong in a first draft.**
> **(1)** Say *"reported success"* — the row's `status` is `ok`. Do **not** say its statistical
> checks looked good: the inlier ratio on that row is **0.057**, which looks terrible, and a judge
> who opens the log would falsify you in ten seconds. The deck corrected exactly this wording on
> Day 6; do not reintroduce it.
> **(2)** The error is **~200 px ≈ 2 km**, the true error against ground truth. It is **not**
> 43 km. That figure is `residual_px` × the grid — a *fit residual* converted to metres, which is
> the one thing this project exists to say you must never do. The app itself prints that number
> labelled *"not an accuracy."*

### 0:30 – 1:10 · What we built
*(Slide 3. Point at the flow, do not read the box.)*

> "So we built a registration engine, and then we built the thing that checks it.
>
> The engine removes the lighting before matching — it keeps the *direction* of every edge and
> throws away the brightness — then matches whole patches rather than corners, then discards the
> matches that disagree.
>
> Then the part that is ours. An independent check re-derives the alignment **from the raw pixels,
> and it never looks at a single match.** The image is divided into an eight-by-eight grid and the
> cells vote. Think of it as the difference between marking your own homework and having someone
> check the answer who has not seen your working. Inlier ratio marks its own homework. This does
> not.
>
> The output is not one accuracy number. It is a map: **verified**, **weak**, and **no evidence** —
> and when the pixels contradict the matcher, the system says so and switches method."

**The one line to get exactly right** is *"it never looks at a single match."* That is the whole
contribution. If a judge takes nothing else, take that.

### 1:10 – 2:05 · The evidence
*(Slide 4, then the sun-angle figure.)*

> "Measured, not asserted.
>
> Against classical methods on identical files, at fifteen degrees of sun difference we are
> **2.88 times** more accurate. Past thirty degrees the classical methods mostly stop returning an
> answer at all.
>
> The trust map is calibrated against exact ground truth over two and a half thousand cells. On the
> hard cases, a cell we mark *verified* is **fourteen times** more accurate than a cell we mark
> *no evidence*. That is what makes it a measurement rather than a colour scheme.
>
> And the failure detection itself: **seventy-seven per cent of failures caught, with a zero per
> cent false-alarm rate.** Across twenty-seven registrations that were correct, it never once cried
> wolf — which matters more than the detection rate, because a detector that fires on good data is
> one nobody keeps trusting."

### 2:05 – 2:35 · Where we lose — say it before they ask
*(Stay on slide 4.)*

> "Three things we will say before you ask.
>
> At **zero** degrees of sun difference, classical SIFT beats us — 0.044 against our 0.086. With
> identical lighting there is no illumination problem to solve. Our advantage is illumination
> robustness, and it grows with the sun difference.
>
> Between forty-five and sixty degrees there is a shoulder where we are wrong and do not know it.
> And our detector resolves to about **a hundred and fifty metres** — below that, by construction,
> it cannot see the error.
>
> We know all three because we measured them."

**Deliver this as confidence, not apology.** It is the strongest half-minute in the pitch: it is
what makes a judge believe the two minutes before it. Do not rush it and do not soften it.

### 2:35 – 3:00 · Impact and close
*(Slide 5, then back to slide 2.)*

> "Why it matters. Aligning imagery across epochs and sensors is the prerequisite for hazard
> mapping at a landing site — directly relevant to **LUPEX**. There are already more than two
> hundred OHRC scenes in the ISRO archive; registration turns strips into time series with no new
> spacecraft. And it runs on a laptop, CPU only, on open licences.
>
> Every registration engine gives you one number for the whole image. Ours tells you where to
> believe it — and when not to.
>
> **A lunar image-registration engine that knows when it is wrong.** Thank you."

---

## 4 · The five numbers, and nothing else

Say these five. Every extra number costs you one of them.

| Number | What it is | Where it comes from |
|---|---|---|
| **~2 km** | how wrong a matcher that reported success actually was (~200 px true error) | `pair_04_tierD_native`, ground-truth rows 3 Sep 15:24 |
| **2.88×** | better than best classical at 15° sun difference | Gate 2 criterion 5 |
| **14×** | verified vs no-evidence accuracy, hard cases | `core/reliability_calibration.csv` |
| **77% / 0%** | failure detection, false-alarm rate | `reliability_failure_detection` |
| **150 m** | the floor below which we cannot detect an error | `core/reliability.py` |

**Never say:** *cross-sensor* · *multi-modal* for anything but optical-vs-elevation · the
**62,519×** ratio (it rests on one surviving run — say *"fourteen of fifteen classical runs failed
outright"* instead) · any Tier D residual as an accuracy · a pixel figure without its grid.

---

## 5 · If every member must speak

| Segment | Speaker | Anchor |
|---|---|---|
| Open + problem | Samartha | the 43 km failure |
| The data we used | Rohan | four sources, licences, what we could *not* get |
| The engine | Samartha | pipeline + the independent check |
| How we know it works | Samrudh | ground truth, the sweep, the calibration |
| The comparison | Risheeth | classical baselines on identical files |
| What it unlocks + close | Saniya | LUPEX, 200+ scenes, the one sentence |

Rishabh takes the first change-detection question in Q&A. Handovers must be one sentence, not
"and now I'll hand over to" — say the *link*: *"Rohan will tell you what we had to work with."*

---

## 6 · Gate 5 — all six answer cold

Gate 5 asks each of you five questions about **your own module**: *what problem · why is it hard ·
what does my module do · how do we know it works · what next.* Full detail is in your brief in
`ops/briefs/`. The compressed version:

| | Your module | "How do we know it works" — your strongest answer |
|---|---|---|
| **Samartha** | `core/` — the pipeline and the trust layer | 2,560 cells against exact ground truth; the three states separate 14× on hard cases |
| **Samrudh** | `evaluation/` — ground truth, metrics, the log | every number the team quotes is a row in an append-only file; I can show the row |
| **Risheeth** | `baselines/` — SIFT, ORB, AKAZE | same pairs, byte-identical files, same scoring function as our own method |
| **Rishabh** | `app/change_detection.py` | on the Tier D pair it proposes 183 candidates and the trust gate keeps zero — none reaches a report |
| **Rohan** | `data/` — pairs, provenance, licences | every pair has a PROVENANCE.md that says how to rebuild it from the original product |
| **Saniya** | `presentation/` — the deck | every figure on a slide names the row it came from |

**The question that will catch someone out:** *"what does your module NOT do?"* Have that answer
ready. Rishabh's is the sharpest — *"it finds differences, not changes; on this pair every
candidate was shadow or artefact, and the system says so."*

---

## 7 · When it goes wrong

- **"Show me cross-sensor."** — *"We don't have one, and we say so on the slide. Every real pair we
  own is one OHRC frame cropped twice, or a photograph against an elevation model."* Do not
  improvise past that sentence.
- **A number you cannot place.** — *"That's in our results log; I'd rather show you the row than
  guess."* Never estimate a figure aloud.
- **"Your inlier ratio on that pair was 0.057 — surely that was the warning?"** — *"It tells you
  the pair was hard. It does not tell you the answer is wrong, by how much, or where. Ours does:
  zero of thirty-five measurable regions agreed with that transform. That is the difference
  between a difficulty signal and a correctness measurement."* Say the 0.057 yourself before they
  find it.
- **You are cut short at 90 seconds.** — open, the independent check, 2.88×, close. Drop the
  evidence detail and the impact.
- **A judge disputes the novelty.** — *"Uss and colleagues did per-region accuracy in 2016 and we
  cite them on the references slide. Theirs is a continuous bound for an area-based method. Ours
  is a three-state map over a learned matcher with an explicit* unmeasured *state, and a declared
  fallback. It's a system contribution and we say so."*
- **Silence after you finish.** Let it sit. Do not fill it.
