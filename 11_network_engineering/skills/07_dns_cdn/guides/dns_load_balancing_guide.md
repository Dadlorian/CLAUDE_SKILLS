# DNS Load Balancing Implementation Guide

## Architecture Overview

```
┌─────────────┐
│  Client     │
└──────┬──────┘
       │ DNS Query: api.example.com
       │
┌──────▼──────────────────────────────┐
│  Authoritative DNS with Health Check│
├──────────────────────────────────────┤
│  Option 1: 192.0.2.1 (Primary)      │
│  Option 2: 192.0.2.2 (Secondary)    │
│  Option 3: 192.0.2.3 (Tertiary)     │
└──────────────────────────────────────┘
       │
       │ Returns: [192.0.2.1, 192.0.2.2]
       │ (if 192.0.2.1 healthy)
       │
┌──────▼──────────────────────────────┐
│  Client Application                  │
├──────────────────────────────────────┤
│  Try 192.0.2.1 (preferred)           │
│  Fallback to 192.0.2.2 (if fails)    │
└──────────────────────────────────────┘
```

## Prerequisites

- Authoritative DNS server (BIND, PowerDNS, etc.)
- Health checking infrastructure
- Multiple backend servers
- Monitoring system

## Step 1: Prepare Backend Servers

### Server Setup
```
Server 1 (East Coast):
IP: 192.0.2.1
Region: us-east-1
Capacity: 100 Mbps
Health endpoint: /health

Server 2 (West Coast):
IP: 192.0.2.2
Region: us-west-2
Capacity: 80 Mbps
Health endpoint: /health

Server 3 (Europe):
IP: 192.0.2.3
Region: eu-west-1
Capacity: 50 Mbps
Health endpoint: /health
```

### Health Check Endpoint
```
# Configure HTTP health check endpoint
GET /health HTTP/1.1

Response (healthy):
HTTP/1.1 200 OK
Content-Type: application/json

{"status": "healthy", "version": "1.0"}

Response (unhealthy):
HTTP/1.1 503 Service Unavailable

{"status": "unhealthy", "reason": "database_offline"}
```

## Step 2: Configure Simple Round-Robin

### Zone File Configuration
```
api.example.com    3600    IN    A    192.0.2.1
api.example.com    3600    IN    A    192.0.2.2
api.example.com    3600    IN    A    192.0.2.3
```

### How It Works
```
Query 1: Returns [192.0.2.1, 192.0.2.2, 192.0.2.3]
Query 2: Returns [192.0.2.2, 192.0.2.3, 192.0.2.1]
Query 3: Returns [192.0.2.3, 192.0.2.1, 192.0.2.2]

Order rotates, clients pick first (usually)
Result: Even distribution
```

### Test
```bash
# Query multiple times
for i in {1..10}; do
  dig @ns1.example.com api.example.com +short
done

# Should see different order each query
```

Limitation: No health checking (returns all even if one is down)

## Step 3: Configure Weighted Round-Robin with SRV Records

### SRV Record Configuration
```
_http._tcp.api.example.com    3600    IN    SRV    10    70    80    server1.example.com.
_http._tcp.api.example.com    3600    IN    SRV    10    20    80    server2.example.com.
_http._tcp.api.example.com    3600    IN    SRV    10    10    80    server3.example.com.

; A records for servers
server1    IN    A    192.0.2.1
server2    IN    A    192.0.2.2
server3    IN    A    192.0.2.3
```

### How It Works
```
Format: priority weight port target

Same priority (10) = use weights
Total weight: 100
- server1: 70% of connections
- server2: 20% of connections
- server3: 10% of connections

Ideal for:
- Capacity-based distribution
- Canary deployments
- Gradual traffic shifts
```

### Test
```bash
dig @ns1.example.com _http._tcp.api.example.com SRV

# Response:
# _http._tcp.api.example.com. 3600 IN SRV 10 70 80 server1.example.com.
# _http._tcp.api.example.com. 3600 IN SRV 10 20 80 server2.example.com.
# _http._tcp.api.example.com. 3600 IN SRV 10 10 80 server3.example.com.
```

## Step 4: Configure AWS Route53 Geolocation Load Balancing

### Terraform Configuration
```hcl
# East Coast
resource "aws_route53_record" "api_us_east" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-us-east"
  geolocation_routing_policy {
    country = "US"
  }

  alias {
    name                   = aws_lb.us_east.dns_name
    zone_id                = aws_lb.us_east.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.us_east.id
}

# Europe
resource "aws_route53_record" "api_eu" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-eu"
  geolocation_routing_policy {
    country = "DE"
  }

  alias {
    name                   = aws_lb.eu_central.dns_name
    zone_id                = aws_lb.eu_central.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.eu_central.id
}

# Default fallback
resource "aws_route53_record" "api_default" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-default"
  geolocation_routing_policy {
    country = "*"
  }

  alias {
    name                   = aws_lb.us_east.dns_name
    zone_id                = aws_lb.us_east.zone_id
    evaluate_target_health = true
  }
}
```

