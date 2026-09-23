# Pre-registration: rebuilding the LIS chlorophyll label on a lab-consistent scale

Written 2026-09-23, **before any model has been re-run on a rebuilt label.** Nothing below
this line has been computed except the descriptive table in §1, which is what prompted it.
Any change to this file after the first model run is logged in §9 with a date and a reason.

## 1. Why this exists

CT DEEP replied on 2026-09-22 that its sampling, analysis methods and analytical laboratory
have not changed in 30+ years. The LIS label (`bloom_28d` in
`src/models/final_evaluation_threshold_sweep.py`, lines 102-112) is built from the
`Chlorophyll` column of `data/hab_features_tidal.csv`, which is the **CTD fluorometer**
reading, not DEEP's extracted **lab** chlorophyll. Matching the two on the same station and
date (`src/models/experiments/sensor_vs_lab_chl.py`, output `data/sensor_vs_lab_chl.csv`,
surface bottle CHLA from the UConn ERDDAP `DEEP_Nutrient` dataset):

| Years | Sensor ÷ lab (median, per year) | Lab share > 10 µg/L | Sensor share > 10 µg/L |
|---|---|---|---|
| 1994-1999 | 2.08-4.79 | 0.00-0.18 | 0.17-0.62 |
| 2003-2008 | 0.96-1.37 | 0.07-0.23 | 0.14-0.35 |
| 2009-2013 | 1.77-3.22 | 0.03-0.18 | 0.42-0.59 |
| 2016-2021 | 0.80-1.05 | 0.05-0.19 | 0.03-0.11 |
| 2022-2024 | 0.86-1.31 | 0.05-0.09 | 0.03-0.13 |

`Corrected_Chlorophyll` sits at 0.82-1.35 of the lab in every year from 1995 to 2021, but it
is empty for 2022-2024.

Two things overlap, and they have to be kept apart:

1. **A sensor scale change.** The fluorometer read roughly two to three times the lab in
   1994-1999 and 2009-2013, and about the same as the lab from 2016 on. The 2014 "cliff" in
   the label (sensor share 0.42-0.59 → 0.03-0.11) is mostly this.
2. **A real, temporary low period in the lab record.** Lab exceedance share was 0.10-0.23 in
   2008-2011, 0.03-0.07 in 2012-2017, and 0.10-0.19 in 2018-2021. This matches DEEP's
   recollection of a region-wide change "around 2011". Lab sample counts are low in 2012
   (74) and 2013 (101), so the start date is soft.

**Consequence:** the training years carry inflated exceedances in 1994-1999 and 2009-2013,
and the chlorophyll features (current value, lags, rolling means, trend, anomaly,
climatology, neighbour means) inherit the same scale drift. The test years 2023-2025 are
affected much less, because the sensor sits near the lab there.

## 2. Question

When the LIS chlorophyll series is put on a lab-consistent scale, for the label and for
every chlorophyll-derived feature, what are the test-set skill numbers, and how far do they
move from the ones currently reported?

## 3. Series (defined now, not after seeing results)

| Name | Chlorophyll value used for the label and all chlorophyll features | Role |
|---|---|---|
| **S0** | raw `Chlorophyll` (sensor), as now | reference: current pipeline |
| **S1** | `Corrected_Chlorophyll`; where it is missing, raw `Chlorophyll` multiplied by that year's median `Corrected_Chlorophyll / Chlorophyll` over rows that have both (at least 30 such rows); if a year has fewer than 30, raw `Chlorophyll` ×1 (this covers 2022-2024, where sensor ÷ lab was 0.86-1.31) | **primary** |
| **S2** | raw `Chlorophyll` divided by that year's median sensor ÷ lab from `data/sensor_vs_lab_chl.csv`; 2025, which has no lab data yet, uses the 2016-2024 median ratio | sensitivity: independent of DEEP's correction |
| **S3** | label from lab surface CHLA only; features from S1; a row is kept only if its forward 28-day window contains at least one lab sample; the test set is therefore 2023 plus 2024 up to 2024-05-07 (28 days before the last lab date, 2024-06-04) | sensitivity: the lab as referee |

Why S1 is primary: it is DEEP's own lab-anchored product, it covers 1993-2021 and 2025
directly, and it keeps every station-day. Its one assumption is the gap fill for
2022-2024. S2 and S3 each remove a different assumption.

