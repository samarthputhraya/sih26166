"""Build the deck's figures from the evidence files. No number is typed in here.

    python -m presentation.make_figures

Writes presentation/figures/*.png at 200 dpi, sized for a projected slide.

Invariant 1 applies to pictures as much as to sentences: every value plotted is read
back out of `evaluation/results_log.csv`, `core/reliability_calibration.csv` or the
cached `run_all()` result dicts in `demo_cache/results/` at run time. If a figure and a
slide ever disagree, re-run this - do not edit the picture.

Four figures:
  fig1_sun_angle_vs_error   ours vs best classical across the sun-azimuth sweep
  fig2_trust_calibration    do the three trust states separate by TRUE error?
  fig3_trust_map            the actual output: two real pairs, one accepted, one refused
  fig4_pipeline             the method as a flowchart (drawn here so it cannot drift from
                            what core/pipeline.py does; there is no hand-drawn diagram)

Colour: slots 1/2/3 of the validated categorical palette (blue #2a78d6, orange #eb6834,
aqua #1baf7a). Checked with the palette validator - all six checks pass; aqua's 2.74:1
contrast against the surface carries a WARN, which is discharged here by direct labels
on every series, so identity is never colour-alone. Marker shape is a second encoding
for the same reason. fig3 uses the demo UI's own three KINDS of mark (tint / hatch /
fade) for the three states, so the picture on the slide is the picture in the app.
"""
from __future__ import annotations

import csv
import pathlib
import pickle
import re
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "evaluation" / "results_log.csv"
CELLS = ROOT / "core" / "reliability_calibration.csv"
CACHE = ROOT / "demo_cache" / "results"
OUT = ROOT / "presentation" / "figures"

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1a1a1a", "#5c5c5c", "#d8d8d6"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    # White, not SURFACE. The slides are white, and a #fcfcfb ground drew a faint grey
    # rectangle around every chart - visible in a real PowerPoint render. SURFACE is kept
    # for marker halos, where it only has to separate a marker from the line under it.
    "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff",
    "font.size": 13, "axes.labelsize": 14, "axes.titlesize": 16,
    "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
})


# Figure name -> (canvas width in inches, the font sizes actually used in it). A figure
# drawn 10 in wide and placed 5.5 in wide on the slide HALVES every point size in it, and
# that is invisible while you are looking at the .png. The first build shipped chart axis
# labels at 7.7 pt and footnotes at 4.5 pt beside 14 pt body text. main() turns this into a
# report, so legibility is a number rather than an impression.
FONT_PT: dict[str, tuple[float, list[float]]] = {}


def _audit(fig, name):
    """Record the font sizes used, and report any text that runs off the canvas.

    Enlarging type inside a smaller canvas is exactly how a title ends up reading
    "...illumination chang". Measured, not eyeballed - the same rule as `_overflows`.
    """
    import matplotlib.text as mtext
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    w_px, h_px = fig.get_figwidth() * fig.dpi, fig.get_figheight() * fig.dpi
    # Matplotlib keeps a Text artist for every tick it MIGHT draw, including ones outside
    # the current limits - they report positions far off the canvas and are never rendered.
    # Their sizes still count towards legibility; their positions must not be checked.
    # The whole tick POOL, not just the labels currently placed: matplotlib keeps spare
    # Tick objects for locations outside the view, and they all report the same degenerate
    # box, which made every tick look like it overlapped every other one.
    ticks = set()
    for ax in fig.get_axes():
        for axis in (ax.xaxis, ax.yaxis):
            for tk in list(axis.majorTicks) + list(axis.minorTicks):
                ticks.add(id(tk.label1))
                ticks.add(id(tk.label2))
            ticks.add(id(axis.offsetText))
    sizes, boxes = [], []
    for t in fig.findobj(mtext.Text):
        if not t.get_text().strip():
            continue
        sizes.append(round(t.get_fontsize(), 1))
        if id(t) in ticks:
            continue
        bb = t.get_window_extent(renderer=r)
        if bb.x0 < -1 or bb.x1 > w_px + 1 or bb.y0 < -1 or bb.y1 > h_px + 1:
            print(f"    !! {name}: {t.get_text().splitlines()[0][:44]!r} runs off the canvas "
                  f"(x {bb.x0 / fig.dpi:.2f}..{bb.x1 / fig.dpi:.2f} in, canvas "
                  f"{w_px / fig.dpi:.2f} in)")
        boxes.append((t, bb))
    # Text printing through other text. Neither of the other checks sees this - both these
    # labels are inside the canvas and inside their own boxes - yet it is how the stacked
    # trust map first rendered its title across "Chandrayaan-2 OHRC · 0.23 m/px", and how
    # the sun-angle chart put "Gate 2 threshold" on top of "ours".
    for i, (t1, b1) in enumerate(boxes):
        for t2, b2 in boxes[i + 1:]:
            ov = (max(0.0, min(b1.x1, b2.x1) - max(b1.x0, b2.x0))
                  * max(0.0, min(b1.y1, b2.y1) - max(b1.y0, b2.y0)))
            smaller = min(b1.width * b1.height, b2.width * b2.height)
            if smaller > 0 and ov / smaller > 0.20:
                print(f"    !! {name}: {t1.get_text().splitlines()[0][:30]!r} overlaps "
                      f"{t2.get_text().splitlines()[0][:30]!r} "
                      f"({ov / smaller * 100:.0f}% of the smaller label)")
    FONT_PT[name] = (fig.get_figwidth(), sorted(set(sizes)))


