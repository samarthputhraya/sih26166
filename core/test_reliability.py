"""Pins the behaviour of core/reliability.py before it reaches a slide.

No LoFTR here - matches are synthesised, so these run in milliseconds. The
calibration against exact ground truth on real renders is
`python -m core.reliability_calibrate`, whose output is the evidence.
"""
import numpy as np
import pytest

from core.reliability import (NO_EVIDENCE, VERIFIED, WEAK, ascii_map, describe,
                              reliability_map, summary_by_state, xcorr_peak)

H, W = 256, 256


def _texture(seed=0):
    rng = np.random.default_rng(seed)
    img = rng.random((H, W)).astype(np.float32)
    # low-pass so cells have structure, not white noise
    import cv2
    return cv2.GaussianBlur(img, (0, 0), 2.0) * 255.0


def _shift_H(dx, dy):
    return np.array([[1.0, 0.0, dx], [0.0, 1.0, dy], [0.0, 0.0, 1.0]])


def _matches_for(H_true, n=800, seed=1, noise=0.0):
    """Source points across the source frame, reference = H_true(source) (+ noise)."""
    import cv2
    rng = np.random.default_rng(seed)
    src = (rng.random((n, 2)) * [W - 1, H - 1]).astype(np.float32)
    ref = cv2.perspectiveTransform(src.reshape(-1, 1, 2), H_true).reshape(-1, 2)
    ref = ref + rng.normal(0, noise, ref.shape).astype(np.float32)
    keep = (ref[:, 0] >= 0) & (ref[:, 0] < W) & (ref[:, 1] >= 0) & (ref[:, 1] < H)
    return src[keep], ref[keep].astype(np.float32)


def test_xcorr_peak_sign():
    a = _texture()
    dx, dy = 7, -4
    b = np.roll(a, (dy, dx), axis=(0, 1))
    px, py, ncc = xcorr_peak(a, b)
    assert (px, py) == (dx, dy), (px, py)
    assert ncc > 0.9


def test_xcorr_peak_constant_block_is_not_evidence():
    assert xcorr_peak(np.zeros((32, 32)), np.zeros((32, 32))) == (None, None, 0.0)


def test_correct_registration_is_verified_where_measured():
    import cv2
    ref = _texture(3)
    H_true = _shift_H(5.0, -3.0)
    src = cv2.warpPerspective(ref, np.linalg.inv(H_true), (W, H))     # source = ref moved
    s, r = _matches_for(H_true, noise=0.2)
    Hfit = H_true.copy()
    warped = cv2.warpPerspective(src, Hfit, (W, H))
    rel = reliability_map((H, W), s, r, Hfit, s, r, warped, ref, gsd_mpp=60.0, H_true=H_true)
    assert rel["global"]["contradicted"] is False
    assert rel["counts"][VERIFIED] >= 48, ascii_map(rel)
    # calibration: verified cells are genuinely accurate
    v = rel["summary_by_state"][VERIFIED]
    assert v["n"] > 0 and v["median_px"] < 0.05
    assert rel["global"]["verdict"] == "agrees"
    assert any("AGREES" in line for line in describe(rel))


def test_confident_but_wrong_homography_is_contradicted():
    """Matches all agree with a shift of +40 px; the pixels say the shift is 0.

    This is the Tier D failure in miniature: perfect self-consistency, wrong answer.
    """
    import cv2
    ref = _texture(5)
    H_wrong = _shift_H(40.0, 0.0)
    s, r = _matches_for(H_wrong, noise=0.1)          # matches consistent with H_wrong
    warped = cv2.warpPerspective(ref, H_wrong, (W, H))   # but the true source IS ref
    rel = reliability_map((H, W), s, r, H_wrong, s, r, warped, ref, gsd_mpp=60.0, H_true=np.eye(3))
    assert rel["global"]["contradicted"] is True
    assert abs(rel["global"]["shift_px"][0] + 40) <= 2   # area check finds the real offset
    assert rel["counts"][VERIFIED] == 0, ascii_map(rel)
    assert rel["global"]["self_consistency_px"] < 1.0    # the matches DO agree with H
    w = rel["summary_by_state"][WEAK]
    assert w["n"] > 0 and w["median_px"] > 30            # and they are wrong by ~40 px


