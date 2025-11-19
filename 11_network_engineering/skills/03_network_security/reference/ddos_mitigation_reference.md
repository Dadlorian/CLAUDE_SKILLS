# DDoS Mitigation Reference

## DDoS Attack Types

### Volumetric Attacks

#### UDP Flood
```
Attack Mechanism:
- Send massive UDP packets
- Overwhelm target bandwidth
- Source usually spoofed
- No connection establishment

Characteristics:
- High packet rate
- Large data volume
- Random/sequential ports
- Simple implementation

Mitigation:
- UDP rate limiting
- Ingress filtering (BCP 38)
- Source IP validation
- ISP-level filtering
```

#### ICMP Flood
```
Attack Mechanism:
- Send large ICMP echo requests
- Force echo replies from target
- Amplified with broadcast
- Consumes bandwidth

Characteristics:
- Echo request/reply pattern
- High volume
- Identifiable pattern
- Easy to detect

Mitigation:
- Disable ICMP echo
- Rate limit ICMP
- Configure firewall rules
- Source validation
```

#### DNS Amplification
```
Attack Mechanism:
- Query recursive DNS servers
- Spoof victim IP as source
- Receive large responses
- Amplification factor: 25-70x

Example:
- Attacker sends 1 KB DNS query
- Server responds with 50 KB
- Attacker controls volume and target

Mitigation:
- Restrict DNS recursion
- Rate limit DNS responses
- Egress filtering
- Anycast DNS scrubbing centers
```

#### NTP Amplification
```
Attack Mechanism:
- Query NTP servers with monlist
- Get large list of clients
- Spoof source as victim
- Amplification factor: 200-600x

Characteristics:
- Single request → 50+ responses
- Easy to detect (NTP ports)
- Well-known attack
- Often automated

Mitigation:
- Disable monlist (recent NTP)
- Restrict NTP queries
- Rate limiting
- Upstream filtering
```

### Protocol Attacks

#### SYN Flood
```
Attack Mechanism:
- Send SYN packets rapidly
- Don't complete 3-way handshake
- Exhaust SYN queue
- Server unable to accept connections

Sequence:
Attacker → SYN → Server (allocates resources)
           └─ (no ACK, resources leak)

Characteristics:
- Incomplete connections
- Resource exhaustion
- Specific port targeting
- CPU/memory impact

Mitigation:
- SYN cookies
- SYN cache
- Connection timeout reduction
- Rate limiting
- SYN proxy (firewall)
```

#### Fragmented Packet Attack
```
Attack Mechanism:
- Send fragmented packets
- Force reassembly overhead
- Exhaust memory/CPU
- Cause packet loss

Mitigation:
- Fragment reassembly timeout (short)
- Maximum fragments per connection
- Check fragment overlap
- Discard invalid fragments
```

#### ACK Flood
```
Attack Mechanism:
- Send TCP ACK packets
- Spoof source IP
- Force processing overhead
- Consume bandwidth

Characteristics:
- Legitimate-looking packets
- ACK flag set
- Random or specific sequence
- Easy to generate

Mitigation:
- Stateful filtering
- Rate limiting by source
- Sequence validation
- ACK number checking
```

### Application Layer Attacks

#### HTTP Flood
```
Attack Mechanism:
- Send HTTP GET/POST requests
- Legitimate-looking traffic
- Consume server resources
- Difficult to distinguish from users

Characteristics:
- Layer 7 (application)
- Appears as web traffic
- Variable payload size
- Can bypass network mitigations

Mitigation:
- Web application firewall (WAF)
- Rate limiting per IP/session
- CAPTCHA challenges
- JavaScript challenge
- DDoS-specific rules
- Load balancing
```

#### Slowloris Attack
```
Attack Mechanism:
- Open many HTTP connections
- Send requests slowly
- Keep connections open long
- Exhaust connection pool

Request Pattern:
GET / HTTP/1.1
Host: example.com
X-Header: value\r\n
(pause - wait 30 seconds)
X-Header2: value2\r\n
(repeat until timeout)

Mitigation:
- Connection timeouts (short)
- Max connections per IP
- Request timeouts
- Request parsing limits
```

