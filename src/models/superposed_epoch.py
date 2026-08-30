"""
superposed_epoch.py
-------------------
Superposed epoch analysis: the generalization behind the per-event atlas.

A single bloom onset carries 3-4 in-situ readings across the 120 days before it,
which is far too thin to read a run-up from. Pooling every clean onset in the
record turns those sparse samples into a distribution: bin each observation by
how many days it sits before its own onset, then ask whether the pooled anomaly
in a bin differs from what that station shows at the same time of year when no
bloom follows.

Design decisions that matter for the result
-------------------------------------------
1. One value per event per bin. Each event contributes the mean of its
   observations in a bin, so a densely-sampled daily feature does not
   pseudo-replicate 15 observations against an in-situ feature's one, and every
   event carries equal weight.

2. A matched null, not a global mean. For every onset we draw up to
   `--n-null` control dates at the SAME station, within +/- 15 days of the same
   day of year, in a different year, with no exceedance in the following 21 days.
   The null composite runs through identical machinery. Without this the
   "precursor" would largely be the seasonal cycle: blooms happen in February and
   August, so anything seasonal looks like a precursor.

3. Station-year clustered bootstrap. Events at one station in one year are not
   independent, so resampling is done over (station, year) clusters, matching the
   convention already used in bootstrap_ci.py. Events and their matched nulls are
   resampled as pairs, so the reported difference is paired.

4. Benjamini-Hochberg across features within each regime and bin, because ~50
   features are tested at once and some will separate by chance.

Winter and summer are analyzed separately throughout. Pooling them lets opposite
temperature and photoperiod signals cancel into a flat composite.

The negative control, and why it is not an onset shuffle
--------------------------------------------------------
`--null-control` splits each event's matched controls into two disjoint halves
and runs half A against half B through identical machinery. Nothing distinguishes
the halves, so any feature that separates is measuring the method, not the water.

Permuting onset dates -- the obvious alternative -- is NOT a valid control here,
and quietly produces a near-full-strength false positive. A shuffled anchor is an
unconditioned date, while the matched null is conditioned on having no exceedance
in the following horizon. Winter's bloom rate is about 0.41, so roughly two in
five shuffled anchors are still genuine pre-bloom windows, and comparing those
against a set that is zero per cent pre-bloom separates strongly however the
dates are permuted. Measured directly: the onset shuffle left 107 of 416 winter
and 216 of 416 summer feature-bins "significant", against 128 and 195 for the
real analysis. The defect is in the control, not in the composite.

Run from repo root:
    python src/models/superposed_epoch.py
    python src/models/superposed_epoch.py --null-control   # verification
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bloom_precursor_events import (  # noqa: E402
    BLOOM_THRESHOLD, LOOKBACK_DAYS, add_doy_climatology_z, build_episode_index,
    load_daily_frames)
from locked_pipeline import FEATURES_ALL, load_locked_dataframe  # noqa: E402

BIN_WIDTH = 15
HORIZON_DAYS = 21
NULL_DOY_TOL = 15        # matched control must sit within this of the same day of year
N_NULL = 3               # controls averaged per event
N_BOOT = 2000            # matches bootstrap_ci.py
MIN_PAIRED = 30          # below this a bin is reported but never called significant
OUT_CSV = "data/superposed_epoch.csv"

DAILY_KEYS = [
    "max_gust_3d", "max_gust_ms", "wind_stress_mag", "wsm_roll3d", "wsm_roll7d",
    "wind_stress_curl", "wsc_roll3d", "wsc_roll7d",
    "connecticut_river_discharge_cfs", "thames_river_discharge_cfs",
    "housatonic_river_discharge_cfs",
    "photoperiod_hrs", "moon_illum_frac", "spring_neap",
]
SATELLITE_KEYS = ["kd490", "kd490_roll7", "kd490_roll14", "kd490_anom"]
CONSTANT_KEYS = ["latitude_x", "longitude_x", "month"]


def lead_bins(lookback=LOOKBACK_DAYS, width=BIN_WIDTH):
    """Bin edges in days-before-onset, e.g. (0,15], (15,30], ... (105,120]."""
    return [(lo, lo + width) for lo in range(0, lookback, width)]


def _bin_of(lead, width=BIN_WIDTH, lookback=LOOKBACK_DAYS):
    """Bin index for a lead time, or -1 outside (0, lookback]."""
    return np.where((lead > 0) & (lead <= lookback),
                    np.ceil(lead / width).astype(int) - 1, -1)


def draw_matched_nulls(episodes, obs_dates, exceed_dates, rng, n_null=N_NULL,
                       doy_tol=NULL_DOY_TOL, horizon=HORIZON_DAYS):
    """For each onset, pick control anchor dates at the same station and time of
    year but in another year, with no exceedance in the following `horizon` days.

    Returns a list (parallel to episodes) of arrays of control anchor dates.
    """
    out = []
    for _, ev in episodes.iterrows():
        station, onset = str(ev["station_name"]), ev["onset"]
        cand = obs_dates.get(station)
        if cand is None or not len(cand):
            out.append(np.array([], dtype="datetime64[D]"))
            continue
        cand = pd.DatetimeIndex(cand)
        # same time of year, different year (wrap the year boundary)
        ddoy = np.abs(cand.dayofyear.to_numpy() - onset.dayofyear)
        ddoy = np.minimum(ddoy, 366 - ddoy)
        ok = (ddoy <= doy_tol) & (cand.year.to_numpy() != onset.year)
        # and no exceedance in the horizon that follows the control anchor
        exc = exceed_dates.get(station, np.array([], dtype="datetime64[D]"))
        if len(exc) and ok.any():
            exc_d = np.asarray(exc, dtype="datetime64[D]")
            anchors = cand.to_numpy().astype("datetime64[D]")
            delta = (exc_d[None, :] - anchors[:, None]).astype(int)
            ok &= ~(((delta > 0) & (delta <= horizon)).any(axis=1))
        pool = cand[ok]
        if not len(pool):
            out.append(np.array([], dtype="datetime64[D]"))
        else:
            take = min(n_null, len(pool))
            picked = rng.choice(pool.to_numpy(), size=take, replace=False)
            out.append(picked.astype("datetime64[D]"))
    return out


def composite_matrix(anchors, station_of, frames, keys, lookback=LOOKBACK_DAYS,
                     width=BIN_WIDTH):
    """Mean anomaly per (event, bin) for every key.

    `anchors` is a list of arrays of anchor dates (one array per event; the event
    composite passes a single onset, the null composite passes its controls).
    `frames` maps a key to (dates, values, stations), with stations None for a
    regional series that has no station dimension.

    Returns {key: array of shape (n_events, n_bins)}, NaN where an event
    contributed no observation to a bin.
    """
    n_bins = lookback // width
    out = {k: np.full((len(anchors), n_bins), np.nan) for k in keys}

    for i, anc in enumerate(anchors):
        anc = np.atleast_1d(anc)
        if not len(anc):
            continue
        station = station_of[i]
        for key in keys:
            dates, values, stations = frames[key]
            if stations is not None:
                sel = stations == station
                d, v = dates[sel], values[sel]
            else:
                d, v = dates, values
            if not len(d):
                continue
            sums = np.zeros(n_bins)
            counts = np.zeros(n_bins)
            for a in anc:
                lead = (a - d).astype("timedelta64[D]").astype(float)
                b = _bin_of(lead, width, lookback)
                keep = (b >= 0) & np.isfinite(v)
                if not keep.any():
                    continue
                np.add.at(sums, b[keep], v[keep])
                np.add.at(counts, b[keep], 1)
            out[key][i] = np.where(counts > 0, sums / np.maximum(counts, 1),
                                   np.nan)
    return out


def clustered_bootstrap(event_mat, null_mat, clusters, n_boot=N_BOOT, seed=42):
    """Paired station-year clustered bootstrap of median(event) - median(null).

    Returns (diff, ci_lo, ci_hi, p_two_sided, n_paired_per_bin).
    """
    rng = np.random.default_rng(seed)
    _, cluster_idx = np.unique(clusters, return_inverse=True)
    n_clusters = cluster_idx.max() + 1 if len(cluster_idx) else 0
    members = [np.flatnonzero(cluster_idx == c) for c in range(n_clusters)]

    with np.errstate(all="ignore"):
        obs = np.nanmedian(event_mat, axis=0) - np.nanmedian(null_mat, axis=0)
    n_per_bin = np.sum(np.isfinite(event_mat) & np.isfinite(null_mat), axis=0)

    draws = np.full((n_boot, event_mat.shape[1]), np.nan)
    for b in range(n_boot):
        pick = rng.integers(0, len(members), len(members))
        rows = np.concatenate([members[p] for p in pick])
        with np.errstate(all="ignore"):
            draws[b] = (np.nanmedian(event_mat[rows], axis=0)
                        - np.nanmedian(null_mat[rows], axis=0))

    with np.errstate(all="ignore"):
        lo = np.nanpercentile(draws, 2.5, axis=0)
        hi = np.nanpercentile(draws, 97.5, axis=0)
        frac = np.nanmean(draws <= 0, axis=0)
    p = 2 * np.minimum(frac, 1 - frac)
    return obs, lo, hi, np.clip(p, 1.0 / n_boot, 1.0), n_per_bin


def benjamini_hochberg(p):
    """BH-adjusted q-values for a 1-D array of p-values (NaNs pass through)."""
    p = np.asarray(p, dtype=float)
    q = np.full_like(p, np.nan)
    ok = np.isfinite(p)
    if not ok.any():
        return q
    vals = p[ok]
    order = np.argsort(vals)
    ranked = vals[order]
    n = len(ranked)
    adj = ranked * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(adj, 0, 1)
    q[ok] = out
    return q


def run(lookback=LOOKBACK_DAYS, n_boot=N_BOOT, n_null=N_NULL, seed=42,
        null_control=False):
    rng = np.random.default_rng(seed)

    df = load_locked_dataframe()
    episodes = build_episode_index(df, lookback=lookback)
    clean = episodes[episodes["clean_onset"]
                     & episodes["regime"].isin(["winter", "summer"])].copy()
    print(f"\n{len(clean)} clean onsets in the two regimes "
          f"({clean['regime'].value_counts().to_dict()})")

    # Station latitude/longitude are constant within a station and `month` is
    # fixed by the lead bin, so their event-minus-null difference is identically
    # zero. The bootstrap then degenerates and reports them as "significant";
    # the null-vs-null control caught exactly these three and nothing else.
    insitu_keys = [k for k in FEATURES_ALL
                   if k in df.columns and k not in DAILY_KEYS
                   and k not in CONSTANT_KEYS]
    df = pd.concat([df, add_doy_climatology_z(df, insitu_keys)], axis=1)

    regional, station_daily = load_daily_frames()
    reg_keys = [k for k in DAILY_KEYS if k in regional.columns]
    sat_keys = [k for k in SATELLITE_KEYS if k in station_daily.columns]
    regional = pd.concat(
        [regional, add_doy_climatology_z(regional, reg_keys, group_col=None)],
        axis=1)
    station_daily = pd.concat(
        [station_daily, add_doy_climatology_z(station_daily, sat_keys)], axis=1)

    # frames keyed by feature: (dates, anomaly values, stations or None)
    frames = {}
    st_is = df["station_name"].astype(str).to_numpy()
    d_is = df["date"].to_numpy().astype("datetime64[D]")
    for k in insitu_keys:
        frames[k] = (d_is, df[f"{k}_z"].to_numpy(dtype=float), st_is)
    d_reg = regional["date"].to_numpy().astype("datetime64[D]")
    for k in reg_keys:
        frames[k] = (d_reg, regional[f"{k}_z"].to_numpy(dtype=float), None)
    st_sat = station_daily["station_name"].astype(str).to_numpy()
    d_sat = station_daily["date"].to_numpy().astype("datetime64[D]")
    for k in sat_keys:
        frames[k] = (d_sat, station_daily[f"{k}_z"].to_numpy(dtype=float), st_sat)

    cadence = {}
    cadence.update({k: "insitu" for k in insitu_keys})
    cadence.update({k: "daily" for k in reg_keys})
    cadence.update({k: "satellite" for k in sat_keys})
    keys = insitu_keys + reg_keys + sat_keys
    print(f"{len(keys)} features: {len(insitu_keys)} in-situ, "
          f"{len(reg_keys)} daily, {len(sat_keys)} satellite")

    # candidate control anchors and exceedance dates, per station
    obs_dates, exceed_dates = {}, {}
    for station, grp in df.dropna(subset=["Chlorophyll"]).groupby("station_name"):
        obs_dates[str(station)] = grp["date"].to_numpy()
        exceed_dates[str(station)] = (
            grp.loc[grp["Chlorophyll"] > BLOOM_THRESHOLD, "date"].to_numpy())

    rows = []
    bins = lead_bins(lookback)
    for regime in ("winter", "summer"):
        ev = clean[clean["regime"] == regime].reset_index(drop=True)
        onsets = ev["onset"].to_numpy().astype("datetime64[D]")
        station_of = ev["station_name"].astype(str).to_list()

        draw_n = 2 * n_null if null_control else n_null
        nulls = draw_matched_nulls(ev, obs_dates, exceed_dates, rng,
                                   n_null=draw_n)
        n_matched = sum(1 for a in nulls if len(a))
        print(f"\n[{regime}] {len(ev)} onsets, {n_matched} with a matched null "
              f"({100 * n_matched / max(len(ev), 1):.0f} %)")

        if null_control:
            # Half the controls stand in for the events. Both sides are
            # non-bloom windows at the same stations and times of year, so a
            # feature that separates is an artefact of the machinery.
            half_a = [a[: len(a) // 2] for a in nulls]
            half_b = [a[len(a) // 2:] for a in nulls]
            emat = composite_matrix(half_a, station_of, frames, keys, lookback)
            nmat = composite_matrix(half_b, station_of, frames, keys, lookback)
        else:
            emat = composite_matrix([np.array([o]) for o in onsets], station_of,
                                    frames, keys, lookback)
            nmat = composite_matrix(nulls, station_of, frames, keys, lookback)

        clusters = (ev["station_name"].astype(str) + "_"
                    + ev["onset"].dt.year.astype(str)).to_numpy()

        for key in keys:
            obs, lo, hi, p, n = clustered_bootstrap(
                emat[key], nmat[key], clusters, n_boot=n_boot, seed=seed)
            for bi, (b0, b1) in enumerate(bins):
                with np.errstate(all="ignore"):
                    ez = np.nanmedian(emat[key][:, bi])
                    nz = np.nanmedian(nmat[key][:, bi])
                rows.append({
                    "regime": regime, "feature": key, "cadence": cadence[key],
                    "lead_lo": b0, "lead_hi": b1,
                    "lead_label": f"{b0}-{b1} d",
                    "n_events": int(n[bi]),
                    "event_median_z": ez, "null_median_z": nz,
                    "diff": obs[bi], "ci_lo": lo[bi], "ci_hi": hi[bi],
                    "p_value": p[bi],
                })

    out = pd.DataFrame(rows)
    # BH within each regime x lead bin, across features
    out["q_value"] = np.nan
    for _, grp in out.groupby(["regime", "lead_lo"]):
        out.loc[grp.index, "q_value"] = benjamini_hochberg(
            grp["p_value"].to_numpy())
    # A bin near onset can rest on a handful of events, because only the most
    # densely-sampled stations have any reading in the last fortnight. Those bins
    # stay in the output but are never called significant -- they describe the
    # sampling, not the bloom.
    out["significant"] = ((out["q_value"] < 0.05)
                          & (np.sign(out["ci_lo"]) == np.sign(out["ci_hi"]))
                          & (out["n_events"] >= MIN_PAIRED))
    return out


def report(out, top=14):
    print("\n" + "=" * 78)
    print("FEATURES SEPARATING FROM THE MATCHED NULL (q < 0.05, CI excludes 0)")
    print("=" * 78)
    for regime in ("winter", "summer"):
        sub = out[(out["regime"] == regime) & out["significant"]].copy()
        tot = len(out[out["regime"] == regime])
        print(f"\n[{regime}] {len(sub)} significant feature-bins of {tot}")
        if sub.empty:
            print("  none")
            continue
        sub["absd"] = sub["diff"].abs()
        cols = ["feature", "cadence", "lead_label", "n_events",
                "event_median_z", "null_median_z", "diff", "ci_lo", "ci_hi",
                "q_value"]
        print(sub.sort_values("absd", ascending=False)[cols]
              .head(top).to_string(index=False,
                                   float_format=lambda v: f"{v:7.3f}"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=OUT_CSV)
    ap.add_argument("--lookback", type=int, default=LOOKBACK_DAYS)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--null-control", action="store_true",
                    help="matched-null half A vs half B; nothing should separate")
    args = ap.parse_args()

    out = run(lookback=args.lookback, n_boot=args.n_boot, n_null=args.n_null,
              seed=args.seed, null_control=args.null_control)
    path = args.out
    if args.null_control:
        path = path.replace(".csv", "_nullcontrol.csv")
    out.to_csv(path, index=False)
    report(out)
    print(f"\n-> {path}")


if __name__ == "__main__":
    main()
