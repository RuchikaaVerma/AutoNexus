import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
 
from ml.api.predictions_api import predict_failure
from datetime import datetime
 
class DiagnosisAgent:
    def __init__(self):
        self.name = 'DiagnosisAgent'
 
    def diagnose(self, vehicle_id: str, vehicle_data: dict) -> dict:
        '''
        Full failure diagnosis for a vehicle.
        vehicle_data: same keys as predict_failure() input.
        Returns prediction dict for Master Agent to route to Engagement Agent (Person 4).
        '''
        prediction = predict_failure(vehicle_data)
 
        # ── Build human-readable explanation ──
        factors = []
        bt  = float(vehicle_data.get('brake_temperature', 65))
        bf  = float(vehicle_data.get('brake_fluid_level', 80))
        mil = float(vehicle_data.get('mileage', 0))
        et  = float(vehicle_data.get('engine_temperature', 88))
        op  = float(vehicle_data.get('oil_pressure', 4.0))
        dss = float(vehicle_data.get('days_since_last_service', 0))
 
        if bt  > 80:  factors.append(f'Brake temp {bt}°C — {round((bt-65)/65*100)}% above normal baseline')
        if bf  < 50:  factors.append(f'Brake fluid at {bf}% — low (recommended: 55%+)')
        if mil > 50000: factors.append(f'High mileage {mil:,.0f} km — increased wear expected')
        if et  > 100: factors.append(f'Engine temp {et}°C — approaching critical threshold')
        if op  < 2.5: factors.append(f'Oil pressure {op} — below safe minimum (2.5)')
        if dss > 180: factors.append(f'{dss:.0f} days since last service — overdue')
 
        action_map = {
            'CRITICAL': 'Contact customer IMMEDIATELY — brake failure within 7 days',
            'HIGH':     'Schedule service within 14 days',
            'MEDIUM':   'Schedule service within 30 days',
            'LOW':      'Monitor and include in next routine service',
        }
 
        # Customer-friendly explanation (used by Engagement Agent)
        urgency = prediction['urgency']
        friendly_msg = {
            'CRITICAL': f'Your vehicle needs urgent attention. We predict {prediction["component_at_risk"]} failure within {prediction["days_until_failure"]} days.',
            'HIGH':     f'Your {prediction["component_at_risk"]} shows wear and should be serviced within 2 weeks.',
            'MEDIUM':   f'Your vehicle is due for a {prediction["component_at_risk"]} check within the next month.',
            'LOW':      f'Your vehicle is in good health. Next service recommended at usual interval.',
        }.get(urgency, 'Service recommended.')
 
        return {
            'vehicle_id':           vehicle_id,
            'timestamp':            datetime.now().isoformat(),
            'prediction':           prediction,
            'contributing_factors': factors,
            'priority':             urgency,
            'recommended_action':   action_map.get(urgency, 'Monitor'),
            'customer_message':     friendly_msg,
            'next_agent':           'EngagementAgent' if urgency in ['CRITICAL','HIGH'] else 'MonitorAgent'
        }
 
 
# ── Quick self-test ──
if __name__ == '__main__':
    agent  = DiagnosisAgent()
    result = agent.diagnose('VEH001', {
        'brake_temperature':89,'brake_fluid_level':32,'mileage':52000,
        'days_since_last_service':185,'engine_temperature':94,
        'oil_pressure':3.9,'vehicle_age':5,'driving_pattern':'city'
    })
    import json
    print(json.dumps(result, indent=2))