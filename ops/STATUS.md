# STATUS — SIH26166

> Rewritten by `/wrap` at the end of every session. Read by `/next` at the start of the next one.
> **Rewrite, never append.** This must be true as of right now.

---

## Position

| | |
|---|---|
| **Day** | 2 of 12 — Gate-1 chain built and running; Rohan and Rishabh have pushed |
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

**Rohan has pushed — the first teammate commit of the project** (`b1e6372`, 30 Aug ~18:45,
`data/DATASET_CARD.md`). One row: LROC NAC EDR `M108587604RE.IMG`, real source URL, product ID,
download date; `tier` and `licence` correctly left blank rather than guessed. The `.IMG` itself is
on his machine only — it is gitignored and there is still no Drive folder, so **no route exists for
it to reach anyone else.** Samartha fetched the same product independently from the public URL to
validate the loader against real data (MD5 in the label matched).

`app/`, `evaluation/`, `baselines/` and `presentation/` still contain only `.gitkeep`.

| Person | GitHub | Access | Pushed | Blocked on |
|---|---|---|---|---|
| Samartha | `samarthputhraya` | owner | 7 commits — io_loader + full Gate-1 chain | nothing |
| Rohan | `rohanshahare` | ✅ accepted | **3 commits** — DATASET_CARD, provenance policy, LROC crater analysis | Drive folder (Samartha) |
| Rishabh | `rizzhub3118` | ✅ accepted | **2 commits + PR #1** — `app/change_detection.py`, 7 passing tests, README | nothing |
| Samrudh | `SamrudhNandakumar` | ✅ accepted | **nothing** | nothing — spec is self-contained. **Gate 1 needs his `evaluate()`** |
| Saniya | `ssaniyabi` | ✅ accepted | **nothing** | nothing — needs no repo, no Python |
| Risheeth | `risheeth26233` | ✅ **accepted** | **1 commit** (`5067ffb`) — all 3 baselines + failure gallery + runner, 759 lines | nothing |

**Rishabh delivered.** He declared change detection complete on Day 1 before anything was in the
repo; it is now pushed, reviewable, and its 7 tests pass. He also avoided both OpenCV 5 traps
unprompted — `cv2.findContours` unpacked as 2 values, and uint8 conversion before `cv2.medianBlur`.
No hardcoded paths.

**Rohan closed both findings raised against his own work** within hours, without being asked twice.

**Risheeth delivered, and delivered well.** `5067ffb` — `sift/orb/akaze_baseline.py`,
`make_test_pair.py`, `run_all_baselines.py` and `draw_failure_gallery.py`, 759 lines, more than
Day 1 asked for. Verified by running his own acceptance test: **all three recover the known shift
exactly** — SIFT 1424 matches, ORB 3657, AKAZE 1922, every one at median `(-7.00, -5.00)`.
He avoided all three known traps unprompted: `cv2.xfeatures2d.AKAZE_create()` (and documented why),
the `des is None` guard, and the `len(p) == 2` ratio-test guard.

⚠️ **One person has now been silent for two days: Samrudh.** That is the Gate-5 risk
the protocol says to flag by name — someone who stops working stops understanding, and cannot answer
for their module cold on Day 12. Risheeth still has not accepted the repo invite, which is a
one-click blocker nobody has cleared in 48 hours. **Samrudh is now on the critical path**: Gate 1
prints "metrics unavailable" until `evaluation/metrics.py :: evaluate()` exists.

⚠️ **Rohan committed ~3.9 MB of PNGs** to `data/lroc_analysis/` (12 files, largest 2.2 MB). Invariant
5 says nothing binary goes in the repo; `.gitignore` has no `*.png` rule, so git accepted them
silently. Git history now carries them permanently — deleting the files does not shrink the repo.
Finding for Rohan, not a silent fix: plots belong in Drive, and the analysis `.md` can reference
them. Decide whether to add `*.png` with a `!baselines/failure_gallery/` exception.

⚠️ Rohan also wrote `ops/lroc/analyze_candidate.py` (620 lines) and `docs/LROC_CANDIDATE_ANALYSIS.md`
(593 lines). `ops/` and `docs/` are Samartha's under Invariant 4. The work looks genuinely good —
this is a boundary question, not a quality one, and the honest fix may be to widen his folder rather
than move his files.

---

## In flight

Nothing mid-edit. Working tree clean, remote in sync.

**`core/io_loader.py` is written and tested** — 31/31 synthetic checks pass (PDS3 attached-label
round-trip, GeoTIFF geo tags, LZW-via-Pillow, five degrade-don't-crash cases, four raise-don't-lie
cases). It exports `load`, `dump_label`, `plan_overlap`, `crop_to_overlap`, `as_cv_safe`.

