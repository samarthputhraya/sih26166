import cv2
import numpy as np


def classify(cnt, img_a, img_b, cx, cy):
    """
    Classify a detected region.

    Returns:
        (label, colour)
    """

    x, y, w, h = cv2.boundingRect(cnt)

    # Measure how elongated the region is
    elong = max(w, h) / max(min(w, h), 1)

    # Pixel intensity at the centre
    a_val = int(img_a[cy, cx])
    b_val = int(img_b[cy, cx])

    # Long, thin regions are likely to be shadows
    if elong > 4:
        return "shadow?", (0, 200, 200)

    # Region became significantly brighter
    if b_val > a_val + 40:
        return "new bright", (0, 255, 0)

    # Region became significantly darker
    if a_val > b_val + 40:
        return "disappeared", (255, 80, 0)

    # Cannot confidently classify
    return "uncertain", (160, 160, 160)


def detect_changes(
    img_a,
    img_b,
    gsd_mpp=0.5,
    thresh=30,
    min_area_px=50,
    edge_margin_frac=0.05
):
    """
    Detect changes between two aligned grayscale images.

    Parameters:
        img_a: First aligned grayscale image.
        img_b: Second aligned grayscale image.
        gsd_mpp: Metres per pixel.
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
        raise ValueError("One or both input images could not be loaded.")

    if len(img_a.shape) != 2 or len(img_b.shape) != 2:
        raise ValueError("Input images must be grayscale.")

    # ---------------------------------------------------------
    # 2. Convert non-uint8 images using a common scale
    # ---------------------------------------------------------

    if img_a.dtype != np.uint8 or img_b.dtype != np.uint8:

        combined_max = max(
            float(img_a.max()),
            float(img_b.max())
        )

        if combined_max > 0:

            img_a = np.clip(
                img_a.astype(np.float32) * 255.0 / combined_max,
                0,
                255
            ).astype(np.uint8)

            img_b = np.clip(
                img_b.astype(np.float32) * 255.0 / combined_max,
                0,
                255
            ).astype(np.uint8)

        else:
            img_a = img_a.astype(np.uint8)
            img_b = img_b.astype(np.uint8)

    # ---------------------------------------------------------
    # 3. Make sure both images have the same size
    # ---------------------------------------------------------

    if img_a.shape != img_b.shape:
        img_b = cv2.resize(
            img_b,
            (img_a.shape[1], img_a.shape[0])
        )

    # ---------------------------------------------------------
    # 4. Calculate absolute difference
    # ---------------------------------------------------------

    diff = cv2.absdiff(img_a, img_b)

    # ---------------------------------------------------------
    # 5. Remove small noise
    # ---------------------------------------------------------

    smooth = cv2.medianBlur(diff, 5)

    # ---------------------------------------------------------
    # 6. Threshold the difference
    # ---------------------------------------------------------

    _, mask = cv2.threshold(
        smooth,
        thresh,
        255,
        cv2.THRESH_BINARY
    )

    # ---------------------------------------------------------
    # 7. Morphological cleanup
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
    # 8. Remove image-border regions
    # ---------------------------------------------------------

    h, w = mask.shape

    margin = int(
        edge_margin_frac * min(h, w)
    )

    mask[:margin, :] = 0
    mask[-margin:, :] = 0
    mask[:, :margin] = 0
    mask[:, -margin:] = 0

    # ---------------------------------------------------------
    # 9. Find contours
    # ---------------------------------------------------------

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # ---------------------------------------------------------
    # 10. Create colour overlay
    # ---------------------------------------------------------

    overlay = cv2.cvtColor(
        img_a,
        cv2.COLOR_GRAY2BGR
    )

    changes = []

    # ---------------------------------------------------------
    # 11. Process every detected region
    # ---------------------------------------------------------

    for cnt in contours:

        area_px = cv2.contourArea(cnt)

        # Ignore tiny regions
        if area_px < min_area_px:
            continue

        # Bounding box
        x, y, bw, bh = cv2.boundingRect(cnt)

        # Centroid
        M = cv2.moments(cnt)

        if M["m00"]:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx = x + bw // 2
            cy = y + bh // 2

        # Classify the region
        label, colour = classify(
            cnt,
            img_a,
            img_b,
            cx,
            cy
        )

        # Calculate real-world area
        area_m2 = area_px * (gsd_mpp ** 2)

        # Store result
        changes.append({
            "bbox": [x, y, bw, bh],
            "centroid_px": [cx, cy],
            "area_px": float(area_px),
            "area_m2": round(area_m2, 2),
            "classification": label
        })

        # Draw bounding box
        cv2.rectangle(
            overlay,
            (x, y),
            (x + bw, y + bh),
            colour,
            2
        )

        # Draw label
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