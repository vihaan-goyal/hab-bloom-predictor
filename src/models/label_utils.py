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


def build_forward_label(df, horizon=HORIZON, threshold=THRESHOLD,
                        sustained_only=False, sustain_window=SUSTAIN_WINDOW):
    """Positive if a qualifying exceedance occurs in (d, d+horizon].
    sustained_only=False -> any exceedance qualifies (original bloom_28d).
    sustained_only=True  -> only sustained exceedances qualify (cleaned target).
    Returns a Series aligned to df.index."""
    work = df
    if sustained_only and 'is_sustained' not in work.columns:
        work = classify_exceedances(work, threshold, sustain_window)

    out = pd.Series(0, index=work.index, dtype=int)
    for _, grp in work.groupby('station_name'):
        dates = grp['date'].values
        if sustained_only:
            qualifies = grp['is_sustained'].values == 1
        else:
            qualifies = grp['Chlorophyll'].values > threshold
        lab = np.zeros(len(grp), dtype=int)
        for i in range(len(grp)):
            mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(horizon, 'D'))
            if mask.any() and qualifies[mask].any():
                lab[i] = 1
        out.loc[grp.index] = lab

    return out.reindex(df.index)