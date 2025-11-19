"""
Encrypted Backup Service for HIPAA Compliance
Ensures all backups are encrypted
"""
import subprocess
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class EncryptedBackupService:
    def __init__(self, encryption_key=None):
        if encryption_key:
            self.key = encryption_key
        else:
            self.key = os.urandom(32)  # AES-256

    def backup_database(self, db_config, backup_path):
        """Backup database and encrypt"""
        # Create backup
        temp_backup = f"{backup_path}.tmp"
        
        # Database dump (example for PostgreSQL)
        subprocess.run([
            'pg_dump',
            '-h', db_config['host'],
            '-U', db_config['user'],
            '-d', db_config['database'],
            '-f', temp_backup
        ])

        # Encrypt backup
        encrypted_path = f"{backup_path}.enc"
        self.encrypt_file(temp_backup, encrypted_path)

        # Remove unencrypted backup
        os.remove(temp_backup)

        return encrypted_path

    def encrypt_file(self, input_path, output_path):
        """Encrypt file using AES-256-GCM"""
        iv = os.urandom(16)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        with open(input_path, 'rb') as f_in:
            plaintext = f_in.read()

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        with open(output_path, 'wb') as f_out:
            # Write IV, tag, and ciphertext
            f_out.write(iv)
            f_out.write(encryptor.tag)
            f_out.write(ciphertext)

    def decrypt_file(self, input_path, output_path):
        """Decrypt backup file"""
        with open(input_path, 'rb') as f_in:
            iv = f_in.read(16)
            tag = f_in.read(16)
            ciphertext = f_in.read()

        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        with open(output_path, 'wb') as f_out:
            f_out.write(plaintext)

    def verify_backup_integrity(self, backup_path):
        """Verify backup can be decrypted"""
        try:
            temp_file = backup_path + '.verify'
            self.decrypt_file(backup_path, temp_file)
            os.remove(temp_file)
            return True
        except Exception as e:
            print(f"Backup verification failed: {e}")
            return False
