# Network Troubleshooting Runbooks

## Executive Summary

This document provides systematic troubleshooting procedures using the OSI model approach, diagnostic methodologies, and common network scenario resolutions. These runbooks enable network engineers to efficiently diagnose and resolve issues at each network layer.

**Version**: 1.0
**Last Updated**: 2025-11-19
**Reference Standards**: OSI Model (ISO 7498), IEEE 802.3, RFC 1918

---

## 1. OSI Layer Troubleshooting Framework

### 1.1 Layer-by-Layer Approach

```
OSI LAYER TROUBLESHOOTING HIERARCHY
═══════════════════════════════════════════════════════════

LAYER 7: APPLICATION
  └─ HTTP not responding, DNS queries fail, email not working
     Tools: curl, dig, telnet, Wireshark application layer
     Fixes: Restart service, check configuration, verify connectivity

LAYER 6: PRESENTATION
  └─ Data corruption, encryption issues, compression problems
     Tools: OpenSSL, certificate validation tools, compression analyzers
     Fixes: Update certificates, check encryption algorithm support

LAYER 5: SESSION
  └─ Session timeouts, persistent connection issues
     Tools: tcpdump, netstat (connection tracking), application logs
     Fixes: Adjust timeout values, restart session

LAYER 4: TRANSPORT
  └─ TCP/UDP port issues, connection refused, timeouts
     Tools: netstat, ss, lsof, firewall logs
     Fixes: Open ports, adjust connection settings, firewall rules

LAYER 3: NETWORK
  └─ Routing issues, IP addressing, ICMP unreachable
     Tools: ping, tracert, route table analysis, BGP/OSPF status
     Fixes: Add routes, adjust metrics, BGP community values

LAYER 2: DATA LINK
  └─ MAC address resolution, VLAN issues, STP problems
     Tools: arp, show interfaces, STP priority, MAC address tables
     Fixes: Clear ARP cache, adjust VLAN, fix STP configuration

LAYER 1: PHYSICAL
  └─ Cable issues, port down, no carrier signal
     Tools: LED status, cable tester, optical power meter
     Fixes: Reseat cable, replace cable, restart port


TROUBLESHOOTING PROGRESSION:
════════════════════════════

❶ Can you physically see the link?
   NO  → Physical layer problem (Layer 1)
   YES → Continue

❷ Is the device getting an IP address?
   NO  → Data link or network layer (Layer 2-3)
   YES → Continue

❸ Can you ping the default gateway?
   NO  → Local network problem (Layer 2-3)
   YES → Continue

❹ Can you ping a remote host?
   NO  → Routing problem (Layer 3)
   YES → Continue

❺ Can you reach a service on a remote host?
   NO  → Transport/Application layer (Layer 4-7)
   YES → Network is working, check application
```

---

## 2. Physical Layer Troubleshooting (Layer 1)

### 2.1 Interface Down Diagnosis

**Symptom**: Interface shows DOWN in show interfaces output

