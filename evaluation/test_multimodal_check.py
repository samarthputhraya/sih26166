"""ops/multimodal_check.py: the infrared fallback measured against the visible-band registration.

Lives here because `ops/` is not in pytest's testpaths; the numbers it logs reach REPORT.md.
"""
import json

import numpy as np

from ops.multimodal_check import FIELDS, check_one, disagreement, log_rows, pairings


def test_pairings_match_1548_to_749_and_iirs_bands_only_when_both_exist():
    latest = {"site_tc_morning_mi1548_w01": {}, "site_tc_morning_mi749_w01": {},
              "site_tc_morning_mi1548_w02": {},                       # no 749 partner
              "site_tc_ortho_iirs1000_w05": {}, "site_tc_ortho_iirs1555_w05": {},
              "site_ohrc_m1153871873le_w01": {}}
    got = {(p["pair_id"], p["against"], p["kind"]) for p in pairings(latest)}
    assert got == {("site_tc_morning_mi1548_w01", "site_tc_morning_mi749_w01", "tc-mi"),
                   ("site_tc_ortho_iirs1000_w05", "site_tc_ortho_iirs1555_w05", "tc-iirs")}


def test_disagreement_of_a_pure_translation_is_that_translation():
    H = np.eye(3)
    T = np.array([[1, 0, 3.0], [0, 1, -4.0], [0, 0, 1]])
    d = disagreement(T, H, (100, 100))
    assert abs(d["median_px"] - 5.0) < 1e-9 and abs(d["max_px"] - 5.0) < 1e-9
    assert abs(d["mean_dx_px"] - 3.0) < 1e-9 and abs(d["mean_dy_px"] + 4.0) < 1e-9
    assert disagreement(H, H, (50, 80))["max_px"] == 0.0


def _bundle(tmp_path, pid, H, sha="abc", transform=(0, 14.8, 0, 0, 0, -14.8), shape=(64, 64),
            declared="fft_phase_correlation (fallback)", verdict="contradicted", fallback=None):
    d = tmp_path / pid
    d.mkdir()
    (d / "report.json").write_text(json.dumps({
        "inputs": {"source": {"sha256": sha}, "reference": {"transform": list(transform), "shape": list(shape)}},
        "H_final": np.asarray(H).tolist(), "declared": {"method": declared},
        "trust": {"verdict": verdict}, "fallback": fallback}), encoding="utf-8")


def test_check_one_compares_only_bundles_cut_from_the_same_source_onto_the_same_grid(tmp_path):
    T = np.array([[1, 0, 1.0], [0, 1, 0.0], [0, 0, 1]])
    _bundle(tmp_path, "a_mi1548_w01", T, fallback={"ncc": 0.61, "spread_px": 18})
    _bundle(tmp_path, "a_mi749_w01", np.eye(3), declared="loftr+magsac++", verdict="agrees")
    _bundle(tmp_path, "b_mi1548_w01", T, sha="other")
    _bundle(tmp_path, "b_mi749_w01", np.eye(3))
    latest = {p: {"ref_gsd_m": "14.8", "window_lat": "-74.1", "window_lon": "43.5", "inliers": "313",
                  "archive_offset_m": "41.5"} for p in
              ("a_mi1548_w01", "a_mi749_w01", "b_mi1548_w01", "b_mi749_w01")}
    prs = {p["pair_id"]: p for p in pairings(latest)}
    row, note = check_one(prs["a_mi1548_w01"], latest, tmp_path)
    assert note == "ok"
    assert abs(row["disagreement_median_px"] - 1.0) < 1e-9
    assert abs(row["disagreement_median_m"] - 14.8) < 1e-9
    assert row["fallback_ncc"] == 0.61 and row["against_inliers"] == "313"
    row, note = check_one(prs["b_mi1548_w01"], latest, tmp_path)
    assert row is None and "not comparable" in note


def test_log_rows_writes_the_header_once_and_refuses_a_foreign_header(tmp_path):
    p = tmp_path / "mm.csv"
    log_rows([{"pair_id": "x", "against": "y"}], p)
    log_rows([{"pair_id": "x2", "against": "y2"}], p)
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(FIELDS) and len(lines) == 3
    p.write_text("pair_id,against\nx,y\n", encoding="utf-8")
    try:
        log_rows([{"pair_id": "z"}], p)
    except RuntimeError as e:
        assert "header" in str(e)
    else:
        raise AssertionError("a foreign header must be refused")
