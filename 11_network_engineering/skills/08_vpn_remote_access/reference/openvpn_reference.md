# OpenVPN Reference

## Protocol Architecture

OpenVPN is an open-source VPN protocol based on SSL/TLS that operates at Layer 3-4 (can work with tun or tap devices).

## Core Technology Stack

### TLS/SSL Foundation
- **TLS 1.2 Minimum**: Modern TLS versions
- **Certificate-based Authentication**: X.509 certificates
- **Diffie-Hellman**: Key exchange
- **OpenSSL Library**: Standard OpenSSL integration

### Encryption Options
- **AES-256-CBC**: Industry standard
- **AES-128-CBC**: Acceptable alternative
- **AES-256-GCM**: Modern authenticated encryption
- **ChaCha20-Poly1305**: Modern cipher suite

### Hash Algorithms
- **SHA-256**: Standard digest
- **SHA-512**: Stronger variant
- **MD5**: Deprecated (no longer use)

## Operating Modes

### Tunnel Mode
- **TUN device**: Network layer VPN
- **Full IP packet tunneling**: All IP traffic encrypted
- **Efficiency**: Lower overhead than TAP
- **Use case**: Site-to-site VPN, remote access

### Bridge Mode
- **TAP device**: Data link layer VPN
- **Ethernet frame tunneling**: Layer 2 traffic
- **Use case**: Network bridging, legacy applications
- **Overhead**: Significant performance impact

## Architecture Models

### Client-Server

**Server Configuration**
```
Server:
  - Accepts multiple client connections
  - Maintains VPN tunnel per client
  - Distributes IP addresses via DHCP
  - Routes traffic between clients and networks
  - Manages session state

Clients:
  - Connect to server
  - Receive IP address from server pool
  - All traffic through server
  - Roaming supported
```

**Characteristics**
- Traditional architecture
- Centralized management
- Scalability limited by server
- Simple configuration for clients
- Server acts as central hub

### Peer-to-Peer

**Configuration**
```
Peer A and Peer B:
  - Direct tunnel between peers
  - No central server
  - Symmetric configuration
  - Equal traffic distribution
```

**Characteristics**
- Decentralized architecture
- Direct connections
- Better performance
- Manual peer management
- Suitable for small deployments

### Mesh Network

**Topology**
- Multiple peers interconnected
- Partial or full mesh possible
- Each peer maintains tunnels
- Distributed routing

**Implementation**
- Central controller (optional) for management
- Automatic peer discovery
- Dynamic tunnel establishment
- Health checking and failover

## Authentication Methods

### Certificate-Based (Most Common)

**Components**
- **CA Certificate**: Root certificate authority
- **Server Certificate**: Server identity certificate
- **Client Certificate**: Client identity certificate
- **Server Key**: Private key for server
- **Client Key**: Private key for client

**Process**
1. OpenVPN starts with --cert and --key options
2. Client initiates TLS handshake
3. Server and client exchange certificates
4. Mutual authentication verified
5. Encrypted channel established

### Pre-Shared Keys (PSK)

**Options**
- **Static Key**: Simple symmetric key
- **TLS-Auth Key**: Additional authentication
- **TLS-Crypt**: Encryption of TLS record layer

**Characteristics**
- Simpler than PKI
- No certificate management
- Limited to simple deployments
- Still requires strong keys

### Username/Password

**Integration**
- RADIUS backend
- LDAP authentication
- PAM (Pluggable Authentication Modules)
- Custom authentication plugin

**Security Consideration**
- Should be combined with certificate-based auth
- Requires secure password handling
- TLS protects password in transit
- Server-side hashing important

## Data Flow

### Tunnel Establishment
1. Client initiates connection to server
2. TLS handshake occurs
3. Certificates verified
4. Encryption keys negotiated
5. VPN tunnel ready for traffic

### Packet Processing
1. Application sends data to VPN IP
2. VPN client intercepts packet (TUN device)
3. OpenVPN encrypts payload
4. TLS record layer wraps encrypted data
5. UDP datagram sent to server
6. Server decrypts and forwards to destination

### Return Path
1. Server receives response traffic
2. Encrypts and sends to client
3. Client decrypts and injects into TUN
4. Application receives data

## Configuration Options

### Cipher Selection

**Secure Defaults**
```
cipher AES-256-GCM
auth SHA256
```

**Legacy Support**
```
cipher AES-128-CBC
auth SHA256
```

**Deprecated (Avoid)**
```
cipher BF-CBC          # Too weak
cipher AES-128-CBC     # Weak for new deployments
auth MD5               # Do not use
```

### Compression
- **LZ4 Compression**: Fast compression
- **LZO Compression**: Legacy compression
- **No Compression**: Recommended for security
- **Security Note**: Compression can leak information

### Key Parameters

```
# Client configuration
client
remote [server-ip] [port]
proto [udp|tcp]
dev [tun|tap]
remote-cert-tls server

# Server configuration
server 10.8.0.0 255.255.255.0
proto [udp|tcp]
port [port]
ca ca.crt
cert server.crt
key server.key
dh dh.pem
```

## Advanced Features

### Split Tunneling

**Usage**
- Route specific traffic through VPN
- Other traffic direct to internet
- Reduces server load
- Privacy trade-off

**Configuration**
```
push "route 10.0.0.0 255.255.255.0"  # Corporate network via VPN
# Other traffic not routed through VPN
```

### Full Tunnel

**Configuration**
```
push "redirect-gateway def1"  # All traffic through VPN
push "dhcp-option DNS 8.8.8.8"  # DNS settings
```

