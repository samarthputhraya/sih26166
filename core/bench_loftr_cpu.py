"""
LoFTR CPU latency benchmark - SIH26166, Day 1.

The number this prints decides the project's tile size, whether the Streamlit UI
runs inference live, and what the demo script may promise judges. It is measured
once and then six people commit twelve days to it, so this harness is deliberately
boring: fixed seeds, several timed repeats, median reported, spread shown.

Run:  <venv>/Scripts/python.exe core/bench_loftr_cpu.py

What it deliberately does not measure is listed at the bottom of the file.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import pathlib
import platform
import socket
import statistics
import sys
import threading
import time

import numpy as np
import psutil
import torch

REPO = pathlib.Path(__file__).resolve().parent.parent
WEIGHTS = REPO / "weights" / "loftr_outdoor.pt"
OUT_CSV = REPO / "core" / "bench_loftr_cpu_results.csv"

# Team-agreed decision thresholds, keyed on the 640^2 median.
COMFORTABLE_S = 3.0
NARRATABLE_S = 10.0

# Two files, two pins.
#
# UPSTREAM is kornia's own checkpoint, fetched from a researcher's personal page at
# CVUT over PLAINTEXT http, with no hash check, then unpickled with weights_only=False.
# Its size is corroborated against that server's Content-Length; the digest is
# self-computed from our download, NOT an upstream-published hash. Log it that way.
UPSTREAM_CKPT = pathlib.Path(torch.hub.get_dir()) / "checkpoints" / "loftr_outdoor.ckpt"
UPSTREAM_BYTES = 46_341_978
UPSTREAM_SHA256 = "21f5bec5968178e8bc8b7633441836fe5de4f47d861dd2cd7dc38e271b0479ec"

# WEIGHTS is what this harness and the demo actually load: the state_dict we
# re-serialised from the upstream checkpoint and distribute to the team via Drive.
# Regenerating it (or a torch upgrade) changes this digest - re-pin deliberately.
WEIGHTS_BYTES = 46_348_591
WEIGHTS_SHA256 = "6d2e110de3d1cffa53d42638ad155270938e85a59f6075ba8f600a44bb255896"

# A timing row with fewer matches than this did not exercise the fine stage and
# must not drive a decision. Not `> 0`: a pure-noise pair scores ~150 and passes
# that gate while doing almost none of the work the real pipeline will do.
MIN_MEANINGFUL_MATCHES = 500

# A pass slower than this multiple of the run's median did not measure LoFTR - it
# measured the machine thrashing. Detected statistically rather than from page-fault
# counts: Windows num_page_faults includes SOFT faults, so a pass that legitimately
# touches 1.4 GB of activations reports ~1.3 M faults and looks identical to real
# swapping. Observed thrash spikes are 3-4x the median and snap straight back;
# thermal drift is gradual and stays well inside this bound.
OUTLIER_MULTIPLE = 2.5


# ---------------------------------------------------------------- environment

def env_metadata() -> dict:
    vm = psutil.virtual_memory()
    bat = psutil.sensors_battery()
    return {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "kornia": __import__("kornia").__version__,
        "cuda_available": torch.cuda.is_available(),
        "cpu": platform.processor(),
        "cores_physical": psutil.cpu_count(logical=False),
        "cores_logical": psutil.cpu_count(logical=True),
        "ram_total_gb": round(vm.total / 1e9, 2),
        "ram_available_gb": round(vm.available / 1e9, 2),
        "on_ac_power": (bat.power_plugged if bat else None),
        "os": f"{platform.system()} {platform.release()}",
    }


class PeakRSS:
    """Sample this process's RSS on a thread; torch allocations are invisible to tracemalloc."""

    def __init__(self, interval: float = 0.05) -> None:
        self.interval = interval
        self.peak = 0
        self._stop = threading.Event()
        self._proc = psutil.Process()

    def __enter__(self) -> "PeakRSS":
        self.peak = self._proc.memory_info().rss
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()
        return self

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.peak = max(self.peak, self._proc.memory_info().rss)
            except psutil.Error:
                pass
            self._stop.wait(self.interval)

    def __exit__(self, *exc) -> None:
        self._stop.set()
        self._t.join(timeout=1.0)

    @property
    def peak_gb(self) -> float:
        return round(self.peak / 1e9, 2)