def _rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def _delta(r):
    m = re.search(r"d_azimuth=(-?[\d.]+)deg", r.get("config") or "")
    return float(m.group(1)) if m else None


def load_curves():
    """Per sun delta: our median, the best classical median, and HOW MANY classical runs scored.

    The n matters and is not decoration. A classical run that fails produces no `rmse_gt_px`
    and so cannot enter a median - correct - but the first version of this figure then
    captioned the survivors' median "median of 5 off-grid shifts". At 180 deg exactly ONE of
    fifteen classical runs scored; that "median of five" was a median of one, and it reached
    the deck, the Q&A bank and the gate evidence. The success rate is returned alongside so
    the plot can show what actually happened: past 30 deg the classical arm mostly returns no
    usable answer at all, which is a stronger result than any median.
    """
    ours, cls, attempts = {}, {}, {}
    for r in _rows(LOG):
        d, v = _delta(r), r.get("rmse_gt_px")
        if d is None:
            continue
        scored = bool(v) and v != "None"
        if r.get("method") == "ours_loftr+subpixel":
            if scored:
                ours.setdefault(d, []).append(float(v))
        elif (r.get("method") in ("SIFT", "ORB", "AKAZE")
              and "GATE 2 CRITERION 5" in (r.get("notes") or "")):
            attempts[d] = attempts.get(d, 0) + 1
            if scored:
                cls.setdefault((d, r["method"]), []).append(float(v))
    deltas = sorted(ours)
    o = [st.median(ours[d]) for d in deltas]
    best, nscored, ntried = [], [], []
    for d in deltas:
        per = [st.median(cls[(d, m)]) for m in ("SIFT", "ORB", "AKAZE") if (d, m) in cls]
        best.append(min(per) if per else np.nan)
        nscored.append(sum(len(v) for k, v in cls.items() if k[0] == d))
        ntried.append(attempts.get(d, 0))
    return deltas, o, best, nscored, ntried


