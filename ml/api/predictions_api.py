"""
Predictions API - Bridge between Person 2's code and your ML model
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml_predictor import MLPredictor

# Initialize ML predictor
ml_predictor = MLPredictor(repo_id="divyanshi-02/autonexus-p2-ml-models")


def predict_failure(vehicle_data: dict) -> dict:
    """
    Bridge function for Person 2's code
    Connects to your ml_predictor
    """

    # Map sensor names
    mapped_data = {
        'brake_temp': vehicle_data.get('brake_temperature', 65),
        'oil_pressure': vehicle_data.get('oil_pressure', 40),
        'engine_temp': vehicle_data.get('engine_temperature', 90),
        'tire_pressure': vehicle_data.get('tire_pressure', 32),
        'brake_fluid_level': vehicle_data.get('brake_fluid_level', 100),
        'mileage': vehicle_data.get('mileage', 0),
    }

    # Use your ML model
    prediction = ml_predictor.predict(mapped_data)

    # Determine component at risk
    brake_temp = mapped_data['brake_temp']
    oil_pressure = mapped_data['oil_pressure']
    brake_fluid = mapped_data['brake_fluid_level']

    if brake_temp > 100 or brake_fluid < 70:
        component = 'brake system'
    elif oil_pressure < 25:
        component = 'engine lubrication'
    else:
        component = 'general components'

    # Map risk level to urgency
    risk = prediction.get('risk_level', 'LOW')
    if risk == 'HIGH':
        days = 7
    elif risk == 'MEDIUM':
        days = 14
    else:
        days = 30

    # Return in Person 2's expected format
    return {
        'urgency': risk,
        'component_at_risk': component,
        'days_until_failure': days,
        'failure_probability': prediction.get('failure_probability', 0),
        'confidence': prediction.get('confidence', 0),
        'prediction': prediction.get('prediction', 'NO FAILURE'),
    }


def detect_anomaly(sensor_data: dict) -> dict:
    """
    Simple anomaly detection
    """

    is_anomaly = False
    anomalies = []

    if sensor_data.get('brake_temp', 0) > 95:
        is_anomaly = True
        anomalies.append('brake_temp_high')

    if sensor_data.get('oil_pressure', 0) < 30:
        is_anomaly = True
        anomalies.append('oil_pressure_low')

    if sensor_data.get('engine_temp', 0) > 102:
        is_anomaly = True
        anomalies.append('engine_temp_high')

    if sensor_data.get('brake_fluid', 0) < 75:
        is_anomaly = True
        anomalies.append('brake_fluid_low')

    if sensor_data.get('tire_pressure', 0) < 28:
        is_anomaly = True
        anomalies.append('tire_pressure_low')

    return {
        'is_anomaly': is_anomaly,
        'anomalies': anomalies,
        'anomaly_count': len(anomalies),
        'confidence': 0.85 if is_anomaly else 0.95
    }