# Encryption Reference

## Introduction

Encryption is a fundamental security control that protects data confidentiality through cryptographic transformation. This reference covers encryption at rest, encryption in transit, key management, and cryptographic best practices for cloud environments.

## Encryption Fundamentals

### Cryptographic Primitives

**Symmetric Encryption**:
- **Algorithms**: AES-256, ChaCha20
- **Use Cases**: Data at rest, bulk data encryption
- **Characteristics**: Fast, same key for encryption and decryption
- **Key Size**: 256-bit minimum for production

**Asymmetric Encryption**:
- **Algorithms**: RSA-4096, ECC (P-256, P-384)
- **Use Cases**: Key exchange, digital signatures, certificate-based authentication
- **Characteristics**: Slower, public/private key pair
- **Key Size**: RSA 4096-bit or ECC 256-bit minimum

**Hashing**:
- **Algorithms**: SHA-256, SHA-384, SHA-512, SHA3, BLAKE2
- **Use Cases**: Data integrity, password storage (with salt and KDF), digital signatures
- **Characteristics**: One-way, deterministic, collision-resistant
- **Avoid**: MD5, SHA-1 (cryptographically broken)

**Key Derivation Functions (KDF)**:
- **Algorithms**: PBKDF2, bcrypt, scrypt, Argon2
- **Use Cases**: Password hashing, key stretching
- **Parameters**: High iteration count/work factor (adjustable for CPU cost)

### Encryption Modes

**Block Cipher Modes**:
- **GCM (Galois/Counter Mode)**: Authenticated encryption, parallelizable, recommended
- **CBC (Cipher Block Chaining)**: Legacy, requires separate MAC, padding oracle risks
- **CTR (Counter)**: Stream cipher mode, parallelizable
- **Avoid**: ECB (Electronic Codebook) - pattern leakage

**Authenticated Encryption**:
- **AES-GCM**: Most common, NIST recommended
- **ChaCha20-Poly1305**: Alternative to AES, better for software implementations
- **Benefits**: Confidentiality + integrity + authenticity in one operation

## Encryption at Rest

### Cloud Storage Encryption

**AWS S3 Encryption**:
- **SSE-S3**: S3-managed keys (AES-256)
- **SSE-KMS**: KMS-managed keys, envelope encryption, audit trail
- **SSE-C**: Customer-provided keys (customer manages keys)
- **Client-Side Encryption**: Encrypt before upload, AWS SDK or custom
- **Default Encryption**: Enable bucket default encryption (mandatory)

**Azure Storage Encryption**:
- **SSE**: Storage Service Encryption with platform-managed keys (enabled by default)
- **CMK**: Customer-managed keys in Azure Key Vault
- **Client-Side Encryption**: Azure Storage Client Library

**GCP Cloud Storage Encryption**:
- **Google-managed keys**: Default encryption
- **Customer-managed keys (CMEK)**: Keys in Cloud KMS
- **Customer-supplied keys (CSEK)**: Customer provides keys with each request
- **Client-Side Encryption**: Encrypt before upload

**Best Practices**:
- Enable encryption by default on all storage
- Use KMS/Key Vault managed keys for audit trail
- Encrypt sensitive data at application layer for defense-in-depth
- Never store encryption keys with encrypted data

### Database Encryption

**Transparent Data Encryption (TDE)**:
- **AWS RDS**: Encryption at rest for MySQL, PostgreSQL, Oracle, SQL Server, MariaDB
- **Azure SQL**: TDE enabled by default
- **GCP Cloud SQL**: Encryption at rest enabled by default
- **Scope**: Encrypts data files, logs, backups
- **Performance**: Minimal overhead (<5%)

**Field-Level Encryption**:
- Encrypt specific columns/fields (e.g., SSN, credit card)
- Application-layer encryption before database storage
- Searchable encryption for encrypted data (format-preserving encryption)
- Key management per field or per tenant

**Database Backup Encryption**:
- Always encrypt backups (at rest)
- Use same or separate keys from production data
- Encrypt automated and manual backups
- Encrypt snapshots and exports

**Best Practices**:
- Enable TDE on all production databases
- Use separate keys for different data classifications
- Encrypt connection strings and database credentials
- Implement column-level encryption for PCI/PII data

