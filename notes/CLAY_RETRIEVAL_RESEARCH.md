# Flocculation + retrieval of algal floc: what has actually been done

Written 2026-09-15 from a web research pass (~55 fetches; research agent, this session; Step 1 of the device plan). Companion to notes/CLAY_FLOCCULATION_RESEARCH.md (clay that sinks) and notes/AERATION_RESEARCH.md. Four primary reports were read in full (FDEP INV002 Lake Jesup, INV003 ARP Pond, INV024 Indian River Lagoon; PJOES magnetic-clay paper) plus USGS SIR 2024-5091, the NOWPAP HAB countermeasures booklet, PNNL-35507 and FDEP Emergency Final Order 18-1100. Where only an abstract or snippet was reachable it says so. Computed values are marked [inferred].

## 1. Magnetic modified clay / magnetic flocculants

**Fan et al. 2026, Pol. J. Environ. Stud. 35(3):4139-4150 (PJOES), magnetic bentonite/kaolinite + CPAM.** Full text read. Synthesis: 1 g bentonite (200 mesh) in 100 mL distilled water, sonicated 10 min; add 1.96 g FeCl3.6H2O + 0.9 g FeCl2.4H2O, stir 10 min; pH 10-11 with NH3.H2O; 60 C for 3 h; separated with a permanent magnet; washed 3x ethanol/water; dried 65 C. Same recipe for kaolinite. [inferred: Fe3+:Fe2+ ~1.6:1 molar; theoretical Fe3O4 ~0.84 g per 1 g clay.] Species: Microcystis aeruginosa (freshwater), 50 mL batches. Optimum: magnetic clay:CPAM 1:1, pH 2, 150 rpm, 10 min, 0.8 g/L magnetic bentonite or 0.4 g/L magnetic kaolinite; Box-Behnken optimum 0.206 g/L, 12.9 min, 170.6 rpm -> 92.13% measured. Floc D50 65-68 um vs 2.4 um cells. NOT reported: magnetic field strength, capture time, recovery fraction of floc or clay, reuse cycles, residual Fe, cost. Removal was measured after settling, not after magnetic capture [inferred from Methods]; reusability listed as future work.

**Ma et al. 2019, J. Cleaner Prod. 248:119276, Fe3O4/CPAM on algae-laden raw water.** Chlamydomonas; >97% Chl-a, 87% turbidity at 1.2 mg/L Fe3O4/CPAM, mass ratio 1.5:1, pH 4-9; recovery and reuse tested but values paywalled. Freshwater.

**Magnetic buoyant beads, J. Environ. Chem. Eng. 2023 (10.1016/j.jece.2023.110170).** Fe3O4 on closed-cell perlite, CPAM pre-flocculant. Removal >97.6% for Chlorella, Microcystis, Anabaena; CPAM raised removal 27-46 points over beads alone; beads + algae "easily separated by applying a magnetic field." Freshwater; no dose, field strength, recovery % or reuse data reachable.

**Iron-oxide-immobilized bioflocculants, ESPR 2026 (PMID 42237017).** Microcystis, ~96% at pH 7, 37 C, 120 rpm, 60 min settling; reusable 4 times. Freshwater.

**Liu, Li & Zhang 2009, Water Sci. Technol.** 4 mg/L Fe3O4 + 1.6 mg/L chitosan: >99% cells, 73.9% TN; "ionic strength had a negative effect on removal efficiency" (warning for seawater).

**Reuse/recovery (magnetic flocculants generally, review snippets, verify before quoting):** particle recovery 84-97.5% via sonication + alkali; 5 cycles typical, 10 with bare Fe3O4; CPAM-grafted Fe3O4 lost efficiency sharply on reuse. Magnetite detaches from flocs at 1,500 Oe or 1,500-2,000 g. Energy/cost (topic summary, unverified): low-gradient magnetic separation 0.05-0.1 kWh/m3; $0.13/m3 at 300 mg/L particles vs $0.52/m3 for HGMS at 50 mg/L.

