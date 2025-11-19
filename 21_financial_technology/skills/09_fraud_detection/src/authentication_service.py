"""
Authentication Service - Handle user authentication
"""

import uuid
from typing import Dict, Tuple
import bcrypt


class AuthenticationService:
    """Manage user authentication"""

    def __init__(self, storage):
        self.storage = storage

    def create_session(self, user_id: str) -> str:
        """Create authenticated session"""
        session_id = str(uuid.uuid4())
        self.storage.set(f'session:{session_id}', user_id, ex=3600)
        return session_id

    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password"""
        hash_value = self.storage.get(f'password_hash:{user_id}')

        if not hash_value:
            return False

        return bcrypt.checkpw(
            password.encode('utf-8'),
            hash_value.encode('utf-8')
        )

    def set_password(self, user_id: str, password: str):
        """Set user password"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.storage.set(f'password_hash:{user_id}', hashed.decode('utf-8'))

    def validate_session(self, session_id: str) -> Tuple[bool, str]:
        """Validate session"""
        user_id = self.storage.get(f'session:{session_id}')

        if not user_id:
            return False, None

        return True, user_id
