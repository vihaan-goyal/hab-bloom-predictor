# HAB Bloom Predictor — Precision Improvement Master Log
# Current best: Precision=0.465, Recall=0.446, F1=0.455, AUC=0.814 (threshold 0.60)
# Corrected baseline (start): Precision=0.307
# Total gain: +15.8pp precision, F1 0.307->0.455

---

## INTEGRATED (in pipeline)

| Approach | Delta Prec | Delta F1 | Notes |
|---|---|---|---|
| chl_roll14_mean + chl_roll21_mean | +10.3pp | +1.2pp | Longer accumulation signal |
| tidal_gt_anom + tidal_msl_anom | +6.0pp | +1.7pp | Monthly tidal mixing anomaly |
| LR C=0.05 regularization | +3.9pp | +1.3pp | Stronger L2 vs default C=1.0 |
| sal_lag2 + sal_lag3 + sal_lag4 | -0.003pp | +1.2pp | Salinity trajectory lags |
| percent_saturation | +1.9pp | +0.9pp | Surface O2 saturation (depth_code=S ERDDAP), 0.446->0.465 |

---

## TESTED AND REJECTED

| Approach | Result | Reason |
|---|---|---|
| XGBoost (tuned) | -15pp prec | Overfits small val set |
| MLP-64-32 | +0.9pp prec, -25pp recall | Threshold artifact, not real |
| Ensemble LR+XGB | Marginal | LR dominates at 80% weight |
| Two-stage classifier | 0 | Stage 1 flagged everything |
| Calibration (isotonic) | -8.5pp prec | Val too small for isotonic |
| Station-specific thresholds | -0pp global | Hurts globally, helps per-station |
| SPW tuning (XGBoost) | ~0 | LR dominates ensemble |
| chl_acceleration feature | -3pp | Wrong direction, not in top SHAP |
| chl_roll14_mean alone | +0.8pp | Less than with roll21 |
| Interaction features (9 types) | -1 to -7pp AUC | Multicollinearity, seasonal confounds |
| Polynomial features degree 2-3 | -17pp prec | Too many features, overfits |
| SMOTE oversampling | Fails | Train bloom rate 22.7% already too high |
| Self-training (10 configs) | -0.006 F1 | Val has too few confident positives |
| Self-training balanced | -0.009 F1 | 14 pseudo-pos too small to move boundary |
| NOAA ASOS wind features | -4pp prec | Seasonal confound, hurts AUC |
| MODIS satellite CHL | -7.8pp prec | Redundant with in-situ chl features |
| USGS river discharge | ~0 | r<0.03 all lags |
| NOAA buoys 44017/44025 | ~0 | 12% coverage, r<0.09 |
| Sentinel-3 satellite | N/A | Algorithm fails in estuarine waters |
| Copernicus Marine | ~0 | r=0.046 with bloom_28d |
| Bayesian prior correction | Untested separately | Affects calibration not AUC |
| sea_water_density | -1pp when combined | Post-2019 imputation noise |
| PAR | Marginal alone | Works only in high_pri group |
| chl_roll3_std | Marginal alone | Works only in high_pri group |
| pH | Marginal alone | 49% coverage |
| neighbor_chl5_mean | -2pp prec | Redundant with neighbor_chl3_mean |
| neighbor_temp3_mean | -3pp prec | Seasonal confound |
| nox_x_month | ~0 | Weak signal |
| TDN-LC | -1pp prec | Low coverage, weak signal |
| do_lag2/3/4 | ~0 | Marginal, already have do_lag1 |
| Longer point lags (chl_lag7/14/21) | -1pp prec | Adds noise vs rolling means |
| Lag differences (chl_lag_diff) | ~0 | Near-zero correlation |
| Extended training (≤2022) | Val too small | XGBoost overfits 382-row val |

---

## STATION-SPECIFIC RESULTS (not in global pipeline)

Strategy B (global model + per-station threshold) beats global at western stations:

