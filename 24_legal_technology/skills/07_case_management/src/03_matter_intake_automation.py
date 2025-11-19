"""
Matter Intake Automation - Automated intake form processing and validation
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class IntakeStatus(Enum):
    """Intake form status"""
    SUBMITTED = "submitted"
    CONFLICT_CHECK = "conflict_check"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"


@dataclass
class IntakeForm:
    """Matter intake form"""
    id: str
    submission_date: datetime
    first_name: str
    last_name: str
    email: str
    phone: str
    company: str = ""
    matter_type: str = ""
    matter_description: str = ""
    opposing_parties: List[str] = field(default_factory=list)
    budget_estimate: float = 0.0
    preferred_contact_method: str = "email"
    insurance_coverage: bool = False
    status: IntakeStatus = IntakeStatus.SUBMITTED
    notes: str = ""
    conflict_check_results: Dict[str, Any] = field(default_factory=dict)
    assigned_attorney: Optional[str] = None
    estimated_fee: float = 0.0
    engagement_letter_sent: bool = False

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class IntakeValidator:
    """Validates intake form data"""

    # Validation rules
    REQUIRED_FIELDS = [
        "first_name", "last_name", "email", "phone",
        "matter_type", "matter_description"
    ]

    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^\+?1?\d{9,15}$'

    def validate(self, form: IntakeForm) -> Dict[str, Any]:
        """
        Validate intake form

        Args:
            form: IntakeForm instance

        Returns:
            Validation result with errors list
        """
        errors = []
        warnings = []

        # Check required fields
        for field_name in self.REQUIRED_FIELDS:
            value = getattr(form, field_name)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"Required field missing: {field_name}")

        # Validate email
        if form.email and not re.match(self.EMAIL_PATTERN, form.email):
            errors.append("Invalid email format")

        # Validate phone
        if form.phone and not re.match(self.PHONE_PATTERN, form.phone.replace("-", "")):
            warnings.append("Phone number format may be invalid")

        # Validate matter description length
        if len(form.matter_description) < 20:
            warnings.append("Matter description is very brief - may need more detail")

        # Check for budget
        if form.budget_estimate == 0:
            warnings.append("No budget estimate provided")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class IntakeProcessor:
    """Processes intake forms through workflow"""

    def __init__(self, conflict_checker, fee_calculator):
        """
        Initialize intake processor

        Args:
            conflict_checker: Conflict checking service
            fee_calculator: Fee estimation service
        """
        self.conflict_checker = conflict_checker
        self.fee_calculator = fee_calculator
        self.validator = IntakeValidator()

    def process_intake(self, form: IntakeForm) -> Dict[str, Any]:
        """
        Process intake form through complete workflow

        Args:
            form: Submitted intake form

        Returns:
            Processing result
        """
        # Step 1: Validate form
        validation_result = self.validator.validate(form)
        if not validation_result["is_valid"]:
            return {
                "success": False,
                "stage": "validation",
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"]
            }

        # Step 2: Check conflicts
        form.status = IntakeStatus.CONFLICT_CHECK
        conflict_result = self.conflict_checker.check(
            client_name=form.full_name,
            opposing_parties=form.opposing_parties,
            company=form.company
        )

        form.conflict_check_results = conflict_result

        if conflict_result["has_conflict"]:
            form.status = IntakeStatus.REJECTED
            return {
                "success": False,
                "stage": "conflict_check",
                "message": f"Conflict identified: {conflict_result['details']}",
                "referral_suggested": True
            }

        # Step 3: Estimate fees
        fee_estimate = self.fee_calculator.estimate(
            matter_type=form.matter_type,
            estimated_hours=self._estimate_hours(form.matter_type),
            billing_rate=self._get_billing_rate(form.matter_type)
        )

        form.estimated_fee = fee_estimate["total"]

        # Step 4: Auto-assign attorney
        assigned_attorney = self._assign_attorney(form.matter_type)
        form.assigned_attorney = assigned_attorney

        # Step 5: Mark as pending review
        form.status = IntakeStatus.PENDING_REVIEW

        return {
            "success": True,
            "stage": "pending_review",
            "intake_id": form.id,
            "estimated_fee": form.estimated_fee,
            "assigned_attorney": assigned_attorney,
            "next_steps": [
                "Attorney review intake form",
                "Confirm fee arrangement with client",
                "Generate engagement letter",
                "Obtain client signature",
                "Create matter record"
            ]
        }

    def _estimate_hours(self, matter_type: str) -> float:
        """Estimate hours based on matter type"""
        estimates = {
            "will_trust": 5.0,
            "asset_purchase": 40.0,
            "contract_review": 8.0,
            "injury_claim": 25.0,
            "employment": 15.0,
            "real_estate": 20.0
        }
        return estimates.get(matter_type.lower(), 10.0)

    def _get_billing_rate(self, matter_type: str) -> float:
        """Get billing rate based on matter type"""
        rates = {
            "will_trust": 300.0,
            "asset_purchase": 350.0,
            "contract_review": 300.0,
            "injury_claim": 250.0,
            "employment": 300.0,
            "real_estate": 325.0
        }
        return rates.get(matter_type.lower(), 300.0)

    def _assign_attorney(self, matter_type: str) -> str:
        """Auto-assign attorney based on matter type"""
        # In real system, would check attorney availability and workload
        assignments = {
            "litigation": "Attorney Sarah Chen",
            "corporate": "Attorney Michael Rodriguez",
            "employment": "Attorney Jennifer Williams",
            "real_estate": "Attorney James Mitchell"
        }
        return assignments.get(matter_type.lower(), "Unassigned")

    def generate_engagement_letter(self, form: IntakeForm) -> str:
        """Generate engagement letter from intake form"""
        letter = f"""
