#!/usr/bin/env python3
"""Security Utilities - Encryption and authentication"""

import hashlib
import secrets
from typing import Tuple

class SecurityUtils:
    """Security-related utilities"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely"""
        salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"

    @staticmethod
    def verify_password(password: str, hash_value: str) -> bool:
        """Verify password"""
        try:
            salt, hash_hex = hash_value.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except:
            return False

    @staticmethod
    def encrypt_data(plaintext: str, key: bytes) -> bytes:
        """Encrypt data"""
        from cryptography.fernet import Fernet
        cipher = Fernet(key)
        return cipher.encrypt(plaintext.encode())

    @staticmethod
    def decrypt_data(ciphertext: bytes, key: bytes) -> str:
        """Decrypt data"""
        from cryptography.fernet import Fernet
        cipher = Fernet(key)
        return cipher.decrypt(ciphertext).decode()

    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
