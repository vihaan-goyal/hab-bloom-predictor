# Pre-registration: the 2026 season as a clean test (written 2026-10-02, before any 2026 row is scored)

**Why.** Every LIS number so far was computed on years we had already looked at (the 35 features
were chosen partly on 2023-25). DEEP (M. Lyman, 2026-10-02) sent profile and lab chlorophyll for
January-July 2026. Those rows have never been scored by any model. This is the first test the
project could not have tuned to.

**What we already know (disclosed).** While checking the files we computed only summary statistics
of the 2026 chlorophyll itself, never a model score:
- 133 surface lab-profile pairs (profile S row joined to the mean of that station-day's lab surface samples; clarified 2026-10-02, numbers unchanged); corrected/lab median 0.99;
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

## Amendment A1 (2026-10-14, written before any 2026 row was scored)

DEEP (M. Lyman, 2026-10-13) sent the 2026 EXO profiles (Jan 8 - Jul 17; 225 casts, 11 cruises)
and corrected chlorophyll for 2022-2023. Nothing below was chosen after seeing a 2026 score.

1. **2022-23 corrected.** `label_rebuild.py` now fills 2022-23 from DEEP's per-cruise lines, as it
   did for 2024. Validation (2020-22) rows change, so the validation-chosen thresholds move:
   t = 0.40 (alert budget) and t* = 0.20 (POD rule). The model itself is unchanged (trained ≤ 2019).
   - The primary test is threshold-free and is not affected.
   - The secondary numbers are reported at **both** pairs: the thresholds fixed above
     (0.47 / 0.25) and the recomputed ones (0.40 / 0.20).
2. **2026 station-days.** One row per station and date: the mean over every depth row of the cast
   (the same aggregation as the 2025 rows); chlorophyll = DEEP's corrected value;
   `percent_saturation` from the depth-code S row.
3. **Nutrient features** (`nox_lag2`, `dip_lag2`, `dip_change`, `dip_x_month`) have no 2026 data,
   so they are missing and train-median filled, as for every 2025 row.
4. **Tides:** NOAA CO-OPS monthly means (MLLW datum), downloaded 2026-10-14; the 2025 months
   match the stored files exactly.
5. **Gusts:** NCEI's airport archive ends 2025-08-25. From 2025-08-26 the same three airports
   (BDR, GON, HVN) come from the Iowa Environmental Mesonet. On 2025 days both sources hold,
   daily maxima agree within 0.23 m/s, apart from one 156-knot report. Rule: drop reports
   > 75 kt (the stored record maximum is 72 kt).
6. **Gate before scoring:** the combined file must reproduce the 2023-25 test predictions exactly.

## Result (run 2026-10-14, partial season: DEEP data to 2026-07-17)

`python src/models/prospective_2026.py build` then `score`; log `data/prospective_2026_score.log`,
rows `data/prospective_2026_predictions.csv`.

- **Gates passed before scoring.**
  - Every rebuilt feature reproduces the stored 2025 rows (max difference 6e-14).
  - The model reproduces all 683 test predictions of 2023-25 (max difference 2e-14) with identical
    labels.
- **Rows.**
  - 225 station-days in 2026 (41 stations, Jan 8 - Jul 17).
  - 66 have a resolved 28-day window (Feb 10 - Jun 8).
  - **6 events**, base rate 0.091. That is at least 5, so the test is powered by the rule above.
- **PRIMARY: model AUC 0.814, calendar AUC 0.883, difference −0.069 [−0.121, −0.005], one-sided
  p = 0.98. The model does not beat the calendar in 2026.**
- **Secondary** (4 sampled months):

  | Threshold | Model alerts | Model TP | Model precision | Model recall | Calendar (same alert count) |
  |---|---|---|---|---|---|
  | 0.47 (fixed budget) | 1 | 1 | 1.00 | 0.17 | TP 0 |
  | 0.25 (fixed POD) | 15 | 4 | 0.27 | 0.67 | TP 4 |
  | 0.40 (recomputed budget) | 2 | 1 | 0.50 | 0.17 | TP 1 |
  | 0.20 (recomputed POD) | 22 | 4 | 0.18 | 0.67 | TP 6 |

- **Reading.**
  - On the first data the project could not have tuned to, the LIS boat-data model ranks well in
    absolute terms (0.81), but the station-month calendar ranks better.
  - This agrees with the 2023-25 result (no better than the calendar).
  - Reported as is; nothing is changed after seeing it.
  - To be rerun on the full season when DEEP's August-October data arrive.
