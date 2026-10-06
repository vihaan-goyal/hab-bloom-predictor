# Evidence review: low-dose hydrogen peroxide from a retrievable bag (Method 3)

Written 2026-09-25 for `notes/mitigation/03_PEROXIDE_BAG.md` and the shared loop in
`00_CONTROL_LOOP.md`. It builds on `notes/snowball/peroxides.md` and adds marine sources.

**How the sources were checked.** Every source below has a record retrieved in this session
from OpenAlex or Europe PMC by DOI: the title, authors, journal and abstract.
- **Full text** was read for Randhawa 2012, Mardones 2023, Weenink 2015 and Mehdizadeh Allaf 2026 (all Europe PMC open access).
- **Everything else is abstract only.** Numbers from those papers are marked "(abstract)".
- Numbers that come only from the earlier notes and were **not** re-checked here are marked "(unverified here)".

---

## 1. Summary and verdict

**What the evidence says**
1. **Most of the success is on freshwater cyanobacteria.**
   - Whole-lake treatment at 2 mg/L cut *Planktothrix* by 99% and kept it low for 7 weeks (Matthijs 2012).
   - Cyanobacteria are affected at about 10x lower doses than green algae and diatoms (Drábková 2007).
   - That selectivity is **weaker than claimed**: mixotrophs and diatoms can be as sensitive as cyanobacteria (Mehdizadeh Allaf 2023).
2. **The marine evidence is thin.** There is **one** brackish field success: Burson 2014, a creek treated at **50 mg/L** that strongly affected zooplankton. The rest is bottle and culture work:
   - small-celled brown tide (Randhawa 2012, 2013);
   - dinoflagellates (Mardones 2023; Hu 2022; Lee 2023);
   - ichthyotoxic flagellates (Moreno-Andrés 2023; Mehdizadeh Allaf 2026; Jasser 2025).
3. **Marine eukaryotic HAB taxa need 3-50 mg/L.** Measured doses:
   - flagellate EC50s: 3.4-7.9 mg/L;
   - *Karenia brevis*: 4.9-7.1 mg/L;
   - *Alexandrium* and other dinoflagellates: about 50 mg/L.

   **The only marine window at a low dose (1.6 mg/L) is for very small cells:** *Aureococcus* (about 2 µm) and *Micromonas*.
4. **Marine non-target harm starts at low doses:**
   - Northern shrimp had 33% delayed mortality after three 2-h pulses at **1.5 mg/L** (Bechmann 2019).
   - Freshwater *Moina*: LC50 2 mg/L (Reichwaldt 2012).
   - Killing dinoflagellates with H2O2 made the water **more** toxic to fish gill cells (Mardones 2023).

**Verdict for our bench**
- At a dose we can call low-risk (≤2.8 mg/L), H2O2 should **not** suppress *Prorocentrum micans* or large diatoms such as *Thalassiosira weissflogii*. At 6.4 mg/L they were not significantly inhibited (Randhawa 2012).
- *Phaeodactylum* (3.4 µm) is in between: 96% inhibited at 6.4 mg/L, and not significantly inhibited at 1.6 mg/L.
- So the honest experiment is a **size-selectivity and dose-response test**, not a demonstration that peroxide stops a dinoflagellate or diatom bloom.
- Peroxide is a credible loop treatment **only for small-celled blooms** (brown-tide type, picoplankton, cyanobacteria) in enclosed water.
- **Do not claim** bloom prevention, field readiness or non-target safety.

---

## 2. Master table