```
LAYER 1 TROUBLESHOOTING RUNBOOK: Interface Down
═══════════════════════════════════════════════════════════

STEP 1: Verify Physical Connection
──────────────────────────────────

Task: Check physical LED indicators
  ✓ Power LED on: YES → device powered
  ✓ Link LED on: ?

  IF Link LED OFF:
    →  Cable not connected or faulty
    →  Remote end not powered
    →  Cable insufficient for signal integrity

Action:
  1. Visually inspect port connectors (both ends)
  2. Reseat cable (disconnect and reconnect firmly)
  3. Check for cable damage (bends, cuts, water damage)
  4. Verify port is not physically covered/blocked

Expected result:
  Link LED turns ON
  Interface transitions from DOWN to UP


STEP 2: Check Interface Configuration
──────────────────────────────────────

Device: Cisco IOS XR
Command: show interfaces GigabitEthernet0/0/1
Output:
  GigabitEthernet0/0/1 is administratively down, line protocol is down

Action: Enable interface
  configure terminal
    interface GigabitEthernet0/0/1
      no shutdown
      commit
  exit

Expected: Interface transitions to UP


STEP 3: Verify Cable Type Compatibility
────────────────────────────────────────

Device capabilities:
  10Gbps port: Supports 10GBASE-T (copper) or 10GBASE-SR (fiber)
  ✗ Incompatible: Cat5e cable on 10Gbps port
  ✓ Compatible: Cat6a cable on 10Gbps port

Symptoms of speed mismatch:
  ├─ Interface flapping (up/down rapidly)
  ├─ High CRC errors
  ├─ Intermittent packet loss
  └─ Lower than expected throughput

Diagnosis commands (Cisco):
  show interfaces GigabitEthernet0/0/1 | include (errors|CRC|input)

Fix: Replace cable with correct type


STEP 4: Check Optical Power (Fiber Connections)
────────────────────────────────────────────────

Tools: Optical power meter
Procedure:
  1. Measure transmit power from source: -5 to +5 dBm typical
  2. Measure receive power at destination: -15 to +5 dBm typical
  3. Calculate loss = Tx - Rx power

Acceptable loss:
  Single-mode fiber:       < 0.5 dB per km
  Multi-mode fiber:        < 3 dB per km
  Typical 1km SMF link:    ~0.5 dB total loss

If loss excessive:
  └─ Actions:
     1. Clean connectors with lint-free cloth
     2. Check for kinks in cable
     3. Replace cable if loss > 10 dB
     4. Contact ISP if on carrier circuit


COMMON ISSUES AND FIXES:
════════════════════════

Issue                          Root Cause              Fix
─────────────────────────────  ──────────────────────  ─────────────────────
Cable not connected            Physical disconnection  Reseat firmly both ends
Orange/red light indicator     Port disabled           Enable with "no shutdown"
Flapping (up/down/up)          Bad cable               Replace cable
No signal on remote end        Cable at max length     Move closer or use amplifier
Port not negotiating speed     Duplex mismatch         Force speed: "speed 1000 duplex full"
```

---

## 3. Data Link Layer Troubleshooting (Layer 2)

### 3.1 VLAN Connectivity Issues

**Symptom**: Users on same VLAN cannot communicate

```
LAYER 2 TROUBLESHOOTING RUNBOOK: VLAN Isolation
═══════════════════════════════════════════════════════════

STEP 1: Verify Device is Tagged in Correct VLAN
───────────────────────────────────────────────

Device: Switch port
User device: Computer in VLAN 10

Cisco command: show vlan id 10
Output:
  VLAN Name                             Status    Ports
  ---- -------------------------------- --------- ------
  10   DATA-PROD                        active    Gi1/0/1, Gi1/0/2, Gi1/0/3

Question: Is Gi1/0/1 (user's port) listed?
  YES  → Port is correctly tagged
  NO   → Port needs to be added to VLAN

Fix:
  configure terminal
    interface GigabitEthernet1/0/1
      switchport mode access
      switchport access vlan 10
    exit
  exit


STEP 2: Verify VLAN Does Not Have Spanning Tree Issues
──────────────────────────────────────────────────────

Symptom: Devices in VLAN see each other intermittently
Cause: Spanning Tree Protocol blocking port

Verification command:
  show spanning-tree vlan 10 | include (Gi1/0/1|State)

Output:
  Gi1/0/1  128.1    PRIORITY   32.00          ALTERNATE  (blocked)

Issue: Port is in ALTERNATE state (blocked)
Reason: STP found a loop and blocked this port
Solution: 1. Check for physical loop in cabling
          2. Enable PortFast if port connects to end device
             interface GigabitEthernet1/0/1
               spanning-tree portfast
               spanning-tree bpduguard enable


STEP 3: Check Trunk Link Configuration
───────────────────────────────────────

If VLAN traffic crosses multiple switches, trunk links must include the VLAN

Verification command:
  show interfaces Gi1/0/48 trunk

Output:
  Native VLAN: 1
  Encapsulation requested:  dot1q
  Encapsulation achieved:   dot1q
  Trunking VLANs enabled:   1,10,20,30,100,200

Question: Is VLAN 10 in "Trunking VLANs"?
  YES  → Trunk is configured correctly
  NO   → Need to add VLAN to trunk

Fix:
  configure terminal
    interface GigabitEthernet1/0/48
      switchport trunk allowed vlan add 10
    exit


STEP 4: Verify VLAN Gateway (L3 Interface)
──────────────────────────────────────────

For inter-VLAN traffic, verify the gateway IP

Show VLAN IP configuration:
  show interface vlan 10

Output:
  Vlan10 is up, line protocol is up (connected)
    Hardware is EtherSVI, address is 001f.64ae.a3ab (bia 001f.64ae.a3ab)
    Internet address is 10.1.10.254 255.255.255.0

Verify:
  1. Is interface UP?
  2. Is IP address correct (matching VLAN subnet)?
  3. Can devices ping the gateway?

Test:
  Device (10.1.10.100) → ping 10.1.10.254
  Expected: Reply from 10.1.10.254

If no reply:
  └─ Fix: Check if gateway interface is enabled
     interface vlan 10
       no shutdown
     exit


COMMON VLAN ISSUES:
═══════════════════

Issue                           Diagnosis Command            Fix
──────────────────────────────  ──────────────────────────  ───────────────────────
Device can't reach gateway      ping 10.1.10.254 → timeout  Enable vlan interface
Two devices on same VLAN        show mac-address-table      Check STP state
see each other intermittently   vlan 10                      Enable PortFast

Can ping gateway but not        show route | grep 10.1      Check routing
other subnet                    show int vlan 10             Verify VLAN gateway IPs

VLAN 10 doesn't exist           show vlan 10                 Create VLAN: vlan 10
on port                                                      Port config: switchport access vlan 10
```

