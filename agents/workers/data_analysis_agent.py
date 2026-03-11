# agents/workers/data_analysis_agent.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime
from ml.api.predictions_api import predict_failure, detect_anomaly

BASELINES = {
    'brake_temperature':  {'healthy_min': 70,  'healthy_max': 90,  'warning': 100, 'critical': 100},
    'brake_fluid_level':  {'healthy_min': 85,  'healthy_max': 100, 'warning': 70,  'critical': 70},
    'oil_pressure':       {'healthy_min': 38,  'healthy_max': 55,  'warning': 28,  'critical': 28},
    'engine_temperature': {'healthy_min': 85,  'healthy_max': 100, 'warning': 105, 'critical': 105},
    'tire_pressure':      {'healthy_min': 30,  'healthy_max': 35,  'warning': 26,  'critical': 26},
}
MILEAGE = {'healthy': 50000, 'warning': 80000, 'critical': 80000}

def check_sensor(name, value):
    b = BASELINES[name]
    if name in ['oil_pressure', 'tire_pressure', 'brake_fluid_level']:
        if value < b['critical']: return {'sensor': name, 'value': value, 'status': 'CRITICAL', 'message': f'{name} critically low: {value}'}
        if value < b['warning']:  return {'sensor': name, 'value': value, 'status': 'WARNING',  'message': f'{name} below warning: {value}'}
    else:
        if value > b['critical']: return {'sensor': name, 'value': value, 'status': 'CRITICAL', 'message': f'{name} critically high: {value}'}
        if value > b['warning']:  return {'sensor': name, 'value': value, 'status': 'WARNING',  'message': f'{name} above warning: {value}'}
    return None

def check_mileage(value):
    if value > MILEAGE['critical']: return {'sensor': 'mileage', 'value': value, 'status': 'CRITICAL', 'message': f'Mileage critically high: {value:,} km'}
    if value > MILEAGE['warning']:  return {'sensor': 'mileage', 'value': value, 'status': 'WARNING',  'message': f'Mileage in warning range: {value:,} km'}
    return None

class DataAnalysisAgent:
    def analyze(self, vehicle_id, sensor_data):
        findings = []
        critical_count = 0
        warning_count  = 0

        for sensor in BASELINES:
            if sensor in sensor_data:
                f = check_sensor(sensor, float(sensor_data[sensor]))
                if f:
                    findings.append(f)
                    if f['status'] == 'CRITICAL': critical_count += 1
                    else: warning_count += 1

        if 'mileage' in sensor_data:
            f = check_mileage(float(sensor_data['mileage']))
            if f:
                findings.append(f)
                if f['status'] == 'CRITICAL': critical_count += 1
                else: warning_count += 1

        severity     = min(10, critical_count * 3 + warning_count * 1)
        health_score = max(0, 100 - (critical_count * 25) - (warning_count * 10))

        anomaly_result = detect_anomaly({
            'brake_temp':    sensor_data.get('brake_temperature',    80),
            'brake_fluid':   sensor_data.get('brake_fluid_level',    92),
            'oil_pressure':  sensor_data.get('oil_pressure',         46),
            'engine_temp':   sensor_data.get('engine_temperature',   92),
            'tire_pressure': sensor_data.get('tire_pressure',        32),
            'mileage':       sensor_data.get('mileage',           25000),
        })

        failure_result = predict_failure({**sensor_data, 'vehicle_id': vehicle_id})

        if critical_count >= 2:   rec = 'IMMEDIATE SERVICE REQUIRED - multiple critical sensors'
        elif critical_count == 1: rec = 'URGENT SERVICE - one critical sensor'
        elif warning_count >= 2:  rec = 'Schedule service within 2 weeks'
        elif warning_count == 1:  rec = 'Monitor closely - one warning sensor'
        else:                     rec = 'Vehicle healthy - next check in 30 days'

        return {
            'vehicle_id':       vehicle_id,
            'timestamp':        datetime.now().isoformat(),
            'anomaly_detected':  anomaly_result['is_anomaly'],
            'severity':         severity,
            'health_score':     health_score,
            'critical_count':   critical_count,
            'warning_count':    warning_count,
            'findings':         findings,
            'anomaly_model':    anomaly_result,
            'failure_model':    failure_result,
            'recommendation':   rec,
        }

if __name__ == '__main__':
    agent = DataAnalysisAgent()

    print("=" * 55)
    print("TEST 1 - CRITICAL vehicle (all sensors bad)")
    print("=" * 55)
    r1 = agent.analyze('VEH001', {
        'brake_temperature': 108, 'brake_fluid_level': 58,
        'oil_pressure': 22, 'engine_temperature': 112,
        'tire_pressure': 23, 'mileage': 90000,
        'days_since_last_service': 200, 'vehicle_age': 8, 'driving_pattern': 'city',
    })
    print(f"  Health score:   {r1['health_score']}")
    print(f"  Severity:       {r1['severity']}/10")
    print(f"  Critical count: {r1['critical_count']}")
    print(f"  Warning count:  {r1['warning_count']}")
    print(f"  Anomaly:        {r1['anomaly_model']['is_anomaly']}")
    print(f"  Urgency:        {r1['failure_model']['urgency']}")
    print(f"  Recommend:      {r1['recommendation']}")

    print()
    print("=" * 55)
    print("TEST 2 - WARNING vehicle")
    print("=" * 55)
    r2 = agent.analyze('VEH002', {
        'brake_temperature': 95, 'brake_fluid_level': 72,
        'oil_pressure': 30, 'engine_temperature': 102,
        'tire_pressure': 28, 'mileage': 60000,
        'days_since_last_service': 120, 'vehicle_age': 4, 'driving_pattern': 'mixed',
    })
    print(f"  Health score:   {r2['health_score']}")
    print(f"  Severity:       {r2['severity']}/10")
    print(f"  Critical count: {r2['critical_count']}")
    print(f"  Warning count:  {r2['warning_count']}")
    print(f"  Anomaly:        {r2['anomaly_model']['is_anomaly']}")
    print(f"  Urgency:        {r2['failure_model']['urgency']}")
    print(f"  Recommend:      {r2['recommendation']}")

    print()
    print("=" * 55)
    print("TEST 3 - HEALTHY vehicle")
    print("=" * 55)
    r3 = agent.analyze('VEH003', {
        'brake_temperature': 80, 'brake_fluid_level': 92,
        'oil_pressure': 46, 'engine_temperature': 92,
        'tire_pressure': 32, 'mileage': 25000,
        'days_since_last_service': 60, 'vehicle_age': 3, 'driving_pattern': 'highway',
    })
    print(f"  Health score:   {r3['health_score']}")
    print(f"  Severity:       {r3['severity']}/10")
    print(f"  Critical count: {r3['critical_count']}")
    print(f"  Warning count:  {r3['warning_count']}")
    print(f"  Anomaly:        {r3['anomaly_model']['is_anomaly']}")
    print(f"  Urgency:        {r3['failure_model']['urgency']}")
    print(f"  Recommend:      {r3['recommendation']}")

    print()
    print("DataAnalysisAgent - all 3 tests complete!")
