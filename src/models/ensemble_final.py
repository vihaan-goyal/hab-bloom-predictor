import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
import xgboost as xgb

# ── Shared setup ──────────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv("data/hab_features_daily.csv")
df['date'] = pd.to_datetime(df['date'])

for n, min_p in [(3,2),(6,3),(9,5)]:
    df[f'chl_roll{n}_mean'] = (df.groupby('station_name')['Chlorophyll']
                                 .transform(lambda x: x.rolling(n, min_periods=min_p).mean()))
df['chl_trend'] = (df.groupby('station_name')['Chlorophyll']
                     .transform(lambda x: x.rolling(4, min_periods=3)
                     .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0])))

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

df = df.sort_values(['station_name', 'date']).reset_index(drop=True)

# ── Feature sets ──────────────────────────────────────────────────────────────
xgb_features = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
]
xgb_features = [f for f in xgb_features if f in df.columns]

lstm_features = [
    'Chlorophyll', 'chl_roll3_mean', 'chl_roll6_mean', 'chl_anomaly',
    'chl_climatology', 'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'month', 'latitude_x', 'longitude_x',
]
lstm_features = [f for f in lstm_features if f in df.columns]

# ── Splits ────────────────────────────────────────────────────────────────────
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test  = df[df['date'].dt.year >= 2023]

def get_xy(split, features):
    clean = split[features + ['bloom_28d']].dropna(subset=['bloom_28d'])
    return clean[features], clean['bloom_28d']

X_tr_xgb, y_tr = get_xy(train, xgb_features)
X_v_xgb,  y_v  = get_xy(val,   xgb_features)
X_te_xgb, y_te = get_xy(test,  xgb_features)

print(f"Train: {len(X_tr_xgb):,} | Val: {len(X_v_xgb):,} | Test: {len(X_te_xgb):,}")
print(f"Bloom: train={y_tr.mean():.1%} val={y_v.mean():.1%} test={y_te.mean():.1%}")

# ── XGBoost ───────────────────────────────────────────────────────────────────
print("\nTraining XGBoost...")
pos_weight = (y_tr == 0).sum() / (y_tr == 1).sum()
xgb_model = xgb.XGBClassifier(
    colsample_bytree=0.7, learning_rate=0.03, max_depth=3,
    min_child_weight=10, n_estimators=200, subsample=0.7,
    scale_pos_weight=pos_weight, eval_metric='auc',
    random_state=42, verbosity=0
)
xgb_model.fit(X_tr_xgb, y_tr, eval_set=[(X_v_xgb, y_v)], verbose=False)
xgb_val_p  = xgb_model.predict_proba(X_v_xgb)[:,1]
xgb_test_p = xgb_model.predict_proba(X_te_xgb)[:,1]
print(f"XGBoost Val AUC:  {roc_auc_score(y_v,  xgb_val_p):.3f}")
print(f"XGBoost Test AUC: {roc_auc_score(y_te, xgb_test_p):.3f}")

# ── Logistic Regression ───────────────────────────────────────────────────────
print("\nTraining Logistic Regression...")
med = X_tr_xgb.median()
scaler = StandardScaler()
X_tr_s = pd.DataFrame(scaler.fit_transform(X_tr_xgb.fillna(med)), columns=xgb_features)
X_v_s  = pd.DataFrame(scaler.transform(X_v_xgb.fillna(med)),      columns=xgb_features)
X_te_s = pd.DataFrame(scaler.transform(X_te_xgb.fillna(med)),     columns=xgb_features)

lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr.fit(X_tr_s, y_tr)
lr_val_p  = lr.predict_proba(X_v_s)[:,1]
lr_test_p = lr.predict_proba(X_te_s)[:,1]
print(f"LR Val AUC:  {roc_auc_score(y_v,  lr_val_p):.3f}")
print(f"LR Test AUC: {roc_auc_score(y_te, lr_test_p):.3f}")

# ── LSTM ──────────────────────────────────────────────────────────────────────
print("\nLoading LSTM...")
SEQUENCE_LEN = 6

df_lstm = df.copy()
for col in lstm_features:
    df_lstm[col] = df_lstm.groupby('station_name')[col].transform(
        lambda x: x.fillna(x.median()))
df_lstm[lstm_features] = df_lstm[lstm_features].fillna(df_lstm[lstm_features].median())

scaler_lstm = StandardScaler()
train_mask = df_lstm['date'].dt.year <= 2019
df_lstm.loc[:, lstm_features] = scaler_lstm.fit_transform(df_lstm[lstm_features])

def build_seqs_with_dates(mask):
    X, y, dates_out, stations_out = [], [], [], []
    for station, grp in df_lstm[mask].groupby('station_name'):
        grp = grp.sort_values('date').reset_index(drop=True)
        for i in range(SEQUENCE_LEN-1, len(grp)):
            seq = grp[lstm_features].iloc[i-SEQUENCE_LEN+1:i+1].values
            if not np.isnan(seq).any():
                X.append(seq)
                y.append(grp['bloom_28d'].iloc[i])
                dates_out.append(grp['date'].iloc[i])
                stations_out.append(station)
    return (np.array(X, dtype=np.float32), np.array(y, dtype=np.float32),
            dates_out, stations_out)

val_mask  = (df_lstm['date'].dt.year >= 2020) & (df_lstm['date'].dt.year <= 2022)
test_mask = df_lstm['date'].dt.year >= 2023

X_v_lstm,  y_v_lstm,  val_dates,  val_stations  = build_seqs_with_dates(val_mask)
X_te_lstm, y_te_lstm, test_dates, test_stations = build_seqs_with_dates(test_mask)

