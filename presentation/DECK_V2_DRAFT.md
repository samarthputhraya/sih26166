# SIH26166 national deck — v2 draft (18 Sep 2026)

> Draft text for the six-slide SIH 2026 template, rebuilt around the real-data evidence of
> 18 Sep. **Every figure is `[TBD — log]` until the evidence freeze (Day 7)**, when every run is
> repeated on the final commit and this file's audit table names the row behind each number.
> The template pointers stay byte-identical (`build_deck._check_pointers`). Audience: SAC-ISRO
> image-processing scientists reading the PDF cold, ranking us against every ISRO PS finalist.

## Slide 1 · TITLE PAGE

Problem Statement ID – `[portal format]` · title as the portal writes it · Space Technology ·
Software · Team ID `[portal]` · Team Name **LunaXX** (the 2026 rules forbid the institute's name).

## Slide 2 · IDEA TITLE

**Figure:** two real pairs side by side from the same site (74° S 43.6° E):
(a) Chandrayaan-2 OHRC → LRO NAC, 64/64 cells verified, `[inliers]` inliers;
(b) Kaguya TC → MI 1548 nm infrared: matcher fails, the independent check refuses it, the
fallback lands within one infrared pixel of the visible-band answer.

**Proposed Solution**
- A registration engine that aligns Chandrayaan-2 OHRC to lunar reference images to sub-pixel
  precision — and certifies, region by region, where that alignment can be trusted.

**Detailed explanation**
- Common ground scale; lighting removed so only edge direction survives; a learned matcher
  (LoFTR) finds thousands of correspondences; MAGSAC++ keeps the consistent ones; NCC refines
  each to sub-pixel.
- An independent check re-derives the alignment from raw pixels in an 8×8 grid, never seeing
  a match. Output: the registered product (GeoTIFF), the match points (CSV, GDAL/QGIS GCPs),
  five metrics and a trust map — verified / weak / no evidence.

**How it addresses the problem** (each on REAL data unless marked)
- Sun angle: one OHRC frame against `[n]` NAC frames `[3–153]°` apart in sun azimuth;
  `[k/n]` windows registered and verified.
- Scale: OHRC 0.25 m → NAC 0.93–1.25 m (3.7–5×), Kaguya 7.4 m, MI 14.8 m.
- Multi-modal: visible → 1548 nm infrared (Kaguya MI), declared and handled.
- Viewpoint: `[synthetic tilt sweep result]` (synthetic, exact truth).
- Sub-pixel, uniform: held-out median `[x] px` on the 0.93 m NAC grid; 3-image loops close to
  `[0.10] m`; full 8×8 coverage on lit windows.

**Innovation and uniqueness**
- Registration that knows when it is wrong — measured on real imagery: planted confident-but-
  wrong alignments caught `[x]%` at ≥ `[d]` m, `[y]%` false alarms.
- "No evidence" is its own state: in 6.9° polar sunlight, shadowed ground is reported as
  unmeasured, never as aligned.

## Slide 3 · TECHNICAL APPROACH

**Figure:** pipeline (drawn from `core/pipeline.py`) + thumbnails of the two deliverables.

**Technologies to be used**
- Python · OpenCV · PyTorch (CPU) · kornia LoFTR (Apache-2.0) · MAGSAC++ · tifffile/GeoTIFF.
- Data: Chandrayaan-2 OHRC (PDS4, geolocation grid) · LRO NAC EDR · Kaguya TC & MI maps · LOLA.
- Runs on a laptop CPU, offline: `[s]` s per 600 m window.

**Methodology and process**
- Archive geometry → common south-polar map → illumination normalisation → matching →
  MAGSAC++ → sub-pixel → independent area check → fallback if contradicted → export.
- Every run appends to one evidence log; the report generator rebuilds every number on this
  deck from it (`ops/make_report.py`).
- 36-hour finale plan: `[one line]`.

## Slide 4 · FEASIBILITY AND VIABILITY

**Figure:** the real sun sweep (`fig5_real_sun_sweep`) or the trust calibration (`fig6`).

**Analysis of the feasibility**
- Built and measured on real Chandrayaan-2 data, not proposed. Requirement checklist:
  illumination ✔ real · scale ✔ real · multi-modal ✔ real (infrared) · viewpoint ◐ synthetic ·
  sub-pixel ✔ held-out + loop closure · uniform distribution ✔ · registered product ✔ ·
  match points ✔ · metrics ✔.

**Potential challenges and risks**
- Shadow: at 6.9° sun elevation much of the OHRC frame is dark; those cells are "no evidence".
- Archive geometry: LRO NAC footprint corners (0.01°) are off ~150 m here — we correct them
  from the images, and report the disagreement.
- Relief parallax is not a homography; `[viewpoint + parallax result]`.
- Infrared at 62 m native: learned matching fails; correlation fallback is `[x]` px.

**Strategies for overcoming these challenges**
- Tile-level local transforms for relief; DEM-aware orthorectification with LOLA.
- IIRS / TMC-2 from PRADAN (registration requested); full-scene tiled processing.

## Slide 5 · IMPACT AND BENEFITS

- Landing-site safety at the lunar south pole (Chandrayaan-4 class sites; our test site is
  74° S): hazard maps are only as good as the alignment under them — every region carries its
  own verdict.
- OHRC's archive becomes co-registrable to LRO and Kaguya — mosaics, time series and change
  detection gated by trust.
- Economic: open source, CPU-only, offline; outputs load in QGIS/GDAL/ISIS today.

## Slide 6 · RESEARCH AND REFERENCES

- Makharia, Singla, Amitabh, Dube, Sharma — SAC ISRO 2025, arXiv:2509.04775 (the benchmark).
- Singh, Singla, Hemrajani, Dube, Amitabh, Patel — SAC 2026, arXiv:2604.25208 ("does not
  address geometric misalignment").
- Sun et al., LoFTR, CVPR 2021 · Barath et al., MAGSAC++, CVPR 2020 · Truong et al., PDC-Net 2021
  · Uss et al., IEEE TGRS 2016.
- Data: Chandrayaan-2 OHRC (ISRO PRADAN) · LRO LROC NAC (NASA PDS) · SELENE TC/MI (JAXA) · LOLA.
- Demo video `[unlisted link]` · code `[repo]`.
