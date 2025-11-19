# Network Naming Conventions Standards

## Executive Summary

This document establishes comprehensive naming conventions for network infrastructure, devices, interfaces, and addressing schemes. These standards ensure consistency, scalability, and operational efficiency across enterprise networks while adhering to industry best practices from Cisco, Juniper, and IETF specifications.

**Version**: 1.0
**Last Updated**: 2025-11-19
**Reference Standards**: RFC 952, RFC 1123, Cisco Best Practices, Juniper Design Guidelines

---

## 1. Hostname and Device Naming

### 1.1 General Format

```
[LOCATION][DEVICE-TYPE][FUNCTION][INSTANCE].[DOMAIN]
```

**Pattern Examples**:
- `dfw-core-01.network.internal`
- `nyc-agg-02.network.internal`
- `sfo-access-leaf-03.network.internal`
- `lhr-border-01.network.internal`

### 1.2 Location Codes (IATA Airport Codes)

Recommended approach for multi-site organizations:

| Location | Code | Example |
|----------|------|---------|
| Dallas Fort Worth | DFW | dfw-core-01 |
| New York | NYC | nyc-access-01 |
| San Francisco | SFO | sfo-edge-01 |
| London Heathrow | LHR | lhr-border-01 |
| Tokyo Narita | NRT | nrt-access-01 |
| Singapore Changi | SIN | sin-gateway-01 |

### 1.3 Device Type Classification

| Device Type | Code | Length | Example |
|------------|------|--------|---------|
| Core Switch | CORE | CR | dfw-cr-01 |
| Aggregation | AGG | AG | nyc-ag-02 |
| Access/Edge | ACCESS | AC | sfo-ac-03 |
| Border Router | BORDER | BR | lhr-br-01 |
| Firewall | FW | FW | dfw-fw-01 |
| Load Balancer | LB | LB | nyc-lb-02 |
| Proxy | PRX | PX | sfo-px-01 |
| DNS Server | DNS | DN | dfw-dn-01 |
| Leaf Switch | LEAF | LF | nyc-lf-01 |
| Spine Switch | SPINE | SP | dfw-sp-01 |
| Autonomous System Border Router | ASBR | AR | lhr-ar-01 |

### 1.4 Functional Descriptors

- **IPv4**: ip4 or 4
- **IPv6**: ip6 or 6
- **Redundancy**: HA (High Availability)
- **Disaster Recovery**: DR
- **Backup**: BK
- **Test**: TEST
- **Production**: PROD (optional, use default)

**Examples**:
- `dfw-core-ha-01.network.internal` (Primary core, redundant pair)
- `nyc-firewall-dr-01.network.internal` (Disaster recovery firewall)
- `sfo-access-test-01.network.internal` (Test access switch)

### 1.5 Numbering Convention

**Incremental Numbering**:
- Two-digit format: 01, 02, 03... 99
- Chassis number comes before line card: `dfw-core-01-lc-01` (Chassis 01, Line Card 01)
- Start numbering from 01, not 00
- Pair redundant devices: 01/02, 03/04

**Geographic Distribution**:
- Primary site devices: 01-09
- Secondary site devices: 10-19
- Tertiary site devices: 20-29
- Remote branch devices: 30-99

### 1.6 Character Restrictions

**Compliance Rules**:
- Maximum length: 63 characters
- Characters: alphanumeric (a-z, 0-9) and hyphen (-)
- Must start with letter (RFC 952 compliance)
- Must end with alphanumeric
- No underscores, spaces, or special characters
- Case: lowercase preferred
- No consecutive hyphens

**Validation Pattern**:
```regex
^[a-z][a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$
```

### 1.7 Domain Names

**Structure**:
```
[HOSTNAME].[SUBDOMAIN].[DOMAIN]
```

**Examples**:
- `dfw-core-01.network.internal` (Production network)
- `dfw-core-01.network.corp.example.com` (Corporate routable)
- `dfw-core-01.network.example.com` (External routable)
- `dfw-core-01.mgmt.internal` (Management network)

**Subdomain Recommendations**:
- `network` - Core network infrastructure
- `mgmt` - Management interfaces
- `oob` - Out-of-band management
- `ilo` - ILO/iDRAC interfaces
- `storage` - Storage network
- `wifi` - Wireless controllers

