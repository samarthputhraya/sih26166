"""Guards the classical-baseline harness.

Everything here is a defect that was live on Day 5 2026 and cost the project real
time. Each test names the one it prevents coming back.

None of these need the lunar data or LoFTR, so they run in milliseconds.
"""
import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from baselines import run_all_baselines as H          # noqa: E402
from baselines.settings import RATIO_TEST            # noqa: E402

SOURCE = (ROOT / "baselines" / "run_all_baselines.py").read_text(encoding="utf-8")


def _code_only(text: str) -> str:
    """`text` with comments and string literals removed.

    The module docstring deliberately NAMES the defects it fixed - "it pointed at
    pair_test_source.tif", "it used cv2.imread". Grepping raw source would then
    flag the explanation as the bug. Strip comments and strings so these checks
    see executable code and nothing else.
    """
    import io
    import tokenize

    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            out.append(tok.string)
    except tokenize.TokenError:            # pragma: no cover - malformed source
        return text
    return " ".join(out)


CODE = _code_only(SOURCE)


# --- finding the data ---------------------------------------------------------

def _make_pair(root: pathlib.Path, pair_dir: str, stem: str) -> None:
    d = root / pair_dir
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{stem}_source.tif").write_bytes(b"x")
    (d / f"{stem}_ref.tif").write_bytes(b"x")


def test_pairs_one_directory_down_are_found(tmp_path):
    """THE defect: the old glob was flat (`data/pairs/*_source.tif`) while every
    real pair lives one level down, so it found ZERO pairs and the classical
    baselines had never run on real lunar data at all."""
    _make_pair(tmp_path, "pair_01", "pair_01")
    _make_pair(tmp_path, "pair_03_tierD", "tier_d_01")

    found = H.discover_pairs(tmp_path)
    assert len(found) == 2, f"nested pairs not found: {found}"
    assert {p[0] for p in found} == {"pair_01", "tier_d_01"}


def test_a_source_without_its_reference_is_skipped(tmp_path):
    d = tmp_path / "lonely"
    d.mkdir()
    (d / "lonely_source.tif").write_bytes(b"x")
    assert H.discover_pairs(tmp_path) == []


def test_missing_pairs_directory_returns_empty_not_an_exception(tmp_path):
    assert H.discover_pairs(tmp_path / "nope") == []


def test_each_pair_is_returned_once(tmp_path):
    _make_pair(tmp_path, "pair_01", "pair_01")
    ids = [p[0] for p in H.discover_pairs(tmp_path)]
    assert len(ids) == len(set(ids))


def test_pair_id_prefers_whatever_the_catalogue_knows(tmp_path, monkeypatch):
    """`pair_03_tierD/` contains `tier_d_01_source.tif` and the catalogue calls it
    `tier_d_01`. Picking the directory name would read UNCATALOGUED and refuse to
    log a real result."""
    monkeypatch.setattr(H, "catalogue_tier", lambda pid: "D" if pid == "tier_d_01" else None)
    _make_pair(tmp_path, "pair_03_tierD", "tier_d_01")
    assert H.discover_pairs(tmp_path)[0][0] == "tier_d_01"


def test_pair_id_falls_back_to_the_directory_when_nothing_is_catalogued(tmp_path, monkeypatch):
    monkeypatch.setattr(H, "catalogue_tier", lambda pid: None)
    _make_pair(tmp_path, "brand_new_pair", "brand_new_pair")
    assert H.discover_pairs(tmp_path)[0][0] == "brand_new_pair"


# --- the tier is never invented ------------------------------------------------

def test_catalogue_tier_returns_none_rather_than_guessing(monkeypatch, tmp_path):
    """`log_result` refuses a falsy tier on purpose. Inventing one - guessing "A"
    for a pair that is two crops of one frame - is the Invariant 2 breach most
    likely to lose a Q&A round."""
    monkeypatch.setattr(H, "CATALOGUE", tmp_path / "absent.csv")
    assert H.catalogue_tier("anything") is None


