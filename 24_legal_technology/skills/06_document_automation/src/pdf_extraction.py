#!/usr/bin/env python3
"""
PDF text and data extraction
Extract structured information from PDFs for data analysis
"""

import PyPDF2
import pdfplumber
import re
from typing import List, Dict

class PDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
    
    def extract_text(self):
        """Extract all text from PDF."""
        text = ""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def extract_by_page(self) -> Dict[int, str]:
        """Extract text from each page separately."""
        pages = {}
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                pages[i] = page.extract_text()
        return pages
    
    def extract_tables(self) -> List[List]:
        """Extract tables from PDF using pdfplumber."""
        tables = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        return tables
    
    def extract_patterns(self, pattern: str) -> List[str]:
        """Extract content matching regex pattern."""
        text = self.extract_text()
        matches = re.findall(pattern, text, re.MULTILINE)
        return matches
    
    def extract_contact_info(self) -> Dict:
        """Extract common contact information patterns."""
        text = self.extract_text()
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Phone pattern (US)
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, text)
        
        # Date pattern (MM/DD/YYYY or YYYY-MM-DD)
        date_pattern = r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-]\d{1,2}[-]\d{1,2})\b'
        dates = re.findall(date_pattern, text)
        
        return {
            'emails': list(set(emails)),
            'phones': list(set([''.join(phone) for phone in phones])),
            'dates': list(set(dates)),
        }
    
    def extract_financial_info(self) -> Dict:
        """Extract financial information."""
        text = self.extract_text()
        
        # Currency amounts
        amount_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*dollars?\b'
        amounts = re.findall(amount_pattern, text, re.IGNORECASE)
        
        # Interest rates
        rate_pattern = r'\b(\d+(?:\.\d{2})?)\s*%?\s*(?:per\s+)?(?:annum|p\.a\.?|a\.p\.r\.?)\b'
        rates = re.findall(rate_pattern, text, re.IGNORECASE)
        
        return {
            'amounts': amounts,
            'rates': rates,
        }
    
    def extract_legal_references(self) -> Dict:
        """Extract legal citations and references."""
        text = self.extract_text()
        
        # Statute citations
        statute_pattern = r'\b[0-9]+\s+U\.S\.C\.?\s+§\.?\s*[0-9]+|[0-9]+\s+Stat\.?\s+[0-9]+'
        statutes = re.findall(statute_pattern, text)
        
        # Case citations
        case_pattern = r'\b\w+\s+v\.?\s+\w+(?:\s*,\s*[0-9]+\s+\w+\.?\s*\d+)?'
        cases = re.findall(case_pattern, text)
        
        return {
            'statutes': list(set(statutes)),
            'cases': list(set(cases)),
        }


# Example usage
if __name__ == '__main__':
    extractor = PDFExtractor('documents/contract.pdf')
    
    # Extract text
    text = extractor.extract_text()
    print("Extracted text length:", len(text))
    
    # Extract contact info
    contacts = extractor.extract_contact_info()
    print("Emails found:", contacts['emails'])
    print("Phones found:", contacts['phones'])
    
    # Extract financial info
    finances = extractor.extract_financial_info()
    print("Amounts found:", finances['amounts'])
    
    # Extract tables
    tables = extractor.extract_tables()
    print(f"Tables found: {len(tables)}")
