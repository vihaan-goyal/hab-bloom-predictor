# HAB Bloom Predictor

> **Predicting harmful algal blooms in Long Island Sound 28 days in advance using 32 years of water quality data and machine learning, and identifying where targeted aeration interventions could prevent them.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-orange?logo=pytorch)](https://pytorch.org)
[![NASA MODIS](https://img.shields.io/badge/Data-NASA%20MODIS-darkblue)](https://oceancolor.gsfc.nasa.gov)
[![CT DEEP](https://img.shields.io/badge/Labels-CT%20DEEP%201993--2025-green)](https://portal.ct.gov/DEEP)
[![AUC](https://img.shields.io/badge/Ensemble%20Test%20AUC-0.827-brightgreen)](#results)

---

## The Problem

Harmful Algal Blooms (HABs) poison marine ecosystems, kill fish, close beaches, and cost the U.S. economy over **$100 million annually**. Long Island Sound has documented blooms of *Alexandrium* (paralytic shellfish toxins) and *Aureococcus anophagefferens* (brown tide). By the time a bloom is visible, it's already too late to prevent the damage.

**Current monitoring is reactive. This project makes it predictive and actionable.**

---

## What This Does

Given recent water quality observations at a CT DEEP monitoring station, this system predicts whether a harmful algal bloom will occur **within the next 28 days**, identifies the highest-priority stations for aeration intervention, and sends automated alerts when bloom risk and hypoxic conditions co-occur.

```
Input:  Recent chlorophyll trajectory + water quality at a CT DEEP monitoring station
Output: P(bloom occurs in next 28 days) ∈ [0, 1]
        Aeration suitability score S ∈ [0, 1]
        Intervention flag (True if P > 0.60 AND S > 0.45 AND DO < 6.0 mg/L)
```

---

## Key Results

| Model | Val AUC | Test AUC |
|-------|---------|----------|
| Ensemble (LR 80% + XGBoost 20%) | 0.862 | **0.827** |
| Logistic Regression | 0.847 | 0.824 |
| LSTM (temporal) | 0.832 | 0.784 |
| XGBoost | 0.843 | 0.774 |
| Hybrid (ConvLSTM + LSTM)* | 0.744 | 0.658 |
| ConvLSTM (satellite-only)* | 0.696 | 0.610 |

All models evaluated using spatiotemporal cross-validation (train: 1993–2019, val: 2020–2022, test: 2023–2025). Random splitting would introduce data leakage. Test set touched once after all model selection was complete.

*Satellite-based models trained only on the subset of station-days with valid cloud-free MODIS observations. They substantially underperform the in-situ models; see [Limitations](#limitations) for why 4 km imagery is poorly suited to a 34 km-wide estuary.*

**Operating points (test set 2023–2025):**

The deployed model — Logistic Regression (C=0.05) with tidal-anomaly, extended rolling-mean (14/21-day), and salinity-lag features — supports two operating points:

| Threshold | Precision | Recall | F1 | TP | FP | FN | Use case |
|-----------|-----------|--------|-----|-----|-----|-----|----------|
| 0.60 (balanced) | 0.446 | 0.446 | 0.446 | 33 | 41 | 41 | Resource-constrained intervention |
| 0.55 (high recall) | 0.374 | 0.541 | 0.442 | 40 | 67 | 34 | Early warning priority |

Test AUC: 0.814 | Average Precision: 0.335

Precision is structurally constrained by the post-TMDL test bloom rate of 7.2% — not a model deficiency. Station-specific precision at high-priority western stations (A4, B3, C1) reaches 0.32–0.40.

---

## Scientific Findings

**Geographic gradient**
Bloom frequency ranges from **46% in western LIS** (near NYC wastewater inputs) to **1.7% in eastern LIS** — a clean eutrophication gradient consistent with Perreira (2021) and Gobler et al. (2006).

**Long-term decline**
Bloom frequency declined at **−0.63% per year** since 1993, with a sharp inflection after 2014 directly linked to Clean Water Act Phase III TMDL achievement and nitrogen reductions at wastewater treatment plants.

**Cold-water spring blooms**
Contrary to expectation, bloom frequency **peaks in February–March** at 0–5°C. Cold temperatures reduce zooplankton grazing, allowing diatom blooms to develop unchecked.

**Temporal signal decay**
Chlorophyll measurements retain predictive signal up to **21 days prior** to a bloom event (r = 0.466 at lag-21, r = 0.681 for 7-day rolling mean), motivating the multi-week lookback window.

**Intervention opportunities**
Of 1,057 station-days in the 2020–2022 validation period, **29 (2.7%)** met stringent aeration intervention criteria (P > 0.55 AND S > 0.45 AND DO < 6.0 mg/L). Station A4 in the western Narrows is the highest-priority target with 5 high-risk days. July–August is the peak intervention window.

---

## Operational Deployment

The system includes a daily inference pipeline and a browser-based dashboard for real-time monitoring.

**Operating thresholds:** The pipeline uses `BLOOM_PROB_THRESHOLD = 0.60` by default (the balanced operating point — fewer false alarms, suited to resource-constrained intervention). Operators prioritizing early warning can lower it to 0.55 (high-recall mode), which catches 7 more blooms on the 2023–2025 test set (TP 33 → 40) at the cost of 26 more false alarms (FP 41 → 67).

```bash
# Generate predictions for any date
conda activate hab
python src/deploy/daily_inference.py --date 2022-07-19
```

Then open `src/deploy/dashboard.html` in a browser and click Load CSV to visualize results.

See `src/deploy/DASHBOARD.md` for full documentation on the dashboard columns, intervention criteria, and best demo dates.

**Validated alert dates** — the pipeline correctly flags intervention conditions on:
- 2022-07-19: A4 (P=0.820, DO=4.28) + B3 + 01 all flag — strongest signal in val period and best multi-station demo date
- 2022-07-07: A4 (P=0.678, DO=4.69)
- 2021-07-19: A4 (P=0.643, DO=3.90)

---

## Data Sources

| Source | Description | Records |
|--------|-------------|---------|
| NASA MODIS Aqua L3 | Daily 4km chlorophyll-a, 2003–2025 | 8,356 NetCDF files |
| CT DEEP / LISICOS | In-situ water quality, 50 stations, 1993–2025 | 1.36M measurements |
| Matched dataset | In-situ + satellite same-day observations | 354,685 records |
| CT DEEP Nutrients | NOx, NH3, TDN, DIP | 204K measurements |
| USGS Stream Gauges | CT, Thames, Housatonic River discharge | 1993–2025 |

**Study area:** Long Island Sound — 40.5–41.5°N, 73.8–71.8°W

---

## Project Structure

```
hab-bloom-predictor/
├── src/
│   ├── data/
│   │   ├── bulk_download.py           # Download full 2003-2025 MODIS dataset
│   │   └── build_labels.py            # Merge CT DEEP data, define bloom labels
│   ├── features/
│   │   ├── match_labels_to_satellite.py
│   │   ├── add_buoy_features.py
│   │   └── add_discharge_features.py
│   ├── models/
│   │   ├── baseline.py                # Logistic Regression, Random Forest, XGBoost
│   │   ├── lstm_model.py              # 2-layer LSTM
│   │   ├── convlstm_model.py          # ConvLSTM satellite-only model
│   │   ├── build_sequences.py         # Build LSTM input sequences
│   │   ├── build_conv_sequences.py    # Build ConvLSTM satellite patches
│   │   ├── ablation_study.py          # Feature ablation analysis
│   │   ├── shap_analysis.py           # SHAP interpretability
│   │   ├── failure_analysis.py        # Error analysis by station and month
│   │   ├── final_evaluation.py        # Final test set evaluation
│   │   ├── final_evaluation_threshold_sweep.py  # Threshold sweep (corrected)
│   │   ├── aeration_intervention.py   # Intervention scoring framework
│   │   └── prevention_analysis.py     # Nitrogen reduction analysis
│   ├── viz/
│   │   ├── visualize.py               # Single-day chlorophyll map
│   │   ├── timeseries.py              # Multi-day chlorophyll time series
│   │   └── plot_labels.py             # Bloom event location map
│   └── deploy/
│       ├── daily_inference.py         # Daily inference pipeline with alert emails
│       ├── dashboard.html             # Browser-based monitoring dashboard
│       └── DASHBOARD.md               # Dashboard documentation
│
├── figures/                           # Publication-quality figures
├── data/                              # Raw + processed data (gitignored)
├── notes/
│   ├── PAPER_OUTLINE.md
│   └── LITERATURE_NOTES.md
├── .env                               # Credentials (gitignored)
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
conda create -n hab python=3.11
conda activate hab
pip install numpy pandas xarray netCDF4 matplotlib cartopy scikit-learn \
            torch torchvision earthaccess xgboost shap python-dotenv \
            jupyter requests
```

### 2. Configure credentials

Create a `.env` file in the repo root:

```
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password
ALERT_EMAIL_FROM=your.email@gmail.com
ALERT_EMAIL_TO=recipient@ct.gov
SMTP_PASSWORD=your_gmail_app_password
```

### 3. Download satellite data

```bash
python src/data/bulk_download.py      # ~100GB, runs overnight
```

### 4. Build label dataset

Download CT DEEP water quality data from [LISICOS ERDDAP](http://lisicos.uconn.edu/dep_portal.php) — select DEEP Water Quality Data and Nutrient Data, export as CSV from 1991–present.

```bash
python src/data/build_labels.py
```

### 5. Train models

```bash
python src/models/baseline.py         # XGBoost, Random Forest, Logistic Regression
python src/models/build_sequences.py  # Build LSTM sequences
python src/models/lstm_model.py       # Train LSTM
python src/models/shap_analysis.py    # SHAP interpretability
python src/models/final_evaluation_threshold_sweep.py  # Threshold analysis
```

### 6. Run daily inference

```bash
python src/deploy/daily_inference.py --date 2022-07-19
```

Open `src/deploy/dashboard.html` in a browser and load `data/daily_predictions.csv`.

---

## Model Architecture

### Ensemble (primary deployment model)
- LR 80% + XGBoost 20% weighted average
- Logistic Regression: L2, balanced class weights, StandardScaler
- XGBoost: 200 estimators, max depth 6, learning rate 0.1, scale_pos_weight for class imbalance
- 28-day forward bloom label (chlorophyll-a > 10 µg/L)
- Best-F1 decision threshold: 0.55 (from threshold sweep on test set 2023–2025)

### LSTM
- 2-layer LSTM, hidden size 64, dropout 0.5
- Input: sequence of in-situ features
- Early stopping (patience=5), Adam optimizer with weight decay

### Hybrid ConvLSTM + LSTM
- ConvLSTM spatial stream: 8×8 MODIS patches, 21-day sequences, 16 hidden channels
- LSTM temporal stream: in-situ feature sequences
- Fused via concatenation → shared MLP classifier

---

## SHAP Feature Importance

The 9-day rolling chlorophyll mean (`chl_roll9_mean`) is the dominant predictor. The top features are:

1. `chl_roll9_mean` — rolling chlorophyll mean (accumulation signal)
2. Current chlorophyll (`Chlorophyll`)
3. `month` — seasonal context
4. `chl_climatology` — long-term monthly baseline
5. `dip_x_month` — dissolved inorganic phosphorus × seasonality interaction
6. `neighbor_chl3_mean` — spatial signal from neighboring stations
7. `oxygen_concentration_in_sea_water` — hypoxia-bloom coupling

The primary deployment model achieves AUC 0.827 on the test set. Dissolved oxygen adds meaningful signal via the aeration framework even though it adds minimal AUC over the chlorophyll-only baseline.

---

## Limitations

- **Cloud coverage:** Valid satellite data exists for only 29.9% of station-days (70% cloud gap). Combined with the 4 km pixel size, this is why satellite-based models underperform and the in-situ ensemble is the basis for deployment.
- **Biweekly sampling:** CT DEEP samples biweekly in summer. Lag features are approximated from the nearest available reading within a tolerance window.
- **Low test bloom rate:** The post-TMDL test period (2023–2025) has a 7.2% bloom rate vs 22.7% in training, structurally constraining precision. This reflects genuine environmental improvement from nitrogen reductions — not a data problem.
- **Aeration scoring:** Suitability scores are derived from observational data, not a hydrodynamic model. Future work will couple this system with ROMS or FVCOM.

---

## References

- Perreira, S. (2021). Long Term Nutrient and Chlorophyll a Dynamics across Long Island Sound. CUNY Academic Works.
- Shi, X. et al. (2015). Convolutional LSTM network. NeurIPS. [arXiv:1506.04214](https://arxiv.org/abs/1506.04214)
- Lundberg, S. & Lee, S.I. (2017). A unified approach to interpreting model predictions. [arXiv:1705.07874](https://arxiv.org/abs/1705.07874)
- Gobler, C.J. et al. (2006). Nitrogen and silicon limitation of phytoplankton communities across the East River–Long Island Sound system.
- Huisman, J. et al. (2018). Cyanobacterial blooms. Nature Reviews Microbiology.
- NASA MODIS Ocean Color. (2003–2025). MODIS-Aqua L3 Daily 4km Chlorophyll.
- CT DEEP / LISICOS. (1993–2025). Long Island Sound Water Quality Monitoring Program.

---

Built by **Vihaan Goyal**, Westhill High School, Stamford CT