#### DNS Query Flood
```
Attack Mechanism:
- Send DNS queries targeting domain
- Legitimate-looking queries
- Consume resolver resources
- Flood auth servers

Characteristics:
- Valid query format
- Various query types (A, MX, etc)
- Random subdomains
- High rate from many IPs

Mitigation:
- Rate limiting per IP
- Query-per-second limits
- Cache optimization
- Anycast DNS distribution
```

## Detection Methods

### Volume-Based Detection

```
Baseline Metrics:
Normal bandwidth: 100 Mbps
Normal packet rate: 50,000 pps
Normal connections: 1,000 per second

Thresholds:
Critical: >500 Mbps (5x baseline)
High: >250 Mbps (2.5x baseline)
Medium: >150 Mbps (1.5x baseline)

Alert Conditions:
IF bandwidth > 500 Mbps for 1 minute
  AND traffic not legitimate
THEN trigger critical alert
```

### Rate-Based Detection

```
Connection Rate Analysis:
Normal: ~100 new connections/sec
Baseline learning: 1 week
Alert threshold: 5x baseline

Packet Rate Analysis:
Normal: ~50,000 packets/sec
Alert threshold: 10x baseline

Detection Rule:
IF (current_rate / baseline_rate) > 5
  AND duration > 10 seconds
  AND sources diverse or concentrated
THEN alert DDoS
```

### Behavioral Analysis

```
Pattern Recognition:
- Source IP distribution
- Destination port distribution
- Protocol mix anomalies
- Payload size anomalies
- Timing patterns
- TTL patterns

Example Rule:
IF source IPs > 10,000
  AND targeting same destination
  AND packet size consistent
  AND protocol UDP
  AND all have similar TTL
THEN classify as volumetric DDoS
```

### Signature Detection

```
Known Attack Patterns:

Memcached Amplification:
- UDP port 11211
- Request: "stats\r\n"
- Response: Multiple large packets
- Detection: Port + payload pattern

NTP Amplification:
- UDP port 123
- Request mode 7 (private)
- Response: Large monlist
- Detection: Port + command pattern
```

## Mitigation Strategies

### Network-Level Mitigation

#### Rate Limiting
```
Interface level:
police rate 1000000 bps burst 10000

Per-flow limiting:
permit tcp any any range 49152 65535 rate-limit 100000

Action: Drop or mark traffic exceeding rate
```

#### Blackhole Routing
```
Route attack traffic to null interface:
route 203.0.113.5/32 null 0

Effect:
- Drops all traffic to target
- Stops attack
- No legitimate access either
- Temporary measure

Implementation:
1. Detect attack destination
2. Create route to null 0
3. Monitor legitimate impact
4. Remove when attack stops
```

#### Ingress Filtering (BCP 38/RFC 2827)
```
Prevent spoofed packets:
- Drop packets with invalid source
- Source IP not in connected networks
- Prevents amplification attacks

Configuration:
access-list 100 permit ip 10.1.0.0 0.0.255.255 any
access-list 100 deny ip any any

Apply on inbound interface:
ip access-group 100 in
```

#### Anycast Scrubbing Centers
```
Architecture:
       Internet
          │
    Anycast Detection
          │
     ┌────┴────┐
     │          │
  [Scrub1]  [Scrub2]  (analyze traffic)
     │          │
     └────┬────┘
          │
    [Cleaned Traffic]
          │
     [Your Network]
```

### Firewall Mitigation

#### Connection Limits
```
Per-Source Limits:
max-connections per-source 100

Per-Port Limits:
max-connections port 80 1000
max-connections port 443 1000

Idle Timeout:
idle-timeout 5 minutes

Actions:
- Drop new connections exceeding limit
- Log violations
- Alert on threshold breach
```

#### Stateful Inspection
```
Firewall validates:
- SYN → SYN-ACK → ACK sequence
- Drop incomplete handshakes
- Track connection state
- Drop out-of-sequence packets

Result:
- SYN floods blocked
- Invalid packets dropped
- Legitimate traffic passes
```

### Application-Level Mitigation

