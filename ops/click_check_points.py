"""Click independent check points: the same feature in a pair's source and reference, by hand.

    python -m ops.click_check_points --list                       # the windows to click, and progress
    python -m ops.click_check_points <pair_id> --clicker <name>    # click 15-20 points
    python -m ops.click_check_points <pair_id> --clicker <name> --repeat 5   # later: re-click 5

The point of a check point is that it knows nothing about the registration it judges. So this tool
never reads a registration: it opens only the pair's two images and its geometry_prior.json, and it
shows the source around where the ARCHIVE georeference (the prior) puts the reference feature - the
archive is off by metres to ~100 m, which is why the source panel spans +-150 m and can be panned.

Four panels:
  top left      the whole reference. Click a feature you can find again: a small crater's centre,
                a boulder. Not a shadow edge - shadows move with the Sun.
  top right     the reference around it, magnified. Click the feature's exact centre (red +).
  bottom left   the source where the archive expects that feature (+-150 m). Find the same
                feature and click it (pan/zoom with the toolbar if it is not there).
  bottom right  the source magnified. Click its exact centre (cyan +).
Keys: Enter accept the pair of clicks   Backspace remove the last accepted point
      1 / 2 / 3 confidence (low / normal / sure; default 2)   c contrast   i invert the source
      q save and quit. Every accepted point is written immediately: nothing is lost on a crash.
--repeat N re-shows N of your accepted points WITHOUT their markers; click both images again. Do it
at least an hour after the first pass: the difference measures how precisely features are clicked.

Writes evaluation/check_points/<pair_id>.csv (columns: evaluation.check_points.FIELDS).
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import pathlib
import random
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from evaluation.check_points import CP_DIR, FIELDS, pair_paths, read_csv, sha12  # noqa: E402

# The windows to click (3 Oct 2026 plan, E3): SAC's equatorial pair on SAC's own 1.1179 m grid; Site N's
# three legs; the real viewpoint test; the 74 S whole-overlap windows whose archive offset is small
# enough for the +-150 m source panel. Ordered so the most-asked-about pairs come first.
TARGETS = (
    # SAC's equatorial pair on its paper's grid (Suns 174 deg apart)
    "sac_ohrc_nac112_w01", "sac_ohrc_nac112_w02", "sac_ohrc_nac112_w03", "sac_ohrc_nac112_w04",
    # Site N, Chandrayaan-2 OHRC -> TMC-2 under matched Suns (archive offset 48-49 m)
    "siten_ohrc2031_tmc20200607_c00", "siten_ohrc2031_tmc20200607_c01",
    # Site N, OHRC -> LRO NAC (offset 7-16 m)
    "siten_ohrc2031_nacm1282456834re_c02", "siten_ohrc2031_nacm1282456834re_c03",
    "siten_ohrc2031_nacm1282456834re_c04",
    # 74 S whole lit overlap, OHRC -> NAC (offset 3-4 m)
    "site_ohrc_m1153871873le_w04_full", "site_ohrc_m1153871873le_w09_full", "site_ohrc_m1153871873le_w25_full",
    # real viewpoint test, OHRC -> OHRC 40 deg apart (relief parallax is part of what remains)
    "siten_ohrc2031_ohrc2229_c06", "siten_ohrc2031_ohrc2229_c09", "siten_ohrc2031_ohrc2229_c15",
    # Site N, LRO NAC -> TMC-2 (offset 90-96 m: pan the source panel if the feature is not in it)
    "siten_nacm1282456834re_tmc20200607_c00", "siten_nacm1282456834re_tmc20200607_c01",
    "siten_nacm1282456834re_tmc20200607_c02",
)
HALF_REF_ZOOM = 40          # reference px each side of the magnified view
SOURCE_SPAN_M = 150.0       # metres each side of the archive-predicted source position
CONTRASTS = (("whole image", 2, 98, False), ("this view", 2, 98, True), ("this view, wide", 0.5, 99.5, True))


def _stretch(img, lo, hi, region=None):
    a = img if region is None else region
    f = a[np.isfinite(a)]
    if f.size == 0:
        return np.zeros_like(img)
    p0, p1 = np.percentile(f, [lo, hi])
    if p1 <= p0:
        p1 = p0 + 1e-6
    return np.clip((img - p0) / (p1 - p0), 0, 1)


def _read(path):
    import tifffile
    a = tifffile.imread(str(path)).astype(np.float32)
    if a.ndim == 3:
        a = a[..., 0]
    a[~np.isfinite(a)] = np.nanmedian(a)
    return a


def _apply(H, x, y):
    p = np.asarray(H, np.float64) @ np.array([x, y, 1.0])
    return p[0] / p[2], p[1] / p[2]


def _rows(path):
    return read_csv(path) if path.exists() else []


def _append(path, row):
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in FIELDS})


def _rewrite(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


class Clicker:
    def __init__(self, pair_id, clicker, repeat=0):
        import os

        import matplotlib
        matplotlib.use(os.environ.get("LUNAXX_CLICK_BACKEND", "TkAgg"))   # tests run it headless (Agg)
        import matplotlib.pyplot as plt
        self.plt = plt
        self.pair_id, self.clicker = pair_id, clicker
        src_p, ref_p, prior_p = pair_paths(pair_id)
        g = json.loads(prior_p.read_text(encoding="utf-8"))
        self.ref_gsd = float(g["reference"]["resampled_gsd_mpp"])
        self.src_gsd = float(g["source"]["resampled_gsd_mpp"])
        self.H_prior_inv = np.linalg.inv(np.asarray(g["prior_H_source_to_reference"], np.float64))
        self.ref, self.src = _read(ref_p), _read(src_p)
        self.sha = (sha12(src_p), sha12(ref_p))
        self.csv = CP_DIR / f"{pair_id}.csv"
        rows = _rows(self.csv)
        for r in rows:
            if (r["src_sha12"], r["ref_sha12"]) != self.sha:
                raise SystemExit(f"{self.csv.name} holds clicks made on other files - move it aside first")
        self.rows = rows
        self.queue = []
        if repeat:
            done = {r["repeat_of"] for r in rows if r.get("repeat_of")}
            pool = [r for r in rows if not r.get("repeat_of") and r["point_id"] not in done]
            random.shuffle(pool)
            self.queue = pool[:repeat]
            if not self.queue:
                raise SystemExit("no accepted points left to repeat")
        self.contrast, self.invert, self.conf = 1, False, 2
        self.ref_pt = self.src_pt = None
        self.ref_focus = (self.ref.shape[1] / 2, self.ref.shape[0] / 2)
        self.src_focus = self._predict(*self.ref_focus)
        self.src_view = self.src_focus
        self.src_half = SOURCE_SPAN_M / self.src_gsd
        self.src_zoom_half = HALF_REF_ZOOM * self.ref_gsd / self.src_gsd
        fig, axs = plt.subplots(2, 2, figsize=(14, 11))
        self.fig, (self.aR, self.aRz), (self.aS, self.aSz) = fig, axs[0], axs[1]
        fig.canvas.mpl_connect("button_press_event", self.on_click)
        fig.canvas.mpl_connect("key_press_event", self.on_key)
        if self.queue:
            self._next_repeat()
        self.draw()

    def _predict(self, u, v):
        return _apply(self.H_prior_inv, u, v)

    def _accepted(self):
        return [r for r in self.rows if not r.get("repeat_of")]

    def _next_repeat(self):
        r = self.queue[0]
        self.ref_focus = (float(r["ref_x"]), float(r["ref_y"]))
        self.src_view = self.src_focus = self._predict(*self.ref_focus)
        self.ref_pt = self.src_pt = None

    def _show(self, ax, img, cx, cy, half, title, region_stretch, invert=False, marks=(), cur=None, col="r"):
        ax.clear()
        h, w = img.shape
        x0, x1 = int(max(0, cx - half)), int(min(w, cx + half + 1))
        y0, y1 = int(max(0, cy - half)), int(min(h, cy + half + 1))
        name, lo, hi, local = CONTRASTS[self.contrast]
        view = img[y0:y1, x0:x1]
        shown = _stretch(view, lo, hi, view if (local and region_stretch) else img)
        if invert:
            shown = 1.0 - shown
        ax.imshow(shown, cmap="gray", extent=(x0 - 0.5, x1 - 0.5, y1 - 0.5, y0 - 0.5), interpolation="nearest")
        for mx, my, lab in marks:
            if x0 <= mx < x1 and y0 <= my < y1:
                ax.plot(mx, my, "+", color="yellow", ms=8, mew=1)
                ax.annotate(lab, (mx, my), color="yellow", fontsize=8, xytext=(3, 3), textcoords="offset points")
        if cur is not None:
            ax.plot(cur[0], cur[1], "+", color=col, ms=18, mew=1.5)
        ax.set_xlim(x0 - 0.5, x1 - 0.5)
        ax.set_ylim(y1 - 0.5, y0 - 0.5)
        ax.set_title(title, fontsize=10)

    def draw(self):
        acc = self._accepted()
        marks = [] if self.queue else [(float(r["ref_x"]), float(r["ref_y"]), r["point_id"]) for r in acc]
        smarks = [] if self.queue else [(float(r["src_x"]), float(r["src_y"]), r["point_id"]) for r in acc]
        big = max(self.ref.shape) / 2
        self._show(self.aR, self.ref, self.ref.shape[1] / 2, self.ref.shape[0] / 2, big,
                   f"reference {self.ref.shape[1]}x{self.ref.shape[0]} @ {self.ref_gsd} m - click a feature",
                   False, marks=marks, cur=self.ref_focus, col="orange")
        self._show(self.aRz, self.ref, *self.ref_focus, HALF_REF_ZOOM,
                   "reference, magnified - click the feature's exact centre", True, marks=marks,
                   cur=self.ref_pt, col="red")
        self._show(self.aS, self.src, *self.src_view, self.src_half,
                   f"source @ {self.src_gsd} m, +-{SOURCE_SPAN_M:.0f} m around the archive's position - find it",
                   True, invert=self.invert, marks=smarks, cur=self.src_focus, col="orange")
        self._show(self.aSz, self.src, *self.src_focus, self.src_zoom_half,
                   "source, magnified - click the same centre", True, invert=self.invert, marks=smarks,
                   cur=self.src_pt, col="cyan")
        mode = (f"REPEAT {len(self.queue)} left (re-click point {self.queue[0]['point_id']})" if self.queue
                else f"{len(acc)} points accepted")
        self.fig.suptitle(f"{self.pair_id} - {mode} - confidence {self.conf} - contrast: "
                          f"{CONTRASTS[self.contrast][0]}{' - source inverted' if self.invert else ''}\n"
                          "Enter accept   Backspace drop last   1/2/3 confidence   c contrast   i invert   q quit",
                          fontsize=10)
        self.fig.canvas.draw_idle()

    def on_click(self, ev):
        tb = getattr(self.fig.canvas, "toolbar", None)
        if ev.inaxes is None or ev.xdata is None or (tb is not None and tb.mode):
            return                                    # the toolbar is panning or zooming
        x, y = float(ev.xdata), float(ev.ydata)
        # A panned source view stays where it was panned to.
        xl, yl = self.aS.get_xlim(), self.aS.get_ylim()
        self.src_view = ((xl[0] + xl[1]) / 2, (yl[0] + yl[1]) / 2)
        if ev.inaxes is self.aR and not self.queue:
            self.ref_focus = (x, y)
            self.ref_pt = None
            self.src_view = self.src_focus = self._predict(x, y)
            self.src_pt = None
        elif ev.inaxes is self.aRz:
            self.ref_pt = (x, y)
            if not self.queue:
                self.ref_focus = (x, y)
        elif ev.inaxes is self.aS:
            self.src_focus = (x, y)
            self.src_pt = None
        elif ev.inaxes is self.aSz:
            self.src_pt = (x, y)
        self.draw()

    def on_key(self, ev):
        k = ev.key
        if k == "enter":
            self.accept()
        elif k == "backspace":
            self.drop_last()
        elif k in ("1", "2", "3"):
            self.conf = int(k)
        elif k == "c":
            self.contrast = (self.contrast + 1) % len(CONTRASTS)
        elif k == "i":
            self.invert = not self.invert
        elif k == "q":
            self.plt.close(self.fig)
            return
        self.draw()

    def accept(self):
        if self.ref_pt is None or self.src_pt is None:
            print("  click the exact centre in BOTH magnified views first")
            return
        n = len(self.rows) + 1
        row = {"point_id": f"p{n:03d}", "src_x": f"{self.src_pt[0]:.2f}", "src_y": f"{self.src_pt[1]:.2f}",
               "ref_x": f"{self.ref_pt[0]:.2f}", "ref_y": f"{self.ref_pt[1]:.2f}",
               "repeat_of": self.queue[0]["point_id"] if self.queue else "", "confidence": self.conf,
               "feature": "", "clicker": self.clicker,
               "utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
               "src_sha12": self.sha[0], "ref_sha12": self.sha[1]}
        _append(self.csv, row)
        self.rows.append(row)
        print(f"  {row['point_id']}" + (f" (repeat of {row['repeat_of']})" if row["repeat_of"] else "") +
              f": ref ({row['ref_x']}, {row['ref_y']})  src ({row['src_x']}, {row['src_y']})")
        self.ref_pt = self.src_pt = None
        if self.queue:
            self.queue.pop(0)
            if self.queue:
                self._next_repeat()
            else:
                print("  repeats done")
                self.plt.close(self.fig)

    def drop_last(self):
        if not self.rows:
            return
        gone = self.rows.pop()
        _rewrite(self.csv, self.rows)
        print(f"  removed {gone['point_id']}")


def progress() -> int:
    print(f"{'pair':34s} {'points':>6s} {'repeats':>8s}")
    for pid in TARGETS:
        rows = _rows(CP_DIR / f"{pid}.csv")
        n_rep = sum(1 for r in rows if r.get("repeat_of"))
        print(f"{pid:34s} {len(rows) - n_rep:6d} {n_rep:8d}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pair_id", nargs="?")
    ap.add_argument("--clicker", help="your name, stored with every point")
    ap.add_argument("--repeat", type=int, default=0, help="re-click this many accepted points, unmarked")
    ap.add_argument("--list", action="store_true", help="the windows to click and how far each has got")
    a = ap.parse_args(argv)
    if a.list or not a.pair_id:
        return progress()
    if not a.clicker:
        raise SystemExit("--clicker <name> is required")
    if not pair_paths(a.pair_id)[0].exists():
        raise SystemExit(f"no pair {a.pair_id} under data/pairs")
    c = Clicker(a.pair_id, a.clicker, a.repeat)
    c.plt.show()
    acc = [r for r in c.rows if not r.get("repeat_of")]
    print(f"{a.pair_id}: {len(acc)} points, {len(c.rows) - len(acc)} repeats in {c.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
