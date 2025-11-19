# Global Server Load Balancing (GSLB) Guide

## Overview
Global Server Load Balancing distributes traffic across geographically dispersed data centers, providing disaster recovery, performance optimization, and high availability.

## GSLB Architecture

### Multi-Data Center Setup
```
Data Center 1 (US East)
  - Production servers
  - Local load balancers
  - Health monitoring

Data Center 2 (EU Central)
  - Production servers
  - Local load balancers
  - Health monitoring

Data Center 3 (APAC)
  - Production servers
  - Local load balancers
  - Health monitoring

         ↓
    GSLB Layer
    (DNS + Health monitoring)
    Global decision engine

         ↓
    Client request
    Directed to optimal DC
```

## GSLB Deployment Models

### DNS-Based GSLB
**How It Works**:
1. Client queries DNS: "What's the IP for example.com?"
2. GSLB DNS server evaluates:
   - Client geographic location
   - Data center health status
   - Current latency metrics
3. Returns IP address of best data center
4. Client connects to returned IP

**Advantages**:
- Works with any client
- No special software needed
- Standards-based (DNS)

**Limitations**:
- DNS TTL delays failover
- No connection-level decisions
- Coarse-grained control

**Configuration Example**:
```
DNS Query: example.com A?

Processing:
  Client IP: 203.0.113.50 (New York area)
  ↓
  Geolocation lookup: US East Coast
  ↓
  Check data center health:
    US East: HEALTHY (all servers up)
    EU Central: HEALTHY (all servers up)
    APAC: DOWN (outage)
  ↓
  Select US East (closest AND healthy)
  ↓
  Return: 192.0.2.1 (US East IP)

Result: Client connects to US East data center
```

### Application-Layer GSLB
**How It Works**:
1. Client connects to local edge server
2. Edge server determines best data center
3. Redirects client to appropriate data center
4. Client reconnects to selected data center

**Methods**:
- HTTP 302 Redirect
- JavaScript detection + redirect
- CDN edge decision

**Advantages**:
- Real-time optimal decision
- Can inspect request content
- No DNS caching issues
- Per-request decisions

**Limitations**:
- Extra HTTP request (latency)
- Client must follow redirects
- More infrastructure needed

## Failover Strategies

### Active-Active (Full Mesh)
**Configuration**:
```
All data centers:
  - Serve production traffic
  - Accept new requests
  - Distributed load

Routing:
  Users → Nearest DC (if healthy)
  Users → Next nearest (if nearest down)
  Users → Any healthy (if multiple down)
```

**Normal Load Distribution**:
```
Total Users: 100,000

US East DC: 40,000 (40%)
EU Central DC: 35,000 (35%)
APAC DC: 25,000 (25%)
```

**Failover Scenario**:
```
EU Central DC Fails (health check fails)

New Distribution:
US East DC: 65,000 (65%)  [+25k from EU]
EU Central DC: 0 (down)
APAC DC: 35,000 (35%)  [+10k from EU]
```

**Recovery**:
```
EU Central Recovers (health check passes)

Return to:
US East DC: 40,000 (40%)
EU Central DC: 35,000 (35%)
APAC DC: 25,000 (25%)
```

### Active-Standby
**Configuration**:
```
Primary DC: Handles all traffic
Standby DC: Idle, monitoring primary

Health Check: Every 5 seconds
  Primary healthy? Route to primary
  Primary failed? Route to standby
```

**Load Distribution**:
```
Normal:
US East (Primary): 100,000 users (100%)
EU Central (Standby): 0 users (0%)

Failover:
US East (Primary): 0 users (down)
EU Central (Standby): 100,000 users (100%)
```

