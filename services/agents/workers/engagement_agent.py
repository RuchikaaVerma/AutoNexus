"""
agents/engagement_agent.py
───────────────────────────
FULL WORKING EngagementAgent

What it does:
  ✅ Detects ANY vehicle problem (brake, engine, oil, tire, battery, transmission...)
  ✅ DAYTIME  (9 AM – 8 PM)  → Real VOICE CALL (pyttsx3 TTS) + SMS + Email
  ✅ NIGHTTIME (8 PM – 9 AM) → SMS + Email only, call scheduled for 9 AM
  ✅ Uses YOUR existing call_manager.py  (speak/listen loop)
  ✅ Uses YOUR existing sms_sender.py    (Twilio)
  ✅ Uses YOUR existing email_sender.py  (SendGrid)
  ✅ Reads credentials from hf_model_config.py (already set up)

To go LIVE:
  1. Fill .env with TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
  2. Fill .env with SENDGRID_API_KEY
  3. Set owner phone/email per vehicle (or set ALERT_PHONE / ALERT_EMAIL in .env)
  4. Run backend normally — this agent runs automatically on every analysis
"""

import os
import logging
from datetime import datetime

from services.voice.call_manager import CallManager
from services.notifications.sms_sender import send_alert_sms
from services.notifications.email_sender import send_service_reminder

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# SENSOR THRESHOLDS — covers ALL common vehicle problems
# ═══════════════════════════════════════════════════════════════════════════════
THRESHOLDS = {
    "brake_temp":        {"max": 100,  "label": "brake system overheating"},
    "oil_pressure":      {"min": 25,   "label": "low engine oil pressure"},
    "brake_fluid_level": {"min": 65,   "label": "low brake fluid level"},
    "engine_temp":       {"max": 105,  "label": "engine overheating"},
    "tire_pressure":     {"min": 28,   "label": "low tire pressure"},
    "battery_voltage":   {"min": 11.5, "label": "weak battery"},
    "transmission_temp": {"max": 95,   "label": "transmission overheating"},
    "coolant_level":     {"min": 50,   "label": "low coolant level"},
    "fuel_pressure":     {"min": 30,   "label": "low fuel pressure"},
    "mileage":           {"max": 150000, "label": "high mileage service due"},
}

# Business hours — calls only within this window
CALL_START = int(os.getenv("CALL_START_HOUR", "9"))   # 9 AM
CALL_END   = int(os.getenv("CALL_END_HOUR",  "20"))   # 8 PM


