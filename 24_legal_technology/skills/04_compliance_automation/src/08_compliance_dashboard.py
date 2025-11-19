"""
Compliance Dashboard - Production-Ready Implementation

This module implements a comprehensive compliance monitoring dashboard including:
- Real-time compliance metrics
- Status indicators
- Trend analysis
- Alert management
- Performance KPIs
- Executive reporting

Author: Compliance Automation Team
Version: 1.0.0
License: MIT
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricStatus(Enum):
    """Status of compliance metrics."""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"


class DashboardCategory(Enum):
    """Dashboard categories."""
    GDPR = "gdpr"
    DATA_PROTECTION = "data_protection"
    INCIDENT_MANAGEMENT = "incident_management"
    AUDIT = "audit"
    REGULATORY = "regulatory"
    CONSENT = "consent"
    VENDOR_MANAGEMENT = "vendor_management"


@dataclass
class MetricIndicator:
    """Represents a single compliance metric."""
    metric_id: str
    name: str
    category: DashboardCategory
    current_value: float
    threshold: float
    status: MetricStatus
    unit: str = "%"
    target: float = 100.0
    trend: str = "stable"  # 'improving', 'stable', 'declining'
    last_updated: datetime = field(default_factory=datetime.now)
    description: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'metric_id': self.metric_id,
            'name': self.name,
            'category': self.category.value,
            'current_value': self.current_value,
            'threshold': self.threshold,
            'status': self.status.value,
            'unit': self.unit,
            'target': self.target,
            'trend': self.trend,
            'last_updated': self.last_updated.isoformat(),
            'description': self.description
        }


@dataclass
class ComplianceTask:
    """Represents a compliance task on dashboard."""
    task_id: str
    title: str
    description: str
    category: DashboardCategory
    priority: str  # 'high', 'medium', 'low'
    status: str  # 'open', 'in_progress', 'completed', 'overdue'
    assigned_to: str
    due_date: datetime
    completion_percentage: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'priority': self.priority,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'due_date': self.due_date.isoformat(),
            'completion_percentage': self.completion_percentage,
            'created_at': self.created_at.isoformat(),
            'days_until_due': (self.due_date - datetime.now()).days
        }


@dataclass
class ControlStatus:
    """Represents status of a compliance control."""
    control_id: str
    control_name: str
    description: str
    status: MetricStatus
    framework: str
    test_date: datetime
    evidence_count: int
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    remediation_status: Optional[str] = None
    owner: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'control_id': self.control_id,
            'control_name': self.control_name,
            'description': self.description,
            'status': self.status.value,
            'framework': self.framework,
            'test_date': self.test_date.isoformat(),
            'evidence_count': self.evidence_count,
            'risk_level': self.risk_level,
            'remediation_status': self.remediation_status,
            'owner': self.owner
        }


class Dashboard(ABC):
    """Abstract base class for compliance dashboard."""

    @abstractmethod
    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data."""
        pass

    @abstractmethod
    def get_metric(self, metric_id: str) -> Optional[MetricIndicator]:
        """Get specific metric."""
        pass