### N+1 Redundancy
**Configuration**:
```
3 Active Data Centers (N=3)
1 Standby Data Center (emergency reserve)

Normal Distribution:
DC1: 35,000 (35%)
DC2: 35,000 (35%)
DC3: 20,000 (20%)
DC4 (Standby): 10,000 (10%) [reduced, standby)

Single DC Failure:
Failing DC: 0
Remaining DCs + Standby: Absorb failed traffic
Standby increases to 40,000 (40%)

Multiple DC Failures:
Two DCs fail: Remaining DCs + Standby (overloaded)
System degraded but still operating
```

## Geographic Routing Implementation

### GeoIP-Based Routing

**Service**: AWS Route 53 Example
```yaml
DNS Record: www.example.com

Geolocation Rules:
  United States:
    Type: A
    Value: 192.0.2.1 (US DC)
    Health Check: us-dc-health

  Europe:
    Type: A
    Value: 192.0.2.2 (EU DC)
    Health Check: eu-dc-health

  Asia Pacific:
    Type: A
    Value: 192.0.2.3 (APAC DC)
    Health Check: apac-dc-health

  Default (Rest of World):
    Type: A
    Value: 192.0.2.4 (Fallback DC)
    Health Check: fallback-dc-health
```

**GeoIP Database Accuracy**:
```
Typical accuracy: 90%+ for country level
Regional accuracy: 70-80%
City-level accuracy: 60-70%

Limitations:
- VPN users show different location
- Proxy users show proxy location
- Cellular networks vary
- Database updates lag reality
```

### Latency-Based Routing

**Continuous Latency Probing**:
```
GSLB Health Check Agents:

US East DC:
  Probe latency to DC-US: 5ms
  Probe latency to DC-EU: 120ms
  Probe latency to DC-APAC: 180ms

EU Central DC:
  Probe latency to DC-US: 130ms
  Probe latency to DC-EU: 5ms
  Probe latency to DC-APAC: 160ms

APAC DC:
  Probe latency to DC-US: 190ms
  Probe latency to DC-EU: 150ms
  Probe latency to DC-APAC: 10ms
```

**Routing Decision**:
```
Client in Bangalore (APAC region):

Query arrives at GSLB
Check latency from client region to DCs:
  APAC DC: 10ms (lowest)
  EU DC: 150ms
  US DC: 190ms

Return: APAC DC IP
```

### Health-Aware Routing

**Health Status Evaluation**:
```
DC1 Status Check:
  Web Tier: HEALTHY (5/5 servers up)
  App Tier: DEGRADED (3/5 servers up)
  DB Tier: HEALTHY (replication running)
  Overall: DEGRADED

DC2 Status Check:
  Web Tier: HEALTHY (5/5 servers up)
  App Tier: HEALTHY (5/5 servers up)
  DB Tier: HEALTHY (replication running)
  Overall: HEALTHY

Routing Decision:
  New requests → DC2 (healthy)
  Existing → DC1 (if already connected)
  Health check interval: 5 seconds
```

## GSLB Implementation Platforms

### F5 Global Traffic Manager (GTM)
**Architecture**:
```
DNS Authority Servers
  ├─ GTM 1 (Primary)
  ├─ GTM 2 (Secondary)
  └─ GTM 3 (Tertiary)

Monitoring Agents:
  ├─ US East DC Monitor
  ├─ EU Central DC Monitor
  └─ APAC DC Monitor

Virtual Servers:
  ├─ US East LTM
  ├─ EU Central LTM
  └─ APAC LTM
```

### AWS Route 53
**Features**:
- Geolocation routing
- Latency-based routing
- Failover routing
- Weighted routing
- Multi-value answer routing

**Configuration**:
```
Hosted Zone: example.com

Record: www.example.com
  Type: A
  Alias: true
  Routing Policy: Latency
    Region: us-east-1, Value: ALB-1
    Region: eu-west-1, Value: ALB-2
    Region: ap-southeast-1, Value: ALB-3
  Health Checks: Enabled
```

### Azure Traffic Manager
**Features**:
- Priority-based routing
- Weighted routing
- Performance-based routing
- Geographic routing
- Multi-value routing
- Subnet-based routing

