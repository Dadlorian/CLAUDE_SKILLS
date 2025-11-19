"""
Fee Agreement Generator - Practice Management Automation

Generates fee agreements and retainer agreements customized for
different billing arrangements and client types.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from decimal import Decimal


class FeeArrangement(Enum):
    """Types of fee arrangements"""
    HOURLY = "hourly"
    FLAT_FEE = "flat_fee"
    CONTINGENCY = "contingency"
    RETAINER = "retainer"
    HYBRID = "hybrid"


class AgreementStatus(Enum):
    """Status of fee agreement"""
    DRAFT = "draft"
    SENT_TO_CLIENT = "sent_to_client"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SIGNED = "signed"
    ARCHIVED = "archived"


@dataclass
class FeeAgreement:
    """Represents a fee agreement"""
    agreement_id: str
    matter_id: str
    client_id: str
    attorney_name: str
    client_name: str
    firm_name: str
    matter_description: str
    arrangement_type: FeeArrangement
    creation_date: datetime
    effective_date: datetime
    terms: Dict  # Contains specific terms based on arrangement type
    status: AgreementStatus = AgreementStatus.DRAFT
    signature_date: Optional[datetime] = None
    notes: str = ""


@dataclass
class HourlyTerms:
    """Terms for hourly billing"""
    hourly_rate: Decimal
    estimated_hours: Decimal
    estimated_total: Decimal
    minimum_fee: Optional[Decimal] = None
    billing_frequency: str = "monthly"
    retainer_amount: Optional[Decimal] = None
    expenses_covered: List[str] = None


@dataclass
class FlatFeeTerms:
    """Terms for flat fee billing"""
    flat_fee: Decimal
    service_scope: List[str]
    payment_schedule: str  # "upfront", "50/50", "upon_completion"
    expenses_included: bool = False
    additional_expense_rate: Decimal = Decimal(0)


@dataclass
class ContingencyTerms:
    """Terms for contingency billing"""
    contingency_percentage: Decimal
    case_cost_responsibility: str  # "client", "firm", "split"
    minimum_settlement: Decimal = Decimal(0)
    hourly_rate_if_unsuccessful: Optional[Decimal] = None
    hourly_cap: Optional[Decimal] = None


@dataclass
class RetainerTerms:
    """Terms for retainer billing"""
    retainer_amount: Decimal
    retainer_period: str  # "monthly", "quarterly", "annually"
    hourly_rate: Decimal
    hours_included: Decimal
    additional_hours_rate: Decimal
    retainer_applied_to_billing: bool = True
    refundable: bool = False


class FeeAgreementGenerator:
    """Generates customized fee agreements"""

    def __init__(self, firm_name: str = "Law Firm"):
        self.firm_name = firm_name
        self.agreements: Dict[str, FeeAgreement] = {}
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize fee agreement templates"""
        return {
            "hourly": """
FEE AGREEMENT

This Fee Agreement ("Agreement") is entered into as of {effective_date} between
{firm_name} ("Firm") and {client_name} ("Client").

MATTER DESCRIPTION
{matter_description}

1. HOURLY RATE
The Client agrees to pay the Firm for legal services at an hourly rate of ${hourly_rate}.

2. ESTIMATED COSTS
The Firm estimates this matter will require approximately {estimated_hours} hours,
resulting in an estimated cost of ${estimated_total}. This is an estimate only and
actual costs may vary.

3. BILLING AND PAYMENT
The Firm will bill the Client {billing_frequency} for services rendered. Payment is
due within 30 days of invoice.

4. EXPENSES
Client is responsible for out-of-pocket expenses including filing fees, court costs,
deposition fees, and expert witness fees.

5. RETAINER
An initial retainer of ${retainer_amount} is required to commence services.

ATTORNEY: {attorney_name}
            """,
            "flat_fee": """
FEE AGREEMENT - FLAT FEE

This Agreement is entered into as of {effective_date} between {firm_name}
and {client_name}.

MATTER: {matter_description}

1. FLAT FEE
For the scope of services described below, the Client agrees to pay a flat fee of
${flat_fee}.

2. SCOPE OF SERVICES
{scope_of_services}

3. PAYMENT SCHEDULE
{payment_schedule}

4. EXPENSES
{expenses_provision}

5. MODIFICATIONS
If the scope of services changes significantly, the parties will negotiate a revised
fee arrangement.

ATTORNEY: {attorney_name}
            """,
            "contingency": """
FEE AGREEMENT - CONTINGENCY

This Agreement is entered into as of {effective_date} between {firm_name}
and {client_name}.

MATTER: {matter_description}

1. CONTINGENCY FEE
The Firm agrees to represent the Client on a contingency fee basis. The Firm will
receive {contingency_percentage}% of any settlement, judgment, or recovery obtained
in this matter.

2. CASE COSTS
{case_cost_responsibility}

3. MINIMUM SETTLEMENT
The Firm will not settle this matter for less than ${minimum_settlement} without
Client's written consent.

4. UNSUCCESSFUL OUTCOME
If this matter is unsuccessful, and no recovery is obtained, the Client will not
owe the Firm attorney fees. However, Client remains responsible for court costs
and expenses.

5. HOURLY RATE ALTERNATIVE
Should the Client terminate this agreement, the Client may be billed at
${hourly_rate} per hour for services rendered.

ATTORNEY: {attorney_name}
            """,
            "retainer": """
FEE AGREEMENT - RETAINER

This Agreement is entered into as of {effective_date} between {firm_name}
and {client_name}.

SCOPE: {matter_description}

1. RETAINER
Client agrees to pay a retainer of ${retainer_amount} per {retainer_period}.
This retainer will be applied against monthly billings at the rate of ${hourly_rate}
per hour.

2. INCLUDED HOURS
The retainer covers approximately {hours_included} hours of legal services per period.

3. ADDITIONAL SERVICES
Services beyond the included hours will be billed at ${hourly_rate} per hour.

4. BILLING
Invoices will be provided {retainer_period} for services rendered.

5. REFUND POLICY
{refund_policy}

ATTORNEY: {attorney_name}
            """
        }

    def create_hourly_agreement(self, agreement_data: Dict) -> str:
        """Create hourly billing fee agreement"""
        terms = HourlyTerms(
            hourly_rate=agreement_data.get("hourly_rate", Decimal(250)),
            estimated_hours=agreement_data.get("estimated_hours", Decimal(40)),
            estimated_total=agreement_data.get("estimated_total", Decimal(10000)),
            minimum_fee=agreement_data.get("minimum_fee"),
            retainer_amount=agreement_data.get("retainer_amount", Decimal(5000))
        )

        agreement = FeeAgreement(
            agreement_id=f"AGR-{agreement_data['matter_id']}-HOURLY",
            matter_id=agreement_data["matter_id"],
            client_id=agreement_data["client_id"],
            attorney_name=agreement_data["attorney_name"],
            client_name=agreement_data["client_name"],
            firm_name=self.firm_name,
            matter_description=agreement_data.get("matter_description", ""),
            arrangement_type=FeeArrangement.HOURLY,
            creation_date=datetime.now(),
            effective_date=datetime.now(),
            terms={
                "hourly_rate": str(terms.hourly_rate),
                "estimated_hours": str(terms.estimated_hours),
                "estimated_total": str(terms.estimated_total),
                "minimum_fee": str(terms.minimum_fee) if terms.minimum_fee else None,
                "retainer_amount": str(terms.retainer_amount)
            }
        )

        self.agreements[agreement.agreement_id] = agreement
        return agreement.agreement_id

    def create_flat_fee_agreement(self, agreement_data: Dict) -> str:
        """Create flat fee billing agreement"""
        terms = FlatFeeTerms(
            flat_fee=agreement_data.get("flat_fee", Decimal(10000)),
            service_scope=agreement_data.get("service_scope", []),
            payment_schedule=agreement_data.get("payment_schedule", "upfront"),
            expenses_included=agreement_data.get("expenses_included", False),
            additional_expense_rate=agreement_data.get("additional_expense_rate", Decimal(0))
        )

        scope_text = "\n".join([f"- {item}" for item in terms.service_scope])
        expenses_text = "Expenses are included in the flat fee." if terms.expenses_included else "Expenses are billed separately."

        agreement = FeeAgreement(
            agreement_id=f"AGR-{agreement_data['matter_id']}-FLAT",
            matter_id=agreement_data["matter_id"],
            client_id=agreement_data["client_id"],
            attorney_name=agreement_data["attorney_name"],
            client_name=agreement_data["client_name"],
            firm_name=self.firm_name,
            matter_description=agreement_data.get("matter_description", ""),
            arrangement_type=FeeArrangement.FLAT_FEE,
            creation_date=datetime.now(),
            effective_date=datetime.now(),
            terms={
                "flat_fee": str(terms.flat_fee),
                "payment_schedule": terms.payment_schedule,
                "scope_of_services": scope_text,
                "expenses_provision": expenses_text
            }
        )

        self.agreements[agreement.agreement_id] = agreement
        return agreement.agreement_id

    def create_contingency_agreement(self, agreement_data: Dict) -> str:
        """Create contingency fee agreement"""
        terms = ContingencyTerms(
            contingency_percentage=agreement_data.get("contingency_percentage", Decimal(33.3)),
            case_cost_responsibility=agreement_data.get("case_cost_responsibility", "client"),
            minimum_settlement=agreement_data.get("minimum_settlement", Decimal(0)),
            hourly_rate_if_unsuccessful=agreement_data.get("hourly_rate_if_unsuccessful")
        )

        agreement = FeeAgreement(
            agreement_id=f"AGR-{agreement_data['matter_id']}-CONTINGENCY",
            matter_id=agreement_data["matter_id"],
            client_id=agreement_data["client_id"],
            attorney_name=agreement_data["attorney_name"],
            client_name=agreement_data["client_name"],
            firm_name=self.firm_name,
            matter_description=agreement_data.get("matter_description", ""),
            arrangement_type=FeeArrangement.CONTINGENCY,
            creation_date=datetime.now(),
            effective_date=datetime.now(),
            terms={
                "contingency_percentage": str(terms.contingency_percentage),
                "case_cost_responsibility": terms.case_cost_responsibility,
                "minimum_settlement": str(terms.minimum_settlement),
                "hourly_rate_if_unsuccessful": str(terms.hourly_rate_if_unsuccessful) if terms.hourly_rate_if_unsuccessful else None
            }
        )

        self.agreements[agreement.agreement_id] = agreement
        return agreement.agreement_id

    def create_retainer_agreement(self, agreement_data: Dict) -> str:
        """Create retainer fee agreement"""
        terms = RetainerTerms(
            retainer_amount=agreement_data.get("retainer_amount", Decimal(5000)),
            retainer_period=agreement_data.get("retainer_period", "monthly"),
            hourly_rate=agreement_data.get("hourly_rate", Decimal(250)),
            hours_included=agreement_data.get("hours_included", Decimal(20)),
            additional_hours_rate=agreement_data.get("additional_hours_rate", Decimal(250)),
            retainer_applied_to_billing=agreement_data.get("retainer_applied_to_billing", True),
            refundable=agreement_data.get("refundable", False)
        )

        refund_policy = "Retainer is non-refundable." if not terms.refundable else "Unused retainer will be refunded."

        agreement = FeeAgreement(
            agreement_id=f"AGR-{agreement_data['matter_id']}-RETAINER",
            matter_id=agreement_data["matter_id"],
            client_id=agreement_data["client_id"],
            attorney_name=agreement_data["attorney_name"],
            client_name=agreement_data["client_name"],
            firm_name=self.firm_name,
            matter_description=agreement_data.get("matter_description", ""),
            arrangement_type=FeeArrangement.RETAINER,
            creation_date=datetime.now(),
            effective_date=datetime.now(),
            terms={
                "retainer_amount": str(terms.retainer_amount),
                "retainer_period": terms.retainer_period,
                "hourly_rate": str(terms.hourly_rate),
                "hours_included": str(terms.hours_included),
                "additional_hours_rate": str(terms.additional_hours_rate),
                "refund_policy": refund_policy
            }
        )

        self.agreements[agreement.agreement_id] = agreement
        return agreement.agreement_id

    def generate_agreement_document(self, agreement_id: str) -> str:
        """Generate agreement document text"""
        if agreement_id not in self.agreements:
            return ""

        agreement = self.agreements[agreement_id]
        arrangement_type = agreement.arrangement_type.value
        template = self.templates.get(arrangement_type, "")

        return template.format(
            firm_name=agreement.firm_name,
            client_name=agreement.client_name,
            attorney_name=agreement.attorney_name,
            matter_description=agreement.matter_description,
            effective_date=agreement.effective_date.strftime("%B %d, %Y"),
            **agreement.terms
        )

    def send_agreement_to_client(self, agreement_id: str) -> bool:
        """Mark agreement as sent to client"""
        if agreement_id not in self.agreements:
            return False

        agreement = self.agreements[agreement_id]
        agreement.status = AgreementStatus.SENT_TO_CLIENT
        return True

    def accept_agreement(self, agreement_id: str) -> bool:
        """Mark agreement as accepted by client"""
        if agreement_id not in self.agreements:
            return False

        agreement = self.agreements[agreement_id]
        agreement.status = AgreementStatus.ACCEPTED
        return True

    def sign_agreement(self, agreement_id: str) -> bool:
        """Mark agreement as signed"""
        if agreement_id not in self.agreements:
            return False

        agreement = self.agreements[agreement_id]
        agreement.status = AgreementStatus.SIGNED
        agreement.signature_date = datetime.now()
        return True

    def get_agreement_status(self, agreement_id: str) -> Dict:
        """Get agreement status and details"""
        if agreement_id not in self.agreements:
            return {}

        agreement = self.agreements[agreement_id]
        return {
            "agreement_id": agreement_id,
            "matter_id": agreement.matter_id,
            "arrangement_type": agreement.arrangement_type.value,
            "status": agreement.status.value,
            "client_name": agreement.client_name,
            "creation_date": agreement.creation_date.isoformat(),
            "signature_date": agreement.signature_date.isoformat() if agreement.signature_date else None
        }


# Example usage
if __name__ == "__main__":
    generator = FeeAgreementGenerator("Smith & Associates LLP")

    agreement_id = generator.create_hourly_agreement({
        "matter_id": "MAT-2024-001",
        "client_id": "CLI-001",
        "attorney_name": "Jane Smith",
        "client_name": "John Client",
        "matter_description": "Contract dispute litigation",
        "hourly_rate": Decimal(350),
        "estimated_hours": Decimal(100),
        "estimated_total": Decimal(35000)
    })

    generator.send_agreement_to_client(agreement_id)
    generator.accept_agreement(agreement_id)
    generator.sign_agreement(agreement_id)

    status = generator.get_agreement_status(agreement_id)
    print(f"Agreement Status: {status}")

    document = generator.generate_agreement_document(agreement_id)
    print(f"Generated Agreement:\n{document}")
