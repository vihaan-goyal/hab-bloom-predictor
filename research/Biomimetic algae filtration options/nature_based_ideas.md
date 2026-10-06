# Nature-based and bio-inspired ideas for HAB control and sensor anti-fouling (beyond filtration, seaweed, shellfish, peroxide, aeration, curcumin, clay)

Method note (2026-10-03): the session's web-search budget was used up before this task started, so these sources were found through the Crossref, OpenAlex and Europe PMC APIs and by fetching publisher or PMC pages directly. Labels used below:
- **[V]** = verified. The number or claim was read in the abstract or full text fetched this session.
- **[T]** = title or bibliographic data verified only. The results were not read.
- **[U]** = from background knowledge and not re-verified this session. Check before citing.

Device screen used throughout: **Switchable** on a forecast alert? Needs **live organisms**? Can run **unattended ~2 weeks**? **Scales** to enclosed water (harbor pens, ponds)?

---

## 1. Artificial or robotic filter feeders (artificial mussel or oyster pumps, gill and gill-raker mimics, mucus-net or sticky capture)

### Takeaway
I found no prototype of an artificial mussel or oyster that removes phytoplankton from open water with reported results. The bio-inspired filter-feeder work is either (a) biomechanics and CFD of manta and devil-ray gill rakers, or (b) microfluidic and robotic-filament demonstrators running at mL/min. That is 6 or more orders of magnitude below the flow a harbor pen would need. For HAB mitigation this is an idea, not a technology.

### Cited Findings
- Manta-ray-inspired microfluidic chip (U-shaped gill-rake filter plus Dean flow). It reached "96.08% and 97.14%" filtration efficiency for 10 and 15 µm monodisperse particles at 6 mL/min, and throughput "up to 8 mL min⁻¹" **[V]**. Hu X, Yu L, Zhu Z, et al. 2024, *Lab on a Chip*. https://doi.org/10.1039/d4lc00039k
- Robotic gill filaments (RoboGFs) modeled on fan-worm gills. Passive adaptive gyration "enhances the particle capture rate by an average of 141% compared to a completely rigid design" **[V]**. This is a lab-tank mechanism study, not a phytoplankton test. Chen X, Jiang W, Wei J, et al. 2026, *Fundamental Research*. https://doi.org/10.1016/j.fmre.2026.03.009
- In mobulid (manta and devil ray) filter CFD models, filtration efficiency is "highly sensitive to the orientation of the filter lobes" **[V]**. Kahane-Rapport SR, Teeple J, Liao JC, et al. 2025, *Proc. R. Soc. B*. https://doi.org/10.1098/rspb.2024.2037
- A comparative review of mobulid filter anatomy discusses "ricochet separation", which can retain particles smaller than the pore size. It gives no prototype specifications **[V]**. Teeple JB, Kahane-Rapport SR, Cohen KE, et al. 2025, *Integrative and Comparative Biology*. https://doi.org/10.1093/icb/icaf142
- Original ricochet-separation paper: Divi RV, Strother JA, Paig-Tran EWM 2018, "Manta rays feed using ricochet separation, a novel nonclogging filtration mechanism", *Science Advances* 4:eaat9533 **[U]**. https://doi.org/10.1126/sciadv.aat9533
- Classic biomechanics of particle capture by marine suspension feeders **[T]**. Patterson MR 1983, "Asymmetrical particle capture in a marine filter feeder", *J. Biomechanics*. https://doi.org/10.1016/0021-9290(83)90136-7

### Inferences
- Device screen: a mechanical gill-rake or crossflow filter is **switchable**, needs **no live organisms**, and could run **2 weeks** (non-clogging is the bio-inspired selling point). It is still filtration, though, which the project has already scoped out. Throughput scaling is the barrier. No data show it at m³/h on real bloom water.
- "Artificial mussel" in the literature mostly means passive metal-uptake **samplers** for monitoring, not filters **[U]**. Do not confuse the two in a write-up.
- Mucus-net or sticky-surface capture devices for phytoplankton: nothing found (see Gaps).

### Gaps
- No peer-reviewed prototype was found that pumps water through a bivalve-mimicking gill or mucus surface and reports phytoplankton or chlorophyll removal. Patent and grey literature were not searchable this session.
- No study was found of salp or appendicularian "mucus house" inspired capture meshes used on HAB cells.

---

## 2. Algal turf scrubbers (ATS) and floating treatment wetlands (FTW)

