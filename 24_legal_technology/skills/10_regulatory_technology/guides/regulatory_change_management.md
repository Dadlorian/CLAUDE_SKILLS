# Regulatory Change Management Guide

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Change Management Framework](#change-management-framework)
3. [Impact Assessment](#impact-assessment)
4. [Compliance Workflows](#compliance-workflows)
5. [Documentation Systems](#documentation-systems)
6. [Stakeholder Communication](#stakeholder-communication)
7. [Implementation Workflow](#implementation-workflow)
8. [Monitoring and Reporting](#monitoring-and-reporting)
9. [Risk Management](#risk-management)
10. [Best Practices](#best-practices)

## Executive Summary

Regulatory change management encompasses identifying, analyzing, prioritizing, and implementing organizational responses to regulatory changes. This guide provides a structured approach to managing regulatory transitions efficiently while minimizing disruption and ensuring compliance.

### Key Objectives
- Rapid identification of applicable regulatory changes
- Comprehensive impact assessment across departments
- Prioritized implementation of compliance requirements
- Clear communication and coordination
- Documentation of compliance efforts
- Risk mitigation throughout transitions

### Success Metrics
- Time from regulatory publication to compliance assessment: <5 business days
- Implementation completion rate: 95%+
- Stakeholder awareness: 90%+ of affected staff
- Compliance violation rate: <1%
- Documentation completeness: 100%

## Change Management Framework

### Three-Phase Model

```
┌─────────────────────────────────────────────────────┐
│         Regulatory Change Management                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Phase 1: DETECTION & ANALYSIS                      │
│  ├─ Regulatory Source Monitoring                   │
│  ├─ Content Analysis                               │
│  ├─ Applicability Assessment                       │
│  └─ Initial Impact Screening                       │
│                                                     │
│  Phase 2: PLANNING & ASSESSMENT                     │
│  ├─ Detailed Impact Analysis                       │
│  ├─ Compliance Gap Analysis                        │
│  ├─ Resource Planning                              │
│  └─ Timeline Development                           │
│                                                     │
│  Phase 3: IMPLEMENTATION & MONITORING               │
│  ├─ Change Execution                               │
│  ├─ Stakeholder Communication                      │
│  ├─ Compliance Verification                        │
│  └─ Ongoing Monitoring                             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Change Classification System

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class ChangeType(Enum):
    """Categorizes regulatory changes by type"""
    NEW_REQUIREMENT = "new_requirement"
    REQUIREMENT_MODIFICATION = "modification"
    REQUIREMENT_REMOVAL = "removal"
    CLARIFICATION = "clarification"
    IMPLEMENTATION_GUIDANCE = "guidance"

class ChangeScope(Enum):
    """Scope of impact"""
    ENTERPRISE_WIDE = "enterprise"
    DEPARTMENT = "department"
    BUSINESS_UNIT = "business_unit"
    SPECIFIC_PROCESS = "process"

class ComplianceUrgency(Enum):
    """Urgency classification"""
    CRITICAL = 1  # Must comply within 30 days
    HIGH = 2      # Must comply within 60 days
    MEDIUM = 3    # Must comply within 90 days
    LOW = 4       # Must comply within 180+ days

@dataclass
class RegulatoryChange:
    """Represents a regulatory change"""

    # Identification
    change_id: str
    source: str  # 'federal', 'state', 'local'
    jurisdiction: str
    regulation_id: str
    regulation_name: str

    # Classification
    change_type: ChangeType
    scope: ChangeScope
    urgency: ComplianceUrgency

    # Content
    title: str
    description: str
    full_text_url: str
    key_requirements: List[str]
    affected_sections: List[str]

    # Dates
    publication_date: datetime
    effective_date: datetime
    deadline_for_compliance: datetime
    comment_period_end: Optional[datetime]

    # Impact
    estimated_hours_required: int
    estimated_cost: Optional[float]
    affected_departments: List[str]
    affected_processes: List[str]
    risk_level: str  # 'critical', 'high', 'medium', 'low'

    # Status
    internal_status: str  # 'identified', 'analyzing', 'planned', 'implementing', 'implemented', 'monitored'
    owner: str
    implementation_team: List[str]

    # Tracking
    created_at: datetime
    last_updated: datetime

class RegulatoryChangeDetector:
    """Detects and classifies regulatory changes"""

    def __init__(self, db_connection):
        self.db = db_connection

    def detect_change(self, regulation_data: Dict) -> RegulatoryChange:
        """
        Detect and classify a new regulatory change

        Args:
            regulation_data: Raw regulation data from source

        Returns:
            Classified RegulatoryChange object
        """
        # Extract key information
        change_type = self._determine_change_type(regulation_data)
        applicability = self._assess_applicability(regulation_data)

        # Initial impact assessment
        affected_departments = self._identify_affected_departments(
            regulation_data.get('subject_areas', [])
        )

        # Determine urgency
        days_until_effective = (
            regulation_data.get('effective_date') - datetime.now()
        ).days
        urgency = self._calculate_urgency(days_until_effective)

        return RegulatoryChange(
            change_id=f"CHG-{regulation_data['regulation_id']}",
            source=regulation_data.get('source', 'federal'),
            jurisdiction=regulation_data.get('jurisdiction', 'US'),
            regulation_id=regulation_data['regulation_id'],
            regulation_name=regulation_data['name'],
            change_type=change_type,
            scope=self._determine_scope(affected_departments),
            urgency=urgency,
            title=regulation_data['title'],
            description=regulation_data.get('summary', ''),
            full_text_url=regulation_data['url'],
            key_requirements=self._extract_requirements(regulation_data),
            affected_sections=regulation_data.get('affected_sections', []),
            publication_date=regulation_data['publication_date'],
            effective_date=regulation_data['effective_date'],
            deadline_for_compliance=regulation_data['effective_date'],
            comment_period_end=regulation_data.get('comment_period_end'),
            estimated_hours_required=self._estimate_hours(regulation_data),
            estimated_cost=None,
            affected_departments=affected_departments,
            affected_processes=self._identify_affected_processes(affected_departments),
            risk_level=self._assess_risk_level(change_type, urgency),
            internal_status='identified',
            owner='Compliance Officer',
            implementation_team=[],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )

    def _determine_change_type(self, regulation_data: Dict) -> ChangeType:
        """Determine type of regulatory change"""
        text = regulation_data.get('description', '').lower()

        if 'new' in text or 'added' in text or 'requires' in text:
            return ChangeType.NEW_REQUIREMENT
        elif 'modified' in text or 'changed' in text or 'amended' in text:
            return ChangeType.REQUIREMENT_MODIFICATION
        elif 'removed' in text or 'repealed' in text or 'eliminated' in text:
            return ChangeType.REQUIREMENT_REMOVAL
        elif 'clarif' in text or 'interpret' in text:
            return ChangeType.CLARIFICATION
        else:
            return ChangeType.IMPLEMENTATION_GUIDANCE

    def _calculate_urgency(self, days_until_effective: int) -> ComplianceUrgency:
        """Determine urgency based on time to compliance"""
        if days_until_effective <= 30:
            return ComplianceUrgency.CRITICAL
        elif days_until_effective <= 60:
            return ComplianceUrgency.HIGH
        elif days_until_effective <= 90:
            return ComplianceUrgency.MEDIUM
        else:
            return ComplianceUrgency.LOW

    def _assess_risk_level(self, change_type: ChangeType,
                          urgency: ComplianceUrgency) -> str:
        """Assess risk level of non-compliance"""
        if urgency == ComplianceUrgency.CRITICAL:
            return 'critical'
        elif change_type == ChangeType.NEW_REQUIREMENT:
            return 'high'
        elif urgency == ComplianceUrgency.HIGH:
            return 'high'
        elif change_type == ChangeType.REQUIREMENT_MODIFICATION:
            return 'medium'
        else:
            return 'low'
```

## Impact Assessment

### Detailed Impact Analysis

```python
from typing import Tuple
from dataclasses import field

@dataclass
class ImpactAssessment:
    """Comprehensive impact assessment of a regulatory change"""

    change_id: str

    # Operational Impact
    processes_affected: List[str]
    systems_requiring_changes: List[str]
    workflow_changes_required: List[Dict]
    estimated_disruption_hours: int

    # Resource Impact
    required_staff: List[Dict]  # {role: str, hours: int}
    required_training: List[str]
    external_expert_needs: List[str]
    capital_investment_required: float

    # Financial Impact
    implementation_cost: float
    ongoing_compliance_cost: float
    cost_per_department: Dict[str, float]
    roi_period: Optional[int]  # months

    # Compliance Gap
    current_compliance_status: str  # 'compliant', 'partial', 'non-compliant'
    gaps: List[Dict]
    gap_remediation_plan: List[Dict]

    # Risk Assessment
    implementation_risks: List[Dict]
    mitigation_strategies: List[Dict]
    residual_risks: List[Dict]

    # Timeline
    implementation_phases: List[Dict]
    critical_milestones: List[Tuple[str, datetime]]

    created_at: datetime = field(default_factory=datetime.now)

class ImpactAnalyzer:
    """Analyzes regulatory change impact"""

    def __init__(self, db_connection, organizational_map: Dict):
        self.db = db_connection
        self.org_map = organizational_map

    def assess_impact(self, change: RegulatoryChange) -> ImpactAssessment:
        """Perform comprehensive impact assessment"""

        # Identify affected processes
        processes = self._identify_affected_processes(change)

        # Identify system changes needed
        systems = self._identify_system_changes(change, processes)

        # Calculate resource requirements
        resources = self._calculate_resources(change, processes, systems)

        # Assess compliance gap
        gaps = self._assess_compliance_gaps(change)

        # Identify risks
        risks = self._identify_implementation_risks(change, resources)

        # Develop timeline
        timeline = self._develop_implementation_timeline(change, processes, resources)

        return ImpactAssessment(
            change_id=change.change_id,
            processes_affected=processes,
            systems_requiring_changes=systems,
            workflow_changes_required=self._detail_workflow_changes(processes),
            estimated_disruption_hours=self._estimate_disruption(processes, resources),
            required_staff=resources['staff'],
            required_training=resources['training'],
            external_expert_needs=resources['external_experts'],
            capital_investment_required=resources['capital'],
            implementation_cost=resources['implementation_cost'],
            ongoing_compliance_cost=resources['ongoing_cost'],
            cost_per_department=resources['departmental_costs'],
            current_compliance_status=gaps['status'],
            gaps=gaps['identified_gaps'],
            gap_remediation_plan=gaps['remediation'],
            implementation_risks=risks['implementation'],
            mitigation_strategies=risks['mitigation'],
            residual_risks=risks['residual'],
            implementation_phases=timeline['phases'],
            critical_milestones=timeline['milestones']
        )

    def _identify_affected_processes(self, change: RegulatoryChange) -> List[str]:
        """Identify all processes affected by the change"""
        affected_processes = []

        for process in self.org_map.get('processes', []):
            regulatory_requirements = process.get('regulatory_requirements', [])

            # Check if regulation applies to this process
            if self._regulation_applies(change, regulatory_requirements):
                affected_processes.append(process['name'])

        return affected_processes

    def _identify_system_changes(self, change: RegulatoryChange,
                                processes: List[str]) -> List[str]:
        """Identify systems requiring changes"""
        systems = []

        for process in processes:
            process_systems = self.org_map.get('processes', {}).get(process, {}).get('systems', [])
            systems.extend(process_systems)

        return list(set(systems))

    def _assess_compliance_gaps(self, change: RegulatoryChange) -> Dict:
        """Assess current compliance gaps"""
        gaps = {
            'status': 'non-compliant',
            'identified_gaps': [],
            'remediation': []
        }

        for requirement in change.key_requirements:
            gap = {
                'requirement': requirement,
                'current_implementation': None,
                'gap_description': '',
                'severity': 'high'
            }

            # Check if requirement is already implemented
            current_state = self._check_requirement_implementation(requirement)

            if current_state['implemented']:
                gap['severity'] = 'none'
            elif current_state['partial']:
                gap['severity'] = 'medium'
                gap['gap_description'] = current_state['reason']
                gaps['status'] = 'partial'
            else:
                gap['severity'] = 'high'
                gap['gap_description'] = 'Not currently implemented'
                gaps['status'] = 'non-compliant'

            if gap['severity'] != 'none':
                gaps['identified_gaps'].append(gap)

                remediation = {
                    'requirement': requirement,
                    'current_state': current_state,
                    'target_state': f"Fully compliant with {change.regulation_name}",
                    'remediation_steps': self._develop_remediation_steps(requirement),
                    'responsible_party': self._identify_responsible_party(requirement),
                    'estimated_effort': self._estimate_effort(requirement),
                    'timeline': self._develop_remediation_timeline(requirement)
                }
                gaps['remediation'].append(remediation)

        return gaps

    def _identify_implementation_risks(self, change: RegulatoryChange,
                                       resources: Dict) -> Dict:
        """Identify risks in implementing the change"""
        risks = {
            'implementation': [],
            'mitigation': [],
            'residual': []
        }

        # Technical risks
        technical_risks = self._assess_technical_risks(change)
        risks['implementation'].extend(technical_risks)

        # Resource risks
        resource_risks = self._assess_resource_risks(resources)
        risks['implementation'].extend(resource_risks)

        # Organizational risks
        org_risks = self._assess_organizational_risks(change)
        risks['implementation'].extend(org_risks)

        # Develop mitigation strategies
        for risk in risks['implementation']:
            mitigation = {
                'risk': risk['description'],
                'probability': risk['probability'],
                'impact': risk['impact'],
                'mitigation_strategy': self._develop_mitigation(risk),
                'responsible_party': risk.get('owner', 'Project Manager'),
                'implementation_date': datetime.now() + timedelta(days=7)
            }
            risks['mitigation'].append(mitigation)

        return risks

    def _develop_implementation_timeline(self, change: RegulatoryChange,
                                        processes: List[str],
                                        resources: Dict) -> Dict:
        """Develop detailed implementation timeline"""

        # Calculate total effort
        total_effort_hours = sum(
            r['hours'] for r in resources['staff']
        )

        # Estimate duration (assuming 8-hour work days)
        total_work_days = total_effort_hours / 8

        # Build phases
        phases = [
            {
                'name': 'Assessment & Planning',
                'duration_days': 5,
                'tasks': ['Finalize impact assessment', 'Develop detailed plan'],
                'start_date': datetime.now()
            },
            {
                'name': 'Design & Approval',
                'duration_days': 10,
                'tasks': ['Design solutions', 'Obtain approvals'],
                'start_date': datetime.now() + timedelta(days=5)
            },
            {
                'name': 'Implementation',
                'duration_days': max(20, int(total_work_days / 5)),
                'tasks': ['Execute system changes', 'Update processes', 'Implement controls'],
                'start_date': datetime.now() + timedelta(days=15)
            },
            {
                'name': 'Testing & Validation',
                'duration_days': 10,
                'tasks': ['Test compliance', 'Validate controls'],
                'start_date': datetime.now() + timedelta(days=35)
            },
            {
                'name': 'Training & Deployment',
                'duration_days': 5,
                'tasks': ['Deliver training', 'Full deployment'],
                'start_date': datetime.now() + timedelta(days=45)
            },
            {
                'name': 'Monitoring & Optimization',
                'duration_days': 30,
                'tasks': ['Monitor compliance', 'Optimize processes'],
                'start_date': datetime.now() + timedelta(days=50)
            }
        ]

        # Set end dates for phases
        for i, phase in enumerate(phases):
            phase['end_date'] = phase['start_date'] + timedelta(days=phase['duration_days'])

        # Identify critical milestones
        milestones = [
            ('Project Kickoff', phases[0]['start_date']),
            ('Design Approval', phases[1]['end_date']),
            ('Implementation Start', phases[2]['start_date']),
            ('Testing Complete', phases[3]['end_date']),
            ('Full Deployment', phases[4]['end_date']),
            ('Compliance Verification', phases[5]['end_date'])
        ]

        return {
            'phases': phases,
            'milestones': milestones,
            'total_duration_days': sum(p['duration_days'] for p in phases)
        }
```

## Compliance Workflows

### Automated Workflow Engine

```python
from enum import Enum
from typing import Callable
import asyncio

class WorkflowStage(Enum):
    DETECTION = "detection"
    ASSESSMENT = "assessment"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    MONITORING = "monitoring"

@dataclass
class WorkflowTask:
    """Individual task in compliance workflow"""

    task_id: str
    stage: WorkflowStage
    task_name: str
    description: str
    responsible_party: str
    estimated_hours: int
    dependencies: List[str]
    due_date: datetime
    status: str  # 'pending', 'in_progress', 'completed', 'blocked'
    completion_date: Optional[datetime] = None
    evidence: Optional[List[str]] = None
    notes: str = ""

class ComplianceWorkflow:
    """Manages regulatory compliance workflows"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.workflows = {}

    def create_workflow(self, change: RegulatoryChange,
                        impact_assessment: ImpactAssessment) -> str:
        """Create a new compliance workflow for a regulatory change"""

        workflow_id = f"WF-{change.change_id}"

        # Generate tasks from assessment
        tasks = self._generate_workflow_tasks(change, impact_assessment)

        # Assign responsibilities
        self._assign_responsibilities(tasks, change.affected_departments)

        # Set dependencies
        self._establish_task_dependencies(tasks)

        # Store workflow
        self.workflows[workflow_id] = {
            'change_id': change.change_id,
            'tasks': tasks,
            'status': 'active',
            'created_at': datetime.now(),
            'target_completion_date': change.deadline_for_compliance
        }

        # Persist to database
        self.db.insert_workflow(workflow_id, self.workflows[workflow_id])

        return workflow_id

    def _generate_workflow_tasks(self, change: RegulatoryChange,
                                impact: ImpactAssessment) -> List[WorkflowTask]:
        """Generate workflow tasks from impact assessment"""

        tasks = []
        base_date = datetime.now()

        # Detection phase (should be complete)
        tasks.append(WorkflowTask(
            task_id='T-001',
            stage=WorkflowStage.DETECTION,
            task_name='Regulatory Change Detected',
            description=f"Identified: {change.title}",
            responsible_party='Compliance Team',
            estimated_hours=2,
            dependencies=[],
            due_date=base_date,
            status='completed',
            completion_date=base_date
        ))

        # Assessment phase
        tasks.append(WorkflowTask(
            task_id='T-002',
            stage=WorkflowStage.ASSESSMENT,
            task_name='Complete Impact Assessment',
            description='Conduct detailed impact analysis',
            responsible_party='Compliance Manager',
            estimated_hours=20,
            dependencies=['T-001'],
            due_date=base_date + timedelta(days=5),
            status='in_progress'
        ))

        # Planning phase
        tasks.append(WorkflowTask(
            task_id='T-003',
            stage=WorkflowStage.PLANNING,
            task_name='Develop Implementation Plan',
            description='Create detailed implementation plan',
            responsible_party='Project Manager',
            estimated_hours=15,
            dependencies=['T-002'],
            due_date=base_date + timedelta(days=10),
            status='pending'
        ))

        tasks.append(WorkflowTask(
            task_id='T-004',
            stage=WorkflowStage.PLANNING,
            task_name='Secure Approvals',
            description='Obtain executive approval for plan',
            responsible_party='Compliance Officer',
            estimated_hours=5,
            dependencies=['T-003'],
            due_date=base_date + timedelta(days=12),
            status='pending'
        ))

        # Implementation phase tasks
        for i, remediation in enumerate(impact.gap_remediation_plan):
            tasks.append(WorkflowTask(
                task_id=f'T-IMP-{i:03d}',
                stage=WorkflowStage.IMPLEMENTATION,
                task_name=f"Implement: {remediation['requirement'][:50]}",
                description=remediation['requirement'],
                responsible_party=remediation['responsible_party'],
                estimated_hours=remediation['estimated_effort'],
                dependencies=['T-004'],
                due_date=base_date + timedelta(days=20) + timedelta(days=i),
                status='pending'
            ))

        # Verification phase
        tasks.append(WorkflowTask(
            task_id='T-VER-001',
            stage=WorkflowStage.VERIFICATION,
            task_name='Verify Compliance',
            description='Verify all changes meet regulatory requirements',
            responsible_party='Compliance Officer',
            estimated_hours=10,
            dependencies=[f'T-IMP-{i:03d}' for i in range(len(impact.gap_remediation_plan))],
            due_date=base_date + timedelta(days=35),
            status='pending'
        ))

        # Monitoring phase
        tasks.append(WorkflowTask(
            task_id='T-MON-001',
            stage=WorkflowStage.MONITORING,
            task_name='Establish Ongoing Monitoring',
            description='Set up controls for ongoing compliance',
            responsible_party='Compliance Manager',
            estimated_hours=8,
            dependencies=['T-VER-001'],
            due_date=base_date + timedelta(days=45),
            status='pending'
        ))

        return tasks

    async def execute_workflow(self, workflow_id: str):
        """Execute workflow asynchronously"""

        workflow = self.workflows[workflow_id]
        tasks = workflow['tasks']

        # Group tasks by stage
        stages = {}
        for task in tasks:
            if task.stage not in stages:
                stages[task.stage] = []
            stages[task.stage].append(task)

        # Execute stages sequentially
        for stage in WorkflowStage:
            if stage not in stages:
                continue

            stage_tasks = stages[stage]

            # Execute stage tasks concurrently
            await asyncio.gather(*[
                self._execute_task(task)
                for task in stage_tasks
            ])

    async def _execute_task(self, task: WorkflowTask):
        """Execute a single workflow task"""

        task.status = 'in_progress'

        try:
            # Simulate task execution
            await asyncio.sleep(task.estimated_hours * 60)  # Convert hours to seconds

            task.status = 'completed'
            task.completion_date = datetime.now()

        except Exception as e:
            task.status = 'blocked'
            task.notes = str(e)
```

## Documentation Systems

### Compliance Documentation Framework

```python
from typing import Optional
from pathlib import Path

@dataclass
class ComplianceDocument:
    """Represents a compliance documentation artifact"""

    document_id: str
    change_id: str
    document_type: str  # 'gap_assessment', 'implementation_plan', 'evidence', etc.
    title: str
    description: str
    content: str
    file_path: Optional[str]
    version: str
    author: str
    review_status: str  # 'draft', 'under_review', 'approved'
    created_date: datetime
    last_modified: datetime
    reviewed_by: Optional[str]
    approved_by: Optional[str]
    retention_until: Optional[datetime]

class ComplianceDocumentManager:
    """Manages compliance documentation"""

    def __init__(self, storage_path: str, db_connection):
        self.storage_path = Path(storage_path)
        self.db = db_connection
        self._ensure_storage_exists()

    def create_gap_assessment_document(self, change: RegulatoryChange,
                                      impact: ImpactAssessment,
                                      author: str) -> ComplianceDocument:
        """Create a gap assessment document"""

        content = self._generate_gap_assessment(change, impact)

        doc = ComplianceDocument(
            document_id=f"GAP-{change.change_id}",
            change_id=change.change_id,
            document_type='gap_assessment',
            title=f"Gap Assessment - {change.regulation_name}",
            description=f"Compliance gap assessment for {change.title}",
            content=content,
            file_path=None,
            version='1.0',
            author=author,
            review_status='draft',
            created_date=datetime.now(),
            last_modified=datetime.now(),
            reviewed_by=None,
            approved_by=None,
            retention_until=datetime.now() + timedelta(days=365*3)  # 3 years
        )

        # Save to storage
        doc.file_path = self._save_document(doc)

        # Store in database
        self.db.insert_document(doc)

        return doc

    def create_implementation_plan_document(self, change: RegulatoryChange,
                                          impact: ImpactAssessment,
                                          author: str) -> ComplianceDocument:
        """Create an implementation plan document"""

        content = self._generate_implementation_plan(change, impact)

        doc = ComplianceDocument(
            document_id=f"IMP-{change.change_id}",
            change_id=change.change_id,
            document_type='implementation_plan',
            title=f"Implementation Plan - {change.regulation_name}",
            description=f"Detailed implementation plan for {change.title}",
            content=content,
            file_path=None,
            version='1.0',
            author=author,
            review_status='draft',
            created_date=datetime.now(),
            last_modified=datetime.now(),
            reviewed_by=None,
            approved_by=None,
            retention_until=datetime.now() + timedelta(days=365*3)
        )

        doc.file_path = self._save_document(doc)
        self.db.insert_document(doc)

        return doc

    def _generate_gap_assessment(self, change: RegulatoryChange,
                                impact: ImpactAssessment) -> str:
        """Generate gap assessment document content"""

        doc_parts = []

        # Header
        doc_parts.append(f"""
# Gap Assessment Report
## {change.regulation_name}
**Change ID:** {change.change_id}
**Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}
**Compliance Deadline:** {change.deadline_for_compliance.strftime('%Y-%m-%d')}

## Executive Summary

This document identifies compliance gaps between current organizational practices and
requirements established by {change.regulation_name}. The assessment found the organization is
currently {impact.current_compliance_status} with the new regulatory requirements.

### Key Findings
- Total identified gaps: {len(impact.gaps)}
- Critical gaps: {len([g for g in impact.gaps if g['severity'] == 'high'])}
- Estimated remediation cost: ${impact.implementation_cost:,.2f}
- Estimated remediation timeline: {len(impact.implementation_phases)} phases

## Regulatory Requirements Overview

### Key Requirements
""")

        for i, requirement in enumerate(change.key_requirements, 1):
            doc_parts.append(f"\n{i}. {requirement}")

        doc_parts.append("\n\n## Compliance Gap Analysis\n")

        for gap in impact.gaps:
            doc_parts.append(f"""
### Gap: {gap['requirement']}
**Severity:** {gap['severity']}
**Current State:** {gap.get('current_implementation', 'Not implemented')}
**Gap Description:** {gap['gap_description']}
""")

        doc_parts.append("\n\n## Remediation Requirements\n")

        for remedy in impact.gap_remediation_plan:
            doc_parts.append(f"""
### Remediation: {remedy['requirement'][:50]}...
**Responsible Party:** {remedy['responsible_party']}
**Estimated Effort:** {remedy['estimated_effort']} hours
**Timeline:** {len(remedy['timeline'])} phases
""")

        return "".join(doc_parts)

    def _generate_implementation_plan(self, change: RegulatoryChange,
                                     impact: ImpactAssessment) -> str:
        """Generate implementation plan document content"""

        doc_parts = []

        doc_parts.append(f"""
# Implementation Plan
## {change.regulation_name}
**Change ID:** {change.change_id}
**Created:** {datetime.now().strftime('%Y-%m-%d')}
**Target Completion:** {change.deadline_for_compliance.strftime('%Y-%m-%d')}

## Project Overview

This document details the implementation plan to achieve full compliance with
{change.regulation_name}. The implementation will be executed in {len(impact.implementation_phases)} phases
over an estimated {impact.implementation_phases[-1]['end_date'] - datetime.now()} days.

## Implementation Phases
""")

        for i, phase in enumerate(impact.implementation_phases, 1):
            doc_parts.append(f"""
### Phase {i}: {phase['name']}
**Duration:** {phase['duration_days']} days
**Start Date:** {phase['start_date'].strftime('%Y-%m-%d')}
**End Date:** {phase['end_date'].strftime('%Y-%m-%d')}

**Tasks:**
""")
            for task in phase['tasks']:
                doc_parts.append(f"- {task}\n")

        doc_parts.append("\n## Critical Milestones\n")

        for milestone_name, milestone_date in impact.critical_milestones:
            doc_parts.append(f"- **{milestone_name}**: {milestone_date.strftime('%Y-%m-%d')}\n")

        return "".join(doc_parts)

    def _save_document(self, doc: ComplianceDocument) -> str:
        """Save document to storage"""

        change_dir = self.storage_path / doc.change_id
        change_dir.mkdir(parents=True, exist_ok=True)

        file_path = change_dir / f"{doc.document_id}_{doc.version}.md"

        with open(file_path, 'w') as f:
            f.write(doc.content)

        return str(file_path)

    def _ensure_storage_exists(self):
        """Ensure storage directory exists"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
```

## Stakeholder Communication

### Communication Strategy

```python
from enum import Enum
from typing import List

class CommunicationChannelType(Enum):
    EMAIL = "email"
    MEETING = "meeting"
    DASHBOARD = "dashboard"
    TRAINING = "training"
    DOCUMENTATION = "documentation"

@dataclass
class CommunicationPlan:
    """Structured communication plan for regulatory change"""

    change_id: str
    stakeholder_groups: List[str]
    communications: List['CommunicationItem']
    escalation_path: List[str]
    created_at: datetime

@dataclass
class CommunicationItem:
    """Individual communication activity"""

    communication_id: str
    change_id: str
    channel: CommunicationChannelType
    target_audience: str
    title: str
    content: str
    scheduled_date: datetime
    owner: str
    status: str  # 'pending', 'sent', 'completed'

class StakeholderCommunicationManager:
    """Manages communication with stakeholders"""

    def __init__(self, db_connection, email_service, meeting_service):
        self.db = db_connection
        self.email = email_service
        self.meetings = meeting_service

    def create_communication_plan(self, change: RegulatoryChange) -> CommunicationPlan:
        """Create stakeholder communication plan"""

        # Identify stakeholder groups
        groups = self._identify_stakeholder_groups(change)

        # Create communications for each group
        communications = []
        base_date = datetime.now()

        # Executive briefing
        communications.append(CommunicationItem(
            communication_id='COMM-001',
            change_id=change.change_id,
            channel=CommunicationChannelType.MEETING,
            target_audience='Executive Leadership',
            title=f"Regulatory Update: {change.title}",
            content=self._generate_executive_briefing(change),
            scheduled_date=base_date + timedelta(days=1),
            owner='Compliance Officer',
            status='pending'
        ))

        # Department updates
        for dept in change.affected_departments:
            communications.append(CommunicationItem(
                communication_id=f'COMM-DEPT-{dept}',
                change_id=change.change_id,
                channel=CommunicationChannelType.EMAIL,
                target_audience=dept,
                title=f"Regulatory Change Impact: {change.title}",
                content=self._generate_department_update(change, dept),
                scheduled_date=base_date + timedelta(days=2),
                owner='Department Manager',
                status='pending'
            ))

        # Training sessions
        communications.append(CommunicationItem(
            communication_id='COMM-TRAINING',
            change_id=change.change_id,
            channel=CommunicationChannelType.TRAINING,
            target_audience='All Affected Staff',
            title=f"Training: {change.regulation_name}",
            content=self._generate_training_content(change),
            scheduled_date=base_date + timedelta(days=20),
            owner='Training Team',
            status='pending'
        ))

        # Weekly updates
        for week in range(12):  # 12 weeks of updates
            communications.append(CommunicationItem(
                communication_id=f'COMM-UPDATE-W{week:02d}',
                change_id=change.change_id,
                channel=CommunicationChannelType.DASHBOARD,
                target_audience='All Stakeholders',
                title=f"Implementation Progress Update - Week {week}",
                content=f"Weekly progress tracking for {change.title}",
                scheduled_date=base_date + timedelta(weeks=week+1),
                owner='Project Manager',
                status='pending'
            ))

        plan = CommunicationPlan(
            change_id=change.change_id,
            stakeholder_groups=groups,
            communications=communications,
            escalation_path=['Department Manager', 'Director', 'VP', 'Executive'],
            created_at=datetime.now()
        )

        self.db.insert_communication_plan(plan)
        return plan

    def execute_communication(self, comm: CommunicationItem):
        """Execute a communication item"""

        if comm.channel == CommunicationChannelType.EMAIL:
            self.email.send(
                to=self._get_audience_emails(comm.target_audience),
                subject=comm.title,
                body=comm.content
            )

        elif comm.channel == CommunicationChannelType.MEETING:
            meeting = self.meetings.schedule(
                title=comm.title,
                description=comm.content,
                participants=self._get_audience_members(comm.target_audience),
                date=comm.scheduled_date
            )
            comm.status = 'completed'

        elif comm.channel == CommunicationChannelType.TRAINING:
            self._schedule_training_session(comm)
            comm.status = 'completed'

        elif comm.channel == CommunicationChannelType.DASHBOARD:
            self._post_to_dashboard(comm)
            comm.status = 'completed'

        self.db.update_communication(comm)

    def _generate_executive_briefing(self, change: RegulatoryChange) -> str:
        """Generate executive briefing content"""

        return f"""
# Executive Briefing: Regulatory Change

## Overview
{change.title}

**Source:** {change.jurisdiction}
**Effective Date:** {change.effective_date.strftime('%Y-%m-%d')}
**Compliance Deadline:** {change.deadline_for_compliance.strftime('%Y-%m-%d')}

## Impact Summary
- **Scope:** {change.scope.value}
- **Urgency:** {change.urgency.value}
- **Estimated Implementation Cost:** TBD
- **Affected Departments:** {', '.join(change.affected_departments)}

## Key Requirements
{chr(10).join(f'- {req}' for req in change.key_requirements[:5])}

## Recommended Actions
1. Approve implementation plan
2. Allocate resources per departmental plans
3. Establish oversight committee
4. Schedule regular progress reviews

## Next Steps
- Full impact assessment: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
- Implementation plan presentation: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}
"""
```

## Implementation Workflow

### Change Implementation Process

```python
class ChangeImplementationManager:
    """Orchestrates change implementation"""

    def __init__(self, db_connection, workflow_engine):
        self.db = db_connection
        self.workflow = workflow_engine

    def execute_change_implementation(self, change: RegulatoryChange):
        """Execute full implementation workflow"""

        # 1. Assessment phase
        impact = self._conduct_assessment(change)

        # 2. Planning phase
        workflow_id = self._develop_implementation_plan(change, impact)

        # 3. Communication phase
        self._communicate_to_stakeholders(change, impact)

        # 4. Implementation phase
        self._execute_implementation(workflow_id, change)

        # 5. Verification phase
        self._verify_compliance(change, impact)

        # 6. Monitoring phase
        self._establish_monitoring(change)

        # Update change status
        change.internal_status = 'implemented'
        self.db.update_change(change)

    def _verify_compliance(self, change: RegulatoryChange,
                          impact: ImpactAssessment):
        """Verify compliance with regulatory requirements"""

        verification_results = {
            'requirements_checked': 0,
            'requirements_compliant': 0,
            'issues_found': [],
            'verification_timestamp': datetime.now()
        }

        for requirement in change.key_requirements:
            # Check compliance
            is_compliant = self._check_requirement_compliance(requirement)

            verification_results['requirements_checked'] += 1

            if is_compliant:
                verification_results['requirements_compliant'] += 1
            else:
                verification_results['issues_found'].append({
                    'requirement': requirement,
                    'status': 'non-compliant',
                    'remediation_required': True
                })

        # Store results
        self.db.insert_verification_results(change.change_id, verification_results)

        # Notify stakeholders
        compliance_rate = (
            verification_results['requirements_compliant'] /
            verification_results['requirements_checked']
        ) * 100

        if compliance_rate < 100:
            self._escalate_compliance_issues(change, verification_results)

    def _establish_monitoring(self, change: RegulatoryChange):
        """Establish ongoing compliance monitoring"""

        monitoring_plan = {
            'change_id': change.change_id,
            'monitoring_frequency': 'quarterly',
            'controls_to_monitor': self._identify_key_controls(change),
            'key_metrics': self._define_monitoring_metrics(change),
            'review_procedures': self._define_review_procedures(change),
            'escalation_criteria': self._define_escalation_criteria(change),
            'start_date': datetime.now(),
            'monitoring_team': 'Compliance Team'
        }

        self.db.insert_monitoring_plan(monitoring_plan)
```

## Monitoring and Reporting

### Compliance Dashboard

```python
from typing import Dict, List

class ComplianceDashboard:
    """Provides real-time compliance status and reporting"""

    def __init__(self, db_connection):
        self.db = db_connection

    def get_change_status_summary(self) -> Dict:
        """Get summary of all regulatory changes"""

        all_changes = self.db.query_all_changes()

        summary = {
            'total_changes': len(all_changes),
            'by_status': {
                'identified': 0,
                'analyzing': 0,
                'planned': 0,
                'implementing': 0,
                'implemented': 0,
                'monitored': 0
            },
            'by_urgency': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'compliance_rate': 0.0,
            'upcoming_deadlines': [],
            'overdue_items': []
        }

        for change in all_changes:
            summary['by_status'][change.internal_status] += 1
            summary['by_urgency'][change.urgency.name.lower()] += 1

            if change.deadline_for_compliance <= datetime.now() + timedelta(days=30):
                summary['upcoming_deadlines'].append({
                    'change_id': change.change_id,
                    'deadline': change.deadline_for_compliance,
                    'days_remaining': (
                        change.deadline_for_compliance - datetime.now()
                    ).days
                })

            if change.deadline_for_compliance < datetime.now() and \
               change.internal_status != 'implemented':
                summary['overdue_items'].append({
                    'change_id': change.change_id,
                    'days_overdue': (
                        datetime.now() - change.deadline_for_compliance
                    ).days
                })

        # Calculate compliance rate
        implemented = summary['by_status']['implemented']
        summary['compliance_rate'] = (implemented / len(all_changes)) * 100 if all_changes else 0

        return summary

    def get_department_status(self, department: str) -> Dict:
        """Get compliance status for a specific department"""

        dept_changes = self.db.query_changes_for_department(department)

        return {
            'department': department,
            'assigned_changes': len(dept_changes),
            'completed': len([c for c in dept_changes if c.internal_status == 'implemented']),
            'in_progress': len([c for c in dept_changes if c.internal_status == 'implementing']),
            'pending': len([c for c in dept_changes if c.internal_status in ['planned', 'analyzing']]),
            'overdue': len([c for c in dept_changes if c.deadline_for_compliance < datetime.now()]),
            'resource_utilization': self._calculate_resource_utilization(dept_changes)
        }

    def generate_compliance_report(self, start_date: datetime,
                                  end_date: datetime) -> Dict:
        """Generate comprehensive compliance report"""

        report = {
            'period': f"{start_date.date()} to {end_date.date()}",
            'generated_at': datetime.now(),
            'executive_summary': {},
            'changes_processed': [],
            'completed_implementations': [],
            'pending_items': [],
            'metrics': {},
            'recommendations': []
        }

        # Query changes in period
        period_changes = self.db.query_changes_by_date_range(start_date, end_date)

        report['changes_processed'] = len(period_changes)
        report['completed_implementations'] = len(
            [c for c in period_changes if c.internal_status == 'implemented']
        )
        report['pending_items'] = len(
            [c for c in period_changes if c.internal_status != 'implemented']
        )

        # Calculate metrics
        report['metrics'] = {
            'average_days_to_implement': self._calculate_avg_implementation_time(period_changes),
            'compliance_success_rate': self._calculate_success_rate(period_changes),
            'cost_per_change': self._calculate_average_cost(period_changes),
            'total_resources_spent': self._calculate_total_resources(period_changes)
        }

        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(period_changes)

        return report
```

## Best Practices

### Change Management Excellence

1. **Early Detection**
   - Monitor multiple regulatory sources
   - Use automated alerts for new regulations
   - Establish relationships with regulatory contacts
   - Participate in industry associations

2. **Rapid Assessment**
   - Use standardized assessment templates
   - Build cross-functional assessment teams
   - Leverage past implementation patterns
   - Document assumptions and dependencies

3. **Clear Accountability**
   - Assign single owner per requirement
   - Define clear responsibility matrices
   - Establish escalation procedures
   - Track individual performance

4. **Stakeholder Engagement**
   - Communicate early and often
   - Tailor messages to audience
   - Provide training and resources
   - Gather feedback and adjust

5. **Documentation and Evidence**
   - Document all decisions
   - Maintain implementation records
   - Keep evidence of compliance
   - Preserve communication records

6. **Testing and Validation**
   - Test changes in controlled environment
   - Validate all system modifications
   - Verify control effectiveness
   - Conduct user acceptance testing

7. **Continuous Monitoring**
   - Establish baseline metrics
   - Monitor key controls regularly
   - Track compliance metrics
   - Adjust controls as needed

## Conclusion

Effective regulatory change management requires:
- Systematic detection and assessment processes
- Clear accountability and ownership
- Comprehensive stakeholder communication
- Well-documented implementation plans
- Rigorous verification procedures
- Continuous monitoring and optimization

Organizations that excel at regulatory change management gain competitive advantages through faster compliance, reduced risk, and more efficient resource utilization.
