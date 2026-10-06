# Current numbers on the lab-consistent label (S1), after the 2026-09-28 audit

## UPDATE 2026-10-02: 2024 now on the corrected (lab) scale. These numbers supersede the ones below where they differ.

**What changed.** DEEP (M. Lyman) sent profile chlorophyll, raw and corrected, for Jan 2024 - Jul 2026.
- DEEP's correction is exactly linear per cruise. Those lines reproduce our 2025 `Corrected_Chlorophyll`
  with zero difference.
- Our 2024 raw values equal DEEP's raw on all 812 depth samples (362 casts).
- `label_rebuild.py` now fills 2024 from these lines (`fill_corrected`). Corrected/lab median for 2024
  is 1.02.
- The 2024 one-day share above 10 µg/L fell from 0.133 (raw sensor) to 0.041.
- 2022-2023 are still on the raw scale (requested from DEEP).
- Train and validation (≤ 2022) are unchanged, so the model and both thresholds are unchanged.

**28-day test 2023-25** (`data/rerun_2024fix_eval28.log`; 683 rows, **25 events**, base 3.7%):
- **AUC 0.590 [0.427, 0.757].**
- **Per year:**
  - 2023: AUC 0.433, 12 events (unchanged);
  - **2024: AUC 0.952, 9 events** (was 0.848 on 49 raw-scale events);
  - 2025: AUC 0.537, 4 events.
- **Budget threshold t = 0.47:** precision 0.163, recall 0.280 (7 of 25), lift 4.45, 2.1 alerts/month.
- **POD rule t* = 0.25:** precision 0.045, recall 0.520, lift 1.22.
- **Reading:**
  - The old pooled 0.767 was carried by about 40 raw-sensor 2024 "events" that the lab scale does not
    confirm.
  - On the corrected label the model ranks 2024 very well and is near chance in 2023 and 2025, with
    only 16 events between them.
  - The pooled AUC is low partly because one model score scale is pooled across very different years.

**21-day walk-forward CV 2016-2025** (`data/rerun_2024fix_cv21.log`): pooled AUC **0.660**, 1,971 rows,
94 events.

**Pre-registered calendar test, rerun on the corrected data** (`data/rerun_2024fix_calendar.log`):
- **2016-25:** model 0.660 vs calendar 0.573, **+0.088 [+0.042, +0.135], p < 0.001. Still PASS.**
- **2023-25:** model 0.602 vs calendar 0.706, −0.104 [−0.258, +0.046], p = 0.91.
  - Not significant either way (16 events), but the calendar is ahead.
  - Honest claim: "no better than the calendar in 2023-25".

**Hybrid:** still not adopted. On development folds the hybrid is below the locked model, −0.008
(`data/rerun_2024fix_hybrid.log`).

**Rerun on the corrected 2024 (2026-10-02, `data/rerun4_*.log`):**
- **Significance, 28-day test** (683 rows, 25 events):
  - Station-shift null p = 0.70; station-year (timing) null p = 0.51.
  - **Month-of-year baseline AUC 0.698 vs model 0.590: −0.108 [−0.225, −0.008], p = 0.98.**
  - Read the other way: baseline > model, one-sided p ≈ 0.02 (post hoc; not the pre-registered direction, and the CI bound is barely past 0).
- **Station-specific, western five, t = 0.47:** global precision 0.188, recall 0.429 (3/7). A4 with its own
  threshold: precision 0.50, recall 0.75. No station clears precision > 0.5 with recall > 0.4.
- **Reference baselines, basin-day** (41 days, 3 events): model lift 1.52 vs persistence 1.95. All CIs
  include 0.
- **Basin alert** at t_basin = 0.55: POD 0.333 [0, 1], FAR 0.889 (TP 1 / FP 8 / FN 2).
- **Decision value, 8 visits/month, LIS:** alert-directed 9.9 visits/bloom [4.8, 35.0] vs calendar 11.0
  [4.7, 105.0]. The CIs overlap, so there is no demonstrated gain. (Narragansett: 1.4 vs 3.6.)
- **LR geometry, 21-day onset rows:** LIS AUC 0.643, precision 0.037 at t* (30 events) vs Narragansett
  0.806 / 0.638.
- **Point of no return:** unchanged conclusion. No pre-onset row reaches analogue risk ≥ 0.6.
- **Cadence thinning:** POD 0.375 at the full cadence, falling to 0 at a 70-day gap.
- **Warning operating point, 21-day test 2023-25, t* = 0.20** (560 rows, 16 events): POD 0.562, FAR 0.965,
  precision 0.035.
- **Warning robustness:** rerun with `--t-star 0.20`; per-station table in `data/warning_robustness.csv`.
- **Reading:**
  - On the corrected label, LIS boat data show no recent skill beyond the calendar.
  - The only robust LIS result is the 2016-2025 walk-forward edge (+0.088, p < 0.001).
  - Narragansett carries the forecasting claim.

