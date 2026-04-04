import pandas as pd
import numpy as np
import os
 
df = pd.read_csv('ml/data/training_data.csv')
print(f'Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns')
 
# ── CORRECT BASELINES (midpoint of healthy range) ──
BRAKE_TEMP_BASELINE    = 80    # midpoint of 70-90°C healthy range
OIL_PRESSURE_BASELINE  = 46    # midpoint of 38-55 PSI healthy range
ENGINE_TEMP_BASELINE   = 92    # midpoint of 85-100°C healthy range
TIRE_PRESSURE_BASELINE = 32    # midpoint of 30-35 PSI healthy range
BRAKE_FLUID_BASELINE   = 92    # midpoint of 85-100% healthy range
 
# ── FEATURE 1: Brake temp deviation from healthy midpoint ──
df['brake_temp_deviation'] = df['brake_temperature'] - BRAKE_TEMP_BASELINE
 
# ── FEATURE 2: Oil pressure deviation from healthy midpoint ──
df['oil_pressure_deviation'] = df['oil_pressure'] - OIL_PRESSURE_BASELINE
 
# ── FEATURE 3: Average daily mileage (wear rate) ──
df['avg_daily_mileage'] = df['mileage'] / (df['vehicle_age'] * 365 + 1)
 
# ── FEATURE 4: Brake risk score (0 to 1 combined) ──
# Higher brake temp + lower fluid + more mileage = higher risk
df['brake_risk_score'] = (
    (df['brake_temperature'] / 100)          * 0.4 +   # weight: 40%
    ((100 - df['brake_fluid_level']) / 100)   * 0.35 +  # weight: 35%
    (df['mileage'] / 100000)                  * 0.25    # weight: 25%
).clip(0, 1)
 
# ── FEATURE 5: Engine risk score ──
df['engine_risk_score'] = (
    (df['engine_temperature'] / 105)  * 0.6 +
    (df['mileage'] / 100000)          * 0.4
).clip(0, 1)
 
# ── FEATURE 6: Multi-sensor instability (variance) ──
# Normalise each sensor to 0-1 before computing variance
df['brake_temp_norm']  = (df['brake_temperature']  - 70)  / (115 - 70)
df['oil_pres_norm']    = (df['oil_pressure']        - 18)  / (60  - 18)
df['engine_temp_norm'] = (df['engine_temperature']  - 80)  / (115 - 80)
df['tire_pres_norm']   = (df['tire_pressure']       - 22)  / (38  - 22)
norm_cols = ['brake_temp_norm','oil_pres_norm','engine_temp_norm','tire_pres_norm']
df['sensor_variance']  = df[norm_cols].std(axis=1)
df.drop(columns=norm_cols, inplace=True)   # remove temp columns
 
# ── FEATURE 7: Mileage category ──
def mileage_category(m):
    if m > 80000: return 2   # critical
    if m > 50000: return 1   # warning
    return 0                  # healthy
df['mileage_category'] = df['mileage'].apply(mileage_category)
 
# ── FEATURE 8: Driving pattern encoded ──
df['driving_encoded'] = df['driving_pattern'].map({
    'city':    2,
    'mixed':   1,
    'highway': 0,
})
 
os.makedirs('ml/data/processed', exist_ok=True)
df.to_csv('ml/data/processed/features_engineered.csv', index=False)
print(f'Saved: ml/data/processed/features_engineered.csv')
print(f'New shape: {df.shape[0]:,} rows x {df.shape[1]} columns')
print('\nNew features:')
new_cols = ['brake_temp_deviation','oil_pressure_deviation','avg_daily_mileage',
            'brake_risk_score','engine_risk_score','sensor_variance',
            'mileage_category','driving_encoded']
print(df[new_cols].describe().round(3).to_string())
 