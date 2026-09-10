# Round 2 — the presentation, word for word

**Friday 11 September. Round 2 starts at 1:00 PM, for teams shortlisted at 12:30.
All six of us must be present. Formal: white shirt, black trousers.**

Round 1 already scored the *content* (criteria F1–F8) from the PDF, with nobody presenting.
Round 2 scores only two things:

- **F9 — Presentation & Communication:** clarity, pitch effectiveness, Q&A handling.
- **F10 — Collaboration & Teamwork:** team dynamics, problem-solving approach.

So Round 2 is not about having better content. It is about **how six people carry content that
is already on the page.** Everything below is built for those two criteria and nothing else.

> **Ask the SPOC one thing before 1 PM: how long do we get?** The schedule says "1:00 PM
> onwards" and gives no duration. **Decide your length before you walk in, not while speaking.**
>
> | Slot | What you give | Runs |
> |---|---|---|
> | 8 min or more | everything below, ⟨angle brackets⟩ included | **7:01** |
> | 5–7 min | everything below **except** the ⟨angle brackets⟩ | **5:57** |
> | 3 min | §8's three-minute cut | 3:00 |
> | cut short on the day | §8's ninety-second cut | 1:30 |
>
> **Anything in ⟨angle brackets⟩ is droppable.** Those passages were chosen so that every story
> and every headline number survives the cut — what goes is only material the slides already
> carry. All six people speak in every version except the ninety-second one.

---

## 1 · The one idea

If a judge remembers one sentence, it must be this:

> ### "A lunar image-registration engine that knows when it is wrong."

Every segment either sets that up or proves it. If you find yourself saying something that does
neither, cut it mid-sentence and move on. Nobody will notice. They will notice you running long.

**The audience is faculty, not domain experts.** They are deciding three things: *is this real,
do these six understand it, and did they find something?* Speak to those three, not to the
algorithm.

---

## 2 · Why we are not doing one slide per person

Five content slides do not divide by six, and slide-by-slide handover reads as six people taking
turns reading aloud — which loses F9. But two speakers with four standing silent loses F10, and
the schedule requires all six of us present.

**So each person owns one claim, not one slide.** The deck stays on whatever slide supports
whoever is speaking. Samartha speaks twice because he owns the core; that reads as a lead, not as
someone hogging.

| # | Who | Time | Words | Slide | The claim they own |
|---|---|---|---|---|---|
| 1 | **Samartha** | 0:00–0:53 | 115 | 2 | The problem — opened on the failure |
| 2 | **Rohan** | 0:56–1:55 | 127 | 2 | The chain of custody — free data, nothing to procure |
| 3 | **Samartha** | 1:58–3:04 | 142 | 3 | The engine, and the check that is ours |
| 4 | **Samrudh** | 3:07–4:09 | 135 | 4 | The exam marker — how we know it works |
| 5 | **Risheeth** | 4:12–5:08 | 122 | 4 (figure) | The control group — and the law it reveals |
| 6 | **Rishabh** | 5:11–5:58 | 101 | 5 | Shadow or crater — what the gate protects |
| 7 | **Saniya** | 6:01–7:01 | 129 | 5 → 2 | Impact, and the close |

**Total spoken: 7 min 01 s**, plus ~3 s per handover — measured from the word counts above at 130 words per minute, not estimated.

Word counts and times are **measured from the prose below** at 130 words a minute — deliberately
slower than you talk normally — not estimated by hand. Rehearse with a timer on the table.
The times in this table include the ⟨optional⟩ passages; drop those and the whole thing is 5:57.

---

## 3 · The scripts

Read your own section. You do not need anyone else's. **Do not memorise word for word** — learn
the shape and the one line marked 🔴, and let the rest come out in your own words.

**⟨Angle brackets⟩ mean: say this if you have the time, skip it if you don't.** Decide as a team
before you start, not mid-sentence. Every story and every headline number sits *outside* the
brackets, so the short version still has all of them.

---

### 1 · SAMARTHA — the opening (0:00–0:53)

**On screen:** slide 2. **Do not read the slide.** Stand to the side of it, not in front.

> "Two photographs of the same place on the Moon, months apart. The Sun has moved, so every
> shadow has moved with it.
>
> Standard alignment software finds corners and edges. A shadow edge is a corner that moves.
>
> Here is what that costs. On a real pair from our data, the software found eighty-eight matching
> points, fitted an alignment, and **reported success**. Against an answer we already knew, it was
> **over two kilometres wrong**.
>
> Nothing it reported would have told you — because match statistics describe the matches.
> **They cannot see the ground.**
>
> So we built the thing that can, and measured how often it works.
>
> Rohan will tell you what we had to work with."

