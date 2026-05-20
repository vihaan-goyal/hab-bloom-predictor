# 🌊 HAB Bloom Predictor

> **Predicting harmful algal blooms in Long Island Sound 7 days in advance using 22 years of NASA satellite data and machine learning.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-orange?logo=pytorch)](https://pytorch.org)
[![NASA MODIS](https://img.shields.io/badge/Data-NASA%20MODIS-darkblue)](https://oceancolor.gsfc.nasa.gov)
[![CT DEEP](https://img.shields.io/badge/Labels-CT%20DEEP%201993--2025-green)](https://portal.ct.gov/DEEP)
[![AUC](https://img.shields.io/badge/Best%20AUC-0.928-brightgreen)](#results)

---

## The Problem

Harmful Algal Blooms (HABs) poison marine ecosystems, kill fish, close beaches, and cost the U.S. economy over **$100 million annually**. Long Island Sound has documented blooms of *Alexandrium* (paralytic shellfish toxins) and *Aureococcus anophagefferens* (brown tide). By the time a bloom is visible, it's already too late to prevent the damage.

**Current monitoring is reactive. This project makes it predictive.**

---

## What This Does

Given 21 days of water quality observations at a monitoring station, this system predicts whether a harmful algal bloom will occur **7 days in the future** — giving agencies like CT DEEP and shellfish harvesters actionable advance warning.

```
Input:  21 days of [chlorophyll, temperature, salinity, oxygen, pH, ...]
Output: P(bloom occurs in next 7 days) ∈ [0, 1]
```

---

## Key Results

| Model | AUC-ROC | Avg Precision |
|-------|---------|---------------|
| XGBoost (baseline) | **0.928** | 0.726 |
| LSTM (temporal) | 0.926 | 0.703 |
| Logistic Regression | 0.922 | 0.712 |
| Random Forest | 0.917 | 0.706 |

All models evaluated on **held-out 2023–2025 data** using spatiotemporal cross-validation (train: 1993–2019, val: 2020–2022, test: 2023–2025). Random splitting would be data leakage — a bloom in 2015 and a bloom in 2016 at nearby stations are not independent.

---

## Scientific Findings

Through exploratory analysis of 1.36 million chlorophyll measurements across 50 CT DEEP monitoring stations (1993–2025), this project identified:

**🗺️ Geographic gradient**
Bloom frequency ranges from **46% in western LIS** (near NYC wastewater inputs) to **1.7% in eastern LIS** — a clean eutrophication gradient consistent with Perreira (2021) and Gobler et al. (2006).

**📉 Long-term decline**
Bloom frequency declined at **−0.63% per year** since 1993, with a sharp inflection after 2014 — directly linked to Clean Water Act Phase III TMDL achievement and nitrogen reductions at wastewater treatment plants.

**❄️ Cold-water spring blooms**
Contrary to expectation, bloom frequency **peaks in February–March** at 0–5°C water temperatures. Cold temperatures reduce zooplankton grazing, allowing diatom blooms to develop unchecked before summer dinoflagellate succession.

**⏱️ Temporal signal decay**
Chlorophyll measurements retain predictive signal up to **21 days prior** to a bloom event (r = 0.466 at lag-21), motivating the LSTM's 21-day lookback window.

---

## Data Sources

| Source | Description | Records |
|--------|-------------|---------|
| [NASA MODIS Aqua L3](https://oceancolor.gsfc.nasa.gov) | Daily 4km chlorophyll-a, 2003–2025 | 7,500+ NetCDF files |
| [CT DEEP / LISICOS](http://lisicos.uconn.edu/dep_portal.php) | In-situ water quality, 50 stations, 1993–2025 | 1.36M measurements |
| [CT DEEP Nutrients](http://lisicos.uconn.edu) | Nitrogen (NOx, NH3, TDN), phosphorus (DIP) | 204K measurements |

**Study area:** Long Island Sound bounding box — 40.5–41.5°N, 73.8–71.8°W

---

## Project Structure

```
hab-bloom-predictor/
│
├── src/
│   ├── data/
│   │   ├── download_modis.py          # Download single MODIS file (test)
│   │   ├── bulk_download.py           # Download full 2003-2025 dataset
│   │   └── build_labels.py            # Merge CT DEEP data, define bloom labels
│   ├── features/
│   │   └── match_labels_to_satellite.py  # Join in-situ labels to satellite pixels
│   ├── models/
│   │   ├── baseline.py                # Logistic Regression, Random Forest, XGBoost
│   │   ├── build_sequences.py         # Reshape data into (samples, 21, features)
│   │   ├── lstm_model.py              # 2-layer LSTM with early stopping
│   │   └── shap_analysis.py           # SHAP interpretability for XGBoost
│   └── viz/
│       ├── visualize.py               # Single-day chlorophyll map
│       ├── timeseries.py              # Multi-day mean chlorophyll time series
│       └── plot_labels.py             # Bloom event location map
│
├── notebooks/
│   ├── eda_labels.ipynb               # Geographic, temporal, seasonal EDA
│   └── eda_features.ipynb             # Feature engineering and lag analysis
│
├── figures/                           # All saved plots
├── data/                              # Raw + processed data (gitignored)
├── notes/
│   ├── LITERATURE_NOTES.md            # Annotated notes from key papers
│   └── PAPER_OUTLINE.md              # Full paper structure
│
├── .env                               # NASA Earthdata credentials (gitignored)
├── INSTRUCTIONS.md                    # Setup guide
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
conda create -n hab python=3.11
conda activate hab
pip install numpy pandas xarray netCDF4 matplotlib cartopy scikit-learn \
            torch torchvision earthaccess xgboost shap python-dotenv jupyter
```

### 2. Configure NASA Earthdata credentials

Create a free account at [earthdata.nasa.gov](https://earthdata.nasa.gov), then create a `.env` file:

```
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password
```

### 3. Download satellite data

```bash
python src/data/bulk_download.py      # Downloads 2003-2025, ~100GB, runs overnight
```

### 4. Build label dataset

Download CT DEEP water quality data from [LISICOS ERDDAP](http://lisicos.uconn.edu/dep_portal.php) — select DEEP Water Quality Data and DEEP Nutrient Data, export as CSV from 1991–present.

```bash
python src/data/build_labels.py
```

### 5. Train models

```bash
python src/models/baseline.py         # XGBoost, Random Forest, Logistic Regression
python src/models/build_sequences.py  # Build LSTM input sequences
python src/models/lstm_model.py       # Train LSTM
python src/models/shap_analysis.py    # SHAP interpretability
```

---

## Model Architecture

### XGBoost Baseline
- 200 estimators, max depth 6, learning rate 0.1
- `scale_pos_weight` handles class imbalance (19.4% positive rate)
- Features: 16 engineered features including lagged chlorophyll (3, 7, 14, 21 days), 7-day rolling mean/std, climatological anomaly, temperature, salinity, oxygen, pH, location, month

### LSTM Temporal Model
- 2-layer LSTM, hidden size 64, dropout 0.5
- Input: 21-day sequence of 15 features per timestep
- Output: single bloom probability
- Early stopping with patience=5, Adam optimizer with weight decay
- BCELoss, class-imbalance handled via pos_weight

---

## SHAP Feature Importance

The 7-day rolling chlorophyll mean (`chl_roll7_mean`) is the dominant predictor — nearly twice as important as any other feature. This validates the core hypothesis: **the trajectory of chlorophyll buildup over the preceding week is the strongest signal of an impending bloom.**

Low salinity drives bloom probability up (freshwater/nutrient input from rivers), while high dissolved oxygen drives it down. All features behave in directions consistent with known bloom biology — no spurious learned correlations.

---

## Limitations

- **Cloud coverage:** The satellite has a 27.4% coverage rate over LIS on CT DEEP sampling days. Cloud gaps are non-random (cloudy conditions correlate with bloom-favorable stratification), creating potential bias.
- **Fixed monitoring stations:** CT DEEP samples at 50 fixed stations. The westernmost station (A4) in the Narrows — with the highest bloom risk — is underrepresented in the standard spring bloom estimate by ~36.7% (Perreira, 2021).
- **Temporal resolution:** CT DEEP samples biweekly in summer and monthly in winter. Daily satellite data can capture dynamics between sampling events that in-situ labels cannot.

---

## References

- Perreira, S. (2021). Long Term Nutrient and Chlorophyll a Dynamics across Long Island Sound. CUNY Academic Works.
- Shi, X. et al. (2015). Convolutional LSTM network. NeurIPS. [arXiv:1506.04214](https://arxiv.org/abs/1506.04214)
- Lundberg, S. & Lee, S.I. (2017). A unified approach to interpreting model predictions. [arXiv:1705.07874](https://arxiv.org/abs/1705.07874)
- Lin, T.Y. et al. (2017). Focal loss for dense object detection. [arXiv:1708.02002](https://arxiv.org/abs/1708.02002)
- Huisman, J. et al. (2018). Cyanobacterial blooms. Nature Reviews Microbiology. [doi:10.1038/s41579-018-0040-1](https://doi.org/10.1038/s41579-018-0040-1)
- Gobler, C.J. et al. (2006). Nitrogen and silicon limitation of phytoplankton communities across the East River-Long Island Sound system.
- NASA MODIS Ocean Color. (2003–2025). MODIS-Aqua L3 Daily 4km Chlorophyll. [oceancolor.gsfc.nasa.gov](https://oceancolor.gsfc.nasa.gov)
- CT DEEP / LISICOS. (1993–2025). Long Island Sound Water Quality Monitoring Program.

---

## About

Built by **Vihaan Goyal**, Westhill High School ('28), Stamford CT
