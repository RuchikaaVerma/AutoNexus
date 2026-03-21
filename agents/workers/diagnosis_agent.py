import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ml.api.predictions_api import predict_failure
from datetime import datetime

class DiagnosisAgent:
    def diagnose(self, vehicle_id, vehicle_data):
        prediction = predict_failure(vehicle_data)
        urgency    = prediction["urgency"]
        comp       = prediction["component_at_risk"]
        days       = prediction["days_until_failure"]

        bt  = float(vehicle_data.get("brake_temperature",  80))
        bf  = float(vehicle_data.get("brake_fluid_level",  92))
        op  = float(vehicle_data.get("oil_pressure",       46))
        et  = float(vehicle_data.get("engine_temperature", 92))
        tp  = float(vehicle_data.get("tire_pressure",      32))
        mil = float(vehicle_data.get("mileage",         25000))
        dss = float(vehicle_data.get("days_since_last_service", 90))

        factors = []
        if bt  > 100: factors.append("Brake temp " + str(bt) + "C - CRITICAL (>100)")
        elif bt > 90: factors.append("Brake temp " + str(bt) + "C - WARNING (90-100)")
        if bf  <  70: factors.append("Brake fluid " + str(bf) + "% - CRITICAL (<70)")
        elif bf < 85: factors.append("Brake fluid " + str(bf) + "% - WARNING (70-85)")
        if op  <  28: factors.append("Oil pressure " + str(op) + " PSI - CRITICAL (<28)")
        elif op < 38: factors.append("Oil pressure " + str(op) + " PSI - WARNING (28-38)")
        if et  > 105: factors.append("Engine temp " + str(et) + "C - CRITICAL (>105)")
        elif et > 100:factors.append("Engine temp " + str(et) + "C - WARNING (100-105)")
        if tp  <  26: factors.append("Tire pressure " + str(tp) + " PSI - CRITICAL (<26)")
        elif tp < 30: factors.append("Tire pressure " + str(tp) + " PSI - WARNING (26-30)")
        if mil > 80000: factors.append("Mileage " + str(int(mil)) + " km - CRITICAL (>80000)")
        elif mil > 50000: factors.append("Mileage " + str(int(mil)) + " km - WARNING (>50000)")
        if dss > 365: factors.append("Days since service " + str(int(dss)) + " - overdue")

        action_map = {
            "CRITICAL": "Contact customer IMMEDIATELY - failure within 7 days",
            "HIGH":     "Schedule service within 14 days",
            "MEDIUM":   "Schedule service within 30 days",
            "LOW":      "Include in next routine service",
        }

        msg_map = {
            "CRITICAL": "Your vehicle needs urgent attention. We predict " + comp + " failure within " + str(days) + " days.",
            "HIGH":     "Your " + comp + " shows wear and should be serviced within 2 weeks.",
            "MEDIUM":   "Your vehicle is due for a " + comp + " check within the next month.",
            "LOW":      "Your vehicle is in good health. Next service at usual interval.",
        }

        return {
            "vehicle_id":           vehicle_id,
            "timestamp":            datetime.now().isoformat(),
            "prediction":           prediction,
            "contributing_factors": factors,
            "priority":             urgency,
            "recommended_action":   action_map.get(urgency, "Monitor"),
            "customer_message":     msg_map.get(urgency, "Service recommended."),
            "next_agent":           "EngagementAgent" if urgency in ["CRITICAL","HIGH"] else "MonitorAgent",
        }

if __name__ == "__main__":
    import json
    agent = DiagnosisAgent()

    print("=" * 55)
    print("TEST 1 - CRITICAL vehicle")
    print("=" * 55)
    r1 = agent.diagnose("VEH001", {
        "brake_temperature": 108, "brake_fluid_level": 58,
        "oil_pressure": 22, "engine_temperature": 112,
        "tire_pressure": 23, "mileage": 90000,
        "days_since_last_service": 200, "vehicle_age": 8,
        "driving_pattern": "city",
    })
    print("  Urgency:  ", r1["priority"])
    print("  Action:   ", r1["recommended_action"])
    print("  Message:  ", r1["customer_message"])
    print("  Factors:  ", r1["contributing_factors"])
    print("  Next:     ", r1["next_agent"])

    print()
    print("=" * 55)
    print("TEST 2 - LOW/healthy vehicle")
    print("=" * 55)
    r2 = agent.diagnose("VEH002", {
        "brake_temperature": 80, "brake_fluid_level": 92,
        "oil_pressure": 46, "engine_temperature": 92,
        "tire_pressure": 32, "mileage": 25000,
        "days_since_last_service": 60, "vehicle_age": 3,
        "driving_pattern": "highway",
    })
    print("  Urgency:  ", r2["priority"])
    print("  Action:   ", r2["recommended_action"])
    print("  Message:  ", r2["customer_message"])
    print("  Next:     ", r2["next_agent"])

    print()
