# ml/training/generate_training_data.py
# RUN: python ml/training/generate_training_data.py
# APPROACH: Generate exactly 3000 rows per urgency class = 12000 total

import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

data = []

def make_row(urgency_target):
    vehicle_age     = random.randint(1, 10)
    days_since_svc  = random.randint(0, 365)
    driving_pattern = random.choice(['city', 'highway', 'mixed'])

    if urgency_target == 'CRITICAL':
        # days 1-7 — sensors clearly bad
        days_fail = random.randint(1, 7)
        prob      = round(random.uniform(75, 99), 1)
        # Pick one critical failure scenario randomly
        scenario  = random.choice(['brake', 'engine', 'oil', 'tire'])
        if scenario == 'brake':
            brake_temp    = round(random.uniform(101, 115), 1)
            brake_fluid   = round(random.uniform(50,   69), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)   # healthy
            engine_temp   = round(random.uniform(85,  100), 1)   # healthy
            tire_pressure = round(random.uniform(30,   35), 1)   # healthy
            mileage       = random.randint(5000, 50000)
            comp          = 'brakes'
        elif scenario == 'engine':
            brake_temp    = round(random.uniform(70,   90), 1)   # healthy
            brake_fluid   = round(random.uniform(85,  100), 1)   # healthy
            oil_pressure  = round(random.uniform(38,   55), 1)   # healthy
            engine_temp   = round(random.uniform(106, 115), 1)
            tire_pressure = round(random.uniform(30,   35), 1)   # healthy
            mileage       = random.randint(5000, 50000)
            comp          = 'engine'
        elif scenario == 'oil':
            brake_temp    = round(random.uniform(70,   90), 1)   # healthy
            brake_fluid   = round(random.uniform(85,  100), 1)   # healthy
            oil_pressure  = round(random.uniform(18,   27), 1)
            engine_temp   = round(random.uniform(85,  100), 1)   # healthy
            tire_pressure = round(random.uniform(30,   35), 1)   # healthy
            mileage       = random.randint(5000, 50000)
            comp          = 'oil_system'
        else:
            brake_temp    = round(random.uniform(70,   90), 1)   # healthy
            brake_fluid   = round(random.uniform(85,  100), 1)   # healthy
            oil_pressure  = round(random.uniform(38,   55), 1)   # healthy
            engine_temp   = round(random.uniform(85,  100), 1)   # healthy
            tire_pressure = round(random.uniform(20,   25), 1)
            mileage       = random.randint(5000, 50000)
            comp          = 'tires'

    elif urgency_target == 'HIGH':
        # days 8-14 — sensors in warning range
        days_fail = random.randint(8, 14)
        prob      = round(random.uniform(50, 79), 1)
        scenario  = random.choice(['brake_temp', 'brake_fluid', 'mileage', 'oil_warn', 'engine_warn'])
        if scenario == 'brake_temp':
            brake_temp    = round(random.uniform(91,  100), 1)
            brake_fluid   = round(random.uniform(75,  100), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(5000, 79999)
            comp          = 'brakes'
        elif scenario == 'brake_fluid':
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(55,   69), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(5000, 79999)
            comp          = 'brakes'
        elif scenario == 'mileage':
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(85,  100), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(80001, 100000)
            comp          = 'general_service'
        elif scenario == 'oil_warn':
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(85,  100), 1)
            oil_pressure  = round(random.uniform(28,   34), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(5000, 79999)
            comp          = 'oil_system'
        else:
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(85,  100), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(101, 105), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(5000, 79999)
            comp          = 'engine'

    elif urgency_target == 'MEDIUM':
        # days 15-30 — sensors mildly out of range
        days_fail = random.randint(15, 30)
        prob      = round(random.uniform(25, 55), 1)
        scenario  = random.choice(['tire_warn', 'oil_mild', 'mileage_mid', 'engine_mild', 'brake_mild'])
        if scenario == 'tire_warn':
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(85,  100), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(26,   29), 1)
            mileage       = random.randint(5000, 79999)
            comp          = 'tires'
        elif scenario == 'oil_mild':
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(85,  100), 1)
            oil_pressure  = round(random.uniform(34,   37), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(5000, 79999)
            comp          = 'oil_system'
        elif scenario == 'mileage_mid':
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(85,  100), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(50001, 80000)
            comp          = 'general_service'
        elif scenario == 'engine_mild':
            brake_temp    = round(random.uniform(70,   90), 1)
            brake_fluid   = round(random.uniform(85,  100), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(100, 105), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(5000, 49999)
            comp          = 'engine'
        else:
            brake_temp    = round(random.uniform(91,   99), 1)
            brake_fluid   = round(random.uniform(72,   84), 1)
            oil_pressure  = round(random.uniform(38,   55), 1)
            engine_temp   = round(random.uniform(85,  100), 1)
            tire_pressure = round(random.uniform(30,   35), 1)
            mileage       = random.randint(5000, 49999)
            comp          = 'brakes'

    else:  # LOW
        # days 31+ — all sensors healthy
        days_fail     = random.randint(31, 180)
        prob          = round(random.uniform(1, 24), 1)
        brake_temp    = round(random.uniform(70,   90), 1)
        brake_fluid   = round(random.uniform(85,  100), 1)
        oil_pressure  = round(random.uniform(38,   55), 1)
        engine_temp   = round(random.uniform(85,  100), 1)
        tire_pressure = round(random.uniform(30,   35), 1)
        mileage       = random.randint(5000, 49999)
        comp          = 'none'

    return {
        'vehicle_age':             vehicle_age,
        'mileage':                 mileage,
        'days_since_last_service': days_since_svc,
        'oil_pressure':            oil_pressure,
        'engine_temperature':      engine_temp,
        'tire_pressure':           tire_pressure,
        'brake_fluid_level':       brake_fluid,
        'brake_temperature':       brake_temp,
        'driving_pattern':         driving_pattern,
        'days_until_failure':      days_fail,
        'failure_probability':     prob,
        'component_at_risk':       comp,
    }

# ── Generate exactly 3000 rows per class ──
for urgency_class in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    for _ in range(3000):
        data.append(make_row(urgency_class))

# Shuffle so classes are mixed
random.shuffle(data)

df = pd.DataFrame(data)
df.to_csv('ml/data/training_data.csv', index=False)
print(f'Saved: ml/data/training_data.csv  ({len(df):,} rows)')

def urgency(d):
    if d <= 7:  return 'CRITICAL'
    if d <= 14: return 'HIGH'
    if d <= 30: return 'MEDIUM'
    return 'LOW'

df['urgency_preview'] = df['days_until_failure'].apply(urgency)
print('\nUrgency distribution (must show ~3000 each):')
print(df['urgency_preview'].value_counts())
print('\nComponent breakdown:')
print(df['component_at_risk'].value_counts())