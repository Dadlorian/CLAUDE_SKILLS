# IP Addressing Schemes

## Introduction
Effective IP address planning is critical for network scalability, manageability, and future growth. This reference covers IPv4 and IPv6 addressing strategies.

## RFC 1918 Private Address Space

### Allocation Options
```
Class A: 10.0.0.0/8 (10.0.0.0 - 10.255.255.255)
  - Available hosts per network: 16,777,214
  - Best for: Large enterprises, multi-region networks

Class B: 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
  - Available hosts per network: 1,048,574
  - Best for: Medium enterprises, multiple sites

Class C: 192.168.0.0/16 (192.168.0.0 - 192.168.255.255)
  - Available hosts per network: 65,534
  - Best for: Small networks, branch offices, test labs
```

## Hierarchical IP Addressing Design

### Enterprise-Wide Addressing (Class A Example)

```
10.0.0.0/8 - Enterprise Network Space
├─ 10.0.0.0/9   - Data Center Region 1
│  ├─ 10.0.0.0/10   - DC1 Pod A
│  │  ├─ 10.0.0.0/16   - DC1-Pod-A Prod
│  │  ├─ 10.64.0.0/16  - DC1-Pod-A Test
│  │  └─ 10.128.0.0/16 - DC1-Pod-A Dev
│  └─ 10.64.0.0/10    - DC1 Pod B
│
├─ 10.128.0.0/9  - Data Center Region 2
│  ├─ 10.128.0.0/10  - DC2 Pod A
│  └─ 10.192.0.0/10  - DC2 Pod B
│
└─ 172.16.0.0/12 - Campus Network
   ├─ 172.16.0.0/13   - Building A
   ├─ 172.24.0.0/13   - Building B
   └─ 172.32.0.0/13   - Building C
```

### Campus Network Subnetting (24-bit Example)

```
10.10.0.0/16 - Campus Network

Department Allocation:
├─ 10.10.1.0/24  - Executive (251 hosts)
├─ 10.10.2.0/24  - Finance (251 hosts)
├─ 10.10.3.0/24  - Engineering (251 hosts)
├─ 10.10.4.0/24  - Sales (251 hosts)
├─ 10.10.5.0/24  - Operations (251 hosts)
├─ 10.10.6.0/24  - Guest/Contractor (251 hosts)
├─ 10.10.7.0/24  - WiFi VLAN (251 hosts)
├─ 10.10.8.0/24  - VoIP (251 hosts)
└─ 10.10.9.0/24  - IoT/Sensors (251 hosts)

Usable host range 10.10.1.0/24:
- Network address: 10.10.1.0
- First usable: 10.10.1.1
- Last usable: 10.10.1.254
- Broadcast: 10.10.1.255
```

## Data Center IP Addressing

### Pod-Based Design (Spine-Leaf)

```
10.0.0.0/8 - Data Center Network

Pod 1 (Servers):     10.0.0.0/17 (10.0.0.1 - 10.0.127.254)
Pod 2 (Servers):     10.0.128.0/17 (10.0.128.1 - 10.0.255.254)
Pod 3 (Servers):     10.1.0.0/17 (10.1.0.1 - 10.1.127.254)
Pod 4 (Servers):     10.1.128.0/17 (10.1.128.1 - 10.1.255.254)
...

Leaf Switch Loopback: 10.255.0.0/16 (one /32 per leaf)
  - Leaf-01: 10.255.0.1/32
  - Leaf-02: 10.255.0.2/32
  - Leaf-03: 10.255.0.3/32

Spine Switch Loopback: 10.255.1.0/16 (one /32 per spine)
  - Spine-01: 10.255.1.1/32
  - Spine-02: 10.255.1.2/32
  - Spine-03: 10.255.1.3/32

Management Network: 10.255.2.0/24
  - Gateway: 10.255.2.1
  - IPMI range: 10.255.2.100-10.255.2.200
```

### Container Network Addressing

```
Docker/Kubernetes Pod Networks: 10.2.0.0/16
Node-1 Pod Range: 10.2.0.0/24
  - Pod IP pool: 10.2.0.2 - 10.2.0.254

Node-2 Pod Range: 10.2.1.0/24
  - Pod IP pool: 10.2.1.2 - 10.2.1.254

Node-3 Pod Range: 10.2.2.0/24
  - Pod IP pool: 10.2.2.2 - 10.2.2.254

Service Network (ClusterIP): 10.3.0.0/16
  - Services: 10.3.0.0 - 10.3.255.255
  - Maximum services: 65,536
```

## WAN IP Addressing

### Multi-Site Network Design