**It has now met one real lunar product.** Rohan's `M108587604RE.IMG` (LROC NAC EDR, 5,190,600
bytes) loads end to end in 0.26 s to `(1024, 5064)` float32, and the image bytes match the
`MD5_CHECKSUM` recorded in the product's own label. Two real bugs came out of that and are fixed —
see Known issues 00 and 0a. `INSTRUMENT_NAME` and `PRODUCT_ID` resolved from the real label without
changes to `CANDIDATES`.

**No PDS4 / CH-2 product has been seen yet**, so the PDS4 branch is still untested against reality
and its field names remain candidate spellings. **The hour the first CH-2 `.xml` lands, run this:**

```
python -c "from core.io_loader import dump_label; dump_label('<the file>')"
```

It prints every label leaf and marks the ones matching a candidate. Copy the true spellings into
`CANDIDATES`. That is a one-line change per field. Guessing them is how a wrong sun angle reaches a
slide.

**THE GATE-1 CHAIN IS BUILT AND RUNS** (`3cbb722`): `core/scale.py`, `core/matcher.py`,
`core/ransac.py`, `core/pipeline.py`.

```
python -m core.pipeline <pair dir or prefix>     # exit 0
load -> to_common_gsd -> illumination -> LoFTR -> MAGSAC++ -> warp -> metrics
```

> 🔴 **CORRECTION — an earlier entry in this file and commit `3cbb722` reported
> "RMSE 0.0392 px on real lunar texture". That was wrong and flattering by 10×.**
> `M108587604RE.IMG` **contains no scene content**: 98.1% of the frame sits in DN 32–46, the
> 400×400 crop has std 1.42 and only 15 distinct DN values, and there are no craters anywhere in
> it. The chain was matching a warped copy of *sensor noise*, which is the EASIEST possible target —
> fine-grained noise is a unique high-frequency fingerprint at every pixel. Same chain, same known
> homography, on content with actual structure:
>
> | content | std | matches | inliers | RMSE |
> |---|---|---|---|---|
> | `M108587604RE` (no scene content) | 1.42 | 5264 | 100% | **0.0370 px** |
> | synthetic lunar relief (`lunar_tile`) | 4.63 | 4075 | 90% | **0.3716 px** |
>
> **Use ~0.37 px as the working expectation, not 0.04.** Both remain **NOT quotable** — neither is
> in `results_log.csv`, and both are self-made pairs, so neither is cross-sensor, multi-modal, or
> even Tier A. This is exactly the error the Day-1 spec's "**Display it**" step exists to catch:
> the loader was provably correct (MD5 matched, and the masked columns 5056/5057 land as exact
> full-height columns, which a wrong stride would smear diagonally) while the *image* was useless.
> **Numbers can pass every test while the picture is empty. Always look at the picture.**

What the dry run does still prove, because these are content-independent geometric facts: the chain
runs end to end unattended, keypoints are `(x, y)`, the homography is recovered in the right
orientation, and the coordinate round-trip through resampling is exact.

Two seams are deliberately empty and announce themselves at runtime: `illumination.py` (Day 5–6)
and `evaluation/metrics.py` (Samrudh, Day 3). **`pipeline.py` computes no metrics of its own** — a
second implementation in `core/` would give this project two sources of truth for its headline
accuracy number. The held-out 20% split stays in Samrudh's `evaluate()` for the same reason;
`filter_matches` fits on everything because its output is the operational warp.

**Resume here next:** Gate 1 needs a **real pair**, which is Rohan's. Until one exists the chain
cannot be exercised for real. Meanwhile the honest next builds are `core/illumination.py` (Day 5–6)
and then `subpixel.py` + `distribution.py` (Day 8). Do **not** tune anything against the self-made
pair — it has no illumination difference and no scale difference, so it cannot tell you anything
about the two problems those modules exist to solve.

⚠️ **The `.tif` branch cannot use rasterio** — see Known issues. Either resolve that first or leave
the branch stubbed with a clear `NotImplementedError`.

---

## Open questions

1. **Internal hackathon date** — still unknown. Reshapes the schedule. Chase the SPOC.
2. ~~SIH 2026 template headings~~ — **CLOSED and propagated.** Real file: 924,505 bytes, sha256
   `ce3e5dee…`, 7 slides. All six affected documents corrected this session — `00_CANONICAL_FACTS`
   §10, `TEAM_TASK_GUIDE` (Saniya Days 1–7), `SANIYA_NARRATIVE_GUIDE` (14 edits incl. the day-by-day
   restructure), `day01_saniya_template`, `01_HOW_WE_WORK_TOGETHER`, and `CLAUDE.md` (now
   **Invariant 7**, so no future session re-derives the wrong list).
