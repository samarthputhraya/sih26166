# SIH26166 — Dataset Card

Provenance for every file we use. One row per file, filled at download time.

Blank means "not known". Never guess — a wrong GSD or sun angle silently
corrupts Samrudh's analysis and cannot be caught downstream.

> ⚠️ **Rohan — this file is yours. Samartha filled it in on Day 3 (1 Sep) while your PC was down,
> because Samrudh's Day-5 metrics and Samartha's Day-7 scale run were both blocked on it.**
> Every number below was measured from the products themselves, not copied from a doc — the
> commands are in "How each number was obtained" at the bottom so you can re-run them yourself.
> **Please read that section and re-run at least one row before Gate 5**, where you have to explain
> this file cold.

---

## Dataset policy

LROC EDR products are retained as source/reference data only. They are **not** used to establish
Tier A illumination differences, because the EDR label carries no illumination geometry.

🔴 **Correction (1 Sep).** An earlier version of this card said Tier A would use **`SDRPHO`**
products. **`SDRPHO` does not exist.** The product is spelled **`SDPPHO`** (P, not R) — and it is
still the wrong route, because ODE reports `ValidIncidenceAngles = F` for it.

**The Tier A route is `EDRNAC4`**, which has `ValidIncidenceAngles = T`. When querying ODE, filter
incidence to **20–80°**: the service also returns 139° and 164°, which are night-side and unusable.

Kaguya comparison data is **downloaded**, not streamed over HTTP/GDAL — `rasterio` is blocked on the
demo laptop by Windows Smart App Control and cannot be enabled without reinstalling Windows.

---

## Files

