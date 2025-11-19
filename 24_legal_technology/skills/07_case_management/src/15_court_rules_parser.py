"""
Court Rules Parser - Practice Management Automation

Parses court rules and deadlines, tracks rule changes,
and generates compliance checklists for case filings.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum


class RuleCategory(Enum):
    """Categories of court rules"""
    FILING_REQUIREMENTS = "filing_requirements"
    DEADLINES = "deadlines"
    DISCOVERY = "discovery"
    MOTION = "motion"
    TRIAL = "trial"
    APPEAL = "appeal"
    DOCUMENTATION = "documentation"


class RuleJurisdiction(Enum):
    """Court jurisdictions"""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    APPELLATE = "appellate"


@dataclass
class CourtRule:
    """Represents a court rule or requirement"""
    rule_id: str
    rule_number: str
    title: str
    category: RuleCategory
    jurisdiction: RuleJurisdiction
    description: str
    requirements: List[str]
    related_rules: List[str] = field(default_factory=list)
    effective_date: datetime = field(default_factory=datetime.now)
    url: Optional[str] = None


@dataclass
class Deadline:
    """Court deadline for case activity"""
    deadline_id: str
    matter_id: str
    activity: str
    due_date: datetime
    rule_reference: str
    priority: int  # 1-5, 5 being highest
    assigned_to: str
    status: str = "pending"
    notes: str = ""
    reminder_sent: bool = False


@dataclass
class ComplianceChecklistItem:
    """Item on compliance checklist"""
    item_id: str
    task: str
    rule_reference: str
    deadline: datetime
    responsible_party: str
    completed: bool = False
    completion_date: Optional[datetime] = None
    notes: str = ""


class CourtRulesParser:
    """Parses and manages court rules and deadlines"""

    def __init__(self):
        self.rules: Dict[str, CourtRule] = {}
        self.deadlines: List[Deadline] = []
        self.checklists: Dict[str, List[ComplianceChecklistItem]] = {}

    def add_rule(self, rule: CourtRule) -> None:
        """Add a court rule to the system"""
        self.rules[rule.rule_id] = rule

    def add_deadline(self, deadline: Deadline) -> None:
        """Add a court deadline"""
        self.deadlines.append(deadline)

    def get_rules_by_category(self, category: RuleCategory) -> List[CourtRule]:
        """Get rules by category"""
        return [r for r in self.rules.values() if r.category == category]

    def get_rules_by_jurisdiction(self, jurisdiction: RuleJurisdiction) -> List[CourtRule]:
        """Get rules for a jurisdiction"""
        return [r for r in self.rules.values() if r.jurisdiction == jurisdiction]

    def get_deadlines_for_matter(self, matter_id: str) -> List[Deadline]:
        """Get all deadlines for a matter"""
        return [d for d in self.deadlines if d.matter_id == matter_id]

    def get_upcoming_deadlines(self, matter_id: str, days_ahead: int = 30) -> List[Deadline]:
        """Get deadlines coming up within specified days"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        matter_deadlines = self.get_deadlines_for_matter(matter_id)

        return [d for d in matter_deadlines
                if d.due_date <= cutoff_date and d.status == "pending"]

    def get_overdue_deadlines(self, matter_id: str) -> List[Deadline]:
        """Get overdue deadlines"""
        matter_deadlines = self.get_deadlines_for_matter(matter_id)
        return [d for d in matter_deadlines if d.due_date < datetime.now() and d.status == "pending"]

    def calculate_deadline(self, activity: str, jurisdiction: RuleJurisdiction,
                          matter_id: str, trigger_date: datetime) -> Optional[Deadline]:
        """Calculate deadline based on rule and trigger date"""
        # Find relevant rules
        relevant_rules = [r for r in self.get_rules_by_jurisdiction(jurisdiction)
                         if activity.lower() in r.description.lower()]

        if not relevant_rules:
            return None

        rule = relevant_rules[0]
        # Extract days from rule description (simplified)
        days_allowed = self._extract_days_from_rule(rule)

        if days_allowed:
            due_date = trigger_date + timedelta(days=days_allowed)
            deadline = Deadline(
                deadline_id=f"DL-{matter_id}-{activity[:3]}-{datetime.now().strftime('%Y%m%d')}",
                matter_id=matter_id,
                activity=activity,
                due_date=due_date,
                rule_reference=rule.rule_id,
                priority=4,
                assigned_to=""
            )
            return deadline

        return None

    def _extract_days_from_rule(self, rule: CourtRule) -> Optional[int]:
        """Extract number of days from rule description"""
        # Simplified extraction - in production would be more sophisticated
        import re
        match = re.search(r'(\d+)\s*days?', rule.description, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def create_compliance_checklist(self, matter_id: str, case_type: str) -> str:
        """Generate compliance checklist for a matter"""
        checklist_id = f"CL-{matter_id}-{datetime.now().strftime('%Y%m%d')}"
        items = []

        # Create standard checklist items based on case type
        standard_tasks = self._get_standard_tasks(case_type)

        for i, task in enumerate(standard_tasks, 1):
            item = ComplianceChecklistItem(
                item_id=f"{checklist_id}-{i}",
                task=task["description"],
                rule_reference=task.get("rule", ""),
                deadline=datetime.now() + timedelta(days=task.get("days", 30)),
                responsible_party="",
                notes=task.get("notes", "")
            )
            items.append(item)

        self.checklists[checklist_id] = items
        return checklist_id

    def _get_standard_tasks(self, case_type: str) -> List[Dict]:
        """Get standard tasks for case type"""
        tasks = {
            "civil": [
                {"description": "File complaint", "rule": "RULE-1", "days": 0, "notes": "Initial filing"},
                {"description": "Serve defendant", "rule": "RULE-2", "days": 30, "notes": "Within 90 days"},
                {"description": "Answer due from defendant", "rule": "RULE-3", "days": 50, "notes": "21 days from service"},
                {"description": "Initial disclosures", "rule": "RULE-4", "days": 50, "notes": "26(a) disclosures"},
                {"description": "Case management conference", "rule": "RULE-5", "days": 120},
            ],
            "criminal": [
                {"description": "First appearance", "rule": "RULE-C1", "days": 1},
                {"description": "Bail hearing", "rule": "RULE-C2", "days": 3},
                {"description": "Preliminary hearing", "rule": "RULE-C3", "days": 14},
                {"description": "Grand jury indictment", "rule": "RULE-C4", "days": 30},
                {"description": "Arraignment", "rule": "RULE-C5", "days": 60},
            ]
        }
        return tasks.get(case_type.lower(), [])

    def get_checklist_progress(self, checklist_id: str) -> Dict:
        """Get progress on compliance checklist"""
        if checklist_id not in self.checklists:
            return {}

        items = self.checklists[checklist_id]
        completed = len([i for i in items if i.completed])

        return {
            "checklist_id": checklist_id,
            "total_items": len(items),
            "completed_items": completed,
            "progress_percent": (completed / len(items) * 100) if items else 0,
            "overdue_items": len([i for i in items if i.deadline < datetime.now() and not i.completed])
        }

    def mark_task_complete(self, checklist_id: str, item_id: str) -> bool:
        """Mark a checklist item as complete"""
        if checklist_id not in self.checklists:
            return False

        for item in self.checklists[checklist_id]:
            if item.item_id == item_id:
                item.completed = True
                item.completion_date = datetime.now()
                return True

        return False


# Example usage
if __name__ == "__main__":
    parser = CourtRulesParser()

    # Add a rule
    rule = CourtRule(
        rule_id="RULE-1",
        rule_number="8(a)",
        title="Complaint Requirements",
        category=RuleCategory.FILING_REQUIREMENTS,
        jurisdiction=RuleJurisdiction.FEDERAL,
        description="A complaint must contain a short and plain statement of the grounds for jurisdiction, claims, and relief sought. 20 days to respond.",
        requirements=["Caption", "Statement of jurisdiction", "Claims for relief", "Prayer for relief"]
    )
    parser.add_rule(rule)

    # Create checklist
    checklist_id = parser.create_compliance_checklist("MAT-2024-001", "civil")

    # Get progress
    progress = parser.get_checklist_progress(checklist_id)
    print(f"Checklist Progress: {progress}")