ENGAGEMENT LETTER

Date: {datetime.now().strftime('%B %d, %Y')}
Client: {form.full_name}
Matter: {form.matter_description}

SCOPE OF SERVICES:
We will represent you in connection with the above-referenced matter.

FEE AGREEMENT:
Our estimated fee for services is: ${form.estimated_fee:,.2f}
Hourly rate: ${self._get_billing_rate(form.matter_type)}/hour

RETAINER:
An initial retainer of ${form.estimated_fee * 0.25:,.2f} is required to begin work.

BILLING:
We will bill monthly for services rendered and costs incurred.

Please contact us if you have questions about this engagement.

Sincerely,
{form.assigned_attorney}
        """
        return letter.strip()


class ConflictChecker:
    """Checks for conflicts of interest"""

    def __init__(self, current_clients: List[str], opposing_parties_history: List[str]):
        self.current_clients = [name.lower() for name in current_clients]
        self.opposing_parties_history = [name.lower() for name in opposing_parties_history]

    def check(self, client_name: str, opposing_parties: List[str], company: str = "") -> Dict[str, Any]:
        """Check for conflicts"""
        conflicts = []

        # Check current clients
        client_name_lower = client_name.lower()
        if client_name_lower in self.current_clients:
            conflicts.append(f"Client {client_name} is already a current client")

        # Check opposing parties
        for party in opposing_parties:
            party_lower = party.lower()
            if party_lower in self.current_clients:
                conflicts.append(f"Opposing party {party} is a current client")
            if party_lower in self.opposing_parties_history:
                conflicts.append(f"Opposing party {party} was previously represented")

        return {
            "has_conflict": len(conflicts) > 0,
            "details": "; ".join(conflicts) if conflicts else "No conflicts detected"
        }


class FeeCalculator:
    """Calculates fee estimates"""

    def estimate(self, matter_type: str, estimated_hours: float, billing_rate: float) -> Dict[str, Any]:
        """Estimate total fees"""
        subtotal = estimated_hours * billing_rate
        contingency = subtotal * 0.1  # 10% contingency

        return {
            "matter_type": matter_type,
            "estimated_hours": estimated_hours,
            "billing_rate": billing_rate,
            "subtotal": subtotal,
            "contingency": contingency,
            "total": subtotal + contingency
        }


# Example usage
if __name__ == "__main__":
    # Initialize services
    current_clients = ["Acme Corporation", "Smith Industries"]
    opposing_parties = ["Johnson Corp", "Williams LLC"]

    conflict_checker = ConflictChecker(current_clients, opposing_parties)
    fee_calculator = FeeCalculator()
    processor = IntakeProcessor(conflict_checker, fee_calculator)

    # Create sample intake form
    form = IntakeForm(
        id="intake_001",
        submission_date=datetime.now(),
        first_name="Robert",
        last_name="Thompson",
        email="robert@example.com",
        phone="555-123-4567",
        company="Thompson Manufacturing",
        matter_type="contract_review",
        matter_description="Need review of commercial lease agreement before signing",
        opposing_parties=["Landlord Corp"],
        budget_estimate=3000.0
    )

    # Process intake
    result = processor.process_intake(form)
    print("Intake Processing Result:")
    print(f"Success: {result['success']}")
    print(f"Estimated Fee: ${result.get('estimated_fee', 0):,.2f}")
    print(f"Assigned Attorney: {result.get('assigned_attorney', 'Unassigned')}")

    # Generate engagement letter
    if result["success"]:
        letter = processor.generate_engagement_letter(form)
        print("\n" + "="*50)
        print(letter)
