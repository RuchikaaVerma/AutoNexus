"""
ML Model Predictor for Person 2
Loads 4 models from Hugging Face repo
"""

import os
import joblib
from huggingface_hub import hf_hub_download

# Set token for private repo access

token = os.environ.get("HF_TOKEN")


class MLPredictor:
    def __init__(self, repo_id=None):
        if repo_id is None:
            repo_id = os.getenv("HF_REPO_ID", "divyanshi-02/autonexus-p2-ml-models")

        self.repo_id = repo_id
        self.models = {}          # Will hold all 4 models
        self.load_all_models()

    def load_all_models(self):
        """Load all 4 models from Divyanshi's repo"""
        print(f"Loading Person 2 models from Hugging Face: {self.repo_id}")

        model_files = {
            "anomaly_detector": "anomaly_detector.pkl",
            "brake_failure": "brake_failure_model.pkl",      # or vehicle_failure_model.pkl
            "demand_forecaster": "demand_forecaster.pkl",
            "label_encoder": "label_encoder.pkl"
        }

        for model_name, filename in model_files.items():
            try:
                model_path = hf_hub_download(
                    repo_id=self.repo_id,
                    filename=filename
                )
                self.models[model_name] = joblib.load(model_path)
                print(f"✓ Loaded {model_name} successfully")
            except Exception as e:
                print(f"⚠️ Could not load {filename}: {e}")
                self.models[model_name] = None

        if len(self.models) > 0:
            print(f"✅ Person 2 models loaded: {list(self.models.keys())}")
        else:
            print("⚠️ No models loaded from Person 2 repo. Will use fallback.")

    def predict(self, vehicle_data: dict) -> dict:
        """
        Main prediction using Person 2's models
        """
        if not self.models or all(v is None for v in self.models.values()):
            print("⚠️ No models available, using fallback prediction")
            return self._fallback_prediction(vehicle_data)

        try:
            # Use anomaly detector first (best for health scoring)
            if self.models.get("anomaly_detector"):
                features = [
                    vehicle_data['brake_temp'],
                    vehicle_data['oil_pressure'],
                    vehicle_data['engine_temp'],
                    vehicle_data['tire_pressure'],
                    vehicle_data['brake_fluid_level'],
                    vehicle_data['mileage']
                ]

                anomaly_model = self.models["anomaly_detector"]
                is_anomaly = anomaly_model.predict([features])[0]
                anomaly_score = float(anomaly_model.decision_function([features])[0]) if hasattr(anomaly_model, 'decision_function') else 0.0

                return {
                    "prediction": "FAILURE" if is_anomaly == 1 else "NO FAILURE",
                    "failure_probability": round(float(85 if is_anomaly == 1 else 15), 2),
                    "confidence": round(float(90), 2),
                    "risk_level": "HIGH" if is_anomaly == 1 else "LOW",
                    "estimated_days": "3-7 days" if is_anomaly == 1 else "3+ weeks",
                    "anomaly_score": round(float(anomaly_score), 2),
                    "model_used": "anomaly_detector"
                }

            # Fallback to brake failure model if available
            elif self.models.get("brake_failure"):
                # Simple prediction using brake model
                return self._fallback_prediction(vehicle_data)

            else:
                return self._fallback_prediction(vehicle_data)

        except Exception as e:
            print(f"✗ Prediction error: {e}")
            return self._fallback_prediction(vehicle_data)

    def _fallback_prediction(self, vehicle_data: dict) -> dict:
        """Simple rule-based fallback"""
        risk_score = 0
        if vehicle_data.get('brake_temp', 0) > 100: risk_score += 30
        if vehicle_data.get('oil_pressure', 0) < 25: risk_score += 30
        if vehicle_data.get('brake_fluid_level', 0) < 65: risk_score += 20

        if risk_score > 50:
            return {
                "prediction": "FAILURE",
                "failure_probability": 85.0,
                "confidence": 75.0,
                "risk_level": "HIGH",
                "estimated_days": "3-7 days"
            }
        else:
            return {
                "prediction": "NO FAILURE",
                "failure_probability": 25.0,
                "confidence": 80.0,
                "risk_level": "LOW",
                "estimated_days": "3+ weeks"
            }