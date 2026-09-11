# Round 2 — one presenter, seven minutes

**Friday 11 September, 1:00 PM. Format changed on the day: one person presents the whole deck,
hard cap seven minutes.** This file replaces the six-speaker split in `ops/ROUND2_SCRIPT.md` for
the talk itself. Everything else in that file — Q&A routing by module owner, the never-say table,
the AI answer — still stands.

Every figure below is on a slide and traces to a row in `evaluation/results_log.csv`; the table in
§5 names the row. Nothing new was measured for this script.

---

## 1 · What the seven minutes have to do

The judges are faculty, not domain experts. In seven minutes they need three things, in this order:

1. **Context** — what the Moon does to a photograph, and why ISRO cares.
2. **The need** — what the problem statement asks for, and the failure that makes it urgent.
3. **The solution** — what we built, how we know it works, and what it is for.

One idea carries all three. If they remember a single sentence, it is:

> ### "A lunar image-registration engine that knows when it is wrong."

Say it once at the very end and then stop. Do not preview it at the start; the failure story
earns it.

**Teamwork still scores (F10), even with one voice.** The script says how six people split the
work — who built the engine, who built the exam, who ran the control — in one breath, where it is
evidence rather than a roll call. Do not add names or a team slide.

---

## 2 · Timing

Measured from the words below at 130 words a minute, which is deliberate projected speech, plus
two seconds per slide change. Rehearse once with a timer against this table; if you are ahead of
the clock, slow down rather than add.

| At this cue | Clock (full) | Clock (⟨brackets⟩ dropped) |
|---|---|---|
| Click to slide 2, "Two photographs" | 0:10 | 0:10 |
| Click to slide 3, "So we built an engine" | 1:46 | 1:46 |
| Click to slide 4, "How do we know?" | 3:36 | 3:30 |
| Click to slide 5, "Why does this matter?" | 5:17 | 5:05 |
| Click to slide 6, "Our references" | 6:12 | 6:00 |
| Last word | **6:41** | **6:29** |

Spoken words: **844** in full, **818** with the two ⟨angle-bracket⟩ passages dropped. At 130
words a minute that is 6:41 or 6:29 including the clicks — nineteen to thirty-one seconds of
margin under the cap, before the pauses you will add. At a natural 140 words a minute it is about
6:15.

**Decide before you stand up whether the ⟨angle-bracket⟩ passages are in or out.** Every headline
number and every story sits outside the brackets, so nothing is lost either way. Never decide
mid-sentence. **If the slide-4 click lands after 3:45 on the clock, the brackets are out from
there on.**

---

## 3 · The script

Spoken text is in the quoted blocks. Everything else is a cue for you and is not said aloud.
**Learn the shape and the five 🔴 lines, not the words.** If a sentence comes out differently in
your own voice, that is better, not worse.

---

### SLIDE 1 · Title — ten seconds, no more

*Stand slightly to the left of the screen. Clicker in your hand. Look at the judges, not the slide.*

> Good afternoon. We're SNPSU LunaX, and this is what six of us built for ISRO's lunar image
> correspondence problem.

**[click → slide 2]**

---

### SLIDE 2 · Context, then the need

*The trust map is on screen. Do not explain it yet — it is the picture the whole talk walks
towards. Speak to the room.*

> Two photographs of the same patch of the Moon, months apart. Same craters, same ridges, but the
> Sun has moved. There's no atmosphere up there, so shadows are pitch black and razor sharp, and
> every one of them has moved. To a computer, those two pictures no longer look like the same
> place.

> That matters, because almost everything ISRO does with lunar imagery starts by lining two images
> up: landing sites, fresh craters, stitching strips into maps. And the problem statement spans
> OHRC at twenty-eight centimetres per pixel to IIRS at eighty metres, in infrared: nearly three
> hundred times apart in scale, under different Sun angles. ISRO wants one engine for all of it,
> sub-pixel accurate, evenly spread, with a metric to prove it.

*Slow down here. This is the hook.*

> Here's the catch. Standard software aligns images by finding corners and edges, and a shadow
> edge is a corner that moves. On a real pair of ours, a state-of-the-art matcher found
> eighty-eight matching points, fitted an alignment, and reported success. Against an answer we
> already knew, it was over two kilometres wrong. Nothing it reported would have told you,
> because match statistics describe the matches. 🔴 They cannot see the ground.

