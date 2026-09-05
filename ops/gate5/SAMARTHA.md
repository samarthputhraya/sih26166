# Samartha — your module, in plain English

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

**You built the engine and the thing that checks the engine. The second one is the project's
contribution.**

The engine: remove the lighting before matching (keep the *direction* of every edge, throw away
brightness), match whole patches rather than corners with a learned matcher, throw away the matches
that disagree, then check the survivors are spread across the frame rather than bunched in one
bright corner.

The part that is ours: **a second, independent check that re-derives the alignment straight from
the pixels and never looks at a single match.** The frame is split into 64 cells and the cells
vote. Three outcomes per cell — verified, weak, no evidence — and if the vote contradicts the
matcher, the system declares it, throws the matcher's answer away, and registers by a different
method instead.

**The analogy that lands with a non-expert:** the inlier ratio is marking your own homework. The
area check is having someone mark it who has not seen your working.

## Part 4 · Why your part is hard (the interesting bit)

**Because the failure this catches is invisible to every standard check.**

On the Tier D pair the matcher produced 88 correspondences, RANSAC reached consensus, and the run
reported `status ok`. Against ground truth the transform was about **two kilometres** wrong. Every
statistic the matcher produces describes the *matches*. None of them can see the ground.

The second hard thing is that **the first version of the check was wrong**, and finding that is
worth telling. A single whole-frame correlation wrongly contradicted every 30° and 45° pair and
triggered a fallback ten to forty times worse than the transform it replaced. The rule became a
vote of cells because cells are high-pass by construction and vote independently. That is measured,
not asserted.

## Part 5 · What your part does NOT do

> *"It cannot see an error smaller than about 150 metres. The area check reads an integer
> correlation peak against a two-pixel threshold, so an error up to about two and a half reference
> pixels is indistinguishable from zero by construction. That is also why our 45-to-60 degree blind
> spot exists rather than being a mystery — at 60 degrees we are 142.7 metres out, which is inside
> that floor. We know the number because we measured it."*

Also: *"the calibration is on rendered pairs, not real photographs — that is the only place an
exact answer exists. The real-data evidence is a single case, and I would not claim more."*

## Part 6 · What you personally did

`core/` and `app/streamlit_app.py` — 94 commits, the majority of the project. You also did
substantial work inside other people's folders when they were blocked, which is recorded in the
commit messages and in the handover notes rather than being quietly absorbed.

**Where that matters for Gate 5:** if a judge asks a teammate something and the honest answer is
"Samartha rewrote that", the recovery is easy and you should take it without hesitation. The commit
messages back it up.

## Part 7 · Questions you will be asked

**"Isn't this just the RANSAC inlier ratio with a colour map?"**
> "No. On that pair the inlier consensus held — the median inlier residual was 0.00 px — and every
> match was wrong. Our verdict comes from a test that never sees the matches: each cell of the
> warped source is cross-correlated against the reference, and the cells vote. And 'no evidence' is
> a separate state, not a low score."

**"Uss et al. did per-region accuracy without ground truth in 2016, including optical–DEM."**
> "Yes, and they are on our references slide. Theirs is a continuous accuracy bound inside an
> area-based method. Ours is a three-state map over a learned matcher's output with an explicit
> unmeasured state, a pixel-versus-match disagreement as the failure signal, a declared fallback,
> and a calibration on lunar data. It is a system contribution, not a new estimator, and we say so."

**"How much better is your map than chance?"**
> "On the hard cases a cell we mark verified has a median true error of 0.231 px against 3.201 px
> for a cell we mark no-evidence — about fourteen times. That is what makes it a measurement rather
> than a colour scheme."

**"Why LoFTR and not SuperGlue?"**
> "Licence and hardware. SuperGlue's published weights depend on SuperPoint, which is academic
> non-commercial only. LoFTR is Apache-2.0 and runs on this laptop's CPU in about six seconds per
> tile with no GPU. If ISRO wanted to deploy this, the licence is the difference."

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
