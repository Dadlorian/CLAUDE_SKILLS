"""Payment processing for premiums and claims"""
from typing import Dict
from decimal import Decimal

class PaymentProcessor:
    def process_payment(self, payment: Dict) -> Dict:
        """Process payment"""
        amount = Decimal(str(payment.get('amount', 0)))
        
        return {
            "transaction_id": "TXN123456",
            "amount": float(amount),
            "status": "processed",
            "method": payment.get('method', 'credit_card'),
            "confirmation": f"Paid {amount}"
        }
    
    def process_refund(self, refund: Dict) -> Dict:
        """Process refund"""
        amount = Decimal(str(refund.get('amount', 0)))
        
        return {
            "refund_id": "REF123456",
            "amount": float(amount),
            "status": "processed",
            "original_transaction": refund.get('original_txn')
        }
