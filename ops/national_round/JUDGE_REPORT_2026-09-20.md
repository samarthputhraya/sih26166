# Judge's walk-through — SIH26166 / team LunaXX

**Inspected 20 Sep 2026, 19:45–21:30 IST, at commit `f052202`** (evidence frozen at `7dd4e5b`).
Read-only: this file is the only thing written. Nothing under `core/`, `evaluation/`, `ops/`,
`app/`, `presentation/` or `web/` was touched; `ops.freeze` and `ops.precompute_demo_cache` were
not run. `git status` at start and at finish: the same two untracked files
(`.claude/commands/judge.md`, `ops/national_round/JUDGE_PROMPT.md`) plus this report.

Every figure below came from a command I ran, a file I read, or a screenshot I took. Where I could
not check something, the report says so instead of guessing.

**Grade in one line: Above average, one token-fix and one link away from High.**

> **Status, added 22:50 the same night — most of this is already fixed.** Every item in §7's
> "before Fri 25 Sep" list was applied except the demo-cache re-run, which was declined on the
> record because its own command would have drifted two Mission Console pairs away from
> `REPORT.md`. The repository is now **public** and slide 6 carries its URL; the OHRC→TMC-2 and
> IIRS terminology defects are gone; the live bay clears its panel and refuses an over-cap upload
> before sending; `web/dist/index.html` fixes the README's broken path; Lighthouse is
> **100 / 100 / 100**. `ops/STATUS.md` → "Judge-report fixes" has the table, the verification for
> each row, and what was deliberately left alone. **Read this report for the reasoning, not as a
> live defect list.** One correction it did not catch, found afterwards by `claim-checker`: the
> slide-6 bullet this report asked for was first written as "in REPORT.md **at** the freeze
> commit", which is false — the freeze *measures* the rows and `REPORT.md` is regenerated
> afterwards. Fixed in four files, and the deck's own audit now verifies the claim.

---

## 1. The reachability chain

**A judge who only opens the PDF sees 1 of the 4 artefacts (25 %), about 8 % of the report's
distinct figures, 2 of the 10 registered pairs as pictures, and 0 of the 8,658 rows of evidence.**

| Check | Command / observation | Result |
|---|---|---|
| Hyperlinks in the PDF | `pymupdf` `page.get_links()` on all 6 pages | **0 link annotations on every page** |
| Any URL in the deck source | `grep -n -i "http\|artifact\|github\|claude.ai" presentation/build_deck.py` | no repo, artifact, video or demo URL |
| Slide 6 rendered | page 6 → PNG, read | references only; **~⅓ of the slide is empty** (matches Known issue 11: "only slide 6 has room") |
| Repo visibility | `gh repo view samarthputhraya/sih26166 --json isPrivate` | `{"isPrivate":true,"visibility":"PRIVATE"}` |
| Mission Console artifact | `Artifact` list → "LunaXX Mission Console — https://claude.ai/artifact/LbbZKdvnVYCCBbPjEBZCA9 — updated 2026-09-20" | exists and is yours. Share state **unverified from this session** (see §3f) — `web/README.md` §2 and `STATUS.md` both say private |
| Portal fields | `ops/national_round/SUBMISSION_FIELDS.md` | the portal asks for **four** things: PS, idea title, idea description, PDF. **There is no link field.** A URL can only reach a judge inside the description text or printed on the PDF |
| Live console | `python -m web.server` binds `127.0.0.1` | finale room only, by design |
| Streamlit | localhost | finale room only |
| Video | `web/dist/mission-console.mp4` is gitignored and published nowhere | unreachable |

Numbers behind the 8 %: the deck's extracted text carries **90 distinct numeric tokens**;
`REPORT.md` carries **1,128**. 69 of the deck's 90 also appear in `REPORT.md` (the other 21 are
arXiv ids, years, slide numbers and template boilerplate). Evidence rows behind it all:
`results_log.csv` 3,299 · `miloi_log.csv` 1,296 · `real_pairs_log.csv` 929 ·
`trust_real_calibration.csv` 3,060 · `multimodal_check.csv` 32 · `miloi_illumination.csv` 42 —
**8,658 rows**, none of them reachable.

This is the single largest finding in the report. Everything else is a defect inside an artefact
that most judges will never open.

---

## 2. Judge B's four minutes — written before any documentation was read

I opened the six-slide PDF, then the console, and gave each the time it would really get. The
console was read on the `python -m web.server` path, which is the wrapper the Artifact runtime also
supplies (`web/server.py:52-70` says so explicitly).

**What is this, in one sentence, from the screen alone?**
From the deck: "a system that aligns Chandrayaan-2 pictures of the Moon to other lunar pictures and
says how well it did." From the console, immediately and without effort: *"Lunar registration that
knows when it is wrong."* The console's headline does in five words what slide 2 takes four
paragraphs to do.

**The one unusual thing.** That it refuses. The console **says so**, in 60 pt type, above the fold.
The deck makes me **infer** it — slide 2's second trust map is captioned "CONTRADICTED — refused,
fallback declared", which is the right idea in a font I have to lean in to read.

**One image that proves the idea without a caption?**
Yes, on both: the **two 8×8 trust maps side by side on deck slide 2** — one mostly green, one
entirely un-green. A person who knows nothing about registration understands "this one it trusts,
this one it doesn't" in about two seconds. That image is the deck's best asset and it is doing more
work than the 400 words beside it.

**Where did my eye go first, and was that right?**
Deck: to the figure on the right, then to the orange bold line at the bottom of slide 2. Correct
both times — the figure is the point and the orange line is the strongest claim.
Console: to WRONG in red. Exactly right.

**Numbers on the first screen.** Deck slide 2: I count 40+ numeric tokens in the left column alone.
Console hero: **21**, of which 6 sit in a labelled stat strip and the rest are in prose. The
console's density helps; **the deck's buries.** Slides 2, 4 and 5 read as a dense technical note
rather than a pitch — which Known issue 11 already records as "at capacity".

**Top 5 of a 40-entry pile at four minutes?**
**The console: yes, easily — probably top 2.** It looks like a product, it has a thesis, and it
does not look like a student project.
**The deck alone: borderline yes**, on the strength of the flow diagram and the fact that it is
visibly measuring real things — but it is carried there by the reader's patience, not by design.
And the deck alone is what almost every judge will get.

---

## 3. The inspection log

### 3a. Three ways of serving the same file — they are not the same

