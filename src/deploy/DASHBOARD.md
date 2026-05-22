# HAB Early Warning Dashboard

**Spatiotemporal Prediction and Targeted Intervention for Harmful Algal Blooms in Long Island Sound**
Vihaan Goyal · Westhill High School · Stamford, Connecticut

---

## What this system does

Once the XGBoost model predicts a bloom is likely at a monitoring station, the dashboard shows three things simultaneously:

1. **How likely** is a bloom in the next 7 days at each station (bloom probability)
2. **How suitable** is that station for aeration intervention right now (aeration score)
3. **Whether all three intervention criteria are met** (the Intervene flag)

---

## Running it

**Step 1 — Generate predictions for a date:**
```bash
conda activate hab
python daily_inference.py --date 2022-09-01
```

This writes results to `data/daily_predictions.csv`.

**Step 2 — Open the dashboard:**

Double-click `dashboard.html` — it opens in your browser. No server needed.

**Step 3 — Load the predictions:**

Click **Load CSV** in the top right and select `data/daily_predictions.csv`.

---

## What each column means

### P(bloom) — Bloom probability
The XGBoost model's core output. The probability that a harmful algal bloom (chlorophyll-a > 10 µg/L) will occur at this station within the next **7 days**.

Computed from 21 days of sensor history using these features:
- `chl_roll7_mean` — 7-day rolling chlorophyll mean (dominant predictor)
- `chl_anomaly` — deviation from the long-term monthly climatology
- `chl_lag3/7/14/21` — chlorophyll readings at lag offsets
- `dissolved_oxygen`, `temperature`, `salinity`, `pH`
- `latitude`, `longitude`, `month`

**Thresholds used in the dashboard:**
| Color | Meaning | Threshold |
|---|---|---|
| Red | High risk | P > 70% |
| Amber | Elevated risk | P > 50% |
| Green | Low risk | P ≤ 50% |

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
Dissolved oxygen in milligrams per liter, measured at the surface (depth_code = 'S').

**Key thresholds:**
- **< 2.0 mg/L** — Severe hypoxia. Fish kills imminent
- **< 6.0 mg/L** — Hypoxia threshold used in intervention criteria. Shellfish and fish are stressed
- **6–8 mg/L** — Sub-optimal but not immediately harmful
- **> 8 mg/L** — Healthy, well-oxygenated water

DO is highlighted red in the table when it falls below 6.0 mg/L.

---

### Temp °C — Water temperature
Surface water temperature in Celsius. Used in the aeration score calculation. Warmer temperatures increase bloom risk (for summer species) and deepen the thermocline, which worsens stratification and hypoxia.

---

## The intervention decision

The **Intervene** badge requires all three conditions to be met simultaneously:

| Criterion | Threshold | Rationale |
|---|---|---|
| P(bloom) | > 70% | Model is confident a bloom is imminent |
| DO | < 6.0 mg/L | Water is already hypoxic — aeration addresses a real oxygen deficit |
| Aeration S | > 0.45 | Site conditions make aeration worthwhile |

**Why all three?**

A station can have very high bloom probability but healthy DO (e.g., B3 at 96% probability but DO = 6.45 mg/L on 2022-09-01). In that case, the water is nutrient-rich and bloom-prone, but aeration is not the right tool — the oxygen is fine. The model flags it as **Monitor**, not **Intervene**.

Conversely, a station can have low DO but low bloom probability — perhaps it's hypoxic due to sediment oxygen demand rather than algal respiration. Aeration might help the oxygen but isn't targeting a bloom.

The three-condition gate ensures aeration is recommended only when:
- A bloom is genuinely predicted (model criterion)
- The oxygen deficit justifies the intervention (physical criterion)
- The combination of conditions makes aeration effective (composite criterion)

---

## Key dates for demonstration

These historical dates produce intervention alerts:

```bash
python daily_inference.py --date 2022-09-01   # A4 + Station 16 flagged
python daily_inference.py --date 2022-08-17   # A4 flagged
python daily_inference.py --date 2021-08-31   # A4 flagged
python daily_inference.py --date 2017-08-15   # A4 flagged (DO = 4.75 mg/L)
```

**2022-09-01 is the best demo date** — A4 shows P=0.970, DO=5.76, S=0.767, and station 16 co-triggers. This means the system would have sent an alert to CT DEEP on August 25, 2022 — a full week before the bloom peaked — giving time to stage aeration equipment at the western Narrows.

---

## Station coverage

| Always processed | Occasionally skipped | Never in dataset |
|---|---|---|
| A4, B3, C1, C2, D3, E1, F2, F3, H2, H4, H6, I2, J2, K2, M3 | A2, N3, J4 (sparse surface sampling) | L1 (not in hab_features_final.csv) |
| 01–30 (numeric stations, western Sound) | 31–36 (far eastern stations, sparse data) | — |

The numeric stations (01–30) are clustered in the western Sound near the New York border — exactly where the west-to-east eutrophication gradient is steepest and bloom frequency is highest (up to 46% at the westernmost stations).

---

## Files

| File | Description |
|---|---|
| `daily_inference.py` | Runs predictions for a given date, writes `data/daily_predictions.csv` |
| `dashboard.html` | Browser-based visualization, loads the CSV |
| `data/xgb_model.json` | Trained XGBoost model (AUC 0.936 on 2023–2025 test set) |
| `data/chl_climatology.csv` | Monthly mean chlorophyll per station (used for anomaly feature) |
| `data/daily_predictions.csv` | Output of most recent inference run |
| `data/hab_features_final.csv` | Full historical feature dataset (1993–2025) |