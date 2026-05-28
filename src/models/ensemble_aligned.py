import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report

df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

# Rebuild bloom_28d to get ground truth indices
df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    idx = grp.index
    dates = grp['date'].values
    chl = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = ((dates > dates[i]) &
                (dates <= dates[i] + np.timedelta64(28, 'D')))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

SEQUENCE_LEN = 6
features_lstm = [
    'Chlorophyll', 'chl_roll3_mean', 'chl_roll6_mean', 'chl_anomaly',
    'chl_climatology', 'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'month', 'latitude_x', 'longitude_x',
]
features_lstm = [f for f in features_lstm if f in df.columns]

# Identify which rows the LSTM used for val and test
# LSTM skips first SEQUENCE_LEN-1 rows per station
val_mask  = (df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)
test_mask = df['date'].dt.year >= 2023

def get_lstm_indices(mask):
    indices = []
    sub = df[mask].copy()
    for station, grp in sub.groupby('station_name'):
        grp = grp.sort_values('date').reset_index(drop=True)
        for i in range(SEQUENCE_LEN - 1, len(grp)):
            seq = grp[features_lstm].iloc[i - SEQUENCE_LEN + 1: i + 1].values
            if not np.isnan(seq).any():
                indices.append(grp.index[i])
    return indices

print("Aligning indices...")
val_lstm_idx  = get_lstm_indices(val_mask)
test_lstm_idx = get_lstm_indices(test_mask)

# XGBoost probabilities — load and filter to matching indices
xgb_val_all  = pd.read_csv("data/xgb_val_probs.csv")['xgb_prob'].values
xgb_test_all = pd.read_csv("data/xgb_test_probs.csv")['xgb_prob'].values
y_val_all    = np.load("data/y_val.npy")
y_test_all   = np.load("data/y_test.npy")

# Map LSTM indices back to XGBoost position in val/test arrays
val_df   = df[val_mask].reset_index()
test_df  = df[test_mask].reset_index()

val_positions  = [val_df[val_df['index'] == i].index[0]
                  for i in val_lstm_idx if i in val_df['index'].values]
test_positions = [test_df[test_df['index'] == i].index[0]
                  for i in test_lstm_idx if i in test_df['index'].values]

xgb_val_aligned  = xgb_val_all[val_positions]
xgb_test_aligned = xgb_test_all[test_positions]
y_val_aligned    = y_val_all[val_positions]
y_test_aligned   = y_test_all[test_positions]

lstm_val  = np.load("data/lstm_val_probs.npy")
lstm_test = np.load("data/lstm_test_probs.npy")

# Trim to same length in case of minor mismatches
n_val  = min(len(xgb_val_aligned),  len(lstm_val))
n_test = min(len(xgb_test_aligned), len(lstm_test))

xgb_val_aligned  = xgb_val_aligned[:n_val]
lstm_val         = lstm_val[:n_val]
y_val_aligned    = y_val_aligned[:n_val]
xgb_test_aligned = xgb_test_aligned[:n_test]
lstm_test        = lstm_test[:n_test]
y_test_aligned   = y_test_aligned[:n_test]

print(f"Aligned val rows: {n_val} | test rows: {n_test}")
print(f"Val bloom rate: {y_val_aligned.mean():.1%} | Test: {y_test_aligned.mean():.1%}")

print(f"\nXGBoost (aligned) Val AUC:  {roc_auc_score(y_val_aligned, xgb_val_aligned):.3f}")
print(f"XGBoost (aligned) Test AUC: {roc_auc_score(y_test_aligned, xgb_test_aligned):.3f}")
print(f"LSTM Val AUC:               {roc_auc_score(y_val_aligned, lstm_val):.3f}")
print(f"LSTM Test AUC:              {roc_auc_score(y_test_aligned, lstm_test):.3f}")

# Try ensemble weights
print("\nEnsemble results:")
best_val, best_w = 0, 0
for w in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    ens_val  = w * xgb_val_aligned  + (1-w) * lstm_val
    ens_test = w * xgb_test_aligned + (1-w) * lstm_test
    v = roc_auc_score(y_val_aligned,  ens_val)
    t = roc_auc_score(y_test_aligned, ens_test)
    print(f"  XGB={w:.0%} LSTM={1-w:.0%}: Val={v:.3f} Test={t:.3f}")
    if v > best_val:
        best_val, best_w = v, w

print(f"\nBest val weight: XGB={best_w:.0%}, LSTM={1-best_w:.0%}")
best_ens_test = roc_auc_score(y_test_aligned,
    best_w * xgb_test_aligned + (1-best_w) * lstm_test)
print(f"Best ensemble test AUC: {best_ens_test:.3f}")