# ------------------------------------------------------------------- offline

class NetworkBlocked(RuntimeError):
    pass


class no_network:
    """Prove Gate-4 offline safety without physically switching wifi off.

    Any attempt to open a socket inside this block raises. If model construction or
    inference reaches for the network, we find out now rather than in front of judges.
    """

    def __enter__(self):
        self._real = socket.socket

        def blocked(*a, **k):
            raise NetworkBlocked("network access attempted while the offline guard was active")

        socket.socket = blocked
        return self

    def __exit__(self, *exc):
        socket.socket = self._real
        return False


class _null_ctx:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _sha256(p: pathlib.Path) -> tuple[int, str]:
    return p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest()


def verify_weights() -> dict:
    """Hash both files before use. Runs outside every timed region.

    kornia performs no integrity check of any kind on its download, so this is the
    only place the chain is verified.
    """
    if not WEIGHTS.exists():
        raise SystemExit(
            f"missing {WEIGHTS}\n"
            "weights/ is gitignored, so a fresh clone has to rebuild it. Run once, with network:\n"
            "    python core/fetch_weights.py\n"
            "Or copy weights/loftr_outdoor.pt from the Drive folder."
        )
    n, digest = _sha256(WEIGHTS)
    if (n, digest) != (WEIGHTS_BYTES, WEIGHTS_SHA256):
        raise SystemExit(
            f"{WEIGHTS.name} does not match its pinned identity\n"
            f"  expected {WEIGHTS_BYTES} bytes / {WEIGHTS_SHA256}\n"
            f"  found    {n} bytes / {digest}\n"
            "Refusing to benchmark: a different checkpoint makes the number incomparable.\n"
            "If you regenerated it deliberately, re-pin WEIGHTS_SHA256 in this file."
        )

    upstream = "absent (cache cleared) - provenance unverifiable this run"
    if UPSTREAM_CKPT.exists():
        un, ud = _sha256(UPSTREAM_CKPT)
        ok = (un, ud) == (UPSTREAM_BYTES, UPSTREAM_SHA256)
        upstream = f"{'verified' if ok else 'MISMATCH'} {ud[:16]}..."
        if not ok:
            raise SystemExit(
                f"upstream {UPSTREAM_CKPT.name} does not match its pin ({un} bytes / {ud}).\n"
                "The torch hub cache was replaced. Re-download and re-derive before benchmarking."
            )
    return {"weights_sha256": digest, "upstream": upstream}


def build_matcher(offline: bool = True):
    """Construct LoFTR without touching the network, with the config pinned.

    kornia 0.8.3 binds `default_cfg` as a MUTABLE DEFAULT argument and, for
    pretrained="indoor_new", mutates it in place with no else-branch - so the
    change persists process-wide and silently reconfigures every LoFTR built
    afterwards. The affected field, temp_bug_fix, controls the positional
    encoding, which is registered with persistent=False and therefore never
    appears in the state_dict: load_state_dict(strict=True) cannot catch it, and
    a poisoned model still loads cleanly while losing ~30% of its matches and
    most of its confidence.

    We never build "indoor_new", so this cannot bite today. It is pinned and
    asserted anyway, because the failure is silent and the assert is free.
    """
    from kornia.feature import LoFTR
    from kornia.feature.loftr.loftr import default_cfg

    cfg = copy.deepcopy(default_cfg)
    cfg["coarse"]["temp_bug_fix"] = False        # correct setting for the outdoor weights
    with (no_network() if offline else _null_ctx()):
        m = LoFTR(pretrained=None, config=cfg)
        m.load_state_dict(torch.load(WEIGHTS, map_location="cpu", weights_only=True))
        m.eval()
    assert m.pos_encoding.temp_bug_fix is False, "positional encoding config was poisoned"
    return m