### Compute Encryption

**Disk Encryption**:
- **AWS EBS**: Encryption enabled by default (as of 2019)
- **Azure Managed Disks**: Azure Disk Encryption (ADE), platform-managed or CMK
- **GCP Persistent Disks**: Encryption at rest enabled by default
- **VM Disk Encryption**: BitLocker (Windows), dm-crypt/LUKS (Linux)

**Ephemeral Storage**:
- Instance store volumes: Not persistent, encrypt if used
- Temporary directories: Consider encrypting sensitive temp data
- Memory encryption: AMD SEV, Intel SGX for confidential computing

**Container Image Encryption**:
- Encrypt container images at rest (registry encryption)
- Layer-level encryption for sensitive layers
- Runtime decryption when pulling images
- Sign images for integrity and authenticity

### Envelope Encryption

**Concept**: Encrypt data with data encryption key (DEK), encrypt DEK with key encryption key (KEK)

**Benefits**:
- Performance: Encrypt large data with fast symmetric key (DEK)
- Security: Protect DEK with KMS-managed KEK
- Rotation: Rotate KEK without re-encrypting all data
- Audit: All DEK requests logged in KMS

**Implementation**:
```
1. Generate DEK from KMS (plaintext + encrypted DEK)
2. Encrypt data with plaintext DEK
3. Store encrypted data + encrypted DEK together
4. Discard plaintext DEK from memory
5. To decrypt: Request KMS to decrypt DEK, then decrypt data
```

**Cloud KMS Support**:
- AWS KMS: GenerateDataKey API
- Azure Key Vault: Wrap/Unwrap operations
- GCP Cloud KMS: Encrypt/Decrypt DEK

## Encryption in Transit

### TLS/SSL Configuration

**TLS Version**:
- **Use**: TLS 1.3 (preferred), TLS 1.2 (minimum)
- **Avoid**: TLS 1.1, TLS 1.0, SSL 3.0, SSL 2.0 (deprecated, insecure)

**Cipher Suites** (Recommended):
```
TLS 1.3:
- TLS_AES_256_GCM_SHA384
- TLS_AES_128_GCM_SHA256
- TLS_CHACHA20_POLY1305_SHA256

TLS 1.2:
- TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
- TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
- TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
```

**Avoid Weak Ciphers**:
- RC4, 3DES, DES, EXPORT ciphers
- NULL encryption ciphers
- Anonymous Diffie-Hellman (ADH)
- MD5-based ciphers

**TLS Best Practices**:
- Enforce TLS 1.2+ for all connections
- Use forward secrecy (ECDHE, DHE)
- Implement HSTS (HTTP Strict Transport Security)
- Use strong cipher suites only
- Regular TLS/SSL certificate rotation
- Monitor certificate expiration

### Certificate Management

**Certificate Authorities**:
- **AWS Certificate Manager (ACM)**: Free SSL/TLS certificates, auto-renewal
- **Azure Key Vault Certificates**: Integrated certificate management
- **GCP Certificate Manager**: Managed SSL certificates
- **Let's Encrypt**: Free, automated, DV certificates
- **Commercial CAs**: DigiCert, GlobalSign for OV/EV certificates

**Certificate Types**:
- **Domain Validation (DV)**: Basic domain ownership verification
- **Organization Validation (OV)**: Organization identity verification
- **Extended Validation (EV)**: Highest level, displays organization in browser
- **Wildcard**: Covers *.domain.com
- **Multi-Domain (SAN)**: Multiple domains in one certificate

**Certificate Lifecycle**:
1. **Generation**: Create CSR, submit to CA
2. **Validation**: DV/OV/EV validation process
3. **Issuance**: CA issues certificate
4. **Deployment**: Install on servers/load balancers
5. **Monitoring**: Track expiration (30 days before expiry alert)
6. **Renewal**: Renew before expiration (automated when possible)
7. **Revocation**: CRL/OCSP for compromised certificates

**Best Practices**:
- Automate certificate renewal (ACM, cert-manager, ACME)
- Use short-lived certificates (90 days recommended)
- Implement certificate pinning for critical connections (with caution)
- Monitor certificate transparency logs
- Store private keys in HSM or key vaults
- Never commit private keys to version control

