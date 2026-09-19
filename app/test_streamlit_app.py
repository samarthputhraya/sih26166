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
    # options are the DISPLAYED labels; pairs with a cached result say so (19 Sep)
    offered = [o.replace("  (cached)", "") for o in at.selectbox[0].options]
    assert offered, "data/pairs has directories but none were offered"
    for expected in ("pair_01",):
        assert expected in offered, f"{expected} missing from {offered}"
    # ...and the app opens ON the demo pair, not on the uncatalogued dry-run fixture.
    assert at.selectbox[0].value == "pair_01"


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
    """verdict() returns (ok, op, threshold); the WORD is rendered by the table."""
    m = _app_module()
    assert m.verdict("rmse_gt_px", 0.32, "<", 0.5)[0] is True
    assert m.verdict("rmse_gt_px", 0.93, "<", 0.5)[0] is False
    assert m.verdict("inlier_ratio", 0.5263, ">", 0.60)[0] is False
    # The Tier D pair really does sit just under 0.80 - it must not read as PASS.
    assert m.verdict("grid_coverage_fraction", 0.796875, ">=", 0.80)[0] is False
    assert m.verdict("grid_coverage_fraction", 0.80, ">=", 0.80)[0] is True
    assert m.verdict("residual_px", 1.0, None, None)[0] is None
    assert m.verdict("rmse_gt_px", None, "<", 0.5)[0] is None
    # ...and the rendered table carries the word, with the threshold beside it.
    html = m.metrics_table_html({"rmse_gt_px": 0.93, "residual_px": 0.0376, "inlier_count": 5183,
                                 "inlier_ratio": 0.9996, "grid_coverage_fraction": 0.796875,
                                 "distribution_cv": 0.357})
    assert "<b>FAIL</b> (&lt; 0.5)" in html
    assert "<b>FAIL</b> (&gt;= 0.80)" in html
    assert "<b>PASS</b> (&gt; 0.60)" in html
    assert 'title="0.796875"' in html, "full precision must ride along in the cell title"
    assert "0.7969" in html, "grid_coverage_fraction is drawn to 4 places, as the deck prints it"
    void = m.metrics_table_html({"rmse_gt_px": None})
    assert "no ground truth on a real pair" in void
    # A value that rounds to its own threshold is drawn to six places, so the
    # digits on screen can never contradict the word beside them.
    edge = m.metrics_table_html({"grid_coverage_fraction": 0.79996})
    assert "0.799960" in edge and "<b>FAIL</b> (&gt;= 0.80)" in edge
    # On a contradicted frame the matcher's residual is drawn void and says why,
    # so a photograph of the table alone never carries a bare 4,685 px "residual".
    contra = m.metrics_table_html({"residual_px": 4684.908484071721}, contradicted=True)
    assert "matcher transform, not used" in contra
    assert 'class="num num--void" title="4684.908484071721">4684.9085 px' in contra


# --- the skin: Gate 4 and the projector, enforced as tests ---------------------

def test_the_skin_has_no_url_and_no_streamlit_internal_class():
    """Invariant 3 as an assertion: a font CDN in the CSS would be a 30-second
    timeout with the wifi off, and it would be caught here instead of on stage.
    st-emotion-cache-* classes are regenerated on every Streamlit build."""
    m = _app_module()
    assert "http" not in m.SKIN
    assert "st-emotion-cache" not in m.SKIN
    assert "@import" not in m.SKIN and "url(" not in m.SKIN


def test_the_source_is_ascii_only():
    """Seven rows of results_log.csv already carry cp1252 mojibake. Typographic
    characters in this file are HTML entities, never literal code points."""
    bad = [(i + 1, ln) for i, ln in enumerate(SOURCE.splitlines())
           if any(ord(ch) > 127 for ch in ln)]
    assert not bad, f"non-ASCII characters at lines {[b[0] for b in bad][:10]}"


