"""
The registration pipeline, end to end. This module IS Gate 1.

    python -m core.pipeline data/pairs/pair_01

Gate 1 (Day 5, 00_CANONICAL_FACTS.md Sec.11), verbatim: *"runs end to end on a
real lunar pair, no manual steps, prints all five metrics"*.

    load -> to_common_gsd -> illumination -> match -> RANSAC -> warp -> metrics

Five design decisions worth defending.

1. THE FIVE METRICS ARE NOT COMPUTED HERE. They come from
   `evaluation/metrics.py :: evaluate()`, which is SAMRUDH'S module (his Day 3).
   A second implementation living in `core/` would give this project two sources
   of truth for its headline accuracy number, and Invariant 1 exists because we
   already shipped an invented figure through four documents. So: we import his
   `evaluate()` if it exists, and if it does not we print the geometry we do have
   and say plainly that the metrics are unavailable. We never substitute our own.

2. `residual_px` AND `rmse_gt_px` ARE NOT INTERCHANGEABLE, and printing the wrong
   one is a fabrication rather than a bug. `rmse_gt_px` is accuracy against a
   KNOWN transform and exists only for synthetic and Tier D pairs. `residual_px`
   is a held-out fit residual and is what a real pair can honestly report. On a
   real lunar pair we have no ground truth, so `rmse_gt_px` is printed as `n/a`,
   never as a number.

3. THE HELD-OUT SPLIT BELONGS TO `evaluate()`, NOT TO US. Samrudh withholds 20%
   and fits on the remainder. Our `filter_matches` fits on everything because its
   output is the operational transform used to warp the image. Fitting a
   transform from the matches and then measuring error on those same matches is
   circular - that exact bug is recorded in Canonical Facts Sec.7.

   THEREFORE `evaluate()` GETS THE RAW MATCHER OUTPUT, NEVER `filter_matches`'
   SURVIVORS. This was wrong until 1 Sep 2026 and it silently inflated our
   headline number. Passing the post-RANSAC inliers makes `inlier_ratio` ask
   "of the points RANSAC accepted, how many does a second RANSAC accept?", whose
   answer is always about 1.0. Measured on a pair built with exactly half its
   matches deliberate garbage:

       evaluate(RAW matches)      inlier_ratio = 0.500   <- the truth
       evaluate(FILTERED inliers) inlier_ratio = 1.000   <- what we reported

   Gate 2 requires `inlier_ratio > 0.60`. We would have passed that criterion
   automatically, on a pair where half the matches were wrong. A held-out split
   cannot rescue an input that has already been filtered by a RANSAC which saw
   all of it. `src_in`/`ref_in` remain in the result dict, for warping and for
   drawing - they are the operational transform, not the measurement.

4. EVERY EXTERNAL MODULE IS AN OPTIONAL HOOK. `illumination.py` and `evaluate()`
   both existed by Day 2-3, but the guarded-import shape stays, because it is
   what let Gate 1 be built before either of them landed. `distribution.py` and
   `evaluation/logger.py` are wired the same way for the same reason.

5. THE THREE MODES ARE ONE CHAIN, NOT THREE. `--synthetic` does not get its own
   pipeline. It builds a pair with a KNOWN `H_true` and hands it to the same
   `run_all()` the Gate 1 command uses, so `rmse_gt_px` measures the real chain
   and not a parallel one written to look good. The only thing `--synthetic`
   adds is ground truth; everything downstream of `load()` is identical.

   `--log` is deliberately reachable ONLY from `main()`, never from `run_all()`.
   `evaluation/logger.py` resolves `RESULTS_LOG` from its own `__file__`, so a
   `log_result()` call inside `run_all()` would append a junk row to the real
   `evaluation/results_log.csv` on every single `pytest` run - the two contract
   tests call `run_all()` directly. Logging is a CLI action, not a library one.

The CLI argument is a DIRECTORY or a prefix, not two files, because that is what
Gate 1 specifies and what Rohan's naming produces (Sec.14):
`pair_01_source.tif` / `pair_01_ref.tif`.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys
import time

import numpy as np

from core.io_loader import load
from core.matcher import match
from core.ransac import filter_matches, warp
from core.scale import to_common_gsd, to_original

SOURCE_HINTS = ("_source", "_src", "_a")
REF_HINTS = ("_ref", "_reference", "_b")
EXTENSIONS = (".tif", ".tiff", ".IMG", ".img", ".xml", ".lbl")


def resolve_pair(target: str | pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """Turn `data/pairs/pair_01` into the two files it names.

    Accepts a directory containing exactly one source/reference pair, or a
    prefix such as `data/pairs/pair_01` matching `pair_01_source.tif` and
    `pair_01_ref.tif`. Tolerant of extension, because Rohan may deliver .tif,
    .IMG or PDS4 .xml depending on tier.
    """
    p = pathlib.Path(target)
    candidates = sorted(p.iterdir()) if p.is_dir() else sorted(
        p.parent.glob(p.name + "*"))
    files = [f for f in candidates if f.suffix in EXTENSIONS and f.is_file()]
    if not files:
        raise SystemExit(
            f"no image files found for {target!r}\n"
            f"  looked for {EXTENSIONS} in "
            f"{p if p.is_dir() else p.parent} matching {p.name!r}*"
        )

    def pick(hints):
        for f in files:
            if any(h in f.stem.lower() for h in hints):
                return f
        return None

    src, ref = pick(SOURCE_HINTS), pick(REF_HINTS)
    if src and ref:
        return src, ref
    if len(files) == 2:
        return files[0], files[1]
    raise SystemExit(
        f"could not identify a source/reference pair in {target!r}.\n"
        f"  found: {[f.name for f in files]}\n"
        f"  expected names containing {SOURCE_HINTS} and {REF_HINTS}, "
        "e.g. pair_01_source.tif / pair_01_ref.tif"
    )


def _normalise_illumination(img, meta):
    """Apply core/illumination.py, if it is there.

    Returns (image, description). Absent is a legitimate state, not an error -
    but it must be VISIBLE, because 'we normalise illumination' is a claim we
    intend to make to a judge and it must not be made before it is true.
    """
    try:
        from core.illumination import DEFAULT_METHOD, normalize
    except ImportError:
        return img, "none (core/illumination.py could not be imported)"
    # Report the METHOD, not just "applied". "We normalise illumination" is a
    # claim a judge can follow up on, and the only useful follow-up is "with
    # what?" - which the A/B in core/bench_illumination.py answers by number.
    return normalize(img), DEFAULT_METHOD


def _evaluate(ref_shape, src_pts, ref_pts, H_true=None):
    """Call Samrudh's evaluate(), or report honestly that it is unavailable."""
    try:
        from evaluation.metrics import evaluate
    except ImportError:
        return None, ("evaluation/metrics.py could not be imported "
                      "- the five metrics cannot be reported")
    return evaluate(ref_shape, src_pts, ref_pts, H_true=H_true), "ok"


