# Audit progress — read this FIRST, before any audit work

State lives on disk, not in a session. Skip every area marked DONE.

| # | Area | State | Findings file |
|---|---|---|---|
| 01 | core correctness | **DONE** (Day 6 recon) | `00_RECON_RAW_DAY6.json` |
| 02 | evidence integrity | **DONE** (Day 6 recon) | `00_RECON_RAW_DAY6.json` |
| 03 | demo fragility | **DONE** (Day 6 recon) | `00_RECON_RAW_DAY6.json` |
| 04 | test coverage | **DONE** (Day 6 recon) | `00_RECON_RAW_DAY6.json` |
| 05 | docs drift | **DONE** (Day 6 recon) | `00_RECON_RAW_DAY6.json` |
| 06 | claims defensibility | **DONE** (Day 6 recon) | `00_RECON_RAW_DAY6.json` |
| 07 | UI rebuild | **NOT STARTED — full spec ready** | `07_UI_SPEC.md` |
| 08 | hygiene / dead code | **DONE** (Day 6 recon) | `00_RECON_RAW_DAY6.json` |

`00_RECON_RAW_DAY6.json` is the full structured output of a 12-agent, 1.69M-token survey
(4 Sep 2026). Every finding carries file:line evidence and a reproduction command.
`00_RECON_journal.jsonl` has one line per agent with its complete return value.

## The three that matter most — verified, with reproductions in the raw file

1. **HIGH — the trust layer has a ~2.5 px (150 m) dead zone by construction.** The area
   check reads an INTEGER correlation peak (`core/reliability.py:128`) against
   `MAX_CELL_SHIFT_PX = 2.0`, so an axis-aligned error up to 2.49 px passes. Measured: a
   **144 m error is labelled `verified` on all 64 cells.** This EXPLAINS the 45–60 deg blind
   spot STATUS.md records as unexplained — 142.7 m at 60 m/px is 2.38 px, inside the floor.
   **Do not fix (algorithm frozen). State it as a number**: "our detector resolves to 2.5
   reference pixels, 150 m at this GSD; the blind spot is inside that floor by construction,
   not by luck." Being asked the smallest catchable error with no answer loses the room.

2. **HIGH — `core/subpixel.py`'s docstring argues AGAINST the shipped default.** It says
   refinement is off and enabling it is "the trap", with dated numbers. It has shipped ON
   since 3 Sep and **every Gate 2 number was measured with it ON** (pair_01: 0.1945 off vs
   0.0376 on). `docs/00_CANONICAL_FACTS.md:593` still says "shipped OFF (measured)".
   Gate 5 risk: anyone revising from that file will tell a judge the opposite of the truth.

3. **MEDIUM — tiled matching emits duplicate matches, up to 3.34x.** `_tiles` clamps origins
   flush to the edge so real overlap far exceeds OVERLAP=96, and `match()` vstacks with no
   dedup. Inflates `n_matches`/`inlier_count` and makes `distribution_cv` (Gate 2 criterion 4)
   look worse than the matcher is. `core/matcher.py:53` claims the bookkeeping "is tested" —
   no test calls `_tiles` or `match`. Only triggers above 640 px, i.e. from the UI uploader,
   which is exactly what Gate 3's stranger will use.
