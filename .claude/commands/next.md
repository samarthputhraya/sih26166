---
description: Start a session — pull teammates' work, rebuild context from STATUS.md, show gate position, and propose today's plan
allowed-tools: Read, Grep, Glob, Bash, Agent
---

Start this working session. Rebuild full context in under two minutes, then propose a plan.

Work through the six steps in order, then stop and wait for confirmation before doing any work.

---

## 1 · Where we were

Read `ops/STATUS.md` completely. That is the handoff from the last session. If it is missing or
stale (older than the last commit), say so — the previous session did not run `/wrap`, and you are
rebuilding context from git alone, which is worse.

## 2 · What arrived overnight

```bash
git pull
git log --oneline --since="18 hours ago"
git diff --stat HEAD@{1}..HEAD 2>/dev/null || git log --stat -3
```

Who pushed, and what landed. Name people, not files: *"Samrudh pushed `metrics.py` with the
held-out split — Risheeth is unblocked."*

## 3 · Does it still work

```bash
python -m pytest evaluation/ -q 2>&1 | tail -3; echo "exit: $?"
python -c "import sys; sys.path.insert(0,'.'); import core.pipeline" 2>&1 | tail -2
```

Report exit codes. **If something a teammate pushed broke the build, that is today's first task**,
ahead of whatever the plan says.

## 4 · Position

State plainly:

```
Day <N> of 12  |  <k> days to Gate <G>  |  Internal hackathon: <date or "DATE STILL UNKNOWN">
Gates passed: <list>          Next gate: <G> on Day <D> — <on track | at risk: reason>
```

Pull the day's row from `docs/TEAM_TASK_GUIDE.md`. Pull gate criteria from
`docs/00_CANONICAL_FACTS.md` §11. If the internal hackathon date is still unknown, say so every
single session until it is not — it is the last open variable that changes the plan's shape.

## 5 · Who is blocked

From `ops/STATUS.md` plus what just landed. For each of the five teammates:

- delivered since last session
- currently blocked on — and **whether the blocker is Samartha**

> If anyone is waiting on Samartha, that is the top of today's list regardless of the plan.
> The project's own rule: *no teammate ever waits on Samartha; if they are, the spec was bad.*

Also check whether a teammate has pushed nothing for two days. That is a Gate 5 risk — someone who
stops working stops understanding, and then cannot answer for their own module. Flag it by name.

## 6 · Propose today

Offer a plan, in priority order, with rough time. Do not start yet.

```
## Day <N> plan
1. <blocking-others item>                      ~<t>
2. <critical-path item from the day's row>     ~<t>
3. <gate-driven item>                          ~<t>

Deferring: <what is in the plan but should slip, and why>
Watch: <the one thing most likely to go wrong today>
```

Then **stop and ask** whether to proceed with this plan or something else.

---

## Optional, on request

- **Teammates pushed a lot since the last review** → suggest launching **`daily-reviewer`**. Do not
  launch it unasked; it costs a few minutes and only earns that after real changes have landed.
- **Day 9 or later** → suggest **`demo-medic`**.
- **Day 8 or later, and `presentation/` changed** → suggest **`claim-checker`**.

---

**Do not begin implementation during `/next`.** This command rebuilds context and proposes. The
user decides what actually happens.