### 3.2 Spanning Tree Protocol (STP) Issues

**Symptom**: Network loops, excessive broadcast traffic

```
LAYER 2 TROUBLESHOOTING RUNBOOK: Spanning Tree Problems
═══════════════════════════════════════════════════════════

STEP 1: Verify STP is Enabled and Active
────────────────────────────────────────

Command: show spanning-tree summary
Output:
  Switch is in pvst mode
  Root bridge for 5 VLANs
  Root ID    Priority    32777
             Address     001f.64ae.a3ab
             Cost        0
             Port        0

Check: "Root ID Address" shows MAC address?
  YES  → STP enabled
  NO   → STP not running

Enable STP if needed:
  configure terminal
    spanning-tree vlan all
  exit


STEP 2: Identify Unexpected STP Topology
─────────────────────────────────────────

Show switch role:
  show spanning-tree vlan 1 | include (Root|Bridge|Port)

Expected roles:
  ✓ One Root Bridge (0 cost, connected to itself)
  ✓ Root Ports (cost = path cost to root)
  ✓ Designated Ports (forwarding on link)
  ✓ Alternate Ports (blocked, backup path)

If unexpected topology:
  1. Identify which switch should be root
  2. Set root bridge priority lower (numeric lower = higher priority)
     configure terminal
       spanning-tree vlan 1 priority 4096
     exit

  3. Allow convergence (30-60 seconds)
  4. Verify new topology


STEP 3: Check for STP Loops
───────────────────────────

Symptom: CPU high, broadcasts flooded, MAC address table unstable
Cause: Loop creates broadcast storm

Verification:
  show spanning-tree summary | include (forwarding|blocking)

  Expected for 3 switches (redundant triangular topology):
    ├─ 6 ports forwarding (each switch: 2 uplinks + 2 downlinks)
    └─ 2 ports blocking (one per trunk link, preventing loop)

If blocking count wrong:
  1. Check for misconfigured ports (not in STP)
  2. Verify all links accounted for
  3. Ensure no additional cables creating loops


STEP 4: Debug STP Calculation (Advanced)
────────────────────────────────────────

Enable STP logging (lab environment only):
  configure terminal
    spanning-tree portfast bpduguard enable
    spanning-tree loopguard enable
    debug spanning-tree events
  exit

Monitor output for:
  ✓ BPDU transmission (every 2 seconds)
  ✓ STP events (topology changes)
  ✓ Port state transitions


SOLUTIONS TO COMMON STP ISSUES:
════════════════════════════════

Problem                    Symptom                     Solution
─────────────────────────  ──────────────────────────  ──────────────────────
Slow convergence           30-60 seconds to reconnect  Lower STP priority on root bridge
                                                       Reduce hello time (network-wide sync needed)

STP loops                  High CPU, MAC flapping      Ensure all ports in STP
                                                       No rogue connections creating loops
                                                       Enable loopguard on blocked ports

Blocked port               Unexpected port blocked     Increase priority on backup switch
not forwarding             on access switch            Verify cost calculations match intended topology

BPDU attacks               Port suddenly blocked       Enable BPDU guard:
                           Topology unstable           spanning-tree portfast bpduguard enable
```

