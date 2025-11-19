# IDS/IPS Deployment Reference

## Overview

Comprehensive guide to Intrusion Detection Systems (IDS) and Intrusion Prevention Systems (IPS) deployment, tuning, and best practices.

## IDS vs IPS

### Comparison Matrix

| Aspect | IDS | IPS |
|--------|-----|-----|
| **Mode** | Detection (passive) | Prevention (active) |
| **Placement** | Passive tap, mirror | Inline |
| **Traffic Impact** | None | Can introduce latency |
| **Action** | Alert, log, notify | Block, drop, reset |
| **Deployment Risk** | Low | Higher |
| **Scalability** | Easier | More challenging |
| **Response Time** | Slower (post-incident) | Fast (inline) |
| **False Positives** | Acceptable | Must be minimal |

### Deployment Models

#### IDS Only (Monitoring)
```
Internet → Firewall → Switch → TAP → IDS Sensor → SIEM

Advantages:
- No latency impact
- Passive observation
- Easy to test and tune
- Safe for initial deployment

Disadvantages:
- Reactive (after attack)
- Depends on incident response
- Attack may succeed before response
```

#### IPS Only (Prevention)
```
Internet → Firewall → IPS Appliance → Switch → Internal Network

Advantages:
- Proactive blocking
- Real-time prevention
- Faster incident response

Disadvantages:
- Must be highly accurate
- False positives block legitimate traffic
- Adds latency
```

#### IDS + IPS (Layered Defense)
```
Layer 1 (IPS - Firewall)
Internet → Firewall/IPS → (Blocks Layer 3/4)
               │
Layer 2 (IPS - Network)
    → Network IPS → (Blocks application attacks)
               │
Layer 3 (IDS - Endpoint)
    → Endpoint IDS → (Detects missed attacks)

Best Practice:
- Network perimeter IPS
- Endpoint IDS for lateral movement
- SIEM for correlation
```

## Detection Methods

### Signature-Based Detection

#### Definition
```
Signature = Pattern that matches known attack

Example:
- SQL Injection pattern: union select
- Buffer overflow: shellcode pattern
- Protocol anomaly: invalid flag combination
```

#### Signature Structure
```
Message: "ET ATTACK SQL Injection"
Flow: client to server
Application: HTTP
Payload: contains "union select" OR
         contains "drop table" OR
         contains "; delete"
Threshold: alert on first match
Action: Log and alert
```

#### Advantages
- Fast, low CPU impact
- Works well for known attacks
- Clear rule documentation
- Easy to understand

#### Disadvantages
- Evasion through obfuscation
- Requires signature updates
- Misses zero-day attacks
- Can be bypassed with encoding

### Anomaly-Based Detection

#### Concept
```
Establish baseline behavior
Compare current traffic to baseline
Alert on significant deviations
```

#### Baseline Metrics

```
Network Baseline:
- Normal bandwidth usage
- Peak/off-peak patterns
- Typical protocols
- Normal traffic volume
- Typical destination networks

Host Baseline:
- Normal process execution
- Typical network connections
- Normal resource usage
- Expected user behavior
- Normal file access patterns
```

#### Anomaly Types

```
Statistical Anomalies:
- Volume anomaly: 10x normal traffic
- Rate anomaly: Connections/minute exceeds baseline
- Entropy anomaly: High randomness in data
- Timing anomaly: Access outside normal hours

Protocol Anomalies:
- Malformed packets
- Invalid flag combinations
- Unexpected sequences
- Fragmentation anomalies

Behavioral Anomalies:
- Unusual user access
- Abnormal process execution
- Suspicious privilege escalation
- Atypical data movement
```

#### Advantages
- Detects zero-day attacks
- Detects variants of known attacks
- Finds sophisticated attacks
- Unknown threat detection

#### Disadvantages
- High false positives (initially)
- Requires tuning
- CPU intensive
- Training period needed

### Heuristic Detection

