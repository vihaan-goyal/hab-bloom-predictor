"""
daily_inference.py
------------------
Scheduled script (run via cron at 6am daily) that:
  1. Fetches the last 21 days of sensor data from CT DEEP LISICOS ERDDAP
  2. Engineers features matching the trained XGBoost model
  3. Runs inference on all stations
  4. Computes aeration suitability score S for high-risk stations
  5. Writes results to data/daily_predictions.csv
  6. Sends an email alert if any station crosses intervention thresholds

Usage:
    python daily_inference.py                  # Run for today
    python daily_inference.py --date 2024-08-15  # Run for a specific date (backtesting)

Cron (every day at 6am):
    0 6 * * * /path/to/conda/envs/hab/bin/python /path/to/daily_inference.py
"""

import argparse
import smtplib
import os
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import numpy as np
import pandas as pd
import requests
import xgboost as xgb
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ERDDAP_BASE = "https://lisicos.uconn.edu/erddap/tabledap/dep_wq_data.csv"

# All 50 CT DEEP stations with their coordinates
STATIONS = {
    # Lettered stations
    "A2": (41.0830, -73.4560), "A4": (41.0170, -73.5780),
    "B3": (41.0830, -73.1830), "C1": (41.1500, -72.9170),
    "C2": (41.0830, -73.0000), "D3": (41.1170, -72.7500),
    "E1": (41.1670, -72.5500), "F2": (41.0830, -72.7330),
    "F3": (41.0178, -73.1445), "H2": (41.1000, -72.5170),
    "H4": (41.0330, -72.5670), "H6": (41.0260, -72.9135),
    "I2": (41.1375, -72.6550), "J2": (41.1170, -72.4170),
    "J4": (41.0330, -72.4170), "K2": (41.1170, -72.2670),
    "M3": (41.2372, -72.0533), "N3": (41.2833, -71.9833),
    # Numeric stations
    "01": (40.9633, -73.6237), "02": (40.9347, -73.6008),
    "03": (40.9794, -73.5606), "04": (40.9378, -73.5194),
    "05": (41.0093, -73.5136), "06": (40.9611, -73.4768),
    "07": (40.9505, -73.4255), "08": (41.0408, -73.4180),
    "09": (41.0708, -73.3362), "10": (40.9517, -73.3326),
    "12": (41.1086, -73.2530), "13": (41.0583, -73.2343),
    "14": (40.9915, -73.2188), "15": (40.9313, -73.2212),
    "16": (41.1203, -73.1625), "18": (41.1223, -73.0900),
    "19": (41.0553, -73.0808), "20": (40.9940, -73.0423),
    "21": (41.1640, -73.0148), "22": (41.0823, -73.0229),
    "23": (41.1402, -72.9488), "25": (40.9810, -72.9182),
    "26": (41.2092, -72.9085), "27": (41.1587, -72.8495),
    "28": (41.0782, -72.8335), "29": (41.2315, -72.8297),
    "30": (41.1963, -72.7750), "31": (41.0042, -72.7683),
    "32": (41.2415, -72.6657), "33": (41.0038, -72.6512),
    "34": (41.2460, -72.4683), "36": (41.2705, -72.2755),
}
# Features the XGBoost model was trained on (must match exactly)
FEATURES = [
    'latitude', 'longitude', 'month',
    'chl_anomaly', 'chl_climatology',
    'chl_roll7_mean', 'chl_roll7_std',
    'chl_lag3', 'chl_lag7', 'chl_lag14', 'chl_lag21',
]

# Full feature set used in SHAP/ablation (superset of above)
FULL_FEATURES = FEATURES + [
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'pH',
]

MODEL_PATH = "data/xgb_model.json"
CLIMATOLOGY_PATH = "data/chl_climatology.csv"  # monthly mean CHL per station
OUTPUT_PATH = "data/daily_predictions.csv"

