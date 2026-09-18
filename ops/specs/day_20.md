# Day 20 specs — written Fri 18 Sep 2026, for Sat 19 Sep (Day 21)

Every dependency below was checked against `origin/main` on 18 Sep. Paste each section into a GitHub Issue assigned to that person.

**Why these tasks, and why they are small.** The internal round was on Fri 11 Sep. **The repo does not record the result**: not the Round 1 shortlist, not how Round 2 went, not whether the SPOC is nominating us to the national portal. Every task below is useful **whichever way it went**. Each one fixes drift in a document you own, or writes down something only you know. No new experiments. No new numbers. Nothing outside your own folder.

**Everyone, step 0, before anything else (10 min):**
```
git status
git pull
```
You are 50–65 commits behind: nobody but Samartha has pushed since 3 Sep. If `git status` shows modified files from early September, **stop and post in chat before pulling.** Don't let an AI assistant "resolve" a merge conflict for you.

**Everyone, last step, only if you were at the college on 11 Sep (15 min):** post the **round record** below as a comment on your Issue, not as a file. Samartha copies all of them into `ops/STATUS.md`. **If you were not there, write "not present" and stop.** Don't rebuild it from what others told you, and don't list a question you *think* they would have asked.

```
Round record — <your name>
1. At the college on 11 Sep: yes / no
2. Round 1 shortlist: shortlisted / not shortlisted / don't know
   How I know: heard it announced / told by <who> / guessing
3. In the Round 2 room: yes / no / we had no Round 2
4. Questions I heard judges ask, as close to their words as I remember:
   - Q: "..."  | answered by: <who> | what was said, roughly: "..."
5. Anything I heard about national nomination: "<exact words>" said by <who>, or "nothing I heard"
```

| Person | Task | File touched |
|---|---|---|
| Rohan | Bring the dataset card's to-do list, B+ claim and sun-azimuth source up to date | `data/DATASET_CARD.md` |
| Samrudh | Fix three claims in the evaluation README that the results log contradicts | `evaluation/README.md` |
| Risheeth | Write the missing baselines hand-off README, with no figures in it | `baselines/README.md` (new) |
| Rishabh | Learn what changed in your module on 4 Sep, and make the README say so | `app/README.md` |
| Saniya | Record the final deck and the portal values the repo can't see | `presentation/DECK_STATUS.md` (new) |

Five different files. No two people touch the same one.

---

## [Day 21] Rohan — data/DATASET_CARD.md

### Goal, in one sentence
By the end, `data/DATASET_CARD.md` no longer shows the 1-Sep to-do list as current. Each item is marked done, superseded or not done, with a pointer. It also stops saying an unrun pair "proves" anything, and it records which source each Kaguya sun azimuth came from.

### Signature
```python
# No code. The deliverable is edits to data/DATASET_CARD.md, in exactly these places:
#   lines 8-13    the banner that asks you to re-run a row "before Gate 5"
#   line 75       "This is the pair that proves scale invariance"
#   lines 84-91   the Kaguya sun azimuth, and which file it came from
#   lines 259-269 "## Still outstanding — Rohan's queue"
```

### Acceptance criteria
1. Input: `data/DATASET_CARD.md` as on `origin/main`, plus the repo files it points at. If you can reach the Drive folder `SIH26166_DATA/raw/`, also use `TC1S2B0_01_03482S746E0433.lbl` and `.stac.json`.
2. Output: only `data/DATASET_CARD.md` changes.
   - **Banner (8-13):** keep the sentence saying Samartha filled the card on 1 Sep. Replace "before Gate 5" with a dated note that Gate 5 was scheduled for 8 Sep and is past.
   - **Line 75:** the B+ pair was *meant* to test scale invariance. It was never cut and never run. `evaluation/results_log.csv` has zero rows with tier `B+`.
   - **Sun azimuth:** add one note. The PDS label says `SOLAR_AZIMUTH_ANGLE = 284.911`. The STAC sidecar says `view:sun_azimuth = 284.90116478095`. The card's table uses 284.901 but credits the *label*. `pairs_catalogue.csv` uses 284.911 for `tier_bplus_01` and 284.901 for `pair_03_tierD` / `pair_04_tierD_native`. The two sources differ by 0.01°.
   - **The queue (259-269):** rename it "Status of the 1-Sep queue, as of 19 Sep" and give one line per item:
     - (1) Tier C: superseded on 1 Sep by `ops/specs/TIER_C_DECISION.md`. The multi-modal leg is Tier D, and `pairs_catalogue.csv` has two Tier D pairs with `status=built`.
     - (2) Tier A: selection solved, cutting failed (this card's "Cutting one is not" section). `tier_a_01` is still `identified`. Delete the "~1 hour" claim.
     - (3) SLDEM tile: superseded. SLDEM2015 doesn't reach −74°, so LOLA `ldem_60s_60m` is used (this card's SLDEM section).
     - (4) CH-3 NAC product IDs: not done, and nothing in the repo uses them.
     - (5) New: `pairs_catalogue.csv` row `pair_01` says `status=identified`, but its own notes say the files are present and in use. Recorded here, not edited there (see Do not).
