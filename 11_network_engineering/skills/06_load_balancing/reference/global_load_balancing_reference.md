# Global Server Load Balancing (GSLB) Reference

## Overview
Global Server Load Balancing distributes traffic across geographically distributed data centers, providing geographic failover, performance optimization, and disaster recovery capabilities.

## GSLB Fundamentals

### What is GSLB?
**Definition**: Load balancing that operates at the DNS level, directing clients to optimal servers based on geographic location, health status, and performance metrics.

**Key Characteristics**:
- Operates at DNS layer (DNS-based)
- Responds to DNS queries with appropriate IP addresses
- Considers geographic location
- Tracks health of remote sites
- Enables disaster recovery
- Optimizes performance across regions

### GSLB vs Local Load Balancing

| Aspect | Local LB | GSLB |
|--------|----------|------|
| Layer | Transport/Application (L4/L7) | DNS (L3) |
| Scope | Single data center | Multiple data centers |
| Decision Point | Per connection | Per DNS query |
| Granularity | Per session | Per client |
| Protocol | TCP/UDP/HTTP | DNS |
| Failover Time | Seconds | Seconds to minutes |
| Complexity | Medium | High |

## GSLB Routing Methods

### Geographic Routing
**Description**: Routes clients to nearest data center based on geographic location.

**How It Works**:
```
DNS Query from Client IP
        ↓
    GeoIP Database Lookup
        ↓
    Determine Client Location
        ↓
    Find Nearest Data Center
        ↓
    Return IP of Nearest DC
```

**Example Configuration**:
```
Region: North America
  Client IP: 203.0.113.100 (New York)
  Nearest DC: East Coast (DC-1)
  Return IP: 192.0.2.1

Region: Europe
  Client IP: 198.51.100.200 (London)
  Nearest DC: EU-Central (DC-2)
  Return IP: 192.0.2.2

Region: Asia Pacific
  Client IP: 192.0.2.50 (Tokyo)
  Nearest DC: APAC (DC-3)
  Return IP: 192.0.2.3
```

**Advantages**:
- Latency optimization
- Network efficiency
- Better user experience
- Reduced WAN usage

**Disadvantages**:
- GeoIP database accuracy (may be wrong)
- Doesn't account for network congestion
- Client location != backend optimal location

### Latency-Based Routing
**Description**: Measures latency to each data center and routes to lowest latency option.

**How It Works**:
```
GSLB Probe Servers:
  → Probe DC-1: Average latency 50ms
  → Probe DC-2: Average latency 120ms
  → Probe DC-3: Average latency 80ms

Routing Decision:
  Client gets DC-1 IP (lowest latency)
```

**Probing Methods**:
```
1. ICMP Ping
   Pros: Simple, fast
   Cons: Often blocked by firewalls

2. TCP Probe
   Pros: Works through firewalls
   Cons: Slower than ICMP

3. Application-Level Probe
   Pros: Measures real latency
   Cons: More overhead

4. Continuous Measurement
   Pros: Real-time updates
   Cons: Requires agent/collector
```

**Configuration Example**:
```
Probing Method: TCP to port 443
Probe Interval: 10 seconds
Sample Size: Last 10 probes
Decision: Weighted average latency
Update Frequency: Every minute
```

**Advantages**:
- Performance optimized
- Real latency data
- Adapts to network conditions
- Dynamic responses

**Disadvantages**:
- Requires continuous probing
- Probe results can be stale
- Client's latency ≠ typical latency
- Potential for cascading overload

### Health-Based Routing
**Description**: Routes only to healthy data centers.

**How It Works**:
```
Health Status:
  DC-1: HEALTHY (all services up)
  DC-2: DEGRADED (partial outage)
  DC-3: DOWN (offline)

Routing:
  All queries → DC-1 (or DC-2 if DC-1 down)
  DC-3 never receives queries (down)
```

**Health Check Configuration**:
```
Check Type: HTTP GET /health-check
Interval: 5 seconds
Timeout: 3 seconds
Healthy Threshold: 2
Unhealthy Threshold: 3

Status Transition:
  3 consecutive failures → Mark DOWN
  2 consecutive successes → Mark UP
```

**Advantages**:
- Prevents routing to failed DCs
- Automatic failover
- No manual intervention needed
- Maintains availability

**Disadvantages**:
- Failover not instantaneous
- DNS TTL delay
- All traffic redirects to healthy DC (possible overload)

