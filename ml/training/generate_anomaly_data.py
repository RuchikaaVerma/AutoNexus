import pandas as pd
import numpy as np
import random
 
np.random.seed(99)
random.seed(99)
 
normal_rows    = []
anomalous_rows = []
 
# ── 4000 NORMAL rows — sensors in HEALTHY range ──
for _ in range(4000):
    normal_rows.append({
        'brake_temp':    round(random.uniform(70, 90),   1),   # healthy: 70-90°C
        'brake_fluid':   round(random.uniform(85, 100),  1),   # healthy: 85-100%
        'oil_pressure':  round(random.uniform(38, 55),   1),   # healthy: 38-55 PSI
        'engine_temp':   round(random.uniform(85, 100),  1),   # healthy: 85-100°C
        'tire_pressure': round(random.uniform(30, 35),   1),   # healthy: 30-35 PSI
        'mileage':       random.randint(5000, 49999),           # healthy: 0-50,000 km
        'is_anomaly': 0
    })
 
# ── 1000 ANOMALOUS rows — sensors in CRITICAL range ──
for _ in range(1000):
    anomalous_rows.append({
        'brake_temp':    round(random.uniform(101, 115),  1),  # critical: >100°C
        'brake_fluid':   round(random.uniform(55,  69),   1),  # critical: <70%
        'oil_pressure':  round(random.uniform(18,  27),   1),  # critical: <28 PSI
        'engine_temp':   round(random.uniform(106, 118),  1),  # critical: >105°C
        'tire_pressure': round(random.uniform(20,  25),   1),  # critical: <26 PSI
        'mileage':       random.randint(80001, 100000),         # critical: >80,000 km
        'is_anomaly': 1
    })
 
df = pd.DataFrame(normal_rows + anomalous_rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
 
df.to_csv('ml/data/anomaly_data.csv', index=False)
print(f'Saved: ml/data/anomaly_data.csv  ({len(df):,} rows)')
print('\nLabel counts:')
print(df['is_anomaly'].value_counts())
print('\nNormal sensor ranges:')
print(df[df['is_anomaly']==0].describe().round(1).to_string())
print('\nAnomalous sensor ranges:')
print(df[df['is_anomaly']==1].describe().round(1).to_string())