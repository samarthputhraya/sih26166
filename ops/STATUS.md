# STATUS - end of Day 7 (5 Sep 2026, small hours)

> Rewritten in full at the end of every session. Previous STATUS is in git history (`1f80369`).
> WARNING: the venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly. A bare
> `python` fails here with `ModuleNotFoundError: numpy` - that is the missing venv, not a broken build.

---

## Position

```
Day 7 of 11  |  4 days to the event  |  Internal hackathon: 9 SEP 2026 (confirmed)
Gate 1: PASSED (Day 5)   Gate 2: PASSED (Day 6, one day early)
NEXT: Gate 3 TOMORROW, Day 8 (6 Sep) - a stranger operates the UI unaided
Then:  Gate 4 Day 9 (7 Sep, CPU-only wifi-off x3)   Gate 5 Day 10 (8 Sep, all six answer cold)
Novelty weight: 25% (confirmed)
```

**Working model, unchanged since Day 6:** Samartha is building the project alone. No work is
routed to teammates, so there are no nightly task specs and `spec-writer` was not run.
`ops/specs/DAY6_HANDOFFS.md` remains superseded. The per-person briefs in `ops/briefs/` still
matter, because **Gate 5 on Day 10 needs all six to explain their own module cold** - that is the
only remaining thing the other five must do, and nobody has prepared it. See Open questions.

## What this session did - area 07 of the audit, the demo UI

Areas 01-06 and 08 were already DONE from the Day-6 twelve-agent recon
(`ops/audit/00_RECON_RAW_DAY6.json`). **Area 07 was the only one open, and it is now closed.**
Four commits, full write-up in `ops/audit/07_ui.md`:

| commit | what |
|---|---|
| `6c89eb5` | `app/streamlit_app.py` rewritten to `ops/audit/07_UI_SPEC.md`; `.streamlit/config.toml` new |
| `dc3115b` | three demo-fragility defects found by the Streamlit-correctness review |
| `e4f1840` | change detection was converting areas with the common grid, not the reference grid |

**What a judge now sees:** a light paper page (a projector cannot project black in a lit room),
one CSS block plus one config file, system fonts only, no Deploy button, no stock coloured alert
boxes, no emoji, no shadows. Every verdict is a WORD first and a colour second - `ALIGNED` /
`FALLBACK USED` / `NO TRANSFORM` / `CONTRADICTED`. The reliability map draws three *kinds* of mark
(tint + "V", hatch + "W", faded-to-paper + "-") beside an ASCII cell map, so it survives a
photograph and a colour-blind judge. **The primary readout has no form that prints a bare pixel
number**: every form names the reference grid and either gives the metres or says why it cannot.

**Four defects found and fixed, each pinned by a test that fails on the previous commit:**

1. **`st.image(None)` crashed the whole page** when a result's images could not be re-opened. The
   `except` set both arrays to `None` and the next line handed `None` to `st.image`
   (`AttributeError: 'NoneType' object has no attribute 'format'`). The cached pickles store
   **this laptop's absolute paths**, so a backup machine or a moved data folder turned the first
   Align into a traceback - the exact Gate 4 failure.
2. **`.streamlit/config.toml` was silently ignored unless launched from the repo root.** Measured
   from `app/`: `theme.base=None`, `fileWatcherType='auto'`, `gatherUsageStats=True` - a dark app,
   file watching on, and a network call with the wifi off, with no error to say why. Streamlit
   also reads the config beside the main script and that copy wins, so `app/.streamlit/config.toml`
   is now a byte-identical mirror and a test stops the two drifting.
3. **Two uploads with the same filename overwrote each other**, so the pipeline aligned an image
   against itself and returned a flawless-looking result from a mistake.
4. **Change detection used the COMMON grid** (the coarser of the two) to convert pixel areas whose
   arrays sit on the REFERENCE grid. Latent - the two are equal on all four bundled pairs, so no
   displayed number moved - but it is the same two-grid confusion already fixed for the residual.
   `reference_gsd()` is now the single definition of the one scale this file may multiply by.

