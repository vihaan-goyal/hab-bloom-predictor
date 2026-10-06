# Past ISEF (and adjacent-competition) projects on mitigating, treating, removing or preventing HABs

Scope: ISEF projects on HAB / cyanobacteria / red tide / eutrophication *treatment or prevention* (forecasting-only projects are noted only where they bear on "sensing + treatment"). Every fact carries a URL; unsourced material is in Gaps. "VERIFIED" = stated on the cited page; "INFERRED" = my reading, not stated.

Our project, for contrast: forecast-triggered, low-impact treatments (live kelp, oysters, aeration, low-dose peroxide, curcumin) switched on early and off at recovery by an Arduino controller; tank bench test with non-toxic algae, 4 arms including late-treatment and false-alarm controls, n=3, pre-registered; Monte Carlo tank simulation; 256-paper evidence scoreboard.

## Q1. Which HAB mitigation/treatment projects placed at ISEF (2015-2026), and with what awards?

### Takeaway
I found 10 verified ISEF treatment/prevention projects from 2018-2026. There are also 3 closely related HAB-treatment projects from the Stockholm Junior Water Prize track. Grand Awards went to 2nd place at most (ENEV 2024, MCRO 2026). Several projects won only special awards (NOAA, EPA Hurd Sustainability, ASU scholarship). Florida's Edgewood Jr/Sr High School produced repeated multi-year HAB projects.

### Cited Findings (catalog)

