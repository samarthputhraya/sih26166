# Rohan — everything you need to do, in order

**Total time: about 4 hours.** You can stop after any Part and come back.

Every link and every number in this file was tested on 31 August 2026 before it was written.
Nothing here is a guess. If something doesn't work, it's a bug in this guide — tell me.

**Read this rule once, it explains a lot of the warnings below:**
`.gitignore` blocks images, PDFs and zips on purpose. When you `git add` one, **git says nothing
and does nothing**. It looks like it worked. It didn't. So: **big files → Google Drive. Text files
→ git.** Never use `git add -f`.

---

# PART A — Google Drive (20 min, do this first)

## A1. Check the folder exists

Samartha creates `SIH26166_DATA` and shares it with you. **Check your email for the share link.**

If you don't have it yet, message him — then skip to Part B and come back. Everything else works
without Drive.

## A2. Install Google Drive for Desktop

1. Go to `google.com/drive/download`, install it, sign in.
2. Find the shared `SIH26166_DATA` folder.
3. **Right-click it → "Make available offline".**

⚠️ **Do not skip step 3.** Without it, Drive keeps files as *links*, not real files, and Python
cannot open them. This breaks silently and you'd waste an hour.

## A3. Make these folders inside `SIH26166_DATA`

```
SIH26166_DATA/
├── raw_samples/         <- the big original downloads
├── pairs/               <- cropped image pairs (later, Day 5)
├── isro_user_guides/    <- the ISRO PDF manuals
├── weights/             <- Samartha puts the AI model here
└── demo_cache/          <- demo files (later)
```

## A4. What goes where — the only table you need