**Configuration**:
```
Profile: example-tm

Endpoints:
  - US East (type: Azure)
  - EU Central (type: Azure)
  - APAC (type: Azure)

Routing Method: Geographic

Health Check:
  Protocol: HTTPS
  Port: 443
  Path: /health
  Interval: 30 seconds
```

### GCP Cloud Load Balancing
**Features**:
- Global load balancing
- Anycast IP address
- HTTP/HTTPS and TCP/UDP
- Traffic splitting for canary

## Health Checking in GSLB

### Multi-Level Health Checks
```
Level 1: Network Check
  Can we reach the data center? (Ping, TCP)
  Result: DC reachable

Level 2: Service Check
  Is the load balancer responding? (TCP 443)
  Result: LB responding

Level 3: Application Check
  Is the application healthy? (HTTP /health)
  Result: App status: 200 OK

Overall Health Decision:
  All three pass = DC Healthy
  Any fails = DC Degraded/Down
```

### Health Check Configuration
```yaml
Data Center: US East

Health Checks:
  - Type: ICMP Ping
    Target: 203.0.2.1
    Interval: 10 seconds
    Timeout: 3 seconds
    Success Threshold: 1 pass
    Failure Threshold: 3 failures

  - Type: TCP
    Target: 203.0.2.1:443
    Interval: 10 seconds
    Timeout: 3 seconds
    Success Threshold: 2 passes
    Failure Threshold: 2 failures

  - Type: HTTP GET
    Target: 203.0.2.1/api/health
    Interval: 30 seconds
    Timeout: 5 seconds
    Expected Response: 200 OK
    Success Threshold: 2 passes
    Failure Threshold: 2 failures

Decision Logic:
  If network reachable AND LB responding AND app healthy
    → DC Status: HEALTHY
  If network reachable BUT app down
    → DC Status: DEGRADED
  If network unreachable
    → DC Status: DOWN
```

## Failover Testing

### Planned Failover Test
```
Objective: Verify failover works correctly

Procedure:
1. Note baseline traffic distribution
2. Manually disable primary DC in GSLB
3. Monitor GSLB response change
4. Verify traffic redirects to secondary
5. Monitor application metrics
6. Re-enable primary
7. Verify traffic returns

Metrics to Monitor:
  - Client traffic percentage per DC
  - Response time from each DC
  - Error rates
  - Connection count per DC
  - DNS query responses
```

### Failure Simulation
```
Scenario: Data center network becomes unreachable

Simulation Method:
1. Disconnect DC's network interface (simulated)
2. Or: Configure firewall to block health checks
3. Or: Shut down health monitoring agents

Expected Behavior:
  - Health checks fail (3-5 checks)
  - GSLB marks DC as DOWN (within 30 seconds)
  - New DNS queries return secondary DC IP
  - Existing connections continue (DNS cached)
  - Monitor metrics for impact

Validation:
  - Existing users unaffected (for TTL period)
  - New users routed to healthy DC
  - No data loss (depends on app)
```

## Best Practices

1. **TTL Optimization**
   - Normal: 300-600 seconds
   - During migration: 60 seconds
   - Balance: Failover speed vs DNS load

2. **Health Check Tuning**
   - Interval: 5-30 seconds
   - Avoid false positives
   - Test thresholds thoroughly

3. **Capacity Planning**
   - Ensure failover DC can handle full load
   - Monitor growth trends
   - Plan upgrades ahead

4. **Geographic Redundancy**
   - GSLB servers in multiple locations
   - Independent health check agents
   - Prevents single point of failure

5. **Monitoring**
   - Alert on DC status changes
   - Monitor DNS query patterns
   - Track failover events
   - Alert on unusual latency

6. **Testing**
   - Regular failover drills
   - Test failback procedures
   - Verify during low-traffic times
   - Document findings

7. **Documentation**
   - GSLB configuration details
   - Health check logic
   - Failover procedures
   - Contact escalation

---

**Last Updated**: 2025-11-19
**Version**: 2.0
