"""Database Field-Level Encryption for PHI at Rest"""
from cryptography.fernet import Fernet
import base64

class DatabaseEncryption:
    def __init__(self, key=None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_field(self, plaintext):
        """Encrypt a database field"""
        if plaintext is None:
            return None
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt_field(self, ciphertext):
        """Decrypt a database field"""
        if ciphertext is None:
            return None
        return self.cipher.decrypt(ciphertext.encode()).decode()
