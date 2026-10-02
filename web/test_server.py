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


def test_a_failed_import_ends_the_job_with_its_error(monkeypatch):
    # 2 Oct: the hosted copy lacked psutil, the import raised outside the job's try, the thread
    # died and the page polled "queued" for ever. The job must end in "error", saying why.
    import sys
    monkeypatch.setitem(sys.modules, "core.pipeline", None)
    job = {"id": "f" * 32, "mode": "sample", "state": "running", "stage": "queued", "done": 0, "total": 0}
    server.run_job(job, {"id": "x"})
    assert job["state"] == "error" and "core.pipeline" in job["error"]
    assert job.get("finished")


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
    assert h["hosted"] is False                        # the page says "this machine", not "a cloud CPU"
    assert _call(live + "api/jobs/" + "0" * 32)[0] == 404
    assert _call(live + "api/thumb/no_such_pair.jpg")[0] == 404
    code, err = _call(live + "api/jobs", {"mode": "nope"})
    assert code == 400 and "mode" in err["error"]
    assert _call(live + "api/nothing", {"mode": "upload"})[0] == 404


def test_an_lzw_geotiff_can_be_drawn(tmp_path):
    """LZW needs imagecodecs in tifffile; the demo laptop has none. The panel reads through
    core's loader, which falls back to Pillow - an LZW upload used to fail after the whole run."""
    from PIL import Image
    from web.panel import jpg
    arr = (np.random.default_rng(1).random((120, 160)) * 255).astype(np.uint8)
    p = tmp_path / "lzw.tif"
    Image.fromarray(arr).save(p, compression="tiff_lzw")
    assert jpg(p).startswith("data:image/jpeg;base64,")


def test_a_malformed_upload_is_refused_by_name(tmp_path):
    with pytest.raises(ValueError, match="image A"):
        server._save("not a dict", tmp_path, "a")


def test_an_empty_post_is_a_400_not_a_413(live):
    req = urllib.request.Request(live + "api/jobs", data=b"", method="POST")
    try:
        urllib.request.urlopen(req, timeout=10)
        code = 200
    except urllib.error.HTTPError as e:
        code = e.code
    assert code == 400


def _tif(path, w, h, gsd=None, seed=0):
    """A grey TIFF, with a GeoTIFF ModelPixelScaleTag when `gsd` is given."""
    import tifffile
    img = (np.random.default_rng(seed).random((h, w)) * 255).astype(np.uint8)
    extra = [(33550, "d", 3, (gsd, gsd, 0.0), False)] if gsd else []
    tifffile.imwrite(str(path), img, extratags=extra)
    return path


def test_two_large_photos_are_reduced_by_one_factor_so_the_reference_fits_a_tile(tmp_path):
    """Until 2 Oct two ordinary screenshots (the page sends at most 1600 px) came back "Not
    registered": core.matcher takes a reference of at most one tile."""
    import tifffile
    a, b = _tif(tmp_path / "a.tif", 1600, 1200), _tif(tmp_path / "b.tif", 1000, 1500, seed=1)
    note = server._fit_reference(a, b)
    ra, rb = tifffile.imread(str(a)), tifffile.imread(str(b))
    assert max(rb.shape) == server.TILE
    f = server.TILE / 1500
    assert ra.shape == (round(1200 * f), round(1600 * f))      # the same factor: relative scale kept
    assert "same factor" in note and f"{f:.2f}" in note


def test_a_photo_already_within_a_tile_and_a_georeferenced_pair_keep_their_pixels(tmp_path):
    small = (_tif(tmp_path / "a.tif", 1600, 1200), _tif(tmp_path / "b.tif", 600, 500))
    geo = (_tif(tmp_path / "ga.tif", 1600, 1600, gsd=1.25), _tif(tmp_path / "gb.tif", 1500, 1500, gsd=5.0))
    for a, b in (small, geo):
        before = [p.read_bytes() for p in (a, b)]
        assert server._fit_reference(a, b) == ""
        assert [p.read_bytes() for p in (a, b)] == before


def test_the_tile_matches_the_matcher():
    from core.matcher import TILE
    assert server.TILE == TILE


def test_the_matchers_oversize_refusal_reaches_the_visitor_in_plain_words():
    raw = ("both images exceed the 640 px tile ((1600, 1600) and (1500, 900)). Crop to the overlap "
           "first with io_loader.crop_to_overlap, and resample to a common GSD with "
           "scale.to_common_gsd - matching two full strips directly is not affordable on this machine.")
    msg = server._plain_error(raw)
    assert "(1500, 900) px" in msg and "at most 640 x 640 px" in msg
    assert "io_loader" not in msg and "this machine" not in msg
    assert server._plain_error("notes.png: could not be decoded as an image") == \
        "notes.png: could not be decoded as an image"


def test_a_hosted_copy_does_not_call_its_cpu_the_visitors_machine(monkeypatch):
    monkeypatch.setattr(server, "PUBLIC", True)
    assert server._where() == "on this server's CPU"
    monkeypatch.setattr(server, "PUBLIC", False)
    assert server._where() == "on this machine"