| file | tier | instrument | gsd (m/px) | nodata | source URL | downloaded | licence | product ID |
|---|---|---|---|---|---|---|---|---|
| `ch2_ohr_ncp_20200229T0739312111_d_img_d18.img` | source (CH-2) | Chandrayaan-2 OHRC | **0.22977000623605362** | — | ISRO PDS4 / archive.org mirror | 2026-08-31 | ISRO open data | `urn:isro:isda:ch2_cho.ohr:data_calibrated:ch2_ohr_ncp_20200229t0739312111_d_img_d18` |
| `TC1S2B0_01_03482S746E0433.tif` | **B+** | Kaguya/SELENE Terrain Camera (TC) | **9.3698731836556** | **−32768** | `https://astrogeo-ard.s3.us-west-2.amazonaws.com/moon/kaguya/terrain_camera/monoscopic/uncontrolled/TC1S2B0_01_03482S746E0433/TC1S2B0_01_03482S746E0433.tif` | 2026-09-01 | **CC0-1.0** | `TC1S2B0_01_03482S746E0433` |
| `ldem_60s_60m.img` (windowed) | **D** | LRO LOLA (elevation) | **60.0** | — | `https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/lola_gdr/polar/img/ldem_60s_60m.img` | 2026-09-01 | PDS public domain | `LRO-L-LOLA-3-RDR-V1.0` |
| ~~`M108587604RE.IMG`~~ | ❌ **REJECTED** | LROC NAC | — | — | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0001/DATA/MAP/2009269/NAC/M108587604RE.IMG` | 2026-08-30 | PDS public domain | `nacr0000bc48` |

### Why `M108587604RE.IMG` is rejected — and why the stated reason was wrong

The rejection **stands**, but the reason first recorded for it does not, and the correction matters
more than the rejection.

| | `M108587604RE` | a good Tier A frame |
|---|---|---|
| raw std | 1.5 | 4.4 |
| DN span | **14** | **51** |
| **row-to-row correlation** | **0.352** | **0.973** |
| length | 1024 lines (a short non-science frame) | 52,224 lines |

🔴 **`std > 10` is the wrong test for LROC NAC, and it nearly cost us Tier A.** That threshold was
calibrated on **calibrated** imagery — CH-2 OHRC is `data_calibrated` and has std 32.4. **NAC EDR
is raw and companded**: good frames sit at std 4–6 with ~93% of pixels inside a 16-DN band.
Applied to raw EDR, `std > 10` **rejected all six of the best Tier A pairs** on the first pass.

🔴 **And stretching proves nothing.** A 2–98% percentile stretch takes `M108587604RE` from std 1.5
to **59.8** and produces a picture that looks like terrain. It is amplified noise. The stretch is
for *looking*; it is not evidence.

**The test that actually works is row-to-row correlation** — terrain is spatially coherent, sensor
noise is not. 0.352 versus 0.973 separates them cleanly where every intensity statistic fails.
Implemented as `looks_like_terrain()` in [`ops/find_tier_a_pairs.py`](../ops/find_tier_a_pairs.py).

**Do not use `M108587604RE`, and do not delete it** — it is our worked example of Known Issue #6,
*"a green pipeline says nothing about whether its input is real."*

---

## The Tier B+ pair — CH-2 OHRC ↔ Kaguya TC

This is the pair that **proves scale invariance**, which the problem statement demands.

| | CH-2 OHRC | Kaguya TC |
|---|---|---|
| GSD | 0.22977000623605362 m/px | 9.3698731836556 m/px |
| acquired | 2020-02-29T07:39:31Z | 2008-07-20T14:48:03Z |
| footprint (lon) | 43.3595 … 43.9577 | 41.1047 … 45.4980 |
| footprint (lat) | −74.3661 … −73.5168 | −75.3535 … −73.7750 |
| incidence angle | *(none in product)* | **86.548°** |
| sun azimuth | *(none in product)* | **284.901°** |
| sun elevation | *(none in product)* | **16.98°** |
| emission / phase | *(none in product)* | 15.650° / 90.612° |

> ✅ **Kaguya DOES carry sun geometry — added 1 Sep.** Known issue #5 records that CH-2 OHRC has
> no illumination geometry anywhere in its product, and that stands. But nobody had checked
> Kaguya, and it has the full set: `INCIDENCE_ANGLE`, `SOLAR_AZIMUTH_ANGLE`, `EMISSION_ANGLE` and
> `PHASE_ANGLE` in the PDS label, plus `view:sun_elevation` in the STAC sidecar. Both files are
> now on the Drive at `SIH26166_DATA/raw/`.
>
> **This means Rohan can fill the sun-angle columns of `pairs_catalogue.csv` for the Kaguya side**
> (they stay blank for CH-2), and Samrudh has one real measured sun geometry rather than only
> synthetic ones.
>
> ⚠️ **Incidence 86.5° is a grazing sun** — 3.5° off the horizon. That is why the scene is a polar
> one with long shadows, and it is worth saying out loud rather than quoting "86.5°" as if it were
> ordinary. It also explains why 51.82% of the frame is NoData.

**Measured overlap: 0.598° longitude × 0.591° latitude.** Both footprints were read from the
products themselves — OHRC from its 113,498-row geometry CSV, Kaguya from its STAC `bbox`.

> 🔴 **Scale ratio is 40.78×, not 36×.** Canonical Facts §4 estimates ~36×; the measured value for
> *these two products* is **40.78×** (9.3698731836556 ÷ 0.22977000623605362). **Quote 40.8×.**
> A learned matcher degrades past roughly 4–8× unaided, so this pair either works because the
> common-GSD resampling works, or it does not work at all.

### Kaguya scene — the two things that will mislead you

**0. The PDS label lists DIFFERENT invalid values, and they are not the ones to mask.**
The JAXA label declares `INVALID_VALUE = (-20000, -21000, -22000, -23000)`. Those apply to the
original `.img`, **not** to the GeoTIFF we use. Checked 1 Sep: **none of the four appears in the
`.tif`** — the only sentinel present is `−32768`, at exactly 51.82%, which the STAC sidecar states
outright (`"nodata": -32768.0`, `"valid_percent": 48.18`). **Mask −32768 and nothing else.**

**1. 51.82% of the scene is NoData, fill value `−32768`.**
An unmasked `img.std()` returns **16440**, which measures the fill, not the Moon. Masked, the valid
pixels are 0 … 3561, mean 133.3, std 230.8. **Always mask first:**

```python
valid = img != -32768
```

**2. It is a polar scene (S74.6) and much of it is in deep shadow.** That is real, not a bug — and
it is relevant, because polar imaging is exactly what LUPEX cares about. But a mostly-shadow tile
produces no matches, and that is a false negative, not a finding.

**Verified 640×640 windows** (measured 1 Sep, all with zero NoData pixels):

| window | dark fraction | std | verdict |
|---|---|---|---|
| **`x=5120, y=2240`** | **2.9%** | 189.2 | ✅ **use this one** |
| `x=3840, y=2240` | 10.3% | 223.8 | ✅ usable |
| `x=4800, y=1920` | 10.0% | 209.8 | ✅ usable |
| `x=3200, y=640` | 96.3% | 28.1 | ❌ avoid — nearly all shadow |

**Everyone use `x=5120, y=2240`** so Samartha, Samrudh and Rishabh are all measuring the same ground.

---

---

## 🔴 SLDEM2015 does not cover our demo site

**Verified 1 Sep 2026.** `SLDEM2015` is named as the Tier D source in Canonical Facts §2, listed in
§3 as **"±60° lat"**, and scheduled as Rohan's Day-4 deliverable. **Our demo site is at −74°.**
The southernmost tile that exists is `sldem2015_256_60s_0s_*`. There is no tile for our site and
there never will be.

**The product that does cover us is LOLA `ldem_60s_60m`** — 60°S to 90°S at **60 m/px**, which is
effectively the same resolution as SLDEM2015's 59 m/px, so nothing is lost.

| | value |
|---|---|
| coverage | −60° to −90° latitude, all longitudes |
| resolution | 60 m/px (`MAP_SCALE`), 505.389 pix/deg |
| projection | south polar stereographic, sphere radius 1737.4 km |
| format | raw 31040 × 31040 `LSB_INTEGER`, 16-bit, **no header** (detached `.lbl`) |
| elevation | `height_m = DN × 0.5`, relative to a 1737.4 km sphere |
| full size | 1.93 GB — **do not download it whole** |

**Use [`ops/fetch_lola_dem.py`](../ops/fetch_lola_dem.py)**, which range-fetches only the rows it
needs (~34 MB for our site) and carries the verified projection. Run it directly to self-test.

> 🔴 **The sign trap.** `line = OFFSET − Y/scale`, **minus**, not plus. Getting it the wrong way
> round lands you **180° away in longitude at the same latitude** — and it still returns
> plausible-looking lunar elevations, so nothing warns you. This happened while preparing this
> card: the first window fetched showed 332 m of relief and looked believable; the correct window
> shows **3238 m**. `self_test()` in that module reproduces the trap deliberately.

**Measured at our site** (OHRC footprint, from the corrected window): elevation −1078 … +2160 m,
**relief 3238 m**, and shaded relief passes the `std > 10` texture check at every sun elevation
tested (25.4 at 25°, 28.1 at 10°).

---

## Tier A — route solved, 47 candidate pairs

**The planned route does not work.** `oderest.rsl.wustl.edu` — the ODE REST host our policy note
points at — **does not resolve** (checked 1 Sep 2026). `ode.rsl.wustl.edu` resolves but serves no
`/live2/` endpoint. There is no live API to query.

**The PDS cumulative index carries the same geometry and cannot go down.**
`LRO-L-LROC-2-EDR-V1.0/LROLRC_0003/INDEX/CUMINDEX.TAB` is 225,950 rows × 901 fixed bytes with
`PRODUCT_ID`, `CENTER_LATITUDE/LONGITUDE`, `INCIDENCE/EMISSION/PHASE_ANGLE` and the file path.
Streaming it and filtering to incidence 20–80° leaves **130,398 usable frames**.

Requiring centres within 0.02° (~0.6 km) and incidence differing ≥15°, from standard LE/RE frames:
**47 candidate pairs.** Top of the list:

| Δ incidence | separation | A | inc | B | inc | lat | lon |
|---|---|---|---|---|---|---|---|
| **47.9°** | 0.3 km | `M118064253RE` | 75.0° | `M122787393RE` | 27.1° | −18.06 | 271.80 |
| 40.1° | 0.3 km | `M119292791RE` | 60.7° | `M126378315LE` | 20.6° | 2.33 | 85.30 |
| 39.2° | 0.4 km | `M119326702LE` | 60.7° | `M126405425LE` | 21.4° | 1.17 | 80.56 |
| 39.0° | 0.2 km | `M109807869RE` | 39.4° | `M118057027RE` | 78.4° | −40.32 | 273.25 |

Reproduce with [`ops/find_tier_a_pairs.py`](../ops/find_tier_a_pairs.py).

> 🔴 **The two candidates previously recorded in STATUS are NOT a Tier A pair.**
> `M124545845LE` (inc 25.2°) and `M102128467RE` (inc 79.3°) have the right 54° of sun-angle
> difference, but their centres are **0.696° apart — about 21 km**. They are different sites.
> A sun-angle test needs the *same ground*.

**A NAC EDR is 264 MB, but you do not download it.** It is uncompressed 8-bit with fixed
5064-byte records and the server sends `Accept-Ranges: bytes`, so a 640-line crop is a
**3.2 MB range request**. `crop()` in that module does it.

⚠️ **Pick by texture, not by incidence difference alone.** The 47.9° pair above sits on
low-contrast mare and is a poor matching target. Rank candidates with `looks_like_terrain()`
before committing to one. ⚠️ **And match resolution**: LRO's orbit ranges ~20–165 km, so two NAC
frames of the same ground can differ several-fold in scale. `find_pairs()` enforces ≤1.25×;
ignoring it drops 47 pairs to 30 and silently turns a sun-angle test into a scale test.

### 🔴 Selecting a pair is solved. **Cutting one is not.** — attempted 1 Sep, honest negative

Best candidate: `M118790149LE` (inc 69.3°) ↔ `M125868733LE` (inc 30.9°), 38.4° apart, 0.55 vs
0.56 m/px, farside highlands at lat −25.39 lon 162.14, both frames `row_corr` > 0.97.

**Crops cut from it do not overlap, and I could not make them.** What was tried:

| attempt | result |
|---|---|
| cut 640² from each frame's middle | LoFTR 221 matches → **7 inliers**, residual 132 px |
| cut 2048² from each middle | SIFT 3 matches, 0 inliers at all four rotations |
| cut at the four-corner common ground | 283 matches → **7 inliers** |
| best-textured window in the overlap | 283 matches → **7 inliers** |
| all four orientations of the reference | **7, 8, 8, 8 inliers** — none jumps |

That last row is the verdict: if the crops overlapped, *one* orientation would jump to dozens.

**Two traps found on the way, both worth knowing:**

1. **Frame centres 0.41 km apart is NOT "the same crop position".** At 0.55 m/px that is
   **745 pixels** — wider than a 640 px crop, so middle-vs-middle crops miss each other entirely.
2. **`NORTH_AZIMUTH` differs by 185°** between the two frames (87.05° vs 272.47°), and their
   corner longitudes run in opposite directions. They are not in the same orientation.
3. ⚠️ **SIFT finding zero matches proves nothing here.** Failing across 38° of incidence is the
   *expected* Tier A result — it is what the tier exists to demonstrate. Only a matcher robust to
   illumination (LoFTR) can be used to test overlap, and it must be run at several orientations.

**Why it cannot be fixed with what we have:** a NAC frame is a 52,224-line pushbroom strip. Four
corner coordinates cannot model ground-track curvature and attitude variation along it, and the
residual error exceeds a 640 px crop. The EDR carries no map projection.

**The route that will work — needs ~2 hrs, not yet done:** use **map-projected** products from
`LRO-L-LROC-5-RDR-V1.0` (reachable, HTTP 200), where both frames can be cut at identical map
coordinates the way the Kaguya↔LOLA pair already is. Checked and ruled out: the `astrogeo-ard` S3
bucket that served Kaguya carries only LOLA under `moon/lro/`, no LROC.

> **Do not hand anyone a Tier A pair until crops from it produce a coherent inlier set.** A pair
> that does not overlap reads as "our method fails on cross-illumination" — the exact opposite of
> what it would actually mean.

---

## Still outstanding — Rohan's queue

1. 🔴 **Tier C (multi-modal) has no data and no owner.** It is in the problem-statement *title* and
   is a hard Gate-2 criterion on Day 8. Candidates: Chandrayaan-1 M3 (imaging spectrometer) or an
   LRO Diviner / Mini-RF product. **An owner must be decided by Day 5.**
2. ~~**Tier A pairs do not exist yet.**~~ ✅ **Route solved 1 Sep — 47 candidate pairs found.**
   See "Tier A" below. What remains is picking one and cutting the crops, which is ~1 hour.
3. **SLDEM tile for the demo site** — Samrudh's synthetic generator currently runs on a made-up
   crater surface. A real DEM tile would let the swept-illumination curve use real terrain.
4. **CH-3 landing-site NAC product IDs** — unverified. Rishabh needs them ~Day 6.
   ⚠️ These are *LROC NAC images of the CH-3 site*, not "Chandrayaan-3 imagery".

---

## How each number was obtained

Re-runnable, from the repo root, with the venv active. **Rohan: run at least one of these.**

```python
from core.io_loader import load
img, meta = load(r'C:/Users/samar/sih26166_data/raw/TC1S2B0_01_03482S746E0433.tif')

