# Evidence review: coarse-bubble aeration and turbulence against bloom algae

Written 2026-09-25 for method 1 (`notes/mitigation/01_BUBBLES.md`), which plugs into the loop in
`00_CONTROL_LOOP.md`. Every source below was retrieved as a record (DOI resolved through OpenAlex,
Europe PMC, Crossref or Semantic Scholar). Most were read as **abstract only**; numbers marked
"(abstract)" come from the abstract, and "(via ...)" means the number comes from a later paper's summary.
Numbers marked **[our calc]** are our own arithmetic, not from a source.

## 1. Summary and verdict

Bubbling and stirring slow many **dinoflagellates**, but they do not reliably kill them, and the effect
depends heavily on the species. In lab cultures, turbulence or shear stops cell division within hours
(G2/M arrest) and cuts net growth by roughly 25-55%. Cells die only after about 4 days of continuous
agitation, and division restarts as soon as the water is calm again. One bench study on a Long Island
fish-killer (*Margalefidinium*) used real macrobubbles and got more than 60% lower cell density. However,
of 10 dinoflagellate species in one tank study, 3 grew *faster* under turbulence.

**Diatoms are the opposite case.** Moderate turbulence usually helps them or has no effect (for
*Thalassiosira*, 34-72% higher final density; *Phaeodactylum* shows no response). They are harmed only at
shear stresses around 1 Pa, or by tiny bubbles bursting at the surface.

In lakes and reservoirs, bubble-plume mixing works through light limitation and destratification, not
shear. It succeeds only in deep, well-designed systems, and it often shifts the community to diatoms.

**Verdict:**
- **Moderate evidence** that bubbling suppresses the growth of *sensitive* dinoflagellates at bench scale (many independent lab studies, consistent mechanism).
- **Weak evidence** that it works as a bloom control outside tanks and enclosures (one bench paper on a HAB species with bubbles, one reservoir field study).
- **Strong evidence** that the response is species-specific and reversible.

It is a growth *brake*, not a kill switch. This review makes no claim about prevention or field-readiness.

## 2. Master table

ε = turbulent energy dissipation rate (m² s⁻³). γ = shear rate (s⁻¹). τ = shear stress (Pa = N m⁻²).

