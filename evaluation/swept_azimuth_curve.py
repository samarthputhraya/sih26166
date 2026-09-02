import numpy as np
import matplotlib.pyplot as plt
from evaluation.synthetic_data import make_pair
from evaluation.metrics import evaluate
from evaluation.logger import log_result
from baselines.sift_baseline import run_sift

def u8(img):
    """Convert a float32 [0,1] shaded-relief render to uint8 for SIFT."""
    return (img * 255.0).clip(0, 255).astype(np.uint8)

def crater_dem(n=420, seed=3, ncr=90):
    rng = np.random.default_rng(seed)
    dem = rng.normal(0, 3, (n, n))
    yy, xx = np.mgrid[0:n, 0:n]
    for _ in range(ncr):
        cx, cy = rng.integers(20, n-20, 2)
        rad = rng.integers(8, 34)
        depth = rad * rng.uniform(0.4, 1.0)
        d = np.sqrt((xx-cx)**2 + (yy-cy)**2)
        dem += np.where(d < rad, -depth*(1-(d/rad)**2), 0.0)
        dem += np.where((d >= rad) & (d < rad*1.25),
                        depth*0.28*(1-(d-rad)/(rad*0.25)), 0.0)
    return dem

if __name__ == "__main__":
    dem = crater_dem()

    results = []
    for d in (0, 30, 60, 90, 120, 150, 180):
        s, r, H_true, meta = make_pair(dem, pixel_size_m=10.0, sun_a=(45, 25),
                                        sun_b=(45+d, 25), rotation_deg=0.0,
                                        scale=1.0, shift_px=(10.0, -6.0))
        src_pts, ref_pts = run_sift(u8(s), u8(r))
        m = evaluate(r.shape, src_pts, ref_pts, H_true=H_true)
        log_result(f"synth_sun_{d:03d}", tier="synthetic", method="SIFT",
                   metrics=m, gsd_mpp=10.0,
                   notes=f"synthetic, DEM-rendered — sun azimuth difference {d} deg")
        results.append({"sun_diff": d, **m})
        print(f"{d:3d}deg  matches={m['n_matches']:4d}  "
              f"status={m['status']:16s}  inlier_ratio={m['inlier_ratio']:.3f}  "
              f"rmse_gt_px={m['rmse_gt_px']}")

        sun_diffs = [row["sun_diff"] for row in results]
    matches = [row["n_matches"] for row in results]
    rmse = [row["rmse_gt_px"] if row["rmse_gt_px"] is not None else np.nan for row in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.plot(sun_diffs, matches, "o-", label="n_matches")
    ax1.set_xlabel("Sun azimuth difference (deg)")
    ax1.set_ylabel("Match count")
    ax1.set_title("SIFT match count vs sun angle\n(synthetic, DEM-rendered)")
    ax1.grid(alpha=0.3)

    ax2.plot(sun_diffs, rmse, "o-", color="tab:red")
    ax2.axhline(0.5, color="gray", linestyle="--", label="Gate 2 threshold (0.5 px)")
    ax2.set_xlabel("Sun azimuth difference (deg)")
    ax2.set_ylabel("rmse_gt_px")
    ax2.set_title("SIFT accuracy vs sun angle\n(synthetic, DEM-rendered)")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("swept_azimuth_sift.png", dpi=150)
    print("Saved swept_azimuth_sift.png — upload to Drive, do NOT git add this file.")