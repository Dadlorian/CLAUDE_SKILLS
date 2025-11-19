# IPsec Site-to-Site VPN Implementation Guide

## Overview
This guide provides step-by-step instructions for deploying IPsec site-to-site VPN between two office locations.

## Network Topology
```
Office A (192.168.1.0/24)     Office B (192.168.2.0/24)
    ↓                                ↓
Router A (192.0.2.1)      Router B (203.0.113.1)
    ↓                                ↓
    ←─────── IPsec Tunnel ──────────→
```

## Prerequisites
- Two routers supporting IPsec (Cisco, Palo Alto, Fortinet, etc.)
- Static public IP addresses on both routers
- Access to router CLI/management interface
- Network range documentation for both sites

## Step 1: Planning Phase

### Information Gathering

**Office A Configuration**
```
Public IP: 192.0.2.1
Local Subnet: 192.168.1.0/24
Router Type: Cisco ASA
```

**Office B Configuration**
```
Public IP: 203.0.113.1
Local Subnet: 192.168.2.0/24
Router Type: Cisco ASA
```

### Encryption Parameters
```
IKE Version: IKEv2 (preferred) or IKEv1
Encryption Algorithm: AES-256 (minimum)
Authentication Algorithm: SHA-256 or better
DH Group: Group 14 (2048-bit) minimum
IPsec Encryption: AES-256-GCM
IPsec Authentication: SHA-256
Perfect Forward Secrecy: Enabled (DH Group 14)
Lifetime: 3600 seconds
```

### Pre-Shared Key Generation
```bash
# Generate strong pre-shared key (on Linux/Unix)
openssl rand -base64 32
# Output: aBc1234567890DEF_GHIJKLMNOP+qrst/uVWXYZ=

# Alternative: Passphrase-based (less secure)
MySecurePass!234@OfficeVPN
```

## Step 2: Cisco ASA Configuration (Office A)

### Access Lists for IPsec

```cisco
access-list OFFICE-A-LOCAL extended permit ip 192.168.1.0 255.255.255.0 192.168.2.0 255.255.255.0
access-list OFFICE-B-LOCAL extended permit ip 192.168.2.0 255.255.255.0 192.168.1.0 255.255.255.0
```

### IKE Policy Configuration

```cisco
! IKEv2 configuration (recommended)
crypto ikev2 policy 1
  encryption aes-256
  integrity sha256
  group 14
  lifetime 86400

crypto ikev2 enable outside
```

### IPsec Transform Set

```cisco
crypto ipsec transform-set OFFICE-TRANSFORM esp-aes 256 esp-sha-hmac
mode tunnel
```

### IKE Keyrings and Peers

```cisco
crypto ikev2 keyring OFFICE-KEYRING
  peer 203.0.113.1
    address 203.0.113.1
    pre-shared-key aBc1234567890DEF_GHIJKLMNOP+qrst/uVWXYZ=

crypto ikev2 profile OFFICE-PROFILE
  match identity address 203.0.113.1
  authentication pre-share
  authentication remote pre-share
  keyring OFFICE-KEYRING
  lifetime 86400
  ipsec-proposal OFFICE-TRANSFORM
```

### Crypto Maps

```cisco
crypto map OFFICE-MAP 1 ipsec-isakmp
  set peer 203.0.113.1
  set transform-set OFFICE-TRANSFORM
  match address OFFICE-A-LOCAL
  set pfs group14
  set security-association lifetime seconds 3600

! Apply to outside interface
crypto map OFFICE-MAP interface outside
```

### NAT Exemption

```cisco
! Exempt VPN traffic from NAT
access-list NO-NAT extended permit ip 192.168.1.0 255.255.255.0 192.168.2.0 255.255.255.0
nat (inside,outside) source static OFFICE-A-SUBNET OFFICE-A-SUBNET destination static OFFICE-B-SUBNET OFFICE-B-SUBNET
```

### Interface Configuration

```cisco
! Ensure outside interface is configured
interface GigabitEthernet0/0
  nameif outside
  ip address 192.0.2.1 255.255.255.0
  speed 1000
  duplex full
  no shutdown
```

## Step 3: Cisco ASA Configuration (Office B)

### Same configuration as Office A with reversed addresses

```cisco
access-list OFFICE-B-LOCAL extended permit ip 192.168.2.0 255.255.255.0 192.168.1.0 255.255.255.0
access-list OFFICE-A-LOCAL extended permit ip 192.168.1.0 255.255.255.0 192.168.2.0 255.255.255.0

crypto ikev2 keyring OFFICE-KEYRING
  peer 192.0.2.1
    address 192.0.2.1
    pre-shared-key aBc1234567890DEF_GHIJKLMNOP+qrst/uVWXYZ=

crypto map OFFICE-MAP 1 ipsec-isakmp
  set peer 192.0.2.1
  match address OFFICE-B-LOCAL
```

## Step 4: Verification and Testing

### Check IKE Status

```cisco
! Office A
show crypto ikev2 sa
show crypto ikev2 stats

Output example:
IKEv2 SAs:
Active SA: 1
Peer Address         Port  Role  EncrypAlg/HashAlg/DHGrp  Lifetime
203.0.113.1         500   Rsp   AES-256/SHA256/Group14    3600
```

