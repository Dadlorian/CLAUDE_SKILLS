"""Tax Calculator - Calculates tax implications"""


class TaxCalculator:
    """Calculates tax impacts"""

    def calculate_capital_gains(self, cost_basis: float,
                               sale_price: float,
                               holding_days: int) -> Dict:
        """Calculate capital gains and determine holding period"""
        gain = sale_price - cost_basis
        is_long_term = holding_days > 365

        tax_rate = 0.15 if is_long_term else 0.37  # Simplified rates

        return {
            'gain': gain,
            'gain_type': 'LONG_TERM' if is_long_term else 'SHORT_TERM',
            'tax_due': gain * tax_rate,
            'holding_period': holding_days
        }

    def estimate_tax_drag(self, portfolio_return: float,
                         tax_rate: float = 0.25) -> float:
        """Estimate tax drag on portfolio"""
        # Simplified - assume taxes on 30% of return annually
        taxable_return = portfolio_return * 0.30
        return taxable_return * tax_rate

    def calculate_after_tax_return(self, pre_tax_return: float,
                                   tax_rate: float = 0.25) -> float:
        """Calculate after-tax return"""
        return pre_tax_return * (1 - tax_rate)
