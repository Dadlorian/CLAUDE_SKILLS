# IPsec Protocol Reference

## Protocol Stack Overview

IPsec operates at Layer 3 (Network Layer) and provides encryption, authentication, and integrity checking for IP traffic.

## Core Components

### 1. Internet Key Exchange (IKE)

#### IKEv1
- Two-phase negotiation process
- Phase 1: Establish secure channel (aggressive or main mode)
- Phase 2: Negotiate IPsec SAs (quick mode)
- Pre-shared keys or RSA signatures
- Aggressive mode for road warrior scenarios

#### IKEv2
- Reduced round trips (2-3 messages vs. 6-9 for IKEv1)
- RFC 7539 standardized
- Supports EAP (Extensible Authentication Protocol)
- Better NAT traversal
- Mobike for mobile users
- RFC 7383 for asymmetric authentication

### 2. Authentication Header (AH)
- Provides data origin authentication and integrity
- Does not provide confidentiality
- Tunnel and transport modes
- Header format:
  - Next Header
  - Payload Length
  - Reserved
  - SPI (Security Parameter Index)
  - Sequence Number
  - Authentication Data

### 3. Encapsulating Security Payload (ESP)
- Provides confidentiality, authentication, and integrity
- More commonly used than AH
- Header format:
  - SPI (Security Parameter Index)
  - Sequence Number
  - Initialization Vector (IV)
  - Ciphertext
  - Padding
  - Pad Length
  - Next Header
  - Authentication Data

### 4. Internet Protocol Security Database (SPDB)

#### Security Policy Database (SPD)
- Defines which traffic requires IPsec protection
- Policy entries specify:
  - Selector (source IP, destination IP, protocol, ports)
  - Action (protect, discard, bypass)
  - IPsec protocol (ESP, AH, or both)

#### Security Association Database (SAD)
- Contains active IPsec SAs
- Each SA includes:
  - Encryption algorithm and keys
  - Authentication algorithm and keys
  - Sequence numbers
  - Lifetime (time-based or volume-based)
  - Mode (tunnel or transport)

## Encryption Algorithms

### Symmetric Ciphers
| Algorithm | Block Size | Key Size | Performance | Status |
|-----------|-----------|----------|-------------|--------|
| 3DES | 64 bits | 168 bits | Slow | Deprecated |
| AES-CBC | 128 bits | 128/192/256 | Good | Standard |
| AES-GCM | 128 bits | 128/192/256 | Excellent | Recommended |
| AES-CCM | 128 bits | 128/192/256 | Good | Suitable |
| ChaCha20 | 256 bits | 256 | Excellent | Modern |

### Authentication Algorithms
| Algorithm | Output | Status | Use Case |
|-----------|--------|--------|----------|
| HMAC-MD5 | 128 bits | Deprecated | Legacy only |
| HMAC-SHA1 | 160 bits | Deprecated | Legacy only |
| HMAC-SHA256 | 256 bits | Standard | Recommended |
| HMAC-SHA384 | 384 bits | Standard | High security |
| HMAC-SHA512 | 512 bits | Standard | Very high security |
| AES-GMAC | 128 bits | Modern | GCM mode |

### Key Exchange Algorithms
| Algorithm | Strength | Audited | Notes |
|-----------|----------|---------|-------|
| DH Group 1 | 1024 bits | Yes | Deprecated |
| DH Group 5 | 1536 bits | Yes | Weak |
| DH Group 14 | 2048 bits | Yes | Standard |
| DH Group 15 | 3072 bits | Yes | Strong |
| DH Group 16 | 4096 bits | Yes | Very Strong |
| Elliptic Curve | Variable | Yes | Modern |

## VPN Modes

### Transport Mode
- End-to-end protection
- Used between hosts or between host and gateway
- Header and payload encrypted
- Original IP header visible
- Lower overhead
- Use case: Host-to-host VPN

