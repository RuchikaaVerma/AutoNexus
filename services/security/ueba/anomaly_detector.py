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

# Minimum samples before ML model is trained on REAL baseline data
MIN_BASELINE_SAMPLES = 30


class AnomalyDetector:
    """
    Detects anomalous agent behaviour using Isolation Forest + rule-based scoring.
    """
    def __init__(self, baseline: BehaviorBaseline = None):
        self.baseline  = baseline or BehaviorBaseline()
        self._models: dict  = {}          # agent_name -> trained IsolationForest
        self._trained: dict = {}          # agent_name -> bool (trained on real data)
        self._building_baseline = set()   # agents currently in baseline phase
        logger.info("AnomalyDetector initialized")

    def start_baseline(self, agent_name: str):
        """
        Call this before recording baseline actions.
        Suppresses anomaly warnings during the learning phase.
        """
        self._building_baseline.add(agent_name)
        logger.info(f"Baseline phase started for {agent_name} — anomaly warnings suppressed")

    def finish_baseline(self, agent_name: str):
        """
        Call this after baseline recording is complete.
        Trains the Isolation Forest on the REAL collected baseline data.
        Re-enables anomaly warnings.
        """
        self._building_baseline.discard(agent_name)
        self._train_on_real_baseline(agent_name)
        logger.info(f"Baseline phase complete for {agent_name} — anomaly detection active")

    def _train_on_real_baseline(self, agent_name: str):
        """Train Isolation Forest on the agent's actual observed behaviour."""
        b       = self.baseline.get_baseline(agent_name)
        samples = b.get("sample_count", 0)

        if samples < MIN_BASELINE_SAMPLES:
            logger.debug(f"Not enough samples to train on real data ({samples} < {MIN_BASELINE_SAMPLES})")
            return

        # Build synthetic training data centred on THIS agent's real behaviour
        real_rate         = b.get("call_rate_rpm", 0)
        counts            = b.get("action_counts", {})
        real_api_calls    = counts.get("api_call", 0)
        real_data_access  = counts.get("data_access", 0)

        # Generate 200 "normal" samples around the observed baseline
        # Small std = tight normal zone, so real anomalies stand out clearly
        normal_data = np.random.normal(
            loc=[real_rate, real_api_calls, real_data_access, 0, 0],
            scale=[
                max(real_rate * 0.2, 1),        # 20% variance on call rate
                max(real_api_calls * 0.2, 1),   # 20% variance on api_call count
                max(real_data_access * 0.2, 1), # 20% variance on data_access count
                0.1,                             # bulk_data_export should always be ~0
                0.1,                             # admin_override should always be ~0
            ],
            size=(200, 5)
        )
        normal_data = np.clip(normal_data, 0, None)

        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(normal_data)
        self._models[agent_name]  = model
        self._trained[agent_name] = True
        logger.info(f"IsolationForest trained on real baseline for {agent_name} | rate={real_rate:.1f}rpm")

    def score_action(self, agent_name: str, action_type: str, metadata: dict = None) -> dict:
        """
        Score a single agent action for anomaly.
        Returns score 0-100 (higher = more suspicious).
        During baseline phase: records action silently, returns score=0.
        """
        # Record the action
        self.baseline.record_action(agent_name, action_type, metadata or {})

        # --- BASELINE PHASE: silent recording, no alerts ---
        if agent_name in self._building_baseline:
            return {
                "agent_name":  agent_name,
                "action_type": action_type,
                "score":       0,
                "rule_score":  0,
                "ml_score":    0,
                "risk_level":  "LOW",
                "is_anomaly":  False,
                "is_critical": False,
                "timestamp":   datetime.now().isoformat(),
                "note":        "baseline_phase",
            }

        # Rule-based scoring (fast, always works)
        rule_score = self._rule_based_score(agent_name, action_type, metadata or {})

        # ML-based scoring (only after real baseline is trained)
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
        suspicious = {
            "bulk_data_export": 40, "schema_access": 30, "admin_override": 50,
            "repeated_failure": 25, "off_hours_access": 20, "unusual_endpoint": 35,
        }
        score += suspicious.get(action_type, 0)

        # High frequency check — only flag if ABOVE baseline rate
        b             = self.baseline.get_baseline(agent_name)
        baseline_rate = b.get("call_rate_rpm", 0)
        current_rate  = b.get("current_rate_rpm", baseline_rate)

        if current_rate > baseline_rate * 3:    # 3x the normal rate = suspicious
            score += 30
        elif current_rate > baseline_rate * 2:  # 2x the normal rate = mild concern
            score += 15

        return min(score, 100)

    def _ml_score(self, agent_name: str) -> int:
        """Isolation Forest anomaly scoring using real baseline."""
        b       = self.baseline.get_baseline(agent_name)
        samples = b.get("sample_count", 0)

        # Not enough data yet — return neutral score
        if samples < MIN_BASELINE_SAMPLES:
            return 10

        # Model not trained yet — train it now
        if agent_name not in self._models:
            self._train_on_real_baseline(agent_name)

        # Still no model (training failed) — fall back to neutral
        if agent_name not in self._models:
            return 10

        try:
            counts  = b.get("action_counts", {})
            feature = np.array([[
                b.get("call_rate_rpm", 0),
                counts.get("api_call", 0),
                counts.get("data_access", 0),
                counts.get("bulk_data_export", 0),
                counts.get("admin_override", 0),
            ]])

            raw_score  = self._models[agent_name].score_samples(feature)[0]
            # score_samples returns negative values — more negative = more anomalous
            # Map [-0.5, 0] → [0, 100]
            normalized = int(min(100, max(0, (-raw_score) * 200)))
            return normalized

        except Exception as e:
            logger.debug(f"ML score failed (using rule-based only): {e}")
            return 10

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

    # ── Baseline phase (silent — no warnings) ──────────────────
    print("\n  [Phase 1] Building baseline (no warnings should appear)...")
    detector.start_baseline("EngagementAgent")
    for _ in range(50):
        detector.score_action("EngagementAgent", "api_call")
        detector.score_action("EngagementAgent", "data_access")
    detector.finish_baseline("EngagementAgent")
    print("  ✅ Baseline built silently")

    # ── Normal actions (should be LOW) ─────────────────────────
    print("\n  [Phase 2] Normal actions (should be LOW):")
    r = detector.score_action("EngagementAgent", "api_call")
    print(f"    api_call      : score={r['score']} | level={r['risk_level']} | anomaly={r['is_anomaly']}")
    r2 = detector.score_action("EngagementAgent", "data_access")
    print(f"    data_access   : score={r2['score']} | level={r2['risk_level']} | anomaly={r2['is_anomaly']}")

    # ── Suspicious actions (should be HIGH/CRITICAL) ────────────
    print("\n  [Phase 3] Suspicious actions (should be HIGH or CRITICAL):")
    r3 = detector.score_action("EngagementAgent", "bulk_data_export")
    print(f"    bulk_export   : score={r3['score']} | level={r3['risk_level']} | anomaly={r3['is_anomaly']}")
    r4 = detector.score_action("EngagementAgent", "admin_override")
    print(f"    admin_override: score={r4['score']} | level={r4['risk_level']} | anomaly={r4['is_anomaly']}")

    print("\n  FILE 15 complete!\n")