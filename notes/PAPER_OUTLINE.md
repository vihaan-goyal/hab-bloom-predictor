# Spatiotemporal Prediction of Harmful Algal Blooms in Long Island Sound
# Using Machine Learning and NASA MODIS Satellite Data

**Vihaan Goyal & Lev Rubin**
Westhill High School, Stamford, Connecticut

---

## Abstract (write LAST, ~250 words)
Five required elements — nothing more, nothing less:
- What you built: ML system that predicts HABs 7 days in advance in Long Island Sound
- Data used: 22 years NASA MODIS satellite data + 32 years CT DEEP in-situ measurements, 1.36M chlorophyll measurements, 50 stations
- Primary result: XGBoost AUC 0.936 on held-out 2023–2025 test set, 81% bloom recall
- Secondary result: hybrid ConvLSTM+LSTM achieves AUC 0.744
- Intervention result: 975 high-priority intervention opportunities; Station A4 DO as low as 1.39 mg/L; August peak window
- Deployment: operational daily inference pipeline with automated alerts

---

## 1. Introduction (~500 words)

### 1.1 Why HABs matter
- HABs cost US economy $100M/year (cite Anderson et al. 2002)
- LIS has documented Alexandrium and Aureococcus blooms threatening $10.7B annual economic value (cite Creedon 2018)
- Shellfish harvesting industry specifically at risk

### 1.2 Why LIS specifically
- Semi-enclosed estuary, well-documented west-to-east eutrophication gradient
- Nitrogen inputs from East River wastewater treatment plants + urban runoff (cite Gobler et al. 2006)
- CT DEEP has monitored 50 stations since 1991 — 32 years of data available

### 1.3 Gap in current practice
- Current HAB detection is REACTIVE — biweekly water samples, blooms confirmed after damage done
- Threshold-based methods fail to capture temporal dynamics preceding bloom formation
- No spatiotemporal ML model exists specifically for LIS — this is the gap you fill
- ⚠ Say "to our knowledge" no such system exists

### 1.4 What satellite data offers (and its limits)
- MODIS Aqua provides daily 4km observations since 2002
- Challenge: ~70% cloud gap rate over LIS
- Challenge: 4km resolution coarse relative to Sound's 34km width

### 1.5 Contributions list
- First ML HAB prediction system for LIS validated on held-out future data
- Temporal feature engineering using lagged chlorophyll trajectories
- Two-stream hybrid ConvLSTM+LSTM architecture
- Aeration intervention framework (prediction → prevention)
- Operational daily inference pipeline with dashboard and email alerts
- SHAP interpretability analysis confirming biological plausibility

---

## 2. Data (~400 words)

### 2.1 Study Area
- LIS bounding box: 40.5–41.5°N, 73.8–71.8°W
- 177 km long, max 34 km wide, 20–70 m depth
- Semi-enclosed geometry → limited tidal flushing → nutrient accumulation in western basin

### 2.2 In-Situ Water Quality
- CT DEEP monitoring program, 50 stations, 1991-present
- Biweekly Jun–Sep, monthly year-round
- Variables: chlorophyll-a (µg/L), temperature (°C), salinity (psu), DO (mg/L), pH
- Bloom threshold: chlorophyll-a > 10 µg/L — cite Perreira (2021)
- Total observations: 1,358,852 measurements
- Bloom observations: 262,959 (19.4% positive rate)
- Years: 1993–2025

### 2.3 Satellite Data
- NASA MODIS Aqua L3, product: MODISA_L3m_CHL
- 4 km resolution, daily, 2003–2025
- 8,356 NetCDF files downloaded
- 29.9% of station-days have valid satellite observations (70% cloud gap)
- For hybrid model: 8×8 pixel patches centered on each station

### 2.4 Auxiliary Data
- USGS discharge gauges: Connecticut R. (01184000), Thames R. (01127000), Housatonic R. (01205500)
- 1993–2025
- ⚠ Discharge was removed in ablation study — mention here but note excluded from final model

### Data summary table
Source | Description | Coverage | Records

---

## 3. Methods (~600 words)

### 3.1 Problem Formulation
- Binary classification: predict bloom within next 7 days (yes/no)
- Formal definition: y(t) = 1 if max{chl(t+1),...,chl(t+7)} > 10 µg/L
- Why 7 days: operationally sufficient for CT DEEP to stage aeration equipment

