"""
FILE: services/agents/config/engagement_config.py
PURPOSE: All configuration specific to the Engagement Agent.
         Controls call behaviour, message templates, urgency levels,
         and how the agent decides who to call and when.
USED BY:
  - services/agents/workers/engagement_agent.py (FILE 8)
  - services/voice/call_manager.py              (FILE 4)
  - services/agents/config/dataset_loader.py
AUTHOR: Person 4
"""

from services.agents.config.hf_model_config import BACKEND_BASE_URL

# ==============================================================================
# SECTION 1: Call Priority Rules
# Based on failure_probability from UCI AI4I dataset analysis
# Overall failure rate in UCI = 3.4% — used to calibrate thresholds
# ==============================================================================

# If failure_probability >= this → call customer IMMEDIATELY (same day)
URGENT_THRESHOLD     = 0.85

# If failure_probability >= this → call within 24 hours
HIGH_THRESHOLD       = 0.65

# If failure_probability >= this → send SMS only, no call
MEDIUM_THRESHOLD     = 0.45

# Below this → monitor only, no contact
LOW_THRESHOLD        = 0.45

# Days until failure thresholds (from NASA CMAPSS RUL model)
CRITICAL_DAYS        = 3     # Call immediately
HIGH_DAYS            = 7     # Call today
MEDIUM_DAYS          = 14    # Call within 2 days
LOW_DAYS             = 30    # SMS reminder only


# ==============================================================================
# SECTION 2: Call Script Templates
# Message templates used by call_manager.py when speaking to customers
# ==============================================================================

CALL_SCRIPTS = {
    "opening": (
        "Hello, may I speak with {customer_name}? "
        "This is AutoNexus, your vehicle health monitoring service. "
        "I am calling regarding your vehicle {vehicle_id}."
    ),

    "alert_urgent": (
        "Our AI system has detected a CRITICAL issue with your {component}. "
        "The failure probability is {probability}% and may occur within "
        "{days} days. Immediate service is strongly recommended."
    ),

    "alert_high": (
        "Our predictive system has detected that your {component} "
        "requires attention within {days} days. "
        "We recommend scheduling a service appointment soon."
    ),

    "alert_medium": (
        "Our system has flagged your {component} for a routine check "
        "within the next {days} days. "
        "Would you like to book a preventive service?"
    ),

    "booking_offer": (
        "Would you like to schedule a service appointment? "
        "We have slots available as early as tomorrow. "
        "Say yes to book, no to decline, or agent to speak with our team."
    ),

    "booking_confirm": (
        "Excellent! I have booked your {component} service for "
        "{date} at {time_slot} at our {service_center}. "
        "You will receive an SMS confirmation shortly."
    ),

    "decline_response": (
        "Understood. Please be aware that delaying {component} service "
        "beyond {days} days may cause further damage. "
        "We will send you a reminder SMS. Thank you and goodbye!"
    ),

    "transfer": (
        "Of course! Let me transfer you to our service team. "
        "Please hold for a moment."
    ),

    "no_response": (
        "We were unable to reach you regarding your vehicle {vehicle_id}. "
        "Please call us at 1800-AUTO-NEX or visit our service center. "
        "Thank you. Goodbye!"
    ),
}


# ==============================================================================
# SECTION 3: Component Display Names
# Maps internal component names to customer-friendly names
# Based on Azure PdM_failures.csv failure types:
# comp1 = brakes, comp2 = engine, comp3 = engine oil, comp4 = tires
# ==============================================================================

COMPONENT_DISPLAY = {
    "brakes":      "brake system",
    "engine":      "engine",
    "engine oil":  "engine oil and filter",
    "tires":       "tire system",
    "comp1":       "brake system",
    "comp2":       "engine",
    "comp3":       "engine oil and filter",
    "comp4":       "tire system",
}

# Azure failure type to AutoNexus component mapping
AZURE_TO_COMPONENT = {
    "comp1": "brakes",
    "comp2": "engine",
    "comp3": "engine oil",
    "comp4": "tires",
}


# ==============================================================================
# SECTION 4: Call Timing Settings
# ==============================================================================

CALL_SETTINGS = {
    "listen_duration_sec":    6,      # How long to listen for customer response
    "max_turns":              5,      # Max back-and-forth turns per call
    "retry_delay_sec":        30,     # Wait before retrying failed call
    "max_retries":            2,      # Max call retry attempts
    "pause_between_calls_sec": 3,     # Pause between calling multiple customers
    "demo_response_delay_sec": 0.8,   # Simulated pause in demo mode
}


# ==============================================================================
# SECTION 5: API Endpoints (Person 1 Backend)
# ==============================================================================

ENGAGEMENT_ENDPOINTS = {
    "get_predictions":  f"{BACKEND_BASE_URL}/predict",
    "get_vehicles":     f"{BACKEND_BASE_URL}/vehicles",
    "post_alert":       f"{BACKEND_BASE_URL}/alerts",
    "register_agent":   f"{BACKEND_BASE_URL}/agents/register",
    "get_vehicle":      f"{BACKEND_BASE_URL}/vehicles/{{vehicle_id}}",
}


# ==============================================================================
# SECTION 6: Urgency Level Calculator
# Uses both failure_probability AND days_until_failure from ML models
# ==============================================================================

def get_urgency_level(failure_probability: float, days_until_failure: int) -> str:
    """
    Calculate urgency level for a prediction.
    Combines probability score (UCI model) with days (NASA CMAPSS model).

    Returns: "CRITICAL", "HIGH", "MEDIUM", "LOW", "MONITOR"
    """
    if failure_probability >= URGENT_THRESHOLD or days_until_failure <= CRITICAL_DAYS:
        return "CRITICAL"
    elif failure_probability >= HIGH_THRESHOLD or days_until_failure <= HIGH_DAYS:
        return "HIGH"
    elif failure_probability >= MEDIUM_THRESHOLD or days_until_failure <= MEDIUM_DAYS:
        return "MEDIUM"
    elif days_until_failure <= LOW_DAYS:
        return "LOW"
    else:
        return "MONITOR"


def get_call_script(script_key: str, **kwargs) -> str:
    """
    Get a formatted call script template.

    Usage:
        msg = get_call_script("alert_urgent",
                              component="brakes",
                              probability=89,
                              days=7)
    """
    template = CALL_SCRIPTS.get(script_key, "")
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def get_component_display(component: str) -> str:
    """Get customer-friendly component name."""
    return COMPONENT_DISPLAY.get(component.lower(), component)


# ==============================================================================
# SELF-TEST
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Engagement Config — Self Test")
    print("="*55)

    # Test urgency levels
    print("\n[1] Urgency level calculations:")
    test_cases = [
        (0.92, 3,  "CRITICAL"),
        (0.87, 7,  "CRITICAL"),
        (0.70, 10, "HIGH"),
        (0.55, 20, "MEDIUM"),
        (0.30, 45, "MONITOR"),
    ]
    for prob, days, expected in test_cases:
        level   = get_urgency_level(prob, days)
        correct = "✅" if level == expected else "❌"
        print(f"    {correct} prob={prob} days={days} → {level}")

    # Test call scripts
    print("\n[2] Call script formatting:")
    msg = get_call_script(
        "alert_urgent",
        component  = "brakes",
        probability= 89,
        days       = 7,
    )
    print(f"    {msg[:80]}...")

    # Test component display
    print("\n[3] Component display names:")
    for code, name in AZURE_TO_COMPONENT.items():
        display = get_component_display(name)
        print(f"    {code} → {name} → '{display}'")

    print("\n  ✅ Engagement config ready!\n")