Also corrected in the UI: the source radio did not reset the previous result; the state rail
described the sidebar rather than the result; "CPU time" was wall-clock time; "about 15 s" was a
number nobody measured.

## Smoke test - exit codes observed this session, not inferred

| Check | Result |
|---|---|
| `pytest -q` | **231 passed**, exit 0 |
| `pytest evaluation/ -q` | 21 passed, exit 0 |
| `pytest app/test_streamlit_app.py -q` | 25 passed, exit 0 |
| `import core.pipeline` | ok, exit 0 |
| `python -m core.pipeline data/pairs/pair_01` | `residual_px 0.03761504064805703`, 63/64 verified - the pinned Gate-1 number, exact |
| Live LoFTR run through the new UI | 19.1 s, same residual |
| `git status` | clean, nothing uncommitted |

## Next session (Day 8, 6 Sep) - in order. **Gate 3 is that day.**

1. `/next`, `pytest -q`, both Gate-1 commands.
2. **Act on the two HIGH design findings below** - both are Gate-3 findings and both are ~20
   minutes in `app/streamlit_app.py`. Do these before the stranger sits down.
3. **Read `demo-medic`'s Gate 3 / Gate 4 verdict** - launched at the end of this session.
4. **Gate 3: recruit the stranger and run it.** Someone who has never seen the project. Launch
   from the repo root, hand them the laptop, say nothing.
5. **Two catalogue rows from the `data/` owner** - known issue 10. The highest-value ten minutes
   available: it is what stops the demo contradicting the deck on the Tier D pair.
6. **Team ID + Team Name into slide 1** from the SIH portal, then re-export the PDF. Still the
   only thing between us and a submittable deck.
7. **Re-run `python -m ops.precompute_demo_cache`** at the frozen HEAD - known issue 9. Add
   `-dirty` to `_commit()` while you are in there.
8. **Gate 5 prep for the other five** (Day 10). Nobody has started it and it needs all six.
9. Migrate the six documents in known issue 2 to the envelope figure; demo script (3:00).

## Design review - the last lens, and it found two Gate-3 problems

The four-lens UI review's design pass had never seen the final build: the first three runs were
shown screenshots of older builds and their design reviewer died on the account session limit
twice. It completed at the end of this session against the five current screenshots. Its verdict:
*"the rebuild no longer looks generated - palette, boxes and borders are sound"*, with two HIGH
findings that matter tomorrow. Full text in `ops/audit/07_ui.md`.

1. **HIGH - the sentence that explains the headline verdict is machine prose.** The strip prints
   `declared['why']` verbatim: *"Method used: loftr+magsac++ - 98% of 64 measurable cells agree
   with H -> agrees."* A stranger cannot say that aloud in their own words: it contains `H`, a
   method token, an arrow, and "agree...agrees". On the fallback pair it reads as two authors
   glued together (a lowercase sentence start after a full stop). **Fix:** keep the raw string in
   the section-03 log where it already prints, and render a human gloss in the strip with no new
   numbers.
2. **HIGH - on the Tier D pair, three red FAILs are the loudest legible thing.** `FAIL (> 0.60)`,
   `FAIL (>= 0.80)`, `FAIL (< 1.0)` at 15 px bold red, while the two sentences that reframe them
   ("matcher transform, not used"; "Gate 2 is judged on the synthetic sweep") are 13-15 px grey. A
   non-domain judge reads orange warning, then three red FAILs, and concludes it failed - on the
   pair carrying the 25% novelty claim. **Fix:** `seclabel()` already takes a `note`; on a
   fallback result pass "matcher's metrics - transform not used" onto the 04 rule, and move the
   Gate-2 sentence above the table at body size. No value changes.
