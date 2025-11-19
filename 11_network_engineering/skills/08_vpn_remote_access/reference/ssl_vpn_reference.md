# SSL/TLS VPN Reference

## Overview

SSL/TLS VPN provides secure remote access through industry-standard encryption protocols. Unlike IPsec, SSL/TLS operates at Layer 4-6 and leverages standard web infrastructure.

## Protocol Architecture

### TLS Stack
- **TLS 1.3** (RFC 8446): Current standard, improved security
- **TLS 1.2** (RFC 5246): Widely supported, acceptable
- **TLS 1.0/1.1**: Deprecated, should not be used
- **SSL 3.0**: Deprecated, removed

### Certificate-Based Authentication
- **X.509 Certificates**: Standard format
- **Subject Alternative Names (SAN)**: Multi-domain support
- **Certificate Pinning**: Prevent MITM attacks
- **Certificate Transparency**: Verify certificate issuance

## VPN Architectures

### 1. Portal-Based (Clientless)

**Characteristics**
- Browser-based access
- No client installation required
- Limited functionality
- User authenticates via HTTPS portal
- Gateway proxies connections

**Use Cases**
- One-time access by partners
- Contractor/vendor access
- Low security requirements
- Administrative access to devices

**Advantages**
- Easy deployment
- No client management
- Works on any device with browser
- Minimal endpoint security impact

**Disadvantages**
- Limited application support
- Reduced functionality
- Potential performance issues
- Browser extensions may be needed

### 2. Client-Based

**Characteristics**
- Dedicated VPN client application
- Full tunnel capability
- Advanced security features
- Persistent connection option
- Client-side policies supported

**Use Cases**
- Full-time remote workers
- Secure application access
- Branch office connectivity
- High security requirements

**Advantages**
- Full network access
- Advanced security controls
- Better performance
- Client-side threat detection

**Disadvantages**
- Client installation and management
- Endpoint compliance required
- OS-specific implementation
- Update complexity

## Split Tunneling

### Concept
- Route some traffic through VPN tunnel
- Route other traffic directly to internet
- Reduces VPN server load
- Improves user experience

### Configuration
```
Split Tunnel Enabled:
  Specific Subnets: 10.0.0.0/8, 192.168.0.0/16
  Everything Else: Direct Internet Access

Full Tunnel:
  All traffic: 0.0.0.0/0 via VPN
```

### Security Considerations
- Reduces management scope (unencrypted traffic)
- May expose user identity if improperly configured
- Malware can bypass VPN easily
- Should correlate with security policy
- DNS split tunneling creates information leak

## Authentication Methods

### 1. Username/Password
- Simple user credentials
- LDAP/Active Directory integration
- No hardware requirements
- Vulnerable to brute force

### 2. Multi-Factor Authentication (MFA)
- **Token-based**: Hardware or software tokens
- **SMS**: One-time codes sent to phone
- **Biometric**: Fingerprint or facial recognition
- **Push notifications**: Approve via mobile app
- **Certificates**: Device certificates

### 3. Certificate-Based
- Client certificates from PKI
- Mutual authentication
- Automatic policy application
- Device identity verification

### 4. Federated Authentication
- **SAML**: Single sign-on integration
- **OAuth 2.0**: Third-party IdP integration
- **OIDC**: OpenID Connect support
- **RADIUS**: Legacy radius servers

## Tunneling Modes

### Full Tunnel Mode
- All IP traffic through VPN gateway
- Gateway becomes default route
- All DNS queries through VPN
- Complete traffic isolation
- Highest security, higher server load

### Split Tunnel Mode
- Selectively route traffic through VPN
- Local traffic remains direct
- VPN traffic to corporate resources only
- Reduced server load
- Lower security perimeter

### Port-Forward Mode
- Only specific ports tunneled
- SSH, RDP, HTTP/HTTPS forwarding
- Minimal network access
- Very restrictive security model

## Encryption Protocols

### Modern Cipher Suites (TLS 1.3)
- **AES-256-GCM**: Strong authenticated encryption
- **ChaCha20-Poly1305**: Alternative authenticated encryption
- **Elliptic Curve Diffie-Hellman Ephemeral**: Key exchange