**Marine/seawater, explicit answer:** No magnetic clay (Fe3O4-on-kaolinite/bentonite) study used seawater or a marine HAB species; all of the above are freshwater. Magnetic materials used in seawater: (a) Japan, Suga 1982 (lab): Fe3O4 + FeCl3 powders + flocculant through a magnetic separator, >80% removal of Chattonella, needing >=10 g iron powder per litre; environmental impacts "unknown" (NOWPAP). (b) Natural magnetic sphalerite, J. Hazard. Mater. 2017: Chattonella marina removed at 1-2 g/L, better at >25 C, salinity >30, pH <7.5; "excellent stability after magnetic recycling" (no cycle count). (c) Cerff et al. 2012: silica-coated magnetic particles, >95% separation of marine Phaeodactylum and Nannochloropsis cultures, HGMS. (d) Hu et al. 2013: naked Fe3O4 120 mg/L, >95% of Nannochloropsis maritima in 4 min, medium recycled 5x. All beaker scale; none on Karenia, Prorocentrum, Skeletonema, Alexandrium or Heterosigma; none in a natural bloom. IOCAS modified-clay work and its spraying patent contain no magnetic or recovery component.

## 2. Flocculation + DAF for blooms in open water

**USACE HABITATS / AECOM.** July 2019, Lake Okeechobee: three weeks, 100 gpm pilot; "100 million gallons a day" was an aspiration (NPR). Coagulant reported: aluminum chlorohydrate (ACH) 30-50 mg/L (unverified in the bot-blocked PDF). Shipboard prototype 400 gpm. Chautauqua Lake NY, Aug-Sep 2020: 205,000 gal treated -> 700 gal algae paste; DAF + ozone + screw press; each module "up to 2 MGD". USGS SIR 2024-5091 techno-economics for the 90-day 2018 event: N+P valued at $2.72/lb; removal 1,078-4,198 lb N+P/day; capex $674k-$1.04M; O&M $3.9-7.3M; net benefit -$2.1M to +$0.8M; "demand has not been demonstrated" for biomass products.

**FDEP Innovative Technology grants (AECOM Hydronucleation Flotation Technology, reports read in full):**
- Lake Jesup (INV002), $1.6M, 100 gpm barge, Sept 2021-May 2022: 388.75 h, 2.42M gal treated, 6,595 gal slurry (76% to a WWTP). Dose 40 mg/L ACH + 2 mg/L polyacrylamide; recycle 27-30%; 1.6-2 skims/h. Removal: Chl-a 85% (132 -> 22 mg/m3), TSS 83%, TP 85%, TN 43%. Energy 5.88 kW, 2,290 kWh [inferred 0.25 kWh/m3]. Effluent failed several chronic Ceriodaphnia tests, attributed to raw lake water. Scale-up cost: $739/lb TP and $54/lb TN at 1 MGD ($319/$23 at 40 MGD); capex $1.9M (1 MGD) to $43.3M (40 MGD). Meeting the in-lake TMDL share needs 40 MGD running 24/365.
- ARP Pond, Tallahassee (INV003), $1.65M, 1 MGD unit, Nov 2021-Jun 2022: 480 h on 79 days, 14.5M gal, 16,720 gal slurry. 20 ppm ACH + 1 ppm polymer: Chl-a 80% mean/94% median, TP 80/88%, TN 40/45%. Energy 18.68 kW [inferred 0.16 kWh/m3]. No acute/chronic toxicity.
- **Indian River Lagoon, brackish (INV024), $999k, 700 gpm barge, Sep-Nov 2023, salinity 19-20 ppt:** 191.5 h, 4.03M gal treated, only ~255 gal slurry at 8% solids, landfilled. ACH 18.7 mg/L + anionic polyacrylamide 0.7 mg/L; recycle 45% vs 20-30% in freshwater because "high salinity reduces air saturation as well as the mobility of bubbles and flocs"; one skim per 55,085 gal. Removal: **Chl-a 21%, TP 26%, TN 0%**, turbidity 75%; effluent DO +1.12 mg/L; TSS *higher* in effluent from wave-induced float-blanket carryover. Full-scale estimate $1.96M/yr, $0.88 per 1,000 gal. **The only saline DAF-harvest field trial found, and the closest analogue to Long Island Sound.**
- Lake Agawam NY, Oct 2019 (2 weeks, 120 gpm): >90% Chl-a, microcystins and TP; >80% TSS and TN; >$9M then secured for three 1 MGD harvesters.
- Lee County 2018 emergency vacuum removal (AECOM): $850k; 115,000+ gal slurry by 23 tankers; liquids to an RO plant then deep well, solids to landfill.
- Pahokee Marina/Franklin Lock 2021: $1M total.

