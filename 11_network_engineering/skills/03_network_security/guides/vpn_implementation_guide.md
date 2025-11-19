# VPN Implementation Guide

## Overview and Planning

### 1. VPN Type Selection

```
Decision Tree:

Purpose?
├─ Site-to-Site
│  ├─ IPsec (if existing cisco/fortinet)
│  ├─ WireGuard (if new deployment)
│  └─ MPLS (if carrier-based)
│
├─ Remote Access
│  ├─ SSL VPN (if user-friendly needed)
│  ├─ WireGuard (if performance critical)
│  └─ IPsec (if legacy required)
│
└─ End-to-End Encryption
   ├─ TLS/SSL (application-level)
   ├─ WireGuard (service encryption)
   └─ IPsec (network encryption)
```

### 2. Requirements Analysis

```
Gather Information:
- Number of remote users
- Required bandwidth
- Expected simultaneous connections
- Geographic locations
- Legacy device support needed
- Performance requirements (latency, throughput)
- Security requirements (encryption strength, authentication)
- Compliance requirements (regulatory standards)
- Budget and timeline
```

## IPsec Site-to-Site VPN

### Phase 1: Planning

```
Pre-Implementation Checklist:
☐ Confirm public IPs at both sites
☐ Determine DPD (Dead Peer Detection) strategy
☐ Choose encryption algorithm (AES-256 recommended)
☐ Choose authentication method
☐ Plan IP ranges (no overlapping)
☐ Plan failover sites
☐ Determine traffic to encrypt (split tunneling?)
☐ Plan QoS (quality of service)
☐ Document implementation details

Network Topology Example:
┌──────────────────┐          ┌──────────────────┐
│ Site A           │          │ Site B           │
│ 10.1.0.0/16     │          │ 10.2.0.0/16     │
│ Public IP: 1.1.1.1          Public IP: 2.2.2.2
│                  │          │                  │
│  [Firewall/VPN]─────IPsec───[Firewall/VPN]  │
│  (Encrypted)                (Encrypted)      │
└──────────────────┘          └──────────────────┘

Encrypted Traffic:
- Source: 10.1.x.x
- Destination: 10.2.x.x
- Tunnel: 1.1.1.1 ↔ 2.2.2.2
```

### Phase 2: Configuration (IKEv2 Recommended)

```
Step 1: IKEv2 Configuration (Cisco ASA Example)

! Enable IKEv2
crypto ikev2 enable

! Configure IKEv2 proposal
crypto ikev2 proposal SITE_TO_SITE
 encryption aes-cbc-256
 integrity sha384
 group 15  ! 3072-bit DH

! Configure IKEv2 policy
crypto ikev2 policy 1
 proposal SITE_TO_SITE
 lifetime 28800  ! 8 hours
 prf sha512
 dh-group 15

! Configure Phase 2 (IPsec)
crypto ipsec transform-set SITE_TO_SITE esp-aes 256 esp-sha512-hmac
 mode tunnel
 pfs group15

! Configure access list for traffic to encrypt
access-list SITE_B permit ip 10.1.0.0 255.255.0.0 10.2.0.0 255.255.0.0

! Configure crypto map
crypto map SITETOSITE 10 ipsec-isakmp
 set peer 2.2.2.2
 set access-list SITE_B
 set transform-set SITE_TO_SITE
 set pfs group15
 set lifetime 3600

! Apply crypto map to interface
interface GigabitEthernet0/0
 crypto map SITETOSITE

Step 2: Enable DPD (Dead Peer Detection)
! Detect non-responsive peers
crypto ikev2 dpd 10 3 on-demand

Step 3: Verify Configuration
show crypto ikev2 sa
show crypto ipsec sa
show crypto map
```

### Phase 3: Testing

