"""
Office Action Tracking System Example
Tracks patent office actions and prosecution responses
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class OfficeActionType(Enum):
    """Types of office actions"""
    NONFINAL_REJECTION = "nonfinal_rejection"
    FINAL_REJECTION = "final_rejection"
    ALLOWANCE = "allowance"
    OFFICE_ACTION = "office_action"
    RESTRICTION_REQUIREMENT = "restriction_requirement"
    INTERNATIONAL_PRELIMINARY_REPORT = "ipr"
    EXAMINATION_REPORT = "examination_report"
    OFFICE_ACTION_RESPONSE_NEEDED = "response_needed"


class ResponseStatus(Enum):
    """Response status"""
    NOT_RESPONDED = "not_responded"
    IN_PREPARATION = "in_preparation"
    FILED = "filed"
    RECEIVED = "received"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class OfficeAction:
    """Office action record"""
    office_action_id: str
    patent_id: str
    application_number: str
    office_action_type: OfficeActionType
    issued_date: datetime
    received_date: datetime
    deadline: datetime
    examiner_name: str
    jurisdiction: str
    claims_rejected: List[int]
    rejections_summary: str
    response_status: ResponseStatus
    rejection_grounds: List[str] = field(default_factory=list)
    office_actions_count: int = 0


@dataclass
class OfficeActionResponse:
    """Response to office action"""
    response_id: str
    office_action_id: str
    filed_date: datetime
    response_type: str  # 'amendment', 'rce', 'rce_with_prosecution_history'
    claims_amended: List[int] = field(default_factory=list)
    cost: float = 0.0
    attorney_name: str = ""
    prosecution_notes: str = ""


class OfficeActionTrackingSystem:
    """Track and analyze office actions"""

    def __init__(self):
        self.office_actions: Dict[str, OfficeAction] = {}
        self.responses: Dict[str, OfficeActionResponse] = {}
        self.patent_prosecution_history: defaultdict = defaultdict(list)

    def add_office_action(self, action: OfficeAction):
        """Add office action"""
        self.office_actions[action.office_action_id] = action
        self.patent_prosecution_history[action.patent_id].append(action.office_action_id)

    def add_response(self, response: OfficeActionResponse):
        """Add response to office action"""
        self.responses[response.response_id] = response
        if response.office_action_id in self.office_actions:
            self.office_actions[response.office_action_id].response_status = ResponseStatus.FILED

    def get_pending_responses(self) -> List[OfficeAction]:
        """
        Get office actions requiring response

        Returns:
            List of office actions needing response
        """
        pending = []
        today = datetime.now()

        for action in self.office_actions.values():
            if action.response_status == ResponseStatus.NOT_RESPONDED and action.deadline >= today:
                pending.append(action)

        return sorted(pending, key=lambda x: (x.deadline, x.jurisdiction))

    def get_overdue_responses(self) -> List[OfficeAction]:
        """
        Get overdue office action responses

        Returns:
            List of overdue office actions
        """
        overdue = []
        today = datetime.now()

        for action in self.office_actions.values():
            if action.response_status == ResponseStatus.NOT_RESPONDED and action.deadline < today:
                overdue.append(action)

        return sorted(overdue, key=lambda x: (today - x.deadline).days, reverse=True)

    def analyze_rejection_patterns(self, patent_id: str) -> Dict:
        """
        Analyze rejection patterns for a patent

        Args:
            patent_id: Patent ID

        Returns:
            Analysis of rejection patterns
        """
        patent_actions = [
            self.office_actions[oa_id]
            for oa_id in self.patent_prosecution_history.get(patent_id, [])
            if oa_id in self.office_actions
        ]

        rejection_grounds = defaultdict(int)
        action_types = defaultdict(int)
        claims_affected = set()

        for action in patent_actions:
            action_types[action.office_action_type.value] += 1

            for ground in action.rejection_grounds:
                rejection_grounds[ground] += 1

            claims_affected.update(action.claims_rejected)

        # Calculate prosecution statistics
        nonfinal_count = sum(1 for a in patent_actions if a.office_action_type == OfficeActionType.NONFINAL_REJECTION)
        final_count = sum(1 for a in patent_actions if a.office_action_type == OfficeActionType.FINAL_REJECTION)
        allowed = any(a.office_action_type == OfficeActionType.ALLOWANCE for a in patent_actions)

        return {
            'patent_id': patent_id,
            'total_office_actions': len(patent_actions),
            'nonfinal_rejections': nonfinal_count,
            'final_rejections': final_count,
            'is_allowed': allowed,
            'top_rejection_grounds': sorted(rejection_grounds.items(), key=lambda x: x[1], reverse=True)[:5],
            'total_claims_rejected': len(claims_affected),
            'prosecution_difficulty': self._assess_difficulty(nonfinal_count, final_count, allowed)
        }

    def _assess_difficulty(self, nonfinal: int, final: int, allowed: bool) -> str:
        """Assess prosecution difficulty"""
        if allowed and nonfinal <= 1:
            return "straightforward"
        elif allowed and final == 0:
            return "moderate"
        elif allowed and final > 0:
            return "challenging"
        elif final > 0 and nonfinal > 2:
            return "very_difficult"
        else:
            return "pending"

    def calculate_response_time_metrics(self) -> Dict:
        """
        Calculate response time metrics

        Returns:
            Response time analysis
        """
        response_times = []

        for response in self.responses.values():
            if response.office_action_id in self.office_actions:
                action = self.office_actions[response.office_action_id]
                time_to_respond = (response.filed_date - action.deadline).days
                response_times.append(time_to_respond)

        if not response_times:
            return {'average_days_to_respond': 0, 'responses_filed': 0}

        return {
            'total_responses_filed': len(response_times),
            'average_days_to_respond': sum(response_times) / len(response_times),
            'fastest_response_days': min(response_times),
            'slowest_response_days': max(response_times),
            'on_time_responses': sum(1 for t in response_times if t <= 0),
            'on_time_percentage': (sum(1 for t in response_times if t <= 0) / len(response_times) * 100) if response_times else 0
        }

    def analyze_prosecution_costs(self, patent_id: str) -> Dict:
        """
        Analyze costs for patent prosecution

        Args:
            patent_id: Patent ID

        Returns:
            Cost analysis
        """
        patent_responses = [
            self.responses[rid]
            for rid in self.responses.keys()
            if rid in self.responses and self.responses[rid].office_action_id in [
                self.patent_prosecution_history[patent_id][i]
                for i in range(len(self.patent_prosecution_history.get(patent_id, [])))
                if self.patent_prosecution_history[patent_id][i] in self.office_actions
            ]
        ]

        total_cost = sum(r.cost for r in patent_responses)
        response_count = len(patent_responses)

        return {
            'patent_id': patent_id,
            'total_prosecution_cost': total_cost,
            'response_count': response_count,
            'average_cost_per_response': total_cost / response_count if response_count > 0 else 0,
            'responses_with_amendments': sum(1 for r in patent_responses if r.response_type == 'amendment')
        }

    def get_prosecution_summary(self, patent_id: str) -> Dict:
        """
        Get complete prosecution summary

        Args:
            patent_id: Patent ID

        Returns:
            Complete prosecution data
        """
        return {
            'patent_id': patent_id,
            'rejection_analysis': self.analyze_rejection_patterns(patent_id),
            'cost_analysis': self.analyze_prosecution_costs(patent_id)
        }

    def estimate_allowance_likelihood(self, patent_id: str) -> Dict:
        """
        Estimate likelihood of allowance based on prosecution history

        Args:
            patent_id: Patent ID

        Returns:
            Allowance likelihood estimate
        """
        analysis = self.analyze_rejection_patterns(patent_id)

        # Simple heuristic model
        score = 100

        # Deduct for final rejections
        score -= analysis['final_rejections'] * 20

        # Deduct for number of rejections
        if analysis['total_office_actions'] > 3:
            score -= 15
        elif analysis['total_office_actions'] > 1:
            score -= 5

        # Check if already allowed
        if analysis['is_allowed']:
            score = 100

        # Clamp score
        score = max(0, min(100, score))

        if score >= 80:
            likelihood = "high"
        elif score >= 50:
            likelihood = "moderate"
        elif score >= 20:
            likelihood = "low"
        else:
            likelihood = "very_low"

        return {
            'patent_id': patent_id,
            'allowance_likelihood': likelihood,
            'score': score,
            'rationale': self._generate_allowance_rationale(analysis)
        }

    @staticmethod
    def _generate_allowance_rationale(analysis: Dict) -> str:
        """Generate rationale for allowance likelihood"""
        if analysis['is_allowed']:
            return "Patent allowed"
        elif analysis['final_rejections'] > 1:
            return "Multiple final rejections present"
        elif analysis['final_rejections'] == 1:
            return "Final rejection on file, amendment needed"
        elif analysis['total_office_actions'] > 2:
            return "Multiple rounds of prosecution"
        else:
            return "Early stage prosecution"

    def generate_prosecution_report(self) -> Dict:
        """
        Generate comprehensive prosecution tracking report

        Returns:
            Complete prosecution analysis
        """
        return {
            'report_date': datetime.now().isoformat(),
            'total_office_actions': len(self.office_actions),
            'pending_responses': len(self.get_pending_responses()),
            'overdue_responses': len(self.get_overdue_responses()),
            'response_time_metrics': self.calculate_response_time_metrics(),
            'pending_actions': [
                {
                    'office_action_id': a.office_action_id,
                    'patent_id': a.patent_id,
                    'type': a.office_action_type.value,
                    'deadline': a.deadline.isoformat(),
                    'days_remaining': (a.deadline - datetime.now()).days
                }
                for a in self.get_pending_responses()
            ]
        }


# Example usage
if __name__ == "__main__":
    tracker = OfficeActionTrackingSystem()

    # Add office actions
    for i in range(5):
        action = OfficeAction(
            office_action_id=f"OA{1000000 + i}",
            patent_id="US7234567",
            application_number="15/234567",
            office_action_type=OfficeActionType.NONFINAL_REJECTION if i < 3 else OfficeActionType.OFFICE_ACTION,
            issued_date=datetime.now() - timedelta(days=i*90),
            received_date=datetime.now() - timedelta(days=i*90-5),
            deadline=datetime.now() + timedelta(days=30 - i*30),
            examiner_name=f"Examiner {i}",
            jurisdiction="US",
            claims_rejected=[1, 2, 3],
            rejections_summary="Claims rejected under 35 USC 102 and 103",
            response_status=ResponseStatus.NOT_RESPONDED if i < 2 else ResponseStatus.FILED,
            rejection_grounds=["102", "103"]
        )
        tracker.add_office_action(action)

    # Generate report
    report = tracker.generate_prosecution_report()
    print("Office Action Tracking Report")
    print(f"Total Office Actions: {report['total_office_actions']}")
    print(f"Pending Responses: {report['pending_responses']}")
    print(f"Overdue Responses: {report['overdue_responses']}")
    print(f"On-Time Response Rate: {report['response_time_metrics']['on_time_percentage']:.1f}%")
