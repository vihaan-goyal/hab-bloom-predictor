# Research Plan (ISEF Form 1A structure), rewritten 2026-10-07

Status: for review and signature by the Adult Sponsor and Direct Supervisor, Meghana Fernandez
(Forms 1, 1A, 1B; Form 3 and 6A alongside). No bench work starts before these are signed and the CSEF
Scientific Review Committee approves Forms 3 and 6A.

This replaces the 2026-09-05/19 plan, which described a magnetic clay-flocculation device. That device
was dropped on 2026-10-01 because it can't run unattended on the water; the bench now tests aeration
and low-dose hydrogen peroxide (`notes/mitigation/EXECUTION_PLAN.md`, "Plan change 2026-10-01"). The
old plan is in git history (before the 2026-10-07 commit). The CSEF registration text, limited to
1,000 words, is the "CSEF Research Plan" Google Doc; this file is the full version with the same
hypotheses.

## A. Rationale

Algal blooms in coastal waters cause severe hypoxia, toxic contamination of marine life, and
disruptions to marine ecosystems and local economies. Water-quality agencies find blooms by sampling
on a fixed schedule, so they usually act only after a bloom is visible, when treatment works least.
Operational forecasts (NOAA Lake Erie, Gulf of Mexico HAB-OFS, California C-HARM) cover a few places
and rely on satellites or circulation models. Continuous sensors now report chlorophyll fluorescence
every 15-60 minutes at thousands of sites, but no low-cost system uses those readings to forecast a
bloom and act on it automatically.

## B. Research question, hypotheses and engineering goals

**Question:** Can a low-cost autonomous device forecast algal blooms from daily sensor data and
trigger treatment early enough to reduce their peak?

**Forecasting hypothesis:** if the forecast uses daily sensor data, then it ranks bloom risk better
than a calendar (time-of-year) forecast in a pre-registered test (p < 0.05), because daily data
captures bloom starts that 3-weekly boat sampling misses.

**Treatment hypothesis:** if a treatment (aeration or low-dose hydrogen peroxide) is switched on
automatically when the forecast predicts a bloom, then treated tanks will have a lower or later bloom
peak than both untreated tanks and tanks treated only after the bloom becomes visible, without
harming non-target organisms (brine shrimp) or pushing algae below their normal levels, because
acting early stops growth before cell numbers are high.
- The pass marks are fixed in `notes/mitigation/00_CONTROL_LOOP.md`: aeration is judged on days held
  below the bloom threshold; peroxide on a ≥ 50% lower peak than untreated tanks and a larger cut than
  reactive treatment; non-target survival equal to untreated; never below 80% of the warm-up level.
- Also reported, with no pass mark: days to regrow after treatment stops, and whether peroxide hits
  small cells (about 2 µm) harder than large ones.

**Engineering goals:** a low-cost device (about $400 in parts) that runs the forecast on board and
matches the computer model's alerts (100% identical), measures chlorophyll within ±20% of a reference
after calibration, runs unattended for 14 days with no gaps in its log, and doses peroxide so the far
side of the tank reaches 0.8 ± 0.2 mg/L within 15 min while staying below 2.8 mg/L 50 cm from the
outlet within 5 min.

## C. Procedures

**Location and supervision.** Bench work at Bi-Cultural Hebrew Academy (Stamford, CT) under Direct
Supervisor Meghana Fernandez (M.S. Microbiology, UCLA; Adjunct Professor, UConn), who is present for
all chemical and culture work. Computational work is done at home on public data.

### C.1 Forecast (computational)
- **Device model:** gradient boosting trained on Narragansett Bay (RI DEM) fixed-site sondes
  (chlorophyll fluorescence, oxygen, temperature, salinity, summarized daily); it predicts whether
  chlorophyll exceeds the bloom level within 7 days. Alert threshold 0.45, chosen on validation data.
- **Long Island Sound model:** CT DEEP boat-survey data (50 stations, 1993-2025, lab-corrected
  chlorophyll), logistic regression with 35 features.
- **Testing:** each model is scored only on years it was not trained on (walk-forward), with
  thresholds chosen on validation data, and compared with a calendar forecast by AUC with a
  station-year bootstrap (2,000 resamples, one-sided p < 0.05), as pre-registered. Model-class
  alternatives (gradient boosting, neural networks, TabPFN) were tested under separate
  pre-registrations. The 2026 season is a pre-registered independent check
  (`notes/PROSPECTIVE_2026_PREREG.md`).

### C.2 Bench
1. **Seawater:** artificial sea salt in distilled water to salinity 27.5 (matched to the Sound), with
   nitrate, phosphate and silicate stocks and f/2 trace metals and vitamins; 12-15 °C; 12:12 light.
2. **Cultures:** non-toxic marine microalgae from NCMA (*Skeletonema*, *Thalassiosira weissflogii*,
   *Phaeodactylum tricornutum*, *Prorocentrum micans*, *P. triestinum*, *Micromonas pusilla*,
   *Nannochloropsis*), grown in f/2 medium.
3. **Aeration screen:** 500 mL cultures at four air flows (none; gentle, CO₂ only; 25 mL/min =
   0.05 vvm; 300 mL/min = 0.6 vvm, matching Sung & Gobler 2026) × 4 species × 3 replicates; 48 h on,
   48 h regrowth.
4. **Peroxide screen:** 250 mL flasks at 0, 0.8, 1.6, 3.2 and 6.4 mg/L H₂O₂ (3% H₂O₂ diluted to a
   0.1% working solution; 160 µL per 200 mL = 0.8 mg/L), plus three daily 0.8 mg/L pulses; sodium
   percarbonate at the same peroxide dose; sodium carbonate as a pH control; 3 replicates; counts at
   24, 48 and 72 h. Brine shrimp (*Artemia*) survival is the non-target check.
