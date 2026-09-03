"""Guards `app/streamlit_app.py`, which is Gate 3 and Gate 4.

A Streamlit app that imports cleanly and then throws on first render is the
classic way a demo dies live, and `import` alone will never catch it - the module
body only executes when Streamlit runs it. So these use `AppTest`, which actually
executes the script the way the server does.

Nothing here runs the real pipeline. Clicking Align would cost ~15 s and needs the
LoFTR weights and the image data, neither of which is in git. The full flow is
verified by hand before each gate - see the manual procedure in
`.claude/agents/demo-medic.md`. What is pinned here is everything that can break
WITHOUT anyone noticing: first render, the honesty rules, and the no-network rule.
"""
import pathlib
import re

import numpy as np
import pytest

APP = pathlib.Path(__file__).resolve().parent / "streamlit_app.py"
SOURCE = APP.read_text(encoding="utf-8")


# --- it renders at all --------------------------------------------------------

def _fresh_app():
    AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
    at = AppTest.from_file(str(APP), default_timeout=120)
    at.run()
    return at


def test_first_render_raises_nothing():
    """The failure this file exists for: imports fine, throws on render."""
    at = _fresh_app()
    assert not at.exception, (
        "streamlit_app.py raised on first render: "
        + " | ".join(str(e.value) for e in at.exception)
    )


def test_the_align_button_exists_and_is_the_only_entry_point():
    at = _fresh_app()
    assert "Align" in [b.label for b in at.button]


def test_every_real_pair_is_offered():
    """If data/pairs is synced, the app must find the pairs the gates use."""
    at = _fresh_app()
    if not at.selectbox:
        pytest.skip("data/pairs is not synced on this machine (files are gitignored)")
    offered = at.selectbox[0].options
    assert offered, "data/pairs has directories but none were offered"
    for expected in ("pair_01",):
        assert expected in offered, f"{expected} missing from {offered}"


# --- the honesty rules, enforced as tests -------------------------------------

def test_the_ui_computes_no_metric_of_its_own():
    """Design decision 1, and Invariant 1.

    A UI that recomputes a metric "just for display" gives the project a second
    source of truth for its headline number. Every figure must come from
    run_all() -> evaluation/metrics.py.
    """
    banned = ["findHomography", "USAC_MAGSAC", "perspectiveTransform",
              "def evaluate", "rmse_gt_px =", "residual_px ="]
    found = [b for b in banned if b in SOURCE]
    assert not found, (
        f"streamlit_app.py appears to compute metrics itself: {found}. "
        "Display values from run_all()'s result dict instead."
    )


def test_rmse_gt_px_is_never_presented_as_a_real_pair_number():
    """rmse_gt_px is accuracy against a KNOWN transform - synthetic pairs only.

    On a real pair it must read n/a, never a number. Confusing it with
    residual_px is a fabrication rather than a bug.
    """
    assert "no ground truth on a real pair" in SOURCE


def test_the_tier_is_read_from_the_catalogue_not_hardcoded():
    """Invariant 2. pair_01 is two crops of ONE frame - the UI must not imply
    otherwise, and the way to guarantee that is to read Rohan's row."""
    assert "pairs_catalogue.csv" in SOURCE
    assert "cross-sensor" in SOURCE, (
        "the UI should say plainly when a pair is same-instrument; that warning "
        "is what stops a demo implying a cross-sensor result"
    )


def test_no_network_access_anywhere():
    """Gate 4 runs with the wifi physically off.

    One hidden fetch turns a 3-second render into a 30-second timeout in front
    of a judge.
    """
    for pattern in (r"https?://", r"\brequests\.", r"\burllib\b", r"\bsocket\b",
                    r"hf_hub_download", r"torch\.hub"):
        hits = [ln for ln in SOURCE.splitlines()
                if re.search(pattern, ln) and not ln.strip().startswith("#")]
        # localhost in a comment or docstring is fine; a real call is not.
        hits = [h for h in hits if "localhost" not in h]
        assert not hits, f"possible network access ({pattern}): {hits}"


