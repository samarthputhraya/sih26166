# Day 3 — addendum to `day_3.md`

**`ops/specs/day_3.md` still stands. Nobody has completed it.** This file records only what changed
during the Day-2 evening session that alters a dependency in it. Read both.

> ⚠️ **The full `spec-writer` dependency pass did NOT run tonight** — the agent hit an API session
> limit partway through. Every claim below was verified by hand against the working tree; nothing
> here is a re-plan, only a delta. **Run `spec-writer` at the next wrap.**

---

## What changed that affects an existing spec

### 1. `data/pairs/pair_01` is now REAL — this unblocks two people

The old fixture was synthetic (its reference tile had 15 distinct grey levels). It has been rebuilt
from the real Chandrayaan-2 OHRC strip by `core/make_demo_pair.py`:

```
data/pairs/pair_01/pair_01_{source,ref}.tif   640x640 uint8   known offset (40, 25)
python -m core.pipeline data/pairs/pair_01    -> exit 0, 5185 matches
```

**This removes the "blocked on Samrudh's synthetic pairs" problem flagged at the bottom of
`day_3.md`.** `TEAM_TASK_GUIDE.md`'s Day-3 rows put both Risheeth and Rishabh on a harness that did
not exist. It still does not exist — but a real pair does.

- **Risheeth** — run the tuned baselines on `data/pairs/pair_01` instead of waiting on
  `evaluation/synthetic_data.py`. Known offset is `(40, 25)`, so a correct result recovers
  `(-40, -25)`. Log to `baselines/results_table.csv` (**not** `results_log.csv` — Samrudh owns that).
- **Rishabh** — same pair for a real-data smoke test of `detect_changes`. Note the two tiles are
  crops of one frame, so **there is no real change in them**: a correct detector finds *nothing*.
  That is a useful negative test and a false-positive check, not a failure.

> ⚠️ **`pair_01` is not a validation tier.** Same frame, same exposure, integer offset — identical
> pixels, no illumination difference. It is a wiring and known-answer fixture. Nobody may describe
> it as cross-sensor, cross-illumination or multi-modal. See `core/make_demo_pair.py`.

### 2. `core/illumination.py` now exists

`normalize(img, method=...)` returns **float32 in [0, 255]**, not [0, 1] — `core.matcher` divides by
255 downstream. Default is `gradient_orientation`, chosen on a measured A/B
(`core/bench_illumination_results.csv`). `phase_congruency` is also available.

Relevant to **Rishabh**: illumination normalisation is now a real option for separating "the sun
moved" from "something changed" — his Day-4 discriminator task. Worth reading before he starts.

### 3. The 46 MB LoFTR weights are now on Drive

`SIH26166_DATA/weights/loftr_outdoor.pt`. Anyone whose spec calls `core.pipeline.run_all()` can now
get them without asking. This closes sequencing risk 2 in `day_3.md`. Still untested on a
teammate's machine — **whoever pulls them first, say so in chat.**

---

## Re-issue, unchanged, with escalation

### 🔴 Samrudh — `evaluation/metrics.py`

**Your four commits at 21:12–21:33 pushed four EMPTY files.** `shaded_relief.py`,
`synthetic_data.py`, `metrics.py`, `test_metrics.py` are all 0 bytes on `origin/main`. The commit
messages are right; the files have nothing in them. Almost certainly `git add` of files that were
never saved out of the editor.

**Nothing is lost and you do not start over — re-save and re-push.** The spec with exact expected
test values is unchanged in `day_3.md`. `metrics.py` remains the **only** thing blocking Gate 1 on
Day 5.

### 🔴 Saniya — the SIH template

Unchanged and now four days outstanding. `presentation/` still contains only `.gitkeep`. 2 hours, no
repo work, no Python. Spec in `day_3.md` and `day01_saniya_template.md`.

### ⚠️ Rohan — placement, not quality

The LROC↔OHRC footprint analysis (`e31f444`) is good work. But it committed ~18 MB of PNGs —
including one at **9.96 MB** — plus `find_lroc_matches.py`, `lroc_coverage.html`,
`lroc_ohrc_matches.csv` and two JPGs **at the repo root**. Invariant 5: nothing over ~5 MB or binary
goes in git. **Git keeps these permanently; deleting them will not shrink the repo**, so this is
about stopping the next one, not undoing this one.

- Previews and plots → Drive.
- Scripts → a folder, not the repo root.
- `lroc_ohrc_matches.csv` (0.48 MB, 998 rows) is genuinely useful — keep it, in `data/`.

---

## Still unowned

**Tier C (multi-modal)** — in the PS *title*, a hard Gate-2 criterion, no data and no owner.
`day_3.md` said decide by Day 5. That is now two days away.
