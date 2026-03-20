"""
Base Agent Class
Parent class for all agents in the system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class BaseAgent(ABC):
    """
    Base class for all agents

    All agents inherit from this class and must implement the process() method

    Think of this as a template/blueprint that all agents follow
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the base agent

        Args:
            name: Agent's name (e.g., "DataAnalysisAgent")
            description: What this agent does
        """
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.call_count = 0  # Track how many times agent is used

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data and return results

        This is an ABSTRACT method - each child agent MUST implement it!
        Like saying: "All agents must have a process method, but each
        does it differently"

        Args:
            data: Input data (vehicle info, sensors, etc.)

        Returns:
            dict: Agent's analysis/results
        """
        pass  # Child classes will implement this

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this agent

        Returns:
            dict: Agent metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "total_calls": self.call_count
        }

    def _log_call(self):
        """
        Internal method to track agent usage
        Called each time process() is executed
        """
        self.call_count += 1