### Weighted Round Robin GSLB
**Description**: Distributes DNS responses with assigned weights to each data center.

**Configuration Example**:
```
DC-1 (Primary): Weight 70
DC-2 (Secondary): Weight 20
DC-3 (Tertiary): Weight 10

Distribution:
  70% queries return DC-1 IP
  20% queries return DC-2 IP
  10% queries return DC-3 IP
```

**Use Cases**:
- Gradual traffic migration
- Testing new data center
- Capacity-aware distribution
- A/B testing across regions

### Performance Policy Routing
**Description**: Advanced routing combining multiple factors.

**Factors Considered**:
```
1. Geographic location (30% weight)
2. Current latency (40% weight)
3. Data center capacity (20% weight)
4. Health status (10% weight)

Score = 0.3*geo + 0.4*latency + 0.2*capacity + 0.1*health
Highest score → Selected DC
```

**Configuration Example**:
```
Primary Routing: Latency-based
Secondary Routing: Geographic
Fallback Routing: Health-based
Load Balancing: Weighted
```

## GSLB Failover Strategies

### Active-Active (Full Mesh)
**Configuration**:
```
DC-1 ↔ DC-2
DC-1 ↔ DC-3
DC-2 ↔ DC-3

All DCs:
  - Serve production traffic
  - Route to multiple DCs
  - Share load equally or weighted
```

**Advantages**:
- Maximum resource utilization
- No idle capacity
- Better ROI

**Disadvantages**:
- Complex configuration
- Potential cascading failures
- Requires session replication
- Careful traffic distribution needed

**Failover Scenario**:
```
Normal:
  Clients → DC-1: 50%
         → DC-2: 50%

DC-1 Fails:
  Clients → DC-2: 100%
  (DC-2 now handles double load)
```

### Active-Standby
**Configuration**:
```
DC-1 (Primary, Active)
  ↓ (serves all traffic)
DC-2 (Secondary, Standby)
  (waits for DC-1 failure)

Failover:
  DC-1 health check fails
  GSLB re-evaluates
  DC-2 now serves all traffic
```

**Advantages**:
- Simple configuration
- Clear primary/secondary
- Predictable behavior
- Easier troubleshooting

**Disadvantages**:
- Capacity waste (standby idle)
- More expensive
- Longer failover (DNS TTL)
- Less efficient resource use

### N+1 Redundancy
**Configuration**:
```
Active DCs: N (e.g., 2 or 3)
Standby DCs: 1 (for any failure)

Normal:
  DC-1: 40%
  DC-2: 40%
  DC-3: 20% (reduced traffic)

DC-1 Fails:
  DC-2: 40%
  DC-3: 60% (increases to full capacity)
```

**Advantages**:
- Handles single failure
- Less idle capacity than Active-Standby
- More efficient than full Active-Active

**Disadvantages**:
- Can't handle multiple simultaneous failures
- Requires capacity planning
- Reduced redundancy with multiple failures

## GSLB Implementation Methods

### DNS-Based GSLB
**How It Works**:
```
Client: "What's the IP for example.com?"
  ↓
Authoritative DNS Server (GSLB-enabled)
  - Check client IP
  - Evaluate health status
  - Calculate best DC
  ↓
Response: "example.com = 192.0.2.1 (DC-1)"
  ↓
Client connects to DC-1
```

**Configuration Example**:
```yaml
Zone: example.com
Record: www
Type: A (or AAAA for IPv6)
TTL: 60 seconds (short for fast failover)

Responses:
  Query from US: 192.0.2.1 (US DC IP)
  Query from EU: 192.0.2.2 (EU DC IP)
  Query from APAC: 192.0.2.3 (APAC DC IP)
```

**Advantages**:
- No application changes needed
- Works with all clients
- Standards-based (DNS)
- No special client software

**Disadvantages**:
- DNS TTL limits failover speed
- Clients cache DNS responses
- Cannot do connection-level decisions
- DNS query response time adds latency

### Application-Layer GSLB
**How It Works**:
```
Client requests web page
  ↓
Server responds with redirect URL
  ↓
Client: HTTP 302 Redirect → best.datacenter.example.com
  ↓
Client follows redirect
  ↓
Connected to optimal DC
```

**Implementation Methods**:
1. HTTP Redirect
2. JavaScript Geolocation
3. CDN Edge Decision
4. Load Balancer Redirect

