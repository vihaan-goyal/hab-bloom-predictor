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
                        sustained_only=False, sustain_window=SUSTAIN_WINDOW,
                        unverifiable='zero'):
    """Positive if a qualifying exceedance occurs in (d, d+horizon].

    sustained_only=False -> any exceedance qualifies (original bloom_28d).
    sustained_only=True  -> only sustained exceedances qualify (cleaned target).

    Returns a FLOAT Series aligned to df.index, because unlabelable rows are
    NaN rather than 0.

    RIGHT-CENSORING (always applied)
    A window that extends past the station's last observation cannot be
    resolved, so it is NaN and drops out of training and scoring. This function
    previously initialized every row to 0 and only ever wrote 1s, so censored
    windows were silently scored as negatives. Every number produced by a
    caller of this builder before this fix inherited that defect -- including
    the rolling-origin CV predictions that the t* operating point was selected
    against.

    EMPTY WINDOWS (`unverifiable`)
    Separately, a window can close with NO station visit inside it at all. At
    h=21 that is 47.7% of rows -- the survey cadence is ~21 days, so most
    windows contain no observation. Such a row records "no exceedance was
    observed", which is not the same claim as "no exceedance occurred".
      'zero'    -- score 0. Matches locked_pipeline.add_forward_label, so this
                   is the default and the locked spec is unchanged.
      'exclude' -- NaN, giving verification-style metrics computed only over
                   windows that could actually be verified. Positive rate rises
                   from 0.146 to 0.280 at h=21, so precision and FAR are
                   materially different under this policy.

    With unverifiable='zero' this reproduces locked_pipeline.add_forward_label
    exactly; tests/test_label_equivalence.py asserts it row for row.
    """
    if unverifiable not in ('zero', 'exclude'):
        raise ValueError("unverifiable must be 'zero' or 'exclude'")

    work = df
    if sustained_only and 'is_sustained' not in work.columns:
        work = classify_exceedances(work, threshold, sustain_window)

    out = pd.Series(np.nan, index=work.index, dtype=float)
    for _, grp in work.groupby('station_name'):
        dates = grp['date'].values
        if sustained_only:
            qualifies = grp['is_sustained'].values == 1
        else:
            qualifies = grp['Chlorophyll'].values > threshold
        last = dates.max()
        lab = np.full(len(grp), np.nan)
        for i in range(len(grp)):
            end = dates[i] + np.timedelta64(horizon, 'D')
            mask = (dates > dates[i]) & (dates <= end)
            has_obs = bool(mask.any())
            if has_obs and qualifies[mask].any():
                lab[i] = 1.0
            elif end <= last:
                # Window is closed. Observed-and-clean is a true negative;
                # an empty window is only a negative under the 'zero' policy.
                if has_obs or unverifiable == 'zero':
                    lab[i] = 0.0
            # else: right-censored, stays NaN
        out.loc[grp.index] = lab

    return out.reindex(df.index)