---

## 4. Network Layer Troubleshooting (Layer 3)

### 4.1 Routing Problems

**Symptom**: Packets cannot reach remote subnet

```
LAYER 3 TROUBLESHOOTING RUNBOOK: Routing Issues
═══════════════════════════════════════════════════════════

STEP 1: Verify Route Exists in Routing Table
─────────────────────────────────────────────

Destination subnet: 10.3.0.0/16 (San Francisco site)
Source device: DFW-Core-01

Command: show route 10.3.0.0
Output:
  O*E2 10.3.0.0/16 [110/500] via 10.0.1.2, 00:05:23, GigabitEthernet0/0/0

Analysis:
  O        = OSPF learned route
  E2       = External type 2 (lower precedence)
  110/500  = Administrative distance / metric
  10.0.1.2 = Next hop IP
  Gi0/0/0  = Outgoing interface

✓ Route exists and is preferred
✓ Next hop is reachable
✓ Outgoing interface is available


STEP 2: Verify Next Hop is Reachable
────────────────────────────────────

Command: ping 10.0.1.2
Expected: Replies from 10.0.1.2 (next hop)

If no reply:
  1. Check if next hop is up
     show route 10.0.1.2
  2. Check if interface to next hop is UP
     show interfaces | include (up|down)
  3. Check for ARP resolution
     show arp 10.0.1.2


STEP 3: Verify Outgoing Interface is UP
───────────────────────────────────────

Command: show interfaces GigabitEthernet0/0/0 | include (status|line)
Expected:
  GigabitEthernet0/0/0 is up, line protocol is up

If DOWN:
  1. Check physical connectivity (layer 1)
  2. Check protocol configuration
  3. Re-enable interface: no shutdown


STEP 4: Check for More Specific Route
──────────────────────────────────────

Multiple routes to same destination with different costs

Command: show route 10.3.0.0/16
Output:
  O   10.3.0.0/16 [110/100] via 10.0.1.2 (preferred - lowest metric)
  O   10.3.0.0/16 [110/500] via 10.0.1.3 (alternative path)

This is correct (ECMP not enabled, single best path)

To use both paths:
  configure terminal
    router ospf 1
      maximum-paths 4  (allow up to 4 equal-cost paths)
    exit


STEP 5: Check for Route Filtering
─────────────────────────────────

Check if route is being advertised/accepted

View route filters:
  show route-policy *

Command to check if route is being filtered:
  show bgp 10.3.0.0/16 in | include (accept|reject)

If route is blocked:
  1. Review incoming route policy
  2. Check prefix lists
  3. Verify community filters


STEP 6: Verify Using Traceroute
──────────────────────────────

Trace path from source to destination:
  tracert 10.3.1.1 (from DFW-Core-01 to San Francisco server)

Expected output:
  1  10.0.1.2 (next hop, 2ms)
  2  10.0.1.3 (next router, 25ms)
  3  10.3.0.1 (SF gateway, 28ms)
  4  10.3.1.1 (destination, 30ms)

Interpretation:
  ✓ All hops reachable (no timeouts)
  ✓ Latency increases gradually (expected)
  ✓ Destination responds (can reach)

If timeout at hop 2:
  └─ Router at hop 1 can reach hop 2, but hop 2 doesn't respond to tracert
  └─ Verify hop 2 has reverse route to source


LAYER 3 TROUBLESHOOTING CHECKLIST:
═══════════════════════════════════

□ Route exists in routing table
□ Next hop IP is reachable (ping)
□ Outgoing interface is UP (not down)
□ No more specific route overriding path
□ Route not being filtered by policy
□ Metrics/costs are correct
□ Reverse path is available (symmetric routing)
□ BGP/OSPF neighbor up and stable
□ No route flapping (metric changing)
```

