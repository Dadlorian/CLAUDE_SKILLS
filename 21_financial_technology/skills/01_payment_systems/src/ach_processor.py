"""ACH (Automated Clearing House) payment processor"""
import logging
from datetime import datetime, timedelta

class ACHProcessor:
    def __init__(self, nacha_formatter, bank_api):
        self.formatter = nacha_formatter
        self.bank = bank_api
        self.logger = logging.getLogger(__name__)

    async def create_ach_batch(self, transactions):
        """Create NACHA batch file"""
        # Format batch according to NACHA standard
        nacha_data = self.formatter.format_batch(transactions)
        
        # Submit to bank
        result = await self.bank.submit_batch(nacha_data)
        
        self.logger.info(f"ACH batch submitted: {result['batch_id']}")
        return result

    def format_nacha_file(self, transactions):
        """Format transactions in NACHA format"""
        lines = []
        
        # File header
        lines.append(self._create_file_header())
        
        # Batch header
        lines.append(self._create_batch_header(len(transactions)))
        
        # Detail records
        for txn in transactions:
            lines.append(self._create_detail_record(txn))
        
        # Batch control
        lines.append(self._create_batch_control(len(transactions)))
        
        # File control
        lines.append(self._create_file_control())
        
        return "\n".join(lines)

    def _create_file_header(self):
        return f"101 031000053 0000000001 {datetime.utcnow().strftime('%y%m%d %H%M')} A094101"

    def _create_batch_header(self, count):
        return f"5200Company Name         1234567890PPDPAYROLL   {datetime.utcnow().strftime('%y%m%d')} "

    def _create_detail_record(self, txn):
        return f"622{txn['account']}      {int(txn['amount']*100):010d}{txn['name']}"

    def _create_batch_control(self, count):
        return f"82000001{count:08d}000000000000000000000000"

    def _create_file_control(self):
        return "9000001000001000000100000000"