def _distribution(ref_pts, ref_shape):
    """WHERE the matches are. A DIAGNOSTIC, never a metric - see the warning below.

    `core/distribution.py` deliberately refuses to return `grid_coverage_fraction`
    or `distribution_cv`; those belong to `evaluation/metrics.py`, and a module
    that both improves a number and reports it can always make itself look good.
    So this returns cell counts and weak cells, and nothing anyone quotes.

    *** `n_weak` IS NOT `1 - grid_coverage_fraction`. ***

    They count different things on different point sets, and reading one as the
    other is the easiest mistake this dict makes available:

      - `summary()` here counts cells holding fewer than MIN_PER_CELL = 2 points,
        over `ref_in` - the survivors of `filter_matches`, fitted on everything.
      - `grid_coverage_fraction` counts cells holding at least ONE point, over
        the RAW matches re-filtered inside `evaluate()` against its own held-out
        fit. Different threshold, different point set, different H.

    A run can honestly show `n_weak = 1` while coverage is exactly 1.0. Measured:
    a 15-degree synthetic pair does precisely that, cell (1, 0).

    Imported lazily. A module-scope import would make `evaluation.metrics` a HARD
    dependency of the pipeline - `distribution.py` imports GRID from it and
    re-raises - which would render `_evaluate`'s graceful-degradation branch
    unreachable and couple Gate 1 to a file we do not own.
    """
    try:
        from core.distribution import summary
    except ImportError as e:
        return None, f"core/distribution.py unavailable ({e})"
    if len(ref_pts) == 0:
        return None, "no inliers to describe"
    return summary(ref_pts, ref_shape), "diagnostic only - not the Gate 2 metric"


def _refine_subpixel(src_pts, ref_pts, a_n, b_n):
    """Optional NCC sub-pixel refinement. OFF by default, and that is a measurement.

    `core/bench_subpixel_results.csv`: NCC refinement converges on ~0.16-0.43 px
    whatever it is handed, so it helps a matcher worse than that floor and hurts
    one that is already better. LoFTR's worst case here is 0.336 px raw and
    0.431 px refined - switching this on would make our headline number worse
    while sounding like an improvement. ORB goes 0.722 -> 0.437, so it belongs on
    Gate 1's classical fallback path instead.
    """
    from core.subpixel import refine
    return refine(src_pts, ref_pts, a_n, b_n)


