# GeoDNS Reference Guide

## GeoDNS Fundamentals

### Definition
DNS routing based on the geographic location or network location of the querying client, returning different answers for same hostname based on where query originates.

### Benefits
```
1. Latency Optimization
   - Route to geographically nearest server
   - Users in USA -> USA servers
   - Users in Europe -> EU servers
   - Users in Asia -> Asia servers

2. Local Content Delivery
   - Localized content (language, currency)
   - Regional compliance (GDPR, data residency)
   - Local payment methods

3. Load Distribution
   - Distribute load geographically
   - Prevent single region overload
   - Utilize global capacity

4. Disaster Recovery
   - Route around failed regions
   - Geographic failover
   - Business continuity
```

## Location Detection Methods

### 1. GeoIP Database Lookup
Most common method

```
Client IP -> GeoIP Database -> Location

IP: 203.0.113.5
GeoIP lookup:
  Country: United States
  Region: California
  City: San Francisco
  Latitude/Longitude: 37.7749, -122.4194
  ISP: Comcast

Return result:
  example.com A 192.0.2.1 (California server)
```

### GeoIP Databases
```
MaxMind GeoIP2:
- Accuracy: 95% country, 75% city level
- Regular updates (monthly)
- Commercial and free tiers
- Used by Cloudflare, Fastly, AWS

IP2Location:
- Accuracy: 98% country, 85% city level
- Comprehensive coverage
- Used by major CDNs

Geolite2 (MaxMind Free):
- Accuracy: 90% country, 50% city level
- Daily updates
- Free for non-commercial use

Measurement:
- Country accuracy: 99%+
- State/Province: 90-95%
- City: 70-85%
- Organization: 70-80%
```

### 2. ASN (Autonomous System Number) Routing
More accurate than GeoIP, based on network topology

```
Client IP -> ASN Lookup -> ISP/Network -> Location

IP: 203.0.113.5
ASN lookup:
  AS Number: AS7922 (Comcast)
  Country: United States
  Organization: Comcast Cable

Return result:
  example.com A 192.0.2.1 (USA server)

Accuracy:
- More reliable than GeoIP for determining location
- Based on actual network topology
- Harder to spoof than GeoIP headers
```

### 3. EDNS Client Subnet (ECS)
Recursive resolver sends client subnet to authoritative DNS

```
Standard DNS query:
Client -> Recursive Resolver -> Authoritative DNS
                 (doesn't know client location)

EDNS Client Subnet:
Client -> Recursive Resolver -> Authoritative DNS
                 (includes client /24 subnet)

Authoritative responds with geolocation-aware answer
based on ECS subnet, not resolver location

Advantages:
- Accurate even behind shared resolvers
- Works with ISP-shared caches

Privacy concern:
- Reveals client subnet information
- Some ISPs disable ECS for privacy
```

## GeoDNS Routing Patterns

### Pattern 1: Simple Geographic Routing
```
Different servers by country:

US traffic:
example.com A 192.0.2.1 (US East Coast)

EU traffic:
example.com A 192.0.2.2 (EU - Ireland)

APAC traffic:
example.com A 192.0.2.3 (APAC - Singapore)

Default (unknown location):
example.com A 192.0.2.1 (US - default)

Implementation (Route53):
- US routing policy: Return 192.0.2.1
- EU routing policy: Return 192.0.2.2
- APAC routing policy: Return 192.0.2.3
```

### Pattern 2: Regional Failover
```
Multiple servers per region with failover:

US Region:
- Primary: 192.0.2.1 (health check OK)
- Secondary: 192.0.2.2 (failover if primary down)

EU Region:
- Primary: 192.0.2.3 (health check OK)
- Secondary: 192.0.2.4 (failover if primary down)

Client in USA:
  - Try 192.0.2.1 (primary)
  - If fails, try 192.0.2.2 (secondary)

Client in EU:
  - Try 192.0.2.3 (primary)
  - If fails, try 192.0.2.4 (secondary)
```

### Pattern 3: Weighted Geographic Distribution
```
Unequal load distribution by region:

Global capacity: 100 Mbps
Distribution:
  - US: 50 Mbps (50%)
  - EU: 30 Mbps (30%)
  - APAC: 20 Mbps (20%)

Implementation:
Each region returns multiple IPs with weights

US traffic: [192.0.2.1, 192.0.2.2]
  - 192.0.2.1: 60% (60 Mbps)
  - 192.0.2.2: 40% (40 Mbps)

EU traffic: [192.0.2.3]
  - 192.0.2.3: 100% (30 Mbps)

APAC traffic: [192.0.2.4]
  - 192.0.2.4: 100% (20 Mbps)
```

