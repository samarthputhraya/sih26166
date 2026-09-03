# SIH26166 — Lunar Image Registration

Registering Chandrayaan-2 imagery against reference lunar imagery under different sun angles
and at different scales, to sub-pixel accuracy, with matches spread across the frame — and, cell
by cell, telling you **where the alignment is verified, where it is weak, and where there is no
evidence at all**. When its own matcher is confidently wrong, the system says so and switches
method (`core/reliability.py`, `core/pipeline.py`).

Smart India Hackathon 2026 · ISRO problem statement SIH26166.

What is and is not validated is in `docs/00_CANONICAL_FACTS.md` §2 and §11. There is no
cross-sensor pair in this repository; do not describe any result here as cross-sensor.

## Start here

`docs/00_CANONICAL_FACTS.md` is the single source of truth — every definition, number and data
source. `docs/TEAM_TASK_GUIDE.md` is the schedule. If they disagree, Canonical Facts wins.

**The internal hackathon is 9 September 2026 = Day 11.** Confirmed by the SPOC on Day 5. Gates run
2 → 5 on Days 7 → 10; the full table is Canonical Facts §11, and the approved plan for Days 5–10 is
`ops/PLAN_TO_9_SEP.md`.

## Setup

The demo machine has **no GPU**. Everything on the demo path runs on CPU.

```
python -m venv C:\Users\<you>\venvs\sih26166     # OUTSIDE the OneDrive folder
C:\Users\<you>\venvs\sih26166\Scripts\activate
pip install -r requirements.txt
```

`python3` fails on Windows (Store alias) — use `python` or `py`.

**Activate the venv in every new terminal.** Without it, `python` on this machine resolves to a bare
3.12 install that has none of these packages, and the failure looks like a missing dependency
(`ModuleNotFoundError: No module named 'numpy'`) rather than a missing venv. Check with
`python -c "import numpy, torch; print('ok')"` before trusting a green or red test run —
**that mistake will read as "a teammate broke the build."**

## Layout

| Folder | Owner | Contents |
|---|---|---|
| `core/` | Samartha | io_loader, scale, illumination, matcher, ransac, subpixel, distribution, pipeline |
| `evaluation/` | Samrudh | synthetic_data, shaded_relief, metrics, **results_log.csv** |
| `baselines/` | Risheeth | sift/orb/akaze, failure_gallery |
| `app/change_detection.py` | Rishabh | change detection |
| `app/streamlit_app.py` | Samartha | the UI |
| `presentation/` | Saniya | deck, demo script, Q&A bank |
| `data/` | Rohan | pairs catalogue and dataset card (imagery itself lives in Drive) |

One folder per person. **Never edit someone else's folder** — that is how six people avoid merge
conflicts, and how each person stays able to explain their own module cold.

## Two rules that override convenience

**Numbers.** No figure enters a slide, demo script, Q&A answer or this README until it exists in
`evaluation/results_log.csv`. Until then write `[TBD — results_log.csv]`.

**Terminology.** `00_CANONICAL_FACTS.md` §2 defines a five-tier validation ladder. LROC NAC ↔ LROC
NAC is the *same sensor* — a sun-angle test, not cross-sensor. "Multi-modal" means visible↔infrared,
radar or elevation only. "Sub-pixel" must always name the pixel grid and give the metres equivalent.

## Data and weights

Code in git, imagery and model weights in Google Drive. Nothing over ~5 MB or binary goes in the
repo. `weights/` and `demo_cache/` are gitignored but must be populated locally before the offline
demo gate.

## The trust layer

```
python -m core.pipeline data/pairs/pair_04_tierD_native        # prints WHERE IT CAN BE TRUSTED
python -m core.reliability_calibrate --dem <dem.npy> --pixel-size 60 --sweep 0,15,30,45 --repeats 5
python -m ops.gate_tier_d_changes                              # change detection, gated by the map
python -m ops.precompute_demo_cache                            # cache run_all() for the demo
```

Every cell of the reference frame is `verified`, `weak` or `no_evidence`. The verdict on the
whole transform is a vote of the cells' own pixel correlations, which never see the matches. The
calibration run writes `core/reliability_calibration.csv` (one row per cell, with the true error)
and logs one row per pair to `evaluation/results_log.csv`.

## Performance

CPU latency, tile size and match quality: `[TBD — results_log.csv]`.
Raw Day-1 measurements are in `core/bench_loftr_cpu_results.csv`; they become quotable only once
they are reproduced into `evaluation/results_log.csv`.
