"""
PURPOSE: Core AI agent — contacts customers about vehicle failures via voice+SMS+email.
CONNECTS TO: FILES 1,2,3,4,5,6,7 (all voice+notification), FILE 12 (calendar)
             P1 backend /predict endpoint
"""
import time, logging, json
from datetime import datetime
from services.agents.config.hf_model_config import BACKEND_BASE_URL
from services.voice.call_manager import CallManager, CallOutcome
from services.notifications.sms_sender import send_alert_sms, send_booking_confirmation_sms
from services.notifications.email_sender import send_service_reminder, send_appointment_confirmation_email
from services.notifications.push_notification import send_maintenance_alert

logger = logging.getLogger(__name__)


class EngagementAgent:
    """
    Main customer engagement agent.
    Gets predictions → contacts customer → books appointment → sends confirmations.
    """
    def __init__(self, demo_mode: bool = True):
        self.demo_mode    = demo_mode
        self.call_manager = CallManager(demo_mode=demo_mode)
        self.name         = "EngagementAgent"
        logger.info(f"EngagementAgent initialized | demo_mode={demo_mode}")

    def process_prediction(self, prediction: dict) -> dict:
        """
        Process a single vehicle prediction and engage the customer.
        Args:
            prediction: dict from P1 /predict endpoint e.g.
                {vehicle_id, customer_name, customer_phone, customer_email,
                 component_at_risk, days_until_failure, failure_probability}
        Returns:
            dict with engagement result
        """
        vid       = prediction.get("vehicle_id", "VEH001")
        name      = prediction.get("customer_name", "Customer")
        phone     = prediction.get("customer_phone", "+919999999999")
        email     = prediction.get("customer_email", "customer@example.com")
        component = prediction.get("component_at_risk", "brakes")
        days      = prediction.get("days_until_failure", 7)
        prob      = prediction.get("failure_probability", 0.8)

        logger.info(f"Processing prediction | vehicle={vid} | component={component} | days={days}")

        result = {
            "vehicle_id":   vid,
            "customer":     name,
            "component":    component,
            "days":         days,
            "call_outcome": None,
            "sms_sent":     False,
            "email_sent":   False,
            "timestamp":    datetime.now().isoformat(),
        }

        # Step 1 — Send pre-call SMS alert
        sms_r = send_alert_sms(phone, name, vid, component, days)
        result["sms_sent"] = sms_r["success"]

        # Step 2 — Send pre-call email alert
        email_r = send_service_reminder(email, name, vid, component, days)
        result["email_sent"] = email_r["success"]

        # Step 3 — Make voice call
        def on_booking(vehicle_id, customer_name, component, date, time_slot):
            """Callback fired when customer says yes to booking."""
            logger.info(f"Booking intent received for {vehicle_id}")
            send_booking_confirmation_sms(phone, customer_name, date, time_slot)
            send_appointment_confirmation_email(
                email, customer_name, vehicle_id,
                date, time_slot, "AutoNexus Central", component
            )

        call_record = self.call_manager.make_call(
            vehicle_id         = vid,
            customer_name      = name,
            customer_phone     = phone,
            component          = component,
            days_until_failure = days,
            on_booking_intent  = on_booking,
        )
        result["call_outcome"] = call_record.outcome.value if call_record.outcome else "unknown"
        result["call_duration"] = call_record.duration_sec
        result["transcript"]    = call_record.transcript

        logger.info(f"Engagement complete | vehicle={vid} | outcome={result['call_outcome']}")
        return result

    def run_fleet_engagement(self, predictions: list) -> list:
        """Process a list of vehicle predictions one by one."""
        results = []
        for pred in predictions:
            try:
                r = self.process_prediction(pred)
                results.append(r)
                time.sleep(2)   # Pause between calls
            except Exception as e:
                logger.error(f"Engagement failed for {pred.get('vehicle_id')}: {e}")
                results.append({"error": str(e), **pred})
        return results

    def get_demo_predictions(self) -> list:
        """Sample predictions for demo/testing — simulates P1 API response."""
        return [
            {
                "vehicle_id": "VEH001", "customer_name": "Rahul Sharma",
                "customer_phone": "+919876543210", "customer_email": "rahul@example.com",
                "component_at_risk": "brakes", "days_until_failure": 7,
                "failure_probability": 0.89,
            },
            {
                "vehicle_id": "VEH002", "customer_name": "Priya Singh",
                "customer_phone": "+919123456789", "customer_email": "priya@example.com",
                "component_at_risk": "engine oil", "days_until_failure": 14,
                "failure_probability": 0.72,
            },
        ]


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FILE 8: Engagement Agent — Self Test")
    print("="*60)
    agent = EngagementAgent(demo_mode=True)
    preds = agent.get_demo_predictions()
    print(f"\n[1] Processing {len(preds)} predictions...")
    results = agent.run_fleet_engagement(preds)
    for r in results:
        print(f"\n  Vehicle : {r.get('vehicle_id')}")
        print(f"  Outcome : {r.get('call_outcome')}")
        print(f"  SMS     : {'✅' if r.get('sms_sent') else '⚠️'}")
        print(f"  Email   : {'✅' if r.get('email_sent') else '⚠️'}")
    print("\n  FILE 8 complete! Commit if results shown ✅\n")

