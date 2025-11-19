# CDN Implementation Guide

## Prerequisites

- Origin server with content
- Domain and DNS management access
- CDN provider account
- HTTPS certificate (recommended)

## Step 1: Choose CDN Provider

### Provider Selection Matrix

| Requirement | Best Option | Alternative |
|------------|------------|-------------|
| Small website | Cloudflare Free | AWS CloudFront |
| Video streaming | Fastly | AWS CloudFront |
| AWS-centric | AWS CloudFront | Cloudflare |
| Global scale | Akamai | Cloudflare Enterprise |
| Budget-conscious | Cloudflare | AWS CloudFront |
| DDoS protection | Cloudflare | Akamai |

### Evaluation Criteria
- Geographic coverage needed
- Budget constraints
- Feature requirements (WAF, analytics, edge computing)
- Existing infrastructure (AWS, GCP, etc.)
- Support level needed

## Step 2: Set Up with Cloudflare (Quick Start)

### Create Cloudflare Account
```
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with email
3. Verify email
4. Create password
```

### Add Domain to Cloudflare
```
1. Login to Cloudflare Dashboard
2. Click "Add site"
3. Enter domain name: example.com
4. Select plan (Free, Pro, Business, Enterprise)
5. Cloudflare scans for existing DNS records
6. Review records (should auto-detect)
7. Click "Continue"
```

### Update Nameservers at Registrar
```
Cloudflare provides:
- ns1.cloudflare.com
- ns2.cloudflare.com

Login to registrar (GoDaddy, Namecheap, etc.):
1. Go to Domain Management
2. Change Nameservers
3. Replace with Cloudflare nameservers
4. Save
5. Wait 24-48 hours for propagation
```

### Verify Propagation
```bash
# Check nameservers changed
dig example.com NS +short
# Should show Cloudflare nameservers

# Verify DNS working
dig example.com A @ns1.cloudflare.com
```

### Configure CDN Settings
```
Cloudflare Dashboard:
1. Go to Caching → Configuration
2. Set Cache Level: "Cache Everything"
3. Set Browser Cache TTL: "1 month"
4. Under Speed → Optimization:
   - Enable Brotli compression
   - Enable Automatic HTTPS Rewrites
5. Under Security → SSL/TLS:
   - Set mode to "Full (strict)"
```

## Step 3: Set Up with AWS CloudFront

### Create S3 Origin (for static website)
```bash
# Create S3 bucket
aws s3 mb s3://example-com-origin --region us-east-1

# Upload files
aws s3 cp ./public s3://example-com-origin --recursive

# Block public access (CloudFront handles serving)
aws s3api put-bucket-public-access-block \
  --bucket example-com-origin \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Create CloudFront Distribution (Terraform)
```hcl
# S3 Origin Access Identity
resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "CloudFront access to S3"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "example" {
  origin {
    domain_name = aws_s3_bucket.origin.bucket_regional_domain_name
    origin_id   = "myS3Origin"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  enabled = true
  is_ipv6_enabled = true
  comment = "CDN for example.com"

  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
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
    compress               = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "example-com-cdn"
  }
}

# Output CloudFront domain
output "cloudfront_domain" {
  value = aws_cloudfront_distribution.example.domain_name
}
```

### Apply Terraform
```bash
terraform init
terraform plan
terraform apply
```

### Update DNS
```bash
# Get CloudFront domain name
cloudfront_domain=$(terraform output cloudfront_domain)

# Add CNAME record to Route53
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "example.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'$cloudfront_domain'"}]
      }
    }]
  }'
```

## Step 4: Configure Cache Behavior

### Cache Headers on Origin
```
For static assets (images, CSS, JS):
Cache-Control: public, max-age=31536000, immutable
ETag: "abc123def456"

For HTML pages:
Cache-Control: public, max-age=3600, must-revalidate
ETag: "xyz789abc123"

