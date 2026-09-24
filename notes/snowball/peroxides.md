# Snowball: hydrogen peroxide, solid peroxides, and other oxidizers (ozone, permanganate, UV)

Compiled 2026-09-24 from Part 2 of `HAB_MITIGATION_LITERATURE.md` (the "Hydrogen peroxide / peroxides" and "Oxidation / UV" rows of `HAB_MITIGATION_SOURCES.csv`), then one more level of OpenAlex citing and referenced works from 12 seed papers (347 peroxide/oxidant-titled hits, filtered by hand), plus PubMed, Europe PMC, and web searches for field trials and agency pages. 45 entries.

**Summary.**
1. **Best teen experiment #1: a selectivity jar test.** Dilute drugstore 3% H2O2 to 0-10 mg/L. Add it to a mixed jar of a non-toxic cyanobacterium (*Synechococcus* or *Anabaena* from a supplier) and a green alga (*Chlorella*). Run it under bright and dim light, and at low and high algal density. This reproduces #18 and #29-#31: cyanobacteria are about 10x more sensitive, the effect is stronger in bright light, and green algae soak up the peroxide and protect the cyanobacteria.
2. **Best teen experiment #2: a marine, small-cell-versus-large-cell test (relevant to Long Island Sound).** Add 0-2 mg/L H2O2 to artificial seawater holding a tiny alga (*Nannochloropsis* or *Micromonas*, standing in for brown tide) and a diatom (*Phaeodactylum* or *Thalassiosira*). This copies the brown-tide design in #3, where 1.6 mg/L wiped out the 2-µm *Aureococcus* but spared cells larger than 2-3 µm.
3. **Best teen experiment #3: slow-release, retrievable peroxide.** Put sodium percarbonate (pure, the active ingredient of oxygen bleach) or calcium peroxide into a fabric "tea bag" and compare it with liquid H2O2. Track the release curve with peroxide test strips, the algae killed, and *Daphnia* survival (#15, #34). The bag can be pulled back out of the water, which speaks to the counselor's "can't be retrieved" objection.
4. **Environmental consensus.** H2O2 breaks down to water and oxygen within about 1-3 days and leaves no residue. At 2-5 mg/L in fresh water it is fairly selective for cyanobacteria. The non-target organisms most at risk are **rotifers and small cladocerans** (*Daphnia*, *Moina*, *Ceriodaphnia*), which suffer above roughly 2-5 mg/L. Bacterial communities shift and then recover within days. Toxins leak out of the cells but are oxidized within days.
5. **Caveats.** The effect is short. Blooms returned in 1-2 weeks in dense, flowing or open waters, and after 3-7 weeks in closed lakes (#1, #4, #6, #10, #17, #26). Marine blooms need 10-50 mg/L, which kills zooplankton (#2) and can make the water *more* toxic to fish gills (#39). Selectivity is weaker than advertised for diatoms and mixotrophs (#38).

---

## A. Whole-lake and field applications

### 1. Whole-lake H2O2 treatment, Lake Koetshuis (Matthijs et al., 2012) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.watres.2011.11.016 (PubMed 22112924)
- **What they did:** *Planktothrix agardhii* in a Dutch recreational lake. They ran lab tests, then in-lake enclosures, then dispersed 2 mg/L (60 µM) through the entire lake with a "water harrow".
- **Environment:** eukaryotic phytoplankton (greens, cryptophytes, chrysophytes, diatoms), zooplankton and macrofauna were "largely unaffected". The peroxide degraded within a few days.
- **Results:** photosynthetic vitality fell by more than 70% within hours. Cyanobacteria and microcystin collapsed by 99% within a few days, and cyanobacteria stayed low for 7 weeks.
- **Effective?** Yes, for about 7 weeks. It is the founding field case.
- **Teen-reproducible?** Partly. The jar pre-test is easy, but the lake dispersal is not.
- **Read:** abstract only.

### 2. Brackish-creek treatment of a toxic *Alexandrium* bloom (Burson et al., 2014) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.hal.2013.10.017 · https://research.wur.nl/en/publications/termination-of-a-toxic-alexandrium-bloom-with-hydrogen-peroxide
- **What they did:** *A. ostenfeldii* at more than 1 million cells/L in the brackish Ouwerkerkse Kreek, Netherlands (it had killed a dog). They ran lab dose tests, then a canal test, then brought **50 mg/L** into the whole creek with a water harrow.
- **Environment:** zooplankton were "strongly affected". Macroinvertebrates and fish showed minimal impact. The peroxide decayed within a few days.
- **Results:** vegetative cells and pellicle cysts fell 99.8% within 48 h, and PSP toxins dropped below 15 µg/L. *Alexandrium* came back at lower levels the next year.
- **Effective?** Yes, as an emergency tool. It was the first marine or brackish field success, but at a dose 25x the freshwater one.
- **Teen-reproducible?** No at field scale. It is also the key evidence that marine targets need far more peroxide.
- **Read:** abstract only.

### 3. Brown tide (*Aureococcus*) cultures and Barnegat Bay microcosms (Randhawa et al., 2012; plus growth-phase follow-up, 2013) [peer-reviewed]
- **Link:** https://doi.org/10.1371/journal.pone.0047844 (PLOS ONE, open access) · https://doi.org/10.1016/j.aquatox.2013.08.015
- **What they did:** 50 mL cultures in 250 mL bottles at 19 °C and 120 µE, 12:12 light. They tested 1.6 mg/L H2O2 on *A. anophagefferens* and 11 other marine species, then ran 450 mL microcosms of Barnegat Bay (NJ) seawater spiked with *Aureococcus*. The 2013 study tested 0.4-1.6 mg/L on exponential-phase versus stationary-phase cells.
- **Environment:** cells larger than about 2-3 µm (5 diatoms, *Dunaliella*, *Isochrysis*, *Emiliania*, *Amphidinium*, *Prorocentrum*) were largely unaffected. The tiny green *Micromonas* was eradicated. Microcosm diatoms and greens dipped briefly and then exceeded the controls within 72 h. Cyanobacteria were down about 50%.
- **Results:** 1.6 mg/L wiped out a high-density brown tide within 24 h. Stationary-phase (late-bloom) cells needed 30-40% less H2O2 to reach 90% removal within 12 h. The paper's own scale-up for a 5×5 km bay 1 m deep needs pumping capacity of about 1,300 million gallons per day.
- **Effective?** Yes, in bottles. Selectivity comes from **cell size**, which is relevant to Long Island Sound's brown-tide bays.
- **Teen-reproducible?** **Yes.** Artificial seawater, a non-toxic small alga plus a diatom from a culture collection, 3% H2O2 diluted to 1-2 mg/L, and chlorophyll by colour or a cheap fluorometer.
- **Read:** full text of the 2012 paper (methods and species list); abstract only for 2013.

### 4. Three Dutch lakes: phytoplankton and zooplankton shifts (Piel et al., 2024) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.hal.2024.102585
- **What they did:** whole-lake treatments of three lakes at an average of 2-5 mg/L. Targets were *Dolichospermum*, *Aphanizomenon*, *P. rubescens* and *P. agardhii*.
- **Environment:** eukaryotic phytoplankton were not significantly affected. **Rotifers declined strongly after most treatments unless the dose was ≤2 mg/L.** Cladocerans were mildly affected and copepods least. Microcystins and anabaenopeptins were released, then disappeared within a few days.
- **Results:** cyanobacteria fell by as much as more than 99%. **A new bloom developed within several weeks in all three lakes**, and two lakes were treated a second time.
- **Effective?** Partly. The knockdown is strong, but it has to be repeated.
- **Teen-reproducible?** Partly. The rotifer sensitivity is testable with rotifers from a supplier (*Brachionus* is sold as fish food).
- **Read:** abstract only.

### 5. Four Long Island lakes (Lusty & Gobler, 2020) [peer-reviewed]
- **Link:** https://doi.org/10.3390/toxins12070428 (open access; PMC7405413)
- **What they did:** 11 bottle experiments in 4 L bottles on an outdoor flow-through table. Water came from Lake Agawam, Mill Pond, Georgica Pond and Roth Pond (Long Island, NY). The dose was **4 mg/L**; the abstract's "4 µg/L" is a typo, and the methods and conclusions say mg/L.
- **Environment:** eukaryotic algae (mainly greens) increased in 75% of experiments. Actinobacteria, Planctomycetes and Verrucomicrobia bacteria were the most harmed. In some runs, dissolved microcystin was slightly *higher* after treatment (0.85 vs 0.56 µg/L).
- **Results:** cyanobacteria fell in 10 of 11 experiments, from 85% to 29% of the community on average. *Planktothrix* was very sensitive, *Microcystis* moderately, and *Cylindrospermopsis* least. Levels mostly did **not** fall below guidance values.
- **Effective?** Partly. It reduces cyanobacteria but does not eliminate them in high-biomass water.
- **Teen-reproducible?** **Yes.** This is the closest local design: 4 L bottles of pond water outdoors. Handle bloom water with gloves.
- **Read:** full text, partly (results and conclusions via Europe PMC).

### 6. Repeated whole-pond dosing and "pollution swapping" (Lusty & Gobler, 2022) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.jes.2021.11.031
- **What they did:** 8 mg/L in mesocosms, plus **10 whole-pond applications over two years** in a eutrophic New York pond.
- **Environment:** **fecal-indicator bacteria (*E. coli*, *Enterococcus*, fecal coliforms) consistently and significantly increased** after H2O2. Heterotrophic bacteria declined in all experiments.
- **Results:** cyanobacteria fell in 6 of 9 experiments. Whole-pond doses never pushed levels below bloom thresholds, and **populations rebounded in two weeks or less**. *Microcystis* stayed dominant.
- **Effective?** No for this ecosystem: the effect is short and swaps one pollution problem for another.
- **Teen-reproducible?** Partly. Coliform counts are feasible with Petrifilm or Coliscan plates, though that means culturing bacteria from pond water (Form 3 and BSL-1 or BSL-2 review).
- **Read:** abstract only.

### 7. Lake Anita Louise, Maryland, winter treatment (Mattheiss, Sellner & Ferrier, 2017) [agency or consultant report]
- **Link:** https://www.lakelinganore.org/wp-content/uploads/2017/01/Peroxide-Application-Summary-Report-Final.pdf
- **What they did:** a Hood College report for a homeowners association. The lake had a *P. rubescens* bloom with microcystin above 300 ppb in winter 2016. On 2016-12-04 they spread 350 lb of GreenCleanPro granules from a small boat. H2O2 was measured with a **Hach HYP-1 titration kit** and pigments with a **Turner Aquafluor**.
- **Environment:** H2O2 peaked at 3 mg/L and returned to background shortly after. Non-cyanobacteria, especially *Synura*, rose 2-3x. Crustacean zooplankton were "abundant and actively swimming" (observed, not counted).
- **Results:** filaments fell 4-5x, from 1,780 to about 360-385 per mL, 3-8 days after treatment. Secchi depth went from 0.73 m to 0.92-1.2 m. Microcystin stayed low at 0.4-1.5 ppb throughout. The ITRC page (#28) says densities "remain low 4 years after treatment". The report itself covers only 8 days and warns that the seed population remains.
- **Effective?** Partly, for the short term.
- **Teen-reproducible?** Partly. Its monitoring kit (a titration kit and a handheld fluorometer) is exactly what a student could use.
- **Read:** full text.

### 8. Lake Okeechobee marina field demonstration (Sperry et al., 2023, US Army ERDC) [agency report]
- **Link:** https://doi.org/10.21079/11681/47624 · https://erdc-library.erdc.dren.mil/jspui/bitstream/11681/47624/1/ERDC-EL%20TR-23-7.pdf
- **What they did:** a peroxide algaecide (sodium carbonate peroxyhydrate) in Pahokee Marina in 2020, with *Microcystis* as the target.
- **Environment:** H2O2 averaged 6.1 mg/L at 0.5 h and was below detection by 24 h.
- **Results:** chlorophyll fell 87% and phycocyanin 85%. Microcystin went from 50 to 4 µg/L at 4 h, then back up to 11 µg/L by 24 h. **Wind-driven inflow of untreated bloom water defeated control at some sites.**
- **Effective?** Partly. It works in enclosed water but fails where water exchanges.
- **Teen-reproducible?** No.
- **Read:** abstract only.

### 9. Same marina: microbial community response to granular PAK 27 (Lefler et al., 2024) [peer-reviewed]
- **Link:** https://doi.org/10.3390/toxins16050206 (PMC11125911)
- **What they did:** a granular peroxide algaecide (PAK 27) on a *Microcystis* bloom in Pahokee Marina, sampled 48 h after treatment.
- **Environment:** a significant shift in bacterial community structure, and more photosynthetic protists.
- **Results:** at 48 h, chlorophyll a fell 96.8%, phycocyanin 93.2%, *Microcystis* cells 99.9% and microcystins 86.7%.
- **Effective?** Yes, in the short term.
- **Teen-reproducible?** No (a field algaecide application needs a licence).
- **Read:** abstract only.

### 10. Caloosahatchee River, Florida: spray, a high-dose mesocosm, and Lake Guard Oxy (Hancock et al., 2024a, 2024b, 2025) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.envpol.2024.123508 · https://doi.org/10.1016/j.hal.2024.102587 · https://doi.org/10.1128/aem.01950-25 (PMC12724209)
- **What they did:**
  - (a) Sprayed a minor *Microcystis* bloom below Franklin Lock at 16.7 mg/L.
  - (b) Sprayed 250 L mesocosms at a very high 473 mg/L.
  - (c) Applied 65 kg of floating sodium-percarbonate granules (Lake Guard Oxy) over about 0.5 acre, plus a liquid application, in a tidally influenced river.
- **Environment:**
  - (a) Non-toxic *Synechococcus* took over, rising to 57% of the community by day 14.
  - (b) Bacteria fell 92% and then regrew; the survivors still degraded microcystin, which fell 70%.
  - (c) No visible wildlife deaths among alligators, manatees, fish and birds, though zooplankton were "likely" harmed. Granules gave a 37 mg/L peak at 15 min, and liquid 74 mg/L; both were back to background the next day.
- **Results:** in (c), chlorophyll fell 81-90% and *Microcystis* colonies 91-97% in the short term. **Three treatments in 2 weeks did not end the bloom.** Chlorophyll was still 447 µg/L at day 14 because the river keeps exchanging water.
- **Effective?** Partly. The knockdown is real, but it fails in flowing water, which is the situation in Long Island Sound.
- **Teen-reproducible?** No for the field work.
- **Read:** full text of 2025 (PMC summary); abstract only for 2024a and 2024b.

### 11. Oder River *Prymnesium parvum* (Jasser et al., 2025; Weber et al., 2026; Wagstaff et al., 2021) [peer-reviewed]
- **Link:** https://doi.org/10.3390/w18010052 (open access) · https://doi.org/10.1016/j.ecohyd.2026.100771 · https://doi.org/10.1021/acs.est.1c04742
- **What they did:** *P. parvum* is the brackish haptophyte behind the 2022 Oder fish kill.
  - Jasser: canal-water experiments; a single dose from 14 mg/L upward.
  - Weber: a field application to stop the spread from a canal.
  - Wagstaff: a Norfolk Broads (UK) field trial of "low doses".
- **Environment:** Jasser saw limited harm to other phytoplankton. Re-inoculation produced *higher* *P. parvum* biomass and more prymnesin toxin, possibly from nutrients released by the dead cells. Weber reports "acceptable effects on non-target organisms".
- **Results:** 14 mg/L cut biomass and prymnesins (Jasser). 10-15 mg/L eliminated 90-99% of cells (Weber).
- **Effective?** Yes, for containment in canals. There is a rebound risk.
- **Teen-reproducible?** No (toxic organism). A non-toxic haptophyte (*Isochrysis*) would be a safe stand-in.
- **Read:** abstract only (Jasser, Wagstaff); highlights only (Weber).

### 12. Lake Guard Oxy at Lake Mattamuskeet, North Carolina (US Fish & Wildlife Service EA, 2024; court block, 2025) [agency report / press]
- **Link:** https://www.fws.gov/sites/default/files/documents/2024-03/ea-update-factsheet-final.pdf · https://coastalreview.org/2025/07/judge-blocks-pilot-lake-mattamuskeet-algaecide-application/
- **What they did:** the plan was a pilot of 400 acres (1% of the lake) behind turbidity curtains, at **no more than 50 lb/acre**. That cap came from bird and aquatic-invertebrate toxicity tests. The plan also included pH and dissolved-oxygen shutdown thresholds and hazing birds away from the treatment areas.
- **Environment:** the public objected because of migratory birds. A federal judge blocked the pilot in July 2025 (press coverage).
- **Results:** none; the treatment never happened.
- **Effective?** Unknown.
- **Teen-reproducible?** No. It is a useful example of how regulators frame the risks.
- **Read:** full text of the fact sheet; the court outcome from press only.

### 13. Hyper-eutrophic aquaculture pond in Alabama (Yang et al., 2018) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.envpol.2018.05.012
- **What they did:** a 5-day lab test on 4 cyanobacteria, then a 7-day in-pond experiment at several doses.
- **Environment:** 6.7 mg/L caused "relatively small" zooplankton losses. **20 mg/L gave the greatest zooplankton harm.** Phytoplankton diversity rose.
- **Results:** the lab EC50 was about 0.41 mg/L for *Anabaena*, *Cylindrospermopsis* and *Planktothrix*, and **5.06 mg/L for *Microcystis*** (about 10x higher). In the pond, 1.3 mg/L or more eliminated *Planktothrix* and 6.7 mg/L or more eliminated *Microcystis*.
- **Effective?** Yes, when dosed to the species present.
- **Teen-reproducible?** **Yes** for the lab part (it gives species-specific dose targets).
- **Read:** abstract only.

---

## B. Mesocosm and enclosure studies (effects on non-targets and regrowth)

### 14. Species sensitivity distribution and two lake treatments (Weenink et al., 2022) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.watres.2022.119169 (open access)
- **What they did:** 24-h toxicity tests on 3 cyanobacteria and 23 non-target species (6 green algae, 8 zooplankton, 9 macroinvertebrates). They built a species sensitivity distribution and checked it against two whole-lake treatments.
- **Environment:** the most sensitive species were all three cyanobacteria **plus the rotifer *Brachionus calyciflorus* and the cladocerans *Ceriodaphnia dubia* and *Daphnia pulex***. The low-dose, short-residence lake treatment had no major non-target effects. The higher-dose, longer-residence treatment only partly suppressed cyanobacteria and **collapsed the rotifers**.
- **Results:** the lab predictions matched the lake responses well.
- **Effective?** Yes, but only inside a narrow dose window.
- **Teen-reproducible?** **Yes** for part of it: *Daphnia* and *Brachionus* are sold for aquariums, so a 24-h survival test next to the algae test is feasible.
- **Read:** abstract only.

### 15. Acute toxicity to *Daphnia* and *Moina* (Reichwaldt et al., 2011); sodium percarbonate and *Daphnia* (Thoo et al., 2020) [peer-reviewed]
- **Link:** https://doi.org/10.1061/(ASCE)EE.1943-7870.0000508 · https://doi.org/10.3390/w12051304 (open access)
- **What they did:** acute H2O2 exposures of two cladocerans (Reichwaldt), and sodium percarbonate added to a natural plankton sample (Thoo).
- **Environment:** LC50 was **5.6 mg/L for *Daphnia carinata*** and **2 mg/L for *Moina***. The no-effect levels (NOAEC) were 3 and 1.5 mg/L. Larger *Daphnia* died more often under sodium percarbonate. Thoo suggests a safe level of **below 10 mg/L sodium percarbonate (2.8 mg/L H2O2)**.
- **Results:** effective cyanobacteria doses in stabilization ponds overlap these toxic levels.
- **Effective?** Not applicable (these are safety data).
- **Teen-reproducible?** **Yes.** A *Daphnia* survival test is a classic safe school bioassay.
- **Read:** abstract only.

### 16. Planktothrix reservoir mesocosms, semi-arid Brazil (Santos et al., 2021) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.watres.2021.117069 (open access)
- **What they did:** a single 10 mg/L dose, followed for 120 h in in-reservoir mesocosms.
- **Environment:** at this dose, **green algae and diatoms were also suppressed for 72 h**. Transparency and dissolved organic carbon rose, dissolved oxygen and pH fell, and nutrients were unchanged. The bacteria shifted to *Exiguobacterium*, *Paracoccus* and *Deinococcus*.
- **Results:** cyanobacteria stayed low at 120 h and greens became dominant. *Cyanobium* was starting to regrow.
- **Effective?** Yes, in the short term, but it was not selective at 10 mg/L.
- **Teen-reproducible?** Partly.
- **Read:** abstract only.

### 17. Okeechobee mesocosms: single versus sequential dosing (Pokrzywinski et al., 2022) [peer-reviewed]
- **Link:** https://doi.org/10.3390/w14020169 (open access)
- **What they did:** 72 h of enclosed mesocosms at the maximum label rate of 10 mg/L (sodium carbonate peroxyhydrate), with and without a second 5 mg/L dose at 48 h.
- **Environment:** peroxide was undetectable by 48 h. Community structure did not change; the community stayed more than 90% cyanobacteria.
- **Results:** biomass fell more than 71% at 24 h, but only 32-45% by 48 h after a single dose. **The repeat dose sustained a 60-91% decrease.**
- **Effective?** Partly. A single dose rebounds within 2 days.
- **Teen-reproducible?** Partly (the repeat-dose design is easy in jars).
- **Read:** abstract only.

### 18. Bloom density sets the dose (Chen et al., 2020; Buley et al., 2023) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.envpol.2020.115923 · https://doi.org/10.1007/s11356-023-25301-4
- **What they did:**
  - Chen: Lake Chaohu mesocosms at high chlorophyll (220-250 µg/L) and low chlorophyll (30-50 µg/L), dosed at 5, 10 and 20 mg/L for 7 days.
  - Buley: lab tests at 2-16 mg/L across humic acid (0-60 mg/L), temperature (20-32 °C) and chlorophyll (82-371 µg/L).
- **Environment:** in dense blooms, 10 mg/L caused a **"dramatic increase" in nutrients and microcystins** in the water. The cyanobacteria also shifted from non-toxic *Dactylococcopsis* to toxic *Oscillatoria*.
- **Results:**
  - Chen: 5 mg/L was enough at low density, but 20 mg/L was needed at high density.
  - Buley: the effective dose was **0.03-0.12 mg H2O2 per µg/L of chlorophyll**. Humic matter and temperature mattered little.
- **Effective?** Yes, if applied early.
- **Teen-reproducible?** **Yes.** "Dose per unit chlorophyll" is a clean variable for a science-fair project.
- **Read:** abstract only.

### 19. Algal harvesting versus H2O2 in Taihu-region mesocosms (Fan et al., 2019) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.scitotenv.2019.133721
- **What they did:** 15-day in-lake mesocosms comparing removal with a 30-µm net (30/60/90% intensity) against 10 mg/L H2O2.
- **Environment:** H2O2 shifted the community to green-algae dominance after day 9. Partial harvesting *promoted* cyanobacterial regrowth.
- **Results:** H2O2 selectively suppressed cyanobacteria for all 15 days. Only 90% harvesting matched it.
- **Effective?** Yes. It worked better than physical harvesting as a one-time measure.
- **Teen-reproducible?** **Yes.** Comparing "net removal" with "peroxide" in buckets is a strong design, since physical removal also answers the retrieval objection.
- **Read:** abstract only.

### 20. Microbial resilience after lake treatments at 2.5 mg/L (Piel et al., 2021) [peer-reviewed]
- **Link:** https://doi.org/10.3390/microorganisms9071495 (open access)
- **What they did:** two lake treatments targeting 2.5 mg/L, plus controlled incubations. They tracked 16S bacterial communities.
- **Environment:** oxidative-stress-tolerant *Rheinheimera* spiked in the first 24 h and then declined. Verrucomicrobia fell. **Bacterial diversity dipped and recovered within a few days.** Predicted community function stayed stable.
- **Results:** *Aphanizomenon* and *Dolichospermum* were suppressed well, *P. agardhii* less so.
- **Effective?** Yes. The authors call it a "short-term pulse disturbance".
- **Teen-reproducible?** No (needs DNA sequencing).
- **Read:** abstract only.

### 21. Bacterial communities during *P. agardhii* suppression, Türkiye (Ozbayram et al., 2025) [peer-reviewed]
- **Link:** https://doi.org/10.1007/s00267-025-02248-5
- **What they did:** 2 mg/L on a *P. agardhii* bloom sample.
- **Environment:** no notable harm to non-target phytoplankton. H2O2 had largely degraded within 4 h and was undetectable at 24 h. *Rheinheimera* rose to 40% on day 3 and fell to about 1% later.
- **Results:** chlorophyll a fell about 55% in 1 h and about 90% in 2 h.
- **Effective?** Yes, for sensitive filamentous species.
- **Teen-reproducible?** Partly (the chlorophyll part is doable).
- **Read:** abstract only.

### 22. Low-dose peroxide as prevention, applied early (Jiang et al., 2022) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.ecoenv.2022.113546 (open access)
- **What they did:** 0.2-1.5 mg/L added to a microcosm at the early cyanobacterial growth stage, followed for 15 days.
- **Environment:** 0.2 mg/L caused **hormesis** (it stimulated the cyanobacteria). At 1.0-1.5 mg/L the eukaryotic community stayed similar to the controls.
- **Results:** 0.5-1.5 mg/L inhibited growth and microcystin production. 1.0-1.5 mg/L prevented the bloom from forming.
- **Effective?** Yes, as prevention. This links to the project's bloom *predictor*: forecast first, then dose low and early.
- **Teen-reproducible?** **Yes.** The hormesis at 0.2 mg/L is a nice extra finding to test.
- **Read:** abstract only.

### 23. Overwintering benthic cyanobacteria (Chen et al., 2016) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.envpol.2016.06.043
- **What they did:** 0, 1, 5 and 20 mg/L on sediment-surface cyanobacteria under simulated winter conditions, followed by a recovery test.
- **Environment:** not assessed.
- **Results:** the damage at 1 mg/L was temporary. **At 5 and 20 mg/L it was permanent.**
- **Effective?** Yes in the lab. It suggests pre-season treatment of the "seed bank".
- **Teen-reproducible?** Partly.
- **Read:** abstract only.

### 24. H2O2 plus 85% shading, Lake Dianchi enclosures (Zhou et al., 2018) [peer-reviewed]
- **Link:** https://doi.org/10.1007/s11356-017-0659-x
- **What they did:** field enclosures in Lake Dianchi, China, comparing dose, light, repeat dosing, and shading after treatment.
- **Environment:** H2O2 alone let the biomass rebound through eukaryotic algae. A second dose at the same level did little.
- **Results:** H2O2 worked better and degraded faster in full light. **H2O2 followed by 85% shading kept biomass low for nearly a month.**
- **Effective?** Yes, when combined with shading.
- **Teen-reproducible?** **Yes.** Shade cloth over jars is a cheap second factor.
- **Read:** abstract only.

### 25. Sodium percarbonate in drinking-water reservoirs (Xu et al., 2021) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.watres.2021.117111
- **What they did:** solid Na2CO3·1.5H2O2 at 3 and 6 mg/L, on surface and bottom water with filamentous cyanobacteria.
- **Environment:** 3 mg/L had only a slight effect on microeukaryotes (18S sequencing). **6 mg/L clearly changed the eukaryotic phytoplankton and zooplankton.** The carbonate released by percarbonate generates radicals even in dim bottom water.
- **Results:** 3 mg/L suppressed cyanobacteria in bottom water by 36 h. Sensitivity ran *Pseudanabaena* > *Raphidiopsis* > *Cylindrospermopsis*.
- **Effective?** Yes.
- **Teen-reproducible?** **Yes.** Sodium percarbonate is sold as pure "oxygen bleach" powder.
- **Read:** abstract only.

### 26. Sodium percarbonate in a small firewater reservoir, Hungary (Bácsi et al., 2026) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.hal.2026.103181
- **What they did:** a low-concentration percarbonate treatment of a severe bloom in a whole small reservoir, with extensive monitoring.
- **Environment:** conductivity rose and nitrogen forms shifted. Eukaryotic algae were not reduced; green algae temporarily increased.
- **Results:** cyanobacteria declined, then **returned to pre-treatment levels within a week**. Cyanopeptide production was unaffected. The authors conclude the method is "best suited for bloom prevention".
- **Effective?** Partly.
- **Teen-reproducible?** Partly.
- **Read:** abstract only.

### 27. Nanobubble ozone versus algaecides: efficacy and zooplankton (Chaffin et al., 2024; Stanislawczyk et al., 2026) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.jenvman.2024.123406 · https://doi.org/10.1080/10402381.2026.2669770 (open access)
- **What they did:**
  - Chaffin: 2,000 L mesocosms plus two 4-week trials in an embayment of about 47 million L at Grand Lake St Marys, Ohio.
  - Stanislawczyk: Lake Erie zooplankton mesocosms given ozone at 0.9 and 4.6 mg/L, versus copper at 1 mg/L and H2O2 at 10 mg/L.
- **Environment:** **both algaecides harmed zooplankton significantly more than ozone nanobubbles.** *Bosmina*, *Daphnia*, Sididae and Chydoridae declined under the H2O2 and copper treatments.
- **Results:** in mesocosms, medium and high ozone doses cut chlorophyll and phycocyanin 98-99% and microcystin 62-92%. **The field trial had no effect**, because too little of the lake was treated and dissolved organic carbon was high. There was no effect 3 m from the outlet.
- **Effective?** Partly: in tanks, yes; in the lake, no.
- **Teen-reproducible?** No. Ozone generators are an inhalation hazard.
- **Read:** abstract only.

---

## C. Lab studies (mechanism, selectivity, protocols)

### 28. ITRC HCB-1 fact sheet: "Peroxide Application" (ITRC, 2021) [agency report]
- **Link:** https://hcb-1.itrcweb.org/peroxide-application/
- **What they did:** a multi-state guidance summary of field evidence.
- **Environment:** "At H2O2 >5 mg/L, may impact zooplankton and fish." Treatment can release cyanotoxins, but peroxide oxidizes them. It is NSF-60 certified for drinking-water sources. It needs applicator training and permits in many states.
- **Results:** effective doses are about 2.3 mg/L for *P. agardhii*, 3-4 mg/L for *Aphanizomenon* and *Dolichospermum*, and more than 5 mg/L for *Microcystis*. The recommended aim is under 5 mg/L in the water. Cost is rated "$$".
- **Effective?** Yes, for non-flowing waters.
- **Teen-reproducible?** Not applicable. It is the best single source for dose targets.
- **Read:** full text.

### 29. H2O2 plus light is selective (Drábková et al., 2007) [peer-reviewed]
- **Link:** https://doi.org/10.1021/es060746i
- **What they did:** pulse doses on *Microcystis*, the green alga *Pseudokirchneriella* and the diatom *Navicula*, in the dark and at several light levels, measured with PAM fluorometry.
- **Environment:** the green alga and the diatom needed **10x more** H2O2 to be affected.
- **Results:** the EC50 for *Microcystis* was 0.27 mg/L in high light, close to the highest natural level of 0.34 mg/L. Decay was faster at higher light.
- **Effective?** Yes (it is the basis of selectivity).
- **Teen-reproducible?** **Yes.** It is a three-species, three-light-level design.
- **Read:** abstract only.

### 30. More effective at high light (Piel et al., 2020) [peer-reviewed]
- **Link:** https://doi.org/10.3390/toxins12010018 (open access)
- **What they did:** *Microcystis* PCC 7806 at 0-10 mg/L under different light intensities and colours.
- **Environment:** the authors recommend sunny-day treatments, so that lower doses spare non-targets. Treatment increased extracellular microcystin because cells leaked.
- **Results:** 1-2 mg/L was "highly effective" in high light. Photosynthetic yield fell more under orange light than blue.
- **Effective?** Yes.
- **Teen-reproducible?** **Yes.** LED colour and intensity are easy variables to change.
- **Read:** abstract only.

### 31. Green algae protect cyanobacteria (Weenink et al., 2021) [peer-reviewed]
- **Link:** https://doi.org/10.1111/1462-2920.15429 (open access)
- **What they did:** *Microcystis* alone and mixed with *Chlorella*, plus two lake treatments.
- **Environment:** green algae degrade H2O2 much faster than cyanobacteria. **Even lysed *Chlorella* protected *Microcystis*.**
- **Results:** protection increased with *Chlorella* density, which can defeat lake treatments.
- **Effective?** Not applicable (a limit on the method).
- **Teen-reproducible?** **Yes.** This is an elegant two-species experiment using safe organisms.
- **Read:** abstract only.

### 32. Lake-sample community succession and re-inoculation (Weenink et al., 2015) [peer-reviewed]
- **Link:** https://doi.org/10.3389/fmicb.2015.00714 (Frontiers, open access)
- **What they did:** 200 mL lake samples in 500 mL bottles on a lab windowsill at 20 °C, dosed at 0, 2.5, 5, 10, 20 and 50 mg/L. They measured with a PHYTO-PAM and H2O2 with a p-nitrophenylboronic acid assay at 405 nm, and followed the samples for 49 days.
- **Environment:** diversity rose after treatment. Green algae went from 0.03-0.12 to 0.89-2.00 million cells/mL at 2.5 mg/L.
- **Results:** at 2.5 mg/L, two replicates were **free of cyanobacteria by day 25**. Re-inoculated cyanobacteria "disappeared rapidly", with **no return even after 6 weeks**. In dense samples, H2O2 was gone within 4 h.
- **Effective?** Yes, in bottles.
- **Teen-reproducible?** **Yes.** It is the most directly copyable protocol: windowsill bottles and pond water. A plate reader can be replaced with peroxide test strips.
- **Read:** full text (methods and results).

### 33. Secondary outbreak after H2O2 (Luo et al., 2024) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.jhazmat.2024.134196
- **What they did:** *Microcystis* treated at 5 and 20 mg/L and followed through recovery.
- **Environment:** not assessed.
- **Results:** cells went **dormant for 20 days (5 mg/L) and 28 days (20 mg/L)**, but photosynthetic activity recovered within 14 days, followed by re-division.
- **Effective?** Partly. "Dead-looking" cultures regrow.
- **Teen-reproducible?** **Yes.** A 4-week regrowth follow-up is easy and often skipped.
- **Read:** abstract only.

### 34. Calcium peroxide granules in fabric bags (Keliri et al., 2022); CaO2 and MgO2 granules in a Cypriot lake (Keliri et al., 2021) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.ceja.2022.100318 (open access) · https://doi.org/10.1186/s12302-021-00471-5 (open access)
- **What they did:**
  - 2022: 0.5-2.0 g/L CaO2 granules enclosed in four types of fabric; they measured H2O2 release and ran bench tests on *Microcystis*.
  - 2021: a dense *Merismopedia* bloom in St. George Lake, Cyprus, treated with liquid H2O2 or with granules.
- **Environment:** the fabric keeps the granules out of the waterbody, which the authors argue avoids exposing non-targets. Recycled fabric was used.
- **Results:**
  - 2 g/L released up to **12 mg/L H2O2 at 24 h**, the same as loose granules for three of the fabric types, and cut *Microcystis* fluorescence from 8,000 to under 1,000 RFU.
  - In Cyprus, **liquid H2O2 at 1-5 mg/L had no effect** on a bloom of about 1 million cells/mL. CaO2 released more H2O2 than MgO2.
- **Effective?** Yes in the lab.
- **Teen-reproducible?** **Yes, strongly.** A retrievable "peroxide tea bag" answers the counselor's retrieval concern. Use sodium percarbonate or CaO2 (garden or pond grade), gloves and goggles.
- **Read:** abstract only.

### 35. Calcium peroxide: threshold, mechanism, and safety to a submerged plant (Gu et al., 2023, 2025) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.scitotenv.2023.163591 · https://doi.org/10.1016/j.scitotenv.2024.178290
- **What they did:** 100 mg/L CaO2 for 96 h (2023). Alginate-encapsulated CaO2 beads at 100 mg/L, with the eelgrass *Vallisneria natans* (2025).
- **Environment:** the beads *relieved* the bloom-induced stress on the plant and its leaf biofilm. CaO2 also clumps cells, with calcium and cell-surface polymers forming aggregates that sink.
- **Results:**
  - 2023: only a 31.4% chlorophyll reduction, and Fv/Fm down to 50%. The *mcy* toxin genes were up-regulated.
  - 2025: beads inhibited cyanobacterial biomass by 93.5%.
- **Effective?** Partly. CaO2 is slow and needs about 100 mg/L.
- **Teen-reproducible?** Partly (alginate beads are a classic school technique).
- **Read:** abstract only.

### 36. Comparison of new solid and liquid peroxide products (Lürling et al., 2025) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.hal.2025.102930
- **What they did:** Oximycin P5, Phycomycin SCP, Lake Guard Oxy, liquid H2O2 and CaO2 on *Microcystis* at 150 and 600 µg/L chlorophyll.
- **Environment:** extracellular microcystin rose at day 1 in all treatments, then fell below the control by day 9.
- **Results:** at 600 µg/L and 3 mg/L, all except Lake Guard Oxy and CaO2 took chlorophyll to zero; those two let it rise again. At 10 mg/L all worked, with no recovery. There was "no obvious top choice".
- **Effective?** Yes.
- **Teen-reproducible?** Partly. Liquid H2O2 against sodium percarbonate is the affordable pair.
- **Read:** abstract only.

### 37. Five oxidants in one experiment (Fan et al., 2013) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.watres.2013.05.057
- **What they did:** CuSO4, chlorine, KMnO4, H2O2 and ozone on *Microcystis* cell integrity, over 7 days.
- **Environment:** fast lysers release toxins all at once. Chlorine compromised 88% or more of cells within 1 minute. Ozone at 6 mg/L lysed 90% in 5 minutes. KMnO4 at 10 mg/L lysed at a rate of 0.83 per hour.
- **Results:** only CuSO4 and H2O2 were also "algistatic", suppressing growth over 7 days.
- **Effective?** Yes (the value is in the comparison).
- **Teen-reproducible?** Partly. Chlorine, ozone and permanganate are harder to handle safely than H2O2.
- **Read:** abstract only.

### 38. Selectivity challenged: mixotrophs and diatoms (Mehdizadeh Allaf et al., 2023) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.watres.2023.119811 (open access)
- **What they did:** CuSO4 and H2O2 on four phytoplankton groups.
- **Environment:** sensitivity ran **mixotrophs > cyanobacteria > diatoms > chlorophytes**. The authors say sparing all non-targets while suppressing cyanobacteria is "unattainable".
- **Results:** H2O2 is a comparable alternative to copper, but not strictly selective.
- **Effective?** Not applicable (a caveat).
- **Teen-reproducible?** **Yes.** Adding a diatom and a mixotroph (*Euglena* or *Ochromonas*) to the jar test is easy.
- **Read:** abstract only.

---

## D. Marine and brackish lab work (most relevant to Long Island Sound)

### 39. H2O2 on marine dinoflagellates increases toxicity to fish gill cells (Mardones et al., 2023) [peer-reviewed]
- **Link:** https://doi.org/10.3390/microorganisms11010083 (PMC9864867)
- **What they did:** 50-1,000 ppm (mg/L) H2O2 at salinity 25-33 on toxic *Alexandrium catenella* and *Karenia selliformis* and on non-toxic *Lepidodinium* and *Prorocentrum micans*. Toxicity was measured on RTgill-W1 trout gill cells.
- **Environment:** H2O2 alone was cytotoxic to the gill cells. **Treating even non-toxic dinoflagellates *increased* gill-cell toxicity.** The proposed cause is toxic aldehydes from lipid peroxidation, which can persist for days.
- **Results:** 50 ppm killed all four species. The paper cites earlier work needing 30 mg/L for *Cochlodinium* in Japan.
- **Effective?** Yes at killing cells, but **"dead bloom does not mean safe water"**.
- **Teen-reproducible?** No for the gill-cell assay. A *Artemia* (brine shrimp) survival test is the teen analogue.
- **Read:** full text (summary of the results).

### 40. Peroxides versus chlorine on *Prymnesium* and *Heterosigma* (Moreno-Andrés et al., 2023) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.jhazmat.2023.131279
- **What they did:** 14-day dose-response curves in seawater for H2O2, peracetic acid, peroxymonosulfate, peroxydisulfate and chlorine. This was ballast-water work.
- **Environment:** not assessed.
- **Results:** peroxymonosulfate (EC50 0.40-1.99 mg/L) and peracetic acid (0.32-2.70 mg/L) acted strongly but briefly. **H2O2 (EC50 6.67-7.08 mg/L) gave a sustained effect.** Peroxydisulfate was negligible.
- **Effective?** Yes, but at marine doses about 3x the freshwater ones.
- **Teen-reproducible?** Partly. It needs a non-toxic raphidophyte stand-in, and peroxymonosulfate (pool "non-chlorine shock") is available.
- **Read:** abstract only.

### 41. Florida red tide and EPA-registered algaecides (Hu et al., 2022) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.hal.2022.102347 (open access)
- **What they did:** 3 copper and 3 peroxide algaecides on *Karenia brevis* at natural bloom density (1.79×10^7 cells/L).
- **Environment:** salinity, microbes and organic matter all sped up H2O2 breakdown in seawater. Oximycin P5 was the most stable, losing 0.467 mg/d. The authors say pilot studies on marine non-targets are still needed.
- **Results:** peroxides needed **4.89-7.08 mg/L** (copper only 0.31-0.34 mg Cu/L). Brevetoxin reduction increased with peroxide dose, via hydroxyl radicals.
- **Effective?** Yes in the lab.
- **Teen-reproducible?** No with *K. brevis*; partly with a non-toxic dinoflagellate.
- **Read:** abstract only.

### 42. Calcium peroxide inside a PAC floc against *K. brevis* (Hossain et al., 2024) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.hal.2024.102707 (open access)
- **What they did:** CaO2 built into a polyaluminum chloride floc, so that cells are killed inside the sinking floc. They measured with PAM fluorometry and viability assays.
- **Environment:** the authors argue that localized release lowers the overall dose. Aluminum floc still settles, which is the same objection as clay.
- **Results:** **30 mg/L CaO2** in the floc suppressed photosynthesis and killed cells within 3-6 h.
- **Effective?** Yes in the lab.
- **Teen-reproducible?** Partly. It adds the objectionable flocculant.
- **Read:** abstract only.

---

## E. UV and other oxidizers (secondary)

### 43. Permanganate compared with copper and with ozone (Fitzgerald, 1966; Xie et al., 2013) [peer-reviewed]
- **Link:** https://doi.org/10.1002/j.1551-8833.1966.tb01619.x · https://doi.org/10.1021/es4027024
- **What they did:**
  - Fitzgerald: KMnO4 against CuSO4 on 8 problem algae.
  - Xie: permanganate versus ozone as pre-oxidation of *Microcystis* water before chlorination.
- **Environment:** ozone at 0.4 mg/L left under 2% of cells intact and **sharply increased chlorinated disinfection by-products**. Permanganate mostly stripped surface organics without lysing cells. Permanganate leaves manganese and turns water pink or brown.
- **Results:** 1-5 ppm KMnO4 killed 7 of 8 species.
- **Effective?** Yes, but it is a treatment-plant tool, not an in-lake one.
- **Teen-reproducible?** Partly. KMnO4 is a strong oxidizer that stains; it is not recommended.
- **Read:** abstract only.

### 44. UV-C with H2O2, and UV with H2O2 on toxins (Zheng et al., 2023; Papadimitriou et al., 2016) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.jhazmat.2023.132826 · https://doi.org/10.1007/s11356-016-7418-2
- **What they did:**
  - Zheng: splits UV-C into two doses around an H2O2 addition, to drive oxidation inside the cells of *Microcystis*.
  - Papadimitriou: H2O2 with and without UV on microcosms from a hypertrophic Greek reservoir.
- **Environment:** UV works only in the water it passes through, so it leaves no residue but has no reach. That makes it a water-treatment or flow-through device.
- **Results:**
  - Zheng: intermittent UV-C plus H2O2 damaged photosynthetic electron transport and triggered apoptosis-like death.
  - Papadimitriou: UV plus H2O2 brought total microcystin **below the WHO 1 µg/L limit**. Cyanobacteria were affected preferentially over the other groups.
- **Effective?** Yes in the lab.
- **Teen-reproducible?** Partly. UV-C lamps burn eyes and skin, so it needs an enclosed box. A 365 nm UV-A LED is safer but weaker.
- **Read:** abstract only.

### 45. Microcystin release after algaecides, Okeechobee lab screen (Kinley-Baird et al., 2020) [peer-reviewed]
- **Link:** https://doi.org/10.1016/j.ecoenv.2020.111233 (open access)
- **What they did:** a lab screen of several EPA-registered algaecides on Lake Okeechobee water, including GreenClean Liquid 5.0 (peroxide) and five chelated-copper products. Measured 1, 4 and 9 days after treatment.
- **Environment:** chelated copper released *less* microcystin at day 1. By day 9, total microcystin in all effective treatments was below the controls.
- **Results:** the peroxide and copper products had similar effects on cyanobacteria.
- **Effective?** Yes.
- **Teen-reproducible?** No (toxin assays and copper).
- **Read:** abstract only.

---

## Notes on method and gaps
- The OpenAlex snowball used cites: and referenced_works for 12 seeds (#1, #2, #3, #4, #6, #14, #16, #17, #25, #29, #32, #35), keeping hits with peroxide or oxidant words in the title (347). Mid-run, the anonymous daily OpenAlex budget ran out (it is shared across agents on this IP), so the remaining abstracts came from PubMed E-utilities and Europe PMC.
- **Gap:** no field trial in open coastal marine water was found. Every marine or brackish success (#2, #11) was in an enclosed creek or canal. The Long Island work (#5, #6) is freshwater ponds.
- **Surprises:**
  - (a) Pond treatments *raised* fecal-indicator bacteria (#6), while one lab study saw coliforms fall.
  - (b) The ITRC claim of "low 4 years later" at Lake Anita Louise (#7) is not in the source report.
  - (c) Treating non-toxic marine dinoflagellates made the water more toxic to fish gill cells (#39).
  - (d) The largest US pilot (#12) was stopped in court.

## Every source URL consulted (included and excluded)
- https://doi.org/10.1016/j.watres.2011.11.016
- https://pubmed.ncbi.nlm.nih.gov/22112924/
- https://doi.org/10.1016/j.hal.2013.10.017
- https://research.wur.nl/en/publications/termination-of-a-toxic-alexandrium-bloom-with-hydrogen-peroxide
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0047844
- https://doi.org/10.1016/j.aquatox.2013.08.015
- https://doi.org/10.1016/j.hal.2024.102585
- https://doi.org/10.3390/toxins12070428
- https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7405413/fullTextXML
- https://pubmed.ncbi.nlm.nih.gov/32610617/ (blocked by cookie wall)
- https://www.mdpi.com/2072-6651/12/7/428 (403)
- https://doi.org/10.1016/j.jes.2021.11.031
- https://www.lakelinganore.org/wp-content/uploads/2017/01/Peroxide-Application-Summary-Report-Final.pdf
- https://doi.org/10.21079/11681/47624
- https://erdc-library.erdc.dren.mil/jspui/bitstream/11681/47624/1/ERDC-EL%20TR-23-7.pdf
- https://doi.org/10.3390/toxins16050206
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11125911/
- https://doi.org/10.1016/j.envpol.2024.123508
- https://doi.org/10.1016/j.hal.2024.102587
- https://doi.org/10.1128/aem.01950-25
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12724209/
- https://doi.org/10.3390/w18010052
- https://doi.org/10.1016/j.ecohyd.2026.100771
- https://doi.org/10.1021/acs.est.1c04742
- https://www.fws.gov/sites/default/files/documents/2024-03/ea-update-factsheet-final.pdf
- https://www.fws.gov/sites/default/files/documents/cyanobacteria-treatment-factsheet-final-508.pdf
- https://fws.gov/sites/default/files/documents/2024-03/202403-mattamuskeet-nwr-final-cyanobacteria-pilot-study-ea-signed.pdf
- https://www.fws.gov/story/2024-03/us-fish-and-wildlife-service-announces-decision-implement-cyanobacteria-pilot-study-4
- https://www.wunc.org/environment/2024-04-02/lake-mattamuskeet-chemical-treatment-worries-effects-birds-fish-wildlife-lake-guard-oxy-bluegreen-water-technologies
- https://coastalreview.org/2024/06/lake-mattamuskeet-algaecide-pilot-study-tied-up-in-court/
- https://coastalreview.org/2025/07/judge-blocks-pilot-lake-mattamuskeet-algaecide-application/
- https://doi.org/10.1016/j.envpol.2018.05.012
- https://doi.org/10.1016/j.watres.2022.119169
- https://doi.org/10.1061/(asce)ee.1943-7870.0000508
- https://doi.org/10.3390/w12051304
- https://doi.org/10.1016/j.watres.2021.117069
- https://doi.org/10.3390/w14020169
- https://doi.org/10.1016/j.envpol.2020.115923
- https://doi.org/10.1007/s11356-023-25301-4
- https://doi.org/10.1016/j.scitotenv.2019.133721
- https://doi.org/10.3390/microorganisms9071495
- https://doi.org/10.1007/s00267-025-02248-5
- https://doi.org/10.1016/j.ecoenv.2022.113546
- https://doi.org/10.1016/j.envpol.2016.06.043
- https://doi.org/10.1007/s11356-017-0659-x
- https://doi.org/10.1016/j.watres.2021.117111
- https://doi.org/10.1016/j.hal.2026.103181
- https://doi.org/10.1016/j.jenvman.2024.123406
- https://doi.org/10.1080/10402381.2026.2669770
- https://repository.library.noaa.gov/view/noaa/68341
- https://cfaes.osu.edu/news/ohio-state-research-shows-promise-new-harmful-algal-bloom-treatment
- https://hcb-1.itrcweb.org/peroxide-application/
- https://hcb-1.itrcweb.org/appendix-c/
- https://hcb-1.itrcweb.org/management-and-control-strategies-for-hcbs/
- https://hcb-2.itrcweb.org/introduction-to-treatment-strategies/
- https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/28/documents/habs/TreatmentOptimizationProtocol.pdf (listed, not read)
- https://doi.org/10.1021/es060746i
- https://doi.org/10.3390/toxins12010018
- https://doi.org/10.1111/1462-2920.15429
- https://doi.org/10.3389/fmicb.2015.00714
- https://www.frontiersin.org/articles/10.3389/fmicb.2015.00714/full
- https://doi.org/10.1016/j.jhazmat.2024.134196
- https://doi.org/10.1016/j.ceja.2022.100318
- https://doi.org/10.1186/s12302-021-00471-5
- https://doi.org/10.1016/j.scitotenv.2023.163591
- https://doi.org/10.1016/j.scitotenv.2024.178290
- https://doi.org/10.1016/j.hal.2025.102930
- https://www.sciencedirect.com/science/article/pii/S1568988325001325
- https://doi.org/10.1016/j.watres.2013.05.057
- https://doi.org/10.1016/j.watres.2023.119811
- https://doi.org/10.3390/microorganisms11010083
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9864867/
- https://doi.org/10.1016/j.jhazmat.2023.131279
- https://doi.org/10.1016/j.hal.2022.102347
- https://doi.org/10.1016/j.hal.2024.102707
- https://www.sciencedirect.com/science/article/pii/S1568988324001409
- https://doi.org/10.1002/j.1551-8833.1966.tb01619.x
- https://doi.org/10.1021/es4027024
- https://doi.org/10.1016/j.jhazmat.2023.132826
- https://doi.org/10.1007/s11356-016-7418-2
- https://doi.org/10.1016/j.ecoenv.2020.111233
- Excluded after reading abstract:
  - https://doi.org/10.3390/toxins6092657 (Bauzá 2014; coliforms fell in the lab, noted in the surprises)
  - https://doi.org/10.1016/j.aqrep.2025.103360 (diuron mesocosm; PAK 27 more selective than copper, and cyanobacteria returned in 2 weeks)
  - https://doi.org/10.1016/j.hal.2025.102984 (DinoSHIELD; a bacterial method, other family)
  - https://doi.org/10.4236/jwarp.2025.176021 (low-tier journal)
  - https://doi.org/10.1016/j.watres.2008.08.007, https://doi.org/10.1016/j.jes.2019.10.014, https://doi.org/10.3390/toxins15010011, https://doi.org/10.1016/j.hal.2016.04.012, https://doi.org/10.1016/j.hal.2025.102920, https://doi.org/10.1016/j.hal.2025.102967 (wrong-DOI lookups, off topic)
- Excluded by title only (abstract not retrieved):
  - https://doi.org/10.1007/s13762-024-06096-4
  - https://doi.org/10.1016/j.ecoleng.2012.04.024
  - https://doi.org/10.1016/j.seppur.2008.11.008
  - https://doi.org/10.1007/s40726-024-00328-4
  - https://doi.org/10.1016/j.jhazmat.2025.139679 and the other percarbonate groundwater and AOP papers in the OpenAlex hit list
- https://www.researchgate.net/publication/366641895 (search result only)
- https://academic.oup.com/plankt/article/40/6/667/5155317 (search result only)
- https://votewater.org/deep-dive-these-chemicals-kill-toxic-algae-but-are-they-safe/ (search result only)
- https://api.openalex.org/works (cites: and openalex_id: queries for the 12 seeds)
- https://eutils.ncbi.nlm.nih.gov/entrez/eutils/ (PubMed abstracts by DOI and title)
