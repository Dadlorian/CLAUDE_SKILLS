# CDN Provider Comparison

## Cloudflare

### Overview
- Global CDN with 275+ edge locations
- Known for performance and DDoS protection
- Fixed pricing model
- DNS + CDN integration

### Strengths
```
Performance:
- Global Anycast network
- Smart routing
- HTTP/2 and HTTP/3 support
- Argo Smart Routing (additional fee)

Security:
- DDoS protection (all plans)
- Web Application Firewall (WAF)
- Bot Management
- Rate limiting
- IP reputation filtering

Features:
- DNS + CDN bundled
- Workers (edge serverless)
- Firewall rules
- Load balancing
- URL forwarding

Pricing:
- Free tier available
- Predictable per-month cost
- No per-bandwidth charges
- Transparent pricing
```

### Configuration Example
```
Terraform:
resource "cloudflare_zone" "example" {
  zone = "example.com"
  account_id = var.account_id
}

resource "cloudflare_record" "www" {
  zone_id = cloudflare_zone.example.id
  name    = "www"
  type    = "CNAME"
  value   = "example.com"
  proxied = true  # Enable CDN
}

resource "cloudflare_cache_rules" "example" {
  zone_id = cloudflare_zone.example.id

  rules {
    description = "Cache static assets"
    if           = "http.request.uri.path matches \"/static/.*\""
    then = {
      cache     = true
      cache_ttl = 86400
    }
  }
}

Workers (serverless):
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  return new Response('Hello from edge!', { status: 200 })
}
```

### Use Cases
- Small to medium websites
- DDoS protection priority
- Fixed budget requirement
- All-in-one DNS + CDN

## Fastly

### Overview
- High-performance CDN for media and APIs
- Real-time analytics
- VCL for edge computing
- Strong in video delivery

### Strengths
```
Performance:
- Low latency (especially for live content)
- Real-time analytics dashboard
- 60+ global POP locations
- Sub-50ms origin connectivity

Edge Computing:
- VCL (Varnish Configuration Language)
- Computed fields
- Request transformation
- Complex routing logic

Features:
- Instant purge (no TTL waiting)
- Origin shield
- Load balancing
- Image optimization
- Video delivery optimization

Analytics:
- Real-time metrics
- Detailed logging
- GeoIP reports
- Cache analytics
```

### Configuration Example
```
VCL (Fastly edge code):
sub vcl_recv {
  # Add VCL logic here
  if (req.method != "GET" && req.method != "HEAD") {
    return (pass);
  }
}

sub vcl_backend_response {
  # Set cache TTL based on content type
  if (beresp.http.Content-Type ~ "application/json") {
    set beresp.ttl = 60s;
  } else if (beresp.http.Content-Type ~ "text/html") {
    set beresp.ttl = 3600s;
  } else {
    set beresp.ttl = 86400s;
  }
}

Terraform:
resource "fastly_service_vcl" "example" {
  name = "example-cdn"

  domain {
    name = "example.com"
  }

  backend {
    name           = "origin"
    address        = "origin.example.com"
    port           = 443
    override_host  = "origin.example.com"
  }

  vcl {
    name    = "main"
    content = file("${path.module}/fastly.vcl")
    main    = true
  }

  activate_version = true
}
```

### Use Cases
- Video streaming platforms
- API CDN
- Real-time analytics requirement
- Custom edge logic
- High-performance requirements

## AWS CloudFront

### Overview
- CDN integrated with AWS ecosystem
- 500+ edge locations globally
- Tight S3 integration
- Lambda@Edge support

### Strengths
```
Integration:
- Seamless S3 origin integration
- AWS WAF integration
- IAM authentication
- AWS Shield DDoS protection

Edge Computing:
- Lambda@Edge (serverless functions)
- CloudFront Functions (lightweight)
- Request transformation
- Response generation

Features:
- Origin Shield
- Field-level encryption
- Signed URLs / Signed Cookies
- Custom SSL certificates
- Geo-blocking

Performance:
- 500+ edge locations
- Excellent AWS region affinity
- HTTP/2 and HTTP/3
- Compression support
```

### Configuration Example
```
Terraform:
resource "aws_cloudfront_distribution" "example" {
  origin {
    domain_name = aws_s3_bucket.origin.bucket_regional_domain_name
    origin_id   = "myS3Origin"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  enabled = true

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "myS3Origin"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

Lambda@Edge:
resource "aws_lambda_function" "edge_function" {
  filename = "lambda.zip"
  function_name = "cloudfront-transform"
  role = aws_iam_role.lambda_role.arn
  handler = "index.handler"
  runtime = "python3.9"

  environment {
    variables = {
      REDIRECT_DOMAIN = "cdn.example.com"
    }
  }
}
```