def run_all(src_path, ref_path, H_true=None, progress=None, subpixel=False) -> dict:
    """Register one pair. Returns a result dict; never raises on a bad pair.

    subpixel: run NCC refinement on the matches. Default False - see
        `_refine_subpixel`. Turn it on for the classical fallback, not for LoFTR.
    """
    t0 = time.perf_counter()
    a, meta_a = load(src_path)
    b, meta_b = load(ref_path)

    a_s, b_s, gsd, factors = to_common_gsd(a, meta_a, b, meta_b)
    a_n, illum = _normalise_illumination(a_s, meta_a)
    b_n, _ = _normalise_illumination(b_s, meta_b)

    src_pts, ref_pts, scores = match(a_n, b_n, progress=progress)

    # Back to ORIGINAL pixel coordinates before anything is measured or reported.
    # Metrics are defined in reference-image pixels (Sec.7); reporting them in
    # resampled pixels would silently change what the number means.
    subpixel_info = None
    if subpixel and len(src_pts):
        src_pts, ref_pts, subpixel_info = _refine_subpixel(src_pts, ref_pts, a_n, b_n)

    src_full = to_original(src_pts, factors["a"]) if len(src_pts) else src_pts
    ref_full = to_original(ref_pts, factors["b"]) if len(ref_pts) else ref_pts

    src_in, ref_in, H, info = filter_matches(src_full, ref_full)
    warped = warp(a, H, b.shape[:2]) if H is not None else None

    # RAW matches, not `src_in`/`ref_in`. See design note 3: handing `evaluate()` the
    # points RANSAC already accepted makes `inlier_ratio` measure nothing.
    metrics, metrics_note = _evaluate(b.shape[:2], src_full, ref_full, H_true)

    # AFTER the measurement, and on the inliers, so nothing `evaluate()` reports
    # can depend on it. This is a picture of where the matches landed, not a score.
    dist_info, dist_note = _distribution(ref_in, b.shape[:2])

    return {
        "source": str(src_path), "reference": str(ref_path),
        "shape_source": a.shape, "shape_reference": b.shape,
        "gsd_mpp": gsd, "scale_note": factors["note"], "scale_factors": factors,
        "illumination": illum,
        "subpixel": subpixel_info,
        "n_matches": int(len(src_pts)), "ransac": info,
        "H": H, "warped": warped,
        "src_inliers": src_in, "ref_inliers": ref_in,
        "metrics": metrics, "metrics_note": metrics_note,
        "distribution": dist_info, "distribution_note": dist_note,
        "seconds": time.perf_counter() - t0,
        "meta_source": meta_a, "meta_reference": meta_b,
    }


# --- synthetic ground truth --------------------------------------------------
#
# Gate 2's first criterion is `rmse_gt_px < 0.5 on synthetic`, and rmse_gt_px is
# the ONE metric a real lunar pair can never produce, because it needs a transform
# we already know. This is the only place in the project that manufactures one.

# __file__-rooted, not cwd-relative: every other output path in this project is
# (`evaluation/logger.py:5`, the three bench scripts), and a cwd-relative one writes
# a stray demo_cache tree wherever the operator happened to be standing.
SYNTH_DIR = pathlib.Path(__file__).resolve().parent.parent / "demo_cache" / "synthetic"
SYNTH_SUN_ELEVATION = 30.0      # fixed; see the cast-shadow warning in _synthetic_pair
SYNTH_REF_AZIMUTH = 45.0

# *** THIS SHIFT IS DELIBERATELY NOT A WHOLE NUMBER, AND THAT IS THE POINT. ***
#
# An integer translation is the one case where `cv2.warpPerspective` interpolates
# NOTHING: the warped image is a literal pixel copy of the original (measured:
# max|source - reference| == 0.0 at a zero sun difference), and the true answer then
# lands exactly on the matcher's integer query grid. rmse_gt_px measured that way is
# not evidence of sub-pixel accuracy - it is a matcher recovering an on-grid shift
# between two byte-identical arrays, and the first judge to ask "what was the true
# offset?" collapses the claim.
#
# Measured at a 30 deg sun difference, everything else held identical:
#     shift (12,   -8   )  rmse_gt_px 0.412   <- integer, on-grid, flattering
#     shift (12.5, -8.5 )  rmse_gt_px 0.806
#     shift (12.37,-8.63)  rmse_gt_px 0.931
#     shift (11,   -9   )  rmse_gt_px 1.045   <- also integer, one pixel away
#     shift (13,   -7   )  rmse_gt_px 1.281
# One shift is one sample, and picking the best one is not a measurement. Hence
# `--repeats`, which draws several off-grid shifts and reports the spread.
SYNTH_SHIFT_PX = (12.37, -8.63)


