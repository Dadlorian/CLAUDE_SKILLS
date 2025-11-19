"""
Regulatory Dashboard - Comprehensive dashboard for government relations monitoring.
Aggregates data from multiple sources for unified regulatory intelligence.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DashboardWidget:
    """Represents a dashboard widget."""
    widget_id: str
    widget_type: str
    title: str
    data: Dict
    last_updated: datetime
    refresh_interval: int  # minutes


@dataclass
class DashboardAlert:
    """Represents a dashboard alert."""
    alert_id: str
    severity: str  # "critical", "warning", "info"
    title: str
    message: str
    source: str  # "foia", "legislation", "pac", etc.
    created_at: datetime
    action_required: bool
    action_url: Optional[str] = None


class RegulatoryDashboard:
    """Comprehensive dashboard for government relations monitoring."""

    def __init__(self, organization_name: str):
        """Initialize regulatory dashboard."""
        self.organization_name = organization_name
        self.widgets: Dict[str, DashboardWidget] = {}
        self.alerts: List[DashboardAlert] = []
        self.created_date = datetime.now()
        self.last_refresh = None

    def add_widget(
        self,
        widget_type: str,
        title: str,
        data: Dict,
        refresh_interval: int = 60
    ) -> DashboardWidget:
        """Add a widget to the dashboard."""
        widget_id = f"widget_{len(self.widgets) + 1}"

        widget = DashboardWidget(
            widget_id=widget_id,
            widget_type=widget_type,
            title=title,
            data=data,
            last_updated=datetime.now(),
            refresh_interval=refresh_interval
        )

        self.widgets[widget_id] = widget
        logger.info(f"Added widget: {title}")
        return widget

    def update_widget(self, widget_id: str, data: Dict) -> bool:
        """Update widget data."""
        if widget_id not in self.widgets:
            return False

        widget = self.widgets[widget_id]
        widget.data = data
        widget.last_updated = datetime.now()
        return True

    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget from dashboard."""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            return True
        return False

    def add_alert(
        self,
        severity: str,
        title: str,
        message: str,
        source: str,
        action_required: bool = False,
        action_url: str = None
    ) -> DashboardAlert:
        """Add an alert to the dashboard."""
        alert_id = f"alert_{datetime.now().timestamp()}"

        alert = DashboardAlert(
            alert_id=alert_id,
            severity=severity,
            title=title,
            message=message,
            source=source,
            created_at=datetime.now(),
            action_required=action_required,
            action_url=action_url
        )

        self.alerts.append(alert)
        logger.info(f"Added {severity} alert: {title}")
        return alert

    def get_critical_alerts(self) -> List[DashboardAlert]:
        """Get all critical alerts."""
        return [a for a in self.alerts if a.severity == "critical"]

    def get_action_required_alerts(self) -> List[DashboardAlert]:
        """Get alerts requiring action."""
        return [a for a in self.alerts if a.action_required]

    def clear_alert(self, alert_id: str) -> bool:
        """Clear/dismiss an alert."""
        for i, alert in enumerate(self.alerts):
            if alert.alert_id == alert_id:
                self.alerts.pop(i)
                return True
        return False

    def clear_old_alerts(self, days: int = 7) -> int:
        """Clear alerts older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.alerts)

        self.alerts = [
            a for a in self.alerts
            if a.created_at > cutoff_date
        ]

        removed = original_count - len(self.alerts)
        logger.info(f"Cleared {removed} old alerts")
        return removed

    def get_summary(self) -> Dict:
        """Get dashboard summary."""
        critical_count = len(self.get_critical_alerts())
        warning_count = len([a for a in self.alerts if a.severity == "warning"])
        info_count = len([a for a in self.alerts if a.severity == "info"])
        action_count = len(self.get_action_required_alerts())

        return {
            "organization": self.organization_name,
            "created_date": self.created_date.isoformat(),
            "last_refresh": self.last_refresh.isoformat() if self.last_refresh else None,
            "widgets": {
                "total": len(self.widgets),
                "by_type": self._group_widgets_by_type()
            },
            "alerts": {
                "total": len(self.alerts),
                "critical": critical_count,
                "warning": warning_count,
                "info": info_count,
                "action_required": action_count
            }
        }

    def _group_widgets_by_type(self) -> Dict[str, int]:
        """Group widgets by type."""
        grouped = {}
        for widget in self.widgets.values():
            grouped[widget.widget_type] = grouped.get(widget.widget_type, 0) + 1
        return grouped

    def create_legislation_widget(
        self,
        tracked_bills: List[Dict]
    ) -> DashboardWidget:
        """Create a legislation monitoring widget."""
        total_bills = len(tracked_bills)
        active_bills = len([b for b in tracked_bills if b.get("status") == "active"])
        votes_scheduled = len([b for b in tracked_bills if b.get("vote_scheduled")])

        data = {
            "total_tracked": total_bills,
            "active": active_bills,
            "votes_scheduled": votes_scheduled,
            "bills": tracked_bills[:10]  # Top 10 for display
        }

        return self.add_widget(
            widget_type="legislation_tracker",
            title="Tracked Legislation",
            data=data,
            refresh_interval=60
        )

    def create_regulatory_widget(
        self,
        fed_register_items: List[Dict],
        days_remaining: Dict
    ) -> DashboardWidget:
        """Create a regulatory monitoring widget."""
        data = {
            "total_items": len(fed_register_items),
            "comment_periods_closing_soon": days_remaining.get("closing_soon", 0),
            "recent_items": fed_register_items[:5],
            "deadline_summary": days_remaining
        }

        return self.add_widget(
            widget_type="regulatory_monitor",
            title="Federal Register Monitor",
            data=data,
            refresh_interval=120
        )

    def create_grassroots_widget(
        self,
        volunteer_count: int,
        actions_completed: int,
        impact_score: int
    ) -> DashboardWidget:
        """Create a grassroots engagement widget."""
        data = {
            "volunteer_count": volunteer_count,
            "actions_completed": actions_completed,
            "impact_score": impact_score,
            "engagement_rate": (actions_completed / (volunteer_count * 5)) * 100
            if volunteer_count > 0 else 0
        }

        return self.add_widget(
            widget_type="grassroots_engagement",
            title="Grassroots Campaign",
            data=data,
            refresh_interval=30
        )

    def create_pac_widget(
        self,
        total_raised: float,
        total_spent: float,
        cash_on_hand: float
    ) -> DashboardWidget:
        """Create a PAC compliance widget."""
        data = {
            "total_raised": total_raised,
            "total_spent": total_spent,
            "cash_on_hand": cash_on_hand,
            "burn_rate": (total_spent / total_raised * 100) if total_raised > 0 else 0
        }

        return self.add_widget(
            widget_type="pac_compliance",
            title="PAC Financial Status",
            data=data,
            refresh_interval=1440  # Daily
        )

    def create_coalition_widget(
        self,
        coalition_name: str,
        member_count: int,
        active_campaigns: int,
        alignment_score: float
    ) -> DashboardWidget:
        """Create a coalition tracking widget."""
        data = {
            "coalition_name": coalition_name,
            "member_count": member_count,
            "active_campaigns": active_campaigns,
            "alignment_score": alignment_score
        }

        return self.add_widget(
            widget_type="coalition_tracker",
            title=f"Coalition: {coalition_name}",
            data=data,
            refresh_interval=240
        )

    def create_foia_widget(
        self,
        pending_requests: int,
        days_to_deadline: List[int],
        responses_received: int
    ) -> DashboardWidget:
        """Create a FOIA tracking widget."""
        data = {
            "pending_requests": pending_requests,
            "urgent_deadlines": len([d for d in days_to_deadline if d <= 5]),
            "responses_received": responses_received,
            "average_days_to_response": sum(days_to_deadline) / len(days_to_deadline)
            if days_to_deadline else 0
        }

        return self.add_widget(
            widget_type="foia_tracker",
            title="FOIA Requests",
            data=data,
            refresh_interval=240
        )

    def create_policy_widget(
        self,
        active_initiatives: int,
        initiatives_at_risk: int,
        success_rate: float,
        top_priority_items: List[str]
    ) -> DashboardWidget:
        """Create a policy tracking widget."""
        data = {
            "active_initiatives": active_initiatives,
            "at_risk": initiatives_at_risk,
            "success_rate": success_rate,
            "priority_items": top_priority_items
        }

        return self.add_widget(
            widget_type="policy_tracker",
            title="Policy Initiatives",
            data=data,
            refresh_interval=120
        )

    def refresh_all_widgets(self) -> int:
        """Refresh all widgets that need updating."""
        now = datetime.now()
        refreshed = 0

        for widget in self.widgets.values():
            minutes_since_update = (
                (now - widget.last_updated).total_seconds() / 60
            )

            if minutes_since_update >= widget.refresh_interval:
                # In production, would refresh data from source
                widget.last_updated = now
                refreshed += 1

        self.last_refresh = now
        logger.info(f"Refreshed {refreshed} widgets")
        return refreshed

    def export_dashboard(self) -> Dict:
        """Export dashboard state."""
        return {
            "organization": self.organization_name,
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "widgets": {
                wid: {
                    "type": w.widget_type,
                    "title": w.title,
                    "data": w.data,
                    "last_updated": w.last_updated.isoformat()
                }
                for wid, w in self.widgets.items()
            },
            "alerts": [
                {
                    "id": a.alert_id,
                    "severity": a.severity,
                    "title": a.title,
                    "message": a.message,
                    "source": a.source,
                    "created_at": a.created_at.isoformat(),
                    "action_required": a.action_required
                }
                for a in self.alerts
            ]
        }

    def generate_report(self) -> Dict:
        """Generate dashboard report."""
        summary = self.get_summary()
        critical_alerts = self.get_critical_alerts()
        action_alerts = self.get_action_required_alerts()

        return {
            "report_date": datetime.now().isoformat(),
            "organization": self.organization_name,
            "summary": summary,
            "critical_issues": [
                {
                    "title": a.title,
                    "message": a.message,
                    "source": a.source,
                    "action_url": a.action_url
                }
                for a in critical_alerts
            ],
            "items_requiring_action": len(action_alerts),
            "health_score": self._calculate_health_score()
        }

    def _calculate_health_score(self) -> float:
        """Calculate overall dashboard health score (0-100)."""
        critical_count = len(self.get_critical_alerts())
        action_count = len(self.get_action_required_alerts())

        # Deduct points for critical issues
        score = 100.0
        score -= (critical_count * 20)
        score -= (action_count * 5)

        return max(0, min(100, score))
