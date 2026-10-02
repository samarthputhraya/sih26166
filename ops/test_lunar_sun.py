"""The Sun over the Moon from first principles, checked against LROC's published sub-solar points;
and the footprint overlap the reference finder ranks by."""
import pytest

from ops import find_reference as F
from ops.lunar_sun import sun_angle_between, sun_at, subsolar

# (NAC, start time UTC, LROC's sub-solar latitude, longitude east, its centre lat, lon, incidence there)
# - copied from LROC's product pages (data.lroc.im-ldi.com/lroc/view_lroc/...), so the test needs no data.
LROC = (("M1350459544RE", "2020-07-27T03:24:37", 0.91, 96.55, -14.44, 25.24, 72.16),
        ("M165491149RE", "2011-07-16T21:31:22", -0.87, 345.16, None, None, None),
        ("M1391535070LE", "2021-11-14T13:16:43", 0.25, 60.21, -13.73, 25.04, 37.53),
        ("M1258792259LE", "2017-08-31T04:16:32", 0.37, 69.63, None, None, 46.16))


@pytest.mark.parametrize("pid,t,slat,slon,clat,clon,inc", LROC)
def test_the_subsolar_point_matches_lroc(pid, t, slat, slon, clat, clon, inc):
    lat, lon = subsolar(t)
    assert lat == pytest.approx(slat, abs=0.1), pid
    assert (lon - slon + 180) % 360 - 180 == pytest.approx(0.0, abs=0.1), pid
    if clat is not None:
        i, _az = sun_at(t, clat, clon)
        assert i == pytest.approx(inc, abs=0.1), pid


def test_the_same_time_is_the_same_light_and_half_a_lunation_is_opposite():
    assert sun_angle_between("2020-07-27T03:24:37", "2020-07-27T03:24:37", -14.4, 25.2) == pytest.approx(0, abs=1e-6)
    # about 14.77 days later the Sun stands on the other side of the sky at the equator
    assert sun_angle_between("2020-07-27T03:24:37", "2020-08-10T21:55:00", 0.0, 25.2) > 150


def test_overlap_of_two_offset_squares():
    sq = [(0.0, 0.0), (0.0, 1.0), (-1.0, 1.0), (-1.0, 0.0)]            # (lat, lon) corners, 1 deg square
    half = [(0.0, 0.5), (0.0, 1.5), (-1.0, 1.5), (-1.0, 0.5)]          # shifted half a square east
    assert F.overlap_fraction(sq, sq, -0.5, 0.5) == pytest.approx(1.0, abs=1e-6)
    assert F.overlap_fraction(sq, half, -0.5, 0.5) == pytest.approx(0.5, abs=0.01)
    far = [(10.0, 10.0), (10.0, 11.0), (9.0, 11.0), (9.0, 10.0)]
    assert F.overlap_fraction(sq, far, -0.5, 0.5) == 0.0


def test_corner_order_does_not_matter():
    sq = [(0.0, 0.0), (0.0, 1.0), (-1.0, 1.0), (-1.0, 0.0)]
    assert F.overlap_fraction(sq, sq[::-1], -0.5, 0.5) == pytest.approx(1.0, abs=1e-6)


def test_overlap_across_the_zero_meridian():
    a = [(1.0, 359.5), (1.0, 0.5), (0.0, 0.5), (0.0, 359.5)]
    b = [(1.0, -0.5), (1.0, 0.5), (0.0, 0.5), (0.0, -0.5)]
    assert F.overlap_fraction(a, b, 0.5, 0.0) == pytest.approx(1.0, abs=1e-6)
