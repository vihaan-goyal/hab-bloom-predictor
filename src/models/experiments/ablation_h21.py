"""Feature ablation rerun on the CURRENT locked pipeline (h21, 35 features).

Supersedes the numbers in data/ablation_results.csv, which were computed on the
28-day label with 34 features. Convention: train <= 2022, test 2023-2025,
threshold t* = 0.35 (the frozen operating point).

Run from repo root with the BASE conda env:
    ~/anaconda3/python.exe src/models/experiments/ablation_h21.py
"""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import sys, os
sys.path.insert(0, os.getcwd())
from src.models.locked_pipeline import (FEATURES_ALL, load_locked_dataframe,
                                        add_forward_label, fit_locked_model,
                                        predict_proba)

TSTAR = 0.35
TRAIN_END = "2022-12-31"

df = load_locked_dataframe()
df = add_forward_label(df)          # adds bloom_fwd
LABEL = "bloom_fwd"

test = df[(df["date"].dt.year >= 2023) & df[LABEL].notna()]

GROUPS = {
    "all CHL history":   ['chl_lag1','chl_lag2','chl_lag3','chl_lag4','chl_roll3_mean',
                          'chl_roll6_mean','chl_roll9_mean','chl_roll14_mean',
                          'chl_roll21_mean','chl_trend','chl_anomaly'],
    "chl_climatology":   ['chl_climatology'],
    "all DO features":   ['do_lag1','oxygen_concentration_in_sea_water','percent_saturation'],
    "all sal features":  ['sal_lag1','sal_lag2','sal_lag3','sal_lag4','sea_water_salinity'],
    "temp features":     ['sea_water_temperature','temp_lag1'],
    "month":             ['month'],
    "all nutrients":     ['nox_lag2','dip_lag2','dip_change','dip_x_month'],
    "all neighbor":      ['neighbor_chl3_mean','neighbor_chl3_lag1'],
    "all tidal":         ['tidal_gt_anom','tidal_msl_anom'],
    "location":          ['latitude_x','longitude_x'],
    "wind gust":         ['max_gust_3d'],
    "current Chlorophyll": ['Chlorophyll'],
}

def run(features):
    bundle = fit_locked_model(df, LABEL, train_end=TRAIN_END, features=features)
    p = predict_proba(bundle, test)
    y = test[LABEL].astype(int).values
    yhat = (p >= TSTAR).astype(int)
    tp = int(((yhat == 1) & (y == 1)).sum()); fp = int(((yhat == 1) & (y == 0)).sum())
    fn = int(((yhat == 0) & (y == 1)).sum())
    prec = tp / (tp + fp) if tp + fp else np.nan
    rec = tp / (tp + fn) if tp + fn else np.nan
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else np.nan
    return dict(auc=roc_auc_score(y, p), precision=prec, recall=rec, f1=f1,
                tp=tp, fp=fp, fn=fn, n_feat=len(features))

base = run(FEATURES_ALL)
print(f"BASELINE h21 t={TSTAR}: AUC={base['auc']:.3f} P={base['precision']:.3f} "
      f"R={base['recall']:.3f} F1={base['f1']:.3f} (tp={base['tp']} fp={base['fp']} fn={base['fn']})")

rows = [dict(type="baseline", removed="none", **base, delta_f1=0.0, delta_precision=0.0)]
for name, feats in GROUPS.items():
    reduced = [f for f in FEATURES_ALL if f not in feats]
    r = run(reduced)
    rows.append(dict(type="group", removed=name, **r,
                     delta_f1=r["f1"] - base["f1"],
                     delta_precision=r["precision"] - base["precision"]))
for f in FEATURES_ALL:
    r = run([x for x in FEATURES_ALL if x != f])
    rows.append(dict(type="single", removed=f, **r,
                     delta_f1=r["f1"] - base["f1"],
                     delta_precision=r["precision"] - base["precision"]))

out = pd.DataFrame(rows)
out.to_csv("data/ablation_h21.csv", index=False)

print("\nGROUP removals sorted by F1 damage (negative = feature group was helping):")
g = out[out.type == "group"].sort_values("delta_f1")
for _, r in g.iterrows():
    print(f"  {r.removed:22s} dF1={r.delta_f1:+.3f} dPrec={r.delta_precision:+.3f} "
          f"AUC={r.auc:.3f} P={r.precision:.3f} R={r.recall:.3f}")
print("\nTop 10 SINGLE removals by F1 damage:")
s = out[out.type == "single"].sort_values("delta_f1").head(10)
for _, r in s.iterrows():
    print(f"  {r.removed:34s} dF1={r.delta_f1:+.3f} dPrec={r.delta_precision:+.3f}")
print("\nSaved data/ablation_h21.csv")
