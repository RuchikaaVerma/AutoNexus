"""
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

import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

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


@dataclass
class CallRecord:
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
            "timestamp": datetime.now().isoformat(),
        })

    def close(self, outcome: CallOutcome):
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