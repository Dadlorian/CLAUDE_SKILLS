"""
HIPAA-Compliant Session Management
Secure session handling with automatic timeout and audit logging
"""
from datetime import datetime, timedelta
import secrets
import hashlib

class HIPAASessionManager:
    def __init__(self, timeout_minutes=15):
        self.timeout_minutes = timeout_minutes
        self.sessions = {}

    def create_session(self, user_id, metadata=None):
        """Create new secure session"""
        session_id = secrets.token_urlsafe(32)
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'metadata': metadata or {},
            'terminated': False
        }
        self.sessions[session_id] = session
        return session_id

    def validate_session(self, session_id):
        """Validate session hasn't timed out"""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        if session['terminated']:
            return False

        time_since_activity = datetime.now() - session['last_activity']
        if time_since_activity > timedelta(minutes=self.timeout_minutes):
            self.terminate_session(session_id, 'TIMEOUT')
            return False

        # Update last activity
        session['last_activity'] = datetime.now()
        return True

    def terminate_session(self, session_id, reason='USER_LOGOUT'):
        """Terminate session and log"""
        if session_id in self.sessions:
            self.sessions[session_id]['terminated'] = True
            self.sessions[session_id]['terminated_at'] = datetime.now()
            self.sessions[session_id]['termination_reason'] = reason
            # Log session termination for audit
            print(f"Session {session_id} terminated: {reason}")

    def get_active_sessions(self, user_id):
        """Get all active sessions for a user"""
        return [s for s in self.sessions.values() 
                if s['user_id'] == user_id and not s['terminated']]
