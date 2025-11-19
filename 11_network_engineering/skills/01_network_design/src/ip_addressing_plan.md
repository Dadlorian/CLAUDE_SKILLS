# IP Addressing Plan - Tabular Format

## Enterprise-Wide IP Allocation

| Region | Building | VLAN | Name | Subnet | Gateway | Hosts | Current Use | Owner | Growth |
|--------|----------|------|------|--------|---------|-------|------------|-------|--------|
| East | HQ-A | 10 | Executive | 10.0.10.0/24 | 10.0.10.1 | 254 | 45 (18%) | CFO | +10%/yr |
| East | HQ-A | 20 | Finance | 10.0.20.0/24 | 10.0.20.1 | 254 | 95 (37%) | Controller | +20%/yr |
| East | HQ-A | 30 | Engineering | 10.0.30.0/24 | 10.0.30.1 | 254 | 120 (47%) | CTO | +15%/yr |
| East | HQ-A | 40 | Operations | 10.0.40.0/24 | 10.0.40.1 | 254 | 60 (24%) | VP Ops | +5%/yr |
| East | HQ-A | 50 | Sales | 10.0.50.0/24 | 10.0.50.1 | 254 | 75 (30%) | VP Sales | +10%/yr |
| East | HQ-A | 100 | Guest | 10.0.100.0/24 | 10.0.100.1 | 254 | 20 (8%) | IT Manager | Static |
| East | HQ-A | 110 | Voice | 10.0.110.0/24 | 10.0.110.1 | 254 | 85 (33%) | PBX Admin | +5%/yr |
| East | HQ-A | 120 | Printers | 10.0.120.0/24 | 10.0.120.1 | 254 | 25 (10%) | IT Manager | +10%/yr |
| East | HQ-A | 200 | Management | 10.0.200.0/24 | 10.0.200.1 | 254 | 50 (20%) | Network Team | Static |
| West | HQ-B | 10 | Executive | 10.16.10.0/24 | 10.16.10.1 | 254 | 30 (12%) | CFO | +10%/yr |
| West | HQ-B | 20 | Finance | 10.16.20.0/24 | 10.16.20.1 | 254 | 60 (24%) | Controller | +20%/yr |

## Point-to-Point WAN Links (/31)

| Link | From Router | To Router | Subnet | Notes |
|------|------------|-----------|--------|-------|
| 1 | Core-1 | Core-2 | 10.254.0.0/31 | Core interconnect, 100G |
| 2 | Core-1 | Distribution-A | 10.254.1.0/31 | Distribution uplink |
| 3 | Core-1 | Distribution-B | 10.254.2.0/31 | Distribution uplink |
| 4 | Core-1 | WAN-Router | 10.254.3.0/31 | WAN edge |
| 5 | WAN-Router | ISP-A | 10.254.4.0/31 | Internet primary |
| 6 | WAN-Router | ISP-B | 10.254.5.0/31 | Internet backup |

## Device Loopback Addressing

| Device | Loopback IP | ASN | Purpose |
|--------|-------------|-----|---------|
| Core-1 | 10.255.3.1/32 | 65001 | BGP Router ID |
| Core-2 | 10.255.3.2/32 | 65001 | BGP Router ID |
| Distribution-A | 10.255.2.1/32 | 65001 | BGP Router ID |
| Distribution-B | 10.255.2.2/32 | 65001 | BGP Router ID |
| Spine-01 | 10.255.0.1/32 | 65000 | BGP Router ID |
| Leaf-01 | 10.255.1.1/32 | 65100 | BGP Router ID |

## Data Center Subnets

| Pod | VLAN | Subnet | Gateway | Servers | Tenant |
|-----|------|--------|---------|---------|--------|
| Pod-1 | 1000 | 10.128.0.0/20 | 10.128.0.1 | 32 | Customer-A |
| Pod-1 | 1010 | 10.128.16.0/20 | 10.128.16.1 | 32 | Customer-B |
| Pod-2 | 1100 | 10.128.32.0/20 | 10.128.32.1 | 32 | Customer-C |
| Pod-3 | 1200 | 10.128.48.0/20 | 10.128.48.1 | 32 | Shared Services |

## Summary

**Total Allocated:** 10.0.0.0/8 (16.7M addresses)
**Currently Used:** ~2.5M addresses (15%)
**Available:** ~14.2M addresses (85%)
**Growth Capacity:** 5-10 years before expansion needed

---

**Last Updated:** November 2025
**Review Date:** Q1 2026
