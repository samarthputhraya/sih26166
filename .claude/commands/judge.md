---
description: Inspect the demo as an SIH judge would — drive the console and the app in a real browser, grade them, and rank the changes
---

Run the judge's walk-through in `ops/national_round/JUDGE_PROMPT.md`.

Read that file in full first, then follow it section by section, §1 through §8. It is the
instruction set for this command; nothing here overrides it.

Two things it is easy to get wrong, so they are repeated here:

- **This is a read-only inspection.** The only file you write is
  `ops/national_round/JUDGE_REPORT_<YYYY-MM-DD>.md`. Do not edit code, rebuild the deck, or run
  `ops.freeze` / `ops.precompute_demo_cache`. Evidence is frozen at `7dd4e5b`.
- **Drive the real thing in a real browser** via the chrome-devtools MCP. Reading the source is
  not inspection — this page has been wrong in ways the source looked right about.

If `$ARGUMENTS` names one artefact (`deck`, `console`, `live`, `streamlit`, `video`), inspect
only that one and still produce the graded verdict for it. With no arguments, do all four.
