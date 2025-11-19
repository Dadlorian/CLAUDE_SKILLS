# SSL/TLS Offloading Guide

## What is SSL Offloading?

**Definition**: Moving SSL/TLS encryption processing from backend servers to the load balancer.

**Traffic Flow**:
```
Client                Load Balancer          Backend Server
(HTTPS)    ←-----→    (decrypt)    ←-----→    (HTTP)

Client:
  - Sends encrypted HTTPS request
  - Completes TLS handshake with LB

Load Balancer:
  - Decrypts request from client
  - Encrypts response for client
  - Sends decrypted request to backend

Backend:
  - Receives unencrypted HTTP request
  - Doesn't need SSL certificate or processing
  - Simple HTTP response sent to LB
```

## Benefits of SSL Offloading

### CPU Resource Savings
```
Scenario: 1000 TLS handshakes/second

Backend Server Handling SSL:
  - 1000 TPS × 30ms/handshake = 30 seconds of CPU time
  - Server: 4-core, each core might 30% busy just on SSL
  - Impact: Less capacity for application logic

Load Balancer Handling SSL:
  - SSL acceleration (hardware + tuned)
  - Specialized SSL processing
  - Frees backend CPU completely
  - Result: 30-50% less backend CPU needed
```

### Performance Improvement
```
Baseline: Without SSL offloading
  - 10,000 requests/second
  - 500 ms average response time

With SSL Offloading:
  - 15,000 requests/second (50% improvement)
  - 350 ms average response time
  - Backend CPUs freed for application
```

### Simplified Backend Configuration
```
Without SSL Offloading:
  - Each backend needs SSL certificate
  - Each backend runs SSL daemon (nginx, apache)
  - Certificate renewal on each server
  - TLS version management everywhere

With SSL Offloading:
  - One certificate on LB
  - Backend is simple HTTP only
  - Certificate management centralized
  - TLS version controlled at LB
```

### Certificate Management Consolidation
```
Without Offloading (3 backends):
  Backend 1: cert.pem, cert.key
  Backend 2: cert.pem, cert.key
  Backend 3: cert.pem, cert.key
  Total: 6 files to manage, 3 renewals needed

With Offloading (centralized):
  Load Balancer: cert.pem, cert.key
  Total: 2 files to manage, 1 renewal needed
```

## SSL Offloading Models

### Model 1: SSL Termination (Complete Offloading)
**Recommended For**: Most use cases, trusted internal network

**Configuration**:
```
Client: HTTPS 443 ←→ Load Balancer (TLS handling)
Load Balancer: HTTP 80 ←→ Backend (no TLS)
```

**Advantages**:
- Maximum performance (no backend SSL overhead)
- Simplest backend setup
- Centralized certificate management
- Easy TLS version upgrade

**Disadvantages**:
- End-to-end encryption lost internally
- Requires internal network security
- Backend can't verify client identity via TLS

**Security Consideration**:
```
Assumption: Internal network is secure
- Trusted network between LB and backend
- Only your servers on this network
- No data exposure on internal link

If this assumption is false:
  Use Model 2 (SSL Bridging) instead
```

### Model 2: SSL Bridging (End-to-End Encryption)
**Recommended For**: Multi-tier architecture, compliance requirement

**Configuration**:
```
Client: HTTPS 443 ←→ Load Balancer (decrypt) ←→ Backend: HTTPS 443 (encrypt)
```

**Process**:
```
1. Client connects to LB with TLS
2. LB decrypts client request
3. LB inspects content (if needed)
4. LB re-encrypts and sends to backend
5. Backend decrypts request
6. Backend processes and responds
7. Backend encrypts response to LB
8. LB decrypts and re-encrypts for client
9. Client decrypts response
```

**Advantages**:
- End-to-end encryption (more secure)
- Backend can verify TLS connection
- Suitable for compliance requirements
- Works with untrusted networks

**Disadvantages**:
- Higher LB CPU usage (encryption twice)
- Backend SSL overhead still needed
- More complex configuration
- Backend certificate management required

