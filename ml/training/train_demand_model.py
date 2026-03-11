import pandas as pd, numpy as np, joblib, os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
 
os.makedirs('ml/models', exist_ok=True)
 
df = pd.read_csv('ml/data/demand_data.csv')
print(f'Loaded: {df.shape}')
 
FEATURES = ['day_of_week', 'month', 'is_weekend', 'is_winter']
X = df[FEATURES]
y = df['service_count']
 
# Last 90 days = test set, everything before = train
X_train, X_test = X.iloc[:-90], X.iloc[-90:]
y_train, y_test = y.iloc[:-90], y.iloc[-90:]
 
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
 
y_pred = model.predict(X_test)
mae    = mean_absolute_error(y_test, y_pred)
print(f'Mean Absolute Error: ±{mae:.1f} appointments/day')
 
joblib.dump(model, 'ml/models/demand_forecaster.pkl')
print('✓ Saved: ml/models/demand_forecaster.pkl')
 
# Quick forecast test
next_week = pd.DataFrame([
    {'day_of_week':0,'month':3,'is_weekend':0,'is_winter':0},  # Monday March
    {'day_of_week':5,'month':3,'is_weekend':1,'is_winter':0},  # Saturday March
    {'day_of_week':1,'month':12,'is_weekend':0,'is_winter':1}, # Tuesday December
])
preds = model.predict(next_week)
print(f'\nSample forecasts:')
print(f'  Monday March:    {preds[0]:.0f} appointments')
print(f'  Saturday March:  {preds[1]:.0f} appointments')
print(f'  Tuesday December:{preds[2]:.0f} appointments (winter spike expected)')