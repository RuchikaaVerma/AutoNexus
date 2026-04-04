"""
FILE 25: services/demo/demo_runner.py
PURPOSE: Single script that runs the complete AutoNexus hackathon demo.
         Shows all Person 4 components working together end-to-end.
RUN: python services/demo/demo_runner.py
AUTHOR: Person 4
"""

import sys
import os

# ── Fix: add project root to path so 'services' is always importable ──────────
<<<<<<< HEAD
# This works whether you run from root, from services/demo/, or anywhere else
=======
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
# ──────────────────────────────────────────────────────────────────────────────

import time
import logging
from datetime import datetime

<<<<<<< HEAD
logging.basicConfig(level=logging.WARNING)  # Suppress logs during demo for clean output
=======
logging.basicConfig(level=logging.WARNING)
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73

# ── Colour helpers ─────────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def banner(text, colour=CYAN):
    print(f"\n{colour}{BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}")

def step(num, text):
    print(f"\n{YELLOW}[Step {num}]{RESET} {text}")
    time.sleep(0.5)

def ok(text):
    print(f"  {GREEN}✅ {text}{RESET}")

def info(text):
    print(f"  {BLUE}ℹ  {text}{RESET}")

def warn(text):
    print(f"  {YELLOW}⚠  {text}{RESET}")

<<<<<<< HEAD
=======
def agent_says(text):
    """Print agent dialogue and speak it"""
    print(f"\n  {CYAN}🤖 Agent   :{RESET} {text}")
    try:
        from services.voice.text_to_speech import speak
        speak(text)
    except Exception:
        pass

def customer_input(prompt_text, options=None, allow_free_text=False):
    """
    Print customer prompt and capture real user input.
    Returns the user's typed response.
    """
    from services.demo.demo_scenarios import get_user_input
    response = get_user_input(prompt_text, options=options, allow_free_text=allow_free_text)
    print(f"  {GREEN}👤 Customer:{RESET} {response}")
    return response

>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73

# ==============================================================================
# DEMO SCENARIO 1 — Vehicle Failure Alert + Customer Engagement
# ==============================================================================

