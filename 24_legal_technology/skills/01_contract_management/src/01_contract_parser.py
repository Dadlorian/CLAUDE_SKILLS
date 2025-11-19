"""
Contract Parser - Extract text and metadata from PDF contracts
Uses PyPDF2 for PDF extraction, regex for pattern matching
"""

import re
import json
from datetime import datetime
from PyPDF2 import PdfReader
from pathlib import Path

class ContractParser:
    """Extract structured data from contract PDFs"""
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""
        self.metadata = {}
    
    def extract_text(self):
        """Extract text from PDF file"""
        reader = PdfReader(self.pdf_path)
        self.text = ""
        for page in reader.pages:
            self.text += page.extract_text()
        return self.text
    
    def extract_parties(self):
        """Extract party names and information"""
        parties = []
        
        # Pattern 1: "Between [Party] and [Party]"
        between_pattern = r'between\s+([^,]+?)\s+(?:and|or)\s+([^,]+?)\s*[,.]'
        between_matches = re.findall(between_pattern, self.text, re.IGNORECASE)
        parties.extend(between_matches)
        
        # Pattern 2: "Parties: [Party1], [Party2]"
        parties_pattern = r'parties?:\s*(.+?)(?:\n|$)'
        parties_matches = re.findall(parties_pattern, self.text, re.IGNORECASE)
        if parties_matches:
            party_list = parties_matches[0].split(',')
            parties.extend([p.strip() for p in party_list])
        
        self.metadata['parties'] = list(set(parties))
        return parties
    
    def extract_dates(self):
        """Extract key dates from contract"""
        dates = {
            'effective_date': None,
            'execution_date': None,
            'expiration_date': None,
            'renewal_date': None
        }
        
        # Date patterns
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}'
        
        # Effective date
        effective_pattern = r'effective\s+(?:as of\s+)?(?:date)?:?\s*(' + date_pattern + r')'
        match = re.search(effective_pattern, self.text, re.IGNORECASE)
        if match:
            dates['effective_date'] = match.group(1)
        
        # Expiration date
        expiration_pattern = r'(?:expiration|terminate|renewal|end)\s+(?:date)?:?\s*(' + date_pattern + r')'
        matches = re.findall(expiration_pattern, self.text, re.IGNORECASE)
        if matches:
            dates['expiration_date'] = matches[-1]
        
        self.metadata['dates'] = dates
        return dates
    
    def extract_financial_terms(self):
        """Extract contract value and payment terms"""
        financial = {
            'contract_value': None,
            'currency': None,
            'payment_terms': None,
            'fee_structure': None
        }
        
        # Contract value pattern: $X,XXX.XX
        value_pattern = r'\$[\d,]+(?:\.\d{2})?|\€[\d,]+(?:\.\d{2})?|£[\d,]+(?:\.\d{2})?'
        values = re.findall(value_pattern, self.text)
        if values:
            financial['contract_value'] = values[0]
        
        # Currency detection
        if '$' in self.text:
            financial['currency'] = 'USD'
        elif '€' in self.text:
            financial['currency'] = 'EUR'
        elif '£' in self.text:
            financial['currency'] = 'GBP'
        
        # Payment terms pattern
        payment_pattern = r'(?:payment\s+terms?|net\s+\d+|due\s+within):\s*([^\n]+)'
        match = re.search(payment_pattern, self.text, re.IGNORECASE)
        if match:
            financial['payment_terms'] = match.group(1).strip()
        
        self.metadata['financial'] = financial
        return financial
    
    def extract_slas(self):
        """Extract Service Level Agreements"""
        slas = []
        
        # SLA pattern
        sla_pattern = r'(?:SLA|service\s+level.*?):\s*([^\.]+\.)'
        sla_matches = re.findall(sla_pattern, self.text, re.IGNORECASE)
        slas = [sla.strip() for sla in sla_matches]
        
        self.metadata['slas'] = slas
        return slas
    
    def parse(self):
        """Run complete parsing pipeline"""
        self.extract_text()
        self.extract_parties()
        self.extract_dates()
        self.extract_financial_terms()
        self.extract_slas()
        
        return self.metadata


# Example usage
if __name__ == "__main__":
    parser = ContractParser("sample_contract.pdf")
    metadata = parser.parse()
    print(json.dumps(metadata, indent=2))
