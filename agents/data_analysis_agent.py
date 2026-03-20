"""
Data Analysis Agent
Analyzes vehicle sensor data and detects anomalies
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class DataAnalysisAgent(BaseAgent):
    """
    Analyzes sensor data and identifies anomalies

    Checks all 6 sensors against thresholds and reports issues
    """

    # Sensor thresholds (automotive engineering standards)
    THRESHOLDS = {
        "brake_temp": {
            "critical_high": 100,
            "warning_high": 90,
            "normal_range": (65, 85)
        },
        "oil_pressure": {
            "critical_low": 25,
            "warning_low": 35,
            "normal_range": (38, 55)
        },
        "engine_temp": {
            "critical_high": 105,
            "warning_high": 100,
            "normal_range": (85, 95)
        },
        "tire_pressure": {
            "critical_low": 25,
            "warning_low": 28,
            "normal_range": (30, 35)
        },
        "brake_fluid_level": {
            "critical_low": 65,
            "warning_low": 80,
            "normal_range": (85, 100)
        },
        "mileage": {
            "high": 80000,
            "medium": 50000
        }
    }

    def __init__(self):
        """Initialize Data Analysis Agent"""
        super().__init__(
            name="DataAnalysisAgent",
            description="Analyzes vehicle sensor data and detects anomalies"
        )

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze vehicle sensor data

        Args:
            data: Dictionary containing:
                - vehicle_id: str
                - sensors: dict with 6 sensor values

        Returns:
            dict: Analysis results with anomalies
        """
        self._log_call()  # Track usage

        vehicle_id = data.get("vehicle_id", "Unknown")
        sensors = data.get("sensors", {})

        # Analyze each sensor
        anomalies = {
            "critical": [],
            "warning": [],
            "normal": []
        }

        overall_status = "healthy"

        # Check brake temperature
        brake_result = self._check_brake_temp(sensors.get("brake_temp", 0))
        self._categorize_finding(brake_result, anomalies)

        # Check oil pressure
        oil_result = self._check_oil_pressure(sensors.get("oil_pressure", 0))
        self._categorize_finding(oil_result, anomalies)

        # Check engine temperature
        engine_result = self._check_engine_temp(sensors.get("engine_temp", 0))
        self._categorize_finding(engine_result, anomalies)

        # Check tire pressure
        tire_result = self._check_tire_pressure(sensors.get("tire_pressure", 0))
        self._categorize_finding(tire_result, anomalies)

        # Check brake fluid
        fluid_result = self._check_brake_fluid(sensors.get("brake_fluid_level", 0))
        self._categorize_finding(fluid_result, anomalies)

        # Check mileage
        mileage_result = self._check_mileage(sensors.get("mileage", 0))
        self._categorize_finding(mileage_result, anomalies)

        # Determine overall status
        if len(anomalies["critical"]) > 0:
            overall_status = "critical"
        elif len(anomalies["warning"]) > 0:
            overall_status = "warning"

        return {
            "agent": self.name,
            "vehicle_id": vehicle_id,
            "overall_status": overall_status,
            "anomalies_detected": {
                "critical_count": len(anomalies["critical"]),
                "warning_count": len(anomalies["warning"]),
                "normal_count": len(anomalies["normal"])
            },
            "findings": anomalies,
            "summary": self._generate_summary(anomalies)
        }

    def _check_brake_temp(self, value: float) -> Dict[str, Any]:
        """Check brake temperature against thresholds"""
        thresholds = self.THRESHOLDS["brake_temp"]

        if value > thresholds["critical_high"]:
            return {
                "sensor": "brake_temp",
                "value": value,
                "severity": "critical",
                "message": f"Brake temperature critically high: {value}°C (>{thresholds['critical_high']}°C)",
                "recommendation": "Stop vehicle immediately and inspect brakes"
            }
        elif value > thresholds["warning_high"]:
            return {
                "sensor": "brake_temp",
                "value": value,
                "severity": "warning",
                "message": f"Brake temperature elevated: {value}°C (>{thresholds['warning_high']}°C)",
                "recommendation": "Schedule brake inspection within 7 days"
            }
        else:
            return {
                "sensor": "brake_temp",
                "value": value,
                "severity": "normal",
                "message": f"Brake temperature normal: {value}°C"
            }

    def _check_oil_pressure(self, value: float) -> Dict[str, Any]:
        """Check oil pressure against thresholds"""
        thresholds = self.THRESHOLDS["oil_pressure"]

        if value < thresholds["critical_low"]:
            return {
                "sensor": "oil_pressure",
                "value": value,
                "severity": "critical",
                "message": f"Oil pressure dangerously low: {value} psi (<{thresholds['critical_low']} psi)",
                "recommendation": "Stop engine immediately - risk of seizure"
            }
        elif value < thresholds["warning_low"]:
            return {
                "sensor": "oil_pressure",
                "value": value,
                "severity": "warning",
                "message": f"Oil pressure below normal: {value} psi (<{thresholds['warning_low']} psi)",
                "recommendation": "Check oil level and inspect for leaks"
            }
        else:
            return {
                "sensor": "oil_pressure",
                "value": value,
                "severity": "normal",
                "message": f"Oil pressure normal: {value} psi"
            }

    def _check_engine_temp(self, value: float) -> Dict[str, Any]:
        """Check engine temperature against thresholds"""
        thresholds = self.THRESHOLDS["engine_temp"]

        if value > thresholds["critical_high"]:
            return {
                "sensor": "engine_temp",
                "value": value,
                "severity": "critical",
                "message": f"Engine overheating: {value}°C (>{thresholds['critical_high']}°C)",
                "recommendation": "Stop vehicle and check coolant system"
            }
        elif value > thresholds["warning_high"]:
            return {
                "sensor": "engine_temp",
                "value": value,
                "severity": "warning",
                "message": f"Engine temperature high: {value}°C (>{thresholds['warning_high']}°C)",
                "recommendation": "Monitor temperature and check coolant level"
            }
        else:
            return {
                "sensor": "engine_temp",
                "value": value,
                "severity": "normal",
                "message": f"Engine temperature normal: {value}°C"
            }

    def _check_tire_pressure(self, value: float) -> Dict[str, Any]:
        """Check tire pressure against thresholds"""
        thresholds = self.THRESHOLDS["tire_pressure"]

        if value < thresholds["critical_low"]:
            return {
                "sensor": "tire_pressure",
                "value": value,
                "severity": "critical",
                "message": f"Tire pressure critically low: {value} psi (<{thresholds['critical_low']} psi)",
                "recommendation": "Inflate tires immediately - blowout risk"
            }
        elif value < thresholds["warning_low"]:
            return {
                "sensor": "tire_pressure",
                "value": value,
                "severity": "warning",
                "message": f"Tire pressure low: {value} psi (<{thresholds['warning_low']} psi)",
                "recommendation": "Inflate tires to recommended pressure"
            }
        else:
            return {
                "sensor": "tire_pressure",
                "value": value,
                "severity": "normal",
                "message": f"Tire pressure normal: {value} psi"
            }

    def _check_brake_fluid(self, value: float) -> Dict[str, Any]:
        """Check brake fluid level against thresholds"""
        thresholds = self.THRESHOLDS["brake_fluid_level"]

        if value < thresholds["critical_low"]:
            return {
                "sensor": "brake_fluid_level",
                "value": value,
                "severity": "critical",
                "message": f"Brake fluid critically low: {value}% (<{thresholds['critical_low']}%)",
                "recommendation": "Do not drive - brake failure risk"
            }
        elif value < thresholds["warning_low"]:
            return {
                "sensor": "brake_fluid_level",
                "value": value,
                "severity": "warning",
                "message": f"Brake fluid low: {value}% (<{thresholds['warning_low']}%)",
                "recommendation": "Top up brake fluid and check for leaks"
            }
        else:
            return {
                "sensor": "brake_fluid_level",
                "value": value,
                "severity": "normal",
                "message": f"Brake fluid level normal: {value}%"
            }

    def _check_mileage(self, value: int) -> Dict[str, Any]:
        """Check mileage for maintenance needs"""
        thresholds = self.THRESHOLDS["mileage"]

        if value > thresholds["high"]:
            return {
                "sensor": "mileage",
                "value": value,
                "severity": "warning",
                "message": f"High mileage: {value:,} km (>{thresholds['high']:,} km)",
                "recommendation": "Schedule comprehensive service"
            }
        elif value > thresholds["medium"]:
            return {
                "sensor": "mileage",
                "value": value,
                "severity": "normal",
                "message": f"Medium mileage: {value:,} km - regular maintenance needed"
            }
        else:
            return {
                "sensor": "mileage",
                "value": value,
                "severity": "normal",
                "message": f"Low mileage: {value:,} km"
            }

    def _categorize_finding(self, finding: Dict[str, Any], anomalies: Dict):
        """Categorize finding into appropriate severity bucket"""
        severity = finding.get("severity", "normal")
        anomalies[severity].append(finding)

    def _generate_summary(self, anomalies: Dict) -> str:
        """Generate human-readable summary"""
        critical_count = len(anomalies["critical"])
        warning_count = len(anomalies["warning"])

        if critical_count > 0:
            return f"CRITICAL: {critical_count} critical issue(s) detected. Immediate action required."
        elif warning_count > 0:
            return f"WARNING: {warning_count} warning(s) detected. Maintenance recommended."
        else:
            return "All sensors within normal range. Vehicle healthy."