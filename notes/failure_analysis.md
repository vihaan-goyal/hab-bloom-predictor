# Failure Analysis Memo

## Overview
XGBoost model evaluated on held-out 2020-2022 validation data.
- False positives: 10,232 (predicted bloom, no bloom occurred)
- False negatives: 4,904 (missed bloom events)
- FP:FN ratio of ~2:1 -- model is conservative, more likely to over-predict than miss

## Temporal Patterns
Both false positives and false negatives peak in July-August:
- FP: July 2,581 / August 3,807
- FN: July 1,391 / August 1,848

Summer is the hardest season. High temperatures and elevated background 
chlorophyll create ambiguous conditions where the model struggles to 
distinguish true bloom trajectories from seasonal elevation.

## Geographic Patterns
Top error stations are all western LIS (A4, B3, D3, C1, C2, F3):
- Station A4 leads in both FP (616) and FN (311)
- Western Narrows stations account for disproportionate share of errors

This is consistent with Perreira (2021) who showed A4 is underrepresented 
in the standard CT DEEP monitoring estimate and has the highest and most 
variable chlorophyll concentrations in the Sound.

## Hypotheses
1. Summer ambiguity: the 7-day rolling chlorophyll signal is less 
   discriminative in summer when background CHL is elevated
2. Western LIS complexity: A4 and Narrows stations experience rapid, 
   localized bloom dynamics driven by East River nutrient inputs that 
   are harder to predict from lagged features alone
3. The LSTM's temporal modeling may reduce summer errors by capturing 
   the full trajectory shape rather than just the rolling mean

## Implication for Model Development
- Consider separate summer/non-summer models or seasonal threshold adjustment
- ConvLSTM spatial model may better capture western LIS bloom dynamics
- Additional features capturing East River discharge or NYC WWTP nutrient 
  outputs could improve western station predictions