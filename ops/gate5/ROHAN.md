# Rohan — your module, in plain English

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

**You are the librarian, and you hold the chain of custody. Nothing else in the project is
trustworthy if your part is not.**

Every image this project uses came from a real space mission — Chandrayaan-2, Japan's Kaguya
orbiter, NASA's LRO. Your job has two halves:

1. **Get the actual data**, from the space agencies' public archives.
2. **Write down exactly what each file is** — and this is the part that matters.

For every image you record: which spacecraft and instrument took it, the original product ID, how
much ground one dot of the image covers, where the Sun was in the sky when it was taken, and where
on the Moon it points. That lives in `data/pairs_catalogue.csv` and `data/DATASET_CARD.md`.

Think of it as the label on a museum exhibit. The object is worthless to a researcher without it.

## Part 4 · Why your part is hard (the interesting bit)

**Because a wrong label is invisible, and it silently corrupts everything downstream.**

Here is the concrete example. One of your entries records that a certain image is **60 metres per
dot**. Our final results are reported in metres — we take an error measured in dots and multiply
it by that number.

If that 60 were actually wrong, **every metre figure in this entire project would be wrong**, on
every slide, and *nothing downstream could possibly catch it*. The alignment would still work. The
tests would still pass. The number would just quietly be false.

That is why the rule in the dataset card is **"blank means not known — never guess."** An honest
blank is safe. A confident wrong number is not.

There is a second hard part: **matching up which images actually overlap.** Two photos of the Moon
are only a "pair" if they cover the same ground. You wrote the footprint analysis that works out
which candidates genuinely overlap and by how much.

## Part 5 · What your part does NOT do

> *"It does not verify that the space agency's own metadata is correct. I record what the product
> label says, and where I measured something myself I say so. What I refuse to do is fill a blank
> with a plausible guess — because a guess and a measurement look identical once they are in the
> file, and only one of them is safe."*

Also be honest about the biggest gap in the project, because it is in your area and a judge will
find it:

> *"We do not have a true cross-sensor pair — two different cameras of the same place. We looked;
> the products that would give us one need map-projected data we could not obtain in time. We say
> that plainly rather than describing what we do have as something it is not."*

**That is a strong answer.** The weak answer is pretending the gap is not there.

## Part 6 · What you personally did

You have **8 commits** in the project — the pairs catalogue, the Tier-D pair builder, the
LROC/OHRC footprint overlap analysis, and the terrain validation for candidate pairs.

**Be straight about one thing:** `data/DATASET_CARD.md` says at the top that Samartha filled it in
on 1 September while your PC was down, because two other people were blocked waiting for it. Every
number in it was measured from the products, and the file lists the exact commands used.

**Before Gate 5, re-run at least one of those rows yourself.** The commands are at the bottom of
that file. Then you can say, truthfully:

> *"The dataset card was filled in by Samartha while my machine was down. I have been through it
> and re-derived [whichever row you check]. I can show you the command."*

That is an honest, confident answer. It is far better than either claiming you wrote it or looking
surprised by the question.

## Part 7 · Questions you will be asked

**"Where did this data come from?"**
> "Public mission archives — ISRO's Chandrayaan-2 portal, JAXA for Kaguya, NASA's PDS for LRO.
> Every file has a provenance record with its original product ID, so any of it can be re-downloaded
> and checked independently."

**"How do you know the scale is right?"**
> "It comes from the product label, and where we derived it ourselves the command that derived it
> is written down. Where we do not know, the field is blank rather than filled with a guess —
> because a guess would be invisible downstream."

**"Do you have Chandrayaan-2 data of different types, as the problem statement asks?"**
> "We have optical imagery. We do not have the infrared instrument data, and we say so. What we do
> have is a genuine cross-*kind* pair — a photograph against an elevation model — which is a
> harder case than two photographs, and it is the pair our system's key result comes from."

**"Could someone reproduce your dataset?"**
> "Yes. Each pair has a provenance file recording the source product, the exact crop window and how
> the reference was generated. That is deliberate — a result nobody can rebuild is not evidence."

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
