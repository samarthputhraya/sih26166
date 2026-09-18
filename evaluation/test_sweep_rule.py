"""The real sun sweep's judging rule (ops/sun_sweep.py, v2), on the cases that changed it.

Lives here because `ops/` is not in pytest's testpaths; the rule decides labels that
REPORT.md prints, so it is evidence code and is tested like it.
"""
from ops.sun_sweep import classify, outcomes_v2

LOFTR = "loftr+magsac++"
FALLBACK = "fft_phase_correlation (fallback)"


def test_inverted_shading_at_opposite_sun_is_a_correct_alignment():
    # site_ohrc_m1369217819re_w03_sw: 1,365 inliers, NCC -0.67 vs archive -0.41, refused
    assert classify(-0.67, -0.41, FALLBACK, "contradicted", True) == "false_alarm"


def test_matcher_as_good_as_the_archive_is_not_a_failure():
    # site_ohrc_m187919735re_w01_sw: 3.5 m from the archive geometry, NCC 0.42 vs 0.39
    assert classify(0.42, 0.39, LOFTR, "agrees", True) == "correct_accepted"


def test_when_neither_alignment_correlates_the_image_cannot_judge():
    # site_ohrc_m1531872919re_w03_sw: 0.07 vs 0.05
    assert classify(0.07, 0.05, LOFTR, "unconfirmed", True) == "inconclusive"
    assert classify(-0.19, -0.26, FALLBACK, "contradicted", True) == "inconclusive"


def test_archive_clearly_better_means_the_matcher_failed():
    assert classify(0.10, 0.60, FALLBACK, "contradicted", True) == "caught_failure"
    assert classify(0.35, 0.60, LOFTR, "agrees", True) == "missed_failure"


def test_no_transform_stays_no_transform():
    assert classify(None, 0.5, "none", None, False) == "no_transform"


def test_outcomes_v2_reads_the_logged_ncc_and_leaves_the_logged_label_alone():
    real = [{"pair_id": "p1", "outcome": "caught_failure", "method_declared": FALLBACK,
             "verdict": "contradicted"},
            {"pair_id": "p2", "outcome": "", "method_declared": LOFTR, "verdict": "agrees"}]
    res = [{"pair_id": "p1", "notes": "sun sweep: ...; NCC matcher-warp -0.61 vs "
                                      "archive-aligned -0.4; declared ..."}]
    assert outcomes_v2(real, res) == {"p1": "false_alarm"}
    assert real[0]["outcome"] == "caught_failure"