3. Passes: every check under Test cases.

### Test cases
1. `no_proves`: `git grep -n "proves scale invariance" -- data/DATASET_CARD.md` → prints nothing.
2. `no_bplus_rows`: `git grep -c ",B+," -- evaluation/results_log.csv` → prints nothing (zero rows). This is the evidence for your line-75 rewrite.
3. `azimuth_values`: if you reach the Drive files, the `.lbl` line reads `SOLAR_AZIMUTH_ANGLE = 284.911 <deg>` and the `.stac.json` line reads `"view:sun_azimuth": 284.90116478095`. Both were verified on Samartha's machine. If you **can't** reach them, write the note anyway and add "not re-checked against the label by Rohan".
4. `only_one_file`: `git status --short` → exactly one line, ` M data/DATASET_CARD.md`.

### Starter code
```markdown
<!-- data/DATASET_CARD.md, replacing lines 259-269 -->
## Status of the 1-Sep queue, as of 19 Sep 2026

1. Tier C — SUPERSEDED 1 Sep. See ops/specs/TIER_C_DECISION.md. ...
2. Tier A — selection solved, cutting FAILED (see "Cutting one is not" above). ...
3. SLDEM tile — SUPERSEDED. ...
4. CH-3 landing-site NAC product IDs — NOT DONE. ...
5. pairs_catalogue.csv inconsistency — pair_01 ...
```

### Dependencies
- Needs: `data/DATASET_CARD.md` — ✅ VERIFIED PRESENT (sections at lines 8, 75, 84-91, 259)
- Needs: `ops/specs/TIER_C_DECISION.md` — ✅ VERIFIED PRESENT
- Needs: `data/pairs_catalogue.csv`, rows `pair_01`, `tier_bplus_01`, `tier_a_01`, `pair_03_tierD`, `pair_04_tierD_native` — ✅ VERIFIED PRESENT
- Needs (optional): Kaguya `.lbl` / `.stac.json` — ✅ present on Samartha's disk at `C:\Users\samar\sih26166_data\raw\`. The Drive copy is claimed by `DATASET_CARD.md:302`; the repo can't confirm it.
- Delivers to: Samartha, and anyone answering a provenance question if there is a national round.

### Do not
- **Do not edit `data/pairs_catalogue.csv`**, not even `pair_01`'s status. The demo UI prints its `notes` column word for word (`app/streamlit_app.py:880`), and `app/test_streamlit_app.py` reads it.
- Don't let an assistant "clean up" the whole card. Edit only the four places above. Keep the rejected `M108587604RE` row and the `Lattitude` spelling note; both are deliberate.
- Don't start cutting Tier A crops ("the route that will work — ~2 hrs"). That's a new experiment, not tomorrow's task.

### Time: 2 hrs

---

## [Day 21] Samrudh — evaluation/README.md

### Goal, in one sentence
By the end, `evaluation/README.md` says only what `evaluation/results_log.csv` supports about the two error metrics. It lists every file in the folder and gives a test command that runs all 24 tests.

### Signature
```python
# No code. The deliverable is edits to evaluation/README.md:
#   "## Core Files"                 add the four missing files
#   "## Running Tests"              one command that runs the whole folder
#   "## CRITICAL: ..." line 19      where rmse_gt_px really exists
#   "## CRITICAL: ..." line 20      delete "lower bound"
#   new "## The log is append-only" section
```

