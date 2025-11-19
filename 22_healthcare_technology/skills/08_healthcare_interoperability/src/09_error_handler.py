#!/usr/bin/env python3
"""Error Handling - Healthcare-specific error handling"""

import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class HealthcareException(Exception):
    """Base healthcare exception"""
    def __init__(self, code: str, message: str, details: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

class PatientNotFound(HealthcareException):
    def __init__(self, mrn: str):
        super().__init__('PATIENT_NOT_FOUND', f'Patient {mrn} not found')

class InvalidMessageFormat(HealthcareException):
    def __init__(self, details: str):
        super().__init__('INVALID_MESSAGE', f'Invalid message format: {details}')

class TerminologyError(HealthcareException):
    def __init__(self, code: str, system: str):
        super().__init__('TERMINOLOGY_ERROR', f'Invalid code {code} in system {system}')

class SecurityException(HealthcareException):
    def __init__(self, reason: str):
        super().__init__('SECURITY_ERROR', f'Security violation: {reason}')

def log_exception(exc: Exception):
    """Log exception with healthcare context"""
    if isinstance(exc, HealthcareException):
        logger.error(f"{exc.code}: {exc.message}", extra=exc.details)
    else:
        logger.error(f"Unexpected error: {exc}")

def handle_gracefully(func):
    """Decorator for graceful error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HealthcareException as e:
            log_exception(e)
            return {'status': 'error', 'code': e.code, 'message': e.message}
        except Exception as e:
            log_exception(e)
            return {'status': 'error', 'code': 'INTERNAL_ERROR', 'message': str(e)}
    return wrapper
