# Day 23 onward (20-27 Sep 2026) - solo, Samartha

> Everything that can be built is built (20 Sep 01:10, `27266f8`). The evidence freeze is FROZEN
> at `49bdad9`, the deck is filled and checked twice, and the PDF exporter works on this laptop.
> What remains needs a person, the portal, or both. Read `ops/STATUS.md` first.

## To submit (about 15 minutes; do it early - the portal closes Tue 30 Sep)

1. **Team ID.** Read it off the SIH portal.
   - Set `TEAM_ID` in `presentation/build_deck.py`, spelled exactly as the portal shows it.
   - `python -m presentation.build_deck` must print `AUDIT: clean`.
2. **PDF.** Close PowerPoint.
   - Run `PYTHONPATH=<dir with pymupdf> python -m presentation.export_pdf`; it must print
     `PDF CHECK: clean`.
   - Don't touch the keyboard for the ~20 s while windows flash.
   - Open `presentation/SIH26166_LunaXX_deck.pdf` and read all 6 pages by eye.
3. **Portal fields.** Paste from `ops/national_round/SUBMISSION_FIELDS.md`: the PS, then the
   title and description (the longest version that fits). Upload the PDF.
4. **Record it.** Screenshot the confirmation. Write the time and Team ID into `ops/STATUS.md`,
   commit, and push.

## Worth doing if there is time (in this order)

5. **Gate 4 by hand.** Wifi off, run `streamlit run app/streamlit_app.py`, and complete three
   clean runs in a row: pair_01, pair_04_tierD_native, sac_ohrc_nac_w06 (plus the 4
   downloads), site_tc_morning_mi1548_w01.
6. **Demo video.** 2 minutes, narrated by you, unlisted. Add its link to slide 6 (`S6` in
   `build_deck.py`), then rebuild and re-export. Nothing else on the deck changes.
7. **Repo link.** Only if you want judges to see the code: make the GitHub repo public, then add
   the link to slide 6. It is private now. This decision is yours.
8. **Close the old Claude sessions** (17-19 Sep). They hold about 12 GB of memory commit, and
   that is the most likely cause of the cv2 crashes (Known issue 8).

## If anything in core/, evaluation/ or ops/ changes before submission

Re-freeze: commit, run `python -m ops.freeze` (about 110 min), and `--check` must say FROZEN.
Then re-read every row of `presentation/DECK_V2_DRAFT.md` against the new REPORT.md, rebuild,
re-export, and run `claim-checker`. Otherwise do not touch the code.

## After 27 Sep

- A walkthrough for the five teammates, in case LunaXX reaches the finale; nobody but
  Samartha can explain the national-round code yet.
- SIH26227 has its own repo and session; its go/no-go is Fri 25 Sep.