**Chinese lakes.** Taihu wet-algae salvage 0.8 Mt (2008) to 1.6 Mt (2016); >10 Mt wet since 2007; >10,000 t dry powder. Wuxi: 14 bases up to 66,500 t/day. Bionic salvage platform 12 x 11 m, ~$290k, "<0.05 yuan per tonne of water". Dianchi harvest boats: CPAM 0.5-2 mg/L + 35 um rotary drum filter, >95% biomass removal in a 20,000 m3 enclosure, effluent Chl-a <8 ug/L, 0.053 kWh/m3 (PMID 33792846). Slurry 96% water.

**Seawater DAF at desalination intakes.** Li et al. 2026 (pilot): 0.5 mg/L NaClO pre-oxidation, 12 mg/L PAC, 0.2 mg/L cationic PAM; DAF + sand filter >95% algae. Villacorte et al. 2015: >75% with inline FeCl3.

**Microalgae DAF harvesting benchmarks.** Ton-scale DAF (5 m3/h) + screw press: 93% harvest, 1.7 kWh/m3 (PMID 39603474); ballasted DAF 99% at 0.04 kWh/m3; Chlorella dispersed-air flotation 98.7% with 40 mg Al3+ + 60 mg CTAB per g biomass, ~700 um bubbles, 15 min (PMC5717653).

**US 9,809,464 (Bryan, 2013):** pontoon boat with serial DAF channels, scum trough, diffused air; no coagulant dosing, no throughput, no field data. **ERDC RAFT** (TR-23-6): xanthan gum + CPAM + microbubbles in 14,000 gal ponds raised surface phycocyanin 5 -> 30 RFU; 2022 field demo formed a surface layer within 30 min.

## 3. Buoyant / floating flocculants

- Self-branched chitosan + CaO2@PEG (Carbohydr. Polym. 2021): released O2 floats flocs; reduced DO depletion and TP; zebrafish-biocompatible. No dose/% reachable.
- Chitosan-coated fly-ash cenospheres (ESPR 2020): 0.3-0.7 g/L, 98.5% Microcystis, >90% in 5 min.
- Fe3O4/closed-cell perlite (section 1) combines buoyancy and magnetism.
- Recovery in all three is skimming the floating layer; none reports a recovered-fraction figure. All freshwater.

## 4. Surface skimmers and booms

AECOM used oil-spill-type skimmers at Pahokee Marina and vacuum trucks in Lee County. Taihu operates the only routine large-scale skimming fleet. Lake Erie: Ohio Sea Grant says no practical harvest exists and cost "would be astronomical". Bycatch: FDEP trials tested effluent toxicity (mysid, silverside, Ceriodaphnia, fathead minnow) but reported no organism bycatch counts; no permit condition on bycatch found.

## 5. Sunk vs retrieved floc outcomes

