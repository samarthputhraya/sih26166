# Rishabh — Application Lead Guide

**Role:** Change detection — show what changed between two aligned lunar images
**Time:** ~2 hrs/day | **The feature that answers "so what?"**

> Read `00_CANONICAL_FACTS.md` §7 (metrics) and §9 (numbers discipline) first.

---

## 🔴 FOUR CHANGES FROM THE OLD GUIDE

**1. You are no longer blocked on Day 1.** The old plan had you working on "Samrudh's synthetic
aligned pairs" on Day 2 — which he doesn't deliver until Day 3. **Now you make your own pair in
three lines and depend on nobody.**

**2. You now speak in the demo.** The old script had you silent for all three minutes while
Samartha demoed *your* feature — and then Gate 5 required you to answer for it cold. You have a
30-second slot at 2:30.

**3. The old code had bugs that would not run.** Listed inline below so you don't hit them.

**4. You need a real change to detect.** This is the big one — see immediately below.

---

## ⭐ THE PROBLEM NOBODY NOTICED: THE MOON DOESN'T CHANGE MUCH

The old guide assumed you'd have "two images of the same area taken weeks apart" showing "a new
crater, a rover track, landed equipment." **Over weeks, essentially nothing on the Moon changes.**
If you difference two real lunar images, ~100% of what lights up will be shadow movement and
registration error, not surface change. A judge who asks *"which of those is a real change?"* and
gets no answer has just destroyed the feature.

You need **three tiers of demonstration**, in this order of value:

### Tier 1 — A real, verifiable, famous change ⭐ ASK ROHAN FOR THIS ON DAY 1

**The Chandrayaan-3 landing site.** Vikram touched down near the lunar south pole in August 2023.
LROC NAC imaged that area **before and after** — and the lander is visible in the after image as a
bright object with a dark halo where the descent engines disturbed the regolith.

That is a genuine surface change, publicly documented, on an **Indian** mission, detectable by
exactly your algorithm. If you get nothing else, get this. An ISRO judge watching your software
autonomously locate Vikram in a before/after pair is the single best 20 seconds in the entire demo.

> [VERIFY with Rohan — he sources the two NAC product IDs covering the CH-3 site, pre- and
> post-August-2023. Search LROC QuickMap around the landing coordinates.]
>
> Related and worth knowing for Q&A: **Chandrayaan-2's own DFSAR radar imaged the Vikram lander
> after touchdown.** So this exact task — finding a lander in orbital imagery — is something
> Chandrayaan-2 has actually been used for.

### Tier 2 — A real new impact crater
LROC's team has published before/after pairs of newly formed impact craters. Same idea, less
narrative punch, still a genuine change.

### Tier 3 — Injected synthetic changes (your fallback and your test set)
Draw a shape into one image. **Always label it on screen as synthetic.** Fine for testing and for
demonstrating the mechanism; never present it as a discovery.

**Be explicit in the demo about which tier you are showing.** That honesty is worth more than the
feature.

---

## 🎯 YOUR MISSION

Given two **aligned** images, find what actually changed — and be trustworthy about what didn't.

