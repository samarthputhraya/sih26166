# Saniya — the deck and the pitch, start to finish

**Written 5 Sep 2026 (Day 7). The round is 9 Sep.**

The SPOC has confirmed the live demo is **not mandatory**. That changes everything about where the
marks are: the deck and how we speak to it now carry the round almost entirely. This is the most
important job left in the project and it is yours.

Read this once, all the way through, before you touch anything. It should take fifteen minutes and
it will save you three hours.

---

## 0 · The good news, and the thing you must not do

**The deck already exists and it is already built.** Six slides, in the official template, with
every number checked against our evidence file. It is at `presentation/SIH26166_deck.pptx`.

**The words on the slides already exist too**, written and audited, in
`presentation/DECK_CONTENT.md`. That file is slide-by-slide, transcription-ready, and every figure
on it names the row it came from.

**So do not rewrite the content.** That is not modesty about your writing — it is that each number
and each phrase has been checked against `evaluation/results_log.csv`, and several were corrected
after a first draft got them subtly wrong in ways that would have lost us the round. If you rewrite
a sentence, you break that chain and nobody will know until a judge asks.

> **Your job is not to write the deck. It is to make the built deck excellent, fill the two things
> only you can get, and be able to speak to it.**

If you think a sentence is weak, that is worth raising — bring it to Samartha rather than editing
it, and we change it together with the row in front of us.

---

## 1 · The four rules. Breaking any one of them loses the round.

**Rule 1 — No number appears anywhere unless it is in `evaluation/results_log.csv`.**
Not on a slide, not in your mouth, not in an answer. This project already shipped an invented
figure ("0.7 px") through four documents once. If you want a number that is not in the deck, ask
for the row first. If there is no row, we do not say it.

**Rule 2 — Three words are banned unless they are literally true.**
- **"Cross-sensor"** means two *different instruments*. We have none. Never say it.
- **"Multi-modal"** means genuinely different kinds of imaging — visible vs infrared vs radar vs
  elevation. We have exactly one such pair: an optical photograph against an elevation model. Two
  cameras are *not* multi-modal.
- **"Sub-pixel"** must always name which image's pixels and give the metres.

These are the likeliest questions to end a Q&A round, because the problem statement asks for
multi-modal work and a judge from the Space Applications Centre will know exactly what the words
mean.

