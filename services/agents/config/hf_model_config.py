"""
FILE 1: services/agents/config/hf_model_config.py
PURPOSE: Central configuration for all HuggingFace models used by Person 4.
         Every agent, voice module, and security component imports from here.
CONNECTS TO:
  - services/agents/workers/*.py        (all agents read model names here)
  - services/voice/text_to_speech.py    (reads TTS_ENGINE)
  - services/voice/speech_to_text.py    (reads WHISPER_SIZE)
  - services/security/ueba/*.py         (reads UEBA thresholds)
AUTHOR: Person 4
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env file from project root ──────────────────────────────────────────
# Goes up 3 levels: config/ → agents/ → services/ → project root
ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ==============================================================================
# SECTION 1: HuggingFace Authentication
# ==============================================================================
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
# Run mode: "api" = call HuggingFace API (needs token + internet)
#           "local" = download model and run on your machine (slow first time)
HF_RUN_MODE = os.getenv("HF_RUN_MODE", "api")

if not HF_TOKEN:
    logger.warning(
        "HUGGINGFACE_API_TOKEN not found in .env — "
        "API calls will fail. Get free token at huggingface.co/settings/tokens"
    )


# ==============================================================================
# SECTION 2: Model Names Per Agent
# Each agent uses a different model suited to its task.
# All are FREE on HuggingFace — no billing required.
# ==============================================================================

# Engagement Agent — conversational, talks to customers
ENGAGEMENT_MODEL = os.getenv(
    "ENGAGEMENT_MODEL",
    "microsoft/DialoGPT-medium"          # Good conversational model, fast
)

# Scheduling Agent — understands intent and books slots
SCHEDULING_MODEL = os.getenv(
    "SCHEDULING_MODEL",
    "microsoft/phi-2"                    # Small but smart, good for logic
)

# Feedback Agent — sentiment analysis on customer responses
FEEDBACK_MODEL = os.getenv(
    "FEEDBACK_MODEL",
    "distilbert-base-uncased-finetuned-sst-2-english"  # Fast sentiment model
)

# Manufacturing Insights Agent — RCA, CAPA, technical reasoning
MANUFACTURING_MODEL = os.getenv(
    "MANUFACTURING_MODEL",
    "mistralai/Mistral-7B-Instruct-v0.2" # Best free instruction model
)

# UEBA Anomaly Explanation — explains why behaviour is suspicious
UEBA_EXPLAIN_MODEL = os.getenv(
    "UEBA_EXPLAIN_MODEL",
    "distilbert-base-uncased"            # Lightweight for fast scoring
)


# ==============================================================================
# SECTION 3: Voice AI Configuration
# ==============================================================================

# Speech-to-Text (Whisper) — transcribes customer voice
WHISPER_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
# Options: "tiny" (fastest), "base" (good balance), "small", "medium", "large"
# For hackathon: "base" is best — fast enough, accurate enough

# Text-to-Speech engine
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")
# Options: "pyttsx3" (offline, no install issues — USE THIS)
#          "coqui"   (better voice, needs TTS package installed)

# Voice call settings
VOICE_LANGUAGE = os.getenv("VOICE_LANGUAGE", "en")
VOICE_SPEED_RATE = int(os.getenv("VOICE_SPEED_RATE", "150"))  # words per min
AUDIO_RECORDINGS_DIR = ROOT_DIR / "services" / "voice" / "audio" / "recordings"
AUDIO_SAMPLES_DIR    = ROOT_DIR / "services" / "voice" / "audio" / "samples"


# ==============================================================================
# SECTION 4: Notification Service Keys
# ==============================================================================

# Twilio (SMS) — free trial at twilio.com
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# SendGrid (Email) — free plan at sendgrid.com
SENDGRID_API_KEY    = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@autonexus.com")
# ============================================================
# ADD THESE 2 LINES to hf_model_config.py
# Place them in SECTION 4, after the SendGrid lines
# (around line 95, after SENDGRID_FROM_EMAIL)
# ============================================================

GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# Firebase (Push notifications) — free at console.firebase.google.com
FIREBASE_SERVER_KEY = os.getenv("FIREBASE_SERVER_KEY", "")


# ==============================================================================
# SECTION 5: UEBA Security Thresholds
# ==============================================================================

# Anomaly score 0-100. Above threshold = suspicious behaviour flagged
UEBA_ANOMALY_THRESHOLD  = int(os.getenv("UEBA_ANOMALY_THRESHOLD", "70"))
# Score above this = immediately block the agent
UEBA_CRITICAL_THRESHOLD = int(os.getenv("UEBA_CRITICAL_THRESHOLD", "90"))
# How many seconds of behaviour history to keep per agent
UEBA_BASELINE_WINDOW_SEC = int(os.getenv("UEBA_BASELINE_WINDOW_SEC", "3600"))


# ==============================================================================
# SECTION 6: Backend API Connection (Person 1)
# ==============================================================================

# Person 1's FastAPI server — P4 agents call these endpoints
BACKEND_BASE_URL    = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
BACKEND_WS_URL      = os.getenv("BACKEND_WS_URL",   "ws://localhost:8000/ws")
AGENT_REGISTER_URL  = f"{BACKEND_BASE_URL}/agents/register"
PREDICT_URL         = f"{BACKEND_BASE_URL}/predict"
ALERTS_URL          = f"{BACKEND_BASE_URL}/alerts"


# ==============================================================================
# SECTION 7: Database & Cache
# ==============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/automotive.db")
REDIS_URL    = os.getenv("REDIS_URL", "redis://localhost:6379")


# ==============================================================================
# SECTION 8: Paths used across all Person 4 modules
# ==============================================================================

SERVICES_DIR      = ROOT_DIR / "services"
TEMPLATES_DIR     = SERVICES_DIR / "notifications" / "templates"
REPORTS_OUTPUT    = SERVICES_DIR / "manufacturing" / "reports"
DEMO_SAMPLE_DATA  = SERVICES_DIR / "demo" / "sample_data"
ML_MODELS_DIR     = ROOT_DIR / "ml" / "models"
ML_EVAL_DIR       = ROOT_DIR / "ml" / "evaluation"

# Auto-create directories that must exist at runtime
for _dir in [AUDIO_RECORDINGS_DIR, AUDIO_SAMPLES_DIR, REPORTS_OUTPUT]:
    _dir.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# SECTION 9: Prometheus Monitoring
# ==============================================================================

PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))
ENABLE_METRICS  = os.getenv("ENABLE_METRICS", "true").lower() == "true"


# ==============================================================================
# SELF-TEST — run this file directly to verify everything loads correctly
# python services/agents/config/hf_model_config.py
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  AutoNexus — Person 4 Configuration Check")
    print("="*60)

    checks = {
        "HuggingFace Token":    bool(HF_TOKEN),
        "Twilio SID":           bool(TWILIO_ACCOUNT_SID),
        "SendGrid Key":         bool(SENDGRID_API_KEY),
        "Backend URL":          bool(BACKEND_BASE_URL),
        "Database URL":         bool(DATABASE_URL),
        "Redis URL":            bool(REDIS_URL),
    }

    all_ok = True
    for name, status in checks.items():
        icon = "✅" if status else "⚠️ "
        if not status:
            all_ok = False
        print(f"  {icon}  {name:<25} {'LOADED' if status else 'MISSING — fill in .env'}")

    print("\n  Models configured:")
    print(f"    Engagement   → {ENGAGEMENT_MODEL}")
    print(f"    Scheduling   → {SCHEDULING_MODEL}")
    print(f"    Feedback     → {FEEDBACK_MODEL}")
    print(f"    Manufacturing→ {MANUFACTURING_MODEL}")
    print(f"    UEBA         → {UEBA_EXPLAIN_MODEL}")

    print("\n  Voice settings:")
    print(f"    TTS Engine   → {TTS_ENGINE}")
    print(f"    Whisper size → {WHISPER_SIZE}")
    print(f"    Speed (wpm)  → {VOICE_SPEED_RATE}")

    print("\n  UEBA thresholds:")
    print(f"    Flag at      → {UEBA_ANOMALY_THRESHOLD}/100")
    print(f"    Block at     → {UEBA_CRITICAL_THRESHOLD}/100")

    print("\n  Project root:", ROOT_DIR)
    print("="*60)

    if all_ok:
        print("  ✅  ALL CHECKS PASSED — Config is ready!\n")
    else:
        print("  ⚠️   Some keys missing — open .env and fill them in\n")
        print("  Get HuggingFace token free: huggingface.co/settings/tokens")
        print("  Get Twilio free trial:      twilio.com/try-twilio")
        print("  Get SendGrid free:          sendgrid.com\n")