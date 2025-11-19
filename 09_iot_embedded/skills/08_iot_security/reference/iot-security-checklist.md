# IoT Security Checklist & Best Practices

## Secure Boot

- [ ] Implement cryptographic signature verification (RSA-2048 or ECDSA P-256)
- [ ] Enable rollback protection with monotonic counters
- [ ] Store public keys in secure storage (OTP/fuses)
- [ ] Verify firmware integrity before execution
- [ ] Implement encrypted firmware support
- [ ] Disable debug interfaces in production
- [ ] Use secure boot chain (bootloader → application)
- [ ] Implement recovery mechanism for failed updates

## Cryptography

- [ ] Use hardware crypto accelerators when available
- [ ] Never implement custom cryptography
- [ ] Use proven libraries (mbedTLS, WolfSSL, TinyCrypt)
- [ ] Key lengths: AES-128/256, RSA-2048+, ECDSA P-256+
- [ ] Use authenticated encryption (GCM, CCM)
- [ ] Implement proper key management
- [ ] Rotate keys periodically
- [ ] Zeroize sensitive data from memory after use

## Secure Communication

- [ ] Use TLS 1.2+ for network communication
- [ ] Verify server certificates
- [ ] Implement mutual authentication (client certs)
- [ ] Use certificate pinning for critical connections
- [ ] Disable weak cipher suites
- [ ] Implement perfect forward secrecy
- [ ] Use secure protocols (HTTPS, MQTTS, CoAPS)
- [ ] Validate all received data

## Key Storage

- [ ] Never hardcode keys in firmware
- [ ] Use hardware security modules (HSM)
- [ ] Use secure elements (ATECC608, SE050)
- [ ] Implement per-device unique keys
- [ ] Store keys in encrypted flash
- [ ] Use key derivation functions (KDF)
- [ ] Implement key provisioning process
- [ ] Protect keys with access control

## Authentication & Authorization

- [ ] Implement strong device authentication
- [ ] Use token-based authentication (JWT)
- [ ] Implement role-based access control
- [ ] Use OAuth 2.0 for cloud services
- [ ] Implement account lockout after failed attempts
- [ ] Use secure password storage (bcrypt, scrypt)
- [ ] Implement session management
- [ ] Use HMAC for message authentication

## Firmware Updates

- [ ] Sign all firmware updates
- [ ] Encrypt firmware images
- [ ] Implement secure OTA update mechanism
- [ ] Verify update before applying
- [ ] Implement atomic updates (A/B partitions)
- [ ] Keep backup firmware partition
- [ ] Implement update rollback capability
- [ ] Log all update attempts

## Physical Security

- [ ] Disable/lock debug ports (JTAG/SWD)
- [ ] Implement tamper detection
- [ ] Use secure chip packaging (anti-tamper)
- [ ] Implement physical intrusion detection
- [ ] Protect against side-channel attacks
- [ ] Use constant-time algorithms
- [ ] Implement fault injection countermeasures
- [ ] Clear memory on tamper detection

## Input Validation

- [ ] Validate all external inputs
- [ ] Implement bounds checking
- [ ] Sanitize user input
- [ ] Use safe string functions (strncpy, snprintf)
- [ ] Validate message lengths
- [ ] Check for buffer overflows
- [ ] Implement format string protection
- [ ] Use input whitelisting

## Network Security

- [ ] Implement firewall rules
- [ ] Use network segmentation
- [ ] Disable unnecessary services
- [ ] Change default credentials
- [ ] Implement rate limiting
- [ ] Use strong Wi-Fi security (WPA3)
- [ ] Implement MAC address filtering
- [ ] Monitor for anomalous traffic

## Logging & Monitoring

- [ ] Log security events
- [ ] Implement intrusion detection
- [ ] Monitor failed authentication attempts
- [ ] Log firmware updates
- [ ] Implement anomaly detection
- [ ] Secure log storage
- [ ] Implement log rotation
- [ ] Use secure time synchronization (NTP)

## Privacy

- [ ] Minimize data collection
- [ ] Encrypt sensitive data at rest
- [ ] Implement data anonymization
- [ ] Follow GDPR/privacy regulations
- [ ] Implement user consent mechanisms
- [ ] Provide data deletion capability
- [ ] Use secure random number generation
- [ ] Protect personally identifiable information (PII)

## Testing

- [ ] Perform security code review
- [ ] Use static analysis tools (Coverity, SonarQube)
- [ ] Perform dynamic analysis (fuzzing)
- [ ] Conduct penetration testing
- [ ] Test for common vulnerabilities (OWASP)
- [ ] Perform cryptographic validation
- [ ] Test secure boot mechanism
- [ ] Verify secure communication

