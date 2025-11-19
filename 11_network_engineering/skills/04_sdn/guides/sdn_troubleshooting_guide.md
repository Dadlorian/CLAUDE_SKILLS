# SDN Troubleshooting Guide

## Troubleshooting Framework

### Systematic Approach

```
1. Gather Information
   ├─ Collect error messages
   ├─ Check logs (controller, switches)
   ├─ Verify basic connectivity
   └─ Document baseline

2. Isolate Problem
   ├─ Is it control plane or data plane?
   ├─ Single device or multiple?
   ├─ Affects all traffic or specific app?
   └─ When did it start?

3. Root Cause Analysis
   ├─ Check recent changes
   ├─ Review metrics
   ├─ Correlate events
   └─ Ask 5 Whys

4. Implement Fix
   ├─ Plan change
   ├─ Test if possible
   ├─ Apply carefully
   └─ Monitor results

5. Prevent Recurrence
   ├─ Document solution
   ├─ Improve monitoring
   ├─ Update runbooks
   └─ Share knowledge
```

## Common Issues & Solutions

### Issue 1: Controller Unreachable

**Symptoms**:
- Switches show "controller disconnected"
- API requests fail

**Diagnosis**:
```bash
# Check controller status
ssh controller "systemctl status onos"

# Check network connectivity
ping <controller-ip>
ssh <controller-ip> "echo connected"

# Check listening ports
netstat -tlnp | grep 6653

# Check firewall rules
iptables -L | grep 6653
```

**Solutions**:
```bash
# Restart controller
systemctl restart onos

# Check config
cat /etc/onos/cfg.d/org.onosproject.core.cfg

# Verify certificate (if TLS)
openssl x509 -in controller.crt -text -noout

# Check memory/CPU
top -b -n1 | head -20
```

### Issue 2: Devices Not Connecting

**Symptoms**:
- "Devices not found" in controller
- Switch shows "unknown controller state"

**Diagnosis**:
```bash
# On controller
onos-client> devices
# Expected: List of devices

# On switch
show openflow summary
show openflow switch

# Test connectivity to controller
ping 10.0.0.1  (controller IP)
```

**Solutions**:
```bash
# Verify controller configured correctly on switch
# Cisco
show run | include openflow

# Correct config
openflow controller ipv4 10.0.0.1 port 6653

# Restart OpenFlow feature
openflow mode standalone
no openflow mode
openflow mode standalone

# Check switch capabilities
onos> device-supports-type of:0000000000000001
```

### Issue 3: Flows Not Installing

**Symptoms**:
- Traffic drops
- Flows show in controller but not on switch
- Packets sent to controller repeatedly

**Diagnosis**:
```bash
# On controller
onos> flows
# Check if flows exist

onos> flows any
# Check flow status (installed? pending?)

# On switch
ovs-ofctl dump-flows br0
# Compare with controller

# Check for errors
tail -f /var/log/openvswitch/ovs-vswitchd.log
```

**Solutions**:
```bash
# Add more specific match criteria
# Instead of just port, add ethernet type

# Increase flow timeout
ovs-vsctl set bridge br0 other-config:flow-table-size=65536

# Clear and resync
onos> purge-flows
# Wait for controller to reinstall

# Check available actions
onos-client> flow-test start of:0000000000000001
```

### Issue 4: VXLAN Not Working

**Symptoms**:
- VTEPs not reaching each other
- No MAC learning
- Broadcast flooding

**Diagnosis**:
```bash
# Verify VTEP status
show nve interface
show nve vni
show nve peers

# Test underlay
ping <remote-vtep-loopback>
ping -M do -s 1472 <remote-vtep>  # Test MTU

# Check multicast (if used)
show ip mroute
show ip pim rp-hash 224.1.1.1

# Check BGP EVPN
show bgp l2vpn evpn summary
show bgp l2vpn evpn
```

**Solutions**:
```bash
# Check VLAN-VNI mapping
show vlan id 100
show vn-segment vlan 100

# Verify loopback is reachable
ping <local-loopback>
ping <remote-loopback>

# Check MTU settings
show interface GigabitEthernet 1/1 | include mtu

# Enable jumbo frames if needed
mtu 1600

# Verify BGP config
show run | section bgp
```