3. MEDIUM - the label tier (what a thing *is*) is 12.2-13.3 px and projector mode only lifts it to
   14.4-15.6 px, all under the 15 arc-minute comfortable-reading threshold at 5 m. Section
   headings are the smallest text on the page. Suggested: a second replace token for the label
   tier, or raise those classes to .86-.92rem and `.verdict__word` to 1rem.
4. MEDIUM - the same provenance is restated four times on screen one (tag, rail, section note,
   sidebar caption), which is how generated UIs look; a lab report states it once.
5. MEDIUM - the three plates are told apart only by 12.9 px captions that clip at 768 px, and the
   black margin on the aligned plate is unexplained (a stranger reads it as broken).
6. MEDIUM - emphasis inverted in the readout: on the fallback pair the only bold text is
   `43897.00 m`, which invites "your error is 44 km?". Bold "not used" instead.
7. LOW - `--caution` on the panel is 4.40:1, below AA, and it is the state word for the novelty
   pair. `#8F4708` gives 5.73:1. The comment at the top of the skin quotes the *ground* figure.
8. LOW - `.tag--live` is a two-level state carried by colour alone; ~40 px of empty paper between
   two rules above the readout; the projector-mode checkbox is below the sidebar fold.

**None of these are fixed.** They are the next session's first task, ahead of the stranger.

## Known issues - do not re-report

1. RESOLVED Day 6 - `detect_changes` normalised both images by their combined max, which crushed
   the optical image on the multi-modal pair. Fixed; 183 candidates, 0 kept / 5 rejected / 178
   unassessable. Pinned by 7 tests.
2. RESOLVED Day 7 (`cc5890e`) - **and it was worse than a stale figure.** The five documents
   were migrated to the envelope figure, but the envelope figure itself
   (0.123 px / 7.4 m / 99.0% / n=817) **was not in `results_log.csv` at all.** The deck quoted it
   and cited `reliability_calibration_pooled`, whose logged rows carry 0.162/n=926 and
   0.147/n=1257 - the pooled populations. The envelope is the `sun_delta <= 30` subset, an
   aggregation of three per-delta groups (300+294+223) that existed only in
   `core/reliability_calibration.csv` - a derivation the calibrate script opens `"w"` and would
   silently overwrite. It is correct (recomputed, matches MOVE2 exactly) and is now its own
   appended row, `reliability_calibration_envelope`.
3. **`core/reliability_calibration.csv` is a derivation, not a log** - the script opens it `"w"`.
   Running a *partial* sweep silently discards the rest. Always run the full delta list.
4. **`presentation/sih_template.pptx` is gitignored**, so a fresh clone has no template. The curl
   command is in `DECK_CONTENT.md`.
5. **No real pair with a sun difference.** MiLOI (github.com/Bin501/CNSFM) remains the route.
6. **`redetect()` still unwired** - claim removed, not deferred.
7. **Submission deadline discrepancy** (15 vs 20 Sep) - still unasked of the SPOC.
8. Frames whose cells are narrower than 24 px (pair_03) fall back to the whole-frame peak; the
   `basis` field says so.
