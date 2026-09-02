"""Guards the three Gate-2 wirings added to `core/pipeline.py` on Day 5.

None of these need LoFTR, so they run in milliseconds. What they pin:

  - the DIRECTION of `H_true`. `evaluate()` fits source -> reference and differences
    our H against `H_true` over one lattice, so `H_true` must be source -> reference
    too. Get it backwards and `rmse_gt_px` is still a plausible small-ish number -
    it just measures the wrong thing. That is the failure this file exists for.
  - the [0,1] -> DN conversion in `_synthetic_pair`. `render_shaded_relief` returns
    [0,1] and `matcher.match` divides by 255 with no range check.
  - `_log_preflight` refusing a results_log.csv that does not end in a newline,
    because the row it would write is invisible to `csv.DictReader`.
  - that `--log` cannot be reached from `run_all`, only from `main()`. If it ever
    moves, every pytest run starts appending junk rows to the real results log.
"""
import csv
import inspect
import pathlib

import numpy as np
import pytest

from core import pipeline


def _dem(n=96):
    """A small, deterministic, non-degenerate elevation surface."""
    y, x = np.mgrid[0:n, 0:n].astype(np.float64)
    return (200.0 * np.sin(x / 11.0) * np.cos(y / 9.0)
            + 60.0 * np.sin((x + y) / 5.0)).astype(np.float32)


# --- H_true's direction, which is the whole ballgame -------------------------

def test_h_true_is_source_to_reference_not_the_inverse():
    """The convention `_synthetic_pair` depends on, pinned against Samrudh's code.

    A backwards H_true does not raise and does not return None - it returns a
    number. So the only way to hold the convention is to assert that the RIGHT
    one scores near zero and the WRONG one does not.
    """
    evaluate = pytest.importorskip("evaluation.metrics").evaluate
    rng = np.random.default_rng(0)
    src = (rng.random((200, 2)) * 400 + 50).astype(np.float32)
    shift = np.array([7.0, -4.0], np.float32)
    ref = (src + shift).astype(np.float32)

    H_true = np.array([[1, 0, shift[0]], [0, 1, shift[1]], [0, 0, 1]], float)

    right = evaluate((512, 512), src, ref, H_true=H_true)["rmse_gt_px"]
    wrong = evaluate((512, 512), src, ref, H_true=np.linalg.inv(H_true))["rmse_gt_px"]

    assert right < 0.01, f"src->ref H_true should score ~0, got {right}"
    assert wrong > 2 * float(np.hypot(*shift)) - 1e-6, (
        f"inv(H_true) scored {wrong}, which is not distinguishable from correct. "
        "If this ever passes, rmse_gt_px has stopped depending on H_true's direction."
    )


def test_synthetic_pair_h_true_carries_the_shift_we_asked_for(tmp_path):
    pytest.importorskip("evaluation.synthetic_data")
    pytest.importorskip("tifffile")
    dem_path = tmp_path / "dem.npy"
    np.save(dem_path, _dem())

    _, _, H_true, meta = pipeline._synthetic_pair(
        dem_path, pixel_size_m=60.0, sun_delta_deg=15.0,
        shift_px=(12.0, -8.0), seed=0, out_dir=tmp_path / "out")

    assert H_true.shape == (3, 3)
    assert H_true[0, 2] == pytest.approx(12.0), "x shift lost"
    assert H_true[1, 2] == pytest.approx(-8.0), "y shift lost"
    # Rotation and scale are pinned; see _synthetic_pair note 2 for why.
    assert H_true[0, 0] == pytest.approx(1.0)
    assert H_true[1, 1] == pytest.approx(1.0)
    assert meta["sun_delta_deg"] == 15.0


def test_synthetic_files_are_dn_shaped_not_unit_range(tmp_path):
    """`matcher.match` divides by 255. A [0,1] image reaches LoFTR as [0, 0.004]."""
    pytest.importorskip("evaluation.synthetic_data")
    tifffile = pytest.importorskip("tifffile")
    dem_path = tmp_path / "dem.npy"
    np.save(dem_path, _dem())

    src_path, ref_path, _, _ = pipeline._synthetic_pair(
        dem_path, pixel_size_m=60.0, sun_delta_deg=0.0, out_dir=tmp_path / "out")

    for p in (src_path, ref_path):
        arr = tifffile.imread(str(p))
        assert arr.max() > 1.0, (
            f"{p.name} has max {arr.max()} - that is unit range, not DN. "
            "matcher.match will divide it by 255 and LoFTR will see nothing."
        )


