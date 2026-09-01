# Rohan — what I did for you today, and exactly what is left

**Written 1 Sep 2026 (Day 3), because your PC was down.** Two people were blocked on your data,
so I did your Day 3 and most of your Day 4 rather than let them sit.

Read Part 1 so you know what changed in your own folder. Part 2 is the only thing still
outstanding, and it is about 90 minutes.

> ⚠️ **Gate 5 is all six of us explaining our own module cold.** I filled in your dataset card,
> but I cannot answer for it on the day — you have to. Part 2 Step 2 is thirty minutes that makes
> it genuinely yours. Please do not skip it.

---

# PART 1 · What I completed for you today

## ✅ Your Day-3 row: Kaguya TC — DONE

Downloaded `TC1S2B0_01_03482S746E0433.tif` (22.6 MB) and checked every acceptance criterion in
your spec. All passed exactly:

| check | expected | got |
|---|---|---|
| shape | 6220 × 6222 | ✅ |
| scale | 9.3698731836556 m/px | ✅ |
| NoData fraction | ~0.518 | 0.5182 ✅ |

It is on my machine at `C:\Users\samar\sih26166_data\raw\` and going to the Drive. **Best window
for everyone to use: `x=5120, y=2240`** — zero NoData, only 2.9% shadow.

## ✅ Your Day-4 row: `DATASET_CARD.md` — DONE, and I fixed two things in it

Every number came from the products themselves, never from a document:

- **CH-2 OHRC scale is 0.22977000623605362 m/px** — read from `<isda:pixel_resolution>` in ISRO's
  own label.
- **The scale ratio is 40.78×, not the ~36× our docs estimated.** This matters — it is Samartha's
  scale-invariance slide.
- **The two footprints really do overlap: 0.598° × 0.591°.** I read OHRC's from all 113,498 rows
  of its geometry CSV and Kaguya's from its metadata file, rather than trusting the estimate.

🔴 **Two corrections in your card, and neither is a criticism — both were in our shared docs too:**

1. **`SDRPHO` does not exist.** The card said Tier A would use it. The real name is `SDPPHO`
   (P, not R) — and that one is *still* wrong for us, because it has no valid incidence angles.
   The route is **`EDRNAC4`**.
2. **`M108587604RE.IMG` is rejected.** It was the only row in the card, and the image is empty —
   no craters, almost no variation. It stays in the card marked REJECTED, as our worked example.

## ⚠️ Your Day-4 SLDEM task: **CANCELLED — it was impossible**

**SLDEM2015 only covers ±60° latitude. Our demo site is at −74°.** It is named as our elevation
source in three of our own documents and scheduled as your Day-4 job. It could never have worked,
and you would have spent an afternoon finding that out.

**Replacement, already downloaded: LOLA `ldem_60s_60m`** — covers 60°S to the pole at 60 m/px,
which is the same resolution SLDEM would have given us. Nothing is lost.

## ⚠️ Your overdue Day-2 Tier A task: **half done**

I found **47 usable Tier A candidate pairs** — same site, sun angle differing by 15° or more.
The best is 38.4° apart at nearly identical scale.

**But I could not cut the actual image crops from them, and neither could you.** The images are
not map-aligned, so there is no reliable way to find the same patch of ground in both. I tried
four approaches and proved they do not overlap. **This is not something you failed to do** — it
needs map-projected products, which is about 2 hours and is mine, not yours.

## ✅ Housekeeping

Moved six files out of the repo root into `data/lroc_analysis/` — `ohrc_preview.png`,
`lroc_ohrc_matches.csv` and four others. Your LROC footprint analysis is genuinely useful work;
it was just sitting in the wrong place.

> ℹ️ **Also: your Day-6 M3 job has changed.** I decided today that our multi-modal leg will be
> **optical ↔ elevation** (Tier D) instead of optical ↔ infrared, because we already have the
> elevation data and it comes with exact ground truth. **M3 is now a stretch goal, not a
> dependency.** Do not start it until the catalogue is done.

---

# PART 2 · The one thing still outstanding — your Day-5 deliverable

**~90 minutes.** `data/pairs_catalogue.csv` does not exist yet. It is the only thing left on your
plate through Day 5, and Rishabh needs it for his Day-5 area calculation.

## Step 0 — Get a working machine (before anything else)

If your PC is still dead, use any laptop — this needs no GPU and barely any disk. You need Python
and git, nothing else. **Tell me in chat within the hour if you cannot get to a machine at all**,
because then I take Day 5 too and we plan around it.

```bash
git pull
```

## Step 1 — Read your own card (15 min)

```bash
```
Open `data/DATASET_CARD.md` and read it end to end. It is your file and it changed a lot today.
Pay particular attention to the section "Why `M108587604RE.IMG` is rejected" — the *reason* I first
wrote for that rejection was wrong, and the correction in there is worth understanding.

## Step 2 — Make one number yours (30 min) 🔴 **Do not skip this**

Pick **one** row of the card and re-derive its number yourself, so that at Gate 5 you are saying
"I checked this" rather than "Samartha told me". The easiest is the Kaguya scale:

```python
import sys; sys.path.insert(0, '.')
from core.io_loader import load

img, meta = load(r'C:\Users\samar\sih26166_data\raw\TC1S2B0_01_03482S746E0433.tif')

