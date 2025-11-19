# IPsec Remote Access VPN Implementation Guide

## Overview
Configure IPsec VPN for remote users to securely access corporate network. This guide covers client-to-gateway IPsec setup with IKEv2 and user authentication.

## Network Architecture
```
Remote Users (Mobile, Broadband)
         ↓
    VPN Client (Cisco Secure Client, strongSwan, etc.)
         ↓
   IPsec Tunnel (IKEv2 + ESP)
         ↓
  VPN Gateway (Cisco ASA, Palo Alto, Fortinet)
         ↓
 Corporate Network (10.0.0.0/8)
```

## Requirements
- VPN Gateway (ASA, FTD, Firewall)
- VPN Client application
- User credentials (RADIUS/AD or local database)
- Client certificates (for mutual authentication)
- At least 500 Kbps bandwidth per user

## Phase 1: Gateway Configuration (Cisco ASA)

### User Database Setup

#### Option A: Local Authentication
```cisco
! Create local user accounts
username vpn_user password Str0ng!Pass123
username vpn_user privilege 15

! Assign group policy
group-policy RemoteAccess internal
  attributes
    banner value "Welcome to Corporate VPN"
    dns-server value 8.8.8.8 1.1.1.1
    pfs enable
    split-dns value corp.internal
```

#### Option B: RADIUS Authentication
```cisco
! Configure RADIUS server
aaa-server RADIUS protocol radius
aaa-server RADIUS host 10.0.0.50
  key SecureRadiusKey123!
  timeout 10
  retries 3

! Apply to tunnel group
tunnel-group RemoteVPN general-attributes
  authentication-server-group RADIUS
  accounting-server-group RADIUS
```

### IKEv2 Configuration

```cisco
! Enable IKEv2
crypto ikev2 enable outside

! IKE Policy
crypto ikev2 policy 10
  encryption aes-256
  integrity sha256
  group 14
  lifetime 86400
  prf sha256

! IKEv2 Keyring (for client authentication)
crypto ikev2 keyring REMOTE-USERS
  peer 0.0.0.0 0.0.0.0
    address 0.0.0.0
    authentication pre-share
    pre-shared-key VPN_Client_PSK_123!

! IKEv2 Profile
crypto ikev2 profile REMOTE-PROFILE
  match identity remote address 0.0.0.0
  match identity user-name
  authentication remote user-nameor eap
  authentication local rsa-sig
  keyring REMOTE-USERS
  lifetime 86400
  ipsec-proposal REMOTE-TRANSFORM
  print-config
```

### IPsec Configuration

```cisco
! Transform set for remote access
crypto ipsec transform-set REMOTE-TRANSFORM esp-aes 256 esp-sha-hmac
mode tunnel

! IPsec profile
crypto ipsec profile REMOTE-PROFILE
  set transform-set REMOTE-TRANSFORM
  set pfs group14
  set security-association lifetime seconds 3600
```

### Access Lists

```cisco
! Traffic that should be allowed to VPN clients
access-list REMOTE-INBOUND extended permit ip any 10.0.0.0 255.0.0.0
access-list REMOTE-INBOUND extended permit ip any 192.168.0.0 255.255.0.0

! Split tunneling - determine what goes through VPN
access-list SPLIT-TUNNEL extended permit ip 10.0.0.0 255.0.0.0 any
access-list SPLIT-TUNNEL extended permit ip 192.168.0.0 255.255.0.0 any
```

### IP Address Pool

```cisco
! Allocate IP addresses for VPN clients
ip local pool REMOTE-USERS 10.255.0.1-10.255.0.254 mask 255.255.255.0

! Configure in tunnel group
tunnel-group RemoteVPN ipv4-attributes
  general
  address-pool REMOTE-USERS
  dns-server value 10.0.0.1 8.8.8.8
  dhcp-server value 10.0.0.2
  default-domain value corp.internal
```

### Tunnel Group Configuration

```cisco
tunnel-group RemoteVPN type remote-access
tunnel-group RemoteVPN general-attributes
  tunnel-group-list enable
  address-pool REMOTE-USERS
  default-group-policy RemoteAccess
  authentication-server-group RADIUS local
  accounting-server-group RADIUS

tunnel-group RemoteVPN ipsec-attributes
  ikev2 remote-authentication pre-share
  ikev2 local-authentication pre-share
  ikev2 rekey interval 3600
  ikev2 lifetime 86400
  peer-id-validate nocheck
  replay disable
```

### Crypto Map for Dynamic Peers

