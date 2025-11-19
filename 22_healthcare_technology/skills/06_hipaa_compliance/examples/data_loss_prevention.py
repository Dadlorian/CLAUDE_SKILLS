"""
Data Loss Prevention (DLP) Rules for PHI Protection
Prevents unauthorized PHI transmission
"""
import re

class PHI_DLP:
    # Patterns for PHI detection
    PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'mrn': r'\bMRN[:\s-]?\d{6,10}\b',
        'dob': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    }

    @classmethod
    def scan_content(cls, content):
        """Scan content for PHI"""
        findings = []
        
        for phi_type, pattern in cls.PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append({
                    'type': phi_type,
                    'value': match.group(),
                    'position': match.span()
                })
        
        return findings

    @classmethod
    def block_if_phi(cls, content, allowed_channels=None):
        """Block transmission if PHI detected"""
        findings = cls.scan_content(content)
        
        if findings:
            return {
                'blocked': True,
                'reason': 'PHI_DETECTED',
                'findings': findings
            }
        
        return {'blocked': False}

    @classmethod
    def redact_phi(cls, content):
        """Redact PHI from content"""
        redacted = content
        
        for phi_type, pattern in cls.PATTERNS.items():
            redacted = re.sub(pattern, f'[{phi_type.upper()}_REDACTED]', redacted, flags=re.IGNORECASE)
        
        return redacted
