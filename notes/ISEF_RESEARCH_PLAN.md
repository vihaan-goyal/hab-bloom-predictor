# Research Plan (ISEF Form 1A structure) — draft 2026-09-05

Status: DRAFT for adult-sponsor review. The prospective test (Section D.3)
has NOT started; it begins the week after Form 1A is signed. Everything in
D.1–D.2 was completed before this plan was written and is labelled as such.
No human or vertebrate subjects, no hazardous materials, no PHBAs; all data
are public government and university monitoring records.

## A. Rationale

Algal blooms in estuaries cause oxygen loss, fish kills and shellfish
closures. Managers find them by sampling on a fixed calendar. Existing
operational forecasts (NOAA Lake Erie, Gulf of Mexico HAB-OFS, California
C-HARM) cover a few places, depend on satellites or hydrodynamic models, and
predict toxin or cell abundance rather than the onset of a chlorophyll bloom.
Long Island Sound (LIS) and Narragansett Bay have decades of public
chlorophyll records, and thousands of continuous sondes worldwide now report
chlorophyll fluorescence every 15–60 minutes. Nobody has tested whether a
single model trained on one bay can forecast bloom onset at those sensors
without retraining.

## B. Research questions and hypotheses

Q1. Can a bloom-onset probability 7 days ahead be forecast from a station's
own recent chlorophyll, oxygen, temperature and salinity record?
H1: yes, with ranking skill (AUC) above 0.7 and precision above the base
rate (lift > 1) in held-out years.

Q2. What limits forecast precision: model class, features, data volume,
sampling frequency, or bloom rarity?
H2: bloom rarity. Prediction (pre-registered 2026-09-01): thinning
Narragansett's daily record to LIS's boat cadence will *not* reproduce LIS's
low precision, but re-thresholding Narragansett to LIS's bloom rate will.

Q3. Does a model trained on Narragansett Bay transfer to other water bodies
with no retraining?
H3: yes at marine and open-coast sondes after rescaling chlorophyll to the
target site's own distribution; retraining on local data will not beat it
except in tidal-fresh water with 3+ local years.

Q4. Does the skill hold prospectively, on forecasts issued before the outcome
is known?
H4: pooled onset lift over a fall season falls inside the retrospective band
for each site group (LIS buoys 2–3×; NERRS and Chesapeake 1.3–2.0×; ERDDAP
top sites 1.5–2.5×). Threshold, sites and scoring rule are frozen before the
first issuance (notes/PROSPECTIVE_PROTOCOL.md in the Narragansett repo).

## C. Data

- CT DEEP Long Island Sound Water Quality Monitoring, 1993–2025, 50 stations,
  monthly-to-biweekly boat samples (lab chlorophyll-a). Public, via UConn ERDDAP.
- RIDEM Narragansett Bay Fixed-Site Monitoring Network sondes, 2005–2023,
  18 stations, 15-minute cadence (fluorescence chlorophyll). Public annual files.
- UConn LISICOS buoys WLIS and EXRX, 2019–2026, ECO-FL fluorescence, live ERDDAP.
- Transfer targets: Maryland DNR Eyes on the Bay, NERRS SWMP (NCEI and IOOS
  ERDDAP), Cefas SmartBuoy (UK), IMOS National Reference Stations (Australia),
  NOAA GLERL Lake Erie buoys, USGS San Francisco Bay; plus 172 fixed sondes
  found by crawling 48 public ERDDAP servers.
- Satellites: MODIS-Aqua and Sentinel-3 OLCI chlorophyll via NOAA CoastWatch
  (feasibility only).

## D. Procedures

### D.1 Completed before plan approval: build and test (2025-06 to 2026-09)
1. Label: daily chlorophyll above threshold (10 µg/L lab; site 75th
   percentile for fluorescence) within the next 7 days (21 days for LIS boat data).
