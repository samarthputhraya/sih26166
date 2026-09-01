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
UPSTREAM_CKPT = (
    pathlib.Path(torch.hub.get_dir())
    / "checkpoints"
    / "loftr_outdoor.ckpt"
)

UPSTREAM_BYTES = 46_341_978
UPSTREAM_SHA256 = (
    "21f5bec5968178e8bc8b7633441836fe5de4f47d861dd2cd7dc38e271b0479ec"
)

WEIGHTS_BYTES = 46_348_591
WEIGHTS_SHA256 = (
    "6d2e110de3d1cffa53d42638ad155270938e85a59f6075ba8f600a44bb255896"
)

# A timing row with fewer matches than this did not exercise the fine stage.
MIN_MEANINGFUL_MATCHES = 500

# A pass slower than this multiple of the run's median is considered thrashing.
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
    """Sample this process's RSS on a thread."""

    def __init__(self, interval: float = 0.05) -> None:
        self.interval = interval
        self.peak = 0
        self._stop = threading.Event()
        self._proc = psutil.Process()

    def __enter__(self) -> "PeakRSS":
        self.peak = self._proc.memory_info().rss
        self._t = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self._t.start()
        return self

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.peak = max(
                    self.peak,
                    self._proc.memory_info().rss,
                )
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
    """
    Prove Gate-4 offline safety without physically switching wifi off.
    """

    def __enter__(self):
        self._real = socket.socket

        def blocked(*a, **k):
            raise NetworkBlocked(
                "network access attempted while the offline guard was active"
            )

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
    return (
        p.stat().st_size,
        hashlib.sha256(p.read_bytes()).hexdigest(),
    )


def verify_weights() -> dict:
    """
    Hash both files before use.
    Runs outside every timed region.
    """

    if not WEIGHTS.exists():
        raise SystemExit(
            f"missing {WEIGHTS}\n"
            "weights/ is gitignored, so a fresh clone has to rebuild it. "
            "Run once, with network:\n"
            "    python core/fetch_weights.py\n"
            "Or copy weights/loftr_outdoor.pt from the Drive folder."
        )

    n, digest = _sha256(WEIGHTS)

    if (n, digest) != (WEIGHTS_BYTES, WEIGHTS_SHA256):
        raise SystemExit(
            f"{WEIGHTS.name} does not match its pinned identity\n"
            f"  expected {WEIGHTS_BYTES} bytes / {WEIGHTS_SHA256}\n"
            f"  found    {n} bytes / {digest}\n"
            "Refusing to benchmark: a different checkpoint makes "
            "the number incomparable.\n"
            "If you regenerated it deliberately, re-pin WEIGHTS_SHA256 "
            "in this file."
        )

    upstream = (
        "absent (cache cleared) - provenance unverifiable this run"
    )

    if UPSTREAM_CKPT.exists():
        un, ud = _sha256(UPSTREAM_CKPT)

        ok = (un, ud) == (
            UPSTREAM_BYTES,
            UPSTREAM_SHA256,
        )

        upstream = (
            f"{'verified' if ok else 'MISMATCH'} "
            f"{ud[:16]}..."
        )

        if not ok:
            raise SystemExit(
                f"upstream {UPSTREAM_CKPT.name} does not match "
                f"its pin ({un} bytes / {ud}).\n"
                "The torch hub cache was replaced. "
                "Re-download and re-derive before benchmarking."
            )

    return {
        "weights_sha256": digest,
        "upstream": upstream,
    }


def build_matcher(offline: bool = True):
    """
    Construct LoFTR without touching the network.

    Handles both checkpoint formats:

    1. Raw state_dict
    2. {"state_dict": state_dict}
    """

    from kornia.feature import LoFTR
    from kornia.feature.loftr.loftr import default_cfg

    cfg = copy.deepcopy(default_cfg)

    # Correct setting for outdoor weights.
    cfg["coarse"]["temp_bug_fix"] = False

    with (no_network() if offline else _null_ctx()):

        m = LoFTR(
            pretrained=None,
            config=cfg,
        )

        # ------------------------------------------------------------
        # FIX:
        # The checkpoint may either be:
        #
        #     state_dict
        #
        # or:
        #
        #     {"state_dict": state_dict}
        #
        # Handle both safely.
        # ------------------------------------------------------------

        checkpoint = torch.load(
            WEIGHTS,
            map_location="cpu",
            weights_only=True,
        )

        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint

        m.load_state_dict(
            state_dict,
            strict=True,
        )

        m.eval()

    assert (
        m.pos_encoding.temp_bug_fix is False
    ), "positional encoding config was poisoned"

    return m


