# Rohan — Data Lead Guide

**Role:** Build the validation ladder — real lunar image pairs across four missions, fully documented
**Time:** ~2 hrs/day
**Renamed** from `ROHAN_PRADAN_REGISTRATION_GUIDE.md` — PRADAN is no longer the plan, see below.

> Read `00_CANONICAL_FACTS.md` §2 (the ladder) and §3 (data sources) before starting.

---

## 🔴 READ THIS FIRST — THE OLD GUIDE WAS WRONG

The previous version of this guide told you to spend Day 1 registering on PRADAN with a college
email, upload an ID card and a bonafide certificate, and wait 2–5 days for approval. **Almost all
of that was unverified, and the parts that were checkable turned out to be wrong.**

| Old claim | Reality |
|---|---|
| *"College email ID — **mandatory**, personal Gmail often rejected"* | **No email-domain requirement is stated anywhere** on the PRADAN login page, the FAQ, or chmapbrowse. This was invented. |
| *"2–5 days for approval"* | **No stated approval delay found.** Also invented. |
| *"Bonafide certificate", "College ID card", "Faculty consent email"* | **No evidence any of these are required.** Do not chase them on Day 1. |
| A registration form table with 15 exact field names | **The real form was never seen.** Those field names are guesses. |
| `pradan@issdc.gov.in`, `helpdesk.issdc@isro.gov.in`, `issdc-support@isro.gov.in`, `ch2-ohrc@issdc.gov.in` | **None of these were verified. Treat them as non-existent.** The one contact actually published by ISSDC is **`issdc[at]istrac.gov.in`**. Emailing invented addresses loses days to silence. |
| *"LROC-LROC cross-orbit... this IS valid cross-sensor"* | **Factually false.** Two LROC images are the same sensor. See §2 below. |

**The real situation is much better than the old guide assumed:**
**Actual Chandrayaan-2 OHRC imagery is publicly mirrored with no account at all.** You can have
real CH-2 data on disk in the first hour.

---

## 🎯 YOUR MISSION

Build a **validation ladder** — not "10 pairs", but pairs that each prove a specific thing the
problem statement demands — plus a provenance document that survives an ISRO judge asking
"where exactly did this come from?"

| Tier | Pair | Proves | Target count |
|---|---|---|---|
| **A** | LROC NAC ↔ LROC NAC, same site, incidence differs ≥15° | **Sun-angle invariance** (same sensor) | 6 pairs |
| **B** | CH-2 OHRC ↔ LROC NAC | **Cross-sensor, cross-mission** | 2 pairs |
| **B+** | CH-2 OHRC ↔ Kaguya TC | **Cross-sensor at ~20× scale** | 1 pair |
| **C** | Optical ↔ M3 infrared band | **MULTI-MODAL** — the PS title | 1 pair |
| **D** | Optical ↔ SLDEM shaded relief | Ground truth at any sun angle | 1 site (Samrudh uses this) |

**Words you must never use for Tier A: "cross-sensor", "multi-modal".** Two LROC NAC images are
the same instrument. Different orbit changes viewpoint and lighting, not modality. Tier A is a
**sun-angle** experiment — a good one. Call it what it is.

---

## 📅 YOUR 12-DAY PLAN

### DAY 1 — Get real Chandrayaan-2 data (no account needed)

**Task 1 (45 min) — Download CH-2 OHRC. This is the one that matters.**

Open `https://archive.org/details/chandrayaan-2-high-resolution-images-of-the-moon`

> 🔴 **THE PAGE WILL LOOK EMPTY. THE DATA IS THERE — 5.39 GB OF IT.**
> The uploader tagged this item `mediatype = texts`, so archive.org renders it with the **book
> reader** instead of a file list. The item actually contains ZIPs, so the reader displays nothing
> and the page appears blank. This is a display quirk, not a missing item — verified 31 Aug 2026:
> the item is live, has 125 files, and a direct byte-range request returns `PK\x03\x04` (a valid
> ZIP).
>
> **Two ways through it:**
> 1. In the right-hand sidebar click **DOWNLOAD OPTIONS → SHOW ALL**, or
> 2. go straight to the file list:
>    `https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/`
>
> The OHRC files sit in a folder whose name contains **spaces and brackets** —
> `Optical High Resolution Camera (OHRC)/` — so a hand-typed URL fails unless they are
> percent-encoded (`%20` and `%28` `%29`). Use the links below rather than typing them.

**The six OHRC image ZIPs, verified present with these exact sizes:**

