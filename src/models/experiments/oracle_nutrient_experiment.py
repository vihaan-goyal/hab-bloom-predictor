"""
oracle_nutrient_experiment.py
------------------------------
ORACLE / UPPER-BOUND EXPERIMENT — NOT FOR PRODUCTION USE.

Establishes the theoretical precision ceiling if perfect nutrient (DIN/DIP)
data were available at all stations. Synthetic concentrations are biologically
grounded (Gobler et al. 2006; Perreira 2021) and correlated with bloom events
at known LIS thresholds; they are NOT real measurements and must never enter
the deployed pipeline.

This is standard ML practice for quantifying the expected value of additional
data before acquiring it. The result justifies the nutrient data request to
CT DEEP.

Run from repo root:
    python src/models/experiments/oracle_nutrient_experiment.py
"""

import glob
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score

# ---------------------------------------------------------------------------
# Data loading — mirrors final_evaluation_threshold_sweep.py exactly
# ---------------------------------------------------------------------------
print("Loading data/hab_features_tidal.csv...")
df = pd.read_csv("data/hab_features_tidal.csv")
df['date'] = pd.to_datetime(df['date'])


def load_percent_saturation():
    frames = []
    for f in sorted(glob.glob('data/raw/deep_wq_extra/deep_wq_S_*.csv')):
        frames.append(pd.read_csv(
            f, skiprows=[1],
            usecols=['station_name', 'time', 'percent_saturation']))
    ps = pd.concat(frames, ignore_index=True)
    ps = ps[ps['station_name'].notna()].copy()
    ps['station_name'] = ps['station_name'].astype(str)
    ps['date'] = (pd.to_datetime(ps['time'], utc=True)
                    .dt.tz_localize(None).dt.normalize())
    ps['percent_saturation'] = pd.to_numeric(ps['percent_saturation'], errors='coerce')
    return (ps.dropna(subset=['percent_saturation'])
              .groupby(['date', 'station_name'], as_index=False)
              ['percent_saturation'].mean())


if 'percent_saturation' not in df.columns:
    print("Merging percent_saturation from deep_wq_S_*.csv...")
    ps = load_percent_saturation()
    df['station_name'] = df['station_name'].astype(str)
    df = df.merge(ps, on=['date', 'station_name'], how='left')
    print(f"  coverage: {df['percent_saturation'].notna().mean()*100:.1f}%")

for n, min_p in [(3, 2), (6, 3), (9, 5), (14, 7), (21, 10)]:
    df[f'chl_roll{n}_mean'] = (
        df.groupby('station_name')['Chlorophyll']
          .transform(lambda x: x.rolling(n, min_periods=min_p).mean())
    )

df['chl_trend'] = (
    df.groupby('station_name')['Chlorophyll']
      .transform(lambda x: x.rolling(4, min_periods=3)
                 .apply(lambda v: np.polyfit(range(len(v)), v, 1)[0]))
)

print("Recomputing bloom_28d labels...")
df['bloom_28d'] = 0
for station, grp in df.groupby('station_name'):
    idx   = grp.index
    dates = grp['date'].values
    chl   = grp['Chlorophyll'].values
    labels = np.zeros(len(grp), dtype=int)
    for i in range(len(grp)):
        mask = (dates > dates[i]) & (dates <= dates[i] + np.timedelta64(28, 'D'))
        if mask.any() and (chl[mask] > 10).any():
            labels[i] = 1
    df.loc[idx, 'bloom_28d'] = labels

