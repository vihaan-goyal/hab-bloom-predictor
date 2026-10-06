# Past ISEF projects on HAB detection, monitoring and forecasting

Method note: most facts below come straight from the Society for Science ISEF Projects Database (abstracts.societyforscience.org). I searched it by keyword (algal bloom(s), harmful algal, cyanobacteria, red tide, Karenia, Microcystis, microcystin, phycocyanin, domoic, eutrophication, chlorophyll, phytoplankton, biotoxin, shellfish, toxin, lake, bloom, algae) and by finalist surname. Each "Full Abstract" page gives title, booth ID, category, year, finalists, school, abstract and "Awards Won". A fact marked VERIFIED has a URL; one marked INFERRED is my reading. The database keyword search appears to match titles, so a project whose title never names algae or blooms could be missing (see Gaps).

Our project, for contrast: an ML forecast of chlorophyll bloom onset for Long Island Sound from 30 years of CT DEEP data (logistic regression, AUC 0.80, lift about 5x, transferred to Narragansett Bay), plus an Arduino control loop, triggered by the forecast, that runs a treatment and was bench-tested in tanks.

## Which HAB detection/forecasting projects placed at ISEF (2015-2026), and what awards?

### Takeaway
I found 19 ISEF finalist projects (2016-2026) that detect, monitor or forecast HABs, eutrophication or chlorophyll. The best result for a pure forecasting project is a **Second Award** in the category: Schweinfurth 2021, Chen 2024, Ma 2024, Choudhury 2026, and Natarajan 2024 (a hardware system). No HAB detection or forecasting project I found won First Award, Best of Category, or a Gordon E. Moore / top award. About half of the finalists won no Grand Award at all.

### Cited Findings (catalog, newest first)

