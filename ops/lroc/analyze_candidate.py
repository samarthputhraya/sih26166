import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


DEFAULT_OFFSET = 15292
DEFAULT_LINES = 25408
DEFAULT_SAMPLES = 3823

DEFAULT_Y = 1565
DEFAULT_X = 2626

PIXEL_SCALE_M = 1.1


def load_lroc(path, offset, lines, samples):
    """Load the four float32 channels from the LROC IMG product."""
    with open(path, "rb") as handle:
        handle.seek(offset)
        data = np.fromfile(
            handle,
            dtype="<f4",
            count=4 * lines * samples,
        )

    expected = 4 * lines * samples
    if data.size != expected:
        raise RuntimeError(
            f"Expected {expected} float32 values, got {data.size}."
        )

    data = data.reshape((4, lines, samples))
    data[data < -1e30] = np.nan
    return data


def save_figure(path):
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a candidate dark lunar surface feature in LROC NAC data."
    )

    parser.add_argument("img", type=Path, help="Path to LROC .IMG file")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/lroc_analysis"),
        help="Directory for generated analysis figures",
    )
    parser.add_argument("--offset", type=int, default=DEFAULT_OFFSET)
    parser.add_argument("--lines", type=int, default=DEFAULT_LINES)
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    parser.add_argument("--y", type=int, default=DEFAULT_Y)
    parser.add_argument("--x", type=int, default=DEFAULT_X)

    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    print("Loading LROC NAC data...")
    print(f"File: {args.img}")
    print(f"Candidate center: line={args.y}, sample={args.x}")

    a = load_lroc(
        args.img,
        args.offset,
        args.lines,
        args.samples,
    )

    IF_full = a[0]
    INC_full = a[3]

    # ------------------------------------------------------------------
    # 1. Candidate crop
    # ------------------------------------------------------------------

    rmax = 100

    y0 = args.y
    x0 = args.x

    IF = IF_full[
        y0 - rmax:y0 + rmax + 1,
        x0 - rmax:x0 + rmax + 1,
    ]

    INC = INC_full[
        y0 - rmax:y0 + rmax + 1,
        x0 - rmax:x0 + rmax + 1,
    ]

    yy, xx = np.indices(IF.shape)

    cy = cx = rmax

    dist = np.sqrt(
        (yy - cy) ** 2 +
        (xx - cx) ** 2
    )

    valid = np.isfinite(IF) & np.isfinite(INC)

    # ------------------------------------------------------------------
    # 2. Local-background normalized I/F
    # ------------------------------------------------------------------

    crater = dist <= 15
    background = (dist >= 30) & (dist <= 80)

    bg = np.nanmedian(IF[background])

    ratio = IF / bg

    print()
    print("--- I/F NORMALIZED TO LOCAL BACKGROUND ---")
    print(f"Local background median I/F: {bg}")
    print("Crater radius: 15 px =", 15 * PIXEL_SCALE_M, "m")
    print("Crater median I/F:", np.nanmedian(IF[crater]))
    print("Crater mean I/F:", np.nanmean(IF[crater]))
    print(
        "Crater/background median ratio:",
        np.nanmedian(ratio[crater]),
    )

    # ------------------------------------------------------------------
    # 3. Incidence-angle comparison
    # ------------------------------------------------------------------

    bins = np.arange(50, 101, 5)

    print()
    print("--- INCIDENCE-BINNED CRATER CONTRAST ---")

    incidence_rows = []

    for i in range(len(bins) - 1):
        lo = bins[i]
        hi = bins[i + 1]

        mask = (
            crater
            & valid
            & (INC >= lo)
            & (INC < hi)
        )

        n = np.sum(mask)

        if n == 0:
            continue

        median_if = np.nanmedian(IF[mask])
        median_ratio = np.nanmedian(ratio[mask])

        incidence_rows.append(
            (lo, hi, n, median_if, median_ratio)
        )

        print(
            f"{lo}-{hi} deg: "
            f"N={n}, "
            f"median I/F={median_if:.6f}, "
            f"median ratio={median_ratio:.3f}"
        )

    # ------------------------------------------------------------------
    # 4. Matched-incidence crater/control comparison
    # ------------------------------------------------------------------

    control = (
        (dist >= 20)
        & (dist <= 35)
    )

    print()
    print("--- MATCHED-INCIDENCE CRATER / CONTROL ---")

    matched_ratios = []

    for i in range(len(bins) - 1):
        lo = bins[i]
        hi = bins[i + 1]

        crater_mask = (
            crater
            & valid
            & (INC >= lo)
            & (INC < hi)
        )

        control_mask = (
            control
            & valid
            & (INC >= lo)
            & (INC < hi)
        )

        crater_n = np.sum(crater_mask)
        control_n = np.sum(control_mask)

        if crater_n == 0 or control_n == 0:
            continue

        crater_if = np.nanmedian(IF[crater_mask])
        control_if = np.nanmedian(IF[control_mask])

        if not np.isfinite(crater_if) or not np.isfinite(control_if):
            continue

        ratio_value = crater_if / control_if

        matched_ratios.append(ratio_value)

        print(
            f"{lo}-{hi} deg: "
            f"crater N={crater_n}, "
            f"control N={control_n}, "
            f"crater I/F={crater_if:.6f}, "
            f"control I/F={control_if:.6f}, "
            f"ratio={ratio_value:.3f}x"
        )

    if matched_ratios:
        print(
            "Median matched-incidence ratio:",
            np.nanmedian(matched_ratios),
        )

    # ------------------------------------------------------------------
    # 5. Illumination correction
    # ------------------------------------------------------------------

    bg_mask = (
        (dist >= 35)
        & (dist <= 80)
        & valid
    )

    bg_inc = INC[bg_mask]
    bg_if = IF[bg_mask]

    correction_bins = np.arange(50, 101, 2)

    centers = []
    medians = []

    for i in range(len(correction_bins) - 1):
        lo = correction_bins[i]
        hi = correction_bins[i + 1]

        mask = (
            (bg_inc >= lo)
            & (bg_inc < hi)
        )

        if np.sum(mask) < 20:
            continue

        centers.append((lo + hi) / 2)
        medians.append(np.nanmedian(bg_if[mask]))

    centers = np.asarray(centers)
    medians = np.asarray(medians)

    if len(centers) >= 3:
        coef = np.polyfit(
            centers,
            medians,
            2,
        )

        expected = np.polyval(coef, INC)

        corrected = IF / expected

        correction_mask = (
            crater
            & valid
            & np.isfinite(expected)
            & (expected > 0)
        )

        control_corrected_mask = (
            background
            & valid
            & np.isfinite(expected)
            & (expected > 0)
        )

        print()
        print("--- ILLUMINATION-CORRECTED RESULT ---")
        print(
            "Crater corrected median:",
            np.nanmedian(corrected[correction_mask]),
        )
        print(
            "Background corrected median:",
            np.nanmedian(corrected[control_corrected_mask]),
        )

        corrected_ratio = (
            np.nanmedian(corrected[correction_mask])
            / np.nanmedian(corrected[control_corrected_mask])
        )

        print(
            "Crater/background corrected ratio:",
            corrected_ratio,
        )

        plt.figure(figsize=(9, 6))
        plt.scatter(
            INC[correction_mask],
            corrected[correction_mask],
            s=5,
            alpha=0.35,
        )
        plt.axhline(1, linestyle="--")
        plt.xlabel("Incidence angle (deg)")
        plt.ylabel("Observed I/F / Expected I/F")
        plt.title("Illumination-Corrected Crater Contrast")
        plt.grid(True)
        save_figure(
            args.output / "illumination_corrected_crater.png"
        )

    # ------------------------------------------------------------------
    # 6. Radial profile
    # ------------------------------------------------------------------

    radial_rmax = 80

    IF_radial = IF_full[
        y0 - radial_rmax:y0 + radial_rmax + 1,
        x0 - radial_rmax:x0 + radial_rmax + 1,
    ]

    yy_r, xx_r = np.indices(IF_radial.shape)

    radial_dist = np.sqrt(
        (yy_r - radial_rmax) ** 2
        + (xx_r - radial_rmax) ** 2
    )

    radial_radii = []
    radial_medians = []

    for radius in range(0, radial_rmax, 2):
        mask = (
            (radial_dist >= radius)
            & (radial_dist < radius + 2)
        )

        value = np.nanmedian(IF_radial[mask])

        radial_radii.append(radius)
        radial_medians.append(value)

    radial_radii = np.asarray(radial_radii)
    radial_medians = np.asarray(radial_medians)

    outer = (
        (radial_radii >= 40)
        & (radial_radii <= 70)
    )

    background_median = np.nanmedian(
        radial_medians[outer]
    )

    interior = radial_radii <= 10

    interior_min = np.nanmin(
        radial_medians[interior]
    )

    rim_region = (
        (radial_radii >= 8)
        & (radial_radii <= 25)
    )

    rim_index = np.nanargmax(
        radial_medians[rim_region]
    )

    rim_candidates = radial_radii[rim_region]

    rim_radius = rim_candidates[rim_index]

    rim_peak = radial_medians[rim_region][rim_index]

    print()
    print("--- RADIAL CRATER PROFILE ---")
    print(
        "Outer background median I/F:",
        background_median,
    )
    print(
        "Interior minimum median I/F:",
        interior_min,
    )
    print(
        "Bright-rim peak radius:",
        rim_radius,
        "px =",
        rim_radius * PIXEL_SCALE_M,
        "m",
    )
    print(
        "Bright-rim peak I/F:",
        rim_peak,
    )
    print(
        "Peak/background ratio:",
        rim_peak / background_median,
    )
    print(
        "Interior/background ratio:",
        interior_min / background_median,
    )
    print(
        "Interior contrast:",
        (1 - interior_min / background_median) * 100,
        "% darker than background",
    )

    plt.figure(figsize=(9, 6))
    plt.plot(
        radial_radii * PIXEL_SCALE_M,
        radial_medians,
        "o-",
    )
    plt.axhline(
        background_median,
        linestyle="--",
        label="Background median",
    )
    plt.axvline(
        rim_radius * PIXEL_SCALE_M,
        linestyle="--",
        label="Rim peak",
    )
    plt.xlabel("Radius from crater center (m)")
    plt.ylabel("Median I/F")
    plt.title("Radial I/F Profile")
    plt.grid(True)
    plt.legend()

    save_figure(
        args.output / "robust_radial_crater_profile.png"
    )

    # ------------------------------------------------------------------
    # 7. Dark-region ellipse
    # ------------------------------------------------------------------

    ellipse_rmax = 50

    IF_ellipse = IF_full[
        y0 - ellipse_rmax:y0 + ellipse_rmax + 1,
        x0 - ellipse_rmax:x0 + ellipse_rmax + 1,
    ]

    yy_e, xx_e = np.indices(IF_ellipse.shape)

    cy_e = cx_e = ellipse_rmax

    dist_e = np.sqrt(
        (yy_e - cy_e) ** 2
        + (xx_e - cx_e) ** 2
    )

    ellipse_background = np.nanmedian(
        IF_ellipse[
            (dist_e >= 30)
            & (dist_e <= 45)
        ]
    )

    threshold = ellipse_background * 0.65

    dark = (
        np.isfinite(IF_ellipse)
        & (dist_e <= 25)
        & (IF_ellipse < threshold)
    )

    ys, xs = np.where(dark)

    if len(xs) >= 3:
        dx = xs - cx_e
        dy = ys - cy_e

        covariance = np.cov(
            np.vstack((dx, dy))
        )

        eigenvalues, eigenvectors = np.linalg.eigh(
            covariance
        )

        order = np.argsort(
            eigenvalues
        )[::-1]

        eigenvalues = eigenvalues[order]
        eigenvectors = eigenvectors[:, order]

        major = 2 * np.sqrt(eigenvalues[0])
        minor = 2 * np.sqrt(eigenvalues[1])

        axis_ratio = minor / major
        eccentricity = np.sqrt(
            1 - axis_ratio ** 2
        )

        orientation = np.degrees(
            np.arctan2(
                eigenvectors[1, 0],
                eigenvectors[0, 0],
            )
        )

        equivalent_diameter = (
            np.sqrt(major * minor)
            * PIXEL_SCALE_M
        )

        print()
        print("--- DARK FEATURE ELLIPSE ---")
        print(
            "Local background median I/F:",
            ellipse_background,
        )
        print(
            "Dark threshold:",
            threshold,
        )
        print(
            "Dark pixels:",
            len(xs),
        )
        print(
            "Major axis:",
            major,
            "px =",
            major * PIXEL_SCALE_M,
            "m",
        )
        print(
            "Minor axis:",
            minor,
            "px =",
            minor * PIXEL_SCALE_M,
            "m",
        )
        print(
            "Axis ratio:",
            axis_ratio,
        )
        print(
            "Eccentricity:",
            eccentricity,
        )
        print(
            "Major-axis orientation:",
            orientation,
            "deg",
        )
        print(
            "Centroid X offset:",
            np.mean(dx),
            "px",
        )
        print(
            "Centroid Y offset:",
            np.mean(dy),
            "px",
        )
        print(
            "Equivalent circular diameter:",
            equivalent_diameter,
            "m",
        )

    # ------------------------------------------------------------------
    # 8. 2-D morphology image
    # ------------------------------------------------------------------

    plt.figure(figsize=(8, 8))
    plt.imshow(
        IF_radial,
        origin="upper",
    )
    plt.axhline(radial_rmax, linestyle="--")
    plt.axvline(radial_rmax, linestyle="--")
    plt.xlabel("Sample offset")
    plt.ylabel("Line offset")
    plt.title("2-D Crater Morphology / I/F")
    plt.colorbar(label="I/F")

    save_figure(
        args.output / "crater_2d_morphology.png"
    )

    print()
    print("--- ANALYSIS COMPLETE ---")
    print("Output directory:", args.output)


if __name__ == "__main__":
    main()