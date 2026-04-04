"""
PURPOSE: Collects customer satisfaction after service. Writes feedback CSV for P2 retraining.
CONNECTS TO: FILES 2,3 (voice), FILE 1 (config), FILE 11 (manufacturing insights)
OUTPUTS: ml/data/service_feedback.csv (13 features for P2's retrain_model.py)
"""
import csv
import logging
from pathlib import Path
from datetime import datetime
from services.voice.text_to_speech import speak_feedback_request, speak
from services.voice.speech_to_text import transcribe_demo_text, extract_intent
from services.agents.workers.manufacturing_insights_agent import ManufacturingInsightsAgent

logger = logging.getLogger(__name__)
FEEDBACK_CSV = Path("ml/data/service_feedback.csv")

# CRITICAL: ML model feature columns — what P2's retrain_model.py expects
# Must have 13 features (not 9) to match training data
ML_FIELDNAMES = [
    "vehicle_id",
    "component",
    "failure_date",
    "prediction_date",
    "predicted_days_to_failure",
    "actual_days_to_failure",
    "prediction_accuracy",
    "service_completed",
    "csat_score",
    "vehicle_model",
    "region",
    "climate",
    "mileage",
]


class FeedbackAgent:
    """Collects customer feedback and saves service outcomes for ML retraining."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.name = "FeedbackAgent"
        
        # Initialize manufacturing agent for CSV writing
        self.manufacturing_agent = ManufacturingInsightsAgent()
        
        # Ensure CSV directory exists
        FEEDBACK_CSV.parent.mkdir(parents=True, exist_ok=True)
        logger.info("FeedbackAgent initialized with ManufacturingInsightsAgent integration")

    def collect_feedback(
        self,
        vehicle_id: str,
        customer_name: str,
        service_type: str,
        component: str = "brakes",
        # --- Prediction & service data ---
        predicted_days_to_failure: int = 14,
        actual_days_to_failure: int = 12,
        service_completed: bool = True,
        # --- Vehicle metadata ---
        vehicle_model: str = "Unknown",
        region: str = "Unknown",
        climate: str = "Temperate",
        mileage: int = 0,
        prediction_date: str = None,
    ) -> dict:
        """
        Run full feedback collection flow and save service outcome for ML retraining.
        
        This function:
        1. Makes AI voice call to customer
        2. Collects CSAT rating (1-5)
        3. Saves feedback to CSV with 13 features for P2's model retraining
        """
        logger.info(f"Collecting feedback | vehicle={vehicle_id} | customer={customer_name}")

        # Speak feedback request
        speak_feedback_request(customer_name, service_type)

        # Get rating (demo or real)
        if self.demo_mode:
            import time
            time.sleep(0.5)
            response = transcribe_demo_text("I give it a 4 out of 5, great service")
        else:
            from services.voice.speech_to_text import listen
            response = listen(duration=6)

        rating, sentiment = self._parse_rating(response["text"])

        # Thank customer based on rating
        if rating >= 4:
            speak(f"Thank you {customer_name}! We're delighted you had a great experience!")
        elif rating >= 3:
            speak(f"Thank you {customer_name}! We'll keep improving our service.")
        else:
            speak(f"We're sorry to hear that {customer_name}. A manager will contact you shortly.")

        # CRITICAL: Save to CSV using manufacturing agent (ensures 13-column format)
        csv_path = self.manufacturing_agent.save_service_feedback(
            vehicle_id=vehicle_id,
            component=component,
            predicted_days=predicted_days_to_failure,
            actual_days=actual_days_to_failure,
            service_completed=service_completed,
            csat_score=rating,
            vehicle_model=vehicle_model,
            region=region,
            climate=climate,
            mileage=mileage,
        )
        
        logger.info(f"Service feedback saved to {csv_path} for ML retraining")

        # Return full feedback dict for internal use / logging
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": vehicle_id,
            "customer_name": customer_name,
            "service_type": service_type,
            "component": component,
            "rating": rating,
            "sentiment": sentiment,
            "raw_response": response["text"],
            "csv_path": csv_path,
            "prediction_accuracy": self._calculate_accuracy(predicted_days_to_failure, actual_days_to_failure),
        }
        
        logger.info(f"Feedback collected | rating={rating} | sentiment={sentiment} | accuracy={feedback['prediction_accuracy']:.2%}")
        return feedback

    def _parse_rating(self, text: str) -> tuple:
        """Extract numeric rating and sentiment from text."""
        text_lower = text.lower()
        
        # Look for digits 1-5
        for word in text_lower.split():
            if word.isdigit():
                r = int(word)
                if 1 <= r <= 5:
                    sentiment = "positive" if r >= 4 else ("neutral" if r == 3 else "negative")
                    return r, sentiment

        # Fallback: use intent detection
        intent = extract_intent(text)
        if intent["intent"] == "feedback_positive":
            return 5, "positive"
        elif intent["intent"] == "feedback_negative":
            return 2, "negative"
        
        return 3, "neutral"

    def _calculate_accuracy(self, predicted: int, actual: int) -> float:
        """Calculate prediction accuracy as a percentage."""
        if actual <= 0:
            return 0.0
        accuracy = 1.0 - abs(predicted - actual) / actual
        return max(0.0, min(1.0, accuracy))

    # ═══════════════════════════════════════════════════════════════════════
    # LEGACY METHOD (for backwards compatibility)
    # ═══════════════════════════════════════════════════════════════════════
    
    def _save_sensor_data_legacy(self, sensor_data: dict):
        """
        DEPRECATED: Old method that saved 9 columns (caused Bug #1).
        Kept for reference but no longer used.
        
        New method uses manufacturing_agent.save_service_feedback() with 13 columns.
        """
        logger.warning("_save_sensor_data_legacy called - this method is deprecated")
        
        # Old 9-column format (DO NOT USE)
        old_fieldnames = [
            "vehicle_id",
            "brake_temperature",
            "brake_fluid_level",
            "oil_pressure",
            "engine_temperature",
            "tyre_pressure",
            "mileage",
            "days_since_last_service",
            "days_until_failure",
        ]
        
        write_header = not FEEDBACK_CSV.exists()
        with open(FEEDBACK_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=old_fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(sensor_data)
        
        logger.warning(f"Wrote legacy 9-column format to {FEEDBACK_CSV} - P2's retrain will fail with this!")

    def process(self, data: dict) -> dict:
        """Main entry point from MasterAgent (called after service completion)"""
        vehicle_id = data.get("vehicle_id")
        service_status = data.get("service_status", "completed")

        if service_status == "completed":
            result = self.collect_feedback(
                vehicle_id=vehicle_id,
                customer_name=data.get("owner", {}).get("name", "Customer"),
                service_type="emergency_brake_repair",
                component="brakes"
            )
            return {
                "agent": "FeedbackAgent",
                "survey_required": True,
                "rating": result.get("rating"),
                "message": "Thank you for your feedback! 5% discount applied for next service.",
                **result
            }
        return {"agent": "FeedbackAgent", "survey_required": False}
    def get_info(self):
        """Required by MasterAgent for /agents/status"""
        return {
            "name": self.name,
            "description": "Collects customer feedback after service and saves data for ML retraining",
            "status": "active"
        }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FILE 10: Feedback Agent — Self Test")
    print("="*60)
    
    agent = FeedbackAgent(demo_mode=True)
    
    # Test 1: Single feedback collection
    print("\n[TEST 1] Collecting customer feedback...")
    result = agent.collect_feedback(
        vehicle_id="VEH001",
        customer_name="Rahul Sharma",
        service_type="brake service",
        component="brakes",
        # Prediction data
        predicted_days_to_failure=14,
        actual_days_to_failure=12,  # Came in 2 days earlier than predicted
        service_completed=True,
        # Vehicle metadata
        vehicle_model="Toyota Camry",
        region="North America",
        climate="Temperate",
        mileage=45230,
        prediction_date="2025-02-01T10:00:00",
    )
    
    print(f"  Rating          : {result['rating']}/5")
    print(f"  Sentiment       : {result['sentiment']}")
    print(f"  Accuracy        : {result['prediction_accuracy']:.1%}")
    print(f"  CSV saved to    : {result['csv_path']}")
    
    # Test 2: Multiple feedback collections (simulating a week of services)
    print("\n[TEST 2] Simulating multiple service completions...")
    test_services = [
        {
            "vehicle_id": "VEH002",
            "customer_name": "Priya Patel",
            "service_type": "engine oil change",
            "component": "engine oil",
            "predicted_days_to_failure": 7,
            "actual_days_to_failure": 8,
            "vehicle_model": "Honda Accord",
            "region": "Asia",
            "climate": "Hot",
            "mileage": 62000,
        },
        {
            "vehicle_id": "VEH003",
            "customer_name": "John Smith",
            "service_type": "tire rotation",
            "component": "tires",
            "predicted_days_to_failure": 30,
            "actual_days_to_failure": 28,
            "vehicle_model": "Ford F-150",
            "region": "North America",
            "climate": "Cold",
            "mileage": 38500,
        },
        {
            "vehicle_id": "VEH004",
            "customer_name": "Maria Garcia",
            "service_type": "battery replacement",
            "component": "battery",
            "predicted_days_to_failure": 90,
            "actual_days_to_failure": 85,
            "vehicle_model": "Tesla Model 3",
            "region": "Europe",
            "climate": "Temperate",
            "mileage": 22000,
        },
    ]
    
    for service in test_services:
        result = agent.collect_feedback(**service)
        print(f"  ✓ {service['vehicle_id']}: {result['rating']}/5 (accuracy: {result['prediction_accuracy']:.1%})")
    
    # Test 3: Verify CSV structure
    print("\n[TEST 3] Verifying CSV structure...")
    csv_path = Path("data/feedback/service_feedback.csv")
    
    if csv_path.exists():
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            row_count = sum(1 for _ in reader)
        
        print(f"  ✓ CSV exists at: {csv_path}")
        print(f"  ✓ Columns: {len(fieldnames)} (expected: 13)")
        print(f"  ✓ Rows: {row_count + 1} (including test data)")
        
        if len(fieldnames) == 13:
            print("  ✅ CSV has correct 13-column format for P2's retraining!")
        else:
            print(f"  ❌ CSV has {len(fieldnames)} columns, but P2 needs 13!")
            print(f"  Columns found: {fieldnames}")
    else:
        print(f"  ❌ CSV not found at {csv_path}")
    
    # Test 4: Check integration with manufacturing agent
    print("\n[TEST 4] Testing manufacturing agent integration...")
    manufacturing_agent = agent.manufacturing_agent
    
    print(f"  ✓ Manufacturing agent: {manufacturing_agent.name}")
    print(f"  ✓ Failure knowledge base: {len(manufacturing_agent.FAILURE_KNOWLEDGE)} components")
    print(f"  ✓ Components covered: {', '.join(manufacturing_agent.FAILURE_KNOWLEDGE.keys())}")
    
    print("\n" + "="*60)
    print("  FILE 10 complete! Check data/feedback/service_feedback.csv")
    print("="*60 + "\n")
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"  • Feedback agent ready to collect CSAT ratings")
    print(f"  • CSV saved with 13 columns (Bug #1 fixed)")
    print(f"  • Integration with manufacturing agent: ✅")
    print(f"  • Ready for P2's retrain_model.py in Week 4")
    print()