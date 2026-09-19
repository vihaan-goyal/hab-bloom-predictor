# Research Plan (ISEF Form 1A structure) — draft 2026-09-05, amended 2026-09-19

Status: DRAFT for adult-sponsor review. The prospective test (Section D.3)
has NOT started; it begins the week after Form 1A is signed. Everything in
D.1–D.2 was completed before this plan was written and is labelled as such.

**This project has two halves.** (1) A *computational half*: forecasting
chlorophyll-a exceedances at monitoring stations from public government and
university monitoring records. It involves no human or vertebrate subjects, no
PHBAs and no hazardous materials. (2) A *bench half* (Sections B, C, D.5, E and
F below), added after the first draft: a closed 20 L laboratory mesocosm in
which a magnetite–kaolin–PAC clay is dosed and then retrieved on a magnet. The
bench half does involve hazardous materials and equipment — PAC powder (an
acidic aluminium coagulant), N52 neodymium magnets, a student-built 12 V
controller and pump used beside water, preservation acid handled by adults
only, and a live, non-toxic marine diatom culture.

**Amendment, 2026-09-19 (hazards).** The 2026-09-05 draft stated that the
project used no hazardous materials. That was true of the computational half
and is no longer true of the project as a whole. ISEF **Form 3 (Risk
Assessment)** is required for the hazardous chemicals, the home-built
electrical device and the protist culture, signed by the Adult Sponsor and by
the Designated Supervisor (the school chemistry teacher). No SRC pre-approval
beyond Form 3 is required: there are no human subjects, no vertebrates, no
potentially hazardous biological agents, no controlled substances and no rDNA.
Forms 1A, 1, 1B and 3 must be signed by **Fri Sep 25, 2026**; the first
hands-on work is Mon Sep 28. Section E is the operative risk assessment.