def test_config_toml_uses_only_keys_this_streamlit_knows():
    """An unknown config KEY warns; an invalid VALUE for a known key can stop the
    app from starting, which is a Gate 4 failure. Every key must exist in the
    installed build, and the three demo-critical values must be what Gate 4 needs."""
    import tomllib
    from streamlit import config
    cfg_path = APP.parent.parent / ".streamlit" / "config.toml"
    assert cfg_path.is_file(), "the skin's theme half is missing"
    cfg = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    known = set(config.get_config_options())
    flat = {}

    def walk(d, prefix=""):
        for k, v in d.items():
            if isinstance(v, dict):
                walk(v, prefix + k + ".")
            else:
                flat[prefix + k] = v
    walk(cfg)
    unknown = sorted(k for k in flat if k not in known)
    assert not unknown, f"config keys this streamlit does not know: {unknown}"
    assert flat["theme.base"] == "light", "a dark ground does not survive a lit classroom"
    assert flat["browser.gatherUsageStats"] is False, "a network call on startup, wifi off"
    assert flat["server.fileWatcherType"] == "none", "a stray Ctrl+S must not rerun the demo"
    for k in ("theme.font", "theme.headingFont", "theme.codeFont"):
        assert "http" not in flat.get(k, "")


def test_reliability_overlay_renders_three_different_kinds_of_mark():
    """State is never colour alone. Verified is a tint, weak is a tint plus a
    hatch, no-evidence is NO tint - faded toward paper. On a projector or for a
    colour-blind judge those must be distinguishable with the hue removed."""
    m = _app_module()
    base = np.full((96, 96), 128, np.uint8)
    state = np.array([[m.VERIFIED, m.WEAK], [m.NO_EVIDENCE, m.NO_EVIDENCE]], dtype=object)
    rel = {"state": state}
    ov = m.reliability_overlay(base, rel)
    assert ov is not None and ov.shape == (96, 96, 3) and ov.dtype == np.uint8
    # interior samples away from borders and glyphs (the glyph sits top-left)
    v = ov[30:44, 30:44].astype(float)
    w = ov[30:44, 78:92].astype(float)
    n = ov[78:92, 78:92].astype(float)
    # no-evidence is LIGHTER than the terrain (faded toward paper), and has no hue
    assert n.mean() > 128 + 20
    assert np.ptp(n.mean(axis=(0, 1))) < 6, "no-evidence must carry no tint"
    # verified and weak are tinted (channels differ), and in different hues
    assert np.ptp(v.mean(axis=(0, 1))) > 10
    assert np.ptp(w.mean(axis=(0, 1))) > 10
    assert v.mean(axis=(0, 1))[1] - v.mean(axis=(0, 1))[0] > 5      # green-leaning
    # weak carries the hatch: its luminance varies inside the cell, verified's does not
    assert w.mean(axis=2).std() > 4 * max(v.mean(axis=2).std(), 1e-6)
    # and every state has a distinct glyph and word, so the legend can say it
    assert len(set(m.STATE_GLYPH.values())) == 3 and all(m.STATE_GLYPH.values())
    assert len(set(m.STATE_WORD.values())) == 3


def test_reliability_overlay_survives_a_tiny_reference_frame():
    """pair_03's reference is 101 x 101, so an 8x8 cell is 12 px. Borders and
    glyphs must scale down rather than eat the cell or raise."""
    m = _app_module()
    base = np.full((101, 101), 90, np.uint8)
    state = np.full((8, 8), m.WEAK, dtype=object)
    state[0, 0] = m.VERIFIED
    ov = m.reliability_overlay(base, {"state": state})
    assert ov is not None and ov.shape == (101, 101, 3)


def test_every_verdict_on_screen_carries_a_word():
    """Stock st.success / st.warning / st.error in the main column are colour-first
    and an instant AI tell. Every verdict_strip call must name its state."""
    calls = re.findall(r'verdict_strip\(\s*"(\w+)",\s*"([A-Z][A-Z ]+)"', SOURCE)
    assert calls, "no verdict strips found"
    kinds = {k for k, _ in calls}
    assert kinds <= {"ok", "caution", "fail"}
    words = {w for _, w in calls}
    assert {"ALIGNED", "FALLBACK USED", "NO TRANSFORM", "CONTRADICTED", "ERROR"} <= words
    main_col = SOURCE.split("# --- render ---")[1]
    for stock in ("st.success(", "st.warning(", "st.info(", "st.error("):
        assert stock not in main_col, f"{stock} survives in the main column"


