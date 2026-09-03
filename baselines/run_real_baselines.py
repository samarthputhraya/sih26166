"""SUPERSEDED - use `run_all_baselines.py`, which does this properly.

    python baselines/run_all_baselines.py --log

This script was a near-duplicate of the old `run_all_baselines.py` and carried
all four of the same defects:

  - it hardcoded `data/pairs/ohrc_real_source.png`, a file that has never existed
    on any machine, so it raised FileNotFoundError for everyone who ran it;
  - it read pixels with `cv2.imread`, which returns None for the Tier D GeoTIFF
    and cannot open PDS4 at all;
  - it invented its own accuracy columns (`calculate_offset`, `calculate_spread`)
    instead of using `evaluation/metrics.py`, so its numbers could not be
    compared with anything else in the project - and the offset was a plain mean
    over UNFILTERED matches, which a handful of outliers moves arbitrarily;
  - it wrote a third private CSV, so nothing it produced could ever be quoted
    under Invariant 1.

`run_all_baselines.py` now discovers every real pair under `data/pairs/`, loads
through `core.io_loader.load`, scores with `evaluation.metrics.evaluate`, and
records rows via `evaluation.logger.log_result`. There is nothing this file did
that it does not do better.

Kept as a signpost rather than deleted, because the file name is referenced in
earlier commit messages and a missing file is a worse clue than an explanation.
The original is in git history if it is ever wanted.
"""
import sys


def main() -> int:
    print(__doc__)
    print("Nothing was run. Use:  python baselines/run_all_baselines.py --log")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
