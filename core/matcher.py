"""
LoFTR dense matching, CPU-only and offline.

    from core.matcher import match
    src_pts, ref_pts, scores = match(img_a, img_b)

`src_pts` and `ref_pts` are (N, 2) float32 arrays of (x, y) in each image's own
pixel coordinates, same order. `scores` is (N,) float32 in [0, 1].

Four things here are not obvious. Each was measured on the real LROC NAC EDR
M108587604RE, using two overlapping 640x640 crops with a KNOWN pure translation
of (dx=24, dy=17) so that correctness is checkable rather than assumed.

1. LoFTR NEEDS [0, 1]. FEEDING RAW DN RETURNS ZERO MATCHES, SILENTLY.
   This is the most dangerous behaviour in the whole pipeline, because there is
   no exception - just an empty result that reads as "the matcher does not work
   on lunar imagery".

       input                 matches   confidence
       [0,1] normalised         5402        0.996
       raw DN [32..199]            0          nan
       per-tile min-max         5402        1.000

   `core.io_loader.load()` deliberately returns RAW DN, because the loader must
   not silently rescale science data. So the normalisation has to happen HERE,
   once, where it can be documented - not in five callers who each get it right
   or wrong on their own. Never pass raw DN to LoFTR.

   We use a fixed /255 rather than per-tile min-max. Per-tile scored marginally
   better in isolation (confidence 1.000 vs 0.996, identical match count) but it
   makes each tile's normalisation depend on its own content, so the same crater
   normalises differently depending on where the tile boundary fell. For a
   tiled matcher that is a correctness hazard, not a tuning choice.

2. KEYPOINTS ARE (x, y), NOT (row, col). Verified by sign and axis: with image1
   shifted +24 columns and +17 rows relative to image0, keypoints1 - keypoints0
   came back as (-23.99, -16.99). Had we assumed (row, col) every homography
   would have been silently transposed.

3. THE OUTPUT DICT, exactly as measured:
       keypoints0     (N, 2) torch.float32
       keypoints1     (N, 2) torch.float32
       confidence     (N,)   torch.float32
       batch_indexes  (N,)   torch.int64
   `batch_indexes` matters the moment a batch is used - it says which pair each
   match belongs to. We run batch size 1, so it is constant, but code that
   ignores it will break silently if that ever changes.

4. WE TILE, BECAUSE 1024x1024 DOES NOT FIT. Day-1 benchmarking on this laptop:
   640x640 costs ~5.5 s cold and ~7.5 s warm at ~1.8 GB peak RSS; 1024x1024
   needs ~3.6 GB of activations and is NOT VIABLE. A full NAC strip is
   1024x5064. So tiles are 640 with overlap, and every match is offset back into
   full-image coordinates. The offset bookkeeping is tested, not assumed - get it
   wrong and every coordinate is wrong by a tile origin, which still *looks*
   like a plausible registration.

The kornia mutable-default-argument bug, the weight pinning and the offline
construction are all handled in `core.bench_loftr_cpu.build_matcher`, which this
module reuses rather than reimplements. Read its docstring before changing this.
"""
from __future__ import annotations

import numpy as np
import torch

from core.bench_loftr_cpu import build_matcher

# LoFTR's coarse stage runs at 1/8 resolution, so both dimensions must be
# divisible by 8. We pad rather than crop: padding adds content that produces no
# matches, whereas cropping silently discards real image area.
STRIDE = 8

# From the Day-1 CPU benchmark. 1024 is not viable on this machine.
TILE = 640
OVERLAP = 96

_MATCHER = None


def _get_matcher():
    """Build once per process. Construction reads 46 MB from disk."""
    global _MATCHER
    if _MATCHER is None:
        _MATCHER = build_matcher(offline=True)
    return _MATCHER


