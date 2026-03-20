"""
Diagnosis Agent
Uses ML model to predict failures
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from ml_predictor import MLPredictor


class DiagnosisAgent(BaseAgent):
    """
    Predicts vehicle failures using ML model

    Uses the XGBoost model trained on OBD-II data
    """

    def __init__(self, ml_predictor: MLPredictor):
        """
        Initialize Diagnosis Agent

        Args:
            ml_predictor: MLPredictor instance with loaded model
        """
        super().__init__(
            name="DiagnosisAgent",
            description="Predicts vehicle failures using ML model"
        )
        self.ml_predictor = ml_predictor

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose vehicle using ML model

        Args:
            data: Dictionary containing:
                - vehicle_id: str
                - sensors: dict with 6 sensor values

        Returns:
            dict: ML prediction results
        """
        self._log_call()

        vehicle_id = data.get("vehicle_id", "Unknown")
        sensors = data.get("sensors", {})

        # Prepare data for ML model
        vehicle_data = {
            'brake_temp': sensors.get('brake_temp', 0),
            'oil_pressure': sensors.get('oil_pressure', 0),
            'engine_temp': sensors.get('engine_temp', 0),
            'tire_pressure': sensors.get('tire_pressure', 0),
            'brake_fluid_level': sensors.get('brake_fluid_level', 0),
            'mileage': sensors.get('mileage', 0)
        }

        # Get ML prediction
        prediction = self.ml_predictor.predict(vehicle_data)

        # Interpret prediction
        diagnosis = self._interpret_prediction(prediction, sensors)

        return {
            "agent": self.name,
            "vehicle_id": vehicle_id,
            "ml_prediction": prediction,
            "diagnosis": diagnosis,
            "confidence": prediction.get("confidence", 0),
            "recommended_actions": self._generate_actions(prediction)
        }

    def _interpret_prediction(self, prediction: Dict, sensors: Dict) -> str:
        """
        Convert ML prediction to human-readable diagnosis

        Args:
            prediction: ML model output
            sensors: Sensor values

        Returns:
            str: Human-readable diagnosis
        """
        failure_prob = prediction.get("failure_probability", 0)
        risk_level = prediction.get("risk_level", "UNKNOWN")

        if failure_prob > 70:
            # Identify likely failure component
            if sensors.get('brake_temp', 0) > 100:
                component = "brake system"
            elif sensors.get('oil_pressure', 0) < 25:
                component = "engine lubrication"
            elif sensors.get('brake_fluid_level', 0) < 65:
                component = "brake hydraulics"
            else:
                component = "multiple systems"

            return f"HIGH RISK: {failure_prob:.1f}% probability of {component} failure within {prediction.get('estimated_days', 'unknown')}"

        elif failure_prob > 40:
            return f"MODERATE RISK: {failure_prob:.1f}% failure probability. Preventive maintenance recommended within {prediction.get('estimated_days', 'unknown')}"

        else:
            return f"LOW RISK: {failure_prob:.1f}% failure probability. Vehicle systems functioning normally. Continue regular maintenance schedule."

    def _generate_actions(self, prediction: Dict) -> list:
        """
        Generate actionable recommendations based on prediction

        Args:
            prediction: ML model output

        Returns:
            list: Recommended actions
        """
        actions = []
        risk_level = prediction.get("risk_level", "LOW")

        if risk_level == "HIGH":
            actions.append("Schedule emergency inspection within 24 hours")
            actions.append("Avoid long trips until serviced")
            actions.append("Monitor all sensors closely")
        elif risk_level == "MEDIUM":
            actions.append("Schedule service within 1 week")
            actions.append("Check fluid levels daily")
            actions.append("Avoid aggressive driving")
        else:
            actions.append("Continue regular maintenance schedule")
            actions.append("Next service in 3-6 months or per manual")

        return actions
