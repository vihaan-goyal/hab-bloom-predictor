"""
chl_calibration.py -- put the DIY fluorometer on a µg/L scale (plan §14)
=======================================================================
Written before the real calibration, and checked on synthetic data with a known answer
(tests/test_chl_calibration.py), so the fitting rules are fixed before any real number exists.

HOW TO USE
    1. Fill in two CSV files (copy the templates in src/lab/templates/; data/ is git-ignored,
       so keep your filled copies in data/lab/):
         spectro_template.csv    one row per acetone extract: sample_id, V_filtered_mL,
                                 V_extract_mL, path_cm, A750, A664, A647, A630
         dilution_template.csv   one row per sensor reading of the dilution series:
                                 dilution_fraction (1 = undiluted culture, 0 = plain water),
                                 chl_ugL (optional: fill it to skip the stock), fl (counts as the
                                 firmware prints them, `fl=` in the `S` line or the `read` command).
                                 Repeat readings: either more rows with the same dilution, or
                                 extra columns fl_2, fl_3, ...
    2. Run from the repo root:
         python src/lab/chl_calibration.py --spectro data/lab/spectro.csv --dilution data/lab/dilution.csv
       Other options:  --stock-ugL 250 (skip the spectro file)   --stock-id A (use one extract only)
                       --tol 0.15 / --noise 5 (inner-filter rule, below)
                       --lab-scale (no ×1.28)   --demo (synthetic example)
                       --templates (write fresh templates)
    3. It prints the Chl a of each extract, the fit, the limit of detection, the top of the
       linear range and the serial commands to send to the ESP32 (hardware/buoy_esp32).

THE MATHS
    Jeffrey & Humphrey (1975), 90% acetone, absorbances corrected by A750:
        Chl a (µg/mL extract) = 11.85·(A664−A750) − 1.54·(A647−A750) − 0.08·(A630−A750)
        Chl a in culture (µg/L) = extract value × V_extract (mL) ÷ V_filtered (L) ÷ path (cm)
    Warnings: A750 > 0.005 (turbid extract: spin or re-filter it) and A664−A750 outside 0.1-0.8
    (outside the spectrophotometer's reliable range: concentrate or dilute the extract).

    Sensor fit: ordinary least squares, fl counts = intercept + slope × Chl (µg/L), on every
    reading of the levels kept. Plain water (dilution 0) is a level too, so the intercept is the
    fitted blank.

    Inner-filter rule (dense samples absorb their own blue light and glow, so the top of the
    series reads LOW): start with the blank and the two weakest dilutions. Going up one level at
    a time, fit a line to the levels kept so far and compare the next level's mean reading with
    the line. If it falls BELOW the line by more than tol (default 15%) of its predicted signal
    AND by more than 3 standard errors (the usual OLS prediction error of a mean of that many
    readings, from the repeat scatter pooled over all levels; --noise 5 sets a floor on that
    scatter, e.g. for reseating jumps), that level and every denser one are dropped. Points above the line are
    never dropped. The highest level kept is the top of the linear range; the final line is
    fitted on the kept levels only. Checked on 1000 synthetic series (8 levels, 4 repeats): it
    finds a planted roll-off at 1/4 of the stock every time, and wrongly cuts a straight line in
    about 3 runs in 1000. Always look at the printed table: the cut should sit where the
    readings visibly bend (the 2026-10-15 spinach series cuts at 1/4, as seen by eye).

    Limit of detection = 3 × SD(blank readings) ÷ slope, in µg/L (needs ≥ 2 blank readings).

FIRMWARE (hardware/buoy_esp32/buoy_esp32.ino)
    The firmware computes chl = (fl − blank) × chlk, chlk in µg/L per count. So chlk = 1 / slope.
    `blank` takes no number: it reads the head in plain water there and then. `chlk <k>` stores k.
    Both are saved in NVS; `cal` prints them. Changing `gain` means redoing both, so calibrate at
    the gain the buoy will use.
    Sonde scale (§14 step 6): the model was trained on sonde readings, and sonde ≈ 1.28 × lab
    (sonde 10 ≈ lab 7.8, fork findings §10/§32; an average across stations, state it as an
    assumption). So the buoy gets chlk_sonde = 1.28 / slope; the lab-scale chlk = 1 / slope is
    printed too, for bench work in lab units.

Run from repo root:  python src/lab/chl_calibration.py --demo
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

SONDE_PER_LAB = 1.28        # §14 step 6: sonde µg/L ≈ 1.28 × lab (extracted) µg/L
A750_MAX = 0.005            # above this the extract is turbid
A664_RANGE = (0.1, 0.8)     # reliable absorbance range for A664 − A750
TOL = 0.15                  # inner-filter rule: allowed shortfall below the line, as a fraction
MIN_LEVELS = 3              # never fit fewer levels than this (blank included)
TEMPLATE_DIR = "src/lab/templates"
SPECTRO_COLS = ["sample_id", "V_filtered_mL", "V_extract_mL", "path_cm", "A750", "A664", "A647", "A630"]


# ---------------------------------------------------------------- step 1: spectrophotometer

def jeffrey_humphrey(a750, a664, a647, a630):
    """Chl a in µg per mL of 90% acetone extract (Jeffrey & Humphrey 1975), A750-corrected."""
    return 11.85 * (a664 - a750) - 1.54 * (a647 - a750) - 0.08 * (a630 - a750)


def culture_chl(chl_extract, v_extract_ml, v_filtered_ml, path_cm=1.0):
    """µg/L in the culture from µg/mL in the extract."""
    return chl_extract * v_extract_ml / (v_filtered_ml / 1000.0) / path_cm


def spectro_table(df):
    """Adds chl_extract_ugmL, chl_culture_ugL and a warning column to the spectro readings."""
    missing = [c for c in SPECTRO_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"spectro file is missing columns: {missing}")
    out = df.copy()
    out["chl_extract_ugmL"] = jeffrey_humphrey(out.A750, out.A664, out.A647, out.A630)
    out["chl_culture_ugL"] = culture_chl(out.chl_extract_ugmL, out.V_extract_mL, out.V_filtered_mL, out.path_cm)
    warns = []
    for _, r in out.iterrows():
        w = []
        if r.A750 > A750_MAX:
            w.append(f"A750 {r.A750:.3f} > {A750_MAX}: turbid extract, spin or re-filter")
        a = r.A664 - r.A750
        if not A664_RANGE[0] <= a <= A664_RANGE[1]:
            w.append(f"A664-A750 {a:.3f} outside {A664_RANGE[0]}-{A664_RANGE[1]}: "
                     + ("filter more culture or use less solvent" if a < A664_RANGE[0] else "dilute the extract"))
        warns.append("; ".join(w))
    out["warning"] = warns
    return out


def stock_from_spectro(table, sample_id=None):
    """Stock Chl a (µg/L): one extract by id, or the mean of all extracts."""
    if sample_id is not None:
        rows = table[table.sample_id.astype(str) == str(sample_id)]
        if rows.empty:
            raise ValueError(f"no extract called {sample_id!r} in the spectro file")
    else:
        rows = table
    return float(rows.chl_culture_ugL.mean())


# ---------------------------------------------------------------- step 2: sensor dilution series

def tidy_dilution(df, stock_ugL=None):
    """Long table, one reading per row: level (µg/L), fl. Accepts fl, fl_2, fl_3 ... as repeats."""
    fl_cols = [c for c in df.columns if c == "fl" or c.startswith("fl_")]
    if not fl_cols:
        raise ValueError("dilution file needs an `fl` column (counts)")
    d = df.copy()
    if "chl_ugL" not in d.columns:
        d["chl_ugL"] = np.nan
    need = d.chl_ugL.isna()
    if need.any():
        if stock_ugL is None:
            raise ValueError("some rows have no chl_ugL: give the stock (spectro file or --stock-ugL)")
        if "dilution_fraction" not in d.columns or d.loc[need, "dilution_fraction"].isna().any():
            raise ValueError("each row needs chl_ugL or dilution_fraction")
        d.loc[need, "chl_ugL"] = d.loc[need, "dilution_fraction"] * stock_ugL
    long = d.melt(id_vars=["chl_ugL"], value_vars=fl_cols, value_name="counts").dropna(subset=["counts"])
    long = long.rename(columns={"counts": "fl"})
    return long[["chl_ugL", "fl"]].astype(float).sort_values("chl_ugL").reset_index(drop=True)


def ols(x, y):
    """Straight line y = a + b x. Returns intercept, slope, R²."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (resid ** 2).sum() / ss_tot if ss_tot > 0 else float("nan")
    return float(a), float(b), float(r2)


