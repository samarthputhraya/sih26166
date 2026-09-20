# SIH 2026 portal: what to type (SIH26166, team LunaXX)

The portal asks for four things (2026 Guidelines p.11): the chosen PS, an **idea title**, an
**idea description**, and the **idea presentation as a PDF**. The character limits were not found
in any official source, so a short and a long version of each is given below. Paste the longest
one that fits. Every number here is in `REPORT.md` at the evidence-freeze commit `7dd4e5b` (20 Sep
2026, after the audit's second pass); the deck carries the same ones. The character counts are the
quoted block joined into one paragraph with single spaces - the form you would paste - and they
are recounted whenever this file changes (they have been stale twice; recount, do not trust a
number written here by hand).

**Both descriptions now end with the repository URL**, because the portal has no link field and
the PDF is otherwise a closed box: slide 6 carries the same URL. If the repo is private on the
day, cut that clause rather than shipping a link a judge cannot open.

| Field | Value |
|---|---|
| Problem Statement | SIH26166: Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS) |
| Theme / category | Space Technology · Software |
| Team ID | SNPSU0192 |
| Team name | LunaXX |
| PDF | `presentation/SIH26166_LunaXX_deck.pdf`, from `python -m presentation.export_pdf` (it must print `PDF CHECK: clean`) |

## Idea title

Long (107 characters):

> Lunar image registration that knows when it is wrong: Sun-, scale- and sensor-robust Chandrayaan-2 matching

Short (71 characters):

> Trust-aware Sun-, scale- and sensor-robust Chandrayaan-2 image matching

## Idea description

Long (1,881 characters):

> We register Chandrayaan-2 images to lunar references across Sun angle, scale and sensor, and
> report, region by region, whether each alignment can be trusted. The pipeline runs in this
> order: one ground scale; illumination reduced to gradient orientation; LoFTR dense matching;
> sub-pixel refinement; MAGSAC++. An independent area check never sees the matches. It
> cross-correlates the warped image against the reference in 8×8 cells and returns agrees,
> unconfirmed or contradicted; a contradicted result falls back and says so. On SAC's own OHRC ↔
> LRO NAC pair (arXiv:2509.04775), with Sun azimuths 174° apart, all 6 windows are accepted. On
> the polar pair 4 of 6 are accepted and the other two are flagged. Across 160 real windows and 8
> instrument pairings (OHRC, TMC-2, IIRS, LRO NAC, Kaguya TC and MI, LOLA): tiling the whole lit,
> textured overlap of one OHRC frame with one NAC at 74 °S, 37 windows over 13.1 km² with no
> window hand-picked, accepts 37 of 37 at a held-out median of 0.61 px = 0.57 m on the 0.93 m NAC
> grid, 36 of the 37 under 3 px; three-image loops close to 0.107 m (0.086 px on the 1.245 m NAC
> grid), which is consistency, not ground accuracy. Planted wrong answers on 30 real windows: 0%
> false alarms, 100% flagged from 5 m on the 22 windows with Sun azimuths under 10° apart, and
> from 10 m on SAC's windows at 132–174°.
> Visible ↔ infrared (Kaguya TC → MI 1548 nm): the matcher is refused on all 3 windows and the
> declared fallback lands 3.4–16.2 m (0.23–1.09 px on MI's 14.8 m grid) from the visible-band
> registration of the same window. Outputs: a GeoTIFF on the reference grid, match points (CSV, GDAL/QGIS, ISIS), metrics
> and the trust map. Median 8.2 s per 640-px window on a CPU laptop, offline, open-source
> libraries only. Every number is regenerated from logs by one command.
> Code, evidence logs and the full report: github.com/samarthputhraya/sih26166

Short (562 characters):

> A lunar image-registration engine that aligns Chandrayaan-2 imagery to lunar references across
> Sun angle, scale and sensor. It also says, region by region, whether the result can be trusted,
> using an independent area check that never sees the matches. On SAC's own OHRC ↔ NAC pair, with
> Sun azimuths 174° apart, 6 of 6 windows are accepted. Planted wrong answers in real windows are 100%
> flagged from 10 m, with 0% false alarms. It outputs a GeoTIFF, match points and metrics, and runs
> CPU-only and offline. Code and evidence: github.com/samarthputhraya/sih26166

## Before pressing submit

1. Slide 1's Team ID must equal the portal's: SNPSU0192 (set 20 Sep; `AUDIT: clean`,
   `PDF CHECK: clean`). Re-run both commands only if anything in the deck changes.
2. Open the PDF and page through all 6 slides once by eye.
3. **Open `github.com/samarthputhraya/sih26166` in a logged-out browser** (a private window is
   enough). If it 404s, the repo is private again and slide 6 plus both descriptions are
   pointing at nothing - that is worse than having no link at all.
4. After submitting, take a screenshot of the confirmation. Write the time and the Team ID into
   `ops/STATUS.md`.