```cisco
! Dynamic crypto map for any remote peer
crypto dynamic-map REMOTE-DYNMAP 1 set transform-set REMOTE-TRANSFORM
crypto dynamic-map REMOTE-DYNMAP 1 set ikev2-profile REMOTE-PROFILE
crypto dynamic-map REMOTE-DYNMAP 1 set pfs group14

! Regular crypto map referencing dynamic map
crypto map REMOTE-MAP 1 ipsec-isakmp dynamic REMOTE-DYNMAP
crypto map REMOTE-MAP interface outside

! Set default counter
crypto map REMOTE-MAP 65535 ipsec-isakmp
  set transform-set REMOTE-TRANSFORM
```

### NAT Exemption

```cisco
! Exempt VPN traffic from NAT
access-list NO-NAT extended permit ip 10.255.0.0 255.255.0.0 10.0.0.0 255.0.0.0
access-list NO-NAT extended permit ip 10.255.0.0 255.255.0.0 192.168.0.0 255.255.0.0
nat (inside,outside) source static any any destination static 10.0.0.0 255.0.0.0 10.0.0.0 255.0.0.0 no-proxy-arp route-lookup
nat (inside,outside) source static any any destination static 192.168.0.0 255.255.0.0 192.168.0.0 255.255.0.0 no-proxy-arp route-lookup
```

## Phase 2: Client Configuration

### Cisco Secure Client Installation

**Windows/Mac/Linux**
1. Download from Cisco website
2. Run installer
3. Accept license agreement
4. Complete installation wizard
5. Restart computer

### Connection Profile Setup

**Windows Client Configuration**
```
Connection Entry Name: Corporate VPN
Server Address: vpn.company.com (or 203.0.113.1)
Protocol: IKEv2
Authentication: User Authentication + Device Certificate

Advanced Options:
  Enable Split Tunneling: Yes
  Split Tunnel List: 10.0.0.0/8, 192.168.0.0/16
  Enable Compression: No
  Perfect Forward Secrecy: On
```

**Configuration File (XML)**
```xml
<AnyConnectProfile>
  <ServerList>
    <HostEntry>
      <HostName>vpn.company.com</HostName>
      <HostAddress>203.0.113.1</HostAddress>
    </HostEntry>
  </ServerList>
  <AuthenticationMethods>
    <AuthenticationMethod Priority="0">
      <AuthType>UsernamePassword</AuthType>
    </AuthenticationMethod>
  </AuthenticationMethods>
  <ClientInitialization>
    <UseStartBeforeLogon>false</UseStartBeforeLogon>
    <AutoConnectOnStart>false</AutoConnectOnStart>
  </ClientInitialization>
</AnyConnectProfile>
```

### strongSwan Client (Linux/Open Source)

```bash
# Installation
sudo apt-get install strongswan

# Configuration file: /etc/ipsec.conf
conn corporate-vpn
  left=%defaultroute
  leftauth=eap-mschapv2
  right=203.0.113.1
  rightauth=pubkey
  rightid=vpn.company.com
  eap_identity=vpn_user
  auto=add
  keyexchange=ikev2
  ike=aes256-sha256-modp2048
  esp=aes256-sha256
  fragmentation=yes
  compress=no

# Credentials file: /etc/ipsec.secrets
vpn_user : EAP "Password123!"

# Connect
sudo ipsec start
sudo ipsec up corporate-vpn
```

## Phase 3: Testing and Verification

### Gateway Verification

```cisco
! Check active sessions
show crypto session brief

Output:
Crypto session status

Interface: outside
Session ID: 1
Status: UP-ACTIVE
Peer: 203.0.113.2:4500
IKEv2 Proposal: AES-256/SHA256/Group14
Transform Set: REMOTE-TRANSFORM
PFS (Y/N): Y

! Monitor client pool
show ip local pool

Output:
LocalPool         Begin              End                 InUse   Free
REMOTE-USERS      10.255.0.1        10.255.0.254       15      240

! Check authentication
show aaa authentication history

Output:
Session ID: 123
UserName: vpn_user
Server: RADIUS
Status: Success
```

### Client-Side Testing

```bash
# Verify VPN connection status
vpnclient stats  # Windows
ifconfig utun0   # macOS
ip addr show tun0 # Linux

# Test connectivity
ping 10.0.1.1    # Corporate resource
ping 192.168.1.1 # Another subnet

# Check traffic routing
route print | grep 10.0  # Windows
netstat -rn | grep 10.0  # Linux/macOS

# Measure latency
ping -c 10 10.0.1.1  # Average latency
```

### Traffic Inspection