print(meta['gsd_mpp'])           # expect 9.3698731836556
print(img.shape)                 # expect (6220, 6222)
print((img == -32768).mean())    # expect about 0.5182  <- half the scene is empty
```

Then do the division that gives our headline scale ratio, by hand:

```
9.3698731836556  /  0.22977000623605362  =  40.78
```

**That single number is the one a judge is most likely to ask you about.** If you can say
*"Kaguya is 9.37 metres per pixel, Chandrayaan-2 is 0.23, so one is about 41 times coarser than
the other — and our method has to bridge that"*, you have passed your part of Gate 5.

## Step 3 — Build the catalogue (45 min)

Create `data/pairs_catalogue.csv`. The columns are already specified in your guide
(`ROHAN_DATA_GUIDE.md`), and **the `tier` column is mandatory** — it is how the whole team stays
honest about what each result actually proves.

🔴 **One change I am asking you to make to that schema: add a `status` column at the end.**
Right now only one pair actually exists as files on disk; the others are identified but not cut.
A catalogue that lists four pairs without saying which ones are real would mislead everyone,
including us.

Use `planned`, `identified` or `ready`.

**Here is every number I measured today, so you are transcribing rather than guessing.** Anything
I do not list below, **leave the cell blank** — never invent one:

**`pair_01` — the one that exists**
- tier: `same-frame offset crop` (⚠️ **NOT** "A" — see the warning below)
- both files: `pair_01_source.tif`, `pair_01_ref.tif`, instrument `CH2_OHRC`, gsd `0.22977`
- scale ratio `1.0`, status `ready`
- notes: `"two crops of one frame, known 40x25 px offset - wiring fixture, not a validation tier"`

**Tier B+ — CH-2 OHRC ↔ Kaguya TC** (both files on disk, pair not cut yet)
- tier `B+`, status `identified`
- source: `CH2_OHRC`, gsd `0.22977000623605362`
- ref: `Kaguya_TC`, file `TC1S2B0_01_03482S746E0433.tif`, gsd `9.3698731836556`
- **ref sun angles — these ARE known, fill them in:** incidence `86.548`, sun azimuth `284.911`,
  sun elevation `16.98` (from the JAXA label and STAC sidecar, both now on the Drive at
  `SIH26166_DATA/raw/`)
- scale ratio `40.78`, overlap `0.598` lat × `0.591` lon
- notes: `"cross-sensor, 40.8x scale. Kaguya NoData = -32768, 51.8% of scene. Use window x=5120 y=2240"`

**Tier A — LROC NAC ↔ LROC NAC** (candidates found, crops not cut)
- tier `A`, status `identified`
- source `LROC_NAC`, file `M118790149LE`, incidence `69.32`, gsd `0.553`
- ref `LROC_NAC`, file `M125868733LE`, incidence `30.95`, gsd `0.564`
- scale ratio `1.02`
- notes: `"same sensor - sun angle test only, 38.4 deg apart. Crops not cut: needs map-projected products"`

**Tier D — Kaguya TC ↔ LOLA shaded relief** (our multi-modal leg)
- tier `D`, status `identified`
- ref `LOLA_LDEM`, file `ldem_60s_60m`, gsd `60.0`
- notes: `"multi-modal: optical vs elevation. Exact ground truth. Replaces SLDEM, which stops at 60S"`

### 🔴 Three rules while you fill it in

1. **Leave sun angle and incidence BLANK for Chandrayaan-2 — but FILL THEM for Kaguya.** I checked
   both on 1 Sep. OHRC's label carries no illumination geometry at all, and neither does its
   geometry CSV. **Kaguya's label carries the full set** (incidence 86.548°, sun azimuth 284.911°,
   sun elevation 16.98°), so those cells are real numbers, not guesses.
   ⚠️ Incidence 86.5° means the sun is 3.5° above the horizon — a grazing polar sun. Worth knowing
   before you quote it. A *guessed* sun angle, by contrast, would silently corrupt Samrudh's entire
   illumination analysis — so for the CH-2 cells, blank is the correct and honest answer.
2. **`pair_01` is not Tier A.** It is two crops of the *same photograph*. Calling it a sun-angle
   test would be false, and it is the likeliest question an ISRO judge asks.
3. **The `tier` letter is a claim about what the pair proves**, not a label. Same sensor = A.
   Different instruments = B. Different modality (picture vs elevation) = D.

## Step 4 — Push and report (10 min)

```bash
git add data/pairs_catalogue.csv
git commit -m "pairs_catalogue v1: Tier A, B+ and D identified, with status per pair"
git push
```

Then post in chat, in your own words:
- the catalogue is up, and how many pairs are `ready` versus `identified`
- the scale ratio you worked out in Step 2
- that **Tier A crops are blocked on Samartha**, not on you

---

# Where that leaves you

| Day | Task | State |
|---|---|---|
| 1 | CH-2 OHRC download | ✅ you did it |
| 2 | LROC NAC Tier A set | ⚠️ half — 47 candidates found, crops blocked on me |
| 3 | Kaguya TC | ✅ **I did it today** |
| 4 | SLDEM tile · start DATASET_CARD | ✅ **I did it today** (SLDEM cancelled — impossible) |
| 5 | **`pairs_catalogue.csv`** | ⬜ **Part 2 above — yours, ~90 min** |
| 6 | M3 infrared | ⏸️ **demoted to a stretch goal** — do not start it |

Do Part 2 and you are fully caught up through Day 5.

---

## Rules that still apply

- **`data/` is yours.** Nobody else edits it. I did today only because two people were blocked;
  tell me if you would rather I had not.
- **Never guess a number to fill a cell.** Blank means "not known", and that is a real answer.
- **Nothing over ~5 MB in git.** Images and `.IMG` files go to the Drive. The repo already carries
  ~18 MB permanently from earlier and we cannot get it back out.
- **If a step takes 30 minutes longer than it says, say so in chat.** A spec that is wrong is my
  bug, not yours.