🔴 **"Reported success."** Say exactly that. Do **not** say its statistics looked good: that row
logs inlier count 5 and ratio 0.057, which look terrible, and a judge who opens the log would
falsify you in ten seconds. If asked, volunteer those two numbers yourself — they prove the pair
was hard, not that we are wrong.

**Why this opening:** it is concrete, surprising, and it makes everything after it necessary.
Do **not** open with "lunar image registration is important." Every team opens that way.

---

### 2 · ROHAN — the data (0:56–1:55)

**Cue:** *"...we had to work with."* **On screen:** still slide 2.

> "My job is the chain of custody: where every image came from, and whether you can trust it
> arrived unchanged.
>
> Four sources, all public and all free — Chandrayaan-2's OHRC camera, NASA's LROC, Japan's
> Kaguya, and NASA's LOLA elevation model. They run from thirty centimetres per pixel down to
> sixty metres — **over two hundred times apart. That is the scale problem, in our own data.**
>
> ⟨Every pair carries a file recording exactly how to rebuild it from the original product —
> window, coordinates, licence. Nothing here is a screenshot somebody made once and lost.⟩
>
> So there is no data to buy and no permission to wait for. **ISRO could run this on its own
> archive tomorrow.**
>
> Samartha will show you what the engine does with it."

🔴 **"No data to buy, no permission to wait for."** That is the line that earns marks — it is
feasibility, cost and deployability in nine words, and nobody else in the pitch says it.

⚠️ **The scale span is 0.28 m/px to 60 m/px — over 200×, not 285×.** 285× is OHRC against **IIRS**,
which is in the problem statement's title but is **not** one of our four sources. Samartha may say
285× on slide 3 because that is the instrument fact from `docs/00_CANONICAL_FACTS.md` §4; you are
describing *the data we actually hold*, and LOLA is 60 m/px. Do not merge the two numbers.

**On the cross-sensor gap: do not volunteer it, never deny it.** We have no genuine cross-sensor
pair, it is stated on slide 4, and if a judge asks you answer straight: *"We don't have one, and
it's on the slide. Every real pair we own is either one OHRC frame cropped twice, or a photograph
against an elevation model."* What changed is only that we no longer spend spoken airtime on it —
the story of five failed attempts needs domain context to read as rigour, and faculty judges do
not have that context. Source if you need it: `data/DATASET_CARD.md`.

**Your "does not do":** *"It does not verify that the space agency's own metadata is correct. I
record what the product label says, and where I measured something myself I say so. What I refuse
to do is fill a blank with a plausible guess."*

---

### 3 · SAMARTHA — the engine (1:58–3:04)

**Cue:** *"...what the engine does with it."* **On screen:** slide 3. Point at the
flow, left to right. Do not read the boxes.

> "Three steps, then the part that is ours.
>
> ⟨Both images go onto the same scale — one camera sees thirty centimetres per pixel, another
> eighty metres.⟩
>
> Then we remove the lighting: we keep the *direction* of every edge and throw the brightness
> away, so a shadow moving does not change what we match on.
>
> Then a learned matcher finds corresponding points, and we discard the ones that disagree.
>
> Now the part that is ours. An independent check re-derives the alignment **from the raw pixels
> alone. It never looks at a single match.** The frame is split into an eight-by-eight grid, and
> the cells vote.
>
> It is the difference between marking your own homework — and having someone check the answer
> who has not seen your working.
>
> When the pixels contradict the matcher, it refuses its own result. Samrudh measured whether
> that works."

🔴 **"It never looks at a single match."** That one clause is the entire contribution. Slow down
on it. If a judge takes nothing else, take that.

**Your "does not do":** *"It cannot see an error smaller than about 150 metres. The area check
reads an integer correlation peak against a two-pixel threshold, so an error up to about two and a
half reference pixels is indistinguishable from zero, by construction. That is also why our
45-to-60-degree blind spot exists — it is a predicted gap, not a surprise."*

---

### 4 · SAMRUDH — how we know (3:07–4:09)

**Cue:** *"...Samrudh measured whether that works."* **On screen:** slide 4.

> "I am the exam marker. I never touch the alignment — I set the questions and I mark the
> answers, because if I did both, nobody should believe the marks.
>
> So I build pairs where I already know the true answer exactly, and sweep the Sun across them.
>
> At fifteen degrees of Sun difference the answer comes back **0.0856 pixels** off — about five
> metres on a sixty-metre grid.
>
> ⟨And the trust label is calibrated, not a colour: across two and a half thousand regions, the
> ones marked *verified* sit within **7.4 metres**, ninety-nine per cent of them under half a
> pixel.⟩
>
> The detector itself catches **seventy-seven per cent of failures at a zero per cent false-alarm
> rate** — across every registration that was actually correct, it never once cried wolf.
>
> Risheeth ran the comparison."

