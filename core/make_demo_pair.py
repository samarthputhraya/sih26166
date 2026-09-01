"""
Cut a registration pair out of one real lunar strip.

    python -m core.make_demo_pair <label> <out_dir> [--x0 N --y0 N --dx N --dy N]

WHAT KIND OF PAIR THIS IS - READ BEFORE QUOTING ANYTHING FROM IT
---------------------------------------------------------------
Two crops of the SAME frame at an INTEGER pixel offset. The overlapping pixels
are therefore bit-identical: no resampling, no sub-pixel shift, no rotation, no
scale change, and - because it is one exposure - no illumination difference at
all. This is the easiest possible case that still uses real lunar texture.

It is NOT any tier of the validation ladder in Canonical Facts Sec.2. It is not
cross-sensor, not cross-illumination, not multi-modal. Its only jobs are:

  1. Give Gate 1 a REAL lunar pair to run end to end on, which is its literal
     criterion, and
  2. Provide a known-answer fixture: because the offset is exact and integer,
     any recovered shift that is not (-dx, -dy) is our error and nothing else.

The moment Rohan delivers a Tier A pair, THAT is what the accuracy claim rests
on. Numbers from this fixture belong in results_log.csv labelled `same-frame
offset crop`, and nowhere near a slide that says "sub-pixel accuracy".

WHY IT EXISTS
-------------
The previous `data/pairs/pair_01` was a synthetic dry-run fixture written an
hour before any real data was downloaded - its reference tile had 15 distinct
grey levels and its source tile held negative values, so the two were not even
crops of one image. The pipeline still reported a 100% inlier ratio on it, which
is exactly the kind of flattering number this project has already been burned
by once.
"""
from __future__ import annotations

import pathlib
import sys

import cv2
import numpy as np

from core.io_loader import load

TILE = 640
DEFAULT_DX, DEFAULT_DY = 40, 25


def make_pair(label: str | pathlib.Path, out_dir: str | pathlib.Path,
              x0: int, y0: int, dx: int = DEFAULT_DX, dy: int = DEFAULT_DY,
              tile: int = TILE) -> tuple[pathlib.Path, pathlib.Path]:
    """Write pair_XX_source.tif / pair_XX_ref.tif. Returns the two paths.

    The reference is taken `dx` right and `dy` down of the source, so a feature
    at (px, py) in the source sits at (px - dx, py - dy) in the reference. A
    correct registration therefore recovers a translation of (-dx, -dy).
    """
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = out_dir.name

    src, meta = load(label, window=(x0, y0, tile, tile))
    ref, _ = load(label, window=(x0 + dx, y0 + dy, tile, tile))

    # Write back at the product's OWN stored dtype. load() hands back raw DN as
    # float32 regardless of storage, so writing what it returns would persist an
    # 8-bit product as 32-bit floats - inventing precision that was never in the
    # data, and quadrupling a file that six people have to sync. The cast is
    # lossless here and asserted to be.
    stored = np.dtype(meta.get("stored_dtype", "uint8"))
    for arr in (src, ref):
        back = arr.astype(stored)
        if not np.array_equal(back.astype(np.float32), arr):
            raise SystemExit(
                f"casting DN back to {stored} would lose data - the label says "
                f"{stored} but the values do not fit it."
            )
    src = src.astype(stored)
    ref = ref.astype(stored)

    p_src = out_dir / f"{name}_source.tif"
    p_ref = out_dir / f"{name}_ref.tif"
    for path, arr in ((p_src, src), (p_ref, ref)):
        if not cv2.imwrite(str(path), arr):
            raise SystemExit(f"cv2.imwrite failed for {path}")

    readme = out_dir / "PROVENANCE.md"
    readme.write_text(
        f"# {name}\n\n"
        f"Two {tile}x{tile} crops of ONE real lunar frame at an integer offset.\n\n"
        f"| field | value |\n|---|---|\n"
        f"| product | `{pathlib.Path(label).name}` |\n"
        f"| instrument | {meta.get('instrument')} |\n"
        f"| gsd_mpp | {meta.get('gsd_mpp')} |\n"
        f"| source window (x, y, w, h) | ({x0}, {y0}, {tile}, {tile}) |\n"
        f"| reference window (x, y, w, h) | ({x0 + dx}, {y0 + dy}, {tile}, {tile}) |\n"
        f"| known offset (dx, dy) | ({dx}, {dy}) |\n"
        f"| expected recovered translation | ({-dx}, {-dy}) |\n\n"
        "**Not a validation tier.** Same frame, same exposure, integer offset - "
        "so identical pixels and no illumination difference. Gate-1 wiring "
        "fixture and known-answer check only. See the module docstring of "
        "`core/make_demo_pair.py`.\n",
        encoding="utf-8",
    )
    return p_src, p_ref


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    kw = {}
    for key in ("x0", "y0", "dx", "dy"):
        flag = f"--{key}"
        if flag in argv:
            kw[key] = int(argv[argv.index(flag) + 1])
    kw.setdefault("x0", 2000)
    kw.setdefault("y0", 64000)

    p_src, p_ref = make_pair(argv[1], argv[2], **kw)
    for p in (p_src, p_ref):
        a, _ = load(p)
        print(f"  {p}  {a.shape} {a.dtype}  DN [{a.min()}, {a.max()}]  "
              f"std {a.std():.2f}")
    print(f"  provenance -> {pathlib.Path(argv[2]) / 'PROVENANCE.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