# Alert thresholds
BLOOM_PROB_THRESHOLD = 0.70     # P(bloom) > 70% triggers alert
AERATION_SCORE_THRESHOLD = 0.60  # S > 0.6 triggers intervention flag
DO_HYPOXIA_THRESHOLD = 6.0       # mg/L — hypoxia threshold

# Email config (set in .env)
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "ctdeep.hab@ct.gov")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

LOCAL_DATA_PATH = "data/hab_features_final.csv"


# ---------------------------------------------------------------------------
# Step 1: Fetch data from LISICOS ERDDAP
# ---------------------------------------------------------------------------

def fetch_local(station: str, end_date: date, n_days: int = 21) -> pd.DataFrame:
    """
    Read the last n_days of data for a station from the local CSV
    instead of hitting ERDDAP directly.
    """
    # Load once and cache globally to avoid re-reading for every station
    global _local_df
    if '_local_df' not in globals():
        print("  Loading local data file...")
        _local_df = pd.read_csv(LOCAL_DATA_PATH, low_memory=False)
        _local_df['date'] = pd.to_datetime(_local_df['date'])

    start_ts = pd.Timestamp(end_date - timedelta(days=n_days))
    end_ts = pd.Timestamp(end_date)

    mask = (
        (_local_df['station_name'] == station) &
        (_local_df['date'] >= start_ts) &
        (_local_df['date'] <= end_ts) &
        (_local_df['depth_code'] == 'S')
    )
    subset = _local_df[mask].copy()

    # Rename columns to match what engineer_features expects
    subset = subset.rename(columns={
        'Chlorophyll': 'Chlorophyll',
        'sea_water_temperature': 'sea_water_temperature',
        'sea_water_salinity': 'sea_water_salinity',
        'oxygen_concentration_in_sea_water': 'oxygen_concentration_in_sea_water',
        'pH': 'pH',
    })

    subset = subset.groupby('date').mean(numeric_only=True).reset_index()
    return subset.sort_values('date').reset_index(drop=True)

# ---------------------------------------------------------------------------
# Step 2: Feature engineering
# ---------------------------------------------------------------------------

def load_climatology() -> pd.DataFrame:
    """
    Load the monthly chlorophyll climatology (mean CHL per station per month).
    Built once from historical data; used to compute chl_anomaly.
    """
    return pd.read_csv(CLIMATOLOGY_PATH)


def engineer_features(raw: pd.DataFrame, station: str,
                      lat: float, lon: float,
                      climatology: pd.DataFrame,
                      target_date: date) -> dict | None:
    if raw.empty:
        return None

    raw = raw.sort_values('date').copy()

    # Get the most recent reading available
    latest = raw.iloc[-1]
    month = target_date.month

    # Chlorophyll series — don't reindex to daily, just work with what we have
    chl_vals = raw['Chlorophyll'].dropna()
    if len(chl_vals) < 1:
        return None

    # Current chlorophyll = most recent reading
    chl_current = float(latest['Chlorophyll']) if not pd.isna(latest['Chlorophyll']) else float(chl_vals.iloc[-1])

    # Climatology lookup
    clim_row = climatology[
        (climatology['station_name'] == station) &
        (climatology['month'] == month)
    ]
    chl_climatology = float(clim_row['chl_mean'].values[0]) if len(clim_row) else np.nan
    chl_anomaly = chl_current - chl_climatology if not np.isnan(chl_climatology) else np.nan

    # Rolling stats — just use available readings
    chl_roll7_mean = float(chl_vals.mean())
    chl_roll7_std = float(chl_vals.std()) if len(chl_vals) > 1 else 0.0

    # Lag features — find closest reading to each lag target date
    def lag_closest(lag_days):
        target = pd.Timestamp(target_date - timedelta(days=lag_days))
        if raw.empty:
            return np.nan
        diffs = (raw['date'] - target).abs()
        closest_idx = diffs.idxmin()
        # Only use if within 7 days of the target lag
        if diffs[closest_idx].days > 7:
            return np.nan
        val = raw.loc[closest_idx, 'Chlorophyll']
        return float(val) if not pd.isna(val) else np.nan

    features = {
        'station_name': station,
        'date': target_date,
        'latitude': lat,
        'longitude': lon,
        'month': month,
        'chl_climatology': chl_climatology,
        'chl_anomaly': chl_anomaly,
        'chl_roll7_mean': chl_roll7_mean,
        'chl_roll7_std': chl_roll7_std,
        'chl_lag3':  lag_closest(3),
        'chl_lag7':  lag_closest(7),
        'chl_lag14': lag_closest(14),
        'chl_lag21': lag_closest(21),
        'sea_water_temperature': float(latest['sea_water_temperature']) if not pd.isna(latest['sea_water_temperature']) else np.nan,
        'sea_water_salinity': float(latest['sea_water_salinity']) if not pd.isna(latest.get('sea_water_salinity', np.nan)) else np.nan,
        'oxygen_concentration_in_sea_water': float(latest['oxygen_concentration_in_sea_water']) if not pd.isna(latest['oxygen_concentration_in_sea_water']) else np.nan,
        'pH': float(latest['pH']) if not pd.isna(latest['pH']) else np.nan,
    }

    # Need at least the core features to be non-NaN
    core = ['chl_roll7_mean', 'chl_climatology', 'chl_anomaly']
    if any(np.isnan(features[f]) for f in core):
        return None

    return features

