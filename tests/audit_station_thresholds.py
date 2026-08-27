"""
audit_station_thresholds.py
---------------------------
Checks data/station_thresholds.csv against the evidence available to support it.

A per-station threshold is only meaningful if that station's validation slice
contains enough positive windows to estimate one. station_specific_models.py
now enforces MIN_VAL_POS before tuning, but the CSV is written incrementally --
only the western rows are refreshed on each run -- so older rows can survive
from a run that predated the guard, the label fix and the leakage fix.

A stale high threshold is an operational failure, not a cosmetic one: a station
pinned at 0.80 issues almost no alerts.

Run:  python tests/audit_station_thresholds.py
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))
from src.models.locked_pipeline import (                       # noqa: E402
    HORIZON_DAYS, add_forward_label, load_locked_dataframe)

MIN_VAL_POS = 5
GLOBAL_T = 0.30
THRESH_CSV = "data/station_thresholds.csv"
VAL_YEARS = (2020, 2022)


def main():
    df = load_locked_dataframe(verbose=False)
    df = add_forward_label(df, horizon=HORIZON_DAYS)
    lab = df.dropna(subset=["bloom_fwd"]).copy()
    lab["station_name"] = lab["station_name"].astype(str)
    yr = lab["date"].dt.year
    val = lab[yr.between(*VAL_YEARS)]

    ev = (val.groupby("station_name")["bloom_fwd"]
             .agg(val_pos="sum", val_n="count").reset_index())
    ev["val_pos"] = ev["val_pos"].astype(int)

    qualified = ev[ev["val_pos"] >= MIN_VAL_POS]
    print(f"Stations with >= {MIN_VAL_POS} validation positives "
          f"(enough to tune a threshold): {len(qualified)} of {len(ev)}")
    if len(qualified):
        print(qualified.to_string(index=False))

    if not os.path.exists(THRESH_CSV):
        print(f"\n{THRESH_CSV} not present; nothing to audit.")
        return 0

    t = pd.read_csv(THRESH_CSV, dtype={"station": str})
    m = t.merge(ev.rename(columns={"station_name": "station"}),
                on="station", how="left")
    m["val_pos"] = m["val_pos"].fillna(0).astype(int)

    unsupported = m[(m["val_pos"] < MIN_VAL_POS)
                    & (m["threshold"].round(4) != GLOBAL_T)]
    print(f"\nRows with a non-global threshold but < {MIN_VAL_POS} val "
          f"positives: {len(unsupported)} of {len(m)}")
    if len(unsupported):
        print(unsupported.sort_values("threshold", ascending=False)
              .to_string(index=False))
        print("\nThese are not supported by the data. Rewrite them to the "
              f"global operating point ({GLOBAL_T}) with --fix.")
    return 1 if len(unsupported) else 0


if __name__ == "__main__":
    if "--fix" in sys.argv:
        df = load_locked_dataframe(verbose=False)
        df = add_forward_label(df, horizon=HORIZON_DAYS)
        lab = df.dropna(subset=["bloom_fwd"]).copy()
        lab["station_name"] = lab["station_name"].astype(str)
        yr = lab["date"].dt.year
        ev = (lab[yr.between(*VAL_YEARS)].groupby("station_name")["bloom_fwd"]
              .sum().astype(int))
        t = pd.read_csv(THRESH_CSV, dtype={"station": str})
        before = t["threshold"].copy()
        keep = t["station"].map(ev).fillna(0) >= MIN_VAL_POS
        t.loc[~keep, "threshold"] = GLOBAL_T
        t.to_csv(THRESH_CSV, index=False)
        n = int((before.round(4) != t["threshold"].round(4)).sum())
        print(f"Reset {n} unsupported threshold(s) to {GLOBAL_T}; "
              f"kept {int(keep.sum())} tuned.")
    raise SystemExit(main())