### 3.2 Feature Engineering
- Lagged chlorophyll at 3, 7, 14, 21 days
- 7-day rolling mean (chl_roll7_mean) and std (chl_roll7_std)
- Climatological anomaly: deviation from long-term monthly mean
- Climatological baseline: long-term monthly mean
- Spatial: latitude, longitude / Temporal: calendar month
- Total: 11 features for primary model; 16 features for extended ablation model
- Correlation decay: r=0.707 same-day → r=0.466 at 21-day lag
- ⚠ Note 3-day and 7-day lags are approximated from nearest reading within 7-day window

### 3.3 Cross-Validation
- Train: 1993–2019 | Val: 2020–2022 | Test: 2023–2025
- Temporal blocked split — NOT random (explain why random would introduce leakage)
- Test set held out completely — touched only once, after all model selection done

### 3.4 Models (all six)
- Logistic Regression: L2, balanced class weights
- Random Forest: 100 trees, balanced class weights
- XGBoost: 200 estimators, max depth 6, lr 0.1, scale_pos_weight ≈ 4.15
- LSTM: 2-layer, hidden 64, dropout 0.5, Adam, weight decay 1e-4, early stopping patience 5
- ConvLSTM: 2-layer, 16 hidden channels, 3×3 kernels, 8×8 pixel MODIS patches
- Hybrid: ConvLSTM spatial stream + LSTM temporal stream, concatenated → shared MLP
- ⚠ Deep learning models trained on satellite-matched subset (290,938 samples) — tabular models on full 1.36M

### 3.4.1 Decision Threshold
- All reported recall/precision values use threshold 0.50
- Swept 0.10–0.90 to verify 0.50 is a reasonable operating point
- At 0.50: recall 0.812, precision 0.662, false alarm rate 6.0%
- At 0.35: recall 0.849 but false alarms triple to 10.1%
- At 0.70 (best F1): recall 0.758, precision 0.743, F1 0.751
- ⚠ Frame as deliberate choice, not default

### 3.5 Aeration Intervention Framework
- Define hypolimnetic aeration and the three conditions it requires
- Score formula: S = 0.45·[(14−DO)/12] + 0.30·[(T−10)/20] + 0.25·p
- Weights: DO=0.45 (primary lever), T=0.30 (stratification), p=0.25 (confidence)
- Highly suitable threshold: P > 0.70 AND S > 0.60 AND DO < 6.0 mg/L
- Applied to validation period (2020–2022) predictions only

### 3.6 Operational Deployment
- Daily inference pipeline: fetches ERDDAP → engineers features → runs XGBoost → computes S → sends email alerts
- Browser-based dashboard: station probability chart, DO vs. bloom scatter, intervention priority table
- No server required — runs from CSV in browser

---

## 4. Results (~500 words)

### 4.1 Exploratory Analysis
- Geographic gradient: 46.3% bloom rate at A2 → 1.7% at N3
- Long-term decline: −0.63%/year, inflection after 2014 linked to Clean Water Act TMDL
- Seasonal pattern: February–March peak (~40%) driven by cold-water diatoms
- Temporal signal decay: r=0.707 (same-day) → r=0.466 (21-day lag)

### 4.2 Model Performance
- Results table with all 6 models: Val AUC + Test AUC for XGBoost
- XGBoost: Val 0.928, Test 0.936, Recall 0.81, Precision 0.66, Avg Precision 0.789
- LSTM: Val 0.926
- Hybrid: Val 0.744, Test 0.658
- ConvLSTM: Val 0.696, Test 0.610
- ⚠ Explain DL models trained on smaller satellite-matched subset

### 4.3 Feature Importance (SHAP)
- Top feature: chl_roll7_mean — SHAP ~2x the next feature
- Rank order: chl_roll7_mean, chl_anomaly, chl_climatology, dissolved_oxygen, salinity, temperature, chl_lag3
- Critical finding: DO/temperature add ΔAUC < 0.005 over chlorophyll-only model

### 4.4 Ablation Study
- Largest drop: removing climatological features (ΔAUC = −0.013)
- Removing river discharge slightly improves (+0.002)
- Minimal model (top 5 features): AUC 0.912