---

## 2. Interface Naming

### 2.1 Cisco Interface Naming

**Standardized Format**: `[TYPE][SLOT]/[MODULE]/[PORT]`

**Interface Types**:

| Interface | Code | Example |
|-----------|------|---------|
| Ethernet | Eth | Eth 1/1/1 |
| Gigabit Ethernet | Gi | Gi 0/0/1 |
| 10 Gigabit Ethernet | Te | Te 1/1/1 |
| 25 Gigabit Ethernet | Twe | Twe 1/1/1 |
| 40 Gigabit Ethernet | Fo | Fo 1/1/1 |
| 100 Gigabit Ethernet | Hun | Hun 1/1/1 |
| Management | Mgmt | Mgmt 0/1 |
| Serial | Se | Se 1/1/1 |
| Port Channel | Po | Po 1, Po 128 |

**Cisco IOS XR Format**:
```
interface HundredGigE0/0/0/0
interface GigabitEthernet0/0/0/1
interface TenGigE0/0/0/2
interface MgmtEth0/0/0/0
```

### 2.2 Juniper Interface Naming

**Standardized Format**: `[INTERFACE-TYPE]-[PORT-NUMBER]`

**Interface Types**:

| Interface | Code | Example |
|-----------|------|---------|
| Ethernet | ge | ge-0/0/0 |
| 10 Gigabit Ethernet | xe | xe-1/0/0 |
| 40 Gigabit Ethernet | et | et-2/0/0 |
| 100 Gigabit Ethernet | et | et-3/0/0 |
| Management | me | me0 |
| Aggregated Ethernet | ae | ae0, ae1 |
| Loopback | lo | lo0 |

**Juniper Format**:
```
ge-0/0/0      (PIC 0, Port 0, Logical Unit 0)
xe-1/1/0      (FPC 1, PIC 1, Port 0)
ae0.100       (Aggregated Ethernet, VLAN 100)
```

### 2.3 Interface Description Standards

**Format**: `[PURPOSE] | [PEER] | [VLAN/CIRCUITS] | [CAPACITY]`

**Cisco Configuration Example**:
```
interface GigabitEthernet0/0/1
 description UPLINK | to-dfw-core-02 | VLAN 10,20,30 | 1Gbps
!
interface GigabitEthernet1/0/0
 description ACCESS-PORT | User-Facing | Data+Voice | 1Gbps
!
interface TenGigE0/0/0/0
 description WAN-LINK | to-nyc-border-01 | MPLS-CORE | 10Gbps
```

**Juniper Configuration Example**:
```
ge-0/0/0 {
    description "UPLINK | to-nyc-core-01 | VLAN 10,20,30 | 1Gbps";
}

et-1/0/0 {
    description "WAN-LINK | to-sfo-border-01 | MPLS-CORE | 100Gbps";
}
```

### 2.4 Subinterface and VLAN Conventions

**Format**: `[BASE-INTERFACE].[VLAN-ID]`

**Examples**:
```
interface GigabitEthernet0/0/1.10
 description VLAN-10 | DATA | Subinterface
 encapsulation dot1Q 10
!
interface GigabitEthernet0/0/1.20
 description VLAN-20 | VOICE | Subinterface
 encapsulation dot1Q 20
!
interface GigabitEthernet0/0/1.100
 description VLAN-100 | MANAGEMENT | Subinterface
 encapsulation dot1Q 100
```

**Juniper Equivalent**:
```
ge-0/0/1 {
    unit 10 {
        description "VLAN-10 | DATA | Subinterface";
        vlan-id 10;
    }
    unit 20 {
        description "VLAN-20 | VOICE | Subinterface";
        vlan-id 20;
    }
}
```

### 2.5 Port Channel / LAG Naming

**Format**: `Po[ID]` (Cisco) or `ae[ID]` (Juniper)

**Numbering**:
- Port channels 1-99: Standard LAG groups
- Port channels 100-199: Inter-switch links (ISL)
- Port channels 200-299: vPC peer links (Cisco)
- Port channels 300-399: Reserved for future use

**Configuration Example**:
```
! Cisco
interface Port-channel 1
 description LAG | to-nrt-access-01 | 4x10Gbps
 mtu 9216
!
! Juniper
ae0 {
    description "LAG | to-nrt-access-01 | 4x10Gbps";
    mtu 9216;
}
```

