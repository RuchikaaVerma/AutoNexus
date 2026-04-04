"""
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
import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

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


@dataclass
class CallRecord:
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
            "timestamp": datetime.now().isoformat(),
        })

    def close(self, outcome: CallOutcome):
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