def _draw_shift(seed, rng_span=6.0, base=SYNTH_SHIFT_PX):
    """An off-grid translation for repeat `seed`. seed 0 returns `base` exactly.

    `make_pair`'s own `seed` does NOT do this: it only reaches its RNG when
    `shift_px is None`, and this module always passes one. So before `--repeats`
    existed, `--seed 0/1/2` produced three byte-identical image pairs under three
    different `pair_id`s - three rows in the results log that look like an error
    bar and are one measurement written down three times.

    The offsets are irrational-ish on purpose: a whole-pixel shift is the one case
    the warp does not interpolate. See SYNTH_SHIFT_PX.
    """
    import numpy as np
    if seed == 0:
        return tuple(float(v) for v in base)
    r = np.random.default_rng(int(seed))
    dx, dy = r.uniform(-rng_span, rng_span, 2)
    # Push off the integer grid even if the draw lands near one.
    return (float(base[0] + dx + 0.37), float(base[1] + dy - 0.63))


def _synthetic_pair(dem_path, pixel_size_m, sun_delta_deg, shift_px=SYNTH_SHIFT_PX,
                    seed=0, max_size=640, out_dir=SYNTH_DIR):
    """Render one DEM under two suns, warp by a KNOWN homography, write two files.

    Returns (src_path, ref_path, H_true, meta). `H_true` maps SOURCE pixels to
    REFERENCE pixels in (x, y) - the same direction `evaluate()` fits, which is
    why it can be differenced against our H directly.

    THREE THINGS THIS DELIBERATELY DOES NOT DO, each of which would produce a
    number that looks like a Gate 2 pass and is not one.

    1. IT DOES NOT USE `make_pair`'s DEFAULT SUNS. Those are 45 and 225 degrees -
       a 180-degree flip, which is a near-exact contrast inversion (Pearson
       -0.99), and `illumination.gradient_orientation` is BUILT to be invariant
       to exactly that. The flattering number is the default one, so the sun
       difference is always stated explicitly and always written into the row.

    2. IT DOES NOT VARY SCALE OR ROTATION, because the pair would stop being a
       controlled illumination experiment. `make_pair` warps with a FIXED output
       size (`evaluation/synthetic_data.py:52`), so a scale far from 1 does not
       change the array shape - it shrinks the OVERLAP, and the matcher then has
       less ground to work with. Measured: scale 4.0 leaves ~25% of the source
       extent matchable and rmse_gt_px rises to 0.671 on otherwise clean data.
       That is a real effect worth measuring one day, but it is a scale result
       wearing an illumination result's clothes, so the CLI does not expose it.

    3. IT DOES NOT WRITE A MAP SCALE. Untagged .tif means `load()` reports
       `gsd_mpp=None` and `to_common_gsd` takes its no-op branch, so no
       resampling happens at all. Tagging both files would NOT corrupt the frame
       - `to_original` inverts the resample exactly (measured round-trip error
       0.0 px) - it would throw away resolution for nothing, since both images
       are already on the same grid. The metres figure is passed to the logger
       from `--pixel-size` instead, which is where it is actually known.

    LIMIT, and it must be stated wherever these numbers are: `shaded_relief.py`
    is a pure local cosine law with NO cast-shadow or ray-occlusion term. Sun
    AZIMUTH sweeps move the shading and are meaningful. Sun ELEVATION sweeps only
    change brightness - a spire that should throw a 380 px shadow throws none. So
    elevation is fixed and only azimuth is varied, and this is an illumination
    test, not a shadow test.
    """
    import numpy as np
    import tifffile
    from evaluation.synthetic_data import make_pair

    dem = np.load(str(dem_path))
    if dem.ndim != 2:
        raise SystemExit(f"--dem must be a 2-D elevation array, got shape {dem.shape}")

    crop_note = ""
    if max_size and max(dem.shape) > max_size:
        dem = dem[:max_size, :max_size]
        crop_note = f", cropped to {dem.shape}"

    sun_a = (SYNTH_REF_AZIMUTH, SYNTH_SUN_ELEVATION)
    sun_b = (SYNTH_REF_AZIMUTH + float(sun_delta_deg), SYNTH_SUN_ELEVATION)
    source, reference, H_true, meta = make_pair(
        dem, pixel_size_m=pixel_size_m, sun_a=sun_a, sun_b=sun_b,
        rotation_deg=0.0, scale=1.0, shift_px=tuple(shift_px), seed=seed)

    # `render_shaded_relief` returns [0, 1]. `matcher.match` divides by 255 with no
    # range check, so on the branch where illumination normalisation is UNAVAILABLE
    # a [0,1] array reaches LoFTR as [0, 0.004] and returns zero matches silently.
    # With normalisation present the two are equivalent (gradient orientation is
    # amplitude-invariant, measured: max difference 0.0006 DN) - but the file on
    # disk should be DN-shaped anyway, so every other consumer reads it sanely.
    source = (np.asarray(source, np.float32) * 255.0).astype(np.float32)
    reference = (np.asarray(reference, np.float32) * 255.0).astype(np.float32)

    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # The stem must name every input that changes the pixels, or two different
    # configurations overwrite each other's cached .tif and log two rows that
    # cannot be told apart afterwards.
    stem = (f"synthetic_d{int(round(sun_delta_deg)):03d}"
            f"_x{shift_px[0]:+.2f}_y{shift_px[1]:+.2f}_s{seed}")
    src_path = out_dir / f"{stem}_source.tif"
    ref_path = out_dir / f"{stem}_ref.tif"
    tifffile.imwrite(str(src_path), source)      # no geo tags, on purpose - see (3)
    tifffile.imwrite(str(ref_path), reference)

    meta["pair_id"] = stem
    meta["dem"] = str(dem_path)
    meta["dem_shape"] = tuple(dem.shape)
    meta["pixel_size_m"] = float(pixel_size_m)
    meta["sun_delta_deg"] = float(sun_delta_deg)
    # Every input that moved a pixel, in the row itself. A synthetic number whose
    # illumination difference and true offset are not attached to it is not evidence.
    meta["config"] = (f"dem={pathlib.Path(dem_path).name} {tuple(dem.shape)}{crop_note}; "
                      f"d_azimuth={float(sun_delta_deg):g}deg at fixed "
                      f"{SYNTH_SUN_ELEVATION:g}deg elevation; "
                      f"shift=({shift_px[0]:+.4f},{shift_px[1]:+.4f}); "
                      f"rot=0; scale=1; seed={seed}")
    return src_path, ref_path, H_true, meta