- PAC-kaolinite (MCII) on Karenia, 80 L mesocosms (PMC12656167): 0.2 g/L; 91% at 5 h; sediment brevetoxin 191 -> 56 ng/g by 72 h; clams 5.1x Al, no mortality; DO "within normal ranges"; harvesting not evaluated.
- 1,400 L mesocosms, Harmful Algae 2024 (PMID 38705612): 0.2 g/L MCII; 57% at 8 h, 95% at 48 h; crab, urchin, clam responses no different from untreated.
- EPA ECOHAB final report: resuspended clay at 0.25 g/L cut clam growth ~90% while sedimented clay had no effect; settled floc retained brevetoxin after 96 h; PAC-treated clay is "fluffy" and easier to resuspend.
- Korea NFRDI: 5-year benthic survey in sprayed areas found no change (NOWPAP). WHOI mesocosm: benthic abundance +121% vs +56% control.
- Chitosan-soil column study (Frontiers 2018): sediment TN improved only when an O2-loaded zeolite cap was added; bare floc did not improve it.
- Floc size vs oxygen (Water Res. 2026, PMID 41547202): macroflocs >200 um consume less O2 per mass than <50 um flocculi; tidal shear breaks flocs into small, oxygen-demanding particles. Relevant to LIS.
- Harvesting side: IRL harvester effluent DO rose 1.12 mg/L. **No study directly compares bottom DO or sediment nutrients after sunk floc versus harvested floc.**

## 6. Nutrient export accounting

- PNNL-35507 (AECOM-harvested biomass): Lake Jesup slurry ash 33% dry, protein 32%, lipid 2%; process-model feed N 3.1 wt% AFDW, P 0.3 wt%; HTL biocrude minimum selling price $4.65-12.95/GGE.
- Dried Taihu cyanobacteria N 11.4%; ~50% protein.
- Wet-to-dry: DAF slurry 8% solids (IRL); Taihu station slurry 96% water; Korean DAF sludge 90% -> 82.6% after drainage.
- Fate: WWTP (Jesup, ARP), landfill (IRL, Lee, Taihu historically), compost (Taihu), HTL biocrude (HABITATS), fish feed trials.
- Crediting: no case found where harvested N or P was formally credited to a TMDL or traded; USGS values removed N+P at $2.72/lb while noting no demonstrated market.

## 7. Stats table

