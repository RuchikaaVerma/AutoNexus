"""
PURPOSE: AI agent for Root Cause Analysis and CAPA using HuggingFace LLM.
         Generates PDF reports and saves CSV feedback for model retraining.
CONNECTS TO: FILES 1,18,19 (rca+capa), ml/evaluation/accuracy_report.json (P2)
OUTPUTS: PDF reports (reports/), CSV feedback (data/feedback/service_feedback.csv)
"""
import json
import logging
import csv
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from services.agents.config.hf_model_config import (
    MANUFACTURING_MODEL, HF_TOKEN, HF_RUN_MODE, ML_EVAL_DIR
)

logger = logging.getLogger(__name__)


class ManufacturingInsightsAgent:
    """Generates RCA and CAPA reports using AI + saves feedback data."""

    FAILURE_KNOWLEDGE = {
        "brakes": {
            "causes":      ["worn brake pads", "low brake fluid", "overheating", "caliper sticking"],
            "corrective":  ["replace brake pads", "top up brake fluid", "inspect calipers"],
            "preventive":  ["monthly brake fluid check", "brake inspection every 10,000km"],
        },
        "engine": {
            "causes":      ["overheating", "low oil pressure", "coolant leak", "timing belt wear"],
            "corrective":  ["replace coolant", "oil change", "timing belt replacement"],
            "preventive":  ["regular oil changes", "coolant flush every 2 years"],
        },
        "engine oil": {
            "causes":      ["oil degradation", "extended service interval", "high mileage"],
            "corrective":  ["immediate oil and filter change"],
            "preventive":  ["oil change every 5,000km or 3 months"],
        },
        "tires": {
            "causes":      ["underinflation", "misalignment", "worn tread"],
            "corrective":  ["rotate tires", "alignment check", "replace worn tires"],
            "preventive":  ["monthly pressure check", "rotation every 8,000km"],
        },
        "transmission": {
            "causes":      ["low transmission fluid", "worn clutch", "overheating"],
            "corrective":  ["fluid replacement", "clutch inspection", "cooling system check"],
            "preventive":  ["transmission fluid check every 40,000km"],
        },
        "battery": {
            "causes":      ["age deterioration", "corrosion", "alternator failure"],
            "corrective":  ["battery replacement", "terminal cleaning", "alternator test"],
            "preventive":  ["annual battery health check", "keep terminals clean"],
        },
    }

    def __init__(self):
        self.name = "ManufacturingInsightsAgent"
        self._ensure_directories()
        logger.info("ManufacturingInsightsAgent initialized")

    def _ensure_directories(self):
        """Create required directories if they don't exist."""
        Path("data/feedback").mkdir(parents=True, exist_ok=True)
        Path("reports").mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured data/feedback/ and reports/ directories exist")

    def analyze_failure(self, vehicle_id: str, component: str, sensor_data: dict = None) -> dict:
        """
        Analyze a vehicle failure and return RCA + CAPA.
        Uses knowledge base (always works) + optional LLM enrichment.
        """
        logger.info(f"Analyzing failure | vehicle={vehicle_id} | component={component}")
        comp_key  = component.lower()
        knowledge = self.FAILURE_KNOWLEDGE.get(comp_key, self.FAILURE_KNOWLEDGE["engine"])

        # Build RCA
        rca = {
            "vehicle_id":    vehicle_id,
            "component":     component,
            "timestamp":     datetime.now().isoformat(),
            "root_causes":   knowledge["causes"],
            "primary_cause": knowledge["causes"][0],
            "sensor_data":   sensor_data or {},
            "severity":      self._calculate_severity(sensor_data),
        }

        # Build CAPA
        capa = {
            "corrective_actions": knowledge["corrective"],
            "preventive_actions": knowledge["preventive"],
            "priority":           "HIGH" if rca["severity"] > 7 else "MEDIUM",
            "deadline_days":      7 if rca["severity"] > 7 else 14,
        }

        # Try LLM enrichment (optional — works without it)
        llm_insight = self._get_llm_insight(component, rca["primary_cause"])
        if llm_insight:
            rca["ai_insight"] = llm_insight

        result = {"rca": rca, "capa": capa, "success": True}
        logger.info(f"Analysis complete | severity={rca['severity']} | priority={capa['priority']}")
        return result

    def _calculate_severity(self, sensor_data: dict) -> int:
        """Score severity 1-10 from sensor readings."""
        if not sensor_data:
            return 5
        score = 5
        if sensor_data.get("brake_temp", 0) > 90:       score += 2
        if sensor_data.get("brake_fluid", 100) < 30:    score += 2
        if sensor_data.get("oil_pressure", 40) < 25:    score += 1
        if sensor_data.get("coolant_temp", 0) > 110:    score += 2
        if sensor_data.get("battery_voltage", 12) < 11: score += 1
        return min(score, 10)

    def _get_llm_insight(self, component: str, cause: str) -> str:
        """Optional LLM enrichment — returns empty string if unavailable."""
        if not HF_TOKEN or HF_RUN_MODE != "api":
            return ""
        try:
            from langchain_huggingface import HuggingFaceEndpoint
            llm = HuggingFaceEndpoint(
                repo_id=MANUFACTURING_MODEL,
                huggingfacehub_api_token=HF_TOKEN,
                max_new_tokens=100,
            )
            prompt = (
                f"In one sentence, explain why {cause} causes {component} failure "
                f"in a vehicle and what the immediate risk is."
            )
            return llm.invoke(prompt).strip()
        except Exception as e:
            logger.debug(f"LLM insight skipped: {e}")
            return ""

    def read_ml_accuracy(self) -> dict:
        """Read P2's model accuracy report."""
        report_path = ML_EVAL_DIR / "accuracy_report.json"
        if report_path.exists():
            with open(report_path) as f:
                return json.load(f)
        return {"note": "P2 accuracy report not yet generated"}

    # ═══════════════════════════════════════════════════════════════════════
    # NEW: FEEDBACK LOOP FUNCTIONS FOR MODEL RETRAINING
    # ═══════════════════════════════════════════════════════════════════════

    def save_service_feedback(
        self,
        vehicle_id: str,
        component: str,
        predicted_days: int,
        actual_days: int,
        service_completed: bool = True,
        csat_score: int = 3,
        vehicle_model: str = "Unknown",
        region: str = "Unknown",
        climate: str = "Temperate",
        mileage: int = 0
    ) -> str:
        """
        Saves service outcome to CSV for Person 2's model retraining.
        
        CRITICAL: This CSV has 13 columns (not 10) to match training data.
        Called after each service completion by feedback_agent.
        
        Returns: Path to the CSV file
        """
        csv_path = 'data/feedback/service_feedback.csv'
        file_exists = os.path.exists(csv_path)
        
        # Calculate prediction accuracy
        if actual_days > 0:
            accuracy = 1.0 - abs(predicted_days - actual_days) / actual_days
            accuracy = max(0.0, min(1.0, accuracy))  # Clamp to [0,1]
        else:
            accuracy = 0.0
        
        # Prepare row data with ALL 13 features
        row = {
            'vehicle_id':               vehicle_id,
            'component':                component,
            'failure_date':             datetime.now().isoformat(),
            'prediction_date':          datetime.now().isoformat(),
            'predicted_days_to_failure': predicted_days,
            'actual_days_to_failure':   actual_days,
            'prediction_accuracy':      round(accuracy, 3),
            'service_completed':        int(service_completed),
            'csat_score':               csat_score,
            'vehicle_model':            vehicle_model,
            'region':                   region,
            'climate':                  climate,
            'mileage':                  mileage,
        }
        
        # Write to CSV
        with open(csv_path, 'a', newline='') as f:
            fieldnames = list(row.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(row)
        
        logger.info(f"Saved service feedback to {csv_path} | vehicle={vehicle_id} | accuracy={accuracy:.2f}")
        return csv_path

    def generate_weekly_report(self, days_back: int = 7) -> dict:
        """
        Generates weekly manufacturing insights report.
        Called by Master Agent every Sunday.
        
        Returns: {
            'pdf_path': str,
            'csv_path': str,
            'failures_analyzed': int,
            'top_components': list,
            'avg_severity': float
        }
        """
        logger.info(f"Generating weekly manufacturing report (last {days_back} days)")
        
        # Read service feedback CSV
        csv_path = 'data/feedback/service_feedback.csv'
        
        if not os.path.exists(csv_path):
            logger.warning("No service feedback data found. Generating empty report.")
            return {
                'status': 'NO_DATA',
                'message': 'No service feedback collected yet. Run the system for a few days first.',
            }
        
        # Parse CSV data
        failures = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                failures.append(row)
        
        if len(failures) == 0:
            return {'status': 'NO_DATA', 'message': 'CSV exists but is empty'}
        
        # Analyze patterns
        patterns = self._analyze_patterns(failures)
        
        # Generate PDF report
        pdf_path = self._generate_pdf_report(patterns, failures)
        
        # Calculate statistics
        avg_accuracy = sum(float(f['prediction_accuracy']) for f in failures) / len(failures)
        avg_csat = sum(int(f['csat_score']) for f in failures) / len(failures)
        
        result = {
            'status': 'SUCCESS',
            'pdf_path': pdf_path,
            'csv_path': csv_path,
            'failures_analyzed': len(failures),
            'top_components': patterns['top_components'][:5],
            'avg_prediction_accuracy': round(avg_accuracy, 3),
            'avg_csat_score': round(avg_csat, 2),
            'patterns': patterns,
        }
        
        logger.info(f"Weekly report generated | failures={len(failures)} | pdf={pdf_path}")
        return result

    def _analyze_patterns(self, failures: List[dict]) -> dict:
        """Analyze failure patterns from service feedback data."""
        from collections import Counter
        
        components = Counter(f['component'] for f in failures)
        regions = Counter(f['region'] for f in failures)
        models = Counter(f['vehicle_model'] for f in failures)
        
        return {
            'top_components': [{'component': c, 'count': n} for c, n in components.most_common(10)],
            'by_region': dict(regions),
            'by_model': dict(models),
            'total_failures': len(failures),
        }

    def _generate_pdf_report(self, patterns: dict, failures: List[dict]) -> str:
        """
        Generates human-readable PDF report for manufacturing stakeholders.
        Uses reportlab for PDF generation.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
        except ImportError:
            logger.error("reportlab not installed. Run: pip install reportlab")
            return ""
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = f'reports/manufacturing_rca_{timestamp}.pdf'
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 50, "Manufacturing RCA Report")
        
        # Metadata
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 80, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, height - 100, f"Failures Analyzed: {len(failures)}")
        c.drawString(50, height - 120, f"Period: Last 7 days")
        
        # Section 1: Top Failing Components
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 160, "Top Failing Components:")
        
        c.setFont("Helvetica", 11)
        y = height - 190
        for item in patterns['top_components'][:10]:
            comp = item['component']
            count = item['count']
            c.drawString(60, y, f"• {comp}: {count} failures")
            y -= 20
        
        # Section 2: Root Causes (from knowledge base)
        y -= 20
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Common Root Causes:")
        y -= 25
        
        c.setFont("Helvetica", 11)
        seen_components = set()
        for item in patterns['top_components'][:5]:
            comp = item['component'].lower()
            if comp in self.FAILURE_KNOWLEDGE and comp not in seen_components:
                seen_components.add(comp)
                causes = self.FAILURE_KNOWLEDGE[comp]['causes']
                c.drawString(60, y, f"{comp.upper()}: {', '.join(causes[:2])}")
                y -= 18
        
        # Section 3: CAPA Recommendations
        y -= 20
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "CAPA Recommendations:")
        y -= 25
        
        c.setFont("Helvetica", 11)
        for item in patterns['top_components'][:3]:
            comp = item['component'].lower()
            if comp in self.FAILURE_KNOWLEDGE:
                preventive = self.FAILURE_KNOWLEDGE[comp]['preventive']
                c.drawString(60, y, f"• {comp.upper()}: {preventive[0]}")
                y -= 18
        
        # Section 4: Regional Distribution
        y -= 20
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Failures by Region:")
        y -= 25
        
        c.setFont("Helvetica", 11)
        for region, count in list(patterns['by_region'].items())[:5]:
            c.drawString(60, y, f"• {region}: {count} failures")
            y -= 18
        
        # Footer
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 50, "Confidential — Autonomous Predictive Maintenance System")
        c.drawString(50, 35, f"Report generated by ManufacturingInsightsAgent")
        
        c.save()
        logger.info(f"PDF report saved: {pdf_path}")
        return pdf_path


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FILE 11: Manufacturing Insights Agent — Self Test")
    print("="*60)
    
    agent = ManufacturingInsightsAgent()
    
    # Test 1: Analyze single failure
    print("\n[TEST 1] Analyzing single failure...")
    result = agent.analyze_failure(
        vehicle_id  = "VEH001",
        component   = "brakes",
        sensor_data = {"brake_temp": 95, "brake_fluid": 25, "oil_pressure": 35},
    )
    rca  = result["rca"]
    capa = result["capa"]
    print(f"  Vehicle      : {rca['vehicle_id']}")
    print(f"  Component    : {rca['component']}")
    print(f"  Primary Cause: {rca['primary_cause']}")
    print(f"  Severity     : {rca['severity']}/10")
    print(f"  Priority     : {capa['priority']}")
    print(f"  Corrective   : {capa['corrective_actions'][0]}")
    print(f"  Preventive   : {capa['preventive_actions'][0]}")
    
    # Test 2: Save service feedback
    print("\n[TEST 2] Saving service feedback to CSV...")
    csv_path = agent.save_service_feedback(
        vehicle_id="VEH001",
        component="brakes",
        predicted_days=14,
        actual_days=12,
        service_completed=True,
        csat_score=4,
        vehicle_model="Toyota Camry",
        region="North America",
        climate="Temperate",
        mileage=45000
    )
    print(f"  ✓ Feedback saved to: {csv_path}")
    
    # Test 3: Save a few more records for demo
    print("\n[TEST 3] Adding more test records...")
    test_records = [
        ("VEH002", "engine", 7, 8, True, 5, "Honda Accord", "Europe", "Cold", 60000),
        ("VEH003", "tires", 30, 28, True, 3, "Ford F-150", "North America", "Hot", 35000),
        ("VEH004", "battery", 90, 85, True, 4, "Tesla Model 3", "Asia", "Temperate", 20000),
    ]
    for rec in test_records:
        agent.save_service_feedback(*rec)
    print(f"  ✓ Added {len(test_records)} more records")
    
    # Test 4: Generate weekly report
    print("\n[TEST 4] Generating weekly manufacturing report...")
    report = agent.generate_weekly_report(days_back=7)
    if report['status'] == 'SUCCESS':
        print(f"  ✓ Report generated: {report['pdf_path']}")
        print(f"  ✓ Failures analyzed: {report['failures_analyzed']}")
        print(f"  ✓ Avg prediction accuracy: {report['avg_prediction_accuracy']:.2%}")
        print(f"  ✓ Avg CSAT: {report['avg_csat_score']:.1f}/5")
        print(f"  ✓ Top component: {report['top_components'][0]['component']}")
    else:
        print(f"  ! {report['message']}")
    
    print("\n" + "="*60)
    print("  FILE 11 complete! Check data/feedback/ and reports/")
    print("="*60 + "\n")