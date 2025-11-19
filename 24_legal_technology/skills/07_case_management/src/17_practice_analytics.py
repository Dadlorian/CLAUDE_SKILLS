"""
Practice Analytics - Practice Management Automation

Provides analytics and insights into practice performance,
matter profitability, attorney productivity, and case outcomes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from enum import Enum


class MetricType(Enum):
    """Types of practice metrics"""
    REVENUE = "revenue"
    PROFITABILITY = "profitability"
    UTILIZATION = "utilization"
    MATTER_SUCCESS_RATE = "matter_success_rate"
    CLIENT_SATISFACTION = "client_satisfaction"
    ATTORNEY_PRODUCTIVITY = "attorney_productivity"
    BILLING_REALIZATION = "billing_realization"


@dataclass
class ProfitabilityMetrics:
    """Profitability metrics for a matter or attorney"""
    entity_id: str
    entity_type: str  # "matter" or "attorney"
    gross_revenue: Decimal
    costs: Decimal
    profit: Decimal
    profit_margin: Decimal
    period: str


@dataclass
class UtilizationMetrics:
    """Attorney utilization metrics"""
    attorney_id: str
    billable_hours: Decimal
    total_hours: Decimal
    utilization_rate: Decimal  # Percentage
    target_utilization: Decimal
    variance: Decimal


@dataclass
class MatterOutcome:
    """Outcome of a completed matter"""
    matter_id: str
    client_id: str
    matter_type: str
    opening_date: datetime
    closing_date: datetime
    outcome: str  # "won", "settled", "dismissed", "lost"
    settlement_amount: Optional[Decimal] = None
    judgment_amount: Optional[Decimal] = None
    fees_earned: Decimal = Decimal(0)
    costs_incurred: Decimal = Decimal(0)


@dataclass
class ClientMetrics:
    """Metrics related to client"""
    client_id: str
    client_name: str
    total_matters: int
    matters_open: int
    matters_closed: int
    total_fees_paid: Decimal
    average_matter_value: Decimal
    satisfaction_rating: Decimal = Decimal(5)
    retention_risk: str = "low"  # "low", "medium", "high"


class PracticeAnalytics:
    """Analytics engine for legal practice"""

    def __init__(self):
        self.matters: Dict[str, Dict] = {}
        self.attorney_data: Dict[str, Dict] = {}
        self.client_data: Dict[str, ClientMetrics] = {}
        self.outcomes: List[MatterOutcome] = []

    def add_matter_data(self, matter_id: str, matter_data: Dict) -> None:
        """Add matter data for analytics"""
        self.matters[matter_id] = matter_data

    def add_attorney_data(self, attorney_id: str, attorney_data: Dict) -> None:
        """Add attorney data for analytics"""
        self.attorney_data[attorney_id] = attorney_data

    def add_client_metrics(self, metrics: ClientMetrics) -> None:
        """Add client metrics"""
        self.client_data[metrics.client_id] = metrics

    def record_matter_outcome(self, outcome: MatterOutcome) -> None:
        """Record outcome of completed matter"""
        self.outcomes.append(outcome)

    def calculate_matter_profitability(self, matter_id: str) -> ProfitabilityMetrics:
        """Calculate profitability metrics for a matter"""
        if matter_id not in self.matters:
            return None

        matter = self.matters[matter_id]
        gross_revenue = Decimal(str(matter.get("revenue", 0)))
        costs = Decimal(str(matter.get("costs", 0)))
        profit = gross_revenue - costs

        profit_margin = Decimal(0)
        if gross_revenue > 0:
            profit_margin = (profit / gross_revenue) * 100

        return ProfitabilityMetrics(
            entity_id=matter_id,
            entity_type="matter",
            gross_revenue=gross_revenue,
            costs=costs,
            profit=profit,
            profit_margin=profit_margin,
            period=matter.get("period", "2024-Q1")
        )

    def calculate_attorney_utilization(self, attorney_id: str, period_days: int = 90) -> UtilizationMetrics:
        """Calculate attorney utilization rate"""
        if attorney_id not in self.attorney_data:
            return None

        attorney = self.attorney_data[attorney_id]
        billable_hours = Decimal(str(attorney.get("billable_hours", 0)))
        total_hours = Decimal(str(attorney.get("total_hours", 2080)))  # ~40 hrs/week

        utilization_rate = Decimal(0)
        if total_hours > 0:
            utilization_rate = (billable_hours / total_hours) * 100

        target_utilization = Decimal(80)
        variance = utilization_rate - target_utilization

        return UtilizationMetrics(
            attorney_id=attorney_id,
            billable_hours=billable_hours,
            total_hours=total_hours,
            utilization_rate=utilization_rate,
            target_utilization=target_utilization,
            variance=variance
        )

    def get_matter_success_rate(self, attorney_id: Optional[str] = None) -> float:
        """Get matter success rate (won/settled vs. lost)"""
        outcomes = self.outcomes
        if attorney_id:
            outcomes = [o for o in outcomes if o.matter_id in self.matters and
                       self.matters[o.matter_id].get("assigned_attorney") == attorney_id]

        if not outcomes:
            return 0.0

        successful = len([o for o in outcomes if o.outcome in ["won", "settled"]])
        return (successful / len(outcomes)) * 100

    def get_top_performing_attorneys(self, metric: str = "profitability", limit: int = 5) -> List[Dict]:
        """Get top performing attorneys by metric"""
        attorney_metrics = []

        for attorney_id in self.attorney_data.keys():
            if metric == "utilization":
                util = self.calculate_attorney_utilization(attorney_id)
                if util:
                    attorney_metrics.append({
                        "attorney_id": attorney_id,
                        "metric": f"{util.utilization_rate:.1f}%",
                        "score": float(util.utilization_rate)
                    })
            elif metric == "success_rate":
                success_rate = self.get_matter_success_rate(attorney_id)
                attorney_metrics.append({
                    "attorney_id": attorney_id,
                    "metric": f"{success_rate:.1f}%",
                    "score": success_rate
                })

        # Sort by score descending
        attorney_metrics.sort(key=lambda x: x["score"], reverse=True)
        return attorney_metrics[:limit]

    def get_most_profitable_matters(self, limit: int = 10) -> List[Dict]:
        """Get most profitable matters"""
        profitability = []

        for matter_id in self.matters.keys():
            metrics = self.calculate_matter_profitability(matter_id)
            if metrics:
                profitability.append({
                    "matter_id": matter_id,
                    "profit": str(metrics.profit),
                    "margin": f"{metrics.profit_margin:.1f}%",
                    "revenue": str(metrics.gross_revenue)
                })

        # Sort by profit descending
        profitability.sort(key=lambda x: float(x["profit"]), reverse=True)
        return profitability[:limit]

    def get_client_value_analysis(self, limit: int = 10) -> List[Dict]:
        """Get analysis of client value"""
        client_values = []

        for client_id, metrics in self.client_data.items():
            client_values.append({
                "client_id": client_id,
                "client_name": metrics.client_name,
                "total_matters": metrics.total_matters,
                "total_fees": str(metrics.total_fees_paid),
                "average_matter_value": str(metrics.average_matter_value),
                "satisfaction": f"{metrics.satisfaction_rating}/5",
                "retention_risk": metrics.retention_risk
            })

        # Sort by total fees descending
        client_values.sort(key=lambda x: float(x["total_fees"]), reverse=True)
        return client_values[:limit]

    def get_practice_dashboard(self) -> Dict:
        """Get comprehensive practice dashboard"""
        total_revenue = sum(
            Decimal(str(m.get("revenue", 0))) for m in self.matters.values()
        )
        total_costs = sum(
            Decimal(str(m.get("costs", 0))) for m in self.matters.values()
        )
        total_profit = total_revenue - total_costs

        return {
            "total_revenue": str(total_revenue),
            "total_costs": str(total_costs),
            "total_profit": str(total_profit),
            "profit_margin": f"{(total_profit/total_revenue*100):.1f}%" if total_revenue > 0 else "0%",
            "total_matters": len(self.matters),
            "total_attorneys": len(self.attorney_data),
            "total_clients": len(self.client_data),
            "average_matter_success_rate": f"{self.get_matter_success_rate():.1f}%",
            "top_attorneys": self.get_top_performing_attorneys("profitability", 3),
            "top_clients": self.get_client_value_analysis(3),
            "dashboard_generated": datetime.now().isoformat()
        }

    def generate_monthly_report(self, month: int, year: int) -> Dict:
        """Generate monthly performance report"""
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, 28)  # Simplified for example

        relevant_outcomes = [
            o for o in self.outcomes
            if start_date <= o.closing_date <= end_date
        ]

        total_fees = sum(o.fees_earned for o in relevant_outcomes)
        total_costs = sum(o.costs_incurred for o in relevant_outcomes)

        return {
            "period": f"{year}-{month:02d}",
            "matters_closed": len(relevant_outcomes),
            "total_fees_earned": str(total_fees),
            "total_costs": str(total_costs),
            "net_profit": str(total_fees - total_costs),
            "success_rate": f"{(len([o for o in relevant_outcomes if o.outcome in ['won', 'settled']]) / len(relevant_outcomes) * 100):.1f}%" if relevant_outcomes else "0%",
            "average_matter_value": str(total_fees / len(relevant_outcomes)) if relevant_outcomes else "0"
        }


# Example usage
if __name__ == "__main__":
    analytics = PracticeAnalytics()

    # Add sample data
    analytics.add_matter_data("MAT-2024-001", {
        "revenue": 25000,
        "costs": 8000,
        "period": "2024-Q1",
        "assigned_attorney": "ATT-001"
    })

    analytics.add_attorney_data("ATT-001", {
        "billable_hours": 1800,
        "total_hours": 2080,
        "name": "Jane Smith"
    })

    # Add client metrics
    client_metrics = ClientMetrics(
        client_id="CLI-001",
        client_name="Acme Corp",
        total_matters=3,
        matters_open=1,
        matters_closed=2,
        total_fees_paid=Decimal(75000),
        average_matter_value=Decimal(25000)
    )
    analytics.add_client_metrics(client_metrics)

    # Get dashboard
    dashboard = analytics.get_practice_dashboard()
    print(f"Practice Dashboard: {dashboard}")
