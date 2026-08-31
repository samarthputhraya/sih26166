# [Day 3] Rohan — Kaguya TC, the Tier B+ pair

**Time: ~2 hrs.** Everything below was verified end to end on 31 Aug 2026 before this spec was
written. No step here is a guess.

> Your Day-3 row says *"Kaguya TC via AWS `--no-sign-request`"*. **You do not need the AWS CLI.**
> The bucket answers plain HTTPS with no account, no credentials and no login. Confirmed.

---

## Goal, in one sentence

One Kaguya TC scene on disk, overlapping our Chandrayaan-2 OHRC footprint, with its GSD, CRS and
NoData value recorded in `DATASET_CARD.md` — giving us the **Tier B+ cross-sensor pair at ~40×
scale ratio**.

---

## Why this one matters more than the others

Tier B+ is the pair that **proves scale invariance**, which is a core demand of the problem
statement. OHRC is 0.22977 m/px; this Kaguya scene is 9.3699 m/px. That is a **40.8× ratio** —
not the "~36×" our own Canonical Facts §4 estimates. **Use the measured number, not the doc's.**

A learned matcher degrades past roughly 4–8× on its own. So this pair either works because our
common-GSD resampling works, or it does not work at all. That contrast is Samartha's strongest
technical slide.

---

## Step 1 — Download (15 min)

Kaguya TC scenes live one-folder-per-scene. **This scene overlaps our OHRC footprint**
(OHRC covers lat −74.35…−73.50, lon 43.31…43.96):

```
https://astrogeo-ard.s3.us-west-2.amazonaws.com/moon/kaguya/terrain_camera/monoscopic/uncontrolled/TC1S2B0_01_03482S746E0433/TC1S2B0_01_03482S746E0433.tif
```

**22.6 MB. Verified downloadable and readable.** Grab the whole folder if you can — it also has
`.lbl`, `.stac.json` and a `.jpg` preview, all tiny.

Second-best neighbours, if you want more overlap (same orbit strip):

| scene | centre |
|---|---|
| `TC1S2B0_01_03482S732E0433` | S73.2 E43.3 |
| `TC1S2B0_01_03481S745E0442` | S74.5 E44.2 |
| `TC1S2B0_01_03481S731E0442` | S73.1 E44.2 |

Scene IDs encode position: `...S746E0433` = **S74.6, E43.3**. Use that to pick more yourself.

To list the bucket:
```
https://astrogeo-ard.s3.us-west-2.amazonaws.com/?list-type=2&max-keys=100&delimiter=/&prefix=moon/kaguya/terrain_camera/monoscopic/uncontrolled/
```

**Store it in `data/raw/`** — gitignored, so git will correctly ignore it. Do not `git add -f`.

> ⚠️ **Keep downloads OUT of any OneDrive-synced folder.** OneDrive does not read `.gitignore`, so
> a big file inside a synced folder gets uploaded to the cloud regardless. If your clone is inside
> OneDrive, put `data/raw/` contents somewhere else and point at it.

---

## Step 2 — Read it and record the truth (30 min)

```python
import sys; sys.path.insert(0, '.')
from core.io_loader import load
img, meta = load(r'data/raw/TC1S2B0_01_03482S746E0433.tif')
print(img.shape, meta['gsd_mpp'], meta['crs'])
```

**Expected output — if you get these, everything is correct:**

| field | value |
|---|---|
| shape | `(6220, 6222)` |
| `gsd_mpp` | `9.3698731836556` |
| `crs` | `Moon (2015) - Sphere / Ocentric / South Polar` |
| `transform` | `(293726.78, 9.36987, 0.0, 371993.34, 0.0, -9.36987)` |
| stored dtype | `int32` |

> **This works even though `rasterio` is dead on our machines.** The file is LZW-compressed, which
> `tifffile` cannot decode without `imagecodecs`; `io_loader` falls back to Pillow for the pixels
> while keeping tifffile's geo tags. You do not need to do anything — just do not "fix" it by
> installing GDAL.

---

## Step 3 — 🔴 The two things that will mislead you

**1. 51.8% of this scene is NoData, and the fill value is `-32768`.**
A naive `img.std()` returns ~16440, which is meaningless — it is measuring the fill, not the
Moon. Valid pixels are `0…3561`, mean 133, std 231. **Always mask before computing anything:**

```python
valid = img != -32768
print(img[valid].min(), img[valid].max(), img[valid].std())
```

**Record `nodata = -32768` in the dataset card.** Samrudh's metrics and Samartha's matcher both
need it; an unmasked fill region will silently wreck both.

**2. This is a polar scene and most of it is in deep shadow.**
At S74.6 the sun is very low. **That is real, not a bug** — and it is genuinely relevant, because
polar imaging is exactly what LUPEX cares about. But a tile that is 90% shadow produces no matches,
and that is a false negative, not a finding.

I searched the scene so you do not have to. Best fully-valid 640×640 windows, by how little of each
is in shadow:

| window | dark fraction | std |
|---|---|---|
| **`x=5120, y=2240`** | **4%** | 189 — **use this one** |
| `x=3840, y=2240` | 11% | 224 |
| `x=4800, y=1920` | 11% | 210 |
| `x=3200, y=640` | ~90% | — **avoid**, it is nearly all shadow |

Record the chosen window in the dataset card so Samartha and Rishabh use the same one.

---

## Acceptance criteria

1. `TC1S2B0_01_03482S746E0433.tif` (or a better-overlapping neighbour) on disk in `data/raw/`.
2. `load()` returns the exact values in the Step-2 table.
3. A new row in `data/DATASET_CARD.md` with **tier `B+`**, instrument `Kaguya TC`, the real source
   URL, download date, licence **CC0 1.0**, product ID, `gsd_mpp = 9.3699`, and
   **`nodata = -32768`**.
4. One line in chat giving the **pixel window** of a well-illuminated region you found.
5. A note in the card recording the measured **OHRC↔Kaguya ratio of 40.8×** (not 36×).

## Test cases

1. `load()` on the scene returns shape `(6220, 6222)` and `gsd_mpp == 9.3698731836556`.
2. `(img == -32768).mean()` is ≈ `0.518`.
3. Your chosen window contains **zero** `-32768` pixels and has `std > 15` after masking.

## Dependencies

- **Needs from others: nothing.** `core/io_loader.py` is committed and working (`ee383de`).
- **Delivers to:** Samartha (Tier B+ pair, Day 7 scale-invariance run) and Samrudh (Day 5 metrics).

## Do not

- Do not install GDAL, rasterio, or the AWS CLI. None is needed and rasterio is blocked on the
  demo laptop by Windows Application Control (which cannot be undone without reinstalling Windows).
- Do not commit the `.tif`. `*.tif` is gitignored deliberately.
- Do not quote "36×" for the scale ratio. The measured value for these two products is **40.8×**.