def lod(sd_blank, slope):
    """Limit of detection in µg/L: 3 × SD of the blank ÷ slope (counts per µg/L)."""
    return 3.0 * sd_blank / slope


def scatter_sd(long):
    """Reading-to-reading scatter in counts: the SD of repeats, pooled over all levels."""
    g = long.groupby("chl_ugL").fl
    var, n = g.var(ddof=1), g.count()
    ok = n >= 2
    if not ok.any():
        return float("nan")
    return float(np.sqrt((var[ok] * (n[ok] - 1)).sum() / (n[ok] - 1).sum()))


def line_error(use, x0, m, sd):
    """Standard error of (mean of m new readings at x0) minus (the line's value there)."""
    x = use.chl_ugL.to_numpy()
    sxx = ((x - x.mean()) ** 2).sum()
    return sd * np.sqrt(1 / len(x) + (x0 - x.mean()) ** 2 / sxx + 1 / m)


def fit_calibration(long, tol=TOL, noise=None):
    """Fits the linear range (inner-filter rule in the module docstring). Returns a dict.
    noise: smallest reading scatter (counts) the rule may assume, e.g. 5 for reseating jumps."""
    blank = long[long.chl_ugL == 0].fl
    if blank.empty:
        raise ValueError("no plain-water reading (dilution_fraction 0 or chl_ugL 0): it is the blank")
    blank_mean = float(blank.mean())
    blank_sd = float(blank.std(ddof=1)) if len(blank) >= 2 else float("nan")
    levels = sorted(long.chl_ugL.unique())
    if len(levels) < MIN_LEVELS:
        raise ValueError(f"need at least {MIN_LEVELS} levels (blank included), got {len(levels)}")
    sd = scatter_sd(long)

    kept = levels[:MIN_LEVELS]                 # blank + the two weakest dilutions
    dropped = []
    for i in range(MIN_LEVELS, len(levels)):
        use = long[long.chl_ugL.isin(kept)]
        a, b, _ = ols(use.chl_ugL, use.fl)
        lev = levels[i]
        here = long[long.chl_ugL == lev].fl
        s = sd if np.isfinite(sd) else float(np.std(use.fl - (a + b * use.chl_ugL), ddof=2)) if len(use) > 2 else 0.0
        s = max(s, noise or 0.0)
        short = (a + b * lev) - here.mean()    # counts below the line
        if short > tol * b * lev and short > 3 * line_error(use, lev, len(here), s):
            dropped = levels[i:]               # inner filter only gets worse as it gets denser
            break
        kept.append(lev)
    use = long[long.chl_ugL.isin(kept)]
    a, b, r2 = ols(use.chl_ugL, use.fl)
    if b <= 0:
        raise ValueError(f"slope {b:.3g} counts per µg/L is not positive: no usable signal")
    return {"intercept": a, "slope": b, "r2": r2, "levels_used": kept, "levels_dropped": sorted(dropped),
            "n_readings": int(long.chl_ugL.isin(kept).sum()), "blank_mean": blank_mean, "blank_sd": blank_sd,
            "n_blank": int(len(blank)), "lod_ugL": lod(blank_sd, b) if np.isfinite(blank_sd) else float("nan"),
            "top_linear_ugL": kept[-1]}


