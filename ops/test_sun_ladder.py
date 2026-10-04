"""The Sun ladder names its legs so they never join another table, and composes them in order."""
import numpy as np

from ops import sun_ladder as S


ITEM = {"T": "M1386611320LE", "window": "w02"}


def test_leg_ids_one_and_two_steps():
    assert S.leg_ids(ITEM, ["M1258744166LE"]) == [
        "ladder_m1386611320le_w02_ohrc_m1258744166le", "ladder_m1386611320le_w02_m1258744166le"]
    assert S.leg_ids(ITEM, ["M1258744166LE", "M1113835448LE"]) == [
        "ladder_m1386611320le_w02_ohrc_m1258744166le",
        "ladder_m1386611320le_w02_m1258744166le_to_m1113835448le",
        "ladder_m1386611320le_w02_m1113835448le"]
    assert S.ladder_id(ITEM, ["M1258744166LE", "M1113835448LE"]) == \
        "ladder_m1386611320le_w02_via_m1258744166le_m1113835448le"


def test_every_ladder_id_starts_with_its_own_prefix():
    # REPORT keeps "ladder_" rows out of every count; the classical axes are anchored on other prefixes
    from ops.classical_real import AXES
    import re
    for pid in S.leg_ids(ITEM, ["M1", "M2"]) + [S.ladder_id(ITEM, ["M1"])]:
        assert pid.startswith("ladder_")
        assert not any(re.match(pat, pid) for _l, pat, _k in AXES)


def test_azimuth_difference_wraps():
    assert S._dz(350.7, 19.6) == 28.9 or abs(S._dz(350.7, 19.6) - 28.9) < 1e-9
    assert S._dz(10, 190) == 180
    assert S._dz(320, 287.6) == 32.39999999999998 or abs(S._dz(320, 287.6) - 32.4) < 1e-9


def test_disagreement_of_two_composites():
    T = np.eye(3)
    U = np.array([[1, 0, 3.0], [0, 1, 4.0], [0, 0, 1]])
    d = S._disagree(T, U, np.array([[0.0, 0.0], [10.0, 10.0]]), gsd=0.5)
    assert abs(d["rms_m"] - 5.0) < 1e-9 and abs(d["rms_px"] - 10.0) < 1e-9 and d["n"] == 2


def test_the_gap_and_links_stay_inside_the_verified_band():
    assert S.GAP == (60.0, 120.0)
    assert S.LINK_MAX_DEG <= 60.0
