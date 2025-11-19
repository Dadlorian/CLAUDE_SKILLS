# SSL/TLS Offloading Reference

## Overview
SSL/TLS offloading (SSL termination) moves the cryptographic processing burden from backend servers to the load balancer, improving performance and simplifying certificate management.

## SSL/TLS Offloading Concepts

### What is SSL Offloading?
**Definition**: The load balancer handles SSL/TLS encryption/decryption instead of backend servers.

**Traffic Flow**:
```
HTTPS Request from Client
        ↓
    Load Balancer (SSL/TLS Processing)
        ↓ (Decrypted to HTTP)
    Backend Servers (Plain HTTP)
        ↓ (Response)
    Load Balancer (Re-encrypt to HTTPS)
        ↓
Client (Receives HTTPS)
```

**Benefits**:
- Reduces backend CPU usage by 30-50%
- Frees backend resources for application logic
- Centralized certificate management
- Easier to upgrade TLS version
- Better performance optimization
- Simplified backend configuration

**Drawbacks**:
- End-to-end encryption lost internally
- Requires backend trust/security
- Load balancer must support all TLS features
- Certificate management at load balancer

## SSL/TLS Offloading Models

### Model 1: SSL Termination (Complete Offloading)
**Configuration**:
```
Client → HTTPS (TLS) → Load Balancer
Load Balancer → HTTP (plain) → Backend
```

**Characteristics**:
- Complete offloading at LB
- Backend receives HTTP traffic
- Highest performance benefit
- No encryption between LB and backend

**Use Cases**:
- Trusted internal networks
- Performance-critical applications
- Simple backend setup

**Configuration Example**:
```
Frontend: HTTPS, port 443
Backend Pool: HTTP, port 80
SSL Certificate: Installed on LB
```

### Model 2: SSL Bridging (Re-encryption)
**Configuration**:
```
Client → HTTPS (TLS) → Load Balancer → HTTPS (TLS) → Backend
```

**Characteristics**:
- LB decrypts from client
- LB re-encrypts to backend
- End-to-end encryption maintained
- Higher CPU usage on LB
- Backend must support SSL

**Use Cases**:
- Security-critical applications
- Compliance requirements
- Multi-hop architectures

**Configuration Example**:
```
Frontend: HTTPS, port 443
Backend Pool: HTTPS, port 443
Client Certificate: For backend auth
SSL Certificate: One for client, one for backend
```

### Model 3: Hybrid Approach (Selective Offloading)
**Configuration**:
```
Client A → HTTPS → Load Balancer → HTTP → Backend A
Client B → HTTPS → Load Balancer → HTTPS → Backend B
```

**Characteristics**:
- Different policies per backend
- Flexibility in architecture
- Granular control
- More complex configuration

**Use Cases**:
- Mixed environment
- Selective end-to-end encryption
- Gradual migration

## Certificate Management

### Single Certificate Setup
**Configuration**:
```
Certificate: *.example.com
Backend: example.com, api.example.com, www.example.com
Load Balancer Port: 443
All traffic shares same certificate
```

**Advantages**:
- Simple setup
- Single renewal
- Cost-effective (wildcard certificate)

**Limitations**:
- Only covers subdomains
- Doesn't work across different base domains
- Renewal affects all services

### Multi-Certificate Setup (SNI)
**Definition**: Server Name Indication allows multiple certificates on single IP:port.

**How It Works**:
1. Client sends SNI extension with desired hostname in TLS ClientHello
2. Load balancer reads SNI hostname
3. Selects appropriate certificate
4. Completes TLS handshake

**Configuration Example**:
```
SNI-enabled: Yes
Certificates:
  - example.com → cert1.pem
  - api.example.com → cert2.pem
  - legacy.example.com → cert3.pem
Port 443: Shared
```

**Client Request**:
```
ClientHello:
  server_name: api.example.com
  ↓
Load Balancer selects cert2.pem
↓
TLS handshake continues
```

**Advantages**:
- Multiple domains on single IP
- Separate certificates per domain
- Efficient use of IPs
- Modern standard (TLS 1.0+)

**Disadvantages**:
- Older clients might not support SNI
- Certificate name must match SNI hostname
- More complex configuration

### Wildcard vs SAN Certificates

**Wildcard Certificate**:
```
Certificate: *.example.com
Covers: api.example.com, www.example.com, any.example.com
Not covered: example.com (if CN not also example.com)
                       deep.nested.example.com (only one level)
```

**SAN (Subject Alternative Name) Certificate**:
```
Primary: example.com
Alternatives: www.example.com, api.example.com, cdn.example.com, admin.example.com
Covers: Each explicitly listed domain
Very flexible, good for multi-domain setup
```

### Certificate Renewal

**Manual Renewal**:
```
1. Generate new certificate
2. Upload to load balancer
3. Select certificate in pool
4. Restart services (might vary)
5. Monitor for issues
```

**Automated Renewal** (with automation tools):
```
1. Certificate expiry monitoring
2. Automatic renewal request
3. Upload to load balancer
4. Configuration update
5. Validation and testing
```

## TLS Protocol Configuration

### TLS Version Support
**Recommended Configuration**:
```
Minimum: TLS 1.2
Preferred: TLS 1.3
Supported:
  - TLS 1.3 (preferred)
  - TLS 1.2 (required)
Disabled:
  - TLS 1.1
  - TLS 1.0
  - SSL 3.0
```

**Version Negotiation**:
```
Client: "I support TLS 1.0, 1.2, 1.3"
  ↓
Load Balancer: "Let's use TLS 1.3"
  ↓
Client: Accepts TLS 1.3
```

### Cipher Suite Configuration

