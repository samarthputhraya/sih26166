"""ops/cut_wac_pairs.py: the WAC mosaic's pixel <-> lat/lon and the chunk reader (no network)."""
import numpy as np
import pytest

from ops import cut_wac_pairs as W


def test_pixel_centres_match_the_files_geotransform():
    # the mosaic spans 360 x 180 deg: (0, 0) sits at its centre; the corners are pixel EDGES
    c, r = W._wac_rc(0.0, 0.0)
    assert c == pytest.approx(W.WAC_SHAPE[1] / 2 - 0.5, abs=0.05)
    assert r == pytest.approx(W.WAC_SHAPE[0] / 2 - 0.5, abs=0.05)
    # one pixel is 100 m on the 1737.4 km sphere, east is +col, north is -row; 354.8 E == -5.2 E
    c1, r1 = W._wac_rc(np.degrees(100 / W.R), np.degrees(100 / W.R))
    assert (c1 - c, r1 - r) == pytest.approx((1.0, -1.0), abs=1e-6)
    assert W._wac_rc(10.0, 354.8) == pytest.approx(W._wac_rc(10.0, -5.2))


def test_reader_places_the_chunk_and_marks_no_data():
    a = np.arange(1, 13, dtype=np.uint8).reshape(3, 4)
    a[0, 0] = 0                                          # 0 is the mosaic's no-data
    read = W.wac_reader(a, r0=100, c0=200)
    out = read(199, 99, 3, 3)                             # one row and one column outside the chunk
    assert np.isnan(out[0]).all() and np.isnan(out[:, 0]).all()
    assert np.isnan(out[1, 1])                            # the no-data pixel
    assert out[1, 2] == 2 and out[2, 1] == 5 and out[2, 2] == 6


def test_frame_round_trip_on_a_local_grid():
    pytest.importorskip("scipy")
    from ops.cut_pradan_pairs import LocalEqc
    a = np.ones((80, 120), np.uint8)
    c, r = W._wac_rc(45.0, 10.0)
    r0, c0 = int(r) - 40, int(c) - 60
    f = W.wac_frame(a, r0, c0, LocalEqc(45.0, 10.0))
    X, Y = f.to_map(np.array([c]), np.array([r]))
    assert (float(X[0]), float(Y[0] - W.R * np.radians(45.0))) == pytest.approx((0.0, 0.0), abs=1.0)
    x, y = f.from_map(X, Y)
    assert (float(x[0]), float(y[0])) == pytest.approx((c, r), abs=1e-3)