| File | Where it goes | Why |
|---|---|---|
| CH-2 OHRC `.zip` (791 MB) | Drive `raw_samples/` | Too big for git |
| The unzipped `.img` (1.1 GB) | **Your own PC only** | Far too big for anything |
| ISRO user guide PDFs | Drive `isro_user_guides/` | `*.pdf` is gitignored |
| LROC `.IMG` files | Drive `raw_samples/` | `*.IMG` is gitignored |
| Kaguya `.tif` files | Drive `raw_samples/` | `*.tif` is gitignored |
| **`DATASET_CARD.md`** | **git** (it's text) | This is your real deliverable |
| Screenshots / plots | Drive | Not git — see the warning below |

⚠️ **You already put 12 PNGs (3.9 MB) into `data/lroc_analysis/` in git.** Git history keeps them
forever now — deleting them doesn't shrink the repo. Not a disaster, but **put future plots in
Drive**, and link to them from your `.md`.

## A5. Keep downloads OUT of OneDrive

If your repo folder is inside OneDrive, **do not put big downloads there.** OneDrive doesn't read
`.gitignore`, so it will upload every gigabyte to the cloud and slow your machine to a crawl.

Make a plain folder instead, e.g. `C:\lunar_data\`, and keep the big files there.

---

# PART B — Chandrayaan-2 OHRC (1 hr) ← **your most overdue task**

This was Day 1 and it still isn't done. **CH-2 is the actual subject of our problem statement.**
Without it we have no cross-sensor pair and Gate 2 fails.

## B1. Why the page looked empty

The archive.org page shows a **book reader** instead of a file list, because the uploader tagged
the item as "texts". It's full of ZIPs, so the reader shows nothing. **The data is there — 5.39 GB.
I checked.**

## B2. Download (click these — don't retype them)

The folder name has spaces and brackets, so typing the URL by hand fails.

**The image ZIP (791 MB):**
```
https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/Optical%20High%20Resolution%20Camera%20%28OHRC%29/ch2_ohr_ncp_20200229T0739312111_d_img_d18.zip
```

**The OHRC user guide (1.8 MB) — Samartha is blocked on this:**
```
https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/OtherDownloads/OHRC/ch2_ohrc_data_products_user_guide.pdf
```

**The TMC-2 user guide (2.1 MB):**
```
https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/OtherDownloads/TMC-2/ch2_tmc2_data_products_user_guide.pdf
```

Full file list, if you want others: `https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/`

## B3. Before you unzip — check disk space

The ZIP is **791 MB** and unzips to **1.14 GB**. You need about **2 GB free**.

## B4. Unzip and check

Unzip into `C:\lunar_data\`. **Do not rename anything** — ISRO filenames carry the product ID and
renaming breaks the label link.

You'll get exactly this:

```
data/calibrated/20200229/..._d_img_d18.img     1124 MB   the image
data/calibrated/20200229/..._d_img_d18.xml        8 KB   the label
browse/calibrated/20200229/..._b_brw_d18.png     10 MB   preview picture
geometry/calibrated/20200229/..._g_grd_d18.csv    4 MB   lat/lon grid
```

**Open the browse PNG and look at it.** It should show craters. (I checked this one — it does.)

## B5. Upload to Drive

- The **791 MB ZIP** → Drive `raw_samples/`
- The **2 PDFs** → Drive `isro_user_guides/`
- Post the Drive link in chat so Samartha can get the OHRC guide.

## B6. What I already confirmed about this product

You don't need to work these out — just record them:

| field | value |
|---|---|
| instrument | `orbiter high resolution camera` |
| image size | 12000 × 93693 pixels |
| **GSD** | **0.22977 m/px** (≈23 cm) |
| tier | **B** (CH-2 OHRC ↔ LROC NAC = cross-sensor) |
| licence | ISRO open data |
| MD5 | `8a566034bdc1cdd2e59bb2b33984c5e7` (matches — file is good) |

⚠️ **Our docs say OHRC is "~28 cm". This product is 23 cm.** GSD changes with orbit altitude.
**Always take it from the label, never quote a fixed number.**

⚠️ **This product has NO sun angle and NO incidence angle** — not in the label, and not in the
geometry CSV either (that file has only `Longitude, Lattitude, Pixel, Scan`). So don't go looking
for it. See Part C for where illumination angles actually come from.

---

# PART C — LROC Tier A pairs (1.5 hrs) ← **this replaces your SDRPHO plan**

## C1. Your dataset card has a mistake, and so did our docs

You wrote that Tier A will use **`SDRPHO`** products. I checked the archive:

- **`SDRPHO` does not exist.** The real code is **`SDPPHO`** (P, not R). Our
  `00_CANONICAL_FACTS.md` had the same typo — my fault, now fixed.
- **`SDPPHO` has no incidence angle** in the archive's search index anyway.

## C2. The good news — there's a much better route

**The LROC search service (ODE) stores the incidence angle for ordinary NAC EDR images.** So you
don't need special products at all. You search by location, it gives you back each image *with its
sun angle*, and you pick two with a big difference.

That is exactly Tier A: **same place, incidence differs by ≥15°.**

## C3. Two ready-made Tier A pairs — I already found these

**Apollo 15 area — incidence differs 54.1°** (you need ≥15°, so this is excellent)

| | incidence | position | download |
|---|---|---|---|
| Low sun | 25.2° | 26.685 N, 3.535 E | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0003/DATA/MAP/2010088/NAC/M124545845LE.IMG` |
| High sun | 79.3° | 26.010 N, 3.752 E | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0001/DATA/COM/2009194/NAC/M102128467RE.IMG` |

**Copernicus crater — incidence differs 55.8°**

| | incidence | position | download |
|---|---|---|---|
| Low sun | 22.2° | 8.855 N, 340.050 E | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0049A/DATA/ESM4/2021267/NAC/M1387148235LE.IMG` |
| High sun | 78.1° | 9.545 N, 340.185 E | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0001/DATA/COM/2009196/NAC/M102293451RE.IMG` |

Start with **Apollo 15**. Download both, put them in Drive `raw_samples/`.

## C4. Check each image is not empty — do this EVERY time

The LROC image you logged yesterday (`M108587604RE`) turned out to be **completely blank** — no
craters, nothing. We only found out because we finally looked at it. Don't let that happen again.

```
python -c "import sys;sys.path.insert(0,'.');from core.io_loader import load;a,m=load(r'C:\lunar_data\M124545845LE.IMG');print('std',round(float(a.std()),1))"
```

- **std above 10** → real terrain, good
- **std around 1** → blank image, throw it away and pick another

**Better still: look at the picture.** Every image that goes in your catalogue needs eyes on it once.

## C5. To find more pairs yourself

Paste this in your browser, changing the lat/lon numbers:

```
https://oderest.rsl.wustl.edu/live2/?target=moon&query=product&results=fmp&output=JSON&pt=EDRNAC4&iid=LROC&ihid=LRO&limit=60&minlat=25.9&maxlat=26.3&westlon=3.4&eastlon=3.8
```

For each result read `Incidence_angle`, and pick two at the same place with a big gap.

⚠️ **Only use incidence between 20° and 80°.** Above 90° means the night side — no sunlight, black
image. Some results are 139° or 164°; those are useless.

---

# PART D — Kaguya TC, the Tier B+ pair (45 min)

**You do NOT need the AWS CLI.** Your task sheet says `--no-sign-request`; ignore that. The archive
answers a normal browser link with no account.

## D1. Download (22.6 MB — I already tested this exact file)

```
https://astrogeo-ard.s3.us-west-2.amazonaws.com/moon/kaguya/terrain_camera/monoscopic/uncontrolled/TC1S2B0_01_03482S746E0433/TC1S2B0_01_03482S746E0433.tif
```

This scene sits right next to our CH-2 OHRC footprint, which is what makes it the cross-sensor pair.

Put it in Drive `raw_samples/`.

## D2. What it should read as

```
python -c "import sys;sys.path.insert(0,'.');from core.io_loader import load;i,m=load(r'C:\lunar_data\TC1S2B0_01_03482S746E0433.tif');print(i.shape,m['gsd_mpp'],m['crs'])"
```

Expected — if you get these, everything is right:

| field | value |
|---|---|
| shape | `(6220, 6222)` |
| GSD | `9.3698731836556` m/px |
| CRS | `Moon (2015) - Sphere / Ocentric / South Polar` |

## D3. 🔴 Two traps in this file

**1. Half the image is empty.** 51.8% of it is "NoData", filled with the number **`-32768`**.
If you measure anything without removing those, you get nonsense (`std` comes out ~16440 instead
of ~231). Always mask first:

```python
valid = img != -32768
```

**Record `nodata = -32768` in your dataset card.**

**2. It's a polar scene, so most of it is in shadow.** I searched it for you — use this window:

| window | how dark | verdict |
|---|---|---|
| **`x=5120, y=2240`** | 4% dark | ✅ **use this** — craters and ridges, clearly visible |
| `x=3840, y=2240` | 11% dark | ok |
| `x=3200, y=640` | ~90% dark | ❌ avoid — nearly all shadow |

## D4. The number that matters

OHRC is 0.22977 m/px, this Kaguya scene is 9.3699 m/px → **the scale ratio is 40.8×**.

⚠️ Our docs estimate "~36×". **The measured value is 40.8×. Use the measured one.** This is the
pair that proves our scale-invariance claim, so the number needs to be right.

---

# PART E — Update `DATASET_CARD.md` (30 min) ← your actual deliverable

This is the **only** file from today that goes in git. Add one row per file.

Fill in these columns: `file | tier | instrument | source URL | downloaded | licence | product ID |
gsd_mpp | nodata | notes`

You now have everything you need:

| file | tier | instrument | GSD | notes |
|---|---|---|---|---|
| `ch2_ohr_ncp_...d18.img` | **B** | orbiter high resolution camera | 0.22977 | ISRO open data. No sun angle in product. |
| `M124545845LE.IMG` | **A** | LROC NAC | ~0.5 | **incidence 25.2°** |
| `M102128467RE.IMG` | **A** | LROC NAC | ~0.5 | **incidence 79.3°** — differs 54.1° from above |
| `TC1S2B0_01_03482S746E0433.tif` | **B+** | Kaguya TC | 9.3699 | **CC0 1.0**. nodata −32768. Ratio to OHRC 40.8× |

Also fix in your card:
- **`SDRPHO` → `SDPPHO`**, and note we're using ODE incidence metadata on NAC EDRs instead.
- Add the note that CH-2 OHRC carries no illumination geometry at all.

Then:
```
git add data/DATASET_CARD.md
git commit -m "Add CH-2 OHRC, Tier A LROC pair, and Kaguya TC to the dataset card"
git push
```

---

# Checklist — tick these off

- [ ] Drive folders made, "available offline" ticked
- [ ] CH-2 OHRC ZIP downloaded, browse PNG looked at, uploaded to Drive
- [ ] Both ISRO user guide PDFs in Drive `isro_user_guides/` + link posted in chat
- [ ] Apollo 15 Tier A pair downloaded (both images), **each one checked with `std`**
- [ ] Kaguya `.tif` downloaded and reads with the expected GSD
- [ ] `DATASET_CARD.md` updated and **pushed**
- [ ] Posted in chat: "CH-2 + Tier A + Kaguya all in Drive, card pushed"

## Never do these

- ❌ `git add -f` on any image, PDF or ZIP
- ❌ Put big downloads inside a OneDrive folder
- ❌ Rename an ISRO or LROC file
- ❌ Log an image in the card without looking at it first
- ❌ Use incidence angles above 90° (that's the night side)
- ❌ Quote "36×" for OHRC↔Kaguya — it's **40.8×**
- ❌ Quote "28 cm" for OHRC — this product is **23 cm**
