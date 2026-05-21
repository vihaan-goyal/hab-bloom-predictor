import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")
df = pd.read_csv("data/hab_features_final.csv", low_memory=False)
df['date'] = pd.to_datetime(df['date'])
df['bloom_7d_ahead'] = df.groupby('station_name')['bloom'].shift(-7)

FEATURES = [
    'latitude', 'longitude', 'month',
    'sea_water_temperature', 'sea_water_salinity',
    'oxygen_concentration_in_sea_water', 'pH',
    'chl_anomaly', 'chl_climatology',
    'chl_lag3', 'chl_lag7', 'chl_lag14', 'chl_lag21',
    'chl_roll7_mean', 'chl_roll7_std',
    'total_discharge_cfs', 'discharge_lag5',
    'discharge_lag10', 'discharge_lag15',
    'discharge_roll7_mean',
]

TARGET = 'bloom_7d_ahead'

# ------------------------------------------------------------------
# Train model
# ------------------------------------------------------------------
train = df[df['date'].dt.year <= 2019]
val   = df[(df['date'].dt.year >= 2020) & (df['date'].dt.year <= 2022)]

# Keep metadata for analysis
val_full = val[FEATURES + [TARGET, 'station_name', 'date']].dropna(subset=FEATURES + [TARGET])

train_clean = train[FEATURES + [TARGET]].dropna()
X_train = train_clean[FEATURES].copy()
y_train = train_clean[TARGET].copy()

X_val = val_full[FEATURES].copy()
y_val = val_full[TARGET].copy()

scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
model = XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1,
    scale_pos_weight=scale_pos_weight, random_state=42,
    n_jobs=-1, eval_metric='logloss', verbosity=0
)

print(f"X_train shape: {X_train.shape}, columns: {X_train.columns.tolist()}")
print(f"X_val shape: {X_val.shape}, columns: {X_val.columns.tolist()}")

model.fit(X_train.values, y_train.values)

probs = model.predict_proba(X_val.values)[:, 1]
val_full = val_full.copy()
val_full['bloom_prob'] = probs
val_full['predicted_bloom'] = (probs >= 0.5).astype(int)

print(f"Baseline Val AUC: {roc_auc_score(y_val, probs):.4f}")
print(f"Total high-risk predictions (prob >= 0.5): {val_full['predicted_bloom'].sum():,}")

# ------------------------------------------------------------------
# Part 1: Aeration Suitability Scoring
#
# Aeration works best when:
# - Water is calm (low wave height)
# - Thermal stratification is present (warm surface, cold bottom proxy)
# - Dissolved oxygen is low (hypoxic conditions driving sediment nutrient release)
# - Salinity is lower (fresher water mixes more easily)
#
# We score each high-risk prediction for aeration suitability.
# ------------------------------------------------------------------
print("\n" + "="*60)
print("PART 1: Aeration Suitability Scoring")
print("="*60)

high_risk = val_full[val_full['predicted_bloom'] == 1].copy()

# Normalize each factor 0-1 (higher = more suitable for aeration)
def normalize(series):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)

# Low wave height = calm water = aeration more effective

do_col   = high_risk['oxygen_concentration_in_sea_water'].fillna(high_risk['oxygen_concentration_in_sea_water'].median())
temp_col = high_risk['sea_water_temperature'].fillna(high_risk['sea_water_temperature'].median())

high_risk['aeration_do']   = 1 - normalize(do_col)
high_risk['aeration_temp'] = normalize(temp_col)
high_risk['aeration_prob'] = normalize(high_risk['bloom_prob'])

high_risk['aeration_score'] = (
    high_risk['aeration_do']   * 0.45 +
    high_risk['aeration_temp'] * 0.30 +
    high_risk['aeration_prob'] * 0.25
)

print(f"\nAeration suitability score distribution:")
print(high_risk['aeration_score'].describe().round(3))

# Top intervention candidates
top_candidates = high_risk.nlargest(20, 'aeration_score')[
    ['station_name', 'date', 'bloom_prob', 'aeration_score',
     'oxygen_concentration_in_sea_water', 'sea_water_temperature']
].reset_index(drop=True)