**1. Prayrona Choudhury (2026), "AquaShift: Synchronized Chemical Equilibrium Convergence as a Leading Indicator of Phycocyanin-Threshold Cyanobacterial Bloom Onset Across Contrasting Freshwater Systems"**
- Hanford High School, WA. EAEV041 (Earth and Environmental Sciences). **Second Award of $2,400.** VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=28688)
- Method: an "Equilibrium-State Stoichiometry" framework. It computes reaction-quotient-to-equilibrium-constant (Q/K) ratios across coupled biochemical reactions from sensor parameters, then flags bloom onset when several reactions shift together. VERIFIED (same URL)
- Validation: NOAA buoy data from western Lake Erie (2016-2018) and the Columbia River. It beat raw-sensor baselines by 12.5% (Columbia River) and 26.2% (Lake Erie) in accuracy. VERIFIED (same URL)
- Society for Science featured it in its 2026 World Water Week alumni blog as an "early warning system for toxic algal blooms". VERIFIED: [Society blog](https://www.societyforscience.org/blog/world-water-week-2026/)
- Why it may have placed (INFERRED): a new mechanistic framing (phase transition / equilibrium) instead of plain ML, tested on two contrasting systems with public agency buoy data.
- vs ours: it is a mechanistic early-warning indicator on buoy data from two sites. Ours is a statistical onset forecast on 30 years of multi-station agency data, with a transfer test to another estuary and a hardware response loop.

**2. Sharanya Natarajan (2023, 2024, 2025), Hub & Spoke / "Seek & Abate" HAB system series**
- Edgewood Junior Senior High School, FL. Environmental Engineering. VERIFIED: [2023](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=23488), [2024](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=24909), [2025](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=26439)
- 2023, "An Engineered Hub & Spoke System to Seek & Destroy HABs (Year 4)" (ENEV021): **Third Award of $1,000.** The system combined a drone with multispectral imagery, a floating sensor platform (pH, DO, TDS, photoresistor, color intensity, temperature), a pump that disperses mitigation agent (alum-bentonite flocculation), and a cloud dashboard. A 4th-order polynomial model predicted TDS with 84% accuracy. It was tested on *Chlorella vulgaris* in the lab.
- 2024, "An Integrated Algae Mitigation System to Seek & Abate Harmful Algal Blooms (Year 5)" (ENEV005): **Second Award of $2,000**, plus an NC State College of Engineering alternate. It added remote-sensing regional scans, H2O2 suppression and an underwater-vehicle sweeper. An ML model predicted DO with 90% accuracy, using TDS as a proxy for algal density.
- 2025, "An Integrated Detection & Delivery System to Abate Contaminants in Water Bodies" (ENEV025): no Grand Award listed. A surface vehicle deployed zeolite for nitrate. Field tests ran in Lake Washington and the Indian River, and a polynomial regression predicted high-nutrient conditions with 92% accuracy.
- Why it placed (INFERRED): a multi-year, full-system engineering build (detect, verify, act) with a working prototype and a cloud dashboard. This is the closest ISEF analogue to our forecast-triggered treatment loop.
- vs ours: its "prediction" is a simple regression between sensor variables, and it has no long-term forecast or skill metrics. Ours has an agency-grade forecast with AUC and lift, and uses it to drive the actuator.

**3. Anson Chen (2024), "Forecasting Domoic Acid Levels From Harmful Algal Blooms Along the Pacific Northwest Coast" (model name: DATect)**
- Nikola Tesla STEM High School (Redmond, WA per school news; the ISEF database lists fair state "OR", a discrepancy I could not resolve). EAEV057. **Second Award of $2,000.** VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=25430)
- Method and data: 21 years of weekly beach biotoxin sampling plus environmental and satellite data. A random forest does both regression and classification. It scored R² 0.59 on DA concentration and 0.82 accuracy on threat level relative to the 20 ppm regulatory limit. Feature selection surfaced temporal features, Pacific Ocean indices and latitude. VERIFIED (same URL)
- Downstream: **Regeneron STS 2025 Top 300 Scholar**, with the project titled "DATect: Forecasting Domoic Acid Levels From Harmful Algal Blooms Along the Pacific Northwest Coast". VERIFIED: [Tesla STEM news](https://tesla.lwsd.org/students-families/families/school-news/news-details/~board/high-schools/post/beyond-the-lab-tesla-stem-student-named-to-top-300-in-prestigious-science-and-math-talent-search); [2025 STS Scholars](https://www.societyforscience.org/regeneron-sts/2025-scholars/)
- Why it placed (INFERRED): long-term agency monitoring data, a regional scale, honest moderate metrics (R² 0.59), and an explicit regulatory threshold framing.
- vs ours: the same "long-term agency data plus ML forecast" design, but it targets a toxin (DA) on the Pacific coast and reports accuracy and R². We report AUC, lift and a cross-estuary transfer, and add hardware.

**4. Yuqin Ma (2024), "CABMS: The First System Against California Marine Biotoxins Through Deep, Spatiotemporal, Multivariate Prediction and Sensor-Based Data Transmission"**
- The Harker School, CA. EAEV091. **Second Award of $2,000, and China Association for Science and Technology (CAST) Award of $1,200.** VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=25519)
- Method: data from several government agencies (six data types, six shellfish regions). It compared two deep and two classical ML algorithms, then trained 10 LSTM single-task and multi-task models, validated with time-series cross-validation. She built two generations of a wireless sensor apparatus, and real-time transmission raised accuracy by 3%. It reports ">90% acc. consistently up to 5 weeks" and ships as a containerized web app. VERIFIED (same URL)
- Why it placed (INFERRED): combines software and hardware (forecast plus a physical sensor feeding it), uses time-series cross-validation, and has a deployment story.
- vs ours: the closest structural match (agency data, a forecast and hardware). Its hardware feeds data to the model, while ours acts on the forecast. It reports accuracy, which is inflated at a low base rate, where we report AUC and lift.

