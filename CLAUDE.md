# CLAUDE.md — HAB Bloom Predictor

## Run instructions

```bash
# Use the BASE conda env: ~/anaconda3/python.exe (or `conda activate base`).
# The `hab` env is BROKEN (exit 127 on np.linalg.lstsq / sklearn fits): its
# pip-installed scipy conflicts with conda-forge MKL. Three in-place repairs
# failed (2026-09-01); recreate it if you need it:
#   conda env remove -n hab && conda env create -f environment.yml
# (2026-09-05: the fork's environment.yml is re-pinned to the base env's real versions and
#  verified to build from scratch; this repo's yml still lists the torch/xgboost extras.)

# Final evaluation with threshold sweep (test set 2023–2025)
python src/models/final_evaluation_threshold_sweep.py

# Daily inference for a given date (generates data/daily_predictions.csv)
python src/deploy/daily_inference.py --date 2022-07-19
```

## Primary data file

`data/hab_features_tidal.csv` — 11,447 station-days, 50 CT DEEP LISICOS stations,
1993–2025, with tidal anomaly and salinity-lag features. This is the input to both
the evaluation script and the daily inference pipeline.

## Deployed model

Logistic Regression, `C=0.05`, `class_weight='balanced'`, 35 features:
BASE + tidal_gt_anom + tidal_msl_anom + chl_roll14_mean + chl_roll21_mean +
sal_lag2 + sal_lag3 + sal_lag4 + percent_saturation + max_gust_3d

Requires `data/gust_features_daily.csv` — generate with:
`python src/features/add_gust_features.py`

Test AUC: 0.815 | Precision @0.60: 0.500 | Recall @0.60: 0.486 | F1 @0.60: 0.493

**Station-specific best operating points (test 2023–2025):**

| Station | Rate | Strategy | Threshold | Prec | Rec | F1 | TP | FP | FN |
|---------|------|----------|-----------|------|-----|-----|-----|-----|-----|
| C1 | 17.5% | B (global) | 0.60 | 1.000 | 0.571 | 0.727 | 4 | 0 | 3 |
| 02 | 33.3% | B (global) | 0.60 | 0.625 | 0.833 | 0.714 | 5 | 3 | 1 |
| 01 | 16.7% | B (global) | 0.60 | 0.500 | 1.000 | 0.667 | 3 | 3 | 0 |
| A4 | 20.0% | A (station-only) | 0.60 | 0.625 | 0.625 | 0.625 | 5 | 3 | 3 |
| B3 | 27.5% | A (station-only) | 0.50 | 0.556 | 0.455 | 0.500 | 5 | 4 | 6 |

Note: C1 precision=1.000 is genuine (4 TP, 0 FP) but small sample (7 test positives).

## Key scripts

| Script | Purpose |
|--------|---------|
| `src/models/final_evaluation_threshold_sweep.py` | Final test-set evaluation; threshold sweep |
| `src/models/station_specific_models.py` | Per-station threshold tuning (Strategy B) |
| `src/models/ablation_study.py` | Feature ablation (useful for paper) |
| `src/deploy/daily_inference.py` | Daily inference pipeline + alert emails |
| `src/deploy/dashboard.html` | Browser-based monitoring dashboard |

## End of every session

Update  (question, hypotheses, variables, results,
conclusion) with what changed. It is the one-page truth of the project.

## Experiment scripts

One-off experiments that are not part of the main pipeline are archived in
`src/models/experiments/`. Do not import from them.