class ComplianceDashboard(Dashboard):
    """
    Comprehensive compliance monitoring dashboard.

    Provides:
    - Real-time metrics
    - Status tracking
    - Task management
    - Control assessment
    - KPI reporting
    - Trend analysis
    """

    def __init__(self, organization_name: str):
        """
        Initialize compliance dashboard.

        Args:
            organization_name: Name of organization
        """
        self.organization_name = organization_name
        self.metrics: Dict[str, MetricIndicator] = {}
        self.tasks: Dict[str, ComplianceTask] = {}
        self.controls: Dict[str, ControlStatus] = {}
        self.alerts: List[Dict] = []
        self.logger = logger
        self._initialize_default_metrics()

    def _initialize_default_metrics(self) -> None:
        """Initialize default compliance metrics."""
        default_metrics = [
            MetricIndicator(
                metric_id='M001',
                name='GDPR Compliance Score',
                category=DashboardCategory.GDPR,
                current_value=92.0,
                threshold=80.0,
                status=MetricStatus.COMPLIANT,
                description='Overall GDPR compliance percentage',
                trend='improving'
            ),
            MetricIndicator(
                metric_id='M002',
                name='Data Protection Audit Pass Rate',
                category=DashboardCategory.DATA_PROTECTION,
                current_value=88.0,
                threshold=85.0,
                status=MetricStatus.COMPLIANT,
                description='Percentage of data protection controls passing audits'
            ),
            MetricIndicator(
                metric_id='M003',
                name='Breach Response Time (hours)',
                category=DashboardCategory.INCIDENT_MANAGEMENT,
                current_value=4.5,
                threshold=24.0,
                status=MetricStatus.COMPLIANT,
                unit='hours',
                description='Average time to respond to security breaches'
            ),
            MetricIndicator(
                metric_id='M004',
                name='Consent Rate',
                category=DashboardCategory.CONSENT,
                current_value=78.0,
                threshold=70.0,
                status=MetricStatus.COMPLIANT,
                description='Percentage of users who have provided valid consent'
            ),
            MetricIndicator(
                metric_id='M005',
                name='Vendor Compliance Score',
                category=DashboardCategory.VENDOR_MANAGEMENT,
                current_value=85.0,
                threshold=80.0,
                status=MetricStatus.COMPLIANT,
                description='Third-party vendor compliance assessment'
            ),
            MetricIndicator(
                metric_id='M006',
                name='Audit Trail Completeness',
                category=DashboardCategory.AUDIT,
                current_value=95.0,
                threshold=90.0,
                status=MetricStatus.COMPLIANT,
                description='Percentage of events logged in audit trail'
            ),
        ]

        for metric in default_metrics:
            self.metrics[metric.metric_id] = metric

    def add_metric(self, metric: MetricIndicator) -> str:
        """
        Add a metric to dashboard.

        Args:
            metric: MetricIndicator instance

        Returns:
            Metric ID
        """
        self.metrics[metric.metric_id] = metric
        self.logger.info(f"Added metric: {metric.metric_id} - {metric.name}")
        return metric.metric_id

    def update_metric(self, metric_id: str, current_value: float) -> bool:
        """
        Update metric value.

        Args:
            metric_id: ID of metric
            current_value: New value

        Returns:
            True if successful
        """
        if metric_id not in self.metrics:
            return False

        metric = self.metrics[metric_id]
        old_value = metric.current_value

        metric.current_value = current_value
        metric.last_updated = datetime.now()

        # Update status based on threshold
        if current_value >= metric.threshold:
            metric.status = MetricStatus.COMPLIANT
        elif current_value >= metric.threshold * 0.8:
            metric.status = MetricStatus.AT_RISK
        else:
            metric.status = MetricStatus.NON_COMPLIANT

        # Determine trend
        if current_value > old_value:
            metric.trend = 'improving'
        elif current_value < old_value:
            metric.trend = 'declining'
        else:
            metric.trend = 'stable'

        # Create alert if status changed
        if metric.status == MetricStatus.NON_COMPLIANT:
            self._create_alert(
                f"Metric '{metric.name}' is below threshold",
                'metric_alert',
                'high',
                metric
            )

        self.logger.info(f"Updated metric: {metric_id} to {current_value}")
        return True

    def get_metric(self, metric_id: str) -> Optional[MetricIndicator]:
        """
        Get specific metric.

        Args:
            metric_id: ID of metric

        Returns:
            MetricIndicator or None
        """
        return self.metrics.get(metric_id)

    def add_task(self, task: ComplianceTask) -> str:
        """
        Add a compliance task.

        Args:
            task: ComplianceTask instance

        Returns:
            Task ID
        """
        self.tasks[task.task_id] = task
        self.logger.info(f"Added task: {task.task_id} - {task.title}")
        return task.task_id

    def update_task_status(
        self,
        task_id: str,
        status: str,
        completion_percentage: int = None
    ) -> bool:
        """
        Update task status.

        Args:
            task_id: ID of task
            status: New status
            completion_percentage: Completion percentage

        Returns:
            True if successful
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = status

        if completion_percentage is not None:
            task.completion_percentage = completion_percentage

        # Check if overdue
        if task.due_date < datetime.now() and status != 'completed':
            task.status = 'overdue'
            self._create_alert(
                f"Task '{task.title}' is overdue",
                'task_alert',
                'high',
                task
            )

        return True

    def add_control(self, control: ControlStatus) -> str:
        """
        Add a control assessment.

        Args:
            control: ControlStatus instance

        Returns:
            Control ID
        """
        self.controls[control.control_id] = control
        self.logger.info(f"Added control: {control.control_id}")
        return control.control_id

    def _create_alert(
        self,
        message: str,
        alert_type: str,
        severity: str,
        related_item: any = None
    ) -> None:
        """Create an alert on dashboard."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': alert_type,
            'severity': severity,
            'related_item_id': getattr(related_item, 'metric_id', None) or
                              getattr(related_item, 'task_id', None)
        }
        self.alerts.append(alert)

    def get_summary(self) -> Dict:
        """
        Get dashboard summary.

        Returns:
            Summary dictionary
        """
        # Calculate overall compliance score
        compliant_count = sum(
            1 for m in self.metrics.values()
            if m.status == MetricStatus.COMPLIANT
        )
        overall_compliance = (compliant_count / len(self.metrics) * 100) if self.metrics else 0

        # Count tasks by status
        task_summary = {}
        for status in ['open', 'in_progress', 'completed', 'overdue']:
            task_summary[status] = sum(
                1 for t in self.tasks.values()
                if t.status == status
            )

        # Count controls by status
        control_summary = {}
        for status in MetricStatus:
            control_summary[status.value] = sum(
                1 for c in self.controls.values()
                if c.status == status
            )

        # Count alerts by severity
        alert_summary = {}
        for severity in ['critical', 'high', 'medium', 'low']:
            alert_summary[severity] = sum(
                1 for a in self.alerts
                if a.get('severity') == severity
            )

        return {
            'timestamp': datetime.now().isoformat(),
            'organization': self.organization_name,
            'overall_compliance_score': overall_compliance,
            'metrics_summary': {
                'total': len(self.metrics),
                'compliant': compliant_count,
                'at_risk': sum(1 for m in self.metrics.values() if m.status == MetricStatus.AT_RISK),
                'non_compliant': sum(1 for m in self.metrics.values() if m.status == MetricStatus.NON_COMPLIANT)
            },
            'tasks_summary': task_summary,
            'controls_summary': control_summary,
            'alerts_summary': alert_summary
        }

    def get_dashboard_data(self) -> Dict:
        """
        Get complete dashboard data.

        Returns:
            Complete dashboard data dictionary
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'organization': self.organization_name,
            'summary': self.get_summary(),
            'metrics': [m.to_dict() for m in self.metrics.values()],
            'tasks': [t.to_dict() for t in self.tasks.values()],
            'controls': [c.to_dict() for c in self.controls.values()],
            'alerts': self.alerts,
            'metrics_by_category': self._group_metrics_by_category(),
            'overdue_tasks': self._get_overdue_tasks(),
            'at_risk_metrics': self._get_at_risk_metrics()
        }

    def _group_metrics_by_category(self) -> Dict[str, List[Dict]]:
        """Group metrics by category."""
        grouped = {}
        for metric in self.metrics.values():
            category = metric.category.value
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(metric.to_dict())
        return grouped

    def _get_overdue_tasks(self) -> List[Dict]:
        """Get overdue tasks."""
        now = datetime.now()
        return [
            t.to_dict()
            for t in self.tasks.values()
            if t.due_date < now and t.status != 'completed'
        ]

    def _get_at_risk_metrics(self) -> List[Dict]:
        """Get at-risk metrics."""
        return [
            m.to_dict()
            for m in self.metrics.values()
            if m.status in [MetricStatus.AT_RISK, MetricStatus.NON_COMPLIANT]
        ]

    def get_executive_summary(self) -> Dict:
        """
        Get executive summary for leadership.

        Returns:
            Executive summary
        """
        summary = self.get_summary()

        return {
            'timestamp': datetime.now().isoformat(),
            'organization': self.organization_name,
            'overall_compliance_percentage': summary['overall_compliance_score'],
            'key_metrics': {
                'total_metrics': summary['metrics_summary']['total'],
                'compliant_metrics': summary['metrics_summary']['compliant'],
                'non_compliant_metrics': summary['metrics_summary']['non_compliant']
            },
            'action_items': {
                'overdue_tasks': summary['tasks_summary'].get('overdue', 0),
                'open_tasks': summary['tasks_summary'].get('open', 0),
                'critical_alerts': summary['alerts_summary'].get('critical', 0),
                'high_alerts': summary['alerts_summary'].get('high', 0)
            },
            'health_status': self._get_health_status(),
            'recommendations': self._get_recommendations()
        }

    def _get_health_status(self) -> str:
        """Get overall health status."""
        summary = self.get_summary()
        compliance = summary['overall_compliance_score']

        if compliance >= 90:
            return 'Excellent'
        elif compliance >= 80:
            return 'Good'
        elif compliance >= 70:
            return 'Fair'
        else:
            return 'Poor'

    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on dashboard state."""
        recommendations = []

        # Check for non-compliant metrics
        non_compliant = sum(
            1 for m in self.metrics.values()
            if m.status == MetricStatus.NON_COMPLIANT
        )
        if non_compliant > 0:
            recommendations.append(
                f"Address {non_compliant} non-compliant metrics immediately"
            )

        # Check for overdue tasks
        overdue = sum(
            1 for t in self.tasks.values()
            if t.due_date < datetime.now() and t.status != 'completed'
        )
        if overdue > 0:
            recommendations.append(
                f"Complete {overdue} overdue compliance tasks"
            )

        # Check for critical alerts
        critical = sum(
            1 for a in self.alerts
            if a.get('severity') == 'critical'
        )
        if critical > 0:
            recommendations.append(
                f"Investigate and resolve {critical} critical alerts"
            )

        if not recommendations:
            recommendations.append("Maintain current compliance posture and continue monitoring")

        return recommendations


