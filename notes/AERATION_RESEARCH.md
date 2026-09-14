# Aeration and oxygenation of estuarine water: practice, bottlenecks, and what a forecast-triggered prototype could do

Written 2026-09-14 from a web research pass (30+ fetches; research agent, this session).
Purpose: decide whether "forecast -> signal -> aerator" is a defensible tangible add-on for CSEF 2027.
Items marked *inference* are ours, not a source's. See notes/SCIENTIFIC_METHOD.md for how this connects to the model.

## 1. Who aerates estuarine or coastal water today

- **Rock Creek, MD (Chesapeake tributary), 1988-present.** Only long-running US tidal-estuary bubbler found. 800 m reach, 138 coarse diffusers, ~15,000 L/min air, ~74 ha influence. Runs June 1-Oct 1, daylight only; bottom water re-anoxifies "within one tidal cycle" when off. 2019 rebuild: two 213 m fine-bubble diffusers, 180 scfm, night shutdown for noise/energy. $285k install, ~$7k/yr, ~$1M replacement. Trigger: calendar. Effect: stopped H2S; increased methane venting (up to 1,500 umol/m2/d). [MD Sea Grant; Frontiers 2022; Maryland Reporter 2019]
- **Chesapeake main-stem proposal (2019, HydroLogics).** 16 O2 pipes, $10-20M build, ~$11M/yr electricity. Rejected on exchange, unproven plume physics, MeHg/N2O, fish-barrier grounds. EPA Bay Program: aeration only an add-on after nutrient cuts. Not built.
- **Baltimore Inner Harbor, Sept 2024 turnover.** ~24,000 fish dead; the National Aquarium wetland's small aerator acted as a localized refuge. Best real-world demo that a small aerator makes a *refuge*, not a fix. [WMAR]
- **Cardiff Bay, Wales (barrage-impounded lake).** GBP 3.4M (2000-01), compressors at five shore sites, ~800 bottom diffusers; statutory 5 mg/L DO floor checked by 9 continuous stations at 15 min; liquid-O2 barge backup ~5 t/day. 2023 minutes: 20-year-old system needs replacement, PhD studying reducing aeration. Not tidal. [BAM Nuttall; Cardiff Harbour Authority; Vale of Glamorgan minutes]
- **Salford Quays, Manchester (enclosed docks).** 16 Helixor air-lift mixers, shore compressor, 1986-90, with nutrient exclusion: lower bacteria/nutrients and "suppression of algal growth". 2010 renewal budget GBP 650k + 350k. [Radway 1988; Salford council]
- **Tidal Thames.** Two EA vessels (Thames Bubbler 1988, Thames Vitality 1997), each up to 30 t O2/day, ~GBP 250k/yr each. Trigger: reactive after storm overflows, DO analyzers on board, manual dispatch. Clearest operational, mobile, DO-triggered estuary program. [Servomex; gasworld]
- **Baltic BOX, Byfjorden SE, 2009-12.** Pumped oxic surface water into the anoxic basin (~2 m3/s pilot); deep O2 rose to ~110 umol/L. Full Baltic concept 10,000 m3/s, ~100 MW, ~2 bn SEK. Not implemented. [ISME J; phys.org; Marsys]
- **Savannah Harbor, GA.** Speece cones injecting 40,000 lb O2/day at two sites as dredging mitigation; pure-O2 injection into truly tidal water, permitted. [ECO2]
- **Hong Kong (Tolo/Victoria), Hood Canal.** No aeration programs found; pollution control / sediment bioremediation / monitoring instead.

## 2. Lake, pond and marina technology

- Diffused-air bubblers: ~1/2 hp per surface acre; $800-2,000 for 1-3 acres, $2-5k+ to ~9 acres (Kasco RobustAire RA1: 1/4 hp, 1-2 acres).
- Marina de-icers/bubblers (Kasco, Power House, Taylor Made): 1/4-2 hp, already permitted fixtures at CT marinas. *Inference:* the natural host for a prototype.
- Solar circulators (SolarBee/Medora, now Ixom): up to 10,000 gpm, 35-50 acres per unit; PA DEP 2004 flags mussel/barnacle cleaning in salt water.
- Hypolimnetic oxygenation (Speece cone, e.g. Camanche Reservoir 1993); destratification (Jordan Lake NC, USACE 2013: two platforms, 7.5 hp VFD motors).
- Nanobubbles (Moleaer): vendor claims 50% cyanobacteria reduction; no price published.
- **Does mixing suppress blooms?** Visser et al. 2016 (Aquatic Ecology 50:423-441): only for buoyant cyanobacteria, only if mixing is strong, deep and well distributed; standing crop often *increases* via nutrient mobilization. *Inference:* LIS/Narragansett summer blooms are diatoms/dinoflagellates, so mixing is a DO tool here, not bloom prevention.