def firmware_constants(fit, sonde=True):
    """chlk (µg/L per count) for the firmware's chl = (fl - blank) * chlk."""
    k_lab = 1.0 / fit["slope"]
    return {"chlk_lab": k_lab, "chlk_sonde": SONDE_PER_LAB * k_lab if sonde else None}


def firmware_commands(fit, sonde=True):
    """The serial lines to send, in order, as text."""
    k = firmware_constants(fit, sonde)
    k_use = k["chlk_sonde"] if sonde else k["chlk_lab"]
    scale = f"sonde scale (lab × {SONDE_PER_LAB})" if sonde else "lab scale"
    lines = [
        "# same gain as the calibration; head in plain water (the dilution water), seated as for the series:",
        "blank",
        f"#   it should read about {fit['blank_mean']:.1f} counts (calibration blank; fitted {fit['intercept']:.1f})",
        f"chlk {k_use:.5f}",
        f"#   {scale}: chl = (fl - blank) x {k_use:.5f}",
        "cal",
        "#   check: cal blank=... chlk=... gain=... matches the above",
    ]
    if sonde:
        lines.append(f"# lab-scale alternative (bench work only, not for the forecast): chlk {k['chlk_lab']:.5f}")
    return lines


# ---------------------------------------------------------------- templates, demo, report

def write_templates(folder=TEMPLATE_DIR):
    os.makedirs(folder, exist_ok=True)
    pd.DataFrame([["A", 50, 10, 1, 0.002, 0.402, 0.102, 0.052],
                  ["B", 50, 10, 1, 0.003, 0.396, 0.101, 0.050]], columns=SPECTRO_COLS) \
        .to_csv(os.path.join(folder, "spectro_template.csv"), index=False)
    pd.DataFrame({"dilution_fraction": [0, 1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2, 1],
                  "chl_ugL": [""] * 8,
                  "fl": [311.0, 318.5, 326.0, 341.0, 371.0, 431.0, 520.0, 590.0],
                  "fl_2": [311.6, 318.0, 326.8, 340.2, 371.9, 430.1, 519.0, 591.2]}) \
        .to_csv(os.path.join(folder, "dilution_template.csv"), index=False)
    return folder


