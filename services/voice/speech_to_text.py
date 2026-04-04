"""
FILE 3: services/voice/speech_to_text.py
PURPOSE: Converts customer voice/audio into text using OpenAI Whisper (local, free).
         Whisper runs 100% on your machine — no API key, no internet needed.
CONNECTS TO:
  - services/voice/call_manager.py              (FILE 4 — calls listen())
  - services/agents/workers/engagement_agent.py (FILE 8 — calls listen())
  - services/agents/workers/feedback_agent.py   (FILE 10 — calls listen())
  - services/agents/config/hf_model_config.py   (FILE 1 — reads WHISPER_SIZE)
AUTHOR: Person 4
"""

import io
import time
import wave
import logging
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional

import whisper
import numpy as np

from services.agents.config.hf_model_config import (
    WHISPER_SIZE,
    AUDIO_RECORDINGS_DIR,
    VOICE_LANGUAGE,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# SECTION 1: Whisper Model Loader
# Model is downloaded once (~140MB for "base"), then cached locally.
# Subsequent loads are instant from cache.
# ==============================================================================

_whisper_model = None
_model_lock = threading.Lock()


def _get_whisper_model():
    """
    Singleton loader for Whisper model.
    Downloads on first call, reuses from cache after.
    """
    global _whisper_model
    if _whisper_model is None:
        with _model_lock:
            if _whisper_model is None:
                logger.info(
                    f"Loading Whisper '{WHISPER_SIZE}' model... "
                    f"(first run downloads ~140MB, subsequent runs are instant)"
                )
                try:
                    _whisper_model = whisper.load_model(WHISPER_SIZE)
                    logger.info(f"Whisper '{WHISPER_SIZE}' model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load Whisper model: {e}")
                    raise
    return _whisper_model


# ==============================================================================
# SECTION 2: Transcribe from audio FILE
# Used when you have a saved .wav / .mp3 file to transcribe.
# ==============================================================================

def transcribe_file(audio_path: str | Path) -> dict:
    """
    Transcribe speech from an audio file using Whisper.

    Args:
        audio_path: Path to .wav, .mp3, .m4a, or .flac file

    Returns:
        dict with keys:
            'text'       : transcribed text string
            'confidence' : estimated confidence (0.0 - 1.0)
            'language'   : detected language code (e.g. 'en')
            'success'    : True/False
            'duration_s' : how long transcription took

    Usage:
        result = transcribe_file("recordings/customer_call.wav")
        if result['success']:
            print(result['text'])
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        logger.error(f"Audio file not found: {audio_path}")
        return _error_result(f"File not found: {audio_path}")

    logger.info(f"Transcribing file: {audio_path.name}")
    start_time = time.time()

    try:
        model = _get_whisper_model()

        # Whisper transcription with language hint for better accuracy
        result = model.transcribe(
            str(audio_path),
            language=VOICE_LANGUAGE,     # 'en' speeds up detection
            fp16=False,                  # fp16=False required on CPU
            verbose=False,
        )

        duration = round(time.time() - start_time, 2)
        text = result.get("text", "").strip()

        # Estimate confidence from avg log probability
        segments = result.get("segments", [])
        if segments:
            avg_logprob = sum(s.get("avg_logprob", -1) for s in segments) / len(segments)
            confidence = round(min(1.0, max(0.0, 1 + avg_logprob)), 2)
        else:
            confidence = 0.5

        logger.info(
            f"Transcription complete | text='{text[:50]}...' | "
            f"confidence={confidence} | took={duration}s"
        )

        return {
            "text":        text,
            "confidence":  confidence,
            "language":    result.get("language", VOICE_LANGUAGE),
            "success":     True,
            "duration_s":  duration,
            "segments":    segments,
        }

    except Exception as e:
        logger.error(f"Transcription failed for {audio_path}: {e}")
        return _error_result(str(e))


# ==============================================================================
# SECTION 3: Transcribe from microphone (live recording)
# Records from mic for `duration` seconds, then transcribes.
# ==============================================================================

def listen(duration: int = 5, save_recording: bool = True) -> dict:
    """
    Record from microphone and transcribe using Whisper.

    Args:
        duration       : How many seconds to record (default 5)
        save_recording : Save .wav file to recordings/ folder

    Returns:
        Same dict format as transcribe_file()

    Usage:
        result = listen(duration=5)
        customer_said = result['text']
    """
    try:
        import sounddevice as sd
    except ImportError:
        logger.error("sounddevice not installed: pip install sounddevice")
        return _error_result("sounddevice not installed")

    SAMPLE_RATE = 16000   # Whisper expects 16kHz audio
    CHANNELS    = 1       # Mono

    logger.info(f"🎤 Recording for {duration} seconds...")
    print(f"\n  🎤 Listening for {duration} seconds... speak now!")

    try:
        # Record audio from default microphone
        audio_data = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
        )
        sd.wait()  # Wait until recording is done
        logger.info("Recording complete — transcribing...")

        # Flatten to 1D array (Whisper needs this)
        audio_flat = audio_data.flatten()

        # Optionally save recording
        if save_recording:
            recording_path = _save_wav(audio_flat, SAMPLE_RATE)
            logger.info(f"Recording saved: {recording_path}")

        # Transcribe the numpy array directly (no file needed)
        start_time = time.time()
        model = _get_whisper_model()
        result = model.transcribe(
            audio_flat,
            language=VOICE_LANGUAGE,
            fp16=False,
            verbose=False,
        )
        duration_s = round(time.time() - start_time, 2)

        text = result.get("text", "").strip()
        segments = result.get("segments", [])

        if segments:
            avg_logprob = sum(s.get("avg_logprob", -1) for s in segments) / len(segments)
            confidence = round(min(1.0, max(0.0, 1 + avg_logprob)), 2)
        else:
            confidence = 0.5

        logger.info(f"Heard: '{text}' | confidence={confidence}")
        print(f"  📝 Heard: '{text}'")

        return {
            "text":       text,
            "confidence": confidence,
            "language":   result.get("language", VOICE_LANGUAGE),
            "success":    bool(text),
            "duration_s": duration_s,
            "segments":   segments,
        }

    except Exception as e:
        logger.error(f"listen() failed: {e}")
        return _error_result(str(e))


# ==============================================================================
# SECTION 4: Intent Extraction
# After transcribing, extract what the customer actually wants.
# Used by engagement_agent and scheduling_agent.
# ==============================================================================

def extract_intent(text: str) -> dict:
    """
    Extract customer intent from transcribed text.
    Simple keyword-based (no ML needed — fast and reliable for hackathon).

    Args:
        text: transcribed customer speech

    Returns:
        dict with:
            'intent'     : one of ['book_appointment', 'cancel', 'confirm',
                                    'feedback_positive', 'feedback_negative',
                                    'speak_agent', 'unknown']
            'confidence' : 0.0 - 1.0
            'entities'   : extracted details (dates, numbers, etc.)

    Usage:
        result = listen()
        intent = extract_intent(result['text'])
        if intent['intent'] == 'book_appointment':
            scheduling_agent.book(...)
    """
    if not text:
        return {"intent": "unknown", "confidence": 0.0, "entities": {}}

    text_lower = text.lower().strip()
    entities   = {}

    # Intent keyword mapping
    intent_keywords = {
        "book_appointment": [
            "book", "schedule", "appointment", "service", "fix",
            "repair", "bring in", "come in", "reserve", "yes", "1"
        ],
        "cancel": [
            "cancel", "no", "don't", "not now", "later",
            "nevermind", "2", "skip"
        ],
        "confirm": [
            "confirm", "yes", "correct", "right", "sure",
            "okay", "ok", "sounds good", "perfect"
        ],
        "feedback_positive": [
            "good", "great", "excellent", "happy", "satisfied",
            "5", "4", "wonderful", "amazing", "love"
        ],
        "feedback_negative": [
            "bad", "poor", "terrible", "unhappy", "dissatisfied",
            "1", "2", "awful", "horrible", "worst"
        ],
        "speak_agent": [
            "agent", "human", "person", "representative", "3",
            "talk to someone", "real person"
        ],
    }

    # Score each intent
    scores = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[intent] = score

    # Extract numeric rating if mentioned (for feedback)
    for word in text_lower.split():
        if word.isdigit():
            entities["rating"] = int(word)
            break

    if not scores:
        return {"intent": "unknown", "confidence": 0.0, "entities": entities}

    # Pick highest scoring intent
    best_intent = max(scores, key=scores.get)
    total       = sum(scores.values())
    confidence  = round(scores[best_intent] / max(total, 1), 2)

    logger.info(f"Intent extracted: '{best_intent}' (confidence={confidence}) from: '{text}'")

    return {
        "intent":     best_intent,
        "confidence": confidence,
        "entities":   entities,
    }


# ==============================================================================
# SECTION 5: Utility Functions
# ==============================================================================

def transcribe_demo_text(text: str) -> dict:
    """
    DEMO MODE: Simulate STT without needing a microphone.
    Returns the given text as if it was transcribed.
    Used during hackathon demo when mic is unavailable.

    Usage:
        result = transcribe_demo_text("Yes, please book an appointment")
    """
    logger.info(f"[DEMO MODE] Simulating STT with text: '{text}'")
    return {
        "text":       text,
        "confidence": 0.95,
        "language":   "en",
        "success":    True,
        "duration_s": 0.1,
        "segments":   [],
    }


def _save_wav(audio_array: np.ndarray, sample_rate: int) -> Path:
    """Save numpy audio array as .wav file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = AUDIO_RECORDINGS_DIR / f"recording_{timestamp}.wav"

    # Convert float32 [-1,1] to int16 for WAV format
    audio_int16 = (audio_array * 32767).astype(np.int16)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # 2 bytes = int16
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    return path


def _error_result(message: str) -> dict:
    """Standard error response dict."""
    return {
        "text":       "",
        "confidence": 0.0,
        "language":   VOICE_LANGUAGE,
        "success":    False,
        "duration_s": 0.0,
        "segments":   [],
        "error":      message,
    }


# ==============================================================================
# SELF-TEST
# Run: python services/voice/speech_to_text.py
# Test 1: Loads Whisper model (downloads ~140MB first time)
# Test 2: Transcribes a demo text (no mic needed)
# Test 3: Tests intent extraction
# Test 4 (optional): Live mic test if sounddevice is available
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 3: Speech-to-Text — Self Test")
    print("="*55)

    # Test 1: Load model
    print("\n[1] Loading Whisper model (downloads if first time)...")
    try:
        model = _get_whisper_model()
        print(f"    ✅ Whisper '{WHISPER_SIZE}' model loaded!")
    except Exception as e:
        print(f"    ❌ Model load failed: {e}")
        exit(1)

    # Test 2: Demo mode transcription (no mic needed)
    print("\n[2] Testing demo transcription (no mic needed)...")
    result = transcribe_demo_text("Yes please book an appointment for Monday")
    print(f"    Text      : '{result['text']}'")
    print(f"    Confidence: {result['confidence']}")
    print(f"    Success   : {'✅' if result['success'] else '❌'}")

    # Test 3: Intent extraction
    print("\n[3] Testing intent extraction...")
    test_phrases = [
        "Yes, please book an appointment",
        "No, I don't need service right now",
        "The service was great, I give it a 5",
        "I want to speak to a real person",
        "Cancel my appointment please",
    ]
    for phrase in test_phrases:
        intent = extract_intent(phrase)
        print(f"    '{phrase[:40]}'")
        print(f"     → intent={intent['intent']} | confidence={intent['confidence']}")

    # Test 4: Live mic (optional — comment out if no mic)
    print("\n[4] Live microphone test (5 seconds)...")
    print("    Speak something after the prompt appears...")
    time.sleep(1)
    try:
        mic_result = listen(duration=5, save_recording=True)
        if mic_result["success"]:
            print(f"    ✅ Transcribed: '{mic_result['text']}'")
            intent = extract_intent(mic_result["text"])
            print(f"    Intent: {intent['intent']}")
        else:
            print(f"    ⚠️  Nothing transcribed (silent or no mic): {mic_result.get('error','')}")
    except Exception as e:
        print(f"    ⚠️  Mic test skipped: {e}")

    print("\n" + "="*55)
    print("  FILE 3 self-test complete!")
    print("  If model loaded + intents extracted — commit ✅")
    print("="*55 + "\n")