## 3. Long Island Sound

No in-water aeration or mixing found for LIS or Stamford/Norwalk/Hempstead/Mamaroneck harbors. Only in-water engineering idea in the literature: Bowman's East River tidal locks. Strategy is the 2000/2001 nitrogen TMDL (58.5% cut by 2017) and CT DEEP's 2016 second-generation strategy. Hypoxic area: 208 sq mi (1987-99 mean) -> 83 sq mi (2021-25) -> 18.3 sq mi in 2025. Neither DEEP nor the Partnership mentions aeration.
Scale (*back-of-envelope*): ~65 km3 volume; 2021-25 hypoxic area = ~290 Rock Creek zones (1987-99 baseline ~730); a one-time 2 mg/L lift of a 5 m bottom layer over 215 km2 = ~2,200 t O2 = ~73 Thames-Bubbler-days, before sediment demand, at 3-5x Rock Creek's compressor depth.

## 4. Bottlenecks named by operators and papers

Reactive triggering (Thames after overflows; Rock Creek on a calendar). Energy and noise (Rock Creek night shutdown; Chesapeake $11M/yr; Baltic 100 MW). Tidal exchange (re-anoxifies in one tidal cycle). Side effects (methane, nutrient mobilization, MeHg/N2O, bubble curtains as fish barriers). Fouling and maintenance (barnacles on SolarBee; Cardiff replacement; Rock Creek $1M rebuild; DO-sensor fouling gives false low readings, In-Situ sells wipers for it). Regulatory framing: aeration is an add-on after load reductions.

## 5. Forecast- or sensor-triggered aeration that exists

- Aquaculture, setpoint-triggered, common: Eruvaka PondGuard (claims 20% energy saving), Reecotech (Vietnam), In-Situ RDO Trio -> PLC over Modbus. Boyd: $2,000-3,500 per 5 ha pond; energy savings alone do not pay back in 5 years. None use a forecast.
- Forecast-triggered, research only: 24 h DO forecast catching 91.8% of drops below 6 mg/L (Water 2026); 15-45 min and multi-hour ML forecasts; MPC in RAS holds DO within +/-0.4 mg/L.
- **No commercial product switches an aerator on a multi-day bloom forecast.** That is the gap.

## 6. Where a small device is plausible

Marinas, shellfish leases, small embayments, stormwater ponds. Vaudrey 2016: dawn hypoxia in inner LIS embayments (sensors 20 cm off bottom, 15 min, 8 embayments, 2014); N loads for 115 CT/NY embayments. CT DEEP logs menhaden kills Darien-New London from school-induced hypoxia. CT aquaculture ~$30M/yr, half oysters. Achievable claim: a measurable refuge patch (two DO loggers, one 1/4-1/2 hp aerator).

## 7. Regulatory (CT)

State: CT DEEP LWRD, Structures/Dredging/Fill; tracks = individual permit, Certificate of Permission (45/90 d), General Permits (90 d); 401 cert only if fill. Federal: USACE CT General Permit GP-41 (2021): GP 1 temporary structures (self-verification, removal within a season), GP 4 floats/misc structures, GP 6 utility lines, GP 16 aquaculture via CT Dept of Agriculture. *Inference:* a shore compressor + weighted air line + diffuser hung from an existing dock, seasonal and removable, is the easiest path.

## Forecast-triggered duty cycle (our number, 2026-09-14)

From the locked LIS test predictions (2023-2025, June-September station-visits): the model flags 15% of summer visits at threshold 0.50 (catching 60% of the visits followed by a bloom) and 7% at 0.60 (catching 48%). A Rock-Creek-style calendar runs 100% of the season. *Inference:* a forecast-triggered controller would run an aerator roughly one-seventh to one-fifteenth of the hours a calendar schedule does, with a corresponding cut in energy, noise and fouling exposure. Per-station share of summer visits flagged at 0.60: A4 0.57, B3 0.48, 02 0.44, C1 0.10.

## Bottom line

1. Sound-scale aeration is off the table (hundreds of Rock Creeks, tens of MW, no agency mentions it; nitrogen cuts already reduced hypoxia ~60%).
2. Aeration works and is operated today at hectare scale in enclosed/shallow water, or as mobile emergency oxygen; always as a DO tool, never bloom prevention.
3. Mixing does not suppress diatom/dinoflagellate blooms. Frame any device as pre-emptive DO support ahead of the post-bloom crash.
4. Every operational system is schedule- or setpoint-triggered. A forecast-to-relay controller on a marina de-icer or pond bubbler is a real gap and a feasible prototype.
5. Credible field test: refuge-patch experiment in a CT cove or marina slip, seasonal removable rig under DEEP COP/GP + USACE self-verification, with a grower or harbor commission as partner.

