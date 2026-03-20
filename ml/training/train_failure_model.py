# ml/training/train_failure_model.py
# RUN: python ml/training/train_failure_model.py

import pandas as pd, numpy as np, json, os, joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

os.makedirs('ml/models',     exist_ok=True)
os.makedirs('ml/evaluation', exist_ok=True)

df = pd.read_csv('ml/data/processed/features_engineered.csv')
print(f'Loaded: {df.shape[0]:,} rows')

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

def urgency(days):
    if days <= 7:   return 'CRITICAL'
    if days <= 14:  return 'HIGH'
    if days <= 30:  return 'MEDIUM'
    return 'LOW'

df['urgency'] = df['days_until_failure'].apply(urgency)
print('\nUrgency distribution:')
print(df['urgency'].value_counts())

le = LabelEncoder()
df['urgency_encoded'] = le.fit_transform(df['urgency'])
print(f'Classes: {list(le.classes_)}')

X = df[FEATURES]
y = df['urgency_encoded']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print(f'\nTraining: {len(X_train):,}  |  Testing: {len(X_test):,}')

print('\nTraining Random Forest...')
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=20,
    min_samples_leaf=10,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred   = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'\nAccuracy: {accuracy*100:.1f}%')

if accuracy < 0.80:
    print('Below 80% — paste output here for help')
elif 0.80 <= accuracy <= 0.92:
    print('Target met (80-92%)!')
else:
    print('Above 92% — still good and acceptable')

print('\nDetailed report:')
print(classification_report(y_test, y_pred, target_names=le.classes_))

cv = cross_val_score(model, X, y, cv=5)
print(f'Cross-validation: {cv.mean()*100:.1f}% +/- {cv.std()*100:.1f}%')

joblib.dump(model, 'ml/models/brake_failure_model.pkl')
joblib.dump(le,    'ml/models/label_encoder.pkl')
print('\nSaved: ml/models/brake_failure_model.pkl')
print('Saved: ml/models/label_encoder.pkl')

report = {
    'model':           'RandomForestClassifier',
    'accuracy_pct':    round(accuracy * 100, 2),
    'cv_accuracy_pct': round(cv.mean() * 100, 2),
    'features':        FEATURES,
    'classes':         list(le.classes_),
    'train_rows':      len(X_train),
    'test_rows':       len(X_test),
}
with open('ml/evaluation/accuracy_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print('Saved: ml/evaluation/accuracy_report.json')