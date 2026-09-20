"""Turn one `core.pipeline.run_all` result into the dict the Mission Console renders.

Both paths into the console go through this single function:

    build_console.py  unpickles a cached result  -> panel()   (the frozen evidence)
    server.py         runs run_all() live        -> panel()   (a pair someone just uploaded)

That is the point of it being one function. If the live path drew its own panel, a judge could
be shown a live result rendered by different code from the frozen one, and the two could
silently disagree about what a verdict means. They cannot disagree if there is only one renderer.

Nothing here computes a registration or reads an evidence log. It converts a result to pixels
and numbers for display, and that is all it is allowed to do.
"""
from __future__ import annotations

import base64

import cv2
import numpy as np


def jpg(a, size=448, q=78):
    """A display JPEG as a data: URI, from an array or a path. None in, None out.

    Contrast is stretched to the 1st-99th percentile because raw lunar products are frequently
    16-bit with most of the range unused; without the stretch half these panels render black.
    """
    if a is None:
        return None
    if not isinstance(a, np.ndarray):
        import pathlib
        import tifffile
        if isinstance(a, (str, pathlib.Path)):
            a = tifffile.imread(str(a))
    a = np.asarray(a, dtype=np.float64)
    if a.ndim == 3:
        a = a[..., 0]
    ok = np.isfinite(a)
    lo, hi = np.percentile(a[ok], [1, 99]) if ok.any() else (0.0, 1.0)
    a = np.clip((np.nan_to_num(a, nan=lo) - lo) / max(hi - lo, 1e-9), 0, 1)
    a = cv2.resize((a * 255).astype(np.uint8), (size, size), interpolation=cv2.INTER_AREA)
    _, buf = cv2.imencode(".jpg", a, [cv2.IMWRITE_JPEG_QUALITY, q])
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


def panel(r, a_side, b_side, *, pid, label, sub, tag, plain, twin=None):
    """`r` is exactly what run_all returned. `a_side`/`b_side` describe the two inputs.

    The layer list is the part that has to be right. A contradicted pair holds TWO results:
    `warped` is what the matcher proposed and the area check threw out, `warped_final` is the
    fallback that rescued it. Showing the fallback under a REFUSED banner teaches the opposite
    of the truth, so `warped` is the layer the page opens on for a refusal, and the fallback is
    offered separately and labelled as a fallback.
    """
    rel = r["reliability"]
    g_ = lambda k: np.asarray(rel[k])
    cells = []
    for y in range(8):
        for x in range(8):
            ncc = g_("area_ncc")[y, x]
            res = g_("median_inlier_residual_px")[y, x]
            cells.append({"s": str(g_("state")[y, x]), "n": int(g_("n_inliers")[y, x]),
                          "raw": int(g_("n_raw")[y, x]),
                          "ncc": None if not np.isfinite(ncc) else round(float(ncc), 3),
                          "res": None if not np.isfinite(res) else round(float(res), 3),
                          "lir": round(float(g_("local_inlier_ratio")[y, x]), 3)})

    ok = rel["global"]["verdict"] == "agrees"
    warped, final = r.get("warped"), r.get("warped_final")
    rescued = (final is not None and warped is not None
               and not np.array_equal(np.nan_to_num(np.asarray(warped)),
                                      np.nan_to_num(np.asarray(final))))
    w_img = jpg(warped)
    layers = [{"k": "src", "n": "INPUT A, BEFORE", "img": jpg(r["source"])},
              {"k": "ref", "n": "INPUT B, REFERENCE", "img": jpg(r["reference"])}]
    if w_img is not None:
        layers.append({"k": "warp", "n": "MATCHER'S ANSWER" + ("" if ok else " · REJECTED"),
                       "img": w_img})
        layers.append({"k": "blink", "n": "BLINK vs B", "img": None})
    if rescued:
        fb = jpg(final)
        if fb is not None:
            layers.append({"k": "fb", "n": "FALLBACK, DELIVERED", "img": fb})

    return {"id": pid, "label": label, "sub": sub, "tag": tag, "plain": plain,
            "cells": cells, "ok": ok,
            "counts": {k: int(v) for k, v in rel["counts"].items()},
            "verdict": rel["global"]["verdict"], "method": r["declared"]["method"],
            "why": r["declared"]["why"], "gsd": rel["gsd_mpp"],
            "n_matches": int(r["n_matches"]), "inliers": int(r["ransac"]["inlier_count"]),
            "seconds": round(float(r["seconds"]), 1),
            "a": a_side, "b": b_side, "layers": layers, "twin": twin,
            "scale_note": (r.get("scale_factors") or {}).get("note"), "rescued": rescued}
