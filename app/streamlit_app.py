"""The demo UI. This module IS Gate 3 and Gate 4.

    streamlit run app/streamlit_app.py

(`.streamlit/config.toml` sits both at the repo root and beside this file, byte-
identical, so the skin loads from any working directory - a test pins the two.)

Gate 3 (Day 8, 6 Sep): *"A stranger operates the UI and explains the output with
nobody speaking."* Gate 4 (Day 9, 7 Sep): *"Demo runs 3x consecutively on
Samartha's laptop, CPU only, wifi OFF, cached weights and data, no crashes."*

Six design decisions worth defending.

1. THIS FILE COMPUTES NOTHING. Every number on screen comes from
   `core.pipeline.run_all()`, which gets them from `evaluation/metrics.py`. A UI
   that recomputes a metric "just for display" gives the project a second source
   of truth for its headline figure, and Invariant 1 exists because we already
   shipped an invented number through four documents. If a value is not in the
   result dict, this file shows `n/a` rather than deriving it. The only
   arithmetic here is pixels x metres-per-pixel, and both factors come from the
   result dict - the residual in REFERENCE pixels, the reference label's own
   ground sample distance.

2. EVERY EXPENSIVE ACTION IS GATED ON `st.session_state`, NEVER ON A NESTED
   BUTTON. Streamlit re-runs this entire script top to bottom on every single
   interaction, so `st.button()` inside `if st.button():` can NEVER fire - the
   outer button is False on the re-run that would have drawn the inner one. That
   bug is recorded in `.claude/agents/demo-medic.md` and it is the classic way a
   Streamlit demo dies live. So: buttons only ever WRITE to session state, and
   rendering only ever READS from it. Every input that changes the pair - the
   selector, the source radio, the uploaders - resets the result, so a stale
   result can never sit under a new pair's name.

3. NOTHING TOUCHES THE NETWORK. No remote images, no font CDNs, no model
   downloads, no telemetry. Gate 4 is run with the wifi physically off, and a
   single hidden fetch turns a 3-second render into a 30-second timeout in front
   of a judge. Weights come from `weights/`, cached by `core.matcher`. The skin
   below uses system font stacks only; `app/test_streamlit_app.py` asserts the
   string `http` never appears in it.

4. THE TIER IS READ FROM THE CATALOGUE AND SHOWN NEXT TO THE RESULT. `pair_01`
   is two crops of ONE Chandrayaan-2 OHRC frame - same sensor, zero sun
   difference - and calling that "cross-sensor" is the likeliest question to lose
   a Q&A round (Invariant 2). The UI states what the pair actually is, so nobody
   demoing it can imply otherwise by accident. The state rail reads the tier of
   the RESULT's pair, never of whatever the sidebar currently points at.

5. `rmse_gt_px` IS NEVER SHOWN AS A NUMBER ON A REAL PAIR. It is accuracy against
   a KNOWN transform and exists only for synthetic pairs. `residual_px` is a
   held-out fit residual and is what a real pair can honestly report. Printing
   one where the other belongs is a fabrication rather than a bug, so the two are
   labelled distinctly and the unavailable one says why - and the residual is
   labelled "not an accuracy" beside the number, at a size the back row can read.

6. THE SKIN IS A LAB REPORT, NOT A WEB APP, AND STATE IS NEVER COLOUR ALONE. One
   config file (`.streamlit/config.toml`) and ONE injected CSS block (`SKIN`).
   Light paper ground because a projector in a lit classroom cannot project
   black; every measured value in a monospace face next to its grid and its
   metres; every verdict carried by a WORD first and a colour second. The
   reliability map renders its three states as three different KINDS of mark -
   solid tint + "V", hatched tint + "W", faded-to-paper + "-" - and repeats them
   as an ASCII map, so the picture survives a photograph, a colour-blind judge,
   and a washed-out lamp. The primary readout's markup has no slot for a bare
   pixel figure: every form names the reference grid and either gives the
   metres or says, in words, why it cannot.
"""
from __future__ import annotations

import csv
import html as _h
import json
import pathlib
import pickle
import sys
import tempfile
import time

import numpy as np
import streamlit as st

# `streamlit run` executes this file as a script, so the repo root is not on
# sys.path the way it is under `python -m`. Without this, `import core` fails
# with ModuleNotFoundError the moment the app starts.
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# `app/` has no __init__.py, so it is not a package and `app.change_detection`
# does not resolve. Rishabh's own test imports it bare; do the same rather than
# adding an __init__.py to a folder we share with him.
if str(ROOT / "app") not in sys.path:
    sys.path.insert(0, str(ROOT / "app"))

from core.pipeline import resolve_pair, run_all  # noqa: E402
from core.reliability import NO_EVIDENCE, VERIFIED, WEAK, ascii_map, describe, gate  # noqa: E402

PAIRS_DIR = ROOT / "data" / "pairs"
CATALOGUE = ROOT / "data" / "pairs_catalogue.csv"
# Precomputed results for the bundled pairs (ops/precompute_demo_cache.py). A live
# 15-second align inside a 3-minute pitch is risk with no upside; the cached result
# is the SAME run_all() output, pickled, and the live path stays one click away.
CACHE_DIR = ROOT / "demo_cache" / "results"

# The reliability map's three marks. Display only - the states come from
# core/reliability.py via run_all(); nothing is decided here. Three states are
# three different KINDS of mark, never three points on one colour scale:
#   verified     tint, solid border, glyph V
#   weak         tint + 45-degree hatch, dashed border, glyph W
#   no_evidence  NO tint - faded toward paper, dotted border, glyph -
# Only "verified" leaves the terrain at full contrast. Absence renders as absence.
PAPER = (247, 247, 244)
STATE_TINT = {VERIFIED: (20, 107, 60), WEAK: (168, 86, 10), NO_EVIDENCE: None}
STATE_ALPHA = {VERIFIED: 0.25, WEAK: 0.36, NO_EVIDENCE: 0.0}
STATE_FADE = {VERIFIED: 0.0, WEAK: 0.0, NO_EVIDENCE: 0.45}
STATE_GLYPH = {VERIFIED: "V", WEAK: "W", NO_EVIDENCE: "-"}
STATE_WORD = {VERIFIED: "verified", WEAK: "weak", NO_EVIDENCE: "no evidence"}
HATCH_PERIOD = 8          # px between hatch lines in the overlay; the CSS swatch matches

# The five metrics, in the order Canonical Facts Sec.7 lists them, with the
# Gate 2 threshold where one exists (`None` = "no threshold - report it"), the
# threshold written the way Sec.11 writes it, the decimal places shown (four, as
# the deck prints them), and the unit. Places change how many digits are DRAWN;
# the full-precision value rides along in the cell's title attribute. No value
# is changed, rounded in our favour, or recomputed.
METRICS = [
    ("rmse_gt_px", "accuracy vs known transform", "<", 0.5, "0.5", 4, "px"),
    ("residual_px", "held-out fit residual", None, None, "", 4, "px"),
    ("inlier_count", "matches RANSAC accepted", None, None, "", 0, ""),
    ("inlier_ratio", "of raw matches, fraction kept", ">", 0.60, "0.60", 4, ""),
    ("grid_coverage_fraction", "8x8 cells containing a match", ">=", 0.80, "0.80", 4, ""),
    ("distribution_cv", "spread of matches (lower is better)", "<", 1.0, "1.0", 4, ""),
]

