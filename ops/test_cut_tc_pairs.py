"""ops/cut_tc_pairs.py and the WAC strip: geometry conventions that need no data."""
import numpy as np
import pytest


def test_tc_frame_pixel_centres_follow_the_pds_label():
    from ops import cut_tc_pairs as T
    from ops.cut_pradan_pairs import LocalEqc
    lat, lon = -13.5, 25.2
    proj = LocalEqc(lat, lon)
    f = T.tc_frame(proj, lat, lon, 1500.0)
    # pixel (col, row) centre is at lat = MAX_LAT - row / PPD, lon = WEST_LON + col / PPD
    row, col = (T.MAX_LAT - lat) * T.PPD, (lon - T.WEST_LON) * T.PPD
    x, y = f.from_map(*proj.fwd(np.array([lat]), np.array([lon])))
    assert (float(x[0]), float(y[0])) == pytest.approx((col, row), abs=1e-3)


def test_wac_strip_windows_are_big_enough_for_every_square_to_vote():
    from core.reliability import MIN_CELL_SIDE_PX
    from ops import cut_wac_pairs as W
    assert W.STRIP_PX / 8 >= MIN_CELL_SIDE_PX
    # the chain-sized windows are not, which is why their verdicts are whole-frame
    assert round(16065 / W.WAC_GSD) / 8 < MIN_CELL_SIDE_PX
