# Encryption Standards Reference

## Symmetric Encryption Algorithms

### AES (Advanced Encryption Standard)

#### Specifications
```
Standard: NIST FIPS 197
Block Size: 128 bits (16 bytes)
Key Sizes: 128, 192, 256 bits
Rounds: 10 (AES-128), 12 (AES-192), 14 (AES-256)
Security: Strong for all variants
Performance: Excellent, hardware acceleration available
```

#### Key Sizes and Equivalence

| AES Variant | Key Size | Equivalent RSA | Secure Until |
|-------------|----------|----------------|--------------|
| AES-128 | 128 bits | RSA-3072 | 2030+ |
| AES-192 | 192 bits | RSA-7680 | 2040+ |
| AES-256 | 256 bits | RSA-15360 | 2100+ |

#### Modes of Operation

**ECB (Electronic Codebook)**
```
Characteristics:
- Block → Same ciphertext
- Deterministic
- NOT SECURE for larger messages
- Pattern leakage

Use: Encryption of single blocks only
Warning: Do NOT use for messages > 1 block
```

**CBC (Cipher Block Chaining)**
```
Characteristics:
- IV (Initialization Vector) required
- Blocks chained together
- Each block depends on previous
- Requires padding

Advantages:
- Deterministic eliminated
- Secure for messages
- Standard practice

Disadvantages:
- Padding oracle vulnerability
- Parallelization limited
- Requires IV management
```

**CTR (Counter Mode)**
```
Characteristics:
- Converts block cipher to stream
- IV + counter
- Parallel encryption possible
- No padding needed

Advantages:
- Parallelizable
- No padding
- Deterministic (with nonce)
- Streaming

Use: TLS, IPsec, modern protocols
```

**GCM (Galois/Counter Mode)**
```
Characteristics:
- Authenticated encryption
- Combines CTR mode + authentication
- Detects tampering
- AEAD cipher

Advantages:
- Authentication included
- No separate MAC needed
- Parallelizable
- Streaming

Recommended for:
- TLS 1.3
- IPsec IKEv2
- All modern protocols
Status: Modern best practice
```

**CCM (Counter with CBC-MAC)**
```
Characteristics:
- Combines CTR + CBC-MAC
- Authenticated encryption
- Less parallel than GCM

Use:
- IoT/embedded (lower overhead)
- WiFi Protected Access
- Some RFID protocols
```

### ChaCha20-Poly1305

#### Specifications
```
Stream Cipher: ChaCha20
Authentication: Poly1305 MAC
Combined: ChaCha20-Poly1305 (AEAD)
Block Size: 64 bytes
Key Size: 256 bits
Nonce: 96 bits
```

#### Characteristics
```
Performance:
- Excellent without AES acceleration
- Better than AES on older processors
- Similar to AES-GCM on modern CPU

Security:
- No known vulnerabilities
- Well-analyzed
- Growing adoption

Advantages:
- Hardware-independent performance
- No padding needed
- Authentication included
- Modern design
```

#### When to Use

```
ChaCha20 preferred when:
- No AES-NI hardware acceleration
- IoT/embedded devices
- Mobile devices
- Performance-critical

AES-GCM preferred when:
- Hardware acceleration available
- Standardized requirement
- Ubiquitous support needed
```

### 3DES (Triple DES)

#### Specifications
```
Standard: NIST legacy
Block Size: 64 bits
Key Size: 192 bits (3x 64-bit keys)
Rounds: 48 (16 per pass × 3)
Security: Weak
Performance: Slow
```

#### Status
```
DEPRECATED for new deployments

Reasons:
- Small block size (64-bit)
- Vulnerable to birthday attack
- Slow performance
- AES superior

Remaining uses:
- Legacy system compatibility
- Hardware device support
- Transition period
- Financial legacy systems

Migration: Move to AES-256
```

## Asymmetric Encryption

### RSA (Rivest-Shamir-Adleman)

#### Specifications
```
Key Sizes: 1024, 2048, 3072, 4096, 8192 bits
Operation: Modular exponentiation
Security: Based on integer factorization
```

#### Key Size Recommendations

| Key Size | Security | Use Case | Expiration |
|----------|----------|----------|-----------|
| 1024-bit | Weak | Legacy only | Deprecated |
| 2048-bit | Adequate | General | 2030 |
| 3072-bit | Strong | Long-term | 2040 |
| 4096-bit | Very Strong | High-security | 2100+ |

