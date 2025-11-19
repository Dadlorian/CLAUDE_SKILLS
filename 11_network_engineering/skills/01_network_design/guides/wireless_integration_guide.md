# Wireless Integration Guide

## Introduction
This guide covers integrating wireless networks into campus designs for seamless user experience and network efficiency.

## Wireless Architecture

### Controller vs Autonomous

```
Autonomous Access Points (Legacy):
  Each AP independent
  Configuration: Individual AP management
  Roaming: Limited (clients must re-authenticate)
  Scalability: Poor (manual management per AP)
  Cost: Low per AP ($500-1000), but high operational cost
  Deployment: Small networks only (< 10 APs)

Controlled Access Points (Modern):
  Centralized controller
  Configuration: Single pane of glass
  Roaming: Seamless (controller manages)
  Scalability: Excellent (controller handles all)
  Cost: Higher per AP ($800-1500), lower operational cost
  Deployment: Enterprise standard (supports 100+ APs)
  Recommended: Always use controlled (better user experience)
```

### Wireless Network Topology

```
Campus wireless design:

            ┌─────────────────────────────┐
            │  Wireless Controller        │
            │  (Central management)       │
            │  Location: DC or HQ         │
            └─────────────────────────────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
      Building A Building B Building C
         │          │          │
    ┌────┴────┐ ┌──┴───┐  ┌───┴──┐
    │ AP-A1   │ │AP-B1 │  │AP-C1 │
    │ AP-A2   │ │AP-B2 │  │AP-C2 │
    │ AP-A3   │ │AP-B3 │  │AP-C3 │
    └─────────┘ └──────┘  └──────┘

Coverage:
  - Each AP: ~100 meters (open space)
  - ~20-30 users per AP (depends on data rates)
  - Overlap: 20% for roaming

AP placement rules:
  - One per 1,500-2,000 sq meters
  - Mounted centrally on ceiling
  - Avoid corners and enclosed spaces
  - Clearance from obstacles (2m minimum)
  - PoE injection: Via switch or injector
```

## Wireless VLAN Design

### VLAN Allocation for WiFi

```
Multiple wireless networks:

SSID-Corporate (WPA2-Enterprise)
  VLAN: 30 (Corporate users)
  Subnet: 10.0.30.0/24 (same as wired)
  Authentication: 802.1X (Active Directory)
  Encryption: WPA2-AES (corporate standard)
  Users: Employees

SSID-Contractor (WPA2-PSK)
  VLAN: 31 (Contractors/Partners)
  Subnet: 10.0.31.0/24 (isolated)
  Authentication: Pre-shared key
  Encryption: WPA2-AES
  Users: Approved contractors

SSID-Guest (Open/Captive Portal)
  VLAN: 100 (Guest WiFi)
  Subnet: 10.0.100.0/24 (internet only)
  Authentication: Captive portal
  Encryption: WPA2 (optional, open acceptable)
  Users: Visitors, guests

SSID-IoT (PSK or Open)
  VLAN: 40 (IoT devices)
  Subnet: 10.0.40.0/24 (isolated from users)
  Authentication: None or PSK
  Encryption: WPA2
  Users: Smart devices, cameras, sensors
```

### Wireless Backhaul

```
AP connection to wired network:

Scenario 1: Wired backhaul (preferred)
  Connection: Ethernet cable from AP to switch
  Benefits: Consistent bandwidth, low latency, high throughput
  Bandwidth: Full interface speed available (100 Mbps to 1 Gbps)
  Cost: Cable run to each AP
  Typical: 10-25 Mbps per client achieved

Scenario 2: Wireless backhaul (mesh)
  Connection: Wireless link between APs
  Benefits: No cable required, flexible placement
  Bandwidth: Half used for backhaul (AP A ↔ AP B)
  Limitation: Cascading APs reduce bandwidth
  Typical: 3-8 Mbps per client (halved per hop)

Recommendation: Wired backhaul when possible
  Cost of cabling < Cost of poor user experience
  Easier troubleshooting (wired is separate from wireless)
  Better performance (not competing for air time)
```

## User Authentication

### Authentication Methods