```
10.0.0.0/10 - Corporate Network

Site 1 (HQ):          10.0.0.0/16
  - Campus LAN: 10.0.0.0/17
  - Data Center: 10.0.128.0/17

Site 2 (Regional):    10.4.0.0/16
  - Campus LAN: 10.4.0.0/17
  - Data Center: 10.4.128.0/17

Site 3 (Branch):      10.8.0.0/16
  - Campus LAN: 10.8.0.0/24

Site 4 (Branch):      10.9.0.0/16
  - Campus LAN: 10.9.0.0/24

WAN Interconnect:     10.32.0.0/14 (Reserved for point-to-point links)
  - MPLS backbone: 10.32.0.0/15
  - SD-WAN overlay: 10.34.0.0/15
```

## IPv6 Addressing Strategy

### Global Unicast Address Format

```
2001:db8::/32 - Organization Global Unicast Prefix (Documentation)

Structure: 2001:db8:XXXX:YYYY::
  - 2001:db8 (48 bits): Global prefix
  - XXXX (16 bits): Subnet ID
  - YYYY (16 bits): Interface ID
```

### IPv6 Campus Subnetting

```
2001:db8:0::/48 - Campus Network (65,536 /64 subnets available)

Building-A:        2001:db8:0:1::/64
Building-B:        2001:db8:0:2::/64
Building-C:        2001:db8:0:3::/64
WiFi VLAN:         2001:db8:0:4::/64
Voice VLAN:        2001:db8:0:5::/64
IoT VLAN:          2001:db8:0:6::/64
Guest VLAN:        2001:db8:0:7::/64
Management:        2001:db8:0:8::/64

Example address in Building-A:
  2001:db8:0:1::1 (Gateway)
  2001:db8:0:1::1000 (Host)
```

## IP Address Calculation Examples

### Subnetting with /25 (Class C with Class B consideration)

```
Network: 192.168.1.0/25

Available addresses: 2^(32-25) = 128 addresses
  - Network address: 192.168.1.0
  - Broadcast: 192.168.1.127
  - Usable hosts: 126
  - Usable range: 192.168.1.1 - 192.168.1.126

Second subnet: 192.168.1.128/25
  - Network address: 192.168.1.128
  - Broadcast: 192.168.1.255
  - Usable hosts: 126
  - Usable range: 192.168.1.129 - 192.168.1.254
```

### VLSM Design for Mixed Requirements

```
10.0.0.0/16 - Main network

Department Network (256 hosts): 10.0.0.0/23
  - Usable: 10.0.0.1 - 10.0.1.254

Server Network (64 hosts): 10.0.2.0/25
  - Usable: 10.0.2.1 - 10.0.2.62

WAN Links (/31): 10.0.3.0/31
  - Router 1: 10.0.3.0
  - Router 2: 10.0.3.1
  - No waste, perfect for point-to-point

IoT Network (16 hosts): 10.0.3.2/28
  - Usable: 10.0.3.3 - 10.0.3.14
```

## RFC 3021: /31 Point-to-Point Links

### Motivation
Traditional /30 networks waste 50% of addresses (2 usable from 4 total).

### Modern Approach
```
/31 networks for point-to-point links (RFC 3021)
- 2 addresses total
- 2 usable addresses (no broadcast)
- Zero waste
- 50% address savings

WAN link example:
  10.255.0.0/31 - Link to Site-1
    Router A: 10.255.0.0
    Router B: 10.255.0.1

  10.255.0.2/31 - Link to Site-2
    Router A: 10.255.0.2
    Router B: 10.255.0.3
```

## IPv6 Link-Local Addressing

### Automatic Configuration
```
fe80::/10 - Link-local prefix (automatic)
  - Each interface generates: fe80::1 through fe80::ffff:ffff:ffff:ffff
  - Unique on link only (not routed)
  - Used for neighbor discovery, router advertisements
  - Automatic EUI-64 generation from MAC address

Example generation:
  MAC: 00:50:F2:00:00:01
  EUI-64: 0050:F2FF:FE00:0001
  Link-local: fe80::250:F2FF:FE00:1
```

## Special-Use Address Blocks

| Prefix | Purpose | Usable | Example |
|--------|---------|--------|---------|
| 10.0.0.0/8 | Private (RFC 1918) | Yes | 10.1.2.3 |
| 172.16.0.0/12 | Private (RFC 1918) | Yes | 172.20.1.1 |
| 192.168.0.0/16 | Private (RFC 1918) | Yes | 192.168.100.1 |
| 127.0.0.0/8 | Loopback | No | 127.0.0.1 |
| 169.254.0.0/16 | Link-Local | Limited | 169.254.1.1 |
| 224.0.0.0/4 | Multicast | Special | 224.0.0.1 |
| 255.255.255.255/32 | Broadcast | No | (limited use) |

---

**Reference Version:** 1.0
**Last Updated:** November 2025
**Standards:** RFC 1918, RFC 3021, RFC 3986
