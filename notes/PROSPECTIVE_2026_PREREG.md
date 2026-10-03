# Pre-registration: the 2026 season as a clean test (written 2026-10-02, before any 2026 row is scored)

**Why.** Every LIS number so far was computed on years we had already looked at (the 35 features
were chosen partly on 2023-25). DEEP (M. Lyman, 2026-10-02) sent profile and lab chlorophyll for
January-July 2026. Those rows have never been scored by any model. This is the first test the
project could not have tuned to.

**What we already know (disclosed).** While checking the files we computed only summary statistics
of the 2026 chlorophyll itself, never a model score:
- 133 surface lab-profile pairs; corrected/lab median 0.99;
- 3.8% of corrected surface values and 3.0% of lab values are above 10 µg/L.

So 2026 so far is a low-bloom season, and the test will have few events.

## Fixed now

**Model.** The locked 28-day logistic regression exactly as evaluated in `notes/S1_NUMBERS_SHEET.md`:
- C = 0.05, balanced classes, the 35 features;
- trained on rows dated ≤ 2020-01-01 − 28 d (`final_evaluation_threshold_sweep.py`).

No refit and no feature changes. The 2024 correction (below) touches only test-period rows, so this
model and its thresholds are unchanged by it.

**Thresholds** (both chosen on validation, 2020-2022):
- t = 0.47 (alert budget, ≤ 8 alerts/month);
- t* = 0.25 (validation POD ≥ 0.8).

**Data.** 2026 station-days built by the same feature code as the S1 file:
- chlorophyll on DEEP's corrected (lab) scale;
- causal climatology from rows before each date;
- tides joined on the previous completed month;
- gusts t-2..t;
- temperature, salinity, DO and % saturation from DEEP's 2026 profiles (requested from DEEP on
  2026-10-02).

The test is not run until those arrive.

**Label.** `label_utils.forward_window_label`, horizon 28 d, bloom = corrected chlorophyll > 10 µg/L.
Unobserved or unfinished windows are NaN and excluded, so with data to 2026-07-17 only rows whose
window is resolved count.

**Calendar baseline.** The station-month bloom rate over all labelled rows dated before 2026-01-01
− 28 d. With < 5 rows, the month rate across stations is used; failing that, the overall rate. This
is the same rule as `notes/CALENDAR_BASELINE_PREREG.md`.

## Tests

1. **Primary:** AUC of the model minus AUC of the calendar on the resolved 2026 rows, with a
   station-clustered bootstrap (2,000 resamples, seed 42) and a one-sided p.
   - "Beats the calendar in 2026" only if p < 0.05.
   - If there are fewer than 5 positive rows, the test is declared **underpowered** and reported
     descriptively, with no claim either way.
2. **Secondary (descriptive):**
   - precision, recall and alerts per month at t = 0.47 and t* = 0.25;
   - the same for the calendar at a matched alert count.
3. **Rerun** when DEEP's August-October 2026 data arrive, with the same rules. The full-season result
   replaces the partial one, and both are kept.

**Whatever the result, it is reported as is.** No change to the model, threshold, label or baseline
after seeing it.

## Result

*(empty until run)*
