"""ops/ortho_tmc.py: the DTM sampler, the viewing geometry and the orthorectified frame (no data)."""
import datetime as dt
import math

import numpy as np
import pytest

from ops import ortho_tmc as O


def _dtm(h, lat0=1.0, lon0=0.0, step=0.01):
    d = O.Dtm.__new__(O.Dtm)                       # no file: the sampler alone
    d.h, d.lon0, d.dlon, d.lat0, d.dlat = np.asarray(h, float), lon0, step, lat0, -step
    return d


def test_dtm_is_bilinear_between_pixel_centres_and_nan_outside():
    d = _dtm([[0, 10], [20, 30]])
    # pixel (0, 0) centre: lat 1 - 0.005, lon 0.005; halfway to (1, 1)
    assert float(d(1 - 0.005, 0.005)) == pytest.approx(0)
    assert float(d(1 - 0.01, 0.01)) == pytest.approx(15)
    assert np.isnan(d(5.0, 5.0))


def _base(step=100, n=5, gsd=5.0):
    from core import geometry as G
    xs = ys = np.arange(n) * float(step)
    gx, gy = np.meshgrid(xs, ys)
    return G.Frame("t", (int(ys[-1]) + 1, int(xs[-1]) + 1), xs, ys, gx * gsd, -gy * gsd, source="test")


class _Proj:      # map metres <-> a fake lat/lon that the DTM stub reads back as metres
    def inv(self, x, y):
        return np.asarray(y, float), np.asarray(x, float)


def test_flat_ground_and_lattice_relief_give_back_the_lattice():
    base = _base()
    dtm = lambda lat, lon: np.full(np.shape(lat), -950.0)  # noqa: E731 - the lattice carries it all
    f = O.OrthoFrame(base, _Proj(), dtm, 28.0, 185.0)
    X, Y = np.array([737.0, 1210.0]), np.array([-333.0, -1500.0])
    assert np.allclose(f.from_map(X, Y), base.from_map(X, Y), atol=1e-6)


def test_relief_between_lattice_nodes_moves_the_pixel_away_from_the_spacecraft():
    base = _base()
    bump = (1250.0, -1250.0)                         # a 40 m hill midway between lattice nodes
    dtm = lambda lat, lon: 40.0 * (np.hypot(np.asarray(lon) - bump[0], np.asarray(lat) - bump[1]) < 1)  # noqa: E731
    e, a = 30.0, 90.0                                # spacecraft due east, 30 deg off vertical
    f = O.OrthoFrame(base, _Proj(), dtm, e, a)
    x, y = f.from_map(np.array([bump[0]]), np.array([bump[1]]))
    k = 40.0 * math.tan(math.radians(e))             # the lattice put the hilltop k m WEST (away)
    xb, yb = base.from_map(np.array([bump[0] - k]), np.array([bump[1]]))
    assert (float(x[0]), float(y[0])) == pytest.approx((float(xb[0]), float(yb[0])), abs=1e-6)


def test_view_geometry_from_an_orbit_record():
    t0 = dt.datetime(2025, 7, 7, 18, 53, 5)
    # spacecraft 100 km up, 1 degree of latitude north of a ground point on the equator
    records = [(t0, 1.0, 0.0, 100.0)]

    class _Xml:
        def read_text(self, encoding=None):
            return ("<start_date_time>2025-07-07T18:53:05Z</start_date_time>"
                    "<stop_date_time>2025-07-07T18:53:05Z</stop_date_time><elements>1</elements>")
    e, a, dt_s = O.view(records, _Xml(), 0, 0.0, 0.0)
    assert a == pytest.approx(0.0, abs=1e-6) or a == pytest.approx(360.0, abs=1e-6)
    assert 10 < e < 20 and dt_s == 0
