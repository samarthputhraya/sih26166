# 02 — Daily Review Protocol

**Who this is for:** everyone. Samartha runs the review; the other five receive its output, and
should understand why it arrives as questions rather than corrections.

---

## THE PROBLEM

Five people work two hours a day, mostly with free-tier AI assistants that give different answers
to the same question. Small mistakes compound: a wrong metric on Day 3 poisons every number after
it. So the work gets reviewed daily, not at the end.

## THE TRAP WE ARE AVOIDING

The obvious version of this is: Samartha reads everyone's code each night and fixes what's wrong.

**That version loses us Gate 5.**

Gate 5 requires all six people to answer questions about their own module cold, with no notes. If
Samartha quietly repairs Samrudh's held-out split at midnight, Samrudh walks into the room unable
to explain his own evaluation method. And *"the AI generated it"* is a known team-killer in SIH
Q&A rounds — judges probe for exactly this.

There is a second-order cost too. Right now you are learning because you get stuck and unstick
yourselves. If someone repairs everything overnight, you stop reading errors, stop debugging, and
by Day 12 there is one person who understands the project and five who typed things.

## THE RULE

> **The review produces findings. You fix your own module.**

The reviewing agent has **no Write or Edit tool.** It structurally cannot fix your code. That is
deliberate.

### What Samartha fixes himself

- anything in `core/` — it's his
- integration glue between two modules
- a crash that would block you tomorrow morning
- mechanical noise: imports, path separators, formatting

### What comes back to you

- anything that changes **what your module does**
- anything you would need to explain at Gate 5
- any algorithm, threshold or statistical choice

The test applied to every finding: *would fixing this leave the owner unable to explain their own
module?* If yes, it comes to you.

---

## WHAT YOU RECEIVE

A GitHub Issue assigned to you, titled `[Day N] <your name> — <one-line problem>`:

```
Where   : evaluation/metrics.py:47
Problem : When H_true is None this returns 0.0 for rmse_gt_px.
Impact  : A judge reading the deck sees "0.0 px accuracy" on real pairs,
          where we have no ground truth at all. That's an overclaim we
          can't defend.
Hint    : What should an unmeasurable quantity return?
```

**Note what is not there: the fix.** That's the point. You close it in your next session, and now
you actually understand why held-out validation matters — which is what you'll be asked about.

## LIMITS THAT PROTECT YOU

- **Maximum 3 findings per person per day.** You have two hours; a review that eats all of it is a
  failed review. If you have more than three real problems, that's a signal the *spec* you were
  given was bad — Samartha's problem, not yours.
- **Known issues are recorded** in `ops/STATUS.md` so nothing gets re-reported daily.
- **Clean work is named.** If your day was clean, the report says so. A report that is only ever
  criticism stops being read by Day 4.

---

## WHAT GETS CHECKED

Ten things, chosen because they are what actually goes wrong in *this* project:

1. **Numbers that aren't in `results_log.csv`** — the fabricated-figure risk
2. **Terminology** — "cross-sensor" for same-sensor pairs, "multi-modal" misused, "sub-pixel" with
   no pixel grid named
3. **Hardcoded ground sample distance** — wrong by 1000× on a Kaguya pair, on screen
4. **Hardcoded absolute paths** — six people, six machines
5. **GPU assumptions** — the demo machine has none
6. **Network calls on the demo path** — Gate 4 runs with wifi off
7. **Interface drift** — a changed signature breaks someone tomorrow
8. **Silent plausible failure** — returning `0.0` where it should return `None`
9. **Tests that assert nothing** — and whether `pytest` actually passes right now
10. **Big files committed** — they belong in Drive

---

## AUTOMATE THE HALF THAT NEEDS NO JUDGEMENT

Before the review runs, these run:

```bash
python -m pytest evaluation/ -q            # do the tests pass?
python -m core.pipeline data/pairs/pair_01 # does the pipeline still run?
```

Roughly half of what a human would catch by reading, caught for free. The review spends its
attention on the half that needs judgement.

---

## UPSTREAM: DIVERGENCE IS A SPEC PROBLEM

If two teammates' code looks nothing alike, that usually isn't a review failure — it's that the
spec was loose enough for two assistants to answer differently.

A spec that says *"build a metrics function"* invites five architectures. A spec that says
`evaluate(ref_shape, matches_src, matches_ref, H_true=None) -> dict` with three named tests and a
**"Do not"** section does not. That's why `spec-writer` exists and why every spec names the
plausible-but-wrong approach for that specific task.

---

## WHEN A JUDGE ASKS WHETHER YOU USED AI

Answer honestly, because the honest answer is good:

> "Yes, as an assistant — for boilerplate, for debugging, and for reviewing each other's work. Every
> module has one owner who wrote its logic and can explain it. We reviewed daily, but the reviews
> produced findings that the owner fixed themselves, specifically so that each of us understands our
> own component."

That is true only if this protocol is followed. Follow it, and the question is an opportunity.