def demo_data(seed=1):
    """Synthetic culture: stock 300 µg/L lab, 0.8 counts per µg/L, blank 310, SD 1.5, inner filter on top."""
    rng = np.random.default_rng(seed)
    spec = pd.DataFrame([["A", 50, 10, 1, 0.002, 0.132, 0.030, 0.020],
                         ["B", 50, 10, 1, 0.002, 0.130, 0.030, 0.020]], columns=SPECTRO_COLS)
    fr = np.array([0, 1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2, 1])
    true = 310 + 0.8 * fr * 300 * np.exp(-1.2 * fr)     # exp(): inner filter, mild at 1/8, big at 1
    dil = pd.DataFrame({"dilution_fraction": fr, "fl": true + rng.normal(0, 1.5, fr.size),
                        "fl_2": true + rng.normal(0, 1.5, fr.size), "fl_3": true + rng.normal(0, 1.5, fr.size)})
    return spec, dil


def report(spec_table, stock, long, fit, sonde=True):
    if spec_table is not None:
        print("Extracts (Jeffrey & Humphrey 1975, 90% acetone):")
        for _, r in spec_table.iterrows():
            print(f"  {r.sample_id}: {r.chl_extract_ugmL:.3f} µg/mL extract -> {r.chl_culture_ugL:.1f} µg/L culture"
                  + (f"   WARNING {r.warning}" if r.warning else ""))
        if len(spec_table) > 1:
            cv = spec_table.chl_culture_ugL.std(ddof=1) / spec_table.chl_culture_ugL.mean()
            print(f"  between extracts: CV {100 * cv:.1f}%")
    if stock is not None:
        print(f"Stock: {stock:.1f} µg/L (lab scale)")
    print("\nDilution series (mean counts per level):")
    for lev, g in long.groupby("chl_ugL"):
        tag = "used" if lev in fit["levels_used"] else "DROPPED (below line: inner filter)"
        print(f"  {lev:8.2f} µg/L  fl {g.fl.mean():7.1f}  (n={len(g)})  {tag}")
    print(f"\nFit: fl = {fit['intercept']:.2f} + {fit['slope']:.4f} × Chl   R² {fit['r2']:.4f}   "
          f"{fit['n_readings']} readings, {len(fit['levels_used'])} levels")
    print(f"Blank (plain water): {fit['blank_mean']:.1f} counts, SD {fit['blank_sd']:.2f} (n={fit['n_blank']})")
    if np.isfinite(fit["lod_ugL"]):
        print(f"Limit of detection (3 SD / slope): {fit['lod_ugL']:.2f} µg/L lab"
              + (f" = {fit['lod_ugL'] * SONDE_PER_LAB:.2f} µg/L sonde" if sonde else ""))
    else:
        print("Limit of detection: needs at least 2 blank readings")
    print(f"Top of linear range: {fit['top_linear_ugL']:.1f} µg/L lab"
          + (f" ({fit['top_linear_ugL'] * SONDE_PER_LAB:.1f} sonde)" if sonde else ""))
    if fit["r2"] < 0.98:
        print("  note: R² < 0.98, check seating and repeat readings before trusting chlk")
    print("\nFirmware serial commands (hardware/buoy_esp32):")
    for line in firmware_commands(fit, sonde):
        print("  " + line)


def main(a):
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # µ and ² on the Windows console
    except AttributeError:
        pass
    if a.templates:
        print("templates written to", write_templates())
        return
    if a.demo:
        spec, dil = demo_data()
    else:
        if not a.dilution:
            raise SystemExit("give --dilution (and --spectro or --stock-ugL), or --demo")
        spec = pd.read_csv(a.spectro) if a.spectro else None
        dil = pd.read_csv(a.dilution)
    table = spectro_table(spec) if spec is not None else None
    stock = a.stock_ugL if a.stock_ugL is not None else (
        stock_from_spectro(table, a.stock_id) if table is not None else None)
    long = tidy_dilution(dil, stock)
    fit = fit_calibration(long, a.tol, a.noise)
    report(table, stock, long, fit, sonde=not a.lab_scale)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fluorometer calibration from extracted chlorophyll (plan §14)")
    ap.add_argument("--spectro", help="spectrophotometer CSV (see src/lab/templates/spectro_template.csv)")
    ap.add_argument("--dilution", help="sensor dilution-series CSV (see src/lab/templates/dilution_template.csv)")
    ap.add_argument("--stock-ugL", type=float, help="stock Chl a in µg/L, instead of the spectro file")
    ap.add_argument("--stock-id", help="use one extract's sample_id as the stock (default: mean of all)")
    ap.add_argument("--tol", type=float, default=TOL, help="inner-filter shortfall allowed (default 0.15)")
    ap.add_argument("--noise", type=float, help="floor on the reading scatter (counts) the rule assumes (default: pooled repeat SD)")
    ap.add_argument("--lab-scale", action="store_true", help="print chlk on the lab scale, no ×1.28")
    ap.add_argument("--demo", action="store_true", help="run on a synthetic example")
    ap.add_argument("--templates", action="store_true", help="write blank templates to src/lab/templates/")
    main(ap.parse_args())