`web/dist/mission-console.html` is a **fragment**. `web/server.py` wraps it in a document
(`SKELETON`, lines 57–70). Nothing else does.

| | `python -m web.server` :8000 | static `http.server` over `web/dist` :8011 | `file:///…/mission-console.html` |
|---|---|---|---|
| `doctype` | **true** | false | false |
| `compatMode` | **CSS1Compat** | **BackCompat (quirks)** | **BackCompat (quirks)** |
| `characterSet` | UTF-8 | **windows-1252** | UTF-8 |
| `meta viewport` | **present** | **absent** | **absent** |
| mojibake count | **0** | **60** | 0 |
| LIVE bay | shown (`display:block`) | hidden (`display:none`) ✔ | hidden ✔ |
| `document.scrollHeight` | 7877 | 7362 | 7338 |

On the static path the header renders **`SIH26166 Â· CHANDRAYAAN-2 IMAGE CORRESPONDENCE`** and
**`EVIDENCE FROZEN Â·`**, and the body reads **`The engine is Python â€" LoFTR`**. Chrome's own
console logs `Page layout may be unexpected due to Quirks Mode`. Screenshot taken.

Worse than cosmetic: with the reset missing, `[hidden]` loses to `.io{display:grid}` (the comment in
`server.py` predicts exactly this). I measured it — inside `.plateimg` there are two 610×610 images,
and on the static path **both render**:

```
server :8000   plate imgs → [{h:610, hidden:false, display:"block"}, {h:0, hidden:true, display:"none"}]
static :8011   plate imgs → [{h:610, hidden:false}, {h:610, hidden:true}]   ← the hidden one paints
```

The visible effect: the trust-map cell colours go dark and muddy, so **verified green and weak brown
stop being distinguishable**. Side-by-side screenshots of the same pairing on both paths confirm it.

**This is the path `web/README.md` §1 tells an operator to take** — "Writes
`web/dist/mission-console.html` — one self-contained file… Open it in any browser." It is not
self-contained, and opening it in any browser is the one thing that breaks it.

### 3b. Every bay, every control

**SUN — correct at every stop, including both ends.** The slider is `#dz`, `min=0 max=160 step=1`.
Driven across 19 stops with two `requestAnimationFrame` awaits between each (see the note below),
the readout, the shaded band on the scatter, the arrow position and the count table agree
everywhere:

| slider | readout | band | windows · frames |
|---|---|---|---|
| 0, 1, 3, 9 | 0, 1, 3, 9° | 0°–10° | 16 · 6 |
| 10, 29 | 10, 29° | 10°–30° | 14 · 5 |
| 30, 59 | 30, 59° | 30°–60° | 12 · 4 |
| 60, 61, 89 | 60, 61, 89° | 60°–90° | 7 · 3 |
| 90, 119 | 90, 119° | 90°–120° | 5 · 2 |
| 120, 121, 152, 153, 159, 160 | matching | 120°–180° | 15 · 5 |

16+14+12+7+5+15 = **69 windows**, 6+5+4+3+2+5 = **25 NAC frames** — identical to `REPORT.md`
lines 253–260, bin for bin, including the median-inlier column (4818 / 4247 / 559 / 58 / 8 / 209).
The 3D relief and the SUN A / SUN B / BLINK A/B buttons all respond (`aria-pressed` tracks, and
the lighting visibly flips; screenshots at Δ = 137° SUN B and Δ = 153° SUN A).

> **Measurement note, so nobody re-files this as a bug.** My first three sweeps appeared to show
> the slider stuck one step behind, and the left end reading 160°. It was not. The MCP-driven
> Chrome window is not OS-frontmost, so `requestAnimationFrame` fired every **358 ms**
> (`visibilityState` still `"visible"`) — Known issue 20, in a second guise. Polling on a timer
> reads stale DOM. Awaiting rAF makes the readings exact. Anyone re-running this must await rAF,
> not `setTimeout`.

**TRUST MAP — all ten pairings, all layers, all clean.** Clicked every pairing, then every layer
button on each, hashing the `src` of `#imgA` and `#imgB` at each step.

- **The refused-pair trap is genuinely fixed.** On all five CONTRADICTED pairs the button reads
  `MATCHER'S ANSWER · REJECTED`, and its image hash differs from `FALLBACK, DELIVERED`'s. Example
  (OHRC → NAC polar): warp `67095:641666261`, fallback `67079:-1927864060`. Different images, and
  the rejected one is the one the page opens on.
- **No pairing shows another pairing's data.** All 10 pairs have distinct image hashes and distinct
  verdict panels. (Pairs 4 and 10 share an `INPUT A` hash because they genuinely share the same
  OHRC source window.)
- Every panel names its grid and gives metres: e.g. "median inlier residual 0.60 px = 0.97 m ·
  pixel grid 1.622 m/px (reference)". Invariant 2's sub-pixel rule is honoured in the trust map.
- The `GRID` toggle works and returns. The 37 window footprints in **TILING are individually
  clickable** (verified: clicking three of them moved the panel to W01, W02, W03) — an interactive
  feature the README does not mention.
- **TILING opens on W15** — the 316 px outlier, its own worst window, with the metric-limit
  explanation beside it. That is a deliberate and excellent choice.

**Console and network.** After the full walk: page 1 had **one** console error on first load —
`GET http://127.0.0.1:8000/favicon.ico [404]`. The static path logs the expected
`api/health` 404 plus Chrome's quirks-mode warning. No other errors, no other 404s. The page does
fetch **Google Fonts and `cdnjs.cloudflare.com/…/three.min.js`** — confirmed by
`list_network_requests` (reqids 57–65).

**Terminology chips.** Nine of ten pairings agree with Invariant 2 and with each other. One does
not — see BLOCKER B2 and B3 below.

### 3c. The live bay, end to end

`api/health` → `{"ok":true,"service":"lunaxx-console","commit":"f052202","max_bytes":67108864,…}`.
LIVE bay present on :8000, absent on :8011 and `file://`. Confirmed both ways.

**The real pair, through the browser's own file inputs** (`data/pairs/site_ohrc_m1153871873le_w02/`):

| | live run, in the browser | `REPORT.md` line 22 |
|---|---|---|
| verdict | ALIGNMENT ACCEPTED | agrees |
| matches | **5,112** | **5112** |
| verified cells | **56 of 64** | **56 / 2** |
| inliers | 4,630 | 4,680 (−1.1 %) |
| time | **7.9 s wall, 6.6 s inside `run_all`** | — |

