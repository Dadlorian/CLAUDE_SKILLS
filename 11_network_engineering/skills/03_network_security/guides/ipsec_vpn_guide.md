# IPsec VPN Implementation Guide

## IPsec Fundamentals

### Components Overview

```
IPsec Stack:

Layer 1: Key Management (IKE)
├── IKEv1: Phase 1 (SA negotiation)
├── IKEv1: Phase 2 (IPsec negotiation)
└── IKEv2: Full negotiation in 4 messages

Layer 2: Encryption (IPsec)
├── ESP (Encapsulating Security Payload)
├── AH (Authentication Header)
└── Tunnel vs Transport mode

Layer 3: Protocols
├── TCP/UDP/IP
└── Data transmission
```

## IKEv2 Site-to-Site Configuration

### Step 1: Basic Configuration (Cisco ASA)

```
Site A Configuration:

! IKEv2 Phase 1 Policy
crypto ikev2 proposal SITE_TO_SITE
 encryption aes-cbc-256
 integrity sha384
 group 15

crypto ikev2 policy 1
 proposal SITE_TO_SITE
 lifetime 28800

! Peer Configuration
crypto ikev2 enable outside

! IKEv2 Keyring (Pre-shared key)
crypto ikev2 keyring KEY_RING
 peer 2.2.2.2
  address 2.2.2.2
  pre-shared-key SuperSecretPSK123!

! IKEv2 Profile
crypto ikev2 profile IKE_PROFILE
 keyring KEY_RING
 lifetime 28800
 match identity remote address 2.2.2.2

! IPsec Phase 2 (Child SA)
crypto ipsec transform-set IPSEC_TS esp-aes 256 esp-sha512-hmac
 mode tunnel
 pfs group15

! Traffic to encrypt
access-list ENCRYPT_TRAFFIC permit ip 10.1.0.0 255.255.0.0 10.2.0.0 255.255.0.0

! Crypto Map
crypto map CMAP 1 ipsec-isakmp
 set peer 2.2.2.2
 set ikev2-profile IKE_PROFILE
 set access-list ENCRYPT_TRAFFIC
 set transform-set IPSEC_TS
 set pfs group15
 set lifetime seconds 3600

! Apply to Interface
interface GigabitEthernet0/0
 crypto map CMAP

! DPD Configuration
crypto ikev2 dpd 10 3 on-demand
```

### Step 2: Perfect Forward Secrecy (PFS)

```
PFS Enables:
- New key for each session
- Compromise of main key doesn't expose past sessions
- More CPU intensive (5-10% overhead)

Configuration:
crypto ipsec transform-set IPSEC_TS esp-aes 256 esp-sha512-hmac
 mode tunnel
 pfs group15   ← Enable PFS

DH Groups (Key Exchange):
group 15 = 3072-bit (Recommended)
group 16 = 4096-bit (Stronger, slower)
group 19 = Curve P-256
group 20 = Curve P-384

Verify:
show crypto ikev2 sa
show crypto ipsec sa
```

### Step 3: Verification and Testing

```
Verify IKE Phase 1:
show crypto ikev2 sa detailed

Output:
IKEv2 SAs:
Profile parent_profile:
  Tunnel-id Local Remote fvrf/ivrf Status
  1 2.2.2.1 2.2.2.2 none/none ESTABLISHED

Verify IPsec Phase 2:
show crypto ipsec sa interface GigabitEthernet0/0

Output:
interface: GigabitEthernet0/0
    Crypto Map Tag: CMAP, seq num 1
    esp server_to_site:
        spi: 0x12345678(305441784) transform: esp-aes-256 esp-sha512-hmac ,
        in use settings ={Tunnel, }

Test Connectivity:
ping 10.2.1.1  (source 10.1.1.1)

View Counters:
show crypto ipsec sa
  (look for "packets encaps" and "packets decaps")
```

## High Availability IPsec

### Active-Passive Configuration

```
Topology:
Site A (10.1.0.0/16)
├── Primary Firewall (1.1.1.1)
│   └── VIP (1.1.1.100)
├── Secondary Firewall (1.1.1.2)
└── Heartbeat link

Site B (10.2.0.0/16)
└── Tunnel to VIP (1.1.1.100)

Primary FW Configuration:
object network SITE_B
 subnet 10.2.0.0 255.255.0.0

crypto map CMAP 1 ipsec-isakmp
 set peer 2.2.2.2
 set access-list ENCRYPT_TRAFFIC

Failover triggers:
- Heartbeat loss
- Interface down
- Manual failover

Active tunnel uses VIP
Secondary assumes VIP on failover
Site B always connects to same IP
```

