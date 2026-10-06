"""
bloom_precursor_events.py
-------------------------
Event-centered view of the record: collapse chlorophyll exceedances into bloom
EPISODES, anchor each on its onset, and expose the pre-onset window for every
feature.

Nothing else in the repo is event-centered -- every existing analysis scores
station-days independently. This module is the shared foundation for the
precursor atlas, the superposed-epoch composite, and the point-of-no-return
analysis.

Definitions
-----------
episode      : consecutive exceedances (Chlorophyll > 10 ug/L) at one station,
               collapsed whenever the gap to the next exceedance is <= 21 days.
onset        : the first exceedance date of an episode.
clean onset  : the station's previous reading was at or below threshold, so the
               onset is a genuine below->above transition rather than a
               continuation the sampling gap happened to split.
regime       : winter (onset month 1-4, the cold-water diatom mode) or
               summer (6-9, matching SUMMER_MONTHS in sampling_interval.py).
               Months 5/10/11/12 are 'other' and are never atlas candidates.

The cadence caveat that shapes everything downstream: the median gap between
station visits is 21 days, so a typical onset has ONE in-situ reading in the
month before it. Pre-onset in-situ series are genuinely sparse and must never be
drawn as connected lines. Daily forcing (gust, wind stress, discharge, astro) and
satellite kd490 are the only densely-sampled pre-onset signals.

Run from repo root:
    python src/models/bloom_precursor_events.py --list
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from locked_pipeline import (  # noqa: E402
    BLOOM_THRESHOLD, load_locked_dataframe)
from label_utils import classify_exceedances  # noqa: E402

EPISODE_GAP_DAYS = 21     # matches the locked forecast horizon
LOOKBACK_DAYS = 120       # pre-onset window shown in the atlas
KD490_START_YEAR = 2003   # first year of satellite coverage
MIN_PRIOR_OBS_120 = 4     # atlas candidates need real pre-history

WINTER_MONTHS = {1, 2, 3, 4}
SUMMER_MONTHS = {6, 7, 8, 9}

EVENTS_CSV = "data/precursor_events.csv"

# Daily forcing layers: (path, columns, per_station?)
DAILY_SOURCES = [
    ("data/gust_features_daily.csv", ["max_gust_ms", "max_gust_3d"], False),
    ("data/era5_wind_features_daily.csv",
     ["wind_stress_mag", "wsm_roll3d", "wsm_roll7d",
      "wind_stress_curl", "wsc_roll3d", "wsc_roll7d"], False),
    ("data/usgs_discharge.csv",
     ["connecticut_river_discharge_cfs", "thames_river_discharge_cfs",
      "housatonic_river_discharge_cfs"], False),
    ("data/astro_features_daily.csv",
     ["moon_illum_frac", "spring_neap", "photoperiod_hrs"], False),
    ("data/kd490_features_daily.csv",
     ["kd490", "kd490_roll7", "kd490_roll14", "kd490_anom"], True),
]


def regime_of(month):
    if month in WINTER_MONTHS:
        return "winter"
    if month in SUMMER_MONTHS:
        return "summer"
    return "other"


def build_episode_index(df, gap_days=EPISODE_GAP_DAYS,
                        threshold=BLOOM_THRESHOLD, lookback=LOOKBACK_DAYS):
    """Collapse exceedances into episodes and describe each one's pre-history.

    Returns one row per episode with onset date, peak chlorophyll, how many
    exceedances it contains, and how many in-situ readings precede the onset at
    that station in the 30/60/90/`lookback` days before it.
    """
    obs = (df.dropna(subset=["Chlorophyll"])
             .sort_values(["station_name", "date"])
             .reset_index(drop=True))
    obs = classify_exceedances(obs, threshold=threshold)

    records = []
    for station, grp in obs.groupby("station_name", sort=True):
        grp = grp.reset_index(drop=True)
        dates = grp["date"].to_numpy()
        chl = grp["Chlorophyll"].to_numpy(dtype=float)
        exc_pos = np.flatnonzero(grp["is_exceedance"].to_numpy() == 1)
        if exc_pos.size == 0:
            continue

        # split exceedance positions into episodes on gaps > gap_days
        splits = np.flatnonzero(
            (dates[exc_pos[1:]] - dates[exc_pos[:-1]])
            .astype("timedelta64[D]").astype(int) > gap_days) + 1
        for chunk in np.split(exc_pos, splits):
            first = chunk[0]
            onset = pd.Timestamp(dates[first])
            prior = dates[:first]
            n_prior = {w: int((prior >= onset - pd.Timedelta(days=w)).sum())
                       for w in (30, 60, 90, lookback)}
            records.append({
                "station_name": station,
                "onset": onset,
                "regime": regime_of(onset.month),
                "peak_chl": float(chl[chunk].max()),
                "onset_chl": float(chl[first]),
                "n_exceedances": int(chunk.size),
                "episode_end": pd.Timestamp(dates[chunk[-1]]),
                "sustained": bool(grp["is_sustained"].to_numpy()[chunk].max()),
                "has_prior_obs": first > 0,
                "prev_chl": float(chl[first - 1]) if first > 0 else np.nan,
                "gap_to_prev_days": (
                    int((onset - pd.Timestamp(dates[first - 1])).days)
                    if first > 0 else np.nan),
                "n_prior_30": n_prior[30],
                "n_prior_60": n_prior[60],
                "n_prior_90": n_prior[90],
                "n_prior_120": n_prior[lookback],
            })

    ep = pd.DataFrame.from_records(records)
    # a clean onset is a genuine below->above transition
    ep["clean_onset"] = ep["has_prior_obs"] & (ep["prev_chl"] <= threshold)
    return ep.sort_values(["onset", "station_name"]).reset_index(drop=True)


def select_atlas_events(episodes, n_per_regime=6, min_year=KD490_START_YEAR,
                        min_prior=MIN_PRIOR_OBS_120):
    """Pick the atlas events: clean onsets, satellite era, real pre-history,
    spread across as many distinct stations and years as possible.

    Diversity beats magnitude here -- twelve panels from three stations would
    show three stations' quirks, not a bloom signature. Stations and years are
    therefore exhausted before any is reused; sustained status and peak
    chlorophyll only rank candidates within that constraint.
    """
    cand = episodes[
        episodes["clean_onset"]
        & (episodes["onset"].dt.year >= min_year)
        & (episodes["n_prior_120"] >= min_prior)
        & episodes["regime"].isin(["winter", "summer"])
    ].copy()

    picked = []
    for regime in ("winter", "summer"):
        pool = cand[cand["regime"] == regime].sort_values(
            ["sustained", "peak_chl", "n_prior_120"],
            ascending=[False, False, False])
        used_st, used_yr, chosen = set(), set(), []
        # first pass refuses any repeated station or year; second pass relaxes
        # only as far as needed to fill the quota
        for strict in (True, False):
            for _, row in pool.iterrows():
                if len(chosen) >= n_per_regime:
                    break
                station, year = row["station_name"], row["onset"].year
                if strict and (station in used_st or year in used_yr):
                    continue
                if any(c["station_name"] == station and c["onset"] == row["onset"]
                       for c in chosen):
                    continue
                chosen.append(row.to_dict())
                used_st.add(station)
                used_yr.add(year)
        picked.extend(chosen[:n_per_regime])

    return (pd.DataFrame(picked)
            .sort_values(["regime", "onset"])
            .reset_index(drop=True))


DOY_BINS = 24            # ~15.2 days per bin
CLIM_MIN_N = 10          # below this, fall back to a coarser climatology


def doy_bin(dates, n_bins=DOY_BINS):
    """Map dates to a day-of-year bin index in [0, n_bins)."""
    doy = pd.DatetimeIndex(dates).dayofyear.to_numpy()
    return np.minimum((doy - 1) * n_bins // 366, n_bins - 1)


def add_doy_climatology_z(df, features, group_col="station_name",
                          n_bins=DOY_BINS, min_n=CLIM_MIN_N):
    """Standardize each feature against its own station x season climatology.

    Every feature is expressed as (value - mean) / sd of that station's history
    in the same part of the year, pooling the neighbouring bins on each side
    (an effective +/- ~23 day window, wrapped at year end). Without this a
    winter onset and a summer onset cannot be plotted on the same axis, and any
    composite would just recover the seasonal cycle instead of a precursor.

    Sparse station-seasons fall back to the network-wide climatology for that
    bin, then to the feature's global mean/sd, so a thin station degrades
    gracefully instead of producing NaN. Returns a frame of '<feature>_z'
    columns aligned to df.index.
    """
    b = doy_bin(df["date"], n_bins)
    keys = df[group_col].astype(str).to_numpy() if group_col else None
    # pooled bin membership: each bin borrows its two neighbours, wrapping
    members = {k: [(k - 1) % n_bins, k, (k + 1) % n_bins] for k in range(n_bins)}

    out = {}
    for feat in features:
        v = pd.to_numeric(df[feat], errors="coerce").to_numpy(dtype=float)
        z = np.full(len(df), np.nan)
        gmean, gsd = np.nanmean(v), np.nanstd(v)

        for k in range(n_bins):
            pool = np.isin(b, members[k])
            here = b == k
            if not here.any():
                continue
            net = v[pool & np.isfinite(v)]
            net_mean = np.nanmean(net) if net.size >= min_n else gmean
            net_sd = np.nanstd(net) if net.size >= min_n else gsd

            if keys is None:
                mu, sd = net_mean, net_sd
                sd = sd if sd and np.isfinite(sd) and sd > 0 else 1.0
                z[here] = (v[here] - mu) / sd
                continue

            for st in np.unique(keys[here]):
                sel = here & (keys == st)
                loc = v[pool & (keys == st)]
                loc = loc[np.isfinite(loc)]
                if loc.size >= min_n:
                    mu, sd = loc.mean(), loc.std()
                else:
                    mu, sd = net_mean, net_sd
                sd = sd if sd and np.isfinite(sd) and sd > 0 else 1.0
                z[sel] = (v[sel] - mu) / sd

        out[f"{feat}_z"] = z
    return pd.DataFrame(out, index=df.index)


def load_daily_frames(sources=DAILY_SOURCES):
    """Load the densely-sampled layers. Returns (regional_df, per_station_df)."""
    regional, station = [], []
    for path, cols, per_station in sources:
        if not os.path.exists(path):
            print(f"  [warn] missing daily source {path}; skipping",
                  file=sys.stderr)
            continue
        keep = ["date"] + (["station_name"] if per_station else []) + cols
        frame = pd.read_csv(path)
        frame["date"] = pd.to_datetime(frame["date"])
        frame = frame[[c for c in keep if c in frame.columns]]
        if per_station:
            frame["station_name"] = frame["station_name"].astype(str)
            station.append(frame)
        else:
            regional.append(frame)

    reg = regional[0] if regional else pd.DataFrame(columns=["date"])
    for f in regional[1:]:
        reg = reg.merge(f, on="date", how="outer")
    sta = (station[0] if station
           else pd.DataFrame(columns=["date", "station_name"]))
    for f in station[1:]:
        sta = sta.merge(f, on=["date", "station_name"], how="outer")
    return reg.sort_values("date"), sta.sort_values(["station_name", "date"])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true",
                    help="print the selected atlas events")
    ap.add_argument("--n-per-regime", type=int, default=6)
    ap.add_argument("--out", default=EVENTS_CSV)
    args = ap.parse_args()

    df = load_locked_dataframe()
    ep = build_episode_index(df)

    clean = ep[ep["clean_onset"]]
    print(f"\nEpisodes: {len(ep)} total, {len(clean)} with a clean onset")
    print("By regime (clean onsets):")
    print(clean["regime"].value_counts().to_string())
    print("\nPre-onset in-situ observation counts (clean onsets):")
    print(clean[["n_prior_30", "n_prior_60", "n_prior_90", "n_prior_120",
                 "gap_to_prev_days"]].describe().round(2).to_string())

    sel = select_atlas_events(ep, n_per_regime=args.n_per_regime)
    os.makedirs("data", exist_ok=True)
    sel.to_csv(args.out, index=False)
    print(f"\nSelected {len(sel)} atlas events -> {args.out}")
    if args.list:
        cols = ["regime", "station_name", "onset", "peak_chl", "n_exceedances",
                "sustained", "prev_chl", "gap_to_prev_days", "n_prior_120"]
        print(sel[cols].to_string(index=False))


if __name__ == "__main__":
    main()
