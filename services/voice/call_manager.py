"""
<<<<<<< HEAD
services/voice/call_manager.py — REAL PHONE CALLS via Twilio
─────────────────────────────────────────────────────────────
Replaces the pyttsx3 local-speaker version with actual Twilio phone calls.

How it works:
  1. Twilio calls the owner's real phone number
  2. When they answer, Twilio reads the alert using Text-to-Speech (no mic needed)
  3. Owner presses 1 to book, 2 to decline, 3 for agent
  4. Response is captured via DTMF (keypad tones) — no mic/speech recognition needed
  5. Result returned to EngagementAgent

This means: NO microphone, NO Whisper, NO local audio — just a real phone call.

Requirements:
  pip install twilio
  .env must have: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

IMPORTANT: Your FastAPI server must be publicly accessible for Twilio webhooks.
  Option A (hackathon): Use ngrok → ngrok http 8000 → get public URL
  Option B (no webhook): Use Twilio's <Gather> with action URL pointing to your server
  Option C (simplest):  Use answering machine mode — Twilio speaks, no response needed
"""

import os
=======
FILE 4: services/voice/call_manager.py
PURPOSE: Orchestrates the complete voice call loop.
         Speaks → Listens → Understands → Responds → Routes.
         This is the brain that connects TTS + STT into a real conversation.
CONNECTS TO:
  - services/voice/text_to_speech.py          (FILE 2 — speaks to customer)
  - services/voice/speech_to_text.py          (FILE 3 — listens to customer)
  - services/agents/config/hf_model_config.py (FILE 1 — settings)
  - services/agents/workers/engagement_agent.py (FILE 8 — calls make_call())
  - services/agents/workers/scheduling_agent.py (FILE 9 — called after booking intent)
