"""
services/voice/text_to_speech.py  — UPGRADED
─────────────────────────────────────────────
Human-sounding voice with warm greeting, natural pauses, proper tone.
Uses pyttsx3 (offline, no API key needed, works on Windows).

DROP THIS FILE into: F:\\automotive-backend\\services\\voice\\text_to_speech.py
"""

import time
import logging
import os

logger = logging.getLogger(__name__)

# ── Try to load pyttsx3 ───────────────────────────────────────────────────────
try:
    import pyttsx3
    _engine = pyttsx3.init()

    # ── Voice selection: prefer a female voice (sounds more professional) ─────
    voices = _engine.getProperty("voices")
    selected_voice = None

    # Priority: female English voice first
    for v in voices:
        name = v.name.lower()
        if any(w in name for w in ["zira", "hazel", "susan", "female", "woman", "india"]):
            selected_voice = v.id
            break

    # Fallback: any English voice
    if not selected_voice:
        for v in voices:
            if "english" in v.name.lower() or "en" in v.id.lower():
                selected_voice = v.id
                break

    if selected_voice:
        _engine.setProperty("voice", selected_voice)
        logger.info(f"Voice selected: {selected_voice}")

    # Natural speaking rate — not too fast, not robotic
    _engine.setProperty("rate",   148)   # words per minute (human avg = 130-150)
    _engine.setProperty("volume", 1.0)   # full volume

    TTS_AVAILABLE = True
    logger.info("pyttsx3 TTS engine ready")

except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 not installed — run: pip install pyttsx3")
except Exception as e:
    TTS_AVAILABLE = False
    logger.warning(f"TTS engine init failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# CORE SPEAK FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def speak(text: str, pause_after: float = 0.4):
    """
    Speak text aloud using pyttsx3.
    Falls back to print if TTS not available.

    Args:
        text        : text to speak
        pause_after : seconds to wait after speaking (natural conversation gap)
    """
    if not text:
        return

    # Clean text for natural speech (remove markdown, extra spaces)
    clean = (
        text.replace("**", "")
            .replace("*", "")
            .replace("_", "")
            .replace("#", "")
            .strip()
    )

    logger.debug(f"Speaking: {clean[:60]}...")

    if TTS_AVAILABLE:
        try:
            _engine.say(clean)
            _engine.runAndWait()
            time.sleep(pause_after)
        except Exception as e:
            logger.error(f"TTS speak error: {e}")
            print(f"[AGENT]: {clean}")
    else:
        print(f"\n🔊 [AGENT SPEAKING]: {clean}\n")
        time.sleep(pause_after)


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIALISED SPEAK FUNCTIONS — used by call_manager.py
# ═══════════════════════════════════════════════════════════════════════════════

def speak_service_alert(
    customer_name: str,
    vehicle_id: str,
    component: str,
    days_until_failure: int,
):
    """
    Warm, human-sounding opening alert call script.
    Friendly but urgent — like a caring service advisor calling.
    """
    # Natural multi-part delivery with slight pauses between sentences
    parts = [
        f"Hello! May I please speak with {customer_name}?",

        "This is Sarah calling from AutoNexus, your vehicle health monitoring service. "
        "I hope I haven't caught you at a bad time.",

        f"I'm calling about your vehicle, {vehicle_id}. "
        f"Our AI monitoring system has flagged something important "
        f"that I wanted to make sure you knew about right away.",

        f"We've detected that your {component} is showing some concerning readings "
        f"and may need attention within the next {days_until_failure} days.",

        "I know that sounds worrying, but the good news is — "
        "because we caught it early, it's much easier and less expensive to fix now "
        "than if we wait.",

        "I'd love to help you get a service appointment booked today. "
        "Would that work for you? "
        "You can say yes to book, no if you'd prefer to wait, "
        "or just say agent if you'd like to speak with one of our service advisors.",
    ]

    for part in parts:
        speak(part, pause_after=0.6)


def speak_appointment_confirmation(
    customer_name: str,
    date: str,
    time_slot: str,
    service_center: str,
):
    """
    Warm confirmation after customer agrees to book.
    """
    parts = [
        f"Wonderful! I've gone ahead and booked that for you, {customer_name}.",

        f"Your service appointment is confirmed for {date} at {time_slot} "
        f"at our {service_center} location.",

        "You'll receive a confirmation SMS and email shortly with all the details, "
        "including the address and a reminder the day before.",

        "Is there anything else I can help you with today?",

        f"Brilliant. Thank you so much for your time, {customer_name}. "
        "We'll see you soon, and please do take care. Goodbye!",
    ]

    for part in parts:
        speak(part, pause_after=0.5)


def speak_feedback_request(customer_name: str, vehicle_id: str):
    """
    Friendly post-service feedback call.
    """
    parts = [
        f"Hello {customer_name}, this is Sarah from AutoNexus.",

        f"I'm calling because your vehicle {vehicle_id} was recently serviced with us, "
        "and I just wanted to check in and make sure everything went smoothly.",

        "How has the vehicle been feeling since the service? "
        "Say great if you're happy, or say issue if there's something we should know about.",
    ]

    for part in parts:
        speak(part, pause_after=0.6)


def speak_decline_response(customer_name: str, component: str):
    """
    Respectful response when customer declines booking.
    """
    parts = [
        "Of course, absolutely no pressure at all.",

        f"I do want to gently mention that the {component} issue can sometimes progress "
        "quickly, so please do keep an eye on it.",

        "I'll make sure we send you a follow-up reminder in a couple of days, "
        "and whenever you're ready to book, you can reach us any time "
        "or visit our website.",

        f"Thank you for your time, {customer_name}. "
        "Take care and have a wonderful day. Goodbye!",
    ]

    for part in parts:
        speak(part, pause_after=0.5)


def speak_transfer_message():
    """When customer asks for a human agent."""
    parts = [
        "Of course! I'll connect you with one of our service advisors right away.",
        "Please hold for just a moment — they'll be with you shortly.",
    ]
    for part in parts:
        speak(part, pause_after=0.5)


def speak_no_response_farewell():
    """When customer doesn't respond."""
    speak(
        "I'm so sorry, I'm having a little trouble hearing you. "
        "Not to worry — I'll send you a full summary by SMS and email right away, "
        "and you can call us back whenever is convenient. "
        "Take care. Goodbye!",
        pause_after=0.3,
    )


def speak_nighttime_sms_notice(customer_name: str):
    """
    Used if we ever do a late follow-up call at 9 AM.
    """
    parts = [
        f"Good morning, {customer_name}! This is Sarah from AutoNexus.",

        "I'm calling this morning because our system detected a vehicle alert last night, "
        "and I wanted to make sure you received our message.",

        "We sent you an SMS and email with full details. "
        "Would you like to go ahead and book a service appointment now?",
    ]
    for part in parts:
        speak(part, pause_after=0.6)


# ═══════════════════════════════════════════════════════════════════════════════
# SELF TEST
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  text_to_speech.py — Voice Test")
    print("="*60)
    print("  You should HEAR the agent speaking...\n")

    speak_service_alert(
        customer_name      = "Rahul",
        vehicle_id         = "VEH002",
        component          = "brake system and engine oil pressure",
        days_until_failure = 5,
    )

    time.sleep(1)

    speak_appointment_confirmation(
        customer_name  = "Rahul",
        date           = "this Monday",
        time_slot      = "10 AM",
        service_center = "AutoNexus Central",
    )

    print("\n  ✅ Voice test complete!")
    print("="*60 + "\n")