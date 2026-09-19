"""The evidence freeze: re-run every piece of evidence on ONE clean commit.

    python -m ops.freeze --plan              # what would run, how long it took last time; runs nothing
    python -m ops.freeze                     # run every step not yet done at this commit (resumes)
    python -m ops.freeze --only real loops   # a subset, by step name
    python -m ops.freeze --skip gate2        # everything but these
    python -m ops.freeze --check             # is every latest evidence row at this commit?

WHY. Every number in REPORT.md and the deck must come from the code being submitted. Until
now the evidence was produced over three days by a dozen commits (and some by an uncommitted
tree), so a trust-layer change made earlier verdicts stale without anything saying so.

WHAT IS RE-RUN, and where the list comes from. The real-pair work list is NOT typed here: it
is read from the evidence itself - the latest row of every pair in real_pairs_log.csv, and the
exact command that produced it:
  real      every pair whose latest row came from `ops.run_real_pairs`, re-run BY EXACT ID.
            A glob would be wrong: `site_ohrc_m1153871873le_w*` also matches the sweep's `_sw`
            windows, and re-logging those through run_real_pairs writes a latest row with no
            `outcome`, which silently drops them out of the sweep table.
  sweep     `ops.sun_sweep --rerun --log`, only for the NACs whose windows are stale.
  loops     each `ops.loop_closure` command exactly as logged (after `real`: it reads the legs'
            exported bundles).
  mmcheck   `ops.multimodal_check --log`: the infrared fallback against the visible-band
            registration of the same window, from the bundles `real` exported.
  trust     `ops.trust_real_calibration` on the same windows the current calibration used,
            plus the pinned hard-Sun patterns (`trust_real_calibration.EXTRA_WINDOWS`), after
            deleting its per-trial CSV (Known issue 8: every run appends to it).
  miloi     `evaluation.miloi --retrust --truth --score --log --table`: re-judges the stored
            matches under the current trust layer, rebuilds the truth, re-scores every method.
            Matching itself (LoFTR, SIFT/ORB/AKAZE, ~50 s a pair, ~4.5 h) is not redone: --plan
            checks that the matching code has not changed since those matches were made.
  viewpoint the synthetic tilt sweep, without and with relief parallax (ops/specs/day_21.md).
  calib     the synthetic trust calibration, 40 pairs x 8 sun deltas (fig2).
  gate2     the synthetic sun sweep, ours and the classical baselines (fig1). Neither fig1 nor
            fig2 is in the v2 deck; skip with `--skip gate2 calib` when short of time.
  report    REPORT.md, the figures, the deck (the deck build exits 1 while it holds [TBD]s -
            recorded, not a failure).

RESUMING. State lives in <data>/freeze/<commit>/state.json with one log file per step. A step
done at this commit is skipped; `real` also skips pairs whose latest row already names this
commit, so a crash (Known issue 11, cv2) loses at most one pair. A failed step is retried once.

SLEEP. While it runs, the process asks Windows not to sleep (SetThreadExecutionState, released
at exit). That does not change any power setting - but closing the lid still follows the lid
setting, so leave it open.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
REAL = ROOT / "evaluation" / "real_pairs_log.csv"
MILOI_LOG = ROOT / "evaluation" / "miloi_log.csv"
TRUST_CSV = ROOT / "evaluation" / "trust_real_calibration.csv"
PY = sys.executable

# Code whose change would make the stored MiLOI matches stale (everything before MAGSAC++).
# evaluation/miloi.py is not listed: its matching loop has not changed, but its truth, retrust
# and scoring code does, and listing the whole file made every change look like a re-match.
MATCHING_CODE = ["core/matcher.py", "core/subpixel.py", "core/illumination.py", "core/scale.py",
                 "core/io_loader.py", "baselines"]
MM_CSV = ROOT / "evaluation" / "multimodal_check.csv"
STEPS = ("real", "sweep", "loops", "mmcheck", "trust", "miloi", "viewpoint", "calib", "gate2", "report")
CHUNK = 12          # pair ids per run_real_pairs process


def _data() -> pathlib.Path:
    return pathlib.Path((ROOT / "data_path.txt").read_text(encoding="utf-8-sig").strip())


def _rows(p):
    p = pathlib.Path(p)
    return list(csv.DictReader(open(p, encoding="utf-8-sig"))) if p.exists() else []


def latest_real(rows=None) -> dict:
    """{pair_id: latest row} of real_pairs_log, withdrawn (INVALIDATED) pairs left out."""
    out = {}
    for r in (_rows(REAL) if rows is None else rows):
        out[r["pair_id"]] = r
    return {k: r for k, r in out.items() if (r.get("verdict") or "") != "INVALIDATED"}


def stale_real(commit: str, rows=None) -> dict:
    """{pair_id: latest row} whose latest row does not name `commit` exactly."""
    return {k: r for k, r in latest_real(rows).items() if r.get("git_commit") != commit}


def plan_real(rows=None) -> dict:
    """The work list, from the evidence: {"real": {original command: [ids]}, "sweep": {NAC ids},
    "loops": [commands]}."""
    real, sweep, loops = {}, set(), []
    for pid, r in sorted(latest_real(rows).items()):
        cmd = r.get("command") or ""
        if cmd.startswith("python -m ops.run_real_pairs"):
            real.setdefault(cmd, []).append(pid)
        elif cmd.startswith("python -m ops.sun_sweep"):
            m = re.match(r"site_ohrc_(m\d+[lr]e)_w\d+_sw$", pid)
            if m:
                sweep.add(m.group(1).upper())
        elif cmd.startswith("python -m ops.loop_closure") and cmd not in loops:
            loops.append(cmd)
    return {"real": real, "sweep": sweep, "loops": loops}


def _seconds(rows, ids) -> float:
    """MEDIAN seconds per pair x pairs. Not the sum: `seconds` is wall time inside run_all, and
    rows run while the laptop slept (19 Sep 02:00-10:00) carry hours."""
    v = []
    for r in rows:
        if r["pair_id"] in ids:
            try:
                v.append(float(r.get("seconds") or 0))
            except ValueError:
                pass
    v.sort()
    return v[len(v) // 2] * len(ids) if v else 0.0


def _git(*args) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _code_dirty() -> list[str]:
    """Tracked or untracked CODE changes (evidence outputs excluded, as core.export._commit)."""
    from core.export import EVIDENCE_LOGS
    out = _git("status", "--porcelain", "--", "core", "evaluation", "ops", "baselines", "app",
               "presentation/build_deck.py", "presentation/make_figures.py",
               *(f":(exclude){p}" for p in EVIDENCE_LOGS))
    return [ln for ln in out.splitlines() if ln.strip()]


def miloi_matching_changed() -> list[str]:
    """Matching code changed since the commits the stored MiLOI matches were made at."""
    runs = set()
    for r in _rows(MILOI_LOG):
        m = re.match(r"run ([0-9a-f]{7,})", r.get("git_commit") or "")
        if m:
            runs.add(m.group(1))
    changed = []
    for c in sorted(runs):
        try:
            diff = _git("diff", "--name-only", c, "HEAD", "--", *MATCHING_CODE)
        except subprocess.CalledProcessError:
            changed.append(f"{c}: unknown commit")
            continue
        if diff:
            changed.append(f"{c}: " + ", ".join(diff.split()))
    return changed


# --- keep-awake ----------------------------------------------------------------------------

def _awake(on: bool) -> None:
    if os.name != "nt":
        return
    import ctypes
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))


# --- running ---------------------------------------------------------------------------------

def _run(argv: list[str], logf) -> int:
    """One subprocess, output teed to the step log and the console."""
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    line = "$ " + " ".join(argv)
    print(line, flush=True)
    logf.write(line + "\n")
    p = subprocess.Popen([PY, *argv], cwd=ROOT, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    for ln in p.stdout:
        if "Warning" in ln or "warn(" in ln:
            logf.write(ln)
            continue
        sys.stdout.write("    " + ln)
        logf.write(ln)
    rc = p.wait()
    logf.write(f"[exit {rc}]\n")
    logf.flush()
    return rc


class Freeze:
    def __init__(self, commit: str):
        self.commit = commit
        self.dir = _data() / "freeze" / commit
        self.dir.mkdir(parents=True, exist_ok=True)
        self.state_p = self.dir / "state.json"
        self.state = (json.loads(self.state_p.read_text(encoding="utf-8")) if self.state_p.exists()
                      else {"commit": commit, "started_utc": _now(), "steps": {}})

    def save(self):
        self.state_p.write_text(json.dumps(self.state, indent=1), encoding="utf-8")

    def done(self, step) -> bool:
        return self.state["steps"].get(step, {}).get("status") == "done"

    def step(self, name, fn):
        if self.done(name):
            print(f"== {name}: done at {self.commit} - skipped")
            return True
        print(f"\n== {name} ==", flush=True)
        rec = self.state["steps"].setdefault(name, {})
        rec.update(started=_now(), status="running", tries=rec.get("tries", 0) + 1)
        self.save()
        with open(self.dir / f"{name}.log", "a", encoding="utf-8") as logf:
            ok = fn(logf)
            if ok is False:          # None = a precondition failed; retrying cannot help
                print(f"   {name}: failed - retrying once (Known issue 11)", flush=True)
                ok = fn(logf)
        rec.update(ended=_now(), status="done" if ok else "failed")
        self.save()
        return ok

    # the steps -----------------------------------------------------------------------------

    def real(self, logf):
        work, stale = plan_real()["real"], stale_real(self.commit)
        todo = {c: [i for i in ids if i in stale] for c, ids in work.items()}
        ok = True
        for cmd, ids in todo.items():
            for k in range(0, len(ids), CHUNK):
                ok &= _run(["-m", "ops.run_real_pairs", *ids[k:k + CHUNK], "--log"], logf) == 0
        return ok

    def sweep(self, logf):
        stale = stale_real(self.commit)
        nacs = sorted({m.group(1).upper() for pid in stale
                       for m in [re.match(r"site_ohrc_(m\d+[lr]e)_w\d+_sw$", pid)] if m})
        if not nacs:
            return True
        return _run(["-m", "ops.sun_sweep", "--windows", "3", "--log", "--rerun", "--only", *nacs],
                    logf) == 0

    def loops(self, logf):
        # A loop is computed from its three legs' exported bundles; legs from an older commit
        # would give a loop row stamped with this commit and built on stale registrations.
        stale = stale_real(self.commit)
        ok = True
        for cmd in plan_real()["loops"]:
            a_, b_ = (re.search(rf"--{k} (\S+)", cmd).group(1).lower() for k in ("a", "b"))
            m = re.search(r"--tag (\S+)", cmd)
            tag = f"_{m.group(1)}" if m else ""
            legs = [p for p in stale if re.fullmatch(
                rf"site_(ohrc_{a_}|{a_}_{b_}|ohrc_{b_})_w\d+{tag}", p)]
            if legs:
                print(f"   {len(legs)} leg(s) of this loop are not at {self.commit} "
                      f"({', '.join(legs[:3])}...) - run the `real` step first")
                return None
            ok &= _run(cmd.split()[1:], logf) == 0      # drop "python"
        return ok

    def mmcheck(self, logf):
        # Compares the bundles `real` exported; a bundle from an older commit would be compared
        # against one from this commit.
        from ops.multimodal_check import pairings
        stale = stale_real(self.commit)
        need = [p for pr in pairings(latest_real()) for p in (pr["pair_id"], pr["against"])]
        old = [p for p in need if p in stale]
        if old:
            print(f"   {len(old)} multi-modal pair(s) not at {self.commit} ({', '.join(old[:3])}...) "
                  f"- run the `real` step first")
            return None
        return _run(["-m", "ops.multimodal_check", "--log"], logf) == 0

    def trust(self, logf):
        wins = self.state.get("trust_windows")
        if not wins:                                    # read BEFORE the CSV is deleted
            import glob
            from ops.trust_real_calibration import EXTRA_WINDOWS
            wins = {r["pair_id"] for r in _rows(TRUST_CSV)}
            if not wins:
                print("   no trust_real_calibration.csv to take the windows from")
                return None
            # The hard-Sun windows (20 Sep 2026): the script itself skips any that fail its rule.
            for pat in EXTRA_WINDOWS:
                wins |= {pathlib.Path(p).name for p in glob.glob(str(ROOT / "data" / "pairs" / pat))}
            wins = sorted(wins)
            # one id per GROUND window: w01_t and w04 of M1153871873LE are the same window cut
            # twice (Known issue 2), which counted its 74 trials twice
            from presentation.make_figures import _distinct_windows
            dup = [ids[1:] for ids in _distinct_windows(wins).values() if len(ids) > 1]
            wins = [w for w in wins if not any(w in d for d in dup)]
            self.state["trust_windows_dropped_as_duplicates"] = [w for d in dup for w in d]
            self.state["trust_windows"] = wins
            self.save()
        if TRUST_CSV.exists():
            TRUST_CSV.unlink()
        return _run(["-m", "ops.trust_real_calibration", *wins, "--log"], logf) == 0

    def miloi(self, logf):
        return _run(["-m", "evaluation.miloi", "--retrust", "--truth", "--score", "--log", "--table"],
                    logf) == 0

    def viewpoint(self, logf):
        dem = str(_data() / "raw" / "dem_site_60m.npy")
        base = ["-m", "core.pipeline", "--synthetic", "--dem", dem, "--pixel-size", "60",
                "--sun-delta", "15", "--tilt-sweep", "0,10,20,30,40,50", "--repeats", "3",
                "--log", "--allow-failed"]
        a = _run(base, logf)
        b = _run(base + ["--parallax"], logf)
        return a in (0, 1) and b in (0, 1)              # 1 = some pair failed, logged anyway

    def calib(self, logf):
        dem = str(_data() / "raw" / "dem_site_60m.npy")
        return _run(["-m", "core.reliability_calibrate", "--dem", dem, "--pixel-size", "60",
                     "--sweep", "0,15,30,45,60,90,120,180", "--repeats", "5", "--log", "--quiet"],
                    logf) == 0

    def gate2(self, logf):
        dem = str(_data() / "raw" / "dem_site_60m.npy")
        sweep = ["--dem", dem, "--pixel-size", "60", "--sweep", "0,15,30,45,60,90,120,180",
                 "--repeats", "5", "--log"]
        a = _run(["-m", "core.pipeline", "--synthetic", *sweep, "--allow-failed"], logf)
        b = _run(["-m", "baselines.sweep_baselines", *sweep], logf)
        return a in (0, 1) and b == 0

    def report(self, logf):
        from presentation.make_figures import FIG3_PAIRS    # fig3 draws cached run_all dicts
        if _run(["-m", "ops.precompute_demo_cache", *FIG3_PAIRS], logf) != 0:
            return False
        a = _run(["-m", "ops.make_report"], logf)
        b = _run(["-m", "presentation.make_figures"], logf)
        c = _run(["-m", "presentation.build_deck"], logf)    # 1 while [TBD]s remain
        self.state["deck_build_exit"] = c
        return a == 0 and b == 0


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def check(commit: str) -> int:
    """Every latest evidence row at `commit`? Prints what is stale; returns the stale count."""
    stale = stale_real(commit)
    fam = {}
    for pid in stale:
        fam.setdefault(re.sub(r"_w\d+.*$", "_w*", pid), []).append(pid)
    print(f"real_pairs_log: {len(latest_real()) - len(stale)}/{len(latest_real())} latest rows at {commit}")
    for f, ids in sorted(fam.items()):
        print(f"   stale  {f:44} {len(ids)}")
    latest = {}
    for r in _rows(MILOI_LOG):
        latest[(r["pair_id"], r["method"])] = r
    ms = [k for k, r in latest.items() if not (r.get("git_commit") or "").endswith(f"scored {commit}")]
    print(f"miloi_log: {len(latest) - len(ms)}/{len(latest)} latest rows scored at {commit}")
    mm = {}
    for r in _rows(MM_CSV):
        mm[r["pair_id"]] = r
    mms = [k for k, r in mm.items() if r.get("git_commit") != commit]
    print(f"multimodal_check: {len(mm) - len(mms)}/{len(mm)} latest rows at {commit}")
    st_p = _data() / "freeze" / commit / "state.json"
    steps = json.loads(st_p.read_text(encoding="utf-8"))["steps"] if st_p.exists() else {}
    for s in STEPS:
        print(f"   step {s:10} {steps.get(s, {}).get('status', 'not run')}")
    n = len(stale) + len(ms) + len(mms) + sum(1 for s in STEPS if steps.get(s, {}).get("status") != "done")
    print("FROZEN" if n == 0 else f"NOT FROZEN: {n} stale item(s)")
    return n


def plan() -> None:
    rows = _rows(REAL)
    p = plan_real(rows)
    n_real = sum(len(v) for v in p["real"].values())
    print(f"real   {n_real} pairs by exact id, from {len(p['real'])} logged commands; last time "
          f"{_seconds(rows, {i for v in p['real'].values() for i in v}) / 60:.0f} min of registration")
    for cmd, ids in p["real"].items():
        print(f"         {len(ids):3d}  (was: {cmd})")
    sw_ids = {k for k in latest_real(rows) if k.endswith("_sw")}
    print(f"sweep  {len(p['sweep'])} NACs, {len(sw_ids)} windows; last time {_seconds(rows, sw_ids) / 60:.0f} min")
    for c in p["loops"]:
        print(f"loops  {c}")
    wins = sorted({r['pair_id'] for r in _rows(TRUST_CSV)})
    from ops.trust_real_calibration import EXTRA_WINDOWS
    print(f"trust  {len(wins)} windows (the current calibration's) + the hard-Sun patterns "
          f"{' '.join(EXTRA_WINDOWS)}, CSV deleted first")
    from ops.multimodal_check import pairings
    print(f"mmcheck {len(pairings(latest_real(rows)))} window pairings from the bundles")
    changed = miloi_matching_changed()
    print("miloi  --retrust --truth --score --log --table; matching code "
          + ("UNCHANGED since the stored matches" if not changed else "CHANGED since the stored "
             "matches - re-match first (evaluation.miloi --run on an emptied miloi_runs):\n         "
             + "\n         ".join(changed)))
    print("viewpoint, calib, gate2: synthetic sweeps (see the docstring); report: REPORT.md, figures, deck")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", nargs="*", choices=STEPS)
    ap.add_argument("--skip", nargs="*", choices=STEPS, default=[])
    ap.add_argument("--allow-dirty", action="store_true", help="for testing the runner only")
    a = ap.parse_args(argv)
    from core.export import _commit
    commit = _commit(("core", "evaluation", "ops"))
    if a.plan:
        print(f"commit {commit}")
        dirty = _code_dirty()
        if dirty:
            print("code is NOT clean - commit first:\n  " + "\n  ".join(dirty))
        plan()
        return 0
    if a.check:
        return 1 if check(commit) else 0
    if _code_dirty() and not a.allow_dirty:
        print("refusing: the code is not committed (a freeze must name a clean commit):\n  "
              + "\n  ".join(_code_dirty()))
        return 2
    steps = [s for s in (a.only or STEPS) if s not in a.skip]
    fz = Freeze(commit)
    print(f"freeze at {commit}: {' '.join(steps)}   (state and logs: {fz.dir})")
    _awake(True)
    t0 = time.time()
    try:
        results = {s: fz.step(s, getattr(fz, s)) for s in steps}
    finally:
        _awake(False)
    print(f"\n== freeze at {commit}: {sum(results.values())}/{len(results)} steps ok in "
          f"{(time.time() - t0) / 60:.0f} min ==")
    for s, ok in results.items():
        print(f"   {s:10} {'ok' if ok else 'FAILED - see ' + str(fz.dir / (s + '.log'))}")
    print()
    check(commit)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