### Pattern 4: Language/Content Routing
```
Content served by user location:

example.com domain structure:
- example.com (English, default)
- example.de (German content)
- example.fr (French content)
- example.es (Spanish content)
- example.jp (Japanese content)

GeoDNS routing:
US/UK traffic    -> example.com (English)
Germany traffic  -> example.de (German)
France traffic   -> example.fr (French)
Spain traffic    -> example.es (Spanish)
Japan traffic    -> example.jp (Japanese)

Implementation:
When client from Germany queries example.com:
GeoDNS returns CNAME to example.de
example.de points to German server (192.0.2.5)
User gets German language content
```

## Implementation Examples

### AWS Route53 GeoDNS
```
Terraform:
resource "aws_route53_record" "geodns_us" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-us"
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

resource "aws_route53_record" "geodns_eu" {
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

resource "aws_route53_record" "geodns_default" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "api-default"
  geolocation_routing_policy {
    country = "*"  # Default/fallback
  }

  alias {
    name                   = aws_lb.us_east.dns_name
    zone_id                = aws_lb.us_east.zone_id
    evaluate_target_health = true
  }
}
```

### Cloudflare Geo-Steering
```
Terraform:
resource "cloudflare_load_balancer" "geodns" {
  zone_id = var.zone_id
  name    = "api.example.com"
  ttl     = 30

  default_pool_ids = ["default-pool"]

  region_pools {
    region   = "WNAM"  # Western North America
    pool_ids = ["west-pool"]
  }

  region_pools {
    region   = "ENAM"  # Eastern North America
    pool_ids = ["east-pool"]
  }

  region_pools {
    region   = "WEUR"  # Western Europe
    pool_ids = ["eu-pool"]
  }

  region_pools {
    region   = "EASIA"  # Eastern Asia
    pool_ids = ["asia-pool"]
  }
}

resource "cloudflare_load_balancer_pool" "west_pool" {
  account_id = var.account_id
  name       = "west-pool"

  origins {
    name    = "west-server"
    address = "west.example.com"
    enabled = true
  }

  check_regions = ["WNAM", "WEUR"]
  description   = "Western US servers"
}
```

### PowerDNS GeoDNS Script
```
PowerDNS Lua script for geolocation:
-- geoip.lua
geoip = require "geoip"
local db = geoip.open("/usr/share/GeoIP/GeoLiteCity.dat", geoip.GEOIP_MEMORY_CACHE)

function preresolve(dnssec)
  local country = db:query_by_addr(dnsheader.ae, geoip.GEOIP_CITY_EDITION_REV1)

  if country == "US" then
    dnssection:addRR("api.example.com", 300, pdns.A, "192.0.2.1")
  elseif country == "DE" then
    dnssection:addRR("api.example.com", 300, pdns.A, "192.0.2.2")
  elseif country == "JP" then
    dnssection:addRR("api.example.com", 300, pdns.A, "192.0.2.3")
  else
    dnssection:addRR("api.example.com", 300, pdns.A, "192.0.2.1")  -- default
  end

  return true
end
```

## Accuracy Considerations

### GeoIP Accuracy Issues
```
False positives:
1. VPN users - appear in VPN location, not actual location
2. Proxies - appear in proxy location
3. Shared corporate networks - all IPs same location
4. Mobile networks - may be at network center, not user

Mitigation:
1. EDNS Client Subnet (ECS) - more accurate
2. Client-side geolocation (browser APIs)
3. AS Number lookup (complementary data)
4. Conservative routing (default to fallback)
```

### Fallback Strategy
```
Query resolution order:
1. Try exact country match (Germany -> German server)
2. Try regional match (Europe -> EU server)
3. Try default (US -> Default server)

Ensures answer always returned
Handles edge cases and unknowns

Configuration:
set_identifier priority order:
1. de (Germany specific)
2. eu (European fallback)
3. default (global fallback)
```

## GeoDNS Health Checking

