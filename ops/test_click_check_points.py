"""The check-point click tool: independent of every registration, and it saves what is clicked."""
import ast
import json
import pathlib
import types

import numpy as np
import pytest

TOOL = pathlib.Path(__file__).resolve().parent / "click_check_points.py"


def test_the_tool_never_reads_a_registration():
    """A check point is only independent if the tool that makes it knows nothing of the result it
    will judge: no pipeline, matcher or export import, and no registration file named."""
    src = TOOL.read_text(encoding="utf-8")
    tree = ast.parse(src)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add(node.module or "")
    assert not any(m.startswith(("core", "baselines", "app")) for m in mods), mods
    assert mods & {"evaluation.check_points"}
    for word in ("report.json", "real_pairs_log", "H_final", "H_matcher", "results_log"):
        assert word not in src, word


def _fake_pair(tmp_path, pid="t_w01"):
    import tifffile
    d = tmp_path / pid
    d.mkdir()
    rng = np.random.default_rng(0)
    tifffile.imwrite(str(d / f"{pid}_source.tif"), rng.random((200, 200), dtype=np.float32))
    tifffile.imwrite(str(d / f"{pid}_ref.tif"), rng.random((100, 100), dtype=np.float32))
    (d / "geometry_prior.json").write_text(json.dumps({
        "source": {"resampled_gsd_mpp": 0.5}, "reference": {"resampled_gsd_mpp": 1.0},
        "prior_H_source_to_reference": [[0.5, 0, 0], [0, 0.5, 0], [0, 0, 1]]}), encoding="utf-8")
    return d


def test_a_simulated_session_writes_points_and_repeats(tmp_path, monkeypatch):
    pytest.importorskip("tifffile")
    monkeypatch.setenv("LUNAXX_CLICK_BACKEND", "Agg")
    from evaluation import check_points as C
    from ops import click_check_points as T
    _fake_pair(tmp_path)
    monkeypatch.setattr(T, "pair_paths", lambda pid: C.pair_paths(pid, tmp_path))
    monkeypatch.setattr(T, "CP_DIR", tmp_path / "cp")

    def ev(ax, x, y):
        return types.SimpleNamespace(inaxes=ax, xdata=x, ydata=y)

    c = T.Clicker("t_w01", "tester")
    # the source panel starts where the ARCHIVE prior puts the reference centre
    assert c.src_focus == pytest.approx((100.0, 100.0))
    for k, (u, v) in enumerate([(20, 30), (60, 70), (80, 15)]):
        c.on_click(ev(c.aR, u, v))
        assert c.src_focus == pytest.approx((2 * u, 2 * v))
        c.on_click(ev(c.aRz, u + 0.4, v - 0.2))
        c.on_click(ev(c.aSz, 2 * u + 1.0, 2 * v))
        c.accept()
    rows = C.read_csv(tmp_path / "cp" / "t_w01.csv")
    assert [r["point_id"] for r in rows] == ["p001", "p002", "p003"]
    assert float(rows[0]["ref_x"]) == pytest.approx(20.4) and float(rows[0]["src_x"]) == pytest.approx(41.0)
    c.drop_last()
    assert len(C.read_csv(tmp_path / "cp" / "t_w01.csv")) == 2
    c.plt.close(c.fig)

    r = T.Clicker("t_w01", "tester", repeat=1)
    first = r.queue[0]["point_id"]
    # the repeat circle names the feature without giving away the old click: its centre (and the zoom's)
    # sits 1.5-3 px from it, the same every time for the same point
    old = (float(r.queue[0]["ref_x"]), float(r.queue[0]["ref_y"]))
    off = np.hypot(r.ref_focus[0] - old[0], r.ref_focus[1] - old[1])
    assert T.HINT_OFFSET[0] <= off <= T.HINT_OFFSET[1]
    assert r.hint(r.queue[0]) == r.ref_focus == r.hint(dict(r.queue[0]))
    r.on_click(ev(r.aRz, 21.0, 30.0))
    r.on_click(ev(r.aSz, 41.0, 61.0))
    r.accept()
    rows = C.read_csv(tmp_path / "cp" / "t_w01.csv")
    assert rows[-1]["repeat_of"] == first
    loaded = C.load("t_w01", tmp_path / "cp", tmp_path)
    assert len(loaded["icp"]) == 2 and len(loaded["repeats"]) == 1
