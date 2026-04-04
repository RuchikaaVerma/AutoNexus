import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime
import numpy as np
from ml.api.predictions_api import predict_failure, detect_anomaly

# ── Sensor thresholds ──
BASELINES = {
    'brake_temperature': {'healthy_min': 70, 'healthy_max': 90, 'warning': 100, 'critical': 100},
    'brake_fluid_level': {'healthy_min': 85, 'healthy_max': 100, 'warning': 70, 'critical': 70},
    'oil_pressure': {'healthy_min': 38, 'healthy_max': 55, 'warning': 28, 'critical': 28},
    'engine_temperature': {'healthy_min': 85, 'healthy_max': 100, 'warning': 105, 'critical': 105},
    'tire_pressure': {'healthy_min': 30, 'healthy_max': 35, 'warning': 26, 'critical': 26},
}

MILEAGE = {'healthy': 50000, 'warning': 80000, 'critical': 80000}


def check_sensor(name, value):
    b = BASELINES[name]
    if name in ['oil_pressure', 'tire_pressure', 'brake_fluid_level']:
        if value < b['critical']:
            return {'sensor': name, 'value': value, 'status': 'CRITICAL',
                    'message': f'{name} is critically low: {value}'}
        if value < b['warning']:
            return {'sensor': name, 'value': value, 'status': 'WARNING',
                    'message': f'{name} is below warning threshold: {value}'}
    else:
        if value > b['critical']:
            return {'sensor': name, 'value': value, 'status': 'CRITICAL',
                    'message': f'{name} is critically high: {value}'}
        if value > b['warning']:
            return {'sensor': name, 'value': value, 'status': 'WARNING',
                    'message': f'{name} is above warning threshold: {value}'}
    return None


def check_mileage(value):
    if value > MILEAGE['critical']:
        return {'sensor': 'mileage', 'value': value, 'status': 'CRITICAL',
                'message': f'Mileage critically high: {value:,} km — major service needed'}
    if value > MILEAGE['warning']:
        return {'sensor': 'mileage', 'value': value, 'status': 'WARNING',
                'message': f'Mileage in warning range: {value:,} km — service due soon'}
    return None


class Person2DataAnalysisAgent:

    def __init__(self):
        self.name = "Person2DataAnalysisAgent"
        self.description = "Advanced analysis with anomaly detection (Person 2)"
        self.call_count = 0

    def _log_call(self):
        self.call_count += 1

    def get_info(self):
        return {
            "name": self.name,
            "description": self.description,
            "total_calls": self.call_count
        }

    def process(self, data: dict) -> dict:
        """Adapter for BaseAgent compatibility"""
        self._log_call()

        vehicle_id = data.get("vehicle_id", "Unknown")
        sensors = data.get("sensors", {})

        # Map your sensor names to Person 2's format
        sensor_data = {
            'brake_temperature': sensors.get('brake_temp', 0),
            'brake_fluid_level': sensors.get('brake_fluid_level', 0),
            'oil_pressure': sensors.get('oil_pressure', 0),
            'engine_temperature': sensors.get('engine_temp', 0),
            'tire_pressure': sensors.get('tire_pressure', 0),
            'mileage': sensors.get('mileage', 0),
            'days_since_last_service': 60,
            'vehicle_age': 3,
            'driving_pattern': 'mixed',
        }

        return self.analyze(vehicle_id, sensor_data)

    def analyze(self, vehicle_id: str, sensor_data: dict) -> dict:
        """Person 2's original analyze method"""

        findings = []
        critical_count = 0
        warning_count = 0

        # Check all 5 sensors
        for sensor in BASELINES:
            if sensor in sensor_data:
                finding = check_sensor(sensor, float(sensor_data[sensor]))
                if finding:
                    findings.append(finding)
                    if finding['status'] == 'CRITICAL':
                        critical_count += 1
                    else:
                        warning_count += 1

        # Check mileage
        if 'mileage' in sensor_data:
            finding = check_mileage(float(sensor_data['mileage']))
            if finding:
                findings.append(finding)
                if finding['status'] == 'CRITICAL':
                    critical_count += 1
                else:
                    warning_count += 1

        # Severity score 0-10
        severity = min(10, critical_count * 3 + warning_count * 1)

        # Health score 0-100
        health_score = max(0, 100 - (critical_count * 25) - (warning_count * 10))

        # Call anomaly model
        anomaly_result = detect_anomaly({
            'brake_temp': sensor_data.get('brake_temperature', 80),
            'brake_fluid': sensor_data.get('brake_fluid_level', 92),
            'oil_pressure': sensor_data.get('oil_pressure', 46),
            'engine_temp': sensor_data.get('engine_temperature', 92),
            'tire_pressure': sensor_data.get('tire_pressure', 32),
            'mileage': sensor_data.get('mileage', 25000),
        })

        # Call failure prediction model
        failure_result = predict_failure({**sensor_data, 'vehicle_id': vehicle_id})

        # Recommendation
        if critical_count >= 2:
            recommendation = 'IMMEDIATE SERVICE REQUIRED — multiple critical sensors'
        elif critical_count == 1:
            recommendation = 'URGENT SERVICE — one critical sensor detected'
        elif warning_count >= 2:
            recommendation = 'Schedule service within 2 weeks — multiple warnings'
        elif warning_count == 1:
            recommendation = 'Monitor closely — one sensor in warning range'
        else:
            recommendation = 'Vehicle healthy — next check in 30 days'

        return {
            'agent': self.name,
            'vehicle_id': vehicle_id,
            'timestamp': datetime.now().isoformat(),
            'anomaly_detected': anomaly_result['is_anomaly'],
            'severity': severity,
            'health_score': health_score,
            'critical_count': critical_count,
            'warning_count': warning_count,
            'findings': findings,
            'anomaly_model': anomaly_result,
            'failure_model': failure_result,
            'recommendation': recommendation,
        }