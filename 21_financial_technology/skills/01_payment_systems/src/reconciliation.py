"""Payment reconciliation engine"""
import logging
from datetime import datetime

class ReconciliationEngine:
    def __init__(self, db, processor_gateway):
        self.db = db
        self.processor = processor_gateway
        self.logger = logging.getLogger(__name__)

    async def reconcile_daily(self, date):
        """Daily reconciliation"""
        self.logger.info(f"Starting daily reconciliation for {date}")
        
        # Get submitted transactions
        submitted = await self._get_submitted_transactions(date)
        
        # Get settled transactions from processor
        settled = await self._get_settled_transactions(date)
        
        # Match transactions
        matches, unmatched = self._match_transactions(submitted, settled)
        
        # Generate report
        report = {
            'date': date,
            'submitted_count': len(submitted),
            'matched_count': len(matches),
            'unmatched_count': len(unmatched),
            'status': 'OK' if len(unmatched) == 0 else 'REVIEW',
            'unmatched': unmatched
        }
        
        await self.db.save_reconciliation_report(report)
        return report

    async def _get_submitted_transactions(self, date):
        return await self.db.get_transactions_by_date(date)

    async def _get_settled_transactions(self, date):
        return await self.processor.get_settlement_report(date)

    def _match_transactions(self, submitted, settled):
        matches = []
        unmatched = list(submitted)
        
        for settlement in settled:
            for idx, submission in enumerate(unmatched):
                if self._is_match(submission, settlement):
                    matches.append((submission, settlement))
                    unmatched.pop(idx)
                    break
        
        return matches, unmatched

    def _is_match(self, submission, settlement):
        return (submission['amount'] == settlement['amount'] and
                submission['reference'] == settlement['reference'])
