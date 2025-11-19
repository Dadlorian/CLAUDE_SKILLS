# CDN Architecture Reference

## CDN Fundamentals

### Architecture Overview
```
Origin Server (1 location)
         |
         | Content distribution
         |
    CDN Edge Nodes
    /    |    |    \
   /     |    |     \
  DC1   DC2  DC3   DC4
 (NYC) (LA) (EU)  (APAC)

Client in NY   -> Routes to DC1 edge node (cached)
Client in LA   -> Routes to DC2 edge node (cached)
Client in Paris-> Routes to DC3 edge node (cached)
Client in Tokyo-> Routes to DC4 edge node (cached)
```

### Benefits
- **Latency**: Content served from geographically close edge
- **Bandwidth**: Offloads traffic from origin
- **Resilience**: Distributed cache survives origin outages
- **Scalability**: Handles traffic spikes at edge
- **Availability**: Multiple serving points for DDoS protection

## Cache Architecture

### Cache Hierarchy
```
Client Browser Cache
         |
         | (expires or cache miss)
         |
    ISP Resolver Cache
         |
         | (expires or miss)
         |
    Recursive Resolver Cache
         |
         | (miss)
         |
  CDN Edge Cache
         |
         | (hit rate 95%+)
         |
  Origin Shield
         |
         | (protects origin)
         |
  Origin Server

Hit rates:
- Browser cache: 60-80% (with Service Workers)
- ISP cache: 30-50%
- CDN edge: 90-95%
- Origin shield: Reduces origin traffic by 90%+
```

### Cache Key Computation
```
Basic cache key:
Scheme + Host + Path + Query String

Example:
https://example.com/api/users?sort=name
Cache Key: https:example.com/api/users?sort=name

Advanced cache key (CDN-specific):
- HTTP method (GET vs POST)
- Accept-Encoding (gzip, brotli)
- Accept-Language (content negotiation)
- Cookie values (for personalization)
- Custom headers (API version, etc.)

Example (Cloudflare):
Cache key = { scheme, host, path, query, language_header, country_header }
```

## Edge Nodes

### PoP (Point of Presence)
```
Cloudflare: 275+ PoPs globally
Fastly: 60+ PoPs strategically placed
AWS CloudFront: 500+ edge locations + regional caches
Akamai: 4000+ servers in ISPs globally

PoP benefits:
- Local origin fallback
- Cache layer for hits
- DDoS scrubbing
- Request transformation
- WAF enforcement
```

### Edge Routing
```
Anycast routing to nearest PoP:
1. Client queries anycast IP
2. BGP routing directs to nearest PoP
3. PoP serves cached content
4. If miss, fetch from origin or origin shield

Latency improvement:
- Without CDN: 100-200ms from distant origin
- With CDN: 10-50ms from nearby PoP
```

## Origin Configuration

### Origin Settings
```
CDN Configuration:
{
  "origin": {
    "address": "origin.example.com",
    "port": 443,
    "protocol": "https",
    "host_header": "origin.example.com",
    "path": "/",
    "connection_timeout": 10,
    "response_timeout": 30,
    "keep_alive": true,
    "ssl_verification": true
  }
}
```

### Custom Origins vs. Origin Shield
```
Direct Origin:
CDN Edge -> Origin (direct connection)
Pros: Low latency
Cons: High load on origin, thundering herd

With Origin Shield:
CDN Edge -> Origin Shield -> Origin
Pros: Protects origin from traffic spikes, regional cache
Cons: Slight latency increase, additional cost

Origin Shield use cases:
- Popular content (viral videos)
- Sudden traffic spikes (sales, launches)
- Small origin servers
- Database-driven content
```

## Content Delivery Patterns

### Static Content
```
Characteristics:
- Long TTL (1 day to 1 year)
- High cache hit ratio (95%+)
- Immutable after upload
- Examples: CSS, JS, images, fonts

CDN configuration:
Cache-Control: public, max-age=31536000, immutable
```

### Dynamic Content
```
Characteristics:
- Short TTL (1-300 seconds)
- Lower cache hit ratio (50-80%)
- May change frequently
- Examples: API responses, personalized content

Strategies:
1. Cache by query string hash
2. Cache by HTTP method
3. Cache by Accept-Encoding
4. Cookie-based cache bypass

Example:
Cache-Control: public, max-age=60, must-revalidate
```

### Personalized Content
```
Vary headers for same URL, different content:
Vary: Accept-Language, Accept-Encoding, Cookie

CDN handles:
- Caches separate copy per language
- Caches separate copy per encoding (gzip, brotli)
- Caches separate copy per user (via cookie)

Cache key expansion:
1 URL -> Multiple cache entries (1 per variation)
```

### Streaming Content
```
Large files (video, software):
- Range requests: Support byte-range requests
- Chunked delivery: Deliver in 256KB - 1MB chunks
- Origin buffering: Buffer small amounts before streaming

Configuration:
Transfer-Encoding: chunked
Range: bytes=0-262143

CDN benefits:
- Parallel downloads (multiple PoP connections)
- Resume capability (resume from broken download)
- Bandwidth optimization (regional paths)
```

## Cache Control Headers

### HTTP Cache Headers
```
Cache-Control directives:

Public caching:
Cache-Control: public, max-age=3600
- CDN caches for 3600 seconds
- Client caches for 3600 seconds

Private caching:
Cache-Control: private, max-age=3600
- Client caches for 3600 seconds
- CDN does NOT cache

No caching:
Cache-Control: no-cache, no-store
- CDN revalidates with origin every request
- Client must revalidate

Maximum age with stale:
Cache-Control: max-age=3600, stale-while-revalidate=86400
- Use cache if < 3600 seconds old
- Revalidate if 3600-86400 seconds old
- Return stale if origin unreachable

ETag validation:
If-None-Match: "abc123def456"
- Return 304 if ETag matches (revalidation)
- 304 response saves bandwidth (no body)
```