#### Recommended Timeline
```
Current (2025):
- Use RSA-2048 minimum
- 3072 preferred
- 4096 for high-security

By 2030:
- Retire RSA-1024
- Prefer 3072+

By 2040:
- Retire 2048
- Use 3072+ only
```

### ECDSA (Elliptic Curve Digital Signature Algorithm)

#### Specifications
```
Curves: P-256, P-384, P-521, Curve25519
Key Size: Much smaller than RSA
Security: Equivalent to larger RSA

Equivalence:
- ECDSA P-256 ≈ RSA 3072
- ECDSA P-384 ≈ RSA 7680
- ECDSA P-521 ≈ RSA 15360
```

#### Advantages Over RSA
```
Smaller keys:
- P-256 = 256 bits ≈ RSA-3072
- Faster operations
- Less bandwidth

Performance:
- Faster key generation
- Faster signing
- Faster verification
- Better for certificates

Modern protocols:
- ECDSA standard
- TLS 1.3
- SSH keys
- Certificate authorities
```

#### Recommended Curves

```
ECDSA P-256:
- General use
- Web certificates
- TLS
- Wide support

ECDSA P-384:
- High security
- Long-term validity
- Government
- Financial

Curve25519:
- Modern systems
- WireGuard
- Signal
- Performance
- Resistance to side-channels
```

## Hash Functions

### SHA (Secure Hash Algorithm) Family

#### SHA-1 (Deprecated)
```
Output: 160 bits
Status: DEPRECATED
Reason: Collision attacks published
Use: Legacy only (phase out)
Timeline: Retire by 2025
```

#### SHA-2 Family
```
SHA-256:
- Output: 256 bits
- Security: Strong
- Use: TLS, certificates, general
- Recommended: Yes

SHA-384:
- Output: 384 bits
- Security: Very strong
- Use: High-security requirements
- Recommended: Yes

SHA-512:
- Output: 512 bits
- Security: Very strong
- Use: Long-term storage
- Recommended: Yes
```

#### SHA-3 (Modern)
```
Output: 256, 384, 512 bits
Status: Modern standard
Performance: Good
Security: Strong
Adoption: Growing (not yet ubiquitous)
Use: New projects, long-term
```

### BLAKE2/BLAKE3

#### Specifications
```
BLAKE2:
- Output: 256 or 512 bits
- Performance: Faster than MD5
- Security: Excellent
- Status: Mature

BLAKE3:
- Output: 256 bits (arbitrary)
- Performance: Fastest
- Parallelizable
- Status: Emerging
```

#### When to Use
```
BLAKE2:
- Performance critical
- New protocols
- Modern systems

BLAKE3:
- Very high performance needed
- Parallelizable operations
- Future-proof systems
- Emerging standard
```

## Hash Selection Guide

| Use Case | Hash | Reasoning |
|----------|------|-----------|
| Passwords | bcrypt/scrypt | Slow, salt |
| Certificates | SHA-256 | Standard, strong |
| HMAC | SHA-256+ | Strong, common |
| Data integrity | SHA-256 | Standard |
| Blockchain | SHA-256 | Proven |
| Performance | BLAKE2/3 | Fast |
| Long-term | SHA-512 | Maximum security |

## Key Exchange & Derivation

### Diffie-Hellman (DH)

#### Classic DH
```
Key Sizes:
- DH-1024: Weak (deprecated)
- DH-2048: Minimum acceptable
- DH-3072: Recommended
- DH-4096: Strong

Perfect Forward Secrecy:
- Ephemeral DH (DHE)
- New key per session
- Session compromise doesn't expose past

Vulnerability:
- Susceptible to MITM without authentication
- Always pair with signature algorithm
```

### Elliptic Curve DH (ECDH)

#### Curves
```
P-256 (prime256v1):
- Widely supported
- TLS standard
- Sufficient security

P-384 (secp384r1):
- Stronger
- Government standard
- Good performance

P-521 (secp521r1):
- Very strong
- Less common

Curve25519:
- Modern, fast
- Secure
- Growing adoption
- Resistance to side-channels
```

### Perfect Forward Secrecy (PFS)

#### Implementation
```
Requirement: Use ephemeral keys
- DHE (Diffie-Hellman Ephemeral)
- ECDHE (EC DH Ephemeral)

Benefit:
- Session compromise doesn't expose keys
- Long-term key compromise doesn't expose past sessions
- Modern best practice

TLS 1.3 Requirement:
- All handshakes use PFS
- Mandatory ephemeral keys
- No static key exchange
```

