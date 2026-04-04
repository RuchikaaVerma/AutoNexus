import pandas as pd, numpy as np
from datetime import datetime, timedelta
np.random.seed(7)
 
start = datetime(2022, 1, 1)
rows  = []
 
for i in range(730):   # 730 days = exactly 2 years
    d    = start + timedelta(days=i)
    base = 20
 
    if d.month in [11, 12, 1, 2]:   # winter → more breakdowns
        base = 35
    if d.weekday() < 5:              # Mon-Fri busier than weekends
        base += 10
    if d.month in [6, 7]:            # summer spike (AC failures etc.)
        base += 5
 
    rows.append({
        'date':          d.strftime('%Y-%m-%d'),
        'day_of_week':   d.weekday(),
        'month':         d.month,
        'is_weekend':    int(d.weekday() >= 5),
        'is_winter':     int(d.month in [11,12,1,2]),
        'service_count': max(0, int(np.random.poisson(base)))
    })
 
df = pd.DataFrame(rows)
df.to_csv('ml/data/demand_data.csv', index=False)
print(f'✓ Saved: ml/data/demand_data.csv  ({len(df):,} rows)')
print(f'  Average daily demand: {df["service_count"].mean():.1f}')
print(f'  Max demand day:       {df["service_count"].max()}')