---

## 3. VLAN Naming and Numbering

### 3.1 VLAN ID Allocation

**Recommended Allocation**:

| VLAN Range | Purpose | Examples |
|-----------|---------|----------|
| 1 | Native VLAN (default) | VLAN0001-NATIVE |
| 2-9 | Reserved for system | VLAN0002-RESERVED |
| 10-99 | Data VLANs | VLAN0010-DATA, VLAN0020-APPS |
| 100-199 | Voice/Video VLANs | VLAN0100-VOICE, VLAN0150-VIDEO |
| 200-299 | Management/OOB | VLAN0200-MGMT, VLAN0250-OOB |
| 300-399 | Guest/Temporary | VLAN0300-GUEST, VLAN0350-TEMP |
| 400-999 | Infrastructure | VLAN0400-NAS, VLAN0500-BACKUP |
| 1000-1499 | Overlay/Tunnel | VLAN1000-VXLAN, VLAN1100-MPLS |
| 1500-2094 | Reserved | (Future use) |
| 2095-4094 | Reserved | (Extended range) |

### 3.2 VLAN Naming Convention

**Format**: `VLAN[ID]-[PURPOSE]-[LOCATION]`

**Naming Examples**:
```
VLAN0010-DATA-PROD          (Data VLAN for production)
VLAN0011-DATA-DEV           (Data VLAN for development)
VLAN0020-APPS-CORP          (Applications VLAN corporate)
VLAN0100-VOICE-DFW          (Voice VLAN Dallas Fort Worth)
VLAN0110-VIDEO-NYC          (Video VLAN New York)
VLAN0200-MGMT-PROD          (Management VLAN production)
VLAN0210-OOB-MGMT           (Out-of-band management)
VLAN0300-GUEST-CORP         (Guest access corporate)
VLAN0310-GUEST-CONTRACTOR   (Guest access contractors)
VLAN0400-STORAGE-SAN        (Storage network SAN)
VLAN0500-BACKUP-DR          (Backup/DR replication)
VLAN0600-WIRELESS-CORP      (Wireless corporate)
VLAN0700-IoT-PROD           (IoT devices production)
VLAN1000-VXLAN-UNDERLAY     (VXLAN underlay fabric)
VLAN1100-MPLS-PE            (MPLS PE interfaces)
```

### 3.3 VLAN Configuration Example

**Cisco Configuration**:
```
vlan 10
 name DATA-PROD
 description Production Data VLAN
!
vlan 100
 name VOICE-DFW
 description Voice VLAN for Dallas Fort Worth site
!
vlan 200
 name MGMT-PROD
 description Production Management VLAN
!
```

**Juniper Configuration**:
```
vlans {
    DATA-PROD {
        vlan-id 10;
        description "Production Data VLAN";
    }
    VOICE-DFW {
        vlan-id 100;
        description "Voice VLAN for Dallas Fort Worth site";
    }
    MGMT-PROD {
        vlan-id 200;
        description "Production Management VLAN";
    }
}
```

---

## 4. IP Addressing Schemes

### 4.1 IPv4 Addressing Strategy

**Supernet Structure**:
```
10.0.0.0/8         Primary enterprise space
├── 10.0.0.0/16    Core network infrastructure
├── 10.1.0.0/16    Dallas Fort Worth site
├── 10.2.0.0/16    New York site
├── 10.3.0.0/16    San Francisco site
├── 10.4.0.0/16    London site
├── 10.5.0.0/16    Tokyo site
└── 10.6.0.0/16    Singapore site
```

### 4.2 Site-Level Addressing

**Dallas Fort Worth (DFW) - 10.1.0.0/16**:
```
10.1.0.0/22      DFW Core Infrastructure (1024 hosts)
├── 10.1.0.0/24  DFW Core Switches
├── 10.1.1.0/24  DFW Aggregation Switches
├── 10.1.2.0/24  DFW Data VLAN
└── 10.1.3.0/24  DFW Voice VLAN

10.1.4.0/22      DFW Management (1024 hosts)
├── 10.1.4.0/24  DFW Device Management
├── 10.1.5.0/24  DFW OOB Management
└── 10.1.6.0/24  DFW iLO/IPMI

10.1.8.0/22      DFW Guest/Wireless (1024 hosts)
├── 10.1.8.0/24  DFW Guest Data
└── 10.1.9.0/24  DFW Guest WiFi

10.1.12.0/22     DFW Applications (1024 hosts)
├── 10.1.12.0/24 DFW App Tier 1
├── 10.1.13.0/24 DFW App Tier 2
└── 10.1.14.0/24 DFW App Tier 3
```

