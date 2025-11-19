"""
EHR Audit Logging
HIPAA-compliant audit logging for all PHI access
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import json

class EHRAuditLogger:
    """HIPAA-compliant audit logger"""

    def __init__(self, log_file='audit.log'):
        self.logger = logging.getLogger('EHR_AUDIT')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_phi_access(
        self,
        user_id: str,
        patient_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True
    ):
        """Log PHI access event"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'PHI_ACCESS',
            'user_id': user_id,
            'patient_id': patient_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'ip_address': ip_address,
            'success': success
        }
        
        self.logger.info(json.dumps(log_entry))

    def log_authentication(
        self,
        user_id: str,
        event: str,
        ip_address: Optional[str] = None,
        success: bool = True
    ):
        """Log authentication events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'AUTHENTICATION',
            'user_id': user_id,
            'event': event,
            'ip_address': ip_address,
            'success': success
        }
        
        self.logger.info(json.dumps(log_entry))

# Example usage
if __name__ == '__main__':
    audit = EHRAuditLogger()
    
    # Log patient chart access
    audit.log_phi_access(
        user_id='DR123',
        patient_id='PAT456',
        action='VIEW',
        resource_type='Patient',
        ip_address='192.168.1.100'
    )
    
    # Log login
    audit.log_authentication(
        user_id='DR123',
        event='LOGIN',
        ip_address='192.168.1.100',
        success=True
    )
