"""
PURPOSE: Generates Corrective Action / Preventive Action plans from RCA output.
CONNECTS TO: FILE 18 (rca_engine), FILE 20 (report_generator), FILE 11
"""
import logging
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

CAPA_DATABASE = {
    "Worn brake pads": {
        "corrective":  ["Replace brake pads immediately", "Inspect rotors for warping", "Bleed brake lines"],
        "preventive":  ["Inspect brake pads every 10,000km", "Use high-quality OEM pads"],
        "cost_est":    "₹2,500 – ₹4,000",
        "time_est":    "2–3 hours",
    },
    "Low brake fluid": {
        "corrective":  ["Top up brake fluid to MAX line", "Inspect for leaks in brake lines"],
        "preventive":  ["Check fluid level monthly", "Replace fluid every 2 years"],
        "cost_est":    "₹500 – ₹800",
        "time_est":    "30 minutes",
    },
    "Coolant system failure": {
        "corrective":  ["Flush and refill coolant", "Pressure test cooling system", "Inspect radiator cap"],
        "preventive":  ["Coolant flush every 2 years", "Check coolant level weekly in summer"],
        "cost_est":    "₹1,500 – ₹3,000",
        "time_est":    "1–2 hours",
    },
    "Oil pressure drop": {
        "corrective":  ["Immediate oil change", "Replace oil filter", "Check for oil leaks"],
        "preventive":  ["Oil change every 5,000km", "Use manufacturer-specified oil grade"],
        "cost_est":    "₹800 – ₹1,500",
        "time_est":    "1 hour",
    },
    "Oil degradation": {
        "corrective":  ["Oil and filter change immediately"],
        "preventive":  ["Adhere to 5,000km / 3-month oil change schedule"],
        "cost_est":    "₹800 – ₹1,200",
        "time_est":    "45 minutes",
    },
    "Underinflation": {
        "corrective":  ["Inflate all tires to recommended PSI", "Inspect for punctures"],
        "preventive":  ["Check tire pressure monthly", "Inspect tires before long trips"],
        "cost_est":    "₹0 – ₹200",
        "time_est":    "15 minutes",
    },
}
DEFAULT_CAPA = {
    "corrective":  ["Schedule full vehicle inspection", "Consult manufacturer service manual"],
    "preventive":  ["Follow manufacturer service schedule", "Regular diagnostic scans"],
    "cost_est":    "₹1,000 – ₹5,000",
    "time_est":    "Variable",
}


class CAPAGenerator:
    """Generates CAPA plans from RCA analysis output."""

    def generate(self, rca_result: dict) -> dict:
        """
        Generate CAPA from RCA output.
        Args:
            rca_result: output dict from RCAEngine.analyze()
        """
        primary_cause = rca_result.get("primary_cause", "")
        severity      = rca_result.get("severity", "MEDIUM")
        component     = rca_result.get("component", "unknown")

        db_entry   = CAPA_DATABASE.get(primary_cause, DEFAULT_CAPA)
        priority   = "IMMEDIATE" if severity == "CRITICAL" else ("HIGH" if severity == "HIGH" else "MEDIUM")
        deadline   = datetime.now() + timedelta(days=1 if severity == "CRITICAL" else (7 if severity == "HIGH" else 14))

        capa = {
            "vehicle_id":         rca_result.get("vehicle_id"),
            "component":          component,
            "primary_cause":      primary_cause,
            "priority":           priority,
            "corrective_actions": db_entry["corrective"],
            "preventive_actions": db_entry["preventive"],
            "estimated_cost":     db_entry["cost_est"],
            "estimated_time":     db_entry["time_est"],
            "deadline":           deadline.strftime("%Y-%m-%d"),
            "generated_at":       datetime.now().isoformat(),
            "status":             "open",
        }
        logger.info(
            f"CAPA generated | vehicle={capa['vehicle_id']} | "
            f"priority={priority} | deadline={capa['deadline']}"
        )
        return capa


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 19: CAPA Generator — Self Test")
    print("="*55)
    from services.manufacturing.rca_engine import RCAEngine
    rca_result = RCAEngine().analyze("VEH001", "brakes", {"brake_temp": 95, "brake_fluid": 25})
    gen        = CAPAGenerator()
    capa       = gen.generate(rca_result)
    print(f"\n  Priority   : {capa['priority']}")
    print(f"  Deadline   : {capa['deadline']}")
    print(f"  Cost est.  : {capa['estimated_cost']}")
    print(f"  Time est.  : {capa['estimated_time']}")
    print(f"  Corrective : {capa['corrective_actions'][0]}")
    print(f"  Preventive : {capa['preventive_actions'][0]}")
    print("  FILE 19 complete!\n")