🔴 **Always say the grid with the pixel.** "0.0856 pixels" alone is meaningless and, on a real
pair, would be a fit residual rather than an accuracy. Say *"on a sixty-metre grid"* or *"which is
five metres"* every single time.

**Why zero false alarms matters more than 77%:** a detector that fires on good data is one nobody
keeps trusting. Detection rate is adjustable by threshold; the false-alarm rate is the one that
decides whether an operator believes the amber regions. Say that if asked.

**Your "does not do":** *"It does not align anything. I never touch the alignment. I build puzzles
where the answer is known and I score what other people's code produces — that separation is the
point. If I both built the aligner and marked it, nobody should believe the marks."*

---

### 5 · RISHEETH — the comparison (4:12–5:08)

**Cue:** *"...Risheeth ran the comparison."* **On screen:** slide 4, hand on the
chart.

> "I am the control group. My job is to make our own result falsifiable: same pairs,
> byte-identical files, the same scoring function — the only thing that changes is the method.
>
> At fifteen degrees of Sun difference we are **2.88 times** more accurate than the best of SIFT,
> ORB and AKAZE. ⟨At ninety degrees, **fourteen of the fifteen standard runs came back with no
> answer to score at all.**⟩
>
> And the pattern matters more than any single number. With identical lighting the standard tools
> are perfectly good — there is no lighting problem to solve. **The further the Sun moves, the
> further ahead we get.** That is exactly the axis the problem statement is about.
>
> Rishabh will show you what that protects."

🔴 **"The further the Sun moves, the further ahead we get."** Land that line. It states the
contribution as a law rather than as an exception, and it ties straight to the words in the
problem statement's own title.

**If a judge asks where you lose, answer immediately and without flinching:** *"At zero degrees
of Sun difference SIFT beats us — 0.044 pixels against our 0.086. With identical lighting there is
no lighting problem to solve, which is exactly why our advantage grows with the Sun angle."* It is
on slide 4 either way. We simply no longer spend spoken airtime volunteering it.

**Never say the 62,519× ratio.** It is arithmetically true and rests on a single surviving run.
Say *"fourteen of fifteen classical runs failed outright"* instead.

**Your "does not do":** *"It does not prove we are better in general. It proves we are better on
these specific pairs, at these specific Sun angles, scored this specific way — and it also shows
where we lose."*

---

### 6 · RISHABH — what it protects (5:11–5:58)

**Cue:** *"...show you what that protects."* **On screen:** slide 5.

> "A shadow that moved is a difference. A new crater is a change. My detector cannot tell them
> apart — it compares pixels, it does not model sunlight. So it does not get to decide on its own.
>
> On the pair the system rejected, it proposed **one hundred and eighty-three** candidate changes.
> The trust gate passed **none** — five rejected outright, a hundred and seventy-eight in regions
> where we have no measurement at all.
>
> ⟨Every one of those would have been a false discovery in somebody's report.⟩ Not one got out.
>
> Saniya will tell you why that matters beyond our laptop."

🔴 **"One hundred and eighty-three proposed, none passed."** That is the most concrete proof on
the slide that the trust layer does something. Land it and pause.

**Your "does not do" — the best one on the team:** *"It finds **differences**, not **changes**.
Those are not the same thing. A shadow that moved is a difference. A new crater is a change. My
detector cannot tell them apart on its own — it is image comparison, not a physics model of
sunlight. That is exactly why its output goes through the gate."*

**If asked about the bug you found:** be straight. On Day 6 you found your own module was scaling
both images by their combined brightest value, which crushed the optical image to nothing on a
multi-modal pair — it reported 1 candidate instead of 183. You found it, fixed it, and pinned it
with a test that feeds the same pixels through both paths and requires the same answer. **Finding
your own bug and saying so is a strength, not an admission.**

---

### 7 · SANIYA — impact and close (6:01–7:01)

**Cue:** *"...why that matters beyond our laptop."* **On screen:** slide 5, then go **back to
slide 2** for the final sentence.

> "When Chandrayaan-2's lander went silent, Chandrayaan-2's own radar was used to find it on the
> surface. Locating anything on the Moon means comparing pictures of the same ground, before and
> after — and that comparison is only ever as good as the alignment underneath it.
>
> That is the work this enables: finding what changed, and deciding where the next lander can
> safely touch down. **LUPEX** is next.
>
> ⟨It runs on an ordinary laptop, CPU only, on open licences — and turns imagery ISRO already
> holds into time series, with no new spacecraft.⟩
>
> Every registration tool we found gives you one number for the whole image.
>
> *(back to slide 2)*
>
> Ours tells you **where** to believe it — and when not to.
>
> **A lunar image-registration engine that knows when it is wrong.**
>
> Thank you."

