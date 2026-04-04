<<<<<<< HEAD
"""
FILE 5: services/notifications/sms_sender.py
PURPOSE: Sends SMS messages via Twilio API.
CONNECTS TO:
  - services/agents/workers/engagement_agent.py (FILE 8)
  - services/calendar/reminder_scheduler.py     (FILE 13)
  - services/agents/config/hf_model_config.py   (FILE 1)
AUTHOR: Person 4
"""

=======
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
import logging
from datetime import datetime
from services.agents.config.hf_model_config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
)

logger = logging.getLogger(__name__)


def _get_client():
    try:
        from twilio.rest import Client
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
            raise ValueError("Twilio credentials missing in .env")
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except ImportError:
        raise ImportError("twilio not installed: pip install twilio")


def send_sms(to_phone: str, message: str) -> dict:
    """
    Send a plain SMS to any phone number.
    Args:
        to_phone: recipient number e.g. "+919876543210"
        message : text content (max 160 chars for single SMS)
    Returns:
        dict with success, sid, error
    """
    if not to_phone or not message:
        return {"success": False, "error": "Phone or message is empty"}

    # DEMO MODE — if no Twilio creds, simulate sending
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logger.warning(f"[DEMO] SMS to {to_phone}: {message[:60]}...")
        return {
            "success": True,
            "sid":     "DEMO_SID_12345",
            "demo":    True,
        }

    try:
        client = _get_client()
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone,
        )
        logger.info(f"SMS sent | to={to_phone} | sid={msg.sid}")
        return {"success": True, "sid": msg.sid, "demo": False}
    except Exception as e:
        logger.error(f"SMS failed to {to_phone}: {e}")
        return {"success": False, "error": str(e)}


def send_appointment_reminder(
    to_phone: str,
    customer_name: str,
    date: str,
    time_slot: str,
    service_center: str,
) -> dict:
    """Send appointment reminder SMS."""
    message = (
        f"Hi {customer_name}! Reminder: Your AutoNexus service appointment "
        f"is on {date} at {time_slot} at {service_center}. "
        f"Reply CANCEL to cancel. AutoNexus Team."
    )
    return send_sms(to_phone, message)


def send_alert_sms(
    to_phone: str,
    customer_name: str,
    vehicle_id: str,
    component: str,
    days: int,
) -> dict:
    """Send vehicle failure alert SMS."""
    message = (
        f"Hi {customer_name}, AutoNexus Alert: Your vehicle {vehicle_id} "
        f"{component} needs attention within {days} days. "
        f"Call us to book: 1800-AUTO-NEX"
    )
    return send_sms(to_phone, message)


def send_booking_confirmation_sms(
    to_phone: str,
    customer_name: str,
    date: str,
    time_slot: str,
) -> dict:
    """Send booking confirmation SMS."""
    message = (
        f"Confirmed! Hi {customer_name}, your AutoNexus service is booked "
        f"for {date} at {time_slot}. We look forward to seeing you!"
    )
    return send_sms(to_phone, message)


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 5: SMS Sender — Self Test")
    print("="*55)

    print("\n[1] Testing plain SMS (demo mode if no Twilio creds)...")
    r1 = send_sms("+919876543210", "Test SMS from AutoNexus system.")
    print(f"    Result: {'✅ SUCCESS' if r1['success'] else '❌ FAILED'}")
    print(f"    Demo  : {r1.get('demo', False)}")

    print("\n[2] Testing appointment reminder SMS...")
    r2 = send_appointment_reminder(
        to_phone       = "+919876543210",
        customer_name  = "Rahul Sharma",
        date           = "Monday March 10",
        time_slot      = "10:00 AM",
        service_center = "AutoNexus Central",
    )
    print(f"    Result: {'✅ SUCCESS' if r2['success'] else '❌ FAILED'}")

    print("\n[3] Testing alert SMS...")
    r3 = send_alert_sms(
        to_phone      = "+919876543210",
        customer_name = "Rahul Sharma",
        vehicle_id    = "VEH001",
        component     = "brakes",
        days          = 7,
    )
    print(f"    Result: {'✅ SUCCESS' if r3['success'] else '❌ FAILED'}")

    print("\n" + "="*55)
    print("  FILE 5 complete! Commit if all ✅")
    print("="*55 + "\n")