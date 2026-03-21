# ml/training/retrain_model.py
# PURPOSE: Add real service feedback to training data and retrain model
# USE IN:  Week 4 — after Person 4 sends service_feedback.csv with sensor data
# RUN:     python ml/training/retrain_model.py

import pandas as pd, numpy as np, joblib, json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

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

def urgency(d):
    if d <= 7:  return 'CRITICAL'
    if d <= 14: return 'HIGH'
    if d <= 30: return 'MEDIUM'
    return 'LOW'

def engineer_features(df):
    if 'brake_temp_deviation'  not in df.columns:
        df['brake_temp_deviation']  = df['brake_temperature'] - 80
    if 'oil_pressure_deviation' not in df.columns:
        df['oil_pressure_deviation'] = df['oil_pressure'] - 46
    if 'avg_daily_mileage' not in df.columns:
        age = df.get('vehicle_age', 3)
        df['avg_daily_mileage'] = df['mileage'] / (age * 365 + 1)
    if 'brake_risk_score' not in df.columns:
        df['brake_risk_score'] = np.clip(
            (df['brake_temperature'] / 100) * 0.4 +
            ((100 - df['brake_fluid_level']) / 100) * 0.35 +
            (df['mileage'] / 100000) * 0.25, 0, 1)
    if 'engine_risk_score' not in df.columns:
        df['engine_risk_score'] = np.clip(
            (df['engine_temperature'] / 105) * 0.6 +
            (df['mileage'] / 100000) * 0.4, 0, 1)
    if 'sensor_variance' not in df.columns:
        bt_n = (df['brake_temperature']  - 70) / (115 - 70)
        op_n = (df['oil_pressure']       - 18) / (60  - 18)
        et_n = (df['engine_temperature'] - 80) / (115 - 80)
        tp_n = (df['tire_pressure']      - 22) / (38  - 22)
        df['sensor_variance'] = np.std([bt_n, op_n, et_n, tp_n], axis=0)
    if 'mileage_category' not in df.columns:
        df['mileage_category'] = df['mileage'].apply(
            lambda m: 2 if m > 80000 else (1 if m > 50000 else 0))
    if 'tire_pressure' not in df.columns:
        df['tire_pressure'] = 32.0
    if 'driving_encoded' not in df.columns:
        df['driving_encoded'] = 1
    return df

# ── Load existing training data ──
print('Loading existing training data...')
df_existing = pd.read_csv('ml/data/processed/features_engineered.csv')
print(f'Existing rows: {len(df_existing):,}')

# ── Load feedback from Person 4 ──
feedback_path = 'ml/data/service_feedback.csv'
df_feedback   = None
try:
    df_fb_raw = pd.read_csv(feedback_path)
    print(f'Loaded {len(df_fb_raw):,} feedback rows from Person 4')

    required = ['brake_temperature', 'oil_pressure', 'days_until_failure']
    missing  = [c for c in required if c not in df_fb_raw.columns]

    if missing:
        print(f'WARNING: feedback CSV is customer ratings, not sensor data.')
        print(f'Missing columns: {missing}')
        print('Skipping feedback — retraining on existing data only.')
        print('Ask Person 4 to include sensor readings in service_feedback.csv')
        df_combined = df_existing
    else:
        df_feedback = engineer_features(df_fb_raw.copy())
        df_combined = pd.concat(
            [df_existing, df_feedback[FEATURES + ['days_until_failure']]],
            ignore_index=True)
        print(f'Combined total: {len(df_combined):,} rows')

except FileNotFoundError:
    print(f'No feedback file yet — expected at: {feedback_path}')
    print('Retraining on existing data only...')
    df_combined = df_existing

# ── Prepare labels ──
df_combined['urgency']         = df_combined['days_until_failure'].apply(urgency)
le                             = LabelEncoder()
df_combined['urgency_encoded'] = le.fit_transform(df_combined['urgency'])

print('\nUrgency distribution:')
print(df_combined['urgency'].value_counts())

X = df_combined[FEATURES]
y = df_combined['urgency_encoded']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
print(f'\nTraining: {len(X_train):,}  |  Testing: {len(X_test):,}')

# ── Train new model ──
print('\nTraining new model...')
new_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=20,
    min_samples_leaf=10,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
new_model.fit(X_train, y_train)

# ── Evaluate BOTH models using DataFrame — no feature name warnings ──
X_test_df = X_test.reset_index(drop=True)   # already a DataFrame with correct column names
new_acc   = accuracy_score(y_test, new_model.predict(X_test_df))

old_model = joblib.load('ml/models/brake_failure_model.pkl')
old_acc   = accuracy_score(y_test, old_model.predict(X_test_df))

print(f'\nOld model accuracy: {old_acc*100:.1f}%')
print(f'New model accuracy: {new_acc*100:.1f}%')

if new_acc >= old_acc:
    joblib.dump(new_model, 'ml/models/brake_failure_model.pkl')
    joblib.dump(le,        'ml/models/label_encoder.pkl')
    print('New model is better — deployed!')
    report = {
        'model':         'RandomForestClassifier',
        'accuracy_pct':  round(new_acc * 100, 2),
        'features':      FEATURES,
        'classes':       list(le.classes_),
        'train_rows':    len(X_train),
        'test_rows':     len(X_test),
        'retrained':     True,
        'feedback_rows': len(df_feedback) if df_feedback is not None else 0,
    }
    with open('ml/evaluation/accuracy_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print('Updated: ml/evaluation/accuracy_report.json')
else:
    print('Old model is still better — keeping old model.')
   