### Takeaway
Both have real field data, but both are slow **nutrient-removal** systems that run continuously. Their nutrient uptake depends on living biomass (attached algae, or plants and root biofilm), and they work over seasons and years. They cannot be "switched on" by a 2-to-4-week bloom forecast. Their direct effect on phytoplankton is small or local. The best use is as background nutrient control, not as an alert-triggered response.

### Cited Findings: algal turf scrubbers
- Wastewater ATS: mean P removal of **0.73 ± 0.28 g m⁻² d⁻¹** and biomass productivity of **35 g m⁻² d⁻¹** **[V]**. Craggs RJ et al. 1996, *Water Science & Technology*. https://doi.org/10.2166/wst.1996.0138
- Attached-algae flow-ways run continuously for **two years** in Upper Laguna Madre, Texas (a hypersaline lagoon with recurrent brown tide). Biomass was **4–10 g m⁻² d⁻¹** ash-free, N recovery **300–500 mg m⁻² d⁻¹**, P recovery **15–30 mg m⁻² d⁻¹** **[V]**. Kim S, Quiroz-Arita C, Monroe EA, et al. 2021, *Water Research*. https://doi.org/10.1016/j.watres.2021.116816
- Lab-scale ATS optimisation: maximum TP and TN removal rates of **8.3 and 19.1 mg L⁻¹ d⁻¹** **[V]**. Gan X et al. 2022, *Frontiers in Bioengineering and Biotechnology*. https://doi.org/10.3389/fbioe.2022.962719
- Small ATS on Chesapeake Bay tributaries ("Toward scrubbing the bay") **[T]**. Mulbry WW et al. 2010, *Ecological Engineering*. https://doi.org/10.1016/j.ecoleng.2009.11.026
- Agricultural drainage ATS running on solar power **[T]**. Kangas PC & Mulbry WW 2014, *Bioresource Technology*. https://doi.org/10.1016/j.biortech.2013.11.027
- ATS at an oyster aquaculture facility (N and P removal) **[T]**. Ray NE et al. 2014, *Ecological Engineering*. https://doi.org/10.1016/j.ecoleng.2014.04.028
- Technical-scale ATS with stable year-round nutrient removal from wastewater **[T]**. Gan X et al. 2022, *Separation and Purification Technology*. https://doi.org/10.1016/j.seppur.2022.122693

### Cited Findings: floating treatment wetlands
- FTW pilots of **40–280 m²** ran **>3 years** in Baltimore, Boston and Chicago harbors. They removed about **2 g P m⁻² yr⁻¹** through plant harvest. Effects on bloom-forming cyanobacteria were described as "localized changes in biotic structure" **[V]**. Rome M, Happel A, Dahlenburg C, et al. 2023, *Science of the Total Environment* 877:162669. https://doi.org/10.1016/j.scitotenv.2023.162669. This is the closest analogue to "harbor pens". The effect was local, not whole-basin.
- Three Florida stormwater ponds with FTWs: total P correlated **negatively** with microcystin and positively with chl-a. The relationships were "conditional to the candidate pond and sampling conditions" **[V]**. Hartshorn N, Marimon Z, Xuan Z, et al. 2016, *Chemosphere* 144:408–419. https://doi.org/10.1016/j.chemosphere.2015.08.023
- FTW mesocosms: plants added 8.2% to TP removal efficiency (pickerelweed) and 18.2% to TN removal (softstem bulrush) at a 7-day retention time. Removal was active only May–August **[V]**. Wang CY & Sample DJ 2014, *J. Environmental Management* 137:23–35. https://doi.org/10.1016/j.jenvman.2014.02.008
- "Living-Filter", an in-reservoir FTW meant to cut phytoplankton before a drinking-water intake (London) **[T]**. Results were not read because the publisher page did not render. Castro-Castellon AT et al. 2016, *Ecological Engineering*. https://doi.org/10.1016/j.ecoleng.2016.07.023. I recall the reported phytoplankton reduction was modest or not significant at reservoir scale **[U]**. Verify before quoting.

### Inferences
- Device screen. ATS: switchable **no** (biofilm has to be kept alive all the time). Live organisms **yes**. 2-week unattended run **possible** (a harvest every 1–2 weeks is typical). It scales to ponds, but the area needed is large. At ~0.5 g N m⁻² d⁻¹ (Kim 2021), removing 1 kg N/day would take about 2,000 m².
- FTW: switchable **no**, live organisms **yes** (plants), scales to ponds and marinas. The effects take seasons and stay local.
- Neither one fits a forecast-triggered device. Either could be a "before the season" partner to the forecast, for example deploying FTW mats in pens that the forecast flags as high-risk each year.