**New York (NYC) - 10.2.0.0/16**:
```
10.2.0.0/22      NYC Core Infrastructure (1024 hosts)
10.2.4.0/22      NYC Management (1024 hosts)
10.2.8.0/22      NYC Guest/Wireless (1024 hosts)
10.2.12.0/22     NYC Applications (1024 hosts)
```

### 4.3 VLAN to Subnet Mapping

**Standard Mapping**:
```
VLAN 10  (DATA-PROD)      → 10.1.2.0/24
VLAN 11  (DATA-DEV)       → 10.1.3.0/24
VLAN 20  (APPS-CORP)      → 10.1.12.0/24
VLAN 100 (VOICE-DFW)      → 10.1.5.0/24
VLAN 200 (MGMT-PROD)      → 10.1.4.0/24
VLAN 210 (OOB-MGMT)       → 10.1.4.0/26 (subset)
VLAN 300 (GUEST-CORP)     → 10.1.8.0/24
VLAN 400 (STORAGE-SAN)    → 10.1.20.0/24
```

### 4.4 Loopback and Management IPs

**Loopback Interface Pattern**:
```
10.0.1.[ID]/32    Router loopback (BGP route reflector, OSPF)
10.0.2.[ID]/32    Switch loopback (switch management)
10.0.3.[ID]/32    Reserved for future use
```

**Examples**:
```
dfw-core-01  → Loopback0: 10.0.1.1/32
dfw-core-02  → Loopback0: 10.0.1.2/32
dfw-agg-01   → Loopback0: 10.0.1.11/32
dfw-agg-02   → Loopback0: 10.0.1.12/32
dfw-access-01 → Loopback0: 10.0.2.1/32
dfw-access-02 → Loopback0: 10.0.2.2/32
```

**Management Interface Pattern**:
```
10.1.4.[DEVICE-ID] for DFW devices
10.2.4.[DEVICE-ID] for NYC devices
```

### 4.5 Point-to-Point Link IPs

**P2P Subnet Strategy** (One /30 per link):
```
10.100.0.0/16    Point-to-point subnets
├── 10.100.0.0/30   DFW-Core-01 to DFW-Core-02
├── 10.100.0.4/30   DFW-Core-01 to DFW-Agg-01
├── 10.100.0.8/30   DFW-Core-01 to NYC-Border-01
├── 10.100.0.12/30  NYC-Border-01 to NYC-Core-01
└── ... (additional P2P links)
```

**Allocation Strategy**:
- First address: .1 (router A)
- Second address: .2 (router B)
- Third address: .3 (reserved)
- Fourth address: .0 (network)

### 4.6 IPv6 Addressing Scheme

**Enterprise IPv6 Allocation**:
```
2001:db8::/32      Enterprise prefix (documentation example)
├── 2001:db8:1::/48  DFW site
├── 2001:db8:2::/48  NYC site
├── 2001:db8:3::/48  SFO site
└── 2001:db8:ff::/48 Management/Loopback
```

**IPv6 Loopback Pattern**:
```
2001:db8:ff::1/128   DFW-Core-01
2001:db8:ff::2/128   DFW-Core-02
2001:db8:ff::11/128  DFW-Agg-01
2001:db8:ff::12/128  DFW-Agg-02
```

**VLAN IPv6 Addressing**:
```
VLAN 10 (DATA)    → 2001:db8:1:10::/64
VLAN 100 (VOICE)  → 2001:db8:1:100::/64
VLAN 200 (MGMT)   → 2001:db8:1:200::/64
```

### 4.7 IP Address Allocation Documentation

