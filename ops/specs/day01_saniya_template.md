# [Day 1] Saniya — the official SIH 2026 template

**Time: 2 hrs.** Read `day01_00_SHARED_SETUP.md` first.
**You need no repo access and no Python for this.** Start now.

> **This is the highest-value two hours anyone has today, and the headings assumed in our own docs
> are WRONG.** The real file has been downloaded and parsed. Your job is to confirm it independently
> and propagate the correction, because you own template compliance at Gate 5.

## Goal, in one sentence
The real 2026 template is downloaded, its actual slide headings are transcribed into the repo, and
the team knows our planning documents describe a slide that does not exist.

## Acceptance criteria
1. **Input:** `https://sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx`
   — **924,505 bytes**, sha256 begins `ce3e5dee`. A different byte count means the wrong file.
   *If your browser refuses, note that the server 403s non-browser requests — just download it
   normally through the browser.*
2. **Output:** `presentation/TEMPLATE_HEADINGS.md` committed and pushed, listing every slide's
   heading **and its bullet prompts**, transcribed from the file you opened yourself.
3. **Output:** one chat message with the headings and the correction flagged.

## Test cases
1. `slide_count` — the file has **7** slides: 6 template slides plus a final instructions slide.
   That instructions slide is **deleted** from our final deck.
2. `headings_match` — parsed from the real file:

| # | Real heading | Prompts on the slide |
|---|---|---|
| 1 | **TITLE PAGE** | Problem Statement ID · Problem Statement Title · Theme · PS Category (Software/Hardware) · Team ID · Team Name (registered on portal) |
| 2 | **IDEA TITLE** | Proposed Solution (describe your idea/solution/prototype) · Detailed explanation · How it addresses the problem · Innovation and uniqueness |
| 3 | **TECHNICAL APPROACH** | Technologies to be used · Methodology and process for implementation (flow charts / images / working prototype) |
| 4 | **FEASIBILITY AND VIABILITY** | Analysis of feasibility · Potential challenges and risks · Strategies for overcoming them |
| 5 | **IMPACT AND BENEFITS** | Potential impact on the target audience · Benefits (social, economic, environmental) |
| 6 | **RESEARCH AND REFERENCES** | Details / links of reference and research work |

   **Open the file and confirm this yourself.** If it differs, **the file wins** — tell the team immediately.

## The correction you must propagate
`00_CANONICAL_FACTS.md` §10 and `TEAM_TASK_GUIDE.md` both assume **Slide 1 = "Problem Statement"**.
**There is no Problem Statement content slide.** Slide 1 is a metadata **TITLE PAGE**, and the
template's own instructions slide says, verbatim:

> "Kindly keep the maximum slides limit up to six (6). (Including the title slide)"
> "You can only use provided template for making the PPT without changing the idea detail pointers."

So the cap **includes** the title page → **five content slides, not six.** Consequences to state in chat:

- Your Day 2 task "Draft Slide 1 (Problem Statement)" targets a slide that does not exist. Day 2
  becomes: fill the Title Page metadata, and start **Slide 2 (IDEA TITLE)** — "Proposed Solution" is
  its first bullet prompt, not the heading. Do not retitle the slide.
- The problem framing lives inside Slide 2's "How it addresses the problem" bullet, or in the spoken
  script — not on its own slide.
- Days 2–7 re-map to: Title Page + Proposed Solution → Technical Approach → Feasibility → Impact →
  Research. That frees roughly one day. Give it to **Impact and Benefits**, our weakest scored area.

## Starter
```markdown
<!-- presentation/TEMPLATE_HEADINGS.md -->
# SIH 2026 Idea Presentation — REAL headings

Source: https://sih.gov.in/letters/2026/SIH2026-IDEA-Presentation-Format.pptx
Downloaded: 2026-08-30 · 924,505 bytes
Transcribed by opening the file, not from any guide.

> Quoted from the template's own instructions slide:
> "Kindly keep the maximum slides limit up to six (6). (Including the title slide)"
> "You can only use provided template for making the PPT without changing the idea detail pointers."

| # | Heading | Prompts on the slide |
|---|---------|----------------------|
| 1 |         |                      |

## Corrections to our own docs
- 00_CANONICAL_FACTS.md §10 lists "Problem Statement" as slide 1. It is not — slide 1 is a
  metadata TITLE PAGE, and the six-slide cap includes it. We have five content slides.
```

## Dependencies
- Needs **nothing from any teammate**, and nothing from the repo to *start*. `presentation/` exists
  in commit `7644b4c`.
- Delivers to: **everyone.** This unblocks all deck work, Days 2–7. It is open question #2 in
  `ops/STATUS.md`.

## Do not
- **Do not download `SIH2025-...`.** Both years link from the same page and the filenames differ by
  two characters. The 2026 one is under `/letters/2026/`. Check the byte count: 924,505.
- **Do not commit the `.pptx`.** `.gitignore` **already blocks it** — line 25 is `*.pptx`, added in
  commit `e8a4e84`, verified with `git check-ignore -v presentation/deck.pptx`. So `git add` silently
  skips it and you get no error. Do **not** reach for `git add -f`. Commit `TEMPLATE_HEADINGS.md`
  (text) now; the binary lives in Drive. (An earlier version of this line claimed `.gitignore` does
  *not* exclude it. That was wrong — recalled instead of run, which is the exact failure mode that
  put `pip install magsac` in our docs.)
- **Do not add a seventh slide, rename a heading, or delete the template's bullet prompts.** Clarity
  in the prescribed format is a scored criterion, and the file itself forbids changing the pointers.
- **Do not start writing slide content today.** Confirming and propagating the headings is the whole
  task; content built on the wrong structure has to be rebuilt.
- **Do not put any number in any slide until it is in `evaluation/results_log.csv`** — which does not
  exist yet. Write `[TBD — results_log.csv]`.

## You are BLOCKED if
The URL 404s or the download is corrupt → **ping Samartha**, then ask your SPOC for the file
directly. Do not proceed on the assumed headings; that is the exact failure this task exists to
prevent.

## The ONE thing most likely to make your Day 1 fail
**You read the six assumed headings in `00_CANONICAL_FACTS.md` §10, they look authoritative and
plausible, and you never open the actual file.** Those six are wrong — there is no Problem Statement
slide, and the title page counts toward the limit. Days 2–7 would each build a slide against a
structure that does not exist.
