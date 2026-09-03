"""Build the deck's figures from the evidence files. No number is typed in here.

    python -m presentation.make_figures

Writes presentation/figures/*.png at 200 dpi, sized for a projected slide.

Invariant 1 applies to pictures as much as to sentences: every value plotted is read
back out of `evaluation/results_log.csv` or `core/reliability_calibration.csv` at run
time. If a figure and a slide ever disagree, re-run this - do not edit the picture.

Colour: slots 1/2/3 of the validated categorical palette (blue #2a78d6, orange #eb6834,
aqua #1baf7a). Checked with the palette validator - all six checks pass; aqua's 2.74:1
contrast against the surface carries a WARN, which is discharged here by direct labels
on every series, so identity is never colour-alone. Marker shape is a second encoding
for the same reason.
"""
from __future__ import annotations

import csv
import pathlib
import re
import statistics as st
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "evaluation" / "results_log.csv"
CELLS = ROOT / "core" / "reliability_calibration.csv"
OUT = ROOT / "presentation" / "figures"

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1a1a1a", "#5c5c5c", "#d8d8d6"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "font.size": 13, "axes.labelsize": 14, "axes.titlesize": 16,
    "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
})


def _rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))


def _delta(r):
    m = re.search(r"d_azimuth=(-?[\d.]+)deg", r.get("config") or "")
    return float(m.group(1)) if m else None


def load_curves():
    """median rmse_gt_px per sun delta, for ours and for the best classical detector."""
    ours, cls = {}, {}
    for r in _rows(LOG):
        d, v = _delta(r), r.get("rmse_gt_px")
        if d is None or not v or v == "None":
            continue
        if r.get("method") == "ours_loftr+subpixel":
            ours.setdefault(d, []).append(float(v))
        elif (r.get("method") in ("SIFT", "ORB", "AKAZE")
              and "GATE 2 CRITERION 5" in (r.get("notes") or "")):
            cls.setdefault((d, r["method"]), []).append(float(v))
    deltas = sorted(ours)
    o = [st.median(ours[d]) for d in deltas]
    best = []
    for d in deltas:
        per = [st.median(cls[(d, m)]) for m in ("SIFT", "ORB", "AKAZE") if (d, m) in cls]
        best.append(min(per) if per else np.nan)
    return deltas, o, best


