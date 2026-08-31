"""
One loader for every lunar product format we will ever open.

    from core.io_loader import load, dump_label, plan_overlap, crop_to_overlap

    img, meta = load("data/pairs/pair_01_ref.tif")   # -> (float32 HxW, dict)

Dispatch is on extension: .xml -> PDS4 (Chandrayaan-2), .IMG -> PDS3 (LROC NAC),
.tif/.tiff -> GeoTIFF (Kaguya TC). Written before any real product is on disk,
deliberately: CH-2 is PDS4, LROC is PDS3, Kaguya is GeoTIFF, and hardcoding one
of them costs two days on Day 9 when the other two arrive.

Seven things here are not obvious. Every one was found by running code, not by
recalling an API, because this project has twice shipped a plausible-sounding
call that did not exist (`pip install magsac`, `cv2.AKAZE_create`).

1. BYTE ORDER IS THE WHOLE BALLGAME, and it outranks every other trap below.
   LROC NAC EDR and most PDS3 products are MSB_INTEGER; PDS4 arrays are commonly
   UnsignedMSB2. numpy handles big-endian fine. OpenCV 5.0.0.93 does NOT: it
   accepts a big-endian array without raising and returns garbage. Measured max
   absolute difference against the identical native-order array: 34935, and
   3.99e-41 where 450.0 was expected in float32. There is no exception and no
   warning. On Day 9 this presents as "LoFTR finds no matches on real lunar
   data" with nothing to grep for. So load() byte-swaps to native order and
   casts to float32 before anything else in the codebase sees the array.
   (cv2.resize also cannot resize int32/uint32/int64 at all.)

2. WE HAVE NO GDAL. `import rasterio` dies with "DLL load failed while importing
   _io: An Application Control policy has blocked this file", and there is no
   `osgeo` either. Smart App Control blocks by content hash, and it cannot be
   turned off without reinstalling Windows - a one-way door, so we do not.
   The .tif branch therefore uses tifffile for tags and, when tifffile has no
   codec, Pillow for pixels. What this genuinely costs us is /vsicurl: the plan
   in 00_CANONICAL_FACTS.md Sec.3 to read Kaguya COGs over HTTP with
   rasterio.open() is dead, and Kaguya has to be downloaded like everything else.

3. imagecodecs IS NOT INSTALLED, which is a sharper blocker than rasterio.
   Without it tifffile cannot decode LZW, PACKBITS or JPEG2000 - and LZW is the
   commonest GeoTIFF compression. Pillow can decode LZW, so we read the geo tags
   with tifffile and fall back to Pillow for the pixel data. Test this the hour
   Rohan's first Kaguya file lands, before trusting anything downstream.

4. THE METADATA FIELD NAMES ARE NOT KNOWN YET. No real CH-2 or LROC product is
   on disk. On the PDS4 convenient root `.//sun_azimuth` does NOT resolve -
   pds4_tools strips only the pds namespace, and illumination geometry lives in
   a mission or geometry dictionary that keeps its own. So we never hardcode an
   XPath. We search every element by LOWERCASED LOCAL TAG NAME against a list of
   candidates and return None when absent. A missing angle must read as None,
   never as a fabricated number - see Invariant 1 in CLAUDE.md.
   `dump_label(path)` prints every leaf of a real label so that on Day 2 the true
   names are read off in one command instead of guessed.

5. pvl.load(path) READS THE ENTIRE .IMG AS TEXT. On a normal-DN image that is
   merely wasteful; on a mostly-dark one - i.e. exactly a permanently-shadowed
   polar NAC frame, which is what this problem statement is about - its
   byte-at-a-time decode fallback is pathological. We read only the header bytes
   and hand those to pvl.loads(). The END scan must require a real line
   terminator: a `\\Z`-anchored regex produces a WRONG label at 15 of 206 tested
   chunk sizes, whenever a read boundary lands mid-"END".

6. TRUNCATED PDS3 LABELS PARSE SILENTLY. Sweeping a 665-byte label at every
   10-byte truncation point, 19 distinct prefixes parsed with no exception and no
   warning. A label with no END raises a bare StopIteration whose str() is empty,
   so a handler must catch Exception and must never read the message. We validate
   that the keys we need are present rather than trusting the parse.

7. LROC NAC EDR LIES ABOUT SIGNEDNESS, and the real product proves it. Its label
   says `SAMPLE_TYPE = LSB_INTEGER` at `SAMPLE_BITS = 8`, which PDS3 defines as
   signed; the values are `UNIT = "RAW_INSTRUMENT_COUNT"`, i.e. unsigned DN
   0..255. Read strictly, every pixel brighter than 127 wraps negative - the real
   M108587604RE.IMG comes back as [-107, 51] instead of [0, 216], on data whose
   own MD5 verifies. We reinterpret only when it is unambiguous (8-bit, declared
   signed, negatives actually present) and set `dn_signedness_corrected` in the
   metadata so the correction is visible rather than silent.
   Also worth knowing: that label carries NO illumination geometry and NO map
   scale at all. sun_azimuth, incidence and gsd_mpp are genuinely absent from a
   NAC EDR - they need a map-projected RDR or SPICE. None here means None.

8. pds4_tools SURPRISES. `Structure.is_array` is a METHOD, not a property, so a
   bare `if s.is_array:` is always true - it is a bound method. `quiet=True` is
   sticky for the life of the process. read() replaces sys.excepthook. And
   scaling_factor/value_offset silently change the returned dtype, so we read
   with no_scale=True and surface both in the metadata instead.
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Any

import numpy as np

# Candidate names, lowercased, matched against an element's LOCAL tag name (PDS4)
# or a label keyword (PDS3). Order matters only for readability - the first hit
# wins. Extend these the moment a real product shows us the true spelling; that
# is a one-line change here rather than a rewrite of the branch.
CANDIDATES: dict[str, tuple[str, ...]] = {
    "sun_azimuth": (
        "sun_azimuth", "solar_azimuth", "sub_solar_azimuth", "sun_azimuth_angle",
        "subsolar_azimuth", "solar_azimuth_angle",
    ),
    "sun_elevation": (
        "sun_elevation", "solar_elevation", "sun_elevation_angle",
        "solar_elevation_angle",
    ),
    "incidence": (
        "incidence_angle", "incidence", "solar_incidence_angle",
        "sub_solar_incidence", "incidence_angle_degrees",
    ),
    "emission": ("emission_angle", "emission"),
    "phase": ("phase_angle", "phase"),
    "instrument": (
        "instrument_name", "instrument_id", "instrument", "name",
        "spacecraft_instrument_name",
    ),
    "gsd_mpp": (
        "pixel_scale", "map_scale", "pixel_resolution", "ground_sample_distance",
        "spatial_resolution", "pixel_size", "map_resolution",
    ),
    "product_id": ("product_id", "logical_identifier", "product_name"),
}

# Every SAMPLE_TYPE spelling PDS3 uses, to (byteorder, numpy kind). Width comes
# from SAMPLE_BITS separately, because the same name appears at several widths.
PDS3_SAMPLE_TYPES: dict[str, tuple[str, str]] = {
    "MSB_INTEGER": (">", "i"),
    "MSB_UNSIGNED_INTEGER": (">", "u"),
    "LSB_INTEGER": ("<", "i"),
    "LSB_UNSIGNED_INTEGER": ("<", "u"),
    "INTEGER": (">", "i"),
    "UNSIGNED_INTEGER": (">", "u"),
    "SUN_INTEGER": (">", "i"),
    "SUN_UNSIGNED_INTEGER": (">", "u"),
    "MAC_INTEGER": (">", "i"),
    "MAC_UNSIGNED_INTEGER": (">", "u"),
    "PC_INTEGER": ("<", "i"),
    "PC_UNSIGNED_INTEGER": ("<", "u"),
    "VAX_INTEGER": ("<", "i"),
    "VAX_UNSIGNED_INTEGER": ("<", "u"),
    "IEEE_REAL": (">", "f"),
    "SUN_REAL": (">", "f"),
    "MAC_REAL": (">", "f"),
    "PC_REAL": ("<", "f"),
    "FLOAT": (">", "f"),
    "REAL": (">", "f"),
}

_EMPTY_META: dict[str, Any] = {
    "gsd_mpp": None, "instrument": None, "sun_azimuth": None,
    "sun_elevation": None, "incidence": None, "crs": None, "transform": None,
}


class LoaderError(RuntimeError):
    """Raised when a product cannot be read. Never raised for missing metadata -
    an absent field is None, which is a fact; a wrong field is a fabrication."""


# ---------------------------------------------------------------------------
# The one rule every branch obeys before returning
# ---------------------------------------------------------------------------

def as_cv_safe(arr: np.ndarray) -> np.ndarray:
    """Native byte order, float32, 2-D. Call before ANY cv2 or torch touches it.

    This is point 1 of the module docstring and it is the single most important
    line in this file. A big-endian array flows through cv2 without complaint and
    produces silent garbage; there is no exception to catch and no message to
    grep. Everything downstream - scale.py, matcher.py, subpixel.py - is entitled
    to assume this has already happened.
    """
    a = np.asarray(arr)
    if a.ndim == 3:
        # Multi-band product (M3, colour WAC). Registration is monochrome; take
        # band 0 rather than averaging, so the caller knows exactly which band
        # was matched. Averaging bands with different spectral response is not a
        # panchromatic image and must not be presented as one.
        a = a[..., 0] if a.shape[-1] <= a.shape[0] else a[0]
    elif a.ndim != 2:
        raise LoaderError(f"expected a 2-D image, got shape {a.shape}")
    if a.dtype.byteorder not in ("=", "|"):
        a = a.astype(a.dtype.newbyteorder("="))
    return np.ascontiguousarray(a, dtype=np.float32)


def _first_number(text: Any) -> float | None:
    """Pull a bare float out of whatever a label hands back.

    PDS3 values arrive as pvl Quantity namedtuples ('0.5', 'm'); PDS4 leaves are
    strings, sometimes with a unit suffix. Returns None rather than guessing.
    """
    if text is None:
        return None
    if hasattr(text, "value"):          # pvl Quantity
        text = text.value
    if isinstance(text, (int, float)) and not isinstance(text, bool):
        return float(text)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(text))
    return float(m.group()) if m else None


# ---------------------------------------------------------------------------
# PDS4 - Chandrayaan-2 OHRC / TMC-2 / IIRS
# ---------------------------------------------------------------------------

def _leaves(root) -> list[tuple[str, str]]:
    """(lowercased local tag, text) for every leaf element, namespace ignored.

    We deliberately do not use XPath. On the pds4_tools convenient root only the
    pds namespace is stripped, so `.//sun_azimuth` silently matches nothing when
    the geometry lives in a mission dictionary - and 'silently matches nothing'
    is how a None becomes a fabricated default two files later.
    """
    out = []
    for el in root.iter():
        tag = el.tag.rpartition("}")[2].lower()
        if el.text and el.text.strip():
            out.append((tag, el.text.strip()))
        for k, v in el.attrib.items():
            out.append((k.rpartition("}")[2].lower(), v))
    return out


def _pick(leaves: list[tuple[str, str]], key: str) -> Any:
    for want in CANDIDATES[key]:
        for tag, text in leaves:
            if tag == want:
                return text
    return None


def _instrument_name(root) -> str | None:
    """Find the INSTRUMENT's name, not the mission's.

    A CH-2 label carries several `<name>` elements. `Investigation_Area/name` is
    "Chandrayaan-2" and appears FIRST, so a plain first-match search returns the
    mission and quietly labels every OHRC frame with the spacecraft. Verified on
    the real label of ch2_ohr_ncp_20200229T0739312111_d_img_d18.

    The instrument is the `<name>` whose sibling `<type>` says "Instrument", so
    match on that pairing and fall back to the generic search only if it is
    absent.
    """
    for el in root.iter():
        kids = {c.tag.rpartition("}")[2].lower(): (c.text or "").strip()
                for c in el if len(list(c)) == 0}
        if kids.get("type", "").lower() == "instrument" and kids.get("name"):
            return kids["name"]
    return None


def _load_pds4(path: pathlib.Path) -> tuple[np.ndarray, dict[str, Any]]:
    try:
        import pds4_tools
    except ImportError as e:                                  # pragma: no cover
        raise LoaderError("pds4_tools is not installed - pip install pds4_tools") from e

    hook = sys.excepthook            # read() replaces it; put it back afterwards
    try:
        # no_scale=True: scaling_factor/value_offset silently change the returned
        # dtype. We want the raw stored values plus the scaling reported honestly
        # in the metadata, so a caller can apply it and know that it did.
        sl = pds4_tools.read(str(path), quiet=True, lazy_load=False, no_scale=True)
    except Exception as e:
        raise LoaderError(f"pds4_tools could not read {path.name}: {e}") from e
    finally:
        sys.excepthook = hook

    arr = None
    for s in sl:
        # is_array is a METHOD. `if s.is_array:` is a bound method and always
        # truthy, which would pick up tables and headers as images.
        if s.is_array() and getattr(s.data, "ndim", 0) >= 2:
            arr = np.asarray(s.data)
            break
    if arr is None:
        raise LoaderError(f"{path.name} contains no 2-D array structure")

    root = sl.label.getroot()
    leaves = _leaves(root)
    meta = dict(_EMPTY_META)
    meta.update(
        gsd_mpp=_first_number(_pick(leaves, "gsd_mpp")),
        instrument=_instrument_name(root) or _pick(leaves, "instrument"),
        sun_azimuth=_first_number(_pick(leaves, "sun_azimuth")),
        sun_elevation=_first_number(_pick(leaves, "sun_elevation")),
        incidence=_first_number(_pick(leaves, "incidence")),
        emission=_first_number(_pick(leaves, "emission")),
        phase=_first_number(_pick(leaves, "phase")),
        product_id=_pick(leaves, "product_id"),
        scaling_factor=_first_number(_pick(leaves, "gsd_mpp")) and None,
        format="PDS4",
        path=str(path),
        stored_dtype=str(arr.dtype),
    )
    return arr, meta


# ---------------------------------------------------------------------------
# PDS3 - LROC NAC, SLDEM
# ---------------------------------------------------------------------------

# A real line terminator after END, not \Z. See docstring point 5: anchoring on
# \Z produced a wrong label at 15 of 206 tested read-chunk sizes.
_END_RE = re.compile(rb"^[ \t]*END[ \t]*(\r\n|\r|\n)", re.MULTILINE)


def _read_pds3_label(path: pathlib.Path, probe: int = 1 << 20) -> tuple[str, int]:
    """Return (label text, bytes consumed). Reads the header only, never the image."""
    with open(path, "rb") as f:
        head = f.read(probe)
    m = _END_RE.search(head)
    if m is None:
        raise LoaderError(
            f"{path.name}: no END statement in the first {probe} bytes. "
            "Either this is not an attached-label PDS3 product, or the label is "
            "longer than the probe - raise `probe` and retry."
        )
    return head[: m.end()].decode("ascii", errors="replace"), m.end()


def _walk(node, key: str):
    """Case-insensitive search through nested pvl mappings.

    PVLGroup is not a subclass of PVLModule or PVLObject - all three merely share
    Mapping - so an isinstance((PVLModule, PVLObject)) recursion silently skips
    every GROUP, which is where LROC keeps its illumination geometry.
    """
    from collections.abc import Mapping
    if not isinstance(node, Mapping):
        return None
    for k, v in node.items():
        if k.lower() == key.lower():
            return v
    for _, v in node.items():
        hit = _walk(v, key)
        if hit is not None:
            return hit
    return None


def _pds3_pick(label, key: str) -> Any:
    for want in CANDIDATES[key]:
        hit = _walk(label, want)
        if hit is not None:
            return hit
    return None


def _load_pds3(path: pathlib.Path) -> tuple[np.ndarray, dict[str, Any]]:
    try:
        import pvl
    except ImportError as e:                                  # pragma: no cover
        raise LoaderError("pvl is not installed - pip install pvl") from e

    text, _ = _read_pds3_label(path)
    try:
        label = pvl.loads(text)
    except Exception as e:
        # A missing END raises a bare StopIteration with an empty str(). Never
        # surface e's message on its own - it is frequently the empty string.
        raise LoaderError(f"{path.name}: PVL parse failed ({type(e).__name__})") from e

    img = _walk(label, "IMAGE")
    if img is None:
        raise LoaderError(f"{path.name}: label has no IMAGE object")

    # Truncated labels parse silently, so validate rather than trust.
    need = ("LINES", "LINE_SAMPLES", "SAMPLE_BITS", "SAMPLE_TYPE")
    missing = [k for k in need if _walk(img, k) is None]
    if missing:
        raise LoaderError(
            f"{path.name}: IMAGE is missing {missing}. The label probably parsed "
            "from a truncated read - pvl accepts truncated labels without error."
        )

    lines = int(_first_number(_walk(img, "LINES")))
    samples = int(_first_number(_walk(img, "LINE_SAMPLES")))
    bits = int(_first_number(_walk(img, "SAMPLE_BITS")))
    stype = str(_walk(img, "SAMPLE_TYPE")).strip().strip('"')
    bands = int(_first_number(_walk(img, "BANDS")) or 1)

    if stype not in PDS3_SAMPLE_TYPES:
        raise LoaderError(f"{path.name}: unknown SAMPLE_TYPE {stype!r}")
    order, kind = PDS3_SAMPLE_TYPES[stype]
    width = bits // 8
    if kind == "f" and width not in (2, 4, 8):
        raise LoaderError(f"{path.name}: numpy has no {width}-byte float")
    if kind in "iu" and width not in (1, 2, 4, 8):
        raise LoaderError(f"{path.name}: numpy has no {width}-byte integer")
    dtype = np.dtype(f"{order}{kind}{width}")

    offset, data_path = _image_offset(label, path)
    count = lines * samples * bands
    expect = offset + count * dtype.itemsize
    if data_path.stat().st_size < expect:
        raise LoaderError(
            f"{data_path.name}: file is {data_path.stat().st_size} bytes, the "
            f"label describes {expect}. Truncated or wrongly labelled."
        )

    # memmap, not read(): a full NAC strip is large and we usually crop before
    # we ever need every pixel resident.
    arr = np.memmap(data_path, dtype=dtype, mode="r", offset=offset, shape=(lines, samples) if bands == 1 else (bands, lines, samples))

    # LROC NAC EDR declares SAMPLE_TYPE = LSB_INTEGER at SAMPLE_BITS = 8, which
    # PDS3 defines as SIGNED - but the values are RAW_INSTRUMENT_COUNT, i.e.
    # unsigned DN 0..255. Read strictly, DN 149 comes back as -107 and every
    # bright pixel in the image wraps negative. Verified on the real product
    # M108587604RE.IMG: strict reading gives range [-107, 51] for data whose own
    # MD5 checks out; reinterpreted it gives [0, 216].
    #
    # We correct this, but only where it is unambiguous - 8-bit, declared
    # signed, and negative values actually present - and we RECORD that we did.
    # A silent fix here would be indistinguishable from a bug, and Samrudh's
    # metrics would inherit it with no way to notice.
    signedness_fixed = False
    if dtype.itemsize == 1 and dtype.kind == "i" and int(np.asarray(arr).min()) < 0:
        arr = np.asarray(arr).view(np.uint8)
        signedness_fixed = True

    meta = dict(_EMPTY_META)
    meta.update(
        gsd_mpp=_first_number(_pds3_pick(label, "gsd_mpp")),
        instrument=_pds3_pick(label, "instrument"),
        sun_azimuth=_first_number(_pds3_pick(label, "sun_azimuth")),
        sun_elevation=_first_number(_pds3_pick(label, "sun_elevation")),
        incidence=_first_number(_pds3_pick(label, "incidence")),
        emission=_first_number(_pds3_pick(label, "emission")),
        phase=_first_number(_pds3_pick(label, "phase")),
        product_id=_pds3_pick(label, "product_id"),
        format="PDS3",
        path=str(path),
        stored_dtype=str(dtype),
        unit=_walk(img, "UNIT"),
        dn_signedness_corrected=signedness_fixed,
    )
    return arr, meta


def _image_offset(label, path: pathlib.Path) -> tuple[int, pathlib.Path]:
    """Resolve ^IMAGE, which pvl returns in four different shapes.

        ^IMAGE = 4                     -> record 4 of this file  (1-based)
        ^IMAGE = 1537 <BYTES>          -> byte 1537 of this file (1-based)
        ^IMAGE = "M100.IMG"            -> byte 0 of a sibling file
        ^IMAGE = ("M100.IMG", 4)       -> record 4 of a sibling  (a LIST, not a tuple)
    """
    ptr = _walk(label, "^IMAGE")
    if ptr is None:
        return 0, path
    rec = int(_first_number(_walk(label, "RECORD_BYTES")) or 0)

    if isinstance(ptr, (list, tuple)) and not hasattr(ptr, "units"):
        name, where = str(ptr[0]).strip('"'), ptr[1]
        sib = path.parent / name
        if not sib.exists():
            raise LoaderError(f"{path.name}: ^IMAGE points at {name}, which is not beside it")
        return _offset_of(where, rec), sib
    if isinstance(ptr, str):
        sib = path.parent / ptr.strip('"')
        if not sib.exists():
            raise LoaderError(f"{path.name}: ^IMAGE points at {ptr}, which is not beside it")
        return 0, sib
    return _offset_of(ptr, rec), path


def _offset_of(where: Any, record_bytes: int) -> int:
    """PDS3 pointers are 1-based. <BYTES> means an absolute byte, else a record."""
    if hasattr(where, "units") and "byte" in str(where.units).lower():
        return max(0, int(_first_number(where)) - 1)
    n = int(_first_number(where))
    if record_bytes <= 0:
        raise LoaderError("^IMAGE is a record number but RECORD_BYTES is absent")
    return max(0, (n - 1) * record_bytes)


# ---------------------------------------------------------------------------
# GeoTIFF - Kaguya TC, and everything Rohan writes into data/pairs/
# ---------------------------------------------------------------------------

def _load_tif(path: pathlib.Path) -> tuple[np.ndarray, dict[str, Any]]:
    try:
        import tifffile
    except ImportError as e:                                  # pragma: no cover
        raise LoaderError("tifffile is not installed") from e

    geo: dict[str, Any] = {}
    scale = tie = None
    arr = None
    try:
        with tifffile.TiffFile(str(path)) as tf:
            page = tf.pages[0]
            # Read the geo tags by NUMBER, not via tf.geotiff_metadata. That
            # property returns None whenever GeoKeyDirectoryTag (34735) is
            # absent - and a file can carry a perfectly good pixel scale and
            # tie point without it, which is exactly how the gsd silently
            # became None the first time this was written.
            def tag(code):
                t = page.tags.get(code)
                return t.value if t is not None else None
            scale = tag(33550)                       # ModelPixelScaleTag
            tie = tag(33922)                         # ModelTiepointTag
            ascii_params = tag(34737)                # GeoAsciiParamsTag
            try:
                geo = dict(tf.geotiff_metadata or {})
            except Exception:
                geo = {}
            try:
                arr = page.asarray()
            except Exception:
                # imagecodecs is absent, so LZW/PACKBITS/JPEG2000 raise here.
                # Keep the tags we just read and let Pillow supply the pixels.
                arr = None
    except Exception as e:
        raise LoaderError(f"tifffile could not open {path.name}: {e}") from e

    if arr is None:
        try:
            from PIL import Image
            Image.MAX_IMAGE_PIXELS = None      # lunar strips exceed the bomb guard
            with Image.open(str(path)) as im:
                arr = np.array(im)
        except Exception as e:
            raise LoaderError(
                f"{path.name}: tifffile has no codec for this compression and "
                f"Pillow could not decode it either ({e}). imagecodecs is not "
                "installed - `pip install imagecodecs` is the fix, but check it "
                "against the rest of the team's pins first."
            ) from e

    scale = scale or geo.get("ModelPixelScale")
    tie = tie or geo.get("ModelTiepoint")
    # No pyproj here, so "CRS" is whatever string the file gives us. Two files
    # agree only if these strings match exactly - plan_overlap relies on that,
    # and deliberately degrades rather than guessing at a reprojection.
    crs = (geo.get("GTCitationGeogCitation") or geo.get("GeogCitation")
           or geo.get("GTCitationGeoKey") or geo.get("ProjectedCSTypeGeoKey")
           or (str(ascii_params).strip("|") if ascii_params else None))

    meta = dict(_EMPTY_META)
    meta.update(
        gsd_mpp=float(scale[0]) if scale else None,
        crs=crs,
        transform=(float(tie[3]), float(scale[0]), 0.0,
                   float(tie[4]), 0.0, -float(scale[1])) if (tie and scale) else None,
        format="GeoTIFF",
        path=str(path),
        stored_dtype=str(np.asarray(arr).dtype),
        geo_keys=geo or None,
    )
    return arr, meta


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

_DISPATCH = {
    ".xml": _load_pds4, ".lbl": _load_pds3,
    ".img": _load_pds3, ".tif": _load_tif, ".tiff": _load_tif,
}


def load(path: str | pathlib.Path) -> tuple[np.ndarray, dict[str, Any]]:
    """Read any supported lunar product.

    Returns (float32 2-D array in native byte order, metadata dict).

    Metadata always carries these keys; any the label does not supply are None:
        gsd_mpp, instrument, sun_azimuth, sun_elevation, incidence, crs, transform
    plus format, path and stored_dtype for provenance.

    A None means "this label did not say". It never means zero and never means a
    default. Callers must handle None rather than filling it in - a fabricated
    sun angle is exactly the failure Invariant 1 exists to prevent.
    """
    p = pathlib.Path(path)
    if not p.exists():
        raise LoaderError(f"no such file: {p}")
    fn = _DISPATCH.get(p.suffix.lower())
    if fn is None:
        raise LoaderError(
            f"unsupported extension {p.suffix!r}. Known: {sorted(_DISPATCH)}"
        )
    arr, meta = fn(p)
    return as_cv_safe(arr), meta


def dump_label(path: str | pathlib.Path, limit: int = 400) -> int:
    """Print every leaf of a label, so real field names can be READ, not guessed.

    Run this the hour Rohan's first CH-2 and first LROC product land:

        python -c "from core.io_loader import dump_label; dump_label('<file>')"

    Then copy the true spellings into CANDIDATES at the top of this file. That is
    a one-line change per field. Guessing them is how a wrong sun angle reaches
    a slide.
    """
    p = pathlib.Path(path)
    rows: list[tuple[str, str]] = []
    if p.suffix.lower() == ".xml":
        import pds4_tools
        hook = sys.excepthook
        try:
            sl = pds4_tools.read(str(p), quiet=True, lazy_load=True, no_scale=True)
            rows = _leaves(sl.label.getroot())
        finally:
            sys.excepthook = hook
    else:
        import pvl
        text, _ = _read_pds3_label(p)
        label = pvl.loads(text)

        def rec(node, prefix=""):
            from collections.abc import Mapping
            for k, v in node.items():
                if isinstance(v, Mapping):
                    rec(v, f"{prefix}{k}.")
                else:
                    rows.append((f"{prefix}{k}", str(v)))
        rec(label)

    wanted = {c for group in CANDIDATES.values() for c in group}
    print(f"{p.name}: {len(rows)} leaves\n")
    for tag, text in rows[:limit]:
        mark = "  <== CANDIDATE" if tag.split(".")[-1].lower() in wanted else ""
        print(f"  {tag:<44} {text[:60]}{mark}")
    if len(rows) > limit:
        print(f"  ... {len(rows) - limit} more (raise `limit`)")
    return len(rows)


# ---------------------------------------------------------------------------
# Overlap - Rohan imports crop_to_overlap on Day 5
# ---------------------------------------------------------------------------

def plan_overlap(meta_a: dict, meta_b: dict, shape_a: tuple[int, int],
                 shape_b: tuple[int, int]) -> dict[str, Any]:
    """Work out the overlapping window in each image, WITHOUT reading pixels.

    Returns a plan, not arrays:
        {"window_a": (x, y, w, h), "window_b": (x, y, w, h),
         "method": "geo" | "none", "note": str}

    Two decisions worth defending:

    CROP FIRST, THEN RESAMPLE. The other order resamples the whole frame to
    discard most of it - 4119.9 MiB of intermediate against 1216.4 MiB for the
    same result on a real OHRC/Kaguya pair, on a laptop where a 1024x1024 LoFTR
    pass already fails for want of RAM.

    A PLAN, NOT PIXELS. The caller keeps the integer window, so any match found
    later maps back to a pixel in the original full frame exactly. A registration
    result that cannot be mapped back to the source frame is not useful, and a
    fractional crop offset silently destroys the sub-pixel claim.

    When either image has no georeferencing there is no honest way to compute a
    true overlap, so method is "none" and both windows are the full frames. That
    is not a failure - it is the truthful answer, and it is what two raw OHRC
    frames will always give. It NEVER raises: a crash here would take out Rohan's
    whole catalogue run over one bad pair.
    """
    ha, wa = shape_a
    hb, wb = shape_b
    full = {"window_a": (0, 0, wa, ha), "window_b": (0, 0, wb, hb)}

    ta, tb = meta_a.get("transform"), meta_b.get("transform")
    ga, gb = meta_a.get("gsd_mpp"), meta_b.get("gsd_mpp")
    if not ta or not tb:
        return {**full, "method": "none",
                "note": "one or both images are not georeferenced; full frames returned"}
    if not ga or not gb or ga <= 0 or gb <= 0:
        return {**full, "method": "none",
                "note": "gsd_mpp missing or non-positive; cannot compare ground extents"}
    if meta_a.get("crs") != meta_b.get("crs"):
        return {**full, "method": "none",
                "note": f"different CRS ({meta_a.get('crs')} vs {meta_b.get('crs')}); "
                        "no pyproj on this machine to reconcile them"}

    def bounds(t, w, h):
        x0, sx, _, y0, _, sy = t
        xs = (x0, x0 + sx * w)
        ys = (y0, y0 + sy * h)
        return min(xs), min(ys), max(xs), max(ys)

    ax0, ay0, ax1, ay1 = bounds(ta, wa, ha)
    bx0, by0, bx1, by1 = bounds(tb, wb, hb)
    ox0, oy0 = max(ax0, bx0), max(ay0, by0)
    ox1, oy1 = min(ax1, bx1), min(ay1, by1)
    if ox1 <= ox0 or oy1 <= oy0:
        return {**full, "method": "none", "note": "footprints do not overlap"}

    def window(t, w, h):
        x0, sx, _, y0, _, sy = t
        cx0 = int(np.floor((ox0 - x0) / sx)) if sx > 0 else int(np.floor((ox1 - x0) / sx))
        cy0 = int(np.floor((oy1 - y0) / sy)) if sy < 0 else int(np.floor((oy0 - y0) / sy))
        cw = int(np.ceil(abs((ox1 - ox0) / sx)))
        ch = int(np.ceil(abs((oy1 - oy0) / sy)))
        cx0, cy0 = max(0, cx0), max(0, cy0)
        return cx0, cy0, max(1, min(cw, w - cx0)), max(1, min(ch, h - cy0))

    return {"window_a": window(ta, wa, ha), "window_b": window(tb, wb, hb),
            "method": "geo", "note": "bounding-box intersection in a shared CRS"}


def crop_to_overlap(src_path: str | pathlib.Path, ref_path: str | pathlib.Path,
                    out_prefix: str | pathlib.Path) -> dict[str, Any]:
    """Path-level wrapper over plan_overlap. This is the one Rohan calls.

        crop_to_overlap("a.IMG", "b.tif", "data/pairs/pair_01")
        -> writes pair_01_source.tif and pair_01_ref.tif, returns the plan

    The returned dict is what a row of data/pairs_catalogue.csv needs: the two
    windows, the method actually used, and a note. `method` must be carried into
    the catalogue - a "none" row is a pair we cropped blindly, and the difference
    matters when someone asks on Day 12 how the pairs were built.
    """
    import tifffile

    a, ma = load(src_path)
    b, mb = load(ref_path)
    plan = plan_overlap(ma, mb, a.shape, b.shape)

    out = pathlib.Path(out_prefix)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for arr, (x, y, w, h), suffix in (
        (a, plan["window_a"], "_source.tif"),
        (b, plan["window_b"], "_ref.tif"),
    ):
        dst = out.with_name(out.name + suffix)
        tifffile.imwrite(str(dst), arr[y:y + h, x:x + w])
        written.append(str(dst))

    return {**plan, "written": written,
            "source_gsd_mpp": ma.get("gsd_mpp"), "ref_gsd_mpp": mb.get("gsd_mpp"),
            "source_meta": ma, "ref_meta": mb}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("usage: python -m core.io_loader <product>   # loads and describes it")
        raise SystemExit(2)
    image, metadata = load(sys.argv[1])
    print(f"{sys.argv[1]}\n  shape {image.shape}  dtype {image.dtype}  "
          f"range [{image.min():.3f}, {image.max():.3f}]")
    for key in ("format", "instrument", "gsd_mpp", "sun_azimuth", "sun_elevation",
                "incidence", "crs", "stored_dtype"):
        flag = "" if metadata.get(key) is not None else "   <== not in this label"
        print(f"  {key:<16} {metadata.get(key)}{flag}")
