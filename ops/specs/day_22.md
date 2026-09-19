# Day 22 (Sun 20 Sep 2026) - solo plan, Samartha + Claude

> Team split suspended for the national push (decision 18 Sep): no teammate specs, `spec-writer` not
> run. Every input below was checked on disk at the Day-21 wrap (19 Sep ~11:30) unless the item says
> it fetches it. Read `ops/STATUS.md` first.

## Track A - SIH26166 (this repo)

1. **Scale rungs at the 74 S site.** OHRC <-> Kaguya TC ortho (`TCO_MAP_02_S72E042S75E045SC`, on disk,
   ~40.8x) needs a chunked reference (four 640-px TC chunks) or the W8 tiled driver - build the chunked
   reference in `ops/cut_site_pairs.py`, not a new core module. OHRC <-> LOLA hillshade
   (`<data>/raw/dem_site_60m.npy`, `evaluation/shaded_relief.py`) as the declared-failure rung,
   logged with `--allow-failed`. Done when: both rungs are rows in real_pairs_log and REPORT.md shows them.
2. **SAC's own benchmark pairs.** Fetch LRO NAC `M1350459544RE` (pairs with OHRC
   `20210401T2357376656`) and `M165491149RE` (pairs with OHRC `20200824T0806596861`) from the LROC
   PDS archive (public; product page gives corners + sub-solar point, as for the 74 S NACs). Neither is
   on disk and neither is in `nac_site_pages.json`. Cut with `ops/cut_pradan_pairs.py` (local
   equirectangular; add an `ohrc-nac` kind and a coarse correction of the NAC corner prior against the
   OHRC, as `cut_site_pairs.correct_against` does). Done when: OHRC <-> NAC rows exist for SAC's frame.
3. **Known issue 3 (tiny-frame verdict).** In `core/reliability.py`: a frame with 0 measurable cells
   and few inliers must say `unconfirmed`, not `agrees`. Test with the `site_tc_ortho_iirs1555_w10`
   case (6 inliers, 112-px reference). Then re-log the IIRS pairs. Done when: test + re-logged rows.
4. **MiLOI figure.** `presentation/make_figures.py` fig7: success vs sun-vector angle for ours and the
   three baselines from `evaluation/miloi_log.csv` only, with n per bin and the S3-truth caveat in the
   caption. Done when: fig7 exists and `make_figures` audits clean.
5. **Deck v2 text** (`presentation/DECK_V2_DRAFT.md` -> `build_deck.py`): title slide `LunaXX`, the
   trust-layer story with the three-state MiLOI cross-tab, fore/aft as the real viewpoint rung, SAC
   site. Every number `[TBD - results_log.csv]` until the freeze. Run `claim-checker`.

## Track B - SIH26227 (session 2, `C:\Users\samar\dev\sih26227`)

6. Continue its PLAN.md; the go/no-go is Fri 25 Sep evening.

## Samartha (manual)

7. Portal questions (STATUS Open questions 1). 8. SPOC questions (Open questions 2).
9. Before any overnight run: Settings -> Power -> never sleep when plugged in.

## BLOCKED

None. Item 2 fetches its own inputs (public data, no login).
