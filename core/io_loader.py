"""
One loader for every lunar product format we will ever open.

Supported:
    .xml       PDS4 - Chandrayaan-2
    .IMG/.img  PDS3 - LROC NAC
    .lbl       PDS3 label
    .tif/.tiff GeoTIFF - Kaguya TC
    .png       PNG - test/demo/generated images
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Candidate metadata names
# ---------------------------------------------------------------------------

CANDIDATES: dict[str, tuple[str, ...]] = {
    "sun_azimuth": (
        "sun_azimuth",
        "solar_azimuth",
        "sub_solar_azimuth",
        "sun_azimuth_angle",
        "subsolar_azimuth",
        "solar_azimuth_angle",
    ),
    "sun_elevation": (
        "sun_elevation",
        "solar_elevation",
        "sun_elevation_angle",
        "solar_elevation_angle",
    ),
    "incidence": (
        "incidence_angle",
        "incidence",
        "solar_incidence_angle",
        "sub_solar_incidence",
        "solar_incidence",
        "incidence_angle_degrees",
    ),
    "emission": (
        "emission_angle",
        "emission",
    ),
    "phase": (
        "phase_angle",
        "phase",
    ),
    "instrument": (
        "instrument_name",
        "instrument_id",
        "instrument",
        "name",
        "spacecraft_instrument_name",
    ),
    "gsd_mpp": (
        "pixel_scale",
        "map_scale",
        "pixel_resolution",
        "ground_sample_distance",
        "spatial_resolution",
        "pixel_size",
        "map_resolution",
    ),
    "product_id": (
        "product_id",
        "logical_identifier",
        "product_name",
    ),
}


# ---------------------------------------------------------------------------
# PDS3 sample types
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# PDS4 data types
# ---------------------------------------------------------------------------

PDS4_DTYPES: dict[str, str] = {
    "UnsignedByte": "u1",
    "SignedByte": "i1",

    "UnsignedMSB2": ">u2",
    "UnsignedMSB4": ">u4",
    "UnsignedMSB8": ">u8",

    "SignedMSB2": ">i2",
    "SignedMSB4": ">i4",
    "SignedMSB8": ">i8",

    "UnsignedLSB2": "<u2",
    "UnsignedLSB4": "<u4",
    "UnsignedLSB8": "<u8",

    "SignedLSB2": "<i2",
    "SignedLSB4": "<i4",
    "SignedLSB8": "<i8",

    "IEEE754MSBSingle": ">f4",
    "IEEE754MSBDouble": ">f8",

    "IEEE754LSBSingle": "<f4",
    "IEEE754LSBDouble": "<f8",
}


# ---------------------------------------------------------------------------
# Safety limit
# ---------------------------------------------------------------------------

MAX_PIXELS_WITHOUT_WINDOW = 64_000_000


_EMPTY_META: dict[str, Any] = {
    "gsd_mpp": None,
    "instrument": None,
    "sun_azimuth": None,
    "sun_elevation": None,
    "incidence": None,
    "crs": None,
    "transform": None,
}


class LoaderError(RuntimeError):
    """Raised when a lunar product cannot be read."""


# ---------------------------------------------------------------------------
# Common conversion
# ---------------------------------------------------------------------------

def as_cv_safe(arr: np.ndarray) -> np.ndarray:
    """
    Convert image to:
        - 2-D
        - native byte order
        - contiguous
        - float32

    This is required before OpenCV or Torch touches the image.
    """

    a = np.asarray(arr)

    if a.ndim == 3:
        # For multi-band data, use band 0.
        if a.shape[-1] <= a.shape[0]:
            a = a[..., 0]
        else:
            a = a[0]

    elif a.ndim != 2:
        raise LoaderError(
            f"expected a 2-D image, got shape {a.shape}"
        )

    if a.dtype.byteorder not in ("=", "|"):
        a = a.astype(a.dtype.newbyteorder("="))

    return np.ascontiguousarray(a, dtype=np.float32)


def _first_number(text: Any) -> float | None:
    """Extract the first numeric value from metadata."""

    if text is None:
        return None

    if hasattr(text, "value"):
        text = text.value

    if isinstance(text, (int, float)) and not isinstance(text, bool):
        return float(text)

    m = re.search(
        r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?",
        str(text),
    )

    return float(m.group()) if m else None


# ---------------------------------------------------------------------------
# PDS4 - Chandrayaan-2
# ---------------------------------------------------------------------------

def _leaves(root) -> list[tuple[str, str]]:
    """Return all leaf XML elements as (tag, text)."""

    out = []

    for el in root.iter():

        tag = el.tag.rpartition("}")[2].lower()

        if el.text and el.text.strip():
            out.append((tag, el.text.strip()))

        for k, v in el.attrib.items():
            out.append(
                (
                    k.rpartition("}")[2].lower(),
                    v,
                )
            )

    return out


def _pick(leaves: list[tuple[str, str]], key: str) -> Any:
    """Find metadata using the candidate names."""

    for want in CANDIDATES[key]:

        for tag, text in leaves:

            if tag == want:
                return text

    return None


def _instrument_name(root) -> str | None:
    """Find the instrument name from an Instrument element."""

    for el in root.iter():

        kids = {
            c.tag.rpartition("}")[2].lower():
            (c.text or "").strip()

            for c in el

            if len(list(c)) == 0
        }

        if (
            kids.get("type", "").lower() == "instrument"
            and kids.get("name")
        ):
            return kids["name"]

    return None


def _pds4_array_spec(
    root,
    path: pathlib.Path,
) -> dict[str, Any] | None:
    """Locate a PDS4 2-D array for memory mapping."""

    for fa in root.iter():

        if fa.tag.rpartition("}")[2] != "File_Area_Observational":
            continue

        kids = {
            c.tag.rpartition("}")[2]: c
            for c in fa
        }

        arr = kids.get("Array_2D_Image")
        fil = kids.get("File")

        if arr is None or fil is None:
            continue

        def text(parent, name):

            for c in parent.iter():

                if (
                    c.tag.rpartition("}")[2] == name
                    and c.text
                ):
                    return c.text.strip()

            return None

        name = text(fil, "file_name")
        dt = text(arr, "data_type")

        if not name or dt not in PDS4_DTYPES:
            continue

        axes = []

        for ax in arr:

            if ax.tag.rpartition("}")[2] == "Axis_Array":

                n = text(ax, "elements")
                seq = text(ax, "sequence_number")

                if n:
                    axes.append(
                        (
                            int(seq or len(axes) + 1),
                            int(n),
                        )
                    )

        if len(axes) != 2:
            continue

        axes.sort()

        data = path.parent / name

        if not data.exists():
            raise LoaderError(
                f"{path.name} references {name}, "
                "which is not beside it."
            )

        order = (
            text(arr, "axis_index_order")
            or "Last Index Fastest"
        )

        return {
            "path": data,
            "dtype": np.dtype(PDS4_DTYPES[dt]),
            "shape": (
                axes[0][1],
                axes[1][1],
            ),
            "offset": int(
                text(arr, "offset") or 0
            ),
            "order": order,
            "declared_type": dt,
            "md5": text(
                fil,
                "md5_checksum",
            ),
        }

    return None


def _load_pds4(
    path: pathlib.Path,
) -> tuple[np.ndarray, dict[str, Any]]:

    try:
        import pds4_tools

    except ImportError as e:

        raise LoaderError(
            "pds4_tools is not installed. "
            "Run: pip install pds4_tools"
        ) from e

    hook = sys.excepthook

    try:

        sl = pds4_tools.read(
            str(path),
            quiet=True,
            lazy_load=True,
            no_scale=True,
        )

    except Exception as e:

        raise LoaderError(
            f"pds4_tools could not read "
            f"{path.name}: {e}"
        ) from e

    finally:
        sys.excepthook = hook

    root = sl.label.getroot()

    spec = _pds4_array_spec(
        root,
        path,
    )

    if spec is not None:

        arr = np.memmap(
            spec["path"],
            dtype=spec["dtype"],
            mode="r",
            offset=spec["offset"],
            shape=spec["shape"],
        )

        if "First Index Fastest" in spec["order"]:
            arr = arr.T

    else:

        arr = None

        for s in sl:

            if (
                s.is_array()
                and getattr(s.data, "ndim", 0) >= 2
            ):
                arr = np.asarray(s.data)
                break

        if arr is None:
            raise LoaderError(
                f"{path.name} contains no 2-D array"
            )

    leaves = _leaves(root)

    meta = dict(_EMPTY_META)

    meta.update(
        gsd_mpp=_first_number(
            _pick(leaves, "gsd_mpp")
        ),

        instrument=(
            _instrument_name(root)
            or _pick(leaves, "instrument")
        ),

        sun_azimuth=_first_number(
            _pick(leaves, "sun_azimuth")
        ),

        sun_elevation=_first_number(
            _pick(leaves, "sun_elevation")
        ),

        incidence=_first_number(
            _pick(leaves, "incidence")
        ),

        emission=_first_number(
            _pick(leaves, "emission")
        ),

        phase=_first_number(
            _pick(leaves, "phase")
        ),

        product_id=_pick(
            leaves,
            "product_id",
        ),

        format="PDS4",

        path=str(path),

        stored_dtype=str(
            arr.dtype
        ),
    )

    return arr, meta


# ---------------------------------------------------------------------------
# PDS3 - LROC NAC
# ---------------------------------------------------------------------------

_END_RE = re.compile(
    rb"^[ \t]*END[ \t]*(\r\n|\r|\n)",
    re.MULTILINE,
)


def _read_pds3_label(
    path: pathlib.Path,
    probe: int = 1 << 20,
) -> tuple[str, int]:

    with open(path, "rb") as f:
        head = f.read(probe)

    m = _END_RE.search(head)

    if m is None:
        raise LoaderError(
            f"{path.name}: no END statement "
            f"in the first {probe} bytes."
        )

    return (
        head[:m.end()].decode(
            "ascii",
            errors="replace",
        ),
        m.end(),
    )


def _walk(node, key: str):

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

        hit = _walk(
            label,
            want,
        )

        if hit is not None:
            return hit

    return None


def _load_pds3(
    path: pathlib.Path,
) -> tuple[np.ndarray, dict[str, Any]]:

    try:
        import pvl

    except ImportError as e:

        raise LoaderError(
            "pvl is not installed. "
            "Run: pip install pvl"
        ) from e

    text, _ = _read_pds3_label(path)

    try:

        label = pvl.loads(text)

    except Exception as e:

        raise LoaderError(
            f"{path.name}: PVL parse failed "
            f"({type(e).__name__})"
        ) from e

    img = _walk(
        label,
        "IMAGE",
    )

    if img is None:
        raise LoaderError(
            f"{path.name}: label has no IMAGE object"
        )

    need = (
        "LINES",
        "LINE_SAMPLES",
        "SAMPLE_BITS",
        "SAMPLE_TYPE",
    )

    missing = [
        k
        for k in need
        if _walk(img, k) is None
    ]

    if missing:
        raise LoaderError(
            f"{path.name}: IMAGE is missing "
            f"{missing}"
        )

    lines = int(
        _first_number(
            _walk(img, "LINES")
        )
    )

    samples = int(
        _first_number(
            _walk(img, "LINE_SAMPLES")
        )
    )

    bits = int(
        _first_number(
            _walk(img, "SAMPLE_BITS")
        )
    )

    stype = str(
        _walk(img, "SAMPLE_TYPE")
    ).strip().strip('"')

    bands = int(
        _first_number(
            _walk(img, "BANDS")
        )
        or 1
    )

    if stype not in PDS3_SAMPLE_TYPES:
        raise LoaderError(
            f"{path.name}: unknown "
            f"SAMPLE_TYPE {stype!r}"
        )

    order, kind = PDS3_SAMPLE_TYPES[stype]

    width = bits // 8

    if kind == "f" and width not in (2, 4, 8):
        raise LoaderError(
            f"{path.name}: unsupported "
            f"{width}-byte float"
        )

    if kind in "iu" and width not in (1, 2, 4, 8):
        raise LoaderError(
            f"{path.name}: unsupported "
            f"{width}-byte integer"
        )

    dtype = np.dtype(
        f"{order}{kind}{width}"
    )

    offset, data_path = _image_offset(
        label,
        path,
    )

    count = (
        lines
        * samples
        * bands
    )

    expect = (
        offset
        + count * dtype.itemsize
    )

    if data_path.stat().st_size < expect:
        raise LoaderError(
            f"{data_path.name}: file is "
            f"{data_path.stat().st_size} bytes, "
            f"but the label describes {expect}"
        )

    if bands == 1:

        shape = (
            lines,
            samples,
        )

    else:

        shape = (
            bands,
            lines,
            samples,
        )

    arr = np.memmap(
        data_path,
        dtype=dtype,
        mode="r",
        offset=offset,
        shape=shape,
    )

    signedness_fixed = False

    if (
        dtype.itemsize == 1
        and dtype.kind == "i"
        and int(np.asarray(arr).min()) < 0
    ):

        arr = np.asarray(arr).view(
            np.uint8
        )

        signedness_fixed = True

    meta = dict(_EMPTY_META)

    meta.update(
        gsd_mpp=_first_number(
            _pds3_pick(
                label,
                "gsd_mpp",
            )
        ),

        instrument=_pds3_pick(
            label,
            "instrument",
        ),

        sun_azimuth=_first_number(
            _pds3_pick(
                label,
                "sun_azimuth",
            )
        ),

        sun_elevation=_first_number(
            _pds3_pick(
                label,
                "sun_elevation",
            )
        ),

        incidence=_first_number(
            _pds3_pick(
                label,
                "incidence",
            )
        ),

        emission=_first_number(
            _pds3_pick(
                label,
                "emission",
            )
        ),

        phase=_first_number(
            _pds3_pick(
                label,
                "phase",
            )
        ),

        product_id=_pds3_pick(
            label,
            "product_id",
        ),

        format="PDS3",

        path=str(path),

        stored_dtype=str(dtype),

        unit=_walk(
            img,
            "UNIT",
        ),

        dn_signedness_corrected=signedness_fixed,
    )

    return arr, meta


def _image_offset(
    label,
    path: pathlib.Path,
) -> tuple[int, pathlib.Path]:

    ptr = _walk(
        label,
        "^IMAGE",
    )

    if ptr is None:
        return 0, path

    rec = int(
        _first_number(
            _walk(
                label,
                "RECORD_BYTES",
            )
        )
        or 0
    )

    if (
        isinstance(ptr, (list, tuple))
        and not hasattr(ptr, "units")
    ):

        name = str(
            ptr[0]
        ).strip('"')

        where = ptr[1]

        sib = path.parent / name

        if not sib.exists():
            raise LoaderError(
                f"{path.name}: ^IMAGE points at "
                f"{name}, which is not beside it"
            )

        return (
            _offset_of(
                where,
                rec,
            ),
            sib,
        )

    if isinstance(ptr, str):

        sib = (
            path.parent
            / ptr.strip('"')
        )

        if not sib.exists():
            raise LoaderError(
                f"{path.name}: ^IMAGE points at "
                f"{ptr}, which is not beside it"
            )

        return 0, sib

    return (
        _offset_of(
            ptr,
            rec,
        ),
        path,
    )


def _offset_of(
    where: Any,
    record_bytes: int,
) -> int:

    if (
        hasattr(where, "units")
        and "byte"
        in str(where.units).lower()
    ):

        return max(
            0,
            int(
                _first_number(where)
            ) - 1,
        )

    n = int(
        _first_number(where)
    )

    if record_bytes <= 0:
        raise LoaderError(
            "^IMAGE is a record number "
            "but RECORD_BYTES is absent"
        )

    return max(
        0,
        (n - 1) * record_bytes,
    )


# ---------------------------------------------------------------------------
# GeoTIFF - Kaguya
# ---------------------------------------------------------------------------

def _load_tif(
    path: pathlib.Path,
) -> tuple[np.ndarray, dict[str, Any]]:

    try:
        import tifffile

    except ImportError as e:

        raise LoaderError(
            "tifffile is not installed."
        ) from e

    geo: dict[str, Any] = {}

    scale = None
    tie = None
    arr = None

    try:

        with tifffile.TiffFile(
            str(path)
        ) as tf:

            page = tf.pages[0]

            def tag(code):

                t = page.tags.get(code)

                return (
                    t.value
                    if t is not None
                    else None
                )

            scale = tag(33550)
            tie = tag(33922)

            ascii_params = tag(34737)

            try:
                geo = dict(
                    tf.geotiff_metadata
                    or {}
                )
            except Exception:
                geo = {}

            try:
                arr = page.asarray()
            except Exception:
                arr = None

    except Exception as e:

        raise LoaderError(
            f"tifffile could not open "
            f"{path.name}: {e}"
        ) from e

    if arr is None:

        try:

            from PIL import Image

            Image.MAX_IMAGE_PIXELS = None

            with Image.open(
                str(path)
            ) as im:

                arr = np.array(im)

        except Exception as e:

            raise LoaderError(
                f"{path.name}: could not decode TIFF "
                f"pixels: {e}"
            ) from e

    scale = (
        scale
        or geo.get(
            "ModelPixelScale"
        )
    )

    tie = (
        tie
        or geo.get(
            "ModelTiepoint"
        )
    )

    crs = (
        geo.get(
            "GTCitationGeogCitation"
        )
        or geo.get(
            "GeogCitation"
        )
        or geo.get(
            "GTCitationGeoKey"
        )
        or geo.get(
            "ProjectedCSTypeGeoKey"
        )
        or (
            str(ascii_params).strip("|")
            if ascii_params
            else None
        )
    )

    meta = dict(_EMPTY_META)

    meta.update(
        gsd_mpp=(
            float(scale[0])
            if scale
            else None
        ),

        crs=crs,

        transform=(
            (
                float(tie[3]),
                float(scale[0]),
                0.0,
                float(tie[4]),
                0.0,
                -float(scale[1]),
            )
            if tie and scale
            else None
        ),

        format="GeoTIFF",

        path=str(path),

        stored_dtype=str(
            np.asarray(arr).dtype
        ),

        geo_keys=geo or None,
    )

    return arr, meta


# ---------------------------------------------------------------------------
# PNG
# ---------------------------------------------------------------------------

def _load_png(
    path: pathlib.Path,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Load PNG images using Pillow.

    PNG files generally do not contain the lunar georeferencing metadata
    required by the registration pipeline, so those metadata fields remain
    None.

    This branch is mainly for:
        - test images
        - generated previews
        - demonstration pairs
        - intermediate PNG products
    """

    try:
        from PIL import Image

    except ImportError as e:

        raise LoaderError(
            "Pillow is not installed. "
            "Run: pip install pillow"
        ) from e

    try:

        Image.MAX_IMAGE_PIXELS = None

        with Image.open(
            str(path)
        ) as im:

            arr = np.array(im)

    except Exception as e:

        raise LoaderError(
            f"could not read PNG "
            f"{path.name}: {e}"
        ) from e

    meta = dict(_EMPTY_META)

    meta.update(
        format="PNG",
        path=str(path),
        stored_dtype=str(
            arr.dtype
        ),
    )

    return arr, meta


