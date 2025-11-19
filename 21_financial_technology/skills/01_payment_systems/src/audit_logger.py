"""Audit logging for compliance"""
import logging
import json
from datetime import datetime

class AuditLogger:
    def __init__(self, audit_db):
        self.db = audit_db
        self.logger = logging.getLogger(__name__)

    async def log_payment_event(self, event_type, transaction_id, details, user_id=None):
        """Log payment event for audit trail"""
        log_entry = {
            'timestamp': datetime.utcnow(),
            'event_type': event_type,
            'transaction_id': transaction_id,
            'details': details,
            'user_id': user_id,
            'ip_address': details.get('ip_address'),
            'user_agent': details.get('user_agent')
        }
        
        await self.db.insert_audit_log(log_entry)
        self.logger.info(f"Audit: {event_type} for {transaction_id}")

    async def log_authorization(self, transaction_id, result):
        """Log authorization attempt"""
        await self.log_payment_event(
            'AUTHORIZATION',
            transaction_id,
            {
                'status': 'SUCCESS' if result['success'] else 'FAILED',
                'processor': result.get('processor'),
                'amount': result.get('amount')
            }
        )

    async def log_refund(self, transaction_id, refund_id, amount):
        """Log refund processing"""
        await self.log_payment_event(
            'REFUND',
            transaction_id,
            {
                'refund_id': refund_id,
                'amount': amount
            }
        )

    async def log_chargeback(self, transaction_id, chargeback_id, reason):
        """Log chargeback"""
        await self.log_payment_event(
            'CHARGEBACK',
            transaction_id,
            {
                'chargeback_id': chargeback_id,
                'reason': reason
            }
        )
