# Content Delivery Network (CDN) Reference

## Introduction

Content Delivery Networks accelerate content delivery by caching and serving content from edge locations closest to end users, reducing latency and improving user experience globally.

## CDN Fundamentals

### How CDN Works

**Request Flow**:
```
1. User requests content (www.example.com/image.jpg)
2. DNS resolves to nearest edge location
3. Edge checks local cache
4. If cached: Serve from edge (cache hit)
5. If not cached: Fetch from origin (cache miss)
6. Edge caches content and serves to user
7. Subsequent requests served from cache
```

### Benefits

**Performance**:
- Reduced latency (geographic proximity)
- Faster page load times
- Improved user experience
- Bandwidth offloading from origin

**Scalability**:
- Handle traffic spikes
- Distribute load globally
- Reduce origin server load
- Scale automatically

**Reliability**:
- Origin shielding
- Automatic failover
- High availability
- DDoS protection

**Cost**:
- Reduce origin bandwidth costs
- Lower data transfer fees
- Optimize infrastructure spend

## AWS CloudFront

### Architecture

**Components**:
```
Users (Global)
    |
CloudFront Edge Locations (225+ locations)
    |
Regional Edge Caches (13 locations)
    |
Origin (S3, ALB, EC2, Custom)
```

### Distribution Types

**Web Distribution**:
- HTTP/HTTPS content
- Static and dynamic content
- Websites, APIs
- Progressive download

**RTMP Distribution** (Deprecated):
- Streaming media
- Adobe Flash Media Server
- Legacy support only

### Origins

**S3 Bucket**:
```
CloudFront --> S3 Bucket
- Static website hosting
- Origin Access Identity (OAI)
- S3 Transfer Acceleration
```

**Application Load Balancer**:
```
CloudFront --> ALB --> EC2/ECS
- Dynamic content
- Application APIs
- Custom headers
```

**EC2 Instance**:
```
CloudFront --> EC2 Public/Elastic IP
- Custom applications
- Self-hosted solutions
```

**Custom Origin**:
```
CloudFront --> On-Premises Server
- Hybrid architecture
- Existing infrastructure
- HTTP/HTTPS server
```

### Cache Behaviors

**Path Patterns**:
```
Default (*):            Cache for 1 day
/images/*:              Cache for 1 year
/api/*:                 No cache, forward all
/static/*:              Cache for 30 days
```

**Cache Key Configuration**:
```
URL Query Strings:      Include/exclude/whitelist
Headers:                None/whitelist/all
Cookies:                None/whitelist/all

Example:
/product?id=123&color=red
Cache key: /product?id=123 (exclude color)
```

### Cache Control

**TTL (Time To Live)**:
```
Minimum TTL: 0 seconds
Default TTL: 86400 seconds (24 hours)
Maximum TTL: 31536000 seconds (1 year)

Cache-Control: max-age=3600
Cache-Control: no-cache (always revalidate)
Cache-Control: no-store (don't cache)
```

**Origin Response Headers**:
```
Cache-Control: public, max-age=31536000
Expires: Thu, 01 Dec 2025 16:00:00 GMT
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Wed, 01 Jan 2025 00:00:00 GMT
```

### Lambda@Edge

**Edge Computing**:
```
Viewer Request  --> Lambda@Edge --> CloudFront
Viewer Response <-- Lambda@Edge <-- CloudFront
Origin Request  --> Lambda@Edge --> Origin
Origin Response <-- Lambda@Edge <-- Origin
```

**Use Cases**:
- URL rewriting and redirects
- A/B testing
- Authentication and authorization
- Image resizing
- Header manipulation
- Bot detection

**Example**: Dynamic Image Resizing
```javascript
exports.handler = async (event) => {
    const request = event.Records[0].cf.request;
    const uri = request.uri;

    // Check for image resize query parameter
    if (uri.match(/\.(jpg|png)$/)) {
        const width = request.querystring.match(/width=(\d+)/);
        if (width) {
            request.uri = uri.replace(/\.(jpg|png)$/,
                `-${width[1]}.$1`);
        }
    }

    return request;
};
```

### CloudFront Functions

