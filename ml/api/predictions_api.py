# ml/api/predictions_api.py
# Person 1 imports this file and calls these functions

import joblib, json, os
import numpy as np
import pandas as pd

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _load(rel):
    return joblib.load(os.path.join(_BASE, rel))

try:
    _failure_model = _load('ml/models/brake_failure_model.pkl')
    _label_encoder = _load('ml/models/label_encoder.pkl')
    _anomaly_model = _load('ml/models/anomaly_detector.pkl')
    _demand_model  = _load('ml/models/demand_forecaster.pkl')
    print('[predictions_api] All models loaded.')
except Exception as e:
    print(f'[predictions_api] Warning: {e}')


def predict_failure(vehicle_data: dict) -> dict:
    '''
    INPUT keys:
        brake_temperature    (°C)   healthy: 70-90
        brake_fluid_level    (%)    healthy: 85-100
        oil_pressure         (PSI)  healthy: 38-55
        engine_temperature   (°C)   healthy: 85-100
        tire_pressure        (PSI)  healthy: 30-35
        mileage              (km)   healthy: 0-50000
        days_since_last_service
        vehicle_age
        driving_pattern      (city/mixed/highway)
    OUTPUT keys:
        urgency, failure_probability, days_until_failure,
        component_at_risk, confidence
    '''
    bt  = float(vehicle_data.get('brake_temperature',    80))
    bf  = float(vehicle_data.get('brake_fluid_level',    92))
    op  = float(vehicle_data.get('oil_pressure',         46))
    et  = float(vehicle_data.get('engine_temperature',   92))
    tp  = float(vehicle_data.get('tire_pressure',        32))
    mil = float(vehicle_data.get('mileage',           25000))
    dss = float(vehicle_data.get('days_since_last_service', 90))
    age = float(vehicle_data.get('vehicle_age',            3))
    dp  = str(vehicle_data.get('driving_pattern',    'mixed'))

    # ── Engineered features — matches feature_engineering.py exactly ──
    bt_dev  = bt - 80
    op_dev  = op - 46
    adm     = mil / (age * 365 + 1)

    b_risk  = float(np.clip(
        (bt / 100) * 0.4 + ((100 - bf) / 100) * 0.35 + (mil / 100000) * 0.25,
        0, 1))

    e_risk  = float(np.clip(
        (et / 105) * 0.6 + (mil / 100000) * 0.4,
        0, 1))

    bt_n  = (bt  - 70) / (115 - 70)
    op_n  = (op  - 18) / (60  - 18)
    et_n  = (et  - 80) / (115 - 80)
    tp_n  = (tp  - 22) / (38  - 22)
    s_var = float(np.std([bt_n, op_n, et_n, tp_n]))

    mil_cat = 2 if mil > 80000 else (1 if mil > 50000 else 0)
    dp_enc  = {'city': 2, 'mixed': 1, 'highway': 0}.get(dp, 1)

    # ── DataFrame so feature names match model training ──
    X = pd.DataFrame([{
        'brake_temperature':       bt,
        'brake_fluid_level':       bf,
        'oil_pressure':            op,
        'engine_temperature':      et,
        'tire_pressure':           tp,
        'mileage':                 mil,
        'days_since_last_service': dss,
        'brake_temp_deviation':    bt_dev,
        'oil_pressure_deviation':  op_dev,
        'avg_daily_mileage':       adm,
        'brake_risk_score':        b_risk,
        'engine_risk_score':       e_risk,
        'sensor_variance':         s_var,
        'mileage_category':        mil_cat,
        'driving_encoded':         dp_enc,
    }])

    pred    = _failure_model.predict(X)[0]
    proba   = float(_failure_model.predict_proba(X)[0].max())
    urgency = _label_encoder.inverse_transform([pred])[0]

    days_map = {'CRITICAL': 5, 'HIGH': 10, 'MEDIUM': 22, 'LOW': 90}

    if bt > 100 or bf < 70:
        component = 'brakes'
    elif et > 105:
        component = 'engine'
    elif op < 28:
        component = 'oil_system'
    elif tp < 26:
        component = 'tires'
    elif mil > 80000:
        component = 'general_service'
    else:
        component = 'general'

    return {
        'urgency':             urgency,
        'failure_probability': round(proba * 100, 1),
        'days_until_failure':  days_map.get(urgency, 90),
        'component_at_risk':   component,
        'confidence':          'HIGH' if proba > 0.75 else ('MEDIUM' if proba > 0.5 else 'LOW'),
    }


def detect_anomaly(sensor_data: dict) -> dict:
    '''
    INPUT keys: brake_temp, brake_fluid, oil_pressure,
                engine_temp, tire_pressure, mileage
    OUTPUT keys: is_anomaly (bool), anomaly_score (float), severity (str)
    '''
    X = pd.DataFrame([{
        'brake_temp':    float(sensor_data.get('brake_temp',    80)),
        'brake_fluid':   float(sensor_data.get('brake_fluid',   92)),
        'oil_pressure':  float(sensor_data.get('oil_pressure',  46)),
        'engine_temp':   float(sensor_data.get('engine_temp',   92)),
        'tire_pressure': float(sensor_data.get('tire_pressure', 32)),
        'mileage':       float(sensor_data.get('mileage',    25000)),
    }])
    score      = float(_anomaly_model.score_samples(X)[0])
    is_anomaly = bool(_anomaly_model.predict(X)[0] == -1)
    severity   = 'CRITICAL' if score < -0.3 else ('HIGH' if score < -0.1 else 'NORMAL')
    return {
        'is_anomaly':    is_anomaly,
        'anomaly_score': round(score, 4),
        'severity':      severity,
    }


def predict_service_demand(day_of_week: int, month: int) -> dict:
    '''
    INPUT:  day_of_week (0=Mon...6=Sun), month (1-12)
    OUTPUT: predicted_count, confidence_range
    '''
    X = pd.DataFrame([{
        'day_of_week': day_of_week,
        'month':       month,
        'is_weekend':  int(day_of_week >= 5),
        'is_winter':   int(month in [11, 12, 1, 2]),
    }])
    pred = float(_demand_model.predict(X)[0])
    return {
        'predicted_count':  int(round(pred)),
        'confidence_range': {'low': int(pred * 0.8), 'high': int(pred * 1.2)},
    }


def get_model_info() -> dict:
    try:
        with open(os.path.join(_BASE, 'ml/evaluation/accuracy_report.json')) as f:
            return json.load(f)
    except Exception as e:
        return {'model': 'RandomForestClassifier', 'status': 'loaded', 'error': str(e)}