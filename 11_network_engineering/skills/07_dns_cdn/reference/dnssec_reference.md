# DNSSEC Reference Guide

## DNSSEC Overview

### Purpose
Cryptographic authentication of DNS responses to prevent:
- DNS spoofing attacks
- DNS hijacking/redirection
- Man-in-the-middle (MITM) attacks
- Cache poisoning

### Trust Chain
```
ICANN Root DNSSEC Keys
         |
       Root Zone
         |
    TLD Zone (e.g., .com)
         |
  Authoritative Zone (example.com)
         |
  DNS Responses (RRsets)
```

## DNSSEC Key Hierarchy

### KSK (Key Signing Key)
- Signs DNSKEY records
- Held by authoritative server operator
- Submitted to registrar for DS record creation
- 2048-bit RSA or 256-bit ECDSA minimum

### ZSK (Zone Signing Key)
- Signs actual DNS records (A, MX, TXT, etc.)
- Rotated more frequently than KSK
- Shorter validity period (30-90 days typical)
- 2048-bit RSA or 256-bit ECDSA typical

### DS (Delegation Signer)
- Created from KSK
- Placed in parent zone by registrar
- Hash-based, so KSK rotation doesn't require DS update
- Multiple DS records for algorithm rollover

### DNSKEY Records
```
Zone.example.com.    3600    IN    DNSKEY    257    3    8    AwEAAZ...    (KSK)
Zone.example.com.    3600    IN    DNSKEY    256    3    8    AwEAAa...    (ZSK)

Fields:
- 257/256: Flags (257=KSK, 256=ZSK)
- 3: Protocol (always 3)
- 8: Algorithm (RSASHA256)
- AwEAA...: Public key data (base64)
```

## Signing Algorithms

| Algorithm | ID | Security | Performance | Notes |
|-----------|----|-----------|-----------| |
| RSAMD5    | 1  | Weak      | Good      | Deprecated |
| RSASHA1   | 5  | Weak      | Good      | Deprecated |
| RSASHA256 | 8  | Strong    | Good      | Standard |
| RSASHA512 | 10 | Very Strong | Slower  | High security |
| ECDSAP256 | 13 | Strong    | Best      | NIST P-256 |
| ECDSAP384 | 14 | Very Strong | Best   | NIST P-384 |
| ED25519   | 15 | Strong    | Excellent | Modern, smaller |

## DNSSEC Records

### RRSIG (Resource Record Signature)
```
example.com.    3600    IN    RRSIG    A    8    2    3600    20241220000000    20241120000000    12345    example.com.    signature_data...

Fields:
- Type Covered: A (record type being signed)
- Algorithm: 8 (RSASHA256)
- Labels: 2 (example.com = 2 labels)
- Original TTL: 3600 (TTL of records)
- Inception: When signature becomes valid
- Expiration: When signature expires
- Key Tag: Identifies DNSKEY used
- Signer's Name: Authority signing records
- Signature: Cryptographic signature (base64)
```

### NSEC (Next Secure)
```
example.com.    3600    IN    NSEC    www.example.com.    A    MX    RRSIG    NSEC

Proves:
- example.com doesn't have other records
- Next record is www.example.com
- Enables negative caching (NXDOMAIN responses)

Downside:
- Leaks entire zone (enumerate via NSEC walking)
```

### NSEC3 (Next Secure v3)
```
@    3600    IN    NSEC3    1    0    0    -    (hashed_next_owner)    A    MX    RRSIG    NSEC3

Improvements over NSEC:
- Hashes domain names (privacy)
- Prevents zone enumeration
- Supports opt-out for insecure delegations
```

## DNSSEC Validation

### Validation Process
```
1. Query for example.com A record
2. Response includes RRSIG record
3. Recursive resolver:
   a. Fetches DNSKEY from example.com
   b. Verifies RRSIG using DNSKEY
   c. Verifies DNSKEY using DS record from parent
   d. Verifies DS record using parent DNSKEY
   e. Chain continues to root
4. If all valid: SECURE (return to client)
5. If any invalid: BOGUS (drop response)
6. If unsigned: INSECURE (return if parent allows)
```

### Validation States
```
SECURE:
- Chain of trust complete and verified
- Response trustworthy

INSECURE:
- Domain not signed
- Parent allows insecure delegation (opt-out NSEC3)
- Acceptable if domain intentionally unsigned

BOGUS:
- Signature invalid
- Chain of trust broken
- Response dropped by resolver
- Client receives SERVFAIL

UNKNOWN:
- Resolver doesn't perform DNSSEC validation
- Accepts response regardless
```

## DNSSEC Signing Workflow