# ---------------------------------------------------------------------------
# Public dispatch
# ---------------------------------------------------------------------------

_DISPATCH = {
    ".xml": _load_pds4,
    ".lbl": _load_pds3,
    ".img": _load_pds3,
    ".tif": _load_tif,
    ".tiff": _load_tif,

    # IMPORTANT:
    # PNG support added here.
    ".png": _load_png,
}


def load(
    path: str | pathlib.Path,
    window: tuple[int, int, int, int] | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Read any supported lunar product.

    window:
        Optional (x, y, w, h) crop in the original image coordinates.
    """

    p = pathlib.Path(path)

    if not p.exists():
        raise LoaderError(
            f"no such file: {p}"
        )

    fn = _DISPATCH.get(
        p.suffix.lower()
    )

    if fn is None:
        raise LoaderError(
            f"unsupported extension "
            f"{p.suffix!r}. Known: "
            f"{sorted(_DISPATCH)}"
        )

    arr, meta = fn(p)

    meta["full_shape"] = tuple(
        arr.shape[:2]
    )

    if window is not None:

        x, y, w, h = (
            int(v)
            for v in window
        )

        H, W = arr.shape[:2]

        if (
            x < 0
            or y < 0
            or w <= 0
            or h <= 0
            or x >= W
            or y >= H
        ):

            raise LoaderError(
                f"window {window} is outside "
                f"the {W}x{H} image "
                f"{p.name}"
            )

        arr = arr[
            y:min(y + h, H),
            x:min(x + w, W),
        ]

        meta["window"] = (
            x,
            y,
            arr.shape[1],
            arr.shape[0],
        )

    elif arr.size > MAX_PIXELS_WITHOUT_WINDOW:

        H, W = arr.shape[:2]

        raise LoaderError(
            f"{p.name} is "
            f"{W}x{H} = "
            f"{arr.size / 1e6:.0f} Mpx "
            f"and is too large to load "
            f"without a window.\n"
            f"Pass a window like:\n"
            f"load(path, window=(0, 0, 640, 640))"
        )

    return as_cv_safe(arr), meta


# ---------------------------------------------------------------------------
# Label inspection
# ---------------------------------------------------------------------------

def dump_label(
    path: str | pathlib.Path,
    limit: int = 400,
) -> int:

    p = pathlib.Path(path)

    rows: list[
        tuple[str, str]
    ] = []

    if p.suffix.lower() == ".xml":

        import pds4_tools

        hook = sys.excepthook

        try:

            sl = pds4_tools.read(
                str(p),
                quiet=True,
                lazy_load=True,
                no_scale=True,
            )

            rows = _leaves(
                sl.label.getroot()
            )

        finally:
            sys.excepthook = hook

    else:

        import pvl

        text, _ = _read_pds3_label(p)

        label = pvl.loads(text)

        def rec(
            node,
            prefix="",
        ):

            from collections.abc import Mapping

            for k, v in node.items():

                if isinstance(
                    v,
                    Mapping,
                ):

                    rec(
                        v,
                        f"{prefix}{k}.",
                    )

                else:

                    rows.append(
                        (
                            f"{prefix}{k}",
                            str(v),
                        )
                    )

        rec(label)

    wanted = {
        c
        for group in CANDIDATES.values()
        for c in group
    }

    print(
        f"{p.name}: "
        f"{len(rows)} leaves\n"
    )

    for tag, text in rows[:limit]:

        mark = (
            "  <== CANDIDATE"
            if tag.split(".")[-1].lower()
            in wanted
            else ""
        )

        print(
            f"  {tag:<44} "
            f"{text[:60]}"
            f"{mark}"
        )

    if len(rows) > limit:

        print(
            f"  ... "
            f"{len(rows) - limit} more"
        )

    return len(rows)


# ---------------------------------------------------------------------------
# Overlap planning
# ---------------------------------------------------------------------------

def plan_overlap(
    meta_a: dict,
    meta_b: dict,
    shape_a: tuple[int, int],
    shape_b: tuple[int, int],
) -> dict[str, Any]:

    ha, wa = shape_a
    hb, wb = shape_b

    full = {
        "window_a": (
            0,
            0,
            wa,
            ha,
        ),

        "window_b": (
            0,
            0,
            wb,
            hb,
        ),
    }

    ta = meta_a.get(
        "transform"
    )

    tb = meta_b.get(
        "transform"
    )

    ga = meta_a.get(
        "gsd_mpp"
    )

    gb = meta_b.get(
        "gsd_mpp"
    )

    if not ta or not tb:

        return {
            **full,
            "method": "none",
            "note": (
                "one or both images are "
                "not georeferenced; "
                "full frames returned"
            ),
        }

    if (
        not ga
        or not gb
        or ga <= 0
        or gb <= 0
    ):

        return {
            **full,
            "method": "none",
            "note": (
                "gsd_mpp missing or "
                "non-positive; cannot "
                "compare ground extents"
            ),
        }

    if (
        meta_a.get("crs")
        != meta_b.get("crs")
    ):

        return {
            **full,
            "method": "none",
            "note": (
                f"different CRS "
                f"({meta_a.get('crs')} "
                f"vs "
                f"{meta_b.get('crs')}); "
                "no pyproj available"
            ),
        }

    def bounds(
        t,
        w,
        h,
    ):

        x0, sx, _, y0, _, sy = t

        xs = (
            x0,
            x0 + sx * w,
        )

        ys = (
            y0,
            y0 + sy * h,
        )

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys),
        )

    ax0, ay0, ax1, ay1 = bounds(
        ta,
        wa,
        ha,
    )

    bx0, by0, bx1, by1 = bounds(
        tb,
        wb,
        hb,
    )

    ox0 = max(
        ax0,
        bx0,
    )

    oy0 = max(
        ay0,
        by0,
    )

    ox1 = min(
        ax1,
        bx1,
    )

    oy1 = min(
        ay1,
        by1,
    )

    if (
        ox1 <= ox0
        or oy1 <= oy0
    ):

        return {
            **full,
            "method": "none",
            "note": (
                "footprints do not overlap"
            ),
        }

    def window(
        t,
        w,
        h,
    ):

        x0, sx, _, y0, _, sy = t

        if sx > 0:
            cx0 = int(
                np.floor(
                    (ox0 - x0) / sx
                )
            )
        else:
            cx0 = int(
                np.floor(
                    (ox1 - x0) / sx
                )
            )

        if sy < 0:
            cy0 = int(
                np.floor(
                    (oy1 - y0) / sy
                )
            )
        else:
            cy0 = int(
                np.floor(
                    (oy0 - y0) / sy
                )
            )

        cw = int(
            np.ceil(
                abs(
                    (ox1 - ox0) / sx
                )
            )
        )

        ch = int(
            np.ceil(
                abs(
                    (oy1 - oy0) / sy
                )
            )
        )

        cx0 = max(
            0,
            cx0,
        )

        cy0 = max(
            0,
            cy0,
        )

        return (
            cx0,
            cy0,
            max(
                1,
                min(
                    cw,
                    w - cx0,
                ),
            ),
            max(
                1,
                min(
                    ch,
                    h - cy0,
                ),
            ),
        )

    return {
        "window_a": window(
            ta,
            wa,
            ha,
        ),

        "window_b": window(
            tb,
            wb,
            hb,
        ),

        "method": "geo",

        "note": (
            "bounding-box intersection "
            "in a shared CRS"
        ),
    }


# ---------------------------------------------------------------------------
# Crop to overlap
# ---------------------------------------------------------------------------

def crop_to_overlap(
    src_path: str | pathlib.Path,
    ref_path: str | pathlib.Path,
    out_prefix: str | pathlib.Path,
) -> dict[str, Any]:

    import tifffile

    a, ma = load(
        src_path
    )

    b, mb = load(
        ref_path
    )

    plan = plan_overlap(
        ma,
        mb,
        a.shape,
        b.shape,
    )

    out = pathlib.Path(
        out_prefix
    )

    out.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    written = []

    for arr, window, suffix in (
        (
            a,
            plan["window_a"],
            "_source.tif",
        ),
        (
            b,
            plan["window_b"],
            "_ref.tif",
        ),
    ):

        x, y, w, h = window

        dst = out.with_name(
            out.name + suffix
        )

        tifffile.imwrite(
            str(dst),
            arr[
                y:y + h,
                x:x + w,
            ],
        )

        written.append(
            str(dst)
        )

    return {
        **plan,

        "written": written,

        "source_gsd_mpp":
            ma.get("gsd_mpp"),

        "ref_gsd_mpp":
            mb.get("gsd_mpp"),

        "source_meta":
            ma,

        "ref_meta":
            mb,
    }


# ---------------------------------------------------------------------------
# Command-line usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(__doc__)

        print(
            "usage: "
            "python -m core.io_loader "
            "<product>"
        )

        raise SystemExit(2)

    image, metadata = load(
        sys.argv[1]
    )

    print(
        f"{sys.argv[1]}\n"
        f"  shape {image.shape}\n"
        f"  dtype {image.dtype}\n"
        f"  range "
        f"[{image.min():.3f}, "
        f"{image.max():.3f}]"
    )

    for key in (
        "format",
        "instrument",
        "gsd_mpp",
        "sun_azimuth",
        "sun_elevation",
        "incidence",
        "crs",
        "stored_dtype",
    ):

        flag = (
            ""
            if metadata.get(key)
            is not None
            else "   <== not in this label"
        )

        print(
            f"  {key:<16} "
            f"{metadata.get(key)}"
            f"{flag}"
        )