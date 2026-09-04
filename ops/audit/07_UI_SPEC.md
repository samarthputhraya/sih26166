# Area 07 — UI rebuild spec (Day 6 recon; NOT yet implemented)

**Winner:** Direction 1 — Reference Frame (instrument skin), 32/40. It wins on the two axes that carry marks: projector legibility, where it is the only entry with measured contrast ratios and a live in-app type-size rescue that does not scale the imagery; and the honesty of its rendering templates, where the primary-readout markup has no slot for a bare pixel number, making the deck's slide-4 defect structurally impossible in the one artefact a judge operates. It is also the cheapest to implement correctly, because `st.html` avoids the Streamlit markdown-indent trap that Direction 2 has to work around and Direction 3 inherits.

## Synthesis

Ship Direction 1's skin, with four grafts and one deletion.

GRAFT FROM DIRECTION 3 — (a) the persistent state rail, but NOT sticky and NOT rendered where D3 puts it. Reserve it with `st.empty()` immediately after CSS injection and fill it at the END of the script, so STATE can never read READY above a live result. Non-sticky because it costs ~90px of permanent vertical space on a 768px projector and D3 concedes it may jitter. (b) The ASCII cell map beside the overlay via the existing `core.reliability.ascii_map` — free, already tested, survives a photograph of the screen. (c) ASCII-only in the Python source, entities in the HTML, grounded in the 7 mojibake lines in results_log.csv. (d) numpy `mgrid` masks for the hatch instead of `cv2.line`, which removes the need to add `import cv2` to the demo path at all.

GRAFT FROM DIRECTION 2 — (a) the `@media print` block. Ctrl+P is the fallback if the projector dies and it produces a handout; nobody else thought of it and it costs 12 lines. (b) The terrain-FADE mechanism as the implementation of D1's 'absence renders as absence' — fade the no-evidence cell toward paper rather than tinting it grey, so verified is the only state that leaves the terrain at full contrast. (c) The two cheap unit tests: SKIN contains no `http` (Invariant 3 as an assertion) and no `st-emotion-cache`.

DELETE FROM DIRECTION 3 — the 40px metres hero. Keep D1's neutral readout band. A large confident distance above 'no cell can be verified' is the wrong instinct on the one pair the team most needs to be honest about.

KEEP FROM DIRECTION 1 — `cv2.putText` glyphs V / W / — in each cell. The ASCII map is the distance channel; the in-cell letter is the channel that survives someone pointing at a specific crater. Both, not either. Draw them once and cache.

SCHEDULE OVERRIDE, and this is the load-bearing correction: Direction 1 says 'Day 8 at the earliest'. Per 00_CANONICAL_FACTS.md:416 Gate 3 IS Day 8 (6 Sep) and Gate 4 is Day 9. Implement TONIGHT (Day 6) or Day 7 morning, in ONE sitting, and smoke-test before the stranger sees it. A half-applied skin is worse than none. If it is not finished and smoke-tested by end of Day 7, revert the whole commit and demo the stock app — that decision must be made on Day 7, not on Gate 3 morning.

## Concrete spec — implement this

## 0. PALETTE (exact hexes — these are the only colours in the app)

Ground and structure:
  --ground     #F7F7F4   page field (paper, not #FFFFFF — a bright lamp blooms on pure white)
  --panel      #ECEBE6   sidebar, table header, verdict strip background
  --panel-2    #E2E0D9   nested/inset, code inside a verdict
  --plate      #E8E7E2   behind image plates
  --rule       #C9C7BF   hairline
  --rule-hard  #8C8A82   section rule

Ink:
  --ink        #14171A   body            16.6:1 on --ground
  --ink-mute   #5A5D63   captions, units  5.7:1
  --ink-faint  #7C8087   metadata, void values

Signal — four colours, all dark and desaturated, no pastels, no tints:
  --accent     #14487F    8.4:1  interactive. ONE element uses it: the Align button.
  --ok         #146B3C    6.0:1  verified / PASS / DECLARED
  --caution    #A8560A    4.7:1  weak / FALLBACK USED.  TIGHTEST — verdict word and 4px bar only, NEVER body text.
  --fail       #A3231E    6.8:1  contradicted / FAIL / NO TRANSFORM

