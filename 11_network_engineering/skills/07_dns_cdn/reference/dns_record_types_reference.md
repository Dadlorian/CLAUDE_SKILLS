# DNS Record Types Reference

## Standard Record Types

### A (Address)
Maps hostname to IPv4 address
```
example.com.    3600    IN    A    192.0.2.1
www.example.com 3600    IN    A    192.0.2.10
```
- **TTL**: Typically 3600-86400 seconds
- **Usage**: Web servers, mail servers, any IPv4 endpoint
- **Lookup**: `dig example.com A`

### AAAA (IPv6 Address)
Maps hostname to IPv6 address
```
example.com.    3600    IN    AAAA    2001:db8::1
www.example.com 3600    IN    AAAA    2001:db8::10
```
- **TTL**: Typically 3600-86400 seconds
- **Usage**: IPv6-enabled services
- **Lookup**: `dig example.com AAAA`

### CNAME (Canonical Name)
Alias for another domain name
```
www.example.com.    3600    IN    CNAME    cdn.example.com.
mail.example.com.   3600    IN    CNAME    mailhost.example.com.
```
- **Constraints**: Cannot coexist with other records at apex
- **Chain Depth**: Keep shallow (max 3-5 hops)
- **Usage**: CDN endpoints, service aliases

### MX (Mail Exchange)
Specifies mail server for domain
```
example.com.    3600    IN    MX    10    mail1.example.com.
example.com.    3600    IN    MX    20    mail2.example.com.
```
- **Priority**: Lower value = higher priority (10 before 20)
- **Multiple Records**: Use for redundancy and load balancing
- **SMTP**: Mail servers query MX records

### NS (Name Server)
Delegates zone to DNS servers
```
example.com.        3600    IN    NS    ns1.example.com.
example.com.        3600    IN    NS    ns2.example.com.
subdomain.example.  3600    IN    NS    ns1.subdomain.example.com.
```
- **Zone Apex**: Required for zone delegation
- **Glue Records**: A records at parent zone for NS servers
- **Minimum**: 2 NS records recommended

### SOA (Start of Authority)
Contains zone authority information
```
example.com.    3600    IN    SOA    ns1.example.com. admin.example.com. (
                                      2024111901    ; Serial
                                      3600          ; Refresh
                                      1800          ; Retry
                                      604800        ; Expire
                                      86400         ; Minimum TTL
                                      )
```
- **Serial**: Increment for zone updates
- **Refresh**: Secondary checks primary interval
- **Retry**: Time before secondary retries failed transfer
- **Expire**: TTL for zone data if primary unreachable
- **Minimum TTL**: Minimum TTL for all records

### TXT (Text)
Arbitrary text data (SPF, DKIM, DMARC, verification)
```
example.com.              3600    IN    TXT    "v=spf1 include:_spf.google.com ~all"
default._domainkey.example.com. IN TXT "v=DKIM1; k=rsa; p=MIGfMA0BC..."
_dmarc.example.com.       3600    IN    TXT    "v=DMARC1; p=reject; rua=mailto:..."
_acme-challenge.example.com. IN  TXT    "validation-token-here"
```
- **Max Length**: 255 characters per string (split with quotes)
- **Multiple Strings**: Concatenated automatically
- **Usage**: SPF, DKIM, DMARC, domain verification

### PTR (Pointer)
Reverse DNS lookup
```
1.2.0.192.in-addr.arpa.    3600    IN    PTR    mail.example.com.
0.0.0.0.0.0.0.0.0.0.0.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.2.ip6.arpa.
                           3600    IN    PTR    mail.example.com.
```
- **Reverse DNS**: Hostname from IP address
- **In-Addr Zone**: 192.0.2.1 → 1.2.0.192.in-addr.arpa
- **IPv6 Reverse**: Nibble format in ip6.arpa zone

### SRV (Service)
Specifies location of specific service
```
_sip._tcp.example.com.           3600    IN    SRV    10    60    5060    sipserver.example.com.
_ldap._tcp.dc._msdcs.example.com. 3600   IN    SRV    10    100   389     dc1.example.com.
_xmpp._tcp.example.com.          3600    IN    SRV    10    5     5222    jabber.example.com.
```
- **Format**: _service._protocol.name TTL SRV priority weight port target
- **Priority**: Lower value selected first
- **Weight**: Distribution among same priority
- **Usage**: SIP, LDAP, XMPP, Kerberos

## DNSSEC Records

