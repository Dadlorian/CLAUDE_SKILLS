"""
Policy Management Service
Handles policy creation, modification, renewal, and management
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass
import json


class PolicyStatus(Enum):
    QUOTE = "quote"
    ACTIVE = "active"
    LAPSED = "lapsed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Coverage:
    coverage_type: str
    limit: float
    deductible: float
    premium: float
    active: bool = True


@dataclass
class PolicyHolder:
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: str
    address: str


class PolicyService:
    """Main policy management service"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.policies = {}  # In-memory storage for demo
        self.policy_counter = 1000

    def generate_quote(self, product: str, risk_data: Dict) -> Dict:
        """Generate insurance quote"""
        base_rate = self._get_base_rate(product)
        adjustment_factor = self._calculate_adjustment_factor(risk_data)
        premium = base_rate * adjustment_factor

        quote = {
            "quote_id": self._generate_quote_id(),
            "product": product,
            "premium": round(premium, 2),
            "effective_date": datetime.now().isoformat(),
            "expiration_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "coverages": self._get_coverages(product, risk_data),
            "status": PolicyStatus.QUOTE.value
        }

        return quote

    def create_policy(self, quote_id: str, policyholder: PolicyHolder) -> Dict:
        """Create policy from approved quote"""
        policy_id = self._generate_policy_number()

        policy = {
            "policy_id": policy_id,
            "quote_id": quote_id,
            "policyholder": {
                "first_name": policyholder.first_name,
                "last_name": policyholder.last_name,
                "email": policyholder.email,
                "phone": policyholder.phone,
                "address": policyholder.address
            },
            "effective_date": datetime.now().isoformat(),
            "expiration_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "status": PolicyStatus.ACTIVE.value,
            "premium": 1250.00,
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }

        self.policies[policy_id] = policy
        return policy

    def modify_policy(self, policy_id: str, modifications: Dict) -> Dict:
        """Modify existing policy"""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")

        policy = self.policies[policy_id]

        endorsement = {
            "endorsement_id": self._generate_endorsement_id(),
            "policy_id": policy_id,
            "effective_date": datetime.now().isoformat(),
            "changes": modifications,
            "created_date": datetime.now().isoformat()
        }

        # Update policy
        policy["last_modified"] = datetime.now().isoformat()
        if "effective_date" in modifications:
            policy["effective_date"] = modifications["effective_date"]

        return endorsement

    def renew_policy(self, policy_id: str) -> Dict:
        """Renew policy for next term"""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")

        old_policy = self.policies[policy_id]

        new_policy = {
            "policy_id": self._generate_policy_number(),
            "prior_policy_id": policy_id,
            "policyholder": old_policy["policyholder"],
            "effective_date": old_policy["expiration_date"],
            "expiration_date": (
                datetime.fromisoformat(old_policy["expiration_date"]) +
                timedelta(days=365)
            ).isoformat(),
            "status": PolicyStatus.ACTIVE.value,
            "premium": self._calculate_renewal_premium(policy_id),
            "created_date": datetime.now().isoformat()
        }

        self.policies[new_policy["policy_id"]] = new_policy
        old_policy["status"] = PolicyStatus.EXPIRED.value

        return new_policy

    def cancel_policy(self, policy_id: str, reason: str) -> Dict:
        """Cancel policy"""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")

        policy = self.policies[policy_id]
        policy["status"] = PolicyStatus.CANCELLED.value
        policy["cancelled_date"] = datetime.now().isoformat()
        policy["cancellation_reason"] = reason

        # Calculate refund
        refund = self._calculate_refund(policy)

        return {
            "policy_id": policy_id,
            "status": "cancelled",
            "refund_amount": refund,
            "effective_date": datetime.now().isoformat()
        }

    def get_policy(self, policy_id: str) -> Dict:
        """Retrieve policy details"""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")

        return self.policies[policy_id]

    def get_customer_policies(self, email: str) -> List[Dict]:
        """Get all policies for a customer"""
        customer_policies = [
            policy for policy in self.policies.values()
            if policy["policyholder"]["email"] == email
        ]
        return customer_policies

    # Helper methods

    def _get_base_rate(self, product: str) -> float:
        """Get base rate for product"""
        rates = {
            "auto": 1200,
            "home": 1500,
            "health": 300
        }
        return rates.get(product, 1000)

    def _calculate_adjustment_factor(self, risk_data: Dict) -> float:
        """Calculate rating adjustment factor"""
        factor = 1.0

        if risk_data.get("age", 0) < 25:
            factor *= 1.5
        elif risk_data.get("age", 0) > 65:
            factor *= 1.1

        if risk_data.get("claims_count", 0) > 0:
            factor *= (1 + 0.2 * risk_data["claims_count"])

        if risk_data.get("good_record"):
            factor *= 0.85

        return factor

    def _get_coverages(self, product: str, risk_data: Dict) -> List[Dict]:
        """Get coverages for product"""
        coverages = []

        if product == "auto":
            coverages = [
                {"type": "liability", "limit": 100000, "deductible": 0, "premium": 450},
                {"type": "collision", "limit": 100000, "deductible": 500, "premium": 500},
                {"type": "comprehensive", "limit": 100000, "deductible": 500, "premium": 300}
            ]

        return coverages

    def _generate_policy_number(self) -> str:
        """Generate unique policy number"""
        self.policy_counter += 1
        return f"POL{datetime.now().year}{self.policy_counter}"

    def _generate_quote_id(self) -> str:
        """Generate unique quote ID"""
        return f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _generate_endorsement_id(self) -> str:
        """Generate endorsement ID"""
        return f"E{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def _calculate_renewal_premium(self, policy_id: str) -> float:
        """Calculate renewal premium"""
        policy = self.policies[policy_id]
        base_premium = policy["premium"]

        # Apply trend (3% annual increase)
        renewal_premium = base_premium * 1.03

        return round(renewal_premium, 2)

    def _calculate_refund(self, policy: Dict) -> float:
        """Calculate prorated refund for cancellation"""
        effective_date = datetime.fromisoformat(policy["effective_date"])
        expiration_date = datetime.fromisoformat(policy["expiration_date"])
        cancellation_date = datetime.now()

        total_days = (expiration_date - effective_date).days
        days_used = (cancellation_date - effective_date).days

        refund = policy["premium"] * (total_days - days_used) / total_days

        return round(refund, 2)


# Example usage
if __name__ == "__main__":
    service = PolicyService(None)

    # Generate quote
    risk_data = {"age": 35, "claims_count": 0, "good_record": True}
    quote = service.generate_quote("auto", risk_data)
    print("Quote:", json.dumps(quote, indent=2))

    # Create policy
    holder = PolicyHolder(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="555-1234",
        date_of_birth="1985-01-15",
        address="123 Main St"
    )
    policy = service.create_policy(quote["quote_id"], holder)
    print("\nPolicy:", json.dumps(policy, indent=2))

    # Modify policy
    modifications = {"address": "456 Oak Ave"}
    endorsement = service.modify_policy(policy["policy_id"], modifications)
    print("\nEndorsement:", json.dumps(endorsement, indent=2))
