# WireGuard Reference

## Protocol Overview

WireGuard is a modern VPN protocol designed with minimalism, performance, and security. It uses a tiny kernel module (approximately 4,000 lines of code) and modern cryptography.

## Core Cryptography

### Key Exchange
- **Curve25519**: Modern elliptic curve for key agreement
- **32-byte keys**: 256-bit symmetric key size
- **No cryptographic agility**: One cipher suite, no legacy algorithms
- **Perfect Forward Secrecy**: Implicit in protocol design

### Symmetric Encryption
- **ChaCha20**: Stream cipher for bulk data
- **Poly1305**: Message authentication code (MAC)
- **ChaCha20-Poly1305**: AEAD (Authenticated Encryption with Associated Data)
- **12-byte nonce**: Per-packet nonce management

### Hash Functions
- **BLAKE2s**: Fast cryptographic hash
- **512-bit output**: Secure hash for key derivation
- **32-bit output**: Session identifiers

### Handshake Protocol
1. **Initiator sends handshake initiation**
   - Ephemeral public key
   - Static public key (encrypted)
   - Timestamp (encrypted)

2. **Responder sends handshake response**
   - Ephemeral public key
   - Empty payload (encrypted)
   - Static public key identity

3. **Session established**
   - Symmetric keys derived
   - Data transfer begins
   - Handshake authentication verified

## Protocol Mechanics

### Peer Discovery and Key Exchange
- **Static configuration**: Peer public keys and endpoints
- **No master keys**: Each peer has unique keypair
- **Asymmetric trust**: Different keys in each direction possible
- **Endpoint migration**: Supports roaming between IPs

### Data Encapsulation
- **Packet format**: Message type (1 byte) + Data
- **Message types**:
  - Type 1: Handshake initiation
  - Type 2: Handshake response
  - Type 3: Transport data
  - Type 4: Cookie reply (DoS protection)

### Packet Structure
```
[Message Type: 1 byte]
[Sender Index: 4 bytes]
[Receiver Index: 4 bytes]
[Counter: 8 bytes]
[Encrypted Packet + Poly1305 Auth Tag: up to 65541 bytes]

Total Header Overhead: 16 bytes
```

## Interface Configuration

### Interface Parameters
- **Private key**: 32-byte private key (base64 encoded)
- **Public key**: Derived from private key
- **Address**: IPv4/IPv6 address assigned to interface
- **MTU**: Maximum transmission unit (default 1420 bytes)
- **Listen port**: UDP port for incoming connections

### Peer Configuration
- **Public key**: Peer's public key
- **Endpoint**: IP address and port (optional)
- **Allowed IPs**: Which traffic goes to this peer (subnet list)
- **Persistent keepalive**: Keepalive interval for NAT

## Deployment Models

### Point-to-Point
- **Topology**: Direct connection between two peers
- **Use case**: VPS-to-VPS, office-to-office
- **Configuration**: Simple, one connection per peer

### Hub-and-Spoke
- **Topology**: Central hub with many spoke peers
- **Use case**: VPN server with multiple clients
- **Configuration**: Hub has many peer configs, spokes have one

### Full Mesh
- **Topology**: Every peer connects to every other peer
- **Use case**: Distributed systems, mesh networks
- **Configuration**: Each peer has N-1 peer configurations

### Roaming Clients
- **Topology**: Clients with dynamic IP addresses
- **Use case**: Mobile users, BYOD
- **Configuration**: Endpoint optional, allowed IPs determines traffic
- **Keepalive**: Periodic packets to maintain NAT mappings

## NAT Traversal

### Challenge
- UDP-based protocol
- Firewalls may close connections during inactivity
- NAT devices may invalidate mappings

### Solutions

#### Persistent Keepalive
```
[Peer]
PublicKey = ...
Endpoint = 192.0.2.1:51820
AllowedIPs = 10.0.0.2/32
PersistentKeepalive = 25
```
- Sends keepalive packet every 25 seconds
- Keeps NAT mapping alive
- Maintains ability to receive incoming traffic

#### Endpoint Discovery
- First packet from peer establishes source IP/port
- Subsequent packets from different source IP update endpoint
- Roaming clients automatically handled

#### Port Forwarding
- Manual port forward on gateway device
- WireGuard traffic reaches gateway
- Gateway forwards to internal peer
- Alternative to UPnP/NAT-PMP

## Cryptographic Properties

### Security Levels
- **Encryption strength**: ChaCha20 = 256-bit key space
- **Authentication strength**: Poly1305 = 128-bit authentication
- **Key exchange strength**: Curve25519 = 128-bit ECDH
- **Hash strength**: BLAKE2s = 256-bit output

### Attack Resistance
- **Replay attacks**: Counter-based defense
- **Man-in-the-middle**: Static key authentication
- **Quantum computers**: Not quantum-resistant (no PQC yet)
- **Timing attacks**: Constant-time operations

### Cryptographic Assurances
- **Confidentiality**: All traffic encrypted
- **Integrity**: Poly1305 ensures unmodified packets
- **Authenticity**: Static key authentication
- **Forward Secrecy**: Ephemeral keys per handshake

## Performance Characteristics