🔴 **Careful with the Vikram line.** Chandrayaan-2's DFSAR is *radar*, and **we do not use
it** — say that ISRO's own orbiter was used to locate the lander, never that we did it or that our
engine was involved. It is there to show the class of task is real ISRO work, not a hypothetical.
Source: `docs/SANIYA_NARRATIVE_GUIDE.md`. If asked "did you use DFSAR?", the answer is a flat no.

🔴 **Say the title sentence last, and then stop.** Do not add "that's all from our side" or "any
questions". Stop, and let the silence sit. It reads as confidence and it invites the Q&A on your
terms.

**Your "does not do":** *"It does not compute anything. Not one number on a slide is typed by
hand — the deck is built from an audited content file by a script, precisely so a figure cannot
drift between the measurement and the slide."*

---

## 4 · Handover choreography — this is what F10 actually scores

Four rules. They are worth more marks than any sentence in the script.

1. **A handover is a link, never an announcement.** ❌ "Now I'll hand over to Rohan." ✅ "Rohan
   will tell you what we actually had to work with." The next person's *subject* is the handover.
2. **Move before you speak, not while you speak.** The next speaker steps forward on the previous
   person's last clause, so there is no gap and no shuffle.
3. **Nobody looks at the screen while someone else is talking.** Look at the speaker or at the
   judges. Six people staring at a projector reads as six people who have not rehearsed.
4. **One person owns the clicker for the whole pitch** — Samartha. Speakers do not advance their
   own slides; it fragments the rhythm and someone always fumbles it.

**Where to stand:** speaker slightly left of the screen, the other five in a loose line behind and
to the side — not a rigid row, not clustered in a corner. Nobody with their back to a judge.

---

## 5 · Q&A — routing is the test

> **The person who owns the module answers. Nobody answers for someone else's module.**

One person answering everything reads as one person having done everything — which is exactly
what F10 is looking for and exactly how to lose it.

If a question lands on the wrong person, hand it over in one clause and stop talking:
*"That's Samrudh's — he built the ground truth."*

| Topic a judge raises | Answers |
|---|---|
| The pipeline, the trust layer, why it works, the 150 m floor | **Samartha** |
| Ground truth, calibration, metrics, the evidence log | **Samrudh** |
| SIFT / ORB / AKAZE, the comparison, where we lose | **Risheeth** |
| Change detection, the 183 → 0 gate | **Rishabh** |
| Where the data came from, licences, what we could not get | **Rohan** |
| The deck, the numbers on it, how it was built | **Saniya** |
| "How much did AI write?" | **Samartha** — see §7 |

### The three answers to have cold

**"Show me a cross-sensor result."** → *Rohan.* "We don't have one, and we say so on the slide.
Every real pair we own is either one OHRC frame cropped twice, or a photograph against an
elevation model. What we validate is Sun-angle invariance against exact ground truth, and where in
the frame an alignment can be trusted."

**"Isn't this just the inlier ratio with a colour map?"** → *Samartha.* "No. On that pair the
inlier consensus held — and every match was wrong. Our verdict comes from a test that never sees
the matches. And 'no evidence' is a separate state, not a low score: a region with no inliers is
unmeasured, and painting it red or green would both be fabrications."

**"Your inlier ratio there was 0.057 — surely that was the warning?"** → *Samartha.* "It tells you
the pair was hard. It doesn't tell you the answer is wrong, by how much, or where. Ours does: zero
of thirty-five measurable regions agreed with that transform. That's the difference between a
difficulty signal and a correctness measurement." **Say the 0.057 yourself before they find it.**

The full bank is `ops/QA_ANSWERS.md` — nine more, each with its row.

### The three-layer rule — this is what stops you getting stuck

For **every** question:

1. **One sentence, no jargon.** Then *stop*.
2. Only if they push: **one number, with its unit and its grid.**
3. Only if they push again: **"I can show you the row."** Offer it; don't dump it.

Most judges stop at layer 1. Volunteering layers 2 and 3 unprompted is how a good answer becomes a
lost minute — and lost minutes are F9.

### When you don't know

> **"We didn't measure that. What we did measure is —"**

Never improvise a number. Never estimate aloud. A team that says "we didn't measure that" once is
believed about everything else; a team caught inventing a figure is finished.

---

