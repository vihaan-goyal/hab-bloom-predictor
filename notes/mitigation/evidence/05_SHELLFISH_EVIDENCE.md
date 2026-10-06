# Evidence review: Method 5, deployable shellfish bags

Written 2026-09-25 for `notes/mitigation/05_SHELLFISH.md`, the method that plugs into the control
loop in `00_CONTROL_LOOP.md`. Sources were found through OpenAlex, Crossref, Europe PMC, publisher
pages and web search. Each source below has a retrieved record: title, authors and DOI were checked
against Crossref or OpenAlex.

**How to read the numbers.** "(abstract)" means the number comes only from the abstract.
"(full text)" means it was read in the paper or chapter. "(snippet)" means it came from a
search-engine summary of the abstract and still needs checking in the paper. Nothing here was
estimated from memory. Numbers that we calculated ourselves are marked **[our calc]**.

---

## 1. Summary and verdict

**Question:** can bags of hard clams (*Mercenaria mercenaria*), eastern oysters (*Crassostrea
virginica*) or mussels (*Mytilus edulis*), lowered into water when a bloom is forecast, remove bloom
algae fast enough to matter?

**What the evidence says**
- **Filtration does draw down phytoplankton when enough animals are present.** The best controlled
  test is Cerrato et al. 2004. In 300 L mesocosms, hard clams kept brown tide about 100× lower than in
  tanks without clams (no-clam tanks peaked above 600,000 cells/mL). Clams clearing about **40% of
  the tank volume per day** were enough to stop the bloom building up (abstract). Mesocosms with
  clams, oysters and mussels also had lower chlorophyll (Wall et al. 2008, abstract). The whole-bay
  Shinnecock result (Gobler et al. 2022) fits this pattern, but it is correlational.
- **At the scale of a nursery or reef, the effect is small or variable.** A commercial oyster nursery
  "did not have a large impact" on phytoplankton (Li et al. 2012). Chlorophyll removal over
  intertidal reefs ranged from −9.8% to 27.9% (Grizzle et al. 2008, snippet). A model found that 10×
  more oysters in Chesapeake Bay would lower summer surface chlorophyll by only about 1 mg/m³ (Cerco
  & Noel 2007, snippet).
- **Harmful algae can switch filtration off.** At dense blooms, feeding stops or shrinks. Hard clams
  cleared *Margalefidinium* at ≤1,000 cells/mL, but their clearance was not different from zero at
  ≥1,500 cells/mL (de Silva & Gobler 2023). Mussels fed less, and 30-100% died, in the 1985
  Narragansett Bay brown tide (Tracey 1988). Oyster feeding fell when *Cochlodinium* was present (Li
  et al. 2012). Responses depend on the species pair (Hégaret et al. 2007).
- **The animals become toxic.** They store saxitoxin, diarrhetic shellfish toxins and microcystin, at
  levels far above closure limits, within hours to days (Bricelj et al. 1990, 1991; McGuire et al.
  2024; Straquadine et al. 2022).

**Verdict for our project:** **plausible as a *slow, early-stage* treatment. It is not a rescue for a
dense bloom.** A bench clearance test is cheap, safe with non-toxic algae, and has a published
protocol (de Silva & Gobler 2023: one 10-20 mm clam in a 250 mL beaker for 1 h). The 7-day loop is
also testable. The literature predicts:
1. Removal will work best at low to moderate algal density.
2. Oysters will clear faster than clams, roughly 4-5× per gram in two independent sources.
3. The OFF decision will be driven more by animal health and ammonia than by chlorophyll.

We make no claim of bloom prevention or field readiness.

---

## 2. Master table

