"""
PURPOSE: Permission matrix — which agent can access which resource.
CONNECTS TO: FILE 16 (alert_manager), FILE 1 (config)
"""
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

# Permission matrix: agent -> set of allowed resources
PERMISSION_MATRIX = {
    "EngagementAgent": {
        "predictions", "vehicles", "appointments",
        "sms", "email", "push",
    },
    "SchedulingAgent": {
        "appointments", "vehicles", "calendar",
        "sms", "email",
    },
    "FeedbackAgent": {
        "feedback_data", "vehicles", "appointments",
        "sms", "email",
    },
    "ManufacturingInsightsAgent": {
        "predictions", "vehicles", "ml_models",
        "accuracy_reports", "rca_data", "capa_data",
    },
    "UEBASystem": {
        "agent_logs", "behavior_data", "alert_logs",
        "all_agents",
    },
}

_access_log: list = []


def check_permission(agent_name: str, resource: str) -> dict:
    """
    Check if an agent is allowed to access a resource.
    Returns dict with allowed bool and reason.
    """
    allowed_resources = PERMISSION_MATRIX.get(agent_name, set())
    allowed = resource in allowed_resources

    entry = {
        "timestamp":  datetime.now().isoformat(),
        "agent":      agent_name,
        "resource":   resource,
        "allowed":    allowed,
        "reason":     "in permission matrix" if allowed else "not in permission matrix",
    }
    _access_log.append(entry)

    if not allowed:
        logger.warning(f"ACCESS DENIED | agent={agent_name} | resource={resource}")
    else:
        logger.debug(f"Access granted | agent={agent_name} | resource={resource}")

    return entry


def get_agent_permissions(agent_name: str) -> list:
    return list(PERMISSION_MATRIX.get(agent_name, set()))


def grant_access(agent_name: str, resource: str):
    if agent_name not in PERMISSION_MATRIX:
        PERMISSION_MATRIX[agent_name] = set()
    PERMISSION_MATRIX[agent_name].add(resource)
    logger.info(f"Access granted | agent={agent_name} | resource={resource}")


def revoke_access(agent_name: str, resource: str):
    if agent_name in PERMISSION_MATRIX:
        PERMISSION_MATRIX[agent_name].discard(resource)
        logger.info(f"Access revoked | agent={agent_name} | resource={resource}")


def get_access_log() -> list:
    return _access_log.copy()


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 17: Access Control — Self Test")
    print("="*55)
    tests = [
        ("EngagementAgent",          "predictions",  True),
        ("EngagementAgent",          "ueba_logs",    False),
        ("SchedulingAgent",          "appointments", True),
        ("ManufacturingInsightsAgent","ml_models",   True),
        ("FeedbackAgent",            "admin_panel",  False),
    ]
    for agent, resource, expected in tests:
        result  = check_permission(agent, resource)
        correct = result["allowed"] == expected
        print(f"  {'✅' if correct else '❌'} {agent:<30} -> {resource:<20}: {result['allowed']}")
    print("  FILE 17 complete!\n")