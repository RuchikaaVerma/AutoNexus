import sys, os
sys.path.insert(0, os.path.abspath("."))
from ml.api.predictions_api import predict_failure, detect_anomaly, predict_service_demand
from agents.workers.data_analysis_agent import DataAnalysisAgent
from agents.workers.diagnosis_agent import DiagnosisAgent
passed = 0
failed = 0
def check(name, condition, got=None):
    global passed, failed
    if condition:
        print("  PASS:", name); passed += 1
    else:
        print("  FAIL:", name, "got:", got); failed += 1
print()
print("=" * 55)
print("TEST 1 - predict_failure()")
print("=" * 55)
r = predict_failure({"brake_temperature": 108, "brake_fluid_level": 58, "oil_pressure": 22, "engine_temperature": 112, "tire_pressure": 23, "mileage": 90000, "days_since_last_service": 200, "vehicle_age": 8, "driving_pattern": "city"})
print(" Result:", r)
check("urgency is CRITICAL or HIGH", r["urgency"] in ["CRITICAL","HIGH"], r["urgency"])
check("failure_probability > 50", r["failure_probability"] > 50, r["failure_probability"])
check("component_at_risk is set", r["component_at_risk"] not in ["","general"], r["component_at_risk"])
check("days_until_failure <= 14", r["days_until_failure"] <= 14, r["days_until_failure"])
print()
print("=" * 55)
print("TEST 2 - detect_anomaly()")
print("=" * 55)
normal = detect_anomaly({"brake_temp": 80, "brake_fluid": 92, "oil_pressure": 46, "engine_temp": 92, "tire_pressure": 32, "mileage": 25000})
danger = detect_anomaly({"brake_temp": 108, "brake_fluid": 55, "oil_pressure": 22, "engine_temp": 112, "tire_pressure": 23, "mileage": 90000})
print(" Normal:", normal)
print(" Danger:", danger)
check("danger is_anomaly = True", danger["is_anomaly"] == True, danger["is_anomaly"])
check("normal score > danger score", normal["anomaly_score"] > danger["anomaly_score"])
check("anomaly_score is float", isinstance(normal["anomaly_score"], float))
print()
print("=" * 55)
print("TEST 3 - predict_service_demand()")
print("=" * 55)
d = predict_service_demand(0, 3)
print(" Result:", d)
check("predicted_count > 0", d["predicted_count"] > 0, d["predicted_count"])
check("confidence_range has low/high", "low" in d["confidence_range"] and "high" in d["confidence_range"])
print()
print("=" * 55)
print("TEST 4 - DataAnalysisAgent")
print("=" * 55)
agent = DataAnalysisAgent()
r4 = agent.analyze("VEH001", {"brake_temperature": 108, "brake_fluid_level": 58, "oil_pressure": 22, "engine_temperature": 112, "tire_pressure": 23, "mileage": 90000, "days_since_last_service": 200, "vehicle_age": 8, "driving_pattern": "city"})
print(" Health:", r4["health_score"], " Severity:", r4["severity"], " Critical:", r4["critical_count"])
check("health_score < 60", r4["health_score"] < 60, r4["health_score"])
check("severity >= 5", r4["severity"] >= 5, r4["severity"])
check("critical_count >= 1", r4["critical_count"] >= 1, r4["critical_count"])
check("findings not empty", len(r4["findings"]) > 0)
print()
print("=" * 55)
print("TEST 5 - DiagnosisAgent")
print("=" * 55)
diagent = DiagnosisAgent()
r5 = diagent.diagnose("VEH001", {"brake_temperature": 108, "brake_fluid_level": 58, "oil_pressure": 22, "engine_temperature": 112, "tire_pressure": 23, "mileage": 90000, "days_since_last_service": 200, "vehicle_age": 8, "driving_pattern": "city"})
print(" Priority:", r5["priority"])
print(" Next agent:", r5["next_agent"])
print(" Message:", r5["customer_message"])
check("priority is CRITICAL or HIGH", r5["priority"] in ["CRITICAL","HIGH"], r5["priority"])
check("next_agent is EngagementAgent", r5["next_agent"] == "EngagementAgent", r5["next_agent"])
check("customer_message not empty", len(r5["customer_message"]) > 10)
check("contributing_factors not empty", len(r5["contributing_factors"]) > 0)
print()
print("=" * 55)
print("RESULTS:", passed, "passed /", failed, "failed / 15 total")
print("=" * 55)
if failed == 0:
    print("ALL TESTS PASSED - Person 2 ML pipeline complete!")
else:
    print(str(failed) + " test(s) failed")