def test_every_readout_form_names_the_grid_and_says_whether_metres_exist():
    """The primary readout has no form that prints a bare pixel figure. Every
    branch names the reference grid; metres appear only when the reference label
    carries a scale, and the void branches say in words why the number is not
    an accuracy."""
    m = _app_module()

    def text(html):
        """What a judge actually reads: markup stripped, entities resolved."""
        import html as _html
        return _html.unescape(re.sub(r"<[^>]+>", "", html))

    ok = m.readout_for(0.0376, 9.3698731836556, "ref.tif", True, False)
    assert "0.0376" in text(ok) and "reference grid of ref.tif" in text(ok)
    assert "9.37 m/px" in text(ok)
    # sub-metre values keep four places: 0.35 m would hide that it is 0.3523 m
    assert f"{0.0376 * 9.3698731836556:.4f} m" in text(ok) and "not an accuracy" in ok
    # the metres are the bold element ONLY when the transform was actually used
    assert f"<b>{0.0376 * 9.3698731836556:.4f} m</b>" in ok
    nogsd = m.readout_for(0.0376, None, "pair_01_ref.tif", True, False)
    assert "reference grid of pair_01_ref.tif" in text(nogsd)
    assert "metres not available" in text(nogsd)
    assert not re.search(r"[0-9.]+\s*m(?!/px)", text(nogsd).split("neither label")[0]),         "no metre figure may be printed without a scale"
    fb = m.readout_for(4684.908484071721, 9.3698731836556, "tier_d_native_ref.tif", True, True)
    assert "readout--void" in fb and "MATCHER TRANSFORM NOT USED" in text(fb)
    assert f"{4684.908484071721 * 9.3698731836556:.2f} m" in text(fb) and "not an accuracy" in fb
    # ...and on a transform the system disowned, the emphasis is on the disclaimer,
    # never on a confident distance. "Your error is 44 km?" is self-inflicted.
    assert f"<b>{4684.908484071721 * 9.3698731836556:.2f} m</b>" not in fb
    assert "<b>the system did not use it</b>" in fb
    void = m.readout_for(None, 60.0, "x.tif", False, False)
    assert "nothing to measure" in text(void) and "reference grid of x.tif" in text(void)
    notr = m.readout_for(2.0, 60.0, "x.tif", False, False)
    assert "NO TRANSFORM" in text(notr) and "not an alignment" in notr
    assert "<b>describes nothing that was aligned</b>" in notr


def test_switching_the_source_radio_drops_the_previous_result():
    """A stale result under a rail that says 'unknown (upload)' is the wrong-number
    demo design decision 2 exists to prevent. Every pair-changing input resets."""
    at = _fresh_app()
    at.session_state["result"] = {"metrics": None}
    at.session_state["pair_label"] = "pair_01"
    at.session_state["pair_mode"] = "Bundled pair"
    at.radio[0].set_value("Upload two images").run()
    assert not at.exception
    assert "result" not in at.session_state, "the radio must reset the result"


def test_the_rail_describes_the_result_pair_not_the_sidebar():
    """pair_identity() is what the rail prints; it is looked up for the pair the
    result came from and never guessed."""
    m = _app_module()
    assert m.pair_identity(None, "Bundled pair") == ("--", "--")
    assert m.pair_identity("a.tif vs b.tif", "Upload two images") == ("unknown (upload)", "unknown")
    assert m.pair_identity("no_such_pair", "Bundled pair") == ("unknown", "unknown")


# --- demo fragility: three defects the streamlit-correctness review found ------

def test_a_result_whose_images_cannot_be_reread_does_not_crash():
    """Gate 4 is 'no crashes'. The cached pickles store the absolute paths of the
    machine that wrote them; on a backup laptop or a moved data folder the images
    cannot be re-opened for display. st.image(None) raises AttributeError, so the
    plates must render as explicit voids and the numbers must still be shown."""
    at = _fresh_app()
    at.session_state["result"] = {
        "source": r"Z:\nowhere\src.tif", "reference": r"Z:\nowhere\ref.tif",
        "shape_source": (8, 8), "shape_reference": (8, 8), "gsd_mpp": None,
        "illumination": "gradient_orientation", "n_matches": 0,
        "ransac": {"note": "MAGSAC++ at 3.0 px"}, "H": None, "warped": None,
        "metrics": None, "distribution": None, "reliability": None,
        "reliability_note": "no transform", "fallback": None,
        "declared": {"method": "none", "why": "no transform", "contradicted": False},
        "H_final": None, "warped_final": None, "seconds": 0.0,
        "meta_source": {}, "meta_reference": {},
    }
    at.session_state["pair_label"] = "ghost"
    at.session_state["pair_mode"] = "Bundled pair"
    at.run()
    assert not at.exception, "render raised: " + " | ".join(str(e.value) for e in at.exception)