**5. Olivia Ye and Ada Wang (2022), "Sea It To Believe It: Machine Learning-Based Prediction of Harmful Algal Bloom (HAB) Intensity"**
- College Park High School, TX. Environmental Engineering. No award listed. VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?Category=Any+Category&AllAbstracts=True&FairCountry=Any+Country&FairState=Any+State&ProjectId=22146)
- Method: *Karenia brevis* counts over 20 years plus nutrients, river discharge, wind and sea-surface height. It trained 21 SVM, KNN and RF models, with a paired t-test showing SVM beat KNN (p<0.020). The best was SVM on nutrients and discharge: **96.65% accuracy, F1 0.95**. It came with a public mobile app. VERIFIED (same URL)
- The isef.net ProjectBoard page "ENEV038T - Machine Learning-Based HAB Prediction" shows the same abstract text, so it appears to be this project. INFERRED from the [search snippet](https://partner.projectboard.world/isef/project/enev038t---machine-learning-based-hab-prediction); the page loads through JavaScript and I could not read it directly.
- vs ours: a red-tide intensity classifier with a very high headline accuracy and no award. It suggests judges are not moved by accuracy numbers on their own.

**6. Claire Gu (2021, 2022), Iowa CyanoHAB / beach-safety forecasting**
- Valley High School, IA. VERIFIED: [2021 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=21041), [2022 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=22559)
- 2021, "Predicting Harmful Algal Blooms in Green Valley Lake Using a Machine Learning Model" (EAEV060): a DNN predicting microcystin and chlorophyll-a from 8 years of physicochemical monitoring data. It beat a linear-regression benchmark. No award listed.
- 2022, "Forecasting Beach Safety in Iowa's Recreational Lakes Using Machine Learning Models" (ROBO049, Robotics and Intelligent Machines): 15 years of Iowa DNR microcystin monitoring (39 beaches, 8 µg/L advisory threshold), plus weather and watershed data. Four models were all above 95% accuracy, with RF and gradient-boosted trees best. It can forecast unmonitored beaches. No award listed.
- vs ours: very similar in spirit (state agency monitoring data, an advisory threshold as the label), but freshwater and toxin-based, with no transfer test, no hardware and no award.

**7. Lila Schweinfurth (2020, 2021), Oregon marine biotoxin prediction**
- Oregon Episcopal School, OR. VERIFIED: [2020 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=19319), [2021 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=20549)
- 2020, "Predicting Harmful Algal Blooms to Mitigate Neurotoxin Exposure Using 20 Years of Shellfish and MODIS Satellite Data" (EAEV013): DA and PSP classifiers, accuracy 0.96-0.98. No award listed. INFERRED: 2020 was the virtual ISEF, so there were likely no Grand Awards that year.
- 2021, "Developing a User-Friendly System for Predicting Harmful Levels of Marine Biotoxins" (EAEV008): gradient boosting and RF time-series models with forecasts up to 5 weeks ahead (accuracy 0.90-0.99), in a web app covering 32 locations. **Second Award of $2,000, and NOAA Second Award of $500.**
- Data partner: the Oregon Department of Agriculture Food Safety Division supplied the archival biotoxin data. **2021 Davidson Fellow.** VERIFIED: [Davidson Institute](https://www.davidsongifted.org/gifted-programs/fellows-scholarship/fellows/current-and-past-fellows/2021-fellows/lila-schweinfurth/)
- **2020 U.S. Stockholm Junior Water Prize, Oregon state winner.** VERIFIED (video title): [YouTube](https://www.youtube.com/watch?v=9MW7HWZEqFY)
- Why it placed (INFERRED): a second-year project that turned a model into a public tool, with a multi-week lead time and a named agency data partner.
- vs ours: shellfish toxin rather than chlorophyll bloom onset. It uses a state agency as a partner the way we use CT DEEP, but reports accuracy only and has no hardware.

**8. Ashesh Amatya (2021), "Artificial Neural Network Modeling of Harmful Algal Blooms in Lake Okeechobee"**
- Alexander W. Dreyfoos School of the Arts, FL. ENEV068. No award listed. VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=21475)
- Method: SFWMD water-quality data from 1990 to 2019, a monthly ANN in Keras (16-8 nodes) predicting chlorophyll-a from DIN, DIP and temperature, with MAE 4.7, RMSE 6.7, R² 0.7. VERIFIED (same URL)
- vs ours: the nearest data analogue (about 30 years of agency data with a chlorophyll target). It is regression on monthly means with no onset or event forecasting, no transfer, no baseline comparison and no award.

**9. Angela Mao (2021), "Analyzing Water Contaminants Through Image Processing of Chlorophyll-a"**
- Syosset High School, NY. EAEV103. No award listed. VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=21418)
- Method: MODIS-Aqua chlorophyll-a imagery from 2008 to 2020, processed with SeaDAS and ImageJ, with a GAM relating chl-a to six contaminants. VERIFIED (same URL)
- vs ours: descriptive remote-sensing correlation, not forecasting.

**10. Jordan Janakievski (2021), "Phytoplankton Detection Using Machine Learning and a Mobile Application"**
- Bellarmine Preparatory School, WA. ROBO057. No award listed. VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=21106)
- Method: a TensorFlow object-detection model on 504 images, running in a phone app held at a microscope eyepiece, aimed at citizen scientists. VERIFIED (same URL)
- vs ours: detection of cells, not forecasting.

