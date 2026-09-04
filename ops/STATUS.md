# STATUS — end of Day 6 (4 Sep 2026)

> Rewritten in full at the end of every session. Previous STATUS is in git history (`ff2d8ec`).
> ⚠️ The venv is `C:\Users\samar\venvs\sih26166`; call its `python.exe` directly. A bare `python`
> fails here with `ModuleNotFoundError: numpy` — that is the missing venv, not a broken build.

---

## Position

```
Day 6 of 11  |  5 days to the event  |  Internal hackathon: 9 SEP 2026 (confirmed)
Gate 1: PASSED (Day 5)      Gate 2: ✅ PASSED (Day 6, one day early)
Next: Gate 3 on Day 8 (6 Sep) — a stranger operates the UI unaided
Novelty weight: 25% (confirmed)
```

**🔴 The working model changed today.** Samartha is building the entire project alone — no
handoffs, no work routed to teammates. `ops/specs/DAY6_HANDOFFS.md` was written before that
decision and is **superseded**; it is kept only for the diagnostics inside it (Risheeth's two
traps, the change-detection root cause). Ownership invariants in `CLAUDE.md` §4 no longer route
work, though the per-person briefs in `ops/briefs/` still matter for Gate 5.

## ✅ Gate 2 PASSED — all six criteria, evidence in `ops/GATE2_EVIDENCE.md`

At the stated sun-azimuth difference of 15°, medians over 5 off-grid shifts:

| # | Criterion | Required | Measured |
|---|---|---|---|
| 1 | `rmse_gt_px` | < 0.5 | **0.0856** |
| 2 | `inlier_ratio` | > 0.60 | **0.9774** |
| 3 | `grid_coverage_fraction` | ≥ 0.80 | **1.0000** |
| 4 | `distribution_cv` | < 1.0 | **0.4006** |
| 5 | ≥2× best of SIFT/ORB/AKAZE, same pair same scale | ≥ 2.0× | **2.88×** |
| 6 | Tier D: matches + degradation in metres | stated | **231 m ± 216 m**, contradicted |

Criterion 5 was closed by new `baselines/sweep_baselines.py`, which regenerates each pair through
`core.pipeline._synthetic_pair` — the same function our own run calls — so both arms see
byte-identical files. **Per the gate rule the algorithm is now frozen.**

## What Day 6 measured, and the three results that were not expected

**Move 2 (the failure-detection rate) is done** — sweep extended to 8 deltas
(0/15/30/45/60/90/120/180), 40 pairs, 2,560 cells, all logged. Full write-up:
`ops/MOVE2_FAILURE_DETECTION_DAY6.md`.

1. **Detection: 77% at a 120 m failure threshold, with a 0% false-alarm rate** (27 correct pairs,
   zero false alarms). At 240 m it is 10/10 detected at a 9% false-alarm cost.
2. **180° is our *easiest* hard case, not our hardest** — 0.080 px, better than our own 15° number.
   The failure peak is **90°**. A 180° flip *inverts* the shading and gradient-orientation
   normalisation is invariant to contrast inversion; 90° *rotates* it, and nothing covers that.
   **The classical arm proves the mechanism: SIFT at 180° is 4,971 px wrong.** If our recovery were
   a renderer artifact, classical would recover too. Quote it as a SUCCESS RATE - we scored 5/5,
   classical 1/15 - not as the 62,519× ratio, which rests on that single surviving run.
3. 🔴 **At 0° sun difference classical BEATS us** — SIFT 0.044 px vs our 0.086. There is no
   illumination problem to solve at 0°, and SIFT is the better sub-pixel corner localiser. **This
   goes on the slide.** The claim is *illumination robustness that grows with the sun difference*,
   not *a better matcher*.

**Our blind spot, stated before a judge finds it:** between 45° and 60° we are wrong and do not know
it — at 60° the transform is 142.7 m out and the contradiction flag stays down.

**Quote the envelope figure, not the pooled one.** Inside Δaz ≤ 30°, verified cells are
**0.123 px = 7.4 m, 99.0% under half a pixel, n=817**. The Day-5 pooled 0.162 px averaged over
angles we do not claim.

## 🔴 The deck exists, and the "blocker" was never real

`presentation/SIH26166_deck.pptx` → **`SIH26166_deck.pdf`, 6 slides, official template.** Both
gitignored by rule; they live locally and in Drive.

- **The template was always downloadable.** Every guide said `sih.gov.in` 403s non-browser agents.
  It 403s the *default* user agent. One `-A` flag and it serves: **924,505 bytes, sha256
  `ce3e5dee…`, matching `CLAUDE.md` exactly.** `presentation/` sat empty for six days behind a
  blocker that did not exist. The exact command is in `presentation/DECK_CONTENT.md`.
- 🔴 **The submission is a PDF, not a `.pptx`** — the instructions slide says so outright, and it
  was written down nowhere in this project until today.
