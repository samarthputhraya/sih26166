"""The freeze's work list comes from the evidence, by exact id - pinned here without running anything."""
from ops.freeze import latest_real, plan_real, stale_real


def _row(pid, cmd, commit="aaa1111", verdict="agrees"):
    return {"pair_id": pid, "command": cmd, "git_commit": commit, "verdict": verdict, "seconds": "10"}


ROWS = [
    _row("site_ohrc_m1153871873le_w01", "python -m ops.run_real_pairs site_ohrc_m1153871873le_w* --log"),
    _row("site_ohrc_m1153871873le_w01_sw", "python -m ops.sun_sweep --windows 3 --log"),
    _row("site_ohrc_m1153871873le_w01_sw", "python -m ops.sun_sweep --windows 3 --log --rerun",
         commit="bbb2222"),
    _row("loop_a_b_w01_t", "python -m ops.loop_closure --a A --b B --tag t --log"),
    _row("loop_a_b_w02_t", "python -m ops.loop_closure --a A --b B --tag t --log"),
    _row("sac_tmc_fore_aft_w01", "manual invalidation (see notes)", verdict="INVALIDATED"),
]


def test_sweep_windows_never_go_through_run_real_pairs():
    p = plan_real(ROWS)
    ids = [i for v in p["real"].values() for i in v]
    assert ids == ["site_ohrc_m1153871873le_w01"]          # the glob would have caught _sw too
    assert p["sweep"] == {"M1153871873LE"}
    assert p["loops"] == ["python -m ops.loop_closure --a A --b B --tag t --log"]


def test_withdrawn_pairs_are_not_rerun_and_latest_row_decides_staleness():
    assert "sac_tmc_fore_aft_w01" not in latest_real(ROWS)
    stale = stale_real("bbb2222", ROWS)
    assert "site_ohrc_m1153871873le_w01_sw" not in stale    # its LATEST row is at bbb2222
    assert "site_ohrc_m1153871873le_w01" in stale
