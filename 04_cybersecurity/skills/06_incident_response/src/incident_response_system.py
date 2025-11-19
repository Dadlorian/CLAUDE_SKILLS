"""
Incident Response Management System
Orchestrate security incident response workflow
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentStatus(Enum):
    """Incident lifecycle status"""
    NEW = "New"
    INVESTIGATING = "Investigating"
    CONTAINED = "Contained"
    ERADICATED = "Eradicated"
    RECOVERING = "Recovering"
    CLOSED = "Closed"


@dataclass
class Incident:
    """Security incident"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: datetime
    assigned_to: str
    affected_systems: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    timeline: List[Dict] = field(default_factory=list)
    containment_actions: List[str] = field(default_factory=list)
    resolution: Optional[str] = None


class IncidentResponseSystem:
    """
    Incident Response Management

    Features:
    - Incident tracking
    - Automated playbooks
    - Timeline management
    - Evidence collection
    - Post-incident analysis
    """

    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.playbooks: Dict[str, List[str]] = self._load_playbooks()

    def _load_playbooks(self) -> Dict[str, List[str]]:
        """Load incident response playbooks"""
        return {
            'malware': [
                'Isolate affected system',
                'Capture memory dump',
                'Collect network traffic',
                'Run antimalware scan',
                'Analyze malware sample',
                'Identify patient zero',
                'Remediate all affected systems',
                'Update signatures'
            ],
            'data_breach': [
                'Contain the breach',
                'Assess scope of data exposure',
                'Preserve evidence',
                'Notify stakeholders',
                'Comply with breach notification laws',
                'Remediate vulnerability',
                'Implement additional controls'
            ],
            'ransomware': [
                'Isolate infected systems',
                'Identify ransomware variant',
                'Check for decryption tools',
                'Restore from backups',
                'DO NOT pay ransom',
                'Report to law enforcement',
                'Implement anti-ransomware controls'
            ],
            'phishing': [
                'Quarantine phishing emails',
                'Block sender domain',
                'Reset compromised credentials',
                'Check for unauthorized access',
                'User awareness notification',
                'Update email filters'
            ]
        }

    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        assigned_to: str,
        affected_systems: List[str] = None
    ) -> Incident:
        """Create new security incident"""
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.NEW,
            detected_at=datetime.now(),
            assigned_to=assigned_to,
            affected_systems=affected_systems or []
        )

        self.incidents[incident_id] = incident

        # Add to timeline
        self._add_timeline_event(
            incident_id,
            "Incident created",
            f"Severity: {severity.value}, Assigned to: {assigned_to}"
        )

        return incident

    def update_status(self, incident_id: str, new_status: IncidentStatus):
        """Update incident status"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        old_status = incident.status
        incident.status = new_status

        self._add_timeline_event(
            incident_id,
            "Status updated",
            f"Changed from {old_status.value} to {new_status.value}"
        )

    def add_containment_action(self, incident_id: str, action: str):
        """Add containment action"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]
        incident.containment_actions.append(action)

        self._add_timeline_event(
            incident_id,
            "Containment action",
            action
        )

    def _add_timeline_event(self, incident_id: str, event_type: str, description: str):
        """Add event to incident timeline"""
        if incident_id not in self.incidents:
            return

        incident = self.incidents[incident_id]
        incident.timeline.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'description': description
        })

    def get_playbook(self, incident_type: str) -> List[str]:
        """Get response playbook for incident type"""
        return self.playbooks.get(incident_type, [])

    def escalate_incident(self, incident_id: str):
        """Escalate incident severity"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]

        if incident.severity == IncidentSeverity.LOW:
            incident.severity = IncidentSeverity.MEDIUM
        elif incident.severity == IncidentSeverity.MEDIUM:
            incident.severity = IncidentSeverity.HIGH
        elif incident.severity == IncidentSeverity.HIGH:
            incident.severity = IncidentSeverity.CRITICAL

        self._add_timeline_event(
            incident_id,
            "Incident escalated",
            f"New severity: {incident.severity.value}"
        )

    def generate_incident_report(self, incident_id: str) -> Dict:
        """Generate detailed incident report"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")

        incident = self.incidents[incident_id]

        return {
            'incident_id': incident.incident_id,
            'title': incident.title,
            'description': incident.description,
            'severity': incident.severity.value,
            'status': incident.status.value,
            'detected_at': incident.detected_at.isoformat(),
            'assigned_to': incident.assigned_to,
            'affected_systems': incident.affected_systems,
            'containment_actions': incident.containment_actions,
            'timeline': incident.timeline,
            'resolution': incident.resolution
        }


if __name__ == "__main__":
    irs = IncidentResponseSystem()

    # Create incident
    incident = irs.create_incident(
        title="Malware Detected on Workstation",
        description="Trojan.Generic detected on WS-001",
        severity=IncidentSeverity.HIGH,
        assigned_to="SOC Team",
        affected_systems=["WS-001"]
    )

    print(f"Incident created: {incident.incident_id}")

    # Get playbook
    playbook = irs.get_playbook('malware')
    print(f"\nResponse steps: {len(playbook)}")

    # Update status
    irs.update_status(incident.incident_id, IncidentStatus.INVESTIGATING)
    print(f"Status: {incident.status.value}")
