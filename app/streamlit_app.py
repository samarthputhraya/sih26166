"""The demo UI. This module IS Gate 3 and Gate 4.

    streamlit run app/streamlit_app.py

Gate 3 (Day 10): *"A stranger operates the UI and explains the output with nobody
speaking."* Gate 4 (Day 11): *"Demo runs 3x consecutively on Samartha's laptop,
CPU only, wifi OFF, cached weights and data, no crashes."*

Five design decisions worth defending.

1. THIS FILE COMPUTES NOTHING. Every number on screen comes from
   `core.pipeline.run_all()`, which gets them from `evaluation/metrics.py`. A UI
   that recomputes a metric "just for display" gives the project a second source
   of truth for its headline figure, and Invariant 1 exists because we already
   shipped an invented number through four documents. If a value is not in the
   result dict, this file shows `n/a` rather than deriving it.

2. EVERY EXPENSIVE ACTION IS GATED ON `st.session_state`, NEVER ON A NESTED
   BUTTON. Streamlit re-runs this entire script top to bottom on every single
   interaction, so `st.button()` inside `if st.button():` can NEVER fire - the
   outer button is False on the re-run that would have drawn the inner one. That
   bug is recorded in `.claude/agents/demo-medic.md` and it is the classic way a
   Streamlit demo dies live. So: buttons only ever WRITE to session state, and
   rendering only ever READS from it.

3. NOTHING TOUCHES THE NETWORK. No remote images, no font CDNs, no model
   downloads, no telemetry. Gate 4 is run with the wifi physically off, and a
   single hidden fetch turns a 3-second render into a 30-second timeout in front
   of a judge. Weights come from `weights/`, cached by `core.matcher`.

4. THE TIER IS READ FROM THE CATALOGUE AND SHOWN NEXT TO THE RESULT. `pair_01`
   is two crops of ONE Chandrayaan-2 OHRC frame - same sensor, zero sun
   difference - and calling that "cross-sensor" is the likeliest question to lose
   a Q&A round (Invariant 2). The UI states what the pair actually is, so nobody
   demoing it can imply otherwise by accident.

5. `rmse_gt_px` IS NEVER SHOWN AS A NUMBER ON A REAL PAIR. It is accuracy against
   a KNOWN transform and exists only for synthetic pairs. `residual_px` is a
   held-out fit residual and is what a real pair can honestly report. Printing
   one where the other belongs is a fabrication rather than a bug, so the two are
   labelled distinctly and the unavailable one says why.
"""
from __future__ import annotations

import csv
import pathlib
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

PAIRS_DIR = ROOT / "data" / "pairs"
CATALOGUE = ROOT / "data" / "pairs_catalogue.csv"

# The five metrics, in the order Canonical Facts Sec.7 lists them, with the
# Gate 2 threshold where one exists. `None` means "no threshold - report it".
METRICS = [
    ("rmse_gt_px", "accuracy vs known transform", "<", 0.5),
    ("residual_px", "held-out fit residual", None, None),
    ("inlier_count", "matches RANSAC accepted", None, None),
    ("inlier_ratio", "of raw matches, fraction kept", ">", 0.60),
    ("grid_coverage_fraction", "8x8 cells containing a match", ">=", 0.80),
    ("distribution_cv", "spread of matches (lower is better)", "<", 1.0),
]


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
    if value is None:
        return "n/a"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    try:
        return f"{float(value):.{places}f}"
    except (TypeError, ValueError):
        return str(value)


def verdict(key: str, value, op: str | None, threshold) -> str:
    """Gate 2's own threshold, applied here rather than left to the reader.

    Nothing else in this project checks a gate criterion in code - all of them
    are judged by a human comparing a printed number to a table in a markdown
    file, which is exactly how 0.796875 gets read as "about 0.8".
    """
    if op is None or threshold is None or value is None:
        return ""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return ""
    ok = (v < threshold) if op == "<" else (v > threshold) if op == ">" else (v >= threshold)
    return f"{'PASS' if ok else 'FAIL'}  ({op} {threshold})"


def reset_results() -> None:
    """Drop everything derived from a previous pair.

    Called whenever the input changes. Without this, switching pairs leaves the
    OLD alignment and the OLD metrics on screen under the NEW pair's name - a
    silent, extremely plausible way to demo the wrong number.
    """
    for k in ("result", "changes", "overlay", "pair_label", "error"):
        st.session_state.pop(k, None)


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------

st.set_page_config(page_title="SIH26166 - Lunar Image Registration", layout="wide")
st.title("Lunar Image Registration")
st.caption(
    "Aligning two images of the same place on the Moon taken under different "
    "sunlight. SIH 2026 - ISRO problem statement SIH26166. Runs on CPU, offline."
)

# --- sidebar: choose the input ------------------------------------------------

