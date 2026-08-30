# STATUS — SIH26166

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewrite, never append.** This must be true as of right now.

---

## Position

| | |
|---|---|
| **Day** | 1 of 12 — repo live, Samartha's Day 1 done, five teammates have not started |
| **Repo path** | `C:\Users\samar\OneDrive\Documents\SIH26166` |
| **Git** | ✅ live — `https://github.com/samarthputhraya/sih26166` (private, branch `main`) |
| **venv** | `C:\Users\samar\venvs\sih26166` — deliberately OUTSIDE the OneDrive folder |
| **Internal hackathon** | ⚠️ **DATE STILL UNKNOWN — chase the SPOC** |
| **Next gate** | Gate 1, Day 5 — pipeline runs end to end on a real lunar pair |
| **Gates passed** | none |
| **Deadlines** | SIH26166 closes 20 Sep 2026 · SPOC portal upload 30 Sep 2026 · Finale Dec 2026 |

---

## Last session (30 Aug 2026, Day 1) — environment, benchmark, repo, specs

**Smoke test, run this session — exit codes observed, not inferred:**

| Command | Exit | Meaning |
|---|---|---|
| `pytest evaluation/ -q` | **5** | "no tests collected" — `evaluation/` is empty. Samrudh writes `test_metrics.py` on Day 4. Not a regression. |
| `import core.pipeline` | **1** | `ModuleNotFoundError` — `pipeline.py` is Day 3 work. Not a regression. |
| `import core.bench_loftr_cpu`, `core.fetch_weights` | **0** | Everything that exists imports cleanly. |

Working tree clean, everything pushed. Three commits, all Samartha's:
`7644b4c` repo init · `15b91ec` fetch_weights · `e8a4e84` Day-1 specs.

### What landed

```
core/bench_loftr_cpu.py          LoFTR CPU benchmark harness
core/bench_loftr_cpu_results.csv 10 measured rows
core/fetch_weights.py            one-off weight fetch + sha256 verify, offline-safe
weights/loftr_outdoor.pt         46 MB, gitignored, NOT YET ON DRIVE
ops/specs/day01_*.md             6 files: shared setup + one per teammate
.gitignore .gitattributes requirements.txt README.md
+ the §14 folder skeleton (.gitkeep so folders survive a clone)
```

---

## Measured this session — do NOT re-measure

**LoFTR CPU latency**, demo laptop, lunar-like synthetic relief, 14 threads.
Logged in `core/bench_loftr_cpu_results.csv`. **Not yet in `results_log.csv`, so not quotable.**

| | |
|---|---|
| 480² | 2.73 s (sd 0.20), 1618 matches, peak RSS 1.18 GB |
| **640²** | **5.50 s cold / 7.54 s warm steady-state** (+24% thermal drift), 2824 matches, peak RSS 1.84 GB |
| 1024² | **NOT VIABLE** — needs ~3.6 GB of activations |

**DECISION: tile size 640. Live inference with a progress bar, narrated.** Quote the **warm** number
(7.5 s) — by demo time the machine has been warm for minutes, and the cold number is the optimistic
direction Invariant 1 forbids.

Three measurement traps, already paid for:
- **`torch.rand` under-reports latency by ~13%** and exercises the fine stage on 139 matches instead
  of 2824. LoFTR's runtime is content-dependent. Never benchmark on noise.
- **Thermal drift is +24%** across 18 back-to-back passes, smooth and monotonic.
- **Memory pressure is a separate effect** that looks similar and is not. Below ~2 GB free the
  machine thrashes: isolated 3–4× spikes that snap back. A first attempt conflated the two and
  produced a wrong reading. The harness now separates them statistically.

**Weights:** kornia fetches LoFTR weights over **plaintext HTTP from a researcher's personal CVUT
page**, with no integrity check, unpickled with `weights_only=False`. Both files are now sha256-pinned
in `bench_loftr_cpu.py`; `fetch_weights.py` reproduces them exactly. SSL fails on this network without
pointing Python at the certifi CA bundle.

---

## Per person

**Nobody except Samartha has pushed anything.** `app/`, `evaluation/`, `baselines/`, `data/` and
`presentation/` contain only `.gitkeep`.

| Person | GitHub | Access | Pushed | Blocked on |
|---|---|---|---|---|
| Samartha | `samarthputhraya` | owner | 3 commits | nothing |
| Rohan | `rohanshahare` | ✅ accepted | nothing | Drive folder (Samartha) for anywhere to put OHRC |
| Samrudh | `SamrudhNandakumar` | ✅ accepted | nothing | nothing — spec is self-contained |
| Rishabh | `rizzhub3118` | ✅ accepted | nothing | nothing — spec is self-contained |
| Saniya | `ssaniyabi` | ✅ accepted | nothing | nothing — needs no repo, no Python |
| Risheeth | `risheeth26233` | ⚠️ **INVITE STILL PENDING** | nothing | cannot clone until he accepts |