# ------------------------------------------------------------------ test data

def lunar_tile(
    size: int,
    seed: int,
    sun_az_deg: float,
) -> torch.Tensor:
    """
    A deterministic lunar-ish grayscale tile.
    """

    rng = np.random.default_rng(seed)

    # Low-frequency terrain.
    coarse = rng.normal(
        0.0,
        1.0,
        (
            max(4, size // 32),
            max(4, size // 32),
        ),
    )

    terrain = torch.nn.functional.interpolate(
        torch.from_numpy(coarse)[None, None].float(),
        size=(size, size),
        mode="bicubic",
        align_corners=False,
    )[0, 0].numpy()

    # Craters.
    yy, xx = np.mgrid[
        0:size,
        0:size,
    ].astype(np.float32)

    for _ in range(max(6, size // 80)):

        cx, cy = rng.uniform(
            0,
            size,
            2,
        )

        r = rng.uniform(
            size * 0.03,
            size * 0.12,
        )

        d = (
            np.sqrt(
                (xx - cx) ** 2
                + (yy - cy) ** 2
            )
            / r
        )

        bowl = np.where(
            d < 1.0,
            -np.sqrt(
                np.clip(
                    1.0 - d ** 2,
                    0.0,
                    None,
                )
            ),
            0.0,
        )

        rim = np.where(
            (d >= 1.0) & (d < 1.25),
            0.35 * (1.25 - d) / 0.25,
            0.0,
        )

        terrain = (
            terrain
            + (bowl + rim).astype(np.float32)
            * rng.uniform(0.5, 1.5)
        )

    # Hillshade.
    gy, gx = np.gradient(
        terrain.astype(np.float32)
    )

    az = np.deg2rad(sun_az_deg)
    el = np.deg2rad(35.0)

    shaded = (
        np.sin(el)
        - np.cos(el)
        * (
            np.cos(az) * gx
            + np.sin(az) * gy
        )
    )

    # Lunar imagery is low contrast.
    shaded = (
        shaded - shaded.min()
    ) / (
        np.ptp(shaded) + 1e-8
    )

    shaded = (
        0.30
        + 0.45 * shaded
    )

    return torch.from_numpy(
        shaded.astype(np.float32)
    )[None, None]


def make_pair(
    kind: str,
    size: int,
) -> tuple[torch.Tensor, torch.Tensor]:

    if kind == "noise":

        g = torch.Generator().manual_seed(0)

        return (
            torch.rand(
                1,
                1,
                size,
                size,
                generator=g,
            ),
            torch.rand(
                1,
                1,
                size,
                size,
                generator=g,
            ),
        )

    a = lunar_tile(
        size,
        seed=42,
        sun_az_deg=135.0,
    )

    b = lunar_tile(
        size,
        seed=42,
        sun_az_deg=155.0,
    )

    b = torch.roll(
        b,
        shifts=(7, 11),
        dims=(2, 3),
    )

    return a, b


# ----------------------------------------------------------------- the timing

def one_pass(
    matcher,
    a,
    b,
) -> tuple[float, int, int]:

    proc = psutil.Process()

    f0 = proc.memory_info().num_page_faults

    with torch.inference_mode():

        t0 = time.perf_counter()

        out = matcher(
            {
                "image0": a,
                "image1": b,
            }
        )

        dt = time.perf_counter() - t0

    f1 = proc.memory_info().num_page_faults

    return (
        dt,
        int(out["keypoints0"].shape[0]),
        f1 - f0,
    )


def drop_thrash(
    times: list[float],
) -> tuple[list[float], int]:

    if len(times) < 4:
        return times, 0

    med = statistics.median(times)

    kept = [
        t
        for t in times
        if t <= OUTLIER_MULTIPLE * med
    ]

    return (
        (kept, len(times) - len(kept))
        if kept
        else (times, 0)
    )


def summarise(
    times: list[float],
    matches: int,
) -> dict:

    return {
        "median_s": round(
            statistics.median(times),
            3,
        ),
        "min_s": round(
            min(times),
            3,
        ),
        "max_s": round(
            max(times),
            3,
        ),
        "stdev_s": round(
            statistics.stdev(times),
            3,
        ) if len(times) > 1 else 0.0,
        "matches": matches,
    }


def time_one(
    matcher,
    a,
    b,
    warmup: int,
    repeats: int,
) -> dict:

    with torch.inference_mode():

        for _ in range(warmup):
            matcher(
                {
                    "image0": a,
                    "image1": b,
                }
            )

        times = []
        matches = 0

        for _ in range(repeats):

            t0 = time.perf_counter()

            out = matcher(
                {
                    "image0": a,
                    "image1": b,
                }
            )

            times.append(
                time.perf_counter() - t0
            )

            matches = int(
                out["keypoints0"].shape[0]
            )

    return {
        "median_s": round(
            statistics.median(times),
            3,
        ),
        "min_s": round(
            min(times),
            3,
        ),
        "max_s": round(
            max(times),
            3,
        ),
        "stdev_s": round(
            statistics.stdev(times),
            3,
        ) if len(times) > 1 else 0.0,
        "matches": matches,
    }


def main() -> None:

    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[480, 640, 1024],
    )

    ap.add_argument(
        "--threads",
        type=int,
        nargs="+",
        default=None,
        help=(
            "thread counts to sweep at 640 "
            "(default: 4, 6, 8 and the torch default)"
        ),
    )

    ap.add_argument(
        "--warmup",
        type=int,
        default=2,
    )

    ap.add_argument(
        "--repeats",
        type=int,
        default=5,
    )

    ap.add_argument(
        "--drift-passes",
        type=int,
        default=18,
    )

    ap.add_argument(
        "--thread-rounds",
        type=int,
        default=4,
    )

    ap.add_argument(
        "--headroom-gb",
        type=float,
        default=1.0,
    )

    ap.add_argument(
        "--force",
        action="store_true",
    )

    ap.add_argument(
        "--allow-network",
        action="store_true",
        help=(
            "disable the offline guard "
            "(only needed for first weight download)"
        ),
    )

    args = ap.parse_args()

    env = env_metadata()

    print("=" * 74)
    print("LoFTR CPU BENCHMARK - SIH26166 Day 1")
    print("=" * 74)

    for k, v in env.items():
        print(f"  {k:20s} {v}")

    if env["ram_available_gb"] < 4:
        print(
            f"\n  !! only {env['ram_available_gb']} GB RAM free. "
            "Close Chrome/VS Code and rerun"
        )
        print(
            "     for a clean number, or read the large sizes as pessimistic."
        )

    print()

    proc = psutil.Process()

    default_threads = torch.get_num_threads()

    ver = verify_weights()

    print(
        f"  weights verified: "
        f"{WEIGHTS.name}, "
        f"sha256 {ver['weights_sha256'][:16]}..."
    )

    print(
        f"  upstream ckpt:    {ver['upstream']}"
    )

    matcher = build_matcher(
        offline=not args.allow_network
    )

    print(
        f"  loaded {WEIGHTS.name} offline "
        f"({sum(p.numel() for p in matcher.parameters()) / 1e6:.2f} M params)"
    )

    print(
        "  offline guard PASSED - "
        "no socket opened during construction or load"
    )

    model_rss = proc.memory_info().rss

    print(
        f"  resident before inference: "
        f"{model_rss / 1e9:.2f} GB\n"
    )

    rows: list[dict] = []

    activation_ref: tuple[int, float] | None = None

    # --------------------------------------------------------- SIZE SWEEP

    print("-" * 74)

    print(
        f"SIZE SWEEP  "
        f"(lunar-like tiles, {default_threads} threads, "
        f"{args.warmup} warmup + {args.repeats} timed)"
    )

    print("-" * 74)

    print(
        f"  {'size':>6} "
        f"{'median':>9} "
        f"{'min':>8} "
        f"{'max':>8} "
        f"{'sd':>7} "
        f"{'match':>7} "
        f"{'peakRAM':>9}"
    )

    for size in sorted(args.sizes):

        if activation_ref and not args.force:

            ref_size, ref_gb = activation_ref

            est_gb = (
                ref_gb
                * (size / ref_size) ** 2
            )

            avail = (
                psutil.virtual_memory()
                .available
                / 1e9
            )

            if est_gb + args.headroom_gb > avail:

                print(
                    f"  {size:>6}  SKIPPED - "
                    f"needs ~{est_gb:.1f} GB of activations, "
                    f"only {avail:.1f} GB free "
                    f"(--force to override)"
                )

                rows.append(
                    {
                        "mode": "size_sweep",
                        "size": size,
                        "threads": default_threads,
                        "input": "lunar",
                        "note": "skipped_low_memory",
                    }
                )

                continue

        a, b = make_pair(
            "lunar",
            size,
        )

        with PeakRSS() as rss:

            r = time_one(
                matcher,
                a,
                b,
                args.warmup,
                args.repeats,
            )

        activation_gb = max(
            0.05,
            (rss.peak - model_rss) / 1e9,
        )

        if activation_ref is None:
            activation_ref = (
                size,
                activation_gb,
            )

        weak = (
            "  <-- TOO FEW MATCHES, not decision-grade"
            if r["matches"] < MIN_MEANINGFUL_MATCHES
            else ""
        )

        print(
            f"  {size:>6} "
            f"{r['median_s']:>8.2f}s "
            f"{r['min_s']:>7.2f}s "
            f"{r['max_s']:>7.2f}s "
            f"{r['stdev_s']:>6.2f}s "
            f"{r['matches']:>7} "
            f"{rss.peak_gb:>8.2f}G"
            f"{weak}"
        )

        rows.append(
            {
                "mode": "size_sweep",
                "size": size,
                "threads": default_threads,
                "input": "lunar",
                "peak_rss_gb": rss.peak_gb,
                "decision_grade": (
                    r["matches"]
                    >= MIN_MEANINGFUL_MATCHES
                ),
                **r,
            }
        )

    # ------------------------------------------------------ THERMAL DRIFT

    print("\n" + "-" * 74)

    print(
        f"THERMAL DRIFT at 640^2 "
        f"({args.drift_passes} back-to-back passes, "
        f"{default_threads} threads)"
    )

    print("-" * 74)

    a, b = make_pair(
        "lunar",
        640,
    )

    for _ in range(args.warmup):
        one_pass(
            matcher,
            a,
            b,
        )

    drift = []
    m = 0

    for i in range(args.drift_passes):

        dt, m, pf = one_pass(
            matcher,
            a,
            b,
        )

        avail = (
            psutil.virtual_memory()
            .available
            / 1e9
        )

        drift.append(
            {
                "t": dt,
                "pf": pf,
                "avail": avail,
            }
        )

        print(
            f"  pass {i + 1:>2}: "
            f"{dt:>6.2f}s  "
            f"pf={pf:>7}  "
            f"free={avail:>4.1f}G  "
            f"{'#' * min(60, int(dt * 4))}"
        )

    series, dropped = drop_thrash(
        [d["t"] for d in drift]
    )

    if dropped:
        print(
            f"\n  {dropped}/{len(drift)} passes "
            f"dropped as thrash "
            f"(>{OUTLIER_MULTIPLE}x median)"
        )

    k = max(
        3,
        len(series) // 3,
    )

    cold = statistics.median(
        series[:k]
    )

    steady = statistics.median(
        series[-k:]
    )

    drift_pct = (
        (steady - cold)
        / cold
        * 100
    )

    print(
        f"\n  n={len(series)}   "
        f"first {k} median {cold:.2f}s   "
        f"last {k} median {steady:.2f}s   "
        f"drift {drift_pct:+.0f}%"
    )

    if dropped > len(drift) // 4:

        print(
            "  !! MEMORY PRESSURE DOMINATES. "
            "This machine cannot produce a decision-grade"
        )

        print(
            "     number right now. "
            "Free ~4 GB and rerun before quoting anything."
        )

    elif abs(drift_pct) > 15:

        print(
            "  -> genuine thermal throttling "
            "under sustained load."
        )

        print(
            "     QUOTE THE STEADY-STATE NUMBER."
        )

    rows.append(
        {
            "mode": "drift",
            "size": 640,
            "threads": default_threads,
            "input": "lunar",
            "cold_median_s": round(cold, 3),
            "steady_median_s": round(steady, 3),
            "drift_pct": round(drift_pct, 1),
            "thrash_dropped": dropped,
            **summarise(series, m),
        }
    )

    # ------------------------------------------------ CONTENT SENSITIVITY

    print("\n" + "-" * 74)
    print(
        "CONTENT SENSITIVITY at 640^2 "
        "(why a torch.rand harness misleads)"
    )
    print("-" * 74)

    pairs = {
        k: make_pair(k, 640)
        for k in ("noise", "lunar")
    }

    acc: dict[str, list[float]] = {
        "noise": [],
        "lunar": [],
    }

    mm: dict[str, int] = {}

    for rnd in range(args.repeats):

        order = (
            ("noise", "lunar")
            if rnd % 2 == 0
            else ("lunar", "noise")
        )

        for kind in order:

            dt, mm[kind], _ = one_pass(
                matcher,
                *pairs[kind],
            )

            acc[kind].append(dt)

    acc = {
        k: drop_thrash(v)[0]
        for k, v in acc.items()
    }

    for kind in ("noise", "lunar"):

        r = summarise(
            acc[kind],
            mm[kind],
        )

        print(
            f"  {kind:>6} input: "
            f"{r['median_s']:>6.2f}s   "
            f"matches={r['matches']}"
        )

        rows.append(
            {
                "mode": "content",
                "size": 640,
                "threads": default_threads,
                "input": kind,
                **r,
            }
        )

    gap = (
        (
            statistics.median(acc["lunar"])
            - statistics.median(acc["noise"])
        )
        / statistics.median(acc["lunar"])
        * 100
    )

    print(
        f"  -> torch.rand under-reports latency by "
        f"{gap:.0f}% and exercises the fine stage"
    )

    print(
        f"     on {mm['noise']} matches instead of "
        f"{mm['lunar']}. Never benchmark on noise."
    )

    # ------------------------------------------------------- THREAD SWEEP

    sweep = (
        args.threads
        if args.threads
        else sorted(
            {
                4,
                6,
                8,
                10,
                default_threads,
            }
        )
    )

    print("\n" + "-" * 74)

    print(
        f"THREAD SWEEP at 640^2 "
        f"({args.thread_rounds} interleaved rounds, "
        f"order rotated)"
    )

    print(
        "  Core Ultra 5 125H = "
        "4 P-cores + 8 E-cores + 2 LP-E cores (14C/18T)"
    )

    print("-" * 74)

    a, b = make_pair(
        "lunar",
        640,
    )

    tacc: dict[int, list[float]] = {
        n: []
        for n in sweep
    }

    thread_matches = 0

    for rnd in range(args.thread_rounds):

        offset = rnd % len(sweep)

        order = (
            sweep[offset:]
            + sweep[:offset]
        )

        for n in order:

            torch.set_num_threads(n)

            one_pass(
                matcher,
                a,
                b,
            )

            dt, thread_matches, _ = one_pass(
                matcher,
                a,
                b,
            )

            tacc[n].append(dt)

    tacc = {
        n: drop_thrash(v)[0]
        for n, v in tacc.items()
    }

    torch.set_num_threads(
        default_threads
    )

    best: tuple[int, float] | None = None

    usable = {
        n: v
        for n, v in tacc.items()
        if v
    }

    for n in sweep:

        if not tacc[n]:

            print(
                f"  {n:>3} threads: "
                "every pass paged - no usable timing"
            )

            rows.append(
                {
                    "mode": "thread_sweep",
                    "size": 640,
                    "threads": n,
                    "input": "lunar",
                    "note": "all_passes_paged",
                }
            )

            continue

        med = statistics.median(
            tacc[n]
        )

        spread = (
            f"{min(tacc[n]):.2f}-"
            f"{max(tacc[n]):.2f}"
        )

        if best is None or med < best[1]:
            best = (
                n,
                med,
            )

        print(
            f"  {n:>3} threads: "
            f"{med:>6.2f}s   "
            f"(n={len(tacc[n])}, "
            f"spread {spread})"
        )

        rows.append(
            {
                "mode": "thread_sweep",
                "size": 640,
                "threads": n,
                "input": "lunar",
                **summarise(
                    tacc[n],
                    thread_matches,
                ),
            }
        )

    if best and len(usable) > 1:

        spread_all = (
            max(
                statistics.median(v)
                for v in usable.values()
            )
            - min(
                statistics.median(v)
                for v in usable.values()
            )
        )

        print(
            f"  -> best {best[0]} threads "
            f"at {best[1]:.2f}s; "
            f"total spread across settings "
            f"{spread_all:.2f}s"
        )

        if spread_all < 1.0:

            print(
                "     That is within run-to-run noise "
                "on this machine - thread count is"
            )

            print(
                "     NOT a lever worth tuning. "
                "Keep the torch default."
            )

    # ------------------------------------------------------------ VERDICT

    at640 = next(
        (
            r
            for r in rows
            if r["mode"] == "size_sweep"
            and r["size"] == 640
            and r.get("median_s")
        ),
        None,
    )

    print("\n" + "=" * 74)
    print("VERDICT")
    print("=" * 74)

    drift_row = next(
        (
            r
            for r in rows
            if r["mode"] == "drift"
        ),
        None,
    )

    if at640 is None:

        print(
            "  640^2 did not run - "
            "no tile-size call can be made."
        )

    else:

        cold_t = at640["median_s"]

        t = (
            drift_row["steady_median_s"]
            if drift_row
            else cold_t
        )

        print(
            f"  640^2 cold:         "
            f"{cold_t:.2f}s   "
            f"(spread "
            f"{at640['min_s']:.2f}-"
            f"{at640['max_s']:.2f}s, "
            f"peak RAM "
            f"{at640.get('peak_rss_gb')} GB, "
            f"{at640['matches']} matches)"
        )

        if drift_row:

            print(
                f"  640^2 STEADY STATE: "
                f"{t:.2f}s   "
                f"({drift_row['drift_pct']:+.0f}% vs cold)  "
                f"<-- QUOTE THIS ONE"
            )

        if not at640.get(
            "decision_grade"
        ):

            print(
                f"  !! only {at640['matches']} matches "
                f"(<{MIN_MEANINGFUL_MATCHES}): "
                "the fine stage"
            )

            print(
                "     barely ran, so this latency "
                "is optimistic. "
                "Do NOT commit a tile size to it."
            )

        if t < COMFORTABLE_S:

            print(
                "  -> LIVE INFERENCE IS COMFORTABLE. "
                "Tile 640. The UI can align on click."
            )

        elif t < NARRATABLE_S:

            print(
                "  -> LIVE BUT NARRATED. "
                "Tile 640, the UI needs a progress bar."
            )

        else:

            print(
                "  -> TOO SLOW FOR LIVE at 640. "
                "Drop to 480, or precompute the demo results"
            )

            print(
                "     and say ON SCREEN that they are cached."
            )

        if cold_t < NARRATABLE_S <= t:

            print(
                "  !! the cold and steady numbers "
                "straddle a decision threshold."
            )

            print(
                "     The plan must follow the STEADY number."
            )

        if (
            best
            and best[0] != default_threads
            and best[1] < t * 0.9
        ):

            print(
                f"  -> torch.set_num_threads({best[0]}) "
                f"gives {best[1]:.2f}s, "
                f"{(t - best[1]) / t * 100:.0f}% "
                f"faster than the "
                f"{default_threads}-thread default."
            )

    # ------------------------------------------------------------- CSV

    OUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = sorted(
        {
            k
            for r in rows
            for k in r
        }
        | {"env"}
    )

    with open(
        OUT_CSV,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        w = csv.DictWriter(
            f,
            fieldnames=fields,
        )

        w.writeheader()

        for r in rows:

            w.writerow(
                {
                    **r,
                    "env": json.dumps(env),
                }
            )

    print(
        f"\n  rows -> "
        f"{OUT_CSV.relative_to(REPO)}"
    )

    print(
        "  Report the 640^2 median to the team."
    )

    print(
        "  Samrudh copies it into results_log.csv; "
        "nothing quotes it from anywhere else."
    )


if __name__ == "__main__":
    main()