**What "S1 is primary" means:** S0 is known to be on an inconsistent scale across the
training years, so **S1 replaces S0 as the headline whichever way the numbers move.** The
choice is made on measurement validity, now, not on results later.

## 4. Held fixed

Everything except the chlorophyll values: logistic regression, `C=0.05`,
`class_weight='balanced'`; the same 35-feature list; train 1993-2019, validation 2020-2022,
test 2023-2025; median imputation and scaler fitted on training rows only; the 10 µg/L cutoff;
the 28-day forward label rule; seed 42; `bootstrap_ci.py` with station-year clusters,
2000 draws.

Operating points reported:
- **t = 0.60**, the locked headline threshold, applied unchanged.
- **The validation-F1-maximising threshold** on the 0.10-0.90 grid (step 0.05), chosen on
  2020-2022 only. The current script's `best_t` is chosen on test F1; that is not used here.

## 5. Implementation, and a gate before any model runs

1. `src/models/label_rebuild.py` writes `data/hab_features_tidal_S1.csv`, `_S2.csv` and
   `_S3.csv`. Each is a copy of `hab_features_tidal.csv` with `Chlorophyll` replaced by the
   series and every chlorophyll-derived column recomputed (`chl_lag1`-`chl_lag4`,
   `chl_climatology`, `chl_anomaly`, `chl_anomaly_pct`, `neighbor_chl3_mean`,
   `neighbor_chl3_lag1`). The rolling means and `chl_trend` are already recomputed inside
   the evaluation script. The feature code is copied from `build_features()` in
   `src/transfer/iec_zero_shot.py` (lines 93-130), not imported.
2. `final_evaluation_threshold_sweep.py` gains `--input` (default unchanged:
   `data/hab_features_tidal.csv`), and for S3 a `--label-col` that reads a prebuilt label
   instead of computing one.
3. **Gate G1:** run the builder on raw `Chlorophyll` (S0). Every recomputed column must
   match the existing column in `hab_features_tidal.csv` to within 1e-9 on every row where
   both are present. If it doesn't, the builder is wrong; fix it before running anything
   else. Running with the default `--input` must reproduce test AUC 0.8150 exactly.
4. **Gate G2:** the S1 and S2 series, compared with lab CHLA on matched pairs, must sit at a
   median ratio of 0.75-1.35 in every year with 50 or more pairs. (S1 is already known to
   pass for 1995-2021; the gate exists to catch a bug in the gap fill or the join.)

## 6. Predictions (graded afterwards; not decision rules)

| # | Prediction | Reasoning |
|---|---|---|
| P1 | S1 training positive rate falls by at least 40% relative to S0 | sensor ÷ lab was 2-3× in 1994-1999 and 2009-2013 |
| P2 | S1 test base rate is within 2 percentage points of S0's 7.2% | 2023-2024 are filled from the raw sensor; only 2025 changes |
| P3 | S1 test AUC is within ±0.05 of 0.815 | the features the model leans on are relative (anomaly, trend, neighbours), so a scale fix should move ranking less than it moves the base rate |
| P4 | S1 precision at t=0.60 differs from 0.500 by more than its own CI half-width | a different training base rate shifts the calibration of `class_weight='balanced'` probabilities, and 0.60 was chosen on the S0 scale |
| P5 | S2 lands within ±0.03 AUC of S1 | two routes to the same lab scale |

## 7. How the result is reported

- S1 becomes the headline for every LIS number that depends on the label, with S0 alongside
  once, labelled as "original sensor-scale label".
- If S1 and S2 differ by more than 0.05 in test AUC, or their lift intervals don't overlap,
  that disagreement is reported as the finding, and neither is called the answer.
- S3 is reported with its (small) n and interval, as the lab-referee check.
- Every prediction in §6 is graded right or wrong in `notes/SCIENTIFIC_METHOD.md`.

## 8. What has to be re-run after S1, in this order

Each depends on the LIS label or the chlorophyll features:

1. `src/models/final_evaluation_threshold_sweep.py` → `bootstrap_ci.py` (headline numbers,
   CLAUDE.md table)
2. `src/models/station_specific_models.py` (per-station operating points)
3. The 21-day locked operating point (README: precision 0.125, POD 0.875, t*=0.35)
4. `src/models/decision_value.py` (15.4 → 8.3 visits per bloom)
5. `src/transfer/iec_zero_shot.py` (the model is trained on DEEP rows, so the IEC transfer
   result moves too; IEC's labels are IEC lab values and don't change)
