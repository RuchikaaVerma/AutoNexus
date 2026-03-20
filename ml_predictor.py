"""
ML Model Predictor
Loads model from Hugging Face and makes predictions
"""

import os
import joblib
from huggingface_hub import hf_hub_download


class MLPredictor:
    def __init__(self, repo_id=None):
        """
        Initialize ML Predictor

        Args:
            repo_id: Hugging Face repository ID (e.g., "username/model-name")
        """
        # Use environment variable if not provided
        if repo_id is None:
            repo_id = os.getenv("HF_REPO_ID", "RashmiVid/vehicle-failure-predictor")

        self.repo_id = repo_id
        self.model = None
        self.load_model()

    def load_model(self):
        """Load model from Hugging Face or local file"""
        try:
            print(f"Loading model from Hugging Face: {self.repo_id}")

            # Download model from Hugging Face
            model_path = hf_hub_download(
                repo_id=self.repo_id,
                filename="vehicle_failure_model.pkl"
            )

            # Load model
            self.model = joblib.load(model_path)
            print("✓ Model loaded successfully!")

        except Exception as e:
            print(f"⚠️  Could not load model from Hugging Face: {e}")
            print("  Will use fallback prediction logic")
            self.model = None

    def predict(self, vehicle_data):
        """
        Predict vehicle failure

        Args:
            vehicle_data: dict with sensor values

        Returns:
            dict: Prediction results (ALL PYTHON TYPES, NO NUMPY!)
        """
        if self.model is None:
            print("⚠️  Model not loaded, using fallback prediction")
            return self._fallback_prediction(vehicle_data)

        try:
            # Prepare features (same order as training)
            features = [
                vehicle_data['brake_temp'],
                vehicle_data['oil_pressure'],
                vehicle_data['engine_temp'],
                vehicle_data['tire_pressure'],
                vehicle_data['brake_fluid_level'],
                vehicle_data['mileage']
            ]

            # Convert to numpy array
            import numpy as np
            features_array = np.array([features])

            # Get prediction
            prediction = self.model.predict(features_array)[0]
            probabilities = self.model.predict_proba(features_array)[0]

            # CRITICAL: Convert numpy types to Python types
            prediction = int(prediction)  # numpy.int64 → int
            failure_probability = float(probabilities[1]) * 100  # numpy.float32 → float
            confidence = float(max(probabilities)) * 100  # numpy.float32 → float

            # Determine risk level based on probability
            if failure_probability > 70:
                risk_level = "HIGH"
                estimated_days = "3-7 days"
            elif failure_probability > 40:
                risk_level = "MEDIUM"
                estimated_days = "1-2 weeks"
            else:
                risk_level = "LOW"
                estimated_days = "3+ weeks"

            # Return prediction (ALL PYTHON TYPES!)
            return {
                "prediction": "FAILURE" if prediction == 1 else "NO FAILURE",
                "failure_probability": round(failure_probability, 2),  # Python float
                "confidence": round(confidence, 2),  # Python float
                "risk_level": risk_level,  # Python str
                "estimated_days": estimated_days  # Python str
            }

        except Exception as e:
            print(f"✗ Prediction error: {e}")
            return self._fallback_prediction(vehicle_data)

    def _fallback_prediction(self, vehicle_data):
        """
        Fallback prediction logic (rule-based)
        Used when ML model is not available
        """
        # Simple rule-based prediction
        risk_score = 0

        # Check brake temperature
        if vehicle_data['brake_temp'] > 100:
            risk_score += 30
        elif vehicle_data['brake_temp'] > 90:
            risk_score += 15

        # Check oil pressure
        if vehicle_data['oil_pressure'] < 25:
            risk_score += 30
        elif vehicle_data['oil_pressure'] < 35:
            risk_score += 15

        # Check engine temperature
        if vehicle_data['engine_temp'] > 105:
            risk_score += 20
        elif vehicle_data['engine_temp'] > 100:
            risk_score += 10

        # Check tire pressure
        if vehicle_data['tire_pressure'] < 25:
            risk_score += 15
        elif vehicle_data['tire_pressure'] < 28:
            risk_score += 8

        # Check brake fluid
        if vehicle_data['brake_fluid_level'] < 65:
            risk_score += 20
        elif vehicle_data['brake_fluid_level'] < 80:
            risk_score += 10

        # Check mileage
        if vehicle_data['mileage'] > 100000:
            risk_score += 10

        # Determine prediction
        if risk_score > 50:
            prediction = "FAILURE"
            risk_level = "HIGH"
            estimated_days = "3-7 days"
        elif risk_score > 25:
            prediction = "WARNING"
            risk_level = "MEDIUM"
            estimated_days = "1-2 weeks"
        else:
            prediction = "NO FAILURE"
            risk_level = "LOW"
            estimated_days = "3+ weeks"

        return {
            "prediction": prediction,
            "failure_probability": float(min(risk_score * 2, 95)),  # Python float
            "confidence": float(max(100 - risk_score, 60)),  # Python float
            "risk_level": risk_level,
            "estimated_days": estimated_days
        }