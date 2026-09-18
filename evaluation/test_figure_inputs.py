"""Which results_log rows the deck's sun-angle figure reads (presentation/make_figures.py).

`presentation/` is not in pytest's testpaths, and on 18 Sep a new kind of row (synthetic
viewpoint, same `d_azimuth=15deg` in its config) silently moved fig1's 15-degree median
from 0.086 to 0.272 px. The selector is tested here so the next new row type cannot.
"""
import pytest

F = pytest.importorskip("presentation.make_figures")


def test_nadir_synthetic_rows_are_read_by_sun_delta():
    assert F._delta({"tier": "synthetic", "config": "... d_azimuth=15deg at fixed 30deg"}) == 15.0


def test_viewpoint_rows_never_enter_the_sun_angle_curve():
    cfg = "... d_azimuth=15deg at fixed 30deg ...; VIEWPOINT tilt=30deg toward image azimuth 0deg"
    assert F._delta({"tier": "synthetic viewpoint", "config": cfg}) is None
    assert F._delta({"tier": "synthetic", "config": cfg}) is None
