import pandas as pd
import random
from datetime import datetime, timedelta

def generate_feedback_csv(rows=100):
    vehicles = ['VEH001','VEH002','VEH003','VEH004','VEH005']
    issues = ['brake_failure','engine_warning','oil_change','tyre_pressure','battery']

    # Sensor ranges per issue type (realistic values)
    issue_sensor_profiles = {
        'brake_failure':  {'brake_temp': (180, 320), 'brake_fluid': (20, 55),  'oil_pressure': (25, 40), 'engine_temp': (85, 105),  'tyre_pressure': (30, 35), 'mileage': (15000, 80000), 'days_last_service': (90, 365)},
        'engine_warning': {'brake_temp': (60, 120),  'brake_fluid': (60, 90),  'oil_pressure': (10, 25), 'engine_temp': (100, 140), 'tyre_pressure': (29, 35), 'mileage': (20000, 90000), 'days_last_service': (60, 300)},
        'battery':        {'brake_temp': (50, 100),  'brake_fluid': (65, 90),  'oil_pressure': (28, 42), 'engine_temp': (80, 100),  'tyre_pressure': (30, 35), 'mileage': (10000, 70000), 'days_last_service': (30, 200)},
        'oil_change':     {'brake_temp': (55, 110),  'brake_fluid': (60, 88),  'oil_pressure': (8, 22),  'engine_temp': (88, 115),  'tyre_pressure': (29, 35), 'mileage': (8000,  60000), 'days_last_service': (120, 400)},
        'tyre_pressure':  {'brake_temp': (55, 110),  'brake_fluid': (65, 92),  'oil_pressure': (28, 42), 'engine_temp': (80, 100),  'tyre_pressure': (18, 26), 'mileage': (5000,  50000), 'days_last_service': (30, 180)},
    }

    data = []
    for _ in range(rows):
        issue = random.choice(issues)
        p = issue_sensor_profiles[issue]

        # days_until_failure: negative means vehicle already came in for service
        days_until_failure = random.randint(-30, 15) if random.random() > 0.3 else random.randint(16, 90)

        data.append({
            'vehicle_id':             random.choice(vehicles),
            'brake_temperature':      round(random.uniform(*p['brake_temp']), 1),
            'brake_fluid_level':      round(random.uniform(*p['brake_fluid']), 1),
            'oil_pressure':           round(random.uniform(*p['oil_pressure']), 1),
            'engine_temperature':     round(random.uniform(*p['engine_temp']), 1),
            'tyre_pressure':          round(random.uniform(*p['tyre_pressure']), 1),
            'mileage':                random.randint(*p['mileage']),
            'days_since_last_service':random.randint(*p['days_last_service']),
            'days_until_failure':     days_until_failure,
        })

    df = pd.DataFrame(data)
    df.to_csv('ml/data/service_feedback.csv', index=False)
    print(f"Generated {rows} rows in ml/data/service_feedback.csv")
    print(df.head())

if __name__ == "__main__":
    generate_feedback_csv(100)