**Strong Ciphers** (Recommended):
```
TLS 1.3:
- TLS_AES_256_GCM_SHA384
- TLS_CHACHA20_POLY1305_SHA256
- TLS_AES_128_GCM_SHA256

TLS 1.2:
- ECDHE-ECDSA-AES256-GCM-SHA384
- ECDHE-RSA-AES256-GCM-SHA384
- ECDHE-ECDSA-CHACHA20-POLY1305
- ECDHE-RSA-CHACHA20-POLY1305
- ECDHE-ECDSA-AES128-GCM-SHA256
- ECDHE-RSA-AES128-GCM-SHA256
```

**Weak Ciphers** (Avoid):
```
- DES (56-bit key)
- RC4 (stream cipher weaknesses)
- MD5 (broken hash)
- Export-grade ciphers
- NULL ciphers (no encryption)
- Anonymous ciphers (no authentication)
```

**Cipher Suite Order** (Preferred to Least):
```
1. ECDHE-RSA-AES256-GCM-SHA384    (PFS, strong)
2. ECDHE-RSA-AES128-GCM-SHA256    (PFS, adequate)
3. AES256-GCM-SHA384              (No PFS, strong)
4. AES128-GCM-SHA256              (No PFS, adequate)
```

## Performance Optimization

### Hardware Acceleration
**Crypto Acceleration Cards**:
- Niagara (Sun)
- AES-NI (Intel)
- Power8 (IBM)
- Cavium (crypto ASICs)

**Benefits**:
- 5-10x faster encryption/decryption
- Reduced CPU usage
- Better throughput

**Configuration Example**:
```
Hardware Acceleration: Enabled
Engines:
  - Intel AES-NI
  - OpenSSL AES-NI support
Monitor: CPU usage reduction
```

### Connection Reuse

**HTTP Keep-Alive**:
```
Client → [TLS Handshake] → LB
    ↓
  Send Request 1
    ↓
  Send Request 2  (reuse connection)
    ↓
  Send Request 3  (reuse connection)
```

**Benefits**:
- Reduces TLS handshake overhead
- Improves throughput
- Reduces latency

**Configuration**:
```
Keep-Alive: Enabled
Timeout: 60 seconds
Max Requests per Connection: 100
```

### Session Resumption

**Session ID Caching**:
```
Connection 1:
  - Full handshake
  - Session ID: sess_123
  - Cached on server

Connection 2:
  - Client sends session ID
  - Server validates cache
  - Abbreviated handshake (faster)
```

**TLS Session Tickets**:
```
Connection 1:
  - Full handshake
  - Server sends encrypted session ticket
  - Client stores ticket

Connection 2:
  - Client sends ticket
  - Server decrypts ticket
  - Abbreviated handshake
  - No server-side cache needed
```

## Backend Communication Security

### Mutual TLS (mTLS)
**Definition**: Both client and server authenticate each other.

**Configuration**:
```
Load Balancer (Client Certificate):
  Certificate: lb-client-cert.pem
  Private Key: lb-client-key.pem
  CA Certificate: backend-ca.pem

Backend (Server Certificate):
  Certificate: backend-server-cert.pem
  Validated against CA

Handshake:
1. Backend sends server certificate
2. LB validates against CA cert
3. LB sends client certificate
4. Backend validates client cert
5. Both authenticated
```

**Use Cases**:
- Secure microservices communication
- Compliance requirements
- Internal service-to-service auth

### Backend Certificate Validation

**Full Validation**:
```
Check 1: Certificate is valid (not expired)
Check 2: Signature is valid
Check 3: Hostname matches certificate CN/SAN
Check 4: Certificate chain valid (CA trusted)
Check 5: No certificate revocation (CRL/OCSP)
```

**Validation Options**:
```
Strict: All checks must pass
Permissive: Allow some checks to fail (for testing)
Disabled: Skip validation (not recommended)
```

## Troubleshooting SSL/TLS Issues

### Common Issues

#### Certificate Mismatch
**Symptom**: Browser warning about certificate name

**Diagnosis**:
```
Certificate CN: example.com
SNI hostname: www.example.com
↑ Mismatch!
```

**Solution**:
```
Option 1: Update certificate with SAN
Option 2: Use matching hostname in SNI
Option 3: Use wildcard certificate
```

#### Weak Cipher Selected
**Symptom**: SSL labs grade is low

**Diagnosis**:
```
Connected with: RC4-SHA (WEAK)
Available: AES256-GCM-SHA384 (STRONG)
```

**Solution**:
```
Remove weak ciphers from configuration
Reorder cipher suite
Test with `openssl s_client`
```

#### TLS Version Negotiation Failed
**Symptom**: Client can't connect to HTTPS

**Diagnosis**:
```
Client supports: TLS 1.0, 1.1
LB requires: TLS 1.2 minimum
↑ No common version!
```

**Solution**:
```
Option 1: Upgrade client
Option 2: Lower minimum TLS version (temporary)
Option 3: Legacy pool with TLS 1.1
```

## SSL/TLS Offloading Configuration Checklist

- [ ] Certificate installed on load balancer
- [ ] Certificate key permissions set correctly (600)
- [ ] Certificate chain complete (root + intermediate)
- [ ] SNI enabled if using multiple certificates
- [ ] TLS version minimum set to 1.2 or 1.3
- [ ] Weak ciphers disabled
- [ ] Hardware acceleration enabled
- [ ] Session resumption configured
- [ ] Backend communication method selected (HTTP/HTTPS)
- [ ] Health checks configured for backend protocol
- [ ] Certificate expiry monitoring in place
- [ ] Failover certificates configured
- [ ] Certificate renewal process documented
- [ ] Performance baseline established
- [ ] Security scanning performed (SSL Labs, nessus)

---

**Last Updated**: 2025-11-19
**Version**: 2.0
