#!/usr/bin/env python3
"""
Settlement Negotiation Analysis
Analyzes settlement value ranges based on case characteristics
"""

import pandas as pd
import numpy as np
from scipy import stats

class SettlementAnalyzer:
    """Analyze and predict settlement values"""

    def __init__(self, historical_settlements=None):
        """Initialize with historical settlement data"""
        self.history = historical_settlements

    def calculate_expected_value(self, win_probability, judgment_value, defense_value):
        """
        Calculate expected settlement value using economic model

        Args:
            win_probability: Probability of plaintiff win (0-1)
            judgment_value: Expected judgment if plaintiff wins
            defense_value: Defendant resources available

        Returns:
            Dictionary with expected value and settlement range
        """

        # Expected value from plaintiff perspective
        plaintiff_ev = win_probability * judgment_value

        # Defendant's expected cost
        defendant_ev = (1 - win_probability) * judgment_value

        # Defendant's value cap is available resources
        defendant_ev = min(defendant_ev, defense_value)

        # Reasonable settlement range is where both benefit
        settlement_low = plaintiff_ev * 0.75  # Plaintiff discount
        settlement_high = defendant_ev * 1.25  # Defendant premium

        # Actual settlement typically between these ranges
        settlement_target = (settlement_low + settlement_high) / 2

        return {
            'plaintiff_expected_value': plaintiff_ev,
            'defendant_expected_cost': defendant_ev,
            'settlement_target': settlement_target,
            'settlement_range_low': settlement_low,
            'settlement_range_high': settlement_high,
            'plaintiff_recommendation': settlement_target,
            'defendant_recommendation': settlement_target
        }

    def settlement_by_case_type(self, case_type):
        """Get historical settlement data by case type"""

        settlement_rates = {
            'employment': {
                'settlement_rate': 0.92,
                'avg_settlement_pct_demand': 0.68,
                'median_settlement_days': 240
            },
            'contract': {
                'settlement_rate': 0.82,
                'avg_settlement_pct_demand': 0.72,
                'median_settlement_days': 320
            },
            'IP': {
                'settlement_rate': 0.71,
                'avg_settlement_pct_demand': 0.65,
                'median_settlement_days': 480
            },
            'complex_litigation': {
                'settlement_rate': 0.75,
                'avg_settlement_pct_demand': 0.60,
                'median_settlement_days': 540
            }
        }

        return settlement_rates.get(case_type, {})

    def settlement_probability(self, case_characteristics):
        """
        Estimate probability of settlement based on case characteristics

        Args:
            case_characteristics: Dictionary with case features

        Returns:
            Probability of settlement (0-1)
        """

        probability = 0.70  # Base rate

        # Factors that increase settlement probability
        if case_characteristics.get('neutral_eval_ordered'):
            probability += 0.10

        if case_characteristics.get('mediation_ordered'):
            probability += 0.15

        if case_characteristics.get('judge_recommends'):
            probability += 0.08

        # Factors that decrease settlement probability
        if case_characteristics.get('high_stakes'):
            probability -= 0.05

        if case_characteristics.get('novel_legal_issues'):
            probability -= 0.08

        # Bound probability
        probability = min(probability, 0.99)
        probability = max(probability, 0.01)

        return probability

    def get_settlement_timing(self, case_type, time_since_filing_months):
        """
        Get expected settlement timing based on case type and progress

        Returns:
            Expected months to settlement from current date
        """

        # Base settlement windows by case type
        settlement_windows = {
            'employment': (6, 18),
            'contract': (9, 24),
            'IP': (18, 36),
            'complex_litigation': (24, 60)
        }

        if case_type not in settlement_windows:
            return None

        early, late = settlement_windows[case_type]

        # If early in case, expect settlement window to be in the future
        if time_since_filing_months < early / 2:
            expected_months = early + (late - early) / 2

        # If in typical settlement window, expect soon
        elif time_since_filing_months < early + (late - early) / 2:
            expected_months = (late - time_since_filing_months) / 2

        # If late in case, settlement unlikely
        else:
            expected_months = late

        return expected_months

    def settlement_structure_analysis(self, settlement_amount, tax_implications=True):
        """
        Analyze different settlement structures

        Args:
            settlement_amount: Total settlement value
            tax_implications: Whether to consider tax

        Returns:
            Dictionary with settlement structure options
        """

        options = {}

        # Option 1: Lump sum
        options['lump_sum'] = {
            'structure': 'Single payment',
            'payment': settlement_amount,
            'net_recipient': settlement_amount if not tax_implications else settlement_amount * 0.85,
            'certainty': 'Immediate',
            'complexity': 'Low'
        }

        # Option 2: Structured settlement (7 years)
        monthly_payment = settlement_amount / 84
        options['structured_7yr'] = {
            'structure': '7-year structure',
            'monthly_payment': monthly_payment,
            'total_payment': settlement_amount,
            'net_recipient': settlement_amount * 1.05 if tax_implications else settlement_amount,
            'certainty': 'Secure (funded)',
            'complexity': 'Medium'
        }

        # Option 3: Mixed (lump + annual)
        lump = settlement_amount * 0.6
        annual = (settlement_amount * 0.4) / 5
        options['mixed'] = {
            'structure': 'Lump + annual',
            'lump_payment': lump,
            'annual_payment': annual,
            'years': 5,
            'total_payment': settlement_amount,
            'net_recipient': settlement_amount * 0.9 if tax_implications else settlement_amount,
            'certainty': 'Medium',
            'complexity': 'Medium'
        }

        return options

    def generate_settlement_recommendation(self, **case_params):
        """
        Generate comprehensive settlement recommendation

        Args:
            win_probability: Probability of favorable outcome
            judgment_value: Expected judgment amount
            defense_value: Defendant's available resources
            case_type: Type of case
            days_litigated: Days in litigation
            judge_factor: Judge's settlement tendencies (0.5-1.5)

        Returns:
            Detailed settlement recommendation
        """

        # Calculate expected value
        ev = self.calculate_expected_value(
            case_params['win_probability'],
            case_params['judgment_value'],
            case_params['defense_value']
        )

        # Adjust for judge
        judge_factor = case_params.get('judge_factor', 1.0)
        ev['settlement_target'] = ev['settlement_target'] * judge_factor

        # Get settlement probability
        settlement_prob = self.settlement_probability({
            'neutral_eval_ordered': case_params.get('neutral_eval', False),
            'mediation_ordered': case_params.get('mediation', False),
            'judge_recommends': case_params.get('judge_urges_settlement', False),
            'high_stakes': case_params.get('high_stakes', False),
            'novel_legal_issues': case_params.get('novel_issues', False)
        })

        # Get timing
        settlement_months = self.get_settlement_timing(
            case_params.get('case_type', 'contract'),
            case_params.get('days_litigated', 180) / 30
        )

        # Get structure options
        structures = self.settlement_structure_analysis(
            ev['settlement_target'],
            case_params.get('consider_tax', True)
        )

        recommendation = {
            'settlement_target': ev['settlement_target'],
            'settlement_range': {
                'low': ev['settlement_range_low'],
                'high': ev['settlement_range_high']
            },
            'settlement_probability': settlement_prob,
            'expected_settlement_months': settlement_months,
            'recommended_structures': structures,
            'risk_factors': self._identify_risk_factors(**case_params),
            'negotiation_strategy': self._recommend_strategy(
                settlement_prob,
                case_params.get('win_probability', 0)
            )
        }

        return recommendation

    def _identify_risk_factors(self, **case_params):
        """Identify risk factors that affect settlement"""
        risks = []

        if case_params.get('win_probability', 0.5) < 0.4:
            risks.append("Low win probability - settlement critical")

        if case_params.get('novel_issues'):
            risks.append("Novel legal issues - unpredictable outcome")

        if case_params.get('judge_factor', 1.0) > 1.2:
            risks.append("Judge known to be unpredictable")

        return risks

    def _recommend_strategy(self, settlement_prob, win_prob):
        """Recommend negotiation strategy"""

        if settlement_prob > 0.80:
            return "Aggressive - high settlement probability, push for favorable terms"
        elif settlement_prob > 0.60:
            return "Balanced - settlement likely, negotiate from strength"
        elif settlement_prob > 0.40:
            return "Cautious - prepare for trial, settle only at favorable terms"
        else:
            return "Trial-focused - settlement unlikely, prepare for trial"