AUTHOR: Person 4
"""

>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

<<<<<<< HEAD
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
# Your public URL (from ngrok or deployment) — needed for interactive calls
# If empty, falls back to one-way announcement call (no keypress needed)
PUBLIC_URL = os.getenv("PUBLIC_URL", "")


class CallStatus(Enum):
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    TRANSFERRED = "transferred"


class CallOutcome(Enum):
    APPOINTMENT_BOOKED = "appointment_booked"
    APPOINTMENT_DECLINED = "appointment_declined"
    FEEDBACK_COLLECTED = "feedback_collected"
    TRANSFERRED_AGENT = "transferred_to_agent"
    CALL_FAILED = "call_failed"
    NO_RESPONSE = "no_response"
    ANNOUNCED = "announced"  # one-way announcement, no response needed
=======
from services.agents.config.hf_model_config import BACKEND_BASE_URL
from services.voice.text_to_speech import (
    speak,
    speak_service_alert,
    speak_appointment_confirmation,
    speak_feedback_request,
)
from services.voice.speech_to_text import (
    listen,
    extract_intent,
    transcribe_demo_text,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# SECTION 1: Data Structures
# ==============================================================================

class CallStatus(Enum):
    """All possible states a call can be in."""
    INITIATED    = "initiated"
    IN_PROGRESS  = "in_progress"
    COMPLETED    = "completed"
    FAILED       = "failed"
    NO_ANSWER    = "no_answer"
    TRANSFERRED  = "transferred"   # Routed to human agent


class CallOutcome(Enum):
    """What happened at the end of the call."""
    APPOINTMENT_BOOKED   = "appointment_booked"
    APPOINTMENT_DECLINED = "appointment_declined"
    FEEDBACK_COLLECTED   = "feedback_collected"
    TRANSFERRED_AGENT    = "transferred_to_agent"
    CALL_FAILED          = "call_failed"
    NO_RESPONSE          = "no_response"
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73


@dataclass
class CallRecord:
<<<<<<< HEAD
    call_id: str
    vehicle_id: str
    customer_name: str
    customer_phone: str
    call_reason: str
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    status: CallStatus = CallStatus.INITIATED
    outcome: Optional[CallOutcome] = None
    transcript: list = field(default_factory=list)
    duration_sec: float = 0.0
    twilio_call_sid: str = ""

    def add_transcript(self, speaker: str, text: str):
        self.transcript.append({
            "speaker": speaker,
            "text": text,
=======
    """
    Complete record of one customer call.
    Saved after every call for audit trail + analytics.
    """
    call_id:        str
    vehicle_id:     str
    customer_name:  str
    customer_phone: str
    call_reason:    str              # e.g. "brake_failure_alert"
    started_at:     datetime         = field(default_factory=datetime.now)
    ended_at:       Optional[datetime] = None
    status:         CallStatus       = CallStatus.INITIATED
    outcome:        Optional[CallOutcome] = None
    transcript:     list             = field(default_factory=list)
    duration_sec:   float            = 0.0
    retry_count:    int              = 0

    def add_transcript(self, speaker: str, text: str):
        """Add a line to the call transcript."""
        self.transcript.append({
            "speaker":   speaker,   # "agent" or "customer"
            "text":      text,
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
            "timestamp": datetime.now().isoformat(),
        })

    def close(self, outcome: CallOutcome):
<<<<<<< HEAD
        self.ended_at = datetime.now()
        self.outcome = outcome
        self.duration_sec = (self.ended_at - self.started_at).total_seconds()
        self.status = CallStatus.COMPLETED


class CallManager:
    """
    Makes REAL phone calls via Twilio.

    Two modes:
      1. ANNOUNCEMENT (no PUBLIC_URL set):
         Calls phone, speaks full alert, asks to press 1 or 2.
         Result checked after 30s via Twilio API.

      2. INTERACTIVE (PUBLIC_URL set via ngrok):
         Full interactive call with keypress routing.
         Twilio posts result to your webhook endpoint.
    """

    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        self._call_log = []
        logger.info(f"CallManager (Twilio) initialized | demo_mode={demo_mode}")

    def make_call(
            self,
            vehicle_id: str,
            customer_name: str,
            customer_phone: str,
            component: str,
            days_until_failure: int,
            on_booking_intent: Optional[Callable] = None,
    ) -> CallRecord:
        """
        Make a real Twilio phone call to the vehicle owner.
        Phone WILL RING. Owner hears Sarah's voice message.
        """
        call_id = f"CALL_{vehicle_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        record = CallRecord(
            call_id=call_id,
            vehicle_id=vehicle_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            call_reason=f"{component}_alert",
        )

        if self.demo_mode:
            return self._demo_call(record, component, days_until_failure)

        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            logger.error("Twilio credentials missing in .env")
            record.outcome = CallOutcome.CALL_FAILED
            record.status = CallStatus.FAILED
            return record

        try:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            # Build the spoken message
            twiml = self._build_twiml(
                customer_name=customer_name,
                vehicle_id=vehicle_id,
                component=component,
                days_until_failure=days_until_failure,
            )

            call = client.calls.create(
                twiml=twiml,
                to=customer_phone,
                from_=TWILIO_PHONE_NUMBER,
            )

            record.twilio_call_sid = call.sid
            record.status = CallStatus.IN_PROGRESS
            logger.info(f"📞 Call initiated | SID={call.sid} | to={customer_phone}")
            record.add_transcript("system", f"Call initiated via Twilio | SID: {call.sid}")

            # Wait and check call outcome
            outcome = self._wait_for_outcome(client, call.sid, record)
            record.close(outcome)

            # Fire booking callback if customer pressed 1
            if outcome == CallOutcome.APPOINTMENT_BOOKED and on_booking_intent:
                try:
                    on_booking_intent(
                        vehicle_id=vehicle_id,
                        customer_name=customer_name,
                        component=component,
                        date=self._next_available_date(),
                        time_slot="10:00",
                    )
                except Exception as e:
                    logger.warning(f"Booking callback failed: {e}")

        except ImportError:
            logger.error("twilio not installed: pip install twilio")
            record.outcome = CallOutcome.CALL_FAILED
            record.status = CallStatus.FAILED

        except Exception as e:
            logger.error(f"Twilio call failed: {e}")
            record.outcome = CallOutcome.CALL_FAILED
            record.status = CallStatus.FAILED

        self._call_log.append(record)
        return record

    # ──────────────────────────────────────────────────────────────────────────
    # TwiML — the spoken script Twilio reads to the customer
    # ──────────────────────────────────────────────────────────────────────────
    def _build_twiml(
            self,
            customer_name: str,
            vehicle_id: str,
            component: str,
            days_until_failure: int,
    ) -> str:
        """
        Builds TwiML — Twilio reads this aloud using Alice's voice (Indian English).
        Customer presses 1 to book, 2 to decline.
        """
        # Clean component text for speech
        component_spoken = component.replace("_", " ").replace(",", ",")

        if PUBLIC_URL:
            # Interactive — gather keypress, post to webhook
            action_url = f"{PUBLIC_URL}/twilio/gather/{vehicle_id}"
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">
    Hello {customer_name}. This is Sarah calling from AutoNexus, 
    your vehicle health monitoring service.
  </Say>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">
    I am calling regarding your vehicle {vehicle_id}.
    Our AI system has detected critical issues with your {component_spoken}.
    These issues may cause failure within {days_until_failure} days 
    if not attended to.
  </Say>
  <Pause length="1"/>
  <Gather numDigits="1" action="{action_url}" method="POST" timeout="10">
    <Say voice="Polly.Aditi" language="en-IN">
      To book an emergency service appointment right now, please press 1.
      To decline and receive details by SMS, please press 2.
      To speak with our service advisor, please press 3.
    </Say>
  </Gather>
  <Say voice="Polly.Aditi" language="en-IN">
    We did not receive your response. 
    We will send you the details by SMS and email.
    Our team will follow up tomorrow morning. 
    Thank you. Goodbye.
  </Say>
</Response>"""
        else:
            # Announcement only — no keypress, just speaks and hangs up
            # Booking is done via SMS link or frontend
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">
    Hello {customer_name}. This is Sarah calling from AutoNexus, 
    your vehicle health monitoring service.
  </Say>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">
    I am calling with an urgent alert about your vehicle {vehicle_id}.
  </Say>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">
    Our AI system has detected critical problems with your {component_spoken}.
    This requires immediate attention within {days_until_failure} days.
    Please do not drive this vehicle until it has been serviced.
  </Say>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">
    We have sent you a detailed SMS and email with full information 
    and a link to book your service appointment immediately.
    Please check your messages now.
  </Say>
  <Pause length="1"/>
  <Say voice="Polly.Aditi" language="en-IN">
    If you have any questions, please call us at 1800 AUTO NEX.
    Thank you for being an AutoNexus customer. 
    We look forward to getting your vehicle back to perfect health.
    Goodbye and stay safe.
  </Say>
