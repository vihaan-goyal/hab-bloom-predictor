# Evidence review: curcumin dosing (method 4)

Written 2026-09-25 for `notes/mitigation/04_CURCUMIN.md`. It covers curcumin and, as comparators,
related plant compounds (berberine, tannic acid, gallic acid, artemisinin, luteolin).

**How much of each source was read** is given in each block. "(abstract)" means a number came only
from the abstract. Hall et al. 2024 was read in full on the MDPI page. The Devillier et al. 2025 full
text sat behind a bot check that was not bypassed, so only its abstract was used. Records were
retrieved from Europe PMC, OpenAlex and Semantic Scholar.

Unit conversion used throughout: curcumin MW 368.4 g/mol, so **1 µM ≈ 0.37 mg/L**.

---

## 1. Summary and verdict

- **Does curcumin kill a marine dinoflagellate at the bench?** Yes. It is shown for one species,
  *Karenia brevis*, by one lab (Mote; #1, #2). The dose-response has a sharp step:
  - 0.1, 1 and 2 mg/L were statistically indistinguishable at every time point.
  - 3 mg/L separated from the low doses only at 72-96 h.
  - 5 mg/L gave 89% fewer cells at 24 h.
  - 30-40 mg/L gave >90% fewer cells by 4 h.
- **Other algae:** one abstract-level study on the raphidophyte *Chattonella* (#3; about 80% at
  10 mg/L, 72 h, as cited by #1).
- **No study was found on curcumin against a diatom, *Prorocentrum*, or *Microcystis*.** Searches
  for "curcumin photodynamic Microcystis" returned only bacterial and fungal work (#12). Our diatom
  arm is therefore new ground, not a replication.
- **Mechanism:** two routes, and they are not exclusive:
  - Dark chemistry: covalent inhibition of thioredoxin reductase, IC50 3.0 µM ≈ 1.1 mg/L (#4).
  - Light-driven ROS: curcumin is a blue-light photosensitizer (#6, #11, #12, #15).
  - No algal study has separated the two. A light-vs-dark arm is the cheapest informative
    experiment we can add.
- **Non-target conflict:** Devillier found no effect on adult clams, urchins or crabs at 5 mg/L over
  72 h (#2). But pure curcumin killed zebrafish embryos at LD50 ≈ 2.8 mg/L (24 h; #13). A solvent-borne
  formulation had a zebrafish LC50 of 5.9 mg/L (#14). Under sunlight, curcumin is lethal to mosquito
  larvae at 0.04-2.2 mg/L, and harmless to them in the dark (#15). **Our 5 mg/L cap sits at or
  above fish-embryo and small-invertebrate lethal levels.** The *Artemia* check must be run under
  the same light as the jars.
- **Persistence:** curcumin breaks down fast in neutral-to-alkaline water: 90% lost in 30 min at pH
  7.2 and 37 °C in dilute solution (#7). It also breaks down fast in light, with a photochemical
  half-life of minutes (#9). Seawater (pH ~8.1) is on the fast side. Yet Hall saw effects keep
  growing to 72-96 h. Either mg/L suspensions persist longer than dilute solutions (#6 notes this),
  or the kill is triggered early and plays out later. We have to measure this rather than assume.
- **Fluorescence interference is real, not hypothetical.** Curcumin absorbs at 410-430 nm. Its first
  pKa is 7.5-8.5, so at seawater pH part of it is the anion, which absorbs at 467 nm (#6). That is on
  top of our fluorometer's 470 nm excitation LED. A chlorophyll drop could be partly an optical
  artefact, so **cell counts must be the primary endpoint.**
- **Comparators:**
  - Berberine's kill of *Microcystis* is light-dependent: it did nothing in darkness and spared
    *Chlorella* (#18, #19). It kills the marine dinoflagellate *Karenia mikimotoi* at 120 h LC50
    3.1 mg/L (#17).
  - Tannic acid slows *Prorocentrum minimum* only above 2.5 mg/L, and halts photosynthesis at
    10 mg/L (#20).
  - Several of these compounds show hormesis or extra toxin release at low or intermediate doses
    (#24, #25).

**Verdict:** keep curcumin as a **comparison arm**, as 04_CURCUMIN.md already says. The dinoflagellate
arm is well grounded at 5 mg/L. Doses of 1-2.5 mg/L are predicted to do little within 24 h. The
diatom arm and the light dependence are genuinely open questions, and they are where a new result
could come from. Nothing here supports claims of bloom prevention or field readiness.

---

## 2. Master table

| # | Citation + link | Organism | Setting | Dose / duration | Result | Effective? |
|---|---|---|---|---|---|---|
| 1 | Hall et al. 2024, *Water* 16:1458 [doi](https://doi.org/10.3390/w16101458) | *Karenia brevis* | Lab: 1.5 L beakers, 10 L aquaria; 13 expts | 0.1-40 mg/L; 2-336 h | 5 mg/L: −89% cells at 24 h, −60% toxin; 0.1-2 mg/L no different from each other; 30-40 mg/L >90% by 4 h | Yes (≥5 mg/L) |
| 2 | Devillier et al. 2025, *L&O Methods* 24 [doi](https://doi.org/10.1002/lom3.10731) | *K. brevis*; clams, urchins, crabs | 1,400 L mesocosms, 2022 + 2024 | 5 mg/L; 72 h | Significant cell and toxin drop in 24 h; turbidity up; no N/P change; no animal effect (abstract) | Yes (mesocosm) |
| 3 | Liu et al. 2016, *ESPR* 23:17793 [doi](https://doi.org/10.1007/s11356-016-6755-5) | *Chattonella marina* | Lab | Curcumin + 4 others; 96 h | ~80% inhibition at 10 mg/L, 72 h (as cited by #1); gramine strongest | Partly |
| 4 | Taher et al. 2025, *Plant Physiol Biochem* [doi](https://doi.org/10.1016/j.plaphy.2025.110905) | *K. brevis* enzyme | In vitro | TrxR assay | IC50 3.0 µM (≈1.1 mg/L); covalent Cys53 adduct (abstract) | Mechanism |
| 5 | Yuan et al. 2021, *Toxins* 13:578 [doi](https://doi.org/10.3390/toxins13080578) | Mussel *Perna viridis* + *Prorocentrum lima* | Lab | Not in abstract | Less toxin in digestive gland, less damage (abstract) | Non-target benefit |
| 6 | Priyadarsini 2014, *Molecules* 19:20091 [doi](https://doi.org/10.3390/molecules191220091) | Chemistry | Review | n/a | λmax 410-430 nm; pKa1 7.5-8.5 (anion 467 nm); logP ~3; fast sunlight fading | Background |
| 7 | Wang et al. 1997, *J Pharm Biomed Anal* 15:1867 [doi](https://doi.org/10.1016/s0731-7085(96)02024-9) | Chemistry | Buffer, 37 °C | pH 3-10 | ~90% lost in 30 min at pH 7.2; faster at neutral-basic; vanillin, ferulic acid (abstract) | Degradation |
| 8 | Kharat et al. 2017, *J Agric Food Chem* 65 [doi](https://doi.org/10.1021/acs.jafc.6b04815) | Chemistry | Solutions, emulsions | 1 month | Unstable at pH ≥7; 10-50 µm crystals settle at pH <7; emulsion keeps 53-62% at pH 7-8 (abstract) | Carrier |
| 9 | Singh et al. 2013, *Pharmazie* 68:160 [PubMed](https://pubmed.ncbi.nlm.nih.gov/23556332/) | Chemistry | Pluronic preparations | pH 7.8-8.8 | Faster hydrolysis at pH 8-8.8; ethanol lowers stability; photochemical half-life "in the minutes range" (abstract) | Degradation |
| 10 | Tønnesen et al. 2002, *Int J Pharm* 244:127 [doi](https://doi.org/10.1016/s0378-5173(02)00323-x) | Chemistry | Cyclodextrin complexes | n/a | Solubility ≥10⁴× at pH 5; slower alkaline hydrolysis; *faster* photodecomposition (abstract) | Carrier |
| 11 | Laneri et al. 2023, *J Photochem Photobiol B* [doi](https://doi.org/10.1016/j.jphotobiol.2023.112756) | Chemistry | Nanocarriers, laser photolysis | n/a | No singlet oxygen detected; triplet H-abstraction → radicals → peroxyl radicals (abstract) | Mechanism |
| 12 | Winter et al. 2013, *Photochem Photobiol Sci* 12:1795 [doi](https://doi.org/10.1039/c3pp50095k) | *S. aureus*, *E. coli* | Lab PDI | 5-50 µM PVP-curcumin, 435 nm, 33.8 J/cm² | >6 log kill of *S. aureus* at 5 µM (≈1.8 mg/L); longer pre-incubation *less* toxic (abstract) | Yes (bacteria, light) |
| 13 | Wu et al. 2007, *Biol Pharm Bull* 30:1336 [doi](https://doi.org/10.1248/bpb.30.1336) | Zebrafish embryos/larvae | Lab | 24 h | LD50 7.5 µM embryos (≈2.8 mg/L), 5 µM larvae (≈1.8 mg/L); tail/spine defects, edema (abstract) | Non-target harm |
| 14 | Venturini et al. 2020, *ESPR* 27:29204 [doi](https://doi.org/10.1007/s11356-020-09210-4) | *Daphnia magna*, zebrafish | Lab | 3 formulations | Zebrafish LC50 5.9 mg/L (ethanol+DMSO); the solvents alone were "extremely toxic" to *Daphnia*; sugar formulations non-toxic (abstract) | Non-target, carrier |
| 15 | Lima et al. 2022, *Molecules* 27:5699 [doi](https://doi.org/10.3390/molecules27175699) | *Aedes* larvae; ECOSAR | Lab + simulated field, 21 d | 4.6 mg/L; sunlight | LT50 3 d; no toxicity in dark; cited LC50-3h 2.2-20 mg/L and LC50-24h 0.04 mg/L in sun; photoproducts predicted low-toxicity (full text) | Light-dependent |
| 16 | Abdullah et al. 2022, *Molecules* 27:4493 [doi](https://doi.org/10.3390/molecules27144493) | Zebrafish embryos | Lab | Native vs Pluronic-F127 curcumin | Nanoformulation delayed and lowered toxicity and ROS vs native (abstract; no numbers) | Carrier |
| 17 | Li et al. 2014, *Water Environ J* 28:270 [doi](https://doi.org/10.1111/wej.12033) | *Chattonella*, *Alexandrium*, *K. mikimotoi* | Lab | Berberine + 4 others | Berberine LC50-120h 3.1 mg/L on *K. mikimotoi*; effects species-selective (abstract) | Yes (comparator) |
| 18 | Liu et al. 2019, *Water Sci Technol* [doi](https://doi.org/10.2166/wst.2019.357) | *Microcystis*, *Chlorella* | Lab | Berberine, light vs dark | Kill light-dependent; PSII target; no effect on *Chlorella* either way (abstract) | Selective |
| 19 | Zhang et al. 2013, *Water Sci Technol* [doi](https://doi.org/10.2166/wst.2013.243) | *Microcystis* | Lab | Berberine 0.001% w/v (10 mg/L) | Strongest when light/temperature favour growth; "hardly" algicidal in darkness; raised extracellular microcystin (abstract) | Light-dependent |
| 20 | Jeong et al. 2016, *IJERPH* 13:503 [doi](https://doi.org/10.3390/ijerph13050503) | *Prorocentrum minimum* | Lab, 7 d | Tannic acid 0.5-10 mg/L | Growth fine <2.5 mg/L; slowed above; 10 mg/L halted photosynthesis; Hsp genes up 10-27× (full text sections) | Partly (≥5 mg/L) |
| 21 | Wang & Xu 2016, *PLoS ONE* 11:e0164842 [doi](https://doi.org/10.1371/journal.pone.0164842) | *Microcystis* | Lab, 120 h | Dihydroartemisinin to 24 mg/L; artemether to 6 mg/L | Max 42% inhibition at 24 mg/L DHA; 56% at 6 mg/L artemether; Fv/Fm to 0 (abstract) | Partly |
| 22 | Sang et al. 2024, *J Hazard Mater* [doi](https://doi.org/10.1016/j.jhazmat.2024.134241) | *Microcystis*, *Chlorella* | Lab | Artemisinin algaecide | Blocks the QB site and ferredoxin-NADP⁺ reductase; ROS; *Chlorella* resists (abstract) | Selective |
| 23 | Li et al. 2020, *Ecotoxicol Environ Saf* [doi](https://doi.org/10.1016/j.ecoenv.2020.110540) | *Microcystis* | Lab, 14 d | Luteolin 0.5-2× IC50 | IC50 ≈ 6.5 mg/L; inhibition plateaus or falls late (abstract) | Partly |
| 24 | Yin et al. 2025, *J Hazard Mater* [doi](https://doi.org/10.1016/j.jhazmat.2025.137205) | *Microcystis* | Lab, long-term | Tannic acid | High doses inhibit; one intermediate dose → extracellular MC-LR 1.91× control, day 15 (abstract) | Risk |
| 25 | Luo et al. 2024, *Sci Total Environ* [doi](https://doi.org/10.1016/j.scitotenv.2023.169765) | *Microcystis* | Lab | Gallic acid 10 mg/L → 0.001 µg/L | Hormesis: 0.1 µg/L raised growth 1.09× and toxin 1.85× (abstract) | Risk |

Context sources (not counted as evidence):
- Anderson et al. 2025, *Harmful Algae* 150:102989 ([doi](https://doi.org/10.1016/j.hal.2025.102989)): the review that calls marine HAB control underdeveloped.
- Mote's 2025 Red Tide Initiative report ("curcumin most effective", now in permitting; `notes/snowball/marine.md` #6). Not re-read this session.
- HAB-CTI funding for Mote's curcumin work on *Alexandrium* and *Pseudo-nitzschia* (marine.md #3). No results published yet.

---

## 3. Per-source detail

### #1 Hall et al. 2024: curcumin vs *K. brevis* (full text read)
- **Organism, setting:**
  - *K. brevis* CCMP 2228, diluted to ~1.0 × 10⁶ cells/L in filtered seawater (salinity 33).
  - Culture kept at 24 °C, salinity 32-34, 12:12 at 50-60 µmol m⁻² s⁻¹.
  - 13 experiments in 2019-2024: 1.5 L beakers under ambient fluorescent light (48 h), and 10 L aquaria at 12:12, 213 ± 12 µmol m⁻² s⁻¹ (48-336 h).
  - Each treatment at least in duplicate, plus a control of *K. brevis* and seawater.
- **Hypothesis:** curcumin cuts *K. brevis* cells and brevetoxins without harming water quality. The paper also set out to find the best dose and stock preparation.
- **Dose, carrier:**
  - Doses 0.1, 1, 2, 3, 5, 10, 20, 30, 40 mg/L of turmeric extract (>95% curcuminoids, Bulk Supplements).
  - Six stock methods: DI water; seawater; seawater heated to 40 °C for 1 h; seawater + 0.001% ethanol; seawater + 0.004% ethanol; 99.5-100% ethanol.
  - Stocks stored dark in glass and poured over the surface.
  - The paper does not report which stock method worked best.
- **Sampling:** live counts (neutral red stain, Sedgwick-Rafter) at 0, 2, 4-6 and 24 h, then daily. Brevetoxins by LC-MS/MS.
- **Results:**
  - Cells at 24 h: 5 mg/L −89.26% ± 3.57 SE; 3 mg/L −44.62% ± 10.12.
  - 0.1, 1 and 2 mg/L never differed from each other.
  - 3 mg/L beat 0.1 mg/L only from 72 h, and 1 mg/L only at 96 h.
  - 5, 10 and 20 mg/L never differed from each other. 30-40 mg/L gave >90% reduction from 4 h.
  - Toxins: 3 and 5 mg/L beat 1-2 mg/L from 24 h. At 72 h, 2 mg/L gave −41.9% and 5 mg/L −79.3% (the best toxin result). 40 mg/L gave −64.4% at 48 h.
  - Other time points recorded earlier in `notes/snowball/natural_compounds.md` #1 (from Table 1; not re-checked this session): 5 mg/L −67% at 48 h and −87% at 72 h; 3 mg/L −65% at 96 h; 30 mg/L −99.4% by 6 h.
- **Carrier control:** an ethanol-only control did not differ from the plain control (p = 0.77).
- **White curcumin:** CuroWhite and zedoary never exceeded 50% reduction at 5-50 mg/L.
- **Water quality:**
  - pH, salinity, temperature and DO stayed in narrow ranges. The exception was the ethanol experiment, where **DO fell from 6-7 to 1.55 mg/L by 48 h**, attributed to a bacterial bloom.
  - Nutrients unchanged in 10 L tanks.
  - Water turned light yellow to dark orange.
- **Mechanism:** not tested. The authors discuss curcumin as a photocatalyst and ROS source, ROS-triggered caspase-like death, and the fact that parent toxins were *not* converted to analogues. That last point is unlike PAC clay.
- **Relevance to us:**
  - Sets the 5 mg/L threshold and the 24 h window.
  - Predicts that a 1 mg/L first pulse does nothing measurable at 24 h.
  - The ethanol DO crash is a warning for small, warm jars.
  - The light level is known for the aquaria only.

### #2 Devillier et al. 2025: 1,400 L mesocosms (abstract only)
- **Setup:** two runs (2022, 2024), 5 mg/L curcumin, ~1.0 × 10⁶ *K. brevis* cells/L. The 2024 run added nutrients, water clarity, and hard clams, sea urchins and blue crabs (mortality, behaviour, toxin content).
- **Results:**
  - Cells and total toxins fell significantly within 24 h in both runs.
  - Turbidity rose significantly. Dissolved N and P did not change.
  - No significant effect on animal mortality or behaviour at 72 h.
  - Percentages, carrier and persistence are not in the abstract.
- **Relevance to us:**
  - The only scale-up evidence.
  - Adult macro-invertebrates are far less sensitive than larvae or embryos (compare #13-#15), so "no harm" here does not cover *Artemia* nauplii.
  - The turbidity may be undissolved curcumin; see #8 on crystals settling.

### #3 Liu et al. 2016: *Chattonella marina* (abstract + citation in #1)
- Five herb compounds tested; gramine was strongest (96 h LC50 0.51 mg/L; oxidative stress, lower Fv/Fm).
- Per Hall et al., curcumin at 10 mg/L gave about 80% inhibition at 72 h. The group dropped curcumin because it coloured the water. Curcumin was dissolved in absolute ethanol (per #1).
- **Relevance:** a second, non-dinoflagellate marine target. It suggests the effective dose may be higher than 5 mg/L outside *K. brevis*.

### #4 Taher et al. 2025: the mechanism (abstract)
- Curcumin inhibits *K. brevis* thioredoxin reductase in a time-dependent way, with IC50 3.0 µM (≈1.1 mg/L), about 20× more potent than PbTx-2.
- It forms a covalent Michael adduct at Cys53, turning the enzyme into a pro-oxidant.
- **Relevance:**
  - This route needs no light.
  - TrxR is universal, so diatoms may be hit too. That supports testing the diatom arm rather than assuming it is immune.
  - The IC50 is below our 2.5 mg/L step, but cellular uptake is unknown.

### #5 Yuan et al. 2021: mussels (abstract)
- Curcumin reduced accumulation of diarrhetic shellfish toxins in *Perna viridis* fed *P. lima*, and reduced digestive-gland damage (via AhR/HR96/CYP3A4 induction).
- Hall notes they dissolved curcumin in dilute NaOH.
- **Relevance:** a positive non-target effect. It uses a *toxic* *Prorocentrum*, which is not suitable for us.

### #6 Priyadarsini 2014: the chemistry of curcumin (full text searched)
- Nearly insoluble in water; logP ~3. Dissolves in ethanol, DMSO and methanol.
- Visible absorption peak at 410-430 nm (ε 55,000 M⁻¹ cm⁻¹ at 425 nm in methanol).
- The first pKa is 7.5-8.5 and turns curcumin from yellow to red. The fully deprotonated form absorbs at 467 nm.
- Degradation runs through the β-diketone:
  - In µM solutions, 90% degrades in 30 min, but less at higher concentration.
  - Much faster in sunlight, giving vanillin, ferulic acid and small phenols.
  - Some reports link singlet oxygen and ROS to its photodynamic activity.
- **Relevance:** the basis of the fluorescence-interference and fading measurements in §7.

### #7 Wang et al. 1997: stability in buffer (abstract)
- About 90% decomposed within 30 min in 0.1 M phosphate buffer at pH 7.2 and 37 °C.
- Faster at neutral-basic pH. Serum proteins slow it down (<20% lost in 1 h; ~50% left at 8 h).
- **Relevance:** in seawater, the dissolved fraction should disappear within hours. Organic matter from dense cultures may slow that.

### #8 Kharat et al. 2017: solutions vs emulsions (abstract)
- Pure curcumin was highly unstable at pH ≥7.0 and crystallised at pH <7 (10-50 µm crystals, fast sedimentation).
- An MCT oil-in-water emulsion retained 62%, 60% and 53% at pH 7.0, 7.4 and 8.0 after a month at 37 °C.
- **Relevance:** a food-grade emulsion carrier would lengthen exposure but adds oil. Crystals may explain the turbidity in #2.

### #9 Singh et al. 2013: hydrolysis and light (abstract)
- Hydrolysis faster at pH 8.0-8.8 than below 8.0, and faster in carbonate than phosphate buffer (seawater is carbonate-buffered).
- Adding ethanol *decreased* hydrolytic stability.
- Photochemical half-life "in the minutes range".
- **Relevance:** under jar lights, dissolved curcumin may be gone within an hour. Track absorbance at 425 nm.

### #10 Tønnesen et al. 2002: cyclodextrin (abstract)
- Complexes raised water solubility at least 10⁴× (pH 5) and improved alkaline stability, but *sped up* photodecomposition.
- **Relevance:** an ethanol-free carrier option (hydroxypropyl-β-cyclodextrin). It needs its own carrier-only control.

### #11 Laneri et al. 2023: photochemistry in carriers (abstract)
- In micelles, microemulsions, zein and albumin, no singlet oxygen was detected.
- Instead, the excited triplet pulls hydrogen atoms from its host, making ketyl radicals that oxygen turns into peroxyl and hydroperoxyl radicals.
- **Relevance:** "photodynamic" may mean radical (Type I) chemistry rather than singlet oxygen. Either way the prediction is the same: stronger effect in light.

### #12 Winter et al. 2013: curcumin photodynamic inactivation (abstract)
- PVP-bound curcumin at 5 µM (≈1.8 mg/L), 5 min incubation, then 435 nm LED at 33.8 J/cm², gave a >6 log10 kill of *S. aureus*. 50 µM for 15-25 min eradicated it.
- *E. coli* needed CaCl₂ to open the cell wall.
- **Longer pre-incubation lowered phototoxicity**, likely because curcumin decayed.
- **Relevance:**
  - The strongest direct evidence that light plus low-mg/L curcumin kills microbes.
  - Suggests a short, bright light pulse after dosing could matter more than dose.
  - Blue light near 435 nm is also what algae absorb, so a light control is essential.
  - No algal study of this kind was found.

### #13 Wu et al. 2007: zebrafish embryos (abstract)
- 24 h LD50: 7.5 µM for embryos (≈2.8 mg/L) and 5 µM for larvae (≈1.8 mg/L).
- Defects: hooked tails, bent spine, pericardial edema, slow yolk resorption, shorter body.
- **Relevance:** the lowest non-target lethal level found, **below our 5 mg/L cap**. It directly conflicts with #2's "no harm" (different life stage and fresh water). This is the strongest reason to keep a larval non-target test.

### #14 Venturini et al. 2020: photolarvicide safety (abstract)
- Tested curcumin in ethanol+DMSO, in sucrose, and in D-mannitol on *Daphnia magna* and zebrafish.
- Zebrafish LC50 was 5.9 mg/L for the ethanol+DMSO formulation.
- In *Daphnia*, the **solvents were "extremely toxic"**, so no LC50 could be estimated.
- The sugar formulations were non-toxic to both. *Daphnia* made ROS at 50 mg/L (mannitol formulation), and its feeding was unaffected.
- **Relevance:** the carrier can be more toxic than curcumin itself. A carrier-only control is mandatory, and total solvent must stay minimal.

### #15 Lima et al. 2022: sunlight-activated curcumin (full text searched)
- 4.6 mg/L with sucrose in sunlight: *Aedes* larval LT50 of 3 days over 21 days. No toxicity in the dark.
- Cited values: LC50-3h of 20.0, 11.6 and 2.2 mg/L (natural turmeric, synthetic, and sucrose formulation) at 30-60 mW/cm² sun; LC50-24h of 0.04 mg/L after 8 h of sun (Souza et al.).
- Photoproducts (m/z 194, 278, 370) were identified at 0, 90 and 180 min under 100 mW/cm². Their toxicity was **predicted by ECOSAR, not measured**.
- **Relevance:**
  - Strong evidence that curcumin's animal toxicity is **light-gated**.
  - An *Artemia* test run in the dark would understate harm.
  - Breakdown products are only computer-assessed.

### #16 Abdullah et al. 2022: nano-curcumin, zebrafish (abstract)
- Pluronic F127 micelles delayed and reduced embryo toxicity and ROS compared with native curcumin. No numbers in the abstract.
- **Relevance:** carriers change toxicity, and may change algicidal potency the same way.

### #17 Li et al. 2014: berberine and others vs marine HABs (abstract)
- ε-polylysine, betaine, stachydrine and berberine inhibited *C. marina*, *A. tamarense* and *K. mikimotoi* selectively. Chitosan did nothing.
- Only berberine inhibited *K. mikimotoi* (LC50 at 120 h: 3.1 mg/L).
- **Relevance:** a plant compound in the same potency range as curcumin against a marine dinoflagellate. Selectivity differs by species.

### #18 Liu et al. 2019 and #19 Zhang et al. 2013: berberine needs light (abstracts)
- Berberine's kill of *Microcystis* was **light-dependent**: no fluorescence change and "hardly" any kill in constant darkness. It targets PSII.
- The green alga *Chlorella* was unaffected in light or dark.
- The effect was strongest when conditions favoured algal growth.
- It raised extracellular microcystin by lysing cells.
- **Relevance:** the template for our light-vs-dark test. It predicts that fast-growing, well-lit cultures respond most.

### #20 Jeong et al. 2016: tannic acid vs *Prorocentrum minimum* (full-text excerpts)
- 0.5, 2.5, 5 and 10 mg/L over 7 days.
- Growth was normal below 2.5 mg/L, slowed above it, and 10 mg/L halted photosynthesis (Fv/Fm, FRR fluorometer).
- Hsp70/Hsp90 up 10-27× at 48 h.
- **Relevance:** the closest organism to our planned *Prorocentrum*. It shows a threshold near 2.5-5 mg/L for a polyphenol.

### #21 Wang & Xu 2016 and #22 Sang et al. 2024: artemisinin (abstracts)
- Dihydroartemisinin: at most −42% at 24 mg/L after 120 h. Artemether: −56% at 6 mg/L, with Fv/Fm, ΦPSII and ETR falling to 0.
- Artemisinin displaces plastoquinone at the QB site, disrupts the ferredoxin-NADP⁺ reductase, and causes ROS build-up.
- *Chlorella* survives through antioxidant defences and repair.
- **Relevance:** photosynthesis-targeting compounds act slowly (120 h) and spare green algae. It is not a good fit for a 24 h loop.

### #23 Li et al. 2020: luteolin (abstract)
- IC50 ≈ 6.5 mg/L sustained to day 14. Inhibition rose with dose, but at each dose it first rose and then plateaued or fell as cells mounted CAT/GSH defences.
- **Relevance:** a sign of adaptation. Repeated pulses may be needed, which fits the MAX_ON = 4 pulses rule.

### #24 Yin et al. 2025 and #25 Luo et al. 2024: dose risks (abstracts)
- Tannic acid at one intermediate dose raised extracellular MC-LR 1.91× on day 15.
- Gallic acid at 0.1 µg/L raised *Microcystis* growth 1.09× and toxin 1.85× (hormesis as the dose dilutes).
- **Relevance:** as the dose fades, low residual concentrations may *stimulate* growth. Hence the cool-down watch, and our regrowth hypothesis H-C7.

---

## 4. Aggregated data

### Effect vs dose and time (curcumin, algae)

| Dose (mg/L) | 2-6 h | 24 h | 48-96 h | Source |
|---|---|---|---|---|
| 0.1-2 | ~0 | 2-45% range (0.1-3 mg/L); no difference among 0.1/1/2 | 2 mg/L: toxin −42% at 72 h | #1 |
| 3 | small | −45 ± 10% | ~−65% at 96 h (table transcription) | #1 |
| 5 | small | **−89 ± 4%**; toxin −60% | −67% (48 h), −87% (72 h); toxin −79% (72 h) | #1 |
| 5 (1,400 L) | n/a | "significant" cell + toxin drop | n/a | #2 |
| 10 | n/a | n/a | ~−80% *C. marina* (72 h) | #3 via #1 |
| 10-20 | n/a | not different from 5 | n/a | #1 |
| 30-40 | **>90% from 4 h**; ~100% by 6 h | 100% | toxin ≥−64% (48 h) | #1 |

**Reading:** a threshold between 3 and 5 mg/L for *K. brevis* at 24 h, a plateau from 5 to 20 mg/L, and a fast-kill regime at 30 mg/L and above. The 48 h dip at 5 mg/L (89% → 67%) hints at partial recovery or counting noise.

### Light dependence

| Compound | Organism | Light | Dark | Source |
|---|---|---|---|---|
| Curcumin (PVP) | *S. aureus* | >6 log kill at ~1.8 mg/L + 33.8 J/cm² blue | not reported | #12 |
| Curcumin | *Aedes* larvae | LC50-24h 0.04 mg/L; LT50 3 d at 4.6 mg/L | no mortality <25 mg/L | #15 |
| Berberine | *Microcystis* | algicidal | "hardly" algicidal | #18, #19 |
| Curcumin | *K. brevis* | effective (lit beakers and aquaria) | **never tested** | #1 |
| Curcumin | TrxR enzyme | n/a | IC50 1.1 mg/L (no light needed) | #4 |

### Effective concentrations of comparators (algae)

| Compound | Organism | Value | Source |
|---|---|---|---|
| Curcumin | *K. brevis* TrxR (enzyme) | IC50 3.0 µM ≈ 1.1 mg/L | #4 |
| Berberine | *K. mikimotoi* | LC50-120h 3.1 mg/L | #17 |
| Gramine | *C. marina* | LC50-96h 0.51 mg/L | #3 |
| Luteolin | *Microcystis* | IC50 ≈ 6.5 mg/L (14 d) | #23 |
| Tannic acid | *P. minimum* | no effect <2.5; photosynthesis stops at 10 mg/L | #20 |
| Artemether | *Microcystis* | −56% at 6 mg/L (120 h) | #21 |

### Non-target thresholds (curcumin)

| Organism, stage | Value | Light | Source |
|---|---|---|---|
| Zebrafish larvae | LD50-24h ≈ 1.8 mg/L (5 µM) | lab (unspecified) | #13 |
| Zebrafish embryos | LD50-24h ≈ 2.8 mg/L (7.5 µM) | lab (unspecified) | #13 |
| Zebrafish | LC50 5.9 mg/L (ethanol+DMSO) | lab | #14 |
| *Daphnia magna* | solvent carrier "extremely toxic"; sugar formulation non-toxic | lab | #14 |
| *Aedes* larvae (insect) | LC50-24h 0.04 mg/L; none in dark <25 mg/L | sunlight | #15 |
| Hard clam, urchin, blue crab (adults) | no effect at 5 mg/L, 72 h | mesocosm | #2 |

### Persistence

| Condition | Loss | Source |
|---|---|---|
| µM solution, pH 7.2, 37 °C, dark | ~90% in 30 min | #7, #6 |
| pH 8.0-8.8 vs <8 | faster | #9 |
| Light | half-life of minutes | #9 |
| Emulsion, pH 8, 37 °C | 47% lost in 1 month | #8 |
| Hall's jars | effect still growing at 72-96 h | #1 |

### Conflicts
1. **Harmless vs toxic to animals.** No effect on adult clams, crabs or urchins at 5 mg/L (#2), against a zebrafish larva/embryo LD50 of 1.8-2.8 mg/L (#13) and light-gated insect-larva toxicity at 0.04-2.2 mg/L (#15). Likely explanations: life stage, fresh vs salt water, light, and carrier. **Unresolved for *Artemia*.**
2. **Fast degradation vs long-lasting effect.** Chemistry says minutes to hours (#7, #9); the algal effect builds over 24-96 h (#1). Either a short exposure triggers a delayed death, or particulate curcumin persists. Measuring A425 over time answers this.
3. **Singlet oxygen vs radicals vs enzyme.** #6 cites singlet oxygen, #11 found none in carriers, and #4 needs no light. The mechanism is open.
4. **Carrier harmless vs harmful.** Hall's ethanol control showed no effect on cells (#1), but the ethanol experiment's DO crashed to 1.55 mg/L, and in #14 the solvents were the most toxic part for *Daphnia*.
5. **"Low early dose works" (our H1) vs Hall.** 1-2 mg/L never differed from 0.1 mg/L in #1. The loop's first pulse may be wasted unless light or low cell density make it more potent. That is a testable claim, not a given.

---

## 5. Hypotheses for our experiment (falsifiable)

Each is stated with its prediction. Test against the **carrier-only control**, n = 3 jars, mean ± 95% t-interval.

| ID | Hypothesis | Prediction; falsified if | Basis |
|---|---|---|---|
| H-C1 | 5 mg/L cuts *Prorocentrum micans* cells | ≥50% fewer cells than carrier control at 24 h; falsified if the 95% CI of the reduction includes <50% | #1, #2 |
| H-C2 | ≤1 mg/L does nothing measurable in 24 h | 1 mg/L within ±20% of carrier control at 24 h; falsified if >20% reduction | #1 |
| H-C3 | The diatom is less sensitive than the dinoflagellate | *Phaeodactylum* % reduction at 5 mg/L, 24 h, is less than half the *Prorocentrum* one; falsified if equal or greater | untested; #18, #22 selectivity pattern; #4 (a universal enzyme argues against it) |
| H-C4 | Kill is light-enhanced | At 2.5 mg/L, 24 h reduction under 12:12 light is ≥2× that in foil-wrapped (dark) jars; falsified if the ratio's CI includes 1 | #12, #15, #18, #19 |
| H-C5 | The fluorometer overstates the kill | In treated jars, % drop in fluorescence exceeds % drop in cell count by ≥10 points at 5 mg/L; falsified if within 10 points | #6 (absorbs at 425/467 nm vs 470 nm LED) |
| H-C6 | Dissolved curcumin fades quickly in light | A425 of an algae-free 5 mg/L jar falls ≥50% within 24 h in light, and less in dark; falsified if <50% | #7, #9, #6 |
| H-C7 | Survivors regrow after a single pulse | Cells in single-pulse 2.5 mg/L jars rise again between 48 and 96 h; falsified if cells stay flat or fall | #1 (48 h dip), #23, #25 |
| H-C8 | 5 mg/L is not safe for larval non-targets under light | *Artemia* nauplii 24 h survival at 5 mg/L, **in light**, is >20 points below carrier control (safety limit hit); falsified if within 20 points | #13, #15 vs #2 |

H-C8 is written so that the safety-limit outcome is the prediction. If it holds, the loop's cap
must come down (see §7).

---

## 6. Mechanisms

| Route | Needs light? | Evidence | What we can observe cheaply |
|---|---|---|---|
| **Thioredoxin reductase inhibition** (covalent Cys adduct; the enzyme becomes a pro-oxidant) | No | #4, *K. brevis* enzyme, IC50 ~1.1 mg/L | Kill in the dark arm |
| **Photosensitised ROS** (curcumin absorbs 410-470 nm; triplet → radicals and/or singlet O₂) | Yes | #6, #11, #12, #15 (bacteria, insects); discussed but untested for algae in #1 | Light arm ≫ dark arm |
| **Photosynthesis (PSII) damage**, then ROS | Yes (via photosynthesis) | Comparators: berberine #18, artemisinin #21-22, tannic acid #20, gramine #3 | Colour loss, Fv/Fm if available |
| **Membrane damage / lysis** | ? | Berberine lyses cells (#19); Hall's cells disappeared from counts (#1) | Neutral red live/dead stain; debris in counts |
| **Oxygen scavenging / toxin chemistry** | ? | Parent brevetoxins not converted (#1) | Not relevant to non-toxic cultures |

Overall: the evidence is consistent with oxidative stress as the final common path, from an
enzyme route (dark) and a photosensitiser route (light). Our light/dark contrast (H-C4) is the one
measurement that separates them at the bench.

---

## 7. Design numbers we adopt

| Item | Value | Source / reason |
|---|---|---|
| **X (ON time)** | **24 h** per pulse, re-measure, then next pulse | #1: 5 mg/L reaches −89% at 24 h |
| **Pre-loop dose-response jars** | 0 (carrier), 0.5, 1, 2.5, 5, 10 mg/L; count at 0, 6, 24, 48, 72 h | Brackets Hall's 3-5 mg/L step (#1); 10 mg/L matches #3 |
| **Loop ladder** | 1 → 2.5 → 5 mg/L (as in 04_CURCUMIN.md); cumulative ≤13.5 mg/L; `MAX_ON` = 4 pulses | H-C2 predicts 1 mg/L fails; keep it because testing that is part of H1 |
| **Dose cap** | **5 mg/L**, lowered to the highest dose that passes the *Artemia* light test if H-C8 holds | #2 mesocosm level; #13 fish LD50 1.8-2.8 mg/L |
| **Curcumin** | ≥95% curcuminoid powder (food/supplement grade), not turmeric spice, not "white" curcumin | #1 (white <50% effect) |
| **Carrier** | Ethanol stock in glass, stored dark, made fresh each dosing day. Choose the stock strength so the top dose adds **≤0.05% v/v** ethanol, and confirm by eye and filter that it is fully dissolved | #1 (ethanol stock; ethanol control OK), #9 (ethanol speeds hydrolysis), #14 (solvent toxicity) |
| **Carrier control** | Same ethanol volume, no curcumin, in every run, for algae *and* *Artemia* | #1, #14 |
| **Optional carrier arm** | Hydroxypropyl-β-cyclodextrin, with its own carrier control | #10 |
| **Light** | 12:12, measure PAR at jar height and report it; aim near culture light (50-60 µmol m⁻² s⁻¹) as in #1's cultures. **Light vs foil-wrapped dark jars at 2.5 mg/L** (H-C4) | #1, #12, #15, #18 |
| **Fluorescence interference** | (a) Algae-free seawater spiked at every dose, read on the fluorometer at every step and subtracted. (b) Curcumin spiked into a *known* culture dilution to get a correction factor. (c) **Cell counts are the primary endpoint**; fluorescence is secondary. (d) Record pH, because the anion at pH ≥7.5 shifts absorbance to 467 nm | #6 |
| **Curcumin tracking** | Absorbance at ~425 nm (cheap spectrometer or LED photometer) on algae-free spiked jars, light and dark, at 0, 1, 6, 24 h | #6, #7, #9 |
| **Live/dead** | Neutral red stain before Sedgwick-Rafter counts, as Mote did | #1 |
| **Non-target test** | *Artemia* nauplii, 24 h, **under the same light** as the jars, at each dose used plus carrier control | #13, #15 |
| **Safety limits** | DO <4 mg/L; pH outside 7.6-8.6; *Artemia* survival >20 points below carrier control; turbidity >3× control (all from 00/04 files). Add: **DO falling >2 mg/L in 24 h in any carrier-control jar → stop and check for bacterial bloom** | #1 (DO 1.55 mg/L in ethanol test), #2 (turbidity) |
| **Cool-down** | 5 days bench, counting regrowth | #23, #25 (hormesis, adaptation) |

---

## 8. Gaps / open questions

1. **No curcumin data for diatoms, *Prorocentrum*, or cyanobacteria.** The "curcumin + *Microcystis* / photodynamic" searches (Europe PMC, OpenAlex, web) found nothing algal. Our diatom and *Prorocentrum* arms are first tests, and a null result is informative.
2. **Devillier 2025 details unread:** carrier, percentage reductions, persistence, and the cause of the turbidity. Ask Mote, or get the PDF through a library.
3. **Hall's table values at 48-96 h** are from an earlier transcription; recheck Table 1 before quoting 67% and 87%.
4. **Light dependence of the algicidal effect is untested** in any algae study. H-C4 is the one new-science question here.
5. **Non-target safety for marine larvae.** No curcumin *Artemia* or copepod LC50 was found. Zebrafish (#13) and insect larvae (#15) suggest the risk is real in light.
6. **Breakdown products** are only predicted by ECOSAR (#15), and vanillin and ferulic acid are identified (#7). Nothing is measured in marine animals.
7. **Persistence at mg/L in seawater** with cells present is unknown; the chemistry data are for µM buffers.
8. **Which of Hall's six stock methods worked best** is not reported. Food-grade emulsion or sugar carriers (#8, #14) might lower toxicity and raise persistence, but are untested on algae.
9. **Mote's HAB-CTI curcumin work on *Alexandrium* and *Pseudo-nitzschia*** (a diatom) has no published results yet. Watch for it; it would answer gap 1.
10. **Toxin-release risk at sub-lethal doses** is shown for tannic and gallic acid (#24, #25), not curcumin. Not measurable with non-toxic cultures; note it as a limitation.
