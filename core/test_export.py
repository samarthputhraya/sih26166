"""The deliverables writer: every file the PS names, in conventions a GIS can read.

No LoFTR here - the result dict is built by hand around a known translation, so each
number in the exported files can be checked against arithmetic.
"""
import csv
import hashlib
import json
import re
import shutil
import subprocess

import numpy as np
import pytest

tifffile = pytest.importorskip("tifffile")

from core import export  # noqa: E402
from core.io_loader import load  # noqa: E402

GSD = 1.5
X0, Y0 = 100000.0, -250000.0
CRS = "Moon (2015) - Sphere / Ocentric / South Polar"
SHIFT = np.array([12.25, -8.5])          # source -> reference, in reference px


def _geotiff(path, img):
    tifffile.imwrite(str(path), img, extratags=[
        (33550, 12, 3, (GSD, GSD, 0.0), True),
        (33922, 12, 6, (0.0, 0.0, 0.0, X0, Y0, 0.0), True),
        (34737, 2, 0, CRS + "|", True),
    ])


def _result(tmp_path, georef=True, failed=False):
    rng = np.random.default_rng(3)
    src_img = rng.integers(10, 250, (96, 96), dtype=np.uint8)
    ref_img = rng.integers(10, 250, (96, 96), dtype=np.uint8)
    sp, rp = tmp_path / "p_source.tif", tmp_path / "p_ref.tif"
    tifffile.imwrite(str(sp), src_img)
    (_geotiff if georef else (lambda p, i: tifffile.imwrite(str(p), i)))(rp, ref_img)
    _, mr = load(rp)
    _, ms = load(sp)

    good = rng.random((40, 2)) * 70 + 5
    bad = rng.random((10, 2)) * 90
    src = np.vstack([good, bad])
    ref = np.vstack([good + SHIFT, rng.random((10, 2)) * 90])
    H = np.array([[1, 0, SHIFT[0]], [0, 1, SHIFT[1]], [0, 0, 1]], float)
    state = np.full((8, 8), "no_evidence", dtype=object)
    state[:4, :] = "verified"
    rel = {"state": state, "counts": {"verified": 32, "weak": 0, "no_evidence": 32},
           "n_cells": 64, "global": {"verdict": "agrees", "contradicted": False,
                                     "note": "test"}, "config": "test"}
    r = {
        "source": str(sp), "reference": str(rp),
        "shape_source": src_img.shape, "shape_reference": ref_img.shape,
        "gsd_mpp": GSD, "scale_note": "same GSD", "illumination": "none",
        "n_matches": len(src), "ransac": {"inlier_count": 40, "note": "test"},
        "H": None if failed else H, "H_final": None if failed else H,
        "warped": None, "warped_final": None if failed else rng.random((96, 96)).astype(np.float32),
        "src_matches": src, "ref_matches": ref,
        "src_inliers": np.zeros((0, 2)) if failed else good,
        "ref_inliers": np.zeros((0, 2)) if failed else good + SHIFT,
        "match_scores": np.linspace(1, 0.5, len(src)).astype(np.float32),
        "metrics": None if failed else {"residual_px": 0.01, "inlier_count": 40,
                                        "inlier_ratio": 0.8, "rmse_gt_px": None,
                                        "grid_coverage_fraction": 0.5, "distribution_cv": 0.4},
        "metrics_note": "failed" if failed else "ok",
        "reliability": None if failed else rel,
        "declared": {"method": "none" if failed else "loftr+magsac++", "why": "test",
                     "contradicted": False},
        "fallback": None, "seconds": 1.0,
        "meta_source": ms, "meta_reference": mr,
    }
    return r, sp, rp


def test_registered_product_carries_the_reference_georeferencing(tmp_path):
    r, sp, rp = _result(tmp_path)
    files = export.export_bundle(r, tmp_path / "out", "t", sp, rp)
    img, meta = load(files["registered_product.tif"])
    _, ref_meta = load(rp)
    assert meta["transform"] == ref_meta["transform"]
    assert meta["gsd_mpp"] == pytest.approx(GSD)
    assert meta["crs"] == ref_meta["crs"]
    assert img.dtype == np.float32 and img.shape == (96, 96)
    # outside the source footprint (shifted by +12/-8.5 px) the product is NaN, not 0
    assert np.isnan(img[-1, 0]) and np.isfinite(img[40, 40])