- **The template's pointer text is never edited**, per *"without changing the idea details
  pointers"*. It is moved to the top, small and grey; our content goes in a new box below.
- Rebuild: `python -m presentation.make_figures && python -m presentation.build_deck`, then export
  to PDF.
- **Still blank: Team ID and Team Name on slide 1.** Only the SIH portal has these.

**Two figures, generated from the evidence rather than drawn** (`presentation/make_figures.py`, reads
`results_log.csv` at run time so a figure cannot drift from the log):
`fig1_sun_angle_vs_error.png` (ours vs classical across sun angle — the 20-second moment) and
`fig2_trust_calibration.png` (the three trust states separating by true error).

## Smoke test — exit codes observed, not inferred

| Check | Result |
|---|---|
| `pytest -q` | **218 passed**, exit 0 |
| `pytest evaluation/ -q` | 21 passed, exit 0 |
| `import core.pipeline` | ok, exit 0 |
| `python -m core.pipeline data/pairs/pair_01` | `residual_px 0.03761504064805703`, 63/64 verified — the pinned Gate-1 number, exact |
| `pytest app/ -q` | 28 passed (12 UI + 7 new scaling + 9 existing) |
| deck render | 6 slides exported to PNG and **every one inspected by eye** |
| `git diff results_log.csv` | append-only; **274 rows**, 0 removed |

## Known issues — do not re-report

1. ✅ **RESOLVED — known issue 9 was a real bug, not a cosmetic mismatch.** `detect_changes`
   normalised only non-uint8 input *and* scaled both images by their **combined max**. On
   `pair_04_tierD_native` the reference peaks at 37,488 DN and the aligned optical image at 2,040 —
   dividing both by 37,488 crushed the optical image to a 2–98 percentile range of **[0, 5]**, so
   nothing could exceed `thresh=30`. The "1 candidate" was total contrast collapse, **on exactly
   the multi-modal case this project is about.** Fixed with a robust per-image percentile stretch
   that always runs. Both entry points now report **183 candidates, 0 kept / 5 rejected / 178
   unassessable** — the UI numbers were right all along. Pinned by 7 tests in
   `app/test_change_detection_scaling.py`.
2. **Six documents still quote the superseded Day-5 pooled figure** (0.162 px / 926 cells / 92% /
   98%): `ops/briefs/BRIEF_SAMARTHA.md`, `BRIEF_SAMRUDH.md`, `BRIEF_SANIYA.md`,
   `ops/PHASE1_NOVELTY_DECISION.md`, `ops/QA_ANSWERS.md`, and this file's history. They remain
   *traceable and true* for the 20-pair population, but should point at the envelope figure.
   **The deck and `QA_ANSWERS.md` §4–7 already use the correct one.**
3. **`core/reliability_calibration.csv` is a derivation, not a log** — `reliability_calibrate.py`
   opens it `"w"`. Running a *partial* sweep silently discards the rest. **Always run the full
   delta list.** A pre-run backup is cheap; take one.
4. **`presentation/sih_template.pptx` is gitignored**, so a fresh clone has no template. The curl
   command is in `DECK_CONTENT.md`.
5. **No real pair with a sun difference.** MiLOI (github.com/Bin501/CNSFM) remains the route;
   ground-truth format unverified. Not attempted.
6. **`redetect()` still unwired** — claim removed, not deferred.
7. **Submission deadline discrepancy** (15 vs 20 Sep) — still unasked of the SPOC.
8. Frames whose cells are narrower than 24 px (pair_03) fall back to the whole-frame peak; the
   `basis` field says so.

## Next session (Day 7, 5 Sep) — in order

1. `/next`, `pytest -q`, both Gate-1 commands.
2. **Team ID + Team Name into slide 1** from the SIH portal, then re-export the PDF. This is the
   only thing standing between us and a submittable deck.
3. **Gate 3 is Day 8 (6 Sep) — recruit the stranger now.** Someone who has never seen this project.
   The UI must be operable with nobody speaking.
4. **Re-run `ops/precompute_demo_cache.py`** — `app/change_detection.py` changed today. The cached
   pipeline results are unaffected (change detection runs live), but re-run before Gate 4 regardless.
5. Migrate the six documents in known-issue 2 to the envelope figure.
6. **Gate 4 is Day 9 (7 Sep): CPU-only, wifi off, 3 consecutive clean runs.** Verify `weights/` and
   `demo_cache/` open cold. `demo-medic` is the agent for this from Day 9.
7. Demo script (3:00) and the rest of the Q&A bank — `QA_ANSWERS.md` gained four entries today
   (§4–7) covering the 0° loss, the 180° mechanism, the detection rate, and "how do we know your
   numbers are right".
8. Optional: MiLOI (2-hour timebox), the reliability *diagram* proper (fig 2 already delivers most
   of Move 3).

## Not doing — settled

Bet A (closed) · a cross-sensor chase · a pyramid · a new matcher · any VM/cloud · re-litigating
the refinement default · **any further algorithm work — Gate 2 froze it.**