| System | Medium | Flocculant, dose | Retrieval | Removal | Recovery | Throughput | Cost | Energy | Time | Scale | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Magnetic bentonite+CPAM (PJOES 2026) | fresh | 0.206 g/L + CPAM 1:1, pH 2 | magnet (lab); settling measured | 92% cells | n/r | 50 mL | n/r | n/r | 13 min | beaker | pjoes.com |
| Fe3O4/CPAM (JCP 2019) | fresh | 1.2 mg/L, 1.5:1 | magnet | >97% Chl-a | tested, n/r | beaker | n/r | n/r | n/r | beaker | S0959652619341460 |
| Fe3O4/perlite beads (JECE 2023) | fresh | CPAM 80 mg/L | float + magnet | 97.6-98% | n/r | beaker | n/r | n/r | n/r | beaker | S2213343723009090 |
| Fe3O4-bioflocculant (ESPR 2026) | fresh | pH 7, 120 rpm | magnet | ~96% | 4 reuses | beaker | n/r | n/r | 60 min | beaker | PMID 42237017 |
| Magnetic sphalerite (JHM 2017) | marine | 1-2 g/L | magnet | high | recyclable | beaker | n/r | n/r | n/r | beaker | PMID 27847251 |
| Japan iron powder (Suga 1982) | marine | >=10 g Fe/L + flocculant | magnetic separator | >80% Chattonella | n/r | lab | n/r | n/r | n/r | lab | NOWPAP |
| HABITATS Okeechobee 2019 | fresh | ACH 30-50 mg/L (unverified) | DAF skim + ozone | n/r | n/a | 100 gpm | USGS scenario $4.6-8.4M/90 d | n/r | 3 wk | pilot | fox4now; USGS |
| HABITATS Chautauqua 2020 | fresh | organic flocculants | DAF + screw press | n/r | 700 gal paste / 205,000 gal | 400 gpm | see USGS | n/r | 5 d | pilot | dvidshub |
| AECOM Lake Jesup 2021-22 | fresh | ACH 40 + PAM 2 mg/L | DAF, 1.6-2 skims/h | Chl-a 85%, TP 85%, TN 43% | 6,595 gal slurry | 100 gpm | $739/lb TP, $54/lb TN (1 MGD) | 0.25 kWh/m3 [inf] | 389 h | pilot barge | INV002 |
| AECOM ARP Pond 2021-22 | fresh | ACH 20 + PAM 1 ppm | DAF | Chl-a 80-94%, TP 80-88% | 16,720 gal slurry | 1 MGD | $1.65M project | 0.16 kWh/m3 [inf] | 480 h | pilot | INV003 |
| **AECOM IRL 2023** | **brackish 19-20 ppt** | ACH 18.7 + anionic PAM 0.7 mg/L | DAF, 1 skim/55,085 gal | **Chl-a 21%, TP 26%, TN 0%** | 255 gal at 8% | 700 gpm | $0.88/1,000 gal; $1.96M/yr | 100 kW genset | 192 h | pilot barge | INV024 |
| Lee County 2018 vacuum | fresh/estuarine | none | vacuum trucks | n/r | 115,000+ gal | 30,000 gal/weekend | $850k | n/r | Aug-Sep | emergency | leegov.com |
| Taihu salvage fleet | fresh | none/flocculant at stations | skimmer boats + stations | n/r | 0.8-1.6 Mt wet/yr | 66,500 t/day (Wuxi) | $290k/platform | n/r | year-round | full | PMC8538822; MEE |
| Dianchi flocculation-drum boat | fresh | CPAM 0.5-2 mg/L | 35 um drum filter | >95% biomass | n/r | 20,000 m3 enclosure | n/r | 0.053 kWh/m3 | n/r | field | PMID 33792846 |
| Desal DAF (Li 2026) | marine | PAC 12 + PAM 0.2 mg/L + NaClO | DAF float | >95% w/ sand filter | n/a | pilot | n/r | n/r | n/r | pilot | PMID 42470165 |
| DAF + screw press (2024) | fresh culture | n/r | DAF | 93% | 11.9% cake | 5 m3/h | n/r | 1.7 kWh/m3 | n/r | ton-scale | PMID 39603474 |
| Korea loess spraying | marine | 100-400 g/m2 | none (sinks) | ~80% Cochlodinium (lab) | none | vessel | $210k/vessel | n/r | 30-40 min intervals | full | NOWPAP |
| MCII Karenia mesocosm | marine | 0.2 g/L PAC-kaolinite | none (sinks) | 91% at 5 h; 95% at 48 h | none | 80-1,400 L | clay ~$600/t + $100/t shipping | n/a | n/a | mesocosm | PMC12656167; WHOI |

## 8. Regulatory

- Florida 2018: Executive Order 18-191 and FDEP Emergency Final Order 18-1100 suspended procurement and employment statutes for emergency response; they did not waive water-quality or dredge/fill permits. Lee County's removal plan was separately approved by FDEP.
- Lake Jesup harvesting: F.A.C. 62-330.485 (environmental restoration general permit), a USACE "No Permit Required" determination, and an FDEP Industrial Wastewater/NPDES permit for returning treated water; the barge operated only "within a FDEP-permitted area". ARP Pond likewise.
- USACE HABITATS authority: WRDA 2018 research authorisation.
- Clay: China listed modified clay as a standard method in 2014 guidelines; Korea disperses loess on NFRDI alerts; Florida clay trials use permitted demonstration sites. **No permitting document distinguishes removal from deposition of clay or floc in coastal water**; the Florida DAF permits treat harvesting as an industrial discharge plus restoration activity.

## 9. What has never been done

1. Magnetic modified clay in seawater, on any marine HAB species, or beyond a beaker.
2. Measurement of the recovered fraction of clay or floc after magnetic capture in any HAB study (PJOES measured settling, not capture).
3. Any flocculation-plus-retrieval trial in tidal or wave-exposed water other than the 2023 IRL barge, whose float blanket broke up in waves.
4. Forecast-triggered, low-density pre-emptive dosing; every deployment was reactive to a visible bloom.
5. A controlled comparison of bottom DO, sediment nutrients or benthic fauna after sunk versus harvested floc.
6. Formal TMDL or nutrient-credit accounting for harvested bloom biomass.
7. Residual Fe/Al measurements after magnetic-clay treatment.