### Multi-Protocol Support

**Port Configuration**
```
# Listen on both UDP and TCP
proto udp
proto tcp
```

**Characteristics**
- UDP preferred for performance
- TCP fallback for firewall traversal
- May need separate instances

### Dynamic IP Assignment

**Server Configuration**
```
server 10.8.0.0 255.255.255.0
push "dhcp-option DNS 8.8.8.8"
ifconfig-pool 10.8.0.100 10.8.0.200
```

**Client Assignment**
- Automatic DHCP-style assignment
- Static allocation possible
- Per-client configuration files

### Session Management

**Idle Timeout**
```
inactive 3600  # Idle timeout 1 hour
```

**Keepalive**
```
keepalive 10 120  # Send keepalive every 10 sec, timeout 120 sec
```

**Rekeying**
```
reneg-sec 3600  # Rekey every hour
```

## Performance Considerations

### Throughput
- **UDP**: Better throughput (typically 300-800 Mbps)
- **TCP**: Lower throughput (firewall friendly)
- **Encryption**: AES-NI accelerates throughput
- **Hardware**: Crypto acceleration important for high throughput

### Latency
- **TLS Handshake**: 1-2 round trips
- **Per-packet**: Minimal additional latency
- **Network Path**: Dependent on server location
- **Encryption**: Minimal impact with hardware acceleration

### CPU Usage
- **Encryption**: Significant per-thread CPU cost
- **Multithreading**: Multiple instances improve scalability
- **Hardware Acceleration**: Critical for high throughput
- **Algorithm**: ChaCha20 more efficient than AES

### Scalability
- **Single Instance**: 100s of clients
- **Multiple Instances**: 1000s of clients possible
- **Load Balancing**: Distribution across servers
- **Clustering**: Not built-in, requires external LB

## Deployment Topologies

### Remote Access VPN
```
Users (anywhere) --> OpenVPN Server --> Corporate Network
  - Clients authenticate with credentials
  - Each client gets VPN IP
  - Access to internal resources
  - Traffic through server
```

### Site-to-Site VPN
```
Office A --> OpenVPN Server --> Office B
  - Endpoint routers as clients
  - Network-level connectivity
  - Traffic routed automatically
  - Persistent connection
```

### VPN Gateway Pattern
```
Public VPN Server --> Internal VPN Gateway --> Internal Network
  - Internal gateway handles routing
  - Public server for client access
  - Scalable architecture
  - Security isolation
```

## OpenVPN Community vs. OpenVPN Access Server

### OpenVPN Community Edition
- Open source (GPLv2)
- Free to use
- Community support
- Full feature set
- Suitable for most deployments

### OpenVPN Access Server
- Commercial product
- Based on community edition
- GUI management interface
- Professional support
- Advanced reporting
- Higher scalability

## Integration with Other Technologies

### Certificate Management
- EASYRSA for key generation
- Self-signed certificates
- Certificate Authority setup
- Certificate revocation lists (CRL)

### Firewall Integration
- Stateful firewall inspection
- DPI (Deep Packet Inspection)
- Rate limiting
- Access control lists

### Monitoring and Logging
- Per-session logging
- Connection attempts tracking
- Bandwidth monitoring
- Real-time statistics

## Security Best Practices

1. **Use TLS 1.2+**: Disable older TLS
2. **Strong Ciphers**: AES-256-GCM minimum
3. **Certificate Management**: Proper PKI
4. **TLS Auth**: Additional protection layer
5. **Firewall Rules**: Restrict VPN access
6. **Updates**: Keep OpenVPN current
7. **Monitoring**: Alert on suspicious activity
8. **Logging**: Audit trail for compliance

## Troubleshooting Common Issues

### Connection Issues
1. **Cannot connect**: Firewall blocking, wrong config
2. **Intermittent failures**: Keepalive issues, network instability
3. **Slow performance**: Encryption overhead, TCP vs UDP
4. **Certificate errors**: Invalid cert, CA mismatch

### Performance Issues
1. **Low throughput**: Encryption bottleneck, TCP mode
2. **High latency**: Server distance, network congestion
3. **CPU high**: Crypto heavy, multi-thread needed
4. **Memory issues**: Too many clients, buffer configuration

### Diagnostic Commands
```
# Monitor connection
tail -f /var/log/openvpn.log

# Check status
openvpn --version

# Performance testing
openssl speed aes-256-cbc

# Monitor bandwidth
iftop -i tun0

# Check active connections
netstat -tuln | grep :1194
```

## Comparison with Other VPN Solutions

| Feature | OpenVPN | IPsec | WireGuard |
|---------|---------|-------|-----------|
| **Code Base** | Moderate | Very Large | Very Small |
| **Throughput** | 300-800 Mbps | 2-5 Gbps | 10+ Gbps |
| **Setup Time** | Moderate | Fast | Very Fast |
| **Complexity** | Medium | High | Low |
| **Maturity** | Very Mature | Very Mature | Newer |
| **Auditability** | Good | Fair | Excellent |

## Use Cases

### Remote Access VPN
- Employees working from home
- Secure connection to corporate network
- Cost-effective alternative to hardware VPN
- Easy client distribution

### Site-to-Site VPN
- Office-to-office connectivity
- Branch office connection
- Redundancy with multiple connections
- Cost savings vs. MPLS

### Privacy/Anonymity
- Hide real IP address
- Bypass geographic restrictions
- Privacy on public networks
- Anonymous browsing (with caveats)