### Mutual TLS (mTLS)

**Use Cases**:
- Service-to-service authentication
- API authentication
- Zero trust networking
- Microservices communication

**Implementation**:
- Client presents certificate to server
- Server presents certificate to client
- Both validate certificates against trusted CAs
- Establishes encrypted, mutually authenticated connection

**Service Mesh mTLS**:
- **Istio**: Automatic mTLS between services
- **Linkerd**: Transparent mTLS encryption
- **Consul Connect**: Service mesh with mTLS
- **AWS App Mesh**: TLS encryption for services

**mTLS Best Practices**:
- Use short-lived certificates (hours to days)
- Automate certificate provisioning (SPIFFE/SPIRE)
- Implement certificate rotation without downtime
- Use service mesh for transparent mTLS
- Monitor certificate validation failures

### VPN and Private Connectivity

**VPN Encryption**:
- **Site-to-Site VPN**: IPsec with AES-256, SHA-256
- **Client VPN**: OpenVPN, WireGuard, IKEv2
- **Cloud VPN Services**:
  - AWS VPN: IPsec, supports BGP
  - Azure VPN Gateway: IKEv2, OpenVPN
  - GCP Cloud VPN: IPsec, HA VPN recommended

**Private Connectivity** (Encrypted by default):
- **AWS PrivateLink**: Private connections to AWS services
- **Azure Private Link**: Private endpoints for Azure services
- **GCP Private Service Connect**: Private connectivity to Google services
- **Direct Connect / ExpressRoute / Interconnect**: Dedicated connections (add encryption for sensitive data)

## Key Management

### Cloud Key Management Services

**AWS KMS**:
- **Features**: Envelope encryption, automatic key rotation, audit logging
- **Key Types**: Customer managed keys (CMK), AWS managed keys, AWS owned keys
- **Regions**: Regional service, multi-region keys available
- **Integration**: Native integration with 100+ AWS services
- **FIPS 140-2 Level 2**: Standard (Level 3 with CloudHSM)

**Azure Key Vault**:
- **Features**: Keys, secrets, certificates in one service
- **Tiers**: Standard (software), Premium (HSM-backed)
- **Key Types**: RSA, EC, symmetric (AES)
- **Access**: RBAC-based access control
- **Integration**: Native Azure service integration

**GCP Cloud KMS**:
- **Features**: Symmetric and asymmetric keys, automatic rotation
- **Protection Levels**: Software, HSM (FIPS 140-2 Level 3)
- **Location**: Regional, multi-regional, global keys
- **Integration**: Native GCP service integration
- **External Key Manager (EKM)**: Use external key management systems

### Key Rotation

**Automatic Rotation**:
- **AWS KMS**: Annual automatic rotation for CMKs (365 days)
- **Azure Key Vault**: Manual or automated via policies
- **GCP Cloud KMS**: Automatic rotation (configurable: 30, 90 days)

**Rotation Strategy**:
- **Frequency**: 90 days for high-security, 365 days standard
- **Process**: Create new key version, re-encrypt or use envelope encryption
- **Backward Compatibility**: Keep old key versions for decryption
- **Versioning**: Track key versions and usage

**Manual Rotation**:
1. Create new key
2. Update applications to use new key for encryption
3. Background job to re-encrypt existing data (if needed)
4. Deprecate old key after re-encryption complete
5. Delete old key after retention period

### Hardware Security Modules (HSM)

**Cloud HSM Services**:
- **AWS CloudHSM**: FIPS 140-2 Level 3, single-tenant, customer managed
- **Azure Dedicated HSM**: FIPS 140-2 Level 3, SafeNet Luna Network HSMs
- **GCP Cloud HSM**: FIPS 140-2 Level 3, integrated with Cloud KMS

**Use Cases**:
- Regulatory requirements (PCI DSS, HIPAA, FedRAMP High)
- Bring Your Own Key (BYOK) scenarios
- Cryptographic operations requiring Level 3 certification
- High-performance cryptographic operations

**Considerations**:
- Higher cost than software-based KMS
- Customer responsible for HSM cluster management
- Key backup and disaster recovery complexity
- Requires specialized knowledge

### Bring Your Own Key (BYOK)

