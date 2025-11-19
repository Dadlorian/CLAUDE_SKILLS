"""
Controls Testing - Production-Ready Implementation

This module implements comprehensive compliance controls testing including:
- Control design evaluation
- Control execution testing
- Evidence collection
- Test result management
- Remediation tracking
- Compliance certification

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
import uuid


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ControlType(Enum):
    """Types of compliance controls."""
    PREVENTIVE = "preventive"  # Prevent occurrence
    DETECTIVE = "detective"  # Detect after occurrence
    CORRECTIVE = "corrective"  # Correct after detection
    DIRECTIVE = "directive"  # Direct/guide behavior
    COMPENSATING = "compensating"  # Alternative when primary unavailable


class TestResult(Enum):
    """Results of control testing."""
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
    NOT_TESTED = "not_tested"
    EXCEPTION_APPROVED = "exception_approved"


class TestingFrequency(Enum):
    """Testing frequency schedules."""
    CONTINUOUS = "continuous"
    ANNUAL = "annual"
    SEMI_ANNUAL = "semi_annual"
    QUARTERLY = "quarterly"
    AS_NEEDED = "as_needed"


class ControlStatus(Enum):
    """Status of compliance control."""
    DESIGNED = "designed"  # Control designed but not yet implemented
    IMPLEMENTED = "implemented"  # Control exists
    TESTED = "tested"  # Control has been tested
    EFFECTIVE = "effective"  # Control is proven effective
    INEFFECTIVE = "ineffective"  # Control not effective
    REMEDIATED = "remediated"  # Previously ineffective control remediated


@dataclass
class ComplianceControl:
    """Represents a compliance control."""
    control_id: str
    control_name: str
    description: str
    control_type: ControlType
    frameworks: List[str]  # e.g., ['GDPR', 'ISO27001']
    control_owner: str
    risk_addressed: str
    testing_frequency: TestingFrequency
    implementation_date: datetime
    last_tested_date: Optional[datetime] = None
    next_test_date: Optional[datetime] = None
    design_documentation: List[str] = field(default_factory=list)
    supporting_policies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['control_type'] = self.control_type.value
        data['testing_frequency'] = self.testing_frequency.value
        data['implementation_date'] = self.implementation_date.isoformat()
        if self.last_tested_date:
            data['last_tested_date'] = self.last_tested_date.isoformat()
        if self.next_test_date:
            data['next_test_date'] = self.next_test_date.isoformat()
        return data


@dataclass
class ControlTestPlan:
    """Plan for testing a control."""
    plan_id: str
    control_id: str
    test_date: datetime
    scheduled_by: str
    test_scope: str
    test_procedures: List[str]
    expected_results: str
    acceptance_criteria: List[str] = field(default_factory=list)
    required_evidence: List[str] = field(default_factory=list)
    testing_frequency: TestingFrequency = TestingFrequency.ANNUAL

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['test_date'] = self.test_date.isoformat()
        data['testing_frequency'] = self.testing_frequency.value
        return data


@dataclass
class TestExecution:
    """Record of a test execution."""
    execution_id: str
    plan_id: str
    control_id: str
    executed_by: str
    execution_date: datetime
    result: TestResult
    observations: str
    evidence_collected: List[str]
    root_cause_if_failed: Optional[str] = None
    remediation_required: bool = False
    approval_status: str = "pending"  # pending, approved, rejected
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['result'] = self.result.value
        data['execution_date'] = self.execution_date.isoformat()
        if self.approval_date:
            data['approval_date'] = self.approval_date.isoformat()
        return data


@dataclass
class RemediationAction:
    """Tracks remediation for failed control."""
    action_id: str
    execution_id: str
    control_id: str
    issue_description: str
    remediation_plan: str
    responsible_party: str
    target_completion_date: datetime
    actual_completion_date: Optional[datetime] = None
    status: str = "open"  # open, in_progress, completed, deferred
    verification_method: str = "retest"
    evidence_of_completion: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['target_completion_date'] = self.target_completion_date.isoformat()
        if self.actual_completion_date:
            data['actual_completion_date'] = self.actual_completion_date.isoformat()
        return data


class ControlsTester(ABC):
    """Abstract base class for controls testing."""

    @abstractmethod
    def execute_test(self, execution: TestExecution) -> str:
        """Execute a control test."""
        pass

    @abstractmethod
    def get_test_status(self, control_id: str) -> Dict:
        """Get testing status for control."""
        pass


class ComplianceControlsTester(ControlsTester):
    """
    Comprehensive compliance controls testing system.

    Provides:
    - Control inventory management
    - Test planning
    - Test execution
    - Evidence collection
    - Remediation tracking
    - Certification reporting
    """

    def __init__(self, organization_name: str):
        """
        Initialize controls tester.

        Args:
            organization_name: Name of organization
        """
        self.organization_name = organization_name
        self.controls: Dict[str, ComplianceControl] = {}
        self.test_plans: Dict[str, ControlTestPlan] = {}
        self.test_executions: Dict[str, TestExecution] = {}
        self.remediation_actions: Dict[str, RemediationAction] = {}
        self.logger = logger

    def add_control(self, control: ComplianceControl) -> str:
        """
        Add a compliance control.

        Args:
            control: ComplianceControl instance

        Returns:
            Control ID
        """
        self.controls[control.control_id] = control
        self.logger.info(f"Added control: {control.control_id} - {control.control_name}")
        return control.control_id

    def plan_control_test(
        self,
        control_id: str,
        test_date: datetime,
        scheduled_by: str,
        test_scope: str,
        test_procedures: List[str],
        expected_results: str,
        acceptance_criteria: List[str] = None
    ) -> str:
        """
        Plan a control test.

        Args:
            control_id: ID of control to test
            test_date: Scheduled test date
            scheduled_by: User scheduling test
            test_scope: Scope of test
            test_procedures: Test procedures to follow
            expected_results: Expected test results
            acceptance_criteria: Test acceptance criteria

        Returns:
            Plan ID
        """
        if control_id not in self.controls:
            raise ValueError(f"Control not found: {control_id}")

        plan_id = str(uuid.uuid4())
        control = self.controls[control_id]

        plan = ControlTestPlan(
            plan_id=plan_id,
            control_id=control_id,
            test_date=test_date,
            scheduled_by=scheduled_by,
            test_scope=test_scope,
            test_procedures=test_procedures,
            expected_results=expected_results,
            acceptance_criteria=acceptance_criteria or [],
            testing_frequency=control.testing_frequency
        )

        self.test_plans[plan_id] = plan
        self.logger.info(f"Created test plan: {plan_id}")
        return plan_id

    def execute_test(self, execution: TestExecution) -> str:
        """
        Execute a control test.

        Args:
            execution: TestExecution instance

        Returns:
            Execution ID
        """
        if execution.control_id not in self.controls:
            raise ValueError(f"Control not found: {execution.control_id}")

        if execution.plan_id not in self.test_plans:
            raise ValueError(f"Test plan not found: {execution.plan_id}")

        self.test_executions[execution.execution_id] = execution

        # Update control information
        control = self.controls[execution.control_id]
        control.last_tested_date = execution.execution_date

        # Schedule next test
        if execution.testing_frequency == TestingFrequency.ANNUAL:
            control.next_test_date = execution.execution_date + timedelta(days=365)
        elif execution.testing_frequency == TestingFrequency.SEMI_ANNUAL:
            control.next_test_date = execution.execution_date + timedelta(days=180)
        elif execution.testing_frequency == TestingFrequency.QUARTERLY:
            control.next_test_date = execution.execution_date + timedelta(days=90)

        # Create remediation if test failed
        if execution.result == TestResult.FAILED and execution.remediation_required:
            self._create_remediation_action(execution)

        self.logger.info(f"Executed test: {execution.execution_id} - Result: {execution.result.value}")
        return execution.execution_id

    def _create_remediation_action(self, execution: TestExecution) -> str:
        """Create remediation action for failed test."""
        action_id = str(uuid.uuid4())

        control = self.controls[execution.control_id]
        action = RemediationAction(
            action_id=action_id,
            execution_id=execution.execution_id,
            control_id=execution.control_id,
            issue_description=execution.observations,
            remediation_plan="To be determined",
            responsible_party=control.control_owner,
            target_completion_date=datetime.now() + timedelta(days=30),
            status="open"
        )

        self.remediation_actions[action_id] = action
        self.logger.info(f"Created remediation action: {action_id}")
        return action_id

    def approve_test_result(
        self,
        execution_id: str,
        approved_by: str,
        approval_status: str = "approved"
    ) -> bool:
        """
        Approve test result.

        Args:
            execution_id: ID of execution
            approved_by: User approving
            approval_status: Approval status

        Returns:
            True if successful
        """
        if execution_id not in self.test_executions:
            return False

        execution = self.test_executions[execution_id]
        execution.approval_status = approval_status
        execution.approved_by = approved_by
        execution.approval_date = datetime.now()

        # Update control status if approved
        if approval_status == "approved":
            control = self.controls[execution.control_id]
            if execution.result == TestResult.PASSED:
                control.metadata['status'] = ControlStatus.EFFECTIVE.value
            elif execution.result == TestResult.FAILED:
                control.metadata['status'] = ControlStatus.INEFFECTIVE.value

        self.logger.info(f"Approved test result: {execution_id}")
        return True

    def update_remediation_action(
        self,
        action_id: str,
        status: str,
        actual_completion_date: Optional[datetime] = None,
        evidence_of_completion: Optional[List[str]] = None
    ) -> bool:
        """
        Update remediation action status.

        Args:
            action_id: ID of remediation action
            status: New status
            actual_completion_date: Completion date
            evidence_of_completion: Evidence files

        Returns:
            True if successful
        """
        if action_id not in self.remediation_actions:
            return False

        action = self.remediation_actions[action_id]
        action.status = status

        if status == "completed" and actual_completion_date:
            action.actual_completion_date = actual_completion_date
            self.logger.info(f"Completed remediation action: {action_id}")

        if evidence_of_completion:
            action.evidence_of_completion = evidence_of_completion

        return True

    def get_test_status(self, control_id: str) -> Dict:
        """
        Get testing status for control.

        Args:
            control_id: ID of control

        Returns:
            Status dictionary
        """
        if control_id not in self.controls:
            return {'error': 'Control not found'}

        control = self.controls[control_id]

        # Find related executions
        related_executions = [
            e for e in self.test_executions.values()
            if e.control_id == control_id
        ]

        latest_execution = (
            max(related_executions, key=lambda e: e.execution_date)
            if related_executions else None
        )

        # Find related remediations
        related_remediations = [
            a for a in self.remediation_actions.values()
            if a.control_id == control_id
        ]

        pending_remediations = [
            a for a in related_remediations
            if a.status in ['open', 'in_progress']
        ]

        return {
            'control_id': control_id,
            'control_name': control.control_name,
            'last_tested_date': control.last_tested_date.isoformat() if control.last_tested_date else None,
            'next_test_date': control.next_test_date.isoformat() if control.next_test_date else None,
            'test_count': len(related_executions),
            'latest_result': latest_execution.result.value if latest_execution else 'not_tested',
            'pending_remediations': len(pending_remediations),
            'remediation_actions': [a.to_dict() for a in pending_remediations]
        }

    def get_controls_by_framework(self, framework: str) -> List[Dict]:
        """
        Get controls for specific framework.

        Args:
            framework: Framework name (e.g., 'GDPR')

        Returns:
            List of controls
        """
        matching_controls = [
            c for c in self.controls.values()
            if framework in c.frameworks
        ]

        return [c.to_dict() for c in matching_controls]

    def generate_control_inventory(self) -> Dict:
        """
        Generate control inventory report.

        Returns:
            Inventory dictionary
        """
        controls_by_type = {}
        for control in self.controls.values():
            control_type = control.control_type.value
            if control_type not in controls_by_type:
                controls_by_type[control_type] = 0
            controls_by_type[control_type] += 1

        controls_by_framework = {}
        for control in self.controls.values():
            for framework in control.frameworks:
                if framework not in controls_by_framework:
                    controls_by_framework[framework] = 0
                controls_by_framework[framework] += 1

        not_tested = sum(
            1 for c in self.controls.values()
            if c.last_tested_date is None
        )

        overdue_tests = sum(
            1 for c in self.controls.values()
            if c.next_test_date and c.next_test_date < datetime.now()
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'total_controls': len(self.controls),
            'controls_by_type': controls_by_type,
            'controls_by_framework': controls_by_framework,
            'never_tested': not_tested,
            'overdue_tests': overdue_tests,
            'controls': [c.to_dict() for c in self.controls.values()]
        }

    def generate_testing_report(self, days: int = 90) -> Dict:
        """
        Generate testing report for period.

        Args:
            days: Number of days to include

        Returns:
            Testing report
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_executions = [
            e for e in self.test_executions.values()
            if e.execution_date >= cutoff_date
        ]

        results_summary = {}
        for result in TestResult:
            results_summary[result.value] = sum(
                1 for e in recent_executions
                if e.result == result
            )

        pending_approvals = sum(
            1 for e in recent_executions
            if e.approval_status == 'pending'
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'executions_count': len(recent_executions),
            'results_summary': results_summary,
            'pass_rate': (
                (results_summary.get('passed', 0) / len(recent_executions) * 100)
                if recent_executions else 0
            ),
            'pending_approvals': pending_approvals,
            'recent_executions': [e.to_dict() for e in recent_executions[-10:]]
        }

    def generate_remediation_report(self) -> Dict:
        """
        Generate remediation tracking report.

        Returns:
            Remediation report
        """
        open_remediations = [
            a for a in self.remediation_actions.values()
            if a.status == 'open'
        ]

        overdue_remediations = [
            a for a in open_remediations
            if a.target_completion_date < datetime.now()
        ]

        return {
            'timestamp': datetime.now().isoformat(),
            'total_remediations': len(self.remediation_actions),
            'open_remediations': len(open_remediations),
            'overdue_remediations': len(overdue_remediations),
            'completed_remediations': sum(
                1 for a in self.remediation_actions.values()
                if a.status == 'completed'
            ),
            'overdue_details': [a.to_dict() for a in overdue_remediations],
            'open_details': [a.to_dict() for a in open_remediations[:10]]
        }

    def generate_certification_report(self) -> Dict:
        """
        Generate compliance certification report.

        Returns:
            Certification report
        """
        total_controls = len(self.controls)
        tested_controls = sum(
            1 for c in self.controls.values()
            if c.last_tested_date is not None
        )

        effective_controls = sum(
            1 for c in self.controls.values()
            if c.metadata.get('status') == ControlStatus.EFFECTIVE.value
        )

        pending_remediation = sum(
            1 for a in self.remediation_actions.values()
            if a.status in ['open', 'in_progress']
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'organization': self.organization_name,
            'overall_control_health': (
                (effective_controls / total_controls * 100) if total_controls > 0 else 0
            ),
            'control_summary': {
                'total': total_controls,
                'tested': tested_controls,
                'effective': effective_controls,
                'ineffective': total_controls - effective_controls - tested_controls + effective_controls
            },
            'remediation_summary': {
                'total_actions': len(self.remediation_actions),
                'pending': pending_remediation,
                'completed': sum(
                    1 for a in self.remediation_actions.values()
                    if a.status == 'completed'
                )
            },
            'certification_ready': effective_controls >= total_controls * 0.95,  # 95% threshold
            'certification_date': datetime.now().isoformat() if effective_controls >= total_controls * 0.95 else None
        }