print(f"\nTop 20 highest-priority aeration intervention candidates:")
print(top_candidates.to_string(index=False))

# ------------------------------------------------------------------
# Part 2: Per-Station Intervention Priority
# ------------------------------------------------------------------
print("\n" + "="*60)
print("PART 2: Station-Level Intervention Priority")
print("="*60)

station_priority = high_risk.groupby('station_name').agg(
    latitude=('latitude', 'first'),
    longitude=('longitude', 'first'),
    n_high_risk_days=('predicted_bloom', 'count'),
    mean_bloom_prob=('bloom_prob', 'mean'),
    mean_aeration_score=('aeration_score', 'mean'),
    mean_do=('oxygen_concentration_in_sea_water', 'mean'),
    mean_temp=('sea_water_temperature', 'mean'),
    pct_low_do=('oxygen_concentration_in_sea_water',
                lambda x: (x < x.quantile(0.25)).mean()),
).reset_index()

station_priority['intervention_priority'] = (
    normalize(station_priority['n_high_risk_days'])   * 0.30 +
    normalize(station_priority['mean_bloom_prob'])     * 0.30 +
    normalize(station_priority['mean_aeration_score']) * 0.40
)

station_priority = station_priority.sort_values(
    'intervention_priority', ascending=False).reset_index(drop=True)

station_priority.to_csv("data/station_intervention_priority.csv", index=False)

print("\nTop 15 stations by intervention priority:")
print(station_priority[['station_name', 'latitude', 'longitude',
                          'n_high_risk_days', 'mean_bloom_prob',
                          'mean_aeration_score', 'intervention_priority']
                        ].head(15).to_string(index=False))

# ------------------------------------------------------------------
# Part 3: Seasonal Intervention Windows
# When during the year are interventions most needed?
# ------------------------------------------------------------------
print("\n" + "="*60)
print("PART 3: Seasonal Intervention Windows")
print("="*60)

high_risk['month'] = pd.to_datetime(high_risk['date']).dt.month
monthly = high_risk.groupby('month').agg(
    high_risk_days=('predicted_bloom', 'count'),
    mean_bloom_prob=('bloom_prob', 'mean'),
    mean_aeration_score=('aeration_score', 'mean'),
).reset_index()

monthly['month_name'] = monthly['month'].map({
    1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
    7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'
})

monthly.to_csv("data/seasonal_intervention_windows.csv", index=False)
print(monthly[['month_name','high_risk_days',
               'mean_bloom_prob','mean_aeration_score']].to_string(index=False))

# ------------------------------------------------------------------
# Part 4: Estimate Bloom-Days Preventable by Aeration
# Assume aeration is effective for top-scoring candidates
# (aeration_score > 0.6 = highly suitable conditions)
# ------------------------------------------------------------------
print("\n" + "="*60)
print("PART 4: Estimated Preventable Bloom-Days")
print("="*60)

# Conservative estimate: aeration effective when score > 0.6
# and DO < 6 mg/L (hypoxic threshold)
highly_suitable = high_risk[
    (high_risk['aeration_score'] > 0.6) &
    (high_risk['oxygen_concentration_in_sea_water'] < 6.0)
]

total_high_risk = len(high_risk)
preventable     = len(highly_suitable)
pct_preventable = preventable / total_high_risk * 100

print(f"\nTotal predicted high-risk bloom-days (2020-2022): {total_high_risk:,}")
print(f"Bloom-days with highly suitable aeration conditions: {preventable:,}")
print(f"Estimated preventable with targeted aeration: {pct_preventable:.1f}%")
print(f"\nOf the {preventable:,} preventable bloom-days:")
print(f"  Stations involved: {highly_suitable['station_name'].nunique()}")

if len(highly_suitable) > 0:
    print(f"  Peak month: {highly_suitable.groupby('month')['predicted_bloom'].count().idxmax()}")
else:
    print("  No highly suitable intervention windows found — lower the aeration_score threshold.")

print(f"  Mean bloom probability: {highly_suitable['bloom_prob'].mean():.3f}")