## Step 5: Configure Health Checks

### AWS Route53 Health Check
```hcl
resource "aws_route53_health_check" "us_east" {
  ip_address        = "192.0.2.1"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30

  measure_latency = true
  enable_sni      = true

  tags = {
    Name = "US-East-Health-Check"
  }
}

resource "aws_cloudwatch_metric_alarm" "us_east_health" {
  alarm_name          = "us-east-health-check-failed"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HealthCheckStatus"
  namespace           = "AWS/Route53"
  period              = "60"
  statistic           = "Minimum"
  threshold           = "1"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    HealthCheckId = aws_route53_health_check.us_east.id
  }
}
```

### Custom Health Check Script
```bash
#!/bin/bash
# health-check.sh

for server in 192.0.2.1 192.0.2.2 192.0.2.3; do
    response=$(curl -s -o /dev/null -w "%{http_code}" https://$server/health)

    if [ "$response" = "200" ]; then
        echo "$server: HEALTHY"
        # Update DNS to include this server
    else
        echo "$server: UNHEALTHY"
        # Remove from DNS rotation
        # Via API call to Route53, PowerDNS, etc.
    fi
done
```

## Step 6: Configure Failover

### Route53 Weighted Failover
```hcl
# Primary endpoint
resource "aws_route53_record" "api_primary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-primary"
  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = aws_lb.us_east.dns_name
    zone_id                = aws_lb.us_east.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.us_east.id
}

# Secondary endpoint (used if primary fails)
resource "aws_route53_record" "api_secondary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-secondary"
  failover_routing_policy {
    type = "SECONDARY"
  }

  alias {
    name                   = aws_lb.eu_central.dns_name
    zone_id                = aws_lb.eu_central.zone_id
    evaluate_target_health = true
  }
}
```

### Failover Timeline
```
Time 0:
- US East Primary: HEALTHY
- EU Secondary: STANDBY
- DNS returns: 192.0.2.1

Time T:
- US East Primary: HEALTH CHECK FAILS
- Health check reports failure

Time T+30s:
- Route53 detects PRIMARY unhealthy
- Route53 switches to SECONDARY
- DNS now returns: 192.0.2.3

Time T+30-60s:
- Clients' DNS caches expire (TTL=60s)
- New queries get EU endpoint
- Traffic redirects

Failover latency: 30 seconds + TTL
```

## Step 7: Configure Latency-Based Routing

### Route53 Latency-Based
```hcl
# US-East endpoint
resource "aws_route53_record" "api_us_east_latency" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-us-east"
  latency_routing_policy {
    region = "us-east-1"
  }

  alias {
    name                   = aws_lb.us_east.dns_name
    zone_id                = aws_lb.us_east.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.us_east.id
}

# EU-Central endpoint
resource "aws_route53_record" "api_eu_latency" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-eu-central"
  latency_routing_policy {
    region = "eu-central-1"
  }

  alias {
    name                   = aws_lb.eu_central.dns_name
    zone_id                = aws_lb.eu_central.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.eu_central.id
}

# APAC endpoint
resource "aws_route53_record" "api_apac_latency" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-ap-southeast"
  latency_routing_policy {
    region = "ap-southeast-1"
  }

  alias {
    name                   = aws_lb.ap_southeast.dns_name
    zone_id                = aws_lb.ap_southeast.zone_id
    evaluate_target_health = true
  }

  health_check_id = aws_route53_health_check.ap_southeast.id
}
```

### How Route53 Measures Latency
```
Route53 measures latency from previous queries
Updates latency data periodically
Routes to lowest-latency endpoint

Client in New York:
  - Previous query latency to US-East: 5ms
  - Previous query latency to EU: 100ms
  - Routed to US-East (lowest)

Client in Frankfurt:
  - Previous query latency to EU: 10ms
  - Previous query latency to US-East: 80ms
  - Routed to EU (lowest)
```

## Step 8: Test and Monitor

### Test from Multiple Locations
```bash
# Test from different regions
dig @8.8.8.8 api.example.com A

# Should get different responses based on location
# From USA: 192.0.2.1
# From EU: 192.0.2.2
# From Asia: 192.0.2.3
```

### Monitoring
```bash
#!/bin/bash
# monitor-lb.sh

ZONE=example.com
API_HOST=api.$ZONE

while true; do
    # Query DNS
    ips=$(dig @ns1.$ZONE $API_HOST A +short)

    # Test each IP
    for ip in $ips; do
        response=$(curl -s -o /dev/null -w "%{http_code}" https://$ip/health)
        echo "$(date): $ip -> $response"
    done

    sleep 30
done
```

