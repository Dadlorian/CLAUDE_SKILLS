# Troubleshooting Methodology Guide

## Systematic Problem-Solving Framework

### The OSI Model Approach

#### Layer-by-Layer Investigation
```
Layer 7 (Application):
  - Application responding?
  - Service started?
  - Correct credentials?

Layer 6 (Presentation):
  - Data format correct?
  - Compression working?
  - Encoding issues?

Layer 5 (Session):
  - Session established?
  - TCP/UDP connection active?
  - Session timeout?

Layer 4 (Transport):
  - Correct port?
  - TCP/UDP working?
  - Firewall blocking?

Layer 3 (Network):
  - IP routes present?
  - Ping working?
  - MTU correct?

Layer 2 (Data Link):
  - MAC address resolution?
  - VLAN tagged correctly?
  - Spanning tree issues?

Layer 1 (Physical):
  - Cable connected?
  - Physical port up?
  - Signal quality?
```

### Top-Down Approach (Recommended for Users)

#### Step 1: Scope the Problem
```
Questions:
  1. What doesn't work?
  2. When did it start?
  3. Who is affected?
  4. Is it all applications or specific?
  5. Any recent changes?

Example:
  "User cannot access web server.
   Started at 2:00 PM.
   Only one user affected.
   Email works fine.
   No changes were made today."
```

#### Step 2: Reproduce the Problem
```
Try to:
  1. Replicate from same user
  2. Replicate from different user
  3. Replicate from different location
  4. Replicate with different application

Results:
  - If only one user: Local problem (PC, credentials)
  - If all on same network: Network segment issue
  - If widespread: Core network or server problem
```

#### Step 3: Gather Information
```
Network diagnostics:
  - ping (connectivity)
  - traceroute (path)
  - nslookup (DNS)
  - telnet (port connectivity)
  - netstat (connections)

Device information:
  - Configuration (show running-config)
  - Status (show interfaces)
  - Logs (debug logs)
  - Statistics (SNMP queries)

Application information:
  - Logs (application logs)
  - Performance (response times)
  - Errors (error codes)
  - Dependencies (required services)
```

#### Step 4: Isolate the Problem
```
Method: Divide and conquer

Is it Layer 3 or below?
  ping source.com → No? Layer 3 problem
  ping source.com → Yes? Problem is higher

Is it DNS?
  nslookup example.com → Failed? DNS problem
  ping 8.8.8.8 → Failed? Routing problem

Is it the server?
  telnet server 80 → Failed? Firewall or server
  ssh server → Works? Server is up

Is it the application?
  curl http://server → Failed? App problem
  Check app logs → Root cause
```

### Bottom-Up Approach (For Complex Issues)

#### Step 1: Verify Physical Layer
```
Checklist:
  [ ] Cables connected
  [ ] No physical damage
  [ ] Port lights on/blinking
  [ ] Right port (verify MAC address)
  [ ] Switch port up
  [ ] No excessive errors
```

#### Step 2: Verify Data Link Layer
```
Commands:
  show interfaces (Cisco)
  show lldp neighbors (Cisco)
  arp -a (PC)

Check:
  [ ] MAC address resolved
  [ ] No CRC errors
  [ ] VLAN correct
  [ ] Duplex mismatch? (Full-duplex standard)
  [ ] Spanning tree blocking?
```

#### Step 3: Verify Network Layer
```
Commands:
  ping (ICMP)
  show ip route
  traceroute
  ip -s link

Check:
  [ ] Default gateway reachable
  [ ] Correct routing
  [ ] ACLs blocking?
  [ ] MTU correct (usually 1500)
  [ ] IP address conflict?
```

#### Step 4: Verify Transport Layer
```
Commands:
  netstat -an
  ss -an
  telnet host port
  tcpdump

Check:
  [ ] Service listening on port
  [ ] Firewall allowing port
  [ ] TCP handshake completes
  [ ] No connection resets
```

#### Step 5: Verify Application Layer
```
Commands:
  Specific to application
  curl, wget, telnet
  Application logs

Check:
  [ ] Service is running
  [ ] Correct credentials
  [ ] Configuration correct
  [ ] Sufficient resources
  [ ] Dependencies available
```

## Common Scenarios

### Scenario 1: "Network is Slow"

#### Investigation Plan
```
Step 1: Define "slow"
  - Response time >2 seconds? (threshold)
  - Affecting all or some apps?
  - Intermittent or constant?

Step 2: Check network metrics
  - Interface utilization
  - Packet loss rate
  - Latency measurements
  - Error rates

Step 3: If network healthy
  - Problem is not network
  - Check server performance
  - Check application
  - Check WAN links

Step 4: If network congested
  - Identify bottleneck interface
  - Use NetFlow to find top talkers
  - Implement QoS
  - Plan upgrade
```