**Lightweight Edge Functions**:
- Viewer request/response only
- Microsecond execution
- Lower cost than Lambda@Edge
- JavaScript (ES5.1)

**Use Cases**:
- URL rewrites
- Header manipulation
- Simple redirects
- Cache key normalization

**Example**: Add Security Headers
```javascript
function handler(event) {
    var response = event.response;
    var headers = response.headers;

    headers['strict-transport-security'] = {
        value: 'max-age=63072000'
    };
    headers['x-content-type-options'] = {
        value: 'nosniff'
    };
    headers['x-frame-options'] = {
        value: 'DENY'
    };

    return response;
}
```

### Security

**Origin Access Identity (OAI)**:
```
S3 Bucket Policy:
{
    "Effect": "Allow",
    "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E..."
    },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::mybucket/*"
}

Users cannot access S3 directly
Must go through CloudFront
```

**Signed URLs and Cookies**:

**Signed URL**:
```
https://d111111abcdef8.cloudfront.net/image.jpg?
Expires=1420070400&
Signature=signature&
Key-Pair-Id=keypairid

Canned Policy: Simple expiration
Custom Policy: IP restrictions, date ranges
```

**Signed Cookies**:
```
Set-Cookie: CloudFront-Policy=base64-encoded-policy
Set-Cookie: CloudFront-Signature=hashed-signature
Set-Cookie: CloudFront-Key-Pair-Id=keypairid

Protect multiple files
No URL modification needed
```

**Field-Level Encryption**:
```
Encrypt sensitive data at edge
Decryption at application
Credit card data protection
PCI DSS compliance
```

**AWS WAF Integration**:
```
CloudFront --> AWS WAF Rules
- Rate limiting
- IP filtering
- SQL injection protection
- XSS protection
```

## Azure CDN

### Profiles and Endpoints

**CDN Profiles**:
- Standard Microsoft
- Standard Akamai
- Standard Verizon
- Premium Verizon

**Architecture**:
```
Users --> Azure CDN Endpoint --> Origin (Storage, App Service, Custom)
```

### Caching Rules

**Global Caching Rules**:
```
All paths: Cache duration
Override origin cache headers
Bypass cache
```

**Custom Caching Rules**:
```
Path: /images/*
Cache duration: 365 days

Path: /api/*
Bypass cache
```

### Azure Front Door Integration

**Global Load Balancing + CDN**:
```
Users (Global)
    |
Azure Front Door (Edge)
    |
+-- Cache Layer
|
+-- WAF Layer
|
+-- Routing Layer
    |
Backend Pools (Multi-Region)
```

**Features**:
- Session affinity
- URL-based routing
- SSL offload
- Health probes
- Custom domains

### Rules Engine

**Advanced Routing**:
```
IF: URL path contains /mobile
THEN: Route to mobile backend

IF: Country = US
THEN: Route to US backend

IF: Cookie user_type = premium
THEN: Route to premium backend
```

## Google Cloud CDN

### Cloud CDN Architecture

**Integration with Cloud Load Balancing**:
```
Users (Global)
    |
Cloud CDN (Edge Locations)
    |
HTTPS Load Balancer (Global)
    |
Backend Services
    |
+-- us-central1: Instance Group
|
+-- europe-west1: Instance Group
```

### Cache Modes

**CACHE_ALL_STATIC** (Default):
```
Caches static content automatically
Based on Cache-Control headers
No configuration needed
```

**USE_ORIGIN_HEADERS**:
```
Cache only if origin sends cache headers
Cache-Control, Expires
Full control from application
```

**FORCE_CACHE_ALL**:
```
Cache everything (use cautiously)
Override origin headers
Specify default TTL
```

### Signed URLs and Cookies

**URL Signing**:
```
https://cdn.example.com/video.mp4?
Expires=1609459200&
KeyName=my-key&
Signature=base64-signature

Time-based expiration
IP restrictions available
```

### Negative Caching

**Error Caching**:
```
404 Not Found: Cache for 5 minutes
500 Server Error: Cache for 1 minute
503 Service Unavailable: No cache

Reduces origin load during issues
```

## Media CDN (Google)

**Next-Generation CDN**:
- 100% global SLA
- Dual-token authentication
- Enhanced analytics
- Better performance