# ------------------------------------------------------------------
# Figures
# ------------------------------------------------------------------

# Figure 1: Intervention priority map
fig, ax = plt.subplots(figsize=(12, 6))
sc = ax.scatter(
    station_priority['longitude'],
    station_priority['latitude'],
    c=station_priority['intervention_priority'],
    cmap='RdYlGn_r',
    s=station_priority['n_high_risk_days'] /
      station_priority['n_high_risk_days'].max() * 400 + 40,
    alpha=0.85,
    edgecolors='gray',
    linewidths=0.5
)
plt.colorbar(sc, ax=ax, label='Intervention Priority Score')
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Aeration Intervention Priority by Station\n"
             "(circle size = number of high-risk days, color = priority score)")
for _, row in station_priority.head(5).iterrows():
    ax.annotate(row['station_name'],
                (row['longitude'], row['latitude']),
                textcoords="offset points", xytext=(5, 5), fontsize=8)
plt.tight_layout()
plt.savefig("figures/intervention_priority_map.png", dpi=150)
plt.close()
print("\nSaved figures/intervention_priority_map.png")

# Figure 2: Seasonal intervention windows
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(monthly['month_name'], monthly['high_risk_days'],
              color='steelblue', alpha=0.7, label='High-risk days')
ax2 = ax.twinx()
ax2.plot(monthly['month_name'], monthly['mean_aeration_score'],
         color='red', marker='o', linewidth=2, label='Aeration suitability')
ax.set_xlabel("Month")
ax.set_ylabel("High-Risk Bloom-Days", color='steelblue')
ax2.set_ylabel("Mean Aeration Suitability Score", color='red')
ax.set_title("Seasonal Intervention Windows\n"
             "High-Risk Bloom Days and Aeration Suitability by Month")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
plt.tight_layout()
plt.savefig("figures/seasonal_intervention_windows.png", dpi=150)
plt.close()
print("Saved figures/seasonal_intervention_windows.png")

# Figure 3: Aeration score distribution by station (top 15)
top15 = station_priority.head(15)
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#d73027' if s > 0.6 else '#fc8d59' if s > 0.4 else '#91bfdb'
          for s in top15['intervention_priority']]
ax.barh(top15['station_name'], top15['intervention_priority'], color=colors)
ax.axvline(x=0.6, linestyle='--', color='red', alpha=0.7, label='High priority threshold')
ax.axvline(x=0.4, linestyle='--', color='orange', alpha=0.7, label='Medium priority threshold')
ax.set_xlabel("Intervention Priority Score")
ax.set_title("Top 15 Stations by Aeration Intervention Priority")
ax.legend()
plt.tight_layout()
plt.savefig("figures/station_intervention_scores.png", dpi=150)
plt.close()
print("Saved figures/station_intervention_scores.png")

# Figure 4: Bloom probability vs aeration suitability scatter
fig, ax = plt.subplots(figsize=(8, 6))
sample = high_risk.sample(min(5000, len(high_risk)), random_state=42)
sc = ax.scatter(sample['bloom_prob'], sample['aeration_score'],
                c=sample['oxygen_concentration_in_sea_water'],
                cmap='RdYlGn', alpha=0.4, s=10)
plt.colorbar(sc, ax=ax, label='Dissolved Oxygen (mg/L)')
ax.axvline(x=0.5, linestyle='--', color='gray', alpha=0.7)
ax.axhline(y=0.6, linestyle='--', color='gray', alpha=0.7)
ax.set_xlabel("Predicted Bloom Probability")
ax.set_ylabel("Aeration Suitability Score")
ax.set_title("Bloom Probability vs Aeration Suitability\n"
             "(color = dissolved oxygen; top-right = highest intervention value)")
ax.text(0.75, 0.65, "High priority\nintervention zone",
        fontsize=9, color='darkred',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
plt.tight_layout()
plt.savefig("figures/bloom_prob_vs_aeration.png", dpi=150)
plt.close()
print("Saved figures/bloom_prob_vs_aeration.png")

print("\nAeration intervention analysis complete.")