Reliability overlay composited over the greyscale plate (numpy, no cv2 needed for fill):
  VERIFIED     tint (20,107,60)  alpha 0.30, no fade, solid 3px border, glyph "V"
  WEAK         tint (168,86,10)  alpha 0.36, plus 45-deg hatch (mask darkens to x0.60), dashed 3px border, glyph "W"
  NO_EVIDENCE  NO TINT. fade toward paper: block = 0.55*block + 0.45*(247,247,244). dotted 1px border, glyph "-"
  Only VERIFIED leaves the terrain at full contrast. Absence renders as absence.

## 1. FONT STACKS (verbatim, no web fonts, no `http` anywhere in the file)

  --mono: Consolas, "Cascadia Mono", "DejaVu Sans Mono", "Liberation Mono", Menlo, Monaco, "Courier New", monospace;
  --sans: "Segoe UI", "Segoe UI Variable Text", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial, "Liberation Sans", sans-serif;

No serif family. Three roles, no exceptions: mono for anything MEASURED, sans for anything ARGUED, mono-uppercase-.72rem-tracking-.11em for every panel label.

## 2. SPACING SCALE (4px base — use these tokens, invent nothing)

  --s1 4px  --s2 8px  --s3 12px  --s4 16px  --s6 24px  --s8 32px  --s12 48px  --s16 64px

Type scale, all rem so the projector knob scales everything at once:
  label .72rem / micro .82rem / body 1rem / section-label .74rem / table-num 1.06rem / readout-value 2.75rem
  html { font-size: 17px }  normal
  html { font-size: 19px }  projector mode  (ONE token, one .replace())

Geometry: `layout="wide"` stays; `[data-testid="stMainBlockContainer"]` max-width 1320px; prose paragraphs max-width 78ch; `baseRadius` none and every radius zeroed in CSS; zero box-shadows.

## 3. FILES

CREATE `.streamlit/config.toml` — Direction 1's Block A verbatim ([theme] base=light, primaryColor #14487F, backgroundColor #F7F7F4, secondaryBackgroundColor #ECEBE6, textColor #14171A, font="sans serif" as the legacy-safe LITERAL; [browser] gatherUsageStats=false; [client] toolbarMode="minimal"; [server] fileWatcherType="none"; [logger] level="warning"). Block B stays COMMENTED. Before uncommenting, run against the real venv, not a bare python:
  C:\Users\samar\venvs\sih26166\Scripts\python.exe -c "from streamlit import config; print('\n'.join(k for k in config.get_config_options() if k.startswith('theme')))"
Do NOT put a font STACK in theme.font. An unknown KEY warns; an invalid VALUE for a known key is what raises, and that is a Gate 4 failure.

## 4. ORDERED CHANGES TO app/streamlit_app.py

