from datetime import datetime
from typing import Dict

class RegulatoryReporter:
    def generate_call_report(self, quarter: int, year: int) -> Dict:
        """Generate quarterly call report for regulators"""
        report = {
            'reporting_period': f"{quarter}Q{year}",
            'total_assets': Decimal('0'),
            'total_liabilities': Decimal('0'),
            'capital_ratio': Decimal('0'),
            'lcr_ratio': Decimal('0'),
            'nsfr_ratio': Decimal('0')
        }
        return report

    def generate_stress_test(self) -> Dict:
        """Generate stress test results"""
        return {
            'scenarios': [],
            'results': {}
        }

    def file_sar(self, customer_id: str, amount: Decimal, reason: str):
        """File Suspicious Activity Report"""
        sar = {
            'filing_date': datetime.utcnow(),
            'customer_id': customer_id,
            'amount': amount,
            'reason': reason,
            'status': 'FILED'
        }
        return sar