### Model 3: Client Certificate Authentication
**Configuration**:
```
Client: Has client certificate
  ↓
Load Balancer: Validates client certificate
  ↓
Can make routing decision based on cert
```

**Use Case**:
- API with mutual TLS (mTLS)
- Service-to-service authentication
- Regulatory compliance

## Certificate Management

### Installing Certificates

**F5 BIG-IP**:
```bash
# Import certificate
tmsh create sys file ssl-cert example_com_crt from-file /root/example.com.crt

# Import key
tmsh create sys file ssl-key example_com_key from-file /root/example.com.key

# Create SSL profile
tmsh create ltm profile client-ssl example_com_ssl \
  cert example_com_crt \
  key example_com_key
```

**NGINX**:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
}
```

**HAProxy**:
```
global
    ssl-default-bind-ciphers HIGH:!aNULL:!MD5
    tune ssl default-dh-param 2048

frontend https_in
    bind *:443 ssl crt /etc/ssl/certs/example.com.pem
    default_backend web_backend
```

### Certificate Renewal

**Automated Renewal (Let's Encrypt + Certbot)**:
```bash
# Initial certificate
certbot certonly --standalone -d example.com

# Renewal (typically automated)
certbot renew

# Deploy to load balancer
./deploy_cert_to_lb.sh /etc/letsencrypt/live/example.com/
```

**Manual Renewal Process**:
```
1. Request new certificate from CA
2. Provide DNS validation or other proof
3. Receive new certificate + key
4. Test certificate locally
5. Upload to load balancer
6. Update configuration to reference new cert
7. Test HTTPS access
8. Verify certificate details
9. Keep old cert as backup
10. Schedule renewal before expiry
```

**Automated Deployment Script**:
```bash
#!/bin/bash
# Deploy SSL certificate to F5 BIG-IP

CERT_FILE="/etc/letsencrypt/live/example.com/fullchain.pem"
KEY_FILE="/etc/letsencrypt/live/example.com/privkey.pem"
F5_HOST="203.0.113.1"
F5_USER="admin"
F5_PASS="password"

# SCP files to F5
scp -u $F5_USER@$F5_HOST "$CERT_FILE" /root/example_com.crt
scp -u $F5_USER@$F5_HOST "$KEY_FILE" /root/example_com.key

# SSH and import on F5
ssh $F5_USER@$F5_HOST "tmsh \
  create sys file ssl-cert example_com_crt from-file /root/example_com.crt; \
  create sys file ssl-key example_com_key from-file /root/example_com.key"

echo "Certificate deployed successfully"
```

### Multi-Certificate Setup (SNI)

**Purpose**: Host multiple SSL certificates on same IP:port

**Configuration** (NGINX):
```nginx
server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
}

server {
    listen 443 ssl;
    server_name api.example.com;
    ssl_certificate /etc/ssl/certs/api.example.com.crt;
    ssl_certificate_key /etc/ssl/private/api.example.com.key;
}

server {
    listen 443 ssl;
    server_name admin.example.com;
    ssl_certificate /etc/ssl/certs/admin.example.com.crt;
    ssl_certificate_key /etc/ssl/private/admin.example.com.key;
}
```

**How SNI Works**:
```
1. Client sends ClientHello with server_name: example.com
2. Load balancer reads SNI hostname
3. Load balancer selects appropriate certificate
4. TLS handshake completes with correct cert
5. Client verifies certificate matches hostname
```

## TLS Configuration

### TLS Version Control

**Recommended Configuration**:
```
Minimum: TLS 1.2
Preferred: TLS 1.3
Disabled: TLS 1.1, TLS 1.0, SSL 3.0
```

**NGINX Configuration**:
```nginx
server {
    listen 443 ssl;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    # Disable older versions
    # ssl_protocols TLSv1 TLSv1.1;  # Never enable these
}
```

**HAProxy Configuration**:
```
frontend https_in
    bind *:443 ssl crt /etc/ssl/certs/example.com.pem \
        ssl-min-ver TLSv1.2 ssl-max-ver TLSv1.3
