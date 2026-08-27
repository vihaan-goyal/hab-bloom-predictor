# figures/ — what is safe to use

Most of the images in this directory were rendered before the 2026-08 audit and
depict results from label definitions since shown to be wrong. **Check a figure
against this list before it goes into a poster, paper, or slide.**

Provenance was recovered by searching the whole repo for each filename, then
by `git log -S` and first-appearance commits for the ones no source mentions.
The defects themselves are described in `src/archive/README.md`; current
verified numbers are in `CLAUDE.md`.

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

## ❌ Superseded — produced by the `src/viz/generate_*.py` figure scripts

All three of these read `BLOOM_COL = "bloom_28d"`, the **baked** Family B label
column in `hab_features_daily.csv` — a 28-day horizon with no right-censoring.
That column has since been stripped from the canonical file. They also predate
the climatology leakage fix.

| File | Produced by |
|---|---|
| `fig2_station_bloom_rates.png` | `src/viz/generate_eda_figures.py` |
| `fig3_annual_monthly_bloom_freq.png` | `src/viz/generate_eda_figures.py` |
| `fig4_seasonal_chl_boxplot.png` | `src/viz/generate_eda_figures.py` |
| `fig5_temp_chl_scatter.png` | `src/viz/generate_eda_figures.py` |
| `fig6_lag_correlation_decay.png` | `src/viz/generate_eda_figures.py` |
| `fig_precision_recall.png` | `src/viz/generate_model_figures.py` |
| `fig_station_specific.png` | `src/viz/generate_model_figures.py` |
| `fig10_aeration_priority_map.png` | `src/viz/generate_aeration_figures.py` |
| `fig11_seasonal_intervention.png` | `src/viz/generate_aeration_figures.py` |

`fig10` and `fig11` are part of the aeration framework. `fig_station_specific`
shows the per-station table that is now void.

## ⏳ Stale but regenerable

Produced by scripts that still exist and are not defective, but rendered before
the fixes. Rerun the script to refresh.

| File | Produced by |
|---|---|
| `precision_bootstrap_ci.png` | `src/models/experiments/precision_bootstrap_ci.py` |
| `selective_prediction.png` | `src/models/experiments/selective_prediction.py` |
| `warning_operating_point_sustained.png` | `warning_operating_point.py` (sustained-label CV run) |

## 📷 Not generated by code

`fig12_dashboard_screenshot.png` — a screen capture of the dashboard.

## ❓ Genuinely orphaned — 4 files

No committed source has ever referenced these names; `git log -S` finds nothing
but this README. Their filenames were added as images only:

| File | First appears |
|---|---|
| `bloom_locations.png` | `f8af187` (2026-05-20) "add figures folder, move plots out of data directory" |
| `lr_feature_importance_corrected.png` | `5bf2d52` (2026-05-28) "checkpoint mid claude code refactor" |
| `shap_bar_corrected.png` | `5bf2d52` (2026-05-28) |
| `shap_beeswarm_corrected.png` | `5bf2d52` (2026-05-28) |

The likely story: `bloom_locations.png` predates the current code entirely — it
was moved out of `data/` when the repo was first organised. The three
`*_corrected.png` files arrived in a mid-refactor checkpoint and share the
`_corrected` suffix with `shap_corrected.py`, which today writes
`fig7_rf_importances.png` and `fig8_shap_beeswarm.png`. They are almost
certainly earlier outputs of that same script under its previous filenames,
which would make them Family B as well. Treat all four as unusable: nothing in
the repo can regenerate or date them.

## Bottom line

Of 57 images:

| | count |
|---|---|
| ✅ current, rendered from the corrected pipeline | 3 |
| ✅ descriptive, unaffected by the label defects | 13 |
| ❌ **superseded — do not use** | **33** |
| ⏳ stale but regenerable by rerunning a sound script | 3 |
| 📷 screenshot, not generated | 1 |
| ❓ orphaned, unusable and unregenerable | 4 |

Regenerating the superseded ones is not a re-render — the underlying analyses
have to be rerun against `locked_pipeline.add_forward_label` first, which is new
work, not a fix.

> **Note on method.** The first version of this file listed 17 figures as
> untraceable. That was an artifact of the scan, which only matched literal
> paths inside `savefig(...)` and so missed scripts that build the path from a
> variable or an argparse default. A repo-wide search by filename resolved 13 of
> the 17. Only 4 are genuinely orphaned.
