# CDN Optimization Guide

## Cache Hit Ratio Optimization

### Measure Current CHR
```bash
# CloudFront
aws cloudfront get-distribution-statistics \
  --distribution-id E123ABC \
  --query 'Statistics.CacheHitRate' \
  --start-time 2024-11-01 \
  --end-time 2024-11-30

# Expected output: 75.5

# Cloudflare API
curl https://api.cloudflare.com/client/v4/zones/{zone_id}/analytics/requests \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json"

# Response includes cache_hit_ratio
```

### Optimization Step 1: Extend TTL

**Before:**
```
Cache-Control: max-age=300
CHR: 65%
```

**After:**
```
Cache-Control: max-age=3600
CHR: 82%
```

**Implementation:**
```hcl
# Terraform - CloudFront
resource "aws_cloudfront_distribution" "example" {
  default_cache_behavior {
    default_ttl = 3600  # 1 hour
    max_ttl     = 86400  # 1 day
  }
}
```

**Guidelines:**
- Static assets: 1 year (31536000)
- CSS/JS: 1 month (2592000)
- Images: 1 month (2592000)
- HTML: 1 hour (3600)
- API: 5 minutes (300)

### Optimization Step 2: Remove Query Strings

**Before:**
```
/product.html?utm_source=google
/product.html?utm_source=facebook
= 2 separate cache entries for same content
CHR: 70%
```

**After:**
```
/product.html (same for all)
= 1 cache entry shared
CHR: 88%
```

**Cloudflare Implementation:**
```
Dashboard:
1. Caching → Cache Key
2. Query String Sort: OFF
3. Cache on Cookie: Remove tracking cookies
```

**AWS CloudFront Implementation:**
```hcl
resource "aws_cloudfront_distribution" "example" {
  default_cache_behavior {
    forwarded_values {
      query_string = false
      query_string_cache_keys {
        # Only forward essential query params
        items = ["search", "filter"]
      }
    }
  }
}
```

### Optimization Step 3: Normalize Cookies

**Before:**
```
Cookie: session_id=user123
Cookie: session_id=user456
= Different cache entries per user
CHR: 50%
```

**After:**
```
Cache key includes: base URL only
Ignore session cookie
= Shared cache for all users (same HTML)
CHR: 85%
```

**Cloudflare Implementation:**
```
Dashboard:
1. Caching → Cache Key
2. Cookies: Remove session/tracking cookies
3. Keep only: language, region
```

**Custom Header Normalization:**
```hcl
# CloudFront Function to normalize headers
resource "aws_cloudfront_function" "normalize" {
  name    = "normalize-headers"
  runtime = "cloudfront-js-1.0"
  code    = file("${path.module}/normalize.js")
}

# normalize.js
function handler(event) {
  var request = event.request;
  var headers = request.headers;

  // Remove tracking cookies
  if (headers.cookie) {
    var cookies = headers.cookie.value.split('; ');
    var filtered = cookies.filter(c => !c.startsWith('utm_') && !c.startsWith('ga_'));
    headers.cookie.value = filtered.join('; ');
  }

  return request;
}
```

### Optimization Step 4: Cache Tags

**Implementation:**
```
Set cache tags on responses:
Cache-Tag: post-123, blog, featured

When blog post updates:
Purge tag: post-123
This purges:
- /blog/post-123.html
- /blog/index.html
- /author/john.html
```

**Cloudflare API:**
```bash
# Set cache tag on response
curl -X POST https://example.com/api/post \
  -H "Cache-Tag: post-123,blog"

# Purge by tag
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  --data '{"tags": ["post-123"]}'
```

## Compression Optimization

### Enable Gzip + Brotli

**Cloudflare:**
```
Dashboard:
1. Speed → Optimization
2. Brotli compression: ON
3. Automatic: GZIP + Brotli selection
```