```
Step 1: Connectivity Test
- Ping across tunnel (10.1.x.x ↔ 10.2.x.x)
- Verify tunnel is up (check IPsec SAs)
- Monitor traffic flow

Step 2: Failover Testing
- Disconnect primary link
- Verify secondary link takes over
- Re-establish primary
- Ensure no data loss

Step 3: Performance Testing
- Bandwidth test across tunnel
- Latency measurement
- Packet loss verification
- Connection stability

Step 4: Security Validation
- Verify encryption (tcpdump shows encrypted)
- Test with invalid credentials (should fail)
- Verify no plaintext in tunnel
- Check authentication works
```

## SSL/TLS VPN (Remote Access)

### Planning

```
Topology:
┌─────────────────┐
│  Remote User    │
│  (Home/Mobile)  │
└────────┬────────┘
         │ Encrypted
         │ (HTTPS/TLS)
         ▼
    [VPN Gateway]
    (Firewall with SSL VPN)
         │
    Decrypted
         │
         ▼
    [Internal Network]
```

### Implementation Steps

#### Step 1: Certificate Preparation

```
Server Certificate:
- Request from CA or self-signed
- Domain name must match VPN gateway
- Key size: RSA 2048+ or ECDSA P-256+
- Validity: 1-3 years

Client Authentication:
Option 1: Username/Password
Option 2: Client Certificate
Option 3: SAML/OAuth (enterprise)
Option 4: Multi-factor (Username + OTP)

Configuration Example (Cisco ASA):
! Generate self-signed cert
crypto ca trustpoint ASA_ROOT
 enrollment self
 fqdn vpn.example.com
 keypair ASA_KEYS
 hash sha256
 ip-address 10.1.100.1
 no dn

! Enroll certificate
crypto ca enroll ASA_ROOT

! Create SSL VPN group policy
group-policy REMOTE_ACCESS internal
 attributes
  vpn-idle-timeout 30
  vpn-session-timeout 480
  vpn-tunnel-protocol ssl-client
  split-tunnel-policy tunnelspecific
  split-tunnel-network-list value REMOTE_ACCESS_LIST
  wins-server none
  dns-server value 10.1.50.10
  dhcp-server none
  default-domain value example.com
```

#### Step 2: User Configuration

```
Create User Database:
- Local users (small deployments)
- RADIUS/LDAP (enterprise)
- SAML/OAuth (cloud)

Local User Example:
username vpn_user password Str0ngP@ssw0rd privilege 15

Access Control:
- Assign users to group policy
- Define resource access
- Set connection parameters
- Enable MFA if available
```

#### Step 3: Protocol Configuration

```
Configure SSL VPN (Cisco ASA):

! Enable SSL VPN
webvpn
 enable outside
 ! Customize portal
 customize hostname VPN_PORTAL

! Configure connection settings
tunnel-group REMOTE_ACCESS type remote-access
 general-attributes
  address-pool REMOTE_POOL
  authentication-server-group LOCAL
  accounting-server-group LOCAL
  default-group-policy REMOTE_ACCESS

 webvpn-attributes
  group-alias REMOTE_ACCESS enable

! Configure SSL settings
ssl-proxy server REMOTE
 server certificate vpn.example.com
 trusted-ca-certificates installed
 protocol tlsv1.2

! Configure IP pool for remote users
ip local pool REMOTE_POOL 192.168.100.1-192.168.100.100
```

#### Step 4: Client Configuration

**Windows AnyConnect Client:**
```
Installation:
1. Download from VPN gateway portal
2. Run installer
3. Accept license
4. Reboot if required

Configuration:
1. Launch AnyConnect
2. Enter gateway: vpn.example.com
3. Enter username
4. Enter password
5. Click Connect
6. Accept certificate warning (first time)
7. Connection established
```

**macOS/Linux AnyConnect:**
```
Installation:
brew install cisco-anyconnect

Configuration:
/opt/cisco/anyconnect/bin/vpn connect vpn.example.com
Enter username
Enter password
```

### Testing

```
Connectivity Tests:
- Connect from external network
- Verify internal access
- Ping internal servers
- Test application access

Security Tests:
- Verify encryption active (tcpdump)
- Test access controls
- Verify DNS resolution
- Test automatic reconnection

Performance Tests:
- Bandwidth measurement
- Latency testing
- Stability over time
- Battery impact (mobile)
```

