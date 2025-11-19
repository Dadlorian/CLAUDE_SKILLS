# VPN Protocols Comparison

## Overview

Comprehensive comparison of modern and legacy VPN protocols with their characteristics, strengths, and appropriate use cases.

## Protocol Comparison Matrix

| Aspect | IPsec | SSL/TLS | WireGuard | PPTP | L2TP | OpenVPN |
|--------|-------|---------|-----------|------|------|---------|
| **OSI Layer** | 3 | 4-7 | 3 | 2-3 | 2-3 | 4 |
| **Encryption** | Strong | Strong | Modern | Weak | Medium | Strong |
| **Speed** | Medium | Medium | Fast | Very Fast | Medium | Slow |
| **Complexity** | High | Medium | Low | Low | Medium | Medium |
| **Mobile Support** | Medium | Good | Good | Poor | Medium | Good |
| **Use Case** | Site-to-site | Remote access | General | Legacy | Legacy | Cross-platform |
| **Firewall Friendly** | Poor | Good | Good | Good | Medium | Medium |
| **Learning Curve** | Steep | Moderate | Easy | Easy | Moderate | Moderate |
| **Production Ready** | Mature | Mature | Growing | Deprecated | Deprecated | Stable |

## IPsec VPN

### Characteristics
- **Layer**: Network layer (Layer 3)
- **Encryption**: Multiple options (AES, 3DES, ChaCha20)
- **Authentication**: IKE (Internet Key Exchange), v1 and v2
- **Standard**: RFC 4301, RFC 7539
- **Use Cases**: Site-to-site, enterprise VPN, DPD

### IKE Versions

#### IKEv1 (RFC 2409)
- **Legacy standard**: Superseded by IKEv2
- **Phases**: 2 (main mode, aggressive mode, quick mode)
- **Overhead**: High with 6 messages minimum
- **Vulnerabilities**: Prone to timing attacks, weak key derivation
- **Status**: Deprecated, use IKEv2 when possible

#### IKEv2 (RFC 7539, RFC 7748)
- **Modern standard**: Faster, more efficient
- **Overhead**: Fewer messages (4 minimum)
- **Security**: Better key derivation, DPD included
- **Mobility**: MOBIKE (Mobility and Multi-homing Protocol)
- **Status**: Recommended for new deployments
- **Performance**: 30-40% faster than IKEv1

### Encryption Algorithms

#### Symmetric Encryption
```
AES-128-GCM: Good balance, 128-bit key
AES-256-GCM: High security, 256-bit key (recommended)
AES-256-CBC: Older standard, slower than GCM
3DES: Legacy, do not use for new deployments
ChaCha20-Poly1305: Modern, fast on systems without AES acceleration
```

#### Key Exchange
```
ECDH (Elliptic Curve Diffie-Hellman): Recommended
 P-256: 256-bit elliptic curve
 P-384: 384-bit elliptic curve
 P-521: 521-bit elliptic curve
 Curve25519: Modern, 128-bit symmetric equivalent

DH (Diffie-Hellman): Older
 DH Group 14: 2048-bit, slow
 DH Group 15: 3072-bit, better
 DH Group 16: 4096-bit, slow for mobile
```

#### Authentication
```
HMAC-SHA256: Secure, widely supported
HMAC-SHA384: Higher security
HMAC-SHA512: Highest security
HMAC-MD5: Do not use, deprecated
```

### DPD (Dead Peer Detection)

```
! Detect non-responsive peers
crypto ikev2 dpd 10 3 on-demand

! Configuration options
- Interval (10s default): How often to send DPD messages
- Retry (3 default): How many retries before declaring dead
- Mode (on-demand): Check only when no traffic
```

### IPsec Transport vs Tunnel Mode

| Mode | Header Encrypted | Original IP | Use Case |
|------|------------------|-------------|----------|
| Transport | No | Yes | Host-to-host |
| Tunnel | Yes | No | Site-to-site |
| Tunnel | Yes | No | Remote client |

### Perfec Forward Secrecy (PFS)

- **Purpose**: Session key independent from long-term keys
- **Benefit**: Compromise of main key doesn't expose past sessions
- **Performance**: 5-10% overhead, highly recommended
- **Configuration**: Enable in quick mode (IKEv1) or CREATE_CHILD_SA (IKEv2)

## SSL/TLS VPN

### Characteristics
- **Layer**: Transport/Application layer (Layer 4-7)
- **Encryption**: AES (128, 256-bit), symmetric
- **Key Exchange**: RSA, ECDHE
- **Standard**: RFC 5246 (TLS 1.2), RFC 8446 (TLS 1.3)
- **Use Cases**: Remote access, clientless access, web-based portals

### TLS Versions

| Version | Status | Security | Notes |
|---------|--------|----------|-------|
| TLS 1.0 | Deprecated | Weak | Do not use |
| TLS 1.1 | Deprecated | Weak | Do not use |
| TLS 1.2 | Stable | Good | Acceptable minimum |
| TLS 1.3 | Recommended | Excellent | Use when possible |

### Certificate-Based Authentication

```
RSA Certificates
- 2048-bit: Minimum acceptable
- 3072-bit: Better security
- 4096-bit: Highest security (slower)

ECDSA Certificates
- ECDSA P-256: Equivalent to RSA 2048-bit
- ECDSA P-384: Equivalent to RSA 3072-bit
- ECDSA P-521: Equivalent to RSA 4096-bit
- Faster than RSA, recommended
```

### Client Types

#### Full Client
```
Advantages:
- Full network access
- Split tunneling support
- Performance optimization
Disadvantages:
- Installation required
- Maintenance overhead
- Multi-platform support
```

