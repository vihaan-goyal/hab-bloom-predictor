# KEY_NUMBERS.md — HAB Bloom Predictor Reference

Corrected pipeline. Do NOT use numbers from the OLD docs listed in Section 6.
Last updated: 2026-05-28

---

## Section 1 — Model Performance (corrected)

| Model | Val AUC | Test AUC | Notes |
|---|---|---|---|
| Ensemble (LR 80% + XGB 20%) | **0.862** | **0.827** | Primary reported result |
| Logistic Regression | 0.847 | 0.824 | Strong linear baseline |
| XGBoost (baselines_corrected.py) | 0.843 | 0.774 | lr=0.03, depth=3 |
| XGBoost (shap_corrected.py) | 0.850 | 0.774 | lr=0.1, depth=6; used for SHAP only |
| LSTM | 0.832 | 0.784 | Confirmed ~0.829/0.802 on latest run |
| Random Forest | ~0.783 | ~0.794 | Used for feature importances (fig7) |

**Temporal split:** Train 1993–2019 | Val 2020–2022 | Test 2023–2025

**Bloom rates:** train 22.7% | val ~6–7% | test 7.2%

**Precision (test set):**
- Global threshold: 0.17–0.29
- Station-specific models: 0.32–0.40

**Prediction horizon:** 28 days (forward calendar window from observation date)

**Top SHAP features (XGBoost):**
chl_roll9_mean, Chlorophyll, month, chl_climatology, chl_roll3_mean,
chl_roll6_mean, dip_x_month, neighbor_chl3_mean, dissolved_oxygen

---

## Section 2 — Dataset (corrected)

| Item | Value |
|---|---|
| Total station-days | **11,447** |
| Train rows (1993–2019) | 9,356 |
| Val rows (2020–2022) | 1,057 |
| Test rows (2023–2025) | 1,034 |
| Stations | ~50 CT DEEP LISICOS stations |
| Key file | data/hab_features_daily.csv |

**How we got here:** Raw CT DEEP depth profiles had 120–200 rows per station
visit (one row per depth). `aggregate_daily.py` reduced this to one row
per station-date. The old pipeline never aggregated, producing a spurious
1.36 M-row dataset with inflated correlations.

---

## Section 3 — Exploratory Findings (corrected)

### Lag correlation decay (fig6): CHL(t-lag) vs bloom_28d(t)

| Lag (days) | Pearson r | p-value | n |
|---|---|---|---|
| 0 | **0.306** | 2.3e-247 | 11,447 |
| 3 | 0.190 | 6.3e-92 | 11,297 |
| 7 | 0.184 | 2.4e-85 | 11,097 |
| 14 | 0.160 | 8.9e-63 | 10,755 |
| 21 | 0.138 | 2.1e-45 | 10,426 |
| 28 | 0.125 | 1.5e-36 | 10,098 |
| 35 | 0.091 | 1.5e-19 | 9,776 |
| 42 | 0.132 | 7.9e-38 | 9,460 |

Signal is present but modest (r~0.19–0.31), consistent with the biweekly
sampling interval and ecological lag structure.

---

## Section 4 — Aeration Intervention (corrected, from Task 3+4 output)

**Period:** 2020–2022 (validation window)
**High-risk criterion:** Aeration score S > 0.45 AND DO < 6.0 mg/L
**Aeration formula:** S = 0.45×(14–DO)/12 + 0.30×(T–10)/20 + 0.25×p

### Summary (model-based, daily_inference.py)

| Metric | Value |
|---|---|
| Total station-days | 1,057 |
| High-risk station-days | **313 (29.6%)** |
| Top month by mean aeration score | Aug (0.574) |

### Top 10 stations by high-risk days (model probabilities)

| Station | High-Risk Days |
|---|---|
| A4 | 18 |
| D3 | 17 |
| E1 | 15 |
| C2 | 15 |
| 03 | 14 |
| B3 | 14 |
| C1 | 14 |
| H6 | 12 |
| F2 | 11 |
| 05 | 11 |

### Top 5 months by mean aeration score

| Month | Mean S |
|---|---|
| Aug | 0.574 |
| Sep | 0.563 |
| Jul | 0.518 |
| Oct | 0.397 |
| Jun | 0.377 |

### Specific historical inference — Station A4

| Date | Bloom Prob | DO (mg/L) | Temp (°C) | Aeration S | High Risk? |
|---|---|---|---|---|---|
| 2022-09-01 | 0.229 | 3.81 | 23.8 | 0.647 | YES |
| 2022-08-17 | 0.501 | 4.59 | 22.8 | 0.670 | YES |
| 2021-08-31 | 0.447 | 3.77 | 23.4 | 0.696 | YES |
| 2017-08-15 | 0.602 | 2.24 | 21.8 | 0.768 | YES |

### Per-station summary (generate_aeration_figures.py, bloom_28d proxy)

300 high-risk days (28.4%) — note: slightly lower than model-based 313/29.6%
because bloom_28d (0/1) replaces continuous model probability.
Highest-priority station: **A4** — 17 days, min DO = 2.68 mg/L

### Seasonal pattern (bloom_28d proxy, fig11)

High-risk days concentrated in **Jul–Sep**: Jul 65, Aug 148, Sep 87 (= 300 total).
Zero high-risk days outside Jun–Sep.

---

## Section 5 — Numbers that did NOT change

These findings came from the EDA and are unaffected by the bloom-label or
aggregation corrections:

- **Spatial gradient:** western stations (A4, C2, B3) have consistently
  higher bloom rates than eastern stations (M3, N3), consistent with
  nutrient loading from the Connecticut and Housatonic rivers.

- **Long-term trend (fig3):** bloom frequency shows a weak declining trend
  (~−0.1–0.2 %/yr) across 1993–2025, with a visible inflection after ~2014.

- **TMDL inflection (fig3):** visible step-change in annual bloom frequency
  near 2014, coinciding with the Long Island Sound TMDL nitrogen reductions.

- **Seasonal peak:** bloom probability peaks in Aug–Sep (confirmed in both
  old and corrected pipelines).

- **Temperature relationship (fig5):** blooms strongly associated with
  temperatures > 20°C, consistent with Alexandrium catenella ecology.

---

## Section 6 — Numbers that are WRONG in old docs — DO NOT USE

These appear in pre-correction scripts, old README sections, or old figures.
They must not be cited.

| Wrong number | Why it is wrong |
|---|---|
| **Test AUC 0.936** | From old pipeline with un-aggregated depth profiles; each cast counted as many rows, leaking same-visit CHL into both features and label |
| **1.36 M rows** | The raw CT DEEP data before `aggregate_daily.py`; not a valid modeling dataset |
| **7-day forecast horizon** | Stated horizon was 7d but biweekly sampling gives median gap ~21d, making the effective horizon 21–28d |
| **r = 0.707 lag correlation** | Computed on unaggregated data (multiple depth rows per visit inflated n and correlation); corrected value is r = 0.306 at lag = 0 |
| **27,412 high-risk predictions** | From old aeration_intervention.py using `hab_features_final.csv` (non-aggregated) and 7-day bloom label |
| **975 stringent candidates** | Same source as above; artifact of inflated dataset size and wrong label |