**AWS CloudFront:**
```hcl
resource "aws_cloudfront_distribution" "example" {
  default_cache_behavior {
    compress = true  # Enables gzip
  }

  # Brotli requires CloudFront Functions
  function_association {
    event_type   = "viewer-response"
    function_arn = aws_cloudfront_function.compress.arn
  }
}
```

### Compression Ratios
```
Content Type       GZIP    Brotli    Benefit
HTML              70%     75%       5% better
CSS               65%     70%       5% better
JavaScript        60%     68%       8% better
JSON              65%     72%       7% better
SVG Images        50%     60%       10% better
PNG/JPEG          ~0%     ~0%       Already compressed
```

### Minimum Size for Compression
```
Only compress if > 1 KB:
- < 1 KB: Compression overhead > benefit
- > 1 KB: Compression saves bandwidth

Configuration:
compress_min_length 1024;
```

## Image Optimization

### Format Selection

**Cloudflare Image Optimization:**
```
Dashboard:
1. Images → Polish
2. Enable for:
   - Lossless (quality preserved)
   - Lossy (smaller, acceptable quality loss)
3. Enables WebP for modern browsers

Result: 30-50% size reduction
```

**NGINX Configuration:**
```
map $http_accept $webp_suffix {
  default "";
  "~*webp" ".webp";
}

location ~* \.(jpg|jpeg|png)$ {
  rewrite ^(.*)\.png$ $1$webp_suffix break;
  rewrite ^(.*)\.jpg$ $1$webp_suffix break;
}
```

### Responsive Images
```
Instead of:
<img src="image.jpg">

Use:
<picture>
  <source srcset="image-small.webp" media="(max-width: 480px)">
  <source srcset="image-medium.webp" media="(max-width: 1024px)">
  <source srcset="image-large.webp" media="(min-width: 1025px)">
  <img src="image.jpg" alt="description">
</picture>

Benefits:
- Mobile clients get smaller images
- Desktop clients get high-quality
- Bandwidth optimization per device
```

## Origin Shield Optimization

### When to Use Origin Shield
```
Cost-Benefit Analysis:

With Origin Shield:
- Cost: Additional ~30%
- Benefit: 90% reduction in origin traffic
- CHR improvement: 95%+

Without Origin Shield:
- Cost: Lower
- Benefit: Limited to CDN single cache level
- CHR: 85-90%

Scenarios where beneficial:
1. Small origin server
2. Sudden traffic spikes
3. Viral content
4. Database-heavy content

Scenario without benefit:
1. Origin is CDN
2. Always cache misses
3. Personalized content
```

### Enable Origin Shield
```hcl
# AWS CloudFront
resource "aws_cloudfront_distribution" "example" {
  origin {
    domain_name = aws_lb.origin.dns_name
    origin_id   = "myOrigin"

    origin_shield {
      enabled              = true
      origin_shield_region = "us-east-1"  # Closest to origin
    }
  }
}
```

## Prefetch & Preload

### Link Prefetch
```html
<!-- Prefetch next page (user might navigate) -->
<link rel="prefetch" href="/next-page.html">

<!-- DNS prefetch (resolve DNS early) -->
<link rel="dns-prefetch" href="https://cdn.example.com">

<!-- Preconnect (establish TCP + TLS) -->
<link rel="preconnect" href="https://api.example.com">

<!-- Preload (fetch critical resource) -->
<link rel="preload" href="/critical.js" as="script">
```

### Predictive Prefetch
```javascript
// Track user navigation patterns
const navigationGraph = {
  '/': ['/products/', '/about/'],
  '/products/': ['/checkout/', '/product-detail/'],
  '/checkout/': ['/thank-you/', '/']
};

// Prefetch likely next pages
function prefetchNext(currentPage) {
  const next = navigationGraph[currentPage] || [];
  next.forEach(url => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  });
}
```

### Cloudflare Argo Smart Routing
```
Enables:
- Intelligent prefetch
- Faster routing paths
- Automatic prioritization

Cost: ~$5/month additional
Benefit: 5-10% latency improvement
```