**11. Vedant Janapaty (2022, 2023), estuarine eutrophication prediction**
- Silver Creek High School, CA. VERIFIED: [2022 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=22584), [2023 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=24347)
- 2022, "A West Coast Estuarine Case Study: A Novel, Predictive Approach to Monitor Estuarine Eutrophication" (ENEV064): 23 years of monthly satellite indices, Fourier features and ML against 10 in-situ parameters, with lagged correlations giving R² 0.2-0.93. **Fourth Award of $500.**
- 2023, "A Novel Physics Based Predictive Model for Wetland Eutrophication" (EAEV067): math models of tides, sun, seasons, sea-level rise and runoff feeding RF across five West Coast estuaries. No award listed.
- vs ours: estuarine and multi-decade like ours, but its target is monthly water-quality parameters rather than bloom events.

**12. Griffin Wagner (2019, 2020), Indian River Lagoon cyanobacteria bloom prediction plus iOS alerts**
- Vero Beach High School, FL. VERIFIED: [2019 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=16893), [2020 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=18937)
- 2019 (ENEV001): a Node.js program that predicts bloom location 4-7 days ahead from nitrate, salinity and temperature at 10 Harbor Branch LOBO sensor sites ("93% accuracy"), with iOS push alerts. It also included crop-growth tests. **Fourth Award of $500.**
- 2020 (EAEV002): an ML microcystin predictor (96.78% validation accuracy, from 4 months of field sampling), 6-7 day bloom-onset prediction, and a septic-density correlation (explaining 83% of variance), in an iOS app with location alerts. No award listed (virtual 2020 fair).
- Why it placed (INFERRED): it used a real sensor network (FAU Harbor Branch LOBO) and turned the model into an end-user alert app.
- vs ours: a short-horizon, threshold-rule early warning with an alert app. Ours adds a probabilistic model evaluated on 3 held-out years and a treatment actuator.