### Gaps
- No study was found that turns an ATS or FTW on or off in response to a bloom forecast, or that measures how fast chl-a drops after deployment during a bloom.
- I could not get the Castro-Castellon results or full texts of the Adey ATS review papers (e.g., Adey WH et al. 2011, *BioScience* 61:434 **[U]**). The fetch returned a different article.

---

## 3. Bio-inspired anti-fouling for optical sensors and filters

### Takeaway
Commercial fluorometers and sondes use **wipers plus copper** (and sometimes UV-C or bleach), not biomimetic coatings. Delgado et al. (2021) state that applying photocatalytic or biomimetic coatings to sensors is "non-existent" in practice. Biofouling can corrupt optical data in "less than a week". Wiper plus copper commonly gives weeks to a few months. One UV-C LED system reported 9 months. Bio-inspired coatings (SLIPS, zwitterionic, microtopography) show 70–180-day panel results, but on test coupons, not on sensor windows. For a 2-week unattended device, a **wiper plus copper** (or a UV-C LED) is the evidence-based choice. A SLIPS or zwitterionic coating is an experimental add-on, not a replacement.

### Cited Findings: sensor-specific
- "Biofouling can disrupt the quality of the measurements, sometimes in less than a week". Very few anti-fouling methods "have been tested in situ on oceanographic sensors for deployment of at least one or two months" **[V]**. Delauney L, Compère C, Lehaitre M 2010, *Ocean Science* 6:503–511. https://doi.org/10.5194/os-6-503-2010
- Review of sensor anti-fouling **[V, full text]**. Delgado A, Briciu-Burghina C, Regan F 2021, *Sensors* 21:389. https://doi.org/10.3390/s21020389 (PMC7827029). Points from the full text:
  - Commercial implementations:
    - YSI EXO: central wiper, copper guard and sleeves.
    - Sea-Bird ECO fluorometer: wiper plus copper plate.
    - Turner C3/C6P: copper tape plus mechanical copper wiper.
    - Chelsea VLux: UV plus copper bezels plus wiper.
    - Sea-Bird WQM/HydroCAT-EP: bleach injection (~125 mL reservoir) plus wiper plus copper.
    - AML X-Series: UV-Xchange LED.
    - Zebra-Tech Hydro-Wiper: stand-alone retrofit.
  - AML UV-C LED protection worked over "**nine months** of deployment" against an unprotected control.
  - Visible fouling appeared on an optical sensor after "as little as one month".
  - Some common marine algae tolerate copper.
  - Ultrasound is effective on hulls, but stand-alone sensor power limits make it "unfeasible at present".
  - Applying TiO₂, ZnO or biomimetic coatings to sensors is "non-existent".
  - A *Pseudoalteromonas* natural-product coating lasted only "14 days due to its fragility".
  - Conclusion: "there is no available universal strategy... rather a combination of strategies that has extended deployment times... from days to months."
- Electro-chlorination on TriOS fluorometer windows (SnO₂ coating, about 1 mA) **[V via Delgado]**. Primary source: Delauney L et al. 2015, OCEANS Genova **[T]**. https://doi.org/10.1109/oceans-genova.2015.7271715. Also Delauney L 2017, "Optimized and high efficiency biofouling protection for oceanographic optical devices", OCEANS Aberdeen **[T]**. https://doi.org/10.1109/oceanse.2017.8084636
- UV-emitting glass (silica nanoparticles) on transparent surfaces: **98%** less visible growth and a **1.79-log** CFU drop after **20 days** submerged at Port Canaveral, FL **[V]**. Alidokht L et al. 2024, *Biofilm*. https://doi.org/10.1016/j.bioflm.2024.100186
- UV-C duty cycles on field biofilms (30, 60 or 90 min, 3× daily; 5.58–16.74 J cm⁻²): chl-a in the biofilm fell in all trials **[V]**. Richard KN, Hunsucker KZ, Swain G, Kardish MR 2025, *Microorganisms*. https://doi.org/10.3390/microorganisms13112561. On cultured diatom biofilms, short doses had to be given more often than long ones **[V]**. Richard KN et al. 2025, *Biofilm*. https://doi.org/10.1016/j.bioflm.2025.100285
- 16 MHz surface-acoustic-wave (SAW) chips on water-quality sensors: about **98%** less biofilm from diatoms and planktonic algae, with operation "up to a couple of months" without maintenance **[V]**. Akther A, Malthus T, Willis A, et al. 2026, *Sensors*. https://doi.org/10.3390/s26113480
- ISE (ion-selective electrode) fouling: drift of about 1–10 mV/h and about 40% sensitivity loss in 20 days without mitigation **[V]**. Rinn P et al. 2025, *Sensors*. https://doi.org/10.3390/s25247515
- Review of anti-biofouling coatings for marine sensors, including field trials **[T]**. Sahoo BN et al. 2025, *ACS Sensors*. https://doi.org/10.1021/acssensors.4c02670
- The Alliance for Coastal Technologies (ACT) evaluations page lists fluorometer, turbidity, DO, pH and nutrient sensor evaluations. It lists **no dedicated anti-fouling technology evaluation** **[V]**. https://www.act-us.info/evaluations.php