**Advantages**:
- Real-time optimization
- Can base on request content
- More intelligent decisions
- Faster failover (no DNS TTL)

**Disadvantages**:
- Extra HTTP request (latency)
- Requires application support
- Browser redirect overhead
- Doesn't work for non-HTTP protocols

### GeoDNS
**Definition**: DNS service that returns different responses based on client geography.

**Services**:
- AWS Route 53
- Azure Traffic Manager
- Google Cloud DNS
- Akamai DNS
- F5 GTM

**Configuration Example** (AWS Route 53):
```
Record: www.example.com
Type: A record
Policy: Geolocation

North America: 192.0.2.1 (US DC)
Europe: 192.0.2.2 (EU DC)
Asia Pacific: 192.0.2.3 (APAC DC)
Default (Other): 192.0.2.4 (Default DC)

Health Checks:
  Each IP has health check
  If health check fails, use next preference
```

## GSLB Performance Considerations

### DNS TTL (Time To Live)
**TTL Impact on Failover**:
```
TTL: 3600 seconds (1 hour)
  - Client caches 1 hour
  - Failover takes 60 minutes (longest case)
  - Users might be routed to dead DC for up to 1 hour

TTL: 60 seconds (1 minute)
  - Client caches 1 minute
  - Failover takes ~2 minutes (in most cases)
  - More DNS queries (higher load)

TTL: 5 seconds (aggressive)
  - Failover takes ~10 seconds
  - Very high DNS query load
  - Not recommended for most scenarios
```

**Optimal TTL Strategy**:
```
Normal Conditions: TTL = 300 seconds (5 minutes)
  - Balance between failover speed and DNS load

During Maintenance: TTL = 60 seconds
  - Faster propagation of configuration changes

Gradual Migration: TTL = 60 seconds
  - Faster switch between DCs
```

### DNS Query Load
**Estimation**:
```
TTL: 60 seconds
Domain: example.com
Users: 100,000
Average Session: 30 minutes

Queries per hour:
  = Users × (60 minutes / TTL seconds) × 60 seconds
  = 100,000 × (60 / 60) × 60 / 3600
  ≈ 100,000 queries/hour
  ≈ 27 queries/second

With 5-second TTL:
  = 100,000 × (60 / 5) × 60 / 3600
  ≈ 2,000 queries/second (High load!)
```

### Latency Considerations
**End-to-End Latency with GSLB**:
```
Traditional:
  Client → LB → Backend: 20ms

With GSLB:
  Client → Local DNS: 5ms
  Local DNS → Authoritative DNS: 30ms
  Authoritative DNS response: 5ms
  Client → Selected DC: 20ms
  Total: ~60ms (more overhead)

Plus DNS Caching (if hit): ~5ms total
```

## GSLB Failure Modes

### Scenario 1: Primary DC Failure
```
Normal:
  50% traffic → DC-1
  50% traffic → DC-2

DC-1 Fails (immediately):
  - GSLB detects failure
  - Stops returning DC-1 IP
  - New queries get DC-2 IP
  - Clients with cached DC-1 IP attempt connection
    - Connection timeout/failure
    - Client retries
    - Gets DC-2 from new DNS query

Impact:
  - Clients without cache: Transparent failover
  - Clients with cache: 1-5 minute disruption
```

### Scenario 2: DNS Server Failure
```
GSLB DNS server goes down
  - Queries to this server fail
  - DNS resolvers retry with different servers
  - Eventual resolution succeeds
  - Failover transparent

Impact: Minimal (DNS redundancy)
```

### Scenario 3: Network Partition
```
DC-1 and DC-2 separated by network failure
  - Health checks might show both "up"
  - Or both "down" (depending on GSLB location)
  - Split-brain scenario

Solution:
  - Quorum-based health determination
  - GSLB server location affects decision
  - Prefer smaller subset over larger
```

## GSLB Best Practices

1. **Multiple GSLB servers** - At least 3 for redundancy
2. **Health check frequency** - 5-10 second intervals
3. **TTL optimization** - Balance failover speed vs DNS load
4. **Session replication** - For active-active setup
5. **Capacity planning** - Ensure failover capacity
6. **Monitoring** - Alert on GSLB issues
7. **Disaster recovery** - Test failover scenarios
8. **Geographic redundancy** - GSLB servers in multiple DCs
9. **Documentation** - Clear routing policies
10. **Testing** - Simulate failures regularly

---

**Last Updated**: 2025-11-19
**Version**: 2.0
