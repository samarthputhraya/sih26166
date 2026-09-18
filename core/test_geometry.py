"""Archive geometry: projection, frames, projection onto a map grid, coarse offsets.

All synthetic - no lunar files needed - so every check is against arithmetic.
"""
import numpy as np
import pytest

from core import geometry as G


def test_polar_stereo_round_trip_and_known_tile_corner():
    lat = np.array([-74.0, -73.5, -89.9, -60.0])
    lon = np.array([43.66, 350.0, 10.0, 180.0])
    x, y = G.ps_south(lat, lon)
    lat2, lon2 = G.ps_south_inv(x, y)
    assert np.allclose(lat2, lat, atol=1e-9) and np.allclose(lon2 % 360, lon % 360, atol=1e-9)
    # Kaguya TC1S2B0_01_03482S746E0433: upper-left tiepoint (293726.78, 371993.34) m lies
    # near 74.3 S, 38.3 E on the same sphere - the formula agrees with the GDAL-written tile.
    la, lo = G.ps_south_inv(293726.78456124, 371993.33526431)
    assert -74.6 < la < -74.0 and 37.5 < lo < 39.0


def _corner_frame(rows=4000, cols=500):
    return G.Frame.from_corners((-73.0, 43.0), (-73.0, 43.2), (-74.0, 44.0), (-74.0, 43.8),
                                (rows, cols), "test", step=128)


def test_corner_frame_hits_its_corners_and_inverts():
    f = _corner_frame()
    X, Y = f.to_map(np.array([0.0, 499.0]), np.array([0.0, 3999.0]))
    x_ul, y_ul = G.ps_south(-73.0, 43.0)
    x_lr, y_lr = G.ps_south(-74.0, 44.0)
    assert abs(X[0] - x_ul) < 1e-6 and abs(Y[0] - y_ul) < 1e-6
    assert abs(X[1] - x_lr) < 1e-6 and abs(Y[1] - y_lr) < 1e-6
    rng = np.random.default_rng(0)
    xs, ys = rng.uniform(1, 498, 200), rng.uniform(1, 3998, 200)
    bx, by = f.from_map(*f.to_map(xs, ys))
    assert np.nanmax(np.hypot(bx - xs, by - ys)) < 1e-4


def test_transform_frame_matches_the_geotiff_convention():
    tr = (1000.0, 2.0, 0.0, 5000.0, 0.0, -2.0)
    f = G.Frame.from_transform(tr, (100, 50))
    X, Y = f.to_map(np.array([0.0]), np.array([0.0]))
    assert X[0] == pytest.approx(1001.0) and Y[0] == pytest.approx(4999.0)   # pixel CENTRE


def test_project_reproduces_a_shifted_copy():
    """Project an image through a transform frame onto a grid offset by whole pixels."""
    rng = np.random.default_rng(1)
    img = rng.random((200, 200)).astype(np.float32)
    tr = (0.0, 1.0, 0.0, 200.0, 0.0, -1.0)
    f = G.Frame.from_transform(tr, img.shape)
    gt, shape = G.map_grid(10.0, 190.0, 100.0, 100.0, 1.0)
    out, ok = G.project(f, lambda x, y, w, h: img[y:y + h, x:x + w], gt, shape, coarse=8)
    assert ok.all()
    assert np.allclose(out, img[10:110, 10:110], atol=1e-4)


def test_fill_invalid_takes_the_nearest_valid_value():
    img = np.arange(16, dtype=np.float32).reshape(4, 4)
    ok = np.ones((4, 4), bool)
    ok[0, 0] = False
    out, n = G.fill_invalid(img, ok)
    assert n == 1 and out[0, 0] in (1.0, 4.0)


def test_affine_correction_is_recovered_through_outliers():
    rng = np.random.default_rng(2)
    P = rng.uniform(-5000, 5000, (60, 2))
    A = np.array([[0.002, -0.001, -140.0], [0.013, 0.0005, 10.0]])
    D = (np.c_[P - P.mean(0), np.ones(60)] @ A.T) + rng.normal(0, 3, (60, 2))
    D[:15] += rng.uniform(-300, 300, (15, 2))                      # a quarter are garbage
    fit = G.fit_affine_correction(P, D, thresh_m=12)
    assert fit["inliers"] >= 42
    Af = np.array(fit["A"])
    assert np.allclose(Af[:, 2], A[:, 2], atol=3) and np.allclose(Af[:, :2], A[:, :2], atol=5e-4)


def test_corrected_frame_moves_by_the_field():
    f = _corner_frame()
    M = {"A": [[0, 0, 12.5], [0, 0, -7.0]], "centre": [0.0, 0.0]}
    g = f.corrected(M)
    assert np.allclose(g.X - f.X, 12.5) and np.allclose(g.Y - f.Y, -7.0)


def test_coarse_offset_recovers_a_known_shift():
    rng = np.random.default_rng(3)
    base = rng.random((300, 300)).astype(np.float32)
    import cv2
    base = cv2.GaussianBlur(base, (0, 0), 2)
    a = np.roll(np.roll(base, -4, 0), 7, 1)[20:276, 20:276]
    b = base[20:276, 20:276]
    dx, dy, pk = G.coarse_offset(a, b, erode_px=0)
    assert abs(dx - 7) < 0.3 and abs(dy + 4) < 0.3 and pk > 0.3


def test_geotiff_written_here_reads_back_with_its_transform(tmp_path):
    from core.io_loader import load
    tr = (293726.78, 0.25, 0.0, 371993.34, 0.0, -0.25)
    p = G.write_geotiff(tmp_path / "t.tif", np.zeros((8, 8), np.float32), tr)
    _, meta = load(p)
    assert meta["transform"] == pytest.approx(tr)
    assert meta["gsd_mpp"] == pytest.approx(0.25)
    assert "South Polar" in meta["crs"]
