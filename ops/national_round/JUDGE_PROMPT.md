# SIH26166 — the judge's walk-through: inspect the demo, grade it, and say what to change

> Paste everything below the line into a **fresh** Claude Code session opened in
> `C:\Users\samar\OneDrive\Documents\SIH26166` (Opus, 1M context). Requires the
> **chrome-devtools** MCP server. Written 20 Sep 2026 at commit `f052202`.
>
> This is the *demo* audit. Its sibling `AUDIT_PROMPT.md` audits the **evidence and the deck**;
> run that one for numbers. This one asks a different question: **when a judge opens what we
> built, what actually happens, and is it good enough to win?**
>
> It is a **read-only inspection**. It writes exactly one file — its own report.

---

You are inspecting the SIH 2026 national-round submission of team **LunaXX**, problem statement
**SIH26166** (ISRO/SAC): *"Multi-modal, Sun angle and scale invariant image correspondence using
Chandrayaan-2 optical images (OHRC, TMC and IIRS)."*

You are not the team. You are two people in one session, and you must keep them separate,
because the project can pass one and fail the other:

- **Judge A — the SAC scientist.** Twenty years in lunar image processing. Has co-authored
  something close to arXiv:2509.04775. Reads a claim and immediately knows which word is doing
  the lying. Bored by dashboards, moved by an honest negative result. Will ask *"what is your
  reference grid?"* before *"what is your accuracy?"*
- **Judge B — the panel generalist.** Senior, technical, but not a remote-sensing person:
  a mentor, an industry jury member, an administrator. Gets about **four minutes**. Decides
  from the shape of the thing, not the arithmetic. Will not ask a clarifying question — will
  just quietly rank it.

Everything you conclude must be attributed to A, to B, or to both.

## 0. Ground rules

1. **Write nothing but your report.** Do not edit code, rebuild the deck, re-run `ops.freeze`,
   or run `ops.precompute_demo_cache`. If a fix is obvious, *describe* it; do not apply it.
   The evidence is frozen at `7dd4e5b` and a stray write costs 90–110 minutes to undo.
2. **No invented numbers.** Invariant 1 binds you too: a figure you quote must come from a
   command you ran, a file you read, or `REPORT.md`. Screenshots and tool output are evidence;
   your impression is not.
3. **Terminology (Invariant 2) is part of the grade.** *Cross-sensor* = different instruments.
   *Multi-modal* = visible ↔ infrared / radar / elevation. *Sub-pixel* always names its pixel
   grid and gives metres. NAC↔NAC and TMC-2 fore↔aft are **same sensor**. If the UI breaks this
   anywhere, that is a BLOCKER, not a nitpick — it is the one error that discredits every other
   number on the page.
4. **Read `ops/STATUS.md` "Known issues" first and do not re-report them.** They are known. Do
   report if one of them is *worse than recorded*, or if it is now judge-visible.
5. Environment: venv `C:\Users\samar\venvs\sih26166\Scripts\python.exe` (bare `python` has no
   numpy). `PYTHONIOENCODING=utf-8`. Data outside git at the path in `data_path.txt` (BOM —
   read with `utf-8-sig`). Run heavy jobs one at a time; commit charge sits at 40–50 of 53 GB.
6. `git status` before you start and before you finish. OneDrive has silently reverted files.

## 1. What you are inspecting

There are **four** artefacts a judge can meet, and they are not equally finished. Grade each,
then grade the whole:

| # | Artefact | How to open it | Who meets it |
|---|---|---|---|
| 1 | **The six-slide PDF** `presentation/SIH26166_LunaXX_deck.pdf` | render all 6 pages to PNG and look at them | **everyone — this is the only guaranteed contact** |
| 2 | **The Mission Console**, published (read-only) | `https://claude.ai/artifact/LbbZKdvnVYCCBbPjEBZCA9` | only if the link reaches them AND is shared |
| 3 | **The Mission Console, live** | `python -m web.server` → `http://127.0.0.1:8000` | finale room only |
| 4 | **The Streamlit app** (what Gate 4 tests) | `streamlit run app/streamlit_app.py` | finale room only |

Plus `web/dist/mission-console.mp4` (built, **silent**) and `web/narration.md` (script, unvoiced).

**Before anything else, establish the reachability chain**, because a perfect demo nobody can
open scores zero:

- Does the PDF contain a link to 2, 3, 4 or the video? Grep `presentation/build_deck.py` and
  read the rendered slide 6.
- Is the artifact shared or private? Is the repo public or private?
- If a judge reads only the PDF, what fraction of the work can they see? State that as a number.

## 2. The four-minute pass — Judge B, first