## Bottom line

- Magnetic clay works on freshwater Microcystis at 0.2-0.8 g/L with CPAM, but no paper reports the magnet, capture time, recovered fraction or reuse loss, and none has touched seawater; the only seawater magnetic data are 1982 Japanese lab work (>=10 g Fe/L) and a 2017 magnetic-sphalerite study at 1-2 g/L.
- Flocculation + DAF harvesting is real and measured: 80-94% Chl-a and TP removal in freshwater at 20-50 mg/L ACH + 1-2 mg/L polymer, 0.16-0.25 kWh/m3, but $319-739 per lb TP.
- The single brackish deployment (IRL 2023, 19-20 ppt) collapsed to 21% Chl-a and 0% TN removal because salinity cut bubble efficiency and waves broke the float blanket: the closest analogue to Long Island Sound and a cautionary result.
- "100 million gallons a day" was an aspiration; pilots ran 100-700 gpm; USGS finds net benefit between -$2.1M and +$0.8M for a 90-day event.
- Sunk PAC-clay floc carries toxin and aluminium to sediment without acute mortality; nobody has measured whether retrieving the floc changes bottom oxygen.
- Harvested biomass is 33-44% ash, ~3% N and 0.3% P dry, 8% solids wet; disposal, not nutrient credit, is the current end point.
- Gaps 1-5 are open and small enough for a bench-to-mesocosm science-fair design.

