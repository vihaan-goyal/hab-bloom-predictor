import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report

# Load probabilities saved by the other two scripts
xgb_val  = pd.read_csv("data/xgb_val_probs.csv")['xgb_prob'].values
xgb_test = pd.read_csv("data/xgb_test_probs.csv")['xgb_prob'].values
y_val    = np.load("data/y_val.npy")
y_test   = np.load("data/y_test.npy")

lstm_val  = np.load("data/lstm_val_probs.npy")
lstm_test = np.load("data/lstm_test_probs.npy")
lstm_val_labels  = np.load("data/lstm_val_labels.npy")
lstm_test_labels = np.load("data/lstm_test_labels.npy")

# LSTM sequences may have fewer rows than XGBoost due to sequence building
# Use only the overlapping labels
print(f"XGBoost val rows: {len(xgb_val)} | LSTM val rows: {len(lstm_val)}")
print(f"XGBoost test rows: {len(xgb_test)} | LSTM test rows: {len(lstm_test)}")

# Individual scores
print(f"\nXGBoost  Val AUC: {roc_auc_score(y_val,  xgb_val):.3f}")
print(f"XGBoost  Test AUC: {roc_auc_score(y_test, xgb_test):.3f}")
print(f"LSTM     Val AUC: {roc_auc_score(lstm_val_labels,  lstm_val):.3f}")
print(f"LSTM     Test AUC: {roc_auc_score(lstm_test_labels, lstm_test):.3f}")

# Simple average ensemble on matching labels
# Find rows where both models have predictions by matching label arrays
if len(lstm_val) == len(y_val):
    for w in [0.3, 0.5, 0.7]:
        ens_val  = w * xgb_val  + (1-w) * lstm_val
        ens_test = w * xgb_test + (1-w) * lstm_test
        val_auc  = roc_auc_score(y_val,  ens_val)
        test_auc = roc_auc_score(y_test, ens_test)
        print(f"\nEnsemble (XGB={w:.0%} / LSTM={1-w:.0%})")
        print(f"  Val AUC: {val_auc:.3f} | Test AUC: {test_auc:.3f}")
else:
    print("\nRow counts differ — LSTM uses sequences so has fewer rows.")
    print("Ensemble requires aligned indices. Run alignment step first.")
    print("For now, best standalone model is XGBoost.")