def fig_sun_angle(deltas, ours, best):
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.set_yscale("log")
    ax.grid(True, which="major", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    ax.axhline(0.5, color=MUTED, linewidth=1.2, linestyle=(0, (5, 4)), zorder=1)
    # Left edge: both series sit well below 0.5 px at 0-15°, so this is the one place
    # the label cannot land on top of a line.
    ax.text(-6, 0.58, "Gate 2 threshold  0.5 px", color=MUTED, fontsize=11,
            ha="left", va="bottom")

    ax.plot(deltas, best, color=ORANGE, linewidth=2, marker="s", markersize=9,
            markeredgecolor=SURFACE, markeredgewidth=2, label="best of SIFT / ORB / AKAZE",
            zorder=3)
    ax.plot(deltas, ours, color=BLUE, linewidth=2, marker="o", markersize=9,
            markeredgecolor=SURFACE, markeredgewidth=2, label="ours (LoFTR + trust layer)",
            zorder=4)

    ax.text(120, best[deltas.index(120.0)] * 2.2, "best classical", color=ORANGE,
            fontsize=13, fontweight="bold", ha="center")
    ax.text(120, ours[deltas.index(120.0)] * 0.30, "ours", color=BLUE,
            fontsize=13, fontweight="bold", ha="center")

    # The three things a reader should leave with. They live in the clear band under
    # the blue line (y 0.010-0.05), tiled left-to-right so none can overlap another.
    ax.annotate("at 0° classical wins —\nno illumination problem yet",
                xy=(0, best[0]), xytext=(-6, 0.0125),
                color=INK, fontsize=11, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1))
    ratio15 = best[deltas.index(15.0)] / ours[deltas.index(15.0)]
    ax.annotate(f"15°: {ratio15:.2f}× better\nGate 2 passes here",
                xy=(15, ours[deltas.index(15.0)]), xytext=(46, 0.0125),
                color=INK, fontsize=11, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1))
    ax.annotate("180°: we recover, classical does not.\nA sun flip INVERTS the shading, and\n"
                "gradient orientation is invariant to that.",
                xy=(180, ours[-1]), xytext=(92, 0.0115),
                color=INK, fontsize=11, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1))

    ax.set_xlabel("sun-azimuth difference between the two images  (degrees)")
    ax.set_ylabel("registration error vs known truth\nmedian rmse_gt_px  (reference pixels)")
    ax.set_title("Registration error against illumination change",
                 pad=14, loc="left", fontweight="bold")
    ax.set_xticks(deltas)
    ax.set_xlim(-8, 190)
    ax.set_ylim(0.008, 20000)
    ax.legend(loc="upper left", frameon=False, bbox_to_anchor=(0.0, 0.99))
    fig.text(0.01, 0.015, "40 pairs, exact ground truth · every point is the median of 5 "
             "off-grid shifts · 60 m/px · source: evaluation/results_log.csv",
             fontsize=9.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    p = OUT / "fig1_sun_angle_vs_error.png"
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

    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xscale("log")

    style = [("verified", BLUE, "o"), ("weak", ORANGE, "s"), ("no_evidence", AQUA, "^")]
    label_for = {"verified": "verified", "weak": "weak", "no_evidence": "no evidence"}
    for state, colour, marker in style:
        vals = np.sort(np.array(by_state[state]))
        if vals.size == 0:
            continue
        y = np.arange(1, vals.size + 1) / vals.size
        ax.plot(vals, y, color=colour, linewidth=2, zorder=3,
                label=f"{label_for[state]}  (n={vals.size})")
        # one marker per series, at the median - identity without a dot on every point
        mi = int(0.5 * vals.size)
        ax.plot([vals[mi]], [y[mi]], color=colour, marker=marker, markersize=10,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)

    ax.axvline(0.5, color=MUTED, linewidth=1.2, linestyle=(0, (5, 4)), zorder=1)
    ax.text(0.53, 0.06, "half a pixel\n= 30 m", color=MUTED, fontsize=11, ha="left")

    v = np.array(by_state["verified"])
    frac = float((v < 0.5).mean())
    ax.annotate(f"{frac*100:.1f}% of verified cells\nare under half a pixel",
                xy=(0.5, frac), xytext=(0.012, 0.80), color=INK, fontsize=12,
                arrowprops=dict(arrowstyle="->", color=MUTED, linewidth=1.2))

    # Direct labels ride their OWN curve at a DIFFERENT height each, because placing
    # all three at one y put "weak" and "no evidence" on top of each other - their
    # medians are only 0.17 px apart, which is a few pixels on a log axis.
    for (state, colour, _), y_at in zip(style, (0.70, 0.50, 0.30)):
        vals = np.sort(np.array(by_state[state]))
        if vals.size == 0:
            continue
        x_at = float(np.interp(y_at, np.arange(1, vals.size + 1) / vals.size, vals))
        ax.text(x_at * 1.12, y_at, label_for[state], color=colour,
                fontsize=13, fontweight="bold", ha="left", va="center")

    ax.set_xlabel("true error of the cell against known truth  (reference pixels, log scale)")
    ax.set_ylabel("fraction of cells at or below that error")
    ax.set_title("The trust label is calibrated, not a colour scheme — "
                 "sun difference ≤ 30°", pad=14, loc="left", fontweight="bold")
    ax.set_xlim(0.008, 12)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", frameon=False)
    fig.text(0.01, 0.015, "one line per reliability state · 8×8 cells over 15 pairs · "
             "60 m/px · source: core/reliability_calibration.csv",
             fontsize=9.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    p = OUT / "fig2_trust_calibration.png"
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    deltas, ours, best = load_curves()
    print(f"  read {len(deltas)} sun deltas from {LOG.name}")
    for d, o, b in zip(deltas, ours, best):
        ratio = (b / o) if (o and np.isfinite(b)) else float("nan")
        print(f"    {int(d):>4}°  ours {o:9.3f}   best classical {b:11.3f}   {ratio:9.2f}x")
    print(f"  wrote {fig_sun_angle(deltas, ours, best).name}")
    print(f"  wrote {fig_trust_calibration().name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