### Scenario 2: "Cannot Connect to Server"

#### Systematic Troubleshooting
```
Step 1: Verify connectivity
  ping server_ip
  Result: Success? → Continue
  Result: Fail? → Network problem

Step 2: Check if it's DNS
  ping server_hostname
  Result: Fails? → DNS problem
  Result: Works? → Continue

Step 3: Check if port is accessible
  telnet server_ip port
  Result: Connection refused? → Server not listening
  Result: Connection timeout? → Firewall blocking

Step 4: Check firewall rules
  device(config)# show access-list
  Is port allowed in ACL?
  Is destination in permitted subnet?

Step 5: Check server
  ssh server_ip
  systemctl status service
  netstat -tlnp | grep :port
```

### Scenario 3: "BGP Neighbor Not Establishing"

#### BGP-Specific Troubleshooting
```
Step 1: Verify neighbor is configured
  show ip bgp summary
  Is neighbor in table?
  State column shows what?

Step 2: Verify connectivity to neighbor
  ping neighbor_ip
  Successful? → Continue
  Failed? → Network problem

Step 3: Check BGP configuration
  show run | include neighbor
  Is neighbor IP correct?
  Is AS number correct?
  Is router-id set?

Step 4: Check BGP timers
  show ip bgp neighbors neighbor_ip
  Keep alive interval correct?
  Hold time reasonable?
  Sent/received packets?

Step 5: Review logs
  show log | include BGP
  Look for authentication failures
  Look for timer expirations
  Look for socket errors
```

## Tools & Commands

### Connectivity Testing
```
ping:        Basic connectivity, RTT
ping -M:     MTU discovery
ping -i:     Interval control
ping -s:     Packet size

traceroute:  Path analysis
traceroute -i: Specify interface
traceroute -m: Max hops
traceroute -w: Timeout

mtr:         Combined ping+traceroute
mtr -r:      Report mode
mtr -c:      Packet count
```

### DNS Troubleshooting
```
nslookup:       Interactive DNS query
nslookup -type: Specific record type
host:           Simple DNS lookup
dig:            Detailed DNS query
dig +trace:     Trace full resolution path
dig +short:     Minimal output
```

### Connectivity to Port
```
telnet host port:  Test TCP connectivity
nc -zv host port:  netcat (port scan)
curl -v:           HTTP debugging
curl --trace:      Full request/response trace
```

### Packet Capture
```
tcpdump -i eth0:           Capture on interface
tcpdump -w file.pcap:      Save to file
tcpdump -r file.pcap:      Read from file
tcpdump 'host IP':         Filter by IP
tcpdump -A:                Show ASCII
tcpdump -XX:               Show hex and ASCII
```

## Escalation Procedures

### When to Escalate
```
Criteria:
  1. Unable to determine root cause in 15 minutes
  2. Issue affects production systems
  3. Requires specialized knowledge
  4. Needs access to restricted systems
  5. Potential vendor support required

Escalation path:
  L1 (Field Tech) →
  L2 (Senior Engineer) →
  L3 (Subject Matter Expert) →
  Vendor Support
```

### Information to Provide When Escalating
```
Include:
  1. Detailed problem description
  2. When it started (exact time)
  3. Who is affected
  4. Impact (how many users, business impact)
  5. Troubleshooting steps already tried
  6. Relevant logs/captures
  7. Configuration changes (if any)
  8. Previous similar issues
  9. Any error messages
  10. Current status (stable, degrading, etc.)
```

## Documentation

### Troubleshooting Runbook Template

```
# Problem: [Clear title]

## Symptoms
- What does the user observe?
- What's not working?
- How is service degraded?

## Root Cause
- What is the actual problem?
- Why did it occur?

## Quick Diagnostic
Commands to verify the issue:
```
<commands>
```

## Resolution Steps
1. [First step]
2. [Second step]
3. [Verification]

## Prevention
- What can prevent recurrence?
- Configuration change?
- Monitoring/alerting?

## References
- Related tickets
- Related procedures
- Vendor documentation
```

## Implementation Checklist

- [ ] Document common issues as runbooks
- [ ] Create troubleshooting decision trees
- [ ] Identify escalation procedures
- [ ] Build tool kit (ping, traceroute, tcpdump, etc.)
- [ ] Practice troubleshooting scenarios
- [ ] Establish baseline metrics
- [ ] Create alert for common issues
- [ ] Document recent changes (change control)
- [ ] Maintain vendor contacts
- [ ] Schedule regular training
- [ ] Collect metrics from incidents
- [ ] Review lessons learned

---

**Guide Type**: Operations & Training
**Methodology**: OSI model, top-down, bottom-up
**Primary Tools**: ping, traceroute, netstat, tcpdump, Wireshark
**Skill Level**: All levels (escalates as complexity increases)
**Last Updated**: 2025-11-19
