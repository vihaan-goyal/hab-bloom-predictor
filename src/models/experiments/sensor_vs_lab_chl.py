"""
sensor_vs_lab_chl.py -- is the 2014 chlorophyll cliff in the sensor, the lab, or the water?
===========================================================================================
Prompted by CT DEEP's reply of 2026-09-22 ("same sampling procedures, analysis methods and
analytical laboratory for 30+ years"). The LIS label is built from the `Chlorophyll` column
of data/hab_features_tidal.csv, which is the in-situ CTD fluorometer reading, not DEEP's
extracted lab chlorophyll. This matches the two on the same station and date and reports,
per year, how far the sensor sits from the lab and how often each exceeds 10 ug/L.

Lab reference: CHLA, surface bottle (Depth_Code 'S'), from the UConn ERDDAP DEEP_Nutrient
dataset already on disk (data/uconn_nutrients_raw.csv). Pairs with lab < 0.5 ug/L are
dropped from the ratio (a ratio against a near-zero denominator is noise), not from the
exceedance shares.

Outputs
    data/sensor_vs_lab_chl.csv   one row per year

Run from repo root:
    python src/models/experiments/sensor_vs_lab_chl.py
"""
import numpy as np
import pandas as pd

FEATURES_CSV = "data/hab_features_tidal.csv"
LAB_CSV = "data/uconn_nutrients_raw.csv"
OUT_CSV = "data/sensor_vs_lab_chl.csv"
BLOOM = 10.0
MIN_LAB_FOR_RATIO = 0.5


def load_lab():
    d = pd.read_csv(LAB_CSV, low_memory=False)
    lab = d[(d.Parameter == "CHLA") & (d.Depth_Code == "S")].copy()
    lab["date"] = pd.to_datetime(lab.time).dt.tz_localize(None).dt.normalize()
    lab["lab"] = pd.to_numeric(lab.Result, errors="coerce")
    lab["station_name"] = lab.Station_Name.astype(str).str.strip()
    return lab.dropna(subset=["lab"])


def main():
    f = pd.read_csv(FEATURES_CSV, usecols=["station_name", "date", "Chlorophyll",
                                           "Corrected_Chlorophyll"])
    f["date"] = pd.to_datetime(f.date)
    f["station_name"] = f.station_name.astype(str)
    f["year"] = f.date.dt.year
    lab = load_lab()
    lab["year"] = lab.date.dt.year

    per_day = lab.groupby(["station_name", "date"]).lab.mean().reset_index()
    m = f.merge(per_day, on=["station_name", "date"], how="inner")
    r = m[m.lab >= MIN_LAB_FOR_RATIO]

    out = pd.DataFrame({
        "model_rows": f.groupby("year").size(),
        "sensor_share_gt10": f.groupby("year").Chlorophyll.apply(lambda s: (s > BLOOM).mean()),
        "corrected_share_gt10": f.groupby("year").Corrected_Chlorophyll.apply(
            lambda s: (s.dropna() > BLOOM).mean() if s.notna().any() else np.nan),
        "corrected_coverage": f.groupby("year").Corrected_Chlorophyll.apply(lambda s: s.notna().mean()),
        "lab_samples": lab.groupby("year").size(),
        "lab_share_gt10": lab.groupby("year").lab.apply(lambda s: (s > BLOOM).mean()),
        "pairs": r.groupby("year").size(),
        "sensor_over_lab": r.groupby("year").apply(lambda g: (g.Chlorophyll / g.lab).median(),
                                                     include_groups=False),
        "corrected_over_lab": r.groupby("year").apply(
            lambda g: (g.Corrected_Chlorophyll / g.lab).median(), include_groups=False),
    })
    out.index.name = "year"
    out.to_csv(OUT_CSV, float_format="%.3f")

    pd.set_option("display.width", 160)
    print(out.round(2).to_string())
    print(f"\nWrote {OUT_CSV}")

    def span(col, a, b):
        s = out.loc[a:b, col].dropna()
        return f"{s.min():.2f}-{s.max():.2f}"

    print("\nHow to read this")
    print(f"  Sensor / lab, 2009-2013: {span('sensor_over_lab', 2009, 2013)}   "
          f"2016-2021: {span('sensor_over_lab', 2016, 2021)}")
    print(f"  Corrected / lab, 1995-2021: {span('corrected_over_lab', 1995, 2021)}")
    print(f"  Lab share > 10, 2008-2011: {span('lab_share_gt10', 2008, 2011)}   "
          f"2012-2017: {span('lab_share_gt10', 2012, 2017)}   "
          f"2018-2021: {span('lab_share_gt10', 2018, 2021)}")
    print(f"  Sensor share > 10, 2009-2013: {span('sensor_share_gt10', 2009, 2013)}   "
          f"2014-2021: {span('sensor_share_gt10', 2014, 2021)}")
    print("  A sensor/lab ratio near 1 means the sensor agrees with the lab. The model's label")
    print("  uses the sensor, so any year the ratio sits well above 1 has inflated 'blooms'.")


if __name__ == "__main__":
    main()
