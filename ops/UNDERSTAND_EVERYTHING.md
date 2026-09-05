# Understand everything we built — from zero

**Read this like a story, start to finish. It assumes you know nothing.**

By the end you will understand the Moon problem, why it is hard, exactly what we built, why our
bit is new, how we proved it, where we lose, and what every short form means. You will be able to
answer a judge without memorising anything, because you will actually *understand* it.

It is long. It is meant to be. Give it forty minutes and you will never need to be nervous in that
room.

---

# PART 1 · The setting — why anybody photographs the Moon

In August 2023, India landed **Chandrayaan-3** near the Moon's south pole. No country had done it
before.

Landing on the Moon is not like landing a plane. There is no runway, no air traffic control, and
nobody there to tell you what the ground looks like. If your lander sets down on a boulder the size
of a fridge, or on the slope of a small crater, it tips over and the mission is finished. It cannot
be repaired. There is nobody there.

So before you land anything, you need a map. Not a rough map — a map good enough to say *"this
particular 10-metre square is flat and free of rocks."*

That map comes from spacecraft in orbit around the Moon, photographing the surface as they pass
over. India has **Chandrayaan-2** doing exactly this right now. It has been circling the Moon since
2019, taking photographs.

## The key idea to hold onto

**One photograph is a picture. Two photographs of the same place are *information*.**

With two photos of the same patch of ground you can ask questions you cannot ask with one:

- Has anything changed here between the two visits?
- Is that dark patch a shadow, or a genuine hole?
- How steep is that slope really?
- Is this landing site still as safe as it was six months ago?

Every one of those questions requires you to **compare** the two photos. And comparing requires
one thing first, which sounds trivial and is not.

---

# PART 2 · The task — what "registration" actually means

**Registration is lining two photographs up so that the same crater sits at the same spot in
both.**

That is the whole definition. When you hear "image registration", think **"stacking two tracing
papers so the drawings line up."**

If they are not lined up, everything you do afterwards is nonsense. You would be comparing crater A
in the first photo to crater B in the second, and concluding that the Moon has changed when
actually your two sheets of paper were just offset by a centimetre.

> **This is the problem ISRO gave us.** Take a Chandrayaan-2 photograph, and line it up
> against a reference image of the same place — accurately, automatically, and reliably.

Sounds like it should be easy. The same rocks are in both pictures. Just slide one until it matches.

Here is why it is not easy.

---

# PART 3 · The villain — the Sun has moved

Imagine photographing your school playground twice: once at 8 in the morning, once at 5 in the
evening.

Same playground. Same swings, same wall, same tree. But look at the two photos side by side and
they are startlingly different. In the morning photo, every shadow stretches to the left. In the
evening photo, every shadow stretches to the right. A wall that was bright is now dark. The tree's
shadow has swung right across the picture.

**Now make it much worse, because this is the Moon:**

- **There is no air.** On Earth, air scatters sunlight around, so shadows are soft and you can
  still see into them. On the Moon there is nothing to scatter light. A shadow is *pitch black* —
  a hole in the picture where information simply does not exist.
- **The south pole is the worst case.** That is where the interesting water-ice is, and where
  everyone wants to land. But the Sun there never rises high — it skims along near the horizon.
  Low Sun means enormous, dramatic shadows that can be longer than the crater itself.
- **There are no helpful clues.** No colours, no trees, no buildings, no roads. Just grey rock and
  grey dust, and hundreds of craters that all look rather alike.

So: two photographs of the same place, taken months apart, can look so different that even a person
struggles to see they are the same place.

## Why this breaks the computer

Here is how image-matching software has worked for the last twenty-odd years.

The computer hunts for **corners** — small, distinctive, high-contrast spots it can recognise again.
The sharp rim of a crater. A bright rock against dark ground. It finds a few thousand of these in
each photo, then tries to pair them up: *"this corner in photo one is that corner in photo two."*

**And here is the trap. The edge of a shadow looks exactly like the edge of a rock.**

To a computer, both are just "a place where bright meets dark". It cannot tell them apart. So it
happily picks up hundreds of shadow edges as if they were solid features on the ground.

**But shadow edges move.** They are not attached to the rock — they are attached to *where the Sun
happens to be*. So the computer confidently pairs a shadow edge in photo one with a completely
different shadow edge in photo two, and works out an alignment from that.