# ---------------------------------------------------------------------------
# Feature sets
# ---------------------------------------------------------------------------
BASE_FEATURES = [
    'Chlorophyll', 'chl_lag1', 'chl_lag2', 'chl_lag3', 'chl_lag4',
    'chl_roll3_mean', 'chl_roll6_mean', 'chl_roll9_mean',
    'chl_roll14_mean', 'chl_roll21_mean', 'chl_trend',
    'chl_anomaly', 'chl_climatology',
    'do_lag1', 'temp_lag1', 'sal_lag1',
    'sal_lag2', 'sal_lag3', 'sal_lag4',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water',
    'month', 'latitude_x', 'longitude_x',
    'nox_lag2', 'dip_lag2', 'dip_change', 'dip_x_month',
    'neighbor_chl3_mean', 'neighbor_chl3_lag1',
    'tidal_gt_anom', 'tidal_msl_anom',
    'percent_saturation',
]
BASE_FEATURES = [f for f in BASE_FEATURES if f in df.columns]
ORACLE_FEATS  = ['syn_nox', 'syn_dip', 'syn_nox_dip_ratio']

# ---------------------------------------------------------------------------
# Splits
# ---------------------------------------------------------------------------
train_df = df[df['date'].dt.year <= 2019].copy().reset_index(drop=True)
test_df  = df[df['date'].dt.year >= 2023].copy().reset_index(drop=True)

print(f"Train (<=2019): {len(train_df):,} | Test (>=2023): {len(test_df):,}")
print(f"Train bloom rate: {train_df['bloom_28d'].mean()*100:.1f}%")
print(f"Test  bloom rate: {test_df['bloom_28d'].mean()*100:.1f}%")

THRESHOLD = 0.60
N_SEEDS   = 5
SEEDS     = [42, 123, 456, 789, 1337]

# Western LIS stations have lower nutrient monitoring coverage
WESTERN_STATIONS = {'A4', 'B3', 'C1', '01', '02'}

# ---------------------------------------------------------------------------
# Synthetic nutrient generation
# ORACLE EXPERIMENT ONLY — biological distributions from peer-reviewed LIS
# literature (Gobler et al. 2006, Perreira 2021).
# ---------------------------------------------------------------------------

def generate_synthetic_nutrients(df_in, version, seed):
    """
    Generate synthetic DIN (syn_nox) and DIP (syn_dip) correlated with bloom_28d.

    Versions:
      'perfect'   — strong signal, 20% noise rows (theoretical upper bound)
      'realistic' — post-TMDL era weakens the signal, 30% noise
      'sparse'    — realistic + 50% NaN (biweekly sampling) + extra NaN on
                    western stations (30% coverage instead of 60%)

    All values are clipped to physical bounds and are NOT real measurements.
    """
    rng   = np.random.default_rng(seed)
    df    = df_in.copy()
    n     = len(df)
    bloom = df['bloom_28d'].values.astype(int)
    pt    = (df['date'].dt.year >= 2014).values  # post-TMDL flag

    syn_nox = np.zeros(n, dtype=float)
    syn_dip = np.zeros(n, dtype=float)

    if version == 'perfect':
        # bloom rows: elevated pre-bloom nutrient conditions
        b1 = bloom == 1
        b0 = ~b1
        syn_nox[b1] = rng.normal(8,   2,    b1.sum())
        syn_dip[b1] = rng.normal(0.4, 0.1,  b1.sum())
        syn_nox[b0] = rng.normal(2,   1.5,  b0.sum())
        syn_dip[b0] = rng.normal(0.1, 0.05, b0.sum())
        noise_frac  = 0.20

    else:  # 'realistic' and 'sparse' share the same distributions
        # Pre-TMDL bloom: very high nutrients (pre-2014, Gobler 2006 range)
        m = (bloom == 1) & ~pt
        syn_nox[m] = rng.normal(10,  3,    m.sum())
        syn_dip[m] = rng.normal(0.5, 0.15, m.sum())
        # Post-TMDL bloom: lower NOX but still bloom-sustaining (Perreira 2021)
        m = (bloom == 1) & pt
        syn_nox[m] = rng.normal(4,   1.5,  m.sum())
        syn_dip[m] = rng.normal(0.25, 0.08, m.sum())
        # Pre-TMDL non-bloom: moderate nutrients
        m = (bloom == 0) & ~pt
        syn_nox[m] = rng.normal(5,   2,    m.sum())
        syn_dip[m] = rng.normal(0.2, 0.08, m.sum())
        # Post-TMDL non-bloom: very low NOX after TMDL reduction
        m = (bloom == 0) & pt
        syn_nox[m] = rng.normal(1.5, 1,    m.sum())
        syn_dip[m] = rng.normal(0.08, 0.04, m.sum())
        noise_frac  = 0.30

    # Measurement noise / spatial mismatch: overwrite with random values
    noise_idx = rng.choice(n, int(n * noise_frac), replace=False)
    syn_nox[noise_idx] = rng.normal(5,   3,   len(noise_idx))
    syn_dip[noise_idx] = rng.normal(0.2, 0.1, len(noise_idx))

    syn_nox = np.clip(syn_nox, 0, 30)
    syn_dip = np.clip(syn_dip, 0, 2)

    df['syn_nox']           = syn_nox
    df['syn_dip']           = syn_dip
    df['syn_nox_dip_ratio'] = syn_nox / (syn_dip + 0.01)

    if version == 'sparse':
        # Simulate biweekly sampling: 50% of all rows missing
        missing_all = rng.choice(n, int(n * 0.50), replace=False)
        df.loc[df.index[missing_all], ORACLE_FEATS] = np.nan
        # Western stations have 30% coverage (additional 20% NaN on remaining)
        w_idx = np.where(df['station_name'].isin(WESTERN_STATIONS))[0]
        if len(w_idx) > 0:
            # Among already-non-NaN western rows, drop another 20%
            w_present = w_idx[df.iloc[w_idx]['syn_nox'].notna().values]
            if len(w_present) > 0:
                extra = rng.choice(w_present, int(len(w_present) * 0.20), replace=False)
                df.loc[df.index[extra], ORACLE_FEATS] = np.nan

    return df


