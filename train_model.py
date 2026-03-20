import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

print("Training ML Model for Vehicle Failure Prediction...\n")

# Load training data
df = pd.read_csv('training_data_from_obd.csv')
print(f"✓ Loaded {len(df)} training examples\n")

# Prepare features and labels
X = df[['brake_temp', 'oil_pressure', 'engine_temp',
        'tire_pressure', 'brake_fluid_level', 'mileage']]
y = df['failure_occurred']

print("Features (6 sensors):")
for col in X.columns:
    print(f"  - {col}")

print(f"\nTarget: failure_occurred (0=No, 1=Yes)")
print(f"  Class 0 (No Failure): {(y == 0).sum()} samples")
print(f"  Class 1 (Failure): {(y == 1).sum()} samples\n")

# Split data: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples\n")

# Train XGBoost model
print("=" * 60)
print("TRAINING XGBOOST MODEL...")
print("=" * 60)

model = XGBClassifier(
    n_estimators=100,  # Number of trees
    max_depth=6,  # Tree depth
    learning_rate=0.1,  # Learning rate
    random_state=42,
    eval_metric='logloss'
)

model.fit(X_train, y_train)
print("✓ Training complete!\n")

# Make predictions on test set
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Evaluate model
accuracy = accuracy_score(y_test, y_pred)
print("=" * 60)
print("MODEL PERFORMANCE:")
print("=" * 60)
print(f"Accuracy: {accuracy * 100:.2f}%\n")

print("Classification Report:")
print(classification_report(y_test, y_pred,
                            target_names=['No Failure', 'Failure']))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("  [[TrueNeg  FalsePos]")
print("   [FalseNeg TruePos]]\n")

# Feature importance
print("=" * 60)
print("FEATURE IMPORTANCE:")
print("=" * 60)
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"  {row['feature']:20} {row['importance']:.4f} {'█' * int(row['importance'] * 50)}")

# Save model
model_filename = 'vehicle_failure_model.pkl'
joblib.dump(model, model_filename)
print(f"\n✓ Model saved to: {model_filename}")

# Test with example predictions
print("\n" + "=" * 60)
print("EXAMPLE PREDICTIONS:")
print("=" * 60)

examples = [
    {
        'name': 'Healthy Vehicle',
        'data': [[75.0, 42.0, 88.0, 32.0, 95.0, 25000]]
    },
    {
        'name': 'Warning Vehicle',
        'data': [[92.0, 32.0, 98.0, 28.0, 75.0, 65000]]
    },
    {
        'name': 'Critical Vehicle',
        'data': [[108.0, 20.0, 110.0, 22.0, 55.0, 95000]]
    }
]

for example in examples:
    pred = model.predict(example['data'])[0]
    proba = model.predict_proba(example['data'])[0]

    print(f"\n{example['name']}:")
    print(f"  Input: {example['data'][0]}")
    print(f"  Prediction: {'FAILURE' if pred == 1 else 'NO FAILURE'}")
    print(f"  Probability: {proba[1] * 100:.1f}% failure risk")

print("\n" + "=" * 60)
print("✓ MODEL TRAINING COMPLETE!")
print("=" * 60)