with st.sidebar:
    st.header("1 - Choose a pair")

    pairs = discover_pairs()
    labels = [p.name for p in pairs]
    mode = st.radio(
        "Source", ["Bundled pair", "Upload two images"],
        help="Bundled pairs live in data/pairs and are the ones used for the gates.",
    )

    src_path = ref_path = None
    pair_label = None

    if mode == "Bundled pair":
        if not labels:
            st.error(
                "No pairs found in data/pairs.\n\n"
                "The image files are gitignored - sync them from the shared Drive "
                "folder before demoing."
            )
        else:
            choice = st.selectbox("Pair", labels, on_change=reset_results)
            pair_label = choice
            try:
                src_path, ref_path = resolve_pair(PAIRS_DIR / choice)
            except SystemExit as e:
                st.error(str(e))
                src_path = ref_path = None

            row = catalogue_row(choice)
            if row:
                tier = (row.get("tier") or "uncatalogued").strip()
                st.markdown(f"**Tier:** `{tier}`")
                inst_a = (row.get("source_instrument") or "?").strip()
                inst_b = (row.get("ref_instrument") or "?").strip()
                st.caption(f"{inst_a} vs {inst_b}")
                # Invariant 2, enforced in the UI so a demo cannot imply otherwise.
                if inst_a and inst_a == inst_b:
                    st.info(
                        "Same instrument on both sides - this is **not** a "
                        "cross-sensor result, whatever else it shows."
                    )
                if row.get("notes"):
                    st.caption(row["notes"])
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
            src_path, ref_path = tmp / up_a.name, tmp / up_b.name
            src_path.write_bytes(up_a.getbuffer())
            ref_path.write_bytes(up_b.getbuffer())
            pair_label = f"{up_a.name} vs {up_b.name}"
            st.warning(
                "Uploaded pair - tier unknown. Nothing measured here may be "
                "quoted without saying what these two images actually are."
            )

    st.divider()
    st.header("2 - Align")
    st.button(
        "Align", type="primary", width='stretch',
        disabled=(src_path is None or ref_path is None),
        # Buttons only ever WRITE state. See design decision 2.
        on_click=lambda: st.session_state.update(run_requested=True),
    )
    st.caption("First run loads the matcher and takes longer than later ones.")

# --- run, if asked ------------------------------------------------------------

if st.session_state.pop("run_requested", False) and src_path and ref_path:
    reset_results()
    st.session_state["pair_label"] = pair_label
    try:
        with st.spinner("Aligning - this is the real pipeline, not a preview..."):
            t0 = time.perf_counter()
            st.session_state["result"] = run_all(src_path, ref_path)
            st.session_state["elapsed"] = time.perf_counter() - t0
    except Exception as e:                       # a live demo must not show a traceback
        st.session_state["error"] = f"{type(e).__name__}: {e}"

# --- render -------------------------------------------------------------------

if st.session_state.get("error"):
    st.error(f"Alignment failed - {st.session_state['error']}")
    st.caption(
        "Nothing is shown above because there is no result to show. A blank "
        "panel is honest; a stale one from the previous pair is not."
    )

r = st.session_state.get("result")

if r is None and not st.session_state.get("error"):
    st.info("Choose a pair on the left and press **Align**.")
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

