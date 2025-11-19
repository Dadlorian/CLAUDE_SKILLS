"""
Fraud Investigator - Case management for fraud investigations
"""

from datetime import datetime
from typing import Dict, List


class FraudCase:
    """Fraud investigation case"""

    def __init__(self, case_id: str, transaction_id: str):
        self.case_id = case_id
        self.transaction_id = transaction_id
        self.status = 'open'
        self.evidence = {}
        self.notes = []
        self.decision = None
        self.created_at = datetime.now()

    def add_evidence(self, evidence_type: str, data: Dict):
        """Add evidence to case"""
        if evidence_type not in self.evidence:
            self.evidence[evidence_type] = []

        self.evidence[evidence_type].append(data)

    def make_decision(self, decision: str, reasoning: str):
        """Record investigation decision"""
        self.decision = decision
        self.reasoning = reasoning
        self.status = 'resolved'

    def to_dict(self) -> Dict:
        """Serialize case"""
        return {
            'case_id': self.case_id,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'decision': self.decision,
            'created_at': self.created_at.isoformat()
        }