### 4.5 Failure Analysis
- FP and FN both peak July–August
- Station A4: highest error rates (616 FP, 311 FN)

### 4.6 Aeration Intervention
- 27,412 high-risk predictions in 2020–2022 validation period
- 975 (3.6%) meet stringent criteria (P > 0.70 AND S > 0.60 AND DO < 6.0 mg/L)
- Mean bloom prob of intervention candidates: 0.836
- Station A4: 2,560 high-risk days, mean bloom prob 0.87, minimum DO = 1.39 mg/L
- August peak: 10,804 high-risk bloom-days, mean aeration score 0.677
- February: highest bloom probability (0.954) but LOWEST aeration suitability (0.341)

### 4.7 Operational Validation
- 2022-09-01: A4 P=0.970, DO=5.76, S=0.767 — Station 16 also flags (P=0.746, DO=5.99)
- 2022-08-17: A4 P=0.886, DO=5.89
- 2021-08-31: A4 P=0.882, DO=5.88
- 2017-08-15: A4 P=0.749, DO=4.75

---

## 5. Discussion (~400 words)

### 5.1 Performance explanation
- AUC 0.936 on truly future data — generalizes well beyond training
- XGBoost beats DL: (a) full 1.36M dataset vs 290K satellite-matched, (b) dominant feature is rolling mean easily captured by trees, (c) 4km patches too coarse for 34km-wide Sound

### 5.2 Biological validation
- Rolling mean dominance validates hypothesis: bloom = temporal accumulation process
- All SHAP directional effects consistent with known LIS bloom biology (cite Gobler 2006, Perreira 2021)
- Spring bloom peak explained: cold-water diatoms, low zooplankton grazing

### 5.3 Aeration framework novelty
- First system to translate bloom forecasts into intervention targeting guidance
- A4 1.39 mg/L DO = sediment enters phosphorus-releasing anoxic state → positive feedback
- August window: aeration most effective when thermal stratification AND bloom risk both high
- February: highest bloom prob but lowest aeration score — cold water is well-mixed

### 5.4 Policy finding
- −0.63%/year decline + 2014 inflection = direct observational evidence for Clean Water Act effectiveness
- Continued nitrogen management is complementary to reactive aeration

### 5.5 Limitations
- 70% cloud gap rate — systematic bias toward cloud-free conditions
- Biweekly sampling → 3-day and 7-day lag features are approximated
- Aeration scores from observational data, not hydrodynamic model
- Fixed monitoring stations — performance at unmonitored locations unknown

### 5.6 Future work
- Couple with ROMS or FVCOM hydrodynamic model
- Higher-res satellite: Sentinel-3 OLCI at 300m or VIIRS at 750m
- Low-cost autonomous chlorophyll sensor platform

---

## 6. Conclusion (~150 words)
- AUC 0.936 on held-out 2023–2025 data
- 81% bloom recall, 7-day advance warning
- 975 intervention opportunities identified, A4 highest priority, August optimal window
- Operational pipeline validated against confirmed low-DO events
- First ML HAB system for LIS validated on held-out future data

---

## References
- Anderson, D.M. et al. (2002). HABs and eutrophication. Estuaries, 25(4), 704–726.
- Chen, T. & Guestrin, C. (2016). XGBoost. KDD 2016.
- Creedon, M. (2018). Dams on Long Island: Their economic impact.
- Gobler, C.J. et al. (2006). Nitrogen and silicon limitation across urban estuary. Est. Coastal Shelf Sci., 68, 127–138.
- Huisman, J. et al. (2018). Cyanobacterial blooms. Nature Reviews Microbiology.
- Lundberg, S.M. & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 30.
- Perreira, S. (2021). Long term nutrient and chlorophyll a dynamics across LIS. CUNY Master's thesis.
- Rice, E. et al. (2013). Impact of anthropogenic nutrient inputs on phytoplankton growth in LIS. Estuaries and Coasts.
- Shi, X. et al. (2015). Convolutional LSTM network. NeurIPS 28.
- Stumpf, R.P. et al. (2009). Skill assessment for operational algal bloom forecast. J. Marine Systems, 76, 151–161.