## WireGuard VPN

### Advantages Over Traditional VPNs

```
Benefits:
- Modern cryptography (built-in)
- Minimal configuration needed
- Excellent performance
- Small code base (few vulnerabilities)
- Cloud-friendly
- Growing ecosystem
- Exceptional mobile support
```

### Site-to-Site Configuration

```
Basic Setup:

Server (Site A):
[Interface]
PrivateKey = <server_private_key>
Address = 10.255.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <client_public_key>
AllowedIPs = 10.2.0.0/16

Client (Site B):
[Interface]
PrivateKey = <client_private_key>
Address = 10.255.0.2/24
PrivateKey = <unique_key>

[Peer]
PublicKey = <server_public_key>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.1.0.0/16

Key Generation:
wg genkey | tee privatekey | wg pubkey > publickey
```

### Implementation Steps

```
Step 1: Generate Keys
wg genkey | tee server_private | wg pubkey > server_public
wg genkey | tee client_private | wg pubkey > client_public

Step 2: Create Configuration Files

Server (/etc/wireguard/wg0.conf):
[Interface]
Address = 10.255.0.1/24
PrivateKey = <server_private>
ListenPort = 51820

[Peer]
PublicKey = <client_public>
AllowedIPs = 10.2.0.0/16

Client (/etc/wireguard/wg0.conf):
[Interface]
Address = 10.255.0.2/24
PrivateKey = <client_private>

[Peer]
PublicKey = <server_public>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.1.0.0/16

Step 3: Enable and Start
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

Step 4: Verify
wg show
ip addr show wg0
```

## Monitoring and Maintenance

### Monitoring Metrics

```
Key Metrics to Track:
- VPN tunnel status (up/down)
- Connection count
- Bandwidth utilization
- Latency
- Packet loss
- Failed authentications
- Disconnection rate
- Data transferred

Alerting Thresholds:
- Tunnel down: Immediate alert
- Connection failures > 10/hour: Alert
- High latency (>200ms): Alert
- Packet loss > 1%: Alert
- Unusual bandwidth: Investigate
```

### Maintenance Tasks

```
Daily:
- Monitor tunnel status
- Check alert logs
- Verify connectivity

Weekly:
- Review connection logs
- Check for failed authentications
- Verify performance metrics

Monthly:
- Review user access patterns
- Test failover if applicable
- Update logs archive
- Security review

Quarterly:
- Penetration test VPN
- Review security policies
- Update certificates (if needed)
- Capacity planning

Annually:
- Full security audit
- User access review
- Update to latest firmware
- Compliance validation
- Renewal of certificates
```

## Troubleshooting Common Issues

### Issue 1: VPN Tunnel Not Coming Up

```
Diagnosis:
1. Check gateway reachability (ping/traceroute)
2. Verify firewall rules allow VPN traffic
3. Check credentials/certificates
4. Review VPN logs for errors

Common Causes:
- Firewall blocking VPN ports
- Incorrect peer addresses
- Certificate mismatch
- Wrong encryption parameters

Solution:
1. Verify firewall rule allows VPN protocol
2. Confirm peer IPs are correct
3. Validate certificates
4. Sync encryption parameters
5. Test connectivity to gateway
```

### Issue 2: Intermittent Disconnections

```
Diagnosis:
- Check for network timeouts
- Review logs for disconnection patterns
- Check DPD settings
- Monitor connection stability

Causes:
- Idle timeout too short
- DPD too aggressive
- Network instability
- Client application issues

Solution:
- Increase idle timeout
- Adjust DPD parameters
- Improve network stability
- Update client software
```

### Issue 3: Poor Performance

```
Diagnosis:
- Measure throughput
- Check latency
- Monitor packet loss
- Check CPU/memory utilization

Causes:
- Hardware limitation
- Encryption overhead
- Network congestion
- Firewall bottleneck

Solution:
- Upgrade hardware
- Enable hardware acceleration
- Optimize MTU size
- Distribute load across VPN gateways
- Reduce encryption strength if acceptable
```
