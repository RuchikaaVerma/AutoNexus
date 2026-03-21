# ml/evaluation/evaluate_model.py
# RUN: python ml/evaluation/evaluate_model.py

import pandas as pd, joblib, json
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score

df    = pd.read_csv('ml/data/processed/features_engineered.csv')
model = joblib.load('ml/models/brake_failure_model.pkl')
le    = joblib.load('ml/models/label_encoder.pkl')

def urgency(d):
    if d <= 7:  return 'CRITICAL'
    if d <= 14: return 'HIGH'
    if d <= 30: return 'MEDIUM'
    return 'LOW'

df['urgency']         = df['days_until_failure'].apply(urgency)
df['urgency_encoded'] = le.transform(df['urgency'])

FEATURES = [
    'brake_temperature',
    'brake_fluid_level',
    'oil_pressure',
    'engine_temperature',
    'tire_pressure',
    'mileage',
    'days_since_last_service',
    'brake_temp_deviation',
    'oil_pressure_deviation',
    'avg_daily_mileage',
    'brake_risk_score',
    'engine_risk_score',
    'sensor_variance',
    'mileage_category',
    'driving_encoded',
]

X, y = df[FEATURES], df['urgency_encoded']

# 5-fold cross validation
cv = cross_val_score(model, X, y, cv=5)
print(f'5-Fold CV: {cv.mean()*100:.1f}% +/- {cv.std()*100:.1f}%')

# ── Test with a known CRITICAL case ──
# All 15 features must be present — matches FEATURES list exactly
test = pd.DataFrame([{
    'brake_temperature':       105,    # CRITICAL >100
    'brake_fluid_level':        62,    # CRITICAL <70
    'oil_pressure':             24,    # CRITICAL <28
    'engine_temperature':      109,    # CRITICAL >105
    'tire_pressure':            23,    # CRITICAL <26
    'mileage':               88000,    # CRITICAL >80000
    'days_since_last_service': 200,

    # Engineered features — computed from raw sensors above
    'brake_temp_deviation':     25,    # 105 - 80 = 25
    'oil_pressure_deviation':  -22,    # 24 - 46 = -22
    'avg_daily_mileage':        24,    # 88000 / (10*365) = 24
    'brake_risk_score':       0.92,    # high risk
    'engine_risk_score':      0.95,    # high risk
    'sensor_variance':        0.45,    # high variance
    'mileage_category':          2,    # critical mileage
    'driving_encoded':           2,    # city driving
}])

pred  = le.inverse_transform(model.predict(test))[0]
proba = model.predict_proba(test)[0].max()
print(f'\nTest prediction:  {pred}  ({proba*100:.1f}% confidence)')
print(f'Expected:         CRITICAL')
print(f'Result:           {"PASS" if pred == "CRITICAL" else "FAIL"}')

# ── Test with a known HEALTHY case ──
test2 = pd.DataFrame([{
    'brake_temperature':        80,
    'brake_fluid_level':        92,
    'oil_pressure':             46,
    'engine_temperature':       92,
    'tire_pressure':            32,
    'mileage':               25000,
    'days_since_last_service':  60,
    'brake_temp_deviation':      0,
    'oil_pressure_deviation':    0,
    'avg_daily_mileage':         7,
    'brake_risk_score':       0.15,
    'engine_risk_score':      0.12,
    'sensor_variance':        0.02,
    'mileage_category':          0,
    'driving_encoded':           1,
}])

pred2  = le.inverse_transform(model.predict(test2))[0]
proba2 = model.predict_proba(test2)[0].max()
print(f'\nTest prediction:  {pred2}  ({proba2*100:.1f}% confidence)')
print(f'Expected:         LOW')
print(f'Result:           {"PASS" if pred2 == "LOW" else "FAIL"}')

print('\nModel evaluation complete.')
print('accuracy_report.json already saved by train_failure_model.py')