# --- the results log ---------------------------------------------------------

def _log_preflight():
    """Refuse to write a row that `csv.DictReader` will not be able to read back.

    `evaluation/results_log.csv` is a 155-byte header with NO trailing newline, and
    `log_result` only writes a header when the file size is 0. So the first row ever
    appended fuses onto the header - one 30-field line, and DictReader then parses
    ZERO data rows. Reproduced on a copy: a 155-byte header plus one appended row
    gives one 30-field line and `csv.DictReader` then reads 0 rows.

    That file is Samrudh's, and Invariant 4 says we do not edit another owner's
    folder - so this checks and refuses rather than fixing. One newline is the whole
    repair. Returns an error string, or None when it is safe to write.
    """
    try:
        from evaluation.logger import RESULTS_LOG
    except ImportError as e:
        return f"evaluation/logger.py unavailable ({e})"
    if not RESULTS_LOG.exists() or RESULTS_LOG.stat().st_size == 0:
        return None                      # log_result writes a fresh header - fine
    with open(RESULTS_LOG, "rb") as f:
        f.seek(-1, 2)
        if f.read(1) == b"\n":
            return None
    return (
        f"REFUSING TO LOG - {RESULTS_LOG} does not end in a newline.\n"
        f"  `log_result` only writes a header when the file is empty, so the first\n"
        f"  row would fuse onto the header line and csv.DictReader would then read\n"
        f"  ZERO data rows. Every number in it would be invisible to every reader.\n"
        f"  FIX (one byte, Samrudh's file - evaluation/ is his under Invariant 4):\n"
        f"      printf '\\n' >> evaluation/results_log.csv\n"
        f"  Then re-run this command."
    )


def _log_row(pair_id, tier, method, metrics, config=None, gsd_mpp=None, notes=""):
    """Append one row to results_log.csv, then read it back and prove it parsed.

    Invariant 1: no figure may enter a slide, demo script, Q&A answer or README
    until it exists in this file. That makes a SILENTLY unreadable row worse than
    no row at all - it looks like evidence and is not. So every write is verified.
    """
    err = _log_preflight()
    if err:
        return False, err

    from evaluation.logger import RESULTS_LOG, log_result

    before = 0
    with open(RESULTS_LOG, newline="", encoding="utf-8") as f:
        before = sum(1 for _ in csv.DictReader(f))

    log_result(pair_id, tier, method, metrics, config=config,
               gsd_mpp=gsd_mpp, notes=notes)

    with open(RESULTS_LOG, newline="", encoding="utf-8") as f:
        after = sum(1 for _ in csv.DictReader(f))
    if after != before + 1:
        return False, (f"wrote a row to {RESULTS_LOG} but csv.DictReader now reads "
                       f"{after} rows, not {before + 1}. The file is malformed; "
                       f"do not quote anything from it.")
    return True, f"logged {pair_id} (tier {tier}) - {after} row(s) in {RESULTS_LOG.name}"


