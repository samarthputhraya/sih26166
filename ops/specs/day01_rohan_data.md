# [Day 1] Rohan — data acquisition + provenance

**Time: 2 hrs.** Read `day01_00_SHARED_SETUP.md` first.

## Goal, in one sentence
One real Chandrayaan-2 OHRC product is unzipped on your PC with its original filename, and
`data/DATASET_CARD.md` exists in the repo with its provenance row filled in.

## Install
```bash
pip install pds4_tools==1.4 pvl==1.3.2 requests
```
No `rasterio` today — it is broken on the demo machine (see shared setup).

## Acceptance criteria
1. **Input:** `https://archive.org/details/chandrayaan-2-high-resolution-images-of-the-moon`
   — no account needed.
2. **Output A:** one OHRC ZIP unzipped on *your own disk* (not the repo), containing at least one
   `.img` and its matching `.xml` PDS4 label, **filenames byte-identical to the download**.
3. **Output B:** `data/DATASET_CARD.md` committed and pushed, with this exact header and ≥1 fully
   populated row. Any value you do not know is left **blank**, never guessed.
   ```
   | file | tier | instrument | source URL | downloaded | licence | product ID |
   ```
4. **Output C:** one chat message with the chmapbrowse registration outcome, quoting the **exact**
   error text if it refused.
5. Passes: `python -c "import pds4_tools; d=pds4_tools.read(r'<path>\<label>.xml'); print(d)"`
   prints structure without raising.

## Test cases
1. `filenames_preserved` — every name still matches `ch2_ohr_*`, with no `(1)` and no `_copy`.
2. `label_pairs` — count of `.img` == count of `.xml`, each pair sharing a stem.
3. `card_has_no_invented_cells` — every non-blank cell is copy-pasted from the archive page or the
   PDS label, never typed from memory.

## Starter
```markdown
<!-- data/DATASET_CARD.md -->
# SIH26166 — Dataset Card

Provenance for every file we use. One row per file, filled at download time.
Blank means "not known". Never guess — a wrong GSD or sun angle silently
corrupts Samrudh's analysis and cannot be caught downstream.

| file | tier | instrument | source URL | downloaded | licence | product ID |
|------|------|-----------|-----------|------------|---------|-----------|
|      |      |           |           |            |         |           |
```

## Dependencies
- Needs **nothing from any teammate**. `data/raw/` and `data/pairs/` exist in commit `7644b4c`.
- Delivers to: Samartha (Day 2, needs a real `.img`+`.xml` to write `io_loader.py`);
  Rishabh (will ask you today for the CH-3 landing-site pair, needs it ~Day 6).

## Do not
- **Do not `git add -f` any `.img`, `.zip` or `.xml` data file.** `.gitignore` covers them; forcing
  past it puts a large blob in history permanently and breaks every teammate's clone.
- **Do not commit the ISRO user-guide PDFs.** `.gitignore` has no `*.pdf` rule yet and they are tens
  of MB. Record the URL in the card; the files move to Drive once it exists.
- **Do not rename a single downloaded file.** A rename breaks PDS label association.
- **Do not `import rasterio`** — blocked by Application Control on the demo machine.
- **Do not watch the download.** Start it in minute one, then do the card and the registration test
  while it runs.

## You are BLOCKED if
The archive.org item is missing or the ZIP will not unzip → **ping Samartha within 30 minutes.**
Fallback needing no login: pull one LROC NAC EDR from
`https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/` and card that instead. Do not spend the
session fighting one download.

## The ONE thing most likely to make your Day 1 fail
**You watch the progress bar and produce nothing else.** The download is the only part that cannot
be rushed and the only part needing none of your attention. The card and the registration test are
the actual deliverables.
