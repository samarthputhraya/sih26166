# Day 6 handoffs — 4 Sep 2026

> Written by Samartha on Day 6 after `/next`. **Everything the trust layer produced is now pushed**
> (`ff2d8ec`) — pull before you start, or you are working against Day-4 code.
>
> **Read your own section only.** Each one names the exact command, the exact pitfall, and what
> "done" looks like. If a spec here does not run for you, that is my bug, not yours — message me
> and I fix it the same day. No one on this team should ever be stuck waiting on me.

---

## 🔴 RISHEETH — Gate 2 criterion 5. **The gate is tomorrow and this is the only open criterion.**

Gate 2 needs: *"≥2× better than the best of SIFT/ORB/AKAZE **on the same pair at the same
scale**."* Five of six criteria already pass on the log. This one has no evidence yet.

**Read this first — there are two traps, and I hit both before writing this.**

1. **`baselines/run_all_baselines.py` cannot see the sweep pairs.** `PAIRS_DIR` is
   `data/pairs/` (`baselines/run_all_baselines.py:67`); the sweep pairs live in
   `demo_cache/synthetic/`. Pointing it there is *not* enough, because —
2. **The comparison metric is `rmse_gt_px`, which needs the true homography**, and `H_true` is
   **not** stored beside the `.tif` files. It is regenerated with the pair. So the pairs must be
   **re-rendered in memory**, not loaded from disk.

**The template already exists and already works.** `evaluation/swept_azimuth_curve.py` does
exactly this for SIFT: `make_pair(...)` → `run_sift(u8(s), u8(r))` →
`evaluate(r.shape, src, ref, H_true=H_true)` → `log_result(...)`. Copy that shape into
`baselines/`, change two things: use **our** DEM and shifts (below) instead of its internal
`crater_dem()`, and run **all three** detectors.

**The exact parameters — these must match our run or it is not a comparison:**

```python
DEM = r"C:/Users/samar/sih26166_data/raw/dem_site_60m.npy"   # np.load, 2-D
pixel_size_m = 60.0 ;  max_size = 640      # crop dem[:640,:640] as core.pipeline does
sun_a = (45.0, 30.0)                       # SYNTH_REF_AZIMUTH, SYNTH_SUN_ELEVATION
sun_b = (45.0 + delta, 30.0)               # elevation FIXED - azimuth only
rotation_deg = 0.0 ;  scale = 1.0
for rep in range(5):
    shift = (12.37, -8.63) if rep == 0 else _draw_shift(0 + rep)   # core.pipeline._draw_shift
    seed  = 0 + rep
deltas = [0, 15, 30, 45]                   # the gate lives at <=15 deg
```

**Two things that will silently ruin the numbers:**

- **Hand `evaluate()` the RAW matches, before any RANSAC.** It fits on 80% and scores the 20% it
  never saw; pre-filtered points make `inlier_ratio` ask "of the points I kept, how many do I
  keep?" and it answers ~1.0. That bug already cost this project a week (Canonical Facts §7).
- **`make_pair` returns float [0,1]; SIFT/ORB/AKAZE need uint8.** Use the `u8()` helper from
  `swept_azimuth_curve.py`. Feeding [0,1] straight in returns near-zero matches, silently.

**Log with `log_result(..., allow_failed=True)`** — classical methods *will* fail at 30–45° and a
logged failure is evidence, not a problem. Set `notes` to name the delta and the shift.

**Done =** rows in `evaluation/results_log.csv` for SIFT, ORB and AKAZE at each of 0/15/30/45°,
and one sentence to me: *"best classical at 15° is X px; ours is 0.086 px; ratio Y×."*
**We need ratio ≥ 2 at 15° to pass.** If it is under 2, tell me tonight — that is a gate decision,
not a failure, and it is mine to make.

**If you cannot start this today, say so by 20:00** and I will run it from `ops/` (importing your
detectors, not editing your folder). No penalty — but silence past 20:00 costs us the gate.

---

## 🔴 SANIYA — two things, and the first one is an apology

**1. Your guide had the wrong dates and that is our fault.** `docs/SANIYA_NARRATIVE_GUIDE.md` was
written against a **12-day** schedule. The round is **9 Sep = Day 11**, so **there is no Day 12**,
and the old plan had you doing Rehearsal 3 and Gate 5 *the day after the hackathon*. It is
corrected now — pull and re-read the top of 📅 YOUR PLAN. **Your real remaining dates:**

| Day | Date | Yours |
|---|---|---|
| **6** | **today** | Slides 3, 5, 6 — these need **no** final numbers |
| 7 | 5 Sep | Slides 2, 4. Full deck draft. |
| 8 | 6 Sep | Deck v1 + numbers audit. **Q&A bank finished** (moved a day earlier). |
| 9 | 7 Sep | Demo script (3:00, all six speak). **Deck final** — code freezes. |
| 10 | 8 Sep | Rehearsals 1–3, backup video, **Gate 5**, final audit |
| 11 | 9 Sep | **THE ROUND** |