def test_matches_flags_exactly_the_ransac_survivors(tmp_path):
    r, sp, rp = _result(tmp_path)
    files = export.export_bundle(r, tmp_path / "out", "t", sp, rp)
    with open(files["matches.csv"], encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    assert len(rows) == 50
    inl = [x for x in rows if x["is_inlier"] == "1"]
    assert len(inl) == 40
    assert max(float(x["residual_px"]) for x in inl) < 1e-6
    assert {x["cell_state"] for x in rows} <= {"verified", "no_evidence", "weak"}
    assert rows[0]["score"] == "1.0000"


def test_gcps_are_in_gdal_convention_on_the_reference_map(tmp_path):
    r, sp, rp = _result(tmp_path)
    files = export.export_bundle(r, tmp_path / "out", "t", sp, rp)
    lines = [ln for ln in files["gcps.txt"].read_text().splitlines() if ln.startswith("-gcp")]
    assert len(lines) == 40
    _, px, ln, X, Y = lines[0].split()
    sx, sy = r["src_inliers"][0]
    rx, ry = sx + SHIFT[0], sy + SHIFT[1]
    assert float(px) == pytest.approx(sx + 0.5, abs=1e-3)
    assert float(X) == pytest.approx(X0 + (rx + 0.5) * GSD, abs=1e-3)
    assert float(Y) == pytest.approx(Y0 - (ry + 0.5) * GSD, abs=1e-3)
    pts = files["gcps.points"].read_text().splitlines()
    assert pts[1].startswith("mapX,mapY,sourceX,sourceY")
    assert float(pts[2].split(",")[3]) < 0          # QGIS: source Y negative


def test_isis_csv_is_one_based(tmp_path):
    r, sp, rp = _result(tmp_path)
    files = export.export_bundle(r, tmp_path / "out", "t", sp, rp)
    with open(files["matches_isis.csv"], encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    assert float(rows[0]["source_sample"]) == pytest.approx(r["src_inliers"][0][0] + 1, abs=1e-3)


def test_report_hashes_inputs_and_names_the_grid(tmp_path):
    r, sp, rp = _result(tmp_path)
    files = export.export_bundle(r, tmp_path / "out", "t", sp, rp)
    rep = json.loads(files["report.json"].read_text())
    assert rep["inputs"]["source"]["sha256"] == hashlib.sha256(sp.read_bytes()).hexdigest()
    assert rep["trust"]["counts"]["verified"] == 32
    md = files["report.md"].read_text()
    # every pixel figure in the report names the grid it is measured on
    for line in md.splitlines():
        if re.search(r"\d px", line):
            assert "grid" in line, line


def test_ungeoreferenced_reference_gets_a_sidecar_and_no_gcps(tmp_path):
    r, sp, rp = _result(tmp_path, georef=False)
    files = export.export_bundle(r, tmp_path / "out", "t", sp, rp)
    assert "registered_product.json" in files and "gcps.txt" not in files
    side = json.loads(files["registered_product.json"].read_text())
    assert side["transform"] is None and "pixels" in side["frame"]


def test_failed_pair_still_writes_matches_and_a_report(tmp_path):
    r, sp, rp = _result(tmp_path, failed=True)
    files = export.export_bundle(r, tmp_path / "out", "t", sp, rp)
    assert "registered_product.tif" not in files
    assert {"matches.csv", "report.json", "report.md"} <= set(files)
    rep = json.loads(files["report.json"].read_text())
    assert rep["declared"]["method"] == "none" and rep["inliers_exported"] == 0


def test_bundle_bytes_matches_the_files(tmp_path):
    r, sp, rp = _result(tmp_path)
    b = export.bundle_bytes(r, "t", sp, rp)
    assert b["registered_product.tif"][:2] in (b"II", b"MM")
    assert b"-gcp" in b["gcps.txt"]


def test_appending_to_the_evidence_logs_does_not_dirty_the_commit_stamp(tmp_path):
    git = shutil.which("git")
    if git is None:
        pytest.skip("git not on PATH")

    def run(*a):
        subprocess.run([git, "-c", "user.name=t", "-c", "user.email=t@t", *a],
                       cwd=tmp_path, check=True, capture_output=True)

    (tmp_path / "core").mkdir()
    (tmp_path / "evaluation").mkdir()
    (tmp_path / "core" / "m.py").write_text("x = 1\n")
    for log in export.EVIDENCE_LOGS[:2]:
        (tmp_path / log).write_text("a,b\n")
    run("init", "-q")
    run("add", "-A")
    run("commit", "-q", "-m", "c")
    sha = export._commit(root=tmp_path)
    assert sha != "?" and not sha.endswith("-dirty")

    # A run appends rows and creates the calibration CSV: still the same code.
    for log in export.EVIDENCE_LOGS[:2]:
        with open(tmp_path / log, "a") as f:
            f.write("1,2\n")
    (tmp_path / export.EVIDENCE_LOGS[2]).write_text("t\n")
    assert export._commit(root=tmp_path) == sha

    # New or changed code is dirty, including an untracked module beside the logs.
    (tmp_path / "evaluation" / "new.py").write_text("y = 2\n")
    assert export._commit(root=tmp_path) == sha + "-dirty"
    (tmp_path / "evaluation" / "new.py").unlink()
    (tmp_path / "core" / "m.py").write_text("x = 2\n")
    assert export._commit(root=tmp_path) == sha + "-dirty"