```

### Cipher Suite Selection

**Strong Cipher Suites**:
```
TLS 1.3:
  - TLS_AES_256_GCM_SHA384
  - TLS_AES_128_GCM_SHA256
  - TLS_CHACHA20_POLY1305_SHA256

TLS 1.2:
  - ECDHE-RSA-AES256-GCM-SHA384
  - ECDHE-RSA-AES128-GCM-SHA256
  - ECDHE-ECDSA-AES256-GCM-SHA384
```

**Weak Ciphers to Avoid**:
```
- DES, 3DES (weak encryption)
- MD5 (weak hash)
- RC4 (broken stream cipher)
- NULL ciphers (no encryption)
- EXPORT ciphers (intentionally weak)
- Anonymous (ANON) ciphers (no authentication)
```

**NGINX Cipher Configuration**:
```nginx
server {
    listen 443 ssl;

    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

    ssl_prefer_server_ciphers on;
}
```

## Performance Optimization

### Hardware Acceleration

**Available Acceleration Options**:
- Intel AES-NI (Common in modern CPUs)
- ARM Neon (Mobile/ARM processors)
- Cavium (Dedicated crypto accelerators)
- FPGAs (Specialized hardware)

**Enabling on Linux**:
```bash
# Check CPU support
grep aes /proc/cpuinfo

# Enable in OpenSSL
openssl engine aesni -t

# Verify acceleration
# Monitor CPU usage during SSL operations
```

### Session Resumption

**Session ID Caching**:
```
Connection 1:
  Client ↔ LB: Full TLS handshake (100ms)
  Session ID generated: sess_abc123
  Server caches session

Connection 2:
  Client sends session ID: sess_abc123
  Server validates cache
  Abbreviated handshake (5ms)
  Significant latency improvement
```

**Session Tickets** (No server cache needed):
```
Connection 1:
  Client ↔ LB: Full handshake
  LB sends encrypted session ticket
  Client stores ticket

Connection 2:
  Client sends encrypted ticket
  LB decrypts ticket
  Abbreviated handshake
  Works across multiple LBs (with shared key)
```

### Keep-Alive Reuse

**Configuration**:
```nginx
keepalive_timeout 60;       # Keep connection open 60 seconds
keepalive_requests 100;     # Reuse up to 100 requests

# Result: Subsequent requests on same connection avoid TLS handshake
```

## Monitoring SSL Offloading

### Metrics to Track
```
1. TLS Handshakes/Second
   - Baseline: 100-500 per second (typical)
   - Alert if: > 1000 per second (unusual)

2. SSL Connection Time
   - Baseline: 20-50ms (typical)
   - Alert if: > 100ms

3. Session Reuse Rate
   - Goal: > 70% (reusing sessions)
   - Alert if: < 50%

4. Certificate Expiry
   - Alert: 30 days before expiry
   - Critical: 7 days before expiry
```

### Certificate Verification

**Check Certificate Validity**:
```bash
openssl x509 -in /etc/ssl/certs/example.com.crt -text -noout

# Key information to verify:
# - Subject CN matches domain
# - Alternative Names (SANs) cover all domains
# - Validity dates (not expired)
# - Issuer is trusted CA
```

**Test HTTPS Connection**:
```bash
curl -v https://example.com

# Or with OpenSSL
openssl s_client -connect example.com:443 -tls1_2
```

## SSL Offloading Checklist

- [ ] SSL certificate installed on load balancer
- [ ] Certificate private key protected (mode 600)
- [ ] Certificate chain complete (CA certs included)
- [ ] TLS versions configured (1.2+ minimum)
- [ ] Weak ciphers disabled
- [ ] Strong cipher suites ordered correctly
- [ ] Session resumption enabled
- [ ] SNI enabled if using multiple certs
- [ ] Hardware acceleration enabled (if available)
- [ ] Firewall allows port 443 inbound
- [ ] Backend receives HTTP (not HTTPS)
- [ ] Certificate expiry monitoring configured
- [ ] Certificate renewal process documented
- [ ] Failover certificate configured
- [ ] Performance tested and baselined

---

**Last Updated**: 2025-11-19
**Version**: 2.0
