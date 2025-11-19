# Network Diagram Template

## Campus Network Topology - Building A (HQ)

```
                              ╔═════════════════════════════╗
                              ║   CORE SWITCHES (2x)        ║
                              ║   Catalyst 9500             ║
                              ║   10.255.3.1 / .2           ║
                              ╚════════════════╤═════════════╝
                                               │ 100G
                                    ┌──────────┴──────────┐
                                    │                     │
                    ╔═══════════════════╗    ╔═════════════════════╗
                    ║  Distribution-A   ║    ║  Distribution-B     ║
                    ║  Catalyst 9500    ║    ║  Catalyst 9500      ║
                    ║  10.0.10.2 (Exec) ║    ║  10.0.10.3 (Exec)   ║
                    ║  10.0.20.2 (Fin)  ║    ║  10.0.20.3 (Fin)    ║
                    ╚═══════════════════╝    ╚═════════════════════╝
                         │ │                      │ │
            ┌────────────┐ ┗━━━────┐  ┌───────────┘ └────────────┐
            │                      │  │                          │
       ╔════▼════╗            ╔════▼══▼═══╗                     │
       ║Access-  ║            ║Access-     ║                     │
       ║A1: 1-24 ║            ║A2: 1-24    ║                     │
       ║ports    ║            ║ports       ║                     │
       ║VLAN 20  ║            ║VLAN 20     ║                     │
       ║(Finance)║            ║(Finance)   ║                     │
       ╚════┬────╝            ╚════┬───────╝                     │
            │                      │                            │
            │ 25G × 48            │ 25G × 48                   │
            │ (1,200 Gbps down)   │ (1,200 Gbps down)          │
            │                      │                            │
       ┌────┴────────┬─────────────┴───┐                        │
       │             │                 │                        │
  Desktop        Desktop           Desktop                  [More Access]
  PC-001         PC-002            PC-003

Fiber Backbone:
    Building A ════════════ Building B ════════════ Building C
    (HQ Core)             (Regional)                 (Branch)

    Access-A1 → Po1 (4×10G) → Distribution-A → 100G → Core-1
                                                        │
    Access-A2 → Po1 (4×10G) → Distribution-B → 100G → Core-2

VLAN Distribution:

    Distribution Layer (L3 Routing)
    ├─ VLAN 10 (Executive, 10.0.10.0/24)
    ├─ VLAN 20 (Finance, 10.0.20.0/24)
    ├─ VLAN 30 (Engineering, 10.0.30.0/24)
    ├─ VLAN 40 (Operations, 10.0.40.0/24)
    ├─ VLAN 50 (Sales, 10.0.50.0/24)
    ├─ VLAN 100 (Guest, 10.0.100.0/24)
    ├─ VLAN 110 (Voice, 10.0.110.0/24)
    └─ VLAN 120 (Printers, 10.0.120.0/24)

    Access Layer (L2 Switching)
    ├─ VLAN 20 ports: 1-24 (Finance)
    ├─ VLAN 110 ports: 25-30 (IP Phones)
    ├─ VLAN 120 ports: 31 (Printers)
    └─ VLAN 100 ports: 32 (WiFi AP)

PoE Devices:
    - IP Phones: 85 devices, 10W each
    - WiFi APs: 8 devices, 30W each
    - Total PoE load: 1,090W per switch
    - Available budget: 885W (9200L limit)
    - STATUS: Requires external PoE injectors

Gateway Redundancy (HSRP):

    VLAN 10 (Executive):
        Virtual Gateway: 10.0.10.1
        Active (Dist-A): 10.0.10.2, Priority 150
        Standby (Dist-B): 10.0.10.3, Priority 100
        Failover: <10 seconds

    VLAN 20 (Finance):
        Virtual Gateway: 10.0.20.1
        Active (Dist-A): 10.0.20.2, Priority 150
        Standby (Dist-B): 10.0.20.3, Priority 100
        Failover: <10 seconds

Performance Characteristics:

    Latency (same VLAN): <1ms (L2 switching)
    Latency (cross-VLAN): <3ms (L3 routing)
    Bandwidth per user: 1 Gbps (theoretical)
    Actual throughput: 100-300 Mbps (shared)
    Uplink oversubscription: 120:1 (48 ports × 1G ÷ 4×10G)

Redundancy:

    Link Failure:
    - Access → Distribution: Dual uplinks via EtherChannel
    - Distribution → Core: Dual links via BGP
    - Failover time: <50ms (hardware detection)

    Device Failure:
    - Distribution-A down: Dist-B takes over (HSRP)
    - Distribution-B down: Dist-A provides service
    - Core-1 down: Core-2 handles all traffic (ECMP)
    - Availability target: 99.99%

Diagram Key:

╔════════╗ = Core/Backbone device
╠════════╣ = Router/L3 device
╠════════╣ = Switch/L2 device
│        │ = Connection (speed/medium)
└────────┘ = End device or grouping

Colors (if available):
    Green = Access Layer
    Blue = Distribution Layer
    Red = Core Layer
    Yellow = WAN connections
    Purple = Management
```

---

## Diagram Notes

1. **Physical Layout:**
   - All switches mounted in Building A central wiring closet
   - Fiber runs to Building B and C via underground conduit
   - Access switches distributed across 3 floors

2. **Bandwidth Calculation:**
   - Each access switch: 48 × 1G = 48 Gbps downlink
   - Total per building: 8 × 48 Gbps = 384 Gbps aggregate
   - Uplink capacity: 4 × 10G = 40 Gbps per access switch
   - Oversubscription: 48:40 = 1.2:1 (acceptable)

3. **Future Expansion:**
   - PoE: Current limit reached, need external injectors
   - Ports: 50% utilized, can add 50+ devices
   - Uplink: 40 Gbps available, growing to 50 Mbps per user
   - Timeline: Upgrade uplinks in 2 years to 10x10G

4. **Security Considerations:**
   - Guest VLAN isolated from internal (firewall enforced)
   - Management VLAN restricted to IT staff only
   - Finance VLAN encrypted traffic, compliance required
   - All inter-VLAN routed via distribution (policy enforced)

5. **Management Access:**
   - Distribution-A: SSH (22) access from 10.255.200.0/24
   - Distribution-B: SSH (22) access from 10.255.200.0/24
   - Switch username/password: AD authentication
   - All changes logged to central syslog server

---

**Created:** November 2025
**Diagram Type:** Logical Topology + Traffic Flow
**Last Updated:** November 2025
**Next Review:** Q1 2026
