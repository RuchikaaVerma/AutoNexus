"""
FILE: services/agents/config/scheduling_config.py
PURPOSE: All configuration specific to the Scheduling Agent.
         Controls available slots, service durations, service centers,
         and how appointments are booked based on component type.
USED BY:
  - services/agents/workers/scheduling_agent.py  (FILE 9)
  - services/calendar/appointment_manager.py     (FILE 12)
  - services/calendar/reminder_scheduler.py      (FILE 13)
AUTHOR: Person 4
"""

# ==============================================================================
# SECTION 1: Service Centers
# ==============================================================================

SERVICE_CENTERS = [
    {
        "id":       "CENTER_01",
        "name":     "AutoNexus Central",
        "address":  "12 Main Street, Mumbai",
        "phone":    "+912212345678",
        "capacity": 6,     # max appointments per day
    },
    {
        "id":       "CENTER_02",
        "name":     "AutoNexus East",
        "address":  "45 East Avenue, Mumbai",
        "phone":    "+912298765432",
        "capacity": 4,
    },
    {
        "id":       "CENTER_03",
        "name":     "AutoNexus West",
        "address":  "78 West Road, Pune",
        "phone":    "+912012345678",
        "capacity": 4,
    },
]

DEFAULT_SERVICE_CENTER = "AutoNexus Central"


# ==============================================================================
# SECTION 2: Available Time Slots
# ==============================================================================

AVAILABLE_SLOTS = [
    "09:00", "10:00", "11:00",   # Morning
    "14:00", "15:00", "16:00",   # Afternoon
]

# Slots NOT available on these days
BLOCKED_DAYS = [
    "Sunday",    # Closed
]


# ==============================================================================
# SECTION 3: Service Duration by Component
# Based on Azure PdM dataset failure types (comp1-4)
# comp1=brakes, comp2=engine, comp3=oil, comp4=tires
# ==============================================================================

SERVICE_DURATION = {
    "brakes":      120,   # 2 hours (brake pad + fluid)
    "engine":      240,   # 4 hours (engine overhaul)
    "engine oil":  60,    # 1 hour  (oil + filter change)
    "tires":       90,    # 1.5 hours (rotate + balance + align)
    "comp1":       120,
    "comp2":       240,
    "comp3":       60,
    "comp4":       90,
    "default":     120,
}

# Estimated cost range by component (in INR)
SERVICE_COST = {
    "brakes":     {"min": 2500,  "max": 4000},
    "engine":     {"min": 8000,  "max": 25000},
    "engine oil": {"min": 800,   "max": 1500},
    "tires":      {"min": 1500,  "max": 3500},
    "default":    {"min": 1000,  "max": 5000},
}


# ==============================================================================
# SECTION 4: Appointment Status Values
# ==============================================================================

APPOINTMENT_STATUSES = [
    "confirmed",
    "cancelled",
    "rescheduled",
    "completed",
    "no_show",
]


# ==============================================================================
# SECTION 5: Reminder Settings
# ==============================================================================

REMINDER_SETTINGS = {
    "reminder_24h_hours_before": 24,    # Send 24hr reminder
    "reminder_1h_hours_before":  1,     # Send 1hr reminder
    "check_interval_sec":        300,   # Check every 5 minutes
    "reminder_window_24h":       25,    # Check appointments within 25 hours
    "reminder_window_1h":        2,     # Check appointments within 2 hours
}


# ==============================================================================
# SECTION 6: Urgency → Scheduling Priority
# When a CRITICAL vehicle needs service, it gets earliest available slot
# Based on days_until_failure from NASA CMAPSS model
# ==============================================================================

URGENCY_SLOT_PRIORITY = {
    "CRITICAL": 0,    # Book FIRST available slot (today if possible)
    "HIGH":     1,    # Book within next 2 days
    "MEDIUM":   3,    # Book within next week
    "LOW":      7,    # Book within 2 weeks
    "MONITOR":  14,   # No rush
}

# Appointment confirmation SMS template
CONFIRMATION_SMS = (
    "Confirmed! Hi {customer_name}, your AutoNexus "
    "{component} service for {vehicle_id} is booked "
    "for {date} at {time_slot} at {service_center}. "
    "Reply CANCEL to cancel."
)

# Reminder SMS template
REMINDER_SMS_24H = (
    "Reminder: Hi {customer_name}, your AutoNexus service "
    "is tomorrow {date} at {time_slot} at {service_center}. "
    "Reply CANCEL to cancel."
)

REMINDER_SMS_1H = (
    "See you soon! {customer_name}, your AutoNexus service "
    "is in 1 hour at {time_slot} at {service_center}. "
    "We are ready for your {vehicle_id}."
)


# ==============================================================================
# SECTION 7: Helper Functions
# ==============================================================================

def get_service_duration(component: str) -> int:
    """Get service duration in minutes for a component."""
    return SERVICE_DURATION.get(component.lower(), SERVICE_DURATION["default"])


def get_service_cost(component: str) -> dict:
    """Get estimated cost range for a component service."""
    return SERVICE_COST.get(component.lower(), SERVICE_COST["default"])


def get_priority_days(urgency: str) -> int:
    """Get how many days ahead to book based on urgency level."""
    return URGENCY_SLOT_PRIORITY.get(urgency, 7)


def format_confirmation_sms(
    customer_name: str,
    component: str,
    vehicle_id: str,
    date: str,
    time_slot: str,
    service_center: str = DEFAULT_SERVICE_CENTER,
) -> str:
    """Format appointment confirmation SMS."""
    return CONFIRMATION_SMS.format(
        customer_name  = customer_name,
        component      = component,
        vehicle_id     = vehicle_id,
        date           = date,
        time_slot      = time_slot,
        service_center = service_center,
    )


def format_reminder_sms(
    reminder_type: str,
    customer_name: str,
    vehicle_id: str,
    date: str,
    time_slot: str,
    service_center: str = DEFAULT_SERVICE_CENTER,
) -> str:
    """Format reminder SMS for 24h or 1h reminder."""
    template = REMINDER_SMS_24H if reminder_type == "24h" else REMINDER_SMS_1H
    return template.format(
        customer_name  = customer_name,
        vehicle_id     = vehicle_id,
        date           = date,
        time_slot      = time_slot,
        service_center = service_center,
    )


# ==============================================================================
# SELF-TEST
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Scheduling Config — Self Test")
    print("="*55)

    print("\n[1] Service centers:")
    for c in SERVICE_CENTERS:
        print(f"    {c['id']} | {c['name']} | capacity={c['capacity']}/day")

    print("\n[2] Service durations and costs:")
    for comp in ["brakes", "engine", "engine oil", "tires"]:
        dur  = get_service_duration(comp)
        cost = get_service_cost(comp)
        print(f"    {comp:<15}: {dur} min | ₹{cost['min']:,}–₹{cost['max']:,}")

    print("\n[3] Urgency → booking priority:")
    for urgency, days in URGENCY_SLOT_PRIORITY.items():
        print(f"    {urgency:<10}: book within {days} days")

    print("\n[4] SMS templates:")
    sms = format_confirmation_sms(
        "Rahul Sharma", "brakes", "VEH001",
        "2026-03-10", "10:00"
    )
    print(f"    Confirmation: {sms[:70]}...")

    reminder = format_reminder_sms(
        "24h", "Rahul Sharma", "VEH001",
        "2026-03-10", "10:00"
    )
    print(f"    24hr Reminder: {reminder[:70]}...")

    print("\n  ✅ Scheduling config ready!\n")