**Supported Scenarios**:
- **AWS**: Import key material into KMS
- **Azure**: Import keys into Key Vault (HSM or software)
- **GCP**: External Key Manager (EKM) for external key management

**Process**:
1. Generate key in on-premises HSM
2. Wrap key with cloud provider's public key
3. Import wrapped key into cloud KMS
4. Use imported key for encryption operations

**Considerations**:
- Customer responsible for key lifecycle
- Cannot use automatic rotation (manual rotation required)
- Higher operational complexity
- Compliance benefits (key material never generated in cloud)

### Key Management Best Practices

**Key Lifecycle**:
1. **Generation**: Use cryptographically secure RNG, sufficient entropy
2. **Storage**: HSM or KMS, never in plaintext
3. **Distribution**: Encrypted channels, certificate-based authentication
4. **Usage**: Principle of least privilege, audit all operations
5. **Rotation**: Regular rotation schedule
6. **Archival**: Retain for decryption of old data
7. **Destruction**: Secure deletion, crypto-shredding

**Access Control**:
- Principle of least privilege for key access
- Separate key administrators from key users
- No single person should have complete key control
- Multi-party authorization for sensitive operations
- Regular access reviews

**Audit and Monitoring**:
- Log all key operations (CloudTrail, Azure Monitor, Cloud Audit Logs)
- Alert on key policy changes
- Monitor key usage patterns (anomaly detection)
- Track key age and rotation status
- Regular key inventory and compliance checks

**Separation of Duties**:
- **Key Administrators**: Create, rotate, delete keys
- **Key Users**: Encrypt/decrypt operations
- **Auditors**: Read-only access to logs and key metadata
- No overlapping permissions between roles

## Cryptographic Best Practices

### Secure Random Number Generation

**Use Cryptographically Secure RNGs**:
- `/dev/urandom` (Linux)
- `CryptGenRandom` (Windows)
- Cloud provider services (KMS GenerateRandom)
- Language-specific: `secrets` module (Python), `crypto.randomBytes` (Node.js)

**Avoid**:
- `rand()`, `srand()` (predictable)
- `/dev/random` (can block, use `/dev/urandom`)
- `Math.random()` (JavaScript - not cryptographically secure)
- Time-based seeds

### Salt and IV Best Practices

**Salt** (for password hashing, KDFs):
- Minimum 128-bit (16 bytes) random salt
- Unique salt per password/user
- Store salt with hashed password (not secret)
- Never reuse salts

**Initialization Vector (IV)** (for encryption):
- Must be random and unique for each encryption operation
- Same size as block size (128-bit for AES)
- Store IV with ciphertext (not secret, but must not be predictable)
- Never reuse IV with same key (nonce-reuse attacks)

### Key Derivation

**PBKDF2**:
```python
import hashlib
iterations = 100000  # Minimum, increase over time
salt = os.urandom(16)
key = hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=32)
```

**Argon2** (recommended for password hashing):
```python
import argon2
hasher = argon2.PasswordHasher(
    time_cost=2,        # Iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,      # Threads
    hash_len=32,
    salt_len=16
)
hash = hasher.hash(password)
```

### Cryptographic Agility

**Design for Algorithm Migration**:
- Version field in encrypted data format
- Algorithm identifier in data structure
- Support multiple algorithms simultaneously during transition
- Plan for post-quantum cryptography migration

**Example Encrypted Data Format**:
```json
{
  "version": "1",
  "algorithm": "AES-256-GCM",
  "iv": "base64-encoded-iv",
  "ciphertext": "base64-encoded-ciphertext",
  "tag": "base64-encoded-auth-tag",
  "key_id": "kms-key-identifier"
}
```

## Compliance and Encryption

### Regulatory Requirements

**PCI DSS 4.0**:
- Requirement 3: Protect stored cardholder data
  - AES-256 or equivalent
  - Key management procedures
- Requirement 4: Encrypt cardholder data in transit
  - TLS 1.2+ with strong ciphers

**HIPAA**:
- 164.312(a)(2)(iv): Encryption and decryption
- 164.312(e)(1): Transmission security
- Not mandatory but addressable (implement or document why not)

**GDPR**:
- Article 32: Security of processing
- Encryption of personal data recommended
- Pseudonymization and encryption as security measures