# --------------------------------------------------------------------------
# The skin. ONE block, injected once, right after set_page_config. Everything
# load-bearing is on classes this file authors itself (.idplate .rail .seclabel
# .verdict .readout .mt .legend .platecap .log .cellmap .note). Blocks marked
# [FRAGILE] target Streamlit's own data-testids, verified against 1.62.0; if an
# upgrade renames one, that widget degrades to Streamlit's default look and the
# page never breaks. No web font, no URL, no emoji, no gradient, no shadow.
# ASCII only in this source; typographic characters are HTML entities.
# Every colour is one of the palette hexes; the two legend swatches are the
# overlay's own tint maths applied to the plate colour. Contrast on the paper
# ground: ink 16.6:1, ink-mute 6.2:1, ink-faint 5.4:1, caution 4.9:1 (word and
# bar only, never a sentence), ok 6.1:1, fail 7.0:1.
# --------------------------------------------------------------------------
SKIN = """<style>
:root {
  --ink: #14171A;
  --ink-mute: #5A5D63;
  --ink-faint: #62666D;
  --ground: #F7F7F4;     /* page field: paper, not pure white - a lamp blooms on white */
  --panel: #ECEBE6;      /* sidebar, table header, verdict strip */
  --panel-2: #E2E0D9;    /* nested / inset */
  --plate: #E8E7E2;      /* behind image plates */
  --rule: #C9C7BF;       /* hairline */
  --rule-hard: #8C8A82;  /* section rule */
  --accent: #14487F;     /* the interactive accent; the only FILLED accent surface is the Align button */
  --ok: #146B3C;         /* verified / PASS / DECLARED */
  --caution: #A8560A;    /* weak / FALLBACK USED - a word and a bar, never a sentence */
  --fail: #A3231E;       /* contradicted / FAIL / NO TRANSFORM */
  --mono: Consolas, "Cascadia Mono", "DejaVu Sans Mono", "Liberation Mono", Menlo, Monaco, "Courier New", monospace;
  --sans: "Segoe UI", "Segoe UI Variable Text", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial, "Liberation Sans", sans-serif;
  --s1: 4px; --s2: 8px; --s3: 12px; --s4: 16px; --s6: 24px; --s8: 32px; --s12: 48px; --s16: 64px;
  --hatch: repeating-linear-gradient(45deg, transparent 0 6px, rgba(20,23,26,.42) 6px 8px);
}
/* Streamlit is rem-based: this one line is the projector knob. 17px normal, 20px projected. */
html { font-size: __BASE_PX__; }

/* ---- 1. delete the web app ------------------------------------- [FRAGILE] */
[data-testid="stDecoration"], [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"],
[data-testid="stMainMenu"], [data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; pointer-events: none; }
[data-testid="stHeader"] button { pointer-events: auto; }
[data-testid="stAppViewContainer"] *, [data-testid="stSidebar"] * { box-shadow: none !important; }
[data-testid="stAppViewContainer"] *, [data-testid="stSidebar"] * { border-radius: 0 !important; }

/* ---- 2. page ------------------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--ground); color: var(--ink); font-family: var(--sans);
  -webkit-font-smoothing: antialiased;
}
[data-testid="stMainBlockContainer"] {
  max-width: 1320px !important;
  padding: var(--s6) var(--s8) var(--s16) var(--s8) !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] { gap: var(--s3); }
[data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] p { max-width: 78ch; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { font-size: 1rem; line-height: 1.55; }
[data-testid="stCaptionContainer"] p { font-size: .86rem !important; line-height: 1.5; color: var(--ink-mute) !important; }
code, kbd, pre { font-family: var(--mono) !important; font-size: .88em !important; }
h1, h2, h3, h4 { font-family: var(--sans); letter-spacing: -0.005em; color: var(--ink); }
h1 { font-size: 1.55rem; font-weight: 600; } h2 { font-size: 1.15rem; font-weight: 600; } h3 { font-size: 1.02rem; font-weight: 600; }
/* the skin's own element container is empty; give it no height */
[data-testid="stElementContainer"]:has(> div > style:only-child) { display: none !important; }
.stHtml { line-height: 1.4; }

/* ---- 3. identification plate --------------------------------------------- */
.idplate { border-bottom: 3px solid var(--ink); padding-bottom: var(--s2); margin-bottom: var(--s2); }
.idplate__name { font-family: var(--sans); font-size: 1.5rem; font-weight: 600; letter-spacing: -0.01em; line-height: 1.15; }
.idplate__ps { font-family: var(--mono); font-size: .74rem; font-weight: 400; letter-spacing: .10em; color: var(--ink-mute); margin-left: var(--s3); vertical-align: 3px; white-space: nowrap; }
.idplate__sub { font-size: .95rem; color: var(--ink-mute); margin-top: var(--s1); max-width: 78ch; }
.idplate__strip { margin-top: var(--s2); display: flex; flex-wrap: wrap; gap: var(--s2); }
.tag { font-family: var(--mono); font-size: .74rem; letter-spacing: .09em; text-transform: uppercase; color: var(--ink-mute); border: 1px solid var(--rule); padding: 2px var(--s2); white-space: nowrap; }
.tag__v { text-transform: none; letter-spacing: .04em; }
.tag--live { color: var(--ink); border-color: var(--ink); }

/* ---- 3b. state rail (filled LAST, so STATE can never read READY above a result) */
.rail { display: flex; flex-wrap: wrap; gap: var(--s6); border-bottom: 1px solid var(--rule); padding: var(--s1) 0 var(--s2) 0; margin: 0; }
.rail__k { display: block; font-family: var(--mono); font-size: .72rem; letter-spacing: .11em; text-transform: uppercase; color: var(--ink-faint); }
.rail__v { font-family: var(--mono); font-size: .92rem; font-weight: 600; color: var(--ink); white-space: nowrap; }
.rail__v--ok { color: var(--ok); } .rail__v--caution { color: var(--caution); } .rail__v--fail { color: var(--fail); }

/* ---- 4. section label (replaces every divider + subheader pair) ---------- */
.seclabel { display: flex; align-items: baseline; gap: var(--s3); font-family: var(--mono); font-size: .78rem; font-weight: 600; letter-spacing: .11em; text-transform: uppercase; color: var(--ink); border-bottom: 1px solid var(--rule-hard); padding-bottom: var(--s2); margin: var(--s12) 0 var(--s4) 0; }
.seclabel--first { margin-top: var(--s3); }
.seclabel__n { color: var(--ink-faint); font-weight: 400; }
.seclabel__id { text-transform: none; letter-spacing: .04em; font-weight: 400; color: var(--ink-mute); }
.seclabel__note { margin-left: auto; font-weight: 400; letter-spacing: .04em; text-transform: none; color: var(--ink-mute); font-size: .74rem; text-align: right; }
.panellabel { font-family: var(--mono); font-size: .74rem; font-weight: 600; letter-spacing: .11em; text-transform: uppercase; color: var(--ink); border-bottom: 1px solid var(--rule-hard); padding-bottom: var(--s2); margin: var(--s4) 0 var(--s3) 0; }

/* ---- 5. primary readout: value + grid + metres, or an explicit void ------ */
.readout { border-top: 3px solid var(--ink); border-bottom: 1px solid var(--rule); padding: var(--s3) 0 var(--s4) 0; margin: var(--s2) 0 var(--s4) 0; }
.readout__k { font-family: var(--mono); font-size: .84rem; font-weight: 600; letter-spacing: .10em; text-transform: uppercase; color: var(--ink); }
.readout__v { font-family: var(--mono); font-size: 2.75rem; font-weight: 600; line-height: 1.05; letter-spacing: -0.01em; color: var(--ink); font-variant-numeric: tabular-nums; margin-top: var(--s1); }
.readout__u { font-size: 1.05rem; font-weight: 400; color: var(--ink-mute); margin-left: var(--s2); }
.readout__q { font-family: var(--sans); font-size: 1rem; font-weight: 400; letter-spacing: 0; color: var(--ink); margin-left: var(--s4); }
.readout__x { font-family: var(--mono); font-size: .92rem; color: var(--ink); margin-top: var(--s2); max-width: 96ch; line-height: 1.5; }
.readout__x b { font-weight: 600; }
.readout__x .warn { color: var(--caution); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.readout--void .readout__v { color: var(--ink-faint); font-size: 1.6rem; }

/* ---- 6. verdict strip: the WORD first, the 4px bar second ---------------- */
.verdict { display: flex; gap: var(--s4); align-items: flex-start; background: var(--panel); border-left: 4px solid var(--ink-mute); padding: var(--s3) var(--s4); margin: var(--s2) 0 var(--s3) 0; }
.verdict__word { font-family: var(--mono); font-size: .84rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; white-space: nowrap; padding-top: 2px; min-width: 15ch; }
.verdict__body { font-size: .98rem; line-height: 1.5; max-width: 80ch; }
.verdict__body .fig { font-family: var(--mono); font-size: .94em; white-space: nowrap; }
.verdict--ok { border-left-color: var(--ok); } .verdict--ok .verdict__word { color: var(--ok); }
.verdict--caution { border-left-color: var(--caution); } .verdict--caution .verdict__word { color: var(--caution); }
.verdict--fail { border-left-color: var(--fail); } .verdict--fail .verdict__word { color: var(--fail); }

/* ---- 6b. note: typographic replacement for an info box ------------------- */
.note { font-size: 1rem; line-height: 1.5; color: var(--ink); border-left: 4px solid var(--rule-hard); padding: var(--s2) var(--s4); margin: var(--s3) 0; max-width: 80ch; }
.note b { font-weight: 600; }
.kv { display: flex; gap: var(--s3); align-items: baseline; font-family: var(--mono); font-size: .84rem; margin: var(--s1) 0; }
.kv__k { font-size: .72rem; letter-spacing: .11em; text-transform: uppercase; color: var(--ink-faint); min-width: 7ch; }
.kv__v { color: var(--ink); font-weight: 600; }

/* ---- 7. metrics table ---------------------------------------------------- */
.mt { width: 100%; border-collapse: collapse; margin-top: var(--s2); }
.mt th { font-family: var(--mono); font-size: .74rem; font-weight: 600; letter-spacing: .10em; text-transform: uppercase; color: var(--ink-mute); text-align: left; padding: var(--s2) var(--s3); border-bottom: 2px solid var(--ink); white-space: nowrap; }
.mt th.num { text-align: right; font-size: .74rem; font-weight: 600; }
.mt td { padding: var(--s3); border-bottom: 1px solid var(--rule); font-size: .96rem; vertical-align: baseline; }
.mt tr:last-child td { border-bottom: 1px solid var(--rule-hard); }
.mt .k { font-family: var(--mono); font-size: .92rem; white-space: nowrap; }
.mt .num { font-family: var(--mono); font-size: 1.10rem; font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.mt .num--void { font-weight: 400; color: var(--ink-faint); text-align: left; font-size: .90rem; white-space: normal; }
.mt .u { font-family: var(--mono); font-size: .80rem; font-weight: 400; color: var(--ink-mute); padding-left: 6px; }
.mt .m { color: var(--ink-mute); }
.mt .g { font-family: var(--mono); font-size: .88rem; white-space: nowrap; }
.mt .g b { font-weight: 700; letter-spacing: .06em; }
.mt .g--pass b { color: var(--ok); } .mt .g--fail b { color: var(--fail); } .mt .g--none { color: var(--ink-faint); }
.mt .num[title] { cursor: help; }
.mt-note { font-family: var(--mono); font-size: .78rem; color: var(--ink-mute); margin-top: var(--s2); }

/* ---- 8. reliability legend: the swatches are the overlay's tint maths on the plate colour */
.legend { list-style: none; margin: 0 0 var(--s4) 0; padding: 0; display: flex; flex-direction: column; gap: var(--s2); }
.legend li { display: flex; align-items: center; gap: var(--s3); }
.sw { width: 30px; height: 30px; border: 2px solid var(--ink); flex: none; }
.sw--v { background: #B3C8B8; }
.sw--w { background: #D1B394; background-image: var(--hatch); border-style: dashed; }
.sw--n { background: var(--plate); border-style: dotted; border-color: var(--ink-mute); }
.legend__g { font-family: var(--mono); font-size: 1.15rem; font-weight: 700; width: 1.4ch; text-align: center; }
.legend__t { font-size: .92rem; line-height: 1.25; }
.legend__t b { display: block; font-family: var(--mono); font-size: 1.15rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.legend__t span { color: var(--ink-mute); font-size: .82rem; }
.cellmap { display: inline-block; font-family: var(--mono); font-size: 1.06rem; letter-spacing: .12em; line-height: 1.3; white-space: pre; padding: var(--s3); border: 1px solid var(--rule); background: var(--panel); color: var(--ink); }
.cellmap__cap { font-family: var(--mono); font-size: .76rem; color: var(--ink-mute); margin-top: var(--s2); max-width: 34ch; line-height: 1.45; }
.log { font-family: var(--mono); font-size: .84rem; line-height: 1.55; white-space: pre-wrap; background: var(--panel); border-left: 4px solid var(--rule-hard); padding: var(--s3) var(--s4); margin: var(--s3) 0; color: var(--ink); overflow-x: auto; }

/* ---- 9. image plates ----------------------------------------------------- */
[data-testid="stImage"] img { border: 1px solid var(--ink); background: var(--plate); display: block; }
[data-testid="stImageCaption"] { font-family: var(--mono) !important; font-size: .76rem !important; color: var(--ink-mute) !important; text-align: left !important; }
.platecap { font-family: var(--mono); font-size: .76rem; letter-spacing: .04em; color: var(--ink-mute); border-top: 1px solid var(--rule); padding-top: var(--s1); margin-bottom: var(--s2); }
.platecap b { color: var(--ink); text-transform: uppercase; letter-spacing: .10em; }
.plate--void { border: 1px dotted var(--ink-mute); background: var(--plate); min-height: 200px; display: flex; align-items: center; justify-content: center; font-family: var(--mono); font-size: .84rem; color: var(--ink-mute); text-align: center; padding: var(--s4); }

/* ---- 10. sidebar: the control panel --------------------------- [FRAGILE] */
[data-testid="stSidebar"] { border-right: 1px solid var(--rule-hard); }
[data-testid="stSidebarUserContent"] { padding-top: var(--s2) !important; }
[data-testid="stSidebar"] .stHtml:first-child .panellabel { margin-top: 0; }
/* group labels (which pair, which source) read as panel labels; a checkbox is a
   sentence a stranger must recognise as a switch, so it keeps sentence case. */
[data-testid="stSidebar"] :is([data-testid="stSelectbox"], [data-testid="stRadio"], [data-testid="stFileUploader"]) [data-testid="stWidgetLabel"] p {
  font-family: var(--mono) !important; font-size: .74rem !important; letter-spacing: .09em; text-transform: uppercase; color: var(--ink-mute) !important; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p { font-size: 1rem !important; color: var(--ink) !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { font-size: .82rem !important; }
.stButton > button { font-family: var(--mono) !important; font-size: .86rem !important; font-weight: 600 !important; letter-spacing: .11em; text-transform: uppercase; border: 1px solid var(--ink) !important; transition: none !important; }
.stButton > button[kind="primary"] { background: var(--accent) !important; border-color: var(--accent) !important; color: #FFFFFF !important; }
.stButton > button[kind="primary"]:hover { background: #14487F !important; filter: brightness(.85); }
.stButton > button:disabled { border-color: var(--rule) !important; color: var(--ink-faint) !important; }
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] { font-family: var(--mono) !important; font-size: .76rem !important; }

/* ---- 11. what remains of Streamlit's own widgets --------------- [FRAGILE] */
[data-testid="stAlert"] { border: 1px solid var(--rule) !important; border-left: 4px solid var(--ink-mute) !important; background: var(--panel) !important; color: var(--ink) !important; padding: var(--s3) var(--s4) !important; }
[data-testid="stAlert"] p { color: var(--ink) !important; }
[data-testid="stAlertContainer"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stAlert"] svg, [data-testid="stAlert"] [data-testid="stIconMaterial"] { display: none !important; }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) { border-left-color: var(--fail) !important; }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { border-left-color: var(--caution) !important; }
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { border-left-color: var(--ok) !important; }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) { border-left-color: var(--ink) !important; }
[data-testid="stExpander"] details { border: 1px solid var(--rule) !important; background: transparent !important; }
[data-testid="stExpander"] summary p { font-family: var(--mono) !important; font-size: .76rem !important; font-weight: 600 !important; letter-spacing: .09em; text-transform: uppercase; color: var(--ink) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--rule); }
[data-testid="stSpinner"] p { font-family: var(--mono) !important; font-size: .84rem !important; }
.colophon-foot { font-family: var(--mono); font-size: .74rem; letter-spacing: .04em; color: var(--ink-mute); border-top: 1px solid var(--rule); padding-top: var(--s2); margin-top: var(--s8); }

/* ---- 12. last-resort legibility and the paper fallback ------------------- */
@media (prefers-contrast: more) {
  :root { --ink-mute: #3A3D42; --ink-faint: #55585E; --rule: #8C8A82; --rule-hard: #14171A; }
}
@media print {
  [data-testid="stSidebar"], [data-testid="stHeader"], .stButton, [data-testid="stSlider"] { display: none !important; }
  html { font-size: 12px; }
  [data-testid="stMainBlockContainer"] { max-width: none !important; padding: 0 !important; }
  html, body, [data-testid="stAppViewContainer"] { background: #FFFFFF !important; }
  .verdict, .readout, .mt, .legend, .log, [data-testid="stImage"], .cellmap { break-inside: avoid; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>"""


