# CLAUDE.md — HAB Bloom Predictor

## Run instructions

```bash
# Use the BASE conda env: ~/anaconda3/python.exe (or `conda activate base`).
# The `hab` env is broken (scipy/MKL conflict). To rebuild it:
#   conda env remove -n hab && conda env create -f environment.yml

# Default input: the lab-consistent label, data/hab_features_tidal_S1.csv. Build it:
python src/features/add_tidal_features.py   # writes data/hab_features_tidal.csv
python src/models/label_rebuild.py build     # writes data/hab_features_tidal_S1.csv
# Prefix HAB_FEATURES_CSV=data/hab_features_tidal.csv to reproduce the original sensor label.

# Final evaluation (test 2023–2025); add --no-censor to reproduce the old label
python src/models/final_evaluation_threshold_sweep.py --tag _S1

# Daily inference for a given date (writes data/daily_predictions.csv)
python src/deploy/daily_inference.py --date 2022-07-19
```

## Primary data files

- `data/hab_features_tidal_S1.csv`: the default. The label and every chlorophyll feature are rebuilt from DEEP's lab-corrected `Corrected_Chlorophyll`. It feeds evaluation and daily inference.
- `data/hab_features_tidal.csv`: 11,447 station-days, 50 CT DEEP LISICOS stations, 1993–2025, with tidal-anomaly and salinity-lag features, labelled from the raw CTD fluorometer (the original sensor label). S1 is built from it.

## Deployed model

Logistic Regression, `C=0.05`, `class_weight='balanced'`, 35 features:
BASE + tidal_gt_anom + tidal_msl_anom + chl_roll14_mean + chl_roll21_mean +
sal_lag2 + sal_lag3 + sal_lag4 + percent_saturation + max_gust_3d.
Requires `data/gust_features_daily.csv` (`python src/features/add_gust_features.py`).

Test (2023–2025, 28-day label, S1, leak-free, right-censored): 951 rows, 65 events, base 6.8% |
AUC 0.789 [0.690, 0.864] | at the pre-registered validation threshold t* = 0.25: precision 0.119,
recall 0.846, lift 1.74 [1.46, 2.04]. The old t = 0.60 (lift ~5) was picked on the test years and is
withdrawn as an operating point.

- 2026-09-28 leak fix: `chl_climatology`, `chl_anomaly`, `tidal_gt_anom` and `tidal_msl_anom` used
  full-record (1993-2025) climatologies. They are now causal (data before each row only). Keep it that
  way: any climatology or anomaly feature must use only earlier data.
- S1 replaced the sensor label on 2026-09-23 (the CTD fluorometer read 2-5× the lab; DEEP advised the
  lab data). Sensor-label numbers (AUC 0.815) are superseded.
- The 21-day operating point, per-station table, S4 check and which results are not yet re-run are in
  `notes/S1_NUMBERS_SHEET.md` (the only source for current numbers); history in
  `notes/LABEL_REBUILD_PREREG.md`.

## Key scripts

| Script | Purpose |
|--------|---------|
| `src/models/final_evaluation_threshold_sweep.py` | 28-day evaluation; validation-chosen threshold; test sweep for display only |
| `tests/check_dependencies.py` | Lists imports missing from `environment.yml` |
| `src/models/station_specific_models.py` | Per-station threshold tuning (Strategy B) |
| `src/models/ablation_study.py` | Feature ablation |
| `src/deploy/daily_inference.py` | Daily inference pipeline + alert emails |
| `src/sim/method_mc.py` (+ `tank_model.py`, `loop_controller.py`) | Layer 2 tank simulation of the treatment loop; see `notes/mitigation/LAYER2_SIM_RESULTS.md` |
| `src/lab/lis_water_recipe.py` | DEEP-based Sound water stats and tank water recipe |
| `hardware/alerter_uno/` | Arduino alerter firmware (`alerter_uno.ino`), laptop link (`alerter_link.py`), build guide (`README.md`) |
| `src/sim/rake_field.py`, `floc_kinetics.py`, `rake_capture.py` | Earlier clay-device simulation; see `notes/DEVICE_SIMULATION.md` |

## Bench experiments

The current plan is in `notes/mitigation/`:
- `EXECUTION_PLAN.md`: the overall plan;
- `00_CONTROL_LOOP.md`: shared loop rules and hypotheses H1-H4;
- `PROCEDURES.md`, `MATERIALS_LIST.md`, `WATER_RECIPE.md`;
- one file per method.

## End of every session

Update `notes/SCIENTIFIC_METHOD.md` (question, hypotheses, variables, results, conclusion)
with what changed. It is the one-page truth of the project.

## Experiment scripts

One-off experiments that are not part of the main pipeline are archived in
`src/models/experiments/`. Do not import from them.