### Cited Findings: bio-inspired coatings (panels or coupons, not sensors)
- SLIPS (bioinspired slippery liquid-infused surfaces): "over 90% biofouling suppression after **180 days**" in a Bohai Sea field test **[V]**. Guo X et al. 2026, *Langmuir*. https://doi.org/10.1021/acs.langmuir.6c01350
- Durable slippery organic coating: **2.08%** bacterial colonisation after 28 days and **99.75%** anti-algal efficacy after 10 days (lab) **[V]**. Jing Y et al. 2025, *ACS Appl. Mater. Interfaces*. https://doi.org/10.1021/acsami.4c19298
- Slippery surface on Ti alloy: adhesion of algae cut by 78.8% and of bacteria by 77.8% (lab) **[V]**. Li Y et al. 2024, *Materials*. https://doi.org/10.3390/ma17225598
- Original SLIPS anti-biofilm paper **[U]**: Epstein AK, Wong T-S, Belisle RA, Boggs EM, Aizenberg J 2012, "Liquid-infused structured surfaces with exceptional anti-biofouling performance", *PNAS* 109:13182. https://doi.org/10.1073/pnas.1201973109 (the page returned 403)
- Zwitterion-enhanced acrylic zinc resin: anti-algae efficacy of 73–83% against three microalgae (lab) and "excellent anti-biofouling performance over **70 days** in a real marine environment" **[V]**. Hao X et al. 2026, *Small*. https://doi.org/10.1002/smll.73894. Note that this coating also contains zinc, so it is not purely biomimetic.
- Amphiphilic nanoparticle coatings resisted marine fouling "up to ~**150 days**" **[V]**. Zhu Z et al. 2026, *Langmuir*. https://doi.org/10.1021/acs.langmuir.6c03609
- Microtopography plus ZnO nanorods: diatom coverage cut by 9.9–72.9% depending on pattern **[V]**. Al-Busaidi A, Dobretsov S, et al. 2026, *PLoS One*. https://doi.org/10.1371/journal.pone.0357826
- Shark-skin-inspired Sharklet microtopography reduced *Ulva* zoospore settlement by about 85% versus smooth PDMS (lab, short assays) **[U]**. Schumacher JF et al. 2007, *Biofouling* 23:55. https://doi.org/10.1080/08927010601136957. Verify the DOI and number.
- Hydrophobic fouling-release coatings: after 6 months in natural seawater, moderate shear removed only part of the biomass **[V]**. Ferré C et al. 2026, *Scientific Reports*. https://doi.org/10.1038/s41598-026-35567-6
- Surface roughness in AF coatings depends on cutoff length (a method caution for microtopography claims) **[T]**. Howell D & Behrends B 2006, *Biofouling*. https://doi.org/10.1080/08927010601035738

### Inferences
- For a ~2-week deployment, plain **copper (tape or mesh guard) plus a servo wiper** that runs on each reading is enough on current evidence. Fouling problems usually start after about 1 week to 1 month. UV-C LED is the main upgrade, and it can run on a duty cycle (switchable). SAW is promising but rests on a single 2026 study.
- Bio-inspired coatings are best framed as an *experiment*: coat half a window with SLIPS and leave half bare, or compare a SLIPS-coated and a bare intake screen. Do not rely on them for data quality. SLIPS loses its oil under abrasion, which conflicts with a wiper.
- None of these methods needs live organisms. All except passive coatings can be switched. Copper leaching in enclosed pens is small but could be raised by reviewers, since copper is also an algicide.