The 1.1 % inlier drift is MAGSAC++'s random sampling and is exactly the range `web/README.md` §7
already documents. **This works, and it is the answer to "are these replayed?".**

**Breaking it the way a judge will — the flagship 52.8 MB pair (`sac_ohrc_nac_w06`):**

- The browser sat for **~2.6 s**, then the status line printed **`Failed to fetch`** — the raw
  JavaScript `TypeError`. No mention of a size, a cap, or what to do next.
- Network: `POST /api/register` → **`net::ERR_CONNECTION_RESET`**.
- Cause: `web/server.py:205` returns a perfectly good `413 {"error": "body must be 1..67108864
  bytes, got N"}` — but it replies **without draining the request body**, so the client's remaining
  upload hits a closed socket and the browser never sees the JSON.
- **And the panel below still showed the previous run's green `ALIGNMENT ACCEPTED · 56 of 64 cells
  verified · 4,630 inliers of 5,112 matches`, under the sentence "This ran just now, on this
  machine."** That sentence was, at that moment, false.

The same staleness happens on the success path: while a new run is in flight (status `RUNNING —
matching, this is the slow part`) the old verdict stays on screen unchanged. See BLOCKER B4.

**Two PNGs with no ground scale.** The panel says so, at length and correctly:

> "Scale: gsd_mpp unknown for source and reference; images NOT resampled… **Neither upload carried
> a ground scale, so the common-scale step had nothing to bridge and both images were taken to be
> at the same scale already. Upload GeoTIFFs to exercise scale invariance.**"

It does **not** quietly assume 1:1. The run itself behaved correctly — a deliberately mis-scaled
pair produced 6,047 matches but only 10 inliers, the area check contradicted it, and the system
REFUSED and declared the fallback. That is a good live demo moment. Two nits: a doubled full stop
(`from the catalogue..`) and a NAC-EDR-specific hint shown for a PNG upload. **It took 118.7 s**
(118.2 s in `run_all`) — twice `web/README.md`'s "~20–60 s" and twice Known issue 12's "48–61 s".

**Same image twice** → 64/64 verified, 5,776 inliers of 5,776 matches, 100 % agree, 6.0 s. Correct.
**A non-image** → clean client-side refusal: `notanimage.txt: need one of .img, .jpeg, .jpg, .lbl,
.png, .tif, .tiff, .xml`. (The page already knows how to write a good error; the 64 MB case just
isn't covered.) **Nothing uploaded** → `REGISTER THE PAIR` is `disabled`.

### 3d. Streamlit — what Gate 4 tests

`python -m pytest -q` → **340 passed in 14.12 s, exit 0.**

| | measured |
|---|---|
| server up | ~1 s from launch to HTTP 200 |
| first render | ~0.5 s |
| align **from cache** | **0.47 s** |
| align **live**, three consecutive runs | **6.8 s / 6.1 s / 6.5 s wall** — identical results each time (5,185 matches, 63/64 verified, AGREES) |

The default pair is `pair_01`, CH2_OHRC vs CH2_OHRC, and the sidebar warns unprompted: *"Same
instrument on both sides — this is **not** a cross-sensor result, whatever else it shows."* The
header names the grid: `REFERENCE GRID 0.2298 m/px (catalogue)`. The metrics panel says
`rmse_gt_px  n/a - no ground truth on a real pair` and `held-out fit residual, not an accuracy`,
and warns `SCALE FROM THE CATALOGUE, NOT THE LABEL`. This is disciplined work.

**Deliverables.** All four buttons exist. `deliverables.zip` downloaded and opens clean
(`testzip()` → `None`), containing seven files: `matches.csv` (319,041 B), `registered_product.tif`
(1,638,672 B), `registered_product.json`, `matches_isis.csv` (365,579 B), `trust_map.csv`,
`report.json`, `report.md`.

The exported GeoTIFF for `pair_01` carries **no geotransform** — no `ModelPixelScaleTag`, no
`ModelTiepointTag`, no `GeoKeyDirectoryTag` — and its sidecar says why, plainly:

```json
{"frame": "reference image pixels (no map transform in the reference)",
 "transform": null, "crs": null,
 "convention": "row/column of the reference image; pixel centre of (0,0) is the top-left pixel"}
```

That is honest and correct — `pair_01_ref.tif` has no map transform to inherit. But a judge who
clicks "Registered product (GeoTIFF)" on the **default** pair and opens it in QGIS gets an
ungeoreferenced raster, and the explanation is in a JSON file beside it. Demo on a pair that has a
grid, or say the sentence out loud.

**I could not confirm the 2nd–4th download buttons land.** After the zip, further scripted clicks
produced no file (Chrome suppresses repeated automatic downloads). A human click may get Chrome's
"allow multiple downloads?" prompt instead of silence — but either way, **the demo script should
say "click the zip; the other three are inside it."**

**Offline.** I did **not** physically switch the wifi off — that is a machine-wide change with no
upside here, and the repo already contains a stricter test. `core/bench_loftr_cpu.no_network()`
replaces `socket.socket` with a raiser. I ran the real demo path inside it:

```
OFFLINE GUARD PASSED - run_all completed in 6.4 s with socket.socket blocked
  verdict          : agrees
  note             : 98% of 64 measurable cells agree with H -> agrees
  matches / inliers: 5185 / 5183
  declared method  : loftr+magsac++