### Use Cases
- AWS-centric environments
- S3-based website hosting
- AWS infrastructure required
- Serverless edge functions
- Tight AWS integration

## Akamai

### Overview
- Enterprise-scale CDN
- 4000+ edge servers
- Most comprehensive feature set
- Highest cost option

### Strengths
```
Scale:
- 4000+ edge servers globally
- Most PoP coverage
- Enterprise SLA
- 99.99% availability

Features:
- Advanced DDoS protection
- Bot protection
- Web performance
- Media services
- Security services

Intelligence:
- Predictive prefetch
- Traffic steering
- Adaptive acceleration
- SSL/TLS optimization

Enterprise:
- 24/7 support
- Custom configurations
- Integration services
- Consulting included
```

### Configuration Example
```
Property definition (Edge, Host, and Origin):
{
  "productId": "prd_Site_Accel",
  "propertyName": "example.com",
  "hostname": "www.example.com",
  "origin": {
    "originId": "my_origin",
    "hostname": "origin.example.com",
    "port": 443
  },
  "caching": {
    "cacheTtl": 3600,
    "cacheKeyOptimization": true
  },
  "performance": {
    "adaptiveAcceleration": true,
    "prefetch": true
  }
}

Image & Video Management:
{
  "imageAndVideoManager": {
    "enabled": true,
    "qualityPerDevice": "auto",
    "compressionLevel": "high",
    "format": "auto"
  }
}
```

### Use Cases
- Enterprise deployments
- Large media companies
- High-security requirements
- 24/7 support needed
- Complex global distribution

## Comparison Table

| Feature | Cloudflare | Fastly | AWS CloudFront | Akamai |
|---------|-----------|--------|----------------|--------|
| Global PoPs | 275+ | 60+ | 500+ | 4000+ |
| Edge Locations | Good | Excellent | Excellent | Best |
| Pricing Model | Fixed/bandwidth | Pay-as-you-go | Pay-as-you-go | Custom |
| DDoS Protection | ✓✓ | ✓ | ✓ | ✓✓✓ |
| WAF | ✓ | ✓ | ✓ (via Shield) | ✓✓ |
| Edge Compute | Workers | VCL | Lambda@Edge | Cloudlets |
| Origin Shield | Limited | ✓ | ✓ | ✓ |
| Real-Time Analytics | ✓ | ✓✓ | ✓ | ✓ |
| Bot Management | ✓ | ✓ | Limited | ✓✓ |
| Video Delivery | ✓ | ✓✓ | ✓ | ✓✓ |
| AWS Integration | ✗ | ✗ | ✓✓ | ✗ |
| Support 24/7 | Limited | ✓ | ✓ | ✓ |
| Entry Price | $20-200/mo | $50+/mo | Pay-per-use | $5000+/mo |

## Selection Matrix

### Small Website (<1GB/month)
```
Best: Cloudflare Free/Pro
- Fixed pricing, no overage charges
- Good performance globally
- DDoS protection included
- Easy setup
```

### Media/Video Streaming
```
Best: Fastly or AWS CloudFront
Fastly:
- Excellent real-time analytics
- VCL flexibility
- Video optimization

AWS CloudFront:
- S3 integration
- Lambda@Edge support
- AWS ecosystem
```

### Enterprise Global Scale
```
Best: Akamai
- Maximum edge coverage
- Enterprise SLA
- Advanced security
- Dedicated support
```

### AWS-Centric
```
Best: AWS CloudFront
- Seamless integration
- No cross-platform costs
- IAM authentication
- Lambda@Edge
```

### API/Microservices
```
Best: Fastly
- Low latency
- Request transformation
- Real-time analytics
- Origin protection
```

## Multi-CDN Strategy

### Failover Configuration
```
Primary CDN (Cloudflare)
       |
   Health check fails
       |
Secondary CDN (Fastly)
       |
   Health check fails
       |
Origin

Implementation:
1. CNAME to primary CDN
2. Health check every 60 seconds
3. Automatic failover on failure
4. TTL 60 seconds for rapid switching
```

### Cost Optimization
```
Mix providers by content type:
- Static assets: Cloudflare (fixed cost)
- Video: Fastly (optimized pricing)
- API: AWS CloudFront (AWS credits)

Tiered approach:
Tier 1: Cache-heavy content (Cloudflare)
Tier 2: Origin-heavy content (Fastly)
Tier 3: Specialized content (AWS)
```

### Redundancy Strategy
```
Production:
- Primary CDN: Fastly
- Secondary CDN: AWS CloudFront
- Origin: Multiple regional origins

Benefits:
- Avoid single vendor lock-in
- Cost optimization per workload
- Vendor-independent disaster recovery
```
