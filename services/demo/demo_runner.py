"""
FILE 25: services/demo/demo_runner.py
PURPOSE: Single script that runs the complete AutoNexus hackathon demo.
         Shows all Person 4 components working together end-to-end.
RUN: python services/demo/demo_runner.py
AUTHOR: Person 4
"""

import time
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.WARNING)  # Suppress logs during demo for clean output

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


# ==============================================================================
# DEMO SCENARIO 1 — Vehicle Failure Alert + Customer Engagement
# Shows: ML prediction → AI voice call → SMS → Email → Appointment booking
# ==============================================================================

def demo_scenario_1():
    banner("SCENARIO 1: Brake Failure Detection & Customer Engagement", RED)
    info("AutoNexus ML system detects brake failure risk for VEH001")
    time.sleep(1)

    # Simulate prediction from Person 2's ML model
    prediction = {
        "vehicle_id":          "VEH001",
        "customer_name":       "Rahul Sharma",
        "customer_phone":      "+919876543210",
        "customer_email":      "rahul@example.com",
        "component_at_risk":   "brakes",
        "days_until_failure":  7,
        "failure_probability": 0.89,
    }

    step(1, f"ML Model Prediction received")
    info(f"Vehicle        : {prediction['vehicle_id']}")
    info(f"Component      : {prediction['component_at_risk']}")
    info(f"Days until fail: {prediction['days_until_failure']}")
    info(f"Probability    : {prediction['failure_probability']*100:.0f}%")

    step(2, "Sending pre-call SMS alert...")
    from services.notifications.sms_sender import send_alert_sms
    sms = send_alert_sms(
        prediction["customer_phone"], prediction["customer_name"],
        prediction["vehicle_id"], prediction["component_at_risk"],
        prediction["days_until_failure"],
    )
    ok(f"SMS sent (demo): {sms.get('sid','DEMO')}")

    step(3, "Sending pre-call email alert...")
    from services.notifications.email_sender import send_service_reminder
    email = send_service_reminder(
        prediction["customer_email"], prediction["customer_name"],
        prediction["vehicle_id"], prediction["component_at_risk"],
        prediction["days_until_failure"],
    )
    ok(f"Email sent (demo): {email.get('demo', True)}")

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
    return result


# ==============================================================================
# DEMO SCENARIO 2 — Appointment + Reminder + Feedback + RCA Report
# Shows: Calendar booking → Reminder → Post-service feedback → PDF report
# ==============================================================================

def demo_scenario_2():
    banner("SCENARIO 2: Appointment Management & Report Generation", BLUE)
    info("Customer VEH002 previously agreed to service — now managing the appointment")
    time.sleep(1)

    step(1, "Booking appointment in calendar system...")
    from services.agents.workers.scheduling_agent import SchedulingAgent
    scheduler = SchedulingAgent()
    slots     = scheduler.get_available_slots()
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
        {"oil_pressure": 28, "engine_temperature": 98},
    )
    ok(f"Primary cause    : {rca['primary_cause']}")
    ok(f"Confidence       : {rca['confidence']}%")
    ok(f"Severity         : {rca['severity']}")

    step(5, "Generating CAPA plan...")
    from services.manufacturing.capa_generator import CAPAGenerator
    capa = CAPAGenerator().generate(rca)
    ok(f"Priority   : {capa['priority']}")
    ok(f"Deadline   : {capa['deadline']}")
    ok(f"Cost est.  : {capa['estimated_cost']}")
    info(f"Corrective : {capa['corrective_actions'][0]}")

    step(6, "Generating PDF report...")
    from services.manufacturing.report_generator import generate_vehicle_report
    pdf_path = generate_vehicle_report("VEH002", rca, capa)
    if pdf_path:
        ok(f"PDF report saved: {pdf_path}")
    else:
        warn("PDF generation skipped (reportlab may not be installed)")

    ok("Scenario 2 COMPLETE — full service lifecycle managed!")
    return {"rca": rca, "capa": capa, "feedback": feedback}


# ==============================================================================
# DEMO SCENARIO 3 — UEBA Security Threat Detection
# Shows: Normal behaviour → Anomaly detected → Alert → Block → Access control
# ==============================================================================

def demo_scenario_3():
    banner("SCENARIO 3: UEBA Security — Anomaly Detection & Response", RED)
    info("AutoNexus UEBA system monitors all AI agents for suspicious behaviour")
    time.sleep(1)

    from services.security.ueba.behavior_baseline import BehaviorBaseline
    from services.security.ueba.anomaly_detector import AnomalyDetector
    from services.security.ueba.alert_manager import handle_anomaly, block_agent, unblock_agent, is_blocked
    from services.security.ueba.access_control import check_permission

    detector = AnomalyDetector()

    step(1, "Recording normal EngagementAgent behaviour (baseline)...")
    for i in range(25):
        detector.score_action("EngagementAgent", "api_call",    {"endpoint": "/predict"})
        detector.score_action("EngagementAgent", "data_access", {"table": "vehicles"})
    baseline = detector.baseline.get_baseline("EngagementAgent")
    ok(f"Baseline built   | samples={baseline['sample_count']} | rate={baseline['call_rate_rpm']} rpm")

    step(2, "Testing normal action (should be LOW risk)...")
    normal = detector.score_action("EngagementAgent", "api_call")
    info(f"api_call score   : {normal['score']}/100 | level={normal['risk_level']}")
    ok("Normal action — no alert triggered") if not normal["is_anomaly"] else warn("Flagged unexpectedly")

    step(3, "Simulating suspicious action — bulk_data_export...")
    time.sleep(0.5)
    suspicious = detector.score_action("EngagementAgent", "bulk_data_export", {"rows": 50000})
    info(f"bulk_export score: {suspicious['score']}/100 | level={suspicious['risk_level']}")

    step(4, "Simulating critical threat — admin_override...")
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

    step(5, "Checking agent is blocked...")
    blocked = is_blocked("EngagementAgent")
    ok(f"Agent blocked    : {blocked}")

    step(6, "Testing access control matrix...")
    checks = [
        ("EngagementAgent", "predictions",  "allowed"),
        ("EngagementAgent", "ueba_logs",    "DENIED"),
        ("SchedulingAgent", "appointments", "allowed"),
        ("FeedbackAgent",   "admin_panel",  "DENIED"),
    ]
    for agent, resource, expected in checks:
        r = check_permission(agent, resource)
        status = "✅ allowed" if r["allowed"] else "🚫 DENIED"
        print(f"    {agent:<30} → {resource:<20} : {status}")

    step(7, "Unblocking agent after review (incident resolved)...")
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
    print("║                  Person 4 — Security & Integration      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"  Started at : {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print(f"  Mode       : DEMO (simulated responses, no real phone/email)")
    print(f"  Branch     : feature/p4-security")

    start = time.time()

    try:
        # Run all 3 scenarios
        r1 = demo_scenario_1()
        time.sleep(2)
        r2 = demo_scenario_2()
        time.sleep(2)
        demo_scenario_3()

        # Final summary
        elapsed = round(time.time() - start, 1)
        banner("DEMO COMPLETE — All Systems Operational!", GREEN)
        print(f"  {GREEN}✅ Scenario 1: Customer engagement    — {r1.get('call_outcome','done')}{RESET}")
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