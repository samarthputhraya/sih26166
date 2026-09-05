# Samrudh — your module, in plain English

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

**You are the exam marker. You never play the game — you score it.**

Everyone else builds things that try to line up images. Your job is to answer one question
honestly: **how well did it actually do?** That sounds simple. It is the hardest job on the team,
and here is why.

To mark an exam you need the answer sheet. But with two real photos of the Moon, **nobody knows
the right answer.** There is no way to look up how far apart they truly are.

So you did the clever thing: **you built puzzles where you already know the answer.**

You take one real image of lunar terrain. You make a second version of it — re-lit as though the
Sun had moved to a different angle — and you shift it by an exact amount that *you chose*. Now
you have two images that look like a genuine hard problem, but **you know the exact answer**,
because you created the puzzle.

Then you let the engine try to solve it, and you measure how far off it was. That measurement is
called `rmse_gt_px` — "how wrong were we, against the truth we know".

**You also keep the logbook.** `evaluation/results_log.csv` is the one file where every
measurement this project has ever made is written down. Rows are only ever **added** — never
edited, never deleted, including the results that made us look bad.

## Part 4 · Why your part is hard (the interesting bit)

**The subtle trap you avoided, and it is worth saying out loud.**

There are two ways to score an alignment, and they sound the same but are not:

- **A fit residual** — "do my own guesses agree with each other?"
- **True error** — "am I actually right?"

You can score beautifully on the first while being catastrophically wrong on the second. That is
exactly what happened on our hardest pair: the matcher's guesses agreed with each other perfectly,
and the answer was about **two kilometres wrong**.

Your scoring function guards against this in a specific way: **it scores the RAW matches, before
any filtering.** If you scored only the matches the system had already decided to keep, you would
be marking the homework after the student rubbed out the wrong answers.

That single decision is why our numbers can be trusted.

## Part 5 · What your part does NOT do

> *"It does not align anything. I never touch the alignment. I build puzzles where the answer is
> known and I score what other people's code produces — that separation is the point. If I both
> built the aligner and marked it, nobody should believe the marks."*

Also be straight that **the ground truth is on rendered images, not real photographs.** That is
not a weakness — it is the only place an exact answer can exist. If we had the true answer for two
real photos, we would not need the project.

## Part 6 · What you personally did

**19 of the 32 commits in `evaluation/` are yours** — the metrics, the logger, the synthetic pair
generator, the shaded-relief renderer, and the tests. Samartha contributed 11, mostly fixes and
the log-integrity test added on Day 7.

You can honestly say: *"the evaluation module is mine."*

## Part 7 · Questions you will be asked

**"How do you know your numbers are right?"**
> "Because I don't measure against an opinion, I measure against a known answer. I build the test
> pairs myself by shifting an image a known amount and re-lighting it, so there is an exact
> correct answer to compare with. And every result goes into a file we only ever add to — including
> the runs that made us look worse."

**"Why is your test data artificial?"**
> "Because that is the only place an exact answer exists. For two real photographs nobody knows the
> true offset — if we did, there would be no problem to solve. We are open about it: the accuracy
> figures come from rendered pairs, and the real-data evidence is that the system caught its own
> failure on a genuine pair."

**"What is the difference between the two accuracy numbers you report?"**
> "One is *do my guesses agree with each other*, the other is *am I actually right*. They can point
> in opposite directions — we have a case where the first looked excellent and the second was two
> kilometres out. We report both and we never mix them up."

**"Has anything ever been deleted from your log?"**
> "One row, and we found it ourselves. It was written by a test — a junk row, not a measurement.
> No real result has ever been removed, and there is now an automatic check that fails if anyone
> tries."

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