Do this **before** you read any documentation, and do not let what you already know leak in.
Open artefact 1, then artefact 2, and give each the time it would really get.

Then answer, in Judge B's voice:

- What is this, in one sentence, from the screen alone?
- What is the one thing it does that is unusual? Did the page say so, or did you infer it?
- Is there **one image** that proves the idea without a caption? Name it or say there isn't.
- Where did your eye go first, and was that the right place?
- Count the numbers on the first screen. Does the density help or bury?
- At four minutes, do you rank this in the top 5 of a 40-entry pile? Say yes or no and why.

## 3. Drive it — the inspection proper

Use the **chrome-devtools** MCP. Do not settle for reading the source: the page has been wrong
in ways the source looked right about.

### 3a. Serve it three ways and compare

The built page in `web/dist/` is a **fragment**; `web/server.py` and the Artifact runtime each
wrap it in a document. So the same file renders differently depending on how it is opened.
Check all three and report any divergence:

1. `python -m web.server` → `http://127.0.0.1:8000/`
2. a plain static server over `web/dist/` (`python -m http.server`) — *this is the path
   `web/README.md` §1 tells an operator to take*
3. `file:///…/web/dist/mission-console.html`

For each, evaluate in the page:

```js
({ doctype: !!document.doctype, compat: document.compatMode,
   charset: document.characterSet,
   viewport: !!document.querySelector('meta[name=viewport]'),
   mojibake: (document.body.innerText.match(/Â|â€|Ã/g)||[]).length,
   layoutWidth: window.innerWidth })
```

`compat` must be `CSS1Compat`, `mojibake` must be `0`, `layoutWidth` must track the device.

### 3b. Every bay, every control

Walk `SUN · TRUST MAP · TILING · CALIBRATION · PIPELINE · RESULTS · REFUSALS`. For each:

- Does every control respond, and does the panel beside it change to match?
- Drag the Sun slider across its full range. Does the count table, the scatter highlight and
  the 3D relief all agree at every stop, including the ends?
- In TRUST MAP, click **all ten pairings** and, on each, open `MATCHER'S ANSWER`. On a refused
  pair it must show the **rejected** warp, never the fallback that rescued it. Showing the
  fallback under a REFUSED banner teaches the opposite of the truth — this bug has shipped once.
- Does any pairing display the previous pairing's verdict? (Also shipped once.)
- Check the terminology chip on every pairing against Invariant 2 **and against the same pair's
  chip in the RESULTS and REFUSALS tables**. They must not disagree with each other.
- `list_console_messages` and `list_network_requests` after each bay. Any error, any 404 that
  is not `api/health` on the static path, is a finding.

### 3c. The live bay, end to end

Start `python -m web.server`. Then:

- Confirm the LIVE bay appears, and confirm it stays **hidden** on the static/published path.
- Register a real pair through the **browser's own file inputs** (not curl). Use
  `data/pairs/site_ohrc_m1153871873le_w02/`. Time it. Compare the verdict, match count and
  verified-cell count against `REPORT.md`. Inlier counts drift ~1 % run to run (MAGSAC++
  samples randomly) — that is expected; anything else is not.
- **Then try to break it the way a judge will.** Upload the flagship roster pair
  `data/pairs/sac_ohrc_nac_w06/` (55 MB source). The payload is JSON+base64, so raw bytes
  inflate by 4/3 against a 64 MB server cap. Report exactly what the operator sees, how long
  the browser sits there first, and whether the message tells them what to do next.
- Upload two PNGs with no ground scale. Does the panel *say* that scale invariance was not
  exercised, or does it quietly assume 1:1?
- Upload one image twice. Upload a non-image. Upload nothing.

### 3d. The Streamlit app — Gate 4

```
python -m pytest -q
streamlit run app/streamlit_app.py
```

- Cold start time. Align time from cache. Align time live.
- Confirm all four deliverables download and open: the zip, the registered GeoTIFF, the match
  points CSV, the report. Open the GeoTIFF and check its geotransform against the reference's.
- **Wifi off.** Repeat. Anything that reaches the network on the demo path is a BLOCKER.
  Note that the console loads Google Fonts and three.js from a CDN — establish what that
  actually costs when offline, and whether the page degrades honestly or looks broken.
- Three consecutive clean runs.

### 3e. The room a judge will be in

- Phone viewport (393×852). Readable, or zoomed to 40 %?
- 1366×768 projector. Does anything clip?
- Slow 3G (`emulate` with network conditions). The page is ~2 MB with inline base64 imagery —
  time to first paint, and what is on screen while it waits.