# ---------------------------------------------------------------------------
# Single-run evaluation
# ---------------------------------------------------------------------------

def run_experiment(feats, version, seed):
    """Return (precision, recall, f1, n_fp) at THRESHOLD for one seed."""
    if version == 'none':
        tr, te = train_df.copy(), test_df.copy()
    else:
        tr = generate_synthetic_nutrients(train_df, version, seed)
        te = generate_synthetic_nutrients(test_df,  version, seed + 2000)

    feat_avail = [f for f in feats if f in tr.columns]

    def prepare(split):
        sub = split[feat_avail + ['bloom_28d']].dropna(subset=['bloom_28d'])
        return (sub[feat_avail].reset_index(drop=True),
                sub['bloom_28d'].reset_index(drop=True))

    X_tr, y_tr = prepare(tr)
    X_te, y_te = prepare(te)

    med      = X_tr.median()
    scaler   = StandardScaler()
    X_tr_s   = scaler.fit_transform(X_tr.fillna(med))
    X_te_s   = scaler.transform(X_te.fillna(med))

    model = LogisticRegression(
        class_weight='balanced', C=0.05, max_iter=1000, random_state=42)
    model.fit(X_tr_s, y_tr)

    probs = model.predict_proba(X_te_s)[:, 1]
    preds = (probs >= THRESHOLD).astype(int)

    prec = precision_score(y_te, preds, zero_division=0)
    rec  = recall_score(y_te, preds, zero_division=0)
    f1   = f1_score(y_te, preds, zero_division=0)
    n_fp = int(((preds == 1) & (y_te == 0)).sum())

    return prec, rec, f1, n_fp


# ---------------------------------------------------------------------------
# Bloom-nutrient correlation report (sanity check)
# ---------------------------------------------------------------------------
print("\nBloom-nutrient correlations (sanity check, seed=42):")
for v in ['perfect', 'realistic']:
    tmp   = generate_synthetic_nutrients(df, v, seed=42)
    r_nox = tmp['syn_nox'].corr(tmp['bloom_28d'])
    r_dip = tmp['syn_dip'].corr(tmp['bloom_28d'])
    print(f"  {v:12s}: corr(syn_nox, bloom_28d)={r_nox:.3f}  "
          f"corr(syn_dip, bloom_28d)={r_dip:.3f}")

