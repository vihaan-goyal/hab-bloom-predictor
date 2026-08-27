"""
test_label_equivalence.py
-------------------------
Pins the label semantics that four separate implementations drifted apart on.

1. label_utils.build_forward_label(unverifiable='zero') must equal
   locked_pipeline.add_forward_label row for row, NaNs in the same places.
   These were independent implementations; the shared builder scored censored
   windows as 0 while the locked one excluded them.

2. Right-censoring must actually produce NaN. The original builder initialized
   every row to 0 and only ever wrote 1s, so this never held.

3. unverifiable='exclude' must be strictly stronger than 'zero': same
   positives, strictly fewer labeled negatives.

Run:  python -m pytest tests/test_label_equivalence.py -q
      python tests/test_label_equivalence.py       (no pytest needed)
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.label_utils import build_forward_label          # noqa: E402
from src.models.locked_pipeline import add_forward_label        # noqa: E402

HORIZON = 21


def _toy():
    """Two stations on a ~21-day cadence, including an exceedance, a clean
    window, an empty window, and a right-censored tail."""
    rows = []
    for stn, chl in [("A", [2.0, 30.0, 3.0, 4.0, 1.0, 12.0, 5.0]),
                     ("B", [8.0, 1.0, 20.0, 2.0, 2.0, 2.0, 9.0])]:
        for i, c in enumerate(chl):
            rows.append({"station_name": stn,
                         "date": pd.Timestamp("2020-05-01") + pd.Timedelta(days=18 * i),
                         "Chlorophyll": c})
    return pd.DataFrame(rows)


def _check(df, tag):
    locked = add_forward_label(df, horizon=HORIZON)["bloom_fwd"]
    shared = build_forward_label(df, horizon=HORIZON, unverifiable="zero")

    both_nan = locked.isna() & shared.isna()
    same_val = (locked == shared) | both_nan
    assert same_val.all(), (
        f"[{tag}] builders disagree on {int((~same_val).sum())} rows")
    assert locked.isna().equals(shared.isna()), f"[{tag}] NaN masks differ"
    print(f"  [{tag}] equivalence OK on {len(df):,} rows "
          f"({int(locked.isna().sum()):,} NaN, {int(locked.sum()):,} positive)")

    excl = build_forward_label(df, horizon=HORIZON, unverifiable="exclude")
    assert ((excl == 1) == (shared == 1)).all(), \
        f"[{tag}] 'exclude' changed the positive set"
    assert int(excl.notna().sum()) <= int(shared.notna().sum()), \
        f"[{tag}] 'exclude' must not label more rows than 'zero'"
    print(f"  [{tag}] exclude policy OK: labeled "
          f"{int(shared.notna().sum()):,} -> {int(excl.notna().sum()):,}, "
          f"positive rate {shared.mean():.3f} -> {excl.mean():.3f}")
    return locked


def test_toy_equivalence():
    df = _toy()
    locked = _check(df, "toy")
    assert locked.isna().any(), "toy fixture must exercise right-censoring"


def test_real_data_equivalence():
    """Runs only when the canonical file is present (data/ is gitignored)."""
    for path in ("data/hab_features_tidal_v2.csv", "data/hab_features_tidal.csv"):
        if os.path.exists(path):
            break
    else:
        print("  [real] skipped: no canonical feature file on disk")
        return
    df = pd.read_csv(path, low_memory=False,
                     usecols=["date", "station_name", "Chlorophyll"])
    df["date"] = pd.to_datetime(df["date"])
    _check(df, f"real:{os.path.basename(path)}")


def test_censoring_produces_nan():
    df = _toy()
    lab = build_forward_label(df, horizon=HORIZON)
    assert lab.isna().any(), "right-censored windows must be NaN, never 0"
    assert lab.dtype.kind == "f", "label must be float to carry NaN"


if __name__ == "__main__":
    print("label equivalence:")
    test_toy_equivalence()
    test_censoring_produces_nan()
    test_real_data_equivalence()
    print("all label equivalence checks passed")
