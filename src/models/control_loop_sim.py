"""
control_loop_sim.py -- Layer 1: replay the forecast-triggered treatment loop on real history
============================================================================================
Tests the CONTROL LOGIC of notes/mitigation/00_CONTROL_LOOP.md, not the treatment itself: the
water here was never treated, so this asks when the loop would have switched on, whether that was
before a real bloom, how long it would have stayed on, and how often it would have been a false
alarm. The rules below are copied from 00_CONTROL_LOOP.md and fixed before this was run.

Loop (per station):
    MONITOR --p >= T_on--> ON for X days --> RE-MEASURE
    RE-MEASURE: OFF if  p < T_off  AND  chl < C_ok  AND  chl <= chl at the last check;
                else ON for another X, up to MAX_ON = 4X; then STOP (logged as "maxed out").
    A missing reading at a check extends ON by one day until a reading exists.
    T_off = 0.8 * T_on.  C_ok = 5 ug/L (half the 10 ug/L bloom line).

Methods (only X differs in Layer 1):
    bubbles  X = 2 days     seaweed  X = 3 days

Bays:
  Narragansett  daily out-of-fold GB probabilities (onset rows, 2015-2023, 15 stations) from
                data/decision_value_rows.csv, joined to daily sonde chlorophyll from the fork's
                data/narragansett_daily_features.csv. T_on = 0.50 (its frozen t*). Horizon 7 d.
  LIS           boat visits 2023-2025 (lab-consistent label S1). Checks can only happen at the
                next visit (~3 weeks), so X is replaced by the visit gap. T_on = 0.35 (frozen t*)
                and 0.20 (the rule's S1 re-selection; open decision). Horizon 21 d.

Definitions:
  onset       a day (visit) with chl > 10 whose previous observation at that station was <= 10.
  early catch the loop switched on 1..H days before the onset.
  on at onset the loop was ON on the onset day, however long before it switched on.
              (p only exists on days with chl <= 10, so the loop cannot trigger on a bloom day;
              an onset is either an early catch or a miss.)
  pre-onset day  a day d with an onset in (d, d+H].
  false-alarm episode  an ON episode with no onset between its start and max(end, start + H).
  Random baseline: the same number of ON days per station placed on random eligible days
  (200 seeds); compares the share of ON days that are pre-onset days.

Outputs: data/control_loop_sim.csv (summary), data/control_loop_episodes.csv (every episode).

Run from repo root:
    python src/models/control_loop_sim.py
"""
import os

import numpy as np
import pandas as pd

ROWS = "data/decision_value_rows.csv"
NAR_DAILY = os.path.join("..", "hab-bloom-predictor-narragansett", "data", "narragansett_daily_features.csv")
LIS_FEATURES = "data/hab_features_tidal_S1.csv"
OUT = "data/control_loop_sim.csv"
OUT_EP = "data/control_loop_episodes.csv"

BLOOM = 10.0
C_OK = 5.0
METHODS = {"bubbles": 2, "seaweed": 3}
N_RANDOM, SEED = 200, 42


def onsets(chl):
    """Boolean array: onset at i if chl[i] > 10 and the previous observed value was <= 10."""
    out = np.zeros(len(chl), dtype=bool)
    prev = np.nan
    for i, c in enumerate(chl):
        if np.isnan(c):
            continue
        if c > BLOOM and not np.isnan(prev) and prev <= BLOOM:
            out[i] = True
        prev = c
    return out


def run_loop(days, p, chl, t_on, x_days):
    """Simulate one station's series. `days` are sorted integer day numbers; p and chl may be NaN.
    Returns per-row ON flags and a list of episodes."""
    t_off = 0.8 * t_on
    max_on = 4 * x_days
    n = len(days)
    on = np.zeros(n, dtype=bool)
    episodes = []
    i = 0
    while i < n:
        if not (np.isfinite(p[i]) and p[i] >= t_on):
            i += 1
            continue
        start = i
        check_day = days[i] + x_days
        last_chl = chl[i]
        end_reason = "end_of_record"
        j = i
        while j < n:
            on[j] = True
            if days[j] >= check_day:
                if not np.isfinite(chl[j]):
                    check_day = days[j] + 1          # no reading: extend one day
                else:
                    stop_ok = (np.isfinite(p[j]) and p[j] < t_off and chl[j] < C_OK
                               and (not np.isfinite(last_chl) or chl[j] <= last_chl))
                    if stop_ok:
                        end_reason = "off_rule"
                        break
                    if days[j] - days[start] >= max_on:
                        end_reason = "maxed_out"
                        break
                    last_chl = chl[j]
                    check_day = days[j] + x_days
            j += 1
        end = min(j, n - 1)
        episodes.append(dict(start_day=int(days[start]), end_day=int(days[end]),
                             on_days=int(days[end] - days[start]) + 1, end_reason=end_reason))
        i = end + 1
    return on, episodes


