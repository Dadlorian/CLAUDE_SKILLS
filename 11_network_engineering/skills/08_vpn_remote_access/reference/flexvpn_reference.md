# FlexVPN Reference

## Overview

FlexVPN (Flexible VPN) is a Cisco technology combining the benefits of DMVPN flexibility with IPsec encryption and modern IKEv2 authentication mechanisms.

## Key Differences from DMVPN

### FlexVPN Advantages
- **IKEv2 Protocol**: More efficient than DMVPN's IKEv1
- **Scalability**: Better suited for large deployments
- **Mobile Support**: Native MobIKE support for roaming
- **Certificate Support**: Easier PKI integration
- **Modern Architecture**: Built from ground up for flexibility

### DMVPN Comparison
- **DMVPN**: Mature, widely deployed
- **FlexVPN**: Newer, more flexibility
- **Migration Path**: DMVPN to FlexVPN upgrade possible
- **Feature Parity**: Mostly equivalent now

## Architecture Components

### 1. IKEv2 Protocol

**Advantages**
- Faster negotiation (fewer round trips)
- Better NAT traversal
- MobIKE for seamless roaming
- EAP support for advanced authentication
- RFC 7539 standardization

**Authentication Options**
- **Pre-shared Keys (PSK)**: Simpler configuration
- **Certificates**: PKI-based, more scalable
- **EAP (Extensible Authentication Protocol)**:
  - Username/password via RADIUS
  - Token-based authentication
  - Certificate-based with EAP

### 2. Encryption and Authentication

**IKEv2 Encryption Suites**
- **AES-GCM-128**: Lightweight encryption
- **AES-GCM-192**: Standard encryption
- **AES-GCM-256**: Strong encryption
- **ChaCha20-Poly1305**: Modern alternative

**Key Exchange Methods**
- **Diffie-Hellman (DH)**:
  - DH Group 14 (2048-bit)
  - DH Group 15 (3072-bit)
  - DH Group 16 (4096-bit)
- **Elliptic Curve DH**:
  - ECDH Group 19 (Curve25519)
  - ECDH Group 20 (Curve448)

### 3. Routing and Forwarding

**Route-Based VPN**
- Uses virtual tunnel interfaces (VTI)
- Dynamic routing protocols supported
- EIGRP, BGP, OSPF compatibility
- Static routes also supported

**Policy-Based VPN**
- Traditional ACL-based crypto policies
- Explicit traffic selection
- More granular control possible
- Less flexible than route-based

## Transport Types

### IPv4 Underlay
- Standard IPv4 connectivity
- Most common deployment
- Good for existing networks
- Well-understood troubleshooting

### IPv6 Underlay
- IPv6 transport for tunnels
- Future-proof architecture
- Dual-stack support
- Modern carrier deployments

### Mixed Transport
- IPv4 and IPv6 simultaneously
- Fallback mechanisms
- Gradual transition path
- Complex routing

## Deployment Models

### Hub-and-Spoke with FlexVPN
```
Hub Configuration:
  - IKEv2 server mode
  - Multiple spoke connections
  - Dynamic routing to redistribute routes
  - Centralized policy enforcement

Spoke Configuration:
  - IKEv2 client mode
  - Single hub connection
  - Dynamic routing to learn routes
  - Local policy application
```

### Any-to-Any Mesh
```
All Nodes:
  - IKEv2 initiator/responder capable
  - Multiple tunnel connections
  - Dynamic peer discovery
  - Distributed routing
```

### Hybrid Hub-and-Spoke + Mesh
```
Topology:
  - Spokes connect to hub
  - Spokes also peer with nearby spokes
  - Direct spoke-to-spoke on demand
  - Hub provides convergence point
```

## Advanced Features

### MobIKE (Mobility and Multihoming Protocol)

**Purpose**
- Seamless mobility (IP address change)
- Multihoming (multiple interfaces)
- Continued session after mobility event
- No re-authentication needed

**Use Cases**
- Mobile users switching networks
- Users between Wi-Fi and cellular
- Roaming devices
- Load balancing between interfaces

**Implementation**
- Automatic detection of IP changes
- Tunnel migration without tear-down
- Minimal packet loss during transition
- Periodic keepalives

### Dynamic Peer Discovery

**Capability**
- Peers can be added without reconfiguration
- Central controller provides peer list (optional)
- DHCP or manual configuration
- Automatic tunnel establishment

### QoS and Bandwidth Management

**Integration**
- Bandwidth allocation per tunnel
- Traffic prioritization
- Service classes support
- Rate limiting per flow

## Configuration Approaches

### CLI-Based Configuration
```
crypto ikev2 proposal PROPOSAL
  encryption aes-cbc-256
  integrity sha512
  dh-group 14

crypto ikev2 policy POLICY
  proposal PROPOSAL

crypto ikev2 keyring KEYRING
  peer [peer-ip]
    address [peer-ip]
    pre-shared-key [secret]

crypto ipsec transform-set TRANSFORM esp-aes 256 esp-sha-hmac

crypto ipsec profile PROFILE
  set transform-set TRANSFORM
  set pfs group14
  set security-association lifetime seconds 3600
```

