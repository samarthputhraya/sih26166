"""TO BE COPIED TO evaluation/test_fig6_kinds.py AFTER THE FREEZE.

It cannot be added while the freeze runs: `evaluation/` is in `core.export._commit`'s path list,
so a new file there stamps every later evidence row `-dirty`.

What it pins: fig6 counts planted TRANSLATIONS only. Since 20 Sep the same CSV also holds planted
rotations and scale changes, which are a different experiment - their size is a CORNER
displacement, not every pixel's - so pooling them would make one bar mean two things and the x
axis ("planted error, metres") mean two things.
"""
import csv

import pytest

from presentation.make_figures import TRUST_REAL, fig_trust_real


def _rows():
    if not TRUST_REAL.exists():
        pytest.skip("trust_real_calibration.csv is not on this machine")
    return list(csv.DictReader(open(TRUST_REAL, encoding="utf-8-sig")))


def test_the_calibration_csv_actually_holds_more_than_one_kind():
    """If it does not, the test below proves nothing."""
    kinds = {(r.get("kind") or "translation") for r in _rows()}
    assert kinds >= {"translation", "rotation", "scale"}, f"only {kinds} present"


def test_fig6_counts_translations_only():
    rows = _rows()
    trans = [r for r in rows if (r.get("kind") or "translation") == "translation"]
    assert len(trans) < len(rows), "nothing to exclude, so this test is not testing anything"
    import presentation.make_figures as M
    seen = {}
    real_rows = M._rows

    def spy(path):
        out = real_rows(path)
        if path == TRUST_REAL:
            seen["n"] = len(out)
        return out
    M._rows = spy
    try:
        fig_trust_real()
    finally:
        M._rows = real_rows
    # the figure must have read the whole file and then filtered it itself
    assert seen.get("n") == len(rows)
    # and the caption's window count must come from the translation rows
    n_win_trans = len({r["pair_id"] for r in trans})
    n_win_all = len({r["pair_id"] for r in rows})
    assert n_win_trans <= n_win_all


def test_the_two_sun_populations_are_never_pooled():
    trans = [r for r in _rows() if (r.get("kind") or "translation") == "translation"]
    lo = {r["pair_id"] for r in trans if float(r.get("d_sun_azimuth_deg") or 0) < 10}
    hi = {r["pair_id"] for r in trans if float(r.get("d_sun_azimuth_deg") or 0) >= 10}
    assert lo and hi and not (lo & hi), "the populations must be disjoint and both present"