### 4.2 BGP Route Issues

**Symptom**: BGP routes not appearing or withdrawn unexpectedly

```
LAYER 3 TROUBLESHOOTING RUNBOOK: BGP Issues
═══════════════════════════════════════════════════════════

STEP 1: Verify BGP Neighbor Status
──────────────────────────────────

Command: show bgp neighbors 10.0.1.2
Output:
  BGP neighbor is 10.0.1.2, remote AS 65001
  BGP version 4, remote router ID 10.0.1.2
  BGP state = Established, up for 10w3d
  Last read 00:00:30, last write 00:00:45
  Hold time is 180, keepalive interval is 60 seconds

✓ Established = working correctly

If state is NOT Established:
  └─ Possible states and fixes:
     Active     = Trying to connect, check reachability
     Connect    = Connection established, waiting for OPEN message
     OpenSent   = Sent OPEN message, waiting for OPEN reply
     OpenConfirm= OPEN messages exchanged, waiting for KEEPALIVE


STEP 2: Check BGP Neighbor Reachability
────────────────────────────────────────

Command: ping 10.0.1.2 (source from loopback: 10.0.1.1)
  ping 10.0.1.2 source 10.0.1.1

Expected: Replies

If no replies:
  1. Verify route to neighbor exists
     show route 10.0.1.2
  2. Check for interface issues
     show interfaces | include (up|down)
  3. Verify ACLs allow BGP traffic (port 179)


STEP 3: Verify BGP Configuration Match
───────────────────────────────────────

Check local vs neighbor configuration:

Local (DFW-Core-01):
  show bgp summary | include (Local AS|Neighbor)
  Local AS is 65001
  Neighbor 10.0.1.2 is remote AS 65001

Remote (NYC-Core-01):
  show bgp summary | include (Local AS|Neighbor)
  Local AS is 65001
  Neighbor 10.0.1.1 is remote AS 65001

Requirements:
  ✓ Both have matching ASN
  ✓ Neighbor addresses match in config
  ✓ Timers configured same way


STEP 4: Check BGP Routes Being Advertised
──────────────────────────────────────────

View routes being advertised:
  show bgp ipv4 neighbors 10.0.1.2 advertised-routes

  BGP table version is 142, main routing table version 142
  Status codes: s suppressed, * valid, > best, i - internal, r RIB-failure, S Stale
  Origin codes: i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
   *> 10.0.0.0/16   0.0.0.0                  0         32768 i
   *> 10.1.0.0/16   0.0.0.0                  0         32768 i

If route not advertised:
  1. Verify network statement exists
     show run | include "network"
  2. Verify route exists in local routing table
     show route 10.0.0.0


STEP 5: Check BGP Routes Being Received
───────────────────────────────────────

Command: show bgp ipv4 neighbors 10.0.1.2 received-routes

If expected routes not received:
  1. Check neighbor is advertising them
     (Verify on remote device)
  2. Check for receive-side filters
     show route-policy
  3. Check for community filters
     show bgp ipv4 route-policy


STEP 6: Analyze BGP Route Selection
───────────────────────────────────

Why is one route preferred over another?

Command: show bgp ipv4 unicast 10.3.0.0/16
  Network          Next Hop            Metric LocPrf Weight Path
  * 10.3.0.0/16   10.0.1.3                           65002 ?
  > 10.3.0.0/16   10.0.1.2            0       100    32768 i

The ">" indicates the best path (10.0.1.2)

BGP Path Selection Order (simplified):
  1. Highest weight (local preference)
  2. Lowest AS-path length
  3. Lowest MED (multi-exit discriminator)
  4. eBGP over iBGP
  5. Lowest IGP metric to next hop


SOLUTIONS:
═══════════

Issue                          Root Cause                Fix
─────────────────────────────  ──────────────────────   ─────────────────────
BGP state stuck at Active      Neighbor unreachable     Verify route to neighbor
                               TCP port 179 blocked     Check firewall rules
                               Loopback mismatch        Verify update-source config

Routes not advertised          Network statement        Add: network 10.0.0.0 mask 255.255.0.0
                               missing                  Verify route exists: show route 10.0.0.0

Routes received but not        Route policy filters     Review and modify policy
used                           Low weight value         Increase weight or priority

Route flapping                 Unstable neighbor        Check neighbor connectivity
(appearing/disappearing)       BGP timer mismatch       Verify holdtime/keepalive same
                               Network instability      Check for routing oscillation
```