The hard part is not finding differences. It is **rejecting the two things that dominate**:
- **shadow movement** (the sun was in a different place)
- **registration error** (the alignment isn't perfect)

Getting those two right is your whole job.

---

## 📅 YOUR 12-DAY PLAN

### DAY 1 — Working, dependent on nobody

```bash
pip install opencv-contrib-python numpy pandas pillow
```
(`python`, not `python3`, on Windows.)

**Make your own pair:**
```python
import cv2, numpy as np
img = cv2.imread("any_image.jpg", 0)
changed = img.copy()
cv2.circle(changed, (200, 150), 25, 255, -1)   # a "new" bright object
cv2.imwrite("my_before.png", img)
cv2.imwrite("my_after.png", changed)
# You know exactly what changed and where.
```

Also: **ask Rohan for the Chandrayaan-3 landing site pair today.** He needs lead time.

---

### DAYS 2–3 — The detector

`app/change_detection.py`:

```python
import cv2, numpy as np

def detect_changes(img_a, img_b, gsd_mpp=0.5,
                   thresh=30, min_area_px=50, edge_margin_frac=0.05):
    """img_a, img_b: aligned uint8 grayscale, same size.
    gsd_mpp: metres per pixel, from the pair catalogue.
    Returns (overlay_bgr, changes_list)."""

    if img_a.dtype != np.uint8: img_a = cv2.normalize(img_a, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if img_b.dtype != np.uint8: img_b = cv2.normalize(img_b, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if img_a.shape != img_b.shape:
        img_b = cv2.resize(img_b, (img_a.shape[1], img_a.shape[0]))

    diff   = cv2.absdiff(img_a, img_b)                 # uint8 in, uint8 out
    smooth = cv2.medianBlur(diff, 5)
    _, mask = cv2.threshold(smooth, thresh, 255, cv2.THRESH_BINARY)

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)

    h, w = mask.shape
    m = int(edge_margin_frac * min(h, w))
    mask[:m, :] = 0; mask[-m:, :] = 0; mask[:, :m] = 0; mask[:, -m:] = 0

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    overlay = cv2.cvtColor(img_a, cv2.COLOR_GRAY2BGR)
    changes = []

    for cnt in contours:
        area_px = cv2.contourArea(cnt)
        if area_px < min_area_px:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00']) if M['m00'] else x + bw//2
        cy = int(M['m01']/M['m00']) if M['m00'] else y + bh//2

        label, colour = classify(cnt, img_a, img_b, cx, cy)
        changes.append({
            "bbox": [x, y, bw, bh], "centroid_px": [cx, cy],
            "area_px": float(area_px),
            "area_m2": round(area_px * gsd_mpp**2, 2),
            "classification": label,
        })
        cv2.rectangle(overlay, (x, y), (x+bw, y+bh), colour, 2)
        cv2.putText(overlay, label, (x, max(y-6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1)

    return overlay, changes
```

> ⚠️ **Bugs in the old version, all of which would have stopped you:**
> - The signature said `img_a_aligned, img_b_aligned` but the body used `img_a, img_b` →
>   `NameError` on the first line.
> - It ran `cv2.absdiff` on `float32` then `cv2.medianBlur(...)` — **medianBlur with ksize 5
>   requires uint8**. Instant error.
> - `cv2.cvtColor(img_a, COLOR_GRAY2BGR)` on a float array gives a black overlay.
> - No dtype guard at all, and lunar products arrive as uint16 or float far more often than uint8.

---

### DAY 4 — The discriminator (your most important day)

Everything that lights up is one of four things. Label each one:

```python
def classify(cnt, img_a, img_b, cx, cy):
    """-> (label, BGR colour). Blunt heuristics, honestly described."""
    x, y, w, h = cv2.boundingRect(cnt)
    elong = max(w, h) / max(min(w, h), 1)
    a_val = int(img_a[cy, cx]); b_val = int(img_b[cy, cx])

    if elong > 4:
        return "shadow?",  (0, 200, 200)   # yellow - long thin = shadow displacement
    if b_val > a_val + 40:
        return "new bright", (0, 255, 0)   # green  - appeared
    if a_val > b_val + 40:
        return "disappeared", (255, 80, 0) # blue   - gone
    return "uncertain", (160, 160, 160)    # grey
```

**Say plainly what these are:** simple shape and intensity heuristics, not physics. Being able to
describe your own method's limits accurately is what Gate 5 is testing.

**The better shadow test, if you have time (Day 7):** you have the sun azimuth for both images in
Rohan's catalogue. A real shadow displacement is **elongated along the direction the sun moved**.
Compute the contour's principal axis with `cv2.fitEllipse` and compare its angle to the azimuth
difference. That is a genuinely defensible shadow filter rather than a shape guess — and it's a
great Q&A answer because it uses the mission metadata rather than a magic number.

---

### DAY 5 — Real units

`area_m2 = area_px × gsd_mpp²`, with `gsd_mpp` read from `data/pairs_catalogue.csv`.

**Never hardcode 0.5.** LROC NAC is ~0.5 m, OHRC is ~0.28 m, Kaguya TC is ~10 m. A hardcoded scale
gives an area wrong by three orders of magnitude on a Kaguya pair, and it will be wrong on screen
in front of a judge.

---

### DAY 6 — Run on real aligned output

Samartha's pipeline has produced real aligned pairs since Gate 1 (Day 5). Run on them.

**Expect a mess.** Most detections will be shadow and registration artifacts. **That is the honest
result and you must not hide it.** Count them, characterise them, report them.

---

### DAY 7 — Honest characterisation

For each real pair, record:

> "Pair 03: 47 regions above threshold. 2 plausible surface changes. 31 classified as shadow
> displacement. 14 at the edges of the overlap, consistent with residual registration error."

That paragraph is worth more to a judge than a clean-looking overlay. It shows you understand your
own output. Put it in `app/README.md`.

Also: improve the shadow filter using sun azimuth (Day 4 note above), if you have time.

---

### DAY 8 — Freeze the module

Fix the interface with Samartha and stop changing it:
```python
detect_changes(img_a, img_b, gsd_mpp) -> (overlay_bgr_uint8, changes_list_of_dicts)
```
No API server. **The old guide had you build a Flask/FastAPI endpoint** — that's a whole extra
process to launch, a port to conflict, and one more thing to crash at Gate 4. Streamlit imports
your function directly. **Delete `api.py` from your plan.**

---

### DAYS 9–10 — UI integration and polish

Samartha imports `detect_changes` into `streamlit_app.py`. You provide:
- the overlay image
- the region list for a `st.dataframe`
- a colour legend (green = appeared · blue = disappeared · yellow = probable shadow · grey = uncertain)

**Add a confidence column** so the table shows classification, not just boxes. And make sure the
legend is on screen — Gate 3 is a stranger reading your output with nobody speaking.

---

### DAYS 11–12 — Rehearse and Gate 5

**Your Gate 5 answers:**
- *"How do you know that's a real change and not a shadow?"* → "Three signals: shape elongation,
  intensity direction, and whether the elongation lines up with the sun-azimuth difference from
  the mission metadata. It's heuristic — I'd want a DEM to do it properly."
- *"How many of your detections are false positives?"* → **know the number.** Say it.
- *"Why does this matter?"* → "Registration on its own is infrastructure. This is what it enables:
  finding a lander, spotting a new impact, monitoring a site over time."
- *"What would you do with more time?"* → "Use the DEM to predict where shadows should fall at
  each image's sun angle and subtract them before differencing."

---

## 📁 YOUR FILES

```
app/
├── change_detection.py       # detect_changes() + classify()
├── test_change_detection.py  # injected changes are found; shadows are labelled
└── README.md                 # honest false-positive characterisation per pair
```
(No `api.py`. See Day 8.)

---

## 💡 TIPS

| Situation | What to do |
|---|---|
| `medianBlur` errors | Input must be uint8. Convert first — see the dtype guard. |
| Overlay comes out black | You passed a float image to `cvtColor`. Normalise to uint8 first. |
| Everything flags as changed | Images aren't aligned. Check with Samartha before touching thresholds. |
| Nothing flags | Lower `thresh` (30→20) and `min_area_px` (50→20). Also — the Moon really doesn't change much. |
| Half the frame lights up at the border | Overlap edge. Raise `edge_margin_frac`. |
| Don't know the pixel scale | `source_gsd_mpp` in `data/pairs_catalogue.csv`. Never hardcode. |
| Tempted to say "15 m² new impact" in the demo | **Only if the CSV says 15.** The old script had exactly that invented number. |
| Blocked > 30 min | Post in chat. |

---

## ✅ DELIVERABLES

- [ ] `change_detection.py` — `detect_changes(img_a, img_b, gsd_mpp)`, dtype-safe
- [ ] `classify()` — four labels with a colour each
- [ ] Works on injected synthetic changes (test passes)
- [ ] Works on real aligned pairs, with **honest false-positive counts written down**
- [ ] **Chandrayaan-3 landing site pair attempted** (with Rohan)
- [ ] Integrated in the UI: overlay + region table + legend
- [ ] Area in m² from the catalogue GSD, never hardcoded
- [ ] Your 30-second demo slot rehearsed

---

## 🗣️ WHAT TO SAY IN THE DEMO (30 seconds, at 2:30)

**If you get the Chandrayaan-3 pair:**
> "Alignment is infrastructure — this is what it's for. These are two LROC images of the
> Chandrayaan-3 landing site, before and after August 2023. Once our pipeline aligns them, the
> difference is unambiguous: Vikram, plus the dark halo where the descent engines disturbed the
> regolith. Our detector finds it automatically and reports its area from the mission's own
> metres-per-pixel. The yellow boxes are shadow displacement, which we flag separately — on the
> Moon most apparent change is just the sun having moved."

**If you don't:**
> "Alignment is infrastructure — this is what it's for. Two aligned images, and we highlight what
> differs. Green is new, blue is gone, yellow is probable shadow displacement — because on the
> Moon most apparent change is just the sun having moved, and saying so is the difference between
> a monitoring tool and a noise generator. Areas come from the mission's own metres-per-pixel.
> We're honest that some detections are registration artifacts; on this pair there were [N]."

**Fill `[N]` from your own notes.** Never guess it.

---

## 📞 ESCALATION

| Problem | Ask |
|---|---|
| Aligned pairs | Samartha |
| **Chandrayaan-3 landing site imagery** | **Rohan — ask on Day 1** |
| Test pairs with known changes | Samrudh |
| Pixel scale | `pairs_catalogue.csv`, then Rohan |
| UI integration | Samartha |
| Which change to feature | Saniya + Samartha |

---

**Keep it visual, keep it simple, and be honest about the false positives.** A judge who catches
you overselling a shadow as a discovery stops believing the rest of the demo. A judge who hears you
volunteer your own error rate starts believing all of it.