class HABLstm(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.lstm = nn.LSTM(n, 64, 2, batch_first=True, dropout=0.4)
        self.drop = nn.Dropout(0.4)
        self.fc   = nn.Linear(64, 1)
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(self.drop(out[:,-1,:])).squeeze(1)

device = torch.device('cpu')
lstm_model = HABLstm(len(lstm_features))
lstm_model.load_state_dict(torch.load("data/lstm_best.pt", map_location=device))
lstm_model.eval()

with torch.no_grad():
    lstm_val_p  = torch.sigmoid(lstm_model(torch.tensor(X_v_lstm))).numpy()
    lstm_test_p = torch.sigmoid(lstm_model(torch.tensor(X_te_lstm))).numpy()

print(f"LSTM Val AUC:  {roc_auc_score(y_v_lstm,  lstm_val_p):.3f}")
print(f"LSTM Test AUC: {roc_auc_score(y_te_lstm, lstm_test_p):.3f}")

# ── Align all three on LSTM rows (fewest rows, most restrictive) ──────────────
print("\nAligning models on LSTM rows...")

# Build lookup from (station, date) -> position in XGB/LR val/test arrays
val_df  = val[xgb_features + ['bloom_28d']].copy()
test_df = test[xgb_features + ['bloom_28d']].copy()
val_df['station']  = val['station_name'].values
val_df['date']     = val['date'].values
test_df['station'] = test['station_name'].values
test_df['date']    = test['date'].values

val_df  = val_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)

def align_probs(df_split, xgb_p, lr_p, lstm_p, lstm_dates, lstm_stations):
    df_split = df_split.reset_index(drop=True)
    lookup = {(str(row['station']), str(row['date'])[:10]): i
              for i, row in df_split.iterrows()}
    xgb_aligned, lr_aligned, lstm_aligned, y_aligned = [], [], [], []
    for j, (d, s) in enumerate(zip(lstm_dates, lstm_stations)):
        key = (str(s), str(d)[:10])
        if key in lookup:
            i = lookup[key]
            xgb_aligned.append(xgb_p[i])
            lr_aligned.append(lr_p[i])
            lstm_aligned.append(lstm_p[j])
            y_aligned.append(df_split['bloom_28d'].iloc[i])
    return (np.array(xgb_aligned), np.array(lr_aligned),
            np.array(lstm_aligned), np.array(y_aligned))

xgb_v, lr_v, lstm_v, y_v_a = align_probs(
    val_df, xgb_val_p, lr_val_p, lstm_val_p, val_dates, val_stations)
xgb_t, lr_t, lstm_t, y_t_a = align_probs(
    test_df, xgb_test_p, lr_test_p, lstm_test_p, test_dates, test_stations)

print(f"Aligned val rows: {len(y_v_a)} | test rows: {len(y_t_a)}")
print(f"Val bloom rate: {y_v_a.mean():.1%} | Test: {y_t_a.mean():.1%}")

# ── Ensemble sweep ────────────────────────────────────────────────────────────
print("\nEnsemble sweep (XGB / LR / LSTM weights):")
best_val, best_combo = 0, (0.4, 0.4, 0.2)
for w_xgb in [0.2, 0.3, 0.4, 0.5]:
    for w_lr in [0.2, 0.3, 0.4, 0.5]:
        w_lstm = round(1 - w_xgb - w_lr, 1)
        if w_lstm < 0.1 or w_lstm > 0.6:
            continue
        ens_v = w_xgb*xgb_v + w_lr*lr_v + w_lstm*lstm_v
        ens_t = w_xgb*xgb_t + w_lr*lr_t + w_lstm*lstm_t
        v = roc_auc_score(y_v_a, ens_v)
        t = roc_auc_score(y_t_a, ens_t)
        if v > best_val:
            best_val, best_combo = v, (w_xgb, w_lr, w_lstm)
            print(f"  XGB={w_xgb} LR={w_lr} LSTM={w_lstm}: Val={v:.3f} Test={t:.3f} <-- best")
        else:
            print(f"  XGB={w_xgb} LR={w_lr} LSTM={w_lstm}: Val={v:.3f} Test={t:.3f}")

w_xgb, w_lr, w_lstm = best_combo
ens_test = w_xgb*xgb_t + w_lr*lr_t + w_lstm*lstm_t
print(f"\nBest combo: XGB={w_xgb} LR={w_lr} LSTM={w_lstm}")
print(f"Best ensemble Val AUC:  {best_val:.3f}")
print(f"Best ensemble Test AUC: {roc_auc_score(y_t_a, ens_test):.3f}")
print(f"Best ensemble Test AP:  {average_precision_score(y_t_a, ens_test):.3f}")
print("\nClassification report (threshold=0.5):")
print(classification_report(y_t_a, (ens_test >= 0.5).astype(int),
                             target_names=['no bloom', 'bloom']))

# Run this in a quick shell to test LR+XGB only
import pandas as pd, numpy as np
from sklearn.metrics import roc_auc_score

# Load the aligned probabilities from ensemble_final.py output
# We need to re-run just the sweep without LSTM
# Add this block at the end of ensemble_final.py temporarily:

print("\nLR + XGB only (no LSTM):")
for w_xgb in [0.2, 0.3, 0.4, 0.5, 0.6]:
    w_lr = round(1 - w_xgb, 1)
    ens_v = w_xgb*xgb_v + w_lr*lr_v
    ens_t = w_xgb*xgb_t + w_lr*lr_t
    v = roc_auc_score(y_v_a, ens_v)
    t = roc_auc_score(y_t_a, ens_t)
    print(f"  XGB={w_xgb} LR={w_lr}: Val={v:.3f} Test={t:.3f}") 