# ---------------------------------------------------------------------------
# Run all experiments
# ---------------------------------------------------------------------------
ORACLE_ONLY_FEATS = ORACLE_FEATS + ['month', 'latitude_x', 'longitude_x']

experiments = [
    ('BASE (current baseline)',  BASE_FEATURES,                'none'),
    ('BASE + perfect oracle',    BASE_FEATURES + ORACLE_FEATS, 'perfect'),
    ('BASE + realistic oracle',  BASE_FEATURES + ORACLE_FEATS, 'realistic'),
    ('BASE + sparse oracle',     BASE_FEATURES + ORACLE_FEATS, 'sparse'),
    ('ORACLE only (no BASE)',     ORACLE_ONLY_FEATS,            'realistic'),
]

print(f"\nRunning {len(experiments)} experiments × {N_SEEDS} seeds "
      f"(threshold={THRESHOLD})...")
results   = {}
baseline_fp = None

for name, feats, version in experiments:
    precs, recs, f1s, fps = [], [], [], []
    for seed in SEEDS:
        p, r, f, fp = run_experiment(feats, version, seed)
        precs.append(p); recs.append(r); f1s.append(f); fps.append(fp)

    results[name] = dict(
        prec_mean=np.mean(precs), prec_std=np.std(precs),
        rec_mean =np.mean(recs),  rec_std =np.std(recs),
        f1_mean  =np.mean(f1s),   f1_std  =np.std(f1s),
        fp_mean  =np.mean(fps),
    )
    if version == 'none':
        baseline_fp = fps[0]
    print(f"  done: {name}")

# ---------------------------------------------------------------------------
# Results table
# ---------------------------------------------------------------------------
print()
print("=" * 65)
print("ORACLE EXPERIMENT RESULTS (mean ± std over 5 seeds)")
print("=" * 65)
hdr = f"{'Experiment':<32}  {'Prec@.60':>13}  {'Rec@.60':>13}  {'F1@.60':>13}"
print(hdr)
print("-" * 65)
for name, r in results.items():
    pm = r['prec_mean']; ps = r['prec_std']
    rm = r['rec_mean'];  rs = r['rec_std']
    fm = r['f1_mean'];   fs = r['f1_std']
    print(f"{name:<32}  {pm:.3f}±{ps:.3f}   {rm:.3f}±{rs:.3f}   {fm:.3f}±{fs:.3f}")

base_prec = results['BASE (current baseline)']['prec_mean']
perf_prec = results['BASE + perfect oracle'  ]['prec_mean']
real_prec = results['BASE + realistic oracle']['prec_mean']
spar_prec = results['BASE + sparse oracle'   ]['prec_mean']

print(f"""
INTERPRETATION:
- Current precision (baseline):              {base_prec:.3f}
- Oracle ceiling (perfect, 20% noise):       {perf_prec:.3f}  (+{perf_prec-base_prec:+.3f} pp)
- Realistic ceiling (post-TMDL, 30% noise):  {real_prec:.3f}  (+{real_prec-base_prec:+.3f} pp)
- Sparse realistic ceiling (50% coverage):   {spar_prec:.3f}  (+{spar_prec-base_prec:+.3f} pp)
- Precision gap that real data could close:  +{real_prec-base_prec:.3f} pp (realistic)
                                             +{perf_prec-base_prec:.3f} pp (if perfect)
""")

if baseline_fp is not None:
    print("False positives eliminated vs baseline (test set, seed=42):")
    for name, r in results.items():
        if name != 'BASE (current baseline)':
            elim = baseline_fp - r['fp_mean']
            print(f"  {name:<32}  {elim:+.1f} FP  "
                  f"({elim/max(baseline_fp,1)*100:+.1f}%)")