if r is not None:
    metrics = r.get("metrics")
    warped = r.get("warped")
    aligned_ok = r.get("H") is not None

    st.subheader(f"Result - {st.session_state.get('pair_label', 'pair')}")

    if not aligned_ok:
        st.error(
            "No usable transform was found. The five metrics below are reported "
            "anyway, because a failed registration is a result and hiding it "
            "would be the dishonest option."
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Source**")
        st.caption(f"{r['shape_source']} - the image being moved")
    with c2:
        st.markdown("**Reference**")
        st.caption(f"{r['shape_reference']} - the frame everything is measured in")
    with c3:
        st.markdown("**Source, aligned onto reference**")
        st.caption("n/a - no transform" if warped is None else "the pipeline's output")

    imgs = st.columns(3)
    # run_all does not return the loaded arrays, so re-read only for DISPLAY.
    # Cheap next to matching, and it keeps run_all's contract unchanged.
    try:
        from core.io_loader import load as _load
        a_img, _ = _load(r["source"])
        b_img, _ = _load(r["reference"])
    except Exception:
        a_img = b_img = None

    imgs[0].image(to_display(a_img), width='stretch', clamp=True)
    imgs[1].image(to_display(b_img), width='stretch', clamp=True)
    if warped is not None:
        imgs[2].image(to_display(warped), width='stretch', clamp=True)
    else:
        imgs[2].info("No aligned image - the transform could not be estimated.")

    # --- swipe ---------------------------------------------------------------
    if warped is not None and b_img is not None:
        st.divider()
        st.subheader("Swipe: reference vs aligned")
        st.caption(
            "Left of the line is the reference image, right of it is the aligned "
            "source. If the alignment is good, features run straight across the "
            "seam without a step."
        )
        frac = st.slider("Seam position", 0.0, 1.0, 0.5, 0.01)
        blended = swipe(to_display(b_img), to_display(warped), frac)
        if blended is None:
            st.info("Reference and aligned image are different sizes - no swipe.")
        else:
            st.image(blended, width='stretch', clamp=True)

    # --- the five metrics ----------------------------------------------------
    st.divider()
    st.subheader("The five metrics")

    if metrics is None:
        st.warning(
            f"Unavailable - {r.get('metrics_note', 'evaluation/metrics.py did not run')}. "
            "No substitute is computed here on purpose: evaluation/metrics.py is "
            "the single source of numbers for this project."
        )
    else:
        rows = []
        for key, meaning, op, threshold in METRICS:
            value = metrics.get(key)
            shown = fmt(value)
            if key == "rmse_gt_px" and value is None:
                shown = "n/a - no ground truth on a real pair"
            rows.append({
                "metric": key,
                "value": shown,
                "what it means": meaning,
                "Gate 2": verdict(key, value, op, threshold),
            })
        st.dataframe(rows, width='stretch', hide_index=True)

        gsd = r.get("gsd_mpp")
        resid = metrics.get("residual_px")
        if gsd and resid is not None:
            st.success(
                f"**{resid:.4g} pixels** on the reference image, which at "
                f"{gsd:.4g} m/pixel is **{resid * gsd:.2f} m on the ground.**"
            )
        elif resid is not None:
            st.caption(
                f"residual_px is {resid:.4g} reference pixels. The metres "
                "equivalent is unavailable because neither label carries a map "
                "scale - never quote a pixel figure without naming its grid."
            )

        st.caption(
            f"matches {r['n_matches']} - {r['ransac']['note']} - "
            f"illumination: {r['illumination']} - "
            f"{st.session_state.get('elapsed', r['seconds']):.1f} s"
        )

        d = r.get("distribution")
        if d:
            st.caption(
                f"Where the matches landed: {d['n_cells'] - d['n_empty']}/{d['n_cells']} "
                f"cells occupied, {d['n_weak']} below {d['min_per_cell']} per cell. "
                f"Diagnostic only - grid_coverage_fraction above is the Gate 2 number "
                f"and counts a different set of points."
            )

    # --- change detection ----------------------------------------------------
    st.divider()
    st.subheader("Change detection")
    st.caption(
        "Only meaningful once the pair is aligned - on misaligned images every "
        "edge looks like a change."
    )

    if warped is None or b_img is None:
        st.info("Align the pair first.")
    else:
        gsd_known = r.get("gsd_mpp")
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
            st.caption("Areas are reported in m2, so a ground scale is required.")

        if st.session_state.pop("detect_requested", False):
            try:
                from change_detection import detect_changes
                ref_u8 = to_display(b_img)
                war_u8 = to_display(warped)
                overlay, changes = detect_changes(ref_u8, war_u8, gsd_mpp=float(gsd_use))
                st.session_state["overlay"] = overlay
                st.session_state["changes"] = changes
            except Exception as e:
                st.session_state["overlay"] = None
                st.session_state["changes"] = None
                st.error(f"Change detection failed - {type(e).__name__}: {e}")

        changes = st.session_state.get("changes")
        if changes is not None:
            overlay = st.session_state.get("overlay")
            if overlay is not None:
                st.image(overlay, channels="BGR", width='stretch')
            if not changes:
                st.info("No changes above the threshold.")
            else:
                buckets: dict[str, int] = {}
                for c in changes:
                    buckets[c.get("classification", "unclassified")] = \
                        buckets.get(c.get("classification", "unclassified"), 0) + 1
                st.markdown(
                    f"**{len(changes)} candidates:** "
                    + ", ".join(f"{n} {k}" for k, n in sorted(buckets.items()))
                )
                st.caption(
                    "Candidates, not confirmed changes. On an optical-versus-"
                    "elevation pair most of these are expected to be artefacts of "
                    "the two images being different kinds of picture."
                )
                st.dataframe(
                    [{"classification": c.get("classification"),
                      "area_m2": c.get("area_m2"),
                      "area_px": c.get("area_px"),
                      "centroid_px": c.get("centroid_px")} for c in changes],
                    width='stretch', hide_index=True,
                )

# --- footer -------------------------------------------------------------------

st.divider()
with st.expander("What these numbers do and do not prove"):
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
st.caption(
    "Every figure shown here comes from evaluation/metrics.py via "
    "core/pipeline.py. This file computes no metric of its own."
)
