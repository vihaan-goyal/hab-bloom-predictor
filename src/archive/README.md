# src/archive — superseded pipelines. Do not use these to generate any result.

Every script in this directory computes its target with a label definition that
has since been shown to be wrong. Their outputs are not comparable to current
results and must not be quoted, plotted, or cited. Nothing in `src/` imports
from here, and nothing should start.

They are kept rather than deleted because they are the provenance of numbers
that were published in `CLAUDE.md`, `README.md` and `notes/`, and you need to be
able to trace where a stale figure came from.

The current label is `locked_pipeline.add_forward_label` (h=21, right-censored).
`label_utils.build_forward_label` is the same function with a `sustained_only`
option and a policy switch for unverifiable windows; `tests/test_label_equivalence.py`
pins the two together row for row.

The files are grouped by *which* defect they carry. The groups are not
interchangeable — the row-shift bug is far more severe than the horizon bug.

---

## Group 1 — Family B: 28-day horizon, no right-censoring

**Files:** `final_evaluation_threshold_sweep.py`, `ablation_study.py`

Each builds its own label inline:

```python
df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    ...
    if mask.any() and (chl[mask] > 10).any():
        labels[i] = 1
```

Two defects:

1. **Horizon is 28 days, not the locked 21.** Results are not comparable to
   anything produced by the current pipeline.
2. **No right-censoring.** The array is initialized to `0` and only ever written
   up to `1`, so a window that could never be resolved is scored as a clean
   negative rather than excluded.

At h=28, **33.4% of all rows (3,827 of 11,447) have no observation whatsoever in
`(t, t+28d]`** and are labeled negative anyway. That deflates the positive rate
from **0.297 among genuinely evaluable rows to 0.198**, inflating the negative
class and therefore specificity.

`final_evaluation_threshold_sweep.py` carries a second, independent defect: by
its own docstring it "runs a full threshold sweep on the TEST set (2023-2025)".
The 0.60 operating point published in `CLAUDE.md` came from that sweep, which is
selection on test reported as test performance. The defensible operating point
is **t\* = 0.30**, selected on validation by `warning_operating_point.py`.

This script also used to be the producer of `data/test_predictions.csv`, which
`bootstrap_ci.py`, `audit_flagged_windows.py` and `check_label_integrity.py` all
consume — so all three were reading Family B labels. It has been replaced by
**`src/models/emit_test_predictions.py`**, which emits the same schema from the
locked pipeline on leak-free features. Run that instead.

> Note: `locked_pipeline.py` once claimed it was "extracted verbatim from
> `final_evaluation_threshold_sweep.py`". Git disproves it — `locked_pipeline.py`
> was written fresh in `44b72b3` (2026-08-12), which never touched this script,
> and this script has used the 28-day uncensored label continuously since
> `c71d985` (2026-06-01). They were never the same. That claim has been removed.

---

## Group 2 — Family C: positional row-shift

**Files:** `baseline.py`, `final_evaluation.py`, `conditional_satellite_eval.py`,
`build_conv_sequences.py`, `build_sequences.py`, `shap_analysis.py`,
`failure_analysis.py`, `prevention_analysis.py`, `aeration_intervention.py`

**This is the severe one.** Each derives its target by shifting *rows*, not days:

```python
df['bloom_7d_ahead'] = df.groupby('station_name')['bloom'].shift(-7)
```

or, equivalently, `station_df.iloc[idx + FORECAST_HORIZON]['bloom']` in
`build_sequences.py`.

That is only a 7-day-ahead label if stations are sampled daily. **They are not.**
CT DEEP station visits are a survey cadence with a **median gap of 21 days**
(mean 45.1, p90 52). So `shift(-7)` spans:

| | days |
|---|---|
| median | **217** |
| p10 | 139 |
| p90 | 684 |
| max | 6,938 |

**100% of `shift(-7)` spans exceed 30 days.** The column named `bloom_7d_ahead`
is a label roughly **seven months** ahead, not seven days. Any model trained on
it learned a seasonal/climatological signal, not a short-range forecast.

Two consequences worth stating explicitly, because both were published:

- **The SHAP feature rankings from `shap_analysis.py` describe a seasonal
  signal.** They are not feature importances for a 21-day forecast and cannot be
  read as such.
- **The entire aeration / intervention framework** (`aeration_intervention.py`,
  `prevention_analysis.py`) was scored against that ~7-month label. Every
  intervention priority, suitability score and threshold in it is invalid for the
  operational question. `src/deploy/daily_inference.py` already omits aeration
  scoring for this reason, pending a rerun on corrected data.

Note that the SHAP ranking quoted in `notes/KEY_NUMBERS.md` came from
`shap_corrected.py`, which is Family B (still in `src/models/`), not from
`shap_analysis.py`. It carries the Group 1 defect instead, not this one.

---

## Group 3 — downstream consumers of Family C sequences

**Files:** `lstm_model.py`, `convlstm_model.py`

These do not build a label themselves; they load tensors built by the Group 2
sequence builders:

- `lstm_model.py` ← `data/X_sequences.npy`, `data/y_labels.npy` ← `build_sequences.py`
- `convlstm_model.py` ← `data/X_conv_sequences.npy`, `data/y_conv_labels.npy` ← `build_conv_sequences.py`

Their training code is sound — the year-based split is correct and normalization
statistics are computed on train only. They are archived solely because their
targets carry the row-shift defect. If the sequence builders are ever rewritten
against `add_forward_label`, these two are worth resurrecting largely as-is.

`conditional_satellite_eval.py` sits in Group 2 but also imports
`ConvLSTMHAB` from `convlstm_model.py`; they were moved together so that import
still resolves.

---

## Outputs

None of these files is the last writer of anything still consumed by live code.
The one entanglement — `data/test_predictions.csv` — was resolved before the move
by `src/models/emit_test_predictions.py`.

The remaining artifacts they produce (`final_test_results.csv`,
`ablation_results.csv`, `threshold_sweep_results.csv`, `figures/threshold_sweep.png`,
`figures/feature_importances.png`, `lstm_model.pt`, `convlstm_model.pt`, the
`*_sequences.npy` tensors, `conditional_satellite_eval.csv`) have no live
consumers. Any of those files still on disk was produced by a superseded label
and should be treated as stale.