5. **Loop runs:** 10 L tanks, 3 per arm: A untreated; B forecast-triggered loop; C reactive
   (starts at 50% of the expected peak); D false alarm (loop triggered with no nutrients added).
   A 21-day low-nutrient warm-up, then a nutrient pulse starts the bloom (2-3 weeks), then 5 days of
   monitoring. Two pilot tanks confirm the culture blooms and set the expected peak.
6. **Loop control:** an Arduino reads chlorophyll (DIY fluorometer), temperature and pH, runs the
   forecast, and turns treatment on at a bloom probability of 0.45. It re-measures after each period
   and turns off when the forecast drops and chlorophyll is low and not rising.
   - Peroxide: 0.8 mg/L per pulse (8 mL of 0.1% per 10 L, calibrated peristaltic pump, inline
     dilution); a new pulse only if the residual is ≤ 0.5 mg/L; at most 3 pulses.
   - Aeration: air pump switched by a relay.
   - Automatic stops: peroxide above 2.8 mg/L, pH outside 7.6-8.6, dissolved oxygen below 4 mg/L,
     or chlorophyll below 80% of normal for 2 days.
   - Before the loop run, procedure P7 checks pump calibration, the controller logic and how the dose
     spreads through the tank (`notes/mitigation/PROCEDURES.md`).

### C.3 Risk and safety (Form 3; Form 6A)
- **Chemicals:** hydrogen peroxide 3% and 7% (up to 1 L), sodium percarbonate (up to 100 g), sodium
  carbonate, nutrient salts (sodium nitrate, sodium phosphate, sodium metasilicate), household bleach,
  90% acetone (up to 250 mL), water-test kit reagents. Hazards: eye and skin irritation or burns;
  percarbonate and nitrate are oxidizers; bleach releases toxic gas with acids or ammonia; acetone is
  flammable.
- **Activities and devices:** mains and 12 V pumps and grow lights near salt water (all mains devices
  on a GFCI; electronics above the water; unplug before reaching into a tank); soldering (lead-free,
  ventilated, iron unplugged after use).
- **Organisms:** non-toxic marine microalgae, Risk Group 1, handled at BSL-1 (Form 6A); brine shrimp
  (invertebrates) for toxicity tests. No humans, no vertebrates, no tissue, no toxic or pathogenic
  strains.
- **Precautions:** supervisor present; splash goggles, nitrile gloves and lab coat; no food or drink;
  small quantities; Safety Data Sheets read before first use; stocks labeled and dated; never mix
  bleach with acids, ammonia or peroxide; acetone only with ventilation and no flames.
- **Disposal:** peroxide-treated water is held until test strips read below 0.5 mg/L; all
  algae-containing water is disinfected with 10% bleach for 30 min and flushed down a lab sink;
  consumables are bleached and bagged; brine shrimp are frozen or bleached, never released. Nothing
  goes into the Sound, storm drains or the ground.

### C.4 Data analysis
- **Forecast:** AUC on held-out years, precision and lift at the validation-chosen threshold, and the
  paired bootstrap against the calendar forecast.
- **Bench:** peak chlorophyll, area under the chlorophyll curve, days below the bloom threshold,
  total treatment (hours ON or mg dosed), number of treatment episodes, brine shrimp survival and
  dissolved oxygen, compared between arms with Welch 95% confidence intervals on n = 3 tanks
  (t-intervals, t = 4.30). With n = 3 a result can be "consistent but underpowered", and it is
  reported that way.

## D. Bibliography

1. Anderson, D. M., Cembella, A. D., & Hallegraeff, G. M. (2012). Progress in understanding harmful
   algal blooms: paradigm shifts and new technologies for research, monitoring, and management.
   *Annual Review of Marine Science*, 4, 143-176.
2. Matthijs, H. C. P., et al. (2012). Selective suppression of harmful cyanobacteria in an entire lake
   with hydrogen peroxide. *Water Research*, 46, 1460-1472.
3. Randhawa, V., Thakkar, M., & Wei, L. (2012). Applicability of hydrogen peroxide in brown tide
   control: culture and microcosm studies. *PLOS ONE*, 7, e47844.
4. Sung, J., & Gobler, C. J. (2026). Mitigation of harmful algal bloom (*Margalefidinium
   polykrikoides*) intensity and toxicity via aeration processes. *Journal of Environmental
   Management*, 402, 129015.
5. Reichwaldt, E. S., Zheng, L., Barrington, D. J., & Ghadouani, A. (2012). Acute toxicological
   response of *Daphnia* and *Moina* to hydrogen peroxide. *Journal of Environmental Engineering*,
   138, 607-611.
6. Thoo, R., Siuda, W., & Jasser, I. (2020). The effects of sodium percarbonate generated free oxygen
   on *Daphnia*: implications for the management of harmful algal blooms. *Water*, 12, 1304.
7. Guillard, R. R. L. (1975). Culture of phytoplankton for feeding marine invertebrates. In W. L.
   Smith & M. H. Chanley (Eds.), *Culture of Marine Invertebrate Animals* (pp. 29-60). Plenum Press.
8. Connecticut Department of Energy and Environmental Protection. Long Island Sound Water Quality
   Monitoring Program data, 1993-2025.
9. Rhode Island Department of Environmental Management. Narragansett Bay Fixed-Site Monitoring
   Network data, 2005-2023.

## Not claimed
- That the device prevents blooms in open water: the test is in tanks; the target is enclosed or
  semi-enclosed water (harbors, shellfish beds, aquaculture pens, coastal ponds).
- That the device is field-ready, or safe without the false-alarm (arm D) data.
- Any result before it is measured.
