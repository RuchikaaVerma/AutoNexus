"""
PURPOSE: Firebase push notifications to mobile app.
CONNECTS TO: engagement_agent.py (FILE 8), alert_manager.py (FILE 16)
"""
import logging
from services.agents.config.hf_model_config import FIREBASE_SERVER_KEY
logger = logging.getLogger(__name__)

def send_push(device_token: str, title: str, body: str, data: dict = None) -> dict:
    if not FIREBASE_SERVER_KEY:
        logger.warning(f"[DEMO] Push | title={title} | body={body[:50]}")
        print(f"  🔔 [DEMO PUSH] {title}: {body}")
        return {"success": True, "demo": True}
    try:
        from pyfcm import FCMNotification
        push = FCMNotification(api_key=FIREBASE_SERVER_KEY)
        result = push.notify_single_device(
            registration_id=device_token,
            message_title=title,
            message_body=body,
            data_message=data or {},
        )
        logger.info(f"Push sent | token={device_token[:20]}... | result={result}")
        return {"success": True, "result": result, "demo": False}
    except Exception as e:
        logger.error(f"Push failed: {e}")
        return {"success": False, "error": str(e)}

def send_maintenance_alert(device_token: str, vehicle_id: str, component: str, days: int) -> dict:
    return send_push(
        device_token=device_token,
        title=f"⚠️ Vehicle {vehicle_id} Alert",
        body=f"Your {component} needs attention within {days} days.",
        data={"vehicle_id": vehicle_id, "component": component, "days": str(days)},
    )

def send_appointment_push(device_token: str, customer_name: str, date: str, time_slot: str) -> dict:
    return send_push(
        device_token=device_token,
        title="✅ Appointment Confirmed",
        body=f"Hi {customer_name}! Your service is booked for {date} at {time_slot}.",
        data={"type": "appointment_confirmation", "date": date},
    )

def send_ueba_push(device_token: str, agent_name: str, score: int) -> dict:
    return send_push(
        device_token=device_token,
        title="🔐 Security Alert",
        body=f"Agent {agent_name} flagged with risk score {score}/100.",
        data={"type": "ueba_alert", "agent": agent_name, "score": str(score)},
    )

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 7: Push Notification — Self Test")
    print("="*55)
    r1 = send_maintenance_alert("DEMO_TOKEN", "VEH001", "brakes", 7)
    print(f"  Alert push : {'✅' if r1['success'] else '❌'}")
    r2 = send_appointment_push("DEMO_TOKEN", "Rahul", "Monday", "10 AM")
    print(f"  Appt push  : {'✅' if r2['success'] else '❌'}")
    r3 = send_ueba_push("DEMO_TOKEN", "EngagementAgent", 85)
    print(f"  UEBA push  : {'✅' if r3['success'] else '❌'}")
    print("  FILE 7 complete! Commit if all ✅\n")