def fig_sun_angle(deltas, ours, best, nscored, ntried):
    """Ours vs the best classical baseline across the sun sweep.

    Sized for a 5.5 in slot on the slide (see SLOT_IN): a 7.6 in canvas means everything
    here is multiplied by 0.72 on the slide, not by 0.55 as in the first build, where the
    axis labels landed at 7.7 pt beside 14 pt body text. The legend is gone - both series
    carry a direct label - and two of the three annotations are gone, because the 0° loss
    and the 2.88× are already bullets on the same slide. `main()` prints the resulting
    on-slide point sizes.
    """
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.set_yscale("log")
    ax.grid(True, which="major", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=14)

    # The threshold line is labelled in the footer, not in the plot. Every in-plot position
    # tried for it collided with something: at the left edge with the "15/15" count, in the
    # middle with the "ours" label, at the right with our own descending curve.
    ax.axhline(0.5, color=MUTED, linewidth=1.3, linestyle=(0, (5, 4)), zorder=1)

    ax.plot(deltas, best, color=ORANGE, linewidth=2.4, marker="s", markersize=10,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=3)
    ax.plot(deltas, ours, color=BLUE, linewidth=2.4, marker="o", markersize=10,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)

    # Direct labels, each in a region both curves and both sets of counts leave empty: the
    # classical label above everything at the left, ours in the gap between our own curve
    # and the threshold line. A legend box at this type size overlapped the "1/15" counts.
    ax.text(4, 33000, "best of SIFT / ORB / AKAZE", color=ORANGE,
            fontsize=14, fontweight="bold", ha="left", va="center")
    ax.text(100, 0.9, "ours", color=BLUE, fontsize=16, fontweight="bold",
            ha="left", va="center")

    # One annotation, for the result that looks like a bug and is not. It lives in the
    # empty strip below every plotted point.
    ax.annotate("180°: shading inverts; gradient\norientation is invariant to it.",
                xy=(180, ours[-1]), xytext=(92, 0.0085),
                color=INK, fontsize=12, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1))

    # How many classical runs actually produced a scoreable transform. Past 30 deg most
    # produce none, and the orange point is then one or two survivors - NOT a median of 15.
    # Printing this on the figure is what stops the number being miscaptioned downstream.
    for x, b, ns, nt in zip(deltas, best, nscored, ntried):
        if np.isfinite(b):
            ax.annotate(f"{ns}/{nt}", xy=(x, b), xytext=(0, 12), textcoords="offset points",
                        ha="center", va="bottom", fontsize=12, color=ORANGE, zorder=5)

    ax.set_xlabel("sun-azimuth difference  (degrees)", fontsize=15)
    ax.set_ylabel("median error vs known truth\nrmse_gt_px  (reference px)", fontsize=14)
    ax.set_title("Registration error vs illumination change",
                 pad=10, loc="left", fontweight="bold", fontsize=17)
    ax.set_xticks(deltas)
    ax.set_xlim(-8, 190)
    ax.set_ylim(0.007, 60000)
    # Two footer lines at 10.5 pt in a 4.4 in canvas need 0.146 in of height each; at
    # y=0.032 and y=0.008 they only had 0.106 in between them and printed into each other.
    fig.text(0.014, 0.044, "dashed line = Gate 2 threshold 0.5 px · n/15 = classical runs "
             "that scored", fontsize=10, color=MUTED)
    fig.text(0.014, 0.006, "40 pairs, exact ground truth · 60 m/px · "
             "evaluation/results_log.csv", fontsize=10, color=MUTED)
    fig.tight_layout(rect=(0, 0.070, 1, 1))
    p = OUT / "fig1_sun_angle_vs_error.png"
    _audit(fig, p.name)
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def fig_trust_calibration():
    """Do the three trust states actually separate by true error? Envelope only."""
    by_state = {"verified": [], "weak": [], "no_evidence": []}
    for r in _rows(CELLS):
        if float(r["sun_delta_deg"]) > 30:      # the envelope we claim
            continue
        v = r.get("true_error_px")
        if r["state"] in by_state and v not in ("", "None", None):
            by_state[r["state"]].append(float(v))

    fig, ax = plt.subplots(figsize=(7.6, 4.4))     # see fig_sun_angle: sized for the slot
    ax.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xscale("log")
    ax.tick_params(labelsize=14)

    style = [("verified", BLUE, "o"), ("weak", ORANGE, "s"), ("no_evidence", AQUA, "^")]
    label_for = {"verified": "verified", "weak": "weak", "no_evidence": "no evidence"}
    for state, colour, marker in style:
        vals = np.sort(np.array(by_state[state]))
        if vals.size == 0:
            continue
        y = np.arange(1, vals.size + 1) / vals.size
        ax.plot(vals, y, color=colour, linewidth=2.4, zorder=3)
        # one marker per series, at the median - identity without a dot on every point
        mi = int(0.5 * vals.size)
        ax.plot([vals[mi]], [y[mi]], color=colour, marker=marker, markersize=11,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)

    ax.axvline(0.5, color=MUTED, linewidth=1.3, linestyle=(0, (5, 4)), zorder=1)
    ax.text(0.56, 0.03, "half a pixel = 30 m", color=MUTED, fontsize=12, ha="left")

    v = np.array(by_state["verified"])
    frac = float((v < 0.5).mean())
    ax.annotate(f"{frac*100:.1f}% of verified cells\nare under half a pixel",
                xy=(0.5, frac), xytext=(0.0105, 0.72), color=INK, fontsize=13,
                arrowprops=dict(arrowstyle="->", color=MUTED, linewidth=1.2))

    # Direct labels carrying the n, so no legend box is needed - the legend was landing on
    # top of the "no evidence" label and the half-pixel note. Each rides its OWN curve at a
    # DIFFERENT height, because at one shared y "weak" and "no evidence" overlapped: their
    # medians are 0.17 px apart, a few pixels on a log axis.
    for (state, colour, _), y_at in zip(style, (0.62, 0.42, 0.22)):
        vals = np.sort(np.array(by_state[state]))
        if vals.size == 0:
            continue
        x_at = float(np.interp(y_at, np.arange(1, vals.size + 1) / vals.size, vals))
        ax.text(x_at * 1.16, y_at, f"{label_for[state]}  n={vals.size}", color=colour,
                fontsize=13, fontweight="bold", ha="left", va="center")

    ax.set_xlabel("true error of the cell vs known truth  (reference px)", fontsize=15)
    ax.set_ylabel("fraction of cells at or\nbelow that error", fontsize=14)
    ax.set_title("Trust states separate by true error  (≤ 30° sun)",
                 pad=10, loc="left", fontweight="bold", fontsize=16)
    ax.set_xlim(0.008, 12)
    ax.set_ylim(0, 1.02)
    fig.text(0.014, 0.012, "8×8 cells over 15 pairs · 60 m/px · "
             "core/reliability_calibration.csv", fontsize=10.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.038, 1, 1))
    p = OUT / "fig2_trust_calibration.png"
    _audit(fig, p.name)
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# --- fig3: the output itself -------------------------------------------------
#
# The three states are drawn exactly as app/streamlit_app.py draws them (its
# `reliability_overlay`): verified = green tint + solid border + "V", weak = orange
# tint + 45-degree hatch + dashed border + "W", no evidence = faded toward paper +
# dotted border + "-". Three KINDS of mark, so the state survives a projector, a
# photograph and a colour-blind viewer. The app is not imported here because it
# runs Streamlit at import time; the constants are copied and a test can pin them.

