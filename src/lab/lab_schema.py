"""
lab_schema.py
-------------
The row contract for the December bench experiment (notes/LAB_PROTOCOL.md s9) and a
validator for it. One CSV row per sample:

    date, batch, vessel, arm, dose_g_L, route, T_min, measure, value, unit, counter, notes

Why this file exists before any measurement: Phase 11 (notes/SCIENTIFIC_METHOD.md) is
pre-registered, so the shape of the record, the controlled vocabularies and the
sanity checks are fixed now, while no number can be tuned to a result. Anything the
validator complains about is a transcription problem to fix at the bench, on the day,
not a modelling choice to make in January.

`validate()` never raises: it returns a list of readable complaints so a whole sheet
can be checked in one pass. `load()` reads the CSV with the dtypes the rest of
src/lab/ expects (dates stay text so a malformed date survives to be complained about).

Outputs
  (none - this module is imported by synth_lab_data.py and analyze_lab.py)

Run from repo root:
    python src/lab/lab_schema.py
"""
import re

import numpy as np
import pandas as pd

TEMPLATE = "src/lab/lab_data_template.csv"

# --- the row contract, notes/LAB_PROTOCOL.md s9 -----------------------------
COLUMNS = ["date", "batch", "vessel", "arm", "dose_g_L", "route",
           "T_min", "measure", "value", "unit", "counter", "notes"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# --- controlled vocabularies ------------------------------------------------
ARMS = ("untreated", "plain", "magnetic")
TREATED_ARMS = ("plain", "magnetic")
ROUTES = ("S", "D")                       # seawater-pasted / DI-pasted stock, s3.4
VESSELS = ("tank",) + tuple(f"jar{i}" for i in range(1, 7))
DOSES = (0.0, 0.05, 0.1, 0.2, 0.4, 0.6)   # dose ladder incl. the 0.6 g/L rerun, s8

# measure -> the one unit it may carry
MEASURES = {
    "cell_count": "cells_per_mL",
    "chl_a": "ug_per_L",
    "do": "mg_per_L",
    "ph": "pH",
    "salinity": "psu",
    "temp": "degC",
    "floc_d50": "um",
    "turbidity_750": "AU",
    "wet_mass": "g",
    "dry_mass": "g",
    "magnetite_equiv": "g",
    "icp_al": "ug_per_L",
}

# every sampling time the protocol defines (s5.3 jars, s6 tank sequence).
# -60 = the T-1 h "before" readings; 0 = t0 from the batch bottle / dosing;
# 11 floc photo, 20 and 33 counts + floor samples, 93 floor sample,
# 300 = 5 h, 1440 = 24 h (also carries the s7 workup masses).
T_MIN_SET = (-60, 0, 11, 20, 33, 93, 300, 1440)

# the s7 workup fractions, written into `notes` as fraction=<name>
FRACTIONS = ("pad", "i", "ii", "iii")

DOSE_TOL = 1e-9

FRACTION_RE = re.compile(r"fraction\s*=\s*([A-Za-z]+)")


def parse_fraction(notes) -> str:
    """The s7 workup fraction, written into `notes` as `fraction=pad` / `=i` / `=ii`
    / `=iii`. Returns '' when the row is not a workup row."""
    if notes is None or (isinstance(notes, float) and np.isnan(notes)):
        return ""
    m = FRACTION_RE.search(str(notes))
    return m.group(1) if m else ""


def load(path: str) -> pd.DataFrame:
    """Read a lab CSV with sane dtypes. Dates stay text so validate() can see them."""
    text_cols = ["date", "batch", "vessel", "arm", "route", "measure",
                 "unit", "counter", "notes"]
    df = pd.read_csv(path, dtype={c: "string" for c in text_cols})
    for c in text_cols:
        if c in df.columns:
            df[c] = df[c].fillna("").str.strip()
    for c in ["dose_g_L", "T_min", "value"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def validate(df: pd.DataFrame) -> list:
    """Return a list of readable complaints. Never raises; an empty list means clean."""
    out = []

    # --- 1. columns ---------------------------------------------------------
    have = list(df.columns)
    missing = [c for c in COLUMNS if c not in have]
    extra = [c for c in have if c not in COLUMNS]
    if missing:
        out.append(f"missing column(s): {', '.join(missing)} "
                   f"(the s9 contract is: {', '.join(COLUMNS)})")
    if extra:
        out.append(f"unexpected column(s): {', '.join(extra)} "
                   f"(the s9 contract is: {', '.join(COLUMNS)})")
    if missing:
        return out                      # nothing else can be checked reliably

    # --- 2. per-row checks --------------------------------------------------
    for i, r in df.iterrows():
        line = i + 2                    # +2: 1-based, plus the header line
        date, batch = str(r["date"]).strip(), str(r["batch"]).strip()
        vessel, arm = str(r["vessel"]).strip(), str(r["arm"]).strip()
        route, measure = str(r["route"]).strip(), str(r["measure"]).strip()
        unit, counter = str(r["unit"]).strip(), str(r["counter"]).strip()

        if not DATE_RE.match(date) or pd.isna(pd.to_datetime(date, errors="coerce")):
            out.append(f"row {line}: date {date!r} is not a real YYYY-MM-DD date")
        if not batch:
            out.append(f"row {line}: batch is blank (every row belongs to a jar batch "
                       f"or a tank run)")
        if vessel not in VESSELS:
            out.append(f"row {line}: unknown vessel {vessel!r} "
                       f"(allowed: {', '.join(VESSELS)})")
        if arm not in ARMS:
            out.append(f"row {line}: unknown arm {arm!r} (allowed: {', '.join(ARMS)})")
        if route and route not in ROUTES:
            out.append(f"row {line}: unknown route {route!r} "
                       f"(allowed: {', '.join(ROUTES)}, or blank for an untreated row)")
        if arm in TREATED_ARMS and not route:
            out.append(f"row {line}: arm {arm!r} has no stock route "
                       f"(s3.4 requires S or D on every dosed row)")

        if measure not in MEASURES:
            out.append(f"row {line}: unknown measure {measure!r} "
                       f"(allowed: {', '.join(sorted(MEASURES))})")
        elif unit != MEASURES[measure]:
            out.append(f"row {line}: measure {measure!r} carries unit {unit!r}, "
                       f"expected {MEASURES[measure]!r}")

        dose = r["dose_g_L"]
        if pd.isna(dose):
            out.append(f"row {line}: dose_g_L is blank or not a number "
                       f"(use 0.0 on untreated rows)")
        elif not any(abs(float(dose) - d) < DOSE_TOL for d in DOSES):
            out.append(f"row {line}: dose_g_L {float(dose):g} is not on the protocol "
                       f"ladder {', '.join(f'{d:g}' for d in DOSES)}")
        elif arm == "untreated" and float(dose) != 0.0:
            out.append(f"row {line}: arm 'untreated' carries dose_g_L "
                       f"{float(dose):g}, expected 0.0")

        t = r["T_min"]
        if pd.isna(t):
            out.append(f"row {line}: T_min is blank or not a number")
        elif int(t) not in T_MIN_SET:
            out.append(f"row {line}: T_min {t:g} is not a protocol sampling time "
                       f"({', '.join(str(x) for x in T_MIN_SET)})")

        v = r["value"]
        if pd.isna(v):
            out.append(f"row {line}: value is blank or not a number "
                       f"(leave the row out rather than recording a non-number)")
        elif float(v) < 0:
            out.append(f"row {line}: value {float(v):g} is negative "
                       f"({measure or 'this measure'} cannot be below zero)")

        if measure == "cell_count" and not counter:
            out.append(f"row {line}: cell_count row has no counter "
                       f"(s7 requires the counter's initials on every count)")

        frac = parse_fraction(r["notes"])
        if frac and frac not in FRACTIONS:
            out.append(f"row {line}: unknown workup fraction {frac!r} in notes "
                       f"(allowed: {', '.join(FRACTIONS)})")

    # --- 3. batch-level checks ----------------------------------------------
    # The s5.3 jar design gives every batch an untreated control jar (round 1).
    # Tank runs (s5.4) are single-arm recovery runs and are exempt.
    jar = df[df["vessel"].astype(str).str.startswith("jar")]
    for batch, g in jar.groupby(df["batch"].astype(str)):
        arms = set(g["arm"].astype(str))
        if arms & set(TREATED_ARMS) and "untreated" not in arms:
            out.append(f"batch {batch!r}: has treated jars "
                       f"({', '.join(sorted(arms & set(TREATED_ARMS)))}) but no untreated "
                       f"control row (s8 removal is control-corrected and cannot be "
                       f"computed)")

    # --- 4. duplicates ------------------------------------------------------
    # Key is (date, vessel, arm, T_min, measure). Two disambiguators the protocol
    # itself creates are added so they are not flagged: `counter` (s7 has five samples
    # deliberately read by both counters) and the workup `fraction` in notes (s7 weighs
    # pad, i, ii and iii on the same run, same measure, same clock).
    k = df[["date", "vessel", "arm", "T_min", "measure", "counter"]].astype(str)
    k["fraction"] = df["notes"].map(parse_fraction)
    dup = k.duplicated(keep=False)
    for kk, g in k[dup].groupby(list(k.columns)):
        lines = ", ".join(str(i + 2) for i in g.index)
        tail = ""
        if kk[5]:
            tail += f", same counter {kk[5]!r}"
        if kk[6]:
            tail += f", same fraction {kk[6]!r}"
        out.append(f"rows {lines}: duplicate (date, vessel, arm, T_min, measure) "
                   f"= ({kk[0]}, {kk[1]}, {kk[2]}, {kk[3]}, {kk[4]}){tail}")

    return out


def main():
    print("--- lab row contract (notes/LAB_PROTOCOL.md s9) ---")
    print("columns :", ", ".join(COLUMNS))
    print("arms    :", ", ".join(ARMS))
    print("routes  :", ", ".join(ROUTES))
    print("vessels :", ", ".join(VESSELS))
    print("doses   :", ", ".join(f"{d:g}" for d in DOSES))
    print("T_min   :", ", ".join(str(t) for t in T_MIN_SET))
    print("measures:")
    for m, u in MEASURES.items():
        print(f"    {m:<16} {u}")
    print("--- template check ---")
    try:
        tpl = load(TEMPLATE)
    except FileNotFoundError:
        print(f"  {TEMPLATE} not found")
        return
    problems = validate(tpl)
    print(f"  {TEMPLATE}: {len(tpl)} rows, {len(problems)} complaint(s)")
    for p in problems:
        print("   -", p)
    print()
    print("Reading the result:")
    print("  A clean template means the header and the two EXAMPLE rows match the s9")
    print("  contract exactly, so a sheet typed against it will validate. Every")
    print("  complaint is phrased as a thing to fix at the bench on the day the sample")
    print("  was taken - not a number to adjust in January.")


if __name__ == "__main__":
    main()
