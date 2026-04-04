import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.api.predictions_api import predict_failure
from datetime import datetime


class Person2DiagnosisAgent:

    def __init__(self):
        self.name = 'Person2DiagnosisAgent'
        self.description = "Comprehensive diagnosis with customer messaging (Person 2)"
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

        # Map to Person 2's format
        vehicle_data = {
            'brake_temperature': sensors.get('brake_temp', 0),
            'brake_fluid_level': sensors.get('brake_fluid_level', 0),
            'oil_pressure': sensors.get('oil_pressure', 0),
            'engine_temperature': sensors.get('engine_temp', 0),
            'tire_pressure': sensors.get('tire_pressure', 0),
            'mileage': sensors.get('mileage', 0),
            'days_since_last_service': 60,
            'vehicle_age': 3,
            'driving_pattern': 'mixed',
            'vehicle_id': vehicle_id,
        }

        return self.diagnose(vehicle_id, vehicle_data)

    def diagnose(self, vehicle_id: str, vehicle_data: dict) -> dict:
        '''Person 2's original diagnose method'''

        prediction = predict_failure(vehicle_data)

        # Build human-readable explanation
        factors = []
        bt = float(vehicle_data.get('brake_temperature', 65))
        bf = float(vehicle_data.get('brake_fluid_level', 80))
        mil = float(vehicle_data.get('mileage', 0))
        et = float(vehicle_data.get('engine_temperature', 88))
        op = float(vehicle_data.get('oil_pressure', 4.0))
        dss = float(vehicle_data.get('days_since_last_service', 0))

        if bt > 80:
            factors.append(f'Brake temp {bt}°C — {round((bt - 65) / 65 * 100)}% above normal baseline')
        if bf < 50:
            factors.append(f'Brake fluid at {bf}% — low (recommended: 55%+)')
        if mil > 50000:
            factors.append(f'High mileage {mil:,.0f} km — increased wear expected')
        if et > 100:
            factors.append(f'Engine temp {et}°C — approaching critical threshold')
        if op < 2.5:
            factors.append(f'Oil pressure {op} — below safe minimum (2.5)')
        if dss > 180:
            factors.append(f'{dss:.0f} days since last service — overdue')

        action_map = {
            'HIGH': 'Contact customer IMMEDIATELY — brake failure within 7 days',
            'MEDIUM': 'Schedule service within 14 days',
            'LOW': 'Schedule service within 30 days',
        }

        # Customer-friendly explanation
        urgency = prediction['urgency']
        friendly_msg = {
            'HIGH': f'Your vehicle needs urgent attention. We predict {prediction["component_at_risk"]} failure within {prediction["days_until_failure"]} days.',
            'MEDIUM': f'Your {prediction["component_at_risk"]} shows wear and should be serviced within 2 weeks.',
            'LOW': f'Your vehicle is in good health. Next service recommended at usual interval.',
        }.get(urgency, 'Service recommended.')

        return {
            'agent': self.name,
            'vehicle_id': vehicle_id,
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'contributing_factors': factors,
            'priority': urgency,
            'recommended_action': action_map.get(urgency, 'Monitor'),
            'customer_message': friendly_msg,
            'next_agent': 'EngagementAgent' if urgency in ['HIGH'] else 'MonitorAgent'
        }