def test_no_nested_buttons():
    """`st.button()` inside `if st.button():` can never fire - Streamlit re-runs
    the whole script on every interaction, so the outer button is False on the
    re-run that would draw the inner one. State must live in st.session_state.

    Recorded in .claude/agents/demo-medic.md as a known killer.
    """
    depth_of_button_if = None
    for line in SOURCE.splitlines():
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if depth_of_button_if is not None and indent <= depth_of_button_if:
            depth_of_button_if = None
        if depth_of_button_if is not None and "st.button(" in stripped:
            pytest.fail(f"nested st.button() inside an `if st.button()` block: {stripped}")
        if stripped.startswith("if ") and "st.button(" in stripped:
            depth_of_button_if = indent


# --- the display helpers ------------------------------------------------------

def _app_module():
    import importlib.util
    import sys
    root = APP.parent.parent
    for p in (str(root), str(root / "app")):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("_sa_helpers", APP)
    mod = importlib.util.module_from_spec(spec)
    # Executing the module body runs Streamlit calls, which is fine in bare mode.
    spec.loader.exec_module(mod)
    return mod


def test_to_display_handles_the_ranges_real_lunar_data_actually_has():
    m = _app_module()
    # Raw DN varies wildly between pairs: [7,255] on pair_01, [0,2040] on Tier D.
    for arr in (np.full((8, 8), 5.0),                       # flat
                np.linspace(0, 2040, 64).reshape(8, 8),     # wide DN
                np.linspace(7, 255, 64).reshape(8, 8)):     # narrow DN
        out = m.to_display(arr)
        assert out.dtype == np.uint8 and out.shape == (8, 8)
    assert m.to_display(None) is None
    assert m.to_display(np.zeros((2, 2, 3))) is None, "colour input should be refused"


def test_to_display_survives_nan_from_a_warp_border():
    """NaN cast to uint8 is undefined behaviour and yields arbitrary bytes.

    On screen that is a confetti of random pixels along the warp border, which a
    viewer reads as a broken alignment rather than the empty region it is.
    `warp()` leaves exactly such a border whenever the source does not cover the
    whole reference frame.
    """
    m = _app_module()
    a = np.full((4, 4), np.nan)
    a[0, 0], a[1, 1] = 10.0, 20.0
    out = m.to_display(a)
    assert out is not None and out.dtype == np.uint8
    assert out[2, 2] == 0, "NaN must render as black, not as an arbitrary byte"
    assert out[3, 3] == 0

    b = np.array([[np.inf, -np.inf], [10.0, 20.0]])
    out_b = m.to_display(b)
    assert out_b is not None and set(np.unique(out_b)) <= set(range(256))


def test_swipe_refuses_mismatched_shapes_rather_than_crashing():
    m = _app_module()
    a = np.zeros((10, 10), np.uint8)
    assert m.swipe(a, np.zeros((10, 12), np.uint8), 0.5) is None
    assert m.swipe(a, None, 0.5) is None
    out = m.swipe(a, np.full((10, 10), 200, np.uint8), 0.5)
    assert out is not None and out.shape == (10, 10)


def test_verdict_applies_gate_2_thresholds_correctly():
    m = _app_module()
    assert m.verdict("rmse_gt_px", 0.32, "<", 0.5).startswith("PASS")
    assert m.verdict("rmse_gt_px", 0.93, "<", 0.5).startswith("FAIL")
    assert m.verdict("inlier_ratio", 0.5263, ">", 0.60).startswith("FAIL")
    # The Tier D pair really does sit just under 0.80 - it must not read as PASS.
    assert m.verdict("grid_coverage_fraction", 0.796875, ">=", 0.80).startswith("FAIL")
    assert m.verdict("grid_coverage_fraction", 0.80, ">=", 0.80).startswith("PASS")
    assert m.verdict("residual_px", 1.0, None, None) == ""
    assert m.verdict("rmse_gt_px", None, "<", 0.5) == ""