## Sources
- https://www.mdsg.umd.edu/fellowship-experiences/bubble-bubble-communitys-fix-bad-smells-offers-unique-research-opportunity
- https://www.frontiersin.org/articles/10.3389/fenvs.2022.866152/full
- https://marylandreporter.com/2019/07/01/bubbling-the-bays-dead-zone-breath-of-fresh-air-or-pipe-dream/
- https://www.wmar2news.com/local/heres-why-dead-fish-were-discovered-floating-in-baltimores-inner-harbor
- https://en.wikipedia.org/wiki/Water_oxygenation
- https://www.bam.com/en/press/press-releases/2000/11/nuttall-secures-ps34-million-cardiff-bay-aeration-scheme
- https://www.cardiffharbour.com/environmental-monitoring/
- https://www.valeofglamorgan.gov.uk/Documents/_Committee%20Reports/Cabinet/2024/24-02-08/Cardiff-Bay-Minutes.pdf
- https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1747-6593.1988.tb01334.x
- https://services.salford.gov.uk/solar_documents/CSSLMR221110D.DOC
- https://www.servomex.com/news/biologically-dead/
- https://www.gasworld.com/story/servomex-uses-oxygen-tech-to-help-inject-life-back-into-the-thames/
- https://www.nature.com/articles/ismej2014172
- https://phys.org/news/2011-05-oxygenation-life-baltic-sea.html
- https://www.marsys.se/baltic-deepwater-oxygenation-box/
- https://eco2tech.com/technical-library/o%E2%82%82-to-the-rescue-savannah-harbor-expansion-project-dissolved-oxygen-mitigation/
- https://www.tandfonline.com/doi/full/10.1080/10402381.2019.1648612
- https://americanaeration.com/products/kasco-ra1-robust-aire-diffused-aeration-system
- https://www.livingwateraeration.com/collections/pond-aerators
- https://www.savvyboater.com/de-icers-ice-eaters/
- https://files.dep.state.pa.us/water/Drinking%20Water%20and%20Facility%20Regulation/lib/watersupply/solarbee.pdf
- https://www.wateronline.com/doc/solarbee-v18-solar-powered-long-distance-0001
- https://www.moleaer.com/en-us/industries/lakes-ponds
- https://agris.fao.org/search/en/records/65df194d7c7033e84beccd19
- https://www.sciencedirect.com/science/article/abs/pii/B9780127518015500101
- https://portal.ct.gov/DEEP/Water/LIS-Monitoring/LIS-Hypoxia-and-Nitrogen-Reduction-Efforts
- https://lispartnership.org/about/our-mission/management-plan/hypoxia/
- https://seagrant.uconn.edu/2025/12/05/hypoxia-in-long-island-sound-drops-to-record-low-in-2025/
- https://in-situ.com/us/pond-aquaculture
- https://agriculture.cioreviewindia.com/vendor/2020/eruvaka_technologies
- https://reecotech.com.vn/en/continuous-monitoring-solution-for-dissolved-oxygen-in-shrimp-farming/
- https://www.globalseafood.org/advocate/automated-dissolved-oxygen-sensing-and-aerator-activation-in-aquaculture/
- https://doi.org/10.3390/w18131618
- https://link.springer.com/article/10.1007/s43926-025-00201-w
- https://link.springer.com/article/10.1007/s10499-026-02504-3
- https://vaudrey.lab.uconn.edu/wp-content/uploads/sites/1663/2017/02/Vaudrey_R-CE-34-CTNY_FinalReport_2016.pdf
- https://portal.ct.gov/DEEP/News-Releases/News-Releases---2020/Menhaden-Fish-Kills-Reported-Along-Connecticut-Shoreline
- https://www.foodmanufacturing.com/supply-chain/news/21614872/connecticut-oyster-industry-thriving-25-years-after-nearly-disappearing
- https://portal.ct.gov/DEEP/Coastal-Resources/Coastal-Permitting/Overview-of-the-Connecticut-Coastal-Permit-Program
- https://portal.ct.gov/-/media/DEEP/Permits_and_Licenses/Land_Use_Permits/LWRD/USACEctGeneralPermit2021
- https://www.nae.usace.army.mil/Missions/Regulatory/State-General-Permits/Connecticut-General-Permit/