---

## 5. Transport and Application Layer (Layer 4-7)

### 5.1 Port Connectivity Issues

**Symptom**: "Connection refused" or timeout to service port

```
LAYER 4+ TROUBLESHOOTING RUNBOOK: Port Connectivity
═════════════════════════════════════════════════════════════

STEP 1: Test Reachability to Host
────────────────────────────────

Goal: Verify host is reachable at network layer

Command: ping 10.3.1.5
Expected: Replies from 10.3.1.5

If no reply:
  └─ Problem is Layer 1-3 (networking, not port)
  └─ Refer to routing troubleshooting above


STEP 2: Test Port Connectivity
───────────────────────────────

Tool: telnet or nc (netcat)
Goal: Verify TCP port is open and listening

Command: telnet 10.3.1.5 22  (SSH port)
Expected:
  Trying 10.3.1.5...
  Connected to 10.3.1.5
  Escape character is '^]'
  SSH-2.0-OpenSSH_7.4

✓ Connected = Port is open
✗ Timeout = Port is filtered/closed

If timeout:
  1. Verify service is running on destination
     Remote server: show services | include ssh
  2. Verify firewall is not blocking
     show access-list | include 22
  3. Check for interface ACLs


STEP 3: Verify Firewall Rules
────────────────────────────

Check if firewall is blocking traffic

Cisco ASA firewall:
  show access-list | include (permit|deny)
  show access-list OUTSIDE_IN | detail

Look for rules blocking port 22:
  deny tcp any any eq 22  (blocks SSH)
  permit tcp any any eq 22 (allows SSH)

Rules are processed top-to-bottom. First match wins.

If SSH blocked:
  Configure firewall:
    access-list OUTSIDE_IN permit tcp any any eq 22
    access-group OUTSIDE_IN in interface OUTSIDE


STEP 4: Verify Service Port Configuration
─────────────────────────────────────────

Destination server listening on expected port:

Command (Linux): netstat -tlnp | grep LISTEN
Output:
  tcp  0  0  0.0.0.0:22  0.0.0.0:*  LISTEN  1234/sshd

Port 22 is listening globally (0.0.0.0)

Command (Windows): netstat -ano | findstr LISTEN
Output:
  TCP  0.0.0.0:22  0.0.0.0:0  LISTEN  1234

If service not listening:
  1. Verify service is running
  2. Check service configuration (what port configured)
  3. Restart service if needed


STEP 5: Check for NAT/Port Translation
──────────────────────────────────────

If accessing from outside network:

Original request: 203.0.113.100:12345 → 10.3.1.5:22
NAT translation: 203.0.113.100:12345 → [public IP]:2222 → 10.3.1.5:22

Verify NAT rule exists:
  show nat | include 10.3.1.5:22

If NAT not configured:
  Configure:
    ip nat inside source static tcp 10.3.1.5 22 [public_ip] 2222


STEP 6: Trace TCP Connection
─────────────────────────────

Detailed connection attempt (tcpdump/Wireshark):

Capture on intermediate router:
  capture detailed traffic on interface

You should see:
  1. SYN (client initiates)
  2. SYN-ACK (server responds)
  3. ACK (client confirms)
  → Connection established

If SYN never reaches destination:
  └─ Layer 3 routing issue

If SYN arrives but no SYN-ACK returns:
  └─ Firewall blocking or service not listening


CONNECTIVITY TESTING CHECKLIST:
════════════════════════════════

Layer 3 (IP routing):
  □ ping destination host
  □ ping arrives from destination (reverse path)

Layer 4 (Port):
  □ telnet host port → Connected
  □ netstat shows listening port
  □ Firewall rules allow traffic
  □ NAT rules configured (if applicable)

Layer 7 (Application):
  □ Service is running
  □ Application listening on configured port
  □ No authentication issues
  □ Service configuration correct
```

