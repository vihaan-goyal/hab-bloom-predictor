# HAB Early Warning Dashboard

**Spatiotemporal Prediction and Targeted Intervention for Harmful Algal Blooms in Long Island Sound**
Vihaan Goyal · Westhill High School · Stamford, Connecticut

---

## What this system does

Once the ensemble model predicts a bloom is likely at a monitoring station, the dashboard shows three things simultaneously:

1. **How likely** is a bloom in the next 28 days at each station (bloom probability)
2. **How suitable** is that station for aeration intervention right now (aeration score)
3. **Whether all three intervention criteria are met** (the Intervene flag)

---

## Running it

**Step 1 — Generate predictions for a date:**
```bash
conda activate hab
python src/deploy/daily_inference.py --date 2022-07-19
```

This writes results to `data/daily_predictions.csv`.

**Step 2 — Open the dashboard:**

Double-click `dashboard.html` — it opens in your browser. No server needed.

**Step 3 — Load the predictions:**

Click **Load CSV** in the top right and select `data/daily_predictions.csv`.

---

## What each column means

### P(bloom) — Bloom probability
The Logistic Regression model output (C=0.05, balanced). The probability that a harmful algal bloom (chlorophyll-a > 10 µg/L) will occur at this station within the next **28 days**.

Computed from recent sensor history using these features:
- `chl_roll7/14/21_mean` — rolling chlorophyll means (accumulation signal)
- `chl_anomaly` — deviation from the long-term monthly climatology
- `chl_lag1/2/3/4` — chlorophyll readings at lag offsets
- `tidal_gt_anom`, `tidal_msl_anom` — NOAA CO-OPS tidal anomaly features
- `sal_lag2/3/4` — salinity trajectory lags
- `percent_saturation` — CT DEEP WQP surface oxygen saturation
- `max_gust_3d` — 3-day maximum wind gust speed (NOAA ASOS, 3 CT stations)
- `dissolved_oxygen`, `temperature`, `salinity`
- `dip_x_month` — dissolved inorganic phosphorus interaction with seasonality
- `neighbor_chl3_mean` — spatial chlorophyll signal from neighboring stations
- `latitude`, `longitude`, `month`

**Thresholds used in the dashboard:**
| Color | Meaning | Threshold |
|-------|---------|-----------|
| Red | High risk (Intervene) | P > 60% (balanced) or P > 55% (high recall) |
| Amber | Elevated risk (Monitor) | P > 40% |
| Green | Low risk | P ≤ 40% |

**Two operating modes.** The high-risk cutoff has two recommended settings:
- **Balanced (P > 60%)** — the default `daily_inference.py` threshold. Minimizes false alarms; use when intervention resources are constrained. Test set: precision 0.500, recall 0.486, F1 0.493 (TP=36, FP=36, FN=38).
- **High recall (P > 55%)** — lowers the bar to catch more blooms; use when early warning is the priority and more false alarms are acceptable. Test set: precision 0.377, recall 0.541, F1 0.444 (catches 4 more blooms, 30 more false alarms than balanced; TP=40, FP=66, FN=34).

---

### Aeration S — Aeration suitability score
A composite score that asks: *if we deployed aeration equipment here right now, how effective and urgent would it be?*

$$S = 0.45 \cdot \frac{14 - \text{DO}}{12} + 0.30 \cdot \frac{T - 10}{20} + 0.25 \cdot p$$

Where:
- **DO term** — lower dissolved oxygen = higher score. Aeration is most needed when the water is already hypoxic. Normalized so DO=2 mg/L → 1.0, DO=14 mg/L → 0.0
- **Temperature term** — warmer water = higher score. Blooms grow faster in warm conditions and thermal stratification (which drives hypoxia) is stronger. Normalized over 10–30°C
- **p term** — bloom probability. Sites with higher predicted bloom risk get higher aeration priority

S ranges from 0 to 1. Higher = more suitable for intervention.

---

### DO mg/L — Dissolved oxygen
Dissolved oxygen in milligrams per liter, measured at the surface.