9. RESOLVED Day 7 (`43d1692`) - re-run at a clean HEAD; the sidecar now says `43d1692`, a
   commit that actually contains the trust layer, and `_commit()` appends `-dirty` when core/,
   evaluation/ or app/ are uncommitted. Every cached number reproduced bit-for-bit
   (pair_01 residual 0.03761504064805703, all four pairs' methods and cell counts identical).
   Original report: **the demo cache was written from an uncommitted working tree.** Every
   `demo_cache/results/*.json` says `git_commit: fce6d05`, but `git ls-tree fce6d05 --
   core/reliability.py` is empty: that commit has no trust layer and no fallback. The cache was
   written four minutes before `65b3224`, which added them. **The numbers are correct** - a live
   `run_all()` at HEAD reproduces every cached metric, verdict, shift and cell count exactly - but
   the provenance string is wrong. The UI now labels it `CACHED RESULT commit fce6d05` rather than
   claiming it is the running code. Fix by re-running the precompute.
10. RESOLVED Day 7 (`03ea293`) - both catalogued from each pair's `PROVENANCE.md`; the rail
    now reads `TIER D / Kaguya_TC vs LOLA_LDEM` and the "not evidence" warning is gone. The
    notes also state that the hillshade is rendered at the photograph's OWN solar geometry, so
    there is zero sun-angle difference in either pair - a modality test, not an illumination
    test. Original report: **the two Tier D demo pairs are absent from
    `data/pairs_catalogue.csv`.** Its `pair_id`
    values are `pair_01, tier_bplus_01, tier_a_01, tier_d_01`; the directories the app offers are
    `pair_03_tierD` and `pair_04_tierD_native`. The UI looks up by directory name, finds nothing,
    and correctly prints `TIER unknown / SENSORS unknown` plus *"A number without its tier is not
    evidence"* - **on the one pair the deck's 25%-weighted novelty claim rests on.** The UI must
    not hardcode a tier; the data file is what is missing. Add rows whose `pair_id` equals the
    directory name, `tier=D`, `source_instrument=Kaguya_TC` (the existing `tier_d_01` row leaves
    it blank, which would render `? vs LOLA_LDEM`), `ref_instrument=LOLA_LDEM`, GSDs from each
    pair's `PROVENANCE.md`. Restart the app afterwards (`catalogue_row` is `st.cache_data`-cached).
    Reconcile with the existing `tier_d_01` row rather than simply appending -
    `ops/PLAN_TO_9_SEP.md:159` already flags the duplicate.
11. RESOLVED Day 7 (`c958eb0`), without touching frozen `core/` - the readout now prints
    `= 0.0086 m on the ground ... SCALE FROM THE CATALOGUE, NOT THE LABEL`, so the metres are
    there and their weaker provenance is stated beside them. Original report: **`pair_01`
    carries no map scale, so its headline number has no metres.** Neither `.tif`
    label declares a GSD, so `meta_reference.gsd_mpp` is `None` and the readout says
    `METRES NOT AVAILABLE`. The catalogue and `PROVENANCE.md` both record 0.22977 m/px. Invariant
    2 wants the metres beside every pixel figure. Either the pipeline accepts a catalogue GSD
    (touches frozen `core/`, argue it first) or the Q&A answers it in words. The UI takes the
    metres form automatically the moment that value is non-null.
12. RESOLVED Day 7 (`03ea293`) - rewritten in the same commit that catalogued the Tier D pairs;
    it now says what the pair is and that neither label carries a map scale. Original report:
    **`pair_01`'s catalogue note still says its files "were not present during repository audit"** -
    true on Day 3, not now, and it is one click from a judge in the sidebar.
13. RESOLVED Day 7 (`2d2bb5e`) - the integration guide's `st.title` sketch is marked
    superseded, and `demo-medic.md` now `cd`s to the repo root in both places and says why.
    Original report: **Three documents describe the old UI**: `docs/SAMARTHA_INTEGRATION_GUIDE.md:237` shows a
    `st.title` that no longer exists, and `.claude/agents/demo-medic.md:97,118` launch the app
    without saying to `cd` to the repo root first.

## Open questions

- **Gate 5 (Day 10) needs all six to answer cold**, and the working model means five of them have
  not touched the code for days. Their briefs exist in `ops/briefs/`. Nobody has scheduled the
  rehearsal. This is the largest unmanaged risk left.
- The rest of the grading rubric. **Novelty is 25% - CONFIRMED Day 5.** The remaining 75% is still
  inferred.
- Submission deadline, 15 vs 20 Sep (known issue 7).

## Day 7 (5 Sep) - what landed

Nine commits. My half of the day's list is done; steps 1 (message the five about Gate 5) and 6
(Team ID + Team Name into slide 1) are Samartha's and were running in parallel.

| commit | what |
|---|---|
| `68b3680` | the eight design-lens findings - the verdict a stranger can read aloud, Tier D stops reading as a failure |
| `03ea293` | the two Tier D pairs catalogued; the novelty pair stops calling itself "not evidence" |
| `591ec5e` | sub-pixel ships ON, the docs said OFF; the append-only log now enforces itself |
| `43d1692` | the cache stamps `-dirty` when the tree that produced it was |
| `cc5890e` | **the deck's headline trust figure was not in the log** - now appended; five docs migrated |
| `2d2bb5e` | the demo script (it did not exist), two Q&A answers, the docs describing the old UI |
| `c958eb0` | pair_01 gets its metres, with the scale's provenance stated beside them |

**Three findings worth knowing about, all now closed:**

1. **Invariant 1 was broken by the number we most want to say.** The deck's
   0.123 px / 99.0% / 817 cells had no row in `results_log.csv`; it lived only in a derivation
   the calibrate script overwrites. Appended as `reliability_calibration_envelope`.
2. **The append-only log had been edited once** - commit `f788a17`, a test-pollution row, found
   with the exact command `CLAUDE.md` tells auditors to run. Documented, not hidden, and a test
   now runs that command on every `pytest`.
3. **`core/subpixel.py` argued against the shipped default and mislabelled its own evidence**,
   calling a per-match endpoint error `rmse_gt_px`. Anyone revising from it - or from Canonical
   Facts, which said "shipped OFF" - would have told a judge the opposite of the truth.

## Still open, and they are Samartha's

- **Gate 5 (Day 10) needs all six.** Nobody has been messaged. Longest lead time on the board.
- **Team ID + Team Name** - the only thing between us and a submittable deck.
- **Gate 3 is tomorrow (Day 8).** Recruit the stranger; hand them the laptop and say nothing.
- **Gate 4 (Day 9) is the formal three wifi-off runs**, and it needs the physical machine.
- The demo script exists now but **has never been read aloud with a timer**.

## In flight - resume this first

Nothing is half-written; the tree is clean and every test passes. **The two HIGH design findings
above are the first thing to do tomorrow**, before the Gate 3 stranger sits down.

**`demo-medic` was launched at wrap and stalled with no verdict** (no progress for 600 s). Do not
assume its checklist is unexamined: most of it was verified directly this session, by command.

| demo-medic check | result, this session |
|---|---|
| Runtime files that are gitignored are present | `weights/loftr_outdoor.pt` 46,348,591 bytes; 4 cached pickles; 4 pair directories |
| CPU only | torch 2.13.0+cpu, `cuda False`; no device code in `core/` |
| Config survives either working directory | from repo root AND from `app/`: `base='light' watcher='none' stats=False` |
| No network on the demo path | `test_no_network_access_anywhere` and the skin-URL test pass; no `http` / `url(` / `@import` |
| Runs repeatedly without a restart | the app was restarted and driven 7 times; cached path on 3 pairs plus one live LoFTR run (19.1 s, correct residual); the stale-result paths are pinned by the radio and selector reset tests |
| Hardcoded absolute paths | found: the cached pickles store this machine's paths. No longer fatal - the plate guard renders a void and an `IMAGES NOT READABLE` strip instead of crashing. Known issue 9 |

**What is genuinely NOT done: the formal Gate 4 procedure** - three consecutive clean runs on
Samartha's laptop with the wifi physically off. That is Day 9's gate and needs the machine, not an
agent. The manual procedure is in `.claude/agents/demo-medic.md`; note that file still tells you
to launch without `cd`-ing to the repo root, which is known issue 13.

## Not doing - settled

Bet A (closed) - a cross-sensor chase - a pyramid - a new matcher - any VM/cloud - re-litigating
the refinement default - **any further algorithm work, Gate 2 froze it** - nightly task specs for
five teammates, while the working model is Samartha alone.