---

## 6. Common Issues and Quick Fixes

### 6.1 One-Minute Fixes

```
QUICK FIX REFERENCE TABLE
═══════════════════════════════════════════════════════════

Symptom                        Quick Diagnosis            60-Second Fix
────────────────────────────  ──────────────────────── ──────────────────────
Interface shows "down"         Is cable connected?      Reseat cable firmly
                               Is port enabled?         "no shutdown"

Cannot ping gateway            Is gateway UP?           "no shutdown" on vlan int
                               Is VLAN on port?         "switchport access vlan X"

Cannot reach remote site       Is BGP neighbor UP?      Check "show bgp summary"
                               Route exists?            Check "show route X.X.X.X"

DNS queries timeout            Can ping DNS server?     Yes → DNS service issue
                               Is port 53 open?         Check firewall port 53

VoIP calls have delays         Is QoS configured?       Check "show qos policy"
                               Bandwidth saturated?     Check "show interface rates"

VLAN 10 not routing traffic    Is VLAN gateway UP?      Check interface vlan 10
                               Is VLAN on trunk?        Check "switchport trunk allowed"

Users in same VLAN            STP blocking port?       Check "show spanning-tree"
can't see each other          Device on VLAN?          Check "show vlan id 10"

Certificate errors (HTTPS)    Certificate expired?     Check "show crypto cert"
                               Wrong CN/SAN?            Verify cert matches hostname

SSH won't connect             SSH port open?           Check "show access-list"
                               Service enabled?         Check "ip ssh version 2"

WAN circuit down              Is interface UP?         Check physical layer
                               Is BGP/OSPF UP?          Check routing protocol status
```

---

## 7. Escalation and Getting Help

### 7.1 Information to Gather Before Escalating

```
ESCALATION INFORMATION CHECKLIST
═════════════════════════════════════════════════════════════

INCIDENT DETAILS:
  □ When did the issue start? (exact time)
  □ Who reported it? (specific user/department)
  □ What is affected? (specific services)
  □ Is it intermittent or constant?
  □ Any recent changes?

WHAT YOU'VE ALREADY TRIED:
  □ Restarted device (Y/N)
  □ Checked physical connectivity (Y/N)
  □ Verified configuration (Y/N)
  □ Collected show command outputs
  □ Checked logs for errors

DIAGNOSTIC DATA TO COLLECT:

From affected device:
  show run                 (Current configuration)
  show version             (Device OS and model)
  show interfaces status   (All interfaces UP/DOWN)
  show ip route            (Routing table)
  show proc cpu            (CPU utilization)
  show mem sum             (Memory usage)
  show log | last 50       (Recent log entries)

Network device (router/core):
  show bgp summary         (BGP neighbor status)
  show ospf neighbor       (OSPF neighbor status)
  show ip bgp neighbors    (BGP route details)
  show log | last 100      (Error messages)

For application issues:
  Application logs         (from app server)
  tcpdump trace            (packet capture)
  show counters            (interface statistics)

INFORMATION FOR VENDOR SUPPORT:

Essential:
  - Device model and serial number
  - Current software version
  - Configuration (sanitized)
  - Error messages from logs
  - When issue started

Helpful:
  - Recent configuration changes
  - Syslog output
  - Device backup from before issue
  - Packet capture (if applicable)
```

---

## References

- **OSI Model**: https://en.wikipedia.org/wiki/OSI_model
- **Cisco Command Reference**: https://www.cisco.com/c/en/us/support/docs/
- **Juniper Troubleshooting Guides**: https://www.juniper.net/documentation/
- **tcpdump/Wireshark**: https://www.wireshark.org/

**Last Revision**: 2025-11-19
**Next Review**: 2026-05-19
**Owner**: Network Operations and Support Team