**Key thresholds:**
- **< 2.0 mg/L** — Severe hypoxia. Fish kills imminent
- **< 6.0 mg/L** — Hypoxia threshold used in intervention criteria. Shellfish and fish are stressed
- **6–8 mg/L** — Sub-optimal but not immediately harmful
- **> 8 mg/L** — Healthy, well-oxygenated water

DO is highlighted red in the table when it falls below 6.0 mg/L.

---

### Temp °C — Water temperature
Surface water temperature in Celsius. Used in the aeration score calculation. Warmer temperatures increase bloom risk and deepen the thermocline, worsening stratification and hypoxia.

---

## The intervention decision

The **Intervene** badge requires all three conditions to be met simultaneously:

| Criterion | Balanced mode | High-recall mode | Rationale |
|------------|---------------|------------------|-----------|
| P(bloom) | > 60% | > 55% | Bloom-probability cutoff (threshold sweep on test set 2023–2025) |
| DO | < 6.0 mg/L | < 6.0 mg/L | Water is already hypoxic — aeration addresses a real oxygen deficit |
| Aeration S | > 0.45 | > 0.45 | Site conditions make aeration worthwhile |

**Balanced mode (P > 60%)** is the `daily_inference.py` default — it prioritizes precision (fewer false alarms) for resource-constrained intervention. **High-recall mode (P > 55%)** catches more blooms for early-warning priority, accepting more false alarms. Only the P(bloom) cutoff changes between modes; the DO and aeration-score gates are identical.

**Why all three?**

A station can have high bloom probability but healthy DO. In that case, the water is nutrient-rich and bloom-prone, but aeration is not the right tool — the oxygen is fine. The model flags it as **Monitor**, not **Intervene**.

Conversely, a station can have low DO but low bloom probability — perhaps it's hypoxic due to sediment oxygen demand rather than algal respiration. Aeration might help the oxygen but isn't targeting a bloom.

The three-condition gate ensures aeration is recommended only when:
- A bloom is genuinely predicted (model criterion)
- The oxygen deficit justifies the intervention (physical criterion)
- The combination of conditions makes aeration effective (composite criterion)

---

## Key dates for demonstration

These historical dates produce intervention alerts on the corrected pipeline:

```bash
python src/deploy/daily_inference.py --date 2022-07-19   # A4 (P=0.813) + B3 + 01 all flag
python src/deploy/daily_inference.py --date 2022-07-07   # A4 (P=0.678) flags
python src/deploy/daily_inference.py --date 2021-07-19   # A4 (P=0.643) flags
```

**2022-07-19 is the best demo date** — three stations flag simultaneously (A4, B3, 01), with A4 the strongest at P=0.813, DO=4.28 mg/L, S=0.722. This demonstrates the spatial clustering of western LIS bloom risk; the system would have sent an alert to CT DEEP weeks before conditions peaked, giving time to stage aeration equipment.

---

## Station coverage

| Always processed | Occasionally skipped | Never in dataset |
|---|---|---|
| A4, B3, C1, C2, D3, E1, F2, F3, H2, H4, H6, I2, J2, K2, M3 | A2, N3, J4 (sparse surface sampling) | — |
| 01–30 (numeric stations, western Sound) | 31–36 (far eastern stations, sparse data) | — |

Stations with no data within 14 days of the target date are skipped automatically.

The numeric stations (01–30) are clustered in the western Sound near the New York border — exactly where the west-to-east eutrophication gradient is steepest and bloom frequency is highest.

---

## Files

| File | Description |
|---|---|
| `src/deploy/daily_inference.py` | Runs predictions for a given date, writes `data/daily_predictions.csv` |
| `src/deploy/dashboard.html` | Browser-based visualization, loads the CSV |
| `data/hab_features_tidal.csv` | Full historical feature dataset (1993–2025, 11,447 station-days, primary data file) |
| `data/daily_predictions.csv` | Output of most recent inference run |
| `data/threshold_sweep_results.csv` | Precision/recall/F1 at all thresholds (test set 2023–2025) |