def test_the_two_config_files_are_identical():
    """Streamlit reads .streamlit/config.toml from the working directory AND from
    beside the main script; the script-level copy wins and works from any cwd.
    Launched from app/ with only the root copy, the theme reverted to default,
    file watching came back and a usage-stats call went out with wifi off
    (measured on 1.62.0). Two copies are the fix; this is what stops them drifting."""
    root = APP.parent.parent / ".streamlit" / "config.toml"
    beside = APP.parent / ".streamlit" / "config.toml"
    assert beside.is_file(), "app/.streamlit/config.toml is missing"
    assert root.read_bytes() == beside.read_bytes(), "the two config copies have drifted"


def test_two_uploads_with_the_same_filename_do_not_overwrite_each_other():
    """Two uploads both named source.tif would land on one path; the pipeline
    would then align an image against itself and return a flawless-looking
    result from a mistake."""
    import tempfile
    m = _app_module()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="sih26166_test_"))
    a, b = m.upload_paths(tmp, "same.tif", "same.tif")
    assert a != b and a.parent != b.parent
    a.write_bytes(b"A")
    b.write_bytes(b"B")
    assert a.read_bytes() == b"A" and b.read_bytes() == b"B"


def test_the_one_scale_the_ui_multiplies_by_is_the_reference_grid():
    """Both derived figures - residual in metres, change area in square metres -
    come from arrays on the REFERENCE grid, so the factor must be the reference
    label's own GSD. result["gsd_mpp"] is the COMMON grid, which core/scale.py
    sets to the coarser of the two; using it would inflate an area by
    (common/reference)^2 the moment the reference is the finer image.

    reference_gsd returns (value, source) so every metre figure can name its own
    provenance. The label always wins; the catalogue is a named fallback.
    """
    m = _app_module()
    assert m.reference_gsd({}) == (None, None)
    assert m.reference_gsd({"gsd_mpp": 60.0, "meta_reference": {}}) == (None, None)
    # the two grids differ: the reference is the finer image
    mixed = {"gsd_mpp": 60.0, "meta_reference": {"gsd_mpp": 9.3698731836556}}
    assert m.reference_gsd(mixed) == (9.3698731836556, "label")
    # a label scale is never overridden by the catalogue, even when both exist
    assert m.reference_gsd(mixed, "pair_01", "Bundled pair") == (9.3698731836556, "label")
    # ...and on every bundled pair the label value is what comes back
    import pickle
    cache = APP.parent.parent / "demo_cache" / "results"
    seen = 0
    for pkl in sorted(cache.glob("*.pkl")):
        with open(pkl, "rb") as f:
            r = pickle.load(f)
        label = (r.get("meta_reference") or {}).get("gsd_mpp")
        if label:
            assert m.reference_gsd(r) == (float(label), "label")
        else:
            assert m.reference_gsd(r) == (None, None), "no label scale, no bare value"
        seen += 1
    if seen == 0:
        pytest.skip("demo_cache is not synced on this machine (gitignored)")


