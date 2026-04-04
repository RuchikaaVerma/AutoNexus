"""
PURPOSE: Takes action when anomaly detected — logs, alerts, blocks, isolates.
CONNECTS TO: FILES 14,15 (baseline+detector), FILES 5,6,7 (notifications), P1+P3
"""
import json, logging
from datetime import datetime
from pathlib import Path
from services.agents.config.hf_model_config import (
    UEBA_ANOMALY_THRESHOLD, UEBA_CRITICAL_THRESHOLD, ALERTS_URL
)

logger    = logging.getLogger(__name__)
LOG_FILE  = Path("logs/ueba_alerts.log")
LOG_FILE.parent.mkdir(exist_ok=True)

# In-memory blocked agents set
_blocked_agents: set = set()
_alert_history: list = []


def handle_anomaly(score_result: dict) -> dict:
    """
    Main entry point — called whenever anomaly detector flags something.
    Args:
        score_result: output dict from anomaly_detector.score_action()
    Returns:
        dict with actions taken
    """
    if not score_result.get("is_anomaly"):
        return {"action": "none", "reason": "below threshold"}

    agent  = score_result["agent_name"]
    score  = score_result["score"]
    level  = score_result["risk_level"]

    alert = {
        "alert_id":    f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "agent":       agent,
        "score":       score,
        "risk_level":  level,
        "action_type": score_result["action_type"],
        "timestamp":   datetime.now().isoformat(),
        "actions_taken": [],
    }

    # Log the alert
    _log_alert(alert)
    alert["actions_taken"].append("logged")

    # Notify P3 dashboard
    _notify_dashboard(alert)
    alert["actions_taken"].append("dashboard_notified")

    # Notify P1 backend
    _notify_backend(alert)
    alert["actions_taken"].append("backend_notified")

    # Block if critical
    if score_result.get("is_critical"):
        block_agent(agent)
        alert["actions_taken"].append("agent_blocked")
        logger.critical(f"Agent BLOCKED | {agent} | score={score}")

    _alert_history.append(alert)
    logger.warning(f"Alert handled | id={alert['alert_id']} | agent={agent} | actions={alert['actions_taken']}")
    return alert


def block_agent(agent_name: str):
    """Add agent to blocked set."""
    _blocked_agents.add(agent_name)
    logger.warning(f"Agent blocked: {agent_name}")


def unblock_agent(agent_name: str):
    """Remove agent from blocked set."""
    _blocked_agents.discard(agent_name)
    logger.info(f"Agent unblocked: {agent_name}")


def is_blocked(agent_name: str) -> bool:
    return agent_name in _blocked_agents


def get_alert_history() -> list:
    return _alert_history.copy()


def _log_alert(alert: dict):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(alert) + "\n")
    except Exception as e:
        logger.error(f"Alert log write failed: {e}")


def _notify_dashboard(alert: dict):
    """Send alert to P3 frontend via WebSocket (demo: just logs)."""
    logger.info(f"[P3 Dashboard] UEBA alert sent: {alert['alert_id']}")
    print(f"  📊 Dashboard notified: {alert['risk_level']} alert for {alert['agent']}")


def _notify_backend(alert: dict):
    """POST alert to P1 backend (demo: just logs)."""
    logger.info(f"[P1 Backend] UEBA alert posted to {ALERTS_URL}: {alert['alert_id']}")


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 16: Alert Manager — Self Test")
    print("="*55)
    from services.security.ueba.anomaly_detector import AnomalyDetector
    detector = AnomalyDetector()
    # Trigger anomaly
    score_result = detector.score_action("EngagementAgent", "admin_override", {"reason": "test"})
    score_result["is_anomaly"] = True   # Force for test
    score_result["is_critical"] = score_result["score"] >= UEBA_CRITICAL_THRESHOLD
    alert = handle_anomaly(score_result)
    print(f"\n  Alert ID : {alert['alert_id']}")
    print(f"  Actions  : {alert['actions_taken']}")
    print(f"  Blocked  : {is_blocked('EngagementAgent')}")
    unblock_agent("EngagementAgent")
    print(f"  Unblocked: {not is_blocked('EngagementAgent')}")
<<<<<<< HEAD
    print("  FILE 16 complete!\n")

    # ==============================
    # FASTAPI ROUTER (FOR API)
    # ==============================

from fastapi import APIRouter

router = APIRouter()


@router.get("/alerts")
def get_alerts():
    return {
            "total_alerts": len(_alert_history),
            "alerts": _alert_history
        }


@router.get("/blocked")
def get_blocked_agents():
    return {
            "blocked_agents": list(_blocked_agents),
            "count": len(_blocked_agents)
        }


@router.post("/unblock/{agent_name}")
def unblock(agent_name: str):
    unblock_agent(agent_name)
    return {"message": f"{agent_name} unblocked"}


@router.get("/status")
def ueba_status():
    return {
            "alerts": len(_alert_history),
            "blocked_agents": list(_blocked_agents),
            "system": "UEBA active"
        }
=======
    print("  FILE 16 complete!\n")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
