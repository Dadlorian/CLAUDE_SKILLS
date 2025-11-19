"""
HIPAA-Compliant PHI Encryption Service

Provides encryption/decryption for PHI at rest using AES-256-GCM.
Implements secure key management and rotation.

Requirements:
- cryptography library: pip install cryptography
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

class PHIEncryptionService:
    """
    HIPAA-compliant encryption service for PHI

    Uses AES-256-GCM for authenticated encryption
    Implements key rotation and secure key storage
    """

    def __init__(self, master_key: bytes = None, key_rotation_days: int = 90):
        """
        Initialize encryption service

        Args:
            master_key: Master encryption key (32 bytes for AES-256)
            key_rotation_days: Days before key rotation required
        """
        self.key_rotation_days = key_rotation_days

        if master_key is None:
            # Generate new master key (in production, use HSM or KMS)
            master_key = AESGCM.generate_key(bit_length=256)

        self.master_key = master_key
        self.aesgcm = AESGCM(master_key)
        self.key_created_date = datetime.now()

    @staticmethod
    def generate_master_key() -> bytes:
        """Generate a new 256-bit master key"""
        return AESGCM.generate_key(bit_length=256)

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2

        Args:
            password: User password
            salt: Salt for key derivation (generated if None)

        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # NIST recommendation
            backend=default_backend()
        )

        key = kdf.derive(password.encode())
        return key, salt

    def encrypt_phi(self, plaintext: str, associated_data: Dict = None) -> str:
        """
        Encrypt PHI with authenticated encryption

        Args:
            plaintext: PHI data to encrypt
            associated_data: Additional authenticated data (e.g., patient ID, user ID)

        Returns:
            Base64-encoded encrypted data with nonce
        """
        # Generate random nonce (12 bytes for GCM)
        nonce = os.urandom(12)

        # Prepare associated data for authentication
        if associated_data:
            aad = json.dumps(associated_data, sort_keys=True).encode()
        else:
            aad = None

        # Encrypt
        ciphertext = self.aesgcm.encrypt(
            nonce,
            plaintext.encode('utf-8'),
            aad
        )

        # Create encrypted package
        encrypted_package = {
            'version': '1.0',
            'algorithm': 'AES-256-GCM',
            'nonce': base64.b64encode(nonce).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'associated_data': associated_data,
            'encrypted_at': datetime.now().isoformat()
        }

        return base64.b64encode(json.dumps(encrypted_package).encode()).decode()

    def decrypt_phi(self, encrypted_data: str) -> str:
        """
        Decrypt PHI

        Args:
            encrypted_data: Base64-encoded encrypted package

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails (tampered data or wrong key)
        """
        try:
            # Decode encrypted package
            package = json.loads(base64.b64decode(encrypted_data))

            # Extract components
            nonce = base64.b64decode(package['nonce'])
            ciphertext = base64.b64decode(package['ciphertext'])
            associated_data = package.get('associated_data')

            # Prepare AAD
            if associated_data:
                aad = json.dumps(associated_data, sort_keys=True).encode()
            else:
                aad = None

            # Decrypt
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, aad)

            return plaintext.decode('utf-8')

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_field(self, value: str, field_name: str, patient_id: str) -> str:
        """
        Encrypt a single field with metadata

        Args:
            value: Field value to encrypt
            field_name: Name of field (for auditing)
            patient_id: Patient identifier (for AAD)

        Returns:
            Encrypted value
        """
        associated_data = {
            'field_name': field_name,
            'patient_id': patient_id
        }

        return self.encrypt_phi(value, associated_data)

    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a single field"""
        return self.decrypt_phi(encrypted_value)

    def encrypt_record(self, record: Dict, patient_id: str) -> Dict:
        """
        Encrypt sensitive fields in a patient record

        Args:
            record: Patient record with PHI
            patient_id: Patient identifier

        Returns:
            Record with encrypted PHI fields
        """
        # Define sensitive fields to encrypt
        sensitive_fields = ['ssn', 'diagnosis', 'medications', 'notes', 'address', 'phone']

        encrypted_record = record.copy()

        for field in sensitive_fields:
            if field in record and record[field]:
                encrypted_record[field] = self.encrypt_field(
                    str(record[field]),
                    field,
                    patient_id
                )
                encrypted_record[f'{field}_encrypted'] = True

        encrypted_record['_encryption_metadata'] = {
            'encrypted_at': datetime.now().isoformat(),
            'encryption_version': '1.0',
            'key_id': self.get_key_id()
        }

        return encrypted_record

    def decrypt_record(self, encrypted_record: Dict) -> Dict:
        """
        Decrypt sensitive fields in a patient record

        Args:
            encrypted_record: Record with encrypted PHI

        Returns:
            Record with decrypted PHI fields
        """
        decrypted_record = encrypted_record.copy()

        for key, value in encrypted_record.items():
            if key.endswith('_encrypted') and value:
                field_name = key.replace('_encrypted', '')
                if field_name in encrypted_record:
                    decrypted_record[field_name] = self.decrypt_field(
                        encrypted_record[field_name]
                    )
                    decrypted_record[key] = False

        return decrypted_record

    def needs_key_rotation(self) -> bool:
        """Check if key rotation is needed"""
        days_since_creation = (datetime.now() - self.key_created_date).days
        return days_since_creation >= self.key_rotation_days

    def get_key_id(self) -> str:
        """Get identifier for current key (for key management)"""
        key_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        key_hash.update(self.master_key)
        return base64.b64encode(key_hash.finalize()[:8]).decode()

    def rotate_key(self, new_master_key: bytes) -> 'PHIEncryptionService':
        """
        Create new encryption service with rotated key

        Args:
            new_master_key: New master encryption key

        Returns:
            New encryption service instance
        """
        return PHIEncryptionService(new_master_key, self.key_rotation_days)


