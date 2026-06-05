# CLAUDE.md — HAB Bloom Predictor

## Run instructions

```bash
conda activate hab

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

## Key scripts

| Script | Purpose |
|--------|---------|
| `src/models/final_evaluation_threshold_sweep.py` | Final test-set evaluation; threshold sweep |
| `src/models/station_specific_models.py` | Per-station threshold tuning (Strategy B) |
| `src/models/ablation_study.py` | Feature ablation (useful for paper) |
| `src/deploy/daily_inference.py` | Daily inference pipeline + alert emails |
| `src/deploy/dashboard.html` | Browser-based monitoring dashboard |

## Experiment scripts

One-off experiments that are not part of the main pipeline are archived in
`src/models/experiments/`. Do not import from them.
