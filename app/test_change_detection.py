import cv2
import numpy as np

from change_detection import detect_changes


def test_new_bright_change():
    img_a = np.zeros((400, 600), dtype=np.uint8)
    img_b = img_a.copy()

    cv2.circle(
        img_b,
        (200, 150),
        25,
        255,
        -1
    )

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=0.5
    )

    assert len(changes) == 1
    assert changes[0]["classification"] == "new bright"

    print("PASS: New bright change")


def test_disappeared_change():
    img_a = np.zeros((400, 600), dtype=np.uint8)

    cv2.circle(
        img_a,
        (200, 150),
        25,
        255,
        -1
    )

    img_b = np.zeros((400, 600), dtype=np.uint8)

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=0.5
    )

    assert len(changes) == 1
    assert changes[0]["classification"] == "disappeared"

    print("PASS: Disappeared change")


def test_shadow_change():
    img_a = np.zeros((400, 600), dtype=np.uint8)
    img_b = img_a.copy()

    cv2.rectangle(
        img_b,
        (150, 180),
        (400, 195),
        255,
        -1
    )

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=0.5
    )

    assert len(changes) == 1
    assert changes[0]["classification"] == "shadow?"

    print("PASS: Shadow classification")


def test_uncertain_change():
    img_a = np.full(
        (400, 600),
        100,
        dtype=np.uint8
    )

    img_b = img_a.copy()

    cv2.circle(
        img_b,
        (200, 150),
        20,
        135,
        -1
    )

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=0.5
    )

    assert len(changes) == 1
    assert changes[0]["classification"] == "uncertain"

    print("PASS: Uncertain classification")


def test_small_noise_is_ignored():
    img_a = np.zeros((400, 600), dtype=np.uint8)
    img_b = img_a.copy()

    cv2.circle(
        img_b,
        (100, 100),
        2,
        255,
        -1
    )

    cv2.circle(
        img_b,
        (300, 200),
        2,
        255,
        -1
    )

    cv2.circle(
        img_b,
        (500, 300),
        2,
        255,
        -1
    )

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=0.5
    )

    assert len(changes) == 0

    print("PASS: Small noise ignored")


def test_border_artifact_is_ignored():
    img_a = np.zeros((400, 600), dtype=np.uint8)
    img_b = img_a.copy()

    cv2.rectangle(
        img_b,
        (0, 100),
        (15, 200),
        255,
        -1
    )

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=0.5
    )

    assert len(changes) == 0

    print("PASS: Border artifact ignored")


def test_uint16_input():
    img_a = np.zeros((400, 600), dtype=np.uint8)
    img_b = img_a.copy()

    cv2.circle(
        img_b,
        (200, 150),
        25,
        255,
        -1
    )

    # Convert both using the same scale.
    img_a = img_a.astype(np.uint16) * 100
    img_b = img_b.astype(np.uint16) * 100

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=0.5
    )

    assert len(changes) == 1
    assert changes[0]["classification"] == "new bright"

    print("PASS: uint16 input")


def test_zero_margin_does_not_erase_everything():
    img_a = np.zeros(
        (100, 100),
        dtype=np.uint8
    )

    img_b = img_a.copy()

    img_b[40:60, 40:60] = 200

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=1.0,
        edge_margin_frac=0.0
    )

    assert len(changes) == 1, (
        "margin=0 wiped the mask"
    )

    print("PASS: Zero margin does not erase everything")


def test_area_matches_known_circle():
    img_a = np.zeros(
        (400, 400),
        dtype=np.uint8
    )

    img_b = img_a.copy()

    cv2.circle(
        img_b,
        (200, 200),
        18,
        255,
        -1
    )

    overlay, changes = detect_changes(
        img_a,
        img_b,
        gsd_mpp=9.3699,
        thresh=30
    )

    expected = np.pi * (18 * 9.3699) ** 2

    assert len(changes) == 1

    assert (
        abs(changes[0]["area_m2"] - expected)
        / expected
        < 0.25
    )

    print("PASS: Known-circle area")


def run_all_tests():
    test_new_bright_change()
    test_disappeared_change()
    test_shadow_change()
    test_uncertain_change()
    test_small_noise_is_ignored()
    test_border_artifact_is_ignored()
    test_uint16_input()
    test_zero_margin_does_not_erase_everything()
    test_area_matches_known_circle()

    print("\nALL TESTS PASSED!")


if __name__ == "__main__":
    run_all_tests()