meta['gsd_mpp']            # 9.3698731836556
img.shape                  # (6220, 6222)
(img == -32768).mean()     # 0.5182
valid = img != -32768
img[valid].std()           # 230.8   (unmasked: 16440 - meaningless)
```

- **Kaguya licence, product ID, acquisition date, footprint** — from the scene's own
  `.stac.json` sidecar, fetched from the same S3 folder as the `.tif`.
- **OHRC GSD and product ID** — from `<isda:pixel_resolution>` and `<logical_identifier>` in
  `ch2_ohr_ncp_20200229T0739312111_d_img_d18.xml`. Not copied from any doc.
- **OHRC footprint** — min/max of the `Longitude` / `Lattitude` columns across all 113,498 rows of
  `..._g_grd_d18.csv`. ⚠️ That header really is spelled **`Lattitude`**, with two t's, while the
  label says `Latitude`. Match on the CSV's spelling or your reader returns nothing.

---

## Rules for this file

- **One row per file, filled at download time.** Blank means "not known" — never guess.
- **Every new product must clear `std > 10` (masked) and be looked at** before it is added.
- **The Drive now has `SIH26166_DATA/raw/`** with the Kaguya `.lbl` and `.stac.json` (the two
  provenance sidecars) plus a `README_raw.md` giving the exact one-line commands to re-fetch the
  three large files. The `.tif` (22.6 MB) and the LOLA window (34 MB) are **not** uploaded — both
  are reproducible in under a minute from a public URL, and `ops/fetch_lola_dem.py` fetches only
  the DEM rows we need rather than the full 1.93 GB.
- **Data lives outside the repo.** The Kaguya scene is at
  `C:\Users\samar\sih26166_data\raw\` — *not* in `data/raw/`, because this clone sits inside
  OneDrive and OneDrive ignores `.gitignore`. Each machine's path is in `data_path.txt`.
- **No images or archives in git.** `*.tif`, `*.IMG` and `*.zip` are gitignored deliberately.