| # | Citation + link | Organism | Setting | Dose / duration | Result | Effective? |
|---|---|---|---|---|---|---|
| 1 | Sung & Gobler 2026, *J Environ Manage* [10.1016/j.jenvman.2026.129015](https://doi.org/10.1016/j.jenvman.2026.129015) | *Margalefidinium polykrikoides* (culture + bloom water), fish | Lab bench | Macrobubbles (> 100 µm) vs nanobubbles (± ozone) vs orbital shaking; flow rates not seen | Density > 60% lower (macro) vs < 20% (nano); lower photosynthetic efficiency; fish survival up to 100% vs 100% mortality in unbubbled controls; *Prorocentrum cordatum* promoted | Yes (bench) |
| 2 | Thomas & Gibson 1990a, *Deep-Sea Res* 37:1583 [10.1016/0198-0149(90)90063-2](https://doi.org/10.1016/0198-0149(90)90063-2) | *Lingulodinium* (= *Gonyaulax*) *polyedra* | Lab, Couette cylinders | Constant γ | Zero growth at γ ≈ 8 s⁻¹; negative above 8; no effect below 2 (via #3) | Yes |
| 3 | Gibson & Thomas 1995, *J Geophys Res* [10.1029/95jc02256](https://doi.org/10.1029/95jc02256) | *L. polyedra* | Lab, Couette | γ ≈ 9 s⁻¹ for 5 min to 2.5 h per day | 0.25-2.5 h/day gave negative growth; 5 min/day no effect; the daily-mean γ needed for zero growth fell to < 0.09 s⁻¹ with intermittency (abstract) | Yes; **pulses work** |
| 4 | Thomas, Vernet & Gibson 1995, *J Phycol* [10.1111/j.0022-3646.1995.00050.x](https://doi.org/10.1111/j.0022-3646.1995.00050.x) | *L. polyedra* | Lab, rotating bottles + Couette | Up to 26.6 s⁻¹ | Photosynthesis is less sensitive than growth; photosynthesis per cell rises; respiration rises (abstract) | Growth yes, photosynthesis no |
| 5 | Berdalet 1992, *J Phycol* 28:267 [10.1111/j.0022-3646.1992.00267.x](https://doi.org/10.1111/j.0022-3646.1992.00267.x) | *Akashiwo sanguinea* (= *Gymnodinium nelsonii*) | Lab flasks, orbital shaker 100 rpm | 10 d; > 20 d | Division stopped; cell volume up to 1.5×; DNA/RNA per cell up to 10×; after stopping, division at once at ~2/3 of the control rate; > 20 d → total death (abstract) | Yes (reversible) |
| 6 | Berdalet et al. 2007, *J Phycol* [10.1111/j.1529-8817.2007.00392.x](https://doi.org/10.1111/j.1529-8817.2007.00392.x) | *Alexandrium minutum*, *Prorocentrum triestinum*, *Gymnodinium* sp. | Lab flasks, shaker 100 rpm | ε ≈ 2 × 10⁻⁴ | Net growth −33% (*A. minutum*), −28% (*P. triestinum*), none (small *Gymnodinium*); cell volume up to 1.4× / 2.5×; swimming speed halved; full recovery in still water (abstract) | Species-specific |
| 7 | Llaveria et al. 2009, *J Phycol* [10.1111/j.1529-8817.2009.00740.x](https://doi.org/10.1111/j.1529-8817.2009.00740.x) | *A. minutum* | Lab flasks, shaker | Same setup as #6; days | Immediate, transient G2/M arrest with no mortality; mortality and swollen cells only after > 4 d (abstract) | Pause first, kill later |
| 8 | Bolli et al. 2007, *Biogeosciences* [10.5194/bg-4-559-2007](https://doi.org/10.5194/bg-4-559-2007) | *A. minutum*, *A. catenella* | Lab flasks | ε = 4 × 10⁻⁵ vs 2.7 × 10⁻³; > 4 d | High ε only: *A. minutum* μ 0.25 → 0.19 d⁻¹, final cells 55.4% lower; *A. catenella* ~23% lower final cells; cysts suppressed, recovered after stop; low ε no effect (abstract) | Yes at high ε only |
| 9 | Sullivan & Swift 2003, *J Phycol* 39:83 [10.1046/j.1529-8817.2003.02094.x](https://doi.org/10.1046/j.1529-8817.2003.02094.x) | 10 dinoflagellate species | Lab, 20 L tanks, oscillating rods | ε ≈ 10⁻⁴ vs 10⁻⁸ vs still | 1 slower (*Ceratium fusus*); 2 no increase; 4 unaffected; 3 **faster** (*Lingulodinium*, *G. catenatum*, *A. fundyense*) (abstract) | Mixed |
| 10 | Juhl, Velazquez & Latz 2000, *Limnol Oceanogr* 45:905 [10.4319/lo.2000.45.4.0905](https://doi.org/10.4319/lo.2000.45.4.0905) | *L. polyedrum* | Lab, Couette + shaken flasks | τ = 0.004 Pa, 1 h/day for 5-8 d | Bigger growth cut when flow was given in the last hour of dark, under low light, and in late-exponential cultures (abstract) | Yes; timing and state matter |
| 11 | Juhl & Latz 2002, *J Phycol* [10.1046/j.1529-8817.2002.00165.x](https://doi.org/10.1046/j.1529-8817.2002.00165.x) | *L. polyedrum* | Lab, 0.5 mL to Couette | τ = 0.004-0.019 Pa | Low shear, early exponential: fewer divisions, no deaths; late exponential or higher τ: mortality (abstract) | Yes |
| 12 | Latz et al. 2009, *Limnol Oceanogr* [10.4319/lo.2009.54.4.1243](https://doi.org/10.4319/lo.2009.54.4.1243) | *L. polyedrum* | Lab, oscillating Couette | Unsteady, mean \|γ\| 4 s⁻¹, 5-120 min | Unsteady flow was more inhibitory than steady flow at 4 and 8 s⁻¹; inhibition rose with duration (abstract) | Yes |
| 13 | Havskum & Hansen 2006, *Aquat Microb Ecol* 42:55 [10.3354/ame042055](https://doi.org/10.3354/ame042055) | *Heterocapsa triquetra* | Lab, 10 d | ε 10⁻⁸-10⁻⁴ | μ ≈ 0.42 d⁻¹ at all levels while pH < 8.9; at high density the most turbulent cultures grew **faster** because CO₂ exchange kept pH lower (abstract) | No (helps) |
| 14 | Strohm et al. 2024, *Harmful Algae* [10.1016/j.hal.2024.102666](https://doi.org/10.1016/j.hal.2024.102666) | *Dinophysis acuminata*, *D. ovum*, *D. caudata* | Lab cultures | ε = 10⁻² | Slower growth in 2 species, faster in *D. caudata*; more intracellular toxin (*D. acuminata*), toxin leakage (*D. ovum*) (abstract) | Mixed; toxin risk |
| 15 | Peters & Marrasé 2000, *Mar Ecol Prog Ser* 205:291 [10.3354/meps205291](https://doi.org/10.3354/meps205291) | Many (review) | Review of lab data | Many | Growth is "in general, negatively affected"; the data are biased toward dinoflagellates, and many ε values are far above ocean levels (abstract) | Context |
| 16 | Arin et al. 2002, *Aquat Microb Ecol* 29:51 [10.3354/ame029051](https://doi.org/10.3354/ame029051) | Natural coastal plankton | 15 L microcosms, oscillating grids | ε = 5.5 × 10⁻⁶, 8 d | Turbulence raised the **diatom** share and mean cell size when nutrients were added (abstract) | Diatoms helped |
| 17 | Peters et al. 2006, *J Mar Syst* 61:134 [10.1016/j.jmarsys.2005.11.012](https://doi.org/10.1016/j.jmarsys.2005.11.012) | *Thalassiosira pseudonana*, *Coscinodiscus* sp. | Lab, P-limited | Still vs turbulent | Turbulence enhanced large *Coscinodiscus*; *T. pseudonana* slightly lower (search-result summary of abstract) | Size-dependent |
| 18 | Liu et al. 2024, *Front Mar Sci* 11 [10.3389/fmars.2024.1400798](https://doi.org/10.3389/fmars.2024.1400798) | *T. pseudonana*, *Skeletonema costatum*, *Phaeodactylum tricornutum* | Lab, orbital shaker 0-180 rpm, 11 d | ε ≈ 10⁻⁷-10⁻⁴ | *T. pseudonana* final density 33.5 → 46-58 × 10⁵ mL⁻¹ (up); *Skeletonema* up, but inhibited at 180 rpm after day 7; *Phaeodactylum* ~no difference (full text) | Diatoms helped or unaffected |
| 19 | Sobczuk et al. 2006, *Bioprocess Biosyst Eng* [10.1007/s00449-005-0030-3](https://doi.org/10.1007/s00449-005-0030-3) | *Phaeodactylum tricornutum*, *Porphyridium* | Aerated stirred photobioreactor | Impeller tip speed | *P. tricornutum* damaged above 1.56 m/s tip speed; damage came from **small bubbles bursting at the surface**, not agitation itself; Pluronic F68 protects (abstract) | Harm only at high energy |
| 20 | Barbosa et al. 2003, *Biotechnol Bioeng* [10.1002/bit.10657](https://doi.org/10.1002/bit.10657) | *Dunaliella*, *Chlamydomonas* | Bubble columns | Superficial gas velocity to 0.085 m/s | No damage to walled cells up to 0.076-0.085 m/s; wall-less mutant death 0.46-1.01 h⁻¹; death linked to **gas entrance velocity at the sparger** (abstract) | Rising bubbles harmless |
| 21 | Hu et al. 2007, *Biotechnol Prog* [10.1021/bp070306a](https://doi.org/10.1021/bp070306a) | *Crypthecodinium cohnii* (dinoflagellate) | Microfluidic contraction + bubbles | Energy dissipation per volume | Flagella lost at 1.6 × 10⁷ W m⁻³; no lysis up to 5.8 × 10⁷ W m⁻³ (abstract) | Sublethal damage first |
| 22 | Michels et al. 2010, *Bioprocess Biosyst Eng* [10.1007/s00449-010-0415-9](https://doi.org/10.1007/s00449-010-0415-9) | *Chaetoceros muelleri* (diatom) | Rheometer, laminar shear | τ ramp; minutes | Viability threshold τ = 1-1.3 Pa, then viability drops to 52-66%; effect within 1 min (abstract) | Diatom lethal threshold |
| 23 | Huang et al. 2022, *Sci Total Environ* [10.1016/j.scitotenv.2022.157400](https://doi.org/10.1016/j.scitotenv.2022.157400) | Spring dinoflagellate bloom | Field, stratified reservoir, water-lifting aerators | Seasonal operation | Dinoflagellates −95.5 to −97.1%; chl-a < 10 µg/L; shift to diatoms; thresholds: Zmix 11.5 m, Zeu/Zmix 0.17 (abstract) | Yes (by light limitation, not shear) |
| 24 | Visser et al. 2016, *Aquat Ecol* [10.1007/s10452-015-9537-0](https://doi.org/10.1007/s10452-015-9537-0) | Cyanobacteria (review) | Lakes and reservoirs | Bubble plumes | Works only if mixing entrains cells, is deep enough to limit light, and is spread across the lake; chl-a per m² often rises (abstract) | Conditional |
| 25 | Pacheco & Lima Neto 2017, *J Environ Eng* [10.1061/(ASCE)EE.1943-7870.0001289](https://doi.org/10.1061/(ASCE)EE.1943-7870.0001289) | Cyanobacteria (40-80 µg/L chl-a) | Field, shallow lake, bubble plumes | Plume ε | First-order decay of chl-a inside plumes; rate scales with ε; pheophytin rose, so cells died (abstract) | Yes, locally |
| 26 | Chaffin et al. 2024, *J Environ Manage* [10.1016/j.jenvman.2024.123406](https://doi.org/10.1016/j.jenvman.2024.123406) | *Planktothrix* bloom | 2,000 L mesocosm + embayment | O₂ nanobubbles vs ozone nanobubbles | Ozone −98-99% chl-a; **oxygen-only nanobubbles: no effect**; embayment trial no effect (abstract) | Bubbles alone: no |
| 27 | Arnott et al. 2021, *Hydrobiologia* [10.1007/s10750-020-04487-5](https://doi.org/10.1007/s10750-020-04487-5) | Review of turbulence methods | Lab setups | - | Report ε; most lab cosms are too small for large eddies; acrylic can leach toxins under UV (abstract) | Methods |

## 3. Per-source detail

Each source gives its hypothesis (H), method (M), results (R), explanation (E), environmental side effects (Env) and what we take (Take).

**#1 Sung & Gobler 2026.**
- **H:** physical aeration can cut *M. polykrikoides* growth and toxicity.
- **M:** orbital shaking, nanobubbles ± ozone and macrobubbles, on cultures (GSe medium, salinity ~32, 21 °C, 12:12 light) and on NY bloom water, plus fish bioassays.
- **R:** see table; higher macrobubble flow gave stronger inhibition (paper page, per `01_BUBBLES.md`).
- **E:** physical stress; lower photosynthetic efficiency.
- **Env:** community shift toward *Prorocentrum cordatum*.
- **Take:** the one direct bench test on a local HAB species. It supports macro > nano and airflow as the dose. Our flows can't be compared with theirs until the numbers are seen.

**#2-#4 Thomas & Gibson (1990; 1995) and Thomas, Vernet & Gibson (1995).**
- **H:** small-scale shear inhibits a red-tide dinoflagellate.
- **M:** Couette cylinders (constant shear) and rotating bottles.
- **R:**
  - Zero growth at about 8 s⁻¹ continuous; no effect below 2 s⁻¹.
  - With intermittent shear of about 9 s⁻¹, 15 min to 2.5 h per day already gave negative growth. 5 min per day did nothing.
  - Photosynthesis was not the target: photosynthesis per cell rose.
- **E:** the lesion is in division, not photosynthesis. Short daily pulses are enough.
- **Take:** the strongest evidence that a **pulsed** schedule can work. The minimum useful pulse is somewhere above 5 min per day. Photosynthesis readings (Fv/Fm) may not show the effect, so count cells.

**#5 Berdalet 1992.**
- **H:** agitation disturbs dinoflagellate division.
- **M:** orbital shaker at 100 rpm, *A. sanguinea*.
- **R:** division blocked, cells bigger, 10× DNA and RNA per cell. After a 10-day shake, division resumed at once at about 2/3 of the normal rate. More than 20 days → total death.
- **E:** microtubules (mitotic spindle) are disturbed.
- **Take:** expect **rebound** after OFF. A kill needs weeks, so the loop's COOL-DOWN must watch for regrowth.

**#6 Berdalet et al. 2007.**
- **H:** the response is species-specific under an identical design.
- **M:** shaker at 100 rpm (ε ≈ 2 × 10⁻⁴ m² s⁻³).
- **R:** −33% (*A. minutum*) and −28% (*P. triestinum*); the small *Gymnodinium* was unaffected. Larger cells, more DNA per cell, half the swimming speed. Full recovery in still water.
- **Take:** our expected effect size is **~30% lower net growth** in a sensitive species. Cell volume (ocular micrometer) is a cheap mechanism marker.

**#7 Llaveria et al. 2009.**
- **H:** lower growth is caused by cell-cycle arrest or by death, depending on exposure time.
- **M:** microscopy plus Coulter counts of broken cells and thecae.
- **R:** immediate G2/M arrest with no deaths; deaths and swollen cells after more than 4 days.
- **E:** possible programmed cell death under prolonged stress.
- **Take:** `X` = 48 h tests *suppression*. `MAX_ON` = 192 h reaches the > 4 d mortality window.

**#8 Bolli et al. 2007.**
- **H:** two ε levels change growth, toxins and cysts in *Alexandrium*.
- **R:** only the high ε (2.7 × 10⁻³, orbital shaker) had an effect: 55% fewer final cells in *A. minutum*. Temporary cysts were suppressed and recovered after shaking stopped. The low ε (4 × 10⁻⁵) did nothing.
- **Take:** there is an **ε threshold** between 10⁻⁵ and 10⁻³ m² s⁻³. Our columns must be above it (see §7).

**#9 Sullivan & Swift 2003.**
- **H:** tests the "turbulence harms dinoflagellates" paradigm on 10 species.
- **M:** 20 L tanks with oscillating rods; ε measured by acoustic Doppler velocimeter.
- **R:** only 1 of 10 species was clearly slowed; 3 grew faster.
- **Take:** **screen the species in the pilot**, because the paradigm is not general. This is the main risk to the method.

**#10-#12 Juhl, Latz and colleagues (2000, 2002, 2009).**
- **H:** how growth conditions and flow type set shear inhibition in *L. polyedrum*.
- **M:** Couette flow at τ 0.004-0.019 Pa (γ ≈ 4-19 s⁻¹ [our calc, μ ≈ 10⁻³ Pa s]), 1 h/day; oscillating flow.
- **R:**
  - Flow in the late dark phase, under low light and on late-exponential cultures inhibits most.
  - Low shear cuts division; higher shear or older cultures also kill.
  - Unsteady flow beats steady flow at the same mean.
- **E:** mechanosensing tied to the cell cycle (division happens around dawn in many dinoflagellates).
- **Take:**
  - Treating a **dense, late-exponential** culture (what a forecast trigger catches) should work better than treating a young one.
  - A bubble plume is naturally unsteady, which helps.
  - Optional test: bubbling in the dark phase against the light phase.

**#13 Havskum & Hansen 2006.**
- **H:** does turbulence change *H. triquetra* growth directly or through pH?
- **R:** no direct effect. At high density, turbulence kept pH lower through CO₂ exchange, which *helped* growth.
- **Env/Take:** bubbling **strips CO₂ limitation and holds pH down**, which may boost algae and confound a still control whose pH climbs above 9. Log pH in every column; the still control's pH is part of the comparison.

**#14 Strohm et al. 2024 (Gobler co-author).**
- **R:** high ε (10⁻²) slowed 2 *Dinophysis* species, sped up the third, raised toxin per cell and caused toxin leakage.
- **Take:** with toxic species, stress can raise toxin release. We use non-toxic cultures, but "less biomass" ≠ "less toxin" must be written as a limit.

**#15 Peters & Marrasé 2000; #27 Arnott et al. 2021 (reviews).**
- **R:** growth mostly negative under lab turbulence, but lab ε values are often above ocean values. Small setups miss large eddies. Acrylic can leach compounds under UV.
- **Take:** report ε, not rpm. Use glass or PET columns and keep them out of UV.

**#16-#18 Diatoms (Arin 2002; Peters 2006; Liu 2024).**
- **H:** turbulence changes diatom growth through nutrient transport.
- **R:**
  - Turbulence raised the diatom share in nutrient-rich microcosms.
  - It helped a large diatom but not the small *T. pseudonana* under phosphorus limitation (Peters).
  - It *raised* *T. pseudonana* under replete medium (Liu).
  - *Phaeodactylum* showed no response from 0 to 180 rpm.
- **E:** a thinner diffusion boundary layer gives faster nutrient uptake; silica walls resist shear.
- **Take:** predict **no inhibition or stimulation** of the diatom arm. That makes it the specificity control. Expect the *Thalassiosira* result to depend on nutrients.

**#19-#22 Bioprocess shear limits (Sobczuk 2006; Barbosa 2003; Hu 2007; Michels 2010).**
- **H:** what hydrodynamic dose kills microalgae in bubbled or stirred reactors?
- **R:**
  - Rising bubbles are harmless up to 0.08 m/s superficial velocity.
  - Death comes from bubble formation at the sparger (Barbosa) or small bubbles bursting at the surface (Sobczuk, *Phaeodactylum*).
  - Diatom viability drops above τ ≈ 1 Pa (Michels).
  - A dinoflagellate loses flagella at 1.6 × 10⁷ W m⁻³, far above any aquarium pump.
- **Take:** these set our **safety ceiling** (§7). An aquarium pump cannot reach lethal shear. A fine airstone makes more small bursting bubbles, so a fine-versus-coarse arm tests the surface-bursting route.

**#23 Huang et al. 2022.**
- **H:** artificial mixing controls a spring dinoflagellate bloom.
- **R:** 95-97% dinoflagellate removal and a shift to diatoms, driven by cooler surface water, lower Zeu/Zmix and a deeper mixed layer.
- **Env:** community shift.
- **Take:** in the field the mechanism is **light and mixing depth**, which a 1 m column can't reproduce. Our bench tests only the small-scale shear route.

**#24-#26 Lake and reservoir mixing, nanobubbles (Visser 2016; Pacheco & Lima Neto 2017; Chaffin 2024).**
- **R:**
  - Mixing succeeds only under strict conditions.
  - Chlorophyll decays first-order inside bubble plumes, at a rate set by ε, with pheophytin rising (cells dying).
  - Oxygen nanobubbles without ozone did nothing.
- **Take:**
  - Fit a first-order decay constant `k` (d⁻¹) to each column's chlorophyll. That is our effect-size unit.
  - Coarse bubbles, not "oxygen", are the active ingredient.

## 4. Aggregated data

### 4a. Pooled effect sizes against dose and duration (dinoflagellates)

| Source | Species | Dose (ε, m² s⁻³, or γ / τ) | Exposure | Effect on growth |
|---|---|---|---|---|
| Thomas & Gibson 1990 | *L. polyedra* | γ < 2 s⁻¹ / ≈ 8 / > 8 | continuous, days | none / zero growth / negative |
| Gibson & Thomas 1995 | *L. polyedra* | γ ≈ 9 s⁻¹ | 5 min/d; 15 min-2.5 h/d | none; negative |
| Juhl et al. 2000; Juhl & Latz 2002 | *L. polyedrum* | τ 0.004-0.019 Pa (γ ≈ 4-19 s⁻¹) | 1 h/d, 5-8 d | reduced; deaths in older cultures |
| Berdalet 2007 | *A. minutum*, *P. triestinum* | ε ≈ 2 × 10⁻⁴ | exponential phase, days | −33%, −28% net growth |
| Bolli 2007 | *A. minutum*; *A. catenella* | ε 2.7 × 10⁻³ (4 × 10⁻⁵ no effect) | > 4 d | μ 0.25 → 0.19 d⁻¹ (−24%), final cells −55%; −23% final cells |
| Berdalet 1992 | *A. sanguinea* | shaker 100 rpm | 10 d; > 20 d | division stopped; total death |
| Llaveria 2009 | *A. minutum* | shaker (as Berdalet 2007) | hours; > 4 d | G2/M arrest; mortality |
| Sullivan & Swift 2003 | 10 species | ε ≈ 10⁻⁴ | days | 1 down, 2 flat, 4 unaffected, 3 up |
| Strohm 2024 | 3 *Dinophysis* | ε = 10⁻² | days | 2 down, 1 up |
| Havskum & Hansen 2006 | *H. triquetra* | ε 10⁻⁸-10⁻⁴ | 10 d | none directly; up via pH |
| Sung & Gobler 2026 | *M. polykrikoides* | macrobubbles, flow n/a | n/a | density > 60% lower |

**Diatoms:**

| Source | Species | Dose | Effect |
|---|---|---|---|
| Liu 2024 | *T. pseudonana* | ε ~10⁻⁷-10⁻⁴, 11 d | final density +39% to +72% [our calc from reported densities] |
| Liu 2024 | *P. tricornutum* | same | ~no difference |
| Liu 2024 | *S. costatum* | 60-180 rpm | +12% to +35% [our calc]; inhibited at 180 rpm after day 7 |
| Peters 2006 | *T. pseudonana* (P-limited) | turbulent vs still | slightly lower |
| Michels 2010 | *C. muelleri* | τ > 1-1.3 Pa | viability 52-66% |
| Sobczuk 2006 | *P. tricornutum* | tip speed > 1.56 m/s + bubbles | biomass falls (bubble bursting) |

### 4b. Ranges
- **Dinoflagellate growth reduction, sensitive species:** −23% to −55% in final cells or net growth over days, and > 60% in the one bubble study. Several species show 0% or growth.
- **Dinoflagellate onset:** division arrest within hours; mortality after > 4 d (Llaveria), total death after > 20 d (Berdalet 1992).
- **Recovery:** immediate, at about 2/3 of the normal rate (Berdalet 1992), with full recovery of cell properties (Berdalet 2007).
- **Threshold dose:** γ ≈ 2-8 s⁻¹ continuous (*L. polyedra*); ε between 4 × 10⁻⁵ (no effect) and 2 × 10⁻⁴ to 2.7 × 10⁻³ (effect) m² s⁻³.
- **Pulses:** 15 min per day can be enough; 5 min per day is not.
- **Diatom harm threshold:** τ ≈ 1 Pa, i.e. γ ≈ 1,000 s⁻¹ [our calc], which is 100× above the dinoflagellate threshold. This gap is the whole basis of "selective" bubbling.

### 4c. Where results conflict, and why
1. ***Lingulodinium* is slowed** in Couette and shaken flasks (#2, #10-12) but **sped up** in 20 L rod-stirred tanks (#9). Likely reasons:
   - laminar shear against 3-D turbulence;
   - ε in #9 (10⁻⁴) may be below the Couette-equivalent dose;
   - strain and growth phase differ (#10 shows late-exponential cells are far more sensitive);
   - shaken flasks add an air-water interface.
2. **Orbital shakers against grids or tanks:** shaker studies (#5-8) give strong effects; tank studies (#9, #13) give weak or positive effects. Shakers create sloshing and a moving meniscus, which is closer to bubbling than grid turbulence is.
3. **Diatoms under turbulence:** helped (#16, #18) or slightly hurt (#17). The difference depends on nutrient status (phosphorus-limited in #17) and cell size.
4. **Lab against field:** field successes (#23, #25) work mainly through light limitation, destratification and cell death in plumes. Lab successes work through arrested division. Neither transfers directly to the other.
5. **Pure-oxygen nanobubbles do nothing** (#26, and < 20% in #1). Bubble size and turbulence matter, not the oxygen itself.

## 5. Hypotheses for our experiment

All are measured against a **still control** (same column, same light, no air) with n = 3 columns per
arm. Each is falsifiable with the stated measurement.

| # | Hypothesis | Measurement | Expected direction | Grounded in |
|---|---|---|---|---|
| H1 | 48 h of coarse bubbling at 2 L/min lowers the dinoflagellate's net growth rate compared with still | Cell counts (Sedgwick-Rafter) at 0, 24, 48 h; μ = ln(N₄₈/N₀)/2 d | μ(bubbled) ≤ 0.7 × μ(still) (≥ 30% lower) | #1, #6, #8 |
| H2 | Dose-response: 2 L/min inhibits more than 0.5 L/min | μ and chl first-order `k` at both flows | μ(2) < μ(0.5) < μ(still) | #1, #2, #8 |
| H3 | The diatom (*Phaeodactylum*) is **not** inhibited by the same bubbling | Cell counts and chl, 48 h | μ(bubbled) ≥ 0.9 × μ(still); *Thalassiosira*, if used, ≥ still | #18, #16, #22 |
| H4 | At 48 h the effect is arrest, not death | % broken cells (microscope; optional Evans Blue); mean cell length (ocular micrometer) | Broken cells within 10 points of still; cell size larger in bubbled | #5, #6, #7 |
| H5 | Growth rebounds within 48 h of switching OFF | μ in the 48 h after OFF compared with still | μ(post-OFF) > 0, and ≥ 0.5 × μ(still) | #5, #6 |
| H6 | Continuous ON for > 4 d causes net decline (only if `MAX_ON` is reached) | Cell counts on days 4-8 | μ < 0 after day 4 | #7, #8 |
| H7 | Bubbling holds pH lower than still at high density | pH probe, daily | pH(still) − pH(bubbled) ≥ 0.2 once density is high | #13 |
| H8 (optional) | Pulsed bubbling (e.g. 2 h/day in the late dark phase) gives ≥ half the continuous effect at ≤ 1/12 of the ON time | μ against ON-hours | μ(pulsed) lower than still, by ≥ 50% of the continuous effect | #3, #10 |
| H9 (optional) | A fine airstone at the same airflow inhibits the dinoflagellate differently from a coarse outlet | μ, broken-cell % | Direction open: macro > nano in #1, but small bursting bubbles damage cells in #19 | #1, #19 |

**Null outcome to pre-register:** if the chosen dinoflagellate's μ is not lower at 2 L/min in the
pilot, report it as a Sullivan & Swift-type "insensitive species" result. Do not change species
silently. Switch only through a pre-registered screening step.

## 6. Mechanisms (consolidated)

1. **Cell-cycle arrest in dinoflagellates (main bench route).** Shear or turbulence above roughly γ 2-8 s⁻¹ stops division at G2/M within hours. Cells swell and accumulate DNA, and swimming slows. The cause is thought to be disturbance of the mitotic microtubules and mechanosensing. Photosynthesis continues, so chlorophyll per cell may *rise* while cell numbers stall (#2-#7, #11).
2. **Delayed death.** After more than 4 days of stress, some cells die, possibly through programmed cell death. Older, late-exponential cells die sooner (#7, #11).
3. **Reversibility.** In calm water, division restarts at once (#5, #6), so bubbling is a brake that has to stay on or be pulsed.
4. **Intermittency.** Daily pulses of 15 min or more can match continuous shear, because inhibition is tied to cell-cycle timing (#3, #10, #12).
5. **Why diatoms don't mind.** They have rigid silica walls and no flagella, and turbulence thins their nutrient boundary layer, so it often helps them (#16, #18). They are harmed only near τ ≈ 1 Pa or by bursting micro-bubbles (#19, #22).
6. **Bubble physics.** Rising bubbles are harmless. Damage comes from bubbles forming at a fast jet and bursting at the surface (#19-#21). Coarse bubbles give bulk turbulence with fewer small bursting bubbles.
7. **Field-scale routes (not reproduced in a column).** Deep mixing limits light and cools the surface, which favours diatoms and greens over buoyant or motile taxa (#23, #24). Plumes also cause local cell death (#25).
8. **Side routes that can work *against* the method.** CO₂ stripping and pH relief help algae (#13). Sediment and nutrient resuspension happen in lakes (#24). Toxin leakage from stressed toxic cells is possible (#14).

## 7. Design numbers we adopt

**Column geometry assumed:** 1 m tall × 8 cm inner diameter ≈ 5 L.

| Item | Value | Source / reasoning |
|---|---|---|
| `X` (ON time) | **48 h** | Arrest is immediate (#7), so 48 h shows suppression within 2 division cycles; > 4 d is reserved for mortality (#7, #8) |
| `MAX_ON` | **192 h** (4 × X) | Reaches the > 4 d mortality window (#7); well below the > 20 d total-death regime (#5) |
| Airflow doses | **0.5 and 2 L/min per column** (0.1 and 0.4 L air per L water per min) | Two doses, since flow is the dose (#1) |
| Estimated ε | 0.5 L/min: U_G ≈ 1.7 × 10⁻³ m/s → ε ≈ g·U_G ≈ **1.6 × 10⁻²** m² s⁻³; 2 L/min: **6.5 × 10⁻²** [our calc; standard bubble-column power input P/V ≈ ρ g U_G, bulk average, very uneven in reality] | Both above the effective range in #6 and #8 (2 × 10⁻⁴ to 2.7 × 10⁻³) and at or above #14 (10⁻²) |
| Estimated bulk shear | γ = (ε/ν)^½ ≈ **130-250 s⁻¹**; τ ≈ **0.13-0.26 Pa** [our calc, ν = 10⁻⁶ m² s⁻¹] | Above the dinoflagellate inhibition range (γ 2-19 s⁻¹, #2, #11); below the diatom lethal τ of 1 Pa (#22) |
| Superficial gas velocity limit | Keep **< 0.02 m/s** (ours: 0.002-0.007) | No damage up to 0.076 m/s (#20); pilot-plant run clean at ≤ 0.026 m/s (#20) |
| Outlet | Open tube or wide-bore outlet (≥ 4 mm); log entrance velocity (≈ 0.7-2.7 m/s) | Death is linked to high gas entrance velocity (#20); keep it low, so any effect is turbulence, not jet damage |
| Main dinoflagellate | ***Akashiwo sanguinea*** (strong published arrest, #5), backup ***Prorocentrum triestinum*** (−28%, #6); confirm non-toxic strain status with NCMA and the sponsor | *P. micans* is only a "resistant" comparison (promoted in #1). Avoid *Alexandrium*, *Lingulodinium* (toxin producers) |
| Diatom check | ***Phaeodactylum tricornutum*** (expected insensitive, #18); optional *Thalassiosira pseudonana* (expected stimulated, #18) | Specificity control |
| Growth phase at start | Late-exponential inoculum (the state a forecast trigger catches) | More sensitive (#10, #11) |
| Controls | (a) still column, same light and temperature; (b) diatom column under identical bubbling; (c) optional fine-airstone column at the same airflow (#1, #19); (d) optional pulsed column, 2 h/day (#3, #10) | - |
| Measurements | Cell count (primary), chl fluorescence, cell size, % broken cells, pH, DO, temperature, salinity; fit first-order `k` to chl (#25) | Chlorophyll alone can mislead, because chl per cell rises under arrest (#4) |
| Safety / quality limits | Temperature > 2 °C above still → EMERGENCY OFF; evaporation > 5% → top up with fresh water (salinity 30 ± 1); pH outside 7.6-8.6; use glass or PET, not UV-exposed acrylic (#27); GFCI outlet | `00_CONTROL_LOOP.md`, #27 |
| Replication / stats | n = 3 columns per arm; mean ± 95% t-interval | `00_CONTROL_LOOP.md` |

## 8. Gaps and open questions

1. **Sung & Gobler's flow rates, vessel volume and duration are still unseen** (paywalled). We can't yet say how our 0.1-0.4 vvm compares with theirs.
2. **No retrieved study bubbles a non-toxic dinoflagellate with an aquarium pump.** All the dose data come from shakers, Couette cells or grids. Our ε estimate is a bulk average; the local ε near the plume is much higher and away from it much lower.
3. **Species choice is the largest uncertainty.** *Akashiwo*'s response was measured in one 1992 lab and a sibling study. Its response to *bubbles* (not shaking) is unknown, and some NCMA strains may differ. A pilot screen is required.
4. **The chlorophyll signal may lag cell numbers**, because arrested cells swell and keep making chlorophyll (#4, #5). This matters for the loop's OFF rule, which uses chlorophyll. Consider an OFF rule based on cell counts, or both.
5. **The pH/CO₂ confound** (#13): does the still control slow down because its pH climbs, making bubbling look *worse*? The pH log answers part of this. A CO₂-neutral stir control (magnetic stirrer at matched ε) is out of scope.
6. **Pulsed schedules** (#3, #10) are only shown in *Lingulodinium* under Couette shear, never with bubbles.
7. ***Karenia brevis*** and ***Margalefidinium*** dose-response curves under quantified turbulence were not found in this search. Only #1 covers *Margalefidinium*.
8. **Field transfer:** field successes act through light limitation and destratification (#23, #24), not shear. A 1 m column says nothing about enclosures or pens. Energy per volume in our columns is about 3 × 10⁵ to 10⁶ times the reservoir destratification rule of thumb (0.005 L/s per ML, `physical.md` #25) [our calc], which is not scalable.
9. **Toxin behaviour under bubbling** is untested for our (non-toxic) species. With toxic species, stress may raise toxin per cell or cause leakage (#14).
