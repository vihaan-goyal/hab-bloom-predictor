# Spatiotemporal Prediction of Harmful Algal Blooms in Long Island Sound
# Using Machine Learning and NASA MODIS Satellite Data

**Vihaan Goyal**
Westhill High School, Stamford, Connecticut

---

## Abstract (write last, ~250 words)
- What you did
- How you did it
- Key result (AUC 0.928, 7 days ahead)
- Why it matters

---

## 1. Introduction (~500 words)
- HABs cost US economy $100M/year, close beaches, kill fish
- LIS specifically has documented Alexandrium and brown tide problems
- Current methods are threshold-based and reactive
- Satellite remote sensing enables proactive monitoring
- Gap: no spatiotemporal ML model exists for LIS at this resolution
- What this paper contributes

---

## 2. Data (~400 words)

### 2.1 Study Area
- Long Island Sound bounding box (40.5-41.5N, 73.8-71.8W)
- Why LIS: documented HAB history, local relevance, CT DEEP monitoring

### 2.2 In-Situ Water Quality Data
- CT DEEP monitoring program, 50 stations, 1993-2025
- 1.36M chlorophyll measurements
- Bloom threshold definition: 10 ug/L (cite literature)
- 19.4% bloom rate

### 2.3 Satellite Data
- NASA MODIS Aqua L3 daily 4km chlorophyll
- 2003-2025, 7,500+ files
- Cloud coverage challenge: 73% gap rate

### 2.4 Auxiliary Features
- Nutrients from CT DEEP (NOX-LC, DIP, NH#-LC)
- Lagged features: 3, 7, 14, 21 day lags
- Rolling statistics: 7-day mean and std
- Climatological anomaly

---

## 3. Methods (~600 words)

### 3.1 Problem Formulation
- Binary classification: bloom within 7 days yes/no
- Spatiotemporal cross-validation (train 1993-2019, val 2020-2022, test 2023-2025)
- Why random split is wrong here

### 3.2 Feature Engineering
- Lagged features rationale (cite lag correlation decay figure)
- Climatological anomaly computation
- Class imbalance handling

### 3.3 Baseline Models
- Logistic Regression
- Random Forest
- XGBoost

### 3.4 LSTM Model
- Architecture: 2-layer LSTM, hidden size 64, dropout 0.5
- Input: 21-day sequence, 15 features
- Early stopping with patience=5
- Training details

---

## 4. Results (~500 words)

### 4.1 Exploratory Analysis
- Western LIS geographic gradient (Figure 1)
- Long-term decline -0.63%/year (Figure 4)
- Seasonal patterns: spring peak (Figure 3)
- Lag correlation decay (Figure 5)

### 4.2 Model Performance
- Results table: LR, RF, XGBoost, LSTM
- XGBoost AUC 0.928, LSTM AUC 0.926
- Test set final numbers (run after download finishes)

### 4.3 Feature Importance
- SHAP analysis (Figures 7, 8)
- chl_roll7_mean dominant
- Biological consistency of all features

---

## 5. Discussion (~400 words)
- What the model learned vs what biology predicts
- Why spring blooms dominate (counterintuitive finding)
- Decline after 2014 -- nitrogen reduction programs
- Limitations: cloud gaps, fixed monitoring stations
- Future work: ConvLSTM, VIIRS higher resolution

---

## 6. Conclusion (~150 words)
- Summary of contribution
- Practical deployment potential for CT DEEP

---

## References
- Huisman et al. 2018 (bloom biology)
- Shi et al. 2015 (ConvLSTM)
- Lundberg & Lee 2017 (SHAP)
- Stumpf et al. 2009 (HAB satellite prediction)
- Lin et al. 2017 (focal loss)
- CT DEEP monitoring program
- NASA MODIS documentation
- Perreira, S. (2021). Long Term Nutrient and Chlorophyll a Dynamics across Long Island Sound and Impacts on Dissolved Oxygen Conditions within the Western Sound (1991-2019). CUNY Academic Works.
    https://academicworks.cuny.edu/cgi/viewcontent.cgi?article=2002&context=cc_etds_theses