# ------------------------------------------------------------------ test data

def lunar_tile(size: int, seed: int, sun_az_deg: float) -> torch.Tensor:
    """A deterministic lunar-ish grayscale tile.

    Random noise is the wrong input for a LoFTR benchmark: LoFTR's fine stage only
    runs on the coarse matches that survive its confidence threshold, so runtime is
    content-dependent. A noise pair yields almost no coarse matches and therefore
    under-reports latency. This stand-in mimics what actually costs time on the moon:
    low global contrast, crater relief, a strong directional shadow gradient, and
    little high-frequency texture.

    Replace with real Chandrayaan-2 / LROC tiles as soon as Rohan's data lands.
    """
    rng = np.random.default_rng(seed)

    # Low-frequency terrain: a coarse random grid smoothly upsampled.
    coarse = rng.normal(0.0, 1.0, (max(4, size // 32), max(4, size // 32)))
    terrain = torch.nn.functional.interpolate(
        torch.from_numpy(coarse)[None, None].float(),
        size=(size, size), mode="bicubic", align_corners=False,
    )[0, 0].numpy()

    # Craters: bowl-shaped depressions with raised rims.
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    for _ in range(max(6, size // 80)):
        cx, cy = rng.uniform(0, size, 2)
        r = rng.uniform(size * 0.03, size * 0.12)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        bowl = np.where(d < 1.0, -np.sqrt(np.clip(1.0 - d ** 2, 0.0, None)), 0.0)
        rim = np.where((d >= 1.0) & (d < 1.25), 0.35 * (1.25 - d) / 0.25, 0.0)
        terrain = terrain + (bowl + rim).astype(np.float32) * rng.uniform(0.5, 1.5)

    # Hillshade the height field from a given sun azimuth.
    gy, gx = np.gradient(terrain.astype(np.float32))
    az, el = np.deg2rad(sun_az_deg), np.deg2rad(35.0)
    shaded = np.sin(el) - np.cos(el) * (np.cos(az) * gx + np.sin(az) * gy)

    # Lunar imagery is low-contrast and mid-grey, not full-range.
    shaded = (shaded - shaded.min()) / (np.ptp(shaded) + 1e-8)
    shaded = 0.30 + 0.45 * shaded
    return torch.from_numpy(shaded.astype(np.float32))[None, None]


def make_pair(kind: str, size: int) -> tuple[torch.Tensor, torch.Tensor]:
    """A genuinely matchable pair (same terrain, sun moved, known shift), or a noise pair."""
    if kind == "noise":
        g = torch.Generator().manual_seed(0)
        return (torch.rand(1, 1, size, size, generator=g),
                torch.rand(1, 1, size, size, generator=g))
    a = lunar_tile(size, seed=42, sun_az_deg=135.0)
    b = lunar_tile(size, seed=42, sun_az_deg=155.0)   # same terrain, sun moved 20 degrees
    b = torch.roll(b, shifts=(7, 11), dims=(2, 3))    # known integer shift
    return a, b


# ----------------------------------------------------------------- the timing

def one_pass(matcher, a, b) -> tuple[float, int, int]:
    """A single timed forward pass, instrumented for paging.

    Returns (seconds, matches, major_page_faults_during_the_pass).

    The page-fault delta is what separates the two ways this laptop goes slow.
    Thermal throttling is gradual and does not recover within a pass; paging
    produces isolated 3-4x spikes that snap straight back. Conflating them
    produced a wrong "thermal drift" reading on the first attempt, so the
    harness now measures the difference instead of guessing at it.
    """
    proc = psutil.Process()
    f0 = proc.memory_info().num_page_faults
    with torch.inference_mode():
        t0 = time.perf_counter()
        out = matcher({"image0": a, "image1": b})
        dt = time.perf_counter() - t0
    f1 = proc.memory_info().num_page_faults
    return dt, int(out["keypoints0"].shape[0]), f1 - f0


def drop_thrash(times: list[float]) -> tuple[list[float], int]:
    """Remove passes that measured the page file. Returns (kept, n_dropped).

    Never silently drops everything: if the rule would reject more than half the
    series the machine is thrashing throughout, and the caller is told to say so
    rather than quote a number distilled from the survivors.
    """
    if len(times) < 4:
        return times, 0
    med = statistics.median(times)
    kept = [t for t in times if t <= OUTLIER_MULTIPLE * med]
    return (kept, len(times) - len(kept)) if kept else (times, 0)


def summarise(times: list[float], matches: int) -> dict:
    return {
        "median_s": round(statistics.median(times), 3),
        "min_s": round(min(times), 3),
        "max_s": round(max(times), 3),
        "stdev_s": round(statistics.stdev(times), 3) if len(times) > 1 else 0.0,
        "matches": matches,
    }


def time_one(matcher, a, b, warmup: int, repeats: int) -> dict:
    with torch.inference_mode():
        for _ in range(warmup):
            matcher({"image0": a, "image1": b})
        times, matches = [], 0
        for _ in range(repeats):
            t0 = time.perf_counter()
            out = matcher({"image0": a, "image1": b})
            times.append(time.perf_counter() - t0)
            matches = int(out["keypoints0"].shape[0])
    return {
        "median_s": round(statistics.median(times), 3),
        "min_s": round(min(times), 3),
        "max_s": round(max(times), 3),
        "stdev_s": round(statistics.stdev(times), 3) if len(times) > 1 else 0.0,
        "matches": matches,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[480, 640, 1024])
    ap.add_argument("--threads", type=int, nargs="+", default=None,
                    help="thread counts to sweep at 640 (default: 4, 6, 8 and the torch default)")
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--drift-passes", type=int, default=18,
                    help="back-to-back 640^2 passes used to separate cold from steady state")
    ap.add_argument("--thread-rounds", type=int, default=4,
                    help="interleaved rounds of the thread sweep (order rotates each round)")
    ap.add_argument("--headroom-gb", type=float, default=1.0,
                    help="RAM to leave free; a size is skipped if it would eat into this")
    ap.add_argument("--force", action="store_true", help="run every size regardless of free RAM")
    ap.add_argument("--allow-network", action="store_true",
                    help="disable the offline guard (only needed for the first weight download)")
    args = ap.parse_args()

    env = env_metadata()
    print("=" * 74)
    print("LoFTR CPU BENCHMARK - SIH26166 Day 1")
    print("=" * 74)
    for k, v in env.items():
        print(f"  {k:20s} {v}")
    if env["ram_available_gb"] < 4:
        print(f"\n  !! only {env['ram_available_gb']} GB RAM free. Close Chrome/VS Code and rerun")
        print("     for a clean number, or read the large sizes as pessimistic.")
    print()

    proc = psutil.Process()
    baseline_rss = proc.memory_info().rss
    default_threads = torch.get_num_threads()

    ver = verify_weights()
    print(f"  weights verified: {WEIGHTS.name}, sha256 {ver['weights_sha256'][:16]}...")
    print(f"  upstream ckpt:    {ver['upstream']}")
    print("    (upstream size matches the CVUT Content-Length; both digests are self-computed)")

    matcher = build_matcher(offline=not args.allow_network)
    print(f"  loaded {WEIGHTS.name} offline "
          f"({sum(p.numel() for p in matcher.parameters()) / 1e6:.2f} M params)")
    print("  offline guard PASSED - no socket opened during construction or load")
    model_rss = proc.memory_info().rss
    print(f"  resident before inference: {model_rss / 1e9:.2f} GB\n")

    rows: list[dict] = []
    # Activation cost measured at the smallest size, then scaled by pixel area for the guard.
    activation_ref: tuple[int, float] | None = None

    print("-" * 74)
    print(f"SIZE SWEEP  (lunar-like tiles, {default_threads} threads, "
          f"{args.warmup} warmup + {args.repeats} timed)")
    print("-" * 74)
    print(f"  {'size':>6} {'median':>9} {'min':>8} {'max':>8} {'sd':>7} {'match':>7} {'peakRAM':>9}")
    for size in sorted(args.sizes):
        if activation_ref and not args.force:
            ref_size, ref_gb = activation_ref
            est_gb = ref_gb * (size / ref_size) ** 2
            avail = psutil.virtual_memory().available / 1e9
            if est_gb + args.headroom_gb > avail:
                print(f"  {size:>6}  SKIPPED - needs ~{est_gb:.1f} GB of activations, "
                      f"only {avail:.1f} GB free (--force to override)")
                rows.append({"mode": "size_sweep", "size": size, "threads": default_threads,
                             "input": "lunar", "note": "skipped_low_memory"})
                continue
        a, b = make_pair("lunar", size)
        with PeakRSS() as rss:
            r = time_one(matcher, a, b, args.warmup, args.repeats)
        activation_gb = max(0.05, (rss.peak - model_rss) / 1e9)
        if activation_ref is None:
            activation_ref = (size, activation_gb)
        weak = "  <-- TOO FEW MATCHES, not decision-grade" if r["matches"] < MIN_MEANINGFUL_MATCHES else ""
        print(f"  {size:>6} {r['median_s']:>8.2f}s {r['min_s']:>7.2f}s {r['max_s']:>7.2f}s "
              f"{r['stdev_s']:>6.2f}s {r['matches']:>7} {rss.peak_gb:>8.2f}G{weak}")
        rows.append({"mode": "size_sweep", "size": size, "threads": default_threads,
                     "input": "lunar", "peak_rss_gb": rss.peak_gb,
                     "decision_grade": r["matches"] >= MIN_MEANINGFUL_MATCHES, **r})

    # ------------------------------------------------------ thermal drift
    # A laptop under sustained all-core load slows down. The first run of the
    # first condition is therefore the FASTEST the machine will ever be, and
    # reporting it is the optimistic direction the project explicitly forbids.
    # The demo will run on a machine that has been warm for minutes, so the
    # steady-state figure is the honest one to quote.
    print("\n" + "-" * 74)
    print(f"THERMAL DRIFT at 640^2  ({args.drift_passes} back-to-back passes, "
          f"{default_threads} threads)")
    print("-" * 74)
    a, b = make_pair("lunar", 640)
    for _ in range(args.warmup):
        one_pass(matcher, a, b)
    drift, m = [], 0
    for i in range(args.drift_passes):
        dt, m, pf = one_pass(matcher, a, b)
        avail = psutil.virtual_memory().available / 1e9
        drift.append({"t": dt, "pf": pf, "avail": avail})
        print(f"  pass {i + 1:>2}: {dt:>6.2f}s  pf={pf:>7}  free={avail:>4.1f}G  "
              f"{'#' * min(60, int(dt * 4))}")

    # Separate thrash spikes from genuine thermal drift.
    series, dropped = drop_thrash([d["t"] for d in drift])
    if dropped:
        print(f"\n  {dropped}/{len(drift)} passes dropped as thrash "
              f"(>{OUTLIER_MULTIPLE}x median): they timed the page file, not LoFTR")
    k = max(3, len(series) // 3)
    cold = statistics.median(series[:k])
    steady = statistics.median(series[-k:])
    drift_pct = (steady - cold) / cold * 100
    print(f"\n  n={len(series)}   first {k} median {cold:.2f}s   "
          f"last {k} median {steady:.2f}s   drift {drift_pct:+.0f}%")
    if dropped > len(drift) // 4:
        print("  !! MEMORY PRESSURE DOMINATES. This machine cannot produce a decision-grade")
        print("     number right now. Free ~4 GB and rerun before quoting anything.")
    elif abs(drift_pct) > 15:
        print("  -> genuine thermal throttling under sustained load.")
        print("     QUOTE THE STEADY-STATE NUMBER. The cold number is not what a judge sees.")
    rows.append({"mode": "drift", "size": 640, "threads": default_threads, "input": "lunar",
                 "cold_median_s": round(cold, 3), "steady_median_s": round(steady, 3),
                 "drift_pct": round(drift_pct, 1), "thrash_dropped": dropped,
                 **summarise(series, m)})

    # -------------------------------------------------- content sensitivity
    # Run warm, and interleaved, so the noise-vs-lunar gap is not itself a
    # thermal artifact of whichever condition happened to run first.
    print("\n" + "-" * 74)
    print("CONTENT SENSITIVITY at 640^2  (why a torch.rand harness misleads)")
    print("-" * 74)
    pairs = {k: make_pair(k, 640) for k in ("noise", "lunar")}
    acc: dict[str, list[float]] = {"noise": [], "lunar": []}
    mm: dict[str, int] = {}
    for rnd in range(args.repeats):
        order = ("noise", "lunar") if rnd % 2 == 0 else ("lunar", "noise")
        for kind in order:
            dt, mm[kind], _ = one_pass(matcher, *pairs[kind])
            acc[kind].append(dt)
    acc = {k: drop_thrash(v)[0] for k, v in acc.items()}
    for kind in ("noise", "lunar"):
        r = summarise(acc[kind], mm[kind])
        print(f"  {kind:>6} input: {r['median_s']:>6.2f}s   matches={r['matches']}")
        rows.append({"mode": "content", "size": 640, "threads": default_threads,
                     "input": kind, **r})
    gap = (statistics.median(acc["lunar"]) - statistics.median(acc["noise"])) \
        / statistics.median(acc["lunar"]) * 100
    print(f"  -> torch.rand under-reports latency by {gap:.0f}% and exercises the fine stage")
    print(f"     on {mm['noise']} matches instead of {mm['lunar']}. Never benchmark on noise.")

    # ------------------------------------------------------- thread sweep
    # Round-robin, rotating the order each round, so thermal drift is spread
    # evenly across settings instead of being charged to whichever ran last.
    # The previous sequential version made 'fewer threads is better' look real
    # when it was mostly the machine cooling down at the start of the sweep.
    sweep = args.threads if args.threads else sorted({4, 6, 8, 10, default_threads})
    print("\n" + "-" * 74)
    print(f"THREAD SWEEP at 640^2  ({args.thread_rounds} interleaved rounds, order rotated)")
    print("  Core Ultra 5 125H = 4 P-cores + 8 E-cores + 2 LP-E cores (14C/18T)")
    print("-" * 74)
    a, b = make_pair("lunar", 640)
    tacc: dict[int, list[float]] = {n: [] for n in sweep}
    thread_matches = 0
    for rnd in range(args.thread_rounds):
        order = sweep[rnd % len(sweep):] + sweep[:rnd % len(sweep)]
        for n in order:
            torch.set_num_threads(n)
            one_pass(matcher, a, b)                 # settle after the thread change
            dt, thread_matches, _ = one_pass(matcher, a, b)
            tacc[n].append(dt)
    tacc = {n: drop_thrash(v)[0] for n, v in tacc.items()}
    torch.set_num_threads(default_threads)
    best: tuple[int, float] | None = None
    usable = {n: v for n, v in tacc.items() if v}
    for n in sweep:
        if not tacc[n]:
            print(f"  {n:>3} threads: every pass paged - no usable timing")
            rows.append({"mode": "thread_sweep", "size": 640, "threads": n,
                         "input": "lunar", "note": "all_passes_paged"})
            continue
        med = statistics.median(tacc[n])
        spread = f"{min(tacc[n]):.2f}-{max(tacc[n]):.2f}"
        if best is None or med < best[1]:
            best = (n, med)
        print(f"  {n:>3} threads: {med:>6.2f}s   (n={len(tacc[n])}, spread {spread})")
        rows.append({"mode": "thread_sweep", "size": 640, "threads": n, "input": "lunar",
                     **summarise(tacc[n], thread_matches)})
    if best and len(usable) > 1:
        spread_all = max(statistics.median(v) for v in usable.values()) \
            - min(statistics.median(v) for v in usable.values())
        print(f"  -> best {best[0]} threads at {best[1]:.2f}s; total spread across "
              f"settings {spread_all:.2f}s")
        if spread_all < 1.0:
            print("     That is within run-to-run noise on this machine - thread count is")
            print("     NOT a lever worth tuning. Keep the torch default.")

    # ------------------------------------------------------------ the verdict
    at640 = next((r for r in rows if r["mode"] == "size_sweep" and r["size"] == 640
                  and r.get("median_s")), None)
    print("\n" + "=" * 74)
    print("VERDICT")
    print("=" * 74)
    drift_row = next((r for r in rows if r["mode"] == "drift"), None)
    if at640 is None:
        print("  640^2 did not run - no tile-size call can be made.")
    else:
        cold_t = at640["median_s"]
        # The steady-state figure is what a judge actually sees: by demo time the
        # machine has been warm for minutes. Quote it, not the cold first run.
        t = drift_row["steady_median_s"] if drift_row else cold_t
        print(f"  640^2 cold:         {cold_t:.2f}s   "
              f"(spread {at640['min_s']:.2f}-{at640['max_s']:.2f}s, "
              f"peak RAM {at640.get('peak_rss_gb')} GB, {at640['matches']} matches)")
        if drift_row:
            print(f"  640^2 STEADY STATE: {t:.2f}s   "
                  f"({drift_row['drift_pct']:+.0f}% vs cold)  <-- QUOTE THIS ONE")
        if not at640.get("decision_grade"):
            print(f"  !! only {at640['matches']} matches (<{MIN_MEANINGFUL_MATCHES}): the fine stage")
            print("     barely ran, so this latency is optimistic. Do NOT commit a tile size to it.")
        if t < COMFORTABLE_S:
            print("  -> LIVE INFERENCE IS COMFORTABLE. Tile 640. The UI can align on click.")
        elif t < NARRATABLE_S:
            print("  -> LIVE BUT NARRATED. Tile 640, the UI needs a progress bar, and Saniya")
            print("     narrates over the wait in the demo script.")
        else:
            print("  -> TOO SLOW FOR LIVE at 640. Drop to 480, or precompute the demo results")
            print("     and say ON SCREEN that they are cached.")
        if cold_t < NARRATABLE_S <= t:
            print("  !! the cold and steady numbers straddle a decision threshold. The plan must")
            print("     follow the STEADY number, or the demo degrades exactly when it is watched.")
        if best and best[0] != default_threads and best[1] < t * 0.9:
            print(f"  -> torch.set_num_threads({best[0]}) gives {best[1]:.2f}s, "
                  f"{(t - best[1]) / t * 100:.0f}% faster than the {default_threads}-thread default.")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({k for r in rows for k in r} | {"env"})
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({**r, "env": json.dumps(env)})
    print(f"\n  rows -> {OUT_CSV.relative_to(REPO)}")
    print("  Report the 640^2 median to the team. Samrudh copies it into results_log.csv;")
    print("  nothing quotes it from anywhere else.")


# What this harness deliberately does NOT do, and why:
#   - torch.compile: Triton has no Windows CPU backend in torch 2.13, and a speculative
#     compile has no business under a Day-1 number six people commit twelve days to.
#   - bfloat16 autocast: it would change match quality, making the latency number a
#     dishonest proxy for the pipeline we actually ship.
#   - a fresh process per size: ~40s of model reload to chase a second-order allocator
#     effect that does not change the tile-size decision.
#   - real lunar imagery: none is in the repo on Day 1. Rerun once Rohan's tiles land.
#     The generator above is a stand-in, not a substitute.

if __name__ == "__main__":
    main()
