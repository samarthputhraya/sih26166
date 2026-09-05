# Risheeth — your module, in plain English

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

**You are the control group. You run the old way, so we can prove the new way is better.**

Any team can say "our method is good". That means nothing on its own. Good *compared to what?*

Your job is to run the **standard, well-known methods** that engineers have used for twenty years
— they are called **SIFT**, **ORB** and **AKAZE** — on the *exact same images*, and score them the
*exact same way*. Then we can say something real: not "we are good", but **"we are 2.88 times more
accurate than the best existing method at 15 degrees of sun difference."**

Think of it as the current record holder. Beating a record only counts if you ran the same track.

**What those three methods do, simply:** each one hunts for distinctive *corners* in both images —
a crater rim, a sharp rock — and tries to pair them up. They are good, fast, and free. They are
also exactly the methods that get fooled by shadows, because a shadow's edge has a corner too.

## Part 4 · Why your part is hard (the interesting bit)

**Because it is dangerously easy to cheat without meaning to.**

If the old methods get slightly blurrier images, or a slightly harder version of the task, or are
scored with a slightly different ruler — the comparison is worthless, and a judge who spots it
throws out our headline claim.

So the rules you enforce are strict:
- The old methods and our method see **byte-identical image files** — literally the same file.
- Both are scored by **the same function** — Samrudh's scorer, not a separate one.
- All three old methods use **the same settings** for the one parameter that could favour one.

There is a second thing, and it is the sharpest point in your whole section:

**When the old methods fail badly, they often produce no score at all.** They give up. So if you
average "the scores that came back", you are averaging *only the runs that succeeded* — which
makes the old methods look far better than they are.

We caught this. At 180 degrees of sun difference, **fourteen of fifteen classical runs failed
outright**, and the one that survived was about 4,972 pixels wrong. The honest way to say this is
as a **success rate**, not as a ratio: *"we scored 5 out of 5; they scored 1 out of 15."*

> ⚠️ **Do not say "62,519 times better".** It is technically in our data, but it rests on that one
> surviving run, and a judge will take it apart in ten seconds. Say the success rate instead. It is
> a stronger claim *and* an honest one.

## Part 5 · What your part does NOT do

> *"It does not prove we are better in general. It proves we are better on these specific pairs,
> at these specific sun angles, scored this specific way — and it also shows where we LOSE. At zero
> degrees of sun difference, SIFT beats us. We put that on the slide."*

That last part is worth volunteering. A team that shows where it loses is believed about where it
wins.

## Part 6 · What you personally did

You wrote the original SIFT, ORB and AKAZE runners and the first benchmark results — **27 commits
across the project.**

**Be straight about one thing:** on 3 September, Samartha did a substantial rewrite of the baseline
harness — it had a hardcoded path to a file that never existed, so it could not run for anyone; it
read images with a function that returns nothing for our file type; and it invented its own scoring
instead of using Samrudh's. That is recorded in the commit message and in the handover notes.

**The honest sentence, if asked:**
> *"I wrote the three classical baselines. The harness that runs them all and logs the results was
> substantially rewritten by Samartha on Day 5 when we found it could not run on the real data. I
> understand what it does and why it changed — do you want me to walk through it?"*

That answer costs you nothing and protects the whole team. Claiming the rewrite and then being
asked a detail about it is the risk.

## Part 7 · Questions you will be asked

**"Is the comparison fair?"**
> "Deliberately so. Both methods get byte-identical files, scored by the same function. The one
> setting that could favour one of the three classical methods is set to the *looser* value, so
> adopting it does not flatter us."

**"Which classical method is best?"**
> "It depends on the sun angle. SIFT is best with identical lighting — it beats us there. ORB is
> best at 30 degrees. Past 45 degrees they mostly stop producing an answer at all."

**"Why not just use SIFT if it's better?"**
> "Because it's only better in the one case where there is no problem to solve. With identical
> lighting there are no moving shadows, and SIFT is an excellent corner finder. The moment the Sun
> moves — which is the actual problem — it degrades and we don't."

**"How many runs did you do?"**
> "Five different offsets at each of eight sun-angle differences, for each of three methods. And
> we count the runs that failed, rather than quietly dropping them out of the average."

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
