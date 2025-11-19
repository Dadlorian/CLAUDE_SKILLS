"""
Compliance and Governance Framework
Track and manage security compliance across multiple frameworks
"""

from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance control status"""
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PARTIALLY_COMPLIANT = "Partially Compliant"
    NOT_APPLICABLE = "Not Applicable"
    NOT_ASSESSED = "Not Assessed"


@dataclass
class ComplianceControl:
    """Compliance control"""
    control_id: str
    framework: str
    title: str
    description: str
    status: ComplianceStatus
    evidence: List[str]
    last_assessment: datetime
    assigned_to: str


class ComplianceFramework:
    """
    Compliance Management System

    Features:
    - Multi-framework support (PCI-DSS, HIPAA, SOC 2, ISO 27001)
    - Control tracking
    - Evidence collection
    - Compliance reporting
    - Gap analysis
    """

    def __init__(self):
        self.controls: Dict[str, ComplianceControl] = {}
        self.frameworks: Dict[str, List[str]] = self._initialize_frameworks()

    def _initialize_frameworks(self) -> Dict[str, List[str]]:
        """Initialize compliance frameworks"""
        return {
            'PCI-DSS': [
                'Install and maintain firewall',
                'Do not use vendor defaults',
                'Protect stored cardholder data',
                'Encrypt transmission of cardholder data',
                'Use and regularly update antivirus',
                'Develop secure systems and applications',
                'Restrict access by business need-to-know',
                'Assign unique ID to each person',
                'Restrict physical access to cardholder data',
                'Track and monitor all access',
                'Regularly test security systems',
                'Maintain information security policy'
            ],
            'HIPAA': [
                'Access Control (164.312(a)(1))',
                'Audit Controls (164.312(b))',
                'Integrity (164.312(c)(1))',
                'Person or Entity Authentication (164.312(d))',
                'Transmission Security (164.312(e)(1))'
            ],
            'SOC2': [
                'CC6.1 - Logical and physical access controls',
                'CC6.2 - Access provisioning and termination',
                'CC6.3 - Removal or restriction of access',
                'CC6.6 - Logical access control vulnerabilities',
                'CC7.1 - System monitoring',
                'CC7.2 - System security events'
            ],
            'ISO27001': [
                'A.5 Information Security Policies',
                'A.6 Organization of Information Security',
                'A.7 Human Resource Security',
                'A.8 Asset Management',
                'A.9 Access Control',
                'A.10 Cryptography',
                'A.11 Physical and Environmental Security',
                'A.12 Operations Security',
                'A.13 Communications Security',
                'A.14 System Acquisition, Development and Maintenance',
                'A.15 Supplier Relationships',
                'A.16 Information Security Incident Management',
                'A.17 Business Continuity Management',
                'A.18 Compliance'
            ]
        }

    def assess_control(
        self,
        control_id: str,
        framework: str,
        status: ComplianceStatus,
        evidence: List[str],
        assigned_to: str
    ):
        """Assess compliance control"""
        control = ComplianceControl(
            control_id=control_id,
            framework=framework,
            title=self._get_control_title(framework, control_id),
            description="",
            status=status,
            evidence=evidence,
            last_assessment=datetime.now(),
            assigned_to=assigned_to
        )

        self.controls[control_id] = control

    def _get_control_title(self, framework: str, control_id: str) -> str:
        """Get control title from framework"""
        if framework in self.frameworks:
            controls = self.frameworks[framework]
            for i, control in enumerate(controls):
                if str(i+1) in control_id or control.startswith(control_id):
                    return control
        return "Unknown Control"

    def get_compliance_score(self, framework: str) -> Dict:
        """Calculate compliance score for framework"""
        framework_controls = [
            c for c in self.controls.values()
            if c.framework == framework
        ]

        if not framework_controls:
            return {
                'framework': framework,
                'total_controls': 0,
                'score': 0
            }

        compliant = sum(
            1 for c in framework_controls
            if c.status == ComplianceStatus.COMPLIANT
        )

        total = len(framework_controls)
        score = (compliant / total * 100) if total > 0 else 0

        return {
            'framework': framework,
            'total_controls': total,
            'compliant': compliant,
            'non_compliant': sum(
                1 for c in framework_controls
                if c.status == ComplianceStatus.NON_COMPLIANT
            ),
            'partially_compliant': sum(
                1 for c in framework_controls
                if c.status == ComplianceStatus.PARTIALLY_COMPLIANT
            ),
            'score': round(score, 2)
        }

    def identify_gaps(self, framework: str) -> List[ComplianceControl]:
        """Identify compliance gaps"""
        return [
            control for control in self.controls.values()
            if control.framework == framework and
            control.status in [ComplianceStatus.NON_COMPLIANT,
                             ComplianceStatus.PARTIALLY_COMPLIANT]
        ]

    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        frameworks_assessed = set(c.framework for c in self.controls.values())

        framework_scores = {}
        for framework in frameworks_assessed:
            framework_scores[framework] = self.get_compliance_score(framework)

        return {
            'report_date': datetime.now().isoformat(),
            'frameworks_assessed': list(frameworks_assessed),
            'framework_scores': framework_scores,
            'total_controls_assessed': len(self.controls),
            'overall_compliance_rate': self._calculate_overall_compliance()
        }

    def _calculate_overall_compliance(self) -> float:
        """Calculate overall compliance rate across all frameworks"""
        if not self.controls:
            return 0.0

        compliant = sum(
            1 for c in self.controls.values()
            if c.status == ComplianceStatus.COMPLIANT
        )

        return round((compliant / len(self.controls)) * 100, 2)


if __name__ == "__main__":
    cf = ComplianceFramework()

    # Assess controls
    cf.assess_control(
        control_id="PCI-1",
        framework="PCI-DSS",
        status=ComplianceStatus.COMPLIANT,
        evidence=["Firewall config review", "Penetration test results"],
        assigned_to="Security Team"
    )

    cf.assess_control(
        control_id="PCI-3",
        framework="PCI-DSS",
        status=ComplianceStatus.NON_COMPLIANT,
        evidence=[],
        assigned_to="Development Team"
    )

    # Get compliance score
    score = cf.get_compliance_score("PCI-DSS")
    print(f"PCI-DSS Compliance: {score['score']}%")

    # Identify gaps
    gaps = cf.identify_gaps("PCI-DSS")
    print(f"Compliance gaps: {len(gaps)}")
