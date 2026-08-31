from pathlib import Path
import csv
import sys
import cv2
import numpy as np


# Allow imports from the project root.
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from baselines.sift_baseline import run_sift
from baselines.orb_baseline import run_orb
from baselines.akaze_baseline import run_akaze


PAIR_SOURCE = ROOT / "data" / "pairs" / "pair_test_source.tif"
PAIR_REFERENCE = ROOT / "data" / "pairs" / "pair_test_ref.tif"

OUTPUT = ROOT / "baselines" / "results.csv"


def load_gray(path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise FileNotFoundError(
            f"Could not read image: {path}"
        )

    return img


def calculate_offset(src_pts, ref_pts):
    """
    For the known synthetic pair:

        source = reference shifted by approximately
        (+7, +5)

    Calculate mean source-reference displacement.
    """

    if len(src_pts) == 0:
        return 0.0, 0.0

    delta = src_pts - ref_pts

    dx = float(np.mean(delta[:, 0]))
    dy = float(np.mean(delta[:, 1]))

    return dx, dy


def calculate_spread(src_pts, ref_pts):
    """
    Calculate the standard deviation of displacement.
    Lower means the estimated translation is more consistent.
    """

    if len(src_pts) == 0:
        return 0.0

    delta = src_pts - ref_pts

    distances = np.sqrt(
        np.sum(delta ** 2, axis=1)
    )

    return float(np.std(distances))


def run_method(name, function, img1, img2):
    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    src, ref, confidence, elapsed = function(
        img1,
        img2
    )

    n_matches = len(src)

    mean_confidence = (
        float(np.mean(confidence))
        if len(confidence)
        else 0.0
    )

    dx, dy = calculate_offset(src, ref)

    spread = calculate_spread(src, ref)

    print(f"matches:          {n_matches}")
    print(f"mean confidence:  {mean_confidence:.6f}")
    print(f"mean dx:          {dx:.3f}")
    print(f"mean dy:          {dy:.3f}")
    print(f"offset spread:    {spread:.3f}")
    print(f"time:             {elapsed:.4f} s")

    return {
        "pair_id": "pair_test",
        "tier": "TEST",
        "config": "raw",
        "method": name,
        "n_matches": n_matches,
        "mean_confidence": mean_confidence,
        "dx_px": dx,
        "dy_px": dy,
        "offset_spread_px": spread,
        "runtime_s": elapsed,
    }


def main():

    print("=" * 70)
    print("SIH26166 — DAY 2 CLASSICAL BASELINE RUN")
    print("=" * 70)

    print(f"source: {PAIR_SOURCE}")
    print(f"reference: {PAIR_REFERENCE}")

    img1 = load_gray(PAIR_SOURCE)
    img2 = load_gray(PAIR_REFERENCE)

    print()
    print(f"source shape:    {img1.shape}")
    print(f"reference shape: {img2.shape}")

    methods = [
        ("SIFT", run_sift),
        ("ORB", run_orb),
        ("AKAZE", run_akaze),
    ]

    rows = []

    for name, function in methods:

        row = run_method(
            name,
            function,
            img1,
            img2
        )

        rows.append(row)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "pair_id",
        "tier",
        "config",
        "method",
        "n_matches",
        "mean_confidence",
        "dx_px",
        "dy_px",
        "offset_spread_px",
        "runtime_s",
    ]

    with open(
        OUTPUT,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)

    print()
    print("=" * 70)
    print("DAY 2 RESULTS")
    print("=" * 70)

    for row in rows:
        print(
            f"{row['method']:6s} | "
            f"matches={row['n_matches']:5d} | "
            f"dx={row['dx_px']:8.3f} | "
            f"dy={row['dy_px']:8.3f} | "
            f"time={row['runtime_s']:.4f}s"
        )

    print()
    print(f"CSV written to:")
    print(OUTPUT)

    print()
    print("KNOWN TEST ANSWER:")
    print("Expected source-reference offset ≈ (+7, +5) pixels.")
    print()
    print("Day 2 baseline run complete.")


if __name__ == "__main__":
    main()