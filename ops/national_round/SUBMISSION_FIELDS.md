# SIH 2026 portal: what to type (SIH26166, team LunaXX)

The portal asks for four things (2026 Guidelines p.11): the chosen PS, an **idea title**, an
**idea description**, and the **idea presentation as a PDF**. No official character limit was
found, so each text field has a long and a short version. Paste the longest one that fits. Each
is in a code block: on GitHub the copy button takes it without the Markdown around it.

Every number below is on the deck (v9) and in `REPORT.md`, whose real-pair rows were **measured
at** the freeze commit `7dd4e5b`; REPORT.md itself was regenerated afterwards (at `3fa526b`), so
"in REPORT.md at 7dd4e5b" would be false - say "measured at". The character counts are
recomputed by a script whenever this file changes; do not trust a count typed by hand.

Both descriptions end with the repository URL: the portal has no link field, and slide 6 carries
the same URL and a QR code. If the repository is ever private on the day, cut that sentence.

| Field | Value |
|---|---|
| Problem Statement | SIH26166: Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS) |
| Theme / category | Space Technology · Software |
| Team ID | SNPSU0192 |
| Team name | LunaXX |
| PDF | `presentation/SIH26166_LunaXX_deck.pdf`, from `python -m presentation.export_pdf` (it must print `PDF CHECK: clean`) |

## Idea title

The first clause is the deck's title on slides 1 and 2. Not "Sun-, scale- and sensor-robust"
(v9 claim-check M8): OHRC → TMC-2 at 120° and TC → IIRS are refused, and 0 of 12 sweep windows
at 60–120° are accepted - slide 4 says so.

Long (105 characters):

```text
Lunar image registration that knows when it is wrong: Chandrayaan-2 matching across Sun, scale and sensor
```

Short (69 characters):

```text
Trust-aware Chandrayaan-2 image matching across Sun, scale and sensor
```

## Idea description

Long (1,923 characters):

```text
On the Moon a registration's residual can look excellent on a fit that no held-out match supports. We register Chandrayaan-2 images onto lunar references across Sun angle, scale and sensor, then check every answer with a test that never reads a match position.

After scale and lighting are normalised, LoFTR matches on a CPU, NCC refines to sub-pixel and MAGSAC++ fits a homography. An independent area check then cross-correlates the warped image against the reference in 8×8 cells. The cells vote: accepted, unconfirmed, or refused, and a refused result falls back to phase correlation, declared, with its uncertainty in metres.

Measured on 160 distinct ground windows and 8 instrument pairings of real Chandrayaan-2, LRO, Kaguya and LOLA data:
- SAC's equatorial OHRC → LRO NAC benchmark pair (arXiv:2509.04775), Sun azimuths 174° apart: 6 of 6 windows accepted.
- The whole lit overlap of one OHRC frame with one NAC at 74 °S, Suns 3.3° apart, tiled, none hand-picked: 37 of 37 accepted over 13.1 km², held-out median 0.61 px = 0.57 m on the 0.93 m NAC grid, 36 of 37 under 3 px.
- Scale: OHRC at 0.25 m onto Kaguya TC at 7.4 m (29.6×), 3 of 4 accepted.
- A Sun sweep of 69 windows, azimuths 3.3–152.7° apart: no undetected failure.
- Wrong answers planted in 30 real windows: no false alarm in either Sun population; every 5 m error flagged with the Suns within 10°, every 10 m error at 132–174°.

It also reports what it cannot do: visible → infrared (Kaguya MI 1548 nm) is refused on 3 of 3 windows, its fallback still within 3.4–16.2 m of the visible-band fit; OHRC → TMC-2 with the Suns 120° apart is refused on 4 of 4.

Outputs: a GeoTIFF on the reference grid, GDAL/QGIS control points, an ISIS match list, metrics and the trust map. Median 8.2 s per 640-px window on a laptop CPU, offline. Open-source (Apache-2.0); every number is regenerated from the logs by one command: github.com/samarthputhraya/sih26166
```

Short (575 characters):

```text
We register Chandrayaan-2 images onto lunar references across Sun angle, scale and sensor, and check every answer with a test that never reads a match position: the warped image is cross-correlated against the reference in 8×8 cells, and the result is accepted, unconfirmed or refused, region by region. On SAC's own OHRC → LRO NAC pair with the Suns 174° apart, 6 of 6 windows are accepted; wrong answers planted in 30 real windows are flagged from 10 m with no false alarm. CPU-only, offline, open-source (Apache-2.0). Code and evidence: github.com/samarthputhraya/sih26166
```

## Before pressing submit

1. Slide 1's Team ID must equal the portal's: SNPSU0192.
2. Open the PDF and page through all 6 slides once by eye. Its modification time must be later
   than the .pptx's.
3. **Open `github.com/samarthputhraya/sih26166` in a logged-out browser** (a private window is
   enough). If it 404s, the repository is private and slide 6 plus both descriptions point at
   nothing.
4. After submitting, take a screenshot of the confirmation. Write the time and the Team ID into
   `ops/STATUS.md`.