### DNSKEY (DNSSEC Key)
Public key for zone signing
```
example.com.    3600    IN    DNSKEY    257    3    8    AwEAAZ4...    ; KSK
example.com.    3600    IN    DNSKEY    256    3    8    AwEAAa8...    ; ZSK
```
- **Flags**: 256 = ZSK, 257 = KSK
- **Protocol**: Always 3 (DNSSEC)
- **Algorithm**: 8 = RSASHA256, 13 = ECDSAP256SHA256, 15 = ED25519

### RRSIG (DNSSEC Signature)
Signature covering record set
```
example.com.    3600    IN    RRSIG    A    8    2    3600    20241220    20241120    12345    example.com.    ...signature...
```
- **Type Covered**: Record type being signed
- **Algorithm**: Must match DNSKEY algorithm
- **Inception/Expiration**: Signature validity window

### DS (Delegation Signer)
Delegation signer record in parent zone
```
example.com.    3600    IN    DS    12345    8    2    1a2b3c4d...
```
- **Key Tag**: References DNSKEY in child zone
- **Algorithm/Digest Type**: Must match child DNSKEY
- **Digest**: Hash of child DNSKEY record

### NSEC/NSEC3 (Next Secure)
Proves non-existence of records
```
example.com.    3600    IN    NSEC    www.example.com.    A NS SOA RRSIG NSEC
```
- **NSEC**: Simple negative caching (exposes zone data)
- **NSEC3**: Hashed next owner (privacy enhanced)

## Service Records

### CAA (Certification Authority Authorization)
Specifies which CAs can issue certificates
```
example.com.    3600    IN    CAA    0    issue    "letsencrypt.org"
example.com.    3600    IN    CAA    0    issuewild    "letsencrypt.org"
example.com.    3600    IN    CAA    0    iodef    "mailto:abuse@example.com"
```
- **Flags**: Usually 0 (non-critical)
- **Tags**: issue, issuewild, iodef
- **Usage**: ACME certificate automation

### TLSA (DANE)
TLSA for DANE (DNS-based Authentication of Named Entities)
```
_443._tcp.example.com.    3600    IN    TLSA    3    1    1    a1b2c3d4...
_25._tcp.example.com.     3600    IN    TLSA    3    1    1    x1y2z3w4...
```
- **Usage Selector**: 3 = DANE-EE (end-entity)
- **Selector**: 1 = SubjectPublicKeyInfo
- **Matching Type**: 1 = SHA256

### SSHFP (SSH Fingerprint)
SSH host key fingerprint
```
server.example.com.    3600    IN    SSHFP    1    1    d5a1...    ; RSA SHA1
server.example.com.    3600    IN    SSHFP    1    2    a2b3c4...  ; RSA SHA256
```
- **Algorithm**: 1 = RSA, 2 = DSA, 3 = ECDSA, 4 = ED25519
- **Fingerprint Type**: 1 = SHA1, 2 = SHA256

## Dynamic DNS Records

### DDNS (Dynamic Updates)
Update zone dynamically via nsupdate or API
```
zone example.com {
    allow-update { 192.0.2.0/24; };  // BIND configuration
};

# nsupdate commands
update add myhost.example.com 300 A 192.0.2.50
send
```

### ACME Challenge Records
Automated certificate management
```
_acme-challenge.example.com.    60    IN    TXT    "challenge-token-xyz"
_acme-challenge.www.example.com. 60   IN    TXT    "wildcard-challenge-abc"
```

## Special Records

### ANAME (Alias to Name - CNAME at Apex)
Some providers offer ANAME/ALIAS for apex CNAME
```
example.com.    3600    IN    ANAME    target.example.com.
```
- **Behavior**: Works like CNAME but at zone apex
- **Provider Support**: CloudFlare (CNAME flattening), AWS Route53, others

### @ALIAS (Cloudflare Alias)
Cloudflare-specific apex CNAME alternative
```
example.com    3600    IN    ALIAS    cdn.example.com
```

## TTL Guidelines

| Record Type | Typical TTL | Notes |
|------------|------------|-------|
| A/AAAA | 3600-86400 | Higher for stable IPs |
| CNAME | 3600 | Shorter for changing targets |
| MX | 3600 | Moderate, changes less frequently |
| NS | 86400+ | Long TTL, delegations stable |
| TXT (SPF/DKIM) | 3600 | Shorter for policy updates |
| SRV | 3600 | Service records change frequency |
| CAA | 3600 | Certificate policy changes |

## Best Practices

1. **Record Validation**: Use `dig` to verify record creation
2. **TTL Strategy**: Balance between flexibility and DNS load
3. **Redundancy**: Multiple A records, MX, NS servers
4. **Comments**: Use zone file comments for documentation
5. **Consistency**: Keep naming conventions consistent
6. **Monitoring**: Alert on MX/NS record changes