## Key Derivation Functions

### PBKDF2 (Password-Based Key Derivation)

```
Standard: NIST SP 800-132
Iterations: 100,000+
Salt: Random, 16+ bytes
Output: Variable length

Use:
- Password → encryption key
- TLS_EXPORT functions

Weakness:
- Fast (not ideal for passwords)
- GPU-attackable
```

### bcrypt

```
Cost factor: 10-12
Output: 192 bits (hashed password)
Salt: Automatic

Use:
- Password hashing (recommended)
- Intentionally slow
- Resistant to GPU attack

Advantages:
- Adaptive (cost increases over time)
- Built-in salt
- Simple to use
```

### scrypt

```
Parameters: N, r, p
Output: Variable length
Salt: Required

Use:
- Password-based encryption
- Key derivation from passwords
- More resistant than PBKDF2

Advantages:
- Memory-hard (resistant to GPU)
- CPU-hard
- Configurable difficulty
```

### Argon2

```
Variants:
- Argon2i: Memory-hard
- Argon2d: Data-dependent
- Argon2id: Hybrid (recommended)

Parameters:
- Time cost
- Memory cost
- Parallelism

Status:
- Modern standard
- Password hashing
- Key derivation
- Recommended (2024+)
```

## SSL/TLS Cipher Suites

### TLS 1.3 (Modern Standard)

#### Recommended Cipher Suites
```
Primary:
TLS_AES_256_GCM_SHA384
- AES-256-GCM encryption
- SHA-384 HMAC
- ECDHE key exchange with PFS

Fallback:
TLS_CHACHA20_POLY1305_SHA256
- ChaCha20-Poly1305 encryption
- SHA-256 HMAC
- Alternative for non-AES systems
```

#### Key Exchange (TLS 1.3)
```
Mandatory PFS with:
- X25519 (ECDHE primary)
- secp256r1 (P-256)
- secp384r1 (P-384)

All handshakes use ephemeral keys
No static RSA/ECDSA key exchange
```

### TLS 1.2 (Legacy)

#### Acceptable Suites
```
ECDHE-RSA-AES256-GCM-SHA384:
- ECDHE: Key exchange
- RSA: Authentication
- AES-256-GCM: Encryption
- SHA-384: HMAC

ECDHE-RSA-AES128-GCM-SHA256:
- Similar but AES-128
- Slightly weaker
- Acceptable minimum

Avoid completely:
- Anything with MD5
- Anything with DES
- Anonymous suites
- Export suites
- Non-GCM (like -AES256-SHA)
```

## Cryptographic Standards Evolution

### Timeline

```
2025-2030:
- Retire RSA-1024 (already done)
- Retire SHA-1 (already done)
- Retire TLS 1.0/1.1 (already done)
- Use AES-256 or ChaCha20-Poly1305
- Use ECDSA P-256+
- Use TLS 1.3

2030-2040:
- Retire RSA-2048 (phase out)
- Use RSA-3072+ or ECDSA-384+
- AES-256 becomes minimum (not negotiable)
- Post-quantum crypto preparation

2040+:
- Full post-quantum migration
- RSA deprecated
- Lattice-based cryptography
- Quantum-safe algorithms
```

## Regulatory Compliance

### NIST Recommendations (SP 800-175B)
```
Symmetric Encryption:
- AES-128: Through 2030
- AES-192/256: Beyond 2030

Asymmetric Encryption:
- RSA-2048: Through 2030
- RSA-3072+: Beyond 2030
- ECDSA: Encouraged

Hashing:
- SHA-256+: All uses
- No SHA-1

Key Exchange:
- DHE 2048+: Acceptable
- ECDHE: Recommended
- Static RSA: Acceptable (deprecated TLS 1.3)
```

### PCI-DSS Requirements
```
TLS Version: 1.2 minimum (1.3 preferred)
Cipher Strength: 128-bit minimum
Key Exchange: Forward secrecy preferred
No weak/deprecated algorithms
Annual review required
```

### HIPAA Requirements
```
Encryption:
- AES-128 minimum (256 preferred)
- 3DES acceptable temporarily
- No MD5

Transport:
- TLS 1.2+
- Certificate validation
- No cleartext transmission
```
