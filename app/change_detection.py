import cv2
import numpy as np


def classify(cnt, img_a, img_b):
    """
    Classify a detected region.

    Returns:
        (label, colour)
    """

    x, y, w, h = cv2.boundingRect(cnt)

    # Measure how elongated the region is.
    elong = max(w, h) / max(min(w, h), 1)

    # Measure the average intensity INSIDE the detected region.
    # This is more reliable than sampling one centroid pixel,
    # especially for crescent/ring-shaped regions.
    region = np.zeros(img_a.shape, np.uint8)
    cv2.drawContours(region, [cnt], -1, 255, -1)

    a_val = float(cv2.mean(img_a, mask=region)[0])
    b_val = float(cv2.mean(img_b, mask=region)[0])

    # Long, thin regions are likely to be shadows.
    if elong > 4:
        return "shadow?", (0, 200, 200)

    # Region became significantly brighter.
    if b_val > a_val + 40:
        return "new bright", (0, 255, 0)

    # Region became significantly darker.
    if a_val > b_val + 40:
        return "disappeared", (255, 80, 0)

    # Cannot confidently classify.
    return "uncertain", (160, 160, 160)


def detect_changes(
    img_a,
    img_b,
    gsd_mpp,
    thresh=30,
    min_area_px=50,
    edge_margin_frac=0.05
):
    """
    Detect changes between two aligned grayscale images.

    Parameters:
        img_a: First aligned grayscale image.
        img_b: Second aligned grayscale image.
        gsd_mpp: Ground sample distance in metres per pixel.
        thresh: Difference threshold.
        min_area_px: Minimum detected area in pixels.
        edge_margin_frac: Fraction of the image edge to ignore.

    Returns:
        overlay: BGR image containing detected changes.
        changes: List of detected change dictionaries.
    """

    # ---------------------------------------------------------
    # 1. Check image inputs
    # ---------------------------------------------------------

    if img_a is None or img_b is None:
        raise ValueError(
            "One or both input images could not be loaded."
        )

    if len(img_a.shape) != 2 or len(img_b.shape) != 2:
        raise ValueError(
            "Input images must be grayscale."
        )

    # ---------------------------------------------------------
    # 2. Check GSD
    # ---------------------------------------------------------

    if gsd_mpp is None:
        raise ValueError(
            "gsd_mpp is required - get it from the catalogue"
        )

    if gsd_mpp <= 0:
        raise ValueError(
            "gsd_mpp must be greater than zero"
        )

    # ---------------------------------------------------------
    # 3. Normalise BOTH images, ALWAYS, and INDEPENDENTLY
    # ---------------------------------------------------------
    #
    # FIXED Day 6 (4 Sep 2026). This block used to do two things wrong, and
    # together they made the detector return a different answer depending on what
    # the caller had already done to the pixels.
    #
    # (a) It only normalised when the input was NOT uint8. So the Streamlit UI,
    #     which hands over percentile-stretched uint8 for display, skipped it
    #     entirely, while ops/gate_tier_d_changes.py, which hands over raw
    #     float32, went through it. Same detector, same pair, 183 candidates
    #     against 1.
    #
    # (b) Worse, it scaled both images by their COMBINED max. On
    #     pair_04_tierD_native the reference peaks at 37488 DN and the aligned
    #     optical image at 2040 - an 18x mismatch, which is normal for a
    #     multi-modal pair because an optical image and an elevation hillshade
    #     share no radiometric scale. Dividing both by 37488 crushed the optical
    #     image to a 2nd-98th percentile range of [0, 5] and a standard deviation
    #     of 1.35. Nothing can differ by `thresh` = 30 DN in an image that is
    #     entirely black, so the detector reported 1 candidate. That was not a
    #     conservative result, it was total contrast collapse, and it happened on
    #     precisely the multi-modal case this project exists to handle.
    #
    # The fix is a robust per-image percentile stretch that always runs. Each
    # image is scaled by its own 2nd-98th percentile, so a difference in absolute
    # DN range between two sensors can no longer annihilate the darker one, and
    # `thresh` means the same thing whoever calls this.
    #
    # THE TRADE-OFF, STATED: normalising each image separately also normalises
    # away a genuine uniform brightness difference between them. For same-sensor
    # change detection joint scaling would preserve that. We take per-image,
    # because across sensors and modalities raw DN is not comparable in the first
    # place - and the failure mode of the joint version is silent garbage rather
    # than a slightly wrong answer.

    # ONE MORE TRAP, and it is why this does not fall back to min/max. A stretch
    # needs a scale, and a near-uniform image does not have one. If the 2nd and
    # 98th percentiles coincide, min/max would take whatever tiny feature exists -
    # a 35 DN circle on a flat 100 DN field - and blow it up to the full 0-255
    # range, turning a deliberately ambiguous difference into a confident "new
    # bright". Classification here is threshold-based (+/-40 DN), so amplifying
    # the scale silently rewrites the labels. When there is no robust range to
    # stretch by, we pass the image through unchanged instead.

    def _stretch(img):
        a = np.asarray(img, dtype=np.float64)
        finite = a[np.isfinite(a)]
        if finite.size == 0:
            return np.zeros(a.shape, np.uint8)
        lo, hi = np.percentile(finite, [2, 98])
        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            # No robust dynamic range: leave the values where they are.
            return np.clip(np.nan_to_num(a), 0, 255).astype(np.uint8)
        return np.clip((a - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)

    img_a = _stretch(img_a)
    img_b = _stretch(img_b)

    # ---------------------------------------------------------
    # 4. Make sure both images have the same size
    # ---------------------------------------------------------

    if img_a.shape != img_b.shape:
        img_b = cv2.resize(
            img_b,
            (img_a.shape[1], img_a.shape[0])
        )

    # ---------------------------------------------------------
    # 5. Calculate absolute difference
    # ---------------------------------------------------------

    diff = cv2.absdiff(img_a, img_b)

    # ---------------------------------------------------------
    # 6. Remove small noise
    # ---------------------------------------------------------

    smooth = cv2.medianBlur(diff, 5)

    # ---------------------------------------------------------
    # 7. Threshold the difference
    # ---------------------------------------------------------

    _, mask = cv2.threshold(
        smooth,
        thresh,
        255,
        cv2.THRESH_BINARY
    )

    # ---------------------------------------------------------
    # 8. Morphological cleanup
    # ---------------------------------------------------------

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # ---------------------------------------------------------
    # 9. Remove image-border regions
    # ---------------------------------------------------------

    h, w = mask.shape

    margin = int(
        edge_margin_frac * min(h, w)
    )

    # IMPORTANT:
    # When margin == 0, mask[-0:, :] would mean the entire image.
    # Only perform border cleanup when there is an actual margin.
    if margin > 0:
        mask[:margin, :] = 0
        mask[-margin:, :] = 0
        mask[:, :margin] = 0
        mask[:, -margin:] = 0

    # ---------------------------------------------------------
    # 10. Find contours
    # ---------------------------------------------------------

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # ---------------------------------------------------------
    # 11. Create colour overlay
    # ---------------------------------------------------------

    overlay = cv2.cvtColor(
        img_a,
        cv2.COLOR_GRAY2BGR
    )

    changes = []

    # ---------------------------------------------------------
    # 12. Process every detected region
    # ---------------------------------------------------------

    for cnt in contours:

        area_px = cv2.contourArea(cnt)

        # Ignore tiny regions.
        if area_px < min_area_px:
            continue

        # Bounding box.
        x, y, bw, bh = cv2.boundingRect(cnt)

        # Centroid.
        M = cv2.moments(cnt)

        if M["m00"]:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx = x + bw // 2
            cy = y + bh // 2

        # Classify the region.
        label, colour = classify(
            cnt,
            img_a,
            img_b
        )

        # Calculate real-world area.
        area_m2 = area_px * (gsd_mpp ** 2)

        # Store result.
        changes.append({
            "bbox": [x, y, bw, bh],
            "centroid_px": [cx, cy],
            "area_px": float(area_px),
            "area_m2": round(area_m2, 2),
            "classification": label
        })

        # Draw bounding box.
        cv2.rectangle(
            overlay,
            (x, y),
            (x + bw, y + bh),
            colour,
            2
        )

        # Draw label.
        cv2.putText(
            overlay,
            label,
            (x, max(y - 6, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            colour,
            1
        )

    return overlay, changes