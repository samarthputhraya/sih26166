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


def _loops_step(monkeypatch, rows, commit):
    """Freeze.loops on `rows`, with the log and the subprocess replaced: returns (result, commands run)."""
    import ops.freeze as F
    monkeypatch.setattr(F, "_rows", lambda p: rows)
    ran = []
    monkeypatch.setattr(F, "_run", lambda argv, logf: ran.append(" ".join(argv)) or 0)
    fz = F.Freeze.__new__(F.Freeze)
    fz.commit = commit
    return fz.loops(None), ran


def test_loops_step_reads_three_leg_commands_and_waits_for_their_legs(monkeypatch):
    legs_cmd = "python -m ops.loop_closure --legs siten_oa siten_ab siten_ob --log"
    rows = [_row("siten_oa_c01", "python -m ops.run_real_pairs siten_* --log", commit="new1234"),
            _row("siten_ab_c01", "python -m ops.run_real_pairs siten_* --log", commit="new1234"),
            _row("siten_ob_c01", "python -m ops.run_real_pairs siten_* --log", commit="new1234"),
            _row("loop_siten_oa_siten_ob_c01", legs_cmd)]
    ok, ran = _loops_step(monkeypatch, rows, "new1234")
    assert ok and ran == ["-m ops.loop_closure --legs siten_oa siten_ab siten_ob --log"]
    rows[1] = _row("siten_ab_c01", "python -m ops.run_real_pairs siten_* --log", commit="old0000")
    ok, ran = _loops_step(monkeypatch, rows, "new1234")
    assert ok is None and ran == []                          # a stale leg: run `real` first