```
Enterprise authentication (802.1X):

User connects to SSID-Corporate
System: User prompted for username/password
Process:
  1. User enters credentials
  2. AP forwards to RADIUS server (usually in AD)
  3. RADIUS validates credentials
  4. RADIUS returns: Accept or Reject
  5. AP grants access (if accept) on corporate VLAN 30
  6. User obtains IP via DHCP on VLAN 30

Benefits:
  - Per-user authentication (not shared key)
  - Automatic VLAN assignment (based on AD group)
  - Encryption key unique per user
  - Audit trail (who logged in, when)

Configuration (Cisco AP):
  ssid SSID-Corporate
    security wpa version 2
    security wpa cipher ccmp
    security wpa psk set-key wpa2 <random> (not used if 802.1X)
    security dot1x system-auth-control
```

### Guest Authentication

```
Captive portal method:

Guest connects to SSID-Guest
System: HTTP redirect to login portal
Process:
  1. Guest opens browser
  2. Any HTTP request redirected to portal
  3. Guest sees login/terms page
  4. Guest enters email address
  5. Portal validates email (if required)
  6. Portal grants access (device MAC added to allow list)
  7. Network access enabled
  8. Browser can now access internet

Configuration:
  Captive Portal Server: Runs on network
  Portal Page: Hosted on internal web server
  Access control: MAC filtering (allow authenticated MACs)
  Bandwidth limit: Per-client (25 Mbps typical)
  Session timeout: 8 hours typical

Features:
  - Terms of Service display
  - Email collection (for marketing)
  - Time-limited access (expire after date)
  - Bandwidth throttling
  - Threat detection (block if infected)
```

## Performance Optimization

### Bandwidth and QoS

```
Wireless bandwidth sharing:

AP 1: 100 clients active
  802.11ac: 1.3 Gbps theoretical max
  Actual (80%): 1.0 Gbps
  Per client: 1.0 Gbps / 100 = 10 Mbps average
  Peak: Some clients 50+ Mbps, others 1 Mbps

QoS configuration:

Video streaming (high priority):
  Traffic class: Video
  Reserved: 25% of bandwidth per AP
  Per AP: 250 Mbps reserved for video
  Benefit: Streaming doesn't stutter

VoIP (high priority):
  Traffic class: Voice
  Reserved: 10% of bandwidth per AP
  Per AP: 100 Mbps reserved for voice
  Benefit: Call quality maintained

Web browsing (medium priority):
  Traffic class: Best-effort
  Guaranteed: 1% minimum (starvation prevention)
  Per AP: 10 Mbps minimum
  Benefit: Always responsive

Remaining: Shared (35% available)
  Downloads, email, messaging
  Use available capacity
  Backoff when priority traffic arrives

Implementation (Cisco):
  policy-map Wireless-QoS
    class Video
      priority percent 25
    class Voice
      priority percent 10
    class Best-Effort
      bandwidth percent 35
    class Default
      bandwidth percent 30
```

### Channel Planning

```
802.11 channels:

2.4 GHz band (only 3 non-overlapping):
  Channel 1: 2.412 GHz (overlap with 1-6)
  Channel 6: 2.437 GHz (overlap with 1-6 and 6-11)
  Channel 11: 2.462 GHz (overlap with 6-11)
  Recommendation: Use 1, 6, 11 for non-overlapping

5 GHz band (many non-overlapping):
  Channels 36-48: 5.1-5.3 GHz (12 non-overlapping)
  Channels 52-144: 5.3-5.6 GHz (many non-overlapping)
  Advantage: Many channels available
  Recommendation: Use 5 GHz when possible (less congestion)

Channel selection:

Small campus (< 10 APs):
  2.4 GHz: Channel 1, 6, 11 (rotate through APs)
  5 GHz: Channels 36, 40, 44, 48 (separate, non-overlapping)

Large campus (> 10 APs):
  2.4 GHz: Minimize usage (only legacy clients)
  5 GHz: Primary band
  6 GHz: Future (Wi-Fi 6E capable APs)
  Strategy: Use different channels per AP (avoid overlaps)

Implementation:
  Automated: Controller detects interference, adjusts channels
  Manual: Plan channels before deployment
  Monitoring: Monthly review for changes in interference
```

## Roaming and Mobility

### Fast Roaming (802.11r)

