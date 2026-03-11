"""Integration test — full system flow from prediction to feedback."""
import pytest
from services.agents.workers.engagement_agent import EngagementAgent
from services.agents.workers.scheduling_agent import SchedulingAgent
from services.agents.workers.feedback_agent import FeedbackAgent
from services.security.ueba.anomaly_detector import AnomalyDetector
from services.security.ueba.alert_manager import handle_anomaly


def test_full_engagement_flow():
    """Test: prediction → call → SMS → email."""
    agent = EngagementAgent(demo_mode=True)
    pred  = {
        "vehicle_id": "VEH_INT_001", "customer_name": "Test Customer",
        "customer_phone": "+910000000000", "customer_email": "test@test.com",
        "component_at_risk": "brakes", "days_until_failure": 7,
        "failure_probability": 0.9,
    }
    result = agent.process_prediction(pred)
    assert result["vehicle_id"] == "VEH_INT_001"
    assert result["call_outcome"] is not None
    assert "transcript" in result


def test_scheduling_flow():
    """Test: booking → cancel → rebook."""
    agent = SchedulingAgent()
    slots = agent.get_available_slots()
    assert len(slots) > 0

    r = agent.book_appointment("VEH_INT_001", "Test Customer", "brakes")
    assert r["success"]
    appt_id = r["appointment"]["appointment_id"]

    cancel = agent.cancel_appointment(appt_id)
    assert cancel["success"]

    r2 = agent.book_appointment("VEH_INT_001", "Test Customer", "brakes")
    assert r2["success"]


def test_feedback_flow():
    """Test: feedback collection → CSV write."""
    agent  = FeedbackAgent(demo_mode=True)
    result = agent.collect_feedback("VEH_INT_001", "Test Customer", "brake service")
    assert 1 <= result["rating"] <= 5
    assert result["sentiment"] in ["positive", "neutral", "negative"]


def test_ueba_flow():
    """Test: normal → anomaly → alert → block."""
    detector = AnomalyDetector()
    for _ in range(10):
        detector.score_action("TestIntAgent", "api_call")

    score = detector.score_action("TestIntAgent", "api_call")
    assert "score" in score
    assert "risk_level" in score

    # Simulate a forced anomaly alert
    fake_anomaly = {
        "agent_name": "TestIntAgent",
        "score": 85,
        "risk_level": "HIGH",
        "action_type": "bulk_data_export",
        "is_anomaly": True,
        "is_critical": False,
    }
    alert = handle_anomaly(fake_anomaly)
    assert "alert_id" in alert
    assert len(alert["actions_taken"]) > 0


if __name__ == "__main__":
    import subprocess
    subprocess.run(["pytest", __file__, "-v", "--tb=short"])