### Check IPsec Status

```cisco
show crypto ipsec sa

Output example:
interface: outside
  Crypto map tag: OFFICE-MAP, seq num: 1, local addr: 192.0.2.1

access-list OFFICE-A-LOCAL extended permit ip 192.168.1.0 255.255.255.0 192.168.2.0 255.255.255.0
  local ident (addr/mask/prot/port): (192.168.1.0/255.255.255.0/0/0)
  remote ident (addr/mask/prot/port): (192.168.2.0/255.255.255.0/0/0)
  current_peer: 203.0.113.1
  #pkts encaps: 1500, #pkts encrypt: 1500, #pkts digest: 1500
  #pkts decaps: 1240, #pkts decrypt: 1240, #pkts verify: 1240
```

### Ping Test

```bash
# From Office A PC
ping 192.168.2.50

# Expected output: Reply from 192.168.2.50 (Office B network)
```

### Detailed Connection Test

```cisco
show crypto session brief

Output:
Crypto session status

Interface: outside
Session ID: 1
Status: UP-ACTIVE
Peer: 203.0.113.1:500
IKEv2 Proposal: AES-256/SHA256/Group14
Transform Set: OFFICE-TRANSFORM
```

## Step 5: Troubleshooting

### IKE Negotiation Failure

**Symptoms**
- IKE Phase 1 fails
- Status shows "DOWN" or "PASSIVE"
- No tunnel establishment

**Debug Commands**
```cisco
debug crypto ikev2 protocol
debug crypto ikev2 error
show crypto ikev2 stats

! Specific error detail
show crypto session detail
```

**Common Issues & Solutions**

| Issue | Cause | Solution |
|-------|-------|----------|
| Peer unreachable | Network connectivity | Verify public IPs, check firewall |
| Proposal mismatch | Encryption mismatch | Verify IKE policy matches on both sides |
| PSK failure | Wrong pre-shared key | Verify PSK matches on both sides exactly |
| NAT issues | NAT breaking IPsec | Configure NAT exemption correctly |

### Traffic Not Passing

**Verification Steps**
```cisco
# 1. Check ACL match
show access-list OFFICE-A-LOCAL
  Should show increasing packet counts

# 2. Check NAT exemption
show nat | include OFFICE

# 3. Check routing
show route | include 192.168.2.0

# 4. Check IPsec SA
show crypto ipsec sa
  Should show #pkts encaps increasing
```

**Debug Commands**
```cisco
debug crypto condition peer 203.0.113.1
debug ipsec
```

### Performance Issues

**Symptoms**
- Slow throughput
- Intermittent packet loss
- High latency

**Troubleshooting**
```cisco
# Check MTU
show interface outside | include MTU

# IPsec adds ~50-70 bytes overhead
# Adjust tunnel MTU accordingly
# MTU 1500 - 70 = 1430 for tunnel

# Check throughput
show interface outside | include "packets output"

# Check DPD status
show crypto ikev2 sa detail
  Look for DPD status
```

## Step 6: Optimization

### QoS Configuration (Cisco ASA)

```cisco
! Define traffic classes
class-map OFFICE-VPN-TRAFFIC
  match access-list OFFICE-A-LOCAL

policy-map OFFICE-VPN-QOS
  class OFFICE-VPN-TRAFFIC
    priority percent 50

! Apply policy
service-policy OFFICE-VPN-QOS interface outside
```

### Rekeying Configuration

```cisco
! Shorter rekey for added security
crypto ipsec security-association lifetime seconds 1800

! Or by volume (after 1GB)
crypto ipsec security-association lifetime kilobytes 1000000
```

### PFS Configuration

```cisco
! Already configured in crypto map
crypto map OFFICE-MAP 1 ipsec-isakmp
  set pfs group14
```

## Step 7: Monitoring and Maintenance

### Continuous Monitoring

```cisco
! Create logging policy
logging host inside 10.0.0.50
logging trap informational

! Enable IPsec logging
logging enable
logging buffer-size 512000

! Monitor tunnel status
show crypto session brief  ! Run regularly
show crypto ipsec sa       ! Track packet statistics
```

### Certificate-Based Authentication (Optional)

**For PKI-based IPsec (more scalable)**

```cisco
! Generate self-signed cert (test environment)
crypto ca trustpoint OFFICE-CA
  enrollment terminal
  revocation-check crl
  subject-name CN=ASA-Office-A

crypto ca enroll OFFICE-CA
  ! Follow enrollment prompts

crypto ikev2 profile OFFICE-PROFILE
  match identity address 203.0.113.1
  authentication remote rsa-sig
  authentication local rsa-sig
  certificate OFFICE-CA
```

## Best Practices Checklist

- [ ] Pre-shared key is strong (32+ characters, random)
- [ ] IKE and IPsec parameters match on both sides
- [ ] NAT exemption configured correctly
- [ ] Test connectivity before production
- [ ] Monitor tunnel status daily
- [ ] Backup router configuration
- [ ] Document all encryption parameters
- [ ] Implement QoS for VPN traffic
- [ ] Set up logging and alerting
- [ ] Test failover scenario
- [ ] Plan for certificate renewal (if using PKI)
- [ ] Schedule security patches