### Acceptance criteria
1. Input: `evaluation/README.md` and `evaluation/results_log.csv` as on `origin/main`.
2. Output: only `evaluation/README.md` changes.
   - **Core Files** adds:
     - `logger.py`: `log_result(...)`, the only way a row enters the log; `allow_failed` must be passed explicitly.
     - `swept_azimuth_curve.py`: **appends rows to the log when run.**
     - `test_shaded_relief.py`.
     - `test_results_log_integrity.py`: enforces append-only; the one known deletion is documented in `KNOWN_DELETIONS`.
   - **Running Tests:** `python -m pytest evaluation/ -q`, using the project venv.
   - **Line 19:** say that `rmse_gt_px` is exact ground truth only where we built the transform ourselves: tier `synthetic` and tier `same-frame fractional shift`. On Tier D, most rows leave it blank. The four that fill it (`pair_04_tierD_native`, method `ours_loftr`) measure against an offset **estimated by FFT cross-correlation**, not a known transform, and their own `notes` say so. Never quote a Tier D number as an accuracy.
   - **Line 20:** delete "serves as a lower bound on error". Use Canonical Facts §7 instead: held-out fit residual, not accuracy. Cite the row in test case 1 as the worked example.
   - **Append-only section:** rows are only ever appended. The file starts with a BOM, so read it with `encoding="utf-8-sig"`. The garbled `â€”` in a few early notes stays, because fixing it would be an edit.