### DMVPN (Dynamic Multipoint VPN)

```
Hub-and-Spoke Topology:
         [Hub]
          / \
        /     \
      [S1]   [S2]
       |       |
      V1      V2

Hub Configuration:
! Enable NHRP
interface Tunnel0
 ip address 192.168.1.1 255.255.255.0
 tunnel source 1.1.1.1
 tunnel destination any
 ip nhrp network-id 1
 ip nhrp authentication SECRET

! Enable mGRE (multipoint GRE)
interface Tunnel0
 no ip next-hop-self eigrp 100
 ip nhrp shortcut

Spoke Configuration:
interface Tunnel0
 ip address 192.168.1.2 255.255.255.0
 tunnel source 2.2.2.1
 tunnel destination 1.1.1.1  (hub)
 ip nhrp network-id 1
 ip nhrp nhs 192.168.1.1
 ip nhrp authentication SECRET

Benefits:
- Scalable (many spokes)
- Spoke-to-spoke direct tunnels
- Efficient bandwidth
- Simple hub configuration
```

## Troubleshooting IPsec

### Common Issues

```
Issue 1: Tunnel Won't Come Up

Diagnosis:
show crypto ikev2 sa
show crypto ipsec sa

Causes:
- Wrong peer IP
- Pre-shared key mismatch
- Firewall blocking IKE (500, 4500)
- Firewall blocking ESP (50)
- Encryption algorithm mismatch

Solutions:
1. Verify peer IP is correct
2. Double-check pre-shared key
3. Verify firewall rules allow IKE/ESP
4. Ensure encryption algorithms match
5. Check crypto transform sets
```

### Packet Capture for Debugging

```
Capture IKE packets:
debug crypto ikev2
debug crypto ipsec

This shows:
- IKE negotiation messages
- SA establishment
- Authentication exchange
- Transform set negotiation
- Encryption algorithm selection

Understand output:
IKE_SA_INIT message = Phase 1
IKE_AUTH message = Authentication
CREATE_CHILD_SA = Phase 2 (IPsec)
INFORMATIONAL = Keep-alive/DPD
```

## Security Best Practices

### Encryption Standards

```
Recommended Configuration:
IKEv2 Encryption: AES-256-CBC or AES-256-GCM
IKEv2 Integrity: SHA-384 or SHA-512
IPsec Encryption: AES-256-GCM
IPsec Integrity: SHA-384 or SHA-512
DH Group: Group 15 (3072-bit) or higher
PFS: Enabled (group 15+)

Acceptable (but weaker):
AES-128 (acceptable until 2030)
SHA-256 (acceptable for most uses)
DH Group 14 (2048-bit, slow)

Never Use:
3DES (deprecated)
DES (deprecated)
MD5 (broken)
No encryption (insecure)
DH Group 1 or 2 (weak)
```

### Pre-Shared Key Management

```
Good Practices:
- Use strong random PSK (32+ characters)
- Mix uppercase, lowercase, numbers, special chars
- Store in secure location (encrypted)
- Change PSK annually
- Never email in plaintext
- Document in secure vault
- Different PSK per tunnel

Example Strong PSK:
Th!s1sAStR0ng&C0mpl3xPSK#2024!

Better Alternative:
Use certificates instead of PSK
- More scalable
- Better security
- Easier rotation
- Professional deployments
```

## Monitoring IPsec Tunnels

### Key Metrics

```
Monitor:
- Tunnel status (up/down)
- Packet count (encap/decap)
- Data rates (in/out)
- Rekey events
- Failed authentications
- DPD timeouts

Cisco Commands:
show crypto ikev2 sa
show crypto ipsec sa
show crypto ikev2 sa detailed
show crypto ipsec sa detail

Watch for:
- Tunnel flapping (up/down cycling)
- Asymmetric traffic (encap ≠ decap)
- Failed authentications
- DPD timeout warnings
```

### Alerting Thresholds

```
Tunnel Down: Immediate alert
Failed Authentications > 10/hour: Alert
Traffic Asymmetry: Alert
Rekey Failures: Alert
DPD Timeout: Alert
CPU on firewall > 80%: Alert
Memory on firewall > 80%: Alert
```

## Maintenance Tasks

```
Weekly:
- Verify tunnel status
- Check authentication logs
- Monitor bandwidth

Monthly:
- Full tunnel test
- Performance check
- Review configuration
- Backup configuration

Quarterly:
- Security audit
- PSK/certificate review
- Algorithm review
- Failover test

Annually:
- PSK rotation
- Certificate renewal
- Security assessment
- Configuration review
- Encryption standard upgrade check
```
