# Benchmarks: LIS EWS vs Reference HAB Forecast Systems

> **Contains superseded numbers (flagged 2026-08-26).** Figures here predate a
> six-defect audit: Family B/C label bugs, full-record climatology leakage in 4
> of the locked 35 features, a threshold swept on test, and a per-station
> strategy chosen on test. Verified current numbers are in `CLAUDE.md`; see
> `notes/KEY_NUMBERS.md` for the full list and `src/archive/README.md` for which
> scripts carry which defect.

Task 3 of the August 2026 plan. Status: draft. C-HARM numbers still TBD
(need Anderson et al. 2016 full text; see Open Items).

## Why this comparison is framed in POD / FAR / CSI

These are the standard categorical verification metrics for operational
hazard forecasts (NOAA HAB-OFS, NWS severe weather). Using them makes the
LIS system directly comparable to the reference systems below and avoids
inventing a private vocabulary. Definitions: POD = TP/(TP+FN),
FAR = FP/(TP+FP), CSI = TP/(TP+FP+FN).

## Key precedent: assessable-only verification is standard practice

The NOAA Gulf of Mexico HAB Operational Forecast System skill assessment
for Texas (Kavanaugh et al. 2015, NOAA Technical Report NOS CO-OPS 080)
could assess only a small fraction of issued forecasts, because
validation required field observations that often did not exist along
sparsely monitored coastline:

- Transport direction: 9 of 187 issued forecasts assessable (4.8%)
- Transport distance: 5 of 208 assessable (2.4%)
- Respiratory irritation: 0.9-8.9% assessable depending on bloom year

Forecasts without observational evidence were recorded as "unconfirmed"
and EXCLUDED from skill statistics, not counted as wrong. The Florida
assessment (Kavanaugh et al. 2013) similarly ranged 10-54% assessable.

This is the same convention as our verifiable-window FAR (ver_far):
score alerts only where a verification observation exists within the
horizon. In our test era, 41% of station-day windows contain zero
observations; the cadence-thinning experiment shows all-window FAR
degrades with sampling sparsity while verifiable-window FAR is flat
(~0.8), decomposing alert error into a cadence-driven component and a
cadence-invariant (biological) residual.

## Benchmark table

| System | Target | Lead | POD | FAR | n (assessable) | Notes |
|---|---|---|---|---|---|---|
| LIS basin alert (this work) | chl-a > 10 ug/L, western LIS | 21 d | 1.00 | 0.60 | 41 basin-days, 12 events (2023-2025) | Initiation forecast; threshold pre-registered on 2020-2022 val; rule-of-three POD lower bound ~0.75 |
| LIS station-day (this work) | same | 21 d | 0.875 | 0.875 | 956 station-days (2023-2025) | ver_far ~0.83; empty-window fraction 41% |
| NOAA GoM HAB-OFS (TX), transport direction | K. brevis bloom movement | days | 1.00 | 0.200 | 6 (of 146 issued) | BY2011-2012; tracking an already-identified bloom |
| NOAA GoM HAB-OFS (TX), high respiratory irritation | aerosol impact | 3-4 d | 1.00 | 0.043 | 22 | BY2011-2012, single large bloom year |
| NOAA Lake Erie seasonal forecast (Stumpf et al. 2012) | seasonal cyanobacteria severity index | months | n/a | n/a | 10 years | Continuous product judged on RMSE: 0.55 CI (discharge-only), 0.37 CI (blended). Benchmark for our planned seasonal severity product, not the EWS |
| C-HARM Pseudo-nitzschia model, all CA stations (Anderson et al. 2016) | P-n bloom > 10^4 cells/L | nowcast | 0.67 | 0.67 | 2014-2015, weekly pier sampling | Optimized prediction point 0.52 (POD/FAR crossover); total accuracy 43%; ROC near 1:1 line |
| C-HARM particulate DA model, Santa Cruz Wharf | pDA > 500 ng/L | nowcast | 0.68 | -- | same | Their best result: AUC 0.77 at prediction point 0.6; P-n model at same site AUC 0.33 (below random); pDA at Stearns Wharf AUC 0.04 (very few events) |

## Comparability caveats (must appear in the paper alongside the table)

1. Task difficulty differs. GoM transport and respiratory forecasts
   TRACK a bloom that has already been identified by sampling; our
   system forecasts INITIATION 21 days ahead. Tracking supports much
   lower FAR; the numbers are context, not a leaderboard.
2. Lead time differs by an order of magnitude (days vs 21 days).
3. Targets differ: chlorophyll biomass exceedance (ours) vs toxic
   species / toxin impact (GoM, C-HARM). See the biomass-vs-species
   framing issue (Vaudrey, Getchis).
4. Small n on both sides: our basin test has 12 events; the GoM
   transport assessment has n=6. Quote CIs, not point values, wherever
   possible.
5. Verification density differs: California pier monitoring is far
   denser than LIS cruise sampling, which is the subject of our
   cadence-thinning result. Notably, Anderson et al. attribute much of
   C-HARM's weak pixel-level skill to spatial/temporal mismatch between
   3-km model output and weekly pier sampling: the third reference
   system (after both NOAA GoM assessments) whose reported skill is
   limited by verification density rather than model quality.
6. Comparison context for AUC: C-HARM nowcasts score AUC 0.33-0.77
   against pier observations; the LIS system scores 0.815 (test) /
   0.852 (rolling-origin CV) at a 21-day horizon. Different target and
   region, but the LIS system operates within the skill range of the
   pre-operational state of the art while forecasting 21 days ahead
   rather than nowcasting.

## Open items

- [x] Pull C-HARM POD/FAR tables from Anderson et al. 2016 (Harmful
      Algae 59). DONE via NOAA IR open-access manuscript
      (repository.library.noaa.gov/view/noaa/33076). Values in table.
- [ ] Check the Florida HAB-OFS assessment (Kavanaugh et al. 2013,
      CO-OPS 073) for additional POD/FAR values at higher n.
- [ ] Decide table placement in paper (Discussion vs Results).

## Sources

- Kavanaugh, K.E., Derner, K., Davis, E., Urizar, C. (2015). Assessment
  of the Western Gulf of Mexico Harmful Algal Bloom Operational Forecast
  System (GOMX HAB-OFS). NOAA Technical Report NOS CO-OPS 080.
  https://tidesandcurrents.noaa.gov/publications/NOAA_Technical_Report_NOS_COOPS_080.pdf
- Stumpf, R.P., Wynne, T.T., Baker, D.B., Fahnenstiel, G.L. (2012).
  Interannual Variability of Cyanobacterial Blooms in Lake Erie.
  PLOS ONE 7(8): e42444.
- Stumpf, R.P., Johnson, L.T., Wynne, T.T., Baker, D.B. (2016).
  Forecasting annual cyanobacterial bloom biomass to inform management
  decisions in Lake Erie. J. Great Lakes Res.
- Anderson, C.R., et al. (2016). Initial skill assessment of the
  California Harmful Algae Risk Mapping (C-HARM) system. Harmful Algae.
  https://pubmed.ncbi.nlm.nih.gov/28073500/
- Kavanaugh, K.E., et al. (2013). Assessment of the Eastern Gulf of
  Mexico HAB-OFS (Florida). NOAA Technical Report NOS CO-OPS 073.