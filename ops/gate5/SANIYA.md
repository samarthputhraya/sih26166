# Saniya — your module, in plain English

**Read this once, slowly. It is written for someone who knows nothing about space, cameras or
code.** By the end you will understand what our project does, what your part does, why your part
is hard, and what to say when a judge asks. Nothing here needs to be memorised word for word —
if you *understand* it, the words come out fine.

**The round is 9 September. Gate 5 (8 Sep) is a rehearsal where all six of us answer questions
about our own part, cold.**

---

## Part 1 · The whole project, in 60 seconds

*(This section is identical in all six cards on purpose. If we describe the project six different
ways, that is what the judge remembers.)*

Imagine two photographs of the **same patch of the Moon**, taken months apart by a spacecraft.

You would think lining them up would be easy — same place, same rocks. It is not, and here is
why: **the Sun has moved.** Every shadow is in a different place, a different length, a different
direction. A crater that had a dark half in the first photo has a bright half in the second.

Computers line up photos by looking for **corners and edges** — sharp features they can spot in
both pictures. The problem is that **the edge of a shadow looks exactly like the edge of a rock**,
and shadow edges *move between photos*. So the computer confidently matches a shadow edge in photo
one to a different shadow edge in photo two, and the alignment comes out wrong.

**Worse: it comes out wrong without telling you.** The software reports a confident, healthy-looking
result. It is measuring how well its own guesses agree with each other — not whether they are
right.

So our project has two halves:

1. **An engine** that lines the two photos up *despite* the Sun having moved — by throwing away
   brightness before matching, and matching whole patches instead of corners.
2. **The part that is genuinely ours** — a second, independent check that works out the alignment
   **again, straight from the pixels, without ever looking at the first method's answer.** It
   splits the image into an 8×8 grid — 64 squares — and each square votes on whether the
   alignment looks right there.

The result is not one score for the whole image. It is a **map**:

| Label | Meaning |
|---|---|
| **verified** | we checked here, two independent methods agree, you can trust this |
| **weak** | we checked here and something does not add up |
| **no evidence** | we could not measure here at all — this is *not* a bad score, it is an honest blank |

And if the pixel check flatly contradicts the matcher, the system **says so out loud and switches
to a different method**, instead of quietly reporting a confident wrong answer.

**The one sentence for the whole project:**

> ### "A lunar image-registration engine that knows when it is wrong."

**Why that matters:** if a scientist uses a misaligned pair to decide a landing site is safe,
nobody finds out until it is too late. A system that admits *"I could not verify this corner"* is
more useful than one that is confidently wrong.

---

## Part 2 · Words you will hear, in plain English

| Word | What it actually means |
|---|---|
| **registration** | lining two images up on top of each other. That is all it means. |
| **a pair** | two images of the same place that we are lining up |
| **the transform** | the instruction that says "shift this photo 40 across and 25 down, and rotate it a bit" |
| **sub-pixel** | accurate to *less than one dot* of the image — very precise |
| **ground truth** | the real, known answer. Only possible when we made the puzzle ourselves. |
| **GSD / m per pixel** | how much ground one dot of the image covers. 60 m/px = each dot is 60 metres across. |
| **the log** | `evaluation/results_log.csv` — the notebook where every measurement is written and never erased |

---

## Part 3 · Your part, in plain English

**You turn six days of measurements into three minutes a non-expert can judge — without any number
losing its paper trail on the way.**

The judges are faculty. They are not going to read our code and they will not adjudicate which
matching algorithm is best. They are deciding three things: **is this real, do these six understand
it, and did they find something?**

The deck and the pitch are how those three questions get answered. Since the SPOC confirmed the
live demo is **not mandatory**, this is now the highest-leverage job left in the project.

Your detailed working guide is **`ops/SANIYA_DECK_AND_PITCH_GUIDE.md`** — that is the step-by-step
document. This card is the shorter thing: what to say if a judge asks *you* about your part.

## Part 4 · Why your part is hard (the interesting bit)

**Because the temptation is always to make a number sound better than it is.**

