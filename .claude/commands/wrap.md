---
description: End the session cleanly — smoke test, update STATUS.md, draft tomorrow's specs, commit, push, and produce the team's WhatsApp update
allowed-tools: Read, Edit, Write, Grep, Glob, Bash, Agent
---

End this working session so the next one can start cold with no lost context.

Work through all seven steps in order. Do not skip a step because it "looks fine" — the value of
`/wrap` is that it is the same every night.

---

## 1 · What changed this session

```bash
git status --short
git diff --stat
git log --oneline -10
```

Summarise in three lines or fewer: what got done, what is half-finished, what broke.

## 2 · Smoke test — run it, don't infer it

```bash
python -m pytest evaluation/ -q 2>&1 | tail -5; echo "pytest exit: $?"
python -c "import sys; sys.path.insert(0,'.'); import core.pipeline" 2>&1 | tail -3
```

Record the **exit codes**. If something is red, that is the first line of tomorrow's plan, not a
footnote. Never write "tests pass" without having seen the exit code this session.

## 3 · Update `ops/STATUS.md`

Rewrite it — do not append. It must be true as of right now:

- **Day number** and days remaining to the next gate
- **Gate status** — which have passed, which is next, and whether it is at risk
- **Per person**: last push, what they delivered, what they are blocked on
- **In flight**: what Samartha was mid-way through, with enough detail to resume cold
- **Open questions**: anything unresolved that would otherwise be re-litigated tomorrow
- **Known issues**: so `daily-reviewer` does not re-report them

Be specific enough that a version of you with no memory of today can pick up in two minutes.
"Working on the matcher" is useless. "`core/matcher.py` LoFTR wrapper done; `to_common_gsd` returns
the wrong scale factor when GSDs are equal — see line 47" is useful.

## 4 · Tomorrow's five specs

Launch the **`spec-writer`** agent. It drafts specs for Rohan, Samrudh, Risheeth, Rishabh and
Saniya, and — critically — verifies each spec's dependencies already exist in the repo.

If it returns anything under `BLOCKED`, **fix the sequencing tonight.** A teammate discovering
tomorrow at 9pm that their input does not exist costs them their entire two hours.

Save the output to `ops/specs/day_<N>.md`. Samartha pastes each into a GitHub Issue assigned to
that person.

## 5 · Commit and push

```bash
git add .
git commit -m "Day <N>: <what actually happened, one line>"
git push
```

If the push is rejected, `git pull` first, then push again.

**If a large binary was staged by accident**, stop and tell the user — do not commit it. Data
belongs in Google Drive. A committed 750 MB file bloats the repo permanently for all six people.

## 6 · Gate check

If tomorrow is a gate day (**5, 8, 10, 11, 12** — see `docs/00_CANONICAL_FACTS.md` §11), state
plainly whether the gate will pass on current evidence, and what is missing. Do not be reassuring.
A gate that is going to fail is worth knowing about tonight, while there is still a night.

For Gates 3 and 4 specifically, launch **`demo-medic`** rather than judging by eye.

## 7 · The team message

Produce a WhatsApp update ready to paste — short, factual, and useful to five people who were not
here:

```
Day <N> done.
Pushed: <what landed>
Unblocked: <who can now start what>
Blocked: <who is waiting on what, and the plan>
Tomorrow's specs are in GitHub Issues — <names> you're assigned.
Gate <N> is on <day>: <on track | at risk because X>
```

Then output, for the user only:

```
SESSION WRAPPED — Day <N>
Next session: run /next
In flight: <the one thing to resume first>
```

---

**Do not start new work during `/wrap`.** If you notice something broken, record it in
`ops/STATUS.md` under Known issues and stop. Fixing "just one thing" at the end of a session is how
a repo ends up in a half-committed state overnight.
