"""
PURPOSE: Tracks and learns normal agent behaviour for UEBA anomaly detection.
CONNECTS TO: FILE 15 (anomaly_detector), FILE 1 (config)
"""
import json, logging, time
from collections import deque, defaultdict
from datetime import datetime
from services.agents.config.hf_model_config import UEBA_BASELINE_WINDOW_SEC

logger = logging.getLogger(__name__)


class BehaviorBaseline:
    """
    Records agent actions and maintains rolling baseline statistics.
    Stores in memory (Redis optional for production).
    """
    def __init__(self):
        # agent_name -> deque of recent actions
        self._actions: dict = defaultdict(lambda: deque(maxlen=1000))
        self._baselines: dict = {}
        logger.info("BehaviorBaseline initialized")

    def record_action(self, agent_name: str, action_type: str, metadata: dict = None):
        """
        Record one agent action.
        Args:
            agent_name  : e.g. "EngagementAgent"
            action_type : e.g. "api_call", "data_access", "prediction_read"
            metadata    : optional extra info
        """
        record = {
            "timestamp":   time.time(),
            "action_type": action_type,
            "metadata":    metadata or {},
        }
        self._actions[agent_name].append(record)
        logger.debug(f"Action recorded | agent={agent_name} | type={action_type}")

    def get_baseline(self, agent_name: str) -> dict:
        """
        Calculate baseline statistics for an agent from recent history.
        Returns means and std-devs of key metrics.
        """
        actions = list(self._actions[agent_name])
        if not actions:
            return {"agent": agent_name, "sample_count": 0}

        now         = time.time()
        window_acts = [a for a in actions if now - a["timestamp"] <= UEBA_BASELINE_WINDOW_SEC]

        # Count action types
        type_counts: dict = defaultdict(int)
        for a in window_acts:
            type_counts[a["action_type"]] += 1

        # Calculate call rate (actions per minute)
        if len(window_acts) > 1:
            duration_min  = (window_acts[-1]["timestamp"] - window_acts[0]["timestamp"]) / 60
            call_rate_rpm = len(window_acts) / max(duration_min, 0.01)
        else:
            call_rate_rpm = 0

        baseline = {
            "agent":          agent_name,
            "sample_count":   len(window_acts),
            "action_counts":  dict(type_counts),
            "call_rate_rpm":  round(call_rate_rpm, 2),
            "dominant_action": max(type_counts, key=type_counts.get) if type_counts else "none",
            "window_sec":     UEBA_BASELINE_WINDOW_SEC,
            "computed_at":    datetime.now().isoformat(),
        }
        self._baselines[agent_name] = baseline
        return baseline

    def get_all_baselines(self) -> dict:
        return {agent: self.get_baseline(agent) for agent in self._actions}

    def reset_agent(self, agent_name: str):
        self._actions[agent_name].clear()
        self._baselines.pop(agent_name, None)
        logger.info(f"Baseline reset for {agent_name}")


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 14: Behavior Baseline — Self Test")
    print("="*55)
    baseline = BehaviorBaseline()
    # Simulate normal behaviour
    for i in range(30):
        baseline.record_action("EngagementAgent", "api_call",    {"endpoint": "/predict"})
        baseline.record_action("EngagementAgent", "data_access", {"table": "vehicles"})
        time.sleep(0.01)
    stats = baseline.get_baseline("EngagementAgent")
    print(f"\n  Agent         : {stats['agent']}")
    print(f"  Sample count  : {stats['sample_count']}")
    print(f"  Call rate/min : {stats['call_rate_rpm']}")
    print(f"  Action counts : {stats['action_counts']}")
    print("  FILE 14 complete!\n")
