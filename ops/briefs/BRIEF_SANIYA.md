# Brief for Saniya — `presentation/` — what changed on 3 Sep and what the deck must now say

**Read time: 12 minutes.** `presentation/` is still empty. The deck is the deliverable on 9 Sep and
`docs/SANIYA_NARRATIVE_GUIDE.md` was rewritten tonight around the Phase 1 decision. Start from it,
and from `ops/PHASE1_NOVELTY_DECISION.md`.

## The one thing that changed: the innovation bullet

The four old bullets (illumination normalisation, common-GSD resampling, enforced uniformity, DEM
re-rendering) are **off slide 2**. Two are the preprocessing steps of the PS-setters' own paper
(arXiv 2509.04775, Space Applications Centre, 2025 — read its abstract); one was never wired; one is
standard methodology. The innovation bullet is now:

> "Every registration tool gives you one accuracy number for the whole image. Ours tells you, cell
> by cell, where the alignment is *verified*, where it is *weak*, and where it has *no evidence at
> all* — and when its own matcher is confidently wrong, it says so and switches method."

Under it, three lines of evidence (all numbers in `evaluation/results_log.csv`; the rows are named):

- **Calibrated** (row `reliability_calibration_pooled`, the one whose config says
  `matcher arm: ours_loftr+subpixel`): over 20 ground-truth pairs, verified cells median true error
  0.162 px (9.7 m at 60 m/px), 92% under half a pixel, 98% under one pixel; weak cells 0.363 px;
  no-evidence cells 0.766 px (45.9 m).
- **Caught a confident failure on real data** (rows `pair_04_tierD_native`): the matcher's 87
  correspondences reached RANSAC consensus; 0 of 87 were correct within 10 px; 0% of the 35
  measurable cells agreed with the transform; the system fell back to global correlation and
  registered the pair by 231 m with a quadrant disagreement of 216 m, and said so.
- **Cites its prior art on the same slide**: Uss et al. 2016 (per-region accuracy without ground
  truth), Brown & Lowe 2007 (match verification from inlier counts — the test our failure passes),
  Wan et al. 2021 (correlation where features fail on optical ↔ DEM). Ours: the no-evidence state,
  pixels-vs-matches disagreement as the failure signal, calibration on lunar data.

## Slide by slide (six including the title; the template is unchanged)

| Slide | What goes there now |
|---|---|
| 2 IDEA | The sentence above; one picture: the reference image tinted green / amber / grey (from the app); the three evidence lines. |
| 3 TECHNICAL APPROACH | Pipeline diagram: load → common GSD → illumination normalisation → LoFTR → MAGSAC++ → **trust layer (cell vote) → declare method / fallback** → metrics. Say "resampling and normalisation follow the SAC 2025 benchmark". |
| 4 FEASIBILITY | CPU-only (Intel iGPU, no CUDA), offline, weights cached, Apache-2.0 LoFTR vs SuperGlue's non-commercial SuperPoint weights; 5.5 s per 640² tile. Risks: no real sun-difference pair yet (MiLOI is the route), no cast shadows in the synthetic renders. |
| 5 IMPACT | Landing-site work (SAC's Chandrayaan-4 Mons Mouton characterisation uses OHRC), change monitoring, mosaicking — and the operational point: an analyst gets *where to trust*, not one number. |
| 6 REFERENCES | arXiv 2509.04775; Uss 2016; Brown & Lowe 2007; Wan 2021; Xie et al. 2025 (MiLOI); Geo-LoFTR 2025; Wagner et al. 2024. |

## The 20-second moment (slide 2, spoken)

"On the one real multi-modal pair we own, our matcher produced 87 confident correspondences. Every
one was wrong — we built the ground truth and checked. A fit residual would have called it
sub-pixel. Our system looked at the pixels, said 'this transform is contradicted', switched
method, and reported the uncertainty. That is the feature."

## Never say (this list is now in the narrative guide too)

Cross-sensor · pyramid · "we enforce uniformity" · "a 2025 paper benchmarks LoFTR on Chandrayaan-2"
(it benchmarks SuperGlue) · any Tier D number as an accuracy · "accurate shadows" · "0.7 px".

## Two dates to confirm with the SPOC before the deck is final

The official SIH 2026 SPOC guideline says portal submission closes **15 Sept**; the PS listing says
**20 Sept**. And ask for the college's own scoring sheet — the two public ones we found weight
innovation 25–30% and relevance 25%.