| size | file |
|---|---|
| 791.0 MB | `ch2_ohr_ncp_20200229T0739312111_d_img_d18.zip` |
| 844.7 MB | `ch2_ohr_ncp_20200229T0938004033_d_img_d32.zip` |
| 854.5 MB | `ch2_ohr_ncp_20200824T1003365280_d_img_d18.zip` |
| 775.7 MB | `ch2_ohr_nrp_20200229T0739312111_d_img_d18.zip` |
| 828.8 MB | `ch2_ohr_nrp_20200229T0938004033_d_img_d32.zip` |
| 840.7 MB | `ch2_ohr_nrp_20200824T1003365280_d_img_d18.zip` |

Working direct link (this exact URL was tested and returns HTTP 206):

```
https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/Optical%20High%20Resolution%20Camera%20%28OHRC%29/ch2_ohr_ncp_20200229T0739312111_d_img_d18.zip
```

The **OHRC user guide** — the format spec Samartha needs — is at:

```
https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/OtherDownloads/OHRC/ch2_ohrc_data_products_user_guide.pdf
```

(1.8 MB. TMC-2's guide is beside it at `OtherDownloads/TMC-2/`, 2.1 MB.)

Note there are two variants of each acquisition, `ncp` and `nrp`. Check the user guide for which
processing level each is before choosing — do not guess, and record the answer in `DATASET_CARD.md`.

1. Download **one** OHRC ZIP (start it, do other work while it runs).
2. Download the **OHRC and TMC-2 Data Products User Guides** — these are the format specification
   Samartha needs to finish the PDS4 branch of the loader, and he is blocked on them.
   **Put them in Drive, `SIH26166_DATA/isro_user_guides/` — not in the repo.** They are PDFs of tens
   of MB and `.gitignore` blocks `*.pdf`, so dropping them in `data/docs/` means git silently ignores
   them, nobody else ever sees them, and Samartha is still blocked. Post the Drive link in chat.
3. Unzip. You should see `.img` files paired with `.xml` PDS4 labels.
4. **Do not rename anything.** Ames Stereo Pipeline's CH-2 tutorial warns:
   *"Keep the original ISRO filenames; a rename can break isisimport."* Same applies to us.
5. Post in chat: "CH-2 OHRC downloaded, N files, original filenames preserved."

**Task 2 (20 min) — Test the PRADAN premise, don't assume it.**

Go to `https://chmapbrowse.issdc.gov.in/` and `https://pradan.issdc.gov.in/ch2/`. Both have a
**"New user? Register"** link (authentication is a Keycloak SSO at `idp.issdc.gov.in`).

**Register with your personal Gmail.** That is the whole test. It takes ten minutes.
- If it works → excellent, we get the full CH-2 archive including IIRS.
- If it explicitly demands an institutional domain → post the exact error text in chat, then ask
  the college for an ID. Not before.
- Only escalation contact that is verified: **`issdc[at]istrac.gov.in`**.

Post the result either way. This one line unblocks or closes a question the whole team has.

**Task 3 (30 min) — Start `data/DATASET_CARD.md`.**

One row per file, from the very first download. Retrofitting provenance on Day 8 is miserable.

```markdown
| file | tier | instrument | source URL | downloaded | licence | product ID |
|------|------|-----------|-----------|------------|---------|-----------|
| ch2_ohr_ncp_20200229T0739312111_d_img_d18.img | B | CH-2 OHRC | archive.org/details/chandrayaan-2-... | 2026-08-30 | ISRO open data | ch2_ohr_ncp_20200229T0739312111_d_img_d18 |
```

**Day 1 deliverable:** CH-2 OHRC on disk + user guides in Drive `isro_user_guides/` + registration result posted
+ `DATASET_CARD.md` started.

---

### DAY 2 — Tier A: LROC NAC sun-angle pairs

**Browse:** `https://quickmap.lroc.im-ldi.com/` — public, no login.
(The old `quickmap.lroc.asu.edu` is the legacy host being retired. Use `im-ldi.com`.)

**Bulk archive:** `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/` — a plain open HTTP
directory. No login, no cart.

**Search front-end:** `https://ode.rsl.wustl.edu/moon/indexproductsearch.aspx` — shows
"You are an anonymous user"; sign-in is optional.

**What you want:** the **same lunar site** imaged at **different incidence angles**.

1. In QuickMap, pick a site with heavy repeat coverage — Apollo 11, Mare Tranquillitatis, or a
   crater with a clear rim.
2. Turn on the NAC footprint layer. Zoom until individual footprints (long thin strips) show.
3. Click footprints. Each popup gives **incidence angle** — that is your sun-angle proxy.
4. Collect **6 pairs** where incidence differs by **≥15°**. Bigger is better; try to get one pair
   above 40° difference for the "hard case."
5. Record product IDs (like `M123456789LE`) in the dataset card as you go.

> 💡 **Prefer map-projected products where you can get them** — ODE dataset
> `LRO-L-LROC-5-RDR-V1.0`, product type **`SDPPHO`** (P, not R — `SDRPHO` does not exist; this
> guide and Canonical Facts both had the typo). Georeferenced means the map coordinates give
> Samrudh approximate ground truth for free. Raw EDRs need much more work.
>
> 🔴 **But for TIER A specifically, use ordinary NAC EDRs and the ODE REST API instead.** ODE
> reports no incidence angles for `SDPPHO`, but it *does* carry them for **`EDRNAC4`**. A NAC EDR
> label contains no illumination geometry at all (verified on a real product), so the sun angle has
> to come from ODE's metadata. That query returns each image *with its `Incidence_angle`*, which is
> precisely how you select "same site, incidence differs ≥15°". Full worked steps, with two
> ready-made pairs, are in `ops/specs/ROHAN_DO_THIS_NOW.md`.

**Day 2 deliverable:** 6 Tier A candidate pairs identified and downloading, dataset card updated.

---

### DAY 3 — Tier B+: Kaguya TC (the easiest win in the project)

CC0 licence, Cloud-Optimized GeoTIFF, no AWS account:

```bash
aws s3 ls --no-sign-request s3://astrogeo-ard/moon/kaguya/terrain_camera/monoscopic/uncontrolled/
```

If the AWS CLI isn't installed: `pip install awscli`.

COG means `rasterio.open()` reads these **directly over HTTP without downloading**. And CC0 means
zero licence risk — worth saying out loud in the deck.

Find a scene overlapping one of your Tier A / OHRC sites. Kaguya TC is ~10 m/px against OHRC's
~28 cm — that is a **~36× scale ratio**, which is exactly the scale-invariance case the PS demands.

**Day 3 deliverable:** 1 Kaguya TC scene overlapping an OHRC footprint, in the catalogue.

---

### DAY 4 — Tier D: SLDEM for ground truth

Samrudh needs this to generate ground truth at arbitrary sun angles.

`https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/sldem2015/`
(browse tiles at `https://imbrium.mit.edu/BROWSE/SLDEM2015/`)

SLDEM2015: LOLA + Kaguya TC merged DEM, ±60° latitude, 512 pixels/degree ≈ **59 m/px**, vertical
accuracy ~3–4 m, in PDS IMG and JPEG-2000.

Download the tile covering your primary demo site. Hand it to Samrudh with the lat/lon bounds.

> There is also a **pre-rendered** shaded relief on USGS Astropedia
> ("LOLA–Kaguya TC Shaded Relief Merge 60N60S 59m") if the DEM rendering proves fiddly. Grab it
> as a backup.

**Day 4 deliverable:** SLDEM tile delivered to Samrudh + `DATASET_CARD.md` current.

---

### DAY 5 — Deliver catalogue v1

Create `data/pairs_catalogue.csv`. **The `tier` column is mandatory** — it is how the whole team
stays honest about what each result proves.

```csv
pair_id,tier,source_instrument,source_file,source_gsd_mpp,source_sun_az,source_sun_el,source_incidence,ref_instrument,ref_file,ref_gsd_mpp,ref_sun_az,ref_sun_el,ref_incidence,scale_ratio,overlap_lat,overlap_lon,notes
pair_01,same-frame offset crop,CH2_OHRC,pair_01_source.tif,0.22977,,,,CH2_OHRC,pair_01_ref.tif,0.22977,,,,1.0,,,"same-frame wiring fixture; known 40x25 px offset; NOT a validation tier"
pair_07,B,CH2_OHRC,pair_07_source.tif,0.28,,,,LROC_NAC,pair_07_ref.tif,0.5,,,,1.8,,,"cross-sensor cross-mission"
```

> ⚠️ **The `pair_01` row above is the real one, and it is deliberately unglamorous.** Until Day 5
> 2026 this example read `pair_01,A,LROC_NAC,...,32,...,58` — claiming Tier A, the wrong
> instrument, and a sun-angle difference that does not exist. `pair_01` is two crops of ONE
> Chandrayaan-2 OHRC frame: same sensor, same instant, zero sun difference.
>
> The lesson the row is here to teach: **the `tier` string is a claim about what a result proves,
> so it has to survive a judge asking "which two sensors?"** `same-frame offset crop` is an
> honest answer. `A` was not.

Leave a field blank if you genuinely don't have it. **Never guess a number to fill a cell** — a
wrong sun angle silently corrupts Samrudh's entire illumination analysis.

**Cropping to the overlap region:** this needs map projection and coordinate transforms, which
nobody on this team has done before. **Do not attempt it alone.** Samartha writes
`core/io_loader.py` with a crop/reproject helper on Days 2–4; you call it:

```python
from core.io_loader import crop_to_overlap
crop_to_overlap("raw/M123456789LE.IMG", "raw/M987654321RE.IMG", out_prefix="data/pairs/pair_01")
```

If that helper isn't ready when you need it, **say so in chat immediately** — that is a bad spec,
which is Samartha's problem to fix, not yours to work around.

**Day 5 deliverable:** `data/pairs/` with Tier A + Tier B pairs, `pairs_catalogue.csv` with tiers.

---

### DAY 6 — Tier C: the multi-modal leg

**This is the single most important download in the project.** "Multi-modal" is the first word of
the problem statement title, and this is the only tier that proves it.

**Chandrayaan-1 M3** — a hyperspectral imaging spectrometer (0.43–3.0 µm), same modality class as
CH-2 IIRS, flown on an **Indian** mission, distributed publicly by NASA PDS with no login.

`https://pds-imaging.jpl.nasa.gov/schedules/m3_release.html`
Format doc: `https://pds-imaging.jpl.nasa.gov/documentation/M3_DPSIS.PDF`

An M3 **L1B** product is four files:
- detached PDS label
- multi-band calibrated radiance image
- **3-band LOC file** — per-pixel latitude / longitude / elevation
- **10-band OBS file** — per-pixel **observation geometry, including illumination angles**

> That OBS file is real measured sun geometry, not simulated. Tell Samrudh it exists — it makes
> the illumination analysis genuine rather than synthetic.

Pick one M3 scene overlapping a site you already have optical coverage for. Extract a single
infrared band as the Tier C reference.

*If your chmapbrowse registration succeeded on Day 1, use **CH-2 IIRS** instead — it is strictly
better because it is the instrument the PS actually names. M3 is the no-login fallback.*

**Day 6 deliverable:** 1 Tier C pair. Post in chat: "Multi-modal leg secured."

---

### DAY 7 — Hard cases

- Incidence angle **>70°** (long shadows — where classical methods die)
- A polar site if you can find overlap (CH-2 tasking shifted polar in 2024 for LUPEX)
- One pair you expect to **fail**. An honest failure case is worth more in Q&A than ten successes.

**Day 7 deliverable:** 3 hard pairs added, flagged `hard=yes` in the catalogue.

---

### DAY 8 — Provenance complete

Finish `data/DATASET_CARD.md`. Every single file: source URL, download date, licence, product ID,
instrument, GSD.

Then write one paragraph at the top titled **"How to reproduce this dataset"** — someone should be
able to rebuild it from your document alone. That paragraph is your answer when a judge asks about
data provenance, and it is a genuine credibility marker.

**Day 8 deliverable:** `DATASET_CARD.md` complete and committed.

---

### DAY 9 — Offline verification (this protects Gate 4)

Every file in `demo_cache/` must open **with wifi off**.

1. Turn wifi off.
2. Load each demo pair with `core.io_loader`.
3. Anything that fails → fix now, not on Day 11.
4. Record checksums so nobody silently swaps a file.

**Day 9 deliverable:** "All demo_cache files verified offline" posted in chat.

---

### DAY 10 — Your 60 seconds, and the stranger

**Write and rehearse your data-provenance answer.** Draft:

> "We use four missions. Chandrayaan-2 OHRC at 28 centimetres is our source — that's ISRO's own
> camera and the sharpest operational one at the Moon. LROC NAC at half a metre is our primary
> reference. Kaguya Terrain Camera gives us a 36× scale ratio to test scale invariance. And
> Chandrayaan-1's M3 spectrometer gives us the infrared leg for the multi-modal case. Everything
> is public and every file's provenance is documented — source, date, licence, product ID."

**Also: recruit the Gate 3 stranger.** Someone who is not on the team and has not heard us talk
about the project. A hostel-mate. They sit down at the UI on Day 10 and must operate it and
explain the output with nobody speaking.

---

### DAYS 11–12 — Rehearsals and Gate 5

Rehearsals 1, 2, 3. Gate 5: answer cold.

**Expect these questions:**
- "Where did the Chandrayaan-2 data come from?" → archive.org public mirror + ISRO's own portal
- "Is LROC-to-LROC really cross-sensor?" → **"No. Same sensor. That's our sun-angle test. Our
  cross-sensor work is Chandrayaan-2 against LROC and Kaguya."** ← the most likely trap question
- "What licence is the Kaguya data?" → CC0, public domain
- "How big is the dataset?" → know the number
- "Could you rebuild this?" → "Yes, the dataset card documents every file."

---

## 🛠️ TOOLS

```bash
pip install pds4_tools pvl rasterio awscli requests
```

- **`pds4_tools`** — reads CH-2 PDS4. **This is the library ISRO itself names** in its own
  instructions to SIH students. Use it, not GDAL, for CH-2.
- **`pvl` + `rasterio`** — PDS3 (LROC, M3, Kaguya).
- **`awscli`** — Kaguya over `--no-sign-request`.

⚠️ On Windows use `python`, not `python3` — `python3` opens the Microsoft Store and fails.

⚠️ The old guide said *"use `gdal_translate` or rasterio to convert PDS4 → TIFF."* GDAL's PDS4
driver may not handle ISRO's local data dictionary. **`pds4_tools` is the safe path for CH-2.**

⚠️ `https://lroc.sese.asu.edu/data/` appeared in the old guide as a bulk search endpoint —
**unverified, may not exist.** Use `pds.lroc.im-ldi.com` (verified open directory) or ODE.

---

## 💡 TIPS

| Situation | What to do |
|---|---|
| A download is 750 MB and slow | Start it, then do another task. Never sit and watch it. |
| "Is this pair cross-sensor?" | Different **instrument**? Then yes. Same instrument, different orbit? **No — that's Tier A.** |
| PDS4 file won't open | `pds4_tools.read(label_path)`. If it still fails, post in chat — Samartha owns format issues. |
| Don't know the sun angle | Leave the CSV cell **blank**. Never guess. A wrong angle corrupts the analysis silently. |
| Two images don't actually overlap | Check in QuickMap before downloading. Cheaper than discovering it after 750 MB. |
| Tempted to rename a file | **Don't.** It breaks the PDS label association. |
| Blocked > 30 min | Post in chat. Thirty minutes, not two hours. |

---

## ✅ DELIVERABLES CHECKLIST

- [ ] `data/raw/` — original downloads, original filenames, never renamed
- [ ] `data/pairs/` — cropped pairs, `pair_NN_source.tif` / `pair_NN_ref.tif`
- [ ] `data/pairs_catalogue.csv` — **with the `tier` column populated**
- [ ] `data/DATASET_CARD.md` — every file: URL, date, licence, product ID + reproduction paragraph
- [ ] Drive `isro_user_guides/` — ISRO OHRC and TMC-2 user guides (**not** the repo; `*.pdf` is gitignored)
- [ ] ≥6 Tier A · ≥2 Tier B · ≥1 Tier B+ · **≥1 Tier C** · 1 Tier D site
- [ ] chmapbrowse/PRADAN registration attempted, result posted
- [ ] All `demo_cache/` files verified to open offline
- [ ] Gate 3 stranger recruited
- [ ] 60-second provenance answer rehearsed

---

## 🗣️ WHAT TO SAY IN THE DEMO (30 seconds)

> "Our data spans four missions, all public. Chandrayaan-2 OHRC at 28 centimetres is the source —
> ISRO's own camera, the sharpest operating at the Moon. We register it against LROC NAC at half a
> metre, and against Kaguya Terrain Camera at ten metres, which gives us a 36× scale ratio to test
> scale invariance directly. For the multi-modal case we go optical against infrared using
> Chandrayaan-1's M3 spectrometer. Every file's source, date and licence is documented — this
> dataset is reproducible from our documentation alone."

**Do not say a number you have not checked.** If you don't know the file count, say
"about a dozen pairs" — vagueness is survivable, a wrong specific is not.

---

## 📞 ESCALATION

| Problem | Ask |
|---|---|
| PDS4 / PDS3 won't parse | Samartha (he owns format issues) |
| Crop / reproject helper missing or broken | Samartha — **and say it's blocking you** |
| What metadata does the catalogue need | Samrudh |
| Which pairs to feature in the demo | Saniya + Samartha |
| ISSDC registration genuinely refuses | `issdc[at]istrac.gov.in` — **the only verified contact** |

---

**Bottom line:** you are not waiting on anyone, and you never were. Real Chandrayaan-2 data is one
download away. Your job is the ladder and the provenance — and the provenance is what makes every
other person's numbers believable.
