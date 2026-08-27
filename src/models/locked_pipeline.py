"""
locked_pipeline.py
------------------
SINGLE SOURCE OF TRUTH for the locked HAB pipeline, so that evaluation,
deployment, and any future script share one implementation instead of copies.

This file used to claim it was "extracted verbatim from
final_evaluation_threshold_sweep.py". Git says otherwise: it was written fresh
in 44b72b3 (2026-08-12), which did not touch the sweep script at all. The sweep
script has used a 28-day uncensored label continuously since c71d985
(2026-06-01) and still does. The two were never the same, so do not treat that
script as this module's reference implementation -- it is the Family B label
(28-day horizon, no right-censoring) that this module exists to replace.

Locked spec:
  data    : data/hab_features_tidal.csv
            + percent_saturation merged from data/raw/deep_wq_extra/deep_wq_S_*.csv
            + max_gust_3d merged from data/gust_features_daily.csv (date-only join;
              regional wind signal, deliberately not per-station)
  features: FEATURES_ALL (35)
  label   : any Chlorophyll > 10 ug/L within `horizon` days of a station visit
            (paper standard: horizon=21)
  model   : LogisticRegression(C=0.05, class_weight='balanced',
            max_iter=1000, random_state=42), StandardScaler,
            train-median imputation

Import from repo root:
    from src.models.locked_pipeline import (
        FEATURES_ALL, load_locked_dataframe, add_forward_label,
        fit_locked_model, predict_proba)
"""

import glob

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# v2 is the leak-free build. hab_features_tidal.csv carries chl_climatology,
# chl_anomaly, tidal_gt_anom and tidal_msl_anom computed against full-record
# climatologies, which fold test-period data into training-row features. All
# four are in FEATURES_ALL. Regenerate v2 with:
#   python src/features/rebuild_climatology.py
#   python src/features/rebuild_tidal_anomalies.py
BASE_CSV = "data/hab_features_tidal_v2.csv"
PS_GLOB = "data/raw/deep_wq_extra/deep_wq_S_*.csv"
GUST_CSV = "data/gust_features_daily.csv"

BLOOM_THRESHOLD = 10.0   # ug/L, locked
HORIZON_DAYS = 21        # paper standard (h21)

FEATURES_ALL = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation',
    'max_gust_3d',
]


def _load_percent_saturation(ps_glob=PS_GLOB):
    """percent_saturation lives only in the raw ERDDAP surface (depth_code='S')
    extracts. Concatenate every deep_wq_S_*.csv, drop the units row, reduce to
    one value per (date, station_name). ERDDAP timestamps store local midnight
    encoded as UTC, so the UTC calendar date equals the local sample date."""
    frames = []
    for f in sorted(glob.glob(ps_glob)):
        frames.append(pd.read_csv(
            f, skiprows=[1],
            usecols=['station_name', 'time', 'percent_saturation']))
    if not frames:
        raise FileNotFoundError(
            f"No files matched {ps_glob}; percent_saturation source missing.")
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = (pd.to_datetime(ps['time'], utc=True)
                    .dt.tz_localize(None).dt.normalize())
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'],
                                             errors='coerce')
    return (ps.dropna(subset=['percent_saturation'])
              .groupby(['date', 'station_name'], as_index=False)
              ['percent_saturation'].mean())