def test_synthetic_config_states_the_sun_difference(tmp_path):
    """A synthetic row whose illumination difference is unstated is not evidence."""
    pytest.importorskip("evaluation.synthetic_data")
    pytest.importorskip("tifffile")
    dem_path = tmp_path / "dem.npy"
    np.save(dem_path, _dem())
    _, _, _, meta = pipeline._synthetic_pair(
        dem_path, pixel_size_m=60.0, sun_delta_deg=30.0, out_dir=tmp_path / "out")
    assert "d_azimuth=30" in meta["config"]
    assert "elevation" in meta["config"]


# --- the results log ---------------------------------------------------------

def _fake_log(tmp_path, monkeypatch, text):
    """Point evaluation.logger at a throwaway CSV, never the project's own."""
    logger = pytest.importorskip("evaluation.logger")
    p = tmp_path / "results_log.csv"
    p.write_bytes(text)
    monkeypatch.setattr(logger, "RESULTS_LOG", p)
    return p


HEADER = (b"timestamp,pair_id,tier,method,config,rmse_gt_px,residual_px,inlier_count,"
          b"inlier_ratio,grid_coverage_fraction,distribution_cv,n_matches,gsd_mpp,"
          b"status,notes")

METRICS = {"rmse_gt_px": 0.21, "residual_px": 1.07, "inlier_count": 1299,
           "inlier_ratio": 0.98, "grid_coverage_fraction": 1.0,
           "distribution_cv": 0.40, "n_matches": 1319, "status": "ok"}


def test_preflight_refuses_a_log_with_no_trailing_newline(tmp_path, monkeypatch):
    _fake_log(tmp_path, monkeypatch, HEADER)          # no terminator, as shipped
    err = pipeline._log_preflight()
    assert err and "does not end in a newline" in err
    assert "results_log.csv" in err


def test_preflight_accepts_a_terminated_log(tmp_path, monkeypatch):
    _fake_log(tmp_path, monkeypatch, HEADER + b"\n")
    assert pipeline._log_preflight() is None


def test_log_row_writes_nothing_when_preflight_refuses(tmp_path, monkeypatch):
    p = _fake_log(tmp_path, monkeypatch, HEADER)
    before = p.read_bytes()
    ok, note = pipeline._log_row("pair_x", "synthetic", "ours", METRICS)
    assert ok is False
    assert p.read_bytes() == before, "refused to log but wrote anyway"
    assert "REFUSING" in note


