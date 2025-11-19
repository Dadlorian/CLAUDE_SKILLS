# DNS Load Balancing Reference

## DNS Load Balancing Overview

### Basic Concept
```
DNS returns multiple IP addresses for single domain
Client selects one and connects

example.com A records:
- 192.0.2.1 (Server 1)
- 192.0.2.2 (Server 2)
- 192.0.2.3 (Server 3)

Client query -> DNS returns all three -> Client picks one
```

### Load Distribution Methods
1. **Round-Robin**: Even distribution across responses
2. **Weighted**: Proportional distribution (30% / 20% / 50%)
3. **Geolocation**: Based on client location
4. **Latency-Based**: Route to lowest latency endpoint
5. **Health-Check Based**: Exclude unhealthy servers

## Round-Robin DNS

### Simple Round-Robin
```
Zone file:
example.com    3600    IN    A    192.0.2.1
example.com    3600    IN    A    192.0.2.2
example.com    3600    IN    A    192.0.2.3

Query 1: Returns [192.0.2.1, 192.0.2.2, 192.0.2.3]
Query 2: Returns [192.0.2.2, 192.0.2.3, 192.0.2.1]
Query 3: Returns [192.0.2.3, 192.0.2.1, 192.0.2.2]

Rotating order achieves distribution
```

### Advantages
- Simple to implement
- No additional infrastructure
- Scales easily (add more A records)

### Disadvantages
- No real health checking (returns all records)
- Can direct traffic to failed servers
- Client must detect failure and retry
- Doesn't account for server capacity differences

## Weighted Round-Robin

### Implementation via SRV Records
```
_service._tcp.example.com    3600    IN    SRV    10    70    5060    server1.example.com.
_service._tcp.example.com    3600    IN    SRV    10    20    5060    server2.example.com.
_service._tcp.example.com    3600    IN    SRV    10    10    5060    server3.example.com.

Format: Priority, Weight, Port, Target
Same priority (10) - use weights (70:20:10)
Total weight: 100
- server1: 70% of traffic
- server2: 20% of traffic
- server3: 10% of traffic
```

### Route53 Weighted Routing
```
Record 1: api.example.com -> 192.0.2.1 (Weight: 70, SetID: server1)
Record 2: api.example.com -> 192.0.2.2 (Weight: 20, SetID: server2)
Record 3: api.example.com -> 192.0.2.3 (Weight: 10, SetID: server3)

Traffic distribution:
- 70% routed to 192.0.2.1
- 20% routed to 192.0.2.2
- 10% routed to 192.0.2.3
```

### Use Cases
- Canary deployments (10% to new version, 90% to stable)
- Gradual traffic migration
- Testing with real traffic
- Capacity-based distribution

## Geolocation-Based Routing

### GeoIP Database Lookup
```
Client in New York -> GeoIP lookup -> Returns NYC endpoint (192.0.2.1)
Client in London -> GeoIP lookup -> Returns London endpoint (192.0.2.2)
Client in Tokyo -> GeoIP lookup -> Returns Tokyo endpoint (192.0.2.3)
```

### Implementation

#### Route53 Geolocation Routing
```
Record 1:
- Location: North America
- Value: 192.0.2.1 (North America CDN)
- SetID: NorthAmerica

Record 2:
- Location: Europe
- Value: 192.0.2.2 (Europe CDN)
- SetID: Europe

Record 3:
- Location: Asia Pacific
- Value: 192.0.2.3 (APAC CDN)
- SetID: AsiaPacific

Default:
- Location: Default (catch-all)
- Value: 192.0.2.1 (primary global)
```

#### Cloudflare Geographic Routing
```
Terraform:
resource "cloudflare_load_balancer" "example" {
  zone_id = var.zone_id
  name    = "lb.example.com"

  default_pools = ["default-pool"]

  region_pools {
    region = "WNAM"  # Western North America
    pool_ids = ["west-pool"]
  }

  region_pools {
    region = "ENAM"  # Eastern North America
    pool_ids = ["east-pool"]
  }
}
```

### Accuracy Considerations
- GeoIP accuracy: 90-99% city level, 99%+ country level
- ASN routing: More accurate than GeoIP alone
- Fallback strategy: Handle clients outside defined regions

## Latency-Based Routing

### Implementation
```
AWS Route53 Latency-Based Routing:

Record 1:
- Region: us-east-1
- IP: 192.0.2.1
- SetID: east-server

Record 2:
- Region: eu-west-1
- IP: 192.0.2.2
- SetID: europe-server

Record 3:
- Region: ap-southeast-1
- IP: 192.0.2.3
- SetID: asia-server

Client in Virginia -> Routes to us-east-1 (lowest latency)
Client in Frankfurt -> Routes to eu-west-1 (lowest latency)
Client in Singapore -> Routes to ap-southeast-1 (lowest latency)
```

### Latency Measurement
```
Measurement methods:
1. BGP AS Path analysis (hop count)
2. ICMP ping measurements
3. TCP handshake latency
4. DNS query latency historical data

Route53 uses:
- Cached latency measurements from previous queries
- Updates periodically with actual measurements
- Client location + endpoint region mapping
```