def _print_report(r: dict) -> None:
    print(f"\n{'='*64}\n  REGISTRATION - SIH26166\n{'='*64}")
    print(f"  source     {pathlib.Path(r['source']).name}  {r['shape_source']}"
          f"  [{r['meta_source'].get('instrument') or 'instrument not in label'}]")
    print(f"  reference  {pathlib.Path(r['reference']).name}  {r['shape_reference']}"
          f"  [{r['meta_reference'].get('instrument') or 'instrument not in label'}]")
    print(f"\n  scale         {r['scale_note']}")
    print(f"  illumination  {r['illumination']}")
    print(f"  matches       {r['n_matches']}")
    print(f"  ransac        {r['ransac']['note']}")
    print(f"  inliers       {r['ransac']['inlier_count']} "
          f"({r['ransac']['inlier_ratio']:.1%})")
    print(f"  elapsed       {r['seconds']:.1f} s")

    print(f"\n  {'-'*60}\n  THE FIVE METRICS\n  {'-'*60}")
    m = r["metrics"]
    if m is None:
        print(f"  UNAVAILABLE - {r['metrics_note']}")
        print("  No substitute is computed here on purpose: evaluation/metrics.py")
        print("  is the single source of numbers for this project.")
    else:
        gt = m.get("rmse_gt_px")
        print(f"  rmse_gt_px              {gt if gt is not None else 'n/a (no ground truth on a real pair)'}")
        for k in ("residual_px", "inlier_count", "inlier_ratio",
                  "grid_coverage_fraction", "distribution_cv"):
            v = m.get(k)
            print(f"  {k:<24}{v if v is not None else 'n/a'}")
        if r["gsd_mpp"] and m.get("residual_px") is not None:
            print(f"\n  residual_px is in REFERENCE-image pixels; at "
                  f"{r['gsd_mpp']:.4g} m/px that is "
                  f"{m['residual_px'] * r['gsd_mpp']:.3f} m on the ground.")

    d = r.get("distribution")
    if d is not None:
        print(f"\n  where the inliers landed  {d['n_cells'] - d['n_empty']}/{d['n_cells']} "
              f"cells occupied, {d['n_weak']} below {d['min_per_cell']}/cell, "
              f"busiest {d['max_in_one_cell']} in cell (row {d['busiest_cell'][0]}, "
              f"col {d['busiest_cell'][1]})")
        # Only meaningful next to the metric it is NOT. On the UNAVAILABLE branch
        # there is no grid_coverage_fraction above to contrast it with, and the
        # sentence written to prevent a confusion would be creating one.
        if m is not None:
            print(f"  ({r['distribution_note']}; grid_coverage_fraction above is the "
                  f"Gate 2 number and counts a different point set)")
        else:
            print(f"  ({r['distribution_note']})")
    print(f"{'='*64}\n")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m core.pipeline",
        description="Register one lunar image pair and print the five metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Gate 1:  python -m core.pipeline data/pairs/pair_01\n"
               "Gate 2:  python -m core.pipeline --synthetic --dem <dem.npy> "
               "--pixel-size 60 --sweep 0,15,30,45 --log")
    p.add_argument("pair", nargs="?",
                   help="pair directory or filename prefix, e.g. data/pairs/pair_01")
    p.add_argument("--synthetic", action="store_true",
                   help="build a pair with a KNOWN transform, so rmse_gt_px exists")
    p.add_argument("--dem", help="path to a .npy elevation array (required by --synthetic)")
    p.add_argument("--pixel-size", type=float, help="DEM ground sample distance, m/px")
    p.add_argument("--sun-delta", type=float, default=0.0,
                   help="sun AZIMUTH difference in degrees between the two renders")
    p.add_argument("--sweep", help="comma-separated sun deltas to run in turn, e.g. 0,15,30,45")
    p.add_argument("--shift", default=",".join(str(s) for s in SYNTH_SHIFT_PX),
                   help="known translation in px as x,y")
    p.add_argument("--repeats", type=int, default=1,
                   help="runs per delta, each at a DIFFERENT off-grid offset. One "
                        "shift is one sample: at a 30 deg sun difference rmse_gt_px "
                        "ranges 0.41-1.28 across nearby shifts, so a single run "
                        "cannot tell you whether Gate 2 passes")
    p.add_argument("--seed", type=int, default=0,
                   help="base seed for the offsets drawn by --repeats")
    p.add_argument("--max-size", type=int, default=640,
                   help="crop the DEM to this many px per side; the matcher raises "
                        "when BOTH images exceed its 640 px tile")
    p.add_argument("--subpixel", action="store_true",
                   help="NCC refinement - measured to HURT LoFTR, see _refine_subpixel")
    p.add_argument("--log", action="store_true",
                   help="append the result to evaluation/results_log.csv")
    p.add_argument("--tier", help="validation tier for the logged row; mandatory with "
                                  "--log on a real pair (Invariant 2)")
    p.add_argument("--method", default="ours_loftr", help="method name for the logged row")
    p.add_argument("--notes", default="", help="free text for the logged row")
    return p


