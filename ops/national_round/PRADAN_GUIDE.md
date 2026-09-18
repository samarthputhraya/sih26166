# PRADAN guide — getting TMC-2, IIRS and SAC's own OHRC products

Checked against the live site on 18 Sep 2026: the registration form, the FAQ, the contacts page,
and the TMC-2 and OHRC data-product user guides. **Deadline: if the data is not on disk by
Tue 22 Sep evening, drop this. Nothing else depends on it.**

## 1. Register (about 10 minutes)

1. Open **https://pradan.issdc.gov.in/ch2/** and click **Login/Signup**.
2. It sends you to the ISSDC sign-in page (`idp.issdc.gov.in`). Click **New user? Register**.
3. The form asks for the following (fields with * are required):

   | Field | What to enter |
   |---|---|
   | Username *, Password *, Confirm password * | your choice |
   | Email * | an address you check now; personal Gmail is fine, nothing asks for a college domain |
   | First name *, Last name * | as on your college ID |
   | Affiliation Category * | **Student** |
   | Designation * | e.g. "B.E. student" |
   | Organization / Institution * | your college's full name |
   | Area of Expertise | "Planetary image processing / image registration" |
   | Area, Pin / Zip, City / Town *, State / Province *, Country * | your address; Country **India** |
   | Phone, Alternate Email | optional |
   | Broadcast Emails Subscription | your choice |

   The form does not ask for an ID card or a bonafide certificate.
4. Submit, then open the verification email and click the link. If the download pages still say
   you have no access after logging in, write to the site administrator: **issdc[at]istrac.gov.in**.
   Use only that address; don't email the payload scientists about the hackathon.

## 2. Finding data (two ways in)

- **Map View (easiest for our site).** On the PRADAN page, click **Map View (Payloads: OHRC, TMC-2,
  IIRS, SAR)**. It opens **chmapbrowse.issdc.gov.in**. ISRO's own instructions to SIH teams:
  *"Change Projection into South Pole. Under Instrument footprint, select footprints will be
  displayed over the pole mosaic image. User can click on any of the footprint in the map view,
  details will be displayed in the left panel. User can select desirable PDS product, which can be
  downloaded."*
- **Table View.** **Browse and Download**, then pick the payload, the processing level and the dates.
  Good when you know the product name or the date.

Download tips from the FAQ:
- The site logs you out after **30 minutes** idle; log in again and resume.
- Use Chrome or a download manager.
- For big files use **Download in Bulk**, not ZIP: ZIP downloads have a size limit and silently
  drop files past it.

## 3. What to download, in priority order

**Our site** is the OHRC frame we already have: latitude **−74.37 to −73.52**, longitude
**43.36 to 43.96** (centre −73.94°, 43.66°E). It was taken **2020-02-29, 07:39 UTC**.

### P1 — TMC-2 over our site (the instrument named in the PS title)

- **First, look for a TMC-2 strip taken on 2020-02-29 around 07:3x UTC.** TMC-2 flies on the same
  spacecraft as the OHRC, so a strip from the same pass has the same sun. That is the cleanest
  possible OHRC↔TMC-2 pair.
- If none crosses the site that day, take the strip that covers the site with the most sunlit
  ground, from any date.
- Files for that strip (the same time stamp in every name):

  | File | What it is | Why we want it |
  |---|---|---|
  | `ch2_tmc_ndn_<time>_d_oth_<stn>.zip` | derived **ortho** image, GeoTIFF (~5 m) | map-projected; easiest to pair |
  | `ch2_tmc_ndn_<time>_d_dtm_<stn>.zip` | derived **DTM**, GeoTIFF | terrain; relief correction |
  | `ch2_tmc_ncn_<time>_d_img_<stn>.zip` | calibrated **nadir** camera | the raw-geometry pair |
  | `ch2_tmc_ncf_…zip` and `ch2_tmc_nca_…zip` | calibrated **fore** and **aft** cameras (±25° off nadir) | **our only real viewpoint test** |

  Name pattern: `n` = normal phase, `c`/`d` = calibrated/derived, then `n`/`f`/`a` = nadir/fore/aft.
  `<stn>` is the ground station (`d18`, `d32`, `blr`, …). Calibrated zips include the geometry
  CSV (the lat/lon grid) that our code reads.