### Throughput
- **10+ Gbps**: Hardware-accelerated (CPU offload)
- **Software**: 5-10 Gbps on modern CPUs
- **Comparison**: 2-5 Gbps for IPsec, 0.3-0.8 Gbps for OpenVPN

### Latency
- **Kernel module**: Minimal overhead (~0.05-0.2 ms)
- **Userspace**: Slightly higher overhead
- **Hardware acceleration**: Further reduced latency

### CPU Efficiency
- **Per-byte CPU cost**: Significantly lower than alternatives
- **Encryption**: Hardware AES-NI or software ChaCha20
- **Handshake**: Minimal CPU cost

## Platform Support

### Linux
- **Kernel integration**: Since Linux 5.6
- **Installation**: Built-in or separate module
- **Distribution support**: All major distributions
- **Performance**: Highest due to kernel integration

### FreeBSD
- **Kernel module**: Available since 12.1
- **Performance**: Excellent performance
- **Configuration**: Similar to Linux

### macOS
- **App**: WireGuard app from App Store
- **Integration**: Network extension framework
- **Performance**: Good performance

### Windows
- **Application**: WireGuard for Windows
- **Integration**: WinTun driver for filtering
- **Performance**: Good performance

### iOS/Android
- **Apps**: WireGuard from app stores
- **Integration**: VPN framework on platform
- **Features**: Split tunneling, on-demand VPN

### Other Platforms
- **OpenWrt**: Supported on most routers
- **Mikrotik**: Router OS support
- **Edge devices**: Various IoT platforms
- **AWS**: Available via TUN devices

## Key Management

### Key Generation
```bash
# Generate private key
wg genkey > privatekey

# Generate public key from private key
wg pubkey < privatekey > publickey

# Generate pre-shared key (optional, for additional security)
wg genpsk > presharedkey
```

### Key Rotation
- **No built-in key rotation**: Must be manual
- **Strategy**: Generate new keys periodically
- **Implementation**: Configuration update and reload
- **Downtime**: Brief interruption during update

### Key Storage
- **File permissions**: 600 (read/write owner only)
- **Encryption**: Store encrypted if sensitive
- **Backup**: Secure backup for recovery
- **Lifecycle**: Track key age, plan rotation

## Allowed IPs

### Concept
- **Source routing**: Determines which peer gets traffic
- **Subnet definition**: CIDR notation (10.0.0.1/32, 10.0.0.0/24)
- **Matching logic**: Longest prefix match
- **Unmatched traffic**: Dropped or routed normally

### Examples
```
Peer A: AllowedIPs = 10.0.0.0/24
  - Traffic destined to 10.0.0.1-254 goes to Peer A

Peer B: AllowedIPs = 10.0.1.0/24, 192.168.0.0/16
  - Traffic to 10.0.1.x or 192.168.x.x goes to Peer B

Catch-all: AllowedIPs = 0.0.0.0/0, ::/0
  - All other traffic tunneled through this peer
```

## Comparison with Other VPNs

### vs. IPsec
- **Complexity**: WireGuard much simpler
- **Performance**: Similar with hardware acceleration
- **Standards**: IPsec more standardized
- **Maturity**: IPsec more mature, WireGuard newer

### vs. OpenVPN
- **Performance**: WireGuard significantly faster
- **Complexity**: WireGuard simpler configuration
- **Auditability**: WireGuard smaller code base
- **Adoption**: OpenVPN more widespread

### vs. SSL/TLS VPN
- **Use case**: Different (Site-to-site vs. remote access)
- **Performance**: WireGuard faster for site-to-site
- **Authentication**: Different models
- **Deployment**: Different architectures

## Security Considerations

### Advantages
- **Code review**: Small code base easy to audit
- **Modern crypto**: Uses latest cryptographic standards
- **Simplicity**: Fewer features = fewer vulnerabilities
- **Constant-time**: Protected against timing attacks

### Disadvantages
- **No feature richness**: Some enterprises need more options
- **Quantum-resistant**: Not quantum-resistant (future concern)
- **Fingerprinting**: Predictable message sizes
- **Limited anonymity**: Static IP addresses per peer

## Advanced Features

### Pre-Shared Keys (PSK)
- Additional layer of security beyond static keys
- Protects against quantum computer attacks (theoretically)
- Slower to verify (cryptographic cost)
- Optional per-peer

### Privileged Tunneling
- Run WireGuard with reduced privileges
- Separate processes for unprivileged operations
- Enhanced security posture

## Troubleshooting

### Common Issues
1. **Peer not reachable**: Endpoint incorrect or firewall blocking
2. **Intermittent connectivity**: NAT timeout or keepalive too low
3. **One-way traffic**: Allowed IPs mismatch on either side
4. **Poor performance**: MTU too large, CPU bound encryption
5. **High latency**: Network path or hardware issues

### Diagnostic Commands
```bash
# Show interface status
ip link show wg0
ip addr show wg0

# Show WireGuard status
wg show

# Show WireGuard detailed info
wg show all dump

# Check packet statistics
ip -s link show dev wg0

# Trace connections
tcpdump -i wg0

# Check for fragmentation
ping -D -s 1400 <peer-ip>
```