def _progress(done, total):
    print(f"    matching tile {done}/{total}", flush=True)


def _run_one(src, ref, H_true, args, pair_id, tier, config, gsd_mpp):
    """Register one pair, print it, optionally log it.

    Returns (registered_ok, logged_ok, metrics_or_None).
    """
    r = run_all(src, ref, H_true=H_true, progress=_progress, subpixel=args.subpixel)
    _print_report(r)

    logged = True
    if args.log:
        m = r["metrics"]
        if m is None:
            print(f"  NOT LOGGED - {r['metrics_note']}")
            logged = False
        elif m.get("status") != "ok":
            # `evaluate()` returns a full-shaped dict on failure too, with
            # rmse_gt_px and residual_px as None and status 'too_few_matches' or
            # 'ransac_failed'. `log_result` does not check status - its only guard
            # is a falsy tier - so a failed registration would enter the evidence
            # file as an ordinary row with two blank cells. Blank is not zero and
            # it is not a pass; refuse, and say which pair it was.
            print(f"  NOT LOGGED - evaluate() returned status "
                  f"{m.get('status')!r}, which is a failed registration, not a "
                  f"result. Logging it would put a blank rmse_gt_px in the "
                  f"evidence file next to a pair_id that looks measured.")
            logged = False
        else:
            # A synthetic pair knows its metres from --pixel-size; a real pair only
            # from its own label, and there `run_all` is the authority.
            logged, note = _log_row(pair_id, tier, args.method, r["metrics"],
                                    config=config,
                                    gsd_mpp=gsd_mpp if gsd_mpp is not None else r["gsd_mpp"],
                                    notes=args.notes)
            print(("  " + note) if logged else f"\n{note}\n")
    return r["H"] is not None, logged, r["metrics"]


GATE2_RMSE_GT_PX = 0.5          # Canonical Facts Sec.11, Gate 2 criterion 1


def _print_sweep_summary(rows) -> None:
    """One table for the whole sweep, with the threshold applied by CODE.

    Nothing else in this repo checks a gate criterion - every one of the seven is
    currently judged by a human comparing a printed number to a markdown table,
    which is exactly how 0.796875 gets read as "about 0.8". So this prints the
    verdict rather than leaving it to the reader, and it prints the SPREAD, because
    one shift is one sample and the best of several is not a measurement.
    """
    bar = "=" * 64
    print(f"\n{bar}\n  SWEEP SUMMARY - rmse_gt_px vs sun azimuth difference\n{bar}")
    print(f"  {'d_az':>6}  {'shift (x,y)':>18}  {'rmse_gt_px':>11}   Gate 2 C1 (< "
          f"{GATE2_RMSE_GT_PX})")
    by_delta = {}
    for d, shift, m in rows:
        v = None if m is None else m.get("rmse_gt_px")
        by_delta.setdefault(d, []).append(v)
        shown = "n/a" if v is None else f"{v:.5f}"
        verdict = "  -  " if v is None else ("PASS" if v < GATE2_RMSE_GT_PX else "FAIL")
        print(f"  {d:>6g}  ({shift[0]:+8.3f},{shift[1]:+7.3f})  {shown:>11}   {verdict}")

    if any(len(v) > 1 for v in by_delta.values()):
        print(f"\n  {'d_az':>6}  {'n':>3}  {'min':>9}  {'median':>9}  {'max':>9}"
              f"   verdict")
        for d in sorted(by_delta):
            vals = sorted(v for v in by_delta[d] if v is not None)
            if not vals:
                continue
            mid = len(vals) // 2
            med = vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2
            # The MEDIAN decides, not the minimum. Reporting the best of several
            # shifts is picking the luckiest draw and calling it accuracy.
            print(f"  {d:>6g}  {len(vals):>3}  {vals[0]:>9.5f}  {med:>9.5f}  "
                  f"{vals[-1]:>9.5f}   "
                  f"{'PASS' if med < GATE2_RMSE_GT_PX else 'FAIL'} on the median")
    print(f"{bar}\n")