**Rishabh reported at 15:31 IST that change detection is "complete with automated tests, robustness
checks and README".** None of it is in the repo. He accepted his repo invite at 16:54 IST — 83
minutes *after* declaring completion — and has not pushed since. The work may exist; there is no
evidence, nothing reviewable, and nothing that survives his laptop dying. **First ask tomorrow: push.**

**Day-1 specs remain live and unexecuted.** No Day-2 specs were issued — see Sequencing below.

---

## In flight

Nothing mid-edit. Working tree clean, remote in sync.

**Resume here:** `core/io_loader.py`. Nothing exists yet. It is Samartha's Day-1 afternoon task,
carried to next session, and it is on the critical path twice over — Rohan's Day-5 catalogue needs
`crop_to_overlap` from it, and Gate 1 on Day 5 needs it under `pipeline.py`.

```python
def load(path) -> tuple[np.ndarray, dict]:
    """Returns (grayscale float32 array, metadata dict).
    metadata keys: gsd_mpp, instrument, sun_azimuth, sun_elevation, incidence, crs, transform
    Dispatch on extension: .xml -> pds4_tools | .IMG -> pvl (+ raw numpy) | .tif -> rasterio
    """
```

Write the **format abstraction now**, even though only one format is testable today. CH-2 is PDS4,
LROC is PDS3, Kaguya is GeoTIFF. Hardcoding one format costs two days on Day 9.

⚠️ **The `.tif` branch cannot use rasterio** — see Known issues. Either resolve that first or leave
the branch stubbed with a clear `NotImplementedError`.

---

## Open questions

1. **Internal hackathon date** — still unknown. Reshapes the schedule. Chase the SPOC.
2. ~~SIH 2026 template headings~~ — **CLOSED.** Real file downloaded and parsed: 924,505 bytes,
   sha256 `ce3e5dee…`, 7 slides. See Known issues #3 for the correction it forces.
3. **`rasterio` is unusable on the demo machine** — see Known issues #1. **Samartha's to resolve,
   needed by Day 3.**
4. **Google Drive `SIH26166_DATA` does not exist.** Blocks Rohan, and blocks distributing
   `weights/loftr_outdoor.pt` (46 MB) to five people. Needs a browser session.
5. **Chandrayaan-3 landing-site NAC product IDs** — still `[VERIFY]`, never confirmed. Rishabh needs
   them ~Day 6. **Terminology warning:** these are **LROC NAC images OF the CH-3 landing site**, not
   "Chandrayaan-3 imagery". CH-3's own cameras are surface cameras and are useless for this. Rishabh
   used the wrong phrasing in chat on Day 1; correct it before it reaches a slide.

---

## Known issues / traps already found

Recorded so `daily-reviewer` does not re-report them.

1. **`rasterio` imports but its DLLs are blocked.** Exact error:
   `ImportError: DLL load failed while importing _base: An Application Control policy has blocked this file.`
   Windows Application Control is blocking its bundled GDAL DLLs. **This threatens Tier B+**:
   `00_CANONICAL_FACTS.md` §3 calls Kaguya TC "the cheapest win in the set" because `rasterio.open()`
   reads COGs over HTTP, and that is Rohan's Day 3. Note that **disabling Smart App Control is a
   one-way door** — it cannot be re-enabled without an OS reinstall. Try a different GDAL wheel, or
   read the COG bytes directly (as Samrudh now does for SLDEM), before touching the OS setting.
2. **`cv2.AKAZE_create()` does not exist in opencv-contrib-python 5.0.0.93.** AKAZE, KAZE and BRISK
   moved into `cv2.xfeatures2d`. `RISHEETH_BASELINE_GUIDE.md` has the old call. The natural "fix"
   (downgrading OpenCV) desynchronises the team's pins and loses SIFT. Verified present:
   `cv2.SIFT_create`, `cv2.ORB_create`, `cv2.xfeatures2d.AKAZE_create`, `cv2.USAC_MAGSAC` (=38).
   AKAZE descriptors are `uint8 (N,61)` → Hamming; SIFT's are `float32` → FLANN is fine.
   `cv2.findContours` returns **2** values in OpenCV 5.
