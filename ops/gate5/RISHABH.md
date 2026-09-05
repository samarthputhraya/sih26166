# Rishabh — your module, in plain English

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

**You play spot-the-difference — and your headline result is that you found nothing, which is the
right answer.**

Once two photos of the same place are lined up on top of each other, the obvious next question is:
**has anything changed?** A new crater. A landslide. A lander that was not there before.

Your code compares the two aligned images and marks every region that looks different. It sorts
what it finds into simple buckets:

| Label | Meaning |
|---|---|
| **new bright** | this area got noticeably brighter |
| **disappeared** | this area got noticeably darker |
| **shadow?** | long and thin — probably a shadow that moved, not a real change |
| **uncertain** | different, but we cannot say what kind |

## Part 4 · Why your part is hard (the interesting bit)

**Because on the Moon, almost nothing actually changes — but almost everything *looks* different.**

There is no weather, no plants, no cities. Between two photos months apart, the real surface is
essentially identical. And yet the two pictures look wildly different, for two reasons:

1. **The Sun moved**, so every shadow moved. A shadow moving is not a change in the ground.
2. **The alignment is never perfect**, and a tiny misalignment makes every crater rim look like it
   gained a bright edge on one side.

So nearly every "difference" you detect is a **false alarm**. That is not a flaw in your code — it
is the nature of the problem, and **being able to say so precisely is your strongest card.**

**Your real result, and say it with confidence:** on our genuine optical-versus-elevation pair,
your detector proposed **183 candidate changes**. The trust map then checked where each one sat:
**zero** were kept, 5 were rejected because they were in unreliable areas, and **178 were in areas
the system could not verify at all**. So **none of them reached a report.**

That is the whole project working exactly as designed. A naive tool would have reported 183
discoveries on the Moon. Ours reported none, and explained why.

## Part 5 · What your part does NOT do

> *"It finds **differences**, not **changes**. Those are not the same thing. A shadow that moved is
> a difference. A new crater is a change. My detector cannot tell them apart on its own — it is
> simple image comparison, not a physics model of sunlight. That is exactly why its output is
> filtered by the trust map before anyone would act on it."*

**This is the best "what it does not do" answer on the team.** It shows you understand the boundary
of your own work, which is the thing judges are actually testing.

Also be straight: **you found a bug in your own module on Day 6 and it was a real one.** The code
scaled both images by their combined brightest value. On the pair where one image peaked at 37,488
and the other at 2,040, that squashed the second image almost flat, so nothing could exceed the
threshold and it reported just 1 candidate instead of 183. You fixed it, and there are now 7 tests
that stop it coming back. **Finding and fixing your own bug is a good story, not a bad one.**

## Part 6 · What you personally did

`app/change_detection.py` is yours — you wrote it and you have the commits on it. You also wrote
its documentation and recorded the honest limitation analysis in the module README, including
counting your own false positives.

You can honestly say: *"the change detection module is mine."*

## Part 7 · Questions you will be asked

**"Did you find any real changes on the Moon?"**
> "No — and that is the correct answer for this data. On our real pair the detector proposed 183
> candidates and the trust layer let none of them through. Every one was in a region where the
> alignment could not be verified, or was a shadow effect. A tool that reported 183 lunar
> discoveries would be wrong 183 times."

**"So is your module useless?"**
> "The opposite. It is the consumer that proves the trust map is worth having. Without the map you
> would have a list of 183 things to investigate. With it you have zero, plus a clear statement of
> why — and that is the difference between a result and a rumour."

**"How would you improve it?"**
> "A shadow filter that uses the Sun's actual position from the image metadata — we know the Sun
> angle for both images, so we can predict where shadows should fall and discount those regions.
> After that, predicting shadows from the elevation model itself."

**"Why do you report an area in square metres?"**
> "So it means something physical. A region 50 dots across means nothing on its own; the same
> region at 60 metres per dot is 3 kilometres wide. We only print the area when we actually know
> the scale of the image."

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
