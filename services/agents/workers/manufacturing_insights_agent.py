"""
PURPOSE: AI agent for Root Cause Analysis and CAPA using HuggingFace LLM.
CONNECTS TO: FILES 1,18,19 (rca+capa), ml/evaluation/accuracy_report.json (P2)
"""
import json, logging
from pathlib import Path
from datetime import datetime
from services.agents.config.hf_model_config import (
    MANUFACTURING_MODEL, HF_TOKEN, HF_RUN_MODE, ML_EVAL_DIR
)

logger = logging.getLogger(__name__)


class ManufacturingInsightsAgent:
    """Generates RCA and CAPA reports using AI."""

    FAILURE_KNOWLEDGE = {
        "brakes": {
            "causes":      ["worn brake pads", "low brake fluid", "overheating", "caliper sticking"],
            "corrective":  ["replace brake pads", "top up brake fluid", "inspect calipers"],
            "preventive":  ["monthly brake fluid check", "brake inspection every 10,000km"],
        },
        "engine": {
            "causes":      ["overheating", "low oil pressure", "coolant leak", "timing belt wear"],
            "corrective":  ["replace coolant", "oil change", "timing belt replacement"],
            "preventive":  ["regular oil changes", "coolant flush every 2 years"],
        },
        "engine oil": {
            "causes":      ["oil degradation", "extended service interval", "high mileage"],
            "corrective":  ["immediate oil and filter change"],
            "preventive":  ["oil change every 5,000km or 3 months"],
        },
        "tires": {
            "causes":      ["underinflation", "misalignment", "worn tread"],
            "corrective":  ["rotate tires", "alignment check", "replace worn tires"],
            "preventive":  ["monthly pressure check", "rotation every 8,000km"],
        },
    }

    def __init__(self):
        self.name = "ManufacturingInsightsAgent"
        logger.info("ManufacturingInsightsAgent initialized")

    def analyze_failure(self, vehicle_id: str, component: str, sensor_data: dict = None) -> dict:
        """
        Analyze a vehicle failure and return RCA + CAPA.
        Uses knowledge base (always works) + optional LLM enrichment.
        """
        logger.info(f"Analyzing failure | vehicle={vehicle_id} | component={component}")
        comp_key  = component.lower()
        knowledge = self.FAILURE_KNOWLEDGE.get(comp_key, self.FAILURE_KNOWLEDGE["engine"])

        # Build RCA
        rca = {
            "vehicle_id":    vehicle_id,
            "component":     component,
            "timestamp":     datetime.now().isoformat(),
            "root_causes":   knowledge["causes"],
            "primary_cause": knowledge["causes"][0],
            "sensor_data":   sensor_data or {},
            "severity":      self._calculate_severity(sensor_data),
        }

        # Build CAPA
        capa = {
            "corrective_actions": knowledge["corrective"],
            "preventive_actions": knowledge["preventive"],
            "priority":           "HIGH" if rca["severity"] > 7 else "MEDIUM",
            "deadline_days":      7 if rca["severity"] > 7 else 14,
        }

        # Try LLM enrichment (optional — works without it)
        llm_insight = self._get_llm_insight(component, rca["primary_cause"])
        if llm_insight:
            rca["ai_insight"] = llm_insight

        result = {"rca": rca, "capa": capa, "success": True}
        logger.info(f"Analysis complete | severity={rca['severity']} | priority={capa['priority']}")
        return result

    def _calculate_severity(self, sensor_data: dict) -> int:
        """Score severity 1-10 from sensor readings."""
        if not sensor_data:
            return 5
        score = 5
        if sensor_data.get("brake_temp", 0) > 90:   score += 2
        if sensor_data.get("brake_fluid", 100) < 30: score += 2
        if sensor_data.get("oil_pressure", 40) < 25: score += 1
        return min(score, 10)

    def _get_llm_insight(self, component: str, cause: str) -> str:
        """Optional LLM enrichment — returns empty string if unavailable."""
        if not HF_TOKEN or HF_RUN_MODE != "api":
            return ""
        try:
            from langchain_huggingface import HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                repo_id=MANUFACTURING_MODEL,
                huggingfacehub_api_token=HF_TOKEN,
                max_new_tokens=100,
            )
            prompt = (
                f"In one sentence, explain why {cause} causes {component} failure "
                f"in a vehicle and what the immediate risk is."
            )
            return llm.invoke(prompt).strip()
        except Exception as e:
            logger.debug(f"LLM insight skipped: {e}")
            return ""

    def read_ml_accuracy(self) -> dict:
        """Read P2's model accuracy report."""
        report_path = ML_EVAL_DIR / "accuracy_report.json"
        if report_path.exists():
            with open(report_path) as f:
                return json.load(f)
        return {"note": "P2 accuracy report not yet generated"}


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 11: Manufacturing Insights Agent — Self Test")
    print("="*55)
    agent = ManufacturingInsightsAgent()
    result = agent.analyze_failure(
        vehicle_id  = "VEH001",
        component   = "brakes",
        sensor_data = {"brake_temp": 95, "brake_fluid": 25, "oil_pressure": 35},
    )
    rca  = result["rca"]
    capa = result["capa"]
    print(f"\n  Vehicle      : {rca['vehicle_id']}")
    print(f"  Component    : {rca['component']}")
    print(f"  Primary Cause: {rca['primary_cause']}")
    print(f"  Severity     : {rca['severity']}/10")
    print(f"  Priority     : {capa['priority']}")
    print(f"  Corrective   : {capa['corrective_actions'][0]}")
    print(f"  Preventive   : {capa['preventive_actions'][0]}")
    print("\n  FILE 11 complete!\n")
