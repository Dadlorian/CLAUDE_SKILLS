#!/usr/bin/env python3
"""
GDPR Data Discovery Script
Scans databases and file systems for personal data (PII)
"""

import re
import psycopg2
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class PersonalDataScanner:
    """Scan for personal data in structured and unstructured sources"""
    
    # Regex patterns for common PII
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'phone_us': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    }
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.findings = []
        
    def scan_database(self):
        """Scan PostgreSQL database for personal data"""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_schema, table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name, ordinal_position
        """)
        
        columns = cursor.fetchall()
        
        for schema, table, column, data_type in columns:
            # Check column name for PII indicators
            pii_type = self._classify_column(column)
            
            if pii_type or data_type in ['text', 'varchar', 'char']:
                # Sample data for pattern matching
                sample_query = f"""
                    SELECT "{column}" 
                    FROM "{schema}"."{table}" 
                    WHERE "{column}" IS NOT NULL 
                    LIMIT 100
                """
                cursor.execute(sample_query)
                samples = cursor.fetchall()
                
                # Check for PII patterns
                for row in samples:
                    if row[0]:
                        detected_pii = self._detect_patterns(str(row[0]))
                        if detected_pii or pii_type:
                            self.findings.append({
                                'source': 'database',
                                'location': f"{schema}.{table}.{column}",
                                'pii_type': pii_type or detected_pii,
                                'data_type': data_type,
                                'sample_count': len(samples),
                                'confidence': 'high' if pii_type else 'medium'
                            })
                            break
        
        cursor.close()
        conn.close()
        return self.findings
    
    def scan_files(self, directory):
        """Scan files for personal data"""
        path = Path(directory)
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.txt', '.csv', '.log', '.json']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(100000)  # Read first 100KB
                        
                    detected_pii = self._detect_patterns(content)
                    if detected_pii:
                        self.findings.append({
                            'source': 'file',
                            'location': str(file_path),
                            'pii_type': detected_pii,
                            'file_type': file_path.suffix,
                            'file_size': file_path.stat().st_size,
                            'confidence': 'medium'
                        })
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
        
        return self.findings
    
    def _classify_column(self, column_name):
        """Classify column based on name"""
        column_lower = column_name.lower()
        
        pii_indicators = {
            'email': ['email', 'e_mail', 'mail'],
            'name': ['first_name', 'last_name', 'full_name', 'name'],
            'phone': ['phone', 'telephone', 'mobile'],
            'address': ['address', 'street', 'city', 'zip', 'postal'],
            'dob': ['birth_date', 'dob', 'date_of_birth'],
            'ssn': ['ssn', 'social_security', 'national_id'],
            'ip': ['ip_address', 'ip_addr'],
            'user_id': ['user_id', 'customer_id', 'account_id']
        }
        
        for pii_type, indicators in pii_indicators.items():
            if any(indicator in column_lower for indicator in indicators):
                return pii_type
        
        return None
    
    def _detect_patterns(self, text):
        """Detect PII using regex patterns"""
        for pii_type, pattern in self.PATTERNS.items():
            if re.search(pattern, text):
                return pii_type
        return None
    
    def generate_report(self, output_file='pii_discovery_report.json'):
        """Generate discovery report"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'total_findings': len(self.findings),
            'findings_by_type': {},
            'findings_by_source': {},
            'detailed_findings': self.findings
        }
        
        # Aggregate by type
        for finding in self.findings:
            pii_type = finding['pii_type']
            source = finding['source']
            
            report['findings_by_type'][pii_type] = report['findings_by_type'].get(pii_type, 0) + 1
            report['findings_by_source'][source] = report['findings_by_source'].get(source, 0) + 1
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report generated: {output_file}")
        print(f"Total findings: {report['total_findings']}")
        print(f"By type: {report['findings_by_type']}")
        return report

# Example usage
if __name__ == '__main__':
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'production',
        'user': 'readonly_user',
        'password': 'secure_password'
    }
    
    scanner = PersonalDataScanner(db_config)
    
    # Scan database
    print("Scanning database...")
    scanner.scan_database()
    
    # Scan file systems
    print("Scanning files...")
    scanner.scan_files('/data/exports')
    scanner.scan_files('/var/log/applications')
    
    # Generate report
    scanner.generate_report()
