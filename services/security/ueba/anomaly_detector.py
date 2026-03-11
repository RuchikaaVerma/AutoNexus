"""
PURPOSE: Scores agent actions 0-100 for suspiciousness using Isolation Forest.
CONNECTS TO: FILE 14 (behavior_baseline), FILE 16 (alert_manager), FILE 1
"""
import logging
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from services.agents.config.hf_model_config import (
    UEBA_ANOMALY_THRESHOLD, UEBA_CRITICAL_THRESHOLD
)
from services.security.ueba.behavior_baseline import BehaviorBaseline

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detects anomalous agent behaviour using Isolation Forest + rule-based scoring.
    """
    def __init__(self, baseline: BehaviorBaseline = None):
        self.baseline  = baseline or BehaviorBaseline()
        self._models: dict = {}   # agent_name -> trained IsolationForest
        logger.info("AnomalyDetector initialized")

    def score_action(self, agent_name: str, action_type: str, metadata: dict = None) -> dict:
        """
        Score a single agent action for anomaly.
        Returns score 0-100 (higher = more suspicious).
        """
        # Record the action first
        self.baseline.record_action(agent_name, action_type, metadata or {})

        # Rule-based scoring (fast, always works)
        rule_score = self._rule_based_score(agent_name, action_type, metadata or {})

        # ML-based scoring (needs enough history)
        ml_score   = self._ml_score(agent_name)

        # Weighted combination
        final_score = int(0.4 * rule_score + 0.6 * ml_score)
        risk_level  = self._risk_level(final_score)

        result = {
            "agent_name":  agent_name,
            "action_type": action_type,
            "score":       final_score,
            "rule_score":  rule_score,
            "ml_score":    ml_score,
            "risk_level":  risk_level,
            "is_anomaly":  final_score >= UEBA_ANOMALY_THRESHOLD,
            "is_critical": final_score >= UEBA_CRITICAL_THRESHOLD,
            "timestamp":   datetime.now().isoformat(),
        }
        if result["is_anomaly"]:
            logger.warning(
                f"ANOMALY DETECTED | agent={agent_name} | score={final_score} | "
                f"action={action_type} | level={risk_level}"
            )
        return result

    def _rule_based_score(self, agent_name: str, action_type: str, metadata: dict) -> int:
        """Fast keyword-based scoring rules."""
        score = 0
        # Suspicious action types
        suspicious = {
            "bulk_data_export": 40, "schema_access": 30, "admin_override": 50,
            "repeated_failure": 25, "off_hours_access": 20, "unusual_endpoint": 35,
        }
        score += suspicious.get(action_type, 0)

        # High frequency check
        b = self.baseline.get_baseline(agent_name)
        if b.get("call_rate_rpm", 0) > 60:   # More than 60 calls/min
            score += 30
        elif b.get("call_rate_rpm", 0) > 30:
            score += 15

        return min(score, 100)

    def _ml_score(self, agent_name: str) -> int:
        """Isolation Forest anomaly scoring."""
        b       = self.baseline.get_baseline(agent_name)
        samples = b.get("sample_count", 0)

        if samples < 10:
            return 20   # Not enough data — return low default

        try:
            counts  = b.get("action_counts", {})
            feature = np.array([[
                b.get("call_rate_rpm", 0),
                counts.get("api_call", 0),
                counts.get("data_access", 0),
                counts.get("bulk_data_export", 0),
                counts.get("admin_override", 0),
            ]])

            if agent_name not in self._models:
                # Train on normal data (first time)
                normal = np.random.normal(loc=[5, 20, 10, 0, 0], scale=[2, 5, 3, 0.1, 0.1], size=(100, 5))
                normal = np.clip(normal, 0, None)
                self._models[agent_name] = IsolationForest(contamination=0.1, random_state=42)
                self._models[agent_name].fit(normal)

            raw_score   = self._models[agent_name].score_samples(feature)[0]
            # Convert: score_samples returns negative values, more negative = more anomalous
            # Map [-0.5, 0] range to [0, 100]
            normalized  = int(min(100, max(0, (-raw_score) * 200)))
            return normalized

        except Exception as e:
            logger.debug(f"ML score failed (using rule-based only): {e}")
            return 20

    def _risk_level(self, score: int) -> str:
        if score >= UEBA_CRITICAL_THRESHOLD: return "CRITICAL"
        if score >= UEBA_ANOMALY_THRESHOLD:  return "HIGH"
        if score >= 40:                      return "MEDIUM"
        return "LOW"


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 15: Anomaly Detector — Self Test")
    print("="*55)
    detector = AnomalyDetector()
    # Warm up with normal actions
    for _ in range(20):
        detector.score_action("EngagementAgent", "api_call")
        detector.score_action("EngagementAgent", "data_access")

    print("\n  Normal actions:")
    r = detector.score_action("EngagementAgent", "api_call")
    print(f"    api_call     : score={r['score']} | level={r['risk_level']} | anomaly={r['is_anomaly']}")

    print("\n  Suspicious actions:")
    r2 = detector.score_action("EngagementAgent", "bulk_data_export")
    print(f"    bulk_export  : score={r2['score']} | level={r2['risk_level']} | anomaly={r2['is_anomaly']}")
    r3 = detector.score_action("EngagementAgent", "admin_override")
    print(f"    admin_override: score={r3['score']} | level={r3['risk_level']} | anomaly={r3['is_anomaly']}")
    print("  FILE 15 complete!\n")