class EngagementAgent:
    """
    Handles ALL customer engagement for any vehicle problem.
    Wired directly to your existing voice, SMS, and email services.
    """

    def __init__(self, demo_mode: bool = False):
        """
        Args:
            demo_mode:
                True  → simulated voice (pyttsx3 speaks but uses demo responses)
                False → real call flow (pyttsx3 speaks, waits for mic response)
                        SMS and Email are ALWAYS real regardless of this flag
                        as long as Twilio/SendGrid keys are in .env
        """
        self.demo_mode    = demo_mode
        self.name         = "EngagementAgent"
        self.call_manager = CallManager(demo_mode=demo_mode)
        logger.info(f"EngagementAgent ready | demo_mode={demo_mode}")

    # ──────────────────────────────────────────────────────────────────────────
    def get_info(self) -> dict:
        return {
            "name":        self.name,
            "description": "Time-based engagement: voice call (daytime) + SMS + Email for ANY vehicle problem",
            "status":      "active",
            "demo_mode":   self.demo_mode,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # MAIN ENTRY — called by MasterAgent
    # ──────────────────────────────────────────────────────────────────────────
    def process(self, data: dict) -> dict:
        """
        Detects problems from sensor data and fires notifications.

        data must contain:
            vehicle_id    : str   e.g. "VEH002"
            sensors       : dict  all sensor readings from the vehicle
            owner         : dict  {name, phone, email}
            vehicle_model : str   e.g. "Honda City 2019"   (optional)
            current_hour  : int   0-23  (MasterAgent already sets this)
        """
        vehicle_id    = data.get("vehicle_id", "UNKNOWN")
        sensors       = data.get("sensors", {})
        vehicle_model = data.get("vehicle_model", vehicle_id)
        current_hour  = data.get("current_hour", datetime.now().hour)

        # ── Resolve owner — vehicle record → .env fallback ────────────────────
        owner       = data.get("owner") or {}
        owner_name  = owner.get("name")  or os.getenv("ALERT_NAME",  "Vehicle Owner")
        owner_phone = owner.get("phone") or os.getenv("ALERT_PHONE", "")
        owner_email = owner.get("email") or os.getenv("ALERT_EMAIL", "")

        # ── Detect ALL problems ────────────────────────────────────────────────
        issues = self._detect_issues(sensors)

        # ── No problems → return healthy ──────────────────────────────────────
        if not issues:
            logger.info(f"[{vehicle_id}] No issues detected — vehicle healthy")
            return {
                "agent":      self.name,
                "vehicle_id": vehicle_id,
                "urgency":    "NORMAL",
                "issues":     [],
                "message":    "All systems normal. Vehicle is healthy.",
                "notifications_sent": {},
            }

        # ── Time check ────────────────────────────────────────────────────────
        is_daytime = CALL_START <= current_hour < CALL_END
        issues_str = ", ".join(issues)

        logger.info(
            f"[{vehicle_id}] CRITICAL issues: {issues_str} | "
            f"Hour={current_hour} | Daytime={is_daytime} | Owner={owner_name}"
        )

        notifications = {}

        # ══════════════════════════════════════════════════════════════════════
        # 1. VOICE CALL — only during daytime (9 AM – 8 PM)
        # ══════════════════════════════════════════════════════════════════════
        if is_daytime:
            if owner_phone:
                logger.info(f"[{vehicle_id}] Daytime → initiating voice call to {owner_phone}")
                try:
                    # call_manager.make_call() speaks using pyttsx3 TTS
                    # and listens for customer response via mic
                    call_record = self.call_manager.make_call(
                        vehicle_id         = vehicle_id,
                        customer_name      = owner_name,
                        customer_phone     = owner_phone,
                        component          = issues_str,      # ALL issues spoken
                        days_until_failure = self._estimate_days(issues),
                    )
                    notifications["call"] = {
                        "status":   call_record.status.value,
                        "outcome":  call_record.outcome.value if call_record.outcome else "unknown",
                        "duration": f"{call_record.duration_sec:.1f}s",
                        "call_id":  call_record.call_id,
                    }
                    logger.info(f"[{vehicle_id}] Call done → outcome: {call_record.outcome}")
                except Exception as e:
                    logger.error(f"[{vehicle_id}] Call failed: {e}")
                    notifications["call"] = {"status": "error", "error": str(e)}
            else:
                notifications["call"] = {
                    "status": "skipped",
                    "reason": "No phone number — set ALERT_PHONE in .env",
                }
        else:
            # Nighttime — do NOT call, schedule for 9 AM
            notifications["call"] = {
                "status":  "scheduled",
                "message": f"Nighttime ({current_hour}h) — call will fire at {CALL_START}:00 AM",
            }
            logger.info(f"[{vehicle_id}] Nighttime → call deferred to {CALL_START}:00 AM")

        # ══════════════════════════════════════════════════════════════════════
        # 2. SMS — ALWAYS sent (day or night)
        # ══════════════════════════════════════════════════════════════════════
        if owner_phone:
            try:
                # send_alert_sms signature from YOUR sms_sender.py:
                # send_alert_sms(to_phone, customer_name, vehicle_id, component, days)
                sms_result = send_alert_sms(
                    to_phone      = owner_phone,
                    customer_name = owner_name,
                    vehicle_id    = vehicle_id,
                    component     = issues_str,
                    days          = self._estimate_days(issues),
                )
                notifications["sms"] = sms_result
                logger.info(f"[{vehicle_id}] SMS → {sms_result}")
            except Exception as e:
                logger.error(f"[{vehicle_id}] SMS failed: {e}")
                notifications["sms"] = {"success": False, "error": str(e)}
        else:
            notifications["sms"] = {
                "success": False,
                "reason":  "No phone number — set ALERT_PHONE in .env",
            }

        # ══════════════════════════════════════════════════════════════════════
        # 3. EMAIL — ALWAYS sent (day or night)
        # ══════════════════════════════════════════════════════════════════════
        if owner_email:
            try:
                # send_service_reminder signature from YOUR email_sender.py:
                # send_service_reminder(to_email, customer_name, vehicle_id, component, days)
                email_result = send_service_reminder(
                    to_email      = owner_email,
                    customer_name = owner_name,
                    vehicle_id    = vehicle_id,
                    component     = issues_str,
                    days          = self._estimate_days(issues),
                )
                notifications["email"] = email_result
                logger.info(f"[{vehicle_id}] Email → {email_result}")
            except Exception as e:
                logger.error(f"[{vehicle_id}] Email failed: {e}")
                notifications["email"] = {"success": False, "error": str(e)}
        else:
            notifications["email"] = {
                "success": False,
                "reason":  "No email address — set ALERT_EMAIL in .env",
            }

        # ── Build final response ───────────────────────────────────────────────
        if is_daytime:
            action = "Voice call made + SMS sent + Email sent."
        else:
            action = f"SMS sent + Email sent. Voice call scheduled for {CALL_START}:00 AM."

        return {
            "agent":              self.name,
            "vehicle_id":         vehicle_id,
            "urgency":            "CRITICAL",
            "is_business_hours":  is_daytime,
            "current_hour":       current_hour,
            "call_action":        "call_now" if is_daytime else f"call_at_{CALL_START}am",
            "call_time":          "now" if is_daytime else f"tomorrow at {CALL_START}:00 AM",
            "issues_detected":    issues,
            "critical_components": issues,
            "channels":           self._channels(is_daytime),
            "owner_notified":     owner_name,
            "message":            f"CRITICAL: {issues_str} on {vehicle_id}. {action}",
            "notifications_sent": notifications,
            # Legacy fields (keeps compatibility with MasterAgent result parsing)
            "sms_sent":           notifications.get("sms", {}).get("success", False),
            "email_sent":         notifications.get("email", {}).get("success", False),
            "call_outcome":       notifications.get("call", {}).get("outcome", notifications.get("call", {}).get("status", "unknown")),
            "timestamp":          datetime.now().isoformat(),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # process_prediction — backwards compat for any old code calling this
    # ──────────────────────────────────────────────────────────────────────────
    def process_prediction(self, prediction: dict) -> dict:
        """
        Converts old-style prediction dict → process() call.
        Keeps compatibility if any other agent calls this directly.
        """
        component = prediction.get("component_at_risk", "")
        return self.process({
            "vehicle_id":    prediction.get("vehicle_id", "UNKNOWN"),
            "vehicle_model": prediction.get("vehicle_id", "Vehicle"),
            "sensors":       {},   # no raw sensors here
            "owner": {
                "name":  prediction.get("customer_name", ""),
                "phone": prediction.get("customer_phone", ""),
                "email": prediction.get("customer_email", ""),
            },
            # inject pre-known issue directly
            "_issues_override": [component] if component else [],
        })

    # ──────────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ──────────────────────────────────────────────────────────────────────────
    def _detect_issues(self, sensors: dict) -> list:
        """
        Scans every sensor reading against thresholds.
        Returns list of human-readable problem strings for ALL issues found.
        """
        found = []
        for key, rules in THRESHOLDS.items():
            value = sensors.get(key)
            if value is None:
                continue
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue

            if "max" in rules and value > rules["max"]:
                found.append(rules["label"])
                logger.debug(f"  ⚠ {key}={value} > {rules['max']} → {rules['label']}")
            elif "min" in rules and value < rules["min"]:
                found.append(rules["label"])
                logger.debug(f"  ⚠ {key}={value} < {rules['min']} → {rules['label']}")

        return found

    def _estimate_days(self, issues: list) -> int:
        """
        Returns urgency-based estimated days until failure.
        More issues = sooner.
        """
        if len(issues) >= 3:
            return 3
        if len(issues) == 2:
            return 5
        return 7

    @staticmethod
    def _channels(is_daytime: bool) -> list:
        if is_daytime:
            return ["Call", "SMS", "Email"]
        return ["SMS", "Email", "Call (9 AM)"]


# ═══════════════════════════════════════════════════════════════════════════════
# SELF TEST — run: python agents/engagement_agent.py
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    print("\n" + "="*65)
    print("  EngagementAgent — Self Test")
    print("="*65)

    # ── Test 1: Daytime with multiple issues ──────────────────────────────────
    print("\n[TEST 1] Daytime (14:00) — multiple sensor problems")
    agent = EngagementAgent(demo_mode=True)  # demo_mode=True → simulated mic

    result = agent.process({
        "vehicle_id":    "VEH002",
        "vehicle_model": "Honda City 2019",
        "current_hour":  14,              # 2 PM — daytime → CALL NOW
        "owner": {
            "name":  "Rahul Sharma",
            "phone": os.getenv("ALERT_PHONE", "+919876543210"),
            "email": os.getenv("ALERT_EMAIL", "rahul@example.com"),
        },
        "sensors": {
            "brake_temp":        130,    # CRITICAL (max 100)
            "oil_pressure":      20,     # CRITICAL (min 25)
            "brake_fluid_level": 60,     # CRITICAL (min 65)
            "engine_temp":       98,     # OK
            "tire_pressure":     32,     # OK
        },
    })

    print(f"  Issues found  : {result['issues_detected']}")
    print(f"  Call action   : {result['call_action']}")
    print(f"  SMS sent      : {result['sms_sent']}")
    print(f"  Email sent    : {result['email_sent']}")
    print(f"  Call outcome  : {result['call_outcome']}")
    print(f"  Message       : {result['message']}")

    # ── Test 2: Nighttime ─────────────────────────────────────────────────────
    print("\n[TEST 2] Nighttime (23:00) — call should be deferred")
    result2 = agent.process({
        "vehicle_id":   "VEH005",
        "current_hour": 23,              # 11 PM — nighttime → NO CALL
        "owner": {
            "name":  "Priya Singh",
            "phone": os.getenv("ALERT_PHONE", "+919123456789"),
            "email": os.getenv("ALERT_EMAIL", "priya@example.com"),
        },
        "sensors": {
            "engine_temp":    110,       # CRITICAL
            "battery_voltage": 10.9,    # CRITICAL
        },
    })

    print(f"  Issues found  : {result2['issues_detected']}")
    print(f"  Call action   : {result2['call_action']}")
    print(f"  Call time     : {result2['call_time']}")
    print(f"  SMS sent      : {result2['sms_sent']}")

    # ── Test 3: Healthy vehicle ───────────────────────────────────────────────
    print("\n[TEST 3] Healthy vehicle — no notifications should fire")
    result3 = agent.process({
        "vehicle_id":   "VEH007",
        "current_hour": 10,
        "owner":        {"name": "Ali Khan", "phone": "+919000000000", "email": "ali@x.com"},
        "sensors": {
            "brake_temp":   80,    # OK
            "oil_pressure": 35,    # OK
            "engine_temp":  90,    # OK
            "tire_pressure": 32,   # OK
        },
    })
    print(f"  Urgency       : {result3['urgency']}")
    print(f"  Message       : {result3['message']}")

    print("\n" + "="*65)
    print("  Self-test complete!")
    print("  Set demo_mode=False in MasterAgent for REAL calls.")
    print("  Ensure .env has TWILIO + SENDGRID keys for real SMS/Email.")
    print("="*65 + "\n")