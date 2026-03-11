# services/demo/demo_scenarios.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── SCENARIO DEFINITIONS ──────────────────────────────────────────────────────

SCENARIOS = {
    1: {
        "name":        "Brake Failure Detection & Customer Engagement",
        "description": "ML detects brake failure → Agent calls customer → Appointment booked",
        "duration":    45,
        "vehicle_id":  "VEH001",
        "customer":    "Rahul Sharma",
        "phone":       "+919876543210",
        "issue":       "brake_failure",
        "severity":    "CRITICAL",
    },
    2: {
        "name":        "Appointment Management & Report Generation",
        "description": "Manage service appointment → Collect feedback → Generate CAPA PDF",
        "duration":    30,
        "vehicle_id":  "VEH002",
        "customer":    "Priya Singh",
        "phone":       "+919123456789",
        "issue":       "oil_change",
        "severity":    "LOW",
    },
    3: {
        "name":        "UEBA Security — Anomaly Detection & Response",
        "description": "Agent behaves suspiciously → UEBA detects → Blocks + alerts dashboard",
        "duration":    30,
        "vehicle_id":  "VEH003",
        "customer":    "Amit Kumar",
        "phone":       "+919988776655",
        "issue":       "engine_warning",
        "severity":    "HIGH",
    },
}


def get_scenario(scenario_id: int) -> dict:
    """Get scenario by ID"""
    if scenario_id not in SCENARIOS:
        raise ValueError(f"Scenario {scenario_id} not found. Choose 1, 2, or 3.")
    return SCENARIOS[scenario_id]


def list_scenarios():
    """Print all available scenarios"""
    print("\n" + "="*60)
    print("  AVAILABLE DEMO SCENARIOS")
    print("="*60)
    for sid, s in SCENARIOS.items():
        print(f"\n  Scenario {sid}: {s['name']}")
        print(f"  Description: {s['description']}")
        print(f"  Duration:    ~{s['duration']} seconds")
        print(f"  Vehicle:     {s['vehicle_id']} — {s['customer']}")
        print(f"  Issue:       {s['issue']} ({s['severity']})")
    print("\n" + "="*60)


def get_scenario_summary(result: dict) -> str:
    """Format scenario result for display"""
    return (
        f"\n  ✅ Scenario {result.get('scenario_id')} COMPLETE\n"
        f"  Name     : {result.get('name')}\n"
        f"  Status   : {result.get('status')}\n"
        f"  Duration : {result.get('duration', 0):.1f}s\n"
        f"  Outcome  : {result.get('outcome', 'N/A')}\n"
    )


if __name__ == "__main__":
    list_scenarios()
    print("\nScenarios loaded successfully!")
    print(f"Total scenarios: {len(SCENARIOS)}")