- `lighthouse_audit` (snapshot, desktop). Report accessibility and best-practices scores as
  numbers, and list what fails.

## 4. Judge A's interrogation

Now read `REPORT.md`, `docs/00_CANONICAL_FACTS.md` §2 and §7, and `presentation/DECK_V2_DRAFT.md`.
Then attack the *demo* — not the evidence, which `AUDIT_PROMPT.md` covers:

1. Take every number the UI shows and find it in `REPORT.md`. Any that is not there, or is
   there with a different definition, is a BLOCKER.
2. For every accuracy figure on screen: is its pixel grid named, and is the metres equivalent
   right? Is a *held-out* number ever shown where a reader will take it as ground truth?
3. Does the UI ever show the best case where a range is honest? Is the refusals table as
   prominent as the results table, or is it buried below the fold?
4. Ask the six questions a SAC scientist asks in the first ninety seconds, and answer each from
   the screen alone. Where the screen cannot answer, say what the operator would have to say out
   loud — and whether `ops/QA_ANSWERS.md` already has it.
5. Which single claim on screen is the most attackable? Draft the attack, then draft our answer.

## 5. The field — are we actually different?

~500 teams enter; about 4–5 per PS reach the finale. Use `ops/national_round/RESEARCH_REPORT.md`
as the base (it already surveys the public field). You may spend **at most 10 web fetches** to
refresh it — no crawling.

Produce two lists, both concrete:

- **What we can show that a strong competitor cannot.** For each, say whether a judge meets it
  in the first four minutes, or only if they dig.
- **What a strong competitor can show that we cannot.** Be honest. Include the published
  state of the art (SuperGlue/LoFTR baselines, ISIS/ASP, commercial tooling), not just other
  students.

Then answer the question plainly: **is the differentiator visible, or is it buried?** The
differentiator here is not accuracy — it is that the system *declares when it is wrong*, and
that the refusals are reported as results. If a judge would not notice that in four minutes, say
so, and that is a HIGH finding on its own.

## 6. The grade

Score each artefact and then the whole submission on this ladder. Use the definitions; do not
soften them.

| Grade | Means |
|---|---|
| **Below average** | Something visibly broken, or a claim a judge can falsify, or nothing a judge can open |
| **Average** | Works; looks like a competent student project; nothing a judge will remember on Monday |
| **Above average** | Works, is clearly presented, and has at least one thing the judge has not seen from another team |
| **High grade** | A judge would ask who built it; the evidence survives an expert's questions; it looks like the start of a tool someone would actually use |

Give each grade with **the specific evidence that fixes it there**, and the single change that
would move it up one rung.

Also answer, directly and without hedging:

- Would Judge A be **pleased**, or merely satisfied? What would it take to move them?
- Would Judge B **understand** it? At which sentence do they get lost?
- Does every feature the team believes it has actually work end to end today? Produce a table:
  feature · works / partly / no · how you verified · what a judge sees if it fails.

## 7. What to change

Rank every finding by **shortlist impact × confidence ÷ effort**, and split into:

- **Before Fri 25 Sep 22:00** (deck and portal freeze) — must not require re-freezing evidence.
- **Before the finale** — larger work, can touch code.
- **Won't do, and why.**

For each, give: the finding, the fix, the cost in hours, the risk it carries, and how to verify
it afterwards. Anything that would invalidate the freeze must be flagged **RE-FREEZE** — those
cost 90–110 minutes plus a full deck re-verification and are almost never worth it this close to
the deadline.

Separately, propose **capability upgrades** — MCP servers, skills, plugins, connectors or tools
that would raise the ceiling rather than patch a defect. For each: what it buys, what it costs to
set up, and whether it is worth doing before 27 Sep or after. Do not propose a tool that
duplicates something the repo already does.

## 8. What you hand back

One file: `ops/national_round/JUDGE_REPORT_<YYYY-MM-DD>.md`, containing

1. the reachability chain, as a number: what fraction of the work a PDF-only judge ever sees;
2. Judge B's four-minute verdict, written before you read the docs;
3. the inspection log — every artefact, every bay, every control, with the command output or
   screenshot that backs each claim;
4. the feature table from §6;
5. the grades, per artefact and overall, each with its fixing evidence;
6. Judge A's six questions and our answers;
7. the field comparison, both directions;
8. the ranked change list from §7, and the capability upgrades;
9. **the three things most likely to lose us a finale place**, in order.

Then, in your reply to Samartha (not in the file): the grade in one line, the single most
valuable change, and anything you could not check and why.

Work through §1–§8 in order. Do not stop at "found problems" — the job is a graded verdict with
a ranked list of changes behind it.