6. The rarity/overlap comparison with Narragansett (OVL 0.44 vs 0.52; `lr_geometry`)
7. `notes/KEY_NUMBERS.md`, CLAUDE.md, the README, the UConn deck and the board

Narragansett, the 74-site transfer and the device work do not use the LIS label and are
unaffected.

## 9. Changes after the first run

Logged 2026-09-23. All three were made **before** any model was fit on S1, S2 or S3.

1. **`bloom` dropped from the rebuilt files.** Gate G1 failed on its first run for one
   column, `bloom`, which was aggregated from profile rows and agrees with
   `Chlorophyll > 10` on only 93.5% of station-days, so it can't be rebuilt from
   station-day values. It is not a model feature: the label is `bloom_28d`, recomputed
   from `Chlorophyll` inside the evaluation script. It is dropped from the rebuilt
   files together with `chl_roll3_std`, `neighbor_chl3_lag2` and `neighbor_chl5_mean`,
   which are also unused and not reproducible. G1 then passed on all 14 rebuilt
   columns (max difference 2.3e-13), and the S0 file reproduced test AUC 0.8150,
   AP 0.3565 and precision 0.500 at t=0.60 exactly.
2. **Where the climatology comes from.** `chl_climatology` is a station×month mean over
   every **profile** reading, all years (notebooks/eda_labels.ipynb, cell 11), so each
   series is also applied to `data/hab_labels_final.csv` before averaging. The
   neighbour feature uses 111·cos(41.1°) km per degree of longitude, the value that
   reproduces the original exactly.
3. **Bootstrap.** AUC and lift intervals come from `label_rebuild.py compare`, not
   `bootstrap_ci.py` (which reports precision, recall and F1 only). It uses the same
   scheme: station-year clusters, 2000 draws, seed 42.

## 10. Result (2026-09-23)

`data/label_rebuild_results.csv`; test 2023-2025.

| Series | Test n / positives | Base rate | AUC [95% CI] | t | Precision [CI] | Recall | Lift [CI] |
|---|---|---|---|---|---|---|---|
| S0 sensor (original) | 1,034 / 74 | 0.072 | 0.815 [0.734, 0.876] | 0.60 | 0.500 [0.360, 0.650] | 0.486 | 6.99 [4.97, 11.26] |
| **S1 corrected (headline)** | 1,034 / 65 | 0.063 | **0.804 [0.706, 0.878]** | 0.60 | **0.316 [0.179, 0.424]** | 0.477 | **5.03 [3.50, 6.88]** |
| S1, validation-F1 t | | | | 0.75 | 0.400 [0.133, 0.550] | 0.215 | 6.36 [2.63, 9.79] |
| S2 lab-calibrated | 1,034 / 98 | 0.095 | 0.799 [0.730, 0.852] | 0.60 | 0.383 [0.276, 0.466] | 0.469 | 4.05 [3.17, 5.32] |
| S3 lab label only | 161 / 15 | 0.093 | 0.760 [0.522, 0.915] | 0.60 | 0.471 [0.159, 0.778] | 0.533 | 5.05 [2.69, 11.36] |

The training positive rate went from 22.7% (S0) to 5.5% (S1) and 8.9% (S2).
Validation-F1 thresholds: S0 0.35, S1 0.75, S2 0.40, S3 0.45.

Predictions (§6):
- **P1 right:** training rate fell 76% (needed at least 40%).
- **P2 right:** test base rate 7.2% → 6.3%.
- **P3 right:** AUC 0.815 → 0.804.
- **P4 right:** precision fell 0.184, more than S1's CI half-width of 0.12.
- **P5 right:** S2 is 0.005 AUC from S1.

§7 disagreement check: S1 and S2 differ by 0.005 AUC and their lift intervals overlap,
so they agree.

## 11. Amendment A1: DEEP's answer, and series S4 (2026-09-23, before S4 is run)

K. O'Brien-Clayton (CT DEEP) replied at 11:52: *"I would not use the in situ fluorometer
data at this point. Use the lab data."* A DEEP seasonal is comparing lab and in-situ
chlorophyll. The CTD changed from a SeaBird to a YSI EXO2 around 2009/2010, consistent
with sensor ÷ lab rising from 1.37 (2008) to 1.84 (2009) and 2.25 (2010). Whether
pre-2010 `Corrected_Chlorophyll` was lab-corrected has been asked of DEEP and is not yet
answered.

