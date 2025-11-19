from datetime import datetime
from typing import List, Dict

class StatementGenerator:
    def generate_statement(self, account_id: str, transactions: List[Dict]) -> Dict:
        statement = {
            'account_id': account_id,
            'statement_date': datetime.utcnow(),
            'opening_balance': 0,
            'closing_balance': 0,
            'transactions': transactions,
            'total_deposits': sum(t['amount'] for t in transactions if t['amount'] > 0),
            'total_withdrawals': sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
        }
        return statement

    def format_pdf(self, statement: Dict) -> bytes:
        # Generate PDF
        return b'PDF content'

    def send_statement(self, customer_email: str, statement: bytes):
        # Send via email
        pass