1. After line 51 add `import html as _h`. Do NOT add `import cv2` — the hatch is numpy; the glyphs come in step 9 and are the only cv2 use, so `import cv2` goes inside `reliability_overlay()` guarded by try/except with a bare-tint fallback.
2. Add module constant `SKIN = """<style> ... </style>"""` — Direction 1's CSS block, WRAPPED IN `<style>` TAGS (as delivered it has none and would print as text), plus Direction 2's `@media print` block appended. ASCII only in the Python source; typographic characters as `&middot;` `&mdash;` entities.
3. Line 272: extend `set_page_config(..., initial_sidebar_state="expanded", menu_items={"Get help":None,"Report a bug":None,"About":None})`, no `page_icon`. Next statement: `st.html(SKIN.replace("__BASE_PX__", "19px" if st.session_state.get("projector") else "17px"))`.
4. Immediately after: `_rail = st.empty()` — reserve, do not fill.
5. Lines 273-277: delete `st.title` + `st.caption`. Replace with the identification plate via one `st.html`: name + `ISRO SIH26166`, one-line subtitle, then a tag strip `CPU ONLY` / `OFFLINE` / `REFERENCE GRID {gsd} m/px` / `BUILD {commit7}`. `{gsd}` is `r['gsd_mpp']` once a result exists and the literal `NOT DECLARED` otherwise — never a guess. `{commit7}` from the sidecar `git_commit` that `load_cached_result()` already parses at 250, else `UNCOMMITTED`.
6. Line 282 and 349: replace `st.header("1 - Choose a pair")` / `st.header("2 - Align")` with `st.html('<div class="panellabel">01&nbsp;&nbsp;SELECT PAIR</div>')` / `02&nbsp;&nbsp;ALIGN`. Delete `st.divider()` at 348. Keep the same-instrument `st.info` at 318-322 exactly as written — that block is the Invariant 2 defence and must stay loud.
7. After 367 add `st.checkbox("Projector mode (larger type)", key="projector")`.
8. Add `def seclabel(n, text, note="")` emitting `.seclabel`. Apply at 429, 487, 512, 545, 599 and 686, DELETING the `st.divider()` at 486, 511, 544, 598, 686 and the `st.subheader()` at 429, 487, 512, 545, 599. Labels: `01 RESULT` (note = the `result_origin` string from 431, folded into the header), `02 SWIPE - REFERENCE VS ALIGNED`, `03 WHERE THE ALIGNMENT CAN BE TRUSTED`, `04 THE FIVE METRICS`, `05 CHANGE DETECTION`, `06 WHAT THESE NUMBERS DO AND DO NOT PROVE`.
9. Lines 433-453: replace the three alerts with `verdict_strip(kind, word, body_html)` — `("fail","NO TRANSFORM")`, `("caution","FALLBACK USED")`, `("ok","DECLARED")`. Sentences unchanged, they are audited text. Every interpolated `declared['why']`, `fallback` prose and catalogue `notes` goes through `_h.escape()` first.
10. Lines 455-465: delete the c1/c2/c3 heading row. Put a `.platecap` UNDER each image in the `imgs` columns at 477-482: `<b>Source</b> &middot; (2048, 2048) &middot; the image being moved`. Recovers a full row of projected height.
11. Line 80 + 210-232: rewrite `STATE_RGB` -> `STATE_TINT` / `STATE_ALPHA` / `STATE_FADE` / `STATE_GLYPH` per section 0. Fill and hatch with `yy, xx = np.mgrid[0:bh,0:bw]`; hatch mask `((xx+yy) % 8) < 2`; borders drawn by slicing, dashed via `(coord % 12) < 7`, dotted via `(coord % 8) < 2`. Glyph via `cv2.putText(..., FONT_HERSHEY_DUPLEX, scale=cell_h/60)` two-pass — `(20,23,26)` at thickness+3 then `(255,255,255)` at thickness — inside a try/except ImportError that degrades to tint+hatch only. Keep the 1px grid lines at 229-230.
12. PERFORMANCE, mandatory: the seam slider at 493 forces a full rerun on every drag and the overlay is currently redrawn each time. Compute it once when the result lands and stash it: `st.session_state["overlay_rel"] = reliability_overlay(...)`, keyed alongside `pair_label`; `reset_results()` at 259 already pops on pair change — add `"overlay_rel"` to its tuple.
13. Lines 524-527: delete the three `st.metric` calls. Replace with the `.legend` list — swatch (solid / hatched via the same `repeating-linear-gradient` / dotted-empty), glyph V / W / -, count `21 / 64`, word. Drop the `caption=` on `st.image` at 531; the legend now says it.
14. After the overlay image, add the ASCII map: extend the import at line 69 to `from core.reliability import NO_EVIDENCE, VERIFIED, WEAK, ascii_map, describe, gate`, split into `mc = st.columns([3,1])`, and render `mc[1].html('<div class="cellmap">' + _h.escape(ascii_map(rel)) + '</div>')` with `white-space: pre; font-size: 18px; letter-spacing: .12em`. Caption: `V verified   w weak   . no evidence. Row 0 is the top of the image.`
15. Lines 532-535 + 541: collapse the `describe()` caption loop into ONE mono `.log` block, `white-space: pre`, keeping the `startswith("true error")` skip verbatim; append `Rule applied: {rel['config']}` as the last line.
16. Lines 85-92 + 554-566: extend `METRICS` with a places and a unit column (rmse 4 px, residual 4 px, inlier_count 0, inlier_ratio 3, grid_coverage 3, distribution_cv 3) — no VALUE changes. Change `verdict()` at 193 to return the tuple `(ok, op, threshold)`, logic byte-identical. Replace `st.dataframe(rows, ...)` at 566 with a hand-built `<table class="mt">` — METRIC / VALUE / WHAT IT MEANS / GATE 2 — because `st.dataframe` renders to a canvas and no CSS can reach its typography. Value cell carries full precision in `title=`. Gate cell renders the WORD `PASS`/`FAIL` plus `(&lt; 0.5)`; colour only reinforces. `rmse_gt_px is None` renders LEFT-aligned `n/a - no ground truth on a real pair` in `.num--void`, so a missing value can never be misread as a number in a right-aligned column.
17. Lines 571-580: delete the `st.success` and its caption fallback. Replace with the `.readout` band, ABOVE the metrics table, in exactly one of two forms and no third: value at 2.75rem mono + `px`, then `= <b>{resid*gsd:.2f} m</b> on the ground &middot; reference grid {gsd:.4g} m/px &middot; {Path(r['reference']).name}`; or `.readout--void` with the value greyed and the reason in --caution. The markup has no slot for a bare pixel figure.
18. Fill the rail from step 4 at the very end of the script: `_rail.html(...)` with PAIR / TIER / SENSORS / STATE / RESULT SOURCE / CPU TIME / `CPU - OFFLINE`, all `_h.escape()`d, `--` where unknown. Filling last is what stops STATE reading READY above a live result.
19. Lines 686-706: keep the expander and its four bullets verbatim — the most defensible prose in the file. Only the `seclabel("06", ...)` and the `.colophon-foot` styling change.
20. KEEP `st.dataframe` at 675 for the change-candidates table only (hundreds of rows need virtual scrolling); add `height=320`. `STATE_WORD` at line 81 already gives it a non-colour channel — leave it.
21. Extend `app/test_streamlit_app.py`: assert `"http" not in SKIN` (Invariant 3 as a test — it would catch a font CDN before Gate 4 rather than during it) and `"st-emotion-cache" not in SKIN`.

