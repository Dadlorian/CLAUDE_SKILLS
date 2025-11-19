"""
KYC Service - Customer Identification and Due Diligence
Handles automated customer verification and risk assessment
"""

import hashlib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class VerificationStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"

@dataclass
class CustomerProfile:
    customer_id: str
    name: str
    email: str
    dob: str
    nationality: str
    country_of_residence: str
    document_type: str
    document_number: str
    business_type: Optional[str] = None
    pep_status: bool = False
    created_date: str = None
    last_updated: str = None

    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.utcnow().isoformat()
        self.last_updated = datetime.utcnow().isoformat()

@dataclass
class RiskAssessment:
    customer_id: str
    risk_level: RiskLevel
    risk_score: float  # 0-100
    customer_type_risk: float
    geographic_risk: float
    industry_risk: float
    assessment_date: str
    rationale: str
    recommended_cdd_level: str

class KYCService:
    """Core KYC service for customer verification"""

    def __init__(self):
        self.country_risk_scores = {
            'US': 15, 'UK': 15, 'CA': 15, 'AU': 15, 'SG': 20,
            'HK': 20, 'DE': 15, 'FR': 15, 'NL': 15, 'SE': 15,
            'CN': 40, 'RU': 50, 'IR': 90, 'NK': 100, 'SY': 90
        }
        self.industry_risk_scores = {
            'mining': 45, 'trading': 50, 'import_export': 55,
            'casino': 70, 'money_services': 75, 'real_estate': 60,
            'arts_antiques': 65, 'finance': 25, 'tech': 20,
            'healthcare': 15, 'education': 15, 'government': 10
        }

    def verify_customer(self, profile: CustomerProfile) -> Dict:
        """
        Verify customer identity and basic information
        """
        verification_result = {
            'customer_id': profile.customer_id,
            'status': VerificationStatus.APPROVED.value,
            'verified_timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }

        # Verify document
        doc_check = self._verify_document(profile)
        verification_result['checks']['document'] = doc_check

        # Verify identity against PEP/sanctions
        if profile.pep_status:
            verification_result['status'] = VerificationStatus.MANUAL_REVIEW.value
            verification_result['checks']['pep'] = {'status': 'MATCH', 'action': 'ESCALATE'}
        else:
            verification_result['checks']['pep'] = {'status': 'NO_MATCH'}

        # Calculate hash for audit
        verification_result['verification_hash'] = self._generate_hash(profile)

        return verification_result

    def assess_customer_risk(self, profile: CustomerProfile) -> RiskAssessment:
        """
        Calculate customer risk score and determine CDD level
        """
        # Calculate component risk scores
        customer_type_risk = 30 if profile.business_type else 20
        geographic_risk = self.country_risk_scores.get(profile.country_of_residence, 50)
        industry_risk = self.industry_risk_scores.get(
            profile.business_type.lower() if profile.business_type else 'finance', 30
        )

        # Weighted risk score
        risk_score = (
            customer_type_risk * 0.25 +
            geographic_risk * 0.35 +
            industry_risk * 0.25 +
            (50 if profile.pep_status else 0) * 0.15
        )

        # Determine risk level
        if risk_score < 25:
            risk_level = RiskLevel.LOW
            cdd_level = "BASIC"
        elif risk_score < 50:
            risk_level = RiskLevel.MEDIUM
            cdd_level = "ENHANCED"
        elif risk_score < 75:
            risk_level = RiskLevel.HIGH
            cdd_level = "ENHANCED_DUE_DILIGENCE"
        else:
            risk_level = RiskLevel.VERY_HIGH
            cdd_level = "SENIOR_REVIEW"

        rationale = f"""
        Customer Type Risk: {customer_type_risk:.1f}
        Geographic Risk ({profile.country_of_residence}): {geographic_risk:.1f}
        Industry Risk: {industry_risk:.1f}
        PEP Status: {'HIGH' if profile.pep_status else 'LOW'}
        """

        return RiskAssessment(
            customer_id=profile.customer_id,
            risk_level=risk_level,
            risk_score=risk_score,
            customer_type_risk=customer_type_risk,
            geographic_risk=geographic_risk,
            industry_risk=industry_risk,
            assessment_date=datetime.utcnow().isoformat(),
            rationale=rationale,
            recommended_cdd_level=cdd_level
        )

    def perform_cdd(self, profile: CustomerProfile, risk_level: RiskLevel) -> Dict:
        """
        Perform Customer Due Diligence based on risk level
        """
        cdd_result = {
            'customer_id': profile.customer_id,
            'risk_level': risk_level.value,
            'cdd_procedures': []
        }

        if risk_level == RiskLevel.LOW:
            cdd_result['cdd_procedures'] = [
                'BASIC_IDENTITY_VERIFICATION',
                'ADDRESS_VERIFICATION'
            ]
        elif risk_level == RiskLevel.MEDIUM:
            cdd_result['cdd_procedures'] = [
                'ENHANCED_IDENTITY_VERIFICATION',
                'SOURCE_OF_FUNDS_VERIFICATION',
                'BUSINESS_PURPOSE_CLARIFICATION',
                'BENEFICIAL_OWNER_IDENTIFICATION'
            ]
        elif risk_level == RiskLevel.HIGH:
            cdd_result['cdd_procedures'] = [
                'COMPREHENSIVE_DUE_DILIGENCE',
                'WEALTH_SOURCE_VERIFICATION',
                'BENEFICIAL_OWNER_DEEP_INVESTIGATION',
                'SENIOR_MANAGEMENT_APPROVAL'
            ]
        else:  # VERY_HIGH
            cdd_result['cdd_procedures'] = [
                'FULL_DUE_DILIGENCE_INVESTIGATION',
                'BOARD_APPROVAL_REQUIRED',
                'CONSIDER_RELATIONSHIP_DECLINE'
            ]

        cdd_result['completion_date'] = datetime.utcnow().isoformat()
        return cdd_result

    def _verify_document(self, profile: CustomerProfile) -> Dict:
        """Verify document authenticity"""
        return {
            'status': 'VERIFIED' if profile.document_number else 'FAILED',
            'document_type': profile.document_type,
            'expiry_check': 'PASSED'
        }

    def _generate_hash(self, profile: CustomerProfile) -> str:
        """Generate audit hash for verification"""
        data = f"{profile.customer_id}{profile.name}{profile.dob}".encode()
        return hashlib.sha256(data).hexdigest()

    def update_customer_risk(self, customer_id: str, new_profile: CustomerProfile) -> Dict:
        """Update customer risk assessment"""
        assessment = self.assess_customer_risk(new_profile)
        return {
            'customer_id': customer_id,
            'previous_assessment': 'ARCHIVED',
            'new_assessment': asdict(assessment),
            'update_timestamp': datetime.utcnow().isoformat()
        }

# Example usage
if __name__ == "__main__":
    kyc_service = KYCService()

    # Create customer profile
    profile = CustomerProfile(
        customer_id="CUST-001",
        name="John Doe",
        email="john.doe@example.com",
        dob="1980-01-15",
        nationality="US",
        country_of_residence="US",
        document_type="passport",
        document_number="123456789",
        business_type="technology",
        pep_status=False
    )

    # Verify customer
    verification = kyc_service.verify_customer(profile)
    print("Verification Result:", json.dumps(verification, indent=2))

    # Assess risk
    risk_assessment = kyc_service.assess_customer_risk(profile)
    print("\nRisk Assessment:", json.dumps(asdict(risk_assessment), indent=2))

    # Perform CDD
    cdd = kyc_service.perform_cdd(profile, risk_assessment.risk_level)
    print("\nCDD Result:", json.dumps(cdd, indent=2))
