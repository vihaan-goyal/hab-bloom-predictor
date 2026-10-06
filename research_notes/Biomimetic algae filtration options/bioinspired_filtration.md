# Bio-inspired (biomimetic) filtration designs and microalgae-sized particles (2-50 µm)

Method note (for the report writer): the general web-search budget for this session was exhausted after one query, so most sources were found through the Europe PMC REST API and read directly (abstracts from Europe PMC "core" records, full text where PMC or publisher pages loaded). "Verified" = I read the abstract or full text in this session. "Inferred" = my own reasoning or calculation, not stated in a source. Full texts that would not load are listed under Gaps. Particle sizes are in µm throughout.

## 1. Fish gill-raker cross-flow and vortical cross-step filtration (Sanderson lab)

### Takeaway
Every Sanderson-lab physical model was tested on particles of roughly 100 µm to 1.6 mm, never on 2-50 µm particles. The one design aimed at harmful algae (Schroeder et al. 2019) targeted *Microcystis* colonies (20-700 µm, median about 117 µm) and was tested with 106-125 µm microspheres, with slots of 6-12 mm. The mechanism is real and resists clogging, but it has only been shown on particles 2-50x larger than single microalgal cells.

### Cited Findings
- **Sanderson SL, Cheer AY, Goodrich JS, Graziano JD, Callan WT (2001), *Nature* 412:439-441, "Crossflow filtration in suspension-feeding fishes", DOI 10.1038/35086574 (verified, abstract).** CFD and video endoscopy in three distantly related species (e.g. tilapia) show that gill rakers act as a cross-flow filter. Particles are not retained on the rakers. Instead, "the high-velocity crossflow along the rakers carries particles away from the raker surfaces and transports the particles towards the oesophagus." — [Europe PMC record / DOI](https://doi.org/10.1038/35086574)
- **Cheer A, Cheung S, Hung TC, Piedrahita RH, Sanderson SL (2012), *Bull Math Biol* 74:981-1000, DOI 10.1007/s11538-011-9709-6 (verified, abstract).** CFD shows that particle retention depends on five variables: flow speed in the oral cavity, the angle at which flow meets the filter, filter dimensions, particle size and particle density. — [DOI](https://doi.org/10.1007/s11538-011-9709-6)
- **Smith JC, Sanderson SL (2007), *J Exp Biol* 210:2706-2713, DOI 10.1242/jeb.000703 (verified, abstract).** In this fish, mucus is proposed to limit water loss between the rakers. That raises cross-flow speed and the inertial lift force on particles, so mucus works as a flow controller here, not mainly as glue. — [DOI](https://doi.org/10.1242/jeb.000703)
- **Callan WT, Sanderson SL (2003), *J Exp Biol* 206:883-892, DOI 10.1242/jeb.00195 (verified, abstract).** Carp use cross-flow filtration to concentrate small food particles and expel small dense inorganic particles through the opercular slits or by spitting. — [DOI](https://doi.org/10.1242/jeb.00195)
- **Sanderson SL, Roberts E, Lineburg J, Brooks H (2016), *Nature Communications* 7:11092, "Fish mouths as engineering structures for vortical cross-step filtration", DOI 10.1038/ncomms11092 (verified, full text via PMC4820540).**
  - Models were 3D-printed in nylon (PA 2200) and covered with mesh of **140 µm pore size** and 55% open area.
  - The test particles were *Artemia* cysts of about **250 µm**.
  - Mainstream flow inside the model was 10.1 cm/s, Re at the gape was 4,200, and internal pressure was 11.5 Pa above ambient.
  - Clogging tolerance: covering 7.0% of the mesh cut particle retention by only 10.2% in cross-step models. In conventional cross-flow models, covering 2.8% cut it by 21.0%.
  - The authors note that "particles that are smaller than the pore size of the mesh could remain suspended and be transported in the vortical crossflow."

  — [PMC4820540](https://pmc.ncbi.nlm.nih.gov/articles/PMC4820540/), [DOI](https://doi.org/10.1038/ncomms11092)
- **Brooks H, Haines GE, Lin MC, Sanderson SL (2018), *PLoS One* 13:e0193874, "Physical modeling of vortical cross-step flow in the American paddlefish", DOI 10.1371/journal.pone.0193874 (verified, title and abstract opening only).** A physical model of cross-step flow in paddlefish. I did not obtain its numbers. — [DOI](https://doi.org/10.1371/journal.pone.0193874)
- **Haines GE, Sanderson SL (2017), *J Exp Biol* 220:4535-4547, DOI 10.1242/jeb.166835 (verified, title only via Europe PMC).** Combines swimming kinematics with ram suspension feeding in a model paddlefish. — [DOI](https://doi.org/10.1242/jeb.166835)
- **Schroeder A, Marshall L, Trease B, Becker A, Sanderson SL (2019), *Bioinspiration & Biomimetics* 14:056008, "Development of helical, fish-inspired cross-step filter for collecting harmful algae", DOI 10.1088/1748-3190/ab2d13 (verified, abstract plus publisher page).**
  - Innovations: helical slots, radial symmetry, and **rotation (about 0.4 rev/s) as an active anti-clogging mechanism** that carries concentrated particles to the downstream end.
  - Target: *Microcystis aeruginosa* colonies of **20-700 µm** (median about 117 µm in Lake Erie).
  - Test particles: polyethylene microspheres of **106-125 µm**.
  - Slot widths were **6-12 mm**, and the flow tunnel ran at **14 cm/s** to match paddlefish.
  - Clogging was measured by image pixel intensity over 10-minute runs at high particle loading (5 g of microspheres). "Vortices in the helical filter were effective at reducing clogging in the center of the slots."
  - The abstract reports the anti-clogging result only qualitatively and gives no capture-efficiency percentage.

  — [Publisher page](https://iopscience.iop.org/article/10.1088/1748-3190/ab2d13), [DOI](https://doi.org/10.1088/1748-3190/ab2d13)
- **Storm TJ, Nolan KE, Roberts EM, Sanderson SL (2020), *J Exp Zool A* 333:493-510, DOI 10.1002/jez.2363 (verified, abstract summary).** American shad oropharyngeal morphology fits cross-step filtration, with a groove aspect ratio of about 0.5 and Re of about 500. — [DOI](https://doi.org/10.1002/jez.2363)
- **Witkop EM, Van Wassenbergh S, Heideman PD, Sanderson SL (2023), *Bioinspiration & Biomimetics* 18:056009, "Biomimetic models of fish gill rakers as lateral displacement arrays for particle separation", DOI 10.1088/1748-3190/acea0e (verified, abstract plus publisher page).**
  - Setup: 3D-printed conical gill-raker models in a recirculating flume at 19.3 cm/s.
  - Particles were **0.94-1.64 mm** (median 1.23 mm), with raker gaps of **1.35 and 1.8 mm**.
  - Reynolds numbers: about 4,420 at the mouth, 260-350 at the slots and about 240 at the particle scale.
  - Results: 82.7 ± 4% of particles contacted the rakers and kept moving posteriorly, and 77 ± 3% exited in the posterior 22% of the model.
  - Mechanism: particles smaller than the slots "skipped over" the vortex and "bumped" along the rakers. The maximum radius of a particle that can exit is set by the distance from the dividing (stagnation) streamline to the raker. The authors compare this explicitly to the critical radius in **deterministic lateral displacement (DLD)** and sieve-based lateral displacement microfluidic devices.

  — [Publisher page](https://iopscience.iop.org/article/10.1088/1748-3190/acea0e), [DOI](https://doi.org/10.1088/1748-3190/acea0e)
- **Van Wassenbergh S, Sanderson SL (2023), *R Soc Open Sci* 10:230315, DOI 10.1098/rsos.230315 (verified, abstract).** An ANSYS Fluent CFD study with a porous-media model of the gill rakers. The vortex shape comes from the flow resistance of the porous layer, and the vortex flow shears the centre of each slot. The model is meant to "enable future design exploration of fish-inspired filters." It contains no particle-capture data. — [DOI](https://doi.org/10.1098/rsos.230315)
- **Xu Z et al. (2025), *Biosystems Engineering*, "Analysis of hydrodynamic filtration performance in a cross-step filter for drip irrigation" (verified, title only; DOI not returned).** This is an engineering follow-up for agriculture, but I did not obtain its particle sizes. — [Europe PMC search](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22cross-step%20filtration%22&format=json)

### Inferences
- **(Inferred)** Cross-step and cross-flow fish filters work because particles carry enough inertia, and get enough lift, to cross or skip streamlines, at Re in the hundreds to thousands. A **5 µm algal cell has negligible inertia** at these speeds. The Stokes number St = ρp·d²·U/(18·μ·L), with ρp = 1,050 kg/m³, U = 0.5 m/s, L = 1 mm and μ = 1e-3 Pa·s, gives:
  - d = 5 µm: St ≈ 7e-4, so the cell follows the water like a tracer;
  - d = 50 µm: St ≈ 0.07;
  - d = 275 µm (the *Artemia* cysts used in these studies): St ≈ 2.2.

  So a 5 µm cell sits roughly 3,000x lower in St than the test particles.
- **(Inferred)** Because the mechanism behaves like a lateral displacement array (Witkop 2023), its cut-off is geometric: set by where the dividing streamline lies relative to the gap. To reject 5-20 µm cells by this route, the gaps would need to be on the order of tens of µm, which means a microfluidic device with very low flow per channel. The cm-scale, high-throughput benefit of the fish design would be lost.
- **(Inferred)** In the fish designs, a fine mesh (140 µm or smaller) still does the actual retention. For 2-50 µm cells, cross-step geometry could at best act as an **anti-fouling flow arrangement around a fine mesh or membrane** (vortex scouring of the mesh), not as a separator in its own right.
- **(Inferred)** Schroeder 2019 is the closest precedent for a HAB device. It suits **colonial** cyanobacteria (*Microcystis* colonies of about 100 µm and up), not single dinoflagellate or diatom cells of 10-40 µm.

### Gaps
- I could not read the Schroeder 2019 full text, so its mesh pore size, capture efficiency and clogging numbers are missing; only qualitative results were reachable.
- No Sanderson-lab study tested particles under about 100 µm or live microalgae, as far as I found.
- The Brooks 2018 and Xu 2025 numbers were not obtained.
- I found no Sanderson-lab follow-up for microplastics, aquaculture or wastewater with performance data (a targeted web search was not possible because the search budget was exhausted).

## 2. Manta/mobula "ricochet separation" and follow-ups

### Takeaway
Ricochet separation works for particles about 200 µm and larger, at Re around 300-1,000 and flow of about 0.5 m/s. Capture falls to minimal below about 200 µm, even in the original study. Microfluidic "lobe filter" spin-offs reach 10-15 µm particles with efficiencies up to 96-99%, but only at mL/min flow rates and by relying on inertial and Dean flow at small channel scale. That is the only part of the literature that reaches the microalgae size range.

### Cited Findings
- **Divi RV, Strother JA, Paig-Tran EWM (2018), *Science Advances* 4:eaat9533, "Manta rays feed using ricochet separation, a novel nonclogging filtration mechanism", DOI 10.1126/sciadv.aat9533 (verified, full text via PMC6157963).**
  - Models were 3D-printed at 1x scale (32 µm layers) and 4x scale from *Manta birostris* measurements.
  - Pore size was **340 µm**, and the test particles were **275 µm** hydrated *Artemia* cysts.
  - Reynolds numbers: free-swimming Re about 1,075; experiments at Re 745 (dye) and 309 (particles). Efficiency rose sharply above Re of about 900. Freestream flow was about 550 mm/s.
  - Efficiency for particles smaller than the pores was **19 ± 5% (wing orientation) and 62 ± 5% (spoiler orientation)**.
  - **Particles under about 200 µm showed minimal capture.**
  - "Visual inspection revealed no clogging."
  - The process was insensitive to particle density.

  — [PMC6157963](https://pmc.ncbi.nlm.nih.gov/articles/PMC6157963/), [DOI](https://doi.org/10.1126/sciadv.aat9533), [CSUF press release](https://news.fullerton.edu/2018/09/manta-ray-research/)
- **Clark AS, San-Miguel A (2021), *Lab on a Chip* 21:3762, "A bioinspired, passive microfluidic lobe filtration system", DOI 10.1039/d1lc00449b (verified, abstract).**
  - Two microfluidic chips based on manta lobe filters, for particles of **about 10-30 µm**.
  - Efficiency rises with flow rate, which "suggest[s] that particle inertial effects play a key role."
  - Efficiencies reached **up to 99% at 20 mL/min**, and particle concentration rose 2x or more at 6-16 mL/min.
  - The design is aimed at reducing clogging for continuous, high-throughput use.

  — [DOI](https://doi.org/10.1039/d1lc00449b), [PMC8486309](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486309/)
- **Hu X, Yu L, Zhu Z, et al. (2024), *Lab on a Chip*, "A self-cleaning micro-fluidic chip bioinspired by the filtering system of manta rays", DOI 10.1039/d4lc00039k (verified, abstract).**
  - A U-shaped "gill rake" chip that combines lobe filtration with **Dean flow**.
  - Tested on monodisperse and bidisperse particle suspensions and on **yeast cells**.
  - Efficiencies were **96.08% (10 µm) and 97.14% (15 µm) at 6 mL/min**, with a maximum throughput of 8 mL/min.
  - There is a flow-rate threshold above which efficiency rises rapidly. At high flow, particles and cells settle near the outer wall and avoid the side channels, which is described as a self-cleaning mechanism.

  — [DOI](https://doi.org/10.1039/d4lc00039k)
- **Adelmann B, Schwiddessen T, Götzendorfer B, Hellmann R (2022), *Materials* 15:8454, "Evaluation of SLS 3D-printed filter structures based on bionic manta structures", DOI 10.3390/ma15238454 (verified, abstract).**
  - Lamella filters were made by selective laser sintering in PA12, based on *Mobula tarapacana* and *Manta birostris*.
  - They removed **more than 90% of sand particles** from water as flat filters and **more than 95%** as round in-pipe filters, with filtered-to-unfiltered water at about 1:1.
  - "The filter effect is based on the different dynamic flow of particles and water rather than filtering by the hole size."
  - The sand particle size was not given in the abstract (inertial separation of a dense mineral).

  — [DOI](https://doi.org/10.3390/ma15238454)
- **Mao X, Bischofberger I, Hosoi AE (2024), *PNAS* 121:e2410018121, "Permeability-selectivity trade-off for a universal leaky channel inspired by mobula filters", DOI 10.1073/pnas.2410018121 (verified, abstract and full text via Europe PMC).**
  - Defines three regimes: pore-flow, transition and vortex. They are set by mean channel velocity: pore-flow below 0.08 m/s, transition 0.08-0.7 m/s, vortex at 0.7 m/s and above.
  - Tests used pores 0.56 mm wide and polystyrene particles of **324 ± 51 µm**.
  - The cut-off particle size **falls as velocity increases**, so selectivity needs fast flow.
  - The model treats particles as tracers, and the authors say inertia, lift and lubrication forces were neglected.

  — [DOI](https://doi.org/10.1073/pnas.2410018121), [PMC11648657](https://pmc.ncbi.nlm.nih.gov/articles/PMC11648657/)
- **Kahane-Rapport SR, Teeple J, Liao JC, Paig-Tran EWM, Strother JA (2025), *Proc R Soc B* 292:20242037, "Filter feeding in devil rays is highly sensitive to morphology", DOI 10.1098/rspb.2024.2037 (verified, title and abstract opening only).** — [DOI](https://doi.org/10.1098/rspb.2024.2037)
- **Teeple JB, Kahane-Rapport SR, Cohen KE, Hamann L, Strother JA, Paig-Tran EWM (2025), *Integr Comp Biol* 65:1576-1600, "Form and function in mobulids: a comparative analysis of filter morphology with bioinspiration applications", DOI 10.1093/icb/icaf142 (verified, full text via PMC12690469).**
  - Mobulid primary pore widths range from **50 ± 20 µm** (distal lobes, *M. thurstoni*) to **800 ± 100 µm**.
  - Earlier CFD found cut-off diameters of **250-600 µm** for pores over 1,000 µm. The predicted lower limit is about 0.5 mm at a lobe angle of about 40°, and about 1.1 mm at 27°.
  - The review lists the microfluidic lobe filters (99% at 20 mL/min; 97% at 8 mL/min) and mentions applications for microplastic interception and algae removal.
  - No patents or companies are named.

  — [PMC12690469](https://pmc.ncbi.nlm.nih.gov/articles/PMC12690469/), [DOI](https://doi.org/10.1093/icb/icaf142)
- **Fastnedge T, Breward CJW, Griffiths IM (2025), arXiv:2511.05157, "A multiple-scales framework for branched channel filters" (verified, abstract; preprint, not peer-reviewed).**
  - Asymptotic theory for **manta-inspired washing-machine microfibre filters**.
  - The fraction of particles entering the side branches "depends critically on Stokes number."
  - The model assumes high-Re laminar flow.

  — [arXiv](https://arxiv.org/abs/2511.05157)
- **Sankrityayan P, Biswas S (2022), *Frontiers in Marine Science* 9:919743, DOI 10.3389/fmars.2022.919743 (verified, full text).**
  - A conceptual manta-inspired microplastic filter combined with *Ideonella sakaiensis* degradation.
  - It exists only as a SolidWorks CAD design, with **no performance data**.

  — [Frontiers](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.919743/full)

### Inferences
- **(Inferred)** In both the 3D-printed models and the PNAS leaky-channel work, ricochet and vortex separation need particle inertia (Re of about 300-1,000 or more, with large dense particles), and selectivity gets worse as particles get smaller. At cm-to-mm scale, **5 µm algae would mostly leak through with the water**. This follows from the less-than-200 µm result (Divi 2018), the Stokes-number dependence (Fastnedge 2025) and the St estimate in Section 4.
- **(Inferred)** The microfluidic lobe chips (10-15 µm at 96-99%) show the principle can be carried down to cell scale, but only by shrinking the channels to the µm scale. At 6-20 mL/min per chip, one chip processes about 9-29 L/day. Treating a tank of hundreds of litres would need parallel chips, and the narrow channels are vulnerable to debris and biofouling. These are concentrators (they split a stream into enriched and depleted fractions), not dead-end removers, so complete removal would need recirculation or cascades.
- **(Inferred)** Hu 2024 used yeast, a living cell of about 3-6 µm. It is the closest analogue to small algae found here, but the yeast-specific efficiency was not in the abstract.

### Gaps
- I could not access the Clark 2021 and Hu 2024 full texts (server errors or 403), so efficiency by particle size below 10 µm, channel Reynolds numbers and the yeast efficiency are missing.
- No study tested a manta-type filter on live microalgae.
- The particle size used by Adelmann 2022 is unknown.

## 3. Bivalve, sponge, tunicate, baleen and other suspension feeders translated into engineered filters at 1-50 µm

### Takeaway
Animals that really do capture 1-50 µm particles (mussels, sponges, tunicates, appendicularians, copepods) mostly do so at low Re (about 0.0002-50). They use mucus nets, cilia and direct interception, not inertial tricks. A 2022 review states that mucus-like adhesive filter media and many of these principles are rarely or never used in engineered solid-liquid filters. I found no engineered prototype from these organisms with measured capture of microalgae.

### Cited Findings
- **Hamann L, Blanke A (2022), *J R Soc Interface* 19:20210741, "Suspension feeders: diversity, principles of particle separation and biomimetic potential", DOI 10.1098/rsif.2021.0741 (verified, full text via Europe PMC).**
  - Size ranges retained:
    - bivalves such as *Mytilus edulis*: 1-100 µm;
    - sponges: 1-100 µm and below 1 µm;
    - ascidian mucus nets: mesh about 0.2 x 0.5 µm, retaining particles down to about 1 µm "at low resistance";
    - copepods: 1-100 µm;
    - herring and silver carp gill rakers: 1-100 µm;
    - baleen: 1-10 mm and larger.
  - Encounter mechanisms (hydrosol filtration theory): direct interception, inertial impaction, gravitational deposition, diffusion and electrostatic attraction. Retention adds sieving, mucus adhesion (used in 13 of the 35 taxa reviewed) and ciliary transport.
  - Reynolds numbers: about 0.00057 around sponge choanocytes and about 0.0002 at mussel cilia. Most suspension feeders work at Re 1-50, and mobulids go up to about 300.
  - On engineering: "mucus-like filter media that use adhesive forces to retain particles are rarely used in solid–liquid filtration technologies." Pleated or angled-mesh ideas from mussel gills and daphnid setules have not had parametric engineering studies. The only engineered spin-offs cited are manta-inspired (a nanofibrous oil-water membrane and ricochet filtration) and the Schroeder 2019 helical harmful-algae filter.
  - Whale sharks filter at about 113 Pa, against about 1 MPa for industrial systems, which points to low-pressure design.
  - The authors stress that dimensionless scaling is needed to move these mechanisms outside the organism's own size range.

  — [DOI](https://doi.org/10.1098/rsif.2021.0741), [PMC8790370](https://pmc.ncbi.nlm.nih.gov/articles/PMC8790370/)
- **Hamann L, Foat T, Blanke A (2025), *J R Soc Interface*, "The diversity of biological models for bio-inspired aerosol filters", DOI 10.1098/rsif.2025.0221 (verified, title only).** This covers aerosols (air), not water. — [DOI](https://doi.org/10.1098/rsif.2025.0221)
- **Filippov AE, Krings W, Gorb SN (2023), *Beilstein J Nanotechnol* 14:603, "Suspension feeding in Copepoda – a numerical model of setae acting in concert", DOI 10.3762/bjnano.14.50 (verified, title only).** — [DOI](https://doi.org/10.3762/bjnano.14.50)
- **Chen X, Jiang W, Wei J, et al. (2026), *Fundamental Research*, "Adaptive gyration mechanism in fan worm gill filaments for enhanced filter-feeding efficiency", DOI 10.1016/j.fmre.2026.03.009 (verified, title only).** — [DOI](https://doi.org/10.1016/j.fmre.2026.03.009)
- **Ackermann IA et al. (2026), *J Exp Biol* 229, "Constraints on lunge feeding: krill can clog the baleen of filter-feeding whales", DOI 10.1242/jeb.251852 (verified, title only).** Baleen is a mm-scale filter, and it can clog. — [DOI](https://doi.org/10.1242/jeb.251852)
- **Li H, Raza A, Yuan S, et al. (2022), *Sci Rep* 12:8178, "Biomimetic on-chip filtration enabled by direct micro-3D printing on membrane", DOI 10.1038/s41598-022-11738-z (verified, title only).** Micro-3D-printed filter structures; I did not obtain sizes. — [DOI](https://doi.org/10.1038/s41598-022-11738-z)
- **Yang Y et al. (2025), *ACS Appl Mater Interfaces*, "Fish gill-inspired bidirectional porous polysaccharide aerogels for micro/nanoplastics removal", DOI 10.1021/acsami.5c18203 (verified, title only).** This is an adsorbent material "inspired by" gills, not a hydrodynamic filter. — [DOI](https://doi.org/10.1021/acsami.5c18203)

### Inferences
- **(Inferred)** The animals that capture 2-50 µm cells operate at low Re, where capture comes from **interception and adhesion on fine, sticky or charged surfaces**, plus ciliary transport that clears the filter. The nearest engineered equivalents are not "biomimetic shapes" but **conventional fine meshes and membranes, coagulation/flocculation and adhesive or charged media**. The project's existing clay-flocculation approach is in fact the engineered analogue of mucus capture.
- **(Inferred)** Oysters and mussels are themselves sometimes proposed as living biofilters. That is biological mitigation, not a biomimetic device, and no source on it was read here.

### Gaps
- I found no peer-reviewed engineered filter based on bivalve gills, sponges or choanoflagellates with measured retention of 1-50 µm algae.
- The full texts of the copepod, fan-worm and micro-3D-printing papers were not read.

## 4. Scaling to µm particles: Reynolds number, Stokes number, inertial vs diffusional capture

### Takeaway
The non-clogging bio-inspired mechanisms (cross-flow, cross-step, ricochet) depend on inertia and vortices at Re of about 100-4,000 with particles of about 100 µm to 1 mm. For a 5 µm alga at device-scale flows, St is around 0.001. The cell follows the streamlines, so these mechanisms will not separate it unless the geometry is shrunk to microfluidic gaps (tens of µm) or the cells are first aggregated into floc of about 100 µm or larger.

### Cited Findings
- The ricochet-filtration test particles were large: efficiency jumped above Re of about 900, and particles under about 200 µm were barely captured. — [Divi et al. 2018, PMC6157963](https://pmc.ncbi.nlm.nih.gov/articles/PMC6157963/)
- The lobe-filter separation efficiency rises with flow rate, which suggests "particle inertial effects play a key role." — [Clark & San-Miguel 2021, DOI 10.1039/d1lc00449b](https://doi.org/10.1039/d1lc00449b)
- In branched-channel (manta) filters, the share of particles entering branches "depends critically on Stokes number." — [Fastnedge et al. 2025, arXiv:2511.05157](https://arxiv.org/abs/2511.05157)
- Most suspension feeders work at Re 1-50, and the µm-scale feeders such as mussels and sponges at Re of about 0.0002-0.0006. These rely on interception, diffusion, mucus and cilia rather than inertial impaction. — [Hamann & Blanke 2022](https://doi.org/10.1098/rsif.2021.0741)
- Gill-raker separation follows lateral-displacement-array physics, with a critical radius set by the dividing streamline (as in DLD microfluidics). — [Witkop et al. 2023](https://doi.org/10.1088/1748-3190/acea0e)
- In Hu 2024, inertial and Dean-flow focusing at 6-8 mL/min separated 10-15 µm particles at 96-97%. — [Hu et al. 2024](https://doi.org/10.1039/d4lc00039k)

### Inferences
- **(Inferred, calculation)** The Stokes number is St = ρp·d²·U / (18·μ·L). With ρp ≈ 1,050-1,100 kg/m³ for algal cells, μ ≈ 1e-3 Pa·s, U = 0.1-0.5 m/s and L = 1 mm (a gap or lobe size):

  | Particle | St |
  |---|---|
  | 5 µm cell | about 1.5e-4 to 7e-4 |
  | 20 µm cell | about 0.002-0.012 |
  | 50 µm cell or chain | about 0.015-0.07 |
  | 275 µm *Artemia* cyst (used in Divi 2018 and Sanderson 2016) | about 0.4-2.2 |

  Inertial ricochet needs St on the order of 0.1-1 or more. Reaching it with a 5 µm cell needs L of about 1-10 µm or U of tens of m/s, which is microfluidic territory or impractical, and high shear may lyse fragile dinoflagellates. Algae are also nearly neutrally buoyant in seawater (density contrast of a few %), which weakens density-based separation further.
- **(Inferred)** **Would ricochet or cross-step separation work on 5 µm algae in a small autonomous device? Essentially no, as a primary separator.** It could work on (a) colonial or chain-forming taxa or aggregates of about 100 µm or more (the Schroeder 2019 precedent), or (b) **cells first flocculated** (for example with clay or coagulant) into floc of 100 µm or more. In that role a cross-step or helical rotating screen could serve as a **non-clogging floc harvester**. That combination is the most plausible bio-inspired option for this project.
- **(Inferred)** At µm scale, the capture mechanisms that still work are interception on fine fibres or meshes, Brownian diffusion (only for particles under about 1 µm), sedimentation, and adhesion or electrostatics. These are conventional depth or membrane filtration mechanisms with the usual clogging problem. The bio-inspired element that transfers best is **tangential (cross-flow) flushing and vortex shear to keep a fine mesh clear**.

### Gaps
- I found no published study that explicitly tested cross-step or ricochet geometries across a particle-size sweep down to 1-10 µm at fixed macro-scale geometry, so the cut-off curve below 100 µm is inferred, not measured.
- Typical St thresholds for lobe or cross-step capture were not given numerically in the sources I read.

## 5. Patents and startups

### Takeaway
I found no verifiable patents or startups commercialising fish-gill or manta-ray filters, but the search was limited by tooling (see Gaps). The applied work I found is academic: microfluidic chips, SLS-printed lamella filters, washing-machine microfibre filter theory, drip irrigation, and one harmful-algae helical filter.

### Cited Findings
- A Europe PMC patent-source query (SRC:PAT with manta, gill raker, cross-step or ricochet, plus filter) returned **zero results**. — [Europe PMC REST query](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:PAT%20AND%20(manta%20OR%20%22gill%20raker%22%20OR%20%22cross-step%22%20OR%20%22ricochet%22)%20AND%20filter&format=json)
- The 2025 mobulid bioinspiration review names no patents or companies. — [Teeple et al. 2025, PMC12690469](https://pmc.ncbi.nlm.nih.gov/articles/PMC12690469/)
- The applied directions found are washing-machine microfibre filters (Fastnedge et al. 2025, theory only), drip-irrigation cross-step filters (Xu et al. 2025, *Biosystems Engineering*), SLS-printed manta lamella filters for sand (Adelmann et al. 2022), the harmful-algae helical filter (Schroeder et al. 2019) and microplastic concepts (Sankrityayan & Biswas 2022, CAD only). — sources as cited in Sections 1-2.

### Inferences
- **(Inferred)** Commercial activity, if there is any, is early-stage or unpublished. A judge-facing claim of "no commercial bio-inspired microalgae filter exists" should be worded as "none found in peer-reviewed literature or the Europe PMC patent index," not as a certainty.

### Gaps
- Google Patents and general web search were not available in this session (search budget exhausted), so USPTO/WIPO patents and startups (for example consumer microplastic laundry filters marketed as fish- or manta-inspired) are **not checked**. This should be redone with a patent search before any claim is made.