### P2 — SAC's own benchmark OHRC (equatorial)

- **`ch2_ohr_ncp_20210401T2357376656_d_img_d18`**, 2021-04-01, ~23:57 UTC, near 14.4°S 25.2°E.
- It is the OHRC half of the pair in the PS setters' paper (arXiv:2509.04775, Table 1). The other
  half, LRO NAC `M1350459544RE`, is open and I can fetch it.
- The ID is rebuilt from a table that wraps across lines in the PDF. **Confirm it by date and time**
  in the search; it should be the only OHRC product at that time.
- Size is about 0.8 GB (OHRC calibrated zips are 775–855 MB).

### P3 — IIRS over our site (infrared: the multi-modal leg the PS names)

- A calibrated IIRS product (`ch2_iir_nci_<time>_d_img_<stn>.zip`) whose footprint crosses our site.
- These are spectral cubes and can be large. **Check the size column before downloading.**

### P4 — SAC's polar benchmark OHRC (only if P1–P3 are done)

- **`ch2_ohr_ncp_20200824T0806596861_d_img_d18`**, 2020-08-24, ~08:06 UTC. It pairs with NAC
  `M165491149RE`. Same caveat: confirm by date and time.

## 3a. What happened on 18 Sep (registered; downloads done by Claude in the logged-in browser)

- **No TMC-2 strip covers our 74°S site.** Checked three ways: PRADAN's own footprint shapefiles
  (`<data>/pradan/shapefiles/`, self-checked: exactly one OHRC footprint contains the site and it is
  our frame), then the calibrated lat/lon grid of the nearest strips. The nearest nadir swath
  (`ch2_tmc_ncn_20241115T2122241048`) spans lon 45.73-47.87° at the site's latitude; our OHRC frame
  is at 43.36-43.96° (~17 km short). The table's "CorrectedCoordinates" filter matches the ortho
  products' bounding boxes, which near the pole are huge - do not trust it for coverage.
- **P1 moved to SAC's benchmark site** (P2's OHRC frame, 13.1-13.9°S 25.1-25.2°E): TMC-2 pass
  `20250707T1853` covers it fully (grid columns 1100-1700 of 4000). Downloaded nadir/fore/aft
  calibrated (`ncn`, `ncf`, `nca`) plus the derived ortho and DTM. Sun differs a lot: OHRC label
  az 270.9° / elev 9.9°, TMC-2 label az 31.1° / elev 69.4° - a hard pair, and an honest one.
- **P2** `ch2_ohr_ncp_20210401T2357376656_d_img_d18` and **P4**
  `ch2_ohr_ncp_20200824T0806596861_d_img_d18` confirmed by time (the only OHRC products then) and
  downloaded. P4 is at 61.5-62.4°S 56.5-56.9°E (label sun az 58.3° / elev 13.6°).
- **P3 IIRS**: three calibrated cubes cover our site (grid-checked): `20201128T1108` (5.45 GB zip),
  `20210621T1517` and `20210621T1715` (3.36 / 3.34 GB). Downloading `20210621T1517` (label sun elev
  24.3°); IIRS served at ~0.55 MB/s vs ~8 MB/s for TMC-2, and the first attempt died part-way.
- Sizes: the table's ProductSizeInBytes is the UNCOMPRESSED size (the 27 GB "ortho" zips are
  0.6-0.9 GB). The server honours HTTP Range, so one member (e.g. the geometry CSV) can be read out
  of a zip without downloading it. Every file's sha256 is in `<data>/download_manifest_done.csv`
  (groups `pradan_ohrc`, `pradan_tmc2`, `pradan_iirs`).

## 4. Where to put the files

```
C:\Users\samar\sih26166_data\pradan\tmc2\
C:\Users\samar\sih26166_data\pradan\ohrc\
C:\Users\samar\sih26166_data\pradan\iirs\
```

- Unzip in place and keep the zip.
- **Never rename a file.** The labels reference the original names.
- Then tell Claude "PRADAN files are in place". It records the checksums, reads each product's
  geometry grid, and cuts the pairs: OHRC↔TMC-2, TMC-2 fore↔aft, OHRC↔IIRS, and SAC's pair.
