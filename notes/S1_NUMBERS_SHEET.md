# Current numbers on the lab-consistent label (S1), leak-free (2026-09-28)

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

## Leak fix, 2026-09-28 (read this first)
Four locked features were anomalies against full-record (1993-2025) climatologies, so test-period
data leaked into training rows: `chl_climatology`, `chl_anomaly` (station-month chlorophyll) and
`tidal_gt_anom`, `tidal_msl_anom` (monthly tides). They are now causal: each row uses only data dated
strictly before it (`label_rebuild.py causal_climatology`, `add_tidal_features.py`). The 28-day label
is now right-censored (windows past a station's last visit are dropped, not scored 0), and its
operating threshold is chosen on validation by the pre-registered rule. The fixes were first found on
the `worktree-climatology-fix` branch (2026-08-26) and never merged; that branch is archived as a tag.
Numbers marked **(pre-leak-fix, not re-run)** below come from the 2026-09-23 run.

## Headline, 28-day label, single split (`data/test_predictions_S1.csv`, `data/rerun2_*.log`)
- Test 2023-2025: **951** station-days (83 unresolvable windows dropped), **65** events, base **6.8%**.
- AUC **0.789** [0.690, 0.864] (station-year clustered bootstrap). Before the fix: 0.804 on 1,034 rows.
- **Operating threshold (pre-registered rule on validation: highest t with 2020-22 POD >= 0.80):
  t* = 0.25** (validation POD 0.848). Test: precision **0.119** [0.072, 0.166], recall **0.846**
  [0.706, 0.950], lift **1.74** [1.46, 2.04]; 55 TP / 408 FP / 10 FN.
- **t = 0.60 is withdrawn as an operating point:** it was picked on the 2023-25 test sweep, so its
  numbers are not independent. For reference only, at 0.60: precision 0.329 [0.171, 0.444], recall
  0.415, lift 4.82 [3.13, 6.76] (was 0.316 / 0.477 / 5.03).
- Significance (exploratory, not pre-registered): block (station) permutation p < 0.001; better than a
  month-of-year baseline by +0.093 AUC [-0.008, +0.207], one-sided p = 0.033. Within-season timing
  (station-year shift p = 0.06; June-Sept p = 0.64) was measured before the fix, not re-run.
- Training bloom rate 5.5%; validation 3.1%.
- Lab-only check S4: AUC **0.781** on 161 test rows / 15 events; at its validation t* = 0.25,
  precision 0.224, recall 0.733, lift 2.41. Too small to stand alone.

## Per-station, western five, global t=0.60 (`data/rerun2_station_specific_models.log`)
Reference only (0.60 was a test-chosen threshold).
| Station | Base rate | Precision | Recall | TP/FP/FN |
|---|---|---|---|---|
| A4 | 20.0% | 0.368 | 0.875 | 7/12/1 |
| B3 | 20.0% | 0.357 | 0.625 | 5/9/3 |
| C1 | 12.5% | 0.444 | 0.800 | 4/5/1 |
| 01 | 16.7% | 0.500 | 0.667 | 2/2/1 |
| 02 | 27.8% | 0.500 | 0.400 | 2/2/3 |

No western station and strategy clears precision > 0.50 with recall > 0.40.

## 21-day operating point
- Locked fit ≤2019, test 2023-25 station-day (`data/reference_baselines.csv`): 954 rows, 43 events,
  base 4.5%. Model at t*=0.35: precision **0.112**, POD **0.628**, FAR 0.888, lift **2.48** (before the
  fix 0.117 / 0.744 / 2.59). Against always-alert: +1.45 [0.78, 2.20], clearly better. Persistence:
  precision 0.164, POD 0.279, lift 3.65. Climatology: not tested fairly (its validation threshold
  degenerates to t=0). Keep "not clearly better than climatology".
- Walk-forward CV predictions at t*=0.35, test 2023-25 (`warning_robustness.py`): POD **0.698**
  [0.500, 0.836], precision **0.111** [0.057, 0.164], FAR 0.889, 30 TP / 240 FP / 13 FN, base 4.2%,
  lift ~2.6 (before the fix 0.791 / 0.114).
- **Open decision (unchanged):** the pre-registered POD ≥ 0.8 rule gives t*=**0.20** (test POD
  **0.837**, precision **0.071**). Deploy keeps 0.35 until the user decides.
- Pooled 21-day rolling-origin CV (`rolling_origin_cv.py --horizon 21`): AUC **0.759**, 3,653 rows /
  121 events (before the fix 0.772).

## Basin level
- Basin-day (`reference_baselines.csv`): model t=0.65, lift **1.63** (41 days, 9 events); persistence
  2.10; against always-alert +0.14 [−1.00, 1.45], not clear (before the fix 2.14). Say "a tie with
  persistence".
- Basin search **(pre-leak-fix, not re-run)**: best validation lift 2.05× at the 70.5th percentile of
  the null, inside it: the search found noise.

## Decision value, 8 visits/month (`data/decision_value.csv`) **(pre-leak-fix, not re-run)**
- LIS: calendar **17.8** [9.6, 55.0] → alert-directed top-V **9.7** [5.5, 26.6] visits per bloom;
  causal 7.8 [3.9, 40.4]; climatology **11.2** [5.7, 53.2]; share caught 0.28 → 0.51; **43** blooms
  (was 15.4 → 8.3, climatology 9.3, 0.29 → 0.54, 48 blooms).
- Narragansett unchanged: 3.81 → 1.45, climatology 1.76.

## IEC zero-shot transfer **(pre-leak-fix, not re-run)** (`data/iec_zero_shot_results.csv`, primary 2020-25 onset, 949 rows, 126 events)
- Lift **1.57** [1.41, 1.75]; AUC **0.707** [0.656, 0.760] (was 1.84 [1.59, 2.11], AUC 0.732).
- Station-month climatology: lift 1.50, AUC 0.733. It **transfers better than chance and no better
  than a calendar.** 4 of 13 stations have a lift interval above 1 (was 5 of 13). It is inside the
  pre-registered band of 1.2-1.8.
- IEC chlorophyll method: Standard Methods 10200H through 2016, both in 2017, EPA 445.0 from 2018
  on. That is before the 2020-25 window, so the transfer is unaffected.

## Class overlap and rarity (`data/lr_geometry_summary.csv`, onset rows, 21 d) **(pre-leak-fix, not re-run)**
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

## Point of no return (`data/ponr_rows.csv`) **(pre-leak-fix, not re-run)**
544 pre-onset observations / 153 events (was 617). Analogue risk peak **0.42**, median 0.02 (was 0.62 /
0.04). Summer model counterfactual (M1 nutrients) 42% of events "locked in" → **0%** once physics
can vary (was 65% → 0%). The conclusion is unchanged: no point of no return.

## Unchanged (not LIS-label dependent)
Narragansett AUC 0.839, precision 0.70, lift 2.00 [1.50, 2.68]; rolling 0.656 / 2.50; the 74-site
transfer (median lift 1.58, 67 of 74, median AUC 0.74); the NN negatives; the device work.
