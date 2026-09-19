# Day 24 onward (20-27 Sep 2026) - solo, Samartha, after the audit

> The national-round audit (`ops/national_round/AUDIT_PROMPT.md`) ran on 20 Sep, 02:30-05:00.
> Its report is `ops/national_round/AUDIT_REPORT.md`. The evidence is FROZEN at `b678272`
> (10/10 steps, 90 min); the deck is v3, `AUDIT: clean`, `PDF CHECK: clean`. The tag
> `submission-v1` (= `0297936`) and `presentation/SIH26166_LunaXX_deck_v1_SAFE.pdf` keep the
> pre-audit submission. Read `ops/STATUS.md` first.

## To submit (about 15 minutes; the portal closes Tue 30 Sep)

1. **Read the PDF cold**, all six pages: `presentation/SIH26166_LunaXX_deck.pdf` (v3). If you
   prefer v2, `git checkout submission-v1 -- presentation/build_deck.py`, rebuild and re-export -
   but v3 carries the sub-pixel line, the measured multi-modal result and the hard-Sun trust
   result that v2 lacks.
2. **Portal fields**: paste from `ops/national_round/SUBMISSION_FIELDS.md` (the long description
   now has the multi-modal and runtime sentences). Upload the PDF.
3. **Record it**: screenshot the confirmation; write the time and Team ID into `ops/STATUS.md`;
   commit, push.

## The one measurable improvement left (needs you: PRADAN login)

4. **TMC-2 with a closer Sun.** Download
   `ch2_tmc_ncn_20251107T2205342105_d_img_d18.zip` (calibrated nadir; PRADAN Table View,
   TMC-2, 2025-11-07; ~0.6-0.9 GB) and unzip it under
   `C:\Users\samar\sih26166_data\pradan\tmc2\` so that
   `data\calibrated\20251107\ch2_tmc_ncn_20251107T2205342105_d_img_d18.{xml,img}` and
   `geometry\calibrated\20251107\ch2_tmc_ncn_20251107T2205342105_g_grd_d18.csv` exist. Then, on
   the clean tree at `b678272`+docs (no code change):
   ```
   python -m ops.cut_pradan_pairs ohrc-tmc --tmc-product ch2_tmc_ncn_20251107T2205342105_d_img_d18
   python -m ops.run_real_pairs "sac_ohrc_tmc20251107_w*" --log
   python -m ops.make_report
   ```
   If windows are accepted, add one clause to slide 4's hard-band bullet ("a second pass with the
   Sun 9° apart in azimuth: N/4 accepted") and one row to DECK_V2_DRAFT.md; rebuild, re-export,
   `claim-checker`. Its rows will name the commit of the run; `ops.freeze --check` counts them as
   frozen only if nothing under core/evaluation/ops changed since `b678272` - so keep the docs
   commits to docs. **Cut-off: Thu 24 Sep 18:00** for any evidence; after that it is the Q&A
   answer already written in DECK_V2_DRAFT.md.

## Optional, in this order

5. **Demo video**: 2 minutes, unlisted, narrated by you; link on slide 6 (`S6` in
   `build_deck.py`); rebuild, re-export.
6. **Repo public + link on slide 6**: the deck says every number traces to the logs; a reviewer
   can only check that if the repo is public. Your decision.
7. **Gate 4 by hand**: wifi off, `streamlit run app/streamlit_app.py`, the four cached pairs
   (`pair_01`, `pair_04_tierD_native`, `sac_ohrc_nac_w06` with the four downloads,
   `site_tc_morning_mi1548_w01`). The AppTest equivalent passed 3 × 4 runs on 20 Sep with sockets
   blocked (0.8-2.4 s per cached align; cold start 4.5 s = 1.0 s import + 3.5 s first render).
8. **Close the old Claude sessions** (17-19 Sep); they hold ~9 GB of commit charge. Another
   session's SIH26227 evaluation ran beside the freeze on 20 Sep without harm, but Known issue 8
   stands.

## If anything in core/, evaluation/ or ops/ changes before submission

Commit, `python -m ops.freeze` (90-110 min, alone), `--check` must print FROZEN, then re-read
every row of `presentation/DECK_V2_DRAFT.md` against the new REPORT.md, rebuild, re-export,
`claim-checker`. Docs and `presentation/` edits do not need this.