VERIFIED, WEAK, NO_EVIDENCE = "verified", "weak", "no_evidence"
PAPER = (247, 247, 244)
STATE_TINT = {VERIFIED: (20, 107, 60), WEAK: (168, 86, 10), NO_EVIDENCE: None}
STATE_ALPHA = {VERIFIED: 0.25, WEAK: 0.36, NO_EVIDENCE: 0.0}
STATE_FADE = {VERIFIED: 0.0, WEAK: 0.0, NO_EVIDENCE: 0.45}
STATE_GLYPH = {VERIFIED: "V", WEAK: "W", NO_EVIDENCE: "-"}
STATE_WORD = {VERIFIED: "verified", WEAK: "weak", NO_EVIDENCE: "no evidence"}
HATCH_PERIOD = 8


def _to_u8(img) -> np.ndarray:
    """2nd-98th percentile stretch, the same rule as the app's `to_display`. Display only."""
    a = np.asarray(img, dtype=np.float64)
    finite = a[np.isfinite(a)]
    lo, hi = np.percentile(finite, [2, 98])
    if hi <= lo:
        lo, hi = float(finite.min()), float(finite.max())
    a = np.nan_to_num(a, nan=lo, posinf=hi, neginf=lo)
    return np.clip((a - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8)


def _overlay(base_u8: np.ndarray, state: np.ndarray) -> np.ndarray:
    """Port of app.streamlit_app.reliability_overlay - same marks, same constants."""
    h, w = base_u8.shape[:2]
    rgb = np.stack([base_u8] * 3, axis=-1).astype(np.float32)
    g = state.shape[0]
    rows = np.linspace(0, h, g + 1).astype(int)
    cols = np.linspace(0, w, g + 1).astype(int)
    paper = np.array(PAPER, np.float32)
    glyphs = []
    for r in range(g):
        for c in range(state.shape[1]):
            s = str(state[r, c])
            block = rgb[rows[r]:rows[r + 1], cols[c]:cols[c + 1]]
            bh, bw = block.shape[:2]
            if bh == 0 or bw == 0:
                continue
            yy, xx = np.mgrid[0:bh, 0:bw]
            tint, alpha = STATE_TINT.get(s), STATE_ALPHA.get(s, 0.0)
            if tint is not None and alpha > 0:
                block[:] = (1.0 - alpha) * block + alpha * np.array(tint, np.float32)
            fade = STATE_FADE.get(s, 0.0)
            if fade > 0:
                block[:] = (1.0 - fade) * block + fade * paper
            if s == WEAK:
                block[((xx + yy) % HATCH_PERIOD) < 2] *= 0.60
            t = 1 if s == NO_EVIDENCE else int(max(1, min(3, min(bh, bw) // 16)))
            on_h = (yy < t) | (yy >= bh - t)
            on_v = (xx < t) | (xx >= bw - t)
            edge = on_h | on_v
            along = np.where(on_h, xx, yy)
            if s == VERIFIED:
                mask = edge
            elif s == WEAK:
                mask = edge & ((along % 12) < 7)
            else:
                mask = edge & ((along % 8) < 2)
            colour = np.array(tint if tint is not None else (98, 102, 109), np.float32)
            block[mask] = colour
            block[:1, :] = 30
            block[:, :1] = 30
            glyphs.append((STATE_GLYPH.get(s, "?"), int(cols[c]), int(rows[r]), int(bh)))
    out = np.clip(rgb, 0, 255).astype(np.uint8)
    try:
        import cv2
    except ImportError:          # tint + hatch + border still carry the state
        return out
    for text, x0, y0, bh in glyphs:
        if bh < 16:
            continue
        scale = bh / 95.0
        thick = max(1, int(round(scale * 1.6)))
        (_tw, th), _base = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, thick)
        org = (x0 + 6, y0 + 6 + th)
        cv2.putText(out, text, org, cv2.FONT_HERSHEY_DUPLEX, scale, (20, 23, 26), thick + 2,
                    cv2.LINE_AA)
        cv2.putText(out, text, org, cv2.FONT_HERSHEY_DUPLEX, scale, (255, 255, 255), thick,
                    cv2.LINE_AA)
    return out


def _cached(pair: str) -> dict:
    p = CACHE / f"{pair}.pkl"
    if not p.is_file():
        raise SystemExit(f"  {p} missing - run `python -m ops.precompute_demo_cache {pair}` first")
    with open(p, "rb") as f:
        return pickle.load(f)


def _reference_image(result: dict, pair: str) -> np.ndarray:
    """The reference frame the trust map is drawn on, loaded through core.io_loader."""
    sys.path.insert(0, str(ROOT))
    from core.io_loader import load  # noqa: E402  (the same loader run_all() used)
    ref = pathlib.Path(result["reference"])
    if not ref.is_file():            # the cache stores an absolute path from another machine
        cands = sorted((ROOT / "data" / "pairs" / pair).glob("*ref*.tif"))
        if not cands:
            raise SystemExit(f"  reference image for {pair} not found")
        ref = cands[0]
    img, _meta = load(ref)
    return img


def fig_trust_map():
    """Two real pairs through the SAME code path: one the system accepts, one it refuses.

    Left: pair_01 - two overlapping 640x640 crops of one real Chandrayaan-2 OHRC frame,
    known offset, zero sun difference. NOT a validation tier (its PROVENANCE.md says so);
    it is here because it is a real OHRC picture and the map is genuinely almost all
    verified. Right: pair_04_tierD_native - a Kaguya TC photograph against a LOLA
    elevation hillshade rendered on the Kaguya grid: the one multi-modal pair we own,
    where the matcher's homography is contradicted by the pixels and the system says so.
    Every count and every metre on this figure is read from the cached result dict.
    """
    # STACKED, not side by side. Slide 2 answers four template pointers, so its text needs
    # width; a wide two-panel figure left the column 5% too narrow whatever was trimmed.
    # Stacked, the same two panels occupy 3.6 in instead of 5.5 in and are TALLER, so they
    # read at least as well - and the text column gains 1.4 in.
    panels = [
        ("pair_01",
         "Chandrayaan-2 OHRC · 0.23 m/px",
         "two crops of one real frame"),
        ("pair_04_tierD_native",
         "Kaguya TC vs LOLA elevation · 9.4 m/px",
         "optical ↔ elevation"),
    ]
    fig = plt.figure(figsize=(5.0, 7.2))
    # top leaves room for a TWO-LINE suptitle plus the first panel's own two-line title;
    # at 0.925 the suptitle printed straight through "Chandrayaan-2 OHRC · 0.23 m/px".
    gs = fig.add_gridspec(3, 1, height_ratios=(1, 1, 0.30), hspace=0.60,
                          left=0.02, right=0.98, top=0.872, bottom=0.045)
    for row, (pair, what, how) in enumerate(panels):
        r = _cached(pair)
        rel = r["reliability"]
        base = _to_u8(_reference_image(r, pair))
        img = _overlay(base, np.asarray(rel["state"]))
        ax = fig.add_subplot(gs[row, 0])
        ax.imshow(img, interpolation="bilinear")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(f"{what}\n{how}", fontsize=11, loc="left", pad=4, color=INK)
        counts, n_cells = rel["counts"], int(rel["n_cells"])
        if r["declared"]["contradicted"]:
            fb = r["fallback"] or {}
            # "0 of 64 verified" is the OUTPUT; the verdict comes from the cells the area
            # check could score. An arrow between them implied a causality that does not
            # hold, and the slide text names the other denominator - so state the count,
            # then the verdict, rather than deriving one from the other.
            verdict = (f"{counts['verified']} of {n_cells} cells verified\n"
                       f"CONTRADICTED — refused, fallback "
                       f"{fb['shift_m']:.0f} m ± {fb['spread_m']:.0f} m")
            colour = ORANGE
        else:
            verdict = (f"{counts['verified']} of {n_cells} cells verified, "
                       f"{counts['weak']} weak → accepted")
            colour = "#146b3c"
        ax.set_xlabel(verdict, fontsize=12, fontweight="bold", color=colour, labelpad=4)

    # Legend: the same three marks the app draws, on a flat grey swatch, produced by the
    # same overlay function - so the key cannot disagree with the picture. Three ROWS, not
    # three columns: a 5 in canvas gives each column 1.7 in, too narrow for the glosses.
    leg = fig.add_subplot(gs[2, 0])
    leg.set_xlim(0, 1)
    leg.set_ylim(0, 3)
    leg.axis("off")
    words = {VERIFIED: ("verified", "matches + pixels agree"),
             WEAK: ("weak", "measured, does not hold"),
             NO_EVIDENCE: ("no evidence", "unmeasured, never guessed")}
    for i, s in enumerate((VERIFIED, WEAK, NO_EVIDENCE)):
        sw = _overlay(np.full((64, 64), 150, np.uint8), np.array([[s]]))
        ins = leg.inset_axes([0.005, (2 - i) / 3 + 0.035, 0.062, 0.26])   # axes fraction
        ins.imshow(sw)
        ins.axis("off")
        head, gloss = words[s]
        leg.text(0.095, 2.5 - i, f"{head} — {gloss}", fontsize=11, va="center",
                 color=INK)                                               # data units
    fig.text(0.02, 0.008, "8×8 cells on the reference grid · rows in "
             "evaluation/results_log.csv", fontsize=9, color=MUTED)
    fig.suptitle("The trust map: one the system\naccepts, one it refuses",
                 x=0.02, ha="left", fontsize=14, fontweight="bold", y=0.995,
                 va="top", linespacing=1.2)
    # JPEG, not PNG: the panels are photographs, and the PNG was 1.5 MB - a third of the
    # deck. The portal wants a PDF under its size cap and a judge's laptop wants it fast.
    p = OUT / "fig3_trust_map.jpg"
    _audit(fig, p.name)
    fig.savefig(p, dpi=200, pil_kwargs={"quality": 88})
    plt.close(fig)
    return p


# --- fig4: the method as a flowchart ----------------------------------------

def _box(ax, x, y, w, h, text, face, edge, fs=11.5, bold=False, colour=INK, radius=0.10):
    """Draw a rounded box with centred text; return (text artist, box rect) for _overflows."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                                facecolor=face, edgecolor=edge, linewidth=1.6, zorder=2))
    t = ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else "normal", color=colour, zorder=3,
                linespacing=1.25)
    return t, (x, y, w, h)


def _arrow(ax, x0, y0, x1, y1, colour=MUTED):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=15,
                                 linewidth=1.6, color=colour, zorder=1,
                                 shrinkA=0, shrinkB=0))


def _overflows(fig, ax, placed):
    """Which labels stick out of their own box, measured rather than estimated.

    Matplotlib does not wrap or shrink text to fit a patch, so a label wider than its box
    simply prints through the border. That is how the first build of this figure shipped
    with the area-check sentence running past its right edge and the incoming arrowhead
    landing on the word "reference". Never eyeball this; the numbers are below.
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    bad = []
    for t, (x, y, w, h) in placed:
        bb = t.get_window_extent(renderer=r)
        (x0, y0), (x1, y1) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
        if x0 < x - 0.02 or x1 > x + w + 0.02 or y0 < y - 0.02 or y1 > y + h + 0.02:
            bad.append(f"{t.get_text().splitlines()[0][:40]!r} needs "
                       f"{x1 - x0:.2f} x {y1 - y0:.2f} in, box is {w:.2f} x {h:.2f} in")
    return bad


def fig_pipeline():
    """core/pipeline.py run_all(), in the order it runs. Text only; every box is a function.

    Vertical budget of the 3.40 in canvas, top to bottom: step row 2.36-3.32 · area check
    1.14-1.88 · outcomes 0.10-0.92. Nothing shares a band, which is the fix for the first
    build, where two italic captions were drawn at y=3.42 with va="top" and printed
    straight down into the step boxes whose tops were at 3.40.

    Those captions ("core/pipeline.py · run_all(), in execution order" and "CPU only · no
    GPU · fully offline") are gone entirely. In grey italic directly under the template's
    grey italic pointer text they read as more pointer text, and both duplicated content
    that is already on the slide - the second is a bold bullet in the right-hand column.

    Saved with a transparent ground: on a white slide the figure's own off-white surface
    read as an unintended grey panel behind the diagram.
    """
    fig, ax = plt.subplots(figsize=(13, 3.40))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 3.40)
    ax.axis("off")
    placed = []

    steps = [
        "Input pair\nCH-2 optical +\nlunar reference",
        "Common-GSD\nresample\n(scale invariance)",
        "Illumination\nnormalisation\n(gradient orientation)",
        "LoFTR\ndense matching\n(detector-free)",
        "MAGSAC++\noutlier rejection",
        "Sub-pixel NCC\nrefinement",
        "8×8 distribution\ncheck\n(coverage, CV)",
    ]
    n, w, gap, h, y = len(steps), 1.74, 0.12, 0.96, 2.36
    x0 = (13 - (n * w + (n - 1) * gap)) / 2
    for i, text in enumerate(steps):
        x = x0 + i * (w + gap)
        placed.append(_box(ax, x, y, w, h, text, "#eef3fa", BLUE, fs=10))
        if i:
            _arrow(ax, x - gap, y + h / 2, x, y + h / 2)

    # The part that is ours: a check that never sees a match. The box spans nearly the full
    # width so the last step can drop straight into it - the earlier narrow box forced a
    # dogleg whose arrowhead landed on the text.
    cx, cw, cy, ch = 0.60, 11.80, 1.14, 0.74
    placed.append(_box(ax, cx, cy, cw, ch,
                       "INDEPENDENT AREA CHECK — cross-correlates the raw pixels of every "
                       "cell against the reference.\nNever sees a match. The cells vote on "
                       "the matcher's transform.",
                       "#fdeee6", ORANGE, fs=10.8, bold=True, colour="#8a3d10"))
    last_x = x0 + (n - 1) * (w + gap) + w / 2
    _arrow(ax, last_x, y, last_x, cy + ch)

    # Two outcomes, and the second one is the point.
    oy, oh = 0.10, 0.82
    placed.append(_box(ax, 0.60, oy, 5.80, oh,
                       "agrees →  aligned image + trust map: verified / weak / no evidence\n"
                       "RMSE, inlier count, inlier ratio, grid coverage, distribution CV",
                       "#e9f5ee", "#146b3c", fs=10, colour="#0f4d2b"))
    placed.append(_box(ax, 6.60, oy, 5.80, oh,
                       "contradicted →  declared, matcher output REFUSED\n"
                       "phase-correlation fallback · uncertainty reported in metres",
                       "#fdeee6", ORANGE, fs=10, colour="#8a3d10"))
    _arrow(ax, cx + cw * 0.30, cy, 3.50, oy + oh, colour="#146b3c")
    _arrow(ax, cx + cw * 0.70, cy, 9.50, oy + oh, colour=ORANGE)

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    for line in _overflows(fig, ax, placed):
        print(f"    !! fig4 label overflows its box: {line}")
    p = OUT / "fig4_pipeline.png"
    _audit(fig, p.name)
    fig.savefig(p, dpi=200, transparent=True)
    plt.close(fig)
    return p


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    deltas, ours, best, nscored, ntried = load_curves()
    print(f"  read {len(deltas)} sun deltas from {LOG.name}")
    for d, o, b, ns, nt in zip(deltas, ours, best, nscored, ntried):
        ratio = (b / o) if (o and np.isfinite(b)) else float("nan")
        print(f"    {int(d):>4}°  ours {o:9.3f}   best classical {b:11.3f} "
              f"(from {ns}/{nt} scoreable runs)   {ratio:9.2f}x")
    print(f"  wrote {fig_sun_angle(deltas, ours, best, nscored, ntried).name}")
    print(f"  wrote {fig_trust_calibration().name}")
    print(f"  wrote {fig_trust_map().name}")
    print(f"  wrote {fig_pipeline().name}")
    _report_slide_legibility()
    return 0


def _report_slide_legibility():
    """What size is the text in these figures once the deck shrinks them onto a slide?

    Read the placed widths from build_deck so there is one source of truth. Body text on
    the content slides is 13-14.5 pt; anything here under ~9 pt is smaller than the prose
    beside it, and under 6 pt a projector will not carry it at all.
    """
    try:
        from presentation.build_deck import SLIDES as DECK
    except Exception as exc:                                # noqa: BLE001
        print(f"  (could not read placed widths from build_deck: {exc})")
        return
    placed = {s["fig"][0]: s["fig"][2] for s in DECK.values() if "fig" in s}
    print("  on-slide font sizes (figure pt x placed width / canvas width):")
    for name, (canvas_w, sizes) in FONT_PT.items():
        w = placed.get(name)
        if w is None:
            continue
        s = w / canvas_w
        lo, hi = min(sizes) * s, max(sizes) * s
        flag = "  <-- BELOW 6 pt, a projector will not carry it" if lo < 6 else ""
        print(f"    {name:28s} {canvas_w:5.2f} in -> {w:.2f} in  (x{s:.2f})   "
              f"smallest {lo:4.1f} pt, largest {hi:4.1f} pt{flag}")


if __name__ == "__main__":
    raise SystemExit(main())