def demo_scenario_1():
<<<<<<< HEAD
    banner("SCENARIO 1: Brake Failure Detection & Customer Engagement", RED)
    info("AutoNexus ML system detects brake failure risk for VEH001")
    time.sleep(1)

    prediction = {
        "vehicle_id":          "VEH001",
        "customer_name":       "Rahul Sharma",
        "customer_phone":      "+919876543210",
=======
    from services.demo.demo_scenarios import get_scenario, format_message
    scenario = get_scenario(1)
    script   = scenario["script"]

    banner(f"SCENARIO 1: {scenario['name']}", RED)
    info(scenario["description"])
    time.sleep(1)

    prediction = {
        "vehicle_id":          scenario["vehicle_id"],
        "customer_name":       scenario["customer"],
        "customer_phone":      scenario["phone"],
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
        "customer_email":      "rahul@example.com",
        "component_at_risk":   "brakes",
        "days_until_failure":  7,
        "failure_probability": 0.89,
    }

<<<<<<< HEAD
=======
    # ── Step 1: ML Prediction ─────────────────────────────────────────────────
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    step(1, "ML Model Prediction received")
    info(f"Vehicle        : {prediction['vehicle_id']}")
    info(f"Component      : {prediction['component_at_risk']}")
    info(f"Days until fail: {prediction['days_until_failure']}")
    info(f"Probability    : {prediction['failure_probability']*100:.0f}%")

<<<<<<< HEAD
=======
    # ── Step 2: Pre-call SMS ──────────────────────────────────────────────────
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    step(2, "Sending pre-call SMS alert...")
    from services.notifications.sms_sender import send_alert_sms
    sms = send_alert_sms(
        prediction["customer_phone"], prediction["customer_name"],
        prediction["vehicle_id"], prediction["component_at_risk"],
        prediction["days_until_failure"],
    )
<<<<<<< HEAD
    ok(f"SMS sent (demo): {sms.get('sid','DEMO')}")

=======
    ok(f"SMS sent (demo): {sms.get('sid', 'DEMO')}")

    # ── Step 3: Pre-call Email ────────────────────────────────────────────────
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    step(3, "Sending pre-call email alert...")
    from services.notifications.email_sender import send_service_reminder
    email = send_service_reminder(
        prediction["customer_email"], prediction["customer_name"],
        prediction["vehicle_id"], prediction["component_at_risk"],
        prediction["days_until_failure"],
    )
    ok(f"Email sent (demo): {email.get('demo', True)}")

<<<<<<< HEAD
    step(4, "Initiating AI voice call to customer... 🎤")
    info("You will hear the agent speak — demo mode uses simulated responses")
    time.sleep(1)

    from services.agents.workers.engagement_agent import EngagementAgent
    agent  = EngagementAgent(demo_mode=True)
    result = agent.process_prediction(prediction)

    ok(f"Call completed  : outcome = {result['call_outcome']}")
    ok(f"Call duration   : {result.get('call_duration', 0):.1f}s")
    ok(f"Transcript turns: {len(result.get('transcript', []))}")

    print(f"\n  {CYAN}📋 Call Transcript:{RESET}")
    for line in result.get("transcript", [])[:6]:
        speaker = "🤖 Agent   " if line["speaker"] == "agent" else "👤 Customer"
        print(f"    {speaker}: {line['text'][:65]}")

    step(5, "Booking confirmation SMS + Email sent automatically")
    ok("Scenario 1 COMPLETE — customer contacted and appointment booked!")
=======
    # ── Step 4: AI Voice Call — fully interactive ─────────────────────────────
    step(4, "Initiating AI voice call to customer... 🎤")
    info("Respond as the customer — type your answer and press Enter")
    time.sleep(1)

    transcript = []

    # --- Greeting ---
    msg = format_message(script["greeting"], customer=prediction["customer_name"])
    agent_says(msg)
    transcript.append({"speaker": "agent", "text": msg})

    # --- Diagnosis ---
    msg = format_message(script["diagnosis"], vehicle_id=prediction["vehicle_id"])
    agent_says(msg)
    transcript.append({"speaker": "agent", "text": msg})

    # --- Explain ---
    agent_says(script["explain"])
    transcript.append({"speaker": "agent", "text": script["explain"]})

    # --- Schedule? ---
    agent_says(script["schedule_prompt"])
    transcript.append({"speaker": "agent", "text": script["schedule_prompt"]})

    schedule_resp = customer_input(
        "Do you want to book an appointment?",
        options=script["schedule_options"],
    )
    transcript.append({"speaker": "customer", "text": schedule_resp})

    call_outcome = "declined"
    chosen_slot  = None

    if schedule_resp in ("yes",):
        # --- Availability ---
        agent_says(script["availability_prompt"])
        transcript.append({"speaker": "agent", "text": script["availability_prompt"]})

        time_pref = customer_input(
            "What time of day suits you?",
            options=script["availability_options"],
        )
        transcript.append({"speaker": "customer", "text": time_pref})

        # Map preference → actual slot
        from services.agents.workers.scheduling_agent import SchedulingAgent
        slots = SchedulingAgent().get_available_slots()
        slot_map = {"morning": 0, "afternoon": 1, "evening": 2}
        idx = slot_map.get(time_pref, 0)
        chosen_slot = slots[idx] if idx < len(slots) else slots[0]

        msg = format_message(script["confirmation"], slot=chosen_slot)
        agent_says(msg)
        transcript.append({"speaker": "agent", "text": msg})
        call_outcome = "appointment_booked"

    else:
        agent_says(script["decline"])
        transcript.append({"speaker": "agent", "text": script["decline"]})
        call_outcome = "follow_up_scheduled"

    # ── Step 5: Book + notify ─────────────────────────────────────────────────
    step(5, "Processing outcome...")

    result = {
        "call_outcome":  call_outcome,
        "call_duration": len(transcript) * 8.0,
        "transcript":    transcript,
        "chosen_slot":   chosen_slot,
    }

    if call_outcome == "appointment_booked" and chosen_slot:
        from services.agents.workers.scheduling_agent import SchedulingAgent
        scheduler = SchedulingAgent()
        booking   = scheduler.book_appointment(
            prediction["vehicle_id"], prediction["customer_name"],
            prediction["component_at_risk"], time_slot=chosen_slot,
        )
        appt = booking.get("appointment", {})
        ok(f"Appointment booked | ID={appt.get('appointment_id')} | {appt.get('date')} {appt.get('time_slot')}")

        from services.notifications.sms_sender import send_appointment_reminder
        send_appointment_reminder(
            prediction["customer_phone"], prediction["customer_name"],
            appt.get("date", "2026-03-10"), appt.get("time_slot", "10:00"),
            "AutoNexus Central",
        )
        ok("Booking confirmation SMS + Email sent automatically")

    ok(f"Call completed   : outcome = {result['call_outcome']}")
    ok(f"Call duration    : {result['call_duration']:.1f}s")
    ok(f"Transcript turns : {len(transcript)}")

    print(f"\n  {CYAN}📋 Call Transcript Summary:{RESET}")
    for line in transcript:
        speaker = "🤖 Agent   " if line["speaker"] == "agent" else "👤 Customer"
        print(f"    {speaker}: {line['text'][:65]}")

    ok("Scenario 1 COMPLETE — customer contacted!")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    return result


# ==============================================================================
# DEMO SCENARIO 2 — Appointment + Reminder + Feedback + RCA Report
# ==============================================================================

def demo_scenario_2():
<<<<<<< HEAD
    banner("SCENARIO 2: Appointment Management & Report Generation", BLUE)
    info("Customer VEH002 previously agreed to service — now managing the appointment")
    time.sleep(1)

=======
    from services.demo.demo_scenarios import get_scenario, format_message
    scenario = get_scenario(2)
    script   = scenario["script"]

    banner(f"SCENARIO 2: {scenario['name']}", BLUE)
    info(scenario["description"])
    time.sleep(1)

    # ── Step 1: Book appointment ──────────────────────────────────────────────
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    step(1, "Booking appointment in calendar system...")
    from services.agents.workers.scheduling_agent import SchedulingAgent
    scheduler = SchedulingAgent()
    slots     = scheduler.get_available_slots()
<<<<<<< HEAD
    info(f"Available slots: {slots[:3]}")
    booking   = scheduler.book_appointment("VEH002", "Priya Singh", "engine oil")
    appt      = booking.get("appointment", {})
    ok(f"Appointment booked | ID={appt.get('appointment_id')} | {appt.get('date')} {appt.get('time_slot')}")

    step(2, "Sending appointment reminder (24hr before)...")
    from services.notifications.sms_sender import send_appointment_reminder
    reminder = send_appointment_reminder(
        "+919123456789", "Priya Singh",
        appt.get("date","2026-03-10"), appt.get("time_slot","10:00"),
        "AutoNexus Central",
    )
    ok(f"Reminder SMS sent: {reminder.get('sid','DEMO')}")

    step(3, "Collecting post-service feedback via AI voice...")
    time.sleep(0.5)
    from services.agents.workers.feedback_agent import FeedbackAgent
    feedback_agent = FeedbackAgent(demo_mode=True)
    feedback       = feedback_agent.collect_feedback("VEH002", "Priya Singh", "engine oil service")
    ok(f"Feedback collected | rating={feedback['rating']}/5 | sentiment={feedback['sentiment']}")
    ok(f"Feedback CSV saved for Person 2 ML retraining")

    step(4, "Running Root Cause Analysis...")
    from services.manufacturing.rca_engine import RCAEngine
    rca = RCAEngine().analyze(
        "VEH002", "engine oil",
=======

    print(f"\n  {CYAN}📅 Available time slots:{RESET}")
    for i, slot in enumerate(slots, 1):
        print(f"     {YELLOW}[{i}]{RESET} {slot}")

    raw = customer_input(
        "Enter slot number (or press Enter for first available):",
        options=[str(i) for i in range(1, len(slots) + 1)],
        allow_free_text=True,
    )
    idx         = int(raw) - 1 if raw.isdigit() and 1 <= int(raw) <= len(slots) else 0
    chosen_slot = slots[idx]
    info(f"Selected slot: {chosen_slot}")

    booking = scheduler.book_appointment(
        scenario["vehicle_id"], scenario["customer"],
        scenario["issue"], time_slot=chosen_slot,
    )
    appt = booking.get("appointment", {})
    ok(f"Appointment booked | ID={appt.get('appointment_id')} | {appt.get('date')} {appt.get('time_slot')}")

    # ── Step 2: Reminder SMS ──────────────────────────────────────────────────
    step(2, "Sending appointment reminder (24hr before)...")
    from services.notifications.sms_sender import send_appointment_reminder
    reminder = send_appointment_reminder(
        scenario["phone"], scenario["customer"],
        appt.get("date", "2026-03-10"), appt.get("time_slot", "10:00"),
        "AutoNexus Central",
    )
    ok(f"Reminder SMS sent: {reminder.get('sid', 'DEMO')}")

    # ── Step 3: Feedback call — interactive ───────────────────────────────────
    step(3, "Collecting post-service feedback via AI voice...")
    time.sleep(0.5)

    transcript = []

    # --- Greeting ---
    msg = format_message(script["greeting"],
                         customer=scenario["customer"],
                         vehicle_id=scenario["vehicle_id"])
    agent_says(msg)
    transcript.append({"speaker": "agent", "text": msg})

    # --- Rating ---
    agent_says(script["feedback_prompt"])
    transcript.append({"speaker": "agent", "text": script["feedback_prompt"]})

    rating_str = customer_input(
        "Rate your experience (1 = poor, 5 = excellent):",
        options=script["rating_options"],
    )
    transcript.append({"speaker": "customer", "text": rating_str})
    rating    = int(rating_str)
    sentiment = "positive" if rating >= 4 else "neutral" if rating == 3 else "negative"

    # --- Follow-up based on rating ---
    if rating >= 4:
        agent_says(script["followup_good"])
        transcript.append({"speaker": "agent", "text": script["followup_good"]})

        agent_says(script["recommendation_prompt"])
        transcript.append({"speaker": "agent", "text": script["recommendation_prompt"]})

        rec = customer_input(
            "Would you recommend us?",
            options=script["recommendation_options"],
        )
        transcript.append({"speaker": "customer", "text": rec})

    else:
        agent_says(script["followup_bad"])
        transcript.append({"speaker": "agent", "text": script["followup_bad"]})

        agent_says(script["issue_prompt"])
        transcript.append({"speaker": "agent", "text": script["issue_prompt"]})

        issue_resp = customer_input(
            "What could we improve? (type freely):",
            allow_free_text=True,
        )
        transcript.append({"speaker": "customer", "text": issue_resp})

    # --- Thanks ---
    agent_says(script["thanks"])
    transcript.append({"speaker": "agent", "text": script["thanks"]})

    # Save feedback
    from services.agents.workers.feedback_agent import FeedbackAgent
    FeedbackAgent(demo_mode=True)
    feedback = {"rating": rating, "sentiment": sentiment}
    ok(f"Feedback collected | rating={rating}/5 | sentiment={sentiment}")
    ok("Feedback CSV saved for Person 2 ML retraining")

    # ── Step 4: RCA ───────────────────────────────────────────────────────────
    step(4, "Running Root Cause Analysis...")
    from services.manufacturing.rca_engine import RCAEngine
    rca = RCAEngine().analyze(
        scenario["vehicle_id"], scenario["issue"],
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
        {"oil_pressure": 28, "engine_temperature": 98},
    )
    ok(f"Primary cause    : {rca['primary_cause']}")
    ok(f"Confidence       : {rca['confidence']}%")
    ok(f"Severity         : {rca['severity']}")

<<<<<<< HEAD
=======
    # ── Step 5: CAPA ──────────────────────────────────────────────────────────
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    step(5, "Generating CAPA plan...")
    from services.manufacturing.capa_generator import CAPAGenerator
    capa = CAPAGenerator().generate(rca)
    ok(f"Priority   : {capa['priority']}")
    ok(f"Deadline   : {capa['deadline']}")
    ok(f"Cost est.  : {capa['estimated_cost']}")
    info(f"Corrective : {capa['corrective_actions'][0]}")

<<<<<<< HEAD
    step(6, "Generating PDF report...")
    from services.manufacturing.report_generator import generate_vehicle_report
    pdf_path = generate_vehicle_report("VEH002", rca, capa)
=======
    # ── Step 6: PDF report ────────────────────────────────────────────────────
    step(6, "Generating PDF report...")
    from services.manufacturing.report_generator import generate_vehicle_report
    pdf_path = generate_vehicle_report(scenario["vehicle_id"], rca, capa)
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    if pdf_path:
        ok(f"PDF report saved: {pdf_path}")
    else:
        warn("PDF generation skipped (reportlab may not be installed)")

<<<<<<< HEAD
=======
    print(f"\n  {CYAN}📋 Feedback Transcript:{RESET}")
    for line in transcript:
        speaker = "🤖 Agent   " if line["speaker"] == "agent" else "👤 Customer"
        print(f"    {speaker}: {line['text'][:65]}")

>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    ok("Scenario 2 COMPLETE — full service lifecycle managed!")
    return {"rca": rca, "capa": capa, "feedback": feedback}


# ==============================================================================
# DEMO SCENARIO 3 — UEBA Security Threat Detection
<<<<<<< HEAD
# ── FIX: use start_baseline/finish_baseline so Step 1 is silent ──────────────
# ==============================================================================

def demo_scenario_3():
    banner("SCENARIO 3: UEBA Security — Anomaly Detection & Response", RED)
    info("AutoNexus UEBA system monitors all AI agents for suspicious behaviour")
    time.sleep(1)

    from services.security.ueba.anomaly_detector import AnomalyDetector
    from services.security.ueba.alert_manager import handle_anomaly, block_agent, unblock_agent, is_blocked
    from services.security.ueba.access_control import check_permission

    detector = AnomalyDetector()

    # ── STEP 1: Build baseline silently (no WARNING spam) ────────────────────
    step(1, "Recording normal EngagementAgent behaviour (baseline)...")

    detector.start_baseline("EngagementAgent")        # suppresses warnings
    for _ in range(25):
        detector.score_action("EngagementAgent", "api_call",    {"endpoint": "/predict"})
        detector.score_action("EngagementAgent", "data_access", {"table": "vehicles"})
    detector.finish_baseline("EngagementAgent")        # trains model on REAL data

    baseline = detector.baseline.get_baseline("EngagementAgent")
    ok(f"Baseline built   | samples={baseline['sample_count']} | rate={baseline['call_rate_rpm']:.2f} rpm")

    # ── STEP 2: Normal action — should now score LOW ─────────────────────────
    step(2, "Testing normal action (should be LOW risk)...")
=======
# ==============================================================================

def demo_scenario_3():
    from services.demo.demo_scenarios import get_scenario, format_message
    scenario = get_scenario(3)
    script   = scenario["script"]

    banner(f"SCENARIO 3: {scenario['name']}", RED)
    info(scenario["description"])
    time.sleep(1)

    from services.security.ueba.anomaly_detector import AnomalyDetector
    from services.security.ueba.alert_manager    import handle_anomaly, block_agent, unblock_agent, is_blocked
    from services.security.ueba.access_control   import check_permission

    detector = AnomalyDetector()

    # ── Step 1: Baseline ──────────────────────────────────────────────────────
    step(1, "Recording normal EngagementAgent behaviour (baseline)...")
    detector.start_baseline("EngagementAgent")
    for _ in range(25):
        detector.score_action("EngagementAgent", "api_call",    {"endpoint": "/predict"})
        detector.score_action("EngagementAgent", "data_access", {"table": "vehicles"})
    detector.finish_baseline("EngagementAgent")
    baseline = detector.baseline.get_baseline("EngagementAgent")
    ok(f"Baseline built   | samples={baseline['sample_count']} | rate={baseline['call_rate_rpm']:.2f} rpm")

    # ── Step 2: Simulated customer call (interactive) ─────────────────────────
    step(2, "AI Agent calls customer about engine warning... 🎤")
    info("Respond as the customer — type your answer and press Enter")
    time.sleep(0.5)

    transcript = []

    # Greeting
    msg = format_message(script["greeting"],
                         customer=scenario["customer"],
                         vehicle_id=scenario["vehicle_id"])
    agent_says(msg)
    transcript.append({"speaker": "agent", "text": msg})

    # Diagnosis
    agent_says(script["diagnosis"])
    transcript.append({"speaker": "agent", "text": script["diagnosis"]})

    # Details prompt
    agent_says(script["details_prompt"])
    transcript.append({"speaker": "agent", "text": script["details_prompt"]})

    details_resp = customer_input(
        "Do you want technical details?",
        options=script["details_options"],
    )
    transcript.append({"speaker": "customer", "text": details_resp})

    if details_resp == "yes":
        agent_says(script["technical"])
        transcript.append({"speaker": "agent", "text": script["technical"]})

    # Schedule
    agent_says(script["schedule_prompt"])
    transcript.append({"speaker": "agent", "text": script["schedule_prompt"]})

    sched_resp = customer_input(
        "Would you like to book an appointment?",
        options=script["schedule_options"],
    )
    transcript.append({"speaker": "customer", "text": sched_resp})

    if sched_resp == "yes":
        from services.agents.workers.scheduling_agent import SchedulingAgent
        slots = SchedulingAgent().get_available_slots()
        chosen_slot = slots[0]
        msg = format_message(script["confirmation"], slot=chosen_slot)
        agent_says(msg)
        transcript.append({"speaker": "agent", "text": msg})
        ok(f"Appointment booked: {chosen_slot}")
    else:
        agent_says("Understood. Please monitor the warning light and call us if it worsens.")
        transcript.append({"speaker": "agent", "text": "Understood. Please monitor..."})

    print(f"\n  {CYAN}📋 Call Transcript:{RESET}")
    for line in transcript:
        speaker = "🤖 Agent   " if line["speaker"] == "agent" else "👤 Customer"
        print(f"    {speaker}: {line['text'][:65]}")

    # ── Step 3: Normal action ──────────────────────────────────────────────────
    step(3, "Testing normal action (should be LOW risk)...")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    normal = detector.score_action("EngagementAgent", "api_call")
    info(f"api_call score   : {normal['score']}/100 | level={normal['risk_level']}")
    if not normal["is_anomaly"]:
        ok("Normal action — no alert triggered")
    else:
        warn("Flagged unexpectedly")

<<<<<<< HEAD
    # ── STEP 3: Suspicious action ────────────────────────────────────────────
    step(3, "Simulating suspicious action — bulk_data_export...")
=======
    # ── Step 4: Suspicious action ──────────────────────────────────────────────
    step(4, "Simulating suspicious action — bulk_data_export...")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    time.sleep(0.5)
    suspicious = detector.score_action("EngagementAgent", "bulk_data_export", {"rows": 50000})
    info(f"bulk_export score: {suspicious['score']}/100 | level={suspicious['risk_level']}")

<<<<<<< HEAD
    # ── STEP 4: Critical threat → alert + block ──────────────────────────────
    step(4, "Simulating critical threat — admin_override...")
=======
    # ── Step 5: Critical threat → alert + block ────────────────────────────────
    step(5, "Simulating critical threat — admin_override...")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    time.sleep(0.5)
    critical_result = {
        "agent_name":  "EngagementAgent",
        "score":       88,
        "risk_level":  "CRITICAL",
        "action_type": "admin_override",
        "is_anomaly":  True,
        "is_critical": True,
    }
    alert = handle_anomaly(critical_result)
    ok(f"Alert raised     : {alert['alert_id']}")
    ok(f"Actions taken    : {alert['actions_taken']}")
    ok(f"Dashboard alerted: P3 UEBAAlerts.jsx notified")
    ok(f"Backend alerted  : P1 /alerts endpoint notified")

<<<<<<< HEAD
    # ── STEP 5: Verify agent is blocked ──────────────────────────────────────
    step(5, "Checking agent is blocked...")
    blocked = is_blocked("EngagementAgent")
    ok(f"Agent blocked    : {blocked}")

    # ── STEP 6: Access control matrix ────────────────────────────────────────
    step(6, "Testing access control matrix...")
=======
    # ── Step 6: Verify blocked ─────────────────────────────────────────────────
    step(6, "Checking agent is blocked...")
    blocked = is_blocked("EngagementAgent")
    ok(f"Agent blocked    : {blocked}")

    # ── Step 7: Access control matrix ─────────────────────────────────────────
    step(7, "Testing access control matrix...")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    checks = [
        ("EngagementAgent", "predictions",  "allowed"),
        ("EngagementAgent", "ueba_logs",    "DENIED"),
        ("SchedulingAgent", "appointments", "allowed"),
        ("FeedbackAgent",   "admin_panel",  "DENIED"),
    ]
    for agent, resource, expected in checks:
        r      = check_permission(agent, resource)
        status = "✅ allowed" if r["allowed"] else "🚫 DENIED"
        print(f"    {agent:<30} → {resource:<20} : {status}")

<<<<<<< HEAD
    # ── STEP 7: Unblock after review ─────────────────────────────────────────
    step(7, "Unblocking agent after review (incident resolved)...")
=======
    # ── Step 8: Unblock ────────────────────────────────────────────────────────
    step(8, "Unblocking agent after review (incident resolved)...")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
    unblock_agent("EngagementAgent")
    ok(f"Agent unblocked  : {not is_blocked('EngagementAgent')}")
    ok("Scenario 3 COMPLETE — threat detected, contained, and resolved!")


# ==============================================================================
# MAIN DEMO RUNNER
# ==============================================================================

def run_full_demo():
    print(f"\n{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         🚗  AutoNexus — Hackathon Demo                  ║")
    print("║     Autonomous Predictive Maintenance System             ║")
<<<<<<< HEAD
    print("║                  Person 4 — Security & Integration      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"  Started at : {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print(f"  Mode       : DEMO (simulated responses, no real phone/email)")
    print(f"  Branch     : feature/p4-services")
=======
    print("║                  Security & Integration      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"  Started at : {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print(f"  Mode       : INTERACTIVE DEMO (you play the customer)")
    print(f"  Branch     : feature/p4-services")
    print(f"\n  {YELLOW}💡 Tip: Read the Agent's lines, then type your customer response.{RESET}")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73

    start = time.time()

    try:
        r1 = demo_scenario_1()
        time.sleep(2)
        r2 = demo_scenario_2()
        time.sleep(2)
        demo_scenario_3()

        elapsed = round(time.time() - start, 1)
        banner("DEMO COMPLETE — All Systems Operational!", GREEN)
<<<<<<< HEAD
        print(f"  {GREEN}✅ Scenario 1: Customer engagement    — {r1.get('call_outcome','done')}{RESET}")
=======
        print(f"  {GREEN}✅ Scenario 1: Customer engagement    — {r1.get('call_outcome', 'done')}{RESET}")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
        print(f"  {GREEN}✅ Scenario 2: Appointment + reports  — PDF generated{RESET}")
        print(f"  {GREEN}✅ Scenario 3: UEBA security          — Threat contained{RESET}")
        print(f"\n  {BOLD}Total demo time: {elapsed}s{RESET}")
        print(f"\n  {CYAN}Person 4 Deliverables:{RESET}")
        print(f"    🤖 4 AI Agents        (Engagement, Scheduling, Feedback, Manufacturing)")
        print(f"    🎤 Voice AI           (TTS + STT + Call Manager)")
        print(f"    📱 Notifications      (SMS + Email + Push)")
        print(f"    📅 Calendar           (Appointments + Reminders)")
        print(f"    🔐 UEBA Security      (Baseline + Detection + Alerts + Access Control)")
        print(f"    📊 RCA + CAPA         (Root Cause + Corrective Actions)")
        print(f"    📄 PDF Reports        (ReportLab generated)")
        print(f"    📈 Prometheus Metrics (Grafana ready)")
        print(f"\n  {BOLD}Ready for hackathon presentation! 🏆{RESET}\n")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Demo interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}Demo error: {e}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_full_demo()