## CDN Best Practices

### Cache Optimization

**Static vs Dynamic Content**:

**Static Content** (Long TTL):
```
Images: 1 year
CSS/JS (versioned): 1 year
Fonts: 1 year
Videos: 1 week - 1 month
```

**Dynamic Content** (Short TTL):
```
API responses: No cache or seconds
User-specific content: No cache
Frequently updated: Minutes
```

**Versioning Strategy**:
```
Style.css?v=1.2.3 (query string)
style-v1.2.3.css (file name)
/v1.2.3/style.css (path)

CloudFront/CDN: Recommend file name versioning
```

### Cache Invalidation

**CloudFront Invalidation**:
```
Invalidate specific paths:
/images/logo.png
/css/*
/*

First 1000 invalidations per month: Free
Additional: $0.005 per path

Prefer versioning over invalidation
```

**Azure CDN Purge**:
```
Purge by path
Purge all
Wildcard support (Premium Verizon)
```

**Cloud CDN Invalidation**:
```
gcloud compute url-maps invalidate-cdn-cache
--path "/path/to/resource"
--host "www.example.com"
```

### Origin Shield

**Concept**:
```
Edge Locations --> Regional Cache (Origin Shield) --> Origin

Reduces origin requests
Improves cache hit ratio
Protects origin from edge misses
```

**AWS CloudFront Origin Shield**:
- Select AWS Region closest to origin
- Consolidated requests to origin
- Additional cost but reduces origin load

### Compression

**Automatic Compression**:
```
CloudFront: Automatic gzip compression
Azure CDN: Compression enabled
Cloud CDN: Automatic compression

Requirements:
- Content-Type in allowed list
- File size > 1KB
- Not already compressed
```

**Supported Content Types**:
```
text/html
text/css
text/javascript
application/javascript
application/json
image/svg+xml
```

## Performance Optimization

### HTTP/2 and HTTP/3

**HTTP/2**:
- Multiplexing (multiple requests per connection)
- Header compression
- Server push
- Binary protocol

**HTTP/3 (QUIC)**:
- UDP-based transport
- Faster connection establishment
- Better mobile performance
- CloudFront supports HTTP/3

### TCP Optimization

**Connection Optimization**:
- Persistent connections (Keep-Alive)
- Connection pooling
- TLS session resumption
- TLS 1.3 (faster handshake)

### Geo-Proximity Routing

**Route to Nearest Edge**:
```
User in Tokyo --> Tokyo edge location
User in London --> London edge location
User in New York --> New York edge location

Minimize network hops
Reduce latency
```

## Security Features

### DDoS Protection

**AWS Shield Standard**:
- Automatic protection
- Network and transport layer
- Free with CloudFront

**AWS Shield Advanced**:
- Application layer protection
- 24/7 DDoS Response Team
- Cost protection
- $3,000/month

**Azure DDoS Protection**:
- Basic (free)
- Standard (paid)
- Always-on traffic monitoring

**Cloud Armor**:
- DDoS protection
- WAF rules
- Rate limiting
- IP allowlist/blocklist

### SSL/TLS

**Certificate Options**:

**CloudFront Default** (*.cloudfront.net):
```
Free
AWS managed
cloudfront.net domain
```

**ACM Certificate** (Custom domain):
```
Free
Automatic renewal
SNI or dedicated IP
```

**Custom Certificate**:
```
Import your own
IAM or ACM
Full control
```

**SNI vs Dedicated IP**:
```
SNI (Server Name Indication):
- Free
- Modern browsers only
- Multiple certs per IP

Dedicated IP:
- $600/month per distribution
- Legacy browser support
- Dedicated IP per distribution
```

### Geo-Restriction

**Whitelist/Blacklist Countries**:
```
CloudFront:
Geo-restriction: Whitelist
Allowed countries: US, CA, GB

Or

Geo-restriction: Blacklist
Blocked countries: XX, YY
```

## Monitoring and Analytics

### CloudFront Metrics

**Standard Metrics** (Free):
```
Requests
Bytes Downloaded
Bytes Uploaded
4xx/5xx Error Rate
```

**Real-Time Metrics**:
```
Requests per second
Error rate
Cache hit rate
Updated every 5 seconds
```

