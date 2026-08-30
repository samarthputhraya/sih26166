# SIH26166 — Dataset Card

Provenance for every file we use. One row per file, filled at download time.

Blank means "not known". Never guess — a wrong GSD or sun angle silently
corrupts Samrudh's analysis and cannot be caught downstream.

## Dataset policy

LROC EDR products are retained as source/reference data only. They are not
used to establish Tier A illumination differences because the downloaded
EDR label does not provide the required illumination geometry.

Tier A analysis will use LROC SDRPHO products from:

LRO-L-LROC-5-RDR-V1.0

SDRPHO provides:
- Band 1: calibrated, map-projected NAC image
- Band 2: incidence angle
- Band 3: emission angle
- Band 4: phase angle

Therefore illumination geometry is measured from the analysis product rather
than inferred from the EDR.

Kaguya comparison data will also be downloaded locally rather than accessed
over HTTP/GDAL on the demo laptop.

| file | tier | instrument | source URL | downloaded | licence | product ID |
|------|------|-----------|------------|------------|---------|-----------|
| M108587604RE.IMG | reference | LUNAR RECONNAISSANCE ORBITER CAMERA NAC | https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_0001/DATA/MAP/2009269/NAC/M108587604RE.IMG | 2026-08-30 |  | nacr0000bc48 |