def evaluate(df, t_on, x_days, horizon, bay, method, rng, day_weight=None):
    """df: one bay, columns station, day, p, chl. Returns a summary dict and episode rows.
    day_weight: for visit-cadence data, ON days are counted as calendar days between visits."""
    ep_rows = []
    pre_on_rows = on_rows = 0
    n_onsets = caught = on_at_onset = 0
    lead = []
    years = 0.0
    rand_num = np.zeros(N_RANDOM)
    rand_den = np.zeros(N_RANDOM)
    on_days_total = 0
    for st, g in df.groupby("station"):
        g = g.sort_values("day")
        days, p, chl = g.day.values, g.p.values, g.chl.values
        ons = onsets(chl)
        onset_days = days[ons]
        on, eps = run_loop(days, p, chl, t_on, x_days)
        pre = np.array([np.any((onset_days > d) & (onset_days <= d + horizon)) for d in days])
        on_rows += on.sum()
        pre_on_rows += (on & pre).sum()
        on_days_total += sum(e["on_days"] for e in eps)
        eligible = np.where(np.isfinite(p))[0]
        k = int(on.sum())
        if 0 < k <= len(eligible):
            for r in range(N_RANDOM):
                pick = rng.choice(eligible, k, replace=False)
                rand_num[r] += pre[pick].sum()
                rand_den[r] += k
        for od in onset_days:
            n_onsets += 1
            on_at_onset += any(e["start_day"] < od <= e["end_day"] for e in eps)
            for e in eps:
                if e["start_day"] < od and od - e["start_day"] <= horizon:
                    caught += 1
                    lead.append(od - e["start_day"])
                    break
        for e in eps:
            window_end = max(e["end_day"], e["start_day"] + horizon)
            e["false_alarm"] = not np.any((onset_days > e["start_day"]) & (onset_days <= window_end))
            e.update(bay=bay, method=method, t_on=t_on, station=st)
            ep_rows.append(e)
        years += (days.max() - days.min() + 1) / 365.25
    eps_df = pd.DataFrame(ep_rows)
    rand = rand_num / np.where(rand_den > 0, rand_den, np.nan)
    return dict(
        bay=bay, method=method, x_days=x_days, t_on=t_on, horizon_days=horizon,
        station_years=round(years, 1), onsets=n_onsets, caught_early=caught,
        share_caught=caught / n_onsets if n_onsets else np.nan,
        share_on_at_onset=on_at_onset / n_onsets if n_onsets else np.nan,
        median_lead_days=float(np.median(lead)) if lead else np.nan,
        episodes=len(eps_df),
        false_alarm_share=float(eps_df.false_alarm.mean()) if len(eps_df) else np.nan,
        on_days=int(on_days_total),
        on_days_per_station_year=on_days_total / years if years else np.nan,
        on_days_per_caught_onset=on_days_total / caught if caught else np.nan,
        pre_onset_share_of_on_rows=pre_on_rows / on_rows if on_rows else np.nan,
        random_pre_onset_share=float(np.nanmean(rand)),
        random_ci_lo=float(np.nanpercentile(rand, 2.5)),
        random_ci_hi=float(np.nanpercentile(rand, 97.5)),
        median_episode_days=float(eps_df.on_days.median()) if len(eps_df) else np.nan,
        maxed_out_share=float((eps_df.end_reason == "maxed_out").mean()) if len(eps_df) else np.nan,
        switches_per_station_year=2 * len(eps_df) / years if years else np.nan,
    ), eps_df


def load_narragansett():
    rows = pd.read_csv(ROWS, parse_dates=["date"])
    rows = rows[rows.bay == "Narragansett"][["station", "date", "prob"]]
    rows["station"] = rows.station.astype(str)
    daily = pd.read_csv(NAR_DAILY, usecols=["station", "date", "chl"], parse_dates=["date"])
    daily["station"] = daily.station.astype(str)
    daily = daily[(daily.date >= "2015-01-01") & (daily.date <= "2023-12-31")]
    daily = daily[daily.station.isin(rows.station.unique())]
    df = daily.merge(rows, on=["station", "date"], how="left").rename(columns={"prob": "p"})
    parts = []
    for st, g in df.groupby("station"):
        full = pd.DataFrame({"date": pd.date_range(g.date.min(), g.date.max(), freq="D")})
        parts.append(full.merge(g.drop(columns="station"), on="date", how="left").assign(station=st))
    df = pd.concat(parts, ignore_index=True)
    df["day"] = (df.date - pd.Timestamp("2015-01-01")).dt.days
    return df


def load_lis():
    rows = pd.read_csv(ROWS, parse_dates=["date"])
    rows = rows[rows.bay == "LIS"][["station", "date", "prob"]]
    rows["station"] = rows.station.astype(str)
    feats = pd.read_csv(LIS_FEATURES, usecols=["station_name", "date", "Chlorophyll"],
                        parse_dates=["date"], dtype={"station_name": str})
    feats = feats.rename(columns={"station_name": "station", "Chlorophyll": "chl"})
    df = rows.merge(feats, on=["station", "date"], how="left").rename(columns={"prob": "p"})
    df["day"] = (df.date - pd.Timestamp("2023-01-01")).dt.days
    return df


def main():
    rng = np.random.default_rng(SEED)
    summaries, episodes = [], []

    nar = load_narragansett()
    print(f"Narragansett: {nar.station.nunique()} stations, {len(nar):,} calendar days, "
          f"{nar.p.notna().sum():,} with a forecast, {nar.chl.notna().sum():,} with chlorophyll")
    for method, x in METHODS.items():
        s, e = evaluate(nar, 0.50, x, 7, "Narragansett", method, rng)
        summaries.append(s)
        episodes.append(e)

    lis = load_lis()
    gaps = lis.sort_values(["station", "day"]).groupby("station").day.diff().dropna()
    print(f"LIS: {lis.station.nunique()} stations, {len(lis):,} visits, chlorophyll on "
          f"{lis.chl.notna().sum():,}; median gap between visits {gaps.median():.0f} days "
          f"(the loop can only re-check at the next visit)")
    for t_on in (0.35, 0.20):
        s, e = evaluate(lis, t_on, 1, 21, "LIS", "either (visit cadence)", rng)
        summaries.append(s)
        episodes.append(e)

    res = pd.DataFrame(summaries)
    res.to_csv(OUT, index=False)
    pd.concat(episodes, ignore_index=True).to_csv(OUT_EP, index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(res.round(3).T.to_string())
    print(f"\nWrote {OUT} and {OUT_EP}")


if __name__ == "__main__":
    main()
