"""Withdrawal Planner - Plans sustainable withdrawals"""


class WithdrawalPlanner:
    """Plans retirement withdrawals"""

    def calculate_4pct_rule(self, portfolio_value: float, year: int,
                           inflation_rate: float = 0.03) -> float:
        """Calculate withdrawal using 4% rule"""
        year_1_withdrawal = portfolio_value * 0.04
        return year_1_withdrawal * (1 + inflation_rate) ** (year - 1)

    def calculate_success_rate(self, portfolio_value: float,
                               annual_withdrawal: float,
                               years: int, annual_return: float = 0.07,
                               volatility: float = 0.12) -> float:
        """Estimate success rate (simplified)"""
        # Simplified probability calculation
        required_return = annual_withdrawal / portfolio_value
        if annual_return > required_return:
            excess = (annual_return - required_return) / volatility
            # Success probability based on excess returns
            return min(0.99, 0.5 + (excess * 0.2))
        else:
            return 0.3

    def create_withdrawal_schedule(self, portfolio_value: float,
                                   retirement_years: int) -> list:
        """Create withdrawal schedule"""
        withdrawals = []
        current_withdrawal = portfolio_value * 0.04

        for year in range(1, retirement_years + 1):
            withdrawals.append({
                'year': year,
                'withdrawal': current_withdrawal,
                'inflation_adjusted': current_withdrawal * (1.03 ** (year - 1))
            })

        return withdrawals