**Rule 3 — Do not edit the template's own prompt text.**
The official template has grey guidance text on each slide ("Proposed Solution", "Technologies to
be used", and so on). The instructions say you may only use the provided template *"without
changing the idea details pointers."* Our build **moves** that text to the top and makes it small
and grey, and puts our content in a new box underneath. Moving is safe; rewriting could be read as
a violation, and the cost of being wrong is disqualification. **Do not retype, shorten, or "tidy"
that grey text.**

**Rule 4 — The submission is a PDF.**
The instructions slide says it outright: *"save the file in PDF and upload the same on portal. No
PPT, Word Doc or any other format will be supported."* Uploading a `.pptx` fails.

---

## 2 · What to read, in this order

| # | File | Why | Time |
|---|---|---|---|
| 1 | `presentation/DECK_CONTENT.md` | what is on each slide, and the row behind every number | 20 min |
| 2 | `ops/PITCH.md` | what we *say* — deliberately not the same words as the slides | 15 min |
| 3 | `ops/briefs/BRIEF_SANIYA.md` | your own module brief for Gate 5 | 10 min |
| 4 | `ops/QA_ANSWERS.md` | the questions judges ask and our answers | 20 min |

You do not need to read the code. Nobody will ask you about it, and §6 gives you the honest answer
if they do.

---

## 3 · Step by step — getting to a finished PDF

### Step 1 — Get the two missing pieces from the SIH portal *(only you or Samartha can)*

Slide 1 has two blanks that no one else can supply:

- **Team ID**
- **Team Name** — exactly as registered, not as we say it out loud

**Copy them from the portal. Do not retype from memory** — a wrong Team ID on the title slide is
the kind of error that costs marks for carelessness before anyone reads a word of content.

### Step 2 — Put them in

They live in one file, `presentation/build_deck.py`, near the top — look for `TITLE_META`, at
lines 58-59:

```python
("Team ID",   "<TEAM ID - from the SIH portal>"),
("Team Name", "<TEAM NAME - as registered>"),
```

Replace the text inside the quotes. Change nothing else in that file.

### Step 3 — Rebuild

From the project folder, run these two commands in order:

```
C:\Users\samar\venvs\sih26166\Scripts\python.exe -m presentation.make_figures
C:\Users\samar\venvs\sih26166\Scripts\python.exe -m presentation.build_deck
```

The first regenerates the two charts from our evidence file, so a chart can never drift from the
data. The second builds the slides. It takes about twenty seconds and prints what it did.

**If that looks intimidating, ask Samartha to run it** — it is two commands and he can do it in
thirty seconds while you watch. What matters is that *you* know what it does: it rebuilds the deck
from the audited content so that nothing is typed by hand into a slide.

### Step 4 — Export to PDF

Open `presentation/SIH26166_deck.pptx` in PowerPoint → **File → Save As → PDF**.

We do not have LibreOffice on this machine, so PowerPoint is the route.

### Step 5 — Now do the quality pass in §4. This is the part that earns the grade.

---

## 4 · The quality pass — what separates a good deck from a generic one

Open the PDF full-screen and go through every slide against this list. This is where your judgement
matters more than anyone's, and it is the reason this job is yours rather than automated.

### The five-metre test
Stand back from the screen — properly back, five paces. **If you cannot read a number, it is too
small.** Faculty judges will be reading this projected in a lit room, possibly from the back. A
figure nobody can read is worse than no figure, because it looks like you did not think about them.

### Word economy
**No slide should exceed roughly forty words of our content.** The instructions themselves say
*"avoid paragraphs, post your idea in points."* If a slide feels dense, the fix is almost never
smaller text — it is fewer words. Cut adjectives before you cut facts.

### One thing per slide
Each slide should have a single idea you could name in four words. Slide 2 is *"it knows when it is
wrong."* Slide 4 is *"here is the proof."* If you cannot name a slide's one idea, it has two and
should have one.

### Make the finding visually dominant on slide 2
Slide 2 carries our entire novelty claim — and novelty is **25% of the mark, confirmed**. The
sentence that must catch the eye first is the finding: a matcher that reported success and was
about two kilometres wrong, and a system that caught it. If the eye lands anywhere else first, the
slide is arranged wrong.

### Figures
- Both charts are generated from the evidence file — **do not edit them in an image editor.** If
  something is wrong with a chart, it is wrong in the data or the script, and that is a real
  finding worth raising.
- Check axis labels are legible at the five-metre test.
- Check nothing is cropped by the slide edge.

### Consistency — the cheapest marks in the deck
Judges notice these without knowing they noticed:
- Bullets either all end with a full stop or none do.
- Capitalisation is consistent between headings.
- The same concept has the same name on every slide — do not call it "the trust map" on one and
  "the reliability layer" on another. **Pick one and use it everywhere.**
- No orphan: a bullet's last word alone on its own line.
- No stray placeholder text anywhere. Search the PDF for `<` and for "TBD".

### Anti-patterns — these read as amateur instantly
- Clip art, stock photos of space, gradients, drop shadows, 3-D effects.
- More than two font sizes in a content block.
- A screenshot of the app pasted in small. Either it is large enough to read or it is not there.
- Emoji.
- Anything that looks like it came from a template gallery rather than from us.

### The last check, and it is the important one
**Every number on every slide: can you say which row of `evaluation/results_log.csv` it came
from?** The deck has an audit table near the bottom of `DECK_CONTENT.md` that maps each figure to
its row. Go through it once. If you find a figure that is not in that table, stop and raise it —
that is exactly the class of problem we found twice this week, and both times it was on the slide
that matters most.

---

## 5 · Your part of the pitch

**Three minutes, two speakers.** Three minutes does not divide six ways — thirty seconds each with
five handovers reads as a group assignment, not a team. Gate 5 tests that all six can answer cold,
and that is tested in **Q&A**, which is where the other four earn their marks.

The full script is `ops/PITCH.md` §3. The split:

| Part | Who |
|---|---|
| Open, the problem, what we built (0:00–1:10) | Samartha |
| **Evidence, honesty, impact, close (1:10–3:00)** | **you**, if you are comfortable — otherwise Samrudh |
| Q&A | all six |

**Take the second half if you can.** It contains the strongest thirty seconds in the pitch — the
part where we say where we lose, before anyone asks. Delivered as confidence rather than apology,
it is what makes a judge believe the two minutes before it.

Three things about delivery:

1. **Do not read the slides.** The slides are the record; you are the argument. If you find
   yourself reading a bullet aloud, the slide has too many words — fix the slide.
2. **130 words a minute.** That is noticeably slower than you talk normally. Rehearse with a timer;
   three minutes means three minutes.
3. **Learn the five numbers so you never read them.** They are in `ops/PITCH.md` §4. Say those
   five and no others — every extra number costs you one of them.

If your format insists every member speaks, `ops/PITCH.md` §5 has a five-way split — but say so in
advance and rehearse the handovers, because that is where a group pitch falls apart. Make each
handover a *link*, not an announcement: *"Rohan will tell you what we had to work with"*, never
"and now I'll hand over to Rohan."

---

## 6 · Your Gate 5 card

Gate 5 asks each of the six the same five questions about **your own module**: what the problem is,
why it is hard, what your module does, how you know it works, and what is next.

Your module is `presentation/` — the deck.

> **What it does:** turns measured results into something a non-expert can judge in three minutes,
> without any figure losing its provenance on the way.
>
> **How I know it works:** every figure on every slide names the row of our append-only evidence
> file it came from. The deck has an audit table that maps each number to its row, and I can open
> that file and show you any of them.
>
> **What it does NOT do:** it does not compute anything. If a number is wrong, it is wrong upstream
> in the measurement, not in the slide — the deck is built from the content file by a script
> precisely so that nobody types a number into a slide by hand.

**The question that catches people out is *"what does your module NOT do?"*** Have that third
answer ready — it is the one that shows you understand the boundary of your own work.

If you are asked something about the algorithm, the honest answer is a good one: *"That is
Samartha's module — but the short version is..."* and give the one sentence. Never bluff. A team
that hands a question to the right person looks like a team; a member who guesses looks like a
member who did not do the work.

---

## 7 · Before you upload — the final checklist

- [ ] Team ID and Team Name are correct, copied from the portal, not typed from memory
- [ ] Exactly **six** slides, including the title page
- [ ] The file is a **PDF**
- [ ] The template's grey prompt text is untouched on every slide
- [ ] No `<`, no "TBD", no placeholder text anywhere in the PDF
- [ ] Every slide passes the five-metre test
- [ ] The words "cross-sensor" and "multi-modal" appear nowhere they are not literally true
- [ ] Every number traces to a row — checked against the audit table
- [ ] Opened on a second machine to confirm nothing shifted in export
- [ ] Uploaded, and **the portal's confirmation seen with your own eyes**

---

## 8 · If something looks wrong

**Raise it, do not fix it silently.** Twice this week a number that looked fine turned out to have
no evidence behind it, and both times it was found by someone stopping to check rather than
assuming. If a sentence reads oddly to you, that instinct is worth more than a quick edit — bring
it up and we resolve it with the evidence open.

The one thing that would genuinely hurt us is a slide that says something we cannot defend. There
is no version of this where a nicer sentence is worth that.
