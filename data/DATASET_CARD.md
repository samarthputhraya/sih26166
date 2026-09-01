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
| ~~`M108587604RE.IMG`~~ | ❌ **REJECTED** | LROC NAC | — | — | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0001/DATA/MAP/2009269/NAC/M108587604RE.IMG` | 2026-08-30 | PDS public domain | `nacr0000bc48` |

### Why `M108587604RE.IMG` is rejected

It decodes perfectly and contains **nothing**: 98.1% of its pixels sit in DN 32–46, std **1.42**,
no visible craters. Every numeric check passed while the image was empty, and it made an early
dry-run figure look ~10× better than reality.

**Do not use it, and do not delete it** — it is our worked example of Known Issue #6, *"a green
pipeline says nothing about whether its input is real."* Any new product must clear **std > 10**
and be **looked at** before it goes in the table above.

---

## The Tier B+ pair — CH-2 OHRC ↔ Kaguya TC

This is the pair that **proves scale invariance**, which the problem statement demands.

| | CH-2 OHRC | Kaguya TC |
|---|---|---|
| GSD | 0.22977000623605362 m/px | 9.3698731836556 m/px |
| acquired | 2020-02-29T07:39:31Z | 2008-07-20T14:48:03Z |
| footprint (lon) | 43.3595 … 43.9577 | 41.1047 … 45.4980 |
| footprint (lat) | −74.3661 … −73.5168 | −75.3535 … −73.7750 |

**Measured overlap: 0.598° longitude × 0.591° latitude.** Both footprints were read from the
products themselves — OHRC from its 113,498-row geometry CSV, Kaguya from its STAC `bbox`.

> 🔴 **Scale ratio is 40.78×, not 36×.** Canonical Facts §4 estimates ~36×; the measured value for
> *these two products* is **40.78×** (9.3698731836556 ÷ 0.22977000623605362). **Quote 40.8×.**
> A learned matcher degrades past roughly 4–8× unaided, so this pair either works because the
> common-GSD resampling works, or it does not work at all.

### Kaguya scene — the two things that will mislead you

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

## Still outstanding — Rohan's queue

1. 🔴 **Tier C (multi-modal) has no data and no owner.** It is in the problem-statement *title* and
   is a hard Gate-2 criterion on Day 8. Candidates: Chandrayaan-1 M3 (imaging spectrometer) or an
   LRO Diviner / Mini-RF product. **An owner must be decided by Day 5.**
2. **Tier A pairs do not exist yet.** Route is `EDRNAC4` with incidence filtered to 20–80° — see the
   policy note above. Needed by Risheeth (Day 4) and Samrudh (Day 6).
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
- **Data lives outside the repo.** The Kaguya scene is at
  `C:\Users\samar\sih26166_data\raw\` — *not* in `data/raw/`, because this clone sits inside
  OneDrive and OneDrive ignores `.gitignore`. Each machine's path is in `data_path.txt`.
- **No images or archives in git.** `*.tif`, `*.IMG` and `*.zip` are gitignored deliberately.