```

**Zero sockets opened on the Python demo path.** The match count (5,185) is identical to the
Streamlit live run, so it is the same computation.

**What offline costs the browser page.** I rebuilt the page in my scratchpad with the two CDN hosts
rewritten to a closed port (same bytes otherwise, wrapped in `server.py`'s own `SKELETON`) and
served it. Result: **it degrades honestly.** `window.THREE` is `undefined`, the 3D stage falls back
to `init2D()`, and the caption **changes itself** to `LOLA 60 m · 21.84 km square · relief 3,152 m ·
hillshade (no WebGL in this viewer)`. Fonts fall back through the declared stack to Arial Narrow and
still look intentional. Every chart, table, trust map and layer button still works — they are all
inline. Screenshot taken. **Nothing looks broken; one feature announces that it is missing.**

### 3e. The room a judge will be in

| Condition | Result |
|---|---|
| Phone 393×852 | Clean. `scrollWidth == clientWidth == 394`, no horizontal page overflow. Nav scrolls sideways by design; `.ledger` tables sit in their own `overflow-x:auto` wrappers. Body 16 px, h1 40 px — readable, not zoomed to 40 % |
| Projector 1366×768 | Clean. `scrollWidth 1351`, nothing clipped. The whole REFUSALS bay — header, seven rows, all three columns including COUNT — fits on **one** screen |
| Slow 3G | **first-contentful-paint 2,480 ms**; DOMContentLoaded **44,197 ms**; 2,098,968 bytes transferred. The hero paints and reads fine at ~2.5 s; charts and the trust map wait for the 44 s mark. Fonts and three.js came from cache in my run, so a cold judge is worse |
| `lighthouse_audit` snapshot, desktop | **Accessibility 99 · Best Practices 100 · SEO 80 · Agentic Browsing 100.** 38 passed, 2 failed: `heading-order` (one `<h4>` out of sequence) and `meta-description` (absent) |

One cosmetic during the 44 s: the provenance sentence renders as *"read back from the evidence logs
at commit  , the same commit the submitted deck quotes"* — with an empty sha — and the header shows
`EVIDENCE FROZEN ·` with nothing after it. Both are JS-filled.

### 3f. What I could not check, and why

- **The published artifact's rendering.** The MCP Chrome is not signed into claude.ai and the
  navigation stopped on a Cloudflare "Performing security verification" interstitial that never
  cleared (Ray IDs `a3e171af2ac93c0c`, `a3e174c9bd4e3c0c`). Known issue 23, still true. I graded
  the same bytes as served by `web/server.py`, whose `SKELETON` comment states it reproduces the
  Artifact runtime's wrapper — so the rendering should match, but **should is not verified**.
- **Whether the artifact is shared.** `Artifact list` confirms it exists and is yours, updated
  2026-09-20. It does not report share state. **Samartha must open the Share menu and look.**
- The `python -m web.server` stdout log was zero bytes under redirection (block buffering), so I
  have no server-side log of the failed upload — only the browser's `ERR_CONNECTION_RESET`.

---

## 4. Judge A's interrogation

### 4.1 Every number on screen, against `REPORT.md`

**No invented numbers. Every figure I checked traces to `REPORT.md` at the freeze.**

| On screen | In `REPORT.md` |
|---|---|
| SUN bins: 16/14/12/7/5/15 windows, 6/5/4/3/2/5 frames, medians 4818/4247/559/58/8/209 | lines 253–260, cell for cell |
| CAL near-Sun: 0 %, 0 %, 0 %, 74.4 %, 100 %×6; 44 trials at 0 m | lines 306–318 |
| CAL SAC: 0 %, 0 %, 4.7 %, 12.5 %, 84.4 %, 100 %; 16 trials at 0 m | lines 324–331 |
| 94.1 % (19,653 of 20,896) and 87.4 % (19,635 of 22,464) | line 357, verbatim |
| 0.086 px = 5.1 m, exact truth, 60 m grid | line 382 |
| 0.086 px = 0.107 m, 6 loops | line 385 |
| 37/37 over 13.1 km², 0.61 px = 0.57 m on the 0.93 m grid | line 40 ("0.931 m grid") |
| 160 distinct ground windows | line 406 |
| 8.2 s median per 640-px window | line 390 |
| live run: 5,112 matches, 56 verified, agrees | line 22 |

### 4.2 Pixel grids and held-out numbers

Both hero tiles name their grid and their kind of claim — "held-out median on the 0.93 m grid" and
"against exact truth (synthetic, 60 m grid)". The RESULTS footnote states the distinction in full
and says the two "are different claims and are never added together". The trust-map panels all name
the grid. The Streamlit metrics panel says `n/a - no ground truth on a real pair` outright.

**One exception, and it is the one a reader will trip on.** The RESULTS row

> `OHRC → NAC A → NAC B, closed loops … 6 loops close to 0.086 px = 0.107 m`

names **no grid** (`REPORT.md` line 385 names it: 1.245 m, NAC B), and it sits directly above a
footnote reading "0.086 px = 5.1 m on the 60 m grid". The same number, two metre values, one grid
named. Also: the `Kaguya TC → MI 1548 nm` RESULTS row gives "0.23–1.09 px" with no grid, while the
REFUSALS row for the same pair does say "on MI's 14.8 m grid".

### 4.3 Best case where a range is honest; is REFUSALS buried?

Ranges are used where ranges exist: "6 / 6 accepted 0.69–1.68 px", "3 / 3 accepted 0.23–0.47 px",
"3.4 to 16.2 m". The TILING bay **opens on its own worst window** and explains the 316 px outlier
rather than averaging it away. This is better discipline than I expected.

**Prominence:** RESULTS is at `offsetTop 6042`, REFUSALS at **6998**, on a 7,877 px page. The
refusals table is the **last** thing before the footer. It has an equally large header and equally
strong copy ("A registration engine earns trust by the results it refuses… none was discovered by a
reviewer, because the system flagged each one itself") — but you have to scroll 7,000 px to read it.
The hero headline carries the idea; the evidence for it is at the bottom.

### 4.4 The six questions a SAC scientist asks in the first ninety seconds

| # | Question | Answerable from the screen? | In `ops/QA_ANSWERS.md`? |
|---|---|---|---|
| 1 | **"What is your reference grid?"** | **Yes.** Every panel, every table row, the Streamlit header. | Implicit only — not its own entry |
| 2 | **"Is that an accuracy or a residual?"** | **Yes.** RESULTS footnote and the Streamlit metrics table both say it outright. | Yes — §8 and the sub-pixel answer |
| 3 | **"Isn't this just the RANSAC inlier ratio with a colour map?"** | **Partly.** The flow diagram says "never uses match positions"; the panel says "an independent area check that never sees the matches". The *proof* (a pair with 0.00 px inlier residual and every match wrong) is not on screen. | **Yes, and it is the best answer in the file.** Say it out loud |
| 4 | **"You call NAC↔NAC a result. Is that cross-sensor?"** | **Yes, pre-empted.** The pairing's own text says "We label this same sensor and never count it as cross-sensor evidence". The footer publishes the rule. | Yes — §1 |
| 5 | **"You say 0 of 64 verified and 59 no evidence, then 51 measurable cells. Which is it?"** | **No — and this is the weak point.** See B5. | No |
| 6 | **"A competitor registers OHRC↔TMC-2 across 8 regions. You refuse all 4. Why?"** | **Partly.** The panel gives the reason (Sun azimuths 120°, incidence 59° apart) and names the fix (one TMC-2 pass ~9° away). | **No.** The operator must say it |

`ops/QA_ANSWERS.md` is dated 5 Sep and is a college-round document. It is still strong — the
"what does verified actually promise" and "why cells, not one whole-frame correlation" answers are
finale-grade. It contains **nothing** about the Mission Console, the TMC-2 refusal, or the
measurable-cells ambiguity.

### 4.5 The most attackable claim on screen, and our answer

**The attack.** *"Your footer says 'Cross-sensor means different instruments.' Your refusals table
calls OHRC → TMC-2 cross-sensor. Your trust map calls the same pair same mission. Your IIRS pair is
chipped multi-modal and its own band label says 'visible/near-visible'. If the terminology moves
around inside one page, why should I trust the numbers it labels?"*

That is the whole audit in one question, and it is available in ninety seconds to anyone who reads
two bays and the footer. **It costs two token edits to make it impossible to ask.**

**Our answer, once fixed.** "Different instruments, same spacecraft — the page now says both, and
`REPORT.md` line 145 says 'both panchromatic, NOT multi-modal; same mission, NOT cross-mission'. The
IIRS band is 998.8 nm, which our cutter's `>= 1000 nm` rule rounded into the wrong bucket; the label
now reads near-infrared and the chip is unchanged. Neither touches a measured value."

**Answer today, unfixed:** an apology. Do not go into the room with this.

---

## 5. The field — are we actually different?

Base: `ops/national_round/RESEARCH_REPORT.md` (18 Sep). Refreshed with **3 web fetches** of the
allowed 10.

- Public GitHub repos under the exact PS ID: **36 today**, 37 on 18 Sep. Field size unchanged.
- The one repo with any traction — `Fable98/chandrayaan2-crossmatch`, **4 stars**, pushed 20 Sep,
  55 MB — I read its README in full.

### What we can show that a strong competitor cannot

| | Meets a judge in 4 min? |
|---|---|
| **A check that never sees the matches.** Every one of the competitor's four "Quality Gates" is computed *from the match set* — count, RANSAC consensus, condition number, inlier spread. All four would pass the case our own Q&A describes: median inlier residual 0.00 px, every match wrong. | **No.** It is one clause in the hero paragraph |
| **A calibration curve in metres.** 0 % flagged at ≤2 m, 74.4 % at 3 m, 100 % from 5 m, with **0/44 and 0/16 false alarms**, from 3,060 planted-error trials. They publish thresholds; they publish no detection floor and no false-alarm rate. | Only on deck slide 5 and if they scroll to CALIBRATION |
| **Held-out validation at scale.** Ours: 4,000–5,000 inliers per window, held-out median on a named grid. Theirs, verbatim: *"In-Sample Fit only… sub-pixel_accurate=true in 2/3 regions"* on **5–6 inlier sets**, and `insufficient_points_for_holdout` when inliers < 8. | No |
| **Spatial support.** Ours: 58/64 and 61/64 cells verified, coverage 1.00. Theirs: **5–7 % of a 10×10 grid** (5–7 inliers). Two orders of magnitude. | No |
| **SAC's own benchmark pair**, registered, with held-out error beside their in-sample RMSE. | Deck slide 2, yes |
| **MiLOI network truth** — 81 published pairs, 33/33 accepted are correct, judged against other pairs. | No |
| **Live registration in front of the judge**, 7.9 s, same renderer as the frozen panels. | Finale room only |

### What a strong competitor can show that we cannot

| | Why it hurts |
|---|---|
| **OHRC ↔ TMC-2 registering, 8 flight regions, fit RMSE 0.99–1.83 px.** | The PS title names TMC. We refuse 4 of 4. To a generalist, they did it and we didn't |
| **An IIRS product** via chained homography through TMC-2 (`H_OHRC→IIRS = H_TMC→IIRS · H_OHRC→TMC`), explicitly avoiding direct 275–320× matching. | We attempt TC→IIRS directly at 12× and refuse 10/11. Their *method* — chain through an intermediate scale — is our own open gap 9 ("no pyramid for 18–285×") |
| **`scripts/isro_official_evaluator.py --input_dir --output_dir --use_dem`** emitting `isro_evaluation_summary.json`. | If the finale has a standard evaluation contract, they are conformant and we are not. Worth finding out |
| **Their own "mission console"** — Next.js + FastAPI, ports 3000/8000. | A dark instrument panel is not, by itself, a differentiator |
| **"Quality Gates that fail cleanly"** and `not_available` / `not_run` reporting. | **Honest failure reporting is no longer ours alone.** `RESEARCH_REPORT.md` gap 6 predicted this on 18 Sep; it is now confirmed and sharper |
| SuperGlue / LoFTR / ISIS / ASP / commercial tooling. | Published SOTA out-registers us on easy pairs. Our answer is licensing (SuperPoint is non-commercial) and that we measure trust, not just accuracy |

### Is the differentiator visible, or is it buried?

**Half-visible, and the half that is visible is no longer unique.**

The hero headline — "knows when it is wrong" — lands in one second, and a competitor can now say
the same sentence. What actually separates us is two clauses further in: **the check is independent
of the matches, and it is calibrated in metres against planted errors.** Neither is on the first
screen in a form a four-minute reader will retain, and neither is on the deck's first screen at all.
The evidence (REFUSALS) is 7,000 px down.

**This is a HIGH finding on its own.** The fix is wording, not work: put "the check never sees the
matches" and "0/44 false alarms, 100 % flagged from 5 m" **in the hero stat strip**, where the six
tiles already are, and on the deck's strongest line.

---

## 6. The grade

### Per artefact

| Artefact | Grade | The evidence that fixes it there | The one change that moves it up |
|---|---|---|---|
| **1. Six-slide PDF** | **Above average** | A flow diagram (13/13 shortlisted decks have one) · measured results from its own work (only 1–2/13 have them) · correct terminology throughout, verified against extracted text · honest negatives on every slide. Held down by: **0 hyperlinks**, 90 numeric tokens crammed into five slides, and slides 2/4/5 at text capacity | **Put a reachable URL on slide 6** (it has the room) and move one refusal claim into the biggest type on slide 2 |
| **2. Mission Console, published** | **Above average** — *content graded via the identical bytes on :8000; the live artifact render is unverified (§3f)* | Every number traces to `REPORT.md` · all 10 pairings and 3 verdicts drive correctly · refused pairs show the rejected warp · offline degrades honestly · Lighthouse a11y 99 / BP 100 · phone and projector clean. Held down by **exactly two terminology defects** (B2, B3) and the measurable-cells ambiguity (B5) | **Fix B2 and B3 — two tokens — and it is High grade.** Then share it |
| **3. Mission Console, live** | **High grade** | The LIVE bay registers a judge's own pair in 7.9 s through the browser's own file inputs, returns 5,112 matches and 56/64 verified against `REPORT.md`'s 5112 and 56, and is drawn by the same renderer as the frozen panels. That is the complete answer to "is this replayed?" | Fix B4 (stale panel + the 64 MB message) so a failure looks like a failure |
| **4. Streamlit app** | **Above average** | 340 tests green, 0.47 s from cache, 6.1–6.8 s live, three identical consecutive runs, four deliverables, zero sockets on the demo path, and unprompted honesty about same-sensor pairs and catalogue scale. Held down by: a plain light-theme UI next to the console's, the false-alarm staleness plate in the header band (Known issue 25), and a no-geotransform GeoTIFF on the default pair | Re-run `precompute_demo_cache` on the final commit, and demo a pair that has a grid |
| **5. Explainer video** | **Below average** *as a judge-facing artefact* | Built and technically clean — 1600×1000 h264, 12 fps, 108.08 s, 1,297 frames, 7,997,862 bytes — but it has **no audio stream at all**, it is published nowhere, and its script does not fit its picture (M3) | Cut the narration to ~260 words or stretch the picture, voice it with an offline TTS, and publish it |

### Overall: **Above average**

Not High, for one reason: the ladder's top rung requires that *a judge would ask who built it*, and
the only artefact a judge is guaranteed to meet is a PDF with no way out of itself. The work behind
it is High grade — I could not find a fabricated number anywhere, the live demo is real, and the
refusals are reported as results. **The submission is graded on the PDF, and the PDF is the weakest
thing here.**

Not Below average: nothing is visibly broken on the paths a judge takes, and no claim I tested is
falsifiable. The two terminology defects are the nearest thing, and they are contradictions between
labels, not false measurements.

### Would Judge A be pleased, or merely satisfied?

**Pleased — then annoyed, in that order.** Pleased by: the TILING bay opening on its own worst
window; "0 of 64 cells verified" printed as a headline; the 749 nm control for the 1548 nm pair
(that is a real experiment, not a demo); the declared fallback with its disagreement in metres; the
footer publishing the terminology rule; `residual_px` explicitly disowned. Annoyed by: the
OHRC→TMC-2 chip disagreement, the "visible/near-visible" label on the multi-modal pair, and the
"51 measurable cells / 59 no evidence" line. **What moves them from pleased to convinced:** register
the closer-Sun TMC-2 pass, or say out loud that a second refusal there is also a publishable result.

### Would Judge B understand it?

**Yes — until the second bullet of deck slide 2.** They get "aligns Moon pictures and says when it
can't" from the headline and the two trust maps. They lose it at *"An independent area check, blind
to match positions, cross-correlates the warped image with the reference in 8×8 cells: agrees,
unconfirmed, or contradicted, which falls back."* Three technical terms in one sentence, before any
of them has been anchored. On the console they get considerably further, because the hero paragraph
does the same job in plainer words and the pictures arrive before the vocabulary.

### Does every feature actually work end to end today?

| Feature | Works | How I verified | What a judge sees if it fails |
|---|---|---|---|
| Six-slide PDF renders, 6 pages | **Yes** | pymupdf, all 6 pages → PNG, read by eye. 1,112,713 B | — |
| PDF links to anything | **No** | 0 link annotations, all pages | They never leave the PDF |
| Console: all 10 pairings, 3 verdicts | **Yes** | clicked all 10, distinct hashes and panels | — |
| Console: refused pair shows the rejected warp | **Yes** | hash of `warp` ≠ hash of `fb` on all 5 refusals | Teaches the opposite of the truth |
| Console: Sun slider ↔ table ↔ scatter ↔ 3D | **Yes** | 19 stops incl. both ends, all agree, = `REPORT.md` | — |
| Console: TILING window map, 37 clickable | **Yes** | clicked 3, panel followed | — |
| Console: terminology chips | **Partly** | 9/10 consistent; OHRC→TMC-2 disagrees across bays | The claim that discredits the rest |
| Console served from `web/dist` directly | **No** | quirks mode, windows-1252, 60 mojibake, hidden layer paints | The README's own instructions produce a broken page |
| Console offline (no CDN) | **Yes, honestly degraded** | THREE undefined → 2D hillshade, caption says so | — |
| LIVE bay: register a real pair | **Yes** | 7.9 s, matches `REPORT.md` | — |
| LIVE bay: oversize upload | **No** | `ERR_CONNECTION_RESET` → "Failed to fetch", stale success panel | A green ACCEPTED panel under a failed run |
| LIVE bay: scale-less PNG | **Yes** | panel states the assumption explicitly | — |
| LIVE bay: bad / missing input | **Yes** | clear message; button disabled | — |
| Streamlit: align from cache | **Yes** | 0.47 s | — |
| Streamlit: align live ×3 | **Yes** | 6.8 / 6.1 / 6.5 s, identical results | — |
| Streamlit: four deliverables | **Partly** | zip verified and opens; buttons 2–4 unconfirmed (§3d) | Three buttons that appear to do nothing |
| Streamlit: GeoTIFF geotransform | **Honest n/a on the default pair** | no Geo tags; sidecar says why | An ungeoreferenced raster in QGIS |
| Offline: Python demo path | **Yes** | `run_all` in 6.4 s with `socket.socket` blocked | — |
| Test suite | **Yes** | 340 passed in 14.12 s, exit 0 | — |
| Explainer video | **Partly** | 108.08 s, no audio stream, unpublished | — |
| Narration fits the video | **No** | 790 spoken words ≈ 327 s at 145 wpm vs 108 s of picture | A voice-over 3× too long |
| Published artifact renders | **Unverified** | Cloudflare interstitial, Known issue 23 | Unknown — check it by hand |
| Published artifact is shareable | **Unverified** | listing does not report share state | A dead link on slide 6 |

---

## 7. What to change

Ranked by shortlist impact × confidence ÷ effort. **None of the "before 25 Sep" items touches
`core/`, `evaluation/`, `ops/`, `app/` or `baselines/`, so none of them re-freezes anything.**

### Before Fri 25 Sep 22:00 — deck and portal freeze

| # | Finding | Fix | Hours | Risk | Verify by |
|---|---|---|---|---|---|
| **B1** | **A PDF-only judge reaches nothing.** 0 link annotations; repo private; artifact private; no link field on the portal | Decide the route (see below), then: one line on slide 6 + the same URL in the long idea description | **1.5–2.5** incl. the deck rebuild and re-export | Medium — touches the deck, so `AUDIT: clean` and `PDF CHECK: clean` must both pass again, and Known issue 17 (intermittent "NO PDF") applies | `python -m presentation.export_pdf` prints `PDF CHECK: clean`; render page 6 and click the link from a logged-out browser |
| **B2** | **Same pair, two chips.** `web/build_console.py:93` tags `sac_ohrc_tmc_w01` **SAME MISSION**; `web/console.template.html:429` tags the same pair **CROSS-SENSOR**. The footer publishes "Cross-sensor means different instruments" | Make them agree. **Recommended: both `SAME MISSION`**, matching `REPORT.md:145` ("same mission - NOT cross-mission"). Alternative `CROSS-SENSOR · SAME MISSION` is true on both axes but adds a fourth chip form | **0.25** | Very low | `python -m web.build_console`, then grep the built page for `TMC-2 at SAC` and read both chips |
| **B3** | **Multi-modal pair labelled "visible/near-visible".** `Kaguya TC → Chandrayaan-2 IIRS` is chipped MULTI-MODAL while its B side reads `998.8 nm (visible/near-visible)` — the same descriptor carried by MI 749 nm, which is chipped CROSS-SENSOR. Root cause: `ops/cut_site_pairs.py:356` uses `nm >= 1000`; 998.8 misses by 1.2 nm | **Override the displayed band in `web/build_console.py`'s `side()`** (or in the ROSTER entry) to `998.8 nm (near-infrared)`. **Do NOT fix `ops/cut_site_pairs.py` — that is inside the freeze path and would cost 90–110 min. RE-FREEZE if done there.** Queue the real fix with F18/F19 | **0.25** | Very low in `web/`; **RE-FREEZE** if touched in `ops/` | Rebuild, open the IIRS pairing, read the B side |
| **B4** | **A failed live run leaves the previous run's green ACCEPTED panel saying "This ran just now."** Verified with the 52.8 MB flagship pair | Three parts: (a) clear the result panel on submit; (b) pre-check `fileA.size + fileB.size` against `api/health`'s `max_bytes` × 3/4 in the page and refuse with a real sentence; (c) in `web/server.py`, drain `self.rfile` before the 413 so the browser sees it | **1.0** — `web/` only | Low | Upload `sac_ohrc_nac_w06`: the panel must clear and the message must name the cap and what to do |
| **B5** | **Two meanings of "measurable cells" in one panel.** "0 of 64 verified, 5 weak, 59 no evidence" beside "16 % of 51 measurable cells agree with H". `core/reliability.py:365` counts cells with finite `area_ncc`; the state tally counts cells with enough inliers | Wording only, in `web/panel.py` / the template: call the verdict line **"51 cells the area check could measure"** and the tally **"cells with match evidence"**, and add one clause saying they are different tests | **0.5** | Low — no value changes | Open the 1548 nm pairing and read the two lines in sequence |
| **H1** | **`web/README.md` §1 tells the operator to open a page that breaks.** Static/`file://` → quirks mode, windows-1252, 60 mojibake, a hidden trust-map layer paints over the visible one | Cheapest: rewrite README §1 to say "serve it with `python -m web.server`; the file in `dist/` is a fragment". Better: have `build_console.py` also write `dist/index.html` = SKELETON + fragment, so the static path is correct too | **0.5** (README) / **1.0** (both) | Low | Serve `dist/` with `python -m http.server` and re-run the `compat / charset / mojibake / viewport` probe |
| **H3** | **The differentiator is not unique and is not on the first screen.** A competitor ships "Quality Gates that fail cleanly" | Two hero stat tiles: **"never sees the matches"** and **"0/44 · 0/16 false alarms · 100 % flagged from 5 m"**. Same on the deck's strongest line | **0.5** console, **+1.0** if the deck changes | Low in `web/`; deck change re-triggers the audit | Read the first screen and ask what is unusual |
| **M7** | Known issue 25 confirmed **in the Streamlit header band**: `CACHED RESULT commit f928995 — CODE IS NOW f052202` | Run the 30 s command in Known issue 25 on the **final** commit. A live run also clears it — verified | **0.1** | None | The plate disappears |
| **M2** | Sub-pixel without a grid in RESULTS (closed loops; 1548 nm row) | Add "on the 1.245 m NAC grid" and "on MI's 14.8 m grid" to those two rows | **0.25** | None | Read the RESULTS table |
| **M6** | Only the first download button fires per session | One line in the demo script: "click the zip; the other three are inside it" | **0.05** | None | — |
| **M1** | `failed, and NOT caught: 0` is a hardcoded literal, identical in all six bands | Read it from the bin's outcome dict, or label it "no band has one" so it reads as a statement, not a measurement | **0.25** | None — all six are genuinely 0 in `REPORT.md` | — |