3. ~~`rasterio` unusable~~ — **CLOSED. Decision: GDAL-free.** See Known issues #1 for the decision
   and its one real cost (no Kaguya-over-HTTP).
4. **⚠️ Google Drive `SIH26166_DATA` STILL DOES NOT EXIST — the top blocker.** Rohan has nowhere to
   put OHRC, and `weights/loftr_outdoor.pt` (46 MB, gitignored) exists on **exactly one laptop**.
   Needs a browser session; no Google Drive desktop mount on this machine, so it cannot be scripted.
   Folder list, now including the two additions made this session:
   `raw_samples/ pairs/ demo_cache/ weights/ isro_user_guides/`
5. **Chandrayaan-3 landing-site NAC product IDs** — still `[VERIFY]`, never confirmed. Rishabh needs
   them ~Day 6. **Terminology warning:** these are **LROC NAC images OF the CH-3 landing site**, not
   "Chandrayaan-3 imagery". CH-3's own cameras are surface cameras and are useless for this. Rishabh
   used the wrong phrasing in chat on Day 1; correct it before it reaches a slide.

---

## Known issues / traps already found

Recorded so `daily-reviewer` does not re-report them.

000. **🔴🔴 LoFTR NEEDS [0,1]. RAW DN RETURNS ZERO MATCHES, SILENTLY.** The single most
   dangerous behaviour found so far, because there is no exception — just an empty result that
   reads as *"the matcher does not work on lunar imagery"*. Measured on real NAC texture, two
   640² crops with a known (24, 17) shift:

   | input | matches | confidence |
   |---|---|---|
   | `[0,1]` normalised | **5402** | 0.996 |
   | raw DN `[32..199]` | **0** | — (no error) |
   | per-tile min–max | 5402 | 1.000 |

   `io_loader.load()` deliberately returns **raw DN** — a loader must not silently rescale science
   data. So `core/matcher.py` normalises **once**, internally, where it is documented. Wiring the
   two together the obvious way would have produced a Day-2-checkpoint "LoFTR fails on lunar data"
   verdict and could have cost us the entire approach. **Never pass raw DN to LoFTR.**
   We use fixed `/255`, not per-tile min–max: per-tile makes each tile's normalisation depend on
   its own content, so the same crater normalises differently depending on where the tile boundary
   fell — a correctness hazard in a tiled matcher, not a tuning choice.
   Also confirmed by sign and axis: **keypoints are `(x, y)`, not `(row, col)`.**

00. **🔴 A NAC EDR CARRIES NO ILLUMINATION GEOMETRY. THIS BREAKS TIER A AS WRITTEN.**
   ✅ **Rohan has acted on this** (`e8ebd75`): `DATASET_CARD.md` now records the policy — EDRs are
   source/reference data only, and Tier A moves off EDRs. He also recorded that Kaguya will be
   downloaded locally rather than read over HTTP/GDAL. Both of last night's findings closed by the
   owner.

   🔴 **But his replacement plan needs correcting, and so did our own docs.** Verified 31 Aug
   against ODE's `query=iipy` product-type listing:
   - **`SDRPHO` DOES NOT EXIST.** The real code is **`SDPPHO`** (P, not R).
     `00_CANONICAL_FACTS.md` §3 carried the typo and `DATASET_CARD.md` inherited it. Canonical
     Facts and `ROHAN_DATA_GUIDE.md` are now fixed; his card is his to fix.
   - **`SDPPHO` has `ValidIncidenceAngles = F`** in ODE — it will not give him incidence anyway.
   - ✅ **`EDRNAC4` and `CDRNAC4` have `ValidIncidenceAngles = T`.** So ordinary NAC EDRs come back
     from the **ODE REST API** *with* `Incidence_angle` attached. The EDR *label* has no
     illumination geometry (confirmed on a real product) but ODE's metadata does. **That is the
     Tier A route.**
   - Two ready-made Tier A pairs already found and handed to him, both far exceeding the ≥15°
     requirement: Apollo 15 (**25.2° vs 79.3°, Δ54.1°**) and Copernicus (**22.2° vs 78.1°, Δ55.8°**).
   - ⚠️ Filter to incidence **20–80°**. ODE returns products at 139° and 164°, which are night-side
     and useless.
   ⚠️ And for Samartha: `io_loader.as_cv_safe()` takes **band 0** of a multi-band product and
   `_load_pds3` assumes **band-sequential** storage. Neither is verified against a real SDRPHO —
   check `BAND_STORAGE_TYPE` the hour one lands.

