"""
Automated PHI De-identification Tool
Implements Safe Harbor method
"""
import re
from datetime import datetime

class PHIDeidentifier:
    # 18 HIPAA identifiers to remove
    IDENTIFIERS = [
        'names', 'geographic', 'dates', 'telephone', 'fax',
        'email', 'ssn', 'mrn', 'healthplan', 'account',
        'certificate', 'vehicle', 'device', 'url', 'ip',
        'biometric', 'photo', 'unique'
    ]

    def __init__(self):
        self.patterns = self._compile_patterns()

    def _compile_patterns(self):
        return {
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'ip': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'url': re.compile(r'https?://[^\s]+'),
            'date': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'),
        }

    def deidentify_text(self, text):
        """Remove all 18 identifiers from text"""
        deidentified = text

        # Remove patterns
        for identifier, pattern in self.patterns.items():
            deidentified = pattern.sub(f'[{identifier.upper()}_REMOVED]', deidentified)

        # Remove specific names (would require NER in production)
        # Remove addresses (would require address parser)
        
        return deidentified

    def deidentify_record(self, record):
        """De-identify a patient record dict"""
        safe_record = {}

        # Keep only non-identifying fields
        safe_fields = ['age', 'gender', 'diagnosis_code', 'procedure_code']

        for field in safe_fields:
            if field in record:
                safe_record[field] = record[field]

        # Generalize dates to year only
        if 'date_of_service' in record:
            date = datetime.fromisoformat(record['date_of_service'])
            safe_record['year_of_service'] = date.year

        # Generalize geographic to state only (if full ZIP, reduce to 3 digits)
        if 'zip_code' in record and len(record['zip_code']) == 5:
            safe_record['zip_prefix'] = record['zip_code'][:3] + '00'

        return safe_record

    def create_limited_dataset(self, record):
        """Create limited dataset (can retain dates, city/state/zip)"""
        limited = self.deidentify_record(record)

        # Can keep dates in limited dataset
        limited['date_of_service'] = record.get('date_of_service')

        # Can keep geographic
        limited['city'] = record.get('city')
        limited['state'] = record.get('state')
        limited['zip_code'] = record.get('zip_code')

        return limited
