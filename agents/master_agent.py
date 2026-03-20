"""
Master Agent
Orchestrates and coordinates all other agents
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
from .base_agent import BaseAgent
from .data_analysis_agent import DataAnalysisAgent
from .diagnosis_agent import DiagnosisAgent

class MasterAgent(BaseAgent):
    """
    Master orchestration agent

    Coordinates multiple agents and combines their results
    """

    def __init__(self, ml_predictor, state_manager=None):
        """
        Initialize Master Agent

        Args:
            ml_predictor: MLPredictor instance
            state_manager: StateManager instance (optional)
        """
        super().__init__(
            name="MasterAgent",
            description="Orchestrates and coordinates all specialized agents"
        )

        # State manager
        self.state_manager = state_manager

        # Initialize child agents
        self.agents = {}
        self._register_default_agents(ml_predictor)

    def _register_default_agents(self, ml_predictor):
        """Register default agents"""
        # Data Analysis Agent
        self.register_agent(DataAnalysisAgent())

        # Diagnosis Agent (uses ML model)
        self.register_agent(DiagnosisAgent(ml_predictor))

    def register_agent(self, agent: BaseAgent):
        """
        Register a new agent

        Args:
            agent: Agent instance to register
        """
        self.agents[agent.name] = agent
        print(f"✓ Registered agent: {agent.name}")

    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """
        Get list of all registered agents

        Returns:
            list: Agent information
        """
        return [agent.get_info() for agent in self.agents.values()]

    def process(self, data: Dict[str, Any], workflow_id: str = None) -> Dict[str, Any]:
        """
        Coordinate multi-agent analysis

        Args:
            data: Dictionary containing vehicle_id and sensors
            workflow_id: Optional workflow ID for tracking

        Returns:
            dict: Combined analysis from all agents
        """
        self._log_call()

        vehicle_id = data.get("vehicle_id", "Unknown")

        print(f"\n{'='*60}")
        print(f"Master Agent: Analyzing {vehicle_id}")
        if workflow_id:
            print(f"Workflow ID: {workflow_id}")
        print('='*60)

        # Update workflow status if state manager available
        if self.state_manager and workflow_id:
            self.state_manager.update_workflow(
                workflow_id,
                status="running"
            )

        results = {
            "vehicle_id": vehicle_id,
            "master_agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_id": workflow_id,
            "agents_consulted": [],
            "findings": {},
            "final_assessment": {}
        }

        try:
            # 1. Call Data Analysis Agent
            if "DataAnalysisAgent" in self.agents:
                print("→ Consulting Data Analysis Agent...")
                analysis = self.agents["DataAnalysisAgent"].process(data)
                results["findings"]["data_analysis"] = analysis
                results["agents_consulted"].append("DataAnalysisAgent")
                print(f"  Status: {analysis.get('overall_status')}")

            # 2. Call Diagnosis Agent
            if "DiagnosisAgent" in self.agents:
                print("→ Consulting Diagnosis Agent...")
                diagnosis = self.agents["DiagnosisAgent"].process(data)
                results["findings"]["diagnosis"] = diagnosis
                results["agents_consulted"].append("DiagnosisAgent")
                print(f"  Risk: {diagnosis['ml_prediction'].get('risk_level')}")

            # 3. Generate final assessment
            print("→ Generating final assessment...")
            final_assessment = self._generate_final_assessment(results["findings"])
            results["final_assessment"] = final_assessment

            print(f"  Final Status: {final_assessment['overall_status']}")

            # Update workflow with success
            if self.state_manager and workflow_id:
                self.state_manager.update_workflow(
                    workflow_id,
                    status="completed",
                    results=results,
                    agents_executed=results["agents_consulted"]
                )

        except Exception as e:
            print(f"✗ Error during analysis: {e}")

            # Update workflow with error
            if self.state_manager and workflow_id:
                self.state_manager.update_workflow(
                    workflow_id,
                    status="failed",
                    error=str(e)
                )

            raise

        print('='*60)

        return results

    def _generate_final_assessment(self, findings: Dict) -> Dict[str, Any]:
        """
        Combine findings from all agents into final assessment

        Args:
            findings: Results from all agents

        Returns:
            dict: Final assessment and recommendations
        """
        # Extract key information
        data_analysis = findings.get("data_analysis", {})
        diagnosis = findings.get("diagnosis", {})

        # Determine overall status (most severe wins)
        statuses = []

        if data_analysis:
            statuses.append(data_analysis.get("overall_status", "unknown"))

        if diagnosis:
            ml_pred = diagnosis.get("ml_prediction", {})
            risk_level = ml_pred.get("risk_level", "LOW")
            if risk_level == "HIGH":
                statuses.append("critical")
            elif risk_level == "MEDIUM":
                statuses.append("warning")
            else:
                statuses.append("healthy")

        # Most severe status
        if "critical" in statuses:
            overall_status = "critical"
            priority = "URGENT"
        elif "warning" in statuses:
            overall_status = "warning"
            priority = "HIGH"
        else:
            overall_status = "healthy"
            priority = "NORMAL"

        # Collect all recommendations
        recommendations = []

        # From data analysis
        if data_analysis:
            critical_anomalies = data_analysis.get("findings", {}).get("critical", [])
            for anomaly in critical_anomalies:
                recommendations.append(anomaly.get("recommendation", ""))

        # From diagnosis
        if diagnosis:
            diag_actions = diagnosis.get("recommended_actions", [])
            recommendations.extend(diag_actions)

        # Remove duplicates
        recommendations = list(set(filter(None, recommendations)))

        # Generate summary
        if overall_status == "critical":
            summary = "CRITICAL CONDITION: Immediate attention required. Multiple systems showing critical issues."
        elif overall_status == "warning":
            summary = "WARNING: Vehicle requires maintenance. Schedule service within 1 week."
        else:
            summary = "HEALTHY: All systems operating normally. Continue regular maintenance schedule."

        return {
            "overall_status": overall_status,
            "priority": priority,
            "summary": summary,
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "critical_issues_count": len(data_analysis.get("findings", {}).get("critical", [])),
            "warning_issues_count": len(data_analysis.get("findings", {}).get("warning", [])),
            "failure_probability": diagnosis.get("ml_prediction", {}).get("failure_probability", 0) if diagnosis else 0
        }