The alignment comes out wrong.

---

# PART 4 · The worse villain — being confidently wrong

This is the heart of our entire project. If you understand only one section, make it this one.

## A story about a student

A boy does a long multiplication in an exam. He gets 4,732.

He wants to check it, so he does it again — the same way, using the same method. He gets 4,732
again. Same answer twice! He is now *very confident*. He underlines it and moves on.

The real answer was 3,891. He made the same mistake both times. **Checking his work the same way
could never have caught it**, because the check shared the mistake.

Being confident and being right are not the same thing. And a confident wrong answer is much more
dangerous than an obviously wrong one — because nobody goes back to look at it.

## This is exactly what alignment software does

When registration software finishes, it reports numbers that sound like a quality score. The most
common is called the **inlier ratio** — roughly, *"what fraction of my matched points agree with
each other?"*

If 95% of its matched points agree, it reports a high score and everyone relaxes.

**But look carefully at what that measures.** It measures whether the software's own guesses are
*consistent with each other*. It does not — cannot — measure whether they are *correct*.

If the software matched shadow to shadow, and all those shadow matches happen to agree with each
other, you get a beautiful score and a completely wrong answer.

**It is marking its own homework.**

## This actually happened to us, and it is our best evidence

We have a genuinely hard pair of images in our project. Here is what our own system did on it,
before the clever part kicked in:

- The matcher found **88 matching points** between the two images.
- The filtering step agreed those points were consistent, and produced an alignment.
- The run reported **status: ok**. Success.

And the actual answer? Measured against the truth, the alignment was **about two kilometres wrong.**

Two kilometres. On a picture where each dot represents about nine metres of ground. And every
number the software produced said everything was fine — because every one of those numbers was
describing the matches, and **the matches cannot see the ground**.

> ### This is the problem we set out to solve.
>
> Not "make alignment better" — plenty of people do that. **Make it tell you when it is wrong.**

---

# PART 5 · What we built, part one: the engine

Our system has two halves. The first half is the engine that does the aligning. It is good
engineering, using known techniques well. **We do not claim this half as our invention**, and being
straight about that is important — a judge will respect it and it protects our real claim.

It has four steps.

## Step 1 · Throw away the brightness, keep the shape

**The idea:** if shadows are the enemy, and shadows are all about *brightness*, then throw the
brightness away before you start matching.

**The analogy:** think of a pencil outline drawing of a face, versus a photograph of that face. The
photograph changes completely depending on whether the light comes from the left or the right. The
outline drawing does not — the nose is in the same place either way.

We do the same thing to the Moon photos. For every tiny spot in the image, instead of storing *"how
bright is this?"*, we store *"which way is the edge running here?"*

**The genuinely clever detail** — and this is worth understanding because it explains a surprising
result later:

We store the edge's **direction as a line, not as an arrow.**

Picture an edge running diagonally across the image. It is the same line whether you think of it as
pointing north-east or south-west. By storing the line rather than the arrow, something remarkable
happens: **if the lighting completely reverses — bright side becomes dark side — the line is
unchanged.**

So even a total flip of the lighting cannot fool this step.

> **Technical name:** *illumination normalisation, by gradient orientation.*
> **What to say:** *"We keep the direction of every edge and throw away the brightness, so a crater
> lit from the east and the same crater lit from the west come out looking the same."*

## Step 2 · Match whole patches, not corners

The old methods hunt for corners. We already saw the two problems: shadows make **fake corners**,
and smooth lunar plains have **almost no real corners at all** — there is nothing distinctive to
find on a flat grey plain.

Instead we use a modern neural network called **LoFTR**. Rather than picking out a few thousand
corners, it looks at the whole image at once and matches *regions* using their surroundings for
context.

**The analogy:** you do not recognise your friend by their nose alone. You recognise the whole
face — the arrangement of everything together. Even in bad light, even at an odd angle. That is
what LoFTR does with patches of ground.

This is off-the-shelf software, free and openly licensed. We chose it deliberately over a
better-known alternative (SuperGlue), for a reason worth knowing:

> **SuperGlue's licence says academic and non-commercial use only.** LoFTR's licence (Apache-2.0)
> allows anyone to use it, including ISRO, including commercially. If this project were ever
> actually deployed, that licence is the difference between "usable" and "not usable".
>
> It also runs on an ordinary laptop with **no graphics card**, which matters because our whole
> system is designed to run on cheap hardware.

## Step 3 · Throw away the matches that disagree

Even with the first two steps, some matches will be wrong. So we need to find the ones that agree.

**The analogy:** a hundred witnesses see a car roll down a hill. Eighty say *"it moved about three
metres to the left."* Twenty say wildly different things — one says it flew upwards, another says
it went backwards.

You do not average all hundred. You notice that eighty agree, you trust those, and you throw away
the twenty.

That is exactly what this step does. It finds the largest group of matches that all agree on the
same story, and discards the rest.

> **Technical name:** *RANSAC*, and specifically a modern version called **MAGSAC++**.
> **The story they agree on** is called a **homography** — one single instruction that says how to
> move, rotate and stretch the whole image so it lines up. Think of it as *"shift 40 across, 25
> down, and tilt very slightly."*

## Step 4 · Check the matches are spread out

One last engine check, and it catches a subtle cheat.

Suppose all your matches come from one bright, rocky corner of the image, and the rest of the frame
— a big smooth plain — has nothing. Your alignment might be perfect *in that corner* and completely
wrong everywhere else. But your score would look excellent.

So we chop the image into a grid of **8 × 8 = 64 squares** and check how the matches are spread
across them.

> **Technical names:** `grid_coverage_fraction` (how many of the 64 squares contain at least one
> good match) and `distribution_cv` (how evenly spread they are — lower is better).
>
> ⚠️ **An honesty point:** we *measure* the spread. We do not *force* it to be even. If a judge
> asks whether we enforce uniform distribution, the answer is no, we report it. Claiming otherwise
> would be false.

---

# PART 6 · What we built, part two: the trust layer — **this is our contribution**

Everything in Part 5 is good engineering that other people also do.

**This part is ours, and it is what the whole project is judged on.** Novelty is 25% of the marks
and it is confirmed. So slow down here.

## The problem, restated

After all four engine steps, we have an alignment. And we *still* have no idea whether it is right.
Every number we have describes the matches. None of them can see the ground.

We need a genuinely independent second opinion.

## The idea, in one sentence

> **A second check that works out the alignment all over again, straight from the raw pixels, and
> never looks at a single one of the matcher's matches.**

**The analogy:** you do a maths problem and check it yourself — that is the inlier ratio, marking
your own homework. Instead, hand it to a second teacher who has *not seen your working* and ask
them to solve it independently. If they get your answer, that means something. If they get a
different answer, you have learned something far more valuable.

## How it actually works

Remember that 8 × 8 grid — 64 squares.

For each square, we do something simple and completely independent of everything before it:

1. Take that square from the aligned image.
2. Slide it around on top of the reference image, trying every position.
3. Find the position where it fits best.
4. **Ask: is the best fit "stay exactly where you are"?**

If the alignment is right, each square should already be in the correct place — so the best fit is
"no movement needed". That square agrees.

If a square says *"actually I fit much better 8 pixels to the left"*, that square disagrees. The
alignment is wrong there.

**Notice what this uses: raw pixels. No corners, no matches, no neural network.** It cannot inherit
the matcher's mistake, because it never sees the matcher's answer.

> **Technical name:** *area-based correlation*, done with a Fast Fourier Transform. You do not need
> to know how the FFT works. Say *"we slide each square around on the reference image and find
> where it genuinely fits best."* That is accurate.

## Then the squares vote

Each of the 64 squares gets one of **three** verdicts:

| Verdict | What it means | Why not just a score? |
|---|---|---|
| **verified** | We measured here. The independent check agrees with the matcher. **You can trust this part of the image.** | |
| **weak** | We measured here, and something does not add up. **Treat with caution.** | |
| **no evidence** | **We could not measure here at all.** | ← **this one is the novel part** |

## Why "no evidence" is the genuinely new idea

This is the bit to really understand, because it is the difference between our project and
everyone else's.

Almost every system in the world gives you a **confidence score** — a number from 0 to 100. Low
score means bad, high score means good.

But there are **two completely different reasons** a score might be low:

1. *"I looked carefully and this is genuinely bad."*
2. *"I could not see anything here at all — this region is a featureless smooth plain, or it is in
   total shadow, or the image does not cover it."*

**Those are not the same thing, and squashing them into one number destroys the difference.**

Think about a doctor. There is a vast difference between *"I examined you and you are healthy"* and
*"the scanner could not see that area."* Both might get written down as "no problem found". Only one
of them means you are fine.

So we refuse to squash them. **"No evidence" is its own state, and it is an honest blank.** Marking
it green would be a lie; marking it red would also be a lie. It means *we do not know*, and saying
so out loud is the whole point.

## And when the vote contradicts the matcher

If enough squares disagree with the matcher's answer, the system does something most software never
does. It **declares its own failure.**

1. It says clearly: *the matcher's answer is contradicted by the pixels.*
2. It **throws the matcher's answer away** — it does not report it.
3. It falls back to a completely different, simpler method that just slides the whole image around
   until it fits best.
4. It reports **how uncertain even that fallback is**, by checking whether the four corners of the
   image agree with each other.

On our hard pair, that fallback produced an alignment of **231 metres**, and reported that the four
quadrants disagree by up to **216 metres**. In other words: *"here is my best answer, and here is
how much you should doubt it."*

**Compare the two outcomes on that same pair:**

| Ordinary software | Our system |
|---|---|
| Reports success | Reports the matcher was contradicted |
| Gives a confident alignment | Refuses to use it |
| The alignment is 2 km wrong | Falls back to a different method |
| Nobody ever finds out | Reports 231 m, ± 216 m uncertainty |

> ### The one sentence for the whole project
>
> ## "A lunar image-registration engine that knows when it is wrong."

---

# PART 7 · How we proved it works

A claim with no evidence is just an opinion. So how do you prove an alignment is correct, when
nobody knows the true answer for two real Moon photographs?

**You cannot.** So we did the only honest thing available.

## We built puzzles where we already know the answer

Here is the trick, and it is genuinely neat:

1. Start with a real **3D elevation map of the Moon** — actual measured heights of the actual lunar
   surface, made by a NASA laser that bounced pulses off the ground from orbit.
2. Use a computer to **draw a picture of that landscape lit from a chosen Sun angle.** Like a video
   game rendering a scene. Call it Image A.
3. Now draw the *same landscape* lit from a **different** Sun angle — and shift it by an exact
   amount we choose. Say 12.37 pixels right and 8.63 pixels down. Call it Image B.

We now have two images that look like a genuinely hard registration problem — different lighting,
real lunar terrain, shifted — **and we know the exact right answer, because we chose it.**

Then we let the system try, and measure how far off it was.

We did this for **40 different pairs**, across **8 different amounts of Sun-angle difference** (0°,
15°, 30°, 45°, 60°, 90°, 120°, 180°), with **5 different shifts each**. That gives 2,560 individual
squares with a known correct answer.

> **The honest limitation, and say it before you are asked:** these are *rendered* images, not
> photographs. That is not a dodge — it is the only place an exact answer can exist. If we knew the
> true answer for two real photographs, there would be no problem to solve in the first place.

## What the measurements showed

**1 · We beat the old methods, and by how much**

At 15° of Sun difference we are **2.88 times more accurate** than the best of the three classical
methods, on byte-identical image files scored by the same function.

Past 45°, the classical methods mostly stop producing an answer at all.

**2 · The trust map is real, not decoration**

This is the number that proves our contribution. On the hard cases:

| Label | How wrong it actually was |
|---|---|
| **verified** | 0.231 pixels |
| weak | 1.373 pixels |
| **no evidence** | 3.201 pixels |

A square we call *verified* is about **fourteen times more accurate** than one we call *no
evidence*. The labels genuinely mean something. **That is what makes it a measurement rather than a
colour scheme.**

**3 · The failure detector works, and never cries wolf**

Across 40 pairs, our system caught **77% of genuine failures** — with a **0% false-alarm rate.**
Across 27 registrations that were correct, it never once wrongly claimed failure.

> **Why the 0% matters more than the 77%:** a smoke alarm that goes off when you make toast gets
> taken down off the wall. A failure detector nobody trusts is worse than no detector at all. We can
> raise the detection rate by being more suspicious, but it costs false alarms — at a higher setting
> we catch 100% but wrongly flag 9% of good results. We chose the setting with zero false alarms.

