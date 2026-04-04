"""
FILE 2: services/voice/text_to_speech.py
PURPOSE: Converts text to speech for customer-facing voice calls.
         Uses pyttsx3 (fully offline, no API key, works on Windows).
CONNECTS TO:
  - services/voice/call_manager.py         (FILE 4 — uses speak())
  - services/agents/workers/engagement_agent.py (FILE 8 — uses speak())
  - services/agents/config/hf_model_config.py   (FILE 1 — reads TTS settings)
AUTHOR: Person 4
"""

import os
import time
import logging
import threading
from pathlib import Path
from datetime import datetime

import pyttsx3

from services.agents.config.hf_model_config import (
    TTS_ENGINE,
    VOICE_SPEED_RATE,
    VOICE_LANGUAGE,
    AUDIO_RECORDINGS_DIR,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# SECTION 1: Engine Initializer
# pyttsx3 is NOT thread-safe — we use a lock to prevent crashes
# when multiple agents try to speak at the same time.
# ==============================================================================

_engine = None
_engine_lock = threading.Lock()


def _get_engine() -> pyttsx3.Engine:
    """
    Returns a singleton pyttsx3 engine instance.
    Creates it on first call, reuses on subsequent calls.
    Thread-safe via lock.
    """
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            _engine.setProperty("rate", VOICE_SPEED_RATE)
            _engine.setProperty("volume", 1.0)  # 0.0 to 1.0

            # Pick the best available voice (prefer female for AutoNexus)
            voices = _engine.getProperty("voices")
            if voices:
                # Try to find English female voice first
                female = next(
                    (v for v in voices if "female" in v.name.lower() or "zira" in v.name.lower()),
                    None
                )
                if female:
                    _engine.setProperty("voice", female.id)
                    logger.info(f"TTS voice set to: {female.name}")
                else:
                    _engine.setProperty("voice", voices[0].id)
                    logger.info(f"TTS voice set to: {voices[0].name}")

            logger.info(f"pyttsx3 engine initialized | speed={VOICE_SPEED_RATE} wpm")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    return _engine


# ==============================================================================
# SECTION 2: Core speak() function
# This is the main function all other modules call.
# ==============================================================================

def speak(text: str, save_audio: bool = False, filename: str = None) -> bool:
    """
    Convert text to speech and play it out loud.

    Args:
        text        : The text to speak aloud
        save_audio  : If True, also save as .wav file in recordings/
        filename    : Custom filename (auto-generated if None)

    Returns:
        True if successful, False if failed

    Usage:
        speak("Hello, your vehicle needs a brake inspection.")
        speak("Appointment confirmed!", save_audio=True)
    """
    if not text or not text.strip():
        logger.warning("speak() called with empty text — skipping")
        return False

    # Clean text — remove special chars that break TTS
    clean_text = _clean_text_for_tts(text)
    logger.info(f"TTS speaking: '{clean_text[:60]}{'...' if len(clean_text)>60 else ''}'")

    with _engine_lock:
        try:
            engine = _get_engine()

            if save_audio:
                # Save to file AND speak
                audio_path = _get_audio_path(filename)
                engine.save_to_file(clean_text, str(audio_path))
                engine.runAndWait()
                logger.info(f"Audio saved to: {audio_path}")
            else:
                # Just speak (no file saved)
                engine.say(clean_text)
                engine.runAndWait()

            return True

        except RuntimeError as e:
            # pyttsx3 sometimes crashes on rapid repeated calls — reinit
            logger.warning(f"TTS runtime error — reinitializing engine: {e}")
            global _engine
            _engine = None
            try:
                engine = _get_engine()
                engine.say(clean_text)
                engine.runAndWait()
                return True
            except Exception as e2:
                logger.error(f"TTS failed after reinit: {e2}")
                return False

        except Exception as e:
            logger.error(f"TTS speak() failed: {e}")
            return False


# ==============================================================================
# SECTION 3: Specialized speak functions for each agent
# These wrap speak() with pre-built message templates.
# ==============================================================================

def speak_service_alert(vehicle_id: str, component: str, days: int) -> bool:
    """
    Speak a vehicle service alert to the customer.
    Called by: engagement_agent.py

    Example output:
      "Hello! This is AutoNexus calling about your vehicle VEH001.
       Our system has detected that your brakes require attention
       within the next 7 days. Please call us to schedule a service."
    """
    message = (
        f"Hello! This is AutoNexus calling about your vehicle {vehicle_id}. "
        f"Our predictive maintenance system has detected that your {component} "
        f"requires attention within the next {days} days. "
        f"Please press 1 to schedule a service appointment, "
        f"or press 2 to speak with our service team."
    )
    logger.info(f"Speaking service alert | vehicle={vehicle_id} | component={component}")
    return speak(message, save_audio=True, filename=f"alert_{vehicle_id}_{component}")


def speak_appointment_confirmation(
    customer_name: str,
    date: str,
    time_slot: str,
    service_center: str
) -> bool:
    """
    Speak appointment booking confirmation.
    Called by: scheduling_agent.py
    """
    message = (
        f"Hello {customer_name}! Your service appointment has been confirmed. "
        f"You are scheduled for {date} at {time_slot} "
        f"at our {service_center} service center. "
        f"You will receive an SMS confirmation shortly. "
        f"Thank you for choosing AutoNexus!"
    )
    logger.info(f"Speaking appointment confirmation | customer={customer_name}")
    return speak(message, save_audio=True, filename=f"confirm_{customer_name}_{date}")


def speak_feedback_request(customer_name: str, service_type: str) -> bool:
    """
    Speak a feedback collection prompt after service.
    Called by: feedback_agent.py
    """
    message = (
        f"Hello {customer_name}! This is AutoNexus following up on your recent "
        f"{service_type} service. "
        f"We hope everything went smoothly. "
        f"On a scale of 1 to 5, how satisfied were you with our service today? "
        f"Please say your rating or press the corresponding number."
    )
    logger.info(f"Speaking feedback request | customer={customer_name}")
    return speak(message)


def speak_ueba_alert(agent_name: str, anomaly_score: int) -> bool:
    """
    Speak internal UEBA security alert (for demo/monitoring purposes).
    Called by: security/ueba/alert_manager.py
    """
    message = (
        f"Security alert! Agent {agent_name} has triggered an anomaly "
        f"with a risk score of {anomaly_score} out of 100. "
        f"Initiating containment protocol."
    )
    logger.warning(f"Speaking UEBA alert | agent={agent_name} | score={anomaly_score}")
    return speak(message, save_audio=True, filename=f"ueba_alert_{agent_name}")


def speak_welcome() -> bool:
    """Speak AutoNexus welcome message. Used in demo."""
    message = (
        "Welcome to AutoNexus! Your intelligent automotive predictive "
        "maintenance system is now active. All agents are online and monitoring "
        "your vehicle fleet."
    )
    return speak(message)


# ==============================================================================
# SECTION 4: Utility Functions
# ==============================================================================

def list_available_voices() -> list:
    """
    Returns all TTS voices available on this machine.
    Useful for debugging voice selection.

    Usage:
        voices = list_available_voices()
        for v in voices: print(v)
    """
    try:
        engine = _get_engine()
        voices = engine.getProperty("voices")
        voice_list = [
            {"id": v.id, "name": v.name, "languages": v.languages}
            for v in voices
        ]
        logger.info(f"Found {len(voice_list)} voices on this system")
        return voice_list
    except Exception as e:
        logger.error(f"Could not list voices: {e}")
        return []


def set_voice_speed(wpm: int) -> bool:
    """
    Dynamically change speaking speed.
    Args:
        wpm: words per minute (100=slow, 150=normal, 200=fast)
    """
    try:
        engine = _get_engine()
        engine.setProperty("rate", wpm)
        logger.info(f"Voice speed changed to {wpm} wpm")
        return True
    except Exception as e:
        logger.error(f"Could not set voice speed: {e}")
        return False


def _clean_text_for_tts(text: str) -> str:
    """
    Remove characters that cause TTS to misbehave.
    Replaces common symbols with spoken equivalents.
    """
    replacements = {
        "&":  "and",
        "%":  "percent",
        "#":  "number",
        "@":  "at",
        "°":  "degrees",
        "→":  "to",
        "←":  "from",
        "\n": " ",
        "\t": " ",
    }
    clean = text
    for char, replacement in replacements.items():
        clean = clean.replace(char, replacement)
    # Collapse multiple spaces
    clean = " ".join(clean.split())
    return clean.strip()


def _get_audio_path(filename: str = None) -> Path:
    """
    Build the full path for saving an audio recording.
    Auto-generates timestamp-based filename if none given.
    """
    if filename:
        # Sanitize filename
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
        return AUDIO_RECORDINGS_DIR / f"{safe_name}.wav"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return AUDIO_RECORDINGS_DIR / f"tts_{timestamp}.wav"


# ==============================================================================
# SELF-TEST
# Run: python services/voice/text_to_speech.py
# You should HEAR the AutoNexus welcome message spoken aloud.
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 2: Text-to-Speech — Self Test")
    print("="*55)

    # Test 1: List available voices
    print("\n[1] Available voices on this system:")
    voices = list_available_voices()
    for i, v in enumerate(voices):
        print(f"    {i+1}. {v['name']}")

    # Test 2: Basic speak
    print("\n[2] Testing basic speak — you should hear audio now...")
    result = speak("Testing AutoNexus text to speech system. If you can hear this, File 2 is working correctly.")
    print(f"    Result: {'✅ SUCCESS' if result else '❌ FAILED'}")

    # Test 3: Service alert
    print("\n[3] Testing service alert message...")
    time.sleep(1)
    result2 = speak_service_alert("VEH001", "brakes", 7)
    print(f"    Result: {'✅ SUCCESS' if result2 else '❌ FAILED'}")

    # Test 4: Appointment confirmation
    print("\n[4] Testing appointment confirmation...")
    time.sleep(1)
    result3 = speak_appointment_confirmation(
        customer_name="Ruchika",
        date="Monday March 10th",
        time_slot="10 AM",
        service_center="AutoNexus Central"
    )
    print(f"    Result: {'✅ SUCCESS' if result3 else '❌ FAILED'}")

    # Test 5: Speed change
    print("\n[5] Testing speed change to 180 wpm...")
    set_voice_speed(180)
    time.sleep(0.5)
    speak("This is faster speaking speed.")

    # Reset speed
    set_voice_speed(VOICE_SPEED_RATE)

    print("\n" + "="*55)
    print("  FILE 2 self-test complete!")
    print("  If you heard all 4 messages — commit this file ✅")
    print("="*55 + "\n")