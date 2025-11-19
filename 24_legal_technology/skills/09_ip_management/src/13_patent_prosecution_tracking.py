"""
Patent Prosecution Tracking Example
Tracks patent prosecution history and office action responses
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class OfficeActionType(Enum):
    """Types of office actions"""
    RESTRICTION_REQUIREMENT = "restriction"
    OFFICE_ACTION = "office_action"
    FINAL_REJECTION = "final_rejection"
    ALLOWANCE = "allowance"
    NOTICE_OF_ABANDONMENT = "abandonment"
    RCE_RESPONSE = "rce_response"

@dataclass
class OfficeAction:
    """Represents an office action"""
    action_id: str
    action_type: OfficeActionType
    mailing_date: str
    response_due_date: str
    subject_matter: str
    rejection_basis: List[str]
    claims_affected: List[int]
    office_action_text: str
    response_filed: bool = False
    response_date: Optional[str] = None
    response_text: Optional[str] = None

@dataclass
class AmendmentSet:
    """Represents amendments to a patent application"""
    amendment_id: str
    filing_date: str
    claims_amended: List[int]
    claims_added: List[int]
    claims_deleted: List[int]
    amendments_to_specification: bool
    amendments_to_drawings: bool
    remarks: str

class PatentProsecutionTracker:
    """Track patent prosecution and office action history"""

    def __init__(self, application_number: str):
        self.application_number = application_number
        self.office_actions: List[OfficeAction] = []
        self.amendments: List[AmendmentSet] = []
        self.prosecution_history: List[Dict] = []

    def add_office_action(self, action: OfficeAction):
        """Add an office action to the prosecution history"""
        self.office_actions.append(action)

    def add_amendment(self, amendment: AmendmentSet):
        """Add amendments to track responses"""
        self.amendments.append(amendment)

    def get_prosecution_status(self) -> Dict:
        """Get current prosecution status"""
        if not self.office_actions:
            return {'status': 'No office actions'}

        latest_action = self.office_actions[-1]

        # Determine status
        if latest_action.action_type == OfficeActionType.ALLOWANCE:
            status = "ALLOWED - Ready for Issue Fee"
        elif latest_action.action_type == OfficeActionType.FINAL_REJECTION:
            status = "FINAL REJECTION - RCE or Appeal Required"
        elif latest_action.action_type == OfficeActionType.NOTICE_OF_ABANDONMENT:
            status = "ABANDONED"
        else:
            status = "PENDING RESPONSE"

        return {
            'application_number': self.application_number,
            'current_status': status,
            'latest_action_date': latest_action.mailing_date,
            'response_due_date': latest_action.response_due_date if not latest_action.response_filed else "N/A",
            'total_office_actions': len(self.office_actions),
            'total_amendments': len(self.amendments)
        }

    def get_rejection_analysis(self) -> Dict:
        """Analyze rejection patterns and rejection bases"""
        rejections = [oa for oa in self.office_actions
                     if oa.action_type in [OfficeActionType.OFFICE_ACTION, OfficeActionType.FINAL_REJECTION]]

        if not rejections:
            return {'rejection_count': 0, 'status': 'No rejections found'}

        # Count rejection bases
        rejection_bases = {}
        for oa in rejections:
            for basis in oa.rejection_basis:
                rejection_bases[basis] = rejection_bases.get(basis, 0) + 1

        # Claims most frequently rejected
        claims_rejected = {}
        for oa in rejections:
            for claim in oa.claims_affected:
                claims_rejected[claim] = claims_rejected.get(claim, 0) + 1

        return {
            'total_rejections': len(rejections),
            'rejection_bases': rejection_bases,
            'most_common_basis': max(rejection_bases.items(), key=lambda x: x[1])[0] if rejection_bases else None,
            'most_frequently_rejected_claims': sorted(claims_rejected.items(), key=lambda x: x[1], reverse=True)[:5],
            'final_rejection_count': sum(1 for oa in rejections if oa.action_type == OfficeActionType.FINAL_REJECTION)
        }

    def get_amendment_effectiveness(self) -> Dict:
        """Analyze effectiveness of amendments in overcoming rejections"""
        if not self.amendments or not self.office_actions:
            return {}

        analysis = {
            'total_amendments': len(self.amendments),
            'claims_amended_count': 0,
            'claims_added_count': 0,
            'claims_deleted_count': 0,
            'successful_amendments': 0,  # Amendments resulting in allowance
            'amendment_efficiency': 0.0  # Allowances / amendments
        }

        # Count amendment statistics
        for amendment in self.amendments:
            analysis['claims_amended_count'] += len(amendment.claims_amended)
            analysis['claims_added_count'] += len(amendment.claims_added)
            analysis['claims_deleted_count'] += len(amendment.claims_deleted)

        # Check if followed by allowance
        for i, amendment in enumerate(self.amendments):
            # Check if any subsequent office action is allowance
            amendment_date = datetime.strptime(amendment.filing_date, '%Y-%m-%d')
            subsequent_actions = [oa for oa in self.office_actions
                                 if datetime.strptime(oa.mailing_date, '%Y-%m-%d') > amendment_date]

            if subsequent_actions and subsequent_actions[0].action_type == OfficeActionType.ALLOWANCE:
                analysis['successful_amendments'] += 1

        if analysis['total_amendments'] > 0:
            analysis['amendment_efficiency'] = analysis['successful_amendments'] / analysis['total_amendments']

        return analysis

    def calculate_prosecution_timeline(self) -> Dict:
        """Calculate key dates in prosecution timeline"""
        if not self.office_actions:
            return {}

        first_oa = self.office_actions[0]
        last_oa = self.office_actions[-1]

        first_date = datetime.strptime(first_oa.mailing_date, '%Y-%m-%d')
        last_date = datetime.strptime(last_oa.mailing_date, '%Y-%m-%d')

        total_days = (last_date - first_date).days

        timeline = {
            'first_office_action_date': first_oa.mailing_date,
            'latest_office_action_date': last_oa.mailing_date,
            'total_prosecution_days': total_days,
            'average_days_between_actions': total_days / (len(self.office_actions) - 1) if len(self.office_actions) > 1 else 0,
            'office_action_timeline': [
                {
                    'action_type': oa.action_type.value,
                    'date': oa.mailing_date,
                    'days_from_start': (datetime.strptime(oa.mailing_date, '%Y-%m-%d') - first_date).days
                }
                for oa in self.office_actions
            ]
        }

        return timeline

    def identify_prosecution_issues(self) -> List[str]:
        """Identify potential prosecution issues or concerns"""
        issues = []

        # Check for excessive rejections
        rejections = len([oa for oa in self.office_actions
                         if oa.action_type == OfficeActionType.OFFICE_ACTION])
        if rejections > 3:
            issues.append(f"High number of rejections ({rejections})")

        # Check for final rejections
        final_rejections = [oa for oa in self.office_actions
                           if oa.action_type == OfficeActionType.FINAL_REJECTION]
        if final_rejections and not any(oa.action_type == OfficeActionType.ALLOWANCE for oa in self.office_actions):
            issues.append("Final rejection without subsequent allowance")

        # Check for specification issues
        for oa in self.office_actions:
            if 'written description' in oa.subject_matter.lower():
                issues.append("Written description/enablement issues raised")
            if 'indefiniteness' in oa.subject_matter.lower():
                issues.append("Claim indefiniteness concerns")

        # Check amendment patterns
        if self.amendments:
            for amendment in self.amendments:
                if len(amendment.claims_deleted) > 0:
                    issues.append("Claims have been deleted (possible dependency issues)")

        return issues

    def get_recommended_next_steps(self) -> List[str]:
        """Recommend next steps in prosecution"""
        status = self.get_prosecution_status()
        current_status = status.get('current_status', '')

        recommendations = []

        if 'ALLOWANCE' in current_status:
            recommendations.append("File Issue Fee to proceed to grant")
            recommendations.append("Ensure maintenance fees are scheduled after issuance")

        elif 'FINAL REJECTION' in current_status:
            recommendations.append("Option 1: File Request for Continued Examination (RCE)")
            recommendations.append("Option 2: Appeal to PTAB")
            recommendations.append("Option 3: Abandon and file continuation application")

        elif 'PENDING' in current_status:
            latest_oa = self.office_actions[-1]
            recommendations.append(f"File response by {latest_oa.response_due_date}")
            recommendations.append("Consider claim amendments to overcome rejections")

        return recommendations


# Example usage
if __name__ == "__main__":
    tracker = PatentProsecutionTracker("US20210123456")

    # Add office action
    oa1 = OfficeAction(
        action_id="OA1",
        action_type=OfficeActionType.OFFICE_ACTION,
        mailing_date="2021-06-01",
        response_due_date="2021-09-01",
        subject_matter="Rejections of claims 1-5 under 35 USC 101",
        rejection_basis=["35 USC 101 - Abstract Idea"],
        claims_affected=[1, 2, 3, 4, 5],
        office_action_text="Claims 1-5 are rejected..."
    )
    tracker.add_office_action(oa1)

    # Get status
    status = tracker.get_prosecution_status()
    print(f"Status: {status['current_status']}")
    print(f"Response due: {status['response_due_date']}")

    # Analyze rejections
    rejection_analysis = tracker.get_rejection_analysis()
    print(f"\nRejections: {rejection_analysis['total_rejections']}")
    print(f"Most common basis: {rejection_analysis['most_common_basis']}")
