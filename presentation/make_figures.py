"""Build the deck's figures from the evidence files. No number is typed in here.

    python -m presentation.make_figures

Writes presentation/figures/*.png at 200 dpi, sized for a projected slide.

Invariant 1 applies to pictures as much as to sentences: every value plotted is read
back out of `evaluation/results_log.csv`, `core/reliability_calibration.csv` or the
cached `run_all()` result dicts in `demo_cache/results/` at run time. If a figure and a
slide ever disagree, re-run this - do not edit the picture.

Figures:
  fig1_sun_angle_vs_error   ours vs best classical across the sun-azimuth sweep
  fig2_trust_calibration    do the three trust states separate by TRUE error?
  fig3_trust_map            the actual output: two real pairs, one accepted, one refused
  fig4_pipeline             the method as a flowchart (drawn here so it cannot drift from
                            what core/pipeline.py does; there is no hand-drawn diagram)
  fig5_real_sun_sweep       real OHRC vs NAC windows across 3-153 deg of sun difference
  fig6_trust_real_calibration  planted wrong answers on real windows: how many are flagged
  fig7_miloi_sun            MiLOI success vs sun angle, ours and SIFT/ORB/AKAZE (miloi_log.csv)

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

# ONE typeface for the whole deck (SPOC review, 27 Sep: "use common font for all slides").
# The slides are set in Calibri, so the figures are too; matplotlib's default DejaVu Sans made
# every chart a third face beside the slide text. Falls back to DejaVu Sans where Windows'
# Calibri files are absent, and says so, rather than failing the build.
from matplotlib import font_manager as _fm
_CALIBRI = [pathlib.Path("C:/Windows/Fonts") / f for f in ("calibri.ttf", "calibrib.ttf", "calibrii.ttf")]
for _f in _CALIBRI:
    if _f.exists():
        _fm.fontManager.addfont(str(_f))
FIG_FONT = "Calibri" if _CALIBRI[0].exists() else "DejaVu Sans"
if FIG_FONT != "Calibri":
    print("  !! Calibri not found - figures fall back to DejaVu Sans and will not match the slides")

plt.rcParams.update({
    "font.family": FIG_FONT,
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
    """The sun-azimuth difference of a NADIR synthetic row, else None.

    Viewpoint rows (18 Sep) carry the same `d_azimuth=15deg` in their config; letting them
    in moved the 15-degree median from 0.086 to 0.272 px, because tilted and relief-parallax
    rows measure something else. They are excluded here, by tier and by config."""
    if r.get("tier") == "synthetic viewpoint" or "VIEWPOINT" in (r.get("config") or ""):
        return None
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
    # The footer used to say "n/15" after the classical arm grew to 60 runs per angle, beside
    # labels that read "4/60"; it now takes the denominator from the data it annotates.
    tried = sorted(set(ntried))
    fig.text(0.014, 0.044, "dashed line = 0.5 px · n/" + "/".join(str(t) for t in tried)
             + " = classical runs that scored", fontsize=10, color=MUTED)
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


# fig3's two pairs (19 Sep, national round). ops.freeze re-caches exactly these before drawing.
FIG3_PAIRS = ("sac_ohrc_nac_w06", "site_tc_morning_mi1548_w01")
# Short enough for a 3.4 in panel title at 11 pt (measured: the long names ran off the canvas).
_SHORT = {"Chandrayaan-2 OHRC": "CH-2 OHRC", "LRO LROC NAC": "LRO NAC",
          "SELENE (Kaguya) Terrain Camera": "Kaguya TC", "SELENE (Kaguya) Multiband Imager": "MI"}


def _panel_lines(pair: str) -> list[str]:
    """Short lines for the column beside a panel: instruments, reference grid, what differs - from
    the pair's own geometry_prior.json."""
    import json
    g = json.loads((ROOT / "data" / "pairs" / pair / "geometry_prior.json").read_text(encoding="utf-8"))
    s, r = g["source"], g["reference"]
    ref = _SHORT.get(r["instrument"], r["instrument"])
    if r.get("band"):
        ref += " " + r["band"].split(" (")[0]
    lines = [f"{_SHORT.get(s['instrument'], s['instrument'])} → {ref}",
             f"{r['resampled_gsd_mpp']:.3g} m/px grid"]
    if g.get("benchmark"):
        lines += ["SAC's own pair", f"Sun azimuths {g['d_sun_azimuth_deg']:.0f}° apart"]
    elif "infrared" in (r.get("band") or ""):
        lines += ["visible ↔ near-infrared", "(multi-modal)"]
    else:
        lines += [g.get("terminology", "")]
    return lines


# fig3 and fig6 are drawn at the size their slides place them (build_deck reads each file's pixel
# width back at FIG10_DPI and places it at exactly that width), so every point size in them IS the
# size on the slide - fig10's rule. Until the cold read of 2 Oct both were drawn larger and shrunk:
# fig3's footnote printed at 8.5 pt and its panel titles at 9.2, fig6's legend at 9.8 and its
# footnote at 9.4.
FIG3_SIZE = (3.55, 5.36)       # slide 2, the column right of the text, from 1.36 in down
FIG6_SIZE = (4.93, 3.80)       # slide 5, right of the impact column, above the benefits tab
AT_SIZE_DPI = 200              # = SITE_N_DPI = build_deck.FIG10_DPI
AT_SIZE_MIN_PT = 11.0


