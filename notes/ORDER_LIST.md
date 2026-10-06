# Order list — bench build, design v8

Shopping worksheet for the materials in `notes/LAB_PROTOCOL.md` sections 2, 3 and 10: one row per orderable item, with the budget line it belongs to and where to go looking.
**No price in this file is a live quote.** The "Budgeted $" column is only the section 10 planning figure; every "Actual $" cell is blank on purpose — fill it in from your own browser today, because vendors, stock and shipping change.

Budget groups (section 10): **A** magnets 176 · **B** rake hardware 58 · **C** vessels 85 · **D** clay + PAC 47 · **E** electronics 85 · **F** chamber 60 · **G** GF/F 40 · **H** culture/consumables 149.

## Items

| Item | Spec | Qty | Budgeted $ | Where to look | Actual $ | Notes |
|---|---|---|---|---|---|---|
| N52 block magnets | 40 x 20 x 10 mm, nickel-plated, axially magnetised through the 10 mm | 22 | A: 176 total (~8 ea) | Magnet houses: K&J Magnetics (kjmagnetics.com), Applied Magnets / magnet4less.com, CMS Magnetics, Apex Magnets | | **Quote this first** — swing item. 20 in stacks + 1 pull test + 1 settling. Ask about bulk price at 22 and shipping surcharge. |
| Square acrylic tube | 1-1/4 in square, 1/8 in wall, ~4 ft | 1 | B: 58 group | Plastics distributors: US Plastic Corp (usplastic.com), TAP Plastics, McMaster-Carr (mcmaster.com), Delvie's Plastics | | Cut to 5 tube lengths + end caps. |
| Nylon rod | 8 mm (or 5/16 in) diameter, ~1 m | 1 | B: 58 group | McMaster-Carr, US Plastic Corp | | Through removable top cap into nylon end-block. |
| Wooden end rails, skids, handles | Hardwood strip for slotted rails at 33 mm centres; 3 mm skid stock; 2 handles; wood screws | 1 set | B: 58 group | Home Depot, Lowe's, local lumber yard; Rockler for hardwood strip | | Screwed, not glued. Add PTFE plumber's tape (hardware store) here. |
| Release tray | ~30 x 25 cm shallow plastic/stainless tray + wash bottle | 1 | B: 58 group | Restaurant supply (WebstaurantStore), US Plastic Corp, Home Depot (boot tray); wash bottle from Flinn Scientific or Carolina Biological | | |
| Aquarium | 10 gal glass, standard 50 x 25 cm footprint | 1 | C: 85 group | Aquarium retailers: Petco, PetSmart, local fish store; Amazon | | Petco/PetSmart run dollar-per-gallon sales — check before paying list. |
| Jars | 2 L glass, wide mouth, straight sided | 6 | C: 85 group | Ball / Anchor Hocking half-gallon jars at Walmart, Target, ACE; lab-grade from Carolina Biological or Qorpak | | **Borrow candidate** — ask the chem teacher for 6 matching beakers/jars first. |
| Carboys | 20 L (5 gal) HDPE or glass, with cap | 2 | C: 85 group | Homebrew suppliers: Northern Brewer (northernbrewer.com), MoreBeer, Adventures in Homebrewing; US Plastic Corp | | Must autoclave/pasteurise-tolerant for f/2. |
| Filter bag | 5 um felt/polyester, standard ring top | 1-2 | C: 85 group | Homebrew and pool suppliers: Northern Brewer, Duda Diesel, US Plastic Corp, McMaster-Carr | | Gravity filtration of seawater diluent. |
| Sample bottles | 125-250 mL HDPE, wide mouth, with caps | ~24 | C: 85 group | Fisher Scientific, Cole-Parmer, US Plastic Corp, Qorpak | | Separate from the trace-metal bottles below. |
| Magnetite pigment | Black iron oxide (Fe3O4) powder, 1 lb | 1 | D: 47 group | Ceramics suppliers: Sheffield Pottery (sheffield-pottery.com), The Ceramic Shop, Axner, Laguna Clay. Pigment houses: The Earth Pigments Company, Kremer Pigmente | | Confirm it is magnetite (Fe3O4), not hematite (Fe2O3) — a magnet on the bag settles it. |
| EPK kaolin | Edgar Plastic Kaolin, 5 lb | 1 | D: 47 group | Sheffield Pottery, The Ceramic Shop, Axner, Big Ceramic Store, Laguna Clay | | Cheapest item to over-buy; 5 lb is plenty. |
| PAC powder | Polyaluminium chloride, 28-30% Al2O3, 1 kg | 1 | D: 47 group | Pool/water-treatment suppliers: Duda Diesel (dudadiesel.com), ChemWorld, Pool supply houses (Leslie's — ask for PAC clarifier, powder not liquid); lab grade from Sigma-Aldrich | | **Get the COA or spec sheet for %Al2O3** — the 28-30% assumption sets the dose. |
| ESP32 dev board | Any ESP32-WROOM-32 dev kit, USB | 1 | E: 85 group | Adafruit, SparkFun, DigiKey, Mouser, Amazon | | |
| Relay module | 2-channel, 5 V logic, opto-isolated | 1 | E: 85 group | Amazon, Adafruit, SparkFun | | Switches pump and paddle. |
| microSD card module | SPI breakout + 8-32 GB card | 1 | E: 85 group | Adafruit, SparkFun, Amazon | | Keep the card away from the magnets. |
| Peristaltic pump | 12 V DC, ~60 mL/min, silicone tubing head | 1 | E: 85 group | Adafruit, Amazon (Kamoer / Gikfun), Cole-Parmer (Masterflex, higher end) | | Note tubing ID so the siphon tubing matches. |
| Gearmotors, jar rig | 12 V DC, ~100 rpm, identical units | 3 | E: 85 group | ServoCity (servocity.com), Pololu (pololu.com), Amazon (Greartisan) | | Must be three of the same part number — G is matched across jars. |
| Gearmotor, tank paddle | 12 V DC, ~50 rpm | 1 | E: 85 group | ServoCity, Pololu, Amazon (Greartisan) | | Drives the 15 cm paddle at 48-50 rpm, G ~60. |
| Power supply | 12 V, 5 A, fused, barrel or screw terminal | 1 | E: 85 group | Mean Well via DigiKey or Mouser; Adafruit; Amazon | | **Borrow candidate** — a lab bench supply works. Behind a GFCI either way. |
| Hall sensor | DRV5055A4 (linear, ±21 mT) | 2-3 | E: 85 group | DigiKey, Mouser, Texas Instruments direct; Pololu sells a carrier board | | Buy spares; they are cents each and easy to cook. |
| Sedgewick-Rafter chamber | 1 mL, ruled, with cover glass | 1 | F: 60 | Wildco (wildco.com), Aquatic Research Instruments, Pyser Instruments, Fisher Scientific, Cole-Parmer | | **Borrow candidate #1** — ask UConn/DEEP partner before ordering (already on the Sep 22 email list). |
| GF/F filters | Whatman GF/F, 47 mm, 0.7 um nominal, box of 100 | 1 | G: 40 | Cytiva Whatman via Fisher Scientific, Cole-Parmer, Sigma-Aldrich, MilliporeSigma | | Generic borosilicate 0.7 um is acceptable if Whatman is backordered — record the brand. |
| f/2 medium | Guillard's f/2 (+Si for diatoms), enough for ~24 L | 1 | H: 149 group | NCMA at Bigelow (ncma.bigelow.org — sells media with cultures), Florida Aqua Farms (florida-aqua-farms.com, Proline f/2), Carolina Biological | | **Borrow candidate #2** — partner lab may make it up for free. **Must include silicate** for *Skeletonema*. |
| Culture LED | Cool white, ~100-150 umol/m2/s at jar face, with timer | 1 | H: 149 group | Home Depot / Lowe's LED shop light; Amazon; aquarium retailers (Petco, Bulk Reef Supply) | | **Borrow candidate #3** — a plant/aquarium light from the bio classroom. Add a mechanical outlet timer. |
| Lugol's iodine | Acid or neutral Lugol's, 100 mL | 1 | H: 149 group | Carolina Biological, Ward's Science, Flinn Scientific, Florida Aqua Farms | | Preservative for counts. Check school policy on iodine storage. |
| pH pen | ±0.1 pH, with calibration buffers | 1 | H: 149 group | Apera Instruments, Hanna Instruments (hannainst.com), Oakton via Cole-Parmer; hydroponics and pool shops | | Buy pH 4 / 7 / 10 buffer sachets with it. |
| Syringe filters | 0.45 um, 25 mm, PES or nylon, pack of 50-100 | 1 | H: 149 group | Fisher Scientific, Cole-Parmer, Restek, Sigma-Aldrich, Amazon | | For the ICP aluminium samples. |
| Trace-metal HDPE bottles | 60-125 mL, acid-cleaned / trace-metal grade | 6-8 | H: 149 group | Fisher Scientific (Nalgene), Environmental Express, Qorpak, Cole-Parmer | | Ask the ICP lab which bottle and preservative **they** want before buying. |
| Acetone | 90% or reagent grade, 500 mL - 1 L | 1 | H: 149 group | School chemistry stockroom first; Flinn Scientific, Carolina Biological; hardware-store acetone (Home Depot) diluted to 90% | | Chlorophyll extraction. Flammable — hood and teacher supervision. |
| PPE | Nitrile gloves, splash goggles, N95/P2 dust masks, lab coat or apron | 1 set | H: 149 group | ULINE, Grainger, Flinn Scientific, Home Depot | | Dust masks are for weighing PAC and magnetite in the hood. |
| Siphon tubing | 6 mm ID silicone or vinyl, ~5 m | 1 | H: 149 group | Homebrew suppliers (Northern Brewer), US Plastic Corp, hardware store | | Match ID to the peristaltic pump head. |
| Syringes | 10 mL, 50 mL, 60 mL luer, several each | ~10 | H: 149 group | Amazon, Cole-Parmer, Carolina Biological, Tractor Supply (farm/vet syringes) | | 60 mL luer must mate with the 0.45 um filters. |
| *Skeletonema marinoi* culture | NCMA **CCMP1332**, live starter culture | 1 | H: 149 group | NCMA at Bigelow Laboratory — ncma.bigelow.org | | **Order first, everything else waits on it.** See "Before you order". |
| ICP aluminium analysis (conditional) | 5 samples, dissolved Al by ICP | 5 | conditional 125-150 | Only if the partner lab cannot run it: commercial environmental labs — Eurofins, Pace Analytical, ALS, or a Connecticut lab such as Phoenix Environmental / Con-Test | | Not in the 700. Ask the partner lab (Sep 22 email) before you price this. |
| **TOTAL** | | | **700 buy everything / 533 with five borrows** | | **______** | Your sum here. Add ~125-150 if ICP goes commercial. |

## Swing items

**The magnets decide the budget.** 22 N52 blocks at the budgeted $8 each is $176 — a quarter of the whole $700. A real quote 30% either way moves the total more than any other line, so get the magnet price in writing before you commit to anything else. If the quote comes back high, options are: fewer spares (20 blocks, no settling spare), unplated blocks, or a different supplier's equivalent grade.

**The five borrows that take the total from $700 to $533** — ask the school and the partner lab for these *first*, before ordering:

| Borrow | Ask who |
|---|---|
| Sedgewick-Rafter chamber | UConn / CT DEEP partner lab (already on the Sep 22 email) |
| 2 L jars (6, matching) | School chemistry teacher — beakers or jars |
| f/2 medium | Partner lab, or school bio department |
| Culture light | School biology classroom (plant/growth light) |
| 12 V 5 A power supply | School physics/robotics bench supply |

Anything you cannot borrow, buy — but log which five you got, because that is the difference between the two totals.

## Before you order

- [ ] **Order the CCMP1332 culture first.** NCMA ships live cultures on **Wednesdays** with at least a **two-week lead**. Order date drives the entire calendar; earliest arrival is Thu Oct 8, which sets the Oct 9 gate, the Oct 23 blank gate and everything after. Get the ship date **in writing**.
- [ ] Confirm someone will be at the delivery address on the arrival Thursday — a live culture cannot sit on a porch.
- [ ] **ISEF Forms 1A, 1, 3 and 1B signed by Fri Sep 25** (Adult Sponsor; Designated Supervisor = school chemistry teacher on Forms 1 and 3), plus the signed after-hours agreement. **No hands-on work before those signatures.** Ordering and receiving materials is not hands-on work, so the culture order does not wait on the forms — but the Oct 5-9 calibrations do.
- [ ] Quote the N52 blocks before placing any other order (see Swing items).
- [ ] Get the PAC %Al2O3 spec sheet before buying — the 28-30% figure sets the blend recipe.
- [ ] Ask the ICP lab for their preferred bottle and preservative before buying trace-metal bottles.
- [ ] Check the school stockroom for acetone, Lugol's, gloves, goggles and dust masks before adding them to a cart.
- [ ] Ship-to address: confirm whether chemicals (PAC, acetone) can go to the school or must go home.
- [ ] Book the shared instruments by **Sep 22**: fume hood, water bath, spectrophotometer, 0.001 g balance, microscope, drying oven.
