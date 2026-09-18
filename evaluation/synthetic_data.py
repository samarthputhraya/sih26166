import numpy as np
import cv2
from evaluation.shaded_relief import render_shaded_relief

def view_matrix(shape, tilt_deg, tilt_azimuth_deg):
    """3x3 map from reference (nadir) pixels to the pixels of a view tilted `tilt_deg`
    off nadir toward image azimuth `tilt_azimuth_deg` (0 = +x, 90 = +y): the ground is
    foreshortened by cos(tilt) along that direction, about the image centre. At
    orbital altitude over a few-km footprint the keystone term is negligible, so this
    affine IS the viewpoint change for flat terrain; relief adds parallax (below)."""
    h, w = shape
    th, ph = np.radians(tilt_deg), np.radians(tilt_azimuth_deg)
    R = np.array([[np.cos(ph), -np.sin(ph)], [np.sin(ph), np.cos(ph)]])
    A = R @ np.diag([np.cos(th), 1.0]) @ R.T
    c = np.array([w / 2.0, h / 2.0])
    V = np.eye(3)
    V[:2, :2] = A
    V[:2, 2] = c - A @ c
    return V


def parallax_field(dem, pixel_size_m, tilt_deg, tilt_azimuth_deg):
    """Relief displacement of every ground pixel in the tilted view, in pixels:
    (z - mean z) * tan(tilt) / pixel_size along the tilt direction. The mean is
    removed - a constant offset is part of any registration's translation."""
    z = np.asarray(dem, np.float64)
    mag = (z - z.mean()) * np.tan(np.radians(tilt_deg)) / pixel_size_m
    ph = np.radians(tilt_azimuth_deg)
    return mag * np.cos(ph), mag * np.sin(ph)


def make_pair(dem, pixel_size_m,
              sun_a=(45, 30), sun_b=(225, 30), 
              rotation_deg=None, scale=None, shift_px=None, seed=0,
              tilt_deg=0.0, tilt_azimuth_deg=0.0, parallax=False):
    """Returns (source, reference, H_true, meta).

    reference = render(dem, sun_a)
    source    = warp(render(dem, sun_b), H_true)

    Two independent difficulties, both with EXACT ground truth:
      - illumination differs (real shadows, opposite direction)
      - geometry differs by a known homography H_true
    """
    rng = np.random.default_rng(seed)
    h, w = dem.shape

    # Strictly enforce Canonical Facts sampling ranges if not explicitly provided
    if rotation_deg is None:
        rotation_deg = 0.0
    
    if scale is None:
        # Default is a SOLVABLE pair. Callers who want the hard 1-20x sweep
        # (real orbital scale ratios) must pass scale= explicitly.
        scale = 1.0
        
    if shift_px is None:
        # +/- 20% of image width/height for footprint offset
        max_shift_x = 0.2 * w
        max_shift_y = 0.2 * h
        shift_px = (
            rng.uniform(-max_shift_x, max_shift_x),
            rng.uniform(-max_shift_y, max_shift_y)
        )

    # 1. Render terrain at specified sun angles (generating physically real shadows)
    ref_base = render_shaded_relief(dem, sun_azimuth_deg=sun_a[0], sun_elevation_deg=sun_a[1], pixel_size_m=pixel_size_m)
    src_base = render_shaded_relief(dem, sun_azimuth_deg=sun_b[0], sun_elevation_deg=sun_b[1], pixel_size_m=pixel_size_m)

    # 2. Build H_true (The ground-truth matrix mapping Source coordinates to Reference coordinates)
    center = (w / 2, h / 2)
    H_sim = cv2.getRotationMatrix2D(center, rotation_deg, scale)
    H_true = np.vstack([H_sim, [0.0, 0.0, 1.0]])
    H_true[0, 2] += shift_px[0]
    H_true[1, 2] += shift_px[1]

    # Viewpoint: the source is seen `tilt_deg` off nadir. V maps nadir (reference)
    # pixels to the tilted view, so the source -> reference truth gains inv(V).
    # Defaults (tilt 0) leave H_true exactly as before.
    truth_field = None
    if tilt_deg:
        V = view_matrix((h, w), tilt_deg, tilt_azimuth_deg)
        H_true = H_true @ np.linalg.inv(V)
        if parallax:
            # Relief moves each ground point along the tilt direction before the view
            # is taken. Rendered by remapping the source-sun render; the truth is no
            # longer one homography, so a per-pixel truth FIELD is returned in meta.
            dxp, dyp = parallax_field(dem, pixel_size_m, tilt_deg, tilt_azimuth_deg)
            gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
            src_base = cv2.remap(src_base.astype(np.float32), gx - dxp.astype(np.float32),
                                 gy - dyp.astype(np.float32), cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REFLECT)
            truth_field = (dxp, dyp)

    # 3. Warp src_base to create the Source image 
    # Since H_true maps Source -> Reference, we use its inverse to map Reference -> Source space
    H_inv = np.linalg.inv(H_true)
    source = cv2.warpPerspective(src_base, H_inv, (w, h), 
                                 flags=cv2.INTER_LINEAR, 
                                 borderMode=cv2.BORDER_CONSTANT, 
                                 borderValue=0)

    # 4. Package metadata for logging and swept-azimuth plotting
    meta = {
        "rotation_deg": rotation_deg,
        "scale": scale,
        "shift_px": shift_px,
        "sun_a": sun_a,
        "sun_b": sun_b,
        "sun_azimuth_diff": abs(sun_a[0] - sun_b[0]),
        "seed": seed,
        "tilt_deg": float(tilt_deg), "tilt_azimuth_deg": float(tilt_azimuth_deg),
        "parallax": bool(parallax and tilt_deg),
        # (dx, dy) per REFERENCE pixel: the content at reference pixel q appears in the
        # parallax-rendered plane at q + d(q), i.e. at source pixel inv(H_true)(q + d(q)).
        "parallax_field_px": truth_field,
    }

    return source, ref_base, H_true, meta

if __name__ == "__main__":
    # Sanity check generation
    print("Testing synthetic pair generation...")
    # Generate dummy DEM terrain (wavy surface)
    x, y = np.mgrid[-250:250, -250:250]
    dummy_dem = np.sin(np.sqrt(x**2 + y**2)/20) * 100
    
    source_img, ref_img, H_true, metadata = make_pair(dummy_dem, pixel_size_m=59.0)
    
    print(f"Source shape: {source_img.shape}")
    print(f"Reference shape: {ref_img.shape}")
    print(f"H_true mapping:\n{H_true}")
    print(f"Metadata generated: {metadata}")