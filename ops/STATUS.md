# STATUS — SIH26166

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewrite, never append.** This must be true as of right now.

---

## Position

| | |
|---|---|
| **Day** | 0 of 12 — planning complete, build not started |
| **Repo path** | `C:\Users\samar\OneDrive\Documents\SIH26166` |
| **Git** | ⚠️ **NOT INITIALISED YET** — first task of next session |
| **Internal hackathon** | ⚠️ **DATE UNKNOWN — chase the SPOC** |
| **Next gate** | Gate 1, Day 5 — pipeline runs end to end on a real lunar pair |
| **Gates passed** | none |
| **Deadlines** | SIH26166 closes 20 Sep 2026 · SPOC portal upload 30 Sep 2026 · Finale Dec 2026 |

---

## Last session (29 Aug 2026) — planning and harness build

No code written. The session audited a pre-existing set of seven AI-drafted planning documents,
found critical defects, rewrote all of them, and built the Claude Code harness.

**Smoke:** `pytest` NOT RUN (no tests exist) · `core.pipeline` NOT RUN (no code exists)

### What now exists

```
docs/   00_CANONICAL_FACTS         <- single source of truth, read first
        01_HOW_WE_WORK_TOGETHER    <- git + Drive workflow, OneDrive warnings
        02_DAILY_REVIEW_PROTOCOL   <- findings-not-fixes, why
        TEAM_TASK_GUIDE            <- 12-day schedule, all 6 people
        + one guide per person (Rohan, Samrudh, Risheeth, Rishabh, Saniya, Samartha)
.claude/ agents/   daily-reviewer, spec-writer, demo-medic, claim-checker  (none can write files)
         commands/ /next, /wrap, /review
         hooks/    session_brief.py (SessionStart)
         settings.json
CLAUDE.md
ops/STATUS.md
```

Nothing else. No `core/`, no `evaluation/`, no `requirements.txt`, no repo.

---

## Verified this session — do NOT re-verify

Checked against live sources. Treat as settled.

**Hardware**
- Samartha's laptop = **demo machine**: Intel Core Ultra 5 125H, 14C/18T, **Intel Arc iGPU with
  0 MB dedicated VRAM**, 15.4 GB RAM, 785 GB free. **No discrete GPU. No CUDA.**
- Rohan's PC: i7-14700K, **RX 9060 XT 16 GB (AMD, gfx1200)**, 32 GB DDR5, 1 TB SSD + 2 TB HDD.
  ~30 km away. Data server, never on the demo path.
- Python 3.12.10 at `C:\Users\samar\AppData\Local\Programs\Python\Python312\`. torch NOT installed.
- `python3` fails on Windows (Store alias). Use `python` or `py`.

**Data — all public, all confirmed reachable**
- **CH-2 OHRC imagery + all ISRO instrument user guides: `archive.org/details/chandrayaan-2-high-resolution-images-of-the-moon` — NO ACCOUNT.** This dissolved the PRADAN blocker.
- ISRO's own SIH guidance names `chmapbrowse.issdc.gov.in` + `pds4_tools`. Registration required
  there and at `pradan.issdc.gov.in`, but **no email-domain rule is stated anywhere** — untested.
- LROC: `pds.lroc.im-ldi.com` open directory · ODE anonymous · `quickmap.lroc.im-ldi.com`
- Kaguya TC: `s3://astrogeo-ard/moon/kaguya/terrain_camera/monoscopic/uncontrolled/`
  `--no-sign-request`, **Cloud-Optimized GeoTIFF, CC0**
- Chandrayaan-1 M3 (the multi-modal leg): PDS Imaging Node, no login
- SLDEM2015 (ground truth): PDS Geosciences, 59 m/px

**Licences**
- LoFTR = **Apache-2.0** (LICENSE file read directly) → our matcher
- **SuperPoint = non-commercial research only** — LightGlue's own README says so. **Rejected.**
- DISK / ALIKED = permissive, if a sparse matcher is ever needed

**Packages**
- `pip install magsac` **DOES NOT EXIST**. Use `cv2.USAC_MAGSAC`.
- Available: `pds4_tools` 1.4 · `pvl` 1.3.2 · `rasterio` 1.5.1 · `kornia` 0.8.3 ·
  `opencv-contrib-python` 5.0.0.93 · `streamlit` 1.62.0 · `pymagsac` 0.2.3

**SIH**
- College SPOC registered before the 14 Aug deadline ✅ · team registered, SIH26166 submitted ✅
- Internal round is **in person, live demo, faculty judges (not domain experts)**
- 226 PS total / 172 software — matches the original brief
- ⚠️ "Level 1" difficulty label does **not** appear in the PS listing. Never say it to a judge.
- OHRC is **~28 cm/px** per ISRO's own portal — not 0.25 m

---

## Decisions made, with reasons

1. **12-day plan, not 15.** Internal round is likely Day 10–12. Days 13–15 are buffer.
2. **Validation ladder replaces loose "cross-sensor" talk.** Tier A sun-angle (same sensor) ·
   B cross-sensor · B+ 20× scale · C **multi-modal** · D ground truth. The old docs called
   LROC↔LROC "cross-sensor", which is false and was the likeliest Q&A kill shot.