**4 · A surprise we can explain**

Here is a result that looks like a bug and is not. Our accuracy at **180°** of Sun difference — the
most extreme possible, lighting from exactly the opposite side — is **better** than at 15°.

That sounds impossible. But remember Step 1: we store each edge as a *line*, not an arrow. Flipping
the lighting to the exact opposite side **reverses** the brightness, and a reversed line is the same
line. So our method sails straight through it.

Our hardest case is **90°**, not 180° — because at 90° the lighting is *sideways*, which genuinely
rotates the shape of the shading rather than just inverting it. Nothing protects against that.

**And here is the proof it is real rather than a fluke of our test images:** at 180°, the classical
methods **failed in fourteen out of fifteen runs**. If the 180° images were somehow secretly easy,
the old methods would have found them easy too. They did not. That difference is caused by our
method, not by our test data.

---

# PART 8 · The dictionary — every short form, explained

## Missions and organisations

| Term | Say it as | What it is |
|---|---|---|
| **ISRO** | *is-ro* | Indian Space Research Organisation. They set this problem. |
| **SAC** | *S-A-C* | Space Applications Centre — the ISRO centre that works on imaging. A judge could be from here. |
| **SIH** | *S-I-H* | Smart India Hackathon. The competition. |
| **PS** | | Problem Statement — the task we were given. Ours is numbered **SIH26166**. |
| **Chandrayaan-2** | *chandra-yaan* | India's Moon orbiter, circling since 2019, still taking photographs. **Our source images come from here.** |
| **Chandrayaan-3** | | India's 2023 lander — the one that landed near the south pole. |
| **LRO** | *L-R-O* | Lunar Reconnaissance Orbiter. NASA's Moon orbiter, there since 2009. |
| **Kaguya** | *ka-goo-ya* | Japan's Moon orbiter (JAXA). Also called SELENE. |
| **LUPEX** | *loo-pex* | Lunar Polar Exploration Mission — the upcoming India–Japan mission to the Moon's south pole. **This is who would use our work.** |

## Cameras and instruments

| Term | Stands for | In plain words |
|---|---|---|
| **OHRC** | Orbiter High Resolution Camera | Chandrayaan-2's sharpest camera. Each dot ≈ 23 cm of ground — sharp enough to see a boulder. |
| **TMC** | Terrain Mapping Camera | Chandrayaan-2's wide camera, for mapping large areas in less detail. |
| **IIRS** | Imaging Infra-Red Spectrometer | Chandrayaan-2's *infrared* instrument. Sees heat and mineral signatures rather than visible light. **We do not have data from this — say so honestly.** |
| **LROC** | Lunar Reconnaissance Orbiter Camera | The camera system on NASA's LRO. |
| **NAC** | Narrow Angle Camera | The zoomed-in half of LROC. "LROC NAC" means that specific camera. |
| **TC** | Terrain Camera | Kaguya's mapping camera. "Kaguya TC" in our documents. |
| **LOLA** | Lunar Orbiter Laser Altimeter | A **laser** on NASA's LRO. Not a camera — it fires pulses at the ground and times the echo to measure *height*. This is how we have a 3D map of the Moon. |
| **panchromatic** | | A black-and-white camera that sees all visible light at once. OHRC and LROC NAC are both panchromatic. |

## Data and measurement words

| Term | In plain words |
|---|---|
| **DEM** | Digital Elevation Model — a 3D height map. For every point, how high the ground is. **LDEM** is the lunar one. |
| **hillshade / shaded relief** | A *picture drawn from* a DEM, showing what that landscape would look like lit from a chosen Sun angle. Like a video game rendering. |
| **GSD** | Ground Sample Distance — how much ground one dot covers. "60 m/px" means each dot is 60 metres across. **Crucial**, because an error of "2 dots" means 46 cm on one image and 120 metres on another. |
| **pixel / px** | One dot of an image. |
| **sub-pixel** | Accurate to *less than one dot*. **Always say which image's dots, and give the metres** — an unqualified "sub-pixel" is not an answer. |
| **ground truth** | The real, known, correct answer. Only exists when we made the puzzle ourselves. |
| **RMSE** | Root Mean Square Error — an average of how wrong we were. Bigger = worse. |
| **residual** | How much our own guesses disagree with each other. **This is NOT accuracy** — see the warning below. |

