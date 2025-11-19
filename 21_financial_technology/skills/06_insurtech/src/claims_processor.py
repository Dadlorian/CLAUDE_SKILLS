"""
Claims Processing Service
Handles claims intake, assessment, and settlement
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import json


class ClaimStatus(Enum):
    SUBMITTED = "submitted"
    INVESTIGATING = "investigating"
    APPROVED = "approved"
    DENIED = "denied"
    PAID = "paid"


class ClaimType(Enum):
    COLLISION = "collision"
    COMPREHENSIVE = "comprehensive"
    LIABILITY = "liability"
    MEDICAL = "medical"


class ClaimsProcessor:
    """Process insurance claims from intake to settlement"""

    def __init__(self):
        self.claims = {}
        self.claim_counter = 5000

    def submit_claim(self, policy_id: str, loss_data: Dict) -> Dict:
        """Submit new claim (FNOL)"""
        claim_id = self._generate_claim_id()

        claim = {
            "claim_id": claim_id,
            "policy_id": policy_id,
            "status": ClaimStatus.SUBMITTED.value,
            "loss_type": loss_data.get("type", "unknown"),
            "loss_date": loss_data.get("loss_date", datetime.now().isoformat()),
            "loss_description": loss_data.get("description"),
            "estimated_amount": loss_data.get("estimated_amount", 0),
            "submitted_date": datetime.now().isoformat(),
            "claimant_contact": loss_data.get("claimant_contact"),
            "documents": loss_data.get("documents", []),
            "last_updated": datetime.now().isoformat()
        }

        self.claims[claim_id] = claim
        return claim

    def assess_claim(self, claim_id: str) -> Dict:
        """Assess claim and determine coverage"""
        if claim_id not in self.claims:
            raise ValueError(f"Claim {claim_id} not found")

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.INVESTIGATING.value

        # Assessment results
        assessment = {
            "claim_id": claim_id,
            "coverage_determination": self._determine_coverage(claim),
            "fraud_risk_score": self._assess_fraud_risk(claim),
            "estimated_payout": self._estimate_payout(claim),
            "assessment_date": datetime.now().isoformat()
        }

        claim["assessment"] = assessment
        claim["last_updated"] = datetime.now().isoformat()

        return assessment

    def approve_claim(self, claim_id: str, approved_amount: float) -> Dict:
        """Approve claim for payment"""
        if claim_id not in self.claims:
            raise ValueError(f"Claim {claim_id} not found")

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.APPROVED.value
        claim["approved_amount"] = approved_amount
        claim["approval_date"] = datetime.now().isoformat()

        return {
            "claim_id": claim_id,
            "status": "approved",
            "approved_amount": approved_amount,
            "payment_date": (datetime.now() + timedelta(days=5)).isoformat()
        }

    def deny_claim(self, claim_id: str, reason: str) -> Dict:
        """Deny claim"""
        if claim_id not in self.claims:
            raise ValueError(f"Claim {claim_id} not found")

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.DENIED.value
        claim["denial_reason"] = reason
        claim["denial_date"] = datetime.now().isoformat()

        return {
            "claim_id": claim_id,
            "status": "denied",
            "reason": reason
        }

    def process_payment(self, claim_id: str) -> Dict:
        """Process payment for approved claim"""
        if claim_id not in self.claims:
            raise ValueError(f"Claim {claim_id} not found")

        claim = self.claims[claim_id]

        if claim["status"] != ClaimStatus.APPROVED.value:
            raise ValueError(f"Claim {claim_id} is not approved")

        claim["status"] = ClaimStatus.PAID.value
        claim["payment_date"] = datetime.now().isoformat()

        return {
            "claim_id": claim_id,
            "status": "paid",
            "amount": claim["approved_amount"],
            "payment_method": "ACH",
            "confirmation": f"Paid on {datetime.now().isoformat()}"
        }

    def get_claim(self, claim_id: str) -> Dict:
        """Retrieve claim details"""
        if claim_id not in self.claims:
            raise ValueError(f"Claim {claim_id} not found")

        return self.claims[claim_id]

    def list_claims(self, policy_id: str) -> List[Dict]:
        """List all claims for a policy"""
        return [
            claim for claim in self.claims.values()
            if claim["policy_id"] == policy_id
        ]

    # Helper methods

    def _generate_claim_id(self) -> str:
        """Generate unique claim ID"""
        self.claim_counter += 1
        return f"CLM{datetime.now().year}{self.claim_counter}"

    def _determine_coverage(self, claim: Dict) -> str:
        """Determine if loss is covered"""
        loss_type = claim.get("loss_type", "").lower()

        coverage_map = {
            "collision": True,
            "comprehensive": True,
            "liability": True,
            "medical": True,
            "wear_and_tear": False,
            "mechanical": False
        }

        return "covered" if coverage_map.get(loss_type, True) else "excluded"

    def _assess_fraud_risk(self, claim: Dict) -> int:
        """Assess fraud risk (0-100 score)"""
        risk_score = 0

        # Check for rapid submission
        if claim.get("estimated_amount", 0) > 10000:
            risk_score += 10

        # Check claimant history
        if "prior_claims" in claim and len(claim["prior_claims"]) > 5:
            risk_score += 20

        # Check documentation
        if len(claim.get("documents", [])) < 2:
            risk_score += 15

        return min(risk_score, 100)

    def _estimate_payout(self, claim: Dict) -> float:
        """Estimate claim payout"""
        estimated = claim.get("estimated_amount", 0)

        # Apply deductible
        deductible = 500
        if estimated > deductible:
            estimated -= deductible

        # Apply limit if applicable
        limit = 100000
        estimated = min(estimated, limit)

        return round(estimated, 2)


# Example usage
if __name__ == "__main__":
    processor = ClaimsProcessor()

    # Submit claim
    loss_data = {
        "type": "collision",
        "loss_date": datetime.now().isoformat(),
        "description": "Vehicle collision at intersection",
        "estimated_amount": 8500,
        "claimant_contact": {"email": "john@example.com", "phone": "555-1234"}
    }

    claim = processor.submit_claim("POL202412001001", loss_data)
    print("Claim Submitted:", json.dumps(claim, indent=2))

    # Assess claim
    assessment = processor.assess_claim(claim["claim_id"])
    print("\nAssessment:", json.dumps(assessment, indent=2))

    # Approve and pay
    processor.approve_claim(claim["claim_id"], 8000)
    payment = processor.process_payment(claim["claim_id"])
    print("\nPayment:", json.dumps(payment, indent=2))
