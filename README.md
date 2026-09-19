# SIH26166 — lunar image registration that knows when it is wrong

Team **LunaXX** · Smart India Hackathon 2026 · ISRO problem statement SIH26166, *"Multi-modal, Sun
angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and
IIRS)"*.

The engine registers a Chandrayaan-2 image to a lunar reference image across Sun angle, scale and
sensor. It also reports, region by region, whether the result can be trusted:

- every cell of an 8×8 grid over the reference is `verified`, `weak` or `no_evidence`;
- an independent area check, which never sees the matches, cross-correlates the warped image
  against the reference (inverted shading included) and says `agrees`, `unconfirmed` or
  `contradicted`;
- `contradicted` switches to global correlation, and the output says it did.

**Measured results are in [`REPORT.md`](REPORT.md).** That file is generated from the evidence
logs by `python -m ops.make_report` and is never edited by hand. This README carries no numbers
on purpose: Invariant 1 (below) allows a figure only where it can be traced to a log row.

## What runs, in order

`core/pipeline.py` `run_all()`:

1. `io_loader`: PDS4 (Chandrayaan-2), PDS3 (LRO, Kaguya) and GeoTIFF, windowed reads.
2. `scale`: both images to one ground scale (area averaging).
3. `illumination`: lighting reduced to gradient orientation.
4. `matcher`: LoFTR on CPU, tiled.
5. `subpixel`: NCC refinement of every match, in original pixels.
6. `ransac`: MAGSAC++ (`cv2.USAC_MAGSAC`).
7. `evaluation/metrics.evaluate`: the five metrics, plus held-out residuals on the 20 % of
   matches the fit never saw.
8. `reliability`: the trust map and the area check, then the fallback when contradicted.
9. `export`: the deliverables, listed below.

The deliverables for every pair are written to `--out DIR`:
- `registered_product.tif`, a GeoTIFF on the reference grid;
- `matches.csv`, every raw match with an inlier flag, its residual and its cell state;
- GDAL/QGIS ground control points;
- `matches_isis.csv`, an ISIS-style match list;
- `trust_map.csv`;
- `report.json` and `report.md`, with metrics, timings, input sha256 and versions.

## Real data it has been run on

Terminology follows `docs/00_CANONICAL_FACTS.md` §2 (Invariant 2).

| Pair | Kind |
|---|---|
| Chandrayaan-2 OHRC ↔ LRO NAC, 74 °S site and SAC's two benchmark pairs (arXiv:2509.04775, Table 1) | cross-sensor, cross-mission |
| OHRC ↔ Kaguya TC ortho map | cross-sensor, cross-mission (scale rung) |
| OHRC ↔ TMC-2 | cross-sensor, same mission |
| LRO NAC ↔ LRO NAC (MiLOI benchmark, real Sun sweep) and TMC-2 fore ↔ aft | **same sensor**: Sun-angle and viewpoint tests |
| Kaguya TC ↔ Kaguya MI 1548 nm, TC ↔ Chandrayaan-2 IIRS | multi-modal (visible ↔ infrared) |
| OHRC ↔ LOLA shaded relief | multi-modal (optical ↔ elevation), a **declared failure** |

## Setup

The demo machine has **no GPU**. Everything runs on CPU.

```
python -m venv C:\Users\<you>\venvs\sih26166     # OUTSIDE the OneDrive folder
C:\Users\<you>\venvs\sih26166\Scripts\activate
pip install -r requirements.txt
python -m core.fetch_weights                      # LoFTR weights into weights/, once, online
```

- `python3` fails on Windows (Store alias); use `python` or `py`.
- Activate the venv in every new terminal. A bare `python` here has no numpy, and the failure
  looks like a broken build.
- External data (imagery, PDS products) lives outside git. Its path goes in `data_path.txt`, which
  is gitignored and differs per machine.

## Run it

```
python -m core.pipeline data/pairs/sac_ohrc_nac_w01 --out out/sac_w01   # one pair, all deliverables
streamlit run app/streamlit_app.py                                     # the demo app (offline)
python -m ops.run_real_pairs "site_ohrc_*" --log                        # register + log real pairs
python -m ops.freeze --plan                                             # the evidence freeze: what would run
python -m ops.freeze                                                    # re-run ALL evidence on this commit
python -m ops.freeze --check                                            # FROZEN = every number is from this commit
python -m ops.make_report                                               # REPORT.md from the logs
python -m pytest -q                                                     # the test suite
```

The app reads cached results from `demo_cache/`, which `python -m ops.precompute_demo_cache`
fills. The live demo therefore needs no network and no GPU.

## Evidence, and the two rules that override convenience

| File | Holds |
|---|---|
| `evaluation/results_log.csv` | every scored run: the 15-column log (Invariant 1) |
| `evaluation/real_pairs_log.csv` | real-pair structure: Sun geometry, window, archive offset, held-out and in-sample residuals, loops, sweep outcomes |
| `evaluation/miloi_log.csv`, `miloi_truth.json` | the MiLOI benchmark and its truth network |
| `evaluation/trust_real_calibration.csv` | planted wrong registrations on real windows |
| `REPORT.md` | all of the above, rendered |

**Numbers.** No figure enters a slide, a script, a Q&A answer or this README unless it is in the
logs above at the freeze commit. REPORT.md is where to copy it from.

**Terminology.** LROC NAC ↔ LROC NAC is the *same sensor*: a Sun-angle test, not cross-sensor.
"Multi-modal" means visible↔infrared, radar or elevation only; two panchromatic cameras are not.
"Sub-pixel" always names its pixel grid and gives the metres.

## Layout

| Folder | Contents |
|---|---|
| `core/` | the pipeline modules above, `geometry` (map projections, NAC corrections), `reliability` (trust layer), `export` |
| `evaluation/` | `metrics`, synthetic and shaded-relief pairs, `real_eval`, `miloi`, the evidence logs |
| `baselines/` | SIFT / ORB / AKAZE and their sweeps |
| `app/` | `streamlit_app.py` (the demo), `change_detection.py` (gated by the trust map) |
| `ops/` | data cutting (`cut_site_pairs`, `cut_pradan_pairs`), runners, `freeze`, `make_report`, `STATUS.md` |
| `presentation/` | `build_deck.py` (the deck text lives there), `make_figures.py`, the audit table |
| `docs/` | `00_CANONICAL_FACTS.md`, the single source of truth for definitions |

Imagery and model weights are never committed (anything over ~5 MB or binary).
`weights/`, `demo_cache/` and `data/pairs/*` are gitignored. Each pair directory carries its own
`geometry_prior.json` (the product ids, grids, Sun geometry and the command that cut it), and
REPORT.md lists every downloaded product with its sha256, so the pairs can be cut again.
