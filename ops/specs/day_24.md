# Day 24 onward (20-27 Sep 2026) - solo, Samartha, after the audit

> The national-round audit (`ops/national_round/AUDIT_PROMPT.md`) ran on 20 Sep in two passes,
> 02:30-05:00 and 09:00-12:45. Its report is `ops/national_round/AUDIT_REPORT.md`. The evidence is
> FROZEN at **`7dd4e5b`** (10/10 steps); the deck is **v4**, `AUDIT: clean`, `PDF CHECK: clean`.
> The tag `submission-v1` (= `0297936`) and `presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf` keep
> the pre-audit submission. Read `ops/STATUS.md` first.

## Done for you on 20 Sep - do not redo these

- **Backups made.** `C:\sih26166_backup\` holds `weights/` (`loftr_outdoor.pt` verified as sha256
  `6d2e110d…`), `data/pairs/` and `demo_cache/` (181 files, 103 MB, re-synced 18:00 after the
  console's eight extra caches were added). All three are gitignored and live inside OneDrive, which has reverted
  files in this repo before, so **put `C:\sih26166_backup\` on a USB stick** - that is the one
  step left and it is not recoverable if skipped.
- **The six demo caches were rebuilt at `f928995`.** The four older ones were computed before the
  F12 fix and carried its bug (an empty inlier flag in the exported match table). All six now
  show a clean identification plate - no "CODE IS NOW" caution - and three consecutive AppTest
  runs of the four demo pairs passed with sockets blocked (0.6-3.2 s per cached align).
  `demo_cache/` now holds **14** pairs, not 6: eight more were added for the Mission Console's
  roster. The extra eight are display-only and are not on the Gate 4 path.
- **The Mission Console was built** (`web/`, published private at
  https://claude.ai/artifact/LbbZKdvnVYCCBbPjEBZCA9). It replaces nothing:
  `app/streamlit_app.py` is untouched and is still what Gate 4 tests. Operator guide in
  `web/README.md`; rebuild with `python -m web.build_console`.
- **A silent 108 s explainer video** is at `web/dist/mission-console.mp4`, with its script in
  `web/narration.md`.

## To submit (about 15 minutes; the portal closes Tue 30 Sep)

1. **Read the PDF cold**, all six pages: `presentation/SIH26166_LunaXX_deck.pdf` (v4). Every page
   was rendered and read on 20 Sep, but you are the one presenting it.
2. **Portal fields**: paste from `ops/national_round/SUBMISSION_FIELDS.md`. The long description
   is 1,804 characters - if the portal rejects it, the short one (507) is there and is true.
   Upload the PDF.
3. **Record it**: screenshot the confirmation; write the time and Team ID into `ops/STATUS.md`;
   commit, push.

## The one measurable improvement left (needs you: PRADAN login)

4. **TMC-2 with a closer Sun.** Download
   `ch2_tmc_ncn_20251107T2205342105_d_img_d18.zip` (calibrated nadir; PRADAN Table View,
   TMC-2, 2025-11-07; ~0.6-0.9 GB) and unzip it under
   `C:\Users\samar\sih26166_data\pradan\tmc2\` so that
   `data\calibrated\20251107\ch2_tmc_ncn_20251107T2205342105_d_img_d18.{xml,img}` and
   `geometry\calibrated\20251107\ch2_tmc_ncn_20251107T2205342105_g_grd_d18.csv` exist. Then, on
   the clean tree at `7dd4e5b`+docs (no code change):
   ```
   python -m ops.cut_pradan_pairs ohrc-tmc --tmc-product ch2_tmc_ncn_20251107T2205342105_d_img_d18
   python -m ops.run_real_pairs "sac_ohrc_tmc20251107_w*" --log
   python -m ops.make_report
   ```
   This is the only pass over SAC's frame with the Sun near the OHRC's (~9° in azimuth), so it is
   the one test that could turn "OHRC → TMC-2: all 4 refused" into a positive result. If windows
   are accepted, add one clause to slide 4's hard-band bullet ("a second pass with the Sun 9°
   apart in azimuth: N/4 accepted") and one row to DECK_V2_DRAFT.md; rebuild, re-export,
   `claim-checker`. **If they are refused, say so on the slide** - a second refusal at a close Sun
   is a stronger statement about relief and viewpoint than silence is.
   **Cut-off: Thu 24 Sep 18:00** for any evidence; after that it is the Q&A answer already written
   in DECK_V2_DRAFT.md.

## Two decisions with dates on them

5. **Console link on slide 6 - decide before Fri 25 Sep 22:00**, the text freeze. Slide 6 is the
   only slide with room. If yes: open the artifact, use its Share menu to make it viewable, put
   the URL in `S6` of `build_deck.py`, rebuild, re-export, re-run `claim-checker`. **It is private
   right now** - a judge clicking a private link sees a sign-in page, which is worse than no link.
6. **Gemini key for the voice-over.** With it:
   `python -m web.voice --key <KEY>` then `python -m web.cut` gives the narrated ~4.7 min version.
   `web/voice.py` has never made a live call, so expect to debug the first one. Watch the silent
   cut first - fixing pacing before the voice is generated is much cheaper than after.

## Optional, in this order

7. **Repo public**: the deck says every number traces to the logs; a reviewer can only check
   that if the repo is public. Your decision, and it is separate from the console link above.
8. **Gate 4 by hand**: wifi off, `streamlit run app/streamlit_app.py`, the four cached pairs
   (`pair_01`, `pair_04_tierD_native`, `sac_ohrc_nac_w06` with the four downloads,
   `site_tc_morning_mi1548_w01`).
   **Re-run the caches on the final commit first** (~30 s), or every pair shows a caution-coloured
   "CODE IS NOW" plate that is a false alarm - Known issue 25:
   ```
   python -m ops.precompute_demo_cache pair_00_dryrun pair_01 pair_03_tierD pair_04_tierD_native sac_ohrc_nac_w06 site_tc_morning_mi1548_w01
   ```
9. **Close the old Claude sessions** (17-19 Sep); they hold ~9 GB of commit charge (Known issue 8).

## After submission, before the finale - the two things the audit left open

- **F18**: `ops.freeze`'s `trust` step takes its window list from the CSV it then deletes. Lose
  that file and the step cannot run, and the failure appears nowhere in its logs. The list belongs
  in the freeze state or pinned in the script. This cost a freeze on 20 Sep.
- **F19**: `ops.freeze`'s summary line adds `None` to an int when a step returns the
  precondition-failed sentinel, so a completed run ends in a traceback. Cosmetic, one line.

Both are `ops/` changes that would force another freeze, which is why they were not done before
the upload.

## If anything in core/, evaluation/ or ops/ changes before submission

Commit, `python -m ops.freeze` (90-110 min, alone), `--check` must print FROZEN, then re-read
every row of `presentation/DECK_V2_DRAFT.md` against the new REPORT.md, rebuild, re-export,
`claim-checker`. Docs and `presentation/` edits do not need this. Two freezes were lost on 20 Sep
to crashes in code that ran only at the end of the job - if you touch the trust step, rehearse it
on a small synthetic calibration file before spending 100 minutes.