**Spreadsheet Template**:
```
Device Name        | Interface   | IPv4 Address   | IPv6 Address        | VLAN | Purpose
dfw-core-01        | Loopback0   | 10.0.1.1/32   | 2001:db8:ff::1/128 | -    | BGP Router-ID
dfw-core-01        | Gi0/0/0     | 10.100.0.1/30 | 2001:db8:ff:100::1 | -    | P2P to DFW-Core-02
dfw-core-01        | Gi0/0/1.10  | 10.1.2.254/24 | 2001:db8:1:10::1   | 10   | DATA VLAN Gateway
dfw-core-01        | Gi0/0/1.20  | 10.1.5.254/24 | 2001:db8:1:20::1   | 20   | VOICE VLAN Gateway
dfw-access-01      | Loopback0   | 10.0.2.1/32   | 2001:db8:ff::101/128| -   | Switch Router-ID
dfw-access-01      | Mgmt0       | 10.1.4.1/24   | 2001:db8:1:200::1  | 200  | Management Access
```

---

## 5. WAN Circuit Naming

### 5.1 WAN Link Naming Convention

**Format**: `[SOURCE-SITE]-[DEST-SITE]-[CIRCUIT-TYPE]-[INSTANCE]`

**Examples**:
```
DFW-NYC-MPLS-01     (DFW to NYC MPLS circuit 1)
DFW-NYC-MPLS-02     (DFW to NYC MPLS circuit 2 - redundant)
DFW-SFO-INTERNET-01 (DFW to SFO Internet uplink)
NYC-LHR-DIA-01      (NYC to London dedicated internet)
SFO-SIN-MPLS-01     (SFO to Singapore MPLS)
```

### 5.2 Circuit Documentation

**Template**:
```
Circuit ID: DFW-NYC-MPLS-01
Source: dfw-border-01 GigabitEthernet0/0/2
Destination: nyc-border-01 GigabitEthernet0/0/1
Bandwidth: 100 Mbps
Protocol: MPLS
VLAN: 100 (WAN traffic)
QoS Class: Premium
Backup Circuit: DFW-NYC-MPLS-02
Service Level: 99.9% availability
Vendor: AT&T
SLA: 50ms latency, 0.1% packet loss max
```

---

## 6. Validation and Compliance

### 6.1 Naming Convention Checklist

- [ ] Hostnames are RFC 952 compliant
- [ ] All names are lowercase alphanumeric
- [ ] Location codes are consistent across documentation
- [ ] Device types match approved codes
- [ ] Sequential numbering without gaps
- [ ] Interface descriptions follow standard format
- [ ] VLAN IDs match allocation ranges
- [ ] IP addresses documented in IPAM system
- [ ] No duplicate hostnames/IP addresses
- [ ] All entries in DNS and CMDB

### 6.2 Automated Validation

**Regex Pattern for Hostname**:
```regex
^[a-z]{3}-[a-z]+(-[a-z0-9]+)?-\d{2}(-[a-z0-9]+)?(\.network\.internal)?$
```

**Validation Script (Pseudo-code)**:
```python
import re

HOSTNAME_PATTERN = r'^[a-z][a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'
VALID_LOCATIONS = ['dfw', 'nyc', 'sfo', 'lhr', 'nrt', 'sin']
VALID_DEVICE_TYPES = ['core', 'agg', 'access', 'border', 'fw', 'lb']

def validate_hostname(hostname):
    if not re.match(HOSTNAME_PATTERN, hostname.lower()):
        return False, "Invalid character set or format"

    location = hostname.split('-')[0]
    if location not in VALID_LOCATIONS:
        return False, f"Unknown location: {location}"

    return True, "Hostname valid"
```

---

## 7. References and Standards

- **RFC 952**: Hostname Syntax and Semantics
- **RFC 1123**: Host Requirements - Application and Support
- **RFC 3986**: Uniform Resource Identifier (URI) Generic Syntax
- **Cisco Best Practices**: Naming, Planning, and Design
- **Juniper Networks Design Guidelines**: Device and Interface Naming
- **IANA IPv4 Special Address Registry**: Private Address Space (RFC 1918)
- **IANA IPv6 Global Unicast Address Assignments**

---

## 8. Change Management

All changes to naming conventions must:
1. Be documented in version control
2. Include rationale and impact analysis
3. Be communicated to infrastructure team
4. Follow change management procedures
5. Include automatic validation rules
6. Update all supporting documentation (DNS, CMDB, IPAM)

**Last Revision**: 2025-11-19
**Next Review**: 2026-05-19
**Owner**: Network Infrastructure Team