**Clean test ahead:** `notes/PROSPECTIVE_2026_PREREG.md` (2026 season, pre-registered 2026-10-02).

Every number here comes from a re-run output file on the default (S1) path. The source file is
given for each group. The rationale and history are in `notes/LABEL_REBUILD_PREREG.md` §§10-15.
Use only these numbers when updating documents. For any result **not** listed, add the label
"(sensor label; not re-run)" rather than changing it or inventing a new value.

## What changed and why (one paragraph, reusable)
The Long Island Sound label used to come from DEEP's CTD fluorometer (`Chlorophyll`). Matched to
DEEP's lab chlorophyll on the same station and date, that sensor read 2.1-4.8× the lab in
1994-1999, 1.8-3.2× in 2009-2013, and 0.8-1.05× from 2016 on. DEEP (K. O'Brien-Clayton,
2026-09-22/23) confirmed that its lab and methods are unchanged for 30+ years, that the CTD
switched from a SeaBird to a YSI EXO2 around 2009/2010, and that it recommends the lab data.
M. Lyman (DEEP) confirmed that `Corrected_Chlorophyll` is corrected against the lab. The label and
every chlorophyll feature were rebuilt from it under a pre-registration (S1, the headline), with a
lab-only check (S4). The "2014 cliff" (sensor-label bloom share 0.42-0.59 in 2009-2013 → 0.03-0.11
from 2014) is mostly this sensor scale change. The lab record has no 2014 step. It does have a real,
temporary low in 2012-2017 (lab exceedance share 0.03-0.07, against 0.10-0.23 before and 0.10-0.19
after). The TMDL attribution was withdrawn on 2026-09-05; the "lab-change" reading was withdrawn
on 2026-09-23.

## The 2026-09-28 audit (read this first)
Four independent audits of both repos. What changed in the LIS pipeline:

**Look-ahead removed.**
- `chl_climatology` / `chl_anomaly` were built over all of 1993-2025. They now use only
  observations dated before each row (`label_rebuild.causal_climatology`).
- `tidal_gt_anom` / `tidal_msl_anom` had two problems: a full-record climatology, and the row's
  own month's mean, which includes later days. They now use the previous month against a
  prior-years climatology.
- The IEC transfer features got the same fixes.

**Label.** A forward window is unresolved (NaN, dropped) if it:
- holds no visit at all, or
- runs past the station's last visit without a bloom.

It is shared by every script (`label_utils.forward_window_label`); it was 0 before. This removed
about a third of rows (unobserved windows).

**Splits and thresholds.**
- Training rows are purged if their label window reaches the next split.
- The withdrawn t = 0.60 had been picked on the test sweep.
- One 21-day threshold constant, `locked_pipeline.T_STAR_21` = 0.20 (the pre-registered
  validation POD ≥ 0.8 rule), is used everywhere.
- The 28-day thresholds are chosen on validation.

**Forecast-time convention, stated.** The forecast is issued at the end of sampling day t, from
everything measured that day. So `max_gust_3d` (days t-2..t) and `dip_change` (day-t lab DIP) are
allowed, the same as the day-t chlorophyll.

**Disclosures that cannot be fixed after the fact.**
1. The 35 features were chosen partly using 2023-25 test results (`PRECISION_OPTIMIZATION_LOG.md`),
   so every 2023-25 number is optimistic. Only future data (the 2026 prospective season) is a clean
   test.
2. S1 in 2022-24 is the raw sensor at factor 1.0, because DEEP has no `Corrected_Chlorophyll` for
   those years; 2025 is lab-corrected (median 0.52 × raw). The scale is not uniform inside the test
   period.
3. `Corrected_Chlorophyll` and DIP exist only after DEEP's lab work. A real-time version would run on
   raw sensor values, which is lab latency, not look-ahead.

## Headline, 28-day label, single split (`data/test_predictions_S1.csv`, `data/rerun3_eval_S1.log`)
- **Test 2023-25:** 683 station-days (unresolved windows dropped), 65 events, base **9.5%**. Train 6,182 (8.3%), validation 701 (4.7%).
- **AUC 0.767** [0.647, 0.857] (station-year bootstrap; `significance_checks.py`).
- **Validation POD ≥ 0.8 threshold, t* = 0.25:** precision **0.151**, recall **0.785**, lift **1.59**; 51 TP / 287 FP / 14 FN.
- **Alert budget (≤ 8 alerts/month on validation), t = 0.47:** 4.8 alerts/month on test; precision **0.354**, recall **0.523**, lift **3.72**; 34 TP / 62 FP / 31 FN.
- **Lab-only S4:** AUC 0.758 on 161 rows / 15 events; at its validation t* = 0.30, precision 0.204, recall 0.733, lift 2.19.