## Compliance

- [ ] Follow OWASP IoT Top 10
- [ ] Comply with IEC 62443 (industrial)
- [ ] Follow ETSI EN 303 645 (consumer IoT)
- [ ] Implement NIST Cybersecurity Framework
- [ ] Follow industry-specific standards
- [ ] Document security architecture
- [ ] Conduct security audits
- [ ] Maintain vulnerability management program

## Common Cryptographic Algorithms

### Symmetric Encryption
```
AES-128/256: Standard choice
ChaCha20: Good for software-only implementations
AES-GCM: Authenticated encryption (recommended)
AES-CCM: Alternative authenticated encryption
```

### Asymmetric Encryption
```
RSA-2048/3072: Widely supported
ECC P-256/P-384: Smaller keys, faster
Ed25519: Fast signature verification
```

### Hash Functions
```
SHA-256: Standard choice
SHA-3: Alternative
BLAKE2: Fast, secure
```

### Key Exchange
```
ECDH: Elliptic Curve Diffie-Hellman
X25519: Modern, fast
```

## Example: TLS Configuration

```c
/* mbedTLS TLS 1.2 configuration */
mbedtls_ssl_config conf;
mbedtls_ssl_config_init(&conf);

/* Only TLS 1.2+ */
mbedtls_ssl_conf_min_version(&conf, MBEDTLS_SSL_MAJOR_VERSION_3,
                              MBEDTLS_SSL_MINOR_VERSION_3);

/* Strong cipher suites only */
static const int ciphersuites[] = {
    MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
    MBEDTLS_TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
    MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
    0
};
mbedtls_ssl_conf_ciphersuites(&conf, ciphersuites);

/* Require certificate verification */
mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
```

## Example: Secure Random Number Generation

```c
/* Use hardware RNG when available */
uint32_t get_random_number(void) {
#ifdef HAS_HARDWARE_RNG
    extern uint32_t hardware_rng_read(void);
    return hardware_rng_read();
#else
    /* Use entropy pool + DRBG */
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    uint32_t random;

    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);

    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func,
                          &entropy, NULL, 0);

    mbedtls_ctr_drbg_random(&ctr_drbg, (uint8_t*)&random,
                             sizeof(random));

    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);

    return random;
#endif
}
```

## Example: Secure Key Storage

```c
/* Store key in encrypted flash */
typedef struct {
    uint8_t key[32];
    uint8_t iv[16];
    uint8_t tag[16];  /* GCM authentication tag */
} encrypted_key_storage_t;

bool store_key_encrypted(const uint8_t *key,
                         const uint8_t *master_key) {
    encrypted_key_storage_t storage;

    /* Generate random IV */
    get_random_bytes(storage.iv, 16);

    /* Encrypt key with AES-256-GCM */
    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES,
                       master_key, 256);

    mbedtls_gcm_crypt_and_tag(&gcm, MBEDTLS_GCM_ENCRYPT,
                               32, storage.iv, 16,
                               NULL, 0, key, storage.key,
                               16, storage.tag);

    mbedtls_gcm_free(&gcm);

    /* Write to flash */
    return flash_write(KEY_STORAGE_ADDR, &storage,
                       sizeof(storage));
}
```

## Security Standards & Frameworks

### OWASP IoT Top 10
1. Weak, Guessable, or Hardcoded Passwords
2. Insecure Network Services
3. Insecure Ecosystem Interfaces
4. Lack of Secure Update Mechanism
5. Use of Insecure or Outdated Components
6. Insufficient Privacy Protection
7. Insecure Data Transfer and Storage
8. Lack of Device Management
9. Insecure Default Settings
10. Lack of Physical Hardening

### IEC 62443 Security Levels
- SL 1: Protection against casual violation
- SL 2: Protection against intentional violation
- SL 3: Protection against sophisticated means
- SL 4: Protection against advanced persistent threats

### NIST Cybersecurity Framework
- Identify: Asset management, risk assessment
- Protect: Access control, data security
- Detect: Anomaly detection, monitoring
- Respond: Incident response, analysis
- Recover: Recovery planning, improvements

## Tools

### Static Analysis
- Coverity Scan
- SonarQube
- Clang Static Analyzer
- PC-lint

### Dynamic Analysis
- Valgrind
- AddressSanitizer
- AFL (American Fuzzy Lop)
- Radamsa

### Penetration Testing
- Metasploit
- Burp Suite
- OWASP ZAP
- Nmap

### Hardware Analysis
- JTAGulator
- Bus Pirate
- Logic Analyzer
- Oscilloscope
