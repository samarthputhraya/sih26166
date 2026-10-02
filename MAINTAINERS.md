# Maintainers and handover

Team LunaXX (six members), Smart India Hackathon 2026, problem statement SIH26166 (ISRO). Each part of
the code has one owner in the team who can explain it end to end; the repository and its issues are
maintained by Samartha Puthraya (@samarthputhraya).

| Part | Folder |
|---|---|
| Registration pipeline, trust layer, workbench and console | `core/`, `web/`, `app/streamlit_app.py`, `ops/` |
| Evaluation: synthetic truth, metrics, the evidence logs | `evaluation/` |
| Classical baselines (SIFT, ORB, AKAZE) and the failure gallery | `baselines/` |
| Change detection on registered pairs | `app/change_detection.py` |
| Deck and figures | `presentation/` |
| Data catalogues | `data/*.csv`, `data/*.md` |

## Handing it over (to SAC, or to anyone)

- **Licence.** Apache-2.0 (`LICENSE`, `NOTICE`): use, change and redistribute, including inside ISRO,
  with no fee and no permission needed.
- **Runs where it is put.** CPU only, no GPU, no cloud service. After the LoFTR weights are fetched
  once (`python core/fetch_weights.py`, sha256-verified), nothing needs the network.
- **Install.** `pip install -r requirements.txt` (pinned, CPU torch), then `pip install -e .`, which
  gives `lunaxx-register`, `lunaxx-find-reference` and `lunaxx-workbench` (`lunaxx/cli.py`).
- **As a service.** `python -m web.cloud_bundle <dir>` assembles the container that runs the hosted
  workbench (Dockerfile included). The same container runs on any server, e.g. one of SAC's own.
- **Kept honest by tests.** `python -m pytest` runs the whole suite. GitHub Actions runs it on a clean
  checkout on every push (`.github/workflows/tests.yml`).
- **Every number reproducible.** The evidence is frozen at one commit (`python -m ops.freeze`) and
  `REPORT.md` is regenerated from the logs by one command (`python -m ops.make_report`). Nothing in it
  is typed by hand.
- **Where to start reading.** `README.md`, then `core/pipeline.py` (`run_all`), then
  `core/reliability.py`, the independent area check that is this project's contribution.