### Legacy Cipher Suites (TLS 1.2)
- **AES-256-CBC-SHA256**: Standard
- **AES-128-CBC-SHA256**: Acceptable
- **ECDHE-RSA**: Elliptic curve exchange
- **Deprecated ciphers**: Should be disabled

## Performance Considerations

### Latency
- TLS handshake: 1-2 round trips
- Session resumption: Reduces handshake time
- Compression overhead: May reduce throughput
- Encryption: CPU-dependent

### Throughput
- Software encryption: 1-3 Gbps
- Hardware acceleration: 10+ Gbps
- Compression: Trade CPU for bandwidth
- Cipher selection impacts performance

### Optimization Techniques
1. **Session Caching**: Reuse sessions
2. **Pipelining**: Multiple requests without waiting
3. **Connection Multiplexing**: Share connections
4. **Compression**: Reduce data transfer
5. **Keep-alive**: Maintain persistent connections

## Device Posture Checking

### Antivirus Verification
- Check if AV installed and running
- Verify signatures current
- Real-time scanning enabled

### Firewall Verification
- Windows Firewall enabled
- Third-party firewall running
- Port-blocking rules active

### Operating System Patches
- Check Windows updates current
- Verify critical patches installed
- OS version whitelist

### Encryption Status
- Full Disk Encryption (BitLocker, FileVault)
- Data at rest encryption
- USB device encryption

### Policy Compliance
- Password complexity requirements
- Idle logout enforcement
- Screen lock enabled
- USB device restrictions

## VPN Client Security

### Endpoint Protection
- Antimalware integration
- Network threat detection
- Application layer filtering
- DNS security

### Data Protection
- Memory encryption
- Config file encryption
- Credential storage security
- Clear VPN credentials on disconnect

### Network Security
- Kill switch (block traffic if VPN drops)
- Local firewall integration
- IPv6 leak prevention
- DNS leak prevention

## Common Implementation Issues

### Connection Issues
- **Certificate validation failure**: Wrong certificate or OCSP failure
- **Protocol negotiation**: TLS version mismatch
- **Timeout**: Firewall blocking or server overload
- **Intermittent drops**: Network instability, server issues

### Performance Issues
- **Slow throughput**: Cipher overhead, server load
- **High latency**: Network path issues, server congestion
- **Packet loss**: Network congestion, MTU issues
- **Dropped sessions**: Timeout settings too aggressive

### Security Issues
- **Man-in-the-middle**: Certificate validation bypass
- **Credential theft**: Insecure storage or logging
- **Data leak**: Split tunnel misconfiguration
- **Unauthorized access**: Weak authentication

## Vendor-Specific Implementations

### Cisco AnyConnect
- **Secure Mobility Architecture**: ASA/ISE/FTD
- **Anyconnect Components**: Core, POSTURE, UMBRELLA, ISE
- **Advanced Options**: Always-on, pre-connection, post-connection
- **Integration**: ISE NAC, Umbrella DNS security

### Palo Alto GlobalProtect
- **Portal Architecture**: User authentication and download
- **Gateway Architecture**: Traffic encryption/decryption
- **App-ID Integration**: Application-aware policies
- **Threat Prevention**: Integrated malware/exploit blocking

### Fortinet FortiClient
- **FortiGate Integration**: Firewall policy enforcement
- **Threat Detection**: Antimalware, IPS integration
- **Asset Risk Assessment**: Endpoint compliance scoring
- **Zero Trust**: Device posture verification

## Monitoring and Logging

### Session Monitoring
- Active user connections
- Connected user device information
- Session duration and bandwidth
- Connection timestamps and source IPs

### Security Logging
- Authentication attempts (success/failure)
- Certificate validation events
- Policy violations
- Threat detection events

### Performance Metrics
- Tunnel throughput
- Encryption performance
- Connection latency
- Failed session counts

## Best Practices

1. **Use TLS 1.3**: Enforce modern TLS versions
2. **Strong Certificates**: 2048-bit RSA minimum, prefer ECDSA
3. **MFA Required**: Strong authentication essential
4. **Device Posture**: Verify endpoint security
5. **Logging**: Audit all connections
6. **Updates**: Regular client and gateway updates
7. **Split Tunnel Carefully**: Understand security implications
8. **Monitor Usage**: Detect anomalous patterns