| Station | Bloom Rate | Precision | Recall | F1 | Threshold |
|---|---|---|---|---|---|
| C1 | 17.5% | 0.800 | 0.571 | 0.667 | 0.60 |
| A4 | 20.0% | 0.625 | 0.625 | 0.625 | 0.60 |
| 02 | 33.3% | 0.571 | 0.667 | 0.615 | 0.60 |
| B3 | 27.5% | 0.545 | 0.545 | 0.545 | best-val |
| 01 | 16.7% | 0.400 | 0.667 | 0.500 | 0.60 |

Global model on these 5 combined: Prec=0.436, Rec=0.686, F1=0.533

---

## REMAINING IDEAS (not yet tried)

### High potential

| Idea | Rationale | Effort | Status |
|---|---|---|---|
| Stricter bloom label (CHL > 20 µg/L) | Rarer events, higher precision | 2 hrs | Not tried |
| Hourly wind gust data | Daily averages smooth out mixing events | 3 hrs | Not tried |
| CT DEEP bottom temperature | Thermal stratification = surface-bottom temp diff | 1 hr | Not tried -- check if in ERDDAP |
| CT DEEP Secchi depth | Water clarity = light penetration = bloom depth | 1 hr | Not tried -- check if in ERDDAP |
| Pre-1993 CT DEEP data | More training data from high-bloom era | 2 hrs | Check availability |
| Narragansett Bay transfer | Pre-train on similar estuary data | 4 hrs | Complex |

### Medium potential

| Idea | Rationale | Effort | Status |
|---|---|---|---|
| all_high_pri features (density+PAR+chl_std+pH) | +2.4pp prec, -5.4pp recall | Already tested | Could report as precision-max variant |
| Threshold 0.55 variant | +0.95pp recall, -7.2pp prec | Done | Already documented in README |
| XGBoost with cross-validated SPW on val F1 | Different tuning objective | 1 hr | Not tried properly |
| CyAN satellite (NASA cyanobacteria) | Different satellite product | Auth issues | Blocked |
| EPA STORET additional nutrients | More nutrient stations | 3 hrs | Not tried |
| USGS nutrient concentrations at gauges | Direct load vs proxy discharge | 2 hrs | Not tried |

### Low potential (likely ceiling)

| Idea | Rationale |
|---|---|
| More regularization tuning (C < 0.05) | C=0.01 already worse than C=0.05 |
| Different LR solver | Results are solver-independent |
| Label propagation | Same constraint as self-training |
| Transductive SVM | Computationally heavy, imbalance kills it |
| VAE synthetic generation | Same as SMOTE -- train rate already 22.7% |

---

## STRUCTURAL CONSTRAINTS (cannot be overcome with current data)

1. **Test bloom rate = 7.2%** -- post-TMDL nitrogen reduction genuinely lowered bloom frequency.
   At 7.2% base rate, a perfect ranker (AUC=1.0) would still struggle to exceed ~0.60 precision
   at reasonable recall. Current 0.465 = 6.5x better than random (0.072).

2. **Biweekly sampling** -- CT DEEP samples every 14 days in summer. Lag features at 3 and 7
   days are approximated from nearest reading within a tolerance window. True daily resolution
   would require autonomous sensors.

3. **74 test bloom events** -- with only 74 positives in the test set, each TP/FP change moves
   precision by ~1.3pp. Results within ~2pp of each other are within noise.

---

## RECOMMENDED NEXT STEPS (priority order)

1. **CT DEEP bottom temperature from ERDDAP** -- check if `sea_water_temperature` at depth_code='B'
   is available. Stratification = surface_temp - bottom_temp. If available, add as a feature.
   Strongest untested physical signal.

2. **Stricter bloom label (CHL > 20 µg/L)** -- rerun everything with a stricter threshold.
   Fewer bloom events but higher-confidence ones. Could move precision significantly.

3. **Secchi depth from ERDDAP** -- water clarity feature, never tested.

4. **CyAN satellite** -- fix the auth issue with proper .netrc OAuth. Different satellite
   product than MODIS, focuses specifically on cyanobacteria.

5. **Accept current result** -- 0.465 precision, F1=0.455, station-specific models reaching
   0.625-0.800 at western stations. Strong result for SJWP.