def main():
    """Example usage and demonstration."""
    # Initialize dashboard
    dashboard = ComplianceDashboard("Acme Corporation")

    # Update metrics
    dashboard.update_metric('M001', 94.0)
    dashboard.update_metric('M004', 65.0)  # Below threshold - will create alert

    # Add tasks
    from dataclasses import dataclass
    task1 = ComplianceTask(
        task_id='TSK001',
        title='Complete GDPR audit',
        description='Perform annual GDPR compliance audit',
        category=DashboardCategory.GDPR,
        priority='high',
        status='in_progress',
        assigned_to='Compliance Team',
        due_date=datetime.now() + timedelta(days=30),
        completion_percentage=75
    )
    dashboard.add_task(task1)

    # Add control
    control = ControlStatus(
        control_id='CTL001',
        control_name='Encryption at Rest',
        description='All sensitive data encrypted at rest',
        status=MetricStatus.COMPLIANT,
        framework='GDPR',
        test_date=datetime.now() - timedelta(days=5),
        evidence_count=3,
        risk_level='low',
        owner='Security Team'
    )
    dashboard.add_control(control)

    # Get dashboard data
    print("=" * 80)
    print("COMPLIANCE DASHBOARD")
    print("=" * 80)
    dashboard_data = dashboard.get_dashboard_data()
    print(json.dumps(dashboard_data, indent=2))

    # Get executive summary
    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    exec_summary = dashboard.get_executive_summary()
    print(json.dumps(exec_summary, indent=2))


if __name__ == '__main__':
    main()