#### Clientless
```
Advantages:
- Browser-based access
- No installation required
- Cross-platform compatible
Disadvantages:
- Limited functionality
- No split tunneling
- Resource usage on server
```

### Protocol Subtypes

#### SSL VPN Portal
- Web-based interface
- Access to specific applications
- HTTP/HTTPS portals
- Limited network access

#### SSL VPN Tunnel
- Complete network access
- Requires client software
- More similar to traditional VPN

#### Hybrid Approaches
- Browser extension
- Lightweight client
- Balance of convenience and functionality

## WireGuard

### Characteristics
- **Layer**: Network layer (Layer 3)
- **Code**: ~4000 lines vs 400,000+ for IPsec
- **Performance**: Excellent, minimal overhead
- **Encryption**: ChaCha20-Poly1305
- **Key Exchange**: Curve25519
- **Status**: Production-ready, rapidly gaining adoption

### Advantages
```
Simplicity: Minimal configuration needed
Performance: 10-15x faster than OpenVPN
Modern Crypto: Uses current best practices
Roaming: Excellent mobile support
Security: Fewer lines = fewer vulnerabilities
```

### Disadvantages
```
Maturity: Newer protocol (vs IPsec/TLS)
Ecosystem: Fewer enterprise features
Vendor Support: Limited in traditional equipment
Logging: Minimal by default
```

### Cryptographic Suite
```
Handshake:
- Curve25519 for ECDH
- ChaCha20 for key derivation
- SipHash for cookies

Data Transport:
- ChaCha20-Poly1305 AEAD cipher
- Blake2s for hashing
```

### Configuration Simplicity
```
# Minimal configuration needed
[Interface]
PrivateKey = <key>
Address = 10.0.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <key>
AllowedIPs = 10.0.0.2/32
Endpoint = 8.8.8.8:51820
```

## Legacy Protocols (NOT RECOMMENDED)

### PPTP (Point-to-Point Tunneling Protocol)

**Characteristics**
- **Layer**: 2-3
- **Encryption**: MS-CHAP-v2 (weak)
- **Status**: DEPRECATED, do not use
- **Issues**: Known cryptographic weaknesses, broken authentication

**Why to Avoid**
```
- Authentication weakness: MS-CHAP-v2 broken
- Encryption: Weak RC4 cipher
- Firewall Issues: Difficult to traverse firewalls
- Speed: No longer relevant advantage
- Security: Multiple published attacks
```

### L2TP (Layer 2 Tunneling Protocol)

**Characteristics**
- **Layer**: 2-3
- **Encryption**: Typically IPsec
- **Status**: DEPRECATED for new deployments
- **Issues**: Only encryption via IPsec, no native crypto

**When Acceptable**
```
- Legacy systems requiring L2TP
- Combined with IPsec (L2TP/IPsec)
- No native encryption support
- Migration path from PPTP
```

## OpenVPN

### Characteristics
- **Layer**: Application layer (Layer 4)
- **Encryption**: OpenSSL library (AES, Camellia, CAST)
- **Key Exchange**: RSA, TLS
- **Standard**: Custom, widely deployed
- **Use Cases**: Cross-platform, flexible deployments

### Strengths
```
Cross-Platform: Windows, macOS, Linux, mobile
Flexibility: Highly configurable
Performance: Decent, not optimized
Portability: UDP or TCP over port 443
Security: Decent, but not optimized
```

### Weaknesses
```
Performance: Slower than WireGuard
Complexity: More configuration than WireGuard
Code Size: Larger attack surface than WireGuard
Mobile: Not native support, requires apps
```

## Protocol Selection Guide

### Site-to-Site Connectivity
**Best Choice**: IPsec with IKEv2
```
Reasons:
- Standard enterprise protocol
- Excellent reliability
- Hardware acceleration support
- Scalability to many sites
```

### Remote Access (Employees)
**Best Choice**: WireGuard or TLS VPN
```
WireGuard:
- Modern client
- Excellent performance
- Easy configuration

TLS VPN:
- Legacy infrastructure
- Clientless option
- Enterprise features
```

### Secure Communication (Applications)
**Best Choice**: TLS 1.3
```
Reasons:
- Application layer encryption
- No separate VPN needed
- Modern security
- Better performance
```

### Cross-Platform Deployment
**Best Choice**: WireGuard or OpenVPN
```
WireGuard:
- Growing support
- Excellent performance
- Modern security

OpenVPN:
- Proven compatibility
- More mature
- Flexible deployment
```

### Mobile-First Organization
**Best Choice**: WireGuard
```
Reasons:
- Excellent mobility support
- Roaming without reconnection
- Low battery impact
- Growing app support
```

## Deployment Considerations

### Firewall Traversal
```
IPsec: Difficult, requires special rules
TLS/SSL: Easy, port 443 standard
WireGuard: Easy, single UDP port
OpenVPN: Moderate, TCP/UDP configurable
```

### Latency
```
IPsec: Low overhead (hardware acceleration)
WireGuard: Very low (optimized code)
TLS/SSL: Medium (encryption overhead)
OpenVPN: Medium-high (more processing)
```

### CPU Utilization
```
IPsec: Low (often hardware accelerated)
WireGuard: Very low (minimal code)
TLS/SSL: Medium (asymmetric operations)
OpenVPN: Higher (more processing steps)
```

### Bandwidth Overhead
```
IPsec: ~20-50 bytes per packet (tunnel mode)
WireGuard: ~16 bytes per packet
TLS/SSL: ~29+ bytes per record
OpenVPN: ~40-60 bytes per packet
```