### Access Logs

**CloudFront Logs**:
```
Timestamp
Edge location
Bytes sent
IP address
Request URI
Status code
User agent
Query string

Delivered to S3
Analyze with Athena
```

### Analytics

**CloudFront Reports**:
- Cache statistics
- Popular objects
- Top referrers
- Usage by location
- Viewer details (OS, browser)

**Azure CDN Analytics**:
- Traffic analytics
- Bandwidth usage
- Cache hit ratio
- Status codes

**Cloud CDN Monitoring**:
```
Request count
Request bytes
Response latency
Cache hit rate
Error counts
```

## Cost Optimization

### Pricing Components

**CloudFront**:
```
Data transfer out (per GB)
HTTP/HTTPS requests
Invalidation requests (after 1000/month)
Field-level encryption requests
Dedicated IP (optional)

Price varies by region:
US/Europe: Lower
Asia Pacific: Higher
```

**Regional Edge Caches**:
- Free tier available
- Reduces origin fetches
- Improves cache hit ratio

### Cost Reduction Strategies

1. **Increase cache TTL**: Reduce origin requests
2. **Use versioning**: Avoid invalidations
3. **Compress content**: Reduce transfer costs
4. **Optimize images**: Smaller file sizes
5. **Origin Shield**: Reduce origin load
6. **Reserved capacity**: For predictable traffic
7. **Right-size origins**: Reduce origin costs

### Price Classes

**CloudFront Price Classes**:
```
All Edge Locations: Full global coverage
Use Only US, Canada, Europe: Lower cost
Use Only US, Canada, Europe, Asia: Medium cost

Choose based on user distribution
```

## Troubleshooting

### Cache Misses

**Causes**:
- Query strings not configured
- Cookies forwarded unnecessarily
- Vary header differences
- Expired cache

**Solutions**:
- Whitelist required query strings only
- Forward only necessary cookies
- Normalize headers
- Increase TTL

### High Latency

**Causes**:
- Origin performance issues
- Large uncached files
- Slow SSL handshake
- Network congestion

**Solutions**:
- Optimize origin performance
- Pre-warm cache
- Enable HTTP/2, HTTP/3
- Use Origin Shield

### Origin Errors

**502 Bad Gateway**:
- Origin unreachable
- Timeout waiting for origin
- SSL certificate mismatch

**503 Service Unavailable**:
- Origin overloaded
- Origin returning errors

**504 Gateway Timeout**:
- Origin response timeout
- Increase origin timeout settings

## Advanced Features

### Streaming

**Live Streaming**:
```
Encoder --> Origin (Media Live) --> CloudFront (HLS/DASH) --> Players

Protocol: HLS, DASH
Adaptive bitrate
Low latency options
```

**On-Demand Video**:
```
S3 (Video files) --> CloudFront --> Progressive Download/Streaming

Formats: MP4, HLS, DASH
Signed URLs for protection
```

### Edge Computing

**Lambda@Edge Use Cases**:
- Real-time image transformation
- A/B testing
- SEO optimization
- Personalization
- Authentication
- Bot detection

**CloudFront Functions Use Cases**:
- URL normalization
- Header manipulation
- Redirects
- Request validation

## Best Practices Summary

### Performance

1. Set appropriate cache TTLs
2. Enable compression
3. Use HTTP/2 and HTTP/3
4. Optimize cache keys
5. Implement Origin Shield
6. Pre-warm cache for events

### Security

1. Use HTTPS only
2. Enable AWS WAF
3. Implement signed URLs/cookies
4. Use Origin Access Identity
5. Enable DDoS protection
6. Regular security audits

### Cost

1. Increase cache hit ratio
2. Use versioning over invalidation
3. Compress content
4. Choose appropriate price class
5. Monitor and optimize usage
6. Right-size infrastructure

### Operations

1. Enable access logging
2. Monitor key metrics
3. Set up alerting
4. Document configuration
5. Regular cache analysis
6. Test failover scenarios

## Conclusion

CDN is essential for delivering fast, reliable, and secure content globally. Proper configuration, cache optimization, security implementation, and monitoring ensure optimal performance and cost-effectiveness.