def test_verdict_is_a_consensus_of_cells_not_one_frame_peak():
    """Half the frame is misaligned by 12 px (a wrong local warp), half is perfect.

    A whole-frame FFT would return some compromise peak; the cells must vote, and
    with ~50% agreeing the verdict is unconfirmed rather than contradicted - so the
    good half keeps its verified cells and no fallback is triggered.
    """
    import cv2
    ref = _texture(17)
    warped = ref.copy()
    warped[:, W // 2:] = np.roll(ref, 12, axis=1)[:, W // 2:]   # right half shifted
    s, r = _matches_for(np.eye(3), noise=0.1)
    rel = reliability_map((H, W), s, r, np.eye(3), s, r, warped, ref)
    g = rel["global"]
    assert g["basis"].endswith("cells")
    assert g["verdict"] in ("unconfirmed", "agrees")
    assert g["contradicted"] is False
    assert (rel["state"][:, :4] == VERIFIED).sum() >= 24, ascii_map(rel)
    assert (rel["state"][:, 4:] == VERIFIED).sum() <= 4, ascii_map(rel)


def test_no_matches_means_no_evidence_not_bad():
    ref = _texture(7)
    rel = reliability_map((H, W), np.zeros((0, 2)), np.zeros((0, 2)), None,
                          np.zeros((0, 2)), np.zeros((0, 2)), None, ref)
    assert rel["counts"][NO_EVIDENCE] == 64
    assert rel["global"]["contradicted"] is None


def test_cells_without_inliers_are_no_evidence_even_when_pixels_agree():
    """Only the left half has matches. The right half aligns perfectly, but the
    matcher measured nothing there, so it must read as unmeasured - not verified."""
    import cv2
    ref = _texture(9)
    s, r = _matches_for(np.eye(3), noise=0.1)
    left = r[:, 0] < W / 2
    s, r = s[left], r[left]
    warped = cv2.warpPerspective(ref, np.eye(3), (W, H))
    rel = reliability_map((H, W), s, r, np.eye(3), s, r, warped, ref)
    right = rel["state"][:, 4:]
    assert (right == NO_EVIDENCE).all(), ascii_map(rel)
    assert (rel["state"][:, :4] == VERIFIED).sum() >= 24


def test_tiny_cells_cannot_be_verified():
    """A 64 px image has 8 px cells: the area check is skipped, so nothing is promoted."""
    import cv2
    n = 64
    rng = np.random.default_rng(2)
    ref = cv2.GaussianBlur(rng.random((n, n)).astype(np.float32), (0, 0), 1.5) * 255
    pts = (rng.random((300, 2)) * (n - 1)).astype(np.float32)
    rel = reliability_map((n, n), pts, pts, np.eye(3), pts, pts, ref.copy(), ref)
    assert rel["counts"][VERIFIED] == 0
    assert rel["counts"][WEAK] > 0


def test_gate_labels_changes_by_cell_state():
    import cv2
    from core.reliability import gate
    ref = _texture(11)
    s, r = _matches_for(np.eye(3), noise=0.1)
    left = r[:, 0] < W / 2
    s, r = s[left], r[left]
    warped = cv2.warpPerspective(ref, np.eye(3), (W, H))
    rel = reliability_map((H, W), s, r, np.eye(3), s, r, warped, ref)
    changes = [{"centroid_px": [20.0, 20.0], "area_px": 60.0},      # left half: verified
               {"centroid_px": [W - 20.0, 20.0], "area_px": 60.0}]  # right half: no evidence
    g = gate(changes, rel, (H, W))
    assert g["counts"] == {"input": 2, "kept": 1, "rejected_weak": 0, "unassessable": 1}
    assert g["kept"][0]["reliability"] == VERIFIED
    assert g["unassessable"][0]["reliability"] == NO_EVIDENCE


def test_gate_keeps_nothing_when_the_frame_is_contradicted():
    import cv2
    from core.reliability import gate
    ref = _texture(13)
    H_wrong = _shift_H(40.0, 0.0)
    s, r = _matches_for(H_wrong, noise=0.1)
    warped = cv2.warpPerspective(ref, H_wrong, (W, H))
    rel = reliability_map((H, W), s, r, H_wrong, s, r, warped, ref)
    assert rel["global"]["contradicted"] is True
    g = gate([{"centroid_px": [100.0, 100.0]}], rel, (H, W))
    assert g["counts"]["kept"] == 0


def test_summary_by_state_handles_empty_states():
    state = np.full((8, 8), WEAK, dtype=object)
    err = np.full((8, 8), 2.0)
    s = summary_by_state(state, err, gsd_mpp=10.0)
    assert s[VERIFIED] == {"n": 0}
    assert s[WEAK]["n"] == 64 and s[WEAK]["median_m"] == pytest.approx(20.0)


def test_xcorr_peak_subpixel_recovers_a_fractional_shift():
    """The fallback's global shift is refined to sub-pixel; the integer peak is not."""
    import numpy as np
    import cv2
    from core.reliability import xcorr_peak, xcorr_peak_subpixel
    rng = np.random.default_rng(5)
    base = cv2.GaussianBlur(rng.random((256, 256)).astype(np.float32), (0, 0), 3)
    M = np.float32([[1, 0, 3.3], [0, 1, -2.6]])           # b = a moved by (+3.3, -2.6)
    b = cv2.warpAffine(base, M, (256, 256), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    a = base
    dx, dy, _ = xcorr_peak_subpixel(a[32:224, 32:224], b[32:224, 32:224])
    ix, iy, _ = xcorr_peak(a[32:224, 32:224], b[32:224, 32:224])
    assert abs(ix - 3.3) <= 1 and abs(iy + 2.6) <= 1              # integer peak: within a pixel
    assert abs(dx - 3.3) < 0.15 and abs(dy + 2.6) < 0.15            # refined: within 0.15 px
    for sx, sy in [(0.25, 0.4), (-1.7, 2.45), (0.5, -0.5), (-4.1, 0.9)]:
        bb = cv2.warpAffine(base, np.float32([[1, 0, sx], [0, 1, sy]]), (256, 256),
                            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        ddx, ddy, _ = xcorr_peak_subpixel(a[32:224, 32:224], bb[32:224, 32:224])
        assert np.hypot(ddx - sx, ddy - sy) < 0.15, (sx, sy, ddx, ddy)