### Model-Driven Configuration (Yang Models)
- Structured configuration
- Device/Network yang models
- Programmable interface
- Ansible/Terraform integration

## Integration Points

### SD-WAN Integration
- FlexVPN as underlay for SD-WAN
- Intelligent path selection over FlexVPN tunnels
- Zero-touch provisioning via controller
- Centralized policy management

### Secure Firewall Integration
- Threat prevention over FlexVPN
- Intrusion detection/prevention
- URL filtering
- Antimalware scanning

### Cloud Connectivity
- AWS Site-to-Site VPN compatible
- Azure VPN Gateway integration
- Google Cloud Interconnect alternative
- Hybrid cloud architecture

## Performance Optimization

### Encryption Acceleration
- Hardware acceleration (AES-NI)
- Crypto offload engines
- Performance scaling with hardware

### Bandwidth Optimization
- Compression (if applicable)
- QoS integration
- Intelligent path selection
- Multi-path load balancing

### Latency Reduction
- Direct tunnel paths (no hub traversal)
- Efficient handshake (IKEv2)
- Minimal encryption overhead
- Optimized timer values

## Scaling Considerations

### Number of Peers
- Hub-and-spoke: 100s to 1000s possible
- Mesh topology: Limited by CPU/memory
- Hybrid approaches: Balanced scalability
- Controller-assisted scaling

### Bandwidth Scaling
- Aggregate bandwidth management
- Per-tunnel bandwidth allocation
- Multi-path aggregation
- Load distribution

### Convergence Time
- IKEv2 faster than IKEv1
- Routing protocol impact
- Failover detection time
- Recovery mechanisms

## Troubleshooting

### IKEv2 Negotiation Issues

**Common Problems**
1. **Proposal Mismatch**: Different encryption suites
2. **DH Group Mismatch**: Incompatible key exchange
3. **Authentication Failure**: PSK/certificate mismatch
4. **Firewall Blocking**: UDP 500/4500 blocked

**Diagnostic Steps**
```
# Monitor IKEv2 negotiation
debug crypto ikev2

# Check tunnel status
show crypto ikev2 sa

# Verify proposals
show crypto ikev2 proposal

# Check peer connectivity
ping [peer-ip]

# Verify encryption
show crypto ipsec sa

# Check transforms
show crypto ipsec transform-set
```

### Traffic Flow Issues

**Common Problems**
1. **No Traffic**: Routing or ACL issue
2. **Asymmetric Flow**: One direction works
3. **Performance Degradation**: Encryption overhead
4. **Intermittent Failures**: Timeout or flapping

**Resolution**
- Verify VTI route propagation
- Check routing table
- Validate crypto ACL
- Monitor tunnel statistics

## Security Best Practices

1. **Use Strong Encryption**: AES-256 minimum
2. **PFS Mandatory**: Perfect Forward Secrecy enabled
3. **IKEv2 Only**: Disable IKEv1 completely
4. **Strong Authentication**: Use certificates over PSK
5. **Regular Rekeying**: Automatic lifetime management
6. **DPD Enabled**: Dead Peer Detection for failover
7. **Logging**: Comprehensive audit logging
8. **Monitoring**: Real-time tunnel monitoring

## Comparison with DMVPN

| Feature | DMVPN | FlexVPN |
|---------|-------|---------|
| **Protocol** | IKEv1 | IKEv2 |
| **Setup Time** | Slower | Faster |
| **NAT Traversal** | Fair | Excellent |
| **Mobility** | Limited | Native MobIKE |
| **Scalability** | Good | Excellent |
| **Maturity** | Very Mature | Mature |
| **Complexity** | Medium | Low-Medium |
| **Routing** | NHRP-based | Standard routing |

## Migration Path

### DMVPN to FlexVPN
1. **Pilot Phase**: Deploy FlexVPN at selected sites
2. **Validation**: Verify performance and features
3. **Parallel Run**: DMVPN and FlexVPN simultaneously
4. **Migration**: Move traffic to FlexVPN gradually
5. **Decommission**: Remove DMVPN when complete

## Use Cases

### Enterprise Branch Connectivity
- Scalable alternative to DMVPN
- Better performance characteristics
- Mobile user support
- Future-proof architecture

### Cloud Hybrid Architecture
- On-premises to cloud connectivity
- Multiple cloud providers
- Site-to-cloud VPN
- Automatic failover

### IoT Device Connectivity
- Lightweight devices
- Scalable connectivity
- Security enforcement
- Centralized management

### 5G/SD-WAN Integration
- Transport for SD-WAN
- Cloud RAN connectivity
- Network slicing support
- Service chaining
