"""
Master Agent - Full Integration (8 Agents)
Orchestrates all agents from Person 1, 2, and 4
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
from .base_agent import BaseAgent

# === IMPORT ALL AGENTS ===
# Your original agents
from .data_analysis_agent import DataAnalysisAgent
from .diagnosis_agent import DiagnosisAgent

# Person 2 Advanced Agents
from .person2_data_analysis_agent import Person2DataAnalysisAgent
from .person2_diagnosis_agent import Person2DiagnosisAgent

# Person 4 Business Logic Agents
from .engagement_agent import EngagementAgent
from .scheduling_agent import SchedulingAgent
from .feedback_agent import FeedbackAgent
from .manufacturing_insights_agent import ManufacturingInsightsAgent


class MasterAgent(BaseAgent):
    def __init__(self, ml_predictor, state_manager=None):
        super().__init__(
            name="MasterAgent",
            description="Orchestrates all 8 specialized agents for predictive maintenance"
        )
        self.state_manager = state_manager
        self.agents = {}
        self._register_all_agents(ml_predictor)

    def _register_all_agents(self, ml_predictor):
        """Register all 8 agents - FIXED for Person 2 & Person 4 constructors"""
        print("🚀 Starting agent registration...")

        # 1. Your Basic Agents (Person 1)
        self.register_agent(DataAnalysisAgent())
        self.register_agent(DiagnosisAgent(ml_predictor))  # ← Needs ml_predictor

        # 2. Person 2 Advanced Agents (NO ml_predictor needed)
        self.register_agent(Person2DataAnalysisAgent())  # Health scoring
        self.register_agent(Person2DiagnosisAgent())  # Customer messaging

        # 3. Person 4 Business Logic Agents (NO ml_predictor needed)
        self.register_agent(EngagementAgent())  # ⭐ Time-based notifications
        self.register_agent(SchedulingAgent())
        self.register_agent(FeedbackAgent())
        self.register_agent(ManufacturingInsightsAgent())

        print(f"✅ Successfully registered {len(self.agents)} agents")

    def register_agent(self, agent: BaseAgent):
        """Register single agent"""
        if agent.name not in self.agents:
            self.agents[agent.name] = agent
            print(f"✓ Registered: {agent.name}")
        else:
            print(f"⚠️ Agent {agent.name} already registered")

    def get_registered_agents(self) -> List[Dict[str, Any]]:
        return [agent.get_info() for agent in self.agents.values()]

    def process(self, data: Dict[str, Any], workflow_id: str = None) -> Dict[str, Any]:
        """Run analysis with ALL agents + time awareness for EngagementAgent"""
        vehicle_id = data.get("vehicle_id", "Unknown")
        now = datetime.now()
        current_hour = now.hour

        # Add current time info (critical for EngagementAgent)
        data = data.copy()
        data.update({
            "current_time": now,
            "current_hour": current_hour,
            "is_business_hours": 9 <= current_hour < 20,   # 9 AM - 8 PM
            "owner": data.get("owner", {})                 # fallback if not provided
        })

        print(f"\n{'='*75}")
        print(f"🔍 MasterAgent analyzing {vehicle_id} | Time: {now.strftime('%H:%M')} ({current_hour}h)")
        print('='*75)

        if self.state_manager and workflow_id:
            self.state_manager.update_workflow(workflow_id, status="running")

        results = {
            "vehicle_id": vehicle_id,
            "timestamp": now.isoformat(),
            "current_hour": current_hour,
            "is_business_hours": data["is_business_hours"],
            "agents_consulted": [],
            "findings": {},
            "final_assessment": {}
        }

        # Run every registered agent
        for name, agent in list(self.agents.items()):
            try:
                print(f"→ Running {name}...")
                agent_result = agent.process(data)   # All agents should have .process(data)
                results["findings"][name] = agent_result
                results["agents_consulted"].append(name)
                print(f"  ✓ {name} completed")
            except Exception as e:
                print(f"  ✗ Error in {name}: {str(e)}")
                results["findings"][name] = {"status": "error", "message": str(e)}

        # Final summary
        results["final_assessment"] = {
            "overall_status": "critical" if any("critical" in str(v).lower() for v in results["findings"].values()) else "healthy",
            "summary": f"Completed analysis using {len(results['agents_consulted'])} agents",
            "recommendations": ["Check individual agent findings for details"]
        }

        if self.state_manager and workflow_id:
            self.state_manager.update_workflow(workflow_id, status="completed", results=results)

        print(f"🎉 Analysis finished with {len(results['agents_consulted'])} agents")
        return results