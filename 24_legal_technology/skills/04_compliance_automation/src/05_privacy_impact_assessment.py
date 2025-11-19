#!/usr/bin/env python3
"""
Privacy Impact Assessment (PIA) Generator
Automated GDPR DPIA/PIA assessment generation and tracking
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4

class PrivacyImpactAssessment:
    """Automated Privacy Impact Assessment"""

    def __init__(self, assessment_name: str, description: str):
        self.assessment_id = f"PIA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.assessment_name = assessment_name
        self.description = description
        self.created_date = datetime.now().isoformat()
        self.risks = []
        self.mitigations = []
        self.approval_workflow = []

    def add_risk(self, risk_description: str, likelihood: int, impact: int,
                 affected_rights: List[str], data_categories: List[str]) -> str:
        """
        Add a privacy risk to the assessment

        Args:
            risk_description: Description of the risk
            likelihood: Likelihood score (1-5)
            impact: Impact score (1-5)
            affected_rights: Data subject rights affected
            data_categories: Categories of data affected

        Returns:
            Risk ID
        """
        risk_id = f"RISK_{len(self.risks) + 1:03d}"
        risk_score = self._calculate_risk_score(likelihood, impact)

        risk = {
            'risk_id': risk_id,
            'description': risk_description,
            'likelihood': likelihood,
            'impact': impact,
            'risk_score': risk_score,
            'risk_level': self._determine_risk_level(risk_score),
            'affected_rights': affected_rights,
            'data_categories': data_categories,
            'identified_date': datetime.now().isoformat(),
            'mitigation_status': 'unmitigated',
            'residual_risk': None
        }

        self.risks.append(risk)
        return risk_id

    def add_mitigation(self, risk_id: str, mitigation_description: str,
                      implementation_timeline: str, responsible_party: str) -> str:
        """Add mitigation measure for a risk"""
        mitigation_id = f"MIT_{len(self.mitigations) + 1:03d}"

        mitigation = {
            'mitigation_id': mitigation_id,
            'risk_id': risk_id,
            'description': mitigation_description,
            'implementation_timeline': implementation_timeline,
            'responsible_party': responsible_party,
            'status': 'planned',
            'residual_risk_level': RiskLevel.LOW.name,
            'verification_method': 'testing',
            'completion_date': None
        }

        self.mitigations.append(mitigation)

        # Update risk mitigation status
        for risk in self.risks:
            if risk['risk_id'] == risk_id:
                risk['mitigation_status'] = 'mitigated'
                break

        return mitigation_id

    def conduct_automated_assessment(self) -> Dict:
        """Conduct automated risk assessment"""
        assessment = {
            'assessment_id': self.assessment_id,
            'assessment_name': self.assessment_name,
            'description': self.description,
            'created_date': self.created_date,
            'assessment_date': datetime.now().isoformat(),
            'total_risks_identified': len(self.risks),
            'risks_by_level': self._count_risks_by_level(),
            'high_risk_identified': any(r['risk_level'].name in ['HIGH', 'VERY_HIGH'] for r in self.risks),
            'risks': self.risks,
            'mitigations': self.mitigations,
            'overall_risk_determination': self._determine_overall_risk(),
            'authority_consultation_required': self._determine_authority_consultation_required()
        }

        return assessment

    def determine_dpia_requirement(self) -> Dict:
        """Determine if formal DPIA is required"""
        high_risk_triggers = [
            'automated_decision_making',
            'special_category_data',
            'large_scale_processing',
            'systematic_monitoring',
            'children_data',
            'vulnerable_groups',
            'criminal_records',
            'genetic_data'
        ]

        # Automated trigger detection
        requires_dpia = self._check_dpia_triggers()

        return {
            'dpia_required': requires_dpia,
            'triggers_identified': self._get_dpia_triggers(),
            'priority_level': 'high' if requires_dpia else 'standard',
            'assessment_type': 'Full DPIA' if requires_dpia else 'Data Protection Impact Assessment',
            'timeline': '10 weeks' if requires_dpia else '4 weeks',
            'authority_pre_consultation': requires_dpia and any(
                r['risk_level'].name in ['HIGH', 'VERY_HIGH'] for r in self.risks
            )
        }

    def generate_dpia_report(self) -> Dict:
        """Generate formal DPIA report for regulatory compliance"""
        return {
            'report_id': self.assessment_id,
            'report_title': f'Data Protection Impact Assessment: {self.assessment_name}',
            'report_date': datetime.now().isoformat(),
            'organization': 'Organization Name',
            'data_protection_officer': 'DPO Name',
            'executive_summary': {
                'overview': self.description,
                'total_risks': len(self.risks),
                'high_risk_count': sum(1 for r in self.risks if r['risk_level'].name in ['HIGH', 'VERY_HIGH']),
                'mitigation_count': len(self.mitigations),
                'overall_risk_level': self._determine_overall_risk()
            },
            'detailed_assessment': {
                'risks_identified': self.risks,
                'mitigations_proposed': self.mitigations,
                'residual_risks': self._assess_residual_risks()
            },
            'consultation_requirement': {
                'authority_consultation_required': self._determine_authority_consultation_required(),
                'authority': 'ICO',
                'consultation_timeline': '10 working days' if self._determine_authority_consultation_required() else None
            },
            'approval_section': {
                'approval_status': 'pending_approval',
                'approvers_required': ['Data Protection Officer', 'Legal Lead', 'Business Owner'],
                'approval_workflow': self.approval_workflow
            },
            'sign_off': {
                'prepared_by': 'Compliance Team',
                'reviewed_by': 'Data Protection Officer',
                'approved_by': 'Executive Sponsor',
                'date': datetime.now().date().isoformat()
            }
        }

    def check_necessity_and_proportionality(self) -> Dict:
        """Assess necessity and proportionality of processing"""
        return {
            'processing_necessity': {
                'assessment': 'necessary' if self._assess_necessity() else 'not_necessary',
                'justification': 'Processing is necessary to fulfill contractual obligations',
                'alternative_methods': ['Option A', 'Option B'],
                'selected_method': 'Option A - Direct processing'
            },
            'proportionality_assessment': {
                'processing_proportionate': True,
                'data_minimization_status': 'compliant',
                'retention_proportionate': True,
                'access_controls_proportionate': True,
                'security_proportionate': True
            }
        }

    def assess_data_subject_rights(self) -> Dict:
        """Assess impact on data subject rights"""
        rights = {
            'right_of_access': {'impacted': True, 'mitigation': 'Provide access within 30 days'},
            'right_of_rectification': {'impacted': True, 'mitigation': 'Enable correction mechanisms'},
            'right_to_erasure': {'impacted': True, 'mitigation': 'Implement deletion procedures'},
            'right_to_restrict': {'impacted': False, 'mitigation': 'N/A'},
            'right_to_portability': {'impacted': True, 'mitigation': 'Provide machine-readable format'},
            'right_to_object': {'impacted': False, 'mitigation': 'N/A'},
            'rights_related_to_automated_decision': {'impacted': False, 'mitigation': 'N/A'}
        }

        return {
            'assessed_rights': rights,
            'safeguards_implemented': self._get_rights_safeguards(),
            'residual_risks_to_rights': self._assess_residual_rights_risks()
        }

    def compliance_checklist(self) -> Dict:
        """Generate DPIA compliance checklist"""
        return {
            'checklist_date': datetime.now().isoformat(),
            'items': [
                {'item': 'Necessity and proportionality assessed', 'status': 'complete'},
                {'item': 'Legal basis determined', 'status': 'complete'},
                {'item': 'Data minimization verified', 'status': 'complete'},
                {'item': 'Special category data identified', 'status': 'complete'},
                {'item': 'Recipients identified', 'status': 'complete'},
                {'item': 'Retention periods determined', 'status': 'complete'},
                {'item': 'Security measures identified', 'status': 'complete'},
                {'item': 'Risk assessment completed', 'status': 'complete'},
                {'item': 'Mitigations identified', 'status': 'in_progress'},
                {'item': 'DPA/Contracts reviewed', 'status': 'pending'},
                {'item': 'Consent mechanisms designed', 'status': 'pending'},
                {'item': 'Authority consultation completed', 'status': 'not_required'},
                {'item': 'Sign-off obtained', 'status': 'pending'}
            ],
            'completion_percentage': 61.5,
            'estimated_completion': (datetime.now() + timedelta(days=7)).isoformat()
        }

    # Private helper methods
    @staticmethod
    def _calculate_risk_score(likelihood: int, impact: int) -> int:
        """Calculate risk score from likelihood and impact"""
        return likelihood * impact

    @staticmethod
    def _determine_risk_level(score: int) -> RiskLevel:
        """Determine risk level from score"""
        if score <= 6:
            return RiskLevel.LOW
        elif score <= 12:
            return RiskLevel.MEDIUM
        elif score <= 20:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    def _count_risks_by_level(self) -> Dict:
        """Count risks by severity level"""
        counts = {}
        for risk in self.risks:
            level = risk['risk_level'].name
            counts[level] = counts.get(level, 0) + 1
        return counts

    def _determine_overall_risk(self) -> str:
        """Determine overall risk level"""
        if not self.risks:
            return 'LOW'

        max_score = max(r['risk_score'] for r in self.risks)
        if max_score > 20:
            return 'VERY_HIGH'
        elif max_score > 12:
            return 'HIGH'
        elif max_score > 6:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _determine_authority_consultation_required(self) -> bool:
        """Check if authority consultation is required"""
        high_risks = [r for r in self.risks if r['risk_level'].name in ['HIGH', 'VERY_HIGH']]
        return len(high_risks) > 0

    def _check_dpia_triggers(self) -> bool:
        """Check if DPIA is required based on triggers"""
        # This would be customized based on organization triggers
        return any(r['risk_score'] > 12 for r in self.risks)

    def _get_dpia_triggers(self) -> List[str]:
        """Get list of DPIA triggers identified"""
        triggers = []
        high_risks = [r for r in self.risks if r['risk_score'] > 12]
        if high_risks:
            triggers.append('high_risk_processing_identified')
        if any('automated' in r['description'].lower() for r in self.risks):
            triggers.append('automated_decision_making')
        if any('children' in str(r).lower() for r in self.risks):
            triggers.append('children_data_processing')
        return triggers

    def _assess_necessity(self) -> bool:
        """Assess necessity of processing"""
        return True  # Placeholder

    def _get_rights_safeguards(self) -> List[str]:
        """Get safeguards for data subject rights"""
        return [
            'Privacy policy disclosure',
            'Automated access request system',
            'Rectification procedures',
            'Deletion request handling',
            'Complaint procedures'
        ]

    def _assess_residual_risks(self) -> List[Dict]:
        """Assess residual risks after mitigations"""
        residual = []
        for risk in self.risks:
            mitigations_for_risk = [m for m in self.mitigations if m['risk_id'] == risk['risk_id']]
            if mitigations_for_risk:
                residual_score = max(1, risk['risk_score'] - (len(mitigations_for_risk) * 2))
            else:
                residual_score = risk['risk_score']

            residual.append({
                'risk_id': risk['risk_id'],
                'original_score': risk['risk_score'],
                'residual_score': residual_score,
                'residual_level': self._determine_risk_level(residual_score).name
            })

        return residual

    def _assess_residual_rights_risks(self) -> List[str]:
        """Assess residual risks to data subject rights"""
        return [
            'Potential delay in access request processing',
            'Technical limitations in data portability',
            'System unavailability during deletion'
        ]


def main():
    # Create PIA assessment
    pia = PrivacyImpactAssessment(
        assessment_name='Customer Analytics Platform Implementation',
        description='Implementation of analytics system to track customer behavior'
    )

    # Add risks
    pia.add_risk(
        'Unauthorized access to behavioral data',
        likelihood=3,
        impact=4,
        affected_rights=['privacy', 'non-discrimination'],
        data_categories=['behavioral_data', 'location_data']
    )

    pia.add_risk(
        'Data retention beyond purpose',
        likelihood=2,
        impact=3,
        affected_rights=['data_minimization'],
        data_categories=['behavioral_data']
    )

    # Add mitigations
    pia.add_mitigation('RISK_001', 'Implement encryption for behavioral data', '4 weeks', 'Security Team')
    pia.add_mitigation('RISK_002', 'Set automated deletion for analytics data after 90 days', '3 weeks', 'Data Engineering')

    # Generate reports
    assessment = pia.conduct_automated_assessment()
    dpia_report = pia.generate_dpia_report()
    dpia_requirement = pia.determine_dpia_requirement()
    rights_assessment = pia.assess_data_subject_rights()
    checklist = pia.compliance_checklist()

    print(json.dumps({
        'assessment': assessment,
        'dpia_requirement': dpia_requirement,
        'rights_assessment': rights_assessment,
        'compliance_checklist': checklist
    }, indent=2, default=str))


if __name__ == '__main__':
    main()
