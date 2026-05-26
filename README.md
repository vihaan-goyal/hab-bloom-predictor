# HAB Bloom Predictor

> **Predicting harmful algal blooms in Long Island Sound 7 days in advance using 22 years of NASA satellite data and machine learning and identifying where targeted aeration interventions could prevent them.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-orange?logo=pytorch)](https://pytorch.org)
[![NASA MODIS](https://img.shields.io/badge/Data-NASA%20MODIS-darkblue)](https://oceancolor.gsfc.nasa.gov)
[![CT DEEP](https://img.shields.io/badge/Labels-CT%20DEEP%201993--2025-green)](https://portal.ct.gov/DEEP)
[![AUC](https://img.shields.io/badge/Test%20AUC-0.936-brightgreen)](#results)

---

## The Problem

Harmful Algal Blooms (HABs) poison marine ecosystems, kill fish, close beaches, and cost the U.S. economy over **$100 million annually**. Long Island Sound has documented blooms of *Alexandrium* (paralytic shellfish toxins) and *Aureococcus anophagefferens* (brown tide). By the time a bloom is visible, it's already too late to prevent the damage.

**Current monitoring is reactive. This project makes it predictive and actionable.**

---

## What This Does

Given 21 days of water quality observations at a monitoring station, this system predicts whether a harmful algal bloom will occur **7 days in the future**, identifies the highest-priority stations for aeration intervention, and sends automated alerts when bloom risk and hypoxic conditions co-occur.

```
Input:  21 days of chlorophyll trajectory at a CT DEEP monitoring station
Output: P(bloom occurs in next 7 days) ∈ [0, 1]
        Aeration suitability score S ∈ [0, 1]
        Intervention flag (True if P > 0.70 AND S > 0.60 AND DO < 6.0 mg/L)
```

---

## Key Results

| Model | Val AUC | Test AUC |
|-------|---------|----------|
| XGBoost | 0.928 | **0.936** |
| LSTM (temporal) | 0.926 | — |
| Logistic Regression | 0.916 | — |
| Random Forest | 0.915 | — |
| Hybrid (ConvLSTM + LSTM)* | 0.744 | 0.658 |
| ConvLSTM (satellite-only)* | 0.696 | 0.610 |

All models evaluated using spatiotemporal cross-validation (train: 1993–2019, val: 2020–2022, test: 2023–2025). Random splitting would introduce data leakage.

*Satellite-based models were trained only on the subset of station-days with valid cloud-free MODIS observations. They substantially underperform the in-situ models; see [Limitations](#limitations) for why 4 km imagery is poorly suited to a 34 km-wide estuary.*

**XGBoost test set performance (2023–2025):** AUC 0.936 · Avg Precision 0.789 · Bloom recall 81% · Bloom precision 66%

---

## Scientific Findings

**Geographic gradient**
Bloom frequency ranges from **46% in western LIS** (near NYC wastewater inputs) to **1.7% in eastern LIS** a clean eutrophication gradient consistent with Perreira (2021) and Gobler et al. (2006).

**Long-term decline**
Bloom frequency declined at **−0.63% per year** since 1993, with a sharp inflection after 2014 directly linked to Clean Water Act Phase III TMDL achievement and nitrogen reductions at wastewater treatment plants.

**Cold-water spring blooms**
Contrary to expectation, bloom frequency **peaks in February–March** at 0–5°C. Cold temperatures reduce zooplankton grazing, allowing diatom blooms to develop unchecked.

**Temporal signal decay**
Chlorophyll measurements retain predictive signal up to **21 days prior** to a bloom event (r = 0.466 at lag-21, r = 0.681 for 7-day rolling mean), motivating the 21-day lookback window.

**Intervention opportunities**
Of 27,412 high-risk bloom predictions in 2020–2022, **975 (3.6%)** met stringent aeration intervention criteria (P > 0.70 AND S > 0.60 AND DO < 6.0 mg/L). Station A4 in the western Narrows is the highest-priority target, with dissolved oxygen as low as **1.39 mg/L** during predicted bloom events. August is the peak intervention window.

---

## Operational Deployment

The system includes a daily inference pipeline and a browser-based dashboard for real-time monitoring.

```bash
# Generate predictions for any date
conda activate hab
python src/deploy/daily_inference.py --date 2022-09-01
```

Then open `src/deploy/dashboard.html` in a browser and click Load CSV to visualize results.

See `src/deploy/DASHBOARD.md` for full documentation on the dashboard columns, intervention criteria, and best demo dates.

**Validated alert dates** — the pipeline correctly flags intervention conditions on:
- 2022-09-01: A4 (P=0.970, DO=5.76) + Station 16 (P=0.746, DO=5.99)
- 2022-08-17: A4 (P=0.886, DO=5.89)
- 2021-08-31: A4 (P=0.882, DO=5.88)
- 2017-08-15: A4 (P=0.749, DO=4.75)

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
├── INSTRUCTIONS.md
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
```

### 6. Run daily inference

```bash
python src/deploy/daily_inference.py --date 2022-09-01
```

Open `src/deploy/dashboard.html` in a browser and load `data/daily_predictions.csv`.

---

## Model Architecture

### XGBoost (primary deployment model)
- 200 estimators, max depth 6, learning rate 0.1
- `scale_pos_weight` for class imbalance (19.4% positive rate)
- 11 features: lagged chlorophyll at 3/7/14/21 days, 7-day rolling mean/std, climatological anomaly and baseline, latitude, longitude, month

### LSTM
- 2-layer LSTM, hidden size 64, dropout 0.5
- Input: 21-day sequence of 15 features
- Early stopping (patience=5), Adam optimizer with weight decay

### Hybrid ConvLSTM + LSTM
- ConvLSTM spatial stream: 8×8 MODIS patches, 21-day sequences, 16 hidden channels
- LSTM temporal stream: 21-day in-situ feature sequences
- Fused via concatenation → shared MLP classifier

---

## SHAP Feature Importance

The 7-day rolling chlorophyll mean (`chl_roll7_mean`) is the dominant predictor, nearly twice as important as the next feature. This validates the core hypothesis: **the trajectory of chlorophyll buildup over the preceding week is the strongest signal of an impending bloom.**

The primary deployment model uses only chlorophyll trajectory features and achieves AUC 0.936, confirming that dissolved oxygen and temperature add negligible predictive power (ΔAUC < 0.005) over the chlorophyll-only baseline.

---

## Limitations

- **Cloud coverage:** Valid satellite data exists for only 29.9% of station-days (70% cloud gap). The loss is more severe inside the 21-day patch sequences used by the deep learning models — roughly 60% of daily timesteps and 89% of individual patch pixels are cloud-obscured. Combined with the 4 km pixel size (a large fraction of the Sound's 34 km width), this is why the satellite-based models perform near chance on held-out years and the in-situ XGBoost model is the basis for deployment. Cloud gaps are also non-random: cloudy conditions correlate with the calm, stratified water that precedes blooms.
- **Biweekly sampling:** CT DEEP samples biweekly in summer. Lag features at 3 and 7 days are approximated from the nearest available reading within a 7-day tolerance window.
- **Aeration scoring:** Suitability scores are derived from observational data, not a hydrodynamic model. Future work will couple this system with ROMS or FVCOM.
- **Future satellite work:** Higher-resolution ocean color sensors — VIIRS (750 m) or Sentinel-3 OLCI (300 m) — may narrow the spatial-resolution gap that limits the MODIS-based models here.

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

Built by **Vihaan Goyal & Lev Rubin**, Westhill High School, Stamford CT