### Conditional Requests
```
Last-Modified / If-Modified-Since:
Response:
Last-Modified: Wed, 20 Nov 2024 10:30:00 GMT
Cache-Control: max-age=3600

Request (after expiry):
If-Modified-Since: Wed, 20 Nov 2024 10:30:00 GMT

If unchanged:
Response: 304 Not Modified

If changed:
Response: 200 OK (with new content)
```

## Cache Purging

### Soft Purge (Stale-While-Revalidate)
```
CDN returns stale content immediately
Fetches fresh content in background

Benefits:
- User gets instant response
- No user-facing latency
- Fresh content available for next request

Implementation:
1. Publish content with stale-while-revalidate header
2. When content updates, purge soft
3. Users see stale version
4. Next request gets fresh version
```

### Hard Purge
```
CDN immediately removes from cache
Next request fetches from origin

Implementation:
curl -X POST "https://api.cloudflare.com/client/v4/zones/zone_id/purge_cache" \
  -H "Content-Type: application/json" \
  --data '{"files": ["https://example.com/page.html"]}'

Selective purge methods:
- Purge by URL path
- Purge by tag (group-based)
- Purge by URL pattern (regex)
- Purge all (full cache flush)
```

### Cache Tag Purging
```
Set cache tags on content:
Cache-Tag: post-123, user-456, homepage

When post-123 updates, purge tag:
curl -X POST "https://api.cloudflare.com/client/v4/zones/zone_id/purge_cache" \
  -H "Content-Type: application/json" \
  --data '{"tags": ["post-123"]}'

Benefits:
- Purge groups of related content
- Example: Update blog post + homepage
- Both purge in single API call
```

## Compression

### Compression Types

#### GZIP
```
Standard HTTP compression

Configuration:
Content-Encoding: gzip
Compression ratio: 70-80% reduction typical

Accept-Encoding: gzip request
Response: gzip-encoded body

Browser support: 100% (all modern browsers)
```

#### Brotli
```
Modern compression (RFC 7932)

Compression ratio: 75-85% reduction (better than gzip)
CPU cost: Higher than gzip
Browser support: 85-90% (not IE, old browsers)

Configuration:
Content-Encoding: br
Accept-Encoding: br

CDN decision:
If client supports brotli: Use brotli
Else if client supports gzip: Use gzip
Else: No compression (uncompressed)
```

#### Compression Best Practices
```
Compressible content types:
- text/html
- text/css
- application/javascript
- application/json
- image/svg+xml
- application/xml

Don't compress:
- image/jpeg, image/png (already compressed)
- video/* (already compressed)
- application/pdf (already compressed)

Minimum size for compression:
Content-Length > 1KB (overhead for small files)

Configuration:
compress_types text/html text/css application/javascript application/json;
compress_min_length 1024;
```

## Performance Features

### HTTP/2 Push
```
Server initiates download of critical resources

Example:
GET /index.html -> Server predicts needs style.css
Server pushes /style.css before client requests

Benefits:
- Client doesn't wait to parse HTML
- Multiple resources in flight

Configuration:
Link: </style.css>; rel=preload; as=style
</script.js>; rel=preload; as=script

Downsides:
- Hard to predict what client needs
- Client browser may cache (duplicate push)
- HTTP/2 specific (not in HTTP/1.1)

Modern approach: Use Resource Hints instead
```

### Resource Hints
```
Preconnect (establish DNS + TCP + TLS):
<link rel="preconnect" href="https://cdn.example.com">

DNS Prefetch (DNS lookup only):
<link rel="dns-prefetch" href="https://cdn.example.com">

Prefetch (fetch resource for future use):
<link rel="prefetch" href="/next-page.html">

Preload (fetch critical resource):
<link rel="preload" href="/critical.js" as="script">
```

## Authentication & Security

### Token-Based Authentication
```
Time-limited URL tokens for cache content:

URL: https://example.com/video.mp4?token=abc123&exp=1733000000

Token validation:
- Extract expiration time
- Compare to current time
- If expired, reject (403 Forbidden)
- If valid, serve content

Benefits:
- Prevent content sharing
- Time-limited access
- IP-locked tokens possible
```

### IP-Based Restrictions
```
Restrict CDN caching to specific IPs:

Configuration:
If client IP in whitelist:
  - Serve from cache
  - Cache hit
Else:
  - Reject request (403 Forbidden)
  - Or serve uncached from origin
```

## Regional CDN Strategy

### Multi-CDN Failover
```
Primary CDN (Cloudflare)
         |
    (health check fails)
         |
Secondary CDN (Fastly)
         |
    (health check fails)
         |
Origin server

Implementation:
1. CNAME to primary CDN
2. Health check primary CDN
3. If down, switch CNAME to secondary
4. TTL = 60 seconds (rapid failover)
```

### CDN Failover with Terraform
```
resource "aws_route53_record" "cdn_failover" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "cdn.example.com"
  type    = "CNAME"

  set_identifier = "primary"
  failover_routing_policy {
    type = "PRIMARY"
  }

  records = ["primary-cdn.example.com"]
  ttl     = 60

  health_check_id = aws_route53_health_check.primary_cdn.id
}

resource "aws_route53_record" "cdn_secondary" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "cdn.example.com"
  type    = "CNAME"

  set_identifier = "secondary"
  failover_routing_policy {
    type = "SECONDARY"
  }

  records = ["secondary-cdn.example.com"]
  ttl     = 60
}
```
