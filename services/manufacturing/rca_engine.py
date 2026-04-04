"""
PURPOSE: Root Cause Analysis — determines WHY a vehicle failure occurred.
CONNECTS TO: FILE 11 (manufacturing_insights_agent), FILE 19 (capa_generator)
"""
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

FAILURE_TREES = {
    "brakes": [
        {"cause": "Worn brake pads",       "probability": 0.45, "evidence": "high brake_temp, vibration"},
        {"cause": "Low brake fluid",        "probability": 0.30, "evidence": "brake_fluid_level < 40%"},
        {"cause": "Sticking brake caliper", "probability": 0.15, "evidence": "uneven braking force"},
        {"cause": "Warped rotors",          "probability": 0.10, "evidence": "steering wheel vibration"},
    ],
    "engine": [
        {"cause": "Coolant system failure", "probability": 0.35, "evidence": "high engine_temp"},
        {"cause": "Oil pressure drop",      "probability": 0.30, "evidence": "low oil_pressure"},
        {"cause": "Timing belt wear",       "probability": 0.20, "evidence": "unusual engine noise"},
        {"cause": "Fuel system issue",      "probability": 0.15, "evidence": "rough idle"},
    ],
    "engine oil": [
        {"cause": "Oil degradation",        "probability": 0.50, "evidence": "high mileage since service"},
        {"cause": "Oil leak",               "probability": 0.30, "evidence": "oil_pressure drop"},
        {"cause": "Wrong oil grade",        "probability": 0.20, "evidence": "unusual consumption"},
    ],
    "tires": [
        {"cause": "Underinflation",         "probability": 0.40, "evidence": "tire_pressure_avg < 28 PSI"},
        {"cause": "Tread wear",             "probability": 0.35, "evidence": "high mileage"},
        {"cause": "Wheel misalignment",     "probability": 0.25, "evidence": "uneven wear pattern"},
    ],
}


class RCAEngine:
    """Root Cause Analysis engine for vehicle failures."""

    def analyze(self, vehicle_id: str, component: str, sensor_data: dict = None) -> dict:
        """
        Perform root cause analysis.
        Returns ranked list of probable causes with evidence.
        """
        comp_key = component.lower()
        tree     = FAILURE_TREES.get(comp_key, FAILURE_TREES["engine"])
        sd       = sensor_data or {}

        # Adjust probabilities based on sensor data
        adjusted = self._adjust_probabilities(tree, comp_key, sd)
        # Sort by probability
        ranked   = sorted(adjusted, key=lambda x: x["probability"], reverse=True)

        rca = {
            "vehicle_id":    vehicle_id,
            "component":     component,
            "sensor_data":   sd,
            "cause_tree":    ranked,
            "primary_cause": ranked[0]["cause"],
            "confidence":    round(ranked[0]["probability"] * 100),
            "severity":      self._severity(sd, comp_key),
            "analyzed_at":   datetime.now().isoformat(),
        }
        logger.info(
            f"RCA complete | vehicle={vehicle_id} | component={component} | "
            f"primary_cause={rca['primary_cause']} | confidence={rca['confidence']}%"
        )
        return rca

    def _adjust_probabilities(self, tree: list, component: str, sd: dict) -> list:
        adjusted = []
        for item in tree:
            prob = item["probability"]
            if component == "brakes":
                if sd.get("brake_temp", 0) > 90 and "pad" in item["cause"].lower():   prob *= 1.5
                if sd.get("brake_fluid", 100) < 35 and "fluid" in item["cause"].lower(): prob *= 1.4
            elif component == "engine":
                if sd.get("engine_temperature", 0) > 105 and "coolant" in item["cause"].lower(): prob *= 1.5
                if sd.get("oil_pressure", 40) < 25 and "oil" in item["cause"].lower(): prob *= 1.4
            adjusted.append({**item, "probability": round(min(prob, 0.99), 2)})
        return adjusted

    def _severity(self, sd: dict, component: str) -> str:
        score = 0
        if sd.get("brake_temp", 0) > 90:       score += 2
        if sd.get("brake_fluid", 100) < 30:    score += 2
        if sd.get("oil_pressure", 40) < 25:    score += 2
        if sd.get("engine_temperature", 0) > 105: score += 3
        if score >= 5:   return "CRITICAL"
        if score >= 3:   return "HIGH"
        if score >= 1:   return "MEDIUM"
        return "LOW"


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 18: RCA Engine — Self Test")
    print("="*55)
    engine = RCAEngine()
    result = engine.analyze("VEH001", "brakes",
                             {"brake_temp": 95, "brake_fluid": 25})
    print(f"\n  Primary cause : {result['primary_cause']}")
    print(f"  Confidence    : {result['confidence']}%")
    print(f"  Severity      : {result['severity']}")
    print(f"  All causes:")
    for c in result["cause_tree"]:
        print(f"    {c['probability']*100:.0f}% — {c['cause']}")
    print("  FILE 18 complete!\n")