3. **CPU-only demo.** Follows from the hardware. Tile size comes from a Day-1 measurement.
4. **Numbers discipline.** Nothing enters a slide until it is in `evaluation/results_log.csv`.
   The old drafts carried invented figures ("0.7 px", "SIFT 4.2 px", "RTX 3080") through four files.
5. **Agents cannot write files.** Protects Gate 5 — each person must be able to explain their own
   module, so reviews produce findings, not fixes.
6. **Direct commits to `main`**, one folder per person. Branch+PR would make Samartha a bottleneck
   on five people's 2-hour days.
7. **Code in git, images in Google Drive.** GitHub rejects >100 MB; OHRC ZIPs are ~750 MB.
8. **Gate 2-alt added.** The old Gate 1 fallback ("drop the learned matcher") made the old Gate 2
   ("3× better than classical") unpassable — it would have been classical vs classical.

---

## Per person

Nobody has started. All six need the Day-1 setup from `docs/01_HOW_WE_WORK_TOGETHER.md`.

| Person | Status | Day 1 task |
|---|---|---|
| Samartha | not started | Repo + `.gitignore` first + **CPU benchmark of LoFTR** |
| Rohan | not started | CH-2 OHRC from archive.org + test registration with personal Gmail |
| Samrudh | not started | Install, `shaded_relief.py` stub, get an SLDEM tile |
| Risheeth | not started | SIFT/ORB/AKAZE on a **self-made** shifted pair — depends on nobody |
| Rishabh | not started | `detect_changes` on a **self-made** pair — depends on nobody |
| Saniya | not started | **Download the SIH template and confirm the six real headings** |

---

## In flight

Nothing mid-edit. The document set and harness are complete and internally consistent
(verified: no surviving fabricated numbers, gate days consistent at 5/8/10/11/12, no
`pip install magsac`, no branch/PR contradictions, all cross-references resolve).

---

## Open questions

1. **Internal hackathon date** — still unknown. Reshapes the schedule. Chase the SPOC.
2. **SIH 2026 template headings** — assumed (Problem Statement · Proposed Solution · Technical
   Approach · Feasibility and Viability · Impact and Benefits · Research and References), **not
   confirmed against the actual file.** Saniya Day 1. Blocks deck work Days 2–7.
3. **LoFTR CPU latency on Samartha's laptop** — Day 1 hour 1. Determines tile size, UI design, and
   what the demo script can promise. Everything downstream waits on this number.
4. **Does chmapbrowse/PRADAN accept a personal Gmail?** Rohan tests Day 1, 10 minutes.
5. **Chandrayaan-3 landing-site NAC product IDs** — `[VERIFY]`. LROC imaged the site before and
   after Aug 2023 and Vikram is visible. If Rohan finds these, Rishabh's change-detection demo
   becomes the best 20 seconds in the pitch.

---

## Known issues / traps already found

Recorded so `daily-reviewer` does not re-report them:

- **OneDrive + git.** Repo sits in a synced folder. Set "Always keep on this device" on the folder
  (Files On-Demand placeholders would break Gate 4). Pause sync during big git operations.
  See `docs/01_HOW_WE_WORK_TOGETHER.md`.
- **Streamlit nested buttons.** `st.button()` inside `if st.button():` can never fire — Streamlit
  reruns the script on every interaction. Use `st.session_state`.
- **ORB/AKAZE need `BFMatcher(NORM_HAMMING)`**, not FLANN KD-tree — binary descriptors.
- **SIFT ratio test crashes** when `knnMatch` returns a single match; guard with `len(pair)==2`.
  Also guard `des is None`, which is normal on dark mare regions.
- **`cv2.medianBlur` requires uint8.** Lunar products arrive uint16/float.
- **Model weights download on first use.** Cache to `weights/` or Gate 4 fails with wifi off.
- **A silently dead hook** was found and fixed this session: Windows cp1252 console + em-dashes in
  STATUS.md → `UnicodeEncodeError` swallowed by `try/except` → hook printed nothing, exit 0. Now
  transliterates. **Lesson: after adding any hook, run it once and confirm you see output.**

---

## Next session — do these in order

1. `git init`, create `.gitignore` **first** (contents in `01_HOW_WE_WORK_TOGETHER.md` §Setup),
   then the folder skeleton from `00_CANONICAL_FACTS.md` §14.
2. Create the private GitHub repo, add 5 collaborators, push.
3. Create + share the Google Drive `SIH26166_DATA` folder.
4. Set OneDrive "Always keep on this device" on the project folder.
5. `pip install torch --index-url https://download.pytorch.org/whl/cpu` then **run the LoFTR CPU
   benchmark** (code in `docs/SAMARTHA_INTEGRATION_GUIDE.md`, Day 1). Post the number to the team.
6. Send the five Day-1 specs as GitHub Issues.
7. Chase the SPOC for the hackathon date.

---

## Reviewed through

No commits exist yet.
