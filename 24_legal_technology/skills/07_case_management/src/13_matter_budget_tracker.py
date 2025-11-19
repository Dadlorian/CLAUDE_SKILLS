"""
Matter Budget Tracker - Practice Management Automation

Tracks budgets for legal matters, monitors spending vs. budget,
and provides alerts when matters exceed budget thresholds.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from decimal import Decimal
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class BudgetAlert:
    """Alert for budget threshold exceeded"""
    matter_id: str
    alert_level: AlertLevel
    message: str
    percentage_used: Decimal
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BudgetExpense:
    """Individual expense against matter budget"""
    expense_id: str
    matter_id: str
    category: str
    amount: Decimal
    description: str
    date: datetime
    attorney_id: str


@dataclass
class MatterBudget:
    """Budget for a legal matter"""
    matter_id: str
    client_id: str
    total_budget: Decimal
    created_date: datetime
    expected_completion: Optional[datetime] = None
    expenses: List[BudgetExpense] = field(default_factory=list)
    alerts: List[BudgetAlert] = field(default_factory=list)

    def add_expense(self, expense: BudgetExpense) -> None:
        """Add expense to budget"""
        self.expenses.append(expense)

    def get_total_expenses(self) -> Decimal:
        """Calculate total expenses"""
        return sum(e.amount for e in self.expenses)

    def get_remaining_budget(self) -> Decimal:
        """Calculate remaining budget"""
        return self.total_budget - self.get_total_expenses()

    def get_budget_percentage_used(self) -> Decimal:
        """Calculate percentage of budget used"""
        if self.total_budget == 0:
            return Decimal(0)
        return (self.get_total_expenses() / self.total_budget) * 100

    def get_expenses_by_category(self) -> Dict[str, Decimal]:
        """Get expenses grouped by category"""
        categories = {}
        for expense in self.expenses:
            if expense.category not in categories:
                categories[expense.category] = Decimal(0)
            categories[expense.category] += expense.amount
        return categories


class MatterBudgetTracker:
    """Tracks and monitors budgets for matters"""

    def __init__(self, warning_threshold: Decimal = Decimal(75), critical_threshold: Decimal = Decimal(90)):
        self.budgets: Dict[str, MatterBudget] = {}
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def create_budget(self, matter_budget: MatterBudget) -> None:
        """Create a new budget for a matter"""
        self.budgets[matter_budget.matter_id] = matter_budget

    def add_expense(self, matter_id: str, expense: BudgetExpense) -> None:
        """Add expense to a matter's budget"""
        if matter_id not in self.budgets:
            raise ValueError(f"Matter {matter_id} not found")

        budget = self.budgets[matter_id]
        budget.add_expense(expense)
        self._check_budget_alerts(matter_id)

    def _check_budget_alerts(self, matter_id: str) -> None:
        """Check if budget thresholds are exceeded"""
        budget = self.budgets[matter_id]
        percentage_used = budget.get_budget_percentage_used()

        # Clear old alerts
        budget.alerts = []

        if percentage_used >= self.critical_threshold:
            alert = BudgetAlert(
                matter_id=matter_id,
                alert_level=AlertLevel.CRITICAL,
                message=f"Matter {matter_id} has exceeded {self.critical_threshold}% of budget",
                percentage_used=percentage_used
            )
            budget.alerts.append(alert)

        elif percentage_used >= self.warning_threshold:
            alert = BudgetAlert(
                matter_id=matter_id,
                alert_level=AlertLevel.WARNING,
                message=f"Matter {matter_id} is approaching budget limit ({percentage_used:.1f}% used)",
                percentage_used=percentage_used
            )
            budget.alerts.append(alert)

    def get_budget_status(self, matter_id: str) -> Dict:
        """Get comprehensive budget status for a matter"""
        if matter_id not in self.budgets:
            return {}

        budget = self.budgets[matter_id]
        return {
            "matter_id": matter_id,
            "total_budget": str(budget.total_budget),
            "total_expenses": str(budget.get_total_expenses()),
            "remaining_budget": str(budget.get_remaining_budget()),
            "percentage_used": str(budget.get_budget_percentage_used()),
            "expense_count": len(budget.expenses),
            "alerts": [
                {
                    "level": a.alert_level.value,
                    "message": a.message,
                    "percentage_used": str(a.percentage_used)
                } for a in budget.alerts
            ]
        }

    def get_expenses_by_category(self, matter_id: str) -> Dict[str, str]:
        """Get expenses by category for a matter"""
        if matter_id not in self.budgets:
            return {}

        expenses = self.budgets[matter_id].get_expenses_by_category()
        return {cat: str(amount) for cat, amount in expenses.items()}

    def get_overbudget_matters(self) -> List[str]:
        """Get list of matters that exceed budget"""
        overbudget = []
        for matter_id, budget in self.budgets.items():
            if budget.get_remaining_budget() < 0:
                overbudget.append(matter_id)
        return overbudget

    def get_matters_with_alerts(self) -> List[str]:
        """Get matters that have active alerts"""
        return [matter_id for matter_id, budget in self.budgets.items() if budget.alerts]

    def project_completion_cost(self, matter_id: str, days_remaining: int) -> Decimal:
        """Project completion cost based on current burn rate"""
        if matter_id not in self.budgets:
            return Decimal(0)

        budget = self.budgets[matter_id]
        if not budget.expenses or not budget.created_date:
            return budget.get_total_expenses()

        days_elapsed = (datetime.now() - budget.created_date).days
        if days_elapsed == 0:
            return budget.get_total_expenses()

        daily_burn_rate = budget.get_total_expenses() / days_elapsed
        projected_total = budget.get_total_expenses() + (daily_burn_rate * days_remaining)

        return projected_total

    def generate_budget_report(self, matter_id: str) -> Dict:
        """Generate detailed budget report for a matter"""
        if matter_id not in self.budgets:
            return {}

        budget = self.budgets[matter_id]

        return {
            "matter_id": matter_id,
            "client_id": budget.client_id,
            "total_budget": str(budget.total_budget),
            "total_expenses": str(budget.get_total_expenses()),
            "remaining_budget": str(budget.get_remaining_budget()),
            "percentage_used": f"{budget.get_budget_percentage_used():.1f}%",
            "expenses_by_category": self.get_expenses_by_category(matter_id),
            "transaction_count": len(budget.expenses),
            "alerts": [
                {
                    "level": a.alert_level.value,
                    "message": a.message
                } for a in budget.alerts
            ]
        }


# Example usage
if __name__ == "__main__":
    tracker = MatterBudgetTracker(warning_threshold=Decimal(75))

    budget = MatterBudget(
        matter_id="MAT-2024-001",
        client_id="CLI-001",
        total_budget=Decimal(50000),
        created_date=datetime(2024, 1, 1)
    )
    tracker.create_budget(budget)

    expense = BudgetExpense(
        expense_id="EXP-001",
        matter_id="MAT-2024-001",
        category="attorney_time",
        amount=Decimal(35000),
        description="Attorney time and services",
        date=datetime.now(),
        attorney_id="ATT-001"
    )
    tracker.add_expense("MAT-2024-001", expense)

    status = tracker.get_budget_status("MAT-2024-001")
    print(f"Budget Status: {status}")
