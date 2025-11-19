"""
Case Manager - Manage investigation cases
"""

from typing import Dict, List
import uuid
from datetime import datetime


class CaseManager:
    """Manage fraud investigation cases"""

    def __init__(self, storage):
        self.storage = storage

    def create_case(self, alert_id: str, transaction_id: str) -> str:
        """Create investigation case"""
        case_id = str(uuid.uuid4())

        case = {
            'case_id': case_id,
            'alert_id': alert_id,
            'transaction_id': transaction_id,
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'evidence': {},
            'notes': []
        }

        self.storage.set(f'case:{case_id}', case)

        return case_id

    def add_evidence(self, case_id: str, evidence_type: str, data: Dict):
        """Add evidence to case"""
        case = self.storage.get(f'case:{case_id}')

        if not case:
            raise ValueError(f"Case {case_id} not found")

        if evidence_type not in case['evidence']:
            case['evidence'][evidence_type] = []

        case['evidence'][evidence_type].append(data)

        self.storage.set(f'case:{case_id}', case)

    def close_case(self, case_id: str, decision: str, reasoning: str):
        """Close investigation case"""
        case = self.storage.get(f'case:{case_id}')

        case['status'] = 'closed'
        case['decision'] = decision
        case['reasoning'] = reasoning
        case['closed_at'] = datetime.now().isoformat()

        self.storage.set(f'case:{case_id}', case)