# ---------------------------------------------------------------------------
# Step 3: Aeration suitability score
# ---------------------------------------------------------------------------

def aeration_score(do: float, temp: float, bloom_prob: float) -> float:
    if np.isnan(do) or do <= 0:
        return np.nan
    # DO term: 0 at DO=14, 1 at DO=2
    do_term = np.clip((14 - do) / 12, 0, 1)
    # Temp term: 0 at 10C, 1 at 30C
    t_norm = np.clip((temp - 10) / 20, 0, 1) if not np.isnan(temp) else 0.5
    S = 0.45 * do_term + 0.30 * t_norm + 0.25 * bloom_prob
    return float(np.clip(S, 0, 1))

def intervention_flag(bloom_prob: float, S: float, do: float) -> bool:
    """Returns True if all three intervention criteria are met."""
    return (
        bloom_prob > BLOOM_PROB_THRESHOLD and
        S > AERATION_SCORE_THRESHOLD and
        not np.isnan(do) and do < DO_HYPOXIA_THRESHOLD
    )


# ---------------------------------------------------------------------------
# Step 4: Send email alert
# ---------------------------------------------------------------------------

def send_alert(alerts: pd.DataFrame, run_date: date):
    """Send an HTML email alert to CT DEEP for stations flagging intervention."""
    if not ALERT_EMAIL_FROM or not SMTP_PASSWORD:
        print("[INFO] Email not configured — printing alert to console instead.")
        print(alerts.to_string())
        return

    subject = f"HAB Alert: {len(alerts)} Station(s) Flagged — {run_date}"

    rows = ""
    for _, row in alerts.iterrows():
        rows += f"""
        <tr>
            <td><b>{row['station_name']}</b></td>
            <td>{row['bloom_prob']:.0%}</td>
            <td>{row['aeration_score']:.2f}</td>
            <td>{row['do']:.2f} mg/L</td>
            <td>{row['temp']:.1f} °C</td>
            <td style="color:#c0392b"><b>INTERVENE</b></td>
        </tr>"""

    html = f"""
    <html><body>
    <h2 style="font-family:sans-serif">🌊 HAB Early Warning System — {run_date}</h2>
    <p style="font-family:sans-serif">
        The following station(s) have crossed all three intervention thresholds:<br>
        Bloom probability &gt; {BLOOM_PROB_THRESHOLD:.0%} AND
        Aeration score &gt; {AERATION_SCORE_THRESHOLD} AND
        DO &lt; {DO_HYPOXIA_THRESHOLD} mg/L
    </p>
    <table border="1" cellpadding="6" style="font-family:monospace;border-collapse:collapse">
        <tr style="background:#2c3e50;color:white">
            <th>Station</th><th>Bloom P</th><th>S Score</th>
            <th>DO</th><th>Temp</th><th>Action</th>
        </tr>
        {rows}
    </table>
    <p style="font-family:sans-serif;font-size:12px;color:#888">
        Full predictions: data/daily_predictions.csv<br>
        HAB Bloom Predictor — Vihaan Goyal, Westhill High School
    </p>
    </body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL_FROM
    msg["To"] = ALERT_EMAIL_TO
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(ALERT_EMAIL_FROM, SMTP_PASSWORD)
        server.sendmail(ALERT_EMAIL_FROM, ALERT_EMAIL_TO, msg.as_string())

    print(f"[INFO] Alert email sent to {ALERT_EMAIL_TO}")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(target_date: date):
    print(f"\n{'='*60}")
    print(f"HAB Daily Inference — {target_date}")
    print(f"{'='*60}")

    # Load model and climatology
    print("Loading model...")
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)

    print("Loading climatology...")
    climatology = load_climatology()

    # Collect features for all stations
    records = []
    for station, (lat, lon) in STATIONS.items():
        print(f"  Fetching {station}...", end=" ")
        raw = fetch_local(station, target_date, n_days=60)
        feats = engineer_features(raw, station, lat, lon, climatology, target_date)
        if feats is None:
            print("insufficient data — skipped")
            continue
        records.append(feats)
        print("ok")

    if not records:
        print("[ERROR] No stations returned usable data.")
        return

    df = pd.DataFrame(records)

    # Run inference
    X = df[FEATURES].copy()
    missing_mask = X.isna().any(axis=1)
    if missing_mask.any():
        print(f"[WARN] {missing_mask.sum()} stations have missing features — imputing with column median")
        X = X.fillna(X.median())

    df['bloom_prob'] = model.predict_proba(X.values)[:, 1]

    # Compute aeration scores
    df['do'] = df['oxygen_concentration_in_sea_water']
    df['temp'] = df['sea_water_temperature']
    df['aeration_score'] = df.apply(
        lambda r: aeration_score(r['do'], r['temp'], r['bloom_prob']), axis=1
    )
    df['intervene'] = df.apply(
        lambda r: intervention_flag(r['bloom_prob'], r['aeration_score'], r['do']), axis=1
    )

    # Save full results
    out_cols = ['station_name', 'date', 'latitude', 'longitude',
                'bloom_prob', 'aeration_score', 'do', 'temp',
                'sea_water_salinity', 'pH', 'intervene']
    df[out_cols].to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved predictions to {OUTPUT_PATH}")

    # Print summary
    print(f"\nResults summary:")
    print(f"  Stations processed: {len(df)}")
    print(f"  High-risk (P > 0.70): {(df['bloom_prob'] > BLOOM_PROB_THRESHOLD).sum()}")
    print(f"  Intervention flagged: {df['intervene'].sum()}")

    top5 = df.nlargest(5, 'bloom_prob')[['station_name', 'bloom_prob', 'aeration_score', 'do', 'intervene']]
    print(f"\nTop 5 stations by bloom probability:")
    print(top5.to_string(index=False))

    # Send alert if any stations flagged
    alerts = df[df['intervene']][out_cols]
    if len(alerts) > 0:
        print(f"\n[ALERT] {len(alerts)} station(s) crossed intervention thresholds!")
        send_alert(alerts, target_date)
    else:
        print("\n[OK] No stations require intervention today.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HAB daily inference pipeline")
    parser.add_argument("--date", type=str, default=None,
                        help="Target date (YYYY-MM-DD). Defaults to today.")
    args = parser.parse_args()

    if args.date:
        target = date.fromisoformat(args.date)
    else:
        target = date.today()

    run(target)