### Manual Signing (BIND example)
```
1. Create DNSSEC keys:
   dnssec-keygen -a ECDSAP256SHA256 -f KSK example.com
   dnssec-keygen -a ECDSAP256SHA256 example.com

2. Add keys to zone file:
   $INCLUDE Kexample.com.+013+12345.key
   $INCLUDE Kexample.com.+013+67890.key

3. Sign zone:
   dnssec-signzone -o example.com example.com.zone

4. Copy DS record from dsset-example.com:
   example.com. IN DS 12345 13 2 abc123def456...

5. Submit DS record to registrar

6. Load signed zone in BIND:
   zone "example.com" { file "example.com.zone.signed"; };
```

### Automated Signing with DNSSEC-Policy
```
zone "example.com" {
    file "example.com.zone";
    dnssec-policy default;
    auto-dnssec maintain;
    inline-signing yes;
};

DNSSEC-Policy handles:
- Key generation and rotation
- Zone signing
- Key rollover process
```

## Key Rotation

### KSK Rollover (Double Signature)
```
Phase 1 (Old KSK):
- Old DS in parent
- Old KSK signs DNSKEY RRset
- New KSK added but not in parent yet

Phase 2 (Both Active):
- TTL of old DS expires (DS TTL = 2 days typical)
- New DS added to parent
- Both KSKs sign DNSKEY for transition period

Phase 3 (New KSK):
- Old DS removed from parent
- Old KSK can be removed

Timeline: 2-4 weeks typical (depends on registrar TTL)
```

### ZSK Rollover (Rapid)
```
Phase 1:
- New ZSK added to DNSKEY RRset
- New ZSK signs RRsets
- Old ZSK still active

Phase 2:
- After TTL expiration
- Old ZSK removed

Timeline: 1-3 days (no registrar involvement)
```

## Algorithm Rollover

### Migrate from RSASHA256 to ECDSAP256
```
Step 1: Add new ECDSAP256 keys (KSK + ZSK)
- Keep RSASHA256 keys active

Step 2: Dual-sign zone (both algorithms)
- ZSK (RSASHA256) and ZSK (ECDSAP256) both sign RRsets
- RRSIG records for both algorithms

Step 3: Update KSK DS record
- Old DS (RSASHA256): Remove from parent
- New DS (ECDSAP256): Add to parent (wait for parent TTL)

Step 4: Retire old algorithm
- Remove RSASHA256 keys
- Keep only ECDSAP256 keys

Benefits:
- Migrates to faster algorithms
- Supports algorithm agility
```

## DNSSEC Monitoring

### Key Expiration
```
Alert when:
- KSK expires in < 30 days
- ZSK expires in < 7 days

Check with:
dig @ns1.example.com example.com DNSKEY +dnssec
dig @8.8.8.8 example.com A +dnssec (test validation)
```

### Signature Validation
```
dnsviz - Visualize DNSSEC chain:
dnsviz query example.com
dnsviz graph -T example.com

DNSSEC Checker online:
- https://dnssec-analyzer.verisignlabs.com/
- https://zonemaster.net/

Automated validation:
- Unbound with validation enabled
- dig +dnssec with validation
```

### Common DNSSEC Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| BOGUS response | Signature invalid | Verify zone signing |
| Signature expired | ZSK not re-signed | Implement auto-signing |
| Chain broken | DS record missing | Submit DS to registrar |
| Key mismatch | Wrong algorithm | Verify DNSKEY matches DS |

## DNSSEC Performance Impact

### Overhead
- Query size increase (RRSIG records)
- Additional lookups (DNSKEY, DS verification)
- Computation (signature verification)

### Mitigation
- Use ECDSAP256 (smaller signatures than RSA)
- Enable caching at recursive resolvers
- Implement DNS over TLS (DoT) for privacy
- Use ED25519 for excellent performance

### Benchmarks
```
Unsigned query:           ~50ms (no validation)
DNSSEC validated query:   ~60-80ms (with validation)
Cached DNSSEC query:      <10ms (cached result)

With ECDSAP256:
- 40% smaller signatures than RSASHA256
- Faster validation computation
- Better overall performance
```

## DNSSEC Best Practices

1. **Always use KSK**: Separate from ZSK for easier rollover
2. **Rotate keys**: ZSK every 30-90 days, KSK yearly
3. **Use modern algorithms**: ECDSAP256SHA256 or ED25519
4. **Automate signing**: Use dnssec-policy in BIND 9.16+
5. **Monitor expiration**: Alert well before expiry
6. **Test validation**: Verify resolvers validate correctly
7. **Document process**: Key rotation procedures, key storage
8. **Backup keys**: Secure backup of private keys
9. **Chain validation**: Test end-to-end with dig +dnssec
10. **Update registrar**: Ensure DS records propagated