## Method names

| Term | In plain words |
|---|---|
| **registration** | Lining two images up. The whole task. |
| **SIFT, ORB, AKAZE** | The three classic corner-finding methods, ~20 years old. Our comparison — the "old way". |
| **LoFTR** | *"lofter"*. The modern neural network we use, which matches whole patches instead of corners. |
| **RANSAC / MAGSAC++** | The "trust the majority of witnesses" step that throws away disagreeing matches. |
| **homography** | The single instruction describing how to move/rotate/stretch one image onto the other. |
| **NCC** | Normalised Cross-Correlation — a way of measuring how well two image patches match, ignoring overall brightness. |
| **FFT / phase correlation** | The fast maths trick for "slide this patch around and find where it fits best". |
| **Streamlit** | The tool our demo app is built with — it makes a web page out of Python code. |

## The two accuracy words — do not mix these up

> **This is the single most important distinction in the project, and a judge may test it.**
>
> - **`rmse_gt_px` — TRUE ERROR.** *"How wrong were we, compared to the known right answer?"*
>   Only possible on our made-up puzzles, where we know the truth.
> - **`residual_px` — FIT RESIDUAL.** *"How much do our own guesses disagree with each other?"*
>   This is all you can compute on a real pair.
>
> **A fit residual can look beautiful while the answer is completely wrong.** That is exactly what
> happened on our hard pair. Never call a residual an accuracy.

---

# PART 9 · Where we lose — and why saying so makes us stronger

Every one of these is on our slides deliberately. **A team that volunteers where it fails is
believed about where it succeeds.** A team that claims everything works perfectly gets picked apart.

**1 · At 0° Sun difference, the old method beats us.**
With identical lighting, SIFT gets 0.044 and we get 0.086. And that makes complete sense: with the
same lighting there *is* no shadow problem to solve, and SIFT is an excellent corner-finder. Our
claim is not "we are a better matcher" — it is **"we are robust to lighting changes, and our
advantage grows as the lighting difference grows."**

**2 · There is a blind spot between 45° and 60°.**
In that range we are wrong and we do not realise it. We know precisely why, which is the good part:

**3 · Our detector cannot see errors smaller than about 150 metres.**
The independent check measures shifts in whole pixels, and only complains when the shift is bigger
than 2 pixels. So an error up to about 2½ pixels — roughly 150 metres on that image — looks
identical to no error at all. At 60° of Sun difference we are 142.7 metres out, which is *inside*
that floor. So the blind spot is not a mystery — **it is exactly where the physics of our detector
says it should be.** Being able to say that number is much stronger than not having a blind spot at
all, because it shows we measured our own limits.

**4 · We do not have a cross-sensor pair.**
"Cross-sensor" means two genuinely *different cameras* of the same place. We could not obtain one in
time. **Never claim we have this.**

**5 · We do not have infrared data.**
The problem statement mentions IIRS, Chandrayaan-2's infrared instrument. We have no IIRS pair. What
we *do* have is one genuinely multi-modal pair — a photograph against an elevation model — which is
arguably a *harder* problem than two photographs, and it is the pair our headline result comes from.

**6 · Our accuracy calibration is on rendered images, not photographs.**
Already covered: it is the only place ground truth can exist.

---

# PART 10 · The questions judges ask, and how to answer

**"What does your project actually do?"**
> "It lines up two photographs of the same place on the Moon, taken under different sunlight — and
> then it tells you which parts of that alignment you can trust and which you cannot. Most systems
> give you one score for the whole image. Ours gives you a map."

**"Why is this hard? Surely you just slide one image until it matches?"**
> "Because the Sun moves between the photos, so every shadow moves too. Software matches images by
> finding corners, and a shadow edge looks exactly like a rock edge — but it moves. So the software
> confidently matches shadows and gets the alignment wrong, and nothing it reports tells you that."

**"What is new here? Image registration is decades old."**
> "The registration isn't the new part and we don't claim it is. The new part is that the system
> knows when it is wrong. We added a second, independent check that redoes the alignment straight
> from the pixels and never sees the matcher's answer. The frame is split into 64 squares and they
> vote. And there are three outcomes, not two — *verified*, *weak*, and *no evidence*, where 'no
> evidence' means we genuinely could not measure there. That third state is the contribution."