def test_real_catalogue_gives_pair_01_its_honest_tier():
    if not H.CATALOGUE.is_file():
        pytest.skip("pairs_catalogue.csv not present")
    tier = H.catalogue_tier("pair_01")
    if tier is None:
        pytest.skip("pair_01 not catalogued on this machine")
    assert tier != "A", (
        "pair_01 is two crops of ONE OHRC frame - same sensor, zero sun "
        "difference. Logging it as Tier A is a false claim."
    )


# --- pixels --------------------------------------------------------------------

def test_to_uint8_handles_the_dn_ranges_real_products_actually_have():
    """io_loader returns raw DN by design: [7,255] on pair_01, [0,2040] on the
    Tier D source. Casting a [0,2040] array straight to uint8 wraps it to noise,
    and handing float32 to cv2.SIFT raises."""
    for arr in (np.linspace(7, 255, 64).reshape(8, 8),
                np.linspace(0, 2040, 64).reshape(8, 8),
                np.full((8, 8), 5.0)):
        out = H.to_uint8(arr)
        assert out.dtype == np.uint8 and out.shape == (8, 8)
        assert out.min() >= 0 and out.max() <= 255


def test_to_uint8_replaces_nan_before_casting():
    """NaN cast to uint8 is undefined behaviour and yields arbitrary bytes."""
    a = np.full((4, 4), np.nan)
    a[0, 0], a[1, 1] = 10.0, 20.0
    out = H.to_uint8(a)
    assert out.dtype == np.uint8
    assert out[3, 3] == 0, "NaN must become black, not an arbitrary byte"


def test_to_uint8_refuses_colour_input():
    with pytest.raises(ValueError):
        H.to_uint8(np.zeros((4, 4, 3)))


# --- the comparison is fair ----------------------------------------------------

def test_all_three_detectors_share_one_ratio_test():
    """SIFT used 0.70 while ORB and AKAZE used 0.75, so the three were tuned
    differently and any "N times better than classical" claim built on them was
    contestable."""
    import inspect
    from baselines.akaze_baseline import run_akaze
    from baselines.orb_baseline import run_orb
    from baselines.sift_baseline import run_sift

    defaults = {f.__name__: inspect.signature(f).parameters["ratio"].default
                for f in (run_sift, run_orb, run_akaze)}
    assert set(defaults.values()) == {RATIO_TEST}, (
        f"detectors disagree on the ratio test: {defaults}. Import RATIO_TEST "
        "from baselines/settings.py instead of retyping a literal."
    )


# --- the harness invents no metrics --------------------------------------------

def test_the_harness_computes_no_metric_of_its_own():
    """It used to invent mean_confidence / dx_px / offset_spread_px, which no
    other part of the project could compare against - and dx/dy was a plain mean
    over UNFILTERED matches, so a few outliers moved it arbitrarily."""
    for banned in ("calculate_offset", "calculate_spread",
                   "mean_confidence", "offset_spread_px", "findHomography"):
        assert banned not in CODE, (
            f"{banned!r} is back. Score with evaluation.metrics.evaluate() so the "
            "baselines and our own method are measured the same way."
        )


def test_scoring_goes_through_samrudhs_evaluate():
    assert "from evaluation.metrics import evaluate" in SOURCE


def test_logging_goes_through_log_result_not_a_private_writer():
    """Invariant 1: a figure not in results_log.csv cannot be presented. The old
    harness wrote only baselines/results.csv with its own 10 invented columns."""
    assert "from evaluation.logger import log_result" in SOURCE


def test_images_are_loaded_through_io_loader_not_cv2_imread():
    """cv2.imread returns None for the Tier D GeoTIFF and cannot read PDS4."""
    assert "from core.io_loader import load" in SOURCE
    assert "cv2.imread" not in CODE


def test_no_hardcoded_pair_paths():
    """It pointed at data/pairs/pair_test_source.tif, which has never existed on
    any machine - so the script raised FileNotFoundError for everyone."""
    for ghost in ("pair_test_source", "pair_test_ref", "ohrc_real_source"):
        assert ghost not in CODE, f"hardcoded path {ghost!r} is back"