| # | Citation + link | Bivalve → algae | Setting | Dose / duration | Main result | Effective? |
|---|---|---|---|---|---|---|
| 1 | Gobler et al. 2022, *Front. Mar. Sci.* 9 [doi:10.3389/fmars.2022.911731](https://doi.org/10.3389/fmars.2022.911731) | Hard clam → brown tide (*Aureococcus*), total chl | Field, Shinnecock Bay NY | 3.2 M adults at ~27/m² in 64 plots, 2012-2019 | Bay filtration time fell from ≤3 months to 10 days; brown tide <10⁴ cells/mL in 2018-21 vs 0.3-1.9×10⁶ in 2007-16 (full text) | Yes (correlational) |
| 2 | Cerrato et al. 2004, *MEPS* 281:93 [doi:10.3354/meps281093](https://doi.org/10.3354/meps281093) | Hard clam → *Aureococcus* + natural phytoplankton | 300 L mesocosms, Peconic Bays water | 8-9 d; several clam densities | No-clam tanks >600,000 cells/mL; clam tanks 100× lower; clearing ~40% of volume/d was enough (abstract) | **Yes (controlled)** |
| 3 | Wall, Peterson & Gobler 2008, *MEPS* 357:165 [doi:10.3354/meps07289](https://doi.org/10.3354/meps07289) | Clam, oyster, mussel → natural phytoplankton | Mesocosms with eelgrass | "Environmentally realistic" densities | Chl a significantly lower with bivalves (p<0.05); eelgrass growth +48% at highest density (abstract) | Yes |
| 4 | Doering & Oviatt 1986, *MEPS* 31:265 [doi:10.3354/meps031265](https://doi.org/10.3354/meps031265) | Hard clam → natural seston | 13 m³ MERL mesocosms (Narragansett) | 16 clams/m² | Gross sedimentation +58% with clams; models using natural-seston rates fit, max-rate models overestimate (snippet + Cranford 2011) | Yes (particle removal) |
| 5 | Riisgård 1988, *MEPS* 45:217 [doi:10.3354/meps045217](https://doi.org/10.3354/meps045217) | 6 NE American bivalves incl. clam and oyster → algae/particles | Lab, 27-29 °C | Size series | Clam retains 100% of particles >4 µm; oyster 100% >5-6 µm, 50% at 2 µm; coefficient *a* in F=aW^b: clam 1.24 vs oyster ~6.x (abstract; digits partly unreadable) | n/a (rates) |
| 6 | Tenore & Dunstan 1973, *Mar. Biol.* 21:190 [doi:10.1007/BF00355249](https://doi.org/10.1007/BF00355249) | Mussel, oyster, clam → food suspensions | Lab flow-through | Food gradient | Feeding: clam < oyster < mussel at every food level; clam % removal *falls* at high food (snippet) | n/a (rates) |
| 7 | Cranford, Ward & Shumway 2011, in *Shellfish Aquaculture and the Environment* pp. 81-124 [doi:10.1002/9780470960967.ch4](https://doi.org/10.1002/9780470960967.ch4) | Meta-analysis, mussels, oysters, scallops, cockles | Review of >60 studies | n/a | Oyster median 3.00 L g⁻¹ h⁻¹ (as reported), 1.09 L ind⁻¹ h⁻¹ at 60 mm; most studies deplete <30% of particles (full text) | n/a (method) |
| 8 | Riisgård 2001, *MEPS* 211:275 [doi:10.3354/meps211275](https://doi.org/10.3354/meps211275) + Coughlan 1969, *Mar. Biol.* 2:356 [doi:10.1007/BF00355716](https://doi.org/10.1007/BF00355716) | Method papers | Review / method | n/a | Conflicting clearance data are partly from misused methods (abstract); the exponential clearance formula (via Cranford 2011, de Silva 2023) | n/a (method) |
| 9 | de Silva & Gobler 2023, *Front. Mar. Sci.* 10 [doi:10.3389/fmars.2023.1252540](https://doi.org/10.3389/fmars.2023.1252540) | Hard clam (10-20 mm) → *Margalefidinium*, *Rhodomonas*, *Gymnodinium aureolum* | Lab, 250 mL beakers, ~21 °C, S~32 | 1 clam/beaker, 1 h, n=10 + 3 controls | Cleared HAB at ≤1,000 cells/mL; ≈0 at ≥1,500; non-harmful dinoflagellate cleared as fast as *Rhodomonas* (full text) | Partly (density-limited) |
| 10 | Hégaret, Wikfors & Shumway 2007, *J. Shellfish Res.* 26:549 [doi:10.2983/0730-8000(2007)26[549:DFROFS]2.0.CO;2](https://doi.org/10.2983/0730-8000(2007)26[549:DFROFS]2.0.CO;2) | 5 bivalves incl. oyster, clam, mussel → *Prorocentrum*, *Alexandrium*, *Heterosigma* vs *Rhodomonas* | Lab | 1 h exposures | Species-specific; mostly *preferential retention* of HAB cells; oysters closed with *Heterosigma*; intact cells in biodeposits (abstract) | Mixed |
| 11 | McGuire et al. 2024, *Harmful Algae* 141:102745 [doi:10.1016/j.hal.2024.102745](https://doi.org/10.1016/j.hal.2024.102745) | Oyster, clam, mussel → *Dinophysis acuminata* | Field, 3 NY sites | Blooms 10²-10⁵ cells/L | CR oyster 1.69, mussel 0.46, clam 0.41 L h⁻¹ g⁻¹; mussel DST 265 ng/g > FDA 160 for 3 weeks (abstract) | Grazes, but toxic |
| 12 | Li et al. 2012, *J. Shellfish Res.* 31:1077 [doi:10.2983/035.031.0419](https://doi.org/10.2983/035.031.0419) | Oyster seed → natural phytoplankton, *Cochlodinium* | Field FLUPSY, Peconic NY | Jun-Sep 2010, 15-min data | Median 0.95 L h⁻¹ g⁻¹ (0.32-2.21 diel); no large phytoplankton impact; *Cochlodinium* → less feeding, more mortality (abstract) | No (at this scale) |
| 13 | Tracey 1988, *MEPS* 50:73 [doi:10.3354/meps050073](https://doi.org/10.3354/meps050073) | Mussel (+ hard clam) → brown tide | Field + lab, Narragansett Bay | 1985 bloom ~10⁶ cells/mL | Clearance normal below 2.5×10⁵ particles/mL, reduced above 5×10⁵; 30-100% mussel mortality (abstract) | Backfires at bloom density |
| 14 | Bricelj et al. 1990, *MEPS* 63:177 [doi:10.3354/meps063177](https://doi.org/10.3354/meps063177) | Mussel → *Alexandrium fundyense* vs *Thalassiosira weissflogii* | Lab | 256 cells/mL, 17 d | CR on *Alexandrium* ~48% lower than on the diatom; exceeded the 80 µg STXeq/100 g limit in <1 h; 79% of ingested toxin kept (abstract) | Grazes, toxic |
| 15 | Bricelj, Lee & Cembella 1991, *MEPS* 74:33 [doi:10.3354/meps074033](https://doi.org/10.3354/meps074033) | Hard clam → two *Alexandrium* isolates (+ *T. weissflogii*) | Lab | ~2 wk uptake | Clams ate the high-toxicity strain only with diatom added; tissues exceeded the closure level "by several orders of magnitude"; detox 3-6 wk (abstract) | Grazes selectively, toxic |
| 16 | Wikfors & Smolowitz 1995, *Biol. Bull.* 188:313 [doi:10.2307/1542308](https://doi.org/10.2307/1542308) | Oyster (4 life stages) → *Prorocentrum minimum* | Lab | Weeks | Juveniles filtered *P. minimum* but **rejected most as pseudofeces** for ~2 weeks before digesting it (abstract) | Removal without ingestion |
| 17 | Straquadine, Kudela & Gobler 2022, *Harmful Algae* 115:102236 [doi:10.1016/j.hal.2022.102236](https://doi.org/10.1016/j.hal.2022.102236) | Oyster, Asian clam → *Microcystis* | Lab + bloom water | 24-72 h, 3-4 d | >3 µg/g microcystin in 24-72 h on culture; oysters did not depurate (abstract) | Grazes, toxic |
| 18 | Grizzle, Greene & Coen 2008, *Estuar. Coasts* 31:1208 [doi:10.1007/s12237-008-9098-8](https://doi.org/10.1007/s12237-008-9098-8) | Oyster reefs → chl a | Field, 8 intertidal reefs SC | ≤1.3 h runs | Chl a removal −9.8% to 27.9% (snippet) | Variable |
| 19 | Cerco & Noel 2007, *Estuar. Coasts* 30:331 [doi:10.1007/BF02700175](https://doi.org/10.1007/BF02700175) | Oysters → Chesapeake phytoplankton | Eutrophication model | 10× oyster biomass | Summer surface chl −~1 mg/m³; deep DO +0.25 g/m³; a supplement to, not a substitute for, nutrient cuts (snippet) | Small |
| 20 | Kellogg et al. 2013, *MEPS* 480:1 [doi:10.3354/meps10331](https://doi.org/10.3354/meps10331) | Restored oyster reef | Field, Choptank MD | 131 oysters/m² | NH₄⁺, SRP and O₂ fluxes ≥10× higher than control; denitrification 0.3-1.6 mmol N m⁻² h⁻¹ (abstract) | Side effect evidence |
| 21 | Bricker et al. 2018, *Environ. Sci. Technol.* 52:173 [doi:10.1021/acs.est.7b03970](https://doi.org/10.1021/acs.est.7b03970) | CT oyster aquaculture → nutrients | Models, Long Island Sound | Current vs expanded | 1.31% / 2.68% of N inputs removed (abstract) | Small co-benefit |
| 22 | Officer, Smayda & Mann 1982, *MEPS* 9:203 [doi:10.3354/meps009203](https://doi.org/10.3354/meps009203) | Benthic filter feeders (theory) | Model, S. San Francisco Bay | n/a | Control works when water recycling time by the benthos ≈ phytoplankton growth time constant; favoured by shallow water (abstract) | Criterion |
| 23 | Meitei et al. 2025, *Discover Sustainability* 6 [doi:10.1007/s43621-025-01104-0](https://doi.org/10.1007/s43621-025-01104-0) | Blood clam, oyster, green mussel → *Thalassiosira* | 5 L microcosms | 1 animal per 2 L, 5 d | Plankton removal 94% / 87.1% / 77.0%; species not significantly different (abstract) | Yes (microcosm) |
| 24 | Shumway et al. 2003, *Aquac. Res.* 34:1391 [doi:10.1111/j.1365-2109.2003.00958.x](https://doi.org/10.1111/j.1365-2109.2003.00958.x) | Oysters, mussels, scallop → *Rhodomonas* + clay | Lab | 0.01-10 g/L loess | Oyster clearance unaffected until 1.0 g/L; scallop down at 0.01 g/L (abstract) | Cross-method warning |

Context only, not counted: Shumway 1990 review of algal blooms and shellfish
([doi:10.1111/j.1749-7345.1990.tb00529.x](https://doi.org/10.1111/j.1749-7345.1990.tb00529.x), abstract
has no numbers). Bricelj et al. 2005, *Nature* 434:763
([doi:10.1038/nature03415](https://doi.org/10.1038/nature03415)): in softshell clams, saxitoxin
resistance comes from a single sodium-channel mutation, and resistant clams accumulate *more* toxin.
Srna & Baggaley 1976, *Mar. Biol.* 36:251
([doi:10.1007/BF00389286](https://doi.org/10.1007/BF00389286)): ammonia excretion by hard clams and
oysters. Title only; the abstract was not retrievable, so no numbers are used.

---

## 3. Per-source detail

### 1. Gobler, Doall, Peterson, Young, DeLaney et al. 2022: Shinnecock spawner sanctuaries
- **Hypothesis:** rebuilding a collapsed hard-clam population with high-density no-harvest sanctuaries restores recruitment, filtration and water quality.
- **Method:** 3.2 M adults were planted at ~27/m² in 64 plots of ~1,850 m², 2012-2019, with surveys through 2021. Bay filtration time came from size-specific allometric clearance rates (Hibbert 1977 and Doering & Oviatt 1986 for >16 mm; Grizzle et al. 2001 for <16 mm) × surveyed densities ÷ basin volume (full text).
- **Results:** densities rose 18× (2015-21) and harvests 16×. Densities: western bay 1.2 → 1.9 clams/m², eastern bay 0.4 → 7.3. Filtration time fell to 10 days. Brown tide was 0.3-1.9×10⁶ cells/mL in 2007-16, ~1×10⁵ in 2017, and <10⁴ in 2018-21. Chl a fell significantly (Apr-Nov, western bay) (full text).
- **Mechanism:** more filtration pressure, plus tidal flushing "acts additively" in the eastern bay.
- **Caveats:** before/after comparison with no randomised control. Adjacent unrestored bays got worse while N loads rose, and the authors call clams "the most parsimonious explanation", not a proven cause.
- **Bench relevance:** it sets the idea but not the numbers. 27/m² is an area density; in a tank what matters is **volume cleared per day**, not animals per m².

### 2. Cerrato, Caron, Lonsdale, Rose & Schaffner 2004: clams vs brown tide in mesocosms
- **Hypothesis:** hard-clam grazing can stop a brown tide developing.
- **Method:** three experiments in 300 L mesocosms of natural Peconic water, nutrient-enriched and mixed, with and without clams, 8-9 days, at several clam densities.
- **Results (abstract):** without clams, *Aureococcus* passed 600,000 cells/mL on average and made up >50% of phytoplankton biomass. With many clams, cell counts were 2 orders of magnitude lower, with no rise in total biomass and no shift in species. A population clearance of **≈40% of volume per day** was enough under their conditions.
- **Mechanism:** grazing removes cells faster than they grow, and prevents a change in which species dominates.
- **Bench relevance:** **this is the closest analogue to our 7-day loop arm.** It gives a clear design target (volume cleared per day). Note that the clams were present from the start (prevention), not added after a trigger.

### 3. Wall, Peterson & Gobler 2008: bivalves, chlorophyll and eelgrass
- **Method:** mesocosms at "environmentally realistic" densities of *M. mercenaria*, *C. virginica* and *M. edulis*, with eelgrass. Densities, volume and temperature are in the paper and were not retrieved.
- **Results (abstract):** chl a was consistently lower with bivalves (p<0.05), light penetration was higher, and eelgrass leaf growth was +48 ± 9.3% at the highest bivalve density.
- **Bench relevance:** it supports a three-species comparison in tanks.

### 4. Doering & Oviatt 1986: clams in MERL mesocosms (Narragansett Bay)
- **Method:** 13 m³ mesocosms, 16 clams/m², ¹⁴C tracer; 8 filtration-rate models were tested.
- **Results (snippet):** gross sedimentation +58% with clams, split 32% clam assimilation, 47% benthic respiration, 21% permanent biodeposits. Models built on natural-seston rates matched. Cranford et al. 2011 add that **maximum lab rates overestimated sedimentation by up to 10×** (full text of Cranford).
- **Bench relevance:** do not plan with maximum lab rates. **Measure the rate on our own culture.**

### 5. Riisgård 1988: retention and filtration rate in 6 NE American bivalves
- **Method:** lab, 27-29 °C, clearance of particles of different sizes.
- **Results (abstract):** *Mercenaria* keeps 100% of particles >4 µm, falling to 35-70% at 2 µm. *Crassostrea* keeps 100% >5-6 µm and 50% at 2 µm. F = aW^b (L/h, W = g tissue dry weight): *a* = 1.24 for *M. mercenaria* and about 6.x for *C. virginica* (the abstract text in the retrieved record is garbled, so exponents and one digit could not be read). **Check in the PDF before using the equations.**
- **Bench relevance:** (i) check that our culture's cells are larger than ~5 µm, or retention will be incomplete. (ii) Per gram, the clam coefficient is several times lower than the oyster's.

### 6. Tenore & Dunstan 1973: feeding and biodeposition of mussel, oyster, clam
- **Results (snippet):** at every food level, feeding ranked clam < oyster < mussel. The % of food removed rose to a plateau at natural food levels. For the clam it then *declined* at higher food.
- **Bench relevance:** a very dense culture may be cleared proportionally *less* by clams. Test more than one starting density.

### 7. Cranford, Ward & Shumway 2011: meta-analysis of clearance rates and methods (full text read)
- **Numbers (Table 4.4):** medians of standardised clearance rate, in L g⁻¹ h⁻¹ as reported: mussel 2.32, scallop 2.63, **oyster 3.00**, cockle 3.37. Restandardised with b = 0.58: oyster 2.05, and the oyster mean on algal diets was 2.15 ± 0.49. Per animal at **60 mm with b = 1.8: oyster median 1.09 L ind⁻¹ h⁻¹**, mussel 3.26. Algal-cell diets gave ~1.7× higher rates than natural seston for mussels, scallops and cockles.
- **Method advice:** the static and "clearance" methods both use exponential decline (Coughlan 1969). Most published studies depleted <30% of particles. Flow-through chambers need <25-30% depletion. Interactions between animals (crowding, refiltration) bias population measurements. Viscosity makes pumping slower in cold water.
- **Bench relevance:** it gives our planning clearance rates and the size scaling (b = 1.8 on length).

### 8. Riisgård 2001 and Coughlan 1969: measurement method
- Riisgård (abstract): conflicting filtration data come partly from incorrect use of methods and partly from different experimental conditions. The debate (Cranford 2011; replies in *MEPS* 215, 221) is about whether maximum lab rates apply in nature.
- Coughlan 1969: the clearance formula used by de Silva & Gobler 2023. Record retrieved; formula as described by Cranford 2011: **CR = (V / (n·t)) · [ln(C₀/Cₜ) − ln(C₀′/Cₜ′)]**, where the primed values are from the no-animal control (corrects for algal growth and settling).

### 9. de Silva & Gobler 2023: hard clams vs *Margalefidinium* (full text methods)
- **Method:** 10-20 mm clams, fed mixed algae for ≥1 week and starved 24 h. **One clam on a mesh platform in each 250 mL beaker**, ~21 °C, salinity ~32. 10 beakers with clams + 3 algae-only controls per treatment. Samples taken when the clam opened and again after 1 h. Coughlan formula, normalised to dry weight. Densities: 250-1,000 cells/mL (single species); 1,500 and 3,000 (mixtures).
- **Results:** clearance of the bloom strains was ≈0 at ≥1,500 cells/mL. The non-harmful dinoflagellate *G. aureolum* was cleared as fast as *Rhodomonas*. There was no change in opening or closing behaviour.
- **Bench relevance:** **a ready-made, teen-reproducible 1-h protocol.** A non-toxic dinoflagellate is cleared normally, which supports using one in our bench.

### 10. Hégaret, Wikfors & Shumway 2007: five bivalves × three HABs
- **Results (abstract):** responses depended on the species pair. In most cases, cells of the harmful algae were retained *preferentially* over *Rhodomonas*. Oysters partly or fully closed with *Heterosigma*. Intact, possibly viable cells were seen in biodeposits of 4 of 5 species.
- **Bench relevance:** check whether cells in faeces and pseudofaeces are still viable. "Removed from the water" does not mean "killed".

### 11. McGuire, Sanderson, Smith & Gobler 2024: *Dinophysis* clearance and toxins
- **Results (abstract):** CR on *D. acuminata* was oyster 1.69 ± 1.34, mussel 0.46 ± 0.32, clam 0.41 ± 0.24 L h⁻¹ g⁻¹. Mussel DST reached 265 ng/g, above the FDA limit of 160, for three weeks.
- **Bench relevance:** oyster:clam ≈ 4:1 per gram **[our calc from abstract]**.

### 12. Li, Meseck, Dixon, Rivara & Wikfors 2012: oyster nursery (FLUPSY), Peconic NY
- **Results (abstract):** median 0.95 L h⁻¹ g⁻¹, with a diel cycle from 0.32 at dawn (low DO) to 2.21 near midnight. There was no large effect on local phytoplankton. *Cochlodinium* coincided with less feeding, no growth and more mortality.
- **Bench relevance:** low DO cuts feeding, so log DO next to the clearance data.

### 13. Tracey 1988: 1985 brown tide, Narragansett Bay
- **Results (abstract):** clearance of *Isochrysis* was normal below 2.5×10⁵ bloom particles/mL and reduced above 5.0×10⁵. Clams responded the same way as mussels. Mussel mortality was 30-100% along the bay, with complete reproductive failure.
- **Bench relevance:** there is a density ceiling above which the "treatment" shuts down and the animals are harmed.

### 14. Bricelj, Lee, Cembella & Anderson 1990: mussels on *Alexandrium*
- **Results (abstract):** maximum ingestion at 150-250 cells/mL. CR on *Alexandrium* was ~48% lower than on the diatom *Thalassiosira weissflogii*. There was no mortality over 17 days. Toxin saturated at 12-13 days, passed the 80 µg STXeq/100 g limit in <1 h at high density, and 79% of ingested toxin was retained.
- **Bench relevance:** *T. weissflogii* is a standard non-toxic control diet, which is a good candidate for our diatom arm.

### 15. Bricelj, Lee & Cembella 1991: hard clams on *Alexandrium*
- **Results (abstract):** clams readily ate the low-toxicity isolate. They ate the high-toxicity isolate only at a lower rate and only with diatom added, which suggests a toxin-recognition mechanism. Toxin peaked within 2 weeks at several orders of magnitude over the closure level, and depurated in 3-6 weeks.

### 16. Wikfors & Smolowitz 1995: oysters on *Prorocentrum minimum*
- **Results (abstract):** juvenile oysters filtered *P. minimum* but rejected most of it as pseudofaeces for ~2 weeks, then became able to digest it. Larvae grew poorly on it.
- **Bench relevance:** a dinoflagellate can vanish from the water without being eaten. **Count cells in pseudofaeces**, or the fate of the "removed" algae is unknown.

### 17. Straquadine, Kudela & Gobler 2022: microcystin in oysters and Asian clams
- **Results (abstract):** both species took up >3 µg/g within 24-72 h on single-cell cultures, but ≤2 ng/g on colonial bloom water. Oysters did not depurate over 3-4 days; clams cut their clearance and depurated.

### 18. Grizzle, Greene & Coen 2008: seston removal over oyster reefs
- **Results (snippet):** chl a removal ranged from −9.8% to 27.9% over 8 reefs, from in-situ fluorometry of water passing over each reef.
- **Bench relevance:** upstream/downstream fluorometry is the same measurement idea as our loop.

### 19. Cerco & Noel 2007: Chesapeake oyster restoration model
- **Results (snippet):** 10× oyster biomass → summer surface chl ~−1 mg/m³, deep DO +0.25 g/m³, SAV +20%. Oysters are "a supplement to nutrient load reduction, not a substitute".

### 20. Kellogg, Cornwell, Owens & Paynter 2013: restored reef nutrient fluxes
- **Results (abstract):** 131 oysters/m². Fluxes of O₂, NH₄⁺, NO₂+NO₃ and SRP were **≥10× the control in every season**. Denitrification was 0.3-1.6 mmol N₂-N m⁻² h⁻¹.
- **Bench relevance:** expect ammonium and phosphate to rise in a closed tank with dense animals. This is why the ammonia limit exists.

### 21. Bricker et al. 2018: Long Island Sound oyster nutrient removal
- 1.31% of N inputs removed now, 2.68% with expanded farming (abstract); 10-30% in an optimistic scenario. A co-benefit, not bloom control.

### 22. Officer, Smayda & Mann 1982: when benthic filter feeders control eutrophication
- **Criterion (abstract):** control happens when the benthic water-recycling time is about equal to the phytoplankton growth time constant. It is favoured by shallow water and dense communities of small animals.
- **Bench relevance:** it gives the formula behind our dose (Section 7).

### 23. Meitei et al. 2025: small-container bivalve filtration
- 5 L containers with *Thalassiosira*, 1 animal per 2 L, 5 days: removal 94% (clam), 87.1% (oyster), 77.0% (mussel), with no significant difference among species (abstract). Tropical species, so the numbers do not transfer directly; the protocol does.

### 24. Shumway, Frank, Ewart & Ward 2003: clay and bivalve clearance
- Oysters were unaffected until 1.0 g/L loess; mussels at 1-10 g/L; scallops at 0.01 g/L (abstract). This matters if methods are **combined** (for example the clay-retrieval device), and it shows the *Rhodomonas* depletion method in use.

---

## 4. Aggregated data

### 4a. Clearance rates (CR)

| Species | CR | Units / basis | Conditions | Source |
|---|---|---|---|---|
| Oyster | median 3.00 (2.05 at b=0.58) | L g⁻¹ h⁻¹ dry tissue | meta-analysis | Cranford 2011 (full text) |
| Oyster | median **1.09** | L ind⁻¹ h⁻¹ at 60 mm (b=1.8) | meta-analysis | Cranford 2011 (full text) |
| Oyster | 2.15 ± 0.49 | L g⁻¹ h⁻¹, algal diets (b=0.58) | meta-analysis | Cranford 2011 (full text) |
| Oyster seed | median 0.95 (0.32-2.21) | L g⁻¹ h⁻¹ | field nursery, summer | Li 2012 (abstract) |
| Oyster | 1.69 ± 1.34 | L g⁻¹ h⁻¹ on *Dinophysis* | field | McGuire 2024 (abstract) |
| Hard clam | 0.41 ± 0.24 | L g⁻¹ h⁻¹ on *Dinophysis* | field | McGuire 2024 (abstract) |
| Mussel | 0.46 ± 0.32 | L g⁻¹ h⁻¹ on *Dinophysis* | field | McGuire 2024 (abstract) |
| Mussel | median 3.26 | L ind⁻¹ h⁻¹ at 60 mm | meta-analysis | Cranford 2011 (full text) |
| Clam vs oyster | *a* = 1.24 vs ~6.x in F=aW^b | L h⁻¹, g dry wt | 27-29 °C lab | Riisgård 1988 (abstract, partly garbled) |
| Ranking | clam < oyster < mussel | % food removed | lab flow-through | Tenore & Dunstan 1973 (snippet) |

**Planning CR per animal [our calc]:** oyster CR(L) = 1.09 × (L/60)^1.8 gives **0.23 L/h at 25 mm,
0.53 at 40 mm and 1.09 at 60 mm**. For clams we assume **~0.25 × the oyster rate**, based on two
independent ratios (McGuire 0.41/1.69 = 0.24; Riisgård *a* 1.24 vs ~6). That gives about **0.13 L/h
for a 40 mm clam**. These are placeholders until our own pilot test replaces them.

**Temperature:** Cranford 2011 says lower temperature raises water viscosity and slows pumping, but
the retrieved sources give no temperature curve for our species. Riisgård 1988 measured at 27-29 °C,
de Silva at ~21 °C, and our bench runs at 16-20 °C. **Expect lower rates than the table; measure at
our temperature.**

### 4b. HAB-induced feeding suppression

| HAB | Bivalve | Effect | Threshold | Source |
|---|---|---|---|---|
| *Margalefidinium* | hard clam | CR ≈ 0 | ≥1,500 cells/mL (cleared at ≤1,000) | de Silva & Gobler 2023 |
| *Aureococcus* (brown tide) | mussel, clam | CR reduced; 30-100% mussel mortality | >5×10⁵ particles/mL (normal <2.5×10⁵) | Tracey 1988 |
| *Alexandrium fundyense* | mussel | CR −48% vs diatom; no mortality | at 256 cells/mL | Bricelj 1990 |
| *Alexandrium* (high toxicity) | hard clam | ate it only with diatom added | n/a | Bricelj 1991 |
| *Cochlodinium* | oyster seed | less feeding, no growth, mortality | field presence | Li 2012 |
| *Heterosigma* | oyster | shells partly or fully closed | 1 h exposure | Hégaret 2007 |
| *P. minimum* | juvenile oyster | filtered but rejected as pseudofaeces ~2 wk | n/a | Wikfors & Smolowitz 1995 |
| *Microcystis* (colonial) | Asian clam | CR lower on bloom water than culture | n/a | Straquadine 2022 |

**Pattern:** feeding shuts down above a density threshold, and some harmful species are rejected or
refused. Non-harmful dinoflagellates (*G. aureolum*) and diatoms (*T. weissflogii*) are cleared
normally. **For our non-toxic cultures, suppression should come from density and pseudofaeces, not
toxins.**

### 4c. Field and mesocosm drawdown

| Scale | Result | Source |
|---|---|---|
| 300 L mesocosm | brown tide 100× lower; 40% volume/d enough | Cerrato 2004 |
| 13 m³ mesocosm | sedimentation +58% at 16 clams/m² | Doering & Oviatt 1986 |
| Mesocosm | chl a significantly lower with 3 species | Wall 2008 |
| 5 L microcosm | 77-94% removal in 5 d | Meitei 2025 |
| Oyster nursery | no large phytoplankton effect | Li 2012 |
| Intertidal reefs | −9.8% to +27.9% chl removal | Grizzle 2008 |
| Bay (model) | 10× oysters → chl −~1 mg/m³ | Cerco & Noel 2007 |
| Bay (field) | filtration time 10 d; brown tides ended (correlational) | Gobler 2022 |
| LIS (model) | 1.3-2.7% of N removed | Bricker 2018 |

### 4d. Conflicts
1. **Maximum vs realistic rates.** Riisgård argues that reliable rates are the maximum lab rates. Cranford et al. and Doering & Oviatt show that maximum rates overestimate field effects by up to 10×. *Our resolution:* measure our own rates on our culture at our temperature.
2. **Oyster vs clam ranking.** Per gram, oysters are faster in McGuire 2024 and Riisgård 1988. In Meitei 2025 (tropical species) the clam was highest and the differences were not significant. Tenore & Dunstan ranked mussel > oyster > clam, while McGuire had mussel ≈ clam. It depends on diet, size and method.
3. **Small containers vs open water.** Containers show big drawdown (Cerrato, Meitei). Nurseries and reefs show small effects (Li, Grizzle, Cerco). The difference is volume per animal and flushing: Officer's criterion is easily met in a tank and rarely in open water. **So a bench success does not show field efficacy.**
4. **Preferential retention vs rejection.** Hégaret 2007 found HAB cells often retained preferentially, while Wikfors 1995 and Bricelj 1991 show refusal or rejection. It is species-specific.
5. **Loop timing.** `05_SHELLFISH.md` sets X = 7 days. Our calculation (Section 7) shows that realistic densities clear a 20 L tank in hours, so a **24 h X on the bench** is more informative, with 7 days kept for a field design.

---

## 5. Hypotheses for our experiment (falsifiable, fixed before running)

- **H1 (clearance exists):** in a 4-h static test at 18 ± 2 °C and salinity ~30, tanks with oysters lose chlorophyll faster than no-animal controls, with the control-corrected Coughlan CR > 0 (95% CI excludes 0). *Falsified if* CR's CI includes 0.
- **H2 (species):** per animal of similar shell length, oyster CR ≥ 2 × hard-clam CR, on the diatom. *Falsified if* the ratio is < 2 or reversed.
- **H3 (diatom vs dinoflagellate):** CR on the non-toxic dinoflagellate is within ±30% of CR on the diatom, as de Silva & Gobler found for *G. aureolum* vs *Rhodomonas*. *Falsified if* it is >30% lower.
- **H4 (density ceiling):** CR at the highest starting density (≥4× the lowest) is ≥30% lower than at the lowest, as in Tenore & Dunstan, Tracey, and de Silva. *Falsified if* CR does not fall.
- **H5 (loop):** in the 7-day loop, the shellfish arm's chlorophyll peak is ≥50% below the untreated control's peak when the dose clears ≥1 tank volume/day (Section 7). *Falsified if* the peak is <50% below.
- **H6 (structure control):** empty-shell bags do **not** lower chlorophyll vs no-bag controls (difference within ±15%). *Falsified if* they do, which would mean settling on the shells or bags explains part of the effect.
- **H7 (side effect):** total ammonia-N in shellfish tanks rises ≥2× over controls within 48 h at the loop dose (Kellogg 2013 direction). *Falsified if* not. This is a side-effect prediction, not a success criterion.

---

## 6. Mechanisms

1. **Filtration (gill pumping plus particle capture).** Cilia drive water through the gills. Particles are caught on the gill filaments: 100% above ~4 µm in *Mercenaria* and above ~5-6 µm in *Crassostrea* (Riisgård 1988). Clearance is the volume of water fully stripped of particles per hour.
2. **Removal vs growth balance.** A bloom declines when the daily fraction of volume cleared is greater than the algal growth rate (Officer 1982; Cerrato 2004: ~0.4 d⁻¹ sufficed there).
3. **Pre-ingestive selection.** Unwanted particles are bound in mucus and ejected as **pseudofaeces**. Algae can leave the water without being eaten (Wikfors 1995; Hégaret 2007), and some cells in biodeposits are intact.
4. **Behavioural shutdown.** Valve closure and reduced pumping when harmful algae are present or cells are too dense (de Silva 2023; Hégaret 2007; Tracey 1988; Li 2012). This caps the method at high bloom density.
5. **Biodeposition and recycling.** Faeces and pseudofaeces sink (Doering & Oviatt 1986: 21% of the extra sedimentation was permanent biodeposits). Excretion returns NH₄⁺ and phosphate (Kellogg 2013), which can feed regrowth in a closed tank.
6. **Toxin transfer.** Ingested toxins are kept in tissues: 79% incorporation for saxitoxin in mussels (Bricelj 1990). Depuration takes weeks, and oysters may not purge microcystin (Straquadine 2022).

---

## 7. Design numbers we adopt

### 7a. Formulas
- **Clearance (Coughlan 1969, as used by de Silva & Gobler 2023):** CR = (V/(n·t)) · [ln(C₀/Cₜ) − ln(C₀′/Cₜ′)], where V = water volume (L), n = animals, t = h, and primes are the no-animal control.
- **Animals for a target drop in a test:** n = V · ln(C₀/Cₜ) / (CR · t) **[our calc]**
- **Animals for the loop:** daily fraction cleared f = n · CR · 24 / V, so n = f · V / (24 · CR) **[our calc]**. Choose f ≥ 2 × the control's measured algal growth rate μ (d⁻¹), and never below Cerrato's 0.4 d⁻¹.

### 7b. Animals per tank [our calc, planning CRs from Section 4a; replace with pilot CR]

| Animal (shell length) | Planning CR (L/h) | 1 L beaker, 50% drop in 4 h | 20 L, 50% drop in 4 h | 20 L, f = 1.0 d⁻¹ | 40 L, f = 1.0 d⁻¹ |
|---|---|---|---|---|---|
| Oyster 25 mm | 0.23 | 0.8 → **1** | 15 | 3.6 → **4** | 7.3 → **8** |
| Oyster 40 mm | 0.53 | 0.3 → **1** | 6.5 → **7** | 1.6 → **2** | 3.1 → **4** |
| Oyster 60 mm | 1.09 | 0.2 → 1 | 3.2 → **4** | 0.8 → 1 | 1.5 → **2** |
| Hard clam 40 mm (~0.25× oyster) | 0.13 | 1.3 → **2** | 27 | 6.4 → **7** | 12.8 → **13** |

**What we adopt**
- **Pilot clearance test (first):** de Silva & Gobler format. **One animal per beaker**, 250 mL for 10-20 mm seed or **1 L for 25-40 mm**, n = 10 beakers per species × alga + 3 no-animal controls. Starve for 24 h. Sample at opening, then every 30 min for **4 h** (the 05 file's test length; the published protocol is 1 h). Keep depletion over any interval **<30%** where possible (Cranford 2011), and gently mix or aerate so the water is uniform.
- **Starting algal densities:** three levels. The lowest is near the prey densities that saturate feeding in the literature (Bricelj 1990: 150-250 cells/mL for a large dinoflagellate; de Silva: ≤1,000 cells/mL). The highest is ≥4× the lowest, to test H4. Record chlorophyll (µg/L) as well as cells/mL so diatom and dinoflagellate can be compared.
- **7-day loop arm (20-40 L tanks):** dose for **f = 1.0 d⁻¹** (2.5× Cerrato's 0.4 d⁻¹) using the *pilot* CR. With 40 mm oysters this is ~2 per 20 L or ~4 per 40 L. Cap density at **1 animal per 2 L** (Meitei 2025 upper bound) to limit ammonia and oxygen demand.
- **X (ON time):** **24 h on the bench** (turnover is <1 day at this dose), with re-measurement every 24 h. `MAX_ON` = 4 × X = 4 days on the bench. Keep **7 days** as the field value in `05_SHELLFISH.md` (Conflict 5). Holding tank between deployments: the non-toxic food alga at low density.
- **Controls:**
  1. No-animal tank (algae only), which also gives μ.
  2. **Empty-shell bags** (same shell count, size and mesh; shells scrubbed and dried), which tests structure and settling (H6).
  3. Animals in clean water with no algae, a baseline for ammonia and DO.
  4. The shared false-alarm arm from `00_CONTROL_LOOP.md`.
- **Algae:** diatom (*Thalassiosira weissflogii* is the non-toxic control diet in Bricelj 1990/1991; *Phaeodactylum* is acceptable) and a non-toxic dinoflagellate (a non-harmful *Gymnodinium* was cleared normally in de Silva 2023). **Measure cell size under the microscope**; cells <4-5 µm are not fully retained (Riisgård 1988).
- **Temperature and salinity:** 18 ± 2 °C, salinity 28-32 (de Silva used ~32). Log temperature, because CR depends on it (Cranford 2011).
- **Extra measurements:** count cells in collected pseudofaeces and faeces and check whether they are intact (Hégaret 2007; Wikfors 1995). Record gaping and closing every re-measure.

### 7c. Safety limits (EMERGENCY OFF, in addition to `00_CONTROL_LOOP.md`)
- **DO < 4 mg/L** (shared limit; Li 2012 shows feeding falls at the dawn DO minimum).
- **Total ammonia-N > 0.5 mg/L** (kept from `05_SHELLFISH.md`; Kellogg 2013 shows NH₄⁺ flux ≥10×). *The 0.5 mg/L value is our threshold; no retrieved source sets it.* Do a partial water change if it is reached.
- **Mortality > 10%**, or animals shut for more than 24 h, means stop and move them to the holding tank.
- **Never eat the animals.** Toxin accumulation happens fast and depuration is slow (Bricelj 1990/1991; McGuire 2024; Straquadine 2022). Use non-toxic cultures only, so no toxin forms are needed.
- Treat biodeposits as waste. Siphon them off, and filter them before the water goes to a drain.

### 7d. Sourcing and permits (not verified in this review)
- Buy seed from a licensed Connecticut or New York hatchery or farm. Ask the supplier, and the CT Department of Agriculture Bureau of Aquaculture, whether keeping animals in a closed school lab needs a permit, and how to dispose of them. **Never release animals or water into Long Island Sound.** These permitting facts were not retrieved here and must be confirmed.

---

## 8. Gaps and open questions

1. **Hard-clam CR per animal at 16-20 °C on our algae is not in any retrieved record.** Our 0.13 L/h is a ratio-based placeholder. The pilot test is required before the loop dose is set. Riisgård 1988's equations need reading in the PDF, because the abstract digits are garbled.
2. **Temperature curve.** No retrieved source gives CR vs temperature for *Mercenaria* or *Crassostrea*. Gobler 2022 cites Hibbert 1977 and Grizzle et al. 2001 (not retrieved).
3. **Ammonia numbers.** Srna & Baggaley 1976 (clam vs oyster excretion) was not readable. Our 0.5 mg/L limit is a precaution, not taken from a source.
4. **Pseudofaeces threshold** for our species and culture densities: no retrieved number. We will measure it.
5. **Does removal equal death?** Intact cells in biodeposits (Hégaret 2007) might resuspend and regrow in a tank. Test by incubating collected biodeposits in fresh medium.
6. **Shinnecock attribution.** It is still correlational; watershed nitrogen and flushing differ between bays.
7. **Scale-up gap.** Bench tanks meet Officer's criterion easily, while nurseries and reefs did not move phytoplankton much (Li 2012; Grizzle 2008). Bench success will not show field efficacy.
8. **Trigger-then-deploy vs always-present.** Every positive study had animals in place *before* the bloom (Cerrato, Gobler). Whether lowering bags after a forecast alert works is **untested**. That is the new question our loop answers.
9. **Permits and sourcing** in Connecticut still need confirming with the state and the supplier.

---

### Retrieval log
- OpenAlex `works/doi:` for abstracts (#1, 5, 9-17, 20-24). Crossref for DOIs and metadata (#4, 6, 8, 13-15, 24). Europe PMC for Bricelj 2005. Frontiers full text for #1 and #9 methods. Wiley chapter PDF (author-posted) for #7. Web-search snippets for #4, 6, 18 and 19, whose Springer pages were paywalled.
- Not retrieved (paywalled or blocked): full texts of Riisgård 1988 and 2001, Wall 2008, Cerrato 2004, Grizzle 2008, Cerco & Noel 2007, and Srna & Baggaley 1976.