### Multi-Region Health Checks
```
Each region checks its own endpoints:

US Health Check:
- Monitor 192.0.2.1
- HTTP GET /health -> 200 OK
- Interval: 10 seconds
- Failure threshold: 2

EU Health Check:
- Monitor 192.0.2.2
- HTTPS GET /health -> 200 OK
- Interval: 10 seconds
- Failure threshold: 2

APAC Health Check:
- Monitor 192.0.2.3
- HTTPS GET /health -> 200 OK
- Interval: 10 seconds
- Failure threshold: 2

If US fails:
- US traffic routed to fallback
- EU and APAC unaffected
```

### Cascading Health Checks
```
Primary endpoints down -> Route to secondary

US Primary (192.0.2.1) down:
  -> Route US traffic to US Secondary (192.0.2.11)

Both US endpoints down:
  -> Route US traffic to EU (192.0.2.2)

All endpoints down:
  -> Route to last-resort endpoint

Configuration (Route53):
1. US Primary health check (depends on US server)
2. US Secondary health check (depends on US server)
3. EU health check (depends on EU server)
4. Failover order: US Primary -> US Secondary -> EU
```

## Performance Impact

### Query Response Time
```
GeoDNS adds minimal latency:

Simple A record lookup:        ~50ms
GeoDNS lookup (with GeoIP):    ~55ms (slight increase)
GeoDNS with health check:      ~60ms (small increase)

Overall impact: 10-20% latency increase
Usually imperceptible to clients

Optimization:
- Cache GeoDNS responses
- Use fast GeoIP database (in-memory)
- Pre-compute common paths
```

### Cache Considerations
```
GeoDNS reduces cache effectiveness:
Standard DNS: Same answer from all resolvers = High hit rate

GeoDNS: Different answers by location = Lower hit rate
- Resolver cache in California: Returns 192.0.2.1
- Resolver cache in Frankfurt: Returns 192.0.2.2
- Different answers = Less cache sharing

TTL strategy:
- Shorter TTL (60-300 sec) = Lower hit rate, more fresh
- Longer TTL (3600+ sec) = Higher hit rate, less fresh

Balance: TTL 300-600 seconds (good for both)
```

## Best Practices

1. **Always Include Default**: Catch-all for unknown locations
2. **Health Check Each Region**: Ensure endpoint health
3. **Monitor Accuracy**: Track misdirected traffic
4. **Test All Regions**: Verify GeoDNS from different locations
5. **Document Policies**: Map GeoDNS decision logic
6. **Cascade Failovers**: Secondary endpoints in each region
7. **Short TTL**: Enable rapid changes (300-600 seconds)
8. **EDNS Client Subnet**: More accurate location detection
9. **Client-Side Fallback**: Clients should retry on connection failure
10. **Redundancy**: Multiple endpoints per region

## Debugging GeoDNS

### Test from Different Locations
```
Query from USA:
dig +short @ns1.example.com api.example.com A
192.0.2.1

Query from Germany:
dig +short @ns1.example.com api.example.com A
192.0.2.2

Different answers = GeoDNS working
```

### Check Effective Location
```
Determine your detected location:

curl "http://ip-api.com/json/?fields=country,region,city,isp,as"
{
  "country": "United States",
  "region": "California",
  "city": "San Francisco",
  "isp": "Comcast",
  "as": "AS7922 Comcast Cable"
}

Your querying location (for GeoDNS purposes)
May differ from actual location (VPN, proxy, etc.)
```

### GeoIP Database Verification
```
Test GeoIP accuracy:

mmdblookup -f /usr/share/GeoIP/GeoLite2-Country.mmdb 203.0.113.5 country iso_code
  {
    "country": {
      "iso_code": "US"
    }
  }

Verify detected country matches actual
```

## Advanced Patterns

### Weighted GeoDNS
```
Route by location AND load distribution:

Example: USA has more capacity (70%) than EU (30%)

US traffic:
api.example.com A 192.0.2.1 (weight 70)
api.example.com A 192.0.2.2 (weight 30)

EU traffic:
api.example.com A 192.0.2.3 (weight 100)

Combines geography + capacity distribution
```

### GeoDNS with CDN
```
GeoDNS points to CDN edge in region:

US query -> example.com A 192.0.2.1
         -> CNAME cdn-us.example.com
         -> Cloudflare US edge node

EU query -> example.com A 192.0.2.2
         -> CNAME cdn-eu.example.com
         -> Cloudflare EU edge node

Adds multiple layers of geographic optimization
```