3. **The SIH 2026 template has NO "Problem Statement" slide.** Slide 1 is a metadata **TITLE PAGE**
   (PS ID, title, theme, category, team ID, team name). The instructions slide says verbatim:
   *"Kindly keep the maximum slides limit up to six (6). (Including the title slide)"* — so the cap
   **includes** the title page and we have **five content slides, not six**.
   `00_CANONICAL_FACTS.md` §10 and `TEAM_TASK_GUIDE.md` both assume otherwise and **still need
   correcting.** Saniya's Day-2 row ("Draft Slide 1 — Problem Statement") is not executable.
   Real order: TITLE PAGE · IDEA TITLE · TECHNICAL APPROACH · FEASIBILITY AND VIABILITY ·
   IMPACT AND BENEFITS · RESEARCH AND REFERENCES.
4. **sih.gov.in returns 403 to non-browser user agents.** Download the template through a browser,
   or send a browser `User-Agent` header.
5. **`.gitignore` had no rule for PDFs or Office files.** Fixed — `*.pdf`, `*.pptx`, `*.docx` added
   before Rohan's ISRO guides or Saniya's template could be committed.
6. **Windows `num_page_faults` counts SOFT faults.** A legitimate 1.4 GB LoFTR pass reports ~1.3 M
   faults. Useless for detecting swapping; use a statistical outlier rule instead.
7. **OneDrive + git.** Repo sits in a synced folder. `attrib +P -U` has been applied recursively —
   verified **0 cloud-only placeholders**. Re-check before Gate 4. Pause sync during big git ops.
8. **Streamlit nested buttons.** `st.button()` inside `if st.button():` can never fire. Use
   `st.session_state`.
9. **SIFT ratio test crashes** when `knnMatch` returns a single match — guard `len(pair)==2`. Also
   guard `des is None`, normal on dark mare regions.
10. **`cv2.medianBlur` requires uint8.** Lunar products arrive uint16/float.
11. **A silently dead hook** was found on Day 0: Windows cp1252 console + em-dashes → swallowed
    `UnicodeEncodeError`. Now transliterates. **After adding any hook, run it once and confirm output.**

---

## Sequencing risks — fix these before they land

- **No Day-2 specs were issued, deliberately.** Zero of the five Day-1 specs were executed. Issuing
  Day-2 on top would double five people's backlog and guarantee both fail. **The Day-1 specs in
  `ops/specs/` stand as tomorrow's specs.** Re-issue Day 2 only once Day 1 is actually pushed.
- **Rohan Day 5 needs `core.io_loader.crop_to_overlap`**, which does not exist. Must land by end of
  Day 4 or his catalogue slips — and the catalogue gates Risheeth Day 4, Rishabh Day 5 and Gate 1.
- **Rishabh Day 5 needs `data/pairs_catalogue.csv`; Rohan does not deliver it until end of Day 5.**
  Same-day collision. Cheap fix: ask Rohan to post `source_gsd_mpp` for his two primary pairs in chat
  by end of Day 4.
- **Risheeth Day 3 wants to log via the harness; `evaluation/metrics.py` does not exist until
  Samrudh's Day 3.** Tell him to write his own two-column CSV on Days 1–2 and adapt later.
- **Samrudh's hillshade has no cast shadows.** `np.clip(shade, 0, 1)` is Lambertian *self*-shading.
  Any claim that "the shadows are physically real" is an overclaim. Either ray-trace cast shadows or
  say "shaded relief at two sun positions". Flag to `claim-checker` before Day 8.
- **`docs/01_HOW_WE_WORK_TOGETHER.md` §Setup step 5 says `pip install -r requirements.txt`.** That
  now pulls ~250 MB of torch nobody needs on Day 1 plus the broken rasterio. The Day-1 specs give
  minimal per-person install lines instead; the doc still needs updating.

---

## Next session — do these in order

1. **`core/io_loader.py`** — the format abstraction. Highest-value solo work; unblocks Rohan Day 5
   and Gate 1. Leave the `.tif` branch stubbed if rasterio is still blocked.
2. **Resolve rasterio**, or decide formally that Kaguya (Tier B+) reads raw bytes instead. Day-3 blocker.
3. **Create the Google Drive folder**, share to five, upload `weights/loftr_outdoor.pt`.
4. **Chase Risheeth's invite acceptance**, and chase Rishabh to push what he says exists.
5. **Correct `00_CANONICAL_FACTS.md` §10 and the Saniya rows in `TEAM_TASK_GUIDE.md`** to the real
   six template headings.
6. **Chase the SPOC** for the internal hackathon date.

---

## Reviewed through

`e8a4e84`. No teammate commits exist yet, so `daily-reviewer` has nothing to review.
