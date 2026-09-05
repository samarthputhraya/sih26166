# Gate 5 cards — one per person

**Send each person their own file. They do not need to read the others.**

| Person | File | Their part, in four words |
|---|---|---|
| Samrudh | `SAMRUDH.md` | the exam marker |
| Risheeth | `RISHEETH.md` | the control group |
| Rishabh | `RISHABH.md` | spot the difference |
| Rohan | `ROHAN.md` | the chain of custody |
| Saniya | `SANIYA.md` | three minutes a judge can use |
| Samartha | `SAMARTHA.md` | the engine, and its checker |

Saniya also has `ops/SANIYA_DECK_AND_PITCH_GUIDE.md`, which is her working document for building
the deck. This card is the shorter thing — what to say if a judge asks about her part.

---

## What these are, and what they are not

Each card explains, for one person: the whole project in 60 seconds *(identical wording in all six
— if we describe the project six different ways, that is what a judge remembers)*, what their part
does in plain English, why it is hard, **what it does not do**, what they personally contributed,
and the questions they will be asked with answers.

**They are written for someone with no background in the domain.** No maths, no jargon that is not
immediately explained, analogies before terminology.

**They are not scripts to memorise.** A memorised answer collapses on the first follow-up. The
cards are built so that if someone *understands* their part, the words come out on their own.

---

## The honesty position, and why it is the strong one

The cards say plainly what each person did — from the actual commit history, not from the org
chart. Where Samartha rewrote something inside someone else's folder, **the card says so and gives
that person the sentence to use.** Two cases:

- **Risheeth** wrote the three classical baselines; the harness that runs them was substantially
  rewritten on Day 5 when it turned out it could not run on real data.
- **Rohan's** dataset card was filled in by Samartha on 1 Sep while Rohan's PC was down. His card
  asks him to re-derive one row himself before Gate 5, using the commands in that file — after
  which he can say something true and confident.
- **Saniya** has no commits; the deck content was drafted by Samartha. Her card gives her the
  honest framing and tells her exactly what to do so that framing becomes true.

**This is deliberate, and it is not modesty.** A rehearsed claim of authorship dies on the first
specific follow-up, and it takes the team's credibility with it. *"I wrote this part; that part was
rewritten by Samartha when we found a problem, and here is what changed"* is unattackable — and it
is the answer of someone who was actually there.

`CLAUDE.md` puts it as a rule: *"the AI wrote it" does not survive an SIH Q&A round.* Nor does
"my teammate wrote it and I said I did".

---

## How to run the rehearsal (Gate 5, Day 10 — 8 Sep)

Do not let people read their card aloud. That tests reading.

1. **Everyone reads their own card once, alone.** Fifteen minutes.
2. **Round one — the four questions, cold.** Someone who is not them asks:
   *what problem · what does your part do · why is it hard · how do you know it works.*
   No notes, no screens.
3. **Round two — the one that matters:** *"what does your part NOT do?"* Almost nobody prepares
   for this and it is the strongest signal that the work is real. Every card has this answer in
   Part 5.
4. **Round three — hand-offs.** Ask each person a question that belongs to somebody else. The
   correct answer is one sentence of context, then the name. Practise it until it is comfortable —
   handing a question to the right person makes a group look like a team.

**The pass condition:** all six can answer the four questions without notes, and nobody bluffs.

---

## The three rules that are in every card

1. **No number that is not in `evaluation/results_log.csv`.** *"I would have to check the row"* is
   a strong answer.
2. **"cross-sensor" and "multi-modal" are banned** unless literally true. We have no cross-sensor
   pair. We have exactly one genuinely multi-modal pair — a photograph against an elevation model.
3. **"I don't know, but Samartha does"** scores better than a guess. Every time.
