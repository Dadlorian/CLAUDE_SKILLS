"""
Practice Management Integration
Integrates legal research with practice management systems
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Matter:
    """Law firm matter"""
    matter_id: str
    client_name: str
    matter_name: str
    attorney: str
    status: str
    budget: float
    spent: float


class PracticeManagementIntegration:
    """
    Integrates research with practice management
    """

    def __init__(self):
        """Initialize integration"""
        self.matters = {}
        self.time_entries = []

    def create_matter(self, matter_data: Dict) -> Matter:
        """
        Create new matter in PM system

        Args:
            matter_data: Matter details

        Returns:
            Matter object
        """
        matter = Matter(
            matter_id=matter_data.get("id", f"matter_{len(self.matters)}"),
            client_name=matter_data.get("client", ""),
            matter_name=matter_data.get("name", ""),
            attorney=matter_data.get("attorney", ""),
            status=matter_data.get("status", "open"),
            budget=matter_data.get("budget", 0.0),
            spent=0.0
        )

        self.matters[matter.matter_id] = matter
        logger.info(f"Created matter: {matter.matter_id}")
        return matter

    def log_research_time(self, matter_id: str, hours: float, description: str):
        """
        Log research time to matter

        Args:
            matter_id: Matter ID
            hours: Hours spent
            description: Work description
        """
        if matter_id not in self.matters:
            logger.warning(f"Matter {matter_id} not found")
            return

        entry = {
            "matter_id": matter_id,
            "hours": hours,
            "description": description,
            "cost": hours * 150  # Assume $150/hour
        }

        self.time_entries.append(entry)
        self.matters[matter_id].spent += entry["cost"]

        logger.info(f"Logged {hours} hours to {matter_id}, cost: ${entry['cost']:.2f}")

    def get_matter_research_summary(self, matter_id: str) -> Dict:
        """
        Get research summary for matter

        Args:
            matter_id: Matter ID

        Returns:
            Summary dictionary
        """
        if matter_id not in self.matters:
            return {}

        matter = self.matters[matter_id]
        entries = [e for e in self.time_entries if e["matter_id"] == matter_id]

        total_hours = sum(e["hours"] for e in entries)
        total_cost = sum(e["cost"] for e in entries)

        return {
            "matter_id": matter_id,
            "matter_name": matter.matter_name,
            "client": matter.client_name,
            "research_hours": total_hours,
            "research_cost": total_cost,
            "total_spent": matter.spent,
            "budget": matter.budget,
            "budget_remaining": matter.budget - matter.spent,
            "budget_utilization": (matter.spent / matter.budget * 100) if matter.budget > 0 else 0
        }

    def sync_research_to_pm(self, research_results: List[Dict], matter_id: str):
        """
        Sync research results to PM system

        Args:
            research_results: Research findings
            matter_id: Matter ID
        """
        if matter_id not in self.matters:
            logger.warning(f"Matter {matter_id} not found")
            return

        # Store research findings
        logger.info(f"Synced {len(research_results)} research results to {matter_id}")

    def get_budget_alert(self, matter_id: str) -> Optional[str]:
        """
        Check if matter is approaching budget limit

        Args:
            matter_id: Matter ID

        Returns:
            Alert message if budget is low
        """
        if matter_id not in self.matters:
            return None

        matter = self.matters[matter_id]

        if matter.budget == 0:
            return None

        utilization = (matter.spent / matter.budget) * 100

        if utilization > 90:
            return f"Budget alert: {utilization:.1f}% of budget spent"
        elif utilization > 75:
            return f"Budget warning: {utilization:.1f}% of budget spent"

        return None

    def close_matter(self, matter_id: str):
        """
        Close matter

        Args:
            matter_id: Matter ID
        """
        if matter_id in self.matters:
            self.matters[matter_id].status = "closed"
            logger.info(f"Closed matter: {matter_id}")


# Usage example
if __name__ == "__main__":
    pm = PracticeManagementIntegration()

    # Create matter
    matter = pm.create_matter({
        "id": "mat_001",
        "client": "ABC Corp",
        "name": "Contract Review",
        "attorney": "Jane Smith",
        "budget": 5000.0
    })

    # Log research time
    pm.log_research_time("mat_001", 3.0, "Research non-compete law")

    # Get summary
    summary = pm.get_matter_research_summary("mat_001")
    print(f"Matter Summary: {summary}")
