"""Precompute run_all() for every bundled pair so the demo never waits on LoFTR.

    python -m ops.precompute_demo_cache            # all pairs under data/pairs
    python -m ops.precompute_demo_cache pair_01    # one pair

Writes demo_cache/results/<pair>.pkl (the exact result dict `run_all` returned,
pickled) and <pair>.json (when, which commit, how long it took). The Streamlit
app loads the pickle when "Use the precomputed result" is ticked and runs the
pipeline live when it is not - the cached result is not a different code path,
it is the same output saved. demo_cache/ is gitignored; re-run this after any
change to core/ and before Gate 4.
"""
from __future__ import annotations

import json
import pathlib
import pickle
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAIRS = ROOT / "data" / "pairs"
OUT = ROOT / "demo_cache" / "results"


def _commit() -> str:
    """The commit that produced this cache - with `-dirty` when it did not.

    The Day-6 cache was stamped `fce6d05`, a commit that has no trust layer and no
    fallback: it was written from an uncommitted working tree four minutes before
    those were committed. The numbers were right, but the sidecar named code that
    could not have produced them, and the UI printed that string on the
    identification plate as provenance. A short SHA on a dirty tree is a claim
    about code that is not what ran, so say so.
    """
    from core.export import _commit as commit
    # Only the paths that can change what run_all() returns. A dirty README
    # does not make a cache stale; a dirty core/ does. The evidence logs never do.
    return commit(("core", "evaluation", "app"))


def main(argv: list[str]) -> int:
    from core.pipeline import resolve_pair, run_all
    wanted = set(argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    done = 0
    for d in sorted(PAIRS.iterdir()):
        if not d.is_dir() or (wanted and d.name not in wanted):
            continue
        try:
            src, ref = resolve_pair(d)
        except SystemExit:
            continue
        t0 = time.perf_counter()
        r = run_all(src, ref)
        dt = time.perf_counter() - t0
        with open(OUT / f"{d.name}.pkl", "wb") as f:
            pickle.dump(r, f, protocol=pickle.HIGHEST_PROTOCOL)
        (OUT / f"{d.name}.json").write_text(json.dumps({
            "pair": d.name, "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git_commit": _commit(), "seconds": dt,
            "method": (r.get("declared") or {}).get("method"),
            "n_matches": r.get("n_matches"),
        }, indent=1), encoding="utf-8")
        print(f"  {d.name:<24} {dt:6.1f} s  method {(r.get('declared') or {}).get('method')}  "
              f"-> {OUT / (d.name + '.pkl')}")
        done += 1
    print(f"{done} pair(s) cached under {OUT}")
    return 0 if done else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