def _check_at_size(name: str):
    small = [s for s in FONT_PT[name][1] if s < AT_SIZE_MIN_PT]
    if small:
        raise RuntimeError(f"{name} has text at {small} pt; it is drawn at its slide size, "
                           f"floor {AT_SIZE_MIN_PT} pt")


def _fallback_vs_visible_m(pair: str) -> str:
    """REPORT.md's metres between `pair`'s declared fallback and the visible-band registration of
    the same window ("Fallback vs the visible band") - printed there, never computed here."""
    m = re.search(rf"\| `{re.escape(pair)}` \| `[^`]+` \|[^|]*\|[^|]*\| [0-9.]+ \(([0-9.]+)\) \|",
                  REPORT_MD.read_text(encoding="utf-8"))
    if not m:
        raise RuntimeError(f"REPORT.md prints no fallback-vs-visible distance for {pair}")
    return m.group(1)


def fig_trust_map():
    """Two REAL pairs through the SAME code path: one the system accepts, one it refuses.

    Top: sac_ohrc_nac_w06 - Chandrayaan-2 OHRC against LRO NAC M1350459544RE, a window of the
    pair SAC's own paper benchmarks (arXiv:2509.04775 Table 1), Sun azimuths ~174 deg apart.
    Bottom: site_tc_morning_mi1548_w01 - Kaguya TC (visible) against Kaguya MI at 1548 nm:
    learned matching fails, the pixels contradict the homography, the system refuses it and
    declares the fallback. Until 19 Sep this figure showed pair_01 (two crops of ONE OHRC
    frame, not a validation tier) and a Tier D pair. Every count on it is read from the cached
    result dict, and matches the pair's row in evaluation/real_pairs_log.csv; the fallback's
    metres are read from REPORT.md, which prints them. Drawn at its slide size (FIG3_SIZE).
    """
    # STACKED, not side by side: slide 2's text needs the width. Each map has its words in the
    # column beside it, which lets the maps be larger at the slide's own size than they were
    # when the whole figure was drawn 5 in wide and shrunk.
    W, H = FIG3_SIZE
    fig = plt.figure(figsize=(W, H))
    canvas = fig.add_axes((0, 0, 1, 1))
    canvas.set_xlim(0, W)
    canvas.set_ylim(0, H)
    canvas.axis("off")

    def at(x, top, s, **kw):                     # inches from the left and from the TOP
        return canvas.text(x, H - top, s, va="top", ha="left", linespacing=1.2, **kw)

    at(0.02, 0.03, "The trust map: one accepted, one refused", fontsize=13, fontweight="bold",
       color=INK)
    side, row_gap, line = 1.78, 0.18, 11 * 1.2 / 72     # 1.85 cut "MI 1548 nm" at the right edge
    tx = side + 0.10
    for k, pair in enumerate(FIG3_PAIRS):
        top = 0.40 + k * (side + row_gap)
        r = _cached(pair)
        rel = r["reliability"]
        img = _overlay(_to_u8(_reference_image(r, pair)), np.asarray(rel["state"]))
        ax = fig.add_axes((0.0, (H - top - side) / H, side / W, side / H))
        ax.imshow(img, interpolation="bilinear")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        lines = _panel_lines(pair)
        at(tx, top, "\n".join(lines), fontsize=11, color=INK)
        vy = top + len(lines) * line + 0.12
        counts, n_cells = rel["counts"], int(rel["n_cells"])
        if r["declared"]["contradicted"]:
            # The count, then the verdict, never one derived from the other: the verdict comes
            # from the cells the area check could score. Whether refusing was RIGHT is the
            # declared fallback's distance from the visible-band registration of the same
            # window, which REPORT prints ("Fallback vs the visible band"). A cold reader took
            # this panel, beside slide 2's "62/62 accepted TMC-2 → IIRS", to mean multi-modal
            # registration fails (2 Oct).
            # v12: "rightly" - both cold readers of 3 Oct read a bare "refused" as the method failing.
            at(tx, vy, f"{counts['verified']} of {n_cells} verified\n→ rightly refused", fontsize=12,
               fontweight="bold", color=DECK_ACCENT)
            at(tx, vy + 2 * 12 * 1.2 / 72 + 0.06,
               f"fallback {_fallback_vs_visible_m(pair)} m from\nthe visible-band fit",
               fontsize=11, color=INK)
        else:
            at(tx, vy, f"{counts['verified']} of {n_cells} verified,\n{counts['weak']} weak → accepted",
               fontsize=12, fontweight="bold", color="#146b3c")

    # Legend: the same three marks the app draws, on a flat grey swatch, produced by the same
    # overlay function - so the key cannot disagree with the picture. "weak" was glossed
    # "measured, does not hold"; both cold readers asked what does not hold (2 Oct).
    words = {VERIFIED: ("verified", "matches and pixels agree"),
             WEAK: ("weak", "measured, alignment not confirmed"),
             NO_EVIDENCE: ("no evidence", "unmeasured, never guessed")}
    ly = 0.40 + 2 * (side + row_gap) + 0.02
    for i, s in enumerate((VERIFIED, WEAK, NO_EVIDENCE)):
        top = ly + i * 0.25
        sw = _overlay(np.full((64, 64), 150, np.uint8), np.array([[s]]))
        ins = fig.add_axes((0.02 / W, (H - top - 0.19) / H, 0.19 / W, 0.19 / H))
        ins.imshow(sw)
        ins.axis("off")
        head, gloss = words[s]
        at(0.30, top, f"{head} — {gloss}", fontsize=11, color=INK)
    # The log file's name meant nothing to a judge (cold read, 2 Oct).
    at(0.02, ly + 3 * 0.25 + 0.03, "8×8 squares on the reference grid", fontsize=11, color=MUTED)
    # JPEG, not PNG: the panels are photographs, and the PNG was 1.5 MB - a third of the
    # deck. The portal wants a PDF under its size cap and a judge's laptop wants it fast.
    p = OUT / "fig3_trust_map.jpg"
    _audit(fig, p.name)
    _check_at_size(p.name)
    fig.savefig(p, dpi=AT_SIZE_DPI, pil_kwargs={"quality": 88})
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
        "Common-GSD\nresample\n(one ground scale)",
        "Illumination\nnormalisation\n(gradient orientation)",
        "LoFTR\ndense matching\n(detector-free)",
        # run_all's order: refinement (pipeline._refine_subpixel) runs BEFORE MAGSAC++
        # (filter_matches); the 9 Sep figure had the two the other way round.
        "Sub-pixel NCC\nrefinement",
        "MAGSAC++\noutlier rejection",
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
                       "INDEPENDENT AREA CHECK — cross-correlates the warped image against the "
                       "reference, cell by cell.\nNever uses match positions. The cells vote on "
                       "the matcher's transform.",
                       "#fdeee6", ORANGE, fs=10.8, bold=True, colour="#8a3d10"))
    last_x = x0 + (n - 1) * (w + gap) + w / 2
    _arrow(ax, last_x, y, last_x, cy + ch)

    # Two outcomes, and the second one is the point.
    oy, oh = 0.02, 0.96
    placed.append(_box(ax, 0.60, oy, 5.80, oh,
                       "agrees →  aligned image + trust map: verified / weak / no evidence\n"
                       "unconfirmed →  kept and labelled, not certified\n"
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


# --- real-data figures (18 Sep 2026) -------------------------------------------------------
REAL_LOG = ROOT / "evaluation" / "real_pairs_log.csv"
TRUST_REAL = ROOT / "evaluation" / "trust_real_calibration.csv"
OUTCOME_STYLE = {   # colour AND marker, so identity is never colour-alone
    "correct_accepted": (AQUA, "o", "registered, accepted"),
    "caught_failure": (BLUE, "s", "failed, and the system said so"),
    "false_alarm": (MUTED, "D", "correct, but flagged"),
    "missed_failure": (ORANGE, "X", "failed, NOT caught"),
    "no_transform": (MUTED, "v", "no transform"),
    "inconclusive": (INK, "P", "image cannot judge"),
}


def fig_real_sun_sweep():
    """The real sun sweep: one Chandrayaan-2 OHRC frame vs LROC NAC frames at 3-153 deg
    of sun-azimuth difference. Inliers per window, marked by outcome (ops/sun_sweep.py).
    Every point is a real_pairs_log row with an `outcome`; nothing is typed in."""
    rows = [r for r in _rows(REAL_LOG) if (r.get("outcome") or "").strip()]
    if not rows:
        return None
    # latest row per pair_id (a pair re-run on a later commit supersedes its old row)
    latest = {}
    for r in rows:
        latest[r["pair_id"]] = r
    rows = list(latest.values())
    # Rule v2 (|NCC|, inconclusive when neither alignment correlates), derived from the
    # NCCs logged in results_log; the logged `outcome` column is v1 and stays as written.
    from ops.sun_sweep import outcomes_v2
    v2 = outcomes_v2(rows, _rows(LOG))
    for r in rows:
        r["outcome"] = v2.get(r["pair_id"], r["outcome"])
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.set_yscale("symlog", linthresh=10)
    ax.grid(True, which="major", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=13)
    counts = {}
    for key, (col, mk, label) in OUTCOME_STYLE.items():
        pts = [(float(r["d_sun_azimuth_deg"]), float(r["inliers"] or 0)) for r in rows
               if r["outcome"] == key and r.get("d_sun_azimuth_deg")]
        if not pts:
            continue
        counts[key] = len(pts)
        x, y = zip(*pts)
        ax.scatter(x, y, s=70, c=col, marker=mk, edgecolors=SURFACE, linewidths=1.2,
                   zorder=5 if key in ("caught_failure", "missed_failure") else 3,
                   label=f"{label} ({len(pts)})")
    ax.set_xlabel("sun-azimuth difference, OHRC vs NAC  (degrees)", fontsize=14)
    ax.set_ylabel("inlier matches per window", fontsize=14)
    az = [float(r["d_sun_azimuth_deg"]) for r in rows if r.get("d_sun_azimuth_deg")]
    ax.set_title(f"Real OHRC vs LRO NAC: Sun azimuths {min(az):.0f}–{max(az):.0f}° apart",
                 loc="left", fontweight="bold", fontsize=15, pad=10)
    ax.set_xlim(-5, 165)
    ax.set_ylim(0, 20000)
    ax.legend(loc="lower left", fontsize=11, frameon=False)
    n_nac = len({r["reference_product"] for r in rows})
    fig.text(0.014, 0.006, f"{len(rows)} windows, {n_nac} NAC frames · outcome by image "
             f"evidence, rule v2 (ops/sun_sweep.py)", fontsize=10, color=MUTED)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    out = OUT / "fig5_real_sun_sweep.png"
    _audit(fig, out.name)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def _distinct_windows(pair_ids) -> dict:
    """{ground window: [pair ids]}, a window being (source, reference, centre, size) from each
    pair's geometry_prior.json. Known issue 2: some windows were cut twice under two ids."""
    import json
    out = {}
    for pid in sorted(pair_ids):
        g = json.loads((ROOT / "data" / "pairs" / pid / "geometry_prior.json").read_text(encoding="utf-8"))
        key = (g["source"]["product_id"], g["reference"]["product_id"],
               round(g["window_centre_map_m"][0]), round(g["window_centre_map_m"][1]), round(g["window_m"]))
        out.setdefault(key, []).append(pid)
    return out


def fig_trust_real():
    """Planted confident-wrong registrations on real windows: how often does the area check
    contradict them, by displacement? d = 0 is the false-alarm rate."""
    if not TRUST_REAL.exists():
        return None
    all_rows = _rows(TRUST_REAL)
    # TRANSLATIONS ONLY. Since 20 Sep the calibration also plants rotations and scale changes,
    # which are a different experiment: they are not uniform over the frame, so a single
    # "flagged as wrong" rate per displacement would pool two quantities that do not mean the
    # same thing, and the x axis ("planted error, metres") would mean the corner displacement for
    # some bars and every pixel's displacement for others. Those rows have their own table in
    # REPORT.md. Rows written before the column existed are translations.
    all_rows = [r for r in all_rows if (r.get("kind") or "translation") == "translation"]
    # Two populations (20 Sep 2026): the 74 °S windows with Sun azimuths under 10° apart (the
    # bars, as before) and SAC's hard-Sun windows at 132-174° (markers), never pooled. Rows
    # written before the column existed are the ≤10° population.
    rows = [r for r in all_rows if float(r.get("d_sun_azimuth_deg") or 0) < 10]
    hard = [r for r in all_rows if float(r.get("d_sun_azimuth_deg") or 0) >= 10]
    ds = sorted({float(r["displacement_m"]) for r in rows})
    rate = [np.mean([r["contradicted"] == "True" for r in rows if float(r["displacement_m"]) == d]) for d in ds]
    n = [sum(1 for r in rows if float(r["displacement_m"]) == d) for d in ds]
    # Every reference grid of BOTH populations, as a range. The 19 Sep fix named the two grids
    # of the near-Sun bars (0.931 / 1.245); the SAC diamonds sit on 1.215 and 1.622 m, so a
    # judge converting the diamond series with the printed grids got the wrong answer
    # (claim-checker, 22 Sep).
    grids = sorted({float(r["gsd_ref_m"]) for r in all_rows})
    fig, ax = plt.subplots(figsize=FIG6_SIZE)          # drawn at its slide size: see FIG6_SIZE
    ax.grid(True, which="major", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    xs = np.arange(len(ds))
    az_lo = sorted({float(r.get("d_sun_azimuth_deg") or 0) for r in rows})
    # two-line labels: the legend must fit inside the empty 0-2 m columns (x < 2.5 bars)
    lo_label = (f"Suns {az_lo[0]:.0f}–{az_lo[-1]:.0f}° apart\n{len({r['pair_id'] for r in rows})} windows"
                if az_lo and az_lo[-1] > 0 else "Suns under 10° apart")
    ax.bar(xs, [100 * v for v in rate], color=[MUTED if d == 0 else BLUE for d in ds], zorder=3, width=0.7,
           label=lo_label if hard else None)
    hx, hr = [], []
    if hard:
        hd = sorted({float(r["displacement_m"]) for r in hard})
        hx = [ds.index(d) for d in hd if d in ds]
        hr = [100 * np.mean([r["contradicted"] == "True" for r in hard if float(r["displacement_m"]) == d])
              for d in hd if d in ds]
    for x, v, k in zip(xs, rate, n):
        # the bar's label sits above the bar AND above the hard-Sun marker at that x (20 Sep:
        # the 2 m marker printed over the "1%")
        top = max(100 * v, max([h for hxi, h in zip(hx, hr) if hxi == x], default=0) + 4)
        ax.text(x, top + 2, f"{100 * v:.0f}%", ha="center", va="bottom", fontsize=11, color=INK)
    if hard:
        az_hi = sorted({float(r["d_sun_azimuth_deg"]) for r in hard})
        # "8 SAC windows" beside slide 2's "6/6 accepted on SAC's pair" read as two counts of one
        # pair to both cold readers (2 Oct): the 8 are windows of SAC's TWO pairs, equatorial and
        # polar, so the label counts the pairs too.
        n_sac_pairs = len({r["pair_id"].rsplit("_w", 1)[0] for r in hard})
        ax.scatter(hx, hr, s=60, marker="D", c=ORANGE, edgecolors=SURFACE, linewidths=1.0, zorder=6,
                   label=f"Suns {az_hi[0]:.0f}–{az_hi[-1]:.0f}° apart\n"
                         f"{len({r['pair_id'] for r in hard})} windows of SAC's {n_sac_pairs} pairs")
        # the 0-2 m columns are empty below ~75 %: the legend sits there, clear of the 3 m bar
        # Above the plot, in one row: at slide-legible sizes the legend no longer fits the empty
        # 0-2 m columns without running into the 3 m bar's label.
        # The bar series' own handle takes the colour of its FIRST bar, the grey 0 m bar, so the
        # key showed grey for a series drawn in blue. Key it with the colour the bars carry.
        from matplotlib.patches import Patch
        handles, labels = ax.get_legend_handles_labels()
        handles = [Patch(facecolor=BLUE, label=lab) if lab == lo_label else h
                   for h, lab in zip(handles, labels)]
        ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2,
                  fontsize=11, frameon=False, columnspacing=1.2, handletextpad=0.4,
                  borderaxespad=0.15)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{d:g}" for d in ds], fontsize=11)
    ax.tick_params(axis="y", labelsize=11)
    ax.set_ylim(0, 112)
    ax.set_xlabel(f"planted shift, metres (reference grids {grids[0]:.2f}–{grids[-1]:.2f} m/px)",
                  fontsize=11.5)
    ax.set_ylabel("flagged as wrong (%)", fontsize=11.5)
    ax.set_title("Planted shifts: how many are flagged?",
                 loc="left", fontweight="bold", fontsize=13, pad=40)
    ids = {r["pair_id"] for r in rows}
    # `_distinct_windows` opens each pair's geometry_prior.json, and data/pairs is gitignored, so
    # on a machine that has the logs but not the imagery this would take the whole figure - and
    # with it the freeze's report step - down over a caption. `ops.make_report._distinct_note`
    # already guards the same call the same way.
    try:
        n_ground = len(_distinct_windows(ids))
    except (OSError, ValueError, KeyError):
        n_ground = len(ids)
    n_win = len(ids)
    n_hard = len({r["pair_id"] for r in hard})
    # The chart plots BOTH populations, so the caption counts both. It said "22 real windows"
    # under a chart of 30 while slide 2 said 30 (claim-checker, 22 Sep).
    wins = (f"{n_win + n_hard} real windows: {n_win} OHRC→NAC and NAC→NAC, {n_hard} SAC OHRC→NAC"
            if hard else
            f"{n_win} real windows" + (f" ({n_ground} distinct)" if n_ground != n_win else "")
            + ", OHRC→NAC and NAC→NAC")
    # "every planted match agrees with the wrong answer" was a phrase a cold reader could not
    # decode (2 Oct); slide 5 now says it the same way as this line.
    fig.text(0.008, 0.008, f"{wins}\n0 m = false-alarm rate · the planted matches fit the "
             f"wrong answer", fontsize=11, color=MUTED, linespacing=1.25, va="bottom")
    fig.tight_layout(rect=(0, 0.115, 1, 1))
    out = OUT / "fig6_trust_real_calibration.png"
    _audit(fig, out.name)
    _check_at_size(out.name)
    fig.savefig(out, dpi=AT_SIZE_DPI)
    plt.close(fig)
    return out


YELLOW = "#eda100"   # categorical slot 4; the 4-slot set passes validate_palette.js (contrast WARN
                     # for aqua and yellow -> marker shapes and a legend carry identity, never colour alone)
MILOI_STYLE = {"ours_loftr+subpixel": (BLUE, "o", "ours (LoFTR + trust layer)"),
               "SIFT": (ORANGE, "s", "SIFT"), "AKAZE": (AQUA, "D", "AKAZE"), "ORB": (YELLOW, "^", "ORB")}


def fig_miloi():
    """MiLOI (real LROC NAC pairs of the same ground under many suns): share of pairs each method
    registers within SUCCESS_PX of the network truth, per sun-vector-angle bin, n under each bin.
    Read from evaluation/miloi_log.csv only (latest row per pair and method), exactly as
    `python -m evaluation.miloi --table` counts it."""
    from evaluation.miloi import BINS, LOG as MILOI_LOG, SUCCESS_PX
    if not MILOI_LOG.exists():
        return None
    latest = {}
    for r in _rows(MILOI_LOG):
        latest[(r["pair_id"], r["method"])] = r
    methods = [m for m in MILOI_STYLE if any(mm == m for _, mm in latest)]
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.grid(True, axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    xs = np.arange(len(BINS))
    ns, rates = [], []
    for m in methods:
        rate, n_m = [], []
        for lo, hi in BINS:
            rs = [r for (_, mm), r in latest.items() if mm == m and lo <= float(r["d_sun_angle_deg"]) < hi]
            n_m.append(len(rs))
            rate.append(100.0 * sum(int(r["success"]) for r in rs) / len(rs) if rs else np.nan)
        ns.append(n_m)
        rates.append(np.array(rate))
    for j, (m, rate) in enumerate(zip(methods, rates)):
        col, mk, label = MILOI_STYLE[m]
        dodge = (j - (len(methods) - 1) / 2) * 0.07          # identical values stay visible
        ax.plot(xs + dodge, rate, color=col, linewidth=2, marker=mk, markersize=8,
                markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=4 if j == 0 else 3, label=label)
    # direct label on ours, at the bin where it leads the best classical by the most
    lead = rates[0] - np.nanmax(np.vstack(rates[1:]), axis=0)
    k = int(np.nanargmax(lead))
    ax.annotate(MILOI_STYLE[methods[0]][2].split(" (")[0], (xs[k], rates[0][k]), xytext=(12, 6),
                textcoords="offset points", fontsize=12, color=INK, fontweight="bold")
    if len({tuple(n) for n in ns}) != 1:
        print("    !! fig7: methods have different pair counts per bin - n below is ours'")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{lo}-{min(hi, 180)}°\nn={n}" for (lo, hi), n in zip(BINS, ns[0])], fontsize=12)
    ax.set_ylim(-4, 104)
    ax.set_ylabel(f"pairs registered within {SUCCESS_PX:g} px  (%)", fontsize=14)
    ax.set_xlabel("angle between the two sun directions", fontsize=14)
    ax.set_title("MiLOI: real NAC pairs of one ground under many suns",
                 loc="left", fontweight="bold", fontsize=15, pad=10)
    ax.legend(loc="upper right", fontsize=11, frameon=False)
    scenes = {}
    for (_, mm), r in latest.items():
        if mm == methods[0]:
            scenes[r["scene"]] = scenes.get(r["scene"], 0) + 1
    fig.text(0.014, 0.008, f"{sum(ns[0])} same-sensor LROC NAC pairs with a truth (MiLOI, Xie et al. 2025) · "
             f"truth = a translation network\nfrom ours+SIFT agreement on OTHER pairs · S3 "
             f"({scenes.get('S3', 0)} pairs): no redundancy, its own error is not measurable",
             fontsize=9.5, color=MUTED, linespacing=1.35, va="bottom")
    fig.set_figheight(4.7)
    fig.tight_layout(rect=(0, 0.085, 1, 1))
    out = OUT / "fig7_miloi_sun.png"
    _audit(fig, out.name)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_sun_map():
    """Sun change on SAC's own OHRC frame, in BOTH axes the PS names: azimuth and elevation.
    One point per LRO NAC registered against that one OHRC frame by the ladder cut
    (sac_ohrclroc_nac*, 1 Oct 2026; SAC's own NAC included) - at the median
    Sun difference of its windows, labelled windows accepted / windows. Every value from
    real_pairs_log.csv (latest row per pair); d_incidence = NAC incidence - OHRC incidence, so the
    elevation change is its negative."""
    latest = {}
    for r in _rows(REAL_LOG):
        latest[r["pair_id"]] = r
    # One method for every point: the ladder cut (both images in LRO's geometry, one 1.75 m grid, shared
    # windows). SAC's own NAC is on it too (re-cut that way); the frozen sac_ohrc_nac_* rows, cut on
    # the NAC's own grid with a 4 m correction against the OHRC, are not mixed in.
    rows = [r for p, r in latest.items() if p.startswith("sac_ohrclroc_nac")
            and r.get("d_sun_azimuth_deg") and r.get("d_incidence_deg") and r.get("verdict") != "INVALIDATED"]
    if not rows:
        return None
    by = {}
    for r in rows:
        by.setdefault(r["reference_product"], []).append(r)
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    style = [(0.75, AQUA, "o", "most windows accepted"), (0.25, YELLOW, "D", "some accepted"),
             (-1.0, ORANGE, "X", "few or none accepted")]
    seen, placed = set(), []
    for nac, rs in sorted(by.items()):
        az = float(np.median([float(r["d_sun_azimuth_deg"]) for r in rs]))
        el = float(np.median([-float(r["d_incidence_deg"]) for r in rs]))
        acc = sum(r["verdict"] == "agrees" for r in rs)
        frac = acc / len(rs)
        cut, col, mk, lab = next(s for s in style if frac >= s[0])
        ax.scatter([az], [el], s=60 + 22 * len(rs), c=col, marker=mk, edgecolors=INK, linewidths=0.8, zorder=4,
                   label=lab if lab not in seen else None)
        seen.add(lab)
        placed.append((az, el, f"{acc}/{len(rs)}"))
    ax.set_xlim(-16, 190)
    ax.set_xticks([0, 30, 60, 90, 120, 150, 180])
    ax.set_xlabel("Sun azimuth difference, OHRC vs NAC  (degrees)", fontsize=14)
    ax.set_ylabel("Sun elevation change, NAC − OHRC  (degrees)", fontsize=14)
    ax.set_title("Sun change on SAC's own OHRC frame: azimuth and elevation", loc="left", fontweight="bold",
                 fontsize=15, pad=10)
    ax.legend(loc="upper center", fontsize=11, frameon=False, ncol=3, bbox_to_anchor=(0.5, -0.17))
    fig.text(0.014, 0.006, f"{len(by)} LRO NACs, {len(rows)} windows · label: windows accepted / windows · "
             f"OHRC → NAC, both panchromatic (cross-sensor)", fontsize=10, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    # Labels placed one by one, each at the first offset whose box touches no earlier label and no
    # marker - measured on the rendered canvas, as _audit measures overlaps.
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    pts_px = [ax.transData.transform((a, e)) for a, e, _ in placed]
    boxes = []
    for a, e, txt in placed:
        for off in ((10, -6), (-38, -6), (8, 7), (8, -19), (-38, 7), (-38, -19), (14, 14), (-44, 14)):
            t = ax.annotate(txt, (a, e), xytext=off, textcoords="offset points", fontsize=12, color=INK, zorder=5)
            bb = t.get_window_extent(renderer=r).expanded(1.05, 1.1)
            hit = any(bb.overlaps(b) for b in boxes) or any(
                bb.x0 - 6 < x < bb.x1 + 6 and bb.y0 - 6 < y < bb.y1 + 6 for x, y in pts_px)
            if not hit:
                boxes.append(bb)
                break
            t.remove()
        else:
            boxes.append(ax.annotate(txt, (a, e), xytext=(10, -6), textcoords="offset points", fontsize=12,
                                     color=INK, zorder=5).get_window_extent(renderer=r))
    out = OUT / "fig9_sun_map.png"
    _audit(fig, out.name)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


# fig10 is drawn at the size slide 4 places it (presentation/build_deck.py reads the PNG's pixel width
# back at SITE_N_DPI), so every point size below IS the size on the slide. The v11 draft was drawn at
# 6.6 x 4.1 in and shrunk to 5.45 in: its captions printed at 7.0 and 7.8 pt and its labels at 8.7-9.5 pt,
# under the deck's 11 pt floor (pre-submission audit, 2 Oct). Nothing here is smaller than 11 pt.
SITE_N_SIZE = (5.90, 3.50)
SITE_N_DPI = 200
SITE_N_MIN_PT = 11.0
REPORT_MD = ROOT / "REPORT.md"
DECK_ACCENT = "#c24a1e"            # the deck's ACCENT (build_deck): readable at 11 pt, unlike ORANGE


def fig_site_n():
    """Site N (ops/cut_chain_pairs.py site, 1 Oct 2026): one place where OHRC, TMC-2, IIRS and an
    LRO NAC were all registered under matched Suns. Four instruments as nodes; every leg an edge
    labelled with windows accepted / windows and the RANGE of its per-window held-out medians on its
    reference grid - the range REPORT.md prints in its Site N table (accepted windows with an inlier
    ratio above 0.5), not a median of medians, which REPORT never prints. The loop closure OHRC -> NAC
    -> TMC-2 against OHRC -> TMC-2 is a caption with its median AND its max: as a bare "2.0 m" it was
    read as a bound, and two of the four loops are above 2.0 m (audit, 2 Oct).

    Every value is read from real_pairs_log.csv, and every one that REPORT.md prints is looked up in
    REPORT.md before the figure is written: a figure that disagrees with the report is not drawn."""
    latest = {}
    for r in _rows(REAL_LOG):
        latest[r["pair_id"]] = r
    legs = {"ot": [r for p, r in latest.items() if p.startswith("siten_ohrc") and "_tmc" in p],
            "on": [r for p, r in latest.items() if p.startswith("siten_ohrc") and "_nac" in p],
            "nt": [r for p, r in latest.items() if p.startswith("siten_nac")]}
    if not (legs["ot"] and legs["on"] and legs["nt"]):
        return None
    tmc = legs["ot"][0]["reference_product"]
    # The IIRS strip of the same orbit, bands beyond TMC-2's 400-850 nm passband (746 nm is the control).
    ti = [r for p, r in latest.items() if p.startswith(f"chain_tmc{tmc[12:20]}_iirs") and "_iirs746_" not in p]
    loops = [r for p, r in latest.items() if p.startswith("loop_siten")]
    if not (ti and loops):
        return None
    report = REPORT_MD.read_text(encoding="utf-8")
    unprinted = []

    def need(text):
        """A value as REPORT.md prints it; recorded if the report does not contain it."""
        if text not in report:
            unprinted.append(text)
        return text

    def leg(rows, grid):
        """REPORT.md's Site N cell for one leg (ops/make_report.py section_site_n): accepted / windows,
        and the min-max of the held-out medians of accepted windows with an inlier ratio above 0.5,
        in pixels of `grid` - the leg's reference, the image at the arrowhead."""
        acc = [r for r in rows if r["verdict"] == "agrees"]
        rob = [float(r["residual_median_px"]) for r in acc
               if r.get("residual_median_px") and float(r.get("inlier_ratio") or 0) > 0.5]
        g = float(rows[0]["ref_gsd_m"])
        lo, hi = min(rob), max(rob)
        need(f"{lo:.2f}-{hi:.2f} ({lo * g:.1f}-{hi * g:.1f} m) on {g:g} m")
        need(f"| {len(rows)} | agrees {len(acc)} |")
        return (f"{len(acc)}/{len(rows)} accepted", f"{lo:.2f}–{hi:.2f} {grid} px",
                f"({lo * g:.1f}–{hi * g:.1f} m)")

    ot, on, nt = leg(legs["ot"], "TMC-2"), leg(legs["on"], "NAC"), leg(legs["nt"], "TMC-2")
    g_ohrc, g_nac, g_tmc = (need(f"{float(legs['ot'][0]['src_gsd_m']):g} m"),
                            need(f"{float(legs['on'][0]['ref_gsd_m']):g} m"),
                            need(f"{float(legs['ot'][0]['ref_gsd_m']):g} m"))
    g_iirs = need(f"{min(float(r['ref_gsd_m']) for r in ti):.2f} m")
    bands = sorted({int(re.search(r"_iirs(\d+)_", r["pair_id"]).group(1)) for r in ti})
    ti_acc = sum(r["verdict"] == "agrees" for r in ti)
    # 30 = the per-band "accepted" cells of that orbit's IIRS table, summed: each must be printed there.
    orbit = report.split(f"orbit of {tmc[12:16]}-{tmc[16:18]}-{tmc[18:20]} (", 1)[-1].split("####", 1)[0]
    for b in bands:
        n_b = sum(f"_iirs{b}_" in r["pair_id"] for r in ti)
        a_b = sum(f"_iirs{b}_" in r["pair_id"] and r["verdict"] == "agrees" for r in ti)
        if f"| {b} nm | infrared: multi-modal | {a_b}/{n_b} |" not in orbit:
            unprinted.append(f"{b} nm {a_b}/{n_b} in the orbit's IIRS table")
    lats = [float(r["window_lat"]) for r in ti]
    for v in (min(lats), max(lats)):
        need(f"{v:.4f}")                                          # the window rows print 4 decimals
    rms = [float(r["loop_rms_m"]) for r in loops]
    need(f"Loop RMS median **{np.median(rms):.2f} m**")
    need(f"max {max(rms):.2f} m")
    every = legs["ot"] + legs["on"] + legs["nt"]                  # the middle of the windows, as REPORT
    lat = float(np.median([float(r["window_lat"]) for r in every]))
    lon = float(np.median([float(r["window_lon"]) for r in every]))
    lon = (lon + 180.0) % 360.0 - 180.0
    site = f"{abs(lat):.1f}°{'N' if lat >= 0 else 'S'} {abs(lon):.1f}°{'E' if lon >= 0 else 'W'}"
    need(f"near {abs(lat):.1f}°{'N' if lat >= 0 else 'S'}, {abs(lon):.1f}°{'E' if lon >= 0 else 'W'}")
    if unprinted:
        raise RuntimeError("fig10 would show values REPORT.md does not print - regenerate REPORT.md or fix "
                           "the figure: " + "; ".join(unprinted))

    W, H = SITE_N_SIZE
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    fs, fs_name, fs_title = 11, 11.5, 12

    def text(x, y, s, size=fs, weight="normal", colour=INK, ha="center"):
        return ax.text(x, y, s, ha=ha, va="center", fontsize=size, fontweight=weight, color=colour,
                       zorder=3)

    # Nodes, in inches from the bottom-left corner: the Chandrayaan-2 cameras in blue, LRO in grey.
    bw, bh = 2.00, 0.48
    top, bot = H - 0.60, H - 2.12                                 # top edges of the two node rows
    left, right = 0.04, W - 0.04 - bw
    # OHRC's own pixels are ~0.25 m; every Site N leg matched it resampled to 1.232 m (src_gsd_m).
    nodes = {"O": (left, top, "Chandrayaan-2 OHRC", f"matched on a {g_ohrc} grid", BLUE),
             "N": (right, top, "LRO NAC", f"{g_nac} grid", MUTED),
             "T": (left, bot, "Chandrayaan-2 TMC-2", f"{g_tmc} grid", BLUE),
             "I": (right, bot, "Chandrayaan-2 IIRS", f"{g_iirs} grid, {bands[0]}–{bands[-1]} nm", BLUE)}
    for x, y, name, detail, col in nodes.values():
        ax.add_patch(FancyBboxPatch((x, y - bh), bw, bh, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc="#eef4fb" if col == BLUE else "#f1f1ef", ec=col, lw=1.4, zorder=2))
        text(x + bw / 2, y - bh / 2 + 0.11, name, fs_name, "bold")
        text(x + bw / 2, y - bh / 2 - 0.11, detail)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16, linewidth=2.0,
                                     color=AQUA, zorder=1, shrinkA=0, shrinkB=0))

    gap = 0.03
    # OHRC -> NAC, along the top; its label above the boxes, where it may run wider than the gap.
    arrow(left + bw + gap, top - bh / 2, right - gap, top - bh / 2)
    text(W / 2, top + 0.16, f"{on[0]} · {on[1]} {on[2]}")
    # OHRC -> TMC-2, straight down the left; three short lines beside it.
    cx = left + bw / 2
    arrow(cx, top - bh - gap, cx, bot + gap)
    mid = (top - bh + bot) / 2
    for k, s in enumerate(ot):
        text(cx + 0.12, mid + (1 - k) * 0.18, s, ha="left")
    # NAC -> TMC-2, the diagonal; its label right of the line and clear of it.
    arrow(right + 0.30, top - bh - gap, left + bw - 0.20, bot + gap)
    text(right - 0.25, mid + 0.07, nt[0], ha="left")
    text(right - 0.25, mid - 0.11, f"{nt[1]} {nt[2]}", ha="left")
    # TMC-2 -> IIRS along the bottom; the IIRS windows lie along the strip, not on the site's windows.
    arrow(left + bw + gap, bot - bh / 2, right - gap, bot - bh / 2)
    text(W / 2, bot - bh - 0.16, f"{ti_acc}/{len(ti)} accepted · {len(bands)} infrared bands (multi-modal)")
    text(W / 2, bot - bh - 0.34, f"IIRS windows along this TMC-2 pass, {min(lats):.1f}–{max(lats):.1f}°N")
    # The loop: median AND max, and what it is.
    text(0.04, 0.31, f"Loop via NAC vs direct, {len(loops)} windows: median {np.median(rms):.2f} m, "
                     f"max {max(rms):.2f} m (consistency, not accuracy)", colour=DECK_ACCENT, ha="left")
    text(0.04, 0.12, "Ranges: per-window held-out medians (matches the fit never saw), inlier ratio > 0.5",
         colour=MUTED, ha="left")
    text(0.04, H - 0.16, f"One site, {site}, and its TMC-2 pass: Suns matched, every leg checked",
         fs_title, "bold", ha="left")

    out = OUT / "fig10_site_n.png"
    _audit(fig, out.name)
    small = [s for s in FONT_PT[out.name][1] if s < SITE_N_MIN_PT]
    if small:
        raise RuntimeError(f"fig10 has text at {small} pt; it is drawn at its slide size, floor {SITE_N_MIN_PT} pt")
    fig.savefig(out, dpi=SITE_N_DPI)
    plt.close(fig)
    return out


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
    for f in (fig_real_sun_sweep, fig_trust_real, fig_miloi, fig_sun_map, fig_site_n):
        out = f()
        print(f"  wrote {out.name}" if out else f"  skipped {f.__name__} (no evidence file yet)")
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