def main(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv[1:])

    if not args.pair and not args.synthetic:
        parser.print_help()
        return 2

    # EVERY refusal that can be decided from the arguments alone is decided HERE,
    # before a single second of matching. A full four-delta sweep is minutes of
    # LoFTR; discovering afterwards that the row cannot be written wastes all of it.
    if args.log:
        if not args.synthetic and not args.tier:
            print("--log needs --tier on a real pair. `log_result` rejects a missing "
                  "tier,\nand a number without its validation tier is not evidence "
                  "(Invariant 2).")
            return 2
        err = _log_preflight()
        if err:
            print(f"\n{err}\n")
            return 3

    # --- synthetic: the only mode that can produce rmse_gt_px -----------------
    if args.synthetic:
        if not args.dem or args.pixel_size is None:
            print("--synthetic needs --dem <file.npy> and --pixel-size <m/px>")
            return 2
        if args.pixel_size <= 0:
            # Reaches np.gradient(dem, 0.0) and renders an all-NaN image in silence.
            print(f"--pixel-size must be positive, got {args.pixel_size}")
            return 2
        if args.repeats < 1:
            print(f"--repeats must be at least 1, got {args.repeats}")
            return 2
        try:
            sx, sy = (float(v) for v in args.shift.split(","))
        except ValueError:
            print(f"--shift must be two numbers 'x,y', got {args.shift!r}")
            return 2

        try:
            # `is not None`, not truthiness: --sweep "" is falsy and used to fall
            # through to [0.0] - the single most flattering point - run silently
            # under the operator's belief that they had asked for a sweep.
            deltas = ([float(d) for d in args.sweep.split(",") if d.strip()]
                      if args.sweep is not None else [float(args.sun_delta)])
        except ValueError:
            print(f"--sweep must be comma-separated numbers, got {args.sweep!r}")
            return 2
        if not deltas:
            # An empty --sweep used to fall through to [0.0] - the single most
            # flattering point, run silently under the operator's assumption
            # that they had asked for a sweep.
            print(f"--sweep parsed to no values from {args.sweep!r}")
            return 2

        # Said once, out loud, before any number is printed. A synthetic result
        # whose illumination difference is not stated is not interpretable, and
        # the flattering values (0 degrees, and 180 degrees) are the easy ones to
        # reach for by accident.
        print(f"\n  SYNTHETIC GROUND TRUTH - sun azimuth difference(s) "
              f"{', '.join(f'{d:g}' for d in deltas)} deg, elevation fixed at "
              f"{SYNTH_SUN_ELEVATION:g} deg.")
        print("  Shaded relief has NO cast-shadow term, so this varies illumination")
        print("  DIRECTION, not shadow geometry. rmse_gt_px below is true accuracy")
        print("  against a known transform - it is NOT comparable to residual_px.")
        if args.repeats > 1:
            print(f"  {args.repeats} repeats per delta, each at a DIFFERENT off-grid")
            print("  offset. One shift is one sample; the spread is the result.")

        ok_all = logged_all = True
        summary_rows = []
        for d in deltas:
            for rep in range(args.repeats):
                # rep 0 uses the shift the operator asked for; later repeats draw
                # their own, so the spread comes from the geometry and not from
                # `make_pair`'s seed, which does nothing once a shift is passed.
                shift = (sx, sy) if rep == 0 else _draw_shift(args.seed + rep)
                src, ref, H_true, meta = _synthetic_pair(
                    args.dem, args.pixel_size, d, shift_px=shift,
                    seed=args.seed + rep, max_size=args.max_size)
                ok, logged, m = _run_one(src, ref, H_true, args,
                                         pair_id=meta["pair_id"],
                                         tier=args.tier or "synthetic",
                                         config=meta["config"],
                                         gsd_mpp=args.pixel_size)
                ok_all, logged_all = ok_all and ok, logged_all and logged
                summary_rows.append((d, shift, m))

        if len(summary_rows) > 1:
            _print_sweep_summary(summary_rows)
        return 0 if (ok_all and logged_all) else (1 if not ok_all else 3)

    # --- a real pair ----------------------------------------------------------
    src, ref = resolve_pair(args.pair)
    ok, logged, _ = _run_one(src, ref, None, args,
                             pair_id=pathlib.Path(args.pair).name,
                             tier=args.tier, config=None,
                             gsd_mpp=None)
    # Exit non-zero when there is no usable registration, so an unattended run
    # (Gate 1, Rohan's catalogue loop) can tell success from a printed apology.
    # Exit 3 means it registered but the row could not be recorded.
    return 0 if (ok and logged) else (1 if not ok else 3)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