Every figure on our slides has to trace back to a specific row of the logbook. Not "roughly this",
not "about that" — the actual row. The deck has an audit table at the bottom that maps each number
to where it came from.

That discipline caught two real problems this week, both on our most important slide: two headline
figures turned out to have **no row behind them**. Both were correct numbers, but one of them lived
only in a working file that gets wiped and rewritten every time we re-run part of the analysis. If
nobody had checked, our best slide would have rested on evidence that could vanish without warning.

The other hard part is **compression without distortion**. Cutting a paragraph to a bullet is easy.
Cutting it without quietly overstating the claim is not.

## Part 5 · What your part does NOT do

> *"It does not compute anything. Not one number on a slide is typed in by hand — the deck is built
> from an audited content file by a script, precisely so that a figure cannot drift between the
> measurement and the slide. If a number is wrong, it is wrong upstream in the measurement, and I
> can show you which row it came from."*

## Part 6 · What you personally did

**Be straightforward here.** The deck content was written on Day 6 by Samartha, and the build
script that puts it into the official template is his. You are taking the presentation on now: the
portal metadata, the quality pass, the export, and delivering the second half of the pitch.

**The honest sentence:**
> *"The deck's content was drafted by Samartha with the evidence file open, because every figure has
> to name the row it came from. I own the presentation — the review, the checking, and I am
> presenting it. If you want the derivation of any number on any slide, I can show you the row."*

Then **be the person who can actually do that.** Open `presentation/DECK_CONTENT.md`, find the
audit table near the bottom, and go through it once so that when someone points at a figure you
know where it lives. That single hour is what makes the sentence above true.

## Part 7 · Questions you will be asked

**"Who made the presentation?"**
> "I own it. The content was drafted with the evidence file open because every figure has to trace
> to a logged row — that is a rule in this project, not a preference. I checked it, I built it, and
> I can show you the source of any number on it."

**"Why is there no live demo?"**
> "We have one and it works — it is a browser app that runs offline on a laptop with no graphics
> card. Our SPOC confirmed the demo is not mandatory, so we chose to spend the three minutes on the
> finding rather than on a screen recording. We are happy to show it if you would like."

**"What is the single most important thing on these slides?"**
> "That the matcher can be confidently wrong and our system catches it. On one real pair the
> matcher reported success and was about two kilometres out — and the system detected that, refused
> to use the answer, and said so. Everything else on the deck supports that one claim."

**"How do you know these numbers are right?"**
> "Because none of them were typed onto a slide by a person. The deck is generated from a content
> file, every figure names the row of our append-only logbook it came from, and there is an audit
> table that maps them. I can open any one of them right now."

---

## The three rules that apply to everyone

**1 · Never say a number that is not in the log.**
Every figure we quote lives in `evaluation/results_log.csv`. If you are not sure, say *"I would
have to check the row"* — which is a strong answer, not a weak one. This project once carried an
invented number through four documents, which is exactly why the rule exists.

**2 · Three words are banned unless they are literally true.**
- **"cross-sensor"** = two *different cameras*. **We do not have this. Never say it.**
- **"multi-modal"** = genuinely different *kinds* of imaging (a photo vs an elevation model).
  We have exactly one such pair. Two ordinary cameras are **not** multi-modal.
- **"sub-pixel"** must always be followed by *of which image*, and the metres.

A judge from the Space Applications Centre will know precisely what these mean. Misusing one is
the fastest way to lose the room.

**3 · If you do not know, say so — then hand it over.**

> *"That is outside my part — Samartha owns that. My understanding is [one sentence]. He can give
> you the exact answer."*

**This scores better than guessing.** A team that routes a question to the right person looks like
a team. A person who bluffs and gets caught costs the whole group. Judges have seen a hundred
students bluff; they have seen very few say "I don't know, but here's who does."

---

## The question that catches people out

> ### "What does your part NOT do?"

Almost nobody prepares for this, and it is the one that separates people who did the work from
people who memorised a script. **Your answer is in Part 5 above. Learn that one properly.**

Knowing the limits of your own work is the strongest possible signal that the work is real.