2. Features from the station's own history only: chlorophyll lags and
   rolling means, trend, anomaly vs station climatology, dissolved oxygen,
   temperature, salinity lags, month. No future information.
3. Models: logistic regression and gradient boosting; walk-forward
   year-by-year training; test years never touched during development.
4. Evaluation on onset rows only (today below threshold) so persistence
   cannot inflate skill; precision always reported beside base rate; lift =
   precision / base rate; 95% CIs by station-year clustered bootstrap
   (n=2000, seed 42); baselines: always-alert, persistence, climatology,
   simple chlorophyll rules.
5. Six pre-registered tests of H2 (cadence thinning, rarity re-thresholding,
   LIS buoys at 15-minute cadence, tuning search, lead-time sweep,
   sonde–lab calibration).

### D.2 Completed before plan approval: transfer and coverage (2026-09-03 to 09-05)
6. Export the Narragansett model; apply unchanged to six foreign networks
   and 100 ERDDAP sites after quantile-rescaling chlorophyll; score with the
   same protocol; compare against local refits three ways.
7. Satellite feasibility: coverage, agreement with sondes, and forecast
   skill at 300 m to 4 km.
8. Reproducibility audit: every result mapped to a script; environment
   rebuilt from scratch.

### D.3 New work under this plan: prospective test (start after approval)
9. Freeze model file (SHA-256 recorded), alert threshold 0.50, a list of 20
   live stations in four groups, each station's 75th-percentile threshold
   from its historical record, and the scoring rule. Publish the protocol
   before the first forecast.
10. Every Monday, pull the last 35 days from each live feed, issue one
    7-day onset probability per station, append to a ledger that is never
    edited, and commit it to a public repository (timestamped).
11. Seven days later, pull the outcome and score each forecast. Report
    precision, base rate, lift and recall with station-week clustered
    bootstrap CIs, only once a stratum has at least 30 scored rows and 5
    positive outcomes. First planned readout after 12 issuances.
12. Send the LIS buoy forecasts weekly to CT DEEP / UConn contacts; record
    any use or feedback.

### D.4 New work under this plan: comparison and value
13. Positioning table against operational HAB forecasts, each row sourced.
14. Decision-value analysis: for a fixed sampling budget, blooms caught by
    calendar sampling vs alert-directed sampling, in visits per confirmed bloom.
15. Independent check of the 2014 LIS chlorophyll step using MODIS satellite
    chlorophyll at the same stations (criterion pre-registered in the script).

## E. Risk and safety

Computational project on public data. No fieldwork, no specimens, no
personal data. Network requests to public servers are rate-limited and
identified with a research user agent.

## F. Data analysis

Python 3.13, scikit-learn 1.7.2, pandas 2.3.3 (pinned in environment.yml;
verified to build from scratch). All scripts, data-fetch procedures and
results are in two public GitHub repositories; every figure and number has a
named script. Statistical reporting rules: onset rows only; base rate
beside every precision; clustered bootstrap CIs; pre-registered criteria
stated in the script docstring before the first run; negative results kept.

## G. Bibliography (to be completed)

Kavanaugh et al. 2015, NOAA Tech. Rep. NOS CO-OPS 080 (GOMX HAB-OFS assessment).
Kavanaugh et al. 2013, NOAA Tech. Rep. NOS CO-OPS 073 (Eastern GOM HAB-OFS).
Stumpf et al. 2012, PLOS ONE 7(8): e42444 (Lake Erie interannual variability).
Stumpf et al. 2016, J. Great Lakes Res. (Lake Erie seasonal forecast).
Anderson et al. 2016, Harmful Algae (C-HARM skill assessment).
Perreira 2021; Reinl et al. 2023; Hattenrath-Lehmann & Gobler 2016
(see notes/LITERATURE_NOTES.md for full citations).
CT DEEP LIS Water Quality Monitoring Program data documentation.
RIDEM Narragansett Bay Fixed-Site Monitoring Network data documentation.
