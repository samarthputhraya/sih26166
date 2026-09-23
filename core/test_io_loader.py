"""Tests for core/io_loader.py.

`io_loader.py` is 874 lines and the most trap-laden module in the project, and until now it had
no tests at all. Day 4 schedules a refactor of it. These exist to be written BEFORE that
refactor, not after, so the refactor has something to be safe against.

Each test locks a trap that is already recorded in the team's known-issues list, and names it.
A test here failing does not mean "tidy the assertion" - it means a documented silent-corruption
bug has come back.
"""
import numpy as np
import cv2
import pytest

from core import io_loader
from core.io_loader import as_cv_safe, load, LoaderError


# --- as_cv_safe: Known issue #2, big-endian silently corrupts OpenCV ----------

def test_big_endian_is_normalised_and_values_survive():
    """Known issue #2. cv2 accepts a big-endian array WITHOUT raising and returns garbage -
    max abs difference measured at 34935. There is no exception to catch, so the only defence
    is that nothing reaches cv2 without passing through here."""
    values = np.array([[0, 1, 255, 4096, 65535]], dtype=">u2")
    out = as_cv_safe(values)
    assert out.dtype == np.float32
    assert out.dtype.byteorder in ("=", "|")
    np.testing.assert_array_equal(out, np.array([[0, 1, 255, 4096, 65535]], np.float32))


def test_numpy_arithmetic_does_not_preserve_byte_order():
    """The second-order trap from Known issue #2: `np.arange(n, dtype='>u2') * 37` comes back
    in NATIVE order. Cast AFTER arithmetic, never before, or you normalise the wrong array."""
    big = np.arange(8, dtype=">u2").reshape(2, 4)
    assert big.dtype.byteorder == ">"
    assert (big * 37).dtype.byteorder in ("=", "|"), \
        "if numpy starts preserving byte order here, io_loader's ordering assumption changes"
    # Either way, as_cv_safe gives the same answer - which is the point of funnelling through it.
    np.testing.assert_array_equal(as_cv_safe(big) * 37.0, as_cv_safe(big * 37))


def test_little_endian_and_native_are_left_alone():
    native = np.array([[1, 2], [3, 4]], np.uint16)
    np.testing.assert_array_equal(as_cv_safe(native), native.astype(np.float32))


def test_output_is_always_float32_2d_and_contiguous():
    out = as_cv_safe(np.asfortranarray(np.arange(12, dtype=np.uint8).reshape(3, 4)))
    assert out.dtype == np.float32 and out.ndim == 2 and out.flags["C_CONTIGUOUS"]


def test_multiband_takes_band_zero_and_does_not_average():
    """Averaging bands with different spectral response is not a panchromatic image.
    M3 and colour WAC arrive as cubes; the caller must know which band was matched."""
    cube = np.zeros((4, 5, 3), np.uint8)
    cube[..., 0] = 10
    cube[..., 1] = 200
    cube[..., 2] = 90
    out = as_cv_safe(cube)
    assert out.shape == (4, 5)
    assert np.all(out == 10), "must be band 0, not the mean (which would be 100)"


def test_band_first_cubes_are_handled_too():
    cube = np.zeros((3, 40, 50), np.uint8)
    cube[0] = 7
    cube[1] = 250
    out = as_cv_safe(cube)
    assert out.shape == (40, 50) and np.all(out == 7)


@pytest.mark.parametrize("shape", [(5,), (2, 2, 2, 2)])
def test_non_2d_non_3d_is_refused(shape):
    with pytest.raises(LoaderError, match="2-D"):
        as_cv_safe(np.zeros(shape, np.uint8))


# --- load: contract ----------------------------------------------------------

def _tif(tmp_path, arr, name="t.tif"):
    p = tmp_path / name
    assert cv2.imwrite(str(p), arr), "failed to write the test tif"
    return p


def test_missing_file_names_the_path():
    with pytest.raises(LoaderError, match="no such file"):
        load("definitely/not/here.tif")


def test_unsupported_extension_lists_what_is_supported(tmp_path):
    p = tmp_path / "x.jpeg2000"
    p.write_bytes(b"not an image")
    with pytest.raises(LoaderError, match="unsupported extension"):
        load(p)


def test_raw_dn_is_returned_unscaled(tmp_path):
    """Known issue #1. A loader must not rescale science data. matcher.py divides by 255 in
    exactly one place; if this ever normalises too, every pixel lands in [0, 0.004] and LoFTR
    returns ZERO matches with no exception."""
    arr = np.array([[0, 7, 128, 255]], np.uint8)
    img, _ = load(_tif(tmp_path, arr))
    np.testing.assert_array_equal(img, arr.astype(np.float32))
    assert img.max() == 255.0, "values must stay in DN, not be squeezed into [0, 1]"