### Issue 5: High Latency

**Symptoms**:
- Applications slower than expected
- SLA breaches
- Packet loss on overlay

**Diagnosis**:
```bash
# Measure latency
ping -c 100 <destination>
mtr <destination>  # Multi-hop latency

# Check buffer stats
show queues
show buffer-usage

# Monitor CPU
top
show processes cpu

# Check for packet loss
show counters
```

**Solutions**:
```bash
# Identify bottleneck layer
- Underlay: ping between VTEPs
- Overlay: ping between VMs
- Application: TCP performance

# Optimize encapsulation
# Use hardware offload if available

# Reduce controller communication
# Proactive flow installation instead of reactive

# Tune switch buffer
# Increase output queue size

# Optimize path
# Use ECMP for load balancing
```

### Issue 6: Policy Not Enforcing

**Symptoms**:
- Firewall rules not blocking traffic
- Contracts not restricting flows

**Diagnosis**:
```bash
# Check policy in controller
onos> policies

# Verify push to devices
show platform internal hal l4log

# Test with specific traffic
# Try denied rule, should be dropped

# Check firewall logs
show firewall log

# Verify EPG assignment
show endpoint interface ethernet 1/10
```

**Solutions**:
```bash
# Verify policy syntax
# Check source/destination EPG names

# Force re-push to devices
onos> policy-resync

# Check rule priority
# Higher priority rules evaluated first

# Verify fabric connectivity
# Device in correct fabric?

# Clear policy cache
# Restart policy engine if available
```

## Log Analysis

### Key Log Files to Check

```
Controller Logs:
├─ /var/log/onos/karaf.log (OpenDaylight)
├─ /opt/onos/log/karaf.log (ONOS)
├─ /var/log/syslog (system)
└─ /var/log/auth.log (authentication)

Switch Logs (Cisco):
├─ Show logging (current buffer)
├─ Show logging history
├─ Show snmp trap
└─ Debug output (if enabled)

Switch Logs (OVS):
├─ /var/log/openvswitch/ovs-vswitchd.log
├─ /var/log/openvswitch/ovsdb-server.log
└─ Journal: journalctl -u openvswitch
```

### Log Analysis Commands

```bash
# Search for errors
grep -i error /var/log/onos/karaf.log | tail -20

# Find recent problems
grep "ERROR\|WARN" /var/log/syslog | tail -50

# Correlate timing
# Note exact time of issue
# Search logs for activity around that time

# Trace flow installation
grep "FlowRuleStore" karaf.log

# Monitor in real-time
tail -f /var/log/onos/karaf.log | grep -i openflow

# Count errors by type
grep ERROR karaf.log | cut -d' ' -f5- | sort | uniq -c | sort -rn
```

## Performance Monitoring

### Key Metrics to Track

```
Controller:
├─ CPU usage (should be <70%)
├─ Memory usage (should have headroom)
├─ API response time (<200ms)
├─ Flow installation rate (flows/sec)
└─ Controller-to-switch latency (<50ms)

Network:
├─ Link utilization (should be <80%)
├─ Packet loss (should be <0.1%)
├─ Latency (within SLA)
├─ Jitter (stability measure)
└─ Out-of-order packets (should be rare)

Flows:
├─ Total flow count (trending)
├─ Flow creation rate (new/sec)
├─ Flow table utilization (% full)
├─ Packet-in rate (indicates misses)
└─ Flow timeout distribution
```

### Monitoring Commands

```bash
# ONOS
onos-client> summary                # Overall stats
onos-client> device-stats           # Device health
onos-client> flow-stats             # Flow statistics
onos-client> port-stats             # Port counters

# OVS
ovs-vsctl get-bridge-statistics br0
ovsdb-client list-columns Open_vSwitch
ovs-appctl stats/show               # Per-flow stats

# Cisco
show platform statistics            # ASIC stats
show queue statistics               # Queue counters
show buffers                        # Buffer usage
```