def load_locked_dataframe(base_csv=BASE_CSV, ps_glob=PS_GLOB,
                          gust_csv=GUST_CSV, verbose=True):
    """Load the canonical feature dataframe: base CSV + the two merges + the
    in-script derived features (rolling means, chl_trend). No label."""
    if verbose:
        print(f"Loading {base_csv}...")
    df = pd.read_csv(base_csv)
    df['date'] = pd.to_datetime(df['date'])

    if 'percent_saturation' not in df.columns:
        if verbose:
            print(f"Merging percent_saturation from {ps_glob}...")
        ps = _load_percent_saturation(ps_glob)
        df['station_name'] = df['station_name'].astype(str)
        df = df.merge(ps, on=['date', 'station_name'], how='left')
        if verbose:
            print(f"  percent_saturation coverage: "
                  f"{df['percent_saturation'].notna().mean() * 100:.1f}%")

    if verbose:
        print(f"Merging max_gust_3d from {gust_csv}...")
    gust = pd.read_csv(gust_csv, usecols=['date', 'max_gust_3d'])
    gust['date'] = pd.to_datetime(gust['date'])
    df = df.merge(gust, on='date', how='left')   # date-only join, by design
    if verbose:
        print(f"  max_gust_3d coverage: "
              f"{df['max_gust_3d'].notna().mean() * 100:.1f}%")

    for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
        df[f'chl_roll{n}_mean'] = (
            df.groupby('station_name')['Chlorophyll']
              .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
        )

    df['chl_trend'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(4, min_periods=3)
                     .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
    )
    return df


def add_forward_label(df, horizon=HORIZON_DAYS, threshold=BLOOM_THRESHOLD,
                      col='bloom_fwd'):
    """Window label: 1 if any Chlorophyll > threshold within `horizon` days
    strictly after the row's date, at the same station. NaN where the window
    extends beyond the last observation at that station (right-censored),
    so unfinished windows are excluded from training rather than counted 0.

    CAVEAT -- right-censoring is not the whole story. At h=21 it excludes only
    87 rows (0.8%). A further 5,458 rows (47.7%) have a window that closed with
    NO station visit inside it, and those are scored 0 here: the survey cadence
    is ~21 days, so most windows contain no observation at all. Such a row means
    "no exceedance was observed", not "no exceedance occurred". Keeping them
    holds the positive rate at 0.146 instead of 0.280 and inflates the negative
    class, which depresses precision and FAR rather than flattering them.

    This is the locked spec and is left unchanged. To compute verification-style
    metrics over resolvable windows only, use
    label_utils.build_forward_label(..., unverifiable='exclude'), which is
    identical to this function apart from that policy
    (tests/test_label_equivalence.py pins the equivalence)."""
    df = df.copy()
    df[col] = np.nan
    for station, grp in df.groupby('station_name'):
        idx = grp.index
        dates = grp['date'].values
        chl = grp['Chlorophyll'].values
        last = dates.max()
        labels = np.full(len(grp), np.nan)
        for i in range(len(grp)):
            end = dates[i] + np.timedelta64(horizon, 'D')
            mask = (dates > dates[i]) & (dates <= end)
            if mask.any() and (chl[mask] > threshold).any():
                labels[i] = 1
            elif end <= last:
                labels[i] = 0
        df.loc[idx, col] = labels
    return df


def make_model():
    return LogisticRegression(class_weight='balanced', C=0.05,
                              max_iter=1000, random_state=42)


def fit_locked_model(df, label_col, train_end=None, features=None):
    """Fit the locked spec. train_end (Timestamp) limits training rows to
    date <= train_end; None uses all labeled rows. Returns a dict bundle."""
    features = features or [f for f in FEATURES_ALL if f in df.columns]
    rows = df.dropna(subset=[label_col])
    if train_end is not None:
        rows = rows[rows['date'] <= pd.Timestamp(train_end)]
    X = rows[features].copy()
    y = rows[label_col].astype(int)
    med = X.median()
    scaler = StandardScaler().fit(X.fillna(med))
    model = make_model().fit(scaler.transform(X.fillna(med)), y)
    return {'model': model, 'scaler': scaler, 'medians': med,
            'features': features, 'n_train': len(rows),
            'train_bloom_rate': float(y.mean())}


def predict_proba(bundle, df_rows):
    X = df_rows[bundle['features']].copy().fillna(bundle['medians'])
    return bundle['model'].predict_proba(bundle['scaler'].transform(X))[:, 1]