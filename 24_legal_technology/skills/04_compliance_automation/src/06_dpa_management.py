#!/usr/bin/env python3
"""
Data Processing Agreement (DPA) Management
Automated DPA generation, execution, and tracking
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class ProcessorRole(Enum):
    DATA_CONTROLLER = "controller"
    DATA_PROCESSOR = "processor"
    JOINT_CONTROLLER = "joint_controller"

class DPATemplate:
    """Base DPA template with GDPR standard clauses"""

    def __init__(self, controller_name: str, processor_name: str, processing_scope: Dict):
        self.dpa_id = f"DPA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_date = datetime.now().isoformat()
        self.controller_name = controller_name
        self.processor_name = processor_name
        self.processing_scope = processing_scope
        self.sub_processors = []
        self.audit_rights = []
        self.data_transfer_mechanisms = []
        self.is_executed = False
        self.execution_date = None

    def add_standard_clauses(self) -> Dict:
        """Add GDPR standard contractual clauses"""
        return {
            'clauses': [
                {
                    'number': 1,
                    'title': 'Purpose and Nature of Processing',
                    'content': f'Processor shall process personal data on behalf of Controller for: {self.processing_scope.get("purpose", "Not specified")}'
                },
                {
                    'number': 2,
                    'title': 'Type of Personal Data',
                    'content': f'Data categories: {", ".join(self.processing_scope.get("data_categories", []))}'
                },
                {
                    'number': 3,
                    'title': 'Categories of Data Subjects',
                    'content': f'Data subjects: {", ".join(self.processing_scope.get("data_subjects", []))}'
                },
                {
                    'number': 4,
                    'title': 'Duration of Processing',
                    'content': f'Processing duration: {self.processing_scope.get("duration", "Not specified")}'
                },
                {
                    'number': 5,
                    'title': 'Subject Matter',
                    'content': 'Subject matter of processing is defined in Schedule A'
                },
                {
                    'number': 6,
                    'title': 'Processor Obligations',
                    'points': [
                        'Process data only on documented instructions from Controller',
                        'Ensure confidentiality of staff',
                        'Implement appropriate technical and organizational security measures',
                        'Obtain prior authorization before engaging sub-processors',
                        'Assist Controller with data subject rights requests',
                        'Delete or return personal data after end of processing',
                        'Provide audit certification and evidence of compliance'
                    ]
                },
                {
                    'number': 7,
                    'title': 'Data Security',
                    'points': [
                        'Encryption at rest and in transit',
                        'Access controls and authentication',
                        'Regular security audits',
                        'Incident response procedures',
                        'Staff training on data protection',
                        'Secure deletion procedures'
                    ]
                },
                {
                    'number': 8,
                    'title': 'International Data Transfers',
                    'content': 'Transfers to third countries only permitted with adequate safeguards'
                },
                {
                    'number': 9,
                    'title': 'Audit and Inspection Rights',
                    'content': 'Controller has right to audit Processor and inspect facilities upon reasonable notice'
                },
                {
                    'number': 10,
                    'title': 'Sub-processor Authorization',
                    'content': 'Processor shall obtain prior written authorization before engaging sub-processors'
                }
            ]
        }

    def add_sub_processor(self, processor_name: str, location: str, processing_activity: str) -> str:
        """Add authorized sub-processor"""
        sub_processor = {
            'id': f"SUB_{len(self.sub_processors) + 1:02d}",
            'name': processor_name,
            'location': location,
            'processing_activity': processing_activity,
            'authorization_date': datetime.now().isoformat(),
            'status': 'authorized',
            'has_dpa': False,
            'audit_status': 'pending'
        }

        self.sub_processors.append(sub_processor)
        return sub_processor['id']

    def add_audit_right(self, audit_type: str, frequency: str, scope: str) -> None:
        """Add audit rights"""
        self.audit_rights.append({
            'type': audit_type,
            'frequency': frequency,
            'scope': scope,
            'last_audit': None,
            'next_audit': (datetime.now() + timedelta(days=365)).isoformat()
        })

    def add_international_transfer_mechanism(self, mechanism_type: str, jurisdiction: str) -> None:
        """Add mechanism for international data transfers"""
        self.data_transfer_mechanisms.append({
            'type': mechanism_type,  # standard_contractual_clauses, adequacy_decision, bcr
            'jurisdiction': jurisdiction,
            'approved_date': datetime.now().isoformat(),
            'next_review': (datetime.now() + timedelta(days=365)).isoformat()
        })

    def generate_dpa_document(self) -> Dict:
        """Generate complete DPA document"""
        return {
            'dpa_id': self.dpa_id,
            'document_title': f'Data Processing Agreement between {self.controller_name} and {self.processor_name}',
            'execution_date': self.execution_date,
            'effective_date': self.created_date,
            'parties': {
                'controller': {
                    'name': self.controller_name,
                    'role': ProcessorRole.DATA_CONTROLLER.value
                },
                'processor': {
                    'name': self.processor_name,
                    'role': ProcessorRole.DATA_PROCESSOR.value
                }
            },
            'processing_scope': self.processing_scope,
            'standard_clauses': self.add_standard_clauses(),
            'sub_processors': self.sub_processors,
            'audit_rights': self.audit_rights,
            'international_transfers': self.data_transfer_mechanisms,
            'execution_status': {
                'is_executed': self.is_executed,
                'execution_date': self.execution_date,
                'signatures_obtained': self.is_executed
            }
        }

    def execute_dpa(self, controller_signer: str, processor_signer: str) -> Dict:
        """Execute DPA with digital signatures"""
        self.is_executed = True
        self.execution_date = datetime.now().isoformat()

        return {
            'dpa_id': self.dpa_id,
            'execution_status': 'executed',
            'execution_date': self.execution_date,
            'signatories': {
                'controller_representative': controller_signer,
                'processor_representative': processor_signer
            },
            'document_hash': self._generate_document_hash(),
            'digital_signatures': {
                'controller_signature': f'SIGNATURE_{datetime.now().timestamp()}',
                'processor_signature': f'SIGNATURE_{datetime.now().timestamp()}'
            },
            'execution_certificate': f'This is to certify that the DPA {self.dpa_id} was executed on {self.execution_date}'
        }

    def track_compliance_obligations(self) -> Dict:
        """Track DPA compliance obligations"""
        return {
            'dpa_id': self.dpa_id,
            'processor_obligations': [
                {'obligation': 'Process data only per instructions', 'status': 'compliant', 'verification_date': datetime.now().isoformat()},
                {'obligation': 'Maintain confidentiality', 'status': 'compliant', 'verification_date': datetime.now().isoformat()},
                {'obligation': 'Implement security measures', 'status': 'compliant_with_exceptions', 'exceptions': []},
                {'obligation': 'Authorize sub-processors', 'status': 'compliant', 'verification_date': datetime.now().isoformat()},
                {'obligation': 'Assist with data subject rights', 'status': 'compliant', 'verification_date': datetime.now().isoformat()},
                {'obligation': 'Notify of breaches', 'status': 'compliant', 'verification_date': datetime.now().isoformat()},
                {'obligation': 'Delete or return data', 'status': 'pending', 'next_check': (datetime.now() + timedelta(days=90)).isoformat()},
                {'obligation': 'Cooperate with audits', 'status': 'compliant', 'verification_date': datetime.now().isoformat()}
            ],
            'compliance_rate': 87.5,
            'next_review_date': (datetime.now() + timedelta(days=180)).isoformat()
        }

    def generate_compliance_report(self) -> Dict:
        """Generate DPA compliance report"""
        return {
            'report_date': datetime.now().isoformat(),
            'dpa_id': self.dpa_id,
            'processor_name': self.processor_name,
            'controller_name': self.controller_name,
            'reporting_period': {
                'start': (datetime.now() - timedelta(days=180)).isoformat(),
                'end': datetime.now().isoformat()
            },
            'key_metrics': {
                'dpa_executed': self.is_executed,
                'sub_processors_authorized': len(self.sub_processors),
                'audits_completed': 1,
                'incidents_reported': 0,
                'data_subject_requests_processed': 45
            },
            'compliance_findings': [
                {'issue': 'Sub-processor documentation incomplete', 'severity': 'medium', 'remediation_due': (datetime.now() + timedelta(days=30)).isoformat()},
                {'issue': 'Annual audit pending', 'severity': 'high', 'remediation_due': (datetime.now() + timedelta(days=14)).isoformat()}
            ],
            'remediation_actions': [
                {'action': 'Update sub-processor DPAs', 'owner': 'Processor', 'due_date': (datetime.now() + timedelta(days=30)).isoformat()},
                {'action': 'Schedule annual audit', 'owner': 'Controller', 'due_date': (datetime.now() + timedelta(days=14)).isoformat()}
            ],
            'next_review_date': (datetime.now() + timedelta(days=180)).isoformat()
        }

    def amendment_request(self, amendment_reason: str, changes: Dict) -> Dict:
        \"\"\"Request DPA amendment\"\"\"\n        amendment = {\n            'amendment_id': f\"AMD_{self.dpa_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}\",\n            'original_dpa': self.dpa_id,\n            'reason': amendment_reason,\n            'requested_date': datetime.now().isoformat(),\n            'changes_proposed': changes,\n            'status': 'pending_approval',\n            'approval_timeline': '10 business days',\n            'affected_parties': [self.controller_name, self.processor_name]\n        }\n\n        return amendment\n\n    @staticmethod\n    def _generate_document_hash() -> str:\n        \"\"\"Generate hash of DPA document\"\"\"\n        import hashlib\n        return hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]\n\n\nclass DPAManagementSystem:\n    \"\"\"Manage multiple DPAs across organization\"\"\"\n\n    def __init__(self):\n        self.dpa_registry: Dict[str, DPATemplate] = {}\n\n    def create_dpa(self, controller_name: str, processor_name: str, scope: Dict) -> str:\n        \"\"\"Create new DPA\"\"\"\n        dpa = DPATemplate(controller_name, processor_name, scope)\n        self.dpa_registry[dpa.dpa_id] = dpa\n        return dpa.dpa_id\n\n    def get_dpa_status_report(self) -> Dict:\n        \"\"\"Get status of all DPAs\"\"\"\n        executed = sum(1 for dpa in self.dpa_registry.values() if dpa.is_executed)\n        pending = len(self.dpa_registry) - executed\n\n        return {\n            'total_dpas': len(self.dpa_registry),\n            'executed_dpas': executed,\n            'pending_execution': pending,\n            'execution_rate': (executed / len(self.dpa_registry) * 100) if self.dpa_registry else 0,\n            'dpa_list': [\n                {\n                    'dpa_id': dpa.dpa_id,\n                    'controller': dpa.controller_name,\n                    'processor': dpa.processor_name,\n                    'status': 'executed' if dpa.is_executed else 'pending',\n                    'created_date': dpa.created_date\n                }\n                for dpa in self.dpa_registry.values()\n            ]\n        }\n\n\ndef main():\n    # Create DPA\n    dpa = DPATemplate(\n        controller_name='TechCorp Inc',\n        processor_name='CloudService Provider',\n        processing_scope={\n            'purpose': 'Customer data processing and analytics',\n            'data_categories': ['name', 'email', 'usage_data'],\n            'data_subjects': ['customers', 'users'],\n            'duration': '3 years'\n        }\n    )\n\n    # Add sub-processors\n    dpa.add_sub_processor('Analytics Provider', 'USA', 'Analytics processing')\n    dpa.add_sub_processor('Backup Service', 'EU', 'Data backup and recovery')\n\n    # Add audit rights\n    dpa.add_audit_right('annual_audit', 'yearly', 'Full security and operational audit')\n    dpa.add_audit_right('spot_check', 'ad_hoc', 'Compliance verification')\n\n    # Add international transfer mechanism\n    dpa.add_international_transfer_mechanism('standard_contractual_clauses', 'USA')\n\n    # Execute DPA\n    execution = dpa.execute_dpa('John Smith, CEO', 'Jane Doe, VP Operations')\n\n    # Generate reports\n    dpa_document = dpa.generate_dpa_document()\n    compliance = dpa.track_compliance_obligations()\n    report = dpa.generate_compliance_report()\n\n    print(json.dumps({\n        'execution': execution,\n        'compliance_tracking': compliance,\n        'compliance_report': report\n    }, indent=2, default=str))\n\n\nif __name__ == '__main__':\n    main()\n