## Escalation Procedures

### Level 1: Operator

```
Can handle:
├─ Common known issues
├─ Basic connectivity checks
├─ Log collection
└─ Ticket documentation

Cannot handle:
├─ Controller bugs
├─ Deep debugging
├─ Design decisions
└─ Major architecture changes

Escalation trigger:
├─ Issue not in runbook?
├─ Affecting multiple users?
├─ Customer SLA at risk?
└─ Unknown root cause?
```

### Level 2: Senior Engineer

```
Can handle:
├─ Complex troubleshooting
├─ Performance tuning
├─ Configuration optimization
└─ Root cause analysis

Requires:
├─ Full information from L1
├─ Lab environment access
├─ Vendor documentation
└─ Time to investigate

Typical response: 2-4 hours
```

### Level 3: Vendor Support

```
When to escalate:
├─ Suspected software bug
├─ Undocumented behavior
├─ Potential hardware issue
├─ Unable to resolve internally

Required info:
├─ Detailed reproduction steps
├─ Full logs and diagnostics
├─ Version information
├─ Description of changes before issue

Vendor response: Next business day (typical)
```

## Runbook Template

```
Title: [Issue Name]
Severity: [Critical/High/Medium/Low]
Estimated Time to Resolve: [Time]

Symptoms:
- [Symptom 1]
- [Symptom 2]
- [Symptom 3]

Quick Diagnosis:
1. Check [X]
2. If [condition], then [action]
3. Else, go to detailed diagnosis

Detailed Diagnosis:
1. Collect logs from [location]
2. Check [metric] with command [X]
3. Compare to baseline [Y]
4. If [condition], proceed to Resolution A
5. Else, proceed to Resolution B

Resolution A:
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. Verify by [test]

Rollback:
1. If resolution fails, [rollback action]
2. Contact [level 3 support]

Prevention:
- [Monitor X in future]
- [Improve Y process]
- [Add Z automation]

Notes:
- [Related issues]
- [Similar past incidents]
- [Vendor contacts]
```

## Debugging Tools

### Network Analysis

```bash
# Packet capture
tcpdump -i eth0 -w capture.pcap host 10.100.0.10
# Analyze with Wireshark

# Flow tracing
onos> trace ipv4 {srcip=10.100.0.10 dstip=10.100.0.20}
# Shows exact flow installation path

# OpenFlow debugging
ovs-ofctl snoop br0
# Shows all OpenFlow messages in real-time

# BGP debugging (if EVPN)
debug ip bgp
# Shows BGP activity
```

### Capacity Planning

```bash
# Monitor trends over time
# Collect metrics daily, plot weekly

# Identify bottlenecks
# Link utilization >80% = concern
# Flow table >80% full = concern

# Plan upgrades
# When will we hit limits?
# What's the upgrade path?

# Growth rate analysis
# Flows growing at X/month?
# Devices at Y/quarter?
```

---

## Troubleshooting Checklist

```
Network Problem Solving:

☐ Problem Definition: Clearly describe issue
☐ Scope: Single device? Multiple? All?
☐ Timeline: When did it start? Sudden or gradual?
☐ Impact: How many users? What applications?
☐ Reproducibility: Can it be repeated?

☐ Baseline: How was it before problem?
☐ Recent Changes: What changed recently?
☐ Log Review: Any errors in logs?
☐ Connectivity: Verify layer 2/3 connectivity
☐ Configuration: Is config correct?

☐ Metrics: Check CPU, memory, bandwidth
☐ Flow Rules: Are policies installed?
☐ Device Health: All devices up?
☐ Controller Health: Controller responsive?
☐ Underlay: Is physical network healthy?

☐ Root Cause: What specifically is broken?
☐ Fix Plan: What will fix it?
☐ Test Plan: How to verify fix?
☐ Rollback: What if fix makes it worse?
☐ Implementation: Execute carefully

☐ Verify Fix: Does it actually work?
☐ Monitor: Watch for recurrence
☐ Document: Update runbook
☐ Communicate: Notify stakeholders
☐ Post-Mortem: Learn from incident
```