### Limitations
- Assumes client location = client network location
- VPN clients may appear in wrong region
- Doesn't measure actual application latency

## Health-Check Based Routing

### Health Check Types

#### TCP Health Check
```
Health checker connects to port:
- TCP handshake success = healthy
- Connection timeout/refused = unhealthy

Example:
Route53 health check:
- Type: TCP
- IP: 192.0.2.1
- Port: 80
- Interval: 30 seconds
- Failure threshold: 3 consecutive failures
```

#### HTTP Health Check
```
Health checker sends HTTP GET request:
- Response code 200-299 = healthy
- Any other code = unhealthy

Example:
Route53 health check:
- Type: HTTP
- IP: 192.0.2.1
- Path: /health
- Port: 80
- Expected response: 200
```

#### HTTPS Health Check
```
Identical to HTTP but with TLS encryption:
- Valid certificate required
- Hostname verification
- Response code 200-299 = healthy
```

#### Calculated Health Check
```
Combine multiple health checks with logic:

Healthy if (Server1 + Server2) = 2 healthy endpoints
- Server 1: TCP port 443 (weight 1)
- Server 2: TCP port 443 (weight 1)
- Threshold: 1 (require at least 1 healthy)

Enables dependencies and failover chains
```

### Health Check Monitoring
```
CloudWatch integration:
- Metrics: Health check status
- Alarms: Notify when unhealthy
- Logs: Health check history

Example alarm:
- If health check unhealthy for > 3 minutes
- Send SNS notification
- Trigger auto-scaling or manual intervention
```

## Failover Routing

### Active-Passive Failover
```
Active: 192.0.2.1 (primary)
Passive: 192.0.2.2 (secondary/failover)

Primary healthy?
  YES -> Return 192.0.2.1
  NO  -> Return 192.0.2.2

Route53 Configuration:
Record 1:
- Type: A
- Value: 192.0.2.1 (primary)
- Routing Policy: Failover
- Failover Record Type: Primary
- Health Check: Route53 health check

Record 2:
- Type: A
- Value: 192.0.2.2 (secondary)
- Routing Policy: Failover
- Failover Record Type: Secondary
```

### Health Check Interval Impact
```
Failover speed = Health check interval + failure threshold

Health check interval: 10 seconds
Failure threshold: 3 failures
Maximum failover time: ~30 seconds

Fast failover:
- Interval: 10 seconds
- Threshold: 1
- Failover time: ~10 seconds

Stable failover (avoids flapping):
- Interval: 30 seconds
- Threshold: 3
- Failover time: ~90 seconds
```

## Multi-Region Load Balancing

### Hierarchy
```
Global Load Balancer
├── North America
│   ├── East Coast (192.0.2.1)
│   └── West Coast (192.0.2.2)
├── Europe
│   ├── UK (192.0.2.3)
│   └── Germany (192.0.2.4)
└── Asia Pacific
    ├── Singapore (192.0.2.5)
    └── Tokyo (192.0.2.6)

Query from New York:
→ GeoLocation routing → North America
→ Latency routing → East Coast (192.0.2.1)
→ Health check → If unhealthy → Failover
```

### Implementation Pattern
```
Terraform:
resource "aws_route53_record" "global" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "global"
  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = aws_route53_record.region_us.fqdn
    zone_id                = aws_route53_zone.main.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.global.id
}
```

## Weighted Failover

### Combined Weighted + Failover
```
api.example.com has 3 servers (grouped by failover):

Group 1 (Primary):
- 192.0.2.1 weight 70
- 192.0.2.2 weight 30

Group 2 (Secondary):
- 192.0.2.3 weight 100

Healthy state:
- 70% to 192.0.2.1
- 30% to 192.0.2.2

Primary Group fails (both unhealthy):
- 100% to 192.0.2.3
```

## Connection Draining

### Graceful Shutdown Pattern
```
Health check implementation:
1. Mark server for removal (drain state)
2. Health check returns unhealthy status
3. DNS stops returning server IP
4. Existing connections complete gracefully
5. Server shuts down

DNS TTL considerations:
- TTL 300: Clients forget old IP in 5 minutes max
- TTL 60: Clients forget old IP in 1 minute max
- TTL 5: Immediate old IP removal (aggressive)

Balancing: TTL 60-300 for graceful drains
```

## DNS Load Balancing Best Practices

1. **Health Checks**: Always include health checks
2. **TTL Strategy**: Short TTL (60-300s) for rapid failover
3. **Multiple Records**: Minimum 2 for redundancy
4. **Monitoring**: Alert on health check failures
5. **Testing**: Test failover scenarios regularly
6. **Geolocation**: Consider latency + geography
7. **Weights**: Use for capacity-based distribution
8. **Failover**: Implement active-passive strategy
9. **Client Timeout**: Configure client retry logic
10. **Documentation**: Map DNS routing decision tree