# --------------------------------------------------------------------------
# Helpers. None of these compute a metric - see design decision 1.
# --------------------------------------------------------------------------

def discover_pairs() -> list[pathlib.Path]:
    """Every directory under data/pairs that resolve_pair() can actually open."""
    if not PAIRS_DIR.is_dir():
        return []
    out = []
    for d in sorted(PAIRS_DIR.iterdir()):
        if not d.is_dir():
            continue
        try:
            resolve_pair(d)          # raises SystemExit if it is not a real pair
        except SystemExit:
            continue
        out.append(d)
    return out


@st.cache_data(show_spinner=False)
def catalogue_row(pair_id: str) -> dict:
    """Rohan's row for this pair, or {} if it is not catalogued.

    Cached because it is read on every re-run and Streamlit re-runs constantly.
    """
    if not CATALOGUE.is_file():
        return {}
    try:
        with open(CATALOGUE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("pair_id") == pair_id:
                    return row
    except (OSError, csv.Error):
        return {}
    return {}


def pair_identity(pair_label: str | None, mode: str | None) -> tuple[str, str]:
    """(tier, sensors) for a pair, from the catalogue - never guessed.

    Uploads are "unknown (upload)"; a bundled pair with no catalogue row is
    "unknown". This is what the rail prints, and it is looked up for the pair the
    RESULT came from, so the rail can never describe a different pair than the
    panel below it.
    """
    if not pair_label:
        return "--", "--"
    if mode == "Upload two images":
        return "unknown (upload)", "unknown"
    row = catalogue_row(pair_label)
    if not row:
        return "unknown", "unknown"
    tier = (row.get("tier") or "uncatalogued").strip()
    inst_a = (row.get("source_instrument") or "?").strip()
    inst_b = (row.get("ref_instrument") or "?").strip()
    return tier, f"{inst_a} vs {inst_b}"


def to_display(img) -> np.ndarray | None:
    """Any 2-D array -> uint8 for display. Percentile-stretched, NOT a metric.

    Raw lunar DN can be [7, 255] on one pair and [0, 2040] on another, and a
    warp leaves black borders that would flatten a naive min/max stretch. The
    2nd-98th percentile keeps the terrain visible in both cases. This changes
    only what the eye sees; nothing measured is touched.
    """
    if img is None:
        return None
    a = np.asarray(img, dtype=np.float64)
    if a.ndim != 2 or a.size == 0:
        return None
    finite = a[np.isfinite(a)]
    if finite.size == 0:
        return np.zeros(a.shape, np.uint8)
    lo, hi = np.percentile(finite, [2, 98])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        lo, hi = float(finite.min()), float(finite.max())
        if hi <= lo:
            return np.zeros(a.shape, np.uint8)
    # NaN and +/-inf must be replaced BEFORE the cast. `np.nan.astype(uint8)` is
    # undefined behaviour and produces arbitrary bytes - on screen that is a
    # confetti of random pixels along the warp border, which looks like a broken
    # alignment rather than the empty region it actually is. `warp()` leaves
    # exactly such a border whenever the source does not cover the whole frame.
    scaled = (a - lo) / (hi - lo) * 255.0
    scaled = np.nan_to_num(scaled, nan=0.0, posinf=255.0, neginf=0.0)
    return np.clip(scaled, 0, 255).astype(np.uint8)


def swipe(left, right, frac: float) -> np.ndarray | None:
    """One image with its left `frac` taken from `left` and the rest from `right`.

    The two are shown in the SAME frame, so a misalignment is visible as a break
    across the seam. That is the single most convincing thing a viewer can see -
    far more than a number - which is why Gate 3 asks a stranger to explain the
    output unaided.
    """
    if left is None or right is None or left.shape != right.shape:
        return None
    cut = int(np.clip(frac, 0.0, 1.0) * left.shape[1])
    out = right.copy()
    out[:, :cut] = left[:, :cut]
    if 0 < cut < out.shape[1]:
        out[:, max(0, cut - 1):cut + 1] = 255      # seam marker
    return out


def fmt(value, places: int = 5) -> str:
    """Draw a value with `places` decimals. Display only; the value is untouched."""
    if value is None:
        return "n/a"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    try:
        return f"{float(value):.{places}f}"
    except (TypeError, ValueError):
        return str(value)


def verdict(key: str, value, op: str | None, threshold) -> tuple[bool | None, str | None, object]:
    """Gate 2's own threshold, applied here rather than left to the reader.

    Returns (ok, op, threshold); `ok` is None when there is no threshold or no
    value. Nothing else in this project checks a gate criterion in code - all
    of them are judged by a human comparing a printed number to a table in a
    markdown file, which is exactly how 0.796875 gets read as "about 0.8".
    """
    if op is None or threshold is None or value is None:
        return None, op, threshold
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None, op, threshold
    ok = (v < threshold) if op == "<" else (v > threshold) if op == ">" else (v >= threshold)
    return bool(ok), op, threshold


def reliability_overlay(base_u8, rel) -> np.ndarray | None:
    """The reference image with each 8x8 cell marked by its reliability state.

    Three KINDS of mark, so the state survives a projector, a photograph and a
    colour-blind viewer: verified = tint, solid border, "V"; weak = tint plus a
    45-degree hatch, dashed border, "W"; no evidence = no tint at all, faded
    toward paper, dotted border, "-". The states are read straight from
    run_all()'s result dict; nothing is decided here. Pure numpy for the fill
    and borders; the glyphs need cv2 and degrade to nothing if it is missing.
    """
    if base_u8 is None or rel is None:
        return None
    h, w = base_u8.shape[:2]
    rgb = np.stack([base_u8] * 3, axis=-1).astype(np.float32)
    state = rel["state"]
    g = state.shape[0]
    rows = np.linspace(0, h, g + 1).astype(int)
    cols = np.linspace(0, w, g + 1).astype(int)
    paper = np.array(PAPER, np.float32)
    glyphs = []
    for r in range(g):
        for c in range(g):
            s = str(state[r, c])
            block = rgb[rows[r]:rows[r + 1], cols[c]:cols[c + 1]]
            bh, bw = block.shape[:2]
            if bh == 0 or bw == 0:
                continue
            yy, xx = np.mgrid[0:bh, 0:bw]
            tint = STATE_TINT.get(s)
            alpha = STATE_ALPHA.get(s, 0.0)
            if tint is not None and alpha > 0:
                block[:] = (1.0 - alpha) * block + alpha * np.array(tint, np.float32)
            fade = STATE_FADE.get(s, 0.0)
            if fade > 0:
                block[:] = (1.0 - fade) * block + fade * paper
            if s == WEAK:
                hatch = ((xx + yy) % HATCH_PERIOD) < 2
                block[hatch] *= 0.60
            # Borders: solid / dashed / dotted, by slicing. Thickness scales with
            # the cell so a 12 px cell (pair_03's 101 px reference) is not eaten.
            if s == NO_EVIDENCE:
                t = 1
            else:
                t = int(max(1, min(3, min(bh, bw) // 16)))
            on_h = (yy < t) | (yy >= bh - t)
            on_v = (xx < t) | (xx >= bw - t)
            edge = on_h | on_v
            along = np.where(on_h, xx, yy)
            if s == VERIFIED:
                mask = edge
            elif s == WEAK:
                mask = edge & ((along % 12) < 7)
            else:
                mask = edge & ((along % 8) < 2)
            colour = np.array(tint if tint is not None else (98, 102, 109), np.float32)
            block[mask] = colour
            # thin grid line so the cells read as cells
            block[:1, :] = 30
            block[:, :1] = 30
            glyphs.append((STATE_GLYPH.get(s, "?"), int(cols[c]), int(rows[r]), int(bh)))
    out = np.clip(rgb, 0, 255).astype(np.uint8)
    try:
        import cv2
    except ImportError:           # tint + hatch + border still carry the state
        return out
    for text, x0, y0, bh in glyphs:
        if bh < 16:
            continue
        scale = bh / 95.0
        thick = max(1, int(round(scale * 1.6)))
        (_tw, th), _base = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, thick)
        org = (x0 + 6, y0 + 6 + th)
        cv2.putText(out, text, org, cv2.FONT_HERSHEY_DUPLEX, scale, (20, 23, 26), thick + 2, cv2.LINE_AA)
        cv2.putText(out, text, org, cv2.FONT_HERSHEY_DUPLEX, scale, (255, 255, 255), thick, cv2.LINE_AA)
    return out


def cached_result_path(pair_label: str | None) -> pathlib.Path | None:
    if not pair_label:
        return None
    p = CACHE_DIR / f"{pair_label}.pkl"
    return p if p.is_file() else None


def cached_sidecar(path: pathlib.Path | None) -> dict:
    """The .json beside a cached result (when, which commit, how long), or {}."""
    if path is None:
        return {}
    side = path.with_suffix(".json")
    if not side.is_file():
        return {}
    try:
        return json.loads(side.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def load_cached_result(path: pathlib.Path) -> tuple[dict, dict]:
    """(result dict, sidecar info) from ops/precompute_demo_cache.py's files."""
    with open(path, "rb") as f:
        result = pickle.load(f)
    return result, cached_sidecar(path)


def reset_results() -> None:
    """Drop everything derived from a previous pair.

    Called whenever the input changes - selector, source radio, uploaders.
    Without this, switching pairs leaves the OLD alignment and the OLD metrics
    on screen under the NEW pair's name - a silent, extremely plausible way to
    demo the wrong number.
    """
    for k in ("result", "changes", "overlay", "gated", "pair_label", "pair_mode", "error",
              "result_origin", "overlay_rel", "cache_info"):
        st.session_state.pop(k, None)


# --- HTML emitters. Every interpolated string goes through esc() first. -------

def esc(x) -> str:
    """html.escape for anything that did not originate in this file."""
    return _h.escape("" if x is None else str(x), quote=True)


def seclabel(n: str, text: str, note: str = "", ident: str = "", first: bool = False) -> None:
    """A numbered section rule. `text` is this file's own markup; `ident` and
    `note` are escaped by the caller."""
    ident_html = f'<span class="seclabel__id">&middot; {ident}</span>' if ident else ""
    cls = "seclabel seclabel--first" if first else "seclabel"
    st.html(f'<div class="{cls}"><span class="seclabel__n">{n}</span><span>{text}</span>'
            f'{ident_html}<span class="seclabel__note">{note}</span></div>')


def verdict_strip(kind: str, word: str, body_html: str) -> None:
    """State is carried by the WORD first and the bar second. Never colour alone."""
    st.html(f'<div class="verdict verdict--{kind}"><span class="verdict__word">{word}</span>'
            f'<span class="verdict__body">{body_html}</span></div>')


def note(body_html: str, target=None) -> None:
    (target or st).html(f'<div class="note">{body_html}</div>')


def platecap(target, title: str, shape, what: str) -> None:
    target.html(f'<div class="platecap"><b>{title}</b> &middot; {esc(shape)} &middot; {what}</div>')


def plate(target, arr, title: str, shape, what: str, void_msg: str = "IMAGE NOT READABLE") -> None:
    """One image plate with its caption. A plate whose array is missing renders
    as an explicit void, never as st.image(None) - which raises AttributeError
    and takes the whole page down with a traceback (Gate 4: no crashes)."""
    u8 = to_display(arr)
    if u8 is None:
        target.html(f'<div class="plate--void">{void_msg}</div>')
    else:
        target.image(u8, width='stretch', clamp=True)
    platecap(target, title, shape, what)


def upload_paths(tmp: pathlib.Path, name_a: str, name_b: str) -> tuple[pathlib.Path, pathlib.Path]:
    """Where two uploads are spilled to disk: separate subdirectories, so two files
    with the SAME name cannot overwrite each other. If they did, the pipeline would
    align an image against itself and return a flawless-looking result from a
    mistake."""
    a_dir, b_dir = tmp / "source", tmp / "reference"
    a_dir.mkdir(parents=True, exist_ok=True)
    b_dir.mkdir(parents=True, exist_ok=True)
    return a_dir / pathlib.Path(name_a).name, b_dir / pathlib.Path(name_b).name


def readout_html(kind: str, key_label: str, value_txt: str, unit: str, qualifier: str,
                 extra_html: str) -> str:
    """The primary readout. `kind` is "ok" (value in ink) or "void" (value greyed).
    Every form carries `extra_html`, which names the reference grid and either
    gives the metres or says why it cannot. There is no form without it."""
    cls = "readout" if kind == "ok" else "readout readout--void"
    q = f'<span class="readout__q">{qualifier}</span>' if qualifier else ""
    return (f'<div class="{cls}"><div class="readout__k">{key_label}</div>'
            f'<div class="readout__v">{value_txt}<span class="readout__u">{unit}</span>{q}</div>'
            f'<div class="readout__x">{extra_html}</div></div>')


def reference_gsd(result: dict):
    """The REFERENCE image's own metres-per-pixel, or None.

    Both figures the UI is allowed to derive - the residual in metres and a
    change candidate's area in square metres - are computed from arrays on the
    REFERENCE grid (`evaluation/metrics.py`: "ALL pixel units are REFERENCE-image
    pixels"; the change detector is handed `b_img` and the warp into `b_img`'s
    frame). `result["gsd_mpp"]` is a different quantity: the COMMON grid the
    matcher ran on, which `core/scale.py` sets to the COARSER of the two. They
    are equal on all four bundled pairs and differ by the scale ratio the moment
    the reference is the finer image - the 6.4x two-grid confusion
    `core/reliability.py`'s docstring records from Day 5. One definition, here.
    """
    return (result.get("meta_reference") or {}).get("gsd_mpp") or None


def readout_for(resid, ref_gsd, ref_name: str, aligned_ok: bool, fallback_used: bool) -> str:
    """Pick the readout form for a result. Pure function of the result dict, so it
    is testable: every branch names the grid, and only the branch with a known
    reference GSD prints metres (resid x ref_gsd, both from the dict)."""
    label = "HELD-OUT FIT RESIDUAL &middot; residual_px"
    grid = f"reference grid of {esc(ref_name)}"
    if resid is None:
        return readout_html("void", label, "&mdash;", "", "",
                            f"no transform &mdash; nothing to measure on the {grid}")
    value = esc(f"{resid:.4f}")
    if ref_gsd:
        where = (f"= <b>{resid * ref_gsd:.2f} m</b> on the ground &middot; {grid} at "
                 f"{ref_gsd:.4g} m/px")
    else:
        where = (f"on the {grid} &middot; <span class=\"warn\">metres not available</span> "
                 f"&mdash; neither label carries a map scale, so no metre figure is printed. "
                 f"Never quote this figure without naming its grid.")
    if not aligned_ok:
        return readout_html("void", label + " &middot; NO TRANSFORM", value, "px",
                            "not an alignment",
                            f"No usable transform was found; this is evaluate()'s own fit on the "
                            f"raw matches, {where}. It describes nothing that was aligned.")
    if fallback_used:
        return readout_html("void", label + " &middot; MATCHER TRANSFORM NOT USED", value, "px",
                            "not an accuracy",
                            f"{where}. This residual describes the matcher's transform, which the "
                            f"pixels contradicted and the system did not use. The declared alignment "
                            f"and its uncertainty are in the verdict above, in metres.")
    return readout_html("ok", label, value, "px", "held-out fit residual, not an accuracy", where)


def metrics_table_html(metrics: dict, contradicted: bool = False) -> str:
    """The five metrics as a table. When the frame is contradicted, the matcher's
    residual is drawn in the void style with the words that say why: a
    photograph of this table alone must not carry a bare 4,685 px "residual".
    A value that rounds to its own threshold is drawn to six places, so the
    drawn digits can never contradict the PASS/FAIL word beside them."""
    rows = []
    for key, meaning, op, threshold, thr_txt, places, unit in METRICS:
        value = metrics.get(key)
        ok, op_, _thr = verdict(key, value, op, threshold)
        if key == "rmse_gt_px" and value is None:
            vcell = '<td class="num num--void">n/a - no ground truth on a real pair</td>'
        elif value is None:
            vcell = '<td class="num num--void">n/a</td>'
        elif key == "residual_px" and contradicted:
            full = repr(float(value))
            vcell = (f'<td class="num num--void" title="{esc(full)}">{esc(fmt(value, places))} px '
                     f'&middot; matcher transform, not used</td>')
        else:
            full = int(value) if isinstance(value, (int, np.integer)) else repr(float(value))
            shown = fmt(value, places)
            if ok is not None and shown == f"{float(threshold):.{places}f}":
                shown = fmt(value, 6)
            u = f'<span class="u">{unit}</span>' if unit else ""
            vcell = f'<td class="num" title="{esc(full)}">{esc(shown)}{u}</td>'
        if ok is None:
            gcell = ('<td class="g g--none">reported, no threshold</td>' if op is None
                     else '<td class="g g--none">n/a</td>')
        else:
            word, cls = ("PASS", "g--pass") if ok else ("FAIL", "g--fail")
            gcell = f'<td class="g {cls}"><b>{word}</b> ({esc(op_)} {esc(thr_txt)})</td>'
        rows.append(f'<tr><td class="k">{key}</td>{vcell}<td class="m">{esc(meaning)}</td>{gcell}</tr>')
    return ('<table class="mt"><thead><tr><th>Metric</th><th class="num">Value</th>'
            '<th>What it means</th><th>Gate 2 threshold</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table>"
            '<div class="mt-note">Gate 2 is judged on the synthetic sun-angle sweep in '
            'evaluation/results_log.csv (Canonical Facts sec. 11); the thresholds are shown here for scale.</div>')


def legend_html(counts: dict, n_cells: int) -> str:
    items = []
    for s, cls in ((VERIFIED, "sw--v"), (WEAK, "sw--w"), (NO_EVIDENCE, "sw--n")):
        items.append(f'<li><span class="sw {cls}"></span><span class="legend__g">{STATE_GLYPH[s]}</span>'
                     f'<span class="legend__t"><b>{int(counts.get(s, 0))} / {int(n_cells)}</b>'
                     f'<span>{STATE_WORD[s]}</span></span></li>')
    return '<ul class="legend">' + "".join(items) + "</ul>"


def rail_html(fields: list[tuple[str, str, str]]) -> str:
    cells = "".join(f'<span><span class="rail__k">{k}</span>'
                    f'<span class="rail__v{(" rail__v--" + cls) if cls else ""}">{v}</span></span>'
                    for k, v, cls in fields)
    return f'<div class="rail">{cells}</div>'


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------

st.set_page_config(page_title="SIH26166 - Lunar Image Registration", layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={"Get help": None, "Report a bug": None, "About": None})
# ONE injected block. The projector checkbox only changes the base font size, and
# because Streamlit is rem-based that scales every widget without scaling the
# imagery. `.replace`, not `.format` - the CSS is full of literal braces.
st.html(SKIN.replace("__BASE_PX__", "20px" if st.session_state.get("projector") else "17px"))
# Reserved now, filled at the very END of the script, so the plate's grid tag and
# the rail's STATE describe the result that is actually on screen below them.
_plate = st.empty()
_rail = st.empty()

# --- sidebar: choose the input ------------------------------------------------

with st.sidebar:
    st.html('<div class="panellabel">SELECT PAIR</div>')

    pairs = discover_pairs()
    labels = [p.name for p in pairs]
    # Changing the source is changing the pair: the previous result goes with it.
    mode = st.radio("Source", ["Bundled pair", "Upload two images"], on_change=reset_results)

    src_path = ref_path = None
    pair_label = None
    catalogue_note = ""

    if mode == "Bundled pair":
        if not labels:
            st.error(
                "No pairs found in data/pairs.\n\n"
                "The image files are gitignored - sync them from the shared Drive "
                "folder before demoing."
            )
        else:
            # Open on the demo pair, not on whatever sorts first: pair_00_dryrun is
            # uncatalogued and would greet the Gate-3 stranger with a warning.
            default = labels.index("pair_01") if "pair_01" in labels else 0
            choice = st.selectbox("Pair", labels, index=default, on_change=reset_results)
            pair_label = choice
            try:
                src_path, ref_path = resolve_pair(PAIRS_DIR / choice)
            except SystemExit as e:
                st.error(str(e))
                src_path = ref_path = None

            row = catalogue_row(choice)
            if row:
                inst_a = (row.get("source_instrument") or "?").strip()
                inst_b = (row.get("ref_instrument") or "?").strip()
                # Tier and sensors are printed in the rail above the result; here
                # only the sentence that matters. Invariant 2, enforced in the UI
                # so a demo cannot imply otherwise.
                if inst_a and inst_a == inst_b:
                    st.info(
                        "Same instrument on both sides - this is **not** a "
                        "cross-sensor result, whatever else it shows."
                    )
                catalogue_note = (row.get("notes") or "").strip()
            else:
                st.warning(
                    f"`{choice}` is not in pairs_catalogue.csv, so its tier is "
                    "unknown. A number without its tier is not evidence."
                )
    else:
        up_a = st.file_uploader("Source image", type=["tif", "tiff", "png", "jpg"],
                                on_change=reset_results)
        up_b = st.file_uploader("Reference image", type=["tif", "tiff", "png", "jpg"],
                                on_change=reset_results)
        if up_a and up_b:
            # run_all() takes paths, not arrays, so the uploads are spilled to a
            # temp directory. Kept for the life of the process, not the repo.
            tmp = pathlib.Path(tempfile.mkdtemp(prefix="sih26166_"))
            src_path, ref_path = upload_paths(tmp, up_a.name, up_b.name)
            src_path.write_bytes(up_a.getbuffer())
            ref_path.write_bytes(up_b.getbuffer())
            pair_label = f"{up_a.name} vs {up_b.name}"
            st.warning(
                "Uploaded pair - tier unknown. Nothing measured here may be "
                "quoted without saying what these two images actually are."
            )

    st.html('<div class="panellabel">ALIGN</div>')
    cache_path = cached_result_path(pair_label) if mode == "Bundled pair" else None
    cache_side = cached_sidecar(cache_path)
    use_cache = st.checkbox(
        "Use the precomputed result", value=cache_path is not None,
        disabled=cache_path is None,
    )
    st.button(
        "Align", type="primary", width='stretch',
        disabled=(src_path is None or ref_path is None),
        # Buttons only ever WRITE state. See design decision 2.
        on_click=lambda: st.session_state.update(run_requested=True),
    )
    if cache_path is None:
        st.caption("No precomputed result for this pair - Align runs the matcher live. The "
                   "first run loads the matcher and takes longer than later ones.")
    else:
        took = cache_side.get("seconds")
        took_txt = f"took {float(took):.1f} s elapsed" if took is not None else "elapsed time not recorded"
        st.caption(f"Precomputed result: the same pipeline output, computed earlier and saved "
                   f"by ops/precompute_demo_cache.py ({took_txt}). Untick the box to run the "
                   f"matcher live.")
    if catalogue_note:
        with st.expander("Catalogue note"):
            st.caption(catalogue_note)

    st.html('<div class="panellabel">DISPLAY</div>')
    st.checkbox("Projector mode (larger type)", key="projector")

# --- run, if asked ------------------------------------------------------------

if st.session_state.pop("run_requested", False) and src_path and ref_path:
    reset_results()
    st.session_state["pair_label"] = pair_label
    st.session_state["pair_mode"] = mode
    try:
        if use_cache and cache_path is not None:
            result, info = load_cached_result(cache_path)
            st.session_state["result"] = result
            st.session_state["cache_info"] = info
            st.session_state["elapsed"] = float(info.get("seconds", result.get("seconds", 0.0)))
            st.session_state["result_origin"] = (
                f"precomputed {info.get('computed_at', '(time unknown)')}, "
                f"commit {info.get('git_commit', '?')}, {st.session_state['elapsed']:.1f} s "
                f"elapsed at the time")
        else:
            with st.spinner("Aligning - this is the real pipeline, not a preview..."):
                t0 = time.perf_counter()
                st.session_state["result"] = run_all(src_path, ref_path)
                st.session_state["elapsed"] = time.perf_counter() - t0
                st.session_state["result_origin"] = "live run"
    except Exception as e:                       # a live demo must not show a traceback
        st.session_state["error"] = f"{type(e).__name__}: {e}"

# --- render -------------------------------------------------------------------

if st.session_state.get("error"):
    verdict_strip("fail", "ERROR",
                  f"Alignment failed &mdash; {esc(st.session_state['error'])}. Nothing is shown "
                  "below because there is no result to show. A blank panel is honest; a stale "
                  "one from the previous pair is not.")

r = st.session_state.get("result")

if r is None and not st.session_state.get("error"):
    seclabel("01", "RESULT", first=True)
    note("<b>No result yet.</b> Choose a pair on the left and press <b>Align</b>.")
    with st.expander("What this does, in one paragraph"):
        st.markdown(
            "Two photographs of the same lunar surface taken at different times "
            "look very different, because the Sun has moved and the shadows with "
            "it. Standard software matches images by finding corners and edges - "
            "and shadow edges are fake corners that move, so the alignment drifts. "
            "This pipeline first removes the lighting (keeping the *direction* of "
            "each edge and discarding its brightness), then matches whole patches "
            "with a learned matcher rather than individual corners, then discards "
            "the matches that disagree and checks the survivors are spread across "
            "the whole frame instead of bunched in one bright corner."
        )

# The reference label's own ground sample distance: residual_px is in REFERENCE
# pixels (evaluation/metrics.py), so this - not the common grid the matcher ran
# on - is the factor that turns it into metres. run_all() stores both.
ref_gsd = reference_gsd(r) if r is not None else None

# The identification plate, filled the moment the result is known (before any
# section renders) so the title never blanks while a live run spins.
if r is not None and ref_gsd:
    grid_tag = f'REFERENCE GRID <span class="tag__v">{ref_gsd:.4g} m/px</span>'
else:
    grid_tag = "REFERENCE GRID NOT DECLARED"
_info = st.session_state.get("cache_info") or {}
if r is None:
    result_tag = "RESULT --"
elif _info.get("git_commit"):
    # The commit recorded when the cache was written - the provenance of the
    # result on screen, not a claim about the code currently running.
    result_tag = f'CACHED RESULT <span class="tag__v">commit {esc(_info["git_commit"])}</span>'
else:
    result_tag = "RESULT LIVE RUN"
_plate.html(
    '<div class="idplate">'
    '<div class="idplate__name">Lunar Image Registration<span class="idplate__ps">ISRO SIH26166</span></div>'
    '<div class="idplate__sub">Aligning two images of the same place on the Moon taken under '
    'different sunlight, and reporting where that alignment can be trusted.</div>'
    '<div class="idplate__strip"><span class="tag tag--live">CPU only</span>'
    '<span class="tag tag--live">Offline</span>'
    f'<span class="tag">{grid_tag}</span><span class="tag">{result_tag}</span></div></div>')


if r is not None:
    metrics = r.get("metrics")
    # What the system DECLARED and used. When the matcher's homography is
    # contradicted by the pixels, `warped_final` is the fallback alignment and the
    # matcher's own `warped` is kept for the "what it would have shown" expander.
    warped = r.get("warped_final", r.get("warped"))
    declared = r.get("declared") or {}
    fallback = r.get("fallback") or {}
    rel = r.get("reliability")
    aligned_ok = r.get("H_final", r.get("H")) is not None

    seclabel("01", "RESULT", note=esc(st.session_state.get("result_origin", "")),
             ident=esc(st.session_state.get("pair_label", "pair")), first=True)

    if not aligned_ok:
        verdict_strip("fail", "NO TRANSFORM",
                      "No usable transform was found. The five metrics below are reported "
                      "anyway, because a failed registration is a result and hiding it "
                      "would be the dishonest option.")
    elif fallback.get("used"):
        dx, dy = fallback["shift_px_common_grid"]
        m_txt = f" ({fallback['shift_m']:.0f} m)" if fallback.get("shift_m") is not None else ""
        sp = fallback.get("spread_px")
        sp_txt = ""
        if sp is not None:
            sp_m = f" ({fallback['spread_m']:.0f} m)" if fallback.get("spread_m") is not None else ""
            sp_txt = (f"; the four quadrants disagree by up to <span class=\"fig\">{esc(sp)} px"
                      f"{esc(sp_m)}</span>")
        verdict_strip("caution", "FALLBACK USED",
                      f"<b>The matcher's result was contradicted and not used.</b> "
                      f"{esc(declared.get('why', '')).replace('-&gt;', '&rarr;')}. The system switched to global "
                      f"correlation of the pixels (no features, no RANSAC) and aligned the pair "
                      f"by a translation of <span class=\"fig\">({dx:+d}, {dy:+d}) px{esc(m_txt)}"
                      f"</span>{sp_txt}. That disagreement is the uncertainty to quote.")
    else:
        verdict_strip("ok", "ALIGNED",
                      f"<b>Method used: {esc(declared.get('method', '?'))}</b> &mdash; "
                      f"{esc(declared.get('why', '')).replace('-&gt;', '&rarr;')}.")

    imgs = st.columns(3)
    # run_all does not return the loaded arrays, so re-read only for DISPLAY.
    # Cheap next to matching, and it keeps run_all's contract unchanged.
    try:
        from core.io_loader import load as _load
        a_img, _ = _load(r["source"])
        b_img, _ = _load(r["reference"])
    except Exception:
        a_img = b_img = None

    if a_img is None or b_img is None:
        # The cached pickles store the paths of the machine that wrote them. On a
        # backup laptop or after the data folder moves, the pictures cannot be
        # re-opened; the numbers are still the pipeline's own output.
        verdict_strip("caution", "IMAGES NOT READABLE",
                      f"The result's image files could not be re-opened for display "
                      f"({esc(pathlib.Path(r['source']).name)}, "
                      f"{esc(pathlib.Path(r['reference']).name)}). The numbers below are still "
                      f"the pipeline's own output; only the pictures are missing. If this is a "
                      f"precomputed result, the cache was written on another machine or the data "
                      f"folder has moved - untick the box and run live.")
    plate(imgs[0], a_img, "Source", r["shape_source"], "the image being moved")
    plate(imgs[1], b_img, "Reference", r["shape_reference"], "the frame everything is measured in")
    if warped is not None:
        plate(imgs[2], warped, "Source, aligned onto reference", tuple(warped.shape[:2]),
              f"what the system declared ({esc(declared.get('method', '?'))})")
    else:
        plate(imgs[2], None, "Source, aligned onto reference", "n/a", "no transform",
              void_msg="NO ALIGNED IMAGE<br>the transform could not be estimated")

    # --- swipe ---------------------------------------------------------------
    if warped is not None and b_img is not None:
        seclabel("02", "SWIPE &mdash; REFERENCE VS ALIGNED")
        sw = st.columns([3, 2])
        with sw[0]:
            frac = st.slider("Seam position", 0.0, 1.0, 0.5, 0.01)
            blended = swipe(to_display(b_img), to_display(warped), frac)
            if blended is None:
                note("Reference and aligned image are different sizes &mdash; no swipe.")
            else:
                st.image(blended, width='stretch', clamp=True)
        with sw[1]:
            note("<b>Left of the line</b> is the reference image, <b>right of it</b> is the "
                 "aligned source. If the alignment is good, features run straight across "
                 "the seam without a step. Drag the seam.")
            if fallback.get("used") and r.get("warped") is not None:
                with st.expander("What the matcher alone would have shown"):
                    st.caption(
                        "The homography MAGSAC++ fitted to the matcher's correspondences. "
                        "It reached consensus - and the pixels say it is wrong. This is why "
                        "a fit residual is not an accuracy."
                    )
                    blended_m = swipe(to_display(b_img), to_display(r["warped"]), frac)
                    if blended_m is not None:
                        st.image(blended_m, width='stretch', clamp=True)

    # --- where it can be trusted ------------------------------------------------
    seclabel("03", "WHERE THE ALIGNMENT CAN BE TRUSTED")
    if rel is None:
        note(f"<b>Unavailable</b> &mdash; {esc(r.get('reliability_note', 'core/reliability.py did not run'))}.")
    else:
        # Drawn once per result, not once per slider drag: the seam slider above
        # forces a full rerun on every move.
        if st.session_state.get("overlay_rel") is None and b_img is not None:
            st.session_state["overlay_rel"] = reliability_overlay(to_display(b_img), rel)
        ov = st.session_state.get("overlay_rel")
        mc = st.columns([3, 2])
        if ov is not None:
            mc[0].image(ov, width='stretch', clamp=True)
        with mc[1]:
            st.html(legend_html(rel["counts"], rel["n_cells"]))
            st.html('<div class="cellmap">' + esc(ascii_map(rel)) + '</div>'
                    '<div class="cellmap__cap">V verified &middot; w weak &middot; . no evidence. '
                    'Row 0 is the top of the image.</div>')
            st.caption(
                "Each cell of the reference frame gets one of three states. **Verified**: "
                "enough matches, they agree with the transform, and an independent check of "
                "the pixels themselves (which never looks at the matches) agrees too. "
                "**Weak**: matches exist but at least one test fails. **No evidence**: the "
                "matcher measured nothing here - not a low score, an absence."
            )
        lines = [ln for ln in describe(rel) if not ln.strip().startswith("true error")]
        st.html('<div class="log">' + esc("\n".join(lines)) + '</div>')
        with st.expander("Rule applied - the exact thresholds"):
            st.html('<div class="log">' + esc(rel["config"]) + '</div>')
        gl = rel.get("global", {})
        if gl.get("contradicted"):
            verdict_strip("fail", "CONTRADICTED",
                          "The whole-frame check contradicts the matcher's transform, so no "
                          "cell can be verified. Nothing measured on this pair should be quoted "
                          "as an alignment accuracy.")

    # --- the five metrics ----------------------------------------------------
    seclabel("04", "THE FIVE METRICS")

    if metrics is None:
        note(f"<b>Unavailable</b> &mdash; {esc(r.get('metrics_note', 'evaluation/metrics.py did not run'))}. "
             "No substitute is computed here on purpose: evaluation/metrics.py is "
             "the single source of numbers for this project.")
    else:
        st.html(readout_for(metrics.get("residual_px"), ref_gsd, pathlib.Path(r["reference"]).name,
                            aligned_ok, bool(fallback.get("used"))))
        st.html(metrics_table_html(metrics, contradicted=(not aligned_ok) or bool(fallback.get("used"))))

        st.html('<div class="log">' + esc(
            f"matches {r['n_matches']}  |  {r['ransac']['note']}  |  "
            f"illumination: {r['illumination']}  |  "
            f"{st.session_state.get('elapsed', r['seconds']):.1f} s elapsed") + '</div>')

        d = r.get("distribution")
        if d:
            st.caption(
                f"Where the matches landed: {d['n_cells'] - d['n_empty']}/{d['n_cells']} "
                f"cells occupied, {d['n_weak']} below {d['min_per_cell']} per cell. "
                f"Diagnostic only - grid_coverage_fraction above is the Gate 2 number "
                f"and counts a different set of points."
            )

    # --- change detection ----------------------------------------------------
    seclabel("05", "CHANGE DETECTION")
    st.caption(
        "Only meaningful once the pair is aligned - on misaligned images every "
        "edge looks like a change."
    )

    if warped is None or b_img is None:
        note("Align the pair first.")
    else:
        # The reference grid, not the common grid: the detector is handed the
        # reference image and the warp into its frame. See reference_gsd().
        gsd_known = ref_gsd
        gsd_use = gsd_known or st.number_input(
            "Ground scale (m/pixel) - not in either label, so it must be supplied",
            min_value=0.0, value=0.0, step=0.01, format="%.5f",
        )
        st.button(
            "Detect changes", width='stretch',
            disabled=not gsd_use,
            on_click=lambda: st.session_state.update(detect_requested=True),
        )
        if not gsd_use:
            st.caption("Areas are reported in square metres, so a ground scale is required.")
        elif not gsd_known:
            st.caption("Ground scale typed by the operator - the areas below depend on it and "
                       "come from no label or catalogue.")

        if st.session_state.pop("detect_requested", False):
            try:
                from change_detection import detect_changes
                ref_u8 = to_display(b_img)
                war_u8 = to_display(warped)
                overlay, changes = detect_changes(ref_u8, war_u8, gsd_mpp=float(gsd_use))
                st.session_state["overlay"] = overlay
                st.session_state["changes"] = changes
                # The gate labels; it does not alter Rishabh's detections.
                st.session_state["gated"] = (gate(changes, rel, b_img.shape[:2])
                                             if rel is not None else None)
            except Exception as e:
                st.session_state["overlay"] = None
                st.session_state["changes"] = None
                st.session_state["gated"] = None
                verdict_strip("fail", "ERROR",
                              f"Change detection failed &mdash; {esc(type(e).__name__)}: {esc(e)}")

        changes = st.session_state.get("changes")
        if changes is not None:
            overlay = st.session_state.get("overlay")
            if overlay is not None:
                st.image(overlay, channels="BGR", width='stretch')
            if not changes:
                note("No changes above the threshold.")
            else:
                buckets: dict[str, int] = {}
                for c in changes:
                    buckets[c.get("classification", "unclassified")] = \
                        buckets.get(c.get("classification", "unclassified"), 0) + 1
                st.markdown(
                    f"**{len(changes)} candidates:** "
                    + ", ".join(f"{n} {k}" for k, n in sorted(buckets.items()))
                )
                gated = st.session_state.get("gated")
                if gated is not None:
                    gc = gated["counts"]
                    st.markdown(
                        f"**After the reliability gate:** {gc['kept']} kept (in verified cells), "
                        f"{gc['rejected_weak']} rejected (in weak cells), "
                        f"{gc['unassessable']} unassessable (in cells with no evidence)."
                    )
                    st.caption(
                        "A difference in a region where the alignment was never verified is "
                        "not a detection and not a false alarm - it is a hole in the evidence, "
                        "and it is reported as one."
                    )
                    labelled = gated["kept"] + gated["rejected_weak"] + gated["unassessable"]
                else:
                    labelled = [dict(c, reliability="n/a") for c in changes]
                st.caption(
                    "Candidates, not confirmed changes. On an optical-versus-"
                    "elevation pair most of these are expected to be artefacts of "
                    "the two images being different kinds of picture."
                )
                # Kept as st.dataframe on purpose: this can run to hundreds of rows
                # and needs virtual scrolling. The reliability column is the WORD.
                area_col = "area_m2" if gsd_known else "area_m2 (operator-supplied scale)"
                st.dataframe(
                    [{"reliability": STATE_WORD.get(c.get("reliability"), c.get("reliability")),
                      "classification": c.get("classification"),
                      area_col: c.get("area_m2"),
                      "area_px": c.get("area_px"),
                      "centroid_px": c.get("centroid_px")} for c in labelled],
                    width='stretch', hide_index=True, height=320,
                )

# --- footer -------------------------------------------------------------------

seclabel("06", "WHAT THESE NUMBERS DO AND DO NOT PROVE")
with st.expander("The four definitions"):
    st.markdown(
        """
- **`rmse_gt_px`** is accuracy against a *known* transform. It exists only for
  synthetic pairs, where we generated the geometry and therefore know the right
  answer. On a real lunar pair it is `n/a` - never a number.
- **`residual_px`** is a held-out fit residual: the transform is fitted on 80% of
  the matches and the error is measured on the 20% it never saw. It is what a
  real pair can honestly report, and it is **not** interchangeable with
  `rmse_gt_px`.
- **"Cross-sensor"** means two *different instruments*. LROC NAC against LROC NAC
  is the same sensor, and two crops of one frame is the same *image*.
- **Any pixel figure** needs the grid it was measured on and its metres
  equivalent, or it means nothing.
        """
    )
st.html('<div class="colophon-foot">Every figure shown here comes from evaluation/metrics.py via '
        'core/pipeline.py. This file computes no metric of its own.</div>')

# --- the rail, filled LAST -------------------------------------------------------
# Filled after everything else has rendered, so STATE describes the result that
# is actually on screen and can never read READY above a live one.

if st.session_state.get("error"):
    state_word, state_cls = "ERROR", "fail"
elif r is None:
    state_word, state_cls = "READY", ""
elif r.get("H_final", r.get("H")) is None:
    state_word, state_cls = "NO TRANSFORM", "fail"
elif (r.get("fallback") or {}).get("used"):
    state_word, state_cls = "FALLBACK USED", "caution"
else:
    state_word, state_cls = "ALIGNED", "ok"
# Tier and sensors of the pair the RESULT came from (design decision 4). Before
# a result exists they describe the sidebar's current selection.
if r is not None:
    rail_pair = st.session_state.get("pair_label")
    rail_tier, rail_sensors = pair_identity(rail_pair, st.session_state.get("pair_mode"))
else:
    rail_pair = pair_label
    rail_tier, rail_sensors = pair_identity(pair_label, mode)
_origin = st.session_state.get("result_origin", "")
_source = "--" if r is None else ("precomputed" if _origin.startswith("precomputed") else "live run")
_elapsed = "--" if r is None else f"{st.session_state.get('elapsed', r.get('seconds', 0.0)):.1f} s"
_rail.html(rail_html([
    ("Pair", esc(rail_pair or "--"), ""),
    ("Tier", esc(rail_tier), ""),
    ("Sensors", esc(rail_sensors), ""),
    ("State", state_word, state_cls),
    ("Result source", _source, ""),
    ("Elapsed", _elapsed, ""),
]))
