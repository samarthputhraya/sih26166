"""`is_inlier` in the exported match table must be MAGSAC++'s answer, not a float comparison.

The bug this pins (found 20 Sep 2026): `core.ransac.filter_matches` casts to float32 because cv2
requires it, while the points it is given are float64 from `core.scale.to_original`. Deciding
which rows were inliers by comparing those coordinates therefore worked only when the float64
value happened to be exactly representable in float32 - true for some reference grids and false
for others. On 41 of 183 exported bundles it flagged ZERO inliers out of thousands, which emptied
`gcps.txt`, `gcps.points` and `matches_isis.csv` - three of the deliverables the problem statement
names - while every logged metric stayed correct, because nothing else asks this question.
"""
import numpy as np

from core.export import match_table, write_isis_csv
from core.ransac import filter_matches


def _pair(n=60, seed=0):
    rng = np.random.default_rng(seed)
    src = rng.uniform(0, 500, (n, 2))
    ref = src + np.array([3.0, -2.0])
    ref[::5] += rng.uniform(40, 80, (len(ref[::5]), 2))      # every fifth match is an outlier
    return src, ref


def _result(src, ref):
    src_in, ref_in, H, info = filter_matches(src, ref)
    return {"src_matches": src, "ref_matches": ref, "src_inliers": src_in, "ref_inliers": ref_in,
            "H": H, "ransac": info, "reliability": None, "shape_reference": (512, 512),
            "match_scores": None}, info


def test_filter_matches_reports_which_rows_it_kept():
    src, ref = _pair()
    _, _, _, info = filter_matches(src, ref)
    keep = info["inlier_mask"]
    assert keep.dtype == bool and keep.shape == (len(src),)
    assert int(keep.sum()) == info["inlier_count"]


def test_the_flag_survives_coordinates_that_do_not_round_trip_through_float32():
    """The failing case, reproduced: float64 points whose float32 copy differs."""
    src, ref = _pair()
    # a scale factor that is not a power of two, exactly as core.scale.to_original produces
    src = (src + 0.5) / 4.98 - 0.5
    ref = (ref + 0.5) / 1.337 - 0.5
    assert not np.array_equal(src, src.astype(np.float32).astype(np.float64)), \
        "this test needs points that lose bits in float32, or it proves nothing"
    result, info = _result(src, ref)
    rows = match_table(result)
    flagged = sum(r["is_inlier"] for r in rows)
    assert flagged == info["inlier_count"] > 0, (
        f"match_table flagged {flagged} inliers, MAGSAC++ kept {info['inlier_count']}")
    assert [bool(r["is_inlier"]) for r in rows] == list(info["inlier_mask"])


def test_the_flag_is_right_when_the_coordinates_do_round_trip():
    src, ref = _pair(seed=3)
    src, ref = src.astype(np.float32).astype(np.float64), ref.astype(np.float32).astype(np.float64)
    result, info = _result(src, ref)
    flagged = sum(r["is_inlier"] for r in match_table(result))
    assert flagged == info["inlier_count"] > 0


def test_a_result_pickled_before_the_mask_existed_still_flags_its_inliers():
    """Old demo caches hold result dicts with no mask; they must not silently lose every flag."""
    src, ref = _pair(seed=5)
    src, ref = src.astype(np.float32).astype(np.float64), ref.astype(np.float32).astype(np.float64)
    result, info = _result(src, ref)
    result["ransac"] = {k: v for k, v in info.items() if k != "inlier_mask"}
    flagged = sum(r["is_inlier"] for r in match_table(result))
    assert flagged == info["inlier_count"] > 0


def test_the_isis_match_list_is_not_empty_when_there_are_inliers(tmp_path):
    src, ref = _pair()
    src = (src + 0.5) / 4.98 - 0.5
    result, info = _result(src, ref)
    p = write_isis_csv(tmp_path / "m.csv", match_table(result), "S", "R")
    data = [ln for ln in p.read_text(encoding="utf-8").splitlines()
            if ln and not ln.startswith("#") and not ln.startswith("point_id")]
    assert len(data) == info["inlier_count"] > 0
