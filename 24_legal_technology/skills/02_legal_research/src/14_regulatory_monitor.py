"""
Regulatory Monitor
Tracks regulatory changes and compliance requirements
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RegulatoryChange:
    """A regulatory change or update"""
    change_id: str
    title: str
    regulation: str
    jurisdiction: str
    effective_date: str
    change_type: str  # new, amended, repealed
    impact_area: str
    description: str
    affected_entities: List[str]


class RegulatoryMonitor:
    """
    Monitors regulatory changes and updates
    """

    def __init__(self):
        """Initialize regulatory monitor"""
        self.changes = []
        self.subscriptions = {}
        self.alert_history = []

    def add_regulatory_change(self, change: Dict) -> RegulatoryChange:
        """
        Add regulatory change to monitor

        Args:
            change: Dictionary with change details

        Returns:
            RegulatoryChange object
        """
        reg_change = RegulatoryChange(
            change_id=change.get("id", f"change_{len(self.changes)}"),
            title=change.get("title", ""),
            regulation=change.get("regulation", ""),
            jurisdiction=change.get("jurisdiction", ""),
            effective_date=change.get("effective_date", ""),
            change_type=change.get("type", "amended"),
            impact_area=change.get("impact_area", ""),
            description=change.get("description", ""),
            affected_entities=change.get("affected_entities", [])
        )

        self.changes.append(reg_change)
        logger.info(f"Added regulatory change: {reg_change.title}")
        return reg_change

    def subscribe_to_changes(self, entity: str, impact_areas: List[str]):
        """
        Subscribe entity to regulatory change alerts

        Args:
            entity: Entity name
            impact_areas: Areas of interest
        """
        self.subscriptions[entity] = impact_areas
        logger.info(f"Subscribed {entity} to changes in: {', '.join(impact_areas)}")

    def get_relevant_changes(self, entity: str) -> List[RegulatoryChange]:
        """
        Get relevant changes for subscribed entity

        Args:
            entity: Entity name

        Returns:
            List of relevant changes
        """
        if entity not in self.subscriptions:
            return []

        areas = self.subscriptions[entity]
        relevant = [c for c in self.changes if c.impact_area in areas]

        return relevant

    def generate_compliance_report(self, entity: str) -> Dict:
        """
        Generate compliance report for entity

        Args:
            entity: Entity name

        Returns:
            Compliance report dictionary
        """
        relevant_changes = self.get_relevant_changes(entity)

        if not relevant_changes:
            return {"entity": entity, "status": "compliant", "changes": []}

        report = {
            "entity": entity,
            "report_date": datetime.now().isoformat(),
            "total_changes": len(relevant_changes),
            "changes": []
        }

        for change in relevant_changes:
            report["changes"].append({
                "title": change.title,
                "regulation": change.regulation,
                "effective_date": change.effective_date,
                "change_type": change.change_type,
                "impact_area": change.impact_area,
                "action_items": self._generate_action_items(change)
            })

        return report

    @staticmethod
    def _generate_action_items(change: RegulatoryChange) -> List[str]:
        """Generate action items for regulatory change"""
        actions = []

        if change.change_type == "new":
            actions.append("Review new requirements")
            actions.append("Assess compliance status")
            actions.append("Update policies and procedures")
        elif change.change_type == "amended":
            actions.append("Review amendments")
            actions.append("Compare to current practices")
            actions.append("Update affected documents")
        elif change.change_type == "repealed":
            actions.append("Remove from compliance framework")
            actions.append("Update documentation")

        actions.append(f"Ensure compliance by {change.effective_date}")
        return actions

    def search_changes(self, query: str) -> List[RegulatoryChange]:
        """
        Search regulatory changes

        Args:
            query: Search query

        Returns:
            List of matching changes
        """
        results = []
        query_lower = query.lower()

        for change in self.changes:
            if (query_lower in change.title.lower() or
                query_lower in change.regulation.lower() or
                query_lower in change.description.lower()):
                results.append(change)

        return results

    def get_deadline_summary(self) -> List[Dict]:
        """
        Get summary of upcoming compliance deadlines

        Returns:
            List of upcoming deadlines
        """
        deadlines = []

        for change in self.changes:
            deadlines.append({
                "regulation": change.regulation,
                "effective_date": change.effective_date,
                "title": change.title,
                "days_until": self._calculate_days_until(change.effective_date)
            })

        # Sort by effective date
        deadlines.sort(key=lambda x: x["effective_date"])
        return deadlines

    @staticmethod
    def _calculate_days_until(date_str: str) -> int:
        """Calculate days until date"""
        try:
            target_date = datetime.fromisoformat(date_str)
            days = (target_date - datetime.now()).days
            return max(0, days)
        except:
            return -1


# Usage example
if __name__ == "__main__":
    monitor = RegulatoryMonitor()

    # Add regulatory changes
    monitor.add_regulatory_change({
        "id": "change_001",
        "title": "Updated Data Privacy Requirements",
        "regulation": "CCPA Amendment",
        "jurisdiction": "California",
        "effective_date": "2024-01-01",
        "type": "amended",
        "impact_area": "data_privacy",
        "description": "New requirements for data handling",
        "affected_entities": ["Tech Companies", "Financial Services"]
    })

    # Subscribe entity
    monitor.subscribe_to_changes("TechCorp", ["data_privacy"])

    # Get compliance report
    report = monitor.generate_compliance_report("TechCorp")
    print(f"Compliance Report: {report}")