**On B1 — which route.** Ranked:

1. **Make the GitHub repo public and put that URL on slide 6.** One click, no login for the judge,
   no Cloudflare, no expiry, and it carries `REPORT.md`, the deck and `web/` in one place. It also
   answers "did you actually build this?" better than any screenshot. Cost: a pass for secrets and
   for anything in `data/` you do not want public. **This is my recommendation.**
2. **Share the artifact and link it.** Zero build cost, but it is a claude.ai URL, it may ask the
   judge to sign in, and you cannot verify the render from here (§3f).
3. **Publish the video** (needs M3 first) and link that.
4. **Do nothing and add a console screenshot to slide 6 instead.** Weakest, but strictly better than
   the empty third of the slide, and it costs one image.

Do **1**, and if time allows, **1 + 3**.

### Before the finale — larger work, may touch code

| # | Item | Hours | Why |
|---|---|---|---|
| **M3** | **The narration does not fit the cut.** Beat headings sum to exactly 108.0 s; the spoken words sum to **790**, which is **327 s at 145 wpm** — 3.0× over. Per beat: "calibration — 8 s" carries 72 words (30 s); "close — 5 s" carries 130 | 2–3 | Either cut to ~260 words or re-time `web/film.py`'s beats. Do this **before** any TTS run, or you will voice a script that cannot be laid down |
| **M4** | Voice the video **without waiting for a Gemini key** — `edge-tts` or Piper runs offline, no key, no account | 1–2 | `web/voice.py` has never made a live call (Known issue 24). An offline TTS removes the dependency entirely and keeps the demo path offline |
| — | **TMC-2 closer-Sun pass** (`ops/specs/day_24.md`), decide by Wed 23 Sep | ~2 + download | The competitor's headline is OHRC↔TMC-2. This is the one measurable answer. **A second refusal is also publishable — say so on the slide either way** |
| — | **Chain through an intermediate scale for IIRS** (`H_TC→IIRS = H_TC→X · H_X→IIRS`), i.e. the competitor's method and your own open gap 9 | days | Turns a limit into a product. December work, not submission work |
| — | **Check whether a standard ISRO evaluation input/output contract exists** for this PS | 1 | A competitor ships `isro_official_evaluator.py`. If a contract exists and we do not meet it, that is a finale scoring gap |
| — | F18, F19, and `core/export._commit` returning HEAD instead of the last touching commit | 2–3 | Already queued in STATUS for after 27 Sep. Correct call |
| **L1–L7** | favicon; nav order (LIVE is listed first but sits second, `offsetTop` 2004 vs 1102); empty sha during load; `heading-order` + `meta-description`; the doubled full stop and NAC-EDR hint in the scale message; the unqualified 8.2 s hero tile; identical truncated filenames in LIVE | 1 total | Cosmetic. Do them in one pass or not at all |

