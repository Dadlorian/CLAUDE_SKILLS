from decimal import Decimal

class OverdraftManager:
    def __init__(self, account_id: str, approved_limit: Decimal):
        self.account_id = account_id
        self.approved_limit = approved_limit
        self.overdraft_fee = Decimal('35.00')
        self.overdraft_interest_rate = Decimal('0.15')

    def check_overdraft(self, balance: Decimal) -> bool:
        return balance < 0

    def apply_overdraft_fee(self, balance: Decimal) -> Decimal:
        if self.check_overdraft(balance):
            return balance - self.overdraft_fee
        return balance

    def calculate_overdraft_interest(self, balance: Decimal, days: int) -> Decimal:
        if balance < 0:
            return abs(balance) * self.overdraft_interest_rate * days / Decimal('365')
        return Decimal('0')
