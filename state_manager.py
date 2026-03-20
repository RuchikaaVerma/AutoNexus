"""
State Management System
Tracks vehicle states, workflow executions, and agent activity
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from collections import defaultdict
import uuid


class StateManager:
    """
    Manages system state and workflow tracking

    Keeps track of:
    - Vehicle analysis history
    - Workflow executions
    - Agent activity
    - System statistics
    """

    def __init__(self):
        """Initialize State Manager"""
        # Storage (in-memory for simplicity)
        self.workflows = {}  # workflow_id -> workflow_data
        self.vehicle_states = {}  # vehicle_id -> latest_state
        self.vehicle_history = defaultdict(list)  # vehicle_id -> [workflow_ids]
        self.agent_activity = defaultdict(int)  # agent_name -> call_count

        # Metadata
        self.created_at = datetime.now(timezone.utc)
        self.total_workflows = 0

        print("✓ State Manager initialized")

    def create_workflow(self, vehicle_id: str, workflow_type: str = "analysis") -> str:
        """
        Create a new workflow execution

        Args:
            vehicle_id: Vehicle being analyzed
            workflow_type: Type of workflow (analysis, prediction, etc.)

        Returns:
            str: Unique workflow ID
        """
        # Generate unique workflow ID
        workflow_id = f"WF-{uuid.uuid4().hex[:8]}"

        # Create workflow record
        workflow = {
            "workflow_id": workflow_id,
            "vehicle_id": vehicle_id,
            "type": workflow_type,
            "status": "running",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "duration_seconds": None,
            "agents_executed": [],
            "results": {},
            "errors": []
        }

        # Store workflow
        self.workflows[workflow_id] = workflow

        # Add to vehicle history
        self.vehicle_history[vehicle_id].append(workflow_id)

        # Increment counter
        self.total_workflows += 1

        print(f"✓ Created workflow: {workflow_id} for {vehicle_id}")

        return workflow_id

    def update_workflow(
            self,
            workflow_id: str,
            status: str = None,
            results: Dict = None,
            agents_executed: List[str] = None,
            error: str = None
    ):
        """
        Update workflow with new information

        Args:
            workflow_id: Workflow to update
            status: New status (running, completed, failed)
            results: Analysis results
            agents_executed: List of agents that ran
            error: Error message if failed
        """
        if workflow_id not in self.workflows:
            print(f"✗ Workflow not found: {workflow_id}")
            return

        workflow = self.workflows[workflow_id]

        # Update status
        if status:
            workflow["status"] = status

        # Update results
        if results:
            workflow["results"] = results

        # Update agents
        if agents_executed:
            workflow["agents_executed"] = agents_executed
            # Track agent activity
            for agent in agents_executed:
                self.agent_activity[agent] += 1

        # Add error
        if error:
            workflow["errors"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error
            })

        # Update timestamp
        workflow["updated_at"] = datetime.now(timezone.utc).isoformat()

        # If completed, calculate duration
        if status in ["completed", "failed"]:
            workflow["completed_at"] = datetime.now(timezone.utc).isoformat()
            started = datetime.fromisoformat(workflow["started_at"])
            completed = datetime.now(timezone.utc)
            workflow["duration_seconds"] = (completed - started).total_seconds()

            # Update vehicle state
            self._update_vehicle_state(workflow["vehicle_id"], workflow)

        print(f"✓ Updated workflow: {workflow_id} - Status: {status}")

    def _update_vehicle_state(self, vehicle_id: str, workflow: Dict):
        """
        Update vehicle's latest state

        Args:
            vehicle_id: Vehicle ID
            workflow: Completed workflow
        """
        # Extract key information from results
        results = workflow.get("results", {})
        final_assessment = results.get("final_assessment", {})

        # Create state snapshot
        state = {
            "vehicle_id": vehicle_id,
            "last_analyzed": workflow["completed_at"],
            "workflow_id": workflow["workflow_id"],
            "overall_status": final_assessment.get("overall_status", "unknown"),
            "failure_probability": final_assessment.get("failure_probability", 0),
            "critical_issues_count": final_assessment.get("critical_issues_count", 0),
            "warning_issues_count": final_assessment.get("warning_issues_count", 0),
            "recommendations": final_assessment.get("recommendations", [])
        }

        self.vehicle_states[vehicle_id] = state

    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """
        Get workflow by ID

        Args:
            workflow_id: Workflow ID

        Returns:
            dict: Workflow data or None
        """
        return self.workflows.get(workflow_id)

    def get_vehicle_state(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get vehicle's current state

        Args:
            vehicle_id: Vehicle ID

        Returns:
            dict: Current state or None
        """
        return self.vehicle_states.get(vehicle_id)

    def get_vehicle_history(self, vehicle_id: str, limit: int = 10) -> List[Dict]:
        """
        Get vehicle's analysis history

        Args:
            vehicle_id: Vehicle ID
            limit: Maximum number of workflows to return

        Returns:
            list: List of workflows (most recent first)
        """
        workflow_ids = self.vehicle_history.get(vehicle_id, [])

        # Get workflows (most recent first)
        workflows = []
        for wf_id in reversed(workflow_ids[-limit:]):
            workflow = self.workflows.get(wf_id)
            if workflow:
                workflows.append(workflow)

        return workflows

    def get_all_vehicle_states(self) -> List[Dict]:
        """
        Get current state of all vehicles

        Returns:
            list: All vehicle states
        """
        return list(self.vehicle_states.values())

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system-wide statistics

        Returns:
            dict: System statistics
        """
        # Count workflows by status
        status_counts = defaultdict(int)
        for workflow in self.workflows.values():
            status_counts[workflow["status"]] += 1

        # Calculate average duration
        completed_workflows = [
            wf for wf in self.workflows.values()
            if wf["duration_seconds"] is not None
        ]
        avg_duration = (
            sum(wf["duration_seconds"] for wf in completed_workflows) / len(completed_workflows)
            if completed_workflows else 0
        )

        # Count vehicles by status
        vehicle_status_counts = defaultdict(int)
        for state in self.vehicle_states.values():
            vehicle_status_counts[state["overall_status"]] += 1

        return {
            "system": {
                "uptime_seconds": (datetime.now(timezone.utc) - self.created_at).total_seconds(),
                "created_at": self.created_at.isoformat()
            },
            "workflows": {
                "total": self.total_workflows,
                "by_status": dict(status_counts),
                "average_duration_seconds": round(avg_duration, 2)
            },
            "vehicles": {
                "total_analyzed": len(self.vehicle_states),
                "by_status": dict(vehicle_status_counts)
            },
            "agents": {
                "activity": dict(self.agent_activity),
                "total_executions": sum(self.agent_activity.values())
            }
        }

    def clear_history(self, vehicle_id: str = None):
        """
        Clear workflow history

        Args:
            vehicle_id: If provided, clear only this vehicle's history
                       If None, clear all history
        """
        if vehicle_id:
            # Clear specific vehicle
            workflow_ids = self.vehicle_history.get(vehicle_id, [])
            for wf_id in workflow_ids:
                if wf_id in self.workflows:
                    del self.workflows[wf_id]
            self.vehicle_history[vehicle_id] = []
            if vehicle_id in self.vehicle_states:
                del self.vehicle_states[vehicle_id]
            print(f"✓ Cleared history for {vehicle_id}")
        else:
            # Clear all
            self.workflows.clear()
            self.vehicle_states.clear()
            self.vehicle_history.clear()
            self.agent_activity.clear()
            self.total_workflows = 0
            print("✓ Cleared all history")