```cisco
! Monitor VPN traffic
show crypto ipsec sa

Output:
interface: outside
  Crypto map tag: REMOTE-MAP, seq num: 1
  access list REMOTE-INBOUND extended permit ip any 10.0.0.0 255.0.0.0
    local ident (addr/mask/prot/port): (10.255.0.50/255.255.255.255/0/0)
    remote ident (addr/mask/prot/port): (0.0.0.0/0.0.0.0/0/0)
    #pkts encaps: 5200, #pkts encrypt: 5200
    #pkts decaps: 3150, #pkts decrypt: 3150
```

## Phase 4: Advanced Configuration

### Device Compliance Checking

```cisco
! Device posture enforcement
device-compliance
  policy vpn-device-compliance
    check-antivirus required
    check-firewall required
    check-patches required
    check-encryption required
    action non-compliant deny-access interval 15

! Apply to group policy
group-policy RemoteAccess internal
  attributes
    device-compliance-policy vpn-device-compliance
```

### Multi-Factor Authentication

```cisco
! Configure for MFA with Duo or similar
tunnel-group RemoteVPN general-attributes
  authentication-server-group RADIUS
  duo-auth-server primary
  duo-auth-server-fallback RADIUS
  duo-client-id [ID]
  duo-client-secret [SECRET]
```

### Load Balancing

```cisco
! Configure multiple VPN gateways
crypto ikev2 policy 10
  backup peer 203.0.113.2

! Or using DNS round-robin
vpn.company.com resolves to:
  203.0.113.1
  203.0.113.2
  203.0.113.3
```

## Phase 5: Monitoring and Maintenance

### Real-time Monitoring

```cisco
! Active sessions
show vpn session detail

! Per-user statistics
show vpn-sessiondb summary

! Bandwidth monitoring
show interface outside | include "packets output|bytes input/output"

! DPD and keepalive monitoring
debug crypto ikev2 protocol | include DPD
```

### Logging and Alerts

```cisco
! Enhanced logging
logging trap debugging
logging host inside 10.0.0.100

! VPN-specific logging
logging list VPN-LOG message 113001-113041
logging on

! Email alerts
object-group network VPN-ALERTS
  network-object 10.255.0.0 255.255.0.0

event-manager applet VPN-CONN-ALERT
  event syslog pattern "%ASA-.*-113009"
  action 1 mail server smtp.company.com
  action 2 mail from vpn-alerts@company.com
  action 3 mail to admin@company.com
  action 4 mail subject "VPN Connection Alert"
  action 5 mail body "User connected to VPN from $REMOTE_IP"
```

### Maintenance Tasks

**Monthly**
- Review user access logs
- Check for failed authentication attempts
- Verify client software versions
- Monitor bandwidth usage trends

**Quarterly**
- Security assessment of VPN infrastructure
- Update threat prevention signatures
- Review and renew certificates
- Audit user access permissions

**Annually**
- Comprehensive security audit
- Penetration testing
- Update encryption standards
- Plan for new technology adoption

## Troubleshooting Guide

### Client Cannot Connect

**Symptoms**: Connection failed, timeout

**Steps**
1. Verify server is reachable (ping/telnet)
2. Check firewall rules allow UDP 500, UDP 4500, ESP
3. Verify pre-shared key matches
4. Check client logs for specific error
5. Review gateway debug output

### Slow Performance

**Symptoms**: High latency, low throughput

**Solutions**
1. Disable compression
2. Optimize cipher (consider AES-NI)
3. Check network congestion
4. Move to closer VPN server
5. Use UDP instead of TCP if available

### Frequent Disconnections

**Symptoms**: Connection drops frequently

**Steps**
1. Increase DPD timeout
2. Enable keepalive
3. Check for NAT issues
4. Update client software
5. Consider network stability

### DNS Not Working

**Symptoms**: Cannot resolve internal hostnames

**Solution**
```cisco
! Push DNS settings to clients
group-policy RemoteAccess internal
  attributes
    dns-server value 10.0.0.1 10.0.0.2
    split-dns value internal.corp.com
    dhcp-server value 10.0.0.2
```

## Best Practices

- [ ] Enforce MFA for all remote access
- [ ] Implement split tunneling policy
- [ ] Regular security patches for client software
- [ ] Monitor bandwidth per user
- [ ] Implement idle timeout (15-30 minutes)
- [ ] Log all VPN activity
- [ ] Use TLS/IPsec for mutual authentication
- [ ] Implement device compliance checking
- [ ] Regular security awareness training
- [ ] Establish incident response procedures
