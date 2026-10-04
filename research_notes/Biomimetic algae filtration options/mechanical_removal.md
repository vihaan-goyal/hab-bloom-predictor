# Non-chemical physical/mechanical removal of microalgae (2-50 µm): efficiency, energy, fouling, scale, cost

Method note (read first). This session's WebSearch budget was used up, so the sources came from the Europe PMC and Crossref APIs (abstracts, plus open-access full text where it existed) and from one USGS report PDF. Labels used below:
- **[V]** means verified this session from the abstract or full text at the cited DOI.
- **[R]** means a widely cited number that was *not* re-read this session. It is listed so the writer knows it exists. Check it before quoting.
- **[I]** means my own inference or arithmetic.

Units: % removal; kWh/m³ of water treated (or kWh/kg of dry biomass where the paper only gives that); L/h.

Key framing for the writer [I]: almost every energy number in the harvesting literature is for **cultures** at 0.3-2 g/L dry weight. A coastal bloom at about 20-50 µg/L chlorophyll-a is only about 2-5 mg/L dry weight (assuming C:Chl ≈ 50 and C ≈ 50% of dry weight). That is 100-1000x more dilute. Cost "per kg harvested" therefore grows by 100-1000x for a HAB device, because energy scales with **volume pumped**, not with biomass. Use the kWh/m³ figures, not the kWh/kg figures, when judging the device.

---

## 1. Microscreens, drum and disc filters, bag/cartridge filters, sand filters: efficiency vs cell size and clogging at bloom densities

### Takeaway
Screens and microstrainers with 10-15 µm mesh use very little energy and run full scale in drinking-water plants. But they remove only about 50-65% of plankton on average, and they miss most cells smaller than the mesh (a large share of 2-10 µm HAB taxa). Fine bag, cartridge and sand filters do catch small cells, but they clog quickly at bloom densities, and plain sand fails during dense blooms. For a solar device, a coarse self-cleaning screen is the only filter type whose energy fits the budget. Its removal is partial and depends on cell size.