S1 is a corrected fluorometer series, so it no longer matches the agency's guidance.
Under the rule at the end of this file, S1 is kept and reported, and a new series is
added.

| Name | Chlorophyll for features | Label | Role |
|---|---|---|---|
| **S4** | lab surface CHLA on station-days that have one; empty otherwise (the pipeline's training-median imputation handles gaps, unchanged). Lags, rolling means, trend and neighbour means use the same recipe on this series; `chl_climatology` is the station×month mean of all lab surface samples, all years (the lab analogue of the original's all-years profile mean) | `bloom_28d_lab`, as S3 | **headline label definition** |

Test set: as S3, 2023-01-01 to 2024-05-07, because the ERDDAP lab record ends
2024-06-04. That is roughly 160 rows and 15 events, so:

- **Headline rule.** S4 is the label definition the project reports as its main result,
  because the agency that collects the data says to use it. Its numbers are always shown
  with intervals, and S1 (AUC 0.804, lift 5.03) is shown beside it as the full-coverage
  lab-scale estimate. If S4's AUC interval is wider than 0.30, the talk and board say
  plainly that the lab-only test is too small to pin down skill, and they don't quote a
  single number without its interval.
- **Extension.** When DEEP releases lab chlorophyll after June 2024, the S4 test set is
  extended with **no code or parameter changes** and re-reported. Only then is it called
  final.
- **Predictions:** P6: S4 test AUC is in 0.65-0.85. P7: S4 AUC is no more than 0.03
  above S3's 0.760, since S4 loses the fluorometer's day-to-day detail and keeps the same
  label.

**Implementation note (before S4 ran).** The lab series has gaps, so `chl_trend` (a
4-point rolling slope) failed on windows containing a missing value. The slope now
skips missing points, in both `label_rebuild.py` and the evaluation script. On windows
without gaps it is identical: G1 still passes, and S0 and S1 reproduce 0.8150 and 0.8036.

**DEEP confirmation (2026-09-23, after S1 and S4 had run).** M. Lyman (CT DEEP),
answering whether pre-2010 corrected chlorophyll was corrected using the lab data:
"Yes, the corrected data has been corrected against the lab data." This confirms S1's
basis for the years it asks about. Our own check shows `Corrected_Chlorophyll` at
0.82-1.35 of lab through 2021, so empirically it is lab-anchored after 2010 as well.
Still unconfirmed: why the field is empty for 2022-2024, where S1 falls back to the raw
sensor (sensor ÷ lab 0.86-1.31 in those years). No series definition changes.

## 12. Result for S4 (2026-09-23)

| Series | Test n / positives | Base rate | AUC [95% CI] | t | Precision [CI] | Recall | Lift [CI] |
|---|---|---|---|---|---|---|---|
| **S4 lab only** | 161 / 15 | 0.093 | **0.782 [0.595, 0.921]** | 0.60 | 0.467 [0.000, 0.667] | 0.467 | 5.01 [0.00, 9.87] |
| S4, validation-F1 t | | | | 0.50 | 0.421 [0.000, 0.571] | 0.533 | 4.52 [0.00, 9.57] |

Validation AUC 0.847 on 310 rows. Training positive rate 15.3% (3,267 rows).

- **P6 right:** 0.782 is within 0.65-0.85.
- **P7 right:** 0.782 is no more than 0.03 above S3's 0.760.
- **Headline rule triggered.** The AUC interval is 0.326 wide, more than 0.30, so the lab-only
  test is too small to pin down skill. It is reported as "consistent with S1, not yet
  measurable on its own": the point estimates agree (0.782 against 0.804; lift 5.0
  against 5.0), and the S4 intervals include everything from barely-above-chance to
  excellent. S4 becomes final once DEEP's post-June-2024 lab data extend the test set.

## Open questions to CT DEEP / UConn

Sent 2026-09-23 (reply-all to DEEP, O'Donnell, Todd and the others on the thread):
- Did the CTD fluorometer, or its calibration, change around 2014?
- Is the corrected chlorophyll field the one DEEP recommends?

Not yet asked: why `Corrected_Chlorophyll` is empty for 2022-2024. Hold this for the reply
to DEEP's answer, or for the UConn talk.

If DEEP's answer changes the definition of S1 (for example, a different correction for the
gap years), that change is logged in §9 **before** S1 is run, or, if S1 has already run,
as a new series S4 with S1 kept and reported.
