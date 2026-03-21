# ml/training/train_anomaly_model.py
# RUN: python ml/training/train_anomaly_model.py

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest

os.makedirs('ml/models', exist_ok=True)

df = pd.read_csv('ml/data/anomaly_data.csv')
print(f'Loaded: {df.shape}')

# ── Must match ALL columns in generate_anomaly_data.py ──
FEATURES = ['brake_temp', 'brake_fluid', 'oil_pressure',
            'engine_temp', 'tire_pressure', 'mileage']

# Train ONLY on normal rows — model learns what healthy looks like
X_normal = df[df['is_anomaly'] == 0][FEATURES]
X_all    = df[FEATURES]

print(f'Training on {len(X_normal):,} normal rows...')
iso = IsolationForest(
    contamination=0.20,
    n_estimators=100,
    random_state=42
)
iso.fit(X_normal)

# Evaluate
y_pred   = iso.predict(X_all)
y_true   = df['is_anomaly'].map({0: 1, 1: -1})
correct  = (y_pred == y_true).sum()
print(f'Correctly classified: {correct}/{len(y_true)} = {correct/len(y_true)*100:.1f}%')

joblib.dump(iso, 'ml/models/anomaly_detector.pkl')
print('Saved: ml/models/anomaly_detector.pkl')

# ── Quick test using DataFrame to avoid feature name warnings ──
test_normal = pd.DataFrame([{
    'brake_temp':    80,
    'brake_fluid':   92,
    'oil_pressure':  45,
    'engine_temp':   92,
    'tire_pressure': 32,
    'mileage':       25000,
}])

test_anomaly = pd.DataFrame([{
    'brake_temp':    108,
    'brake_fluid':   58,
    'oil_pressure':  22,
    'engine_temp':   112,
    'tire_pressure': 23,
    'mileage':       90000,
}])

r1 = iso.predict(test_normal)[0]
r2 = iso.predict(test_anomaly)[0]
print(f'\nQuick test:')
print(f'  Normal sensors  → {"NORMAL" if r1 == 1 else "ANOMALY"}  (expected: NORMAL)')
print(f'  Danger sensors  → {"NORMAL" if r2 == 1 else "ANOMALY"}  (expected: ANOMALY)')

if r1 == 1 and r2 == -1:
    print('\nAnomaly model working correctly!')
else:
    print('\nStill wrong — paste output here for help')