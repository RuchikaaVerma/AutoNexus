<<<<<<< HEAD
"""
PURPOSE: Background scheduler — sends 24hr and 1hr reminders automatically.
CONNECTS TO: FILE 12 (appointment_manager), FILES 5,6 (SMS+email)
"""
=======
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
import logging, time, threading
from datetime import datetime
from services.calendar.appointment_manager import AppointmentManager
from services.notifications.sms_sender import send_appointment_reminder
from services.notifications.email_sender import send_appointment_confirmation_email

logger     = logging.getLogger(__name__)
_scheduler = None
_running   = False


def _check_and_send_reminders(mgr: AppointmentManager):
    """Check appointments and send reminders as needed."""
    try:
        # 24-hour reminders
        upcoming_24 = mgr.get_upcoming_appointments(hours_ahead=25)
        for appt in upcoming_24:
            if appt.get("reminder_24h") == "pending":
                send_appointment_reminder(
                    to_phone       = appt.get("customer_phone", ""),
                    customer_name  = appt["customer_name"],
                    date           = appt["date"],
                    time_slot      = appt["time_slot"],
                    service_center = appt.get("service_center", "AutoNexus Central"),
                )
                mgr.update_reminder_status(appt["appointment_id"], "24h", "sent")
                logger.info(f"24hr reminder sent | {appt['appointment_id']}")

        # 1-hour reminders
        upcoming_1 = mgr.get_upcoming_appointments(hours_ahead=2)
        for appt in upcoming_1:
            if appt.get("reminder_1h") == "pending":
                send_appointment_reminder(
                    to_phone       = appt.get("customer_phone", ""),
                    customer_name  = appt["customer_name"],
                    date           = appt["date"],
                    time_slot      = appt["time_slot"],
                    service_center = appt.get("service_center", "AutoNexus Central"),
                )
                mgr.update_reminder_status(appt["appointment_id"], "1h", "sent")
                logger.info(f"1hr reminder sent | {appt['appointment_id']}")

    except Exception as e:
        logger.error(f"Reminder check failed: {e}")


def start_scheduler(check_interval_sec: int = 300):
    """Start reminder scheduler as background thread."""
    global _running
    _running = True
    mgr = AppointmentManager()

    def _loop():
        logger.info(f"Reminder scheduler started | interval={check_interval_sec}s")
        while _running:
            _check_and_send_reminders(mgr)
            time.sleep(check_interval_sec)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    logger.info("Reminder scheduler thread running")
    return t


def stop_scheduler():
    global _running
    _running = False
    logger.info("Reminder scheduler stopped")


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 13: Reminder Scheduler — Self Test")
    print("="*55)
    print("\n  Starting scheduler for 3 seconds...")
    t = start_scheduler(check_interval_sec=2)
    time.sleep(3)
    stop_scheduler()
    print("  Scheduler started and stopped ✅")
    print("  FILE 13 complete!\n")
