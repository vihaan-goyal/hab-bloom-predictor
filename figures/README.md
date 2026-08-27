# figures/ — what is safe to use

Most of the images in this directory were rendered before the 2026-08 audit and
depict results from label definitions since shown to be wrong. **Check a figure
against this list before it goes into a poster, paper, or slide.**

Provenance was recovered by matching `savefig(...)` calls across the repo. The
defects themselves are described in `src/archive/README.md`; current verified
numbers are in `CLAUDE.md`.

---

## ✅ Current — rendered from the corrected pipeline

Regenerated 2026-08-26 at the corrected operating point **t\* = 0.30**, on
leak-free features and right-censored labels.

| File | Produced by |
|---|---|
| `warning_operating_point_locked.png` | `warning_operating_point.py` |
| `warning_threshold_selection.png` | `warning_threshold_selection.py` |
| `cadence_thinning_curve.png` | `src/models/cadence_thinning.py` |

Regenerate any of them by rerunning the script named above.

## ✅ Descriptive — not affected by the label defects

These plot observed chlorophyll, dissolved oxygen, temperature and station
geography. They do not depend on the forward-looking bloom label, so the audit
does not touch them. (`bloom` here is "this reading exceeded 10 µg/L", which is
a fact about the sample, not the defective forward label.)

`bloom_frequency.png` · `bloom_trend.png` · `seasonal_chl_distribution.png` ·
`station_bloom_rates.png` · `temp_vs_chl.png` · `lag_correlation_decay.png` ·
`lis_timeseries.png` · `lis_chlorophyll_20200715.png` ·
`do_distribution_by_bloom.png` · `do_lag_correlation_decay.png` ·
`do_seasonal_pattern.png` · `do_station_gradient.png` · `do_temporal_trend.png`

---

## ❌ Superseded — produced by archived scripts

Every one of these comes from a script now in `src/archive/`. **Do not use.**

### From the positional row-shift label (Family C)

`shift(-7)` on a survey cadence with a ~21-day median gap spans a **median of
217 days**. These describe a roughly seven-month-ahead seasonal signal, not a
21-day forecast.

| File | Produced by |
|---|---|
| `shap_importance.png` | `shap_analysis.py` |
| `shap_summary.png` | `shap_analysis.py` |
| `feature_importances.png` | `baseline.py` |
| `bloom_prevention_curve.png` | `prevention_analysis.py` |
| `station_reduction_needed.png` | `prevention_analysis.py` |
| `station_sensitivity_map.png` | `prevention_analysis.py` |
| `bloom_prob_vs_aeration.png` | `aeration_intervention.py` |
| `intervention_priority_map.png` | `aeration_intervention.py` |
| `seasonal_intervention_windows.png` | `aeration_intervention.py` |
| `station_intervention_scores.png` | `aeration_intervention.py` |
| `lstm_training.png` | `lstm_model.py` (Family C sequences) |
| `convlstm_training_curve.png` | `convlstm_model.py` (Family C sequences) |

**The whole aeration / intervention framework is in this group.** So is every
SHAP figure from `shap_analysis.py`.

### From a threshold swept on the test set

| File | Produced by |
|---|---|
| `threshold_sweep.png` | `final_evaluation_threshold_sweep.py` |

That sweep is where the retired 0.60 operating point came from. The defensible
point is t\* = 0.30, selected on validation.

---

## ⚠️ Superseded — produced by Family B scripts still in `src/models/`

These scripts were not archived, but they build their own label inline: a
28-day horizon with no right-censoring, which scores unresolvable windows as
clean negatives and deflates the positive rate from 0.280 to 0.146. Their
figures inherit that. They also predate the climatology leakage fix.

| File | Produced by |
|---|---|
| `fig7_rf_importances.png` | `shap_corrected.py` |
| `fig8_shap_beeswarm.png` | `shap_corrected.py` |
| `fig9_lstm_training.png` | `lstm_corrected.py` |
| `calibration.png` | `calibration.py` |
| `acceleration_pr_curve.png` | `acceleration_feature.py` |
| `fp_feature_distributions.png` | `false_positive_analysis.py` |
| `precision_features_pr_curve.png` | `precision_features.py` |
| `regularization_path.png` | `regularization_sweep.py` |
| `spw_sweep.png` | `tune_scale_pos_weight.py` |
| `station_thresholds.png` | `station_thresholds.py` |
| `two_stage_pr_curve.png` | `two_stage_classifier.py` |

**`fig7_rf_importances.png` and `fig8_shap_beeswarm.png` are the source of the
SHAP ranking quoted in `notes/KEY_NUMBERS.md`.** Beyond the label defect, that
ranking has a second problem: `dip_x_month` appears in the top seven while
being 49.5% missing, and missingness alone tracks the label hard (`dip_change`
missing → bloom rate 0.201 vs 0.054 present). Median imputation means the
ranking is partly reading *"was this measured?"* rather than nutrient
chemistry. Dropping all four nutrient features moves test AUC by −0.0012.

---

## ❓ Unknown provenance — treat as suspect

No script in the repo produces these, so they cannot be regenerated or dated.
Several are clearly renamed copies of superseded work (`fig10`/`fig11` are
aeration; `fig_station_specific` is the per-station table that is now void;
`shap_*_corrected` correspond to `shap_corrected.py`, Family B).

`bloom_locations.png` · `fig2_station_bloom_rates.png` ·
`fig3_annual_monthly_bloom_freq.png` · `fig4_seasonal_chl_boxplot.png` ·
`fig5_temp_chl_scatter.png` · `fig6_lag_correlation_decay.png` ·
`fig10_aeration_priority_map.png` · `fig11_seasonal_intervention.png` ·
`fig12_dashboard_screenshot.png` · `fig_precision_recall.png` ·
`fig_station_specific.png` · `lr_feature_importance_corrected.png` ·
`precision_bootstrap_ci.png` · `selective_prediction.png` ·
`shap_bar_corrected.png` · `shap_beeswarm_corrected.png` ·
`warning_operating_point_sustained.png`

The descriptive ones among these (`fig2`–`fig6`, `bloom_locations`) are very
likely fine on content, since they show observed distributions rather than
model output — but nothing in the repo can confirm what produced them.

---

## Bottom line

Of 57 images, **3 are confirmed current**, 13 are descriptive and unaffected,
**24 are confirmed superseded**, and 17 cannot be traced. Regenerating the
superseded ones is not a re-render — the underlying analyses have to be rerun
against `locked_pipeline.add_forward_label` first, which is new work, not a fix.