**2. Your work has been invisible, and that was also our bug.** `.gitignore` blocks `*.pptx`, and
your own guide tells you to keep the deck in Drive — so **nothing you build can show up in git**,
and a contingency had been written that would have read "failed" no matter how much you had done.
That criterion is rewritten.

**What to commit today, and it takes five minutes: `presentation/DECK_STATUS.md`** — a text file
(`presentation/` accepts text) with the **Drive link**, whether the official template is
downloaded, and a per-slide state for all six slides. Exact format is in your guide under
📁 YOUR FILES. **That file, not the `.pptx`, is how we see the deck exists.** If it says you are
blocked on something, clearing it is my job that same day.

Content for slides 3/5/6 is already written in your guide and `ops/briefs/BRIEF_SANIYA.md` — you
are transcribing, not inventing. ⚠️ One number in your brief changes today: see
`ops/MOVE2_FAILURE_DETECTION_DAY6.md` §5 for the figure that goes on the slide.

---

## 🔴 ROHAN — the Tier A decision is due **today**, and you are 2 days quiet

**1. Tier A: `cut` or `abandoned` — end of Day 6 (today).** `PLAN_TO_9_SEP.md` Part 6 put this on
you with today's date. It is a one-word decision plus a line in `data/pairs_catalogue.csv`. Tier A
is a *bonus* arm now, not a blocker — so "abandoned" is a completely acceptable answer and it
costs us nothing. What costs us is not knowing.

**2. `demo_cache/` must open with wifi off.** Gate 4 moved to **Day 9 (7 Sep)** — two days earlier
than your guide says. Every file under `demo_cache/` opens from a cold start, no network, and the
checksums recorded. If anything reaches for the network, I need to know before Day 9, not on it.

**3. Recruit the Gate 3 stranger — Gate 3 is now Day 8 (6 Sep), not Day 10.** Someone who has
never seen this project. Not a teammate, not a friend who has heard you talk about it. They
operate the UI while nobody speaks.

**You have not pushed since 2 Sep.** That is a Gate 5 risk more than a schedule risk: Gate 5 asks
you to explain your own module cold, and provenance is a genuinely strong answer — four missions,
every file with a URL, a date and a licence. Do not lose it by going quiet.

---

## RISHABH — one real bug, in your module, found in a browser

`ops/STATUS.md` known issue 9: on `pair_04_tierD_native`, **the UI reports 183 raw change
candidates where `python -m ops.gate_tier_d_changes` reports 1.** Same detector, same pair, two
numbers.

**Cause (diagnosed, not guessed):** the UI hands `detect_changes` images that have already been
`to_display()`-percentile-stretched to uint8; the ops script hands it **raw float32** and lets
`detect_changes` do its own max-based scaling. Different contrast in, different candidate count out.

**Yours to decide, because it is your module's contract:** either `detect_changes` normalises its
own input so the caller cannot change the answer (my preference — it makes the function honest on
its own), or it documents that it requires pre-stretched uint8 and the ops script is changed to
match. **Pick one and pin it with a test.** I will change `app/streamlit_app.py` to whatever you
decide — tell me which.

**The gate's conclusion is identical either way** (0 kept, because no cell is verified on that
pair), so no claim is at risk and **neither number is quoted anywhere in the deck**. But a judge
who tries both routes sees two numbers, and "which is right?" is not a question we want to answer
live. ~20 minutes.

---

## SAMRUDH — independent verification, which is the whole point of your role

Today's run extended the sun sweep to **8 deltas** (0/15/30/45/60/90/120/180) — 40 pairs, 2,560
cells. Results and reasoning: `ops/MOVE2_FAILURE_DETECTION_DAY6.md`.

**Verify it, do not take it from me.** Three specific things:

1. **The envelope figure** (§5): inside Δaz ≤ 30°, verified cells median **0.123 px, 99.0% under
   0.5 px, n=817**. Re-derive it from `core/reliability_calibration.csv` yourself. This is the
   number going on a slide, replacing the pooled 0.162 px we published on Day 5.
2. **The detection table** (§3): at a 120 m failure threshold, **77% detection, 0% false alarms**.
   Recompute from `pair_rmse_gt_px` and `global_contradicted`.
3. **The 180° result** (§2): 0.080 px, better than 30°. It is surprising and I want a second pair
   of eyes on whether it is real or an artifact of how `make_pair` renders a 180° flip.

**Also — six documents still quote the superseded Day-5 pooled figure** (0.162 px / 926 cells /
92% / 98%): `ops/briefs/BRIEF_SAMARTHA.md`, `BRIEF_SAMRUDH.md`, `BRIEF_SANIYA.md`,
`ops/PHASE1_NOVELTY_DECISION.md`, `ops/QA_ANSWERS.md`, `ops/STATUS.md`. They are still *traceable
and true* for the 20-pair population, so this is not a fire — but before the deck is built they
should point at the envelope figure. **List them; do not edit anyone's folder.**

If any of the three numbers does not reproduce, that is a finding and I want it tonight, not on
Day 8.