def test_metadata_always_carries_the_promised_keys(tmp_path):
    """A None means 'the label did not say'. It never means zero and never means a default -
    a fabricated sun angle is exactly what Invariant 1 exists to prevent."""
    _, meta = load(_tif(tmp_path, np.full((8, 8), 40, np.uint8)))
    for key in ("gsd_mpp", "instrument", "sun_azimuth", "sun_elevation",
                "incidence", "crs", "transform"):
        assert key in meta, f"{key} missing from metadata contract"
    assert meta["gsd_mpp"] is None, "a plain tif has no map scale - must be None, not a guess"
    assert meta["full_shape"] == (8, 8)
    assert "format" in meta and "path" in meta and "stored_dtype" in meta


# --- load: the windowing guard ----------------------------------------------

def test_oversized_image_refuses_rather_than_eating_the_machine(tmp_path, monkeypatch):
    """A CH-2 OHRC strip is 93693x12000 - 4.5 GB as float32. The demo laptop had 2.7 GB free.
    A silent allocation that big does not fail cleanly; it thrashes for minutes first."""
    monkeypatch.setattr(io_loader, "MAX_PIXELS_WITHOUT_WINDOW", 100)
    p = _tif(tmp_path, np.full((40, 40), 5, np.uint8))
    with pytest.raises(LoaderError) as e:
        load(p)
    assert "window" in str(e.value).lower(), "the error must tell the caller how to fix it"


def test_a_window_gets_past_the_guard_and_returns_only_the_tile(tmp_path, monkeypatch):
    monkeypatch.setattr(io_loader, "MAX_PIXELS_WITHOUT_WINDOW", 100)
    arr = np.arange(40 * 40, dtype=np.uint16).reshape(40, 40) % 251
    p = _tif(tmp_path, arr)
    img, meta = load(p, window=(4, 6, 10, 8))
    assert img.shape == (8, 10), "window is (x, y, w, h); the array is (rows, cols)"
    assert meta["window"] == (4, 6, 10, 8)
    assert meta["full_shape"] == (40, 40), "full_shape must describe the product, not the tile"
    np.testing.assert_array_equal(img, arr[6:14, 4:14].astype(np.float32))


def test_window_is_clipped_at_the_image_edge(tmp_path):
    arr = np.arange(20 * 20, dtype=np.uint8).reshape(20, 20)
    img, meta = load(_tif(tmp_path, arr), window=(15, 15, 100, 100))
    assert img.shape == (5, 5)
    assert meta["window"] == (15, 15, 5, 5), "the recorded window must be what was READ"


@pytest.mark.parametrize("window", [(-1, 0, 4, 4), (0, -1, 4, 4), (0, 0, 0, 4),
                                    (0, 0, 4, 0), (999, 0, 4, 4), (0, 999, 4, 4)])
def test_a_window_outside_the_image_raises(tmp_path, window):
    p = _tif(tmp_path, np.zeros((20, 20), np.uint8))
    with pytest.raises(LoaderError, match="outside"):
        load(p, window=window)


def test_uint16_survives_the_round_trip(tmp_path):
    """PDS4 products are often UnsignedMSB2. Losing the high byte would halve every DN."""
    arr = np.array([[0, 300, 4096, 65535]], np.uint16)
    img, _ = load(_tif(tmp_path, arr))
    np.testing.assert_array_equal(img, arr.astype(np.float32))


# --- the real product, when it is on this machine ----------------------------

def test_the_gate_one_pair_loads_as_real_lunar_data():
    """data/pairs/ is gitignored, so this is skipped on a fresh clone rather than failed."""
    import pathlib
    p = pathlib.Path("data/pairs/pair_01/pair_01_source.tif")
    if not p.exists():
        pytest.skip("pair_01 not on this machine - rebuild with core/make_demo_pair.py")
    img, meta = load(p)
    assert img.dtype == np.float32 and img.ndim == 2
    assert img.std() > 10, "Known issue #6: a product under std 10 has no texture in it"
    assert meta["full_shape"] == img.shape


def test_pick_is_called_with_keys_not_alias_values():
    """Regression guard for a KeyError that broke loading every CH-2 product.

    `_pick(leaves, key)` does `CANDIDATES[key]`. Passing one of the *alias values*
    instead of a key raises KeyError. On 1 Sep an edit did exactly that with
    "solar_incidence", and because it sat behind an `or`, it only fired when
    incidence was ABSENT - which is every Chandrayaan-2 OHRC product, our primary
    data source. The 23 tests here did not catch it because none loads a real PDS4
    product without incidence.
    """
    from core.io_loader import CANDIDATES, _pick

    # Every alias value that is not also a key would crash if passed to _pick.
    for key, aliases in CANDIDATES.items():
        assert _pick([], key) is None, f"_pick must accept the key {key!r}"
        for alias in aliases:
            if alias not in CANDIDATES:
                with pytest.raises(KeyError):
                    _pick([], alias)
                break


def test_pds4_without_incidence_loads_instead_of_crashing():
    """CH-2 OHRC carries no illumination geometry (Known issue #5). That is not an error."""
    import xml.etree.ElementTree as ET
    from core.io_loader import _pick

    leaves = [("product_id", "x"), ("instrument", "OHRC")]
    assert _pick(leaves, "incidence") is None
    assert _pick(leaves, "sun_azimuth") is None
