"""Classical baselines on the real pairs: which windows each axis takes, and the one acceptance rule."""
from ops import classical_real as C


def _row(pid, verdict="agrees", declared="loftr+magsac++", d_az="3.0", notes=""):
    return {"pair_id": pid, "verdict": verdict, "method_declared": declared, "d_sun_azimuth_deg": d_az,
            "notes": notes}


def test_accepted_means_the_area_check_agrees_and_no_fallback_was_needed():
    assert C.accepted("agrees", "sift+magsac++")
    assert not C.accepted("agrees", "fft_phase_correlation (fallback)")
    assert not C.accepted("unconfirmed", "orb+magsac++")
    assert not C.accepted("contradicted", "akaze+magsac++")
    assert C.ours_accepted(_row("x"))
    assert not C.ours_accepted(_row("x", declared="fft_phase_correlation (fallback)"))


def test_each_axis_takes_its_own_windows_and_the_ladder_splits_by_sun_azimuth():
    latest = {p: _row(p) for p in ("sac_ohrc_nac_w01", "sac_ohrc_nac112_w01", "sac_ohrc_nac_w01_sw",
                                   "siten_ohrc2031_tmc20200607_c00", "chain_tmc20200203_iirs1555_w01",
                                   "chain_tmc20200203_iirs746_w01", "wac_iirs20200607_1555_w01",
                                   "wacstrip_iirs20200607_1555_s002", "tcmap_tmc20250707_s001",
                                   "sac_tmcfore_tmcaft_dtm_w01", "sac_tmcfore_tmcaft_w01")}
    latest["sac_ohrclroc_nacm1_c00"] = _row("sac_ohrclroc_nacm1_c00", d_az="12.0")
    latest["sac_ohrclroc_nacm2_c00"] = _row("sac_ohrclroc_nacm2_c00", d_az="170.0")
    got = dict(C.axis_pairs(latest))
    labels = [a[0] for a in C.AXES]
    assert got[labels[0]] == ["sac_ohrc_nac_w01"]                  # never the _sw copy, never nac112
    assert got[labels[1]] == ["sac_ohrc_nac112_w01"]
    assert got[labels[2]] == ["sac_ohrclroc_nacm1_c00"] and got[labels[3]] == ["sac_ohrclroc_nacm2_c00"]
    assert got[labels[8]] == ["chain_tmc20200203_iirs1555_w01"]    # 746 nm is the visible control
    assert got[labels[9]] == ["chain_tmc20200203_iirs746_w01"]
    assert got[labels[10]] == ["wac_iirs20200607_1555_w01"]          # IIRS onto the WAC mosaic
    assert got[labels[11]] == ["wacstrip_iirs20200607_1555_s002"]
    assert got[labels[12]] == ["tcmap_tmc20250707_s001"]
    assert got[labels[13]] == ["sac_tmcfore_tmcaft_dtm_w01"]         # never the un-orthorectified pair


def test_invalidated_rows_never_reach_an_axis(tmp_path):
    log = tmp_path / "real.csv"
    log.write_text("pair_id,notes,verdict,method_declared,d_sun_azimuth_deg\n"
                   "sac_ohrc_nac_w01,,agrees,loftr+magsac++,173.5\n"
                   "sac_ohrc_nac_w02,INVALIDATED: test,agrees,loftr+magsac++,173.6\n", encoding="utf-8")
    assert list(C.latest_real(log)) == ["sac_ohrc_nac_w01"]


def test_the_notes_tail_round_trips():
    j = {"verdict": "contradicted", "declared": "fft_phase_correlation (fallback)", "accepted": False,
         "verified": 0, "weak": 3, "no_evidence": 61, "n_matches": 27, "inliers": 4, "residual_median_px": 31.5,
         "holdout_inlier_frac": 0.12, "seconds": 3.5, "error": None}
    p = C.parse_notes(C.notes_of(j, "abc1234"))
    assert p["verdict"] == "contradicted" and p["accepted"] == "False" and p["commit"] == "abc1234"
    assert p["residual_median_px"] == "31.5000" and p["error"] == "None"
