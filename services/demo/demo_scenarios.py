# services/demo/demo_scenarios.py
"""
Interactive Demo Scenarios with User Input
User responds to AI agent prompts - no auto-generation
"""
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ── SCENARIO DEFINITIONS ──────────────────────────────────────────────────────

SCENARIOS = {
    1: {
        "name":        "Brake Failure Detection & Customer Engagement",
        "description": "ML detects brake failure → Agent calls customer → Appointment booked",
        "duration":    45,
        "vehicle_id":  "VEH001",
        "customer":    "Rahul Sharma",
        "phone":       "+919876543210",
        "issue":       "brake_failure",
        "severity":    "CRITICAL",
        "script": {
            "greeting": "Hello {customer}, this is the Predictive Maintenance AI calling from your auto service center.",
            "diagnosis": "We've detected an issue with your vehicle {vehicle_id}. Our sensors show your brake system needs attention - we predict brake failure within 12 days.",
            "explain": "Your brake temperature is running high at 95°C and brake fluid is at 25%. This could lead to brake failure if not serviced soon.",
            "schedule_prompt": "Would you like to schedule a preventive maintenance appointment?",
            "schedule_options": ["yes", "no", "maybe later"],
            "availability_prompt": "Great! When would work best for you?",
            "availability_options": ["morning", "afternoon", "evening"],
            "confirmation": "Perfect! I've booked your appointment for {slot}. You'll receive a confirmation SMS and email shortly.",
            "decline": "No problem. I'll send you a reminder in 3 days. Please don't delay - this is critical for your safety.",
        }
    },
    2: {
        "name":        "Appointment Management & Report Generation",
        "description": "Manage service appointment → Collect feedback → Generate CAPA PDF",
        "duration":    30,
        "vehicle_id":  "VEH002",
        "customer":    "Priya Singh",
        "phone":       "+919123456789",
        "issue":       "oil_change",
        "severity":    "LOW",
        "script": {
            "greeting": "Hello {customer}, this is your service center following up on your recent oil change for {vehicle_id}.",
            "feedback_prompt": "How would you rate your service experience on a scale of 1 to 5?",
            "rating_options": ["1", "2", "3", "4", "5"],
            "followup_good": "That's wonderful! We're glad you had a great experience. Would you recommend us to friends?",
            "followup_bad": "We're sorry to hear that. Can you tell us what went wrong?",
            "recommendation_prompt": "Would you recommend our service to others?",
            "recommendation_options": ["yes", "no", "maybe"],
            "issue_prompt": "What specifically could we improve?",
            "thanks": "Thank you for your feedback. We'll use this to improve our service.",
        }
    },
    3: {
        "name":        "UEBA Security — Anomaly Detection & Response",
        "description": "Agent behaves suspiciously → UEBA detects → Blocks + alerts dashboard",
        "duration":    30,
        "vehicle_id":  "VEH003",
        "customer":    "Amit Kumar",
        "phone":       "+919988776655",
        "issue":       "engine_warning",
        "severity":    "HIGH",
        "script": {
            "greeting": "Hello {customer}, we've detected an engine warning light on your {vehicle_id}.",
            "diagnosis": "Our analysis shows your engine temperature is elevated. Would you like to hear more details?",
            "details_prompt": "Should I explain the technical details?",
            "details_options": ["yes", "no"],
            "technical": "Your coolant temperature is at 105°C (normal is 85-95°C) and oil pressure is slightly low at 28 psi.",
            "schedule_prompt": "We recommend bringing your vehicle in within 5 days. Can we schedule an appointment?",
            "schedule_options": ["yes", "no", "let me check my calendar"],
            "confirmation": "Great! I'll schedule you for {slot}. Drive safely and avoid long trips until then.",
        }
    },
}


def get_scenario(scenario_id: int) -> dict:
    """Get scenario by ID"""
    if scenario_id not in SCENARIOS:
        raise ValueError(f"Scenario {scenario_id} not found. Choose 1, 2, or 3.")
    return SCENARIOS[scenario_id]


def list_scenarios():
    """Print all available scenarios"""
    print("\n" + "="*60)
    print("  AVAILABLE DEMO SCENARIOS")
    print("="*60)
    for sid, s in SCENARIOS.items():
        print(f"\n  Scenario {sid}: {s['name']}")
        print(f"  Description: {s['description']}")
        print(f"  Duration:    ~{s['duration']} seconds")
        print(f"  Vehicle:     {s['vehicle_id']} — {s['customer']}")
        print(f"  Issue:       {s['issue']} ({s['severity']})")
    print("\n" + "="*60)


def get_user_input(prompt: str, options: list = None, allow_free_text: bool = False) -> str:
    """
    Get user input with optional validation
    
    Args:
        prompt: Question to ask user
        options: List of valid options (if None, any input accepted)
        allow_free_text: If True, accept any text even when options provided
    
    Returns:
        User's response (validated if options provided)
    """
    if options:
        print(f"\n{prompt}")
        print(f"Options: {', '.join(options)}")
        if allow_free_text:
            print("(or type your own response)")
    else:
        print(f"\n{prompt}")
    
    while True:
        user_input = input("Your response: ").strip().lower()
        
        if not user_input:
            print("Please enter a response.")
            continue
        
        # If no options provided, accept any input
        if not options:
            return user_input
        
        # Check if input matches any option
        if user_input in [opt.lower() for opt in options]:
            return user_input
        
        # If free text allowed, accept any input
        if allow_free_text:
            return user_input
        
        # Invalid input - ask again
        print(f"Invalid input. Please choose from: {', '.join(options)}")


def format_message(template: str, **kwargs) -> str:
    """Format a message template with variables"""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.warning(f"Missing template variable: {e}")
        return template


def get_scenario_summary(result: dict) -> str:
    """Format scenario result for display"""
    return (
        f"\n  ✅ Scenario {result.get('scenario_id')} COMPLETE\n"
        f"  Name     : {result.get('name')}\n"
        f"  Status   : {result.get('status')}\n"
        f"  Duration : {result.get('duration', 0):.1f}s\n"
        f"  Outcome  : {result.get('outcome', 'N/A')}\n"
    )


if __name__ == "__main__":
    list_scenarios()
    print("\nScenarios loaded successfully!")
    print(f"Total scenarios: {len(SCENARIOS)}")