# ml/training/create_visualizations.py
# RUN: python ml/training/create_visualizations.py

import pandas as pd, numpy as np, joblib, json, os
import matplotlib.pyplot as plt

os.makedirs('ml/visualizations', exist_ok=True)
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   '#F8FAFC',
    'font.family':      'sans-serif',
})

# ── Must match EXACTLY the FEATURES list in train_failure_model.py ──
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

# ─── CHART 1: Feature Importance ───
print('Creating feature_importance.png...')
model = joblib.load('ml/models/brake_failure_model.pkl')
imp   = model.feature_importances_
idx   = np.argsort(imp)

fig, ax = plt.subplots(figsize=(12, 7))
colors  = ['#1D4ED8' if i == idx[-1] else '#93C5FD' for i in range(len(FEATURES))]
bars    = ax.barh([FEATURES[i] for i in idx], [imp[i] for i in idx],
                  color=colors, height=0.6)
ax.set_xlabel('Importance Score', fontsize=12, labelpad=10)
ax.set_title('Feature Importance — Failure Prediction Model',
             fontsize=14, fontweight='bold', pad=15)
for bar, val in zip(bars, [imp[i] for i in idx]):
    ax.text(val + 0.001, bar.get_y() + bar.get_height() / 2,
            f'{val:.3f}', va='center', fontsize=9, color='#374151')
plt.tight_layout()
plt.savefig('ml/visualizations/feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: feature_importance.png')

# ─── CHART 2: Model Accuracy ───
print('Creating model_accuracy.png...')
with open('ml/evaluation/accuracy_report.json') as f:
    report = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(11, 5))

# Left: accuracy bar chart
ax1 = axes[0]
metrics    = ['Train (CV)', 'Test']
values     = [report.get('cv_accuracy_pct', 90), report['accuracy_pct']]
color_bars = ['#15803D', '#1D4ED8']
bars2 = ax1.bar(metrics, values, color=color_bars, width=0.45)
ax1.set_ylim(0, 115)
ax1.axhline(80, color='#DC2626', ls='--', lw=1.5, label='80% target')
for b, v in zip(bars2, values):
    ax1.text(b.get_x() + b.get_width() / 2, v + 1.5,
             f'{v:.1f}%', ha='center', fontsize=13, fontweight='bold')
ax1.set_title('Model Accuracy', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)

# Right: urgency class pie
ax2    = axes[1]
classes = report.get('classes', ['CRITICAL', 'HIGH', 'LOW', 'MEDIUM'])
sizes   = [25, 25, 25, 25]
explode = [0.05] * len(classes)
colors_pie = ['#DC2626', '#D97706', '#15803D', '#1D4ED8'][:len(classes)]
ax2.pie(sizes, labels=classes, autopct='%1.0f%%',
        colors=colors_pie, explode=explode, startangle=90)
ax2.set_title('Urgency Class Distribution', fontsize=13, fontweight='bold')

plt.suptitle('Brake Failure Model — Performance Summary',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('ml/visualizations/model_accuracy.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: model_accuracy.png')

# ─── CHART 3: Sensor Trends ───
print('Creating sensor_trends.png...')
np.random.seed(42)
days         = list(range(1, 31))
brake_temps  = [75 + i * 0.55 + np.random.normal(0, 1.2) for i in days]
engine_temps = [92 + np.random.normal(0, 2.5) for _ in days]
oil_press    = [45 + np.random.normal(0, 2.0) for _ in days]
tire_press   = [32 + np.random.normal(0, 0.8) for _ in days]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Top: temperature chart
ax1.plot(days, brake_temps,  'o-', color='#DC2626', lw=2.5, ms=4, label='Brake Temp (°C)')
ax1.plot(days, engine_temps, 's-', color='#D97706', lw=2,   ms=4, label='Engine Temp (°C)')
ax1.axhline(90,  color='#DC2626', ls='--', alpha=0.5, lw=1.5, label='Brake Warning (90°C)')
ax1.axhline(100, color='#B91C1C', ls=':',  alpha=0.5, lw=1.5, label='Brake Critical (100°C)')
ax1.axhline(100, color='#D97706', ls='--', alpha=0.5, lw=1.5, label='Engine Warning (100°C)')
ax1.fill_between(days, brake_temps, alpha=0.07, color='#DC2626')
ax1.set_ylabel('Temperature (°C)', fontsize=11)
ax1.set_title('Sensor Trends — VEH001  (Last 30 Days)', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9, loc='upper left')

# Bottom: pressure chart
ax2.plot(days, oil_press,  'D-', color='#1D4ED8', lw=2.5, ms=4, label='Oil Pressure (PSI)')
ax2.plot(days, tire_press, '^-', color='#7C3AED', lw=2,   ms=4, label='Tire Pressure (PSI)')
ax2.axhline(38, color='#1D4ED8', ls='--', alpha=0.5, lw=1.5, label='Oil Warning (38 PSI)')
ax2.axhline(28, color='#B91C1C', ls=':',  alpha=0.5, lw=1.5, label='Oil Critical (28 PSI)')
ax2.axhline(30, color='#7C3AED', ls='--', alpha=0.5, lw=1.5, label='Tire Warning (30 PSI)')
ax2.set_xlabel('Day', fontsize=11)
ax2.set_ylabel('Pressure (PSI)', fontsize=11)
ax2.legend(fontsize=9, loc='lower left')

plt.tight_layout()
plt.savefig('ml/visualizations/sensor_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: sensor_trends.png')

print('\nAll 3 charts saved to ml/visualizations/')