3. Passes: `python -m pytest evaluation/ -q` → 24 passed, 0 failed (the count on Samartha's machine).

### Test cases
1. `residual_is_not_a_lower_bound`: run the snippet below → it prints `0.15552175045013428 0.4571960584047365`. The held-out residual is about three times the true error on the same row, so it isn't a lower bound.
2. `where_ground_truth_exists`: the second line prints `['D', 'same-frame fractional shift', 'synthetic']`, and the third prints `ours_loftr` four times.
3. `old_claims_gone`: `git grep -n "lower bound" -- evaluation/README.md` → nothing. `git grep -n "test_metrics.py -v" -- evaluation/README.md` → nothing.
4. `log_untouched`: `git diff --stat` → only `evaluation/README.md`. `git diff evaluation/results_log.csv` → empty.

### Starter code
```python
# run from the repo root; read-only, writes nothing
import csv
rows = list(csv.DictReader(open("evaluation/results_log.csv", encoding="utf-8-sig")))
r = [x for x in rows if x["pair_id"] == "ohrc_fracshift_x+0.50_y+0.50" and x["method"] == "ours_loftr"][0]
print(r["rmse_gt_px"], r["residual_px"])
print(sorted({x["tier"] for x in rows if x["rmse_gt_px"].strip()}))
print([x["method"] for x in rows if x["tier"] == "D" and x["rmse_gt_px"].strip()])
```

### Dependencies
- Needs: `evaluation/logger.py:log_result` — ✅ VERIFIED PRESENT at `evaluation/logger.py:14`
- Needs: `evaluation/metrics.py:evaluate` — ✅ VERIFIED PRESENT at `evaluation/metrics.py:12`
- Needs: `evaluation/test_results_log_integrity.py` (`KNOWN_DELETIONS`) — ✅ VERIFIED PRESENT
- Needs: `docs/00_CANONICAL_FACTS.md` §7 — ✅ VERIFIED PRESENT (line 245)
- Delivers to: anyone answering "how do you know it works?", and Samartha. **Also post one line on this Issue:** Canonical Facts §7 says `rmse_gt_px` applies to "Synthetic + Tier D only". That is the same drift in Samartha's file, so he fixes it there; you don't.

### Do not
- **Do not open `results_log.csv` in Excel and save it.** Excel rewrites the encoding and quoting, and `test_results_log_integrity.py` will fail. Don't "fix" the `â€”` either.
- **Do not run `python -m evaluation.swept_azimuth_curve`**, or anything that calls `log_result`. It appends new rows, and that means new numbers.
- Don't edit `docs/00_CANONICAL_FACTS.md`. Report the §7 line; Samartha fixes it.

### Time: 2 hrs

---

## [Day 21] Risheeth — baselines/README.md

### Goal, in one sentence
By the end, `baselines/` has a README that tells a stranger which files are live, which are superseded and which are scratch. It also says how to run each one safely, where the classical numbers really live, and the two known limitations, all without quoting a single figure.

### Signature
```markdown
# baselines/README.md — exactly these headings
## What this folder is
## Files: live / superseded / scratch
## How to run (and which flags write to the evidence log)
## Where the numbers are
## Known limitations
```

### Acceptance criteria
1. Input: the files in `baselines/`, and the method column (`SIFT` / `ORB` / `AKAZE`) of `evaluation/results_log.csv`.
2. Output: one new file, `baselines/README.md`.
   - **Files table:**
     - Live: `sift_baseline.py`, `orb_baseline.py`, `akaze_baseline.py`, `settings.py` (the one shared Lowe ratio), `run_all_baselines.py`, `sweep_baselines.py`, `make_test_pair.py`, the three `test_*.py`.
     - Superseded: `run_real_baselines.py` (its own docstring says so) and `real_ohrc_results.csv` (that script's output: invented columns like `dx_px`, and **no row in `results_log.csv`**, so not quotable).
     - Scratch: `results.csv`, overwritten on every run of `run_all_baselines.py` (`run_all_baselines.py:69`, `SCRATCH_CSV`).
   - **How to run:** the commands from the docstrings. State that `--log` on either script **appends to the evidence file**.
   - **Where the numbers are:** `results_log.csv` rows with method SIFT/ORB/AKAZE. Pair ids: `pair_01` (a same-frame wiring fixture, not validation), `tier_d_01` (the superseded id for `pair_03_tierD`), `synthetic_dNNN_*` (Gate 2 criterion 5) and `synth_sun_NNN` (Samrudh's curve). **Point to the rows; don't copy numbers.**
   - **Known limitations:**
     - (a) `draw_failure_gallery.py:37-38` looks for `data/pairs/{pair_id}_source.tif` at the top level, but real pairs sit one folder down (`data/pairs/pair_01/...`), so it can't load any real pair. The three committed images are `pair_test_*`, from the Day-1 synthetic test pair, not lunar data. It also scores with its own `_compute_metrics`, not `evaluation.metrics.evaluate`.
     - (b) At 0° sun difference the classical baselines beat us. Point to Canonical Facts §11; no figure in this README.
3. Passes: `python -m pytest baselines/ -q` → 0 failed. It was 28 passed on Samartha's machine; some tests may skip on yours if `data/pairs/` is empty.

### Test cases
1. `flat_path_bug_is_real`: `git grep -n "pairs_dir / f" -- baselines/draw_failure_gallery.py` → lines 37 and 38, both `pairs_dir / f"{pair_id}_..."` with no subfolder. That is the evidence for limitation (a).
2. `ohrc_csv_not_in_log`: `git grep -c "ohrc_real" -- evaluation/results_log.csv` → prints nothing (zero rows).
3. `no_figures`: `git grep --untracked -nE "[0-9]\.[0-9]" -- baselines/README.md` → every line printed is a setting (the 0.75 ratio) or a date, never a result.
4. `nothing_else_changed`: `git status --short` → exactly `?? baselines/README.md`. In particular, `baselines/results.csv` is **not** modified.

### Starter code
```markdown
# baselines/ — the classical control group (SIFT, ORB, AKAZE)

## What this folder is
<two sentences: why a control group exists; this README quotes no figures, every figure lives in evaluation/results_log.csv>

## Files: live / superseded / scratch
| File | Status | What it does |
|---|---|---|

## How to run (and which flags write to the evidence log)

## Where the numbers are

## Known limitations
```

### Dependencies
- Needs: `baselines/run_all_baselines.py` (docstring and `SCRATCH_CSV`) — ✅ VERIFIED PRESENT, lines 1-50 and 69
- Needs: `baselines/run_real_baselines.py` superseded docstring — ✅ VERIFIED PRESENT, lines 1-28
- Needs: `baselines/draw_failure_gallery.py:_load_pair` — ✅ VERIFIED PRESENT at line 34 (flat path at 37-38)
- Needs: `baselines/settings.py:RATIO_TEST` — ✅ VERIFIED PRESENT at line 31
- Needs: `baselines/failure_gallery/pair_test_{SIFT,ORB,AKAZE}_failure.jpg` — ✅ VERIFIED PRESENT
- Delivers to: whoever answers "was the comparison fair?" in any later round, and Samartha.

### Do not
- **Do not run `run_all_baselines.py` tomorrow, even without `--log`.** It overwrites `baselines/results.csv`, which is tracked in git. `--help` is safe. **Never** use `--log` on it or on `sweep_baselines.py`; that appends evidence.
- **Do not fix `draw_failure_gallery.py` tomorrow.** Record the limitation only. A fix creates new images that need review, and it is an "only if nominated" task.
- Don't let an assistant write a results table "from the CSV" into the README. It will retype or invent figures. Point to rows.

### Time: 2 hrs

---

## [Day 21] Rishabh — app/README.md

> **Ownership note:** `app/README.md` is not named in the ownership rule (only
> `app/change_detection.py` is), but all four of its commits are Rishabh's, so it is treated as
> his. Samartha to confirm before this Issue goes out.

### Goal, in one sentence
By the end, you can explain the 4-Sep change Samartha made to `detect_changes`, and `app/README.md` describes the detector as it actually runs now. Every figure in it is either labelled "measured before 4 Sep" or points to its row in the results log.

### Signature
```python
# No code change. The function you are documenting, as it is now (app/change_detection.py:43):
def detect_changes(img_a, img_b, gsd_mpp, thresh=30, min_area_px=50, edge_margin_frac=0.05):
    """Returns (overlay_bgr, changes). Since 80f198b: each image is stretched to uint8 by its
    OWN 2nd-98th percentile, always; a near-uniform image passes through unchanged."""
```

### Acceptance criteria
1. Input: `git show 80f198b -- app/change_detection.py`. Read all of it, including the commit message, before editing anything. It changed your module after your last push (3 Sep).
2. Output: only `app/README.md` changes.
   - **Pipeline step 2 (line 29):** replace "Convert non-uint8 images to uint8 using a common intensity scale" with the per-image 2nd–98th percentile stretch, which always runs.
   - **New section, "Normalisation — changed 4 Sep (commit 80f198b)":** three to five sentences **in your own words**:
     - what the old combined-max scaling did to a multi-modal pair, and why that gave 1 candidate instead of 183;
     - the trade-off stated in the code comment (per-image scaling also removes a genuine uniform brightness change);
     - why a near-uniform image isn't stretched.
   - **Line 1** (the "35 changes" sentence above the title): move it under a heading and label it. It is row `pair_03_tierD` / `change_detection_absdiff` / `2026-09-03T04:38:42`, **measured before the 4-Sep fix**. Beside it, point to the post-fix row: `pair_04_tierD_native` / `change_detection_absdiff+reliability_gate` / `2026-09-03T19:47:52` (183 candidates; kept 0, rejected 5, unassessable 178, all in that row's notes).
   - **"Real Kaguya Validation" (line 212):** 5544, 83,054.09 m², 89,364 m² and 67,000–112,000 m² have **no row in `results_log.csv`**. Replace each with `[TBD — results_log.csv]` and add: "measured 31 Aug, before the 4-Sep normalisation change; not re-run".
   - Optional, last 15 minutes: remove the paste artefacts (`\#`, `\_`, `&#x20;`) so the headings render.
3. Passes: `python -m pytest app/test_change_detection.py app/test_change_detection_scaling.py -q` → 16 passed, 0 failed.

### Test cases
1. `old_step_gone`: `git grep -n "common intensity scale" -- app/README.md` → nothing.
2. `unlogged_figures_gone`: `git grep -nE "83,054|5544|89,364" -- app/README.md` → nothing.
3. `row_pointers_real`: `git grep -n "2026-09-03T19:47:52" -- evaluation/results_log.csv` → one line containing `183 candidates` and `kept 0`. `git grep -n "2026-09-03T04:38:42" -- evaluation/results_log.csv` → one line containing `35 candidate changes`.
4. `module_untouched`: `git diff --stat` → only `app/README.md`. `git diff app/change_detection.py` → empty.

### Starter code
```markdown
<!-- app/README.md, new section after the pipeline list -->
## Normalisation — changed 4 Sep 2026 (commit 80f198b, Samartha)

Before: <what combined-max scaling did, in your words>
Why it broke on pair_04_tierD_native: <reference vs optical DN ranges; see the commit message>
Now: <per-image 2nd-98th percentile stretch, always>
Trade-off: <what per-image scaling gives up>
Near-uniform images: <why they are not stretched; test_uncertain_change in app/test_change_detection.py>
```

### Dependencies
- Needs: `app/change_detection.py:detect_changes` — ✅ VERIFIED PRESENT at line 43; `_stretch` at line 141; `classify` at line 5
- Needs: commit `80f198b` on `origin/main` — ✅ VERIFIED
- Needs: `app/test_change_detection_scaling.py` (7 tests) and `app/test_change_detection.py:test_uncertain_change` (line 80) — ✅ VERIFIED PRESENT
- Needs: `evaluation/results_log.csv` rows at `2026-09-03T04:38:42` and `2026-09-03T19:47:52` — ✅ VERIFIED PRESENT
- Delivers to: you, first. If there is any later round, you have to explain this module cold, and it is no longer the code you last pushed. Then Samartha.

### Do not
- **Do not restore joint (combined-max) scaling**, even if an assistant argues it "preserves real brightness changes". That trade-off is already written in the code comment, and `test_wildly_mismatched_dn_ranges_do_not_annihilate_the_darker_image` will fail.
- Don't edit `app/change_detection.py` or either test file tomorrow.
- Don't re-run the Kaguya validation to "refresh" the numbers. That's a new experiment; mark them `[TBD]`.

### Time: 2 hrs

---

## [Day 21] Saniya — presentation/DECK_STATUS.md

**Stated plainly: this is about one hour of real work, not two.** Until the outcome is known, there is no other useful task in `presentation/`. If we were nominated, Samartha will replace this with a deck-checking spec against the portal. Please don't fill the second hour.

### Goal, in one sentence
By the end, `presentation/DECK_STATUS.md` records which deck file is the final one, where the team can find it, and what the SIH portal actually shows for our Team ID, Team Name and PS ID. That last part is something the repo can't see.

### Signature
```markdown
# presentation/DECK_STATUS.md — exactly these headings
## Final deck
## Where it lives
## Portal values, as the portal displays them
## How the deck is built (do not hand-edit)
```

### Acceptance criteria
1. Input: the final PDF from Drive, and your SIH portal login if you have one.
2. Output: one new file, `presentation/DECK_STATUS.md`.
   - **Final deck:** filename `SIH26166_deck_UPLOAD.pdf`, 6 pages, 1,098,333 bytes, the SHA-256 you computed yourself, and the date you checked.
   - **Where it lives:** the Drive link, with sharing on for the team.
   - **Portal values:** Team ID, Team Name and the PS ID **copied from the portal screen**. The key question is whether the portal shows `SIH26166` or `26166`; that is Samartha's open question 3. If you have no portal access, write "not checked — no portal access".
   - **How the deck is built:** one line each: `build_deck.py` builds the slides, `make_figures.py` builds the charts, `DECK_CONTENT.md` is generated by `build_deck`.
3. Passes: the hash in test case 1 matches.

### Test cases
1. `hash_matches`: in Windows Command Prompt, run `certutil -hashfile "SIH26166_deck_UPLOAD.pdf" SHA256` → `5f6adbc7931d1896f65fa643cc2f20c090f13bef5dba755bc970aa38d08f6c18` (verified on Samartha's copy on 18 Sep). If the Drive copy gives a different hash, **write down the hash you got and flag it on this Issue**. Two different "final" decks is exactly what this file exists to catch.
2. `title_slide_agrees`: `git grep -n "^TEAM_ID\|^TEAM_NAME" -- presentation/build_deck.py` → `TEAM_ID = "SNPSU0192"` and `TEAM_NAME = "SNPSU LunaX"`. If the portal shows anything different, write both values down and flag it. **Do not edit `build_deck.py`.**
3. `text_only`: `git status --short` → exactly `?? presentation/DECK_STATUS.md`.

### Starter code
```markdown
# Deck status — <date you checked>

## Final deck
File: SIH26166_deck_UPLOAD.pdf · 6 pages · 1,098,333 bytes
SHA-256 (computed by me): <paste>

## Where it lives
Drive: <link>

## Portal values, as the portal displays them
Team ID: <copied> · Team Name: <copied> · PS ID shown as: <SIH26166 or 26166>

## How the deck is built (do not hand-edit)
```

### Dependencies
- Needs: `presentation/build_deck.py` `TEAM_ID` / `TEAM_NAME` — ✅ VERIFIED PRESENT at lines 81-82; `TITLE_META` at line 87
- Needs: `SIH26166_deck_UPLOAD.pdf` — ✅ present on Samartha's machine (gitignored); the hash above was verified there. The Drive copy is claimed in `ops/STATUS.md`, but the repo can't confirm it.
- Delivers to: Samartha, for open question 3, and for any national submission if nominated.
- **If you can't commit:** paste the file's contents as a comment on this Issue, and Samartha will commit it with you as co-author.

### Do not
- **Do not open the .pptx and re-save it or re-export the PDF.** That changes the hash, and the uploaded file is the record.
- Don't `git add -f` a PDF or PPTX (they're gitignored on purpose), and don't hand-edit `DECK_CONTENT.md` (it's generated).
- Don't type the Team ID or PS ID from memory. Copy them from the portal or write "not checked".

### Time: ~1 hr (stated honestly; no padding)

---

## BLOCKED — do not send these

**BLOCKED: none.** Every file, line and function named above is on `origin/main` as of 18 Sep. Three parts depend on something the repo can't show, and each spec has a written fallback, so none is blocked:
- Rohan's sun-azimuth check needs the Kaguya `.lbl` / `.stac.json` on Drive. Fallback: write the note and mark it "not re-checked".
- Saniya's portal values need portal access. Fallback: "not checked — no portal access".
- Everyone's round record needs them to have been there. Fallback: "not present". An empty record isn't a failure, and if we weren't shortlisted there was no Round 2 to record.

## Sequencing risks

- **Push first.** Teammates will pull whatever is on origin.
- **Stale clones.** Teammates are 50–65 commits behind. Anyone with uncommitted early-September edits in their folder will hit a conflict on pull; step 0 tells them to stop and post.
- **No collisions tomorrow.** The five files are all different, and none is in `ops/`, `core/` or `docs/`.
- **If we were nominated and 20 Sep is the binding deadline, it is Sunday.** Any deck change (for example `TITLE_META` in `presentation/build_deck.py`) is in Saniya's folder under the ownership rule, but Samartha wrote the build script. Decide who touches it before Saturday. Saniya's spec deliberately forbids editing it.
- **`app/README.md` ownership** isn't named in the ownership rule. Confirm, or strike Rishabh's spec.
- **OneDrive** has silently reverted files on Samartha's clone before. Run `git status` after pulling teammates' pushes.
- **Test counts vary by machine.** On clones without `data/pairs/`, some baselines/app tests skip. The bar in each spec is "0 failed", with Samartha's count given for reference.

## Slipped from the plan

- **There is no plan row for Day 20/21.** `docs/TEAM_TASK_GUIDE.md` and `ops/PLAN_TO_9_SEP.md` both end at the event, so these specs come from the repo's state, not from a plan. Any next phase needs a new plan, and it depends on the unrecorded outcome.
- **New tonight, Samartha's files:** Canonical Facts §7 says `rmse_gt_px` applies to "Synthetic + Tier D only" (the log has exact ground truth only for `synthetic` and `same-frame fractional shift`); Canonical Facts §14 lists `baselines/results_table.csv` where the real file is `baselines/results.csv`. Both recorded in `ops/STATUS.md` Known issues.
- **Saniya's guide asked for `presentation/DECK_STATUS.md` in early September.** It was never committed; her spec above creates it.

---

*Drafted by the `spec-writer` agent on 18 Sep 2026; key claims (README lines, gallery path bug, residual row, deck hash, TEAM_ID/TEAM_NAME) re-checked first-hand by Samartha's session before saving.*