### Metrics
```
Track:
1. DNS query response time (should be <50ms)
2. Health check status (% healthy per endpoint)
3. Traffic distribution (% traffic per endpoint)
4. Failover events (when endpoints switched)

Dashboard in CloudWatch/Grafana:
- DNS latency percentiles (p50, p95, p99)
- Health check status timeseries
- Traffic distribution pie chart
- Failover event log
```

## Step 9: Configure TTL Strategy

### TTL Considerations
```
Short TTL (60 seconds):
Pros:
  - Rapid failover (clients forget old IP quickly)
  - Quick to adapt to changes

Cons:
  - Higher DNS load
  - More cache misses
  - Higher origin traffic

Long TTL (3600+ seconds):
Pros:
  - Lower DNS load
  - Better cache hit rate
  - Reduced origin traffic

Cons:
  - Slower failover (up to TTL seconds)
  - Longer to adapt to changes

Recommendation:
- Failover required: TTL 60-300 seconds
- Static service: TTL 3600 seconds
- Balance: TTL 300 seconds
```

## Step 10: Implement Client-Side Failover

### Client Implementation (Python)
```python
import socket
import time

class DNSClient:
    def __init__(self, domain, ttl_cache=300):
        self.domain = domain
        self.ttl_cache = ttl_cache
        self.cache_time = 0
        self.endpoints = []

    def get_endpoint(self):
        """Get endpoint, refresh if TTL expired"""
        now = time.time()

        if not self.endpoints or (now - self.cache_time) > self.ttl_cache:
            # Refresh from DNS
            try:
                self.endpoints = socket.gethostbyname_ex(self.domain)[2]
                self.cache_time = now
            except socket.gaierror:
                return None

        return self.endpoints[0] if self.endpoints else None

    def request(self, path, timeout=5):
        """Make request with failover"""
        endpoints = self.endpoints if self.endpoints else [self.domain]

        for endpoint in endpoints:
            try:
                # Try endpoint
                response = requests.get(
                    f"https://{endpoint}{path}",
                    timeout=timeout
                )
                return response
            except requests.exceptions.RequestException:
                continue  # Try next endpoint

        raise Exception(f"All endpoints failed for {self.domain}")

# Usage
client = DNSClient("api.example.com")
response = client.request("/api/users")
```

### Client Implementation (JavaScript)
```javascript
class DNSClient {
    constructor(domain, ttl = 300) {
        this.domain = domain;
        this.ttl = ttl;
        this.endpoints = [];
        this.cacheTime = 0;
    }

    async getEndpoints() {
        const now = Date.now();

        if (this.endpoints.length === 0 ||
            (now - this.cacheTime) > this.ttl * 1000) {
            // Refresh from DNS (via /dns-lookup endpoint)
            const response = await fetch(`/dns-lookup?domain=${this.domain}`);
            this.endpoints = await response.json();
            this.cacheTime = now;
        }

        return this.endpoints;
    }

    async request(path, options = {}) {
        const endpoints = await this.getEndpoints();

        for (const endpoint of endpoints) {
            try {
                const response = await fetch(
                    `https://${endpoint}${path}`,
                    { ...options, timeout: 5000 }
                );
                return response;
            } catch (error) {
                continue; // Try next endpoint
            }
        }

        throw new Error(`All endpoints failed for ${this.domain}`);
    }
}

// Usage
const client = new DNSClient("api.example.com");
const response = await client.request("/api/users");
```

## Production Checklist

- [ ] Multiple backend servers deployed and tested
- [ ] Health check endpoints configured on all servers
- [ ] DNS records created for all endpoints
- [ ] Health checks configured and verified
- [ ] Failover tested (manually bring down server)
- [ ] TTL set appropriately for your failover RTO
- [ ] Monitoring and alerting in place
- [ ] Client-side failover implemented
- [ ] Disaster recovery plan documented
- [ ] Load distribution verified (traffic analysis)
- [ ] Performance tested (latency, throughput)
- [ ] Documentation updated

## Troubleshooting

### Issue: Endpoints Not Distributing Evenly
```
Problem: All queries getting same server

Causes:
1. Client caching results
2. Resolver caching results
3. TTL too long

Solutions:
1. Lower TTL for testing
2. Clear resolver cache
3. Query from different resolvers
4. Check router/ISP caching
```

### Issue: Failover Not Working
```
Problem: Failed server still getting traffic

Causes:
1. Health check not detecting failure
2. TTL not expired yet
3. Client not retrying

Solutions:
1. Check health check endpoint response
2. Manually verify health check
3. Lower TTL
4. Implement client-side retry logic
```
