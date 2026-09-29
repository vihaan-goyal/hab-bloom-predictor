"""
label_utils.py
--------------
Shared label logic so the audit script and the CV harness agree exactly.

Definitions:
  exceedance  : an in-situ Chlorophyll reading strictly above `threshold` (10 ug/L).
  sustained   : an exceedance that has at least one OTHER exceedance within
                +/- `sustain_window` days at the same station. A real bloom
                persists; a lone reading above 10 with no nearby exceedance is a
                single-sample spike (instrument noise or a transient that never
                became a bloom).

`build_forward_label` reproduces the locked `bloom_28d` exactly when
sustained_only=False, so it is a drop-in replacement that can also produce the
cleaned target when sustained_only=True.
"""

import numpy as np
import pandas as pd

THRESHOLD = 10.0
HORIZON = 28
SUSTAIN_WINDOW = 14


def classify_exceedances(df, threshold=THRESHOLD, sustain_window=SUSTAIN_WINDOW):
    """Return df with two added columns: is_exceedance, is_sustained."""
    df = df.sort_values(['station_name', 'date']).copy()
    df['is_exceedance'] = (df['Chlorophyll'] > threshold).astype(int)
    df['is_sustained'] = 0

    for _, grp in df.groupby('station_name'):
        dates = grp['date'].values.astype('datetime64[D]')
        exc = grp['is_exceedance'].values
        exc_pos = np.where(exc == 1)[0]
        exc_dates = dates[exc_pos]
        sustained_local = np.zeros(len(grp), dtype=int)
        for pos in exc_pos:
            d = dates[pos]
            diff = np.abs((exc_dates - d).astype('timedelta64[D]').astype(int))
            # >= 2 means self plus at least one other exceedance in the window
            if int((diff <= sustain_window).sum()) >= 2:
                sustained_local[pos] = 1
        df.loc[grp.index, 'is_sustained'] = sustained_local

    return df


def forward_window_label(dates, qualifies, horizon, unresolved_as_zero=False):
    """1 if a qualifying day falls in (d, d+horizon]; 0 if the window holds at least one visit,
    none qualifies, and it closes by the station's last visit; NaN otherwise (unresolved)."""
    dates = np.asarray(dates)
    last = dates.max()
    lab = np.full(len(dates), np.nan)
    for i in range(len(dates)):
        end = dates[i] + np.timedelta64(horizon, 'D')
        mask = (dates > dates[i]) & (dates <= end)
        if mask.any() and qualifies[mask].any():
            lab[i] = 1
        elif (mask.any() and end <= last) or unresolved_as_zero:
            lab[i] = 0
    return lab


def build_forward_label(df, horizon=HORIZON, threshold=THRESHOLD,
                        sustained_only=False, sustain_window=SUSTAIN_WINDOW,
                        unresolved_as_zero=False):
    """Positive if a qualifying exceedance occurs in (d, d+horizon].
    sustained_only=False -> any exceedance qualifies (original bloom_28d).
    sustained_only=True  -> only sustained exceedances qualify (cleaned target).
    Returns a Series aligned to df.index."""
    work = df
    if sustained_only and 'is_sustained' not in work.columns:
        work = classify_exceedances(work, threshold, sustain_window)

    # Unresolved windows are NaN (fix 2026-09-28): a window with no visit inside it, or one that
    # runs past the station's last visit without a bloom, cannot be verified, so it is not scored
    # 0. Callers drop NaN labels. unresolved_as_zero=True reproduces the old label.
    out = pd.Series(np.nan, index=work.index, dtype=float)
    for _, grp in work.groupby('station_name'):
        dates = grp['date'].values
        if sustained_only:
            qualifies = grp['is_sustained'].values == 1
        else:
            qualifies = grp['Chlorophyll'].values > threshold
        out.loc[grp.index] = forward_window_label(dates, qualifies, horizon, unresolved_as_zero)

    return out.reindex(df.index)