### Won't do, and why

- **Fix the band threshold in `ops/cut_site_pairs.py`.** Correct fix, wrong week — **RE-FREEZE**,
  90–110 min plus a full deck re-verification, four days out, to change a display string that
  `web/build_console.py` can override for free.
- **Re-cut the IIRS roster pair to an `iirs1555` window.** Also RE-FREEZE, and it needs a
  `precompute_demo_cache` run. The override achieves the same on screen.
- **Rebuild the Streamlit app to match the console's visual identity.** Real problem (M5), but it is
  the Gate-4 artefact and it passes 340 tests. Do not restyle a working demo in the last week.
- **Physically disable the wifi for the offline test.** The repo's own `no_network()` guard is
  strictly stronger and does not risk leaving the demo machine offline.
- **Ship a favicon just for the local server.** One 404, invisible next to everything else.

### Capability upgrades — things that raise the ceiling, not patch a defect

| Upgrade | What it buys | Setup cost | Before or after 27 Sep |
|---|---|---|---|
| **Make the repo public + GitHub Pages serving `SKELETON + fragment`** | Fixes B1 and H1 at once: a real, shareable, login-free URL that renders in standards mode, and a route to the code. Nothing else on this list buys two findings | 1–2 h incl. a secrets pass | **Before.** Highest-value item here |
| **An offline TTS (`edge-tts` or Piper) instead of the Gemini key** | Unblocks the video today, keeps the whole demo path offline, removes Known issue 24 | 0.5–1 h | **Before**, but only after M3 |
| **`pypdfium2` or `pymupdf` in the venv** | Lets `presentation/export_pdf.py` verify **rendered pages** instead of text-box geometry — the real fix for Known issue 11. I had to install pymupdf into a scratch dir to read your own deck | 10 min | **After.** Don't touch the venv this week |
| **chrome-devtools MCP** | Already present, and it earned its place: the quirks-mode divergence, the hidden-layer paint, the stale LIVE panel and the `ERR_CONNECTION_RESET` are all things source-reading would have missed. Keep it for the finale rehearsal | 0 | Keep |

