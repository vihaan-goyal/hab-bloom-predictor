"""
cadence_check.py
----------------
Lock (or break) the conclusion that monitoring cadence, not a nitrogen mechanism,
is the dominant precision limiter. Three checks:

  1) genuine_low single-reading fraction across horizons (21/28/35). If it stays
     ~100%, the "model fired but chl was low" errors are unverifiable at every
     horizon, not an artifact of one window width.
  2) per-station sampling gap (days between consecutive readings), with the FP-heavy
     stations called out. ~3-week gaps = cadence-limited.
  3) systemic observability: across ALL labeled rows, what fraction of forward
     windows contain 0 / 1 / >=2 readings. If most windows have <=1 reading, the
     labeling scheme itself is cadence-limited, which is the headline finding.

Run from repo root:
    python cadence_check.py
"""

import argparse
import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--predictions", default="data/cv_pred_orig_h21.csv")
    p.add_argument("--series", default="data/hab_features_tidal.csv")
    p.add_argument("--threshold", type=float, default=0.60)
    p.add_argument("--floor", type=float, default=8.0)
    p.add_argument("--horizons", type=int, nargs="+", default=[21, 28, 35])
    return p.parse_args()


def build_smap(ser):
    smap = {}
    for st, g in ser[["station_name", "date", "Chlorophyll"]].dropna().groupby("station_name"):
        g = g.sort_values("date")
        smap[st] = (g["date"].values.astype("datetime64[ns]"),
                    g["Chlorophyll"].values.astype(float))
    return smap


def main():
    a = parse_args()
    pred = pd.read_csv(a.predictions); pred["date"] = pd.to_datetime(pred["date"])
    ser = pd.read_csv(a.series); ser["date"] = pd.to_datetime(ser["date"])
    pred["station_name"] = pred["station_name"].astype(str)
    ser["station_name"] = ser["station_name"].astype(str)
    smap = build_smap(ser)

    # ---- 1) genuine_low single-reading fraction across horizons ----
    print("=" * 64)
    print("1) genuine_low single-reading fraction by horizon")
    print("=" * 64)
    pp = pred["y_prob"].values >= a.threshold
    fp = pred[pp & (pred["y_true"].values == 0)]
    for H in a.horizons:
        Hd = np.timedelta64(H, "D")
        gl_dens = []
        for _, r in fp.iterrows():
            st, d = str(r["station_name"]), np.datetime64(r["date"])
            if st not in smap:
                continue
            dates, chl = smap[st]
            inw = (dates > d) & (dates <= d + Hd)
            k = int(inw.sum())
            if k == 0:
                continue
            if float(np.max(chl[inw])) < a.floor:  # genuine_low
                gl_dens.append(k)
        gl_dens = np.array(gl_dens)
        if len(gl_dens):
            on1 = (gl_dens == 1).mean()
            print(f"  h={H:>2}d  genuine_low={len(gl_dens):>3}  "
                  f"on 1 reading={on1:.0%}  median readings={np.median(gl_dens):.0f}")
    print()

    # ---- 2) per-station sampling gap ----
    print("=" * 64)
    print("2) per-station sampling gap (days)")
    print("=" * 64)
    gap_rows = []
    for st, (dates, _) in smap.items():
        if len(dates) < 3:
            continue
        g = np.diff(dates).astype("timedelta64[D]").astype(int)
        gap_rows.append((st, np.median(g), np.percentile(g, 25), np.percentile(g, 75), len(dates)))
    gaps = pd.DataFrame(gap_rows, columns=["station", "median", "p25", "p75", "n"])
    print(f"  network-wide median gap: {gaps['median'].median():.0f} days")
    fp_stations = fp["station_name"].value_counts().head(10).index.tolist()
    print(f"  FP-heavy stations:")
    for st in fp_stations:
        row = gaps[gaps["station"] == st]
        if len(row):
            r = row.iloc[0]
            print(f"    {st:<6} median={r['median']:>3.0f}d  "
                  f"IQR[{r['p25']:.0f},{r['p75']:.0f}]  n={int(r['n'])}")
    print()

    # ---- 3) systemic observability across all rows ----
    print("=" * 64)
    print("3) forward-window observability across ALL labeled rows")
    print("=" * 64)
    for H in a.horizons:
        Hd = np.timedelta64(H, "D")
        counts = {0: 0, 1: 0, 2: 0}
        tot = 0
        for st, (dates, _) in smap.items():
            for d in dates:
                inw = (dates > d) & (dates <= d + Hd)
                k = int(inw.sum())
                counts[min(k, 2)] += 1
                tot += 1
        print(f"  h={H:>2}d  0 readings={counts[0]/tot:.0%}  "
              f"1 reading={counts[1]/tot:.0%}  >=2 readings={counts[2]/tot:.0%}")
    print("\nIf most windows have <=1 reading, the label itself is cadence-limited:")
    print("blooms in unsampled windows are invisible, so both the labels and the")
    print("'errors' are bounded by how often the water is sampled, not by the model.")


if __name__ == "__main__":
    main()