### Cited Findings
- Full-scale microstrainers at WTP Zawada (Poland) use three drums with **10 µm** mesh. Over four years (2011-2014), average plankton removal was **50.2-65.1%** (single samples 9.1-93.8%) and cyanobacteria removal was **48.6-65.9%** (5.0-93.0%). Removal **rose with raw-water plankton density** (65-66% when density was >100 × 10³ org/dm³) [V] — [Czyżewska & Piontek 2019, *Toxins* 11:285, doi:10.3390/toxins11050285](https://doi.org/10.3390/toxins11050285)
- Same paper: the Stuttgart (Lake Constance) plant uses 12 microstrainers with **15 µm** mesh. Microstrainers mainly protect downstream filters from clogging by plankton and debris [V] — [Czyżewska & Piontek 2019](https://doi.org/10.3390/toxins11050285)
- Same paper, citing earlier work: low-pressure microfiltration and ultrafiltration membranes remove **>98%** of intact cyanobacterial cells but do not reject dissolved toxins [V, secondary citation] — [Czyżewska & Piontek 2019](https://doi.org/10.3390/toxins11050285)
- "High-density algal cells and the released algal toxins during harmful algal blooms cannot be effectively removed by traditional sand filtration systems." Adding 2 wt% biochar fixed this for *Microcystis* and *Chlorella* at slow and fast filtration rates over 50 pore volumes (lab columns) [V] — [Zhang et al. 2025, *J Hazard Mater*, doi:10.1016/j.jhazmat.2025.138068](https://doi.org/10.1016/j.jhazmat.2025.138068)
- Sand filtration also acts as a biological barrier that degrades many cyanobacterial metabolites, but **microcystin-LR is among the least removed**. Cells caught in a filter can lyse and release dissolved metabolites [V] — [Rougé et al. 2026, *Environ Sci Technol*, doi:10.1021/acs.est.5c16532](https://doi.org/10.1021/acs.est.5c16532)
- GAC-sand deep-bed DAF/filtration on algae-laden raw water removed **95.1%** of algae and 92.2% of chlorophyll-a. Filter run time was **36 h** (unit filter run volume 504 m³/m²). This used chemical coagulation, since residual Al was measured [V] — [Zhang et al. 2004, *Huan Jing Ke Xue* (PMID record)](https://europepmc.org/search?query=GAC-sand%20dual%20media%20deep%20bed%20dissolved%20air%20flotation)
- Reviews state that screening and filtration work for large or colonial algae (e.g. *Spirulina*, *Coelastrum*) but fail for cells below about 10 µm without pre-flocculation. Pressure and vacuum filtration of small cells clog quickly [R] — [Milledge & Heaven 2013, *Rev Environ Sci Biotechnol* 12:165, doi:10.1007/s11157-012-9301-z](https://doi.org/10.1007/s11157-012-9301-z); [Uduman et al. 2010, *J Renew Sustain Energy* 2:012701, doi:10.1063/1.3294480](https://doi.org/10.1063/1.3294480); [Barros et al. 2015, *Renew Sustain Energy Rev* 41:1489, doi:10.1016/j.rser.2014.09.037](https://doi.org/10.1016/j.rser.2014.09.037)

### Inferences
- [I] At a 10 µm mesh, single 2-10 µm HAB cells (many *Karenia*, *Heterosigma*, *Prorocentrum minimum*, *Aureococcus* about 2 µm, picocyanobacteria) mostly pass. Chains, colonies and large dinoflagellates (*Margalefidinium/Cochlodinium* chains, *Dinophysis*, 30-50 µm *Akashiwo*) are held. Expect roughly 50% bulk removal per pass in mixed plankton, as Zawada found.
- [I] Energy for a screen is mostly pumping at low head. Ideal pumping energy is ρgH/η, which is about **0.0054 kWh/m³ per metre of head at 50% pump efficiency**. A 1 kWh/day solar budget (about 200-250 W panel) could therefore move about 180 m³/day (about 7,500 L/h) through a screen with about 1 m head loss. That is the only class with clear headroom.
- [I] Clogging load: a 50 µg/L Chl-a bloom is about 5 mg DW/L, i.e. about 5 g dry (roughly 50-100 g wet) per m³. A 300 m³ pen therefore delivers about 1.5 kg dry biomass per full pass. A 1-5 µm bag or cartridge filter would blind within hours to a day, not two weeks. Fine filters need auto-backwash or a spray-washed rotating drum (as in Zawada's sprinkler-cleaned drums). Static bags only work as a polishing stage.

### Gaps
- No peer-reviewed clogging rate (pressure rise per volume) was found for bag or cartridge filters at marine bloom densities. Vendor or aquaculture data are needed.
- No drum or disc filter study measured removal *as a function of cell size* (2-50 µm) for marine dinoflagellates or raphidophytes.
- No energy numbers per m³ for microstrainers were found in the retrieved sources.

---

## 2. Cross-flow / tangential-flow (MF/UF) membrane filtration: flux, fouling, energy

### Takeaway
Membranes are the only purely physical method that removes essentially all 2-50 µm cells (>98%). Energy is about 0.2 to 2 kWh/m³ of feed, and flux is only about 5-30 L/m²/h. Membranes foul, need backflushing plus chemical cleaning, and shear fragile cells (dinoflagellates, raphidophytes), which can release toxins. Energy is 1-2 orders of magnitude too high for a small solar device at pen-turnover volumes.

### Cited Findings
- Tangential-flow filtration of marine *Tetraselmis suecica* reached **148x concentration at 2.06 kWh/m³**. Polymer flocculation reached 357x at 14.81 kWh/m³. Payback for TFF was about 1.5 years at high biomass value [V] — [Danquah et al. 2009, *J Chem Technol Biotechnol* 84:1078, doi:10.1002/jctb.2137](https://doi.org/10.1002/jctb.2137)
- Submerged microfiltration of *Chlorella vulgaris* and marine diatom *Phaeodactylum* showed a **low degree of fouling**, comparable to a submerged MBR. Membrane up-concentration plus centrifuge to 22% w/v used **0.84 kWh/m³** (*C. vulgaris*) and **0.91 kWh/m³** (*P. tricornutum*) [V] — [Bilad et al. 2012, *Bioresour Technol* 111:343, doi:10.1016/j.biortech.2012.02.009](https://doi.org/10.1016/j.biortech.2012.02.009)
- A magnetically induced membrane vibration (MMV) system gave 15x membrane concentration, then centrifuge to 25% w/v. Total energy was **0.84 kWh/m³** (*P. tricornutum*) and **0.77 kWh/m³** (*C. vulgaris*), i.e. 1.46 and 1.39 kWh/kg. MMV gave "good fouling control" [V] — [Bilad et al. 2013, *Bioresour Technol* 140:? , doi:10.1016/j.biortech.2013.03.175](https://doi.org/10.1016/j.biortech.2013.03.175)
- Second-generation MMV: intermittent vibration (4 min cycle, 50% on) gave high flux, low energy, fouling control and **no algal cell damage** [V, abstract gives no kWh number] — [Zhao et al. 2020, *Bioresour Technol* 298:122688, doi:10.1016/j.biortech.2019.122688](https://doi.org/10.1016/j.biortech.2019.122688)
- A 212-day pilot of cross-flow UF on a pre-concentrated culture: concentration ratio 15-27, **average flux 5-28 L/m²/h**. Backflush plus chemical cleaning recovered about 21% more flux than backflush alone, i.e. **chemical cleaning was still needed** [V, preprint] — [Mora-Sánchez et al. 2023, Preprints 202312.0254, doi:10.20944/preprints202312.0254.v1](https://doi.org/10.20944/preprints202312.0254.v1)
- Pumps and valves in TFF loops damage brittle marine microalgae (*Skeletonema costatum*, *Haslea ostrearia*). The damage depends on pump type, speed and valve pressure-drop coefficient [V] — [Vandanjon et al. 1999, *Biotechnol Bioeng* 63:1, doi:10.1002/(SICI)1097-0290(19990405)63:1<1::AID-BIT1>3.0.CO;2-K](https://doi.org/10.1002/(SICI)1097-0290(19990405)63:1%3C1::AID-BIT1%3E3.0.CO;2-K)
- MF/UF removes >98% of cyanobacterial cells. Intracellular compounds are released during low-pressure membrane filtration [V, secondary] — [Czyżewska & Piontek 2019](https://doi.org/10.3390/toxins11050285)
- Commonly quoted review figure for cross-flow filtration is about 2 kWh/m³ [R] — [Milledge & Heaven 2013](https://doi.org/10.1007/s11157-012-9301-z)

### Inferences
- [I] At 0.8-2 kWh/m³, treating a 300 m³ pen once a day takes 240-600 kWh/day. That is about 250-600x a small solar budget. Membranes only fit if the device treats a tiny volume (e.g. a 1-5 m³ refuge or intake stream), or uses a very low-energy submerged/gravity design at a few L/m²/h.
- [I] At flux 10-25 L/m²/h, 1,000 L/h needs about 40-100 m² of membrane. That is not "low-cost" for an autonomous float.

### Gaps
- No MF/UF study was found treating *natural* seawater at HAB densities (mg/L, not g/L) in continuous dead-end/backwash mode with measured kWh/m³. Desalination-pretreatment UF data would be the closest analogue (not retrieved).

---

## 3. Hydrocyclones and centrifugal separators at 2-50 µm

### Takeaway
Hydrocyclones have no moving parts and need little energy, but their cut size is too large for most 2-10 µm cells. Even 3D-printed mini-cyclones only concentrate marine *Tetraselmis* (about 10 µm) by about 7x, and they need high pressure and many parallel units. Centrifuges remove cells well (>90%) but use about 1-8 kWh/m³ and are complex, so they are unsuitable for an autonomous float.

### Cited Findings
- A 3D-printed mini-hydrocyclone (HC-1), designed by CFD for a smaller cut size, increased marine *Tetraselmis suecica* concentration **7.13x in 11 min** "with low energy input". The authors present it as a *primary* harvesting step [V] — [Shakeel Syed et al. 2017, *Lab Chip* 17:2459, doi:10.1039/c7lc00294g](https://doi.org/10.1039/c7lc00294g)
- A novel 3D-printed hydrocyclone with an arc inlet was studied for classifying ultrafine particles (experiment plus CFD) [V, title only] — [Xu et al. 2023, *ACS Omega*, doi:10.1021/acsomega.2c06383](https://doi.org/10.1021/acsomega.2c06383)
- Mohn's hydrocyclone tests reported about 0.3 kWh/m³ and a concentration factor of about 4, with unreliable separation. Review values for centrifuges are about 1 kWh/m³ for disc-stack and about 8 kWh/m³ for decanters, with >90% recovery [R] — [Milledge & Heaven 2013](https://doi.org/10.1007/s11157-012-9301-z); [Uduman et al. 2010](https://doi.org/10.1063/1.3294480)
- ECF energy was compared against centrifugation and judged "more energy efficient" than centrifuge [V] — [Vandamme et al. 2011, *Biotechnol Bioeng* 108:2320, doi:10.1002/bit.23199](https://doi.org/10.1002/bit.23199)

### Inferences
- [I] Hydrocyclone separation scales with (density difference × d²). Algae are only about 1.03-1.10 g/cm³ against seawater at 1.025, so the cut size d50 stays well above 5 µm unless the cyclones are mm-scale at high pressure. Small HAB cells would mostly report to the overflow. Not recommended as the main stage. At most it could be a pre-concentrator for >20 µm cells.

### Gaps
- No paper was retrieved giving hydrocyclone grade-efficiency curves (removal % vs µm) for marine dinoflagellates, nor kWh/m³ for the Syed 2017 device (the full text was not accessible).

---

## 4. DAF, electro-flotation, electrocoagulation/electro-flocculation (Al/Fe electrodes): efficiency, energy, metal release, field HAB use

### Takeaway
Flotation and electro-coagulation reach >90-99% cell removal. **None of them is truly "non-chemical"**:
- DAF needs coagulant or polymer dosing (or polymer-coated bubbles).
- Sacrificial-anode EC doses Al or Fe ions in situ (the coagulant is made electrochemically).
- Inert-anode electrolysis in seawater makes chlorine/hypochlorite (an oxidant).

Energy per m³ at culture densities is about 0.4-3 kWh/m³. Al release was <2 mg/L in process water. The field HAB use of these methods is DAF at agency scale (US Army Corps HABITATS). It cost US$3.9-7.3 M for a modelled 90-day deployment.

### Cited Findings
**Electrocoagulation-flocculation (sacrificial anode)**
- ECF worked better with an **Al anode than Fe**. Lower current density reduced both energy per kg and Al release. Harvested biomass contained **<1% Al** and process water had **<2 mg/L Al**. Energy was about **2 kWh/kg** for freshwater *Chlorella* and about **0.3 kWh/kg** for marine *Phaeodactylum*. Seawater's high conductivity makes ECF "particularly attractive" for marine algae [V] — [Vandamme et al. 2011, *Biotechnol Bioeng* 108:2320, doi:10.1002/bit.23199](https://doi.org/10.1002/bit.23199)
- ECF of freshwater *Scenedesmus* achieved complete harvest at 12 mA/cm², 15 min electrolysis and 60 min settling. Energy was **2.65 kWh/kg** and operating cost **US$0.29/kg** [V] — [Pandey et al. 2020, *Environ Sci Pollut Res*, doi:10.1007/s11356-019-06897-y](https://doi.org/10.1007/s11356-019-06897-y)
- Al-based electrocoagulation-flocculation-flotation of *Microcystis* at 5 mA/cm² and pH 8 harvested **99.5% of cells** and 95% of phosphate at 1 mg/L P. High phosphate (10 mg/L) impaired harvest, and **raising current increased release of algal organic matter** [V] — [Lin & Sidik 2024, *Water Res*, doi:10.1016/j.watres.2024.121868](https://doi.org/10.1016/j.watres.2024.121868)
- Saltwater electroflocculation with **non-sacrificial** electrodes (pH-mediated): best volumetric energy **3.1 ± 0.1 kWh/m³**, or **3.0 ± 0.2 kWh/kg**, at 0.5-1.6 g/L biomass. "A major issue with non-sacrificial electrode flocculation is the toxic effects of chlorine and ClOx" in seawater (Cl₂ evolves at the anode). The paper cites Zhu et al.: Al electrodes gave >95% flocculation of *Picochlorum* in 5-20 min at 0.8-3.2 A/L [V, full text] — [Dennis, Karns & Posewitz 2026, *RSC Adv* 16:2449, doi:10.1039/d5ra07757e](https://doi.org/10.1039/d5ra07757e)

**Electrolysis aimed at HAB cells (inactivation rather than removal)**
- Electrolysis with a Ti/RuO₂ anode inhibited *Microcystis* growth by up to about **100% at 12 mA/cm²** in NaCl electrolyte. Free radicals were detected, i.e. the effect is oxidative [V] — [Xu et al. 2006, *Environ Technol*, doi:10.1080/09593332708618682](https://doi.org/10.1080/09593332708618682)
- The current-density threshold for complete *Microcystis* inactivation rises with cell density: **8 mA/cm² at 2.5 × 10⁷ cells/mL up to 22 mA/cm² at 5 × 10⁸ cells/mL** [V] — [Lin et al. 2015, *Environ Sci Pollut Res*, doi:10.1007/s11356-015-4708-z](https://doi.org/10.1007/s11356-015-4708-z)
- Ti/RuO₂ anode with a gas-diffusion cathode: **85% of *Microcystis* inactivated in 20 min** at 20 mA/cm². The effect was dominated by electrogenerated **H₂O₂ (up to 58 mg/L)** [V] — [Zhang et al. 2023, *Environ Pollut*, doi:10.1016/j.envpol.2023.121316](https://doi.org/10.1016/j.envpol.2023.121316)
- Korean patent for a red-tide removal device: seawater electrolysis cell plus photocatalyst cartridge, with current set to keep **free chlorine ≤1 ppm**. This shows the Korean approach is oxidant-based [V, patent abstract] — [Cha et al. 2007, KR patent (Europe PMC record)](https://europepmc.org/search?query=RED-TIDE%20REMOVAL%20DEVICE%20USING%20A%20SEA-WATER%20ELECTROLYSIS)

**Electro-flotation (no coagulant)**
- Electro-flotation of hydrophobic *Tribonema* without coagulant removed **96.3%** at **0.19 kWh/kg** (1 g/L). Moderately hydrophobic *Scenedesmus* reached only **70%**, and hydrophilic *Pandorina* **<10%**: **efficiency depends strongly on cell hydrophobicity** [V] — [Qi et al. 2022, *Sci Total Environ*, doi:10.1016/j.scitotenv.2022.155866](https://doi.org/10.1016/j.scitotenv.2022.155866)
- Electro-flotation of *Chlorella vulgaris* with a stainless-steel cathode and a non-sacrificial anode gave **>90% harvest**. Finer cathode wires made smaller bubbles [V] — [Li et al. 2022, *Bioresour Technol*, doi:10.1016/j.biortech.2022.127961](https://doi.org/10.1016/j.biortech.2022.127961)
- Alternating-current electro-flotation with non-consumable electrodes on stabilization-pond algae: **99% chlorophyll-a removal** after a 140 min batch. It also disrupted cells (which would release toxins in a HAB context) [V] — [de Carvalho Neto et al. 2014, *Water Sci Technol*, doi:10.2166/wst.2014.220](https://doi.org/10.2166/wst.2014.220)
- Electro-flotation of activated sludge removed 97% of solids at **0.4-0.5 kWh/m³**, with a 20 min retention time [V] — [Chen, Wan & Shi 2006, *Huan Jing Ke Xue* (Europe PMC record)](https://europepmc.org/search?query=Electro-flotation%20using%20in%20solid-liquid%20separation%20of%20activated%20sludge)

**Dissolved-air flotation (DAF)**
- DAF "is highly dependent on coagulation-flocculation". Algae cause unpredictable coagulant demand during blooms. Cationic polymer-coated bubbles (PosiDAF) removed **>90%** of cells without a separate coagulation step [V] — [Yap et al. 2014, *Water Res*, doi:10.1016/j.watres.2014.05.032](https://doi.org/10.1016/j.watres.2014.05.032)
- Surfactant-modified bubbles removed at most **87%** of *M. aeruginosa*. Larger species were removed better and needed lower surfactant doses [V] — [Henderson, Parsons & Jefferson 2008, *Environ Sci Technol*, doi:10.1021/es702649h](https://doi.org/10.1021/es702649h)
- PosiDAF separation depends on the algal organic matter of each strain [V] — [Hanumanth Rao et al. 2018, *Water Res*, doi:10.1016/j.watres.2017.11.049](https://doi.org/10.1016/j.watres.2017.11.049)
- Seawater desalination HAB pilot: DAF needed NaClO pre-oxidation, PAC at 12 mg/L and PAM at 0.2 mg/L. Overall algae removal was **>95%** only after a post sand-filter [V] — [Li et al. 2026, *Water Environ Res*, doi:10.1002/wer.70498](https://doi.org/10.1002/wer.70498)
- A commonly quoted DAF energy for algae is about 1.5 kWh/m³ [R] — [Milledge & Heaven 2013](https://doi.org/10.1007/s11157-012-9301-z)

**Field HAB application of DAF: US Army Corps ERDC HABITATS**
- HABITATS has three stages. **Interception**: a floating weir skimmer plus booms. **Treatment**: DAF, then oxidation if needed. **Transformation**: biomass to biocrude by hydrothermal liquefaction. Pilots ran in 2019 (Lake Okeechobee, shore-based) and 2020 (Chautauqua Lake NY, a shipboard prototype: two boats towing 50 ft booms to a weir skimmer feeding a DAF barge). The 2019 Port Mayaca test was **not run for lack of algae** [V] — [Boubacar, Pindilli, Brown & Simon 2024, USGS SIR 2024-5091, doi:10.3133/sir20245091](https://doi.org/10.3133/sir20245091)
- Modelled 90-day deployment for the 2018 Lake Okeechobee event:
  - Total cost **US$3.88 M (basic) to $7.32 M (with "rapid air flotation technology", RAFT)**.
  - Operating cost $0.67-1.04 M.
  - Algal removal **25% (basic, well-mixed bloom) to 87% (RAFT, surface bloom)**.
  - Net societal benefit **−$2.1 M to +$0.83 M**.
  - Shipboard HABITATS was "previously determined to be more costly" than shore-based [V] — [USGS SIR 2024-5091](https://doi.org/10.3133/sir20245091)
- The 2021 ERDC optimisation report covers a new **organic flocculant** for neutralising and floating cells, a "high-throughput biomass dewatering system with low power requirements", the first shipboard prototype, and field pilots with FL DEP and NYS DEC [V, abstract] — [Page et al. 2021, ERDC report, doi:10.21079/11681/42223](https://doi.org/10.21079/11681/42223); Phase I report: [Page et al. 2020, ERDC TR-20-1, doi:10.21079/11681/35214](https://doi.org/10.21079/11681/35214)

### Inferences
- [I] Per-kg energy figures (0.19-3 kWh/kg) look small but were measured at 0.5-2 g/L. EC must dose Al per *volume* to destabilise cells, and electrolysis must reach a current density threshold. So at bloom densities of about 0.005 g/L, per-m³ energy will not fall 100-fold. Expect roughly 0.1-1 kWh/m³ for EC/EF in seawater. This is an estimate from Dennis 2026 (3.1 kWh/m³ at g/L) and the Chen 2006 sludge figure (0.4-0.5 kWh/m³). It should be measured.
- [I] Sacrificial-Al EC releases Al (process water <2 mg/L in Vandamme 2011). This is functionally a coagulant dose and will likely face the same permitting and "chemical" objections as PAC or clay. Inert-anode electrolysis in seawater makes chlorine, i.e. an oxidant treatment.
- [I] HABITATS is the only agency-scale pump-through removal system found. It needs boats, booms, a DAF barge and flocculant, and costs millions per season. This is a strong argument that a small device should target **small enclosed volumes**, not open water.

### Gaps
- The HABITATS treatment flow rate (gal/day) was not in the USGS report text that was accessible. The ERDC reports themselves (doi:10.21079/11681/35214, /42223) were blocked by a bot-check page.
- No peer-reviewed field trial of EC or electrolysis against *marine* HABs (Korea, China, US) with measured volumes and kWh/m³ was retrieved. Only the Korean patent was found.
- No AECOM Lake Okeechobee (2019) or Florida/Lake Erie "bloom removal" barge data with peer-reviewed volumes or costs were retrieved (the AECOM web page returned no content).

---

## 5. Ultrasound with filtration; magnetic separation (clay out of scope)

### Takeaway
Ultrasound does not remove cells. In the most recent multi-reservoir field evaluation it had **no measurable effect**. Lab sonication can lyse cells and release toxins. It is not a removal method for a device. Magnetic-particle separation was not researched here because the project already covers it and it is a dosing method (clay is excluded by the brief).

### Cited Findings
- Field measurements at five reservoirs with commercial ultrasound units showed **no significant water-quality difference vs control reservoirs**. The sound attenuated exponentially, about 10x faster than in pure water. Cavitation, gas-vesicle collapse and resonance are "unlikely to affect cHABs" at field sound levels [V] — [Tischer et al. 2025, *J Environ Manage*, doi:10.1016/j.jenvman.2025.125057](https://doi.org/10.1016/j.jenvman.2025.125057)
- A review found that most ultrasound HAB studies are lab-only, with few field or pilot tests in small reservoirs. Applicability "is still under question" [V] — [Park et al. 2017, *Ultrason Sonochem* 38:326, doi:10.1016/j.ultsonch.2017.03.003](https://doi.org/10.1016/j.ultsonch.2017.03.003)
- Ultrasound-enhanced *coagulation* of cyanobacteria depends on frequency and energy density, with leakage of intracellular organic matter [V, title] — [Huang et al. 2021, *Water Res*, doi:10.1016/j.watres.2021.117348](https://doi.org/10.1016/j.watres.2021.117348)

### Inferences
- [I] Ultrasound may help as a pre-treatment to make cells stick before a screen, but it risks releasing toxins. It should not be counted as removal.

### Gaps
- No study was retrieved that combines ultrasound with a screen or filter at bloom densities.

---

## 6. Comparison for a low-cost autonomous on-water device (solar/battery, pump-through, 2-week service)

### Takeaway
Only low-head screening (a self-cleaning drum or disc microscreen at 10-20 µm, possibly with a coarse-bag polish stage) has an energy demand that a small solar float can supply at useful flows (hundreds of m³/day). Its removal is partial: about 50% of bulk plankton in full-scale use, much better for chain-forming and large species, poor for 2-10 µm cells. Membranes, centrifuges, DAF and EC remove >90% but need about 0.4-3 kWh/m³, and (DAF/EC) coagulant or oxidant. They are only feasible for small treated volumes or with grid power.

### Cited Findings (summary table; numbers from sections above)

| Method | Removal of 2-50 µm cells | Energy | Clogging / fouling | Maintenance | Largest scale found | Cost signal | Source |
|---|---|---|---|---|---|---|---|
| Microstrainer drum, 10 µm | 50-66% avg plankton/cyanos (5-94% range) [V] | not reported; low-head pumping ≈0.005 kWh/m³/m head [I] | spray-wash self-cleaning drums [V] | rotating drum, spray bars | full-scale drinking-water plants (Zawada; Stuttgart, 12 units at 15 µm) [V] | n/a | [Czyżewska & Piontek 2019](https://doi.org/10.3390/toxins11050285) |
| Sand filtration | poor for dense HAB cells without modification [V]; 95% with DAF and coagulant [V] | low (gravity) | filter runs of about 36 h in DAF-filter [V] | backwash | full-scale WTPs | n/a | [Zhang 2025](https://doi.org/10.1016/j.jhazmat.2025.138068); [Zhang 2004](https://europepmc.org/search?query=GAC-sand%20dual%20media%20deep%20bed%20dissolved%20air%20flotation) |
| Cross-flow / submerged MF-UF | >98% [V] | 0.77-0.91 kWh/m³ (with centrifuge); TFF 2.06 kWh/m³ [V] | flux 5-28 L/m²/h; needs chemical clean [V] | backflush plus CIP | 212-day pilot [V] | TFF payback about 1.5 yr (high-value biomass) [V] | [Bilad 2012](https://doi.org/10.1016/j.biortech.2012.02.009), [Bilad 2013](https://doi.org/10.1016/j.biortech.2013.03.175), [Danquah 2009](https://doi.org/10.1002/jctb.2137), [Mora-Sánchez 2023](https://doi.org/10.20944/preprints202312.0254.v1) |
| Hydrocyclone (mini) | 7.13x concentration of *Tetraselmis* [V] | "low" [V]; about 0.3 kWh/m³ [R] | no fouling; erosion | none | lab [V] | cheap (3D-printed) [V] | [Syed 2017](https://doi.org/10.1039/c7lc00294g) |
| Centrifuge | >90% [R] | about 1 (disc) to 8 (decanter) kWh/m³ [R] | n/a | high | industrial | high capex [R] | [Milledge & Heaven 2013](https://doi.org/10.1007/s11157-012-9301-z) |
| DAF (+ coagulant or PosiDAF polymer) | 87% to >95% [V] | about 1.5 kWh/m³ [R] | sludge float | chemical dosing, saturator | agency field barge (HABITATS) [V] | US$3.9-7.3 M per 90-day modelled deployment [V] | [Yap 2014](https://doi.org/10.1016/j.watres.2014.05.032); [USGS 2024](https://doi.org/10.3133/sir20245091) |
| EC (Al anode) | 95-99.5% [V] | 0.3 kWh/kg marine, 2-2.65 kWh/kg fresh [V] | electrode passivation [R] | replace anodes | lab | US$0.29/kg op. cost [V] | [Vandamme 2011](https://doi.org/10.1002/bit.23199); [Pandey 2020](https://doi.org/10.1007/s11356-019-06897-y); [Lin & Sidik 2024](https://doi.org/10.1016/j.watres.2024.121868) |
| Electro-flotation / inert-anode EF in seawater | <10% to 96%, depends on hydrophobicity [V]; >90% [V] | 0.19 kWh/kg [V]; 3.1 kWh/m³ in saltwater [V]; 0.4-0.5 kWh/m³ (sludge) [V] | electrode scaling [R] | electrode cleaning | lab | n/a | [Qi 2022](https://doi.org/10.1016/j.scitotenv.2022.155866); [Dennis 2026](https://doi.org/10.1039/d5ra07757e); [Chen 2006](https://europepmc.org/search?query=Electro-flotation%20using%20in%20solid-liquid%20separation%20of%20activated%20sludge) |
| Ultrasound | no field effect [V] | n/a | n/a | n/a | 5 reservoirs [V] | n/a | [Tischer 2025](https://doi.org/10.1016/j.jenvman.2025.125057) |

### Inferences (device sizing, all [I])
- **Volume to treat.** Example pen 10 × 10 × 3 m = 300 m³. One turnover per day = 12.5 m³/h (12,500 L/h).
- **Solar budget.** About 200 W panel ≈ 0.8-1 kWh/day (northeast US summer, about 4-5 sun-hours). That supports about 0.003 kWh/m³ at 300 m³/day. Only a screen at less than about 0.5 m head loss meets this.
- **Energy per turnover by method** (300 m³/day):
  - membranes about 230-620 kWh/day;
  - DAF about 450 kWh/day [R-based];
  - EC/EF about 30-900 kWh/day (0.1-3 kWh/m³).
  - All of these are **30-900x** a small solar budget.
- **Cell size.** A 10-20 µm screen will strongly favour removal of 20-50 µm dinoflagellates and chain-formers (e.g. *Margalefidinium polykrikoides* chains). It will do little for 2-10 µm cells. The device's claim should name the target taxa.
- **Service interval.** A static fine bag will blind long before 14 days at bloom densities (section 1 arithmetic). A self-cleaning drum or disc with a spray-back or reverse-flow pulse, plus a sludge bag that collects the wash-off, is the only 2-week-autonomous filter design. Plan the wash-water pump energy into the budget.
- **Honest headline for a student device:** report per-pass removal by size class and kWh/m³ in a tank. Do not claim bloom control in open water. HABITATS needed millions of dollars and still removed only 25-87% in modelling.

### Gaps
- Energy per m³ for small self-cleaning drum or disc microscreens (aquaculture RAS drum filters at 10-60 µm) was not retrieved. This is the key missing number and is likely available from aquaculture engineering papers or vendor sheets.
- No field deployment of a small solar pump-through algae filter for HAB control with measured L/h and removal was found.
- The [R] centrifuge, DAF and hydrocyclone energy figures (Milledge & Heaven 2013; Uduman 2010; Barros 2015) need checking against the original tables before they are quoted.