Deliberately **not** proposed: another dashboard, another evaluation framework, a vector store, or
any MCP that duplicates `ops.freeze` / `ops.make_report`. The repo's evidence pipeline is better
than anything I would bolt onto it.

---

## 8. The three things most likely to lose a finale place

**1. Nobody opens anything except the PDF.**
0 link annotations across 6 pages, repo private, artifact private, no link field on the portal. The
console is the best thing this team has made and it is currently invisible to the people scoring it.
A PDF-only judge sees 25 % of the artefacts and ~8 % of the figures. *Fix: B1, 1.5–2.5 h, this week.*

**2. A SAC judge finds the terminology moving inside one page.**
`OHRC → TMC-2` is **SAME MISSION** in the trust map and **CROSS-SENSOR** in the refusals table, on a
page whose footer publishes "Cross-sensor means different instruments". The IIRS pair is chipped
MULTI-MODAL with a band label reading "visible/near-visible". Nothing else I tested is falsifiable —
which is exactly why these two matter: they are the only handhold on an otherwise clean page, and
Invariant 2 says a terminology break discredits every number beside it. *Fix: B2 + B3, half an hour,
no re-freeze.*

**3. "They registered TMC-2 and IIRS. You refused both." **
The strongest visible competitor registers OHRC↔TMC-2 across 8 regions (0.99–1.83 px) and delivers
an IIRS overlay by chaining through TMC-2 — and also pitches clean failure reporting. To a
four-minute generalist, they delivered more and claim the same virtue. Our real advantage — a check
that never sees the matches, calibrated in metres, on 4,000-inlier windows against their 5–6 —
requires two more sentences than that judge will give us. *Fix: H3 wording now; the TMC-2 closer-Sun
pass by Wed 23 Sep; and rehearse the one-sentence version of "their gates all read the matches;
ours doesn't."*

---

### Appendix — verification environment

```
venv        C:\Users\samar\venvs\sih26166\Scripts\python.exe
HEAD        f052202   evidence frozen at 7dd4e5b
pytest      340 passed in 14.12 s (exit 0)
browser     chrome-devtools MCP, dedicated profile; rAF ~358 ms when not frontmost (Known issue 20)
servers     python -m web.server :8000 · python -m http.server :8011 over web/dist
            python -m http.server :8022 over a scratch copy with the CDN hosts blackholed
            streamlit run app/streamlit_app.py :8501
scratch     C:\Users\samar\AppData\Local\Temp\claude\…\scratchpad  (pymupdf installed with
            --target here only; the venv was not modified)
web fetches 3 of the 10 allowed
git status  unchanged apart from this report
```
