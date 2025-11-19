#!/usr/bin/env python3
"""
Data Mapping Tool
Automated data flow mapping and inventory generation for compliance
"""

import json
from typing import Dict, List, Set
from enum import Enum
from dataclasses import dataclass, asdict

class DataClassification(Enum):
    """Data sensitivity levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    HIGHLY_SENSITIVE = "highly_sensitive"

class DataCategory(Enum):
    """GDPR data categories"""
    PERSONAL_IDENTIFIER = "personal_identifier"
    CONTACT_DATA = "contact_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"
    BEHAVIORAL_DATA = "behavioral_data"
    DEVICE_DATA = "device_data"

@dataclass
class DataElement:
    """Represents a data element in inventory"""
    name: str
    category: str
    classification: str
    description: str
    storage_location: str
    retention_period_days: int
    processing_purpose: str
    legitimate_basis: str
    recipients: List[str]
    is_encrypted: bool
    data_subject_rights_supported: List[str]

class DataMappingTool:
    """Automated data flow mapping and inventory"""

    def __init__(self):
        self.data_inventory: Dict[str, DataElement] = {}
        self.data_flows: List[Dict] = []
        self.processing_activities: List[Dict] = []

    def add_data_element(self, element: DataElement) -> bool:
        """Add a data element to inventory"""
        if element.name in self.data_inventory:
            print(f"Warning: Element {element.name} already exists, updating...")

        # Validation
        if not element.retention_period_days > 0:
            print(f"Error: Invalid retention period for {element.name}")
            return False

        self.data_inventory[element.name] = element
        return True

    def map_data_flow(self, source: str, destination: str, data_elements: List[str],
                     frequency: str, security_measures: List[str]) -> Dict:
        """Map a data flow between systems"""
        flow = {
            'id': f"flow_{len(self.data_flows) + 1}",
            'source': source,
            'destination': destination,
            'data_elements': data_elements,
            'frequency': frequency,  # real-time, batch_daily, batch_weekly, etc.
            'security_measures': security_measures,
            'sensitive_data_transferred': self._is_sensitive_flow(data_elements),
            'requires_dpia': len(data_elements) > 5 or self._is_sensitive_flow(data_elements)
        }

        self.data_flows.append(flow)
        return flow

    def create_processing_activity(self, name: str, purpose: str, data_categories: List[str],
                                  legal_basis: str, data_sources: List[str],
                                  recipients: List[str], retention_days: int) -> Dict:
        """Create a GDPR processing activity record"""
        activity = {
            'id': f"activity_{len(self.processing_activities) + 1}",
            'name': name,
            'purpose': purpose,
            'data_categories': data_categories,
            'legal_basis': legal_basis,
            'data_sources': data_sources,
            'recipients': recipients,
            'retention_period_days': retention_days,
            'involves_children': False,
            'involves_special_category_data': self._involves_special_data(data_categories),
            'automated_decision_making': False,
            'requires_dpia': self._assess_dpia_requirement(data_categories, legal_basis)
        }

        self.processing_activities.append(activity)
        return activity

    def generate_data_inventory_report(self) -> Dict:
        """Generate a data inventory report"""
        return {
            'total_data_elements': len(self.data_inventory),
            'elements_by_classification': self._count_by_classification(),
            'elements_by_category': self._count_by_category(),
            'elements_without_encryption': self._find_unencrypted_elements(),
            'data_elements': [asdict(elem) for elem in self.data_inventory.values()],
            'inventory_completeness_score': self._calculate_completeness_score()
        }

    def generate_dpia_trigger_report(self) -> Dict:
        """Identify processing activities requiring DPIA"""
        dpia_required = [a for a in self.processing_activities if a['requires_dpia']]
        high_risk_flows = [f for f in self.data_flows if f['requires_dpia']]

        return {
            'total_processing_activities': len(self.processing_activities),
            'activities_requiring_dpia': len(dpia_required),
            'data_flows_requiring_dpia': len(high_risk_flows),
            'dpia_required_activities': dpia_required,
            'dpia_required_flows': high_risk_flows,
            'priority': 'high' if len(dpia_required) > 5 else 'medium' if len(dpia_required) > 0 else 'low'
        }

    def check_data_retention_compliance(self) -> Dict:
        """Check data retention policy compliance"""
        violations = []

        for element in self.data_inventory.values():
            # High-risk data should have shorter retention
            if element.classification == DataClassification.HIGHLY_SENSITIVE.value:
                if element.retention_period_days > 365:
                    violations.append({
                        'element': element.name,
                        'issue': 'Highly sensitive data retention exceeds 1 year',
                        'current_retention': element.retention_period_days,
                        'recommended_retention': 180
                    })

            # Special category data should have strict retention
            if element.category in [DataCategory.HEALTH_DATA.value, DataCategory.BIOMETRIC_DATA.value]:
                if element.retention_period_days > 180:
                    violations.append({
                        'element': element.name,
                        'issue': f'Special category data ({element.category}) retention exceeds 6 months',
                        'current_retention': element.retention_period_days,
                        'recommended_retention': 180
                    })

        return {
            'total_elements': len(self.data_inventory),
            'compliance_violations': len(violations),
            'violations': violations,
            'compliance_status': 'compliant' if not violations else 'non-compliant'
        }

    def export_processing_inventory(self) -> Dict:
        """Export processing activity inventory for GDPR Article 30 compliance"""
        return {
            'name_of_organization': 'Company Name',
            'processing_activities': self.processing_activities,
            'total_activities': len(self.processing_activities),
            'data_protection_officer_contact': 'dpo@company.com',
            'last_updated': '2024-01-15',
            'next_review_date': '2024-07-15'
        }

    def _is_sensitive_flow(self, data_elements: List[str]) -> bool:
        """Check if flow involves sensitive data"""
        for elem_name in data_elements:
            if elem_name in self.data_inventory:
                elem = self.data_inventory[elem_name]
                if elem.classification in [DataClassification.CONFIDENTIAL.value,
                                          DataClassification.HIGHLY_SENSITIVE.value]:
                    return True
        return False

    def _involves_special_data(self, categories: List[str]) -> bool:
        """Check if processing involves special category data"""
        special_categories = [DataCategory.HEALTH_DATA.value, DataCategory.BIOMETRIC_DATA.value]
        return any(cat in special_categories for cat in categories)

    def _assess_dpia_requirement(self, categories: List[str], basis: str) -> bool:
        """Assess if DPIA is required"""
        requires_dpia = False

        # Special category data requires DPIA
        if self._involves_special_data(categories):
            requires_dpia = True

        # Automated decision-making requires DPIA
        if basis == 'automated_decision_making':
            requires_dpia = True

        # Large-scale processing requires DPIA
        if len(categories) > 5:
            requires_dpia = True

        return requires_dpia

    def _count_by_classification(self) -> Dict:
        """Count data elements by classification level"""
        counts = {}
        for elem in self.data_inventory.values():
            classification = elem.classification
            counts[classification] = counts.get(classification, 0) + 1
        return counts

    def _count_by_category(self) -> Dict:
        """Count data elements by category"""
        counts = {}
        for elem in self.data_inventory.values():
            category = elem.category
            counts[category] = counts.get(category, 0) + 1
        return counts

    def _find_unencrypted_elements(self) -> List[str]:
        """Find data elements without encryption"""
        return [elem.name for elem in self.data_inventory.values() if not elem.is_encrypted]

    def _calculate_completeness_score(self) -> float:
        """Calculate data inventory completeness score (0-100)"""
        if not self.data_inventory:
            return 0.0

        complete_elements = 0
        for elem in self.data_inventory.values():
            # Check if all required fields are populated
            if all([elem.name, elem.category, elem.classification, elem.storage_location,
                   elem.retention_period_days, elem.processing_purpose, elem.legitimate_basis,
                   elem.recipients]):
                complete_elements += 1

        return (complete_elements / len(self.data_inventory)) * 100


def main():
    tool = DataMappingTool()

    # Add data elements
    customer_name = DataElement(
        name='customer_name',
        category=DataCategory.PERSONAL_IDENTIFIER.value,
        classification=DataClassification.CONFIDENTIAL.value,
        description='Customer full name',
        storage_location='customer_database',
        retention_period_days=365,
        processing_purpose='Customer identification and communication',
        legitimate_basis='Contractual necessity',
        recipients=['customer_service', 'marketing'],
        is_encrypted=True,
        data_subject_rights_supported=['access', 'rectification', 'erasure']
    )
    tool.add_data_element(customer_name)

    # Map a data flow
    tool.map_data_flow(
        source='web_form',
        destination='customer_database',
        data_elements=['customer_name'],
        frequency='real-time',
        security_measures=['TLS_encryption', 'firewall', 'access_control']
    )

    # Create processing activity
    tool.create_processing_activity(
        name='Customer Registration',
        purpose='To establish customer account',
        data_categories=[DataCategory.PERSONAL_IDENTIFIER.value, DataCategory.CONTACT_DATA.value],
        legal_basis='Contractual necessity',
        data_sources=['website_registration_form'],
        recipients=['customer_service_team'],
        retention_days=365
    )

    # Generate reports
    inventory_report = tool.generate_data_inventory_report()
    dpia_report = tool.generate_dpia_trigger_report()
    retention_report = tool.check_data_retention_compliance()

    print(json.dumps({
        'inventory': inventory_report,
        'dpia_assessment': dpia_report,
        'retention_compliance': retention_report
    }, indent=2, default=str))


if __name__ == '__main__':
    main()