For API responses:
Cache-Control: public, max-age=60, stale-while-revalidate=300
ETag: "api-version-1"
```

### Configure in Cloudflare
```
Page Rules (Cloudflare Dashboard):
1. Caching → Rules
2. Create rule for /api/*
   - Cache Level: Bypass (don't cache)

3. Create rule for /static/*
   - Cache Level: Cache Everything
   - Browser Cache TTL: 1 year

4. Create rule for /
   - Cache Level: Cache Everything
   - Browser Cache TTL: 30 minutes
```

### Configure in AWS CloudFront
```hcl
# Additional cache behaviors for different paths
resource "aws_cloudfront_distribution" "example" {
  # ... previous config ...

  # Static assets (long cache)
  cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    path_pattern     = "/static/*"
    target_origin_id = "myS3Origin"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400  # 1 day
    max_ttl                = 31536000  # 1 year
    compress               = true
  }

  # API responses (short cache)
  cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods   = ["GET", "HEAD"]
    path_pattern     = "/api/*"
    target_origin_id = "myS3Origin"

    forwarded_values {
      query_string = true
      cookies { forward = "all" }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 60  # 1 minute
    max_ttl                = 300  # 5 minutes
    compress               = true
  }
}
```

## Step 5: Enable HTTPS/TLS

### Cloudflare SSL Certificate
```
Cloudflare Dashboard:
1. SSL/TLS → Overview
2. Select "Full (strict)"
3. Cloudflare automatically provisions certificate
4. Enable "Always Use HTTPS"
5. Enable "HSTS" for security headers
```

### AWS CloudFront Certificate
```hcl
# Request ACM certificate
resource "aws_acm_certificate" "example" {
  domain_name       = "example.com"
  validation_method = "DNS"

  subject_alternative_names = ["*.example.com"]

  lifecycle {
    create_before_destroy = true
  }
}

# Create validation record in Route53
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.example.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# Configure CloudFront with certificate
resource "aws_cloudfront_distribution" "example" {
  # ... previous config ...

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.example.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}
```

## Step 6: Test CDN

### Verify CDN is Working
```bash
# Check origin server
curl -i https://origin.example.com/index.html
# Should be slow (direct origin)

# Check through CDN
curl -i https://example.com/index.html
# Should be fast (cached)

# Verify CDN serving
curl -I https://example.com/index.html | grep -i "CF-"
# Cloudflare headers should be present

# Check cache status
curl -I https://example.com/index.html | grep "CF-Cache-Status"
# HIT = cached, MISS = fetched from origin
```

### Performance Testing
```bash
# Test latency
time curl -o /dev/null -s https://example.com/

# Test from different locations
# Use online tools: https://tools.pingdom.com/

# Monitor with curl
for i in {1..5}; do
  curl -w "Time: %{time_total}s Status: %{http_code}\n" -o /dev/null -s https://example.com/
  sleep 1
done
```

## Step 7: Configure Origin Shield (Optional)

### AWS CloudFront Origin Shield
```hcl
resource "aws_cloudfront_distribution" "example" {
  origin {
    # ... S3 origin config ...

    origin_shield {
      enabled              = true
      origin_shield_region = "us-east-1"
    }
  }

  # ... rest of config ...
}
```

### Cloudflare Origin Shield
```
Cloudflare Dashboard:
1. Caching → Configuration
2. Find "Origin Shield"
3. Enable and select region
4. Adds extra caching layer (fee applies)
```

## Step 8: Monitor and Optimize

### Set Up Analytics

#### Cloudflare Analytics
```
Dashboard:
Analytics → Overview
- Requests per second
- Cache hit ratio
- Bandwidth saved
- Top content
- Top countries
```

#### AWS CloudFront Monitoring
```hcl
resource "aws_cloudwatch_dashboard" "cdn" {
  dashboard_name = "cdn-monitoring"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/CloudFront", "Requests", {"stat": "Sum"}],
            [".", "BytesSent", {"stat": "Sum"}],
            [".", "BytesDownloadedByViewer", {"stat": "Sum"}],
            [".", "CacheHitRate", {"stat": "Average"}]
          ]
          period = 300
          stat   = "Average"
          region = "us-east-1"
          title  = "CloudFront Metrics"
        }
      }
    ]
  })
}
```

### Optimize Cache Hit Ratio
```
Monitor CHR in dashboard
Current CHR: 75%

Improvement steps:
1. Increase TTL for static content (long-lived)
2. Remove query strings for static assets
3. Set cache headers correctly on origin
4. Use cache tags for related content
5. Enable Origin Shield

Target: 85%+ CHR
```

## Step 9: Enable DDoS Protection

### Cloudflare DDoS Protection
```
Dashboard:
1. Security → DDoS Protection
2. Already enabled (all plans)
3. Under Firewall → Waf Rules
4. Enable Managed Rulesets for DDoS rules
```

### AWS Shield Standard (Included)
```
Automatically enabled for all AWS customers
Free DDoS protection at Layer 3 and 4
```

### AWS Shield Advanced (Optional)
```hcl
resource "aws_shield_protection" "example" {
  name          = "example-com-shield"
  resource_arn  = aws_cloudfront_distribution.example.arn
}
```

## Production Checklist

- [ ] Domain added to CDN
- [ ] Nameservers updated at registrar
- [ ] DNS propagated globally
- [ ] HTTPS certificate installed
- [ ] Cache behavior configured
- [ ] Origin server responding
- [ ] Cache hit ratio acceptable (>70%)
- [ ] CDN serving content (test with curl)
- [ ] Analytics dashboard set up
- [ ] DDoS protection enabled
- [ ] Origin Shield enabled (if needed)
- [ ] Monitoring alerts configured
- [ ] Performance tested from multiple locations
- [ ] Failover tested

## Troubleshooting

### Issue: Cache Hit Ratio Low (< 50%)
```
Causes:
1. TTL too short
2. Query strings in URLs
3. Cookies varying responses
4. Dynamic content

Solutions:
1. Increase TTL for static content
2. Remove tracking query strings
3. Normalize cookies in cache key
4. Use Origin Shield
```

### Issue: HTTPS Certificate Error
```
Causes:
1. Certificate not yet issued
2. Domain not validated
3. Certificate mismatch

Solutions:
1. Wait 24 hours for certificate provisioning
2. Verify DNS records for validation
3. Check domain in certificate CN
```

### Issue: Slow Performance
```
Causes:
1. Origin server slow
2. Geographic distance
3. Cache misses

Solutions:
1. Optimize origin server
2. Enable Origin Shield
3. Enable Brotli compression
4. Minify CSS/JS
```