## 5. REHEARSAL, in the room, in this order (90 seconds)

(a) Read the readout and all five metric values aloud from the back row. If `inlier_ratio` is ambiguous, tick Projector mode and STOP — do not start restyling. (b) Photograph the reliability map from the back row and confirm V / W / - resolve; if not, hatch period 8 -> 12. (c) Confirm the browser is at 100% zoom and no extension is inverting the page. (d) Ctrl+P -> Save as PDF, background graphics ON — that is the artefact if the projector dies. (e) Launch from the repo root or `.streamlit/config.toml` is ignored and a Windows-dark-mode laptop inverts the whole app.

## 6. SCOPE

Touches `app/streamlit_app.py` and `core/reliability.py`'s import line only (both Samartha's), plus a new root-level `.streamlit/`. No number is added, computed or reformatted in value — Invariant 1 untouched, `evaluation/metrics.py` remains the only source. Say so explicitly in the commit message.

## 7. OUT OF SCOPE, AND SAY SO OUT LOUD

None of this fixes the audit findings. Separately and unrelated to the skin: `grep -c "â" evaluation/results_log.csv` returns 7 rows of cp1252 mojibake in the notes column of an append-only file, and HEAD carries a UTF-8 BOM that commit 9794a4d did not. That is a data-provenance issue for whoever owns the log, not a CSS one. A better-looking demo of a wrong number is worse than an ugly demo of a right one.

## Scores

| direction | SIH-fit | projector | avoids-AI | feasible | total |
|---|---|---|---|---|---|
| Direction 1 — Reference Frame (instrument skin) | 8 | 9 | 8 | 7 | 32 |
| Direction 2 — Plate (engineering-report skin) | 7 | 7 | 8 | 6 | 28 |
| Direction 3 — Console 26166 (mission-ops readout) | 7 | 7 | 6 | 7 | 27 |