## Significance and the calendar (`significance_checks.py`, `notes/CALENDAR_BASELINE_PREREG.md`)
- **Better than chance:** station-shift null, p < 0.001.
- **Timing within a season is not shown:** station-year shift null, p = 0.42.
- **Single split vs a training-year station-month calendar:** +0.039 AUC [−0.045, +0.112], p = 0.17. Not significant.
- **Pre-registered walk-forward 2016-2025, 21-day, 121 events:** model 0.693 vs calendar 0.616, **+0.077 [+0.034, +0.121], p < 0.001. PASS.** The model wins 6 of 10 folds.
  - In 2023-25 it is a tie: −0.013, p = 0.64.
- **Pre-registered "calendar + conditions" model: not adopted.** Development 0.668 vs locked 0.676. The locked model already encodes season and site.

## Per-station, western five, global t = 0.47 (`data/rerun3_station_specific_models.log`)
- Global model on the western subset: precision 0.476, recall 0.690 (20 TP / 22 FP / 9 FN).
- Station-tuned thresholds (A and B) do not beat it.
- The log's "@0.60" labels mean the global threshold, now 0.47.

## 21-day operating point (`T_STAR_21` = 0.20)
- **Walk-forward CV** (`rolling_origin_cv.py --horizon 21`): pooled AUC **0.693**, 1,971 rows / 121 events (was 0.759 before the audit and 0.772 before 2026-09-28).
- **Test 2023-25 at t* = 0.20** (`scripts/warning/warning_robustness.py`): POD **0.791** [0.636, 0.904], precision **0.115** [0.065, 0.165], FAR 0.885; 34 TP / 261 FP / 9 FN, 560 rows.
  - Extra years 2016-19: POD 0.500, precision 0.095.
- **Locked fit ≤ 2019, station-day** (`reference_baselines.py`): base 7.7%, model POD 0.791, precision 0.125, lift **1.63**.
  - Against always-alert: +0.63 [+0.35, +0.92], clearly better.
  - Station-month and day-of-year climatology degenerate to always-alert on validation.
  - Persistence: lift 3.26 at POD 0.279.

## Basin level
- **Basin-day** (`reference_baselines.py`): model t = 0.55, lift 1.75, POD 0.556. Against always-alert: +0.76 [−1.00, +2.25], not clear (month-block bootstrap).
- **Basin search:** best validation lift 1.82× at the 25th percentile of its null, which is noise. Test lift 1.15× on 39 days / 8 events.

## Decision value, 8 visits/month (`data/rerun3_decision_value.log`)
| | LIS visits per bloom | LIS share caught | Narragansett visits per bloom |
|---|---|---|---|
| Calendar sampling | 6.2 [3.1, 21.0] | 0.37 | 3.65 |
| Climatology | 4.5 [2.6, 11.7] | 0.51 | 1.72 |
| Alert-directed, top-V | 4.5 [2.8, 9.9] | 0.51 | 1.42 |

In LIS, alerts tie climatology. In Narragansett, alerts beat it.

## IEC zero-shot transfer (`data/iec_zero_shot_results.csv`, primary 2020-25 onset, 404 rows, 126 events)
- Model AUC **0.667** [0.606, 0.725] (was 0.707).
- At its calibration-chosen t* = 0.93: lift **2.18** [1.57, 2.85], POD 0.151.
- The withdrawn t = 0.60 gives lift 1.37.
- Station-month climatology (threshold from calibration rows): AUC 0.566, lift 1.12.
- **The model transfers better than the IEC calendar.**

## Class overlap and rarity (`data/lr_geometry_summary.csv`, 21-day onset rows)
- **LIS:** base 0.045, AUC 0.673, OVL 0.737, precision 0.064, POD 0.750.
- **Narragansett:** base 0.351, AUC 0.806, OVL 0.523, precision 0.638.
- The Sound separates the classes worse as well as being rarer.

## Point of no return (`data/rerun3_point_of_no_return.log`)
Re-run: 322 pre-onset observations over 98 events. Conclusions are in the log. Not re-summarized
here; check it before quoting.

## Narragansett (being corrected by the fork audit fix; see that repo's CLAUDE.md for current values)
Current fork values after its 2026-09-28 audit (fork CLAUDE.md and findings §5, §24-25, §29-30):
- **Onset GB:** AUC 0.829, precision 0.682 [0.584, 0.783] at POD 0.572, lift 1.94 [1.53, 2.51].
- **Rolling CV:** 0.666 / lift 2.47 / AUC 0.877.
- **Beats the calendar on bloom starts in 9 of 9 years:** pooled +0.060 [+0.047, +0.074], p < 0.0001; 2023 +0.066, p = 0.0005.
- **74-site transfer, leak-free:** median lift 1.51, 65 of 74 with CI above 1, median AUC 0.74.
- **Local refit vs zero-shot:** refit is better on lift at 10 of 16 top sites (median +0.05).
- **Matched-rarity lift:** 9.15× [6.60, 13.64].
- **Tank-sensor forecast:** onset AUC 0.804 (full 0.829).
- **Unchanged:** the NN negatives and the device work.