Throughout, the forecast target is a **chlorophyll-a exceedance** (a lab value
above 10 µg/L, or a station's own 75th percentile for fluorescence), not a
"harmful algal bloom"; and the bench device is tested for cell **removal and
retrieval in a closed tank**, never for bloom prevention or nutrient removal.

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
Model class and input resolution were tested last (2026-09-10, two
pre-registered neural-network tests, Narragansett findings §26–27): a 1-D
CNN on the raw 15-minute record scored reliably slightly *below* the
daily-feature gradient-boosting model on identical rows (paired ΔAUC −0.017
[−0.027, −0.002]), and a pooled six-site network with a learned site
embedding transferred worse than pooled boosting (AUC 0.70 vs 0.76). Model
class, features, data volume and sampling frequency are all now excluded;
rarity stands.

Q3. Does a model trained on Narragansett Bay transfer to other water bodies
with no retraining?
H3: yes at marine and open-coast sondes after rescaling chlorophyll to the
target site's own distribution; retraining on local data will not beat it
except in tidal-fresh water with 3+ local years.

Q4. Does the skill hold prospectively, on forecasts issued before the outcome
is known?
H4: pooled onset lift over a fall season falls inside the retrospective band
for each site group (LIS buoys 1.1–2.5×; NERRS and Chesapeake 1.3–2.0×; ERDDAP
top sites 1.5–2.5×). Threshold, sites and scoring rule are frozen before the
first issuance (notes/PROSPECTIVE_PROTOCOL.md in the Narragansett repo).

Q5 (bench half). When a forecast row alerts, does a magnetic clay dose remove a
Long Island Sound diatom at pre-bloom density, and how much of the clay comes
back out on a magnet instead of staying on the bottom? The hypotheses and their
bands were pre-registered on 2026-09-15, before any bench run, in
notes/SCIENTIFIC_METHOD.md Phase 11 (device record: notes/DEVICE_PROTOTYPE.md;
procedure: notes/LAB_PROTOCOL.md). They are reproduced here unchanged:

- **H11a (removal).** Magnetic PAC-kaolin at 0.2 g/L (product basis; stock route
  S or D per the Oct 30 amendment) removes *Skeletonema marinoi* (CCMP1332,
  Milford CT isolate) at 1e4 cells/mL by 70–95% at 5 h (control-normalised
  Sedgewick-Rafter counts, n = 3 batches), and within +/-15 points of plain
  PAC-kaolin at the same dose. Pass: mean RE >= 70% with the n = 3 CI lower
  bound > 50% and |magnetic − plain| <= 15 points. Mean >= 70% with a lower
  bound of 40–50% reads "consistent, underpowered", not failed; the interval is
  a t-interval on three batch REs (t = 4.30), and "consistent, underpowered" is
  the pre-registered likely reading. Below 50%: rerun at 0.6 g/L and report both.
- **H11b (recovery).** The settle–raster–column sequence recovers 75–95% of
  dosed magnetite-equivalent by pull test on homogenised pad aliquots and >= 70%
  of total dry product in the winning route's blank, 60–90% / 50–85% with
  culture, and <= 10% of plain PAC-kaolin (one plain tank blank, n = 1, reported
  as a description with its ~2–3% solids floor). Pass: mean
  magnetite-equivalent >= 70% over n = 3 tank runs, each >= 60%; total >= 50%;
  plain <= 10%. A blank below 70/80 is a design failure (gate), not a
  hypothesis failure.
- **H11c (dose-density), MVP version.** RE at 1e4 cells/mL rises monotonically
  by ordered means over 0.05, 0.1, 0.2 g/L (three means with t-intervals); D90
  by log-linear interpolation only when bracketed by two adjacent means,
  otherwise reported as "> 0.2 g/L" or "< 0.05 g/L". Pass: ordered means
  non-decreasing and, when bracketed, D90 in 0.05–0.2 g/L; an unbracketed D90
  reads "not testable". (Amendment A1, 2026-09-16, adds a fourth screening arm
  at 0.4 g/L; the band above is unchanged.)

What Q5 does **not** claim, as pre-registered: not bloom prevention, not
nutrient removal, not "no habitat impact", not field-ready.

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

Data generated at the bench (Q5; one CSV row per sample, notes/LAB_PROTOCOL.md
s9):
- Cell counts, Lugol-fixed, 1 mL Sedgewick-Rafter chamber, at t0, 5 h and 24 h,
  with mean chain length; five samples counted independently by two counters.
- Extracted chlorophyll-a: 250 mL on 47 mm GF/F, 90% acetone, 664/750 nm.
- Dry solids mass and magnetite-equivalent mass (0.001 g balance plus a
  magnet pull test calibrated daily against magnetite standards) for the magnet
  pad and for three loss fractions: tube rinses, floor rinse, and a 5 L
  supernatant pull.
- Dissolved oxygen, pH, salinity and temperature in each tank run and jar.
- Aluminium by ICP, one batch of about five samples (treated jars plus a
  seawater blank and a filter blank), run by a partner laboratory and reported
  with its reporting limit beside the 24 µg/L marine guideline.
- Controller SD-card log of every ledger poll and relay action; floc photographs
  and 750 nm floor turbidity reads.

## D. Procedures

### D.1 Completed before plan approval: build and test (2025-06 to 2026-09)
1. Label: daily chlorophyll above threshold (10 µg/L lab; site 75th
   percentile for fluorescence) within the next 7 days (21 days for LIS boat data).
2. Features from the station's own history only: chlorophyll lags and
   rolling means, trend, anomaly vs station climatology, dissolved oxygen,
   temperature, salinity lags, month. No future information.
3. Models: logistic regression and gradient boosting; walk-forward
   year-by-year training; test years never touched during development.
   Neural networks (tabular MLP, 1-D CNN on 7-day 15-minute windows, a
   hybrid, and a pooled multi-site MLP with site embedding) were tested
   under pre-registered criteria on 2026-09-10 and did not beat gradient
   boosting; they are reported as negative results, not used.
4. Evaluation on onset rows only (today below threshold) so persistence
   cannot inflate skill; precision always reported beside base rate; lift =
   precision / base rate; 95% CIs by station-year clustered bootstrap
   (n=2000, seed 42); baselines: always-alert, persistence, climatology,
   simple chlorophyll rules.
5. Eight pre-registered tests of H2 (cadence thinning, rarity re-thresholding,
   LIS buoys at 15-minute cadence, tuning search, lead-time sweep,
   sonde–lab calibration, and the two neural-network tests in item 3:
   sequence model on 15-minute data, pooled site-embedding network).

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

### D.5 New work under this plan: bench test of forecast-triggered clay (Oct–Dec 2026)

The operative procedure is `notes/LAB_PROTOCOL.md`; this is a summary. All work
is in the school laboratory with the Designated Supervisor present, and starts
only after Forms 1A, 1, 1B and 3 are signed.

16. *Setup.* A 10 gal glass aquarium at 20 L working volume is the mesocosm; jar
    tests use three 1.8 L jars at a time on a 12 V paddle rig. Tank water is
    Long Island Sound seawater collected at Milford or Stratford, gravity
    filtered through a 5 µm bag, stored cold and dark. Culture water is
    additionally pasteurised or 0.2 µm filtered. The test organism is
    *Skeletonema marinoi* CCMP1332, a non-toxic marine diatom purchased from
    the NCMA (Bigelow), grown in f/2 medium at 18–20 °C and diluted to 1e4
    cells/mL, a pre-bloom density.
17. *Clay blend and dose.* Dry blend of 8 g magnetite pigment, 25.3 g EPK kaolin
    and 6.7 g PAC powder (20% magnetite), weighed in a fume hood with gloves,
    goggles and a dust mask; a plain kaolin + PAC blend is the comparison arm.
    Blends are pasted to a 100 g/L stock 24 h before use. Nominal dose 0.2 g/L
    of dry blend (4 g per 20 L tank); the screen runs 0.05, 0.1, 0.2 and
    0.4 g/L.
18. *Run sequence.* A test ledger row is written by hand and read by the ESP32
    controller, which doses only on `status = ok`, `alert = 1`, `onset_row = 1`;
    it fires a peristaltic pump for 40 s and a paddle relay for 10 min while the
    student rapid-mixes for 60 s. Then 10 min slow mix (~50 rpm), 10 min settle,
    two wall-to-wall magnet-rake passes across the floor at 2 cm/s with release
    of the pad into a tray after each pass, one mid-depth column pass, and
    counts plus water-quality reads at t0, T20, T33, T93, 5 h and 24 h. Three
    clay-only blanks, a stock-route pilot, three jar batches and three tank runs.
19. *Workup.* The magnet pad and the three loss fractions are settled, dried at
    65 °C, weighed, ground and pull-tested for magnetite-equivalent mass; counts
    are read on a Sedgewick-Rafter chamber; chlorophyll is extracted in 90%
    acetone. Gates at Oct 9 (calibration), Oct 23 (recovery blank), Oct 30
    (stock route), Nov 6 (design freeze) and Dec 4 (controller) each decide
    whether the next stage runs.

**Containment.** This is a closed 20 L mesocosm on a bench in a school
classroom. Nothing is dosed, released or deployed in Long Island Sound or any
other natural water; the only fieldwork is collecting seawater in carboys from
shore. No organism leaves the laboratory alive: all culture and all tank
contents are bleached before disposal, aluminium floc is kept as lab solid
waste, and the bleached, diluted effluent is disposed of under school drain
policy. The field version of the device is documented as a concept only and is
explicitly *not performed* (notes/DEVICE_PROTOTYPE.md s5).

## E. Risk and safety

**Computational half.** Public data only; no fieldwork, no specimens, no
personal data. Network requests to public servers are rate-limited and
identified with a research user agent.

**Bench half — risk assessment** (source: notes/LAB_PROTOCOL.md s11 and
notes/DEVICE_PROTOTYPE.md s6). Exposed persons are the student and, at every
session, the Designated Supervisor; no other students handle materials.

| Hazard | Who is exposed | Control | Disposal |
|---|---|---|---|
| **PAC powder** — acidic aluminium coagulant, dust and eye/skin irritant | student weighing and blending | weighed in a fume hood; nitrile gloves, goggles, dust mask; kept dry and labelled; SDS on file | aluminium floc collected as lab solid waste; effluent bleached, diluted and drain-disposed per school policy |
| **Route D paste, pH ~3–4** | student pasting stock | gloves; small volumes (11–40 mL); made and used in the hood tray | neutralised with the bulk effluent, drain-disposed per school policy |
| **N52 magnets** — ~25 kg pull to steel per block, stacks repel at ~12 kgf; blocks pinch, shatter and snap together | student assembling the rake, anyone nearby | stacks assembled one at a time in a locked slotted frame; blocks stay in capped acrylic tubes in use; gloves and eye protection during assembly; phones, cards and any implanted medical device kept away; no magnets carried loose | retained; not waste |
| **12 V device beside water** — pump, paddle motors, controller | student operating the tank | everything touching water runs at 12 V from a fused supply behind a GFCI outlet; mains tools (drill, hot plate) on a separate bench away from the tank; no mains voltage near water | n/a |
| **Preservation acid** (sample acidification for ICP aluminium) | partner-lab staff or the chemistry teacher | handled **only** by the partner lab or the teacher; the student never handles the acid | partner lab's waste stream |
| **Live culture** — *Skeletonema marinoi* CCMP1332, a non-toxic marine diatom, BSL-1 | student and supervisor | closed carboys and tanks; standard lab hygiene, gloves, no mouth pipetting; nothing removed from the lab | all culture and tank contents bleached before disposal; no organism leaves the lab alive |
| **Lugol's iodine, 90% acetone (chlorophyll extraction)** | student | small volumes; gloves and goggles; acetone used in the hood, away from ignition sources | collected as lab waste per school policy |

**Supervision.** The Adult Sponsor signs Form 1. The **Designated Supervisor is
the school chemistry teacher**, named on Forms 1 and 3, trained in this
procedure and present for every hands-on session. Any work outside normal
school hours (the 5 h and 24 h reads) is covered by a signed after-hours
agreement among student, parent, Designated Supervisor and principal, with the
Designated Supervisor present; no hands-on work occurs before those forms are
signed.

**What is not involved.** No human subjects or human-subject data. No
vertebrate animals. No potentially hazardous biological agents: no pathogens,
no human or animal tissue, no blood or body fluids, no unidentified
environmental microbial cultures (the only organism is a purchased,
characterised, non-toxic marine diatom). No controlled substances. No
recombinant DNA or gene transfer. **Form 3 is therefore required for the
hazardous chemicals, the home-built electrical device and the protist culture;
no further SRC pre-review is expected beyond it.**

## F. Data analysis

Python 3.13, scikit-learn 1.7.2, pandas 2.3.3 (pinned in environment.yml;
verified to build from scratch; the neural-network tests add CPU PyTorch
2.12 in a second pinned environment, environment-nn.yml). All scripts, data-fetch procedures and
results are in two public GitHub repositories; every figure and number has a
named script. Statistical reporting rules: onset rows only; base rate
beside every precision; clustered bootstrap CIs; pre-registered criteria
stated in the script docstring before the first run; negative results kept.

**Bench analysis** (specified in notes/LAB_PROTOCOL.md s8, written and frozen
before any measurement exists):
- *Removal, per batch:* RE = 1 − (Ct/C0) / (Ct,control / C0,control) at 5 h, so
  every batch is corrected against its own untreated control jar.
- *H11a:* the mean of the three batch REs with a **t-interval at t = 4.30**
  (n = 3), read against the pre-registered band in Section B; the magnetic arm
  is compared with the plain arm at the same dose.
- *H11b:* recovery per tank run = magnetite-equivalent in the pad / magnetite
  dosed, with total dry solids recovered / solids dosed reported beside it, and
  a mass balance: dosed magnetite = pad + tube rinses + floor rinse + 5 L
  supernatant + unaccounted. The supernatant pull test is reported with its
  detection floor (8 mg = 1.0% of dosed magnetite) and its quantitative floor
  (20 mg = 2.5%) printed beside the number. A within-tank resuspension index
  (T33 count / T20 count, ±20% from counting) says whether the rake stirred
  cells back up.
- *H11c:* three batch means per dose with t-intervals, monotonicity judged on
  ordered means, D90 by log-linear interpolation only when bracketed by two
  adjacent means, otherwise reported as unbracketed or "not testable".
- *Counting quality:* mean absolute relative difference and Lin's concordance
  coefficient on five duplicate counts by two independent counters; Poisson
  intervals on every count.
- Measured recovery is compared with the pre-measurement simulation prediction
  (~95%, an upper bound; notes/DEVICE_SIMULATION.md). Every gate, decision and
  batch result is committed to git on the day it is produced, so the order of
  analysis and measurement is on the record.

## G. Bibliography

Forecasting and Long Island Sound ecology:

1. Kavanaugh et al. 2015, NOAA Tech. Rep. NOS CO-OPS 080 (GOMX HAB-OFS assessment).
2. Kavanaugh et al. 2013, NOAA Tech. Rep. NOS CO-OPS 073 (Eastern GOM HAB-OFS).
3. Stumpf et al. 2012, PLOS ONE 7(8): e42444 (Lake Erie interannual variability).
4. Stumpf et al. 2016, J. Great Lakes Res. (Lake Erie seasonal forecast).
5. Anderson et al. 2016, Harmful Algae (C-HARM skill assessment).
6. Perreira, S. (2021). *Long Term Nutrient and Chlorophyll a Dynamics across
   Long Island Sound and Impacts on Dissolved Oxygen Conditions within the
   Western Sound (1991–2019).* Thesis, CUNY Academic Works.
   https://academicworks.cuny.edu/cc_etds_theses/961
7. Reinl et al. (2023). "Blooms also like it cold." *Limnology and Oceanography
   Letters* 8: 546–564. doi:10.1002/lol2.10316. (Freshwater lakes only; cited
   for the cold-bloom mechanism, not for estuarine transfer.)
8. Hattenrath-Lehmann and Gobler (2016). *Historical Occurrence and Current
   Status of Harmful Algal Blooms in Suffolk County, NY, USA.* December 2016,
   121 pp.; free PDF via New York Sea Grant and suffolkcountyny.gov.
9. Wallace, M. K., Kudela, R. M., Gobler, C. J. (2025). "Microcystin
   contamination of shellfish along the freshwater-to-marine continuum within
   US mid-Atlantic and Northeast estuaries." *Harmful Algae* 145: 102860.
   doi:10.1016/j.hal.2025.102860.
10. CT DEEP Long Island Sound Water Quality Monitoring Program data documentation.
11. RIDEM Narragansett Bay Fixed-Site Monitoring Network data documentation.

Clay flocculation and magnetic retrieval (bench half):

12. Sengco, M. R. and Anderson, D. M. (2004). "Controlling harmful algal blooms
    through clay flocculation." *Journal of Eukaryotic Microbiology*.
    PubMed 15134251.
13. Yu et al. (2017). "Mitigation of harmful algal blooms using modified clays"
    (review). PubMed 29122242; open PDF hosted by the WHOI Anderson Lab.
14. Fan et al. (2026). Removal of *Microcystis aeruginosa* by magnetic clay
    minerals synergized with CPAM. *Polish Journal of Environmental Studies*
    35(3): 4139–4150. (Freshwater; the closest published magnetic-clay recipe.)
15. Ma et al. (2019). Fe3O4/CPAM flocculation of algae-laden raw water.
    *Journal of Cleaner Production* 248: 119276. (Freshwater.)
16. NOAA NCCOS, *Prevention, Control and Mitigation of HABs (PCMHAB)
    Programmatic Environmental Assessment*, final document
    (cdn.coastalscience.noaa.gov/page-attachments/about/pcm_hab_pea_finaldoc.pdf).
17. US Patent 10,822,258 B2 (clay spray device) and US Patent 10,981,813 B2
    (slurry concentrations and a monitoring-keyed dose table).
18. NCMA at Bigelow Laboratory, strain record CCMP1332 (*Skeletonema marinoi*,
    Milford CT isolate). https://ncma.bigelow.org/CCMP1332

Working notes behind these entries, including sources judged too incompletely
recorded to cite here: notes/LITERATURE_NOTES.md,
notes/CLAY_FLOCCULATION_RESEARCH.md, notes/CLAY_RETRIEVAL_RESEARCH.md.