#### Concept
```
Analyze patterns and characteristics
Make educated decisions about threats
Balance signatures and anomalies
```

#### Examples

```
Heuristic 1: Code Injection Detection
IF packet contains executable code
  AND packet sent to network service port
  AND service not known to handle code
THEN alert "Possible code injection"

Heuristic 2: Reconnaissance Detection
IF host scans 50+ ports in 1 minute
  AND majority of connections timeout
  AND from non-routine source
THEN alert "Possible port scan"

Heuristic 3: DDoS Detection
IF traffic exceeds 5x baseline
  AND sources are diverse
  AND destination is single host
  AND pattern consistent
THEN alert "Possible DDoS attack"
```

## Deployment Topologies

### Network Perimeter Deployment

```
┌─────────────────────────────────┐
│ Internet                        │
└──────────────┬──────────────────┘
               │
        [Perimeter Firewall]
               │
          [IPS Appliance]  ← Inline, monitors all traffic
               │
        [Core Switch]
               │
    ┌──────────┴──────────┐
    │                     │
[DMZ Network]    [Internal Network]
```

### Internal Network Deployment

```
┌─────────────────────────────────┐
│ Data Center Network             │
│                                 │
│  ┌─────────────┐      ┌──────┐ │
│  │ Web Servers │      │ IDS  │ │
│  └─────────────┘      └──────┘ │
│                         │       │
│  ┌─────────────┐    (Tap/Mirror)
│  │ App Servers │        │       │
│  └─────────────┘        │       │
│                         │       │
│  ┌─────────────┐        │       │
│  │ Databases   │────────┘       │
│  └─────────────┘                │
│                                 │
└─────────────────────────────────┘
```

### DMZ Segmentation with IPS

```
Internet → [Perimeter FW] → [IPS] → DMZ → [Internal FW] → Internal

Traffic Flow:
1. Internet traffic enters perimeter firewall
2. IPS inspects at network layer
3. DMZ hosts receive filtered traffic
4. Internal firewall protects internal network
```

### Endpoint-Based Detection

```
┌─────────────────┐
│  Endpoint IDS   │  Host-based agent
│  - Process mon  │  - Monitors local activity
│  - File access  │  - Detects lateral movement
│  - Network mon  │  - Logs all events
│  - Behavior     │
└─────────────────┘
        │
        │ Report anomalies
        ▼
   [SIEM System]
```

## Rule Management

### Rule Categories

#### Exploit Rules
```
Detect known exploitation techniques
- Buffer overflows
- Format string attacks
- Directory traversal
- Command injection
```

#### Policy Rules
```
Enforce security policies
- Unauthorized protocols
- Peer-to-peer applications
- Streaming services
- Unauthorized VPN
```

#### Malware Rules
```
Detect malicious code signatures
- Trojan patterns
- Worm signatures
- Botnet communication
- C&C server connections
```

#### Application Rules
```
Monitor application security
- SQL injection
- XSS attacks
- CSRF tokens
- Default credentials
```

### Rule Tuning Process

```
1. Deploy initial rules (baseline)
   └─ Use standard rulesets
   └─ Enable critical rules only
   └─ Document baseline

2. Monitor for false positives
   └─ Run for 1-2 weeks
   └─ Collect statistics
   └─ Identify noisy rules

3. Tune noisy rules
   └─ Increase thresholds
   └─ Add exceptions
   └─ Refine signatures

4. Review coverage
   └─ Check detection gaps
   └─ Enable additional rules
   └─ Validate against threats

5. Ongoing refinement
   └─ Quarterly review
   └─ Update rules
   └─ Adjust thresholds
   └─ Add new rules
```

### Whitelist Management

#### Whitelist Examples
```
Server Whitelists:
- Known secure servers
- Approved update servers
- Trusted partners
- Business services

Application Whitelists:
- Approved software
- Standard updates
- Known secure apps
- Vendor patches

Network Whitelists:
- Trusted network ranges
- Partner networks
- ISP networks
- Internal networks
```