```
Problem: User walks between APs, connection drops

Traditional:
  User moves AP range: Old AP → New AP
  Duration: 1-2 seconds
  Effect: VoIP call drops, video pauses

Solution: 802.11r Fast Roaming
  Controller: Caches credentials and keys
  Reassociation: Instant (no authentication needed)
  Duration: < 250 ms
  Effect: Seamless (user doesn't notice)

Requirement:
  - All APs in coverage area must have 802.11r
  - Client device must support 802.11r
  - Controller must handle pre-key handoff

Configuration:
  AP config:
    dot11-11r enable
    mobility-domain 12345
```

### Roaming Mesh

```
Non-wired AP scenario (less typical):

Main AP (wired backhaul):
  - Wired connection to switch
  - Bridge VLAN 30 to wireless

Mesh AP 1 (wireless backhaul):
  - Wireless connection to Main AP
  - Bridges VLAN 30 over air
  - Provides coverage for clients

Mesh AP 2 (wireless backhaul):
  - Wireless connection to Mesh AP 1
  - Extends coverage further
  - Throughput: Halved per hop (cascading)

Performance:
  Main AP: 1 Gbps wired = 500 Mbps wireless (backhaul) + client
  Mesh AP 1: 250 Mbps available (half of 500 Mbps)
  Mesh AP 2: 125 Mbps available (half of 250 Mbps)

Recommendation: Limit mesh to 2 hops maximum
  Beyond 2 hops: Throughput too low
  Invest in wired backhaul (better ROI)
```

## Security Considerations

### Encryption Standards

```
WPA2 (current standard):
  - CCMP (AES-based encryption)
  - 128-bit key (minimum)
  - 256-bit key (preferred)
  - Mandatory for corporate

WPA3 (next generation):
  - CCMP-256 or GCMP-256 (stronger encryption)
  - Simultaneous Authentication of Equals (SAE)
  - Protection against key recovery attacks
  - Individualized Data Encryption (OWE for open)
  - Status: Emerging (some APs support)

Legacy (DO NOT USE):
  - WEP: Deprecated (broken encryption)
  - WPA (original): Weak (TKIP vulnerable)
  - None/Open: Only for guest with captive portal

Recommendation:
  Corporate: WPA2-Enterprise with 256-bit encryption
  Guest: WPA2-Personal or Open + Captive Portal
  Migrate: WPA3 as devices support becomes available
```

### Guest Network Protection

```
Guest isolation:

Requirement: Guests cannot access internal resources

Configuration:

AP settings:
  AP Isolation: Enabled (clients can't see each other)
  Guest VLAN: 100 (isolated from corporate)
  Access control: Block all internal IPs

Firewall rules:
  Guest VLAN → Corporate VLAN: BLOCKED
  Guest VLAN → Internal servers: BLOCKED
  Guest VLAN → Internet: ALLOWED
  All → Guest VLAN: BLOCKED (return traffic only)

Threat detection:
  Malware: Monitor outbound from guest (unusual traffic patterns)
  DDoS: Limit outbound bandwidth
  Botnet: Block known C&C servers
  Credential theft: DNS sinkholing

Benefit: Guests can use network without compromising security
```

## Implementation Checklist

```
Pre-deployment:

[ ] Site survey conducted (coverage maps)
[ ] AP count and placement determined
[ ] Power availability verified (PoE budget)
[ ] VLAN allocation planned
[ ] SSID list finalized
[ ] Authentication method selected
[ ] Security policy defined

Deployment:

[ ] Controller installed (central location)
[ ] APs installed per site survey
[ ] Cables run from switch to AP (PoE injected)
[ ] Controller configured (SSIDs, VLANs, security)
[ ] APs associated to controller
[ ] RF optimization configured (auto channel/power)
[ ] Authentication validated (test logins)

Testing:

[ ] Coverage verified (signal strength mapping)
[ ] Performance tested (throughput, latency)
[ ] Roaming tested (move between APs)
[ ] Failover tested (AP failure recovery)
[ ] Guest access tested (isolated properly)
[ ] Security verified (no internal access from guest)

Production:

[ ] User documentation distributed
[ ] Help desk trained
[ ] Monitoring enabled
[ ] Monthly reviews scheduled
[ ] Annual security audit planned
```

---

**Guide Version:** 1.0
**Last Updated:** November 2025
**Experience Level:** Intermediate to Advanced
**Standards:** IEEE 802.11, WPA2/WPA3, 802.1X
