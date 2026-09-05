"""`evaluation/results_log.csv` is append-only. This is that rule, enforced.

Invariant 1 says no figure reaches a slide, demo script, Q&A answer or README
until it exists in this file. The rule that makes the file worth trusting is that
rows are only ever ADDED - including the rows that make the project look worse.
A row that can be quietly edited or removed is not evidence, it is a claim.

`CLAUDE.md` tells an auditor to verify this with:

    git log -p evaluation/results_log.csv

which is exactly what `test_the_log_has_only_ever_been_appended_to` does, so the
check runs on every `pytest` instead of only when somebody remembers. It found
one historical deletion, which is documented below rather than hidden: the point
of an append-only log is undermined more by a silent exception than by a stated
one.
"""
from __future__ import annotations

import csv
import pathlib
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "evaluation" / "results_log.csv"

# The ONE data row ever removed from this file, and the commit that removed it.
#
# Commit f788a17 (Rishabh, 3 Sep 2026, "change detection: log results and move
# Day 6 notes") was `1 insertion(+), 1 deletion(-)`: it REPLACED this row with a
# real change-detection row instead of appending. The row it removed was written
# by the pytest that exercises the `allow_failed` logging path - `pair_id` is
# `test_pair_allowed`, `method` is `test`, and its status is `too_few_matches`,
# so it carries no accuracy figure (the `0` / `0.0` it does carry are the failure
# sentinels `logger.py` writes for a run that produced nothing). A test polluted
# the real log and the next commit to touch the file cleaned it up.
#
# No MEASURED result has ever been removed from this file. That is the sentence
# to say out loud; "nothing has ever been deleted" is not, and a judge running
# the command in CLAUDE.md would find this in seconds.
#
# It is NOT re-added: re-adding it would itself be an edit, and would put a row
# that looks like a failed run back into a file people read as measurements.
KNOWN_DELETIONS = {
    "2026-09-03T04:07:42.295307+00:00,test_pair_allowed,synthetic,test,,,,0,0.0,,,,,"
    "too_few_matches,",
}


def _git(*args: str) -> str:
    try:
        out = subprocess.run(("git", *args), cwd=ROOT, capture_output=True, text=True,
                             timeout=120, check=False)
    except (OSError, subprocess.SubprocessError) as e:  # pragma: no cover
        pytest.skip(f"git unavailable: {e}")
    if out.returncode != 0:  # pragma: no cover
        pytest.skip(f"git failed: {out.stderr.strip()[:200]}")
    return out.stdout


def test_the_log_has_only_ever_been_appended_to():
    """Every removed DATA line in this file's whole history must be a known one.

    Header rewrites are allowed and ignored: the schema gained a `notes` column,
    which necessarily rewrites the header line. A header carries no measurement.
    """
    patch = _git("log", "-p", "--follow", "--", "evaluation/results_log.csv")
    removed = []
    for line in patch.splitlines():
        if not line.startswith("-") or line.startswith("---"):
            continue
        body = line[1:]
        if not body.strip() or body.startswith("timestamp,"):
            continue                       # header rewrite, not a measurement
        removed.append(body)

    unexpected = [r for r in removed if r not in KNOWN_DELETIONS]
    assert not unexpected, (
        "results_log.csv is APPEND-ONLY and these rows were removed from its "
        "history:\n  " + "\n  ".join(unexpected[:10]) + "\n\n"
        "If a row is wrong, append a corrected row and say in its notes that it "
        "supersedes the earlier one. Never edit or delete. If a removal was "
        "genuinely unavoidable, add it to KNOWN_DELETIONS with the commit and the "
        "reason, so it is stated rather than hidden."
    )


def test_no_measured_row_has_ever_been_removed():
    """The stronger claim, and the one that is actually said out loud.

    Every known deletion must be a test artifact from a run that produced no
    measurement. Note what is NOT asserted: the row does carry `inlier_count=0`
    and `inlier_ratio=0.0`. Those are what `evaluation/logger.py` writes for a run
    that FAILED - its status is `too_few_matches` - not measurements of anything.
    The figures that would make a row evidence are the accuracy columns, and those
    are empty. Being exact about this is the point: "no measured row was ever
    removed" is defensible, "the row was completely empty" would not have been.
    """
    header = LOG.read_text(encoding="utf-8-sig").splitlines()[0].split(",")
    for row_text in KNOWN_DELETIONS:
        row = dict(zip(header, next(csv.reader([row_text]))))
        assert row["pair_id"].startswith("test_"), (
            f"a deleted row names a real pair: {row['pair_id']}")
        assert row["method"] == "test", f"a deleted row names a real method: {row['method']}"
        assert row["status"] != "ok", (
            f"a deleted row was a SUCCESSFUL run: status={row['status']!r}")
        for metric in ("rmse_gt_px", "residual_px", "grid_coverage_fraction",
                       "distribution_cv"):
            assert not (row.get(metric) or "").strip(), (
                f"a deleted row carried an accuracy figure: {metric}={row[metric]!r}")


def test_the_log_still_parses_and_only_grows():
    """A file that is appended to for eleven days is one bad write from unusable."""
    rows = list(csv.DictReader(LOG.open(encoding="utf-8-sig")))
    assert len(rows) >= 274, f"the log has shrunk: {len(rows)} rows"
    assert all(r.get("pair_id") for r in rows), "a row lost its pair_id"
    assert all(r.get("timestamp") for r in rows), "a row lost its timestamp"
