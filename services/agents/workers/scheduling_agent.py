"""
PURPOSE: Books, cancels, reschedules service appointments.
CONNECTS TO: FILE 12 (appointment_manager), FILE 1 (config), P1 backend
"""
import logging
from datetime import datetime, timedelta
from services.agents.config.hf_model_config import BACKEND_BASE_URL

logger = logging.getLogger(__name__)

# In-memory appointment store (replaced by DB in FILE 12)
_appointments: dict = {}
_slot_counter: int  = 1


class SchedulingAgent:
    """Books and manages service appointments."""

    AVAILABLE_SLOTS = [
        "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"
    ]
    SERVICE_CENTER  = "AutoNexus Central"

    def __init__(self):
        self.name = "SchedulingAgent"
        logger.info("SchedulingAgent initialized")

    def get_available_slots(self, date: str = None) -> list:
        """Return available time slots for a given date."""
        target = date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        booked = {
            a["time_slot"] for a in _appointments.values()
            if a["date"] == target and a["status"] == "confirmed"
        }
        available = [s for s in self.AVAILABLE_SLOTS if s not in booked]
        logger.info(f"Available slots for {target}: {available}")
        return available

    def book_appointment(
        self,
        vehicle_id: str,
        customer_name: str,
        component: str,
        date: str = None,
        time_slot: str = None,
    ) -> dict:
        """Book a service appointment."""
        global _slot_counter
        target_date = date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slots = self.get_available_slots(target_date)

        if not slots:
            logger.warning(f"No slots available for {target_date}")
            return {"success": False, "error": "No slots available"}

        chosen_slot = time_slot if time_slot in slots else slots[0]
        appt_id     = f"APPT_{_slot_counter:04d}"
        _slot_counter += 1

        appointment = {
            "appointment_id": appt_id,
            "vehicle_id":     vehicle_id,
            "customer_name":  customer_name,
            "component":      component,
            "date":           target_date,
            "time_slot":      chosen_slot,
            "service_center": self.SERVICE_CENTER,
            "status":         "confirmed",
            "created_at":     datetime.now().isoformat(),
        }
        _appointments[appt_id] = appointment
        logger.info(f"Appointment booked | id={appt_id} | {customer_name} | {target_date} {chosen_slot}")
        return {"success": True, "appointment": appointment}

    def cancel_appointment(self, appointment_id: str) -> dict:
        """Cancel an existing appointment."""
        if appointment_id not in _appointments:
            return {"success": False, "error": f"{appointment_id} not found"}
        _appointments[appointment_id]["status"] = "cancelled"
        logger.info(f"Appointment cancelled | id={appointment_id}")
        return {"success": True, "appointment_id": appointment_id}

    def get_appointments(self, vehicle_id: str = None) -> list:
        """Get all appointments, optionally filtered by vehicle."""
        appts = list(_appointments.values())
        if vehicle_id:
            appts = [a for a in appts if a["vehicle_id"] == vehicle_id]
        return appts

    def reschedule_appointment(self, appointment_id: str, new_date: str, new_slot: str) -> dict:
        """Reschedule an existing appointment."""
        if appointment_id not in _appointments:
            return {"success": False, "error": "Not found"}
        _appointments[appointment_id]["date"]      = new_date
        _appointments[appointment_id]["time_slot"] = new_slot
        _appointments[appointment_id]["status"]    = "rescheduled"
        logger.info(f"Rescheduled {appointment_id} to {new_date} {new_slot}")
        return {"success": True, "appointment": _appointments[appointment_id]}


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 9: Scheduling Agent — Self Test")
    print("="*55)
    agent = SchedulingAgent()
    print("\n[1] Available slots:", agent.get_available_slots())
    r = agent.book_appointment("VEH001", "Rahul Sharma", "brakes")
    print(f"[2] Book: {'✅' if r['success'] else '❌'} | {r.get('appointment',{}).get('appointment_id')}")
    appts = agent.get_appointments("VEH001")
    print(f"[3] Appointments for VEH001: {len(appts)}")
    cancel = agent.cancel_appointment(appts[0]["appointment_id"])
    print(f"[4] Cancel: {'✅' if cancel['success'] else '❌'}")
    print("  FILE 9 complete!\n")