**13. Marvin Li (2018, 2019), satellite chlorophyll ML and red-tide classifiers**
- James M. Bennett High School, Salisbury, MD. VERIFIED: [2018 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=16319), [2019 abstract](https://abstracts.societyforscience.org/Home/FullAbstract?Category=Any+Category&AllAbstracts=False&FairCountry=Any+Country&FairState=Any+State&ProjectId=18419)
- 2018, "Machine Learning Algorithms for Satellite Remote Sensing of Ocean Color in Coastal Waters" (EAEV045): SVR, RVM and ANN retrieving chlorophyll from satellite reflectance in the Chesapeake Bay. RVM reached rmse 0.17 and r² 0.66, against NASA's OC3M at rmse 1.07. **Fourth Award of $500, and American Statistical Association Second Award of $1,000.**
- 2019, "Machine Learning Classifiers to Predict Red Tide in Florida" (EAEV044): SVM, NB and ANN on long-term *K. brevis* monitoring data. SVM reached 63% HAB accuracy, 85% non-HAB and 78% overall, and the project argued mechanisms (northerly winds causing upwelling, river nutrient loads). **Fourth Award of $500.**
- Downstream: **Regeneron STS 2021 Finalist** (top 40), with "Machine Learning Classifiers to Predict Outbreaks of Toxic *Karenia brevis* Blooms on the West Florida Shelf". VERIFIED: [STS 2021 finalists](https://societyforscience.org/regeneron-sts/2021-finalists/)
- Why it did well (INFERRED): he reported class-wise accuracy (honest about 63% on bloom events), gave a physical mechanism for the predictors, ran a scenario analysis (nutrient reduction versus climate), and built multi-year depth that carried the work to STS finalist.
- vs ours: the closest precedent to our story (long-term monitoring data, ML, and a mechanism). The STS finalist outcome shows that modest, honestly reported skill plus physical interpretation can go far. Ours adds AUC, lift, a cross-estuary transfer and hardware.

**14. Sreya Banik (2019), "Generation of Classified Image Libraries to Train Machine Learning Algorithms to Identify Different Marine Phytoplankton"**
- Lincoln Park Academy, FL. ROBO011. No award listed. It used FlowCam images from the Indian River Lagoon and a neural net that reached 88% accuracy across 5 classes. VERIFIED: [ISEF abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=17238)
- vs ours: image classification of cells, not forecasting.

**15. Sichen Shawn Chao (2016, 2017), "Developing a Numerical Box Model to Compute Algae Concentration (as Chlorophyll)"**
- MS. EAEV072 / EAEV085. **Fourth Award of $500 (2016)**, none listed in 2017. A mechanistic growth/death box model calibrated and validated on Lake Vechten (NL) and Beasley Lake (MS), delivered as a Flask web interface. VERIFIED: [2016](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=11383), [2017](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=10396)
- vs ours: a process model, not a data-driven onset forecast.

**Adjacent monitoring hardware (not HAB-specific, for context):**
- Iltekin, Akin, Leylekoglu (2024, Izmir Fen Lisesi, Turkey), "Development of a Solar Powered Buoy to Measure and Report the Pollution Level of Wetlands": **Second Award of $2,000, and a Qatar Research, Development, and Innovation Council award.** VERIFIED via database search row, ProjectId 24819: [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=24819)
- Lao and Ho (2018, Pui Ching Middle School, Macao), "A Multi-Functional, Deep Water Monitoring Robot for Pollution Control in Reservoirs": **Third Award of $1,000, and a King Abdulaziz Foundation water-technology award.** VERIFIED via database row, ProjectId 15188: [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=15188)
- Luca Barcelo (2017, CT), "Crowd-Sourced Detection and Mapping of Nitrate Water Pollutants via a Mobile Web-Based Image Analysis System": **Second Award of $2,000, and a University of Arizona scholarship.** A CT citizen-science precedent. VERIFIED via database row, ProjectId 6717: [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=6717)

**HAB projects that placed higher but are prevention or mitigation, not detection (excluded from the catalog, listed for scale):**
- Syed, Supanklang, Burgos-Rosario (2019, VA), "Cyanocide: ... HAB Mitigation via Initiation of Programmed Cell Death": **First Award of $3,000** (listed in the database under Microbiology). VERIFIED via database row, ProjectId 17934: [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=17934)
- Harshal Agrawal (2019, NJ), mycelium buffer strips, Year 5: **EPA Patrick Hurd Sustainability Award.** VERIFIED: [EPA release](https://www.epa.gov/newsreleases/innovative-water-quality-project-new-jersey-high-school-student-wins-epa-award)
- Annabelle Rayson (2023, MT), "Plankton Wars: ... Daphnia Genotype Biomanipulation for Algae Bloom Prevention": **Fourth Award of $500, and CAST $1,200** at ISEF ([database row, ProjectId 24296](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=24296)). She won the **2022 international Stockholm Junior Water Prize** for Canada ([Down To Earth](https://www.downtoearth.org.in/water/canadian-student-wins-2022-stockholm-junior-water-prize-84642)).

### Inferences
- The award ceiling for HAB forecasting at ISEF has been Second Award ($2,000-$2,400) plus agency special awards (NOAA, ASA, CAST). No HAB detection or forecasting project in the database won First Award or Best of Category from 2016 to 2026. Our project would be competing to break that ceiling rather than match precedent.
- Earth and Environmental Sciences (EAEV) holds most forecasting projects. Engineering-heavy system builds went to Environmental Engineering (ENEV), and one forecasting project went to ROBO.
- Projects with high headline accuracy but no system or mechanism (Ye/Wang 96.65%, Gu >95%, Amatya R² 0.7) won nothing. Projects with honest or moderate metrics plus a deployed tool, a data partner, hardware or a mechanism (Li, Schweinfurth, Chen, Ma, Choudhury) placed. Judges appear to reward completeness and rigor over the size of the accuracy number.

### Gaps
- The keyword search seems to match titles only, so projects with non-obvious titles (for example "LakeGuard" or "BloomNet") could be missed. The isef.net / ProjectBoard pages load through JavaScript and could not be read.
- I did not check special-award lists (NOAA, EPA, ASA, AFRL) for every year. Only the special awards printed in each abstract's "Awards Won" are recorded here.
- I cannot say whether 2020 finalists received any awards. The virtual 2020 fair structure is INFERRED, not verified here.

## What methods, data, and validation did winners use?

### Takeaway
The placing forecasting projects used long-term public or agency datasets: shellfish biotoxin archives (ODA, WA/CA agencies), NOAA buoys, FAU Harbor Branch LOBO, SFWMD, Iowa DNR and MODIS. The models were tree ensembles, SVMs or LSTMs, and the results were delivered as a web or mobile app. Validation was mostly an accuracy score on a split or time-series CV. None reported AUC, lift, or a cross-system transfer test on unseen water bodies, except Choudhury's two-system comparison.

### Cited Findings
- Time-series cross-validation and multi-week forecast horizons ("up to 5 weeks", >90% accuracy) with sensor hardware feeding the model: Ma 2024. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=25519)
- A regulatory-threshold classification (20 ppm DA) alongside regression (R² 0.59): Chen 2024. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=25430)
- A forecast horizon of up to 5 weeks with a public web app over 32 locations, and data from the Oregon Department of Agriculture: Schweinfurth 2021. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=20549); [Davidson](https://www.davidsongifted.org/gifted-programs/fellows-scholarship/fellows/current-and-past-fellows/2021-fellows/lila-schweinfurth/)
- Validation across two contrasting systems (Lake Erie and the Columbia River) against a raw-sensor baseline: Choudhury 2026. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=28688)
- Class-wise accuracy (HAB versus non-HAB) plus a mechanistic explanation: Li 2019. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?Category=Any+Category&AllAbstracts=False&FairCountry=Any+Country&FairState=Any+State&ProjectId=18419)
- A comparison against an operational NASA algorithm as the baseline: Li 2018. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=16319)
- Field deployment of hardware in Lake Washington and the Indian River: Natarajan 2025. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=26439)