| # | Citation + link | Organism(s) | Setting | Dose / duration | Main result | Effective? |
|---|---|---|---|---|---|---|
| 1 | Matthijs et al. 2012, *Water Res* 46:1460 [doi](https://doi.org/10.1016/j.watres.2011.11.016) | *Planktothrix agardhii* (FW cyano) | Lab → enclosures → whole lake | 2 mg/L once | Cyanos and microcystin -99% in days; low for 7 wk; eukaryotes, zooplankton, macrofauna largely unaffected | Yes (FW cyano) |
| 2 | Burson et al. 2014, *Harmful Algae* 31:125 [doi](https://doi.org/10.1016/j.hal.2013.10.017) | *Alexandrium ostenfeldii* (dinoflagellate) | Lab → canal → whole brackish creek | 50 mg/L | Cells and cysts -99.8% in 48 h; zooplankton strongly affected; returned the next year | Yes, at high dose |
| 3 | Randhawa et al. 2012, *PLOS ONE* 7:e47844 [doi](https://doi.org/10.1371/journal.pone.0047844) | *Aureococcus* + 11 marine species incl. *Phaeodactylum*, *T. pseudonana*, *T. weissflogii*, *P. micans*, *Amphidinium* | Cultures + Barnegat Bay seawater microcosms | 0.8-6.4 mg/L; 1 wk (cultures), 72 h (microcosms) | 1.6 mg/L removed *Aureococcus* >90% in 24 h; larger cells spared; inhibition fell with cell size | Yes, for small cells |
| 4 | Randhawa et al. 2013, *Aquat Toxicol* 142-143:230 [doi](https://doi.org/10.1016/j.aquatox.2013.08.015) | *Aureococcus* | Cultures | 0.4-1.6 mg/L | Stationary-phase cells need 30-40% less H2O2 for 90% removal in 12 h | Yes |
| 5 | Mardones et al. 2023, *Microorganisms* 11:83 [doi](https://doi.org/10.3390/microorganisms11010083) | *A. catenella*, *Karenia selliformis*, *Lepidodinium*, *P. micans* | Cultures (salinity 25/33) + RTgill-W1 fish gill cells | 50-1000 ppm (mg/L) | 50 mg/L killed all 4 dinoflagellates; gill toxicity **rose**, even with non-toxic species | Kills cells, water more toxic |
| 6 | Lee et al. 2023, *Water Res* 242:120230 [doi](https://doi.org/10.1016/j.watres.2023.120230) | *Cochlodinium polykrikoides* | Lab; fish-farm intake water | O3, MnO4⁻, NaOCl, H2O2 compared | H2O2 was the least potent oxidant, but the most practical (no bromate); fish 72-h LC50 102.6 mg/L | Yes, but weakest |
| 7 | Hu et al. 2022, *Harmful Algae* 120:102347 [doi](https://doi.org/10.1016/j.hal.2022.102347) | *Karenia brevis* | Lab, natural bloom density | 3 peroxide products | 4.89-7.08 mg/L needed; decay faster with salinity, microbes and organics | Yes, at 5-7 mg/L |
| 8 | Moreno-Andrés et al. 2023, *J Hazard Mater* 452:131279 [doi](https://doi.org/10.1016/j.jhazmat.2023.131279) | *Prymnesium parvum*, *Heterosigma akashiwo* | Seawater cultures, 14 d | Dose-response | H2O2 EC50 6.67-7.08 mg/L, with a lasting effect | Yes, at about 7 mg/L |
| 9 | Mehdizadeh Allaf et al. 2026, *Microorganisms* 14:1086 [doi](https://doi.org/10.3390/microorganisms14051086) | *P. parvum*, *H. akashiwo*, *Fibrocapsa japonica* | Cultures (f/2, f/20), 24 h | Dose-response | 24-h EC50: 3.35 (*P. parvum*), 6.01 (*H. akashiwo*), 7.86 (*F. japonica*) mg/L; motility lost at sublethal doses | Partly |
| 10 | Jasser et al. 2025, *Water* 18:52 [doi](https://doi.org/10.3390/w18010052) | *P. parvum* + community | Canal water, lab | ≥14 mg/L single dose | Biomass and prymnesins cut; re-inoculation gave **higher** *P. parvum* and more toxin | Yes, then rebound |
| 11 | Hossain et al. 2024, *Harmful Algae* 138:102707 [doi](https://doi.org/10.1016/j.hal.2024.102707) | *K. brevis* | Lab; CaO2 inside PAC floc | 30 mg/L CaO2 | Photosynthesis suppressed, cells dead in 3-6 h | Yes (adds a flocculant) |
| 12 | Petasne & Zika 1997, *Mar Chem* 56:215 [doi](https://doi.org/10.1016/s0304-4203(96)00072-2) | Natural seawater microbes | South Florida coast / offshore | Natural H2O2 | First-order decay; half-life **<10 h coastal**, >120 h open ocean; mostly biological (<1 µm organisms) | n/a (fate) |
| 13 | Escobar Lux et al. 2019, *FACETS* 4:626 [doi](https://doi.org/10.1139/facets-2019-0011) | *Calanus* spp. (marine copepod) | Lab, 1 h pulses | 1h-LC50 48.6 (adult) / 214 (CV); 25h-LC50 30.6 / 77.1 mg/L | Escape response impaired at 0.5-1% of the sea-lice dose (about 8.5-17 mg/L); no escape reaction at all at 85 mg/L | n/a (non-target) |
| 14 | Bechmann et al. 2019, *Ecotox Env Saf* 180:473 [doi](https://doi.org/10.1016/j.ecoenv.2019.05.045) | Northern shrimp *Pandalus borealis* | Lab, 2 h pulses + recovery | 0.15, 1.5, 15 mg/L | 50% mortality (15 mg/L once); 33% (1.5 mg/L × 3 days); none at 0.15; deaths 2-4 d later; gill damage | n/a (non-target) |
| 15 | Escobar Lux & Samuelsen 2020, *Bull Env Contam Tox* 105:705 [doi](https://doi.org/10.1007/s00128-020-02996-6) | Northern krill | Lab, 1 h | 1h-LC50 32.5 mg/L | LC50 kept falling over 48 h after exposure (delayed mortality) | n/a (non-target) |
| 16 | Reichwaldt et al. 2012, *J Environ Eng* 138:607 [doi](https://doi.org/10.1061/(ASCE)EE.1943-7870.0000508) | *Daphnia carinata*, *Moina* | Lab acute | — | LC50 5.6 / 2.0 mg/L; NOAEC 3 / 1.5 mg/L | n/a (non-target) |
| 17 | Thoo et al. 2020, *Water* 12:1304 [doi](https://doi.org/10.3390/w12051304) | *Daphnia* in a natural plankton sample | Lab, **sodium percarbonate** | Graded SPC | Safe level <10 mg/L SPC (**2.8 mg/L H2O2**); large *Daphnia* died more | n/a (non-target) |
| 18 | Weenink et al. 2022, *Water Res* 225:119169 [doi](https://doi.org/10.1016/j.watres.2022.119169) | 3 cyanos + 23 non-targets | 24-h tests, species sensitivity distribution + 2 lakes | — | Most sensitive: cyanos + *Brachionus*, *Ceriodaphnia*, *Daphnia pulex*; higher dose/longer residence collapsed rotifers | n/a (window) |
| 19 | Weenink et al. 2015, *Front Microbiol* 6:714 [doi](https://doi.org/10.3389/fmicb.2015.00714) | *Planktothrix* lake community | Bottles, 3 densities | 2.5-50 mg/L | Dense water degraded H2O2 within hours; 2.5 mg/L cleared cyanos in diluted water | Yes, if biomass is low |
| 20 | Drábková et al. 2007, *Environ Sci Technol* 41:309 [doi](https://doi.org/10.1021/es060746i) | *Microcystis*, green alga, diatom *Navicula* | Lab, light × dose | Pulse | *Microcystis* EC50 0.27 mg/L in high light; greens and diatom 10x less sensitive; decay scales with light | Yes (mechanism) |
| 21 | Mehdizadeh Allaf et al. 2023, *Water Res* 234:119811 [doi](https://doi.org/10.1016/j.watres.2023.119811) | 4 FW algal divisions | Lab | H2O2 vs CuSO4 | Sensitivity: mixotrophs > cyanos > diatoms > chlorophytes; full selectivity "unattainable" | Caveat |
| 22 | Keliri et al. 2022, *Chem Eng J Adv* 11:100318 [doi](https://doi.org/10.1016/j.ceja.2022.100318) | *Microcystis* | Bench; **CaO2 in fabric bags** | 0.5-2 g/L CaO2 | 2 g/L released up to 12 mg/L H2O2 by 24 h (3 of 4 fabrics same as loose); RFU 8000 → <1000 | Yes (FW) |
| 23 | Kober et al. 2026, *ACS ES&T Water* 6:1716 [doi](https://doi.org/10.1021/acsestwater.5c01257) | Lake Erie cyanobacteria | Microcosm, 14 d; **hydrogel-barrier buoy** | Commercial H2O2 algaecide | First-order release set by gel thickness; release >1 month; sustained effect on early-stage blooms | Yes (FW, early) |
| 24 | Lusty & Gobler 2020, *Toxins* 12:428 [doi](https://doi.org/10.3390/toxins12070428); 2022, *J Environ Sci* 124:522 [doi](https://doi.org/10.1016/j.jes.2021.11.031) | Long Island lake / pond cyanos | 4 L bottles; mesocosms; whole pond | 4 mg/L; 8 mg/L | Cyanos 85% → 29% of community; whole pond rebounded ≤2 wk; fecal-indicator bacteria **rose** | Partly |
| 25 | Yang et al. 2018, *Environ Pollut* 240:590 [doi](https://doi.org/10.1016/j.envpol.2018.05.012) | 4 cyanobacteria | Lab 5 d + pond 7 d | Graded | EC50 0.41 (filamentous) vs 5.06 mg/L (*Microcystis*); 20 mg/L hurt zooplankton most | Yes, species-dosed |
| 26 | Hancock et al. 2025, *Appl Environ Microbiol* 91:e01950-25 [doi](https://doi.org/10.1128/aem.01950-25) | *Microcystis* | River field; **sodium percarbonate** granules vs liquid | Field | Chl-a -81% / -90% short term; no lasting effect in flowing water | Short-term |
| 27 | Lürling et al. 2025, *Harmful Algae* 149:102930 [doi](https://doi.org/10.1016/j.hal.2025.102930) | *Microcystis* | Lab; 5 peroxide products incl. CaO2, percarbonate | 3, 10 mg/L | At 600 µg/L chl, 3 mg/L: CaO2 and percarbonate let chl recover; all worked at 10 mg/L | Yes, product-dependent |

27 records in total: 14 marine or brackish (#2-15) and 13 freshwater or delivery studies.

---

## 3. Per-source detail

### Marine and brackish efficacy

**#1 Matthijs 2012 (anchor; freshwater).**
- **Hypothesis:** cyanobacteria are more H2O2-sensitive than eukaryotes, so a low whole-lake dose is selective.
- **Dose and delivery:** 2 mg/L (60 µM), liquid, spread with a "water harrow".
- **Results (abstract):**
  - Photosynthetic vitality fell >70% within hours.
  - Cyanobacteria and microcystin fell 99% within a few days and stayed low for 7 weeks.
  - Green algae, cryptophytes, chrysophytes, diatoms, zooplankton and macrofauna were largely unaffected.
  - H2O2 was gone within a few days.
- **Relevance:** the dose benchmark (2 mg/L). It is freshwater, and the target was a cyanobacterium.

**#2 Burson 2014.**
- **Setting:** *A. ostenfeldii* at more than 1 million cells/L in a brackish Dutch creek. Lab dose finding came first, then a canal test.
- **Dose:** 50 mg/L across the whole creek.
- **Results (abstract):**
  - Vegetative cells and pellicle cysts -99.8% within 48 h; PSP toxins below 15 µg/L.
  - Zooplankton were "strongly affected"; macroinvertebrates and fish minimally.
  - The bloom recurred at lower levels the next year.
- **Relevance:** the only marine/brackish field success, at **25x the freshwater dose**. Its lab dose-response numbers were not in the retrieved text.

**#3 Randhawa 2012 (full text read). The most relevant source for our bench.**
- **Species (all NCMA):** *Aureococcus*, five diatoms (*Phaeodactylum*, *Minutocellus*, *T. pseudonana*, *Skeletonema*, *T. weissflogii*), *Micromonas*, *Dunaliella*, *Isochrysis*, *Emiliania*, *Amphidinium*, *P. micans*.
- **Methods:** 12 species in culture; Barnegat Bay seawater microcosms. Measured with a Turner Trilogy in vivo fluorescence reader, acetone chl-a and a Coulter counter.
- **Doses:** 0.8, 1.6, 3.2 and 6.4 mg/L, from a 30% reagent-grade stock.
- **Results at 1.6 mg/L:**
  - *Aureococcus*: 24-h EC50 0.91 mg/L (3-h EC50 1.39). Chl-a fell >90% by 24 h at ≥1.6 mg/L. At 0.8 mg/L the inhibition was transient.
  - Of the other 11 species, only *Micromonas* was eradicated (>90% fluorescence loss in 24 h).
  - *Amphidinium* grew 17% slower. All others showed no significant inhibition.
- **Table 2, % growth inhibition at 6.4 mg/L (mean of 24/48/72 h):**
  - *Phaeodactylum* (3.4 µm): **96.0%**
  - *T. pseudonana* (3.8 µm): **71.5%**
  - *Skeletonema* (6.6 µm): 9.6% (not significant)
  - *T. weissflogii* (11 µm): 2.6% (not significant)
  - *Amphidinium* (9 µm): 95.7%
  - ***P. micans* (45 µm): 11.2% (not significant)**
  - *Dunaliella*: 1.3% (not significant)
  - *Isochrysis* 98.6%; *Emiliania* 95.9%
- **Fitted relationship:** % inhibition = 0.688 - 0.0561 × cell diameter (µm) + 0.00262 × (H2O2 : chl-a weight ratio); R² = 0.69.
- **Microcosms:** diatoms and greens dipped, then exceeded the controls within 72 h. Cyanobacteria were down about 50%.
- **Mechanism (discussion):** cell size, cell-wall structure (silica, theca) and ROS scavenging (catalase, peroxidases, glutathione, ascorbate).
- **Relevance:** gives dose-specific predictions for **our exact diatoms and our dinoflagellate**.

**#4 Randhawa 2013 (abstract).**
- **Setting:** *Aureococcus* at 1.6×10⁶ cells/mL, 0.4-1.6 mg/L.
- **Result:** stationary-phase cells had weaker ROS scavenging and needed 30-40% less H2O2 for 90% removal within 12 h.
- **Relevance:** it cuts against "treat early". Early (exponential-phase) cells are *harder* per cell to kill; see Conflicts.

**#5 Mardones 2023 (full text read).**
- **Setting:** cultures in L1 medium at 15 °C, salinity 33. Dinoflagellates at 1000 cells/mL, crossed with 0-1000 ppm H2O2.
- **Results:**
  - 50 ppm was the lowest dose tested. It left photosynthetic efficiency at 12% and cell viability at 6.4%.
  - H2O2 alone was cytotoxic to RTgill-W1 cells, depending on dose and time. Below 200 ppm that toxicity faded after 24 h.
  - Adding H2O2 to **non-toxic *P. micans* and *Lepidodinium* increased gill-cell toxicity**. The proposed cause is aldehydes from lipid peroxidation, which can persist for days.
  - The discussion cites 30 ppm as effective on *Cochlodinium* in Japan (secondary).
- **Relevance:** no data below 50 mg/L, and a "dead bloom ≠ safe water" warning that applies to our *P. micans*.

**#6 Lee 2023 (abstract).**
- **Comparison:** ozone, permanganate, hypochlorite and H2O2 against *C. polykrikoides*. Potency ran O3 > MnO4⁻ > NaOCl > H2O2.
- **Fish safety:** red sea bream 72-h LC50 was 102.6 mg/L for H2O2, against 0.39-1.35 mg/L for the other oxidants.
- **By-products:** ozone and hypochlorite made bromate in seawater; H2O2 did not.
- **Relevance:** H2O2 is the weakest oxidant but the widest fish-safety margin. The effective H2O2 dose was not in the abstract.

**#7 Hu 2022 (abstract).**
- **Result:** *K. brevis* at 1.79×10⁷ cells/L needed 4.89-7.08 mg/L of the peroxide products; copper needed only 0.31-0.34 mg Cu/L.
- **Decay:** salinity, microbes and particles ≥0.2 µm sped up H2O2 decay. The most stable product (Oximycin P5) lost **0.467 mg/L per day** in natural seawater.
- **Note:** the authors call for pilot studies on marine non-targets.

**#8 Moreno-Andrés 2023 (abstract).**
- **Setting:** ballast-water context; 14-day concentration-response in seawater.
- **Result:** H2O2 EC50 6.67-7.08 mg/L, with a "maintained" effect. Peroxymonosulfate and peracetic acid were stronger but short-lived.
- ***Heterosigma*** was more resistant than *Prymnesium* to the other oxidants, but not to H2O2.

**#9 Mehdizadeh Allaf 2026 (full text read).**
- **Result:** 24-h H2O2 EC50 was *P. parvum* 3.35 ± 0.17, *H. akashiwo* 6.01 ± 1.51 and *F. japonica* 7.86 ± 2.94 mg/L.
- **Swimming:** motility and mean squared displacement fell at sublethal doses.
- **Relevance:** swimming speed is a cheap early endpoint for a motile dinoflagellate under a microscope.

**#10 Jasser 2025 (abstract).**
- **Setting:** canal water; one dose of ≥14 mg/L.
- **Result:** *P. parvum* biomass and prymnesins fell, with limited harm to other phytoplankton.
- **Rebound:** re-inoculating bloom water gave *higher* *P. parvum* biomass and toxin, possibly from nutrient release.
- **Relevance:** supports the loop's cool-down watch and a re-inoculation arm.

**#11 Hossain 2024 (abstract).**
- **Setting:** CaO2 built into a polyaluminum-chloride floc.
- **Result:** 30 mg/L CaO2 suppressed *K. brevis* photosynthesis and killed cells in 3-6 h. The floc concentrates the oxidant at the cells.
- **Relevance:** it depends on a flocculant, which is not retrievable, so it is not our design.

### Fate and decay

**#12 Petasne & Zika 1997 (abstract).**
- Natural seawater H2O2 decays by first-order kinetics. Half-life is **<10 h in coastal water** and >120 h offshore.
- Decay is mainly biological, by organisms <1 µm (e.g. *Vibrio*, *Synechococcus*).
- **Relevance:** a bench jar with a culture and its bacteria should lose most of a dose within a day. Sterile, low-biomass jars will be slower (see Randhawa: in culture, 1.6 mg/L fell to 0.7 mg/L after 1 day, citing its ref 33).

**#19 Weenink 2015 (full text read).**
- **Densest samples:** all H2O2 was gone within 24 h, except at 50 mg/L (6.3 mg/L left).
- **Diluted samples:** 24.9 of 50 mg/L remained at 24 h. At 4 h, 0.4 of 2.5 mg/L and 4.2 of 5 mg/L remained.
- **Working hypothesis:** a treatment works when cells see **≥2 mg/L for 5 daylight hours**.
- **Result:** in diluted water, 2.5 mg/L removed the cyanobacterial signal and left the greens and diatoms.

### Non-target effects (the dose ceiling)

**#13-15 Marine crustaceans (abstracts).** These tests come from sea-lice treatments, which use 1500-1700 mg/L baths.
- ***Calanus* copepods:** 25-h LC50 30.6 mg/L (adults). Escape response already fell at 0.5-1% of the treatment dose. The authors warn that "safe" values underestimate the harm.
- **Northern shrimp:** 1.5 mg/L for 2 h on 3 days caused 33% mortality, gill damage and 66% lower feeding 12 days later. No mortality at 0.15 mg/L. **Deaths came 2-4 days after exposure.**
- **Krill:** 1h-LC50 32.5 mg/L, falling with time over 48 h after exposure.

**#16 Reichwaldt; #17 Thoo; #18 Weenink 2022 (freshwater zooplankton).**
- *Moina* NOAEC 1.5 mg/L; *Daphnia* NOAEC 3 mg/L (Reichwaldt).
- Percarbonate safe level <10 mg/L SPC = 2.8 mg/L H2O2 (Thoo).
- Rotifers and small cladocerans are as sensitive as cyanobacteria (Weenink 2022).
- Exact species-sensitivity EC50s were not in the retrieved text.

**#24 Lusty & Gobler 2022.** Fecal-indicator bacteria rose after H2O2 in a pond ("pollution swapping").

### Mechanism and selectivity

**#20 Drábková 2007.**
- *Microcystis* EC50 0.27 mg/L in high light. Green alga and diatom needed about 10x more.
- Decay was proportional to irradiance and depended on the species.

**#21 Mehdizadeh Allaf 2023.** Diatoms and mixotrophs can be nearly as sensitive as cyanobacteria.

**#25 Yang 2018.** Filamentous cyanobacteria had an EC50 of about 0.41 mg/L, against 5.06 for *Microcystis*.

### Delivery (bag, slow release, percarbonate)

**#22 Keliri 2022.**
- CaO2 granules (0.5, 1, 2 g/L) in four fabrics. Three fabrics released as much as loose granules: up to 12 mg/L at 24 h from 2 g/L.
- Only about **0.6% of the CaO2 mass appeared as H2O2 by 24 h** (12 mg/L ÷ 2000 mg/L; our arithmetic). The release is slow and incomplete.
- pH was not in the abstract.

**#23 Kober 2026.**
- A hydrogel diffusion barrier gave predictable **first-order** release for more than a month, tuned by gel thickness, loading and area/volume.
- It had a sustained effect on early-stage blooms in 14-day microcosms.
- **Relevance:** the closest precedent for a controllable, retrievable release device.

**#26 Hancock 2025.**
- Floating percarbonate granules versus liquid H2O2 in a river: similar short-term knockdown.
- Three treatments in 2 weeks failed, because the water kept exchanging.

**#27 Lürling 2025.**
- At high biomass and 3 mg/L, **CaO2 and the percarbonate product let chlorophyll recover** where liquid H2O2 did not.
- All products worked at 10 mg/L.

---

## 4. Aggregated data

### 4a. Effective dose by taxon (mg/L H2O2)

| Taxon (size) | Water | Effective dose / EC50 | Source |
|---|---|---|---|
| Filamentous cyanobacteria | FW | EC50 ≈ 0.41; field 1.3-2.5 | Yang 2018; Matthijs 2012 |
| *Microcystis* | FW | EC50 0.27 (high light) to 5.06; field ≥6.7 | Drábková 2007; Yang 2018 |
| *Aureococcus* (≈2 µm) | Marine | 24-h EC50 0.91; ≥1.6 for >90% | Randhawa 2012 |
| *Micromonas* (≈1.4 µm) | Marine | ≤1.6 eradicates | Randhawa 2012 |
| *Phaeodactylum* (3.4 µm) | Marine | Not significant at 1.6; 96% inhibited at 6.4 | Randhawa 2012 |
| *T. pseudonana* (3.8 µm) | Marine | 71.5% at 6.4 | Randhawa 2012 |
| *T. weissflogii*, *Skeletonema* (6.6-11 µm) | Marine | Not significant at 6.4 | Randhawa 2012 |
| *Prymnesium parvum* | Brackish | EC50 3.35 (24 h); 6.67-7.08 (14 d); ≥14 in canal water | Mehdizadeh Allaf 2026; Moreno-Andrés 2023; Jasser 2025 |
| *Heterosigma*, *Fibrocapsa* | Marine | EC50 6.0-7.9 | Mehdizadeh Allaf 2026; Moreno-Andrés 2023 |
| *Karenia brevis* | Marine | 4.89-7.08 | Hu 2022 |
| *Amphidinium carterae* (9 µm) | Marine | 17% slower growth at 1.6; 95.7% at 6.4 | Randhawa 2012 |
| ***Prorocentrum micans* (45 µm)** | Marine | **Not significant at 6.4; killed at 50** | Randhawa 2012; Mardones 2023 |
| *Alexandrium* spp., *Karenia selliformis* | Marine/brackish | 50 | Burson 2014; Mardones 2023 |

**Rule of thumb from the table:** the dose needed rises with cell size, and in marine water it is roughly 3-25x the freshwater cyanobacterial dose.

### 4b. Decay

| Condition | Decay | Source |
|---|---|---|
| Coastal seawater, natural | Half-life <10 h | Petasne & Zika 1997 |
| Open ocean | Half-life >120 h | Petasne & Zika 1997 |
| Dense lake sample, 2.5-20 mg/L | Gone within 24 h | Weenink 2015 |
| Diluted lake sample, 50 mg/L | 50% left at 24 h | Weenink 2015 |
| Most stable product in seawater | -0.467 mg/L per day | Hu 2022 |
| Rivers, lakes, marina after field dosing | Background by the next day to a few days | Hancock 2025; Matthijs 2012; Burson 2014 |

**What drives decay:** biomass and bacteria, and light (faster decay in brighter light; Drábková 2007).

### 4c. Non-target thresholds

| Organism | Value (mg/L) | Exposure | Source |
|---|---|---|---|
| *Pandalus* shrimp | No effect 0.15; 33% delayed mortality at 1.5 | 2 h × 3 d | Bechmann 2019 |
| *Moina* | NOAEC 1.5; LC50 2.0 | Acute | Reichwaldt 2012 |
| *Daphnia* | Safe level 2.8 (as percarbonate) | — | Thoo 2020 |
| *Daphnia carinata* | NOAEC 3; LC50 5.6 | Acute | Reichwaldt 2012 |
| *Calanus* adults | LC50 30.6 | 25 h | Escobar Lux 2019 |
| Northern krill | LC50 32.5 | 1 h | Escobar Lux & Samuelsen 2020 |
| Red sea bream juveniles | LC50 102.6 | 72 h | Lee 2023 |
| Fish gill cells | Toxicity **increases** when dinoflagellates are lysed | ≥50 | Mardones 2023 |

### 4d. Conflicts
1. **Early vs late treatment.**
   - Against early: stationary (late) cells need 30-40% less H2O2 (Randhawa 2013).
   - For early: low biomass decays H2O2 more slowly and scavenges less (Weenink 2015; Lürling 2025), and early sustained release worked (Kober 2026).
   - **Net: unknown.** It is a real test for arm B vs arm C.
2. **"Selective" vs not selective.**
   - Selective: Matthijs 2012, Drábková 2007.
   - Not selective: Mehdizadeh Allaf 2023 (diatoms and mixotrophs are sensitive). Randhawa 2012 reconciles the two: **size**, not taxon, predicts sensitivity in marine species.
3. **Solid vs liquid.**
   - Equal: bags released like loose granules (Keliri 2022).
   - Worse: CaO2 and percarbonate were less effective at high biomass (Lürling 2025).
4. **Lab vs field.** High knockdown in enclosed water, but rebound in ≤2 weeks where water exchanges (Lusty & Gobler 2022; Hancock 2025).

---

## 5. Hypotheses for our experiment (falsifiable, fixed before the run)

**P1 (size selectivity).** At 1.6 mg/L (liquid, one dose, lights on):
- a small-cell alga (*Micromonas*-type) loses ≥90% of in vivo fluorescence versus control by 24 h;
- *T. weissflogii* and *P. micans* stay within 20% of control at 72 h.

Falsified if the small alga loses <50%, or either large species loses >30%. (Randhawa 2012)

**P2 (*Phaeodactylum* dose-response).** Inhibition at 72 h is <30% at 1.6 mg/L and >80% at 6.4 mg/L, so the EC50 lies between them. (Randhawa 2012, Table 2)

**P3 (dinoflagellate resistance).** *P. micans* growth inhibition is <20% at every dose ≤6.4 mg/L. If P3 holds, peroxide is **not** a viable loop treatment for dinoflagellates at non-target-safe doses. (Randhawa 2012; Mardones 2023)

**P4 (bag = liquid).** Two checks:
- The bag's measured H2O2 at 4 h and 24 h is within ±30% of the liquid arm at the same target.
- Inhibition of the target alga differs by <15 percentage points.

(Keliri 2022; against it, Lürling 2025)

**P5 (decay).** In culture jars, H2O2 half-life is 4-48 h, and it is shorter in the higher-biomass jars than in the medium-only jars. (Petasne & Zika 1997; Weenink 2015)

**P6 (non-target).** *Artemia* survival at 24 h **and 96 h** is ≥80% of control at ≤2.8 mg/L.
- Delayed deaths are expected if any appear (Bechmann 2019).
- No *Artemia* LC50 for H2O2 was found, so this is new data, not a replication.

**P7 (loop timing).** Arm B (forecast-triggered) reaches the OFF rule using less total H2O2 than arm C (late) for the small-cell target. Randhawa 2013 predicts the opposite, so either result is informative.

---

## 6. Mechanisms
- **Oxidative stress.** H2O2 is uncharged, crosses membranes, and inside the cell forms hydroxyl radicals (Fenton chemistry with iron). These damage photosystem II (Fv/Fm falls within hours), lipids (lipid peroxidation) and proteins (Drábková 2007; Hossain 2024; Mardones 2023).
- **Light dependence.** H2O2 plus bright light hits photosystem II harder. Decay also speeds up with light (Drábková 2007). Weenink 2015's working rule is about 2 mg/L for 5 daylight hours.
- **Defences decide sensitivity.** Catalase, peroxidases, glutathione and ascorbate break H2O2 down.
  - Cyanobacteria and very small cells have little defence per cell and a high surface-to-volume ratio.
  - Large, thecate or silicified cells resist (Randhawa 2012).
  - Stationary-phase cells have weaker scavenging (Randhawa 2013).
- **Community protection.** Dense biomass and bacteria destroy H2O2 quickly, so sparse targets get the full dose (Weenink 2015; Petasne & Zika 1997).
- **Secondary harm.** Lysed dinoflagellates release fatty acids, whose oxidation forms aldehydes that are toxic to gill cells (Mardones 2023). Dead cells can release nutrients that fuel a rebound (Jasser 2025).

---

## 7. Design numbers we adopt

| Item | Value | Source / reason |
|---|---|---|
| **`X` (ON time)** | **24 h**, then pull the bag | >90% small-cell kill by 24 h (Randhawa 2012); coastal half-life <10 h (Petasne & Zika 1997); CaO2 release peaks by 24 h (Keliri 2022) |
| **Pilot dose series** (liquid) | 0, 0.8, 1.6, 3.2, 6.4 mg/L; triplicates | Randhawa 2012 series, which lets P1-P3 be compared directly |
| **Loop target dose** | **1.6 mg/L** at 1 h | Lowest dose effective on small cells (Randhawa 2012); below *Daphnia* NOAEC 3 and the 2.8 safe level (Reichwaldt 2012; Thoo 2020) |
| **Hard cap (residual)** | **2.8 mg/L** → pull the bag early | Thoo 2020. Note that Bechmann 2019 saw shrimp harm at 1.5 mg/L repeated, so 2.8 is not "safe" for marine crustaceans |
| **Exposure check** | Aim for ≥1.5 mg/L during the first 5 h of light | Weenink 2015 working hypothesis (2 mg/L × 5 h), scaled to our lower target |
| **Timing** | Dose at lights-on, under the same PAR in every jar | Light dependence (Drábková 2007) |
| **`MAX_ON`** | 3 bags per event (lowered from 4) | Repeated 1.5 mg/L pulses caused delayed crustacean deaths (Bechmann 2019) |
| **Delivery A: sodium percarbonate** | SPC mass = target × volume ÷ 0.28 (e.g. 1.6 mg/L in 2 L ≈ 11.4 mg). Weigh on a 0.001 g balance, or dose from a fresh SPC stock | 2.8 mg/L H2O2 per 10 mg/L SPC (Thoo 2020); pure SPC is 32.5% H2O2 by formula |
| **Delivery B: CaO2 bag** | Calibrate first: 0.25, 0.5, 1, 2 g/L in plain artificial seawater, with strips at 1, 4, 12, 24 h | Keliri 2022: 2 g/L → 12 mg/L at 24 h (freshwater). Linear scaling suggests about 0.5 g/L for 2.8 mg/L, **untested in seawater** |
| **Bag note** | SPC dissolves fast, so a percarbonate bag gives a pulse, not slow release; retrieving it removes only undissolved solid. For true slow release, consider a hydrogel barrier | Hancock 2025 (granule pulse); Kober 2026 (gel release) |
| **Controls** | Untreated; liquid H2O2 at the same target; **empty bag**; **sodium carbonate** at the SPC-equivalent mass (pH and carbonate control); for CaO2, a Ca(OH)2 pH-matched control | Separates the peroxide effect from fabric, carbonate and pH |
| **Re-inoculation arm** | Day 5: add 10% untreated culture to treated jars | Jasser 2025; Weenink 2015 (opposite outcomes) |
| **Cool-down `Y`** | 5 days bench (as in `00`), and log regrowth | Rebound in ≤2 weeks (Lusty & Gobler 2022) |
| **Safety limits** | Residual >2.8 mg/L; pH outside 7.6-8.6; DO <4 mg/L; *Artemia* survival >20 points below control **at 24 h or 96 h** | `00_CONTROL_LOOP.md`; delayed mortality (Bechmann 2019; Escobar Lux 2020) |
| **Measurements** | H2O2 strips at 1, 4, 12, 24, 48 h; fluorescence; cell counts by size class; Fv/Fm if available; motility of *P. micans* (video) | Randhawa 2012; Mehdizadeh Allaf 2026 (motility endpoint) |

**Recommended organisms**
- Primary target: a **small-celled non-toxic marine alga**, *Micromonas* or *Nannochloropsis*-type.
- Test species: ***Phaeodactylum*** (the P2 dose-response).
- Resistant controls: ***T. weissflogii*** and ***P. micans*** (P1, P3).

This is more honest than asking peroxide to clear the diatom or dinoflagellate bloom.

**Change from `03_PEROXIDE_BAG.md`:** its dose rule (0.06 mg/L per µg/L chlorophyll) comes from Buley 2023 on freshwater *Microcystis* at 82-371 µg/L chlorophyll (unverified here). For marine cells, Randhawa's fitted relationship says **cell size** matters more than the dose-per-chlorophyll ratio. Use the fixed 1.6 mg/L target and the pilot curve instead.

---

## 8. Gaps, open questions, and school-lab chemical safety

### Gaps
1. **No marine field trial below 50 mg/L**, and no open-coast trial at all. Our results transfer only to enclosed water.
2. **No *Artemia* H2O2 LC50** was found. Marine crustacean data come from sea-lice work (1-2 h pulses at high doses) and are not a match for a 24 h pulse at 1-3 mg/L.
3. **CaO2 release in seawater** (salinity 30, pH 8) is unmeasured. Calcium and carbonate chemistry may change the yield. Keliri's pH data were not retrieved.
4. **Percarbonate's carbonate load** in small jars: pH drift is probably small in seawater at mg/L levels, but it has to be measured, hence the carbonate control.
5. **No data on *P. micans* below 50 mg/L except Randhawa's 1.6 and 6.4 mg/L.** Neither Burson's lab dose-response nor Lee's *Cochlodinium* dose was in the retrieved abstracts; read the full texts if library access allows.
6. **Early vs late treatment** is unresolved (see Conflicts 1).
7. **Strip resolution.** 0.5-25 mg/L strips cannot confirm residuals below 0.5 mg/L or tell 1.6 from 2.0 well. Calibrate the strips against dilutions of 3% H2O2 made the same day, and record them as semi-quantitative.
8. **Gill-toxicity effect** (Mardones 2023) cannot be measured in a school lab. *Artemia* is only a rough proxy.

### Chemical safety (school lab, Form 3)
- **Use only drugstore 3% H2O2** (30,000 mg/L). Do not bring 30% H2O2 into the lab: it is corrosive and needs a much stricter risk assessment.
- **Dilution recipe for 1.6 mg/L in 2 L:**
  1. Make a 300 mg/L working stock: 1.0 mL of 3% H2O2 into 99 mL of artificial seawater.
  2. Add **10.7 mL of stock per 2 L jar**.
  3. Make the stock fresh each day, and check it with a strip (diluted into range).
- **Sodium percarbonate and calcium peroxide are solid oxidizers.** Goggles and nitrile gloves; weigh away from paper or organics; store dry, sealed and cool, away from acids and heat. The eye hazard is the main risk: dust or splashes, so goggles, not glasses.
- **ISEF paperwork:** hazardous chemicals mean **Form 3 (Risk Assessment)**, signed by the Designated Supervisor, who is present for handling. Keep the SDS for each chemical in the logbook. Use only non-toxic cultures (no *Alexandrium*, *Karenia*, *Prymnesium* or *Heterosigma*).
- **Disposal:** wait until strips read <0.5 mg/L (usually 1-2 days), then drain. Rinse empty bags before disposal. Unused solid peroxide goes back to the teacher's chemical store, not the trash.
- **Wording for the board:** "reduced small-cell algae in jars at 1.6 mg/L; large diatoms and dinoflagellates unaffected; non-target survival measured". Do not write "prevents blooms", "safe" or "ready for the Sound".
