from decimal import Decimal, ROUND_HALF_UP

class InterestCalculator:
    @staticmethod
    def calculate_simple_interest(principal: Decimal, rate: Decimal, days: int) -> Decimal:
        interest = (principal * rate * days) / Decimal('36500')
        return interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_compound_interest(principal: Decimal, rate: Decimal, periods: int) -> Decimal:
        return principal * ((1 + rate) ** periods)

    @staticmethod
    def calculate_daily_accrual(balance: Decimal, annual_rate: Decimal) -> Decimal:
        daily_rate = annual_rate / Decimal('365')
        return balance * daily_rate