0d. **✅ DAY-2 CHECKPOINT PASSED ON REAL CHANDRAYAAN-2 OHRC DATA.**
   Product `ch2_ohr_ncp_20200229T0739312111_d_img_d18` downloaded from archive.org (791 MB zip →
   1.12 GB `.img`), **MD5 verified against the label's own `md5_checksum`**. 93693 × 12000 at
   **0.22977 m/px**. Two 640² tiles read with the new windowed loader in **0.01 s**, tile std 20.7
   (real terrain — compare the dud LROC frame at 1.42).

   | | |
   |---|---|
   | matches | 5186, mean confidence 0.998 |
   | inliers | 5183 (99.9%) |
   | recovered offset | (−40.00, −24.98) vs known (−40, −25) |
   | offset error | median **0.117 px** = 2.7 cm on the ground |
   | latency | 6.1 s (Day-1 benchmark: 5.5 cold / 7.5 warm) |
   | RSS delta | 1.41 GB |

   > ⚠️ **Read the caveats before this number goes anywhere.** The two tiles are an **integer**-pixel
   > offset crop of the *same* frame, so they contain literally identical pixels — no resampling, no
   > sub-pixel shift, no rotation, no scale change and **no illumination difference**. That is the
   > easiest possible real-data case and 0.117 px reflects that. On synthetic lunar relief *with* a
   > rotation and scale change the same chain gives 0.37 px. Expect real Tier A/B pairs to be worse
   > than both. **Not quotable** until it is in `results_log.csv`, and it is **not cross-sensor, not
   > multi-modal, not Tier A** — it is one OHRC frame matched against itself.
   >
   > What it *does* prove: LoFTR works on real OHRC lunar texture at an affordable CPU latency, the
   > windowed loader works, and the whole chain is wired correctly. That was the Day-2 question.