*Pause. Two full seconds.*

> That one failure is why our project exists.

**[click → slide 3]**

🔴 **"Reported success"** — say exactly that. The row's status is `ok`. Do **not** say its
statistics looked good: the same row logs 5 inliers and an inlier ratio of 0.057, which look
terrible. If asked, say those two numbers yourself; they prove the pair was hard, not that we are
wrong.

---

### SLIDE 3 · The solution

*Point along the flowchart, left to right, as you name the steps. Do not read the boxes.*

> So we built an engine, and then the thing that checks it.

> The engine is this flow. Both images go onto a common scale. We strip the lighting out, keeping
> the direction of every edge and throwing the brightness away, so a moving shadow doesn't change
> what we match on. Then a learned matcher, LoFTR, finds corresponding points across the whole
> image, and a robust estimator discards the ones that disagree. ⟨Those steps are standard, and we
> cite the people who did them first.⟩

*Now change gear. Step towards the judges. This is the contribution.*

> Now the part that is ours. An independent check re-derives the alignment from the raw pixels
> alone. 🔴 It never looks at a single match. We split the frame into an eight-by-eight grid, and
> each cell asks: laid over the reference, do the pixels agree here? The cells vote. It's the
> difference between marking your own homework, and having someone check the answer who never saw
> your working.

> So the output isn't one number. It's a map: verified, weak, or no evidence, because we won't
> colour a region we didn't measure. And when the pixels contradict the matcher, the system rejects
> its own result, falls back to a coarser method, and says so.

> That's what happened on the pair I described. The matcher said success; zero of thirty-five
> measurable cells agreed. The system threw it out and reported 231 metres, give or take 216,
> instead of a confident answer two kilometres out.

**[click → slide 4]**

⚠️ Illumination normalisation and common-scale resampling are **preprocessing in the
problem-setters' own 2025 paper** (arXiv 2509.04775). Never present them as our innovation. The
bracketed sentence acknowledges it; if you drop the bracket, be ready to say it in Q&A.

---

### SLIDE 4 · How we know

*Hand towards the chart. The curve does the talking; you narrate it.*

> How do we know? We split the job so nobody marked their own homework: one of us built the
> aligner, another built the exam, pairs where the true alignment is known exactly, and a third
> ran the classical methods on the same files.

> At fifteen degrees of Sun difference our error is 0.0856 pixels, about five metres on a
> sixty-metre grid, with the whole frame covered: 2.88 times more accurate than the best classical
> method on identical files.

> But the pattern matters more than the number. With no lighting change, classical methods
> actually beat us, because there's no lighting problem to solve. 🔴 The further the Sun moves,
> the further ahead we get. Past forty-five degrees, fourteen of fifteen classical runs return no
> answer at all. That is the axis ISRO's title is about.

> And the check itself: it caught seventy-seven per cent of failures at a zero per cent
> false-alarm rate. On every registration that was actually correct, it never once cried wolf.

*Deliver the next block as confidence, not apology. It is what makes them believe the last minute.*

> Where it breaks, before you ask: between forty-five and sixty degrees it's wrong and doesn't
> know it, and it can't see an error under about a hundred and fifty metres, by construction.
> ⟨It's calibrated on rendered pairs; we don't yet hold a genuine cross-sensor pair.⟩ Each has a
> fix on this slide.

**[click → slide 5]**

🔴 **Always say the grid with the pixel.** "0.0856 pixels" alone means nothing. It is always
"about five metres on a sixty-metre grid." If asked for the 0° numbers: SIFT 0.044 px, ours 0.086.

---

### SLIDE 5 · Why it matters

*The calibration chart is on screen. You do not need to narrate it; if asked, it is the
99%-within-half-a-pixel figure in §5 and §6.*

> Why does this matter? Three reasons.

> First, landing, for missions like LUPEX. A lander needs a map of rocks and slopes, and that map
> is only as good as the alignment underneath. With our system, every part of the map says whether
> it can be trusted, so a bad alignment never sneaks into a landing decision.

> Second, finding changes on the Moon. On that bad pair, our change finder flagged a hundred and
> eighty-three possible changes. 🔴 Our trust check blocked every single one, because the
> alignment underneath them couldn't be trusted.