### Inferences
- Beating an operational or baseline method (Li 2018 against NASA OC3M; Choudhury against raw sensors) is a recurring feature of the placed projects. Our climatology and persistence baselines, and the lift figure, fit this pattern well.
- None of the catalogued projects reports ROC AUC with confidence intervals, pre-registered predictions, or a label-quality audit (like our CTD-versus-lab chlorophyll correction). Those would be distinguishing rigor signals.

### Gaps
- None of the abstracts give the test-set design (random versus temporal split) except Ma's time-series CV. That cannot be verified without posters or papers.

## Any projects that forecast blooms from long-term state-agency monitoring data with ML, and how did they validate and present?

### Takeaway
Yes, several: Li 2019 (Florida *K. brevis* monitoring), Amatya 2021 (SFWMD, 1990-2019), Gu 2021/2022 (Iowa DNR, 15 years), Schweinfurth 2020/2021 (Oregon Department of Agriculture, 20 years), Chen 2024 (21 years of PNW beach sampling) and Ma 2024 (California agencies). Every one presented a single-region model with accuracy-type metrics, and most added an app. None tested transfer to a second estuary with a frozen model.

### Cited Findings
- Amatya: SFWMD Lake Okeechobee 1990-2019, a monthly ANN for chl-a, R² 0.7. No award. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=21475)
- Gu: Iowa DNR weekly microcystin at 39 beaches over 15 years, >95% accuracy, forecasts at unmonitored beaches. No award. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=22559)
- Schweinfurth: ODA shellfish data over 20 years with MODIS, 5-week lead. Second Award and NOAA. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=20549)
- Chen: 21 years of weekly beach DA sampling, RF, R² 0.59 and 0.82 threshold accuracy. Second Award, then STS Scholar. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?projectId=25430)
- Li: long-term *K. brevis* monitoring, SVM 78% overall and 63% on HAB events. Fourth Award, then STS 2021 Finalist. [abstract](https://abstracts.societyforscience.org/Home/FullAbstract?Category=Any+Category&AllAbstracts=False&FairCountry=Any+Country&FairState=Any+State&ProjectId=18419); [STS](https://societyforscience.org/regeneron-sts/2021-finalists/)

### Inferences
- Our project sits squarely in this precedent class (agency monitoring data plus ML). What sets it apart is (a) a 30-year, 50-station dataset with a lab-corrected label, (b) a transfer to Narragansett Bay, (c) event-based skill metrics (AUC, lift, precision and recall at an operating threshold), and (d) a closed-loop actuator. No project in the catalog does (b) or (d) together with a forecast.
- The best-placed precedents (Schweinfurth, Ma) each had a public-facing tool. A dashboard or alert demo is probably expected.

### Gaps
- I found no ISEF project using Long Island Sound or CT DEEP LISICOS data (none in the searched titles). I did not check the 2026 finalists who did not win awards in full.

## Which went on to Regeneron STS, JSHS, Stockholm Junior Water Prize, or publications?

### Takeaway
Marvin Li became an STS 2021 Finalist, Anson Chen an STS 2025 Scholar, and Lila Schweinfurth a 2021 Davidson Fellow and 2020 Oregon SJWP state winner. The Maryland team Wankhede and Bhattacharyya (AntiBloom buoy) was 2023 U.S. SJWP runner-up, with no ISEF appearance found. I found no JSHS outcomes for these students.

### Cited Findings
- Marvin Li: Regeneron STS 2021 Finalist. [STS 2021 finalists](https://societyforscience.org/regeneron-sts/2021-finalists/)
- Anson Chen: Regeneron STS 2025 Top 300 Scholar, "DATect". [Tesla STEM news](https://tesla.lwsd.org/students-families/families/school-news/news-details/~board/high-schools/post/beyond-the-lab-tesla-stem-student-named-to-top-300-in-prestigious-science-and-math-talent-search)
- Lila Schweinfurth: 2021 Davidson Fellow ([Davidson](https://www.davidsongifted.org/gifted-programs/fellows-scholarship/fellows/current-and-past-fellows/2021-fellows/lila-schweinfurth/)), and 2020 U.S. SJWP Oregon state winner ([YouTube](https://www.youtube.com/watch?v=9MW7HWZEqFY))
- Jay Wankhede and Neel Bhattacharyya (Poolesville HS, MD): "AntiBloom: A Novel Deep Learning-Powered Harmful Algal Bloom (HAB) Prediction Device", named runner-up at the 2023 U.S. Stockholm Junior Water Prize ([WEF press release](https://www.wef.org/publications/news/wef-press-releases/park-wins-u.s.-stockholm-junior-water-prize/)). It was a $150 buoy measuring wind speed, UV, pH, water temperature and salinity, with an ANN (Keras/sklearn) and AWS alerts. A paper is on ResearchGate ([ResearchGate](https://www.researchgate.net/publication/382963900_AntiBloom_A_Novel_Deep_Learning-Powered_Device_to_Predict_Harmful_Algal_Blooms); the page returned 403, so details come from the search snippet only). A surname search of the ISEF database found no ISEF entry for them.
  - vs ours: a low-cost sensor buoy with ANN prediction and alerts. It does detection and nowcast; ours does a multi-week agency-data forecast that drives treatment.
- Annabelle Rayson: 2022 international SJWP winner (prevention, not detection). [Down To Earth](https://www.downtoearth.org.in/water/canadian-student-wins-2022-stockholm-junior-water-prize-84642)

### Inferences
- Long-term-data HAB forecasting projects have converted into STS recognition twice (Li, Chen), even though their ISEF awards were modest. That suggests the ISEF, STS and SJWP pipeline values this kind of work, especially with a strong written paper.

### Gaps
- I did not find peer-reviewed publications by Li, Schweinfurth, Chen, Ma, Gu or Choudhury in this pass. Not searched: Journal of Emerging Investigators, arXiv author searches, and JSHS national winner lists.
- There is no verified record of Yuqin Ma or Prayrona Choudhury in STS lists. Not checked.