# Usage Example
if __name__ == "__main__":
    # Initialize encryption service
    encryption_service = PHIEncryptionService()

    # Example: Encrypt single PHI field
    ssn = "123-45-6789"
    encrypted_ssn = encryption_service.encrypt_field(ssn, "ssn", "PATIENT-001")
    print(f"Encrypted SSN: {encrypted_ssn[:50]}...")

    # Decrypt
    decrypted_ssn = encryption_service.decrypt_field(encrypted_ssn)
    print(f"Decrypted SSN: {decrypted_ssn}")

    # Example: Encrypt patient record
    patient_record = {
        'patient_id': 'PATIENT-001',
        'name': 'John Doe',
        'ssn': '123-45-6789',
        'diagnosis': 'Type 2 Diabetes',
        'medications': 'Metformin 500mg BID',
        'address': '123 Main St, Anytown, USA',
        'phone': '555-1234',
        'date_of_birth': '1970-01-01'
    }

    print("\nOriginal Record:")
    print(json.dumps(patient_record, indent=2))

    # Encrypt sensitive fields
    encrypted_record = encryption_service.encrypt_record(patient_record, 'PATIENT-001')
    print("\nEncrypted Record:")
    print(json.dumps({k: v[:50] + '...' if isinstance(v, str) and len(v) > 50 else v
                     for k, v in encrypted_record.items()}, indent=2))

    # Decrypt record
    decrypted_record = encryption_service.decrypt_record(encrypted_record)
    print("\nDecrypted Record:")
    print(json.dumps(decrypted_record, indent=2))

    # Check key rotation
    print(f"\nKey rotation needed: {encryption_service.needs_key_rotation()}")
    print(f"Current key ID: {encryption_service.get_key_id()}")

    # Key derivation from password (for user-specific encryption)
    password = "SecurePassword123!"
    derived_key, salt = PHIEncryptionService.derive_key_from_password(password)
    print(f"\nDerived key length: {len(derived_key)} bytes")
    print(f"Salt: {base64.b64encode(salt).decode()}")
