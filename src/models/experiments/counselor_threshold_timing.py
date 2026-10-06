"""Counselor's question (Aug 2026): when chl-a reaches a level, how long until
the bloom (chl > 10 ug/L), and do DO / temperature at that moment change the odds?

Caveat baked into every number here: station revisit gap has median ~21 days,
so timing resolution is weeks, not days.

One-off experiment. Run from repo root with the BASE conda env:
    ~/anaconda3/python.exe src/models/experiments/counselor_threshold_timing.py
"""
import numpy as np
import pandas as pd

BLOOM = 10.0
CSV = "data/hab_features_tidal.csv"

df = pd.read_csv(CSV, dtype={"station_name": str}, parse_dates=["date"])
df = df.sort_values(["station_name", "date"]).reset_index(drop=True)
chl, do_col, temp_col = "Chlorophyll", "oxygen_concentration_in_sea_water", "sea_water_temperature"

gaps = df.groupby("station_name")["date"].diff().dt.days.dropna()
print(f"rows={len(df)}  stations={df.station_name.nunique()}")
print(f"revisit gap days: median={gaps.median():.0f}  IQR=[{gaps.quantile(.25):.0f}, {gaps.quantile(.75):.0f}]")

# ---- A. time from an upcrossing of level T to first reading > 10 ----------
print("\nA. Upcrossing of level T (prev visit <= T, this visit > T, this visit <= 10)")
print("   -> days until first subsequent visit with chl > 10 at the same station")
print(f"{'T':>4} {'n_cross':>8} {'reach10_ever90d':>16} {'median_days':>12} {'IQR':>14} {'within21d':>10} {'within42d':>10}")
for T in (2.0, 4.0, 6.0, 8.0):
    days_to = []
    n_cross = 0
    for st, g in df.groupby("station_name"):
        c = g[chl].values; d = g["date"].values
        for i in range(1, len(g)):
            if np.isnan(c[i]) or np.isnan(c[i-1]):
                continue
            if c[i-1] <= T and T < c[i] <= BLOOM:
                n_cross += 1
                fut = np.where(c[i+1:] > BLOOM)[0]
                # censor: only count if a future visit exists within 90 d
                fut_days = (d[i+1:] - d[i]) / np.timedelta64(1, "D")
                hit = None
                for j in fut:
                    if fut_days[j] <= 90:
                        hit = fut_days[j]; break
                if hit is not None:
                    days_to.append(hit)
    arr = np.array(days_to)
    if len(arr):
        w21 = (arr <= 21).mean(); w42 = (arr <= 42).mean()
        print(f"{T:>4.0f} {n_cross:>8} {len(arr)/n_cross:>16.2f} {np.median(arr):>12.0f} "
              f"[{np.percentile(arr,25):>4.0f},{np.percentile(arr,75):>4.0f}] {w21:>10.2f} {w42:>10.2f}")

# ---- B. persistence once above 10 ----------------------------------------
above = df[df[chl] > BLOOM]
nxt_above, nxt_gap = [], []
for st, g in df.groupby("station_name"):
    c = g[chl].values; d = g["date"].values
    for i in range(len(g) - 1):
        if not np.isnan(c[i]) and c[i] > BLOOM and not np.isnan(c[i+1]):
            nxt_above.append(c[i+1] > BLOOM)
            nxt_gap.append((d[i+1] - d[i]) / np.timedelta64(1, "D"))
nxt_above = np.array(nxt_above); nxt_gap = np.array(nxt_gap)
print(f"\nB. Persistence: given a visit > 10 (n={len(nxt_above)}), next visit also > 10: "
      f"{nxt_above.mean():.2f} (median gap {np.median(nxt_gap):.0f} d)")
m = nxt_gap <= 30
print(f"   restricted to next visit within 30 d (n={m.sum()}): {nxt_above[m].mean():.2f}")

# ---- C. DO / temp conditioning at elevated-but-subbloom chl ---------------
print("\nC. Among visits with chl in (5, 10] (elevated but sub-bloom):")
print("   P(any chl > 10 within 21 d, same station) by temp / DO tercile at that visit")
lab = np.full(len(df), np.nan)
for st, g in df.groupby("station_name"):
    c = g[chl].values; d = g["date"].values; idx = g.index.values
    for i in range(len(g)):
        fut_days = (d[i+1:] - d[i]) / np.timedelta64(1, "D")
        infut = fut_days <= 21
        if infut.any():
            lab[idx[i]] = float(np.nanmax(np.where(infut, c[i+1:], np.nan)) > BLOOM) \
                if not np.all(np.isnan(np.where(infut, c[i+1:], np.nan))) else np.nan
df["bloom21"] = lab
band = df[(df[chl] > 5) & (df[chl] <= 10) & df["bloom21"].notna()].copy()
print(f"   n in band with verifiable 21-d window: {len(band)}  base P = {band['bloom21'].mean():.2f}")
for col, name in ((temp_col, "temperature"), (do_col, "dissolved oxygen")):
    sub = band[band[col].notna()].copy()
    sub["terc"] = pd.qcut(sub[col], 3, labels=["low", "mid", "high"])
    tab = sub.groupby("terc", observed=True).agg(n=("bloom21", "size"), P=("bloom21", "mean"),
                                                 lo=(col, "min"), hi=(col, "max"))
    print(f"\n   {name} terciles:")
    for t, r in tab.iterrows():
        print(f"     {t:>4}  [{r.lo:6.2f}, {r.hi:6.2f}]  n={int(r.n):4d}  P(bloom within 21d)={r.P:.2f}")

# same conditioning but at already-bloom chl (>10): does DO/temp predict persistence?
print("\n   Same terciles among visits with chl > 10 (does bloom PERSIST 21 d?):")
band2 = df[(df[chl] > 10) & df["bloom21"].notna()]
for col, name in ((temp_col, "temperature"), (do_col, "dissolved oxygen")):
    sub = band2[band2[col].notna()].copy()
    sub["terc"] = pd.qcut(sub[col], 3, labels=["low", "mid", "high"])
    tab = sub.groupby("terc", observed=True).agg(n=("bloom21", "size"), P=("bloom21", "mean"),
                                                 lo=(col, "min"), hi=(col, "max"))
    print(f"   {name}:")
    for t, r in tab.iterrows():
        print(f"     {t:>4}  [{r.lo:6.2f}, {r.hi:6.2f}]  n={int(r.n):4d}  P={r.P:.2f}")
