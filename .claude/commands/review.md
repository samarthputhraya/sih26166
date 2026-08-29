---
description: Review the team's work since the last review — findings for owners to fix, never silent fixes
allowed-tools: Read, Grep, Glob, Bash, Agent
argument-hint: "[optional: person's name, to review only their work]"
---

Run the daily review of teammates' work.

Launch the **`daily-reviewer`** agent. If `$ARGUMENTS` names a person, scope the review to that
person's folder only; otherwise review everything pushed since the last review recorded in
`ops/STATUS.md`.

---

## Before launching

```bash
git log --oneline --since="1 day ago" --stat | head -40
```

If nothing has been pushed since the last review, say so and stop. Running a review over an
unchanged tree wastes minutes and produces noise.

## After it returns

**1. Split the findings into two piles.**

- `SAMARTHA-FIXES` — `core/`, integration glue, blocking crashes, mechanical noise. Fix these now.
- `OWNER-FIXES` — everything else. **Do not fix these.**

The test for every finding: *would fixing this leave the owner unable to explain their own module?*
If yes, it goes back to them. Gate 5 requires all six to answer cold about their own work, and
"the AI wrote it" does not survive an SIH Q&A round.

**2. Turn each `OWNER-FIXES` finding into a GitHub Issue** — assigned to that person, titled
`[Day N] <name> — <one-line problem>`, containing the finding's Where / Problem / Impact / Hint.

**Never paste the fix into the issue.** Name the concept, point at the line, let them close it.

**3. Respect the cap.** Three findings per person per day, maximum. If someone has more, send the
three that matter and note the rest in `ops/STATUS.md` under Known issues so tomorrow's review does
not re-report them. More than three real problems in one person's work is a signal about the spec
they were given, not a list to hand them.

**4. Record what was reviewed** in `ops/STATUS.md` — the commit range and the date — so the next
review starts from the right place.

**5. Post one line to the team.** Not the full report:

```
Reviewed today's pushes. <N> issues filed — <names>, check your GitHub Issues.
Clean today: <names>.
```

Naming who was clean matters. A report that is only ever criticism stops being read by day four.