**"Isn't 'no evidence' just a low confidence score?"**
> "No, and that is the heart of it. A low score means 'I looked and it is bad.' No evidence means
> 'I could not look.' Those are completely different things and squashing them into one number
> throws away the difference. It is the difference between a doctor saying 'I examined you and
> you're fine' and 'the scanner couldn't see that area.'"

**"How do you know your trust map means anything?"**
> "Because we measured it against known answers. On the hard cases, a square we mark *verified* is
> about fourteen times more accurate than one we mark *no evidence*. If the labels didn't separate,
> the claim would be dead — that was the first thing we tested."

**"Show me it catching a real failure."**
> "On our optical-versus-elevation pair, the matcher found 88 correspondences, produced a transform,
> and reported success. Against ground truth it was about two kilometres wrong. Zero of the 35
> measurable squares agreed with it. The system declared it contradicted, refused to use it, fell
> back to a different method, and reported 231 metres with a ±216 metre uncertainty. That is a
> declared failure with a number on it instead of a confident wrong answer."

**"Why is your test data artificial?"**
> "Because that is the only place an exact answer exists. For two real photographs nobody knows the
> true offset — if we did, there'd be no problem to solve. We're open about it: the accuracy
> figures come from rendered pairs, and the real-data evidence is that the system caught its own
> failure on a genuine pair."

**"The problem statement asks for multi-modal. Where is it?"**
> "Our one genuinely multi-modal pair is optical against elevation — a Kaguya photograph against a
> LOLA elevation model. Two different physical ways of sensing, which is what multi-modal means.
> We do not have optical-against-infrared and we say so. What we can show is a system that detects
> when its matcher has failed on a different modality, and says so."

**"Is this cross-sensor?"**
> "No, and we never claim it is. Cross-sensor means two different cameras, and we could not obtain
> such a pair in time. Our app displays what each pair actually is on screen, so nobody can imply
> otherwise by accident."

**"Someone already did per-region accuracy estimation — Uss et al., 2016."**
> "Yes, and they're on our references slide. Theirs is a continuous accuracy bound inside an
> area-based method. Ours is a three-state map over a learned matcher's output with an explicit
> unmeasured state, a pixel-versus-match disagreement as the failure signal, a declared fallback,
> and a calibration on lunar data. It's a system contribution, not a new estimator, and we say so."

**"What would you do with another month?"**
> "Two things. Calibrate the trust map on real multi-illumination pairs rather than rendered ones —
> a public dataset exists. And make the independent check measure fractional pixels rather than
> whole ones, which would drop that 150-metre floor and close the 45-to-60-degree blind spot."

**"Who did what on this team?"**
> Answer honestly, name the person, and hand over. *"That's Samrudh's part — he built the scoring
> and the logbook. Shall I bring him in?"* **A team that routes a question to the right person looks
> like a team. Bluffing and getting caught costs everyone.**

**Anything you genuinely do not know:**
> "I don't know that off the top of my head — but every number we quote is a row in our results
> file and I can show you the exact one." **This is a strong answer, not a weak one.**

---

# PART 11 · If you remember only five things

1. **Two photos of the Moon, months apart, look totally different because the Sun has moved — and
   software matches shadows by mistake and gets it wrong.**

2. **Worse: it gets it wrong *confidently*, because it only checks whether its own guesses agree
   with each other. That is marking your own homework.**

3. **We built a second, independent check that redoes the alignment straight from the pixels and
   never sees the matcher's answer. 64 squares vote. Three outcomes: verified, weak, and — the new
   idea — no evidence.**

4. **It works: a *verified* square is fourteen times more accurate than a *no evidence* square, and
   the system catches 77% of failures with zero false alarms. On one real pair it caught a matcher
   that was two kilometres wrong and reported success.**

5. **We say where we lose — at 0° the old method beats us, we have a blind spot at 45–60°, and our
   detector cannot see errors under 150 metres. We know all three because we measured them.**

> ## "A lunar image-registration engine that knows when it is wrong."

That is the sentence. Everything else supports it.
