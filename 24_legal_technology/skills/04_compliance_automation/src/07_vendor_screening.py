#!/usr/bin/env python3
"""
Vendor Screening and Due Diligence Automation
Automated vendor risk assessment and compliance verification
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from enum import Enum

class VendorRiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class VendorScreeningEngine:
    """Automated vendor screening and risk assessment"""

    def __init__(self):
        self.screening_results = {}
        self.vendor_registry = {}
        self.screening_queries = {
            'sanctions_list': ['OFAC', 'UN', 'EU'],
            'pep_database': ['Reuters', 'Commercial PEP DB'],
            'regulatory_status': ['Company Registry', 'Financial Authority']
        }

    def conduct_vendor_screening(self, vendor_name: str, vendor_id: str) -> Dict:
        """
        Conduct automated vendor screening

        Args:
            vendor_name: Name of vendor company
            vendor_id: Unique vendor identifier

        Returns:
            Screening results and risk assessment
        """
        screening_id = f"SCREEN_{vendor_id}_{datetime.now().strftime('%Y%m%d')}"

        # Check sanctions lists
        sanctions_check = self._check_sanctions_lists(vendor_name)

        # Check PEP databases
        pep_check = self._check_pep_database(vendor_name)

        # Check regulatory status
        regulatory_check = self._check_regulatory_status(vendor_name)

        # Check adverse media
        adverse_media = self._check_adverse_media(vendor_name)

        # Calculate overall risk
        risk_score, risk_level = self._calculate_vendor_risk(
            sanctions_check, pep_check, regulatory_check, adverse_media
        )

        return {
            'screening_id': screening_id,
            'vendor_name': vendor_name,
            'vendor_id': vendor_id,
            'screening_date': datetime.now().isoformat(),
            'screening_results': {
                'sanctions_list_match': sanctions_check['matched'],
                'pep_match': pep_check['matched'],
                'regulatory_issues': regulatory_check['issues_found'],
                'adverse_media': adverse_media['articles_found']
            },
            'risk_score': risk_score,
            'risk_level': risk_level.value,
            'proceed_with_vendor': risk_level != VendorRiskLevel.CRITICAL,
            'conditions': self._get_vendor_conditions(risk_level),
            'next_review_date': (datetime.now() + timedelta(days=365)).isoformat()
        }

    def collect_due_diligence_questionnaire(self, vendor_id: str, risk_level: str) -> Dict:
        """Generate due diligence questionnaire based on vendor risk"""
        if risk_level == VendorRiskLevel.CRITICAL.value:
            questionnaire = self._generate_extended_questionnaire()
        elif risk_level == VendorRiskLevel.HIGH.value:
            questionnaire = self._generate_standard_questionnaire()
        else:
            questionnaire = self._generate_basic_questionnaire()

        return {
            'questionnaire_id': f"Q_{vendor_id}_{datetime.now().strftime('%Y%m%d')}",
            'vendor_id': vendor_id,
            'risk_level': risk_level,
            'questions': questionnaire,
            'response_deadline': (datetime.now() + timedelta(days=14)).isoformat(),
            'required_documents': self._get_required_documents(risk_level)
        }

    def assess_data_processing_suitability(self, vendor_profile: Dict) -> Dict:
        """Assess vendor suitability for data processing"""
        criteria = {
            'data_protection_certification': vendor_profile.get('iso_27001', False),
            'soc_2_certification': vendor_profile.get('soc_2', False),
            'privacy_policy_exists': vendor_profile.get('privacy_policy', False),
            'data_processing_agreement': vendor_profile.get('dpa_available', False),
            'sub_processor_management': vendor_profile.get('sub_processor_mgmt', False),
            'security_audit_frequency': vendor_profile.get('audit_frequency', 'never'),
            'breach_history': vendor_profile.get('breach_incidents', 0),
            'data_retention_policy': vendor_profile.get('retention_policy', False),
            'data_deletion_capability': vendor_profile.get('deletion_capability', False),
            'international_transfers': vendor_profile.get('international_transfers', False)
        }

        suitability_score = self._calculate_suitability_score(criteria)

        return {
            'vendor_id': vendor_profile.get('vendor_id'),
            'data_processing_suitable': suitability_score >= 70,
            'suitability_score': suitability_score,
            'assessment_criteria': criteria,
            'gap_items': self._identify_gaps(criteria),
            'remediation_timeline': '30 days' if self._identify_gaps(criteria) else None
        }

    def generate_vendor_risk_report(self, vendor_id: str, screening_result: Dict) -> Dict:
        \"\"\"Generate comprehensive vendor risk report\"\"\"\n        return {\n            'report_id': f\"VR_{vendor_id}_{datetime.now().strftime('%Y%m%d_%H%M')}\",\n            'vendor_id': vendor_id,\n            'report_date': datetime.now().isoformat(),\n            'executive_summary': {\n                'vendor_name': screening_result.get('vendor_name'),\n                'overall_risk_level': screening_result.get('risk_level'),\n                'recommendation': 'Proceed' if screening_result.get('proceed_with_vendor') else 'Do not proceed',\n                'screening_date': screening_result.get('screening_date')\n            },\n            'detailed_findings': screening_result.get('screening_results'),\n            'conditions_for_engagement': screening_result.get('conditions'),\n            'monitoring_requirements': self._get_monitoring_requirements(screening_result.get('risk_level')),\n            'due_diligence_schedule': self._get_due_diligence_schedule(screening_result.get('risk_level')),\n            'approvals_required': self._get_approvals_required(screening_result.get('risk_level')),\n            'next_review': screening_result.get('next_review_date')\n        }\n\n    def monitor_vendor_compliance(self, vendor_id: str) -> Dict:\n        \"\"\"Ongoing monitoring of vendor compliance\"\"\"\n        return {\n            'monitoring_id': f\"MON_{vendor_id}_{datetime.now().strftime('%Y%m%d')}\",\n            'vendor_id': vendor_id,\n            'monitoring_activities': [\n                {'activity': 'Quarterly financial check', 'last_completed': (datetime.now() - timedelta(days=30)).isoformat(), 'status': 'due'},\n                {'activity': 'Regulatory status update', 'last_completed': (datetime.now() - timedelta(days=60)).isoformat(), 'status': 'overdue'},\n                {'activity': 'Adverse media review', 'last_completed': (datetime.now() - timedelta(days=7)).isoformat(), 'status': 'current'},\n                {'activity': 'Security certification verification', 'last_completed': (datetime.now() - timedelta(days=90)).isoformat(), 'status': 'due'}\n            ],\n            'monitoring_frequency': 'quarterly',\n            'next_monitoring_date': (datetime.now() + timedelta(days=30)).isoformat()\n        }\n\n    def manage_vendor_offboarding(self, vendor_id: str) -> Dict:\n        \"\"\"Manage vendor offboarding process\"\"\"\n        return {\n            'offboarding_id': f\"OFF_{vendor_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}\",\n            'vendor_id': vendor_id,\n            'offboarding_date': datetime.now().isoformat(),\n            'offboarding_checklist': [\n                {'task': 'Notify vendor of termination', 'status': 'pending', 'due_date': (datetime.now() + timedelta(days=1)).isoformat()},\n                {'task': 'Request data return/deletion schedule', 'status': 'pending', 'due_date': (datetime.now() + timedelta(days=3)).isoformat()},\n                {'task': 'Disable system access', 'status': 'pending', 'due_date': (datetime.now() + timedelta(days=1)).isoformat()},\n                {'task': 'Collect vendor assets', 'status': 'pending', 'due_date': (datetime.now() + timedelta(days=5)).isoformat()},\n                {'task': 'Verify data deletion', 'status': 'pending', 'due_date': (datetime.now() + timedelta(days=30)).isoformat()},\n                {'task': 'Final security review', 'status': 'pending', 'due_date': (datetime.now() + timedelta(days=30)).isoformat()}\n            ],\n            'data_handling': {\n                'data_to_be_returned': True,\n                'return_method': 'Secure encrypted transfer',\n                'verification_required': True,\n                'timeline_days': 30\n            }\n        }\n\n    # Private helper methods\n    @staticmethod\n    def _check_sanctions_lists(vendor_name: str) -> Dict:\n        \"\"\"Check vendor against sanctions lists\"\"\"\n        # Placeholder - would integrate with actual sanctions list APIs\n        return {\n            'matched': False,\n            'sources_checked': ['OFAC', 'UN', 'EU'],\n            'last_checked': datetime.now().isoformat()\n        }\n\n    @staticmethod\n    def _check_pep_database(vendor_name: str) -> Dict:\n        \"\"\"Check for politically exposed persons\"\"\"\n        return {\n            'matched': False,\n            'sources_checked': ['Reuters PEP', 'Commercial DB'],\n            'beneficial_owners_checked': True,\n            'last_checked': datetime.now().isoformat()\n        }\n\n    @staticmethod\n    def _check_regulatory_status(vendor_name: str) -> Dict:\n        \"\"\"Check regulatory compliance status\"\"\"\n        return {\n            'issues_found': False,\n            'license_status': 'valid',\n            'violations': [],\n            'last_checked': datetime.now().isoformat()\n        }\n\n    @staticmethod\n    def _check_adverse_media(vendor_name: str) -> Dict:\n        \"\"\"Check for adverse media mentions\"\"\"\n        return {\n            'articles_found': 0,\n            'negative_articles': 0,\n            'sources_monitored': ['News', 'Social Media', 'Industry Reports'],\n            'last_checked': datetime.now().isoformat()\n        }\n\n    @staticmethod\n    def _calculate_vendor_risk(sanctions: Dict, pep: Dict, regulatory: Dict, media: Dict) -> Tuple[int, VendorRiskLevel]:\n        \"\"\"Calculate overall vendor risk score\"\"\"\n        risk_score = 0\n\n        if sanctions['matched']:\n            risk_score += 40\n        if pep['matched']:\n            risk_score += 30\n        if regulatory['issues_found']:\n            risk_score += 20\n        if media['negative_articles'] > 3:\n            risk_score += 10\n\n        if risk_score >= 40:\n            risk_level = VendorRiskLevel.CRITICAL\n        elif risk_score >= 25:\n            risk_level = VendorRiskLevel.HIGH\n        elif risk_score >= 10:\n            risk_level = VendorRiskLevel.MEDIUM\n        else:\n            risk_level = VendorRiskLevel.LOW\n\n        return risk_score, risk_level\n\n    @staticmethod\n    def _get_vendor_conditions(risk_level: VendorRiskLevel) -> List[str]:\n        \"\"\"Get engagement conditions based on risk level\"\"\"\n        conditions = {\n            VendorRiskLevel.CRITICAL: ['Do not engage'],\n            VendorRiskLevel.HIGH: [\n                'Enhanced due diligence required',\n                'Executive approval mandatory',\n                'Enhanced monitoring required',\n                'Limited data access'\n            ],\n            VendorRiskLevel.MEDIUM: [\n                'Standard due diligence required',\n                'Manager approval required',\n                'Quarterly monitoring'\n            ],\n            VendorRiskLevel.LOW: [\n                'Basic due diligence',\n                'Annual monitoring'\n            ]\n        }\n        return conditions.get(risk_level, [])\n\n    @staticmethod\n    def _generate_extended_questionnaire() -> List[Dict]:\n        \"\"\"Generate extended questionnaire for high-risk vendors\"\"\"\n        return [\n            {'id': 1, 'question': 'Describe your data security measures', 'required': True},\n            {'id': 2, 'question': 'Provide list of beneficial owners', 'required': True},\n            {'id': 3, 'question': 'Describe your sub-processor policy', 'required': True},\n            {'id': 4, 'question': 'Provide recent audit report', 'required': True},\n            {'id': 5, 'question': 'Describe your incident response process', 'required': True}\n        ]\n\n    @staticmethod\n    def _generate_standard_questionnaire() -> List[Dict]:\n        \"\"\"Generate standard questionnaire\"\"\"\n        return [\n            {'id': 1, 'question': 'Do you have data protection certifications?', 'required': True},\n            {'id': 2, 'question': 'Describe your security measures', 'required': True},\n            {'id': 3, 'question': 'Do you have DPA capability?', 'required': True}\n        ]\n\n    @staticmethod\n    def _generate_basic_questionnaire() -> List[Dict]:\n        \"\"\"Generate basic questionnaire\"\"\"\n        return [\n            {'id': 1, 'question': 'Do you process personal data?', 'required': True},\n            {'id': 2, 'question': 'Do you have basic security measures?', 'required': False}\n        ]\n\n    @staticmethod\n    def _get_required_documents(risk_level: str) -> List[str]:\n        \"\"\"Get required documents based on risk level\"\"\"\n        documents = {\n            VendorRiskLevel.CRITICAL.value: [\n                'Security audit report (SOC 2 Type II)',\n                'Privacy policy',\n                'Financial statements',\n                'Business continuity plan',\n                'Insurance certificates'\n            ],\n            VendorRiskLevel.HIGH.value: [\n                'Security audit report',\n                'Privacy policy',\n                'Insurance certificates'\n            ],\n            VendorRiskLevel.MEDIUM.value: ['Privacy policy'],\n            VendorRiskLevel.LOW.value: []\n        }\n        return documents.get(risk_level, [])\n\n    @staticmethod\n    def _calculate_suitability_score(criteria: Dict) -> float:\n        \"\"\"Calculate data processing suitability score\"\"\"\n        points = 0\n        max_points = 10\n\n        if criteria.get('data_protection_certification'):\n            points += 2\n        if criteria.get('soc_2_certification'):\n            points += 1\n        if criteria.get('privacy_policy_exists'):\n            points += 1\n        if criteria.get('data_processing_agreement'):\n            points += 1\n        if criteria.get('sub_processor_management'):\n            points += 1\n        if criteria.get('data_retention_policy'):\n            points += 1\n        if criteria.get('data_deletion_capability'):\n            points += 1\n        if criteria.get('breach_incidents', 0) == 0:\n            points += 1\n        if criteria.get('security_audit_frequency') == 'annually':\n            points += 1\n\n        return (points / max_points) * 100\n\n    @staticmethod\n    def _identify_gaps(criteria: Dict) -> List[str]:\n        \"\"\"Identify gaps in vendor data processing capabilities\"\"\"\n        gaps = []\n        if not criteria.get('data_protection_certification'):\n            gaps.append('Obtain ISO 27001 certification')\n        if not criteria.get('dpa_available'):\n            gaps.append('Sign Data Processing Agreement')\n        if not criteria.get('data_deletion_capability'):\n            gaps.append('Implement secure data deletion')\n        return gaps\n\n    @staticmethod\n    def _get_monitoring_requirements(risk_level: str) -> List[str]:\n        \"\"\"Get monitoring requirements based on risk level\"\"\"\n        requirements = {\n            VendorRiskLevel.CRITICAL.value: ['Monthly monitoring', 'Continuous screening'],\n            VendorRiskLevel.HIGH.value: ['Quarterly monitoring', 'Semi-annual audit'],\n            VendorRiskLevel.MEDIUM.value: ['Annual monitoring'],\n            VendorRiskLevel.LOW.value: ['As needed']\n        }\n        return requirements.get(risk_level, [])\n\n    @staticmethod\n    def _get_due_diligence_schedule(risk_level: str) -> Dict:\n        \"\"\"Get due diligence review schedule\"\"\"\n        return {\n            'initial_review': 'Before engagement',\n            'periodic_review': {'critical': 'quarterly', 'high': 'annual', 'medium': 'biennial', 'low': 'triennial'}.get(risk_level),\n            'trigger_review': 'Upon significant changes or incidents'\n        }\n\n    @staticmethod\n    def _get_approvals_required(risk_level: str) -> List[str]:\n        \"\"\"Get approvals required based on risk level\"\"\"\n        approvals = {\n            VendorRiskLevel.CRITICAL.value: ['Cannot engage'],\n            VendorRiskLevel.HIGH.value: ['Executive approval', 'Legal approval', 'Security approval'],\n            VendorRiskLevel.MEDIUM.value: ['Manager approval', 'Compliance approval'],\n            VendorRiskLevel.LOW.value: ['Standard approval']\n        }\n        return approvals.get(risk_level, [])\n\n\ndef main():\n    engine = VendorScreeningEngine()\n\n    # Conduct vendor screening\n    screening = engine.conduct_vendor_screening('TechService Ltd', 'VENDOR_001')\n    questionnaire = engine.collect_due_diligence_questionnaire(\n        'VENDOR_001',\n        screening['risk_level']\n    )\n    report = engine.generate_vendor_risk_report('VENDOR_001', screening)\n\n    print(json.dumps({\n        'screening_result': screening,\n        'questionnaire': questionnaire,\n        'risk_report': report\n    }, indent=2, default=str))\n\n\nif __name__ == '__main__':\n    main()\n