### Tunnel Mode
- Entire IP packet encrypted
- New IP header added
- More secure (header encrypted)
- Higher overhead
- Use case: Gateway-to-gateway VPN (site-to-site)

## Security Associations (SA)

### SA Parameters
- **SPI**: Unique identifier for SA (32 bits)
- **Encryption Algorithm**: Algorithm and key material
- **Authentication Algorithm**: Hash algorithm and key
- **Sequence Number Counter**: Prevent replay attacks
- **Lifetime**: Hard and soft limits
- **Mode**: Tunnel or transport
- **Flags**: Tunnel (tunnel mode) or transport (transport mode)

### SA Lifetime Management
- **Hard Lifetime**: SAs expire and are deleted
- **Soft Lifetime**: SAs rekey before hard lifetime
- **Bytes Lifetime**: Delete SA after X bytes transmitted
- **Time-based Lifetime**: Delete after time period

## Perfect Forward Secrecy (PFS)

### Benefits
- Compromise of long-term key does not expose past sessions
- Each session has unique keys derived from ephemeral values
- Requires new key exchange for each session

### Implementation
- DH key exchange for each Phase 2 negotiation (IKEv1)
- IKEv2 implicit PFS
- Diffie-Hellman group selection critical
- Performance impact minimal with modern hardware

## NAT Traversal (NAT-T)

### Challenge
- IPsec uses protocol numbers (50, 51) not passed through NAT
- NAT devices don't understand AH/ESP protocols
- Source/destination IP changes break IPsec

### Solution (RFC 3947/3948)
- Encapsulate ESP in UDP (port 4500)
- Send keepalive packets every 20 seconds
- Detect NAT device changes
- Recalculate hashes if addresses change

## Dead Peer Detection (DPD)

### Mechanism
- Periodic status requests to verify peer reachability
- Reduce failover time on peer loss
- Two modes:
  - Periodic: Send status request every N seconds
  - On-demand: Send only if traffic delayed

### Benefits
- Fast detection of tunnel failure
- Automatic SA cleanup
- Better reliability for failover scenarios

## Antireplay Protection

### Mechanism
- Sequence number for each packet
- 32-bit or 64-bit counter
- Sliding window (default 64 packets)
- Packet arriving out of window discarded

### Benefits
- Prevents replay attacks
- Maintains packet order integrity
- Essential for security

## Fragmentation and PMTUD

### Challenge
- IPsec headers increase packet size
- May exceed MTU (Maximum Transmission Unit)
- Fragmentation may occur at tunnel endpoints

### Solutions
1. **Path MTU Discovery (PMTUD)**
   - Detect maximum allowed MTU
   - Adjust tunnel MTU accordingly
   - ICMP handling critical

2. **Manual MTU Adjustment**
   - Reduce local MTU on interfaces
   - Account for tunnel overhead (50-73 bytes typical)
   - Test with ping and traceroute

3. **TCP MSS Clamping**
   - Limit TCP segment size
   - Automatically adjust for tunnel
   - Prevent unnecessary fragmentation

## Common Vulnerabilities

### IKE/IPsec Vulnerabilities
- IV reuse in CBC mode (rare with proper implementation)
- Weak random number generation
- DPD timing attacks
- Aggressive mode enumeration

### Mitigations
- Use AES-GCM instead of CBC
- Strong PRNG implementation
- DPD randomization
- Disable aggressive mode if not needed

## Troubleshooting Indicators

### Common Issues
1. **No SA Established**: IKE failure, authentication problem
2. **Intermittent Connectivity**: Fragmentation, MTU issues
3. **Poor Performance**: Wrong encryption algorithm, MTU issues
4. **DPD Timeout**: Network congestion, keepalive frequency too low
5. **Replay Errors**: Out-of-order packets, window size too small

### Diagnostic Commands
- Monitor IKE/IPsec logs
- Check SA lifetime consumption
- Verify encryption/authentication algorithms
- Test MTU with traceroute and ping
- Capture packets with tcpdump/Wireshark