def test_a_catalogue_scale_is_used_but_never_silently():
    """Known issue 11. pair_01 carries no map scale in either .tif, so the pair
    the demo OPENS with printed METRES NOT AVAILABLE - and Invariant 2 wants the
    metres beside every pixel figure. The catalogue records 0.22977 m/px for it,
    but from a teammate handoff, not from the file.

    So the metres are printed AND the readout says where the scale came from. A
    metre figure whose provenance is weaker than the pixel figure beside it has to
    say so, in a project whose entire argument is that provenance is the point.
    """
    m = _app_module()
    no_label = {"meta_reference": {}}
    # uploads have no catalogue row and must stay void
    assert m.reference_gsd(no_label, "whatever.tif vs other.tif",
                           "Upload two images") == (None, None)
    got = m.reference_gsd(no_label, "pair_01", "Bundled pair")
    if got == (None, None):
        pytest.skip("pairs_catalogue.csv has no ref_gsd_mpp for pair_01 on this machine")
    value, source = got
    assert source == "catalogue" and value > 0

    # the readout prints the metres AND names the source. At 0.23 m/px a 0.0376 px
    # residual is 8.6 MILLIMETRES; two decimals would render that "0.01 m", which
    # reads as a rounded number rather than the precise one it is.
    html = m.readout_for(0.0376, value, "pair_01_ref.tif", True, False, "catalogue")
    assert f"{0.0376 * value:.4f} m" in html
    assert "0.01 m" not in html
    # ...and a large value still reads in plain metres, not four decimals
    big = m.readout_for(4684.908484071721, 9.3698731836556, "t.tif", True, True, "label")
    assert "43897.00 m" in big
    assert "Scale from the catalogue, not the label" in html
    # a label-sourced scale carries no such qualifier
    plain = m.readout_for(0.0376, value, "pair_01_ref.tif", True, False, "label")
    assert "Scale from the catalogue" not in plain

