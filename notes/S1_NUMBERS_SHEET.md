# Current numbers on the lab-consistent label (S1), 2026-09-23

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

## Headline, 28-day label, single split (`data/test_predictions.csv`, `data/label_rebuild_results.csv`)
- Test 2023-2025: 1,034 station-days, 65 events, base rate **6.3%** (was 7.2%).
- AUC **0.804** [0.706, 0.878] (was 0.815).
- At t=0.60: precision **0.316** [0.179, 0.424] (was 0.500); recall **0.477** (was 0.486);
  **31 TP / 67 FP / 34 FN** (was 36/36/38 of 74); lift **5.03** [3.50, 6.88] (was 6.99).
- Training bloom rate **5.5%** (was 22.7%); validation 3.1%.
- Lab-only check S4: AUC **0.782 [0.595, 0.921]** on 161 test rows / 15 events. It is too small to
  stand alone until DEEP's post-June-2024 lab data arrive.
- All seven pre-registered predictions were right.

## Per-station, western five, global t=0.60 (`data/rerun_station_specific_models.log`)
| Station | Base rate | Precision | Recall | TP/FP/FN |
|---|---|---|---|---|
| A4 | 20.0% | 0.333 | 0.875 | 7/14/1 |
| B3 | 20.0% | 0.333 | 0.625 | 5/10/3 |
| C1 | 12.5% | 0.444 | 0.800 | 4/5/1 |
| 01 | 16.7% | 0.500 | 0.667 | 2/2/1 |
| 02 | 27.8% | 0.429 | 0.600 | 3/4/2 |

No western station and strategy clears precision > 0.50 with recall > 0.40. The old C1 1.000 is gone.

## 21-day operating point
- Locked fit ≤2019, test 2023-25 station-day (`data/reference_baselines.csv`): 954 rows, 43 events,
  base 4.5%. Model at t*=0.35: precision **0.117**, POD **0.744**, FAR 0.883, lift **2.59** (was
  0.132 / 0.917 / 2.63 on 956 rows / 48 events). Against always-alert: lift difference +1.59
  [1.07, 2.22], clearly better. Persistence: precision 0.164, POD 0.279, lift 3.65. Against
  climatology it was **not tested fairly under S1**: climatology's own validation-chosen threshold
  degenerated to t=0, so it equals always-alert. Keep the original statement, "not clearly better
  than climatology".
- Walk-forward CV predictions at t*=0.35, test 2023-25 (`warning_robustness.py`): POD **0.791**
  [0.636, 0.906], precision **0.114** [0.063, 0.163], FAR 0.886, 34 TP / 265 FP / 9 FN, base 4.2%,
  lift ~2.7 (was POD 0.875, precision 0.125, base 4.6%).
- **Open decision:** re-applying the pre-registered "highest t with CV-selection POD ≥ 0.8" rule
  on S1 gives t*=**0.20** (test POD 0.907, precision 0.072). Deploy keeps the frozen 0.35 until the
  user decides. Say "open" wherever t* is discussed.
- Pooled 21-day rolling-origin CV (`rolling_origin_cv.py --horizon 21`): AUC **0.772**, 3,653 rows /
  121 events, test years 2016-2025 (was 0.852, 4,040 / 156, 2015-2025).

## Basin level
- Basin-day (`reference_baselines.csv`): model t=0.65, lift **2.14** (41 days, 9 events);
  persistence 2.10; against always-alert +0.43 [−1.00, 1.77], not clear (was model 1.37, persistence
  1.81, 12 events). Say "a tie with persistence".
- Basin search (`data/basin_search_result.csv`, 912 cells, 200-shuffle null): best validation lift
  **2.05×** at the **70.5th percentile** of the null (median 1.79×, 95th percentile 2.86×): inside
  the null, so the search found noise. Test lift 1.56× (was 1.84× at the 52nd percentile, null median
  1.83×, 95th 3.01×).

## Decision value, 8 visits/month (`data/decision_value.csv`)
- LIS: calendar **17.8** [9.6, 55.0] → alert-directed top-V **9.7** [5.5, 26.6] visits per bloom;
  causal 7.8 [3.9, 40.4]; climatology **11.2** [5.7, 53.2]; share caught 0.28 → 0.51; **43** blooms
  (was 15.4 → 8.3, climatology 9.3, 0.29 → 0.54, 48 blooms).
- Narragansett unchanged: 3.81 → 1.45, climatology 1.76.

## IEC zero-shot transfer (`data/iec_zero_shot_results.csv`, primary 2020-25 onset, 949 rows, 126 events)
- Lift **1.57** [1.41, 1.75]; AUC **0.707** [0.656, 0.760] (was 1.84 [1.59, 2.11], AUC 0.732).
- Station-month climatology: lift 1.50, AUC 0.733. It **transfers better than chance and no better
  than a calendar.** 4 of 13 stations have a lift interval above 1 (was 5 of 13). It is inside the
  pre-registered band of 1.2-1.8.
- IEC chlorophyll method: Standard Methods 10200H through 2016, both in 2017, EPA 445.0 from 2018
  on. That is before the 2020-25 window, so the transfer is unaffected.

## Class overlap and rarity (`data/lr_geometry_summary.csv`, onset rows, 21 d)
- LIS: base **0.026**, AUC 0.770, OVL **0.620**, precision 0.055, POD 0.667 (was 0.036, 0.855, 0.445,
  0.112, 0.868).
- Narragansett unchanged: 0.347, 0.810, OVL 0.516, precision 0.641.
- Wording: the Sound's low precision is **"mostly rarity, not only"**. The Sound also separates the
  classes less well. **"Precision follows rarity, not skill" is withdrawn.**
- Matched-rarity tests (fork, Narragansett-only computations, unchanged): at matched 5% rarity with
  daily sampling, precision 0.09-0.14 (the Sound's 0.117 sits inside). Lift at rarity over nine CV
  years: 8.48× [5.98, 12.81] at T=52.5 and 6.92× [5.32, 9.31] at T=39, both above the Sound's 2.59.
  The fork's LIS reference is now precision 0.117, AUC 0.825 (21-day station-day test), base 0.045,
  lift 2.59.

## Point of no return (`data/ponr_rows.csv`)
544 pre-onset observations / 153 events (was 617). Analogue risk peak **0.42**, median 0.02 (was 0.62 /
0.04). Summer model counterfactual (M1 nutrients) 42% of events "locked in" → **0%** once physics
can vary (was 65% → 0%). The conclusion is unchanged: no point of no return.

## Unchanged (not LIS-label dependent)
Narragansett AUC 0.839, precision 0.70, lift 2.00 [1.50, 2.68]; rolling 0.656 / 2.50; the 74-site
transfer (median lift 1.58, 67 of 74, median AUC 0.74); the NN negatives; the device work.