#### Web Application Firewall (WAF)
```
Layer 7 inspection:
- Analyze HTTP requests
- Detect SQL injection
- Block malformed requests
- Rate limit requests
- CAPTCHA challenges

Example Rules:
Rule 1: Rate limit per IP
  IF requests/second > 100 from single IP
  THEN require CAPTCHA

Rule 2: User-Agent validation
  IF User-Agent contains bot patterns
  THEN challenge or block

Rule 3: Geographic blocking
  IF request from high-risk country
  THEN require additional auth
```

#### Bot Mitigation
```
JavaScript Challenge:
- Serve challenge page
- Require JavaScript execution
- Bots often can't execute
- Legitimate users pass through

CAPTCHA Challenge:
- Present visual puzzle
- User must solve
- Robots typically fail
- Slows attackers significantly

Cookie-Based:
- Set cookie on first visit
- Require cookie on return
- Bots may not maintain cookies
```

## Cloud-Based DDoS Protection

### SaaS DDoS Services

```
Service Model:
1. Change DNS to protection service
2. Traffic routes through provider
3. Provider filters malicious traffic
4. Clean traffic forwarded to origin

Provider: Cloudflare, Akamai, etc.

Advantages:
- No on-premises equipment
- Absorbs large attacks
- Always on protection
- Global scrubbing centers

Disadvantages:
- Cost per bandwidth
- Third-party dependency
- Latency considerations
- Setup and configuration
```

### Hybrid Approach

```
Architecture:
Internet
    │
[ISP + Cloud DDoS]  (1st layer - volumetric)
    │
[On-premises Firewall]  (2nd layer - protocol)
    │
[Web Application Firewall]  (3rd layer - app)
    │
[Origin Servers]

Benefits:
- Defense in depth
- Redundant protection
- Catches different attack types
- Layered approach
```

## Response Procedures

### Detection to Response Timeline

```
0-30 seconds:
- Alert generated
- Initial classification
- Threshold verification

30 seconds - 2 minutes:
- Alert escalation
- Engineer notified
- Analysis begins

2-5 minutes:
- Attack confirmed
- Mitigation activated
- Stakeholders notified

5-15 minutes:
- Monitor mitigation
- Adjust thresholds
- Full response team engaged

15+ minutes:
- Sustained mitigation
- Root cause analysis
- Coordination with providers
```

### Incident Response Plan

```
Pre-Attack Planning:
1. Define DDoS threshold
2. Create playbooks
3. Establish escalation
4. Plan team coverage
5. Test procedures
6. Document contacts

During Attack:
1. Verify DDoS (not outage)
2. Activate incident response
3. Notify stakeholders
4. Implement mitigation
5. Monitor effectiveness
6. Adjust as needed

Post-Attack:
1. Analyze logs
2. Determine attack source
3. Identify vulnerabilities
4. Plan improvements
5. Update procedures
6. Communication/lessons learned
```

## Monitoring and Alerting

### Key Metrics

```
Bandwidth:
- Inbound/outbound utilization
- Peak rate
- Spike detection
- Sustained vs. burst

Packet Rate:
- Packets per second
- Protocol distribution
- Port distribution
- Fragmentation ratio

Connection Count:
- New connections/sec
- Connection states
- Connection duration
- Half-open connections

Application Metrics:
- HTTP requests/sec
- Response times
- Error rates
- Cache hit ratio
```

### Alert Configuration

```
Alert: Bandwidth Spike
Condition: Inbound > 200 Mbps
Duration: 60 seconds
Severity: High
Action: Notify engineering team

Alert: SYN Flood
Condition: Half-open > 10,000
Duration: 30 seconds
Severity: Critical
Action: Auto-activate SYN proxy

Alert: Protocol Anomaly
Condition: UDP > 70% of traffic
Duration: 60 seconds
Severity: Medium
Action: Analyze, notify
```

## Best Practices

### Prevention
- Implement BCP 38 (ingress filtering)
- Disable unnecessary services
- Use stateful firewalls
- Rate limit at edges
- Validate input
- Harden systems

### Detection
- Monitor baseline behavior
- Set appropriate thresholds
- Use multiple detection methods
- Log all security events
- Alert on anomalies
- Review logs regularly

### Response
- Have documented procedures
- Pre-define escalation
- Test playbooks
- Train team
- Establish partnerships
- Communicate effectively

### Recovery
- Document lessons learned
- Improve monitoring
- Update procedures
- Adjust thresholds
- Plan improvements
- Regular testing