## Sources
- https://www.pjoes.com/Experimental-Removal-of-Microcystis-aeruginosa-nby-Magnetic-Clay-Minerals-Synergized,205257,0,2.html
- https://www.sciencedirect.com/science/article/abs/pii/S0959652619341460
- https://www.sciencedirect.com/science/article/abs/pii/S2213343723009090
- https://pubmed.ncbi.nlm.nih.gov/42237017/ ; https://pubmed.ncbi.nlm.nih.gov/19342803/ ; https://pubmed.ncbi.nlm.nih.gov/27847251/ ; https://pubmed.ncbi.nlm.nih.gov/26609948/ ; https://pubmed.ncbi.nlm.nih.gov/22705536/ ; https://pubmed.ncbi.nlm.nih.gov/23639490/
- https://www.sciencedirect.com/science/article/pii/S2211926425004515 ; https://pubmed.ncbi.nlm.nih.gov/29968210/ ; https://www.sciencedirect.com/topics/engineering/gradient-magnetic-separation
- https://cearac.nowpap.org/nowpap/wp-content/uploads/2023/11/HAB_Booklet.pdf
- https://patents.google.com/patent/US10822258B2/en ; https://patents.google.com/patent/US9809464
- https://www.npr.org/2019/07/29/745666501/a-new-old-way-to-combat-toxic-algae-float-them-up-then-skim-them-off
- https://www.fox4now.com/news/protecting-paradise/u-s-army-corps-partners-with-private-sector-on-algae-cleanup-project
- https://www.dvidshub.net/news/380902/erdc-reports-chautauqua-lake-habitats-research-results
- https://extapps.dec.ny.gov/docs/water_pdf/nysdecusacehabwebf.pdf ; https://apps.dtic.mil/sti/trecms/pdf/AD1150054.pdf
- https://www.erdc.usace.army.mil/Portals/55/CERL/HABITATS/HABITATS%20Pilot%20Reaserch%20Study-%20ERDC%20TR-20-1.pdf?ver=2020-06-23
- https://ansrp.el.erdc.dren.mil/pdfs/gantt-pdfs/2024_Internal/05_Clinton_Cender_RAFT_FS.pdf
- https://pubs.usgs.gov/sir/2024/5091/sir20245091.pdf
- https://www.wateronline.com/doc/will-dissolved-air-flotation-fix-harmful-algal-blooms-0001
- https://floridadep.gov/owper/water-policy/content/innovative-technology-harmful-algal-blooms-final-reports
- https://floridadep.gov/sites/default/files/INV002.pdf ; https://floridadep.gov/sites/default/files/INV003.pdf ; https://floridadep.gov/sites/default/files/INV024.pdf
- https://www.hometownnewstc.com/news/aecom-demonstrates-algae-removal-system-in-indian-river-lagoon/article_970bafe2-57dd-11ee-bf30-37f39e686aab.html
- https://www.controlglobal.com/manage/sustainability/article/33013233/clearing-harmful-algal-bloom
- https://www.27east.com/southampton-press/news/government-news/article_457ddfd7-7bbc-599c-a9b4-f25b65fe7464.html ; https://www.danspapers.com/2019/10/combating-harmful-algal-blooms-in-lake-agawam/ ; https://www.southamptontownny.gov/1701/Lake-Agawam-Algae-Harvesting-Phase---SH-
- https://www.leegov.com/waterqualityinfo/bluegreenalgae
- https://bluegreenwatertech.com/post/florida-spent-1-million-on-toxic-algae-in-caloosahatchee-pahokee-marina ; https://www.lakeonews.com/stories/six-different-companies-to-try-to-clean-lake-o,84080
- https://pmc.ncbi.nlm.nih.gov/articles/PMC8538822/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC5684341/
- https://english.mee.gov.cn/News_service/media_news/201704/t20170411_409623.shtml ; http://english.scio.gov.cn/chinavoices/2025-03/14/content_117765961.html ; https://www.scmp.com/news/china/science/article/3189608/chinese-scientists-clear-blue-green-algae-bloom-massive-lake
- https://pubmed.ncbi.nlm.nih.gov/33792846/ ; https://pubmed.ncbi.nlm.nih.gov/42470165/
- https://darchive.mblwhoilibrary.org/bitstream/1912/7240/1/2015_Villacorte_etal_SWRO_HABs_accepted%20manuscript.pdf
- https://pubmed.ncbi.nlm.nih.gov/39603474/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC5717653/
- https://pubmed.ncbi.nlm.nih.gov/33673989/ ; https://pubmed.ncbi.nlm.nih.gov/32440871/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12656167/ ; https://pubmed.ncbi.nlm.nih.gov/38705612/
- https://cfpub.epa.gov/ncer_abstracts/index.cfm/fuseaction/display.abstractDetail/abstract_id/1014/report/F
- https://www2.whoi.edu/site/andersonlab/current-projects/florida-clay-mitigation/
- https://coastalscience.noaa.gov/project/application-of-clay-flocculation-for-removal-of-karenia-brevis-cells-and-toxins-in-southwest-florida-coastal-waters/
- https://mote.org/news/article/rapid-test-of-red-tide-mitigation-strategy-deployed-in-sarasota ; https://www.sarasotamagazine.com/news-and-profiles/2021/07/clay-focculation-red-tide ; https://hoodline.com/2026/04/sarasota-science-squad-takes-big-swing-at-red-tide-menace/
- https://www.sciencedirect.com/science/article/abs/pii/S1568988303000416
- https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2018.00060/full
- https://pubmed.ncbi.nlm.nih.gov/41547202/ ; https://pubmed.ncbi.nlm.nih.gov/29286322/ ; https://pubmed.ncbi.nlm.nih.gov/39567062/
- https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-35507.pdf
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9233212/ ; https://www.sciencedirect.com/science/article/abs/pii/S2211926425005181
- https://floridadep.gov/sites/default/files/18-1100_0.pdf ; https://floridadep.gov/ogc/ogc/content/2018-final-orders
- https://www.floridadisaster.org/news-media/news/20180709-gov.-scott-issues-emergency-order-to-combat-algal-blooms-in-south-florida/
- https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-62-330-485
- http://english.scio.gov.cn/chinavoices/2018-11/28/content_74218061.htm
- https://www.epa.gov/chesapeake-bay-tmdl/trading-and-offsets-chesapeake-bay-watershed