def _contrast(hex_a: str, hex_b: str) -> float:
    """WCAG contrast ratio between two #rrggbb colours."""
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        f = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]
    la, lb = lum(hex_a), lum(hex_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _token(name: str) -> str:
    """Read a --token's hex value out of the SKIN block."""
    m = re.search(r"--" + name + r":\s*(#[0-9A-Fa-f]{6})", _app_module().SKIN)
    assert m, f"--{name} not found in SKIN"
    return m.group(1).upper()


def test_every_signal_colour_meets_AA_on_the_ground_it_is_printed_on():
    """Finding 7. `--caution` is the state word for the Tier D pair - the one
    carrying the 25% novelty claim - and it is printed on `--panel`, not on the
    page. At #A8560A that was 4.40:1, below AA, while the comment quoted the
    4.9:1 it scores on `--ground`. A colour is only as legible as the surface it
    is actually drawn on, so both surfaces are checked here."""
    ground, panel = _token("ground"), _token("panel")
    for name in ("ink", "ink-mute", "accent", "ok", "caution", "fail"):
        c = _token(name)
        assert _contrast(c, ground) >= 4.5, f"--{name} is {_contrast(c, ground):.2f}:1 on --ground"
    # the three that are drawn on the panel: verdict word, table header, strip
    for name in ("ok", "caution", "fail"):
        c = _token(name)
        assert _contrast(c, panel) >= 4.5, f"--{name} is {_contrast(c, panel):.2f}:1 on --panel"


def test_the_hairline_survives_a_projector_lamp():
    """Finding 7. At #C9C7BF the rule was 1.58:1 on the ground: under a lamp it
    washes out and the metrics table becomes rows floating in space."""
    assert _contrast(_token("rule"), _token("ground")) >= 2.0


def test_the_aligned_verdict_is_glossed_in_words_not_machine_prose():
    """Finding 1, and it is a Gate 3 finding: a stranger must explain the output
    unaided. The strip used to interpolate `declared['why']` verbatim - "98% of 64
    measurable cells agree with H -> agrees" - which contains a matrix name, a
    method token, an arrow and "agree...agrees". The raw string still prints in
    the section-03 log, where the audit trail belongs."""
    m = _app_module()
    aligned = SOURCE.split('_v = ((rel or {})')[1].split("imgs = st.columns")[0]
    assert "declared.get('why'" not in aligned, (
        "the ALIGNED strip interpolates the raw reliability sentence again")
    assert "Aligned by the feature matcher" in aligned
    # and the gloss must not claim agreement the check never gave
    assert '"agrees"' in aligned and "could not confirm or contradict" in aligned
    # the raw sentence still reaches the page, in the log
    assert "describe(rel)" in SOURCE
    assert m._cap("area check contradicts H") == "Area check contradicts H"
    assert m._cap("") == ""


def test_the_metrics_section_says_whose_metrics_they_are_on_a_fallback():
    """Finding 2. On the Tier D pair three red FAILs were the loudest legible
    thing on the page, and the sentences that reframe them were the smallest and
    greyest. A judge reads orange, then three FAILs, and concludes it failed - on
    the pair carrying the novelty claim. The rule itself now says whose numbers
    these are, and the Gate-2 sentence leads the section instead of trailing it."""
    m = _app_module()
    assert "matcher's metrics &mdash; transform not used" in SOURCE
    # the Gate-2 sentence is no longer inside the table's own markup...
    table = m.metrics_table_html({"rmse_gt_px": None, "residual_px": 0.1})
    assert "Gate 2 is judged on" not in table
    # ...it is a separate lead, in sans at body size, emitted above the table
    assert "Gate 2 is judged on the synthetic sun-angle sweep" in m.MT_LEAD
    assert "passing or failing them here is not the gate" in m.MT_LEAD
    lead_at = SOURCE.index("st.html(MT_LEAD)")
    table_at = SOURCE.index("st.html(metrics_table_html(")
    assert lead_at < table_at, "the Gate-2 lead must render above the table"


def test_the_label_tier_is_legible_from_five_metres():
    """Finding 3. Cap-height angle = px * 0.70 * (2.0 m / 1366 px) / 5 m; ~15
    arc-minutes is comfortable sustained reading. Every label class sat at
    .72-.78rem = 12.2-13.3 px = 8.6-9.3', so the page read as a big number, three
    photographs and a green grid, with none of the words that say what any of it
    is. This pins the floor rather than the exact sizes."""
    skin = _app_module().SKIN
    for cls in (".tag", ".rail__k", ".seclabel", ".panellabel", ".platecap",
                ".readout__k", ".verdict__word"):
        m = re.search(re.escape(cls) + r"\s*\{[^}]*?font-size:\s*([0-9.]+)rem", skin)
        assert m, f"{cls} has no font-size"
        rem = float(m.group(1))
        px = rem * 17
        arcmin = px * 0.70 * (2000.0 / 1366.0) / 5000.0 * (180 / 3.141592653589793) * 60
        assert arcmin >= 10.0, f"{cls} is {rem}rem = {px:.1f}px = {arcmin:.1f}' at 5 m"


def test_state_is_never_carried_by_colour_alone_in_the_tag_strip():
    """Finding 8. `.tag--live` gave two of the four tags ink and a dark border and
    the other two grey - a two-level state, by colour only, with nothing on the
    page saying what the levels meant."""
    assert "tag--live" not in SOURCE


def test_the_readout_argues_in_sans_and_prints_figures_in_mono():
    """Finding 6. On the fallback pair the only bold text in the readout was
    "= 43897.00 m on the ground", beside a greyed residual - a confident distance
    on the pair we most need to be honest about. The explanatory line is prose and
    is now set as prose."""
    skin = _app_module().SKIN
    m = re.search(r"\.readout__x\s*\{[^}]*?font-family:\s*var\(--(\w+)\)", skin)
    assert m and m.group(1) == "sans", "the readout's explanatory line must be sans"
    assert re.search(r"^\.fig\s*\{", skin, re.M), ".fig must be usable outside .verdict__body"


def test_real_pairs_take_tier_and_same_sensor_from_their_geometry_prior(tmp_path, monkeypatch):
    """demo-medic, 19 Sep: only six pairs are catalogued, so every real pair said
    "Tier unknown" and the same-sensor note never fired on TMC-2 fore/aft."""
    m = _app_module()
    d = tmp_path / "sac_tmcfore_tmcaft_w01"
    d.mkdir()
    (d / "geometry_prior.json").write_text(
        '{"tier": "A (same sensor, viewpoint, real)", "terminology": "same instrument (TMC-2 fore '
        'vs aft): a VIEWPOINT test, NOT cross-sensor", "source": {"instrument": "TMC-2 fore"}, '
        '"reference": {"instrument": "TMC-2 aft"}}', encoding="utf-8")
    monkeypatch.setattr(m, "PAIRS_DIR", tmp_path)
    m.pair_prior.clear()
    meta = m.pair_meta("sac_tmcfore_tmcaft_w01")
    assert meta["tier"] == "A (same sensor, viewpoint, real)" and meta["same_sensor"]
    assert m.pair_identity("sac_tmcfore_tmcaft_w01", "Bundled pair") == (
        "A (same sensor, viewpoint, real)", "TMC-2 fore vs TMC-2 aft")
    assert m.pair_meta("no_such_pair") == {}
    m.pair_prior.clear()
