"""Handle payment refunds"""
import logging
from datetime import datetime

class RefundProcessor:
    def __init__(self, processor_gateway, db):
        self.processor = processor_gateway
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def process_refund(self, transaction_id, amount=None, reason=None):
        """Process refund (full or partial)"""
        self.logger.info(f"Processing refund for {transaction_id}")
        
        # Get original transaction
        transaction = await self.db.get_transaction(transaction_id)
        
        # Validate refund eligibility
        if not self._can_refund(transaction):
            return {'success': False, 'error': 'Not eligible for refund'}
        
        # Execute refund
        result = await self.processor.refund(
            transaction['processor'],
            transaction_id,
            amount
        )
        
        if result['success']:
            # Record refund
            await self._record_refund(transaction_id, result, reason)
        
        return result

    def _can_refund(self, transaction):
        refundable_statuses = ['captured', 'settled']
        return transaction['status'] in refundable_statuses

    async def _record_refund(self, transaction_id, refund_result, reason):
        refund_record = {
            'transaction_id': transaction_id,
            'refund_id': refund_result['refund_id'],
            'amount': refund_result['amount'],
            'reason': reason,
            'created_at': datetime.utcnow()
        }
        await self.db.save_refund(refund_record)