**1. Natalie Elizabeth Muro, "A Sustainable Cyanobacteria Mitigation Method for Freshwater Ecosystems in the Rocky Mountain Region" (ISEF 2025)**
- William J. Palmer High School, Colorado Springs, CO. Award: Arizona State University ISEF Scholarship (up to $32,000), a special award. No Grand Award is listed in the 2025 full-awards release. VERIFIED: [SfS 2025 special awards](https://www.societyforscience.org/press-release/regeneron-isef-2025-special-awards-winners/); [2025 full awards](https://www.societyforscience.org/press-release/regeneron-isef-2025-full-awards/)
- Method: a floating device powered by wind-driven waves (no motor) that slowly releases 3% hydrogen peroxide into the upper water layer. Mesh bags hold biochar made from invasive Great Mullein, which collects dead microbes so their nutrients do not feed survivors. VERIFIED: [SN Explores](https://www.snexplores.org/article/peroxide-fight-algal-blooms); [Layne McDonald (secondary)](https://www.laynemcdonald.com/post/good-news-18-year-old-invents-wave-powered-device-that-fights-toxic-algal-blooms)
- Field test: she tested it in a reservoir or lake near Colorado Springs that had been closed for a HAB. After treatment, samples had fewer cyanobacteria and other microbes were unharmed, which is a non-target check. She became a 2026 Regeneron STS finalist. VERIFIED: [SN Explores](https://www.snexplores.org/article/peroxide-fight-algal-blooms)
- ISEF category: not stated in the sources I found (Gap).
- How it differs from ours: a single passive peroxide treatment run continuously in the field. There is no forecast trigger, no on/off switching and no controlled multi-arm replication in the sources.

**2. Sharanya Natarajan, Edgewood Junior Senior High School, FL: a multi-year "Seek & Destroy HABs" system**
- 2023 (Year 4), ENEV021, "An Engineered Hub & Spoke System to Seek & Destroy HABs". Award: Third Award $1,000 (Environmental Engineering). VERIFIED: [SfS abstract 23488](https://abstracts.societyforscience.org/Home/FullAbstract?Category=Any+Category&AllAbstracts=True&FairCountry=Any+Country&FairState=Any+State&ProjectId=23488)
  - The system has three spokes and a cloud-dashboard hub:
    - a drone with multispectral imagery to find blooms;
    - a floating device with six sensors (pH, DO, TDS, light, color intensity, temperature);
    - a remote-controlled unit that disperses a suppression agent.
  - An alum-bentonite agent suppressed algae by flocculation, and an ML model predicted water quality with 84% accuracy. VERIFIED (same URL)
- 2024 (Year 5), ENEV005, "An Integrated Algae Mitigation System to Seek & Abate Harmful Algal Blooms". Award: Second Award $2,000 (Environmental Engineering). VERIFIED: [SfS 2024 full awards](https://www.societyforscience.org/press-release/regeneron-isef-2024-full-awards/)
- Published in the Journal of Emerging Investigators (2023), "Suppress that algae: Mitigating the effects of harmful algal blooms through preemptive detection & suppression". It reports a Wi-Fi microcontroller float with five sensors, cloud data transfer, and a 4th-order polynomial fit (94%) linking the green spectrum to DO. VERIFIED: [JEI 22-200](https://emerginginvestigators.org/articles/22-200)
- How it differs from ours: this is the closest analogue, since it also pairs sensing with treatment. Its treatment is a chemical flocculant (alum-bentonite) dispersed by remote control, not a forecast-triggered biological or low-dose treatment with an automatic off-switch. The sources show no late-treatment or false-alarm control arms.

**3. Mark Leone, "Mitigation of Florida Red Tide (Karenia brevis) Blooms through Flocculation with Enhanced Local Sediments" (ISEF 2019, EAEV082)**
- Estero High School, FL. Category: Earth and Environmental Sciences. Award: NOAA Second Award ($500). VERIFIED: [SfS abstract 18428](https://abstracts.societyforscience.org/Home/FullAbstract?ProjectId=18428)
- Method: he used local Barefoot Beach sand and Spring Creek silt, enhanced with polyaluminum chloride or chitosan, as clay flocculants against K. brevis. The enhanced local sediments beat outsourced clay on flocculation efficiency, 10-day floc retention and aggregate size, and they prevented regrowth. Statistics used a linear mixed model with p<0.05, and cost was the framing ("inexpensive, readily available"). VERIFIED (same URL)
- How it differs from ours: a one-shot clay flocculation in the lab against a real toxic dinoflagellate. There is no trigger or timing logic, and the non-target (benthic) effects of the sediment are not reported.

**4. Harshal Agrawal, "Large-Scale Field Testing of Stropharia Mycelium Buffer Strips for Harmful Algae Bloom Prevention, Year 5" (Intel ISEF 2019)**
- Dr. Ronald E. McNair Academic High School, Jersey City, NJ. Award: EPA Patrick H. Hurd Sustainability Award, which funds travel to the EPA National Sustainability Design Expo. VERIFIED: [EPA news release](https://www.epa.gov/newsreleases/innovative-water-quality-project-new-jersey-high-school-student-wins-epa-award)
- Method: buffer strips of mushroom (Stropharia) mycelium grown on waste vegetation capture N and P runoff before it reaches the water, and the mushrooms can be sold. Over 5 years the work moved from lab to field scale on a New Jersey golf course, in partnership with county officials. It was inspired by a HAB at Jersey City Reservoir #3. VERIFIED (same URL)
- How it differs from ours: upstream nutrient prevention at the watershed edge, always on. It does not treat an active bloom and has no forecast link.

**5. Savio Le, "Evaluating Phosphorus Absorbing Materials for the Mitigation of Harmful Algal Blooms (HABs)" (Intel ISEF 2018)**
- Holy Rosary Academy, Anchorage, AK. It won an ISEF 2018 award. VERIFIED per search snippet of [SfS ISEF 2018 special awards](https://www.societyforscience.org/press-release/intel-international-science-and-engineering-fair-2018-special-award-winners/). I did not open the page, so the exact award name and place are a Gap.
- How it differs from ours: a P-sorbent materials comparison, not a timed or triggered living treatment.

**6. Christopher Kwok and Nicholas Kwok, "Eukaryotic Algicide: Environmental Remediation of Harmful Algal Blooms via Microencapsulation for Bioactivation of Programmed Cell Death" (ISEF 2022)**
- Sequoia High School, CA. Award: Fourth Award $500, Microbiology (MCRO). VERIFIED: [SfS 2022 full awards](https://www.societyforscience.org/press-release/regeneron-isef-full-awards-2022/)
- They also placed 3rd in the 2022 California Stockholm Junior Water Prize. VERIFIED: [CWEA](https://www.cwea.org/news/fresno-students-win-california-stockholm-junior-water-prize/)
- Method details are title-only: a microencapsulated agent that triggers programmed cell death in bloom algae (INFERRED from the title).
- How it differs from ours: a novel targeted algicide with delivery chemistry, not reuse of existing low-impact treatments under a control policy.

**7. Erin Gaydar, "Abolition of Unfurling Nutrients Is the Solution for Elimination of Microalgae in the Indian River Lagoon (Year III)" (ISEF 2022)**
- Edgewood Junior Senior High School, FL. Award: Fourth Award $500, Plant Sciences (PLNT). VERIFIED: [SfS 2022 full awards](https://www.societyforscience.org/press-release/regeneron-isef-full-awards-2022/)
- Method details not found (Gap). It is a nutrient-removal approach per the title (INFERRED).
- How it differs from ours: nutrient abatement in the lagoon, with no sensing or trigger component evident.

**8. Jinxuan Wu, "A Nano-Chitin and HACC Multilayer System for Remediating Severely Eutrophic Waters via Oxygenation, Bacterial Inhibition, and Nutrient Stabilization" (ISEF 2026)**
- Shanghai Pinghe Bilingual School, China. Award: Second Award $2,400, Microbiology (MCRO). VERIFIED: [SfS 2026 full awards](https://www.societyforscience.org/press-release/regeneron-isef-2026-full-awards/)
- Method details are title-only: a multilayer material combining oxygenation, antibacterial HACC (a quaternized chitosan) and nutrient stabilization.
- How it differs from ours: an engineered material stack for severe eutrophication, not an on/off controller using biological treatments.

**9. Enyu Zhang, "Exploring Biogeochemical Climate Solutions for Nutrient Removal in the Narragansett Bay Estuarine Ecosystem" (ISEF 2025)**
- Portsmouth Abbey School, Portsmouth, RI. Awards: NOAA "Taking the Pulse of the Planet" First Award, and the Fondazione Bruno Kessler award (Web Valley summer school). VERIFIED: [SfS 2025 special awards](https://www.societyforscience.org/press-release/regeneron-isef-2025-special-awards-winners/)
- Method details not found (Gap).
- How it differs from ours: estuarine nutrient removal. It is relevant to our Narragansett fork, but the sources show no treatment-timing element.

**10. Prayrona Choudhury, "AquaShift: Synchronized Chemical Equilibrium Convergence as a Leading Indicator of Phycocyanin-Threshold Cyanobacterial Bloom Onset Across Contrasting Freshwater Systems" (ISEF 2026)**
- Hanford High School, WA. Award: Second Award $2,400, Earth and Environmental Sciences (EAEV). VERIFIED: [SfS 2026 full awards](https://www.societyforscience.org/press-release/regeneron-isef-2026-full-awards/)
- This is an early-warning project, not a treatment project. It is included because a leading indicator is the trigger half of our design.
- How it differs from ours: detection only, with no treatment arm.

**Adjacent ISEF forecast projects (not treatment; for the judging landscape)**
- ISEF 2024: two EAEV Second Awards ($2,000) went to HAB toxin forecasting. VERIFIED: [SfS 2024 full awards](https://www.societyforscience.org/press-release/regeneron-isef-2024-full-awards/)
  - Anson Chen (Nikola Tesla STEM HS, WA), "Forecasting Domoic Acid Levels From Harmful Algal Blooms Along the Pacific Northwest Coast".
  - Yuqin Ma (The Harker School, CA), "CABMS ... Deep, Spatiotemporal, Multivariate Prediction and Sensor-Based Data Transmission".

**Stockholm Junior Water Prize track (HAB treatment; ISEF participation not confirmed)**
- **Annabelle Rayson** (Sarnia, Ontario, Canada) won the international 2022 Stockholm Junior Water Prize. Her project used biomanipulation: finding which zooplankton species best treat and prevent algal blooms. Her father, a Great Lakes commercial fisherman, was her motivation. VERIFIED: [ES&E Magazine](https://esemag.com/water/ontario-highschooler-wins-stockholm-water-prize/); [Down To Earth](https://www.downtoearth.org.in/water/canadian-student-wins-2022-stockholm-junior-water-prize-84642)
  - How it differs from ours: a single biocontrol agent (grazers) tested for efficacy, with no trigger timing.
- **Saranya Anantapantula** (Spring-Ford Area HS, Phoenixville, PA) was a 2023 U.S. SJWP runner-up with "Meta-analysis of Field Experiments & Experimentation of Gypsum, an Inexpensive and Natural Treatment, Towards Effective, Low-Cost, High-Efficacy Algal Bloom Control". The meta-analysis was published as "Most treatments to control freshwater algal blooms are not effective: meta-analysis of field experiments" (Water Research, 2023). VERIFIED: [WEF 2023 state winners PDF](https://www.wef.org/globalassets/assets-wef/3-membership/stockholm-junior-water-prize/2023-sjwp-state-winners.pdf); [PubMed 37544109](https://pubmed.ncbi.nlm.nih.gov/37544109/); [WilsonLab page](https://www.wilsonlab.com/person/saranya-anantapantula/)
  - How it differs from ours: this is the most direct precedent for our 256-paper evidence scoreboard, and its finding that most field treatments fail is a result we must engage with. It tests one treatment (gypsum) rather than trigger timing.
- **Sathvika Siva and Diya Narayanan** (Lynbrook HS, CA) won 1st place in the 2026 California SJWP for HAB research and fertilizer pellets meant to prevent aquatic dead zones. VERIFIED per search snippet: [CWEA 2026](https://www.cwea.org/news/cwea-announces-californias-2026-stockholm-junior-water-prize-winners/)
  - How it differs from ours: prevention at the fertilizer source.

### Inferences
- In this sample no HAB treatment project reached First Award or a Top Award (Gordon E. Moore / Regeneron Young Scientist). The best result is Second Award (Natarajan 2024; Wu 2026). INFERRED from the pages cited above. I did not exhaustively check 2015-2021 Grand Award lists.
- Multi-year continuity is common among placers: Natarajan was in Year 5, Agrawal in Year 5 and Gaydar in Year III. Judges appear to reward projects that progress from lab to device to field.
- Special-award sponsors that fit HAB treatment are NOAA (Leone, Zhang), EPA Hurd Sustainability (Agrawal) and university scholarships (Muro). INFERRED: these are realistic targets for our project.

### Gaps
- The Society for Science abstracts database search URL returned 404 via fetch, so I could not do systematic keyword sweeps ("microcystin", "algicide", "barley straw", "ultrasound", "phage", "oyster", "kelp").
- Pre-2018 and 2020-2021 treatment projects are almost certainly under-sampled.
- The NOAA special-award winners page returned 403.
- Unconfirmed items: the ISEF category for Muro 2025, Savio Le's exact 2018 award, and the method details for Gaydar, Wu and Zhang.
- The 2023 full-awards release URL guess returned 404. The 2023 Grand Award HAB projects, apart from Natarajan's Third Award from the abstract, were not checked.

## Q2. Did winners test at field or mesocosm scale, test non-target safety, report cost, or partner with agencies, farms or universities?

### Takeaway
The strongest placers either went to the field (Muro reservoir; Agrawal golf course with county officials; Natarajan drone plus float) or framed the work on low cost (Leone; Agrawal; Anantapantula). Explicit non-target testing appears only for Muro, where other microbes were unharmed. None of the sources describe pre-registration, false-alarm controls or treatment-timing experiments.

### Cited Findings
- Field scale:
  - Muro tested in a HAB-closed reservoir or lake, and other microbes were unharmed — [SN Explores](https://www.snexplores.org/article/peroxide-fight-algal-blooms)
  - Agrawal field-tested at a NJ golf course with county officials — [EPA](https://www.epa.gov/newsreleases/innovative-water-quality-project-new-jersey-high-school-student-wins-epa-award)
  - Natarajan used drone surveillance and a floating sensor device — [SfS abstract 23488](https://abstracts.societyforscience.org/Home/FullAbstract?Category=Any+Category&AllAbstracts=True&FairCountry=Any+Country&FairState=Any+State&ProjectId=23488)
- Cost framing:
  - Leone: "inexpensive, readily available ... alternative to expensive, outsourced clays" — [SfS abstract 18428](https://abstracts.societyforscience.org/Home/FullAbstract?ProjectId=18428)
  - Agrawal: "low-cost, eco-friendly", with mushroom revenue — [EPA](https://www.epa.gov/newsreleases/innovative-water-quality-project-new-jersey-high-school-student-wins-epa-award)
  - Natarajan: "cost-effective" — [JEI 22-200](https://emerginginvestigators.org/articles/22-200)
- Statistical rigor: Leone reported a linear mixed model at p<0.05 — [SfS abstract 18428](https://abstracts.societyforscience.org/Home/FullAbstract?ProjectId=18428)
- Evidence synthesis: Anantapantula published a peer-reviewed meta-analysis of field experiments — [PubMed](https://pubmed.ncbi.nlm.nih.gov/37544109/)

### Inferences
- Our pre-registration, the false-alarm and late-treatment control arms, and the evidence scoreboard look distinctive in this sample. The weak spot relative to winners is the lack of a field or mesocosm test and of a partner (DEEP or UConn could fill that). INFERRED.
- Using non-toxic algae in tanks is safer, but it is less realistic than Leone (K. brevis) or Muro (a real bloom). Judges may ask about that transfer. INFERRED.

### Gaps
- Replication (n), controls and effect sizes for Muro, Natarajan and Agrawal are not in the sources I could read.

## Q3. Any projects combining sensing or automation with treatment (closed-loop, IoT, robots)?

### Takeaway
Yes, one clear case: Sharanya Natarajan's Hub & Spoke system (ISEF 2023 Third Award, 2024 Second Award), which combines drone and float sensing, an ML model and a remote-dispersed alum-bentonite flocculant. It appears operator-in-the-loop (remote control) rather than an automatic forecast-triggered on/off loop. Muro's device is automated only passively (wave-driven release).

### Cited Findings
- The suppression agent is dispersed "via remote control", and there is a 24/7 cloud dashboard hub — [SfS abstract 23488](https://abstracts.societyforscience.org/Home/FullAbstract?Category=Any+Category&AllAbstracts=True&FairCountry=Any+Country&FairState=Any+State&ProjectId=23488)
- "preemptive detection & suppression", with a Wi-Fi microcontroller float — [JEI 22-200](https://emerginginvestigators.org/articles/22-200)
- Wave-powered passive peroxide release — [SN Explores](https://www.snexplores.org/article/peroxide-fight-algal-blooms)
- Search surfaced US patents titled "Harmful algae bloom mitigation system" (US 12351494) and "Autonomous system and method for monitoring and improving water quality by mitigating harmful algal blooms" (US 12129191) — [USPTO 12351494](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12351494); [USPTO 12129191](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12129191). Inventors could not be read (scanned PDF), so any link to a student is UNVERIFIED.

### Inferences
- Our key point of difference from Natarajan is automatic triggering from a forecast plus switching off at recovery, tested against false-alarm and late-treatment controls. Neither Natarajan nor Muro reports that. INFERRED.
- Judges who saw Natarajan will compare directly, so the prior art check should cite the patents above. INFERRED.

### Gaps
- Inventors and assignees of the USPTO patents were not confirmed.

## Q4. Which went on to the Stockholm Junior Water Prize, Regeneron STS, JSHS, patents or publications?

### Takeaway
- Muro became a Regeneron STS 2026 finalist.
- Natarajan published in JEI (2023).
- The Kwoks placed 3rd in the California SJWP (2022).
- Anantapantula (SJWP US runner-up 2023) published in Water Research.
- Rayson won the international SJWP (2022).

I found no JSHS links or confirmed student patents.

### Cited Findings
- Muro, STS 2026 finalist — [SN Explores](https://www.snexplores.org/article/peroxide-fight-algal-blooms)
- Natarajan, JEI article — [JEI 22-200](https://emerginginvestigators.org/articles/22-200)
- Kwoks, California SJWP 3rd place — [CWEA](https://www.cwea.org/news/fresno-students-win-california-stockholm-junior-water-prize/)
- Anantapantula, U.S. SJWP runner-up and Water Research 2023 — [WEF PDF](https://www.wef.org/globalassets/assets-wef/3-membership/stockholm-junior-water-prize/2023-sjwp-state-winners.pdf); [PubMed 37544109](https://pubmed.ncbi.nlm.nih.gov/37544109/)
- Rayson, 2022 international SJWP — [Down To Earth](https://www.downtoearth.org.in/water/canadian-student-wins-2022-stockholm-junior-water-prize-84642)
- Agrawal, EPA National Sustainability Design Expo invitation — [EPA](https://www.epa.gov/newsreleases/innovative-water-quality-project-new-jersey-high-school-student-wins-epa-award)

### Inferences
- The SJWP is a natural second venue for our project. Anantapantula's meta-analysis is the key paper to cite and differentiate from, since our scoreboard covers similar ground. INFERRED.

### Gaps
- I could not open the Water Research abstract (PubMed captcha), so study counts and effect sizes are unverified.
- The SIWI international winners page returned 404.
- No JSHS or patent outcomes were verified for any project above.