## Bandwidth Optimization

### Minification

**CSS Minification:**
```
Before:
body {
  margin: 0;
  padding: 0;
}

After:
body{margin:0;padding:0}

Reduction: 20-30%
```

**JavaScript Minification:**
```
Before:
function calculateTotal(items) {
  let total = 0;
  for (let item of items) {
    total += item.price;
  }
  return total;
}

After:
function calculateTotal(a){let b=0;for(let c of a)b+=c.price;return b}

Reduction: 40-50%
```

**Build Configuration:**
```javascript
// webpack.config.js
const TerserPlugin = require("terser-webpack-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

module.exports = {
  mode: 'production',
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin(),
      new CssMinimizerPlugin(),
    ],
  },
};
```

### Asset Versioning

**Content Hashing:**
```javascript
// Webpack generates hash-based filenames
output: {
  filename: 'js/[name].[contenthash].js',
  assetModuleFilename: 'assets/[name].[contenthash][ext]'
}

Result:
- app.abc123def456.js (version 1)
- style.xyz789abc012.css (version 1)

On update:
- app.xyz789abc012.js (version 2, new hash)
- style.abc123def456.css (version 2, new hash)

Benefits:
- Old versions remain cached
- New version fetched immediately
- No TTL expiration needed
```

## Real-Time Analytics

### Cloudflare Analytics
```
Dashboard:
1. Analytics & Logs → Overview
   - Requests per second
   - Cache hit ratio
   - Top countries
   - Bandwidth saved

2. Analytics & Logs → Requests
   - Query requests
   - Filter by status code
   - See slow queries

3. Create custom dashboard
```

### AWS CloudFront Analytics
```bash
# Real-time metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --start-time 2024-11-19T00:00:00Z \
  --end-time 2024-11-19T23:59:59Z \
  --period 300 \
  --statistics Sum
```

## Monitoring & Alerting

### Key Metrics to Monitor
```
1. Cache Hit Ratio (target: 85%+)
2. Origin Bandwidth (should decrease with CDN)
3. Response Time (p95 < 100ms)
4. Error Rate (< 1%)
5. 4xx Errors (user errors, not critical)
6. 5xx Errors (> 5% indicates origin issues)
```

### CloudWatch Alarms
```hcl
resource "aws_cloudwatch_metric_alarm" "chr_low" {
  alarm_name          = "cdn-chr-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CacheHitRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 70  # Alert if < 70%
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DistributionId = aws_cloudfront_distribution.example.id
  }
}

resource "aws_cloudwatch_metric_alarm" "origin_errors" {
  alarm_name          = "cdn-origin-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "OriginLatency"
  namespace           = "AWS/CloudFront"
  period              = 60
  statistic           = "Average"
  threshold           = 1000  # Alert if > 1s
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

## Performance Tuning Checklist

- [ ] TTL optimized by content type
- [ ] Query strings removed from cache key
- [ ] Cookies normalized
- [ ] Compression enabled (gzip + brotli)
- [ ] Image optimization enabled
- [ ] Asset versioning implemented
- [ ] Origin Shield enabled (if beneficial)
- [ ] Cache hit ratio > 85%
- [ ] Origin latency monitored
- [ ] Monitoring alerts configured
- [ ] Performance tested from multiple locations
- [ ] Analytics reviewed weekly

## Optimization Workflow

```
Week 1: Measure baseline
- Collect CHR, bandwidth, latency metrics
- Identify bottlenecks

Week 2: Quick wins
- Enable compression
- Extend TTL for static
- Remove query strings

Week 3: Medium efforts
- Image optimization
- Cache tag implementation
- Asset versioning

Week 4: Advanced
- Origin Shield
- Prefetch strategy
- Edge functions

Review:
- Target 85%+ CHR
- 50%+ bandwidth reduction
- <100ms p95 latency
```
