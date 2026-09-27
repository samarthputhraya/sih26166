"""The workbench server's own logic: the pair library, the one-image known-answer test, and
the job lifecycle. No LoFTR here - a registration is replaced by a stand-in wherever one would
run, so these stay fast and never touch data/pairs or the weights."""
import base64
import json
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import cv2
import numpy as np
import pytest

from web import server


def _prior(root, pid, terminology, a="Chandrayaan-2 OHRC", b="LRO LROC NAC", rid="M1153871873LE", band=None):
    d = root / pid
    d.mkdir()
    ref = {"instrument": b, "product_id": rid}
    if band:
        ref["band"] = band
    (d / "geometry_prior.json").write_text(json.dumps(
        {"tier": "B", "terminology": terminology, "source": {"instrument": a}, "reference": ref}),
        encoding="utf-8")
    (d / f"{pid}_source.tif").write_bytes(b"")
    (d / f"{pid}_ref.tif").write_bytes(b"")


def test_library_takes_terminology_from_each_pair_prior(tmp_path):
    _prior(tmp_path, "site_ohrc_x_w03", "cross-sensor, cross-mission (OHRC vs NAC); both panchromatic")
    _prior(tmp_path, "site_tc_mi_w01", "cross-sensor and multi-modal: visible vs near-infrared",
           a="SELENE (Kaguya) Terrain Camera", b="SELENE (Kaguya) Multiband Imager", rid="MI_MAP",
           band="1548 nm (near-infrared)")
    _prior(tmp_path, "site_nac_nac_w02", "same sensor (LROC NAC) - a sun-angle test, NOT cross-sensor",
           a="LRO LROC NAC")
    (tmp_path / "no_prior_w01").mkdir()                     # skipped: nothing says what it is
    lib = {e["id"]: e for e in server.library(tmp_path)}
    assert set(lib) == {"site_ohrc_x_w03", "site_tc_mi_w01", "site_nac_nac_w02"}
    assert lib["site_ohrc_x_w03"]["tag"] == "cross-sensor, cross-mission"
    assert lib["site_ohrc_x_w03"]["window"] == 3 and lib["site_ohrc_x_w03"]["family"] == "site_ohrc_x"
    assert lib["site_ohrc_x_w03"]["label"].endswith("M1153871873LE")
    assert lib["site_tc_mi_w01"]["tag"] == "cross-sensor and multi-modal"
    assert lib["site_tc_mi_w01"]["group"] == "Kaguya TC → Kaguya MI 1548 nm"
    assert lib["site_nac_nac_w02"]["tag"] == "same sensor"          # never "cross-sensor"


def test_a_descriptive_band_is_not_shown_as_a_wavelength(tmp_path):
    _prior(tmp_path, "site_ohrc_lola_w01", "multi-modal: optical vs elevation", b="LRO LOLA (elevation, rendered)",
           rid="", band="shaded relief of the DEM, sun az 70.5 deg from north")
    (e,) = server.library(tmp_path)
    assert e["group"] == "OHRC → LOLA relief"


def test_known_transform_is_off_the_pixel_grid_and_reads_back_exactly():
    H, dx, dy = server.known_transform(640, 480, 10.0, 1.2, 30, -20)
    assert (dx, dy) == pytest.approx((30.37, -20.63))
    got = server.decompose(H, 640, 480)
    assert got["rot"] == pytest.approx(10.0, abs=1e-3)
    assert got["scale"] == pytest.approx(1.2, abs=1e-4)
    assert (got["dx"], got["dy"]) == pytest.approx((30.37, -20.63), abs=1e-3)


def test_grid_error_is_zero_for_the_truth_and_the_shift_for_a_shift():
    H, _, _ = server.known_transform(400, 400, 5, 1.0, 10, 10)
    assert server.grid_error(H, H, 400, 400) == {"rms": 0.0, "max": 0.0}
    off = H.copy()
    off[0, 2] += 3.0
    assert server.grid_error(off, H, 400, 400)["rms"] == pytest.approx(3.0)
    assert server.grid_error(None, H, 400, 400) is None


def _png(w, h, seed=0):
    img = (np.random.default_rng(seed).random((h, w)) * 255).astype(np.uint8)
    ok, buf = cv2.imencode(".png", cv2.GaussianBlur(img, (0, 0), 2))
    return {"name": "moon.png", "data": base64.b64encode(buf.tobytes()).decode()}


def test_known_pair_shrinks_a_large_upload_and_warps_it_by_the_truth(tmp_path):
    a, b, H, extra = server.known_pair(_png(1800, 1200), tmp_path, 0, 1.0, 20, 0)
    assert max(extra["w"], extra["h"]) == server.KNOWN_MAX_SIDE and extra["shrunk_from"] == [1800, 1200]
    import tifffile
    src, ref = tifffile.imread(str(a)), tifffile.imread(str(b))
    assert src.shape == ref.shape == (extra["h"], extra["w"])
    # source(p) = ref(H p): a pure shift of +20.37 px moves the reference left in the source
    assert np.allclose(src[100:200, 100:200], cv2.warpPerspective(ref, np.linalg.inv(H), ref.shape[::-1])[100:200, 100:200])


def test_known_pair_refuses_a_tiny_image(tmp_path):
    with pytest.raises(ValueError, match="96 px"):
        server.known_pair(_png(60, 60), tmp_path, 0, 1.0, 0, 0)


def test_start_job_validates_and_the_view_reports_progress():
    with pytest.raises(ValueError):
        server.start_job({"mode": "nope"})
    with pytest.raises(ValueError):
        server.start_job({"mode": "upload", "a": {}})
    done = threading.Event()

    def fake(job, body):
        job.update(stage="match", done=2, total=4)
        done.wait(2)
        job.update(state="done", stage="done", result={"id": "x"}, finished=time.time())

    job = server.start_job({"mode": "sample", "id": "anything"}, runner=fake)
    time.sleep(0.1)
    v = server.job_view(job)
    assert (v["state"], v["stage"], v["done"], v["total"]) == ("running", "match", 2, 4)
    done.set()
    for _ in range(50):
        if server.job_view(job)["state"] == "done":
            break
        time.sleep(0.02)
    assert server.job_view(job)["result"] == {"id": "x"}


def test_finished_jobs_are_trimmed_to_keep_jobs():
    before = len(server._jobs)
    for _ in range(server.KEEP_JOBS + 5):
        server.start_job({"mode": "sample", "id": "x"},
                         runner=lambda j, b: j.update(state="done", finished=time.time()))
        time.sleep(0.01)
    assert len(server._jobs) <= max(server.KEEP_JOBS, before)


@pytest.fixture()
def live():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/"
    srv.shutdown()
    srv.server_close()


def _call(url, body=None):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
                                 method="GET" if body is None else "POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_the_routes_answer_and_refuse_what_they_should(live):
    code, h = _call(live + "api/health")
    assert code == 200 and h["service"] == "lunaxx-console" and h["modes"] == ["upload", "sample", "known"]
    assert _call(live + "api/jobs/" + "0" * 32)[0] == 404
    assert _call(live + "api/thumb/no_such_pair.jpg")[0] == 404
    code, err = _call(live + "api/jobs", {"mode": "nope"})
    assert code == 400 and "mode" in err["error"]
    assert _call(live + "api/nothing", {"mode": "upload"})[0] == 404