#### Whitelist Rules

```
Rule: Suppress false positive
IF source in TRUSTED_SERVERS
  AND destination 8.8.8.8 port 53
  AND protocol DNS
THEN suppress alert

Rationale: Trusted servers querying Google DNS is normal

Review: Quarterly - ensure still valid
```

## Popular IDS/IPS Platforms

### Suricata
```
Open-source IDS/IPS
- Excellent performance
- Lua scripting support
- Mod-security integration
- Multi-threading
- Active development
```

### Snort
```
Original IDS standard
- Well-known signature set
- Flexible rule writing
- Proven in enterprise
- Community-driven
- Some commercial variants
```

### Zeek (Bro)
```
Network monitoring and analysis
- Protocol analysis
- Scripting language (Zeek)
- Log generation
- Can feed IDS alerts
- Forensic capability
```

### Palo Alto Networks
```
Commercial IPS
- Advanced threat protection
- Machine learning integration
- Integrated firewall
- Easy management
- 24/7 support
```

### Cisco
```
Commercial IDS/IPS options
- Snort-based
- ESA for email
- Web security
- Integrated ecosystem
- Enterprise support
```

## Alert and Response

### Alert Categories

```
Severity Levels:

Critical (Response in 15 minutes)
- Active exploitation detected
- Malware detected
- DDoS in progress
- Unauthorized access attempts

High (Response in 1 hour)
- Suspicious anomalies
- Policy violations
- Reconnaissance activity
- Unusual network behavior

Medium (Response in 1 day)
- Benign anomalies
- Minor violations
- Potential issues
- Items for investigation

Low (Review periodically)
- Informational
- Statistics
- Learning events
- Configuration changes
```

### Alert Enrichment

```
Raw Alert:
"ET TROJAN Win32/Upatre.A Checkin"

Enriched Alert:
Event ID: 12345
Timestamp: 2025-11-19 14:23:45 UTC
Source IP: 192.168.1.100
Source Hostname: WORKSTATION-42
Source User: john.doe
Destination IP: 185.220.101.45
Destination Port: 443
Protocol: TCP
Category: Trojan
Severity: Critical

Threat Intelligence:
- IP reputation: Malicious C&C
- Last seen: 2025-11-15
- Known IOCs: 3
- Recommendations: Isolate host, clean malware

Historical:
- Same user same source: 2 other alerts
- Same destination: 47 other alerts
```

### Automated Response

```
Detection → Analysis → Decision → Action

Example 1: Known Malware
Alert Type: Trojan signature match
Detection Time: <1 second
Decision: Block at IPS
Action: Segment network, isolate host, alert SOC

Example 2: DDoS Attack
Alert Type: Volume anomaly + protocol
Detection Time: 10 seconds
Decision: Rate limit, blackhole
Action: Activate DDoS mitigation, notify

Example 3: Policy Violation
Alert Type: Unauthorized protocol
Detection Time: Real-time
Decision: Block connection
Action: Log, alert, report
```

## Best Practices

### Deployment
- Test thoroughly in lab first
- Deploy in passive/IDS mode initially
- Monitor for 2-4 weeks
- Tune false positives aggressively
- Enable IPS mode gradually
- Plan failover/redundancy

### Tuning
- Start conservative (fewer alerts)
- Gradually increase coverage
- Document every rule change
- Test changes in lab
- Implement change control
- Schedule maintenance windows

### Monitoring
- Baseline normal traffic
- Monitor alert rates
- Alert on high volume (DoS)
- Alert on zero alerts (evasion)
- Regular rule review
- Update threat intelligence

### Integration
- Feed data to SIEM
- Correlate with firewalls
- Integrate with endpoint detection
- Share threat intelligence
- Automate response where safe
- Manual review critical alerts

### Maintenance
- Update rules regularly
- Patch sensors promptly
- Monitor sensor health
- Track rule effectiveness
- Review performance metrics
- Plan capacity growth