def _to_tensor(img: np.ndarray) -> tuple[torch.Tensor, tuple[int, int]]:
    """(H, W) float32 raw DN -> (1, 1, H8, W8) float32 in [0, 1], plus true size.

    Normalisation and padding both live here so there is exactly one place where
    either can be wrong.
    """
    a = np.asarray(img, dtype=np.float32)
    if a.ndim != 2:
        raise ValueError(f"matcher expects a 2-D image, got shape {a.shape}")
    h, w = a.shape
    ph, pw = (-h) % STRIDE, (-w) % STRIDE
    if ph or pw:
        a = np.pad(a, ((0, ph), (0, pw)), mode="edge")
    return torch.from_numpy(np.ascontiguousarray(a / 255.0))[None, None], (h, w)


def _tiles(h: int, w: int, tile: int, overlap: int) -> list[tuple[int, int, int, int]]:
    """Top-left origins and sizes covering (h, w). Last tile is flush to the edge."""
    step = max(1, tile - overlap)
    ys = list(range(0, max(1, h - overlap), step))
    xs = list(range(0, max(1, w - overlap), step))
    out = []
    for y in ys:
        for x in xs:
            y0 = min(y, max(0, h - tile))
            x0 = min(x, max(0, w - tile))
            out.append((x0, y0, min(tile, w), min(tile, h)))
    return sorted(set(out))


def match_tile(a: np.ndarray, b: np.ndarray,
               min_confidence: float = 0.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Match two images small enough to go through LoFTR in one pass.

    Returns (pts_a, pts_b, scores) as (N, 2) float32 (x, y) and (N,) float32.
    Coordinates are relative to the images passed in.
    """
    ta, (ha, wa) = _to_tensor(a)
    tb, (hb, wb) = _to_tensor(b)
    with torch.inference_mode():
        out = _get_matcher()({"image0": ta, "image1": tb})

    k0 = out["keypoints0"].numpy().astype(np.float32)
    k1 = out["keypoints1"].numpy().astype(np.float32)
    sc = out["confidence"].numpy().astype(np.float32)
    if len(k0) == 0:
        return k0.reshape(0, 2), k1.reshape(0, 2), sc.reshape(0)

    # Discard anything the padding invented. A match landing in padded area is
    # not a real correspondence, and it sits exactly on the image border where
    # sub-pixel refinement is least reliable.
    keep = ((k0[:, 0] < wa) & (k0[:, 1] < ha) &
            (k1[:, 0] < wb) & (k1[:, 1] < hb) & (sc >= min_confidence))
    return k0[keep], k1[keep], sc[keep]


def match(a: np.ndarray, b: np.ndarray, tile: int = TILE, overlap: int = OVERLAP,
          min_confidence: float = 0.2,
          progress=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Dense-match two images of any size. Returns (src_pts, ref_pts, scores).

    Coordinates are in each input image's own full-resolution pixel space.

    `progress` is an optional callable(done, total) - the Streamlit demo narrates
    a live run rather than appearing to hang for the ~7.5 s per tile it costs.
    """
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    if max(a.shape) <= tile and max(b.shape) <= tile:
        return match_tile(a, b, min_confidence)

    # Tile over the SOURCE only, and match each source tile against the whole of
    # b when b is small enough. Tiling both sides independently would compare
    # tiles that do not overlap on the ground and waste most of the passes.
    if max(b.shape) > tile:
        raise ValueError(
            f"both images exceed the {tile} px tile ({a.shape} and {b.shape}). "
            "Crop to the overlap first with io_loader.crop_to_overlap, and "
            "resample to a common GSD with scale.to_common_gsd - matching two "
            "full strips directly is not affordable on this machine."
        )

    wins = _tiles(a.shape[0], a.shape[1], tile, overlap)
    pa, pb, ps = [], [], []
    for i, (x0, y0, tw, th) in enumerate(wins):
        sub = a[y0:y0 + th, x0:x0 + tw]
        ka, kb, sc = match_tile(sub, b, min_confidence)
        if len(ka):
            ka = ka + np.array([x0, y0], dtype=np.float32)   # back to full-image
            pa.append(ka)
            pb.append(kb)
            ps.append(sc)
        if progress is not None:
            progress(i + 1, len(wins))

    if not pa:
        return (np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32),
                np.zeros((0,), np.float32))
    return np.vstack(pa), np.vstack(pb), np.concatenate(ps)
