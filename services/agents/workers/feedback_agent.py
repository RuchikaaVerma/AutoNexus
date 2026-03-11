"""
PURPOSE: Collects customer satisfaction after service. Writes feedback CSV for P2.
CONNECTS TO: FILES 2,3 (voice), FILE 1 (config), ml/data/service_feedback.csv (P2)
"""
import csv, logging
from pathlib import Path
from datetime import datetime
from services.voice.text_to_speech import speak_feedback_request, speak
from services.voice.speech_to_text import transcribe_demo_text, extract_intent

logger = logging.getLogger(__name__)
FEEDBACK_CSV = Path("ml/data/service_feedback.csv")


class FeedbackAgent:
    """Collects and stores customer feedback after service."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.name      = "FeedbackAgent"
        FEEDBACK_CSV.parent.mkdir(parents=True, exist_ok=True)
        logger.info("FeedbackAgent initialized")

    def collect_feedback(
        self,
        vehicle_id:    str,
        customer_name: str,
        service_type:  str,
    ) -> dict:
        """Run full feedback collection flow."""
        logger.info(f"Collecting feedback | vehicle={vehicle_id} | customer={customer_name}")

        # Speak feedback request
        speak_feedback_request(customer_name, service_type)

        # Get rating (demo or real)
        if self.demo_mode:
            import time; time.sleep(0.5)
            response = transcribe_demo_text("I give it a 4 out of 5, great service")
        else:
            from services.voice.speech_to_text import listen
            response = listen(duration=6)

        rating, sentiment = self._parse_rating(response["text"])

        # Thank customer
        if rating >= 4:
            speak(f"Thank you {customer_name}! We're delighted you had a great experience!")
        elif rating >= 3:
            speak(f"Thank you {customer_name}! We'll keep improving our service.")
        else:
            speak(f"We're sorry to hear that {customer_name}. A manager will contact you shortly.")

        feedback = {
            "timestamp":     datetime.now().isoformat(),
            "vehicle_id":    vehicle_id,
            "customer_name": customer_name,
            "service_type":  service_type,
            "rating":        rating,
            "sentiment":     sentiment,
            "raw_response":  response["text"],
        }
        self._save_feedback(feedback)
        logger.info(f"Feedback saved | rating={rating} | sentiment={sentiment}")
        return feedback

    def _parse_rating(self, text: str) -> tuple:
        """Extract numeric rating and sentiment from text."""
        text_lower = text.lower()
        # Look for explicit number
        for word in text_lower.split():
            if word.isdigit():
                r = int(word)
                if 1 <= r <= 5:
                    sentiment = "positive" if r >= 4 else ("neutral" if r == 3 else "negative")
                    return r, sentiment

        # Keyword-based fallback
        intent = extract_intent(text)
        if intent["intent"] == "feedback_positive":
            return 5, "positive"
        elif intent["intent"] == "feedback_negative":
            return 2, "negative"
        return 3, "neutral"

    def _save_feedback(self, feedback: dict):
        """Append feedback row to CSV for P2 ML retraining."""
        write_header = not FEEDBACK_CSV.exists()
        with open(FEEDBACK_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=feedback.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(feedback)
        logger.info(f"Feedback written to {FEEDBACK_CSV}")


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 10: Feedback Agent — Self Test")
    print("="*55)
    agent = FeedbackAgent(demo_mode=True)
    result = agent.collect_feedback("VEH001", "Rahul Sharma", "brake service")
    print(f"\n  Rating   : {result['rating']}/5")
    print(f"  Sentiment: {result['sentiment']}")
    print(f"  CSV saved: {'✅' if FEEDBACK_CSV.exists() else '❌'}")
    print("  FILE 10 complete!\n")
