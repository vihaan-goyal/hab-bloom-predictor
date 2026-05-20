import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import (roc_auc_score, average_precision_score, 
                             classification_report, confusion_matrix)
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

print("Loading data...")
df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])
df['bloom_7d_ahead'] = df.groupby('station_name')['bloom'].shift(-7)

features = [
    'latitude', 'longitude', 'month',
    'chl_anomaly', 'chl_climatology',
    'chl_roll7_mean', 'chl_roll7_std',
    'chl_lag3', 'chl_lag7', 'chl_lag14', 'chl_lag21',
]

# Splits
train = df[df['date'].dt.year <= 2019]
val = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]
test = df[df['date'].dt.year >= 2023]

def prepare(split):
    X = split[features + ['bloom_7d_ahead']].dropna()
    y = X.pop('bloom_7d_ahead')
    X = X.loc[:, ~X.columns.duplicated()].reset_index(drop=True)
    y = y.reset_index(drop=True)
    return X, y

X_train, y_train = prepare(train)
X_val, y_val = prepare(val)
X_test, y_test = prepare(test)

print(f"Train: {len(X_train):,} | Val: {len(X_val):,} | Test: {len(X_test):,}")
print(f"Test bloom rate: {y_test.mean()*100:.1f}%")

# Train on train+val combined for final model
X_trainval = pd.concat([X_train, X_val]).reset_index(drop=True)
y_trainval = pd.concat([y_train, y_val]).reset_index(drop=True)

scale_pos_weight = (y_trainval == 0).sum() / (y_trainval == 1).sum()
model = XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1,
    scale_pos_weight=scale_pos_weight, random_state=42,
    n_jobs=-1, eval_metric='logloss', verbosity=0
)
model.fit(X_trainval.values, y_trainval.values)

probs = model.predict_proba(X_test.values)[:,1]
preds = (probs > 0.5).astype(int)

print("\n" + "="*50)
print("FINAL TEST SET RESULTS (2023-2025)")
print("="*50)
print(classification_report(y_test, preds))
print(f"AUC-ROC:          {roc_auc_score(y_test, probs):.4f}")
print(f"Avg Precision:    {average_precision_score(y_test, probs):.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, preds)
print(f"\nConfusion Matrix:")
print(f"  True Negatives:  {cm[0,0]:,}")
print(f"  False Positives: {cm[0,1]:,}")
print(f"  False Negatives: {cm[1,0]:,}")
print(f"  True Positives:  {cm[1,1]:,}")

# Save results
results = {
    'auc_roc': roc_auc_score(y_test, probs),
    'avg_precision': average_precision_score(y_test, probs),
    'true_negatives': int(cm[0,0]),
    'false_positives': int(cm[0,1]),
    'false_negatives': int(cm[1,0]),
    'true_positives': int(cm[1,1]),
}
pd.Series(results).to_csv("data/final_test_results.csv")
print("\nSaved to data/final_test_results.csv")