> Third, cost. It's free, open-source, and runs offline on an ordinary laptop. And it works on
> pictures ISRO already has. No new spacecraft needed.

**[click → slide 6]**

---

### SLIDE 6 · References — one breath, then back to slide 2

> Our references are here, and every number I've said is a row in our results log, including the
> ones where we lose.

**[click → slide 2]**

*Stop moving. Look at the judges. Slower than feels natural.*

> Every registration tool we found gives you one number for the whole image. Ours tells you where
> to believe it, and when not to.

> 🔴 A lunar image-registration engine that knows when it is wrong.

> Thank you.

*Then stop. No "that's all from our side", no "any questions". Let the silence sit; it reads as
confidence and it opens the Q&A on your terms.*

---

## 4 · If time goes wrong

**Running long at the slide-4 click** (later than the clock in §2): drop both ⟨brackets⟩ and, on
slide 5, skip the "Third, cost" paragraph and say "Two reasons" instead (cost is printed on the
slide). Saves about twenty-five
seconds.

**Cut to four minutes by the organisers:** slide 2 in full · slide 3 without the engine paragraph
(*"Three steps put the images on a common scale, remove the lighting, and match; now the part
that is ours…"*) · slide 4 down to 2.88×, "the further the Sun moves", 77% at zero false alarms,
and the 150-metre floor · slide 5 only the "Second, finding changes" paragraph · close.

**Cut to ninety seconds:** the failure story, "it never looks at a single match", 77% at zero
false alarms, the last sentence.

**Projector dies:** keep going. Only slide 4 needs the picture, and the chart is one sentence:
*"the classical line climbs off the top of the chart past thirty degrees; ours stays flat."*

**You blank:** say the last thing you were sure of, then go to the next 🔴 line. Nobody has the
script.

**A judge interrupts:** answer in one sentence, then *"— which is the point I was coming to,"* and
continue. Do not restart.

---

## 5 · Every number you say, and where it lives

| You say | It is | Row in `evaluation/results_log.csv` |
|---|---|---|
| 28 cm · 80 m · nearly 300× | OHRC, IIRS; OHRC↔IIRS = 285× (TMC-2 is ~5 m/px if asked) | instrument facts, `docs/00_CANONICAL_FACTS.md` §4 — not a measurement |
| 88 matching points · reported success | `n_matches` 88, `inlier_count` 5, ratio 0.057, `status` ok | `pair_04_tierD_native`, `ours_loftr+subpixel`, 3 Sep 15:36 |
| more than two kilometres | true error 239–273 px at 9.37 m/px = 2.2–2.6 km | `pair_04_tierD_native`, `ours_loftr`, 3 Sep 15:24 |
| zero of thirty-five cells | area check: 0% of 35 measurable cells agree → contradicted | same row as 88 |
| 231 m ± 216 m | fallback translation (+9,−23) px; quadrant disagreement up to 23 px | `fft_phase_correlation (fallback)`, 3 Sep 15:36 |
| 0.0856 px · five metres · whole frame | median of five shifts at 15°; 0.0856 × 60 m; coverage 1.00 | `ours_loftr+subpixel`, `d_azimuth=15deg` |
| 2.88× | SIFT 0.2466 px ÷ 0.0856 | `SIFT`, `d_azimuth=15deg`, notes `GATE 2 CRITERION 5` |
| classical beats us at 0° | SIFT 0.044 px vs ours 0.086 (medians) | same families, `d_azimuth=0deg` |
| past 45°, 14 of 15 classical runs fail | at 60°, 90°, 120° and 180°: one scoreable run in fifteen, each hundreds to thousands of px wrong | `SIFT`/`ORB`/`AKAZE`, `d_azimuth=60…180deg` |
| 77% at 0% false alarms | 120 m threshold: 10/13 failures caught, 0/27 good pairs flagged; 40 pairs, 2,560 cells | `reliability_failure_detection`, 5 Sep |
| 45–60° blind · 150 m floor | 142.7 m at 60° undetected; integer peak vs 2 px threshold | `synthetic_d060_*`; KNOWN LIMIT note on the row above |
| *(slide 5 chart, not spoken)* 99% within half a pixel · 7.4 m | verified cells, sun difference ≤ 30°: median 0.123 px = 7.4 m, 99.0% under 0.5 px, 817 cells | `reliability_calibration_envelope`, 5 Sep |
| 183 flagged · all blocked | 5 rejected, 178 unassessable | `change_detection_absdiff+reliability_gate`, 3 Sep 19:47 |

If a judge asks for a number that is not in this table: **"We didn't measure that. What we did
measure is —"** Never estimate aloud.

---

## 6 · Q&A — the answers to have cold

If the judges take questions from the whole team, route by module owner exactly as
`ops/ROUND2_SCRIPT.md` §5 says. If they take questions only from the presenter, these eight cover
what a faculty panel asks. One sentence first; a number only if pushed; "I can show you the row"
only if pushed again.

**"What does 'verified' actually promise?"**
"Something measured, inside the range we claim. Up to thirty degrees of Sun difference, regions we
mark verified have a median true error of 0.123 pixels — 7.4 metres on a sixty-metre grid — with
ninety-nine per cent under half a pixel, over 817 regions. That is the chart on slide 5. Outside
that range it degrades, and we show the whole curve rather than the average."

**"What was the pair that went two kilometres wrong?"**
"A Kaguya Terrain Camera photograph against a shaded-relief image rendered from NASA's LOLA
elevation model, at the photograph's own Sun geometry. It's our one genuine multi-modal pair —
optical against elevation — and the matcher that failed on it was our own matching stage, before
the check. That's the point: the check is what caught it."

**"Isn't the trust map just the inlier ratio with colours?"**
"No. On that pair the matches agreed with each other and every one of them was wrong. Our verdict
comes from a test that never sees the matches. And 'no evidence' is a separate state, not a low
score — painting an unmeasured region red or green would both be fabrications."

**"Show me a cross-sensor result."**
"We don't have one, and it's on slide 4. Every real pair we own is either one OHRC frame cropped
twice, or a photograph against an elevation model. What we validate is Sun-angle invariance
against exact ground truth, and where in the frame an alignment can be trusted. The next step is
OHRC against LROC NAC."

**"Your synthetic pairs — are they realistic?"**
"They are rendered from a real lunar elevation model with the Sun moved in known steps, so the true
alignment is exact. They are an illumination test, not a shadow test: the renderer has no cast
shadows. That is why the next calibration is MiLOI, a public set of 321 real multi-illumination
LROC pairs."

**"The first steps of your pipeline — aren't those known?"**
"Yes. Illumination normalisation and common-scale resampling are preprocessing in the
problem-setters' own 2025 paper, and we cite it. What is ours is the independent check, the
three-state map with an explicit unmeasured state, the declared fallback, and the calibration on
lunar data. It's a system contribution, and we say so."

**"How much of this did AI write?"**
"We used AI the way we'd use any tool — writing code, drafting text. The engine is ours and the
numbers are ours: the deck is built by a script in our repository that reads our own results log,
so every figure on it is a run we measured. Ask me about any number and I'll tell you which row it
came from."

**"Where does it lose?"**
"Three places, all on the slide. With identical lighting SIFT beats us, 0.044 pixels to our
0.086. Between forty-five and sixty degrees of Sun difference we are wrong without knowing it. And
below about a hundred and fifty metres the check cannot see an error at all — that floor is by
construction, an integer correlation peak against a two-pixel threshold, and a sub-pixel peak fit
removes it."

**Never say:** *cross-sensor* as something we have · *multi-modal* for anything but optical against
elevation · a pixel figure without its grid and metres · the 62,519× ratio · "it always catches
it" · a GPU model name · that Chandrayaan-2's radar has anything to do with us.

---

## 7 · Delivery

- **Pace.** 130 words a minute is slower than you talk. The 🔴 lines slower still, with a beat
  after each. Silence after a strong line is not dead air; it is the line landing.
- **Eyes.** On the judges, not the screen. Glance at a slide only when you point at it.
- **Hands.** Point at the flow on slide 3 and the chart on slide 4. Otherwise still.
- **Numbers.** Say them as words — "two point eight eight times", "seventy-seven per cent" — so
  they sound owned, not read.
- **Rehearsal.** Twice, standing, with a timer, not more. Over-rehearsed reads as recited and
  recited loses F9. The second run is for the five 🔴 lines and the six clicks only.