### Gaps
- I found no published head-to-head of SLIPS, zwitterionic or Sharklet coatings on an actual **fluorometer window** with drift data.
- ACT anti-fouling or long-deployment reports (if any exist outside the evaluations page) were not found.
- I could not extract per-manufacturer deployment-duration claims beyond the Delgado table.

---

## 4. Biomimicry-based HAB mitigation in the literature and student competitions (ISEF, Stockholm Junior Water Prize)

### Takeaway
I could not verify any specific ISEF or Stockholm Junior Water Prize project on biomimetic HAB mitigation this session. The SJWP site redirected and its content was truncated, and there was no search budget left for the ISEF abstracts database. Peer-reviewed "biomimetic HAB mitigation" is essentially absent. The bio-inspired literature found is about filters (Section 1) and anti-fouling (Section 3), not about removing blooms.

### Cited Findings
- SJWP is now hosted by the Stockholm Water Foundation (siwi.org redirects to https://stockholmwaterfoundation.org/stockholm-junior-water-prize/) **[V, redirect only]**. The winner list and judging criteria were not retrieved.
- Oyster-mediated denitrification is framed as a nutrient-management service (policy and concepts) **[T]**. Rose JM et al. 2021, *Estuaries and Coasts*. https://doi.org/10.1007/s12237-021-00936-z

### Inferences
- For judging: ISEF Environmental Engineering judges typically reward a measured, controlled bench result over a "bio-inspired" label. The project's current framing (forecast plus a switchable treatment, with recovery fraction as the headline) is more defensible than a biomimicry claim with no quantitative comparison. **[inference, not sourced]**

### Gaps
- ISEF abstracts (Society for Science project database) for "algal bloom" plus "biomimetic", "filter" or "mussel" have not been searched. Do this manually at https://abstracts.societyforscience.org/.
- The SJWP international winner list, and any algae-related winners, have not been retrieved.

---

## 5. Light-, UV- and ultrasound-based treatments (brief)

### Takeaway
Ultrasound for **in-situ** bloom control has strong negative evidence from independent studies. It works in small lab vessels, but commercial transducers showed no effect in the field. UV-C works well for keeping **surfaces** free of fouling (sensor windows) but is not a whole-water bloom treatment for open pens. Calling either one "bio-inspired" is marketing, not biomimicry.

### Cited Findings
- "There is no music in controlling cyanobacteria in situ with the commercially available ultrasound transducers we have tested" **[V]**. Lürling M & Tolman Y 2014, *Water Research*. https://doi.org/10.1016/j.watres.2014.08.043
- Ohio reservoirs with ultrasound, compared with control reservoirs: no significant differences in any water-quality variable, "suggesting there is no effect of ultrasound in the evaluated reservoirs" **[V]**. Tischer MA, Murphy KA, Weaver CR, Crafton-Nelson E, Weavers LK 2025, *J. Environmental Management*. https://doi.org/10.1016/j.jenvman.2025.125057
- Lab sonocatalysis (40 kHz, 10 min, plus 400 mg/L Fe-biochar): >90% inactivation of *Microcystis* at 2×10⁶ cells/mL. The authors say pilot validation "is required" **[V]**. Zhu Y et al. 2026, *Ultrasonics Sonochemistry*. https://doi.org/10.1016/j.ultsonch.2026.107988
- Stirring-vortex-enhanced ultrasonic cavitation for algae inactivation (lab only) **[V]**. Wang Y et al. 2026, *Water Research*. https://doi.org/10.1016/j.watres.2025.124535
- UV-C for surface fouling: see Section 3 (Richard et al. 2025; Alidokht et al. 2024; AML 9 months via Delgado 2021).

### Inferences
- Device screen. Ultrasound: switchable **yes**, no live organisms, 2-week run **yes**. But the field efficacy evidence is **negative**, so it is not worth bench time except as a negative control. UV-C whole-water treatment: switchable **yes**, but contact time and turbidity limit it to a flow-through side-stream, which makes it filtration-adjacent. Its useful role here is keeping the device's own sensor and intake clean.

### Gaps
- No field study was found of pulsed UV-LED or blue-light treatment of open water against marine HAB species (e.g., *Alexandrium*, *Margalefidinium*, *Prorocentrum*).