</Response>"""

        return twiml

    # ──────────────────────────────────────────────────────────────────────────
    def _wait_for_outcome(self, client, call_sid: str, record: CallRecord) -> CallOutcome:
        """
        Poll Twilio API to check if call was answered and completed.
        Returns outcome based on call status.
        """
        max_wait = 60  # seconds
        interval = 5
        elapsed = 0

        while elapsed < max_wait:
            time.sleep(interval)
            elapsed += interval
            try:
                call = client.calls(call_sid).fetch()
                logger.info(f"Call {call_sid} status: {call.status}")

                if call.status == "completed":
                    record.add_transcript("system", f"Call completed | duration: {call.duration}s")
                    # If interactive + PUBLIC_URL: outcome set by webhook
                    # If announcement: outcome = announced (we spoke, they heard)
                    return CallOutcome.ANNOUNCED if not PUBLIC_URL else CallOutcome.APPOINTMENT_BOOKED

                elif call.status in ["busy", "no-answer", "failed", "canceled"]:
                    record.add_transcript("system", f"Call ended: {call.status}")
                    return CallOutcome.NO_RESPONSE

            except Exception as e:
                logger.warning(f"Status check failed: {e}")
                break

        return CallOutcome.NO_RESPONSE

    # ──────────────────────────────────────────────────────────────────────────
    def _demo_call(self, record: CallRecord, component: str, days: int) -> CallRecord:
        logger.info(
            f"[DEMO CALL] Would call {record.customer_phone} | "
            f"Vehicle: {record.vehicle_id} | Component: {component}"
        )
        print(
            f"\n📞 [DEMO] TWILIO CALL TO: {record.customer_phone}\n"
            f"   Sarah would say: URGENT alert for {record.customer_name} — "
            f"{record.vehicle_id} has critical issues: {component}.\n"
            f"   (Set DEMO_MODE=false in .env for real calls)\n"
        )
        record.close(CallOutcome.ANNOUNCED)
        return record

    @staticmethod
    def _next_available_date() -> str:
        from datetime import timedelta
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    def get_call_history(self):
        return self._call_log

    def get_call_stats(self) -> dict:
        total = len(self._call_log)
        if not total:
            return {"total": 0}
        return {
            "total": total,
            "announced": sum(1 for c in self._call_log if c.outcome == CallOutcome.ANNOUNCED),
            "booked": sum(1 for c in self._call_log if c.outcome == CallOutcome.APPOINTMENT_BOOKED),
            "failed": sum(1 for c in self._call_log if c.outcome == CallOutcome.CALL_FAILED),
        }
=======
        """Mark call as finished."""
        self.ended_at    = datetime.now()
        self.outcome     = outcome
        self.duration_sec = (self.ended_at - self.started_at).total_seconds()
        self.status      = CallStatus.COMPLETED


# ==============================================================================
# SECTION 2: Core Call Manager Class
# ==============================================================================

class CallManager:
    """
    Manages the complete lifecycle of a voice call.

    Usage:
        manager = CallManager()
        record  = manager.make_call(
            vehicle_id     = "VEH001",
            customer_name  = "Rahul Sharma",
            customer_phone = "+91-9876543210",
            component      = "brakes",
            days_until_failure = 7,
        )
        print(record.outcome)
    """

    MAX_RETRIES     = 2    # Retry call this many times if no answer
    LISTEN_DURATION = 6    # Seconds to listen for customer response
    MAX_TURNS       = 5    # Max back-and-forth turns before ending call

    def __init__(self, demo_mode: bool = False):
        """
        Args:
            demo_mode: If True, uses simulated responses instead of real mic.
                       Set to True for hackathon demo, False for production.
        """
        self.demo_mode    = demo_mode
        self._call_log: list[CallRecord] = []   # In-memory call history
        logger.info(f"CallManager initialized | demo_mode={demo_mode}")

    # ── Main entry point ───────────────────────────────────────────────────────

    def make_call(
        self,
        vehicle_id:         str,
        customer_name:      str,
        customer_phone:     str,
        component:          str,
        days_until_failure: int,
        on_booking_intent:  Optional[Callable] = None,
    ) -> CallRecord:
        """
        Make a complete voice call to a customer about their vehicle.

        Args:
            vehicle_id          : e.g. "VEH001"
            customer_name       : e.g. "Rahul Sharma"
            customer_phone      : e.g. "+91-9876543210"
            component           : e.g. "brakes", "engine", "oil"
            days_until_failure  : e.g. 7
            on_booking_intent   : Optional callback when customer says yes to booking

        Returns:
            CallRecord with full transcript and outcome
        """
        call_id = f"CALL_{vehicle_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        record  = CallRecord(
            call_id        = call_id,
            vehicle_id     = vehicle_id,
            customer_name  = customer_name,
            customer_phone = customer_phone,
            call_reason    = f"{component}_failure_alert",
        )

        logger.info(
            f"Initiating call | id={call_id} | customer={customer_name} "
            f"| vehicle={vehicle_id} | component={component} | days={days_until_failure}"
        )

        record.status = CallStatus.IN_PROGRESS

        try:
            outcome = self._run_service_alert_call(
                record             = record,
                component          = component,
                days_until_failure = days_until_failure,
                on_booking_intent  = on_booking_intent,
            )
            record.close(outcome)

        except Exception as e:
            logger.error(f"Call {call_id} failed with exception: {e}")
            record.status  = CallStatus.FAILED
            record.outcome = CallOutcome.CALL_FAILED
            record.ended_at = datetime.now()

        self._call_log.append(record)
        self._log_call_summary(record)
        return record

    # ── Call flow: Service Alert ───────────────────────────────────────────────

    def _run_service_alert_call(
        self,
        record:             CallRecord,
        component:          str,
        days_until_failure: int,
        on_booking_intent:  Optional[Callable],
    ) -> CallOutcome:
        """
        Full call script for a vehicle service alert.

        Flow:
          1. Greet customer + state reason for call
          2. Listen for response
          3. If YES → offer booking → confirm
          4. If NO  → log declined, end politely
          5. If AGENT → transfer
          6. If no response → retry up to MAX_RETRIES
        """

        # ── Turn 1: Opening greeting + alert ──────────────────────────────────
        opening = (
            f"Hello, may I speak with {record.customer_name}? "
            f"This is AutoNexus, your vehicle health monitoring service. "
            f"I'm calling regarding your vehicle {record.vehicle_id}. "
            f"Our system has detected that your {component} may require "
            f"attention within the next {days_until_failure} days. "
            f"Would you like to schedule a service appointment? "
            f"Say yes to book, no to decline, or agent to speak with our team."
        )
        self._agent_speak(record, opening)

        # ── Turn 2: Listen for initial response ───────────────────────────────
        response = self._customer_listen(
            record,
            demo_text="Yes please book an appointment"
        )

        if not response["success"] or not response["text"]:
            # No response — retry once
            speak("I'm sorry, I didn't catch that. Could you please repeat?")
            response = self._customer_listen(
                record,
                demo_text="Yes book it"
            )
            if not response["success"]:
                self._agent_speak(
                    record,
                    "I'm unable to hear your response. "
                    "We'll send you an SMS with details. Goodbye!"
                )
                return CallOutcome.NO_RESPONSE

        intent = extract_intent(response["text"])
        logger.info(f"Customer intent: {intent['intent']} | text: '{response['text']}'")

        # ── Route based on intent ──────────────────────────────────────────────
        if intent["intent"] == "book_appointment":
            return self._handle_booking_intent(
                record, component, on_booking_intent
            )

        elif intent["intent"] == "cancel":
            return self._handle_decline(record, component)

        elif intent["intent"] == "speak_agent":
            return self._handle_transfer(record)

        else:
            # Unclear response — ask once more
            self._agent_speak(
                record,
                "I'm sorry, I didn't quite understand. "
                "Please say yes to book a service, no to decline, "
                "or agent to speak with our team."
            )
            response2 = self._customer_listen(record, demo_text="yes")
            intent2   = extract_intent(response2["text"])

            if intent2["intent"] == "book_appointment":
                return self._handle_booking_intent(
                    record, component, on_booking_intent
                )
            elif intent2["intent"] == "cancel":
                return self._handle_decline(record, component)
            else:
                self._agent_speak(
                    record,
                    "Thank you for your time. We'll send you details via SMS. Goodbye!"
                )
                return CallOutcome.APPOINTMENT_DECLINED

    # ── Sub-handlers ──────────────────────────────────────────────────────────

    def _handle_booking_intent(
        self,
        record:            CallRecord,
        component:         str,
        on_booking_intent: Optional[Callable],
    ) -> CallOutcome:
        """Customer said yes — confirm and book."""
        self._agent_speak(
            record,
            f"Excellent! I'll arrange a {component} service appointment for you. "
            f"Our next available slot is Monday at 10 AM at AutoNexus Central. "
            f"Shall I confirm this booking?"
        )

        confirm_response = self._customer_listen(record, demo_text="yes confirm it")
        confirm_intent   = extract_intent(confirm_response["text"])

        if confirm_intent["intent"] in ["confirm", "book_appointment"]:
            speak_appointment_confirmation(
                customer_name  = record.customer_name,
                date           = "Monday March 10th",
                time_slot      = "10 AM",
                service_center = "AutoNexus Central",
            )
            record.add_transcript("agent", "Appointment confirmed and SMS sent.")

            # Fire callback so scheduling_agent can persist the booking
            if on_booking_intent:
                try:
                    on_booking_intent(
                        vehicle_id    = record.vehicle_id,
                        customer_name = record.customer_name,
                        component     = component,
                        date          = "2026-03-10",
                        time_slot     = "10:00",
                    )
                    logger.info("Booking callback fired successfully")
                except Exception as e:
                    logger.warning(f"Booking callback failed (non-critical): {e}")

            return CallOutcome.APPOINTMENT_BOOKED

        else:
            self._agent_speak(
                record,
                "No problem. We'll send you our available slots via SMS "
                "so you can choose a convenient time. Goodbye!"
            )
            return CallOutcome.APPOINTMENT_DECLINED

    def _handle_decline(self, record: CallRecord, component: str) -> CallOutcome:
        """Customer said no."""
        self._agent_speak(
            record,
            f"Understood. Please be aware that your {component} may need attention soon. "
            f"We'll send you a reminder in 3 days. "
            f"You can always call us at AutoNexus to book. Thank you and goodbye!"
        )
        return CallOutcome.APPOINTMENT_DECLINED

    def _handle_transfer(self, record: CallRecord) -> CallOutcome:
        """Customer wants a human."""
        self._agent_speak(
            record,
            "Of course! I'll transfer you to our service team right away. "
            "Please hold for a moment."
        )
        record.status = CallStatus.TRANSFERRED
        logger.info(f"Call {record.call_id} transferred to human agent")
        return CallOutcome.TRANSFERRED_AGENT

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _agent_speak(self, record: CallRecord, text: str):
        """Speak text and log to transcript."""
        record.add_transcript("agent", text)
        speak(text)

    def _customer_listen(
        self,
        record:    CallRecord,
        demo_text: str = "yes",
    ) -> dict:
        """
        Listen to customer and log to transcript.
        In demo_mode: uses demo_text instead of real mic.
        """
        if self.demo_mode:
            time.sleep(0.8)   # Simulate realistic pause
            result = transcribe_demo_text(demo_text)
        else:
            result = listen(duration=self.LISTEN_DURATION)

        if result["text"]:
            record.add_transcript("customer", result["text"])

        return result

    # ── Analytics ─────────────────────────────────────────────────────────────

    def get_call_history(self) -> list[CallRecord]:
        """Returns all calls made this session."""
        return self._call_log

    def get_call_stats(self) -> dict:
        """Summary statistics of all calls this session."""
        total    = len(self._call_log)
        if total == 0:
            return {"total": 0}

        booked   = sum(1 for c in self._call_log if c.outcome == CallOutcome.APPOINTMENT_BOOKED)
        declined = sum(1 for c in self._call_log if c.outcome == CallOutcome.APPOINTMENT_DECLINED)
        failed   = sum(1 for c in self._call_log if c.outcome == CallOutcome.CALL_FAILED)
        avg_dur  = sum(c.duration_sec for c in self._call_log) / total

        return {
            "total":           total,
            "booked":          booked,
            "declined":        declined,
            "failed":          failed,
            "booking_rate_%":  round(booked / total * 100, 1),
            "avg_duration_s":  round(avg_dur, 1),
        }

    def _log_call_summary(self, record: CallRecord):
        """Print a clean summary after each call."""
        logger.info(
            f"Call complete | id={record.call_id} | "
            f"outcome={record.outcome.value if record.outcome else 'unknown'} | "
            f"duration={record.duration_sec:.1f}s | "
            f"turns={len(record.transcript)}"
        )


# ==============================================================================
# SELF-TEST
# Run: python services/voice/call_manager.py
# Simulates a full customer call in demo mode (no real mic/phone needed).
# You will HEAR the agent speak each turn of the conversation.
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FILE 4: Call Manager — Self Test (DEMO MODE)")
    print("="*60)

    # Create manager in demo mode — uses simulated customer responses
    manager = CallManager(demo_mode=True)

    print("\n[1] Simulating service alert call for VEH001 (brake failure)...")
    print("    You will hear the full call conversation.\n")
    time.sleep(1)

    record = manager.make_call(
        vehicle_id         = "VEH001",
        customer_name      = "Rahul Sharma",
        customer_phone     = "+91-9876543210",
        component          = "brakes",
        days_until_failure = 7,
    )

    print(f"\n  Call ID    : {record.call_id}")
    print(f"  Status     : {record.status.value}")
    print(f"  Outcome    : {record.outcome.value if record.outcome else 'N/A'}")
    print(f"  Duration   : {record.duration_sec:.1f} seconds")
    print(f"  Turns      : {len(record.transcript)}")

    print("\n  Full Transcript:")
    for line in record.transcript:
        speaker = "🤖 Agent   " if line["speaker"] == "agent" else "👤 Customer"
        print(f"    {speaker}: {line['text'][:70]}")

    print("\n[2] Testing a declined call...")
    time.sleep(1)

    # Override demo to simulate customer saying NO
    manager2 = CallManager(demo_mode=True)
    # Monkey-patch to simulate decline
    original_listen = manager2._customer_listen
    call_count = [0]
    def mock_decline(record, demo_text="yes"):
        call_count[0] += 1
        if call_count[0] == 1:
            return transcribe_demo_text("No I don't want service right now")
        return transcribe_demo_text("no cancel")
    manager2._customer_listen = mock_decline

    record2 = manager2.make_call(
        vehicle_id         = "VEH002",
        customer_name      = "Priya Singh",
        customer_phone     = "+91-9123456789",
        component          = "engine oil",
        days_until_failure = 14,
    )
    print(f"  Outcome: {record2.outcome.value if record2.outcome else 'N/A'}")

    print("\n[3] Call Statistics:")
    stats = manager.get_call_stats()
    for k, v in stats.items():
        print(f"    {k:<20}: {v}")

    print("\n" + "="*60)
    print("  FILE 4 self-test complete!")
    print("  If you heard full conversation + saw transcript — commit ✅")
    print("="*60 + "\n")
>>>>>>> d60c5abde7246fb5a06ce796ac3be5e2c92cec73