0e. **🔴 CHANDRAYAAN-2 OHRC SHIPS NO ILLUMINATION GEOMETRY. ANYWHERE.**
   Not in the PDS4 label, and **not in the geometry file either** — the 3.9 MB
   `..._g_grd_d18.csv` has exactly four columns: `Longitude, Lattitude, Pixel, Scan`
   (113,499 rows). No sun azimuth, no incidence, no emission, no phase. Confirmed against the real
   product, so this is settled, not suspected. Consequences:
   - **Tier B (CH-2 OHRC ↔ LROC NAC) is unaffected** — cross-sensor does not need sun angles.
   - **Any sun-angle claim about CH-2 is not supportable from the product.** Sun-angle work must
     ride on LROC SDRPHO (which carries incidence per pixel), or the angles must be computed from
     acquisition time + lat/lon via SPICE, which is out of scope for 12 days. **Do not let a
     "we handle illumination variation" claim about Chandrayaan-2 reach a slide unqualified.**
   - **The upside:** those 113,499 `(Pixel, Scan) → (Lon, Lat)` points ARE georeferencing. That is
     what will make `crop_to_overlap` work for CH-2, and it is the route to a real GSD/footprint.
   - ⚠️ **Trap:** the CSV header spells it **`Lattitude`** (two t's) while the label's own
     `<name>` element says `Latitude`. A parser keyed to the label will silently find nothing.

0c. **🔴 ROHAN'S ONLY IMAGE PRODUCT IS EMPTY. WE STILL HAVE NO USABLE LUNAR IMAGE.**
   *(Superseded for Samartha's purposes by 0d — a good CH-2 frame now exists locally. Rohan still
   needs terrain-bearing LROC frames for Tier A, and the check below still applies to every product
   he catalogues.)*
   `M108587604RE.IMG` decodes perfectly and shows nothing: 98.1% of pixels in DN 32–46, std 1.42
   over a 400×400 crop, 15 distinct DN values, no craters at any stretch. The only bright pixels in
   the entire frame are columns 5056 and 5057 — the NAC's masked reference columns, which is a
   detector artefact, not terrain. Its label fits: `RATIONALE_DESC = "TARGET OF OPPORTUNITY"`,
   `LINE_EXPOSURE_DURATION = 0.678933 ms`, only 1024 lines (a real imaging strip is tens of
   thousands). This is a short, dark, low-signal acquisition.
   **The loader is not at fault and is proven correct** — see the CORRECTION note under In flight.
   **Rohan needs to download a frame with actual terrain**, and the check is one line, before the
   product ever goes in the catalogue:
   `python -c "from core.io_loader import load; a,_=load('<file>'); print(a.std(), len(__import__('numpy').unique(a)))"`
   A std of ~1 and a handful of distinct values means an empty frame. Real terrain is std ≳ 10.
   Better still, look at it. **Every product entering `pairs_catalogue.csv` needs eyes on it once.**
   Confirmed against Rohan's own first product, `M108587604RE.IMG`, by reading its real label.
   The label has **no incidence angle, no sun azimuth, no sun elevation, no emission, no phase and
   no map scale** — 62 keywords, and not one of them is geometry. An EDR is raw: geometry needs
   SPICE, or a map-projected product.
   **Tier A is defined as "LROC NAC ↔ LROC NAC, same site, incidence differs ≥15°".** You cannot
   select pairs on an angle the file does not contain, and you cannot report the sun-angle result
   without it. **Rohan must switch to the map-projected RDR** — `00_CANONICAL_FACTS.md` §3 already
   lists it: ODE dataset `LRO-L-LROC-5-RDR-V1.0`, product type **`SDRPHO`**, georeferenced, no
   login — **or** pull incidence from ODE's product metadata / the CUMINDEX table alongside each
   EDR. Either is fine; picking neither means Tier A quietly has no numbers on Day 6.
   `io_loader` reports these as `None`, which is the honest answer and must not be filled in.

0a. **LROC NAC EDR mislabels its own signedness.** `SAMPLE_TYPE = LSB_INTEGER` at `SAMPLE_BITS = 8`
   is signed per PDS3, but the values are `UNIT = "RAW_INSTRUMENT_COUNT"`, unsigned DN 0..255. Read
   strictly, the real product returns range **[-107, 51]** — every pixel above DN 127 wrapped
   negative — on data whose own MD5 verifies. Corrected to **[32, 199]**. `io_loader` reinterprets
   only when unambiguous (8-bit, declared signed, negatives present) and sets
   `dn_signedness_corrected` in the metadata so it is never a silent fix.

0. **⚠️ THE BIG-ENDIAN TRAP — the worst thing found this session.** OpenCV 5.0.0.93 accepts a
   big-endian numpy array **without raising** and returns garbage. Measured max abs difference vs
   the identical native-order array: **34935**, and `3.99e-41` where `450.0` was expected in float32.
   LROC NAC EDR is `MSB_INTEGER`; PDS4 arrays are commonly `UnsignedMSB2`. **Both of our real
   sources are big-endian.** On Day 9 this would have presented as *"LoFTR finds no matches on real
   lunar data"* with no exception and nothing to grep for. `io_loader.as_cv_safe()` now normalises
   to native order + float32 before anything else sees the array; every `core/` module may assume
   this has happened. Related: `cv2.resize` cannot resize int32/uint32/int64 at all.
   **Second-order trap:** numpy arithmetic does **not** preserve byte order —
   `np.arange(n, dtype=">u2") * 37` returns a *native*-order array. This bit the test fixture for
   this very feature. Cast after the arithmetic, never before.

0b. **`imagecodecs` is NOT installed, and that is a sharper blocker than rasterio.** Without it
   `tifffile` cannot decode **LZW**, PACKBITS or JPEG2000 — and LZW is the commonest GeoTIFF
   compression, i.e. quite possibly Kaguya TC. **Resolved:** `io_loader` reads geo tags with
   tifffile and falls back to **Pillow** for the pixels. Verified — a Pillow-written LZW TIFF fails
   in tifffile and loads exactly through `io_loader`. DEFLATE and uncompressed work in tifffile
   directly. Do not `pip install imagecodecs` without re-pinning for all six people.
   Also: `tifffile.geotiff_metadata` returns **None** unless GeoKeyDirectoryTag (34735) is present,
   even when a valid pixel scale and tie point are. Read tags 33550/33922 by number instead.

1. **`rasterio` imports but its DLLs are blocked.** ✅ **DECIDED: go GDAL-free, do not fight it.**
   Smart App Control blocks **by content hash**; exactly one file is blocked; being unsigned is not
   the discriminator, and `Unblock-File` is irrelevant (different mechanism). Nothing that once
   loaded has ever become blocked, so this is not expected to move — but a **fresh `pip install`
   mints unrated hashes**, so nobody should install packages on demo morning or expect a teammate's
   machine to behave identically. **Cost, and it is real:** `/vsicurl` is gone, so the plan in
   `00_CANONICAL_FACTS.md` §3 / `ROHAN_DATA_GUIDE.md` to read Kaguya COGs over HTTP with
   `rasterio.open()` is dead — **Kaguya must be downloaded like everything else.** Tell Rohan.
   Exact error:
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