def test_log_row_writes_a_row_that_dictreader_can_actually_read(tmp_path, monkeypatch):
    p = _fake_log(tmp_path, monkeypatch, HEADER + b"\n")
    ok, note = pipeline._log_row("synthetic_d015_s0", "synthetic", "ours_loftr",
                                 METRICS, config="d_azimuth=15deg", gsd_mpp=60.0)
    assert ok is True, note
    rows = list(csv.DictReader(p.open(newline="", encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["rmse_gt_px"] == "0.21"
    assert rows[0]["tier"] == "synthetic"
    assert rows[0]["gsd_mpp"] == "60.0"


def test_logging_is_not_reachable_from_run_all(tmp_path, monkeypatch):
    """`evaluation/logger.py` resolves RESULTS_LOG from its own __file__.

    So a log_result() call inside run_all() would append a row to the REAL
    evaluation/results_log.csv on every pytest run - tmp_path cannot save us.
    Logging is a CLI action and must stay in main().
    """
    src = inspect.getsource(pipeline.run_all)
    assert "_log_row" not in src and "log_result" not in src, (
        "run_all() now writes to results_log.csv. Move it back into main(): the "
        "contract tests call run_all() directly and would pollute the real log."
    )


# --- the distribution diagnostic ---------------------------------------------

def test_run_all_reports_where_the_matches_landed():
    src = inspect.getsource(pipeline.run_all)
    for key in ('"distribution"', '"distribution_note"'):
        assert key in src, f"run_all() no longer returns {key}"


def test_distribution_is_a_diagnostic_and_says_so():
    """It must never hand back the two numbers Gate 2 is judged on."""
    pytest.importorskip("evaluation.metrics")
    rng = np.random.default_rng(1)
    pts = (rng.random((300, 2)) * 500).astype(np.float32)
    info, note = pipeline._distribution(pts, (500, 500))
    assert info is not None
    assert "diagnostic" in note
    assert "grid_coverage_fraction" not in info
    assert "distribution_cv" not in info


def test_distribution_handles_zero_inliers():
    info, note = pipeline._distribution(np.zeros((0, 2), np.float32), (500, 500))
    assert info is None and "no inliers" in note


# --- the CLI ------------------------------------------------------------------

def test_gate_1_command_still_parses_as_a_bare_positional():
    args = pipeline._build_parser().parse_args(["data/pairs/pair_01"])
    assert args.pair == "data/pairs/pair_01"
    assert args.synthetic is False and args.log is False


def test_log_on_a_real_pair_requires_a_tier(capsys):
    """`log_result` rejects a falsy tier, and a number without its tier is not
    evidence (Invariant 2). Fail before doing 15 s of matching, not after."""
    rc = pipeline.main(["prog", "data/pairs/pair_01", "--log"])
    assert rc == 2
    assert "--tier" in capsys.readouterr().out


def test_synthetic_requires_a_dem_and_a_pixel_size(capsys):
    assert pipeline.main(["prog", "--synthetic"]) == 2
    assert "--dem" in capsys.readouterr().out


def test_no_arguments_prints_help_and_exits_2(capsys):
    assert pipeline.main(["prog"]) == 2
    assert "core.pipeline" in capsys.readouterr().out


# --- what the adversarial review of 2 Sep 2026 found -------------------------
#
# Each test below corresponds to a defect that a skeptic reproduced. They are
# grouped so that if one regresses it is obvious which finding came back.

def test_the_default_shift_is_not_a_whole_number():
    """An integer shift is the one case cv2.warpPerspective does not interpolate.

    The warped image is then a literal pixel copy and the true answer sits exactly
    on the matcher's integer query grid, so rmse_gt_px stops being a sub-pixel
    measurement at all. Measured at a 30 deg sun difference: shift (12,-8) gave
    0.412 and passed Gate 2, while (11,-9) - also integer, one pixel away - gave
    1.045 and failed. The default must be off-grid.
    """
    for v in pipeline.SYNTH_SHIFT_PX:
        assert abs(v - round(v)) > 0.1, (
            f"SYNTH_SHIFT_PX component {v} is too close to a whole pixel; "
            "rmse_gt_px measured against it is not evidence of sub-pixel accuracy."
        )


def test_draw_shift_is_off_grid_and_varies_with_seed():
    """`make_pair`'s own seed does nothing once a shift is passed, so repeats have
    to draw their own - otherwise three seeds give three identical image pairs
    logged under three pair_ids, which looks like an error bar and is not."""
    assert pipeline._draw_shift(0) == tuple(float(v) for v in pipeline.SYNTH_SHIFT_PX)
    a, b = pipeline._draw_shift(1), pipeline._draw_shift(2)
    assert a != b, "different seeds must give different offsets"
    assert pipeline._draw_shift(1) == a, "the same seed must be reproducible"
    for v in (*a, *b):
        assert abs(v - round(v)) > 0.05, f"{v} landed on the integer grid"


def test_a_failed_registration_is_not_logged(tmp_path, monkeypatch, capsys):
    """`evaluate()` returns a full-shaped dict on failure, and `log_result`'s only
    guard is a falsy tier - so without this check a failed run enters the evidence
    file as a normal row with a blank rmse_gt_px."""
    p = _fake_log(tmp_path, monkeypatch, HEADER + b"\n")
    failed = dict(METRICS, status="ransac_failed", rmse_gt_px=None, residual_px=None)

    class Args:
        log, subpixel, method, notes = True, False, "ours", ""

    monkeypatch.setattr(pipeline, "run_all",
                        lambda *a, **k: {"metrics": failed, "metrics_note": "ok",
                                         "H": None, "gsd_mpp": None,
                                         "distribution": None, "distribution_note": "",
                                         "source": "s", "reference": "r",
                                         "shape_source": (4, 4), "shape_reference": (4, 4),
                                         "scale_note": "", "illumination": "",
                                         "n_matches": 3, "seconds": 0.0,
                                         "ransac": {"note": "", "inlier_count": 0,
                                                    "inlier_ratio": 0.0},
                                         "meta_source": {}, "meta_reference": {}})
    ok, logged, _ = pipeline._run_one("s", "r", None, Args(), "pair_x", "A", None, None)
    assert logged is False
    assert "NOT LOGGED" in capsys.readouterr().out
    assert list(csv.DictReader(p.open(newline="", encoding="utf-8"))) == []


def test_preflight_runs_before_any_matching(tmp_path, monkeypatch, capsys):
    """A four-delta sweep is minutes of LoFTR. Discovering afterwards that the row
    cannot be written wastes all of it, and the refusal used to print once per
    delta AFTER each run. Proof of ordering: a DEM path that does not exist would
    raise on np.load, so returning 3 means we never got that far."""
    _fake_log(tmp_path, monkeypatch, HEADER)          # no trailing newline -> refuse
    rc = pipeline.main(["prog", "--synthetic", "--dem", str(tmp_path / "nope.npy"),
                        "--pixel-size", "60", "--sweep", "0,15,30,45", "--log"])
    assert rc == 3
    assert "REFUSING TO LOG" in capsys.readouterr().out


@pytest.mark.parametrize("argv,why", [
    (["--synthetic", "--dem", "d.npy", "--pixel-size", "60", "--sweep", "0,15,x"],
     "a bad --sweep used to raise a raw ValueError traceback"),
    (["--synthetic", "--dem", "d.npy", "--pixel-size", "60", "--sweep", ""],
     "an empty --sweep used to fall through to the flattering 0-degree case"),
    (["--synthetic", "--dem", "d.npy", "--pixel-size", "0"],
     "--pixel-size 0 reaches np.gradient(dem, 0.0) and renders all-NaN in silence"),
    (["--synthetic", "--dem", "d.npy", "--pixel-size", "60", "--repeats", "0"],
     "--repeats 0 would run nothing and report success"),
])
def test_bad_synthetic_arguments_exit_2_with_a_message(argv, why, capsys):
    assert pipeline.main(["prog", *argv]) == 2, why
    assert capsys.readouterr().out.strip(), "exited 2 without telling the user why"


def test_sweep_summary_applies_the_gate_threshold_in_code(capsys):
    """Nothing else in this repo checks a gate criterion - all seven are judged by
    a human reading a printed number against a markdown table. That is how 0.796875
    gets read as 'about 0.8'. The median decides, not the best run."""
    rows = [(30.0, (12.0, -8.0), {"rmse_gt_px": 0.41}),
            (30.0, (12.5, -8.5), {"rmse_gt_px": 0.81}),
            (30.0, (11.3, -9.7), {"rmse_gt_px": 1.04})]
    pipeline._print_sweep_summary(rows)
    out = capsys.readouterr().out
    assert "PASS" in out and "FAIL" in out
    assert "FAIL on the median" in out, (
        "the median of 0.41/0.81/1.04 is 0.81, which fails Gate 2's 0.5 threshold; "
        "reporting the minimum instead would be picking the luckiest draw"
    )


def test_synthetic_stem_names_every_input_that_moves_a_pixel(tmp_path):
    """Two configurations must not overwrite each other's cached .tif and log two
    rows that cannot be told apart afterwards."""
    pytest.importorskip("evaluation.synthetic_data")
    pytest.importorskip("tifffile")
    dem_path = tmp_path / "dem.npy"
    np.save(dem_path, _dem())
    ids = set()
    for shift in ((12.37, -8.63), (5.11, 3.29)):
        _, _, _, meta = pipeline._synthetic_pair(
            dem_path, pixel_size_m=60.0, sun_delta_deg=30.0,
            shift_px=shift, out_dir=tmp_path / "out")
        ids.add(meta["pair_id"])
        assert f"{shift[0]:+.4f}" in meta["config"], "config must carry the true offset"
    assert len(ids) == 2, f"two different shifts collided on one pair_id: {ids}"


def test_synth_dir_is_repo_rooted_not_cwd_relative():
    """Every other output path in this project is __file__-rooted. A cwd-relative
    one writes a stray demo_cache tree wherever the operator happened to be."""
    assert pipeline.SYNTH_DIR.is_absolute()
    assert pipeline.SYNTH_DIR.parent.name == "demo_cache"
