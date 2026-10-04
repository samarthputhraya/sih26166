"""Quarter windows cover the parent window's ground exactly, source and reference alike."""
import json

import numpy as np

from ops import split_windows as W


def _pair(tmp_path, pid, n_ref=64, n_src=64):
    from core import geometry as G
    d = tmp_path / pid
    d.mkdir()
    rt = [1000.0, 6.0, 0.0, 2000.0, 0.0, -6.0]
    st = [1000.0, 6.0, 0.0, 2000.0, 0.0, -6.0]
    G.write_geotiff(d / f"{pid}_ref.tif", np.arange(n_ref * n_ref, dtype=np.float32).reshape(n_ref, n_ref), rt)
    G.write_geotiff(d / f"{pid}_source.tif", np.arange(n_src * n_src, dtype=np.float32).reshape(n_src, n_src), st)
    g = {"pair_id": pid, "crs": "Moon sphere 1737.4 km / local equirectangular (lat_ts -13.0, lon_0 25.0)",
         "window_centre_map_m": [1000 + 32 * 6, 2000 - 32 * 6], "window_centre_latlon": [-13.0, 25.0],
         "window_m": 384.0, "source": {"transform": st, "shape": [n_src, n_src]},
         "reference": {"transform": rt, "shape": [n_ref, n_ref]}}
    (d / "geometry_prior.json").write_text(json.dumps(g), encoding="utf-8")


def test_quarters_tile_the_parent(tmp_path, monkeypatch):
    monkeypatch.setattr(W, "PAIRS", tmp_path)
    _pair(tmp_path, "parent_w01")
    ids = W.split("parent_w01", "q")
    assert ids == ["q_w01_q11", "q_w01_q12", "q_w01_q21", "q_w01_q22"]
    xs = set()
    for pid in ids:
        g = json.loads((tmp_path / pid / "geometry_prior.json").read_text(encoding="utf-8"))
        assert g["reference"]["shape"] == [32, 32] and g["source"]["shape"] == [32, 32]
        # source and reference start on the same ground
        assert g["source"]["transform"][0] == g["reference"]["transform"][0]
        assert g["source"]["transform"][3] == g["reference"]["transform"][3]
        xs.add((g["reference"]["transform"][0], g["reference"]["transform"][3]))
        lat, lon = g["window_centre_latlon"]
        assert abs(lat + 13.0) < 0.01 and abs(lon - 25.0) < 0.01
    assert xs == {(1000.0, 2000.0), (1192.0, 2000.0), (1000.0, 1808.0), (1192.0, 1808.0)}
