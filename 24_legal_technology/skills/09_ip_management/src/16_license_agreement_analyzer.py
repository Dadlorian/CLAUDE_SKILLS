"""
License Agreement Analyzer Example
Analyzes IP licensing agreements and terms
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class LicenseType(Enum):
    """Types of IP licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SOLE = "sole"
    CROSS_LICENSE = "cross_license"

@dataclass
class LicenseAgreement:
    """Represents an IP license agreement"""
    agreement_id: str
    licensor: str
    licensee: str
    license_type: LicenseType
    ip_assets: List[str]  # Patent numbers, trademark ids, etc.
    effective_date: str
    expiration_date: str
    territory: List[str]  # Geographic scope
    field_of_use: List[str]  # Technology areas
    upfront_fee: float
    running_royalty_rate: float  # As decimal (e.g., 0.03 for 3%)
    minimum_annual_royalty: float
    maximum_royalty_per_unit: Optional[float]
    payment_terms: str
    milestone_payments: Dict[str, float]  # Milestone -> amount
    grant_back: bool  # Improvements granted back to licensor
    exclusivity_scope: str
    termination_clause: str
    notes: Optional[str] = None

class LicenseAgreementAnalyzer:
    """Analyze IP licensing agreements"""

    def __init__(self):
        self.agreements: Dict[str, LicenseAgreement] = {}

    def add_agreement(self, agreement: LicenseAgreement):
        """Add a license agreement for analysis"""
        self.agreements[agreement.agreement_id] = agreement

    def analyze_agreement(self, agreement_id: str) -> Dict:
        """Comprehensive analysis of a license agreement"""
        if agreement_id not in self.agreements:
            return {}

        agreement = self.agreements[agreement_id]

        return {
            'agreement_id': agreement_id,
            'parties': f"{agreement.licensor} -> {agreement.licensee}",
            'type': agreement.license_type.value,
            'status': self._determine_status(agreement),
            'duration_years': self._calculate_duration(agreement),
            'territorial_scope': agreement.territory,
            'ip_assets_count': len(agreement.ip_assets),
            'financial_terms': self._analyze_financial_terms(agreement),
            'exclusivity': agreement.exclusivity_scope,
            'grant_back': agreement.grant_back,
            'risks': self._identify_agreement_risks(agreement)
        }

    def _determine_status(self, agreement: LicenseAgreement) -> str:
        """Determine if agreement is active, expired, or upcoming"""
        today = datetime.now().date()
        eff_date = datetime.strptime(agreement.effective_date, '%Y-%m-%d').date()
        exp_date = datetime.strptime(agreement.expiration_date, '%Y-%m-%d').date()

        if today < eff_date:
            return "Upcoming"
        elif today > exp_date:
            return "Expired"
        else:
            return "Active"

    def _calculate_duration(self, agreement: LicenseAgreement) -> float:
        """Calculate agreement duration in years"""
        eff_date = datetime.strptime(agreement.effective_date, '%Y-%m-%d')
        exp_date = datetime.strptime(agreement.expiration_date, '%Y-%m-%d')

        return (exp_date - eff_date).days / 365.25

    def _analyze_financial_terms(self, agreement: LicenseAgreement) -> Dict:
        """Analyze financial terms of agreement"""
        return {
            'upfront_fee': agreement.upfront_fee,
            'running_royalty_rate': f"{agreement.running_royalty_rate:.1%}",
            'minimum_annual_royalty': agreement.minimum_annual_royalty,
            'maximum_royalty_per_unit': agreement.maximum_royalty_per_unit,
            'payment_terms': agreement.payment_terms,
            'milestone_payments': agreement.milestone_payments,
            'total_possible_income': self._calculate_max_income(agreement)
        }

    def _calculate_max_income(self, agreement: LicenseAgreement) -> float:
        """Estimate maximum income from agreement"""
        income = agreement.upfront_fee

        # Add milestone payments
        income += sum(amount for amount in agreement.milestone_payments.values())

        # Estimate royalties (10 years * minimum annual royalty)
        duration = self._calculate_duration(agreement)
        income += agreement.minimum_annual_royalty * duration

        return income

    def _identify_agreement_risks(self, agreement: LicenseAgreement) -> List[str]:
        """Identify risks in agreement terms"""
        risks = []

        # Low upfront fee risk
        if agreement.upfront_fee < 50000 and agreement.license_type == LicenseType.EXCLUSIVE:
            risks.append("Low upfront fee for exclusive license")

        # Low royalty rates
        if agreement.running_royalty_rate < 0.01 and agreement.license_type == LicenseType.EXCLUSIVE:
            risks.append("Running royalty rate appears very low")

        # No minimum royalty
        if agreement.minimum_annual_royalty == 0:
            risks.append("No minimum annual royalty - licensee may not commercialize")

        # Grant back requirements
        if agreement.grant_back and agreement.license_type == LicenseType.EXCLUSIVE:
            risks.append("Grant back of improvements reduces value of exclusive license")

        # Termination terms
        if 'termination_for_convenience' in agreement.termination_clause.lower():
            risks.append("Termination for convenience may create uncertainty")

        return risks

    def compare_agreements(self, agreement_id1: str, agreement_id2: str) -> Dict:
        """Compare two license agreements"""
        if agreement_id1 not in self.agreements or agreement_id2 not in self.agreements:
            return {}

        agreement1 = self.agreements[agreement_id1]
        agreement2 = self.agreements[agreement_id2]

        return {
            'comparison': {
                'agreement_1': agreement_id1,
                'agreement_2': agreement_id2,
                'license_types': {
                    'agreement_1': agreement1.license_type.value,
                    'agreement_2': agreement2.license_type.value
                },
                'upfront_fees': {
                    'agreement_1': agreement1.upfront_fee,
                    'agreement_2': agreement2.upfront_fee,
                    'difference': agreement1.upfront_fee - agreement2.upfront_fee
                },
                'royalty_rates': {
                    'agreement_1': f"{agreement1.running_royalty_rate:.1%}",
                    'agreement_2': f"{agreement2.running_royalty_rate:.1%}",
                    'higher_rate': 'agreement_1' if agreement1.running_royalty_rate > agreement2.running_royalty_rate else 'agreement_2'
                },
                'territories': {
                    'agreement_1': agreement1.territory,
                    'agreement_2': agreement2.territory,
                    'shared_territories': list(set(agreement1.territory) & set(agreement2.territory))
                }
            }
        }

    def get_licensee_portfolio(self, licensee_name: str) -> Dict:
        """Get all licenses for a specific licensee"""
        licensee_agreements = [a for a in self.agreements.values()
                              if a.licensee == licensee_name]

        if not licensee_agreements:
            return {'licensee': licensee_name, 'agreements': []}

        # Calculate portfolio metrics
        total_upfront = sum(a.upfront_fee for a in licensee_agreements)
        total_minimum_royalties = sum(a.minimum_annual_royalty for a in licensee_agreements)
        avg_royalty_rate = sum(a.running_royalty_rate for a in licensee_agreements) / len(licensee_agreements) if licensee_agreements else 0

        territories = set()
        fields = set()
        for agreement in licensee_agreements:
            territories.update(agreement.territory)
            fields.update(agreement.field_of_use)

        return {
            'licensee': licensee_name,
            'agreement_count': len(licensee_agreements),
            'total_upfront_fees': total_upfront,
            'total_minimum_annual_royalties': total_minimum_royalties,
            'average_royalty_rate': f"{avg_royalty_rate:.1%}",
            'territorial_scope': list(territories),
            'field_of_use_scope': list(fields),
            'agreements': [a.agreement_id for a in licensee_agreements]
        }

    def get_licensor_portfolio(self, licensor_name: str) -> Dict:
        """Get all licenses offered by a licensor"""
        licensor_agreements = [a for a in self.agreements.values()
                              if a.licensor == licensor_name]

        if not licensor_agreements:
            return {'licensor': licensor_name, 'agreements': []}

        # Calculate revenue estimates
        total_upfront = sum(a.upfront_fee for a in licensor_agreements)
        total_annual_minimum = sum(a.minimum_annual_royalty for a in licensor_agreements)
        exclusive_count = sum(1 for a in licensor_agreements if a.license_type == LicenseType.EXCLUSIVE)

        return {
            'licensor': licensor_name,
            'total_agreements': len(licensor_agreements),
            'exclusive_licenses': exclusive_count,
            'estimated_annual_income': total_annual_minimum,
            'total_upfront_income': total_upfront,
            'estimated_total_income': sum(self._calculate_max_income(a) for a in licensor_agreements),
            'licensees': list(set(a.licensee for a in licensor_agreements))
        }

    def assess_royalty_reasonableness(self, agreement_id: str) -> Dict:
        """Assess if royalty rates are reasonable"""
        if agreement_id not in self.agreements:
            return {}

        agreement = self.agreements[agreement_id]

        # Benchmark royalty rates by industry
        benchmark_rates = {
            'software': 0.03,
            'pharma': 0.05,
            'mechanical': 0.025,
            'default': 0.03
        }

        # Get field of use to determine appropriate benchmark
        field = agreement.field_of_use[0] if agreement.field_of_use else 'default'
        benchmark = benchmark_rates.get(field, benchmark_rates['default'])

        # Compare to benchmark
        if agreement.running_royalty_rate > benchmark * 1.5:
            assessment = "Higher than typical"
            reason = "Above benchmark rates"
        elif agreement.running_royalty_rate < benchmark * 0.5:
            assessment = "Lower than typical"
            reason = "Below benchmark rates"
        else:
            assessment = "In line with market"
            reason = "Within typical range"

        return {
            'agreement_id': agreement_id,
            'royalty_rate': f"{agreement.running_royalty_rate:.1%}",
            'benchmark_rate': f"{benchmark:.1%}",
            'assessment': assessment,
            'reason': reason
        }


# Example usage
if __name__ == "__main__":
    analyzer = LicenseAgreementAnalyzer()

    # Add a license agreement
    agreement = LicenseAgreement(
        "LIC001",
        licensor="TechCorp",
        licensee="LicenseeCo",
        license_type=LicenseType.EXCLUSIVE,
        ip_assets=["US10000001", "US10000002"],
        effective_date="2022-01-01",
        expiration_date="2027-01-01",
        territory=["US", "EU"],
        field_of_use=["Software"],
        upfront_fee=500000,
        running_royalty_rate=0.03,
        minimum_annual_royalty=100000,
        maximum_royalty_per_unit=None,
        payment_terms="Quarterly",
        milestone_payments={"First Product": 250000},
        grant_back=True,
        exclusivity_scope="Exclusive in Software field for licensed patents",
        termination_clause="Termination for material breach after 30-day cure period"
    )
    analyzer.add_agreement(agreement)

    # Analyze agreement
    analysis = analyzer.analyze_agreement("LIC001")
    print(f"Agreement Status: {analysis['status']}")
    print(f"Financial Terms: {analysis['financial_terms']}")