def main():
    """Example usage and demonstration."""
    # Initialize tester
    tester = ComplianceControlsTester("Acme Corporation")

    # Add controls
    control1 = ComplianceControl(
        control_id='CTL001',
        control_name='Encryption at Rest',
        description='All sensitive data encrypted at rest',
        control_type=ControlType.PREVENTIVE,
        frameworks=['GDPR', 'ISO27001'],
        control_owner='Security Team',
        risk_addressed='Unauthorized data access',
        testing_frequency=TestingFrequency.ANNUAL,
        implementation_date=datetime.now() - timedelta(days=365)
    )
    tester.add_control(control1)

    control2 = ComplianceControl(
        control_id='CTL002',
        control_name='Access Logging',
        description='All data access logged and monitored',
        control_type=ControlType.DETECTIVE,
        frameworks=['GDPR', 'HIPAA'],
        control_owner='Security Team',
        risk_addressed='Unauthorized data access detection',
        testing_frequency=TestingFrequency.QUARTERLY,
        implementation_date=datetime.now() - timedelta(days=180)
    )
    tester.add_control(control2)

    # Plan test
    plan_id = tester.plan_control_test(
        'CTL001',
        datetime.now() + timedelta(days=7),
        'compliance_officer',
        'Test encryption implementation',
        ['Verify encryption keys', 'Test key rotation', 'Validate encryption standards'],
        'All data encrypted using approved standards',
        ['AES-256 encryption', 'Regular key rotation', 'Secure key storage']
    )

    # Execute test
    execution = TestExecution(
        execution_id=str(uuid.uuid4()),
        plan_id=plan_id,
        control_id='CTL001',
        executed_by='security_tester',
        execution_date=datetime.now(),
        result=TestResult.PASSED,
        observations='All data properly encrypted, key rotation working correctly',
        evidence_collected=['Encryption verification report', 'Key rotation logs']
    )
    tester.execute_test(execution)

    # Approve test
    tester.approve_test_result(execution.execution_id, 'compliance_manager')

    # Generate reports
    print("=" * 80)
    print("CONTROL INVENTORY")
    print("=" * 80)
    inventory = tester.generate_control_inventory()
    print(json.dumps(inventory, indent=2))

    print("\n" + "=" * 80)
    print("TESTING REPORT")
    print("=" * 80)
    testing_report = tester.generate_testing_report(days=90)
    print(json.dumps(testing_report, indent=2))

    print("\n" + "=" * 80)
    print("CERTIFICATION REPORT")
    print("=" * 80)
    certification = tester.generate_certification_report()
    print(json.dumps(certification, indent=2))


if __name__ == '__main__':
    main()
