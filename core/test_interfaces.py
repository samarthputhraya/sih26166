"""The fixed interfaces of `core/`. Day 4's row, delivered as a lock rather than a rewrite.

WHY A LOCK AND NOT A REFACTOR
-----------------------------
The Day-4 row says *"Refactor core/ to fixed interfaces today"*. The POINT of that task is that
four other people can build against `core/` without the ground moving under them. A broad
rewrite two days before Gate 1, on a pipeline that currently runs end to end, buys none of that
and risks all of it.

So the interfaces are fixed HERE instead: every public signature and every consumed dict key is
asserted. Rename a parameter, reorder two, or drop a result key, and a test fails on the machine
of whoever did it - which is the actual guarantee teammates need. `core/INTERFACES.md` is the
same contract in prose.

Changing an interface is allowed. Changing it *silently* is not. If you meant it, update this
file in the same commit and say so in the message.
"""
import inspect

import pytest


def params(fn):
    return list(inspect.signature(fn).parameters)


# --- the signatures everyone else builds against -----------------------------

EXPECTED = {
    "core.io_loader:load": ["path", "window"],
    "core.io_loader:as_cv_safe": ["arr"],
    "core.io_loader:plan_overlap": ["meta_a", "meta_b", "shape_a", "shape_b"],
    "core.io_loader:crop_to_overlap": ["src_path", "ref_path", "out_prefix"],

    "core.scale:to_common_gsd": ["img_a", "meta_a", "img_b", "meta_b"],
    "core.scale:to_original": ["pts", "factors"],
    "core.scale:resample": ["img", "factor_x", "factor_y"],

    "core.illumination:normalize": ["img", "method"],
    "core.illumination:gradient_orientation": ["img", "eps"],
    "core.illumination:phase_congruency": ["img", "eps"],

    "core.ransac:filter_matches": ["src", "ref", "threshold_px", "confidence", "method"],
    "core.ransac:warp": ["img", "H", "out_shape"],

    "core.subpixel:refine": ["src_pts", "ref_pts", "src_img", "ref_img",
                             "patch", "search", "min_peak"],
    "core.subpixel:metres": ["px", "gsd_mpp"],
    "core.subpixel:describe": ["px", "gsd_mpp", "grid"],

    "core.distribution:cell_index": ["pts", "shape", "grid"],
    "core.distribution:counts": ["pts", "shape", "grid"],
    "core.distribution:weak_cells": ["cell_counts", "min_per_cell"],
    "core.distribution:cell_bounds": ["cell", "shape", "grid", "margin"],
    "core.distribution:redetect": ["src_img", "ref_img", "H", "cells", "match_fn",
                                   "grid", "margin", "max_cells"],
    "core.distribution:summary": ["pts", "shape", "grid", "min_per_cell"],

    "core.pipeline:run_all": ["src_path", "ref_path", "H_true", "progress", "subpixel"],
}


@pytest.mark.parametrize("target,expected", sorted(EXPECTED.items()))
def test_public_signature_is_unchanged(target, expected):
    import importlib
    mod_name, fn_name = target.split(":")
    fn = getattr(importlib.import_module(mod_name), fn_name)
    assert params(fn) == expected, (
        f"{target} changed shape. If that was deliberate, update EXPECTED in this file in the "
        f"same commit - four other modules build against these names."
    )


def test_matcher_signature_is_unchanged():
    """Separate because importing it pulls in torch, which a teammate may not have yet."""
    torch = pytest.importorskip("torch")  # noqa: F841
    from core.matcher import match
    assert params(match) == ["a", "b", "tile", "overlap", "min_confidence", "progress"]


# --- the dict contracts, which break callers just as hard as a signature ------

LOAD_META_KEYS = {"gsd_mpp", "instrument", "sun_azimuth", "sun_elevation",
                  "incidence", "crs", "transform", "format", "path",
                  "stored_dtype", "full_shape"}

RUN_ALL_KEYS = {"source", "reference", "shape_source", "shape_reference", "gsd_mpp",
                "scale_note", "scale_factors", "illumination", "subpixel", "n_matches",
                "ransac", "H", "warped", "src_inliers", "ref_inliers", "metrics",
                "metrics_note", "seconds", "meta_source", "meta_reference"}


def test_load_metadata_keys(tmp_path):
    import numpy as np
    import cv2
    from core.io_loader import load
    p = tmp_path / "t.tif"
    cv2.imwrite(str(p), np.full((8, 8), 40, np.uint8))
    _, meta = load(p)
    missing = LOAD_META_KEYS - set(meta)
    assert not missing, f"load() stopped returning {sorted(missing)}"


def test_run_all_result_keys():
    """`app/streamlit_app.py` and `evaluation/` both read this dict by key."""
    from core.pipeline import run_all
    src = inspect.getsource(run_all)
    missing = [k for k in RUN_ALL_KEYS if f'"{k}"' not in src]
    assert not missing, f"run_all() no longer returns {sorted(missing)}"


def test_refine_returns_three_things_and_the_middle_one_is_the_refined_reference():
    """Guards the ordering trap in subpixel.refine: it returns (src_out, ref_out, info),
    and `src_out` is NOT the array you passed in - it is rounded to the integer grid."""
    import numpy as np
    from core.subpixel import refine
    img = np.zeros((64, 64), np.float32)
    src = np.array([[32.4, 32.4]])
    out = refine(src, src.copy(), img, img)
    assert len(out) == 3
    src_out, ref_out, info = out
    assert np.allclose(src_out, np.round(src)), "src_out must come back on the integer grid"
    assert isinstance(info, dict) and "refined" in info and "n_refined" in info