## 6 · Never say these

| Never | Say instead |
|---|---|
| "cross-sensor" as something we have | "we don't have one, and it's on the slide" |
| "multi-modal" for anything but optical ↔ elevation | name the two things: "a photograph against an elevation model" |
| a pixel figure with no grid | "0.0856 pixels — five metres on a sixty-metre grid" |
| the 62,519× ratio | "fourteen of fifteen classical runs failed outright" |
| "we use AI" | "LoFTR, a detector-free transformer matcher" |
| "it always catches it" | "77% at a 120-metre threshold, with zero false alarms" |
| a fit residual as an accuracy | "that's a residual, not an accuracy — here's the accuracy" |
| a GPU model name | "CPU only, no discrete GPU" |

---

## 7 · If a judge asks about AI

There is **no ban** on using AI tools to build. The rules require the work to be your own and
require you to be able to explain and defend it. The one hard prohibition is on AI-generated
demonstration *videos* and narration — we have none.

**Samartha answers, in one breath, without defensiveness:**

> "We used AI the way we'd use any tool — writing code, drafting text. The engine is ours and the
> numbers are ours: the deck is built by a script in our repository that reads our own results
> log, so every figure on it is a run we measured. Ask me about any number on any slide and I'll
> tell you which row it came from."

Then stop. Do not elaborate. **The one thing that would actually hurt us is claiming we wrote
something we didn't, or not being able to explain a slide.**

---

## 8 · Cut-downs — decide before you walk in

**If you get 3 minutes** — drop segments 2 and 6. Rohan and Rishabh earn their marks in Q&A
instead, and Samartha adds one clause: *"...all public data, four sources, every pair reproducible
from its original product."*

| Samartha | 0:00–0:50 | the failure |
| Samartha | 0:50–1:40 | the engine + the check |
| Samrudh | 1:40–2:15 | how we know |
| Risheeth | 2:15–2:40 | 2.88×, and where we lose |
| Saniya | 2:40–3:00 | impact + close |

**If you are cut to 90 seconds** — Samartha does the failure and the independent check; Samrudh
says 77% at zero false alarms; Saniya closes on the one sentence. Three speakers, nothing else.

**If you get 8–10 minutes** — do **not** add content. Give each person the same script more
slowly, pause after each 🔴 line, and let Q&A take the rest. Padding is how a good pitch dies.

---

## 9 · Rehearsal — tonight and tomorrow morning

**Tonight, 25 minutes.** Each person reads only their own section, twice, aloud, standing.
Then the drill that matters: **explain your module to someone outside the team in 60 seconds with
no jargon.** If they can repeat it back, you're ready. That is what `ops/gate5/<YOUR NAME>.md` was
written for.

**Tomorrow morning, 20 minutes, once.**

1. Full run with a timer. Do not stop for mistakes — you need the real length.
2. Handovers only: just the last clause and the first clause of each pair, five times through.
   This is the highest-value ten minutes available to you.
3. Q&A round-robin: one person plays judge and fires the questions in §5 out of order. The rule is
   that the **wrong** person must hand it to the right one within one clause.

**Do not rehearse the full pitch more than twice tomorrow.** Over-rehearsed reads as recited, and
recited loses F9.

---

## 10 · When it goes wrong

- **You blank.** Say the last thing you were sure of, then move to your 🔴 line. Nobody knows your
  script.
- **A judge interrupts mid-segment.** Answer it, then say *"— and that leads to the point I was
  making"* and continue. Do not restart.
- **Someone overruns.** The next speaker starts anyway on the handover cue. Never negotiate timing
  in front of judges.
- **The projector fails.** Keep talking. Every segment above works without the slides; only
  Risheeth's needs the chart, and he can describe it: *"the classical line climbs off the top of
  the chart past thirty degrees; ours stays flat."*
- **A number is challenged.** *"That's in our results log — I'd rather show you the row than
  guess."*
- **Silence after Saniya finishes.** Let it sit. Do not fill it.

---

## 11 · The five numbers, and nothing else

Every extra number you say costs you one of these.

| Number | What it is | Who says it |
|---|---|---|
| **over 2 km** | how wrong a matcher that reported success actually was | Samartha |
| **2.88×** | more accurate than the best classical, at 15° Sun difference | Risheeth |
| **77% / 0%** | failures caught / false-alarm rate, over 2,560 regions | Samrudh |
| **183 → 0** | change candidates proposed / passed by the trust gate | Rishabh |
| **150 m** | the floor below which the check cannot see an error | Samartha, if asked |

Everything on the slides traces to a row in `evaluation/results_log.csv`. If you cannot place a
number, do not say it.
