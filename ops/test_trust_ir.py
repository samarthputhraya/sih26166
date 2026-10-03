"""The visible-infrared trust population stays out of the panchromatic calibration's way."""
from ops import trust_real_calibration as T


def test_its_own_file_windows_and_sizes():
    assert T.OUT_CSV_IR != T.OUT_CSV
    assert not set(T.IR_WINDOWS) & set(T.EXTRA_WINDOWS)
    assert T.IR_DISPLACEMENTS_PX[0] == 0 and T.IR_DISPLACEMENTS_PX == sorted(T.IR_DISPLACEMENTS_PX)


def test_reference_index_counts_other_orbits_separately():
    from ops.reference_index import summary
    idx = {"targets": [
        {"time": "2020-01-01T00:00:00Z", "candidates": [
            {"time": "2020-01-01T00:00:30Z", "sun_angle": 0.1, "instrument": "TMC-2"},     # same pass
            {"time": "2020-01-02T00:00:00Z", "sun_angle": 7.0, "instrument": "OHRC"}]},   # another orbit
        {"time": "2020-01-01T00:00:00Z", "candidates": []}]}
    s = summary(idx)
    assert (s["n"], s["within_5"], s["other_orbit_within_5"], s["other_orbit_within_10"], s["none"]) == (2, 1, 0, 1, 1)


def test_every_file_the_trust_step_writes_is_an_evidence_log():
    """An evidence file missing from EVIDENCE_LOGS stamps every later row of a freeze `-dirty`."""
    from core.export import EVIDENCE_LOGS
    root = T.ROOT
    for p in (T.OUT_CSV, T.OUT_CSV_IR):
        assert p.relative_to(root).as_posix() in EVIDENCE_LOGS