**FedRAMP**:
- FIPS 140-2 validated encryption modules
- NIST 800-53 cryptographic controls
- FIPS 140-2 Level 2 minimum (Level 3 for High impact)

### Encryption for Different Data Classifications

**Public Data**: Encryption optional, integrity important
**Internal Data**: TLS in transit, optional at rest
**Confidential Data**: Encryption at rest and in transit, access controls
**Restricted/Regulated**: Strong encryption, HSM, strict key management, audit logging

## Testing and Validation

### SSL/TLS Testing
- **SSL Labs**: https://www.ssllabs.com/ssltest/
- **testssl.sh**: Command-line SSL/TLS testing tool
- **nmap**: `nmap --script ssl-enum-ciphers -p 443 domain.com`

### Encryption Verification
- Verify encryption at rest enabled (cloud console, CLI, APIs)
- Test data cannot be read without proper keys
- Validate key rotation procedures
- Confirm encrypted backups and snapshots
- Penetration testing for encryption bypasses

### Compliance Validation
- CIS Benchmark checks for encryption
- Cloud provider compliance tools (AWS Config, Azure Policy, GCP Policy)
- Third-party CSPM tools (Prisma Cloud, Wiz, Orca)
- Manual compliance validation and attestation

## Common Encryption Anti-Patterns

### Anti-Pattern 1: Weak or No Encryption
**Problem**: Using deprecated algorithms (DES, 3DES, RC4, MD5)
**Solution**: AES-256, SHA-256+, modern algorithms

### Anti-Pattern 2: Storing Keys with Data
**Problem**: Encryption keys stored on same disk/bucket as encrypted data
**Solution**: Key management service (KMS), HSM, external key vault

### Anti-Pattern 3: Hardcoded Keys
**Problem**: Encryption keys in source code or configuration
**Solution**: KMS, environment-specific key management, secrets management

### Anti-Pattern 4: No Key Rotation
**Problem**: Using same encryption key indefinitely
**Solution**: Automated key rotation (90-365 days)

### Anti-Pattern 5: Reusing IVs/Nonces
**Problem**: Same IV used multiple times with same key
**Solution**: Generate new random IV for each encryption operation

### Anti-Pattern 6: Encryption Without Authentication
**Problem**: Using encryption modes without integrity (CBC without HMAC)
**Solution**: Authenticated encryption (AES-GCM, ChaCha20-Poly1305)

### Anti-Pattern 7: Rolling Your Own Crypto
**Problem**: Custom cryptographic implementations
**Solution**: Use well-tested libraries (OpenSSL, libsodium, cloud KMS SDKs)

## Tools and Libraries

### Cryptographic Libraries
- **OpenSSL**: Industry-standard cryptographic library (C)
- **libsodium**: Modern, easy-to-use crypto library
- **Bouncy Castle**: Cryptography for Java, C#
- **cryptography.io**: Python cryptography library
- **Go crypto**: Standard library crypto packages

### Cloud SDKs
- **AWS Encryption SDK**: Client-side encryption with KMS
- **Azure SDK**: Key Vault and encryption services
- **GCP Tink**: Multi-language crypto library from Google

### Testing Tools
- **testssl.sh**: SSL/TLS testing
- **OpenSSL s_client**: Manual TLS testing
- **Qualys SSL Labs**: Online SSL testing
- **Nmap**: Network and SSL/TLS scanning
- **Metasploit**: Encryption vulnerability testing (authorized testing only)

## Resources

### Standards and Guidelines
- NIST SP 800-57: Key Management
- NIST SP 800-52: TLS Implementation
- NIST SP 800-175B: Cryptographic Algorithm Validation
- FIPS 140-2/140-3: Cryptographic Module Validation

### Cloud Provider Documentation
- AWS KMS: https://docs.aws.amazon.com/kms/
- Azure Key Vault: https://docs.microsoft.com/azure/key-vault/
- GCP Cloud KMS: https://cloud.google.com/kms/docs

### Learning Resources
- Cryptography I (Coursera - Stanford)
- The Cryptographic Doom Principle (blog post)
- Crypto 101 (free book): https://www.crypto101.io/
- OWASP Cryptographic Storage Cheat Sheet
