from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class StandingOrder:
    order_id: str
    from_account: str
    to_account: str
    amount: Decimal
    frequency: str  # DAILY, WEEKLY, MONTHLY, QUARTERLY, ANNUALLY
    start_date: datetime
    end_date: datetime
    status: str

class StandingOrderService:
    def setup_standing_order(self, from_account: str, to_account: str, amount: Decimal) -> str:
        order_id = 'so-001'
        return order_id

    def execute_order(self, order_id: str) -> bool:
        # Execute standing order payment
        return True

    def cancel_order(self, order_id: str):
        # Cancel standing order
        pass
