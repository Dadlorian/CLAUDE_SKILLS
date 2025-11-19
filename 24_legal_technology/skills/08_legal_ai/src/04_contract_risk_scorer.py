"""
Contract Risk Scoring System
Automatically assess risk in contracts using ML and rule-based approaches
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskFactor:
    """Individual risk factor"""
    factor_name: str
    risk_score: float  # 0-100
    severity: RiskLevel
    description: str
    recommendation: str
    clause_location: str = ""

class ContractRiskScorer:
    """Score contract risk based on multiple factors"""

    def __init__(self):
        self.risk_rules = self.load_risk_rules()
        self.risk_weights = {
            "liability": 0.30,
            "indemnification": 0.25,
            "termination": 0.15,
            "payment": 0.10,
            "ip_rights": 0.10,
            "warranties": 0.10
        }

    def load_risk_rules(self) -> Dict:
        """Load risk assessment rules"""

        return {
            "liability": {
                "unlimited_liability": {
                    "score": 90,
                    "severity": RiskLevel.CRITICAL,
                    "patterns": ["unlimited", "no limit on liability"],
                    "recommendation": "Add liability cap"
                },
                "no_liability_cap": {
                    "score": 80,
                    "severity": RiskLevel.HIGH,
                    "patterns": ["liability", "NOT:cap", "NOT:limit"],
                    "recommendation": "Add liability limitation clause"
                },
                "low_liability_cap": {
                    "score": 60,
                    "severity": RiskLevel.MEDIUM,
                    "threshold": "< 2x contract value",
                    "recommendation": "Negotiate higher liability cap"
                }
            },
            "indemnification": {
                "broad_indemnification": {
                    "score": 75,
                    "severity": RiskLevel.HIGH,
                    "patterns": ["indemnify", "all claims", "any claims"],
                    "recommendation": "Add carve-outs for own negligence"
                },
                "third_party_only": {
                    "score": 40,
                    "severity": RiskLevel.MEDIUM,
                    "patterns": ["third-party", "third party"],
                    "recommendation": "Acceptable if IP-focused"
                }
            },
            "termination": {
                "no_termination_for_convenience": {
                    "score": 70,
                    "severity": RiskLevel.HIGH,
                    "patterns": ["NOT:for convenience", "for cause only"],
                    "recommendation": "Add termination for convenience clause"
                },
                "auto_renewal": {
                    "score": 50,
                    "severity": RiskLevel.MEDIUM,
                    "patterns": ["automatic", "auto-renew"],
                    "recommendation": "Add notice requirement to prevent renewal"
                }
            }
        }

    def assess_contract_risk(self, contract_dict: Dict) -> Dict:
        """
        Assess overall contract risk

        Args:
            contract_dict: Dictionary with contract analysis
                {
                    "clauses": {...},
                    "financial_terms": {...},
                    "parties": {...}
                }

        Returns:
            Risk assessment report
        """

        risk_factors = []
        category_scores = {}

        # Assess each category
        for category, weight in self.risk_weights.items():
            category_risk = self.assess_category(category, contract_dict)
            category_scores[category] = category_risk

            # Add factors
            for factor in category_risk['factors']:
                risk_factors.append(factor)

        # Calculate overall score
        overall_score = sum(
            category_scores[cat]['score'] * weight
            for cat, weight in self.risk_weights.items()
        )

        # Determine overall risk level
        overall_level = self.get_risk_level(overall_score)

        # Generate recommendations
        recommendations = self.generate_recommendations(risk_factors)

        return {
            "overall_score": overall_score,
            "overall_level": overall_level,
            "category_scores": category_scores,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "approval_decision": self.get_approval_decision(overall_score, risk_factors)
        }

    def assess_category(self, category: str, contract: Dict) -> Dict:
        """Assess risk for specific category"""

        factors = []
        total_score = 0

        if category == "liability":
            factors = self.assess_liability(contract)
        elif category == "indemnification":
            factors = self.assess_indemnification(contract)
        elif category == "termination":
            factors = self.assess_termination(contract)
        elif category == "payment":
            factors = self.assess_payment_terms(contract)
        elif category == "ip_rights":
            factors = self.assess_ip_rights(contract)
        elif category == "warranties":
            factors = self.assess_warranties(contract)

        # Calculate category score
        if factors:
            total_score = sum(f.risk_score for f in factors) / len(factors)
        else:
            total_score = 50  # Default medium risk if no factors found

        return {
            "category": category,
            "score": total_score,
            "factors": factors,
            "level": self.get_risk_level(total_score)
        }

    def assess_liability(self, contract: Dict) -> List[RiskFactor]:
        """Assess liability provisions"""

        factors = []
        liability_clause = contract.get("clauses", {}).get("limitation_of_liability", "")

        # Check for unlimited liability
        if not liability_clause:
            factors.append(RiskFactor(
                factor_name="Missing liability limitation",
                risk_score=85,
                severity=RiskLevel.HIGH,
                description="No limitation of liability clause found",
                recommendation="Add liability limitation clause with reasonable cap"
            ))

        # Check for liability cap
        elif "exceed" not in liability_clause.lower():
            factors.append(RiskFactor(
                factor_name="No explicit liability cap",
                risk_score=75,
                severity=RiskLevel.HIGH,
                description="Liability clause doesn't specify cap amount",
                recommendation="Add specific dollar amount or formula for cap",
                clause_location=liability_clause[:100]
            ))

        # Check for consequential damages waiver
        if "consequential" not in liability_clause.lower():
            factors.append(RiskFactor(
                factor_name="No consequential damages waiver",
                risk_score=60,
                severity=RiskLevel.MEDIUM,
                description="No waiver of consequential damages",
                recommendation="Add 'no consequential damages' provision"
            ))

        return factors

    def assess_indemnification(self, contract: Dict) -> List[RiskFactor]:
        """Assess indemnification provisions"""

        factors = []
        indem_clause = contract.get("clauses", {}).get("indemnification", "")

        if not indem_clause:
            return factors

        # Check scope
        if "all claims" in indem_clause.lower():
            factors.append(RiskFactor(
                factor_name="Broad indemnification scope",
                risk_score=80,
                severity=RiskLevel.HIGH,
                description="Indemnification covers 'all claims'",
                recommendation="Narrow to specific claim types (e.g., third-party IP claims)"
            ))

        # Check for mutual indemnification
        if contract.get("indemnification_mutual", False):
            factors.append(RiskFactor(
                factor_name="Mutual indemnification",
                risk_score=30,
                severity=RiskLevel.LOW,
                description="Balanced mutual indemnification",
                recommendation="Acceptable"
            ))
        else:
            factors.append(RiskFactor(
                factor_name="One-sided indemnification",
                risk_score=70,
                severity=RiskLevel.HIGH,
                description="Only we indemnify, counterparty doesn't",
                recommendation="Negotiate mutual indemnification"
            ))

        return factors

    def assess_termination(self, contract: Dict) -> List[RiskFactor]:
        """Assess termination provisions"""

        factors = []
        term_clause = contract.get("clauses", {}).get("termination", "")

        # Check for termination for convenience
        if "for convenience" not in term_clause.lower():
            factors.append(RiskFactor(
                factor_name="No termination for convenience",
                risk_score=65,
                severity=RiskLevel.MEDIUM,
                description="Can only terminate for cause",
                recommendation="Add termination for convenience with notice period"
            ))

        # Check notice period
        contract_term = contract.get("term_years", 1)
        if contract_term >= 3:
            factors.append(RiskFactor(
                factor_name="Long-term commitment",
                risk_score=55,
                severity=RiskLevel.MEDIUM,
                description=f"{contract_term}-year term without early termination",
                recommendation="Add early termination option or annual renewal"
            ))

        return factors

    def assess_payment_terms(self, contract: Dict) -> List[RiskFactor]:
        """Assess payment terms"""

        factors = []
        payment_terms = contract.get("payment_terms", "")

        # Check payment timeline
        if "upon signing" in payment_terms.lower() or "upfront" in payment_terms.lower():
            factors.append(RiskFactor(
                factor_name="Upfront payment required",
                risk_score=40,
                severity=RiskLevel.MEDIUM,
                description="Payment required before services delivered",
                recommendation="Negotiate milestone-based payments"
            ))

        return factors

    def assess_ip_rights(self, contract: Dict) -> List[RiskFactor]:
        """Assess IP provisions"""

        factors = []
        ip_clause = contract.get("clauses", {}).get("intellectual_property", "")

        if not ip_clause:
            factors.append(RiskFactor(
                factor_name="Missing IP provisions",
                risk_score=70,
                severity=RiskLevel.HIGH,
                description="No clear IP ownership provisions",
                recommendation="Add IP ownership and licensing provisions"
            ))

        return factors

    def assess_warranties(self, contract: Dict) -> List[RiskFactor]:
        """Assess warranty provisions"""

        factors = []
        warranty_clause = contract.get("clauses", {}).get("warranties", "")

        # Check for warranty disclaimer
        if "as is" in warranty_clause.lower():
            factors.append(RiskFactor(
                factor_name="As-is warranty disclaimer",
                risk_score=60,
                severity=RiskLevel.MEDIUM,
                description="Services provided 'as is' without warranties",
                recommendation="If we're the recipient, push for service level warranties"
            ))

        return factors

    def get_risk_level(self, score: float) -> RiskLevel:
        """Convert numerical score to risk level"""

        if score >= 75:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def generate_recommendations(self, risk_factors: List[RiskFactor]) -> List[str]:
        """Generate prioritized recommendations"""

        # Sort by risk score
        sorted_factors = sorted(risk_factors, key=lambda x: x.risk_score, reverse=True)

        recommendations = []
        for factor in sorted_factors[:5]:  # Top 5 risks
            recommendations.append(
                f"[{factor.severity.value.upper()}] {factor.factor_name}: {factor.recommendation}"
            )

        return recommendations

    def get_approval_decision(self, overall_score: float, risk_factors: List[RiskFactor]) -> Dict:
        """Determine if contract should be approved"""

        critical_risks = [f for f in risk_factors if f.severity == RiskLevel.CRITICAL]

        if critical_risks:
            decision = "REJECT"
            reason = "Critical risk factors must be addressed"
        elif overall_score >= 70:
            decision = "ESCALATE"
            reason = "High risk - requires senior counsel review"
        elif overall_score >= 50:
            decision = "REVIEW"
            reason = "Medium risk - requires legal review"
        else:
            decision = "APPROVE"
            reason = "Low risk - may proceed with standard review"

        return {
            "decision": decision,
            "reason": reason,
            "requires_negotiation": overall_score >= 60,
            "requires_senior_review": overall_score >= 70
        }

def main():
    """Demo contract risk scoring"""

    # Sample contract analysis
    contract = {
        "clauses": {
            "limitation_of_liability": "Supplier's liability shall not exceed $100,000.",
            "indemnification": "Supplier shall indemnify Client against all claims arising from Services.",
            "termination": "Either party may terminate for cause with 30 days notice.",
            "intellectual_property": "All work product is work for hire owned by Client.",
            "warranties": "Supplier warrants Services will be performed professionally."
        },
        "financial_terms": {
            "contract_value": 500000,
            "payment_schedule": "Net 30"
        },
        "term_years": 2,
        "indemnification_mutual": False
    }

    scorer = ContractRiskScorer()

    print("="*70)
    print("CONTRACT RISK ASSESSMENT REPORT")
    print("="*70)

    assessment = scorer.assess_contract_risk(contract)

    print(f"\nOVERALL RISK SCORE: {assessment['overall_score']:.1f}/100")
    print(f"RISK LEVEL: {assessment['overall_level'].value.upper()}")

    print(f"\n{'='*70}")
    print("APPROVAL DECISION")
    print(f"{'='*70}")

    decision = assessment['approval_decision']
    print(f"Decision: {decision['decision']}")
    print(f"Reason: {decision['reason']}")
    print(f"Requires Negotiation: {decision['requires_negotiation']}")
    print(f"Requires Senior Review: {decision['requires_senior_review']}")

    print(f"\n{'='*70}")
    print("CATEGORY BREAKDOWN")
    print(f"{'='*70}")

    for category, details in assessment['category_scores'].items():
        print(f"\n{category.upper().replace('_', ' ')}")
        print(f"  Score: {details['score']:.1f}")
        print(f"  Level: {details['level'].value}")
        print(f"  Issues: {len(details['factors'])}")

    print(f"\n{'='*70}")
    print("TOP RISK FACTORS")
    print(f"{'='*70}")

    for i, factor in enumerate(sorted(assessment['risk_factors'], key=lambda x: x.risk_score, reverse=True)[:5], 1):
        print(f"\n{i}. {factor.factor_name}")
        print(f"   Risk Score: {factor.risk_score}")
        print(f"   Severity: {factor.severity.value}")
        print(f"   Description: {factor.description}")
        print(f"   Recommendation: {factor.recommendation}")

    print(f"\n{'='*70}")
    print("RECOMMENDED ACTIONS")
    print(f"{'='*70}")

    for i, rec in enumerate(assessment['recommendations'], 1):
        print(f"{i}. {rec}")

if __name__ == "__main__":
    main()