if __name__ == "__main__":
    analyzer = SettlementAnalyzer()

    # Example settlement analysis
    print("SETTLEMENT NEGOTIATION ANALYSIS")
    print("=" * 60)

    # Case 1: Employee discrimination claim
    case1_rec = analyzer.generate_settlement_recommendation(
        win_probability=0.65,
        judgment_value=500000,
        defense_value=750000,
        case_type='employment',
        days_litigated=120,
        judge_factor=1.1,
        mediation=True,
        high_stakes=False
    )

    print("\nCase 1: Employment Discrimination")
    print(f"Settlement Target: ${case1_rec['settlement_target']:,.0f}")
    print(f"Settlement Range: ${case1_rec['settlement_range']['low']:,.0f} - ${case1_rec['settlement_range']['high']:,.0f}")
    print(f"Settlement Probability: {case1_rec['settlement_probability']:.0%}")
    print(f"Expected Settlement in: {case1_rec['expected_settlement_months']:.0f} months")
    print(f"Strategy: {case1_rec['negotiation_strategy']}")

    # Case 2: Complex commercial litigation
    case2_rec = analyzer.generate_settlement_recommendation(
        win_probability=0.55,
        judgment_value=5000000,
        defense_value=8000000,
        case_type='complex_litigation',
        days_litigated=360,
        judge_factor=0.95,
        novel_issues=True,
        high_stakes=True
    )

    print("\n\nCase 2: Complex Commercial Litigation")
    print(f"Settlement Target: ${case2_rec['settlement_target']:,.0f}")
    print(f"Settlement Range: ${case2_rec['settlement_range']['low']:,.0f} - ${case2_rec['settlement_range']['high']:,.0f}")
    print(f"Settlement Probability: {case2_rec['settlement_probability']:.0%}")
    print(f"Strategy: {case2_rec['negotiation_strategy']}")
